from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, ContactDetail, CodeableConcept, Reference,
                      Period, RelatedArtifact, Annotation)
from typing import Optional, List, Literal

ResearchStudy_Primary_Purpose_Type_Code = ["treatment", "prevention", "diagnostic", "supportive-care", "screening",
                                           "health-services-research", "basic-science", "device-feasibility"]
ResearchStudy_Phase_Code = ["n-a", "early-phase-1", "phase-1", "phase-1-phase-2", "phase-2", "phase-2-phase-3",
                            "phase-3", "phase-4"]
ResearchStudy_Reason_Stopped = ["accrual-goal-met", "closed-due-to-toxicity", "closed-due-to-lack-of-study-progress",
                                "temporarily-closed-per-study-design"]


class Arm:

    def __init__(self, name: str, arm_type: Optional[CodeableConcept] = None, description: Optional[str] = None):
        self.name = name
        self.arm_type = arm_type
        self.description = description

    def get(self):
        arm = {
            "name": self.name if isinstance(self.name, str) else None,
            "type": self.arm_type.get() if isinstance(self.arm_type, CodeableConcept) else None,
            "description": self.description if isinstance(self.description, str) else None
        }
        return {k: v for k, v in arm.items() if v not in ("", None)}


class ResearchObjective:

    def __init__(self, name: Optional[str] = None, research_objective_type: Optional[CodeableConcept] = None):
        self.name = name
        self.research_objective_type = research_objective_type

    def get(self):
        objective = {
            "name": self.name if isinstance(self.name, str) else None,
            "type": self.research_objective_type.get() if isinstance(self.research_objective_type,
                                                                     CodeableConcept) else None
        }
        return {k: v for k, v in objective.items() if v not in ("", None)}


class ResearchStudy(AbstractResource, ABC):

    def __init__(self,
                 status: Literal[
                     "active", "administratively-completed", "approved", "closed-to-accrual", "closed-to-accrual-and-intervention", "completed", "disapproved", "in-review", "temporarily-closed-to-accrual", "temporarily-closed-to-accrual-and-intervention", "withdrawn"],
                 meta: Optional[Meta] = None, identifier: Optional[List[Identifier]] = None,
                 title: Optional[str] = None, protocol: Optional[List[Reference]] = None,
                 part_of: Optional[List[Reference]] = None, primary_purpose_type: Optional[CodeableConcept] = None,
                 phase: Optional[CodeableConcept] = None, category: Optional[List[CodeableConcept]] = None,
                 focus: Optional[List[CodeableConcept]] = None, condition: Optional[List[CodeableConcept]] = None,
                 contact: Optional[List[ContactDetail]] = None,
                 related_artifact: Optional[List[RelatedArtifact]] = None,
                 keyword: Optional[List[CodeableConcept]] = None, location: Optional[List[CodeableConcept]] = None,
                 description: Optional[str] = None, enrollment: Optional[List[Reference]] = None,
                 period: Optional[Period] = None, sponsor: Optional[Reference] = None,
                 principal_investigator: Optional[Reference] = None, site: Optional[List[Reference]] = None,
                 reason_stopped: Optional[CodeableConcept] = None, note: Optional[List[Annotation]] = None,
                 arm: Optional[List[Arm]] = None, objective: Optional[List[ResearchObjective]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "ResearchStudy"
        self.title = title
        self.protocol = protocol
        self.part_of = part_of
        self.status = status
        self.primary_purpose_type = primary_purpose_type
        self.phase = phase
        self.category = category
        self.focus = focus
        self.condition = condition
        self.contact = contact
        self.related_artifact = related_artifact
        self.keyword = keyword
        self.location = location
        self.description = description
        self.enrollment = enrollment
        self.period = period
        self.sponsor = sponsor
        self.principal_investigator = principal_investigator
        self.site = site
        self.reason_stopped = reason_stopped
        self.note = note
        self.arm = arm
        self.objective = objective

    def get(self):
        researchstudy = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "title": self.title if isinstance(self.title, str) else None,
            "protocol": [p.get() for p in self.protocol if isinstance(p, Reference)] if isinstance(self.protocol,
                                                                                                   list) else None,
            "partOf": [p.get() for p in self.part_of if isinstance(p, Reference)] if isinstance(self.part_of,
                                                                                                list) else None,
            "status": self.status if self.status in [
                "active", "administratively-completed", "approved", "closed-to-accrual",
                "closed-to-accrual-and-intervention", "completed", "disapproved", "in-review",
                "temporarily-closed-to-accrual", "temporarily-closed-to-accrual-and-intervention",
                "withdrawn"] else None,
            "primaryPurposeType": self.primary_purpose_type.get() if isinstance(self.primary_purpose_type,
                                                                                CodeableConcept) else None,
            "phase": self.phase.get() if isinstance(self.phase, CodeableConcept) else None,
            "category": [c.get() for c in self.category if isinstance(c, CodeableConcept)] if isinstance(self.category,
                                                                                                         list) else None,
            "focus": [f.get() for f in self.focus if isinstance(f, CodeableConcept)] if isinstance(self.focus,
                                                                                                   list) else None,
            "condition": [c.get() for c in self.condition if isinstance(c, CodeableConcept)] if isinstance(
                self.condition, list) else None,
            "contact": [c.get() for c in self.contact if isinstance(c, ContactDetail)] if isinstance(
                self.contact,
                list) else None,
            "relatedArtifact": [a.get() for a in self.related_artifact if isinstance(a, RelatedArtifact)] if isinstance(
                self.related_artifact, list) else None,
            "keyword": [k.get() for k in self.keyword if isinstance(k, CodeableConcept)] if isinstance(self.keyword,
                                                                                                       list) else None,
            "location": [l.get() for l in self.location if isinstance(l, CodeableConcept)] if isinstance(self.location,
                                                                                                         list) else None,
            "description": self.description if isinstance(self.description, str) else None,
            "enrollment": [e.get() for e in self.enrollment if isinstance(e, Reference)] if isinstance(self.enrollment,
                                                                                                       list) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "sponsor": self.sponsor.get() if isinstance(self.sponsor, Reference) else None,
            "principalInvestigator": self.principal_investigator.get() if isinstance(self.principal_investigator,
                                                                                     Reference) else None,
            "site": [s.get() for s in self.site if isinstance(s, Reference)] if isinstance(self.site, list) else None,
            "reasonStopped": self.reason_stopped.get() if isinstance(self.reason_stopped, CodeableConcept) else None,
            "note": [n.get() for n in self.note if isinstance(n, Annotation)] if isinstance(self.note, list) else None,
            "arm": [a.get() for a in self.arm if isinstance(a, Arm)] if isinstance(self.arm, list) else None,
            "objective": [o.get() for o in self.objective if isinstance(o, ResearchObjective)] if isinstance(
                self.objective, list) else None
        }
        return {k: v for k, v in researchstudy.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
