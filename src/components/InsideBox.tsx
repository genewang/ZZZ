import { Reveal } from "./Reveal";
import { boxContents } from "../data/content";

export function InsideBox() {
  return (
    <section className="section section--foam" id="box">
      <div className="shell">
        <Reveal>
          <p className="eyebrow eyebrow--dark">Inside every box</p>
          <h2 className="section__title section__title--dark">
            Designed to inspire — and to finish in one sitting.
          </h2>
        </Reveal>
        <ul className="box-grid">
          {boxContents.map((item, index) => (
            <Reveal
              key={item.title}
              as="li"
              className="box-grid__item"
              delay={index * 80}
            >
              <span className="box-grid__num">0{index + 1}</span>
              <h3>{item.title}</h3>
              <p>{item.body}</p>
            </Reveal>
          ))}
        </ul>
      </div>
    </section>
  );
}
