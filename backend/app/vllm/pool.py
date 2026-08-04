"""vLLM-centric multi-head inference fabric.

Every adaptable LLM is registered as a Head served by vLLM's OpenAI-compatible
API (continuous batching, PagedAttention, tensor parallel). Multi-agent graphs
bind nodes to heads; the semantic router picks heads for single-shot calls.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.config import Settings, get_settings


class HeadRole(str, Enum):
    CLASSIFIER = "classifier"
    ROUTER = "router"
    REASONER = "reasoner"
    CREATOR = "creator"
    CRITIC = "critic"
    COMPILER = "compiler"
    EMBEDDER = "embedder"
    GENERAL = "general"


class VLLMHead(BaseModel):
    head_id: str
    model: str
    base_url: str
    role: HeadRole = HeadRole.GENERAL
    max_model_len: int = 8192
    temperature: float = 0.4
    priority: int = 100
    enabled: bool = True
    tags: list[str] = Field(default_factory=list)
    # Cost weight for MoM routing (lower = cheaper)
    cost_weight: float = 1.0


class ChatMessage(BaseModel):
    role: str
    content: str


class VLLMCompletion(BaseModel):
    head_id: str
    model: str
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    raw: dict[str, Any] = Field(default_factory=dict)
    stub: bool = False


@dataclass
class HeadHealth:
    head_id: str
    ok: bool
    latency_ms: int | None = None
    detail: str = ""


class VLLMClient:
    """Thin OpenAI-compatible client aimed at vLLM servers."""

    def __init__(self, timeout: float = 60.0) -> None:
        self.timeout = timeout

    def chat(
        self,
        head: VLLMHead,
        messages: list[ChatMessage],
        *,
        temperature: float | None = None,
        max_tokens: int = 512,
        extra: dict[str, Any] | None = None,
    ) -> VLLMCompletion:
        started = time.perf_counter()
        url = head.base_url.rstrip("/") + "/v1/chat/completions"
        payload: dict[str, Any] = {
            "model": head.model,
            "messages": [m.model_dump() for m in messages],
            "temperature": head.temperature if temperature is None else temperature,
            "max_tokens": max_tokens,
        }
        if extra:
            payload.update(extra)

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
        except Exception as exc:
            # Deterministic stub so the framework remains runnable without a cluster
            content = self._stub_content(head, messages)
            return VLLMCompletion(
                head_id=head.head_id,
                model=head.model,
                content=content,
                prompt_tokens=sum(len(m.content.split()) for m in messages),
                completion_tokens=len(content.split()),
                total_tokens=0,
                latency_ms=int((time.perf_counter() - started) * 1000),
                raw={"error": str(exc), "mode": "stub"},
                stub=True,
            )

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = data.get("usage") or {}
        content = message.get("content") or ""
        return VLLMCompletion(
            head_id=head.head_id,
            model=data.get("model") or head.model,
            content=content,
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            total_tokens=int(usage.get("total_tokens") or 0),
            latency_ms=int((time.perf_counter() - started) * 1000),
            raw=data,
            stub=False,
        )

    def health(self, head: VLLMHead) -> HeadHealth:
        started = time.perf_counter()
        url = head.base_url.rstrip("/") + "/v1/models"
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(url)
                res.raise_for_status()
            return HeadHealth(
                head_id=head.head_id,
                ok=True,
                latency_ms=int((time.perf_counter() - started) * 1000),
                detail="reachable",
            )
        except Exception as exc:
            return HeadHealth(
                head_id=head.head_id,
                ok=False,
                latency_ms=int((time.perf_counter() - started) * 1000),
                detail=str(exc),
            )

    @staticmethod
    def _stub_content(head: VLLMHead, messages: list[ChatMessage]) -> str:
        user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return f"[{head.head_id}/{head.model}] {user[:240]}"


@dataclass
class VLLMHeadPool:
    """Registry of vLLM-served model heads for multi-agent / MoM routing."""

    heads: dict[str, VLLMHead] = field(default_factory=dict)
    client: VLLMClient = field(default_factory=VLLMClient)

    def register(self, head: VLLMHead) -> None:
        self.heads[head.head_id] = head

    def get(self, head_id: str) -> VLLMHead:
        if head_id not in self.heads:
            raise KeyError(f"Unknown vLLM head: {head_id}")
        return self.heads[head_id]

    def by_role(self, role: HeadRole) -> list[VLLMHead]:
        return sorted(
            [h for h in self.heads.values() if h.enabled and h.role == role],
            key=lambda h: (h.priority, h.cost_weight),
        )

    def by_tag(self, tag: str) -> list[VLLMHead]:
        return [h for h in self.heads.values() if h.enabled and tag in h.tags]

    def list_heads(self) -> list[VLLMHead]:
        return list(self.heads.values())

    def chat(self, head_id: str, messages: list[ChatMessage], **kwargs: Any) -> VLLMCompletion:
        return self.client.chat(self.get(head_id), messages, **kwargs)

    def health(self) -> list[HeadHealth]:
        return [self.client.health(h) for h in self.heads.values() if h.enabled]


def default_heads(settings: Settings) -> list[VLLMHead]:
    """Canonical multi-head layout — all assumed behind vLLM OpenAI servers."""
    base = settings.vllm_base_url.rstrip("/")
    return [
        VLLMHead(
            head_id="classifier",
            model=settings.vllm_classifier_model,
            base_url=base,
            role=HeadRole.CLASSIFIER,
            temperature=0.0,
            priority=10,
            cost_weight=0.1,
            tags=["route", "safety"],
        ),
        VLLMHead(
            head_id="router",
            model=settings.vllm_router_model,
            base_url=base,
            role=HeadRole.ROUTER,
            temperature=0.0,
            priority=20,
            cost_weight=0.15,
            tags=["route", "mom"],
        ),
        VLLMHead(
            head_id="reasoner_small",
            model=settings.vllm_small_model,
            base_url=base,
            role=HeadRole.REASONER,
            priority=30,
            cost_weight=0.4,
            tags=["devotion", "general", "fast"],
        ),
        VLLMHead(
            head_id="reasoner_large",
            model=settings.vllm_large_model,
            base_url=base,
            role=HeadRole.REASONER,
            priority=40,
            cost_weight=1.0,
            tags=["devotion", "storykeeper", "deep"],
        ),
        VLLMHead(
            head_id="creator",
            model=settings.vllm_creator_model,
            base_url=base,
            role=HeadRole.CREATOR,
            priority=35,
            cost_weight=0.9,
            tags=["create_3d", "mesh", "vision"],
        ),
        VLLMHead(
            head_id="critic",
            model=settings.vllm_critic_model,
            base_url=base,
            role=HeadRole.CRITIC,
            temperature=0.1,
            priority=50,
            cost_weight=0.5,
            tags=["critique", "eval"],
        ),
        VLLMHead(
            head_id="compiler",
            model=settings.vllm_compiler_model,
            base_url=base,
            role=HeadRole.COMPILER,
            temperature=0.0,
            priority=60,
            cost_weight=0.7,
            tags=["compile", "codegen"],
        ),
        VLLMHead(
            head_id="frontier",
            model=settings.vllm_frontier_model,
            base_url=settings.vllm_frontier_base_url or base,
            role=HeadRole.GENERAL,
            priority=90,
            cost_weight=3.0,
            tags=["frontier", "fallback"],
        ),
    ]


_pool: VLLMHeadPool | None = None


def get_vllm_pool(settings: Settings | None = None) -> VLLMHeadPool:
    global _pool
    if _pool is None:
        cfg = settings or get_settings()
        pool = VLLMHeadPool()
        for head in default_heads(cfg):
            pool.register(head)
        _pool = pool
    return _pool
