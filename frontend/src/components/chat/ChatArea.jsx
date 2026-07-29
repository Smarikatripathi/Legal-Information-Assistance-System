"use client";

import { useState, useEffect, useRef } from "react";
import { Scale, AlertTriangle, Loader2 } from "lucide-react";
import { useOutletContext } from "react-router-dom";

import ChatInput from "./ChatInput";
import { sendMessage } from "../../services/chatService";
import MessageBubble from "./MessageBubble";

const EMPTY_MESSAGES = [];

const ChatArea = () => {
  const context = useOutletContext();

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef(null);

  const messages = context?.messages ?? EMPTY_MESSAGES;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }, [messages]);

  if (!context) {
    return (
      <div className="flex h-full items-center justify-center">Loading...</div>
    );
  }

  const { setMessages, conversationId, setConversationId, loadConversations } = context;

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;

    setInput("");
    setIsLoading(true);

    try {
      const response = await sendMessage(currentInput, conversationId);

      const assistantMessage = {
        role: "assistant",
        content: response.answer,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.conversation_id) {
  setConversationId(response.conversation_id);

  // refresh sidebar history
  loadConversations();
}
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="flex h-full min-h-0 flex-col bg-[#F8FAFC]">
      {/* CHAT SCROLL AREA */}
      <div
        className="
          flex-1
          min-h-0
          overflow-y-auto
          pb-16
        "
      >
        {messages.length === 0 ? (
          <div className="flex h-full min-h-0 items-center justify-center px-8 pt-8">
            <div className="w-full max-w-[900px] text-center animate-fade-in">
              {/* Small Logo */}
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-[#2563EB] shadow-lg shadow-blue-100">
                <Scale size={24} className="text-white" />
              </div>

              <div className="mb-4">
                <span className="inline-flex items-center rounded-full bg-blue-100 px-4 py-1.5 text-sm font-semibold text-[#2563EB]">
                   Welcome to Legal Assist
                </span>
              </div>

              <h1 className="text-[28px] font-bold text-slate-900 mb-3 leading-tight">
                How can I help you today?
              </h1>

              <p className="mx-auto mt-3 max-w-2xl text-[16px] leading-relaxed text-slate-600">
                Ask questions about Nepal's laws, legal rights, court
                procedures, property, employment, contracts and other legal
                matters.
              </p>

              {/* Disclaimer */}
              <div className="mx-auto mt-4 max-w-[760px] rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-center">
                <p className="text-xs leading-tight text-amber-900">
                  <strong>⚠ Disclaimer:</strong> AI responses may be inaccurate.
                  Always verify important legal information with a qualified
                  legal professional.
                </p>
              </div>

              {/* Examples */}
              <div className="mt-5">
                <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">
                  Example Questions
                </h2>

                <div className="grid gap-3 sm:grid-cols-2">
                  <button
                    onClick={() =>
                      setInput("How do I register land ownership in Nepal?")
                    }
                    className="h-16 rounded-xl border border-slate-200 bg-white px-4 py-2 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-[#2563EB] hover:shadow-md hover:shadow-blue-100"
                  >
                    <p className="text-sm font-medium text-slate-800">
                      How do I register land ownership in Nepal?
                    </p>
                  </button>

                  <button
                    onClick={() =>
                      setInput("What rights do tenants have under Nepal law?")
                    }
                    className="h-16 rounded-xl border border-slate-200 bg-white px-4 py-2 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-[#2563EB] hover:shadow-md hover:shadow-blue-100"
                  >
                    <p className="text-sm font-medium text-slate-800">
                      What rights do tenants have?
                    </p>
                  </button>

                  <button
                    onClick={() =>
                      setInput("How can I file a police complaint in Nepal?")
                    }
                    className="h-16 rounded-xl border border-slate-200 bg-white px-4 py-2 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-[#2563EB] hover:shadow-md hover:shadow-blue-100"
                  >
                    <p className="text-sm font-medium text-slate-800">
                      How do I file a police complaint?
                    </p>
                  </button>

                  <button
                    onClick={() =>
                      setInput("What is the divorce procedure in Nepal?")
                    }
                    className="h-16 rounded-xl border border-slate-200 bg-white px-4 py-2 text-left transition-all duration-200 hover:-translate-y-0.5 hover:border-[#2563EB] hover:shadow-md hover:shadow-blue-100"
                  >
                    <p className="text-sm font-medium text-slate-800">
                      What is the divorce procedure?
                    </p>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div
            className="
              mx-auto
              w-full
              max-w-4xl
              space-y-6
              p-4
              md:p-6
            "
          >
            {messages.map((msg, index) => (
              <MessageBubble
                key={index}
                role={msg.role}
                content={msg.content}
              />
            ))}

            {isLoading && (
              <div className="flex items-start gap-4 p-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#084FF4]">
                  <Scale size={20} className="text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex gap-1.5">
                    <div className="h-2.5 w-2.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="h-2.5 w-2.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="h-2.5 w-2.5 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* INPUT */}
      <div
        className="
          shrink-0
          border-t
          border-slate-200
          bg-white
          p-6
        "
      >
        <div
          className="
            mx-auto
            w-full
            max-w-4xl
          "
        >
          <ChatInput value={input} onChange={setInput} onSend={handleSend} />
        </div>
      </div>
    </section>
  );
};

export default ChatArea;
