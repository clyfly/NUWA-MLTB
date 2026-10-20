from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from os import replace, walk
from os.path import basename, join, splitext

from aiofiles.os import path as aiopath, remove

from .. import (
    LOGGER,
    cores,
    cpu_eater_lock,
    task_dict,
    task_dict_lock,
    threads,
)
from ..helper.ext_utils.bot_utils import sync_to_async
from ..helper.ext_utils.files_utils import get_path_size
from ..helper.ext_utils.media_utils import (
    FFMpeg,
    get_document_type,
    get_media_info,
    get_streams,
)
from ..helper.mirror_leech_utils.status_utils.ffmpeg_status import FFmpegStatus


async def apply_metadata_title(
    listener,
    dl_path,
    gid,
    metadata_dict,
    audio_metadata_dict=None,
    video_metadata_dict=None,
    subtitle_metadata_dict=None,
):
    if not any(
        (
            metadata_dict,
            audio_metadata_dict,
            video_metadata_dict,
            subtitle_metadata_dict,
        )
    ):
        return dl_path

    LOGGER.info(f"Applying metadata: {listener.name}")
    ffmpeg = FFMpeg(listener)
    if await aiopath.isfile(dl_path):
        paths = [dl_path]
    else:
        paths = [
            join(directory, filename)
            for directory, _, filenames in await sync_to_async(
                lambda: list(walk(dl_path, topdown=False))
            )
            for filename in filenames
        ]

    files = []
    for path in paths:
        is_video, is_audio, _ = await get_document_type(path)
        if is_video or is_audio:
            files.append((path, is_video, is_audio))

    if not files:
        LOGGER.info(f"No audio/video files found in {dl_path} to apply metadata.")
        return dl_path

    status = FFmpegStatus(listener, ffmpeg, gid, "Metadata")
    async with task_dict_lock:
        task_dict[listener.mid] = status
    listener.progress = False

    try:
        async with cpu_eater_lock:
            listener.progress = True
            for file_path, _, _ in files:
                if listener.is_cancelled:
                    break

                listener.subname = basename(file_path)
                listener.subsize = await get_path_size(file_path)
                processor = listener.metadata_processor
                try:
                    metadata = await processor.process_all(
                        video_metadata_dict or {},
                        audio_metadata_dict or {},
                        subtitle_metadata_dict or {},
                        file_path,
                    )
                    if metadata_dict:
                        metadata["global"].update(
                            processor.apply_vars(metadata_dict)
                        )
                except Exception as error:
                    LOGGER.error(
                        f"Could not format metadata for {file_path}: {error}"
                    )
                    continue

                streams = processor.streams
                if not streams:
                    LOGGER.error(f"No streams found in {file_path}. Skipping metadata.")
                    continue

                extension = splitext(file_path)[1]
                temp_output = f"{splitext(file_path)[0]}.meta_temp{extension}"
                command = [
                    "taskset",
                    "-c",
                    str(cores),
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    file_path,
                ]
                stream_options = []
                video_index = audio_index = subtitle_index = 0

                for stream in streams:
                    stream_index = stream.get("index", 0)
                    stream_type = stream.get("codec_type")
                    command.extend(["-map", f"0:{stream_index}"])
                    if stream_type == "video":
                        command.extend([f"-c:v:{video_index}", "copy"])
                        if language := stream.get("tags", {}).get("language"):
                            stream_options.extend(
                                [
                                    f"-metadata:s:v:{video_index}",
                                    f"language={language}",
                                ]
                            )
                        for key, value in metadata["video"].items():
                            stream_options.extend(
                                [
                                    f"-metadata:s:v:{video_index}",
                                    f"{key}={value}",
                                ]
                            )
                        video_index += 1
                    elif stream_type == "audio":
                        command.extend([f"-c:a:{audio_index}", "copy"])
                        if language := stream.get("tags", {}).get("language"):
                            stream_options.extend(
                                [
                                    f"-metadata:s:a:{audio_index}",
                                    f"language={language}",
                                ]
                            )
                        audio_metadata = next(
                            (
                                item["metadata"]
                                for item in metadata["audio_streams"]
                                if item["index"] == stream_index
                            ),
                            {},
                        )
                        for key, value in audio_metadata.items():
                            stream_options.extend(
                                [
                                    f"-metadata:s:a:{audio_index}",
                                    f"{key}={value}",
                                ]
                            )
                        audio_index += 1
                    elif stream_type == "subtitle":
                        command.extend([f"-c:s:{subtitle_index}", "copy"])
                        if language := stream.get("tags", {}).get("language"):
                            stream_options.extend(
                                [
                                    f"-metadata:s:s:{subtitle_index}",
                                    f"language={language}",
                                ]
                            )
                        subtitle_metadata = next(
                            (
                                item["metadata"]
                                for item in metadata["subtitle_streams"]
                                if item["index"] == stream_index
                            ),
                            {},
                        )
                        for key, value in subtitle_metadata.items():
                            stream_options.extend(
                                [
                                    f"-metadata:s:s:{subtitle_index}",
                                    f"{key}={value}",
                                ]
                            )
                        subtitle_index += 1
                    else:
                        command.extend([f"-c:{stream_index}", "copy"])

                command.extend(["-map_metadata", "-1", *stream_options])
                for key, value in metadata["global"].items():
                    command.extend(["-metadata", f"{key}={value}"])
                command.extend(
                    [
                        "-threads",
                        str(threads),
                        "-progress",
                        "pipe:1",
                        "-y",
                        temp_output,
                    ]
                )

                ffmpeg.clear()
                media_info = await get_media_info(file_path)
                if media_info:
                    ffmpeg._total_time = media_info[0]

                try:
                    listener.subproc = await create_subprocess_exec(
                        *command,
                        stdout=PIPE,
                        stderr=PIPE,
                    )
                    await ffmpeg._ffmpeg_progress()
                    _, stderr = await listener.subproc.communicate()
                    return_code = listener.subproc.returncode
                except Exception as error:
                    LOGGER.error(
                        f"FFmpeg could not apply metadata to {file_path}: {error}"
                    )
                    if await aiopath.exists(temp_output):
                        await remove(temp_output)
                    continue

                if listener.is_cancelled:
                    if await aiopath.exists(temp_output):
                        await remove(temp_output)
                    break

                if return_code == 0 and await aiopath.exists(temp_output):
                    await sync_to_async(replace, temp_output, file_path)
                    LOGGER.info(f"Successfully applied metadata to {file_path}")
                else:
                    error_text = stderr.decode(errors="replace").strip() if stderr else ""
                    LOGGER.error(
                        f"Error applying metadata to {file_path}: {error_text}"
                    )
                    if await aiopath.exists(temp_output):
                        await remove(temp_output)
    except Exception as error:
        LOGGER.error(f"Metadata processing failed for {listener.name}: {error}")
    finally:
        listener.progress = True

    return dl_path
