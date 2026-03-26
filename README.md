# Markdown Resume Converter

Python CLI for converting Markdown resumes to DOCX and optional PDF using Pandoc.

## Usage

```bash
python convert.py resume.md
python convert.py resume.md --format pdf
python convert.py resume.md --format both --template ./template.docx
```

## Defaults

- Input: required markdown path.
- Default format: `docx`.
- Default template: `template.docx` in the same directory as input.
- Default output directory: same directory as input.

## Install test dependencies

```bash
python -m pip install pytest
```

## Run tests

```bash
pytest -q
```
