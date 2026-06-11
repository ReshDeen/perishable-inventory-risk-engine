export default function Loader({ label = "Loading..." }) {
  return (
    <div className="flex items-center justify-center rounded-3xl border border-white/10 bg-white/5 p-10 text-sm text-slate-300">
      <div className="mr-3 h-4 w-4 animate-spin rounded-full border-2 border-emerald-400 border-t-transparent" />
      {label}
    </div>
  );
}
