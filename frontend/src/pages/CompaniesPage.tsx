import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { EmptyState } from "../components/EmptyState";
import { Search, Building2, ChevronLeft, ChevronRight, ExternalLink, SlidersHorizontal } from "lucide-react";

interface CompanyItem {
    id: number;
    name: string;
    industry: string;
    website: string;
    drives_count: number;
    total_registered: number;
    total_placed: number;
}

const CompaniesPage: React.FC = () => {
    const [companies, setCompanies] = useState<CompanyItem[]>([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [pages, setPages] = useState(1);
    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("");
    const [department, setDepartment] = useState("");
    const [roundName, setRoundName] = useState("");
    const [academicYear, setAcademicYear] = useState("");
    const [industry, setIndustry] = useState("");
    const [filterOptions, setFilterOptions] = useState({ departments: [] as string[], rounds: [] as string[], academic_years: [] as string[] });
    const [isLoading, setIsLoading] = useState(true);

    const fetchCompanies = async (p: number, q = search) => {
        setIsLoading(true);
        try {
            const res = await api.get("/admin/companies", {
                params: {
                    page: p,
                    limit: 12,
                    search: q || undefined,
                    status: status || undefined,
                    department: department || undefined,
                    round_name: roundName || undefined,
                    academic_year: academicYear || undefined,
                    industry: industry || undefined,
                },
            });
            setCompanies(res.data.items);
            setTotal(res.data.total);
            setPages(res.data.pages);
            setFilterOptions(res.data.filter_options ?? { departments: [], rounds: [], academic_years: [] });
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => { fetchCompanies(page); }, [page]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (page === 1) fetchCompanies(1);
        else setPage(1);
    };

    const applyFilters = () => {
        if (page === 1) fetchCompanies(1);
        else setPage(1);
    };

    const clearFilters = () => {
        setSearch("");
        setStatus("");
        setDepartment("");
        setRoundName("");
        setAcademicYear("");
        setIndustry("");
        if (page === 1) fetchCompanies(1, "");
        else setPage(1);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Companies</h1>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">{total} companies registered</p>
                </div>
                <form onSubmit={handleSearch} className="relative max-w-xs w-full">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search companies…"
                        className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 focus:border-indigo-500 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-slate-500 outline-none"
                    />
                </form>
            </div>

            <div className="flex flex-wrap items-end gap-3 p-4 bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl">
                <div className="flex items-center gap-2 w-full text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wide">
                    <SlidersHorizontal className="w-4 h-4" /> Filters
                </div>
                <select value={status} onChange={(e) => setStatus(e.target.value)} className="px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-800 dark:text-slate-200 outline-none">
                    <option value="">All participation</option>
                    <option value="REGISTERED">Registered</option>
                    <option value="PLACED">Placed</option>
                    <option value="NON_PLACED">Non-placed</option>
                </select>
                <select value={department} onChange={(e) => setDepartment(e.target.value)} className="px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-800 dark:text-slate-200 outline-none">
                    <option value="">All departments</option>
                    {filterOptions.departments.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
                <select value={roundName} onChange={(e) => setRoundName(e.target.value)} className="px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-800 dark:text-slate-200 outline-none">
                    <option value="">All rounds</option>
                    {filterOptions.rounds.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
                <select value={academicYear} onChange={(e) => setAcademicYear(e.target.value)} className="px-3 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-800 dark:text-slate-200 outline-none">
                    <option value="">All academic years</option>
                    {filterOptions.academic_years.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
                <input value={industry} onChange={(e) => setIndustry(e.target.value)} placeholder="Industry" className="px-3 py-2 w-36 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 outline-none" />
                <button onClick={applyFilters} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition-colors">Apply</button>
                <button onClick={clearFilters} className="px-3 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white text-sm">Clear</button>
            </div>

            {isLoading ? (
                <LoadingSpinner />
            ) : companies.length === 0 ? (
                <EmptyState title="No companies found" icon={<Building2 className="w-8 h-8 text-indigo-400" />} />
            ) : (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {companies.map((c) => (
                            <Link
                                key={c.id}
                                to={`/companies/${c.id}`}
                                className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 hover:border-indigo-500/30 rounded-2xl p-5 transition-all group shadow-sm"
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-gradient-to-tr from-violet-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                                            <Building2 className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="text-sm font-semibold text-slate-900 dark:text-white group-hover:text-indigo-500 dark:group-hover:text-indigo-400 transition-colors">{c.name}</h3>
                                            <p className="text-xs text-slate-600 dark:text-slate-400">{c.industry || "—"}</p>
                                        </div>
                                    </div>
                                    <ExternalLink className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 dark:group-hover:text-indigo-400 transition-colors" />
                                </div>

                                <div className="grid grid-cols-3 gap-2 mt-4">
                                    <div className="bg-slate-50 dark:bg-slate-800/60 rounded-lg p-2 text-center">
                                        <p className="text-lg font-bold text-indigo-600 dark:text-indigo-400">{c.drives_count}</p>
                                        <p className="text-[10px] text-slate-600 dark:text-slate-400 font-medium uppercase">Drives</p>
                                    </div>
                                    <div className="bg-slate-50 dark:bg-slate-800/60 rounded-lg p-2 text-center">
                                        <p className="text-lg font-bold text-cyan-600 dark:text-cyan-400">{c.total_registered}</p>
                                        <p className="text-[10px] text-slate-600 dark:text-slate-400 font-medium uppercase">Registered</p>
                                    </div>
                                    <div className="bg-slate-50 dark:bg-slate-800/60 rounded-lg p-2 text-center">
                                        <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">{c.total_placed}</p>
                                        <p className="text-[10px] text-slate-600 dark:text-slate-400 font-medium uppercase">Placed</p>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>

                    <div className="flex items-center justify-between">
                        <p className="text-xs text-slate-600 dark:text-slate-400">Page {page} of {pages}</p>
                        <div className="flex space-x-2">
                            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1} className="p-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg disabled:opacity-30"><ChevronLeft className="w-4 h-4 text-slate-700 dark:text-slate-300" /></button>
                            <button onClick={() => setPage(Math.min(pages, page + 1))} disabled={page >= pages} className="p-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg disabled:opacity-30"><ChevronRight className="w-4 h-4 text-slate-700 dark:text-slate-300" /></button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default CompaniesPage;
