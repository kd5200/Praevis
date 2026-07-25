"use client";

import { useFormStatus } from "react-dom";
import { useActionState } from "react";

import { submitScanAction, type SubmitState } from "@/app/actions";

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className="rounded-md bg-accent px-4 py-2.5 text-sm font-medium text-white transition hover:opacity-90 disabled:cursor-wait disabled:opacity-60"
    >
      {pending ? "Submitting…" : "Inspect URL"}
    </button>
  );
}

const initial: SubmitState = {};

export function ScanForm() {
  const [state, action] = useActionState(submitScanAction, initial);

  return (
    <form action={action} className="space-y-3">
      <label className="block text-sm font-medium text-ink" htmlFor="url">
        URL to inspect
      </label>
      <div className="flex flex-col gap-3 sm:flex-row">
        <input
          id="url"
          name="url"
          type="text"
          required
          placeholder="fixture://direct-prompt-injection.html"
          className="w-full flex-1 rounded-md border border-ink/15 bg-white px-3 py-2.5 text-sm text-ink outline-none ring-accent/30 placeholder:text-ink-muted/70 focus:ring-2"
        />
        <SubmitButton />
      </div>
      <label className="flex items-center gap-2 text-sm text-ink-muted">
        <input
          type="checkbox"
          name="wait_for_completion"
          value="true"
          defaultChecked
          className="rounded border-ink/30 text-accent focus:ring-accent"
        />
        Wait for completion (sync). Uncheck to queue for the worker and poll status.
      </label>
      {state.error ? (
        <p className="text-sm text-red-700" role="alert">
          {state.error}
        </p>
      ) : (
        <p className="text-xs text-ink-muted">
          Try a failing demo: <code>fixture://direct-prompt-injection.html</code>. Async mode
          requires <code>make worker</code>.
        </p>
      )}
    </form>
  );
}
