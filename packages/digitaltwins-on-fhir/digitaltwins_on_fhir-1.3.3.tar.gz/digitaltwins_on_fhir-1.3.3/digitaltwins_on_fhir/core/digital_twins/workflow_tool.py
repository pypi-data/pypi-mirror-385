from abc import ABC
from .digital_twins import AbstractDigitalTWINBase
from datetime import datetime, timezone
from digitaltwins_on_fhir.core.utils import transform_value
from fhir_cda import Annotator
from pprint import pprint
from digitaltwins_on_fhir.core.resource import (Identifier, ActivityDefinition, DefinitionParticipant, CodeableConcept,
                                                Code, Coding, Reference)
from .knowledgebase import DIGITALTWIN_ON_FHIR_SYSTEM
from typing import Dict, Any, List


class WorkflowTool(AbstractDigitalTWINBase, ABC):
    def __init__(self, core, operator):
        self.descriptions: Dict[str, Any] = {}
        self.cda_descriptions = None
        super().__init__(core, operator)

    def add_workflow_tool_description(self, descriptions):
        """
        :param descriptions: json format data
        :return:
        """
        if not isinstance(descriptions, (dict, list)):
            raise ValueError("description must be json format data")
        if not isinstance(descriptions.get("workflow_tool"), dict):
            raise ValueError("description must be SPARC Clinic Description Annotator Workflow tool json format data")
        self.cda_descriptions = descriptions
        return self._generate_workflow_tool_via_cda_descriptions()

    def _generate_workflow_tool_via_cda_descriptions(self):
        self.descriptions = {
            "resource": None,
            "reference": None,
        }
        self.descriptions.update(self.cda_descriptions.get("workflow_tool"))
        return self

    def _generate_participants(self):
        participants = []
        if self.descriptions.get("model") and type(self.descriptions.get("model")) == list:
            for model in self.descriptions.get("model"):
                participants.append(
                    DefinitionParticipant(participant_type="device",
                                          role=CodeableConcept(
                                              codings=[
                                                  Coding(
                                                      system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                                      code=Code(value=model),
                                                      display="model")],
                                              text=model)))
        if self.descriptions.get("software") and type(self.descriptions.get("software")) == list:
            for software in self.descriptions.get("software"):
                participants.append(
                    DefinitionParticipant(participant_type="device",
                                          role=CodeableConcept(
                                              codings=[
                                                  Coding(
                                                      system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                                      code=Code(value=software),
                                                      display="software")],
                                              text=software)))

        return participants

    async def generate_resources(self):
        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                value=self.descriptions["uuid"])
        activity_definition = ActivityDefinition(identifier=[identifier],
                                                 status="active",
                                                 version=self.descriptions.get("version"),
                                                 name=self.descriptions.get("name"),
                                                 title=self.descriptions.get("title"),
                                                 description=self.descriptions.get("description"),
                                                 participant=self._generate_participants())
        resource = await self.operator.create(activity_definition).save()
        self.descriptions["resource"] = resource
        self.descriptions["reference"] = Reference(reference=resource.to_reference().reference, display="Workflow tool")
        return self
