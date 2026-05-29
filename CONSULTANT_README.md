# Astro Destiny Analyzer — 顧問版使用手冊

> **隱私提醒**  
> 所有客戶資料均儲存於本機 `data/` 目錄，不上傳至外部伺服器。  
> 不串接外部 CRM、Email 或付款服務。

---

## Consultant Mode 是什麼

Consultant Mode（顧問模式）是為命理顧問設計的工作模式，在標準客戶功能之外，提供以下額外工具：

| 功能 | 說明 |
|------|------|
| 📊 Lead Funnel | 查看 Lead 來源統計與轉換漏斗 |
| 🗂️ 客戶個案 | 建立與追蹤客戶個案、備註、待辦、報告交付 |

開發者校準工具（紫微校準、人類圖校準）在顧問模式下不顯示。

---

## 如何啟動 Consultant Mode

使用專屬啟動腳本：

```
run_consultant.bat
```

這會自動設定以下環境變數：
- `ASTRO_CONSULTANT_MODE=1`
- `ASTRO_DEVELOPER_MODE=0`
- `ASTRO_BUILD_PROFILE=consultant`

啟動後開啟瀏覽器：`http://localhost:8501`

> 第一次使用前，請先執行 `setup.bat` 安裝必要套件。

---

## Lead Funnel

在側邊欄選擇「📊 Lead Funnel」頁面。

功能：
- 查看總 Lead 數
- 依報告類型分佈
- 同意條款率 / 行銷同意率
- 轉換漏斗概覽

Lead 資料來源：客戶透過「免費報告」頁面提交的表單，儲存於 `data/leads_mock.json`。

---

## 客戶個案（Client Cases）

在側邊欄選擇「🗂️ 客戶個案」頁面。

### 主要功能

**個案總覽**
- 查看所有個案清單與狀態

**從 Lead 建立個案**
- 從已有的 Lead 建立正式個案
- 自動填入基本資料

**個案詳情**
- 查看單一個案完整資訊
- 新增備註（case notes）

**待辦與交付**
- 新增待辦任務
- 記錄報告交付狀態

**匯出**
- 匯出單一個案：Markdown / HTML
- 匯出全部個案：CSV
- 匯出個案指標摘要：Markdown

---

## 匯出格式說明

| 格式 | 用途 |
|------|------|
| CSV | 整體個案清單、匯入試算表 |
| Markdown | 個案詳情文字版 |
| HTML | 個案詳情可列印版（不含外部 CDN） |

匯出檔案儲存於 `data/client_case_exports/`。

---

## 隱私提醒

- 所有客戶資料（leads、client cases）儲存於本機 `data/` 目錄
- 不串接外部 CRM
- 不串接 Email API
- 不上傳任何個案資料至外部伺服器
- 請定期備份 `data/` 目錄

---

## 常見問題

**Q: 顧問模式與客戶模式的差別？**  
A: 顧問模式額外提供 Lead Funnel 與客戶個案頁面，不顯示開發者校準工具。

**Q: 如何切換回客戶模式？**  
A: 關閉程式，改用 `run.bat` 啟動。

**Q: 可以在顧問模式看到紫微校準嗎？**  
A: 不行。紫微校準和人類圖校準屬於開發者工具，需使用 `run_dev.bat` 啟動才能存取。

**Q: 客戶資料存在哪裡？**  
A: `data/client_cases.json`（個案）、`data/leads_mock.json`（Lead）。

---

*版本：2.0.0 — Astro Destiny Analyzer*
