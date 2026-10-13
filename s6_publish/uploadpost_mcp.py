#!/usr/bin/env python3
"""Upload-Post 托管 MCP 客户端 —— 把官方 MCP 服务直接接进项目（2026-10-12）。

来源：本机 Hermes 里已验证可用的直连脚本（直连 streamable-HTTP MCP 端点，自己处理
OAuth refresh）。这里落进项目：**去掉本机绝对路径、改用环境变量**，作为
`s6_publish/uploadpost.py`（REST 客户端）之外的第二条发布/互动通道 —— 当 REST 不可用、
或要用 MCP 专属工具（如平台分析、AutoDM）时走这条。

端点：``https://mcp.upload-post.com/mcp``（JSON-RPC over streamable HTTP，OAuth 2.1）
凭据（**不进仓库**）：token 落在 token 目录里的 ``upload-post*.json``，由既有 OAuth 流程
写入；本模块只读它，并在过期前刷新（写回同一目录）。

环境变量：
  UPLOADPOST_MCP_HOME    token 目录（默认 ``%LOCALAPPDATA%\\hermes``）
  UPLOADPOST_MCP_PROXY   需要走本地代理时设置（如 ``http://127.0.0.1:15715``）；默认直连
  UPLOADPOST_MCP_URL     覆盖 MCP 端点（默认官方端点）

用法：
  python s6_publish/uploadpost_mcp.py --list                 # 列出 MCP 工具
  python s6_publish/uploadpost_mcp.py <tool> '<json-args>'   # 调一个工具

代码内：
  from s6_publish.uploadpost_mcp import call_tool, list_tools
  call_tool("get_profile", {})
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

MCP_URL = os.environ.get("UPLOADPOST_MCP_URL", "https://mcp.upload-post.com/mcp")
PROXY = os.environ.get("UPLOADPOST_MCP_PROXY") or None


def _home() -> str:
    """token 目录：优先 UPLOADPOST_MCP_HOME，否则 %LOCALAPPDATA%\\hermes。"""
    explicit = os.environ.get("UPLOADPOST_MCP_HOME")
    if explicit:
        return str(Path(explicit).expanduser())
    local = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~/.local/share")
    return os.path.join(local, "hermes")


def _paths() -> dict[str, str]:
    tok = Path(_home()) / "mcp-tokens"
    return {
        "tokens": str(tok / "upload-post.json"),
        "meta": str(tok / "upload-post.meta.json"),
        "client": str(tok / "upload-post.client.json"),
    }


def _load(p: str) -> dict:
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(p: str, d: dict) -> None:
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def get_token() -> str:
    """返回可用的 access_token；剩余有效期 < 120s 时先刷新。"""
    paths = _paths()
    t = _load(paths["tokens"])
    if t.get("expires_at", 0) - time.time() > 120:
        return t["access_token"]
    meta = _load(paths["meta"])
    try:
        client = _load(paths["client"])
    except OSError:
        client = {}
    cid = client.get("client_id") if isinstance(client, dict) else None
    data = {
        "grant_type": "refresh_token",
        "refresh_token": t["refresh_token"],
        "client_id": cid or "",
    }
    r = requests.post(meta.get("token_endpoint", "https://mcp.upload-post.com/token"),
                      data=data, timeout=60)
    r.raise_for_status()
    new = r.json()
    t["access_token"] = new["access_token"]
    t["refresh_token"] = new.get("refresh_token", t["refresh_token"])
    t["expires_at"] = time.time() + new.get("expires_in", 3600) - 60
    _save(paths["tokens"], t)
    sys.stderr.write("[token refreshed]\n")
    return t["access_token"]


def _parse(resp) -> dict | None:
    """MCP 可能返回 JSON 或 text/event-stream；两种都解出最后一个 JSON 事件。"""
    ct = resp.headers.get("content-type", "")
    try:
        text = resp.content.decode("utf-8")
    except Exception:  # noqa: BLE001
        text = resp.text
    if "text/event-stream" in ct:
        events, cur = [], []
        for line in text.splitlines():
            if line.startswith("data:"):
                cur.append(line[5:].lstrip())
            elif line.strip() == "" and cur:
                events.append("\n".join(cur))
                cur = []
        if cur:
            events.append("\n".join(cur))
        for ev in reversed(events):
            try:
                return json.loads(ev)
            except Exception:  # noqa: BLE001
                continue
        return {"_sse_raw": text[:4000]}
    if not text.strip():
        return None
    return json.loads(text)


def _new_session(session, token: str) -> dict:
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "openJY", "version": "1.0"},
        },
    }
    r = session.post(MCP_URL, headers=headers, json=body, timeout=120)
    r.raise_for_status()
    sid = r.headers.get("mcp-session-id")
    headers2 = dict(headers)
    if sid:
        headers2["Mcp-Session-Id"] = sid
    session.headers.update(headers2)
    session.post(MCP_URL, headers=headers2,
                 json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                 timeout=60)
    return headers2


def call_tool(tool: str, args: dict | None = None, *, timeout: int = 300) -> dict | None:
    """调用一个 MCP 工具，返回解析后的 JSON-RPC 响应。

    直连优先；失败时若配了 UPLOADPOST_MCP_PROXY 再走代理重试一遍（与旧脚本同款兜底）。
    """
    token = get_token()
    last: str | None = None
    for _attempt in range(2):
        for proxy in (None, PROXY):
            if proxy is None and PROXY is None:
                pass  # 直连
            session = requests.Session()
            session.trust_env = False          # 忽略 env 里的全局 socks 代理，直连优先
            if proxy:
                session.proxies = {"http": proxy, "https": proxy}
            try:
                headers = _new_session(session, token)
                body = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": tool, "arguments": args or {}},
                }
                r = session.post(MCP_URL, headers=headers, json=body, timeout=timeout)
                r.raise_for_status()
                return _parse(r)
            except Exception as e:  # noqa: BLE001
                last = f"{type(e).__name__}: {e}"
                time.sleep(3)
        if PROXY is None:
            break                              # 没配代理就别空转第二轮
    raise SystemExit("MCP call failed: " + str(last))


def list_tools() -> list[str]:
    """MCP 工具名列表。"""
    res = call_tool("tools/list", {})
    tools = (res or {}).get("result", {}).get("tools", [])
    return [t["name"] for t in tools]


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--list":
        for name in list_tools():
            print(name)
        return 0
    tool = argv[0]
    args = json.loads(argv[1]) if len(argv) > 1 and argv[1] else {}
    print(json.dumps(call_tool(tool, args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
