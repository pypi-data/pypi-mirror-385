import os
import socket
from dataclasses import dataclass
from typing import Any

from paramiko import (
    SSHClient,
    BadHostKeyException,
    AuthenticationException,
    SSHException,
    SFTPClient,
)
from paramiko.ssh_exception import UnableToAuthenticate, NoValidConnectionsError

from easyfederated.common.errors import SshConnectionError, SshCommandError
from easyfederated.common.machines import RemoteCredentials, Machine


class SFTPConnection:
    def __init__(self, sftp: SFTPClient):
        self._sftp = sftp

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            self._sftp.close()
        except Exception:
            pass

    def mkdir(self, remote_path: str, ignore_existing: bool = True):
        try:
            self._sftp.mkdir(remote_path)
        except Exception:
            if ignore_existing:
                # try to stat it to see if it exists
                try:
                    self._sftp.stat(remote_path)
                except Exception:
                    # it truly failed
                    raise
                # else it exists, so ignore
            else:
                raise

    def _ensure_remote_dir(self, remote_path: str):
        """
        Create all components in remote_path (mkdir -p style).
        """
        parts = remote_path.strip("/").split("/")
        cur = "/" if remote_path.startswith("/") else ""
        for part in parts:
            if not part:
                continue
            if cur == "/":
                cur = "/" + part
            elif cur == "":
                cur = part
            else:
                cur = cur.rstrip("/") + "/" + part
            self.mkdir(cur, ignore_existing=True)

    def put_folder(self, local_folder: str, remote_folder: str):
        local_folder = os.path.normpath(local_folder)
        self._ensure_remote_dir(remote_folder)

        for root, dirs, files in os.walk(local_folder):
            rel = os.path.relpath(root, local_folder)
            # remote path for this root
            if rel == "." or rel == "":
                remote_root = remote_folder
            else:
                # convert local separators to '/'
                rel_posix = rel.replace(os.sep, "/")
                remote_root = remote_folder.rstrip("/") + "/" + rel_posix

            # make subdirectories
            for d in dirs:
                remote_sub = remote_root.rstrip("/") + "/" + d
                self.mkdir(remote_sub, ignore_existing=True)

            # put files
            for f in files:
                local_f = os.path.join(root, f)
                remote_f = remote_root.rstrip("/") + "/" + f
                self._sftp.put(local_f, remote_f)


@dataclass
class SSHConnection:
    credentials: RemoteCredentials
    client: SSHClient | None = None

    def __enter__(self) -> "SSHConnection":
        try:
            self.client = SSHClient()
            self.client.load_system_host_keys()
            self.client.connect(
                hostname=self.credentials.ip, username=self.credentials.user
            )
            return self
        except (
            IOError,
            BadHostKeyException,
            AuthenticationException,
            UnableToAuthenticate,
            socket.error,
            NoValidConnectionsError,
            SSHException,
        ):
            raise SshConnectionError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()
            self.client = None

    @staticmethod
    def from_machine(machine: Machine) -> "SSHConnection":
        return SSHConnection(credentials=machine.credentials)

    def exec_command(self, command: str) -> Any:
        if self.client:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                return (
                    None,
                    "\n".join(stdout.readlines()),
                    "\n".join(stderr.readlines()),
                )
            else:
                raise SshCommandError(
                    f"Command failed with exit status {exit_status}, stdout: {stdout.readlines()}, stderr: {stderr.readlines()}"
                )
        raise SshCommandError("Client is not enabled...")

    def get_sftp(self) -> SFTPConnection:
        if self.client is None:
            raise ValueError("TODO: Change this")
        sftp = self.client.open_sftp()
        return SFTPConnection(sftp)
