import { useEffect, useState } from "react";
import ChatWindow from "./components/chat/ChatWindow";
import AdminDashboard from "./components/admin/AdminDashboard";

function App() {
  const [hash, setHash] = useState(window.location.hash);

  useEffect(() => {
    const onHashChange = () => setHash(window.location.hash);
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  if (hash === "#admin") {
    return <AdminDashboard />;
  }
  return <ChatWindow />;
}

export default App;
