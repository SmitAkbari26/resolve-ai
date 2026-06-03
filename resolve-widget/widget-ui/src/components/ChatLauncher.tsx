import { useState } from "react";
import { MessageCircle, X } from "lucide-react";
import ChatPanel from "./ChatPanel";
import { AnimatePresence } from "framer-motion";
import { useWidgetConfig } from "../context/WidgetContext";

export default function ChatLauncher() {
  const [open, setOpen] = useState(false);
  const config = useWidgetConfig();

  const positionClass = config.position === "left" ? "left-6" : "right-6";

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className={`
          fixed bottom-6 ${positionClass}
          h-16 w-16 rounded-full
          shadow-2xl
          flex items-center justify-center
          hover:scale-110
          transition-all duration-300
          z-50
          cursor-pointer
        `}
        style={{
          background: `linear-gradient(135deg, ${config.primaryColor}, #6366f1)`,
        }}
      >
        {open ? (
          <X className="text-white" />
        ) : (
          <MessageCircle className="text-white" />
        )}

        {!open && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-400 rounded-full animate-pulse" />
        )}
      </button>

      <AnimatePresence>
        {open && <ChatPanel onClose={() => setOpen(false)} />}
      </AnimatePresence>
    </>
  );
}
