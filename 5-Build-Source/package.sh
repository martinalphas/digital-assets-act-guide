#!/usr/bin/env bash
# Copies deliverables into the site and builds the two zip packages.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p site/downloads
cp deliverables/DAF-Act-Tokeniser-Explainer.pdf deliverables/DAF-Act-Tokeniser-Explainer.docx \
   deliverables/Community-Summary.md deliverables/Sources.md deliverables/Sources.csv site/downloads/

STAGE="$(mktemp -d)"
PKG="$STAGE/DAF-Act-Explainer-Package"
mkdir -p "$PKG/1-Explainer" "$PKG/2-Community-Summary" "$PKG/3-Source-List" "$PKG/4-Website" "$PKG/5-Build-Source"
cp README.md "$PKG/"
cp deliverables/DAF-Act-Tokeniser-Explainer.pdf deliverables/DAF-Act-Tokeniser-Explainer.docx "$PKG/1-Explainer/"
cp deliverables/Community-Summary.md "$PKG/2-Community-Summary/"
cp deliverables/Sources.md deliverables/Sources.csv src/linkcheck.json "$PKG/3-Source-List/"
cp -a site/. "$PKG/4-Website/"
rm -rf "$PKG/4-Website/.vercel" "$PKG"/4-Website/_*.html "$PKG"/4-Website/downloads/*.zip
cp src/content.html src/sources.json src/build.py src/linkcheck.py src/make_docs.js src/make_docx.py src/package.sh "$PKG/5-Build-Source/"

rm -f deliverables/*.zip
(cd "$STAGE" && zip -qr -X "$ROOT/deliverables/DAF-Act-Explainer-Package.zip" DAF-Act-Explainer-Package)
(cd "$PKG/4-Website" && zip -qr -X "$ROOT/deliverables/DAF-Act-Website.zip" .)
cp deliverables/DAF-Act-Explainer-Package.zip site/downloads/
rm -rf "$STAGE"
ls -la deliverables
