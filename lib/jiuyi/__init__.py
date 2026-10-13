"""就医引流（China Medical Journey）外文出片层（现为西语 es）。

宝哥 2026-10-12 定的新分工：不再用付费出片接口，改成
  · 我产出成批 Seedance 文生视频提示词（本包：render / validate / catalog）；
  · 宝哥在 Seedance 出片、丢进仓库根的 out/；
  · 后期器烧外文字幕 + 配 BGM，输出仓库根的 video/。
"""
from .promptpack import (
    ASPECT,
    DEFAULT_DURATION,
    PromptPack,
    redline_hits,
    render,
    speech_units,
    unit_budget,
    validate,
)

__all__ = [
    "ASPECT", "DEFAULT_DURATION", "PromptPack", "redline_hits", "render",
    "speech_units", "unit_budget", "validate",
]
