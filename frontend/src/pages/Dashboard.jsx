"use client";

import { useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";

const Dashboard = () => {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);

  return (
    <DashboardLayout
      messages={messages}
      setMessages={setMessages}
      conversationId={conversationId}
      setConversationId={setConversationId}
    />
  );
};

export default Dashboard;