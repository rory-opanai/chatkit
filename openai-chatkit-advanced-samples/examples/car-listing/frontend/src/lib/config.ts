import { StartScreenPrompt } from "@openai/chatkit";

const LISTING_API_BASE = import.meta.env.VITE_LISTING_API_BASE ?? "/listing";

export const LISTING_CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_LISTING_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const LISTING_CHATKIT_API_URL =
  import.meta.env.VITE_LISTING_CHATKIT_API_URL ?? `${LISTING_API_BASE}/chatkit`;

export const LISTING_DRAFT_URL =
  import.meta.env.VITE_LISTING_DRAFT_URL ?? `${LISTING_API_BASE}/draft`;

export const LISTING_SUBMIT_URL =
  import.meta.env.VITE_LISTING_SUBMIT_URL ?? `${LISTING_API_BASE}/draft/submit`;

export const LISTING_RESET_URL =
  import.meta.env.VITE_LISTING_RESET_URL ?? `${LISTING_API_BASE}/draft/reset`;

export const LISTING_GREETING =
  import.meta.env.VITE_LISTING_GREETING ??
  "Let's capture every detail for your listing.";

export const LISTING_STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Start a fresh listing",
    prompt: "Let's capture seller name, email, phone, make, model, year, trim, body style, fuel type, transmission, drivetrain, colour, mileage, asking price, location, MOT expiry, service history, key features, and photo links.",
    icon: "sparkle",
  },
  {
    label: "Add photos + price",
    prompt: "I have photos, mileage, and a price ready to go.",
    icon: "atom",
  },
  {
    label: "Check missing details",
    prompt: "What information am I still missing for my listing?",
    icon: "globe",
  },
];

export const LISTING_COMPOSER_PLACEHOLDER =
  import.meta.env.VITE_LISTING_COMPOSER_PLACEHOLDER ??
  "Share details like make, mileage, price, or photos";
