"""由 config/schema.yml 與實際資料產生 docs/codebook.md 與 datapackage.json。

用法：uv run python src/docs.py
"""
import hashlib
import json
import sys

import pandas as pd

from common import DOCS_DIR, OUT_DIR, ROOT, load_config

DATASET_NAME = "tw-highschool-panel"
VERSION = "2026.10.0"


def sha256_of(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    schema, sources = load_config("schema.yml"), load_config("sources.yml")
    lines = [
        "# 欄位字典（Codebook）",
        "",
        f"> 由 `src/docs.py` 依 `config/schema.yml` 與實際資料自動產生，請勿手動修改。資料版本：{VERSION}",
        "",
        "所有 CSV 皆為 UTF-8（含 BOM，方便以 Excel 開啟），空白儲存格表示缺失。學年度為民國紀年。",
        "",
    ]
    resources = []
    for name, t in schema["tables"].items():
        path = OUT_DIR / f"{name}.csv"
        str_cols = {f["name"]: str for f in t["fields"] if f["type"] == "string"}
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str_cols, keep_default_na=False, na_values=[""])
        lines += [f"## `{name}.csv` — {t['title']}", "", t["description"].strip(), "",
                  f"- 列數：{len(df):,}",
                  f"- 主鍵：{', '.join(f'`{k}`' for k in t['primary_key'])}", "",
                  "| 欄位 | 型別 | 說明 | 缺失數 | 範例 |", "|---|---|---|---:|---|"]
        for f in t["fields"]:
            col = df[f["name"]]
            example = col.dropna().iloc[0] if col.notna().any() else ""
            desc = str(f["description"]).replace("|", "\\|")
            lines.append(f"| `{f['name']}` | {f['type']} | {desc} | {int(col.isna().sum()):,} | {example} |")
        lines.append("")
        resources.append({
            "name": name.replace("_", "-"),
            "path": f"data/processed/{name}.csv",
            "title": t["title"],
            "description": t["description"].strip(),
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "bytes": path.stat().st_size,
            "hash": f"sha256:{sha256_of(path)}",
            "schema": {
                "fields": [{"name": f["name"], "type": f["type"], "description": str(f["description"])}
                           for f in t["fields"]],
                "primaryKey": t["primary_key"],
                "missingValues": [""],
            },
        })

    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "codebook.md").write_text("\n".join(lines), encoding="utf-8")

    package = {
        "name": DATASET_NAME,
        "title": "臺灣高級中等學校校級面板資料（103–114 學年度）",
        "description": "整合教育部統計處公開之高級中等學校校別、科別、縣市概況與學校名錄資料，"
                       "建立可跨年追蹤的校×學年度面板，並附資料品質驗證。",
        "version": VERSION,
        "created": sources["snapshot_date"],
        "licenses": [
            {"name": "CC-BY-4.0", "path": "https://creativecommons.org/licenses/by/4.0/",
             "title": "衍生資料表（data/processed/）"},
            {"name": "OGDL-Taiwan-1.0", "path": sources["license_url"],
             "title": "原始資料（data/raw/）：政府資料開放授權條款-第1版"},
        ],
        "sources": [{"title": f"{sources['provider']}：{s['title']}", "path": s["page"]} for s in sources["sources"]],
        "resources": resources,
    }
    (ROOT / "datapackage.json").write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] docs/codebook.md、datapackage.json（{len(resources)} 個資料表）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
