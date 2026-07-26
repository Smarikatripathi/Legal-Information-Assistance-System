"use client";

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import DashboardLayout from "../layout/DashboardLayout";
import { conversationService } from "../services/conversationService";

const Dashboard = () => {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [refreshConversations, setRefreshConversations] = useState(0);
  const [loading, setLoading] = useState(false);
  const { conversationId: urlConversationId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    if (urlConversationId) {
      loadConversation(urlConversationId);
    } else {
      // New chat - clear messages
      setMessages([]);
      setConversationId(null);
      setCurrentConversationId(null);
    }
  }, [urlConversationId]);

  const loadConversation = async (convId) => {
    setLoading(true);
    try {
      const data = await conversationService.getConversation(convId);
      setConversationId(convId);
      setCurrentConversationId(convId);
      
      // Convert API messages to frontend format
      const formattedMessages = data.messages.map((msg) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.created_at,
      }));
      setMessages(formattedMessages);
    } catch (error) {
      console.error("Failed to load conversation:", error);
      // If conversation not found, navigate to new chat
      navigate("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const triggerConversationRefresh = () => {
    setRefreshConversations((prev) => prev + 1);
  };

  return (
    <DashboardLayout
      messages={messages}
      setMessages={setMessages}
      conversationId={conversationId}
      setConversationId={setConversationId}
      currentConversationId={currentConversationId}
      refreshConversations={refreshConversations}
      setRefreshConversations={setRefreshConversations}
    />
  );
};

export default Dashboard;