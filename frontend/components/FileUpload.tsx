"use client";

import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { UploadCloud, FileText } from "lucide-react";

export default function FileUpload({ onUpload }: { onUpload: (file: File) => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = () => {
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto mt-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`relative flex flex-col items-center justify-center w-full h-64 p-6 border-2 border-dashed rounded-2xl transition-colors duration-300 ease-in-out cursor-pointer bg-zinc-900/50 backdrop-blur-sm
          ${isDragging ? "border-emerald-500 bg-emerald-500/10" : "border-zinc-700 hover:border-zinc-500"}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".txt,.pdf"
          className="hidden"
        />

        {file ? (
          <motion.div 
            initial={{ scale: 0.9 }} 
            animate={{ scale: 1 }} 
            className="flex flex-col items-center text-emerald-400"
          >
            <FileText className="w-16 h-16 mb-4" />
            <p className="text-lg font-medium text-slate-200">{file.name}</p>
            <p className="text-sm text-zinc-400 mt-2">Click to change file</p>
          </motion.div>
        ) : (
          <div className="flex flex-col items-center text-zinc-400">
            <UploadCloud className={`w-16 h-16 mb-4 transition-colors ${isDragging ? "text-emerald-500" : "text-zinc-500"}`} />
            <p className="text-lg font-medium text-slate-200">
              Drop portfolio PDF here
            </p>
            <p className="text-sm mt-2">or click to browse files</p>
          </div>
        )}
      </motion.div>

      {/* Action Button */}
      {file && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 flex justify-center"
        >
          <button
            onClick={handleAnalyze}
            className="px-8 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-full shadow-lg hover:shadow-emerald-500/25 transition-all duration-200 flex items-center gap-2"
          >
            Generate X-Ray Report
          </button>
        </motion.div>
      )}
    </div>
  );
}