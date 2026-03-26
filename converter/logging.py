from pathlib import Path


class ConsoleLogger:
    def __init__(self, quiet: bool = False) -> None:
        self.quiet = quiet

    def info(self, message: str) -> None:
        if not self.quiet:
            print(message)

    def converting_docx(self) -> None:
        self.info("Converting to DOCX...")

    def converting_pdf(self) -> None:
        self.info("Converting to PDF...")

    def fallback_pdf(self) -> None:
        self.info("Direct PDF failed; trying DOCX-based fallback...")

    def saved_to(self, path: Path) -> None:
        self.info(f"Saved to {path}")
