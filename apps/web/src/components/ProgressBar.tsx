export function ProgressBar({ value, colorClass }: { value: number; colorClass?: string }) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className="progress-track">
      <div className={`progress-fill ${colorClass ?? ""}`} style={{ width: `${clamped}%` }} />
    </div>
  );
}
