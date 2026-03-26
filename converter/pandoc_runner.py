from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os
import platform
import subprocess
from typing import Dict, List, Optional

from .errors import ConversionFailedError, PandocNotInstalledError


@dataclass(frozen=True)
class CommandResult:
    command: List[str]
    stderr: str


def build_markdown_to_docx_cmd(input_md: Path, output_docx: Path, template_docx: Path) -> List[str]:
    # fenced_divs + bracketed_spans enable custom Word styles via {custom-style="..."} in Markdown.
    return [
        "pandoc",
        "-f",
        "markdown+fenced_divs+bracketed_spans",
        str(input_md),
        "-o",
        str(output_docx),
        "--reference-doc",
        str(template_docx),
    ]


def build_markdown_to_pdf_cmd(input_md: Path, output_pdf: Path) -> List[str]:
    return ["pandoc", str(input_md), "-o", str(output_pdf)]


def build_docx_to_pdf_cmd(input_docx: Path, output_pdf: Path) -> List[str]:
    return ["pandoc", str(input_docx), "-o", str(output_pdf)]


@lru_cache(maxsize=1)
def ensure_pandoc_available() -> None:
    try:
        subprocess.run(
            ["pandoc", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise PandocNotInstalledError("Pandoc is not installed or not available in PATH.") from exc


def _pandoc_subprocess_env() -> Optional[Dict[str, str]]:
    """Prepend common TeX Live paths so Pandoc can find pdflatex / xelatex."""
    extra_dirs: List[str] = []
    if platform.system() == "Darwin":
        extra_dirs.append("/Library/TeX/texbin")
    for d in extra_dirs:
        if Path(d).is_dir():
            env = os.environ.copy()
            env["PATH"] = f"{d}{os.pathsep}{env.get('PATH', '')}"
            return env
    return None


def run_pandoc(command: List[str]) -> CommandResult:
    ensure_pandoc_available()
    env = _pandoc_subprocess_env()
    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env if env is not None else os.environ,
    )
    if process.returncode != 0:
        stderr = (process.stderr or "").strip()
        raise ConversionFailedError("Pandoc conversion failed.", stderr=stderr)
    return CommandResult(command=command, stderr=(process.stderr or "").strip())
