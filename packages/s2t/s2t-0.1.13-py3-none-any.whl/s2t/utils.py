from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np


def check_dependency(cmd: str, install_hint: str) -> None:
    if shutil.which(cmd) is None:
        raise RuntimeError(f"Dependency '{cmd}' not found. Hint: {install_hint}")


def convert_wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    check_dependency(
        "ffmpeg",
        "macOS: brew install ffmpeg; Linux: apt/yum; Windows: install ffmpeg and add to PATH",
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(wav_path),
        "-vn",
        "-acodec",
        "libmp3lame",
        "-q:a",
        "2",
        str(mp3_path),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


# Baseline at program start for relative timestamps in verbose logs
_START_TIME = time.perf_counter()


def debug_log(verbose: bool, component: str, msg: str) -> None:
    """Emit a timestamped debug line to stderr if verbose is enabled.

    Args:
        verbose: Whether verbose mode is active.
        component: Short component tag (e.g., 'recorder', 'whisper', 'cli', 'argos').
        msg: Message to print.
    """
    if not verbose:
        return
    elapsed = time.perf_counter() - _START_TIME
    # Elapsed with milliseconds precision
    print(f"[+{elapsed:.3f}s] [{component}] {msg}", file=sys.stderr, flush=True)


def copy_to_clipboard(text: str) -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return
        if system == "Windows":
            subprocess.run(["clip"], input=text, text=True, check=True)
            return
        if shutil.which("xclip"):
            subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
            return
        if shutil.which("xsel"):
            subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
            return
        try:
            import pyperclip

            pyperclip.copy(text)
            return
        except Exception:
            pass
    except Exception as e:
        print(f"Copy to clipboard failed: {e}", file=sys.stderr)
        return
    print("No clipboard tool found (pbcopy/clip/xclip/xsel). Optional: pip install pyperclip.")


def open_in_shell_editor(file_path: Path) -> tuple[bool, str]:
    """Open the given file in a shell editor, respecting $VISUAL/$EDITOR.

    Behavior:
    - If $VISUAL or $EDITOR is set and found on PATH, run exactly that command.
    - Otherwise, choose the first available from a small fallback list.
    - Do not fall back to other editors based on the editor's exit code.
      A non-zero exit (e.g., Vim :cq) is treated as "opened but aborted" and
      reported as a failure to the caller without trying another editor.

    Returns:
        (opened_ok, used_cmd)
        opened_ok is True only if the editor exited with code 0.
        used_cmd is the command string that was attempted (empty if none found).
    """
    env_editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")

    def _parse_cmd(cmd: str) -> list[str]:
        import shlex as _shlex

        try:
            return _shlex.split(cmd)
        except Exception:
            return [cmd]

    chosen: list[str] | None = None
    if env_editor:
        argv = _parse_cmd(env_editor)
        if argv and shutil.which(argv[0]) is not None:
            chosen = argv
    if chosen is None:
        for argv in [["vim"], ["nvim"], ["nano"], ["micro"], ["notepad"]]:
            if shutil.which(argv[0]) is not None:
                chosen = argv
                break

    if chosen is None:
        return False, ""

    used = " ".join(chosen)
    try:
        # Run once; do not fall back on non-zero exit
        proc = subprocess.run(chosen + [str(file_path)], check=False)
        return (proc.returncode == 0), used
    except Exception:
        # Invocation failure (e.g., permission/OS error)
        return False, used


def make_session_dir(base_dir: Path | None = None) -> Path:
    ts = datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")
    base = Path(base_dir) if base_dir is not None else Path.cwd()
    base.mkdir(parents=True, exist_ok=True)
    session = base / ts
    session.mkdir(parents=True, exist_ok=False)
    return session


def resample_linear(x: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    if src_sr == dst_sr:
        return x.astype(np.float32, copy=False)
    x = x.astype(np.float32, copy=False)
    n_src = x.shape[0]
    n_dst = int(round(n_src * (dst_sr / float(src_sr))))
    if n_src == 0 or n_dst == 0:
        return np.zeros(n_dst, dtype=np.float32)
    src_t = np.linspace(0.0, 1.0, num=n_src, endpoint=False)
    dst_t = np.linspace(0.0, 1.0, num=n_dst, endpoint=False)
    return np.interp(dst_t, src_t, x).astype(np.float32)
