import { Building2, MessageSquare } from "lucide-react";

interface Props {
  companyName: string;
  welcomeMessage: string;
  onCompanyChange: (value: string) => void;
  onWelcomeChange: (value: string) => void;
}

export default function WidgetSettings({
  companyName,
  welcomeMessage,
  onCompanyChange,
  onWelcomeChange,
}: Props) {
  return (
    <div className="space-y-6">
      <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Building2 className="w-5 h-5 text-emerald-400" />
          <h3 className="text-slate-100 font-semibold">Company Name</h3>
        </div>

        <input
          value={companyName}
          onChange={(e) => onCompanyChange(e.target.value)}
          className="w-full bg-slate-900 border border-slate-700 rounded-2xl p-4 text-white"
        />
      </div>

      <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <MessageSquare className="w-5 h-5 text-emerald-400" />
          <h3 className="text-slate-100 font-semibold">Welcome Message</h3>
        </div>

        <textarea
          value={welcomeMessage}
          onChange={(e) => onWelcomeChange(e.target.value)}
          className="w-full h-28 bg-slate-900 border border-slate-700 rounded-2xl p-4 text-white"
        />
      </div>
    </div>
  );
}
