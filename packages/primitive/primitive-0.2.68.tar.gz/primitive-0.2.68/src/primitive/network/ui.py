from rich.console import Console
from rich.table import Table


def render_ports_table(ports_dict) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold #FFA800")
    table.add_column("Port")
    table.add_column("Status")
    table.add_column("MAC Address")
    table.add_column("IP Address")

    for k, v in ports_dict.items():
        table.add_row(
            k, v.get("link_status"), v.get("mac_address"), v.get("ip_address")
        )

    console.print(table)
