import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

const getAuthHeaders = () => {
  const accessToken = localStorage.getItem("access");
  return {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  };
};

export const conversationService = {
  // List all conversations
  listConversations: async (search = "") => {
    try {
      const url = search
        ? `${API_BASE}/conversations/?search=${encodeURIComponent(search)}`
        : `${API_BASE}/conversations/`;
      const response = await axios.get(url, getAuthHeaders());
      return response.data;
    } catch (error) {
      console.error("Error fetching conversations:", error);
      throw error;
    }
  },

  // Create a new conversation
  createConversation: async (title = "New conversation") => {
    try {
      const response = await axios.post(
        `${API_BASE}/conversations/`,
        { title },
        getAuthHeaders()
      );
      return response.data;
    } catch (error) {
      console.error("Error creating conversation:", error);
      throw error;
    }
  },

  // Get a single conversation with messages
  getConversation: async (conversationId) => {
    try {
      const response = await axios.get(
        `${API_BASE}/conversations/${conversationId}/`,
        getAuthHeaders()
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching conversation:", error);
      throw error;
    }
  },

  // Update conversation (rename/archive)
  updateConversation: async (conversationId, data) => {
    try {
      const response = await axios.patch(
        `${API_BASE}/conversations/${conversationId}/`,
        data,
        getAuthHeaders()
      );
      return response.data;
    } catch (error) {
      console.error("Error updating conversation:", error);
      throw error;
    }
  },

  // Delete a conversation
  deleteConversation: async (conversationId) => {
    try {
      await axios.delete(
        `${API_BASE}/conversations/${conversationId}/`,
        getAuthHeaders()
      );
      return true;
    } catch (error) {
      console.error("Error deleting conversation:", error);
      throw error;
    }
  },

  // Send a query to a conversation
  sendQuery: async (query, conversationId = null, topK = 5) => {
    try {
      const response = await axios.post(
        `${API_BASE}/legal-ai/query/`,
        {
          query,
          conversation_id: conversationId,
          top_k: topK,
        },
        getAuthHeaders()
      );
      return response.data;
    } catch (error) {
      console.error("Error sending query:", error);
      throw error;
    }
  },
};
