import { useState } from "react";
import { Link } from "react-router-dom";
import { Mail, ArrowLeft, Scale } from "lucide-react";
import { toast } from "react-toastify";
import { forgotPassword } from "../services/authService";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      await forgotPassword(email);

      toast.success(
        "If an account exists, a password reset link has been sent."
      );

      setEmail("");
    } catch (err) {
      toast.error(
        err.response?.data?.detail || "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-white px-6">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -right-40 h-112 w-md rounded-full bg-[#084FF4]/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-112 w-md rounded-full bg-[#C30A1C]/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md animate-fade-in">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-2xl">
          {/* Logo */}
          <div className="mb-8 flex flex-col items-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#C30A1C] text-white shadow-lg">
              <Scale size={30} />
            </div>

            <h1 className="text-3xl font-bold text-slate-900">
              Forgot Password
            </h1>

            <p className="mt-2 text-center text-slate-500">
              Enter your email and we'll send you a password reset link.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Email Address
              </label>

              <div className="relative">
                <Mail
                  size={18}
                  className="absolute top-1/2 left-4 -translate-y-1/2 text-slate-400"
                />

                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full rounded-xl border border-slate-300 py-3 pr-4 pl-11 transition focus:border-[#084FF4] focus:ring-4 focus:ring-[#084FF4]/15 focus:outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[#084FF4] py-3.5 font-semibold text-white transition hover:bg-[#063fd1] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? "Sending..." : "Send Reset Link"}
            </button>
          </form>

          <Link
            to="/login"
            className="mt-8 flex items-center justify-center gap-2 text-sm font-medium text-[#084FF4] transition hover:text-[#063fd1]"
          >
            <ArrowLeft size={18} />
            Back to Login
          </Link>
        </div>
      </div>
    </main>
  );
};

export default ForgotPassword;