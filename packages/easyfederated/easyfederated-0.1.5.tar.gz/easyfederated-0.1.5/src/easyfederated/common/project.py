from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Tuple

from easyfederated.common.config import Config
from easyfederated.common.machines import Machine
from easyfederated.build.uv import UvProject
from easyfederated.common.state import ProjectState


@dataclass(frozen=True)
class EasyFedProject:
    config: Config

    def __post_init__(self):
        # TODO: Check that we have the same machines as nvflare on our configuration
        pass

    @property
    def machines_with_project(
        self,
    ) -> Generator[Tuple[Machine, UvProject | None], None, None]:
        for machine in self.config.machines:
            machine = machine.to_machine()
            yield machine, self.__get_uv_project_for(machine)

    @property
    def num_machines(self) -> int:
        return len(self.config.machines)

    def __get_uv_project_for(self, machine: Machine) -> UvProject | None:
        for project in self.config.project:
            if project.name == machine.name:
                return UvProject(path=Path(project.folder))
        return None

    @property
    def project_folder(self) -> Path:
        return self.config.easyfed_folder

    @property
    def project_state(self) -> ProjectState:
        return ProjectState.from_path(state_directory=self.project_folder)
