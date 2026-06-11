export default function RiskBadge({ value }) {
  const styles = {
    "High Risk": "bg-rose-500/15 text-rose-300 border-rose-500/30",
    "Moderate Risk": "bg-amber-500/15 text-amber-300 border-amber-500/30",
    Safe: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  };

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${styles[value] || styles.Safe}`}>
      {value || "Safe"}
    </span>
  );
}
