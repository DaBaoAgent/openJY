"""发布通道替身 —— 让发布验收在 0 网络、0 真发下跑完整 Gate 链。

`FakePublishAdapter` 实现 `PublishAdapter` 协议的 `publish()`，可编排每个平台的返回。
"""
from __future__ import annotations


class FakePublishAdapter:
    """发布通道替身：可编排每个平台的返回，绝不真发。"""

    def __init__(self, *, status: str = "SUCCESS", platform_status: dict | None = None,
                 error: str = "", post_id: str = "fake_post") -> None:
        self.status = status
        self.platform_status = dict(platform_status or {})
        self.error = error
        self.post_id = post_id
        self.calls: list[dict] = []

    def publish(self, *, uid, job, brief, platform, copy, mode) -> dict:
        self.calls.append({"uid": uid, "platform": platform, "mode": mode, "copy": dict(copy)})
        status = self.platform_status.get(platform, self.status)
        out: dict = {"status": status}
        if status in ("SUCCESS", "DRAFT"):
            out["post_id"] = f"{self.post_id}_{platform}"
            out["post_url"] = f"https://example.invalid/{uid}/{platform}"
        if status == "AUTH_EXPIRED":
            out["error"] = self.error or "凭据失效（fake）"
        if status == "FAILED":
            out["error"] = self.error or "fake publish failed"
        return out

    @property
    def platforms(self) -> list[str]:
        return [c["platform"] for c in self.calls]
