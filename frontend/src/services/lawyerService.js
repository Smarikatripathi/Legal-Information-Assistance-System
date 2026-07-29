import axios from "axios";

const API = "http://localhost:8000/api";

export const getLawyers = async () => {
  const res = await axios.get(`${API}/lawyers/`);

  return res.data;
};

export const getLawyer = async (id) => {
  const res = await axios.get(`${API}/lawyers/${id}/`);

  return res.data;
};