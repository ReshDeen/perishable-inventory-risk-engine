import { useEffect, useState } from "react";

const emptyForm = {
  name: "",
  category: "Vegetables",
  quantity: 0,
  unit: "kg",
  purchaseDate: "",
  expiryDate: "",
  pricePerUnit: 0,
  consumptionRate: 0,
};

export default function InventoryForm({ initialValue, onSubmit, loading = false, submitLabel = "Save Item" }) {
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (initialValue) {
      setForm({
        name: initialValue.name || "",
        category: initialValue.category || "Vegetables",
        quantity: initialValue.quantity ?? 0,
        unit: initialValue.unit || "kg",
        purchaseDate: initialValue.purchaseDate ? String(initialValue.purchaseDate).slice(0, 10) : "",
        expiryDate: initialValue.expiryDate ? String(initialValue.expiryDate).slice(0, 10) : "",
        pricePerUnit: initialValue.pricePerUnit ?? 0,
        consumptionRate: initialValue.consumptionRate ?? 0,
      });
    }
  }, [initialValue]);

  const handleChange = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  const submit = (event) => {
    event.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={submit} className="grid gap-4 rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl md:grid-cols-2">
      <input className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none focus:border-emerald-400" placeholder="Product name" value={form.name} onChange={(e) => handleChange("name", e.target.value)} />
      <select className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none focus:border-emerald-400" value={form.category} onChange={(e) => handleChange("category", e.target.value)}>
        <option>Vegetables</option>
        <option>Fruits</option>
        <option>Dairy</option>
        <option>Meat</option>
        <option>Bakery</option>
        <option>Seafood</option>
      </select>
      <input type="number" min="0" className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none focus:border-emerald-400" placeholder="Quantity" value={form.quantity} onChange={(e) => handleChange("quantity", Number(e.target.value))} />
      <input className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none focus:border-emerald-400" placeholder="Unit (kg, pcs)" value={form.unit} onChange={(e) => handleChange("unit", e.target.value)} />
      <input type="date" className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none focus:border-emerald-400" value={form.purchaseDate} onChange={(e) => handleChange("purchaseDate", e.target.value)} />
      <input type="date" className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none focus:border-emerald-400" value={form.expiryDate} onChange={(e) => handleChange("expiryDate", e.target.value)} />
      <input type="number" min="0" step="0.01" className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none focus:border-emerald-400" placeholder="Price per unit" value={form.pricePerUnit} onChange={(e) => handleChange("pricePerUnit", Number(e.target.value))} />
      <input type="number" min="0" step="0.01" className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 outline-none focus:border-emerald-400" placeholder="Consumption rate" value={form.consumptionRate} onChange={(e) => handleChange("consumptionRate", Number(e.target.value))} />
      <button disabled={loading} className="rounded-2xl bg-emerald-500 px-4 py-3 font-semibold text-white transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60 md:col-span-2">
        {loading ? "Processing..." : submitLabel}
      </button>
    </form>
  );
}
