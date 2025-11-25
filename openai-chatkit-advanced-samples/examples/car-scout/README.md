# Car Scout Demo

Guide shoppers through a curated inventory with ChatKit. This example mirrors an in-store salesperson: the chat panel on the left collects goals, while the React list on the right instantly narrows the catalog with every reply so buyers can browse real listings.

## What's Inside
- FastAPI service streaming from an OpenAI Agent trained on dealership tooling and the sample `cars.json` inventory.
- ChatKit Web Component embedded in a React layout that mirrors the customer-support demo but swaps in a list-based results pane.
- Client refresh loop that re-fetches the filtered inventory after each chat response so the UI always reflects the latest criteria.

## Prerequisites
- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip`
- OpenAI API key exported as `OPENAI_API_KEY`
- ChatKit domain key exported as `VITE_AUTO_CHATKIT_API_DOMAIN_KEY` (any placeholder works locally; register a real key before shipping)

## Quickstart Overview
1. Install dependencies and start the Car Scout backend.
2. Configure the domain key and launch the React frontend.
3. Chat with the agent and watch the results panel adapt.

### 1. Start the FastAPI backend

```bash
cd examples/car-scout/backend
uv sync
export OPENAI_API_KEY="sk-proj-..."
uv run uvicorn app.main:app --reload --port 8004
```

The API hosts ChatKit at `http://127.0.0.1:8004/autos/chatkit` plus a helper endpoint at `/autos/cars` for the inventory pane.

### 2. Run the React frontend

```bash
cd examples/car-scout/frontend
npm install
npm run dev
```

The Vite dev server runs at `http://127.0.0.1:5174` and proxies `/autos/*` calls to the backend.

From `examples/car-scout` you can also run `npm start` to launch both the backend (`uv sync` + Uvicorn) and frontend together. Make sure `OPENAI_API_KEY` and `VITE_AUTO_CHATKIT_API_DOMAIN_KEY` are exported before using the shortcut.

### 3. Configure the domain key for production

1. Host the frontend on your domain.
2. Register the domain on the [ChatKit domain allowlist](https://platform.openai.com/settings/organization/security/domain-allowlist) and mirror it in `examples/car-scout/frontend/vite.config.ts` under `server.allowedHosts`.
3. Set `VITE_AUTO_CHATKIT_API_DOMAIN_KEY` to the key returned by the allowlist and surface it in `examples/car-scout/frontend/src/lib/config.ts`.

For remote testing (ngrok, Cloudflare Tunnel, etc.) add the temporary hostname to the allowlist before sharing a link.

### 4. Try the workflow

Open the printed URL and try prompts such as:

- `I need an AWD wagon with rails for skis under £40k.`
- `Show me electric crossovers with at least 300 miles of range.`
- `We need an 8-seat family hauler that still fits in the garage.`

The agent calls `search_inventory`, the backend stores the narrowed results per thread, and the right-hand panel refreshes with matching vehicles and \"More info\" buttons to jump into real listings.
