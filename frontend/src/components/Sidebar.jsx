import {
  Scale,
  MessageSquarePlus,
  History,
  Users,
  User,
  LogOut,
} from "lucide-react";

import Button from "./Button";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Sidebar = ({
  sidebarOpen,
  setSidebarOpen,
  messages,
  setMessages,
  conversationId,
  setConversationId,
}) => {
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const navigate = useNavigate();

  const handleLogoutClick = () => {
    setShowLogoutModal(true);
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);
  };

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    setMessages([]);
    setConversationId(null);
    setSidebarOpen(false);
    navigate("/");
  };

  const handleProfile = () =>{
    navigate("/dashboard/profile");
  }

  return (
    <>
      {sidebarOpen && (
        <div
          className="
            fixed
            inset-0
            bg-black/40
            z-40
            lg:hidden
          "
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed
          top-0
          left-0
          h-screen
          w-72
          lg:w-80
          bg-white/95
          backdrop-blur-md
          border-r
          border-border
          z-50
          flex
          flex-col
          transition-transform
          duration-300
          ease-in-out

          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}

          lg:translate-x-0
          lg:static
          lg:flex
        `}
      >
        {/* Logo */}

        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-4">
            <div
              className="
              h-14
              w-14
              rounded-2xl
              gradient-primary
              flex
              items-center
              justify-center
              text-white
            "
            >
              <Scale size={28} />
            </div>

            <div>
              <button onClick={handleNewChat}>
                <h1 className="font-bold text-lg">Legal Assist</h1>

                <p className="text-sm text-muted-foreground">Nepal Legal AI</p>
              </button>
            </div>
          </div>
        </div>

        {/* New Chat */}

        <div className="p-4">
          <Button
            onClick={handleNewChat}
            variant="gradient"
            size="lg"
            className="w-full flex items-center justify-center gap-3"
          >
            <MessageSquarePlus size={18} />
            <span>New Chat</span>
          </Button>
        </div>

        {/* History */}

        <div className="flex-1 px-4 overflow-y-auto">
          <p className="text-xs uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
            <History size={14} />
            Recent Chats
          </p>

          <div className="space-y-2">
            <button className="sidebar-link w-full text-left">
              Contract Law
            </button>

            <button className="sidebar-link w-full text-left">
              Property Rights
            </button>

            <button className="sidebar-link w-full text-left">
              Employment Law
            </button>
          </div>
        </div>

        {/* Footer */}

        <div className="border-t border-border p-4 space-y-2">
          <button className="sidebar-link w-full">
            <Users size={18} />
            Lawyers Directory
          </button>

          <button onClick={handleProfile} className="sidebar-link w-full">
            <User size={18} />
            Profile
          </button>

          <button onClick={handleLogoutClick} className="sidebar-link w-full">
            <LogOut size={18} />
            Logout
          </button>
        </div>

      
      </aside>
        {showLogoutModal && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-100">
            <div className="bg-white rounded-xl p-6 w-sm shadow-lg text-center">
             

              <p className="text-sm text-foreground mb-6">
                Are you sure you want to logout?
              </p>

              <div className="flex gap-15 justify-center">
                <Button
                  onClick={() => setShowLogoutModal(false)}
                  className="  rounded-lg border"
                >
                  Cancel
                </Button>

                <Button
                  onClick={handleLogout}
                  variant="gradient"
                  className=" rounded-lg  text-white" size="md"
                >
                  Logout
                </Button>
              </div>
            </div>
          </div>
        )}
    </>
  );
};

export default Sidebar;
