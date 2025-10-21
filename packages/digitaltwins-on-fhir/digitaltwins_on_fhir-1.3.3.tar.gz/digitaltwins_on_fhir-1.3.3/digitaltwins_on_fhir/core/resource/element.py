from typing import List, Optional, Literal, Union
from ..utils import transform_value


class Code:
    def __init__(self, value: str = ""):
        self.value = value if isinstance(value, str) else None

    def get(self):
        return self.value if isinstance(self.value, str) else None

    def convert(self, fhirpy_code):
        self.value = fhirpy_code
        return self


class Coding:

    def __init__(self, system: str = "", version: str = "", code: Code = None, display: str = "",
                 user_selected: bool = ""):
        self.system = system
        self.version = version
        self.code = code
        self.display = display
        self.user_selected = user_selected

    def get(self):
        coding = {
            "system": self.system if isinstance(self.system, str) else None,
            "version": self.version if isinstance(self.version, str) else None,
            "code": self.code.get() if isinstance(self.code, Code) else None,
            "display": self.display if isinstance(self.display, str) else None,
            "userSelected": self.user_selected if isinstance(self.user_selected, bool) else None
        }
        return {k: v for k, v in coding.items() if v not in ("", None)}

    def convert(self, fhirpy_coding):
        if fhirpy_coding is None:
            return None
        self.system = fhirpy_coding.get("system")
        self.version = fhirpy_coding.get("version")
        self.code = Code().convert(fhirpy_coding.get("code"))
        self.display = fhirpy_coding.get("display")
        self.user_selected = fhirpy_coding.get("userSelected")
        return self


class CodeableConcept:

    def __init__(self, codings: List[Coding] = None, text: str = ""):
        self.codings = codings
        self.text = text

    def get(self):
        codeableconcept = {
            "coding": [coding.get() for coding in self.codings if isinstance(coding, Coding)] if isinstance(
                self.codings, list) else None,
            "text": self.text if isinstance(self.text, str) else None
        }

        return {k: v for k, v in codeableconcept.items() if v not in ("", None, [])}

    def set(self, codings: List = None, text: str = ""):
        self.codings = [Coding(system=c.get("system"), code=Code(value=c.get("code")), display=c.get("display", "")) for
                        c in codings] if codings is not None else None
        self.text = text

    def convert(self, fhirpy_codeable):
        if fhirpy_codeable is None:
            return None
        self.codings = [Coding().convert(c) for c in fhirpy_codeable.get("coding", []) if c is not None] or None
        self.text = fhirpy_codeable.get("text")
        return self


class Period:

    def __init__(self, start: str = '', end: str = ''):
        self.start = start
        self.end = end

    def get(self):
        period = {
            "start": self.start if isinstance(self.start, str) else None,
            "end": self.end if isinstance(self.end, str) else None
        }
        return {k: v for k, v in period.items() if v not in ("", None)}

    def convert(self, fhirpy_period):
        if fhirpy_period is None:
            return None
        self.start = fhirpy_period.get("start")
        self.end = fhirpy_period.get("end")
        return self


class Reference:

    def __init__(self, reference: str = "", display: str = ""):
        self.reference = reference
        self.display = display

    def get(self):
        reference = {
            "reference": self.reference if isinstance(self.reference, str) else None,
            "display": self.display if isinstance(self.display, str) else None
        }
        return {k: v for k, v in reference.items() if v not in ("", None)}

    def convert(self, fhirpy_reference):
        if fhirpy_reference is None:
            return None
        self.reference = fhirpy_reference.get("reference")
        self.display = fhirpy_reference.get("display")
        return self


class Identifier:

    def __init__(self, use: Code = None, system: str = "", value: str = "", period: Period = None,
                 assigner: Reference = None):
        self.use = use
        self.system = system
        self.value = value
        self.period = period if isinstance(period, Period) else None
        self.assigner = assigner if isinstance(assigner, Reference) else None

    def get(self):
        identifier = {
            "use": self.use.get() if isinstance(self.use, Code) and self.use.get() in ["usual", "official", "temp",
                                                                                       "secondary", "old"] else None,
            "system": self.system if isinstance(self.system, str) else None,
            "value": self.value if isinstance(self.value, str) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "assigner": self.assigner.get() if isinstance(self.assigner, Reference) else None
        }

        return {k: v for k, v in identifier.items() if v not in ("", None)}

    def convert(self, fhirpy_identifier):
        if fhirpy_identifier is None:
            return None
        self.use = fhirpy_identifier.get("use")
        self.system = fhirpy_identifier.get("system")
        self.value = fhirpy_identifier.get("value")
        self.period = Period().convert(fhirpy_identifier.get("period"))
        self.assigner = Reference().convert(fhirpy_identifier.get("assigner"))
        return self


class Profile:

    def __init__(self, url):
        self.url = url if isinstance(url, str) else None

    def get(self):
        return self.url


class Meta:

    def __init__(self, version_id: str = "", last_updated: str = "", source: str = "", profile: List[Profile] = None):
        self.version_id = version_id
        self.last_updated = last_updated
        self.source = source
        self.profile = profile

    def get(self):
        meta = {
            "versionId": self.version_id if isinstance(self.version_id, str) else None,
            "lastUpdated": self.last_updated if isinstance(self.last_updated, str) else None,
            "source": self.source if isinstance(self.source, str) else None,
            "profile": [p for p in self.profile if isinstance(p, Profile)] if isinstance(self.profile, list) else None
        }
        return {k: v for k, v in meta.items() if v not in ("", None, [])}

    def convert(self, fhirpy_meta):
        if fhirpy_meta is None:
            return None
        self.version_id = fhirpy_meta.get("versionId")
        self.last_updated = fhirpy_meta.get("lastUpdated")
        self.source = fhirpy_meta.get("source")
        self.profile = [Profile(url=p) for p in fhirpy_meta.get("profile", []) if p is not None] or None
        return self


class HumanName:

    def __init__(self, use: Literal["usual", "official", "temp", "nickname", "anonymous", "old", "maiden", ""] = "",
                 text: str = "", family: str = "", given: List[str] = None,
                 prefix: List[str] = None, suffix: List[str] = None, period: Optional[Period] = None):
        self.use = use
        self.text = text
        self.family = family
        self.given = given
        self.prefix = prefix
        self.suffix = suffix
        self.period = period

    def get(self):
        name = {
            "use": self.use if self.use in ["usual", "official", "temp", "nickname", "anonymous", "old",
                                            "maiden"] else None,
            "text": self.text if isinstance(self.text, str) else None,
            "family": self.family if isinstance(self.family, str) else None,
            "given": [g for g in self.given if isinstance(g, str)] if isinstance(self.given, list) else None,
            "prefix": [p for p in self.prefix if isinstance(p, str)] if isinstance(self.prefix, list) else None,
            "suffix": [s for s in self.suffix if isinstance(s, str)] if isinstance(self.suffix, list) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None
        }
        return {k: v for k, v in name.items() if v not in ("", None, [])}


class ContactPoint:

    def __init__(self, system: Literal["phone", "fax", "email", "pager", "url", "sms", "other", ""] = "",
                 value: str = "", use: Literal["home", "work", "temp", "old", "mobile", ""] = "",
                 rank: Optional[int] = None,
                 period: Optional[Period] = None):
        self.system = system
        self.value = value
        self.use = use
        self.rank = rank
        self.period = period

    def get(self):
        contactpoint = {
            "system": self.system if self.system in ["phone", "fax", "email", "pager", "url", "sms", "other"] else None,
            "value": self.value if isinstance(self.value, str) else None,
            "use": self.use if self.use in ["home", "work", "temp", "old", "mobile"] else None,
            "rank": self.rank if isinstance(self.rank, int) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None
        }
        return {k: v for k, v in contactpoint.items() if v not in ("", None)}


class ContactDetail:

    def __init__(self, name: Optional[str] = None, telecom: Optional[List[ContactPoint]] = None):
        self.name = name
        self.telecom = telecom

    def get(self):
        contactdetail = {
            "name": self.name if isinstance(self.name, str) else None,
            "telecom": [t.get() for t in self.telecom if isinstance(t, ContactPoint)] if isinstance(self.telecom,
                                                                                                    list) else None
        }
        return {k: v for k, v in contactdetail.items() if v not in ("", None, [])}


class Address:

    def __init__(self, use: Literal["home", "work", "temp", "old", "billing", ""] = "", text: str = "",
                 line: List[str] = None, city: str = "", district: str = "", state: str = "", postal_code: str = "",
                 country: str = "", period: Optional[Period] = None):
        self.use = use
        self.text = text
        self.line = line
        self.city = city
        self.district = district
        self.state = state
        self.postal_code = postal_code
        self.country = country
        self.period = period

    def get(self):
        address = {
            "use": self.use if self.use in ["home", "work", "temp", "old", "billing"] else None,
            "text": self.text if isinstance(self.text, str) else None,
            "line": [l for l in self.line if isinstance(l, str)] if isinstance(self.line, list) else None,
            "city": self.city if isinstance(self.city, str) else None,
            "district": self.district if isinstance(self.district, str) else None,
            "state": self.state if isinstance(self.state, str) else None,
            "postalCode": self.postal_code if isinstance(self.postal_code, str) else None,
            "country": self.country if isinstance(self.country, str) else None,
            "period": self.period.get() if isinstance(self.period, Period) else None
        }

        return {k: v for k, v in address.items() if v not in ("", None, [])}


class Attachment:

    def __init__(self, content_type: Optional[Code] = None, language: Optional[Code] = None, data: str = "",
                 url: str = "", size: Optional[int] = None, hash: str = "", title: str = "", creation: str = ""):
        self.content_type = content_type
        self.language = language
        self.data = data
        self.url = url
        self.size = size
        self.hash = hash
        self.title = title
        self.creation = creation

    def get(self):
        attachment = {
            "contentType": self.content_type.get() if isinstance(self.content_type, Code) else None,
            "language": self.language.get() if isinstance(self.language, Code) else None,
            "data": self.data if isinstance(self.data, str) else None,
            "url": self.url if isinstance(self.url, str) else None,
            "size": self.size if isinstance(self.size, int) else None,
            "hash": self.hash if isinstance(self.hash, str) else None,
            "title": self.title if isinstance(self.title, str) else None,
            "creation": self.creation if isinstance(self.creation, str) else None
        }
        return {k: v for k, v in attachment.items() if v not in ("", None)}


class Quantity:

    def __init__(self, value: Optional[Union[float, int]] = None,
                 comparator: Optional[Literal["<", "<=", ">=", ">"]] = None,
                 unit: Optional[str] = None, system: Optional[str] = None, code: Optional[Code] = None):
        try:
            value = float(value)
        except ValueError:
            print("Quantity value is not a number!")

        self.value = value
        self.comparator = comparator
        self.unit = unit
        self.system = system
        self.code = code

    def get(self):
        quantity = {
            "value": self.value if isinstance(self.value, float) else None,
            "comparator": self.comparator if self.comparator in ["<", "<=", ">=", ">"] else None,
            "unit": self.unit if isinstance(self.unit, str) else None,
            "system": self.system if isinstance(self.system, str) else None,
            "code": self.code.get() if isinstance(self.code, Code) else None
        }
        return {k: v for k, v in quantity.items() if v not in ("", None)}

    def convert(self, fhir_quantity):
        if fhir_quantity is None:
            return None
        self.value = fhir_quantity.get('value')
        self.comparator = fhir_quantity.get('comparator')
        self.unit = fhir_quantity.get('unit')
        self.system = fhir_quantity.get('system')
        self.code = fhir_quantity.get('code')
        return self


class Range:

    def __init__(self, low: Optional[float] = None, high: Optional[float] = None):
        self.low = low
        self.high = high

    def get(self):
        _range = {
            "low": self.low if isinstance(self.low, float) else None,
            "high": self.high if isinstance(self.high, float) else None
        }
        return {k: v for k, v in _range.items() if v not in ("", None)}

    def convert(self, fhir_range):
        if fhir_range is None:
            return None
        self.low = fhir_range.get("low")
        self.high = fhir_range.get("high")
        return self


class RelatedArtifact:

    def __init__(self, related_artifact_type: Literal[
        "documentation", "justification", "citation", "predecessor", "successor", "derived-from", "depends-on", "composed-of"],
                 label: Optional[str] = None, display: Optional[str] = None, citation: Optional[str] = None,
                 url: Optional[str] = None, document: Optional[Attachment] = None, resource: Optional[str] = None):
        self.related_artifact_type = related_artifact_type
        self.label = label
        self.display = display
        self.citation = citation
        self.url = url
        self.document = document
        self.resource = resource

    def get(self):
        relatedartifact = {
            "type": self.related_artifact_type if self.related_artifact_type in [
                "documentation", "justification", "citation", "predecessor", "successor", "derived-from", "depends-on",
                "composed-of"] else None,
            "label": self.label if isinstance(self.label, str) else None,
            "display": self.display if isinstance(self.display, str) else None,
            "citation": self.citation if isinstance(self.citation, str) else None,
            "url": self.url if isinstance(self.url, str) else None,
            "document": self.document.get() if isinstance(self.document, Attachment) else None,
            "resource": self.resource if isinstance(self.resource, str) else None
        }
        return {k: v for k, v in relatedartifact.items() if v not in ("", None)}


class Author:

    def __init__(self, author_reference: Optional[Reference] = None, author_string: Optional[str] = None):
        self.author_reference = author_reference
        self.author_string = author_string

    def get(self):
        author = {
            "authorReference": self.author_reference if isinstance(self.author_reference, Reference) else None,
            "authorString": self.author_string if isinstance(self.author_string, str) else None
        }
        return {k: v for k, v in author.items() if v not in ("", None)}

    def convert(self, fhirpy_author):
        if fhirpy_author is None:
            return None
        self.author_reference = Reference().convert(fhirpy_author.get("authorReference"))
        self.author_string = fhirpy_author.get("authorString")
        return self


class Annotation:

    def __init__(self, text: str, author: Optional[Author] = None, time: str = None):
        self.author = author
        self.time = time
        self.text = text

    def get(self):
        annotation = {
            "authorReference": self.author.get().get("authorReference") if isinstance(self.author, Author) else None,
            "authorString": self.author.get().get("authorString") if isinstance(self.author, Author) else None,
            "time": self.time if isinstance(self.time, str) else None,
            "text": self.text if isinstance(self.text, str) else None
        }
        return {k: v for k, v in annotation.items() if v not in ("", None)}

    def convert(self, fhirpy_annotation):
        if fhirpy_annotation is None:
            return None
        self.author = Author().convert({"authorReference": fhirpy_annotation.get("authorReference"),
                                        "authorString": fhirpy_annotation.get("authorString")})
        self.time = fhirpy_annotation.get("time")
        self.text = fhirpy_annotation.get("text")
        return self


class RepeatBounds:

    def __init__(self, bounds_duration: Optional[str] = None, bounds_range: Optional[Range] = None,
                 bounds_period: Optional[Period] = None):
        self.bounds_duration = bounds_duration
        self.bounds_range = bounds_range
        self.bounds_period = bounds_period

    def get(self):
        bounds = {
            "boundsDuration": self.bounds_duration if isinstance(self.bounds_duration, str) else None,
            "boundsRange": self.bounds_range.get() if isinstance(self.bounds_range, Range) else None,
            "boundsPeriod": self.bounds_period.get() if isinstance(self.bounds_period, Period) else None
        }
        return {k: v for k, v in bounds.items() if v not in ("", None)}

    def convert(self, fhirpy_repeatbounds):
        if fhirpy_repeatbounds is None:
            return None
        self.bounds_duration = fhirpy_repeatbounds.get("boundsDuration")
        self.bounds_range = Range().convert(fhirpy_repeatbounds.get("boundsRange"))
        self.bounds_period = Period().convert(fhirpy_repeatbounds.get("boundsPeriod"))

        return self


class Repeat:

    def __init__(self, bounds: Optional[RepeatBounds] = None, count: Optional[int] = None,
                 count_max: Optional[int] = None, duration: Optional[float] = None,
                 duration_max: Optional[float] = None,
                 duration_unit: Optional[Literal["s", "min", "h", "d", "wk", "mo", "a"]] = None,
                 frequency: Optional[int] = None, frequency_max: Optional[int] = None,
                 period: Optional[float] = None, period_max: Optional[float] = None,
                 period_unit: Optional[Literal["s", "min", "h", "d", "wk", "mo", "a"]] = None,
                 day_of_week: Optional[List[Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]]] = None,
                 time_of_day: Optional[List[str]] = None, when: Optional[List[Code]] = None,
                 offset: Optional[int] = None):
        self.bounds = bounds
        self.count = count
        self.count_max = count_max
        self.duration = duration
        self.duration_max = duration_max
        self.duration_unit = duration_unit
        self.frequency = frequency
        self.frequency_max = frequency_max
        self.period = period
        self.period_max = period_max
        self.period_unit = period_unit
        self.day_of_week = day_of_week
        self.time_of_day = time_of_day
        self.when = when
        self.offset = offset

    def get(self):
        repeat = {
            "boundsDuration": self.bounds.get().get("boundsDuration") if isinstance(self.bounds,
                                                                                    RepeatBounds) else None,
            "boundsRange": self.bounds.get().get("boundsRange") if isinstance(self.bounds, RepeatBounds) else None,
            "boundsPeriod": self.bounds.get().get("boundsPeriod") if isinstance(self.bounds, RepeatBounds) else None,
            "count": self.count if isinstance(self.count, int) and self.count > 0 else None,
            "countMax": self.count_max if isinstance(self.count_max, int) and self.count_max > 0 else None,
            "duration": self.duration if isinstance(self.duration, float) else None,
            "durationMax": self.duration_max if isinstance(self.duration_max, float) else None,
            "durationUnit": self.duration_unit if self.duration_unit in ["s", "min", "h", "d", "wk", "mo",
                                                                         "a"] else None,
            "frequency": self.frequency if isinstance(self.frequency, int) and self.frequency > 0 else None,
            "frequencyMax": self.frequency_max if isinstance(self.frequency_max,
                                                             int) and self.frequency_max > 0 else None,
            "period": self.period if isinstance(self.period, float) else None,
            "periodMax": self.period_max if isinstance(self.period_max, float) else None,
            "periodUnit": self.period_unit if self.period_unit in ["s", "min", "h", "d", "wk", "mo",
                                                                   "a"] else None,
            "dayOfWeek": [d for d in self.day_of_week if
                          d in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]] if isinstance(self.day_of_week,
                                                                                                list) else None,
            "timeOfDay": [t for t in self.time_of_day if isinstance(t, str)] if isinstance(self.time_of_day,
                                                                                           list) else None,
            "when": [w.get() for w in self.when if isinstance(w, Code)] if isinstance(self.when, list) else None,
            "offset": self.offset if isinstance(self.offset, int) and self.offset > 0 else None
        }
        return {k: v for k, v in repeat.items() if v not in ("", None, [])}

    def convert(self, fhir_repeat):
        if fhir_repeat is None:
            return None
        self.bounds = RepeatBounds().convert(
            {"boundsDuration": fhir_repeat.get("boundsDuration"),
             "boundsRange": fhir_repeat.get("boundsRange"),
             "boundsPeriod": fhir_repeat.get("boundsPeriod")})
        self.count = fhir_repeat.get("count")
        self.count_max = fhir_repeat.get("countMax")
        self.duration = fhir_repeat.get("duration")
        self.duration_max = fhir_repeat.get("durationMax")
        self.duration_unit = fhir_repeat.get("durationUnit")
        self.frequency = fhir_repeat.get("frequency")
        self.frequency_max = fhir_repeat.get("frequencyMax")
        self.period = fhir_repeat.get("period")
        self.period_max = fhir_repeat.get("periodMax")
        self.period_unit = fhir_repeat.get("periodUnit")
        self.day_of_week = fhir_repeat.get("dayOfWeek")
        self.time_of_day = fhir_repeat.get("timeOfDay")
        self.when = [Code().convert(w) for w in fhir_repeat.get("when") if w is not None] if isinstance(
            fhir_repeat.get("when"), list) else None
        self.offset = fhir_repeat.get("offset")
        return self


class Timing:

    def __init__(self, event: Optional[List[str]] = None, repeat: Optional[Repeat] = None,
                 code: Optional[CodeableConcept] = None):
        self.event = event
        self.repeat = repeat
        self.code = code

    def get(self):
        timing = {
            "event": [e for e in self.event if isinstance(e, str)] if isinstance(self.event, list) else None,
            "repeat": self.repeat.get() if isinstance(self.repeat, Repeat) else None,
            "code": self.code.get() if isinstance(self.code, CodeableConcept) else None
        }
        return {k: v for k, v in timing.items() if v not in ("", None, [])}

    def convert(self, fhir_timing):
        if fhir_timing is None:
            return None
        self.event = fhir_timing.get("event") if isinstance(self.event, list) else None
        self.repeat = Repeat().convert(fhir_timing.get("repeat"))
        self.code = CodeableConcept().convert(fhir_timing.get("code"))
        return self


class Ratio:

    def __init__(self, numerator: Optional[Quantity] = None, denominator: Optional[Quantity] = None):
        self.numerator = numerator
        self.denominator = denominator

    def get(self):
        ratio = {
            "numerator": self.numerator.get() if isinstance(self.numerator, Quantity) else None,
            "denominator": self.denominator.get() if isinstance(self.denominator, Quantity) else None
        }
        return {k: v for k, v in ratio.items() if v not in ("", None)}

    def convert(self, fhir_ratio):
        if fhir_ratio is None:
            return None
        self.numerator = Quantity().convert(fhir_ratio.get("numerator"))
        self.denominator = Quantity().convert(fhir_ratio.get("denominator"))
        return self


class SampledData:

    def __init__(self, origin: str, period: float, dimensions: int, factor: Optional[float] = None,
                 lower_limit: Optional[float] = None, upper_limit: Optional[float] = None, data: Optional[str] = None):
        self.origin = origin
        self.period = period
        self.dimensions = dimensions
        self.factor = factor
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.data = data

    def get(self):
        sampled_data = {
            "origin": self.origin if isinstance(self.origin, str) else None,
            "period": self.period if isinstance(self.period, float) else None,
            "factor": self.factor if isinstance(self.factor, float) else None,
            "lowerLimit": self.lower_limit if isinstance(self.lower_limit, float) else None,
            "upperLimit": self.upper_limit if isinstance(self.upper_limit, float) else None,
            "dimensions": self.dimensions if isinstance(self.dimensions, int) and self.dimensions > 0 else None,
            "data": self.data if isinstance(self.data, str) else None
        }
        return {k: v for k, v in sampled_data.items() if v not in ("", None)}

    def convert(self, fhir_sampled_data):
        if fhir_sampled_data is None:
            return None
        self.origin = fhir_sampled_data.get("origin")
        self.period = fhir_sampled_data.get("period")
        self.dimensions = fhir_sampled_data.get("dimensions")
        self.factor = fhir_sampled_data.get("factor")
        self.lower_limit = fhir_sampled_data.get("lowerLimit")
        self.upper_limit = fhir_sampled_data.get("upperLimit")
        self.data = fhir_sampled_data.get("data")
        return self


class UsageContextValue:

    def __init__(self, value_codeable_concept: Optional[CodeableConcept] = None,
                 value_quantity: Optional[Quantity] = None, value_range: Optional[Range] = None,
                 value_reference: Optional[Reference] = None):
        self.value_codeable_concept = value_codeable_concept
        self.value_quantity = value_quantity
        self.value_range = value_range
        self.value_reference = value_reference

    def get(self):
        value = {
            "valueCodeableConcept": self.value_codeable_concept if isinstance(self.value_codeable_concept,
                                                                              CodeableConcept) else None,
            "valueQuantity": self.value_quantity if isinstance(self.value_quantity, Quantity) else None,
            "valueRange": self.value_range if isinstance(self.value_range, Range) else None,
            "valueReference": self.value_reference if isinstance(self.value_reference, Reference) else None
        }
        return {k: v for k, v in value.items() if v not in ("", None)}


class UsageContext:

    def __init__(self, code: Coding, value: UsageContextValue):
        self.code = code
        self.value = value

    def get(self):
        context = {
            "code": self.code if isinstance(self.code, Coding) else None,
            "valueCodeableConcept": self.value.get().get("valueCodeableConcept") if isinstance(self.value,
                                                                                               UsageContextValue) else None,
            "valueQuantity": self.value.get().get("valueQuantity") if isinstance(self.value,
                                                                                 UsageContextValue) else None,
            "valueRange": self.value.get().get("valueRange") if isinstance(self.value,
                                                                           UsageContextValue) else None,
            "valueReference": self.value.get().get("valueReference") if isinstance(self.value,
                                                                                   UsageContextValue) else None,
        }
        return {k: v for k, v in context.items() if v not in ("", None)}


class FHIRSubject:
    def __init__(self, subject_codeable_concept: Optional[CodeableConcept] = None,
                 subject_reference: Optional[Reference] = None):
        self.subject_codeable_concept = subject_codeable_concept
        self.subject_reference = subject_reference

    def get(self):
        subject = {
            "subjectCodeableConcept": self.subject_codeable_concept.get() if isinstance(self.subject_codeable_concept,
                                                                                        CodeableConcept) else None,
            "subjectReference": self.subject_reference.get() if isinstance(self.subject_reference, Reference) else None
        }
        return {k: v for k, v in subject.items() if v not in ("", None)}


class DataRequirementCodeFilter:
    def __init__(self, path: Optional[str] = None, search_param: Optional[str] = None, value_set: Optional[str] = None,
                 code: Optional[List[Coding]] = None):
        self.path = path
        self.search_param = search_param
        self.value_set = value_set
        self.code = code

    def get(self):
        code_filter = {
            "path": self.path if isinstance(self.path, str) else None,
            "searchParam": self.search_param if isinstance(self.search_param, str) else None,
            "valueSet": self.value_set if isinstance(self.value_set, str) else None,
            "code": [c.get() for c in self.code if isinstance(c, Coding)] if isinstance(self.code, list) else None,
        }
        return {k: v for k, v in code_filter.items() if v not in ("", None, [])}


class DataRequirementDateFilterValue:

    def __init__(self, value_date_time: Optional[str] = None, value_period: Optional[Period] = None,
                 value_duration: Optional[str] = None):
        self.value_date_time = value_date_time
        self.value_period = value_period
        self.value_duration = value_duration

    def get(self):
        value = {
            "valueDateTime": self.value_date_time if isinstance(self.value_date_time, str) else None,
            "valuePeriod": self.value_period.get() if isinstance(self.value_period, Period) else None,
            "valueDuration": self.value_duration if isinstance(self.value_duration, str) else None
        }
        return {k: v for k, v in value.items() if v not in ("", None)}


class DataRequirementDateFilter:
    def __init__(self, path: Optional[str] = None, search_param: Optional[str] = None,
                 value: Optional[DataRequirementDateFilterValue] = None):
        self.path = path
        self.search_param = search_param
        self.value = value

    def get(self):
        code_filter = {
            "path": self.path if isinstance(self.path, str) else None,
            "searchParam": self.search_param if isinstance(self.search_param, str) else None,
            "valueDateTime": self.value.get().get("valueDateTime") if isinstance(self.value,
                                                                                 DataRequirementDateFilterValue) else None,
            "valuePeriod": self.value.get().get("valuePeriod") if isinstance(self.value,
                                                                             DataRequirementDateFilterValue) else None,
            "valueDuration": self.value.get().get("valueDuration") if isinstance(self.value,
                                                                                 DataRequirementDateFilterValue) else None,
        }
        return {k: v for k, v in code_filter.items() if v not in ("", None)}


class DataRequirementSort:

    def __init__(self, path: str, direction: Literal["ascending", "descending"]):
        self.path = path
        self.direction = direction

    def get(self):
        sort = {
            "path": self.path if isinstance(self.path, str) else None,
            "direction": self.direction if self.direction in ["ascending", "descending"] else None
        }
        return {k: v for k, v in sort.items() if v not in ("", None)}


class DataRequirement:

    def __init__(self, data_requirement_type: Code, profile: Optional[List[str]] = None,
                 subject: Optional[FHIRSubject] = None, must_support: Optional[List[str]] = None,
                 code_filter: Optional[List[DataRequirementCodeFilter]] = None,
                 data_filter: Optional[List[DataRequirementDateFilter]] = None, limit: Optional[int] = None,
                 sort: Optional[List[DataRequirementSort]] = None):
        self.data_requirement_type = data_requirement_type
        self.profile = profile
        self.subject = subject
        self.must_support = must_support
        self.code_filter = code_filter
        self.data_filter = data_filter
        self.limit = limit
        self.sort = sort

    def get(self):
        data_requirement = {
            "type": self.data_requirement_type.get() if isinstance(self.data_requirement_type, Code) else None,
            "profile": [p for p in self.profile if isinstance(p, str)] if isinstance(self.profile, list) else None,
            "subjectCodeableConcept": self.subject.get().get("subjectCodeableConcept") if isinstance(self.subject,
                                                                                                     FHIRSubject) else None,
            "subjectReference": self.subject.get().get("subjectReference") if isinstance(self.subject,
                                                                                         FHIRSubject) else None,
            "mustSupport": [m for m in self.must_support if isinstance(m, str)] if isinstance(self.must_support,
                                                                                              list) else None,
            "codeFilter": [c.get() for c in self.code_filter if isinstance(c, DataRequirementCodeFilter)] if isinstance(
                self.code_filter, list) else None,
            "dateFilter": [d.get() for d in self.data_filter if isinstance(d, DataRequirementDateFilter)] if isinstance(
                self.data_filter, list) else None,
            "limit": self.limit if isinstance(self.limit, int) and self.limit > 0 else None,
            "sort": [s.get() for s in self.sort if isinstance(s, DataRequirementSort)] if isinstance(self.sort,
                                                                                                     list) else None
        }
        return {k: v for k, v in data_requirement.items() if v not in ("", None, [])}


class Expression:

    def __init__(self, language: Literal["text/cql", "text/fhirpath", "application/x-fhir-query", "etc"],
                 description: Optional[str] = None, name: Optional[str] = None, expression: Optional[str] = None,
                 reference: Optional[str] = None):
        self.language = language
        self.description = description
        self.name = name
        self.expression = expression
        self.reference = reference

    def get(self):
        expression = {
            "description": self.description if isinstance(self.description, str) else None,
            "name": self.name if isinstance(self.name, str) else None,
            "language": self.language if isinstance(self.language, str) else None,
            "expression": self.expression if isinstance(self.expression, str) else None,
            "reference": self.reference if isinstance(self.reference, str) else None,
        }
        return {k: v for k, v in expression.items() if v not in ("", None)}


class TriggerDefinitionTiming:

    def __init__(self, timing_timing: Optional[Timing], timing_reference: Optional[Reference] = None,
                 timing_date: Optional[str] = None, timing_date_time: Optional[str] = None):
        self.timing_timing = timing_timing
        self.timing_reference = timing_reference
        self.timing_date = timing_date
        self.timing_date_time = timing_date_time

    def get(self):
        timing = {
            "timingTiming": self.timing_timing.get() if isinstance(self.timing_timing, Timing) else None,
            "timingReference": self.timing_reference.get() if isinstance(self.timing_reference, Reference) else None,
            "timingDate": self.timing_date if isinstance(self.timing_date, str) else None,
            "timingDateTime": self.timing_date_time if isinstance(self.timing_date_time, str) else None
        }
        return {k: v for k, v in timing.items() if v not in ("", None)}


class TriggerDefinition:

    def __init__(self, trigger_definition_type: Literal[
        "named-event", "periodic", "data-changed", "data-added", "data-modified", "data-removed", "data-accessed", "data-access-ended"],
                 name: Optional[str] = None, timing: Optional[TriggerDefinitionTiming] = None,
                 data: Optional[List[DataRequirement]] = None, condition: Optional[Expression] = None):
        self.trigger_definition_type = trigger_definition_type
        self.name = name
        self.timing = timing
        self.data = data
        self.condition = condition

    def get(self):
        trigger_definition = {
            "type": self.trigger_definition_type if self.trigger_definition_type in [
                "named-event", "periodic", "data-changed", "data-added", "data-modified", "data-removed",
                "data-accessed", "data-access-ended"] else None,
            "name": self.name if isinstance(self.name, str) else None,
            "timingTiming": self.timing.get().get("timingTiming") if isinstance(self.timing,
                                                                                TriggerDefinitionTiming) else None,
            "timingReference": self.timing.get().get("timingReference") if isinstance(self.timing,
                                                                                      TriggerDefinitionTiming) else None,
            "timingDate": self.timing.get().get("timingDate") if isinstance(self.timing,
                                                                            TriggerDefinitionTiming) else None,
            "timingDateTime": self.timing.get().get("timingDateTime") if isinstance(self.timing,
                                                                                    TriggerDefinitionTiming) else None,
            "data": [d.get() for d in self.data if isinstance(d, DataRequirement)] if isinstance(self.data,
                                                                                                 list) else None,
            "condition": self.condition.get() if isinstance(self.condition, Expression) else None
        }
        return {k: v for k, v in trigger_definition.items() if v not in ("", None, [])}


class Narrative:

    def __init__(self, status: Literal["generated", "extensions", "additional", "empty"], div: str):
        self.status = status
        self.div = div

    def get(self):
        narrative = {
            "status": self.status if self.status in ["generated", "extensions", "additional", "empty"] else None,
            "div": self.div if isinstance(self.div, str) else None
        }
        return {k: v for k, v in narrative.items() if v not in ("", None)}


class DosageAsNeeded:
    def __init__(self, as_needed_boolean: Optional[bool] = None,
                 as_needed_codeable_concept: Optional[CodeableConcept] = None):
        self.as_needed_boolean = as_needed_boolean
        self.as_needed_codeable_concept = as_needed_codeable_concept

    def get(self):
        needed = {
            "asNeededBoolean": self.as_needed_boolean if isinstance(self.as_needed_boolean, bool) else None,
            "asNeededCodeableConcept:": self.as_needed_codeable_concept.get() if isinstance(
                self.as_needed_codeable_concept, CodeableConcept) else None,
        }
        return {k: v for k, v in needed.items() if v not in ("", None)}


class DosageDoseAndRateDose:
    def __init__(self, dose_range: Optional[Range] = None, dose_quantity: Optional[str] = None):
        self.range = dose_range
        self.quantity = dose_quantity

    def get(self):
        dose = {
            "doseRange": self.range.get() if self.range else None,
            "doseQuantity": self.quantity if isinstance(self.quantity, str) else None
        }
        return {k: v for k, v in dose.items() if v not in ("", None)}


class DosageDoseAndRateRate:
    def __init__(self, rate_ratio: Optional[Ratio] = None, rate_range: Optional[Range] = None,
                 rate_quantity: Optional[str] = None):
        self.rate_ratio = rate_ratio
        self.rate_range = rate_range
        self.rate_quantity = rate_quantity

    def get(self):
        rate = {
            "rateRatio": self.rate_ratio.get() if isinstance(self.rate_ratio, Ratio) else None,
            "rateRange": self.rate_range.get() if isinstance(self.rate_range, Range) else None,
            "rateQuantity": self.rate_quantity if isinstance(self.rate_quantity, str) else None
        }
        return {k: v for k, v in rate.items() if v not in ("", None)}


class DosageDoseAndRate:
    def __init__(self, _type: Optional[CodeableConcept] = None, dose: Optional[DosageDoseAndRateDose] = None,
                 rate: Optional[DosageDoseAndRateRate] = None):
        self._type = _type
        self.dose = dose
        self.rate = rate

    def get(self):
        dose_rate = {
            "type": self._type.get() if isinstance(self._type, CodeableConcept) else None,
            "doseRange": self.dose.get().get("doseRange") if isinstance(self.dose, DosageDoseAndRateDose) else None,
            "doseQuantity": self.dose.get().get("doseQuantity") if isinstance(self.dose,
                                                                              DosageDoseAndRateDose) else None,
            "rateRatio": self.rate.get().get("rateRatio") if isinstance(self.rate, DosageDoseAndRateRate) else None,
            "rateRange": self.rate.get().get("rateRange") if isinstance(self.rate, DosageDoseAndRateRate) else None,
            "rateQuantity": self.rate.get().get("rateQuantity") if isinstance(self.rate,
                                                                              DosageDoseAndRateRate) else None
        }
        return {k: v for k, v in dose_rate.items() if v not in ("", None)}


class Dosage:

    def __init__(self, sequence: Optional[int] = None, text: Optional[str] = None,
                 additional_instruction: Optional[List[CodeableConcept]] = None,
                 patient_instruction: Optional[str] = None, timing: Optional[Timing] = None,
                 as_needed: Optional[DosageAsNeeded] = None, site: Optional[CodeableConcept] = None,
                 route: Optional[CodeableConcept] = None, method: Optional[CodeableConcept] = None,
                 dose_and_rate: Optional[DosageDoseAndRate] = None, max_dose_period: Optional[Ratio] = None,
                 max_dose_per_administration: Optional[str] = None, max_dose_per_lifetime: Optional[str] = None):
        self.sequence = sequence
        self.text = text
        self.additional_instruction = additional_instruction
        self.patient_instruction = patient_instruction
        self.timing = timing
        self.as_needed = as_needed
        self.site = site
        self.route = route
        self.method = method
        self.dose_and_rate = dose_and_rate
        self.max_dose_period = max_dose_period
        self.max_dose_per_administration = max_dose_per_administration
        self.max_dose_per_lifetime = max_dose_per_lifetime

    def get(self):
        dosage = {
            "sequence": self.sequence if isinstance(self.sequence, int) else None,
            "text": self.text if isinstance(self.text, str) else None,
            "additionalInstruction": [a.get() for a in self.additional_instruction if
                                      isinstance(a, CodeableConcept)] if isinstance(self.additional_instruction,
                                                                                    list) else None,
            "patientInstruction": self.patient_instruction if isinstance(self.patient_instruction, str) else None,
            "timing": self.timing.get() if isinstance(self.timing, Timing) else None,
            "asNeededBoolean": self.as_needed.get().get("asNeededBoolean") if isinstance(self.as_needed,
                                                                                         DosageAsNeeded) else None,
            "asNeededCodeableConcept": self.as_needed.get().get("asNeededCodeableConcept") if isinstance(self.as_needed,
                                                                                                         DosageAsNeeded) else None,
            "site": self.site if isinstance(self.site, CodeableConcept) else None,
            "route": self.route if isinstance(self.route, CodeableConcept) else None,
            "method": self.method if isinstance(self.method, CodeableConcept) else None,
            "doseAndRate": self.dose_and_rate.get() if isinstance(self.dose_and_rate, DosageDoseAndRate) else None,
            "maxDosePerPeriod": self.max_dose_period.get() if isinstance(self.max_dose_period, Ratio) else None,
            "maxDosePerAdministration": self.max_dose_per_administration if isinstance(self.max_dose_per_administration,
                                                                                       str) else None,
            "maxDosePerLifetime": self.max_dose_per_lifetime.get() if isinstance(self.max_dose_per_lifetime,
                                                                                 str) else None,
        }
        return {k: v for k, v in dosage.items() if v not in ("", None)}
