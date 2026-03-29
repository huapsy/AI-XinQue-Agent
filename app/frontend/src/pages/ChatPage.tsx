import ChatWindow from "../components/chat/ChatWindow";

interface ChatPageProps {
  sessionId: string | null;
  historyMode: boolean;
}

export default function ChatPage({ sessionId, historyMode }: ChatPageProps) {
  return <ChatWindow routeSessionId={sessionId} routeHistoryMode={historyMode} />;
}
