from __future__ import annotations


class ValidationError(Exception):
    def __init__(self, message: str, path: list[str | int] | None = None) -> None:
        self.message: str = message
        self.path: list[str | int] = path or []

        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if not self.path:
            return self.message

        path_str: str = self._format_path()
        return f"Validation failed at {path_str}: {self.message}"

    def _format_path(self) -> str:
        parts: list[str] = []
        for segment in self.path:
            if isinstance(segment, int):
                parts.append(f"[{segment}]")
            elif parts:
                parts.append(f".{segment}")
            else:
                parts.append(segment)
        return "".join(parts)

    def add_path(self, segment: str | int) -> ValidationError:
        self.path.insert(0, segment)
        self.args = (self._format_message(),)
        return self
