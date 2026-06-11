import { useEffect, useState } from "react";
import { AlertTriangle, ArrowUpRight, Package, ShieldCheck, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../services/api";
import Loader from "../components/ui/Loader";
import KpiCard from "../components/KpiCard";
import RiskBadge from "../components/ui/RiskBadge";

const colors = ["#16A34A", "#F59E0B", "#EF4444"];

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [riskDistribution, setRiskDistribution] = useState([]);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [summaryRes, riskRes, trendsRes, inventoryRes, alertsRes] = await Promise.all([
          api.get("/analytics/summary"),
          api.get("/analytics/risk-distribution"),
          api.get("/analytics/monthly-trends"),
          api.get("/inventory"),
          api.get("/alerts"),
        ]);
        setSummary(summaryRes.data);
        setRiskDistribution(riskRes.data);
        setMonthlyTrends(trendsRes.data);
        setInventory(inventoryRes.data);
        setAlerts(alertsRes.data.slice(0, 4));
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  if (loading) {
    return <Loader label="Loading dashboard intelligence..." />;
  }

  return (
    <div className="space-y-6 text-slate-100">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <KpiCard title="Total Products" value={summary?.totalProducts ?? 0} delta="Tracked across active inventory" icon={Package} tone="emerald" />
        <KpiCard title="High Risk" value={summary?.highRiskCount ?? 0} delta="Needs urgent intervention" icon={AlertTriangle} tone="rose" />
        <KpiCard title="Estimated Waste Value" value={`$${summary?.estimatedWasteValue ?? 0}`} delta="Potential spoilage exposure" icon={ArrowUpRight} tone="amber" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">Monthly Trends</h3>
              <p className="text-sm text-slate-400">Stock growth and risk exposure over time</p>
            </div>
            <ShieldCheck className="text-emerald-300" />
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyTrends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Legend />
                <Line type="monotone" dataKey="addedItems" stroke="#16A34A" strokeWidth={3} />
                <Line type="monotone" dataKey="highRisk" stroke="#EF4444" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
          <h3 className="text-xl font-semibold text-white">Risk Distribution</h3>
          <p className="text-sm text-slate-400">Current spoilage classification mix</p>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskDistribution} dataKey="value" nameKey="risk" innerRadius={70} outerRadius={110} paddingAngle={4}>
                  {riskDistribution.map((entry, index) => (
                    <Cell key={entry.risk} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
          <h3 className="text-xl font-semibold text-white">Inventory Health Snapshot</h3>
          <div className="mt-4 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={inventory.slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Bar dataKey="quantity" fill="#16A34A" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
          <h3 className="text-xl font-semibold text-white">Priority Alerts</h3>
          <div className="mt-4 space-y-3">
            {alerts.map((alert) => (
              <div key={`${alert.type}-${alert.message}`} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-white">{alert.type}</p>
                    <p className="mt-1 text-sm text-slate-300">{alert.message}</p>
                  </div>
                  <RiskBadge value={alert.type === "High Risk" ? "High Risk" : "Moderate Risk"} />
                </div>
              </div>
            ))}
            {!alerts.length ? <p className="text-sm text-slate-400">No active alerts.</p> : null}
          </div>
        </div>
      </section>
    </div>
  );
}
