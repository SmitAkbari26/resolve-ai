import { Settings2 } from "lucide-react";

interface Props {
  config: any;
  setConfig: (config: any) => void;
}

export default function BehaviorControls({ config, setConfig }: Props) {
  const Toggle = ({ label, keyName }: any) => (
    <label className="flex justify-between items-center">
      <span>{label}</span>

      <input
        type="checkbox"
        checked={config[keyName]}
        onChange={(e) =>
          setConfig({
            ...config,
            [keyName]: e.target.checked,
          })
        }
      />
    </label>
  );

  return (
    <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 space-y-5">
      <div className="flex items-center gap-3">
        <Settings2 className="text-emerald-400" />
        <h3 className="font-semibold">Behavior</h3>
      </div>

      <Toggle label="Show Badge" keyName="showBadge" />

      <Toggle label="Mobile Fullscreen" keyName="fullscreenMobile" />

      <Toggle label="Auto Open" keyName="autoOpen" />
    </div>
  );
}
