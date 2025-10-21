import pytest

from gpt_invoker import GPTInvoker, Usage


def test_usage_str_contains_totals():
    invoker = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )
    s = str(invoker.usage)
    assert "Input:" in s and "Total:" in s


def test_usage_default_model_string():
    u = Usage("unknown-model")
    out = str(u)
    assert "default price tier" in out


def test_env_missing_api_key_raises(monkeypatch, tmp_path):
    monkeypatch.delenv("GPT_INVOKER_API_KEY", raising=False)
    invoker_kwargs = dict(
        gpt_cache_path=str(tmp_path / "cache.db"),
        gpt_log_path=None,
        gpt_dump_folder=None,
    )

    with pytest.raises(ValueError):
        GPTInvoker(**invoker_kwargs)  # type: ignore


def test_top_p_branch_and_model_args():
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
        top_p=0.9,
    )
    assert inv.model_args.get("top_p") == 0.9
