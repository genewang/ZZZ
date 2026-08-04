export function SiteFooter() {
  return (
    <footer className="footer">
      <div className="shell footer__grid">
        <div>
          <p className="footer__brand">
            <span className="nav__mark" aria-hidden="true" />
            kits4kid
          </p>
          <p className="footer__note">
            Monthly Bible kits + supervised Create Studio for families,
            churches, and schools.
          </p>
        </div>
        <div>
          <p className="footer__head">Explore</p>
          <a href="#kits">Kits</a>
          <a href="#create">Create Studio</a>
          <a href="#system">System</a>
          <a href="#churches">Churches</a>
          <a href="#faq">FAQ</a>
        </div>
        <div>
          <p className="footer__head">Company</p>
          <a href="#trust">Safety</a>
          <a href="#how">How it works</a>
          <a href="#stories">Stories</a>
        </div>
      </div>
      <div className="shell footer__legal">
        <p>© {new Date().getFullYear()} kits4kid. All rights reserved.</p>
      </div>
    </footer>
  );
}
