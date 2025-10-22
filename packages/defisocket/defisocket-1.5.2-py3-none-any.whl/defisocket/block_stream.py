from time import time
import pandas as pd
from io import BytesIO
from pprint import pprint
import asyncio
import requests
import os
from typing import Awaitable, Callable, Optional, Tuple
from dotenv import load_dotenv
import websockets
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if logger.hasHandlers(): logger.handlers.clear()
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(handler)
logger.propagate = False

load_dotenv()

BlockCallback = Callable[[str], Awaitable[None]]  # Callback type for WebSocket events

class HistoricalBlockStream:
    def __init__(self, name: str, server_address: str) -> None:
        self.name = name
        self.base_url = f'{server_address}/historical/block'

    @staticmethod
    def last_block(networks: list[str], server_address: str):
        base_url = f'{server_address}/historical/block'
        url = f'{base_url}/last'
        payload = {
            'networks': networks
        }
        res = requests.post(url, json=payload).json()
        if res['status'] == 'error':
            raise Exception(f"Error getting last block: {res['message']}")
        logger.debug(res)
        return res['message']

    async def start_and_wait(
        self,
        block_ranges: dict[str, Tuple[int, int]],
        block_steps: Optional[dict[str, int]] = None,
        sleep_time: int = 5,
        timeout_seconds: int | None = None
    ):
        """
        Starts the historical stream and waits for it to finish.
        """
        _start = time()
        self.start(block_ranges, block_steps)
        await asyncio.sleep(5)  # Give some time for the stream to start

        while True:
            if timeout_seconds and (time() - _start) > timeout_seconds:
                self.remove()
                raise TimeoutError(f"Stream {self.name} timed out after {timeout_seconds} seconds")

            progress = self.get_progress()
            if progress >= 1.0:
                break
            logger.debug(f"Stream {self.name} is running: {progress:.2%} complete")
            await asyncio.sleep(sleep_time)

        logger.debug(f"Stream {self.name} completed")

        return self.list_downloaded_files()

    def start(
        self,
        block_ranges: dict[str, Tuple[int, int]],
        block_steps: Optional[dict[str, int]] = None
    ):
        url = f'{self.base_url}/create'
        payload = {
            'name': self.name,
            'block_ranges': block_ranges,
        }

        if block_steps:
            payload['block_steps'] = block_steps

        res = requests.post(url, json=payload).json()
        logger.debug(res)

        if res['status'] == 'error':
            raise Exception(f"Error creating stream '{self.name}': {res['message']}")
        else:
            return res['message']

    def is_running(self):
        url = f'{self.base_url}/running'
        res = requests.get(url).json()
        if res['status'] == 'error':
            raise Exception(f"Error checking if stream is running: {res['message']}")
        logger.debug(res)
        return self.name in res['message']

    def get_progress(self):
        url = f'{self.base_url}/progress'
        res = requests.post(url, json={'name': self.name}).json()
        if res['status'] == 'error':
            raise Exception(f"Error getting progress: {res['message']}")
        logger.debug(res)
        return res['message']['progress']

    def stop(self):
        url = f'{self.base_url}/stop'
        res = requests.post(url, json={'name': self.name}).json()
        if res['status'] == 'error':
            raise Exception(f"Error stopping stream: {res['message']}")
        return res['message']

    def remove(self):
        url = f'{self.base_url}/remove'
        res = requests.post(url, json={'name': self.name}).json()
        if res['status'] == 'error':
            raise Exception(f"Error removing stream: {res['message']}")
        logger.debug(res)
        return res['message']

    def list_downloaded_files(self):
        url = f'{self.base_url}/list_files'
        res = requests.post(url, json={'name': self.name}).json()
        if res['status'] == 'error':
            raise Exception(f"Error listing downloaded files: {res['message']}")
        logger.debug(res)
        return res['message']


    def download_file(self, network, file_name, dir: str = '.'):
        url = f'{self.base_url}/download'
        res = requests.post(url, json={
            'stream_name': self.name,
            'network': network,
            'file_name': file_name,
        })
        cd = res.headers.get('Content-Disposition')

        filename = 'downloaded_file.csv'
        if cd and 'filename=' in cd:
            filename = cd.split('filename=')[1].strip('"')

        if res.status_code != 200:
            logger.error(f"Error: {res.status_code} - {res.text}")
            return

        filepath = os.path.join(dir, filename)
        logger.debug(f'Saving file as {filepath}')
        with open(filepath, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.debug(f"Download completed. File saved as {filepath}")

        return filepath

    def download_file_as_dataframe(self, network, file_name):
        url = f'{self.base_url}/download'
        res = requests.post(url, json={
            'stream_name': self.name,
            'network': network,
            'file_name': file_name,
        }, stream=True)

        if res.status_code != 200:
            logger.error(f"Error: {res.status_code} - {res.text}")
            return None

        # Extract filename (if available)
        cd = res.headers.get('Content-Disposition')
        filename = 'downloaded_file'
        if cd and 'filename=' in cd:
            filename = cd.split('filename=')[1].strip('"')

        logger.debug(f"Downloading {filename} into memory...")

        # Download to memory buffer
        buffer = BytesIO()
        for chunk in res.iter_content(chunk_size=8192):
            buffer.write(chunk)
        buffer.seek(0)

        # Detect file type (by name or header)
        if filename.endswith('.parquet'):
            df = pd.read_parquet(buffer)
        elif filename.endswith('.csv'):
            df = pd.read_csv(buffer)
        else:
            # Fallback: try parquet, then CSV
            try:
                buffer.seek(0)
                df = pd.read_parquet(buffer)
            except Exception:
                buffer.seek(0)
                df = pd.read_csv(buffer)

        buffer.close()
        logger.debug(f"Download completed. Returning DataFrame with {len(df)} rows.")
        return df

class LiveBlockStream:
    def __init__(self, network: str, server_address: str) -> None:
        self.network = network
        self.base_url = f'{server_address}/live'

    async def listen(
        self,
        callback: BlockCallback,
        timeout: Optional[int] = None
    ):
        """
        Starts listening to the block info on websocket
        """
        ws_url = self.base_url.replace('http', 'ws', 1)
        stream_url = f'{ws_url}/block/ws/{self.network}'
        logger.debug(f"Connecting to WebSocket at {stream_url}")

        async with websockets.connect(stream_url) as websocket:
            try:
                async with asyncio.timeout(timeout):
                    while True:
                        event = await websocket.recv(decode=True)
                        logger.debug(f"Received: {event}")
                        await callback(event)
            except asyncio.TimeoutError:
                logger.debug("Listening timeout reached, closing connection")
                await websocket.close()
