"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { AuditEvent } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";

export default function AuditPage() {
  const { data, isLoading } = useQuery({ queryKey: ["audit"], queryFn: () => api.get<AuditEvent[]>("/api/audit?limit=100") });

  return (
    <div>
      <PageHeader title="Audit Trail" subtitle="Every mutation to your evidence graph, projects, goals, and recommendations." />
      {isLoading && <p className="text-sm text-ink-400">Loading audit log...</p>}
      <div className="card divide-y divide-ink-100">
        {(data ?? []).map((e) => (
          <div key={e.id} className="flex items-center gap-4 px-5 py-3">
            <span className="badge badge-neutral w-52 shrink-0 justify-center">{e.action.replace(/_/g, " ")}</span>
            <span className="flex-1 text-sm text-ink-700">{e.entity_type} #{e.entity_id}</span>
            <span className="text-xs text-ink-400">{new Date(e.created_at).toLocaleString()}</span>
          </div>
        ))}
        {(data ?? []).length === 0 && !isLoading && <p className="px-5 py-6 text-sm text-ink-400">No audit events yet.</p>}
      </div>
    </div>
  );
}
