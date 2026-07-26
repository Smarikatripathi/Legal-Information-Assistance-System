import { SendHorizontal } from "lucide-react";

const ChatInput = ({
  value,
  onChange,
  onSend,
  disabled = false,
}) => {
  return (
    <div className="dashboard-card p-2 flex items-center gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !disabled) {
            onSend();
          }
        }}
        placeholder="Ask a legal question..."
        disabled={disabled}
        className="
          flex-1
          px-4
          py-3
          outline-none
          bg-transparent
          disabled:opacity-50
          disabled:cursor-not-allowed
        "
      />

      <button
        onClick={onSend}
        disabled={disabled}
        className="
          gradient-primary
          text-white
          p-3
          rounded-xl
          hover:scale-105
          transition-all
          duration-200
          disabled:opacity-50
          disabled:cursor-not-allowed
          disabled:hover:scale-100
        "
      >
        <SendHorizontal size={20} />
      </button>
    </div>
  );
};

export default ChatInput;