import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Scale } from "lucide-react";
import { loginFetch } from "../services/authService";
import { toast } from "react-toastify";

const Login = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    try {
      await loginFetch(form.email, form.password);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    }
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-50 px-6">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-[#084FF4]/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-[#C30A1C]/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50">
          {/* Logo */}
          <div className="mb-8 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[#C30A1C]/10">
              <Scale className="h-8 w-8 text-[#C30A1C]" />
            </div>

            <h1 className="mt-5 text-3xl font-bold text-slate-900">Welcome</h1>

            <p className="mt-2 text-slate-500">
              Sign in to continue to{" "}
              <span className="font-semibold text-[#084FF4]">Legal AI</span>
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-5 rounded-xl border border-[#C30A1C]/20 bg-[#C30A1C]/10 px-4 py-3 text-sm font-medium text-[#C30A1C]">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
                Email Address
              </label>

              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="you@example.com"
                className="input"
                required
              />
            </div>

            {/* Password */}
            <div>
              <div className="mb-2 flex items-center justify-between">
                <label className="text-sm font-semibold text-slate-700">
                  Password
                </label>

                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-[#084FF4] transition hover:underline"
                >
                  Forgot Password?
                </Link>
              </div>

              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="input"
                minLength={6}
                required
              />
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="
                w-full
                rounded-xl
                bg-[#084FF4]
                py-3.5
                text-base
                font-semibold
                text-white
                transition-all
                duration-300
                hover:bg-[#063fd1]
                hover:shadow-lg
                hover:shadow-[#084FF4]/20
                active:scale-95
              "
            >
              Log In
            </button>
          </form>

          {/* Divider */}
          <div className="my-7 flex items-center">
            <div className="h-px flex-1 bg-slate-200" />
            <span className="px-4 text-sm text-slate-400">OR</span>
            <div className="h-px flex-1 bg-slate-200" />
          </div>

          {/* Signup */}
          <p className="text-center text-sm text-slate-500">
            Don't have an account?{" "}
            <Link
              to="/signup"
              className="font-semibold text-[#C30A1C] transition hover:underline"
            >
              Create Account
            </Link>
          </p>

          {/* Back */}
          <div className="mt-6 text-center">
            <Link
              to="/"
              className="text-sm font-medium text-slate-500 transition hover:text-[#084FF4]"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
};

export default Login;
