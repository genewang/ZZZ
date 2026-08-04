import { useEffect, useState } from "react";
import { Reveal } from "./Reveal";
import { createModes, createPresets } from "../data/content";

type Phase = "idle" | "generating" | "ready";

export function CreateStudio() {
  const [mode, setMode] = useState<(typeof createModes)[number]["id"]>("text");
  const [prompt, setPrompt] = useState<string>(createPresets[0].prompt);
  const [activePreset, setActivePreset] = useState(0);
  const [phase, setPhase] = useState<Phase>("idle");
  const [approved, setApproved] = useState(false);

  useEffect(() => {
    if (phase !== "generating") return;
    const timer = window.setTimeout(() => setPhase("ready"), 1600);
    return () => window.clearTimeout(timer);
  }, [phase]);

  const preset = createPresets[activePreset];

  function runGenerate() {
    setApproved(false);
    setPhase("generating");
  }

  return (
    <section className="section section--deep" id="create">
      <div className="shell">
        <Reveal>
          <p className="eyebrow">Create Studio</p>
          <h2 className="section__title">
            From Bible story to something you can hold.
          </h2>
          <p className="section__lede">
            Text or sketch in. A kid-safe 3D scene out — printable, shareable,
            and locked behind a parent Approve. The easiest way to make faith
            tangible.
          </p>
        </Reveal>

        <Reveal className="create" delay={100}>
          <div className="create__panel">
            <div className="create__tabs" role="tablist" aria-label="Create mode">
              {createModes.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  role="tab"
                  aria-selected={mode === item.id}
                  className={mode === item.id ? "is-active" : ""}
                  onClick={() => setMode(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <div key={mode} className="create__mode-panel">
              {mode === "text" ? (
                <>
                  <label className="create__label" htmlFor="create-prompt">
                    Describe a scene
                  </label>
                  <textarea
                    id="create-prompt"
                    className="create__input"
                    rows={3}
                    value={prompt}
                    onChange={(e) => {
                      setPrompt(e.target.value);
                      setPhase("idle");
                      setApproved(false);
                    }}
                  />
                  <div className="create__presets">
                    {createPresets.map((item, index) => (
                      <button
                        key={item.title}
                        type="button"
                        className={
                          index === activePreset ? "chip chip--active" : "chip"
                        }
                        onClick={() => {
                          setActivePreset(index);
                          setPrompt(item.prompt);
                          setPhase("idle");
                          setApproved(false);
                        }}
                      >
                        {item.title}
                      </button>
                    ))}
                  </div>
                </>
              ) : (
                <div className="create__upload">
                  <div className="create__upload-art" aria-hidden="true" />
                  <p>Drop a child’s sketch of a Bible scene</p>
                  <span>PNG or JPG · parent review before generate</span>
                </div>
              )}
            </div>

            <div className="create__actions">
              <button
                type="button"
                className="btn btn--gold"
                onClick={runGenerate}
                disabled={phase === "generating"}
              >
                {phase === "generating" ? "Shaping…" : "Generate scene"}
              </button>
              <p className="create__hint">Parent gate required before print</p>
            </div>
          </div>

          <div className="create__stage" aria-live="polite">
            <div
              className={`model ${phase === "generating" ? "model--spin" : ""} ${
                phase === "ready" ? "model--ready" : ""
              }`}
            >
              <div className="model__ring" aria-hidden="true" />
              <div className="model__orb" />
              <div className="model__mesh" />
              <div className="model__base" />
            </div>

            <div key={phase} className="create__meta create__meta--fade">
              {phase === "idle" ? (
                <p>Pick a preset or write your own — then generate.</p>
              ) : null}
              {phase === "generating" ? (
                <p>Compiling a kid-safe mesh for {preset.title}…</p>
              ) : null}
              {phase === "ready" ? (
                <>
                  <p className="create__ready-title">
                    {preset.title}{" "}
                    <span className="create__tag">{preset.tag}</span>
                  </p>
                  <p>Watertight · Print-ready · Age-styled</p>
                  <button
                    type="button"
                    className={`btn ${approved ? "btn--leaf btn--pop" : "btn--ghost"}`}
                    onClick={() => setApproved(true)}
                  >
                    {approved ? "Approved · ready to print" : "Parent Approve"}
                  </button>
                </>
              ) : null}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
