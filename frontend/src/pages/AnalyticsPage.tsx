import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { StatusBadge } from "../components/StatusBadge";
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from "recharts";
import {
    Users, Building2, Target, Award, Search, BarChart3,
    PieChart as PieIcon, Layers, FileText, CheckCircle2, UserCheck
} from "lucide-react";

interface OverviewData {
    academic_year: string;
    total_students: number;
    total_companies: number;
    total_drives: number;
    total_registrations: number;
    total_placement_records: number;
    students_placed: number;
    students_in_process: number;
    students_not_placed: number;
    placement_rate_percentage: number;
    average_ctc_lpa: number;
    highest_ctc_lpa: number;
}

interface DeptItem {
    department: string;
    total_students: number;
    placed_students: number;
    in_process_students: number;
    not_placed_students: number;
    placement_rate_percentage: number;
    average_ctc_lpa: number;
}

interface CompanyStat {
    company_id: number;
    company_name: string;
    industry: string;
    registered_students: number;
    unplaced_counts?: number;
    progression_counts?: number;
    placed_students: number;
    max_ctc_lpa: number;
}

interface RoundStat {
    stage_name: string;
    total_participants: number;
    qualified_count: number;
    drop_off_count: number;
}

interface StudentAnalytics {
    register_number: string;
    full_name: string;
    department: string;
    cgpa: number;
    overall_status: string;
    registered_companies: number;
    unplaced_companies?: number;
    progression_companies?: number;
    placed_companies: number;
    company_breakdown: Array<{
        drive_id: number;
        company_name: string;
        highest_round_reached: number;
        status: string;
    }>;
}

const AnalyticsPage: React.FC = () => {
    const [overview, setOverview] = useState<OverviewData | null>(null);
    const [depts, setDepts] = useState<DeptItem[]>([]);
    const [companies, setCompanies] = useState<CompanyStat[]>([]);
    const [rounds, setRounds] = useState<RoundStat[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    // Student Search state
    const [studentRegisterNo, setStudentRegisterNo] = useState("");
    const [studentData, setStudentData] = useState<StudentAnalytics | null>(null);
    const [isSearchingStudent, setIsSearchingStudent] = useState(false);
    const [studentSearchError, setStudentSearchError] = useState("");

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
                console.error("Failed to load analytics", err);
            } finally {
                setIsLoading(false);
            }
        };
        fetchAnalytics();
    }, []);

    const handleStudentSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!studentRegisterNo.trim()) return;

        setIsSearchingStudent(true);
        setStudentSearchError("");
        setStudentData(null);

        try {
            const res = await api.get<StudentAnalytics>(`/admin/analytics/student/${studentRegisterNo.trim()}`);
            setStudentData(res.data);
        } catch (err: any) {
            setStudentSearchError(err.response?.data?.detail || "Student analytics not found.");
        } finally {
            setIsSearchingStudent(false);
        }
    };

    if (isLoading) return <LoadingSpinner message="Querying PostgreSQL analytics engine..." />;

    const pieData = overview
        ? [
            { name: "Placed", value: overview.students_placed },
            { name: "Not Placed", value: overview.students_not_placed },
        ]
        : [];

    const PIE_COLORS = ["#10b981", "#f43f5e"];

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Placement Analytics & Metrics</h1>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
                    Deterministic SQL aggregations across students, companies, departments, and rounds
                </p>
            </div>

            {/* OVERALL COLLEGE METRICS KPI GRID */}
            {overview && (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                    <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-4">
                        <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">Total Students</p>
                        <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{overview.total_students}</p>
                    </div>
                    <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-4">
                        <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">Total Companies</p>
                        <p className="text-2xl font-bold text-violet-600 dark:text-violet-400 mt-1">{overview.total_companies}</p>
                    </div>
                    <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-4">
                        <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">Total Registrations</p>
                        <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">{overview.total_registrations}</p>
                    </div>
                    <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-4">
                        <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">Students Placed</p>
                        <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{overview.students_placed}</p>
                    </div>
                    <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-4">
                        <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">Students Not Placed</p>
                        <p className="text-2xl font-bold text-rose-600 dark:text-rose-400 mt-1">{overview.students_not_placed}</p>
                    </div>
                    <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-4">
                        <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">Placement Records</p>
                        <p className="text-2xl font-bold text-cyan-600 dark:text-cyan-400 mt-1">{overview.total_placement_records}</p>
                    </div>
                    <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-4">
                        <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">Placement Rate</p>
                        <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-300 mt-1">{overview.placement_rate_percentage}%</p>
                    </div>
                </div>
            )}

            {/* DEPARTMENT ANALYTICS */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Status Ratio Pie */}
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-5">
                    <div className="flex items-center space-x-2 mb-4">
                        <PieIcon className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                        <h2 className="text-sm font-semibold text-slate-900 dark:text-white">College Placement Status Breakdown</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={240}>
                        <PieChart>
                            <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={85} paddingAngle={5} dataKey="value">
                                {pieData.map((_, idx) => (
                                    <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "10px", color: "#f8fafc", padding: "10px 14px" }}
                                itemStyle={{ color: "#f8fafc", fontWeight: 500 }}
                                labelStyle={{ color: "#ffffff", fontWeight: 700, marginBottom: "4px" }}
                            />
                            <Legend verticalAlign="bottom" height={36} iconType="circle" />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Department Stacked Bar Chart */}
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 lg:col-span-2">
                    <div className="flex items-center space-x-2 mb-4">
                        <BarChart3 className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                        <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Department Placement & Progression Analytics</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={240}>
                        <BarChart data={depts}>
                            <XAxis dataKey="department" tick={{ fill: "#64748b", fontSize: 11 }} />
                            <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "10px", color: "#f8fafc", padding: "10px 14px" }}
                                itemStyle={{ color: "#f8fafc", fontWeight: 500 }}
                                labelStyle={{ color: "#ffffff", fontWeight: 700, marginBottom: "4px" }}
                            />
                            <Bar dataKey="placed_students" name="Placed" fill="#10b981" stackId="a" radius={[0, 0, 0, 0]} />
                            <Bar dataKey="not_placed_students" name="Not Placed" fill="#64748b" stackId="a" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* COMPANY ANALYTICS & ROUND FUNNELS */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Company Candidate Participation */}
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-5">
                    <div className="flex items-center space-x-2 mb-4">
                        <Building2 className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                        <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Company Candidate Participation</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={companies}>
                            <XAxis dataKey="company_name" tick={{ fill: "#64748b", fontSize: 11 }} />
                            <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "10px", color: "#f8fafc", padding: "10px 14px" }}
                                itemStyle={{ color: "#f8fafc", fontWeight: 500 }}
                                labelStyle={{ color: "#ffffff", fontWeight: 700, marginBottom: "4px" }}
                            />
                            <Bar dataKey="registered_students" name="Registered" fill="#6366f1" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="unplaced_counts" name="Not Placed" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="placed_students" name="Placed" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Round Progression & Drop-off */}
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-5">
                    <div className="flex items-center space-x-2 mb-4">
                        <Layers className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                        <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Round Funnel Drop-off</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={rounds}>
                            <XAxis dataKey="stage_name" tick={{ fill: "#64748b", fontSize: 11 }} />
                            <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "10px", color: "#f8fafc", padding: "10px 14px" }}
                                itemStyle={{ color: "#f8fafc", fontWeight: 500 }}
                                labelStyle={{ color: "#ffffff", fontWeight: 700, marginBottom: "4px" }}
                            />
                            <Bar dataKey="qualified_count" name="Qualified" fill="#818cf8" radius={[4, 4, 0, 0]} />
                            <Bar dataKey="drop_off_count" name="Drop-off" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* STUDENT ANALYTICS LIVE LOOKUP */}
            <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center space-x-3">
                    <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
                        <UserCheck className="w-5 h-5 text-indigo-500 dark:text-indigo-400" />
                    </div>
                    <div>
                        <h2 className="text-base font-semibold text-slate-900 dark:text-white">Student Analytics Lookup</h2>
                        <p className="text-xs text-slate-600 dark:text-slate-400">
                            Query registered companies, progression companies, placed companies, and highest round reached
                        </p>
                    </div>
                </div>

                <form onSubmit={handleStudentSearch} className="flex gap-3 max-w-md">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500" />
                        <input
                            type="text"
                            value={studentRegisterNo}
                            onChange={(e) => setStudentRegisterNo(e.target.value)}
                            placeholder="Enter Register Number (e.g. 7376221CS101)"
                            className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 focus:border-indigo-500 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-slate-500 outline-none"
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={isSearchingStudent || !studentRegisterNo.trim()}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-semibold transition-colors disabled:opacity-40"
                    >
                        {isSearchingStudent ? "Searching..." : "Analyze"}
                    </button>
                </form>

                {studentSearchError && (
                    <p className="text-xs text-rose-400">{studentSearchError}</p>
                )}

                {studentData && (
                    <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-800">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 dark:text-white">{studentData.full_name}</h3>
                                <p className="text-xs text-slate-600 dark:text-slate-400">{studentData.register_number} · {studentData.department} (CGPA: {studentData.cgpa})</p>
                            </div>
                            <StatusBadge status={studentData.overall_status} />
                        </div>

                        <div className="grid grid-cols-3 gap-3">
                            <div className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-3 text-center border border-slate-200 dark:border-slate-700/50">
                                <p className="text-xl font-bold text-indigo-600 dark:text-indigo-400">{studentData.registered_companies}</p>
                                <p className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-semibold">Registered Companies</p>
                            </div>
                            <div className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-3 text-center border border-slate-200 dark:border-slate-700/50">
                                <p className="text-xl font-bold text-rose-600 dark:text-rose-400">{studentData.unplaced_companies ?? studentData.progression_companies}</p>
                                <p className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-semibold">Unplaced Drives</p>
                            </div>
                            <div className="bg-slate-50 dark:bg-slate-800/60 rounded-xl p-3 text-center border border-slate-200 dark:border-slate-700/50">
                                <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400">{studentData.placed_companies}</p>
                                <p className="text-[10px] text-slate-600 dark:text-slate-400 uppercase font-semibold">Placed Companies</p>
                            </div>
                        </div>

                        {studentData.company_breakdown.length > 0 && (
                            <div className="overflow-x-auto">
                                <table className="w-full text-xs">
                                    <thead className="bg-slate-100 dark:bg-slate-800/50">
                                        <tr>
                                            <th className="text-left px-3 py-2 text-slate-700 dark:text-slate-300 font-semibold uppercase">Company</th>
                                            <th className="text-center px-3 py-2 text-slate-700 dark:text-slate-300 font-semibold uppercase">Highest Round Reached</th>
                                            <th className="text-left px-3 py-2 text-slate-700 dark:text-slate-300 font-semibold uppercase">Status</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-200 dark:divide-slate-800/50">
                                        {studentData.company_breakdown.map((cb, idx) => (
                                            <tr key={idx}>
                                                <td className="px-3 py-2 text-slate-900 dark:text-white font-medium">{cb.company_name}</td>
                                                <td className="px-3 py-2 text-center text-cyan-600 dark:text-cyan-400 font-mono font-semibold">Round {cb.highest_round_reached}</td>
                                                <td className="px-3 py-2"><StatusBadge status={cb.status} /></td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AnalyticsPage;
