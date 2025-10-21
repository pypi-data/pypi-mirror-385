from abc import ABC
from .digital_twins import AbstractDigitalTWINBase
from datetime import datetime, timezone
from digitaltwins_on_fhir.core.utils import transform_value
from digitaltwins_on_fhir.core.resource import (Identifier, ObservationValue, Observation, CodeableConcept,
                                                Code, Coding, Reference, Task, TaskInputOutput, Composition,
                                                CompositionSection, DiagnosticReport, ResearchStudy, ResearchSubject,
                                                Consent, Group, GroupMember, ConsentScopeCodeableConcept,
                                                ConsentCategoryCodeableConcept)
from .knowledgebase import DIGITALTWIN_ON_FHIR_SYSTEM
from typing import Dict, Any, List
from .measurements import Measurements
from pprint import pprint


class WorkflowToolProcess(AbstractDigitalTWINBase, ABC):
    def __init__(self, core, operator):
        self.descriptions: Dict[str, Any] = {}
        self.cda_descriptions = None
        self.measurements: Measurements = Measurements(core, operator)
        super().__init__(core, operator)

    async def generate_diagnostic_report(self, report: DiagnosticReport):
        resource = await self.operator.create(report).save()
        return resource

    def add_workflow_tool_process_description(self, descriptions):
        """
        :param descriptions: json format data
        :return:
        """
        if not isinstance(descriptions, (dict, list)):
            raise ValueError("description must be json format data")
        if not isinstance(descriptions.get("process"), dict):
            raise ValueError(
                "description must be SPARC Clinic Description Annotator Workflow tool process json format data")
        self.cda_descriptions = descriptions
        return self._generate_workflow_tool_process_via_cda_descriptions()

    def _generate_workflow_tool_process_via_cda_descriptions(self):
        """
            One assay only have one cohort
        :return:
        """
        process = self.cda_descriptions.get("process")
        self.descriptions = {
            "study": {
                "uuid": process.get("study").get("uuid"),
                "name": process.get("study").get("name"),
                "reference": None,
            },
            "researcher": {
                "uuid": process.get("researcher").get("uuid"),
                "reference": None,
            },
            "assay": {
                "uuid": process.get("assay").get("uuid"),
                "name": process.get("assay").get("name"),
                "reference": None,
            },
            "patients": [{"uuid": p.get("uuid"), "reference": None} for p in process.get("cohort")],
            "workflow": {
                "uuid": process.get("workflow"),
                "reference": None,
            },
            "measurements": {
                "dataset": {
                    "uuid": process.get("dataset").get("uuid"),
                    "name": process.get("dataset").get("name"),
                },
                "patients": [
                    {
                        "uuid": p.get("uuid"),
                        "observations": patient_outputs["observations"],
                        "imagingStudy": patient_outputs["imagingStudy"],
                        "documentReference": patient_outputs["documentReference"],
                    } for p in process.get("cohort") if
                    (patient_outputs := self._get_patient_outputs(p.get("processes"))) is not None
                ]
            },
            "processes": []
        }

        for patient in process.get("cohort"):
            for tool_process in patient.get("processes"):
                temp = {
                    "uuid": tool_process.get("uuid"),
                    "tool_uuid": tool_process.get("tool_uuid"),
                    "patient_uuid": patient.get("uuid"),
                    "date": tool_process.get("date"),
                    "input": tool_process.get("input"),
                    "output": tool_process.get("output"),
                    "output_dataset_uuid": process.get("dataset").get("uuid")
                }
                self.descriptions["processes"].append(temp)
        return self

    @staticmethod
    def _get_patient_outputs(processes):
        res = {
            "observations": [],
            "imagingStudy": [],
            "documentReference": []
        }
        for i, process in enumerate(processes):
            if process.get("output"):
                for j, o in enumerate(process.get("output", [])):
                    if o.get("resource_type") == "ImagingStudy":
                        o.update({
                            "uuid": f"{process.get('uuid')}_{process.get('tool_uuid')}_Workflow-Process-Output-ImagingStudy-{i}-{j}"
                        })
                        res["imagingStudy"].append(o)
                    elif o.get("resource_type") == "Observation":
                        o.update({
                            "uuid": f"{process.get('uuid')}_{process.get('tool_uuid')}_Workflow-Process-Output-Observation-{i}-{j}"
                        })
                        res["observations"].append(o)
                    elif o.get("resource_type") == "DocumentReference":
                        o.update({
                            "uuid": f"{process.get('uuid')}_{process.get('tool_uuid')}_Workflow-Process-Output-DocumentReference-{i}-{j}"
                        })
                        res["documentReference"].append(o)
        return res

    async def generate_resources(self):
        # 1. Create Study resource
        await self._generate_study_resource()
        # 2. Create Assay resource
        await self._generate_assay_resource()
        # 3. Generate Cohort resource
        await self._generate_cohort_resource()
        # 4. Generate Output measurements
        await self._generate_measurement()
        # 5. Generate processes
        for p in self.descriptions["processes"]:
            await self._generate_task(p)
        return self

    async def _generate_study_resource(self):
        researcher_description = self.descriptions.get("researcher")
        researcher = await self.get_resource("Practitioner", researcher_description.get("uuid"))
        researcher_description["reference"] = researcher.to_reference()

        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                value=self.descriptions["study"]["uuid"])
        study = ResearchStudy(
            identifier=[identifier],
            status="completed",
            title=self.descriptions["study"]["name"],
            principal_investigator=Reference(reference=researcher.to_reference().reference,
                                             display=researcher["name"][0]["text"])
        )
        resource = await self.operator.create(study).save()
        self.descriptions.get("study")["reference"] = resource.to_reference()

    async def _generate_assay_resource(self):
        """
        study ResearchStudy resource should be store in assay Resource's partOf attribute
        workflow PlanDefinition resource should be store in assay Resource's protocol attribute
        :return:
        """
        workflow_description = self.descriptions.get("workflow")
        workflow_resource = await self.get_resource("PlanDefinition", workflow_description.get("uuid"))
        workflow_description["reference"] = workflow_resource.to_reference()

        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                value=self.descriptions["assay"]["uuid"])
        assay = ResearchStudy(
            identifier=[identifier],
            status="completed",
            title=self.descriptions["assay"]["name"],
            part_of=[Reference(reference=self.descriptions["study"]["reference"].reference)],
            protocol=[Reference(reference=workflow_description["reference"].reference)],
        )
        assay_resource = await self.operator.create(assay).save()
        self.descriptions.get("assay")["reference"] = assay_resource.to_reference()

    async def _generate_cohort_resource(self):
        patients = self.descriptions.get("patients")
        for patient in patients:
            patient_resource = await self.get_resource("Patient", patient.get("uuid"))
            patient["reference"] = patient_resource.to_reference()
            consent_resource = await self.operator.create(Consent(status="active",
                                                                  identifier=[
                                                                      Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                                                                 value=f"{self.descriptions.get('assay').get('uuid')}-{patient.get('uuid')}-subject-consent")],
                                                                  scope=ConsentScopeCodeableConcept.get("research"),
                                                                  category=[
                                                                      ConsentCategoryCodeableConcept.get("research")],
                                                                  patient=Reference(
                                                                      reference=patient["reference"].reference,
                                                                      display=patient_resource["name"][0]["text"])
                                                                  )).save()

            research_subject_resource = await self.operator.create(ResearchSubject(
                identifier=[Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                       value=f"{self.descriptions.get('assay').get('uuid')}-{patient.get('uuid')}-subject")],
                status="on-study",
                individual=Reference(reference=patient["reference"].reference,
                                     display=patient_resource["name"][0]["text"]),
                consent=Reference(reference=consent_resource.to_reference().reference),
                study=Reference(reference=self.descriptions.get("assay").get("reference").reference),
            )).save()
            patient.update({
                "subject_reference": research_subject_resource.to_reference(),
            })

            # Issue: group member can not store research subject, cannot save in FHIR server!

    async def _generate_measurement(self):
        await self.measurements.add_measurements_description(
            descriptions=self.descriptions.get("measurements")).generate_resources()

    async def _generate_task(self, process):
        """
        FHIR Task Resource:
            owner: patient reference
            for: Assay reference
            focus: workflow tool reference
            basedOn: research subject reference
            requester (Optional): practitioner reference
        """
        tool_resource = await self.get_resource("ActivityDefinition", process.get("tool_uuid"))
        patient = [p for p in self.descriptions.get("patients") if p.get("uuid") == process.get("patient_uuid")][0]
        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                value=process.get("uuid"))
        task_input = []
        task_output = []
        if len(process.get("input")) > 0:
            for i in process.get("input"):
                task_input.append(await self._generate_task_input_output(i))
        if len(process.get("output")) > 0:
            for o in process.get("output"):
                task_output.append(await self._generate_task_input_output(o))
        task = Task(identifier=[identifier], status="accepted", intent="unknown",
                    description=f"Workflow process for {tool_resource.get('name', '')}",
                    authored_on=process.get("date"),
                    last_modified=process.get("date"),
                    based_on=[Reference(reference=patient["subject_reference"].reference)],
                    owner=Reference(reference=patient["reference"].reference),
                    task_for=Reference(reference=self.descriptions.get("assay").get("reference").reference),
                    focus=Reference(reference=tool_resource.to_reference().reference),
                    task_input=task_input,
                    task_output=task_output)

        resource = await self.operator.create(task).save()
        process.update(
            {"reference": Reference(reference=resource.to_reference().reference, display="Workflow Tool Process")})

    async def _generate_task_input_output(self, item):
        resource = await self.get_resource(item.get("resource_type"), item.get("uuid"))
        return TaskInputOutput(
            CodeableConcept(
                codings=[
                    Coding(system="http://hl7.org/fhir/resource-types",
                           code=Code(value=item.get("resource_type")),
                           display=item.get("resource_type"))],
                text=item.get("resource_type")),
            value=Reference(reference=resource.to_reference().reference, display=item.get("resource_type"))
        )
