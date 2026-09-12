"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { AssessmentQuestion, AssessmentResult, Skill } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";

// Skills with a real question bank in the seed data — keeps the picker relevant.
const ASSESSABLE_SKILL_NAMES = [
  "Python", "SQL", "Machine Learning", "Docker", "MLOps", "React", "Cloud Architecture",
  "System Design", "Natural Language Processing", "Application Security", "Statistics",
  "Kubernetes", "CI/CD", "Data Engineering", "REST APIs", "Product Management", "Terraform",
  "Computer Vision", "Distributed Systems", "Prompt Engineering", "Retrieval-Augmented Generation",
  "Data Visualization", "Identity & Access Management",
];

export default function AssessmentsPage() {
  const [skillId, setSkillId] = useState<number | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<AssessmentResult | null>(null);

  const { data: skills } = useQuery({ queryKey: ["skills"], queryFn: () => api.get<Skill[]>("/api/skills?limit=500") });
  const assessable = (skills ?? []).filter((s) => ASSESSABLE_SKILL_NAMES.includes(s.name));

  const { data: questions } = useQuery({
    queryKey: ["assessment-questions", skillId],
    queryFn: () => api.get<AssessmentQuestion[]>(`/api/assessments/questions?skill_id=${skillId}`),
    enabled: !!skillId,
  });

  const submit = useMutation({
    mutationFn: () => api.post<AssessmentResult>("/api/assessments", { skill_id: skillId, answers }),
    onSuccess: (data) => setResult(data),
  });

  const startAssessment = (id: number) => {
    setSkillId(id);
    setAnswers({});
    setResult(null);
  };

  return (
    <div>
      <PageHeader title="Skill Assessments" subtitle="A deterministic capability signal — not a professional certification." />

      {!skillId && (
        <div className="flex flex-wrap gap-2">
          {assessable.map((s) => (
            <button key={s.id} onClick={() => startAssessment(s.id)} className="btn-secondary">{s.name}</button>
          ))}
        </div>
      )}

      {skillId && !result && questions && (
        <div className="card space-y-5 p-5">
          {questions.map((q) => (
            <div key={q.id}>
              <p className="mb-2 text-sm font-medium text-ink-800">{q.question}</p>
              <div className="space-y-1.5">
                {q.options.map((opt) => (
                  <label key={opt} className="flex items-center gap-2 text-sm text-ink-600">
                    <input
                      type="radio"
                      name={`q-${q.id}`}
                      value={opt}
                      checked={answers[q.id] === opt}
                      onChange={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                    />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <div className="flex gap-2">
            <button className="btn-primary" onClick={() => submit.mutate()} disabled={submit.isPending}>
              {submit.isPending ? "Scoring..." : "Submit assessment"}
            </button>
            <button className="btn-secondary" onClick={() => setSkillId(null)}>Cancel</button>
          </div>
        </div>
      )}

      {result && (
        <div className="card p-5">
          <h2 className="mb-2 text-sm font-semibold text-ink-900">Result: {result.score}/{result.total} ({result.percentage}%)</h2>
          <p className="mb-3 text-sm text-ink-600">Capability signal: <span className="font-medium">{result.capability_signal}</span></p>
          {result.became_evidence && (
            <p className="mb-3 rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
              This score qualified as VERIFIED evidence and was added to your evidence graph.
            </p>
          )}
          <div className="space-y-2">
            {result.per_question.map((pq) => (
              <div key={pq.question_id} className={`rounded-lg px-3 py-2 text-xs ${pq.correct ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>
                {pq.correct ? "Correct" : `Incorrect — correct answer: ${pq.correct_answer}`}. {pq.explanation}
              </div>
            ))}
          </div>
          <button className="btn-secondary mt-4" onClick={() => setSkillId(null)}>Take another</button>
        </div>
      )}
    </div>
  );
}
