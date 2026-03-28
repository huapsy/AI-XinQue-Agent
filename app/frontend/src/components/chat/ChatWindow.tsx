import { useState, useRef, useEffect, useCallback } from "react";
import { shouldRestoreSavedSession } from "./sessionRestore";
import { describeMoodTrend, type MoodTrendPayload } from "./moodTrend";

const API_BASE = "http://localhost:8000";

// ── 类型定义 ──

interface CardStep {
  instruction: string;
  duration?: number;
  phase?: string;
}

interface ReferralResource {
  name: string;
  description?: string;
  url?: string;
  phone?: string;
  action?: string;
}

interface CardData {
  type: string;
  title: string;
  description?: string;
  steps?: CardStep[];
  fields?: Array<{ label: string; placeholder?: string }>;
  items?: Array<{ label: string; checked?: boolean }>;
  rounds?: number;
  resources?: ReferralResource[];
  footer?: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  card_data?: CardData | null;
}

interface SessionItem {
  session_id: string;
  started_at: string | null;
  ended_at: string | null;
  summary_preview: string | null;
  opening_mood_score: number | null;
}

const EMPTY_TREND: MoodTrendPayload = {
  count: 0,
  average_mood_score: null,
  latest_mood_score: null,
  trend_direction: "stable",
  volatility: 0,
  points: [],
};

// ── 工具函数 ──

function getClientId(): string {
  const key = "xinque_client_id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  const isToday = d.toDateString() === now.toDateString();
  if (isToday) return d.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
  return d.toLocaleDateString("zh-CN", { month: "short", day: "numeric" });
}

const MOOD_OPTIONS = [
  { score: 1, label: "很差", emoji: "😞" },
  { score: 2, label: "不太好", emoji: "😔" },
  { score: 3, label: "一般", emoji: "😐" },
  { score: 4, label: "还不错", emoji: "🙂" },
  { score: 5, label: "很好", emoji: "😊" },
];

// ── 卡片组件 ──

function ReferralCard({ card }: { card: CardData }) {
  return (
    <div style={{ backgroundColor: "#fef2f2", border: "1px solid #fca5a5", borderRadius: "12px", padding: "16px", marginTop: "8px" }}>
      <div style={{ fontSize: "15px", fontWeight: 600, color: "#dc2626", marginBottom: "8px" }}>{card.title}</div>
      {card.description && <div style={{ fontSize: "13px", color: "#991b1b", marginBottom: "12px" }}>{card.description}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {card.resources?.map((res, i) => (
          <div key={i} style={{ backgroundColor: "#fff", borderRadius: "8px", padding: "10px 12px", border: "1px solid #fecaca" }}>
            <div style={{ fontSize: "14px", fontWeight: 600, color: "#1f2937" }}>{res.name}</div>
            {res.description && <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "2px" }}>{res.description}</div>}
            {res.phone && <div style={{ fontSize: "15px", fontWeight: 600, color: "#dc2626", marginTop: "4px" }}>{res.phone}</div>}
            {res.url && res.action && (
              <a href={res.url} target="_blank" rel="noopener noreferrer"
                style={{ display: "inline-block", marginTop: "6px", fontSize: "13px", color: "#fff", backgroundColor: "#dc2626", padding: "6px 14px", borderRadius: "16px", textDecoration: "none", fontWeight: 500 }}>
                {res.action} →
              </a>
            )}
          </div>
        ))}
      </div>
      {card.footer && <div style={{ marginTop: "10px", fontSize: "12px", color: "#991b1b", textAlign: "center", fontWeight: 500 }}>{card.footer}</div>}
    </div>
  );
}

function ExerciseCard({ card }: { card: CardData }) {
  return (
    <div style={{ backgroundColor: "#eef2ff", border: "1px solid #c7d2fe", borderRadius: "12px", padding: "16px", marginTop: "8px" }}>
      <div style={{ fontSize: "15px", fontWeight: 600, color: "#4338ca", marginBottom: "8px" }}>{card.title}</div>
      {card.description && <div style={{ fontSize: "13px", color: "#6366f1", marginBottom: "12px" }}>{card.description}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {card.steps?.map((step, i) => (
          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: "10px" }}>
            <span style={{ backgroundColor: "#4f46e5", color: "#fff", borderRadius: "50%", width: "22px", height: "22px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "12px", fontWeight: 600, flexShrink: 0 }}>
              {i + 1}
            </span>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flex: 1, fontSize: "13px", color: "#374151" }}>
              <span>{step.instruction}</span>
              {step.duration && <span style={{ fontSize: "12px", color: "#6366f1", fontWeight: 500, marginLeft: "8px", whiteSpace: "nowrap" }}>{step.duration}秒</span>}
            </div>
          </div>
        ))}
      </div>
      {card.rounds && <div style={{ marginTop: "10px", fontSize: "13px", color: "#6366f1", fontWeight: 500, textAlign: "center" }}>重复 {card.rounds} 轮</div>}
    </div>
  );
}

function JournalCard({ card }: { card: CardData }) {
  return (
    <div style={{ backgroundColor: "#f8fafc", border: "1px solid #cbd5e1", borderRadius: "12px", padding: "16px", marginTop: "8px" }}>
      <div style={{ fontSize: "15px", fontWeight: 600, color: "#0f172a", marginBottom: "8px" }}>{card.title}</div>
      {card.description && <div style={{ fontSize: "13px", color: "#475569", marginBottom: "12px" }}>{card.description}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {card.fields?.map((field, index) => (
          <div key={`${field.label}-${index}`} style={{ borderRadius: "10px", padding: "10px 12px", backgroundColor: "#fff", border: "1px dashed #cbd5e1" }}>
            <div style={{ fontSize: "12px", color: "#64748b", marginBottom: "4px" }}>{field.label}</div>
            <div style={{ fontSize: "13px", color: "#94a3b8" }}>{field.placeholder || "在这里写下你的内容"}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ChecklistCard({ card }: { card: CardData }) {
  return (
    <div style={{ backgroundColor: "#fefce8", border: "1px solid #fde68a", borderRadius: "12px", padding: "16px", marginTop: "8px" }}>
      <div style={{ fontSize: "15px", fontWeight: 600, color: "#854d0e", marginBottom: "8px" }}>{card.title}</div>
      {card.description && <div style={{ fontSize: "13px", color: "#a16207", marginBottom: "12px" }}>{card.description}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {card.items?.map((item, index) => (
          <div key={`${item.label}-${index}`} style={{ display: "flex", alignItems: "center", gap: "10px", fontSize: "13px", color: "#713f12" }}>
            <span style={{ width: "18px", height: "18px", borderRadius: "6px", border: "1px solid #f59e0b", backgroundColor: item.checked ? "#f59e0b" : "#fff7ed" }} />
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function CardRenderer({ card }: { card: CardData }) {
  if (card.type === "referral") return <ReferralCard card={card} />;
  if (card.type === "journal") return <JournalCard card={card} />;
  if (card.type === "checklist") return <ChecklistCard card={card} />;
  return <ExerciseCard card={card} />;
}

// ── 情绪签到组件 ──

function MoodCheckin({ onSelect }: { onSelect: (score: number) => void }) {
  return (
    <div style={S.moodOverlay}>
      <div style={S.moodCard}>
        <div style={{ fontSize: "18px", fontWeight: 600, color: "#1f2937", marginBottom: "8px" }}>今天感觉怎么样？</div>
        <div style={{ fontSize: "13px", color: "#6b7280", marginBottom: "20px" }}>选一个最贴近你当前心情的</div>
        <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
          {MOOD_OPTIONS.map((opt) => (
            <button key={opt.score} onClick={() => onSelect(opt.score)} style={S.moodButton}>
              <span style={{ fontSize: "28px" }}>{opt.emoji}</span>
              <span style={{ fontSize: "12px", color: "#374151", marginTop: "4px" }}>{opt.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── 主组件 ──

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(
    localStorage.getItem("xinque_session_id"),
  );
  const [sessionList, setSessionList] = useState<SessionItem[]>([]);
  const [viewingHistory, setViewingHistory] = useState(false);
  const [showMoodCheckin, setShowMoodCheckin] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [moodTrend, setMoodTrend] = useState<MoodTrendPayload>(EMPTY_TREND);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const clientId = useRef(getClientId());

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 加载会话列表
  const loadSessionList = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/users/${clientId.current}/sessions`);
      const data = await res.json();
      setSessionList(data.sessions || []);
    } catch { /* ignore */ }
  }, []);

  const loadMoodTrend = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/users/${clientId.current}/mood-trend`);
      const data = await res.json();
      setMoodTrend({
        count: data.count || 0,
        average_mood_score: data.average_mood_score ?? null,
        latest_mood_score: data.latest_mood_score ?? null,
        trend_direction: data.trend_direction ?? "stable",
        volatility: data.volatility ?? 0,
        points: data.points || [],
      });
    } catch {
      setMoodTrend(EMPTY_TREND);
    }
  }, []);

  useEffect(() => {
    loadSessionList();
    loadMoodTrend();
  }, [loadSessionList, loadMoodTrend]);

  // 页面关闭时结束会话
  useEffect(() => {
    const handleUnload = () => {
      const sid = localStorage.getItem("xinque_session_id");
      if (sid) {
        navigator.sendBeacon(`${API_BASE}/api/sessions/${sid}/end`);
      }
    };
    window.addEventListener("beforeunload", handleUnload);
    return () => window.removeEventListener("beforeunload", handleUnload);
  }, []);

  // 初始化：恢复会话 或 创建新会话
  useEffect(() => {
    const init = async () => {
      const savedSid = localStorage.getItem("xinque_session_id");
      if (savedSid) {
        // 尝试恢复已有会话
        try {
          const res = await fetch(`${API_BASE}/api/sessions/${savedSid}/messages`);
          const data = await res.json();
          if (shouldRestoreSavedSession(data)) {
            setSessionId(savedSid);
            setMessages(data.messages);
            return; // 恢复成功
          }
        } catch { /* fall through to create new */ }
      }
      // 没有会话 或 恢复失败 → 创建新会话 + 弹情绪签到
      try {
        const res = await fetch(`${API_BASE}/api/sessions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ client_id: clientId.current }),
        });
        const data = await res.json();
        setSessionId(data.session_id);
        localStorage.setItem("xinque_session_id", data.session_id);
        setShowMoodCheckin(true);
        loadSessionList();
        loadMoodTrend();
      } catch { /* ignore */ }
    };
    init();
  }, [loadMoodTrend, loadSessionList]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading || viewingHistory) return;

    const userMessage: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: clientId.current,
          session_id: sessionId,
          message: text,
        }),
      });
      const data = await res.json();

      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
        localStorage.setItem("xinque_session_id", data.session_id);
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply, card_data: data.card_data || null },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "抱歉，连接出现问题，请稍后再试。" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const endCurrentSession = useCallback(async (sid: string | null) => {
    if (!sid) return;
    try {
      await fetch(`${API_BASE}/api/sessions/${sid}/end`, { method: "POST" });
    } catch { /* ignore */ }
  }, []);

  const newSession = useCallback(async () => {
    await endCurrentSession(sessionId);
    try {
      const res = await fetch(`${API_BASE}/api/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ client_id: clientId.current }),
      });
      const data = await res.json();
      setSessionId(data.session_id);
      localStorage.setItem("xinque_session_id", data.session_id);
      setMessages([]);
      setViewingHistory(false);
      setShowMoodCheckin(true);
      loadSessionList();
      loadMoodTrend();
    } catch { /* ignore */ }
  }, [sessionId, endCurrentSession, loadMoodTrend, loadSessionList]);

  const viewSession = useCallback(async (sid: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/sessions/${sid}/messages`);
      const data = await res.json();
      setMessages(data.messages || []);
      const item = sessionList.find((s) => s.session_id === sid);
      const isEnded = item?.ended_at != null;
      setViewingHistory(isEnded);
      if (!isEnded) {
        setSessionId(sid);
        localStorage.setItem("xinque_session_id", sid);
      }
    } catch { /* ignore */ }
  }, [sessionList]);

  const handleMoodSelect = useCallback(async (score: number) => {
    setShowMoodCheckin(false);
    if (sessionId) {
      try {
        await fetch(`${API_BASE}/api/sessions/${sessionId}/mood`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mood_score: score }),
        });
        loadMoodTrend();
        loadSessionList();
      } catch { /* ignore */ }
    }
  }, [sessionId, loadMoodTrend, loadSessionList]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={S.root}>
      {/* 侧边栏 */}
      {sidebarOpen && (
        <div style={S.sidebar}>
          <div style={S.sidebarHeader}>
            <span style={{ fontWeight: 600, fontSize: "15px" }}>会话记录</span>
            <button style={S.sidebarClose} onClick={() => setSidebarOpen(false)}>✕</button>
          </div>
          <button style={S.newChatSidebar} onClick={newSession}>+ 新对话</button>
          <div style={S.trendCard}>
            <div style={S.trendTitle}>情绪趋势</div>
            <div style={S.trendStats}>
              <div>
                <div style={S.trendStatValue}>
                  {moodTrend.average_mood_score?.toFixed(1) ?? "--"}
                </div>
                <div style={S.trendStatLabel}>平均分</div>
              </div>
              <div>
                <div style={S.trendStatValue}>{moodTrend.count}</div>
                <div style={S.trendStatLabel}>已签到</div>
              </div>
              <div>
                <div style={S.trendStatValue}>
                  {moodTrend.latest_mood_score ?? "--"}
                </div>
                <div style={S.trendStatLabel}>最近一次</div>
              </div>
            </div>
            <div style={S.trendChart}>
              {moodTrend.points.length ? moodTrend.points.map((point) => (
                <div key={point.session_id} style={S.trendBarWrap} title={`${point.date || ""} ${point.score}分`}>
                  <div style={{ ...S.trendBar, height: `${point.score * 16}px` }} />
                </div>
              )) : (
                <div style={S.trendEmpty}>还没有足够的数据</div>
              )}
            </div>
            <div style={S.trendHint}>{describeMoodTrend(moodTrend)}</div>
          </div>
          <div style={S.sessionList}>
            {sessionList.map((s) => (
              <div
                key={s.session_id}
                style={{
                  ...S.sessionItem,
                  ...(s.session_id === sessionId && !viewingHistory ? S.sessionItemActive : {}),
                }}
                onClick={() => viewSession(s.session_id)}
              >
                <div style={S.sessionItemTop}>
                  <span style={S.sessionDate}>{formatDate(s.started_at)}</span>
                  {s.opening_mood_score && (
                    <span style={S.sessionMood}>{MOOD_OPTIONS[s.opening_mood_score - 1]?.emoji}</span>
                  )}
                  {s.ended_at && <span style={S.sessionEnded}>已结束</span>}
                </div>
                <div style={S.sessionSummary}>
                  {s.summary_preview || "新对话"}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 主聊天区 */}
      <div style={S.main}>
        <div style={S.header}>
          {!sidebarOpen && (
            <button style={S.menuButton} onClick={() => setSidebarOpen(true)}>☰</button>
          )}
          <span>心雀</span>
          {viewingHistory && <span style={S.historyBadge}>查看历史</span>}
          <a href="#admin" style={S.adminLink}>统计</a>
          <button style={S.newChatButton} onClick={newSession}>新对话</button>
        </div>

        {/* 情绪签到 */}
        {showMoodCheckin && <MoodCheckin onSelect={handleMoodSelect} />}

        <div style={S.messageList}>
          {messages.map((msg, i) => (
            <div key={i}>
              <div
                style={{
                  ...S.messageBubble,
                  ...(msg.role === "user" ? S.userBubble : S.assistantBubble),
                }}
              >
                {msg.content}
                {msg.role === "assistant" && msg.card_data && <CardRenderer card={msg.card_data} />}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ ...S.messageBubble, ...S.assistantBubble }}>正在思考...</div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div style={S.inputArea}>
          {viewingHistory ? (
            <div style={S.historyNotice}>
              此会话已结束
              <button style={S.backButton} onClick={newSession}>开始新对话</button>
            </div>
          ) : (
            <>
              <textarea
                style={S.textarea}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="输入你想说的..."
                rows={1}
              />
              <button
                style={{ ...S.sendButton, ...(loading || !input.trim() ? S.sendButtonDisabled : {}) }}
                onClick={sendMessage}
                disabled={loading || !input.trim()}
              >
                发送
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── 样式 ──

const S: Record<string, React.CSSProperties> = {
  root: {
    display: "flex",
    height: "100vh",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  // 侧边栏
  sidebar: {
    width: "260px",
    borderRight: "1px solid #e5e5e5",
    display: "flex",
    flexDirection: "column",
    backgroundColor: "#fafafa",
    flexShrink: 0,
  },
  sidebarHeader: {
    padding: "14px 16px",
    borderBottom: "1px solid #e5e5e5",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  sidebarClose: {
    border: "none",
    background: "none",
    fontSize: "16px",
    cursor: "pointer",
    color: "#9ca3af",
    padding: "2px 6px",
  },
  newChatSidebar: {
    margin: "12px 12px 8px",
    padding: "8px",
    borderRadius: "8px",
    border: "1px dashed #d1d5db",
    backgroundColor: "#fff",
    color: "#4f46e5",
    fontSize: "13px",
    cursor: "pointer",
    fontWeight: 500,
  },
  trendCard: {
    margin: "0 12px 12px",
    padding: "12px",
    borderRadius: "14px",
    background: "linear-gradient(180deg, #fff7ed 0%, #ffffff 100%)",
    border: "1px solid #fed7aa",
    boxShadow: "0 8px 18px rgba(251, 146, 60, 0.08)",
  },
  trendTitle: {
    fontSize: "13px",
    fontWeight: 700,
    color: "#9a3412",
    marginBottom: "10px",
  },
  trendStats: {
    display: "grid",
    gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
    gap: "8px",
    marginBottom: "12px",
  },
  trendStatValue: {
    fontSize: "18px",
    fontWeight: 700,
    color: "#7c2d12",
  },
  trendStatLabel: {
    fontSize: "11px",
    color: "#9a3412",
  },
  trendChart: {
    height: "92px",
    display: "flex",
    alignItems: "flex-end",
    gap: "6px",
    marginBottom: "10px",
  },
  trendBarWrap: {
    flex: 1,
    minWidth: 0,
    height: "100%",
    display: "flex",
    alignItems: "flex-end",
  },
  trendBar: {
    width: "100%",
    borderRadius: "999px",
    background: "linear-gradient(180deg, #fb923c 0%, #ea580c 100%)",
  },
  trendEmpty: {
    fontSize: "12px",
    color: "#9a3412",
    alignSelf: "center",
  },
  trendHint: {
    fontSize: "12px",
    lineHeight: 1.5,
    color: "#7c2d12",
  },
  sessionList: {
    flex: 1,
    overflowY: "auto",
    padding: "0 8px 8px",
  },
  sessionItem: {
    padding: "10px 12px",
    borderRadius: "8px",
    cursor: "pointer",
    marginBottom: "4px",
    transition: "background-color 0.15s",
  },
  sessionItemActive: {
    backgroundColor: "#eef2ff",
    border: "1px solid #c7d2fe",
  },
  sessionItemTop: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    marginBottom: "4px",
  },
  sessionDate: {
    fontSize: "11px",
    color: "#9ca3af",
  },
  sessionMood: {
    fontSize: "12px",
  },
  sessionEnded: {
    fontSize: "10px",
    color: "#9ca3af",
    backgroundColor: "#f3f4f6",
    padding: "1px 6px",
    borderRadius: "4px",
  },
  sessionSummary: {
    fontSize: "12px",
    color: "#6b7280",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  // 主区域
  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    maxWidth: "700px",
    minWidth: 0,
  },
  header: {
    padding: "12px 16px",
    fontSize: "18px",
    fontWeight: 600,
    textAlign: "center",
    borderBottom: "1px solid #e5e5e5",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
    gap: "8px",
  },
  menuButton: {
    position: "absolute",
    left: 16,
    border: "none",
    background: "none",
    fontSize: "20px",
    cursor: "pointer",
    color: "#374151",
    padding: "2px 8px",
  },
  historyBadge: {
    fontSize: "11px",
    color: "#6b7280",
    backgroundColor: "#f3f4f6",
    padding: "2px 8px",
    borderRadius: "8px",
    fontWeight: 400,
  },
  newChatButton: {
    position: "absolute",
    right: 16,
    padding: "6px 14px",
    borderRadius: "16px",
    border: "1px solid #d1d5db",
    backgroundColor: "#fff",
    color: "#374151",
    fontSize: "13px",
    cursor: "pointer",
    fontWeight: 500,
  },
  adminLink: {
    position: "absolute",
    right: 88,
    padding: "6px 12px",
    borderRadius: "16px",
    border: "1px solid #d1d5db",
    backgroundColor: "#fff",
    color: "#2563eb",
    fontSize: "13px",
    textDecoration: "none",
    fontWeight: 500,
  },
  // 情绪签到
  moodOverlay: {
    position: "absolute",
    inset: 0,
    backgroundColor: "rgba(0,0,0,0.3)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 10,
  },
  moodCard: {
    backgroundColor: "#fff",
    borderRadius: "16px",
    padding: "28px 32px",
    textAlign: "center",
    boxShadow: "0 4px 24px rgba(0,0,0,0.12)",
  },
  moodButton: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "10px 8px",
    border: "1px solid #e5e5e5",
    borderRadius: "12px",
    backgroundColor: "#fff",
    cursor: "pointer",
    minWidth: "56px",
    transition: "all 0.15s",
  },
  // 消息区
  messageList: {
    flex: 1,
    overflowY: "auto",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  messageBubble: {
    maxWidth: "75%",
    padding: "10px 14px",
    borderRadius: "16px",
    lineHeight: 1.5,
    fontSize: "14px",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  userBubble: {
    alignSelf: "flex-end",
    backgroundColor: "#4f46e5",
    color: "#fff",
    borderBottomRightRadius: "4px",
  },
  assistantBubble: {
    alignSelf: "flex-start",
    backgroundColor: "#f3f4f6",
    color: "#1f2937",
    borderBottomLeftRadius: "4px",
  },
  // 输入区
  inputArea: {
    display: "flex",
    gap: "8px",
    padding: "12px 16px",
    borderTop: "1px solid #e5e5e5",
  },
  textarea: {
    flex: 1,
    padding: "10px 14px",
    borderRadius: "20px",
    border: "1px solid #d1d5db",
    outline: "none",
    fontSize: "14px",
    resize: "none",
    fontFamily: "inherit",
  },
  sendButton: {
    padding: "10px 20px",
    borderRadius: "20px",
    border: "none",
    backgroundColor: "#4f46e5",
    color: "#fff",
    fontSize: "14px",
    cursor: "pointer",
    fontWeight: 500,
  },
  sendButtonDisabled: {
    backgroundColor: "#9ca3af",
    cursor: "not-allowed",
  },
  historyNotice: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "12px",
    color: "#9ca3af",
    fontSize: "13px",
  },
  backButton: {
    padding: "6px 14px",
    borderRadius: "16px",
    border: "1px solid #d1d5db",
    backgroundColor: "#fff",
    color: "#4f46e5",
    fontSize: "13px",
    cursor: "pointer",
    fontWeight: 500,
  },
};
