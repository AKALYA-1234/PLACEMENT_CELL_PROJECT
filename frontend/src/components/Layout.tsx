import React from "react";
import { Outlet } from "react-router-dom";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { useAuth } from "../contexts/AuthContext";
import { LoadingSpinner } from "./LoadingSpinner";

// DEMO MODE: Shows loading spinner while auto-login completes,
// error message if demo auth fails, then the dashboard.
export const Layout: React.FC = () => {
    const { isLoading, demoError } = useAuth();

    if (isLoading) {
        return (
            <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center transition-colors duration-200">
                <LoadingSpinner message="Authenticating demo session..." />
            </div>
        );
    }

    if (demoError) {
        return (
            <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center transition-colors duration-200">
                <div className="bg-white dark:bg-slate-900 border border-rose-200 dark:border-rose-800 rounded-2xl p-8 max-w-md text-center shadow-xl">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center">
                        <svg className="w-6 h-6 text-rose-600 dark:text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                    </div>
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Connection Error</h2>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{demoError}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white transition-colors duration-200">
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
