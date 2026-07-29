import { useState, useEffect } from "react";
import { Menu, Scale } from "lucide-react";
import { Outlet, useNavigate } from "react-router-dom";

import Sidebar from "../components/navigation/Sidebar";
import { getProfile } from "../services/authService";

const DashboardLayout = ({
  messages,
  setMessages,
  conversationId,
  setConversationId,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await getProfile();
        setUser(data);
      } catch (err) {
        console.error("Failed to load profile:", err);
      }
    };

    fetchProfile();
  }, []);

  const initial =
    user?.first_name?.charAt(0)?.toUpperCase() ||
    user?.username?.charAt(0)?.toUpperCase() ||
    "U";

  return (
    <div className="h-screen overflow-hidden bg-slate-50">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-40 h-16 border-b border-slate-200 bg-white/95 backdrop-blur-md">
        <div className="flex h-full items-center justify-between px-4 md:px-6">
          {/* Left */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded-lg p-2 transition hover:bg-slate-100 lg:hidden"
            >
              <Menu size={22} />
            </button>

            <div className="hidden md:flex h-10 w-10 items-center justify-center rounded-xl bg-[#C30A1C]/10">
              <Scale className="h-5 w-5 text-[#C30A1C]" />
            </div>

            <div>
              <h1 className="text-lg font-semibold text-slate-900">
                Legal Information Assistant
              </h1>

              <p className="text-sm text-slate-500">
                Nepal Legal Support Platform
              </p>
            </div>
          </div>

          {/* Right */}
          <div className="relative group">
            <button
              onClick={() => navigate("/dashboard/profile")}
              className="
                flex
                h-8
                w-8
                items-center
                justify-center
                rounded-full
                bg-[#1f5ae2]
                text-base
                text-white
                shadow-sm
                transition-all
                duration-200
                hover:scale-102
                hover:shadow-md
                active:scale-95
              "
            >
              {initial}
            </button>

            {/* Tooltip */}
            <div
              className="
                pointer-events-none
                absolute
                right-0
                top-12
                rounded-lg
                bg-slate-900
                px-3
                py-1.5
                text-xs
                text-white
                opacity-0
                transition
                duration-200
                group-hover:opacity-100
              "
            >
              Profile
            </div>
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="mt-16 flex h-[calc(100vh-4rem)]">
        <Sidebar
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          messages={messages}
          setMessages={setMessages}
          conversationId={conversationId}
          setConversationId={setConversationId}
        />

        <main className="flex-1 min-w-0 overflow-hidden bg-slate-50">
          <Outlet
            context={{
              user,
              setUser,

              messages,
              setMessages,

              conversationId,
              setConversationId,
            }}
          />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
