import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import {
    Users, Building2, TrendingUp, Award, Target,
    ArrowUpRight, BarChart3, Upload
} from "lucide-react";

interface OverviewData {
    total_students: number;
    students_placed: number;
    total_placed?: number;
    students_not_placed: number;
    unplaced_students?: number;
    placement_rate_percentage: number;
    total_companies: number;
    total_drives: number;
    average_ctc_lpa: number;
    highest_ctc_lpa: number;
}

const DashboardPage: React.FC = () => {
    const [data, setData] = useState<OverviewData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchOverview = async () => {
            try {
                const res = await api.get<OverviewData>("/admin/analytics/overview");
                setData(res.data);
            } catch (err: any) {
                setError(err.response?.data?.detail || "Failed to load dashboard data.");
            } finally {
                setIsLoading(false);
            }
        };
        fetchOverview();
    }, []);

    if (isLoading) return <LoadingSpinner message="Loading dashboard..." />;

    if (error) {
        return (
            <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-6 text-rose-300 text-sm">
                {error}
            </div>
        );
    }

    if (!data) return null;

    const kpiCards = [
        {
            label: "Total Students",
            value: data.total_students,
            icon: Users,
            gradient: "from-indigo-600 to-blue-600",
            shadow: "shadow-indigo-500/20",
        },
        {
            label: "Total Companies",
            value: data.total_companies,
            icon: Building2,
            gradient: "from-violet-600 to-purple-600",
            shadow: "shadow-violet-500/20",
        },
        {
            label: "Total Drives",
            value: data.total_drives,
            icon: Target,
            gradient: "from-cyan-600 to-teal-600",
            shadow: "shadow-cyan-500/20",
        },
        {
            label: "Students Placed",
            value: data.students_placed ?? data.total_placed ?? 0,
            icon: Award,
            gradient: "from-emerald-600 to-green-600",
            shadow: "shadow-emerald-500/20",
        },
        {
            label: "Placement Rate",
            value: `${data.placement_rate_percentage}%`,
            icon: TrendingUp,
            gradient: "from-amber-600 to-orange-600",
            shadow: "shadow-amber-500/20",
        },
        {
            label: "Highest CTC (LPA)",
            value: data.highest_ctc_lpa,
            icon: BarChart3,
            gradient: "from-rose-600 to-pink-600",
            shadow: "shadow-rose-500/20",
        },
    ];

    return (
        <div className="space-y-6">
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Admin Dashboard</h1>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">Overview of placement activity and key metrics</p>
                </div>
                <Link
                    to="/import/upload"
                    className="inline-flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-600/25 transition-all"
                >
                    <Upload className="w-4 h-4" />
                    <span>Import Excel</span>
                </Link>
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {kpiCards.map((card) => (
                    <div
                        key={card.label}
                        className={`relative overflow-hidden bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 group hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-md dark:shadow-xl ${card.shadow}`}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                                    {card.label}
                                </p>
                                <p className="text-3xl font-extrabold text-slate-900 dark:text-white mt-1.5">{card.value}</p>
                            </div>
                            <div
                                className={`p-3 rounded-xl bg-gradient-to-tr ${card.gradient} shadow-lg group-hover:scale-110 transition-transform`}
                            >
                                <card.icon className="w-6 h-6 text-white" />
                            </div>
                        </div>
                        <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-gradient-to-tr from-transparent to-slate-900/[0.02] dark:to-white/[0.02] rounded-full" />
                    </div>
                ))}
            </div>

            {/* Secondary Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
                    <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-4">
                        Placement Summary
                    </h3>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-600 dark:text-slate-300">Unplaced Students</span>
                            <span className="text-lg font-bold text-rose-500 dark:text-rose-400">{data.unplaced_students}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-600 dark:text-slate-300">Average CTC (LPA)</span>
                            <span className="text-lg font-bold text-indigo-600 dark:text-indigo-400">{data.average_ctc_lpa}</span>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
                    <h3 className="text-sm font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-4">
                        Quick Actions
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                        {[
                            { label: "Students", to: "/students", icon: Users },
                            { label: "Companies", to: "/companies", icon: Building2 },
                            { label: "Analytics", to: "/analytics", icon: BarChart3 },
                            { label: "Import History", to: "/imports", icon: TrendingUp },
                        ].map((item) => (
                            <Link
                                key={item.to}
                                to={item.to}
                                className="flex items-center space-x-2 p-3 bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700/50 hover:border-indigo-300 dark:hover:border-indigo-500/30 rounded-xl transition-all group"
                            >
                                <item.icon className="w-4 h-4 text-slate-500 dark:text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
                                <span className="text-sm text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">
                                    {item.label}
                                </span>
                                <ArrowUpRight className="w-3 h-3 text-slate-400 dark:text-slate-500 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 ml-auto transition-colors" />
                            </Link>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;
