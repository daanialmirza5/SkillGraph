export function Disclaimer({ text }: { text?: string }) {
  return (
    <p className="mt-8 rounded-lg border border-ink-200 bg-ink-50 p-3 text-[11px] leading-relaxed text-ink-500">
      {text ??
        "SkillGraph uses synthetic demonstration profiles, roles, skills, and evidence. Readiness scores and capability indicators are analytical estimates, not hiring decisions, professional certifications, or guarantees of employment."}
    </p>
  );
}
