#!/usr/bin/env python3
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "index.html"
PAYLOAD = ROOT / "tools" / "presentation_polish" / "presentation_polish.html"
START = "<!-- HN_PRESENTATION_POLISH_V216_START -->"
END = "<!-- HN_PRESENTATION_POLISH_V216_END -->"


def fail(msg):
    raise SystemExit(msg)


def main():
    if not INDEX.exists() or INDEX.stat().st_size < 1_000_000:
        fail("Production index.html is missing or unexpectedly small")
    if not PAYLOAD.exists():
        fail("Presentation polish payload is missing")

    html = INDEX.read_text(encoding="utf-8")
    payload = PAYLOAD.read_text(encoding="utf-8").strip()

    if payload.count(START) != 1 or payload.count(END) != 1:
        fail("Presentation payload markers are invalid")
    if "HNPresentationPolishV216" not in payload:
        fail("Presentation payload API marker missing")

    required_before = [
        "HNClinicOutput",
        "HN_TWIN_V215_START",
        "HN_TWIN_V215_END",
        "HN_CLINICAL_ADDONS_V216_START",
        "HN_CLINICAL_ADDONS_V216_END",
        "hnTwinV215Button",
        "hnv216-launch",
        "</body>",
    ]
    missing = [x for x in required_before if x not in html]
    if missing:
        fail("Base production validation failed: " + ", ".join(missing))

    # Remove any previous presentation payload so the installer is idempotent.
    html = re.sub(re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)

    # Presentation-facing metadata/version cleanup only. Core module code is untouched.
    html = re.sub(r"<title>.*?</title>", "<title>HN Radiology Suite v2.16 — Clinical Edition</title>", html, count=1, flags=re.S)
    html = re.sub(
        r'<meta name="description" content="[^"]*"\s*/?>',
        '<meta name="description" content="HN Radiology Suite v2.16 — structured radiology reporting and clinical workflow tools" />',
        html,
        count=1,
    )
    html = html.replace('version:"2.12.0"', 'version:"2.16.0"', 1)
    html = html.replace('versionLabel:"v2.13.1"', 'versionLabel:"v2.16"', 1)
    html = html.replace('buildDate:"2026-08-07"', 'buildDate:"2026-08-18"', 1)
    html = html.replace('HN_v2.13.1_diagnostics_', 'HN_v2.16_diagnostics_')
    html = html.replace('HN Diagnostics — v2.13.1', 'HN Diagnostics — v2.16')
    html = html.replace('v2.13.1 Stable', 'v2.16 Stable')
    html = html.replace('v2.13.1 Check', 'v2.16 Check')

    pos = html.lower().rfind("</body>")
    if pos < 0:
        fail("Closing body tag not found")
    html = html[:pos] + "\n" + payload + "\n" + html[pos:]

    checks = {
        "large_index": len(html.encode("utf-8")) > 1_000_000,
        "single_twin": html.count("HN_TWIN_V215_START") == 1 and html.count("HN_TWIN_V215_END") == 1,
        "single_clinical": html.count("HN_CLINICAL_ADDONS_V216_START") == 1 and html.count("HN_CLINICAL_ADDONS_V216_END") == 1,
        "single_presentation": html.count(START) == 1 and html.count(END) == 1,
        "twin_button": html.count('id="hnTwinV215Button"') == 1,
        "clinical_button": html.count('id="hnv216-launch"') == 1,
        "presentation_toolbar": html.count('id="hn-present-toolbar"') == 1,
        "about_modal": html.count('id="hn-about-modal"') == 1,
        "output_api": "HNClinicOutput" in html,
        "version_title": "HN Radiology Suite v2.16 — Clinical Edition" in html,
        "body_closed": "</body>" in html.lower(),
    }
    if not all(checks.values()):
        fail("Smoke validation failed: " + json.dumps(checks, ensure_ascii=False))

    INDEX.write_text(html, encoding="utf-8")
    report = ROOT / "presentation-smoke-report.json"
    report.write_text(json.dumps({"status": "PASS", "checks": checks}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("PRESENTATION HARDENING PASS")
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    print("index bytes:", INDEX.stat().st_size)


if __name__ == "__main__":
    main()
