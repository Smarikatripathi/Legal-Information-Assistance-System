import apiClient from "./apiClient";

export const conversationService = {
  // List all conversations
  listConversations: async (search = "") => {
    try {
      const response = await apiClient.get(
        search
          ? `/api/conversations/?search=${encodeURIComponent(search)}`
          : "/api/conversations/"
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching conversations:", error);
      throw error;
    }
  },

  // Create a new conversation
  createConversation: async (title = "New conversation") => {
    try {
      const response = await apiClient.post("/api/conversations/", { title });
      return response.data;
    } catch (error) {
      console.error("Error creating conversation:", error);
      throw error;
    }
  },

  // Get a single conversation with messages
  getConversation: async (conversationId) => {
    try {
      const response = await apiClient.get(`/api/conversations/${conversationId}/`);
      return response.data;
    } catch (error) {
      console.error("Error fetching conversation:", error);
      throw error;
    }
  },

  // Update conversation (rename/archive)
  updateConversation: async (conversationId, data) => {
    try {
      const response = await apiClient.patch(`/api/conversations/${conversationId}/`, data);
      return response.data;
    } catch (error) {
      console.error("Error updating conversation:", error);
      throw error;
    }
  },

  // Delete a conversation
  deleteConversation: async (conversationId) => {
    try {
      await apiClient.delete(`/api/conversations/${conversationId}/`);
      return true;
    } catch (error) {
      console.error("Error deleting conversation:", error);
      throw error;
    }
  },

  // Send a query to a conversation
  sendQuery: async (query, conversationId = null, topK = 5) => {
    try {
      const response = await apiClient.post(
        "/api/legal-ai/query/",
        {
          query,
          conversation_id: conversationId,
          top_k: topK,
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error sending query:", error);
      throw error;
    }
  },
};
