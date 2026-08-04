import { useEffect, useState } from "react";
import { navLinks } from "../data/content";

export function PromoBar() {
  const [open, setOpen] = useState(true);
  if (!open) return null;

  return (
    <div className="promo">
      <p>
        First box on us for new families — use code <strong>DAWN40</strong>
      </p>
      <button
        type="button"
        className="promo__close"
        aria-label="Dismiss promotion"
        onClick={() => setOpen(false)}
      >
        ×
      </button>
    </div>
  );
}

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`nav ${scrolled ? "nav--solid" : ""}`}>
      <button
        type="button"
        className="nav__menu"
        aria-expanded={menuOpen}
        aria-controls="mobile-nav"
        onClick={() => setMenuOpen((v) => !v)}
      >
        Menu
      </button>

      <a className="nav__brand" href="#top">
        <span className="nav__mark" aria-hidden="true" />
        kits4kid
      </a>

      <nav className="nav__links" aria-label="Primary">
        {navLinks.map((link) => (
          <a key={link.href} href={link.href}>
            {link.label}
          </a>
        ))}
      </nav>

      <div className="nav__actions">
        <a className="nav__ghost" href="#faq">
          Sign in
        </a>
        <a className="btn btn--gold btn--sm" href="#kits">
          Start exploring
        </a>
      </div>

      {menuOpen ? (
        <div className="nav__drawer" id="mobile-nav">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <a href="#kits" onClick={() => setMenuOpen(false)}>
            Start exploring
          </a>
        </div>
      ) : null}
    </header>
  );
}
