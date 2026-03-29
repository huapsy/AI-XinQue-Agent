import { useEffect, useRef, useState } from "react";
import { API_BASE } from "../config";
import { buildHashRoute } from "../navigation";
import { getClientId, setStoredSessionId } from "../sessionStorage";

interface SessionItem {
  session_id: string;
  started_at: string | null;
  ended_at: string | null;
  summary_preview: string | null;
  opening_mood_score: number | null;
}

function formatDate(iso: string | null): string {
  if (!iso) return "未知时间";
  return new Date(iso).toLocaleString("zh-CN", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function HistoryPage() {
  const clientId = useRef(getClientId());
  const [sessions, setSessions] = useState<SessionItem[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/users/${clientId.current}/sessions`);
        const data = await res.json();
        setSessions(data.sessions || []);
      } catch {
        setSessions([]);
      }
    };
    load();
  }, []);

  return (
    <div style={S.page}>
      <div style={S.header}>
        <div>
          <div style={S.eyebrow}>连续支持</div>
          <h1 style={S.title}>历史会话</h1>
        </div>
        <div style={S.actions}>
          <a href={buildHashRoute("chat")} style={S.link}>返回对话</a>
          <a href={buildHashRoute("admin")} style={S.link}>查看统计</a>
        </div>
      </div>
      <div style={S.list}>
        {sessions.length ? sessions.map((session) => (
          <div key={session.session_id} style={S.card}>
            <div style={S.cardTop}>
              <div>
                <div style={S.cardTitle}>{formatDate(session.started_at)}</div>
                <div style={S.cardMeta}>
                  {session.ended_at ? "已结束" : "进行中"}
                  {session.opening_mood_score ? ` · 情绪 ${session.opening_mood_score}/5` : ""}
                </div>
              </div>
              <a
                href={buildHashRoute("chat", {
                  session: session.session_id,
                  history: session.ended_at ? 1 : 0,
                })}
                onClick={() => setStoredSessionId(session.session_id)}
                style={S.openLink}
              >
                打开
              </a>
            </div>
            <div style={S.summary}>{session.summary_preview || "还没有摘要，打开后可查看完整内容。"}</div>
          </div>
        )) : (
          <div style={S.empty}>还没有历史会话。</div>
        )}
      </div>
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
    gap: "16px",
    marginBottom: "24px",
  },
  eyebrow: {
    fontSize: "12px",
    color: "#64748b",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  title: {
    margin: "6px 0 0",
    fontSize: "30px",
    color: "#0f172a",
  },
  actions: {
    display: "flex",
    gap: "12px",
  },
  link: {
    color: "#2563eb",
    textDecoration: "none",
    fontWeight: 600,
  },
  list: {
    display: "grid",
    gap: "14px",
    maxWidth: "820px",
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: "18px",
    border: "1px solid #e2e8f0",
    padding: "18px 20px",
    boxShadow: "0 12px 26px rgba(15, 23, 42, 0.05)",
  },
  cardTop: {
    display: "flex",
    justifyContent: "space-between",
    gap: "16px",
    alignItems: "flex-start",
    marginBottom: "10px",
  },
  cardTitle: {
    fontSize: "16px",
    fontWeight: 700,
    color: "#0f172a",
  },
  cardMeta: {
    fontSize: "12px",
    color: "#64748b",
    marginTop: "4px",
  },
  openLink: {
    color: "#fff",
    backgroundColor: "#2563eb",
    padding: "8px 14px",
    borderRadius: "999px",
    textDecoration: "none",
    fontWeight: 600,
    fontSize: "13px",
    whiteSpace: "nowrap",
  },
  summary: {
    fontSize: "14px",
    lineHeight: 1.6,
    color: "#475569",
  },
  empty: {
    color: "#64748b",
    fontSize: "14px",
  },
};
