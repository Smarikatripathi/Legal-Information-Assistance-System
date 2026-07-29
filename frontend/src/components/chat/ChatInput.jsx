import { SendHorizontal } from "lucide-react";

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
  rounded-2xl
  border
  border-slate-200
  bg-[#F5F7FA]
  px-3
  py-3
  transition-colors
  duration-200
  hover:border-slate-400
"
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
          text-[15px]
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
          h-11
          w-11
          shrink-0
          items-center
          justify-center
          rounded-xl
          bg-[#084FF4]
          text-white

          transition-all
          duration-200

          hover:bg-[#063fd1]
          hover:scale-105

          group-focus-within:scale-105
          group-focus-within:bg-[#063fd1]

          active:scale-95

          disabled:bg-slate-300
          disabled:text-slate-500
          disabled:cursor-not-allowed
          disabled:hover:scale-100
          disabled:group-focus-within:scale-100
        "
      >
        <SendHorizontal size={18} />
      </button>
    </div>
  );
};

export default ChatInput;