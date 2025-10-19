import os
from abc import ABC
from typing import Any

from nvflare import FedJob
from nvflare.app_common.np.np_model_persistor import NPModelPersistor
from nvflare.app_common.workflows.fedavg import FedAvg
from nvflare.client.config import ExchangeFormat
from nvflare.job_config.script_runner import ScriptRunner, FrameworkType

from easyfederated.lib.config import JobConfiguration
from easyfederated.lib.constants import ENV_RUN_JOB_STAGE


class FederatedNumpy(ABC):
    def forward(self, x: Any):
        raise NotImplementedError()

    def get_weights(self) -> Any:
        raise NotImplementedError()

    def set_weights(self, new_weights: Any) -> None:
        raise NotImplementedError()

    def train_step(self, learning_rate=1.0) -> Any:
        raise NotImplementedError()


def __create_numpy_job(config: JobConfiguration, output_path: str):
    name = "fed_numpy"
    job = FedJob(name=name, min_clients=config.num_clients)

    # TODO: Change
    persistor = NPModelPersistor(model_dir="/models", model_name="server.npy")
    persistor_id = job.to_server(persistor, config.server.name)

    # Controller workflow
    controller = FedAvg(
        num_clients=config.num_clients,
        num_rounds=config.num_rounds,
        persistor_id=persistor_id,
    )
    job.to_server(controller, config.server.name)

    # Define script runner for clients
    train_script = config.to_execute_script_path
    # TODO: Add environment flag for running
    script_runner = ScriptRunner(
        script=train_script,
        script_args=f"{ENV_RUN_JOB_STAGE}",
        launch_external_process=False,
        framework=FrameworkType.NUMPY,
        server_expected_format=ExchangeFormat.NUMPY,
        params_transfer_type="FULL",
    )

    # Assign to clients
    for client in config.clients:
        client_name = client.name
        job.to(script_runner, client_name, tasks=["train"])

    # Export job folder
    job.export_job(job_root=output_path)
    return os.path.join(output_path, name)


def __execute(model: FederatedNumpy):
    pass
