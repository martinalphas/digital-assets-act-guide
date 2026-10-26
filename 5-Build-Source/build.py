#!/usr/bin/env python3
"""Builds the website, the print/PDF source, and the Markdown/CSV deliverables
from src/content.html, src/sources.json and the community summary below."""
import csv
import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SITE = ROOT / "site"
OUT = ROOT / "deliverables"
# PUBLIC_URL: where readers can find the explainer and files (used in the thread, PDF and Word file).
# DEPLOY_URL: the live website address, if any (used only for social preview tags). Leave empty until deployed.
SITE_URL = os.environ.get("PUBLIC_URL", "https://github.com/martinalphas/digital-assets-act-guide").rstrip("/")
DEPLOY_URL = os.environ.get("DEPLOY_URL", "").rstrip("/")
AS_AT = "26 October 2026"
TITLE = "Australia's Digital Assets Framework Act: What It Means for Tokeniser"
SHORT = "DAF Act explainer"
DESC = ("Plain-language explainer of Australia's Corporations Amendment (Digital Assets Framework) Act 2026: "
        "who needs a licence, key dates, what changes for issuers using Tokeniser, and where Redbelly's "
        "compliance design fits. General information, not legal advice.")

PDF_NAME = "DAF-Act-Tokeniser-Explainer.pdf"
DOCX_NAME = "DAF-Act-Tokeniser-Explainer.docx"
ZIP_NAME = "DAF-Act-Explainer-Package.zip"

sources = json.loads((SRC / "sources.json").read_text())
SRC_BY_ID = {s["id"]: s for s in sources}
content = (SRC / "content.html").read_text()
linkcheck_path = SRC / "linkcheck.json"
linkcheck = json.loads(linkcheck_path.read_text()) if linkcheck_path.exists() else None

THREAD = [
    "Australia's Digital Assets Framework Act is now law. From 8 April 2027, digital asset platforms and tokenised custody platforms become regulated financial products, licensed by ASIC.\n\nWhat it means for issuers and Tokeniser, in plain English 🧵\n(General info, not legal advice.)",
    "Two new products:\n\n• Digital asset platform (DAP): an operator holds tokens for clients\n• Tokenised custody platform (TCP): an operator holds a real asset and issues one redeemable token per asset\n\nOperators will generally need an AFS licence.",
    "Key dates:\n\n• 8 Apr 2026: Royal Assent\n• 8 Apr 2027: Act starts, applications open\n• 7 Oct 2027: last day for existing operators to apply (they can keep operating while ASIC decides)\n\nSome earlier ASIC pages said 9 April. ASIC's latest says 8 April.",
    "Not everyone needs a licence. Exemptions include:\n\n• low-value platforms (up to $10m in transactions a year and $5,000 per client, plus other conditions)\n• people who only mention or arrange a platform as a minor part of their business\n• qualifying public token infrastructure",
    "For issuers on Tokeniser: the Act regulates platforms, not the act of tokenising.\n\nTokenised fund units and shares stay under existing law. ASIC's draft guide says a natively tokenised fund is generally a managed investment scheme, not a TCP.",
    "Where it can bite: if anyone holds investors' tokens or keys, or an issuer mints custody-backed tokens, the new platform rules may apply.\n\nOpen question: do freeze, recovery or forced-transfer admin powers count as \"possessing\" tokens? Worth asking a lawyer.",
    "Redbelly's tools (verifiable credentials, programmable eligibility, KYC'd onboarding, final settlement) could help licensees meet parts of the rules.\n\nBut the legal duties sit with licensees, and no source says Redbelly or Tokeniser is compliant.",
    "Biggest open question: is Redbelly \"public digital token infrastructure\" under s 9E?\n\nASIC's draft view: if only select people can validate (e.g. because of KYC limits), it may not qualify. Redbelly's docs gate network access and node operators. Unresolved for now.",
    "Next: ASIC's CP 392 consultation closes 27 Nov 2026. Final rules are planned for March 2027.\n\nFull explainer, timeline and every source: {url}\n\nGeneral information only. Not legal, financial or investment advice.",
]
THREAD = [t.replace("{url}", SITE_URL) for t in THREAD]

PARAGRAPHS = [
    "Australia's Corporations Amendment (Digital Assets Framework) Act 2026 received Royal Assent on 8 April 2026 and starts on 8 April 2027. It makes two kinds of platform into regulated financial products. In a digital asset platform, an operator holds tokens for clients. In a tokenised custody platform, an operator holds a real asset and issues one redeemable token for each asset. Operators will generally need an Australian financial services licence from ASIC. Platforms already operating must apply by 7 October 2027 and can keep operating while ASIC decides. Some low-value platforms, people who only introduce a platform as a minor part of their business, and qualifying public blockchain infrastructure are exempt.",
    "For issuers who tokenise through Tokeniser, the Act regulates platforms rather than the act of tokenising. Tokenised fund units and shares stay under the existing rules. ASIC's draft guidance says a natively tokenised fund is generally a managed investment scheme rather than a tokenised custody platform. The new rules matter where someone holds tokens or keys for investors, or where an issuer creates tokens backed by assets held in custody.",
    "Redbelly's identity and eligibility tools could help licensees meet parts of the new rules. But the legal duties sit with licensees, and no source we reviewed says Redbelly or Tokeniser is compliant. The biggest open question is whether Redbelly counts as \"public digital token infrastructure\", given ASIC's draft view on identity checks for validators. ASIC is consulting until 27 November 2026. This is general information, not legal advice.",
]

TOC = [
    ("notice", "", "Not legal advice"),
    ("how-to-read", "", "How to read this"),
    ("glance", "01", "The short version"),
    ("why", "02", "Why the Act exists"),
    ("terms", "03", "Key ideas"),
    ("licence", "04", "Who needs a licence"),
    ("timeline", "05", "Timeline"),
    ("issuers", "06", "Issuers and Tokeniser"),
    ("redbelly", "07", "Redbelly's compliance fit"),
    ("next", "08", "What to watch"),
    ("community", "09", "Community summary"),
    ("sources", "10", "Sources"),
    ("verification", "11", "How we checked"),
    ("downloads", "12", "Downloads"),
]


def x_len(text: str) -> int:
    """Approximate X character count: URLs count as 23, emoji as 2."""
    t = re.sub(r"https?://\S+", "x" * 23, text)
    n = 0
    for ch in t:
        n += 2 if ord(ch) > 0xFFFF else 1
    return n


def linkify(escaped: str) -> str:
    return re.sub(r"(https?://[^\s<]+)", r'<a href="\1" rel="noopener" target="_blank">\1</a>', escaped)


def cite(m):
    sid, pin = m.group(1), m.group(2)
    s = SRC_BY_ID[sid]
    title = html.escape(f"{s['title']} ({s['publisher']}) {pin}", quote=True)
    return f'<a class="cite" href="#{sid}" title="{title}">{sid}&nbsp;·&nbsp;{html.escape(pin)}</a>'


def render_cites(text: str) -> str:
    out = re.sub(r"\[\[(S\d+)\|([^\]]+)\]\]", cite, text)
    missing = re.findall(r"\[\[", out)
    assert not missing, "unrendered citation"
    return out


def add_data_labels(text: str) -> str:
    def per_table(tm):
        t = tm.group(0)
        heads = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th[^>]*scope=\"col\"[^>]*>(.*?)</th>", t, re.S)]
        def per_row(rm):
            row = rm.group(0)
            idx = [0]
            def per_cell(cm):
                i = idx[0]
                idx[0] += 1
                label = html.escape(heads[i]) if i < len(heads) else ""
                return f'{cm.group(1)} data-label="{label}"{cm.group(2)}'
            return re.sub(r"(<t[hd])((?:\s[^>]*)?>)", per_cell, row)
        body = re.sub(r"<tbody>.*?</tbody>", lambda b: re.sub(r"<tr>.*?</tr>", per_row, b.group(0), flags=re.S), t, flags=re.S)
        return body
    return re.sub(r"<table[^>]*>.*?</table>", per_table, text, flags=re.S)


def community_html(interactive=True) -> str:
    posts = []
    for i, t in enumerate(THREAD, 1):
        n = x_len(t)
        assert n <= 280, f"post {i} too long: {n}"
        btn = f'<button class="copy" type="button" data-copy="post-{i}">Copy</button>' if interactive else ""
        posts.append(
            f'<article class="post"><div class="meta"><span class="n">{i}/{len(THREAD)}</span>'
            f'<span>{n}/280 characters</span>{btn}</div><p id="post-{i}">{linkify(html.escape(t))}</p></article>'
        )
    paras = "".join(f"<p>{html.escape(p)}</p>" for p in PARAGRAPHS)
    copy_all = '<button class="copy" type="button" data-copy-thread>Copy whole thread</button>' if interactive else ""
    copy_paras = '<button class="copy" type="button" data-copy="summary-paras">Copy paragraphs</button>' if interactive else ""
    return f"""
<section id="community" aria-labelledby="community-h">
  <p class="eyebrow">09</p>
  <h2 id="community-h">Community summary</h2>
  <p>A short version for the DAO to share. It has no price talk, makes no claims of compliance, and keeps the "not legal advice" line. Every point is drawn from the cited sections above.</p>
  <div class="row-between"><h3>X thread ({len(THREAD)} posts)</h3>{copy_all}</div>
  <div class="thread">{''.join(posts)}</div>
  <div class="row-between"><h3>Short paragraphs</h3>{copy_paras}</div>
  <div class="summary-box" id="summary-paras">{paras}</div>
</section>"""


def sources_html() -> str:
    items = []
    for s in sources:
        items.append(
            f'<li id="{s["id"]}"><span class="sid">{s["id"]}</span><span class="stitle">{html.escape(s["title"])}</span>'
            f'<span class="stype">{html.escape(s["type"])}</span>'
            f'<div class="smeta">{html.escape(s["publisher"])} · {html.escape(s["date"])}</div>'
            f'<div class="surl"><a href="{html.escape(s["url"])}" rel="noopener" target="_blank">{html.escape(s["url"])}</a></div>'
            f'<div class="sused"><strong>Supports:</strong> {html.escape(s["used_for"])}</div></li>'
        )
    return f"""
<section id="sources" aria-labelledby="sources-h">
  <p class="eyebrow">10</p>
  <h2 id="sources-h">Sources</h2>
  <p>Primary sources come first: the Act itself (S1) and ASIC material (S2–S10). Redbelly and Tokeniser pages (S11–S27) are used only to report what those organisations say about themselves, and are labelled that way in the text. No factual claim relies on news coverage or law-firm commentary. Every in-text citation gives a pinpoint (a section, paragraph, table or page section).</p>
  <ol class="sources">{''.join(items)}</ol>
</section>"""


def verification_html() -> str:
    rows = ""
    summary = "<p>Link check results were not available when this file was built.</p>"
    if linkcheck:
        ok = sum(1 for r in linkcheck["results"] if r["status"] == 200)
        total = len(linkcheck["results"])
        summary = (f'<p><strong>{ok} of {total}</strong> source links returned HTTP 200 when checked on '
                   f'{html.escape(linkcheck["checked_at"])}.</p>')
        for r in linkcheck["results"]:
            cls = "status-ok" if r["status"] == 200 else ""
            rows += (f'<tr><th scope="row">{r["id"]}</th><td class="{cls}">{r["status"]}</td>'
                     f'<td>{html.escape(r.get("note", ""))}</td></tr>')
        rows = (f'<div class="table-wrap"><table class="check-table"><thead><tr><th scope="col">Source</th>'
                f'<th scope="col">HTTP status</th><th scope="col">Content check</th></tr></thead><tbody>{rows}</tbody></table></div>')
    return f"""
<section id="verification" aria-labelledby="verification-h">
  <p class="eyebrow">11</p>
  <h2 id="verification-h">How we checked</h2>
  <ul>
    <li>We read the full text of the Act as made, from the Federal Register of Legislation, and took every definition, threshold and date from it. [[S1|whole Act]]</li>
    <li>We read ASIC's roadmap, media releases, CP 392 and the draft regulatory guide. Where ASIC is only proposing something, the text says <em>draft</em>. [[S2|Roadmap]] [[S5|CP 392]] [[S6|draft RG 000]]</li>
    <li>We checked the commencement date against both the Act and ASIC's latest material, and explain the 8/9 April difference <a href="#date-note">in the timeline</a>.</li>
    <li>Statements by Redbelly and Tokeniser are labelled as company statements and are not treated as facts about the law.</li>
    <li>Each source was fetched and its cited content confirmed against the text it supports. The results are below.</li>
  </ul>
  {summary}
  {rows}
</section>"""


def downloads_html() -> str:
    return f"""
<section id="downloads" aria-labelledby="downloads-h">
  <p class="eyebrow">12</p>
  <h2 id="downloads-h">Downloads</h2>
  <div class="downloads">
    <a class="dl" href="downloads/{PDF_NAME}" download><span class="ext red">PDF</span><span><span class="t">Explainer (PDF)</span><span class="d">Full explainer with sources, print-ready A4</span></span></a>
    <a class="dl" href="downloads/{DOCX_NAME}" download><span class="ext">DOCX</span><span><span class="t">Explainer (Word)</span><span class="d">Editable version for review</span></span></a>
    <a class="dl" href="downloads/Community-Summary.md" download><span class="ext">MD</span><span><span class="t">Community summary</span><span class="d">X thread and short paragraphs</span></span></a>
    <a class="dl" href="downloads/Sources.md" download><span class="ext">MD</span><span><span class="t">Source list</span><span class="d">Every source, with what it supports</span></span></a>
    <a class="dl" href="downloads/Sources.csv" download><span class="ext">CSV</span><span><span class="t">Source list (CSV)</span><span class="d">For spreadsheets and review</span></span></a>
    <a class="dl" href="downloads/{ZIP_NAME}" download><span class="ext red">ZIP</span><span><span class="t">Full package</span><span class="d">All deliverables and the website source</span></span></a>
  </div>
</section>"""


ICON_SUN = '<svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
ICON_MOON = '<svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'
ICON_ALERT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/></svg>'

FACTS = """
<div class="facts">
  <div class="fact"><div class="label">Royal Assent</div><div class="value">8 Apr 2026</div><div class="note">Act No. 38, 2026</div></div>
  <div class="fact"><div class="label">Commences</div><div class="value"><span class="red">8 Apr 2027</span></div><div class="note">Act s 2 and ASIC CP 392</div></div>
  <div class="fact"><div class="label">Apply by</div><div class="value">7 Oct 2027</div><div class="note">Existing operators</div></div>
  <div class="fact"><div class="label">Regulator</div><div class="value">ASIC</div><div class="note">AFS licensing</div></div>
</div>"""

SCRIPT = r"""
<script>
(function () {
  var root = document.documentElement;
  var KEY = 'daf-theme';
  try { var saved = localStorage.getItem(KEY); if (saved) root.setAttribute('data-theme', saved); } catch (e) {}
  var tbtn = document.querySelector('.theme-toggle');
  if (tbtn) tbtn.addEventListener('click', function () {
    var cur = root.getAttribute('data-theme');
    if (!cur) cur = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    var next = cur === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem(KEY, next); } catch (e) {}
  });

  function copyText(text, btn) {
    function done() { var t = btn.textContent; btn.textContent = 'Copied'; btn.classList.add('done'); setTimeout(function () { btn.textContent = t; btn.classList.remove('done'); }, 1600); }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(); });
    } else { fallback(); }
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', '');
      ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) {}
      document.body.removeChild(ta);
    }
  }
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = document.getElementById(b.getAttribute('data-copy'));
      if (el) copyText(el.innerText.trim(), b);
    });
  });
  var all = document.querySelector('[data-copy-thread]');
  if (all) all.addEventListener('click', function () {
    var parts = Array.prototype.map.call(document.querySelectorAll('.thread .post p'), function (p) { return p.innerText.trim(); });
    copyText(parts.join('\n\n---\n\n'), all);
  });

  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  var map = {};
  links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && map[e.target.id]) {
          links.forEach(function (l) { l.classList.remove('active'); });
          map[e.target.id].classList.add('active');
        }
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
  }
  var top = document.querySelector('.to-top');
  if (top) window.addEventListener('scroll', function () { top.classList.toggle('show', window.scrollY > 900); }, { passive: true });
})();
</script>"""


def site_page(body_main: str) -> str:
    OG_DEPLOY = (f'<meta property="og:url" content="{DEPLOY_URL}/">\n'
                 f'<meta property="og:image" content="{DEPLOY_URL}/assets/og.png">\n'
                 '<meta name="twitter:card" content="summary_large_image">') if DEPLOY_URL else '<meta name="twitter:card" content="summary">'
    toc_items = "".join(
        f'<li><a href="#{i}"><span class="num">{n}</span>{html.escape(l)}</a></li>' for i, n, l in TOC
    )
    mobile_items = "".join(f'<li><a href="#{i}">{html.escape(l)}</a></li>' for i, n, l in TOC)
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DAF Act and Tokeniser</title>
<meta name="description" content="{html.escape(DESC)}">
<meta name="theme-color" content="#142530">
<meta property="og:title" content="{html.escape(TITLE)}">
<meta property="og:description" content="{html.escape(DESC)}">
<meta property="og:type" content="article">
{OG_DEPLOY}
<link rel="icon" href="assets/redbelly-isotype-red.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/readex-pro-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/styles.css">
<script>try{{var t=localStorage.getItem('daf-theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="inner">
    <a class="brand" href="#top" aria-label="Back to top">
      <img class="logo-light" src="assets/redbelly-logo-color.svg" alt="Redbelly" width="108" height="30">
      <img class="logo-dark" src="assets/redbelly-logo-negative.svg" alt="Redbelly" width="108" height="30">
      <span class="divider" aria-hidden="true"></span>
      <span class="site-name">{SHORT}</span>
    </a>
    <div class="actions">
      <button class="btn icon-btn theme-toggle" type="button" aria-label="Switch light or dark theme">{ICON_SUN}{ICON_MOON}</button>
      <a class="btn primary" href="downloads/{PDF_NAME}" download>Download PDF</a>
    </div>
  </div>
</header>
<div class="hero" id="top">
  <div class="inner">
    <div class="kicker"><span class="chip red">Community explainer</span><span class="chip">Prepared for the Redbelly DAO</span><span class="chip">As at {AS_AT}</span></div>
    <h1>Australia's Digital Assets Framework Act: what it means for <span class="hl">Tokeniser</span></h1>
    <p class="lead">A plain-language guide to Australia's new licensing rules for digital asset platforms and tokenised custody platforms: who they cover, when they start, what changes for issuers who tokenise through Tokeniser, and where Redbelly's built-in compliance tools fit.</p>
    {FACTS}
    <div class="ctas">
      <a class="btn primary" href="#glance">Read the explainer</a>
      <a class="btn ghost-light" href="downloads/{PDF_NAME}" download>PDF</a>
      <a class="btn ghost-light" href="downloads/{DOCX_NAME}" download>Word</a>
      <a class="btn ghost-light" href="#community">Community summary</a>
      <a class="btn ghost-light" href="#sources">Sources</a>
    </div>
    <p class="disclaimer-strip">{ICON_ALERT}<span>General information only, not legal advice. This is not an official publication of Redbelly Network, Tokeniser, ASIC or the Australian Government. It does not claim that anyone is licensed or compliant.</span></p>
  </div>
</div>
<div class="layout">
  <nav class="toc" aria-label="Contents"><div class="toc-title">Contents</div><ol>{toc_items}</ol></nav>
  <main id="main">
    <details class="mobile-toc"><summary>Contents</summary><ol>{mobile_items}</ol></details>
    {body_main}
  </main>
</div>
<footer class="site">
  <div class="inner">
    <div>
      <img src="assets/redbelly-logo-negative.svg" alt="Redbelly" width="101" height="28">
      <p>An independent community explainer prepared for review by the Redbelly DAO. It is not an official publication of Redbelly Network, Tokeniser, ASIC or the Australian Government, and it does not claim that any person is licensed or compliant.</p>
      <p>General information only, as at {AS_AT}. Not legal, financial, tax or investment advice. Seek advice from a qualified Australian lawyer.</p>
    </div>
    <div>
      <h4>Primary sources</h4>
      <p><a href="{SRC_BY_ID['S1']['url']}" rel="noopener" target="_blank">The Act (C2026A00038)</a><br>
      <a href="{SRC_BY_ID['S2']['url']}" rel="noopener" target="_blank">ASIC implementation roadmap</a><br>
      <a href="{SRC_BY_ID['S4']['url']}" rel="noopener" target="_blank">ASIC CP 392</a></p>
      <p class="small" style="color:#AEB7BE">Visual identity follows the published <a href="https://redbelly.network/brand" rel="noopener" target="_blank">Redbelly brand guidelines</a>. Typeface: Readex Pro (SIL Open Font License).</p>
    </div>
  </div>
</footer>
<a class="btn primary to-top" href="#top" aria-label="Back to top">↑ Top</a>
{SCRIPT}
</body>
</html>
"""


PRINT_CSS = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
@page :first { margin: 0; }
html, body { background: #fff; }
body { font-size: 10.6pt; line-height: 1.55; }
.cover { height: 297mm; width: 210mm; background: #142530; color: #E7EBEE; position: relative; overflow: hidden;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; page-break-after: always; break-after: page; }
.cover::after { content: ""; position: absolute; inset: 0; background-image: url("assets/hex.svg"); background-size: 110px auto; opacity: .55; }
.cover .in { position: relative; z-index: 1; padding: 26mm 22mm; height: 100%; display: flex; flex-direction: column; }
.cover img { height: 15mm; width: auto; align-self: flex-start; }
.cover .k { margin-top: 48mm; font-size: 10pt; letter-spacing: .14em; text-transform: uppercase; color: #FF5050; font-weight: 600; }
.cover h1 { color: #fff; font-size: 33pt; line-height: 1.06; font-weight: 500; margin: 6mm 0 8mm; letter-spacing: -0.02em; }
.cover h1 span { color: #FF5050; }
.cover .lead { font-size: 12.5pt; font-weight: 300; color: #D6DCE0; max-width: 150mm; }
.cover .meta { margin-top: auto; border-top: 1px solid rgba(255,255,255,.25); padding-top: 6mm; font-size: 9.5pt; color: #C9D0D5; display: grid; grid-template-columns: 1fr 1fr; gap: 4mm 10mm; }
.cover .meta b { color: #fff; font-weight: 500; display: block; }
.cover .warn { margin-top: 8mm; font-size: 9.5pt; color: #fff; border-left: 3px solid #FF5050; padding-left: 4mm; }
.doc { padding: 0; }
.doc h2 { font-size: 18pt; margin-top: 0; }
.doc h3 { font-size: 12.5pt; margin-top: 6mm; }
.doc > section { margin-bottom: 9mm; }
.doc > section#glance, .doc > section#licence, .doc > section#issuers, .doc > section#redbelly,
.doc > section#community, .doc > section#sources { break-before: page; }
.doc h2, .doc h3 { break-after: avoid; }
.claim, .post, .steps li, .timeline li, tr, .callout, .fact, .sources li { break-inside: avoid; }
.claim { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
thead th, .tag, .pill, a.cite, .notice, .steps li::before, .timeline li::before { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
a.cite { font-size: 7.4pt; }
.table-wrap { overflow: visible; }
table { font-size: 9pt; }
.timeline::before { left: 7.4rem; }
.post { box-shadow: none; }
.notice, .steps, .callout { box-shadow: none; }
"""


def print_page(body_main: str) -> str:
    return f"""<!doctype html>
<html lang="en-AU" data-theme="light">
<head>
<meta charset="utf-8">
<title>{html.escape(TITLE)}</title>
<link rel="stylesheet" href="assets/styles.css">
<style>{PRINT_CSS}</style>
</head>
<body>
<div class="cover"><div class="in">
  <img src="assets/redbelly-logo-negative.svg" alt="Redbelly">
  <div class="k">Community explainer · Prepared for the Redbelly DAO</div>
  <h1>Australia's Digital Assets Framework Act: what it means for <span>Tokeniser</span></h1>
  <p class="lead">A plain-language guide to the new licensing rules for digital asset platforms and tokenised custody platforms, what changes for issuers, and where Redbelly's built-in compliance fits.</p>
  <div class="meta">
    <div><b>Royal Assent</b>8 April 2026</div>
    <div><b>Commences</b>8 April 2027 (Act s 2; ASIC CP 392)</div>
    <div><b>Existing operators apply by</b>7 October 2027</div>
    <div><b>Information current as at</b>{AS_AT}</div>
  </div>
  <p class="warn">General information only. This is not legal, financial, tax or investment advice. It is not an official publication of Redbelly Network, Tokeniser, ASIC or the Australian Government, and it does not claim that anyone is licensed or compliant.</p>
</div></div>
<main class="doc">
{body_main}
<p class="small">Explainer files and sources online: <a href="{SITE_URL}">{SITE_URL}</a></p>
</main>
</body>
</html>
"""


def build():
    main_core = add_data_labels(render_cites(content))
    verification = add_data_labels(render_cites(verification_html()))
    site_main = main_core + community_html(True) + sources_html() + verification + downloads_html()
    (SITE / "index.html").write_text(site_page(site_main))

    print_main = main_core + community_html(False) + sources_html() + verification
    (SITE / "_print.html").write_text(print_page(print_main))

    # Word version: labels become bracketed bold text so they survive conversion.
    docx_main = re.sub(r'<span class="tag [a-z]+">(.*?)</span>', r'<strong>[\1]</strong>', print_main)
    docx_main = re.sub(r'<span class="pill [a-z]+">(.*?)</span>', r'<strong>[\1]</strong>', docx_main)
    docx_main = re.sub(r'<a class="cite" href="(#S\d+)"[^>]*>(.*?)</a>', r'<a href="\1">[\2]</a>', docx_main)
    docx_main = re.sub(r'<p class="eyebrow">\d+</p>', '', docx_main)
    notice = ("<p><strong>General information only. Not legal, financial, tax or investment advice.</strong> "
              f"Information current as at {AS_AT}. Not an official publication of Redbelly Network, Tokeniser, ASIC "
              f"or the Australian Government. Explainer files and sources online: <a href=\"{SITE_URL}\">{SITE_URL}</a></p>")
    (SITE / "_docx.html").write_text(
        f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>{html.escape(TITLE)}</title></head>'
        f'<body><p><em>A plain-language explainer for issuers, holders and the Redbelly community</em></p>'
        f'{notice}{docx_main}</body></html>')

    OUT.mkdir(exist_ok=True)
    # Community summary (Markdown)
    md = [f"# Community summary: {TITLE}", "",
          f"_General information only, not legal advice. As at {AS_AT}. Full explainer and sources: {SITE_URL}_", "",
          f"## X thread ({len(THREAD)} posts)", ""]
    for i, t in enumerate(THREAD, 1):
        md += [f"**{i}/{len(THREAD)}** ({x_len(t)}/280 characters)", "", t, "", "---", ""]
    md += ["## Short paragraphs", ""] + [p + "\n" for p in PARAGRAPHS]
    md += ["## Sources behind this summary", "",
           "Each point is drawn from the full explainer, where every statement carries a pinpoint citation. Key sources: "
           f"the Act ({SRC_BY_ID['S1']['url']}), ASIC CP 392 ({SRC_BY_ID['S5']['url']}), draft RG 000 ({SRC_BY_ID['S6']['url']}), "
           f"ASIC 26-245MR ({SRC_BY_ID['S3']['url']}).", ""]
    (OUT / "Community-Summary.md").write_text("\n".join(md))

    # Sources (Markdown + CSV)
    smd = [f"# Source list: {TITLE}", "", f"Accessed and checked {AS_AT}. Primary sources (the Act and ASIC) are S1–S10. "
           "Company and technical sources (S11–S27) are used only to report what those organisations say about themselves.", ""]
    for s in sources:
        status = ""
        if linkcheck:
            r = next((r for r in linkcheck["results"] if r["id"] == s["id"]), None)
            if r:
                status = f" — link check: HTTP {r['status']}"
        smd += [f"**{s['id']}. {s['title']}**  ", f"{s['publisher']} · {s['date']} · {s['type']}{status}  ",
                f"<{s['url']}>  ", f"Supports: {s['used_for']}", ""]
    (OUT / "Sources.md").write_text("\n".join(smd))
    with open(OUT / "Sources.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "title", "publisher", "date", "type", "url", "supports", "http_status_checked"])
        for s in sources:
            st = ""
            if linkcheck:
                r = next((r for r in linkcheck["results"] if r["id"] == s["id"]), None)
                st = r["status"] if r else ""
            w.writerow([s["id"], s["title"], s["publisher"], s["date"], s["type"], s["url"], s["used_for"], st])

    # cite coverage report
    used = sorted(set(re.findall(r"\[\[(S\d+)\|", content + verification_html())), key=lambda x: int(x[1:]))
    unused = [s["id"] for s in sources if s["id"] not in used]
    print("citations:", len(re.findall(r"\[\[S\d+\|", content)), "sources used:", len(used), "unused:", unused)
    print("thread lengths:", [x_len(t) for t in THREAD])


if __name__ == "__main__":
    build()
