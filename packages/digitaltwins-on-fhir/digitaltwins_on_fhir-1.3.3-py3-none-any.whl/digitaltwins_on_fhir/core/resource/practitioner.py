from abc import ABC
from .abstract_resource import AbstractResource
from .element import Meta, Identifier, HumanName, ContactPoint, Address, CodeableConcept, Attachment, Reference, Period
from typing import Optional, List, Literal


class Qualification:

    def __init__(self, identifier: Optional[List[Identifier]] = None, code: CodeableConcept = None,
                 period: Optional[Period] = None, issuer: Optional[Reference] = None):
        self.identifier = identifier
        self.code = code
        self.period = period
        self.issuer = issuer

    def get(self):
        qualification = {
            "identifier": [i.get() for i in self.identifier if isinstance(i, Identifier)] if isinstance(self.identifier,
                                                                                                        list) else None,
            "code": self.code.get() if isinstance(self.code, CodeableConcept) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "issuer": self.issuer.get() if isinstance(self.issuer, Reference) else None
        }
        return {k: v for k, v in qualification.items() if v not in ("", None, [])}


class Practitioner(AbstractResource, ABC):

    def __init__(self, meta: Optional[Meta] = None, identifier: Optional[List[Identifier]] = None,
                 active: Optional[bool] = None, name: Optional[List[HumanName]] = None,
                 telecom: Optional[List[ContactPoint]] = None, address: Optional[List[Address]] = None,
                 gender: Optional[Literal["male", "female", "other", "unknown", ""]] = None,
                 birth_date: Optional[str] = None, photo: Optional[List[Attachment]] = None,
                 qualification: Optional[List[Qualification]] = None,
                 communication: Optional[List[CodeableConcept]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Practitioner"
        self.active = active
        self.name = name
        self.telecom = telecom
        self.address = address
        self.gender = gender
        self.birth_date = birth_date
        self.photo = photo
        self.qualification = qualification
        self.communication = communication

    def get(self):
        practitioner = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "active": self.active if isinstance(self.active, bool) else None,
            "name": [n.get() for n in self.name if isinstance(n, HumanName)] if isinstance(self.name, list) else None,
            "telecom": [t.get() for t in self.telecom if
                        isinstance(t, ContactPoint)] if isinstance(self.telecom, list) else None,
            "address": [a.get() for a in self.address if isinstance(a, Address)] if isinstance(self.address,
                                                                                               list) else None,
            "gender": self.gender if self.gender in ["male", "female", "other", "unknown"] else None,
            "birthDate": self.birth_date,
            "photo": [p.get() for p in self.photo if isinstance(p, Attachment)] if isinstance(self.photo,
                                                                                              list) else None,
            "qualification": [q.get() for q in self.qualification if isinstance(q, Qualification)] if isinstance(
                self.qualification, list) else None,
            "communication": [c.get() for c in self.communication if isinstance(c, CodeableConcept)] if isinstance(
                self.communication, list) else None
        }
        return {k: v for k, v in practitioner.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
