import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../components/Button";
import { loginFetch } from "../services/authService";

const Login = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    try {
      const data = await loginFetch(form.email, form.password);
      console.log("SUCCESS", data);
      navigate("/dashboard");
    } catch (err) {
      console.log("ERROR", err.response?.data);
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-md animate-fade-in">
        <div className="auth-card p-8">
          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary">Legal Assist</h1>

            <p className="text-muted-foreground mt-2">Sign in to continue</p>
          </div>

          {/* FORM */}
          {error && (
            <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-400">
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* EMAIL */}
            <div className="form-group">
              <label className="text-sm font-medium">Email</label>

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

            {/* PASSWORD */}
            <div className="form-group">
              <label className="text-sm font-medium">Password</label>

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

            {/* BUTTON */}
            <Button
              type="submit"
              variant="gradient"
              size="lg"
              className="w-full"
            >
              Log In
            </Button>
          </form>

          {/* LINK */}
          <p className="text-center text-sm text-muted-foreground mt-6">
            Don't have an account?{" "}
            <Link
              to="/signup"
              className="text-accent font-semibold hover:underline"
            >
              Sign Up
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
};

export default Login;
