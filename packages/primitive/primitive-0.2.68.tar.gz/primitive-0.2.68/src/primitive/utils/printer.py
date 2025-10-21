import json

import click
from loguru import logger


def print_result(message: str | dict, context: click.Context, fg: str = None):
    """Print message to stdout or stderr"""
    if context.obj["DEBUG"]:
        logger.info(json.dumps(message))
    else:
        if context.obj["JSON"]:
            message = json.dumps(message, indent=2)
        click.secho(message, fg=fg)
