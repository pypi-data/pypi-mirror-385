import logging
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from mediacatch.utils import MediacatchUploadError, make_request, read_file_in_chunks

logger = logging.getLogger('mediacatch.embed.speech')


def embed(
    fpaths: str | Path | list[str | Path],
    speaker_id: str,
    api_key: str | None = None,
    quota: str | None = None,
    max_threads: int = 5,
    max_request_retries: int = 3,
    request_delay: float = 0.5,
    chunk_size=100 * 1024 * 1024,  # 100 MB
    url: str = 'https://api.mediacatch.io/speech',
    verbose: bool = True,
) -> str:
    """Uploads a file to MediaCatch Speech API.

    Args:
        fpath (str | Path | list[str | Path]): Path or list of paths to the file/files to embed.
        speaker_id (str): ID of the speaker to add the embeddings to.
        api_key (str, optional): API key for the vision API. Defaults to None.
        quota (str | None, optional): The quota to add the embeddings to. Can be None if the user only has one quota. Defaults to None.
        max_threads (int, optional): Number of maximum threads. Defaults to 5.
        max_request_retries (int, optional): Number of maximum retries for request. Defaults to 3.
        request_delay (float, optional): Delay between request retries. Defaults to 0.5.
        chunk_size (_type_, optional): Size of each chunk to upload. Defaults to 100*1024*1024.
        url (str, optional): URL of the MediaCatch Speech API. Defaults to 'https://api.mediacatch.io/speech'.
        verbose (bool, optional): Show verbose output. Defaults to True.

    Returns:
        str: File ID of the uploaded file.
    """
    if not isinstance(fpaths, list):
        fpaths = [fpaths]
    fpaths = [Path(p) for p in fpaths]

    for fpath in fpaths:
        if not fpath.is_file():
            raise MediacatchUploadError(f'File {fpath} does not exist')

    if verbose:
        logger.info(
            f'Uploading files {[fpath.name for fpath in fpaths]} to MediaCatch Speech Embedding API'
        )

    # Create headers with API key
    _api_key = api_key or os.getenv('MEDIACATCH_API_KEY')
    if not _api_key:
        raise MediacatchUploadError('API key is required')

    headers = {
        'Content-type': 'application/json',
        'X-API-KEY': _api_key,
        'X-Quota': str(quota),
    }

    # Initiate file upload
    start_embed_url = f'{url}/embed/'
    data = {
        'file_names': [fpath.name for fpath in fpaths],
        'file_extensions': [fpath.suffix for fpath in fpaths],
        'quota': quota,
        'speaker_id': speaker_id,
    }
    response = make_request(
        'post',
        start_embed_url,
        headers=headers,
        max_retries=max_request_retries,
        delay=request_delay,
        json=data,
    )
    embedding_id = response.json()['embedding_id']

    # Upload file chunks
    upload_file_url = f'{url}/embed/{{embedding_id}}/{{file_number}}/{{part_number}}'
    etags = defaultdict(list)

    def upload_chunk(file_number: int, part_number: int, chunk: bytes) -> None:
        # Get signed URL to upload chunk
        signed_url_response = make_request(
            'get',
            upload_file_url.format(
                embedding_id=embedding_id, file_number=file_number, part_number=part_number
            ),
            headers=headers,
        )
        signed_url = signed_url_response.json()['url']

        # Upload chunk to storage
        reponse = requests.put(signed_url, data=chunk)
        etag = reponse.headers['ETag']
        etags[file_number].append({'e_tag': etag, 'part_number': part_number})

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {}
        for file_number, f in enumerate(fpaths, start=1):
            with f.open('rb') as f:
                for part_number, chunk in enumerate(
                    read_file_in_chunks(file_=f, chunk_size=chunk_size), start=1
                ):
                    futures[executor.submit(upload_chunk, file_number, part_number, chunk)] = (
                        file_number,
                        part_number,
                    )

        for future in as_completed(futures):
            file_number, part_number = futures[future]
            try:
                future.result()
            except Exception as e:
                if verbose:
                    logger.error(
                        f'Chunk {part_number} of file {file_number} failed to upload due to: {e}'
                    )

    # Complete file upload
    complete_upload_url = f'{url}/embed/{embedding_id}/complete'
    response = make_request(
        'post',
        complete_upload_url,
        json={'uploads': [v for _, v in sorted(etags.items())]},
        headers=headers,
    )

    if verbose:
        logger.info(
            f'Files {[fpath.name for fpath in fpaths]} uploaded successfully. Embedding will begin momentarilly'
        )
