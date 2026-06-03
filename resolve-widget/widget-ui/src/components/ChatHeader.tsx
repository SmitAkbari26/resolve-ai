import { X } from "lucide-react";
import { useWidgetConfig } from "../context/WidgetContext";

interface Props {
  connected: boolean;
  onClose: () => void;
}

export default function ChatHeader({ connected, onClose }: Props) {
  const config = useWidgetConfig();

  return (
    <div
      className="text-white p-5 flex items-center justify-between"
      style={{
        background: `linear-gradient(135deg, ${config.primaryColor}, #6366f1)`,
      }}
    >
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center font-bold">
          {config.companyName.charAt(0)}
        </div>

        <div>
          <h2 className="font-semibold text-lg">{config.companyName}</h2>

          <div className="flex items-center gap-2 text-sm opacity-90">
            <span
              className={`w-2 h-2 rounded-full ${
                connected ? "bg-green-400" : "bg-red-400"
              }`}
            />

            {connected ? "Connected" : "Disconnected"}
          </div>
        </div>
      </div>

      <button onClick={onClose} className="cursor-pointer">
        <X />
      </button>
    </div>
  );
}
