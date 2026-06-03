import { Layout } from "lucide-react";

interface Props {
  value: string;
  onChange: (position: string) => void;
}

export default function PositionSelector({ value, onChange }: Props) {
  return (
    <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6">
      <div className="flex items-center gap-3 mb-5">
        <Layout className="w-5 h-5 text-emerald-400" />
        <h3 className="text-slate-100 font-semibold">Widget Position</h3>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {["left", "right"].map((pos) => (
          <button
            key={pos}
            onClick={() => onChange(pos)}
            className={`py-4 rounded-2xl border transition-all ${
              value === pos
                ? "border-emerald-500 bg-emerald-500/10 text-emerald-400"
                : "border-slate-700 text-slate-300"
            }`}
          >
            {pos.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}
