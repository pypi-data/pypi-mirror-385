import sys

from rich_argparse import ArgumentDefaultsRichHelpFormatter

import confclasses
from ssm_cli.config import CONFIG
from ssm_cli.xdg import get_log_file, get_conf_file
from ssm_cli.commands import COMMANDS, BaseCommand
from ssm_cli.cli_args import CliArgumentParser, ARGS
from ssm_cli.aws import AWSAuthError
from ssm_cli.console import console

# Setup logging
import logging
logging.basicConfig(
    level=logging.WARNING,
    filename=get_log_file(),
    filemode='+wt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def cli(argv: list = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Manually set the log level now, so we get accurate logging during argument parsing
    for i, arg in enumerate(argv):
        if arg == '--log-level':
            logging.getLogger().setLevel(argv[i+1].upper())
        if arg.startswith('--log-level='):
            logging.getLogger().setLevel(arg.split('=')[1].upper())

    logger.debug(f"CLI called with {argv}")

    # Build the actual parser
    parser = CliArgumentParser(
        prog="ssm",
        description="tool to manage AWS SSM",
        formatter_class=ArgumentDefaultsRichHelpFormatter,
    )
    parser.add_global_argument("--profile", type=str, help="Which AWS profile to use")

    for name, command in COMMANDS.items():
        command_parser = parser.add_command_parser(name, command.HELP)
        command.add_arguments(command_parser)

    parser.parse_args(argv)

    logger.debug(f"Arguments: {ARGS}")

    if not ARGS.command:
        parser.print_help()
        return 1
    
    # Setup is a special case, we cannot load config if we dont have any.
    if ARGS.command == "setup":
        run_command()
        return 0
    
    try:
        with open(get_conf_file(), 'r') as file:
            confclasses.load(CONFIG, file)
            ARGS.update_config()
            logger.debug(f"Config: {CONFIG}")
    except EnvironmentError as e:
        console.print(f"[red]Invalid config: {e}[/red]")
        return 1
    
    logging.getLogger().setLevel(CONFIG.log.level.upper())

    
    for logger_name, level in CONFIG.log.loggers.items():
        logger.debug(f"setting logger {logger_name} to {level}")
        logging.getLogger(logger_name).setLevel(level.upper())

    try:
        if ARGS.command not in COMMANDS:
            console.print(f"[red]failed to find action {ARGS.action}[/red]")
            return 3
        COMMANDS[ARGS.command].run()
    except AWSAuthError as e:
        console.print(f"[red]AWS Authentication error: {e}[/red]")
        return 2
    
    return 0

def run_command():
    """
    Run a command, better exceptions and logging
    """
    try:
        COMMANDS[ARGS.command].run()
    except Exception as e:
        logger.error(f"Unhandled exception in {ARGS.command}")
        console.print(f"Unhandled exception, check [link=file://{get_log_file()}]{get_log_file()}[/link] for more information", style="red")
        console.print(f"Error: {e}", style="red bold")
        logger.exception(e, stack_info=True, stacklevel=20)
        return 1
    return 0