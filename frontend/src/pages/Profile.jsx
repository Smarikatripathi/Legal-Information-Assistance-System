import { useState, useEffect } from "react";
import { getProfile } from "../services/authService";

const Profile = () => {
  const [profile, setProfile] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
  });

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

  return (
    <div className="p-6 md:p-8 max-w-4xl mx-auto">
      {/* Header */}

      <div className="dashboard-card p-8 mb-6">
        <h1 className="text-3xl font-bold text-primary mb-2">My Profile</h1>

        <p className="text-muted-foreground">
          Manage your account information and security settings.
        </p>
      </div>

      {/* Profile Information */}

      <div className="dashboard-card p-8 mb-6">
        <h2 className="text-xl font-semibold text-primary mb-6">
          Profile Information
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block mb-2 text-sm font-medium">First Name</label>

            <input
              type="text"
              value={profile.first_name}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  first_name: e.target.value,
                })
              }
              className="
                w-full
                border
                border-border
                rounded-xl
                px-4
                py-3
                focus:outline-none
                focus:ring-2
                focus:ring-primary
              "
            />
          </div>

          <div>
            <label className="block mb-2 text-sm font-medium">Last Name</label>

            <input
              type="text"
              value={profile.last_name}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  last_name: e.target.value,
                })
              }
              className="
                w-full
                border
                border-border
                rounded-xl
                px-4
                py-3
                focus:outline-none
                focus:ring-2
                focus:ring-primary
              "
            />
          </div>
        </div>

        <div className="mt-6">
          <label className="block mb-2 text-sm font-medium">Username</label>

          <input
            type="text"
            name="username"
            autoComplete="new-username"
            value={profile.username}
            onChange={(e) =>
              setProfile({
                ...profile,
                username: e.target.value,
              })
            }
            className="
              w-full
              border
              border-border
              rounded-xl
              px-4
              py-3
              focus:outline-none
              focus:ring-2
              focus:ring-primary
            "
          />
        </div>

        <div className="mt-6">
          <label className="block mb-2 text-sm font-medium">Email</label>

          <input
            type="email"
            value={profile.email}
            readOnly
            className="
              w-full
              border
              border-border
              rounded-xl
              px-4
              py-3
              bg-gray-100
              cursor-not-allowed
            "
          />
        </div>

        <button
          className="
            mt-8
            px-6
            py-3
            rounded-xl
            gradient-primary
            text-white
            font-medium
          "
        >
          Save Changes
        </button>
      </div>

      {/* Security */}

      <div className="dashboard-card p-8">
        <h2 className="text-xl font-semibold text-accent mb-6">
          Change Password
        </h2>

        <div className="space-y-5">
          <div>
            <label className="block mb-2 text-sm font-medium">
              Current Password
            </label>

            <input
              type="password"
              className="
                w-full
                border
                border-border
                rounded-xl
                px-4
                py-3
                focus:outline-none
                focus:ring-2
                focus:ring-accent
              "
            />
          </div>

          <div>
            <label className="block mb-2 text-sm font-medium">
              New Password
            </label>

            <input
              type="password"
              className="
                w-full
                border
                border-border
                rounded-xl
                px-4
                py-3
                focus:outline-none
                focus:ring-2
                focus:ring-accent
              "
            />
          </div>

          <button
            className="
              px-6
              py-3
              rounded-xl
              bg-accent
              text-white
              font-medium
            "
          >
            Update Password
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;
