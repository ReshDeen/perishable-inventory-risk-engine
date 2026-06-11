import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../services/api";
import Loader from "../components/ui/Loader";
import KpiCard from "../components/KpiCard";
import { Package, ShieldAlert, ShieldCheck, ArrowDownRight } from "lucide-react";

const pieColors = ["#16A34A", "#F59E0B", "#EF4444"];

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [riskDistribution, setRiskDistribution] = useState([]);
  const [monthlyTrends, setMonthlyTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [summaryRes, riskRes, trendsRes] = await Promise.all([
          api.get("/analytics/summary"),
          api.get("/analytics/risk-distribution"),
          api.get("/analytics/monthly-trends"),
        ]);
        setSummary(summaryRes.data);
        setRiskDistribution(riskRes.data);
        setMonthlyTrends(trendsRes.data);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <Loader label="Loading analytics..." />;

  return (
    <div className="space-y-6 text-slate-100">
      <div>
        <h1 className="text-2xl font-semibold text-white">Analytics</h1>
        <p className="text-sm text-slate-400">Operational performance and spoilage intelligence.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <KpiCard title="Safe Items" value={summary?.safeCount ?? 0} icon={ShieldCheck} tone="emerald" />
        <KpiCard title="Moderate Risk" value={summary?.moderateRiskCount ?? 0} icon={ShieldAlert} tone="amber" />
        <KpiCard title="Expiring Soon" value={summary?.expiringSoonCount ?? 0} icon={ArrowDownRight} tone="rose" />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
          <h3 className="text-xl font-semibold text-white">Risk Distribution</h3>
          <div className="mt-4 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskDistribution} dataKey="value" nameKey="risk" innerRadius={60} outerRadius={110} paddingAngle={4}>
                  {riskDistribution.map((entry, index) => <Cell key={entry.risk} fill={pieColors[index % pieColors.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
          <h3 className="text-xl font-semibold text-white">Monthly Trend</h3>
          <div className="mt-4 h-80">
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
      </div>

      <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
        <h3 className="text-xl font-semibold text-white">Inventory Volume</h3>
        <div className="mt-4 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthlyTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="month" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Bar dataKey="addedItems" fill="#16A34A" radius={[10, 10, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
