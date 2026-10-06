import React from "react";
import { FolderOpen } from "lucide-react";

interface EmptyStateProps {
    title?: string;
    description?: string;
    actionLabel?: string;
    onAction?: () => void;
    icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
    title = "No records found",
    description = "There are currently no items matching your criteria.",
    actionLabel,
    onAction,
    icon,
}) => {
    return (
        <div className="flex flex-col items-center justify-center p-10 text-center bg-white/60 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-800">
            <div className="p-3 bg-slate-100 dark:bg-slate-800/80 rounded-full text-indigo-600 dark:text-indigo-400 mb-3">
                {icon || <FolderOpen className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />}
            </div>
            <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200">{title}</h3>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 max-w-md">{description}</p>
            {actionLabel && onAction && (
                <button
                    onClick={onAction}
                    className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-slate-900 dark:text-white rounded-lg text-sm font-medium transition-colors"
                >
                    {actionLabel}
                </button>
            )}
        </div>
    );
};
