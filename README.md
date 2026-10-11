# 臺灣高級中等學校校級面板資料（103–114 學年度）

**tw-highschool-panel** 整合教育部統計處公開的高級中等學校校別、科別、縣市概況與學校名錄資料，建立一份**可以跨年追蹤同一所學校**的校×學年度面板，並附完整的資料處理程式與品質驗證。

> 版本 2026.10.1｜原始資料快照日期 2026-10-11｜涵蓋 103–114 學年度（學校名錄至 115 學年度）

**English summary.** A school-by-year panel of all senior high schools in Taiwan for academic years 2014–2025 (ROC 103–114), built from open data published by the Ministry of Education. It harmonises school codes across years (including code changes when national schools were transferred to municipal governments), derives public/private status, parses township from school addresses, and aggregates programme structure (academic, vocational, comprehensive). Every processing rule and the 43 validation checks are published with the code. Data are aggregated at the school level; there is no student-level information. Tables are in UTF-8 CSV with Chinese labels; field definitions are in [docs/codebook.md](docs/codebook.md).

## 這份資料解決了什麼問題

官方原始檔可以直接下載，但要拿來做跨年分析，會遇到幾個不容易察覺的問題。本資料集已逐一處理並驗證：

| 問題 | 若不處理 | 本資料集的處理 |
|---|---|---|
| 113 學年度起官方校碼加上前導零（`10301` → `010301`） | 240 校在 112→113 學年度間「消失又出現」 | 校碼統一補零為 6 碼 |
| 國立高中改隸直轄市時校碼改變（106 臺中 15 校、107 桃園 8 校） | 同一學校被當成兩校 | 新增跨年識別碼 `school_id`，23 組串連都以名錄地址交叉比對 |
| 臺中、臺南、高雄因 2010 年合併各有兩組縣市代碼 | 以縣市代碼分組會變成 25 區 | 提供現行 22 縣市名稱 |
| 原始檔沒有公私立欄位 | 從校名推導會誤判（如「新北市裕德高級中等學校」是私立） | 由校碼推導，並與名錄官方欄位核對：5,115 校年**全部一致** |
| 科別資料含附設國中部 | 和校別資料加總對不上 | 分開計算；排除國中部後，學生數和班級數 6,297 校年**全部一致** |
| 原始檔沒有鄉鎮市區 | 無法做縣市以下的分析 | 由名錄地址解析（97.9% 校年有值），並統一升格後的名稱（員林市、頭份市） |

## 資料表

| 檔案 | 內容 | 列數 |
|---|---|---:|
| [`data/processed/hs_school_year.csv`](data/processed/hs_school_year.csv) | 校×學年度面板：師資、班級、學生、學程結構、設立別、鄉鎮市區 | 6,297 |
| [`data/processed/hs_program_year.csv`](data/processed/hs_program_year.csv) | 校×學年度×科別明細 | 45,837 |
| [`data/processed/hs_school_directory.csv`](data/processed/hs_school_directory.csv) | 學校名錄（103–115），含郵遞區號與鄉鎮市區 | 6,667 |
| [`data/processed/school_id_crosswalk.csv`](data/processed/school_id_crosswalk.csv) | 改碼學校對照表 | 23 |

每個欄位的定義、缺失數與範例見 **[docs/codebook.md](docs/codebook.md)**；機器可讀的 schema 見 [`datapackage.json`](datapackage.json)（[Frictionless Data](https://frictionlessdata.io/) 格式）。

### 快速開始

```python
import pandas as pd

panel = pd.read_csv("data/processed/hs_school_year.csv", dtype={"school_id": str, "school_code": str})
# 跨年追蹤同一所學校請用 school_id；以縣市分組請用 county_name
```

```r
library(readr)
panel <- read_csv("data/processed/hs_school_year.csv", col_types = cols(school_id = "c", school_code = "c"))
```

## 資料品質

`src/validate.py` 執行 43 項檢查，結果見 **[docs/data_quality_report.md](docs/data_quality_report.md)**。重點如下：

- 校別資料依縣市加總後，22 縣市 × 11 學年度的學生數、班級數、專任教師數，和官方「縣市概況」（31454）**完全一致**。
- 科別資料（排除附設國中部）加總，和校別資料的學生數、班級數**完全一致**。
- 校碼推導的公私立，和名錄官方欄位**完全一致**。
- 目前沒有 FAIL。WARN 項目的說明見下方「已知限制」。

## 已知限制

- **學校層級的彙總資料**：沒有個別學生資料，不能用來推論學生個人的表現或行為。
- **沒有學習成果指標**：例如升學率、會考或學測成績，都不在這份資料中。
- **`school_id` 是依規則串連的**：規則見 codebook。23 組都以程式比對名錄地址，其中 21 組地址完全相同，1 組只有寫法不同（沙鹿高工），1 組因名錄未收錄而無法比對（臺中啟明學校）。其他形式的改制，例如兩校合併、一校分設，或校碼和校名同時改變且後 3 碼不同，不在串連範圍內。
- **鄉鎮市區缺漏**：矯正學校、部分進修學校與特殊教育學校不在一般名錄中，共 130 校年沒有鄉鎮市區。
- **名錄原始資料的小問題**：115 學年度名錄有 1 列備註欄含未加引號的換行，讀取時已接回原列，原始檔未修改。宜寧高中 106 學年度起的地址郵遞區號（402）和區名（西屯區）不一致，鄉鎮市區以地址文字為準。
- **公私立校數與縣市概況不同**：校別資料每縣市比縣市概況多 0–3 校，推測縣市概況不另計分校或附設部。學生數、班級數、教師數則完全一致。
- **統計口徑**：學生數含延修生、不含附設國中部；教師數分專任與兼任，縣市概況的「教師數」等於專任教師數。
- **地址為名錄當年資料**：學校遷址會反映在不同學年度的名錄中。

## 適合與不適合的用途

**適合**：學校規模與師資配置的分布和趨勢、少子化下的學校規模變化、公私立或縣市之間的比較、學程結構（普通、技職、綜合）的變遷、鄉鎮層級的學校分布。

**使用時請留意**：

- **師生比不等於教學品質**：它只反映人力配置，不代表教學成效或學生表現。
- **避免生態謬誤**：縣市或鄉鎮層級的關聯，不能直接推論到個別學校；學校層級的關聯，也不能推論到個別學生。
- **關聯不是因果**：這是觀察性的行政資料，例如「學校規模和師生比有關」不代表改變規模就會改變師生比。
- **跨年分析請用 `school_id`**，以縣市分組請用 `county_name`；需要可比較的樣本時，可以用 `continuing_school`、`special_education_school`、`sector` 排除性質特殊的學校。

## 重現與更新

需要 [uv](https://docs.astral.sh/uv/)。

```bash
uv sync                               # 依 uv.lock 建立相同環境（Python 3.12）
uv run python src/acquire.py          # 下載缺少的原始檔（已存在的檔案保留為快照）
uv run python src/build.py            # 建立 data/processed/ 的四張資料表
uv run python src/validate.py         # 資料品質檢查；有 FAIL 時結束碼為 1
uv run python src/docs.py             # 產生 codebook 與 datapackage.json
```

官方每學年度更新一次。建立新快照時執行 `uv run python src/acquire.py --refresh`，再跑完上面的流程，然後更新 `CHANGELOG.md` 與版本號。

處理規則都放在設定檔：[`config/sources.yml`](config/sources.yml)（來源）、[`config/build.yml`](config/build.yml)（處理規則）、[`config/schema.yml`](config/schema.yml)（欄位定義）。

## 資料來源

所有原始資料皆由**教育部統計處**提供，依《[政府資料開放授權條款—第 1 版](https://data.gov.tw/license)》釋出：

| 資料集 | 頁面 | 用途 |
|---|---|---|
| 高級中等學校校別資料（含進修部（學校）） | <https://data.gov.tw/dataset/6238> | 面板主體 |
| 高級中等學校科別資料 | <https://data.gov.tw/dataset/9617> | 科別明細、學程結構 |
| 高級中等學校概況—按學校所在縣市別分 | <https://data.gov.tw/dataset/31454> | 只用於核對 |
| 一般高級中等學校名錄 | <https://data.gov.tw/dataset/6089> | 地址、鄉鎮市區、官方公私立 |
| 大專附設高級中等進修學校名錄 | <https://data.gov.tw/dataset/24393> | 地址 |

原始檔快照與 SHA-256 列於 [`data/raw/MANIFEST.csv`](data/raw/MANIFEST.csv)。

## 授權與引用

- **衍生資料表**（`data/processed/`、`docs/`）：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **原始資料**（`data/raw/`）：政府資料開放授權條款—第 1 版
- **程式碼**（`src/`、`config/`）：[MIT](LICENSE)

使用時請同時標示原始資料來源與本資料集，詳見 [LICENSE-DATA.md](LICENSE-DATA.md)。

**建議引用格式：**

> Chuang, C.-C. (2026). *tw-highschool-panel：臺灣高級中等學校校級面板資料（103–114 學年度）* (Version 2026.10.1) [Data set]. https://github.com/gemini960114/tw-highschool-panel

> 原始資料：教育部統計處（2026）。高級中等學校校別資料、科別資料、縣市概況與學校名錄。政府資料開放平臺。https://data.gov.tw/

機器可讀的引用資訊見 [CITATION.cff](CITATION.cff)；GitHub 頁面右側的「Cite this repository」也可以直接產生 APA 或 BibTeX 格式。

## 維護者與問題回報

- 維護者：Chao-Chun Chuang（[@gemini960114](https://github.com/gemini960114)）
- 發現資料錯誤、對處理規則有疑問，或想建議新增資料，歡迎開 [Issue](https://github.com/gemini960114/tw-highschool-panel/issues)。回報資料錯誤時，請附上學年度與學校代碼。

本資料集的整理工作使用了 AI 程式助理（Claude）協助撰寫程式與文件。處理規則和驗證結果都公開在 `config/` 與 `docs/`，可以逐項核對。
