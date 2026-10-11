# 資料品質報告

> 由 `src/validate.py` 自動產生，請勿手動修改。產生時間（UTC）：2026-10-11T06:34:24+00:00

**結果：** INFO 5、PASS 35、WARN 3

PASS＝通過；WARN＝需留意但不影響使用；INFO＝描述性資訊；FAIL＝資料有誤（發布前必須為 0）。

## 檢查項目

| group | check | status | value |
|---|---|---|---|
| 來源 | MANIFEST 列出的原始檔都存在且非空 | PASS | 17 個檔案 |
| 結構 | hs_school_year：欄位與 schema 完全一致（名稱與順序） | PASS |  |
| 結構 | hs_school_year：主鍵 ['academic_year', 'school_id'] 唯一 | PASS | 重複 0 |
| 結構 | hs_program_year：欄位與 schema 完全一致（名稱與順序） | PASS |  |
| 結構 | hs_program_year：主鍵 ['academic_year', 'school_code', 'level_code', 'day_night_code', 'group_code', 'dept_code'] 唯一 | PASS | 重複 0 |
| 結構 | hs_school_directory：欄位與 schema 完全一致（名稱與順序） | PASS |  |
| 結構 | hs_school_directory：主鍵 ['academic_year', 'directory_type', 'school_code'] 唯一 | PASS | 重複 0 |
| 結構 | school_id_crosswalk：欄位與 schema 完全一致（名稱與順序） | PASS |  |
| 結構 | school_id_crosswalk：主鍵 ['old_code'] 唯一 | PASS | 重複 0 |
| 完整性 | 面板列數 = base0 原始列數 | PASS | 6297 / 6297 |
| 完整性 | 學年度連續無缺 | PASS | 103–114 |
| 完整性 | (學年度, school_code) 唯一 | PASS |  |
| 完整性 | 人數欄位無缺失 | PASS | 0 |
| 完整性 | 人數欄位無負值 | PASS |  |
| 完整性 | 校碼皆為 6 碼 | PASS |  |
| 代碼 | 每個縣市代碼只對應一個縣市名稱 | PASS | 25 個代碼／22 個縣市 |
| 代碼 | 一縣市多代碼僅限 2010 年合併的已知舊代碼 | PASS | {'臺中市': ['06', '19'], '臺南市': ['11', '21'], '高雄市': ['12', '50']} |
| 代碼 | 縣市名稱集合與縣市概況（31454）相同 | PASS |  |
| 代碼 | sector 無法判定（unknown）的列 | PASS | 0 |
| 交叉核對 | 校碼推導的公私立 = 名錄官方公私立欄位 | PASS | 一致 5118/5118 校年（104–114） |
| 串連 | 改碼串連組數 = 23 | PASS | 23 |
| 串連 | 校碼數 − 串連數 = school_id 數 | PASS | 575 − 23 = 552 |
| 串連 | 串連前後名錄地址完全相同 | WARN | 21/23 |
| 串連 | 同一 school_id 的公私立跨年不變 | PASS | 0 |
| 串連 | 串連後單一學年度新增學校 ≤ 10（偵測未串連的改碼） | PASS | {104: 7, 105: 1, 106: 5, 107: 2, 108: 7, 109: 2, 110: 3, 111: 1, 112: 0, 113: 3, 114: 3} |
| 串連 | 沒有中途缺年又出現的學校 | PASS |  |
| 串連 | 全期每年都有資料的學校 | INFO | 491/552 校 |
| 交叉核對 | 科別資料加總學生數（不含附設國中部）= 校別學生數 | PASS | 一致 6297/6297 |
| 交叉核對 | 科別資料加總班級數（不含附設國中部）= 校別班級數 | PASS | 一致 6297/6297 |
| 交叉核對 | 各學程學生數（普通、專業群科、綜合、實用技能、進修部）加總 = 學生總數 | PASS | 一致 6297/6297 |
| 交叉核對 | 科別資料的校碼都在校別資料中 | PASS |  |
| 交叉核對 | 校別資料中沒有科別資料的校年 | INFO | 1 列（學生數皆為 0：True） |
| 交叉核對 | 縣市×學年度配對數 = 22 × 11 | PASS | 242 |
| 交叉核對 | 縣市×學年度學生數與縣市概況完全一致 | PASS | 不一致 0/242 |
| 交叉核對 | 縣市×學年度班級數與縣市概況完全一致 | PASS | 不一致 0/242 |
| 交叉核對 | 縣市×學年度專任教師數與縣市概況完全一致 | PASS | 不一致 0/242 |
| 名錄 | 讀取時修補的欄位內換行（原始檔未修改） | INFO | directory_115.csv：1 列 |
| 名錄 | 一般名錄的學年度欄 = 檔名學年度 | PASS |  |
| 名錄 | 地址解析出鄉鎮市區的比例 | WARN | 99.93% |
| 名錄 | 同一縣市＋郵遞區號只對應一個鄉鎮市區 | WARN | {'嘉義市600': 2, '新竹市300': 3, '臺中市402': 2} |
| 名錄 | 地址中的縣市 = 名錄縣市欄位 | PASS | 不一致 0： |
| 位置 | 面板有鄉鎮市區的校年比例 | INFO | 97.94%（同年度名錄 97.14%，其他年度補值 0.79%） |
| 位置 | 面板缺鄉鎮市區的校年 | INFO | 130 列；其中進修學校 62、學生數為 0 3 |

## 原始檔快照

| file | source_id | downloaded_at_utc | bytes | sha256 |
|---|---|---|---|---|
| school_stats_base0.csv | school_stats | 2026-10-11T06:23:37+00:00 | 491976 | 72b050da31f55342d5f5e3ab0c00e0449dadf836120592f1bbbef5859bfb9d20 |
| program_stats_base2.csv | program_stats | 2026-10-11T06:23:38+00:00 | 6503868 | 08f3c315851c9012c13bb0a54f0ee5d5d64a81ef336d57cf1dad537f26e61ae3 |
| county_summary_edu_B_4_2.csv | county_summary | 2026-10-11T06:23:38+00:00 | 15527 | 2ebef174d6c298a482448c16908846c2b0587565637c45b75306e1092d607a9e |
| directory_103.csv | directory | 2026-10-11T06:23:38+00:00 | 63081 | 811953c6125bac5603b8a8468419fbd724d4f879f3e7332c088291d256398f4d |
| directory_104.csv | directory | 2026-10-11T06:23:38+00:00 | 63313 | a59279b3a93815115e748b3f67f33725bc8581c216be88b94340b4dadbd6be7c |
| directory_105.csv | directory | 2026-10-11T06:23:38+00:00 | 70933 | 6447c144b18bbbec140f5be3179138fd6611f34b5bfb9d9e87e74b5de4cf397e |
| directory_106.csv | directory | 2026-10-11T06:23:38+00:00 | 70120 | c48f96e2bed21f205b6bebf0d30bf00084a801b393a638634343d3707122dd39 |
| directory_107.csv | directory | 2026-10-11T06:23:39+00:00 | 71199 | e7f97d7d3431f176ba90ddf450139f8ed8771d79de7b39e807bfdf25ee419547 |
| directory_108.csv | directory | 2026-10-11T06:23:39+00:00 | 70229 | 90f298ef2ae96df9d15a9d66727d3b0be3092b6afd809d26902329c9bb9ffcd4 |
| directory_109.csv | directory | 2026-10-11T06:23:39+00:00 | 70627 | 0b25d650edcdd7fbf05bead41243b49baf58f0c59f0648db596a83226fcf0676 |
| directory_110.csv | directory | 2026-10-11T06:23:39+00:00 | 70805 | 663797116e7da5be74d5776d4693af89dea8dad896c2ae9e27622bdeeca66d03 |
| directory_111.csv | directory | 2026-10-11T06:23:39+00:00 | 70506 | 638892921b54a4e6109d544b8c5f1ccf8de4043d4816ddcc84f7de11e53b3893 |
| directory_112.csv | directory | 2026-10-11T06:23:40+00:00 | 70425 | 101b3a2f0c28219d01c59b0b4b60d737ed5a87370f2f0e6d564c23f1f900bbed |
| directory_113.csv | directory | 2026-10-11T06:23:40+00:00 | 70342 | 2995939a574edccd54d52b640bd3f789099f27ec8153f32688171d5fd41ebaad |
| directory_114.csv | directory | 2026-10-11T06:23:40+00:00 | 70021 | 05af287c1125b85d06f54744475b19a7700f79509c1f7767c4931645b4eff4be |
| directory_115.csv | directory | 2026-10-11T06:23:40+00:00 | 70257 | 826979ec988a0a941c6a71d3570c3b7efe16fea7b03e7a9dcb2ea8090eba7ca1 |
| directory_continuing_115.csv | directory_continuing | 2026-10-11T06:23:40+00:00 | 4171 | 99ac1881ed55b84144619b732e72a20b700db991e3ebd15cdd1d91993ff7f366 |
