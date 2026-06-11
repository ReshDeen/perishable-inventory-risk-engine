import { CheckCircle2, AlertTriangle, Info } from "lucide-react";
import { useToast } from "../../context/ToastContext";

export default function ToastViewport() {
  const toastContext = useToast();

  if (!toastContext) return null;
  const { toasts } = toastContext;

  const icons = {
    success: <CheckCircle2 size={18} />,
    error: <AlertTriangle size={18} />,
    info: <Info size={18} />,
  };

  return (
    <div className="fixed right-4 top-4 z-50 space-y-3">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`w-80 rounded-2xl border px-4 py-3 shadow-2xl backdrop-blur ${
            toast.type === "error"
              ? "border-rose-500/30 bg-rose-500/15 text-rose-100"
              : toast.type === "info"
              ? "border-sky-500/30 bg-sky-500/15 text-sky-100"
              : "border-emerald-500/30 bg-emerald-500/15 text-emerald-100"
          }`}
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5">{icons[toast.type] || icons.success}</div>
            <p className="text-sm font-medium">{toast.message}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
