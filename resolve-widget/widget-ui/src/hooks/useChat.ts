import { useEffect, useRef, useState } from "react";

import { API_WS_URL } from "../config/api";
import { WidgetWebSocket } from "../services/websocket";
import type { ChatMessage, ChatResponse } from "../types/chat";

export function useChat(welcomeMessage: string) {
  const wsRef = useRef(new WidgetWebSocket());

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      message: welcomeMessage,
    },
  ]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const [connected, setConnected] = useState(false);

  const [conversationId, setConversationId] = useState<string | null>(null);

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
              };

              return updated;
            }

            return [
              ...prev,
              {
                role: "assistant",
                message: result.delta || "",
              },
            ];
          });

          return;
        }

        setLoading(false);

        if (result.conversation_id) {
          setConversationId(result.conversation_id);
        }

        if (result.ai_response) {
          setMessages((prev) => {
            const last = prev[prev.length - 1];

            if (last && last.role === "assistant") {
              const updated = [...prev];

              updated[updated.length - 1] = {
                role: "assistant",
                message: result.ai_response || "",
              };

              return updated;
            }

            return [
              ...prev,
              {
                role: "assistant",
                message: result.ai_response || "",
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

  console.log("Sending:", {
    conversationId,
  });

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
      },
    ]);

    setLoading(true);

    wsRef.current.send({
      user_id: "21f54207-121b-4607-b2b4-d84c09086eae",
      user_email: "smit.akbari@example.com",
      message: text,
      conversation_id: conversationId,
    });
  };

  return {
    messages,
    loading,
    error,
    connected,
    conversationId,
    sendMessage,
  };
}
