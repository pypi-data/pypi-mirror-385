from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from mediacatch import __version__
from mediacatch.commands.vision import VisionCLI
from mediacatch.commands.viz import VizCLI
from mediacatch.commands.speech import SpeechCLI
from mediacatch.commands.embed import EmbedCLI


def main():
    parser = ArgumentParser(
        prog='MediaCatch CLI tool',
        usage='mediacatch <command> [<args>]',
        description='MediaCatch CLI tool',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )
    commands_parser = parser.add_subparsers(help='mediacatch command helpers')

    # Register commands
    SpeechCLI.register_subcommand(commands_parser)
    VisionCLI.register_subcommand(commands_parser)
    VizCLI.register_subcommand(commands_parser)
    EmbedCLI.register_subcommand(commands_parser)

    # Let's go
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        exit(1)

    # Run
    service = args.func(args)
    service.run()


if __name__ == '__main__':
    main()
