import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { StatusBadge } from "../components/StatusBadge";
import { ArrowLeft, Building2, Users, Award, UserX, ExternalLink } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface DriveData {
    id: number;
    drive_name: string;
    academic_year: string;
    job_role: string;
    ctc_lpa: number;
    status: string;
    registered_count: number;
    placed_count: number;
}

interface CompanyDetail {
    id: number;
    name: string;
    industry: string;
    website: string;
    contact_email: string;
    drives: DriveData[];
}

interface StageBreakdown {
    stage_name: string;
    stage_order: number;
    qualified_count: number;
}

interface CompanyStats {
    company_name: string;
    total_drives: number;
    registered_candidates: number;
    placed_candidates: number;
    selection_rate_percentage: number;
    stages_breakdown: StageBreakdown[];
}

interface StudentRow {
    student_id: number;
    register_number: string;
    full_name: string;
    department: string;
    drive_name: string;
    is_placed: boolean;
    package_ctc: number | null;
}

const FUNNEL_COLORS = ["#818cf8", "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#312e81", "#22d3ee", "#10b981"];

const CompanyDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [company, setCompany] = useState<CompanyDetail | null>(null);
    const [stats, setStats] = useState<CompanyStats | null>(null);
    const [students, setStudents] = useState<StudentRow[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchAll = async () => {
            try {
                const [detailRes, statsRes, studentsRes] = await Promise.all([
                    api.get<CompanyDetail>(`/admin/companies/${id}`),
                    api.get<CompanyStats>(`/admin/companies/${id}/statistics`),
                    api.get<{ items: StudentRow[] }>(`/admin/companies/${id}/students`, { params: { limit: 50 } }),
                ]);
                setCompany(detailRes.data);
                setStats(statsRes.data);
                setStudents(studentsRes.data.items);
            } catch (err: any) {
                setError(err.response?.data?.detail || "Company not found.");
            } finally {
                setIsLoading(false);
            }
        };
        fetchAll();
    }, [id]);

    if (isLoading) return <LoadingSpinner message="Loading company profile..." />;
    if (error) return <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-6 text-rose-300 text-sm">{error}</div>;
    if (!company || !stats) return null;

    const funnelData = stats.stages_breakdown.map((s) => ({
        name: s.stage_name,
        qualified: s.qualified_count,
    }));

    return (
        <div className="max-w-5xl mx-auto space-y-6">
            <button onClick={() => navigate(-1)} className="flex items-center space-x-1 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                <ArrowLeft className="w-4 h-4" /><span>Back to Companies</span>
            </button>

            {/* Company Header */}
            <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-6">
                <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-violet-600 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
                        <Building2 className="w-7 h-7 text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-slate-900 dark:text-white">{company.name}</h1>
                        <p className="text-xs text-slate-600 dark:text-slate-400">{company.industry || "Industry not specified"}</p>
                    </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5">
                    {[
                        { label: "Website", value: company.website || "—" },
                        { label: "Contact", value: company.contact_email || "—" },
                        { label: "Total Drives", value: stats.total_drives },
                        { label: "Selection Rate", value: `${stats.selection_rate_percentage}%` },
                    ].map((item) => (
                        <div key={item.label}>
                            <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">{item.label}</p>
                            <p className="text-sm font-medium text-slate-900 dark:text-white mt-0.5 truncate">{item.value}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-3 gap-4">
                {[
                    { label: "Registered", value: stats.registered_candidates, icon: Users, color: "text-indigo-600 dark:text-indigo-400" },
                    { label: "Not Placed", value: Math.max(0, stats.registered_candidates - stats.placed_candidates), icon: UserX, color: "text-rose-600 dark:text-rose-400" },
                    { label: "Placed", value: stats.placed_candidates, icon: Award, color: "text-emerald-600 dark:text-emerald-400" },
                ].map((kpi) => (
                    <div key={kpi.label} className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-center">
                        <kpi.icon className={`w-5 h-5 ${kpi.color} mx-auto mb-1`} />
                        <p className={`text-2xl font-bold ${kpi.color}`}>{kpi.value}</p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 font-medium mt-0.5">{kpi.label}</p>
                    </div>
                ))}
            </div>

            {/* Round-wise Funnel Chart */}
            {funnelData.length > 0 && (
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-6">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">Round-wise Selection Funnel</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={funnelData} layout="vertical" margin={{ left: 20 }}>
                            <XAxis type="number" tick={{ fill: "#64748b", fontSize: 11 }} />
                            <YAxis type="category" dataKey="name" tick={{ fill: "#64748b", fontSize: 12 }} width={120} />
                            <Tooltip
                                contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "10px", color: "#f8fafc", padding: "10px 14px", fontSize: "12px" }}
                                itemStyle={{ color: "#f8fafc", fontWeight: 500 }}
                                labelStyle={{ color: "#ffffff", fontWeight: 700, marginBottom: "4px" }}
                            />
                            <Bar dataKey="qualified" radius={[0, 6, 6, 0]}>
                                {funnelData.map((_, idx) => (
                                    <Cell key={idx} fill={FUNNEL_COLORS[idx % FUNNEL_COLORS.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* Student List */}
            <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-200 dark:border-slate-800">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Candidate List ({students.length})</h3>
                </div>
                {students.length === 0 ? (
                    <div className="p-6 text-center text-sm text-slate-600 dark:text-slate-400">No candidates found.</div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-100 dark:bg-slate-800/50">
                                <tr>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Register No.</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Name</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Department</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Drive</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Status</th>
                                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">CTC</th>
                                    <th className="text-center px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">View</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-200 dark:divide-slate-800/50">
                                {students.map((s, i) => (
                                    <tr key={i} className="hover:bg-slate-100 dark:bg-slate-800/30 transition-colors">
                                        <td className="px-4 py-2.5 text-indigo-400 font-mono text-xs">{s.register_number}</td>
                                        <td className="px-4 py-2.5 text-slate-900 dark:text-white font-medium">{s.full_name}</td>
                                        <td className="px-4 py-2.5 text-slate-700 dark:text-slate-300">{s.department}</td>
                                        <td className="px-4 py-2.5 text-slate-700 dark:text-slate-300 text-xs">{s.drive_name}</td>
                                        <td className="px-4 py-2.5"><StatusBadge status={s.is_placed ? "PLACED" : "REGISTERED"} /></td>
                                        <td className="px-4 py-2.5 text-right text-emerald-400">{s.package_ctc ? `${s.package_ctc} LPA` : "—"}</td>
                                        <td className="px-4 py-2.5 text-center">
                                            <Link to={`/students/${s.register_number}`} className="text-indigo-400 hover:text-indigo-300"><ExternalLink className="w-4 h-4" /></Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CompanyDetailPage;
