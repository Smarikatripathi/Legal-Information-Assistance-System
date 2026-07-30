import { Scale } from "lucide-react";
import { useNavigate } from "react-router-dom";

const DashboardNavbar = ({ user }) => {
  const navigate = useNavigate();

  const initial =
    user?.first_name?.charAt(0)?.toUpperCase() ||
    user?.username?.charAt(0)?.toUpperCase() ||
    "U";

  return (
    <header className="h-18 shrink-0 border-b border-slate-200 bg-white shadow-sm">
      <div className="flex h-full items-center justify-between px-6">
        {/* Left */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-3 transition hover:opacity-80"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#2563EB] shadow-sm">
              <Scale className="h-5 w-5 text-white" />
            </div>

            <div className="leading-tight text-left hidden sm:block">
              <h1 className="text-lg font-bold tracking-tight text-slate-900">
                Legal Assist
              </h1>
              <p className="text-xs text-slate-500">
                AI-Powered Legal Information System
              </p>
            </div>
          </button>
        </div>

        {/* Right */}
        <div className="flex items-center gap-3">
          {/* User Avatar */}
          <button
            onClick={() => navigate("/dashboard/profile")}
            className="relative group"
            aria-label="User profile"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#2563EB] text-base text-white shadow-sm transition-all duration-200 hover:scale-105 hover:shadow-md active:scale-95">
              {initial}
            </div>

            {/* Tooltip */}
            <div className="pointer-events-none absolute right-0 top-12 rounded-lg bg-slate-900 px-3 py-1.5 text-xs text-white opacity-0 transition duration-200 group-hover:opacity-100">
              Profile
            </div>
          </button>
        </div>
      </div>
    </header>
  );
};

export default DashboardNavbar;
