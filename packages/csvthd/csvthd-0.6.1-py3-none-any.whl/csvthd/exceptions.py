"""Collection of custom exception classes."""


class EmptyTransactionFile(RuntimeError):
    """Raised when a transaction file is read that doesn't contain any transactions."""

    def __init__(self, filepath, *args, **kwargs):
        self.filepath = filepath
        super().__init__(*args, **kwargs)


class AmountColumnUnparsable(ValueError):
    """Raised when the amount column cannot be successfully parsed."""

    def __init__(self, _input, filepath, row_index, *args, **kwargs):
        self._input = _input
        self.filepath = filepath
        self.row_index = row_index
        super().__init__(*args, **kwargs)
