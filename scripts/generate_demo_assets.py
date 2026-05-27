"""
Astro Destiny Analyzer — Demo Asset Generator
Reads demo/sample_profiles.py and generates MD / HTML / DOCX / PDF
reports into demo_outputs/.

Usage:
    python scripts/generate_demo_assets.py

Exit code: 0 = all profiles succeeded, 1 = at least one profile failed.
"""
import sys
import os

# Allow running from project root or scripts/
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "demo_outputs")


def _safe_name(name: str) -> str:
    """Convert a profile name to a safe filename stem."""
    import re
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t\s]+', "_", name)
    return cleaned.strip("_")[:60] or "demo"


def _generate_one(profile, output_dir: str) -> dict:
    """
    Generate all report formats for one profile.
    Returns a dict: {format: path_or_None, 'errors': [str]}
    """
    from reports.generator import ReportGenerator
    from reports.markdown_exporter import MarkdownExporter
    from reports.html_exporter import HtmlExporter
    from reports.docx_exporter import DocxExporter
    from reports.pdf_exporter import PdfExporter

    results = {"errors": []}
    stem = _safe_name(profile.name)

    gen = ReportGenerator()
    try:
        report = gen.generate(profile, persist=False)
    except Exception as exc:
        results["errors"].append(f"ReportGenerator failed: {exc}")
        return results

    # Markdown
    try:
        md_path = os.path.join(output_dir, f"{stem}.md")
        md_content = MarkdownExporter().export(report)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        results["md"] = md_path
        print(f"[OK]   Generated Markdown : {md_path}")
    except Exception as exc:
        results["errors"].append(f"Markdown failed: {exc}")
        print(f"[FAIL] Markdown: {exc}")

    # HTML
    try:
        html_path = os.path.join(output_dir, f"{stem}.html")
        html_content = HtmlExporter().export(report)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        results["html"] = html_path
        print(f"[OK]   Generated HTML     : {html_path}")
    except Exception as exc:
        results["errors"].append(f"HTML failed: {exc}")
        print(f"[FAIL] HTML: {exc}")

    # DOCX (optional)
    docx_exp = DocxExporter()
    if docx_exp.is_available():
        try:
            docx_path = os.path.join(output_dir, f"{stem}.docx")
            docx_bytes = docx_exp.export(report)
            with open(docx_path, "wb") as f:
                f.write(docx_bytes)
            results["docx"] = docx_path
            print(f"[OK]   Generated DOCX     : {docx_path}")
        except Exception as exc:
            results["errors"].append(f"DOCX failed: {exc}")
            print(f"[FAIL] DOCX: {exc}")
    else:
        print("[WARN] DOCX unavailable — pip install python-docx")

    # PDF (optional)
    pdf_exp = PdfExporter()
    if pdf_exp.is_available():
        try:
            pdf_path = os.path.join(output_dir, f"{stem}.pdf")
            pdf_bytes = pdf_exp.export(report)
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            results["pdf"] = pdf_path
            print(f"[OK]   Generated PDF      : {pdf_path}")
        except Exception as exc:
            results["errors"].append(f"PDF failed: {exc}")
            print(f"[FAIL] PDF: {exc}")
    else:
        print("[WARN] PDF unavailable — pip install weasyprint")

    return results


def main() -> int:
    """Generate demo assets for all sample profiles. Returns 0 on success."""
    from demo.sample_profiles import SAMPLE_PROFILES

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    total = len(SAMPLE_PROFILES)
    success = 0
    failed = 0

    for profile in SAMPLE_PROFILES:
        print(f"── Generating: {profile.name} ──")
        result = _generate_one(profile, OUTPUT_DIR)
        if result.get("errors"):
            failed += 1
            for err in result["errors"]:
                print(f"   [ERROR] {err}")
        else:
            success += 1
        print()

    print("=" * 60)
    print(f"Summary: {total} profiles | {success} succeeded | {failed} failed")
    print(f"Output : {OUTPUT_DIR}")
    print("=" * 60)

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
