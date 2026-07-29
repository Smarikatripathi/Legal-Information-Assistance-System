import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { Lock, Mail, User, Save } from "lucide-react";
import { toast } from "react-toastify";

import { updateProfile, changePassword } from "../services/authService";

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
  const { user, setUser } = useOutletContext();

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

  const [profileError, setProfileError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  useEffect(() => {
    if (!user) return;

    setProfile({
      username: user.username || "",
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      email: user.email || "",
    });
  }, [user]);

  const initial =
    profile.first_name?.charAt(0).toUpperCase() ||
    profile.username?.charAt(0).toUpperCase() ||
    "U";

  const displayName =
    `${profile.first_name} ${profile.last_name}`.trim() || profile.username;

  const handleProfileSubmit = async (e) => {
    e.preventDefault();

    setProfileLoading(true);
    setProfileError("");

    try {
      const data = await updateProfile({
        first_name: profile.first_name,
        last_name: profile.last_name,
        username: profile.username,
      });

      const updatedUser = {
        ...user,
        ...data,
      };

      setUser(updatedUser);

      setProfile({
        username: updatedUser.username || "",
        first_name: updatedUser.first_name || "",
        last_name: updatedUser.last_name || "",
        email: updatedUser.email || "",
      });

      toast.success("Profile updated successfully.");
    } catch (error) {
      setProfileError(getErrorMessage(error, "Failed to update profile."));
    } finally {
      setProfileLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();

    setPasswordLoading(true);
    setPasswordError("");

    try {
      await changePassword(
        passwordForm.currentPassword,
        passwordForm.newPassword,
      );

      setPasswordForm({
        currentPassword: "",
        newPassword: "",
      });

      toast.success("Password updated successfully.");
    } catch (error) {
      setPasswordError(getErrorMessage(error, "Failed to update password."));
    } finally {
      setPasswordLoading(false);
    }
  };

  return (
    <div className="h-full overflow-y-auto bg-slate-50">
      <div className="mx-auto max-w-5xl px-5 py-8">
        {/* Profile Header */}

        <div className="mb-8 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex flex-col items-center text-center">
            <div className="mb-5 flex h-24 w-24 items-center justify-center rounded-full bg-[#084FF4] text-4xl font-bold text-white shadow-lg">
              {initial}
            </div>

            <h1 className="text-3xl font-bold text-slate-900">{displayName}</h1>

            <p className="mt-2 text-slate-500">{profile.email}</p>
          </div>
        </div>

        {/* Personal Information */}

        <form
          onSubmit={handleProfileSubmit}
          className="mb-8 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm"
        >
          <div className="mb-8 flex items-center gap-3">
            <div className="rounded-xl bg-[#084FF4]/10 p-3">
              <User className="h-5 w-5 text-[#084FF4]" />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-slate-900">
                Personal Information
              </h2>

              <p className="text-sm text-slate-500">
                Update your account details.
              </p>
            </div>
          </div>

          {profileError && (
            <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {profileError}
            </div>
          )}

          <div className="grid gap-5 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
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
                className="input"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
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
                className="input"
              />
            </div>

            {/* Username */}

            <div className="md:col-span-2">
              <label className="mb-2 block text-sm font-semibold text-slate-700">
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
                className="input"
              />
            </div>

            {/* Email */}

            <div className="md:col-span-2">
              <label className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
                <Mail size={16} />
                Email Address
              </label>

              <input
                type="email"
                value={profile.email}
                readOnly
                className="
                  input
                  cursor-not-allowed
                  bg-slate-100
                  text-slate-500
                "
              />
            </div>

                        {/* Username */}

            <div className="md:col-span-2">

              <label className="mb-2 block text-sm font-semibold text-slate-700">
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
                className="input"
              />

            </div>


            {/* Email */}

            <div className="md:col-span-2">

              <label className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
                <Mail size={16} />
                Email Address
              </label>

              <input
                type="email"
                value={profile.email}
                readOnly
                className="
                  input
                  cursor-not-allowed
                  bg-slate-100
                  text-slate-500
                "
              />

            </div>


          </div>

          {/* Save Button */}

          <button
            type="submit"
            disabled={profileLoading}
            className="
              mt-8
              flex
              items-center
              justify-center
              gap-2
              rounded-xl
              bg-[#084FF4]
              px-6
              py-3
              font-semibold
              text-white
              transition-all
              duration-300
              hover:bg-[#063fd1]
              hover:shadow-lg
              hover:shadow-[#084FF4]/20
              active:scale-95
              disabled:cursor-not-allowed
              disabled:opacity-60
            "
          >
            <Save size={18} />

            {profileLoading ? "Saving..." : "Save Changes"}
          </button>


        </form>

        {/* Security Section */}

        <form
          onSubmit={handlePasswordSubmit}
          className="
            rounded-3xl
            border
            border-slate-200
            bg-white
            p-8
            shadow-sm
          "
        >
          <div className="mb-8 flex items-center gap-3">
            <div className="rounded-xl bg-[#C30A1C]/10 p-3">
              <Lock className="h-5 w-5 text-[#C30A1C]" />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-slate-900">Security</h2>

              <p className="text-sm text-slate-500">
                Update your password and keep your account secure.
              </p>
            </div>
          </div>

          {passwordError && (
            <div
              className="
                mb-6
                rounded-xl
                border
                border-red-200
                bg-red-50
                px-4
                py-3
                text-sm
                text-red-700
              "
            >
              {passwordError}

            </div>

          )}



          <div className="space-y-5">
            {/* Current Password */}

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
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
                placeholder="Enter current password"
                className="input"
                required
              />

            </div>

            {/* New Password */}

            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-700">
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
                placeholder="Enter new password"
                className="input"
                minLength={8}
                required
              />

            </div>
          </div>

          <button
            type="submit"
            disabled={passwordLoading}
            className="
              mt-8
              rounded-xl
              bg-[#C30A1C]
              px-6
              py-3
              font-semibold
              text-white
              transition-all
              duration-300
              hover:bg-[#a50817]
              hover:shadow-lg
              hover:shadow-[#C30A1C]/20
              active:scale-95
              disabled:cursor-not-allowed
              disabled:opacity-60
            "
          >
            {passwordLoading ? "Updating..." : "Update Password"}
          </button>
        </form>



      </div>

    </div>
  );
};


export default Profile;