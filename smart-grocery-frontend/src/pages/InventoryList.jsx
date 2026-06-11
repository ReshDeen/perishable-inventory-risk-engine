import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Pencil, ShieldAlert, Trash2 } from "lucide-react";
import api from "../services/api";
import RiskBadge from "../components/ui/RiskBadge";
import Loader from "../components/ui/Loader";
import { useToast } from "../context/ToastContext";

export default function InventoryList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [risk, setRisk] = useState("");
  const toast = useToast();
  const navigate = useNavigate();

  const loadItems = async () => {
    setLoading(true);
    try {
      const response = await api.get("/inventory", {
        params: { search: search || undefined, risk: risk || undefined },
      });
      setItems(response.data);
    } catch (error) {
      toast?.pushToast(error.response?.data?.message || "Failed to load inventory.", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, [risk]);

  const removeItem = async (id) => {
    if (!window.confirm("Delete this item?")) return;
    try {
      await api.delete(`/inventory/${id}`);
      toast?.pushToast("Inventory item deleted.");
      loadItems();
    } catch (error) {
      toast?.pushToast("Could not delete item.", "error");
    }
  };

  if (loading) return <Loader label="Loading inventory..." />;

  return (
    <div className="space-y-6 text-slate-100">
      <div className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">Inventory List</h1>
          <p className="text-sm text-slate-400">Search, filter, update, and predict risk for each item.</p>
        </div>
        <Link to="/app/inventory/add" className="rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-400">Add Item</Link>
      </div>

      <div className="grid gap-4 md:grid-cols-[1fr_220px_140px]">
        <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-emerald-400" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by name" />
        <select className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 outline-none focus:border-emerald-400" value={risk} onChange={(e) => setRisk(e.target.value)}>
          <option value="">All Risk Levels</option>
          <option value="High Risk">High Risk</option>
          <option value="Moderate Risk">Moderate Risk</option>
          <option value="Safe">Safe</option>
        </select>
        <button onClick={loadItems} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 font-semibold text-white hover:border-emerald-400/30">Filter</button>
      </div>

      <div className="grid gap-4">
        {items.map((item) => (
          <div key={item._id} className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-xl">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <h3 className="text-xl font-semibold text-white">{item.name}</h3>
                  <RiskBadge value={item.riskPrediction} />
                </div>
                <p className="mt-2 text-sm text-slate-400">{item.category} · {item.quantity} {item.unit} · Expiry {new Date(item.expiryDate).toLocaleDateString()}</p>
                <p className="mt-2 text-sm text-slate-300">Action: {item.recommendedAction || "Monitor"}</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <button onClick={() => navigate(`/app/inventory/edit/${item._id}`)} className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white hover:border-emerald-400/30"><Pencil size={16} /> Edit</button>
                <button onClick={() => navigate("/app/prediction", { state: { item } })} className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white hover:border-emerald-400/30"><ShieldAlert size={16} /> Predict</button>
                <button onClick={() => removeItem(item._id)} className="inline-flex items-center gap-2 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm font-semibold text-rose-200 hover:bg-rose-500/20"><Trash2 size={16} /> Delete</button>
              </div>
            </div>
          </div>
        ))}
        {!items.length ? <p className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center text-slate-300">No inventory items available.</p> : null}
      </div>
    </div>
  );
}
