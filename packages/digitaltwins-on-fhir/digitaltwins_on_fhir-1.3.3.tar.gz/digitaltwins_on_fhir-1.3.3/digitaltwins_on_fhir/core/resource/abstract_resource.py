from abc import ABC, abstractmethod
from typing import Optional, List
from .element import Identifier, Meta


class AbstractResource(ABC):
    def __init__(self, meta: Optional[Meta] = None, identifier: Optional[List[Identifier]] = None):
        self._resource_type = None
        self.meta = meta
        self.identifier = identifier

    @property
    def resource_type(self):
        return self._resource_type  # Define a getter method

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def convert(self, fhirpy_resource):
        pass
