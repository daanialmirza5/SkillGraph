"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { UserSkillCapability } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { ProgressBar } from "@/components/ProgressBar";

const FILTERS = ["ALL", "STRONG", "DEVELOPING", "WEAK", "EVIDENCE_GAP"] as const;
type Filter = (typeof FILTERS)[number];

const LEVEL_COLOR: Record<string, string> = {
  "EXPERT-LIKE": "bg-emerald-500",
  STRONG: "bg-emerald-500",
  PRACTICAL: "bg-brand-500",
  DEVELOPING: "bg-amber-500",
  FOUNDATIONAL: "bg-rose-400",
};

export default function SkillsPage() {
  const [filter, setFilter] = useState<Filter>("ALL");
  const { data, isLoading } = useQuery({ queryKey: ["my-skill-graph"], queryFn: () => api.get<UserSkillCapability[]>("/api/skills/me/graph") });

  const filtered = useMemo(() => {
    if (!data) return [];
    switch (filter) {
      case "STRONG":
        return data.filter((s) => s.level === "STRONG" || s.level === "EXPERT-LIKE");
      case "DEVELOPING":
        return data.filter((s) => s.level === "DEVELOPING" || s.level === "PRACTICAL");
      case "WEAK":
        return data.filter((s) => s.level === "FOUNDATIONAL" && s.evidence_count > 0);
      case "EVIDENCE_GAP":
        return data.filter((s) => s.is_evidence_gap);
      default:
        return data;
    }
  }, [data, filter]);

  return (
    <div>
      <PageHeader title="My Skills" subtitle="Evidence-based capability across every skill you've claimed or demonstrated." />

      <div className="mb-4 flex gap-2">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition ${
              filter === f ? "bg-brand-600 text-white" : "bg-white text-ink-600 hover:bg-ink-50"
            } border border-ink-200`}
          >
            {f.replace("_", " ")}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-ink-400">Loading skills...</p>}

      <div className="card divide-y divide-ink-100">
        {filtered.map((s) => (
          <div key={s.skill.id} className="flex items-center gap-4 px-5 py-3.5">
            <div className="w-48 shrink-0">
              <div className="text-sm font-medium text-ink-900">{s.skill.name}</div>
              <div className="text-[11px] text-ink-400">
                {s.evidence_count} evidence item{s.evidence_count === 1 ? "" : "s"} · {s.confidence} confidence
              </div>
            </div>
            <div className="flex-1">
              <ProgressBar value={s.score} colorClass={LEVEL_COLOR[s.level]} />
            </div>
            <div className="w-24 shrink-0 text-right text-sm font-medium text-ink-700">{s.score}/100</div>
            <div className="w-32 shrink-0 text-right text-xs font-medium text-ink-500">{s.level}</div>
            {s.is_evidence_gap && <span className="badge badge-missing shrink-0">Evidence gap</span>}
          </div>
        ))}
        {filtered.length === 0 && !isLoading && <p className="px-5 py-6 text-sm text-ink-400">No skills match this filter.</p>}
      </div>
    </div>
  );
}
