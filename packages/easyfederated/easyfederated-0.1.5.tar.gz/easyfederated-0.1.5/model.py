from typing import Any, Dict, Optional

import os
import copy
import numpy as np
from torch import nn, optim, Tensor, no_grad, device, cuda, as_tensor, tensor, max as max_torch, save, cat
from torch.utils.tensorboard import SummaryWriter
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset

from easyfederated.lib.backends.torch import FederatedTorch
from easyfederated.lib.easyfed import Client, Server, Federated


# from easyfederated import Client, Server, Federated, FederatedTorch

@Federated(
    server=Server("server.localhost", save_model_path="/models/test.pl"),
    clients=[Client(name="site1"), Client(name="site2", env_vars={"VAR": "VALUE"})],
    easyfed_config="/home/pablo/projects/phd/easyfed/examples/fake_project/easyfed.yaml",
)
class CIFAR10Federated(FederatedTorch):
    """
    A FederatedTorch implementation for CIFAR-10 local training and validation.
    This replaces NVFlare-based learner code and exposes:
      - get_weights() -> state_dict (CPU tensors)
      - set_weights(new_state_dict)
      - train_step(...) -> updated state_dict (CPU tensors)
      - validate(...) -> dict(metrics)
    """

    # Replace this with the actual network you used (ModerateCNN).
    # For completeness, here's a simple CIFAR-like CNN stub. Replace by your real net.
    class ModerateCNN(nn.Module):
        def __init__(self, num_classes: int = 10):
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(3, 32, 3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, 3, padding=1),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(64 * 8 * 8, 256),
                nn.ReLU(inplace=True),
                nn.Linear(256, num_classes),
            )

        def forward(self, x: Tensor) -> Tensor:
            return self.classifier(self.features(x))

    # Simple FedProx term implementation: mu/2 * ||w - w_global||^2
    def fedprox_term(model: nn.Module, model_global: nn.Module, mu: float) -> Tensor:
        prox_loss = 0.0
        for p, pg in zip(model.parameters(), model_global.parameters()):
            prox_loss = prox_loss + ((p - pg).view(-1).pow(2).sum())
        return (mu / 2.0) * prox_loss

    def __init__(
            self,
            cifar_root: str = "./dataset",
            aggregation_epochs: int = 1,
            lr: float = 1e-2,
            fedprox_mu: float = 0.0,
            central: bool = False,
            batch_size: int = 64,
            num_workers: int = 0,
            tb_log_dir: Optional[str] = None,
            device_def: Optional[device] = None,
    ):
        super().__init__()
        self.cifar_root = cifar_root
        self.aggregation_epochs = aggregation_epochs
        self.lr = lr
        self.fedprox_mu = fedprox_mu
        self.central = central
        self.batch_size = batch_size
        self.num_workers = num_workers

        # bookkeeping
        self.best_acc = 0.0
        self.epoch_global = 0
        self.epoch_of_start_time = 0

        # model / training objects (initialized below)
        self.device = device_def or (device("cuda:0") if cuda.is_available() else device("cpu"))
        self.model = self.ModerateCNN().to(self.device)
        self.optimizer = optim.SGD(self.model.parameters(), lr=self.lr, momentum=0.9)
        self.criterion = nn.CrossEntropyLoss()
        self.param_shapes = [p.data.shape for p in self.model.parameters()]
        self.param_sizes = [p.numel() for p in self.model.parameters()]
        self.total_params = sum(self.param_sizes)

        # optional writer
        if tb_log_dir:
            os.makedirs(tb_log_dir, exist_ok=True)
            self.writer = SummaryWriter(tb_log_dir)
        else:
            self.writer = None

        # transforms
        self.transform_train = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.ToPILImage(),
                transforms.Pad(4, padding_mode="reflect"),
                transforms.RandomCrop(32),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[x / 255.0 for x in [125.3, 123.0, 113.9]],
                    std=[x / 255.0 for x in [63.0, 62.1, 66.7]],
                ),
            ]
        )
        self.transform_valid = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[x / 255.0 for x in [125.3, 123.0, 113.9]],
                    std=[x / 255.0 for x in [63.0, 62.1, 66.7]],
                ),
            ]
        )

        # datasets/loaders (lazy created)
        self.train_dataset = None
        self.valid_dataset = None
        self.train_loader = None
        self.valid_loader = None

        # optional paths to save local models
        self.local_model_file = None
        self.best_local_model_file = None

    def _create_datasets(self, index_file: Optional[str] = None):
        """
        Create train/valid datasets and dataloaders.
        index_file: optional .npy file listing indices for a local partition (if simulating client split).
        """
        # train dataset
        if self.train_dataset is None or self.train_loader is None:
            if index_file:
                if not os.path.exists(index_file):
                    raise FileNotFoundError(f"Index file {index_file} does not exist")
                indices = np.load(index_file).tolist()
            else:
                indices = None  # use whole dataset (central)

            # Use a small wrapper dataset to select indices if provided
            if indices is None:
                self.train_dataset = datasets.CIFAR10(root="/ds/cifar10", train=True, download=False,
                                                      transform=self.transform_train)
            else:
                # load full dataset then subset via indices
                full = datasets.CIFAR10(root="/ds/cifar10", train=True, download=False, transform=self.transform_train)
                self.train_dataset = Subset(full, indices)

            self.train_loader = DataLoader(
                self.train_dataset, batch_size=self.batch_size, shuffle=True, num_workers=self.num_workers
            )

        # val dataset

        if self.valid_dataset is None or self.valid_loader is None:
            self.valid_dataset = datasets.CIFAR10(root="/ds/cifar10", train=False, download=False,
                                                      transform=self.transform_valid)
            self.valid_loader = DataLoader(self.valid_dataset, batch_size=self.batch_size, shuffle=False,
                                           num_workers=self.num_workers)

        # set local model save paths if not set and if easyfed provides working_dir attribute
        if not self.local_model_file:
            work_dir = getattr(self, "working_dir", ".")
            self.local_model_file = os.path.join(work_dir, "local_model.pt")
            self.best_local_model_file = os.path.join(work_dir, "best_local_model.pt")

    def get_weights(self) -> Dict[str, Tensor]:
        """
        Return model state_dict as CPU tensors. This mirrors the earlier behavior of returning numpy arrays,
        but returning CPU tensors is convenient and preserves dtype.
        """
        sd = self.model.state_dict()
        cpu_sd = {k: v.detach().cpu() for k, v in sd.items()}
        return cpu_sd

    def set_weights(self, new_state: Dict[str, Any]) -> None:
        """
        Accepts a dict-like state dict (CPU tensors or numpy arrays) and loads into the model.
        """
        local_sd = self.model.state_dict()
        # convert incoming values to tensors of the right shape / device
        for k in list(local_sd.keys()):
            if k in new_state:
                val = new_state[k]
                # if numpy array -> convert, if tensor but on cpu -> ok
                if isinstance(val, np.ndarray):
                    t = torch.as_tensor(val, device=self.device)
                elif isinstance(val, torch.Tensor):
                    t = val.to(self.device)
                else:
                    # try cast
                    t = torch.tensor(val, device=self.device)
                # reshape if needed
                try:
                    t = t.reshape(local_sd[k].shape)
                except Exception:
                    # if reshape fails, let load_state_dict raise later
                    pass
                local_sd[k] = t
        # load into model
        self.model.load_state_dict(local_sd)

    # -----------------------
    # local train / validate
    # -----------------------
    def _local_train(self, model_global: Optional[nn.Module] = None, val_freq: int = 0):
        """
        Run local training for self.aggregation_epochs. If model_global is provided and fedprox_mu>0,
        include FedProx term.
        """
        for epoch in range(self.aggregation_epochs):
            self.model.train()
            epoch_len = len(self.train_loader)
            self.epoch_global = self.epoch_of_start_time + epoch
            avg_loss = 0.0

            for i, (inputs, labels) in enumerate(self.train_loader):
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)

                if self.fedprox_mu > 0.0 and model_global is not None:
                    prox = self.fedprox_term(self.model, model_global, self.fedprox_mu)
                    loss = loss + prox

                loss.backward()
                self.optimizer.step()
                avg_loss += loss.item()

            # tensorboard logging (optional)
            if self.writer:
                global_step = epoch_len * self.epoch_global
                self.writer.add_scalar("train_loss", avg_loss / max(1, epoch_len), global_step)

            # optional local validation during training
            if val_freq > 0 and (epoch % val_freq == 0):
                acc = self._local_valid(tb_tag="val_acc_during_train")
                if acc > self.best_acc:
                    self.best_acc = acc
                    self._save_model(is_best=True)

    def _local_valid(self, tb_tag: Optional[str] = None) -> float:
        self.model.eval()
        correct = 0
        total = 0
        with no_grad():
            for inputs, labels in self.valid_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                _, pred = max_torch(outputs.data, 1)
                total += inputs.size(0)
                correct += (pred == labels).sum().item()
        metric = correct / float(total) if total > 0 else 0.0
        if tb_tag and self.writer:
            self.writer.add_scalar(tb_tag, metric, self.epoch_global)
        return metric

    def _save_model(self, is_best: bool = False):
        sd = {"model_weights": self.model.state_dict(), "epoch": self.epoch_global}
        if is_best:
            sd["best_acc"] = self.best_acc
            save(sd, self.best_local_model_file)
        else:
            save(sd, self.local_model_file)

    def train_step(self, learning_rate=1.0) -> Dict[
        str, Tensor]:
        """
        Perform one local training phase. If incoming_weights is provided, load them first.
        Returns the updated model weights as CPU tensors (state_dict).
        The easyfed framework may call train_step with server weights.
        """
        # ensure datasets exist
        self._create_datasets(index_file=None)

        # compute epoch_len for metadata if needed
        epoch_len = len(self.train_loader)

        # keep a frozen copy of global model for FedProx (if requested)
        model_global = None
        if self.fedprox_mu > 0.0:
            model_global = copy.deepcopy(self.model)
            for p in model_global.parameters():
                p.requires_grad = False

        # run local train
        self._local_train(model_global=model_global, val_freq=1 if self.central else 0)
        self.epoch_of_start_time += self.aggregation_epochs

        # post train validation
        val_acc = self._local_valid(tb_tag="val_acc_local_model")
        if val_acc > self.best_acc:
            self.best_acc = val_acc
            self._save_model(is_best=True)
        else:
            self._save_model(is_best=False)

        # return updated weights (CPU)
        return self.get_weights()

    def validate(self, incoming_weights: Dict[str, Any], index_file: Optional[str] = None) -> Dict[str, float]:
        """
        Validate a provided model (incoming_weights) on local train and val sets.
        Returns a dict with 'train_accuracy' and 'val_accuracy'.
        """
        self._create_datasets(index_file=index_file)

        # load weights for validation
        self.set_weights(incoming_weights)

        # compute metrics
        train_acc = self._local_valid(tb_tag="train_acc_global_model")
        val_acc = self._local_valid(tb_tag="val_acc_global_model")

        # if new best, save
        if val_acc > self.best_acc:
            self.best_acc = val_acc
            self._save_model(is_best=True)

        return {"train_accuracy": train_acc, "val_accuracy": val_acc}

    # convenience: save full model to a path (e.g., server can pull)
    def save_local_best(self, path: Optional[str] = None):
        path = path or self.best_local_model_file
        if not path:
            raise ValueError("No path configured to save model")
        sd = {"model_weights": self.model.state_dict(), "epoch": self.epoch_global, "best_acc": self.best_acc}
        save(sd, path)
        return path
#
# from typing import Any
#
# from torch import nn, optim, Tensor, tensor, float32, no_grad, sum
#
# from src.lib.backends.torch import FederatedTorch
# from src.lib.easyfed import Client, Server, Federated
#
#
# @Federated(
#     server=Server("server.pablofraile.net", save_model_path="/models/test.pl"),
#     clients=[Client(name="site1"), Client(name="site2", env_vars={"VAR": "VALUE"})],
#     easyfed_config="./test/fake_project/easyfed.yaml",
# )
# class MyModel(FederatedTorch):
#     def __init__(self):
#         super().__init__()
#         init_weights = tensor([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float32)
#         self.weights = nn.Parameter(init_weights)
#
#     def forward(self, x: Any):
#         """
#         Forward pass (optional for this example).
#         If x is provided, multiply by weight matrix; otherwise return weights.
#         """
#         if x is None:
#             return self.weights
#         return x.matmul(self.weights)
#
#     def get_weights(self) -> Tensor:
#         return self.weights.detach().cpu()
#
#     def set_weights(self, new_weights) -> None:
#         with no_grad():
#             self.weights.copy_(new_weights)
#
#     def train_step(self, learning_rate=1.0) -> Tensor:
#         optimizer = optim.Adam(self.parameters(), lr=learning_rate)
#         optimizer.zero_grad()
#         loss = -sum(self.weights)
#         loss.backward()
#         optimizer.step()
#         return self.get_weights()
