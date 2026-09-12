"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import { Evidence, Project, Skill } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";

const EVIDENCE_TYPES = ["PROJECT", "WORK_EXPERIENCE", "INTERNSHIP", "CERTIFICATION", "COURSE", "GITHUB_REPOSITORY", "PUBLICATION", "COMPETITION", "PORTFOLIO", "ASSESSMENT"];
const VERIFICATION = ["SELF_REPORTED", "VERIFIED", "UNVERIFIED"];

export default function EvidencePage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { data: evidence, isLoading } = useQuery({ queryKey: ["evidence"], queryFn: () => api.get<Evidence[]>("/api/evidence") });
  const { data: skills } = useQuery({ queryKey: ["skills"], queryFn: () => api.get<Skill[]>("/api/skills?limit=500") });
  const { data: projects } = useQuery({ queryKey: ["projects"], queryFn: () => api.get<Project[]>("/api/projects") });

  const skillById = new Map((skills ?? []).map((s) => [s.id, s]));

  const createEvidence = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post<Evidence>("/api/evidence", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evidence"] });
      queryClient.invalidateQueries({ queryKey: ["my-skill-graph"] });
      setShowForm(false);
      setError(null);
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to add evidence."),
  });

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    createEvidence.mutate({
      skill_id: Number(form.get("skill_id")),
      type: form.get("type"),
      title: form.get("title"),
      description: form.get("description") || null,
      date: form.get("date"),
      verification_status: form.get("verification_status"),
      complexity: Number(form.get("complexity")),
      project_id: form.get("project_id") ? Number(form.get("project_id")) : null,
    });
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <PageHeader title="Evidence" subtitle="The proof behind every claimed skill: projects, work experience, certifications, and more." />
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancel" : "Add evidence"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={onSubmit} className="card mb-6 grid grid-cols-2 gap-4 p-5">
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Skill</label>
            <select name="skill_id" required className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm">
              {(skills ?? []).map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Evidence type</label>
            <select name="type" required className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm">
              {EVIDENCE_TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
            </select>
          </div>
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-medium text-ink-600">Title</label>
            <input name="title" required className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" placeholder="e.g. Built a production ML API" />
          </div>
          <div className="col-span-2">
            <label className="mb-1 block text-xs font-medium text-ink-600">Description</label>
            <textarea name="description" rows={2} className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Date</label>
            <input type="date" name="date" required defaultValue={new Date().toISOString().slice(0, 10)} className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Verification</label>
            <select name="verification_status" className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm">
              {VERIFICATION.map((v) => <option key={v} value={v}>{v.replace("_", " ")}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Complexity (1-5)</label>
            <input type="number" name="complexity" min={1} max={5} defaultValue={3} className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Linked project (optional)</label>
            <select name="project_id" className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm">
              <option value="">None</option>
              {(projects ?? []).map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          {error && <p className="col-span-2 text-sm text-rose-600">{error}</p>}
          <div className="col-span-2">
            <button type="submit" disabled={createEvidence.isPending} className="btn-primary">
              {createEvidence.isPending ? "Saving..." : "Save evidence"}
            </button>
          </div>
        </form>
      )}

      {isLoading && <p className="text-sm text-ink-400">Loading evidence...</p>}

      <div className="card divide-y divide-ink-100">
        {(evidence ?? []).map((ev) => (
          <div key={ev.id} className="flex items-center gap-4 px-5 py-3.5">
            <span className="badge badge-neutral w-36 shrink-0 justify-center">{ev.type.replace("_", " ")}</span>
            <div className="flex-1">
              <div className="text-sm font-medium text-ink-900">{ev.title}</div>
              <div className="text-[11px] text-ink-400">{skillById.get(ev.skill_id)?.name ?? `Skill #${ev.skill_id}`} · {ev.date}</div>
            </div>
            <span className={`badge ${ev.verification_status === "VERIFIED" ? "badge-strong" : "badge-neutral"}`}>{ev.verification_status.replace("_", " ")}</span>
          </div>
        ))}
        {(evidence ?? []).length === 0 && !isLoading && <p className="px-5 py-6 text-sm text-ink-400">No evidence recorded yet.</p>}
      </div>
    </div>
  );
}
