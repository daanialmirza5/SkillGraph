"use client";

import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import { Project, Skill } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [selectedSkills, setSelectedSkills] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);

  const { data: projects, isLoading } = useQuery({ queryKey: ["projects"], queryFn: () => api.get<Project[]>("/api/projects") });
  const { data: skills } = useQuery({ queryKey: ["skills"], queryFn: () => api.get<Skill[]>("/api/skills?limit=500") });

  const createProject = useMutation({
    mutationFn: (payload: Record<string, unknown>) => api.post<Project>("/api/projects", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setShowForm(false);
      setSelectedSkills([]);
      setError(null);
    },
    onError: (err) => setError(err instanceof ApiError ? err.message : "Failed to create project."),
  });

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    createProject.mutate({
      name: form.get("name"),
      description: form.get("description"),
      complexity: Number(form.get("complexity")),
      is_production: form.get("is_production") === "on",
      technologies: (form.get("technologies") as string)?.split(",").map((t) => t.trim()).filter(Boolean) ?? [],
      skill_ids: selectedSkills,
    });
  };

  const toggleSkill = (id: number) => setSelectedSkills((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <PageHeader title="Projects" subtitle="Every project you've built, mapped to the skills it demonstrates." />
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>{showForm ? "Cancel" : "Add project"}</button>
      </div>

      {showForm && (
        <form onSubmit={onSubmit} className="card mb-6 space-y-4 p-5">
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Name</label>
            <input name="name" required className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Description</label>
            <textarea name="description" required rows={2} className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-xs font-medium text-ink-600">Technologies (comma separated)</label>
              <input name="technologies" className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" placeholder="Python, FastAPI, Docker" />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-ink-600">Complexity (1-5)</label>
              <input type="number" name="complexity" min={1} max={5} defaultValue={3} className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-ink-600">
            <input type="checkbox" name="is_production" /> Deployed to production
          </label>
          <div>
            <label className="mb-1 block text-xs font-medium text-ink-600">Skills demonstrated</label>
            <div className="flex max-h-40 flex-wrap gap-1.5 overflow-y-auto rounded-lg border border-ink-200 p-2">
              {(skills ?? []).map((s) => (
                <button
                  type="button"
                  key={s.id}
                  onClick={() => toggleSkill(s.id)}
                  className={`rounded-full px-2.5 py-1 text-xs ${selectedSkills.includes(s.id) ? "bg-brand-600 text-white" : "bg-ink-100 text-ink-600"}`}
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <button type="submit" disabled={createProject.isPending} className="btn-primary">
            {createProject.isPending ? "Saving..." : "Save project"}
          </button>
        </form>
      )}

      {isLoading && <p className="text-sm text-ink-400">Loading projects...</p>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {(projects ?? []).map((p) => (
          <div key={p.id} className="card p-5">
            <div className="mb-1 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-ink-900">{p.name}</h3>
              {p.is_production && <span className="badge badge-strong">Production</span>}
            </div>
            <p className="mb-3 text-xs leading-relaxed text-ink-500">{p.description}</p>
            <div className="flex flex-wrap gap-1.5">
              {p.technologies.map((t) => (
                <span key={t} className="badge badge-neutral">{t}</span>
              ))}
            </div>
          </div>
        ))}
        {(projects ?? []).length === 0 && !isLoading && <p className="text-sm text-ink-400">No projects yet.</p>}
      </div>
    </div>
  );
}
