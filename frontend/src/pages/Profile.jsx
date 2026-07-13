import { useState, useEffect } from "react";
import {
  changePassword,
  getProfile,
  updateProfile,
} from "../services/authService";

const getErrorMessage = (error, fallback) => {
  const data = error.response?.data;

  if (typeof data?.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data?.detail)) {
    return data.detail.join(" ");
  }

  const firstFieldError = data && Object.values(data).flat()[0];
  return firstFieldError || fallback;
};

const Profile = () => {
  const [profile, setProfile] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
  });
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
  });
  const [profileLoading, setProfileLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [profileMessage, setProfileMessage] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [profileError, setProfileError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getProfile();

        setProfile({
          username: data.username || "",
          first_name: data.first_name || "",
          last_name: data.last_name || "",
          email: data.email || "",
        });
      } catch (error) {
        console.error("Failed to load profile:", error);
      }
    };

    fetchProfile();
  }, []);

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setProfileLoading(true);
    setProfileMessage("");
    setProfileError("");

    try {
      const data = await updateProfile({
        first_name: profile.first_name,
        last_name: profile.last_name,
        username: profile.username,
      });

      setProfile({
        username: data.username || "",
        first_name: data.first_name || "",
        last_name: data.last_name || "",
        email: data.email || profile.email,
      });
      setProfileMessage("Profile updated successfully.");
    } catch (error) {
      setProfileError(
        getErrorMessage(error, "Failed to update profile. Please try again.")
      );
    } finally {
      setProfileLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setPasswordLoading(true);
    setPasswordMessage("");
    setPasswordError("");

    try {
      await changePassword(
        passwordForm.currentPassword,
        passwordForm.newPassword
      );
      setPasswordForm({
        currentPassword: "",
        newPassword: "",
      });
      setPasswordMessage("Password updated successfully.");
    } catch (error) {
      setPasswordError(
        getErrorMessage(error, "Failed to update password. Please try again.")
      );
    } finally {
      setPasswordLoading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-6 md:p-8 max-w-4xl mx-auto">
        {/* Header */}
        <div className="dashboard-card p-8 mb-6">
          <h1 className="text-3xl font-bold text-primary mb-2">
            My Profile
          </h1>

          <p className="text-muted-foreground">
            Manage your account information and security settings.
          </p>
        </div>

        {/* Profile Information */}
        <form onSubmit={handleProfileSubmit} className="dashboard-card p-8 mb-6">
          <h2 className="text-xl font-semibold text-primary mb-6">
            Profile Information
          </h2>

          {profileMessage && (
            <div className="mb-4 rounded-xl border border-green-500/20 bg-green-500/10 p-3 text-sm text-green-700">
              {profileMessage}
            </div>
          )}

          {profileError && (
            <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-500">
              {profileError}
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block mb-2 text-sm font-medium">
                First Name
              </label>

              <input
                type="text"
                value={profile.first_name}
                onChange={(e) =>
                  setProfile({
                    ...profile,
                    first_name: e.target.value,
                  })
                }
                className="w-full border border-border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium">
                Last Name
              </label>

              <input
                type="text"
                value={profile.last_name}
                onChange={(e) =>
                  setProfile({
                    ...profile,
                    last_name: e.target.value,
                  })
                }
                className="w-full border border-border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div className="mt-6">
            <label className="block mb-2 text-sm font-medium">
              Username
            </label>

            <input
              type="text"
              value={profile.username}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  username: e.target.value,
                })
              }
              className="w-full border border-border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="mt-6">
            <label className="block mb-2 text-sm font-medium">
              Email
            </label>

            <input
              type="email"
              value={profile.email}
              readOnly
              className="w-full border border-border rounded-xl px-4 py-3 bg-gray-100 cursor-not-allowed"
            />
          </div>

          <button
            type="submit"
            disabled={profileLoading}
            className="mt-8 px-6 py-3 rounded-xl gradient-primary text-white font-medium disabled:cursor-not-allowed disabled:opacity-70"
          >
            {profileLoading ? "Saving..." : "Save Changes"}
          </button>
        </form>

        {/* Security */}
        <form onSubmit={handlePasswordSubmit} className="dashboard-card p-8">
          <h2 className="text-xl font-semibold text-accent mb-6">
            Change Password
          </h2>

          {passwordMessage && (
            <div className="mb-4 rounded-xl border border-green-500/20 bg-green-500/10 p-3 text-sm text-green-700">
              {passwordMessage}
            </div>
          )}

          {passwordError && (
            <div className="mb-4 rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-500">
              {passwordError}
            </div>
          )}

          <div className="space-y-5">
            <div>
              <label className="block mb-2 text-sm font-medium">
                Current Password
              </label>

              <input
                type="password"
                value={passwordForm.currentPassword}
                onChange={(e) =>
                  setPasswordForm({
                    ...passwordForm,
                    currentPassword: e.target.value,
                  })
                }
                className="w-full border border-border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-accent"
                required
              />
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium">
                New Password
              </label>

              <input
                type="password"
                value={passwordForm.newPassword}
                onChange={(e) =>
                  setPasswordForm({
                    ...passwordForm,
                    newPassword: e.target.value,
                  })
                }
                className="w-full border border-border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-accent"
                minLength={8}
                required
              />
            </div>

            <button
              type="submit"
              disabled={passwordLoading}
              className="px-6 py-3 rounded-xl gradient-primary text-white font-medium disabled:cursor-not-allowed disabled:opacity-70"
            >
              {passwordLoading ? "Updating..." : "Update Password"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Profile;
