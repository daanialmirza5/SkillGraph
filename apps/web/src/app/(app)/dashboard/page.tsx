"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { api } from "@/lib/api";
import { DashboardData, Role } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { Disclaimer } from "@/components/Disclaimer";
import { ProgressBar } from "@/components/ProgressBar";
import { TrendingUp, Layers, AlertCircle, FolderKanban, ArrowRight } from "lucide-react";

function StatCard({ label, value, icon: Icon }: { label: string; value: string | number; icon: React.ElementType }) {
  return (
    <div className="card p-5">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-ink-400">{label}</span>
        <Icon size={16} className="text-ink-300" />
      </div>
      <div className="text-2xl font-semibold text-ink-900">{value}</div>
    </div>
  );
}

export default function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: () => api.get<DashboardData>("/api/dashboard") });
  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: () => api.get<Role[]>("/api/roles") });

  const activeRole = roles?.find((r) => r.id === data?.active_goal_role_id);

  if (isLoading) return <p className="text-sm text-ink-400">Loading dashboard...</p>;

  return (
    <div>
      <PageHeader title="Career Intelligence Command Center" subtitle="An evidence-based view of what you can currently prove." />

      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard label="Evidenced Skills" value={data?.evidence_coverage_skill_count ?? 0} icon={Layers} />
        <StatCard label="Strong Skills" value={data?.strong_skill_count ?? 0} icon={TrendingUp} />
        <StatCard label="Evidence Gaps" value={data?.evidence_gap_count ?? 0} icon={AlertCircle} />
        <StatCard label="Projects Logged" value={data?.project_count ?? 0} icon={FolderKanban} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card p-6 lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-ink-900">Target Role Readiness</h2>
            {activeRole && (
              <Link href={`/roles/${activeRole.id}`} className="text-xs font-medium text-brand-600 hover:underline">
                View role graph
              </Link>
            )}
          </div>
          {activeRole ? (
            <>
              <div className="mb-2 flex items-baseline justify-between">
                <span className="text-sm text-ink-600">{activeRole.title}</span>
                <span className="text-lg font-semibold text-ink-900">{data?.target_role_readiness ?? 0}%</span>
              </div>
              <ProgressBar value={data?.target_role_readiness ?? 0} />
              <p className="mt-3 text-xs text-ink-400">
                Weighted capability coverage against this demo role&apos;s modeled requirements — not a hiring
                probability.
              </p>
            </>
          ) : (
            <div className="text-sm text-ink-500">
              No active career goal yet.{" "}
              <Link href="/roles" className="font-medium text-brand-600 hover:underline">
                Choose a target role
              </Link>{" "}
              to see readiness here.
            </div>
          )}
        </div>

        <div className="card p-6">
          <h2 className="mb-3 text-sm font-semibold text-ink-900">Next Best Action</h2>
          {data?.next_best_action ? (
            <div>
              <div className="mb-1 text-sm font-medium text-ink-800">{data.next_best_action.title}</div>
              <p className="text-xs leading-relaxed text-ink-500">{data.next_best_action.reason}</p>
              <Link href="/recommendations" className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-brand-600 hover:underline">
                View recommendations <ArrowRight size={12} />
              </Link>
            </div>
          ) : (
            <p className="text-sm text-ink-500">Set a target role to get a prioritized next action.</p>
          )}
        </div>
      </div>

      <Disclaimer text={data?.disclaimer} />
    </div>
  );
}
