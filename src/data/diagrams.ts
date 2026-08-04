export type DiagramTab = {
  id: string;
  label: string;
  summary: string;
};

export const diagramTabs: DiagramTab[] = [
  {
    id: "flywheel-eng",
    label: "Flywheel Eng",
    summary:
      "Short-style layers: Harness → Loop → Graph → Flywheel Engineering powered by Triple Zero",
  },
  {
    id: "layers",
    label: "6 Layers",
    summary:
      "Prompt → Context → Harness → Loop → Graph → Flywheel — reusable engineering stack",
  },
  {
    id: "architecture",
    label: "Architecture",
    summary:
      "Experience surfaces on vLLM multi-head agents over the Triple Zero kernel",
  },
  {
    id: "vllm",
    label: "vLLM heads",
    summary:
      "Mixture-of-Models fabric: cache → compiled → role heads → frontier",
  },
  {
    id: "engine",
    label: "Engine run",
    summary:
      "Vertical-agnostic /v1/engine/run path through all six layers",
  },
  {
    id: "create",
    label: "Create Studio",
    summary:
      "Multi-agent graph: creator head → critic head → parent Approve → print",
  },
  {
    id: "monthly",
    label: "Monthly kit",
    summary: "Subscription loop from pick → craft → create → renew",
  },
  {
    id: "flywheel",
    label: "Flywheel",
    summary:
      "Action traces → labelling → evals → Zero-Token compile candidates",
  },
  {
    id: "trust",
    label: "Zero-Trust",
    summary: "Harness jail boundary and parent Approve quarantine",
  },
];

export const engineeringLayers = [
  {
    id: "01",
    name: "Prompt Engineering",
    owns: "Templates, system packs, few-shots, output schemas",
  },
  {
    id: "02",
    name: "Context Engineering",
    owns: "Retrieval, Zero-Copy refs, window packing, session memory",
  },
  {
    id: "03",
    name: "Harness Engineering",
    owns: "Tool registry, WASM/policy jail, validators, Approve gates",
  },
  {
    id: "04",
    name: "Loop Engineering",
    owns: "Generate → critique → refine, token budgets, stop criteria",
  },
  {
    id: "05",
    name: "Graph Engineering",
    owns: "Multi-agent DAGs, vLLM head affinity, handoffs, shared plane",
  },
  {
    id: "06",
    name: "Flywheel Engineering",
    owns: "Traces, labelling, eval suites, compiled Zero-Token paths",
  },
] as const;

export const archLayers = [
  {
    id: "L0",
    title: "Engineering progression",
    items: [
      "Prompt",
      "Context",
      "Harness",
      "Loop",
      "Graph",
      "Flywheel",
    ],
  },
  {
    id: "L1",
    title: "Experience surfaces",
    items: [
      "Monthly kits",
      "Create Studio",
      "Avarta",
      "StoryKeeper",
      "Church admin",
    ],
  },
  {
    id: "L2",
    title: "vLLM multi-head agents",
    items: [
      "classifier",
      "router",
      "reasoner",
      "creator",
      "critic",
      "compiler",
      "frontier",
    ],
  },
  {
    id: "L3",
    title: "Triple Zero kernel",
    items: [
      "Zero-Copy (Plasma/Arrow)",
      "Zero-Trust (WASM jail)",
      "Zero-Token (MoM + compile)",
    ],
    highlight: true,
  },
  {
    id: "L4",
    title: "Domain data",
    items: [
      "Scripture corpus",
      "Craft assets",
      "Family media",
      "Action traces",
    ],
  },
] as const;

export const vllmHeads = [
  {
    id: "classifier / router",
    role: "MoM classify & route",
    cost: "lowest",
  },
  {
    id: "reasoner_small",
    role: "Fast devotion / general",
    cost: "low",
  },
  {
    id: "reasoner_large",
    role: "Deep / StoryKeeper",
    cost: "medium",
  },
  {
    id: "creator",
    role: "Create Studio mesh briefs",
    cost: "medium",
  },
  {
    id: "critic",
    role: "Loop critique / eval",
    cost: "low",
  },
  {
    id: "compiler",
    role: "Compiled AI / Zero-Token",
    cost: "medium",
  },
  {
    id: "frontier",
    role: "Costly fallback",
    cost: "high",
  },
] as const;

export const flowCharts: Record<
  string,
  { nodes: string[]; edges: [number, number][]; note?: string }
> = {
  layers: {
    nodes: [
      "Prompt Engineering",
      "Context Engineering",
      "Harness Engineering",
      "Loop Engineering",
      "Graph Engineering",
      "Flywheel Engineering",
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [5, 0],
    ],
    note: "Flywheel compounds back into better prompts, context packs, and compiled paths.",
  },
  vllm: {
    nodes: [
      "Incoming request",
      "Semantic cache?",
      "Compiled path?",
      "Role-fit vLLM head",
      "Frontier fallback",
      "Completion + meter",
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 5],
      [2, 4],
      [4, 5],
      [1, 5],
    ],
    note: "Cache and compiled paths bill zero tokens; heads run on vLLM continuous batching.",
  },
  engine: {
    nodes: [
      "EngineRequest",
      "Render prompt",
      "Pack context (Zero-Copy)",
      "Harness gate",
      "Loop or Graph",
      "vLLM head(s)",
      "Flywheel record",
      "EngineResponse",
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [5, 6],
      [6, 7],
      [3, 7],
    ],
    note: "Deny/hold can short-circuit to response; drafts still land in quarantine objects.",
  },
  monthly: {
    nodes: [
      "Pick kit line",
      "Monthly ship",
      "Open the box",
      "Hands-on craft",
      "Create prompt",
      "Parent Approve",
      "Keep / print",
      "Next month arc",
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [5, 6],
      [6, 7],
      [7, 1],
    ],
    note: "Dashed return = subscription renew into the next scripture arc.",
  },
  create: {
    nodes: [
      "Story or Sketch",
      "Prompt + Context pack",
      "Harness jail gate",
      "creator head (vLLM)",
      "critic head loop",
      "Parent Approve",
      "export_mesh / print",
      "Flywheel trace",
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [5, 6],
      [6, 7],
      [5, 1],
    ],
    note: "Graph kits4kid.create_and_check — reject path returns for parent edits.",
  },
  flywheel: {
    nodes: [
      "Household adoption",
      "Action traces",
      "Corrections / outcomes",
      "Labelling signals",
      "Eval suites",
      "Tune heads / prompts",
      "Compile candidate",
      "Zero-Token path",
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [5, 6],
      [6, 7],
      [7, 0],
    ],
    note: "Repeated workflows graduate to compiled free execution via MoM router.",
  },
  trust: {
    nodes: [
      "Child / agent action",
      "Harness evaluate",
      "Quarantine HOLD",
      "Parent Approve",
      "Speak / print ALLOW",
      "Flywheel + audit",
    ],
    edges: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [3, 0],
      [1, 5],
    ],
    note: "Hard denies never enter quarantine — structurally impossible in the jail.",
  },
};
