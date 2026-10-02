import React from "react";
import { useAuth } from "../contexts/AuthContext";
import { LogOut, User, ShieldCheck } from "lucide-react";

export const Navbar: React.FC = () => {
    const { admin, logout } = useAuth();

    return (
        <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 px-6 flex items-center justify-between">
            <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-xl shadow-lg shadow-indigo-500/20">
                    <ShieldCheck className="w-5 h-5 text-white" />
                </div>
                <div>
                    <h1 className="text-base font-bold text-white tracking-wide">PLACEMENT CELL PORTAL</h1>
                    <p className="text-xs text-indigo-400 font-medium">ADMINISTRATIVE MANAGEMENT & ANALYTICS</p>
                </div>
            </div>

            <div className="flex items-center space-x-4">
                {admin && (
                    <div className="flex items-center space-x-3 bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700/60">
                        <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs">
                            {admin.full_name?.charAt(0) || "A"}
                        </div>
                        <div className="text-left hidden sm:block">
                            <p className="text-xs font-semibold text-slate-200">{admin.full_name}</p>
                            <p className="text-[10px] text-slate-400">{admin.role}</p>
                        </div>
                    </div>
                )}

                <button
                    onClick={logout}
                    className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-all border border-transparent hover:border-rose-500/20"
                    title="Sign Out"
                >
                    <LogOut className="w-5 h-5" />
                </button>
            </div>
        </header>
    );
};
