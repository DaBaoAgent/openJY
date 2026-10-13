"""Seedance 文生视频提示词包 —— 数据契约 + 渲染 + 校验。

一条「提示词包」= 宝哥在 Seedance 里出片所需的**全部信息**：人物 / 场景 / 机位 /
表演 / 口播台词 / 音色 / 环境声 / 干净度 / 负向词 + 时长与画幅。`render()` 把它拼成
一段可直接粘贴的提示词；`validate()` 用**和产线同一套口径**把不合格的包拦下（花钱前）。

预算口径（speech_units）：拉丁词按「词 × 2 单位」（重音字母算词内）、数字按 ×2；
去 0.6s 起句留白后按语速档铺满整条。
语速档**按语言分**（LANG_PROFILES）：en 5.0–5.6、es 5.6–6.2 单位/秒。
10s 档 → en = 47~52 单位；es = 52~58 单位。

2026-10-12 宝哥口径：口播**稍快、连续、中途不许停顿**，一条连贯说完；2026-10-13 追加
「西语再快一点」—— 因此 es 档整体比 en 高一档，且 render() 里固定追加 DELIVERY 段把
语速/连贯要求写死，避免只改台词却没让模型「说得更密更顺」。

医疗红线（报告 §7.3/§9）：不得承诺疗效/治愈、不得用绝对化用语（最好/第一/唯一/100%）、
不得写具体报价。这里对台词与正文做静态扫描，命中即拒绝。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

DEFAULT_DURATION = 10
ASPECT = "9:16"
LEAD_IN_SECONDS = 0.6
DEFAULT_LANGUAGE = "en"
# 语速档（单位/秒）**按语言分**：宝哥 2026-10-13 要求西语「再快一点」——西语语流本就密，
# 所以 es 的上下限整体比 en 高一档。10s 档：en = 47~52 单位，es = 52~58 单位（≈26~29 词）。
LANG_PROFILES: dict[str, dict] = {
    "en": {"units_per_sec": (5.0, 5.6), "name": "English",
           "delivery": "speaks a little faster than normal"},
    "es": {"units_per_sec": (5.6, 6.2), "name": "Spanish",
           "delivery": ("speaks noticeably faster than normal, with lively, "
                        "flowing Latin rhythm and clear articulation")},
}

# 医疗红线（大小写不敏感）；命中即 ERROR。这些是最容易在英文稿里溜进来的绝对化/疗效词。
FORBIDDEN_PATTERNS: tuple[tuple[str, str], ...] = (
    ("疗效/治愈承诺", r"\b(cure|cures|cured|curing|heal|heals|healed|guarantee[ds]?|guaranteed?)\b"),
    ("绝对化用语", r"\b(best|number one|#\s*1|no\.\s*1|the only|world[- ]class|top[- ]tier)\b"),
    ("无痛/零风险", r"\b(painless|risk[- ]free|no risk|zero risk|100\s*%|completely safe)\b"),
    ("具体报价/折扣", r"\b(\$\s*\d|usd\s*\d|discount|cheapest|lowest price)\b"),
)

# 西语医疗红线（口语短句里最容易溜进来的绝对化/疗效/报价词）。与英文表**分开维护**，
# 扫描时两张表都过（英文表不会误伤西语、西语表不会误伤英文，代价只是多几次正则）。
FORBIDDEN_PATTERNS_ES: tuple[tuple[str, str], ...] = (
    ("疗效/治愈承诺",
     r"\b(cura|curaci[oó]n|curar|curado|sanar|sanaci[oó]n|garantiz\w*|sanado)\b"),
    ("绝对化用语",
     r"(el mejor|la mejor|los mejores|las mejores|n[uú]mero uno|el [uú]nico|la [uú]nica|"
     r"de primera categor[ií]a|#\s*1|n[oº]\.?\s*1|100\s*%)"),
    ("无痛/零风险",
     r"\b(sin dolor|indolor\w*|sin riesgo|riesgo cero|totalmente seguro|completamente seguro)\b"),
    ("具体报价/折扣",
     r"(\$\s*\d|\bdescuento\b|\bm[aá]s barato\b|\bprecio m[aá]s bajo\b|\boferta\b)"),
)


def unit_budget(duration: int = DEFAULT_DURATION, language: str = DEFAULT_LANGUAGE) -> tuple[int, int]:
    """本条时长的台词单位预算 [low, high]（en 10s → 47~52；es 10s → 52~58）。"""
    lo, hi = LANG_PROFILES.get(language, LANG_PROFILES[DEFAULT_LANGUAGE])["units_per_sec"]
    avail = max(0.0, float(duration) - LEAD_IN_SECONDS)
    return int(avail * lo), int(avail * hi)


_LATIN_WORD = r"[A-Za-z\u00C0-\u024F]+"     # 含 Latin-1 重音（español/así/médico）


def speech_units(text: str) -> int:
    """语速单位数：汉字按字、拉丁词×2（重音算词内）、数字×2。"""
    s = str(text or "")
    return (len(re.findall(r"[\u3400-\u9fff]", s))
            + len(re.findall(_LATIN_WORD, s)) * 2
            + len(re.findall(r"[0-9]+", s)) * 2)


def word_count(text: str) -> int:
    return len(re.findall(_LATIN_WORD, str(text or "")))


def redline_hits(text: str) -> list[str]:
    """返回命中的红线标签（空 = 干净）。英文表 + 西语表都过一遍。"""
    hits: list[str] = []
    s = str(text or "")
    for label, pattern in (*FORBIDDEN_PATTERNS, *FORBIDDEN_PATTERNS_ES):
        if re.search(pattern, s, re.IGNORECASE):
            hits.append(label)
    return hits


@dataclass
class PromptPack:
    """一条 Seedance 提示词包（全部字段都是给生成器看的英文字面描述）。"""

    id: str
    angle: str                       # M1..M6（lib/angles.py 的就医思路）
    person: str                      # 人物形象
    scene: str                       # 场景
    camera: str                      # 机位/运动（必须含 handheld + walk）
    performance: str                 # 表演/口播方式（必须含 lip-sync 语义）
    mode: str = "direct-to-camera talking head with accurate lip-sync"
    lines: list[str] = field(default_factory=list)
    voice: str = "their own natural voice, clear English, slightly faster and fluid, continuous"
    ambient: str = "quiet hospital room tone, faint distant footsteps; no music"
    clean: str = "no on-screen text or subtitles, no watermark, no logos, no UI overlays"
    negative: str = ("no extra people, no distorted hands, no lip desync, no captions, "
                     "no watermark, no floating text")
    duration: int = DEFAULT_DURATION
    aspect: str = ASPECT
    title: str = ""
    language: str = DEFAULT_LANGUAGE     # "en" / "es"；决定语速档、渲染语言与红线表

    # ── 派生量 ──────────────────────────────────────────────
    @property
    def units(self) -> int:
        return sum(speech_units(line) for line in self.lines)

    @property
    def words(self) -> int:
        return sum(word_count(line) for line in self.lines)

    def to_dict(self) -> dict:
        return {
            "id": self.id, "angle": self.angle, "title": self.title,
            "person": self.person, "scene": self.scene, "camera": self.camera,
            "performance": self.performance, "mode": self.mode,
            "lines": list(self.lines), "voice": self.voice, "ambient": self.ambient,
            "clean": self.clean, "negative": self.negative,
            "duration": self.duration, "aspect": self.aspect,
            "units": self.units, "words": self.words,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PromptPack:
        return cls(
            id=str(d.get("id") or ""), angle=str(d.get("angle") or ""),
            person=str(d.get("person") or ""), scene=str(d.get("scene") or ""),
            camera=str(d.get("camera") or ""), performance=str(d.get("performance") or ""),
            mode=str(d.get("mode") or "direct-to-camera talking head with accurate lip-sync"),
            lines=[str(x) for x in (d.get("lines") or [])],
            voice=str(d.get("voice") or ""), ambient=str(d.get("ambient") or ""),
            clean=str(d.get("clean") or ""), negative=str(d.get("negative") or ""),
            duration=int(d.get("duration") or DEFAULT_DURATION),
            aspect=str(d.get("aspect") or ASPECT), title=str(d.get("title") or ""),
            language=str(d.get("language") or DEFAULT_LANGUAGE),
        )


def render(pack: PromptPack) -> str:
    """拼成一段可直接粘贴给 Seedance 的文生视频提示词。

    正文用英文给生成器下指令（Seedance 对英文指令最稳），但 DIALOGUE 的语言/语速、
    DELIVERY 的语速口径由 `pack.language` 决定：en=稍快（宝哥 2026-10-12），
    es=更快、更有拉美语流（宝哥 2026-10-13「再快一点」）。台词本身照原样给出。
    """
    prof = LANG_PROFILES.get(pack.language, LANG_PROFILES[DEFAULT_LANGUAGE])
    lang_name = prof["name"]
    lines_block = "\n".join(f'  "{ln}"' for ln in pack.lines)
    return (
        f"{pack.duration}-second {pack.aspect} vertical video (single continuous take).\n\n"
        f"PERSON: {pack.person}\n"
        f"SCENE: {pack.scene}\n"
        f"CAMERA: {pack.camera}\n"
        f"PERFORMANCE: {pack.performance} ({pack.mode}).\n"
        f"DELIVERY: {prof['delivery']}, in ONE continuous, uninterrupted "
        f"flow from the very first word to the very last — no pauses or gaps between "
        f"sentences, no ~0.2-second hesitation, no dead air, no breath-holding the middle. "
        f"The whole script is delivered seamlessly as a single complete talking-take.\n\n"
        f"DIALOGUE (spoken in clear, natural {lang_name}, back-to-back with no breaks; the "
        f"person's lips articulate every word for perfect lip-sync; no on-screen text):\n"
        f"{lines_block}\n\n"
        f"VOICE: {pack.voice}\n"
        f"AMBIENT: {pack.ambient}\n"
        f"CLEAN PLATE: {pack.clean}\n"
        f"NEGATIVE: {pack.negative}\n"
    )


def validate(pack: PromptPack) -> list[str]:
    """不合格问题清单（空 = 可出片）。口径与产线一致，花钱前拦。"""
    problems: list[str] = []
    if not pack.id:
        problems.append("缺少 id")
    if not pack.lines:
        problems.append("没有台词")
        return problems

    low, high = unit_budget(pack.duration, pack.language)
    units = pack.units
    if not (low <= units <= high):
        problems.append(f"台词量 {units} 单位，要求 {low}-{high}"
                        f"（{pack.duration}s / {pack.language} 按语速档铺满、一条连贯无停顿）")

    for i, line in enumerate(pack.lines, 1):
        if re.search(r"[0-9]", line):
            problems.append(f"第 {i} 句含阿拉伯数字：「{line}」→ 改写成英文读法")
        if re.search(r"[\u3400-\u9fff]", line):
            problems.append(f"第 {i} 句夹了中文：「{line}」")

    text = "\n".join([*pack.lines, pack.person, pack.scene, pack.performance, pack.clean])
    for label in redline_hits(text):
        problems.append(f"命中医疗红线「{label}」")

    if pack.angle not in {"M1", "M2", "M3", "M4", "M5", "M6"}:
        problems.append(f"angle「{pack.angle}」不在 M1-M6")

    cam = pack.camera.lower()
    if "handheld" not in cam:
        problems.append("camera 缺少 handheld（宝哥要求手持手机机位）")
    if "walk" not in cam and "walk" not in pack.performance.lower():
        problems.append("camera/performance 缺少 walk（人物边走边说话）")
    if "lip" not in pack.mode.lower():
        problems.append("mode 缺少 lip-sync（要直接口播对嘴型）")

    clean_all = (pack.clean + " " + pack.negative).lower()
    if "watermark" not in clean_all:
        problems.append("clean/negative 缺少 no watermark（画面不要平台水印）")
    if "text" not in clean_all and "subtitles" not in clean_all:
        problems.append("clean/negative 缺少 no on-screen text（字幕由后期烧，画面里不要自带字）")
    return problems
