import { ArrowRight, ShieldCheck, TrendingUp, BellRing } from "lucide-react";
import { Link } from "react-router-dom";

const features = [
  { icon: ShieldCheck, title: "Risk detection", text: "Predict expiry risk before spoilage impacts margins." },
  { icon: TrendingUp, title: "Live analytics", text: "Track stock health, spoilage exposure, and trends." },
  { icon: BellRing, title: "Action alerts", text: "Act on items expiring soon or moving too slowly." },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,#173b2a_0%,#08111a_45%,#02060b_100%)] text-white">
      <div className="mx-auto flex min-h-screen max-w-7xl items-center px-6 py-12 lg:px-10">
        <div className="grid gap-12 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
          <div>
            <p className="inline-flex rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.35em] text-emerald-200">
              P.I.R.E. – Perishable Inventory Risk Engine
            </p>
            <h1 className="mt-6 max-w-3xl text-5xl font-black tracking-tight sm:text-6xl lg:text-7xl">
              Predict. Prevent. Preserve.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
              A production-ready MERN + Python + XGBoost system for perishable inventory intelligence, real-time expiry risk prediction, and waste reduction.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link to="/login" className="inline-flex items-center gap-2 rounded-2xl bg-emerald-500 px-6 py-4 font-semibold text-white transition hover:bg-emerald-400">
                Launch Dashboard <ArrowRight size={18} />
              </Link>
              <Link to="/register" className="inline-flex items-center gap-2 rounded-2xl border border-white/15 bg-white/5 px-6 py-4 font-semibold text-white transition hover:border-emerald-400/30 hover:bg-emerald-400/10">
                Create Account
              </Link>
            </div>
          </div>

          <div className="grid gap-4 rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-2xl backdrop-blur-xl">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div key={feature.title} className="rounded-3xl border border-white/10 bg-slate-950/60 p-5">
                  <div className="flex items-start gap-4">
                    <div className="rounded-2xl bg-emerald-500/15 p-3 text-emerald-300">
                      <Icon size={22} />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
                      <p className="mt-2 text-sm leading-6 text-slate-300">{feature.text}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
