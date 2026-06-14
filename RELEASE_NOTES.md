# Release Notes — Astro Destiny Analyzer v2.0.5

## Version Summary

**v2.0.5 — Full UI Localization & RTL Support**
Release date: 2026-06-14
Build type: Commercial MVP — Full UI Localization

This release completes the UI localization layer: all customer-visible Chinese text in the main pages (Home, Input, Calculate, Free Content) is now wrapped in `_tr()` calls. Spanish (es) and Arabic (ar) locales have been added, bringing the total to 6 supported UI languages. Arabic uses RTL CSS injection via the new `i18n/rtl.py` module.

---

## Main Changes (v2.0.5)

- **Spanish locale** (`i18n/locales/es.py`): Full translation of all UI strings
- **Arabic locale** (`i18n/locales/ar.py`): Full translation with RTL support
- **RTL module** (`i18n/rtl.py`): CSS injection for right-to-left layout when Arabic is selected
- **i18n helpers** (`ui/i18n_helpers.py`): Utility functions for translated booleans, mode names, page labels
- **Home page**: Fully localized (welcome text, module table, metric labels, CTA buttons)
- **Input page**: All labels, placeholders, subheaders, validation messages localized
- **Calculate page**: All titles, tabs, metric labels, spinner, error messages localized
- **Free Content page**: Title, subtitle, subheader, empty state localized
- **Config**: `SUPPORTED_UI_LANGUAGES` extended with "es" and "ar"; `RTL_LANGUAGES` set added
- **All existing locales** (zh-TW, en, th, ja): New keys added for complete coverage

### New Files (v2.0.5)

- `i18n/rtl.py` — RTL CSS layout support
- `i18n/locales/es.py` — Spanish translations
- `i18n/locales/ar.py` — Arabic translations
- `ui/i18n_helpers.py` — UI i18n utility functions
- `tests/test_i18n_spanish.py` — Spanish locale tests
- `tests/test_i18n_arabic.py` — Arabic locale and RTL tests
- `tests/test_i18n_full_ui_coverage.py` — Full UI coverage tests

---

# Release Notes — Astro Destiny Analyzer v2.0.4

## Version Summary

**v2.0.4 — Multilingual UI & Report Localization**
Release date: 2026-06-14
Build type: Commercial MVP — Multilingual Release

This release adds a full i18n layer supporting Traditional Chinese (zh-TW), English (en), Thai (th), and Japanese (ja). The UI language can be switched live from the sidebar. Navigation uses stable canonical page IDs instead of translated strings, enabling language switching without breaking session state.

---

## Main Changes (v2.0.4)

- **i18n Module**: New `i18n/` package with `translator.py`, `display_names.py`, and locale files for zh-TW, English, Thai, and Japanese
- **Language Selector**: Sidebar language selector — switches UI language without clearing input state
- **Canonical Page IDs**: `nav_page` session key now stores stable canonical IDs (e.g. `"home"`, `"input"`) instead of translated emoji+label strings
- **Report Language Selector**: Language selector on Report Preview page for future report localization
- **Display Name Translations**: `translate_gender`, `translate_hd_type`, `translate_authority`, `translate_center`, `translate_zodiac` for display layer
- **Home Page Onboarding**: Three-step quick start section now uses `_tr()` for all labels
- **Config**: Added `SUPPORTED_UI_LANGUAGES`, `DEFAULT_LANGUAGE`, `APP_LANGUAGE` to `config.py`
- **Build**: Added `i18n` to `_COLLECT_SUBMODULES` in `build_protected.py`

### New Files (v2.0.4)

- `i18n/__init__.py` — i18n package re-exports
- `i18n/translator.py` — core translation engine with fallback chain
- `i18n/display_names.py` — canonical value display translators
- `i18n/locales/__init__.py` — locales package
- `i18n/locales/zh_TW.py` — Traditional Chinese translations
- `i18n/locales/en.py` — English translations
- `i18n/locales/th.py` — Thai translations
- `i18n/locales/ja.py` — Japanese translations
- `tests/test_i18n_translator.py` — translator unit tests
- `tests/test_i18n_locale_completeness.py` — locale key completeness tests
- `tests/test_i18n_display_names.py` — display name translation tests
- `tests/test_i18n_report.py` — report language tests
- `tests/test_i18n_ui.py` — UI integration tests

---

# Release Notes — Astro Destiny Analyzer v2.0.3

## Version Summary

**v2.0.3 — Protected Trial EXE Package**
Release date: 2026-05-30
Build type: Commercial MVP — Protected Trial Build

This release adds a PyInstaller one-folder protected trial build.
Customers receive a compiled executable package — Python source code is not directly exposed.
No new astrology algorithms or external service integrations.

---

## Main Changes (v2.0.3)

- **Protected Trial Build**: New `scripts/build_protected.py` — PyInstaller one-folder EXE build
- **Protected Smoke Test**: New `scripts/protected_smoke_test.py` — validates protected ZIP
- **App Launcher**: New `app_launcher.py` — PyInstaller entry point with customer/trial env vars
- **Trial Docs**: New `TRIAL_README.txt`, `試用說明.txt`, `start_protected.bat`
- **Release Check**: Added `protected_trial` profile to `release_check.py`
- **Test Coverage**: New `tests/test_protected_packaging.py`, `tests/test_protected_customer_mode.py`

### New Files (v2.0.3)

- `app_launcher.py` — PyInstaller launcher entry point
- `start_protected.bat` — Protected trial startup script
- `TRIAL_README.txt` — Trial version readme (English)
- `試用說明.txt` — Trial version readme (Chinese)
- `requirements-build.txt` — Build-time dependencies (pyinstaller)
- `scripts/build_protected.py` — Protected trial build script
- `scripts/protected_smoke_test.py` — Protected ZIP smoke test

### Privacy & Security (v2.0.3)

- Protected trial build contains no Python source code at the top level
- Source modules compiled to bytecode inside `_internal/` (PyInstaller bundle)
- Note: Python bytecode is not absolute protection against reverse engineering
- Future options: Nuitka, PyArmor, cloud API for core algorithms

---

# Release Notes — Astro Destiny Analyzer v2.0.2

## Version Summary

**v2.0.2 — Release QA Smoke Test & Customer Onboarding Polish**  
Release date: 2026-05-30  
Build type: Commercial MVP — Release QA & UX Polish

This release improves customer onboarding experience, adds release ZIP smoke testing, polishes empty states, and strengthens export format guidance. No new astrology algorithms or external service integrations.

---

## Main Changes (v2.0.2)

- **Customer Onboarding**: New `CUSTOMER_ONBOARDING.md` — step-by-step first-use guide
- **Release Smoke Test**: New `scripts/release_smoke_test.py` — static ZIP validation tool
- **Release QA Checklist**: New `RELEASE_QA_CHECKLIST.md` — Go/No-Go QA document
- **Home Page Onboarding**: Three-step quickstart block with CTA buttons on home page
- **Empty State Polish**: Clearer guidance messages on all pages when no data exists
- **Export Format Guidance**: Updated format recommendation table (HTML 最穩定 / Word 可編輯 / PDF 為選用功能)
- **Config**: `FIRST_RUN_ONBOARDING_ENABLED`, `CUSTOMER_SMOKE_TEST_VERSION` added
- **Test Coverage**: New test files for smoke test, onboarding, and empty states

### New Files

- `CUSTOMER_ONBOARDING.md` — Customer first-use guide
- `RELEASE_QA_CHECKLIST.md` — Release QA checklist
- `scripts/release_smoke_test.py` — ZIP smoke test script
- `tests/test_release_smoke_test.py`
- `tests/test_customer_onboarding.py`
- `tests/test_customer_empty_states.py`

### Not Changed

- Western astrology, BaZi, Zi Wei, Human Design core engines unchanged
- Three-way mode governance (Customer / Consultant / Developer) unchanged
- No Email, Payment, or CRM integration added
- No data transmitted externally

---

## Privacy

All privacy guarantees from V2.0.0 maintained:
- Customer release ZIP excludes: `.git`, `.venv`, `tests/`, `data/*.json`, `.env`, `*.key`, `*.pem`, `run_dev.bat`
- No external data transmission
- All data local-first

---

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
