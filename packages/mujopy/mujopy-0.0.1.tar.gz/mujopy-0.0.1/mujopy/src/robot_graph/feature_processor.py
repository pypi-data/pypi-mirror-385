import numpy as np


class FeatureProcessor:
    """
    Class that contains feature-specific processing functions.
    """

    def __init__(self):
        self.dispatch = {
            "identity": self._identity,
            "flatten": self._flatten,
        }

    def process(self, value, method: str):
        fn = self.dispatch.get(method)
        if fn is None:
            raise Exception(f"Unknown processing method '{method}'.")
        return fn(x=value)

    def _identity(self, x):
        if x is None:
            return [0.0]
        return [float(np.asarray(x).item())]

    def _flatten(self, x):
        if x is None:
            return [0.0]
        return list(np.array(x).flatten())
