import { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

interface AdminMetrics {
  session_count: number;
  average_turns: number;
  intervention_completion_rate: number;
  safety_trigger_rate: number;
  tool_failure_rate: number;
  average_latency_ms: number;
}

const EMPTY_METRICS: AdminMetrics = {
  session_count: 0,
  average_turns: 0,
  intervention_completion_rate: 0,
  safety_trigger_rate: 0,
  tool_failure_rate: 0,
  average_latency_ms: 0,
};

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState<AdminMetrics>(EMPTY_METRICS);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/admin/metrics`);
        const data = await res.json();
        setMetrics({ ...EMPTY_METRICS, ...data });
      } catch {
        setMetrics(EMPTY_METRICS);
      }
    };
    load();
  }, []);

  return (
    <div style={S.page}>
      <div style={S.header}>
        <div>
          <div style={S.eyebrow}>匿名统计</div>
          <h1 style={S.title}>心雀运营看板</h1>
        </div>
        <a href="#chat" style={S.backLink}>返回对话</a>
      </div>
      <div style={S.grid}>
        <MetricCard label="会话数" value={metrics.session_count} />
        <MetricCard label="平均轮次" value={metrics.average_turns} />
        <MetricCard label="干预完成率" value={`${Math.round(metrics.intervention_completion_rate * 100)}%`} />
        <MetricCard label="安全触发率" value={`${Math.round(metrics.safety_trigger_rate * 100)}%`} />
        <MetricCard label="Tool 失败率" value={`${Math.round(metrics.tool_failure_rate * 100)}%`} />
        <MetricCard label="平均延迟" value={`${Math.round(metrics.average_latency_ms)}ms`} />
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div style={S.card}>
      <div style={S.cardLabel}>{label}</div>
      <div style={S.cardValue}>{value}</div>
    </div>
  );
}

const S: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    padding: "32px",
    background: "linear-gradient(180deg, #fff 0%, #f8fafc 100%)",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "28px",
  },
  eyebrow: {
    fontSize: "12px",
    color: "#64748b",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  title: {
    margin: "6px 0 0",
    fontSize: "28px",
    color: "#0f172a",
  },
  backLink: {
    color: "#2563eb",
    textDecoration: "none",
    fontWeight: 600,
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "16px",
  },
  card: {
    padding: "20px",
    borderRadius: "18px",
    backgroundColor: "#ffffff",
    border: "1px solid #e2e8f0",
    boxShadow: "0 10px 30px rgba(15, 23, 42, 0.05)",
  },
  cardLabel: {
    fontSize: "13px",
    color: "#64748b",
    marginBottom: "10px",
  },
  cardValue: {
    fontSize: "30px",
    color: "#0f172a",
    fontWeight: 700,
  },
};
