from abc import ABC, abstractmethod

class Pipe(ABC):
    @abstractmethod
    def write(self, message: str):
        pass

    @abstractmethod
    def read(self) -> str:
        pass
