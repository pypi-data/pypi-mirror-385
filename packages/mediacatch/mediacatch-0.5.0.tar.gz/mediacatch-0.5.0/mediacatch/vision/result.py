import json
import logging
import time
from http import HTTPStatus
from typing import Any

import requests

from mediacatch.utils import MediacatchAPIError, MediacatchError, MediacatchTimeoutError

logger = logging.getLogger('mediacatch.vision.result')


def wait_for_result(
    file_id: str,
    url: str = 'https://api.mediacatch.io/vision',
    timeout: int = 3600,
    delay: int = 10,
    verbose: bool = True,
) -> dict[str, Any] | None:
    """Wait for result from a URL.

    Args:
        file_id (str): The file ID to get the result from.
        url (str): The URL to get the result from.
        timeout (int, optional): Timeout for waiting in seconds. Defaults to 3600.
        delay (int, optional): Delay between each request. Defaults to 10.
        verbose (bool, optional): If True, print log messages. Defaults to True.

    Returns:
        dict[str, Any] | None: Dictionary with the result from the URL or None if failed.
    """
    result_url = f'{url}/result/{file_id}'
    if verbose:
        logger.info(f'Waiting for result from {result_url}')

    start_time = time.time()
    end_time = start_time + timeout
    while time.time() < end_time:
        try:
            response = requests.get(result_url)

            if response.status_code in [
                HTTPStatus.NOT_FOUND,
                HTTPStatus.TOO_MANY_REQUESTS,
                HTTPStatus.INTERNAL_SERVER_ERROR,
            ]:
                if response.status_code == HTTPStatus.NOT_FOUND:
                    reason = 'File not found'
                elif response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    reason = 'Too many requests'
                else:
                    reason = 'Internal server error'
                raise MediacatchAPIError(response.status_code, reason)

            if response.status_code in [HTTPStatus.ACCEPTED, HTTPStatus.PROCESSING]:
                if verbose:
                    logger.info(f'Waiting for result from {result_url}')

                time.sleep(delay)
                continue
            elif response.status_code == HTTPStatus.NO_CONTENT:
                if verbose:
                    logger.info(f'No results found for {file_id}')

                return {}
            elif response.status_code == HTTPStatus.GATEWAY_TIMEOUT:
                time.sleep(delay)
                continue

            response.raise_for_status()

            result = response.json()
            elapsed_time = time.time() - start_time
            if verbose:
                logger.info(f'Got result from {result_url} in {elapsed_time:.2f} seconds')

            return result

        except (requests.RequestException, json.JSONDecodeError):
            if verbose:
                logger.error('Error occurred while waiting for JSON response')

        except Exception as e:
            if verbose:
                logger.error(f'Failed to get result from {result_url}: {e}')

            raise MediacatchError(f'Failed to get result from {result_url}: {e}')

        time.sleep(delay)

    if verbose:
        logger.error(f'Timeout waiting for result from {result_url}, give up')

    raise MediacatchTimeoutError(f'Timeout waiting for result from {result_url}')


if __name__ == '__main__':
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
    from pprint import pprint

    parser = ArgumentParser(
        description='Wait for result from a URL',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        'file_id',
        type=str,
        help='The file ID to get the result from',
    )
    parser.add_argument(
        '--url',
        type=str,
        default='https://api.mediacatch.io/vision',
        help='The URL to get the result from',
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=3600,
        help='Timeout for waiting in seconds',
    )
    parser.add_argument(
        '--delay',
        type=int,
        default=10,
        help='Delay between each request',
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show verbose output',
    )
    args = parser.parse_args()

    result = wait_for_result(
        args.file_id, url=args.url, timeout=args.timeout, delay=args.delay, verbose=args.verbose
    )
    pprint(result)
