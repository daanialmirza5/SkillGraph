"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import {
  LayoutDashboard,
  Network,
  FileStack,
  FolderKanban,
  Briefcase,
  Target,
  AlertTriangle,
  GraduationCap,
  Lightbulb,
  LineChart,
  ClipboardCheck,
  FlaskConical,
  Bot,
  History,
  Settings as SettingsIcon,
  LogOut,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/skill-graph", label: "Skill Graph", icon: Network },
  { href: "/skills", label: "Skills", icon: FileStack },
  { href: "/evidence", label: "Evidence", icon: FolderKanban },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/roles", label: "Roles", icon: Briefcase },
  { href: "/gaps", label: "Gap Center", icon: AlertTriangle },
  { href: "/learning", label: "Learning Path", icon: GraduationCap },
  { href: "/recommendations", label: "Recommendations", icon: Lightbulb },
  { href: "/portfolio", label: "Portfolio", icon: LineChart },
  { href: "/assessments", label: "Assessments", icon: ClipboardCheck },
  { href: "/career-simulator", label: "Career Simulator", icon: FlaskConical },
  { href: "/ai-analyst", label: "AI Analyst", icon: Bot },
  { href: "/audit", label: "Audit Trail", icon: History },
  { href: "/settings", label: "Settings", icon: SettingsIcon },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-[#f7f8fb]">
      <aside className="flex w-64 shrink-0 flex-col border-r border-ink-200 bg-white">
        <div className="flex items-center gap-2 px-5 py-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">SG</div>
          <div>
            <div className="text-sm font-semibold text-ink-900">SkillGraph</div>
            <div className="text-[11px] text-ink-400">Career Intelligence OS</div>
          </div>
        </div>
        <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-2">
          {NAV.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition ${
                  active ? "bg-brand-100 font-medium text-brand-600" : "text-ink-600 hover:bg-ink-50"
                }`}
              >
                <Icon size={16} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-ink-200 px-4 py-3">
          <div className="mb-2 text-xs text-ink-400">Signed in as</div>
          <div className="mb-2 truncate text-sm font-medium text-ink-800">{user?.name ?? "..."}</div>
          <button onClick={logout} className="flex items-center gap-2 text-xs text-ink-500 hover:text-ink-800">
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl px-8 py-8">{children}</div>
      </main>
    </div>
  );
}
