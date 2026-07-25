"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import type { Scan } from "@/lib/types";
import { getApiBaseUrl } from "@/lib/config";

const TERMINAL = new Set(["completed", "blocked", "failed"]);

export function ScanStatusPoller({
  scanId,
  initialStatus,
}: {
  scanId: string;
  initialStatus: string;
}) {
  const router = useRouter();
  const [status, setStatus] = useState(initialStatus);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (TERMINAL.has(initialStatus)) {
      return;
    }

    let cancelled = false;
    const interval = window.setInterval(async () => {
      try {
        const response = await fetch(`${getApiBaseUrl()}/v1/scans/${scanId}`, {
          headers: { Accept: "application/json" },
          cache: "no-store",
        });
        if (!response.ok) {
          throw new Error(`poll failed (${response.status})`);
        }
        const data = (await response.json()) as Scan;
        if (cancelled) return;
        setStatus(data.status);
        if (TERMINAL.has(data.status)) {
          window.clearInterval(interval);
          router.refresh();
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Polling failed");
        }
      }
    }, 1500);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [scanId, initialStatus, router]);

  if (TERMINAL.has(initialStatus) && TERMINAL.has(status)) {
    return null;
  }

  return (
    <div className="mt-4 rounded-md border border-accent/20 bg-accent/5 px-3 py-2 text-sm text-ink">
      <p>
        Scan in progress: <span className="font-mono font-medium">{status}</span>
      </p>
      <p className="mt-1 text-xs text-ink-muted">Polling every 1.5s until the scan finishes.</p>
      {error ? (
        <p className="mt-1 text-xs text-red-700" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
