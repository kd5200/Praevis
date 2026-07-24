"use server";

import { redirect } from "next/navigation";

import { ApiError, createScan } from "@/lib/api";

export type SubmitState = {
  error?: string;
};

export async function submitScanAction(
  _prev: SubmitState,
  formData: FormData,
): Promise<SubmitState> {
  const url = String(formData.get("url") ?? "").trim();
  if (!url) {
    return { error: "Enter a URL to inspect." };
  }

  try {
    const scan = await createScan(url, true);
    redirect(`/scans/${scan.scan_id}`);
  } catch (error) {
    if (error instanceof ApiError) {
      return { error: `Scan failed (${error.status}): ${error.message}` };
    }
    throw error;
  }
}
