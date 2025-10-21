from abc import ABC

from .abstract_resource import AbstractResource
from .element import Meta, Identifier, HumanName, ContactPoint, Address, CodeableConcept, Attachment, Reference, Period
from typing import Optional, List, Literal


class Deceased:
    def __init__(self, deceased_boolean: bool, deceased_date_time: str):
        self.deceased_boolean = deceased_boolean,
        self.deceased_date_time = deceased_date_time

    def get(self):
        deceased = {
            "deceasedBoolean": self.deceased_boolean if isinstance(self.deceased_boolean, bool) else None,
            "deceasedDateTime": self.deceased_date_time if isinstance(self.deceased_date_time, str) else None
        }
        return {k: v for k, v in deceased.items() if v not in ("", None)}


class MultipleBrith:

    def __init__(self, multiple_birth_boolean: bool, multiple_birth_integer: int):
        self.multiple_birth_boolean = multiple_birth_boolean,
        self.multiple_birth_integer = multiple_birth_integer

    def get(self):
        multiple_brith = {
            "multipleBirthBoolean": self.multiple_birth_boolean if isinstance(self.multiple_birth_boolean,
                                                                              bool) else None,
            "multipleBirthInteger": self.multiple_birth_integer if isinstance(self.multiple_birth_integer,
                                                                              int) else None
        }
        return {k: v for k, v in multiple_brith.items() if v not in ("", None)}


class Contact:

    def __init__(self, relationship: Optional[List[CodeableConcept]] = None, name: Optional[HumanName] = None,
                 telecom: Optional[List[ContactPoint]] = None, address: Optional[Address] = None,
                 gender: Optional[Literal["male", "female", "other", "unknown", ""]] = None,
                 organization: Optional[Reference] = None, period: Optional[Period] = None):
        self.relationship = relationship
        self.name = name
        self.telecom = telecom
        self.address = address
        self.gender = gender
        self.organization = organization
        self.period = period

    def get(self):
        contact = {
            "relationship": [r.get() for r in self.relationship if isinstance(r, CodeableConcept)] if isinstance(
                self.relationship, list) else None,
            "name": self.name.get() if isinstance(self.name, HumanName) else None,
            "telecom": [t.get() for t in self.telecom if isinstance(t, ContactPoint)] if isinstance(self.telecom,
                                                                                                    list) else None,
            "address": self.address.get() if isinstance(self.address, Address) else None,
            "gender": self.gender if self.gender in ["male", "female", "other", "unknown"] else None,
            "organization": self.organization.get() if isinstance(self.organization, Reference) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None
        }
        return {k: v for k, v in contact.items() if v not in ("", None)}


class Communication:

    def __init__(self, language: CodeableConcept, preferred: Optional[bool] = None):
        self.language = language
        self.preferred = preferred

    def get(self):
        communication = {
            "language": self.language.get() if isinstance(self.language, CodeableConcept) else None,
            "preferred": self.preferred
        }
        return {k: v for k, v in communication.items() if v not in ("", None)}


class Link:

    def __init__(self, other: Reference, link_type: Literal["replaced-by", "replaces", "refer", "seealso"]):
        self.other = other
        self.link_type = link_type

    def get(self):
        link = {
            "other": self.other.get() if isinstance(self.other, Reference) else None,
            "type": self.link_type if self.link_type in ["replaced-by", "replaces", "refer", "seealso"] else None
        }
        return {k: v for k, v in link.items() if v not in ("", None)}


class Patient(AbstractResource, ABC):

    def __init__(self, meta: Optional[Meta] = None,
                 identifier: Optional[List[Identifier]] = None,
                 active: Optional[bool] = None, name: Optional[List[HumanName]] = None,
                 telecom: Optional[List[ContactPoint]] = None,
                 gender: Optional[Literal["male", "female", "other", "unknown", ""]] = None,
                 birth_date: Optional[str] = None, deceased: Optional[Deceased] = None,
                 address: Optional[List[Address]] = None,
                 marital_status: Optional[CodeableConcept] = None, multiple_brith: Optional[MultipleBrith] = None,
                 photo: Optional[List[Attachment]] = None, contact: Optional[List[Contact]] = None,
                 communication: Optional[List[Communication]] = None,
                 general_practitioner: Optional[List[Reference]] = None,
                 managing_organization: Optional[Reference] = None, link: Optional[List[Link]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Patient"
        self.active = active
        self.name = name
        self.telecom = telecom
        self.gender = gender
        self.birth_date = birth_date
        self.deceased = deceased
        self.address = address
        self.marital_status = marital_status
        self.multiple_brith = multiple_brith
        self.photo = photo
        self.contact = contact
        self.communication = communication
        self.general_practitioner = general_practitioner
        self.managing_organization = managing_organization
        self.link = link

    def get(self):
        patient = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "active": self.active if isinstance(self.active, bool) else None,
            "name": [n.get() for n in self.name if isinstance(n, HumanName)] if isinstance(self.name, list) else None,
            "telecom": [t.get() for t in self.telecom if
                        isinstance(t, ContactPoint)] if isinstance(self.telecom, list) else None,
            "gender": self.gender if self.gender in ["male", "female", "other", "unknown"] else None,
            "birthDate": self.birth_date,
            "deceasedBoolean": self.deceased.get().get("deceasedBoolean") if isinstance(self.deceased,
                                                                                        Deceased) else None,
            "deceasedDateTime": self.deceased.get().get("deceasedDateTime") if isinstance(self.deceased,
                                                                                          Deceased) else None,
            "address": [a.get() for a in self.address if isinstance(a, Address)] if isinstance(self.address,
                                                                                               list) else None,
            "maritalStatus": self.marital_status.get() if isinstance(self.marital_status, CodeableConcept) else None,
            "multipleBirthBoolean": self.multiple_brith.get().get("multipleBirthBoolean") if isinstance(
                self.multiple_brith,
                MultipleBrith) else None,
            "multipleBirthInteger": self.multiple_brith.get().get("multipleBirthInteger") if isinstance(
                self.multiple_brith,
                MultipleBrith) else None,
            "photo": [p.get() for p in self.photo if isinstance(p, Attachment)] if isinstance(self.photo,
                                                                                              list) else None,
            "contact": [c.get() for c in self.contact if isinstance(c, Contact)] if isinstance(self.contact,
                                                                                               list) else None,
            "communication": [c.get() for c in self.communication if
                              isinstance(c, Communication)] if isinstance(self.communication, list) else None,
            "generalPractitioner": [g.get() for g in self.general_practitioner if
                                    isinstance(g, Reference)] if isinstance(self.general_practitioner, list) else None,
            "managingOrganization": self.managing_organization.get() if isinstance(self.managing_organization,
                                                                                   Reference) else None,
            "link": [l.get() for l in self.link if isinstance(l, Link)] if isinstance(self.link, list) else None
        }

        return {k: v for k, v in patient.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
