import React from "react";
import { Outlet } from "react-router-dom";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

// TODO: RESTORE AUTHENTICATION BEFORE PRODUCTION
// DEMO MODE: Layout renders directly without waiting for login or checking auth state.
export const Layout: React.FC = () => {
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
