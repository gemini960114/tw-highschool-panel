"""驗證 data/processed/ 的資料表：結構、完整性，以及各官方來源之間的交叉核對。

用法：uv run python src/validate.py
輸出：docs/data_quality_checks.csv、docs/data_quality_report.md
結束碼：有任何 FAIL 時為 1。
"""
import sys
from datetime import datetime, timezone

import pandas as pd

from common import DOCS_DIR, OUT_DIR, RAW_DIR, load_config, read_raw, read_raw_repairing

checks: list[dict] = []


def check(group: str, desc: str, ok, value="", warn_only: bool = False) -> None:
    status = "INFO" if ok is None else ("PASS" if ok else ("WARN" if warn_only else "FAIL"))
    checks.append({"group": group, "check": desc, "status": status, "value": str(value)})


def load(name: str, schema: dict) -> pd.DataFrame:
    fields = schema["tables"][name]["fields"]
    str_cols = {f["name"]: str for f in fields if f["type"] == "string"}
    df = pd.read_csv(OUT_DIR / f"{name}.csv", encoding="utf-8-sig", dtype=str_cols, keep_default_na=False,
                     na_values=[""])
    check("結構", f"{name}：欄位與 schema 完全一致（名稱與順序）", list(df.columns) == [f["name"] for f in fields])
    for f in fields:
        col = df[f["name"]].dropna()
        if f["type"] == "integer":
            ok = pd.to_numeric(col, errors="coerce").notna().all() and (pd.to_numeric(col) % 1 == 0).all()
        elif f["type"] == "boolean":
            ok = col.astype(str).isin(["True", "False"]).all()
        else:
            continue
        if not ok:
            check("結構", f"{name}.{f['name']} 符合型別 {f['type']}", False)
    pk = schema["tables"][name]["primary_key"]
    dup = int(df.duplicated(pk).sum())
    check("結構", f"{name}：主鍵 {pk} 唯一", dup == 0, f"重複 {dup}")
    return df


def main() -> int:
    cfg, schema = load_config("build.yml"), load_config("schema.yml")
    manifest = pd.read_csv(RAW_DIR / "MANIFEST.csv", encoding="utf-8-sig", dtype=str)
    check("來源", "MANIFEST 列出的原始檔都存在且非空",
          all((RAW_DIR / f).exists() and (RAW_DIR / f).stat().st_size > 0 for f in manifest["file"]),
          f"{len(manifest)} 個檔案")

    sy = load("hs_school_year", schema)
    pg = load("hs_program_year", schema)
    dr = load("hs_school_directory", schema)
    cw = load("school_id_crosswalk", schema)
    for c in ["continuing_school", "special_education_school", "no_enrolled_students"]:
        sy[c] = sy[c].astype(str).eq("True")

    # ---- 面板完整性 ----
    raw0 = read_raw("school_stats_base0.csv")
    check("完整性", "面板列數 = base0 原始列數", len(sy) == len(raw0), f"{len(sy)} / {len(raw0)}")
    yrs = sorted(sy["academic_year"].unique())
    check("完整性", "學年度連續無缺", yrs == list(range(yrs[0], yrs[-1] + 1)), f"{yrs[0]}–{yrs[-1]}")
    check("完整性", "(學年度, school_code) 唯一", sy.duplicated(["academic_year", "school_code"]).sum() == 0)
    counts = ["ft_teacher_m", "ft_teacher_f", "pt_teacher_m", "pt_teacher_f", "staff_m", "staff_f", "classes",
              "student_m", "student_f", "prev_grad_m", "prev_grad_f"]
    check("完整性", "人數欄位無缺失", int(sy[counts].isna().sum().sum()) == 0, int(sy[counts].isna().sum().sum()))
    check("完整性", "人數欄位無負值", int((sy[counts] < 0).sum().sum()) == 0)
    check("完整性", "校碼皆為 6 碼", (sy["school_code"].str.len() == 6).all())

    # ---- 代碼 ----
    c2n = sy.groupby("county_code")["county_name"].nunique()
    check("代碼", "每個縣市代碼只對應一個縣市名稱", (c2n == 1).all(), f"{len(c2n)} 個代碼／{sy['county_name'].nunique()} 個縣市")
    n2c = sy.groupby("county_name")["county_code"].apply(lambda s: sorted(s.unique()))
    multi = {k: v for k, v in n2c.items() if len(v) > 1}
    check("代碼", "一縣市多代碼僅限 2010 年合併的已知舊代碼",
          multi == {k: sorted(v) for k, v in cfg["normalize"]["county_codes_merged_2010"].items()}, multi)
    t03 = read_raw("county_summary_edu_B_4_2.csv")
    check("代碼", "縣市名稱集合與縣市概況（31454）相同", set(sy["county_name"]) == set(t03["學校所在地[縣市別]"]))
    check("代碼", "sector 無法判定（unknown）的列", (sy["sector"] == "unknown").sum() == 0,
          int((sy["sector"] == "unknown").sum()))

    # ---- 設立別 vs 名錄官方欄位 ----
    s = sy.dropna(subset=["sector_official"])
    derived_public = s["sector"].isin(["public_national", "public_local"])
    official_public = s["sector_official"].str.startswith("公")
    agree = (derived_public == official_public)
    check("交叉核對", "校碼推導的公私立 = 名錄官方公私立欄位", agree.all(),
          f"一致 {int(agree.sum())}/{len(s)} 校年（{s['academic_year'].min()}–{s['academic_year'].max()}）")

    # ---- 改碼串連 ----
    check("串連", f"改碼串連組數 = {cfg['school_linkage']['expected_links']}",
          len(cw) == cfg["school_linkage"]["expected_links"], len(cw))
    check("串連", "校碼數 − 串連數 = school_id 數",
          sy["school_code"].nunique() - len(cw) == sy["school_id"].nunique(),
          f"{sy['school_code'].nunique()} − {len(cw)} = {sy['school_id'].nunique()}")
    cw_same = cw["address_same"].astype(str).eq("True")
    check("串連", "串連前後名錄地址完全相同", cw_same.all(), f"{int(cw_same.sum())}/{len(cw)}", warn_only=True)
    pub = sy.assign(p=sy["sector"].isin(["public_national", "public_local"])).groupby("school_id")["p"].nunique()
    check("串連", "同一 school_id 的公私立跨年不變", (pub == 1).all(), int((pub > 1).sum()))
    sets = {y: set(sy.loc[sy["academic_year"] == y, "school_id"]) for y in yrs}
    new_per_year = {int(y): len(sets[y] - sets[yrs[i - 1]]) for i, y in enumerate(yrs) if i}
    check("串連", "串連後單一學年度新增學校 ≤ 10（偵測未串連的改碼）", max(new_per_year.values()) <= 10,
          new_per_year, warn_only=True)
    span = sy.groupby("school_id")["academic_year"].agg(["min", "max", "count"])
    check("串連", "沒有中途缺年又出現的學校", ((span["max"] - span["min"] + 1) == span["count"]).all())
    check("串連", "全期每年都有資料的學校", None, f"{int((span['count'] == len(yrs)).sum())}/{len(span)} 校")

    # ---- 科別資料 vs 校別資料 ----
    ok_s = (sy["hs_students_from_programs"] == sy["student_total"])
    ok_c = (sy["hs_classes_from_programs"] == sy["classes"])
    check("交叉核對", "科別資料加總學生數（不含附設國中部）= 校別學生數", ok_s.all(), f"一致 {int(ok_s.sum())}/{len(sy)}")
    check("交叉核對", "科別資料加總班級數（不含附設國中部）= 校別班級數", ok_c.all(), f"一致 {int(ok_c.sum())}/{len(sy)}")
    levels = list(cfg["program"]["level_columns"].values())
    ok_l = sy[levels].sum(axis=1) == sy["student_total"]
    check("交叉核對", "各學程學生數（普通、專業群科、綜合、實用技能、進修部）加總 = 學生總數", ok_l.all(),
          f"一致 {int(ok_l.sum())}/{len(sy)}")
    check("交叉核對", "科別資料的校碼都在校別資料中",
          set(zip(pg["academic_year"], pg["school_code"])) <= set(zip(sy["academic_year"], sy["school_code"])))
    no_prog = sy[~sy.set_index(["academic_year", "school_code"]).index.isin(
        pg.set_index(["academic_year", "school_code"]).index)]
    check("交叉核對", "校別資料中沒有科別資料的校年", None,
          f"{len(no_prog)} 列（學生數皆為 0：{bool((no_prog['student_total'] == 0).all())}）")

    # ---- 縣市概況 vs 校別資料 ----
    t = t03.copy()
    t["academic_year"] = t["學年度"].astype(int)
    for a, b in [("公立學生數[人]", "私立學生數[人]"), ("公立班級數", "私立班級數"), ("公立教師數[人]", "私立教師數[人]")]:
        t[a.replace("公立", "")] = pd.to_numeric(t[a]) + pd.to_numeric(t[b])
    agg = sy.groupby(["academic_year", "county_name"])[["student_total", "classes", "ft_teacher_total"]].sum()
    t = t.rename(columns={"學校所在地[縣市別]": "county_name"}).set_index(["academic_year", "county_name"])
    m = agg.join(t[["學生數[人]", "班級數", "教師數[人]"]], how="inner")
    check("交叉核對", "縣市×學年度配對數 = 22 × 11", len(m) == 242, len(m))
    for mine, theirs, name in [("student_total", "學生數[人]", "學生數"), ("classes", "班級數", "班級數"),
                               ("ft_teacher_total", "教師數[人]", "專任教師數")]:
        diff = int((m[mine] != m[theirs]).sum())
        check("交叉核對", f"縣市×學年度{name}與縣市概況完全一致", diff == 0, f"不一致 {diff}/{len(m)}")

    # ---- 名錄 ----
    _, repaired = read_raw_repairing("directory_115.csv")
    check("名錄", "讀取時修補的欄位內換行（原始檔未修改）", None, f"directory_115.csv：{repaired} 列")
    gen = dr[dr["directory_type"] == "general"]
    file_year = gen["source_file"].str.extract(r"(\d{3})")[0].astype(int)
    check("名錄", "一般名錄的學年度欄 = 檔名學年度", (gen["academic_year"] == file_year).all())
    check("名錄", "地址解析出鄉鎮市區的比例", dr["township"].notna().mean() == 1,
          f"{dr['township'].notna().mean():.2%}", warn_only=True)
    p2t = dr.dropna(subset=["postal_code", "township"]).groupby(["address_county", "postal_code"])["township"].nunique()
    check("名錄", "同一縣市＋郵遞區號只對應一個鄉鎮市區", (p2t == 1).all(),
          {f"{k[0]}{k[1]}": int(v) for k, v in p2t[p2t > 1].items()} or "全部唯一", warn_only=True)
    cc = dr.dropna(subset=["address_county"])
    mism = cc[cc["address_county"] != cc["county_name"]]
    check("名錄", "地址中的縣市 = 名錄縣市欄位", mism.empty,
          f"不一致 {len(mism)}：" + "、".join(sorted(set(mism["school_name"])))[:200], warn_only=True)

    # ---- 面板位置欄位 ----
    has = sy["township"].notna()
    same_year = sy["location_source_year"] == sy["academic_year"]
    check("位置", "面板有鄉鎮市區的校年比例", None,
          f"{has.mean():.2%}（同年度名錄 {same_year.mean():.2%}，其他年度補值 {(has & ~same_year).mean():.2%}）")
    miss = sy[~has]
    check("位置", "面板缺鄉鎮市區的校年", None,
          f"{len(miss)} 列；其中進修學校 {int(miss['continuing_school'].sum())}、學生數為 0 {int(miss['no_enrolled_students'].sum())}")

    # ---- 輸出 ----
    df = pd.DataFrame(checks)
    DOCS_DIR.mkdir(exist_ok=True)
    df.to_csv(DOCS_DIR / "data_quality_checks.csv", index=False, encoding="utf-8-sig", lineterminator="\n")
    write_report(df, manifest)
    for c in checks:
        print(f"[{c['status']:<4}] {c['group']}｜{c['check']}：{c['value']}")
    return 1 if (df["status"] == "FAIL").any() else 0


def write_report(df: pd.DataFrame, manifest: pd.DataFrame) -> None:
    def table(d: pd.DataFrame) -> str:
        esc = lambda v: str(v).replace("|", "\\|").replace("\n", " ")
        return "\n".join(["| " + " | ".join(d.columns) + " |", "|" + "---|" * len(d.columns),
                          *["| " + " | ".join(esc(v) for v in r) + " |" for r in d.itertuples(index=False)]])
    counts = "、".join(f"{k} {v}" for k, v in df["status"].value_counts().sort_index().items())
    text = [
        "# 資料品質報告",
        "",
        f"> 由 `src/validate.py` 自動產生，請勿手動修改。產生時間（UTC）：{datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        f"**結果：** {counts}",
        "",
        "PASS＝通過；WARN＝需留意但不影響使用；INFO＝描述性資訊；FAIL＝資料有誤（發布前必須為 0）。",
        "",
        "## 檢查項目",
        "",
        table(df[["group", "check", "status", "value"]]),
        "",
        "## 原始檔快照",
        "",
        table(manifest[["file", "source_id", "downloaded_at_utc", "bytes", "sha256"]]),
        "",
    ]
    (DOCS_DIR / "data_quality_report.md").write_text("\n".join(text), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
