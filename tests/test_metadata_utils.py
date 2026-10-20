from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
import sys

import pytest


@pytest.fixture
def metadata_module(monkeypatch):
    package_name = "_isolated_metadata_test"
    package = ModuleType(package_name)
    package.__path__ = []
    media_utils = ModuleType(f"{package_name}.media_utils")

    async def get_streams(_):
        return []

    media_utils.get_streams = get_streams
    monkeypatch.setitem(sys.modules, package_name, package)
    monkeypatch.setitem(sys.modules, f"{package_name}.media_utils", media_utils)

    source = (
        Path(__file__).resolve().parent.parent
        / "bot"
        / "helper"
        / "ext_utils"
        / "metadata_utils.py"
    )
    spec = spec_from_file_location(f"{package_name}.metadata_utils", source)
    module = module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_parse_metadata_pairs_with_escaped_pipe(metadata_module):
    parsed = metadata_module.MetadataProcessor.parse_string(
        r"title=Movie|comment=Tamil \| Telugu|date={year}"
    )
    assert parsed == {
        "title": "Movie",
        "comment": "Tamil | Telugu",
        "date": "{year}",
    }


def test_parse_metadata_rejects_malformed_pair(metadata_module):
    with pytest.raises(ValueError, match="key=value"):
        metadata_module.MetadataProcessor.parse_string("title")


def test_command_metadata_overrides_matching_defaults(metadata_module):
    defaults = metadata_module.MetadataProcessor.parse_string(
        "title={basename}|comment=default"
    )
    command = metadata_module.MetadataProcessor.parse_string(
        "title=custom|artist={audiolang}"
    )
    merged = metadata_module.MetadataProcessor.merge_dicts(defaults, command)
    assert merged == {
        "title": "custom",
        "comment": "default",
        "artist": "{audiolang}",
    }


@pytest.mark.asyncio
async def test_metadata_variables_cover_movie_and_multi_stream_series(
    metadata_module, monkeypatch
):
    async def get_streams(_):
        return [
            {"index": 0, "codec_type": "video"},
            {"index": 1, "codec_type": "audio", "tags": {"language": "tam"}},
            {"index": 2, "codec_type": "audio", "tags": {"language": "hin"}},
            {"index": 3, "codec_type": "subtitle", "tags": {"language": "eng"}},
        ]

    monkeypatch.setattr(metadata_module, "get_streams", get_streams)
    processor = metadata_module.MetadataProcessor()

    movie = await processor.process_all(
        {"title": "{basename} ({year})"},
        {"comment": "Audio in {audiolang}"},
        {"title": "Subtitles in {sublang}"},
        "/downloads/Film (2026).mkv",
    )
    assert processor.vars["filename"] == "Film (2026).mkv"
    assert processor.vars["basename"] == "Film (2026)"
    assert processor.vars["extension"] == "mkv"
    assert processor.vars["year"] == "2026"
    assert processor.vars["audiolang"] == "Tamil"
    assert movie["video"]["title"] == "Film (2026) (2026)"
    assert movie["audio_streams"][0]["metadata"]["comment"] == "Audio in Tamil"
    assert movie["subtitle_streams"][0]["metadata"]["title"] == "Subtitles in English"

    series = await processor.process_all(
        {"title": "{basename}"},
        {"title": "{audiolang}"},
        {"title": "{sublang}"},
        "/downloads/Show S01E02 (2026).mkv",
    )
    assert processor.vars["filename"] == "Show S01E02 (2026).mkv"
    assert series["video"]["title"] == "Show S01E02 (2026)"
    assert [
        stream["metadata"]["title"] for stream in series["audio_streams"]
    ] == ["Tamil", "Hindi"]
    assert series["subtitle_streams"][0]["metadata"]["title"] == "English"

    await processor.process_all({}, {}, {}, "/downloads/No Year.mkv")
    assert processor.vars["year"] == ""
