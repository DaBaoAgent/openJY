"""选题器（openJY 精简版）——从词表轮换里给出一个「角度 + 片型 + 卖点」组合。

刻意**不依赖**任何旧的「策划/评分」机器（Planner / Director / Scorer / Prescreen
随付费出片路径一并删除）：这里只有三件事 —— 词表轮换 + Claims Registry 事实 +
本地调研库摘要。用 `--commit <tag>` 把本组合记入已用表，下一条就不会再撞。

  python tools/jiuyi_select.py                  # 出一个候选组合 + 调研摘要
  python tools/jiuyi_select.py --commit es_001  # 记录本组合已用（tag = 视频名/序号）
  python tools/jiuyi_select.py --list           # 列出三个池子 + 已用次数
  python tools/jiuyi_select.py --json           # 机器可读
  python tools/jiuyi_select.py --lang es        # 语言标签（仅进记录/输出，默认取配置）

产出是给「出提示词」阶段用的**选题卡**：宝哥据此写/挑 Seedance 提示词包
（lib/jiuyi/catalog*.py），或直接用 lib/jiuyi 渲染。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib import angles as angles_mod           # noqa: E402
from lib import genres as genres_mod           # noqa: E402
from lib import products as products_mod       # noqa: E402
from lib.console import enable_utf8_console    # noqa: E402
from lib.creative_research import build_research_brief  # noqa: E402

enable_utf8_console()


def _lang_default() -> str:
    try:
        from lib.settings import get_settings

        return str(getattr(get_settings().script, "language", "es") or "es").lower()
    except Exception:                          # noqa: BLE001 —— 配置不可用时退回 es
        return "es"


def pick() -> dict:
    """选一个组合：未用过的角度 + 使用最少的片型 + 使用最少的可用卖点。"""
    angle = angles_mod.next_angle()
    genre = genres_mod.next_genre()
    point = products_mod.next_point()
    facts = products_mod.point_facts(point["id"], "script")
    try:
        brief = build_research_brief()
    except RuntimeError as exc:
        brief = {"error": str(exc)}
    return {"angle": angle, "genre": genre, "point": point,
            "point_facts": facts, "brief": brief}


def commit(combo: dict, tag: str) -> None:
    angles_mod.record_angle(combo["angle"]["id"], tag)
    genres_mod.record_genre(combo["genre"]["id"], tag)
    products_mod.record_point(combo["point"]["id"], tag)


def _print_card(combo: dict, lang: str) -> None:
    a, g, p = combo["angle"], combo["genre"], combo["point"]
    print("── 选题卡 ─────────────────────────────")
    print(f"  语言    : {lang}")
    print(f"  角度    : {a['id']} {a['name']} — {a['dir']}")
    print(f"  片型    : {g['id']} {g['name']} — {g['dir']}（约 {g.get('shots', '?')} 镜）")
    print(f"  主打卖点: {p['id']} {p['name']}")
    if combo["point_facts"]:
        print("  卖点事实:")
        for line in str(combo["point_facts"]).splitlines():
            print(f"      {line}")
    brief = combo.get("brief") or {}
    if brief.get("error"):
        print(f"  调研    : ⚠ 知识库不完整 — {brief['error']}")
    elif brief.get("hotspot"):
        hot = brief["hotspot"]
        print(f"  调研选题: [{hot.get('platform', '?')}] {hot.get('title', '')}")
        for rel in brief.get("related_topics", [])[:3]:
            print(f"            · {rel.get('title', '')}")
    print("  已用提醒: " + (products_mod.points_block() or "（无历史，首条）"))
    print("──────────────────────────────────────")


def show_list() -> None:
    ac, gc, pc = angles_mod.use_counts(), genres_mod.used_count(), products_mod.use_counts()
    print("角度池：")
    for a in angles_mod.ANGLES:
        flag = "（已耗尽）" if a.get("used_up") else f"（已用 {ac[a['id']]} 次）"
        print(f"  {a['id']:>4} {a['name']} {flag}")
    print("\n片型池：")
    for g in genres_mod.GENRES:
        print(f"  {g['id']:>4} {g['name']}（已用 {gc[g['id']]} 次）")
    print("\n卖点池：")
    for p in products_mod.SALES_POINTS:
        tag = "" if p.get("usable") else f"  ⚠ 不可用：{p.get('blocked', '')}"
        print(f"  {p['id']:<18} {p['name']}（已用 {pc.get(p['id'], 0)} 次）{tag}")


def main() -> int:
    ap = argparse.ArgumentParser(description="选题器：角度 + 片型 + 卖点（词表轮换）")
    ap.add_argument("--commit", default="", help="记录本组合已用（tag = 视频名/序号）")
    ap.add_argument("--list", action="store_true", help="列出三个池子与已用次数")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    ap.add_argument("--lang", default="", help="语言标签（默认取配置 script.language）")
    args = ap.parse_args()

    lang = (args.lang or _lang_default()).lower()

    if args.list:
        show_list()
        return 0

    combo = pick()
    if args.commit:
        commit(combo, args.commit)

    if args.json:
        print(json.dumps({"lang": lang, "committed": args.commit, **combo},
                         ensure_ascii=False, indent=1))
    else:
        _print_card(combo, lang)
        if args.commit:
            print(f"✓ 已记录使用（tag={args.commit}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
