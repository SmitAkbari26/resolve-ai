import { Palette } from "lucide-react";

interface Props {
  value: string;
  onChange: (color: string) => void;
}

export default function ColorPicker({ value, onChange }: Props) {
  return (
    <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6">
      <div className="flex items-center gap-3 mb-5">
        <Palette className="w-5 h-5 text-emerald-400" />
        <h3 className="text-slate-100 font-semibold">Primary Color</h3>
      </div>

      <div className="flex items-center gap-4">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-16 h-16 rounded-2xl border-none cursor-pointer"
        />

        <div>
          <p className="text-slate-400 text-sm">Widget Accent</p>
          <p className="text-white font-mono">{value}</p>
        </div>
      </div>
    </div>
  );
}
