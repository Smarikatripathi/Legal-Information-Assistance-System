import { useState } from "react";
import { Menu } from "lucide-react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";

const DashboardLayout = ({
  messages,
  setMessages,
  conversationId,
  setConversationId,
  currentConversationId,
  refreshConversations,
  setRefreshConversations,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen overflow-hidden bg-background">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-40 h-14 border-b  border-border bg-white backdrop-blur-md flex items-center justify-between px-4 md:px-6">
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden absolute left-2 top-1/2 -translate-y-1/2 p-2"
        >
          <Menu size={24} />
        </button>

        <div>
          <h2 className="font-semibold ml-10 lg:ml-0 text-gradient">
            Legal Information Assistant
          </h2>
          <p className="text-sm text-muted-foreground ml-10 lg:ml-0">
            Nepal Legal Support Platform
          </p>
        </div>

        <div className="flex gap-2">
          <div className="h-3 w-3 rounded-full bg-accent" />
          <div className="h-3 w-3 rounded-full bg-primary" />
        </div>
      </header>

      {/* Main Area */}
      <div className="flex h-[calc(100vh-3.5rem)] mt-14">
        <Sidebar
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          messages={messages}
          setMessages={setMessages}
          conversationId={conversationId}
          setConversationId={setConversationId}
          currentConversationId={currentConversationId}
          refreshConversations={refreshConversations}
        />

        <main className="flex-1 min-w-0 h-full overflow-hidden">
          <Outlet
            context={{
              messages,
              setMessages,
              conversationId,
              setConversationId,
              currentConversationId,
              refreshConversations,
              setRefreshConversations,
            }}
          />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
