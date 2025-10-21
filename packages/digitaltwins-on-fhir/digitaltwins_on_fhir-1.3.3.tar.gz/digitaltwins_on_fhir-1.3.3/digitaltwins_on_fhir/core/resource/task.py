from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, Reference, CodeableConcept, Annotation, Period)
from typing import Optional, List, Literal, Any


class TaskRestriction:

    def __init__(self, repetitions: Optional[int] = None, period: Optional[Period] = None,
                 recipient: Optional[List[Reference]] = None):
        self.repetitions = repetitions
        self.period = period
        self.recipient = recipient

    def get(self):
        restriction = {
            "repetitions": self.repetitions if isinstance(self.repetitions, int) and self.repetitions > 0 else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "recipient": [r.get() for r in self.recipient if isinstance(r, Reference)] if isinstance(self.recipient,
                                                                                                     list) else None
        }
        return {k: v for k, v in restriction.items() if v not in ("", None, [])}


class TaskInputOutput:
    def __init__(self, input_output_type: CodeableConcept, value: Any):
        self.input_output_type = input_output_type
        self.value = value

    def get(self):
        param = {
            "type": self.input_output_type.get() if isinstance(self.input_output_type, CodeableConcept) else None,
            "valueReference": self.value.get() if isinstance(self.value, Reference) else None,
            "valuePositiveInt": self.value if isinstance(self.value, int) and self.value > 0 else None,
            "valueString": self.value if isinstance(self.value, str) else None
        }
        return {k: v for k, v in param.items() if v not in ("", None, [])}


class Task(AbstractResource, ABC):

    def __init__(self, status: Literal["draft", "requested", "received", "accepted"], intent: Literal[
        "unknown", "proposal", "plan", "order", "original-order", "reflex-order", "filler-order", "instance-order", "option"],
                 meta: Optional[Meta] = None,
                 identifier: Optional[List[Identifier]] = None,
                 instantiates_canonical: Optional[str] = None, instantiates_uri: Optional[str] = None,
                 based_on: Optional[List[Reference]] = None, group_identifier: Optional[Identifier] = None,
                 part_of: Optional[List[Reference]] = None, status_reason: Optional[CodeableConcept] = None,
                 business_status: Optional[CodeableConcept] = None,
                 priority: Optional[Literal["routine", "urgent", "asap", "stat"]] = None,
                 code: Optional[CodeableConcept] = None, description: Optional[str] = None,
                 focus: Optional[Reference] = None, task_for: Optional[Reference] = None,
                 encounter: Optional[Reference] = None, execution_period: Optional[Period] = None,
                 authored_on: Optional[str] = None, last_modified: Optional[str] = None,
                 requester: Optional[Reference] = None, performer_type: Optional[List[CodeableConcept]] = None,
                 owner: Optional[Reference] = None, location: Optional[Reference] = None,
                 reason_code: Optional[CodeableConcept] = None, reason_reference: Optional[Reference] = None,
                 insurance: Optional[List[Reference]] = None, note: Optional[List[Annotation]] = None,
                 relevant_history: Optional[List[Reference]] = None, restriction: Optional[TaskRestriction] = None,
                 task_input: Optional[List[TaskInputOutput]] = None,
                 task_output: Optional[List[TaskInputOutput]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Task"
        self.instantiates_canonical = instantiates_canonical
        self.instantiates_uri = instantiates_uri
        self.based_on = based_on
        self.group_identifier = group_identifier
        self.part_of = part_of
        self.status = status
        self.status_reason = status_reason
        self.business_status = business_status
        self.intent = intent
        self.priority = priority
        self.code = code
        self.description = description
        self.focus = focus
        self.task_for = task_for
        self.encounter = encounter
        self.execution_period = execution_period
        self.authored_on = authored_on
        self.last_modified = last_modified
        self.requester = requester
        self.performer_type = performer_type
        self.owner = owner
        self.location = location
        self.reason_code = reason_code
        self.reason_reference = reason_reference
        self.insurance = insurance
        self.note = note
        self.relevant_history = relevant_history
        self.restriction = restriction
        self.task_input = task_input
        self.task_output = task_output

    def get(self):
        task = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "instantiatesCanonical": self.instantiates_canonical if isinstance(self.instantiates_canonical,
                                                                               str) else None,
            "instantiatesUri": self.instantiates_uri if isinstance(self.instantiates_uri, str) else None,
            "basedOn": [b.get() for b in self.based_on if isinstance(b, Reference)] if isinstance(self.based_on,
                                                                                                  list) else None,
            "groupIdentifier": self.group_identifier.get() if isinstance(self.group_identifier, Identifier) else None,
            "partOf": [p.get() for p in self.part_of if isinstance(p, Reference)] if isinstance(self.part_of,
                                                                                                list) else None,
            "status": self.status if self.status in ["draft", "requested", "received", "accepted"] else None,
            "statusReason": self.status_reason.get() if isinstance(self.status_reason, CodeableConcept) else None,
            "businessStatus": self.business_status.get() if isinstance(self.business_status, CodeableConcept) else None,
            "intent": self.intent if self.intent in [
                "unknown", "proposal", "plan", "order", "original-order", "reflex-order", "filler-order",
                "instance-order", "option"] else None,
            "priority": self.priority if self.priority in ["routine", "urgent", "asap", "stat"] else None,
            "code": self.code.get() if isinstance(self.code, CodeableConcept) else None,
            "description": self.description if isinstance(self.description, str) else None,
            "focus": self.focus.get() if isinstance(self.focus, Reference) else None,
            "for": self.task_for.get() if isinstance(self.task_for, Reference) else None,
            "encounter": self.encounter.get() if isinstance(self.encounter, Reference) else None,
            "executionPeriod": self.execution_period.get() if isinstance(self.execution_period, Period) else None,
            "authoredOn": self.authored_on if isinstance(self.authored_on, str) else None,
            "lastModified": self.last_modified if isinstance(self.last_modified, str) else None,
            "requester": self.requester.get() if isinstance(self.requester, Reference) else None,
            "performerType": [p.get() for p in self.performer_type if isinstance(p, CodeableConcept)] if isinstance(
                self.performer_type, list) else None,
            "owner": self.owner.get() if isinstance(self.owner, Reference) else None,
            "location": self.location.get() if isinstance(self.location, Reference) else None,
            "reasonCode": self.reason_code.get() if isinstance(self.reason_code, CodeableConcept) else None,
            "reasonReference": self.reason_reference.get() if isinstance(self.reason_reference, Reference) else None,
            "insurance": [i.get() for i in self.insurance if isinstance(i, Reference)] if isinstance(self.insurance,
                                                                                                     list) else None,
            "note": [n.get() for n in self.note if isinstance(n, Annotation)] if isinstance(self.note, list) else None,
            "relevantHistory": [r.get() for r in self.relevant_history if isinstance(r, Reference)] if isinstance(
                self.relevant_history, list) else None,
            "restriction": self.restriction.get() if isinstance(self.restriction, TaskRestriction) else None,
            "input": [i.get() for i in self.task_input if isinstance(i, TaskInputOutput)] if isinstance(self.task_input,
                                                                                                        list) else None,
            "output": [o.get() for o in self.task_output if isinstance(o, TaskInputOutput)] if isinstance(
                self.task_output, list) else None,
        }
        return {k: v for k, v in task.items() if v not in ("", None, [])}

    def convert(self):
        pass
