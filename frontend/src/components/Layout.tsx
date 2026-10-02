import React from "react";
import { Outlet, Navigate } from "react-router-dom";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { useAuth } from "../contexts/AuthContext";
import { LoadingSpinner } from "./LoadingSpinner";

export const Layout: React.FC = () => {
    const { admin, isLoading } = useAuth();

    if (isLoading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <LoadingSpinner message="Initializing admin portal..." />
            </div>
        );
    }

    if (!admin) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="min-h-screen bg-slate-950 text-white">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 overflow-auto min-h-[calc(100vh-4rem)]">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};
