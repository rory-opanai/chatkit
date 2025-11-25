# Car Listing Builder Demo

Standardise every vehicle listing with a conversational intake form. Sellers chat with the agent on the left,
while the right-hand preview auto-fills the template so the final listing always looks the same.

## What's Inside
- FastAPI service streaming from an OpenAI Agent that manages a strict listing schema and validation.
- ChatKit React panel embedded in a customer-support style layout that mirrors progress in live preview cards.
- Submission flow that confirms success, then offers a one-click “Submit another” reset for the next listing.

## Prerequisites
- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip`
- OpenAI API key exported as `OPENAI_API_KEY`
- ChatKit domain key exported as `VITE_LISTING_CHATKIT_API_DOMAIN_KEY`

## Quickstart Overview
1. Install dependencies and start the Car Listing backend.
2. Configure the domain key and launch the React frontend.
3. Chat with the agent and watch the preview fill itself in.

### 1. Start the FastAPI backend

```bash
cd examples/car-listing/backend
uv sync
export OPENAI_API_KEY="sk-proj-..."
uv run uvicorn app.main:app --reload --port 8005
```

The API hosts ChatKit at `http://127.0.0.1:8005/listing/chatkit` with helper endpoints under `/listing/*`
for fetching, submitting, and resetting drafts.

### 2. Run the React frontend

```bash
cd examples/car-listing/frontend
npm install
npm run dev
```

The Vite dev server runs at `http://127.0.0.1:5175` and proxies `/listing/*` calls to the backend.

From `examples/car-listing` you can also run `npm start` to launch both backend and frontend together.
Ensure `OPENAI_API_KEY` and `VITE_LISTING_CHATKIT_API_DOMAIN_KEY` are exported first.

### 3. Configure the domain key for production

1. Host the frontend on your production domain.
2. Register that domain on the [ChatKit domain allowlist](https://platform.openai.com/settings/organization/security/domain-allowlist)
   and mirror it in `examples/car-listing/frontend/vite.config.ts` under `server.allowedHosts`.
3. Set `VITE_LISTING_CHATKIT_API_DOMAIN_KEY` to the provided key and expose it via `examples/car-listing/frontend/src/lib/config.ts`.

For remote demos (ngrok, Cloudflare Tunnel, etc.), add the temporary hostname to the allowlist before sharing a link.

### 4. Try the workflow

Open the printed URL and try prompts such as:

- `I need to publish my 2018 hatchback—what details do you need?`
- `Here is the mileage, MOT date, and two photo links.`
- `Which fields am I still missing before we submit?`

The agent asks for anything missing, updates the structured record, and once every field is filled you can submit and immediately start another listing.
