import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user } = useAuth();

  return (
    <div className="space-y-6 text-slate-100">
      <div>
        <h1 className="text-2xl font-semibold text-white">Profile</h1>
        <p className="text-sm text-slate-400">Account information for P.I.R.E. access.</p>
      </div>
      <div className="max-w-2xl rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl">
        <div className="space-y-3 text-sm text-slate-300">
          <p>Name: {user?.name}</p>
          <p>Email: {user?.email}</p>
          <p>Role: {user?.role || "manager"}</p>
          <p>Platform: P.I.R.E. – Predict. Prevent. Preserve.</p>
        </div>
      </div>
    </div>
  );
}
