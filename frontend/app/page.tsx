"use client";

import { useState } from "react";

const API_BASE =
  typeof window !== "undefined"
    ? "/api/backend"
    : "http://localhost:8000";

export default function Home() {
  const [company, setCompany] = useState("");
  const [industry, setIndustry] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">(
    "idle"
  );
  const [message, setMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("loading");
    setMessage("");
    try {
      const res = await fetch(`${API_BASE}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: company || undefined,
          industry: industry || undefined,
          notes: notes || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      setStatus("success");
      setMessage(data.message || "Lead received.");
      setCompany("");
      setIndustry("");
      setNotes("");
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Something went wrong.");
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-800/80 bg-slate-950/90 backdrop-blur">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <span className="font-semibold text-lg tracking-tight text-white">
            Tensorblue
          </span>
          <span className="text-xs uppercase tracking-wider text-slate-400">
            Universal Leads AI
          </span>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="max-w-xl w-full text-center space-y-8">
          <div>
            <h1 className="text-4xl sm:text-5xl font-bold text-white tracking-tight">
              Get more clients for Tensorblue
            </h1>
            <p className="mt-4 text-slate-400 text-lg">
              Universal Leads AI agent — smarter outreach, qualified leads,
              less manual work.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 sm:p-8 space-y-4 text-left"
          >
            <div>
              <label
                htmlFor="company"
                className="block text-sm font-medium text-slate-300 mb-1"
              >
                Company name
              </label>
              <input
                id="company"
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="Acme Inc."
                className="w-full rounded-lg border border-slate-700 bg-slate-800/80 px-4 py-2.5 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label
                htmlFor="industry"
                className="block text-sm font-medium text-slate-300 mb-1"
              >
                Industry
              </label>
              <input
                id="industry"
                type="text"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g. SaaS, Fintech"
                className="w-full rounded-lg border border-slate-700 bg-slate-800/80 px-4 py-2.5 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label
                htmlFor="notes"
                className="block text-sm font-medium text-slate-300 mb-1"
              >
                Notes
              </label>
              <textarea
                id="notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Any context for this lead..."
                rows={3}
                className="w-full rounded-lg border border-slate-700 bg-slate-800/80 px-4 py-2.5 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
              />
            </div>
            {message && (
              <p
                className={
                  status === "success"
                    ? "text-green-400 text-sm"
                    : status === "error"
                      ? "text-red-400 text-sm"
                      : "text-slate-400 text-sm"
                }
              >
                {message}
              </p>
            )}
            <button
              type="submit"
              disabled={status === "loading"}
              className="w-full rounded-lg bg-blue-600 px-4 py-3 font-medium text-white hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:pointer-events-none"
            >
              {status === "loading" ? "Sending…" : "Submit lead"}
            </button>
          </form>

          <p className="text-slate-500 text-sm">
            Leads are processed by the Universal Leads AI pipeline and used to
            grow Tensorblue’s client base.
          </p>
        </div>
      </main>

      <footer className="border-t border-slate-800/80 py-4">
        <div className="max-w-5xl mx-auto px-4 text-center text-slate-500 text-sm">
          Tensorblue Universal Leads AI · Backend: Python (FastAPI) · Frontend:
          Next.js + Tailwind
        </div>
      </footer>
    </div>
  );
}
