from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, Reference, Period, CodeableConcept, Attachment)
from typing import Optional, List, Literal


class DiagnosticEffective:
    def __init__(self, effective_date_time: Optional[str] = None, effective_period: Optional[Period] = None):
        self.effective_date_time = effective_date_time
        self.effective_period = effective_period

    def get(self):
        effective = {
            "effectiveDateTime": self.effective_date_time if isinstance(self.effective_date_time, str) else None,
            "effectivePeriod": self.effective_period.get() if isinstance(self.effective_period, Period) else None
        }
        return {k: v for k, v in effective.items() if v not in ("", None)}

    def convert(self, fhir_resource):
        if fhir_resource is None:
            return None
        self.effective_date_time = fhir_resource.get("effectiveDateTime")
        self.effective_period = Period().convert(fhir_resource.get("effectivePeriod"))
        return self


class DiagnosticReportMedia:
    def __init__(self, link: Reference, comment: Optional[str] = None):
        self.link = link
        self.comment = comment

    def get(self):
        media = {
            "comment": self.comment if isinstance(self.comment, str) else None,
            "link": self.link.get() if isinstance(self.link, Reference) else None,
        }
        return {k: v for k, v in media.items() if v not in ("", None)}


class DiagnosticReport(AbstractResource, ABC):
    def __init__(self, status: Literal["registered", "partial", "preliminary", "final"],
                 code: CodeableConcept, meta: Optional[Meta] = None,
                 identifier: Optional[List[Identifier]] = None, category: Optional[List[CodeableConcept]] = None,
                 subject: Optional[Reference] = None, encounter: Optional[Reference] = None,
                 effective: Optional[DiagnosticEffective] = None, issued: Optional[str] = None,
                 performer: Optional[List[Reference]] = None, results_interpreter: Optional[List[Reference]] = None,
                 specimen: Optional[List[Reference]] = None, result: Optional[List[Reference]] = None,
                 imaging_study: Optional[List[Reference]] = None, media: List[DiagnosticReportMedia] = None,
                 conclusion: Optional[str] = None, conclusion_code: Optional[List[CodeableConcept]] = None,
                 presented_form: Optional[List[Attachment]] = None
                 ):
        super().__init__(meta, identifier)
        self._resource_type = "DiagnosticReport"
        self.status = status
        self.code = code
        self.category = category
        self.subject = subject
        self.encounter = encounter
        self.effective = effective
        self.issued = issued
        self.performer = performer
        self.results_interpreter = results_interpreter
        self.specimen = specimen
        self.result = result
        self.imaging_study = imaging_study
        self.media = media
        self.conclusion = conclusion
        self.conclusion_code = conclusion_code
        self.presented_form = presented_form

    def get(self):
        diagnostic_report = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "status": self.status if self.status in ["registered", "partial", "preliminary", "final"] else None,
            "code": self.code.get() if isinstance(self.code, CodeableConcept) else None,
            "category": [c.get() for c in self.category if isinstance(c, CodeableConcept)] if isinstance(self.category,
                                                                                                         list) else None,
            "subject": self.subject.get() if isinstance(self.subject, Reference) else None,
            "encounter": self.encounter if isinstance(self.encounter, Reference) else None,
            "effectiveDateTime": self.effective.get().get("effectiveDateTime") if isinstance(self.effective,
                                                                                             DiagnosticEffective) else None,
            "effectivePeriod": self.effective.get().get("effectivePeriod") if isinstance(self.effective,
                                                                                         DiagnosticEffective) else None,
            "issued": self.issued if isinstance(self.issued, str) else None,
            "performer": [p.get() for p in self.performer if isinstance(p, Reference)] if isinstance(self.performer,
                                                                                                     list) else None,
            "specimen": [s.get() for s in self.specimen if isinstance(s, Reference)] if isinstance(self.specimen,
                                                                                                   list) else None,
            "result": [r.get() for r in self.result if isinstance(r, Reference)] if isinstance(self.result,
                                                                                               list) else None,
            "imagingStudy": [i.get() for i in self.imaging_study if isinstance(i, Reference)] if isinstance(
                self.imaging_study, list) else None,
            "media": [m.get() for m in self.media if isinstance(m, DiagnosticReportMedia)] if isinstance(self.media,
                                                                                                         list) else None,
            "conclusion": self.conclusion if isinstance(self.conclusion, str) else None,
            "conclusionCode": [c.get() for c in self.conclusion_code if isinstance(c, CodeableConcept)] if isinstance(
                self.conclusion_code, list) else None,
            "presentedForm": [p.get() for p in self.presented_form if isinstance(p, Attachment)] if isinstance(
                self.presented_form, list) else None
        }
        return {k: v for k, v in diagnostic_report.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass
