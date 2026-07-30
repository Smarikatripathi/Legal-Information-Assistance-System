import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Scale, Eye, EyeOff } from "lucide-react";
import { loginFetch, googleOAuthLogin } from "../services/authService";
import { toast } from "react-toastify";

const Login = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [googleScriptLoaded, setGoogleScriptLoaded] = useState(false);

  // Load Google Identity Services script
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => {
      setGoogleScriptLoaded(true);
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

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
      toast.success("Welcome back!", { toastId: "login-success" });
      navigate("/dashboard");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Login failed. Please try again."
      );
    }
  };

  const handleGoogleLogin = () => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId) {
      setError("Google OAuth is not configured. Please add VITE_GOOGLE_CLIENT_ID to your environment.");
      return;
    }

    // Redirect to Google OAuth using Django allauth
    const redirectUri = `${window.location.origin}/auth/callback/google/`;
    const scope = "email profile";
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&scope=${encodeURIComponent(scope)}`;
    
    window.location.href = authUrl;
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-50 px-4 py-8 sm:py-10">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-[#084FF4]/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-[#2563EB]/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xl shadow-slate-200/50 sm:p-6 md:p-8">
          {/* Logo */}
          <div className="mb-8 text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[#2563EB]/10 sm:h-16 sm:w-16">
              <Scale className="h-7 w-7 text-[#2563EB] sm:h-8 sm:w-8" />
            </div>

            <h1 className="mt-5 text-2xl font-bold text-slate-900 sm:text-3xl">
              Welcome
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Sign in to continue to{" "}
              <span className="font-semibold text-[#084FF4]">
                Legal AI
              </span>
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-5 rounded-xl border border-accent/20 bg-accent/10 px-4 py-3 text-sm font-medium text-accent">
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

              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className="input pr-12"
                  minLength={6}
                  required
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-3 flex items-center text-slate-500 transition hover:text-[#084FF4]"
                  aria-label={
                    showPassword ? "Hide password" : "Show password"
                  }
                >
                  {showPassword ? (
                    <EyeOff size={20} />
                  ) : (
                    <Eye size={20} />
                  )}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="
                w-full
                rounded-xl
                bg-[#084FF4]
                py-3
                sm:py-3.5
                text-sm
                sm:text-base
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

          {/* Google Login */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={!googleScriptLoaded}
            className="w-full flex items-center justify-center gap-3 rounded-lg border border-slate-300 bg-white px-6 py-3 text-slate-700 transition hover:bg-slate-50 hover:border-slate-400 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span className="font-medium">Continue with Google</span>
          </button>

          {/* Signup */}
          <p className="mt-6 text-center text-sm text-slate-500">
            Don't have an account?{" "}
            <Link
              to="/signup"
              className="font-semibold text-accent transition hover:underline"
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