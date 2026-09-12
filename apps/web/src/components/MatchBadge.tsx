const LABELS: Record<string, { text: string; className: string }> = {
  STRONG_MATCH: { text: "Strong match", className: "badge-strong" },
  PARTIAL_MATCH: { text: "Partial match", className: "badge-partial" },
  WEAK_MATCH: { text: "Weak match", className: "badge-weak" },
  MISSING: { text: "Missing", className: "badge-missing" },
  CRITICAL: { text: "Critical", className: "badge-missing" },
  HIGH: { text: "High", className: "badge-weak" },
  MEDIUM: { text: "Medium", className: "badge-partial" },
  LOW: { text: "Low", className: "badge-neutral" },
};

export function MatchBadge({ value }: { value: string }) {
  const meta = LABELS[value] ?? { text: value, className: "badge-neutral" };
  return <span className={`badge ${meta.className}`}>{meta.text}</span>;
}
