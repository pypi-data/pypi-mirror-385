import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import yaml

from easyfederated.common.errors import NvidiaFlareProjectFileNotFound
from easyfederated.common.machines import Machine, Connection, RemoteCredentials


@dataclass(frozen=True)
class EasyFedConfig:
    folder: str
    nvidia_flare_project: str


@dataclass(frozen=True)
class MachineConfig:
    name: str
    type: str
    ip: Optional[str] = None
    user: Optional[str] = None

    def to_machine(self) -> Machine:
        remote_credentials = None
        if self.ip or self.user:
            remote_credentials = RemoteCredentials(user=self.user, ip=self.ip)
        return Machine(
            name=self.name,
            connection=Connection(
                type=self.type, remote_credentials=remote_credentials
            ),
        )


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    folder: str


@dataclass(frozen=True)
class Config:
    easyfed: EasyFedConfig
    machines: List[MachineConfig]
    project: List[ProjectConfig]

    def __post_init__(self):
        os.makedirs(self.easyfed.folder, exist_ok=True)
        if not os.path.exists(self.easyfed.nvidia_flare_project):
            raise NvidiaFlareProjectFileNotFound()

    @property
    def easyfed_folder(self) -> Path:
        return Path(self.easyfed.folder)

    @property
    def flare_config(self) -> Path:
        return Path(self.easyfed.nvidia_flare_project)


def get_easyfed_config_from_yaml(path: str) -> Config | None:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    easyfed = EasyFedConfig(**data["easyfed"])
    machines = [
        MachineConfig(name=name, **attrs)
        for name, attrs in data.get("machines", {}).items()
    ]
    project = [
        ProjectConfig(name=name, **attrs)
        for name, attrs in data.get("project", {}).items()
    ]
    return Config(easyfed=easyfed, machines=machines, project=project)
