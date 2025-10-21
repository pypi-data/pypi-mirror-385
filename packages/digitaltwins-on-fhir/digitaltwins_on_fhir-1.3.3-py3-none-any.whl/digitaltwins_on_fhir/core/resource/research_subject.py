from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, Reference, Period)
from typing import Optional, List, Literal


class ResearchSubject(AbstractResource, ABC):
    def __init__(self, status: Literal[
        "candidate", "eligible", "follow-up", "ineligible", "not-registered", "off-study", "on-study",
        "on-study-intervention", "on-study-observation", "pending-on-study", "potential-candidate", "screening",
        "withdrawn"], individual: Reference, study: Optional[Reference] = None, meta: Optional[Meta] = None,
                 identifier: Optional[List[Identifier]] = None, period: Optional[Period] = None,
                 assigned_arm: Optional[str] = None, actual_arm: Optional[str] = None,
                 consent: Optional[Reference] = None):
        super().__init__(meta, identifier)
        self._resource_type = "ResearchSubject"
        self.status = status
        self.period = period
        self.study = study
        self.individual = individual
        self.assigned_arm = assigned_arm
        self.actual_arm = actual_arm
        self.consent = consent

    def get(self):
        research_subject = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "status": self.status if self.status in [
                "candidate", "eligible", "follow-up", "ineligible", "not-registered", "off-study", "on-study",
                "on-study-intervention", "on-study-observation", "pending-on-study", "potential-candidate", "screening",
                "withdrawn"] else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "study": self.study.get() if isinstance(self.study, Reference) else None,
            "individual": self.individual.get() if isinstance(self.individual, Reference) else None,
            "assignedArm": self.assigned_arm if isinstance(self.assigned_arm, str) else None,
            "actualArm": self.actual_arm if isinstance(self.actual_arm, str) else None,
            "consent": self.consent.get() if isinstance(self.consent, Reference) else None
        }
        return {k: v for k, v in research_subject.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
