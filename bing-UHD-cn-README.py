# bing-UHD-cn-README-0.1.0.py
# github.com/shenjuexiao
# 20261023

# bing-UHD-cn-README.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重新生成 Bing 每日壁纸 - UHD 中文 的 README.md
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
OUTPUT_MAIN = Path("bing-UHD-cn-README.md")
OUTPUT_README = Path("README.md")

# Bing 官方 URL 前缀
BING_BASE = "https://www.bing.com"


def load_json_data(year: int) -> list[dict]:
    """读取指定年份的 JSON 数据文件。"""
    json_path = Path(f"bing-JSON-cn-{year}")
    if not json_path.is_dir():
        return []

    items = []
    for fp in sorted(json_path.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        # Bing API 返回结构通常为 {"images": [...]} 或直接是列表
        if isinstance(data, dict):
            data = data.get("images", [data])
        if isinstance(data, list):
            items.extend(data)
    return items


def pick_random_items(items: list[dict], count: int = TOTAL) -> list[dict]:
    """随机抽取不重复条目，按 enddate 时间排序。"""
    # 过滤掉缺少必要字段的条目
    valid = [it for it in items if it.get("urlbase") and it.get("enddate")]
    if not valid:
        return []

    count = min(count, len(valid))
    chosen = random.sample(valid, count)
    chosen.sort(key=lambda x: x["enddate"])
    return chosen


def build_urls(item: dict) -> tuple[str, str]:
    """返回 (缩略图 URL, 高清图 URL)。"""
    urlbase = item["urlbase"]
    thumb = BING_BASE + urlbase + "_320x240.jpg"
    uhd = BING_BASE + urlbase + "_UHD.jpg"
    return thumb, uhd


def format_date(enddate: str) -> str:
    """enddate 格式 YYYYMMDD → YYYY-MM-DD。"""
    if len(enddate) == 8 and enddate.isdigit():
        return f"{enddate[:4]}-{enddate[4:6]}-{enddate[6:]}"
    return enddate


def render_thumb_table(items: list[dict]) -> str:
    """生成 4×4 缩略图 + 日期表格（Markdown）。"""
    if not items:
        return "> 暂无数据\n"

    # 补齐到 TOTAL 个，避免表格不齐（用最后一项填充）
    while len(items) < TOTAL:
        items.append(items[-1])

    lines = []
    for r in range(ROWS):
        row = items[r * COLS:(r + 1) * COLS]

        # 缩略图行
        img_cells = []
        for it in row:
            thumb, uhd = build_urls(it)
            title = (it.get("title") or "").replace("|", "｜").replace("]", "】")
            img_cells.append(f"[![{title}]({thumb})]({uhd})")
        lines.append("| " + " | ".join(img_cells) + " |")

        # 对齐行
        lines.append("| " + " | ".join([":---:"] * COLS) + " |")

        # 日期行
        date_cells = [format_date(it["enddate"]) for it in row]
        lines.append("| " + " | ".join(date_cells) + " |")

    return "\n".join(lines)


def build_readme() -> str:
    parts = []
    parts.append("# Bing 每日壁纸 - UHD 中文\n")

    parts.append(
        "🚀 [bingmen/bing-UHD-cn](https://github.com/bingmen/bing-UHD-cn)\n"
    )

    parts.append("## 简介\n")
    parts.append(
        "👀 自动抓取 Bing 每日壁纸（中国地区），存储 UHD 和 320×240 格式，"
        "后者作为略缩图形成归档汇总表格。\n"
    )

    parts.append("## 归档\n")
    for year in YEARS:
        emoji = YEAR_EMOJI[year]
        parts.append(
            f"### {emoji} [{year}]"
            f"(https://uhdcn.bingmen.com/bing-UHD-cn-{year}.html)\n"
        )
        items = load_json_data(year)
        chosen = pick_random_items(items)
        parts.append(render_thumb_table(chosen))
        parts.append("")

    parts.append("## 🗂️ 目录\n")
    parts.append("- 📄 数据：bing-JSON-cn-{year}")
    parts.append("- 🖼️ 略缩图：bing-320-cn-{year}")
    parts.append("- 🎞️ 高清图：bing-UHD-cn-{year}\n")

    parts.append("## 📚 参考\n")
    parts.append(
        "- [Bing-Wallpaper-Action 公开API](https://bing-wallpaper.apifox.cn/)\n"
    )

    parts.append("## 📄 许可证\n")
    parts.append("[MIT](LICENSE)\n")

    return "\n".join(parts)


def main():
    random.seed()  # 每次运行随机；如需可复现可固定种子
    content = build_readme()
    OUTPUT_MAIN.write_text(content, encoding="utf-8")
    print(f"已生成 {OUTPUT_MAIN.resolve()}")

    # 复制一份为 README.md
    OUTPUT_README.write_text(content, encoding="utf-8")
    print(f"已生成 {OUTPUT_README.resolve()}")


if __name__ == "__main__":
    main()
