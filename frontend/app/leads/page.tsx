"use client";

import { useState, useEffect } from "react";

const API = "/api/backend";

export default function LeadsPage() {
  const [running, setRunning] = useState(false);
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null);
  const [outputs, setOutputs] = useState<{ name: string; path: string }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API}/runs/latest`)
      .then((r) => (r.ok ? r.json() : null))
      .then(setSummary)
      .catch(() => setSummary(null));
    fetch(`${API}/outputs`)
      .then((r) => r.json())
      .then((d) => setOutputs(d.files || []))
      .catch(() => setOutputs([]));
  }, []);

  const runScrape = async () => {
    setRunning(true);
    setError(null);
    try {
      const res = await fetch(`${API}/run`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Run failed");
      setSummary(data);
      const outRes = await fetch(`${API}/outputs`);
      const outData = await outRes.json();
      setOutputs(outData.files || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Run failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h1 className="text-2xl font-bold">Universal Leads Agent</h1>
          <a href="/" className="text-slate-400 hover:text-white text-sm">
            Home
          </a>
        </header>

        <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h2 className="text-lg font-semibold mb-4">Run scrape</h2>
          <p className="text-slate-400 text-sm mb-4">
            Run all enabled platforms (browser-only). Merge, dedupe, export XLSX + JSONL.
          </p>
          <button
            onClick={runScrape}
            disabled={running}
            className="rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-500 disabled:opacity-50"
          >
            {running ? "Running…" : "Run scrape"}
          </button>
          {error && <p className="mt-2 text-red-400 text-sm">{error}</p>}
        </section>

        {summary && (
          <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <h2 className="text-lg font-semibold mb-4">Last run summary</h2>
            <dl className="grid grid-cols-2 gap-2 text-sm">
              <dt className="text-slate-400">Total leads</dt>
              <dd>{String(summary.total_leads ?? 0)}</dd>
              <dt className="text-slate-400">Unique (after dedupe)</dt>
              <dd>{String(summary.unique_leads_after_dedupe ?? 0)}</dd>
              <dt className="text-slate-400">Platforms ok / failed</dt>
              <dd>{String(summary.platforms_ok ?? 0)} / {String(summary.platforms_failed ?? 0)}</dd>
              <dt className="text-slate-400">Runtime (s)</dt>
              <dd>{Number(summary.total_runtime_seconds ?? 0).toFixed(1)}</dd>
              <dt className="text-slate-400">XLSX</dt>
              <dd className="truncate">{String(summary.output_xlsx ?? "")}</dd>
            </dl>
          </section>
        )}

        <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h2 className="text-lg font-semibold mb-4">Outputs</h2>
          <ul className="space-y-2">
            {outputs.length === 0 && <li className="text-slate-500 text-sm">No files yet.</li>}
            {outputs.map((f) => (
              <li key={f.name} className="flex items-center gap-2">
                <a
                  href={`${API}/outputs/${f.name}`}
                  download={f.name}
                  className="text-blue-400 hover:underline text-sm"
                >
                  {f.name}
                </a>
                <span className="text-slate-500 text-xs">Download</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
          <h2 className="text-lg font-semibold mb-4">Platforms</h2>
          <p className="text-slate-400 text-sm mb-4">
            Full: Reddit, GitHub, Hacker News, Search discovery, Craigslist. Others are stubs (exit quickly).
          </p>
          <div className="flex flex-wrap gap-2">
            {["reddit", "github", "hackernews", "search_discovery", "craigslist"].map((p) => (
              <span key={p} className="rounded bg-slate-800 px-2 py-1 text-xs">
                {p}
              </span>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
