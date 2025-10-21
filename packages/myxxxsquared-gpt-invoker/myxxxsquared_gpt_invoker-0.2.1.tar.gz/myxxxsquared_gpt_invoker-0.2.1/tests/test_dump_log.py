import json
from pathlib import Path
from typing import Any, Dict, List, cast

from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from gpt_invoker import GPTInvoker


def _make_invoker(tmp_path: Path) -> GPTInvoker:
    return GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=str(tmp_path / "gpt_log.txt"),
        gpt_dump_folder=str(tmp_path / "gpt_dump"),
        read_from_cache=False,
        write_to_cache=False,
    )


def _find_single_md(tmp_path: Path) -> Path:
    mds = list((tmp_path / "gpt_dump").rglob("*.md"))
    assert len(mds) == 1, f"Expected 1 md file, got {len(mds)}: {mds}"
    return mds[0]


class FakeLogProbs:
    def model_dump_json(self) -> str:
        return '{"lp":1}'


class FakeAnnotation:
    def model_dump_json(self) -> str:
        return '{"ann":1}'


class FakeAudio:
    def model_dump_json(self) -> str:
        return '{"audio":1}'


class FakeFuncCall:
    def model_dump_json(self) -> str:
        return '{"fn":1}'


class FakeToolCall:
    def model_dump_json(self) -> str:
        return '{"tool":1}'


class FakeMessage:
    def __init__(
        self,
        content: str | None = None,
        refusal: str | None = None,
        annotations: List[Any] | None = None,
        audio: Any | None = None,
        function_call: Any | None = None,
        tool_calls: List[Any] | None = None,
    ) -> None:
        self.content = content
        self.refusal = refusal
        self.annotations = annotations
        self.audio = audio
        self.function_call = function_call
        self.tool_calls = tool_calls


class FakeChoice:
    def __init__(self, finish_reason: str, index: int, logprobs: Any, message: Any):
        self.finish_reason = finish_reason
        self.index = index
        self.logprobs = logprobs
        self.message = message


class FakeCompletion:
    def __init__(
        self,
        *,
        created: int = 0,
        model: str = "m",
        service_tier: str | None = None,
        system_fingerprint: str | None = None,
        usage: Dict[str, Any] | None = None,
        choices: List[Any] | None = None,
    ) -> None:
        self.created = created
        self.model = model
        self.service_tier = service_tier
        self.system_fingerprint = system_fingerprint
        self.usage = usage
        self.choices = choices or []

    def model_dump_json(self) -> str:
        # Minimal JSON for append-only log; structure does not affect dump_log assertions
        return json.dumps(
            {
                "created": self.created,
                "model": self.model,
                "service_tier": self.service_tier,
                "system_fingerprint": self.system_fingerprint,
                "usage": self.usage,
                "choices": [],
            }
        )


def test_dump_log_error_branch_writes_error_file(tmp_path):
    inv = _make_invoker(tmp_path)
    # Provide two messages; second includes extra fields to trigger "Fields:" block
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "hi", "name": "u1"},
    ]

    inv.dump_log(
        cast(list[ChatCompletionMessageParam], messages),
        output=None,
        is_from_cache=False,
        is_error=True,
        err_msg="boom",
    )

    md = _find_single_md(tmp_path)
    text = md.read_text(encoding="utf-8")

    # Validate error header and message
    assert "ERROR Generation:" in text
    assert "boom" in text
    # Validate input message sections and fields JSON
    assert "------------ Input Message system ------------" in text
    assert "------------ Input Message user ------------" in text
    assert "Fields:" in text

    # Ensure path includes -E (error) marker
    assert "-E" in str(md.parent)


def test_dump_log_cache_flag_and_no_choices_meta(tmp_path):
    inv = _make_invoker(tmp_path)
    messages: List[Dict[str, Any]] = [{"role": "user", "content": "hello"}]

    fake = FakeCompletion(
        created=123,
        model="gpt-X",
        service_tier="tier1",
        system_fingerprint="fp-123",
        usage={"prompt_tokens": 1},
        choices=[],  # trigger "No choices in the response."
    )

    inv.dump_log(
        cast(list[ChatCompletionMessageParam], messages),
        output=cast(ChatCompletion, fake),
        is_from_cache=True,
    )

    md = _find_single_md(tmp_path)
    text = md.read_text(encoding="utf-8")

    # Meta info written
    assert "------------ Response Meta Info ------------" in text
    assert "Created: 123" in text
    assert "Model: gpt-X" in text
    assert "ServiceTier: tier1" in text
    assert "SystemFingerprint: fp-123" in text
    assert "Usage: " in text

    # No choices branch
    assert "No choices in the response." in text

    # Ensure path includes -C (cache) marker
    assert "-C" in str(md.parent)

    # Validate JSON log line appended
    log_path = tmp_path / "gpt_log.txt"
    log_content = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(log_content) >= 1
    last = json.loads(log_content[-1])
    assert last["is_from_cache"] is True
    assert last["is_error"] is False
    assert last["error_message"] is None


def test_dump_log_full_fields_and_non_cached(tmp_path):
    inv = _make_invoker(tmp_path)
    messages: List[Dict[str, Any]] = [
        {"role": "user", "content": "hello", "tool_call_id": "t1"}
    ]

    fake = FakeCompletion(
        created=1,
        model="m2",
        service_tier=None,
        system_fingerprint=None,
        usage={"anything": "ok"},
        choices=[
            FakeChoice(
                finish_reason="stop",
                index=0,
                logprobs=FakeLogProbs(),
                message=FakeMessage(
                    content="the content",
                    refusal="nope",
                    annotations=[FakeAnnotation()],
                    audio=FakeAudio(),
                    function_call=FakeFuncCall(),
                    tool_calls=[FakeToolCall()],
                ),
            )
        ],
    )

    inv.dump_log(
        cast(list[ChatCompletionMessageParam], messages),
        output=cast(ChatCompletion, fake),
        is_from_cache=False,
    )

    md = _find_single_md(tmp_path)
    text = md.read_text(encoding="utf-8")

    # Choice section and logprobs present
    assert "------------ Choice 0 stop Probs: " in text
    assert '{"lp":1}' in text

    # Message content and extras
    assert "the content" in text
    assert "Refusal: nope" in text

    # Annotations/audio/function call/tool calls blocks
    assert "Annotations:" in text
    assert '{"ann":1}' in text

    assert "Audio: " in text
    assert '{"audio":1}' in text

    assert "Function Call: " in text
    assert '{"fn":1}' in text

    assert "Tool Calls:" in text
    assert '{"tool":1}' in text

    # Other fields for the user message should be printed
    assert "Fields:" in text

    # Ensure path includes -N (non-cached) marker
    assert "-N" in str(md.parent)

    # Validate JSON log line appended
    log_path = tmp_path / "gpt_log.txt"
    log_content = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(log_content) >= 1
    last = json.loads(log_content[-1])
    assert last["is_from_cache"] is False
    assert last["is_error"] is False
    assert last["error_message"] is None
