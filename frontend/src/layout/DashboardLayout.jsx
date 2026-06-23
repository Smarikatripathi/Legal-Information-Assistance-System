"use client";

import { useState } from "react";
import { Menu } from "lucide-react";
import { Outlet } from "react-router-dom";

import Sidebar from "../components/Sidebar";

const DashboardLayout = ({
  messages,
  setMessages,
  conversationId,
  setConversationId,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <main className="flex flex-col h-screen overflow-hidden bg-background">

      {/* HEADER (fixed) */}
      <header className="fixed top-0 left-0 right-0 z-40 h-14 border-b border-border bg-white/70 backdrop-blur-md flex items-center justify-between px-4 md:px-6">

        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden absolute left-2 top-1/2 -translate-y-1/2 p-2"
        >
          <Menu size={24} />
        </button>

        <div>
          <h2 className="font-semibold ml-10 lg:ml-0">
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

      {/* SIDEBAR */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        messages={messages}
        setMessages={setMessages}
        conversationId={conversationId}
        setConversationId={setConversationId}
      />

      {/* CONTENT AREA */}
      <section className="flex-1 overflow-hidden pt-14 h-[calc(100vh-3.5rem)]">
        <Outlet
          context={{
            messages,
            setMessages,
            conversationId,
            setConversationId,
          }}
        />
      </section>

    </main>
  );
};

export default DashboardLayout;