import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from nvflare.lighter.ctx import ProvisionContext
from nvflare.lighter.provision import prepare_project, prepare_builders
from nvflare.lighter.provisioner import Provisioner
from nvflare.lighter.utils import load_yaml
from nvflare.lighter.entity import Participant

from easyfederated.common.machines import Machine
from easyfederated.build.nix import Closure
from easyfederated.common.project import EasyFedProject


@dataclass(frozen=True)
class FlareProvision:
    _context: ProvisionContext

    @property
    def participants(self) -> List[str]:
        participants: List[Participant] = (
            self._context.get_project().get_all_participants()
        )
        return [participant.name for participant in participants]

    def patch_with_closure(self, closure: Closure):
        workspace = self._context.get_workspace()
        file_to_patch = Path(
            os.path.join(
                workspace, "prod_00", closure.machine.name, "startup", "sub_start.sh"
            )
        )
        lines = file_to_patch.read_text(encoding="utf-8")
        patched_script = re.sub(
            r"\bpython3\b",
            closure.python_path,
            lines,
        )
        file_to_patch.write_text(patched_script, encoding="utf-8")

    def get_provision_path_for_machine(self, machine: Machine) -> str:
        return Path(os.path.join(self.deployed_files_path, machine.name)).as_posix()

    @property
    def deployed_files_path(self) -> str:
        return self._context.get_result_location()


@dataclass(frozen=True)
class NvidiaFlare:
    flare_project_file: Path
    easyfed_folder: Path
    workspace_name: str = "workspace"

    def __post_init__(self):
        os.makedirs(self.workspace_folder, exist_ok=True)

    @property
    def workspace_folder(self) -> Path:
        return Path(os.path.join(self.easyfed_folder, self.workspace_name))

    def provision(self) -> FlareProvision:
        workspace = self.workspace_folder.resolve().as_posix()
        project = self.flare_project_file.resolve().as_posix()
        # Same implementation as:
        # from nvflare.lighter.provision import provision
        # But we do it manually because we want to get the Context
        project_dict = load_yaml(project)
        project = prepare_project(project_dict, None, None)
        builders = prepare_builders(project_dict)
        provisioner = Provisioner(workspace, builders)
        context = provisioner.provision(project)
        return FlareProvision(_context=context)


def nvidia_flare_from_configuration(configuration: EasyFedProject) -> NvidiaFlare:
    return NvidiaFlare(
        flare_project_file=configuration.config.flare_config,
        easyfed_folder=configuration.config.easyfed_folder,
    )
