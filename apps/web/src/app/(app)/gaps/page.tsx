"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Role } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { MatchBadge } from "@/components/MatchBadge";
import { RoleSelector } from "@/components/RoleSelector";

interface GapPayload {
  skill: { id: number; name: string };
  importance: string;
  match: string;
  user_score: number;
  is_evidence_gap: boolean;
  priority_score: number;
  dependency_chain: string[];
}

interface GapCenterResponse {
  role_title: string;
  readiness: number;
  critical_gaps: GapPayload[];
  high_priority_gaps: GapPayload[];
  medium_priority_gaps: GapPayload[];
  evidence_gaps: GapPayload[];
}

function GapRow({ gap }: { gap: GapPayload }) {
  return (
    <div className="rounded-lg border border-ink-100 px-4 py-3">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-sm font-medium text-ink-900">{gap.skill.name}</span>
        <div className="flex items-center gap-2">
          <MatchBadge value={gap.importance} />
          <MatchBadge value={gap.match} />
        </div>
      </div>
      {gap.dependency_chain.length > 1 && (
        <p className="text-xs text-ink-500">Dependency chain: {gap.dependency_chain.join(" → ")}</p>
      )}
      {gap.is_evidence_gap && <p className="text-xs text-rose-500">Claimed but no supporting evidence on file.</p>}
    </div>
  );
}

export default function GapsPage() {
  const [roleId, setRoleId] = useState<number | null>(null);
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: () => api.get<Role[]>("/api/roles") });

  useEffect(() => {
    if (!roleId && roles && roles.length > 0) setRoleId(roles[0].id);
  }, [roles, roleId]);

  const { data } = useQuery({
    queryKey: ["gap-center", roleId],
    queryFn: () => api.get<GapCenterResponse>(`/api/skill-gaps?role_id=${roleId}`),
    enabled: !!roleId,
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <PageHeader title="Skill Gap Center" subtitle="Prioritized, dependency-aware gaps between your evidence and a target role." />
        <RoleSelector roles={roles ?? []} value={roleId} onChange={setRoleId} />
      </div>

      {data && (
        <div className="space-y-6">
          <section>
            <h2 className="mb-2 text-sm font-semibold text-rose-600">Critical Gaps ({data.critical_gaps.length})</h2>
            <div className="space-y-2">{data.critical_gaps.map((g) => <GapRow key={g.skill.id} gap={g} />)}</div>
            {data.critical_gaps.length === 0 && <p className="text-xs text-ink-400">No critical gaps — nice work.</p>}
          </section>
          <section>
            <h2 className="mb-2 text-sm font-semibold text-orange-600">High Priority Gaps ({data.high_priority_gaps.length})</h2>
            <div className="space-y-2">{data.high_priority_gaps.map((g) => <GapRow key={g.skill.id} gap={g} />)}</div>
          </section>
          <section>
            <h2 className="mb-2 text-sm font-semibold text-amber-600">Medium / Low Priority Gaps ({data.medium_priority_gaps.length})</h2>
            <div className="space-y-2">{data.medium_priority_gaps.map((g) => <GapRow key={g.skill.id} gap={g} />)}</div>
          </section>
          <section>
            <h2 className="mb-2 text-sm font-semibold text-ink-700">Evidence Gaps ({data.evidence_gaps.length})</h2>
            <p className="mb-2 text-xs text-ink-400">Skills you claim but haven&apos;t backed with evidence yet — different from not knowing them at all.</p>
            <div className="space-y-2">{data.evidence_gaps.map((g) => <GapRow key={g.skill.id} gap={g} />)}</div>
            {data.evidence_gaps.length === 0 && <p className="text-xs text-ink-400">No evidence gaps found.</p>}
          </section>
        </div>
      )}
    </div>
  );
}
