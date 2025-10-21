"""
GPT Invoker - a thin utility around the OpenAI Chat Completions API with:

- Local SQLite response cache (content-addressed by prompt + model args)
- Token usage accounting with rough price estimation per model
- Rich dump logging to markdown files for later inspection
- Optional structured JSONL-like append-only log
- Convenience helpers to extract code/JSON/java blocks from responses

Environment variables:
- GPT_INVOKER_API_KEY: API key for the target API host. Required unless
    explicitly passed into GPTInvoker.
- GPT_INVOKER_API_HOST: Base URL for the API. Defaults to https://api.openai.com
- GPT_INVOKER_DEF_MODEL: Default model name used if not provided.

Thread-safety:
- The SQLite cache connection is opened with check_same_thread depending on
    sqlite3.threadsafety. A threading.Lock is used only for usage counters.

Notes:
- This module focuses on simple, reproducible calls and traceability. It does
    not aim to expose the entire OpenAI API surface.
"""

import datetime
import hashlib
import json
import logging
import os
import re
import sqlite3
import threading
import traceback
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Optional

import colorlog
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "UNKNOWN"


logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)


def _init_logger():
    """Initialize a colorized console logger for this module.

    Sets a DEBUG-level colored formatter so that library consumers get
    helpful diagnostics by default. This function is called at import time.
    """
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter("%(log_color)s%(levelname)s: %(name)s %(message)s")
    )
    handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


_init_logger()


# Regex helpers to extract common content patterns from model responses
RESPONSE_CODE_PATTERN = re.compile("```(?:\\w+\\s+)?(.*?)```", re.DOTALL)
RESPONSE_INVARIANT_PATTERN = re.compile("<invariant>(.*?)</invariant>")
RESPONSE_FIELD_PATTERN = re.compile("<field>(.*?)</field>")
RESPONSE_JSON_PATTERN = re.compile("```json\n(.*?)```", re.DOTALL)
RESPONSE_JAVA_PATTERN = re.compile("```java\n(.*?)```", re.DOTALL)


# Rough pricing table per million tokens for estimation only.
# Format: model -> (input_price, output_price, audio_price) where some values
# may be None if not applicable. These are indicative and may be outdated.
GPT_PRICE_TABLE = {
    "default": (1.25, 10.0, 0.125),
    # --- GPT-5 ---
    "gpt-5": (1.25, 10.0, 0.125),
    "gpt-5-mini": (0.25, 2.0, 0.025),
    "gpt-5-nano": (0.05, 0.40, 0.005),
    "gpt-5-chat-latest": (1.25, 10.0, 0.125),
    "gpt-5-codex": (1.25, 10.0, 0.125),
    "gpt-5-pro": (15.0, 120.0, None),
    "gpt-5-search-api": (1.25, 10.0, 0.125),
    # --- GPT-4.1 ---
    "gpt-4.1": (2.0, 8.0, 0.5),
    "gpt-4.1-mini": (0.4, 1.6, 0.1),
    "gpt-4.1-nano": (0.1, 0.4, 0.025),
    # --- GPT-4o ---
    "gpt-4o": (2.5, 10.0, 1.25),
    "gpt-4o-2024-05-13": (5.0, 15.0, None),
    "gpt-4o-mini": (0.15, 0.6, 0.075),
    "gpt-4o-realtime-preview": (5.0, 20.0, 2.5),
    "gpt-4o-mini-realtime-preview": (0.6, 2.4, 0.3),
    "gpt-4o-search-preview": (2.5, 10.0, None),
    "gpt-4o-mini-search-preview": (0.15, 0.6, None),
    "gpt-4o-audio-preview": (2.5, 10.0, None),
    "gpt-4o-mini-audio-preview": (0.15, 0.6, None),
    # --- GPT-o ---
    "o1": (15.0, 60.0, 7.5),
    "o1-pro": (150.0, 600.0, None),
    "o1-mini": (1.10, 4.40, 0.55),
    "o3": (2.0, 8.0, 0.5),
    "o3-pro": (20.0, 80.0, None),
    "o3-deep-research": (10.0, 40.0, 2.5),
    "o3-mini": (1.10, 4.40, 0.55),
    "o4-mini": (1.10, 4.40, 0.275),
    "o4-mini-deep-research": (2.0, 8.0, 0.5),
    # --- Claude Opus ---
    "claude-opus-4-1": (15.0, 75.0, 1.5),
    "claude-opus-4": (15.0, 75.0, 1.5),
    "claude-opus-3": (15.0, 75.0, 1.5),
    # --- Claude Sonnet ---
    "claude-sonnet-4-5": (3.0, 15.0, 0.3),
    "claude-sonnet-4": (3.0, 15.0, 0.3),
    "claude-sonnet-3-7": (3.0, 15.0, 0.3),
    "claude-sonnet-3-5": (3.0, 15.0, 0.3),
    # --- Claude Haiku ---
    "claude-haiku-4-5": (1.0, 5.0, 0.1),
    "claude-haiku-3-5": (0.8, 4.0, 0.08),
    "claude-haiku-3": (0.25, 1.25, 0.03),
}


class Usage:
    """Track token usage and estimate cost for a given model tier.

    This class accumulates prompt and completion token counts both for
    cache hits and fresh calls, and can render a short price summary
    using GPT_PRICE_TABLE.
    """

    def __init__(self, model_name: Optional[str] = None):
        """Create a Usage tracker.

        Args:
            model_name: The name looked up in GPT_PRICE_TABLE. If missing,
                a default price tier is used for estimation only.
        """
        self.clear()

        if model_name not in GPT_PRICE_TABLE:
            logger.warning(
                f"Model {model_name} not found in price table, using default tier for estimation."
            )
            model_name = "default"
        self.model_name = model_name

        self.lock = threading.Lock()

    def clear(self):
        """Reset all counters to zero."""
        self.completion_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens_cached = 0
        self.prompt_tokens_cached = 0

    def update(self, result: ChatCompletion, is_cached: bool = False):
        """Update counters from an API result.

        Args:
            result: The ChatCompletion object returned by the client.
            is_cached: True if this result came from local cache, recorded
                separately for reporting.
        """
        usage = result.usage
        if usage is None:
            return

        with self.lock:
            if not is_cached:
                self.completion_tokens += usage.completion_tokens
                self.prompt_tokens += usage.prompt_tokens
            else:
                self.completion_tokens_cached += usage.completion_tokens
                self.prompt_tokens_cached += usage.prompt_tokens

    def __str__(self):
        """Return a compact human-readable usage summary with price estimate."""
        model_str = ""
        if self.model_name == "default":
            model_str = "(Estimated by default price tier) "

        input_tokens = self.prompt_tokens
        output_tokens = self.completion_tokens
        input_tokens_cached = self.prompt_tokens_cached
        output_tokens_cached = self.completion_tokens_cached

        input_tokens_price = (
            input_tokens * GPT_PRICE_TABLE[self.model_name][0] / 1000000
        )
        output_tokens_price = (
            output_tokens * GPT_PRICE_TABLE[self.model_name][1] / 1000000
        )
        input_tokens_cached_price = (
            input_tokens_cached * GPT_PRICE_TABLE[self.model_name][0] / 1000000
        )
        output_tokens_cached_price = (
            output_tokens_cached * GPT_PRICE_TABLE[self.model_name][1] / 1000000
        )

        total_tokens = (
            input_tokens + output_tokens + input_tokens_cached + output_tokens_cached
        )
        total_price = (
            input_tokens_price
            + output_tokens_price
            + input_tokens_cached_price
            + output_tokens_cached_price
        )

        return (
            f"{model_str}Input: {input_tokens} tokens ({input_tokens_price:.4f} USD), "
            f"Output: {output_tokens} tokens ({output_tokens_price:.4f} USD), "
            f"Cached Input: {input_tokens_cached} tokens ({input_tokens_cached_price:.4f} USD), "
            f"Cached Output: {output_tokens_cached} tokens ({output_tokens_cached_price:.4f} USD), "
            f"Total: {total_tokens} tokens ({total_price:.4f} USD)"
        )


class GPTInvoker:
    """A small helper around OpenAI's Chat Completions with caching and logs.

    Features:
    - Optional SQLite-backed cache keyed by model args + message payload
    - Markdown dump of request/response for reproducibility
    - Append-only structured log for machine parsing
    - Token usage accounting and price estimation

    Typical usage:
        invoker = GPTInvoker()
        text = invoker.generate([{"role": "user", "content": "hi"}])

    All parameters can be provided via environment variables; see module docstring.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        top_p: Optional[float] = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        api_host: Optional[str] = None,
        gpt_cache_path: Optional[str] = None,
        read_from_cache: bool = True,
        write_to_cache: bool = True,
        gpt_log_path: Optional[str] = None,
        write_gpt_log: bool = True,
        gpt_dump_folder: Optional[str] = None,
        dump_gpt_log: bool = True,
    ) -> None:
        """Initialize the invoker and supporting facilities.

        Args:
            api_key: API key for the target host; otherwise read from env.
            model: Model name for chat.completions.
            top_p: Nucleus sampling parameter.
            max_tokens: Max tokens for generated content.
            temperature: Sampling temperature.
            api_host: Base URL for the API service.
            gpt_cache_path: Path to a SQLite file for caching.
            read_from_cache: Whether to attempt cache lookups.
            write_to_cache: Whether to write successful responses to cache.
            gpt_log_path: Path to append-only JSON lines log; None disables it.
            write_gpt_log: Currently unused toggle kept for compatibility.
            gpt_dump_folder: Folder for markdown dumps; None disables dumps.
            dump_gpt_log: Currently unused toggle kept for compatibility.
        """
        cur_path = os.path.dirname(os.path.abspath(__file__))

        if api_host is None:
            api_host = os.getenv("GPT_INVOKER_API_HOST", "https://api.openai.com")
        if api_key is None:
            api_key = os.getenv("GPT_INVOKER_API_KEY", "")
            if (api_key.startswith("<") and api_key.endswith(">")) or api_key == "":
                raise ValueError(
                    "API key is not provided. Please set the api_key parameter or GPT_INVOKER_API_KEY environment variable or .env file."
                )
        if model is None:
            model = os.getenv("GPT_INVOKER_DEF_MODEL", "gpt-5")

        if gpt_cache_path is None:
            gpt_cache_path = os.path.join(cur_path, "gpt_cache.db")
        if gpt_log_path is None and (write_gpt_log is True):
            gpt_log_path = os.path.join(cur_path, "gpt_log.txt")
        if gpt_dump_folder is None and (dump_gpt_log is True):
            gpt_dump_folder = os.path.join(cur_path, "gpt_dump")

        self.gpt_cache_path = gpt_cache_path
        self.gpt_log_path = gpt_log_path
        self.gpt_dump_folder = gpt_dump_folder
        self.read_from_cache = read_from_cache
        self.write_to_cache = write_to_cache
        self.enable_cache = read_from_cache or write_to_cache
        self.write_gpt_log = write_gpt_log
        self.dump_gpt_log = dump_gpt_log

        self.client = OpenAI(api_key=api_key, base_url=api_host)
        self.model = model
        self.model_args = {
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if top_p is not None:
            self.model_args["top_p"] = top_p

        self.gpt_cache = None
        self._init_gpt_cache()

        self.gpt_log = (
            None
            if self.gpt_log_path is None
            else open(self.gpt_log_path, "ab", buffering=0)
        )

        self.prompt_organize_input_system = None
        self.prompt_organize_input_user = None
        self.prompt_organize_input_error = None

        self.usage = Usage(self.model)

    def __del__(self):
        """Best-effort cleanup of open resources to avoid warnings."""
        try:
            gpt_log = getattr(self, "gpt_log", None)
            if gpt_log is not None:
                gpt_log.close()
        except Exception:  # pragma: no cover
            pass  # pragma: no cover
        try:
            gpt_cache = getattr(self, "gpt_cache", None)
            if gpt_cache is not None:
                gpt_cache.close()
        except Exception:  # pragma: no cover
            pass  # pragma: no cover

    def _to_json_str(self, obj: ChatCompletion) -> str:
        """Serialize an object to JSON string."""
        return obj.model_dump_json()

    def _init_gpt_cache(self):
        """Create/open the SQLite cache and compute a stable model-args prefix.

        Also prepares an index on the cache digest for fast lookups and
        generates a deterministic string of model args used when hashing prompts.
        """
        if not self.enable_cache:
            return

        check_thread = True
        if sqlite3.threadsafety == 3:
            check_thread = False  # pragma: no cover
        else:
            logger.warning(
                "SQLite threadsafety is not 3, which may cause issues with concurrent access."
            )  # pragma: no cover

        self.gpt_cache = sqlite3.connect(
            self.gpt_cache_path, check_same_thread=check_thread
        )

        cursor = self.gpt_cache.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS gpt_cache (cache_id PRIMARY KEY, cache_digest TEXT, cache_prompt TEXT, cache_response TEXT)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS cache_digest_index ON gpt_cache (cache_digest)"
        )
        try:
            self.gpt_cache.commit()
        except sqlite3.OperationalError:  # pragma: no cover
            pass  # pragma: no cover

        seperate_token = "|9ZPA|"
        model_args_sorted = sorted(self.model_args.items())
        msg_concat = []
        for key, value in model_args_sorted:
            msg_concat.append(seperate_token)
            msg_concat.append(key)
            msg_concat.append(seperate_token)
            msg_concat.append(repr(value))
        msg_concat.append(seperate_token)
        msg_concat.append(self.model)
        self.model_args_str = "".join(msg_concat)

    def _query_gpt_cache(
        self, msg_digest: str, msg_concat: str
    ) -> Optional[ChatCompletion]:
        """Return a cached ChatCompletion if prompt+args match exactly.

        Args:
            msg_digest: The SHA1 digest of model-args-string + message JSON.
            msg_concat: The exact concatenated string used to verify equality.

        Returns:
            A deserialized ChatCompletion if present and matching; otherwise None.
        """
        assert self.gpt_cache is not None

        cursor = self.gpt_cache.cursor()
        cursor.execute(
            "SELECT cache_prompt, cache_response FROM gpt_cache WHERE cache_digest = ? ",
            (msg_digest,),
        )
        response = cursor.fetchone()
        if response:
            cache_prompt_q, cache_response = response
            if cache_prompt_q == msg_concat:
                return ChatCompletion(**json.loads(cache_response))
        return None

    def _put_gpt_cache(
        self, msg_digest: str, msg_concat: str, msg_response: ChatCompletion
    ):
        """Insert or update a cache entry for the given prompt digest."""
        assert self.gpt_cache is not None

        try:
            cursor = self.gpt_cache.cursor()
            cursor.execute(
                "SELECT cache_prompt, cache_response FROM gpt_cache WHERE cache_digest = ? ",
                (msg_digest,),
            )
            response = cursor.fetchone()
            if response:
                cache_prompt_q, existing_cache_response = response[0], response[1]
                if cache_prompt_q == msg_concat:
                    new_json = msg_response.model_dump_json()
                    cursor.execute(
                        "UPDATE gpt_cache SET cache_response = ? WHERE cache_digest = ?",
                        (new_json, msg_digest),
                    )
                else:
                    return  # pragma: no cover
            else:
                # No existing row: serialize best-effort
                to_store = self._to_json_str(msg_response)
                cursor.execute(
                    "INSERT INTO gpt_cache (cache_digest, cache_prompt, cache_response) VALUES (?, ?, ?)",
                    (msg_digest, msg_concat, to_store),
                )
            try:
                self.gpt_cache.commit()
            except sqlite3.OperationalError:  # pragma: no cover
                pass  # pragma: no cover
        except Exception:  # pragma: no cover
            logger.error(
                "Error while writing to GPT cache", exc_info=True
            )  # pragma: no cover

    def _msg_digest(self, message: list[ChatCompletionMessageParam]) -> tuple[str, str]:
        """Compute a content digest for the given messages and current model args.

        Returns a tuple of (digest_hex, concat_string) to enable equality checks
        alongside quick indexed lookups.
        """
        msg_concat = [self.model_args_str]
        msg_concat.append(json.dumps(message, ensure_ascii=False))
        msg_concat = "".join(msg_concat)
        msg_digest = hashlib.sha1(msg_concat.encode()).hexdigest()
        return msg_digest, msg_concat

    def generate_inner(
        self, messages: list[ChatCompletionMessageParam]
    ) -> ChatCompletion:
        """Perform a raw API call using current model and args."""
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, **self.model_args
        )
        return response

    def generate_inner_stream(self, messages: list[ChatCompletionMessageParam]) -> str:
        """Stream a response and return the concatenated text content.

        Note: This helper only returns textual content from the first choice.
        """
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, stream=True, **self.model_args
        )
        all_text = []
        for sse_chunk in response:
            if len(sse_chunk.choices) > 0:
                content = sse_chunk.choices[0].delta.content
                if content is not None:
                    all_text.append(content)
        response = "".join(all_text)
        return response

    def generate_all_res(
        self, messages: list[ChatCompletionMessageParam], ignore_cache=False
    ) -> ChatCompletion:
        """Return the full ChatCompletion, consulting cache when enabled.

        On errors the request/exception is dumped to the markdown log for
        later inspection.
        """
        msg_digest, msg_concat = None, None
        if (self.read_from_cache and not ignore_cache) or self.write_to_cache:
            msg_digest, msg_concat = self._msg_digest(messages)
            if self.read_from_cache and not ignore_cache:
                gpt_cache = self._query_gpt_cache(msg_digest, msg_concat)
                if gpt_cache is not None:
                    self.dump_log(messages, gpt_cache, True)
                    self.usage.update(gpt_cache, is_cached=True)
                    return gpt_cache

        try:
            response = self.generate_inner(messages)
        except Exception:
            logger.error("Error while generating response", exc_info=True)
            err_msg = traceback.format_exc()
            self.dump_log(messages, None, False, True, err_msg)
            raise

        self.usage.update(response)

        if self.enable_cache and self.write_to_cache:
            assert msg_digest is not None and msg_concat is not None
            self._put_gpt_cache(msg_digest, msg_concat, response)

        self.dump_log(messages, response, False)

        return response

    def generate(self, messages: list[ChatCompletionMessageParam]) -> str:
        """Convenience wrapper that returns the single choice's text content.

        Raises if there are zero or multiple choices, or if finish_reason is
        not "stop".
        """
        response = self.generate_all_res(messages)
        choices = response.choices
        if len(choices) == 0:
            raise ValueError("No choices in the response")
        if len(choices) > 1:
            raise ValueError("Multiple choices in the response")
        choice = choices[0]
        finish_reason = choice.finish_reason
        if finish_reason != "stop":
            raise ValueError(f"Finish reason is not 'stop': {finish_reason}")
        msg = choice.message
        if msg.refusal is not None:
            logger.warning(f"GPT refused to answer: {msg.refusal}.")
        if msg.content is None:
            if msg.refusal is not None:
                raise ValueError("Refused Message: " + msg.refusal)
            raise ValueError("No content in the response message")
        content = msg.content
        return content

    def extract_code(self, message: str) -> str:
        """Extract the first fenced code block from a response body.

        Supports an optional language specifier after the opening backticks.
        Raises if none or multiple blocks are present.
        """
        code_matches = RESPONSE_CODE_PATTERN.findall(message)
        if len(code_matches) == 0:
            raise ValueError("No code block found in the response")
        if len(code_matches) > 1:
            raise ValueError("Multiple code blocks found in the response")

        code = code_matches[0]

        return code

    def extract_invs(self, message: str) -> list[str]:
        """Extract all <invariant>...</invariant> blocks from text."""
        invariant_matches = RESPONSE_INVARIANT_PATTERN.findall(message)
        return invariant_matches

    def extract_json(self, message: str):
        """Extract the first ```json fenced block and parse it into a dict/list."""
        json_matches = RESPONSE_JSON_PATTERN.findall(message)
        if len(json_matches) == 0:
            raise ValueError("No json block found in the response")
        if len(json_matches) > 1:
            raise ValueError("Multiple json blocks found in the response")
        json_str = json_matches[0]
        json_obj = json.loads(json_str)
        return json_obj

    def extract_java(self, message: str):
        """Extract the first ```java fenced block as a raw string."""
        java_matches = RESPONSE_JAVA_PATTERN.findall(message)
        if len(java_matches) == 0:
            raise ValueError("No java block found in the response")
        if len(java_matches) > 1:
            raise ValueError("Multiple java blocks found in the response")
        java_str = java_matches[0]
        return java_str

    def dump_log(
        self,
        messages: list[ChatCompletionMessageParam],
        output: Optional[ChatCompletion],
        is_from_cache: bool,
        is_error: bool = False,
        err_msg: Optional[str] = None,
    ):
        """Dump a human-readable snapshot of the request/response to disk.

        Two forms are supported:
        - Markdown file under gpt_dump/YYYY-MM-DD/HH-[C|N|E]/...
        - Optional JSON-structured append-only log to `gpt_log_path`.

        Args:
            messages: The chat messages sent to the API.
            output: The ChatCompletion result; None for error cases.
            is_from_cache: Whether `output` came from local cache.
            is_error: Whether this log records an exception instead of a result.
            err_msg: Traceback text if `is_error` is True.
        """
        # if self.gpt_dump_folder is None: return
        if self.gpt_dump_folder is not None:
            all_msgs = str(messages)
            md5 = hashlib.md5(all_msgs.encode()).hexdigest()

            now_time = datetime.datetime.now()
            now = now_time.strftime("%Y-%m-%d-%H-%M-%S-%f")
            idx = 0
            cache_str = "-C" if is_from_cache else "-N"
            if is_error:
                cache_str = "-E"
            while True:
                folder = now_time.strftime("%Y-%m-%d/%H" + cache_str)
                os.makedirs(os.path.join(self.gpt_dump_folder, folder), exist_ok=True)
                full_name = os.path.join(
                    self.gpt_dump_folder, folder, f"{now}-{md5}-{idx}.md"
                )
                if not os.path.exists(full_name):
                    break
                idx += 1

            with open(full_name, "w") as f:
                if is_error:
                    f.write(f"ERROR Generation: \n{err_msg}\n")
                if output is not None:
                    f.write("------------ Response Meta Info ------------\n")
                    f.write(f"Created: {output.created}\n")
                    f.write(f"Model: {output.model}\n")
                    f.write(f"ServiceTier: {output.service_tier}\n")
                    f.write(f"SystemFingerprint: {output.system_fingerprint}\n")
                    f.write(f"Usage: {output.usage}\n")
                for msg in messages:
                    role = msg["role"]
                    f.write(f"\n\n------------ Input Message {role} ------------\n")
                    other_fields = {}
                    for k, v in msg.items():
                        if k == "role" or k == "content":
                            continue
                        other_fields[k] = v
                    if len(other_fields) > 0:
                        other_fields = json.dumps(
                            other_fields, ensure_ascii=False, indent=2
                        )
                        f.write(f"Fields: {other_fields}\n\n")
                    if "content" in msg:
                        f.write(msg["content"])  # type: ignore
                if output is not None:
                    f.write("\n\n------------ Response Message ------------\n")
                    choices = output.choices
                    if len(choices) == 0:
                        f.write("No choices in the response.\n")
                    for choice in choices:
                        finish_reason = choice.finish_reason
                        index = choice.index
                        log_probs = choice.logprobs
                        if log_probs is not None:
                            log_probs = log_probs.model_dump_json()
                        else:
                            log_probs = "None"
                        f.write(
                            f"\n\n------------ Choice {index} {finish_reason} Probs: {log_probs} ------------\n"
                        )
                        message = choice.message

                        content = message.content
                        refusal = message.refusal
                        annotations = message.annotations
                        audio = message.audio
                        function_call = message.function_call
                        tool_calls = message.tool_calls

                        if content is not None:
                            f.write(f"{content}\n")

                        if refusal is not None:
                            f.write(f"Refusal: {refusal}\n")

                        if annotations is not None and len(annotations) > 0:
                            f.write("Annotations:\n")
                            for annotation in annotations:
                                f.write(f"{annotation.model_dump_json()}\n")

                        if audio is not None:
                            f.write(f"Audio: {audio.model_dump_json()}\n")

                        if function_call is not None:
                            f.write(
                                f"Function Call: {function_call.model_dump_json()}\n"
                            )

                        if tool_calls is not None:
                            f.write("Tool Calls:\n")
                            for tool_call in tool_calls:
                                f.write(f"{tool_call.model_dump_json()}\n")

        if self.gpt_log is not None:
            messages_str = json.dumps(messages, ensure_ascii=False)
            output_str = self._to_json_str(output) if output is not None else None
            log_content = {
                "timestamp": datetime.datetime.now().isoformat(),
                "messages": messages_str,
                "output": output_str,
                "is_from_cache": is_from_cache,
                "is_error": is_error,
                "error_message": err_msg,
            }
            log_content_str = json.dumps(log_content, ensure_ascii=False) + "\n"
            self.gpt_log.write(log_content_str.encode("utf-8"))
