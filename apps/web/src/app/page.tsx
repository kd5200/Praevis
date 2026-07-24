import { ScanForm } from "@/components/ScanForm";
import { ScanList } from "@/components/ScanList";
import { listScans } from "@/lib/api";
import { getAppName } from "@/lib/config";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const appName = getAppName();
  let scans: Awaited<ReturnType<typeof listScans>> = { items: [], total: 0 };
  let listError: string | null = null;

  try {
    scans = await listScans(20);
  } catch (error) {
    listError = error instanceof Error ? error.message : "Unable to load recent scans.";
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <section className="max-w-2xl">
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-accent">{appName}</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-ink md:text-4xl">
          Inspect untrusted URLs before agents consume them
        </h1>
        <p className="mt-3 text-ink-muted">
          Submit a URL to the security gateway. Review the decision, scores, findings, and
          sanitized content with provenance.
        </p>
      </section>

      <section className="mt-10 max-w-2xl rounded-md border border-ink/10 bg-surface-card/80 p-5 shadow-sm">
        <ScanForm />
      </section>

      <section className="mt-14">
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-ink">Recent scans</h2>
            <p className="mt-1 text-sm text-ink-muted">
              {listError ? listError : `${scans.total} total`}
            </p>
          </div>
        </div>
        {listError ? null : <ScanList scans={scans.items} />}
      </section>
    </main>
  );
}
