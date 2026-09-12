"use client";

import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/PageHeader";
import { Disclaimer } from "@/components/Disclaimer";

interface Profile {
  headline?: string | null;
  bio?: string | null;
  persona?: string | null;
  target_level?: string | null;
  target_timeline_months?: number | null;
}

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: () => api.get<Profile>("/api/profile") });
  const [headline, setHeadline] = useState("");
  const [bio, setBio] = useState("");

  useEffect(() => {
    if (profile) {
      setHeadline(profile.headline ?? "");
      setBio(profile.bio ?? "");
    }
  }, [profile]);

  const update = useMutation({
    mutationFn: (payload: Partial<Profile>) => api.patch("/api/profile", payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["profile"] }),
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    update.mutate({ headline, bio });
  };

  return (
    <div>
      <PageHeader title="Settings" subtitle="Profile details and platform information." />

      <form onSubmit={onSubmit} className="card mb-6 space-y-4 p-5">
        <div>
          <label className="mb-1 block text-xs font-medium text-ink-600">Headline</label>
          <input value={headline} onChange={(e) => setHeadline(e.target.value)} className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-ink-600">Bio</label>
          <textarea value={bio} onChange={(e) => setBio(e.target.value)} rows={3} className="w-full rounded-lg border border-ink-200 px-3 py-2 text-sm" />
        </div>
        <button type="submit" className="btn-primary" disabled={update.isPending}>{update.isPending ? "Saving..." : "Save changes"}</button>
      </form>

      <div className="card p-5">
        <h2 className="mb-2 text-sm font-semibold text-ink-900">About SkillGraph</h2>
        <p className="text-sm text-ink-600">
          SkillGraph models an evidence graph — claimed skills, the evidence behind them, and how that evidence maps
          to target role requirements — rather than matching resume keywords.
        </p>
        <Disclaimer />
      </div>
    </div>
  );
}
