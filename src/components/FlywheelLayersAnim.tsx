import { useEffect, useState, type CSSProperties } from "react";
import { FlywheelDynamicImage } from "./FlywheelDynamicImage";

/**
 * Short-style layered agent animation inspired by
 * Harness → Loop · Graph engineering explainers, extended with
 * Flywheel Engineering driven by Triple Zero.
 * Reference pattern: https://youtube.com/shorts/b5IF6co4Wd0
 */

const STAGES = [
  { id: "harness", label: "Harness", sub: "" },
  { id: "loop", label: "Loop", sub: "" },
  { id: "graph", label: "Graph", sub: "" },
  { id: "flywheel", label: "Flywheel", sub: "Your innovation · compounds" },
] as const;

const TRIPLE = [
  { id: "copy", label: "Zero-Copy", hint: "Plasma / Arrow" },
  { id: "trust", label: "Zero-Trust", hint: "WASM jail" },
  { id: "token", label: "Zero-Token", hint: "MoM · compile" },
] as const;

export function FlywheelLayersAnim() {
  const [stage, setStage] = useState(0);
  const [playing, setPlaying] = useState(true);

  useEffect(() => {
    if (!playing) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setStage(STAGES.length);
      return;
    }
    // Hold the final Flywheel + Triple Zero scene longer
    const delay = stage >= STAGES.length ? 4200 : 1600;
    const id = window.setTimeout(() => {
      setStage((s) => (s >= STAGES.length ? 0 : s + 1));
    }, delay);
    return () => window.clearTimeout(id);
  }, [playing, stage]);

  const showFlywheel = stage >= 3;
  const showTriple = stage >= 4 || stage === STAGES.length;

  return (
    <div className="fla" aria-label="Harness Loop Graph Flywheel engineering animation">
      <div className="fla__chrome">
        <p className="fla__eyebrow">Agent engineering layers</p>
        <h3 className="fla__title">
          Harness · Loop · Graph · <em>Flywheel</em>
        </h3>
        <p className="fla__lede">
          Beyond the three layers — Flywheel Engineering, powered by Triple Zero,
          turns every run into cheaper, safer, compiled practice.
        </p>
      </div>

      <div className="fla__stage" data-stage={stage}>
        <div className="fla__stack" aria-hidden="true">
          {STAGES.slice(0, 3).map((item, index) => {
            const visible = stage > index;
            const active = stage === index + 1 || (stage > 3 && index === 2);
            return (
              <div
                key={item.id}
                className={`fla__plate fla__plate--${item.id} ${visible ? "is-in" : ""} ${active ? "is-active" : ""}`}
                style={{ "--i": index } as CSSProperties}
              >
                <span className="fla__plate-label">{item.label}</span>
                {item.sub ? <span className="fla__plate-sub">{item.sub}</span> : null}
              </div>
            );
          })}

          <div className={`fla__flywheel ${showFlywheel ? "is-in" : ""}`}>
            <FlywheelDynamicImage active={showFlywheel} showTriple={showTriple} />
          </div>
        </div>

        <ol className="fla__legend">
          {STAGES.map((item, index) => (
            <li
              key={item.id}
              className={`${stage > index ? "is-on" : ""} ${item.id === "flywheel" ? "fla__legend--innov" : ""}`}
            >
              <button
                type="button"
                onClick={() => {
                  setPlaying(false);
                  setStage(index + 1);
                }}
              >
                <strong>{item.label} Engineering</strong>
                {item.sub ? <span>{item.sub}</span> : null}
              </button>
            </li>
          ))}
        </ol>
      </div>

      <div className="fla__footer">
        <div className={`fla__triple ${showTriple ? "is-in" : ""}`}>
          {TRIPLE.map((t) => (
            <div key={t.id} className={`fla__pill fla__pill--${t.id}`}>
              <strong>{t.label}</strong>
              <span>{t.hint}</span>
            </div>
          ))}
        </div>
        <div className="fla__controls">
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={() => {
              setPlaying((p) => !p);
              if (!playing) setStage(0);
            }}
          >
            {playing ? "Pause" : "Replay"}
          </button>
          <a
            className="fla__ref"
            href="/flywheel-layers.html"
            target="_blank"
            rel="noreferrer"
          >
            Open layers SVG
          </a>
          <a
            className="fla__ref"
            href="/flywheel-engineering.html"
            target="_blank"
            rel="noreferrer"
          >
            Open shareable image
          </a>
          <a
            className="fla__ref"
            href="/flywheel-layers.svg"
            download="flywheel-layers.svg"
          >
            Download layers SVG
          </a>
          <a
            className="fla__ref"
            href="/flywheel-engineering.svg"
            download="flywheel-engineering.svg"
          >
            Download SVG
          </a>
          <a
            className="fla__ref"
            href="https://youtube.com/shorts/b5IF6co4Wd0"
            target="_blank"
            rel="noreferrer"
          >
            Inspired by Harness · Loop · Graph
          </a>
        </div>
      </div>
    </div>
  );
}
