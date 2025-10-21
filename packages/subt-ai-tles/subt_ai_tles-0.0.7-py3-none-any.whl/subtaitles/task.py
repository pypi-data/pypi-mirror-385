from __future__ import annotations

import asyncio
from asyncio import Task
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .providers import get_translator
from .translate import translate_srt_file

if TYPE_CHECKING:
    from .language import Lang
    from .providers.protocol import TranslateProtocol
    from .translate import Engine


@dataclass
class TranslateTaskData:
    path: Path
    source: Lang
    target: Lang
    new_path: Path


@dataclass
class ProgressData:
    total: int
    current: int


class TranslateTask:
    def __init__(
        self, task_data: TranslateTaskData, translator: Engine | TranslateProtocol
    ) -> None:
        self.task_data = task_data
        if not hasattr(translator, "translate"):
            translator = get_translator(translator)
        self.translator = translator
        self.progress = ProgressData(total=0, current=0)
        self.task: Task | None = None

    def run(self) -> None:
        self.task = asyncio.create_task(
            translate_srt_file(
                path=self.task_data.path,
                new_path=self.task_data.new_path,
                translator=self.translator,
                source=self.task_data.source,
                target=self.task_data.target,
                progress=self.progress,
            )
        )

    @property
    def is_done(self) -> bool:
        return self.task.done()

    @property
    def exception(self) -> BaseException | None:
        return self.task.exception()


def get_translate_task(
    path: Path | str,
    new_path: Path | str,
    source: Lang,
    target: Lang,
    translator: Engine | TranslateProtocol,
) -> TranslateTask:
    path = Path(path)
    new_path = Path(new_path)
    if not path.exists():
        msg = "Supplied path does NOT exist"
        raise FileNotFoundError(msg)

    return TranslateTask(
        task_data=TranslateTaskData(
            path=path,
            new_path=new_path,
            source=source,
            target=target,
        ),
        translator=translator,
    )
