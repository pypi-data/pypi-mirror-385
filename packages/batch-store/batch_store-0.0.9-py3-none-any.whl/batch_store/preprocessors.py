import asyncio
import shutil
import tempfile
import traceback
from abc import ABC
from pathlib import Path
from typing import Any, Dict

import httpx
from util_common.io_util import b64str2bytes, bytes2b64str, json2bytes
from util_common.path import (
    duplicate,
    ensure_folder,
    remove_file,
    remove_folder,
    sort_paths,
    split_basename,
)
from util_common.singleton import singleton

from batch_store._log import logger
from batch_store.settings import batch_store_settings


class HTTPXClient(ABC):
    def __init__(self, base_url: str, timeout: int = 600, max_retries: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self._init_client()
        self.client: httpx.AsyncClient | None = None

    def _init_client(self):
        """Initialize the HTTP client."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def close(self):
        """Close the HTTP client."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    def __del__(self):
        """Ensure client is closed when object is garbage collected."""
        if self.client is not None:
            try:
                # Check if there's already a running event loop
                try:
                    loop = asyncio.get_running_loop()
                    # If there's a running loop, we can't use asyncio.run()
                    # Create a task to close the client
                    if not loop.is_closed():
                        loop.create_task(self.client.aclose())
                except RuntimeError:
                    # No running event loop, safe to use asyncio.run()
                    asyncio.run(self.client.aclose())
            except Exception:
                # Ignore any exceptions during cleanup to prevent the warning
                pass

    def get_client(self):
        """Get the client, reinitializing it if necessary."""
        if self.client is None:
            self._init_client()
        return self.client


@singleton
class DecompressClient(HTTPXClient):
    def __init__(self):
        super().__init__(batch_store_settings.decompress_base_url)


@singleton
class UnifyClient(HTTPXClient):
    def __init__(self):
        super().__init__(batch_store_settings.unify_base_url)


async def close_all_clients():
    """Close all singleton HTTP clients."""
    await DecompressClient().close()
    await UnifyClient().close()


def _log_file_size(file_type: str, file: bytes):
    size_mb = len(file) / 1024
    logger.info(f'Writing {file_type}, file size: {size_mb:.2f} KB')


async def save_unified_file(
    save_page_dir: Path,
    unified_page: dict[str, Any],
):
    """Helper method to save unified file and its associated data."""

    ensure_folder(save_page_dir)
    logger.info(f'Writing {save_page_dir.name} ===')

    if unified_page.get('text'):
        save_page_dir.joinpath('pure.txt').write_text(unified_page['text'])
    else:
        save_page_dir.joinpath('pure.txt').write_text('')
    if unified_page.get('html'):
        save_page_dir.joinpath('raw.html').write_text(unified_page['html'])
    else:
        save_page_dir.joinpath('raw.html').write_text(unified_page['text'])

    for file_type, file_key, file_name, ext in [
        ('Excel', 'xlsx', 'raw', 'xlsx'),
        ('PDF', 'pdf', 'raw', 'pdf'),
        ('norm_image', 'norm_image', 'norm', 'png'),
        ('char_block', 'char_block', 'char_block', 'json'),
        ('text_block', 'text_block', 'text_block', 'json'),
        ('table_block', 'table_block', 'table_block', 'json'),
    ]:
        if unified_page.get(file_key):
            if file_key in ['char_block', 'text_block', 'table_block']:
                content = json2bytes(unified_page[file_key])
            else:
                content = b64str2bytes(unified_page[file_key]['file_b64str'])
            _log_file_size(file_type, content)
            save_page_dir.joinpath(f'{file_name}.{ext}').write_bytes(content)


async def request_unify_pages(file_name: str, content: bytes, target_results: list[str]):
    res = await make_request(
        UnifyClient().get_client(),
        "/unify-pages",
        {
            "file_name": file_name,
            "file_b64str": bytes2b64str(content),
            "task_settings": {
                "target_results": target_results,
            },
            "step_settings": [
                {
                    "step_name": "excel",
                    "excel_rows_limit": 500,
                    "excel_rows_limit_exceed_schema": "truncate",
                    "delete_invalid_rows": False,
                },
            ],
        },
    )
    success_pages = res.json()['success_pages']
    failed_files = res.json()['failures']
    return success_pages, failed_files


async def unify_pages_and_save(
    file_path: Path,
    sample_dir: Path,
    failed_dir: Path,
    target_results: list[str],
) -> None:
    try:
        success_pages, failed_files = await request_unify_pages(
            file_path.name, file_path.read_bytes(), target_results
        )

        for unified_page in success_pages:
            stem, ext = split_basename(file_path.name)
            pid = unified_page["page_id"]
            sheet_name = unified_page["sheet_name"]
            if sheet_name:
                save_page_dir = sample_dir / f'{stem}-p{pid}_{sheet_name.replace("-", "_")}.{ext}'
            else:
                save_page_dir = sample_dir / f'{stem}-p{pid}.{ext}'
            await save_unified_file(save_page_dir, unified_page)

        failed_sample_path = failed_dir / file_path.parent.name
        if len(failed_files) == 0:
            if failed_sample_path.is_dir():
                remove_folder(failed_sample_path)
            elif failed_sample_path.is_file():
                remove_file(failed_sample_path)

        for failure in failed_files:
            logger.error(
                'File normalization failed: '
                f'{failure["file_name"]}.{failure["page_id"]}: {failure["error_msg"]}'
            )
            duplicate(file_path.parent, failed_sample_path)

    except Exception:
        logger.error(f"Error in unify_pages: {traceback.format_exc()}")
        duplicate(file_path.parent, failed_sample_path)


async def decompress_sample_and_save(
    sample_path: Path,
    decompressed_dir: Path,
    failed_dir: Path | None = None,
):
    save_dir = decompressed_dir / sample_path.name
    if sample_path.is_dir():
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = Path(tmpdir) / f"{sample_path.name}.zip"
                shutil.make_archive(str(zip_path.with_suffix('')), 'zip', root_dir=sample_path)
                content = zip_path.read_bytes()
        except Exception:
            logger.error(f"Error zipping sample directory {sample_path}: {traceback.format_exc()}")
            if failed_dir:
                duplicate(sample_path, failed_dir / sample_path.name)
            return []
    else:
        content = sample_path.read_bytes()

    try:
        payload = {
            "file_name": sample_path.name,
            "file_b64str": bytes2b64str(content),
        }
        res = await make_request(DecompressClient().get_client(), "/decompress", payload)
        response_data = res.json()
        ensure_folder(save_dir)
        for file in response_data['success_files']:
            file_name = file['file_name']
            (save_dir / file_name).write_bytes(b64str2bytes(file['file_b64str']))
        for file in response_data['failed_files']:
            logger.error('Decompression failed: ' f'{file["file_name"]}. {file["error_msg"]}')
            if failed_dir:
                duplicate(sample_path, failed_dir / sample_path.name)
    except Exception:
        logger.error(f"Error in decompress_sample: {traceback.format_exc()}")
        if failed_dir:
            duplicate(sample_path, failed_dir / sample_path.name)
        return []
    return sort_paths(save_dir.iterdir())


async def make_request(
    client: httpx.AsyncClient | None,
    url: str,
    payload: Dict[str, Any],
    max_retries: int = 3,
) -> httpx.Response:
    """Make an HTTP request with retries and proper error handling."""
    if client is None:
        raise ValueError("Client cannot be None")

    for attempt in range(max_retries):
        try:
            response = await client.post(url=url, json=payload)
            response.raise_for_status()
            logger.info(f'Request {url} success')
            return response
        except httpx.HTTPStatusError as e:
            logger.warning(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}, retrying..."
            )
            if attempt == max_retries - 1:
                raise e
        except httpx.RequestError as e:
            logger.warning(f"Request error occurred: {str(e)}, retrying...")
            if attempt == max_retries - 1:
                raise e
        except Exception as e:
            logger.warning(f"Unexpected error occurred: {traceback.format_exc()}, retrying...")
            if attempt == max_retries - 1:
                raise e
        await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
    raise Exception('Failed to make request')
