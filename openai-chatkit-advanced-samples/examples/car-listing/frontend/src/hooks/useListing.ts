import { useCallback, useEffect, useState } from "react";

import { LISTING_DRAFT_URL, LISTING_RESET_URL, LISTING_SUBMIT_URL } from "../lib/config";

export type ListingFields = {
  title: string | null;
  seller_name: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  make: string | null;
  model: string | null;
  year: number | null;
  trim: string | null;
  body_style: string | null;
  fuel_type: string | null;
  transmission: string | null;
  drivetrain: string | null;
  color: string | null;
  mileage: number | null;
  asking_price: number | null;
  location: string | null;
  mot_expiry: string | null;
  service_history: string | null;
  description: string | null;
  key_features: string[];
  photo_urls: string[];
  status: string;
  submitted_at: string | null;
};

export type ListingSnapshot = {
  fields: ListingFields;
  missing_fields: string[];
  completed: boolean;
};

type ListingResponse = {
  listing: ListingSnapshot;
};

export function useListing(threadId: string | null) {
  const [snapshot, setSnapshot] = useState<ListingSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchListing = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const url = new URL(LISTING_DRAFT_URL, window.location.origin);
      if (threadId) {
        url.searchParams.set("thread_id", threadId);
      }
      const response = await fetch(url.toString(), {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error(`Failed to load listing (${response.status})`);
      }
      const payload = (await response.json()) as ListingResponse;
      setSnapshot(payload.listing);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message);
      setSnapshot(null);
    } finally {
      setLoading(false);
    }
  }, [threadId]);

  useEffect(() => {
    void fetchListing();
  }, [fetchListing]);

  return {
    snapshot,
    loading,
    error,
    refresh: fetchListing,
  };
}

export async function submitListingDraft(threadId: string) {
  const url = new URL(LISTING_SUBMIT_URL, window.location.origin);
  url.searchParams.set("thread_id", threadId);
  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Unable to submit listing");
  }
  return (await response.json()) as { status: string; submitted_at: string | null };
}

export async function resetListingDraft(threadId: string) {
  const url = new URL(LISTING_RESET_URL, window.location.origin);
  url.searchParams.set("thread_id", threadId);
  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Unable to reset listing");
  }
  return response.json();
}
