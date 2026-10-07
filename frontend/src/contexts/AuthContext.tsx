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
    demoError: string | null;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// DEMO MODE: Auto-login credentials for the demo admin account.
// The frontend calls the real backend /api/auth/login on startup.
// Revert this file to restore manual login.
const DEMO_EMAIL = "admin@college.edu";
const DEMO_PASSWORD = "admin123";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [admin, setAdmin] = useState<AdminUser | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [demoError, setDemoError] = useState<string | null>(null);

    useEffect(() => {
        const demoLogin = async () => {
            try {
                // Step 1: Authenticate with the real backend login API
                const loginResponse = await api.post<{ access_token: string }>(
                    "/api/auth/login",
                    { email: DEMO_EMAIL, password: DEMO_PASSWORD }
                );
                const accessToken = loginResponse.data.access_token;

                // Step 2: Store the real JWT exactly like the normal login flow
                localStorage.setItem("token", accessToken);
                setToken(accessToken);

                // Step 3: Fetch the admin profile using the real token
                const meResponse = await api.get<AdminUser>("/api/auth/me", {
                    headers: { Authorization: `Bearer ${accessToken}` },
                });
                setAdmin(meResponse.data);
            } catch (err) {
                console.error("Demo auto-login failed:", err);
                setDemoError(
                    "Demo authentication failed. Please check the backend connection."
                );
                localStorage.removeItem("token");
                setToken(null);
                setAdmin(null);
            } finally {
                setIsLoading(false);
            }
        };

        demoLogin();
    }, []);

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
        <AuthContext.Provider value={{ admin, token, isLoading, demoError, login, logout }}>
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
