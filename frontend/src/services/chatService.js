import apiClient from "./apiClient";

/* ------------------------- */
/* Send Message              */
/* ------------------------- */

export const sendMessage = async (
  query,
  conversationId = null
) => {
  const res = await apiClient.post(
    "/api/legal-ai/query/",
    {
      query,
      conversation_id: conversationId,
    }
  );

  return res.data;
};

/* ------------------------- */
/* Conversation History      */
/* ------------------------- */

export const getConversations = async () => {
  const res = await apiClient.get("/api/conversations/");
  return res.data;
};

/* ------------------------- */
/* Single Conversation       */
/* ------------------------- */

export const getConversation = async (conversationId) => {
  const res = await apiClient.get(`/api/conversations/${conversationId}/`);
  return res.data;
};

/* ------------------------- */
/* Delete Conversation       */
/* ------------------------- */

export const deleteConversation = async (conversationId) => {
  await apiClient.delete(`/api/conversations/${conversationId}/`);
};