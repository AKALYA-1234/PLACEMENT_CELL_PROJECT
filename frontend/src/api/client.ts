import axios from "axios";

const API_BASE_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// DEMO MODE: 401 redirect interceptor removed to prevent login redirects.
api.interceptors.response.use(
    (response) => response,
    (error) => Promise.reject(error)
);
