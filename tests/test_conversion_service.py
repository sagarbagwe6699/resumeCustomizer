from pathlib import Path
from typing import List

import pytest

from converter.conversion_service import convert_pdf
from converter.errors import ConversionFailedError, PdfFallbackFailedError, TemplateNotFoundError
from converter.logging import ConsoleLogger
from converter.paths import ConversionRequest


def _request(tmp_path: Path) -> ConversionRequest:
    input_md = tmp_path / "resume.md"
    template = tmp_path / "template.docx"
    input_md.write_text("# Resume\n", encoding="utf-8")
    template.write_text("template", encoding="utf-8")
    return ConversionRequest(
        input_path=input_md,
        template_path=template,
        output_dir=tmp_path,
        format="pdf",
        quiet=True,
    )


def test_pdf_direct_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    request = _request(tmp_path)
    calls: List[List[str]] = []

    def fake_run(cmd: List[str]) -> object:
        calls.append(cmd)
        return object()

    monkeypatch.setattr("converter.conversion_service.run_pandoc", fake_run)
    pdf_path = convert_pdf(request, ConsoleLogger(quiet=True))

    assert pdf_path == request.pdf_output
    assert len(calls) == 1
    assert str(request.input_path) in calls[0]


def test_pdf_fallback_when_engine_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    request = _request(tmp_path)
    calls: List[List[str]] = []

    def fake_run(cmd: List[str]) -> object:
        calls.append(cmd)
        if len(calls) == 1:
            raise ConversionFailedError("failed", stderr="xelatex not found")
        return object()

    monkeypatch.setattr("converter.conversion_service.run_pandoc", fake_run)
    pdf_path = convert_pdf(request, ConsoleLogger(quiet=True))

    assert pdf_path == request.pdf_output
    assert len(calls) == 3  # direct pdf, docx, fallback pdf
    assert any(part.endswith(".md") for part in calls[0])
    assert any(part.endswith(".md") for part in calls[1])
    assert any(part.endswith(".docx") for part in calls[2])


def test_pdf_fallback_failure_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    request = _request(tmp_path)
    calls: List[List[str]] = []

    def fake_run(cmd: List[str]) -> object:
        calls.append(cmd)
        if len(calls) == 1:
            raise ConversionFailedError("failed", stderr="pdflatex missing")
        if len(calls) == 3:
            raise ConversionFailedError("failed again", stderr="still broken")
        return object()

    monkeypatch.setattr("converter.conversion_service.run_pandoc", fake_run)

    with pytest.raises(PdfFallbackFailedError):
        convert_pdf(request, ConsoleLogger(quiet=True))


def test_pdf_fallback_missing_template_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    request = _request(tmp_path)
    request.template_path.unlink()

    def fake_run(cmd: List[str]) -> object:
        if cmd[1].endswith(".md"):
            raise ConversionFailedError("failed", stderr="pdflatex missing")
        return object()

    monkeypatch.setattr("converter.conversion_service.run_pandoc", fake_run)

    with pytest.raises(TemplateNotFoundError):
        convert_pdf(request, ConsoleLogger(quiet=True))
