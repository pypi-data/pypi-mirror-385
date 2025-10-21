from typing import TYPE_CHECKING

import click
from primitive.utils.printer import print_result
from primitive.network.ui import render_ports_table

if TYPE_CHECKING:
    from ..client import Primitive


@click.group()
@click.pass_context
def cli(context):
    """Network"""
    pass


@cli.command("switch")
@click.pass_context
def switch(context):
    """Switch"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    switch_info = primitive.network.get_switch_info()
    if context.obj["JSON"]:
        message = switch_info
    else:
        message = f"Vendor: {switch_info.get('vendor')}. Model: {switch_info.get('model')}. IP: {switch_info.get('ip_address')}"
    print_result(message=message, context=context)


@cli.command("ports")
@click.pass_context
def ports(context):
    """Ports"""
    primitive: Primitive = context.obj.get("PRIMITIVE")
    ports_info = primitive.network.get_interfaces_info()
    if context.obj["JSON"]:
        print_result(message=ports_info, context=context)
    else:
        render_ports_table(ports_info.get("interfaces"))
