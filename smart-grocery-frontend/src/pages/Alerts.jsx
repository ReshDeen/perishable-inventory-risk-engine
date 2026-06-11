import { useEffect, useState } from "react";
import api from "../services/api";
import Loader from "../components/ui/Loader";

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get("/alerts");
        setAlerts(response.data);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <Loader label="Generating alerts..." />;

  return (
    <div className="space-y-6 text-slate-100">
      <div>
        <h1 className="text-2xl font-semibold text-white">Alerts</h1>
        <p className="text-sm text-slate-400">Expiry warnings, spoilage risk, and overstock signals.</p>
      </div>

      <div className="grid gap-4">
        {alerts.map((alert) => (
          <div key={`${alert.type}-${alert.message}`} className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-lg font-semibold text-white">{alert.type}</p>
                <p className="mt-1 text-sm text-slate-300">{alert.message}</p>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${alert.severity === "high" ? "bg-rose-500/15 text-rose-300" : "bg-amber-500/15 text-amber-300"}`}>
                {alert.severity}
              </span>
            </div>
          </div>
        ))}
        {!alerts.length ? <p className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center text-slate-300">No alerts at this time.</p> : null}
      </div>
    </div>
  );
}
