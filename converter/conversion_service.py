from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .errors import ConversionFailedError, PdfFallbackFailedError, TemplateNotFoundError
from .logging import ConsoleLogger
from .pandoc_runner import (
    build_docx_to_pdf_cmd,
    build_markdown_to_docx_cmd,
    build_markdown_to_pdf_cmd,
    run_pandoc,
)
from .paths import ConversionRequest


@dataclass
class ConversionResult:
    docx_path: Optional[Path] = None
    pdf_path: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)


def _is_pdf_engine_failure(stderr: str) -> bool:
    lowered = stderr.lower()
    hints = (
        "xelatex",
        "pdflatex",
        "lualatex",
        "latex",
        "wkhtmltopdf",
        "pdf-engine",
    )
    return any(hint in lowered for hint in hints)


def convert_docx(request: ConversionRequest, logger: ConsoleLogger) -> Path:
    if not request.template_path.exists() or not request.template_path.is_file():
        raise TemplateNotFoundError(
            f"DOCX template not found: {request.template_path}. "
            "Provide a valid template via --template."
        )
    logger.converting_docx()
    command = build_markdown_to_docx_cmd(
        request.input_path, request.docx_output, request.template_path
    )
    run_pandoc(command)
    logger.saved_to(request.docx_output)
    return request.docx_output


def convert_pdf(
    request: ConversionRequest,
    logger: ConsoleLogger,
    existing_docx: Optional[Path] = None,
) -> Path:
    logger.converting_pdf()
    command = build_markdown_to_pdf_cmd(request.input_path, request.pdf_output)
    try:
        run_pandoc(command)
        logger.saved_to(request.pdf_output)
        return request.pdf_output
    except ConversionFailedError as exc:
        if not _is_pdf_engine_failure(exc.stderr):
            raise

        logger.fallback_pdf()
        docx_path = existing_docx if existing_docx and existing_docx.exists() else convert_docx(request, logger)
        fallback_command = build_docx_to_pdf_cmd(docx_path, request.pdf_output)
        try:
            run_pandoc(fallback_command)
            logger.saved_to(request.pdf_output)
            return request.pdf_output
        except ConversionFailedError as fallback_exc:
            raise PdfFallbackFailedError(
                f"PDF fallback also failed. Pandoc said: {fallback_exc.stderr}"
            ) from fallback_exc


def convert_both(request: ConversionRequest, logger: ConsoleLogger) -> ConversionResult:
    docx_path = convert_docx(request, logger)
    pdf_path = convert_pdf(request, logger, existing_docx=docx_path)
    return ConversionResult(docx_path=docx_path, pdf_path=pdf_path)
