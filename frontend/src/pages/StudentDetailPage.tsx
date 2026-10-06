import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { StatusBadge } from "../components/StatusBadge";
import { ArrowLeft, User, GraduationCap, Building2, Trophy } from "lucide-react";

interface DriveHistory {
    drive_id: number;
    drive_name: string;
    company_id: number;
    company_name: string;
    academic_year: string;
    stage_results: Array<{ stage_name: string; stage_order: number; status: string }>;
    placement: { status: string; package_ctc: number | null } | null;
}

interface StudentDetail {
    id: number;
    register_number: string;
    full_name: string;
    department: string;
    email: string;
    mobile_number: string;
    gender: string;
    accommodation_type: string;
    cgpa: number;
    academic_year: string;
    is_placed: boolean;
    drives_history: DriveHistory[];
}

const StudentDetailPage: React.FC = () => {
    const { registerNumber } = useParams<{ registerNumber: string }>();
    const navigate = useNavigate();
    const [student, setStudent] = useState<StudentDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetch = async () => {
            try {
                const res = await api.get<StudentDetail>(`/admin/students/${registerNumber}`);
                setStudent(res.data);
            } catch (err: any) {
                setError(err.response?.data?.detail || "Student not found.");
            } finally {
                setIsLoading(false);
            }
        };
        fetch();
    }, [registerNumber]);

    if (isLoading) return <LoadingSpinner message="Loading student profile..." />;
    if (error) return <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-6 text-rose-300 text-sm">{error}</div>;
    if (!student) return null;

    const registeredCompanies = student.drives_history.length;
    const unplacedCompanies = student.drives_history.filter(d => !d.placement).length;
    const placedCompanies = student.drives_history.filter(d => d.placement !== null).length;

    const highestRound = student.drives_history.reduce((max, d) => {
        const qualifiedStages = d.stage_results.filter(s => s.status === "QUALIFIED");
        const maxOrder = qualifiedStages.length > 0 ? Math.max(...qualifiedStages.map(s => s.stage_order)) : 0;
        return Math.max(max, maxOrder);
    }, 0);

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <button onClick={() => navigate(-1)} className="flex items-center space-x-1 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
                <ArrowLeft className="w-4 h-4" /><span>Back to Students</span>
            </button>

            {/* Profile Card */}
            <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-6">
                <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-4">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                            <User className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-slate-900 dark:text-white">{student.full_name}</h1>
                            <p className="text-xs font-mono text-indigo-600 dark:text-indigo-400 font-semibold mt-0.5">{student.register_number}</p>
                        </div>
                    </div>
                    <StatusBadge status={student.is_placed ? "PLACED" : "UNPLACED"} />
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                    {[
                        { label: "Department", value: student.department, icon: GraduationCap },
                        { label: "CGPA", value: student.cgpa ?? "—", icon: Trophy },
                        { label: "Email", value: student.email || "—" },
                        { label: "Mobile", value: student.mobile_number || "—" },
                        { label: "Gender", value: student.gender || "—" },
                        { label: "Accommodation", value: student.accommodation_type || "—" },
                        { label: "Academic Year", value: student.academic_year || "—" },
                    ].map((item) => (
                        <div key={item.label}>
                            <p className="text-xs text-slate-600 dark:text-slate-400 uppercase tracking-wider font-semibold">{item.label}</p>
                            <p className="text-sm font-medium text-slate-900 dark:text-white mt-0.5 truncate">{item.value}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* KPI Mini Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                    { label: "Registered Companies", value: registeredCompanies, color: "text-indigo-600 dark:text-indigo-400" },
                    { label: "Unplaced Drives", value: unplacedCompanies, color: "text-rose-600 dark:text-rose-400" },
                    { label: "Placed Companies", value: placedCompanies, color: "text-emerald-600 dark:text-emerald-400" },
                    { label: "Highest Round", value: highestRound, color: "text-cyan-600 dark:text-cyan-400" },
                ].map((kpi) => (
                    <div key={kpi.label} className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl p-4 text-center">
                        <p className={`text-2xl font-bold ${kpi.color}`}>{kpi.value}</p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 font-medium mt-1">{kpi.label}</p>
                    </div>
                ))}
            </div>

            {/* Company-wise Drives */}
            <div className="space-y-4">
                <h2 className="text-base font-semibold text-slate-900 dark:text-white flex items-center space-x-2">
                    <Building2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    <span>Company-wise Status</span>
                </h2>

                {student.drives_history.length === 0 ? (
                    <p className="text-sm text-slate-600 dark:text-slate-400">No drive registrations found.</p>
                ) : (
                    student.drives_history.map((drive) => (
                        <div key={drive.drive_id} className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-xl p-5">
                            <div className="flex items-center justify-between mb-3">
                                <div>
                                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{drive.company_name}</h3>
                                    <p className="text-xs text-slate-600 dark:text-slate-400">{drive.drive_name} · {drive.academic_year}</p>
                                </div>
                                {drive.placement ? (
                                    <StatusBadge status={drive.placement.status} />
                                ) : (
                                    <StatusBadge status="REGISTERED" />
                                )}
                            </div>

                            {/* Stage Results Timeline */}
                            {drive.stage_results.length > 0 && (
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {drive.stage_results.map((sr, i) => (
                                        <div key={i} className="flex items-center space-x-1.5 bg-slate-50 dark:bg-slate-800/60 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700/40">
                                            <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">R{sr.stage_order}:</span>
                                            <span className="text-xs font-medium text-slate-800 dark:text-slate-200">{sr.stage_name}</span>
                                            <StatusBadge status={sr.status} className="text-[10px] px-1.5 py-0" />
                                        </div>
                                    ))}
                                </div>
                            )}

                            {drive.placement?.package_ctc && (
                                <p className="text-xs text-emerald-400 mt-2">
                                    Package: <span className="font-semibold">{drive.placement.package_ctc} LPA</span>
                                </p>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default StudentDetailPage;
