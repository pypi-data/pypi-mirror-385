import os
from pathlib import Path
from typing import List

from easyfederated.build.ssh import SSHConnection
from easyfederated.common.config import get_easyfed_config_from_yaml
from easyfederated.common.errors import InvalidStateError
from easyfederated.common.machines import Machine
from easyfederated.common.project import EasyFedProject
from easyfederated.common.state import Running, MachineRunning, Dirty

# The script provisioned by nvflare provision uses this for detecting it has
# to stop the proces... So yeah, it is what it is
SHUTDOWN_FILE = "shutdown.fl"


def stop_machine_remote(machine: Machine, directory: str):
    command = f"touch {directory}/{SHUTDOWN_FILE}"
    with SSHConnection.from_machine(machine) as conn:
        conn.exec_command(command)


def stop_machine_local(directory: str):
    file = Path(os.path.join(directory, SHUTDOWN_FILE))
    if not file.exists():
        file.touch()


def stop_machines(machines: List[MachineRunning]):
    for machine in machines:
        m = machine.closure.machine
        if m.is_remote:
            stop_machine_remote(m, machine.tmp_dir)
        else:
            stop_machine_local(machine.tmp_dir)


def stop(path: str):
    configuration = get_easyfed_config_from_yaml(path=path)
    easyfed_project = EasyFedProject(config=configuration)
    easyfed_state = easyfed_project.project_state
    match easyfed_state.state:
        case Running(machines, _):
            stop_machines(machines)
            easyfed_state.update_state(Dirty())
        case _:
            raise InvalidStateError()
