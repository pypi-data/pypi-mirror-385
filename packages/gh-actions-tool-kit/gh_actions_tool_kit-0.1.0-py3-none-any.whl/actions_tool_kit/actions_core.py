# actions_core.py
# Minimal Python equivalent of @actions/core for GitHub Actions (typed + docstrings)
from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import Any, ContextManager, Iterable, Optional, Union

def _file_from_env(var: str) -> Optional[str]:
    """Return the path from an env var if set and non-empty, else None.

    Args:
        var: Environment variable name.

    Returns:
        The string path if present, otherwise None.
    """
    p: Optional[str] = os.getenv(var)
    return p if p and p.strip() else None

def _append_line(filepath: str, line: str) -> None:
    """Append a single line to a file, ensuring a trailing newline.

    Args:
        filepath: Target file path.
        line: Line content (newline will be added if missing).
    """
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")

def _serialize_props(**props: Any) -> str:
    """Serialize command properties per workflow command format with escaping.

    Note:
        See GH Actions 'workflow commands' docs for escaping rules.

    Returns:
        A string like " key=val,key2=val2" or empty string if no props.
    """
    def esc(val: Any) -> str:
        s = str(val)
        return (
            s.replace("%", "%25")
            .replace("\r", "%0D")
            .replace("\n", "%0A")
            .replace(":", "%3A")
            .replace(",", "%2C")
        )

    items: list[str] = [
        f"{k}={esc(v)}" for k, v in props.items() if v not in (None, "", False)
    ]
    return " " + ",".join(items) if items else ""

def _escape_msg(msg: Union[str, Any]) -> str:
    """Escape a command message payload per GH runner rules.

    Args:
        msg: Message to escape.

    Returns:
        Escaped message.
    """
    s = str(msg)
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")

def _cmd(command: str, message: str = "", **props: Any) -> None:
    """Emit a raw workflow command to stdout.

    Args:
        command: Command verb (e.g., 'notice', 'warning').
        message: Optional message body.
        **props: Optional command properties such as title=, file=, line=.
    """
    sys.stdout.write(f"::{command}{_serialize_props(**props)}::{_escape_msg(message)}\n")
    sys.stdout.flush()

# ---------- inputs ----------
def get_input(
    name: str,
    *,
    required: bool = False,
    trim: bool = True,
    default: Optional[str] = None,
) -> str:
    """Read an action input from environment (INPUT_<NAME>).

    Args:
        name: Input name as defined in workflow 'with:' (case-insensitive).
        required: If True, raise if missing and also emit a failed error.
        trim: If True, strip surrounding whitespace.
        default: Optional default if not provided.

    Returns:
        The input value (possibly empty string if not required and missing).

    Raises:
        RuntimeError: If required is True and the input is missing.
    """
    key = f"INPUT_{name.replace(' ', '_').upper()}"
    val: Optional[str] = os.getenv(key)
    if val is None or val == "":
        if default is not None:
            return default
        if required:
            set_failed(f"Input required and not supplied: {name}")
            raise RuntimeError(f"Missing required input: {name}")
        return ""
    return val.strip() if trim else val

def get_boolean_input(
    name: str,
    *,
    required: bool = False,
    trim: bool = True,
    default: Optional[str] = None,
) -> bool:
    """Read a boolean action input.

    Accepts truthy values: 1, true, t, yes, y, on (case-insensitive).

    Args:
        name: Input name.
        required: If True, raise when missing.
        trim: If True, strip whitespace.
        default: Default string passed through truthy check if provided.

    Returns:
        Parsed boolean value.
    """
    val: str = get_input(name, required=required, trim=trim, default=default)
    return val.strip().lower() in {"1", "true", "t", "yes", "y", "on"}

# ---------- outputs / env / path / state / summary ----------
def set_output(name: str, value: Union[str, int, float, bool]) -> None:
    """Set a step output using $GITHUB_OUTPUT, with legacy fallback.

    Args:
        name: Output variable name.
        value: Output value; will be stringified.
    """
    v = str(value)
    path: Optional[str] = _file_from_env("GITHUB_OUTPUT")
    if not path:
        _cmd("set-output", f"{name}={v}")  # legacy/local fallback
        return
    _append_line(path, f"{name}={v}")

def export_variable(name: str, value: Union[str, int, float, bool]) -> None:
    """Export an environment variable for subsequent steps.

    Args:
        name: Variable name.
        value: Value; will be stringified.
    """
    v = str(value)
    path: Optional[str] = _file_from_env("GITHUB_ENV")
    if not path:
        os.environ[name] = v  # local fallback
        return
    _append_line(path, f"{name}={v}")

def add_path(input_path: str) -> None:
    """Prepend a path to the runner PATH for subsequent steps.

    Args:
        input_path: Directory to add to PATH.
    """
    path: Optional[str] = _file_from_env("GITHUB_PATH")
    if not path:
        os.environ["PATH"] = f"{input_path}{os.pathsep}{os.environ.get('PATH','')}"
        return
    _append_line(path, input_path)

def save_state(name: str, value: Union[str, int, float, bool]) -> None:
    """Persist state for the post-step using $GITHUB_STATE (runner-managed).

    Note:
        When not running on the runner (local tests), this function stores
        the value in process env under STATE_<name> as a convenience.

    Args:
        name: State key.
        value: State value; will be stringified.
    """
    v = str(value)
    path: Optional[str] = _file_from_env("GITHUB_STATE")
    if not path:
        os.environ[f"STATE_{name}"] = v  # local fallback
        return
    _append_line(path, f"{name}={v}")

def get_state(name: str) -> str:
    """Return locally saved state (testing fallback only).

    Note:
        On the real runner, post-steps read $GITHUB_STATE file directly.
        This helper only returns the local fallback (STATE_<name>).

    Args:
        name: State key.

    Returns:
        The value if set via local fallback; empty string otherwise.
    """
    return os.getenv(f"STATE_{name}", "")

def set_secret(secret: str) -> None:
    """Mask a secret in the logs using 'add-mask' command.

    Args:
        secret: The sensitive string to mask.
    """
    _cmd("add-mask", secret)

def append_summary(markdown: Union[str, Iterable[str]]) -> None:
    """Append markdown to the step summary panel.

    Args:
        markdown: Markdown string or iterable of chunks.

    Note:
        When $GITHUB_STEP_SUMMARY is not set (local runs), content is printed
        between markers to stdout for easy preview.
    """
    body: str = "".join(markdown) if not isinstance(markdown, str) else markdown
    path: Optional[str] = _file_from_env("GITHUB_STEP_SUMMARY")
    if not path:
        sys.stdout.write("\n--- STEP SUMMARY (local) ---\n" + body + "\n----------------------------\n")
        sys.stdout.flush()
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(body)

# ---------- logging / annotations ----------
def debug(message: Union[str, Any]) -> None:
    """Emit a debug annotation (visible when step debug is enabled)."""
    _cmd("debug", str(message))

def notice(
    message: Union[str, Any],
    *,
    title: Optional[str] = None,
    file: Optional[str] = None,
    line: Optional[int] = None,
    col: Optional[int] = None,
) -> None:
    """Emit a non-fatal informational annotation (blue box in UI).

    Args:
        message: The content to display.
        title: Optional short title shown in UI.
        file: Optional file path to attach to annotation.
        line: Optional line number.
        col: Optional column number.
    """
    _cmd("notice", str(message), title=title, file=file, line=line, col=col)

def warning(
    message: Union[str, Any],
    *,
    title: Optional[str] = None,
    file: Optional[str] = None,
    line: Optional[int] = None,
    col: Optional[int] = None,
) -> None:
    """Emit a warning annotation (yellow)."""
    _cmd("warning", str(message), title=title, file=file, line=line, col=col)

def error(
    message: Union[str, Any],
    *,
    title: Optional[str] = None,
    file: Optional[str] = None,
    line: Optional[int] = None,
    col: Optional[int] = None,
) -> None:
    """Emit an error annotation (red)."""
    _cmd("error", str(message), title=title, file=file, line=line, col=col)

def set_failed(message: Union[str, Any]) -> None:
    """Mark the step as failed by emitting an error annotation.

    Note:
        This function does NOT exit the process. Callers may raise or sys.exit(1).
    """
    error(str(message))

# ---------- groups ----------
def start_group(name: str) -> None:
    """Start a collapsible log group with the given name."""
    _cmd("group", name)

def end_group() -> None:
    """End the current collapsible log group."""
    _cmd("endgroup")

@contextmanager
def group(name: str) -> ContextManager[None]:
    """Context manager that wraps logs in a collapsible group.

    Example:
        with group("Install deps"):
            print("pip install ...")
    """
    start_group(name)
    try:
        yield
    finally:
        end_group()

__all__ = [
    "get_input",
    "get_boolean_input",
    "set_output",
    "export_variable",
    "add_path",
    "save_state",
    "get_state",
    "set_secret",
    "append_summary",
    "debug",
    "notice",
    "warning",
    "error",
    "set_failed",
    "start_group",
    "end_group",
    "group",
]
