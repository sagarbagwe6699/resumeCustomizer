class ConverterError(Exception):
    """Base class for expected, user-facing converter errors."""


class PandocNotInstalledError(ConverterError):
    pass


class TemplateNotFoundError(ConverterError):
    pass


class InputFileNotFoundError(ConverterError):
    pass


class ConversionFailedError(ConverterError):
    def __init__(self, message: str, stderr: str = "") -> None:
        super().__init__(message)
        self.stderr = stderr


class PdfFallbackFailedError(ConverterError):
    pass
