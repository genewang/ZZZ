"""Semantic + role-aware routing across vLLM heads (Mixture of Models)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.contracts import IntentClass, ModelTier, RouteResult
from app.vllm.pool import HeadRole, VLLMHead, VLLMHeadPool, get_vllm_pool
from app.zero_token.router import IntentClassifier, SemanticCache, COMPILED_WORKFLOWS
from app.config import get_settings


@dataclass
class HeadRoute:
    head: VLLMHead
    route: RouteResult
    compiled_output: str | None = None
    cached_output: str | None = None


class VLLMSemanticRouter:
    """Zero-Token aware router that prefers cache → compiled → vLLM heads."""

    INTENT_TAGS: dict[IntentClass, list[str]] = {
        IntentClass.CREATE_3D: ["create_3d", "mesh"],
        IntentClass.STORYKEEPER: ["storykeeper", "deep"],
        IntentClass.DEVOTION: ["devotion", "fast"],
        IntentClass.CHURCH_CURRICULUM: ["devotion", "deep"],
        IntentClass.GENERAL: ["general", "fast"],
    }

    def __init__(self, pool: VLLMHeadPool | None = None) -> None:
        self.settings = get_settings()
        self.pool = pool or get_vllm_pool()
        self.classifier = IntentClassifier()
        self.cache = SemanticCache(self.settings.semantic_cache_threshold)

    def route(self, prompt: str, *, prefer_compiled: str | None = None) -> HeadRoute:
        intent = self.classifier.classify(prompt)

        if intent == IntentClass.UNSAFE:
            head = self.pool.by_role(HeadRole.CLASSIFIER)[0]
            return HeadRoute(
                head=head,
                route=RouteResult(
                    tier=ModelTier.LOCAL_SMALL,
                    intent=intent,
                    model_id=head.model,
                    tokens_billed=0,
                ),
            )

        hit, sim = self.cache.lookup(prompt)
        if hit is not None:
            head = self.pool.by_role(HeadRole.ROUTER)[0]
            return HeadRoute(
                head=head,
                route=RouteResult(
                    tier=ModelTier.CACHE,
                    intent=intent,
                    cache_hit=True,
                    similarity=round(sim, 4),
                    model_id="semantic-cache",
                    tokens_billed=0,
                ),
                cached_output=hit.output,
            )

        if self.settings.enable_compiled_paths:
            compiled = prefer_compiled or self._match_compiled(prompt)
            if compiled and compiled in COMPILED_WORKFLOWS:
                head = self.pool.by_role(HeadRole.COMPILER)[0]
                return HeadRoute(
                    head=head,
                    route=RouteResult(
                        tier=ModelTier.COMPILED,
                        intent=intent,
                        model_id="compiled-ai",
                        tokens_billed=0,
                        compiled_path=compiled,
                    ),
                    compiled_output=COMPILED_WORKFLOWS[compiled],
                )

        head = self._select_head(intent, prompt)
        tier = self._tier_for_head(head)
        tokens = max(16, len(re.findall(r"\w+", prompt)) * 2)
        return HeadRoute(
            head=head,
            route=RouteResult(
                tier=tier,
                intent=intent,
                model_id=head.model,
                tokens_billed=tokens,
            ),
        )

    def remember(self, prompt: str, output: str, intent: IntentClass) -> None:
        self.cache.store(prompt, output, intent)

    def _select_head(self, intent: IntentClass, prompt: str) -> VLLMHead:
        tags = self.INTENT_TAGS.get(intent, ["general"])
        candidates: list[VLLMHead] = []
        for tag in tags:
            candidates.extend(self.pool.by_tag(tag))
        if not candidates:
            candidates = [h for h in self.pool.list_heads() if h.enabled]
        # Prefer lower cost when prompt is short
        word_count = len(re.findall(r"\w+", prompt))
        candidates = sorted(candidates, key=lambda h: (h.cost_weight, h.priority))
        if word_count > 80:
            deep = [h for h in candidates if "deep" in h.tags or h.cost_weight >= 1.0]
            if deep:
                return deep[-1]
        return candidates[0]

    @staticmethod
    def _tier_for_head(head: VLLMHead) -> ModelTier:
        if head.cost_weight <= 0.5:
            return ModelTier.LOCAL_SMALL
        if head.cost_weight <= 1.2:
            return ModelTier.LOCAL_LARGE
        return ModelTier.FRONTIER

    @staticmethod
    def _match_compiled(prompt: str) -> str | None:
        lower = prompt.lower()
        if "exodus" in lower and ("bedtime" in lower or "age" in lower):
            return "age5_exodus_bedtime"
        if "noah" in lower and ("ark" in lower or "create" in lower or "3d" in lower):
            return "sprout_noah_create"
        return None


_router: VLLMSemanticRouter | None = None


def get_vllm_router() -> VLLMSemanticRouter:
    global _router
    if _router is None:
        _router = VLLMSemanticRouter()
    return _router
