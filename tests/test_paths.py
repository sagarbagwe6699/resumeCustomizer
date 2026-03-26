from pathlib import Path

import pytest

from converter.errors import InputFileNotFoundError, TemplateNotFoundError
from converter.paths import resolve_request


def test_resolve_request_defaults(tmp_path: Path) -> None:
    input_md = tmp_path / "resume.md"
    template = tmp_path / "template.docx"
    input_md.write_text("# Resume\n", encoding="utf-8")
    template.write_text("docx-template", encoding="utf-8")

    request = resolve_request(str(input_md))

    assert request.input_path == input_md.resolve()
    assert request.template_path == template.resolve()
    assert request.docx_output == tmp_path / "resume.docx"
    assert request.pdf_output == tmp_path / "resume.pdf"


def test_resolve_request_missing_input_raises(tmp_path: Path) -> None:
    with pytest.raises(InputFileNotFoundError):
        resolve_request(str(tmp_path / "missing.md"))


def test_resolve_request_missing_template_raises(tmp_path: Path) -> None:
    input_md = tmp_path / "resume.md"
    input_md.write_text("# Resume\n", encoding="utf-8")

    with pytest.raises(TemplateNotFoundError):
        resolve_request(str(input_md))


def test_resolve_request_pdf_allows_missing_default_template(tmp_path: Path) -> None:
    input_md = tmp_path / "resume.md"
    input_md.write_text("# Resume\n", encoding="utf-8")

    request = resolve_request(str(input_md), output_format="pdf")

    assert request.template_path == (tmp_path / "template.docx").resolve()
