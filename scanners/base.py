from abc import ABC, abstractmethod
from typing import List
from models import Resource

class BaseScanner(ABC):
    def __init__(self, session, region: str):
        self.session = session
        self.region = region

    @abstractmethod
    def scan(self) -> List[Resource]:
        pass

    def name(self) -> str:
        return self.__class__.__name__.replace("Scanner", "").lower()