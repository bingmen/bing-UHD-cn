# bing-UHD-cn-README-0.1.1.py
# github.com/shenjuexiao
# 20261024

# bing-UHD-cn-README.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
重新生成 Bing 每日壁纸 - UHD 中文 的 bing-UHD-cn-README.md 和 README.md
"""

import json
import random
import shutil
from datetime import date, datetime
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
ROWS = 1
TOTAL = COLS * ROWS
OUTPUT = Path("bing-UHD-cn-README.md")
README = Path("README.md")

# 每个年份对应的 JSON 数据文件
JSON_TEMPLATE = "bing-JSON-cn-{year}.json"


def load_items(year: int) -> list[dict]:
    """读取指定年份的 JSON 数据。"""
    path = Path(JSON_TEMPLATE.format(year=year))
    if not path.exists():
        print(f"警告：未找到 {path}，跳过 {year} 年")
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"警告：{path} 解析失败：{exc}")
        return []

    # 兼容两种结构：直接是 list，或 {"images": [...]} / {"data": [...]}
    if isinstance(data, dict):
        for key in ("images", "data", "items"):
            if isinstance(data.get(key), list):
                data = data[key]
                break

    if not isinstance(data, list):
        print(f"警告：{path} 不是列表结构，跳过 {year} 年")
        return []

    items = []
    for item in data:
        if not isinstance(item, dict):
            continue
        urlbase = item.get("urlbase")
        if not urlbase:
            continue
        items.append(item)
    return items


def parse_enddate(item: dict) -> date | None:
    """解析 JSON 中的 enddate，支持 YYYYMMDD 和 YYYY-MM-DD。"""
    raw = item.get("enddate")
    if not raw:
        return None
    raw = str(raw).strip()
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def random_items(year: int, count: int = TOTAL) -> list[dict]:
    """随机选取不重复条目，按 enddate 时间顺序排列。"""
    items = load_items(year)
    if not items:
        return []

    # 去重（按 urlbase），并过滤无法解析日期的条目
    seen = set()
    unique = []
    for item in items:
        key = item["urlbase"]
        if key in seen:
            continue
        d = parse_enddate(item)
        if d is None:
            continue
        seen.add(key)
        unique.append((d, item))

    if not unique:
        return []

    unique.sort(key=lambda x: x[0])
    count = min(count, len(unique))
    picked = random.sample(unique, count)
    picked.sort(key=lambda x: x[0])
    return [item for _, item in picked]


def item_urls(item: dict) -> tuple[str, str, str]:
    """返回 (thumb, uhd, fallback)。"""
    urlbase = item["urlbase"]
    thumb = "https://www.bing.com" + urlbase + "_320x240.jpg"
    uhd = "https://www.bing.com" + urlbase + "_UHD.jpg"
    fallback = "https://www.bing.com" + urlbase + "_1920x1080.jpg"
    return thumb, uhd, fallback


def item_title(item: dict) -> str:
    """获取标题，转义 Markdown 表格中的竖线。"""
    title = str(item.get("title") or "Bing 每日壁纸")
    return title.replace("|", "\\|").replace("\n", " ").strip()


def item_date(item: dict) -> str:
    d = parse_enddate(item)
    return d.strftime("%Y-%m-%d") if d else ""


def render_thumb_table(year: int, items: list[dict]) -> str:
    """生成 4×4 的日期/标题/缩略图表格（Markdown）。"""
    if not items:
        return "（暂无数据）"

    # 补齐到 TOTAL 个，避免表格不齐
    while len(items) < TOTAL:
        items.append(items[-1])

    lines = []
    for r in range(ROWS):
        row = items[r * COLS:(r + 1) * COLS]

        # 日期行
        date_cells = [item_date(item) for item in row]
        lines.append("| " + " | ".join(date_cells) + " |")

        # 分隔行（每组表格都带分隔行）
        lines.append("| " + " | ".join([":---:"] * COLS) + " |")

        # 标题链接行
        title_cells = []
        for item in row:
            title = item_title(item)
            _, uhd, fallback = item_urls(item)
            link = uhd if uhd else fallback
            title_cells.append(f"[{title}]({link})")
        lines.append("| " + " | ".join(title_cells) + " |")

        # 缩略图行
        thumb_cells = []
        for item in row:
            title = item_title(item)
            thumb, uhd, fallback = item_urls(item)
            link = uhd if uhd else fallback
            thumb_cells.append(f'[![{title}]({thumb})]({link})')
        lines.append("| " + " | ".join(thumb_cells) + " |")

        lines.append("")  # 空行分隔

    return "\n".join(lines).rstrip()


def build_readme() -> str:
    parts = []
    parts.append("# Bing 每日壁纸 - UHD 中文")
    parts.append("")
    parts.append(
        "🚀 [bingmen/bing-UHD-cn](https://github.com/bingmen/bing-UHD-cn)"
    )
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
        emoji = YEAR_EMOJI[year]
        parts.append(
            f"### {emoji} [{year}]"
            f"(https://uhdcn.bingmen.comn/bing-UHD-cn-{year}.html)"
        )
        parts.append("")
        items = random_items(year)
        parts.append(render_thumb_table(year, items))
        parts.append("")

    parts.append("## 🗂️ 目录")
    parts.append("")
    parts.append("- 📄 数据：bing-JSON-cn-{year}")
    parts.append("- 🖼️ 略缩图：bing-320-cn-{year}")
    parts.append("- 🎞️ 高清图：bing-UHD-cn-{year}")
    parts.append("")
    parts.append("## 📚 参考")
    parts.append("")
    parts.append(
        "- [Bing-Wallpaper-Action 公开API](https://bing-wallpaper.apifox.cn/)"
    )
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
    shutil.copyfile(OUTPUT, README)
    print(f"已生成 {OUTPUT.resolve()}")
    print(f"已复制为 {README.resolve()}")


if __name__ == "__main__":
    main()
