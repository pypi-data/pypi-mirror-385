from typing import cast

from openai.types.chat import ChatCompletion

from gpt_invoker import Usage


class DummyResult:
    usage = None


def test_usage_update_early_return_on_none_usage():
    u = Usage("gpt-5")
    # Baseline counters should start at zero
    assert u.prompt_tokens == 0
    assert u.completion_tokens == 0
    assert u.prompt_tokens_cached == 0
    assert u.completion_tokens_cached == 0

    # Call update with a result whose usage is None; should early return
    u.update(cast(ChatCompletion, DummyResult()), is_cached=False)

    # Counters must remain unchanged
    assert u.prompt_tokens == 0
    assert u.completion_tokens == 0
    assert u.prompt_tokens_cached == 0
    assert u.completion_tokens_cached == 0

    # Also verify cached path still early-returns with None usage
    u.update(cast(ChatCompletion, DummyResult()), is_cached=True)

    # Still unchanged
    assert u.prompt_tokens == 0
    assert u.completion_tokens == 0
    assert u.prompt_tokens_cached == 0
    assert u.completion_tokens_cached == 0
