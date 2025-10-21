from abc import ABC, abstractmethod
from digitaltwins_on_fhir.core.resource import ImagingStudy, Reference

Observation_Value_Type = ["valueQuantity", "valueCodeableConcept", "valueString", "valueBoolean",
                          "valueInteger", "valueRange", "valueRatio", "valueSampledData", "valueTime",
                          "valueDateTime", "valuePeriod"]


class AbstractSearch(ABC):
    core = None

    def __init__(self, core):
        self.core = core

    @abstractmethod
    def search_resource_async(self, resource_type, identifier):
        pass

    @abstractmethod
    def search_resources_async(self, resource_type, identifier):
        pass

    @abstractmethod
    def search_resource_sync(self, resource_type, identifier):
        pass

    @abstractmethod
    def search_resources_sync(self, resource_type, identifier):
        pass


class Search(AbstractSearch):
    async_client = None

    def __init__(self, core):
        super().__init__(core)
        self.async_client = self.core.async_client
        self.sync_client = self.core.sync_client

    async def search_resource_async(self, resource_type, identifier):
        resources_search_set = self.async_client.resources(resource_type)
        searched_resource = await resources_search_set.search(identifier=identifier).first()
        return searched_resource

    async def search_resources_async(self, resource_type, identifier=None):
        resources_search_set = self.async_client.resources(resource_type)
        if identifier is None:
            resources = await resources_search_set.search().fetch_all()
        else:
            resources = await resources_search_set.search(identifier=identifier).fetch_all()
        return resources

    def search_resource_sync(self, resource_type, identifier):
        resources_search_set = self.sync_client.resources(resource_type)
        searched_resource = resources_search_set.search(identifier=identifier).first()
        return searched_resource

    def search_resources_sync(self, resource_type, identifier=None):
        resources_search_set = self.sync_client.resources(resource_type)
        if identifier is None:
            resources = resources_search_set.search().fetch_all()
        else:
            resources = resources_search_set.search(identifier=identifier).fetch_all()
        return resources

    @staticmethod
    def _get_resource_identifier(resource):
        return resource.get_by_path(['identifier', {'system': 'https://www.auckland.ac.nz/en/abi.html'}, 'value'],
                                    '')

    @staticmethod
    async def _generate_measurement_details(resource, detail):
        global Observation_Value_Type
        if resource['resourceType'] == "Observation":
            detail.update({
                "coding": {
                    "display": resource.get_by_path(["code", "coding", 0, "display"]),
                    "system": resource.get_by_path(["code", "coding", 0, "system"]),
                    "code": resource.get_by_path(["code", "coding", 0, "code"]),
                },
                "value": [resource.get(v) for v in Observation_Value_Type if resource.get(v, None) is not None],
            })

        elif resource['resourceType'] == "ImagingStudy":
            # endpoint = await self.async_client.resources("Endpoint").search(
            #     _id=mr["endpoint"][0]["reference"].split("/")[-1]).first()
            endpoint = await resource.get("endpoint")[0].to_resource()
            detail.update({
                "description": resource.get('description'),
                "url": endpoint.get("address"),
                "numberOfSeries": resource['numberOfSeries']
            })

        elif resource['resourceType'] == "DocumentReference":
            des = resource.get_by_path([
                'content',
                0,
                "attachment",
                "title"
            ], '')
            url = resource.get_by_path([
                'content',
                0,
                "attachment",
                "url"
            ], '')
            detail.update({
                "description": des,
                "url": url
            })

    async def get_dataset_information(self, dataset_identifier):
        infos = {}

        research_study = await self.search_resource_async("ResearchStudy", dataset_identifier)
        if research_study is None:
            return None
        group_search_set = self.async_client.resources("Group")
        group = await group_search_set.search(
            characteristic_value=research_study.to_reference()).first()
        practitioner = await group["managingEntity"].to_resource()

        infos["dataset"] = research_study
        infos["practitioner"] = practitioner
        infos["group"] = group
        infos["patients"] = []

        for p in group["member"]:
            appointment = await self.async_client.resources("Appointment").search(patient=p.get("entity"),
                                                                                  supporting_info=research_study.to_reference()).first()
            encounter = await self.async_client.resources("Encounter").search(patient=p.get("entity"),
                                                                              appointment=appointment.to_reference()).first()
            count_imaging_study = self.sync_client.resources('ImagingStudy').search(
                encounter=encounter.to_reference()).count()
            count_observation = self.sync_client.resources('Observation').search(
                encounter=encounter.to_reference()).count()

            imagings = await self.async_client.resources("ImagingStudy").search(
                encounter=encounter.to_reference()).limit(count_imaging_study).fetch()

            infos["patients"].append({
                "patient": await p.get("entity").to_resource(),
                "appointment": appointment,
                "encounter": encounter,
                "observations": await self.async_client.resources("Observation").search(
                    encounter=encounter.to_reference()).limit(count_observation).fetch(),
                "imagingstudies": imagings
            })

        return infos

    async def get_patient_measurements(self, patient_identifier):
        """
        Get patient all primary measurements
        :param patient_identifier:
        :return:
        """
        res = []
        dataset = []
        patients = await self.search_resources_async(resource_type="Patient", identifier=patient_identifier)
        if len(patients) == 0:
            return res
        target_patient = patients[0]

        research_subjects = await self.async_client.resources("ResearchSubject").search(
            patient=target_patient.to_reference()).fetch_all()
        for r in research_subjects:
            compositions = await self.async_client.resources("Composition").search(type="primary measurements",
                                                                                   subject=r.to_reference()).fetch_all()
            dataset.extend(compositions)

        for c in dataset:
            measurements = c.get_by_path(["section", 0, "entry"])
            duuid = c.get_by_path(['identifier', 'value'], '')
            d = {
                "datasetName": c.get('title'),
                "uuid": duuid,
                "measurements": []
            }
            res.append(d)
            for m in measurements:
                mr = await m.to_resource()
                mr_uid = self._get_resource_identifier(mr)
                detail = {
                    "resourceType": mr['resourceType'],
                    "uuid": mr_uid,
                }
                d["measurements"].append(detail)
                await self._generate_measurement_details(mr, detail)
        return res

    async def get_dataset_patient_by_resource(self, resource_type, identifier):
        """
        Get measurement's dataset and patient by resource
        :param resource_type:
        :param identifier:
        :return:
        """
        resource = await self.async_client.resources(resource_type).search(identifier=identifier).first()
        composition = await self.async_client.resources("Composition").search(
            entry=resource.to_reference().reference).first()
        authors = composition.get("author")
        target_patient = None
        for a in authors:
            temp = await a.to_resource()
            if temp["resourceType"] == "Patient":
                target_patient = temp
                break
        return {
            "resource": resource,
            "dataset": composition,
            "patient": target_patient
        }

    async def get_workflow_details_by_derived_data(self, resource_type, identifier):
        """
        Find which workflow, tool, and primary data was used to generate a specific derived measurement observation
        :param resource_type: string FHIR resource type
        :param identifier: string
        :return:
        """
        res = {}
        data = await self.get_dataset_patient_by_resource(resource_type, identifier)
        resource = data.get("resource")
        target_patient = data.get("patient")
        if target_patient is not None:
            p_uuid = self._get_resource_identifier(target_patient)
            research_subjects = await self.async_client.resources("ResearchSubject").search(
                individual=target_patient.to_reference().reference).fetch_all()
            assays = [await r["study"].to_resource() for r in research_subjects if r.get("study", None) is not None]
            tool_process = []
            flag = False
            for a in assays:
                processes = await self.async_client.resources("Task").search(
                    subject=a.to_reference().reference).fetch_all()
                tool_process.extend(processes)
            for t in tool_process:
                outputs = t.get("output")
                if outputs is not None:
                    for o in outputs:
                        if resource.to_reference().reference == o["valueReference"].reference:
                            flag = True
                            assay = await t["for"].to_resource()
                            workflow = await assay["protocol"][0].to_resource()
                            study = await assay["partOf"][0].to_resource()
                            workflow_tool = await t["focus"].to_resource()
                            res = {
                                "assay": {
                                    "uuid": self._get_resource_identifier(assay),
                                    "name": assay.get('title')
                                },
                                "study": {
                                    "uuid": self._get_resource_identifier(study),
                                    "name": study.get('title')
                                },
                                "patient": p_uuid,
                                "process": {
                                    "uuid": self._get_resource_identifier(t),
                                    "workflow": {
                                        "uuid": self._get_resource_identifier(workflow),
                                        "name": workflow.get('name')
                                    },
                                    "tool": {
                                        "uuid": self._get_resource_identifier(workflow_tool),
                                        "name": workflow_tool.get('name')
                                    }
                                }
                            }
                            break
                    if flag:
                        break

        return res

    async def get_all_inputs_by_derived_data(self, resource_type, identifier):
        """
        We can find all inputs and their dataset uuid for the derived measurement's data
        :param resource_type: string FHIR resource type
        :param identifier: string
        :return:
        """
        res = {"inputs": []}
        data = await self.get_workflow_details_by_derived_data(resource_type, identifier)
        processes = await self.async_client.resources("Task").search(identifier=data["process"]["uuid"]).fetch_all()
        for t in processes:
            temp = t.get("input")
            if temp is not None:
                for i in temp:
                    primary_input = await i["valueReference"].to_resource()
                    primary_input_uuid = self._get_resource_identifier(primary_input)
                    composition = await self.async_client.resources("Composition").search(
                        entry=primary_input.to_reference().reference).first()
                    d_uuid = composition.get_by_path(['identifier', 'value'], '')
                    detail = {
                        "datasetUUID": d_uuid,
                        "inputResourceType": primary_input.get("resourceType", ""),
                        "resourceUUID": primary_input_uuid
                    }
                    res["inputs"].append(detail)
                    await self._generate_measurement_details(primary_input, detail)

        return res

    async def get_all_workflow_tools_by_workflow(self, name: str = "", identifier: str = "") -> dict:
        if not name and not identifier:
            return {}

        search_params = {"name": name} if name else {"identifier": identifier}
        workflow = await self.async_client.resources("PlanDefinition").search(**search_params).first()
        if not workflow:
            return {}

        res = {
            "workflow": {
                "uuid": self._get_resource_identifier(workflow),
                "name": workflow.get("name"),
                "tools": []
            }
        }

        actions = workflow.get("action", [])
        for action in actions:
            canonical = action.get("definitionCanonical")
            if not canonical:
                continue
            try:
                resource_type, resource_id = canonical.split("/")
                workflow_tool = await self.async_client.reference(resource_type, resource_id).to_resource()
                res["workflow"]["tools"].append({
                    "uuid": self._get_resource_identifier(workflow_tool),
                    "name": workflow_tool.get("name"),
                })
            except (ValueError, AttributeError):
                continue

        return res

    async def get_all_inputs_outputs_of_workflow_tool(self, name: str = "", identifier: str = "") -> dict:
        if not name and not identifier:
            return {}

        search_params = {"name": name} if name else {"identifier": identifier}
        workflow_tool = await self.async_client.resources("ActivityDefinition").search(**search_params).first()
        if not workflow_tool:
            return {}

        workflow_tool_canonical = workflow_tool.to_reference().reference
        workflow = await self.async_client.resources("PlanDefinition").search(
            definition=workflow_tool_canonical).first()
        if not workflow:
            return {}

        assays = await self.async_client.resources("ResearchStudy").search(
            protocol=workflow.to_reference().reference).fetch_all()

        res = {
            "workflow": {
                "uuid": self._get_resource_identifier(workflow),
                "name": workflow.get("name"),
            },
            "workflow_tool": {
                "uuid": self._get_resource_identifier(workflow_tool),
                "name": workflow_tool.get("name"),
                "inputs": [],
                "outputs": []
            }
        }

        for assay in assays:
            tasks = await self.async_client.resources("Task").search(
                subject=assay.to_reference(),
                focus=workflow_tool.to_reference()
            ).fetch_all()

            for task in tasks:
                try:
                    patient = await task.get("owner").to_resource()
                    assay_ref = await task.get("for").to_resource()
                    for field in ("input", "output"):
                        io_items = task.get(field, [])
                        for item in io_items:
                            detail = await self._build_io_detail(item, assay_ref, patient)
                            if detail:
                                res["workflow_tool"][f"{field}s"].append(detail)
                except BaseException as e:
                    # logger.warning(f"Error processing task {task['id']}: {e}")
                    continue

        return res

    async def _build_io_detail(self, item, assay, patient) -> dict:
        try:
            ref = item.get("valueReference")
            if not ref:
                return {}
            resource = await ref.to_resource()

            composition = await self.async_client.resources("Composition").search(entry=ref).first()
            dataset_uuid = composition.get_by_path(["identifier", "value"], "") if composition else ""

            detail = {
                "relevant": {
                    "datasetUUID": dataset_uuid,
                    "assay": {
                        "uuid": self._get_resource_identifier(assay),
                        "name": assay.get("title", "")
                    },
                    "patient": self._get_resource_identifier(patient),
                },
                "data": {
                    "inputResourceType": resource.get("resourceType", ""),
                    "resourceUUID": self._get_resource_identifier(resource),
                }
            }

            await self._generate_measurement_details(resource, detail["data"])
            return detail
        except Exception:
            return {}
