import axios from "axios";

const API = "http://localhost:8000/api";

const getAuthConfig = () => {
  const token = localStorage.getItem("access");

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
};

/* ------------------------- */
/* Send Message              */
/* ------------------------- */

export const sendMessage = async (
  query,
  conversationId = null
) => {
  const res = await axios.post(
    `${API}/query/`,
    {
      query,
      conversation_id: conversationId,
    },
    getAuthConfig()
  );

  return res.data;
};

/* ------------------------- */
/* Conversation History      */
/* ------------------------- */

export const getConversations = async () => {
  const res = await axios.get(
    `${API}/conversations/`,
    getAuthConfig()
  );

  return res.data;
};

/* ------------------------- */
/* Single Conversation       */
/* ------------------------- */

export const getConversation = async (conversationId) => {
  const res = await axios.get(
    `${API}/conversations/${conversationId}/`,
    getAuthConfig()
  );

  return res.data;
};

/* ------------------------- */
/* Delete Conversation       */
/* ------------------------- */

export const deleteConversation = async (conversationId) => {
  await axios.delete(
    `${API}/conversations/${conversationId}/`,
    getAuthConfig()
  );
};