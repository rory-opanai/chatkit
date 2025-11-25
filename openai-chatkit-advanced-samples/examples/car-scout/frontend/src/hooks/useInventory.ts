import { useCallback, useEffect, useMemo, useState } from "react";

import { CAR_INVENTORY_URL } from "../lib/config";

const currencyFormatter = new Intl.NumberFormat("en-GB", {
  style: "currency",
  currency: "GBP",
  maximumFractionDigits: 0,
});
const mileageFormatter = new Intl.NumberFormat("en-GB");

export type CarRecord = {
  id: string;
  name: string;
  make: string;
  model: string;
  trim: string;
  year: number;
  price: number;
  mileage: number;
  body_style: string;
  drivetrain: string;
  fuel_type: string;
  seats: number;
  range_miles: number | null;
  color: string;
  location: string;
  description: string;
  features: string[];
  listing_url: string;
  image_url: string;
};

export type InventoryFilters = {
  price_min: number | null;
  price_max: number | null;
  makes: string[];
  body_styles: string[];
  drivetrains: string[];
  fuel_types: string[];
  seats_min: number | null;
  max_mileage: number | null;
  min_year: number | null;
  must_have_features: string[];
  locations: string[];
};

type InventoryResponse = {
  inventory: {
    cars: CarRecord[];
    filters: InventoryFilters;
    total: number;
  };
};

export function useInventory(threadId: string | null) {
  const [cars, setCars] = useState<CarRecord[]>([]);
  const [filters, setFilters] = useState<InventoryFilters | null>(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInventory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const url = new URL(CAR_INVENTORY_URL, window.location.origin);
      if (threadId) {
        url.searchParams.set("thread_id", threadId);
      }
      const response = await fetch(url.toString(), {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error(`Failed to load inventory (${response.status})`);
      }
      const payload = (await response.json()) as InventoryResponse;
      setCars(payload.inventory.cars);
      setFilters(payload.inventory.filters);
      setTotal(payload.inventory.total);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      setCars([]);
      setFilters(null);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [threadId]);

  useEffect(() => {
    void fetchInventory();
  }, [fetchInventory]);

  const activeFilters = useMemo(() => {
    if (!filters) {
      return [] as string[];
    }
    const chips: string[] = [];
    if (filters.price_min || filters.price_max) {
      if (filters.price_min && filters.price_max) {
        chips.push(
          `${currencyFormatter.format(filters.price_min)}-${currencyFormatter.format(filters.price_max)}`
        );
      } else if (filters.price_min) {
        chips.push(`From ${currencyFormatter.format(filters.price_min)}`);
      } else if (filters.price_max) {
        chips.push(`Under ${currencyFormatter.format(filters.price_max)}`);
      }
    }
    if (filters.seats_min) {
      chips.push(`${filters.seats_min}+ seats`);
    }
    if (filters.max_mileage) {
      chips.push(`< ${mileageFormatter.format(filters.max_mileage)} mi`);
    }
    if (filters.min_year) {
      chips.push(`${filters.min_year}+ model year`);
    }
    if (filters.makes.length) {
      chips.push(`Makes: ${filters.makes.join(", ")}`);
    }
    if (filters.body_styles.length) {
      chips.push(filters.body_styles.join(" · "));
    }
    if (filters.drivetrains.length) {
      chips.push(`Drive: ${filters.drivetrains.join(", ")}`);
    }
    if (filters.fuel_types.length) {
      chips.push(filters.fuel_types.join(" "));
    }
    if (filters.must_have_features.length) {
      chips.push(`Features: ${filters.must_have_features.join(", ")}`);
    }
    if (filters.locations.length) {
      chips.push(`Near ${filters.locations.join(", ")}`);
    }
    return chips;
  }, [filters]);

  return {
    cars,
    filters,
    total,
    activeFilters,
    loading,
    error,
    refresh: fetchInventory,
  };
}
