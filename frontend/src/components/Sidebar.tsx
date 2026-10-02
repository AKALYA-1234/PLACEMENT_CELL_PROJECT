import React from "react";
import { NavLink } from "react-router-dom";
import {
    LayoutDashboard,
    Upload,
    History,
    Users,
    Building2,
    BarChart3,
} from "lucide-react";

const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { to: "/import/upload", label: "Upload Excel", icon: Upload },
    { to: "/imports", label: "Import History", icon: History },
    { to: "/students", label: "Students", icon: Users },
    { to: "/companies", label: "Companies", icon: Building2 },
    { to: "/analytics", label: "Analytics", icon: BarChart3 },
];

export const Sidebar: React.FC = () => {
    return (
        <aside className="w-64 bg-slate-900/60 border-r border-slate-800 h-[calc(100vh-4rem)] sticky top-16 flex flex-col py-4 px-3 overflow-y-auto">
            <nav className="flex-1 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                            `flex items-center space-x-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${isActive
                                ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/20 shadow-sm shadow-indigo-500/5"
                                : "text-slate-400 hover:text-white hover:bg-slate-800/80 border border-transparent"
                            }`
                        }
                    >
                        <item.icon className="w-4.5 h-4.5 shrink-0" />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="mt-auto pt-4 border-t border-slate-800/60">
                <div className="bg-gradient-to-r from-indigo-600/10 to-purple-600/10 border border-indigo-500/15 rounded-xl p-3">
                    <p className="text-xs text-indigo-300 font-semibold">Admin Portal v1.0</p>
                    <p className="text-[10px] text-slate-500 mt-0.5">Placement Cell System</p>
                </div>
            </div>
        </aside>
    );
};
