export function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero__atmosphere" aria-hidden="true">
        <div className="hero__glow hero__glow--a" />
        <div className="hero__glow hero__glow--b" />
        <div className="hero__scene">
          <div className="hero__kit hero__kit--enter">
            <span className="hero__kit-lid" />
            <span className="hero__kit-body" />
            <span className="hero__kit-label">Sprout</span>
          </div>
          <div className="hero__figure hero__figure--a" />
          <div className="hero__figure hero__figure--b" />
          <div className="hero__figure hero__figure--c" />
        </div>
        <div className="hero__horizon" />
      </div>

      <div className="hero__content">
        <p className="hero__brand hero__anim" style={{ "--d": "0ms" } as never}>
          kits4kid
        </p>
        <h1
          className="hero__title hero__anim"
          style={{ "--d": "120ms" } as never}
        >
          Open. Make. Believe.
        </h1>
        <p className="hero__lede hero__anim" style={{ "--d": "220ms" } as never}>
          Monthly Bible kits for curious kids — plus a supervised Create Studio
          that turns stories into printable 3D scenes families can hold.
        </p>
        <div
          className="hero__actions hero__anim"
          style={{ "--d": "320ms" } as never}
        >
          <a className="btn btn--gold" href="#kits">
            Start exploring
          </a>
          <a className="btn btn--ghost" href="#create">
            Try Create Studio
          </a>
        </div>
      </div>
    </section>
  );
}
