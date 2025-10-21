from abc import ABC

import fhirpy.lib

from .digital_twins import AbstractDigitalTWINBase
from datetime import datetime, timezone
from digitaltwins_on_fhir.core.utils import transform_value
from fhir_cda import Annotator
from pprint import pprint
from digitaltwins_on_fhir.core.resource import (
    Code, Coding, CodeableConcept, Reference, ContactDetail, Identifier, PlanDefinition, PlanDefinitionGoal,
    PlanDefinitionAction,
    PlanDefinitionActionDefinition, DataRequirement, DataRequirementCodeFilter)
from .knowledgebase import DIGITALTWIN_ON_FHIR_SYSTEM
from typing import Dict, Any, List


class Workflow(AbstractDigitalTWINBase, ABC):
    def __init__(self, core, operator):
        self.descriptions: Dict[str, Any] = {}
        self.cda_descriptions = None
        super().__init__(core, operator)

    def add_workflow_description(self, descriptions):
        """
        :param descriptions: json format data
        :return:
        """
        if not isinstance(descriptions, (dict, list)):
            raise ValueError("description must be json format data")
        if not isinstance(descriptions.get("workflow"), dict):
            raise ValueError("description must be SPARC Clinic Description Annotator Workflow json format data")
        self.cda_descriptions = descriptions
        return self._generate_workflow_via_cda_descriptions()

    def _generate_workflow_via_cda_descriptions(self):
        self.descriptions = {
            "resource": None,
            "reference": None,
        }
        self.descriptions.update(self.cda_descriptions.get("workflow"))
        return self

    async def generate_resources(self):
        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                value=self.descriptions["uuid"])
        goals = [PlanDefinitionGoal(
            description=CodeableConcept(codings=[Coding(display=g.get("description"))], text=g.get("description"))) for
            g in self.descriptions.get("goal") if
            g is not None]

        actions = await self._generate_actions(self.descriptions.get("action"))

        plan_definition = PlanDefinition(identifier=[identifier], status="active",
                                         version=self.descriptions.get("version"),
                                         name=self.descriptions.get("name"),
                                         title=self.descriptions.get("title"),
                                         date=transform_value(datetime.now(timezone.utc)),
                                         description=self.descriptions.get("description"),
                                         purpose=self.descriptions.get("purpose"),
                                         usage=self.descriptions.get("usage"),
                                         author=[ContactDetail(name=self.descriptions.get("author"))],
                                         goal=goals,
                                         action=actions
                                         )
        resource = await self.operator.create(plan_definition).save()
        self.descriptions["resource"] = resource
        self.descriptions["reference"] = Reference(reference=resource.to_reference().reference, display="Workflow")
        return self

    @staticmethod
    def _generate_action_input_output(inputs_outputs) -> list[DataRequirement]:
        temp = []
        for r in inputs_outputs:
            if r.get("resource_type") == "ImagingStudy":
                temp.append(DataRequirement(data_requirement_type=Code("ImagingStudy"),
                                            code_filter=[DataRequirementCodeFilter(code=[
                                                Coding(code=Code(value=r.get("code", None)), system=r.get("system", None),
                                                       display=r.get("display", None))])]
                                            ))
            elif r.get("resource_type") == "DocumentReference":
                temp.append(DataRequirement(data_requirement_type=Code("DocumentReference"),
                                            code_filter=[DataRequirementCodeFilter(code=[
                                                Coding(code=Code(value=r.get("code", None)), system=r.get("system", None),
                                                       display=r.get("display", None))])]
                                            ))
            elif r.get("resource_type") == "Observation":
                temp.append(DataRequirement(data_requirement_type=Code("Observation"),
                                            must_support=[r.get("unit", "")],
                                            code_filter=[DataRequirementCodeFilter(code=[
                                                Coding(code=Code(value=r.get("code", None)), system=r.get("system", None),
                                                       display=r.get("display", None))])]))

        return temp

    async def _generate_actions(self, actions):
        temp = []
        for a in actions:
            if a is not None:
                tool = await self.get_resource("ActivityDefinition", a.get("related_tool_uuid"))
                temp.append(PlanDefinitionAction(
                    title=a.get("title"),
                    description=a.get("description"),
                    definition=PlanDefinitionActionDefinition(
                        definition_canonical=tool.to_reference().reference) if tool is not None else None,
                    input=self._generate_action_input_output(a.get("input")),
                    output=self._generate_action_input_output(a.get("output")),
                ))
        return temp
