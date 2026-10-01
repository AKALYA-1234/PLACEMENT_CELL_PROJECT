import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';
import { AdminUser } from '../types';

interface AuthContextType {
    token: string | null;
    admin: AdminUser | null;
    loading: boolean;
    login: (token: string) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
    const [admin, setAdmin] = useState<AdminUser | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    const fetchAdmin = async () => {
        try {
            const res = await api.get('/auth/me');
            setAdmin(res.data);
        } catch {
            logout();
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (token) {
            fetchAdmin();
        } else {
            setLoading(false);
        }
    }, [token]);

    const login = async (newToken: string) => {
        localStorage.setItem('token', newToken);
        setToken(newToken);
        await fetchAdmin();
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setAdmin(null);
    };

    return (
        <AuthContext.Provider value={{ token, admin, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
