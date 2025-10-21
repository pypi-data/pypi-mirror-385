import json

from openai.types.chat import ChatCompletionMessageParam

from gpt_invoker import GPTInvoker


def test_dump_log_creates_markdown(tmp_path):
    invoker = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=str(tmp_path / "dump"),
        read_from_cache=False,
        write_to_cache=False,
    )

    invoker.dump_log(
        messages=[{"role": "user", "content": "Hi"}],
        output=None,
        is_from_cache=False,
        is_error=True,
        err_msg="Traceback...",
    )

    dump_dir = tmp_path / "dump"
    found = list(dump_dir.rglob("*.md"))
    assert found


def test_jsonl_log_written(tmp_path):
    log_path = tmp_path / "log.jsonl"
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=str(log_path),
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )
    inv.dump_log(
        messages=[{"role": "user", "content": "x"}],
        output=None,
        is_from_cache=False,
        is_error=True,
        err_msg="e",
    )
    data = log_path.read_text("utf-8").strip().splitlines()
    assert data and json.loads(data[0])["is_error"] is True


def test_dump_log_filename_collision_loop(tmp_path, monkeypatch):
    from datetime import datetime as real_dt

    class FixedDT:
        @classmethod
        def now(cls):
            return real_dt(2025, 1, 2, 3, 4, 5, 123456)

    monkeypatch.setattr("gpt_invoker.datetime.datetime", FixedDT)
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=str(tmp_path / "dump"),
        read_from_cache=False,
        write_to_cache=False,
    )
    msgs: list[ChatCompletionMessageParam] = [{"role": "user", "content": "x"}]
    inv.dump_log(
        messages=msgs, output=None, is_from_cache=False, is_error=True, err_msg="e1"
    )
    inv.dump_log(
        messages=msgs, output=None, is_from_cache=False, is_error=True, err_msg="e2"
    )
    files = sorted((tmp_path / "dump").rglob("*.md"))
    assert len(files) == 2
