"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ProjectRecommendation, Recommendation, Role } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { RoleSelector } from "@/components/RoleSelector";

const STATUS_STYLE: Record<string, string> = {
  SUGGESTED: "badge-partial",
  ACCEPTED: "badge-strong",
  EDITED: "badge-neutral",
  REJECTED: "badge-missing",
};

export default function RecommendationsPage() {
  const queryClient = useQueryClient();
  const [roleId, setRoleId] = useState<number | null>(null);
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: () => api.get<Role[]>("/api/roles") });

  useEffect(() => {
    if (!roleId && roles && roles.length > 0) setRoleId(roles[0].id);
  }, [roles, roleId]);

  const { data: preview } = useQuery({
    queryKey: ["rec-preview", roleId],
    queryFn: () => api.get<ProjectRecommendation[]>(`/api/recommendations/preview?role_id=${roleId}`),
    enabled: !!roleId,
  });

  const { data: saved } = useQuery({ queryKey: ["recommendations"], queryFn: () => api.get<Recommendation[]>("/api/recommendations") });

  const generate = useMutation({
    mutationFn: () => api.post<Recommendation>(`/api/recommendations/generate?role_id=${roleId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recommendations"] }),
  });

  const decide = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => api.post(`/api/recommendations/${id}/decision`, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["audit"] });
    },
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <PageHeader title="What Should I Build Next?" subtitle="Evidence-first project recommendations that close the largest weighted gap." />
        <RoleSelector roles={roles ?? []} value={roleId} onChange={setRoleId} />
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2">
        {(preview ?? []).map((rec) => (
          <div key={rec.title} className="card p-5">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-ink-900">{rec.title}</h3>
              <span className="badge badge-strong">{rec.expected_gap_reduction} impact</span>
            </div>
            <p className="mb-2 text-xs text-ink-500">{rec.description}</p>
            <p className="mb-3 text-xs text-ink-600">{rec.reason}</p>
            <div className="mb-3 flex flex-wrap gap-1.5">
              {rec.target_skill_names.map((s) => (
                <span key={s} className={`badge ${rec.closes_gap_skill_names.includes(s) ? "badge-partial" : "badge-neutral"}`}>{s}</span>
              ))}
            </div>
            <button className="btn-secondary" onClick={() => generate.mutate()} disabled={generate.isPending}>
              Save as recommendation
            </button>
          </div>
        ))}
        {(preview ?? []).length === 0 && <p className="text-sm text-ink-400">No open gaps for this role right now.</p>}
      </div>

      <h2 className="mb-3 text-sm font-semibold text-ink-900">Your Recommendations (Human-in-the-loop)</h2>
      <div className="card divide-y divide-ink-100">
        {(saved ?? []).map((rec) => (
          <div key={rec.id} className="flex items-center gap-4 px-5 py-4">
            <div className="flex-1">
              <div className="text-sm font-medium text-ink-900">{rec.title}</div>
              <div className="text-xs text-ink-500">{rec.reason}</div>
            </div>
            <span className={`badge ${STATUS_STYLE[rec.status] ?? "badge-neutral"}`}>{rec.status}</span>
            {rec.status === "SUGGESTED" && (
              <div className="flex gap-2">
                <button className="btn-secondary" onClick={() => decide.mutate({ id: rec.id, status: "ACCEPTED" })}>Accept</button>
                <button className="btn-secondary" onClick={() => decide.mutate({ id: rec.id, status: "REJECTED" })}>Reject</button>
              </div>
            )}
          </div>
        ))}
        {(saved ?? []).length === 0 && <p className="px-5 py-6 text-sm text-ink-400">No saved recommendations yet.</p>}
      </div>
    </div>
  );
}
