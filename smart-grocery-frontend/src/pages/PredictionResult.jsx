import { useLocation, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../services/api";
import Loader from "../components/ui/Loader";
import RiskBadge from "../components/ui/RiskBadge";
import { useToast } from "../context/ToastContext";

export default function PredictionResult() {
  const location = useLocation();
  const item = location.state?.item;
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (!item) return;
    const run = async () => {
      setLoading(true);
      try {
        const payload = {
          inventoryItemId: item._id,
          quantity: item.quantity,
          consumptionRate: item.consumptionRate,
          daysToExpiry: Math.max(0, Math.ceil((new Date(item.expiryDate).getTime() - Date.now()) / 86400000)),
          pricePerUnit: item.pricePerUnit,
        };
        const response = await api.post("/predict", payload);
        setResult(response.data);
        toast?.pushToast("Prediction generated successfully.");
      } catch {
        toast?.pushToast("Prediction request failed.", "error");
      } finally {
        setLoading(false);
      }
    };

    run();
  }, [item]);

  return (
    <div className="space-y-6 text-slate-100">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl">
        <h1 className="text-2xl font-semibold text-white">Prediction Result</h1>
        <p className="mt-2 text-sm text-slate-400">AI-generated spoilage risk for the selected inventory item.</p>
      </div>

      {!item ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center text-slate-300">
          No item selected. Go to the <Link className="text-emerald-300" to="/app/inventory">inventory list</Link> and click Predict.
        </div>
      ) : loading ? (
        <Loader label="Running XGBoost prediction..." />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-white">Item Details</h3>
            <div className="mt-4 space-y-3 text-sm text-slate-300">
              <p>Name: {item.name}</p>
              <p>Category: {item.category}</p>
              <p>Quantity: {item.quantity} {item.unit}</p>
              <p>Expiry Date: {new Date(item.expiryDate).toLocaleDateString()}</p>
              <p>Consumption Rate: {item.consumptionRate}</p>
            </div>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-white">Risk Prediction</h3>
            <div className="mt-6 space-y-4">
              <RiskBadge value={result?.riskPrediction || item.riskPrediction} />
              <p className="text-4xl font-black text-white">{Math.round((result?.confidenceScore || item.confidenceScore || 0) * 100)}%</p>
              <p className="text-slate-300">{result?.recommendedAction || item.recommendedAction || "Monitor stock levels."}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
