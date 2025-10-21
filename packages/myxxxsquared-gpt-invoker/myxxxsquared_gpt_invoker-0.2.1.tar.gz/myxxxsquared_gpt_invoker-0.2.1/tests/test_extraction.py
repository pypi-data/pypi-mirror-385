import json

import pytest

from gpt_invoker import GPTInvoker


def test_extract_code_success_and_errors():
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )

    msg = "Here is code:\n```python\nprint('hi')\n```\n"
    assert inv.extract_code(msg) == "print('hi')\n"

    with pytest.raises(ValueError):
        inv.extract_code("No code block here")

    with pytest.raises(ValueError):
        inv.extract_code("```py\na\n```\ntext\n```js\nb\n```")


def test_extract_invs_multiple():
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )
    txt = "<invariant>A</invariant> and <invariant>B</invariant>"
    assert inv.extract_invs(txt) == ["A", "B"]


def test_extract_json_success_and_errors():
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )

    good = """Here:\n```json
{"k": 1, "v": [1,2]}
```
"""
    assert inv.extract_json(good) == {"k": 1, "v": [1, 2]}

    with pytest.raises(ValueError):
        inv.extract_json("no json fence")

    with pytest.raises(ValueError):
        inv.extract_json("```json\n{}\n``` and another ```json\n{}\n```")

    with pytest.raises(json.JSONDecodeError):
        inv.extract_json("```json\n{bad}\n```")


def test_extract_java_success_and_errors():
    inv = GPTInvoker(
        api_key="x",
        api_host="127.0.0.1",
        gpt_log_path=None,
        gpt_dump_folder=None,
        read_from_cache=False,
        write_to_cache=False,
    )

    good = """```java
class A {}
```
"""
    assert inv.extract_java(good) == "class A {}\n"

    with pytest.raises(ValueError):
        inv.extract_java("no java fence")

    with pytest.raises(ValueError):
        inv.extract_java("```java\nA\n``` and another ```java\nB\n```")
