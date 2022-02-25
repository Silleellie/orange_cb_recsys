from abc import ABC, abstractmethod

import numpy as np
import torch


class VectorStrategy(ABC):
    """
    Useful class in order to abstract the strategies that use more layers in order to obtain an only final
    representation of the model
    """
    def __init__(self, last_interesting_layers: int):
        self.last_interesting_layers = last_interesting_layers

    @abstractmethod
    def build_embedding(self, token_embeddings) -> np.ndarray:
        pass


class SumStrategy(VectorStrategy):
    """
    class that extends VectorStrategy and allows me to sum up the last layers
    """
    def __init__(self, last_interesting_layers: int):
        super().__init__(last_interesting_layers)

    def build_embedding(self, token_embeddings: torch.Tensor) -> np.ndarray:
        token_vecs_sum = []
        for token in token_embeddings:
            sum_vec = torch.sum(token[-self.last_interesting_layers:], dim=0)
            token_vecs_sum.append(sum_vec)
        return torch.stack(token_vecs_sum).numpy()


class CatStrategy(VectorStrategy):
    """
    class that extends VectorStrategy and allows me to concatenate the last layers
    """
    def __init__(self, last_interesting_layers: int):
        super().__init__(last_interesting_layers)

    def build_embedding(self, token_embeddings: torch.Tensor) -> np.ndarray:
        token_vecs_cat = []
        for token in token_embeddings:
            cat_vec = token[-1]
            for i in range(-2, -self.last_interesting_layers - 1, -1):
                cat_vec = torch.cat((cat_vec, token[i]), dim=0)
            token_vecs_cat.append(cat_vec)
        return torch.stack(token_vecs_cat).numpy()


