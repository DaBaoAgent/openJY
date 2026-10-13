# openJY — 就医引流（China Medical Journey）西语短视频管线

把「来华就医」引流短片从**选题到海外发布**的完整、可跑通管线收敛到一个精简仓库。
出片环节刻意改成人机分工：**Claude 出 Seedance 提示词 → 宝哥在 Seedance 出片 → 本仓库做后期 + 发布**。

> 本项目是从 `D:\@kaifa\jiuyi` 复制出来的**精简版**：只保留跑通的西语链路。
> 旧的付费出片（H3/AutoDL）、旧策划评分链（Planner/Director/Scorer/Compiler）、
> 抖音抓取（s1_trend）、中文 8 句产线等**一概未带**。

## 管线一览

```
① 调研 / 卖点 / 选题      tools/jiuyi_select.py        （本地素材：热点库 + 桥段库 + claims）
② 出提示词（免费）        tools/jiuyi_prompts.py emit  （→ prompts/<id>.md 可直接粘贴）
   —— 宝哥在 Seedance 出片，把 mp4 丢进 out/
③ 后期：字幕 + BGM        tools/jiuyi_finish.py        （out/*.mp4 → video/*_final.mp4）
④ 海外发布 + 运营          s6_publish/ + s7_learn/      （Upload-Post 上传、评论互动、学习闭环）
```

- **选题**：`lib/angles.py`（M1–M6 就医角度）+ `lib/genres.py`（G1–G10 片型）+ `lib/products.py`
  （claims 卖点）三池词表轮换；`lib/creative_research.py` 从本地热点/桥段库取一条未用过的选题。
- **提示词**：`lib/jiuyi/` 里手写的成品包（`catalog.py` 英文批 / `catalog_es.py` 西语批），
  经 `promptpack.py` 渲染 + 校验（语速档 / 无阿拉伯数字 / 医疗红线 / lip-sync 必备项）。
- **后期**：`lib/post/transcript.py`（faster-whisper 字级时间轴）→ 自动匹配提示词包 →
  `s5_compose/burn_subtitles.py` 烧**无标点 + 卖点词高亮 + Noto Sans SC** 字幕 →
  `lib/post/audio_director.py` 选 BGM + `lib/post/loudness.py` 混音到目标响度。
- **发布**：`lib/packaging/`（合规 Gate + 平台策略）+ `s6_publish/uploadpost*.py`（海外 Upload-Post）。
- **运营**：`s6_publish/engage.py`（评论/DM 自动回复 + 安全护栏）+ `s7_learn/`（表现采集 → 学习 → 报告）。

## 目录

| 目录 | 作用 |
|---|---|
| `lib/jiuyi/` | Seedance 提示词包：数据契约 + 渲染 + 校验 + 成品 catalog |
| `lib/post/` | 后期：转写 / 选曲 / 响度 / 音效 |
| `s5_compose/` | 视频合成（字幕烧录） |
| `s6_publish/` | 发布（Upload-Post）+ 评论互动 |
| `s7_learn/` | 运营学习：采集 / 特征 / 归一 / 打分 / 报告 |
| `lib/packaging/` | 发布前合规 Gate + 平台策略 |
| `tools/` | 命令行入口 |
| `config/default.yaml` | 唯一权威非敏感配置（语言 = es） |
| `assets/` | BGM 曲库 + claims 卖点表 + 本地调研素材（热点库/桥段库） |
| `prompts/` `out/` `video/` | 交接目录：提示词 → 宝哥出片 → 成片（均不进 git） |

## 环境

无系统级依赖绑定；ffmpeg / ffprobe 需在 PATH 或由 `config.paths.ffmpeg` 指定。

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows
pip install -e .                 # 运行时依赖
pip install -r requirements-asr.txt   # 仅当需要本地转写字幕
```

密钥（DeepSeek / Upload-Post）走环境变量或系统凭据库（`keyring`），**绝不进仓库**，见 `.env.example`。

## 常用命令

```bash
# ① 选一个「角度 + 片型 + 卖点」组合（可 --commit <tag> 记录已用）
python tools/jiuyi_select.py
python tools/jiuyi_select.py --list          # 看三个池子 + 已用次数

# ② 出提示词包（默认 en+es 全出到 prompts/）
python tools/jiuyi_prompts.py emit
python tools/jiuyi_prompts.py emit --lang es --count 10
python tools/jiuyi_prompts.py check          # 只校验不落盘

# ③ 后期：out/*.mp4 → video/*_final.mp4（字幕 + BGM）
python tools/jiuyi_finish.py
python tools/jiuyi_finish.py --dry           # 只转写+匹配+打印，不落盘
python tools/jiuyi_finish.py --pack <id>     # 强制指定台词包（跳过自动识别）

# 体检 / 测试
python tools/health_check.py
python -m pytest tests -q
```

## 测试

只保留覆盖**跑通链路**的测试（单元 + 集成，共 241 项，0 联网 0 付费）。
`tests/conftest.py` 把 state 落盘重定向到临时目录，测试之间互不影响。

live / paid 标记的测试默认永不执行，需显式 `AYHMJ_RUN_LIVE=1` / `AYHMJ_RUN_PAID=1` 放行。
