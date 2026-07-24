import Link from "next/link";

export default function ScanNotFound() {
  return (
    <main className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-2xl font-semibold text-ink">Scan not found</h1>
      <p className="mt-2 text-ink-muted">That scan id does not exist or is no longer available.</p>
      <Link href="/" className="mt-6 inline-block text-accent hover:underline">
        ← Back to scans
      </Link>
    </main>
  );
}
