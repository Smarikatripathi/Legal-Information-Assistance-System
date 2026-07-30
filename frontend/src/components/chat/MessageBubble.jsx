import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Scale } from "lucide-react";

const MessageBubble = ({ role, content }) => {
  const isUser = role === "user";

  return (
    <div className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}>
      {/* Small AI Label */}
      {!isUser && (
        <div className="mb-1 ml-2 flex items-center gap-1.5">
          <Scale size={12} className="text-accent" />

          <span className="text-xs font-medium text-slate-500">
            Legal Assist
          </span>
        </div>
      )}

      {/* User Label */}
      {isUser && (
        <span className="mb-1 mr-2 text-xs font-medium text-slate-500">
          You
        </span>
      )}

      {/* Bubble */}
      <div
        className={`
          max-w-[85%]
          rounded-2xl
          px-5
          pt-3
          shadow-sm

          ${
            isUser
              ? "bg-[#084FF4] text-white"
              : "border border-slate-200 bg-white text-slate-800"
          }
        `}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap leading-6">{content}</p>
        ) : (
          <div className="legal-markdown prose prose-sm max-w-none prose-headings:text-slate-900 prose-p:text-slate-700 prose-li:text-slate-700 prose-strong:text-slate-900">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
