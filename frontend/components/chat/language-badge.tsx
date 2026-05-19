import type { LanguageDetected } from "@/lib/types";

const BADGE_CONFIG: Record<
  LanguageDetected,
  { label: string; className: string }
> = {
  EN: {
    label: "EN",
    className: "bg-blue-100 text-blue-700 border border-blue-200",
  },
  HI: {
    label: "हिं",
    className: "bg-orange-100 text-orange-700 border border-orange-200",
  },
  HINGLISH: {
    label: "HIN",
    className: "bg-green-100 text-green-700 border border-green-200",
  },
};

export function LanguageBadge({ language }: { language: LanguageDetected }) {
  const config = BADGE_CONFIG[language];
  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold tracking-wide ${config.className}`}
      title={`Detected: ${language}`}
    >
      {config.label}
    </span>
  );
}
