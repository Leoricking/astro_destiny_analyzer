# Commercial MVP Checklist — Astro Destiny Analyzer v2.0.0

This checklist confirms readiness for a Commercial MVP release.

---

## App Modes

### Customer Mode
- [ ] `ASTRO_CUSTOMER_MODE=1` in run.bat
- [ ] `ASTRO_CONSULTANT_MODE=0` in run.bat
- [ ] `ASTRO_DEVELOPER_MODE=0` in run.bat
- [ ] `ASTRO_BUILD_PROFILE=customer` in run.bat
- [ ] Customer page list contains: 首頁, 免費內容入口, 免費報告, 輸入資料, 計算命盤, 報告預覽, 歷史報告, 匯出, 合盤分析, 設定
- [ ] Customer page list does NOT contain: Lead Funnel, 客戶個案, 紫微校準, 人類圖校準
- [ ] Demo data hidden (SHOW_DEMO_DATA=False)
- [ ] No internal debug labels visible

### Consultant Mode
- [ ] `ASTRO_CONSULTANT_MODE=1` in run_consultant.bat
- [ ] `ASTRO_DEVELOPER_MODE=0` in run_consultant.bat
- [ ] `ASTRO_BUILD_PROFILE=consultant` in run_consultant.bat
- [ ] Consultant pages include: Lead Funnel, 客戶個案
- [ ] Consultant pages do NOT include: 紫微校準, 人類圖校準
- [ ] run_consultant.bat launches correctly

### Developer Mode
- [ ] `ASTRO_DEVELOPER_MODE=1` in run_dev.bat
- [ ] `ASTRO_CONSULTANT_MODE=1` in run_dev.bat
- [ ] `ASTRO_BUILD_PROFILE=developer` in run_dev.bat
- [ ] Developer pages include: ALL pages including calibration tools
- [ ] Calibration tools accessible: 紫微校準, 人類圖校準
- [ ] SHOW_DEMO_DATA=1

---

## Customer Delivery

### Setup & Launch
- [ ] `setup.bat` installs dependencies successfully
- [ ] `run.bat` launches Streamlit in Customer Mode
- [ ] `install_pdf_support.bat` installs WeasyPrint (optional)
- [ ] `CUSTOMER_README.md` covers setup steps in Traditional Chinese

### Export
- [ ] HTML export works (reports/html_exporter.py)
- [ ] Word (.docx) export works
- [ ] Markdown export works
- [ ] PDF export works when WeasyPrint installed (optional)

---

## Privacy

- [ ] No external email API calls
- [ ] No payment integration
- [ ] No CRM integration
- [ ] All lead/client data stored locally in `data/`
- [ ] No external data transmission
- [ ] Release ZIP excludes: leads_mock.json, client_cases.json, calibration data
- [ ] Release ZIP excludes: .env, *.key, *.pem, *.token
- [ ] Release ZIP excludes: Rossi filenames, demo_outputs
- [ ] Release ZIP excludes: .git, .venv, tests/ (customer profile)

---

## Reports

- [ ] Natal chart: Western Astrology (Swiss Ephemeris)
- [ ] Natal chart: BaZi (Four Pillars, solar-term precision)
- [ ] Natal chart: Zi Wei Dou Shu (Phase 1, auxiliary stars, Da Xian)
- [ ] Natal chart: Human Design (Type / Profile / Authority / Centers / Gates)
- [ ] Compatibility report (multi-system synastry)
- [ ] Free report (lead magnet: zodiac / HD type / compatibility / integrated summary)
- [ ] Numerology card
- [ ] Blood type analysis

---

## Funnel / Consultant Tools

- [ ] Lead Magnet page (免費報告) captures name + email + consent
- [ ] Leads stored locally in `data/leads_mock.json`
- [ ] Lead Funnel page shows analytics (Consultant Mode only)
- [ ] Client Cases page (Consultant Mode only)
- [ ] Case: create from Lead, add notes/tasks/deliveries
- [ ] Export: CSV, Markdown, HTML per case
- [ ] Export: metrics summary Markdown

---

## Release Build

- [ ] `python scripts/release_check.py --profile customer` → all PASS
- [ ] `python scripts/release_check.py --profile consultant` → all PASS
- [ ] `python scripts/release_check.py --profile developer` → all PASS
- [ ] `python scripts/build_release.py --profile customer` → ZIP created
- [ ] `python scripts/build_release.py --profile consultant` → ZIP created
- [ ] Customer ZIP name: `astro_destiny_analyzer_v2.0.0_customer.zip`
- [ ] Consultant ZIP name: `astro_destiny_analyzer_v2.0.0_consultant.zip`
- [ ] Developer ZIP name: `astro_destiny_analyzer_v2.0.0_developer.zip`
- [ ] VERSION.txt: `Version: 2.0.0`
- [ ] No forbidden entries in customer ZIP (verified by zip safety checker)

---

## Known Issues

See `KNOWN_ISSUES.md` for documented limitations.

---

## Go / No-Go Checklist

Before customer delivery:

- [ ] `python scripts/preflight_check.py` → all required PASS
- [ ] `python scripts/release_check.py --profile customer` → all PASS
- [ ] Customer ZIP built and manually spot-checked
- [ ] CUSTOMER_README.md reviewed — no internal terms
- [ ] No Rossi / golden case / debug content in customer-facing files
- [ ] Release ZIP manually extracted and `run.bat` tested
- [ ] Known issues reviewed and acceptable for this release
