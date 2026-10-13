"""就医引流 Seedance 提示词包生成器。

把 lib/jiuyi/catalog.py 里手写的成品包**渲染 + 校验 + 落盘**，产出一批宝哥可以直接
粘贴进 Seedance 的完整提示词。全链免费、可复跑、不动 spec、不提交任何生成任务。

用法
  python tools/jiuyi_prompts.py emit                 # 出全部（en+es，默认写到仓库根的 prompts/）
  python tools/jiuyi_prompts.py emit --lang es       # 只出西语批 10 条
  python tools/jiuyi_prompts.py emit --count 5       # 只出前 5 条
  python tools/jiuyi_prompts.py emit --out "<目录>"  # 自定义输出目录
  python tools/jiuyi_prompts.py check                # 只校验、不落盘

产物（每条一个 .md = 纯提示词，可直接全选复制）：
  <out>/<id>.md          —— 粘贴用提示词（纯英文，无多余头尾）
  <out>/_index.json      —— 机器可读清单（后期器自动识别台词用）
  <out>/_index.md        —— 人看的对照表（id/角度/单位数/标题/首句）
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.jiuyi.catalog import CATALOG  # noqa: E402
from lib.jiuyi.catalog_es import CATALOG_ES  # noqa: E402
from lib.jiuyi.promptpack import PromptPack, render, unit_budget, validate  # noqa: E402

# en 批（catalog.py）+ es 批（catalog_es.py）合并；--lang 过滤。
ALL_PACKS: list[PromptPack] = [*CATALOG, *CATALOG_ES]

# 默认输出到仓库根下的 prompts/（自解析、不写死本机路径）
DEFAULT_OUT = ROOT / "prompts"


def _report(pack: PromptPack, problems: list[str]) -> str:
    low, high = unit_budget(pack.duration, pack.language)
    head = (f"  {'✓' if not problems else '✗'} {pack.id:<26} {pack.language}/{pack.angle} "
            f"｜{pack.units} 单位（{low}-{high}）｜{pack.words} 词｜"
            f"{len(pack.lines)} 句｜{pack.title}")
    if not problems:
        return head
    return head + "\n" + "\n".join(f"        - {p}" for p in problems)


def _index_row(pack: PromptPack) -> dict:
    return {
        "id": pack.id, "angle": pack.angle, "title": pack.title,
        "language": pack.language,
        "duration": pack.duration, "aspect": pack.aspect,
        "units": pack.units, "words": pack.words,
        "person": pack.person, "scene": pack.scene, "mode": pack.mode,
        "lines": list(pack.lines),
        "voice": pack.voice, "ambient": pack.ambient,
    }


def _select(args: argparse.Namespace) -> list[PromptPack]:
    pool = ALL_PACKS if args.lang == "all" else [p for p in ALL_PACKS if p.language == args.lang]
    n = int(args.count) if int(args.count) > 0 else len(pool)
    return pool[: max(1, n)]


def cmd_emit(args: argparse.Namespace) -> int:
    packs = _select(args)
    out_dir = Path(args.out)

    langs = sorted({p.language for p in packs})
    print("=" * 78)
    print(f"就医引流提示词包 ｜ 共 {len(packs)} 条 ｜ 语言 {','.join(langs)}"
          f"（--lang {args.lang}）｜ 输出目录 {out_dir}")
    print("=" * 78)

    checked: list[tuple[PromptPack, list[str]]] = [(p, validate(p)) for p in packs]
    bad = [p for p, problems in checked if problems]
    for pack, problems in checked:
        print(_report(pack, problems))

    if bad:
        print("-" * 78)
        print(f"✗ {len(bad)} 条未通过校验 → 拒绝落盘（先改 lib/jiuyi/catalog.py）")
        print("=" * 78)
        return 1

    if args.check:
        print("-" * 78)
        print("✓ 全部通过校验（--check：未落盘）")
        print("=" * 78)
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    for pack, _ in checked:
        (out_dir / f"{pack.id}.md").write_text(render(pack), encoding="utf-8")

    index = {
        "product": "China Medical Journey",
        "generated_by": "tools/jiuyi_prompts.py",
        "count": len(packs),
        "packs": [_index_row(p) for p, _ in checked],
    }
    (out_dir / "_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")

    table = ["| id | lang | angle | 单位 | 词 | 标题 | 首句 | 场景 |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for pack, _ in checked:
        table.append(f"| {pack.id} | {pack.language} | {pack.angle} | {pack.units} | "
                     f"{pack.words} | {pack.title} | "
                     f"{pack.lines[0] if pack.lines else ''} | {pack.scene} |")
    (out_dir / "_index.md").write_text("# 就医引流提示词包\n\n" + "\n".join(table) + "\n",
                                       encoding="utf-8")

    print("-" * 78)
    print(f"✓ 已写出 {len(packs)} 条：{out_dir}")
    print(f"   · <id>.md        —— 每条一个，纯提示词，直接复制粘贴进 Seedance")
    print(f"   · _index.json    —— 后期器自动识别台词用")
    print(f"   · _index.md      —— 对照表")
    print("=" * 78)
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="就医引流 Seedance 提示词包生成器")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--count", type=int, default=0,
                       help="取前 N 条（默认 0 = 该语言全部）")
        p.add_argument("--lang", default="all", choices=["all", "en", "es"],
                       help="语言过滤（默认 all = en 批 + es 批；es = 西语批）")
        p.add_argument("--out", default=str(DEFAULT_OUT), help=f"输出目录（默认 {DEFAULT_OUT}）")

    e = sub.add_parser("emit", help="渲染 + 校验 + 落盘")
    add_common(e)
    e.set_defaults(func=cmd_emit, check=False)

    c = sub.add_parser("check", help="只校验，不落盘")
    add_common(c)
    c.set_defaults(func=cmd_emit, check=True)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
