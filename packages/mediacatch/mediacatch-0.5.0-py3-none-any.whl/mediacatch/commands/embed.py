from __future__ import annotations

import logging
from argparse import ArgumentParser, _SubParsersAction

from mediacatch.commands import BaseCLICommand
from mediacatch.speech import embed

logger = logging.getLogger('mediacatch.cli.embed')


def embed_speech_cli_factory(args):
    return EmbedSpeechCLI(
        file_paths=args.file_paths,
        speaker_id=args.speaker_id,
        qouta=args.quota,
        url=args.url,
        max_threads=args.max_threads,
        max_request_retries=args.max_request_retries,
        request_delay=args.request_delay,
        chunk_size=args.chunk_size,
    )


class EmbedCLI(BaseCLICommand):
    @staticmethod
    def register_subcommand(parser: _SubParsersAction[ArgumentParser]):
        embed_parser: ArgumentParser = parser.add_parser(
            'embed',
            help='CLI tool to embed files for speech and face recognition with MediaCatch API',
        )

        embed_subcommands_parser = embed_parser.add_subparsers(
            help='mediacatch embed command helpers'
        )

        EmbedSpeechCLI.register_subcommand(embed_subcommands_parser)


class EmbedSpeechCLI(BaseCLICommand):
    @staticmethod
    def register_subcommand(parser: _SubParsersAction[ArgumentParser]):
        embed_speech_parser: ArgumentParser = parser.add_parser(
            'speech',
            help='CLI tool to embed files for speech recognition with MediaCatch Speech API',
        )

        embed_speech_parser.add_argument(
            'file_paths', nargs='+', type=str, help='Path to the files to embed'
        )
        embed_speech_parser.add_argument(
            'speaker_id',
            type=str,
            help='ID of the speaker to embed the files for',
        )
        embed_speech_parser.add_argument(
            '--quota',
            type=str,
            default=None,
            help='Quota for the speech recognition',
        )
        embed_speech_parser.add_argument(
            '--url',
            type=str,
            default='https://api.mediacatch.io/speech',
            help='URL to the MediaCatch Speech API',
        )
        embed_speech_parser.add_argument(
            '--max-threads',
            type=int,
            default=5,
            help='Maximum number of threads to use for uploading and waiting for result',
        )
        embed_speech_parser.add_argument(
            '--max-request-retries',
            type=int,
            default=3,
            help='Maximum number of retries for requests to the API',
        )
        embed_speech_parser.add_argument(
            '--request-delay',
            type=float,
            default=1.0,
            help='Delay between requests to the API',
        )
        embed_speech_parser.add_argument(
            '--chunk-size',
            type=int,
            default=100 * 1024 * 1024,
            help='Chunk size for uploading the file to the API',
        )

        embed_speech_parser.set_defaults(func=embed_speech_cli_factory)

    def __init__(
        self,
        file_paths: str,
        speaker_id: str,
        qouta: str | None = None,
        url: str = 'https://api.mediacatch.io/speech',
        max_threads: int = 5,
        max_request_retries: int = 3,
        request_delay: float = 1.0,
        chunk_size: int = 100 * 1024 * 1024,
    ) -> None:
        self.file_paths = file_paths
        self.speaker_id = speaker_id
        self.qouta = qouta
        self.url = url
        self.max_threads = max_threads
        self.max_request_retries = max_request_retries
        self.request_delay = request_delay
        self.chunk_size = chunk_size

    def run(self) -> None:
        # Upload file to MediaCatch Speech API
        embed(
            self.file_paths,
            speaker_id=self.speaker_id,
            quota=self.qouta,
            max_threads=self.max_threads,
            max_request_retries=self.max_request_retries,
            request_delay=self.request_delay,
            chunk_size=self.chunk_size,
            url=self.url,
        )
