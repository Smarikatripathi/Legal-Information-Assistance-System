import {
  Scale,
  MessageSquarePlus,
  History,
  Users,
  User,
  LogOut,
  Search,
  Trash2,
  Edit2,
  X,
} from "lucide-react";

import Button from "./Button";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { conversationService } from "../services/conversationService";

const Sidebar = ({
  sidebarOpen,
  setSidebarOpen,
  setMessages,
  setConversationId,
  currentConversationId,
  refreshConversations,
}) => {
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    loadConversations();
  }, [refreshConversations]);

  const loadConversations = async () => {
    try {
      const data = await conversationService.listConversations(searchQuery);
      setConversations(data);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    }
  };

  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      loadConversations();
    }, 300);
    return () => clearTimeout(delayedSearch);
  }, [searchQuery]);

  const handleLogoutClick = () => {
    setShowLogoutModal(true);
  };

  const handleNewChat = async () => {
    setSidebarOpen(false);
    setMessages([]);
    setConversationId(null);
    navigate("/dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    setMessages([]);
    setConversationId(null);
    setSidebarOpen(false);
    navigate("/");
  };

  const handleProfile = () => {
    setSidebarOpen(false);
    navigate("/dashboard/profile");
  };

  const handleConversationClick = (conversation) => {
    setSidebarOpen(false);
    setConversationId(conversation.id);
    navigate(`/dashboard/${conversation.id}`);
  };

  const handleDeleteConversation = async (e, conversationId) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this conversation?")) {
      try {
        await conversationService.deleteConversation(conversationId);
        loadConversations();
        if (currentConversationId === conversationId) {
          handleNewChat();
        }
      } catch (error) {
        console.error("Failed to delete conversation:", error);
      }
    }
  };

  const handleStartEdit = (e, conversation) => {
    e.stopPropagation();
    setEditingId(conversation.id);
    setEditTitle(conversation.title);
  };

  const handleSaveEdit = async (e, conversationId) => {
    e.stopPropagation();
    try {
      await conversationService.updateConversation(conversationId, { title: editTitle });
      setEditingId(null);
      loadConversations();
    } catch (error) {
      console.error("Failed to update conversation:", error);
    }
  };

  const handleCancelEdit = (e) => {
    e.stopPropagation();
    setEditingId(null);
    setEditTitle("");
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const groupConversations = (convs) => {
    const groups = {
      today: [],
      yesterday: [],
      previous7days: [],
      older: [],
    };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);

    convs.forEach((conv) => {
      const convDate = new Date(conv.updated_at);
      if (convDate >= today) {
        groups.today.push(conv);
      } else if (convDate >= yesterday) {
        groups.yesterday.push(conv);
      } else if (convDate >= weekAgo) {
        groups.previous7days.push(conv);
      } else {
        groups.older.push(conv);
      }
    });

    return groups;
  };

  const groupedConversations = groupConversations(conversations);

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
    top-14
    left-0
    h-[calc(100vh-3.5rem)]
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
    lg:relative
    lg:top-0
    lg:h-full
    lg:shrink-0
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

        {/* Search */}

        <div className="px-4 pb-4">
          <div className="relative">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
            />
          </div>
        </div>

        {/* History */}

        <div className="flex-1 px-4 overflow-y-auto">
          <p className="text-xs uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
            <History size={14} />
            Recent Chats
          </p>

          {groupedConversations.today.length > 0 && (
            <>
              <p className="text-xs text-muted-foreground mb-2">Today</p>
              {groupedConversations.today.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isActive={conv.id === currentConversationId}
                  onClick={() => handleConversationClick(conv)}
                  onDelete={(e) => handleDeleteConversation(e, conv.id)}
                  onEdit={(e) => handleStartEdit(e, conv)}
                  isEditing={editingId === conv.id}
                  editTitle={editTitle}
                  onEditChange={setEditTitle}
                  onSaveEdit={(e) => handleSaveEdit(e, conv.id)}
                  onCancelEdit={handleCancelEdit}
                  formatTime={formatTime}
                />
              ))}
            </>
          )}

          {groupedConversations.yesterday.length > 0 && (
            <>
              <p className="text-xs text-muted-foreground mb-2 mt-4">Yesterday</p>
              {groupedConversations.yesterday.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isActive={conv.id === currentConversationId}
                  onClick={() => handleConversationClick(conv)}
                  onDelete={(e) => handleDeleteConversation(e, conv.id)}
                  onEdit={(e) => handleStartEdit(e, conv)}
                  isEditing={editingId === conv.id}
                  editTitle={editTitle}
                  onEditChange={setEditTitle}
                  onSaveEdit={(e) => handleSaveEdit(e, conv.id)}
                  onCancelEdit={handleCancelEdit}
                  formatTime={formatTime}
                />
              ))}
            </>
          )}

          {groupedConversations.previous7days.length > 0 && (
            <>
              <p className="text-xs text-muted-foreground mb-2 mt-4">Previous 7 Days</p>
              {groupedConversations.previous7days.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isActive={conv.id === currentConversationId}
                  onClick={() => handleConversationClick(conv)}
                  onDelete={(e) => handleDeleteConversation(e, conv.id)}
                  onEdit={(e) => handleStartEdit(e, conv)}
                  isEditing={editingId === conv.id}
                  editTitle={editTitle}
                  onEditChange={setEditTitle}
                  onSaveEdit={(e) => handleSaveEdit(e, conv.id)}
                  onCancelEdit={handleCancelEdit}
                  formatTime={formatTime}
                />
              ))}
            </>
          )}

          {groupedConversations.older.length > 0 && (
            <>
              <p className="text-xs text-muted-foreground mb-2 mt-4">Older</p>
              {groupedConversations.older.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isActive={conv.id === currentConversationId}
                  onClick={() => handleConversationClick(conv)}
                  onDelete={(e) => handleDeleteConversation(e, conv.id)}
                  onEdit={(e) => handleStartEdit(e, conv)}
                  isEditing={editingId === conv.id}
                  editTitle={editTitle}
                  onEditChange={setEditTitle}
                  onSaveEdit={(e) => handleSaveEdit(e, conv.id)}
                  onCancelEdit={handleCancelEdit}
                  formatTime={formatTime}
                />
              ))}
            </>
          )}

          {conversations.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-8">
              No conversations yet
            </p>
          )}
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
                className=" rounded-lg  text-white"
                size="md"
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

const ConversationItem = ({
  conversation,
  isActive,
  onClick,
  onDelete,
  onEdit,
  isEditing,
  editTitle,
  onEditChange,
  onSaveEdit,
  onCancelEdit,
  formatTime,
}) => {
  return (
    <div
      className={`
        relative group p-3 rounded-lg mb-2 cursor-pointer transition-all
        ${isActive ? "bg-primary/10 border border-primary/20" : "hover:bg-muted"}
      `}
      onClick={onClick}
    >
      {isEditing ? (
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => onEditChange(e.target.value)}
            className="flex-1 px-2 py-1 text-sm rounded border border-border focus:outline-none focus:ring-2 focus:ring-primary/20"
            onClick={(e) => e.stopPropagation()}
          />
          <button
            onClick={onSaveEdit}
            className="p-1 hover:bg-primary/20 rounded"
            title="Save"
          >
            <Scale size={14} />
          </button>
          <button
            onClick={onCancelEdit}
            className="p-1 hover:bg-destructive/20 rounded"
            title="Cancel"
          >
            <X size={14} />
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{conversation.title}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {formatTime(conversation.updated_at)}
              </p>
            </div>
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={onEdit}
                className="p-1 hover:bg-primary/20 rounded"
                title="Rename"
              >
                <Edit2 size={14} />
              </button>
              <button
                onClick={onDelete}
                className="p-1 hover:bg-destructive/20 rounded"
                title="Delete"
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Sidebar;
