from typing import List

from rich import print
from rich.table import Table

from easyfederated.common.config import get_easyfed_config_from_yaml
from easyfederated.common.project import EasyFedProject
from easyfederated.common.state import Running, Clean, MachineRunning, State, Dirty


def print_running_machines(machines: List[MachineRunning], deployed_files_path: str):
    print(f"[green]Based on workspace: [/green] {deployed_files_path}")
    table = Table("Machine Name", "Type", "Files Folder", "IP", "User")
    for machine in machines:
        m = machine.closure.machine
        type = m.connection.type
        ip = m.connection.remote_credentials.ip if m.is_remote else "N/A"
        user = m.connection.remote_credentials.user if m.is_remote else "N/A"
        table.add_row(m.name, type, machine.tmp_dir, ip, user)
    print(table)


def print_from_state(state: State):
    match state:
        case Running(machines, deployed_files_path):
            print_running_machines(machines, deployed_files_path)
        case Clean():
            print("[green]Project is clean![/green]")
        case Dirty():
            print("[orange]Project contains old builds and unnecessary files[/orange]")
        case _:
            print(f"[red]Invalid state... {state}[/red]")


def status(path: str) -> None:
    configuration = get_easyfed_config_from_yaml(path=path)
    easyfed_project = EasyFedProject(config=configuration)
    project_state = easyfed_project.project_state
    print_from_state(state=project_state.state)
