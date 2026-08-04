"""Zero-Token Mixture-of-Models layer.

Pipeline: classify → semantic cache → dynamic route → (optional) compiled path.
Production target: vLLM Semantic Router + Milvus. Local: numpy hash embeddings.
"""

from __future__ import annotations

import hashlib
import math
import re
import threading
import time
from dataclasses import dataclass

import numpy as np

from app.config import Settings, get_settings
from app.contracts import IntentClass, ModelTier, RouteResult


TOKEN_RE = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def embed(text: str, dims: int = 256) -> np.ndarray:
    """Fast local embedding via hashed n-grams (swap for BERT later)."""
    vec = np.zeros(dims, dtype=np.float32)
    toks = tokenize(text)
    if not toks:
        return vec
    for tok in toks:
        h = int(hashlib.blake2b(tok.encode(), digest_size=8).hexdigest(), 16)
        idx = h % dims
        sign = 1.0 if (h >> 8) & 1 else -1.0
        vec[idx] += sign
    for a, b in zip(toks, toks[1:]):
        bigram = f"{a}_{b}".encode()
        h = int(hashlib.blake2b(bigram, digest_size=8).hexdigest(), 16)
        idx = h % dims
        vec[idx] += 0.5 if (h >> 8) & 1 else -0.5
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


class IntentClassifier:
    """Tiny domain classifier — production would be a distilled BERT."""

    RULES: list[tuple[IntentClass, tuple[str, ...]]] = [
        (IntentClass.UNSAFE, ("rm -rf", "exfiltrate", "ignore previous", "jailbreak")),
        (IntentClass.CREATE_3D, ("3d", "mesh", "print", "ark", "sling", "sketch", "scene")),
        (IntentClass.STORYKEEPER, ("grandma", "legacy", "psalm", "recording", "keepsake")),
        (IntentClass.CHURCH_CURRICULUM, ("sunday", "classroom", "volunteer", "church")),
        (IntentClass.DEVOTION, ("bible", "devotion", "parable", "prayer", "scripture")),
    ]

    def classify(self, prompt: str) -> IntentClass:
        lower = prompt.lower()
        for intent, keys in self.RULES:
            if any(k in lower for k in keys):
                return intent
        return IntentClass.GENERAL


@dataclass
class CacheEntry:
    prompt: str
    vector: np.ndarray
    output: str
    intent: IntentClass
    hits: int = 0


class SemanticCache:
    """In-memory semantic cache — production: Milvus / pgvector."""

    def __init__(self, threshold: float) -> None:
        self.threshold = threshold
        self._lock = threading.RLock()
        self._entries: list[CacheEntry] = []

    def lookup(self, prompt: str) -> tuple[CacheEntry | None, float]:
        query = embed(prompt)
        best: CacheEntry | None = None
        best_sim = -1.0
        with self._lock:
            for entry in self._entries:
                sim = cosine(query, entry.vector)
                if sim > best_sim:
                    best_sim = sim
                    best = entry
        if best is not None and best_sim >= self.threshold:
            best.hits += 1
            return best, best_sim
        return None, best_sim if best is not None else 0.0

    def store(self, prompt: str, output: str, intent: IntentClass) -> None:
        entry = CacheEntry(prompt=prompt, vector=embed(prompt), output=output, intent=intent)
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > 2000:
                self._entries = self._entries[-1500:]

    def stats(self) -> dict[str, int | float]:
        with self._lock:
            return {
                "entries": len(self._entries),
                "threshold": self.threshold,
                "total_hits": sum(e.hits for e in self._entries),
            }


COMPILED_WORKFLOWS: dict[str, str] = {
    "age5_exodus_bedtime": (
        "Tonight's age-fit Exodus story: Moses leads the people through the sea. "
        "Craft cue: fold paper waves. Family prompt: When have we needed courage together?"
    ),
    "sprout_noah_create": (
        "Create Studio preset: Noah's ark on a misty mountain, kid-friendly, printable. "
        "Mesh style: soft toy. Parent gate required before export."
    ),
}


class MixtureOfModelsRouter:
    """MoM router: cache → compiled → small → large → frontier."""

    TIER_MODELS = {
        ModelTier.CACHE: "semantic-cache",
        ModelTier.COMPILED: "compiled-ai",
        ModelTier.LOCAL_SMALL: "local-small-llm",
        ModelTier.LOCAL_LARGE: "local-large-llm",
        ModelTier.FRONTIER: "frontier-llm",
    }

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.classifier = IntentClassifier()
        self.cache = SemanticCache(self.settings.semantic_cache_threshold)

    def route(self, prompt: str, *, prefer_compiled: str | None = None) -> RouteResult:
        started = time.perf_counter()
        intent = self.classifier.classify(prompt)

        if intent == IntentClass.UNSAFE:
            return RouteResult(
                tier=ModelTier.LOCAL_SMALL,
                intent=intent,
                cache_hit=False,
                model_id="policy-block",
                tokens_billed=0,
                latency_ms=self._ms(started),
            )

        hit, sim = self.cache.lookup(prompt)
        if hit is not None:
            return RouteResult(
                tier=ModelTier.CACHE,
                intent=intent,
                cache_hit=True,
                similarity=round(sim, 4),
                model_id=self.TIER_MODELS[ModelTier.CACHE],
                tokens_billed=0,
                latency_ms=self._ms(started),
            )

        if self.settings.enable_compiled_paths:
            compiled = prefer_compiled or self._match_compiled(prompt)
            if compiled:
                return RouteResult(
                    tier=ModelTier.COMPILED,
                    intent=intent,
                    cache_hit=False,
                    model_id=self.TIER_MODELS[ModelTier.COMPILED],
                    tokens_billed=0,
                    latency_ms=self._ms(started),
                    compiled_path=compiled,
                )

        # Complexity heuristic
        tokens = len(tokenize(prompt))
        if tokens < 24 and intent in {IntentClass.DEVOTION, IntentClass.GENERAL}:
            tier = ModelTier.LOCAL_SMALL
        elif intent in {IntentClass.CREATE_3D, IntentClass.STORYKEEPER}:
            tier = ModelTier.LOCAL_LARGE
        else:
            tier = ModelTier.FRONTIER if tokens > 80 else ModelTier.LOCAL_LARGE

        # Estimated billable tokens (stub metering)
        billed = 0 if tier in {ModelTier.CACHE, ModelTier.COMPILED} else max(16, tokens * 2)

        return RouteResult(
            tier=tier,
            intent=intent,
            cache_hit=False,
            model_id=self.TIER_MODELS[tier],
            tokens_billed=billed,
            latency_ms=self._ms(started),
        )

    def remember(self, prompt: str, output: str, intent: IntentClass) -> None:
        self.cache.store(prompt, output, intent)

    def resolve_compiled(self, path: str) -> str:
        return COMPILED_WORKFLOWS[path]

    def _match_compiled(self, prompt: str) -> str | None:
        lower = prompt.lower()
        if "exodus" in lower and ("bedtime" in lower or "age" in lower):
            return "age5_exodus_bedtime"
        if "noah" in lower and ("ark" in lower or "create" in lower or "3d" in lower):
            return "sprout_noah_create"
        return None

    @staticmethod
    def _ms(started: float) -> int:
        return int((time.perf_counter() - started) * 1000)


_router: MixtureOfModelsRouter | None = None


def get_router() -> MixtureOfModelsRouter:
    global _router
    if _router is None:
        _router = MixtureOfModelsRouter()
    return _router
