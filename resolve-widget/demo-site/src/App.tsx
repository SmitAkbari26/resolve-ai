import { useEffect } from "react";
import {
  ShieldCheck,
  Zap,
  Cpu,
  Globe,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

export default function App() {
  useEffect(() => {
    (window as any).ResolveAIConfig = {
      apiKey: "rw_live_nova_123456",
    };

    const script = document.createElement("script");
    const link = document.createElement("link");

    script.src =
      "https://cdn.jsdelivr.net/gh/SmitAkbari26/resolve-ai@main/resolve-widget/cdn/widget.js";

    document.body.appendChild(script);

    link.rel = "stylesheet";

    link.href =
      "https://cdn.jsdelivr.net/gh/SmitAkbari26/resolve-ai@main/resolve-widget/cdn/widget.css";

    document.head.appendChild(link);

    console.log("Widget CSS Loaded");
  }, []);
  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(139,92,246,0.18),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(16,185,129,0.15),transparent_35%)]" />

      {/* Navbar */}
      <header className="sticky top-0 z-40 backdrop-blur-xl bg-slate-950/80 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-8 py-5 flex items-center justify-between">
          <div className="text-2xl font-bold text-emerald-400">
            Nova Electronics
          </div>

          <nav className="hidden md:flex gap-10 text-slate-300">
            <a href="#" className="hover:text-white transition">
              Products
            </a>
            <a href="#" className="hover:text-white transition">
              Solutions
            </a>
            <a href="#" className="hover:text-white transition">
              Pricing
            </a>
            <a href="#" className="hover:text-white transition">
              Support
            </a>
          </nav>

          <button className="px-5 py-3 rounded-xl bg-emerald-500 font-medium hover:scale-105 transition">
            Get Started
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative max-w-7xl mx-auto px-8 py-28 grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-900 border border-slate-800 text-emerald-400 text-sm mb-8">
            <Zap size={16} />
            AI-Powered Consumer Intelligence
          </div>

          <h1 className="text-6xl lg:text-7xl font-bold leading-tight">
            Smart Devices for
            <span className="block bg-linear-to-r from-emerald-400 to-violet-500 bg-clip-text text-transparent">
              Modern Living
            </span>
          </h1>

          <p className="mt-8 text-xl text-slate-300 leading-relaxed max-w-xl">
            Experience next-generation electronics powered by intelligent
            automation, predictive support, and seamless connectivity.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <button className="px-7 py-4 rounded-2xl bg-emerald-500 font-semibold flex items-center gap-2 hover:scale-105 transition">
              Explore Products
              <ArrowRight size={18} />
            </button>

            <button className="px-7 py-4 rounded-2xl border border-slate-700 hover:border-slate-500 transition">
              Book Demo
            </button>
          </div>

          <div className="mt-12 flex gap-8 text-slate-400">
            <Stat number="250K+" label="Active Devices" />
            <Stat number="99.99%" label="Uptime" />
            <Stat number="24/7" label="AI Support" />
          </div>
        </div>

        {/* Dashboard Preview */}
        <div className="relative">
          <div className="absolute inset-0 bg-linear-to-r from-emerald-500/20 to-violet-500/20 blur-3xl rounded-full" />

          <div className="relative bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
            <div className="space-y-6">
              <DashboardCard
                icon={<Cpu />}
                title="AI Device Hub"
                text="Control every connected device from one intelligence layer."
              />

              <DashboardCard
                icon={<ShieldCheck />}
                title="Predictive Protection"
                text="Advanced diagnostics prevent failures before they happen."
              />

              <DashboardCard
                icon={<Globe />}
                title="Global Connectivity"
                text="Seamless synchronization across every environment."
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-8 py-24">
        <h2 className="text-4xl font-bold text-center mb-16">
          Why Customers Choose Nova
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            title="Instant AI Assistance"
            text="Resolve issues instantly through intelligent support automation."
          />

          <FeatureCard
            title="Enterprise Security"
            text="Built with multi-layer device and cloud protection."
          />

          <FeatureCard
            title="Adaptive Automation"
            text="Devices learn your behavior and optimize automatically."
          />
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-slate-900 py-24 border-y border-slate-800">
        <div className="max-w-7xl mx-auto px-8">
          <h2 className="text-4xl font-bold text-center mb-16">
            Pricing Plans
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <PricingCard
              title="Starter"
              price="$29"
              features={[
                "Smart hub access",
                "Email support",
                "Basic automation",
              ]}
            />

            <PricingCard
              featured
              title="Professional"
              price="$79"
              features={[
                "AI predictive support",
                "Priority assistance",
                "Advanced automation",
              ]}
            />

            <PricingCard
              title="Enterprise"
              price="$199"
              features={[
                "Unlimited integrations",
                "Dedicated AI support",
                "Custom deployments",
              ]}
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 text-center text-slate-500">
        © 2026 Nova Electronics
      </footer>
    </div>
  );
}

function Stat({ number, label }: { number: string; label: string }) {
  return (
    <div>
      <div className="text-2xl font-bold text-white">{number}</div>
      <div className="text-sm">{label}</div>
    </div>
  );
}

function DashboardCard({
  icon,
  title,
  text,
}: {
  icon: React.ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
      <div className="text-emerald-400 mb-4">{icon}</div>
      <h3 className="font-semibold text-lg">{title}</h3>
      <p className="text-slate-400 mt-2">{text}</p>
    </div>
  );
}

function FeatureCard({ title, text }: { title: string; text: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8">
      <CheckCircle2 className="text-emerald-400 mb-5" />
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="text-slate-400 mt-3">{text}</p>
    </div>
  );
}

function PricingCard({
  title,
  price,
  features,
  featured,
}: {
  title: string;
  price: string;
  features: string[];
  featured?: boolean;
}) {
  return (
    <div
      className={`rounded-3xl p-8 border ${
        featured
          ? "border-emerald-500 bg-slate-800 scale-105"
          : "border-slate-800 bg-slate-950"
      }`}
    >
      <h3 className="text-2xl font-bold">{title}</h3>

      <div className="text-5xl font-bold mt-5">{price}</div>

      <ul className="mt-8 space-y-4 text-slate-300">
        {features.map((feature) => (
          <li key={feature}>{feature}</li>
        ))}
      </ul>

      <button className="w-full mt-8 py-4 rounded-2xl bg-emerald-500 font-semibold hover:scale-105 transition">
        Choose Plan
      </button>
    </div>
  );
}
