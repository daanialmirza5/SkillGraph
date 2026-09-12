import { Role } from "@/lib/types";

export function RoleSelector({
  roles,
  value,
  onChange,
}: {
  roles: Role[];
  value: number | null;
  onChange: (id: number) => void;
}) {
  return (
    <select
      value={value ?? ""}
      onChange={(e) => onChange(Number(e.target.value))}
      className="rounded-lg border border-ink-200 bg-white px-3 py-2 text-sm"
    >
      {roles.map((r) => (
        <option key={r.id} value={r.id}>
          {r.title}
        </option>
      ))}
    </select>
  );
}
