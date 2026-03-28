export interface MoodTrendPoint {
  session_id: string;
  date: string | null;
  score: number;
}

export interface MoodTrendPayload {
  count: number;
  average_mood_score: number | null;
  latest_mood_score: number | null;
  trend_direction?: "up" | "down" | "stable";
  volatility?: number;
  points: MoodTrendPoint[];
}

export function describeMoodTrend(trend: MoodTrendPayload): string {
  if (!trend.count || trend.average_mood_score == null) {
    return "完成首次签到后，这里会开始显示你的情绪轨迹。";
  }

  if (trend.points.length < 2) {
    return "你已经留下第一条情绪记录，继续签到会更容易看见变化。";
  }

  if (trend.trend_direction === "up") {
    return "最近的状态比最开始更稳一些，继续保持这个节奏。";
  }
  if (trend.trend_direction === "down") {
    return "最近波动有点明显，如果愿意，可以把这段时间最难的部分聊出来。";
  }
  if ((trend.volatility ?? 0) >= 0.5) {
    return "最近有一些明显波动，适合继续观察哪些事件会影响你的状态。";
  }
  return "最近的起伏整体平稳，适合继续观察哪些时刻会拉低或抬高你的状态。";
}
