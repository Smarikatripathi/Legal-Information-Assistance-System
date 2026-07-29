import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Scale, Eye, EyeOff } from "lucide-react";
import { signup } from "../services/authService";
import { toast } from "react-toastify";

const Signup = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      await signup({
        first_name: form.first_name,
        last_name: form.last_name,
        username: form.username,
        email: form.email,
        password: form.password,
      });

      toast.success("Account created successfully!");
      navigate("/dashboard");
    } catch (err) {
      const backendError =
        err.response?.data?.password?.[0] ||
        err.response?.data?.username?.[0] ||
        err.response?.data?.email?.[0] ||
        err.response?.data?.detail ||
        "Failed to create account.";

      setError(backendError);
    }
  };

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-50 px-4 py-8 sm:py-10">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-[#084FF4]/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-[#C30A1C]/10 blur-3xl" />
      </div>

      <div className="relative w-full max-w-2xl">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-xl shadow-slate-200/60 sm:p-6 md:p-8">
          {/* Logo */}
          <div className="mb-8 text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[#C30A1C]/10 sm:h-16 sm:w-16">
              <Scale className="h-7 w-7 text-[#C30A1C] sm:h-8 sm:w-8" />
            </div>

            <h1 className="mt-5 text-2xl font-bold text-slate-900 sm:text-3xl">
              Create Account
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Join{" "}
              <span className="font-semibold text-[#084FF4]">Legal AI</span>{" "}
              today
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
            {/* First + Last */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  First Name
                </label>

                <input
                  type="text"
                  name="first_name"
                  value={form.first_name}
                  onChange={handleChange}
                  className="input"
                  placeholder="John"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Last Name
                </label>

                <input
                  type="text"
                  name="last_name"
                  value={form.last_name}
                  onChange={handleChange}
                  className="input"
                  placeholder="Doe"
                />
              </div>
            </div>

            {/* Username + Email */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Username
                </label>

                <input
                  type="text"
                  name="username"
                  value={form.username}
                  onChange={handleChange}
                  className="input"
                  placeholder="johndoe"
                  required
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Email Address
                </label>

                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleChange}
                  className="input"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            {/* Password + Confirm */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Password
                </label>

                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    className="input pr-12"
                    placeholder="••••••••"
                    minLength={8}
                    required
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-3 flex items-center text-slate-500 hover:text-[#084FF4]"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Confirm Password
                </label>

                <div className="relative">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={form.confirmPassword}
                    onChange={handleChange}
                    className="input pr-12"
                    placeholder="••••••••"
                    minLength={8}
                    required
                  />

                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-3 flex items-center text-slate-500 hover:text-[#084FF4]"
                  >
                    {showConfirmPassword ? (
                      <EyeOff size={20} />
                    ) : (
                      <Eye size={20} />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Button */}
            <button
              type="submit"
              className="
                mt-2
                w-full
                rounded-xl
                bg-[#084FF4]
                py-3
                sm:py-3.5
                text-sm
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
              Create Account
            </button>
          </form>

          {/* Footer */}
          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-semibold text-[#C30A1C] hover:underline"
            >
              Log In
            </Link>
          </p>

          <div className="mt-4 text-center">
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

export default Signup;
