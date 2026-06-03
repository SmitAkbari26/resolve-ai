import React, { useState, useEffect, useRef } from "react";
import { chatApi, API_WS_URL } from "../services/api";
import {
  Send,
  Bot,
  RefreshCw,
  AlertCircle,
  HelpCircle,
  Brain,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";

interface ChatMessage {
  role: "user" | "assistant";
  message: string;
}

export const Chat: React.FC = () => {
  const { user } = useAuth();
  const USER_ID = user?.id || null;
  const USER_EMAIL = user?.email || null;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [inputMsg, setInputMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket connection setup
  const connectWebSocket = () => {
    if (
      wsRef.current &&
      (wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    const ws = new WebSocket(API_WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = async (event) => {
      try {
        const result = JSON.parse(event.data);

        if (result.error) {
          setError(result.error);
          setLoading(false);
          return;
        }

        if (result) {
          if (result.type === "chunk") {
            setLoading(false);
            setMessages((prev) => {
              const lastMsg = prev[prev.length - 1];
              if (lastMsg && lastMsg.role === "assistant") {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: "assistant",
                  message: lastMsg.message + result.delta,
                };
                return updated;
              } else {
                return [
                  ...prev,
                  {
                    role: "assistant",
                    message: result.delta,
                  },
                ];
              }
            });
          } else {
            setLoading(false);
            if (result.conversation_id) {
              setConversationId(result.conversation_id);
            }

            const fullMessage = result.ai_response || "Request processed.";
            setMessages((prev) => {
              const lastMsg = prev[prev.length - 1];
              if (lastMsg && lastMsg.role === "assistant") {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: "assistant",
                  message: fullMessage,
                };
                return updated;
              } else {
                return [
                  ...prev,
                  {
                    role: "assistant",
                    message: fullMessage,
                  },
                ];
              }
            });
          }
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
        setLoading(false);
      }
    };
    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      // Show error only after a successful connection has been made
      if (isConnected) {
        setError("Connection error.");
      }
      setLoading(false);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected. Reconnecting...");
      setIsConnected(false);
      setTimeout(connectWebSocket, 3000);
    };
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          role: "assistant",
          message:
            "👋 Welcome to Resolve AI. Describe your issue and our autonomous support engine will resolve it.",
        },
      ]);
    }
  }, []);

  const loadHistory = async () => {
    if (!conversationId) return;

    setHistoryLoading(true);

    try {
      const history = await chatApi.getHistory(conversationId);

      if (history?.messages) {
        setMessages(
          history.messages.map((m: any) => ({
            role: m.role,
            message: m.content,
          })),
        );
      }
    } catch {
      setError("Failed to load history.");
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMsg.trim() || loading) return;

    const userText = inputMsg;

    setInputMsg("");
    setMessages((prev) => [...prev, { role: "user", message: userText }]);
    setLoading(true);
    setError(null);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(
          JSON.stringify({
            user_id: USER_ID,
            user_email: USER_EMAIL,
            message: userText,
            conversation_id: conversationId,
          }),
        );
      } catch {
        setError("Failed to send message via WebSocket.");
        setLoading(false);
      }
    } else {
      setError("Connection lost. Attempting to reconnect...");
      connectWebSocket();
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-12 gap-6 h-[calc(100vh-120px)]">
      {/* LEFT CHAT PANEL */}
      <div className="col-span-8 flex flex-col bg-[#0b1120] rounded-3xl border border-slate-800 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-800 flex justify-between items-center bg-[#111827]">
          <div className="flex items-center gap-3">
            <div className="bg-emerald-600 p-2 rounded-xl">
              <Bot className="w-5 h-5 text-white" />
            </div>

            <div>
              <h2 className="text-slate-100 font-bold">Resolve AI Live</h2>
              <p className="text-xs text-slate-400">
                Autonomous Resolution Engine
              </p>
            </div>
          </div>

          {conversationId && (
            <button
              onClick={loadHistory}
              className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-xs text-slate-300"
            >
              <RefreshCw
                className={`w-4 h-4 ${historyLoading ? "animate-spin" : ""}`}
              />
              Reload
            </button>
          )}
        </div>

        {/* Messages */}
        <div className="flex-grow overflow-y-auto p-6 space-y-5 bg-[#020617]">
          {messages.map((msg, idx) => {
            const isUser = msg.role === "user";

            return (
              <div
                key={idx}
                className={`flex ${isUser ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[75%] px-5 py-4 rounded-2xl text-sm leading-relaxed shadow-lg whitespace-pre-wrap break-words ${
                    isUser
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-800 text-slate-200 border border-slate-700"
                  }`}
                >
                  {msg.message}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex items-center gap-3 text-emerald-400">
              <Brain className="w-5 h-5 animate-pulse" />
              <span className="text-sm">Resolve AI is analyzing...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error */}
        {error && (
          <div className="bg-rose-900/20 border-t border-rose-700 text-rose-400 px-6 py-3 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        {/* Input */}
        <form
          onSubmit={handleSend}
          className="p-5 border-t border-slate-800 bg-[#111827] flex gap-4"
        >
          <input
            type="text"
            value={inputMsg}
            onChange={(e) => setInputMsg(e.target.value)}
            placeholder="Describe your issue..."
            className="flex-grow bg-slate-900 border border-slate-700 rounded-2xl px-5 py-4 text-slate-200 focus:outline-none focus:border-emerald-500"
          />

          <button
            type="submit"
            disabled={loading}
            className="bg-emerald-600 hover:bg-emerald-700 px-6 rounded-2xl text-white"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>

      {/* RIGHT SIDEBAR */}
      <div className="col-span-4 overflow-y-auto">
        <div className="bg-[#0b1120] rounded-3xl border border-slate-800 p-6 h-full flex flex-col">
          <div className="flex items-center gap-2 mb-6">
            <HelpCircle className="w-5 h-5 text-emerald-400" />
            <span className="text-slate-100 font-bold text-lg">Try Asking</span>
          </div>

          <p className="text-sm text-slate-400 mb-6">
            Explore different support scenarios Resolve AI can autonomously
            handle.
          </p>

          <div className="space-y-3 overflow-y-auto pr-2">
            {[
              "My payment failed but money was deducted",
              "Refund for duplicate transaction",
              "Unable to login after password reset",
              "Billing policy clarification",
              "My subscription was cancelled unexpectedly",
              "Application crashes on startup",
              "Technical issue report",
              "API integration not working",
              "Why was my account suspended?",
              "Need invoice for last transaction",
              "Feature request for dashboard analytics",
              "I was charged twice for one purchase",
              "How do I upgrade my plan?",
              "My service is running very slow",
              "Ticket status update",
              "Need urgent production support",
              "Error while processing checkout",
              "Reset my account settings",
              "Why is my request timing out?",
              "Cannot connect to server",
            ].map((q) => (
              <button
                key={q}
                onClick={() => setInputMsg(q)}
                className="w-full text-left bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-2xl px-4 py-4 text-sm text-slate-300 transition-all duration-200 hover:border-emerald-500 hover:translate-x-1"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
