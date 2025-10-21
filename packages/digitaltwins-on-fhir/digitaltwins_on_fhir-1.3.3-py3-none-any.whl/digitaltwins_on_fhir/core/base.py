from pathlib import Path
from abc import ABC, abstractmethod
from .resource import Code, Coding, CodeableConcept


class AbstractOperatorBase(ABC):
    core = None
    operator = None

    def __init__(self, operator, core):
        self.operator = operator
        self.core = core


class Create(AbstractOperatorBase, ABC):
    def __init__(self, operator, core, resource):
        super().__init__(operator, core)
        self.resource = None
        self.resource_json = resource.get()
        # sync
        # self._create_resource()

    # def _create_resource(self):
    #     try:
    #         identifier = self.resource_json["identifier"]
    #         resource_type = self.resource_json["resourceType"]
    #         is_exist = self._is_resource_exist(resource_type, identifier[0]["value"])
    #         if is_exist:
    #             return
    #         self.resource = self.core.sync_client.resource(resource_type)
    #         for k, v in self.resource_json.items():
    #             self.resource[k] = v
    #     except KeyError:
    #         self.resource = None
    #         print("Please provide identifier for this resource")

    async def update_reference(self, **kwargs):
        if self.resource is None:
            return

    async def save(self):
        try:
            identifier = self.resource_json["identifier"]
            resource_type = self.resource_json["resourceType"]
            resource = await self._is_resource_exist(resource_type, identifier[0]["value"])
            if resource is not False:
                self.resource = resource
                return self.resource
            self.resource = self.core.async_client.resource(resource_type)
            for k, v in self.resource_json.items():
                self.resource[k] = v
        except KeyError:
            self.resource = None
            print("Please provide identifier for this resource")
        self.resource = await self.resource.create()
        return self.resource

    async def _is_resource_exist(self, resource_type, identifier):
        resources = await self.core.search().search_resources_async(resource_type=resource_type, identifier=identifier)
        if resources is not None and len(resources) > 0:
            print(f"the {resource_type} already exist! identifier: {identifier}")
            return resources[0]
        return False

