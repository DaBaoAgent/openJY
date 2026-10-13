"""就医引流后期器 —— `out/*.mp4` → 外文字幕 + BGM → `video/*_final.mp4`（Phase A2c）。

宝哥的产线分工（2026-10-12 定）：
  ① 我出提示词包（tools/jiuyi_prompts.py → 仓库根的 prompts/）；
  ② 宝哥在 Seedance 出片，丢进仓库根的 out/；
  ③ 本工具逐条：转写(按项目语言) → 自动识别台词包 → 烧外文字幕（无标点 + 卖点词高亮 +
     Noto Sans SC）+ BGM 铺底 → 写仓库根的 video/<stem>_final.mp4 供终审。

字幕语言随台词包（`language` 字段，现为 es；无包时用 settings.script.language），卖点词高亮
按语言选表（es→ES_HIGHLIGHT_WORDS / 其它→EN_HIGHLIGHT_WORDS）。
一条视频**只转写一次**（lib.post.transcript canonical），字幕时间全部来自它，绝不重推。
不出片、不发布、不碰 spec —— 纯免费后期。

用法
  python tools/jiuyi_finish.py                            # 处理 out/ 全部 mp4
  python tools/jiuyi_finish.py --only "生成竖屏口播视频.mp4"  # 只处理指定文件
  python tools/jiuyi_finish.py --pack jiuyi_es_m2_habitacion_01   # 强制指定台词包（跳过自动识别）
  python tools/jiuyi_finish.py --asr-lines                # 按实际转写文本烧字幕（不匹配台词包）
  python tools/jiuyi_finish.py --dry                       # 只转写+匹配+打印，不烧字幕/不落盘

`--asr-lines` 用于**不是由提示词包生成**的视频（如宝哥的测试片）：不拿包台词改稿，直接烧
转写出来的原话（时间仍来自 canonical），卖点词高亮照旧。默认不开 —— 默认口径是「匹配不上就
不猜、要求 --pack」，只有显式加此开关才用 ASR 原话。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
_S5 = ROOT / "s5_compose"
if str(_S5) not in sys.path:
    sys.path.insert(0, str(_S5))       # burn_subtitles 不是包，靠 path 注入导入（与 transcript.split_line 同法）

from lib.post import transcript as T                       # noqa: E402
from lib.post.audio_director import select_bgm             # noqa: E402
from lib.post import loudness as L                         # noqa: E402
from lib.tools import ffmpeg                               # noqa: E402
import burn_subtitles as BS                                # noqa: E402

# 交接目录 = 仓库根下的 prompts/out/video，自解析、不写死本机路径
DEFAULT_OUT = ROOT / "out"
DEFAULT_VIDEO = ROOT / "video"
DEFAULT_PROMPTS = ROOT / "prompts"
WORK_DIRNAME = "_work"
MATCH_THRESHOLD = 0.55        # 低于此分：不猜，标注「未匹配，需人工 --pack 指定」
BGM_GAIN = 0.20               # 与 tools/audio_polish.py 同口径
BGM_GENRE = "G7"             # 就医题材：calm/neutral 低能量 profile


def _norm(text: str) -> str:
    """匹配用归一：小写 + 只留字母数字 + 空白折叠（去标点/大小写差异）。"""
    keep = [c.lower() if c.isalnum() else " " for c in (text or "")]
    return " ".join("".join(keep).split())


def load_packs(prompts_dir: Path) -> list[dict]:
    idx = Path(prompts_dir) / "_index.json"
    if not idx.is_file():
        raise FileNotFoundError(
            f"找不到提示词清单 {idx} —— 先跑 tools/jiuyi_prompts.py emit 生成")
    data = json.loads(idx.read_text(encoding="utf-8"))
    return [p for p in (data.get("packs") or []) if isinstance(p, dict) and p.get("id")]


def match_pack(spoken: str, packs: list[dict]) -> tuple[dict | None, float, list[tuple[float, dict]]]:
    """转写文本 ↔ 各台词包：按归一文本相似度打分 → (最佳包, 分数, 全部排序候选)。"""
    hyp = _norm(spoken)
    scored: list[tuple[float, dict]] = []
    for p in packs:
        exp = _norm(" ".join(str(x) for x in (p.get("lines") or [])))
        score = SequenceMatcher(None, exp, hyp, autojunk=False).ratio()
        scored.append((round(score, 4), p))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return None, 0.0, []
    best_score, best = scored[0]
    return best, best_score, scored


def english_rows(tr: T.CanonicalTranscript, lines: list[str], *, max_chars: int,
                 gap: float = 0.03) -> list[tuple[float, float, str]]:
    """台词 → 英文字幕行：时间来自 canonical `align_spans`，断行按**词**（不切单词）。

    与 transcript.rows_from_spans 的区别只在断行函数（这里是 `_split_words`，中文那条
    是 `_split_natural`）—— 避免英文被按字符硬切、避免无谓的中文数字转换。
    """
    spans = T.align_spans(tr, lines)
    rows: list[tuple[float, float, str]] = []
    for (a, b), line in zip(spans, lines, strict=False):
        chunks = BS._split_words(line, max_chars)
        total = sum(len(c) for c in chunks) or 1
        t = a
        for c in chunks:
            share = (b - a) * len(c) / total
            rows.append((round(t, 3), round(t + share, 3), c))
            t += share
    out: list[tuple[float, float, str]] = []
    for i, (a, b, txt) in enumerate(rows):
        a2, b2 = a, b
        if i and a2 < out[-1][1] + gap:
            a2 = round(out[-1][1] + gap, 3)
        if b2 - a2 < 0.3:              # 单行太短看不清（拆行后按比例分到的碎时长）
            b2 = round(a2 + 0.3, 3)
        out.append((a2, b2, txt))
    return out


def bgm_under(sub_video: Path, out_path: Path, bgm: Path, work_dir: Path) -> dict:
    """BGM 垫底（sidechain 让路给人声）→ 母线实测 → 拉响度 + 限幅；**视频流 copy**。

    与 tools/audio_polish.py / make_15s._mix_sfx 共用 lib.post.loudness 的
    master_for_mix（一套阈值、一次实测），不另造口径。
    """
    inputs = [ffmpeg(), "-y", "-i", str(sub_video)]
    fc = ["[0:a]anull[v0]"]
    inputs += ["-stream_loop", "-1", "-i", str(bgm)]
    fc.append(f"[1:a]volume={BGM_GAIN}[bg]")
    fc.append("[bg][v0]sidechaincompress=threshold=0.03:ratio=6:attack=80:release=350[bgd]")
    mix = "[v0][bgd]amix=inputs=2:duration=first:normalize=0"
    wav = work_dir / f"{out_path.stem}_premaster.wav"
    # tp=-2.0：alimiter 的样点峰值定 -2.0，给真峰值（过采样）留 ~0.6dB 余量，
    # 使成片 dBTP 落在 TRUE_PEAK_MAX(-1.0) 之内（Seedance 源音轨本身偏响）。
    master, _pre = L.master_for_mix(inputs, ";".join(fc + [mix]), wav, tp=-2.0)
    if wav.exists():
        wav.unlink()
    cmd = inputs + ["-filter_complex", ";".join(fc + [f"{mix},{master}[aout]"]),
                    "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"BGM 混音失败: {r.stderr[-400:]}")
    return L.measure(out_path)      # 量**成片**（母线之后），不是未过母线的 pre-master


def recent_bgm(video_dir: Path) -> set[str]:
    """历史已用 BGM 名（AudioDirector 的防重复惩罚项，不是唯一逻辑）。"""
    log = Path(video_dir) / "_finish_log.json"
    if not log.is_file():
        return set()
    try:
        data = json.loads(log.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {str(v.get("bgm")) for v in data.values() if isinstance(v, dict) and v.get("bgm")}


def _write_log(video_dir: Path, stem: str, entry: dict) -> None:
    log = Path(video_dir) / "_finish_log.json"
    data: dict = {}
    if log.is_file():
        try:
            data = json.loads(log.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
    data[stem] = entry
    Path(video_dir).mkdir(parents=True, exist_ok=True)
    log.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def process(video: Path, *, packs: list[dict], video_dir: Path, work_root: Path,
            settings, pack_id: str = "", asr_lines: bool = False, dry: bool = False) -> bool:
    stem = video.stem
    work = Path(work_root) / stem
    work.mkdir(parents=True, exist_ok=True)
    max_chars = int(settings.compose.subtitle.max_chars_per_line)

    print("=" * 78)
    print(f"▶ {video.name}")

    # 1) 唯一 ASR（canonical，命中缓存不重推）
    tr, reused = T.ensure(video, workspace=work, model=settings.asr.model,
                          language=settings.asr.language)
    print(f"  ASR {'↻ 复用' if reused else '🎧 新转写'}（{tr.model}/{tr.language}"
          f"）｜{len(tr.segments)} 段 / {tr.char_count} 字 / 指纹 {tr.fingerprint()}")
    print(f"  转写：{tr.text.strip()[:160]}")

    # 2) 定台词：强制包 / 自动识别 / 直接烧 ASR 原话
    pack_name = ""
    lang = str(settings.script.language or "en")     # 无包时（--asr-lines）按项目语言
    if asr_lines:
        lines = [s.text.strip() for s in tr.segments if s.text.strip()]
        if not lines:
            print("  ✗ --asr-lines：转写为空 → 跳过")
            return False
        print(f"  台词：--asr-lines → 按**实际转写文本**烧字幕（不匹配台词包；lang={lang}）")
    elif pack_id:
        pack = next((p for p in packs if p["id"] == pack_id), None)
        if pack is None:
            print(f"  ✗ --pack {pack_id} 不在 _index.json 里 → 跳过")
            return False
        print(f"  匹配：强制指定 {pack_id}")
        lines = [str(x) for x in (pack.get("lines") or [])]
        pack_name = pack["id"]
        lang = str(pack.get("language") or "en")
    else:
        pack, score, ranked = match_pack(tr.text, packs)
        if not pack:
            print("  ✗ 提示词清单为空 → 跳过")
            return False
        top = ", ".join(f"{s:.2f}·{p['id']}" for s, p in ranked[:3])
        print(f"  匹配：{pack['id']}（{pack['title']}）｜置信度 {score:.2f}｜候选 {top}")
        if score < MATCH_THRESHOLD:
            print(f"  ⚠ 置信度 {score:.2f} < {MATCH_THRESHOLD} → **不猜**：请人工核对，"
                  f"用 --pack <id> 指定，或加 --asr-lines 按实际转写烧字幕。")
            return False
        lines = [str(x) for x in (pack.get("lines") or [])]
        pack_name = pack["id"]
        lang = str(pack.get("language") or "en")

    print(f"  台词 {len(lines)} 句：")
    for i, ln in enumerate(lines, 1):
        print(f"     {i}. {ln}")

    # 3) 英文字幕行（时间来自 canonical）
    rows = english_rows(tr, lines, max_chars=max_chars)
    print(f"  字幕 {len(rows)} 行（≤{max_chars} 字符/行，无标点，卖点词高亮）：")
    for a, b, txt in rows:
        print(f"     [{a:5.2f}-{b:5.2f}] {txt}")

    if dry:
        print("  (dry) 未烧字幕、未混 BGM、未落盘")
        return True

    # 4) 烧字幕（语言随台词包；卖点词高亮按语言选表）→ 工作目录
    sub = work / f"{stem}_sub.mp4"
    hl = BS.ES_HIGHLIGHT_WORDS if lang == "es" else BS.EN_HIGHLIGHT_WORDS
    BS.burn_rows(video, rows, lang=lang, highlight=hl, out=sub, work_dir=work)

    # 5) BGM 垫底 → video/<stem>_final.mp4
    track, rationale = select_bgm(genre=BGM_GENRE, recent=recent_bgm(video_dir))
    final = Path(video_dir) / f"{stem}_final.mp4"
    Path(video_dir).mkdir(parents=True, exist_ok=True)
    if track is None:
        print(f"  ⚠ 曲库为空（{rationale.get('error')}）→ 只出字幕版，BGM 跳过")
        final.write_bytes(sub.read_bytes())
        bgm_name = ""
    else:
        print(f"  🎵 BGM：{track.name}（mood={track.mood} energy={track.energy}"
              f"｜genre={BGM_GENRE}｜score={rationale.get('score')}）")
        measured = bgm_under(sub, final, Path(track.path), work)
        print(f"  响度：{L.summarize(measured)}")
        bgm_name = track.name

    size = final.stat().st_size if final.is_file() else 0
    print(f"  ✓ 成片：{final}（{size/1024/1024:.2f} MB）")
    _write_log(Path(video_dir), stem, {"pack": pack_name, "bgm": bgm_name,
                                       "rows": len(rows), "final": str(final)})
    return True


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="jiuyi_finish",
                                 description="就医引流后期器（外文字幕 + BGM）")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT), help=f"输入 mp4 目录（默认 {DEFAULT_OUT}）")
    ap.add_argument("--video-dir", default=str(DEFAULT_VIDEO),
                    help=f"成片输出目录（默认 {DEFAULT_VIDEO}）")
    ap.add_argument("--prompts", default=str(DEFAULT_PROMPTS),
                    help=f"提示词包目录（默认 {DEFAULT_PROMPTS}）")
    ap.add_argument("--only", default="", help="只处理该文件名（如 生成竖屏口播视频.mp4）")
    ap.add_argument("--pack", default="", help="强制指定台词包 id（跳过自动识别）")
    ap.add_argument("--asr-lines", action="store_true",
                    help="按实际转写文本烧字幕（不匹配台词包；用于非包生成的视频）")
    ap.add_argument("--dry", action="store_true", help="只转写+匹配+打印，不烧字幕/不落盘")
    args = ap.parse_args(argv)

    from lib.settings import get_settings
    settings = get_settings()

    out_dir, video_dir, prompts_dir = Path(args.out_dir), Path(args.video_dir), Path(args.prompts)
    packs = load_packs(prompts_dir)
    vids = sorted(p for p in out_dir.glob("*.mp4") if not p.name.startswith("_"))
    if args.only:
        vids = [p for p in vids if p.name == args.only]
    print(f"就医引流后期器 ｜ out={out_dir} → video={video_dir} ｜ 提示词包 {len(packs)} 个"
          f" ｜ ASR {settings.asr.model}/{settings.asr.language}"
          f"{' ｜ DRY' if args.dry else ''}")
    if not vids:
        print(f"✗ {out_dir} 里没有可处理的 mp4" + (f"（--only {args.only}）" if args.only else ""))
        return 1

    ok, fail = 0, 0
    for v in vids:
        try:
            if process(v, packs=packs, video_dir=video_dir, work_root=out_dir / WORK_DIRNAME,
                       settings=settings, pack_id=args.pack, asr_lines=args.asr_lines,
                       dry=args.dry):
                ok += 1
            else:
                fail += 1
        except Exception as exc:      # noqa: BLE001 - 单条失败不拖垮整批
            print(f"  ✗ 处理失败：{type(exc).__name__}: {exc}")
            fail += 1
    print("=" * 78)
    print(f"完成：{ok} 条成功 / {fail} 条跳过或失败" + (f" ｜ 成片目录 {video_dir}" if not args.dry else ""))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
