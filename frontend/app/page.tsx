"use client";

import { useState } from "react";
import axios from "axios";
import { Loader2 } from "lucide-react";
import FileUpload from "../components/FileUpload";
import Dashboard from "../components/Dashboard"; // <-- Import the new component

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [reportData, setReportData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    setIsLoading(true);
    setError(null);
    setReportData(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/analyze-portfolio", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setReportData(response.data);
    } catch (err) {
      console.error("Upload error:", err);
      setError("Failed to analyze portfolio. Ensure your Python backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-slate-50 flex flex-col items-center pt-16 px-6 pb-24">
      
      {/* Header Section */}
      <div className="text-center mb-8">
        <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight mb-4">
          Portfolio <span className="text-emerald-500">X-Ray</span>
        </h1>
        <p className="text-zinc-400 max-w-lg mx-auto text-lg">
          Upload a client statement to instantly detect hidden fees, overlapping assets, and calculate Wealthsimple transition savings.
        </p>
      </div>

      {!isLoading && !reportData && (
        <FileUpload onUpload={handleFileUpload} />
      )}

      {isLoading && (
        <div className="flex flex-col items-center mt-16 text-emerald-500">
          <Loader2 className="w-12 h-12 animate-spin mb-4" />
          <p className="text-lg text-slate-300 animate-pulse">
            AI is analyzing portfolio... this takes a few seconds.
          </p>
        </div>
      )}

      {error && (
        <div className="mt-8 p-4 bg-red-900/30 border border-red-500/50 text-red-200 rounded-lg max-w-xl text-center">
          {error}
        </div>
      )}

      {/* 4. Render the new stunning Dashboard! */}
      {reportData && (
        <Dashboard data={reportData} onReset={() => setReportData(null)} />
      )}

    </main>
  );
}