"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { api } from "@/lib/api";
import { Role, RoleFitSummary } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { ProgressBar } from "@/components/ProgressBar";

export default function RolesPage() {
  const [category, setCategory] = useState<string>("ALL");
  const { data: roles, isLoading } = useQuery({ queryKey: ["roles"], queryFn: () => api.get<Role[]>("/api/roles") });
  const { data: bestFit } = useQuery({ queryKey: ["best-fit"], queryFn: () => api.get<RoleFitSummary[]>("/api/roles/best-fit") });

  const categories = Array.from(new Set((roles ?? []).map((r) => r.category)));
  const filtered = (roles ?? []).filter((r) => category === "ALL" || r.category === category);
  const readinessByRole = new Map((bestFit ?? []).map((r) => [r.role.id, r.readiness]));

  return (
    <div>
      <PageHeader title="Role Explorer" subtitle="Browse the role library and see your evidence-based fit for each." />

      {bestFit && bestFit.length > 0 && (
        <div className="card mb-6 p-5">
          <h2 className="mb-3 text-sm font-semibold text-ink-900">Your best-fit roles</h2>
          <div className="space-y-3">
            {bestFit.slice(0, 5).map((r) => (
              <div key={r.role.id} className="flex items-center gap-4">
                <Link href={`/roles/${r.role.id}`} className="w-56 shrink-0 truncate text-sm text-ink-800 hover:text-brand-600 hover:underline">
                  {r.role.title}
                </Link>
                <div className="flex-1"><ProgressBar value={r.readiness} /></div>
                <span className="w-14 shrink-0 text-right text-sm font-medium text-ink-700">{r.readiness}%</span>
              </div>
            ))}
          </div>
          <p className="mt-3 text-[11px] text-ink-400">Evidence-based capability alignment — not a probability of employment.</p>
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        <button onClick={() => setCategory("ALL")} className={`rounded-full border border-ink-200 px-3 py-1.5 text-xs font-medium ${category === "ALL" ? "bg-brand-600 text-white" : "bg-white text-ink-600"}`}>All</button>
        {categories.map((c) => (
          <button key={c} onClick={() => setCategory(c)} className={`rounded-full border border-ink-200 px-3 py-1.5 text-xs font-medium ${category === c ? "bg-brand-600 text-white" : "bg-white text-ink-600"}`}>{c}</button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-ink-400">Loading roles...</p>}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {filtered.map((r) => (
          <Link key={r.id} href={`/roles/${r.id}`} className="card p-4 transition hover:border-brand-400">
            <div className="mb-1 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-ink-900">{r.title}</h3>
              <span className="badge badge-neutral">{r.level}</span>
            </div>
            <p className="mb-2 text-xs text-ink-500">{r.description}</p>
            {readinessByRole.has(r.id) && (
              <div className="flex items-center gap-2">
                <div className="flex-1"><ProgressBar value={readinessByRole.get(r.id)!} /></div>
                <span className="text-xs font-medium text-ink-600">{readinessByRole.get(r.id)}%</span>
              </div>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
