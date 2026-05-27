# Astro Destiny Analyzer — 命盤整合分析系統

> **免責聲明**  
> 本系統為「自我探索與娛樂型命盤分析工具」，不構成科學定論、醫療診斷、投資建議或絕對命運預測。  
> 報告內容僅供使用者進行人格理解、情感觀察、職涯思考與生活規劃參考。

---

## 1. 專案簡介

Astro Destiny Analyzer 是一套結合多種命理與人格敘事系統的整合分析工具。

目前 V1 MVP 已完成：

- 西洋占星資料結構與 Mock 計算層
- 八字四柱、六十甲子、五行、十神、大運、流年基礎邏輯
- 紫微斗數十二宮、十四主星、四化資料結構
- 血型分析
- 生命靈數與大師數
- Synthesis Engine 跨系統整合分析
- Jinja2 長篇報告模板
- Markdown / HTML / Word 匯出
- SQLite 本機資料儲存
- Streamlit Web UI
- Pytest 測試

---

## 2. 功能一覽

| 模組 | 狀態 | 說明 |
|---|---|---|
| 西洋占星 | V1 Mock | 行星、宮位、相位、上升、天頂等結構已完成，預留 Swiss Ephemeris 替換點 |
| 八字命理 | V1.4 節氣精準 | 年柱以立春切年、月柱以節令切月、四柱、五行、十神、大運、流年 |
| 紫微斗數 | V1.5 Phase 1 | 農曆轉換、命宮/身宮、五行局、十四主星、生年四化正式排盤 |
| 血型分析 | 已實作 | 人際、感情、壓力、職場、財富輔助分析 |
| 生命靈數 | 已實作 | 生命靈數、生日數、天賦數、個人年運，大師數 11 / 22 / 33 保留 |
| 整合分析 | 已實作 | 跨系統矛盾偵測與整合建議 |
| 報告系統 | 已實作 | 簡短版、標準版、萬字完整版 |
| 資料儲存 | 已實作 | SQLite 儲存出生資料、命盤結果與報告歷史 |
| Web UI | 已實作 | Streamlit 七頁式互動介面 |
| 匯出 | 部分完成 | Markdown、HTML、Word 可用；PDF 介面保留 |

---

## 3. 環境需求

- Python 3.10+
- Windows / macOS / Linux
- 建議使用虛擬環境 `.venv`

---

## 4. 安裝與啟動

### 4.1 進入專案資料夾

```bash
cd astro_destiny_analyzer
```

或使用你目前的實際路徑：

```powershell
cd C:\Users\Rossi\Documents\Claude\fate
```

### 4.2 建立虛擬環境

```bash
python -m venv .venv
```

### 4.3 啟動虛擬環境

macOS / Linux：

```bash
source .venv/bin/activate
```

Windows CMD：

```cmd
.venv\Scripts\activate.bat
```

Windows PowerShell（若 Execution Policy 未限制）：

```powershell
.venv\Scripts\activate
```

> **PowerShell Execution Policy 問題**  
> 若出現「因為這個系統上已停用指令碼執行，所以無法載入 Activate.ps1」，  
> **不需要修改系統 Execution Policy**，改用第 4.4 節的直接路徑方式即可。

### 4.4 安裝依賴套件

activate 成功後：

```bash
pip install -r requirements.txt
```

**PowerShell / 未 activate 時**，改用完整路徑：

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
```

### 4.5 啟動應用程式

activate 成功後，任選一種方式：

```bash
streamlit run ui/streamlit_app.py
```

```bash
python app.py
```

**PowerShell / 未 activate 時**（推薦，不需要 activate）：

```powershell
.venv\Scripts\python -m streamlit run ui\streamlit_app.py
```

啟動後，瀏覽器會開啟：

```text
http://localhost:8501
```

---

## 5. 使用流程

### 5.1 輸入資料

在「輸入資料」頁面填寫：

- 姓名或暱稱
- 出生日期
- 出生時間
- 出生城市 / 國家
- 血型
- 分析主題
- 報告語言
- 報告長度

### 5.2 計算命盤

在「計算命盤」頁面點擊開始計算。

系統會依序產生：

- 西洋占星資料
- 八字命盤
- 紫微斗數結構
- 血型分析
- 生命靈數
- 跨系統整合分析

### 5.3 閱讀報告

在「報告預覽」頁面可查看：

- 核心人格摘要
- 東西方交叉驗證
- 感情與親密關係
- 事業與職涯方向
- 財富與風險模式
- 內在矛盾與建議
- 行動清單

### 5.4 匯出報告

在「匯出」頁面可下載：

- Markdown `.md`
- HTML `.html`
- Word `.docx`

PDF 目前保留介面，正式排版建議於後續版本完成。

### 5.5 歷史報告

在「歷史報告」頁面可載入或刪除過去產生的報告。

---

## 6. 資料格式

### BirthProfile

| 欄位 | 型別 | 說明 |
|---|---|---|
| name | str | 姓名或暱稱 |
| gender | Gender | male / female / other / unknown |
| birth_date | date | 出生日期，格式 YYYY-MM-DD |
| birth_time | time | 出生時間，格式 HH:MM，可為 None |
| birth_city | str | 出生城市 |
| birth_country | str | 出生國家 |
| blood_type | BloodType | A / B / O / AB / Unknown |
| themes | list[AnalysisTheme] | 分析主題清單 |
| report_language | ReportLanguage | 繁體中文 / 簡體中文 / English |
| report_length | ReportLength | 簡短版 / 標準版 / 萬字完整版 |

---

## 7. 報告匯出格式

| 格式 | 狀態 | 說明 |
|---|---|---|
| Markdown `.md` | 可用 | 純文字格式，適合 Git、AI 二次整理與人工編輯 |
| HTML `.html` | 可用 | 含樣式的單一網頁，可用瀏覽器開啟與列印 |
| Word `.docx` | 可用 | 適合交付客戶或人工排版 |
| PDF `.pdf` | 保留介面 | 需安裝 WeasyPrint 與 CJK 字型，建議後續版本再正式啟用 |

---

## 8. 執行測試

執行全部測試：

```bash
python -m pytest tests -v
```

單獨測試：

```bash
python -m pytest tests/test_numerology.py -v
python -m pytest tests/test_blood_type.py -v
python -m pytest tests/test_report_generator.py -v
python -m pytest tests/test_synthesis.py -v
```

編譯檢查：

```bash
python -m compileall .
```

目前測試狀態：

```text
128 passed, 13 skipped (pyswisseph-dependent)
```

---

## 9. 專案結構

```text
astro_destiny_analyzer/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── data/
│   └── astro_destiny.db
├── core/
│   ├── models.py
│   ├── database.py
│   └── validators.py
├── engines/
│   ├── western_astrology.py
│   ├── bazi.py
│   ├── ziwei.py
│   ├── blood_type.py
│   ├── numerology.py
│   └── synthesis.py
├── reports/
│   ├── templates.py
│   ├── generator.py
│   ├── markdown_exporter.py
│   ├── html_exporter.py
│   ├── pdf_exporter.py
│   └── docx_exporter.py
├── ui/
│   ├── streamlit_app.py
│   └── components.py
└── tests/
    ├── test_numerology.py
    ├── test_blood_type.py
    ├── test_report_generator.py
    └── test_synthesis.py
```

---

## 10. SQLite 資料庫

預設資料庫位置：

```text
data/astro_destiny.db
```

注意：

- SQLite 會在首次啟動時自動建立
- 不建議將本機資料庫提交到 Git
- 建議在 `.gitignore` 中排除：

```gitignore
data/*.db
data/*.sqlite
data/*.sqlite3
```

---

## 11. Mock Engine 與正式演算法替換方向

### 11.1 西洋占星

V1.3 起已導入 Swiss Ephemeris（`pyswisseph`），主要行星（太陽、月亮、水星、金星、火星、木星、土星、天王星、海王星、冥王星）使用真實黃經計算星座。

V1.3.5 新增出生地經緯度支援：

#### 上升（ASC）與天頂（MC）精確計算條件

精確計算上升與天頂，**三個條件必須同時具備**：

| 條件 | 說明 |
|---|---|
| 出生時間 | 必須已知精確時分 |
| 出生地緯度 | birth_latitude（南緯為負） |
| 出生地經度 | birth_longitude（西經為負） |

若缺少任何一項：
- 系統仍可精確計算主要行星星座
- ASC / MC 欄位標示為 `ascendant_accuracy = "unknown"`
- UI 顯示「─ 需補充資料」，**不會用假值冒充精準上升**
- `accuracy_note` 說明缺少什麼資料

`calculation_mode` 三種模式：

| 模式 | 說明 |
|---|---|
| `swiss_ephemeris` | 行星 + ASC/MC 均為精確計算 |
| `partial_real` | 行星精確；ASC/MC 需補充時間或地點 |
| `mock_fallback` | pyswisseph 不可用，使用 Mock 層 |

#### 台灣城市自動對應

輸入資料頁提供台灣主要城市下拉選單，選擇後自動帶入內建經緯度與時區（UTC+8）。  
非台灣城市可在「進階：手動輸入經緯度」展開欄中補填。

後續：

- 加入夏令時間自動判斷
- 支援 Whole Sign 等宮位制切換（HOUSE_SYSTEM 常數已預留）
- 加入全球主要城市對應資料庫

### 11.2 八字

#### V1.4 節氣精準化（已完成）

V1.4 起，年柱與月柱改以節氣為分界：

| 規則 | 說明 |
|---|---|
| 年柱 | 以**立春**（約 2/4）為八字換年分界，不再用西曆 1/1 |
| 月柱 | 以 12 個**節令**切月：立春→寅、驚蟄→卯、清明→辰、立夏→巳、芒種→午、小暑→未、立秋→申、白露→酉、寒露→戌、立冬→亥、大雪→子、小寒→丑 |
| 日柱 | 維持現有六十甲子演算法，保持穩定 |
| 時柱 | 依日干起時干；出生時間未知則標示為不可視為精準 |

V1.4 使用**近似節氣日期**（`calculation_mode = "solar_term_approx"`）：

```text
計算模式：solar_term_approx
年界規則：lichun（立春 ~Feb 4）
月界規則：solar_terms（12 節令近似日）
accuracy_note：V1.4 使用節氣近似日期切年切月；若需專業級精準，後續版本將導入天文節氣精確時刻。
```

出生時間未知時：
- 時柱欄位保留為 None
- `birth_time_accuracy = "unknown"`
- `accuracy_note` 附加說明「時柱需精確出生時間，當前不可視為精準」

#### V1.4.5 日柱 / 時柱精準化（已完成）

**時辰地支切分**（`_get_hour_branch(hour, minute)`）：

| 時辰 | 時段 |
|---|---|
| 子 | 23:00–00:59 |
| 丑 | 01:00–02:59 |
| 寅 | 03:00–04:59 |
| 卯 | 05:00–06:59 |
| 辰 | 07:00–08:59 |
| 巳 | 09:00–10:59 |
| 午 | 11:00–12:59 |
| 未 | 13:00–14:59 |
| 申 | 15:00–16:59 |
| 酉 | 17:00–18:59 |
| 戌 | 19:00–20:59 |
| 亥 | 21:00–22:59 |

**時干依日干推算**（`_hour_stem(day_stem, hour_branch)`）：

| 日干 | 子時起 |
|---|---|
| 甲、己 | 甲 |
| 乙、庚 | 丙 |
| 丙、辛 | 戊 |
| 丁、壬 | 庚 |
| 戊、癸 | 壬 |

**子時 Policy**（`ZI_HOUR_POLICY`，設定於 `config.py`）：

| 模式 | 說明 |
|---|---|
| `late_zi_same_day`（預設）| 23:00–23:59 仍視為當天日柱；00:00–00:59 亦同當天 |
| `late_zi_next_day` | 23:00–23:59 視為隔日日柱（部分命理派別） |

注意：子時 policy 僅影響日柱與時柱。年柱 / 月柱仍依原始出生日期 + 節氣規則計算，不受影響。

出生時間未知：
- `birth_time_accuracy = "unknown"`
- `hour_pillar_is_precise = False`
- `accuracy_note` 說明「時柱需精確出生時間，當前不可視為精準」

後續：

- 導入 pyswisseph 太陽黃經計算精準節氣時刻（升級為 `solar_term_precise`）
- 精準起運歲數（大運與節氣差計算）
- 加入流月、流日

### 11.3 紫微斗數

#### V1.5 Phase 1 正式排盤（已完成）

| 功能 | 說明 |
|---|---|
| 農曆轉換 | 使用 `lunardate` 套件；lunardate 不可用時 fallback 到 mock |
| 命宮 | 從寅宮起正月，順數至農曆月，逆數至出生時辰 |
| 身宮 | 從寅宮起正月，順數至農曆月，順數至出生時辰 |
| 五行局 | 依命宮天干地支納音決定：水二/木三/金四/土五/火六局 |
| 十四主星 | 紫微系（紫微、天機、太陽、武曲、天同、廉貞）+ 天府系（天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍） |
| 生年四化 | 依出生年天干安化祿/化權/化科/化忌 |

`calculation_mode` 三種模式：

| 模式 | 說明 |
|---|---|
| `formal_layout_phase1` | 農曆成功 + 出生時間已知 → 完整第一階段排盤 |
| `partial_lunar_only` | 農曆成功但出生時間未知 → 命宮/身宮不精準 |
| `mock_fallback` | lunardate 不可用或轉換失敗 |

限制（後續版本）：
- 輔星與煞星尚未安置
- 閏月採保守處理
- 大限、流年、流月尚未實作
- 宮干四化尚未實作（目前僅生年四化）
- 流派差異（廟旺陷、星曜細節）後續版本處理

---

## 12. 建議開發 Roadmap

```text
V1.0：MVP 骨架完成
V1.2：升級 Synthesis Engine 敘事深度與正向轉化規則
V1.3：導入 Swiss Ephemeris 真實星曆計算（行星星座）
V1.3.5：出生地經緯度支援與 ASC/MC 精準計算
V1.4：八字節氣與大運精準化
V1.5：紫微斗數正式安星
V1.6：圖表視覺化與 PDF / Word 排版強化
V1.7：感情合盤與合作夥伴合盤
```

---

## 13. Git Commit Message

```text
feat: add astro destiny analyzer MVP

- add Streamlit-based birth profile input workflow
- add western astrology, BaZi, Zi Wei, blood type, and numerology engine interfaces
- add synthesis engine for integrated personality and life-theme analysis
- add markdown/html report generator with long-form report template
- add SQLite persistence for birth profiles and generated reports
- add basic tests for deterministic helper engines
- add README with setup, usage, validation, and export workflow
```

---

## 14. 版本資訊

```text
Version: v1.5.1
Date: 2026-05-27
Status: Zi Wei UI & Report Interpretation Polish
```

---

## 15. V1.5.1 更新說明 — 紫微 UI 與報告敘事校準

### 15.1 紫微分頁 UI 優化

| 新增區塊 | 說明 |
|---|---|
| 排盤狀態卡片 | 顯示 calculation_mode（正式 / 部分 / fallback）與 accuracy_note |
| 基本盤資訊卡片 | 農曆生日、出生時辰、命宮地支、身宮地支、五行局、生年天干 |
| 命宮 / 身宮解讀 | 命宮主星逐星解讀、身宮說明 |
| 十二宮表格 | 新增 `render_ziwei_formal_table()`，欄位：宮位 / 地支 / 主星 / 四化 / 解讀摘要 |
| 十四主星總覽 | expander 列出 14 顆主星各自所在宮位與四化 |
| 生年四化總覽 | expander 列出化祿 / 化權 / 化科 / 化忌星曜，區分主星與輔星四化 |

### 15.2 紫微報告敘事強化

完整版報告（萬字完整版）紫微章節新增：

1. 排盤狀態說明（formal_layout_phase1 / partial_lunar_only / mock_fallback）
2. 命宮解讀（主星意義、人格主軸）
3. 身宮解讀（後天行動重心、中年後方向）
4. 官祿宮解讀（事業格局）
5. 財帛宮解讀（財富模式）
6. 夫妻宮解讀（感情模式）
7. 福德宮解讀（精神世界 / 內在修復）
8. 生年四化詳細解讀（化祿 / 化權 / 化科 / 化忌 各自段落）
9. 版本限制聲明（輔星 / 大限 / 流年尚未完成）

### 15.3 interpretation helpers 新增

`engines/ziwei.py` 新增：

| 函數 | 說明 |
|---|---|
| `_interpret_main_star(star)` | 回傳 14 主星的命理顧問式解讀文字 |
| `_interpret_palace(palace_name, stars, transformations)` | 組合宮位 + 主星 + 四化的完整解讀段落 |
| `_build_ziwei_summary(chart)` | 產出命盤摘要字串，供 Synthesis Engine 引用 |

### 15.4 Synthesis Engine 銜接

`engines/synthesis.py` 小幅新增：

- 若 `ziwei.calculation_mode == "formal_layout_phase1"`，在核心人格段落補充正式排盤說明。
- 若 `mock_fallback`，保持保守語氣。
- 事業分析段落標注紫微官祿宮是否為正式盤資料。

### 15.5 V1.5.1 不包含的功能

- 輔星、煞星安置
- 大限、流年、流月
- 宮干四化
- 廟旺陷流派細節

以上功能待後續版本實作。
