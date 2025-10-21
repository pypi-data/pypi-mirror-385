from abc import ABC, abstractmethod
import sys
from pathlib import Path
import json
from .digital_twins import Measurements
from .digital_twins import WorkflowToolProcess
from .digital_twins import Workflow
from .digital_twins import WorkflowTool


class AbstractDigitalTwin(ABC):
    def __init__(self, core, operator):
        self.core = core
        self.operator = operator

    @abstractmethod
    def measurements(self):
        pass

    @abstractmethod
    def workflow(self):
        pass

    @abstractmethod
    def workflow_tool(self):
        pass

    @abstractmethod
    def process(self):
        pass


class DigitalTwin(AbstractDigitalTwin, ABC):
    measurements_class = Measurements
    workflow_class = Workflow
    workflow_tool_class = WorkflowTool
    workflow_tool_process_class = WorkflowToolProcess

    def __init__(self, core, operator):
        super().__init__(core, operator)

    def measurements(self):
        return self.measurements_class(self.core, self.operator)

    def workflow(self):
        return self.workflow_class(self.core, self.operator)

    def workflow_tool(self):
        return self.workflow_tool_class(self.core, self.operator)

    def process(self):
        return self.workflow_tool_process_class(self.core, self.operator)
