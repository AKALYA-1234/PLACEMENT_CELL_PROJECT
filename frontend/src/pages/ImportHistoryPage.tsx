import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { EmptyState } from "../components/EmptyState";
import { StatusBadge } from "../components/StatusBadge";
import { History, ChevronLeft, ChevronRight, Search } from "lucide-react";

interface ImportItem {
    id: number;
    filename: string;
    company_name: string;
    total_rows: number;
    imported_rows: number;
    failed_rows: number;
    status: string;
    imported_at: string | null;
}

const ImportHistoryPage: React.FC = () => {
    const [imports, setImports] = useState<ImportItem[]>([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [pages, setPages] = useState(1);
    const [search, setSearch] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchImports = async (p: number, q: string) => {
        setIsLoading(true);
        try {
            const res = await api.get("/admin/imports", { params: { page: p, limit: 10, search: q || undefined } });
            setImports(res.data.items);
            setTotal(res.data.total);
            setPages(res.data.pages);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to load import history.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => { fetchImports(page, search); }, [page]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setPage(1);
        fetchImports(1, search);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Import History</h1>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">{total} import records found</p>
                </div>
                <form onSubmit={handleSearch} className="relative max-w-xs w-full">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search by filename…"
                        className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 focus:border-indigo-500 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-slate-500 outline-none"
                    />
                </form>
            </div>

            {error && <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-3 text-sm text-rose-300">{error}</div>}

            {isLoading ? (
                <LoadingSpinner />
            ) : imports.length === 0 ? (
                <EmptyState title="No imports found" description="Upload an Excel workbook to get started." icon={<History className="w-8 h-8 text-indigo-400" />} />
            ) : (
                <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-100 dark:bg-slate-800/50">
                                <tr>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">ID</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Filename</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Company</th>
                                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Total</th>
                                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Imported</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Status</th>
                                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase">Date</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-200 dark:divide-slate-800/50">
                                {imports.map((item) => (
                                    <tr key={item.id} className="hover:bg-slate-100 dark:bg-slate-800/30 transition-colors">
                                        <td className="px-4 py-3 text-slate-500 dark:text-slate-400 font-mono text-xs">#{item.id}</td>
                                        <td className="px-4 py-3 text-slate-900 dark:text-white font-medium">{item.filename}</td>
                                        <td className="px-4 py-3 text-slate-700 dark:text-slate-300">{item.company_name}</td>
                                        <td className="px-4 py-3 text-right text-slate-700 dark:text-slate-300">{item.total_rows}</td>
                                        <td className="px-4 py-3 text-right text-emerald-600 dark:text-emerald-400 font-semibold">{item.imported_rows}</td>
                                        <td className="px-4 py-3"><StatusBadge status={item.status || "UNKNOWN"} /></td>
                                        <td className="px-4 py-3 text-slate-500 dark:text-slate-400 text-xs">{item.imported_at ? new Date(item.imported_at).toLocaleDateString() : "—"}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {/* Pagination */}
                    <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-800">
                        <p className="text-xs text-slate-600 dark:text-slate-400">Page {page} of {pages}</p>
                        <div className="flex space-x-2">
                            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1} className="p-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg disabled:opacity-30 transition-colors"><ChevronLeft className="w-4 h-4 text-slate-700 dark:text-slate-300" /></button>
                            <button onClick={() => setPage(Math.min(pages, page + 1))} disabled={page >= pages} className="p-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg disabled:opacity-30 transition-colors"><ChevronRight className="w-4 h-4 text-slate-700 dark:text-slate-300" /></button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ImportHistoryPage;
