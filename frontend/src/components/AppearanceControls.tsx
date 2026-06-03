import { SlidersHorizontal } from "lucide-react";

interface Props {
  config: any;
  setConfig: (config: any) => void;
}

export default function AppearanceControls({ config, setConfig }: Props) {
  const update = (key: string, value: number) => {
    setConfig({
      ...config,
      [key]: value,
    });
  };

  const Slider = ({ label, keyName, min, max }: any) => (
    <div>
      <div className="flex justify-between mb-2">
        <span>{label}</span>
        <span>{config[keyName]}</span>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        value={config[keyName]}
        onChange={(e) => update(keyName, Number(e.target.value))}
        className="w-full"
      />
    </div>
  );

  return (
    <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 space-y-5">
      <div className="flex items-center gap-3">
        <SlidersHorizontal className="text-emerald-400" />
        <h3 className="font-semibold">Appearance</h3>
      </div>

      <Slider label="Width" keyName="width" min={350} max={600} />

      <Slider label="Height" keyName="height" min={500} max={900} />

      <Slider label="Radius" keyName="borderRadius" min={16} max={48} />

      <Slider label="Launcher" keyName="launcherSize" min={48} max={90} />
    </div>
  );
}
