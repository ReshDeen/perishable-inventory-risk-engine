import { NavLink } from "react-router-dom";
import { Bell, LayoutDashboard, PlusCircle, PieChart, Package, FileSpreadsheet, User, ShieldAlert, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/app/inventory", label: "Inventory", icon: Package },
  { to: "/app/inventory/add", label: "Add Inventory", icon: PlusCircle },
  { to: "/app/prediction", label: "Prediction", icon: ShieldAlert },
  { to: "/app/analytics", label: "Analytics", icon: PieChart },
  { to: "/app/alerts", label: "Alerts", icon: Bell },
  { to: "/app/profile", label: "Profile", icon: User },
  { to: "/app/export", label: "Export Center", icon: FileSpreadsheet },
];

export default function Sidebar() {
  const { logout, user } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-80 border-r border-white/10 bg-slate-950/95 px-5 py-6 backdrop-blur-xl lg:flex lg:flex-col">
      <div className="mb-8 rounded-3xl border border-emerald-500/20 bg-gradient-to-br from-emerald-500/20 to-teal-500/10 p-5">
        <p className="text-xs uppercase tracking-[0.35em] text-emerald-300/80">P.I.R.E.</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Perishable Intelligence Platform</h1>
        <p className="mt-2 text-sm text-slate-300">Predict. Prevent. Preserve.</p>
        <p className="mt-4 text-xs text-slate-400">Signed in as {user?.name || "User"}</p>
      </div>

      <nav className="flex-1 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                  isActive
                    ? "bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30"
                    : "text-slate-300 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              <Icon size={18} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <button
        onClick={logout}
        className="mt-6 flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-slate-200 transition hover:border-emerald-500/30 hover:bg-emerald-500/10"
      >
        <LogOut size={18} />
        Logout
      </button>
    </aside>
  );
}
