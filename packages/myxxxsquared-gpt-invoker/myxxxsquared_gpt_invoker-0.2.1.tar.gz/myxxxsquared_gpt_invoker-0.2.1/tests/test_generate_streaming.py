import pytest

from gpt_invoker import GPTInvoker


def test_generate_edge_cases(monkeypatch):
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )

    class FakeMsg:
        def __init__(self, content=None, refusal=None):
            self.content = content
            self.refusal = refusal

    class FakeChoice:
        def __init__(self, message, finish_reason="stop", index=0):
            self.message = message
            self.finish_reason = finish_reason
            self.index = index
            self.logprobs = None

    class FakeResp:
        def __init__(self, choices):
            self.choices = choices

    monkeypatch.setattr(inv, "generate_all_res", lambda m: FakeResp([]))
    with pytest.raises(ValueError):
        inv.generate([{"role": "user", "content": "x"}])

    monkeypatch.setattr(
        inv,
        "generate_all_res",
        lambda m: FakeResp([FakeChoice(FakeMsg("a")), FakeChoice(FakeMsg("b"))]),
    )
    with pytest.raises(ValueError):
        inv.generate([{"role": "user", "content": "x"}])

    monkeypatch.setattr(
        inv,
        "generate_all_res",
        lambda m: FakeResp([FakeChoice(FakeMsg("a"), finish_reason="length")]),
    )
    with pytest.raises(ValueError):
        inv.generate([{"role": "user", "content": "x"}])

    monkeypatch.setattr(
        inv,
        "generate_all_res",
        lambda m: FakeResp([FakeChoice(FakeMsg(None, refusal="no"))]),
    )
    with pytest.raises(ValueError):
        inv.generate([{"role": "user", "content": "x"}])

    monkeypatch.setattr(
        inv,
        "generate_all_res",
        lambda m: FakeResp([FakeChoice(FakeMsg(None, refusal=None))]),
    )
    with pytest.raises(ValueError):
        inv.generate([{"role": "user", "content": "x"}])


def test_generate_inner_stream_monkeypatched(monkeypatch):
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )

    class Delta:
        def __init__(self, content):
            self.content = content

    class Choice:
        def __init__(self, text):
            self.delta = Delta(text)

    class Chunk:
        def __init__(self, text):
            self.choices = [Choice(text)]

    def fake_create(**kwargs):
        return iter([Chunk("hel"), Chunk("lo")])

    monkeypatch.setattr(
        inv.client.chat.completions, "create", lambda **kw: fake_create(**kw)
    )
    out = inv.generate_inner_stream([{"role": "user", "content": "x"}])
    assert out == "hello"


def test_generate_inner_stream_with_none_delta(monkeypatch):
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )

    class Delta:
        def __init__(self, content):
            self.content = content

    class Choice:
        def __init__(self, text):
            self.delta = Delta(text)

    class Chunk:
        def __init__(self, text):
            self.choices = [Choice(text)]

    def fake_create(**kwargs):
        return iter([Chunk("he"), Chunk(None), Chunk("llo")])

    monkeypatch.setattr(
        inv.client.chat.completions, "create", lambda **kw: fake_create(**kw)
    )
    out = inv.generate_inner_stream([{"role": "user", "content": "x"}])
    assert out == "hello"


def test_generate_warning_on_refusal_with_content(monkeypatch, caplog):
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )

    class Msg:
        def __init__(self):
            self.content = "ok"
            self.refusal = "policy"

    class Choice:
        def __init__(self):
            self.message = Msg()
            self.finish_reason = "stop"
            self.index = 0
            self.logprobs = None

    class Resp:
        def __init__(self):
            self.choices = [Choice()]

    monkeypatch.setattr(inv, "generate_all_res", lambda m: Resp())
    with caplog.at_level("WARNING"):
        out = inv.generate([{"role": "user", "content": "x"}])
        assert out == "ok"
        assert any("refused" in r.message.lower() for r in caplog.records)
