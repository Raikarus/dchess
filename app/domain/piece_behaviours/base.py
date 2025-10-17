from abc import ABC, abstractmethod


class Base(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass
