import { useEffect, useState } from "react";
import { parseHashRoute } from "./navigation";
import AdminPage from "./pages/AdminPage";
import ChatPage from "./pages/ChatPage";
import HistoryPage from "./pages/HistoryPage";

function App() {
  const [hash, setHash] = useState(window.location.hash);

  useEffect(() => {
    const onHashChange = () => setHash(window.location.hash);
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const parsed = parseHashRoute(hash);

  if (parsed.route === "admin") {
    return <AdminPage />;
  }
  if (parsed.route === "history") {
    return <HistoryPage />;
  }
  return (
    <ChatPage
      key={hash}
      sessionId={parsed.params.get("session")}
      historyMode={parsed.params.get("history") === "1"}
    />
  );
}

export default App;
