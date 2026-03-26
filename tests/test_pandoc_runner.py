from pathlib import Path

from converter.pandoc_runner import (
    build_docx_to_pdf_cmd,
    build_markdown_to_docx_cmd,
    build_markdown_to_pdf_cmd,
)


def test_build_markdown_to_docx_command() -> None:
    cmd = build_markdown_to_docx_cmd(
        Path("resume.md"), Path("resume.docx"), Path("template.docx")
    )
    assert cmd == [
        "pandoc",
        "-f",
        "markdown+fenced_divs+bracketed_spans",
        "resume.md",
        "-o",
        "resume.docx",
        "--reference-doc",
        "template.docx",
    ]


def test_build_markdown_to_pdf_command() -> None:
    cmd = build_markdown_to_pdf_cmd(Path("resume.md"), Path("resume.pdf"))
    assert cmd == ["pandoc", "resume.md", "-o", "resume.pdf"]


def test_build_docx_to_pdf_command() -> None:
    cmd = build_docx_to_pdf_cmd(Path("resume.docx"), Path("resume.pdf"))
    assert cmd == ["pandoc", "resume.docx", "-o", "resume.pdf"]
