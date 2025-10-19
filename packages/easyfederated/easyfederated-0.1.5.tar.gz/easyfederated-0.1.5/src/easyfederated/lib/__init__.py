"""
This module enables easyfed
2
"""

from easyfederated.lib.easyfed import Federated
from easyfederated.lib.backends.numpy import FederatedNumpy
from easyfederated.lib.backends.torch import FederatedTorch
from easyfederated.lib.config import Server, Client

__all__ = ["Federated", "FederatedNumpy", "FederatedTorch", Server, Client]


def my_func(a: int) -> None:
    """
    This is my func!
    How good it is
    """
    pass
