import axios from "axios";
import { clearAuthTokens, getAccessToken, getRefreshToken, setAuthTokens } from "./tokenStorage";

const API_BASE = "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE,
});

let refreshPromise = null;
let redirectingToLogin = false;

const forceLogout = () => {
  clearAuthTokens();
  if (!redirectingToLogin && window.location.pathname !== "/") {
    redirectingToLogin = true;
    window.location.assign("/");
  }
};

const refreshAccessToken = async () => {
  const refresh = getRefreshToken();
  if (!refresh) {
    throw new Error("No refresh token available");
  }

  const response = await axios.post(`${API_BASE}/api/auth/token/refresh/`, {
    refresh,
  });

  const nextAccess = response.data?.access;
  const nextRefresh = response.data?.refresh;

  if (!nextAccess) {
    throw new Error("Refresh response did not include access token");
  }

  setAuthTokens({ access: nextAccess, refresh: nextRefresh });
  return nextAccess;
};

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    if (!originalRequest || status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    const requestUrl = originalRequest.url || "";
    if (
      requestUrl.includes("/api/auth/login/") ||
      requestUrl.includes("/api/auth/signup/") ||
      requestUrl.includes("/api/auth/logout/") ||
      requestUrl.includes("/api/auth/token/refresh/")
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      const newAccessToken = await refreshPromise;
      originalRequest.headers = originalRequest.headers ?? {};
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      forceLogout();
      return Promise.reject(refreshError);
    }
  }
);

export const logoutClientAuth = () => {
  clearAuthTokens();
  redirectingToLogin = false;
};

export default apiClient;
