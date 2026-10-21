# Installing the Settled plugin and skill

## Claude Code (plugin: skill + MCP server)

```
/plugin marketplace add justinedwardvolmer/settled-skill
/plugin install settled@settled
```

From a terminal, the same two steps are `claude plugin marketplace add justinedwardvolmer/settled-skill` and `claude plugin install settled@settled`. This adds the `settled-x402` skill and the free Settled MCP server (`https://settled.tools/mcp/free`: 13 tools, 300 calls a day, no key). Update later with `/plugin marketplace update settled`.

## Any other agent (skill only)

- Copy `plugins/settled/skills/settled-x402/` into your agent's skills folder, or
- download the packaged skill: https://settled.tools/skills/settled-x402.skill, or
- with Node 20+: `npx settled-x402 skill install` (`--global` for `~/.claude/skills`, `--to <dir>` for any other folder).

## MCP server only

Add `https://settled.tools/mcp/free` (Streamable HTTP) to any MCP client. Clients that can pay over x402 can use the full server at `https://settled.tools/mcp`.

## Check it works

Ask your agent to check an x402 endpoint before paying it, or run the skill's script directly:

```
python3 plugins/settled/skills/settled-x402/scripts/settled_check.py https://x402.ottoai.services/whois-lookup
```

It prints a one-line decision (exit code 0 pay, 1 caution, 2 do not pay).
