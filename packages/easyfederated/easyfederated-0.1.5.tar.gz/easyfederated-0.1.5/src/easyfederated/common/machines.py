from dataclasses import dataclass
from decimal import InvalidOperation
from typing import Literal

from easyfederated.common.errors import NotAValidConnectionType


@dataclass(frozen=True)
class RemoteCredentials:
    user: str
    ip: str
    password: str | None = None
    port: int = 22


@dataclass(frozen=True)
class Connection:
    type: Literal["remote", "local"]
    remote_credentials: RemoteCredentials | None = None

    def __post_init__(self):
        if self.type not in ["remote", "local"]:
            raise NotAValidConnectionType()


@dataclass(frozen=True)
class Machine:
    name: str
    connection: Connection

    @property
    def is_remote(self):
        return self.connection.type == "remote"

    @property
    def is_local(self):
        return self.connection.type == "local"

    @property
    def credentials(self) -> RemoteCredentials:
        if self.is_local:
            raise InvalidOperation("A local machine can't have credentials.")
        return self.connection.remote_credentials
