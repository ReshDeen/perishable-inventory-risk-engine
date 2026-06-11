import { useState } from "react";
import api from "../services/api";
import { useToast } from "../context/ToastContext";

export default function ExportPage() {
  const [loadingCsv, setLoadingCsv] = useState(false);
  const [loadingPdf, setLoadingPdf] = useState(false);
  const toast = useToast();

  const download = async (endpoint, filename, setLoading) => {
    setLoading(true);
    try {
      const response = await api.get(endpoint, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast?.pushToast(`${filename} downloaded.`);
    } catch {
      toast?.pushToast("Export failed.", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 text-slate-100">
      <div>
        <h1 className="text-2xl font-semibold text-white">Export Center</h1>
        <p className="text-sm text-slate-400">Download inventory and analytics reports for submission or viva demo.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <button onClick={() => download("/export/inventory/csv", "inventory-export.csv", setLoadingCsv)} disabled={loadingCsv} className="rounded-3xl border border-white/10 bg-white/5 p-6 text-left transition hover:border-emerald-400/30">
          <p className="text-lg font-semibold text-white">Export Inventory CSV</p>
          <p className="mt-2 text-sm text-slate-400">Current inventory snapshot in spreadsheet format.</p>
        </button>
        <button onClick={() => download("/export/analytics/pdf", "analytics-report.pdf", setLoadingPdf)} disabled={loadingPdf} className="rounded-3xl border border-white/10 bg-white/5 p-6 text-left transition hover:border-emerald-400/30">
          <p className="text-lg font-semibold text-white">Export Analytics PDF</p>
          <p className="mt-2 text-sm text-slate-400">Presentation-ready analytics summary report.</p>
        </button>
      </div>
    </div>
  );
}
