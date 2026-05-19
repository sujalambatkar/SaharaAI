import type { Message } from "@/lib/types";
import { LanguageBadge } from "./language-badge";
import { ConfidenceBar } from "./confidence-bar";
import { SourceChips } from "./source-chips";
import { HandoffCard } from "./handoff-card";
import { ExternalLink } from "lucide-react";

function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

export function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  const meta = message.metadata;

  if (isUser) {
    return (
      <div className="flex justify-end mb-3">
        <div className="max-w-[75%]">
          <div className="bg-sahara-saffron text-white px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm leading-relaxed">
            {message.content}
          </div>
          <p className="text-[10px] text-gray-400 text-right mt-1 pr-1">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-3">
      <div className="flex gap-2.5 max-w-[80%]">
        {/* Avatar */}
        <div className="flex-shrink-0 w-7 h-7 rounded-full bg-sahara-saffron text-white text-xs font-bold flex items-center justify-center mt-0.5">
          S
        </div>

        <div className="flex-1">
          {/* Main bubble */}
          <div className="bg-white border border-gray-100 shadow-sm px-4 py-3 rounded-2xl rounded-tl-sm">
            {meta?.handoff_triggered ? (
              <HandoffCard message={message.content} />
            ) : (
              <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
                {message.content}
              </p>
            )}

            {/* Metadata row */}
            {meta && (
              <div className="mt-2.5 pt-2.5 border-t border-gray-50">
                <div className="flex items-center gap-2 flex-wrap">
                  <LanguageBadge language={meta.language_detected} />
                  <span className="text-[10px] text-gray-400 font-mono uppercase">
                    {meta.retrieval_mode_used}
                  </span>
                  {meta.trace_url && (
                    <a
                      href={meta.trace_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-0.5 text-[10px] text-blue-400 hover:text-blue-600 transition-colors"
                    >
                      <ExternalLink size={9} />
                      trace
                    </a>
                  )}
                </div>
                <ConfidenceBar confidence={meta.confidence} />
                <SourceChips sources={meta.sources} />
              </div>
            )}
          </div>

          <p className="text-[10px] text-gray-400 mt-1 pl-1">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    </div>
  );
}
