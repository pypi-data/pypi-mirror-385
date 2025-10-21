from .element import (Meta, Identifier, CodeableConcept, ContactDetail, UsageContext, RelatedArtifact,
                      Period, Timing, FHIRSubject, Quantity, Range, TriggerDefinition, Expression, DataRequirement)
from typing import Optional, List, Literal


class DynamicValue:
    def __init__(self, path: Optional[str] = None, expression: Optional[Expression] = None):
        self.path = path
        self.expression = expression

    def get(self):
        dynamic_value = {
            "path": self.path if isinstance(self.path, str) else None,
            "expression": self.expression if isinstance(self.expression, Expression) else None
        }
        return {k: v for k, v in dynamic_value.items() if v not in ("", None)}


class DefinitionTiming:
    def __init__(self, timing_date_time: Optional[str] = None, timing_age: Optional[str] = None,
                 timing_period: Optional[Period] = None, timing_duration: Optional[str] = None,
                 timing_range: Optional[Range] = None, timing_timing: Optional[Timing] = None):
        self.timing_date_time = timing_date_time
        self.timing_age = timing_age
        self.timing_period = timing_period
        self.timing_duration = timing_duration
        self.timing_range = timing_range
        self.timing_timing = timing_timing

    def get(self):
        timing = {
            "timingDateTime": self.timing_date_time if isinstance(self.timing_date_time, str) else None,
            "timingAge": self.timing_age if isinstance(self.timing_age, str) else None,
            "timingPeriod": self.timing_period.get() if isinstance(self.timing_period, Period) else None,
            "timingDuration": self.timing_duration if isinstance(self.timing_duration, str) else None,
            "timingRange": self.timing_range.get() if isinstance(self.timing_range, Range) else None,
            "timingTiming": self.timing_timing.get() if isinstance(self.timing_timing, Timing) else None
        }
        return {k: v for k, v in timing.items() if v not in ("", None)}


class DefinitionParticipant:
    def __init__(self, participant_type: Literal["patient", "practitioner", "related-person", "device"],
                 role: Optional[CodeableConcept] = None):
        self.participant_type = participant_type
        self.role = role

    def get(self):
        participant = {
            "type": self.participant_type if self.participant_type in ["patient", "practitioner", "related-person",
                                                                       "device"] else None,
            "role": self.role.get() if isinstance(self.role, CodeableConcept) else None
        }
        return {k: v for k, v in participant.items() if v not in ("", None)}
