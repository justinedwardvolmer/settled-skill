# Settled API reference for agents

Base URL `https://settled.tools`. JSON everywhere. Every successful data response carries `attested_at` and an `attestation` block (`hash` = keccak256 of the canonical JSON without `attestation`; `signature` = EIP-191 by the published signer, `GET /v1/signer`). Verify any response with `POST /v1/verify`.

## Routes an agent uses

| Route | Price | What it answers |
| --- | --- | --- |
| `GET /v1/free/check?url=` | free, 300/day | Everything below for one endpoint, from the index (cached ≤ 5 min) |
| `GET /v1/check?url=&force=1` | $0.002 | Same, with a fresh probe |
| `GET /v1/preflight?url=` | $0.005 | Pre-spend check with `recommendation: pay / caution / avoid` and `reasons` |
| `GET /v1/free/endpoints?q=&network=&max_price=&status=&sort=&limit=` | free, 300/day | Ranked live endpoints (`sort`: quality, price, latency, payers) |
| `GET /v1/payto/{address}` | $0.005 | Seller reputation by wallet, with `settlement_integrity` |
| `POST /v1/submit {"url"}` | free | Add an endpoint to the index |
| `POST /v1/report {"url","tx","ok","signature"}` | free | Say whether a paid call worked (two-step, see SKILL.md) |
| `POST /v1/pass` | $0.05 | 24-hour pass: every paid route except Watchdog, Seller Watch and re-test; 120 req/min |
| `GET /v1/income/venues` | free | Venue scorecard with verdicts |
| `GET /v1/income?venue=&rail=&min_reward=` | $0.01 | Verified agent-income listings with honeypot flags |
| `GET /v1/income/check?url=` | $0.01 | Honeypot / trust scan of one listing |
| `GET /v1/events?limit=` | free | Change feed: verdict flips, new honeypots, integrity changes |
| `POST /v1/watch {"url","webhook"?}` | $1.00 / 10 days | Watchdog: probe every 15 min, signed alert on any change to status, price or payTo |
| `GET /v1/status` | free | Index size, freshness, ledger coverage |

MCP server: `https://settled.tools/mcp` (Streamable HTTP). Tools mirror the routes: `settled_check`, `settled_preflight`, `settled_find_endpoints`, `settled_seller_reputation`, `settled_submit`, `settled_report`, `settled_income_venues`, `settled_income_listings`, `settled_income_check`, `settled_events`, `settled_watch`, `settled_watch_alerts`, `settled_verify`, `settled_status`, and more. Pass a day pass as the `x-settled-pass` header on the connection or as the `pass` argument.

## Fields in a check

- `status` — `live` · `degraded` (one recent blip) · `dead` · `free` (no paywall) · `auth_gated` · `not_found` · `quote_invalid` · `unknown` (not probed yet). Dead/free/auth_gated/not_found/quote_invalid are set only after 3 consecutive consistent failures.
- `payability.verdict` — `delivered` (the scout paid, got usable content, nothing broke the listing) · `payable` (valid 402 on the verb that answers) · `unpriced` · `malformed_402` · `cannot_pay_either_verb` · `free` · `auth_gated` · `unreachable` · `unknown`. `payability.payable_verb` is the verb that actually pays when it differs from the listing.
- `price_usd`, `network` (CAIP-2, e.g. `eip155:8453` for Base), `asset`, `pay_to` — the quote Settled's probe sees. Compare `pay_to` and `price_usd` with the 402 you hold.
- `payee.seen_onchain` — whether the payTo has a USDC balance, a nonce or code on Base. `payee.seller` summarises the wallet's other endpoints and flags.
- `delivery_verified` — a real scout payment (within 30 days) came back with usable content and nothing in it broke the listing. `delivery_receipt` is that purchase: `paid_usd`, `tx` (on Base), `checks.verdict`:
  - `as_advertised` — promised fields present, at the listed price
  - `not_as_advertised` — fields missing, wrong type, placeholder sample served as the product, or overcharged; reasons in `why`
  - `disclosed_problem` — the response itself says it is degraded or stale (counts for little)
  - `partial_match`, `unverified` (too large or not checkable), `nothing_to_compare` (no sample in the listing), `not_delivered` (error, empty body, bad JSON; endpoint gets `delivery_failed`)
- `onchain` — `settlements_30d`, `unique_payers_30d`, `last_settlement_at` for the payTo, from Base.
- `reports` — paying agents' own reports (`worked`, `failed`); tallies count once 3+ wallets report.
- `quality.total` (0–100) = liveness 40 · schema 15 · latency 10 · on-chain payer activity 20 · verified delivery 15.
- `flags` — `price_changed`, `unpriceable`, `v1_only`, `slow`, `template_unresolved`, `clone_farm` (one wallet behind 200+ near-identical endpoints), `quote_only` (quotes but never settles), `verb_mismatch`, `payee_unseen`, `delivery_failed`, `seller_on_hold`, `sanctioned_payee`.
- `seller_claim` — the seller proved control of the payTo wallet and published a profile (name, website, contact, docs). A claim never changes a score.
- `erc8004` — present when the payTo owns or is the agent wallet of an ERC-8004 agent on Base: `agent_id`, `name`, whether its registration file loads.
- `payee_sanctions` — `{listed, lists_checked, as_of}` when the payTo matches the OFAC SDN list.
- `cached`, `checked_at` — whether the answer came from the 5-minute cache and when it was built.

## Preflight

Adds `recommendation` (`pay` / `caution` / `avoid`) and `reasons` (plain sentences), a fresh `liveness` block for both verbs, `payee` with seller reputation and `settlement_integrity` (`organic` / `concentrated` / `single_source` / `circular`), `honeypot` (scan of the listing text: `clean` or `suspected_honeypot` with `flags`), and `same_response_as` when another seller's endpoint returns identical content.

## Seller hold (why `avoid` happens)

When the scout's payments to one payTo are confirmed on Base at least twice within 30 days and nothing usable comes back either time, every endpoint paid to that wallet is flagged `seller_on_hold`: the scout stops buying, preflight answers `avoid`, and the endpoints leave the discovery feed. The hold lifts as soon as a scout purchase delivers again.

## Venue verdicts

`paying` (USDC left the venue's escrow to worker wallets in the last 7 days and ≥ $100 in 30) · `paying_small` (payouts in the last 30 days) · `paying_offchain` (awards in the venue's own public records, not verified on-chain) · `measuring` (under 7 days of coverage) · `no_payouts_seen` · `closed_to_agents` (terms bar bots, or payouts require a verified human) · `defunct` · `unmeasured`.

Listing labels from `/v1/income` and `/v1/income/check`: `verified_paying`, `unverified`, `gated`, `suspected_honeypot`, `dead`, `closed_to_agents`.
