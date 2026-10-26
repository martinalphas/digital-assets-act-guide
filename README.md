# Australia's Digital Assets Framework Act: What It Means for Tokeniser

A plain-language explainer of the *Corporations Amendment (Digital Assets Framework) Act 2026*, prepared for review by the Redbelly DAO. It covers what the Act is, who needs a licence, the timeline, what changes for issuers who tokenise through Tokeniser, and where Redbelly's compliance design fits or is unclear.

**General information only. This is not legal advice.** The information is current as at 26 October 2026. This is not an official publication of Redbelly Network, Tokeniser, ASIC or the Australian Government, and it does not claim that anyone is licensed or compliant.

## Deliverables (mapped to the brief)

| Brief requirement | File |
|---|---|
| 1. Explainer (Word file or PDF) | `deliverables/DAF-Act-Tokeniser-Explainer.pdf` (A4, 29 pages including annexes) and `deliverables/DAF-Act-Tokeniser-Explainer.docx` (editable) |
| 2. Community summary (X thread or paragraphs) | `deliverables/Community-Summary.md`: a 9-post X thread (each post checked at 280 characters or fewer) plus three short paragraphs |
| 3. Source list with a link for every factual claim | `deliverables/Sources.md` and `deliverables/Sources.csv` (27 sources, each with what it supports), plus `src/linkcheck.json` (results of the link and content check) |
| Website | `site/` is a static site, with `site/index.html` as the full explainer. It deploys to Vercel as is. |

### Scope checklist
- Not-legal-advice statement: first block of the website, the PDF cover and page 2, the Word file, the PDF footer on every page, and the community summary.
- What the Act is and why it was introduced: section 02.
- Who needs a licence and who does not: section 04, with the low-value thresholds of $10 million and $5,000 taken from s 911A(2)(ja).
- Timeline before and after commencement: section 05.
- What changes for issuers using Tokeniser: section 06.
- Where Redbelly's design lines up, and where it is unclear: section 07.
- Separating law from analysis: every block is labelled *The Act says*, *ASIC says* (with *draft* flagged), *Company statement* or *Our analysis*.

## Note for reviewers: the commencement date
The brief says the Act commences on **9 April 2027**. The Act (s 2: "the day after the end of the period of 12 months beginning on the day this Act receives the Royal Assent"; the commencement table gives 8 April 2027) and ASIC's latest material (26-245MR and CP 392, 15 October 2026) give **8 April 2027**. ASIC's April 2026 roadmap and a May 2026 news item said 9 April 2027. The explainer uses 8 April 2027 and explains the difference, citing all of these sources.

## Verification
- Every factual statement carries an inline citation with a pinpoint, such as `S1 · s 911A(2)(ja)` or `S6 · RG 000.35 note`.
- `src/linkcheck.py` fetched all 27 source URLs and confirmed that the phrase each citation relies on appears in the source. All 27 returned HTTP 200, and all cited phrases were found (see `src/linkcheck.json`).
- No factual claim relies on news coverage or law-firm commentary.

## Deploy the website

**Vercel CLI** (from this folder):
```bash
npx vercel@latest deploy site --prod
```

**Vercel dashboard:** create a new project, import or upload the `site/` folder, and set the framework preset to "Other". No build command is needed.

The site is fully static: one `index.html`, with the CSS, fonts and logos in `site/assets/` and the files in `site/downloads/`. Nothing loads from third-party CDNs.

## Rebuild from source
```bash
python3 src/linkcheck.py                 # re-check every source (optional)
SITE_URL=https://<your-domain> python3 src/build.py
(cd site && python3 -m http.server 8765 &)
node src/make_docs.js http://127.0.0.1:8765   # PDF + social image (needs Playwright/Chromium)
python3 src/make_docx.py                       # Word file (needs pandoc + python-docx)
```
- Content: `src/content.html`. Citations use `[[S#|pinpoint]]`.
- Sources: `src/sources.json`.
- The community summary text is in `src/build.py` (`THREAD`, `PARAGRAPHS`).

## Brand
The visual identity follows the published Redbelly brand guidelines (https://redbelly.network/brand):
- Typeface: Readex Pro, self-hosted under the SIL Open Font License (`site/assets/fonts/OFL.txt`).
- Main colours: #FF5050 and #283A46. Secondary colours: #FA423C, #142530, #848B91, #DCDCDC and #ECEBEC.
- Logos: the official SVG files from the brand pack, used unaltered.
