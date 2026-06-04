import { useEffect, useState } from "react";
import { MessageCircle, X } from "lucide-react";
import ChatPanel from "./ChatPanel";
import { AnimatePresence } from "framer-motion";
import { useWidgetConfig } from "../context/WidgetContext";

export default function ChatLauncher() {
  const [open, setOpen] = useState(false);
  const config = useWidgetConfig();

  const positionClass = config.position === "left" ? "left-6" : "right-6";

  // Auto-open behaviour driven by config
  useEffect(() => {
    if (!config.autoOpen) return;
    const timer = setTimeout(
      () => setOpen(true),
      config.autoOpenDelay ?? 2000,
    );
    return () => clearTimeout(timer);
  }, [config.autoOpen, config.autoOpenDelay]);

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className={`
          fixed bottom-6 ${positionClass}
          rounded-full
          shadow-2xl
          flex items-center justify-center
          hover:scale-110
          transition-all duration-300
          z-50
          cursor-pointer
        `}
        style={{
          width: config.launcherSize,
          height: config.launcherSize,
          background: `linear-gradient(135deg, ${config.primaryColor}, #6366f1)`,
        }}
      >
        {open ? (
          <X className="text-white" />
        ) : (
          <MessageCircle className="text-white" />
        )}

        {!open && config.showBadge && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-400 rounded-full animate-pulse" />
        )}
      </button>

      <AnimatePresence>
        {open && <ChatPanel onClose={() => setOpen(false)} />}
      </AnimatePresence>
    </>
  );
}
