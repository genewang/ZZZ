import { useState } from "react";
import { Reveal } from "./Reveal";
import { faqs } from "../data/content";

export function Faq() {
  const [open, setOpen] = useState(0);

  return (
    <section className="section section--foam" id="faq">
      <div className="shell faq">
        <Reveal>
          <p className="eyebrow eyebrow--dark">FAQ</p>
          <h2 className="section__title section__title--dark">
            Questions before the first box.
          </h2>
        </Reveal>
        <Reveal className="faq__list" delay={80}>
          {faqs.map((item, index) => {
            const isOpen = open === index;
            return (
              <div
                key={item.q}
                className={`faq__item ${isOpen ? "faq__item--open" : ""}`}
              >
                <button
                  type="button"
                  className="faq__q"
                  aria-expanded={isOpen}
                  onClick={() => setOpen(isOpen ? -1 : index)}
                >
                  <span>{item.q}</span>
                  <span className="faq__icon" aria-hidden="true">
                    {isOpen ? "−" : "+"}
                  </span>
                </button>
                <div className="faq__a-wrap">
                  <p className="faq__a">{item.a}</p>
                </div>
              </div>
            );
          })}
        </Reveal>
      </div>
    </section>
  );
}
