import type { CSSProperties, ReactNode } from "react";
import { useInView } from "../hooks/useInView";

type RevealProps = {
  children: ReactNode;
  className?: string;
  /** Stagger delay in ms for sibling reveals */
  delay?: number;
  as?: "div" | "section" | "article" | "li" | "figure";
};

export function Reveal({
  children,
  className = "",
  delay = 0,
  as: Tag = "div",
}: RevealProps) {
  const [ref, inView] = useInView<HTMLDivElement>();

  const style = {
    "--reveal-delay": `${delay}ms`,
  } as CSSProperties;

  return (
    <Tag
      ref={ref as never}
      className={`reveal ${inView ? "reveal--in" : ""} ${className}`.trim()}
      style={style}
    >
      {children}
    </Tag>
  );
}
