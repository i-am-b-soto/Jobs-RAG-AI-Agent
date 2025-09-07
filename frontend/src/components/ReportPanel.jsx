import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { FileText, Loader2, MessageSquareText } from "lucide-react";

const ReportPanel = ({ report, onNewReport, convID }) => {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([])
  const messagesEndRef = useRef(null);
  const [loading, setLoading] = useState(false);

  useEffect(()=>{

    setMessages([{"role":"clanker", "content": report}])
    return () => {}
  }, [report])


  // Scroll to newest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);


  const set_user_question = async (content) => {
    const current_messages = [...messages];
    current_messages.push({"role":"user", "content": content})
    setMessages(current_messages)
  }

  const set_clanker_response = async (content) => {
    const current_messages = [...messages];
    current_messages.push({"role":"clanker", "content": content})
    setMessages(current_messages)      
  }

  const handleAsk = async () => {
    if (!question.trim()) return;
  
    const currentQuestion = question; // store locally
    setQuestion(""); // immediately clear input
    setMessages((prev) => [...prev, { role: "user", content: currentQuestion }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: currentQuestion, conv_id: convID }),
      });
  
      if (!res.ok) throw new Error("Failed to fetch answer");
  
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "clanker", content: data.openai_response }]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 p-6 bg-gradient-to-br from-indigo-50 to-white border border-indigo-100 rounded-xl shadow-sm"
        >
        <h2 className="text-lg font-semibold mb-2 text-indigo-700 flex items-center gap-2">
          <FileText className="h-5 w-5" /> Report
        </h2>
        {messages && messages.map((msg, index) =>(
          <React.Fragment key={index}>
            {
            msg.role === "clanker" ? (
              <pre className="system-message whitespace-pre-wrap break-words">
                {msg.content.split("\n").map((line, idx) => (
                  <div key={idx}>{line}</div>))}
              </pre>):(
                <div className="user-message">
                  {msg.content}
                </div> 
                )
            }
          
          </React.Fragment>
        ))}
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
            <Loader2 className="spinner-small" />
          ) : (
            <MessageSquareText></MessageSquareText>
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
      <div ref={messagesEndRef} />
      </motion.div>
    </>
  );
};

export default ReportPanel;