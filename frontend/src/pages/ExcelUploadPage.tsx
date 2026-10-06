import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { Upload, FileSpreadsheet, X, AlertCircle, CheckCircle2, Loader2, Building2, Calendar } from "lucide-react";

interface ExistingCompany {
    id: number;
    name: string;
}

const ExcelUploadPage: React.FC = () => {
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [file, setFile] = useState<File | null>(null);
    const [companyName, setCompanyName] = useState("");
    const [academicYear, setAcademicYear] = useState("2025-2026");
    const [existingCompanies, setExistingCompanies] = useState<ExistingCompany[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const [isDragOver, setIsDragOver] = useState(false);

    useEffect(() => {
        const fetchCompanies = async () => {
            try {
                const res = await api.get<{ items: ExistingCompany[] }>("/admin/companies", { params: { limit: 50 } });
                setExistingCompanies(res.data.items);
            } catch (err) {
                console.error("Failed to load existing companies", err);
            }
        };
        fetchCompanies();
    }, []);

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
            setError("Please provide both an Excel file and company name.");
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
            navigate("/import/preview", {
                state: { validationData: res.data, file, companyName: companyName.trim(), academicYear },
            });
        } catch (err: any) {
            setError(err.response?.data?.detail || "Validation failed. Please check the Excel file format.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Upload Placement Excel Workbook</h1>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
                    Ingest company drive results, student registrations, round progression, and offers.
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
                    ? "border-indigo-500 bg-indigo-500/10"
                    : file
                        ? "border-emerald-500/50 bg-emerald-500/5"
                        : "border-slate-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-slate-700 bg-white/60 dark:bg-slate-900/60"
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
                        <CheckCircle2 className="w-12 h-12 text-emerald-400 mb-3 animate-bounce" />
                        <p className="text-base font-semibold text-slate-900 dark:text-white">{file.name}</p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                            {(file.size / 1024).toFixed(1)} KB — Click to change file
                        </p>
                        <button
                            onClick={(e) => { e.stopPropagation(); setFile(null); }}
                            className="mt-4 px-3 py-1 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-xs text-rose-400 rounded-lg flex items-center space-x-1 transition-colors"
                        >
                            <X className="w-3 h-3" />
                            <span>Remove File</span>
                        </button>
                    </div>
                ) : (
                    <div className="flex flex-col items-center">
                        <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl mb-3">
                            <FileSpreadsheet className="w-8 h-8 text-indigo-500 dark:text-indigo-400" />
                        </div>
                        <p className="text-base font-semibold text-slate-800 dark:text-slate-200">
                            Drag & Drop your Excel workbook here, or click to browse
                        </p>
                        <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Accepts .xlsx and .xls formats</p>
                    </div>
                )}
            </div>

            {/* Inputs Card */}
            <div className="bg-white dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 space-y-4">
                <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider flex items-center space-x-1.5">
                        <Building2 className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />
                        <span>Company Name *</span>
                    </label>
                    <input
                        type="text"
                        value={companyName}
                        onChange={(e) => setCompanyName(e.target.value)}
                        placeholder="e.g. Presidio, Netgear, Soliton"
                        className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 rounded-xl text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-slate-500 outline-none transition-all"
                    />

                    {/* Quick Select Buttons from existing companies */}
                    {existingCompanies.length > 0 && (
                        <div className="mt-2.5 flex flex-wrap gap-1.5 items-center">
                            <span className="text-[11px] text-slate-600 dark:text-slate-400 mr-1">Select existing:</span>
                            {existingCompanies.slice(0, 6).map((c) => (
                                <button
                                    key={c.id}
                                    type="button"
                                    onClick={() => setCompanyName(c.name)}
                                    className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white rounded-lg text-xs transition-colors border border-slate-200 dark:border-slate-700/60"
                                >
                                    {c.name}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider flex items-center space-x-1.5">
                        <Calendar className="w-3.5 h-3.5 text-indigo-500 dark:text-indigo-400" />
                        <span>Academic Year</span>
                    </label>
                    <select
                        value={academicYear}
                        onChange={(e) => setAcademicYear(e.target.value)}
                        className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 rounded-xl text-slate-900 dark:text-white text-sm outline-none transition-all"
                    >
                        <option value="2025-2026">2025-2026</option>
                        <option value="2024-2025">2024-2025</option>
                        <option value="2023-2024">2023-2024</option>
                    </select>
                </div>
            </div>

            {/* Validate & Preview Trigger */}
            <button
                onClick={handleValidate}
                disabled={isLoading || !file || !companyName.trim()}
                className="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-sm"
            >
                {isLoading ? (
                    <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Parsing & Validating Workbook...</span>
                    </>
                ) : (
                    <>
                        <Upload className="w-4 h-4" />
                        <span>Upload & Validate Workbook</span>
                    </>
                )}
            </button>
        </div>
    );
};

export default ExcelUploadPage;
