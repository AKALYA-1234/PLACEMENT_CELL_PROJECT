import React, { useState } from "react";
import { useLocation, useNavigate, Navigate, Link } from "react-router-dom";
import { api } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { ConfirmationDialog } from "../components/ConfirmationDialog";
import {
    CheckCircle2, AlertTriangle, FileSpreadsheet,
    ArrowLeft, Database, XCircle, HelpCircle, Layers,
    Users, Award, Target, ArrowRight
} from "lucide-react";

interface SheetDetail {
    sheet_name: string;
    record_count: number;
    category: string;
}

const CATEGORY_OPTIONS = [
    { value: "REGISTERED", label: "Registered Candidates" },
    { value: "ROUND_1", label: "Round 1 (Aptitude / Online Test)" },
    { value: "ROUND_2", label: "Round 2 (Technical Interview)" },
    { value: "ROUND_3", label: "Round 3 (HR / Managerial)" },
    { value: "PLACED", label: "Final Offers / Placed (Normalized)" },
    { value: "IGNORE", label: "Ignore / Do Not Import" },
];

const ImportPreviewPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const state = location.state as any;

    if (!state?.validationData) {
        return <Navigate to="/import/upload" replace />;
    }

    const data = state.validationData;

    // State to manage sheet category overrides (resolving ambiguous sheets)
    const [sheetCategories, setSheetCategories] = useState<Record<string, string>>(() => {
        const initial: Record<string, string> = {};
        if (data.sheets_detail) {
            data.sheets_detail.forEach((s: SheetDetail) => {
                initial[s.sheet_name] = s.category || "REGISTERED";
            });
        }
        return initial;
    });

    const [showConfirmDialog, setShowConfirmDialog] = useState(false);
    const [isImporting, setIsImporting] = useState(false);
    const [importResult, setImportResult] = useState<any>(null);
    const [importError, setImportError] = useState("");

    const handleCategoryChange = (sheetName: string, category: string) => {
        setSheetCategories((prev) => ({ ...prev, [sheetName]: category }));
    };

    const hasUnresolvedAmbiguousSheets = Object.values(sheetCategories).some(
        (cat) => cat === "UNKNOWN" || cat === "AMBIGUOUS"
    );

    const handleConfirmImport = async () => {
        setIsImporting(true);
        setImportError("");

        const formData = new FormData();
        formData.append("file", state.file);
        formData.append("company_name", state.companyName);
        formData.append("academic_year", state.academicYear);
        formData.append("sheet_overrides", JSON.stringify(sheetCategories));

        try {
            const res = await api.post("/admin/import/confirm", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setImportResult(res.data);
            setShowConfirmDialog(false);
        } catch (err: any) {
            setImportError(err.response?.data?.detail || "Import failed. Please try again.");
            setShowConfirmDialog(false);
        } finally {
            setIsImporting(false);
        }
    };

    // SUCCESS SUMMARY VIEW
    if (importResult) {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <div className="bg-slate-900/80 border border-emerald-500/30 rounded-2xl p-8 text-center shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />

                    <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center">
                        <CheckCircle2 className="w-10 h-10 text-emerald-400" />
                    </div>

                    <h2 className="text-2xl font-bold text-white">Import Complete & Database Updated</h2>
                    <p className="text-sm text-slate-300 mt-1 max-w-md mx-auto">
                        Successfully parsed, validated, and normalized placement data for{" "}
                        <span className="text-emerald-400 font-semibold">{importResult.company_name}</span>.
                    </p>

                    <div className="grid grid-cols-3 gap-4 mt-6 max-w-xl mx-auto">
                        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
                            <Users className="w-5 h-5 text-indigo-400 mx-auto mb-1" />
                            <p className="text-2xl font-bold text-indigo-400">{importResult.total_rows ?? data.registered_count}</p>
                            <p className="text-xs text-slate-400 mt-0.5">Total Records</p>
                        </div>
                        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
                            <Target className="w-5 h-5 text-amber-400 mx-auto mb-1" />
                            <p className="text-2xl font-bold text-amber-400">{Math.max(0, (importResult.total_rows ?? data.registered_count) - (importResult.placed_count ?? data.placed_count))}</p>
                            <p className="text-xs text-slate-400 mt-0.5">In Progression</p>
                        </div>
                        <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
                            <Award className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                            <p className="text-2xl font-bold text-emerald-400">{importResult.placed_count ?? data.placed_count}</p>
                            <p className="text-xs text-slate-400 mt-0.5">Placed (Normalized)</p>
                        </div>
                    </div>

                    <div className="flex items-center justify-center space-x-4 mt-8">
                        <Link
                            to="/imports"
                            className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm font-semibold transition-colors"
                        >
                            View Import History
                        </Link>
                        <Link
                            to="/students"
                            className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-xl text-sm font-semibold transition-all shadow-lg shadow-indigo-600/25 flex items-center space-x-1.5"
                        >
                            <span>Explore Students</span>
                            <ArrowRight className="w-4 h-4" />
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    // Calculate progression count safely
    const registeredCount = data.registered_count || 0;
    const placedCount = data.placed_count || 0;
    const progressionCount = Math.max(0, registeredCount - placedCount);

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <button
                        onClick={() => navigate(-1)}
                        className="flex items-center space-x-1 text-sm text-slate-400 hover:text-white mb-2 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        <span>Back to Upload</span>
                    </button>
                    <h1 className="text-2xl font-bold text-white">Workbook Import Preview</h1>
                    <p className="text-sm text-slate-400 mt-0.5">
                        Review sheet classification, candidate progression, and validation logs.
                    </p>
                </div>
                <StatusBadge status={data.is_valid_for_import ? "READY_FOR_IMPORT" : "VALIDATION_WARNINGS"} />
            </div>

            {importError && (
                <div className="flex items-center space-x-2 bg-rose-500/10 border border-rose-500/20 rounded-xl p-4">
                    <XCircle className="w-5 h-5 text-rose-400 shrink-0" />
                    <p className="text-sm text-rose-300">{importError}</p>
                </div>
            )}

            {/* Overview Card */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center space-x-3 mb-4">
                    <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
                        <FileSpreadsheet className="w-6 h-6 text-indigo-400" />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-white">{data.company_name}</h2>
                        <p className="text-xs text-slate-400">File: {data.file_name} · Year: {state.academicYear}</p>
                    </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t border-slate-800">
                    <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Total Sheets</p>
                        <p className="text-lg font-bold text-white mt-0.5">{data.total_sheets}</p>
                    </div>
                    <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Registered</p>
                        <p className="text-lg font-bold text-indigo-400 mt-0.5">{registeredCount}</p>
                    </div>
                    <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Progression</p>
                        <p className="text-lg font-bold text-amber-400 mt-0.5">{progressionCount}</p>
                    </div>
                    <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider">Placed (Normalized)</p>
                        <p className="text-lg font-bold text-emerald-400 mt-0.5">{placedCount}</p>
                    </div>
                </div>
            </div>

            {/* Candidate Status Categorization Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-indigo-500/5 border border-indigo-500/20 rounded-2xl p-4">
                    <div className="flex items-center space-x-2 mb-2">
                        <Users className="w-4 h-4 text-indigo-400" />
                        <h3 className="text-sm font-semibold text-indigo-300">REGISTERED</h3>
                    </div>
                    <p className="text-2xl font-bold text-white">{registeredCount}</p>
                    <p className="text-xs text-slate-400 mt-1">Initial candidate drive registrations</p>
                </div>

                <div className="bg-amber-500/5 border border-amber-500/20 rounded-2xl p-4">
                    <div className="flex items-center space-x-2 mb-2">
                        <Target className="w-4 h-4 text-amber-400" />
                        <h3 className="text-sm font-semibold text-amber-300">PROGRESSION / NEXT ROUND</h3>
                    </div>
                    <p className="text-2xl font-bold text-white">{progressionCount}</p>
                    <p className="text-xs text-slate-400 mt-1">Cleared intermediate evaluation rounds</p>
                </div>

                <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-2xl p-4">
                    <div className="flex items-center space-x-2 mb-2">
                        <Award className="w-4 h-4 text-emerald-400" />
                        <h3 className="text-sm font-semibold text-emerald-300">PLACED</h3>
                    </div>
                    <p className="text-2xl font-bold text-white">{placedCount}</p>
                    <p className="text-xs text-slate-400 mt-1">
                        Confirmed placement offers (strictly normalized from OFFERED/ACCEPTED)
                    </p>
                </div>
            </div>

            {/* Detected Sheets & Admin Resolution Dropdown */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <Layers className="w-4 h-4 text-indigo-400" />
                        <h3 className="text-sm font-semibold text-white">Workbook Sheets & Category Classification</h3>
                    </div>
                    {hasUnresolvedAmbiguousSheets && (
                        <span className="text-xs text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/20 flex items-center space-x-1">
                            <AlertTriangle className="w-3 h-3" />
                            <span>Resolve ambiguous sheets below</span>
                        </span>
                    )}
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-slate-800/50">
                            <tr>
                                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase">Sheet Name</th>
                                <th className="text-right px-4 py-3 text-xs font-semibold text-slate-400 uppercase">Records</th>
                                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase">Detected Classification</th>
                                <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase">Admin Action / Category</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/50">
                            {data.sheets_detail?.map((sheet: SheetDetail, i: number) => {
                                const currentCategory = sheetCategories[sheet.sheet_name] || "REGISTERED";
                                const isAmbiguous = currentCategory === "UNKNOWN" || currentCategory === "AMBIGUOUS";

                                return (
                                    <tr key={i} className={`transition-colors ${isAmbiguous ? "bg-amber-500/5" : "hover:bg-slate-800/30"}`}>
                                        <td className="px-4 py-3 font-medium text-white flex items-center space-x-2">
                                            <span>{sheet.sheet_name}</span>
                                            {isAmbiguous && (
                                                <span className="text-[10px] text-amber-400 bg-amber-500/20 px-1.5 py-0.5 rounded font-mono">
                                                    AMBIGUOUS
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 text-right text-slate-300 font-mono">{sheet.record_count}</td>
                                        <td className="px-4 py-3">
                                            <StatusBadge status={sheet.category || "REGISTERED"} />
                                        </td>
                                        <td className="px-4 py-3">
                                            <select
                                                value={currentCategory}
                                                onChange={(e) => handleCategoryChange(sheet.sheet_name, e.target.value)}
                                                className={`px-3 py-1.5 rounded-lg text-xs font-medium outline-none transition-all ${isAmbiguous
                                                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                                                        : "bg-slate-800 text-slate-200 border border-slate-700 focus:border-indigo-500"
                                                    }`}
                                            >
                                                {CATEGORY_OPTIONS.map((opt) => (
                                                    <option key={opt.value} value={opt.value}>
                                                        {opt.label}
                                                    </option>
                                                ))}
                                            </select>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Validation Warnings & Errors Section */}
            {(data.invalid_register_numbers?.length > 0 ||
                data.duplicate_register_numbers?.length > 0 ||
                data.students_not_in_master?.length > 0) && (
                    <div className="bg-amber-500/5 border border-amber-500/20 rounded-2xl p-6 space-y-4">
                        <div className="flex items-center space-x-2">
                            <AlertTriangle className="w-5 h-5 text-amber-400" />
                            <h3 className="text-sm font-semibold text-amber-300">Validation Warnings & Master Data Mismatches</h3>
                        </div>

                        {data.invalid_register_numbers?.length > 0 && (
                            <div>
                                <p className="text-xs font-semibold text-slate-400 mb-1.5">
                                    Invalid Register Numbers ({data.invalid_register_numbers.length})
                                </p>
                                <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                                    {data.invalid_register_numbers.map((r: string) => (
                                        <span key={r} className="px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded text-xs font-mono">
                                            {r}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {data.duplicate_register_numbers?.length > 0 && (
                            <div>
                                <p className="text-xs font-semibold text-slate-400 mb-1.5">
                                    Duplicate Register Numbers ({data.duplicate_register_numbers.length})
                                </p>
                                <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                                    {data.duplicate_register_numbers.map((r: string) => (
                                        <span key={r} className="px-2 py-0.5 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded text-xs font-mono">
                                            {r}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {data.students_not_in_master?.length > 0 && (
                            <div>
                                <p className="text-xs font-semibold text-slate-400 mb-1.5">
                                    Students Not in Master Records ({data.students_not_in_master.length})
                                </p>
                                <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                                    {data.students_not_in_master.slice(0, 30).map((r: string) => (
                                        <span key={r} className="px-2 py-0.5 bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded text-xs font-mono">
                                            {r}
                                        </span>
                                    ))}
                                    {data.students_not_in_master.length > 30 && (
                                        <span className="text-xs text-slate-500 self-center">
                                            +{data.students_not_in_master.length - 30} more
                                        </span>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}

            {/* Confirmation & Import Trigger Buttons */}
            <div className="flex items-center justify-end space-x-4 pt-2">
                <button
                    onClick={() => navigate("/import/upload")}
                    className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-sm font-medium transition-colors"
                >
                    Cancel Upload
                </button>

                <button
                    onClick={() => setShowConfirmDialog(true)}
                    disabled={hasUnresolvedAmbiguousSheets}
                    className="px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-500 hover:to-green-500 text-white font-semibold rounded-xl shadow-lg shadow-emerald-600/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-2 text-sm"
                >
                    <Database className="w-4 h-4" />
                    <span>Confirm & Import Database</span>
                </button>
            </div>

            {/* Confirmation Modal */}
            <ConfirmationDialog
                isOpen={showConfirmDialog}
                title="Confirm Excel Ingestion"
                message={`Are you sure you want to import workbook "${data.file_name}" for ${data.company_name}? This will record drive registrations, stage results, and normalize offer statuses into the production database.`}
                confirmLabel="Execute Ingestion"
                isLoading={isImporting}
                onConfirm={handleConfirmImport}
                onCancel={() => setShowConfirmDialog(false)}
            />
        </div>
    );
};

export default ImportPreviewPage;
