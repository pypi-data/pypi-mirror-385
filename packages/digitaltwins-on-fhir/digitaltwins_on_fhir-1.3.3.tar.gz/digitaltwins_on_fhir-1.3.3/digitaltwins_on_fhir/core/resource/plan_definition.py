from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, CodeableConcept, ContactDetail, UsageContext, RelatedArtifact,
                      Period, FHIRSubject, Quantity, Range, TriggerDefinition, Expression, DataRequirement)
from .definition import (DynamicValue, DefinitionTiming, DefinitionParticipant)
from typing import Optional, List, Literal


class PlanDefinitionTargetDetail:
    def __init__(self, detail_quantity: Optional[Quantity] = None, detail_range: Optional[Range] = None,
                 detail_codeable_concept: Optional[CodeableConcept] = None):
        self.detail_quantity = detail_quantity
        self.detail_range = detail_range
        self.detail_codeable_concept = detail_codeable_concept

    def get(self):
        detail = {
            "detailQuantity": self.detail_quantity.get() if isinstance(self.detail_quantity, Quantity) else None,
            "detailRange": self.detail_range.get() if isinstance(self.detail_range, Range) else None,
            "detailCodeableConcept": self.detail_codeable_concept.get() if isinstance(self.detail_codeable_concept,
                                                                                      CodeableConcept) else None
        }
        return {k: v for k, v in detail.items() if v not in ("", None)}


class PlanDefinitionTarget:

    def __init__(self, measure: Optional[CodeableConcept] = None, detail: Optional[PlanDefinitionTargetDetail] = None,
                 due: Optional[str] = None):
        self.measure = measure
        self.detail = detail
        self.due = due

    def get(self):
        target = {
            "measure": self.measure.get() if isinstance(self.measure, CodeableConcept) else None,
            "detailQuantity": self.detail.get().get("detailQuantity") if isinstance(self.detail,
                                                                                    PlanDefinitionTargetDetail) else None,
            "detailRange": self.detail.get().get("detailRange") if isinstance(self.detail,
                                                                              PlanDefinitionTargetDetail) else None,
            "detailCodeableConcept": self.detail.get().get("detailCodeableConcept") if isinstance(self.detail,
                                                                                                  PlanDefinitionTargetDetail) else None,
            "due": self.due if isinstance(self.due, str) else None
        }
        return {k: v for k, v in target.items() if v not in ("", None)}


class PlanDefinitionGoal:

    def __init__(self, description: CodeableConcept, category: Optional[CodeableConcept] = None,
                 priority: Optional[CodeableConcept] = None, start: Optional[CodeableConcept] = None,
                 addresses: Optional[List[CodeableConcept]] = None,
                 documentation: Optional[List[RelatedArtifact]] = None,
                 target: Optional[List[PlanDefinitionTarget]] = None):
        self.description = description
        self.category = category
        self.priority = priority
        self.start = start
        self.addresses = addresses
        self.documentation = documentation
        self.target = target

    def get(self):
        goal = {
            "category": self.category.get() if isinstance(self.category, CodeableConcept) else None,
            "description": self.description.get() if isinstance(self.description, CodeableConcept) else None,
            "priority": self.priority.get() if isinstance(self.priority, CodeableConcept) else None,
            "start": self.start.get() if isinstance(self.start, CodeableConcept) else None,
            "addresses": [a.get() for a in self.addresses if isinstance(a, CodeableConcept)] if isinstance(
                self.addresses, list) else None,
            "documentation": [d.get() for d in self.documentation if isinstance(d, RelatedArtifact)] if isinstance(
                self.documentation, list) else None,
            "target": [t.get() for t in self.target if isinstance(t, PlanDefinitionTarget)] if isinstance(self.target,
                                                                                                          list) else None
        }
        return {k: v for k, v in goal.items() if v not in ("", None, [])}


class PlanDefinitionActionCondition:

    def __init__(self, kind: Literal["applicability", "start", "stop"], expression: Optional[Expression] = None):
        self.kind = kind
        self.expression = expression

    def get(self):
        condition = {
            "kind": self.kind if self.kind in ["applicability", "start", "stop"] else None,
            "expression": self.expression.get() if isinstance(self.expression, Expression) else None
        }
        return {k: v for k, v in condition.items() if v not in ("", None)}


class PlanDefinitionActionRelatedActionOffset:

    def __init__(self, offset_duration: Optional[str] = None, offset_range: Optional[Range] = None):
        self.offset_duration = offset_duration
        self.offset_range = offset_range

    def get(self):
        offset = {
            "offsetDuration": self.offset_duration if isinstance(self.offset_duration, str) else None,
            "offsetRange": self.offset_range.get() if isinstance(self.offset_range, Range) else None
        }
        return {k: v for k, v in offset.items() if v not in ("", None)}


class PlanDefinitionActionRelatedAction:

    def __init__(self, action_id: Optional[str], relationship: Literal[
        "before-start", "before", "before-end", "concurrent-with-start", "concurrent", "concurrent-with-end", "after-start", "after", "after-end"],
                 offset: Optional[PlanDefinitionActionRelatedActionOffset] = None):
        self.action_id = action_id
        self.relationship = relationship
        self.offset = offset

    def get(self):
        related_action = {
            "actionId": self.action_id if isinstance(self.action_id, str) else None,
            "relationship": self.relationship if self.relationship in [
                "before-start", "before", "before-end", "concurrent-with-start", "concurrent", "concurrent-with-end",
                "after-start", "after", "after-end"] else None,
            "offsetDuration": self.offset.get().get("offsetDuration") if isinstance(self.offset,
                                                                                    PlanDefinitionActionRelatedActionOffset) else None,
            "offsetRange": self.offset.get().get("offsetRange") if isinstance(self.offset,
                                                                              PlanDefinitionActionRelatedActionOffset) else None
        }
        return {k: v for k, v in related_action.items() if v not in ("", None)}


class PlanDefinitionActionDefinition:
    def __init__(self, definition_canonical: Optional[str] = None, definition_uri: Optional[str] = None):
        self.definition_canonical = definition_canonical
        self.definition_uri = definition_uri

    def get(self):
        definition = {
            "definitionCanonical": self.definition_canonical if isinstance(self.definition_canonical, str) else None,
            "definitionUri": self.definition_uri if isinstance(self.definition_uri, str) else None
        }
        return {k: v for k, v in definition.items() if v not in ("", None)}


class PlanDefinitionAction:
    def __init__(self, prefix: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None,
                 text_equivalent: Optional[str] = None,
                 priority: Optional[Literal["routine", "urgent", "asap", "stat"]] = None,
                 code: Optional[List[CodeableConcept]] = None, reason: Optional[List[CodeableConcept]] = None,
                 documentation: Optional[List[RelatedArtifact]] = None, goal_id: Optional[List[str]] = None,
                 subject: Optional[FHIRSubject] = None, trigger: Optional[List[TriggerDefinition]] = None,
                 condition: Optional[List[PlanDefinitionActionCondition]] = None,
                 input: Optional[List[DataRequirement]] = None, output: Optional[List[DataRequirement]] = None,
                 related_action: Optional[List[PlanDefinitionActionRelatedAction]] = None,
                 timing: Optional[DefinitionTiming] = None,
                 participant: Optional[List[DefinitionParticipant]] = None,
                 action_type: Optional[CodeableConcept] = None,
                 grouping_behavior: Optional[Literal["visual-group", "logical-group", "sentence-group"]] = None,
                 selection_behavior: Optional[
                     Literal["any", "all", "all-or-none", "exactly-one", "at-most-one", "one-or-more"]] = None,
                 required_behavior: Optional[Literal["must", "could", "must-unless-documented"]] = None,
                 precheck_behavior: Optional[Literal["yes", "no"]] = None,
                 cardinality_behavior: Optional[Literal["single", "multiple"]] = None,
                 definition: Optional[PlanDefinitionActionDefinition] = None, transform: Optional[str] = None,
                 dynamic_value: Optional[List[DynamicValue]] = None,
                 action: Optional = None):
        self.prefix = prefix
        self.title = title
        self.description = description
        self.text_equivalent = text_equivalent
        self.priority = priority
        self.code = code
        self.reason = reason
        self.documentation = documentation
        self.goal_id = goal_id
        self.subject = subject
        self.trigger = trigger
        self.condition = condition
        self.input = input
        self.output = output
        self.related_action = related_action
        self.timing = timing
        self.participant = participant
        self.action_type = action_type
        self.grouping_behavior = grouping_behavior
        self.selection_behavior = selection_behavior
        self.required_behavior = required_behavior
        self.precheck_behavior = precheck_behavior
        self.cardinality_behavior = cardinality_behavior
        self.definition = definition
        self.transform = transform
        self.dynamic_value = dynamic_value
        self.action = action

    def get(self):
        action = {
            "prefix": self.prefix if isinstance(self.prefix, str) else None,
            "title": self.title if isinstance(self.title, str) else None,
            "description": self.description if isinstance(self.description, str) else None,
            "textEquivalent": self.text_equivalent if isinstance(self.text_equivalent, str) else None,
            "priority": self.priority if self.priority in ["routine", "urgent", "asap", "stat"] else None,
            "code": [c.get() for c in self.code if isinstance(c, CodeableConcept)] if isinstance(self.code,
                                                                                                 list) else None,
            "reason": [r.get() for r in self.reason if isinstance(r, CodeableConcept)] if isinstance(self.reason,
                                                                                                     list) else None,
            "documentation": [d.get() for d in self.documentation if isinstance(d, RelatedArtifact)] if isinstance(
                self.documentation, list) else None,
            "goalId": [g for g in self.goal_id if isinstance(g, str)] if isinstance(
                self.goal_id, list) else None,
            "subjectCodeableConcept": self.subject.get().get("subjectCodeableConcept") if isinstance(self.subject,
                                                                                                     FHIRSubject) else None,
            "subjectReference": self.subject.get().get("subjectReference") if isinstance(self.subject,
                                                                                         FHIRSubject) else None,
            "trigger": [t.get() for t in self.trigger if isinstance(t, TriggerDefinition)] if isinstance(self.trigger,
                                                                                                         list) else None,
            "condition": [c.get() for c in self.condition if
                          isinstance(c, PlanDefinitionActionCondition)] if isinstance(self.condition, list) else None,
            "input": [i.get() for i in self.input if
                      isinstance(i, DataRequirement)] if isinstance(self.input, list) else None,
            "output": [o.get() for o in self.output if
                       isinstance(o, DataRequirement)] if isinstance(self.output, list) else None,
            "relatedAction": [r.get() for r in self.related_action if
                              isinstance(r, PlanDefinitionActionRelatedAction)] if isinstance(self.related_action,
                                                                                              list) else None,
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
            "participant": [p.get() for p in self.participant if
                            isinstance(p, DefinitionParticipant)] if isinstance(self.participant,
                                                                                          list) else None,
            "type": self.action_type.get() if isinstance(self.action_type, CodeableConcept) else None,
            "groupingBehavior": self.grouping_behavior if self.grouping_behavior in ["visual-group", "logical-group",
                                                                                     "sentence-group"] else None,
            "selectionBehavior": self.selection_behavior if self.selection_behavior in ["any", "all", "all-or-none",
                                                                                        "exactly-one", "at-most-one",
                                                                                        "one-or-more"] else None,
            "requiredBehavior": self.required_behavior if self.required_behavior in ["must", "could",
                                                                                     "must-unless-documented"] else None,
            "precheckBehavior": self.precheck_behavior if self.precheck_behavior in ["yes", "no"] else None,
            "cardinalityBehavior": self.cardinality_behavior if self.cardinality_behavior in ["single",
                                                                                              "multiple"] else None,
            "definitionCanonical": self.definition.get().get("definitionCanonical") if isinstance(self.definition,
                                                                                                  PlanDefinitionActionDefinition) else None,
            "definitionUri": self.definition.get().get("definitionUri") if isinstance(self.definition,
                                                                                      PlanDefinitionActionDefinition) else None,
            "transform": self.transform if isinstance(self.transform, str) else None,
            "dynamicValue": [d.get() for d in self.dynamic_value if
                             isinstance(d, DynamicValue)] if isinstance(self.dynamic_value,
                                                                        list) else None,
            "action": self.action.get() if isinstance(self.action, PlanDefinitionAction) else None
        }
        return {k: v for k, v in action.items() if v not in ("", None, [])}


class PlanDefinition(AbstractResource, ABC):

    def __init__(self, status: Literal["draft", "active", "retired", "unknown"], meta: Optional[Meta] = None,
                 identifier: Optional[List[Identifier]] = None,
                 url: Optional[str] = None, version: Optional[str] = None, name: Optional[str] = None,
                 title: Optional[str] = None, subtitle: Optional[str] = None,
                 plan_definition_type: Optional[CodeableConcept] = None, experimental: Optional[bool] = None,
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
                 goal: Optional[List[PlanDefinitionGoal]] = None, action: Optional[List[PlanDefinitionAction]] = None):
        super().__init__(meta, identifier)
        self._resource_type = "PlanDefinition"
        self.url = url
        self.version = version
        self.name = name
        self.title = title
        self.subtitle = subtitle
        self.plan_definition_type = plan_definition_type
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
        self.goal = goal
        self.action = action

    def get(self):
        plan_definition = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "url": self.url if isinstance(self.url, str) else None,
            "version": self.version if isinstance(self.version, str) else None,
            "name": self.name if isinstance(self.name, str) else None,
            "title": self.title if isinstance(self.title, str) else None,
            "subtitle": self.subtitle if isinstance(self.subtitle, str) else None,
            "type": self.plan_definition_type.get() if isinstance(self.plan_definition_type, CodeableConcept) else None,
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
            "goal": [g.get() for g in self.goal if isinstance(g, PlanDefinitionGoal)] if isinstance(self.goal,
                                                                                                    list) else None,
            "action": [a.get() for a in self.action if isinstance(a, PlanDefinitionAction)] if isinstance(self.action,
                                                                                                          list) else None
        }
        return {k: v for k, v in plan_definition.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
