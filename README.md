# Astro Destiny Analyzer — 命盤整合分析系統

> **免責聲明**  
> 本系統為「自我探索與娛樂型命盤分析工具」，不構成科學定論、醫療診斷、投資建議或絕對命運預測。  
> 報告內容僅供使用者進行人格理解、情感觀察、職涯思考與生活規劃參考。

---

## V1.9.4 更新說明 — Human Design External Case Import & Calibration Report Export

### 外部案例匯入 / 校準資料集 / 批次比對 / 報告匯出

本版在「🔷 人類圖校準」頁新增四個 tab，支援外部案例管理、批次比對與多格式匯出。

**新增功能：**

| 功能 | 說明 |
|------|------|
| 外部案例匯入 | JSON 貼上 / .json 檔案上傳，解析後預覽並存入資料集 |
| 校準資料集 | 儲存至 `data/human_design_calibration_cases.json`，支援載入/追加/批次比對 |
| 批次比對 | 一鍵對資料集所有案例執行 reconciliation，輸出 BatchReconciliationSummary |
| Markdown 匯出 | 單案例報告 + 批次摘要 |
| HTML 匯出 | 無 JS / CDN，含 UTF-8 + footer，可直接開啟 |
| JSON 匯出 | 完整資料集 JSON（ensure_ascii=False） |

**新增模組：**
- `human_design_reconciliation/dataset.py` — 解析、儲存、載入、追加案例
- `human_design_reconciliation/exporters.py` — Markdown / HTML / JSON 匯出
- `human_design_reconciliation/models.py` — 3 新模型：`HumanDesignCalibrationCase`, `HumanDesignCalibrationDataset`, `BatchReconciliationSummary`

**資料集路徑：**`data/human_design_calibration_cases.json`（由 `config.HUMAN_DESIGN_CALIBRATION_DATASET_PATH` 控制）

**UI Tab 結構（人類圖校準頁）：**
1. 單案例比對（原有功能）
2. 外部案例匯入（新）
3. 多案例資料集（新）
4. 校準報告匯出（新）

**限制：**
- 所有功能僅 DEVELOPER_MODE 可用
- 本工具不自動修正核心演算法
- 差異需人工審核
- 不可為單一案例硬調 offset

**config.py：**`APP_VERSION = "1.9.4"`

---

## V1.9.3 更新說明 — Human Design Exact Design Date & Gate Wheel Calibration

### 人類圖精準設計日期 & Gate Wheel Offset 校準

本版升級人類圖引擎（`human_design/engine.py`），將設計日期計算從「出生時間 −88 天近似值」升級為**精準 88° 太陽弧回推**，並新增 Gate Wheel Offset 校準功能。

**新功能：**

| 功能 | 說明 |
|------|------|
| Exact Solar Arc Design Date | 以 Swiss Ephemeris 搜尋太陽黃經剛好回退 88° 的時刻 |
| Gate Wheel Offset | 可透過環境變數調整 I-Ching wheel 起點偏移量 |
| Calibration Diagnostics | 人類圖校準頁新增 offset 模擬表與 solar arc 誤差顯示 |
| Method Summary | 命盤頁人類圖 tab 顯示方法摘要（設計日期方法、offset、設計日期） |

**新增環境變數（config.py）：**

```
HUMAN_DESIGN_DESIGN_DATE_METHOD=solar_arc_88   # 預設：精準太陽弧
HUMAN_DESIGN_GATE_WHEEL_OFFSET_DEGREES=0.0     # 預設：無偏移
HUMAN_DESIGN_ENABLE_OFFSET_DEBUG=0             # 開發者模式自動啟用
```

**搜尋演算法（三階段）：**
1. Coarse：−100 至 −80 天，每 6 小時一步
2. Refine：最佳候選 ±12 小時，每 1 小時一步
3. Fine：最終 ±1 小時，每 10 分鐘一步
- 目標精度：≤0.1° solar arc 誤差

**新增模組：**
- `human_design/calibration.py` — `simulate_gate_offset_for_activations()` 模擬工具
- `human_design/engine.py` — `_calculate_design_datetime_solar_arc()`, `_angular_distance()`, `apply_gate_wheel_offset()`

**HumanDesignChart 新欄位：**
`design_date_method`, `design_date_fallback_used`, `design_solar_arc_target_longitude`,
`design_solar_arc_actual_longitude`, `design_solar_arc_error_degrees`,
`gate_wheel_offset_degrees`, `gate_wheel_version`, `calibration_notes`

**config.py：**`APP_VERSION = "1.9.3"`

---

## V1.9.2 更新說明 — Human Design External Chart Reconciliation

### 人類圖外部排盤校準工具

本版新增 `human_design_reconciliation/` 模組，提供開發者模式人類圖外部排盤比對工具。

**可比對欄位：**

| 欄位 | 說明 |
|------|------|
| Type | 類型（含中英文 normalize） |
| Strategy | 策略 |
| Authority | 內在權威（含中英文 normalize） |
| Profile | 人生角色（支援 4/6、4-6、4｜6 等格式） |
| Incarnation Cross | 輪迴交叉（標記方法差異，不強行比對） |
| Conscious Sun / Earth | 意識面太陽 / 地球 gate / line |
| Design Sun / Earth | 設計面太陽 / 地球 gate / line |
| Gates | 啟動閘門 set 比對 |
| Channels | 定義通道 set 比對（含雙向 normalize） |
| Centers | 定義中心 set 比對（含中英文 normalize） |

**使用方式：**

1. 開發者模式啟動（`run_dev.bat` 或 `set ASTRO_DEVELOPER_MODE=1`）
2. 計算命盤後前往「🔷 人類圖校準」頁
3. 從外部人類圖系統取得資料並填入 JSON 模板
4. 點擊「開始人類圖校準比對」

**重要說明：**

- 本工具不代表已完成外部校準
- 需使用者輸入真實外部資料（Jovian Archive / Genetic Matrix / MyBodyGraph）後才能比對
- 不直接聲稱完全一致；若發現差異，輸出差異原因與修正建議，不自動修改計算核心
- 客戶模式不顯示「人類圖校準」頁

**差異原因分析：**

- Gate 差異 → I-Ching wheel order、黃經 offset、timezone
- Design planets 差異 → 本機使用 88-day 近似；商業軟體使用精準 88° solar arc
- Centers/Authority 差異 → 通常由 gate/channel 差異造成
- Profile 差異 → 出生時間精確度、timezone

**下一步（V1.9.3 預告）：**
> 人類圖精準 Design Date：太陽回推 88° exact solar arc / Gate Wheel Offset 校準

**config.py：**`APP_VERSION = "1.9.2"`

---

## V1.9.1 更新說明 — Human Design 報告深化與外部校準說明

### 新增模組

- **`human_design/validation.py`** — `HDValidationStatus`、`build_validation_status()`、`render_validation_markdown()`
  - 涵蓋 Gate Table 狀態、Channel Table 狀態、Design Date 方法、Ephemeris 來源、校準建議
- **`human_design/visuals.py`** — `HDCenterVisual`、`HDVisualBundle`、`build_hd_visuals()`、`render_centers_markdown_table()`、`render_centers_html()`
  - 固定 9 中心顯示順序（頭部→根部），提供 Markdown 與 HTML 兩種輸出
- **`human_design/templates.py`** — 各 Type / Authority / Profile 深度敘事文本、`render_hd_full_narrative()`
  - 完整 12 節 Markdown HD 章節，整合 visuals 與 validation

### 報告整合

- `reports/templates.py` TEMPLATE_FULL：HD 章節改由 `render_hd_full_narrative()` 產生，包含更豐富的類型解讀、權威說明、中心視覺表格與校準章節
- `ui/streamlit_app.py` HD Tab：新增 Centers 視覺化總覽（使用 `build_hd_visuals()`）、準確度與外部校準說明 expander、DEVELOPER_MODE 增強 debug（含 validation_level / ephemeris_status）

### 新增測試

- `tests/test_human_design_validation.py` — 10 tests
- `tests/test_human_design_visuals.py` — 10 tests
- 更新 `test_human_design_report.py`、`test_human_design_ui.py`、`test_human_design_gates_channels.py`

**config.py：**`APP_VERSION = "1.9.1"`

---

## V1.9.0 更新說明 — Human Design Chart MVP

### 新增 Human Design 人類圖模組

本版新增 Human Design MVP，整合至現有系統，所有報告匯出與 UI 均支援。

**支援功能：**
- Type / Strategy（類型 / 策略）
- Authority（內在權威）
- Profile（人生角色）
- 9 大 Centers（已定義 / 開放）
- 36 Channels（通道判斷）
- 64 Gates（閘門啟動）
- Conscious Personality Planets（意識面行星）
- Design Planets（設計面行星）
- Incarnation Cross 初版（輪迴交叉）

**計算說明：**
- 使用 Swiss Ephemeris 計算行星黃經
- Design date = 出生時間 − 88 天（MVP 近似值，未來版本可改為精確太陽弧）
- Gate wheel 為 Phase 1 I-Ching 輪序表，建議以外部軟體校準

**⚠️ 限制與聲明：**
- 需要精確出生時間；出生時間不確定時 Type / Authority / Centers 可能出現偏差
- 人類圖分析定位為自我探索與決策模式參考，不代表絕對命運
- 不構成醫療、法律或投資建議
- Gate wheel Phase 1 需外部校準

**config.py：**`APP_VERSION = "1.9.0"`

---

## V1.8.4 更新說明 — Customer Delivery Mode & Branding Polish

### 客戶交付模式（Customer Delivery Mode）

客戶版預設啟用交付模式，以下內容在客戶版中自動隱藏：

- 紫微校準開發工具
- Demo / 範例資料
- 內部 debug 說明

| 環境變數 | 預設 | 說明 |
|---|---|---|
| `ASTRO_CUSTOMER_MODE` | `1`（啟用） | 客戶交付模式 |
| `ASTRO_DEVELOPER_MODE` | `0`（關閉） | 開發者工具模式 |
| `ASTRO_SHOW_DEMO_DATA` | `0`（隱藏） | 顯示範例資料 |
| `ASTRO_BRAND_NAME` | `Astro Destiny Analyzer` | 報告品牌名稱 |
| `ASTRO_BRAND_TAGLINE` | `Relationship & Destiny Insight Report` | 品牌標語 |
| `ASTRO_REPORT_WATERMARK` | `Generated by Astro Destiny Analyzer` | 報告浮水印 |

### 報告品牌 / 浮水印 / Footer

所有報告匯出（Markdown / HTML / Word）均包含：

- 封面品牌名稱（`BRAND_NAME`）與標語（`BRAND_TAGLINE`）
- Footer 浮水印：`{REPORT_WATERMARK} · v{APP_VERSION}`
- 免責聲明

### 匯出檔名格式

合盤報告匯出格式：

```
relationship_report_{A方姓名}_{B方姓名}_{YYYYMMDD}.html
```

- 不含 emoji、不含非法字元、空白轉底線

### 建議交付流程

1. 執行 `setup.bat` 安裝環境
2. 執行 `run.bat` 啟動（客戶模式）
3. 客戶輸入個人資料
4. 計算命盤 → 預覽報告
5. 匯出 HTML（最穩定）或 Word（可編修）
6. PDF 為選用功能，執行 `install_pdf_support.bat` 安裝

---

## V1.8.3 更新說明

### 開發者模式（客戶版預設隱藏紫微校準）

客戶版預設不顯示「🧭 紫微校準」頁面。開發者可透過以下方式啟用：

**Windows CMD：**
```bat
set ASTRO_DEVELOPER_MODE=1
run_dev.bat
```

**PowerShell：**
```powershell
$env:ASTRO_DEVELOPER_MODE="1"
.\run_dev.bat
```

或直接雙擊 `run_dev.bat`（已內建 `ASTRO_DEVELOPER_MODE=1`）。

### 一鍵安裝與啟動

| 腳本 | 用途 |
|---|---|
| `setup.bat` | 一鍵建立 `.venv` 並安裝所有必要套件 |
| `run.bat` | 一鍵啟動（客戶版，不含紫微校準） |
| `run_dev.bat` | 開發者模式啟動（含紫微校準） |
| `install_pdf_support.bat` | 安裝 PDF 匯出支援（WeasyPrint，選用） |

### Word 匯出

`python-docx` 為必要依賴，已包含於 `requirements.txt`。
執行 `setup.bat` 後 Word 匯出應自動可用，無需額外安裝。

### PDF 匯出（選用）

PDF 匯出需要 WeasyPrint，**不**包含於預設依賴中：

```bat
install_pdf_support.bat
```

或手動安裝：

```bash
pip install weasyprint
```

> **Windows 注意：** WeasyPrint 在 Windows 上可能需要 GTK / Pango 系統依賴。  
> 建議交付時優先使用 **HTML**（最穩定）或 **Word**（可編修），PDF 留給有完整環境的使用者。

### 推薦匯出格式

| 格式 | 推薦場景 |
|---|---|
| HTML | 最穩定，跨平台，無需額外套件 |
| Word | 可人工調整排版，適合交付客戶 |
| PDF | 需 WeasyPrint + GTK/Pango，適合有完整環境者 |

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

### V1.8.2 — Relationship Report Visual Charts (2026-05-28)

- 新增 `compatibility/visuals.py`：圖表資料模型 + build/render 函式
- 新增視覺資料模型：`RadarChartData`, `AspectCategoryBarData`, `AspectBalanceData`, `CompositeDistributionData`, `RelationshipVisualBundle`
- `CompatibilityReport` 新增 `visuals: Optional[RelationshipVisualBundle]`
- `CompatibilityEngine.generate()` 自動 build visuals（失敗時 fallback 不 crash）
- Markdown 報告新增「合盤視覺化總覽」章節：雷達圖表格、和諧/張力比例、相位分類統計、Composite 元素/模式分布
- HTML export 包含視覺資料表（純 HTML table + CSS bar，無 JS / CDN，離線可用）
- Word export 不 crash（視覺資料已在 markdown 中，文字版本）
- Streamlit UI 新增 3 個視覺 tab：「視覺總覽」/ 「相位分類圖」/ 「Composite 分布圖」
  - 視覺總覽：st.bar_chart 雷達替代方案 + 7 項分數 metric
  - 相位分類圖：分類 bar_chart + 和諧/張力比例
  - Composite 分布圖：元素/模式 bar_chart + 行星星座展開表
- 不依賴外部 JS / CDN / plotly / matplotlib
- 限制說明：視覺圖表是互動模式的輔助觀察，不是適合度的絕對評分

### V1.8.1 — Relationship Report UI Polish & UTF-8 Encoding Fix (2026-05-28)

- Windows 中文編碼修正：run.bat / setup.bat 加入 `chcp 65001`, `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, `PYTHONLEGACYWINDOWSSTDIO=0`
- 新增 `scripts/encoding_utils.py`：`ensure_utf8_console()` — 安全 reconfigure stdout/stderr 為 UTF-8
- 相位矩陣 UI 全面升級：中文欄位名稱、分類篩選 multiselect、最強 / 張力 / 和諧 checkbox、Top cards（最強 / 最強吸引力 / 最強情緒 / 最強張力）
- 新增顯示 helper：`aspect_type_zh`, `category_zh`, `aspect_nature`, `format_orb`, `aspect_to_display_dict`
- 進階合盤分數 UI 分區：分數總覽（`border=True` container）、優勢、挑戰、修復建議
- 衝突強度加 caption：「衝突張力高不等於不適合，而是代表需要明確修復流程。」
- Label 說明：5 種 label 對應詳細中文描述
- Composite Chart UI 升級：核心行星卡片（太陽 / 月亮 / 金星 / 火星 / 土星 + 角色說明）、完整行星展開表格
- ASC/MC 說明：精確時間不足時顯示「Composite ASC / MC 需要雙方精準出生時間與出生地，本次未納入四軸解讀。」
- 報告 Synastry 章節：加入 Synastry 概念說明、Top 8 改為 Markdown 表格、使用中文相位 / 分類名稱
- 報告 Composite 章節：加入共同場域說明、核心行星加 role 標籤
- 進階分數章節：加入「不是絕對適合度」免責聲明、表格新增說明欄
- HTML export 確認包含 `<meta charset="UTF-8">`
- 限制說明：
  - Synastry / Composite 不是絕對適合度，也不代表一定在一起或分開
  - Composite ASC / MC 需要雙方精準時間與地點

### V1.8.0 — Advanced Synastry & Composite Chart (2026-05-28)

- 新增進階西洋合盤：Synastry 相位矩陣（6 種主要相位 × 10 行星）
- 新增 Composite Chart 中點盤 Phase 1（跨 0° 處理、太陽 / 月亮 / 金星 / 火星 / 土星解讀）
- 新增進階合盤分數：情緒連結、溝通流暢度、吸引力、穩定潛力、成長張力、衝突強度、長期潛力
- UI 新增「進階西洋合盤」/ 「相位矩陣」/ 「Composite 中點盤」三個 tab
- 合盤報告新增 Synastry 相位矩陣、Composite Chart、進階分數章節
- 缺行星經度時 fallback 不 crash
- 限制說明：
  - Composite ASC/MC 需雙方精確出生時間與地點
  - 分數是互動模式參考，不是絕對適合度
  - Synastry / Composite 是關係理解工具，不是婚姻保證

### V1.7.7 — Zi Wei Multi-Case Regression & Accuracy Guardrails (2026-05-28)

- 新增多案例回歸測試（5 種場景：Rossi golden / 不同時辰 / 不同年份 / 不同性別 / 未知時辰）
- 防止 overfit Rossi：驗證命宮、主星、命主、身主、天馬、分數在多案例均合理
- 新增紫微準確度護欄說明（不同流派、閏月、廟旺陷表可能差異）
- 未知時辰 fallback：確認 partial_lunar_only 不誤標為 formal_layout_phase1
- 未知性別 fallback：確認大限方向標示 unknown
- UI / 報告加入流派差異提示

### V1.7.6 — Zi Wei Score Calibration & Explanation Polish (2026-05-28)

- 紫微盤面結構支援度校準（Phase 1 calibrated v1）
- 分數從過度膨脹（98）修正為保守解讀（max 92，Rossi 案例 78–86 區間）
- 分數名稱從「盤面強度」明確改為「盤面結構支援度」
- 強調不等同外部網站好運指數，不是命運好壞分數
- 高分（>=85）自動附加責任承載提醒
- 新增 ziwei_score_components / ziwei_score_version / ziwei_score_warnings 欄位
- Reconciliation score 項目文字更新為「盤面結構支援度」
- V1.7.4 / V1.7.5 校準成果（十二宮、主星、命主、身主、天馬、廟旺陷）保留

### V1.7.5 — Zi Wei Missing Features: Ming Zhu / Shen Zhu / Brightness (2026-05-28)
- 新增命主（先天人格輔助星）依命宮地支計算
- 新增身主（後天行動重心輔助星）依年支計算
- 新增天馬依年支三合局安星
- 新增廟旺陷 Phase 1 表（14主星 × 12地支）
- 新增紫微盤面強度分數 Phase 1（0–100）
- 盤面強度分數不等同外部網站好運指數
- Reconciliation not_implemented 從 5 降至 0

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
Version: v1.5.5
Date: 2026-05-27
Status: Zi Wei Auxiliary Stars & Da Xian Phase 1
```

---

## 20. V1.6.3 更新說明 — Release Package & Demo Assets

### 20.1 本版重點

| 項目 | 說明 |
|------|------|
| Demo 資產生成 | `python scripts/generate_demo_assets.py` — 自動為所有 Demo Profile 生成 MD / HTML / DOCX / PDF |
| Release 打包 | `python scripts/build_release.py` — 建立乾淨發佈包（含 RELEASE_INFO.txt，可選 zip） |
| 產品文件 | `docs/QUICK_START.md`、`docs/DEMO_GUIDE.md`、`docs/RELEASE_CHECKLIST.md`、`docs/PRODUCT_OVERVIEW.md` |
| .gitignore 補充 | `demo_outputs/`、`release/`、`*.zip`、`*.rar` 排除提交 |

### 20.2 生成 Demo 報告

```bash
python scripts/generate_demo_assets.py
```

輸出至 `demo_outputs/`（不含個人資料，不寫入 DB）：

```
demo_outputs/
├── Demo_台北精準時間.md
├── Demo_台北精準時間.html
├── Demo_新竹科技職涯.md
├── Demo_新竹科技職涯.html
├── Demo_未知出生時間.md
└── Demo_未知出生時間.html
```

### 20.3 建立 Release 包

```bash
python scripts/build_release.py
```

輸出至 `release/astro_destiny_analyzer_vX.X.X/`，自動排除：
- `.venv/`、`.git/`、`__pycache__/`
- `data/*.db`、`exports/`、`release/`、`demo_outputs/`

並生成 `RELEASE_INFO.txt`（版本、時間、Python 版本、功能列表、啟動說明）。

> **注意**：`demo_outputs/` 和 `release/` 不提交 Git（已加入 `.gitignore`）。

### 20.4 文件索引

| 文件 | 用途 |
|------|------|
| `docs/QUICK_START.md` | 一般使用者快速上手 |
| `docs/DEMO_GUIDE.md` | 展示 / 錄影 / 對外 Demo 腳本 |
| `docs/RELEASE_CHECKLIST.md` | 發佈前完整檢查清單 |
| `docs/PRODUCT_OVERVIEW.md` | 產品介紹與差異化說明 |

### 20.5 新增 / 修改檔案

| 檔案 | 說明 |
|------|------|
| `scripts/generate_demo_assets.py` | 新增：Demo 報告批次生成 |
| `scripts/build_release.py` | 新增：Release 打包工具 |
| `docs/QUICK_START.md` | 新增 |
| `docs/DEMO_GUIDE.md` | 新增 |
| `docs/RELEASE_CHECKLIST.md` | 新增 |
| `docs/PRODUCT_OVERVIEW.md` | 新增 |
| `release/.gitkeep` | 新增：保留 release 目錄結構 |
| `.gitignore` | 補充 demo_outputs/、release/、*.zip、*.rar |
| `config.py` | 版本 1.6.3 |
| `tests/test_release_assets.py` | 新增：40+ 項測試 |

---

## 19. V1.6.2 更新說明 — Windows 一鍵啟動

### 19.1 Windows 一鍵啟動

#### 第一次使用

雙擊 `setup.bat`，自動完成：
1. 檢查 Python 版本
2. 建立虛擬環境 `.venv`
3. 安裝所有依賴套件（`requirements.txt`）
4. 執行環境檢查（`scripts/check_env.py`）

#### 日常使用

雙擊 `run.bat`，自動：
1. 確認 Python / `.venv` 存在
2. 更新依賴套件
3. 執行環境檢查
4. 啟動 Streamlit（http://localhost:8501）

#### 不需要手動執行

```
# 不需要這些步驟：
.venv\Scripts\activate
streamlit run ui\streamlit_app.py
```

#### 手動啟動（備用）

```bat
.venv\Scripts\python -m streamlit run ui\streamlit_app.py
```

#### PowerShell Execution Policy 問題

`run.bat` 不使用 `activate.ps1`，因此不受 PowerShell 執行政策影響。
無需修改系統 `ExecutionPolicy`。

### 19.2 環境檢查（check_env.py）

```
python scripts\check_env.py
```

輸出範例：
```
[OK]   Python 3.11.5
[OK]   streamlit
[OK]   pydantic
[OK]   jinja2
[OK]   markdown
[OK]   python-docx
[OK]   lunardate
[OK]   swisseph
[WARN] weasyprint not installed; PDF export disabled
[OK]   data directory
[OK]   exports directory
[OK]   DB path writable
```

Exit code 0 = 通過（weasyprint 缺失為警告，不算失敗）
Exit code 1 = 有必備套件缺失

### 19.3 常見錯誤排除

| 錯誤 | 解決方法 |
|------|----------|
| 找不到 Python | 安裝 Python 3.10+，並確認已加入 PATH |
| pip install 失敗 | 確認網路正常；可改用 `pip install -r requirements.txt -i https://pypi.org/simple` |
| streamlit 找不到 | 執行 `setup.bat` 重新安裝依賴 |
| PDF 不可用 | 安裝 WeasyPrint：`pip install weasyprint`（Windows 需額外依賴） |
| 瀏覽器沒有自動開啟 | 手動開啟 http://localhost:8501 |

### 19.4 新增 / 修改檔案

| 檔案 | 說明 |
|------|------|
| `run.bat` | 新增：5 步驟一鍵啟動腳本 |
| `setup.bat` | 新增：首次安裝腳本 |
| `scripts/__init__.py` | 新增：scripts 套件 |
| `scripts/check_env.py` | 新增：環境檢查工具 |
| `config.py` | 版本 1.6.2 |
| `tests/test_launcher_scripts.py` | 新增：launcher 測試 |

---

## 18. V1.6.1 更新說明 — UX QA & Sample Report Pack

### 18.1 3 分鐘快速體驗

不需要手動輸入資料，直接使用內建 Demo：

1. 啟動應用程式（`streamlit run ui/streamlit_app.py`）
2. 首頁點選「**💼 Demo 新竹科技職涯**」
3. 跳轉到「🔮 計算命盤」，點「**開始計算命盤**」
4. 前往「**📄 報告預覽**」閱讀完整分析
5. 前往「**📤 匯出**」下載 HTML 報告

### 18.2 Demo 資料說明

| 範例 | 出生日期 | 時間 | 特點 |
|------|----------|------|------|
| Demo 台北精準時間 | 1990-02-05 | 12:30 | 完整精確計算（ASC / MC / 紫微命宮） |
| Demo 新竹科技職涯 | 1989-09-21 | 11:05 | 萬字完整版，事業 / 財富主題 |
| Demo 未知出生時間 | 1995-06-15 | 未知 | 測試不完整資料路徑（部分計算） |

### 18.3 推薦展示流程

```
首頁 → 點 Demo → 計算命盤 → 報告預覽 → 匯出 HTML
```

### 18.4 如何切換成自己的資料

1. 點選左側「**📝 輸入資料**」
2. 填寫真實出生資料（姓名、日期、時間、城市）
3. 點「確認資料」後前往「計算命盤」

### 18.5 常見問題

**Q: 為什麼上升星座（ASC）和天頂（MC）顯示「需補充資料」？**  
A: 精確計算 ASC / MC 需要「精確出生時間」加「出生地經緯度」兩者同時具備。
缺少任一者，西洋占星引擎仍會計算行星位置，但上升與天頂無法確定。

**Q: 為什麼 PDF 下載按鈕顯示「未安裝」？**  
A: PDF 匯出依賴 WeasyPrint，屬於選用套件。
執行 `pip install weasyprint`（Windows 可能需要額外系統依賴）。
建議優先使用 HTML 或 Word 格式交付。

**Q: 為什麼紫微斗數標示「Phase 1」？**  
A: V1.6 的紫微排盤已完成命宮 / 身宮 / 十四主星 / 四化 / 輔星 / 煞星 / 大限骨架。
尚未加入的功能：大限四化、流年飛化、小限、流月。這些列為 V1.7+ 計畫。

**Q: 為什麼八字節氣是「近似」？**  
A: 節氣時刻精確到年份，但依所在地略有差異。目前使用台灣中午 12:00 作為當日節氣基準。
若出生時間恰在節氣當日，建議在設定頁確認計算模式說明。

### 18.6 新增 / 修改檔案

| 檔案 | 說明 |
|------|------|
| `demo/__init__.py` | 新增：demo 套件 |
| `demo/sample_profiles.py` | 新增：3 組 Demo BirthProfile（台北 / 新竹 / 台中未知時間） |
| `ui/streamlit_app.py` | 首頁快速體驗、報告預覽 Demo 標籤、匯出頁格式說明 |
| `config.py` | 版本 1.6.1 |
| `tests/test_sample_profiles.py` | 新增：Demo 資料測試（結構 / 產生報告 / 匯出） |
| `README.md` | 新增 Section 18（Quick Start / FAQ） |

---

## 17. V1.6.0 更新說明 — 報告產品化整理 & 匯出強化

### 17.1 本版重點

| 項目 | 說明 |
|------|------|
| 報告封面 | 所有匯出格式均包含封面（姓名、日期、地點、版本、產生時間） |
| 免責聲明統一 | 統一免責聲明文字，出現在封面後與報告結尾 |
| 基本資料頁 | 姓名、性別、血型、分析主題、報告長度 |
| 計算模式摘要 | 西洋 / 八字 / 紫微各系統 calculation_mode 與 accuracy_note 一覽 |
| 一頁式總覽 | 太陽 / 月亮 / 上升 / MC、八字日主 / 喜用神、命宮 / 身宮、生命靈數、血型 |
| 目錄 | Markdown 標題模擬目錄；HTML 含清楚目錄區塊 |
| HTML 美化 | max-width 960px、Microsoft JhengHei + Noto Sans TC 字型、封面區塊、免責聲明區塊、計算模式卡片、@media print 列印最佳化 |
| Word 排版 | 封面標題、免責聲明、基本資料表、計算模式表、CJK 字型安全設定 |
| PDF 安全策略 | WeasyPrint 可用時 HTML → PDF；不可用時 is_available() 回傳 False，不 crash |
| 安全檔名 | sanitize_filename() 移除 Windows 非法字元、保留中文、最長 80 字元 |
| 匯出檔名格式 | {name}_命盤整合分析報告_{YYYYMMDD_HHMM}.{ext} |
| 匯出頁 UX | 報告摘要卡、每格式 caption 說明、不可用時清楚提示 |
| 報告預覽 UX | 頂部摘要卡（姓名 / 長度 / 版本 / 時間）、計算模式 expander |
| 設定頁 | 版本、支援功能清單、匯出格式可用性、資料庫路徑與報告數 |

### 17.2 推薦交付格式

| 格式 | 用途 |
|------|------|
| HTML | 最穩，適合瀏覽與列印，單一檔案自含 CSS |
| Word | 適合客戶交付與人工排版 |
| Markdown | 適合二次編輯與版本控制 |
| PDF | 等 WeasyPrint 環境設定完成後使用（Windows 需額外依賴） |

### 17.3 PDF 安裝說明

WeasyPrint 為選用套件，不列入 requirements.txt：

```bash
pip install weasyprint
```

Windows 安裝 WeasyPrint 可能需要額外系統依賴（GTK / Pango / libpango）。
V1.6 建議優先使用 HTML / Word 交付，待環境就緒後再啟用 PDF。

### 17.4 新增 / 修改檔案

| 檔案 | 說明 |
|------|------|
| `reports/utils.py` | 新增：sanitize_filename、make_export_filename、build_report_meta、DISCLAIMER |
| `reports/markdown_exporter.py` | 加入封面、免責聲明、計算模式摘要、目錄 |
| `reports/html_exporter.py` | 全面美化 CSS、封面 / 免責聲明 / 計算模式卡片 / TOC / 列印樣式 |
| `reports/docx_exporter.py` | 封面表格、免責聲明、基本資料表、計算模式表、CJK 字型 |
| `reports/pdf_exporter.py` | WeasyPrint 路徑實作；安全 fallback（RuntimeError，不 crash） |
| `reports/generator.py` | 新增 to_docx()、to_pdf() 方法 |
| `ui/streamlit_app.py` | 匯出頁 / 報告預覽頁 / 設定頁全面優化 |
| `config.py` | 版本 1.6.0 |
| `tests/test_report_export_product.py` | 新增：66 項測試（sanitize、meta、MD、HTML、DOCX、PDF） |

---

## 16. V1.5.5 更新說明 — 紫微輔星 / 煞星 / 大限 Phase 1

### 16.1 新增輔星（六吉星 + 祿存）

| 星曜 | 安置規則 | 類別 |
|---|---|---|
| 左輔 | 辰宮起正月，順數至生月 | 吉輔 |
| 右弼 | 戌宮起正月，逆數至生月 | 吉輔 |
| 文昌 | 依出生時辰（戌宮逆數） | 吉輔 |
| 文曲 | 依出生時辰（辰宮順數） | 吉輔 |
| 天魁 | 依出生年天干（常見表法） | 吉輔 |
| 天鉞 | 依出生年天干（常見表法） | 吉輔 |
| 祿存 | 依出生年天干 | 吉輔 |

### 16.2 新增六煞星 Phase 1

| 星曜 | 安置規則 | 類別 |
|---|---|---|
| 擎羊 | 祿存+1 宮 | 煞曜 |
| 陀羅 | 祿存-1 宮 | 煞曜 |
| 火星 | 依年支三合局 + 時辰 | 煞曜 |
| 鈴星 | 依年支三合局 + 時辰 | 煞曜 |
| 地空 | 依時辰（亥宮逆數） | 煞曜 |
| 地劫 | 依時辰（亥宮順數） | 煞曜 |

> 文昌、文曲、火星、鈴星、地空、地劫需出生時辰；未填出生時辰時略過。
> 輔星煞星採 Phase 1 常見表法，流派差異後續版本可配置。

### 16.3 大限 10 年運限骨架

**方向規則**（V1.5.5 Phase 1）：

| 條件 | 大限方向 |
|---|---|
| 陽年（甲丙戊庚壬）+ 男 | 順行 |
| 陽年 + 女 | 逆行 |
| 陰年（乙丁己辛癸）+ 男 | 逆行 |
| 陰年 + 女 | 順行 |
| 性別未填 | 方向 unknown，保守以順行計算 |

**大限起始歲數**：依五行局數（水二=2歲、木三=3歲、金四=4歲、土五=5歲、火六=6歲）

**每大限 10 年**，共 12 個大限，涵蓋整個人生週期。

### 16.4 V1.5.5 資料模型新增欄位

`ZiWeiChart` 新增：
- `auxiliary_star_map: Dict[str, str]` — 吉輔星 → 所在地支
- `malefic_star_map: Dict[str, str]` — 煞曜 → 所在地支
- `star_categories: Dict[str, str]` — 星曜 → "auspicious" / "malefic"
- `da_xian: List[DaXianPeriod]` — 12 個大限資料
- `da_xian_direction: str` — "forward" / "backward" / "unknown"
- `da_xian_start_age: int` — 第一大限起始歲數
- `da_xian_accuracy: str` — "phase1"
- `auxiliary_accuracy_note: str` — 輔星精度說明

新增 `DaXianPeriod` 模型：
- `start_age / end_age / palace_name / branch / main_stars / auxiliary_stars / interpretation`

### 16.5 V1.5.5 限制聲明

- **大限四化 / 宮干四化**：尚未實作
- **流年 / 流月 / 流日**：尚未實作
- **廟旺陷強弱**：尚未實作
- **輔星安星流派差異**：採 Phase 1 常見表法，後續版本可配置
- **閏月精準處理**：採保守處理

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

---

## 20. V1.7.0 — 合盤分析功能（Compatibility / Relationship Analysis）

### 20.1 新功能

新增雙人關係分析模組，支援以下關係類型：

| 關係類型 | 說明 |
|----------|------|
| 情侶 / 伴侶 | 感情吸引、情緒共鳴、長期潛力 |
| 婚姻 | 穩定性、夫妻宮互動 |
| 合作夥伴 | 官祿宮、財帛宮、協作效能 |
| 親子 | 父母宮、子女宮、溝通模式 |
| 朋友 | 交友宮、互動風格 |
| 同事 | 官祿宮、溝通與分工 |
| 一般關係 | 通用互動分析 |

### 20.2 合盤分析包含

- 西洋占星互動：太陽、月亮、水星、金星火星、上升配對，含主要星象相位
- 八字五行互補：日主關係、喜用神互補、忌神放大
- 紫微宮位互動：命宮主星、身宮、關係類型重點宮位、主星共鳴、大限背景
- 生命靈數：生命靈數配對、共鳴主題、挑戰主題
- 血型：互動風格、衝突模式、建議
- 關係總分（7 維度）：情感、溝通、吸引力、穩定、成長、衝突強度、協作
- 30 天關係練習

### 20.3 架構

新增 `compatibility/` 模組：

```
compatibility/
  __init__.py
  models.py      # 資料模型（RelationshipType, CompatibilityInput, CompatibilityReport 等）
  engine.py      # CompatibilityEngine.generate()
  report.py      # render_compatibility_report()
  templates.py   # build_compatibility_markdown()
  exporters.py   # HTML / DOCX 匯出，make_compat_filename()
```

### 20.4 Demo 範例

`demo/sample_profiles.py` 新增 `SAMPLE_COUPLES`：
- Demo 情侶合盤：新竹科技職涯 × 高雄創意
- Demo 合作夥伴合盤：台北策略 × 台中執行

### 20.5 UI

Streamlit 左側新增「💕 合盤分析」頁面，支援：
- 手動輸入 A / B 方資料
- 載入目前命盤作為 A 方
- Demo 情侶 / 合作夥伴快速體驗
- 合盤結果分 tabs 顯示
- Markdown / HTML / Word 匯出

### 20.6 V1.7.0 不包含的功能（Phase 1 限制）

- 完整 Composite Chart / Davison Chart / 中點盤
- 精準 Synastry 全相位矩陣
- 紫微雙盤飛化
- 八字完整合婚神煞
- 流年合盤、婚期選日
- 合盤歷史記錄（SQLite）

---

## 21. V1.7.1 — 合盤報告敘事校準 & Demo Couples 優化

### 21.1 本版重點

| 項目 | 說明 |
|------|------|
| 分數解讀聲明 | 報告正文與 UI 頂部加入「分數不是絕對適合度」說明 |
| 關係定位總論 | 依 relationship_type 提供不同語氣的核心提問、避免模式與最佳實踐 |
| 高張力高成長 | 衝突分數高 + 成長分數高時，自動標示「高張力高成長型」並說明意義 |
| 舒適但需避免停滯 | 衝突低 + 成長低時，提醒加入共同目標 |
| 情緒互動章節 | 月亮配對說明、誰需要被安撫、如何修復情緒斷線 |
| 溝通模式章節 | 水星配對說明、溝通速度與直接度觀察表 |
| 吸引力 / 合作動能 | 依 relationship_type 調整詮釋重點 |
| 衝突修復七步驟 | 具體行為步驟（暫停、命名情緒、回到事實、說明需求、約定下一步、不翻舊帳、不用沉默懲罰） |
| 30 天關係練習（4 週） | Week 1 觀察觸發點、Week 2 建立規則、Week 3 共同決策、Week 4 回顧調整 |
| 安全界線提醒 | 新增「關係紅旗與安全界線」章節，提醒在真實傷害情境下尋求專業協助 |
| Demo Couples 強化 | 每組 Demo 新增 description / talking_points，新增第三組親子 Demo |
| UI 優化 | 10 分頁結果展示、衝突分數 caption、dynamic_label、Demo 展示點後顯示說明 |
| 匯出檔名 | 加入 relationship_type：`{A}_x_{B}_{rel}_合盤分析報告_{ts}.{ext}` |

### 21.2 分數解讀聲明

> 分數不是絕對適合度，而是互動模式的可觀察指標。
> 高分代表自然共鳴較多；中等分代表需要溝通設計；
> 衝突分數高不等於不好，而是代表關係張力與成長課題較強。

### 21.3 內建 Demo Couples

| Demo | 說明 |
|------|------|
| 情侶合盤：高張力高成長型 | 情緒安全感、吸引力、衝突修復、長期磨合 |
| 合作夥伴：策略 × 執行互補型 | 決策分工、財務風險、合作節奏 |
| 親子關係：支持與界線型 | 期待落差、支持與控制的界線、成長節奏 |

若需手動測試其他關係類型（朋友、同事、一般關係），可在「選擇關係類型」下拉選單手動切換後輸入資料。

### 21.4 V1.7.1 不包含的功能

V1.7.1 不做完整 Synastry / Composite / 紫微雙盤飛化，
所有合盤演算法保持 V1.7.0 Phase 1 骨架，本版僅強化報告敘事與 Demo 展示體驗。

## 22. V1.7.3 — 紫微外部排盤校準（Zi Wei External Chart Reconciliation）

### 22.1 功能概述

V1.7.3 新增「🧭 紫微校準」頁面，讓使用者可以將外部網站或人工排盤的紫微結果輸入進來，
系統自動與本機 ZiWeiChart 逐項比對，產出一致 / 差異 / 流派差異說明報告。

### 22.2 可比對項目

| 比對類別 | 說明 |
|----------|------|
| 五行局 | 正規化後比對（如「爐中火六局」= 「火六局」） |
| 命宮地支 | 命宮起算點比對 |
| 身宮地支 | 身宮比對 |
| 農曆日期 | 農曆換算結果比對 |
| 十二宮地支 | 各宮位地支逐一比對 |
| 十四主星 | 各宮位主星比對（順序不影響） |
| 四化（化祿/權/科/忌） | 生年四化比對 |
| 輔星 / 六煞 | 擎羊、陀羅、火鈴、地空地劫等 |
| 大限起始歲數 | 大限 Phase 1 比對 |
| 命主 / 身主 | 標記為尚未實作 |
| 好運指數 | 標記為尚未實作（非標準紫微欄位） |
| 廟旺陷 | 標記為尚未實作 |

### 22.3 差異狀態說明

| 狀態 | 說明 |
|------|------|
| 一致 | 本機與外部結果相同 |
| 不一致 | 有差異，附嚴重度（低/中/高） |
| 可能流派差異 | 部分相同，差異可能源自不同安星流派 |
| 本機缺少 | 外部有此欄位，本機未計算 |
| 尚未實作 | 好運指數、廟旺陷、命主身主等屬外部網站自家功能 |

### 22.4 使用流程

1. 先在「📝 輸入資料」填寫資料並計算命盤。
2. 進入左側「🧭 紫微校準」頁面。
3. 選擇「使用內建 Rossi 截圖範例」或「手動 JSON 輸入」。
4. 按「🔍 開始紫微校準比對」。
5. 查看分頁結果（總覽 / 一致項 / 差異項 / 流派差異 / 尚未實作 / Markdown 報告）。
6. 可下載 Markdown 報告。

### 22.5 重要說明

- 目前不做 OCR 解析截圖，需手動輸入外部盤 JSON 或使用內建範例。
- 不同網站可能採不同安星流派，差異不一定代表本機排盤錯誤。
- 好運指數通常是網站自家權重模型，不是標準紫微必備欄位。
- 若命宮、五行局、大限起始一致，基礎排盤大致符合。

### 22.6 新增模組

| 模組 | 說明 |
|------|------|
| `ziwei_reconciliation/models.py` | 外部盤資料模型、比對結果模型 |
| `ziwei_reconciliation/engine.py` | 比對引擎（ZiWeiReconciliationEngine） |
| `ziwei_reconciliation/templates.py` | Markdown 報告模板 |
| `ziwei_reconciliation/examples.py` | 內建範例（Rossi 截圖）與空白 JSON 模板 |
| `tests/test_ziwei_reconciliation.py` | 35 項測試 |

### 22.7 V1.7.3 不包含的功能

- OCR 解析截圖
- 自動爬外部網站
- 完整流派切換
- 完整廟旺陷演算法
- 好運指數正式演算法
- 流年 / 流月 / 飛化深化


---

## Developer Notes

以下內容僅供開發者參考，不適用於客戶交付文件。

### 測試案例說明

本系統包含多個以 "Rossi" 命名的內部測試案例（golden case），用於紫微斗數精準度驗證：

- V1.7.7 多案例回歸測試包含 "Rossi golden case"（台北精準出生時間參考盤）
- 此測試用於防止紫微演算法 overfit 至單一案例
- 相關測試位於 `tests/test_ziwei_multi_case_regression.py`（已整合於 V1.7.7 之後的版本）

### 開發者模式啟動

```bat
run_dev.bat
```

或手動設定：
```bat
set ASTRO_DEVELOPER_MODE=1
set ASTRO_CUSTOMER_MODE=0
set ASTRO_SHOW_DEMO_DATA=1
```

### Demo 資料

`demo/sample_profiles.py` 包含內部測試用範例資料，客戶版預設不顯示。
使用 `run_dev.bat` 或設定 `ASTRO_SHOW_DEMO_DATA=1` 可啟用。
