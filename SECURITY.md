# Security

## Supported versions

The latest release of the Settled plugin and skill (this repository) is supported. Older versions get no fixes; update with `/plugin marketplace update settled`.

## What the plugin does

It adds one skill (`settled-x402`: instructions, a field reference and a standard-library Python script) and one remote MCP server, `https://settled.tools/mcp/free`. It runs no hooks, installs no packages, reads no environment variables and holds no keys. The script and the MCP server send only the x402 endpoint URL being checked to settled.tools. Details: [plugins/settled/README.md](plugins/settled/README.md); privacy policy: https://settled.tools/privacy.

## Reporting a vulnerability

Email alerts@settled.tools, or send a direct message to [@settledfyi](https://x.com/settledfyi) on X. Please don't open a public issue for a security problem. You can expect a reply within 3 days.
