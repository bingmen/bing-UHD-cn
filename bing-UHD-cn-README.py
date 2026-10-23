# bing-UHD-cn-README-0.1.0.py
# github.com/shenjuexiao
# 20261023

# bing-UHD-cn-README.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成 Bing 每日壁纸 - UHD 中文 的 README.md
数据源：bing-JSON-cn-{year}.json
"""

import json
import random
from datetime import date
from pathlib import Path

# 配置
YEARS = [2026, 2025, 2024, 2023, 2022]
YEAR_EMOJI = {
    2026: "🐎",
    2025: "🐍",
    2024: "🐉",
    2023: "🐇",
    2022: "🐅",
}
COLS = 4
ROWS = 4
TOTAL = COLS * ROWS

JSON_DIR = Path(".")  # JSON 文件所在目录，按需修改
OUTPUT_ARCHIVE = Path("bing-UHD-cn-README.md")
OUTPUT_README = Path("README.md")

BING_BASE = "https://www.bing.com"


def load_json(year: int) -> list[dict]:
    """读取某年的 JSON 数据文件。"""
    path = JSON_DIR / f"bing-JSON-cn-{year}.json"
    if not path.exists():
        print(f"[警告] 未找到 {path}，跳过 {year} 年")
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # 兼容 { "images": [...] } 或直接是数组
    if isinstance(data, dict):
        data = data.get("images") or data.get("data") or []
    return data


def pick_items(items: list[dict], count: int = TOTAL) -> list[dict]:
    """随机抽取不重复条目，并按 enddate 升序排列。"""
    if not items:
        return []
    count = min(count, len(items))
    chosen = random.sample(items, count)
    chosen.sort(key=lambda x: x.get("enddate", ""))
    return chosen


def build_links(item: dict) -> tuple[str, str, str]:
    """返回 (缩略图URL, 点击跳转URL, 标题)。"""
    urlbase = item.get("urlbase", "")
    title = item.get("title", "").replace('"', "&quot;")
    thumb = f"{BING_BASE}{urlbase}_320x240.jpg"
    # 优先 UHD，回退 1920x1080
    if item.get("uhd") or True:  # urlbase 拼接约定，统一走 UHD，缺失时浏览器会 404
        target = f"{BING_BASE}{urlbase}_UHD.jpg"
    else:
        target = f"{BING_BASE}{urlbase}_1920x1080.jpg"
    return thumb, target, title


def render_thumb_table(items: list[dict]) -> str:
    """生成 4×4 略缩图 + 日期表格（Markdown）。"""
    if not items:
        return "_暂无数据_"

    # 补齐到 TOTAL 个，避免表格不齐（用最后一条重复填充）
    while len(items) < TOTAL:
        items.append(items[-1])

    lines = []
    for r in range(ROWS):
        row = items[r * COLS:(r + 1) * COLS]

        img_cells, date_cells = [], []
        for item in row:
            thumb, target, title = build_links(item)
            img_cells.append(
                f'<a href="{target}" target="_blank">'
                f'<img src="{thumb}" width="200" title="{title}" alt="{title}">'
                f'</a>'
            )
            date_cells.append(item.get("enddate", ""))

        lines.append("| " + " | ".join(img_cells) + " |")
        lines.append("| " + " | ".join(["---"] * COLS) + " |")
        lines.append("| " + " | ".join(date_cells) + " |")
        lines.append("")

    return "\n".join(lines).rstrip()


def build_archive() -> str:
    parts = []
    parts.append("# Bing 每日壁纸 - UHD 中文\n")

    parts.append("## 🚀 项目\n")
    parts.append("🔗 [bingmen/bing-UHD](https://github.com/bingmen/bing-UHD)\n")

    parts.append("## 😀 简介\n")
    parts.append(
        "👀 自动抓取 Bing 每日壁纸（中国地区），存储 UHD 和 320×240 格式，"
        "后者作为略缩图形成归档汇总表格。"
    )
    parts.append("")

    parts.append("## 🗂️ 归档\n")
    for year in YEARS:
        emoji = YEAR_EMOJI[year]
        parts.append(f"### {emoji} [{year}](bing-UHD-cn-{year}.md)")
        parts.append("")
        items = pick_items(load_json(year))
        parts.append(render_thumb_table(items))
        parts.append("")

    parts.append("## 📁️ 目录\n")
    parts.append("- 📄 数据：bing-JSON-cn-{year}/")
    parts.append("- 🖼️ 略缩图：bing-320-cn-{year}/")
    parts.append("- 🎞️ 高清图：bing-UHD-cn-{year}/")
    parts.append("")

    parts.append("## 📚 参考\n")
    parts.append("- [Bing-Wallpaper-Action 公开API](https://bing-wallpaper.apifox.cn/)")
    parts.append("")

    return "\n".join(parts)


def build_readme(archive_content: str) -> str:
    """根目录 README.md：项目说明 + 归档入口。"""
    parts = []
    parts.append("# Bing 每日壁纸 - UHD 中文\n")

    parts.append("## 🚀 项目\n")
    parts.append("🔗 [bingmen/bing-UHD](https://github.com/bingmen/bing-UHD)\n")

    parts.append("## 😀 简介\n")
    parts.append(
        "👀 自动抓取 Bing 每日壁纸（中国地区），存储 UHD 和 320×240 格式，"
        "后者作为略缩图形成归档汇总表格。"
    )
    parts.append("")

    parts.append("## 🗂️ 归档入口\n")
    for year in YEARS:
        emoji = YEAR_EMOJI[year]
        parts.append(f"- {emoji} [{year}](bing-UHD-cn-{year}.md)")
    parts.append("- 📜 [完整归档（含缩略图汇总）](bing-UHD-cn-README.md)")
    parts.append("")

    parts.append("## 📁️ 目录\n")
    parts.append("- 📄 数据：bing-JSON-cn-{year}/")
    parts.append("- 🖼️ 略缩图：bing-320-cn-{year}/")
    parts.append("- 🎞️ 高清图：bing-UHD-cn-{year}/")
    parts.append("")

    parts.append("## 📚 参考\n")
    parts.append("- [Bing-Wallpaper-Action 公开API](https://bing-wallpaper.apifox.cn/)")
    parts.append("")

    return "\n".join(parts)


def main():
    random.seed()  # 每次运行都不同；如需可复现可固定种子
    archive = build_archive()
    OUTPUT_ARCHIVE.write_text(archive, encoding="utf-8")
    print(f"已生成 {OUTPUT_ARCHIVE.resolve()}")

    readme = build_readme(archive)
    OUTPUT_README.write_text(readme, encoding="utf-8")
    print(f"已生成 {OUTPUT_README.resolve()}")


if __name__ == "__main__":
    main()
