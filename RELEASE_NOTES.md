# Release Notes — Astro Destiny Analyzer v2.0.0

## Version Summary

**v2.0.0 — Commercial MVP Stabilization**  
Release date: 2026-05-29  
Build type: Commercial MVP — multi-profile release

This release establishes the Commercial MVP foundation: three-way mode governance (Customer / Consultant / Developer), multi-profile release builds, preflight health check, and comprehensive documentation.

---

## Main Features (v2.0.0)

- Three-way mode governance: Customer / Consultant / Developer
- `CUSTOMER_PAGES`, `CONSULTANT_PAGES`, `DEVELOPER_PAGES` page lists
- `get_active_pages()` / `is_page_allowed()` helpers
- Stale navigation guard (auto-reset to home if page not in active list)
- `📊 Lead Funnel` page (Consultant / Developer mode)
- `run_consultant.bat` — dedicated Consultant Mode launcher
- `BUILD_PROFILE` config variable (`customer` | `consultant` | `developer`)
- `scripts/preflight_check.py` — environment and readiness health check
- `scripts/seed_demo_data.py` — demo seed data generator (not auto-run)
- `scripts/build_release.py --profile` — multi-profile release ZIP builder
- `scripts/release_check.py --profile` — multi-profile release validation
- `COMMERCIAL_MVP_CHECKLIST.md` — Go/No-Go release checklist
- `KNOWN_ISSUES.md` — documented pre-existing known issues
- `CONSULTANT_README.md` — consultant mode user manual
- Updated `CUSTOMER_README.md` — v2.0.0
- Updated `README.md` — V2.0.0 build/release documentation

---

## Privacy

All privacy guarantees from V1.9.9 are maintained:
- Customer release ZIP excludes: `.git`, `.venv`, `tests/`, `data/*.json`, `.env`, `*.key`, `*.pem`, personal demo filenames
- Consultant release ZIP excludes: `run_dev.bat`, private data
- All profiles: `.env` / credential files always excluded

---

## New Features Since V1.8.4

### V2.0.0 — Commercial MVP Stabilization
- Three-way mode governance (Customer / Consultant / Developer)
- `📊 Lead Funnel` navigation page (Consultant mode)
- `run_consultant.bat` dedicated launcher
- `BUILD_PROFILE` environment variable
- Preflight health check script
- Demo seed data generator
- Multi-profile build and release check
- Commercial MVP checklist, Known Issues, Consultant README

### V1.9.9 — Product Packaging & Release Build
- Release ZIP builder with automated privacy exclusion
- Customer README, Release Notes, VERSION.txt
- Pre-release checklist script

### V1.9.8 — Consultant Workflow & Client Case Management
- `consultant_workflow` module: ClientCase, CaseNote, CaseTask, ReportDelivery
- Local JSON storage at `data/client_cases.json`
- 🗂️ 客戶個案 page (Consultant / Developer mode)
- Create cases from Leads; track status, notes, tasks, deliveries
- Export: CSV / Markdown / HTML per case, metrics summary

### V1.9.7.1 — Default Taiwan Country Fix
- All birth country fields default to 台灣

### V1.9.7 — Lead Funnel Analytics
- Local funnel event tracking (no external analytics)
- Lead analytics now accessible via dedicated Lead Funnel page (Consultant mode, V2.0.0)

### V1.9.6 — Free Report Lead Magnet & Email Capture Mock
- Free report form with email capture (local storage only)
- Four report types: zodiac / Human Design / compatibility / integrated summary
- Lead storage at `data/leads_mock.json`

### V1.9.5 — Public Content Landing Pages
- Public-facing content pages for SEO/marketing

### V1.9.0–V1.9.4 — Human Design
- Human Design Type / Profile / Authority / Centers / Gates
- External case import and calibration dataset export
- Exact design date calculation (solar arc 88°)
- Gate wheel calibration

### V1.8.4 — Customer Delivery Mode & Branding
- Customer Mode (hides developer tools by default)
- Developer Mode via `ASTRO_DEVELOPER_MODE=1`
- Branding: BRAND_NAME / BRAND_TAGLINE / REPORT_WATERMARK

---

## Release Profiles

| Profile | ZIP Name | Includes | Excludes |
|---------|----------|----------|---------|
| customer | `astro_destiny_analyzer_v2.0.0_customer.zip` | run.bat, app source, customer docs | run_dev.bat, run_consultant.bat, tests/, private data |
| consultant | `astro_destiny_analyzer_v2.0.0_consultant.zip` | run_consultant.bat, consultant_workflow, lead_magnet | run_dev.bat, tests/, private data |
| developer | `astro_destiny_analyzer_v2.0.0_developer.zip` | run_dev.bat, tests/ | .git, .venv, private data, credentials |

---

## Known Limitations

See `KNOWN_ISSUES.md` for full details.

- **Zi Wei snapshot failures**: ~34 pre-existing test snapshot mismatches (not new in V2.0.0)
- **PDF export**: optional, requires WeasyPrint
- **Human Design Gate Wheel**: Phase 1; external calibration recommended
- **Email / CRM / Payment**: not integrated — all data remains local

---

## Privacy Declaration

- All data stored locally in `data/` — no cloud sync
- No external Email API
- No payment integration
- No CRM integration
- Release ZIPs exclude all personal/lead/client/calibration data
- Demo seed data excluded from all customer release ZIPs

---

## Upgrade Notes

If upgrading from v1.9.9:
1. Run `setup.bat` to confirm dependencies
2. Existing `data/` files are preserved — no migration needed
3. New files added: `run_consultant.bat`, `CONSULTANT_README.md`, `COMMERCIAL_MVP_CHECKLIST.md`, `KNOWN_ISSUES.md`

---

*Astro Destiny Analyzer v2.0.0*
