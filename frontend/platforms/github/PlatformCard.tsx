"use client";

interface PlatformCardProps {
  name: string;
  status?: "ok" | "failed" | "stub";
  leads?: number;
  timeSeconds?: number;
}

export default function PlatformCard({ name, status = "stub", leads = 0, timeSeconds = 0 }: PlatformCardProps) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
      <div className="font-medium text-slate-200">{name}</div>
      <div className="mt-2 flex gap-2 text-xs">
        <span className={status === "ok" ? "text-green-400" : status === "failed" ? "text-red-400" : "text-slate-500"}>
          {status}
        </span>
        {leads > 0 && <span className="text-slate-400">{leads} leads</span>}
        {timeSeconds > 0 && <span className="text-slate-400">{timeSeconds.toFixed(0)}s</span>}
      </div>
    </div>
  );
}
