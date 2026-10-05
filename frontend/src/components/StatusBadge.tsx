import React from "react";

interface StatusBadgeProps {
    status: string;
    className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = "" }) => {
    const norm = status.toUpperCase();

    let colorClasses = "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700";
    if (["PLACED", "SUCCESS", "QUALIFIED"].includes(norm)) {
        colorClasses = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    } else if (["PARTIAL_SUCCESS", "PROGRESSION", "WARNING"].includes(norm)) {
        colorClasses = "bg-amber-500/10 text-amber-400 border-amber-500/20";
    } else if (["FAILED", "DISQUALIFIED", "ABSENT", "UNPLACED", "ERROR"].includes(norm)) {
        colorClasses = "bg-rose-500/10 text-rose-400 border-rose-500/20";
    } else if (["REGISTERED", "INFO"].includes(norm)) {
        colorClasses = "bg-indigo-500/10 text-indigo-400 border-indigo-500/20";
    }

    return (
        <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClasses} ${className}`}
        >
            <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-80" />
            {status}
        </span>
    );
};
