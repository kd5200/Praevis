import Link from "next/link";

import { getApiBaseUrl, getAppName } from "@/lib/config";

export function AppHeader() {
  const appName = getAppName();
  return (
    <header className="border-b border-ink/10 bg-surface-card/70 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="group">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-accent">{appName}</p>
          <p className="text-sm text-ink-muted group-hover:text-ink">Security gateway</p>
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/" className="text-ink-muted transition hover:text-ink">
            Scans
          </Link>
          <a
            className="text-ink-muted transition hover:text-ink"
            href={`${getApiBaseUrl()}/docs`}
            rel="noreferrer"
            target="_blank"
          >
            API
          </a>
        </nav>
      </div>
    </header>
  );
}
