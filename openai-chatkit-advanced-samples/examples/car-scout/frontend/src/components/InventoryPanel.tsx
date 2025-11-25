import clsx from "clsx";

import type { CarRecord, InventoryFilters } from "../hooks/useInventory";

const currency = new Intl.NumberFormat("en-GB", {
  style: "currency",
  currency: "GBP",
  maximumFractionDigits: 0,
});
const mileageFormat = new Intl.NumberFormat("en-GB");

type InventoryPanelProps = {
  cars: CarRecord[];
  filters: InventoryFilters | null;
  total: number;
  activeFilters: string[];
  loading: boolean;
  error: string | null;
};

export function InventoryPanel({ cars, filters, total, activeFilters, loading, error }: InventoryPanelProps) {
  if (loading) {
    return (
      <section className="flex h-full flex-col gap-4 rounded-3xl border border-slate-200/60 bg-white/80 p-6 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.5)] ring-1 ring-slate-200/60 backdrop-blur dark:border-slate-800/70 dark:bg-slate-900/70 dark:shadow-[0_45px_95px_-55px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
        <header>
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">Matching vehicles</h2>
          <p className="text-sm text-slate-500 dark:text-slate-300">Pulling the latest inventory…</p>
        </header>
        <div className="flex flex-1 items-center justify-center text-sm text-slate-500 dark:text-slate-400">
          Let me check the garage.
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="flex h-full flex-col gap-4 rounded-3xl border border-rose-200 bg-rose-50/60 p-6 text-rose-700 shadow-sm dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-200">
        <header>
          <h2 className="text-xl font-semibold">Matching vehicles</h2>
        </header>
        <p className="text-sm">{error}</p>
      </section>
    );
  }

  return (
    <section className="flex h-full flex-col gap-4 overflow-hidden rounded-3xl border border-slate-200/60 bg-white/85 p-6 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.5)] ring-1 ring-slate-200/60 backdrop-blur dark:border-slate-800/70 dark:bg-slate-900/75 dark:shadow-[0_45px_95px_-55px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
      <header className="space-y-1">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400 dark:text-slate-500">Inventory matches</p>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
              {total ? `${total} car${total === 1 ? "" : "s"}` : "No matches yet"}
            </h2>
          </div>
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-700 dark:border-emerald-900/60 dark:bg-emerald-900/30 dark:text-emerald-200">
            Live refresh
          </div>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          {filters?.price_min || filters?.price_max
            ? "Filtered by your latest preferences."
            : "Showing the full lot until you narrow it down."}
        </p>
      </header>

      {activeFilters.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {activeFilters.map((chip) => (
            <span
              key={chip}
              className="inline-flex items-center rounded-full border border-slate-200/70 bg-white/90 px-3 py-1 text-xs font-medium text-slate-600 shadow-sm dark:border-slate-800/70 dark:bg-slate-900/70 dark:text-slate-200"
            >
              {chip}
            </span>
          ))}
        </div>
      )}

      <div className="flex-1 overflow-y-auto pr-1">
        {cars.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center text-sm text-slate-500 dark:text-slate-400">
            <p>No vehicles match those filters yet.</p>
            <p>Try relaxing price, mileage, or drive type and I'll widen the list.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {cars.map((car) => (
              <CarCard key={car.id} car={car} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

function CarCard({ car }: { car: CarRecord }) {
  return (
    <article className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white/95 p-4 shadow-sm transition hover:border-emerald-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900/80">
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="aspect-video h-40 w-full overflow-hidden rounded-xl bg-slate-200/60 sm:w-56">
          <img
            src={car.image_url}
            alt={car.name}
            className="h-full w-full object-cover"
            loading="lazy"
          />
        </div>
        <div className="flex flex-1 flex-col justify-between gap-2">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-slate-400 dark:text-slate-500">
              {car.location}
            </p>
            <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100">{car.name}</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">{car.description}</p>
          </div>
          <dl className="grid grid-cols-2 gap-2 text-sm text-slate-600 dark:text-slate-300">
            <InventoryFact label="Price">{currency.format(car.price)}</InventoryFact>
            <InventoryFact label="Mileage">{mileageFormat.format(car.mileage)} mi</InventoryFact>
            <InventoryFact label="Setup">{`${car.body_style} · ${car.drivetrain}`}</InventoryFact>
            <InventoryFact label="Fuel">{car.fuel_type}</InventoryFact>
          </dl>
          <div className="flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-400">
            {car.features.slice(0, 4).map((feature) => (
              <span
                key={feature}
                className="rounded-full border border-slate-200/70 bg-slate-50/70 px-2 py-0.5 dark:border-slate-700 dark:bg-slate-800/60"
              >
                {feature}
              </span>
            ))}
          </div>
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400 dark:text-slate-500">
          {car.range_miles ? `${car.range_miles} mi est. range` : `${car.seats} seats`}
        </p>
        <a
          href={car.listing_url}
          target="_blank"
          rel="noreferrer"
          className={clsx(
            "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold text-white shadow focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
            "bg-emerald-600 hover:bg-emerald-500 focus-visible:outline-emerald-600",
          )}
        >
          More info
        </a>
      </div>
    </article>
  );
}

function InventoryFact({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200/60 bg-slate-50/70 px-3 py-2 dark:border-slate-800/70 dark:bg-slate-900/60">
      <dt className="text-xs uppercase tracking-wide text-slate-400 dark:text-slate-500">{label}</dt>
      <dd className="text-sm font-semibold text-slate-900 dark:text-slate-100">{children}</dd>
    </div>
  );
}
