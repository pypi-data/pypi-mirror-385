import json
from typing import Any, Dict, List, cast

from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from gpt_invoker import GPTInvoker


def _make_invoker(tmp_path):
    return GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_cache_path=str(tmp_path / "cache.db"),
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=True,
        write_to_cache=True,
    )


class FakeCompletionWithDump:
    def __init__(self, id_value: str, model: str = "m"):
        self._id_value = id_value
        self._model = model

    def model_dump_json(self) -> str:
        # Minimal but valid JSON-ish structure for our cache storage test.
        # It does not need to conform to OpenAI's full schema for this test.
        return json.dumps(
            {
                "id": self._id_value,
                "object": "chat.completion",
                "created": 0,
                "model": self._model,
                "choices": [],
                "usage": {},
            }
        )


def test_put_gpt_cache_overwrites_when_same_digest_and_prompt(tmp_path):
    inv = _make_invoker(tmp_path)
    # Same messages -> same msg_digest and msg_concat
    messages: List[Dict[str, Any]] = [{"role": "user", "content": "hello"}]
    msg_digest, msg_concat = inv._msg_digest(
        cast(list[ChatCompletionMessageParam], messages)
    )

    # First insert old value
    inv._put_gpt_cache(
        msg_digest,
        msg_concat,
        cast(ChatCompletion, FakeCompletionWithDump("old", "m1")),
    )

    # Now update with new value under the same digest/prompt
    inv._put_gpt_cache(
        msg_digest,
        msg_concat,
        cast(ChatCompletion, FakeCompletionWithDump("new", "m2")),
    )

    # Verify DB now stores the new value
    cursor = inv.gpt_cache.cursor()  # type: ignore[union-attr]
    cursor.execute(
        "SELECT cache_response FROM gpt_cache WHERE cache_digest = ?", (msg_digest,)
    )
    row = cursor.fetchone()
    assert row is not None
    stored = json.loads(row[0])
    assert stored["id"] == "new"
    assert stored["model"] == "m2"
