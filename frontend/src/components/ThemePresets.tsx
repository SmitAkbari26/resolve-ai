const presets = [
  {
    name: "Modern Violet",
    color: "#8b5cf6",
  },
  {
    name: "Emerald Pro",
    color: "#10b981",
  },
  {
    name: "Ocean Blue",
    color: "#3b82f6",
  },
  {
    name: "Enterprise Dark",
    color: "#334155",
  },
];

export default function ThemePresets({ setConfig, config }: any) {
  return (
    <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6">
      <h3 className="font-semibold mb-5">Theme Presets</h3>

      <div className="grid grid-cols-2 gap-4">
        {presets.map((preset) => (
          <button
            key={preset.name}
            onClick={() =>
              setConfig({
                ...config,
                primaryColor: preset.color,
              })
            }
            className="p-4 rounded-2xl text-white"
            style={{
              backgroundColor: preset.color,
            }}
          >
            {preset.name}
          </button>
        ))}
      </div>
    </div>
  );
}
