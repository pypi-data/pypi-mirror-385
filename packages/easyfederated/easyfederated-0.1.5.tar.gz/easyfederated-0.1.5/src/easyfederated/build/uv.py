import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UvProject:
    path: Path

    def __post_init__(self):
        # TODO: Here in init assert that we have a project.yml and a uv.lock file inside the Path
        pass

    @property
    def hash(self) -> str:
        # TODO: Put a hash here
        return str(uuid.uuid4())
