from abc import ABC, abstractmethod


class BaseEmbeddingModel(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def encode(self, query):
        pass

    @abstractmethod
    def encode_batch(self, texts: list[str]):
        pass
