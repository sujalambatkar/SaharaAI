import { PhoneCall } from "lucide-react";

export function HandoffCard({ message }: { message: string }) {
  return (
    <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg flex gap-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center">
        <PhoneCall size={14} className="text-amber-600" />
      </div>
      <div>
        <p className="text-xs font-semibold text-amber-800 mb-0.5">
          Connecting to Support Team
        </p>
        <p className="text-xs text-amber-700 leading-relaxed">{message}</p>
        <div className="mt-2 flex gap-2">
          <a
            href="mailto:support@saharaai.in"
            className="text-[10px] px-2 py-1 bg-amber-200 text-amber-800 rounded hover:bg-amber-300 transition-colors"
          >
            Email Support
          </a>
          <a
            href="tel:1800XXXXXXX"
            className="text-[10px] px-2 py-1 bg-amber-200 text-amber-800 rounded hover:bg-amber-300 transition-colors"
          >
            Call 1800-XXX-XXXX
          </a>
        </div>
      </div>
    </div>
  );
}
