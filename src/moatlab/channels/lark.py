"""Lark 渠道核心：客户端初始化、事件处理、消息收发。"""

from __future__ import annotations

import json
import logging
import threading

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
)

from moatlab.channels.commands import parse_command
from moatlab.channels.formatter import format_analysis, format_error, format_help
from moatlab.config import settings

logger = logging.getLogger(__name__)

# ── Lark Client（海外域名）──────────────────────────────────────────

_client: lark.Client | None = None


def get_client() -> lark.Client:
    """延迟初始化 Lark Client。"""
    global _client
    if _client is None:
        _client = (
            lark.Client.builder()
            .app_id(settings.lark_app_id)
            .app_secret(settings.lark_app_secret)
            .domain(lark.LARK_DOMAIN)
            .log_level(lark.LogLevel.INFO)
            .build()
        )
    return _client


# ── 事件处理 ────────────────────────────────────────────────────────

def handle_event(body: dict) -> dict:
    """解析 Lark HTTP Callback 事件体并分发处理。

    返回 dict 供 FastAPI 作为 JSON 响应。
    """
    header = body.get("header", {})
    event = body.get("event", {})
    event_type = header.get("event_type", "")

    if event_type == "im.message.receive_v1":
        try:
            _handle_message(event)
        except Exception:
            logger.exception("处理 Lark 消息事件失败")

    return {"code": 0}


def _handle_message(event: dict) -> None:
    """处理单条消息事件。"""
    message = event.get("message", {})
    sender = event.get("sender", {})

    chat_type = message.get("chat_type", "")  # "p2p" | "group"
    content_str = message.get("content", "{}")
    chat_id = message.get("chat_id", "")
    message_id = message.get("message_id", "")

    # 解析消息文本
    try:
        content = json.loads(content_str)
    except json.JSONDecodeError:
        content = {}
    text = content.get("text", "").strip()

    if not text:
        return

    # 群聊：需要 @Bot 才触发
    if chat_type == "group":
        mentions = message.get("mentions")
        if not mentions:
            return  # 未 @任何人，忽略
        # 检查是否 @了 Bot（bot 的 id.type == "app"）
        bot_mentioned = any(
            m.get("id", {}).get("union_id") or m.get("key")
            for m in mentions
        )
        if not bot_mentioned:
            return
        # 去除 @mention 占位符（Lark 用 @_user_N 格式）
        text = _strip_mentions(text)

    if not text:
        return

    # 解析指令
    command = parse_command(text)

    if command.type == "help" or command.type == "unknown":
        _reply_text(message_id, format_help())
        return

    if command.type == "analyze":
        _reply_text(message_id, f"⏳ 正在分析 {command.ticker}，请稍候...")
        threading.Thread(
            target=_run_analysis,
            args=(command.ticker, chat_id),
            daemon=True,
        ).start()


def _strip_mentions(text: str) -> str:
    """去除 Lark 消息中的 @mention 占位符。

    Lark 消息中 @用户 会被替换为 @_user_N 格式的占位符。
    """
    import re
    return re.sub(r"@_user_\d+", "", text).strip()


# ── 异步分析 ────────────────────────────────────────────────────────

def _run_analysis(ticker: str, chat_id: str) -> None:
    """后台线程执行全面分析并推送结果。"""
    try:
        from moatlab.agents.orchestrator import Orchestrator

        orchestrator = Orchestrator()
        reports = orchestrator.analyze(ticker)
        text = format_analysis(ticker, reports)
        _send_message(chat_id, text)
    except Exception as e:
        logger.exception("分析 %s 失败", ticker)
        _send_message(chat_id, format_error(ticker, str(e)))


# ── 消息发送 ────────────────────────────────────────────────────────

def _reply_text(message_id: str, text: str) -> None:
    """回复某条消息（群聊中关联上下文）。"""
    request = (
        ReplyMessageRequest.builder()
        .message_id(message_id)
        .request_body(
            ReplyMessageRequestBody.builder()
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()
        )
        .build()
    )
    response = get_client().im.v1.message.reply(request)
    if not response.success():
        logger.error("回复消息失败: code=%s msg=%s", response.code, response.msg)


def _send_message(chat_id: str, text: str) -> None:
    """主动发消息到会话（用于异步结果推送）。"""
    request = (
        CreateMessageRequest.builder()
        .receive_id_type("chat_id")
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(json.dumps({"text": text}))
            .build()
        )
        .build()
    )
    response = get_client().im.v1.message.create(request)
    if not response.success():
        logger.error("发送消息失败: code=%s msg=%s", response.code, response.msg)
