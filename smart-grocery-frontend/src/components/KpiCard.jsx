export default function KpiCard({ title, value, delta, icon: Icon, tone = "emerald" }) {
  const tones = {
    emerald: "from-emerald-500/20 to-emerald-500/5 border-emerald-500/20",
    amber: "from-amber-500/20 to-amber-500/5 border-amber-500/20",
    rose: "from-rose-500/20 to-rose-500/5 border-rose-500/20",
    sky: "from-sky-500/20 to-sky-500/5 border-sky-500/20",
  };

  return (
    <div className={`rounded-3xl border bg-gradient-to-br p-5 shadow-xl ${tones[tone]}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">{title}</p>
          <h3 className="mt-2 text-3xl font-bold text-white">{value}</h3>
          {delta ? <p className="mt-2 text-xs text-slate-300">{delta}</p> : null}
        </div>
        {Icon ? (
          <div className="rounded-2xl bg-white/10 p-3 text-emerald-300">
            <Icon size={22} />
          </div>
        ) : null}
      </div>
    </div>
  );
}
