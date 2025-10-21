from abc import ABC, abstractmethod
from .base import Create
import sys
from pathlib import Path
import json


class AbstractOperator(ABC):
    core = None

    def __init__(self, core):
        self.core = core

    @abstractmethod
    def create(self, resource):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass


class Operator(AbstractOperator):
    create_class = Create

    def __init__(self, core):
        super().__init__(core)

    def create(self, resource):
        return self.create_class(self, self.core, resource)

    def update(self):
        pass

    def delete(self):
        pass

