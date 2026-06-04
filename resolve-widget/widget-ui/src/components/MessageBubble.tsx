import { motion } from "framer-motion";
import { Bot } from "lucide-react";
import { useWidgetConfig } from "../context/WidgetContext";
import type { ChatMessage } from "../types/chat";
import ReactMarkdown from "react-markdown";

interface Props {
  text: ChatMessage;
}

function formatTimestamp(ts?: Date | string): string {
  if (!ts) return "";
  const date = typeof ts === "string" ? new Date(ts) : ts;
  if (isNaN(date.getTime())) return "";
  const timeStr = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const today = new Date();
  if (date.toDateString() === today.toDateString()) return timeStr;
  return `${date.toLocaleDateString([], { month: "short", day: "numeric" })} ${timeStr}`;
}

export default function MessageBubble({ text }: Props) {
  const config = useWidgetConfig();
  const isUser = text.role === "user";
  const timeLabel = formatTimestamp(text.timestamp);

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.2 }}
        className="flex flex-col items-end gap-1"
      >
        <div
          className="max-w-[78%] px-4 py-3 rounded-2xl rounded-br-sm text-white text-sm leading-relaxed shadow-md"
          style={{
            background: `linear-gradient(135deg, ${config.primaryColor}, ${config.primaryColor}cc)`,
          }}
        >
          {text.message}
        </div>
        {timeLabel && (
          <span className="text-[10px] text-slate-400 px-1">{timeLabel}</span>
        )}
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.2 }}
      className="flex items-start gap-2.5"
    >
      {/* Bot Avatar */}
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 shadow-sm"
        style={{
          background: `linear-gradient(135deg, ${config.primaryColor}30, ${config.primaryColor}15)`,
          border: `1.5px solid ${config.primaryColor}40`,
        }}
      >
        <Bot size={13} style={{ color: config.primaryColor }} />
      </div>

      {/* Message bubble */}
      <div className="flex flex-col gap-1 max-w-[82%]">
        <div className="bg-white border border-slate-100 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm text-sm text-slate-700 leading-relaxed">
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="text-base font-bold mb-2 text-slate-800">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-sm font-semibold mb-1.5 text-slate-800">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold mt-2 mb-1 text-slate-800">{children}</h3>
              ),
              ul: ({ children }) => (
                <ul className="list-disc ml-4 space-y-0.5 text-slate-700">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal ml-4 space-y-0.5 text-slate-700">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="text-sm">{children}</li>
              ),
              p: ({ children }) => (
                <p className="mb-1.5 last:mb-0 text-slate-700">{children}</p>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-slate-800">{children}</strong>
              ),
              code: ({ children }) => (
                <code className="bg-slate-100 text-slate-800 rounded px-1 py-0.5 text-xs font-mono">
                  {children}
                </code>
              ),
            }}
          >
            {text.message}
          </ReactMarkdown>
        </div>
        {timeLabel && (
          <span className="text-[10px] text-slate-400 px-1">{timeLabel}</span>
        )}
      </div>
    </motion.div>
  );
}
