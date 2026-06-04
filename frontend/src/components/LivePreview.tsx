import { Monitor, Smartphone, RefreshCw } from "lucide-react";
import { useEffect, useRef, useState } from "react";

interface LivePreviewProps {
  config: Record<string, unknown>;
}

export default function LivePreview({ config }: LivePreviewProps) {
  const [mobile, setMobile] = useState(false);
  const desktopRef = useRef<HTMLIFrameElement>(null);
  const mobileRef = useRef<HTMLIFrameElement>(null);

  /** Push the latest config into whichever iframe is currently visible */
  const postConfig = (payload: Record<string, unknown>) => {
    const iframe = mobile ? mobileRef.current : desktopRef.current;
    if (iframe?.contentWindow) {
      iframe.contentWindow.postMessage(
        { type: "UPDATE_WIDGET_CONFIG", payload },
        "*",
      );
    }
  };

  /** Re-post every time config or the active view changes */
  useEffect(() => {
    // Small delay so the iframe has time to load on first render
    const id = setTimeout(() => postConfig(config), 300);
    return () => clearTimeout(id);
  }, [config, mobile]);

  const handleRefresh = () => {
    const iframe = mobile ? mobileRef.current : desktopRef.current;
    if (iframe) {
      const src = iframe.src;
      iframe.src = "";
      requestAnimationFrame(() => {
        iframe.src = src;
      });
    }
  };

  const WIDGET_URL = "http://localhost:5175";

  return (
    <div className="h-[calc(100%-3rem)] bg-slate-950 flex flex-col">
      {/* Top Bar */}
      <div className="h-16 px-6 border-b border-slate-800/80 flex items-center justify-between bg-slate-900/45">
        <div className="flex items-center gap-3">
          <Monitor className="w-5 h-5 text-emerald-400" />
          <span className="font-semibold text-slate-200">Live Preview</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setMobile(false)}
            className={`p-2 rounded-xl transition-all border ${
              !mobile
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
            }`}
          >
            <Monitor size={18} />
          </button>

          <button
            onClick={() => setMobile(true)}
            className={`p-2 rounded-xl transition-all border ${
              mobile
                ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
                : "bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200"
            }`}
          >
            <Smartphone size={18} />
          </button>

          <button
            onClick={handleRefresh}
            className="p-2 rounded-xl bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200 transition-all"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Device Preview */}
      <div className="flex-1 w-full bg-slate-950 relative overflow-hidden flex items-center justify-center">
        {/* ── Desktop ── */}
        <iframe
          ref={desktopRef}
          id="preview-frame-desktop"
          src={WIDGET_URL}
          className={`border-0 bg-slate-950 ${mobile ? "hidden" : "w-full h-full"}`}
          onLoad={() => postConfig(config)}
        />

        {/* ── Mobile phone shell ── */}
        {mobile && (
          <div className="w-full h-full flex items-center justify-center p-6 bg-slate-950/80">
            <div className="h-full max-h-[92%] aspect-[9/18.5] bg-[#0d111c] p-3 rounded-[48px] border-4 border-slate-800 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.9)] ring-1 ring-white/10 flex flex-col relative">
              {/* Dynamic Island / Notch */}
              <div className="absolute top-5 left-1/2 -translate-x-1/2 w-28 h-4.5 bg-black rounded-full flex items-center justify-center gap-1.5 z-10 border border-slate-850 shadow-inner">
                <div className="w-10 h-0.75 bg-slate-800 rounded-full" />
                <div className="w-2 h-2 rounded-full bg-slate-900 border border-indigo-950/60 relative">
                  <div className="absolute top-0.5 left-0.5 w-0.5 h-0.5 rounded-full bg-white/40" />
                </div>
              </div>

              {/* Screen */}
              <div className="w-full h-full bg-slate-950 rounded-[38px] overflow-hidden border border-slate-900 relative flex flex-col">
                <div className="h-7 w-full bg-slate-950 shrink-0" />
                <iframe
                  ref={mobileRef}
                  id="preview-frame-mobile"
                  src={WIDGET_URL}
                  className="w-full flex-1 border-0 bg-slate-950"
                  onLoad={() => postConfig(config)}
                />
                <div className="h-4.5 w-full bg-slate-950 shrink-0 flex items-center justify-center">
                  <div className="w-28 h-1 bg-slate-750/85 rounded-full" />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
