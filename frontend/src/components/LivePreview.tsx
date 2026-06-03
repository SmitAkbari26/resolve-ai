import { Monitor, Smartphone, RefreshCw } from "lucide-react";
import { useState } from "react";

export default function LivePreview() {
  const [mobile, setMobile] = useState(false);

  return (
    <div className="h-full bg-slate-950 flex flex-col">
      {/* Top Bar */}
      <div className="h-16 px-6 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Monitor className="w-5 h-5 text-emerald-400" />
          <span className="font-semibold">Live Preview</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setMobile(false)}
            className={`p-2 rounded-xl ${
              !mobile ? "bg-emerald-500 text-white" : "bg-slate-800"
            }`}
          >
            <Monitor size={18} />
          </button>

          <button
            onClick={() => setMobile(true)}
            className={`p-2 rounded-xl ${
              mobile ? "bg-emerald-500 text-white" : "bg-slate-800"
            }`}
          >
            <Smartphone size={18} />
          </button>

          <button className="p-2 rounded-xl bg-slate-800">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Device Preview */}
      <div className="flex-1 flex items-center justify-center p-10 overflow-hidden">
        {!mobile ? (
          <div className="relative">
            {/* Monitor */}
            <div className="bg-slate-800 rounded-[28px] p-3 shadow-2xl border border-slate-700">
              <div className="w-[1100px] h-[650px] bg-white rounded-2xl overflow-hidden">
                <iframe
                  id="preview-frame"
                  src="http://localhost:5175"
                  className="w-full h-full border-0"
                />
              </div>
            </div>

            {/* Monitor Stand */}
            <div className="flex justify-center">
              <div className="w-24 h-6 bg-slate-700 rounded-b-xl" />
            </div>

            <div className="flex justify-center">
              <div className="w-48 h-4 bg-slate-800 rounded-full" />
            </div>
          </div>
        ) : (
          <div className="bg-slate-800 p-3 rounded-[40px] border border-slate-700 shadow-2xl">
            <div className="w-[390px] h-[800px] bg-white rounded-[32px] overflow-hidden">
              <iframe
                id="preview-frame"
                src="http://localhost:5175"
                className="w-full h-full border-0"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
