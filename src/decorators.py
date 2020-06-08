from types import FunctionType
from src.optimizer import Optimizer

# TODO: fix


def optimize(func: FunctionType) -> FunctionType:
    def wrapper(*args, **kwargs):
        optimizer = Optimizer(func)\
            .optimize()
        func(args, kwargs)
    return wrapper
