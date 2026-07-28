import { Link } from "react-router-dom";
import { Scale, Home } from "lucide-react";

const NotFound = () => {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-50 px-6">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-[#084FF4]/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-[#C30A1C]/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-xl shadow-slate-200/50">
          {/* Logo */}
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[#C30A1C]/10">
            <Scale className="h-8 w-8 text-[#C30A1C]" />
          </div>

          <h1 className="mt-6 text-6xl font-extrabold text-slate-900">
            404
          </h1>

          <h2 className="mt-3 text-2xl font-bold text-slate-800">
            Page Not Found
          </h2>

          <p className="mt-3 text-slate-500">
            Sorry, the page you're looking for doesn't exist or may have been
            moved.
          </p>

          <Link
            to="/"
            className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#084FF4] px-6 py-3.5 font-semibold text-white transition-all duration-300 hover:bg-[#063fd1] hover:shadow-lg hover:shadow-[#084FF4]/20 active:scale-95"
          >
            <Home size={18} />
            Back to Home
          </Link>

          <p className="mt-6 text-sm text-slate-400">
            Legal Information Assistance System
          </p>
        </div>
      </div>
    </main>
  );
};

export default NotFound;