# bing-UHD-cn-README-0.1.0.py
# github.com/shenjuexiao
# 20261023

# bing-UHD-cn-README.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成 Bing 每日壁纸 - UHD 中文 的 README.md
从 bing-JSON-cn-{year}.json 读取数据，随机不重复展示缩略图。
"""

import json
import random
import shutil
from datetime import date
from pathlib import Path

# 配置
YEARS = [2026, 2025, 2024, 2023, 2022]
EMOJI = {
    2026: "🐎",
    2025: "🐍",
    2024: "🐉",
    2023: "🐇",
    2022: "🐅",
}
COLS = 4
ROWS = 4
TOTAL = COLS * ROWS
OUTPUT = Path("bing-UHD-cn-README.md")
README = Path("README.md")
JSON_DIR_TEMPLATE = "bing-JSON-cn-{year}"
JSON_FILE_TEMPLATE = "bing-JSON-cn-{year}.json"


def load_items(year: int) -> list[dict]:
    """读取指定年份的 JSON 数据。"""
    path = Path(JSON_DIR_TEMPLATE.format(year=year)) / JSON_FILE_TEMPLATE.format(year=year)
    if not path.exists():
        # 兼容 JSON 直接放在根目录的情况
        alt = Path(JSON_FILE_TEMPLATE.format(year=year))
        path = alt if alt.exists() else path
    if not path.exists():
        print(f"[警告] 未找到 {path}，跳过 {year}")
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[警告] 读取 {path} 失败：{e}")
        return []

    # 兼容 {"images": [...]} 或直接列表
    if isinstance(data, dict):
        data = data.get("images") or data.get("data") or []
    return data if isinstance(data, list) else []


def normalize_item(item: dict) -> dict | None:
    """提取 title / enddate / thumb / uhd / fallback。"""
    urlbase = item.get("urlbase")
    if not urlbase:
        return None
    enddate = (item.get("enddate") or "").strip()
    title = (item.get("title") or "").strip() or enddate
    base = "https://www.bing.com" + urlbase
    return {
        "title": title,
        "enddate": enddate,
        "thumb": base + "_320x240.jpg",
        "uhd": base + "_UHD.jpg",
        "fallback": base + "_1920x1080.jpg",
    }


def random_items(year: int, count: int = TOTAL) -> list[dict]:
    """随机选取不重复条目，按 enddate 时间顺序排列。"""
    items = [normalize_item(i) for i in load_items(year)]
    items = [i for i in items if i and i["enddate"]]
    if not items:
        return []
    # 去重（按 enddate）
    seen, unique = set(), []
    for i in items:
        if i["enddate"] not in seen:
            seen.add(i["enddate"])
            unique.append(i)
    count = min(count, len(unique))
    picked = random.sample(unique, count)
    return sorted(picked, key=lambda x: x["enddate"])


def render_table(items: list[dict]) -> str:
    """生成 4×4 表格：日期行 → 标题行 → 图片行。"""
    if not items:
        return "_暂无数据_"

    # 补齐到 TOTAL，避免表格不齐
    while len(items) < TOTAL:
        items.append(items[-1])

    lines = []
    for r in range(ROWS):
        row = items[r * COLS:(r + 1) * COLS]

        # 日期行
        lines.append("| " + " | ".join(i["enddate"] for i in row) + " |")
        # 对齐行
        lines.append("| " + " | ".join([":---:"] * COLS) + " |")
        # 标题行
        lines.append("| " + " | ".join(i["title"] for i in row) + " |")
        # 图片行
        img_cells = []
        for i in row:
            img_cells.append(
                f'[![{i["title"]}]({i["thumb"]})]({i["uhd"]})'
            )
        lines.append("| " + " | ".join(img_cells) + " |")
        lines.append("")  # 空行分隔

    return "\n".join(lines).rstrip()


def build_readme() -> str:
    parts = []
    parts.append("# Bing 每日壁纸 - UHD 中文")
    parts.append("")
    parts.append("🚀 [bingmen/bing-UHD-cn](https://github.com/bingmen/bing-UHD-cn)")
    parts.append("")
    parts.append("## 简介")
    parts.append("")
    parts.append(
        "👀 自动抓取 Bing 每日壁纸（中国地区），存储 UHD 和 320×240 格式，"
        "后者作为略缩图形成归档汇总表格。"
    )
    parts.append("")
    parts.append("## 归档")
    parts.append("")

    for year in YEARS:
        emoji = EMOJI[year]
        parts.append(
            f"### {emoji} [{year}](https://uhdcn.bingmen.com/bing-UHD-cn-{year}.html)"
        )
        parts.append("")
        items = random_items(year)
        parts.append(render_table(items))
        parts.append("")

    parts.append("## 🗂️ 目录")
    parts.append("")
    parts.append("- 📄 数据：bing-JSON-cn-{year}")
    parts.append("- 🖼️ 略缩图：bing-320-cn-{year}")
    parts.append("- 🎞️ 高清图：bing-UHD-cn-{year}")
    parts.append("")
    parts.append("## 📚 参考")
    parts.append("")
    parts.append("- [Bing-Wallpaper-Action 公开API](https://bing-wallpaper.apifox.cn/)")
    parts.append("")
    parts.append("## 📄 许可证")
    parts.append("")
    parts.append("[MIT](LICENSE)")
    parts.append("")

    return "\n".join(parts)


def main():
    random.seed()  # 每次运行都不同；如需可复现可固定种子
    content = build_readme()
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"已生成 {OUTPUT.resolve()}")

    shutil.copyfile(OUTPUT, README)
    print(f"已复制为 {README.resolve()}")


if __name__ == "__main__":
    main()
