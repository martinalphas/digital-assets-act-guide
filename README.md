# Australia's Digital Assets Framework Act: What It Means for Tokeniser

A plain-language explainer of the **Corporations Amendment (Digital Assets Framework) Act 2026**. It covers what the Act is, who needs a licence and who does not, the key dates, what changes for issuers who tokenise through Tokeniser, and where Redbelly's built-in compliance design lines up with the new rules and where it is unclear.

**Live site:** https://digital-assets-act-guide.vercel.app

> [!IMPORTANT]
> **General information only. This is not legal advice.** The information is current as at 26 October 2026. This is an independent community explainer prepared for review by the Redbelly DAO. It is not an official publication of Redbelly Network, Tokeniser, ASIC or the Australian Government. It does not claim that Redbelly, Tokeniser or any issuer is licensed or compliant. Get advice from a qualified Australian lawyer before acting on anything here.

---

## Quick links

| Deliverable | Format | Link |
|---|---|---|
| Explainer | PDF (A4, print-ready, about 20 minutes to read) | [`1-Explainer/DAF-Act-Tokeniser-Explainer.pdf`](1-Explainer/DAF-Act-Tokeniser-Explainer.pdf) |
| Explainer | Word (editable) | [`1-Explainer/DAF-Act-Tokeniser-Explainer.docx`](1-Explainer/DAF-Act-Tokeniser-Explainer.docx) |
| Community summary | X thread (9 posts) and short paragraphs | [`2-Community-Summary/Community-Summary.md`](2-Community-Summary/Community-Summary.md) |
| Source list | Markdown and CSV, with the link-check log | [`3-Source-List/`](3-Source-List/) |
| Website | Static site, deployed on Vercel | [`4-Website/`](4-Website/) · [live](https://digital-assets-act-guide.vercel.app) |
| Everything in one file | ZIP | [`zips/DAF-Act-Explainer-Package.zip`](zips/DAF-Act-Explainer-Package.zip) |

## Key facts at a glance

| | |
|---|---|
| **Royal Assent** | 8 April 2026 (Act No. 38, 2026) |
| **Commencement** | 8 April 2027, per the Act (s 2) and ASIC CP 392 ([see note](#a-note-on-the-commencement-date)) |
| **Transition** | Six months from commencement. Existing operators must apply by **7 October 2027** and can keep operating while ASIC assesses their application. |
| **What is regulated** | Two new financial products: digital asset platforms (DAPs) and tokenised custody platforms (TCPs) |
| **Regulator** | ASIC, through Australian financial services (AFS) licensing |
| **ASIC consultation** | CP 392. Submissions close 27 November 2026, and final standards and guidance are planned for March 2027. |

## What the explainer covers

1. **The short version**: the Act in five points.
2. **Why the Act was introduced**: ASIC's stated purpose, the "same activity, same risk, same regulatory outcome" principle, and how the Act builds on INFO 225.
3. **Key ideas in plain English**: digital token, possession, DAP, TCP, public digital token infrastructure (PDTI), wrapped tokens and custodial staking.
4. **Who needs a licence, and who does not**: operators, intermediaries and the exemptions. The low-value DAP exemption, for example, requires $10 million or less in transactions over 12 months and $5,000 or less in entry value per client.
5. **Timeline**: dates before and after commencement, including the transition window.
6. **What changes for issuers using Tokeniser**: what stays the same, where the new rules can reach an issuer, and five questions to take to a lawyer.
7. **Where Redbelly's compliance design fits**: a requirement-by-requirement comparison, plus the open questions (PDTI status, and whether admin powers count as "possession").
8. **What to watch next**.

## How to read it

Every statement is labelled so that the law is kept separate from analysis:

| Label | Meaning |
|---|---|
| **The Act says** | Taken directly from the Act |
| **ASIC says** | ASIC statements. Proposals are marked *draft*. |
| **Company statement** | What Redbelly or Tokeniser say about themselves (not verified) |
| **Our analysis** | The writer's interpretation, not settled law |

Every factual claim links to a numbered source with a pinpoint, for example `S1 · s 911A(2)(ja)` or `S6 · RG 000.35 note`.

## Sources and verification

- **27 sources.** Primary sources come first: the Act itself (S1) and ASIC material (S2–S10). Redbelly and Tokeniser pages (S11–S27) are used only to report what those organisations say about themselves.
- **No factual claim relies on news coverage or law-firm commentary.**
- **Link and content check.** Every source URL was fetched and returned HTTP 200 (27 of 27, re-checked 30 October 2026). For each source, the exact phrase the explainer relies on was confirmed to be present, including the wording of s 9E that the explainer quotes. The log is in [`3-Source-List/linkcheck.json`](3-Source-List/linkcheck.json).

### A note on the commencement date
The Act commences on "the day after the end of the period of 12 months beginning on the day this Act receives the Royal Assent" (s 2). The commencement table published with the Act, and ASIC's latest material (26-245MR and CP 392, 15 October 2026), both give **8 April 2027**. Some earlier ASIC pages, including the April 2026 roadmap, said 9 April 2027. The explainer uses 8 April 2027 and cites all of these sources.

## Repository structure

```
├── 1-Explainer/           PDF and Word versions of the explainer
├── 2-Community-Summary/   X thread and short paragraphs
├── 3-Source-List/         Sources.md, Sources.csv, linkcheck.json
├── 4-Website/             Static site (index.html, assets/, downloads/, vercel.json)
├── 5-Build-Source/        Content, source data and build scripts
└── zips/                  Full package and website-only archives
```

## Deploying the website

The site is fully static. It has no build step and no third-party CDNs, and the fonts and logos are self-hosted.

**Vercel**
1. Import this repository into Vercel.
2. Set **Root Directory** to `4-Website`.
3. Set **Framework Preset** to `Other`, and leave the build command and output directory empty.
4. Deploy.

**Any static host:** serve the contents of `4-Website/` as the web root.

## Rebuilding from source

The build scripts use a `src/` and `site/` layout. To rebuild:

```bash
mkdir work && cp -r 5-Build-Source work/src && cp -r 4-Website work/site
cp 3-Source-List/linkcheck.json work/src/ && cp work/src/_og.html work/site/
cd work
python3 src/linkcheck.py                                   # optional: re-check every source
python3 src/build.py                                       # links point to the live site; override with PUBLIC_URL
(cd site && python3 -m http.server 8765 &)
node src/make_docs.js http://127.0.0.1:8765                # PDF and social image (Playwright)
python3 src/make_docx.py                                   # Word file (pandoc and python-docx)
```

- Explainer text: `src/content.html`. Citations are written as `[[S#|pinpoint]]`.
- Source register: `src/sources.json`.
- Community summary text: `THREAD` and `PARAGRAPHS` in `src/build.py`.

## Brand and typeface

The visual identity follows the published [Redbelly brand guidelines](https://redbelly.network/brand):
- Typeface: Readex Pro.
- Main colours: `#FF5050` and `#283A46`.
- Secondary colours: `#FA423C`, `#142530`, `#848B91`, `#DCDCDC` and `#ECEBEC`.
- Logos: the official SVG files, used unaltered.

Readex Pro is distributed under the SIL Open Font License; the licence is in [`4-Website/assets/fonts/OFL.txt`](4-Website/assets/fonts/OFL.txt).

---

<sub>General information only, as at 26 October 2026. Not legal, financial, tax or investment advice.</sub>
