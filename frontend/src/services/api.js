import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: API_URL, headers: { "Content-Type": "application/json" } });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (d) => api.post("/api/auth/register", d),
  login: (d) => api.post("/api/auth/login", d),
};

export const reviewAPI = {
  trigger: (d) => api.post("/api/reviews/trigger", d),
  list: (params) => api.get("/api/reviews/", { params }),
  get: (id) => api.get(`/api/reviews/${id}`),
  getComment: (id) => api.get(`/api/reviews/${id}/comment`),
};

export const repoAPI = {
  list: () => api.get("/api/repos/"),
  add: (d) => api.post("/api/repos/", d),
  delete: (id) => api.delete(`/api/repos/${id}`),
};

export const analyticsAPI = {
  dashboard: () => api.get("/api/analytics/dashboard"),
  mlflow: () => api.get("/api/analytics/mlflow"),
  faiss: () => api.get("/api/analytics/faiss"),
};

export default api;
