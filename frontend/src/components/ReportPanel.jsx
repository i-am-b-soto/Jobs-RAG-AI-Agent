import React, { useState } from "react";
import { motion } from "framer-motion";

export default function ReportPanel({ report, onNewReport }) {
  const [question, setQuestion] = useState("ask a question?");

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="report-panel"
    >
      <h2 className="report-title">Report</h2>

      <pre className="report-content">{report}</pre>

      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        className="report-input"
      />

      <button onClick={onNewReport} className="report-button">
        Make a new report
      </button>
    </motion.div>
  );
}
