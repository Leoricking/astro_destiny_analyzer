# Release Notes — Astro Destiny Analyzer v1.9.9

## Version Summary

**v1.9.9 — Product Packaging & Release Build**  
Release date: 2026-05-29  
Build type: Customer Delivery Package

This release finalises the product packaging pipeline, adds customer-facing documentation, and establishes a repeatable release build process with privacy safety checks.

---

## Main Features (v1.9.9)

- `scripts/build_release.py` — automated release ZIP builder with privacy exclusion rules
- `scripts/release_check.py` — pre-release validation checklist (required files, version, privacy)
- `CUSTOMER_README.md` — customer-facing user manual in Traditional Chinese
- `RELEASE_NOTES.md` — this document
- `VERSION.txt` — machine-readable version and feature summary
- Updated `.gitignore` — excludes lead/client/calibration data and credential files
- Updated `README.md` — V1.9.9 packaging and release documentation

---

## New Features Since V1.8.4

### V1.9.9 — Product Packaging & Release Build
- Release ZIP builder with automated privacy exclusion
- Customer README, Release Notes, VERSION.txt
- Pre-release checklist script

### V1.9.8 — Consultant Workflow & Client Case Management
- `consultant_workflow` module: ClientCase, CaseNote, CaseTask, ReportDelivery
- Local JSON storage at `data/client_cases.json`
- 🗂️ 客戶個案 page (Developer / Consultant mode only)
- Create cases from Leads; track status, notes, tasks, deliveries
- Export: CSV / Markdown / HTML per case, metrics summary

### V1.9.7.1 — Default Taiwan Country Fix
- All birth country fields default to 台灣
- Existing user-entered values preserved

### V1.9.7 — Lead Funnel Analytics
- Local funnel event tracking (no external analytics)
- Conversion dashboard (Developer mode)

### V1.9.6 — Free Report Lead Magnet & Email Capture Mock
- Free report form with email capture (local storage only)
- Four report types: zodiac / Human Design / compatibility / integrated summary
- Lead storage at `data/leads_mock.json`

### V1.9.5 — Public Content Landing Pages
- Public-facing content pages for SEO/marketing
- Multiple article templates

### V1.9.0–V1.9.4 — Human Design
- Human Design Type / Profile / Authority / Centers / Gates
- External case import and calibration dataset export
- Exact design date calculation (solar arc 88°)
- Gate wheel calibration

### V1.8.4 — Customer Delivery Mode & Branding
- Customer Mode (hides developer tools by default)
- Developer Mode via `ASTRO_DEVELOPER_MODE=1`
- Branding: BRAND_NAME / BRAND_TAGLINE / REPORT_WATERMARK
- `run.bat` / `run_dev.bat` / `setup.bat` launcher scripts

---

## Release Package Contents

| 含蓋 | 說明 |
|------|------|
| ✅ App source code | `core/`, `engines/`, `reports/`, `ui/`, `compatibility/`, `human_design/`, `human_design_reconciliation/`, `public_content/`, `lead_magnet/`, `consultant_workflow/`, `scripts/` |
| ✅ Launchers | `run.bat`, `setup.bat`, `install_pdf_support.bat` |
| ✅ Documentation | `README.md`, `CUSTOMER_README.md`, `RELEASE_NOTES.md`, `VERSION.txt` |
| ✅ Dependencies | `requirements.txt` |
| ✅ Empty data dirs | `data/`, `data/exports/`, `data/lead_exports/`, `data/client_case_exports/` |
| ❌ 排除 | `.git`, `.venv`, `tests/`, `demo_outputs/`, `data/*.json`, `data/*.db`, `data/*.csv`, `*.log`, `.env`, `*.key`, `*.pem` |

---

## Known Limitations

- **PDF export**: optional, requires WeasyPrint + GTK/Pango on Windows
- **Human Design Gate Wheel**: Phase 1 approximation; external calibration recommended for precision work
- **Email / CRM / Payment**: not integrated — all data remains local
- **Lead & Client data**: stored locally in `data/`; user is responsible for backup and privacy

---

## Privacy Declaration

- All data stored locally in `data/` — no cloud sync by default
- No external Email API
- No payment integration
- No CRM integration
- Release ZIP excludes all personal/lead/client/calibration data
- CSV exports exclude sensitive birth details and internal notes

---

## Test Summary

*(Fill in latest pytest results at build time)*

Run:
```
.venv\Scripts\python -m pytest tests --ignore=tests/test_report_generator.py -q
```

---

## Upgrade Notes

If upgrading from v1.9.8:
1. Run `setup.bat` to update dependencies
2. Existing `data/` files are preserved — no migration needed
3. New `CUSTOMER_README.md`, `RELEASE_NOTES.md`, `VERSION.txt` are added

---

*Astro Destiny Analyzer v1.9.9*
