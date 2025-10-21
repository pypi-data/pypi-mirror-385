from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, Reference, CodeableConcept, Annotation, Period, Range)
from typing import Optional, List, Literal


class ProcedurePerformed:

    def __init__(self, performed_date_time: Optional[str] = None, performed_period: Optional[Period] = None,
                 performed_string: Optional[str] = None, performed_age: Optional[str] = None,
                 performed_range: Optional[Range] = None):
        self.performed_date_time = performed_date_time
        self.performed_period = performed_period
        self.performed_string = performed_string
        self.performed_age = performed_age
        self.performed_range = performed_range

    def get(self):
        performed = {
            "performedDateTime": self.performed_date_time if isinstance(self.performed_date_time, str) else None,
            "performedPeriod": self.performed_period.get() if isinstance(self.performed_period, Period) else None,
            "performedString": self.performed_string if isinstance(self.performed_string, str) else None,
            "performedAge": self.performed_age if isinstance(self.performed_age, str) else None,
            "performedRange": self.performed_range.get() if isinstance(self.performed_range, Range) else None,
        }
        return {k: v for k, v in performed.items() if v not in ("", None)}


class ProcedurePerformer:

    def __init__(self, actor: Reference, function: Optional[CodeableConcept] = None,
                 on_behalf_of: Optional[Reference] = None):
        self.actor = actor
        self.function = function
        self.on_behalf_of = on_behalf_of

    def get(self):
        performer = {
            "function": self.function.get() if isinstance(self.function, CodeableConcept) else None,
            "actor": self.actor.get() if isinstance(self.actor, Reference) else None,
            "onBehalfOf": self.on_behalf_of.get() if isinstance(self.on_behalf_of, Reference) else None
        }
        return {k: v for k, v in performer.items() if v not in ("", None)}


class ProcedureFocalDevice:

    def __init__(self, manipulated: Reference, action: Optional[CodeableConcept] = None):
        self.action = action
        self.manipulated = manipulated

    def get(self):
        focal_device = {
            "action": self.action.get() if isinstance(self.action, CodeableConcept) else None,
            "manipulated": self.manipulated.get() if isinstance(self.manipulated, Reference) else None
        }
        return {k: v for k, v in focal_device.items() if v not in ("", None)}


class Procedure(AbstractResource, ABC):

    def __init__(self, status: Optional[Literal[
        "preparation", "in-progress", "not-done", "on-hold", "stopped", "completed", "entered-in-error", "unknown"]],
                 subject: Reference, meta: Optional[Meta] = None, identifier: Optional[List[Identifier]] = None,
                 instantiates_canonical: Optional[List[str]] = None, instantiates_uri: Optional[List[str]] = None,
                 based_on: Optional[List[Reference]] = None, part_of: Optional[List[Reference]] = None,
                 status_reason: Optional[CodeableConcept] = None, category: Optional[CodeableConcept] = None,
                 code: Optional[CodeableConcept] = None, encounter: Optional[Reference] = None,
                 performed: Optional[ProcedurePerformed] = None, recorder: Optional[Reference] = None,
                 asserter: Optional[Reference] = None, performer: Optional[List[ProcedurePerformer]] = None,
                 location: Optional[Reference] = None, reason_code: Optional[List[CodeableConcept]] = None,
                 reason_reference: Optional[List[Reference]] = None, body_site: Optional[List[CodeableConcept]] = None,
                 outcome: Optional[CodeableConcept] = None, report: Optional[List[Reference]] = None,
                 complication: Optional[List[CodeableConcept]] = None,
                 complication_detail: Optional[List[Reference]] = None,
                 follow_up: Optional[List[CodeableConcept]] = None, note: Optional[List[Annotation]] = None,
                 focal_device: Optional[List[ProcedureFocalDevice]] = None,
                 used_reference: Optional[List[Reference]] = None, used_code: Optional[List[CodeableConcept]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Procedure"
        self.instantiates_canonical = instantiates_canonical
        self.instantiates_uri = instantiates_uri
        self.based_on = based_on
        self.part_of = part_of
        self.status = status
        self.status_reason = status_reason
        self.category = category
        self.code = code
        self.subject = subject
        self.encounter = encounter
        self.performed = performed
        self.recorder = recorder
        self.asserter = asserter
        self.performer = performer
        self.location = location
        self.reason_code = reason_code
        self.reason_reference = reason_reference
        self.body_site = body_site
        self.outcome = outcome
        self.report = report
        self.complication = complication
        self.complication_detail = complication_detail
        self.follow_up = follow_up
        self.note = note
        self.focal_device = focal_device
        self.used_reference = used_reference
        self.used_code = used_code

    def get(self):
        procedure = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "instantiatesCanonical": [i for i in self.instantiates_canonical if isinstance(i, str)] if isinstance(
                self.instantiates_canonical, list) else None,
            "instantiatesUri": [i for i in self.instantiates_uri if isinstance(i, str)] if isinstance(
                self.instantiates_uri, list) else None,
            "basedOn": [b.get() for b in self.based_on if isinstance(b, Reference)] if isinstance(self.based_on,
                                                                                                  list) else None,
            "partOf": [p.get() for p in self.part_of if isinstance(p, Reference)] if isinstance(self.part_of,
                                                                                                list) else None,
            "status": self.status if self.status in [
                "preparation", "in-progress", "not-done", "on-hold", "stopped", "completed", "entered-in-error",
                "unknown"] else None,
            "statusReason": self.status_reason.get() if isinstance(self.status_reason, CodeableConcept) else None,
            "category": self.category.get() if isinstance(self.category, CodeableConcept) else None,
            "code": self.code.get() if isinstance(self.code, CodeableConcept) else None,
            "subject": self.subject.get() if isinstance(self.subject, Reference) else None,
            "encounter": self.encounter.get() if isinstance(self.encounter, Reference) else None,
            "performedDateTime": self.performed.get().get("performedDateTime") if isinstance(self.performed,
                                                                                             ProcedurePerformed) else None,
            "performedPeriod": self.performed.get().get("performedPeriod") if isinstance(self.performed,
                                                                                         ProcedurePerformed) else None,
            "performedString": self.performed.get().get("performedString") if isinstance(self.performed,
                                                                                         ProcedurePerformed) else None,
            "performedAge": self.performed.get().get("performedAge") if isinstance(self.performed,
                                                                                   ProcedurePerformed) else None,
            "performedRange": self.performed.get().get("performedRange") if isinstance(self.performed,
                                                                                       ProcedurePerformed) else None,
            "recorder": self.recorder.get() if isinstance(self.recorder, Reference) else None,
            "asserter": self.asserter.get() if isinstance(self.asserter, Reference) else None,
            "performer": [p.get() for p in self.performer if isinstance(p, ProcedurePerformer)] if isinstance(
                self.performer, list) else None,
            "location": self.location.get() if isinstance(self.location, Reference) else None,
            "reasonCode": [r.get() for r in self.reason_code if isinstance(r, CodeableConcept)] if isinstance(
                self.reason_code, list) else None,
            "reasonReference": [r.get() for r in self.reason_reference if isinstance(r, Reference)] if isinstance(
                self.reason_reference, list) else None,
            "bodySite": [b.get() for b in self.body_site if isinstance(b, CodeableConcept)] if isinstance(
                self.based_on, list) else None,
            "outcome": self.outcome.get() if isinstance(self.outcome, CodeableConcept) else None,
            "report": [r.get() for r in self.report if isinstance(r, Reference)] if isinstance(
                self.report, list) else None,
            "complication": [c.get() for c in self.complication if isinstance(c, CodeableConcept)] if isinstance(
                self.complication, list) else None,
            "complicationDetail": [c.get() for c in self.complication_detail if isinstance(c, Reference)] if isinstance(
                self.complication_detail, list) else None,
            "followUp": [f.get() for f in self.follow_up if isinstance(f, CodeableConcept)] if isinstance(
                self.follow_up, list) else None,
            "note": [n.get() for n in self.note if isinstance(n, Annotation)] if isinstance(
                self.note, list) else None,
            "focalDevice": [f.get() for f in self.focal_device if isinstance(f, ProcedureFocalDevice)] if isinstance(
                self.focal_device, list) else None,
            "usedReference": [u.get() for u in self.used_reference if isinstance(u, Reference)] if isinstance(
                self.used_reference, list) else None,
            "usedCode": [u.get() for u in self.used_code if isinstance(u, CodeableConcept)] if isinstance(
                self.used_code, list) else None,
        }
        return {k: v for k, v in procedure.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
