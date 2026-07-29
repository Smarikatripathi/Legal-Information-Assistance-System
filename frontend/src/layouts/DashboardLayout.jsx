import { useState, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";

import Sidebar from "../components/navigation/Sidebar";
import DashboardNavbar from "../components/navigation/DashboardNavbar";
import { getProfile } from "../services/authService";

const DashboardLayout = ({
  messages,
  setMessages,
  conversationId,
  setConversationId,
  conversations,
  setConversations,
  historyLoading,
  loadConversations,
}) => {
  // Three-state sidebar: 'expanded' | 'collapsed' | 'hidden'
  const [sidebarState, setSidebarState] = useState(() => {
    const saved = localStorage.getItem("sidebarState");
    return saved || 'expanded';
  });
  
  // Resizable sidebar width (for expanded state)
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    const saved = localStorage.getItem("sidebarWidth");
    return saved ? parseInt(saved) : 280;
  });
  
  const [isMobile, setIsMobile] = useState(false);
  
  const [user, setUser] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Track mobile/desktop state
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Filter state for Lawyers page
  const [filters, setFilters] = useState({
    location: "",
    practiceAreas: [],
    experience: "All",
  });

  const [availableLocations, setAvailableLocations] = useState([]);

  const currentPage = location.pathname === "/dashboard"
    ? "dashboard"
    : location.pathname.startsWith("/dashboard/lawyers")
    ? "lawyers"
    : location.pathname === "/dashboard/profile"
    ? "profile"
    : "dashboard";

  // Persist sidebar state to localStorage
  useEffect(() => {
    localStorage.setItem("sidebarState", sidebarState);
  }, [sidebarState]);

  // Persist sidebar width to localStorage
  useEffect(() => {
    localStorage.setItem("sidebarWidth", sidebarWidth.toString());
  }, [sidebarWidth]);

  // Close sidebar drawer when navigating on mobile
  useEffect(() => {
    if (isMobile) {
      setSidebarState('hidden');
    }
  }, [location.pathname, isMobile]);

  // Handle hamburger button click
  const handleMenuClick = () => {
    if (isMobile) {
      // Mobile: toggle drawer
      setSidebarState(prev => prev === 'hidden' ? 'expanded' : 'hidden');
    } else {
      // Desktop: toggle collapse/expand
      setSidebarState(prev => prev === 'expanded' ? 'collapsed' : 'expanded');
    }
  };

  // Prevent body scroll when sidebar drawer is open on mobile
  useEffect(() => {
    const isDrawerOpen = isMobile && sidebarState !== 'hidden';
    
    if (isDrawerOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [sidebarState, isMobile]);

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

  return (
    <div className="flex h-[100dvh] overflow-hidden bg-slate-50">
      {/* Sidebar - z-index: 30 */}
      <Sidebar
        sidebarState={sidebarState}
        setSidebarState={setSidebarState}
        sidebarWidth={sidebarWidth}
        setSidebarWidth={setSidebarWidth}

        messages={messages}
        setMessages={setMessages}

        conversationId={conversationId}
        setConversationId={setConversationId}

        conversations={conversations}
        historyLoading={historyLoading}
        loadConversations={loadConversations}
        currentPage={currentPage}
        // Filter props for Lawyers page
        filters={filters}
        setFilters={setFilters}
        availableLocations={availableLocations}
      />
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Navbar - z-index: 40, fixed height 64px */}
        <DashboardNavbar 
          user={user}
          className="shrink-0"
        />

        {/* Main Content */}
        <main className="flex h-full flex-1 flex-col overflow-hidden bg-slate-50">
          <Outlet
            context={{
              user,
              setUser,

              messages,
              setMessages,

              conversationId,
              setConversationId,

              conversations,
              loadConversations,
              // Filter props for Lawyers page
              filters,
              setFilters,
              availableLocations,
              setAvailableLocations,
            }}
          />
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
