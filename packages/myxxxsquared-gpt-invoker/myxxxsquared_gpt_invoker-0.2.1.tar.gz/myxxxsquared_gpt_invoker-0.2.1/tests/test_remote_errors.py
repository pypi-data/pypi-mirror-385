import pytest

from gpt_invoker import GPTInvoker


def test_generate_all_res_error_dump(tmp_path, monkeypatch):
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=str(tmp_path / "dump"),
        read_from_cache=False,
        write_to_cache=False,
    )

    def boom(_):
        raise RuntimeError("failure")

    monkeypatch.setattr(inv, "generate_inner", boom)
    with pytest.raises(RuntimeError):
        inv.generate_all_res([{"role": "user", "content": "x"}])
    found = list((tmp_path / "dump").rglob("*-E/*.md"))
    assert found
