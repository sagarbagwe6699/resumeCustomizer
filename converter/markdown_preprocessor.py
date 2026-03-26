from typing import Optional


def select_section(markdown: str, marker: Optional[str]) -> str:
    """
    Placeholder extension hook for future section extraction.
    For now this returns original markdown unchanged.
    """
    _ = marker
    return markdown
