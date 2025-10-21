from abc import ABC
from .abstract_resource import AbstractResource
from .element import (Meta, Identifier, Reference, Period, CodeableConcept, Coding, Code, Attachment)
from typing import Optional, List, Literal


class ConsentProvisionActor:
    def __init__(self, role: CodeableConcept, reference: Reference):
        self.role = role
        self.reference = reference

    def get(self):
        actor = {
            "role": self.role.get() if isinstance(self.role, CodeableConcept) else None,
            "reference": self.reference.get() if isinstance(self.reference, Reference) else None,
        }
        return {k: v for k, v in actor.items() if v not in ("", None, [])}


class ConsentProvisionData:
    def __init__(self, meaning: Literal["instance", "related", "dependents", "authoredby"], reference: Reference):
        self.meaning = meaning
        self.reference = reference

    def get(self):
        data = {
            "meaning": self.meaning if self.meaning in ("instance", "related", "dependents", "authoredby") else None,
            "reference": self.reference.get() if isinstance(self.reference, Reference) else None,
        }
        return {k: v for k, v in data.items() if v not in ("", None, [])}


class ConsentProvision:
    def __init__(self, _type: Literal["deny", "permit"], period: Optional[Period] = None,
                 actor: Optional[List[ConsentProvisionActor]] = None, action: Optional[List[CodeableConcept]] = None,
                 security_label: Optional[List[Coding]] = None, purpose: Optional[List[Coding]] = None,
                 _class: Optional[List[Coding]] = None, code: Optional[List[CodeableConcept]] = None,
                 data_period: Optional[Period] = None, data: Optional[List[ConsentProvisionData]] = None):
        self._type = _type
        self.period = period
        self.actor = actor
        self.action = action
        self.security_label = security_label
        self.purpose = purpose
        self._class = _class
        self.code = code
        self.data_period = data_period
        self.data = data

    def get(self):
        provision = {
            "type": self._type if self._type in ("deny", "permit") else None,
            "period": self.period.get() if isinstance(self.period, Period) else None,
            "actor": [a.get() for a in self.actor if isinstance(a, ConsentProvisionActor)] if isinstance(self.actor,
                                                                                                         list) else None,
            "action": [a.get() for a in self.action if isinstance(a, CodeableConcept)] if isinstance(self.action,
                                                                                                     list) else None,
            "securityLabel": [s.get() for s in self.security_label if isinstance(s, Coding)] if isinstance(
                self.security_label, list) else None,
            "purpose": [p.get() for p in self.purpose if isinstance(p, Coding)] if isinstance(
                self.purpose, list) else None,
            "class": [c.get() for c in self._class if isinstance(c, Coding)] if isinstance(
                self._class, list) else None,
            "dataPeriod": self.data_period.get() if isinstance(self.data_period, Period) else None,
            "data": [d.get() for d in self.data if isinstance(d, ConsentProvisionData)] if isinstance(self.data,
                                                                                                      list) else None
        }
        return {k: v for k, v in provision.items() if v not in ("", None, [])}


class ConsentVerification:
    def __init__(self, verified: bool, verified_with: Optional[Reference] = None,
                 verification_date: Optional[str] = None):
        self.verified = verified
        self.verified_with = verified_with
        self.verification_date = verification_date

    def get(self):
        verification = {
            "verified": self.verified if isinstance(self.verified, bool) else None,
            "verifiedWith": self.verified_with.get() if isinstance(self.verified_with, Reference) else None,
            "verificationDate": self.verification_date if isinstance(self.verification_date, str) else None,
        }
        return {k: v for k, v in verification.items() if v not in ("", None, [])}


class ConsentPolicy:
    def __init__(self, authority: Optional[str] = None, uri: Optional[str] = None):
        self.authority = authority
        self.uri = uri

    def get(self):
        policy = {
            "authority": self.authority if isinstance(self.authority, str) else None,
            "uri": self.uri if isinstance(self.uri, str) else None,
        }
        return {k: v for k, v in policy.items() if v not in ("", None, [])}


class ConsentSource:
    def __init__(self, source_attachment: Optional[Attachment] = None, source_reference: Optional[Reference] = None):
        self.source_attachment = source_attachment
        self.source_reference = source_reference

    def get(self):
        source = {
            "sourceAttachment": self.source_attachment.get() if isinstance(self.source_attachment,
                                                                           Attachment) else None,
            "sourceReference": self.source_reference.get() if isinstance(self.source_reference, Reference) else None,
        }
        return {k: v for k, v in source.items() if v not in ("", None, [])}


class Consent(AbstractResource, ABC):
    def __init__(self, status: Literal["draft", "proposed", "active", "rejected", "inactive", "entered-in-error"],
                 scope: CodeableConcept, category: List[CodeableConcept], meta: Optional[Meta] = None,
                 identifier: Optional[List[Identifier]] = None, patient: Optional[Reference] = None,
                 date_time: Optional[str] = None, performer: Optional[List[Reference]] = None,
                 organization: Optional[Reference] = None, source: Optional[ConsentSource] = None,
                 policy: Optional[List[ConsentPolicy]] = None, policy_rule: Optional[CodeableConcept] = None,
                 verification: Optional[List[ConsentVerification]] = None,
                 provision: Optional[ConsentProvision] = None):
        super().__init__(meta, identifier)
        self._resource_type = "Consent"
        self.status = status
        self.scope = scope
        self.category = category
        self.patient = patient
        self.date_time = date_time
        self.performer = performer
        self.organization = organization
        self.source = source
        self.policy = policy
        self.policy_rule = policy_rule
        self.verification = verification
        self.provision = provision

    def get(self):
        consent = {
            "resourceType": self._resource_type,
            "meta": self.meta.get() if isinstance(self.meta, Meta) else None,
            "identifier": [i.get() for i in self.identifier if
                           isinstance(i, Identifier)] if isinstance(self.identifier, list) else None,
            "status": self.status if self.status in [
                "draft", "proposed", "active", "rejected", "inactive", "entered-in-error"] else None,
            "scope": self.scope.get() if isinstance(self.scope, CodeableConcept) else None,
            "category": [c.get() for c in self.category if isinstance(c, CodeableConcept)] if isinstance(self.category,
                                                                                                         list) else None,
            "patient": self.patient.get() if isinstance(self.patient, Reference) else None,
            "dateTime": self.date_time if isinstance(self.date_time, str) else None,
            "performer": [p.get() for p in self.performer if isinstance(p, Reference)] if isinstance(self.performer,
                                                                                               list) else None,
            "organization": [o.get() for o in self.organization if isinstance(o, Reference)] if isinstance(self.organization,
                                                                                                     list) else None,
            "sourceAttachment": self.source.get().get("sourceAttachment") if isinstance(self.source,
                                                                                        ConsentSource) else None,
            "sourceReference": self.source.get().get("sourceReference") if isinstance(self.source,
                                                                                      ConsentSource) else None,
            "policy": [p.get() for p in self.policy if isinstance(p, ConsentPolicy)] if isinstance(self.policy,
                                                                                             list) else None,
            "policyRule": self.policy_rule.get() if isinstance(self.policy_rule, CodeableConcept) else None,
            "verification": [v.get() for v in self.verification if isinstance(v, ConsentVerification)] if isinstance(
                self.verification, list) else None,
            "provision": self.provision.get() if isinstance(self.provision, ConsentProvision) else None,
        }
        return {k: v for k, v in consent.items() if v not in ("", None, [])}

    def convert(self, fhirpy_resource):
        pass


ConsentScopeCodeableConcept = {
    "adr": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentscope", code=Code(value="adr"),
                        display="Advanced Care Directive")],
        text="Actions to be taken if they are no longer able to make decisions for themselves"),
    "research": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentscope", code=Code(value="research"),
                        display="Consent to participate in research protocol and information sharing required")],
        text="Actions to be taken if they are no longer able to make decisions for themselves"),
    "patient-privacy": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentscope", code=Code(value="patient-privacy"),
                        display="Privacy Consent")],
        text="Agreement to collect, access, use or disclose (share) information"),
    "treatment": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentscope", code=Code(value="treatment"),
                        display="Treatment")],
        text="Consent to undergo a specific treatment")
}

ConsentCategoryCodeableConcept = {
    "acd": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="acd"),
                        display="Advance Directive")],
        text="Any instructions, written or given verbally by a patient to a health care provider in anticipation of potential need for medical treatment. [2005 Honor My Wishes]"),
    "dnr": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="dnr"),
                        display="Do Not Resuscitate")],
        text="A legal document, signed by both the patient and their provider, stating a desire not to have CPR initiated in case of a cardiac event. Note: This form was replaced in 2003 with the Physician Orders for Life-Sustaining Treatment [POLST]."),
    "emrgonly": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="emrgonly"),
                   display="	Emergency Only")],
        text="Opt-in to disclosure of health information for emergency only consent directive. Comment: This general consent directive specifically limits disclosure of health information for purpose of emergency treatment. Additional parameters may further limit the disclosure to specific users, roles, duration, types of information, and impose uses obligations. [ActConsentDirective (2.16.840.1.113883.1.11.20425)]"),
    "hcd": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="hcd"),
                        display="Health Care Directive")],
        text="Patient's document telling patient's health care provider what the patient wants or does not want if the patient is diagnosed as being terminally ill and in a persistent vegetative state or in a permanently unconscious condition.[2005 Honor My Wishes]"),
    "npp": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="npp"),
                        display="Notice of Privacy Practices")],
        text="Acknowledgement of custodian notice of privacy practices. Usage Notes: This type of consent directive acknowledges a custodian's notice of privacy practices including its permitted collection, access, use and disclosure of health information to users and for purposes of use specified. [ActConsentDirective (2.16.840.1.113883.1.11.20425)]"),
    "polst": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="polst"),
                        display="POLST")],
        text="The Physician Order for Life-Sustaining Treatment form records a person's health care wishes for end of life emergency treatment and translates them into an order by the physician. It must be reviewed and signed by both the patient and the physician, Advanced Registered Nurse Practitioner or Physician Assistant. [2005 Honor My Wishes] Comment: Opt-in Consent Directive with restrictions."),
    "research": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="research"),
                   display="Research Information Access")],
        text="Consent to have healthcare information in an electronic health record accessed for research purposes. [VALUE SET: ActConsentType (2.16.840.1.113883.1.11.19897)]"),
    "rsdid": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="rsdid"),
                        display="De-identified Information Access")],
        text="Consent to have de-identified healthcare information in an electronic health record that is accessed for research purposes, but without consent to re-identify the information under any circumstance. [VALUE SET: ActConsentType (2.16.840.1.113883.1.11.19897)"),
    "rsreid": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentcategorycodes", code=Code(value="rsreid"),
                        display="Re-identifiable Information Access")],
        text="Consent to have de-identified healthcare information in an electronic health record that is accessed for research purposes re-identified under specific circumstances outlined in the consent. [VALUE SET: ActConsentType (2.16.840.1.113883.1.11.19897)]"),
    "ICOL": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="ICOL"),
                        display="information collection")],
        text="Definition: Consent to have healthcare information collected in an electronic health record. This entails that the information may be used in analysis, modified, updated."),
    "IDSCL": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="IDSCL"),
                        display="information disclosure")],
        text="Definition: Consent to have collected healthcare information disclosed."),
    "INFA": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="INFA"),
                        display="information access")],
        text="Definition: Consent to access healthcare information."),
    "INFAO": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="INFAO"),
                        display="access only")],
        text="Definition: Consent to access or 'read' only, which entails that the information is not to be copied, screen printed, saved, emailed, stored, re-disclosed or altered in any way. This level ensures that data which is masked or to which access is restricted will not be. Example: Opened and then emailed or screen printed for use outside of the consent directive purpose."),
    "INFASO": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="INFASO"),
                        display="access and save only")],
        text="Definition: Consent to access and save only, which entails that access to the saved copy will remain locked."),
    "IRDSCL": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="IRDSCL"),
                        display="information redisclosure")],
        text="Definition: Information re-disclosed without the patient's consent."),
    "RESEARCH": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="RESEARCH"),
                        display="research information access")],
        text="Definition: Consent to have healthcare information in an electronic health record accessed for research purposes."),
    "RSDID": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="RSDID"),
                        display="de-identified information access")],
        text="Definition: Consent to have de-identified healthcare information in an electronic health record that is accessed for research purposes, but without consent to re-identify the information under any circumstance."),
    "RSREID": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ActCode", code=Code(value="RSREID"),
                        display="re-identifiable information access")],
        text="Definition: Consent to have de-identified healthcare information in an electronic health record that is accessed for research purposes re-identified under specific circumstances outlined in the consent. Example:: Where there is a need to inform the subject of potential health issues."),
    "59284-0": CodeableConcept(
        codings=[Coding(system="http://loinc.org", code=Code(value="59284-0"),
                        display="Patient Consent")]),
    "57016-8": CodeableConcept(
        codings=[Coding(system="http://loinc.org", code=Code(value="57016-8"),
                        display="Privacy policy acknowledgement Document")]),
    "57017-6": CodeableConcept(
        codings=[Coding(system="http://loinc.org", code=Code(value="57017-6"),
                        display="Privacy policy Organization Document")]),
    "64292-6": CodeableConcept(
        codings=[Coding(system="http://loinc.org", code=Code(value="64292-6"),
                        display="Release of information consent")]),
}

ConsentPolicyRuleCodeableConcept = {
    "cric": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="cric"),
                        display="Common Rule Informed Consent")],
        text="45 CFR part 46 §46.116 General requirements for informed consent; and §46.117 Documentation of informed consent. https://www.gpo.gov/fdsys/pkg/FR-2017-01-19/pdf/2017-01058.pdf"),
    "illinois-minor-procedure": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes",
                        code=Code(value="illinois-minor-procedure"),
                        display="Illinois Consent by Minors to Medical Procedures")],
        text="The consent to the performance of a medical or surgical procedure by a physician licensed to practice medicine and surgery, a licensed advanced practice nurse, or a licensed physician assistant executed by a married person who is a minor, by a parent who is a minor, by a pregnant woman who is a minor, or by any person 18 years of age or older, is not voidable because of such minority, and, for such purpose, a married person who is a minor, a parent who is a minor, a pregnant woman who is a minor, or any person 18 years of age or older, is deemed to have the same legal capacity to act and has the same powers and obligations as has a person of legal age. Consent by Minors to Medical Procedures Act. (410 ILCS 210/0.01) (from Ch. 111, par. 4500) Sec. 0.01. Short title. This Act may be cited as the Consent by Minors to Medical Procedures Act. (Source: P.A. 86-1324.) http://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1539&ChapterID=35"),
    "hipaa-auth": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="hipaa-auth"),
                   display="HIPAA Authorization")],
        text="HIPAA 45 CFR Section 164.508 Uses and disclosures for which an authorization is required. (a) Standard: Authorizations for uses and disclosures. (1) Authorization required: General rule. Except as otherwise permitted or required by this subchapter, a covered entity SHALL not use or disclose protected health information without an authorization that is valid under this section. When a covered entity obtains or receives a valid authorization for its use or disclosure of protected health information, such use or disclosure must be consistent with such authorization. Usage Note: Authorizations governed under this regulation meet the definition of an opt in class of consent directive."),
    "hipaa-npp": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="hipaa-npp"),
                        display="HIPAA Notice of Privacy Practices")],
        text="164.520 Notice of privacy practices for protected health information. (1) Right to notice. Except as provided by paragraph (a)(2) or (3) of this section, an individual has a right to adequate notice of the uses and disclosures of protected health information that may be made by the covered entity, and of the individual's rights and the covered entity's legal duties with respect to protected health information. Usage Note: Restrictions governed under this regulation meet the definition of an implied with an opportunity to dissent class of consent directive."),
    "hipaa-restrictions": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes",
                        code=Code(value="hipaa-restrictions"),
                        display="HIPAA Restrictions")],
        text="HIPAA 45 CFR 164.510 - Uses and disclosures requiring an opportunity for the individual to agree or to object. A covered entity may use or disclose protected health information, provided that the individual is informed in advance of the use or disclosure and has the opportunity to agree to or prohibit or restrict the use or disclosure, in accordance with the applicable requirements of this section. The covered entity may orally inform the individual of and obtain the individual's oral agreement or objection to a use or disclosure permitted by this section. Usage Note: Restrictions governed under this regulation meet the definition of an opt out with exception class of consent directive."),
    "hipaa-research": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="hipaa-research"),
                   display="HIPAA Research Authorization")],
        text="HIPAA 45 CFR 164.508 - Uses and disclosures for which an authorization is required. (a) Standard: Authorizations for uses and disclosures. (3) Compound authorizations. An authorization for use or disclosure of protected health information SHALL NOT be combined with any other document to create a compound authorization, except as follows: (i) An authorization for the use or disclosure of protected health information for a research study may be combined with any other type of written permission for the same or another research study. This exception includes combining an authorization for the use or disclosure of protected health information for a research study with another authorization for the same research study, with an authorization for the creation or maintenance of a research database or repository, or with a consent to participate in research. Where a covered health care provider has conditioned the provision of research-related treatment on the provision of one of the authorizations, as permitted under paragraph (b)(4)(i) of this section, any compound authorization created under this paragraph must clearly differentiate between the conditioned and unconditioned components and provide the individual with an opportunity to opt in to the research activities described in the unconditioned authorization. Usage Notes: See HHS http://www.hhs.gov/hipaa/for-professionals/special-topics/research/index.html and OCR http://www.hhs.gov/hipaa/for-professionals/special-topics/research/index.html"),
    "hipaa-self-pay": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="hipaa-self-pay"),
                   display="HIPAA Self-Pay Restriction")],
        text="HIPAA 45 CFR 164.522(a) Right To Request a Restriction of Uses and Disclosures. (vi) A covered entity must agree to the request of an individual to restrict disclosure of protected health information about the individual to a health plan if: (A) The disclosure is for the purpose of carrying out payment or health care operations and is not otherwise required by law; and (B) The protected health information pertains solely to a health care item or service for which the individual, or person other than the health plan on behalf of the individual, has paid the covered entity in full. Usage Note: Restrictions governed under this regulation meet the definition of an opt out with exception class of consent directive. Opt out is limited to disclosures to a payer for payment and operations purpose of use. See HL7 HIPAA Self-Pay code in ActPrivacyLaw (2.16.840.1.113883.1.11.20426)."),
    "mdhhs-5515": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="mdhhs-5515"),
                   display="Michigan MDHHS-5515 Consent to Share Behavioral Health Information for Care Coordination Purposes")],
        text="On January 1, 2015, the Michigan Department of Health and Human Services (MDHHS) released a standard consent form for the sharing of health information specific to behavioral health and substance use treatment in accordance with Public Act 129 of 2014. In Michigan, while providers are not required to use this new standard form (MDHHS-5515), they are required to accept it. Note: Form is available at http://www.michigan.gov/documents/mdhhs/Consent_to_Share_Behavioral_Health_Information_for_Care_Coordination_Purposes_548835_7.docx For more information see http://www.michigan.gov/documents/mdhhs/Behavioral_Health_Consent_Form_Background_Information_548864_7.pdf"),
    "nyssipp": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="nyssipp"),
                        display="New York State Surgical and Invasive Procedure Protocol")],
        text="The New York State Surgical and Invasive Procedure Protocol (NYSSIPP) applies to all operative and invasive procedures including endoscopy, general surgery or interventional radiology. Other procedures that involve puncture or incision of the skin, or insertion of an instrument or foreign material into the body are within the scope of the protocol. This protocol also applies to those anesthesia procedures either prior to a surgical procedure or independent of a surgical procedure such as spinal facet blocks. Example: Certain 'minor' procedures such as venipuncture, peripheral IV placement, insertion of nasogastric tube and foley catheter insertion are not within the scope of the protocol. From http://www.health.ny.gov/professionals/protocols_and_guidelines/surgical_and_invasive_procedure/nyssipp_faq.htm Note: HHC 100B-1 Form is available at http://www.downstate.edu/emergency_medicine/documents/Consent_CT_with_contrast.pdf"),
    "va-10-0484": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="va-10-0484"),
                   display="VA Form 10-0484")],
        text="VA Form 10-0484 Revocation for Release of Individually-Identifiable Health Information enables a veteran to revoke authorization for the VA to release specified copies of individually-identifiable health information with the non-VA health care provider organizations participating in the eHealth Exchange and partnering with VA. Comment: Opt-in Consent Directive with status = rescinded (aka 'revoked'). Note: Form is available at http://www.va.gov/vaforms/medical/pdf/vha-10-0484-fill.pdf"),
    "va-10-0485": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="va-10-0485"),
                   display="VA Form 10-0485")],
        text="VA Form 10-0485 Request for and Authorization to Release Protected Health Information to eHealth Exchange enables a veteran to request and authorize a VA health care facility to release protected health information (PHI) for treatment purposes only to the communities that are participating in the eHealth Exchange, VLER Directive, and other Health Information Exchanges with who VA has an agreement. This information may consist of the diagnosis of Sickle Cell Anemia, the treatment of or referral for Drug Abuse, treatment of or referral for Alcohol Abuse or the treatment of or testing for infection with Human Immunodeficiency Virus. This authorization covers the diagnoses that I may have upon signing of the authorization and the diagnoses that I may acquire in the future including those protected by 38 U.S.C. 7332. Comment: Opt-in Consent Directive. Note: Form is available at http://www.va.gov/vaforms/medical/pdf/10-0485-fill.pdf"),
    "va-10-5345": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="va-10-5345"),
                   display="VA Form 10-5345")],
        text="VA Form 10-5345 Request for and Authorization to Release Medical Records or Health Information enables a veteran to request and authorize the VA to release specified copies of protected health information (PHI), such as hospital summary or outpatient treatment notes, which may include information about conditions governed under Title 38 Section 7332 (drug abuse, alcoholism or alcohol abuse, testing for or infection with HIV, and sickle cell anemia). Comment: Opt-in Consent Directive. Note: Form is available at http://www.va.gov/vaforms/medical/pdf/vha-10-5345-fill.pdf"),
    "va-10-5345a": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="va-10-5345a"),
                   display="VA Form 10-5345a")],
        text="VA Form 10-5345a Individuals' Request for a Copy of Their Own Health Information enables a veteran to request and authorize the VA to release specified copies of protected health information (PHI), such as hospital summary or outpatient treatment notes. Note: Form is available at http://www.va.gov/vaforms/medical/pdf/vha-10-5345a-fill.pdf"),
    "va-10-5345a-mhv": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes",
                        code=Code(value="va-10-5345a-mhv"),
                        display="VA Form 10-5345a-MHV")],
        text="VA Form 10-5345a-MHV Individual's Request for a Copy of their own health information from MyHealtheVet enables a veteran to receive a copy of all available personal health information to be delivered through the veteran's My HealtheVet account. Note: Form is available at http://www.va.gov/vaforms/medical/pdf/vha-10-5345a-MHV-fill.pdf"),
    "va-10-10116": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="va-10-10116"),
                   display="VA Form 10-10-10116")],
        text="VA Form 10-10116 Revocation of Authorization for Use and Release of Individually Identifiable Health Information for Veterans Health Administration Research. Comment: Opt-in with Restriction Consent Directive with status = 'completed'. Note: Form is available at http://www.northerncalifornia.va.gov/northerncalifornia/services/rnd/docs/vha-10-10116.pdf"),
    "va-21-4142": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="va-21-4142"),
                   display="VA Form 21-4142")],
        text="VA Form 21-4142 (Authorization and Consent to Release Information to the Department of Veterans Affairs (VA) enables a veteran to authorize the US Veterans Administration [VA] to request veteran's health information from non-VA providers. Aka VA Compensation Application Note: Form is available at http://www.vba.va.gov/pubs/forms/VBA-21-4142-ARE.pdf . For additional information regarding VA Form 21-4142, refer to the following website: www.benefits.va.gov/compensation/consent_privateproviders"),
    "ssa-827": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="ssa-827"),
                        display="SSA Authorization to Disclose")],
        text="SA Form SSA-827 (Authorization to Disclose Information to the Social Security Administration (SSA)). Form is available at https://www.socialsecurity.gov/forms/ssa-827-inst-sp.pdf"),
    "dch-3927": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="dch-3927"),
                        display="Michigan behavior and mental health consent")],
        text="Michigan DCH-3927 Consent to Share Behavioral Health Information for Care Coordination Purposes, which combines 42 CFR Part 2 and Michigan Mental Health Code, Act 258 of 1974. Form is available at http://www.michigan.gov/documents/mdch/DCH-3927_Consent_to_Share_Health_Information_477005_7.docx"),
    "squaxin": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="squaxin"),
                        display="Squaxin Indian behavioral health and HIPAA consent")],
        text="Squaxin Indian HIPAA and 42 CFR Part 2 Consent for Release and Exchange of Confidential Information, which permits consenter to select healthcare record type and types of treatment purposes. This consent requires disclosers and recipients to comply with 42 C.F.R. Part 2, and HIPAA 45 C.F.R. parts 160 and 164. It includes patient notice of the refrain policy not to disclose without consent, and revocation rights. https://www.ncsacw.samhsa.gov/files/SI_ConsentForReleaseAndExchange.PDF"),
    "nl-lsp": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="nl-lsp"),
                        display="NL LSP Permission")],
        text="LSP (National Exchange Point) requires that providers, hospitals and pharmacy obtain explicit permission [opt-in] from healthcare consumers to submit and retrieve all or only some of a subject of care’s health information collected by the LSP for purpose of treatment, which can be revoked. Without permission, a provider cannot access LSP information even in an emergency. The LSP provides healthcare consumers with accountings of disclosures. https://www.vzvz.nl/uploaded/FILES/htmlcontent/Formulieren/TOESTEMMINGSFORMULIER.pdf, https://www.ikgeeftoestemming.nl/en, https://www.ikgeeftoestemming.nl/en/registration/find-healthcare-provider"),
    "at-elga": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="at-elga"),
                        display="AT ELGA Opt-in Consent")],
        text="Pursuant to Sec. 2 no. 9 Health Telematics Act 2012, ELGA Health Data ( “ELGA-Gesundheitsdaten”) = Medical documents. Austria opted for an opt-out approach. This means that a person is by default ‘ELGA participant’ unless he/she objects. ELGA participants have the following options: General opt out: No participation in ELGA, Partial opt-out: No participation in a particular ELGA application, e.g. eMedication and Case-specific opt-out: No participation in ELGA only regarding a particular case/treatment. There is the possibility to opt-in again. ELGA participants can also exclude the access of a particular ELGA healthcare provider to a particular piece of or all of their ELGA data. http://ec.europa.eu/health/ehealth/docs/laws_austria_en.pdf"),
    "nih-hipaa": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="nih-hipaa"),
                        display="HHS NIH HIPAA Research Authorization")],
        text="Guidance and template form https://privacyruleandresearch.nih.gov/pdf/authorization.pdf"),
    "nci": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="nci"),
                        display="NCI Cancer Clinical Trial consent")],
        text="see http://ctep.cancer.gov/protocolDevelopment/docs/Informed_Consent_Template.docx"),
    "nih-grdr": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="nih-grdr"),
                        display="NIH Global Rare Disease Patient Registry and Data Repository consent")],
        text="Global Rare Disease Patient Registry and Data Repository (GRDR) consent is an agreement of a healthcare consumer to permit collection, access, use and disclosure of de-identified rare disease information and collection of bio-specimens, medical information, family history and other related information from patients to permit the registry collection of health and genetic information, and specimens for pseudonymized disclosure for research purpose of use. https://rarediseases.info.nih.gov/files/informed_consent_template.pdf"),
    "nih-527": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="nih-527"),
                        display="NIH Authorization for the Release of Medical Information")],
        text="NIH Authorization for the Release of Medical Information is a patient’s consent for the National Institutes of Health Clinical Center to release medical information to care providers, which can be revoked. Note: Consent Form available @ http://cc.nih.gov/participate/_pdf/NIH-527.pdf"),
    "ga4gh": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentpolicycodes", code=Code(value="ga4gh"),
                        display="Population origins and ancestry research consent")],
        text="Global Alliance for Genomic Health Data Sharing Consent Form is an example of the GA4GH Population origins and ancestry research consent form. Consenters agree to permitting a specified research project to collect ancestry and genetic information in controlled-access databases, and to allow other researchers to use deidentified information from those databases. http://www.commonaccord.org/index.php?action=doc&file=Wx/org/genomicsandhealth/REWG/Demo/Roberta_Robinson_US")
}

ConsentProvisionActorCodeableConcept = {
    "AMENDER": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="AMENDER"),
                   display="Amender")],
        text="A person who has corrected, edited, or amended pre-existing information."),
    "COAUTH": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="COAUTH"),
                   display="Co-Author")],
        text="The entity that co-authored content. There can be multiple co-authors of content, which may take such forms as a contract, a healthcare record entry or document, a policy, or a consent directive."),
    "CONT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="CONT"),
                        display="Contact")],
        text="A person or an organization that provides or receives information regarding another entity. Examples; patient NOK and emergency contacts; guarantor contact; employer contact."),
    "EVTWIT": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="EVTWIT"),
                   display="Event Witness")],
        text="A person who attests to observing an occurrence. For example, the witness has observed a procedure and is attesting to this fact."),
    "PRIMAUTH": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="PRIMAUTH"),
                   display="Primary Author")],
        text="An entity that is the primary or sole author of information content. In the healthcare context, there can be only one primary author of health information content in a record entry or document."),
    "REVIEWER": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="REVIEWER"),
                   display="Reviewer")],
        text="A person, device, or algorithm that has used approved criteria for filtered data for inclusion into the patient record. Examples: (1) a medical records clerk who scans a document for inclusion in the medical record, enters header information, or catalogues and classifies the data, or a combination thereof; (2) a gateway that receives data from another computer system and interprets that data or changes its format, or both, before entering it into the patient record."),
    "SOURCE": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="SOURCE"),
                   display="Source")],
        text="An automated data source that generates a signature along with content. Examples: (1) the signature for an image that is generated by a device for inclusion in the patient record; (2) the signature for an ECG derived by an ECG system for inclusion in the patient record; (3) the data from a biomedical monitoring device or system that is for inclusion in the patient record."),
    "TRANS": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="TRANS"),
                   display="Transcriber")],
        text="An entity entering the data into the originating system. This includes the transcriptionist for dictated text transcribed into electronic form."),
    "VALID": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="VALID"),
                   display="Validator")],
        text="A person who validates a health information document for inclusion in the patient record. For example, a medical student or resident is credentialed to perform history or physical examinations and to write progress notes. The attending physician signs the history and physical examination to validate the entry for inclusion in the patient's medical record."),
    "VERF": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/contractsignertypecodes", code=Code(value="VERF"),
                        display="Verifier")],
        text="A person who asserts the correctness and appropriateness of an act or the recording of the act, and is accountable for the assertion that the act or the recording of the act complies with jurisdictional or organizational policy. For example, a physician is required to countersign a verbal order that has previously been recorded in the medical record by a registered nurse who has carried out the verbal order."),
    "AFFL": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="AFFL"),
                        display="affiliate")],
        text="Player of the Affiliate role has a business/professional relationship with scoper. Player and scoper may be persons or organization. The Affiliate relationship does not imply membership in a group, nor does it exist for resource scheduling purposes. Example: A healthcare provider is affiliated with another provider as a business associate."),
    "AGNT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="AGNT"),
                        display="agent")],
        text="An entity (player) that acts or is authorized to act on behalf of another entity (scoper)."),
    "ASSIGNED": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="ASSIGNED"),
                        display="assigned entity")],
        text="An agent role in which the agent is an Entity acting in the employ of an organization. The focus is on functional role on behalf of the organization, unlike the Employee role where the focus is on the 'Human Resources' relationship between the employee and the organization."),
    "CLAIM": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="CLAIM"),
                        display="claimant")],
        text="Description: A role played by a party making a claim for coverage under a policy or program. A claimant must be either a person or organization, or a group of persons or organizations. A claimant is not a named insured or a program eligible. Discussion: With respect to liability insurance such as property and casualty insurance, a claimant must file a claim requesting indemnification for a loss that the claimant considers covered under the policy of a named insured. The claims adjuster for the policy underwriter will review the claim to determine whether the loss meets the benefit coverage criteria under a policy, and base any indemnification or coverage payment on that review. If a third party is liable in whole or part for the loss, the underwriter may pursue third party liability recovery. A claimant may be involved in civil or criminal legal proceedings involving claims against a defendant party that is indemnified by an insurance policy or to protest the finding of a claims adjustor. With respect to life insurance, a beneficiary designated by a named insured becomes a claimant of the proceeds of coverage, as in the case of a life insurance policy. However, a claimant for coverage under life insurance is not necessarily a designated beneficiary. Note: A claimant is not a named insured. However, a named insured may make a claim under a policy, e.g., an insured driver may make a claim for an injury under his or her comprehensive automobile insurance policy. Similarly, a program eligible may make a claim under program, e.g., an unemployed worker may claim benefits under an unemployment insurance program, but parties playing these covered party role classes are not, for purposes of this vocabulary and in an effort to clearly distinguish role classes, considered claimants. In the case of a named insured making a claim, a role type code INSCLM (insured claimant) subtypes the class to indicate that either a named insured or an individual insured has filed a claim for a loss. In the case of a program eligible, a role type code INJWKR (injured worker) subtypes the class to indicate that the covered party in a workers compensation program is an injured worker, and as such, has filed a 'claim' under the program for benefits. Likewise, a covered role type code UNEMP (unemployed worker) subtypes the program eligible class to indicate that the covered party in an unemployment insurance program has filed a claim for unemployment benefits. Example: A claimant under automobile policy that is not the named insured."),
    "COVPTY": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="COVPTY"),
                        display="covered party")],
        text="A role class played by a person who receives benefit coverage under the terms of a particular insurance policy. The underwriter of that policy is the scoping entity. The covered party receives coverage because of some contractual or other relationship with the holder of that policy. Discussion:This reason for coverage is captured in 'Role.code' and a relationship link with type code of indirect authority should be included using the policy holder role as the source, and the covered party role as the target. Note that a particular policy may cover several individuals one of whom may be, but need not be, the policy holder. Thus the notion of covered party is a role that is distinct from that of the policy holder."),
    "DEPEN": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="DEPEN"),
                        display="dependent")],
        text="Description: A role played by a person covered under a policy or program based on an association with a subscriber, which is recognized by the policy holder. Note: The party playing the role of a dependent is not a claimant in the sense conveyed by the RoleClassCoveredParty CLAIM (claimant). However, a dependent may make a claim under a policy, e.g., a dependent under a health insurance policy may become the claimant for coverage under that policy for wellness examines or if injured and there is no liable third party. In the case of a dependent making a claim, a role type code INSCLM (insured claimant) subtypes the class to indicate that the dependent has filed a claim for services covered under the health insurance policy. Example: The dependent has an association with the subscriber such as a financial dependency or personal relationship such as that of a spouse, or a natural or adopted child. The policy holder may be required by law to recognize certain associations or may have discretion about the associations. For example, a policy holder may dictate the criteria for the dependent status of adult children who are students, such as requiring full time enrollment, or may recognize domestic partners as dependents. Under certain circumstances, the dependent may be under the indirect authority of a responsible party acting as a surrogate for the subscriber, for example, if the subscriber is differently abled or deceased, a guardian ad Lidem or estate executor may be appointed to assume the subscriberaTMs legal standing in the relationship with the dependent."),
    "ECON": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="ECON"),
                        display="emergency contact")],
        text="An entity to be contacted in the event of an emergency."),
    "EMP": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="EMP"),
                        display="employee")],
        text="A relationship between a person or organization and a person or organization formed for the purpose of exchanging work for compensation. The purpose of the role is to identify the type of relationship the employee has to the employer, rather than the nature of the work actually performed. (Contrast with AssignedEntity.)"),
    "GUARD": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="GUARD"),
                        display="guardian")],
        text="Guardian of a ward"),
    "INVSBJ": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="INVSBJ"),
                        display="Investigation Subject")],
        text="An entity that is the subject of an investigation. This role is scoped by the party responsible for the investigation."),
    "NAMED": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="NAMED"),
                        display="named insured")],
        text="Description: A role played by a party to an insurance policy to which the insurer agrees to indemnify for losses, provides benefits for, or renders services. A named insured may be either a person, non-person living subject, or an organization, or a group of persons, non-person living subjects, or organizations. Discussion: The coded concept NAMED should not be used where a more specific child concept in this Specializable value set applies. In some cases, the named insured may not be the policy holder, e.g., where a policy holder purchases life insurance policy in which another party is the named insured and the policy holder is the beneficiary of the policy. Note: The party playing the role of a named insured is not a claimant in the sense conveyed by the RoleClassCoveredParty CLAIM (claimant). However, a named insured may make a claim under a policy, e.g., e.g., a party that is the named insured and policy holder under a comprehensive automobile insurance policy may become the claimant for coverage under that policy e.g., if injured in an automobile accident and there is no liable third party. In the case of a named insured making a claim, a role type code INSCLM (insured claimant) subtypes the class to indicate that a named insured has filed a claim for a loss. Example: The named insured under a comprehensive automobile, disability, or property and casualty policy that is the named insured and may or may not be the policy holder."),
    "NOK": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="NOK"),
                        display="next of kin")],
        text="An individual designated for notification as the next of kin for a given entity."),
    "PAT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="PAT"),
                        display="patient")],
        text="A Role of a LivingSubject (player) as an actual or potential recipient of health care services from a healthcare provider organization (scoper). Usage Note: Communication about relationships between patients and specific healthcare practitioners (people) is not done via scoper. Instead this is generally done using the CareProvision act. This allows linkage between patient and a particular healthcare practitioner role and also allows description of the type of care involved in the relationship."),
    "PROV": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="PROV"),
                        display="healthcare provider")],
        text="An Entity (player) that is authorized to provide health care services by some authorizing agency (scoper)."),
    "NOT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleClass", code=Code(value="NOT"),
                        display="notary public")],
        text="notary public"),
    "CLASSIFIER": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CLASSIFIER"),
                        display="classifier")],
        text="An individual authorized to assign an original classification to information, including compilations of unclassified information, based on a determination that the information requires protection against unauthorized disclosure. The individual marks the information with immutable, computable, and human readable security labels in accordance with applicable security labeling policies. The labeling policies provide instructions on whether and if so how the security labels may be later reclassified [i.e., upgraded, downgraded, used in derivative classification, or declassified] in a manner that preserves the overridden original classification binding and provenance."),
    "CONSENTER": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CONSENTER"),
                        display="consenter")],
        text="An entity or an entity's delegatee who is the grantee in an agreement such as a consent for services, advanced directive, or a privacy consent directive in accordance with jurisdictional, organizational, or patient policy."),
    "CONSWIT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CONSWIT"),
                        display="consent witness")],
        text="An entity which has witnessed and attests to observing another entity being counseled about an agreement such as a consent for services, advanced directive, or a privacy consent directive."),
    "COPART": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="COPART"),
                        display="co-participant")],
        text="An entity which participates in the generation of and attest to veracity of content, but is not an author or coauthor. For example a surgeon who is required by institutional, regulatory, or legal rules to sign an operative report, but who was not involved in the authorship of that report."),
    "DECLASSIFIER": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="DECLASSIFIER"),
                        display="declassifier")],
        text="An individual which is authorized to declassify information based on a determination that the information no longer requires protection against unauthorized disclosure. The individual marks the information being declassified using computable and human readable security labels indicating that this is copy of previously classified information is unclassified in accordance with applicable security labeling policies. The labeling policies provide instructions on whether and if so how the security labels may be later reclassified [i.e., upgraded or used in derivative classification] in a manner that preserves the overridden original classification binding and provenance."),
    "DELEGATEE": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="DELEGATEE"),
                        display="delegatee")],
        text="A party to whom some right or authority is granted by a delegator."),
    "DELEGATOR": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="DELEGATOR"),
                        display="delegator")],
        text="A party that grants all or some portion its right or authority to another party."),
    "DOWNGRDER": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="DOWNGRDER"),
                        display="downgrader")],
        text="An individual authorized to lower the classification level of labeled content and provide rationale for doing so as directed by a classification guide."),
    "DPOWATT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="DPOWATT"),
                        display="durable power of attorney")],
        text="A relationship between two people in which one person authorizes another, usually a family member or relative, to act for him or her in a manner which is a legally binding upon the person giving such authority as if he or she personally were to do the acts that is often limited in the kinds of powers that can be assigned. Unlike ordinary powers of attorney, durable powers can survive for long periods of time, and again, unlike standard powers of attorney, durable powers can continue after incompetency."),
    "EXCEST": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="EXCEST"),
                        display="executor of estate")],
        text="The role played by a person acting as the estate executor for a deceased subscriber or policyholder who was the responsible party"),
    "GRANTEE": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="GRANTEE"),
                        display="grantee")],
        text="An entity which accepts certain rights or authority from a grantor."),
    "GRANTOR": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="GRANTOR"),
                        display="grantor")],
        text="An entity which agrees to confer certain rights or authority to a grantee."),
    "GT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="GT"),
                        display="Guarantor")],
        text="An individual or organization that makes or gives a promise, assurance, pledge to pay or has paid the healthcare service provider."),
    "GUADLTM": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="GUADLTM"),
                        display="guardian ad lidem")],
        text="The role played by a person appointed by the court to look out for the best interests of a minor child during the course of legal proceedings."),
    "HPOWATT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="HPOWATT"),
                        display="healthcare power of attorney")],
        text="A relationship between two people in which one person authorizes another to act for him or her in a manner which is a legally binding upon the person giving such authority as if he or she personally were to do the acts that continues (by its terms) to be effective even though the grantor has become mentally incompetent after signing the document."),
    "INTPRTER": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="INTPRTER"),
                        display="interpreter")],
        text="An entity which converts spoken or written language into the language of key participants in an event such as when a provider is obtaining a patient's consent to treatment or permission to disclose information."),
    "POWATT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="POWATT"),
                        display="power of attorney")],
        text="A relationship between two people in which one person authorizes another to act for him in a manner which is a legally binding upon the person giving such authority as if he or she personally were to do the acts."),
    "RESPRSN": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="RESPRSN"),
                        display="responsible party")],
        text="The role played by a party who has legal responsibility for another party."),
    "SPOWATT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="SPOWATT"),
                        display="special power of attorney")],
        text="A relationship between two people in which one person authorizes another to act for him or her in a manner which is a legally binding upon the person giving such authority as if he or she personally were to do the acts that is often limited in the kinds of powers that can be assigned."),
    "_CitizenRoleType": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="_CitizenRoleType"),
                        display="CitizenRoleType")],
        text="A role type used to qualify a person's legal status within a country or nation."),
    "CAS": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CAS"),
                        display="asylum seeker")],
        text="A person who has fled his or her home country to find a safe place elsewhere."),
    "CASM": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CASM"),
                        display="single minor asylum seeker")],
        text="A person who is someone of below legal age who has fled his or her home country, without his or her parents, to find a safe place elsewhere at time of categorization."),
    "CN": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CN"),
                        display="national")],
        text="A person who is legally recognized as a member of a nation or country, with associated rights and obligations."),
    "CNRP": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CNRP"),
                        display="non-country member without residence permit")],
        text="A foreigner who is present in a country (which is foreign to him/her) unlawfully or without the country's authorization (may be called an illegal alien)."),
    "CNRPM": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CNRPM"),
                        display="non-country member minor without residence permit")],
        text="A person who is below legal age present in a country, without his or her parents, (which is foreign to him/her) unlawfully or without the country's authorization."),
    "CPCA": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CPCA"),
                        display="permit card applicant")],
        text="A non-country member admitted to the territory of a nation or country as a non-resident for an explicit purpose."),
    "CRP": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CRP"),
                        display="non-country member with residence permit")],
        text="A foreigner who is a resident of the country but does not have citizenship."),
    "CRPM": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-RoleCode", code=Code(value="CRPM"),
                        display="non-country member minor with residence permit")],
        text="A person who is a resident below legal age of the country without his or her parents and does not have citizenship."),
    "AUCG": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationFunction", code=Code(value="AUCG"),
                   display="caregiver information receiver")],
        text="Description:Caregiver authorized to receive patient health information."),
    "AULR": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationFunction", code=Code(value="AULR"),
                   display="legitimate relationship information receiver")],
        text="Description:Provider with legitimate relationship authorized to receive patient health information."),
    "AUTM": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationFunction", code=Code(value="AUTM"),
                   display="care team information receiver")],
        text="Description:Member of care team authorized to receive patient health information."),
    "AUWA": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationFunction", code=Code(value="AUWA"),
                   display="work area information receiver")],
        text="Description:Entities within specified work area authorized to receive patient health information."),
    "PROMSK": CodeableConcept(
        codings=[
            Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationFunction", code=Code(value="PROMSK"),
                   display="authorized provider masking author")],
        text="Definition:Provider authorized to mask information to protect the patient, a third party, or to ensure that the provider has consulted with the patient prior to release of this information."),
    "AUT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationType", code=Code(value="AUT"),
                        display="author (originator)")],
        text="Definition: A party that originates the Act and therefore has responsibility for the information given in the Act and ownership of this Act. Example: the report writer, the person writing the act definition, the guideline author, the placer of an order, the EKG cart (device) creating a report etc. Every Act should have an author. Authorship is regardless of mood always actual authorship. Examples of such policies might include: The author and anyone they explicitly delegate may update the report; All administrators within the same clinic may cancel and reschedule appointments created by other administrators within that clinic; A party that is neither an author nor a party who is extended authorship maintenance rights by policy, may only amend, reverse, override, replace, or follow up in other ways on this Act, whereby the Act remains intact and is linked to another Act authored by that other party."),
    "CST": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationType", code=Code(value="CST"),
                        display="custodian")],
        text="An entity (person, organization or device) that is in charge of maintaining the information of this act (e.g., who maintains the report or the master service catalog item, etc.)."),
    "INF": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationType", code=Code(value="INF"),
                        display="informant")],
        text="A source of reported information (e.g., a next of kin who answers questions about the patient's history). For history questions, the patient is logically an informant, yet the informant of history questions is implicitly the subject."),
    "IRCP": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationType", code=Code(value="IRCP"),
                        display="information recipient")],
        text="A party, who may or should receive or who has recieved the Act or subsequent or derivative information of that Act. Information recipient is inert, i.e., independent of mood. Rationale: this is a generalization of a too diverse family that the definition can't be any more specific, and the concept is abstract so one of the specializations should be used."),
    "LA": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationType", code=Code(value="LA"),
                        display="legal authenticator")],
        text="A verifier who legally authenticates the accuracy of an act. An example would be a staff physician who sees a patient and dictates a note, then later signs it. Their signature constitutes a legal authentication."),
    "TRC": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationType", code=Code(value="TRC"),
                        display="tracker")],
        text="A secondary information recipient, who receives copies (e.g., a primary care provider receiving copies of results as ordered by specialist)."),
    "WIT": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/v3-ParticipationType", code=Code(value="WIT"),
                        display="witness")],
        text="Only with service events. A person witnessing the action happening without doing anything. A witness is not necessarily aware, much less approves of anything stated in the service event. Example for a witness is students watching an operation or an advanced directive witness."),
    "authserver": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/extra-security-role-type",
                        code=Code(value="authserver"),
                        display="authorization server")],
        text="An entity providing authorization services to enable the electronic sharing of health-related information based on resource owner's preapproved permissions. For example, an UMA Authorization Server[UMA]"),
    "datacollector": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/extra-security-role-type",
                        code=Code(value="datacollector"),
                        display="data collector")],
        text="An entity that collects information over which the data subject may have certain rights under policy or law to control that information's management and distribution by data collectors, including the right to access, retrieve, distribute, or delete that information."),
    "dataprocessor": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/extra-security-role-type",
                        code=Code(value="dataprocessor"),
                        display="data processor")],
        text="An entity that processes collected information over which the data subject may have certain rights under policy or law to control that information's management and distribution by data processors, including the right to access, retrieve, distribute, or delete that information."),
    "datasubject": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/extra-security-role-type",
                        code=Code(value="datasubject"),
                        display="data subject")],
        text="A person whose personal information is collected or processed, and who may have certain rights under policy or law to control that information's management and distribution by data collectors or processors, including the right to access, retrieve, distribute, or delete that information."),
    "humanuser": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/extra-security-role-type",
                        code=Code(value="humanuser"),
                        display="human user")],
        text="The human user that has participated."),
    "110150": CodeableConcept(
        codings=[Coding(system="http://dicom.nema.org/resources/ontology/DCM", code=Code(value="110150"),
                        display="Application")],
        text="Audit participant role ID of software application"),
    "110151": CodeableConcept(
        codings=[Coding(system="http://dicom.nema.org/resources/ontology/DCM", code=Code(value="110151"),
                        display="Application Launcher")],
        text="Audit participant role ID of software application launcher, i.e., the entity that started or stopped an application"),
    "110152": CodeableConcept(
        codings=[Coding(system="http://dicom.nema.org/resources/ontology/DCM", code=Code(value="110152"),
                        display="Destination Role ID")],
        text="Audit participant role ID of the receiver of data"),
    "110153": CodeableConcept(
        codings=[Coding(system="http://dicom.nema.org/resources/ontology/DCM", code=Code(value="110153"),
                        display="Source Role ID")],
        text="Audit participant role ID of the sender of data"),
    "110154": CodeableConcept(
        codings=[Coding(system="http://dicom.nema.org/resources/ontology/DCM", code=Code(value="110154"),
                        display="Destination Media")],
        text="Audit participant role ID of media receiving data during an export"),
    "110155": CodeableConcept(
        codings=[Coding(system="http://dicom.nema.org/resources/ontology/DCM", code=Code(value="110155"),
                        display="Source Media")],
        text="Audit participant role ID of media providing data during an import")
}

ConsentProvisionActionCodeableConcept = {
    "collect": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentaction", code=Code(value="collect"),
                        display="Collect")],
        text="Gather retrieved information for storage"),
    "access": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentaction", code=Code(value="access"),
                        display="Access")],
        text="	Retrieval without permitting collection, use or disclosure. e.g., no screen-scraping for collection, use or disclosure (view-only access)"),
    "use": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentaction", code=Code(value="use"),
                        display="Use")],
        text="Utilize the retrieved information"),
    "disclose": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentaction", code=Code(value="disclose"),
                        display="Disclose")],
        text="Transfer retrieved information"),
    "correct": CodeableConcept(
        codings=[Coding(system="http://terminology.hl7.org/CodeSystem/consentaction", code=Code(value="correct"),
                        display="Access and Correct")],
        text="Allow retrieval of a patient's information for the purpose of update or rectify"),
}
