from abc import ABC
from .digital_twins import AbstractDigitalTWINBase
from datetime import datetime, timezone
from digitaltwins_on_fhir.core.utils import transform_value
from fhir_cda import Annotator
from pprint import pprint
from digitaltwins_on_fhir.core.resource import (
    Code, Coding, CodeableConcept, ResearchStudy, Identifier,
    Practitioner, Patient, Reference, Endpoint, ImagingStudy, ImagingStudySeries, ImagingStudyInstance, HumanName,
    ResearchSubject, Consent, ConsentScopeCodeableConcept, ConsentCategoryCodeableConcept, Observation,
    ObservationValue, Composition, CompositionAttester, CompositionSection, DocumentReference, Attachment,
    DocumentReferenceContent
)
from .knowledgebase import DIGITALTWIN_ON_FHIR_SYSTEM, LOINC
from typing import Dict, Any, List


class Measurements(AbstractDigitalTWINBase, ABC):
    def __init__(self, core, operator):
        self.primary_measurements: Dict[str, Any] = {}
        self.cda_descriptions = None
        super().__init__(core, operator)

    def analysis_dataset(self, dataset_path):
        annotator = Annotator(dataset_path)
        self.cda_descriptions = annotator.descriptions
        return annotator

    def add_measurements_description(self, descriptions):
        """
        :param descriptions: json format data
        :return:
        """
        if not isinstance(descriptions, (dict, list)):
            raise ValueError("description must be json format data")
        if not isinstance(descriptions.get("dataset"), dict) or not isinstance(descriptions.get("patients"), list):
            raise ValueError("description must be SPARC Clinic Description Annotator Measurements json format data")
        self.cda_descriptions = descriptions
        return self._generate_measurements_via_cda_descriptions()

    def _generate_measurements_via_cda_descriptions(self):
        self.primary_measurements["patients"] = []
        for cda_patient in self.cda_descriptions.get("patients"):
            data = {
                "uuid": cda_patient.get("uuid"),
                "name": cda_patient.get("name", ""),
                "resource": None,
                "reference": "",
                "research_subject": {
                    "uuid": f"{self.cda_descriptions.get('dataset').get('uuid')}_{cda_patient.get('uuid')}_ResearchSubject",
                    "resource": None,
                    "reference": "",
                    "consent": {
                        "uuid": f"{self.cda_descriptions.get('dataset').get('uuid')}_{cda_patient.get('uuid')}_ResearchSubject_Consent",
                        "resource": None,
                        "reference": "",
                    }
                },
                "composition": {
                    "uuid": self.cda_descriptions.get("dataset").get("uuid"),
                    "title": self.cda_descriptions.get("dataset").get("name"),
                    "resource": None,
                    "reference": "",
                    "observations": [],
                    "imagingStudy": [],
                    "documentReference": [],
                }
            }

            for i, ob in enumerate(cda_patient.get("observations")):
                obc = {
                    "uuid": ob.get(
                        "uuid") or f"{self.cda_descriptions.get('dataset').get('uuid')}_{cda_patient.get('uuid')}_Primary_Measurements_Composition_Observation_{i}",
                    "resource": None,
                    "reference": "",
                }
                obc.update(ob)
                data["composition"]["observations"].append(obc)

            for i, imaging in enumerate(cda_patient.get("imagingStudy")):
                image = {
                    "uuid": imaging.get(
                        "uuid") or f"{self.cda_descriptions.get('dataset').get('uuid')}_{cda_patient.get('uuid')}_Primary_Measurements_Composition_ImagingStudy_{i}",
                    "resource": None,
                    "reference": "",
                    "description": imaging.get("description", None),
                    "endpoint": {
                        "uuid": f"{self.cda_descriptions.get('dataset').get('uuid')}_{cda_patient.get('uuid')}_Primary_Measurements_Composition_ImagingStudy_Endpoint_{i}",
                        "url": imaging.get("endpointUrl"),
                        "resource": None,
                        "reference": "",
                    },
                    "series": [
                        {
                            "uid": s.get("uid"),
                            "endpoint": {
                                "uuid": f"{self.cda_descriptions.get('dataset').get('uuid')}_{cda_patient.get('uuid')}_Primary_Measurements_Composition_ImagingStudy_Series_Endpoint_{s.get('uid')}",
                                "url": s.get("endpointUrl"),
                                "resource": None,
                                "reference": "",
                            },
                            "description": s.get("description", ""),
                            "numberOfInstances": s.get("numberOfInstances"),
                            "bodySite": s.get("bodySite"),
                            "instances": s.get("instances"),
                        } for s in imaging.get("series")
                    ]
                }
                data["composition"]["imagingStudy"].append(image)

            for i, doc in enumerate(cda_patient.get("documentReference", [])):
                doc_reference = {
                    "uuid": doc.get(
                        "uuid") or f"{self.cda_descriptions.get('dataset').get('uuid')}_{cda_patient.get('uuid')}_Primary_Measurements_Composition_DocumentReference_{i}",
                    "contentType": doc.get("contentType"),
                    "url": doc.get("url"),
                    "title": doc.get("title", None),
                    "resource": None,
                    "reference": "",
                }
                data["composition"]["documentReference"].append(doc_reference)

            self.primary_measurements["patients"].append(data)

        return self

    async def add_practitioner(self, researcher: Practitioner):
        resource = await self.operator.create(researcher).save()
        if resource is None:
            return
        return self

    async def generate_resources(self):

        # Generate Patient
        await self._generate_patients()

        return self

    async def _generate_patients(self):
        for p in self.primary_measurements["patients"]:
            identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM, value=p["uuid"])
            patient = Patient(active=True, identifier=[identifier],
                              name=[HumanName(use="usual", text=p.get("name"), given=[p.get("name")])])
            resource = await self.operator.create(patient).save()
            p["resource"] = resource
            p["reference"] = Reference(reference=resource.to_reference().reference,
                                       display=resource["name"][0][
                                           "text"] if "name" in resource else "")
            await self._generate_consent(p)
            await self._generate_research_subject(p)

            for image in p["composition"]["imagingStudy"]:
                await self._generate_imaging_study(p, image)

            for ob in p["composition"]["observations"]:
                await self._generate_primary_observation(p, ob)

            for doc in p["composition"]["documentReference"]:
                await self._generate_document_reference(p, doc)
            await self._generate_primary_composition(p)

    async def _generate_consent(self, patient):
        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                value=patient.get("research_subject").get("consent").get("uuid"))
        consent = Consent(identifier=[identifier], status="active", scope=ConsentScopeCodeableConcept.get("research"),
                          category=[ConsentCategoryCodeableConcept.get("research")], patient=patient.get("reference"))
        resource = await self.operator.create(consent).save()
        patient["research_subject"]["consent"]["resource"] = resource
        patient["research_subject"]["consent"]["reference"] = Reference(reference=resource.to_reference().reference,
                                                                        display=f"Consent for patient {patient.get('name')} in dataset {patient.get('composition').get('title')}")

    async def _generate_research_subject(self, patient):
        """
        study -> ResearchStudy reference
        individual -> Patient reference
        :param patient: the patient in self.primary_measurements["patients"]
        :return:
        """
        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM, value=patient.get("research_subject").get("uuid"))
        research_subject = ResearchSubject(identifier=[identifier], status="on-study",
                                           individual=patient.get("reference"),
                                           consent=patient.get("research_subject").get("consent").get("reference"))
        resource = await self.operator.create(research_subject).save()
        patient["research_subject"]["resource"] = resource
        patient["research_subject"]["reference"] = Reference(reference=resource.to_reference().reference,
                                                             display=f"Research Subject for patient {patient.get('name')} in dataset {patient.get('composition').get('title')}")

    async def _generate_primary_observation(self, patient, observation):
        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM, value=observation.get("uuid"))
        value_keys = observation.get("value").keys()
        value_key = list(value_keys)[0]
        ob_value = ObservationValue()
        ob_value.set(key=value_key, value=observation.get("value").get(value_key))
        ob = Observation(identifier=[identifier],
                         status="final",
                         code=CodeableConcept(
                             codings=[
                                 Coding(
                                     system=observation.get("codeSystem"),
                                     code=Code(value=observation.get("code")),
                                     display=observation.get("display"))],
                             text=observation.get("display")),
                         value=ob_value,
                         subject=patient.get("reference"))
        resource = await self.operator.create(ob).save()
        observation["resource"] = resource
        observation["reference"] = Reference(reference=resource.to_reference().reference)

    async def _generate_imaging_study(self, patient, image):
        """
            (0020, 000d) Study Instance UID
            (0020, 000e) Series Instance UID
            (0008, 0018) SOP Instance UID
            (0020, 0013) Instance Number
            (0008,0016) SOP Class UID
            (0008, 0030) Study Time
            (0020,1208) Number of Study Related Instances
            (0020,1206) Number of Study Related Series
            (0020,1209) Number of Series Related Instances
            (0018, 0010) Contrast/Bolus Agent                LO: 'Magnevist'
            (0018, 0015) Body Part Examined                  CS: 'BREAST'
        """
        endpoint = image.get("endpoint")
        endpoint_imagingstudy = self._generate_endpoint(identifier_value=endpoint.get("uuid"),
                                                        url=endpoint.get("url"))

        endpoint_image_resource = await self.operator.create(endpoint_imagingstudy).save()

        endpoint["resource"] = endpoint_image_resource
        endpoint["reference"] = Reference(reference=endpoint_image_resource.to_reference().reference,
                                          display="Imaging Study Endpoint")

        # # Generate imaging series
        result = await self._generate_imaging_study_series(image.get("series"))

        number_of_series = len(image["series"])
        number_of_instances = result["number_of_instances"]

        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM, value=image["uuid"])
        imaging_study = ImagingStudy(identifier=[identifier],
                                     status="available",
                                     started=transform_value(datetime.now(timezone.utc)),
                                     subject=patient.get("reference"),
                                     description=image.get("description", None),
                                     endpoint=[endpoint.get("reference")],
                                     number_of_series=number_of_series,
                                     number_of_instances=number_of_instances,
                                     series=result["series"]
                                     )
        imaging_study_resource = await self.operator.create(imaging_study).save()
        image["resource"] = imaging_study_resource
        image["reference"] = Reference(reference=imaging_study_resource.to_reference().reference)

    async def _generate_imaging_study_series(self, series):
        if series is None:
            return
        series_components = []
        number_of_instances = 0
        for s in series:
            number_of_instances += s.get("numberOfInstances")
            endpoint = s.get("endpoint")
            endpoint_series = self._generate_endpoint(identifier_value=endpoint.get("uuid"),
                                                      url=endpoint.get("url"))
            endpoint_series_resource = await self.operator.create(endpoint_series).save()
            endpoint["resource"] = endpoint_series_resource
            endpoint["reference"] = Reference(reference=endpoint_series_resource.to_reference().reference,
                                              display="Series Endpoint")

            # Generate ImagingStudy series instances
            instances = self._generate_imaging_study_instance(s.get("instances"))

            body_site = None if s.get("bodySite") is None else s.get("bodySite")

            number_of_series_instances = s.get("numberOfInstances")

            series_component = ImagingStudySeries(
                uid=s.get('uid'),
                modality=Coding(
                    system="http://dicom.nema.org/resources/ontology/DCM",
                    code=Code("MR"),
                    display="MRI"
                ),
                description=s.get("description", ""),
                number_of_instances=number_of_series_instances,
                endpoint=[endpoint.get("reference")],
                body_site=Coding(code=Code(body_site["code"]), display=body_site["display"],
                                 system=body_site["system"]) if body_site is not None else None,
                instance=instances
            )
            series_components.append(series_component)
        return {
            "number_of_instances": number_of_instances,
            "series": series_components
        }

    @staticmethod
    def _generate_imaging_study_instance(instances):
        instance_components = []
        for instance in instances:
            instance = ImagingStudyInstance(
                uid=instance.get("uid"),
                sop_class=Coding(code=Code(instance.get("sopClassUid")),
                                 system="http://dicom.nema.org/medical/dicom/current/output/chtml/part04/sect_B.5.html#table_B.5-1",
                                 display=instance.get("sopClassName")),
                number=instance.get("number")
            )
            instance_components.append(instance)
        return instance_components

    @staticmethod
    def _generate_endpoint(identifier_value, url):
        return Endpoint(status="active",
                        identifier=[Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM,
                                               value=identifier_value)],
                        connection_type=Coding(code=Code("dicom-wado-rs"),
                                               system="http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                                               display="DICOM WADO-RS"),
                        name="PACS DICOM Endpoint",
                        address=url,
                        payload_mime_type=[
                            Code(value="application/dicom")
                        ],
                        payload_type=[CodeableConcept(codings=[
                            Coding(code=Code("DICOM WADO-RS"),
                                   system="http://hl7.org/fhir/endpoint-payload-type",
                                   display="DICOM WADO-RS")])])

    async def _generate_document_reference(self, patient, doc):
        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM, value=doc.get("uuid"))
        _type = LOINC.get(doc.get("contentType"), None)
        document_reference = DocumentReference(
            identifier=[identifier],
            status="current",
            doc_status="final",
            document_reference_type=CodeableConcept().set(_type.get("coding"),
                                                          _type.get("text")) if _type is not None else None,
            category=[CodeableConcept().set(codings=[
                {
                    "system": "http://hl7.org/fhir/document-classification",
                    "code": "IMAGING",
                    "display": "Imaging"
                }
            ])],
            subject=patient.get("reference"),
            content=[DocumentReferenceContent(
                Attachment(content_type=doc.get("contentType"), url=doc.get("url"), title=doc.get("title")))]
        )
        resource = await self.operator.create(document_reference).save()
        doc["resource"] = resource
        doc["reference"] = Reference(reference=resource.to_reference().reference)

    async def _generate_primary_composition(self, patient):
        composition = patient.get("composition")
        identifier = Identifier(system=DIGITALTWIN_ON_FHIR_SYSTEM, value=composition.get("uuid"))
        entry = [ob.get("reference") for ob in composition.get("observations")]
        entry.extend([image.get("reference") for image in composition.get("imagingStudy")])
        entry.extend([doc.get("reference") for doc in composition.get("documentReference")])
        c = Composition(
            identifier=[identifier],
            status="final",
            title=composition.get("title"),
            composition_type=CodeableConcept(codings=[
                Coding(system=DIGITALTWIN_ON_FHIR_SYSTEM, code=Code(value="primary measurements"),
                       display="primary measurements")], text="primary measurements"),
            subject=patient.get("research_subject").get("reference"),
            date=transform_value(datetime.now(timezone.utc)),
            author=[patient.get("reference")],
            section=[CompositionSection(
                title="primary measurements",
                entry=entry,
            )]
        )

        resource = await self.operator.create(c).save()
        composition["resource"] = resource
        composition["reference"] = Reference(reference=resource.to_reference().reference)
