import React from "react";
import { AlertTriangle, X } from "lucide-react";

interface ConfirmationDialogProps {
    isOpen: boolean;
    title: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    isDangerous?: boolean;
    isLoading?: boolean;
    onConfirm: () => void;
    onCancel: () => void;
}

export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
    isOpen,
    title,
    message,
    confirmLabel = "Confirm",
    cancelLabel = "Cancel",
    isDangerous = false,
    isLoading = false,
    onConfirm,
    onCancel,
}) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
            <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden p-6">
                <button
                    onClick={onCancel}
                    disabled={isLoading}
                    className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
                >
                    <X className="w-5 h-5" />
                </button>

                <div className="flex items-center space-x-3 mb-4">
                    <div
                        className={`p-3 rounded-full ${isDangerous ? "bg-rose-500/10 text-rose-400" : "bg-indigo-500/10 text-indigo-400"
                            }`}
                    >
                        <AlertTriangle className="w-6 h-6" />
                    </div>
                    <h3 className="text-lg font-bold text-white">{title}</h3>
                </div>

                <p className="text-sm text-slate-300 mb-6 leading-relaxed">{message}</p>

                <div className="flex items-center justify-end space-x-3">
                    <button
                        onClick={onCancel}
                        disabled={isLoading}
                        className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
                    >
                        {cancelLabel}
                    </button>
                    <button
                        onClick={onConfirm}
                        disabled={isLoading}
                        className={`px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors flex items-center space-x-2 ${isDangerous
                                ? "bg-rose-600 hover:bg-rose-500"
                                : "bg-indigo-600 hover:bg-indigo-500"
                            }`}
                    >
                        {isLoading ? "Processing..." : confirmLabel}
                    </button>
                </div>
            </div>
        </div>
    );
};
