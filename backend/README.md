# Triple Zero Backend

Reusable multi-agent / multi-head kernel for **kits4kid** and future verticals.

## Engineering stack

```
Prompt → Context → Harness → Loop → Graph → Flywheel
         ▲                                    │
         └──────── vLLM multi-head fabric ────┘
```

| Layer | Responsibility |
| --- | --- |
| **Prompt** | Templates, system packs, few-shots, schemas |
| **Context** | Zero-Copy object refs, memory, window packing |
| **Harness** | Tools, deny-by-default jail, parent Approve |
| **Loop** | Generate → critique → refine under budget (vLLM) |
| **Graph** | Multi-agent DAGs with head affinity |
| **Flywheel** | Traces, corrections, Zero-Token compile candidates |

## vLLM multi-head fabric

All adaptable LLMs are registered as **Heads** behind vLLM OpenAI-compatible servers:

| Head | Role | Default model env |
| --- | --- | --- |
| `classifier` / `router` | MoM routing | `TZ_VLLM_CLASSIFIER_MODEL` |
| `reasoner_small` / `reasoner_large` | Devotion / deep | `TZ_VLLM_*_MODEL` |
| `creator` | Create Studio | `TZ_VLLM_CREATOR_MODEL` |
| `critic` | Loop critique | `TZ_VLLM_CRITIC_MODEL` |
| `compiler` | Compiled AI | `TZ_VLLM_COMPILER_MODEL` |
| `frontier` | Costly fallback | `TZ_VLLM_FRONTIER_*` |

Without a live vLLM cluster, the client **stubs** deterministically so local tests still pass.

## Run

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Point heads at your vLLM servers:

```bash
export TZ_VLLM_BASE_URL=http://127.0.0.1:8001
export TZ_VLLM_SMALL_MODEL=meta-llama/Llama-3.2-3B-Instruct
export TZ_VLLM_LARGE_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

## Key routes

- `GET /v1/architecture` — six-layer map + heads + graphs
- `GET /v1/vllm/heads` — head registry + health
- `POST /v1/engine/run` — vertical-agnostic engine entry
- `POST /v1/create/scene` — kits4kid Create Studio graph
- `POST /v1/inference` — kits4kid devotion via engine
- `GET /v1/flywheel` — action data + compile candidates

## Tests

```bash
pytest -q
```
