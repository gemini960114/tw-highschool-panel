"""下載 config/sources.yml 列出的官方檔案，記錄 SHA-256。

用法：
    uv run python src/acquire.py            # 已存在的檔案不重新下載（保留快照）
    uv run python src/acquire.py --refresh  # 重新下載全部檔案（建立新快照時使用）
輸出：data/raw/*.csv（唯讀）、data/raw/MANIFEST.csv
"""
import argparse
import csv
import hashlib
import os
import stat
import sys
import urllib.request
from datetime import datetime, timezone

from common import RAW_DIR, iter_files, load_config


def sha256_of(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest) -> None:
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(url, timeout=120) as resp, open(tmp, "wb") as f:
        f.write(resp.read())
    if dest.exists():
        os.chmod(dest, stat.S_IWRITE)
        dest.unlink()
    tmp.rename(dest)
    os.chmod(dest, stat.S_IREAD)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    cfg = load_config("sources.yml")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = RAW_DIR / "MANIFEST.csv"
    previous = {}
    if manifest.exists():
        with open(manifest, encoding="utf-8-sig", newline="") as f:
            previous = {r["file"]: r for r in csv.DictReader(f)}

    rows = []
    for item in iter_files(cfg):
        dest = RAW_DIR / item["file"]
        if args.refresh or not dest.exists():
            print(f"[download] {item['file']} ← {item['url']}")
            download(item["url"], dest)
            when = datetime.now(timezone.utc).isoformat(timespec="seconds")
        else:
            when = previous.get(item["file"], {}).get("downloaded_at_utc", "")
        rows.append({**item, "year": item["year"] or "", "downloaded_at_utc": when,
                     "bytes": dest.stat().st_size, "sha256": sha256_of(dest)})

    with open(manifest, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] {len(rows)} 個檔案，清單：{manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
