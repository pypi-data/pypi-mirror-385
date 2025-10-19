import shutil
import subprocess
import uuid
from typing import List

from tqdm import tqdm

from easyfederated.build.flare import FlareProvision, nvidia_flare_from_configuration
from easyfederated.build.nix import NixMachine, Closure
from easyfederated.build.ssh import SSHConnection
from easyfederated.build.uv import UvProject
from easyfederated.common.config import get_easyfed_config_from_yaml
from easyfederated.common.errors import ProjectAlreadyRunningError
from easyfederated.common.machines import Machine
from easyfederated.common.project import EasyFedProject
from easyfederated.common.state import MachineRunning, Running


def build_closure_for_machine(
    machine: Machine, uv_project: UvProject | None
) -> Closure:
    nix_machine = NixMachine(machine)
    nix_machine.install_nix()
    return nix_machine.build_closure(uv_project)


def build_closures_for_all_machines(project: EasyFedProject) -> List[Closure]:
    builds = []
    with tqdm(
        total=project.num_machines,
        desc="📦 Building environments...",
        bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
    ) as pbar:
        for machine, project in project.machines_with_project:
            builds.append(
                build_closure_for_machine(machine=machine, uv_project=project)
            )
            pbar.set_postfix_str(f"🖥️ {machine.name}")
            pbar.update(1)
    return builds


def patch_provision_with_closures(provision: FlareProvision, closures: List[Closure]):
    with tqdm(
        total=len(closures),
        desc="✂️ Patching provisioned files so they run on the generated easyfed environment...",
        bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
    ) as pbar:
        for closure in closures:
            provision.patch_with_closure(closure)
            pbar.update(1)


def upload_and_run_build(
    provision: FlareProvision, closures: List[Closure]
) -> List[MachineRunning]:
    # TODO: If something fails, then maybe kill the others?
    running_machines = []
    with tqdm(
        total=len(closures),
        desc="🚀 Starting services on all machines...",
        bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
    ) as pbar:
        for closure in closures:
            path = provision.get_provision_path_for_machine(closure.machine)
            identifier = str(uuid.uuid4())
            directory_client = f"/tmp/{identifier}"
            command = f"nohup {directory_client}/startup/start.sh > /dev/null 2>&1 &"
            match closure.machine.is_local:
                case True:
                    shutil.copytree(path, directory_client)
                    subprocess.run(command.split(), check=True)
                case False:
                    with SSHConnection.from_machine(closure.machine) as conn:
                        with conn.get_sftp() as sftp:
                            sftp.put_folder(
                                local_folder=path, remote_folder=directory_client
                            )
                        conn.exec_command(f"chmod -R +x {directory_client}")
                        conn.exec_command(command)
            running_machines.append(
                MachineRunning(closure=closure, tmp_dir=directory_client)
            )
            pbar.update(1)
    return running_machines


def execute(easy_fed_project: EasyFedProject):
    state = easy_fed_project.project_state
    if state.is_running:
        raise ProjectAlreadyRunningError()
    flare = nvidia_flare_from_configuration(easy_fed_project)
    provision = flare.provision()
    closures = build_closures_for_all_machines(project=easy_fed_project)
    patch_provision_with_closures(provision, closures)
    machines_running = upload_and_run_build(provision, closures)
    state.update_state(
        Running(
            machines=machines_running, deployed_files_path=provision.deployed_files_path
        )
    )


def start(path: str) -> None:
    configuration = get_easyfed_config_from_yaml(path=path)
    easyfed_project = EasyFedProject(config=configuration)
    execute(easyfed_project)
