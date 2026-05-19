"use client";

import { useState, useCallback } from "react";
import { ChatWindow } from "@/components/chat/chat-window";
import { InputBar } from "@/components/chat/input-bar";
import { sendMessage } from "@/lib/api";
import type { Message, ChatResponse } from "@/lib/types";
import Link from "next/link";
import { BarChart2 } from "lucide-react";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Namaste! I'm SaharaAI, your customer support assistant. Ask me anything about your orders, returns, payments, or products — in Hindi, English, or Hinglish!",
      timestamp: new Date(),
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [currentMode, setCurrentMode] = useState<string>("hybrid");

  const handleSend = useCallback(
    async (query: string) => {
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: query,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setLoading(true);

      try {
        const response: ChatResponse = await sendMessage(query);
        setCurrentMode(response.retrieval_mode_used);

        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.answer,
          timestamp: new Date(),
          metadata: response,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } catch {
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          role: "assistant",
          content:
            "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return (
    <div className="flex flex-col h-screen bg-sahara-cream">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 bg-white border-b border-sahara-sand shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-sahara-saffron flex items-center justify-center text-white font-bold text-sm">
            S
          </div>
          <div>
            <h1 className="font-semibold text-gray-900 text-sm">SaharaAI</h1>
            <p className="text-xs text-gray-500">Customer Support Assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 font-mono uppercase tracking-wide">
            {currentMode}
          </span>
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-sahara-saffron transition-colors"
          >
            <BarChart2 size={14} />
            Dashboard
          </Link>
        </div>
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-hidden">
        <ChatWindow messages={messages} loading={loading} />
      </div>

      {/* Input */}
      <div className="border-t border-sahara-sand bg-white">
        <InputBar onSend={handleSend} loading={loading} />
      </div>
    </div>
  );
}
