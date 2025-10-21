from abc import ABC
from xml.dom.minidom import Document

from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, Reference, Attachment, Coding, CodeableConcept, Period)
from typing import Optional, List, Literal


class DocumentReferenceRelatesTo:
    def __init__(self, code: Literal["replaces", "transforms", "signs", "appends"], target: Reference):
        self.code = code
        self.target = target

    def get(self):
        relates_to = {
            "code": self.code if self.code in ["replaces", "transforms", "signs", "appends"] else None,
            "target": self.target.get() if isinstance(self.target, Reference) else None
        }
        return {k: v for k, v in relates_to.items() if v not in ("", None, [])}


class DocumentReferenceContent:
    def __init__(self, attachment: Attachment, content_format: Optional[Coding] = None):
        self.attachment = attachment
        self.content_format = content_format

    def get(self):
        content = {
            "attachment": self.attachment.get() if isinstance(self.attachment, Attachment) else None,
            "format": self.content_format.get() if isinstance(self.content_format, Coding) else None
        }
        return {k: v for k, v in content.items() if v not in ("", None, [])}


class DocumentReferenceContext:
    def __init__(self, encounter: Optional[List[Reference]] = None, event: Optional[List[CodeableConcept]] = None,
                 period: Optional[Period] = None, facility_type: Optional[CodeableConcept] = None,
                 practice_setting: Optional[CodeableConcept] = None, source_patient_info: Optional[Reference] = None,
                 related: Optional[List[Reference]] = None):
        self.encounter = encounter
        self.event = event
        self.period = period
        self.facility_type = facility_type
        self.practice_setting = practice_setting
        self.source_patient_info = source_patient_info
        self.related = related

    def get(self):
        context = {
            "encounter": [e.get() for e in self.encounter if isinstance(e, Reference)] if isinstance(self.encounter,
                                                                                                     List) else None,
            "event": [e.get() for e in self.event if isinstance(e, CodeableConcept)] if isinstance(self.event,
                                                                                                   List) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "facilityType": self.facility_type.get() if isinstance(self.facility_type, CodeableConcept) else None,
            "practiceSetting": self.practice_setting.get() if isinstance(self.practice_setting,
                                                                         CodeableConcept) else None,
            "sourcePatientInfo": self.source_patient_info.get() if isinstance(self.source_patient_info,
                                                                              Reference) else None,
            "related": [r.get() for r in self.related if isinstance(r, Reference)] if isinstance(self.related,
                                                                                                 List) else None
        }
        return {k: v for k, v in context.items() if v not in ("", None, [])}


class DocumentReference(AbstractResource, ABC):
    def __init__(self, status: Literal["current", "superseded", "entered-in-error"],
                 content: List[DocumentReferenceContent],
                 meta: Optional[Meta] = None, master_identifier: Optional[Identifier] = None,
                 identifier: Optional[List[Identifier]] = None,
                 doc_status: Optional[Literal["preliminary", "final", "amended", "entered-in-error"]] = None,
                 document_reference_type: Optional[CodeableConcept] = None,
                 category: Optional[List[CodeableConcept]] = None,
                 subject: Optional[Reference] = None,
                 date: Optional[str] = None, author: Optional[List[Reference]] = None,
                 authenticator: Optional[Reference] = None, custodian: Optional[Reference] = None,
                 relates_to: Optional[List[DocumentReferenceRelatesTo]] = None,
                 description: Optional[str] = None,
                 security_label: Optional[List[CodeableConcept]] = None,
                 context: Optional[DocumentReferenceContext] = None,
                 ):
        super().__init__(meta, identifier)
        self._resource_type = "DocumentReference"
        self.status = status
        self.content = content
        self.meta = meta
        self.master_identifier = master_identifier
        self.identifier = identifier
        self.doc_status = doc_status
        self.document_reference_type = document_reference_type
        self.category = category
        self.subject = subject
        self.date = date
        self.author = author
        self.authenticator = authenticator
        self.custodian = custodian
        self.relates_to = relates_to
        self.description = description
        self.security_label = security_label
        self.context = context

    def get(self):
        research_subject = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "masterIdentifier": self.master_identifier.get() if isinstance(self.master_identifier,
                                                                           Identifier) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "status": self.status if self.status in ["current", "superseded", "entered-in-error"] else None,
            "docStatus": self.doc_status if self.doc_status in ["preliminary", "final", "amended",
                                                                "entered-in-error"] else None,
            "type": self.document_reference_type.get() if isinstance(self.document_reference_type,
                                                                     CodeableConcept) else None,
            "category": [c.get() for c in self.category if isinstance(c, CodeableConcept)] if isinstance(self.category,
                                                                                                         list) else None,
            "subject": self.subject.get() if isinstance(self.subject, Reference) else None,
            "date": self.date if isinstance(self.date, str) else None,
            "author": [a.get() for a in self.author if isinstance(a, Reference)] if isinstance(self.author,
                                                                                               List) else None,
            "authenticator": self.authenticator.get() if isinstance(self.authenticator, Reference) else None,
            "custodian": self.custodian.get() if isinstance(self.custodian, Reference) else None,
            "relatesTo": [r.get() for r in self.relates_to if isinstance(r, DocumentReferenceRelatesTo)] if isinstance(
                self.relates_to, List) else None,
            "description": self.description if isinstance(self.description, str) else None,
            "securityLabel": [s.get() for s in self.security_label if isinstance(s, CodeableConcept)] if isinstance(
                self.security_label, list) else None,
            "content": [c.get() for c in self.content if isinstance(c, DocumentReferenceContent)] if isinstance(
                self.content, List) else None,
            "context": self.context.get() if isinstance(self.context, DocumentReferenceContext) else None,
        }
        return {k: v for k, v in research_subject.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
