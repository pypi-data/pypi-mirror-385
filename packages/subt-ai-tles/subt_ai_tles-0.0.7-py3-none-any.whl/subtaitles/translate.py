from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING

import pysrt
from pysrt import SubRipFile

from .exceptions import FailedToTranslateError
from .providers import Engine, TranslateProtocol, get_translator
from .srt import strip_srt_markup

if TYPE_CHECKING:
    from .language import Lang
    from .providers.protocol import Progress


logger = logging.getLogger(__name__)


async def translate_srt(
    srt: SubRipFile,
    source: Lang,
    target: Lang,
    translator: Engine | TranslateProtocol,
    progress: Progress | None = None,
) -> SubRipFile:
    """Translate subtitle file (.srt) a parsed SubRipFile object.

    :param srt: parsed srt file
    :param source: source language
    :param target: target language
    :param translator: translation engine or translator instance
    :param progress: progress object
    :return: translated subtitle file as SubRipFile object
    """
    if not hasattr(translator, "translate"):
        translator = get_translator(translator)

    translations = await translator.translate(
        strip_srt_markup([item.text for item in srt]), source, target, progress
    )

    result = SubRipFile(items=[])
    for item, translation in zip(srt, translations, strict=False):
        new_item = deepcopy(item)
        new_item.text = translation
        result.append(new_item)

    return result


async def translate_srt_file(  # noqa: PLR0913
    path: Path | str,
    source: Lang,
    target: Lang,
    translator: Engine | TranslateProtocol,
    new_path: Path | str | None = None,
    progress: Progress | None = None,
) -> Path:
    """Translate subtitle file (.srt) given a path on the local filesystem.

    :param path: filesystem path to the srt source file
    :param source: source language
    :param target: target language
    :param translator: translation engine type or translator instance
    :param new_path: arbitrary path to the new file with translated subtitles
    :param progress: progress object
    :return: path to the new file with translated subtitles
    """
    try:
        path = Path(path)
        logger.info("Translating subtitle file %s", path)
        filename, ext = path.name.rsplit(".", 1)
        new_path = Path(new_path) or path.parent / f"{filename}-{target}.{ext}"
        srt = pysrt.open(path.absolute())

        result = await translate_srt(srt, source, target, translator, progress)
        with new_path.open("w") as file:
            result.write_into(file)

        logger.info("Translated subtitles written to %s", new_path)
    except ValueError as exc:
        raise FailedToTranslateError(path, new_path, f"Translator failed: {exc}") from exc
    except Exception as exc:
        raise FailedToTranslateError(path, new_path, f"Unexpected error: {exc}") from exc
    else:
        return new_path
