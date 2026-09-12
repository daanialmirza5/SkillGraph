"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { LearningStep, Role } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { RoleSelector } from "@/components/RoleSelector";

export default function LearningPage() {
  const [roleId, setRoleId] = useState<number | null>(null);
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: () => api.get<Role[]>("/api/roles") });

  useEffect(() => {
    if (!roleId && roles && roles.length > 0) setRoleId(roles[0].id);
  }, [roles, roleId]);

  const { data: steps, isLoading } = useQuery({
    queryKey: ["learning-path", roleId],
    queryFn: () => api.get<LearningStep[]>(`/api/learning-paths?role_id=${roleId}`),
    enabled: !!roleId,
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <PageHeader title="Learning Path" subtitle="A dependency-ordered path from your current evidence to a target role." />
        <RoleSelector roles={roles ?? []} value={roleId} onChange={setRoleId} />
      </div>

      {isLoading && <p className="text-sm text-ink-400">Building path...</p>}

      <div className="relative space-y-4 pl-6">
        <div className="absolute bottom-2 left-2.5 top-2 w-px bg-ink-200" />
        {(steps ?? []).map((step) => (
          <div key={step.skill.id} className="relative">
            <div className="absolute -left-6 top-1 flex h-5 w-5 items-center justify-center rounded-full bg-brand-600 text-[11px] font-semibold text-white">
              {step.order}
            </div>
            <div className="card p-4">
              <h3 className="mb-1 text-sm font-semibold text-ink-900">{step.skill.name}</h3>
              <p className="mb-2 text-xs text-ink-500">{step.why}</p>
              <p className="mb-2 text-xs text-ink-600">
                <span className="font-medium">Evidence to create:</span> {step.evidence_to_create}
              </p>
              {step.resource_titles.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {step.resource_titles.map((r) => (
                    <span key={r} className="badge badge-neutral">{r}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {(steps ?? []).length === 0 && !isLoading && (
          <p className="text-sm text-ink-400">No open gaps for this role — your evidence already covers it well.</p>
        )}
      </div>
    </div>
  );
}
