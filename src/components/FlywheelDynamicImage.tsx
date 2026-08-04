type Props = {
  active?: boolean;
  showTriple?: boolean;
  className?: string;
};

/**
 * Animated SVG “dynamic image” of Flywheel Engineering + Triple Zero.
 * Standalone asset — also used inside the layers animation.
 */
export function FlywheelDynamicImage({
  active = true,
  showTriple = true,
  className = "",
}: Props) {
  return (
    <svg
      className={`fla-img ${active ? "is-active" : ""} ${showTriple ? "is-triple" : ""} ${className}`}
      viewBox="0 0 320 320"
      role="img"
      aria-label="Flywheel Engineering powered by Zero-Copy, Zero-Trust, and Zero-Token"
    >
      <defs>
        <radialGradient id="fla-img-glow" cx="50%" cy="45%" r="55%">
          <stop offset="0%" stopColor="#e0b34a" stopOpacity="0.28" />
          <stop offset="55%" stopColor="#7eb8d4" stopOpacity="0.08" />
          <stop offset="100%" stopColor="#061824" stopOpacity="0" />
        </radialGradient>
        <filter id="fla-img-soft" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="1.2" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <rect width="320" height="320" fill="transparent" />
      <circle cx="160" cy="160" r="148" fill="url(#fla-img-glow)" />

      {/* Outer ring */}
      <circle
        className="fla-img__ring fla-img__ring--outer"
        cx="160"
        cy="160"
        r="118"
        fill="none"
        stroke="#c4922a"
        strokeOpacity="0.55"
        strokeWidth="2.5"
      />

      {/* Mid ring */}
      <circle
        className="fla-img__ring fla-img__ring--mid"
        cx="160"
        cy="160"
        r="82"
        fill="none"
        stroke="#7eb8d4"
        strokeOpacity="0.45"
        strokeWidth="1.75"
        strokeDasharray="5 7"
      />

      {/* Orbit dots on outer ring (r=118), 120° apart */}
      <g className="fla-img__orbit" filter="url(#fla-img-soft)">
        <circle cx="160" cy="42" r="4.5" fill="#e0b34a" />
        <circle cx="262.2" cy="219" r="4" fill="#7eb8d4" />
        <circle cx="57.8" cy="219" r="4" fill="#6fbf8a" />
      </g>

      {/* Hub */}
      <g className="fla-img__hub" textAnchor="middle">
        <text
          x="160"
          y="154"
          fill="#e0b34a"
          fontFamily="Fraunces, Georgia, serif"
          fontSize="22"
          fontWeight="650"
        >
          Flywheel
        </text>
        <text
          x="160"
          y="176"
          fill="#e0b34a"
          fontFamily="Outfit, system-ui, sans-serif"
          fontSize="9"
          fontWeight="650"
          letterSpacing="2.2"
        >
          ENGINEERING
        </text>
      </g>

      {/* Triple Zero — Copy + Trust top, Token bottom */}
      <g className="fla-img__triple" fontFamily="Outfit, system-ui, sans-serif">
        <g className="fla-img__pill" transform="translate(78 58)">
          <rect
            x="0"
            y="0"
            width="78"
            height="24"
            rx="12"
            fill="rgba(6,24,36,0.92)"
            stroke="rgba(244,248,251,0.22)"
          />
          <text
            x="39"
            y="16"
            textAnchor="middle"
            fill="#f4f8fb"
            fontSize="10"
            fontWeight="650"
          >
            Zero-Copy
          </text>
        </g>
        <g className="fla-img__pill" transform="translate(164 58)">
          <rect
            x="0"
            y="0"
            width="78"
            height="24"
            rx="12"
            fill="rgba(6,24,36,0.92)"
            stroke="rgba(244,248,251,0.22)"
          />
          <text
            x="39"
            y="16"
            textAnchor="middle"
            fill="#f4f8fb"
            fontSize="10"
            fontWeight="650"
          >
            Zero-Trust
          </text>
        </g>
        <g className="fla-img__pill" transform="translate(111 248)">
          <rect
            x="0"
            y="0"
            width="98"
            height="24"
            rx="12"
            fill="rgba(6,24,36,0.92)"
            stroke="rgba(244,248,251,0.22)"
          />
          <text
            x="49"
            y="16"
            textAnchor="middle"
            fill="#f4f8fb"
            fontSize="10"
            fontWeight="650"
          >
            Zero-Token
          </text>
        </g>
      </g>

      <text
        className="fla-img__wm"
        x="12"
        y="312"
        textAnchor="start"
        fill="#e8f0f6"
        fillOpacity="0.38"
        fontFamily="Outfit, system-ui, sans-serif"
        fontSize="8"
        fontWeight="500"
        letterSpacing="0.4"
      >
        Aug01-2026
      </text>
      <text
        className="fla-img__wm"
        x="308"
        y="312"
        textAnchor="end"
        fill="#e8f0f6"
        fillOpacity="0.38"
        fontFamily="Outfit, system-ui, sans-serif"
        fontSize="8"
        fontWeight="500"
        letterSpacing="0.4"
      >
        GeneWang
      </text>
    </svg>
  );
}
