const prompts = [
  "Pricing plans",
  "Product support",
  "Talk to sales",
  "Technical help",
];

export default function SuggestedPrompts({
  onSelect,
}: {
  onSelect: (text: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {prompts.map((p) => (
        <button
          key={p}
          onClick={() => onSelect(p)}
          className="px-3 py-2 rounded-full bg-gray-100 hover:bg-gray-200 text-sm cursor-pointer"
        >
          {p}
        </button>
      ))}
    </div>
  );
}
