# Release QA Checklist — v2.0.2

> 本文件用於 Release QA 驗收，確認客戶 ZIP 交付品質。  
> 完成所有 PASS 後方可執行正式 Go。

---

## 1. ZIP 解壓測試

- [ ] ZIP 檔案可正常下載
- [ ] ZIP 檔案可完整解壓縮（無損壞）
- [ ] 解壓縮後資料夾結構正確
- [ ] 必要檔案全部存在：`run.bat`、`setup.bat`、`install_pdf_support.bat`、`CUSTOMER_README.md`、`CUSTOMER_ONBOARDING.md`、`VERSION.txt`、`RELEASE_NOTES.md`、`requirements.txt`、`config.py`、`ui/streamlit_app.py`
- [ ] 禁止內容不存在：`.git`、`.venv`、`tests/`、`data/leads_mock.json`、`data/client_cases.json`、`.env`、`*.key`、`*.pem`、`run_dev.bat`（customer profile）

---

## 2. setup.bat 測試

- [ ] 雙擊 `setup.bat` 可正常執行
- [ ] 套件安裝完成（streamlit、pydantic、python-docx 等）
- [ ] 安裝過程無致命錯誤
- [ ] `.venv` 資料夾成功建立

---

## 3. run.bat 測試

- [ ] 雙擊 `run.bat` 可正常啟動
- [ ] 瀏覽器自動開啟 `http://localhost:8501`
- [ ] 首頁正常顯示（標題、三步驟 Onboarding 區塊可見）
- [ ] 左側選單顯示正確頁面（Customer Mode 頁面清單）

---

## 4. 首頁 Onboarding 檢查

- [ ] 「快速開始：三步驟建立第一份報告」區塊可見
- [ ] 三步驟卡片正確顯示（輸入資料、計算命盤、匯出報告）
- [ ] CTA 按鈕可點擊（開始輸入資料、建立合盤分析、查看免費內容、領取免費摘要）
- [ ] 不顯示 Developer / Calibration / Debug 相關內容

---

## 5. 輸入資料測試

- [ ] 前往「📝 輸入資料」頁面正常顯示
- [ ] 出生國家預設顯示「台灣」
- [ ] 姓名、日期、時間、城市欄位可正常輸入
- [ ] 儲存後資料保留正確

---

## 6. 命盤計算測試

- [ ] 前往「🔮 計算命盤」可正常執行
- [ ] 計算完成後顯示結果（西洋占星、八字、紫微、人類圖）
- [ ] 無 crash 或 Traceback

---

## 7. 合盤測試

- [ ] 前往「💕 合盤分析」頁面正常顯示
- [ ] 未輸入資料時顯示提示訊息
- [ ] A 方 / B 方資料可分別輸入
- [ ] 計算合盤後結果正常顯示

---

## 8. 免費內容入口測試

- [ ] 前往「🌐 免費內容入口」頁面正常顯示
- [ ] 精選內容卡片可見
- [ ] 分類篩選功能正常

---

## 9. 免費報告測試

- [ ] 前往「🎁 免費報告」頁面正常顯示
- [ ] 「資料只儲存在本機，不會外送」說明可見
- [ ] 填寫 Email 與基本資料可送出
- [ ] 免費摘要正常產生

---

## 10. 匯出 HTML / Word / Markdown 測試

- [ ] 「📤 匯出」頁面正常顯示
- [ ] 格式建議區塊可見（HTML 最穩定 / Word 可編輯 / PDF 為選用功能）
- [ ] HTML 下載按鈕可使用 → 下載檔案可正常在瀏覽器開啟
- [ ] Word 下載按鈕可使用 → 下載 .docx 可在 Word 開啟
- [ ] Markdown 下載按鈕可使用 → 下載 .md 可正常閱讀

---

## 11. PDF Optional 測試

- [ ] 未安裝 WeasyPrint 時，PDF 按鈕顯示「未安裝」提示（非紅色錯誤）
- [ ] 提示說明如何安裝（install_pdf_support.bat 或 pip install weasyprint）
- [ ] 安裝後 PDF 可正常匯出

---

## 12. 客戶模式 Forbidden Pages 檢查

- [ ] 左側選單不顯示「🧭 紫微校準」
- [ ] 左側選單不顯示「🔷 人類圖校準」
- [ ] 左側選單不顯示「📊 Lead Funnel」
- [ ] 左側選單不顯示「🗂️ 客戶個案」
- [ ] 手動導航至 forbidden page 時自動跳回首頁

---

## 13. 隱私資料排除檢查

- [ ] ZIP 不含 `data/leads_mock.json`
- [ ] ZIP 不含 `data/client_cases.json`
- [ ] ZIP 不含 `data/human_design_calibration_cases.json`
- [ ] ZIP 不含 `.env`
- [ ] ZIP 不含 `*.key`、`*.pem`
- [ ] ZIP 不含 `tests/` 資料夾
- [ ] ZIP 不含 `run_dev.bat`（customer profile）

---

## 14. release_check

```bat
.venv\Scripts\python scripts\release_check.py --profile customer
```

- [ ] 所有 PASS
- [ ] APP_VERSION == 2.0.2
- [ ] CUSTOMER_ONBOARDING.md 存在
- [ ] RELEASE_QA_CHECKLIST.md 存在

---

## 15. build_release

```bat
.venv\Scripts\python scripts\build_release.py --profile customer
```

- [ ] ZIP 成功建立於 `release/astro_destiny_analyzer_v2.0.2_customer.zip`
- [ ] 無 WARN 或 FAIL 訊息

---

## 16. Smoke Test

```bat
.venv\Scripts\python scripts\release_smoke_test.py --zip release\astro_destiny_analyzer_v2.0.2_customer.zip --profile customer
```

- [ ] PASS
- [ ] 所有必要檔案存在
- [ ] 所有禁止內容不存在
- [ ] VERSION.txt 包含 2.0.2

---

## Go / No-Go

| 項目 | 狀態 |
|------|------|
| ZIP smoke test PASS | ⬜ |
| release_check PASS | ⬜ |
| build_release 成功 | ⬜ |
| 首頁 Onboarding 可見 | ⬜ |
| 匯出功能正常 | ⬜ |
| Forbidden pages 已隱藏 | ⬜ |
| 隱私資料已排除 | ⬜ |

**Go** = 全部 ✅ 後可交付客戶

---

*Astro Destiny Analyzer v2.0.2 — Release QA Checklist*
