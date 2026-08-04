import { useEffect, useState, type CSSProperties } from "react";
import { Reveal } from "./Reveal";
import { kitLines } from "../data/content";

export function Kits() {
  const [activeId, setActiveId] = useState(kitLines[1].id);
  const [detailKey, setDetailKey] = useState(0);
  const active = kitLines.find((k) => k.id === activeId) ?? kitLines[1];

  useEffect(() => {
    setDetailKey((k) => k + 1);
  }, [activeId]);

  return (
    <section className="section section--ink" id="kits">
      <div className="shell">
        <Reveal>
          <p className="eyebrow">Subscriptions</p>
          <h2 className="section__title">Pick a line. Grow with them.</h2>
          <p className="section__lede">
            Like the best crate clubs — but every month points to scripture,
            craft, and a Create prompt your child can finish with you.
          </p>
        </Reveal>

        <div className="kits">
          <Reveal className="kits__grid" delay={80}>
            {kitLines.map((kit) => {
              const selected = kit.id === activeId;
              return (
                <button
                  key={kit.id}
                  type="button"
                  className={`kit-card ${selected ? "kit-card--active" : ""}`}
                  style={{ "--kit-accent": kit.accent } as CSSProperties}
                  aria-pressed={selected}
                  onClick={() => setActiveId(kit.id)}
                >
                  <span className="kit-card__ages">{kit.ages}</span>
                  <span className="kit-card__name">{kit.name}</span>
                  <span className="kit-card__focus">{kit.focus}</span>
                </button>
              );
            })}
          </Reveal>

          <div
            key={detailKey}
            className="kit-detail kit-detail--swap"
            style={{ "--kit-accent": active.accent } as CSSProperties}
          >
            <p className="kit-detail__ages">{active.ages}</p>
            <h3>{active.name}</h3>
            <p className="kit-detail__blurb">{active.blurb}</p>
            <ul className="kit-detail__includes">
              {active.includes.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <a className="btn btn--gold" href="#close">
              Get {active.name} · from $29/mo
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
