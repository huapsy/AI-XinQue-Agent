export interface SessionMessagesResponse {
  exists?: boolean;
  messages?: unknown;
}

export function shouldRestoreSavedSession(data: SessionMessagesResponse): boolean {
  return data.exists !== false && Array.isArray(data.messages);
}
