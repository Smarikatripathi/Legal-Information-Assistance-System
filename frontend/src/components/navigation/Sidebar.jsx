import {
  History,
  Home,
  LogOut,
  MapPin,
  Menu,
  MessageSquarePlus,
  MoreHorizontal,
  Trash2,
  Users,
} from "lucide-react";

import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import Button from "../ui/Button";

import {
  deleteConversation,
  getConversation,
} from "../../services/chatService";

const Sidebar = ({
  sidebarState,
  setSidebarState,
  sidebarWidth,
  setSidebarWidth,

  messages,
  setMessages,

  conversationId,
  setConversationId,

  conversations,
  historyLoading,
  loadConversations,
  currentPage,
  // Filter props for Lawyers page
  filters,
  setFilters,
  availableLocations,
}) => {
  const navigate = useNavigate();

  const menuRef = useRef(null);
  const sidebarRef = useRef(null);
  const resizeRef = useRef(null);

  const [menuOpen, setMenuOpen] = useState(null);
  const [isResizing, setIsResizing] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedConversation, setSelectedConversation] = useState(null);

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
  const [localFilters, setLocalFilters] = useState({
    location: "",
    practiceAreas: [],
    experience: "All",
  });

  // Use props if provided, otherwise use local state
  const activeFilters = filters || localFilters;
  const activeSetFilters = setFilters || setLocalFilters;

  // Pass filter state to parent when it changes
  useEffect(() => {
    if (setFilters) {
      setFilters(activeFilters);
    }
  }, [activeFilters, setFilters]);

  // Handle ESC key to close sidebar drawer on mobile
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape" && sidebarState !== 'hidden' && isMobile) {
        setSidebarState('hidden');
      }
    };

    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [sidebarState, isMobile, setSidebarState]);

  // Handle click outside to close sidebar drawer on mobile
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(null);
      }
      // Close drawer when clicking outside on mobile
      if (isMobile && sidebarState !== 'hidden' && 
          sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        setSidebarState('hidden');
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [sidebarState, isMobile, setSidebarState]);

  // Handle sidebar resizing
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return;
      
      const newWidth = e.clientX;
      if (newWidth >= 72 && newWidth <= 340) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, setSidebarWidth]);

  const handleResizeStart = (e) => {
    e.preventDefault();
    setIsResizing(true);
  };

  const formatDate = (date) => {
    const d = new Date(date);
    const now = new Date();

    const diff = Math.floor((now - d) / (1000 * 60 * 60 * 24));

    if (diff === 0) return "Today";
    if (diff === 1) return "Yesterday";
    if (diff < 7) return `${diff} days ago`;

    return d.toLocaleDateString();
  };

  const handleNewChat = () => {
    setMessages([]);
    setConversationId(null);

    navigate("/dashboard");
  };

  const handleConversationClick = async (conversation) => {
    try {
      const data = await getConversation(conversation.id);

      setConversationId(conversation.id);

      setMessages(data.messages);
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteClick = (conversation) => {
    setSelectedConversation(conversation);

    setShowDeleteModal(true);

    setMenuOpen(null);
  };

  const handleDeleteConversation = async () => {
    if (!selectedConversation) return;

    try {
      await deleteConversation(selectedConversation.id);

      if (selectedConversation.id === conversationId) {
        setConversationId(null);

        setMessages([]);
      }

      await loadConversations();

      setSelectedConversation(null);

      setShowDeleteModal(false);
    } catch (error) {
      console.error(error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    setConversationId(null);
    setMessages([]);

    navigate("/");
  };

  const handleLogoutClick = () => {
    setShowLogoutModal(true);
  };

  return (
    <>
      {/* Mobile/Tablet Overlay - z-index: 50 */}
      {sidebarState !== 'hidden' && isMobile && (
        <div
          className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarState('hidden')}
          aria-hidden="true"
        />
      )}

      {/* Mobile/Tablet Sidebar (Drawer) - z-index: 60 */}
      <aside
        ref={sidebarRef}
        style={{ zIndex: 60 }}
        className={`
          fixed
          top-0
          left-0
          flex
          h-[100dvh]
          flex-col
          border-r
          border-slate-200
          bg-white
          shadow-lg
          transition-all
          duration-300
          ease-in-out
          w-[280px]
          ${sidebarState !== 'hidden' && isMobile ? "translate-x-0" : "-translate-x-full"}
          lg:hidden
        `}
      >
        {/* Mobile/Tablet Content */}
        {currentPage === "lawyers" ? (
          <>
            {/* Filters Panel */}
            <div className="border-b border-slate-200 bg-white p-5 shrink-0">
              <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">
                Filters
              </h3>

              {/* Location Filter */}
              <div className="mb-5">
                <label className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
                  <MapPin size={16} />
                  Location
                </label>
                <select
                  value={activeFilters.location}
                  onChange={(e) => activeSetFilters({ ...activeFilters, location: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB]"
                >
                  <option value="">All Locations</option>
                  {availableLocations?.map((loc) => (
                    <option key={loc} value={loc}>
                      {loc}
                    </option>
                  ))}
                </select>
              </div>

              {/* Practice Area Filter */}
              <div className="mb-5">
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Practice Area
                </label>
                <div className="space-y-2">
                  {["Civil", "Criminal", "Family", "Property", "Corporate"].map((area) => (
                    <label key={area} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={activeFilters.practiceAreas.includes(area)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            activeSetFilters({
                              ...activeFilters,
                              practiceAreas: [...activeFilters.practiceAreas, area],
                            });
                          } else {
                            activeSetFilters({
                              ...activeFilters,
                              practiceAreas: activeFilters.practiceAreas.filter((a) => a !== area),
                            });
                          }
                        }}
                        className="h-4 w-4 rounded border-slate-300 text-[#2563EB] focus:ring-[#2563EB]"
                      />
                      <span className="text-sm text-slate-700">{area}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Experience Filter */}
              <div className="mb-5">
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Experience
                </label>
                <div className="space-y-2">
                  {["All", "0-2 years", "3-5 years", "5+ years"].map((exp) => (
                    <label key={exp} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="experience"
                        checked={activeFilters.experience === exp}
                        onChange={() => activeSetFilters({ ...activeFilters, experience: exp })}
                        className="h-4 w-4 border-slate-300 text-[#2563EB] focus:ring-[#2563EB]"
                      />
                      <span className="text-sm text-slate-700">{exp}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Reset Filters Button */}
              <button
                onClick={() => activeSetFilters({ location: "", practiceAreas: [], experience: "All" })}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition-all hover:bg-slate-50"
              >
                Reset Filters
              </button>
            </div>
          </>
        ) : (
          <>
            {/* New Chat */}
            <div className="border-b border-slate-400/30 bg-gray-300 p-5 shrink-0">
              <Button
                onClick={handleNewChat}
                className="
          flex
          w-full
          items-center
          justify-center
          gap-2
          rounded-xl
          bg-[#084FF4]
          py-3
          font-medium
          text-white
          transition-all
          hover:bg-[#063fd1]
        "
              >
                <MessageSquarePlus size={18} />
                <span>New Chat</span>
              </Button>
            </div>

            {/* Conversation History - Scrollable */}
            <div className="flex flex-col flex-1 overflow-hidden">
              <div className="flex items-center gap-2 px-5 pt-5 pb-3 shrink-0">
                <History size={15} className="text-slate-500" />

                <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
                  Recent Conversations
                </p>
              </div>

              <div className="flex-1 overflow-y-auto px-3 pb-4">
                {historyLoading ? (
                  <div className="py-12 text-center text-sm text-slate-500">
                    Loading conversations...
                  </div>
                ) : conversations.length === 0 ? (
                  <div className="flex h-full flex-col items-center justify-center px-6 text-center">
                    <History size={36} className="mb-4 text-slate-300" />

                    <h3 className="text-base font-semibold text-slate-800">
                      No conversations yet
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      Start a new chat and your conversation history will appear
                      here automatically.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {conversations.map((conversation) => (
                      <div
                        key={conversation.id}
                        className={`
                  group
                  relative
                  overflow-visible
                  rounded-xl
                  transition-all

                  ${
                    conversation.id === conversationId
                      ? "border-l-4 border-[#2563EB] bg-[#2563EB]/5"
                      : "hover:bg-slate-50"
                  }
                `}
                      >
                        <button
                          onClick={() => handleConversationClick(conversation)}
                          className="
                    w-full
                    px-4
                    py-3.5
                    pr-12
                    text-left
                  "
                        >
                          <p className="truncate text-sm font-semibold text-slate-800">
                            {conversation.title}
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            {formatDate(conversation.updated_at)}
                          </p>
                        </button>

                        <button
                          onClick={() =>
                            setMenuOpen(
                              menuOpen === conversation.id ? null : conversation.id,
                            )
                          }
                          className="
                    absolute
                    right-3
                    top-1/2
                    -translate-y-1/2
                    rounded-lg
                    p-1.5
                    opacity-0
                    transition-all
                    duration-200
                    group-hover:opacity-100
                    hover:bg-slate-200
                  "
                        >
                          <MoreHorizontal size={16} />
                        </button>

                        {menuOpen === conversation.id && (
                          <div
                            ref={menuRef}
                            className="
                      absolute
                      right-0
                      top-full
                      mt-1
                      z-50
                      w-48
                      overflow-hidden
                      rounded-xl
                      border
                      border-slate-200
                      bg-white
                      py-1
                      shadow-xl
                    "
                          >
                            <button
                              onClick={() => handleDeleteClick(conversation)}
                              className="
                        flex
                        w-full
                        items-center
                        gap-3
                        px-4
                        py-3
                        text-left
                        text-sm
                        text-red-600
                        transition-colors
                        hover:bg-red-50
                      "
                            >
                              <Trash2 size={16} />
                              Delete conversation
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Footer - Fixed at bottom */}
        <div className="border-t border-slate-400/30 bg-gray-300 p-3 shrink-0">
          <button
            onClick={() => {
              setSidebarState('hidden');
              navigate("/dashboard/lawyers")
            }}
            className="sidebar-link w-full"
          >
            <Users size={18} />
            Lawyers Directory
          </button>

          <button
            onClick={handleLogoutClick}
            className="sidebar-link w-full text-red-600 hover:bg-red-50"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </aside>

      {/* Desktop/Laptop Sidebar (Static) - z-index: 30 */}
      <aside
        ref={sidebarRef}
        className={`
          hidden
          lg:flex
          flex-col
          border-r
          border-slate-200
          bg-white
          shadow-sm
          transition-all
          duration-300
          ease-in-out
          h-[100dvh]
          shrink-0
          z-30
          ${sidebarState === 'collapsed' ? 'w-[72px]' : 'w-[280px]'}
        `}
      >
          {/* Collapse Button */}
          <div className="border-b border-slate-200 bg-white px-3 py-2">
            <button
              onClick={() => setSidebarState(sidebarState === 'expanded' ? 'collapsed' : 'expanded')}
              className="w-full flex items-center justify-center rounded-lg p-2 transition hover:bg-slate-100"
              aria-label={sidebarState === 'collapsed' ? "Expand sidebar" : "Collapse sidebar"}
            >
              <Menu size={18} className="text-slate-600" />
            </button>
          </div>

          {/* New Chat Button - Hide on Lawyers page */}
          {currentPage !== "lawyers" && (
            <div className={`p-4 ${sidebarState === 'collapsed' ? 'px-2' : ''}`}>
              <Button
                onClick={handleNewChat}
                className="w-full rounded-xl bg-[#2563EB] py-3 font-medium text-white shadow-sm transition-all hover:bg-[#1D4ED8] hover:shadow-md"
              >
                <div className={`flex items-center ${sidebarState === 'collapsed' ? 'justify-center' : 'justify-center gap-2'}`}>
                  <MessageSquarePlus size={18} />
                  <span className={sidebarState === 'collapsed' ? 'hidden' : ''}>New Chat</span>
                </div>
              </Button>
            </div>
          )}

          {/* Show Filters on Lawyers page, otherwise show Chat components */}
          {currentPage === "lawyers" ? (
            <>
              {/* Filters Panel */}
              <div className={`border-b border-slate-200 bg-white p-5 ${sidebarState === 'collapsed' ? 'hidden' : ''}`}>
                <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">
                  Filters
                </h3>

                {/* Location Filter */}
                <div className="mb-5">
                  <label className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
                    <MapPin size={16} />
                    Location
                  </label>
                  <select
                    value={activeFilters.location}
                    onChange={(e) => activeSetFilters({ ...activeFilters, location: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB]"
                  >
                    <option value="">All Locations</option>
                    {availableLocations?.map((loc) => (
                      <option key={loc} value={loc}>
                        {loc}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Practice Area Filter */}
                <div className="mb-5">
                  <label className="mb-2 block text-sm font-semibold text-slate-700">
                    Practice Area
                  </label>
                  <div className="space-y-2">
                    {["Civil", "Criminal", "Family", "Property", "Corporate"].map((area) => (
                      <label key={area} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={activeFilters.practiceAreas.includes(area)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              activeSetFilters({
                                ...activeFilters,
                                practiceAreas: [...activeFilters.practiceAreas, area],
                              });
                            } else {
                              activeSetFilters({
                                ...activeFilters,
                                practiceAreas: activeFilters.practiceAreas.filter((a) => a !== area),
                              });
                            }
                          }}
                          className="h-4 w-4 rounded border-slate-300 text-[#2563EB] focus:ring-[#2563EB]"
                        />
                        <span className="text-sm text-slate-700">{area}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Experience Filter */}
                <div className="mb-5">
                  <label className="mb-2 block text-sm font-semibold text-slate-700">
                  Experience
                </label>
                <div className="space-y-2">
                  {["All", "0-2 years", "3-5 years", "5+ years"].map((exp) => (
                    <label key={exp} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="experience"
                        checked={activeFilters.experience === exp}
                        onChange={() => activeSetFilters({ ...activeFilters, experience: exp })}
                        className="h-4 w-4 border-slate-300 text-[#2563EB] focus:ring-[#2563EB]"
                      />
                      <span className="text-sm text-slate-700">{exp}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Reset Filters Button */}
              <button
                onClick={() => activeSetFilters({ location: "", practiceAreas: [], experience: "All" })}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition-all hover:bg-slate-50"
              >
                Reset Filters
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Conversation History - Scrollable */}
            <div className={`flex flex-col ${sidebarState === 'collapsed' ? 'hidden' : ''} flex-1 overflow-hidden`}>
              <div className="flex items-center gap-2 px-5 pt-5 pb-3 shrink-0">
                <History size={15} className="text-slate-500" />

                <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
                  Recent Conversations
                </p>
              </div>

              <div className="flex-1 overflow-y-auto px-3 pb-4">
                {historyLoading ? (
                  <div className="py-12 text-center text-sm text-slate-500">
                    Loading conversations...
                  </div>
                ) : conversations.length === 0 ? (
                  <div className="flex h-full flex-col items-center justify-center px-6 text-center">
                    <History size={36} className="mb-4 text-slate-300" />

                    <h3 className="text-base font-semibold text-slate-800">
                      No conversations yet
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      Start a new chat and your conversation history will appear
                      here automatically.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {conversations.map((conversation) => (
                      <div
                        key={conversation.id}
                        className={`
                  group
                  relative
                  overflow-visible
                  rounded-xl
                  transition-all

                  ${
                    conversation.id === conversationId
                      ? "border-l-4 border-[#2563EB] bg-[#2563EB]/5"
                      : "hover:bg-slate-50"
                  }
                `}
                      >
                        <button
                          onClick={() => handleConversationClick(conversation)}
                          className="
                    w-full
                    px-4
                    py-3.5
                    pr-12
                    text-left
                  "
                        >
                          <p className="truncate text-sm font-semibold text-slate-800">
                            {conversation.title}
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            {formatDate(conversation.updated_at)}
                          </p>
                        </button>

                        <button
                          onClick={() =>
                            setMenuOpen(
                              menuOpen === conversation.id ? null : conversation.id,
                            )
                          }
                          className="
                    absolute
                    right-3
                    top-1/2
                    -translate-y-1/2
                    rounded-lg
                    p-1.5
                    opacity-0
                    transition-all
                    duration-200
                    group-hover:opacity-100
                    hover:bg-slate-200
                  "
                        >
                          <MoreHorizontal size={16} />
                        </button>

                        {menuOpen === conversation.id && (
                          <div
                            ref={menuRef}
                            className="
                      absolute
                      right-0
                      top-full
                      mt-1
                      z-50
                      w-48
                      overflow-hidden
                      rounded-xl
                      border
                      border-slate-200
                      bg-white
                      py-1
                      shadow-xl
                    "
                          >
                            <button
                              onClick={() => handleDeleteClick(conversation)}
                              className="
                        flex
                        w-full
                        items-center
                        gap-3
                        px-4
                        py-3
                        text-left
                        text-sm
                        text-red-600
                        transition-colors
                        hover:bg-red-50
                      "
                            >
                              <Trash2 size={16} />
                              Delete conversation
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Footer - Fixed at bottom */}
        <div className={`border-t border-slate-200 bg-white p-3 shrink-0 ${sidebarState === 'collapsed' ? "px-2" : ""}`}>
          <button
            onClick={() => navigate("/dashboard")}
            className={`sidebar-link w-full ${sidebarState === 'collapsed' ? "justify-center" : ""}`}
            title="Dashboard"
          >
            <Home size={18} />
            <span className={sidebarState !== 'collapsed' ? "" : "hidden"}>Dashboard</span>
          </button>

          {currentPage !== "lawyers" && (
            <button
              onClick={() => navigate("/dashboard/lawyers")}
              className={`sidebar-link w-full ${sidebarState === 'collapsed' ? "justify-center" : ""}`}
              title="Lawyers Directory"
            >
              <Users size={18} />
              <span className={sidebarState !== 'collapsed' ? "" : "hidden"}>Lawyers Directory</span>
            </button>
          )}

          <button
            onClick={handleLogoutClick}
            className={`sidebar-link w-full text-red-600 hover:bg-red-50 ${sidebarState === 'collapsed' ? "justify-center" : ""}`}
            title="Logout"
          >
            <LogOut size={18} />
            <span className={sidebarState !== 'collapsed' ? "" : "hidden"}>Logout</span>
          </button>
        </div>
      </aside>

      {/* Delete Conversation Modal */}

      {showDeleteModal && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            {/* Header */}

            <div className="mb-6 flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-100">
                <Trash2 size={26} className="text-[#C30A1C]" />
              </div>

              <div>
                <h2 className="text-xl font-semibold text-slate-900">
                  Delete Conversation
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  This action cannot be undone.
                </p>
              </div>
            </div>

            {/* Actions */}

            <div className="flex justify-end gap-3">
              <Button
                onClick={() => {
                  setShowDeleteModal(false);
                  setSelectedConversation(null);
                }}
                className="
                  rounded-xl
                  bg-[#084FF4]
                  text-white
                  hover:bg-[#063fd1]
                "
              >
                Cancel
              </Button>

              <Button
                onClick={handleDeleteConversation}
                className="
                  rounded-xl
                  bg-[#C30A1C]
                  text-white
                  hover:bg-[#a70917]
                "
              >
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Logout Modal */}

      {showLogoutModal && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
            {/* Header */}

            <div className="mb-6 flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#C30A1C]/10">
                <LogOut size={26} className="text-[#C30A1C]" />
              </div>

              <div>
                <h2 className="text-xl font-semibold text-slate-900">Logout</h2>

                <p className="mt-1 text-sm text-slate-500">
                  Are you sure you want to logout?
                </p>
              </div>
            </div>

            {/* Actions */}

            <div className="flex justify-end gap-3">
              <Button
                onClick={() => setShowLogoutModal(false)}
                className="
                  rounded-xl
                  bg-[#084FF4]
                  text-white
                  hover:bg-[#063fd1]
                "
              >
                Cancel
              </Button>

              <Button
                onClick={handleLogout}
                className="
                  rounded-xl
                  bg-[#C30A1C]
                  text-white
                  hover:bg-[#a70917]
                "
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
