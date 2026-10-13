"""产品卖点库 — 卖点池 + 卖点轮换（每条视频换主打）。

Phase 6：本文件**不再持有任何参数口径**。每个卖点的对外文案（`hook`）都实时来自
`assets/products/claims.yaml`（经 Claims Service）。参数只在 Claims Registry 里存在一份，
这里只保留"池成员 + 轮换状态 + 模板适配"这三件不属于事实层的事。
"""
import json
from pathlib import Path

from . import STATE_DIR
from . import claims as claims_mod

ROOT = Path(__file__).resolve().parent.parent
POINTS_DIR = ROOT / "assets" / "products"
STATE = STATE_DIR / "sales_points_used.json"

# ── 卖点池（就医引流：每条视频轮换主打服务点）──
# (point_id, 展示名)。文案一律从 claims registry 取，本表不写参数。
# point_id 与 claim_id 同名，故 POINT_CLAIMS 留空即默认一一对应。
_POINT_NAMES: list[tuple[str, str]] = [
    ("top_hospital", "对接三甲公立医院"),
    ("english_care", "全程英文接待"),
    ("cost_transparent", "费用透明可预估"),
    ("fast_track", "预约与排期协助"),
    ("travel_logistics", "签证住宿接送协助"),
    ("modern_tech", "先进诊疗设备"),
    ("recovery_env", "康复环境与陪护"),
    ("brand_cta", "品牌引导"),
]

# 卖点 id → 支撑它的 claim（一个卖点可由多条 claim 组成）。就医服务点与 claim 一一同名。
POINT_CLAIMS: dict[str, tuple[str, ...]] = {}


def _claim_ids(point_id: str) -> tuple[str, ...]:
    pid = str(point_id or "").strip()
    if not pid:
        return ()
    return POINT_CLAIMS.get(pid, (pid,))


def _build_points() -> list[dict]:
    """从 Claims Registry 物化卖点池；registry 不可用时只保留 id/name 且标记不可用。"""
    try:
        reg = claims_mod.load()
        broken = ""
    except Exception as exc:                       # 注册表缺失/损坏 → 一律按"不可用"
        reg, broken = None, f"{type(exc).__name__}: {exc}"
    out: list[dict] = []
    for pid, name in _POINT_NAMES:
        ids = _claim_ids(pid)
        points = [reg.get(cid) for cid in ids] if reg else []
        usable = bool(reg) and all(p is not None and p.usable("script") for p in points)
        primary = points[0] if points and points[0] is not None else None
        out.append({"id": pid, "name": name,
                    "hook": (primary.display_text if usable and primary else ""),
                    "claim_ids": list(ids), "usable": usable,
                    "blocked": "" if usable else (broken or "claim 待核验/禁止使用")})
    return out


SALES_POINTS: list[dict] = _build_points()
POINT_IDS: tuple[str, ...] = tuple(p["id"] for p in SALES_POINTS)

# ── 模板-卖点适配（防止"就医场景讲无关服务点"这类画面/台词违和）──
TEMPLATE_FIT = {
    "T01": ["top_hospital", "cost_transparent", "english_care"],
    "T02": ["english_care", "travel_logistics", "fast_track"],
    "T03": ["modern_tech", "top_hospital"],
    "T04": ["cost_transparent", "fast_track", "english_care"],
    "T05": ["travel_logistics", "english_care"],
    "T06": ["recovery_env", "modern_tech"],
    "T07": ["top_hospital", "fast_track"],
    "T08": ["travel_logistics", "english_care", "cost_transparent"],
    "T09": ["modern_tech", "recovery_env"],
    "T10": ["top_hospital", "english_care", "cost_transparent"],
}

# vNext StorySpec 的场景-服务点兼容表：先限定"这个故事能自然讲什么"，再在兼容池里轮换评分。
STRUCTURE_FIT: dict[str, tuple[str, ...]] = {
    "S_duo_conflict": ("top_hospital", "cost_transparent", "english_care", "fast_track"),
    "S_solo_vlog": ("english_care", "travel_logistics", "modern_tech", "recovery_env",
                    "cost_transparent", "top_hospital"),
    "S_street_interview": ("top_hospital", "cost_transparent", "english_care", "travel_logistics"),
    "S_suspense_reveal": ("modern_tech", "recovery_env", "top_hospital"),
    "S_magic_loop": (),
    "S_product_test": ("top_hospital", "modern_tech", "cost_transparent"),
    "S_pov_first": ("english_care", "travel_logistics", "recovery_env"),
    "S_silent_slapstick": (),
    "S_emotional_story": ("english_care", "recovery_env", "travel_logistics", "top_hospital"),
    "S_comment_reply": tuple(pid for pid, _ in _POINT_NAMES),
}

# 就医引流没有"售后/人情故事"这类语境过滤；保留空集，等于不做额外限制。
HUMAN_STORY_TERMS: tuple[str, ...] = ()
HUMAN_STORY_POINTS: frozenset[str] = frozenset()

POINT_TOPIC_TERMS: dict[str, tuple[str, ...]] = {
    "top_hospital": ("hospital", "tertiary", "clinic", "三甲", "医院", "surgeon", "doctor", "specialist"),
    "english_care": ("english", "language", "translator", "coordinator", "translate", "英文", "翻译", "沟通"),
    "cost_transparent": ("cost", "price", "quote", "budget", "afford", "estimate", "费用", "报价", "预算"),
    "fast_track": ("appointment", "book", "schedule", "wait", "queue", "预约", "排期", "等待"),
    "travel_logistics": ("visa", "flight", "airport", "hotel", "travel", "pickup", "签证", "机场", "住宿"),
    "modern_tech": ("equipment", "scanner", "surgery", "technology", "machinery", "设备", "手术", "检查"),
    "recovery_env": ("recovery", "ward", "room", "aftercare", "rehab", "康复", "病房", "陪护"),
    "brand_cta": tuple(),
}


def _used() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def claim_ids_for(point_id: str) -> list[str]:
    """该卖点对应的 claim_id 列表（供 artifact/发布记录，Phase 6 任务 7）。"""
    return list(_claim_ids(str(point_id or "")))


def is_usable(point_id: str, channel: str = "script") -> bool:
    """该卖点能不能自动对外使用（口径已验证 + 渠道允许）。"""
    try:
        reg = claims_mod.load()
    except Exception:
        return False
    points = [reg.get(cid) for cid in _claim_ids(str(point_id or ""))]
    return bool(points) and all(p is not None and p.usable(channel) for p in points)


def point_facts(point_id: str, channel: str = "script") -> str:
    """该卖点的对外文案（唯一来源 = registry 的 display/spoken_text）。"""
    try:
        reg = claims_mod.load()
    except Exception:
        return ""
    chunks: list[str] = []
    for cid in _claim_ids(str(point_id or "")):
        c = reg.get(cid)
        if c is None or not c.usable(channel):
            continue
        chunks.append(c.spoken_text or c.display_text)
    return "；".join(chunks)


def use_counts() -> dict:
    """每个卖点的使用次数 {point_id: n}（供 Planner 当 novelty 特征，只读不改）。"""
    used = _used()
    return {p["id"]: len(used.get(p["id"], [])) for p in SALES_POINTS}


def sales_point_fit(point_id: str, *, topic: str = "", structure_id: str = "",
                    genre_id: str = "", visual_motif: str = "") -> tuple[float, list[str]]:
    """返回卖点对当前选题/骨架的语义适配度（0..1）和理由。

    这是 9/26 `TEMPLATE_FIT` 的 vNext 版本：结构匹配是基础，选题语义再加/减分。
    强语义卖点（质保、飞机、续航等）没有对应上下文时必须低分，不能靠“少用过”入选。
    """
    pid = str(point_id or "")
    text = " ".join((str(topic or ""), str(visual_motif or ""))).lower()
    fit_ids = STRUCTURE_FIT.get(str(structure_id or ""), ())
    structure_score = 1.0 if pid in fit_ids else 0.25
    reasons = ["骨架匹配" if pid in fit_ids else "骨架不匹配"]

    terms = POINT_TOPIC_TERMS.get(pid, ())
    matched = [term for term in terms if term.lower() in text]
    if matched:
        topic_score = min(1.0, 0.72 + 0.09 * len(matched))
        reasons.append("选题命中：" + "、".join(matched[:4]))
    elif terms:
        # 有明确适用语境却完全未命中：只能作为弱备选。质保尤其严格。
        topic_score = 0.05 if pid == "warranty_life" else 0.32
        reasons.append("选题未出现该卖点的适用语境")
    else:
        topic_score = 0.50
        reasons.append("通用卖点，无专属关键词")

    # 情感/人物故事中，纯售后承诺若没有售后语境直接判不适配。
    if genre_id == "G5" and pid == "warranty_life" and not matched:
        topic_score = 0.0
        reasons.append("情感故事禁止无缘由硬转售后")
    score = max(0.0, min(1.0, 0.58 * structure_score + 0.42 * topic_score))
    return round(score, 4), reasons


def compatible_points(*, topic: str, structure_id: str, genre_id: str = "",
                      visual_motif: str = "", min_score: float = 0.48) -> list[dict]:
    """按语义适配度返回可用卖点；没有合格项时宁可退回结构兼容池，也不全池乱配。"""
    used = _used()
    human_story = any(term in str(topic or "") for term in HUMAN_STORY_TERMS)
    rows: list[tuple[float, int, dict]] = []
    for point in SALES_POINTS:
        if not point.get("usable"):
            continue
        if human_story and point["id"] not in HUMAN_STORY_POINTS:
            continue
        score, _ = sales_point_fit(point["id"], topic=topic, structure_id=structure_id,
                                   genre_id=genre_id, visual_motif=visual_motif)
        if score >= min_score:
            rows.append((score, len(used.get(point["id"], [])), point))
    if not rows:
        allowed = set(STRUCTURE_FIT.get(structure_id, ()))
        if human_story:
            allowed &= set(HUMAN_STORY_POINTS)
        rows = [(0.5, len(used.get(p["id"], [])), p) for p in SALES_POINTS
                if p.get("usable") and p["id"] in allowed]
    rows.sort(key=lambda row: (-row[0], row[1], row[2]["id"]))
    return [dict(point, semantic_fit=score) for score, _, point in rows]


def next_point(template_id: str = "") -> dict:
    """选本期主打卖点：优先与模板动作匹配 + 使用次数最少（且口径可用）"""
    used = _used()
    fit = TEMPLATE_FIT.get(template_id)
    pool = [p for p in SALES_POINTS if (not fit or p["id"] in fit)] or SALES_POINTS
    usable = [p for p in pool if p.get("usable")] or pool
    return min(usable, key=lambda p: len(used.get(p["id"], [])))


def record_point(point_id: str, tag: str) -> None:
    """记录本片主打卖点（tag 用 job uid 或主题名）"""
    used = _used()
    lst = used.setdefault(point_id, [])
    if tag not in lst:
        lst.append(tag)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(used, ensure_ascii=False, indent=1), encoding="utf-8")


def points_block() -> str:
    """已用卖点清单（注入文案提示词，强制换新卖点）"""
    used = _used()
    rows = []
    for p in SALES_POINTS:
        n = len(used.get(p["id"], []))
        if n:
            rows.append(f"{p['name']}（已用{n}次，避开当主打）")
    return "；".join(rows)


def sales_points_brief(max_chars: int = 900) -> str:
    """读 Claims Registry → 可用事实摘要（供 LLM 文案/提示词引用真实参数）。

    Phase 6：不再直接读 markdown 正文——markdown 只是 claim 的 evidence 出处。
    """
    try:
        text = claims_mod.load().facts_block("script")
    except Exception as exc:
        return f"（产品事项目前不可用：{type(exc).__name__}: {exc}）"
    return text[:max_chars]


if __name__ == "__main__":
    print(sales_points_brief(400))
    print("\n下次主打:", next_point())
    print("已用:", points_block())
    print("\n口径不可用的卖点:", [p["id"] for p in SALES_POINTS if not p["usable"]])
