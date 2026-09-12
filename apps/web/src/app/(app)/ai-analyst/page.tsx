"use client";

import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { AIAnswer, Role } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";
import { RoleSelector } from "@/components/RoleSelector";

const SAMPLE_QUESTIONS = [
  "Why am I not ready for this role yet?",
  "What is my strongest evidence right now?",
  "Which skill should I improve first?",
  "Which project would close the largest gap?",
];

export default function AIAnalystPage() {
  const [roleId, setRoleId] = useState<number | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AIAnswer | null>(null);

  const { data: roles } = useQuery({ queryKey: ["roles"], queryFn: () => api.get<Role[]>("/api/roles") });
  useEffect(() => {
    if (!roleId && roles && roles.length > 0) setRoleId(roles[0].id);
  }, [roles, roleId]);

  const ask = useMutation({
    mutationFn: (q: string) => api.post<AIAnswer>("/api/ai/analyze", { question: q, role_id: roleId }),
    onSuccess: setAnswer,
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (question.trim()) ask.mutate(question);
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <PageHeader title="AI Career Analyst" subtitle="Grounded in your evidence graph — never invents a skill, project, or score." />
        <RoleSelector roles={roles ?? []} value={roleId} onChange={setRoleId} />
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {SAMPLE_QUESTIONS.map((q) => (
          <button key={q} className="btn-secondary text-xs" onClick={() => { setQuestion(q); ask.mutate(q); }}>
            {q}
          </button>
        ))}
      </div>

      <form onSubmit={onSubmit} className="mb-6 flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about your skills, gaps, or readiness..."
          className="flex-1 rounded-lg border border-ink-200 px-3 py-2 text-sm"
        />
        <button type="submit" className="btn-primary" disabled={ask.isPending}>{ask.isPending ? "Thinking..." : "Ask"}</button>
      </form>

      {answer && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="card p-5 lg:col-span-2">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-ink-900">Answer</h2>
              <span className="badge badge-neutral">provider: {answer.provider}</span>
            </div>
            <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-ink-700">{answer.answer}</pre>
          </div>
          <div className="space-y-4">
            <div className="card p-4">
              <h3 className="mb-2 text-xs font-semibold uppercase text-ink-400">Confidence</h3>
              <span className="badge badge-neutral">{answer.confidence}</span>
            </div>
            <div className="card p-4">
              <h3 className="mb-2 text-xs font-semibold uppercase text-ink-400">Evidence Used</h3>
              <ul className="space-y-1 text-xs text-ink-600">
                {answer.evidence_used.map((e, i) => <li key={i}>• {e}</li>)}
              </ul>
            </div>
            <div className="card p-4">
              <h3 className="mb-2 text-xs font-semibold uppercase text-ink-400">Limitations</h3>
              <ul className="space-y-1 text-xs text-ink-600">
                {answer.limitations.map((l, i) => <li key={i}>• {l}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
