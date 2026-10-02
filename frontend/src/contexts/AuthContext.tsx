import React, { createContext, useContext, useState, useEffect } from "react";
import { api } from "../api/client";

export interface AdminUser {
    id: number;
    email: string;
    full_name: string;
    role: string;
    is_active: boolean;
}

interface AuthContextType {
    admin: AdminUser | null;
    token: string | null;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [admin, setAdmin] = useState<AdminUser | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchAdmin = async () => {
            if (!token) {
                setIsLoading(false);
                return;
            }
            try {
                const response = await api.get<AdminUser>("/api/auth/me");
                setAdmin(response.data);
            } catch (err) {
                console.error("Failed to verify token:", err);
                localStorage.removeItem("token");
                setToken(null);
                setAdmin(null);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAdmin();
    }, [token]);

    const login = async (email: string, password: string) => {
        const response = await api.post<{ access_token: string }>("/api/auth/login", { email, password });
        const accessToken = response.data.access_token;
        localStorage.setItem("token", accessToken);
        setToken(accessToken);

        const meResponse = await api.get<AdminUser>("/api/auth/me", {
            headers: { Authorization: `Bearer ${accessToken}` },
        });
        setAdmin(meResponse.data);
    };

    const logout = () => {
        localStorage.removeItem("token");
        setToken(null);
        setAdmin(null);
    };

    return (
        <AuthContext.Provider value={{ admin, token, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
