import React, { createContext, useContext } from "react";

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

// DEMO MODE: Hardcoded admin user — no API calls or tokens required.
// Revert this file to restore real authentication.
const DEMO_ADMIN: AdminUser = {
    id: 0,
    email: "demo@portal.local",
    full_name: "Demo Admin",
    role: "super_admin",
    is_active: true,
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const value: AuthContextType = {
        admin: DEMO_ADMIN,
        token: "demo-token",
        isLoading: false,
        login: async () => { },
        logout: () => { },
    };

    return (
        <AuthContext.Provider value={value}>
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
