"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Role, RoleGap, SimulationResult } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { RoleSelector } from "@/components/RoleSelector";
import { ProgressBar } from "@/components/ProgressBar";

export default function CareerSimulatorPage() {
  const [roleId, setRoleId] = useState<number | null>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [result, setResult] = useState<SimulationResult | null>(null);

  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: () => api.get<Role[]>("/api/roles") });
  useEffect(() => {
    if (!roleId && roles && roles.length > 0) setRoleId(roles[0].id);
  }, [roles, roleId]);

  const { data: fit } = useQuery({
    queryKey: ["role-fit", roleId],
    queryFn: () => api.get<RoleGap>(`/api/roles/${roleId}/fit`),
    enabled: !!roleId,
  });

  const gapSkills = [...(fit?.weak ?? []), ...(fit?.missing ?? []), ...(fit?.partial ?? [])];

  const simulate = useMutation({
    mutationFn: () =>
      api.post<SimulationResult>("/api/simulations", {
        role_id: roleId,
        hypothetical_evidence: selected.map((skill_id) => ({ skill_id, evidence_type: "PROJECT", complexity: 5, verification_status: "VERIFIED" })),
      }),
    onSuccess: setResult,
  });

  const toggle = (id: number) => setSelected((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <PageHeader title="Career What-If Simulator" subtitle="Simulate adding evidence and see the projected readiness shift — nothing is saved to your real profile." />
        <RoleSelector roles={roles ?? []} value={roleId} onChange={(id) => { setRoleId(id); setSelected([]); setResult(null); }} />
      </div>

      <div className="card mb-6 p-5">
        <h2 className="mb-3 text-sm font-semibold text-ink-900">Choose hypothetical evidence to add</h2>
        <div className="flex flex-wrap gap-2">
          {gapSkills.map((g) => (
            <button
              key={g.skill.id}
              onClick={() => toggle(g.skill.id)}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium ${selected.includes(g.skill.id) ? "border-brand-600 bg-brand-600 text-white" : "border-ink-200 bg-white text-ink-600"}`}
            >
              {g.skill.name}
            </button>
          ))}
          {gapSkills.length === 0 && <p className="text-xs text-ink-400">No gaps to simulate for this role.</p>}
        </div>
        <button className="btn-primary mt-4" onClick={() => simulate.mutate()} disabled={selected.length === 0 || simulate.isPending}>
          {simulate.isPending ? "Simulating..." : "Run simulation"}
        </button>
      </div>

      {result && (
        <div className="card p-5">
          <h2 className="mb-4 text-sm font-semibold text-ink-900">Simulated Impact on {result.role_title}</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <div className="mb-1 text-xs text-ink-400">Before</div>
              <div className="mb-2 text-2xl font-semibold text-ink-900">{result.before_readiness}%</div>
              <ProgressBar value={result.before_readiness} />
            </div>
            <div>
              <div className="mb-1 text-xs text-ink-400">After (simulated)</div>
              <div className="mb-2 text-2xl font-semibold text-emerald-600">{result.after_readiness}%</div>
              <ProgressBar value={result.after_readiness} colorClass="bg-emerald-500" />
            </div>
          </div>
          <p className="mt-4 text-sm text-ink-600">Change: <span className="font-medium text-emerald-600">+{result.delta}%</span></p>
          {result.newly_covered_skills.length > 0 && (
            <p className="mt-1 text-xs text-ink-500">Newly covered: {result.newly_covered_skills.join(", ")}</p>
          )}
          <p className="mt-3 text-[11px] text-ink-400">This simulation is temporary and was not written to your real profile.</p>
        </div>
      )}
    </div>
  );
}
