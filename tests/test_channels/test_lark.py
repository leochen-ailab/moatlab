import pytest

pytest.importorskip("lark_oapi")

from moatlab.channels.lark import LarkBotService, LarkCredentials


class TestLarkBotService:
    def test_handle_event_url_verification(self):
        service = LarkBotService(LarkCredentials("app", "secret", ""))
        resp = service.handle_event({"type": "url_verification", "challenge": "abc"})
        assert resp == {"challenge": "abc"}

    def test_handle_event_invalid_token(self):
        service = LarkBotService(LarkCredentials("app", "secret", "expected-token"))
        resp = service.handle_event({"header": {"token": "wrong-token"}})
        assert resp["code"] == 1

    def test_extract_and_strip_mentions(self):
        text = LarkBotService._extract_text('{"text":"<at id=\"123\">bot</at> 分析 aapl"}')
        clean = LarkBotService._strip_mentions(text)
        assert clean == "分析 aapl"

    def test_group_message_without_mentions_is_ignored(self):
        service = object.__new__(LarkBotService)
        service.reply_text = lambda *_args, **_kwargs: (_args, _kwargs)

        called = {"count": 0}

        def fake_run(*_args, **_kwargs):
            called["count"] += 1

        service.run_analysis = fake_run
        service.handle_message(
            {
                "message": {
                    "chat_type": "group",
                    "message_id": "m1",
                    "chat_id": "c1",
                    "content": '{"text":"分析 AAPL"}',
                }
            }
        )
        assert called["count"] == 0

    def test_group_message_with_mentions_triggers_analysis(self, monkeypatch):
        service = object.__new__(LarkBotService)

        replies: list[tuple[str, str]] = []
        service.reply_text = lambda message_id, text: replies.append((message_id, text))

        class FakeThread:
            def __init__(self, target, args, daemon):
                self.target = target
                self.args = args
                self.daemon = daemon

            def start(self):
                self.target(*self.args)

        monkeypatch.setattr("moatlab.channels.lark.threading.Thread", FakeThread)

        captured: list[tuple[str, str]] = []
        service.run_analysis = lambda ticker, chat_id: captured.append((ticker, chat_id))
        service.handle_message(
            {
                "message": {
                    "chat_type": "group",
                    "message_id": "m1",
                    "chat_id": "c1",
                    "content": '{"text":"<at id=\"123\">bot</at> AAPL"}',
                    "mentions": [{"id": {"open_id": "ou_xxx"}}],
                }
            }
        )
        assert replies
        assert "正在分析 AAPL" in replies[0][1]
        assert captured == [("AAPL", "c1")]
