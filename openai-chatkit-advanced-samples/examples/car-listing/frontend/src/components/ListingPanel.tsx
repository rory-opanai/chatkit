import clsx from "clsx";
import { CheckCircle2, Loader2 } from "lucide-react";

import type { ListingSnapshot } from "../hooks/useListing";

const REQUIRED_COUNT = 21;

type ListingPanelProps = {
  snapshot: ListingSnapshot | null;
  loading: boolean;
  error: string | null;
  onSubmit: () => Promise<void>;
  submitting: boolean;
  onSubmitAnother: () => Promise<void>;
  submitError: string | null;
};

export function ListingPanel({
  snapshot,
  loading,
  error,
  onSubmit,
  submitting,
  onSubmitAnother,
  submitError,
}: ListingPanelProps) {
  if (loading && !snapshot) {
    return (
      <section className="flex h-full flex-col items-center justify-center rounded-3xl border border-slate-200/60 bg-white/80 text-slate-500">
        <Loader2 className="mb-4 h-6 w-6 animate-spin" aria-hidden />
        Preparing draft workspace…
      </section>
    );
  }

  if (error) {
    return (
      <section className="rounded-3xl border border-rose-200 bg-rose-50/60 p-6 text-rose-700 shadow-sm">
        <h2 className="text-xl font-semibold">Listing preview</h2>
        <p className="mt-2 text-sm">{error}</p>
      </section>
    );
  }

  const fields = snapshot?.fields;
  const missing = snapshot?.missing_fields ?? [];
  const completed = countCompleted(fields);
  const denominator = snapshot ? missing.length + completed || REQUIRED_COUNT : REQUIRED_COUNT;
  const progressText = `${completed}/${denominator} fields captured`;
  const submitted = fields?.status === "submitted";

  return (
    <section className="flex h-full flex-col gap-4 overflow-y-auto rounded-3xl border border-slate-200/60 bg-white/90 p-5 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.5)] text-sm">
      <header className="space-y-1">
        <p className="text-xs uppercase tracking-[0.4em] text-slate-400">Listing preview</p>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900">
            {fields?.title || "Vehicle title"}
          </h2>
          <span className="text-sm text-slate-500">{progressText}</span>
        </div>
      </header>

      <div className="rounded-2xl border border-slate-100 bg-gradient-to-br from-slate-50 to-slate-100 p-4">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Title</p>
        <h3 className="mt-2 text-lg font-semibold text-slate-900">
          {fields?.title || "Vehicle title will appear here."}
        </h3>
        <p className="mt-1 text-xs text-slate-600">
          {fields?.location || "Location pending"} · {fields?.asking_price ? formatCurrency(fields.asking_price) : "Price TBD"}
        </p>
        <p className="mt-3 text-sm text-slate-600 leading-relaxed">
          {fields?.description ?? "I'll draft the description for you once we have the full story."}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <InfoCard title="Vehicle details">
          <DetailGrid
            rows={[
              ["Body style", fields?.body_style],
              ["Fuel / Transmission", joinValues(fields?.fuel_type, fields?.transmission)],
              ["Drivetrain", fields?.drivetrain],
              ["Colour", fields?.color],
              ["Mileage", fields?.mileage ? `${fields.mileage.toLocaleString()} miles` : null],
              ["MOT expiry", fields?.mot_expiry],
            ]}
          />
        </InfoCard>
        <InfoCard title="Seller contact">
          <DetailGrid
            rows={[
              ["Seller", fields?.seller_name],
              ["Email", fields?.contact_email],
              ["Phone", fields?.contact_phone],
              ["Service history", fields?.service_history],
            ]}
          />
        </InfoCard>
      </div>

      {missing.length > 0 && !submitted && (
        <div className="rounded-2xl border border-amber-200 bg-amber-50/80 p-4">
          <p className="text-xs uppercase tracking-[0.3em] text-amber-700">Missing fields</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {missing.map((field) => (
              <span
                key={field}
                className="rounded-full border border-amber-200 bg-white/80 px-3 py-1 text-xs font-semibold text-amber-700"
              >
                {formatFieldLabel(field)}
              </span>
            ))}
          </div>
        </div>
      )}

      <InfoCard title="Highlights & media">
        <FeatureList items={fields?.key_features ?? []} placeholder="Add bullet points for key upgrades or extras." />
        <PhotoStrip photos={fields?.photo_urls ?? []} />
      </InfoCard>

      {submitted ? (
        <SuccessBanner onSubmitAnother={onSubmitAnother} />
      ) : (
        <SubmissionBar
          canSubmit={Boolean(snapshot?.completed && !submitting)}
          submitting={submitting}
          missingCount={missing.length}
          onSubmit={onSubmit}
          submitError={submitError}
        />
      )}
    </section>
  );
}

function InfoCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white/90 p-4 shadow-inner">
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{title}</p>
      {children}
    </div>
  );
}

function DetailGrid({ rows }: { rows: [string, string | null][] }) {
  return (
    <dl className="grid grid-cols-1 gap-3 text-sm text-slate-600">
      {rows.map(([label, value]) => (
        <div key={label}>
          <dt className="text-xs uppercase tracking-[0.25em] text-slate-400">{label}</dt>
          <dd className="mt-1 text-base font-medium text-slate-900">{value || "—"}</dd>
        </div>
      ))}
    </dl>
  );
}

function FeatureList({ items, placeholder }: { items: string[]; placeholder: string }) {
  if (!items.length) {
    return <p className="text-sm text-slate-500">{placeholder}</p>;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span
          key={item}
          className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600"
        >
          {item}
        </span>
      ))}
    </div>
  );
}

function PhotoStrip({ photos }: { photos: string[] }) {
  if (!photos.length) {
    return (
      <div className="mt-3 rounded-xl border border-dashed border-slate-200 p-4 text-sm text-slate-500">
        Drop image URLs in the chat to see them here.
      </div>
    );
  }
  return (
    <div className="mt-3 grid grid-cols-3 gap-3">
      {photos.slice(0, 3).map((url) => (
        <div key={url} className="aspect-video overflow-hidden rounded-xl border border-slate-100 bg-slate-100">
          <img src={url} alt="" className="h-full w-full object-cover" loading="lazy" />
        </div>
      ))}
    </div>
  );
}

function SubmissionBar({
  canSubmit,
  submitting,
  missingCount,
  onSubmit,
  submitError,
}: {
  canSubmit: boolean;
  submitting: boolean;
  missingCount: number;
  onSubmit: () => Promise<void>;
  submitError: string | null;
}) {
  return (
    <div className="mt-auto flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white/80 p-4 md:flex-row md:items-center md:justify-between">
      <div className="text-sm text-slate-500">
        {missingCount
          ? `${missingCount} field${missingCount === 1 ? "" : "s"} remaining`
          : "Ready to submit and publish."}
        {submitError && <span className="mt-1 block text-rose-600">{submitError}</span>}
      </div>
      <button
        type="button"
        disabled={!canSubmit || submitting}
        onClick={() => void onSubmit()}
        className={clsx(
          "inline-flex items-center justify-center rounded-full px-6 py-2 text-sm font-semibold text-white shadow transition",
          canSubmit
            ? "bg-emerald-600 hover:bg-emerald-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-600"
            : "bg-slate-400 cursor-not-allowed"
        )}
      >
        {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden />}
        Submit listing
      </button>
    </div>
  );
}

function SuccessBanner({ onSubmitAnother }: { onSubmitAnother: () => Promise<void> }) {
  return (
    <div className="mt-auto flex flex-col gap-4 rounded-2xl border border-emerald-200 bg-emerald-50/80 p-4 text-emerald-800">
      <div className="flex items-center gap-3 text-lg font-semibold">
        <CheckCircle2 className="h-6 w-6" aria-hidden />
        Listing submitted successfully
      </div>
      <p className="text-sm">
        We’ll review and publish it shortly. Feel free to share the summary with your team or start another listing.
      </p>
      <button
        type="button"
        onClick={() => void onSubmitAnother()}
        className="inline-flex w-fit items-center justify-center rounded-full border border-emerald-600 px-4 py-2 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-600 hover:text-white"
      >
        Submit another
      </button>
    </div>
  );
}

function countCompleted(fields: ListingSnapshot["fields"] | undefined) {
  if (!fields) return 0;
  let count = 0;
  for (const [key, value] of Object.entries(fields)) {
    if (key === "status" || key === "submitted_at" || key === "title") continue;
    if (Array.isArray(value)) {
      if (value.length) count += 1;
    } else if (value !== null && value !== "") {
      count += 1;
    }
  }
  return count;
}

function joinValues(...values: (string | null | undefined)[]) {
  return values.filter(Boolean).join(" · ") || null;
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatFieldLabel(field: string) {
  return field
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}
