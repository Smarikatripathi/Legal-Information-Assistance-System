"use client";

import { useState, useEffect, useRef } from "react";
import { Scale, FileText, Home, ShieldCheck } from "lucide-react";
import { useOutletContext } from "react-router-dom";

import ChatInput from "./ChatInput";
import { sendMessage } from "../services/chatService";
import MessageBubble from "./MessageBubble";

const ChatArea = () => {
  const context = useOutletContext();

  if (!context) {
    return (
      <div className="flex items-center justify-center h-screen">
        Loading...
      </div>
    );
  }

  const {
    messages,
    setMessages,
    conversationId,
    setConversationId,
  } = context;

  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;
    setInput("");

    try {
      const response = await sendMessage(currentInput, conversationId);

      const assistantMessage = {
        role: "assistant",
        content: response.answer,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    }
  };

  return (
    <section className="flex flex-col h-full overflow-hidden">

      {/* SCROLL AREA */}
      <div className="flex-1 overflow-y-auto">

        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full px-6 py-10">
            <div className="max-w-5xl text-center animate-fade-in">

              {/* Logo */}
              <div className="mx-auto mb-8 h-24 w-24 rounded-3xl gradient-primary flex items-center justify-center">
                <Scale size={48} className="text-white" />
              </div>

              {/* Title */}
              <h1 className="text-4xl md:text-6xl font-bold mb-5">
                <span className="text-primary">Legal Information</span>
                <br />
                <span className="text-accent">Assistant</span>
              </h1>

              <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
                Ask legal questions, understand laws, and connect with legal resources in Nepal.
              </p>

              {/* Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-12">
                <div className="dashboard-card p-6 text-left">
                  <FileText className="text-primary mb-2" />
                  <h3 className="font-semibold">Contract Law</h3>
                  <p className="text-sm text-muted-foreground">
                    Agreements, obligations and disputes.
                  </p>
                </div>

                <div className="dashboard-card p-6 text-left">
                  <Home className="text-accent mb-2" />
                  <h3 className="font-semibold">Property Rights</h3>
                  <p className="text-sm text-muted-foreground">
                    Ownership and land law.
                  </p>
                </div>

                <div className="dashboard-card p-6 text-left">
                  <ShieldCheck className="text-primary mb-2" />
                  <h3 className="font-semibold">Consumer Protection</h3>
                  <p className="text-sm text-muted-foreground">
                    Rights, refunds and complaints.
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

      {/* INPUT (ALWAYS VISIBLE) */}
      <div className="shrink-0 border-t border-border p-4 bg-white/60">
        <div className="max-w-4xl mx-auto w-full">
          <ChatInput
            value={input}
            onChange={setInput}
            onSend={handleSend}
          />
        </div>
      </div>

    </section>
  );
};

export default ChatArea;