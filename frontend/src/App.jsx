import React from "react";
import JobReportForm from "./components/JobReportForm";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900 mb-4 ">
            Job Report Generator
          </h1>
          <div className="wrapper">

          </div>
 
        </div>


        <JobReportForm />
      </div>
    </div>
  );
}