"use client";

import { useState, useEffect, useRef } from "react";
import { Scale, AlertTriangle } from "lucide-react";
import { useOutletContext } from "react-router-dom";

import ChatInput from "./ChatInput";
import { sendMessage } from "../../services/chatService";
import MessageBubble from "./MessageBubble";

const EMPTY_MESSAGES = [];

const ChatArea = () => {
  const context = useOutletContext();

  const [input, setInput] = useState("");
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

  const { setMessages, conversationId, setConversationId } = context;

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
    } catch {
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
    <section className="flex h-full min-h-0 flex-col bg-linear-to-br from-blue-50 via-slate-100 to-state-100">
      {/* CHAT SCROLL AREA */}

      <div
        className="
          flex-1
          min-h-0
          overflow-y-auto
        "
      >
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center px-6 py-10">
            <div className="w-full max-w-3xl text-center animate-fade-in">
              {/* Small Logo */}
              <div className="mx-auto mb-8 flex h-17 w-17 items-center justify-center rounded-2xl bg-[#C30A1C] shadow-xl shadow-red-100">
                <Scale size={30} className="text-white" />
              </div>

              <div className="mb-5">
                <span className="inline-flex items-center rounded-full bg-blue-100 px-4 py-1 text-sm font-semibold text-[#084FF4]">
                  Nepal Legal AI Assistant
                </span>
              </div>

              {/* Heading */}
              <h1 className="text-4xl font-bold text-slate-900">
                Legal Information Assistant
              </h1>

              <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-slate-600">
                Ask questions about Nepal's laws, legal rights, court
                procedures, property, employment, contracts and other legal
                matters.
              </p>

              {/* Disclaimer */}
              <div className="mt-8 rounded-xl border border-amber-200 bg-amber-50 px-6 py-4 text-center">
                <p className="text-sm leading-6 text-amber-900">
                  <strong>⚠ Disclaimer:</strong> AI responses may be inaccurate.
                  Always verify important legal information with a qualified
                  legal professional.
                </p>
              </div>

              {/* Examples */}
              <div className="mt-10">
                <h2 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-500">
                  Example Questions
                </h2>

                <div className="grid gap-4 sm:grid-cols-2">
                  <button
                    onClick={() =>
                      setInput("How do I register land ownership in Nepal?")
                    }
                    className="rounded-2xl border border-slate-200 bg-white p-4 text-left transition hover:-translate-y-1 hover:border-[#084FF4] hover:shadow-md"
                  >
                    <p className="font-medium text-slate-800">
                      How do I register land ownership in Nepal?
                    </p>
                  </button>

                  <button
                    onClick={() =>
                      setInput("What rights do tenants have under Nepal law?")
                    }
                    className="rounded-2xl border border-slate-200 bg-white p-4 text-left transition hover:-translate-y-1 hover:border-[#084FF4] hover:shadow-md"
                  >
                    <p className="font-medium text-slate-800">
                      What rights do tenants have?
                    </p>
                  </button>

                  <button
                    onClick={() =>
                      setInput("How can I file a police complaint in Nepal?")
                    }
                    className="rounded-2xl border border-slate-200 bg-white p-4 text-left transition hover:-translate-y-1 hover:border-[#084FF4] hover:shadow-md"
                  >
                    <p className="font-medium text-slate-800">
                      How do I file a police complaint?
                    </p>
                  </button>

                  <button
                    onClick={() =>
                      setInput("What is the divorce procedure in Nepal?")
                    }
                    className="rounded-2xl border border-slate-200 bg-white p-4 text-left transition hover:-translate-y-1 hover:border-[#084FF4] hover:shadow-md"
                  >
                    <p className="font-medium text-slate-800">
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
              space-y-4
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

            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* INPUT */}

      <div
        className="
          shrink-0
          border-t
          border-border
          bg-white/80
          p-3
          md:p-4
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
