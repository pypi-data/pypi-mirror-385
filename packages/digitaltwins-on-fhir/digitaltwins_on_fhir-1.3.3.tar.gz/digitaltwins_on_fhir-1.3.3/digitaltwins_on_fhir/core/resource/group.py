from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, CodeableConcept, Reference, Period, Range, Quantity)
from typing import Optional, List, Literal


class GroupValue:
    def __init__(self, value_codeable_concept: Optional[CodeableConcept] = None, value_boolean: Optional[bool] = None,
                 value_quantity: Optional[Quantity] = None, value_range: Optional[Range] = None,
                 value_reference: Optional[Reference] = None):
        self.value_codeable_concept = value_codeable_concept
        self.value_boolean = value_boolean
        self.value_quantity = value_quantity
        self.value_range = value_range
        self.value_reference = value_reference

    def get(self):
        value = {
            "valueCodeableConcept": self.value_codeable_concept.get() if isinstance(self.value_codeable_concept,
                                                                                    CodeableConcept) else None,
            "valueBoolean": self.value_boolean if isinstance(self.value_boolean, bool) else None,
            "valueQuantity": self.value_quantity.get() if isinstance(self.value_quantity, Quantity) else None,
            "valueRange": self.value_range.get() if isinstance(self.value_range, Range) else None,
            "valueReference": self.value_reference.get() if isinstance(self.value_reference, Reference) else None
        }
        return {k: v for k, v in value.items() if v not in ("", None)}


class Characteristic:
    def __init__(self, code: CodeableConcept, value: GroupValue, exclude: bool = False,
                 period: Optional[Period] = None):
        self.code = code
        self.value = value
        self.exclude = exclude
        self.period = period

    def get(self):
        characteristic = {
            "code": self.code.get() if isinstance(self.code, CodeableConcept) else None,
            "valueCodeableConcept": self.value.get().get("valueCodeableConcept") if isinstance(self.value,
                                                                                           GroupValue) else None,
            "valueBoolean": self.value.get().get("valueBoolean") if isinstance(self.value, GroupValue) else None,
            "valueQuantity": self.value.get().get("valueQuantity") if isinstance(self.value, GroupValue) else None,
            "valueRange": self.value.get().get("valueRange") if isinstance(self.value, GroupValue) else None,
            "valueReference": self.value.get().get("valueReference") if isinstance(self.value, GroupValue) else None,
            "exclude": self.exclude if isinstance(self.exclude, bool) else False,
            "period": self.period.get() if isinstance(self.period, Period) else None
        }

        return {k: v for k, v in characteristic.items() if v not in ("", None)}


class GroupMember:

    def __init__(self, entity: Reference, period: Optional[Period] = None, inactive: Optional[bool] = None):
        self.entity = entity
        self.period = period
        self.inactive = inactive

    def get(self):
        member = {
            "entity": self.entity.get() if isinstance(self.entity, Reference) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "inactive": self.inactive if isinstance(self.inactive, bool) else None
        }
        return {k: v for k, v in member.items() if v not in ("", None)}


class Group(AbstractResource, ABC):

    def __init__(self, group_type: Literal["person", "animal", "practitioner", "device", "medication", "substance"],
                 actual: bool = True,
                 meta: Optional[Meta] = None, identifier: Optional[List[Identifier]] = None,
                 active: Optional[bool] = None,
                 code: Optional[CodeableConcept] = None,
                 name: Optional[str] = None, quantity: Optional[int] = None,
                 managing_entity: Optional[Reference] = None, characteristic: Optional[List[Characteristic]] = None,
                 member: Optional[List[GroupMember]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Group"
        self.active = active
        self.group_type = group_type
        self.actual = actual
        self.code = code
        self.name = name
        self.quantity = quantity
        self.managing_entity = managing_entity
        self.characteristic = characteristic
        self.member = member

    def get(self):
        group = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "active": self.active if isinstance(self.active, bool) else None,
            "type": self.group_type if self.group_type in ["person", "animal", "practitioner", "device", "medication",
                                                 "substance"] else None,
            "actual": self.actual if isinstance(self.actual, bool) else None,
            "code": self.code.get() if isinstance(self.code, CodeableConcept) else None,
            "name": self.name if isinstance(self.name, str) else None,
            "quantity": self.quantity if isinstance(self.quantity, int) and self.quantity > 0 else None,
            "managingEntity": self.managing_entity.get() if isinstance(self.managing_entity, Reference) else None,
            "characteristic": [c.get() for c in self.characteristic if isinstance(c, Characteristic)] if isinstance(
                self.characteristic, list) else None,
            "member": [m.get() for m in self.member if isinstance(m, GroupMember)] if isinstance(self.member,
                                                                                                 list) else None
        }
        return {k: v for k, v in group.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
