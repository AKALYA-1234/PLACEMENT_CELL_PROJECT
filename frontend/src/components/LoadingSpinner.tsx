import React from "react";
import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
    message?: string;
    className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    message = "Loading data...",
    className = "py-12",
}) => {
    return (
        <div className={`flex flex-col items-center justify-center ${className}`}>
            <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mb-3" />
            <p className="text-sm font-medium text-slate-600 dark:text-slate-300">{message}</p>
        </div>
    );
};
