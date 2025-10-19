from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List


class Backend(Enum):
    PYTORCH = "torch"
    NUMPY = "numpy"


@dataclass(frozen=True)
class Client:
    name: str
    env_vars: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Server:
    name: str
    save_model_path: str | None = None


@dataclass(frozen=True)
class JobConfiguration:
    server: Server
    clients: List[Client]
    easyfed_config: str
    to_execute_script_path: str
    num_rounds: int
    model_cls: Any
    type: Backend

    @property
    def num_clients(self) -> int:
        return len(self.clients)
