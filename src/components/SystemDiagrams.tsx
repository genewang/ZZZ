import { useMemo, useState } from "react";
import { Reveal } from "./Reveal";
import { FlywheelLayersAnim } from "./FlywheelLayersAnim";
import {
  archLayers,
  diagramTabs,
  engineeringLayers,
  flowCharts,
  vllmHeads,
} from "../data/diagrams";

function FlowSvg({ chartId }: { chartId: keyof typeof flowCharts }) {
  const chart = flowCharts[chartId];
  const layout = useMemo(() => {
    const nodeW = 168;
    const nodeH = 40;
    const gapY = 52;
    const pad = 20;
    const nodes = chart.nodes.map((label, i) => ({
      id: i,
      label,
      x: pad + 28,
      y: pad + i * gapY,
    }));
    const width = pad * 2 + nodeW + 80;
    const height = pad * 2 + chart.nodes.length * gapY;
    return { nodes, width, height, nodeW, nodeH };
  }, [chart]);

  const backEdges = new Set(
    chart.edges
      .filter(([from, to]) => to <= from)
      .map(([from, to]) => `${from}-${to}`),
  );

  return (
    <div className="flow">
      <svg
        className="flow__svg"
        viewBox={`0 0 ${layout.width} ${layout.height}`}
        role="img"
        aria-label={`${chartId} workflow diagram`}
      >
        {chart.edges.map(([from, to]) => {
          const a = layout.nodes[from];
          const b = layout.nodes[to];
          const isBack = backEdges.has(`${from}-${to}`);
          const x1 = a.x + layout.nodeW / 2;
          const y1 = a.y + layout.nodeH;
          const x2 = b.x + layout.nodeW / 2;
          const y2 = b.y;
          if (isBack) {
            const midX = a.x + layout.nodeW + 36;
            return (
              <path
                key={`${from}-${to}`}
                d={`M ${x1} ${a.y + layout.nodeH / 2} H ${midX} V ${b.y + layout.nodeH / 2} H ${x2}`}
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeDasharray="6 4"
                className="flow__edge flow__edge--back"
              />
            );
          }
          return (
            <line
              key={`${from}-${to}`}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="currentColor"
              strokeWidth="1.5"
              className="flow__edge"
            />
          );
        })}
        {layout.nodes.map((n) => (
          <g key={n.id}>
            <rect
              x={n.x}
              y={n.y}
              width={layout.nodeW}
              height={layout.nodeH}
              rx="8"
              className="flow__node"
            />
            <text
              x={n.x + layout.nodeW / 2}
              y={n.y + 25}
              textAnchor="middle"
              className="flow__label"
            >
              {n.label.length > 28 ? `${n.label.slice(0, 26)}…` : n.label}
            </text>
          </g>
        ))}
      </svg>
      {chart.note ? <p className="flow__note">{chart.note}</p> : null}
    </div>
  );
}

function LayersPanel() {
  return (
    <div className="layers-panel layers-panel--stack">
      <FlywheelLayersAnim />
      <ol className="layers-list">
        {engineeringLayers.map((layer, index) => (
          <li key={layer.id} className="layers-list__item">
            <span className="layers-list__id">{layer.id}</span>
            <div>
              <h3>{layer.name}</h3>
              <p>{layer.owns}</p>
            </div>
            {index < engineeringLayers.length - 1 ? (
              <span className="layers-list__arrow" aria-hidden="true">
                ↓
              </span>
            ) : (
              <span className="layers-list__arrow layers-list__arrow--loop" aria-hidden="true">
                ↺ compounds
              </span>
            )}
          </li>
        ))}
      </ol>
      <FlowSvg chartId="layers" />
    </div>
  );
}

function ArchitecturePanel() {
  return (
    <div className="arch">
      {archLayers.map((layer) => (
        <div
          key={layer.id}
          className={`arch__layer ${"highlight" in layer && layer.highlight ? "arch__layer--hot" : ""}`}
        >
          <div className="arch__head">
            <span>{layer.id}</span>
            <h3>{layer.title}</h3>
          </div>
          <ul>
            {layer.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

function VllmPanel() {
  return (
    <div className="vllm-panel">
      <ul className="vllm-heads">
        {vllmHeads.map((head) => (
          <li key={head.id}>
            <strong>{head.id}</strong>
            <span>{head.role}</span>
            <em>{head.cost}</em>
          </li>
        ))}
      </ul>
      <FlowSvg chartId="vllm" />
    </div>
  );
}

function TrustSplit() {
  return (
    <div className="trust-split">
      <div>
        <h3>Outside the jail</h3>
        <ul>
          <li>Open chat without Approve</li>
          <li>Raw family media export</li>
          <li>Unscoped web tools for kids</li>
          <li>Off-doctrine publish</li>
        </ul>
      </div>
      <div>
        <h3>Inside Zero-Trust harness</h3>
        <ul>
          <li>Gated devotion (reasoner heads)</li>
          <li>Create Studio graph (creator → critic)</li>
          <li>StoryKeeper drafts</li>
          <li>Church shared prompts</li>
        </ul>
      </div>
    </div>
  );
}

function DiagramBody({ active }: { active: string }) {
  switch (active) {
    case "flywheel-eng":
      return <FlywheelLayersAnim />;
    case "layers":
      return <LayersPanel />;
    case "architecture":
      return <ArchitecturePanel />;
    case "vllm":
      return <VllmPanel />;
    case "engine":
      return <FlowSvg chartId="engine" />;
    case "monthly":
      return <FlowSvg chartId="monthly" />;
    case "create":
      return <FlowSvg chartId="create" />;
    case "flywheel":
      return <FlowSvg chartId="flywheel" />;
    case "trust":
      return (
        <>
          <TrustSplit />
          <FlowSvg chartId="trust" />
        </>
      );
    default:
      return <FlywheelLayersAnim />;
  }
}

export function SystemDiagrams() {
  const [active, setActive] = useState(diagramTabs[0].id);
  const tab = diagramTabs.find((t) => t.id === active) ?? diagramTabs[0];

  return (
    <section className="section section--deep" id="system">
      <div className="shell">
        <Reveal>
          <p className="eyebrow">System &amp; workflows</p>
          <h2 className="section__title">How the platform actually runs.</h2>
          <p className="section__lede">
            Six reusable engineering layers on a vLLM multi-head fabric — plus
            Flywheel Engineering (Triple Zero) as the compounding layer beyond
            Harness · Loop · Graph.
          </p>
        </Reveal>

        <Reveal delay={80}>
          <div className="diagram-tabs" role="tablist" aria-label="System diagrams">
            {diagramTabs.map((item) => (
              <button
                key={item.id}
                type="button"
                role="tab"
                aria-selected={active === item.id}
                className={active === item.id ? "is-active" : ""}
                onClick={() => setActive(item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>

          <p className="diagram-summary">{tab.summary}</p>

          <div className="diagram-panel" role="tabpanel" key={active}>
            <DiagramBody active={active} />
          </div>
        </Reveal>
      </div>
    </section>
  );
}
