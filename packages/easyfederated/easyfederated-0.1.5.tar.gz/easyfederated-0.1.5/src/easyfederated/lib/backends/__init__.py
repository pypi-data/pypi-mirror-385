from easyfederated.lib.backends.numpy import FederatedNumpy
from easyfederated.lib.backends.torch import FederatedTorch
from easyfederated.lib.config import Backend


def get_backend_from_type(cls):
    if issubclass(cls, FederatedTorch):
        return Backend.PYTORCH
    elif issubclass(cls, FederatedNumpy):
        return Backend.NUMPY
    else:
        raise NotImplementedError(f"EasyFed doesn't support {cls} types")
