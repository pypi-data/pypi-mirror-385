from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, CodeableConcept, Coding, Reference, Period, ContactPoint, Code)
from typing import Optional, List, Literal


class Endpoint(AbstractResource, ABC):

    def __init__(self, status: Literal["active", "suspended", "error", "off", "entered-in-error", "test"],
                 connection_type: Coding, address: str, payload_type: List[CodeableConcept],
                 meta: Optional[Meta] = None,
                 identifier: Optional[List[Identifier]] = None, name: Optional[str] = None,
                 managing_organization: Optional[Reference] = None, contact: Optional[List[ContactPoint]] = None,
                 period: Optional[Period] = None,
                 payload_mime_type: Optional[List[Code]] = None, header: Optional[List[str]] = None):
        """
        :param status: active | suspended | error | off | entered-in-error | test
        :param connection_type: https://hl7.org/fhir/R4/valueset-endpoint-connection-type.html#expansion
        :param payload_type: https://hl7.org/fhir/R4/valueset-endpoint-payload-type.html
        """
        super().__init__(meta, identifier)
        self._resource_type = "Endpoint"
        self.status = status
        self.connection_type = connection_type
        self.address = address
        self.name = name
        self.managing_organization = managing_organization
        self.contact = contact
        self.period = period
        self.payload_type = payload_type
        self.payload_mime_type = payload_mime_type
        self.header = header

    def get(self):
        endpoint = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "status": self.status if self.status in ["active", "suspended", "error", "off", "entered-in-error",
                                                     "test"] else None,
            "connectionType": self.connection_type.get() if isinstance(self.connection_type, Coding) else None,
            "name": self.name if isinstance(self.name, str) else None,
            "managingOrganization": self.managing_organization.get() if isinstance(self.managing_organization,
                                                                                   Reference) else None,
            "contact": [c.get() for c in self.contact if isinstance(c, ContactPoint)] if isinstance(self.contact,
                                                                                                    list) else None,
            "period": self.period if isinstance(self.period, Period) else None,
            "payloadType": [p.get() for p in self.payload_type if isinstance(p, CodeableConcept)] if isinstance(
                self.payload_type, list) else None,
            "payloadMimeType": [p.get() for p in self.payload_mime_type if isinstance(p, Code)] if isinstance(
                self.payload_mime_type, list) else None,
            "address": self.address if isinstance(self.address, str) else None,
            "header": [h for h in self.header if isinstance(h, str)] if isinstance(self.header, list) else None
        }
        return {k: v for k, v in endpoint.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
