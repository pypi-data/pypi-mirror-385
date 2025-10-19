import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dacite import from_dict

from easyfederated.build.nix import Closure
from easyfederated.common.errors import InvalidStateError


@dataclass(frozen=True)
class MachineRunning:
    closure: Closure
    tmp_dir: str


class State:
    pass


@dataclass
class Clean(State):
    pass


@dataclass
class Dirty(State):
    pass


@dataclass
class Running(State):
    machines: List[MachineRunning]
    deployed_files_path: str


@dataclass
class StateFile:
    directory: Path
    STATE_MAP = {"clean": Clean, "running": Running, "dirty": Dirty}

    @property
    def state_file_path(self) -> str:
        return f"{self.directory.resolve().as_posix()}/state.json"

    @property
    def exists(self) -> bool:
        return Path(self.state_file_path).exists()

    def __get_key(self, state: State):
        for k, v in self.STATE_MAP.items():
            if isinstance(state, v):
                return k
        raise NotImplementedError(f"No key for state {state} found")

    def write_state(self, state: State):
        key = self.__get_key(state)
        result = {
            "type": key,
            "data": dataclasses.asdict(state),
        }
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    @property
    def state(self) -> State:
        if not self.exists:
            return Clean()
        with open(self.state_file_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
            type = data.get("type")
            state_data = data.get("data")
            return from_dict(data_class=self.STATE_MAP[type], data=state_data)


@dataclass(frozen=True)
class ProjectState:
    file: StateFile

    @property
    def is_running(self) -> bool:
        match self.state:
            case Running(_):
                return True
            case _:
                return False

    @property
    def state(self) -> State:
        return self.file.state

    def update_state(self, state: State):
        match self.state, state:
            case Running(_), Running(_):
                raise InvalidStateError()
        self.file.write_state(state)

    @staticmethod
    def from_path(state_directory: Path):
        return ProjectState(file=StateFile(directory=state_directory))
