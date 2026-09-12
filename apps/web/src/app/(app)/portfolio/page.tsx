"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PortfolioData } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";

function SkillPills({ items, className }: { items: { skill: string; score: number }[]; className: string }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((i) => (
        <span key={i.skill} className={`badge ${className}`}>{i.skill} · {i.score}</span>
      ))}
      {items.length === 0 && <span className="text-xs text-ink-400">None</span>}
    </div>
  );
}

export default function PortfolioPage() {
  const { data, isLoading } = useQuery({ queryKey: ["portfolio"], queryFn: () => api.get<PortfolioData>("/api/portfolio") });

  return (
    <div>
      <PageHeader title="Portfolio Intelligence" subtitle="What your evidence graph actually proves — and what it doesn't." />
      {isLoading && <p className="text-sm text-ink-400">Analyzing portfolio...</p>}

      {data && (
        <div className="space-y-6">
          <div className="card p-5">
            <h2 className="mb-2 text-sm font-semibold text-emerald-700">Strong</h2>
            <SkillPills items={data.strong} className="badge-strong" />
          </div>
          <div className="card p-5">
            <h2 className="mb-2 text-sm font-semibold text-amber-700">Moderate</h2>
            <SkillPills items={data.moderate} className="badge-partial" />
          </div>
          <div className="card p-5">
            <h2 className="mb-2 text-sm font-semibold text-rose-700">Weak</h2>
            <SkillPills items={data.weak} className="badge-weak" />
          </div>
          <div className="card p-5">
            <h2 className="mb-2 text-sm font-semibold text-ink-900">What Your Portfolio Does Not Prove</h2>
            {data.what_your_portfolio_does_not_prove.length === 0 ? (
              <p className="text-xs text-ink-400">No unsupported claims found — every claimed skill has at least some evidence.</p>
            ) : (
              <ul className="space-y-2">
                {data.what_your_portfolio_does_not_prove.map((item) => (
                  <li key={item.skill} className="rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">{item.note}</li>
                ))}
              </ul>
            )}
          </div>
          <div className="card p-5">
            <h2 className="mb-2 text-sm font-semibold text-ink-900">Categories Covered</h2>
            <div className="flex flex-wrap gap-1.5">
              {data.categories_covered.map((c) => <span key={c} className="badge badge-neutral">{c}</span>)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
