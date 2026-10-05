import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { EmptyState } from "../components/EmptyState";
import { StatusBadge } from "../components/StatusBadge";
import { Search, Users, ChevronLeft, ChevronRight, ExternalLink } from "lucide-react";

interface StudentItem {
    id: number;
    register_number: string;
    full_name: string;
    department: string;
    cgpa: number;
    is_placed: boolean;
    placement_count: number;
    placements: Array<{ company_name: string; status: string; package_ctc: number | null }>;
}

const StudentsPage: React.FC = () => {
    const [students, setStudents] = useState<StudentItem[]>([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [pages, setPages] = useState(1);
    const [search, setSearch] = useState("");
    const [department, setDepartment] = useState("");
    const [placedFilter, setPlacedFilter] = useState("");
    const [sortBy, setSortBy] = useState("register_number");
    const [order, setOrder] = useState("asc");
    const [isLoading, setIsLoading] = useState(true);

    const fetchStudents = async (requestedPage = page) => {
        setIsLoading(true);
        try {
            const params: any = { page: requestedPage, limit: 15, sort_by: sortBy, order };
            if (search) params.search = search;
            if (department) params.department = department;
            if (placedFilter) params.status = placedFilter;

            const res = await api.get("/admin/students", { params });
            setStudents(res.data.items);
            setTotal(res.data.total);
            setPage(res.data.page);
            setPages(res.data.pages);
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => { fetchStudents(); }, [page, sortBy, order]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (page === 1) fetchStudents(1);
        else setPage(1);
    };

    const handleApplyFilters = () => {
        if (page === 1) fetchStudents(1);
        else setPage(1);
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Students</h1>
                <p className="text-sm text-slate-400 dark:text-slate-500 dark:text-slate-400 mt-0.5">{total} student records</p>
            </div>

            {/* Filters Row */}
            <div className="flex flex-wrap gap-3 items-end">
                <form onSubmit={handleSearch} className="relative flex-1 min-w-[200px] max-w-sm">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search register no. or name…"
                        className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 focus:border-indigo-500 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-500 outline-none"
                    />
                </form>

                <select value={department} onChange={(e) => setDepartment(e.target.value)} className="px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-700 dark:text-slate-300 outline-none">
                    <option value="">All Departments</option>
                    <option value="CSE">CSE</option>
                    <option value="ECE">ECE</option>
                    <option value="EEE">EEE</option>
                    <option value="MECH">MECH</option>
                    <option value="IT">IT</option>
                    <option value="CIVIL">CIVIL</option>
                    <option value="AIDS">AIDS</option>
                    <option value="AIML">AIML</option>
                </select>

                <select value={placedFilter} onChange={(e) => setPlacedFilter(e.target.value)} className="px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-700 dark:text-slate-300 outline-none">
                    <option value="">All Status</option>
                    <option value="PLACED">Placed</option>
                    <option value="UNPLACED">Unplaced</option>
                </select>

                <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-700 dark:text-slate-300 outline-none">
                    <option value="register_number">Register No.</option>
                    <option value="full_name">Name</option>
                    <option value="cgpa">CGPA</option>
                    <option value="department">Department</option>
                </select>

                <button onClick={() => setOrder(order === "asc" ? "desc" : "asc")} className="px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
                    {order === "asc" ? "↑ Asc" : "↓ Desc"}
                </button>

                <button onClick={handleApplyFilters} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-slate-900 dark:text-white rounded-xl text-sm font-medium transition-colors">
                    Apply
                </button>
            </div>

            {isLoading ? (
                <LoadingSpinner />
            ) : students.length === 0 ? (
                <EmptyState title="No students found" description="Adjust your search or filters." icon={<Users className="w-8 h-8 text-indigo-400" />} />
            ) : (
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-100 dark:bg-slate-800/50">
                                <tr>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 dark:text-slate-500 dark:text-slate-400 uppercase">Register No.</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 dark:text-slate-500 dark:text-slate-400 uppercase">Name</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 dark:text-slate-500 dark:text-slate-400 uppercase">Department</th>
                                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-400 dark:text-slate-500 dark:text-slate-400 uppercase">CGPA</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 dark:text-slate-500 dark:text-slate-400 uppercase">Status</th>
                                    <th className="text-center px-4 py-3 text-xs font-semibold text-slate-400 dark:text-slate-500 dark:text-slate-400 uppercase">Placements</th>
                                    <th className="text-center px-4 py-3 text-xs font-semibold text-slate-400 dark:text-slate-500 dark:text-slate-400 uppercase">View</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-200 dark:divide-slate-800/50">
                                {students.map((s) => (
                                    <tr key={s.id} className="hover:bg-slate-100 dark:bg-slate-800/30 transition-colors">
                                        <td className="px-4 py-3 text-indigo-400 font-mono text-xs">{s.register_number}</td>
                                        <td className="px-4 py-3 text-slate-900 dark:text-white font-medium">{s.full_name}</td>
                                        <td className="px-4 py-3 text-slate-700 dark:text-slate-300">{s.department}</td>
                                        <td className="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{s.cgpa ?? "—"}</td>
                                        <td className="px-4 py-3"><StatusBadge status={s.is_placed ? "PLACED" : "UNPLACED"} /></td>
                                        <td className="px-4 py-3 text-center text-slate-700 dark:text-slate-300">{s.placement_count}</td>
                                        <td className="px-4 py-3 text-center">
                                            <Link to={`/students/${s.register_number}`} className="inline-flex items-center text-indigo-400 hover:text-indigo-300 transition-colors">
                                                <ExternalLink className="w-4 h-4" />
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800">
                        <p className="text-xs text-slate-400 dark:text-slate-500">Page {page} of {pages} · {total} records</p>
                        <div className="flex space-x-2">
                            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1} className="p-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg disabled:opacity-30"><ChevronLeft className="w-4 h-4 text-slate-700 dark:text-slate-300" /></button>
                            <button onClick={() => setPage(Math.min(pages, page + 1))} disabled={page >= pages} className="p-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg disabled:opacity-30"><ChevronRight className="w-4 h-4 text-slate-700 dark:text-slate-300" /></button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default StudentsPage;
