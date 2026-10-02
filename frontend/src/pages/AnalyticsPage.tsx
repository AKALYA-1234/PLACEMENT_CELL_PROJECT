import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from "recharts";
import { BarChart3, PieChart as PieIcon, Layers, Building2 } from "lucide-react";

interface OverviewData {
    total_students: number;
    total_placed: number;
    unplaced_students: number;
    placement_rate_percentage: number;
    total_companies: number;
    average_ctc_lpa: number;
    highest_ctc_lpa: number;
}

interface DeptItem {
    department: string;
    total_students: number;
    placed_students: number;
    unplaced_students: number;
    placement_rate_percentage: number;
    average_ctc_lpa: number;
}

interface CompanyStat {
    company_id: number;
    company_name: string;
    registered_candidates: number;
    placed_candidates: number;
    max_ctc_lpa: number;
}

interface RoundStat {
    stage_name: string;
    total_participants: number;
    qualified_count: number;
    drop_off_count: number;
}

const COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899"];

const AnalyticsPage: React.FC = () => {
    const [overview, setOverview] = useState<OverviewData | null>(null);
    const [depts, setDepts] = useState<DeptItem[]>([]);
    const [companies, setCompanies] = useState<CompanyStat[]>([]);
    const [rounds, setRounds] = useState<RoundStat[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const [ovRes, deptRes, compRes, roundRes] = await Promise.all([
                    api.get<OverviewData>("/admin/analytics/overview"),
                    api.get<{ departments: DeptItem[] }>("/admin/analytics/departments"),
                    api.get<{ companies: CompanyStat[] }>("/admin/analytics/companies"),
                    api.get<{ rounds: RoundStat[] }>("/admin/analytics/rounds"),
                ]);
                setOverview(ovRes.data);
                setDepts(deptRes.data.departments);
                setCompanies(compRes.data.companies);
                setRounds(roundRes.data.rounds);
            } catch (err) {
                console.error("Failed to load analytics data", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchAnalytics();
    }, []);

    if (isLoading) return <LoadingSpinner message="Generating analytics dashboards..." />;

    const pieData = overview
        ? [
            { name: "Placed", value: overview.total_placed },
            { name: "Unplaced", value: overview.unplaced_students },
        ]
        : [];

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">Placement Analytics</h1>
                <p className="text-sm text-slate-400 mt-0.5">Comprehensive metrics, department performance, and company insights</p>
            </div>

            {/* KPI Row */}
            {overview && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                        { label: "Placement Rate", value: `${overview.placement_rate_percentage}%`, color: "text-emerald-400" },
                        { label: "Total Placed", value: overview.total_placed, color: "text-indigo-400" },
                        { label: "Avg Package", value: `${overview.average_ctc_lpa} LPA`, color: "text-cyan-400" },
                        { label: "Highest Package", value: `${overview.highest_ctc_lpa} LPA`, color: "text-amber-400" },
                    ].map((item) => (
                        <div key={item.label} className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 text-center">
                            <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
                            <p className="text-xs text-slate-400 mt-1">{item.label}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Grid 1: Pie + Dept Bar */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Placement Ratio Pie Chart */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5">
                    <div className="flex items-center space-x-2 mb-4">
                        <PieIcon className="w-5 h-5 text-indigo-400" />
                        <h2 className="text-sm font-semibold text-white">Overall Placement Status</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={240}>
                        <PieChart>
                            <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={85} paddingAngle={5} dataKey="value">
                                <Cell fill="#10b981" />
                                <Cell fill="#334155" />
                            </Pie>
                            <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#fff" }} />
                            <Legend verticalAlign="bottom" height={36} iconType="circle" />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Department Breakdown Chart */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 lg:col-span-2">
                    <div className="flex items-center space-x-2 mb-4">
                        <BarChart3 className="w-5 h-5 text-indigo-400" />
                        <h2 className="text-sm font-semibold text-white">Department Placement Breakdown</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={240}>
                        <BarChart data={depts}>
                            <XAxis dataKey="department" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                            <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#fff" }} />
                            <Bar dataKey="placed_students" name="Placed" fill="#6366f1" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="unplaced_students" name="Unplaced" fill="#334155" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Grid 2: Companies CTC & Round Funnel */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Company Placement Comparison */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5">
                    <div className="flex items-center space-x-2 mb-4">
                        <Building2 className="w-5 h-5 text-indigo-400" />
                        <h2 className="text-sm font-semibold text-white">Company CTC (LPA) Comparison</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={companies}>
                            <XAxis dataKey="company_name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                            <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#fff" }} />
                            <Bar dataKey="max_ctc_lpa" name="Max CTC (LPA)" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Round Drop-off Funnel */}
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5">
                    <div className="flex items-center space-x-2 mb-4">
                        <Layers className="w-5 h-5 text-indigo-400" />
                        <h2 className="text-sm font-semibold text-white">Round Progression & Drop-off</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={rounds}>
                            <XAxis dataKey="stage_name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                            <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
                            <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#fff" }} />
                            <Bar dataKey="qualified_count" name="Qualified" fill="#818cf8" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="drop_off_count" name="Dropped Off" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsPage;
