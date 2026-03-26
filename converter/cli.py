import argparse
from typing import List, Optional

from .conversion_service import ConversionResult, convert_both, convert_docx, convert_pdf
from .errors import ConverterError
from .logging import ConsoleLogger
from .paths import resolve_request


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Markdown resumes to ATS-friendly DOCX/PDF via Pandoc."
    )
    parser.add_argument("input", help="Path to input markdown file.")
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=("docx", "pdf", "both"),
        default="docx",
        help="Output format to generate (default: docx).",
    )
    parser.add_argument(
        "--template",
        dest="template_path",
        default=None,
        help="Path to DOCX template (default: template.docx next to input).",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default=None,
        help="Directory for generated files (default: input file directory).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output and print only errors.",
    )
    return parser


def _execute(args: argparse.Namespace) -> ConversionResult:
    request = resolve_request(
        input_path=args.input,
        output_format=args.output_format,
        template_path=args.template_path,
        output_dir=args.output_dir,
        quiet=args.quiet,
    )
    logger = ConsoleLogger(quiet=request.quiet)

    if request.format == "docx":
        docx = convert_docx(request, logger)
        return ConversionResult(docx_path=docx)
    if request.format == "pdf":
        pdf = convert_pdf(request, logger)
        return ConversionResult(pdf_path=pdf)
    return convert_both(request, logger)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        _execute(args)
        return 0
    except ConverterError as exc:
        print(f"Error: {exc}")
        return 2
