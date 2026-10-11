"""共用設定與讀檔函式。"""
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
DOCS_DIR = ROOT / "docs"


def load_config(name: str) -> dict:
    return yaml.safe_load((ROOT / "config" / name).read_text(encoding="utf-8"))


def iter_files(cfg: dict):
    """把 sources.yml 展開成逐一檔案（名錄依學年度展開）。"""
    for s in cfg["sources"]:
        if "url_template" in s:
            for y in s["year_list"]:
                yield {"source_id": s["id"], "title": s["title"], "page": s["page"], "year": y,
                       "url": s["url_template"].format(year=y), "file": s["file_template"].format(year=y)}
        else:
            yield {"source_id": s["id"], "title": s["title"], "page": s["page"], "year": None,
                   "url": s["url"], "file": s["file"]}


def read_raw_repairing(file: str) -> tuple[pd.DataFrame, int]:
    """讀取時修補欄位內未加引號的換行：欄數不足的列接回上一列的最後一欄。

    原始檔保持不動；回傳 (資料, 修補列數)，修補數由 validate.py 報告。
    """
    import csv

    with open(RAW_DIR / file, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = [c.replace("﻿", "").strip() for c in rows[0]]
    fixed, repaired = [], 0
    for r in rows[1:]:
        if not any(x.strip() for x in r):
            continue
        if len(r) < len(header) and fixed:
            fixed[-1][-1] = (fixed[-1][-1] + " " + ",".join(r)).strip()
            repaired += 1
        elif len(r) == len(header):
            fixed.append(r)
        else:
            raise ValueError(f"{file} 有無法修補的列：{r}")
    df = pd.DataFrame(fixed, columns=header, dtype="str").replace({"": pd.NA})
    return df, repaired


def read_raw(file: str) -> pd.DataFrame:
    """所有欄位以字串讀入；只有空白儲存格視為缺失。欄名去除 BOM 與空白。"""
    df = pd.read_csv(RAW_DIR / file, encoding="utf-8-sig", dtype=str, keep_default_na=False, na_values=[""])
    df.columns = [c.replace("﻿", "").strip() for c in df.columns]
    return df
