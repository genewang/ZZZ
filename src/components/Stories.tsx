import { Reveal } from "./Reveal";
import { testimonials } from "../data/content";

export function Stories() {
  return (
    <section className="section section--foam" id="stories">
      <div className="shell">
        <Reveal>
          <p className="eyebrow eyebrow--dark">Loved by families</p>
          <h2 className="section__title section__title--dark">
            Real nights. Real keepsakes.
          </h2>
        </Reveal>
        <div className="stories">
          {testimonials.map((item, index) => (
            <Reveal
              key={item.name}
              as="figure"
              className="story"
              delay={index * 100}
            >
              <blockquote>“{item.quote}”</blockquote>
              <figcaption>
                <strong>{item.name}</strong>
                <span>{item.role}</span>
              </figcaption>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
