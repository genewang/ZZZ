import { Reveal } from "./Reveal";
import { howSteps } from "../data/content";

export function HowItWorks() {
  return (
    <section className="section section--foam" id="how">
      <div className="shell">
        <Reveal>
          <p className="eyebrow eyebrow--dark">How it works</p>
          <h2 className="section__title section__title--dark">
            Fun &amp; faithful projects for every age
          </h2>
        </Reveal>
        <ol className="steps">
          {howSteps.map((step, index) => (
            <Reveal key={step.step} as="li" className="steps__item" delay={index * 90}>
              <span className="steps__num">{step.step}</span>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </Reveal>
          ))}
        </ol>
      </div>
    </section>
  );
}
