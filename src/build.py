"""由 data/raw/ 的官方檔案建立四張資料表。

用法：uv run python src/build.py
輸出（data/processed/）：
    hs_school_year.csv          校×學年度面板（103–114）
    hs_program_year.csv         校×學年度×科別明細（103–114）
    hs_school_directory.csv     學校名錄（103–115，含地址與鄉鎮市區）
    school_id_crosswalk.csv     改碼學校對照表
處理規則見 config/build.yml；欄位定義見 config/schema.yml。
"""
import re
import sys

import pandas as pd

from common import OUT_DIR, load_config, read_raw, read_raw_repairing

BASE0_COLS = {
    "學年度": "academic_year", "縣市代碼": "county_code", "縣市名稱": "county_name", "學校代碼": "school_code",
    "學校名稱": "school_name", "專任教師數男": "ft_teacher_m", "專任教師數女": "ft_teacher_f",
    "兼任教師數男": "pt_teacher_m", "兼任教師數女": "pt_teacher_f", "職員數男": "staff_m", "職員數女": "staff_f",
    "班級數": "classes", "學生數男": "student_m", "學生數女": "student_f",
    "上學年畢業生數男": "prev_grad_m", "上學年畢業生數女": "prev_grad_f",
}
BASE2_COLS = {
    "學年度": "academic_year", "縣市代碼": "county_code", "縣市名稱": "county_name", "學校代碼": "school_code",
    "學校名稱": "school_name", "等級別": "level_code", "等級名稱": "level_name", "日夜別": "day_night_code",
    "日夜別名稱": "day_night_name", "群別代碼": "group_code", "群別名稱": "group_name", "科系代碼": "dept_code",
    "科系名稱": "dept_name",
    "一年級班級數": "classes_g1", "二年級班級數": "classes_g2", "三年級班級數": "classes_g3", "四年級班級數": "classes_g4",
    "一年級男學生數": "student_g1_m", "一年級女學生數": "student_g1_f", "二年級男學生數": "student_g2_m",
    "二年級女學生數": "student_g2_f", "三年級男學生數": "student_g3_m", "三年級女學生數": "student_g3_f",
    "四年級男學生數": "student_g4_m", "四年級女學生數": "student_g4_f",
    "延修生男學生數": "student_ext_m", "延修生女學生數": "student_ext_f",
    "上學年畢業生數男": "prev_grad_m", "上學年畢業生數女": "prev_grad_f",
}
TEXT_COLS = {"academic_year", "county_code", "county_name", "school_code", "school_name", "level_code", "level_name",
             "day_night_code", "day_night_name", "group_code", "group_name", "dept_code", "dept_name"}


def to_int(d: pd.DataFrame, cols) -> pd.DataFrame:
    """轉整數；有無法解析或非整數的值就停止，不默默轉成缺失。"""
    for c in cols:
        v = pd.to_numeric(d[c], errors="coerce")
        bad = v.isna() & d[c].notna()
        if bad.any() or (v.dropna() % 1 != 0).any():
            raise ValueError(f"{c} 有無法解析的值：{d.loc[bad, c].unique()[:5].tolist()}")
        d[c] = v.astype("Int64")
    return d


def normalize_codes(d: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    n = cfg["normalize"]
    d["academic_year"] = d["academic_year"].astype(int)
    d["school_code"] = d["school_code"].str.strip().str.zfill(n["school_code_width"])
    if "county_code" in d:
        d["county_code"] = d["county_code"].str.strip().str.zfill(n["county_code_width"])
    d["county_name"] = d["county_name"].str.strip().replace(n["county_name_map"])
    d["school_name"] = d["school_name"].str.strip()
    return d


def link_schools(d: pd.DataFrame, cfg: dict) -> tuple[dict, pd.DataFrame]:
    """改碼學校串連：舊碼最後出現於 t−1、新碼首次出現於 t、同縣市、後 3 碼相同、去字首校名相同。"""
    strip = re.compile(cfg["name_prefix_strip"])
    g = d.sort_values("academic_year").groupby("school_code")
    first, last = g["academic_year"].min(), g["academic_year"].max()
    name_first, name_last, county = g["school_name"].first(), g["school_name"].last(), g["county_name"].first()
    links = []
    for old in last.index[last < d["academic_year"].max()]:
        for new in first.index[first == last[old] + 1]:
            if (county[new] == county[old] and new[3:] == old[3:]
                    and strip.sub("", name_first[new]) == strip.sub("", name_last[old])):
                links.append({"old_code": old, "new_code": new, "old_name": name_last[old], "new_name": name_first[new],
                              "county_name": county[old], "last_year_old": int(last[old]),
                              "first_year_new": int(first[new])})
    cw = pd.DataFrame(links, columns=["old_code", "new_code", "old_name", "new_name", "county_name",
                                      "last_year_old", "first_year_new"])
    if cw["old_code"].duplicated().any() or cw["new_code"].duplicated().any():
        raise ValueError(f"改碼串連不是一對一：\n{cw}")
    parent = dict(zip(cw["new_code"], cw["old_code"]))

    def root(code):
        while code in parent:
            code = parent[code]
        return code

    id_map = {c: root(c) for c in d["school_code"].unique()}
    cw.insert(2, "school_id", cw["old_code"].map(id_map))
    return id_map, cw


def parse_address(addr: str, acfg: dict) -> tuple:
    """'[220]新北市板橋區大觀路…' → ('220', '新北市', '板橋區')；省略縣名的地址縣市回傳缺失。"""
    if pd.isna(addr):
        return (pd.NA, pd.NA, pd.NA)
    m = re.match(r"^\[(\d+)\]\s*(.*)$", addr.strip())
    postal, rest = (m.group(1), m.group(2)) if m else (pd.NA, addr.strip())
    rest = rest.replace("台", "臺")
    county = next((c for c in acfg["counties"] if rest.startswith(c)), pd.NA)
    tail = rest[len(county):] if isinstance(county, str) else rest
    suffixes = acfg["township_suffixes"]
    m = re.match(rf"^(\S{{1,3}}?[{suffixes}])", tail)
    if not m:
        return (postal, county, pd.NA)
    town = m.group(1)
    # 「新市區」：非貪婪比對停在「新市」；只有「…市」後面緊接「區」時才補上
    if town.endswith("市") and tail[len(town):len(town) + 1] == "區":
        town += "區"
    return (postal, county, acfg["township_name_map"].get(town, town))


def build_school_year(cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = read_raw("school_stats_base0.csv")
    if list(raw.columns) != list(BASE0_COLS):
        raise ValueError(f"base0 欄名改變：{list(raw.columns)}")
    d = raw.rename(columns=BASE0_COLS)
    d["school_code_raw"], d["county_code_raw"], d["county_name_raw"] = d["school_code"], d["county_code"], d["county_name"]
    d = normalize_codes(d, cfg)
    d = to_int(d, [c for c in BASE0_COLS.values() if c not in TEXT_COLS])
    for total, (m, f) in {"student_total": ("student_m", "student_f"), "ft_teacher_total": ("ft_teacher_m", "ft_teacher_f"),
                          "pt_teacher_total": ("pt_teacher_m", "pt_teacher_f"), "staff_total": ("staff_m", "staff_f"),
                          "prev_grad_total": ("prev_grad_m", "prev_grad_f")}.items():
        d[total] = d[m] + d[f]
    id_map, cw = link_schools(d, cfg["school_linkage"])
    d["school_id"] = d["school_code"].map(id_map)

    sec = cfg["sector"]
    d["sector_code_digit"] = d["school_code"].str[2]
    d["sector"] = d["sector_code_digit"].map(sec["map"]).fillna(sec["other"])
    for flag, pattern in cfg["flags"].items():
        d[flag] = d["school_name"].str.contains(pattern)
    d["no_enrolled_students"] = d["student_total"] == 0
    return d, cw


def build_program(cfg: dict, id_map: dict) -> pd.DataFrame:
    raw = read_raw("program_stats_base2.csv")
    if list(raw.columns) != list(BASE2_COLS):
        raise ValueError(f"base2 欄名改變：{list(raw.columns)}")
    p = normalize_codes(raw.rename(columns=BASE2_COLS), cfg)
    p = to_int(p, [c for c in BASE2_COLS.values() if c not in TEXT_COLS])
    missing = set(p["school_code"]) - set(id_map)
    if missing:
        raise ValueError(f"科別資料有校別資料沒有的校碼：{sorted(missing)[:10]}")
    p["school_id"] = p["school_code"].map(id_map)
    stu = [c for c in p.columns if c.startswith("student_")]
    p["student_total"] = p[stu].sum(axis=1)
    p["classes_total"] = p[[c for c in p.columns if c.startswith("classes_g")]].sum(axis=1)
    lead = ["academic_year", "school_id", "school_code", "school_name", "county_code", "county_name"]
    return p[lead + [c for c in p.columns if c not in lead]].sort_values(
        ["school_id", "academic_year", "level_code", "day_night_code", "group_code", "dept_code"]).reset_index(drop=True)


def program_aggregates(p: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """把科別明細彙整成校×學年度的學程結構欄位。"""
    jh = cfg["program"]["junior_high_level_code"]
    hs = p[p["level_code"] != jh]
    keys = ["academic_year", "school_code"]
    out = hs.groupby(keys).agg(
        students_grade1=("student_g1_m", "sum"), n_departments=("dept_code", "nunique"))
    out["students_grade1"] += hs.groupby(keys)["student_g1_f"].sum()
    out["students_extended"] = hs.groupby(keys)[["student_ext_m", "student_ext_f"]].sum().sum(axis=1)
    out["students_night"] = hs[hs["day_night_code"] == "N"].groupby(keys)["student_total"].sum()
    for code, col in cfg["program"]["level_columns"].items():
        out[col] = hs[hs["level_code"] == code].groupby(keys)["student_total"].sum()
    j = p[p["level_code"] == jh].groupby(keys)
    out["students_junior_high_dept"] = j["student_total"].sum()
    out["classes_junior_high_dept"] = j["classes_total"].sum()
    out["hs_students_from_programs"] = hs.groupby(keys)["student_total"].sum()
    out["hs_classes_from_programs"] = hs.groupby(keys)["classes_total"].sum()
    return out.fillna(0).astype("Int64").reset_index()


def build_directory(cfg: dict, id_map: dict, files: list[tuple]) -> pd.DataFrame:
    rename = {"學年度": "academic_year", "代碼": "school_code", "學校名稱": "school_name", "公/私立": "sector_official",
              "公私立別": "sector_official", "縣市名稱": "county_label", "地址": "address", "電話": "phone",
              "網址": "url", "備註": "note"}
    frames = []
    for file, year, dtype in files:
        d, repaired = read_raw_repairing(file)
        if repaired:
            print(f"[repair] {file}：{repaired} 列因欄位內換行被接回上一列")
        d = d.rename(columns=rename)
        if "academic_year" not in d:
            d["academic_year"] = str(year)
        if "sector_official" not in d:
            d["sector_official"] = pd.NA
        d["directory_type"] = dtype
        d["source_file"] = file
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d["academic_year"] = d["academic_year"].astype(int)
    d["school_code"] = d["school_code"].str.strip().str.zfill(cfg["normalize"]["school_code_width"])
    lab = d["county_label"].str.extract(r"^\[(\d+)\](.+)$")
    d["county_code"] = lab[0].str.zfill(cfg["normalize"]["county_code_width"])
    d["county_name"] = lab[1].str.strip().replace(cfg["normalize"]["county_name_map"])
    parsed = d["address"].apply(lambda a: parse_address(a, cfg["address"]))
    d["postal_code"] = parsed.str[0]
    d["address_county"] = parsed.str[1]
    d["township"] = parsed.str[2]
    d["school_id"] = d["school_code"].map(id_map).fillna(d["school_code"])  # 115 學年度新校沿用自己的校碼
    d["school_name"] = d["school_name"].str.strip()
    cols = ["academic_year", "directory_type", "school_id", "school_code", "school_name", "sector_official",
            "county_code", "county_name", "postal_code", "township", "address", "address_county", "phone", "url",
            "note", "source_file"]
    return d[cols].sort_values(["school_id", "academic_year", "directory_type"]).reset_index(drop=True)


def attach_location(d: pd.DataFrame, directory: pd.DataFrame) -> pd.DataFrame:
    """同學年度名錄優先；沒有時取同一 school_id 最接近學年度的名錄。"""
    loc = directory.dropna(subset=["township"]).drop_duplicates(["school_id", "academic_year"])
    loc = loc[["school_id", "academic_year", "school_code", "postal_code", "township", "sector_official"]]
    same = d.merge(loc.drop(columns="school_id"), on=["academic_year", "school_code"], how="left")
    same["location_source_year"] = same["academic_year"].where(same["township"].notna())
    need = same["township"].isna()
    if need.any():
        cand = same.loc[need, ["academic_year", "school_id"]].reset_index().merge(
            loc.rename(columns={"academic_year": "dir_year"}), on="school_id")
        cand["gap"] = (cand["dir_year"] - cand["academic_year"]).abs()
        best = cand.sort_values(["index", "gap", "dir_year"]).drop_duplicates("index").set_index("index")
        same.loc[best.index, ["postal_code", "township"]] = best[["postal_code", "township"]].values
        same.loc[best.index, "location_source_year"] = best["dir_year"].values
    same["location_source_year"] = same["location_source_year"].astype("Int64")
    return same


def main() -> int:
    cfg = load_config("build.yml")
    src = load_config("sources.yml")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    d, cw = build_school_year(cfg)
    id_map = dict(zip(d["school_code"], d["school_id"]))
    p = build_program(cfg, id_map)
    agg = program_aggregates(p, cfg)

    dir_src = next(s for s in src["sources"] if s["id"] == "directory")
    files = [(dir_src["file_template"].format(year=y), y, "general") for y in dir_src["year_list"]]
    files.append(("directory_continuing_115.csv", None, "continuing"))
    directory = build_directory(cfg, id_map, files)

    d = d.merge(agg, on=["academic_year", "school_code"], how="left")
    agg_cols = [c for c in agg.columns if c not in ("academic_year", "school_code")]
    d[agg_cols] = d[agg_cols].fillna(0)  # 沒有科別資料的校年（學生數皆為 0）→ 學程人數為 0
    d = attach_location(d, directory)

    # 改碼對照表加上名錄地址，供核對
    addr = directory[directory["directory_type"] == "general"].set_index(["academic_year", "school_code"])["address"]
    cw["address_old"] = [addr.get((y, c), pd.NA) for y, c in zip(cw["last_year_old"], cw["old_code"])]
    cw["address_new"] = [addr.get((y, c), pd.NA) for y, c in zip(cw["first_year_new"], cw["new_code"])]
    cw["address_same"] = cw["address_old"] == cw["address_new"]

    schema = load_config("schema.yml")
    outputs = {"hs_school_year": d, "hs_program_year": p, "hs_school_directory": directory, "school_id_crosswalk": cw}
    for name, df in outputs.items():
        cols = [f["name"] for f in schema["tables"][name]["fields"]]
        extra, missing = set(df.columns) - set(cols), set(cols) - set(df.columns)
        if missing:
            raise ValueError(f"{name}：schema 有但資料沒有的欄位 {sorted(missing)}")
        df = df[cols]  # 只輸出 schema 定義的欄位，依 schema 順序
        if name == "hs_school_year":
            df = df.sort_values(["school_id", "academic_year"])
        df.to_csv(OUT_DIR / f"{name}.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
        note = f"（未輸出的中間欄位：{sorted(extra)}）" if extra else ""
        print(f"[OK] {name}.csv：{len(df)} 列 × {len(cols)} 欄{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
