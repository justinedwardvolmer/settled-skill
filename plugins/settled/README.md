# Settled

Check any x402 endpoint before your agent pays it, and find out which venues actually pay agents.

[Settled](https://settled.tools) is an independent x402 index. It probes every endpoint listed with the four public facilitator catalogs, buys from them with real USDC on Base and compares what comes back with the listing, follows every USDC payment to each seller on Base, and signs every answer so it can be verified later.

## What this plugin adds

- **The Settled MCP server** at `https://settled.tools/mcp/free`: the 13 tools that work without a pass or a payment. `settled_check` (status, payability, payTo, the scout's last real purchase, agent reports, risk flags for one endpoint), `settled_find_endpoints` (live endpoints by keyword, network and price), `settled_peek`, `settled_submit`, `settled_report`, `settled_claim`, `settled_sellers`, `settled_income_venues` (which bounty boards and task markets pay agents), `settled_events`, `settled_weekly_report`, `settled_watch_alerts`, `settled_verify` and `settled_status`. Free: 300 calls a day per client, 30 a minute, no account and no key.
- **The `settled-x402` skill**, which tells Claude what to do with a 402: run the free check before paying an endpoint it has not paid successfully before, walk a short decision table (sanctioned payee, seller on hold, dead status, payTo mismatch with the quote in hand, price drift, verified delivery, quality), report afterwards, and say which field drove the decision.

## What it sends, runs and fetches

- Tool calls send Settled only their arguments: an endpoint URL, a wallet address, keywords, a transaction hash, or a signature the paying wallet made. Settled never sees the rest of the conversation. Requests reach `https://settled.tools` over HTTPS, and the server sees the connecting IP address, as any web server does. An endpoint URL Settled has not seen before is added to its public index and probed.
- Nothing runs on your machine. The skill's `scripts/settled_check.py` is a standard-library Python script that calls the same free check over HTTPS and prints a one-line decision; Claude runs it only if you ask it to work from a shell.
- The plugin never holds keys and never moves money. The full server at `https://settled.tools/mcp` adds tools that need a Settled day pass or an x402 payment (preflight, seller reputation, income listings, the Watchdog); they are left out here because this client cannot pay.
- Privacy policy: https://settled.tools/privacy. Documentation: https://settled.tools/for-agents and https://settled.tools/llms.txt.

## Honesty

Settled measures what it can observe: probes, its own purchases, public on-chain transfers, venues' own records. A clean check is evidence, not a guarantee, and the skill says so. Best-effort observational data, not financial advice. Scores are never for sale.

## License

MIT.
