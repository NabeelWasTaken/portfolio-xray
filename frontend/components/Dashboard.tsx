"use client";

import { useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { AlertTriangle, TrendingDown, Mail, ArrowRight, Loader2, MessageSquare } from "lucide-react";
import ChatSidebar from "./ChatSidebar";

export default function Dashboard({ data, onReset }: { data: any, onReset: () => void }) {
  const [emailDraft, setEmailDraft] = useState<string | null>(null);
  const [isDrafting, setIsDrafting] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  // 1. Format the data for Recharts
  const chartData = [
    { name: "Legacy Funds", fees: data.legacy_fees },
    { name: "Wealthsimple", fees: data.wealthsimple_fees }
  ];

  // 2. Function to call your AI Email Agent
  const handleDraftEmail = async () => {  // <--- Ensure 'async' is here
  setIsDrafting(true);
  try {
    // Use the environment variable from Vercel, fallback to Render URL if missing
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://portfolio-xray.onrender.com";

    const response = await axios.post(`${API_URL}/api/draft-email`, {
      // We pass "Valued Client" as a placeholder, but in a real app this comes from the CRM
      client_name: "Valued Client", 
      legacy_fees: data.legacy_fees,
      savings: data.legacy_fees - data.wealthsimple_fees,
      overlap_summary: data.overlap_analysis
    });
    setEmailDraft(response.data.email_draft);
  } catch (error) {
    console.error("Failed to draft email", error);
    setEmailDraft("Error generating draft. Check backend connection.");
  } finally {
    setIsDrafting(false);
  }
};

  const savings = data.legacy_fees - data.wealthsimple_fees;

  return (
    <div className="w-full max-w-5xl mx-auto mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Top Action Bar */}
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          Portfolio Analysis Complete
        </h2>
        <button onClick={onReset} className="text-sm text-zinc-400 hover:text-white transition-colors">
          Upload New Document
        </button>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        
        {/* Savings Card */}
        <div className="bg-zinc-900 border border-emerald-500/30 p-6 rounded-2xl shadow-[0_0_30px_-5px_rgba(16,185,129,0.15)]">
          <p className="text-zinc-400 text-sm font-medium mb-1">Annual Savings Potential</p>
          <p className="text-4xl font-extrabold text-emerald-400">${savings.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
          <div className="mt-4 flex items-center text-emerald-500 text-sm font-medium">
            <TrendingDown className="w-4 h-4 mr-1" /> Fee reduction optimized
          </div>
        </div>

        {/* Legacy Fees Card */}
        <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl">
          <p className="text-zinc-400 text-sm font-medium mb-1">Current Hidden Fees</p>
          <p className="text-3xl font-bold text-red-400">${data.legacy_fees.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>

        {/* Wealthsimple Fees Card */}
        <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl">
          <p className="text-zinc-400 text-sm font-medium mb-1">Wealthsimple Fee (0.40%)</p>
          <p className="text-3xl font-bold text-white">${data.wealthsimple_fees.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
        </div>
      </div>

      {/* Main Content Split */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart Section */}
        <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl">
          <h3 className="text-lg font-semibold text-white mb-6">Fee Comparison (Annual)</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
                <Tooltip 
                  cursor={{ fill: '#27272a' }}
                  contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="fees" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === 0 ? '#f87171' : '#34d399'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Overlap & Actions Section */}
        <div className="flex flex-col gap-6">
          
          {/* Overlap Warning */}
          <div className="bg-amber-950/20 border border-amber-500/30 p-6 rounded-2xl">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-6 h-6 text-amber-500 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-amber-500 mb-2">Concentration Risk Detected</h3>
                <p className="text-amber-200/70 text-sm leading-relaxed">
                  {data.overlap_analysis}
                </p>
                <p className="text-amber-200/50 text-xs mt-3">
                  This client is paying multiple management fees to hold the exact same underlying assets.
                </p>
              </div>
            </div>
          </div>

          {/* AI Email Action */}
          <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-2xl flex-grow flex flex-col justify-center">
            {emailDraft ? (
              <div className="animate-in fade-in duration-500">
                <h3 className="text-sm font-semibold text-emerald-400 mb-3 flex items-center gap-2">
                  <Mail className="w-4 h-4" /> AI Draft Generated
                </h3>
                <div className="bg-black/50 p-4 rounded-xl border border-zinc-800 text-sm text-zinc-300 whitespace-pre-wrap">
                  {emailDraft}
                </div>
              </div>
            ) : (
              <div className="text-center">
                <Mail className="w-10 h-10 text-zinc-500 mx-auto mb-3" />
                <h3 className="text-lg font-semibold text-white mb-2">Ready to Pitch?</h3>
                <p className="text-zinc-400 text-sm mb-6">
                  Use Gemini to generate a personalized sales email based on these exact math findings.
                </p>
                <button 
                  onClick={handleDraftEmail}
                  disabled={isDrafting}
                  className="w-full py-3 bg-white text-black font-semibold rounded-xl hover:bg-zinc-200 transition-colors flex justify-center items-center gap-2"
                >
                  {isDrafting ? (
                    <><Loader2 className="w-5 h-5 animate-spin" /> Drafting...</>
                  ) : (
                    <>Draft Pitch Email <ArrowRight className="w-4 h-4" /></>
                  )}
                </button>
              </div>
            )}
          </div>

        </div>
      </div>
      
      {/* Floating Action Button to open Co-Pilot */}
      <button
        onClick={() => setIsChatOpen(true)}
        className="fixed bottom-8 right-8 bg-emerald-600 hover:bg-emerald-500 text-white p-4 rounded-full shadow-lg hover:shadow-emerald-500/25 transition-all duration-200 group flex items-center gap-3 z-30"
      >
        <MessageSquare className="w-6 h-6" />
        <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 ease-in-out whitespace-nowrap font-medium">
          Ask AI Co-Pilot
        </span>
      </button>

      {/* Render the Sidebar */}
      <ChatSidebar 
        isOpen={isChatOpen} 
        onClose={() => setIsChatOpen(false)} 
        portfolioData={data} 
      />
    </div>
  );
}