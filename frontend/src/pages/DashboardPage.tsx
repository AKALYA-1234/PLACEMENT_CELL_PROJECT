import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, LayoutDashboard, Upload, Search, Building2, BarChart3, Settings } from 'lucide-react';

export const DashboardPage: React.FC = () => {
    const { admin, logout } = useAuth();

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex">
            {/* Sidebar Navigation */}
            <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col">
                <div className="p-6 flex items-center space-x-3 border-b border-slate-800">
                    <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center font-bold text-white shadow-md shadow-blue-500/20">
                        PC
                    </div>
                    <div>
                        <h1 className="font-bold text-slate-100 text-sm">Placement Portal</h1>
                        <p className="text-xs text-slate-400">Admin Control Center</p>
                    </div>
                </div>

                <nav className="flex-1 p-4 space-y-1.5">
                    <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl bg-blue-600/10 text-blue-400 font-medium text-sm border border-blue-500/20">
                        <LayoutDashboard className="w-4 h-4" />
                        <span>Dashboard</span>
                    </a>
                    <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors text-sm font-medium">
                        <Upload className="w-4 h-4" />
                        <span>Excel Upload</span>
                    </a>
                    <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors text-sm font-medium">
                        <Search className="w-4 h-4" />
                        <span>Student Search</span>
                    </a>
                    <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors text-sm font-medium">
                        <Building2 className="w-4 h-4" />
                        <span>Companies</span>
                    </a>
                    <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors text-sm font-medium">
                        <BarChart3 className="w-4 h-4" />
                        <span>Analytics</span>
                    </a>
                    <a href="#" className="flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors text-sm font-medium">
                        <Settings className="w-4 h-4" />
                        <span>Settings</span>
                    </a>
                </nav>

                <div className="p-4 border-t border-slate-800">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-semibold text-slate-300 text-xs">
                                {admin?.username ? admin.username[0].toUpperCase() : 'A'}
                            </div>
                            <div className="text-xs">
                                <p className="font-semibold text-slate-200">{admin?.username}</p>
                                <p className="text-slate-500">Administrator</p>
                            </div>
                        </div>
                        <button
                            onClick={logout}
                            title="Logout"
                            className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors cursor-pointer"
                        >
                            <LogOut className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 p-8 overflow-y-auto">
                <header className="mb-8">
                    <h2 className="text-2xl font-bold text-slate-100">Welcome, {admin?.username} 👋</h2>
                    <p className="text-sm text-slate-400 mt-1">Phase 1 Admin Shell & Authentication System Ready.</p>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">System Status</p>
                        <p className="text-xl font-bold text-emerald-400 mt-2 flex items-center space-x-2">
                            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
                            <span>Backend Connected</span>
                        </p>
                    </div>
                    <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Auth Token</p>
                        <p className="text-xl font-bold text-blue-400 mt-2">Active JWT Session</p>
                    </div>
                    <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Database</p>
                        <p className="text-xl font-bold text-indigo-400 mt-2">SQLAlchemy Engine Ready</p>
                    </div>
                </div>

                <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80">
                    <h3 className="font-semibold text-slate-200 text-lg mb-2">Phase 1 Implementation Complete</h3>
                    <p className="text-sm text-slate-400">
                        The core authentication foundation, database ORM models, and navigation shell are active. Proceeding to Phase 2 for Excel parsing and normalization engine.
                    </p>
                </div>
            </main>
        </div>
    );
};
