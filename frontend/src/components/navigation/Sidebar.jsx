import {
  History,
  LogOut,
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
  sidebarOpen,
  setSidebarOpen,

  messages,
  setMessages,

  conversationId,
  setConversationId,

  conversations,
  historyLoading,
  loadConversations,
}) => {
  const navigate = useNavigate();

  const menuRef = useRef(null);

  const [menuOpen, setMenuOpen] = useState(null);

  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [selectedConversation, setSelectedConversation] = useState(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

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
    setSidebarOpen(false);

    navigate("/dashboard");
  };

  const handleConversationClick = async (conversation) => {
    try {
      const data = await getConversation(conversation.id);

      setConversationId(conversation.id);

      setMessages(data.messages);

      setSidebarOpen(false);
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
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
      fixed
      top-0
      left-0
      z-50
      flex
      h-full
      w-80
      flex-col
      border-r
      border-slate-400/40
      bg-gray-300
      transition-transform
      duration-300
      ease-in-out

      ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}

      lg:relative
      lg:top-0
      lg:h-full
      lg:translate-x-0
      lg:shrink-0
    `}
      >
        {/* New Chat */}

        <div className="border-b border-slate-400/30 bg-gray-300 p-5">
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

        {/* Conversation History */}

        <div className="flex min-h-0 flex-1 flex-col">
          <div className="flex items-center gap-2 px-5 pt-5 pb-3">
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
                      ? "border-l-4 border-[#C30A1C] bg-[#C30A1C]/5"
                      : "hover:bg-white"
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
                    right-2
                    top-2
                    rounded-lg
                    p-1.5
                    opacity-0
                    transition-all
                    duration-200
                    group-hover:opacity-100
                    hover:bg-slate-200
                  "
                    >
                      <MoreHorizontal size={17} />
                    </button>

                    {menuOpen === conversation.id && (
                      <div
                        ref={menuRef}
                        className="
                      absolute
                      right-2
                      top-11
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

        {/* Footer */}

        <div className="border-t border-slate-400/30 bg-gray-300 p-3">
          <button
            onClick={() => {
              setSidebarOpen(false);
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
