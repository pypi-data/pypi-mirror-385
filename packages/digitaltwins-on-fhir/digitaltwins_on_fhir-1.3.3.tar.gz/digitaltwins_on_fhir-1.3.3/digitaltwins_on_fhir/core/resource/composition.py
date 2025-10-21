from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, Reference, CodeableConcept, Code, Period, Narrative)
from typing import Optional, List, Literal, Any


class CompositionAttester:
    def __init__(self, mode: Literal["personal", "professional", "legal", "official"], time: Optional[str] = None,
                 party: Optional[Reference] = None):
        self.mode = mode
        self.time = time
        self.party = party

    def get(self):
        attester = {
            "mode": self.mode if self.mode in ["personal", "professional", "legal", "official"] else None,
            "time": self.time if isinstance(self.time, str) else None,
            "party": self.party.get() if isinstance(self.party, Reference) else None
        }
        return {k: v for k, v in attester.items() if v not in ("", None)}


class CompositionTarget:

    def __init__(self, target_identifier: Optional[Identifier], target_reference: Optional[Reference]):
        self.target_identifier = target_identifier
        self.target_reference = target_reference

    def get(self):
        target = {
            "targetIdentifier": self.target_identifier.get() if isinstance(self.target_identifier,
                                                                           Identifier) else None,
            "targetReference": self.target_reference.get() if isinstance(self.target_reference, Reference) else None
        }
        return {k: v for k, v in target.items() if v not in ("", None)}


class CompositionRelatesTo:

    def __init__(self, code: Literal["replaces", "transforms", "signs", "appends"], target: CompositionTarget):
        self.code = code
        self.target = target

    def get(self):
        target = {
            "mode": self.code if self.code in ["replaces", "transforms", "signs", "appends"] else None,
            "targetIdentifier": self.target.get().get("targetIdentifier") if isinstance(self.target,
                                                                                        CompositionTarget) else None,
            "targetReference": self.target.get().get("targetReference") if isinstance(self.target,
                                                                                      CompositionTarget) else None
        }
        return {k: v for k, v in target.items() if v not in ("", None)}


class CompositionEvent:
    def __init__(self, code: Optional[List[CodeableConcept]] = None, period: Optional[Period] = None,
                 detail: Optional[List[Reference]] = None):
        self.code = code
        self.period = period
        self.detail = detail

    def get(self):
        event = {
            "code": [c.get() for c in self.code if isinstance(c, CodeableConcept)] if isinstance(self.code,
                                                                                                 list) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "detail": [d.get() for d in self.detail if isinstance(d, Reference)] if isinstance(self.detail,
                                                                                               list) else None
        }
        return {k: v for k, v in event.items() if v not in ("", None, [])}


class CompositionSection:

    def __init__(self, title: Optional[str] = None, code: Optional[CodeableConcept] = None,
                 author: Optional[List[Reference]] = None,
                 focus: Optional[Reference] = None, text: Optional[Narrative] = None,
                 mode: Optional[Literal["working", "snapshot", "changes"]] = None,
                 ordered_by: Optional[CodeableConcept] = None, entry: Optional[List[Reference]] = None,
                 empty_reason: Optional[CodeableConcept] = None, section: Optional[List[Any]] = None):
        self.title = title
        self.code = code
        self.author = author
        self.focus = focus
        self.text = text
        self.mode = mode
        self.ordered_by = ordered_by
        self.entry = entry
        self.empty_reason = empty_reason
        self.section = section

    def get(self):
        section = {
            "title": self.title if isinstance(self.title, str) else None,
            "code": self.code.get() if isinstance(self.code, CodeableConcept) else None,
            "author": [a.get() for a in self.author if isinstance(a, Reference)] if isinstance(self.author,
                                                                                               list) else None,
            "focus": self.focus.get() if isinstance(self.focus, Reference) else None,
            "text": self.text.get() if isinstance(self.text, Narrative) else None,
            "mode": self.mode if self.mode in ["working", "snapshot", "changes"] else None,
            "orderedBy": self.ordered_by.get() if isinstance(self.ordered_by, CodeableConcept) else None,
            "entry": [e.get() for e in self.entry if isinstance(e, Reference)] if isinstance(self.entry,
                                                                                             list) else None,
            "emptyReason": self.empty_reason.get() if isinstance(self.empty_reason, CodeableConcept) else None,
            "section": [s.get() for s in self.section if isinstance(s, CompositionSection)] if isinstance(self.section,
                                                                                                          list) else None
        }
        return {k: v for k, v in section.items() if v not in ("", None, [])}


class Composition(AbstractResource, ABC):

    def __init__(self, status: Literal["preliminary", "final", "amended", "entered-in-error"],
                 composition_type: CodeableConcept, date: str, author: List[Reference], title: str,
                 meta: Optional[Meta] = None, identifier: Optional[List[Identifier]] = None,
                 category: Optional[List[CodeableConcept]] = None, subject: Optional[Reference] = None,
                 encounter: Optional[Reference] = None, confidentiality: Optional[Code] = None,
                 attester: Optional[List[CompositionAttester]] = None, custodian: Optional[Reference] = None,
                 relates_to: Optional[List[CompositionRelatesTo]] = None,
                 event: Optional[List[CompositionEvent]] = None, section: Optional[List[CompositionSection]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Composition"
        self.status = status
        self.composition_type = composition_type
        self.category = category
        self.subject = subject
        self.encounter = encounter
        self.date = date
        self.author = author
        self.title = title
        self.confidentiality = confidentiality
        self.attester = attester
        self.custodian = custodian
        self.relates_to = relates_to
        self.event = event
        self.section = section

    def get(self):
        composition = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "status": self.status if self.status in ["preliminary", "final", "amended", "entered-in-error"] else None,
            "type": self.composition_type.get() if isinstance(self.composition_type, CodeableConcept) else None,
            "category": [c.get() for c in self.category if isinstance(c, CodeableConcept)] if isinstance(self.category,
                                                                                                         list) else None,
            "subject": self.subject.get() if isinstance(self.subject, Reference) else None,
            "encounter": self.encounter.get() if isinstance(self.encounter, Reference) else None,
            "date": self.date if isinstance(self.date, str) else None,
            "author": [a.get() for a in self.author if isinstance(a, Reference)] if isinstance(self.author,
                                                                                               list) else None,
            "title": self.title if isinstance(self.title, str) else None,
            "confidentiality": self.confidentiality.get() if isinstance(self.confidentiality, Code) else None,
            "attester": [a.get() for a in self.attester if isinstance(a, CompositionAttester)] if isinstance(
                self.attester, list) else None,
            "custodian": self.custodian.get() if isinstance(self.custodian, Reference) else None,
            "relatesTo": [r.get() for r in self.relates_to if isinstance(r, CompositionRelatesTo)] if isinstance(
                self.relates_to, list) else None,
            "event": [e.get() for e in self.event if isinstance(e, CompositionEvent)] if isinstance(self.event,
                                                                                                    list) else None,
            "section": [s.get() for s in self.section if isinstance(s, CompositionSection)] if isinstance(self.section,
                                                                                                          list) else None
        }
        return {k: v for k, v in composition.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
