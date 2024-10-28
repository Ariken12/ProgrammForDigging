from Core.Components.Compute.Constants import EPSILON
from Core.Components.Compute.BaseComputeYear import BaseComputeYear


class CustomCompute(BaseComputeYear):
    def __init__(self, parent) -> None:
        self.parent = parent
        self.core = self.parent.core

    def __call__(self):
        pass