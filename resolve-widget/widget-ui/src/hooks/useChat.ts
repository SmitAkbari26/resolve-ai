import { useEffect, useRef, useState } from "react";

import { API_WS_URL } from "../config/api";
import { WidgetWebSocket } from "../services/websocket";
import { chatApi } from "../services/chatApi";
import type { ChatMessage, ChatResponse } from "../types/chat";

export function useChat(welcomeMessage: string) {
  const wsRef = useRef(new WidgetWebSocket());

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  const globalConfig = (window as any).ResolveAIConfig || {};
  const apiKey = globalConfig.apiKey || "";

  const getOrInitUserId = (): string => {
    if (globalConfig.userId) {
      return globalConfig.userId;
    }
    let uId = localStorage.getItem("resolve_ai_user_id");
    if (!uId) {
      uId = crypto.randomUUID ? crypto.randomUUID() : "user_" + Math.random().toString(36).substring(2, 15);
      localStorage.setItem("resolve_ai_user_id", uId);
    }
    return uId;
  };

  const [userId, setUserId] = useState<string>(getOrInitUserId());
  const [conversationId, setConversationId] = useState<string | null>(
    localStorage.getItem("resolve_ai_conversation_id")
  );

  useEffect(() => {
    const loadHistory = async () => {
      if (conversationId) {
        setLoading(true);
        try {
          const history = await chatApi.getHistory(conversationId);
          if (history && history.messages) {
            const mapped = history.messages.map((m: any) => ({
              role: m.role as "user" | "assistant",
              message: m.content,
              timestamp: m.created_at ? new Date(m.created_at) : new Date(),
            }));
            setMessages(mapped.length > 0 ? mapped : [{ role: "assistant", message: welcomeMessage, timestamp: new Date() }]);
          }
        } catch (err) {
          console.error("Failed to load conversation history:", err);
          localStorage.removeItem("resolve_ai_conversation_id");
          setConversationId(null);
          setMessages([{ role: "assistant", message: welcomeMessage, timestamp: new Date() }]);
        } finally {
          setLoading(false);
        }
      } else {
        setMessages([{ role: "assistant", message: welcomeMessage, timestamp: new Date() }]);
      }
    };
    loadHistory();
  }, [conversationId, welcomeMessage]);

  const connect = () => {
    wsRef.current.connect(
      API_WS_URL,

      (result: ChatResponse) => {
        if (result.error) {
          setError(result.error);
          setLoading(false);
          return;
        }

        if (result.type === "chunk") {
          setLoading(false);

          setMessages((prev) => {
            const last = prev[prev.length - 1];

            if (last && last.role === "assistant") {
              const updated = [...prev];

              updated[updated.length - 1] = {
                role: "assistant",
                message: last.message + (result.delta || ""),
                timestamp: last.timestamp || new Date(),
              };

              return updated;
            }

            return [
              ...prev,
              {
                role: "assistant",
                message: result.delta || "",
                timestamp: new Date(),
              },
            ];
          });

          return;
        }

        setLoading(false);

        if (result.conversation_id) {
          setConversationId(result.conversation_id);
          localStorage.setItem("resolve_ai_conversation_id", result.conversation_id);
        }

        if (result.ai_response) {
          setMessages((prev) => {
            const last = prev[prev.length - 1];

            if (last && last.role === "assistant") {
              const updated = [...prev];

              updated[updated.length - 1] = {
                role: "assistant",
                message: result.ai_response || "",
                timestamp: new Date(),
              };

              return updated;
            }

            return [
              ...prev,
              {
                role: "assistant",
                message: result.ai_response || "",
                timestamp: new Date(),
              },
            ];
          });
        }
      },

      () => {
        setConnected(true);
        setError(null);
      },

      () => {
        setConnected(false);

        setTimeout(() => {
          connect();
        }, 3000);
      },

      () => {
        setConnected(false);
      },
    );
  };

  useEffect(() => {
    connect();

    return () => {
      wsRef.current.disconnect();
    };
  }, []);

  const sendMessage = (text: string) => {
    if (!text.trim()) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        message: text,
        timestamp: new Date(),
      },
    ]);

    setLoading(true);

    wsRef.current.send({
      user_id: userId,
      user_email: globalConfig.userEmail || `${userId}@guest.resolve.ai`,
      message: text,
      conversation_id: conversationId,
      api_key: apiKey,
    });
  };

  const startNewChat = () => {
    localStorage.removeItem("resolve_ai_conversation_id");
    const newUid = crypto.randomUUID ? crypto.randomUUID() : "user_" + Math.random().toString(36).substring(2, 15);
    localStorage.setItem("resolve_ai_user_id", newUid);
    setUserId(newUid);
    setConversationId(null);
    setMessages([{ role: "assistant", message: welcomeMessage, timestamp: new Date() }]);
  };

  return {
    messages,
    loading,
    error,
    connected,
    conversationId,
    sendMessage,
    startNewChat,
  };
}

