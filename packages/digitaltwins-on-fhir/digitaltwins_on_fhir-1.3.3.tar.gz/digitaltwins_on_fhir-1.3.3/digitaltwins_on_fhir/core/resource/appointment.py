from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, CodeableConcept, Reference, Period)
from typing import Optional, List, Literal


class AppointmentParticipant:

    def __init__(self, status: Literal["accepted", "declined", "tentative", "needs-action"],
                 participant_type: Optional[List[CodeableConcept]] = None, actor: Optional[Reference] = None,
                 required: Optional[Literal["required", "optional", "information-only"]] = None,
                 period: Optional[Period] = None):
        self.status = status
        self.participant_type = participant_type
        self.actor = actor
        self.required = required
        self.period = period

    def get(self):
        participant = {
            "status": self.status if self.status in ["accepted", "declined", "tentative", "needs-action"] else None,
            "type": [t.get() for t in self.participant_type if isinstance(t, CodeableConcept)] if isinstance(
                self.participant_type,
                list) else None,
            "actor": self.actor.get() if isinstance(self.actor, Reference) else None,
            "required": self.required if self.required in ["required", "optional", "information-only"] else None,
            "period": self.period.get() if isinstance(self.period, Period) else None
        }
        return {k: v for k, v in participant.items() if v not in ("", None, [])}


class Appointment(AbstractResource, ABC):

    def __init__(self, status: Literal[
        "proposed", "pending", "booked", "arrived", "fulfilled", "cancelled", "noshow", "entered-in-error", "checked-in", "waitlist"],
                 participant: Optional[List[AppointmentParticipant]],
                 meta: Optional[Meta] = None, identifier: Optional[List[Identifier]] = None,
                 cancelation_reason: Optional[CodeableConcept] = None,
                 service_category: Optional[List[CodeableConcept]] = None,
                 service_type: Optional[List[CodeableConcept]] = None,
                 specialty: Optional[List[CodeableConcept]] = None, appointment_type: Optional[CodeableConcept] = None,
                 reason_code: Optional[List[CodeableConcept]] = None,
                 reason_reference: Optional[List[CodeableConcept]] = None, priority: Optional[int] = None,
                 description: Optional[str] = None, supporting_information: Optional[List[Reference]] = None,
                 start: Optional[str] = None,
                 end: Optional[str] = None,
                 minutes_duration: Optional[int] = None,
                 slot: Optional[List[Reference]] = None, created: Optional[str] = None, comment: Optional[str] = None,
                 patient_instruction: Optional[str] = None, based_on: Optional[List[Reference]] = None,
                 requested_period: Optional[List[Period]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Appointment"
        self.status = status
        self.cancelation_reason = cancelation_reason
        self.service_category = service_category
        self.service_type = service_type
        self.specialty = specialty
        self.appointment_type = appointment_type
        self.reason_code = reason_code
        self.reason_reference = reason_reference
        self.priority = priority
        self.description = description
        self.supporting_information = supporting_information
        self.start = start
        self.end = end
        self.minutes_duration = minutes_duration
        self.slot = slot
        self.created = created
        self.comment = comment
        self.patient_instruction = patient_instruction
        self.based_on = based_on
        self.participant = participant
        self.requested_period = requested_period

    def get(self):
        appointment = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "status": self.status if self.status in [
                "proposed", "pending", "booked", "arrived", "fulfilled", "cancelled", "noshow", "entered-in-error",
                "checked-in", "waitlist"] else None,
            "cancelationReason": self.cancelation_reason.get() if isinstance(self.cancelation_reason,
                                                                             CodeableConcept) else None,
            "serviceCategory": [s.get() for s in self.service_category if isinstance(s, CodeableConcept)] if isinstance(
                self.service_category, list) else None,
            "serviceType": [s.get() for s in self.service_type if isinstance(s, CodeableConcept)] if isinstance(
                self.service_type, list) else None,
            "specialty": [s.get() for s in self.specialty if isinstance(s, CodeableConcept)] if isinstance(
                self.specialty, list) else None,
            "appointmentType": self.appointment_type.get() if isinstance(self.appointment_type,
                                                                         CodeableConcept) else None,
            "reasonCode": [r.get() for r in self.reason_code if isinstance(r, CodeableConcept)] if isinstance(
                self.reason_code, list) else None,
            "reasonReference": [r.get() for r in self.reason_reference if isinstance(r, Reference)] if isinstance(
                self.reason_reference, list) else None,
            "priority": self.priority if isinstance(self.priority, int) and self.priority >= 0 else None,
            "description": self.description if isinstance(self.description, str) else None,
            "supportingInformation": [s.get() for s in self.supporting_information if
                                      isinstance(s, Reference)] if isinstance(self.supporting_information,
                                                                              list) else None,
            "start": self.start if isinstance(self.start, str) else None,
            "end": self.end if isinstance(self.end, str) else None,
            "minutesDuration": self.minutes_duration if isinstance(self.minutes_duration,
                                                                   int) and self.minutes_duration > 0 else None,
            "slot": [s.get() for s in self.slot if isinstance(s, Reference)] if isinstance(self.slot, list) else None,
            "created": self.created if isinstance(self.created, str) else None,
            "comment": self.comment if isinstance(self.comment, str) else None,
            "patientInstruction": self.patient_instruction if isinstance(self.patient_instruction, str) else None,
            "basedOn": [b.get() for b in self.based_on if isinstance(b, Reference)] if isinstance(self.based_on,
                                                                                                  list) else None,
            "participant": [p.get() for p in self.participant if isinstance(p, AppointmentParticipant)] if isinstance(
                self.participant, list) else None,
            "requestedPeriod": [r.get() for r in self.requested_period if isinstance(r, Period)] if isinstance(
                self.requested_period, list) else None
        }
        return {k: v for k, v in appointment.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
