# Settled skill and plugin

[Settled](https://settled.tools) checks x402 endpoints before agents pay them: live probes of every endpoint listed with the four public facilitator catalogs, real USDC test purchases compared with each listing, every seller's payments followed on Base, and a venue scorecard of who actually pays agents. Every answer is signed.

This repository packages that as an **agent skill** (`settled-x402`) and as a **Claude Code plugin** that also connects the Settled MCP server.

## Claude Code

```
/plugin marketplace add justinedwardvolmer/settled-skill
/plugin install settled@settled
```

That adds the MCP server `https://settled.tools/mcp` (18 tools, free tier of 300 calls a day) and the skill, which tells Claude to run `settled_check` before any x402 payment and `settled_preflight` when the money matters.

## Any other agent (Managed Agents, Agent SDK, OpenClaw, your own harness)

Copy `plugins/settled/skills/settled-x402/` into your skills directory, download the packaged skill from https://settled.tools/skills/settled-x402.skill, or, if you already use the npm package, run `npx settled-x402 skill install` (`--global` for `~/.claude/skills`, `--to <dir>` for any skills folder). The skill is three files: `SKILL.md` (the rule and the decision table), `references/api.md` (field reference) and `scripts/settled_check.py` (standard-library script that prints a one-line decision; exit code 0 pay, 1 caution, 2 do not pay).

MCP server: `https://settled.tools/mcp` (Streamable HTTP). HTTP: https://settled.tools/llms.txt. npm: [`settled-x402`](https://www.npmjs.com/package/settled-x402) guards every x402 payment in code.

## What the skill makes an agent do

1. Before paying an x402 endpoint it has not paid successfully before, call the free check and walk a short decision table: sanctioned payee, seller on hold, dead status, payTo mismatch with the quote in hand, price drift, verified delivery, quality.
2. When the free check is not enough (more than a few cents, never delivered, the user asks "is this safe"), run preflight and follow `pay / caution / avoid`.
3. After paying, report whether the call worked, if it holds the paying key.
4. Say what it decided and why, quoting the field that drove it.

Settled measures what it can observe. A clean check is evidence, not a guarantee, and the skill says so.

## License

MIT. Settled's data is best-effort observational data, not financial advice; scores are never for sale.
