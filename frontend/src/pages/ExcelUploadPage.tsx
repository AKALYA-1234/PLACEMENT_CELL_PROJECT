import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { Upload, FileSpreadsheet, X, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

const ExcelUploadPage: React.FC = () => {
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [file, setFile] = useState<File | null>(null);
    const [companyName, setCompanyName] = useState("");
    const [academicYear, setAcademicYear] = useState("2025-2026");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const [isDragOver, setIsDragOver] = useState(false);

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && (droppedFile.name.endsWith(".xlsx") || droppedFile.name.endsWith(".xls"))) {
            setFile(droppedFile);
            setError("");
        } else {
            setError("Please upload a valid Excel workbook (.xlsx or .xls)");
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = e.target.files?.[0];
        if (selected) {
            setFile(selected);
            setError("");
        }
    };

    const handleValidate = async () => {
        if (!file || !companyName.trim()) {
            setError("Please provide both a file and company name.");
            return;
        }

        setIsLoading(true);
        setError("");

        const formData = new FormData();
        formData.append("file", file);
        formData.append("company_name", companyName.trim());
        formData.append("academic_year", academicYear);

        try {
            const res = await api.post("/admin/import/validate", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            navigate("/import/preview", { state: { validationData: res.data, file, companyName, academicYear } });
        } catch (err: any) {
            setError(err.response?.data?.detail || "Validation failed. Please check the file format.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white">Upload Excel Workbook</h1>
                <p className="text-sm text-slate-400 mt-0.5">
                    Upload a company placement roundwise Excel file for validation and import.
                </p>
            </div>

            {error && (
                <div className="flex items-center space-x-2 bg-rose-500/10 border border-rose-500/20 rounded-xl p-3">
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                    <p className="text-sm text-rose-300">{error}</p>
                </div>
            )}

            {/* Drag & Drop Zone */}
            <div
                onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${isDragOver
                        ? "border-indigo-500 bg-indigo-500/5"
                        : file
                            ? "border-emerald-500/40 bg-emerald-500/5"
                            : "border-slate-700 hover:border-slate-600 bg-slate-900/50"
                    }`}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleFileSelect}
                    className="hidden"
                />

                {file ? (
                    <div className="flex flex-col items-center">
                        <CheckCircle2 className="w-10 h-10 text-emerald-400 mb-3" />
                        <p className="text-sm font-semibold text-white">{file.name}</p>
                        <p className="text-xs text-slate-400 mt-1">
                            {(file.size / 1024).toFixed(1)} KB
                        </p>
                        <button
                            onClick={(e) => { e.stopPropagation(); setFile(null); }}
                            className="mt-3 text-xs text-rose-400 hover:text-rose-300 flex items-center space-x-1"
                        >
                            <X className="w-3 h-3" />
                            <span>Remove file</span>
                        </button>
                    </div>
                ) : (
                    <div className="flex flex-col items-center">
                        <div className="p-4 bg-slate-800/80 rounded-2xl mb-3">
                            <FileSpreadsheet className="w-8 h-8 text-indigo-400" />
                        </div>
                        <p className="text-sm font-semibold text-slate-200">
                            Drop your Excel file here or click to browse
                        </p>
                        <p className="text-xs text-slate-500 mt-1">Supports .xlsx and .xls files</p>
                    </div>
                )}
            </div>

            {/* Form Fields */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-4">
                <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                        Company Name *
                    </label>
                    <input
                        type="text"
                        value={companyName}
                        onChange={(e) => setCompanyName(e.target.value)}
                        placeholder="e.g. Presidio, Netgear Inc."
                        className="w-full px-4 py-2.5 bg-slate-800/80 border border-slate-700 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 rounded-xl text-white text-sm placeholder-slate-500 outline-none transition-all"
                    />
                </div>

                <div>
                    <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
                        Academic Year
                    </label>
                    <input
                        type="text"
                        value={academicYear}
                        onChange={(e) => setAcademicYear(e.target.value)}
                        placeholder="2025-2026"
                        className="w-full px-4 py-2.5 bg-slate-800/80 border border-slate-700 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 rounded-xl text-white text-sm placeholder-slate-500 outline-none transition-all"
                    />
                </div>
            </div>

            {/* Submit */}
            <button
                onClick={handleValidate}
                disabled={isLoading || !file || !companyName.trim()}
                className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
                {isLoading ? (
                    <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Validating workbook...</span>
                    </>
                ) : (
                    <>
                        <Upload className="w-4 h-4" />
                        <span>Validate & Preview</span>
                    </>
                )}
            </button>
        </div>
    );
};

export default ExcelUploadPage;
