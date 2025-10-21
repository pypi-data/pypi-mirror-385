from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, CodeableConcept, Coding, Reference, Period, Range, Quantity)
from typing import Optional, List, Literal


class EncounterHistory:

    def __init__(self,
                 status: Literal["planned", "arrived", "triaged", "in-progress", "onleave", "finished", "cancelled"],
                 period: Period):
        self.status = status
        self.period = period

    def get(self):
        history = {
            "status": self.status if self.status in ["planned", "arrived", "triaged", "in-progress", "onleave",
                                                     "finished", "cancelled"] else None,
            "period": self.period.get() if isinstance(self.period, Period) else None
        }
        return {k: v for k, v in history.items() if v not in ("", None)}


class EncounterParticipant:

    def __init__(self, paticipant_type: Optional[List[CodeableConcept]] = None, period: Optional[Period] = None,
                 individual: Optional[Reference] = None):
        self.paticipant_type = paticipant_type
        self.period = period
        self.individual = individual

    def get(self):
        participant = {
            "type": [t.get() for t in self.paticipant_type if isinstance(t, CodeableConcept)] if isinstance(
                self.paticipant_type, list) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "individual": self.individual.get() if isinstance(self.individual, Reference) else None
        }
        return {k: v for k, v in participant.items() if v not in ("", None, [])}


class EncounterDiagnosis:

    def __init__(self, condition: Reference, use: Optional[CodeableConcept] = None, rank: Optional[int] = None):
        self.condition = condition
        self.use = use
        self.rank = rank

    def get(self):
        diagnosis = {
            "condition": self.condition.get() if isinstance(self.condition, Reference) else None,
            "use": self.use.get() if isinstance(self.use, CodeableConcept) else None,
            "rank": self.rank if isinstance(self.rank, int) and self.rank > 0 else None
        }
        return {k: v for k, v in diagnosis.items() if v not in ("", None, [])}


class EncounterHospitalization:

    def __init__(self, pre_admission_identifier: Optional[Identifier], origin: Optional[Reference],
                 admit_source: Optional[CodeableConcept] = None, readmission: Optional[CodeableConcept] = None,
                 diet_preference: Optional[List[CodeableConcept]] = None,
                 special_courtesy: Optional[List[CodeableConcept]] = None,
                 special_arrangement: Optional[List[CodeableConcept]] = None,
                 destination: Optional[Reference] = None,
                 discharge_disposition: Optional[CodeableConcept] = None):
        self.pre_admission_identifier = pre_admission_identifier
        self.origin = origin
        self.admit_source = admit_source
        self.readmission = readmission
        self.diet_preference = diet_preference
        self.special_courtesy = special_courtesy
        self.special_arrangement = special_arrangement
        self.destination = destination
        self.discharge_disposition = discharge_disposition

    def get(self):
        hospitalization = {
            "preAdmissionIdentifier": self.pre_admission_identifier.get() if isinstance(self.pre_admission_identifier,
                                                                                        Identifier) else None,
            "origin": self.origin.get() if isinstance(self.origin, Reference) else None,
            "admitSource": self.admit_source.get() if isinstance(self.admit_source, CodeableConcept) else None,
            "reAdmission": self.readmission.get() if isinstance(self.readmission, CodeableConcept) else None,
            "dietPreference": [d.get() for d in self.diet_preference if isinstance(d, CodeableConcept)] if isinstance(
                self.diet_preference, list) else None,
            "specialCourtesy": [s.get() for s in self.special_courtesy if isinstance(s, CodeableConcept)] if isinstance(
                self.special_courtesy, list) else None,
            "specialArrangement": [s.get() for s in self.special_arrangement if
                                   isinstance(s, CodeableConcept)] if isinstance(self.special_arrangement,
                                                                                 list) else None,
            "destination": self.destination.get() if isinstance(self.destination, Reference) else None,
            "dischargeDisposition": self.discharge_disposition.get() if isinstance(self.discharge_disposition,
                                                                                   CodeableConcept) else None
        }
        return {k: v for k, v in hospitalization.items() if v not in ("", None, [])}


class EncounterLocation:

    def __init__(self, location: Reference,
                 status: Optional[Literal["planned", "active", "reserved", "completed"]] = None,
                 physical_type: Optional[CodeableConcept] = None, period: Optional[Period] = None):
        self.location = location
        self.status = status
        self.physical_type = physical_type
        self.period = period

    def get(self):
        location = {
            "location": self.location.get() if isinstance(self.location, Reference) else None,
            "status": self.status if self.status in ["planned", "active", "reserved", "completed"] else None,
            "physicalType": self.physical_type.get() if isinstance(self.physical_type, CodeableConcept) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None
        }
        return {k: v for k, v in location.items() if v not in ("", None)}


class Encounter(AbstractResource, ABC):

    def __init__(self,
                 status: Literal["planned", "arrived", "triaged", "in-progress", "onleave", "finished", "cancelled"],
                 encounter_class: Coding,
                 meta: Optional[Meta] = None, identifier: Optional[List[Identifier]] = None,
                 status_history: Optional[List[EncounterHistory]] = None,
                 class_history: Optional[List[EncounterHistory]] = None,
                 encounter_type: Optional[List[CodeableConcept]] = None,
                 service_type: Optional[CodeableConcept] = None, priority: Optional[CodeableConcept] = None,
                 subject: Optional[Reference] = None, episode_of_care: Optional[List[Reference]] = None,
                 based_on: Optional[List[Reference]] = None, participant: Optional[List[EncounterParticipant]] = None,
                 appointment: Optional[List[Reference]] = None, period: Optional[Period] = None,
                 length: Optional[str] = None, reason_code: Optional[List[CodeableConcept]] = None,
                 reason_reference: Optional[List[Reference]] = None,
                 diagnosis: Optional[List[EncounterDiagnosis]] = None, account: Optional[List[Reference]] = None,
                 hospitalization: Optional[EncounterHospitalization] = None,
                 location: Optional[List[EncounterLocation]] = None, service_provider: Optional[Reference] = None,
                 part_of: Optional[Reference] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Encounter"
        self.status = status
        self.encounter_class = encounter_class
        self.status_history = status_history
        self.class_history = class_history
        self.encounter_type = encounter_type
        self.service_type = service_type
        self.priority = priority
        self.subject = subject
        self.episode_of_care = episode_of_care
        self.based_on = based_on
        self.participant = participant
        self.appointment = appointment
        self.period = period
        self.length = length
        self.reason_code = reason_code
        self.reason_reference = reason_reference
        self.diagnosis = diagnosis
        self.account = account
        self.hospitalization = hospitalization
        self.location = location
        self.service_provider = service_provider
        self.part_of = part_of

    def get(self):
        encounter = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "status": self.status if self.status in ["planned", "arrived", "triaged", "in-progress", "onleave",
                                                     "finished", "cancelled"] else None,
            "statusHistory": [s.get() for s in self.status_history if isinstance(s, EncounterHistory)] if isinstance(
                self.status_history, list) else None,
            "class": self.encounter_class.get() if isinstance(self.encounter_class, Coding) else None,
            "classHistory": [c.get() for c in self.class_history if isinstance(c, EncounterHistory)] if isinstance(
                self.class_history, list) else None,
            "type": [t.get() for t in self.encounter_type if isinstance(t, CodeableConcept)] if isinstance(
                self.encounter_type, list) else None,
            "service_type": self.service_type.get() if isinstance(self.service_type, CodeableConcept) else None,
            "priority": self.priority.get() if isinstance(self.priority, CodeableConcept) else None,
            "subject": self.subject.get() if isinstance(self.subject, Reference) else None,
            "episodeOfCare": [e.get() for e in self.episode_of_care if isinstance(e, Reference)] if isinstance(
                self.episode_of_care, list) else None,
            "basedOn": [b.get() for b in self.based_on if isinstance(b, Reference)] if isinstance(self.based_on,
                                                                                                  list) else None,
            "participant": [p.get() for p in self.participant if isinstance(p, EncounterParticipant)] if isinstance(
                self.participant, list) else None,
            "appointment": [a.get() for a in self.appointment if isinstance(a, Reference)] if isinstance(
                self.appointment, list) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "length": self.length if isinstance(self.length, str) else None,
            "reasonCode": [r.get() for r in self.reason_code if isinstance(r, CodeableConcept)] if isinstance(
                self.reason_code, list) else None,
            "reasonReference": [r.get() for r in self.reason_reference if isinstance(r, Reference)] if isinstance(
                self.reason_reference, list) else None,
            "diagnosis": [d.get() for d in self.diagnosis if isinstance(d, EncounterDiagnosis)] if isinstance(
                self.diagnosis, list) else None,
            "account": [a.get() for a in self.account if isinstance(a, Reference)] if isinstance(self.account,
                                                                                                 list) else None,
            "hospitalization": self.hospitalization.get() if isinstance(self.hospitalization,
                                                                        EncounterHospitalization) else None,
            "location": [l.get() for l in self.location if isinstance(l, EncounterLocation)] if isinstance(
                self.location, list) else None,
            "serviceProvider": self.service_provider.get() if isinstance(self.service_provider, Reference) else None,
            "partOf": self.part_of.get() if isinstance(self.part_of, Reference) else None
        }
        return {k: v for k, v in encounter.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
