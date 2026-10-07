import axios from "axios";

const API_BASE_URL =
    import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
// In demo mode, token is optional; if present in localStorage, it will be attached.
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

// TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
// 401 errors pass through without forcing /login redirects in unauthenticated demo mode.
api.interceptors.response.use(
    (response) => response,
    (error) => Promise.reject(error)
);
