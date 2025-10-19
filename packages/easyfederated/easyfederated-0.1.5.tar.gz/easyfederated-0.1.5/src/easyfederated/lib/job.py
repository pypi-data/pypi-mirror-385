import dataclasses
import os
import shutil
from dataclasses import dataclass
from tempfile import mkdtemp

from nvflare.fuel.flare_api.flare_api import new_secure_session
from nvflare.tool.job.job_cli import (
    get_app_dirs_from_job_folder,
    prepare_job_config,
    find_admin_user_and_dir,
)
from nvflare.tool.job.job_client_const import DEFAULT_APP_NAME

from easyfederated.common.config import get_easyfed_config_from_yaml
from easyfederated.common.project import EasyFedProject
from easyfederated.common.state import Running
from easyfederated.lib.backends import Backend
from easyfederated.lib.backends.numpy import __create_numpy_job
from easyfederated.lib.backends.torch import __create_torch_job
from easyfederated.lib.config import JobConfiguration


@dataclass(frozen=True)
class Job:
    id: str


def internal_submit_job(admin_user_dir, username, temp_job_dir) -> str:
    # From: https://github.com/NVIDIA/NVFlare/blob/2.6/nvflare/tool/job/job_cli.py#L347
    print("trying to connect to the server")
    sess = new_secure_session(username=username, startup_kit_location=admin_user_dir)
    job_id = sess.submit_job(temp_job_dir)
    print(f"job: '{job_id} was submitted")
    return job_id


@dataclass
class Args:
    job_folder: str
    config_file: str | None = None

    def __iter__(self):
        return iter(dataclasses.asdict(self))


def submit_job(job_folder: str) -> Job:
    # From: https://github.com/NVIDIA/NVFlare/blob/2.6/nvflare/tool/job/job_cli.py#L347
    cmd_args = Args(job_folder=job_folder)
    temp_job_dir = None
    try:
        if not os.path.isdir(cmd_args.job_folder):
            raise ValueError(f"invalid job folder: {cmd_args.job_folder}")

        temp_job_dir = mkdtemp()
        shutil.copytree(cmd_args.job_folder, temp_job_dir, dirs_exist_ok=True)

        app_dirs = get_app_dirs_from_job_folder(cmd_args.job_folder)
        app_names = [os.path.basename(f) for f in app_dirs]
        app_names = app_names if app_names else [DEFAULT_APP_NAME]

        prepare_job_config(cmd_args, app_names, temp_job_dir)
        admin_username, admin_user_dir = find_admin_user_and_dir()

        # TODO: get from nvflare project
        admin_username = "admin@pablofraile.net"

        return Job(internal_submit_job(admin_user_dir, admin_username, temp_job_dir))
    except ValueError as e:
        print(f"\nUnable to submit due to: {e} \n")
    finally:
        if temp_job_dir:
            shutil.rmtree(temp_job_dir)


def create_job(job_config: JobConfiguration, output_path: str) -> str:
    match job_config.type:
        case Backend.PYTORCH:
            return __create_torch_job(job_config, output_path)
        case Backend.NUMPY:
            return __create_numpy_job(job_config, output_path)


def execute_job_config(job_config: JobConfiguration):
    configuration = get_easyfed_config_from_yaml(path=job_config.easyfed_config)
    project = EasyFedProject(config=configuration)
    state = project.project_state
    job_folder = f"{project.project_folder}/jobs"
    match state.state:
        case Running(_, deployed_files_path):
            # TODO: Check that project and job_config are valid (names, etc)
            # This is needed for flare to detect our current deployment
            os.environ["NVFLARE_STARTUP_KIT_DIR"] = deployed_files_path
            created_folder = create_job(job_config, job_folder)
            job = submit_job(created_folder)
            print(f"Started job: {job}")
        case _:
            # TODO: Change for another exception
            raise ValueError("Project should be running..")
