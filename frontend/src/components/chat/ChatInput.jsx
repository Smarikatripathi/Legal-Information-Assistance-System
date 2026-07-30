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
  rounded-xl
  border
  border-slate-200
  bg-white
  px-4
  py-1
  shadow-sm
  transition-all
  duration-200
  hover:border-slate-300
  focus-within:border-[#2563EB]
  focus-within:shadow-md
"
      style={{ minHeight: '72px' }}
    >

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

          hover:bg-primary
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