import axios from "axios";

const API = "http://localhost:8000/api/auth"; 
const API2 = "http://localhost:8000/api/users/me/";
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

// ---------------- FORGOT PASSWORD ----------------

export const forgotPassword = async (email) => {
  const res = await axios.post(
    `${API}/forgot-password/`,
    {
      email,
    }
  );

  return res.data;
};


// ---------------- RESET PASSWORD ----------------

export const resetPassword = async (
  uid,
  token,
  new_password
) => {

  const res = await axios.post(
    `${API}/reset-password/`,
    {
      uid,
      token,
      new_password,
    }
  );

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

// ---------------- CHANGE PASSWORD ----------------
export const changePassword = async (oldPassword, newPassword) => {
  const token = localStorage.getItem("access");

  const res = await axios.post(
    `${API}/change-password/`,
    {
      old_password: oldPassword,
      new_password: newPassword,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return res.data;
};
