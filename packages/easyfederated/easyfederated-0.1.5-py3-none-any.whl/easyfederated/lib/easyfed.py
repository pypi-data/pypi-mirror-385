import sys
from inspect import getfile
from typing import List

from easyfederated.lib.backends import Backend
from easyfederated.lib.backends.numpy import __execute as execute_numpy
from easyfederated.lib.backends.torch import __execute as execute_torch
from easyfederated.lib.config import JobConfiguration, Server, Client
from easyfederated.lib.job import execute_job_config


def Federated(
    server: Server,
    clients: List[Client],
    easyfed_config: str,
    num_rounds=1,
    backend=Backend.PYTORCH,
):
    """
     Runs a federated learning experiment using the specified backend and configuration.

    This function orchestrates the communication and training rounds between a central
    server and multiple clients according to the provided `easyfed_config` file.
    The backend determines the machine learning framework used (e.g., PyTorch or NumPy).

    Args:
        server (Server): The federated server responsible for aggregating model updates
            and coordinating the training process.
        clients (List[Client]): A list of participating clients, each responsible for
            local model training and update submission.
        easyfed_config (str): Path to the EasyFed configuration file (YAML or JSON)
            that defines the experiment setup, data paths, and hyperparameters.
        num_rounds (int, optional): Number of federated training rounds to execute.
            Defaults to 1.
        backend (Backend, optional): Backend to use for computation. Can be one of the
            supported frameworks in `Backend` (e.g., `Backend.PYTORCH`, `Backend.NUMPY`).
            Defaults to `Backend.PYTORCH`.

    Returns:
        None: This function does not return a value directly, but performs training,
        logging, and potentially saves model artifacts or metrics as side effects.

    Raises:
        ValueError: If the configuration file path is invalid or unreadable.
        RuntimeError: If the backend fails to initialize or training fails mid-process.
        ConnectionError: If communication with clients fails during aggregation rounds.

    Example:
    """

    def decorator(cls):
        # Only run the logic if this module is executed as __main__
        if cls.__module__ == "__main__":
            args = sys.argv
            should_execute = len(args) >= 2 and "EASYFED_EXECUTE" in args[1]

            if should_execute:
                if backend == Backend.PYTORCH:
                    execute_torch(cls())
                elif backend == Backend.NUMPY:
                    execute_numpy(cls())
                else:
                    raise NotImplementedError(f"Unsupported backend {backend}")
            else:
                script_path = getfile(cls)
                job_config = JobConfiguration(
                    server=server,
                    clients=clients,
                    easyfed_config=easyfed_config,
                    to_execute_script_path=script_path,
                    num_rounds=num_rounds,
                    model_cls=cls,
                    type=backend,
                )
                execute_job_config(job_config)
        return cls

    return decorator
