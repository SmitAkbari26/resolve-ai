import { motion } from "framer-motion";
import { useWidgetConfig } from "../context/WidgetContext";
import type { ChatMessage } from "../types/chat";
import ReactMarkdown from "react-markdown";

interface Props {
  text: ChatMessage;
}

export default function MessageBubble({ text }: Props) {
  const config = useWidgetConfig();

  const isUser = text.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`max-w-[80%] ${isUser ? "ml-auto" : ""}`}
    >
      <div
        className={`p-4 rounded-3xl ${
          isUser ? "text-white" : "bg-white shadow-sm"
        }`}
        style={{
          backgroundColor: isUser ? config.primaryColor : undefined,
        }}
      >
        {isUser ? (
          text.message
        ) : (
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="text-xl font-bold mb-3">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-lg font-semibold mb-2">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="font-semibold mt-3 mb-2">{children}</h3>
              ),
              ul: ({ children }) => (
                <ul className="list-disc ml-5 space-y-1">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal ml-5 space-y-1">{children}</ol>
              ),
              p: ({ children }) => <p className="mb-2">{children}</p>,
            }}
          >
            {text.message}
          </ReactMarkdown>
        )}
      </div>

      <p className="text-xs text-slate-400 mt-1 px-2">just now</p>
    </motion.div>
  );
}
