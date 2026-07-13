import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const MessageBubble = ({ role, content }) => {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`
          max-w-[85%]
          px-5
          py-3
          rounded-3xl
          shadow-sm
          ${isUser ? "gradient-primary text-white" : "dashboard-card text-foreground"}
        `}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{content}</p>
        ) : (
          <div className="legal-markdown prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
