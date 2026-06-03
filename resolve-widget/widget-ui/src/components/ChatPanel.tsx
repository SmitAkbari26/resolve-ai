import { Send, Paperclip, Smile } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

import TypingIndicator from "./TypingIndicator";
import SuggestedPrompts from "./SuggestedPrompts";
import ChatHeader from "./ChatHeader";
import MessageBubble from "./MessageBubble";

import { useResponsive } from "../hooks/useResponsive";
import { useWidgetConfig } from "../context/WidgetContext";
import { useChat } from "../hooks/useChat";

interface Props {
  onClose: () => void;
}

export default function ChatPanel({ onClose }: Props) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isMobile = useResponsive();
  const config = useWidgetConfig();

  const { messages, loading, connected, sendMessage } = useChat(
    config.welcomeMessage,
  );
  const [input, setInput] = useState("");

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
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
      className={`
        fixed bg-white/95 backdrop-blur-xl
        shadow-[0_20px_80px_rgba(0,0,0,0.25)]
        flex flex-col overflow-hidden z-50 border border-white/30
        ${
          isMobile
            ? "inset-0 rounded-none"
            : `${
                config.position === "left" ? "left-6" : "right-6"
              } bottom-24 w-107.5 h-180 rounded-4xl`
        }
      `}
    >
      {/* Header */}
      <ChatHeader connected={connected} onClose={onClose} />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50">
        <SuggestedPrompts onSelect={send} />

        {messages.map((message, index) => (
          <MessageBubble key={index} text={message} />
        ))}

        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t bg-white">
        <div className="flex items-center gap-3 bg-slate-100 rounded-2xl px-4 py-3">
          <Paperclip size={18} className="text-slate-500 cursor-pointer" />

          <input
            className="flex-1 bg-transparent outline-none text-slate-800"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything..."
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
          />

          <Smile size={18} className="text-slate-500 cursor-pointer" />

          <button
            onClick={() => send()}
            className="p-3 rounded-xl text-white transition hover:scale-105"
            style={{
              backgroundColor: config.primaryColor,
            }}
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </motion.div>
  );
}
