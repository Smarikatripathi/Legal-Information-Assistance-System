import {
  Scale,
  MessageSquarePlus,
  History,
  Users,
  User,
  LogOut,
} from "lucide-react";

import Button from "./Button";

const Sidebar = ({sidebarOpen,setSidebarOpen}) => {
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
          onClick={() =>
            setSidebarOpen(false)
          }
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

          ${
            sidebarOpen
              ? "translate-x-0"
              : "-translate-x-full"
          }

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
            <h1 className="font-bold text-lg">
              Legal Assist
            </h1>

            <p className="text-sm text-muted-foreground">
              Nepal Legal AI
            </p>
          </div>
        </div>
      </div>

      {/* New Chat */}

      <div className="p-4">
        <Button
          variant="gradient"
          size="lg"
          className="w-full flex p-6  items-center"
        >
          <MessageSquarePlus size={18} className="mr-15"/>

          New Chat
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

        <button className="sidebar-link w-full">
          <User size={18} />
          Profile
        </button>

        <button className="sidebar-link w-full">
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
    </>
  );
};

export default Sidebar;