from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class ExtractedResume:
    company: str
    markdown: str


_JOB_HEADER_RE = re.compile(
    r"^#\s*JOB\s+(?P<job_num>\d+)\s*:\s*(?P<role>.*?)\s+—\s+(?P<company>.*?)(?:\s*\(.*\))?\s*$",
    re.MULTILINE,
)


def _slugify_company(name: str) -> str:
    slug = re.sub(r"[^\w]+", "_", name.strip(), flags=re.UNICODE).strip("_")
    return slug or "UnknownCompany"


def _iter_job_blocks(text: str) -> Iterable[tuple[str, str]]:
    """
    Yields (company, block_text) for each '# JOB n: ... — Company ...' section.
    """
    matches = list(_JOB_HEADER_RE.finditer(text))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        company = m.group("company").strip()
        yield company, text[start:end]


def _extract_resume_markdown(job_block: str) -> Optional[str]:
    """
    Within a JOB block, keep only the actual resume content (starts at '## SAGAR BAGWE').
    """
    marker = "## SAGAR BAGWE"
    idx = job_block.find(marker)
    if idx == -1:
        return None
    md = job_block[idx:].strip() + "\n"
    return md


def extract_resumes(text: str) -> List[ExtractedResume]:
    resumes: List[ExtractedResume] = []
    for company, block in _iter_job_blocks(text):
        md = _extract_resume_markdown(block)
        if md is None:
            continue
        resumes.append(ExtractedResume(company=company, markdown=md))
    return resumes


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Split a multi-job optimized resume markdown into per-company folders and generate DOCX outputs."
    )
    p.add_argument(
        "--input",
        required=True,
        help="Path to the optimized markdown file containing multiple JOB sections.",
    )
    p.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parent / "template.docx"),
        help="Path to template.docx (default: template.docx in project root).",
    )
    p.add_argument(
        "--output-root",
        default=str(Path(__file__).resolve().parent / "output"),
        help="Root output directory (default: ./output).",
    )
    p.add_argument(
        "--format",
        choices=("docx", "pdf", "both"),
        default="docx",
        help="Output format to generate (default: docx).",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output and print only errors.",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    input_path = Path(args.input).expanduser().resolve()
    template_path = Path(args.template).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    text = input_path.read_text(encoding="utf-8")
    resumes = extract_resumes(text)
    if not resumes:
        raise SystemExit(
            f"No resumes extracted from {input_path}. Expected '# JOB n: ... — <Company>' and '## SAGAR BAGWE' markers."
        )

    # Import here so this script can be used for extraction-only if desired.
    from converter.cli import main as convert_main

    for r in resumes:
        company_dir = output_root / _slugify_company(r.company)
        company_dir.mkdir(parents=True, exist_ok=True)

        md_path = company_dir / "resume.md"
        md_path.write_text(r.markdown, encoding="utf-8")

        convert_args = [
            str(md_path),
            "--format",
            args.format,
            "--template",
            str(template_path),
            "--output-dir",
            str(company_dir),
        ]
        if args.quiet:
            convert_args.append("--quiet")

        rc = convert_main(convert_args)
        if rc != 0:
            return rc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

