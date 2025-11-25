import { useCallback, useState } from "react";
import clsx from "clsx";

import { ChatKitPanel } from "./ChatKitPanel";
import { ListingPanel } from "./ListingPanel";
import { resetListingDraft, submitListingDraft, useListing } from "../hooks/useListing";

export default function Home() {
  const [threadId, setThreadId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const { snapshot, loading, error, refresh } = useListing(threadId);

  const handleThreadChange = useCallback((nextThreadId: string | null) => {
    setThreadId(nextThreadId);
  }, []);

  const handleResponseCompleted = useCallback(() => {
    void refresh();
  }, [refresh]);

  const handleSubmit = useCallback(async () => {
    if (!threadId) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      await submitListingDraft(threadId);
      await refresh();
    } catch (err) {
      console.error(err);
      const message = err instanceof Error ? err.message : "Unable to submit listing.";
      setSubmitError(message);
    } finally {
      setSubmitting(false);
    }
  }, [threadId, refresh]);

  const handleSubmitAnother = useCallback(async () => {
    if (threadId) {
      try {
        await resetListingDraft(threadId);
      } catch (err) {
        console.error(err);
      }
    }
    window.location.reload();
  }, [threadId]);

  const containerClass = clsx(
    "min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 text-slate-900"
  );

  return (
    <div className={containerClass}>
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-8 lg:h-screen lg:max-h-screen lg:py-10">
        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Listing builder</p>
          <h1 className="text-3xl font-semibold sm:text-4xl">Guide every seller through the same checklist</h1>
          <p className="max-w-3xl text-sm text-slate-600">
            Chat on the left to collect details; the preview on the right auto-fills each field so every listing launches with the same structure.
          </p>
        </header>

        <div className="grid flex-1 grid-cols-1 gap-8 lg:h-[calc(100vh-240px)] lg:grid-cols-[minmax(320px,380px)_1fr] lg:items-stretch xl:grid-cols-[minmax(360px,420px)_1fr]">
          <section className="flex flex-1 flex-col overflow-hidden rounded-3xl border border-slate-200/60 bg-white shadow-[0_45px_90px_-45px_rgba(15,23,42,0.6)]">
            <ChatKitPanel
              onThreadChange={handleThreadChange}
              onResponseCompleted={handleResponseCompleted}
            />
          </section>

          <ListingPanel
            snapshot={snapshot}
            loading={loading}
            error={error}
            onSubmit={handleSubmit}
            submitting={submitting}
            onSubmitAnother={handleSubmitAnother}
            submitError={submitError}
          />
        </div>
      </div>
    </div>
  );
}
