"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactFlow, { Background, Controls, Edge, Node, MarkerType } from "reactflow";
import "reactflow/dist/style.css";
import { api } from "@/lib/api";
import { GraphData } from "@/lib/types";
import { PageHeader } from "@/components/PageHeader";

const LEVEL_COLOR: Record<string, string> = {
  "EXPERT-LIKE": "#059669",
  STRONG: "#10b981",
  PRACTICAL: "#6366f1",
  DEVELOPING: "#f59e0b",
  FOUNDATIONAL: "#f43f5e",
};

function layout(data: GraphData): { nodes: Node[]; edges: Edge[] } {
  const skillNodes = data.nodes.filter((n) => n.type === "skill");
  const projectNodes = data.nodes.filter((n) => n.type === "project");

  const nodes: Node[] = [
    {
      id: "user",
      position: { x: 0, y: 0 },
      data: { label: data.nodes.find((n) => n.type === "person")?.label ?? "You" },
      style: { background: "#111827", color: "white", borderRadius: 999, padding: 10, fontSize: 12, fontWeight: 600 },
    },
  ];

  skillNodes.forEach((n, i) => {
    const angle = (2 * Math.PI * i) / skillNodes.length;
    nodes.push({
      id: n.id,
      position: { x: Math.cos(angle) * 320, y: Math.sin(angle) * 320 },
      data: { label: `${n.label}\n${n.score ?? 0}/100` },
      style: {
        background: LEVEL_COLOR[n.level ?? "FOUNDATIONAL"],
        color: "white",
        borderRadius: 10,
        padding: 8,
        fontSize: 11,
        whiteSpace: "pre-line",
        textAlign: "center",
        width: 110,
      },
    });
  });

  projectNodes.forEach((n, i) => {
    const angle = (2 * Math.PI * i) / projectNodes.length + 0.3;
    nodes.push({
      id: n.id,
      position: { x: Math.cos(angle) * 580, y: Math.sin(angle) * 580 },
      data: { label: n.label },
      style: { background: "white", border: "1px solid #e5e7eb", borderRadius: 8, padding: 8, fontSize: 11, width: 130 },
    });
  });

  const edges: Edge[] = data.edges.map((e, i) => ({
    id: `e-${i}`,
    source: e.source,
    target: e.target,
    animated: e.type === "DEMONSTRATED_BY",
    style: { stroke: e.type === "HAS_SKILL" ? "#c7d2fe" : "#e5e7eb" },
    markerEnd: { type: MarkerType.ArrowClosed, width: 12, height: 12 },
  }));

  return { nodes, edges };
}

export default function SkillGraphPage() {
  const { data } = useQuery({ queryKey: ["graph"], queryFn: () => api.get<GraphData>("/api/graph") });
  const { nodes, edges } = useMemo(() => (data ? layout(data) : { nodes: [], edges: [] }), [data]);

  return (
    <div>
      <PageHeader title="Skill Graph Explorer" subtitle="Person → Skills → Projects, colored by evidence-based capability level." />
      <div className="card" style={{ height: "70vh" }}>
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
