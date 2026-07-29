import { useEffect, useState } from "react";

import DashboardLayout from "../layouts/DashboardLayout";
import { getConversations } from "../services/chatService";

const Dashboard = () => {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);

  const [conversations, setConversations] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
  try {
    setHistoryLoading(true);

    const data = await getConversations();

    setConversations(data);

  } catch (error) {
    console.log(
      "AUTH ERROR:",
      error.response?.data
    );

    console.error(error);

  } finally {
    setHistoryLoading(false);
  }
};

  return (
    <DashboardLayout
      messages={messages}
      setMessages={setMessages}
      conversationId={conversationId}
      setConversationId={setConversationId}
      conversations={conversations}
      setConversations={setConversations}
      historyLoading={historyLoading}
      loadConversations={loadConversations}
    />
  );
};

export default Dashboard;