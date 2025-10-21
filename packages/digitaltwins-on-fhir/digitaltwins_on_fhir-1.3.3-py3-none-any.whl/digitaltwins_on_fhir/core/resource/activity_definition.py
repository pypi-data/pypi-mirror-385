from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, CodeableConcept, Code, ContactDetail, UsageContext, RelatedArtifact,
                      Period, FHIRSubject, Reference, Dosage)
from .definition import (DynamicValue, DefinitionTiming, DefinitionParticipant)
from typing import Optional, List, Literal


class ActivityDefinitionProduct:
    def __init__(self, product_reference: Optional[Reference], product_codeable_concept: Optional[CodeableConcept]):
        self.product_reference = product_reference
        self.product_codeable_concept = product_codeable_concept

    def get(self):
        product = {
            "productReference": self.product_reference.get() if isinstance(self.product_reference, Reference) else None,
            "productCodeableConcept": self.product_codeable_concept.get() if isinstance(self.product_codeable_concept,
                                                                                        CodeableConcept) else None,
        }
        return {k: v for k, v in product.items() if v not in ("", None, [])}


class ActivityDefinition(AbstractResource, ABC):

    def __init__(self, status: Literal["draft", "active", "retired", "unknown"], meta: Optional[Meta] = None,
                 identifier: Optional[List[Identifier]] = None,
                 url: Optional[str] = None, version: Optional[str] = None, name: Optional[str] = None,
                 title: Optional[str] = None, subtitle: Optional[str] = None, experimental: Optional[bool] = None,
                 subject: Optional[FHIRSubject] = None, date: Optional[str] = None, publisher: Optional[str] = None,
                 contact: Optional[List[ContactDetail]] = None, description: Optional[str] = None,
                 use_context: Optional[List[UsageContext]] = None,
                 jurisdiction: Optional[List[CodeableConcept]] = None, purpose: Optional[str] = None,
                 usage: Optional[str] = None, copyright: Optional[str] = None, approval_date: Optional[str] = None,
                 last_review_date: Optional[str] = None, effective_period: Optional[Period] = None,
                 topic: Optional[List[CodeableConcept]] = None, author: Optional[List[ContactDetail]] = None,
                 editor: Optional[List[ContactDetail]] = None, reviewer: Optional[List[ContactDetail]] = None,
                 endorser: Optional[List[ContactDetail]] = None,
                 related_artifact: Optional[List[RelatedArtifact]] = None, library: Optional[List[str]] = None,
                 kind: Optional[Code] = None,
                 intent: Optional[Literal[
                     "proposal", "plan", "directive", "order", "original-order", "reflex-order", "filler-order", "instance-order", "option"]] = None,
                 priority: Optional[Literal["routine", "urgent", "asap", "stat"]] = None,
                 do_not_perform: Optional[bool] = None,
                 timing: Optional[DefinitionTiming] = None, location: Optional[Reference] = None,
                 participant: Optional[List[DefinitionParticipant]] = None,
                 product: Optional[ActivityDefinitionProduct] = None, quantity: Optional[str] = None,
                 dosage: Optional[List[Dosage]] = None,
                 body_site: Optional[List[CodeableConcept]] = None,
                 specimen_requirement: Optional[List[Reference]] = None,
                 observation_requirement: Optional[List[Reference]] = None,
                 observation_result_requirement: Optional[List[Reference]] = None,
                 transform: Optional[str] = None, dynamic_value: Optional[List[DynamicValue]] = None,
                 ):
        super().__init__(meta, identifier)
        self._resource_type = "ActivityDefinition"
        self.url = url
        self.version = version
        self.name = name
        self.title = title
        self.subtitle = subtitle
        self.status = status
        self.experimental = experimental
        self.subject = subject
        self.date = date
        self.publisher = publisher
        self.contact = contact
        self.description = description
        self.use_context = use_context
        self.jurisdiction = jurisdiction
        self.purpose = purpose
        self.usage = usage
        self.copyright = copyright
        self.approval_date = approval_date
        self.last_review_date = last_review_date
        self.effective_period = effective_period
        self.topic = topic
        self.author = author
        self.editor = editor
        self.reviewer = reviewer
        self.endorser = endorser
        self.related_artifact = related_artifact
        self.library = library
        self.kind = kind
        self.intent = intent
        self.priority = priority
        self.do_not_perform = do_not_perform
        self.timing = timing
        self.location = location
        self.participant = participant
        self.product = product
        self.quantity = quantity
        self.dosage = dosage
        self.body_site = body_site
        self.specimen_requirement = specimen_requirement
        self.observation_requirement = observation_requirement
        self.observation_result_requirement = observation_result_requirement
        self.transform = transform
        self.dynamic_value = dynamic_value

    def get(self):
        activity_definition = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "url": self.url if isinstance(self.url, str) else None,
            "version": self.version if isinstance(self.version, str) else None,
            "name": self.name if isinstance(self.name, str) else None,
            "title": self.title if isinstance(self.title, str) else None,
            "subtitle": self.subtitle if isinstance(self.subtitle, str) else None,
            "status": self.status if self.status in ["draft", "active", "retired", "unknown"] else None,
            "experimental": self.experimental if isinstance(self.experimental, bool) else None,
            "subjectCodeableConcept": self.subject.get().get("subjectCodeableConcept") if isinstance(self.subject,
                                                                                                     FHIRSubject) else None,
            "subjectReference": self.subject.get().get("subjectReference") if isinstance(self.subject,
                                                                                         FHIRSubject) else None,
            "date": self.date if isinstance(self.date, str) else None,
            "publisher": self.publisher if isinstance(self.publisher, str) else None,
            "contact": [c.get() for c in self.contact if isinstance(c, ContactDetail)] if isinstance(self.contact,
                                                                                                     list) else None,
            "description": self.description if isinstance(self.description, str) else None,
            "useContext": [u.get() for u in self.use_context if isinstance(u, UsageContext)] if isinstance(
                self.use_context, list) else None,
            "jurisdiction": [j.get() for j in self.jurisdiction if isinstance(j, CodeableConcept)] if isinstance(
                self.jurisdiction, list) else None,
            "purpose": self.purpose if isinstance(self.purpose, str) else None,
            "usage": self.usage if isinstance(self.usage, str) else None,
            "copyright": self.copyright if isinstance(self.copyright, str) else None,
            "approvalDate": self.approval_date if isinstance(self.approval_date, str) else None,
            "lastReviewDate": self.last_review_date if isinstance(self.last_review_date, str) else None,
            "effectivePeriod": self.effective_period.get() if isinstance(self.effective_period, Period) else None,
            "topic": [t.get() for t in self.topic if isinstance(t, CodeableConcept)] if isinstance(self.topic,
                                                                                                   list) else None,
            "author": [a.get() for a in self.author if isinstance(a, ContactDetail)] if isinstance(self.author,
                                                                                                   list) else None,
            "editor": [e.get() for e in self.editor if isinstance(e, ContactDetail)] if isinstance(self.editor,
                                                                                                   list) else None,
            "reviewer": [r.get() for r in self.reviewer if isinstance(r, ContactDetail)] if isinstance(self.reviewer,
                                                                                                       list) else None,
            "endorser": [e.get() for e in self.endorser if isinstance(e, ContactDetail)] if isinstance(self.endorser,
                                                                                                       list) else None,
            "relatedArtifact": [r.get() for r in self.related_artifact if isinstance(r, RelatedArtifact)] if isinstance(
                self.related_artifact, list) else None,
            "library": [l for l in self.library if isinstance(l, str)] if isinstance(self.library, list) else None,
            "kind": self.kind.get() if isinstance(self.kind, Code) else None,
            "intent": self.intent if self.intent in [
                "proposal", "plan", "directive", "order", "original-order", "reflex-order", "filler-order",
                "instance-order", "option"] else None,
            "priority": self.priority if self.priority in ["routine", "urgent", "asap", "stat"] else None,
            "doNotPerform": self.do_not_perform if isinstance(self.do_not_perform, bool) else None,
            "timingDateTime": self.timing.get().get("timingDateTime") if isinstance(self.timing,
                                                                                    DefinitionTiming) else None,
            "timingAge": self.timing.get().get("timingAge") if isinstance(self.timing,
                                                                          DefinitionTiming) else None,
            "timingPeriod": self.timing.get().get("timingPeriod") if isinstance(self.timing,
                                                                                DefinitionTiming) else None,
            "timingDuration": self.timing.get().get("timingDuration") if isinstance(self.timing,
                                                                                    DefinitionTiming) else None,
            "timingRange": self.timing.get().get("timingRange") if isinstance(self.timing,
                                                                              DefinitionTiming) else None,
            "timingTiming": self.timing.get().get("timingTiming") if isinstance(self.timing,
                                                                                DefinitionTiming) else None,
            "location": self.location.get() if isinstance(self.location, Reference) else None,
            "participant": [p.get() for p in self.participant if
                            isinstance(p, DefinitionParticipant)] if isinstance(self.participant,
                                                                                list) else None,
            "quantity": self.quantity if isinstance(self.quantity, str) else None,
            "dosage": [d.get() for d in self.dosage if isinstance(d, Dosage)] if isinstance(self.dosage,
                                                                                            list) else None,
            "bodySite": [b.get() for b in self.body_site if isinstance(b, CodeableConcept)] if isinstance(
                self.body_site, list) else None,
            "specimenRequirement": [s.get() for s in self.specimen_requirement if
                                    isinstance(s, Reference)] if isinstance(self.specimen_requirement, list) else None,
            "observationRequirement": [o.get() for o in self.observation_requirement if
                                       isinstance(o, Reference)] if isinstance(self.observation_requirement,
                                                                               list) else None,
            "observationResultRequirement": [o.get() for o in self.observation_result_requirement if
                                             isinstance(o, Reference)] if isinstance(
                self.observation_result_requirement, list) else None,
            "transform": self.transform if isinstance(self.transform, str) else None,
            "dynamicValue": [d.get() for d in self.dynamic_value if isinstance(d, DynamicValue)] if isinstance(
                self.dynamic_value, list) else None
        }
        return {k: v for k, v in activity_definition.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
