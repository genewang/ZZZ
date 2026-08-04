import { Reveal } from "./Reveal";
import { trustPoints } from "../data/content";

export function Trust() {
  return (
    <section className="section section--ink" id="trust">
      <div className="shell">
        <Reveal>
          <p className="eyebrow">Built for families</p>
          <h2 className="section__title">AI that waits for you.</h2>
          <p className="section__lede">
            The tech moat shows up as trust you can feel — not jargon. Parent
            gates, sealed data, models born to print.
          </p>
        </Reveal>
        <ul className="trust">
          {trustPoints.map((point, index) => (
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
