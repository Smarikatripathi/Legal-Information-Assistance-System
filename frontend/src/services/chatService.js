import axios from "axios";

const API = "http://localhost:8000/api";

export const sendMessage = async (query , conversationId = null)=>{
const token = localStorage.getItem("access");

const res = await axios.post(
    `${API}/query/`,
    {
        query,
        conversation_id : conversationId,
    },
    {
        headers:{
            Authorization : `Bearer ${token}`
        },
    }
);

return res.data;
}
