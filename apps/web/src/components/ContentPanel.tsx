import type { ScanContent } from "@/lib/types";

export function ContentPanel({ content }: { content?: ScanContent | null }) {
  if (!content) {
    return <p className="text-sm text-ink-muted">No sanitized content available.</p>;
  }

  return (
    <div className="space-y-3">
      {content.title ? <h3 className="text-lg font-medium text-ink">{content.title}</h3> : null}
      <p className="font-mono text-xs text-ink-muted">{content.content_type ?? "unknown type"}</p>
      <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-md bg-ink/[0.04] p-4 text-sm leading-relaxed text-ink">
        {content.text || "(empty)"}
      </pre>
    </div>
  );
}
