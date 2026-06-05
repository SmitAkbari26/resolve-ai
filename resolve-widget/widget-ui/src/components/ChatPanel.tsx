import { Send, Mic, Smile } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

import TypingIndicator from "./TypingIndicator";
import SuggestedPrompts from "./SuggestedPrompts";
import ChatHeader from "./ChatHeader";
import MessageBubble from "./MessageBubble";

import { useResponsive } from "../hooks/useResponsive";
import { useWidgetConfig } from "../context/WidgetContext";
import { useChat } from "../hooks/useChat";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";

interface Props {
  onClose: () => void;
}

export default function ChatPanel({ onClose }: Props) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isMobile = useResponsive();
  const config = useWidgetConfig();
  const { isListening, startListening, stopListening } = useSpeechRecognition();

  const {
    messages,
    loading,
    connected,
    conversationId,
    sendMessage,
    startNewChat,
  } = useChat(config.welcomeMessage);
  const [input, setInput] = useState("");

  // true when the user has an existing saved session
  const hasSession = Boolean(conversationId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = (text?: string) => {
    const message = text || input;
    if (!message.trim()) return;
    sendMessage(message);
    setInput("");
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 40 }}
      className="fixed bg-white/95 backdrop-blur-xl shadow-[0_20px_80px_rgba(0,0,0,0.25)] flex flex-col overflow-hidden z-50 border border-white/30"
      style={
        isMobile
          ? { inset: 0, borderRadius: 0 }
          : {
              [config.position === "left" ? "left" : "right"]: 24,
              bottom: config.launcherSize + 16,
              width: config.width,
              height: config.height,
              borderRadius: config.borderRadius,
            }
      }
    >
      {/* Header */}
      <ChatHeader
        connected={connected}
        hasSession={hasSession}
        onClose={onClose}
        onNewChat={startNewChat}
      />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 bg-slate-50">
        <SuggestedPrompts onSelect={send} />

        {messages.map((message, index) => (
          <MessageBubble key={index} text={message} />
        ))}

        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 sm:p-4 border-t bg-white shrink-0">
        <div className="flex items-center gap-2 sm:gap-3 bg-slate-100 rounded-2xl px-3 sm:px-4 py-2.5 sm:py-3">
          <button
            onClick={() =>
              !isListening
                ? startListening((text) => {
                    setInput(text);
                    send();
                  })
                : stopListening()
            }
            className="text-slate-500 cursor-pointer shrink-0 hidden sm:block"
          >
            <Mic size={16} />
          </button>

          <input
            className="flex-1 bg-transparent outline-none text-slate-800 text-sm sm:text-base min-w-0"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Listening..." : "Ask anything..."}
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
          />

          <Smile
            size={16}
            className="text-slate-500 cursor-pointer shrink-0 hidden sm:block"
          />

          <button
            onClick={() => send()}
            className="p-2.5 sm:p-3 rounded-xl text-white transition hover:scale-105 shrink-0"
            style={{ backgroundColor: config.primaryColor }}
          >
            <Send size={16} />
          </button>
        </div>

        <p className="text-[10px] text-center text-slate-400 mt-2">
          Powered by <span className="font-semibold">ResolveAI</span>
        </p>
      </div>
    </motion.div>
  );
}
