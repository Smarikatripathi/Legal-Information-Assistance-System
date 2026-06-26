const MessageBubble = ({ role, content }) => {
  const isUser = role === "user";

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`
          max-w-[80%]
          px-5
          py-3
          rounded-3xl
          shadow-sm

          ${
            isUser
              ? "gradient-primary text-white"
              : "dashboard-card text-foreground"
          }
        `}
      >
        {content}
      </div>
    </div>
  );
};

export default MessageBubble;
