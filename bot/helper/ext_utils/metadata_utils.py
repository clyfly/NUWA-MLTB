from os.path import basename, splitext
from re import compile as re_compile

from pycountry import languages

from .media_utils import get_streams


class MetadataProcessor:
    _year_pattern = re_compile(r"\b(?:19|20)\d{2}\b")
    _sanitize_pattern = re_compile(r'[<>:"/\\?*]')

    def __init__(self):
        self.vars = {}
        self.streams = []
        self.audio_streams = []
        self.subtitle_streams = []

    @staticmethod
    def convert_lang_code(lang_code):
        if not lang_code or lang_code.lower() in {"unknown", "und", "none"}:
            return lang_code
        try:
            if len(lang_code) == 2:
                lang = languages.get(alpha_2=lang_code.lower())
            elif len(lang_code) == 3:
                lang = languages.get(alpha_3=lang_code.lower())
            else:
                return lang_code
            return lang.name if lang else lang_code
        except Exception:
            return lang_code

    async def extract_file_vars(self, file_path):
        filename = basename(file_path)
        basename_, extension = splitext(filename)
        self.vars = {
            "filename": filename,
            "basename": basename_,
            "extension": extension.lstrip("."),
            "audiolang": "unknown",
            "sublang": "none",
            "year": "",
        }
        self.streams = await get_streams(file_path) or []
        self.audio_streams = []
        self.subtitle_streams = []

        for stream in self.streams:
            stream_type = stream.get("codec_type", "").lower()
            language = str(stream.get("tags", {}).get("language") or "unknown")
            full_language = self.convert_lang_code(language)
            entry = {
                "index": stream.get("index", 0),
                "language": language,
                "full_language": full_language,
            }
            if stream_type == "audio":
                self.audio_streams.append(entry)
                if self.vars["audiolang"] == "unknown" and language.lower() not in {
                    "und",
                    "unknown",
                    "none",
                }:
                    self.vars["audiolang"] = full_language
            elif stream_type == "subtitle":
                self.subtitle_streams.append(entry)
                if self.vars["sublang"] == "none" and language.lower() not in {
                    "und",
                    "unknown",
                    "none",
                }:
                    self.vars["sublang"] = full_language

        if year_matches := list(self._year_pattern.finditer(basename_)):
            self.vars["year"] = year_matches[-1].group()

    @staticmethod
    def parse_string(metadata_str):
        if not metadata_str or not isinstance(metadata_str, str):
            return {}

        parts = []
        current = []
        index = 0
        while index < len(metadata_str):
            char = metadata_str[index]
            if char == "\\" and index + 1 < len(metadata_str) and metadata_str[index + 1] == "|":
                current.append("|")
                index += 2
                continue
            if char == "|":
                parts.append("".join(current))
                current = []
            else:
                current.append(char)
            index += 1
        parts.append("".join(current))

        result = {}
        for part in parts:
            if not part.strip():
                continue
            if "=" not in part:
                raise ValueError(f"Metadata entry must use key=value: {part}")
            key, value = part.split("=", 1)
            key = key.strip()
            if not key:
                raise ValueError("Metadata keys cannot be empty.")
            result[key] = value.strip()
        return result

    @staticmethod
    def merge_dicts(default_dict, command_dict):
        return {**(default_dict or {}), **(command_dict or {})}

    def sanitize(self, value):
        return self._sanitize_pattern.sub("_", str(value))[:100]

    def apply_vars_to_stream(
        self, metadata_dict, stream_lang=None, full_lang=None, stream_type="audio"
    ):
        if not isinstance(metadata_dict, dict):
            return {}
        stream_vars = self.vars.copy()
        key = "audiolang" if stream_type == "audio" else "sublang"
        if stream_lang and stream_lang.lower() not in {"unknown", "und", "none"}:
            stream_vars[key] = full_lang or self.convert_lang_code(stream_lang)
        else:
            stream_vars[key] = "unknown" if stream_type == "audio" else "none"
        return {
            self.sanitize(key): (
                str(value).format(**stream_vars)
                if isinstance(value, str)
                else str(value)
            )
            for key, value in metadata_dict.items()
        }

    def apply_vars(self, metadata_dict):
        return self.apply_vars_to_stream(metadata_dict)

    def get_audio_metadata(self, audio_metadata_dict):
        return [
            {
                "index": stream["index"],
                "metadata": self.apply_vars_to_stream(
                    audio_metadata_dict,
                    stream["language"],
                    stream["full_language"],
                    "audio",
                ),
            }
            for stream in self.audio_streams
        ]

    def get_subtitle_metadata(self, subtitle_metadata_dict):
        return [
            {
                "index": stream["index"],
                "metadata": self.apply_vars_to_stream(
                    subtitle_metadata_dict,
                    stream["language"],
                    stream["full_language"],
                    "subtitle",
                ),
            }
            for stream in self.subtitle_streams
        ]

    async def process_all(
        self,
        video_metadata_dict,
        audio_metadata_dict,
        subtitle_metadata_dict,
        file_path,
    ):
        await self.extract_file_vars(file_path)
        return {
            "video": self.apply_vars(video_metadata_dict),
            "audio_streams": (
                self.get_audio_metadata(audio_metadata_dict)
                if audio_metadata_dict
                else []
            ),
            "subtitle_streams": (
                self.get_subtitle_metadata(subtitle_metadata_dict)
                if subtitle_metadata_dict
                else []
            ),
            "global": {},
        }

    async def process(self, metadata_dict, file_path):
        await self.extract_file_vars(file_path)
        return self.apply_vars(metadata_dict)
