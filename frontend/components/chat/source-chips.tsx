export function SourceChips({ sources }: { sources: string[] }) {
  if (!sources.length) return null;

  return (
    <div className="flex flex-wrap gap-1 mt-2">
      <span className="text-[10px] text-gray-400 self-center">Sources:</span>
      {sources.map((src) => (
        <span
          key={src}
          className="text-[10px] px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded font-mono border border-gray-200"
        >
          {src}
        </span>
      ))}
    </div>
  );
}
