import apiClient from "./apiClient";

export const sendMessage = async (query , conversationId = null)=>{
const res = await apiClient.post(
    "/api/query/",
    {
        query,
        conversation_id : conversationId,
    }
);

return res.data;
}
