import { X, RotateCcw } from "lucide-react";
import { useWidgetConfig } from "../context/WidgetContext";

interface Props {
  connected: boolean;
  hasSession: boolean;
  onClose: () => void;
  onNewChat: () => void;
}

export default function ChatHeader({ connected, hasSession, onClose, onNewChat }: Props) {
  const config = useWidgetConfig();

  return (
    <div
      className="text-white p-5 flex items-center justify-between shrink-0"
      style={{
        background: `linear-gradient(135deg, ${config.primaryColor}, #6366f1)`,
      }}
    >
      {/* Left: avatar + name */}
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/20 flex items-center justify-center font-bold text-base sm:text-lg shrink-0">
          {config.companyName.charAt(0)}
        </div>

        <div className="min-w-0">
          <h2 className="font-semibold text-sm sm:text-lg leading-tight truncate">
            {config.companyName}
          </h2>

          <div className="flex items-center gap-2 text-xs sm:text-sm opacity-90 mt-0.5">
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${
                connected ? "bg-green-400" : "bg-red-400"
              }`}
            />
            {connected ? "Online" : "Reconnecting…"}
          </div>
        </div>
      </div>

      {/* Right: actions */}
      <div className="flex items-center gap-2 shrink-0">
        {/* "New Chat" only when a previous session exists */}
        {hasSession && (
          <button
            onClick={onNewChat}
            title="Start a new chat"
            className="flex items-center gap-1 bg-white/15 hover:bg-white/25 transition-colors rounded-full px-2.5 py-1.5 text-xs font-medium cursor-pointer"
          >
            <RotateCcw size={13} />
            <span className="hidden sm:inline">New Chat</span>
          </button>
        )}

        <button
          onClick={onClose}
          className="p-1.5 rounded-full hover:bg-white/20 transition-colors cursor-pointer"
          title="Close chat"
        >
          <X size={18} />
        </button>
      </div>
    </div>
  );
}
