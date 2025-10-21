import os
from pathlib import Path
from typing import Callable

import pytest

import actions_core as core


def test_get_input_required_and_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # default when missing
    assert core.get_input("foo", default="bar") == "bar"

    # required raises
    with pytest.raises(RuntimeError):
        core.get_input("missing", required=True)

    # provided via env
    monkeypatch.setenv("INPUT_NAME", " Akash ")
    assert core.get_input("name") == "Akash"
    assert core.get_input("name", trim=False) == " Akash "


@pytest.mark.parametrize(
    "val,expected",
    [
        ("true", True),
        ("TrUe", True),
        ("1", True),
        ("yes", True),
        ("on", True),
        ("false", False),
        ("0", False),
        ("no", False),
        ("", False),
    ],
)
def test_get_boolean_input(monkeypatch: pytest.MonkeyPatch, val: str, expected: bool) -> None:
    monkeypatch.setenv("INPUT_FLAG", val)
    assert core.get_boolean_input("flag") is expected


def test_set_output_and_export_variable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "out.txt"
    envf = tmp_path / "env.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setenv("GITHUB_ENV", str(envf))

    core.set_output("result", "ok")
    core.export_variable("FOO", "bar")

    assert out.read_text().strip() == "result=ok"
    assert envf.read_text().strip() == "FOO=bar"


def test_add_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pathf = tmp_path / "path.txt"
    monkeypatch.setenv("GITHUB_PATH", str(pathf))
    core.add_path("/tool/bin")
    assert pathf.read_text().strip() == "/tool/bin"


def test_state_local_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    # No GITHUB_STATE -> uses local fallback
    core.save_state("TOKEN", "abc")
    assert core.get_state("TOKEN") == "abc"


def test_summary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    sumf = tmp_path / "sum.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(sumf))
    core.append_summary("# Hello\n")
    assert sumf.read_text() == "# Hello\n"


def test_notice_and_group(capsys: pytest.CaptureFixture[str]) -> None:
    core.notice("hello", title="greet", file="a.py", line=10)
    with core.group("Stuff"):
        print("inside")
    captured = capsys.readouterr().out.splitlines()
    # Notice line present
    assert any(l.startswith("::notice ") and "::hello" in l for l in captured)
    # Group markers present
    assert any(l.startswith("::group::Stuff") for l in captured)
    assert any(l == "::endgroup::" for l in captured)


def test_set_secret_masks_in_logs(capsys: pytest.CaptureFixture[str]) -> None:
    core.set_secret("supersecret")
    out = capsys.readouterr().out
    assert "::add-mask::supersecret" in out
