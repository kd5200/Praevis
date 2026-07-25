import Link from "next/link";
import { notFound } from "next/navigation";

import { ContentPanel } from "@/components/ContentPanel";
import { DecisionBadge } from "@/components/DecisionBadge";
import { FindingsPanel } from "@/components/FindingsPanel";
import { ProvenancePanel } from "@/components/ProvenancePanel";
import { ScanStatusPoller } from "@/components/ScanStatusPoller";
import { ScorePanel } from "@/components/ScorePanel";
import { ApiError, getScan } from "@/lib/api";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ scanId: string }>;
};

export default async function ScanDetailPage({ params }: PageProps) {
  const { scanId } = await params;

  let scan;
  try {
    scan = await getScan(scanId);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <p className="text-sm">
        <Link href="/" className="text-accent hover:underline">
          ← All scans
        </Link>
      </p>

      <section className="mt-6">
        <div className="flex flex-wrap items-center gap-3">
          <DecisionBadge decision={scan.decision} status={scan.status} />
          <span className="rounded-md bg-ink/5 px-2 py-1 font-mono text-xs text-ink-muted">
            {scan.status}
          </span>
        </div>
        <h1 className="mt-4 break-all text-2xl font-semibold tracking-tight text-ink md:text-3xl">
          {scan.submitted_url}
        </h1>
        <p className="mt-2 font-mono text-xs text-ink-muted">scan_id {scan.scan_id}</p>
        <ScanStatusPoller scanId={scan.scan_id} initialStatus={scan.status} />
        {scan.error_message ? (
          <p className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-800" role="alert">
            {scan.error_code ? `${scan.error_code}: ` : ""}
            {scan.error_message}
          </p>
        ) : null}
      </section>

      <section className="mt-10 border-t border-ink/10 pt-8">
        <h2 className="text-lg font-semibold text-ink">Scores</h2>
        <p className="mt-1 text-sm text-ink-muted">
          Risk measures detected danger; trust measures confidence in safe consumption.
        </p>
        <div className="mt-5">
          <ScorePanel riskScore={scan.risk_score} trustScore={scan.trust_score} />
        </div>
      </section>

      <section className="mt-10 border-t border-ink/10 pt-8">
        <h2 className="text-lg font-semibold text-ink">Findings</h2>
        <div className="mt-4">
          <FindingsPanel findings={scan.findings} />
        </div>
      </section>

      <section className="mt-10 border-t border-ink/10 pt-8">
        <h2 className="text-lg font-semibold text-ink">Sanitized content</h2>
        <p className="mt-1 text-sm text-ink-muted">Primary AI-consumable plain text from the gateway.</p>
        <div className="mt-4">
          <ContentPanel content={scan.content} />
        </div>
      </section>

      <section className="mt-10 border-t border-ink/10 pt-8">
        <h2 className="text-lg font-semibold text-ink">Provenance</h2>
        <div className="mt-4">
          <ProvenancePanel
            provenance={scan.provenance}
            finalUrl={scan.final_url}
            normalizedUrl={scan.normalized_url}
          />
        </div>
      </section>

      {scan.score_explanation ? (
        <section className="mt-10 border-t border-ink/10 pt-8">
          <h2 className="text-lg font-semibold text-ink">Score explanation</h2>
          <p className="mt-1 text-sm text-ink-muted">Deterministic contribution breakdown from the scoring engine.</p>
          <pre className="mt-4 max-h-80 overflow-auto rounded-md bg-ink/[0.04] p-4 font-mono text-xs text-ink">
            {JSON.stringify(scan.score_explanation, null, 2)}
          </pre>
        </section>
      ) : null}
    </main>
  );
}
