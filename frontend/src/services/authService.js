import axios from "axios";

const API = "http://localhost:8000/api/auth"; 
const API2 = "http://localhost:8000/api/users/me/"
// adjust if your backend prefix is different

// ---------------- LOGIN ----------------
export const loginFetch = async (email, password) => {
  const res = await axios.post(`${API}/login/`, {
    email,
    password,
  });

  // store tokens
  if (res.data.access) {
    localStorage.setItem("access", res.data.access);
    localStorage.setItem("refresh", res.data.refresh);
  }
  return res.data;
};

// ---------------- SIGNUP ----------------
export const signup = async (data) => {
  const res = await axios.post(`${API}/signup/`, data);

  if (res.data.access) {
    localStorage.setItem("access", res.data.access);
    localStorage.setItem("refresh", res.data.refresh);
  }

  return res.data;
};

// ---------------- LOGOUT ----------------
export const logout = async () => {
  const refresh = localStorage.getItem("refresh");

  await axios.post(`${API}/logout/`, { refresh });

  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};

// ---------------- PROFILE ----------------
export const getProfile = async () => {
  const token = localStorage.getItem("access");

  const res = await axios.get(`${API2}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return res.data;
};

// ---------------- UPDATE PROFILE ----------------
export const updateProfile = async (data) => {
  const token = localStorage.getItem("access");

  const res = await axios.patch(`${API}/profile/`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return res.data;
};