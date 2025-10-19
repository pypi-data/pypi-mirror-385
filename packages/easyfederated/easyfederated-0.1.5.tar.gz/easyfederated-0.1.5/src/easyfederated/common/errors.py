# Config Related


class NvidiaFlareProjectFileNotFound(Exception):
    pass


class MachineNotFound(Exception):
    pass


class NotAValidConnectionType(Exception):
    pass


# Uv related


class MachineDoesNotHaveAValidUvProject(Exception):
    pass


# Nix Related (Install it, build closure, etc)


class NixBuildClosureError(Exception):
    message: str

    def __init__(self, message: str):
        super().__init__()
        self.message = message


class NixClosureAlreadyUsed(Exception):
    message: str

    def __init__(self, message: str):
        super().__init__()
        self.message = message


class NixInstallationError(Exception):
    message: str


# Ssh Related


class SshConnectionError(Exception):
    pass


class SshCommandError(Exception):
    pass


# State


class ProjectAlreadyRunningError(Exception):
    pass


class InvalidStateError(Exception):
    pass
