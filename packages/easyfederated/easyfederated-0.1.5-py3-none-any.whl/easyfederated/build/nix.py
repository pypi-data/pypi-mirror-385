import os
import subprocess
from dataclasses import dataclass
from shutil import which

from easyfederated.build.ssh import SSHConnection
from easyfederated.build.uv import UvProject
from easyfederated.common.errors import NixBuildClosureError, SshCommandError
from easyfederated.common.machines import Machine

NIX_BUILD_UV_PROJECT_TEMPLATE = "github:pablito2020/testing-flakes-template"


@dataclass
class Closure:
    identifier: str
    machine: Machine
    src_uv_project_path: str | None = None

    def __post_init__(self):
        # TODO: Check if identifier is really from nix store
        self.identifier = self.identifier.strip()

    @property
    def python_path(self) -> str:
        return f"{self.identifier}/bin/python3"


def build_pyproject_from_project(project: UvProject | None) -> str:
    command = (
        f"nix build {NIX_BUILD_UV_PROJECT_TEMPLATE} --no-link --print-out-paths"
        if project is None
        else f"nix build {NIX_BUILD_UV_PROJECT_TEMPLATE} --override-input mysrc path:{project.path.resolve()} --no-link --print-out-paths"
    )
    args = command.split()
    try:
        output_path_closure = subprocess.run(args, capture_output=True, check=True)
        return output_path_closure.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr)
        raise NixBuildClosureError(
            message=f"Return Code: {e.returncode}. \n Stdout Message: {e.stdout}. \n Stderr Message: {e.stderr}"
        )


@dataclass(frozen=True)
class NixMachine:
    machine: Machine

    def has_nix_installed(self) -> bool:
        if self.machine.is_local:
            return which("nix") is not None
        with SSHConnection.from_machine(self.machine) as conn:
            try:
                conn.exec_command("nix --version")
                return True
            except SshCommandError:
                return False

    def install_nix(self):
        if self.has_nix_installed():
            return
        install_script = "curl -fsSL https://install.determinate.systems/nix | sh -s -- install --no-confirm"
        match self.machine.is_local:
            case True:
                os.system(install_script)
            case False:
                # TODO: See if we can catch errors?
                with SSHConnection.from_machine(self.machine) as conn:
                    stdin, stdout, stderr = conn.exec_command(install_script)

    def build_closure(self, project: UvProject | None) -> Closure:
        if self.machine.is_local:
            closure_result = build_pyproject_from_project(project)
            return Closure(
                identifier=closure_result,
                machine=self.machine,
                src_uv_project_path=project.path.as_posix() if project else None,
            )
        with SSHConnection.from_machine(self.machine) as conn:
            command = (
                f"nix build {NIX_BUILD_UV_PROJECT_TEMPLATE} --no-link --print-out-paths"
            )
            if project:
                with conn.get_sftp() as sftp:
                    directory_client = f"/tmp/{project.hash}"
                    sftp.put_folder(
                        local_folder=project.path.as_posix(),
                        remote_folder=directory_client,
                    )
                command = f"nix build {NIX_BUILD_UV_PROJECT_TEMPLATE} --override-input mysrc path:{directory_client} --no-link --print-out-paths"
            # TODO: Check for error
            stdin, stdout, stderr = conn.exec_command(command)
            return Closure(
                identifier=stdout,
                src_uv_project_path=directory_client,
                machine=self.machine,
            )
