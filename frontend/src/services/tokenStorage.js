export const getAccessToken = () => localStorage.getItem("access");
export const getRefreshToken = () => localStorage.getItem("refresh");

export const setAuthTokens = ({ access, refresh } = {}) => {
  if (access) {
    localStorage.setItem("access", access);
  }
  if (refresh) {
    localStorage.setItem("refresh", refresh);
  }
};

export const clearAuthTokens = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
};
