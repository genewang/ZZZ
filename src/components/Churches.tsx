import { Reveal } from "./Reveal";
import { churchPoints } from "../data/content";

export function Churches() {
  return (
    <section className="section section--deep" id="churches">
      <div className="shell churches">
        <Reveal>
          <p className="eyebrow">For churches &amp; schools</p>
          <h2 className="section__title">Sunday-ready without the scramble.</h2>
          <p className="section__lede">
            License the same kits and Create tools your families use at home —
            coherent arcs, volunteer-friendly, Zero-Trust controls included.
          </p>
          <a className="btn btn--gold" href="#close">
            Talk to church success
          </a>
        </Reveal>
        <ul className="churches__list">
          {churchPoints.map((point, index) => (
            <Reveal key={point.title} as="li" delay={index * 90}>
              <h3>{point.title}</h3>
              <p>{point.body}</p>
            </Reveal>
          ))}
        </ul>
      </div>
    </section>
  );
}
