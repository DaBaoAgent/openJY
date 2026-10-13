"""叙事思路库 — 每条视频换一个故事框架（就医引流：China Medical Journey）

- 记录已用思路，新片从"未用池"优先取；耗尽时停止而非重复旧套路。
- 思路 = 故事由头/场景背景/冲突类型（不是台词的微调），与 Seedance 提示词包的
  `angle` 字段（M1–M6）一一对应。
"""
import json
from pathlib import Path

from . import STATE_DIR

ROOT = Path(__file__).resolve().parent.parent
STATE = STATE_DIR / "story_angles_used.json"

# ── 思路池（就医引流的 6 个叙事框架，2026-10-12 转向西语区后只保留 M 系列）──
ANGLES = [
    {"id": "M1", "name": "街访设问", "dir": "街头采访外国人：为什么越来越多人飞中国看病——用回答带出服务点"},
    {"id": "M2", "name": "亲身自述", "dir": "外籍患者第一人称旁白：从决定到落地就医，讲述真实流程（可信度钩子）"},
    {"id": "M3", "name": "误解破除", "dir": "先给出对『中国医疗』的旧印象，再用现代医院画面与服务打脸纠偏"},
    {"id": "M4", "name": "全流程一日", "dir": "一天走完：机场接机→问诊→检查→病房，展示服务链条的顺滑"},
    {"id": "M5", "name": "费用透明", "dir": "先讲『怕账单看不清』的顾虑，再展示先给参考估算、医院出最终报价的流程"},
    {"id": "M6", "name": "语言无忧", "dir": "担心语言不通的外国人，被全程英文陪诊打消顾虑（沟通场景）"},
]


def _used() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def use_counts() -> dict:
    """每个思路的使用次数 {angle_id: n}（供 Planner 当 novelty 特征，只读不改）。"""
    used = _used()
    return {a["id"]: len(used.get(a["id"], [])) for a in ANGLES}


def next_angle() -> dict:
    """选本期叙事思路：只用未使用框架，耗尽时停止而非重复旧套路。"""
    used = _used()
    pool = [a for a in ANGLES if not a.get("used_up")]
    fresh = [a for a in pool if not used.get(a["id"])]
    if not fresh:
        raise RuntimeError("未使用的叙事思路已耗尽；请扩充思路库，不能重复旧套路")
    return fresh[0]


def record_angle(angle_id: str, tag: str) -> None:
    used = _used()
    lst = used.setdefault(angle_id, [])
    if tag not in lst:
        lst.append(tag)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(used, ensure_ascii=False, indent=1), encoding="utf-8")


def angles_block() -> str:
    """已用思路清单（注入提示词强制避开）"""
    used = _used()
    names = []
    for a in ANGLES:
        if a.get("used_up") or used.get(a["id"]):
            names.append(a["name"])
    return "、".join(names)


if __name__ == "__main__":
    print("下次思路:", next_angle())
    print("已用:", angles_block())
