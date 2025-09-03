import React from "react";
import { useState } from "react";
import { motion } from "framer-motion";
import { Loader2, FileText } from "lucide-react";

export default function JobReportForm() {
  const [jobTitle, setJobTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const res = await fetch("http://localhost:8000/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_title: jobTitle }),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.statusText}`);
      }

      const data = await res.json();
      setReport(data.report); // backend: { report: "..." }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="wrapper">
      
      <div className="container">
     
        <form onSubmit={handleSubmit} className="space-y-4">
            <h4 className="text-gray-600 mb-8">
              Enter a job title to generate an AI-powered report
            </h4>
          <input
            type="text"
            placeholder="e.g. Frontend Developer"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white py-3 rounded-xl font-semibold shadow-md hover:bg-indigo-700 transition disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin h-5 w-5" /> Generating...
              </>
            ) : (
              <>
                <FileText className="h-5 w-5" /> Generate Report
              </>
            )}
          </button>
        </form>

        {error && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 text-red-500 font-medium text-center"
          >
            {error}
          </motion.p>
        )}

        {report && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 p-6 bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-xl shadow-sm"
          >
            <h2 className="text-lg font-semibold mb-2 text-indigo-700 flex items-center gap-2">
              <FileText className="h-5 w-5" /> Report
            </h2>
            <pre className="whitespace-pre-wrap text-gray-800 text-sm leading-relaxed">
              {report}
            </pre>
          </motion.div>
        )}
    </div>
    </div>
  );
}
