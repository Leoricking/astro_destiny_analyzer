# Astro Destiny Analyzer — Release Checklist

每次發佈前請依序確認以下項目。

---

## 一、程式碼品質

- [ ] `git status` 工作目錄乾淨（clean working tree）
- [ ] `python -m compileall .` 無語法錯誤
- [ ] `python -m pytest tests -v` 全部通過（允許已知 skip）
- [ ] `config.py` 的 `APP_VERSION` 已更新至正確版本號

---

## 二、環境檢查

- [ ] `python scripts/check_env.py` 全部 [OK]（weasyprint 為 [WARN] 可接受）

---

## 三、Demo 資產

- [ ] `python scripts/generate_demo_assets.py` 無錯誤
- [ ] `demo_outputs/` 下有 MD 和 HTML 檔案
- [ ] 手動開啟至少一個 HTML 確認可正常顯示

---

## 四、Windows 啟動流程

- [ ] 雙擊 `setup.bat` 從乾淨狀態安裝無錯誤
- [ ] 雙擊 `run.bat` 正常啟動 Streamlit
- [ ] 瀏覽器可正常開啟 http://localhost:8501

---

## 五、UI 功能驗證

- [ ] 首頁三個 Demo 按鈕正常載入
- [ ] 計算命盤完整跑完（含西洋 / 八字 / 紫微 / 血型 / 靈數）
- [ ] 報告預覽頁正常顯示
- [ ] 匯出頁可下載 Markdown 和 HTML
- [ ] Word 可下載（若 python-docx 已安裝）
- [ ] PDF 若不可用，顯示友善提示（不顯示錯誤）

---

## 六、建立 Release 包

- [ ] `python scripts/build_release.py` 無錯誤
- [ ] 確認 `release/astro_destiny_analyzer_vX.X.X/` 存在
- [ ] 確認 release 包**不含**以下項目：
  - [ ] `.venv/`
  - [ ] `data/*.db`
  - [ ] `.git/`
  - [ ] `__pycache__/`
  - [ ] `exports/`
- [ ] 確認 release 包含：
  - [ ] `run.bat`
  - [ ] `setup.bat`
  - [ ] `requirements.txt`
  - [ ] `README.md`
  - [ ] `RELEASE_INFO.txt`
  - [ ] `docs/`
  - [ ] `demo/`

---

## 七、文件與版本

- [ ] `README.md` 版本號與 `APP_VERSION` 一致
- [ ] `docs/QUICK_START.md` 內容正確
- [ ] `docs/DEMO_GUIDE.md` 內容正確
- [ ] `docs/PRODUCT_OVERVIEW.md` 內容正確
- [ ] Git tag 已建立：`git tag v{VERSION}`
- [ ] 已推送至遠端：`git push origin main --tags`

---

## 八、ZIP 確認（若有生成）

- [ ] `release/astro_destiny_analyzer_vX.X.X.zip` 存在
- [ ] zip 解壓後可正常啟動
- [ ] zip 不包含 `.venv` 或 `.git`

---

> 以上所有項目確認後，方可正式發佈。
