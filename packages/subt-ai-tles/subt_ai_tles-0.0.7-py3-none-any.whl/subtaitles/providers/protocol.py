from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from subtaitles.language import Lang


class Progress(Protocol):
    total: int
    current: int


class TranslateProtocol(Protocol):
    async def translate(
        self,
        text: list[str],
        language_from: Lang,
        language_to: Lang,
        progress: Progress | None = None,
    ) -> list[str]: ...
