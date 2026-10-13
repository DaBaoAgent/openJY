"""创意素材层（openJY 精简版）——只保留**素材/词表**，不含旧的「选题评分链」。

这里对外只暴露两块下游真正用得到的东西：

  · `dna`        —— `CreativeDNA` 数据模型与字段校验（s7_learn 运营复盘读它的字段表）；
  · `structures` —— 结构骨架库（镜头/叙事弧/台词模式/角色槽位）。

旧的 Planner / Director / Scorer / Prescreen / PromptCompiler / StoryWriter
（H3 时代的「自动选题 + 评分 + 编译」机器）随付费出片路径一并删除，不再保留。
现行产线的选题由 `tools/jiuyi_select.py`（词表轮换）完成，提示词由
`lib/jiuyi` + `tools/jiuyi_prompts.py` 出。
"""
from .dna import CreativeDNA
from .structures import (
    STORY_STRUCTURES,
    compatible_genres,
    line_plan_for,
    structure_by_id,
)

__all__ = [
    "CreativeDNA",
    "STORY_STRUCTURES",
    "structure_by_id",
    "compatible_genres",
    "line_plan_for",
]
