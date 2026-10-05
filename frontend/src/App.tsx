import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { Layout } from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ExcelUploadPage from "./pages/ExcelUploadPage";
import ImportPreviewPage from "./pages/ImportPreviewPage";
import ImportHistoryPage from "./pages/ImportHistoryPage";
import StudentsPage from "./pages/StudentsPage";
import StudentDetailPage from "./pages/StudentDetailPage";
import CompaniesPage from "./pages/CompaniesPage";
import CompanyDetailPage from "./pages/CompanyDetailPage";
import AnalyticsPage from "./pages/AnalyticsPage";

const App: React.FC = () => {
    return (
        <ThemeProvider>
            <BrowserRouter>
                <AuthProvider>
                    <Routes>
                        {/* Public Auth Route */}
                        <Route path="/login" element={<LoginPage />} />

                        {/* Protected Admin Routes */}
                        <Route element={<Layout />}>
                            <Route path="/" element={<Navigate to="/dashboard" replace />} />
                            <Route path="/dashboard" element={<DashboardPage />} />
                            <Route path="/import/upload" element={<ExcelUploadPage />} />
                            <Route path="/import/preview" element={<ImportPreviewPage />} />
                            <Route path="/imports" element={<ImportHistoryPage />} />
                            <Route path="/students" element={<StudentsPage />} />
                            <Route path="/students/:registerNumber" element={<StudentDetailPage />} />
                            <Route path="/companies" element={<CompaniesPage />} />
                            <Route path="/companies/:id" element={<CompanyDetailPage />} />
                            <Route path="/analytics" element={<AnalyticsPage />} />
                        </Route>

                        {/* Fallback Catch-all */}
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                </AuthProvider>
            </BrowserRouter>
        </ThemeProvider>
    );
};

export default App;
