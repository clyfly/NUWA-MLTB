import aiohttp
from asyncio import sleep
from logging import getLogger
from os import path as ospath, listdir
from time import time

from .... import bot_loop, Config
from ...ext_utils.bot_utils import async_to_sync, sync_to_async
from ...ext_utils.files_utils import get_mime_type, clean_path
from ...ext_utils.task_manager import is_task_cancelled

LOGGER = getLogger(__name__)
API_URL = "https://api.gofile.io"

class GofileUploader:
    def __init__(self, listener, path, api_token=None):
        self._listener = listener
        self._path = path
        self._last_uploaded = 0
        self._is_cancelled = False
        self._is_errored = False
        self._total_files = 0
        self._total_folders = 0
        self.is_uploading = True
        self.api_token = api_token
        self._server = None
        self.download_url = None

    async def _get_server(self, session):
        try:
            async with session.get(f"{API_URL}/getServer") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["status"] == "ok":
                        self._server = data["data"]["server"]
                        return
            self._server = "store1"
        except Exception as e:
            LOGGER.error(f"Gofile.io: Failed to get best server: {e}")
            self._server = "store1"

    async def _upload_file(self, file_path, file_name, folder_id=None):
        if self._is_cancelled:
            return

        try:
            if not self._server:
                await self._get_server(self._session)

            url = f"https://{self._server}.gofile.io/uploadFile"
            headers = {}
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'

            data = aiohttp.FormData()
            with open(file_path, 'rb') as f:
                data.add_field('file', f, filename=file_name, content_type=get_mime_type(file_path))
                if self.api_token:
                    data.add_field('token', self.api_token)
                if folder_id:
                    data.add_field('folderId', folder_id)

                async with self._session.post(url, data=data, headers=headers) as resp:
                    if resp.status == 200:
                        res_json = await resp.json()
                        if res_json['status'] == 'ok':
                            self.download_url = res_json['data']['downloadPage']
                            return self.download_url
                        else:
                            error = res_json.get('data', {}).get('error', 'Unknown error')
                            raise Exception(f"Failed to upload to Gofile.io: {error}")
                    else:
                        raise Exception(f"Failed to upload to Gofile.io. Status: {resp.status}, Response: {await resp.text()}")
        except Exception as e:
            LOGGER.error(f"Gofile.io upload error: {e}")
            self._is_errored = True
            await self._listener.on_upload_error(str(e))
            return None

    async def _upload_dir(self, input_directory, parent_id=None):
        if self._is_cancelled:
            return

        folder_name = ospath.basename(input_directory)
        folder_id = await self._create_folder(folder_name, parent_id)
        if not folder_id:
            # If folder creation fails (e.g., no token), upload files to the parent directory
            folder_id = parent_id
        else:
            # The public URL for a folder is not directly available.
            # We'll use the URL of the first file uploaded to the folder as a workaround.
            pass

        for item in listdir(input_directory):
            if self._is_cancelled:
                return
            current_path = ospath.join(input_directory, item)
            if ospath.isdir(current_path):
                self._total_folders += 1
                await self._upload_dir(current_path, folder_id)
            else:
                self._total_files += 1
                file_url = await self._upload_file(current_path, item, folder_id)
                if file_url and not self.download_url:
                    self.download_url = file_url # Set the download URL to the first file's URL

        return folder_id

    async def _create_folder(self, folder_name, parent_id=None):
        if not self.api_token:
            return None

        try:
            url = f"{API_URL}/createFolder"
            params = {
                'token': self.api_token,
                'parentFolderId': parent_id or await self._get_root_folder_id(self._session),
                'folderName': folder_name
            }
            async with self._session.put(url, data=params) as resp:
                if resp.status == 200:
                    res_json = await resp.json()
                    if res_json['status'] == 'ok':
                        return res_json['data']['id']
                    else:
                        LOGGER.error(f"Failed to create folder: {res_json.get('data', {}).get('error')}")
                        return None
                else:
                    LOGGER.error(f"Failed to create folder. Status: {resp.status}, Response: {await resp.text()}")
                    return None
        except Exception as e:
            LOGGER.error(f"Gofile.io create folder error: {e}")
            return None

    async def _get_root_folder_id(self, session):
        if not self.api_token:
            return None
        try:
            async with session.get(f"{API_URL}/getAccountDetails?token={self.api_token}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["status"] == "ok":
                        return data["data"]["rootFolder"]
        except Exception as e:
            LOGGER.error(f"Gofile.io: Failed to get root folder ID: {e}")
        return None

    async def upload(self):
        async with aiohttp.ClientSession() as session:
            self._session = session
            bot_loop.create_task(self._status_reporter())

            if ospath.isfile(self._path):
                self._total_files = 1
                await self._upload_file(self._path, self._listener.name)
            else:
                self._total_folders = 1
                await self._upload_dir(self._path)

            if self._is_cancelled:
                return

            if self._is_errored:
                await self._listener.on_upload_error("Upload failed")
                return

            await self._listener.on_upload_complete(self.download_url, self._total_files, self._total_folders, get_mime_type(self._path), self._listener.name)

    async def _status_reporter(self):
        # A simple status reporter. A better implementation would be to estimate the progress.
        while self.is_uploading and not self._is_cancelled:
            await sleep(5)

    def cancel_upload(self):
        self._is_cancelled = True
        self.is_uploading = False
        LOGGER.info(f"Cancelling upload: {self._listener.name}")
        bot_loop.create_task(self._listener.on_upload_error("Upload cancelled by user"))
        bot_loop.create_task(self._session.close())