import { getApiBaseUrl } from "./config";
import type { Scan, ScanList } from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = String(body.detail);
    } catch {
      // ignore
    }
    throw new ApiError(detail || "API request failed", response.status);
  }
  return (await response.json()) as T;
}

export async function createScan(url: string, waitForCompletion = true): Promise<Scan> {
  const response = await fetch(`${getApiBaseUrl()}/v1/scans`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({
      url,
      mode: "standard",
      wait_for_completion: waitForCompletion,
    }),
    cache: "no-store",
  });
  return parseJson<Scan>(response);
}

export async function getScan(scanId: string): Promise<Scan> {
  const response = await fetch(`${getApiBaseUrl()}/v1/scans/${scanId}`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  return parseJson<Scan>(response);
}

export async function listScans(limit = 20): Promise<ScanList> {
  const response = await fetch(`${getApiBaseUrl()}/v1/scans?limit=${limit}`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  return parseJson<ScanList>(response);
}
