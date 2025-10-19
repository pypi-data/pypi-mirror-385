"""Utility helpers for process execution and interpreter discovery."""

import os
import subprocess
from packaging.version import Version
import threading
import sys
import shutil
from typing import Optional, Callable, Sequence, Mapping, Union
from pathlib import Path
import asyncio


def locate_system_pythons() -> list[dict]:
    """Discover available system Python interpreters.

    Uses `where` on Windows and `which` on POSIX to find `python`
    executables, then probes each for its version.

    Returns:
        list[dict]: A list of dicts with keys `executable` and `version`.

    Raises:
        ValueError: If discovery fails unexpectedly.
    """
    try:
        # Use 'where' on Windows and 'which' on Unix-based systems
        command = "where" if os.name == "nt" else "which"
        result = subprocess.run([command, "python"], capture_output=True, text=True)
        pyths = []
        for line in result.stdout.strip().splitlines():
            try:
                versionresult = subprocess.run(
                    [line, "--version"], check=True, capture_output=True, text=True
                )
                vers_string = versionresult.stdout
                vers_string = Version(vers_string.split()[-1])

            except Exception:
                continue

            if not vers_string:
                continue
            dat = {
                "executable": line,
                "version": vers_string,
            }

            pyths.append(dat)
        if not pyths:
            raise ValueError("No suitable system Python found.")
        return pyths
    except Exception as exc:
        raise ValueError("Failed to locate system Python.") from exc


def run_subprocess_with_streams(args, stdout_callback=None, stderr_callback=None):
    """Run a subprocess and stream stdout/stderr to callbacks.

    Args:
        args (list[str]): Command and arguments to execute.
        stdout_callback (Callable[[str], None] | None): Callback for stdout lines.
        stderr_callback (Callable[[str], None] | None): Callback for stderr lines.

    Raises:
        ValueError: If the process returns a non-zero exit code.
    """
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Define a function to read and forward each stream in a separate thread
    def read_stream(stream, callback):
        """Read lines from a stream and forward to a callback."""
        for line in iter(stream.readline, ""):
            if callback:
                callback(line)
        stream.close()

    # Start threads for stdout and stderr
    stdout_thread = threading.Thread(
        target=read_stream, args=(process.stdout, stdout_callback)
    )
    stderr_thread = threading.Thread(
        target=read_stream, args=(process.stderr, stderr_callback)
    )

    stdout_thread.start()
    stderr_thread.start()

    # Wait for both threads to complete
    stdout_thread.join()
    stderr_thread.join()

    # Wait for the process to complete
    process.wait()

    if process.returncode != 0:
        raise ValueError(
            f"Failed to call {' '.join(args)}"
        ) from subprocess.CalledProcessError(process.returncode, process.args)


def get_python_executable() -> str:
    """
    Get the Python executable path.
    Handles PyInstaller packaging scenarios where `sys.executable`
    may not point to a valid Python interpreter.

    Returns:
        str: Path to the Python interpreter.
    """
    # Check if running in a PyInstaller environment
    if hasattr(sys, "_MEIPASS"):
        # Try to find a system Python
        python_path = shutil.which("python")
        if not python_path:
            raise RuntimeError("Could not locate a valid Python interpreter.")
        return python_path

    # Default to the current executable (should be a valid Python interpreter)
    return sys.executable


async def arun_subprocess_with_streams(
    args: Sequence[str],
    stdout_callback: Optional[Callable[[str], None]] = None,
    stderr_callback: Optional[Callable[[str], None]] = None,
    *,
    env: Optional[Mapping[str, str]] = None,
    cwd: Optional[Union[str, Path]] = None,
) -> tuple[int, str, str]:
    """Async variant of run_subprocess_with_streams with streaming callbacks."""
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
        cwd=str(cwd) if cwd is not None else None,
    )

    collected_out: list[str] = []
    collected_err: list[str] = []

    async def _forward(
        reader: asyncio.StreamReader,
        cb: Optional[Callable[[str], None]],
        collector: list[str],
    ):
        while True:
            chunk = await reader.readline()
            if not chunk:
                break
            line = chunk.decode(errors="replace")
            collector.append(line)
            if cb:
                res = cb(line)
                if asyncio.iscoroutine(res):
                    await res

    try:
        await asyncio.wait(
            [
                asyncio.create_task(
                    _forward(proc.stdout, stdout_callback, collected_out)
                ),
                asyncio.create_task(
                    _forward(proc.stderr, stderr_callback, collected_err)
                ),
            ],
            return_when=asyncio.ALL_COMPLETED,
        )
        returncode = await proc.wait()
    except asyncio.CancelledError:
        try:
            proc.terminate()
        except ProcessLookupError:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=3)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            await proc.wait()
        raise

    if returncode != 0:
        raise ValueError(f"Failed to call {' '.join(args)}")

    return returncode, "".join(collected_out), "".join(collected_err)


async def alocate_system_pythons():
    """Async wrapper around locate_system_pythons using a worker thread."""
    return await asyncio.to_thread(locate_system_pythons)
