"""Lark bot channel integration."""

from __future__ import annotations

import json
import logging
import re
import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
)

from moatlab.channels.commands import parse_command
from moatlab.channels.formatter import format_analysis
from moatlab.config import settings

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "MoatLab Lark Bot 使用说明\n"
    "- 分析 AAPL\n"
    "- analyze AAPL\n"
    "- 直接发送 ticker（如 AAPL）\n"
    "- 帮助 / help"
)


@dataclass
class LarkCredentials:
    app_id: str
    app_secret: str
    verification_token: str


class LarkBotService:
    """Handle Lark webhook events and async analysis workflow."""

    def __init__(self, credentials: LarkCredentials):
        self.credentials = credentials
        self._client = (
            lark.Client.builder()
            .app_id(self.credentials.app_id)
            .app_secret(self.credentials.app_secret)
            .domain(lark.LARK_DOMAIN)
            .build()
        )

    def handle_event(self, body: dict[str, Any]) -> dict[str, Any]:
        """Dispatch Lark events."""
        if body.get("type") == "url_verification":
            return {"challenge": body.get("challenge", "")}

        header = body.get("header", {})
        event = body.get("event", {})
        event_type = header.get("event_type", "")

        if self.credentials.verification_token:
            token = header.get("token", "")
            if token != self.credentials.verification_token:
                logger.warning("[Lark] verification token mismatch")
                return {"code": 1, "msg": "invalid token"}

        if event_type == "im.message.receive_v1":
            self.handle_message(event)

        return {"code": 0}

    def handle_message(self, event: dict[str, Any]) -> None:
        """Handle one message event."""
        message = event.get("message", {})
        chat_type = message.get("chat_type", "")
        message_id = message.get("message_id", "")
        chat_id = message.get("chat_id", "")

        text = self._extract_text(message.get("content", ""))
        if chat_type == "group":
            mentions = message.get("mentions") or event.get("mentions") or []
            if not mentions:
                return
            text = self._strip_mentions(text)

        command = parse_command(text)

        if command.type == "help":
            self.reply_text(message_id, HELP_TEXT)
            return

        if command.type == "analyze":
            self.reply_text(message_id, f"正在分析 {command.ticker}，请稍候...")
            threading.Thread(
                target=self.run_analysis,
                args=(command.ticker, chat_id),
                daemon=True,
            ).start()
            return

        self.reply_text(message_id, HELP_TEXT)

    def run_analysis(self, ticker: str, chat_id: str) -> None:
        """Run analysis in background and push result message."""
        try:
            from moatlab.agents.orchestrator import Orchestrator

            reports = Orchestrator().analyze(ticker)
            self.send_text(chat_id, format_analysis(ticker, reports))
        except Exception as exc:  # noqa: BLE001
            logger.exception("[Lark] analysis failed for %s", ticker)
            self.send_text(chat_id, f"分析 {ticker} 失败，请稍后重试。错误信息: {exc}")

    def send_text(self, chat_id: str, text: str) -> None:
        """Send text message to chat."""
        req = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("text")
                .content(json.dumps({"text": text}, ensure_ascii=False))
                .build()
            )
            .build()
        )
        resp = self._client.im.v1.message.create(req)
        if not resp.success():
            logger.error("[Lark] send message failed: %s", lark.JSON.marshal(resp.raw))

    def reply_text(self, message_id: str, text: str) -> None:
        """Reply to a message by message_id."""
        req = (
            ReplyMessageRequest.builder()
            .message_id(message_id)
            .request_body(
                ReplyMessageRequestBody.builder()
                .msg_type("text")
                .content(json.dumps({"text": text}, ensure_ascii=False))
                .build()
            )
            .build()
        )
        resp = self._client.im.v1.message.reply(req)
        if not resp.success():
            logger.error("[Lark] reply message failed: %s", lark.JSON.marshal(resp.raw))

    @staticmethod
    def _extract_text(content: str) -> str:
        if not content:
            return ""
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return content
        return payload.get("text", "")

    @staticmethod
    def _strip_mentions(text: str) -> str:
        cleaned = re.sub(r"<at[^>]*>.*?</at>", "", text)
        return " ".join(cleaned.split())


@lru_cache(maxsize=1)
def get_lark_service() -> LarkBotService:
    """Create singleton lark service from settings."""
    if not settings.lark_app_id or not settings.lark_app_secret:
        raise RuntimeError("Lark 未配置：请设置 LARK_APP_ID 与 LARK_APP_SECRET")

    return LarkBotService(
        credentials=LarkCredentials(
            app_id=settings.lark_app_id,
            app_secret=settings.lark_app_secret,
            verification_token=settings.lark_verification_token,
        )
    )
