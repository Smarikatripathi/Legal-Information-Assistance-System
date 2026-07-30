import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { googleOAuthLogin } from "../services/authService";
import { toast } from "react-toastify";

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get("code");
      const error = searchParams.get("error");

      if (error) {
        setError(error);
        setLoading(false);
        return;
      }

      if (!code) {
        setError("No authorization code received from Google.");
        setLoading(false);
        return;
      }

      // Add retry logic for temporary failures
      const maxRetries = 3;
      const retryDelay = 1000; // 1 second
      let lastError = null;

      for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
          // Send the authorization code to backend
          await googleOAuthLogin(code);
          toast.success("Logged in with Google successfully!");
          navigate("/dashboard");
          return; // Success, exit the function
        } catch (err) {
          lastError = err;
          // Only retry on server errors (500) or network errors
          const isRetryable = 
            !err.response || 
            err.response?.status >= 500 ||
            err.code === 'ERR_NETWORK' ||
            err.message?.includes('Network Error');

          if (isRetryable && attempt < maxRetries - 1) {
            // Wait before retrying (keep loading state true)
            await new Promise(resolve => setTimeout(resolve, retryDelay));
            continue;
          }

          // If it's not retryable or we've exhausted retries, show error
          setError(
            err.response?.data?.detail || "Google login failed. Please try again."
          );
          setLoading(false);
          return;
        }
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-[#2563EB] border-t-transparent mx-auto" />
          <p className="text-slate-600">Signing in with Google...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
        <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl">
          <div className="mb-6 rounded-xl border border-accent/20 bg-accent/10 px-4 py-3 text-sm font-medium text-accent">
            {error}
          </div>
          <button
            onClick={() => navigate("/login")}
            className="w-full rounded-xl bg-[#084FF4] py-3 text-sm font-semibold text-white transition-all hover:bg-[#063fd1]"
          >
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default OAuthCallback;
