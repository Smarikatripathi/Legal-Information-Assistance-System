import { useState, useEffect, useRef } from "react";

import { Scale, FileText, Home, ShieldCheck } from "lucide-react";

import ChatInput from "./ChatInput";
import MessageBubble from "./MessageBubble";

const ChatArea = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
    };

    const assistantMessage = {
      role: "assistant",
      content: "This is a temporary legal assistant response.",
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
      assistantMessage,
    ]);

    setInput("");
  };

  return (
    <section className="flex flex-col h-screen overflow-hidden">
      {/* HEADER */}

      <header
        className="
          h-14
          border-b
          border-border
          bg-white/70
          backdrop-blur-md
          flex
          items-center
          justify-between
          px-4
          md:px-6
        "
      >
        <div>
          <h2 className="font-semibold ml-10 lg:ml-0">
            Legal Information Assistant
          </h2>

          <p className="text-sm text-muted-foreground ml-10 lg:ml-0">
            Nepal Legal Support Platform
          </p>
        </div>

        <div className="flex gap-2">
          <div className="h-3 w-3 rounded-full bg-accent" />
          <div className="h-3 w-3 rounded-full bg-primary" />
        </div>
      </header>

      {/* MAIN */}

      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full px-6">
            <div className="max-w-5xl text-center animate-fade-in">
              {/* Logo */}

              <div
                className="
                  mx-auto
                  mb-8
                  h-24
                  w-24
                  rounded-3xl
                  gradient-primary
                  flex
                  items-center
                  justify-center
                "
              >
                <Scale size={48} className="text-white" />
              </div>

              {/* Heading */}

              <h1 className="text-4xl md:text-6xl font-bold mb-5">
                <span className="text-primary">Legal Information</span>

                <br />

                <span className="text-accent">Assistant</span>
              </h1>

              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Ask legal questions, understand laws, explore legal resources
                and connect with legal professionals across Nepal.
              </p>

              {/* CARDS */}

              <div className="grid md:grid-cols-3 gap-5 mt-12">
                <div className="dashboard-card p-6 text-left">
                  <FileText className="text-primary mb-4" />

                  <h3 className="font-semibold text-primary mb-2">
                    Contract Law
                  </h3>

                  <p className="text-sm text-muted-foreground">
                    Agreements, obligations and disputes.
                  </p>
                </div>

                <div className="dashboard-card p-6 text-left">
                  <Home className="text-accent mb-4" />

                  <h3 className="font-semibold text-accent mb-2">
                    Property Rights
                  </h3>

                  <p className="text-sm text-muted-foreground">
                    Ownership, inheritance and land law.
                  </p>
                </div>

                <div className="dashboard-card p-6 text-left">
                  <ShieldCheck className="text-primary mb-4" />

                  <h3 className="font-semibold text-primary mb-2">
                    Consumer Protection
                  </h3>

                  <p className="text-sm text-muted-foreground">
                    Complaints, refunds and legal rights.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto p-6 space-y-4">
            {messages.map((msg, index) => (
              <MessageBubble
                key={index}
                role={msg.role}
                content={msg.content}
              />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* INPUT */}

      <div className="border-t border-border p-4 bg-white/60">
        <div className="max-w-4xl mx-auto">
          <ChatInput value={input} onChange={setInput} onSend={handleSend} />
        </div>
      </div>
    </section>
  );
};

export default ChatArea;
