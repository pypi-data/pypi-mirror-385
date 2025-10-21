import os

import pytest
from openai.types.chat import ChatCompletionMessageParam

from gpt_invoker import GPTInvoker


def test_local_server_basic(local_api_server, tmp_path):
    invoker = GPTInvoker(
        api_key="test-key",
        api_host=local_api_server,
        model="gpt-5",
        gpt_cache_path=str(tmp_path / "cache.db"),
        gpt_log_path=None,
        gpt_dump_folder=str(tmp_path / "dump"),
        read_from_cache=True,
        write_to_cache=True,
        max_tokens=16,
    )

    content = invoker.generate([{"role": "user", "content": "Hello"}])
    assert isinstance(content, str)
    assert content == "hello"

    assert invoker.usage.prompt_tokens == 3
    assert invoker.usage.completion_tokens == 2


def test_cache_ignore_flag_and_write(local_api_server, tmp_path):
    invoker = GPTInvoker(
        api_key="test-key",
        api_host=local_api_server,
        model="gpt-5",
        gpt_cache_path=str(tmp_path / "cache.db"),
        gpt_log_path=None,
        gpt_dump_folder=str(tmp_path / "dump"),
        read_from_cache=True,
        write_to_cache=True,
        max_tokens=16,
    )

    messages: list[ChatCompletionMessageParam] = [{"role": "user", "content": "Hello"}]

    res1 = invoker.generate_all_res(messages, ignore_cache=True)
    assert res1.choices[0].message.content == "hello"
    assert invoker.usage.prompt_tokens == 3
    assert invoker.usage.prompt_tokens_cached == 0

    res2 = invoker.generate_all_res(messages)
    assert res2.choices[0].message.content == "hello"
    assert invoker.usage.prompt_tokens == 3
    assert invoker.usage.prompt_tokens_cached == 3


def test_cache_disabled_no_read_no_write(local_api_server, tmp_path):
    invoker = GPTInvoker(
        api_key="test-key",
        api_host=local_api_server,
        model="gpt-5",
        gpt_cache_path=str(tmp_path / "cache.db"),
        gpt_log_path=None,
        gpt_dump_folder=str(tmp_path / "dump"),
        read_from_cache=False,
        write_to_cache=False,
        max_tokens=16,
    )

    messages: list[ChatCompletionMessageParam] = [{"role": "user", "content": "Hello"}]

    _ = invoker.generate(messages)
    _ = invoker.generate(messages)

    assert invoker.usage.prompt_tokens == 6
    assert invoker.usage.prompt_tokens_cached == 0


@pytest.mark.skipif(
    not os.getenv("GPT_INVOKER_API_KEY")
    or os.getenv("GPT_INVOKER_API_KEY", "").strip()
    in {"", "<your_api_key_here>", "<api_key>"},
    reason="Real API test requires GPT_INVOKER_API_KEY and GPT_INVOKER_RUN_REAL=1.",
)
def test_real_api_basic(tmp_path):
    invoker = GPTInvoker(
        # Read key and default host/model from environment
        gpt_cache_path=str(tmp_path / "cache.db"),
        gpt_log_path=None,
        gpt_dump_folder=str(tmp_path / "dump"),
        max_tokens=16384,
    )

    content = invoker.generate([{"role": "user", "content": "say world 'Hello'"}])
    assert isinstance(content, str)
    assert len(content) > 0
