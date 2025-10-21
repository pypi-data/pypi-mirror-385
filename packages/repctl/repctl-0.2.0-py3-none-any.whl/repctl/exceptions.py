class RepctlException(Exception):
    def __init__(self, msg, *args) -> None:
        super().__init__(*args)
        self.msg = msg

    def __str__(self):
        return f"{super().__str__()}{self.msg}"


class SnippetParsingException(RepctlException): ...


class InvalidScubaReport(RepctlException): ...
