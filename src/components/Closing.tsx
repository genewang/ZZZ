import { Reveal } from "./Reveal";

export function Closing() {
  return (
    <section className="closing" id="close">
      <Reveal className="shell closing__inner">
        <p className="closing__brand">kits4kid</p>
        <h2>Start creating faith your family can hold.</h2>
        <p>
          No seminary degree required. First box ships with a Create Studio
          credit and parent-gated Avarta ready when you are.
        </p>
        <div className="hero__actions" style={{ justifyContent: "center" }}>
          <a className="btn btn--gold" href="#kits">
            Start exploring
          </a>
          <a className="btn btn--ghost" href="#create">
            Generate a free scene
          </a>
        </div>
      </Reveal>
    </section>
  );
}
