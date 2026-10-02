import React, { useState } from "react";
import { useLocation, useNavigate, Navigate } from "react-router-dom";
import { api } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { ConfirmationDialog } from "../components/ConfirmationDialog";
import {
    CheckCircle2, AlertTriangle, FileSpreadsheet, Loader2,
    ArrowLeft, Database, XCircle
} from "lucide-react";

const ImportPreviewPage: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const state = location.state as any;

    const [showConfirmDialog, setShowConfirmDialog] = useState(false);
    const [isImporting, setIsImporting] = useState(false);
    const [importResult, setImportResult] = useState<any>(null);
    const [importError, setImportError] = useState("");

    if (!state?.validationData) {
        return <Navigate to="/import/upload" replace />;
    }

    const data = state.validationData;

    const handleConfirmImport = async () => {
        setIsImporting(true);
        setImportError("");

        const formData = new FormData();
        formData.append("file", state.file);
        formData.append("company_name", state.companyName);
        formData.append("academic_year", state.academicYear);

        try {
            const res = await api.post("/admin/import/confirm", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setImportResult(res.data);
            setShowConfirmDialog(false);
        } catch (err: any) {
            setImportError(err.response?.data?.detail || "Import failed.");
            setShowConfirmDialog(false);
        } finally {
            setIsImporting(false);
        }
    };

    if (importResult) {
        return (
            <div className="max-w-2xl mx-auto space-y-6">
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-8 text-center">
                    <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-white">Import Successful</h2>
                    <p className="text-sm text-slate-400 mt-1">
                        {importResult.company_name} — {importResult.imported_rows ?? 0} records imported.
                    </p>
                    <div className="flex items-center justify-center space-x-3 mt-6">
                        <button onClick={() => navigate("/imports")} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm font-medium transition-colors">
                            View Import History
                        </button>
                        <button onClick={() => navigate("/import/upload")} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition-colors">
                            Upload Another
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <button onClick={() => navigate(-1)} className="flex items-center space-x-1 text-sm text-slate-400 hover:text-white mb-2 transition-colors">
                        <ArrowLeft className="w-4 h-4" /><span>Back</span>
                    </button>
                    <h1 className="text-2xl font-bold text-white">Import Preview</h1>
                    <p className="text-sm text-slate-400 mt-0.5">Review validation results before confirming import.</p>
                </div>
                <StatusBadge status={data.is_valid_for_import ? "VALID" : "INVALID"} />
            </div>

            {importError && (
                <div className="flex items-center space-x-2 bg-rose-500/10 border border-rose-500/20 rounded-xl p-3">
                    <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                    <p className="text-sm text-rose-300">{importError}</p>
                </div>
            )}

            {/* Summary Card */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center space-x-3 mb-4">
                    <FileSpreadsheet className="w-5 h-5 text-indigo-400" />
                    <h2 className="text-base font-semibold text-white">{data.company_name}</h2>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                        { label: "File", value: data.file_name },
                        { label: "Sheets", value: data.total_sheets },
                        { label: "Registered", value: data.registered_count },
                        { label: "Placed", value: data.placed_count },
                    ].map((item) => (
                        <div key={item.label}>
                            <p className="text-xs text-slate-500 uppercase tracking-wider">{item.label}</p>
                            <p className="text-sm font-semibold text-white mt-0.5">{item.value}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Issues */}
            {(data.invalid_register_numbers?.length > 0 ||
                data.duplicate_register_numbers?.length > 0 ||
                data.students_not_in_master?.length > 0) && (
                    <div className="bg-amber-500/5 border border-amber-500/20 rounded-2xl p-6 space-y-3">
                        <div className="flex items-center space-x-2 mb-2">
                            <AlertTriangle className="w-5 h-5 text-amber-400" />
                            <h3 className="text-sm font-semibold text-amber-300">Validation Warnings</h3>
                        </div>
                        {data.invalid_register_numbers?.length > 0 && (
                            <div>
                                <p className="text-xs text-slate-400 mb-1">Invalid Register Numbers ({data.invalid_register_numbers.length})</p>
                                <div className="flex flex-wrap gap-1.5">
                                    {data.invalid_register_numbers.map((r: string) => (
                                        <span key={r} className="px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded text-xs">{r}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {data.duplicate_register_numbers?.length > 0 && (
                            <div>
                                <p className="text-xs text-slate-400 mb-1">Duplicate Register Numbers ({data.duplicate_register_numbers.length})</p>
                                <div className="flex flex-wrap gap-1.5">
                                    {data.duplicate_register_numbers.map((r: string) => (
                                        <span key={r} className="px-2 py-0.5 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded text-xs">{r}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {data.students_not_in_master?.length > 0 && (
                            <div>
                                <p className="text-xs text-slate-400 mb-1">Not in Master Student Table ({data.students_not_in_master.length})</p>
                                <div className="flex flex-wrap gap-1.5">
                                    {data.students_not_in_master.slice(0, 20).map((r: string) => (
                                        <span key={r} className="px-2 py-0.5 bg-orange-500/10 text-orange-400 border border-orange-500/20 rounded text-xs">{r}</span>
                                    ))}
                                    {data.students_not_in_master.length > 20 && (
                                        <span className="text-xs text-slate-500">+{data.students_not_in_master.length - 20} more</span>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                )}

            {/* Sheet Breakdown */}
            {data.sheets_detail && data.sheets_detail.length > 0 && (
                <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden">
                    <div className="p-4 border-b border-slate-800">
                        <h3 className="text-sm font-semibold text-white">Sheet Breakdown</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-800/50">
                                <tr>
                                    <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-400 uppercase">Sheet Name</th>
                                    <th className="text-right px-4 py-2.5 text-xs font-semibold text-slate-400 uppercase">Records</th>
                                    <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-400 uppercase">Category</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/50">
                                {data.sheets_detail.map((sheet: any, i: number) => (
                                    <tr key={i} className="hover:bg-slate-800/30 transition-colors">
                                        <td className="px-4 py-2.5 text-white font-medium">{sheet.sheet_name}</td>
                                        <td className="px-4 py-2.5 text-right text-slate-300">{sheet.record_count}</td>
                                        <td className="px-4 py-2.5"><StatusBadge status={sheet.category || "UNKNOWN"} /></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-end space-x-3">
                <button onClick={() => navigate("/import/upload")} className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm font-medium transition-colors">
                    Cancel
                </button>
                <button
                    onClick={() => setShowConfirmDialog(true)}
                    disabled={!data.is_valid_for_import}
                    className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-500 hover:to-green-500 text-white font-semibold rounded-xl shadow-lg shadow-emerald-600/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                    <Database className="w-4 h-4" />
                    <span>Confirm Import</span>
                </button>
            </div>

            <ConfirmationDialog
                isOpen={showConfirmDialog}
                title="Confirm Import"
                message={`This will import all validated records from "${data.file_name}" for ${data.company_name} into the database. This action cannot be undone. Proceed?`}
                confirmLabel="Import Now"
                isLoading={isImporting}
                onConfirm={handleConfirmImport}
                onCancel={() => setShowConfirmDialog(false)}
            />
        </div>
    );
};

export default ImportPreviewPage;
