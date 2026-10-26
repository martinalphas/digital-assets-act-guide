#!/usr/bin/env python3
"""Fetches every source URL and confirms a phrase the explainer relies on appears in it.
Writes src/linkcheck.json, which build.py uses for the 'How we checked' table."""
import datetime
import io
import json
import re
import subprocess
import urllib.request
from pathlib import Path

SRC = Path(__file__).resolve().parent
sources = json.loads((SRC / "sources.json").read_text())

# A phrase from each source that a cited statement depends on.
EXPECT = {
    "S1": ["day after the end of the period of 12 months", "$10 million", "$5,000", "761GD Meaning of tokenised custody platform", "transition period means the 6"],
    "S2": ["passed Parliament on 1 April 2026", "9 April 2027", "18-month"],
    "S3": ["commencing on 8 April 2027", "same activity, same risk, same regulatory outcome", "27 November 2026", "30 September 2026"],
    "S4": ["asset-holding standards", "transactional and settlement standards"],
    "S5": ["8 April 2027", "7 October 2027", "only select persons became able to conduct consensus activities"],
    "S6": ["unit-holder register", "cannot rely on an appointment as a corporate authorised", "Custody-only DAP"],
    "S7": ["such as gold"],
    "S8": ["30 September 2026"],
    "S9": ["tokenised securities", "30 June 2026"],
    "S10": ["9 April 2027"],
    "S11": ["operate under an Asset Issuer", "Redbelly Network"],
    "S12": ["three statutory tests", "400 validators"],
    "S13": ["ERC-3643", "Regulations can move the line"],
    "S14": ["Digital Assets", "existing licence"],
    "S15": ["KYC/AML", "enforced automatically"],
    "S16": ["not retail self-custody", "key management and recovery"],
    "S17": ["without restricting access at the network level"],
    "S18": ["real world asset tokenisation"],
    "S19": ["KYC verification"],
    "S20": ["Proof by Query", "Selective disclosure"],
    "S21": ["World Wide Web Consortium"],
    "S22": ["biometric"],
    "S23": ["all network participants must prove they are who they say they are"],
    "S24": ["100,000 RBNT", "previous experience, location and commitment", "Submissions currently closed"],
    "S25": ["cannot fork"],
    "S26": ["recovery system", "force transfers", "freeze"],
    "S27": ["Project Acacia", "NotCentralised"],
}

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read(), r.headers.get("Content-Type", "")


def to_text(body, ctype, url):
    if "pdf" in ctype or url.endswith(".pdf"):
        p = subprocess.run(["pdftotext", "-layout", "-", "-"], input=body, capture_output=True)
        t = p.stdout.decode("utf-8", "ignore")
    else:
        t = body.decode("utf-8", "ignore")
        t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S | re.I)
        t = re.sub(r"<[^>]+>", " ", t)
        import html as h
        t = h.unescape(t)
    t = t.replace("’", "'").replace("‘", "'").replace("‑", "-").replace("\xa0", " ")
    return re.sub(r"\s+", " ", t)


def main():
    results = []
    for s in sources:
        url = s["url"]
        # The Act's text page is rendered by script; its full text is served from the register's document URL.
        text_url = url
        if s["id"] == "S1":
            text_url = "https://www.legislation.gov.au/C2026A00038/asmade/2026-04-08/text/original/epub/OEBPS/document_1/document_1.html"
        try:
            status, body, ctype = fetch(url)
            if text_url != url:
                _, body, ctype = fetch(text_url)
            text = to_text(body, ctype, text_url)
            found = [p for p in EXPECT.get(s["id"], []) if p.lower() in text.lower()]
            missing = [p for p in EXPECT.get(s["id"], []) if p.lower() not in text.lower()]
            note = f"{len(found)}/{len(found) + len(missing)} cited phrases found"
            if missing:
                note += " (missing: " + "; ".join(missing) + ")"
            results.append({"id": s["id"], "url": url, "status": status, "note": note, "missing": missing})
        except Exception as e:  # noqa: BLE001
            results.append({"id": s["id"], "url": url, "status": getattr(e, "code", 0) or 0, "note": f"error: {e}", "missing": ["fetch"]})
        print(results[-1]["id"], results[-1]["status"], results[-1]["note"])
    out = {"checked_at": datetime.datetime.now(datetime.timezone.utc).strftime("%d %B %Y, %H:%M UTC"), "results": results}
    (SRC / "linkcheck.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
