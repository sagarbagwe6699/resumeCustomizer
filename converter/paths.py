from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .errors import InputFileNotFoundError, TemplateNotFoundError


@dataclass(frozen=True)
class ConversionRequest:
    input_path: Path
    template_path: Path
    output_dir: Path
    format: str
    quiet: bool = False

    @property
    def docx_output(self) -> Path:
        return self.output_dir / f"{self.input_path.stem}.docx"

    @property
    def pdf_output(self) -> Path:
        return self.output_dir / f"{self.input_path.stem}.pdf"


def resolve_request(
    input_path: str,
    output_format: str = "docx",
    template_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    quiet: bool = False,
) -> ConversionRequest:
    resolved_input = Path(input_path).expanduser().resolve()
    if not resolved_input.exists() or not resolved_input.is_file():
        raise InputFileNotFoundError(f"Input markdown file not found: {resolved_input}")

    resolved_template = (
        Path(template_path).expanduser().resolve()
        if template_path
        else (resolved_input.parent / "template.docx").resolve()
    )
    # For pdf-only flow, template is only needed if fallback to DOCX happens.
    # We still validate when the user explicitly provides --template.
    should_validate_template = bool(template_path) or output_format in ("docx", "both")
    if should_validate_template and (
        not resolved_template.exists() or not resolved_template.is_file()
    ):
        raise TemplateNotFoundError(
            f"DOCX template not found: {resolved_template}. "
            "Provide a valid template via --template."
        )

    resolved_output_dir = (
        Path(output_dir).expanduser().resolve() if output_dir else resolved_input.parent
    )
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    return ConversionRequest(
        input_path=resolved_input,
        template_path=resolved_template,
        output_dir=resolved_output_dir,
        format=output_format,
        quiet=quiet,
    )
