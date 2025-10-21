import fhirpy
import digitaltwins_on_fhir
from abc import ABC, abstractmethod


class AbstractDigitalTWINBase(ABC):
    core = None
    operator = None

    def __init__(self, core, operator):
        self.core: digitaltwins_on_fhir.Adapter = core
        self.operator = operator
        self.client: fhirpy.lib.AsyncClient = core.async_client

    async def get_resource(self, resource_type, identifier):
        resource = await self.client.resources(resource_type).search(identifier=identifier).first()
        return resource
    # async def _get_existing_resource(self, resource: AbstractResource):
    #     if resource.identifier is None or len(resource.identifier) == 0:
    #         return
    #     resources = await self.operator.core.search().search_resource_async(resource_type=resource.resource_type,
    #                                                                         identifier=resource.identifier[0]["value"])
    #     return resources
