# Known Issues — Astro Destiny Analyzer v2.0.2

This document records pre-existing known issues as of the V2.0.0 Commercial MVP release.

---

## Zi Wei Stored Snapshot Failures

**Issue:** The full test suite includes approximately 34 pre-existing Zi Wei Dou Shu stored snapshot / expectation failures.

**Details:**
- These failures are snapshot/stored-expectation mismatches in `tests/test_ziwei_multi_case_regression.py` and related Zi Wei test files.
- They were present before V2.0.0 and were NOT introduced by V2.0.0 changes.
- The count has not increased with V2.0.0 changes.
- The failures do not affect new commercial workflow features (consultant workflow, lead funnel, mode governance).
- The Zi Wei Dou Shu calculation engine itself is functional for customer report generation.

**Impact:** Low — does not affect customer-facing report output.

**Resolution:** Pre-existing issue carried forward from V2.0.0. Snapshot refresh and Zi Wei calculation alignment planned for a future version.

---

## PDF Optional Dependency

**Issue:** PDF export requires WeasyPrint, which is NOT included in the default `requirements.txt`.

**Details:**
- WeasyPrint has system-level dependencies (GTK, Cairo, Pango) that vary by platform.
- On Windows, installation can require additional system libraries.
- The `install_pdf_support.bat` script attempts to install WeasyPrint.

**Impact:** Medium for customers expecting PDF output.

**Workaround:** Use HTML or Word (.docx) export, which work without WeasyPrint.

**Resolution:** Customers can install WeasyPrint via `install_pdf_support.bat`. No core feature changes required.

---

## Human Design External Validation Limitations

**Issue:** The Human Design gate wheel table and external site reconciliation require more multi-case calibration.

**Details:**
- The current implementation uses a Phase 1 gate wheel with a configurable offset.
- Results may differ from some external Human Design platforms depending on their gate calculation methods.
- The `data/human_design_calibration_cases.json` dataset is used internally for calibration and is not distributed in customer releases.

**Impact:** Low to medium — HD chart values are calculated correctly per internal algorithm, but may not match all external platforms exactly.

**Resolution:** Ongoing calibration. Not claimed to be 100% consistent with all external platforms.

---

## Email / Payment / CRM Integration

**Issue:** No real external services are integrated.

**Details:**
- Email capture (lead magnet) stores locally only — no actual email is sent.
- No payment gateway is integrated.
- No CRM integration exists.
- All data is local-first.

**Impact:** None for current use case. This is by design.

**Resolution:** Future versions may add optional integrations. Current design is intentionally local-only.

---

## Run Consultant Mode on First Launch

**Issue:** `run_consultant.bat` requires the virtual environment to exist (created by `setup.bat` or `run.bat`).

**Workaround:** Run `setup.bat` or `run.bat` once before using `run_consultant.bat`.

---

*Last updated: 2026-05-30*  
*Version: 2.0.2*
