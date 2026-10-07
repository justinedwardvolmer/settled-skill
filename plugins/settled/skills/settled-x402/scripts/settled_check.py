#!/usr/bin/env python3
"""Check an x402 endpoint with Settled's free route and print a one-line decision.

Usage: settled_check.py <endpoint-url> [--quote-payto 0x...] [--quote-price 0.001] [--json]

Exit codes: 0 pay · 1 caution · 2 do not pay · 3 could not check.
Standard library only; no key needed (300 free checks a day per client).
"""
import json
import sys
import urllib.parse
import urllib.request

BASE = "https://settled.tools"


def fetch(url):
    req = urllib.request.Request(url, headers={"accept": "application/json", "user-agent": "settled-x402-skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"error": f"http_{e.code}"}
    except Exception as e:  # network, timeout, bad JSON
        return 0, {"error": str(e)[:120]}


def decide(d, quote_payto=None, quote_price=None):
    """Return (verdict, reason). verdict: pay | caution | avoid | unknown."""
    if d.get("error") == "first_party":
        return "pay", "this is one of Settled's own routes"
    if d.get("error") in ("not_indexed", "bad_url") or d.get("status") == "unknown":
        return "unknown", "not indexed yet; POST /v1/submit and check again in a few minutes"
    flags = d.get("flags") or []
    status = d.get("status")
    if "sanctioned_payee" in flags:
        return "avoid", "payTo is on the OFAC sanctions list"
    if "seller_on_hold" in flags:
        return "avoid", "seller on hold: Settled's scout paid this seller and got nothing usable back (twice in 30 days)"
    if "delivery_failed" in flags:
        return "avoid", "the scout's last real payment came back without usable content"
    if status in ("dead", "not_found", "quote_invalid", "auth_gated"):
        return "avoid", f"status is {status}; a plain x402 purchase will not work"
    if status == "free":
        return "pay", "no paywall: call it without paying"
    pay_to = (d.get("pay_to") or "").lower()
    if quote_payto and pay_to and quote_payto.lower() != pay_to:
        return "avoid", f"the 402 you hold names payTo {quote_payto} but Settled's probe sees {d.get('pay_to')}; possible clone or hijack"
    price = d.get("price_usd")
    if quote_price is not None and price and quote_price > price * 1.1:
        return "caution", f"the 402 you hold charges ${quote_price} but Settled last saw ${price}"
    receipt = d.get("delivery_receipt") or {}
    verdict = ((receipt.get("checks") or {}).get("verdict")) if isinstance(receipt, dict) else None
    if d.get("delivery_verified") and verdict in (None, "as_advertised", "disclosed_problem", "nothing_to_compare"):
        return "pay", f"a real scout purchase delivered ({verdict or 'delivered'}); quality {d.get('quality', {}).get('total')}"
    pv = (d.get("payability") or {}).get("verdict")
    q = (d.get("quality") or {}).get("total") or 0
    bad = [f for f in flags if f in ("clone_farm", "quote_only", "payee_unseen", "verb_mismatch", "template_unresolved")]
    if pv == "payable" and q >= 60 and not bad:
        return "pay", f"payable, quality {q}, no delivery yet: fine for cents, preflight for more"
    return "caution", f"payability {pv}, quality {q}" + (f", flags {','.join(bad)}" if bad else "") + "; prefer a delivered alternative or run preflight"


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 3
    url = argv[1]
    quote_payto = quote_price = None
    as_json = "--json" in argv
    if "--quote-payto" in argv:
        quote_payto = argv[argv.index("--quote-payto") + 1]
    if "--quote-price" in argv:
        quote_price = float(argv[argv.index("--quote-price") + 1])
    code, d = fetch(f"{BASE}/v1/free/check?url={urllib.parse.quote(url, safe='')}")
    if code == 429:
        print("settled: rate limited or free quota exhausted; retry later or use a day pass", file=sys.stderr)
        return 3
    if code == 0:
        print(f"settled: could not reach settled.tools ({d.get('error')})", file=sys.stderr)
        return 3
    verdict, reason = decide(d, quote_payto, quote_price)
    if as_json:
        print(json.dumps({"verdict": verdict, "reason": reason, "check": d}, indent=1))
    else:
        print(f"settled {verdict.upper()}: {reason}")
        print(f"  {url}")
        print(f"  status={d.get('status')} payability={(d.get('payability') or {}).get('verdict')} price_usd={d.get('price_usd')} pay_to={d.get('pay_to')} quality={(d.get('quality') or {}).get('total')} flags={d.get('flags')}")
    return {"pay": 0, "caution": 1, "avoid": 2, "unknown": 3}[verdict]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
