# 欄位字典（Codebook）

> 由 `src/docs.py` 依 `config/schema.yml` 與實際資料自動產生，請勿手動修改。資料版本：2026.10.1

所有 CSV 皆為 UTF-8（含 BOM，方便以 Excel 開啟），空白儲存格表示缺失。學年度為民國紀年。

## `hs_school_year.csv` — 高級中等學校校×學年度面板

每列為一所學校在一個學年度的師資、班級與學生統計（103–114 學年度，統計基準日為每學年度 9 月底）。 人數欄位直接取自教育部「高級中等學校校別資料」；學程結構欄位由「科別資料」彙整；鄉鎮市區取自學校名錄地址。

- 列數：6,297
- 主鍵：`academic_year`, `school_id`

| 欄位 | 型別 | 說明 | 缺失數 | 範例 |
|---|---|---|---:|---|
| `academic_year` | integer | 學年度（民國）。 | 0 | 103 |
| `school_id` | string | 跨年學校識別碼。等於該校最早出現的校碼；改碼學校（見 school_id_crosswalk）共用同一個 school_id。跨年追蹤學校請用此欄。 | 0 | 010301 |
| `school_code` | string | 該學年度的教育部學校代碼，已補零為 6 碼。 | 0 | 010301 |
| `school_name` | string | 該學年度的學校名稱。 | 0 | 國立華僑中學 |
| `county_code` | string | 縣市代碼（補零為 2 碼）。注意臺中市、臺南市、高雄市因 2010 年縣市合併各有兩組代碼；以縣市分組時請用 county_name。 | 0 | 01 |
| `county_name` | string | 縣市名稱（現行 22 縣市；103 學年度的「桃園縣」已統一為「桃園市」）。 | 0 | 新北市 |
| `township` | string | 鄉鎮市區，由學校名錄地址解析。名錄未收錄時取同一 school_id 最接近學年度的名錄。 | 130 | 板橋區 |
| `postal_code` | string | 郵遞區號，取自學校名錄地址。 | 131 | 220 |
| `location_source_year` | integer | township／postal_code 取自哪一個學年度的名錄；與 academic_year 相同表示同年度資料。空白表示名錄未收錄。 | 130 | 103.0 |
| `sector_code_digit` | string | 校碼第 3 碼（推導 sector 的依據）。 | 0 | 0 |
| `sector` | string | 設立別，由校碼第 3 碼推導：public_national（國立）、public_local（直轄市及縣市立）、private（私立）、correctional（矯正學校）。已與名錄官方公私立欄位核對（見資料品質報告）。 | 0 | public_national |
| `sector_official` | string | 同學年度學校名錄的官方「公立／私立」欄位；105 學年度起才有，名錄未收錄的學校為空白。 | 1,179 | 公立 |
| `continuing_school` | boolean | 校名含「進修」或「進校」（進修學校、附設進修部學校、進校分校）。 | 0 | False |
| `special_education_school` | boolean | 校名含「啟明」「啟聰」「啟智」「特殊學校」「特殊教育」。 | 0 | False |
| `no_enrolled_students` | boolean | 學生總數為 0（多為停招或退場中的學校）。 | 0 | False |
| `ft_teacher_m` | integer | 專任教師數（男）。 | 0 | 46 |
| `ft_teacher_f` | integer | 專任教師數（女）。 | 0 | 97 |
| `pt_teacher_m` | integer | 兼任教師數（男）。 | 0 | 4 |
| `pt_teacher_f` | integer | 兼任教師數（女）。 | 0 | 8 |
| `staff_m` | integer | 職員數（男）。 | 0 | 7 |
| `staff_f` | integer | 職員數（女）。 | 0 | 22 |
| `classes` | integer | 班級數（不含附設國中部）。 | 0 | 48 |
| `student_m` | integer | 學生數（男；含延修生，不含附設國中部）。 | 0 | 804 |
| `student_f` | integer | 學生數（女；含延修生，不含附設國中部）。 | 0 | 892 |
| `prev_grad_m` | integer | 上學年度畢業生數（男）。注意：屬於前一學年度。 | 0 | 232 |
| `prev_grad_f` | integer | 上學年度畢業生數（女）。注意：屬於前一學年度。 | 0 | 272 |
| `student_total` | integer | student_m + student_f。 | 0 | 1696 |
| `ft_teacher_total` | integer | ft_teacher_m + ft_teacher_f。 | 0 | 143 |
| `pt_teacher_total` | integer | pt_teacher_m + pt_teacher_f。 | 0 | 12 |
| `staff_total` | integer | staff_m + staff_f。 | 0 | 29 |
| `prev_grad_total` | integer | prev_grad_m + prev_grad_f。 | 0 | 504 |
| `students_general` | integer | 普通科學生數（科別資料等級別 A）。 | 0 | 67 |
| `students_vocational` | integer | 專業群科學生數（等級別 B）。 | 0 | 0 |
| `students_comprehensive` | integer | 綜合高中學生數（等級別 O）。 | 0 | 1629 |
| `students_practical_skills` | integer | 實用技能學程學生數（等級別 U）。 | 0 | 0 |
| `students_continuing_dept` | integer | 進修部學生數（等級別 C）。 | 0 | 0 |
| `students_night` | integer | 夜間部學生數（日夜別 N，不含附設國中部）。 | 0 | 0 |
| `students_grade1` | integer | 一年級學生數（不含附設國中部），可視為當學年度新生規模。 | 0 | 534 |
| `students_extended` | integer | 延修生數。 | 0 | 0 |
| `students_junior_high_dept` | integer | 附設國中部學生數（等級別 J；不計入 student_total）。 | 0 | 69 |
| `classes_junior_high_dept` | integer | 附設國中部班級數（不計入 classes）。 | 0 | 3 |
| `n_departments` | integer | 科別數（不含附設國中部）。 | 0 | 3 |
| `hs_students_from_programs` | integer | 由科別資料加總的學生數（不含附設國中部）；應等於 student_total，供核對。 | 0 | 1696 |
| `hs_classes_from_programs` | integer | 由科別資料加總的班級數（不含附設國中部）；應等於 classes，供核對。 | 0 | 48 |
| `school_code_raw` | string | 原始檔中的學校代碼（未補零）。 | 0 | 10301 |
| `county_code_raw` | string | 原始檔中的縣市代碼（未補零）。 | 0 | 1 |
| `county_name_raw` | string | 原始檔中的縣市名稱。 | 0 | 新北市 |

## `hs_program_year.csv` — 高級中等學校校×學年度×科別明細

每列為一所學校一個學年度的一個等級別×日夜別×科別，取自教育部「高級中等學校科別資料」（103–114 學年度）。

- 列數：45,837
- 主鍵：`academic_year`, `school_code`, `level_code`, `day_night_code`, `group_code`, `dept_code`

| 欄位 | 型別 | 說明 | 缺失數 | 範例 |
|---|---|---|---:|---|
| `academic_year` | integer | 學年度（民國）。 | 0 | 103 |
| `school_id` | string | 跨年學校識別碼（同 hs_school_year）。 | 0 | 010301 |
| `school_code` | string | 學校代碼（補零為 6 碼）。 | 0 | 010301 |
| `school_name` | string | 學校名稱。 | 0 | 國立華僑中學 |
| `county_code` | string | 縣市代碼（補零為 2 碼）。 | 0 | 01 |
| `county_name` | string | 縣市名稱。 | 0 | 新北市 |
| `level_code` | string | 等級別代碼：A 普通科、B 專業群科、C 進修部、O 綜合高中、U 實用技能學程、J 附設國中部。 | 0 | A |
| `level_name` | string | 等級名稱。 | 0 | 普通科 |
| `day_night_code` | string | 日夜別代碼：D 日間部、N 夜間部。 | 0 | D |
| `day_night_name` | string | 日夜別名稱。 | 0 | 日間部 |
| `group_code` | string | 群別代碼。 | 2,677 | 11 |
| `group_name` | string | 群別名稱（如學術群、商業與管理群）。 | 2,677 | 學術群 |
| `dept_code` | string | 科系代碼。 | 0 | 105 |
| `dept_name` | string | 科系名稱。 | 0 | 體育班 |
| `classes_g1` | integer | 一年級班級數。 | 0 | 1 |
| `classes_g2` | integer | 二年級班級數。 | 0 | 1 |
| `classes_g3` | integer | 三年級班級數。 | 0 | 1 |
| `classes_g4` | integer | 四年級班級數。 | 0 | 0 |
| `student_g1_m` | integer | 一年級男學生數。 | 0 | 12 |
| `student_g1_f` | integer | 一年級女學生數。 | 0 | 7 |
| `student_g2_m` | integer | 二年級男學生數。 | 0 | 14 |
| `student_g2_f` | integer | 二年級女學生數。 | 0 | 6 |
| `student_g3_m` | integer | 三年級男學生數。 | 0 | 15 |
| `student_g3_f` | integer | 三年級女學生數。 | 0 | 13 |
| `student_g4_m` | integer | 四年級男學生數。 | 0 | 0 |
| `student_g4_f` | integer | 四年級女學生數。 | 0 | 0 |
| `student_ext_m` | integer | 延修生男學生數。 | 0 | 0 |
| `student_ext_f` | integer | 延修生女學生數。 | 0 | 0 |
| `prev_grad_m` | integer | 上學年度畢業生數（男）。 | 0 | 14 |
| `prev_grad_f` | integer | 上學年度畢業生數（女）。 | 0 | 10 |
| `student_total` | integer | 該列所有年級與延修生的學生數合計。 | 0 | 67 |
| `classes_total` | integer | 該列所有年級的班級數合計。 | 0 | 3 |

## `hs_school_directory.csv` — 高級中等學校名錄

教育部「一般高級中等學校名錄」（103–115 學年度）與「大專附設高級中等進修學校名錄」合併，含地址解析出的郵遞區號與鄉鎮市區。

- 列數：6,667
- 主鍵：`academic_year`, `directory_type`, `school_code`

| 欄位 | 型別 | 說明 | 缺失數 | 範例 |
|---|---|---|---:|---|
| `academic_year` | integer | 名錄學年度（民國）。 | 0 | 103 |
| `directory_type` | string | general（一般高級中等學校名錄）或 continuing（大專附設高級中等進修學校名錄）。 | 0 | general |
| `school_id` | string | 跨年學校識別碼；hs_school_year 沒有的學校（如 115 學年度新校）沿用自己的校碼。 | 0 | 010301 |
| `school_code` | string | 學校代碼（補零為 6 碼）。 | 0 | 010301 |
| `school_name` | string | 學校名稱。 | 0 | 國立華僑中學 |
| `sector_official` | string | 官方公立／私立欄位（105 學年度起）。 | 1,005 | 公立 |
| `county_code` | string | 名錄縣市欄位中的代碼。 | 0 | 01 |
| `county_name` | string | 名錄縣市欄位中的名稱。 | 0 | 新北市 |
| `postal_code` | string | 地址開頭的郵遞區號。 | 1 | 220 |
| `township` | string | 由地址解析的鄉鎮市區。 | 5 | 板橋區 |
| `address` | string | 原始地址。 | 0 | [220]新北市板橋區大觀路一段32號 |
| `address_county` | string | 由地址解析的縣市（供與 county_name 核對）。 | 9 | 新北市 |
| `phone` | string | 電話。 | 0 | (02)29684131 |
| `url` | string | 網址。 | 6 | http://www.nocsh.ntpc.edu.tw |
| `note` | string | 備註。 | 6,597 | 高中部無學生 |
| `source_file` | string | 來源原始檔名（data/raw/）。 | 0 | directory_103.csv |

## `school_id_crosswalk.csv` — 改碼學校對照表

國立高中改隸直轄市時校碼改變，依規則串連為同一 school_id：舊校碼最後出現於學年度 t−1、新校碼首次出現於 t， 且同縣市、校碼後 3 碼相同、校名去除「國立／市立／縣立／私立」字首後相同。另附名錄地址供核對。

- 列數：23
- 主鍵：`old_code`

| 欄位 | 型別 | 說明 | 缺失數 | 範例 |
|---|---|---|---:|---|
| `old_code` | string | 舊校碼。 | 0 | 030302 |
| `new_code` | string | 新校碼。 | 0 | 033302 |
| `school_id` | string | 串連後的學校識別碼（最早的校碼）。 | 0 | 030302 |
| `old_name` | string | 舊校碼最後一年的校名。 | 0 | 國立龍潭高中 |
| `new_name` | string | 新校碼第一年的校名。 | 0 | 市立龍潭高中 |
| `county_name` | string | 縣市。 | 0 | 桃園市 |
| `last_year_old` | integer | 舊校碼最後出現的學年度。 | 0 | 106 |
| `first_year_new` | integer | 新校碼首次出現的學年度。 | 0 | 107 |
| `address_old` | string | 舊校碼最後一年在名錄中的地址。 | 1 | [325]桃園市龍潭區神龍路155號 |
| `address_new` | string | 新校碼第一年在名錄中的地址。 | 1 | [325]桃園市龍潭區神龍路155號 |
| `address_same` | boolean | 兩者地址是否完全相同（輔助驗證串連正確）。 | 0 | True |
