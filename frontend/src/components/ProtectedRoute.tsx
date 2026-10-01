import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { token, loading } = useAuth();

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="flex items-center space-x-3 text-blue-400">
                    <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="font-medium text-slate-300">Authenticating...</span>
                </div>
            </div>
        );
    }

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
};
