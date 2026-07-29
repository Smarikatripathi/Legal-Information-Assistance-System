import { SendHorizontal, Paperclip, Mic } from "lucide-react";

const ChatInput = ({
  value,
  onChange,
  onSend,
  disabled = false,
}) => {
  return (
    <div
      className="
  group
  flex
  items-center
  gap-3
  rounded-[20px]
  border
  border-slate-200
  bg-white
  px-4
  py-4
  shadow-sm
  transition-all
  duration-200
  hover:border-slate-300
  focus-within:border-[#2563EB]
  focus-within:shadow-md
"
      style={{ minHeight: '72px' }}
    >
      {/* Attachment Icon */}
      <button
        className="flex h-10 w-10 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
        aria-label="Attach file"
      >
        <Paperclip size={20} />
      </button>

      {/* Microphone Icon */}
      <button
        className="flex h-10 w-10 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
        aria-label="Voice input"
      >
        <Mic size={20} />
      </button>

      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSend();
          }
        }}
        placeholder="Ask anything about Nepal's laws..."
        className="
          flex-1
          bg-transparent
          px-2
          py-2
          text-base
          text-slate-700
          placeholder:text-slate-400
          outline-none
        "
      />

      <button
        onClick={onSend}
        disabled={!value.trim()}
        className="
          flex
          h-12
          w-12
          shrink-0
          items-center
          justify-center
          rounded-full
          bg-[#2563EB]
          text-white
          shadow-sm

          transition-all
          duration-200

          hover:bg-[#1D4ED8]
          hover:scale-105
          hover:shadow-md

          active:scale-95

          disabled:bg-slate-300
          disabled:text-slate-500
          disabled:cursor-not-allowed
          disabled:hover:scale-100
          disabled:hover:shadow-sm
        "
      >
        <SendHorizontal size={20} />
      </button>
    </div>
  );
};

export default ChatInput;