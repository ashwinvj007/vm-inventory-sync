from abc import ABC, abstractmethod
from models import VM

class Collector(ABC):
    name: str = ""

    @abstractmethod
    def collect(self) -> list[VM]:
        """Return VMs from this platform in the common VM model."""