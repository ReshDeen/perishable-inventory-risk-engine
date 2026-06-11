import { Search, Download, Bell } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Topbar() {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8 lg:pl-12">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-emerald-300/80">Predict. Prevent. Preserve.</p>
          <h2 className="mt-1 text-lg font-semibold text-white sm:text-2xl">P.I.R.E. Control Center</h2>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 md:flex">
            <Search size={16} />
            Live inventory intelligence
          </div>
          <Link to="/app/alerts" className="rounded-2xl border border-white/10 bg-white/5 p-3 text-slate-300 transition hover:border-emerald-500/30 hover:text-white">
            <Bell size={18} />
          </Link>
          <Link to="/app/export" className="rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-400 flex items-center gap-2">
            <Download size={16} />
            Export
          </Link>
          <div className="hidden rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300 sm:block">
            {user?.name || "Manager"}
          </div>
        </div>
      </div>
    </header>
  );
}
