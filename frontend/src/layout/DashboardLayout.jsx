"use client"

import { useState } from "react";
import { Menu } from "lucide-react";

import Sidebar from "../components/Sidebar";

const DashboardLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  return (
    <main className="flex min-h-screen bg-background">
      {/* Mobile Hamburger */}

      <button
        onClick={() => setSidebarOpen(true)}
        className="
          lg:hidden
          fixed
          top-0.5
          left-4
          z-50
          p-2
          rounded-lg
          bg-transparent
        "
      >
        <Menu size={24} />
      </button>

      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />

      <section className="flex-1 overflow-hidden">
        {children}
      </section>
    </main>
  );
};

export default DashboardLayout;