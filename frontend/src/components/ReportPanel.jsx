import React, { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Loader2 } from "lucide-react";

const ReportPanel = ({ report, loading, onAsk, onNewReport }) => {
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setAsking(true);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) throw new Error("Failed to fetch answer");

      const data = await res.json();
      if (onAsk) onAsk(data.answer || "No answer returned.");
    } catch (err) {
      console.error(err);
      if (onAsk) onAsk("❌ Error asking question.");
    } finally {
      setAsking(false);
    }
  };

  return (
    <>
      {report && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 p-6 bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-xl shadow-sm"
        >
          <h2 className="text-lg font-semibold mb-2 text-indigo-700 flex items-center gap-2">
            <FileText className="h-5 w-5" /> Report
          </h2>
          <pre className="report-content whitespace-pre-wrap break-words">
          {report.split("\n").map((line, idx) => (
              <div key={idx}>{line}</div>
            ))}
          </pre>

          {/* Question input */}
          <div className="ask-button-group">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question?"
              className="ask-input"
            />
            <button
              onClick={handleAsk}
              disabled={loading}
              className="ask-button"
            >
              {loading ? (
                <Loader2 className="animate-spin w-5 h-5" />
              ) : (
                "Go"
              )}
            </button>
          </div>         
          {/* New report button */}
          <div className="mt-4">
            <button
              onClick={onNewReport}
              className="w-full px-4 py-2 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200"
            >
              Make a new report
            </button>
          </div>
        </motion.div>
      )}
    </>
  );
};

export default ReportPanel;