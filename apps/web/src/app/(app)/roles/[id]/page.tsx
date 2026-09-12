"use client";

import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { RoleDetail, RoleGap } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { ProgressBar } from "@/components/ProgressBar";
import { MatchBadge } from "@/components/MatchBadge";

export default function RoleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const { data: role, isLoading: roleLoading } = useQuery({ queryKey: ["role", id], queryFn: () => api.get<RoleDetail>(`/api/roles/${id}`) });
  const { data: fit, isLoading: fitLoading } = useQuery({ queryKey: ["role-fit", id], queryFn: () => api.get<RoleGap>(`/api/roles/${id}/fit`) });

  const setGoal = useMutation({
    mutationFn: () => api.post("/api/career-goals", { target_role_id: Number(id), timeline_months: 6 }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["career-goals"] });
    },
  });

  if (roleLoading || !role) return <p className="text-sm text-ink-400">Loading role...</p>;

  const grouped = ["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((imp) => ({
    importance: imp,
    skills: role.required_skills.filter((rs) => rs.importance === imp),
  }));

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <PageHeader title={role.title} subtitle={role.description ?? undefined} />
        <button className="btn-primary" onClick={() => setGoal.mutate()} disabled={setGoal.isPending}>
          {setGoal.isSuccess ? "Set as goal ✓" : setGoal.isPending ? "Setting..." : "Set as career goal"}
        </button>
      </div>

      {fit && !fitLoading && (
        <div className="card mb-6 p-5">
          <div className="mb-2 flex items-baseline justify-between">
            <h2 className="text-sm font-semibold text-ink-900">Your evidence-based coverage</h2>
            <span className="text-lg font-semibold text-ink-900">{fit.readiness}%</span>
          </div>
          <ProgressBar value={fit.readiness} />
        </div>
      )}

      <div className="card p-5">
        <h2 className="mb-4 text-sm font-semibold text-ink-900">Role Skill Requirements</h2>
        <div className="space-y-5">
          {grouped.map((group) =>
            group.skills.length > 0 ? (
              <div key={group.importance}>
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-400">{group.importance}</div>
                <div className="space-y-2">
                  {group.skills.map((rs) => {
                    const gap = fit?.strong.concat(fit.partial, fit.weak, fit.missing).find((g) => g.skill.id === rs.skill.id);
                    return (
                      <div key={rs.skill.id} className="flex items-center gap-3 rounded-lg border border-ink-100 px-3 py-2">
                        <span className="w-48 shrink-0 text-sm text-ink-800">{rs.skill.name}</span>
                        <div className="flex-1"><ProgressBar value={gap?.user_score ?? 0} /></div>
                        <span className="w-12 shrink-0 text-right text-xs text-ink-500">{gap?.user_score ?? 0}</span>
                        {gap && <MatchBadge value={gap.match} />}
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : null
          )}
        </div>
      </div>
    </div>
  );
}
