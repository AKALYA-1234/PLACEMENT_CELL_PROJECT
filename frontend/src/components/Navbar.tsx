import React from "react";
import { useAuth } from "../contexts/AuthContext";
import { useTheme } from "../contexts/ThemeContext";
import { ShieldCheck, Sun, Moon } from "lucide-react";

// DEMO MODE: Logout button removed. Admin info comes from real API response.
export const Navbar: React.FC = () => {
    const { admin } = useAuth();
    const { theme, toggleTheme } = useTheme();

    return (
        <header className="h-16 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40 px-6 flex items-center justify-between transition-colors duration-200">
            <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-xl shadow-lg shadow-indigo-500/20">
                    <ShieldCheck className="w-5 h-5 text-slate-900 dark:text-white" />
                </div>
                <div>
                    <h1 className="text-base font-bold text-slate-900 dark:text-white tracking-wide">PLACEMENT CELL PORTAL</h1>
                    <p className="text-xs text-indigo-600 dark:text-indigo-400 font-medium">ADMINISTRATIVE MANAGEMENT & ANALYTICS</p>
                </div>
            </div>

            <div className="flex items-center space-x-4">
                <button
                    onClick={toggleTheme}
                    className="p-2 text-slate-600 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-all"
                    title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
                >
                    {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
                </button>

                {admin && (
                    <div className="flex items-center space-x-3 bg-slate-100 dark:bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-200 dark:border-slate-700/60">
                        <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs">
                            {admin.full_name?.charAt(0) || "A"}
                        </div>
                        <div className="text-left hidden sm:block">
                            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{admin.full_name}</p>
                            <p className="text-[10px] text-slate-500 dark:text-slate-400">{admin.role}</p>
                        </div>
                    </div>
                )}
            </div>
        </header>
    );
};
