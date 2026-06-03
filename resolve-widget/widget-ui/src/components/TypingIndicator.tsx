export default function TypingIndicator() {
  return (
    <div className="flex gap-1 p-3 bg-gray-100 rounded-2xl w-fit">
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" />
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-100" />
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce delay-200" />
    </div>
  );
}
