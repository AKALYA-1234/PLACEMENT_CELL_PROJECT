import React, { createContext, useContext, useState } from "react";

// TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
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

// TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
// DEMO MODE: Static demo admin user — no login API calls, credentials, or tokens required.
const DEMO_ADMIN: AdminUser = {
    id: 1,
    email: "admin@college.edu",
    full_name: "Demo Admin",
    role: "super_admin",
    is_active: true,
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
    const [admin] = useState<AdminUser | null>(DEMO_ADMIN);
    const [token] = useState<string | null>("demo-token");
    const [isLoading] = useState<boolean>(false);

    const login = async () => {
        // TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
    };

    const logout = () => {
        // TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
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
