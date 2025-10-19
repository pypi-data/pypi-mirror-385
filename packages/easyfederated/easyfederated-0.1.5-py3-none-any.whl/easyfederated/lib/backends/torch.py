import os
from typing import Any

import nvflare.client as flare
import torch
from nvflare import FedJob
from nvflare.app_common.workflows.fedavg import FedAvg
from nvflare.app_opt.pt import PTFileModelPersistor
from nvflare.client.config import ExchangeFormat
from nvflare.job_config.script_runner import ScriptRunner, FrameworkType
from torch import nn

from easyfederated.lib.config import JobConfiguration
from easyfederated.lib.constants import ENV_RUN_JOB_STAGE


class FederatedTorch(nn.Module):
    def __init__(self):
        super(FederatedTorch, self).__init__()

    def forward(self, x: Any):
        raise NotImplementedError()

    def get_weights(self) -> torch.Tensor:
        raise NotImplementedError()

    def set_weights(self, new_weights: torch.Tensor) -> None:
        raise NotImplementedError()

    def train_step(self, learning_rate=1.0) -> torch.Tensor:
        raise NotImplementedError()


def __create_torch_job(config: JobConfiguration, output_path: str):
    # TODO: Maybe add timestamp to job?
    name = "torch_job"
    job = FedJob(name=name, min_clients=config.num_clients)

    persistor = PTFileModelPersistor(
        model=config.model_cls(), global_model_file_name=config.server.save_model_path
    )
    persistor_id = job.to_server(persistor, config.server.name)

    # Controller workflow
    controller = FedAvg(
        num_clients=config.num_clients,
        num_rounds=config.num_rounds,
        persistor_id=persistor_id,
    )
    job.to_server(controller, config.server.name)  # replace with your server name

    train_script = config.to_execute_script_path
    for client in config.clients:
        # TODO: Build env vars + add the env var for ignoring creation of job
        script_runner = ScriptRunner(
            script=train_script,
            script_args=f"{ENV_RUN_JOB_STAGE}",
            launch_external_process=False,
            framework=FrameworkType.PYTORCH,
            server_expected_format=ExchangeFormat.PYTORCH,
            params_transfer_type="FULL",
        )
        client_name = client.name
        job.to(script_runner, client_name, tasks=["train"])

    job.export_job(job_root=output_path)
    return os.path.join(output_path, name)


def __execute(model: FederatedTorch):
    # Initialize FLARE
    flare.init()
    sys_info = flare.system_info()
    client_name = sys_info["site_name"]
    print(f"Client {client_name} initialized")

    while flare.is_running():
        # Receive model from server
        input_model = flare.receive()
        print(f"Client {client_name}, current_round={input_model.current_round}")
        print(f"Received weights: {input_model.params}")

        # Load the received model weights
        if input_model.params == {}:
            params = model.get_weights()
        else:
            params = input_model.params
        model.set_weights(params)

        # Perform local training
        print(f"Client {client_name} starting training...")
        new_params = model.train_step(learning_rate=1.0)

        print(
            f"Client {client_name} finished training for round {input_model.current_round}"
        )
        print(f"Sending weights: {new_params}")

        output_model = flare.FLModel(
            params=model.cpu().state_dict(),
            params_type="FULL",
            current_round=input_model.current_round,
        )
        flare.send(output_model)
