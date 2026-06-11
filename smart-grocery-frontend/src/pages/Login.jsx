import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/app/dashboard";

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
      toast?.pushToast("Login successful. Welcome to P.I.R.E.");
      navigate(from, { replace: true });
    } catch (error) {
      toast?.pushToast(error.response?.data?.message || "Login failed.", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 px-6 py-10 text-white">
      <div className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-7xl items-center">
        <div className="grid w-full gap-10 lg:grid-cols-2">
          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-xl">
            <p className="text-sm uppercase tracking-[0.35em] text-emerald-300/80">P.I.R.E.</p>
            <h1 className="mt-4 text-4xl font-black sm:text-5xl">Predict. Prevent. Preserve.</h1>
            <p className="mt-4 max-w-xl text-slate-300">Sign in to monitor risk, expiry alerts, inventory health, and analytics in one intelligent control center.</p>
          </div>

          <form onSubmit={submit} className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 shadow-2xl">
            <h2 className="text-2xl font-semibold">Login</h2>
            <div className="mt-6 space-y-4">
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-emerald-400" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              <input type="password" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-emerald-400" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
              <button disabled={loading} className="w-full rounded-2xl bg-emerald-500 px-4 py-3 font-semibold text-white transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60">{loading ? "Signing in..." : "Login"}</button>
            </div>
            <p className="mt-6 text-sm text-slate-300">New here? <Link className="text-emerald-300 hover:text-emerald-200" to="/register">Create an account</Link></p>
          </form>
        </div>
      </div>
    </div>
  );
}
