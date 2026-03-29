const CLIENT_ID_KEY = "xinque_client_id";
const SESSION_ID_KEY = "xinque_session_id";

export function getClientId(): string {
  let id = localStorage.getItem(CLIENT_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(CLIENT_ID_KEY, id);
  }
  return id;
}

export function getStoredSessionId(): string | null {
  return localStorage.getItem(SESSION_ID_KEY);
}

export function setStoredSessionId(sessionId: string | null): void {
  if (sessionId) {
    localStorage.setItem(SESSION_ID_KEY, sessionId);
    return;
  }
  localStorage.removeItem(SESSION_ID_KEY);
}
