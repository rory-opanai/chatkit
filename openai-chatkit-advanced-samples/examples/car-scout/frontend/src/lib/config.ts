import { StartScreenPrompt } from "@openai/chatkit";

export const THEME_STORAGE_KEY = "car-scout-theme";

const AUTO_API_BASE = import.meta.env.VITE_AUTO_API_BASE ?? "/autos";

/**
 * ChatKit still expects a domain key at runtime. Use any placeholder locally,
 * but register your production domain at
 * https://platform.openai.com/settings/organization/security/domain-allowlist
 * and deploy the real key.
 */
export const AUTO_CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_AUTO_CHATKIT_API_DOMAIN_KEY ?? "domain_pk_localhost_dev";

export const AUTO_CHATKIT_API_URL =
  import.meta.env.VITE_AUTO_CHATKIT_API_URL ?? `${AUTO_API_BASE}/chatkit`;

export const CAR_INVENTORY_URL =
  import.meta.env.VITE_AUTO_INVENTORY_URL ?? `${AUTO_API_BASE}/cars`;

export const CAR_GREETING =
  import.meta.env.VITE_AUTO_GREETING ??
  "Tell me how you drive and I'll shortlist a few cars.";

export const CAR_STARTER_PROMPTS: StartScreenPrompt[] = [
  {
    label: "Family SUV under £40k",
    prompt: "We need a quiet 3-row SUV under £40k with good safety tech.",
    icon: "sparkle",
  },
  {
    label: "Electric commuter",
    prompt: "Find a compact EV with at least 250 miles of range.",
    icon: "atom",
  },
  {
    label: "Weekend truck",
    prompt: "Looking for a crew-cab truck that can tow a camper.",
    icon: "suitcase",
  },
  {
    label: "All-wheel-drive wagon",
    prompt: "Any AWD wagons with roof rails for skis?",
    icon: "globe",
  },
];

export const CAR_COMPOSER_PLACEHOLDER =
  import.meta.env.VITE_AUTO_COMPOSER_PLACEHOLDER ??
  "Ask for body style, budget, or key features";
