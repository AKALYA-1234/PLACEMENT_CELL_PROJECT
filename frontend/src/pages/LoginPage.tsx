import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/client';
import { Shield, Lock, User, AlertCircle, ArrowRight } from 'lucide-react';

export const LoginPage: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!username.trim() || !password) {
            setError('Please enter both username and password.');
            return;
        }

        setSubmitting(true);
        try {
            const res = await api.post('/auth/login', { username, password });
            await login(res.data.access_token);
            navigate('/dashboard');
        } catch (err: any) {
            const msg = err.response?.data?.detail || 'Invalid credentials or server error.';
            setError(msg);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
            {/* Dynamic Background Glow Elements */}
            <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>
            <div className="absolute bottom-10 right-10 w-72 h-72 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>

            <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
                <div className="flex justify-center">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <Shield className="w-8 h-8 text-white" />
                    </div>
                </div>
                <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-slate-100">
                    Placement Portal
                </h2>
                <p className="mt-2 text-center text-sm text-slate-400">
                    Admin Portal — Authorized Personnel Only
                </p>
            </div>

            <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
                <div className="bg-slate-900/80 backdrop-blur-xl py-8 px-6 shadow-2xl border border-slate-800/80 rounded-2xl sm:px-10">
                    {error && (
                        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start space-x-3">
                            <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                            <div className="text-sm text-red-300">{error}</div>
                        </div>
                    )}

                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Username
                            </label>
                            <div className="relative rounded-xl shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                    <User className="h-5 w-5 text-slate-500" />
                                </div>
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="admin"
                                    required
                                    className="block w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Password
                            </label>
                            <div className="relative rounded-xl shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                    <Lock className="h-5 w-5 text-slate-500" />
                                </div>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    className="block w-full pl-10 pr-4 py-3 bg-slate-950/70 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={submitting}
                            className="w-full flex justify-center items-center py-3 px-4 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:ring-offset-slate-900 shadow-lg shadow-blue-600/25 disabled:opacity-50 transition-all duration-200 cursor-pointer"
                        >
                            {submitting ? (
                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    Sign In to Dashboard
                                    <ArrowRight className="ml-2 w-4 h-4" />
                                </>
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};
