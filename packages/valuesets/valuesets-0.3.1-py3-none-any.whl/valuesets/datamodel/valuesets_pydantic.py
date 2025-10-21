"""
Generated Pydantic models with rich enum support.

This module was automatically generated from a LinkML schema.
It includes enums with full metadata support (descriptions, meanings, annotations).
"""

from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

# Import our rich enum support
from valuesets.generators.rich_enum import RichEnum

metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    pass


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'valuesets', 'description': 'A collection of commonly used value sets', 'id': 'https://w3id.org/linkml/valuesets', 'name': 'valuesets', 'title': 'valuesets'})

class RelativeTimeEnum(RichEnum):
    # Enum members
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    AT_SAME_TIME_AS = "AT_SAME_TIME_AS"

# Set metadata after class creation to avoid it becoming an enum member
RelativeTimeEnum._metadata = {
}

class PresenceEnum(RichEnum):
    # Enum members
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    BELOW_DETECTION_LIMIT = "BELOW_DETECTION_LIMIT"
    ABOVE_DETECTION_LIMIT = "ABOVE_DETECTION_LIMIT"

# Set metadata after class creation to avoid it becoming an enum member
PresenceEnum._metadata = {
    "PRESENT": {'description': 'The entity is present'},
    "ABSENT": {'description': 'The entity is absent'},
    "BELOW_DETECTION_LIMIT": {'description': 'The entity is below the detection limit'},
    "ABOVE_DETECTION_LIMIT": {'description': 'The entity is above the detection limit'},
}

class ContributorType(RichEnum):
    """
    The type of contributor being represented.
    """
    # Enum members
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"

# Set metadata after class creation to avoid it becoming an enum member
ContributorType._metadata = {
    "PERSON": {'description': 'A person.', 'meaning': 'NCIT:C25190'},
    "ORGANIZATION": {'description': 'An organization.', 'meaning': 'NCIT:C41206', 'aliases': ['Institution']},
}

class DataAbsentEnum(RichEnum):
    """
    Used to specify why the normally expected content of the data element is missing.
    """
    # Enum members
    UNKNOWN = "unknown"
    ASKED_UNKNOWN = "asked-unknown"
    TEMP_UNKNOWN = "temp-unknown"
    NOT_ASKED = "not-asked"
    ASKED_DECLINED = "asked-declined"
    MASKED = "masked"
    NOT_APPLICABLE = "not-applicable"
    UNSUPPORTED = "unsupported"
    AS_TEXT = "as-text"
    ERROR = "error"
    NOT_A_NUMBER = "not-a-number"
    NEGATIVE_INFINITY = "negative-infinity"
    POSITIVE_INFINITY = "positive-infinity"
    NOT_PERFORMED = "not-performed"
    NOT_PERMITTED = "not-permitted"

# Set metadata after class creation to avoid it becoming an enum member
DataAbsentEnum._metadata = {
    "UNKNOWN": {'description': 'The value is expected to exist but is not known.', 'meaning': 'fhir_data_absent_reason:unknown'},
    "ASKED_UNKNOWN": {'description': 'The source was asked but does not know the value.', 'meaning': 'fhir_data_absent_reason:asked-unknown'},
    "TEMP_UNKNOWN": {'description': 'There is reason to expect (from the workflow) that the value may become known.', 'meaning': 'fhir_data_absent_reason:temp-unknown'},
    "NOT_ASKED": {'description': "The workflow didn't lead to this value being known.", 'meaning': 'fhir_data_absent_reason:not-asked'},
    "ASKED_DECLINED": {'description': 'The source was asked but declined to answer.', 'meaning': 'fhir_data_absent_reason:asked-declined'},
    "MASKED": {'description': 'The information is not available due to security, privacy or related reasons.', 'meaning': 'fhir_data_absent_reason:masked'},
    "NOT_APPLICABLE": {'description': 'There is no proper value for this element (e.g. last menstrual period for a male).', 'meaning': 'fhir_data_absent_reason:not-applicable'},
    "UNSUPPORTED": {'description': "The source system wasn't capable of supporting this element.", 'meaning': 'fhir_data_absent_reason:unsupported'},
    "AS_TEXT": {'description': 'The content of the data is represented in the resource narrative.', 'meaning': 'fhir_data_absent_reason:as-text'},
    "ERROR": {'description': 'Some system or workflow process error means that the information is not available.', 'meaning': 'fhir_data_absent_reason:error'},
    "NOT_A_NUMBER": {'description': 'The numeric value is undefined or unrepresentable due to a floating point processing error.', 'meaning': 'fhir_data_absent_reason:not-a-number'},
    "NEGATIVE_INFINITY": {'description': 'The numeric value is excessively low and unrepresentable due to a floating point processing        error.', 'meaning': 'fhir_data_absent_reason:negative-infinity'},
    "POSITIVE_INFINITY": {'description': 'The numeric value is excessively high and unrepresentable due to a floating point processing        error.', 'meaning': 'fhir_data_absent_reason:positive-infinity'},
    "NOT_PERFORMED": {'description': 'The value is not available because the observation procedure (test, etc.) was not performed.', 'meaning': 'fhir_data_absent_reason:not-performed'},
    "NOT_PERMITTED": {'description': 'The value is not permitted in this context (e.g. due to profiles, or the base data types).', 'meaning': 'fhir_data_absent_reason:not-permitted'},
}

class PredictionOutcomeType(RichEnum):
    # Enum members
    TP = "TP"
    FP = "FP"
    TN = "TN"
    FN = "FN"

# Set metadata after class creation to avoid it becoming an enum member
PredictionOutcomeType._metadata = {
    "TP": {'description': 'True Positive'},
    "FP": {'description': 'False Positive'},
    "TN": {'description': 'True Negative'},
    "FN": {'description': 'False Negative'},
}

class VitalStatusEnum(RichEnum):
    """
    The vital status of a person or organism
    """
    # Enum members
    ALIVE = "ALIVE"
    DECEASED = "DECEASED"
    UNKNOWN = "UNKNOWN"
    PRESUMED_ALIVE = "PRESUMED_ALIVE"
    PRESUMED_DECEASED = "PRESUMED_DECEASED"

# Set metadata after class creation to avoid it becoming an enum member
VitalStatusEnum._metadata = {
    "ALIVE": {'description': 'The person is living', 'meaning': 'NCIT:C37987'},
    "DECEASED": {'description': 'The person has died', 'meaning': 'NCIT:C28554'},
    "UNKNOWN": {'description': 'The vital status is not known', 'meaning': 'NCIT:C17998'},
    "PRESUMED_ALIVE": {'description': 'The person is presumed to be alive based on available information'},
    "PRESUMED_DECEASED": {'description': 'The person is presumed to be deceased based on available information'},
}

class VaccinationStatusEnum(RichEnum):
    """
    The vaccination status of an individual
    """
    # Enum members
    VACCINATED = "VACCINATED"
    NOT_VACCINATED = "NOT_VACCINATED"
    FULLY_VACCINATED = "FULLY_VACCINATED"
    PARTIALLY_VACCINATED = "PARTIALLY_VACCINATED"
    BOOSTER = "BOOSTER"
    UNVACCINATED = "UNVACCINATED"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
VaccinationStatusEnum._metadata = {
    "VACCINATED": {'description': 'A status indicating that an individual has received a vaccination', 'meaning': 'NCIT:C28385'},
    "NOT_VACCINATED": {'description': 'A status indicating that an individual has not received any of the required vaccinations', 'meaning': 'NCIT:C183125'},
    "FULLY_VACCINATED": {'description': 'A status indicating that an individual has received all the required vaccinations', 'meaning': 'NCIT:C183123'},
    "PARTIALLY_VACCINATED": {'description': 'A status indicating that an individual has received some of the required vaccinations', 'meaning': 'NCIT:C183124'},
    "BOOSTER": {'description': 'A status indicating that an individual has received a booster vaccination', 'meaning': 'NCIT:C28320'},
    "UNVACCINATED": {'description': 'An organismal quality that indicates an organism is unvaccinated with any vaccine', 'meaning': 'VO:0001377'},
    "UNKNOWN": {'description': 'The vaccination status is not known', 'meaning': 'NCIT:C17998'},
}

class VaccinationPeriodicityEnum(RichEnum):
    """
    The periodicity or frequency of vaccination
    """
    # Enum members
    SINGLE_DOSE = "SINGLE_DOSE"
    ANNUAL = "ANNUAL"
    SEASONAL = "SEASONAL"
    BOOSTER = "BOOSTER"
    PRIMARY_SERIES = "PRIMARY_SERIES"
    PERIODIC = "PERIODIC"
    ONE_TIME = "ONE_TIME"
    AS_NEEDED = "AS_NEEDED"

# Set metadata after class creation to avoid it becoming an enum member
VaccinationPeriodicityEnum._metadata = {
    "SINGLE_DOSE": {'description': 'A vaccination regimen requiring only one dose'},
    "ANNUAL": {'description': 'Vaccination occurring once per year', 'meaning': 'NCIT:C54647'},
    "SEASONAL": {'description': 'Vaccination occurring seasonally (e.g., for influenza)'},
    "BOOSTER": {'description': 'A second or later vaccine dose to maintain immune response', 'meaning': 'NCIT:C28320'},
    "PRIMARY_SERIES": {'description': 'The initial series of vaccine doses'},
    "PERIODIC": {'description': 'Vaccination occurring at regular intervals'},
    "ONE_TIME": {'description': 'A vaccination given only once in a lifetime'},
    "AS_NEEDED": {'description': 'Vaccination given as needed based on exposure risk or other factors'},
}

class VaccineCategoryEnum(RichEnum):
    """
    The broad category or type of vaccine
    """
    # Enum members
    LIVE_ATTENUATED_VACCINE = "LIVE_ATTENUATED_VACCINE"
    INACTIVATED_VACCINE = "INACTIVATED_VACCINE"
    CONJUGATE_VACCINE = "CONJUGATE_VACCINE"
    MRNA_VACCINE = "MRNA_VACCINE"
    DNA_VACCINE = "DNA_VACCINE"
    PEPTIDE_VACCINE = "PEPTIDE_VACCINE"
    VIRAL_VECTOR = "VIRAL_VECTOR"
    SUBUNIT = "SUBUNIT"
    TOXOID = "TOXOID"
    RECOMBINANT = "RECOMBINANT"

# Set metadata after class creation to avoid it becoming an enum member
VaccineCategoryEnum._metadata = {
    "LIVE_ATTENUATED_VACCINE": {'description': 'A vaccine made from microbes that have been weakened in the laboratory', 'meaning': 'VO:0000367'},
    "INACTIVATED_VACCINE": {'description': 'A preparation of killed microorganisms intended to prevent infectious disease', 'meaning': 'NCIT:C29694'},
    "CONJUGATE_VACCINE": {'description': 'A vaccine created by covalently attaching an antigen to a carrier protein', 'meaning': 'NCIT:C1455'},
    "MRNA_VACCINE": {'description': 'A vaccine based on mRNA that encodes the antigen of interest', 'meaning': 'NCIT:C172787'},
    "DNA_VACCINE": {'description': 'A vaccine using DNA to produce protein that promotes immune responses', 'meaning': 'NCIT:C39619'},
    "PEPTIDE_VACCINE": {'description': 'A vaccine based on synthetic peptides', 'meaning': 'NCIT:C1752'},
    "VIRAL_VECTOR": {'description': 'A vaccine using a modified virus as a delivery system'},
    "SUBUNIT": {'description': 'A vaccine containing purified pieces of the pathogen'},
    "TOXOID": {'description': 'A vaccine made from a toxin that has been made harmless'},
    "RECOMBINANT": {'description': 'A vaccine produced using recombinant DNA technology'},
}

class HealthcareEncounterClassification(RichEnum):
    # Enum members
    INPATIENT_VISIT = "Inpatient Visit"
    EMERGENCY_ROOM_VISIT = "Emergency Room Visit"
    EMERGENCY_ROOM_AND_INPATIENT_VISIT = "Emergency Room and Inpatient Visit"
    NON_HOSPITAL_INSTITUTION_VISIT = "Non-hospital institution Visit"
    OUTPATIENT_VISIT = "Outpatient Visit"
    HOME_VISIT = "Home Visit"
    TELEHEALTH_VISIT = "Telehealth Visit"
    PHARMACY_VISIT = "Pharmacy Visit"
    LABORATORY_VISIT = "Laboratory Visit"
    AMBULANCE_VISIT = "Ambulance Visit"
    CASE_MANAGEMENT_VISIT = "Case Management Visit"

# Set metadata after class creation to avoid it becoming an enum member
HealthcareEncounterClassification._metadata = {
    "INPATIENT_VISIT": {'description': 'Person visiting hospital, at a Care Site, in bed, for duration of more than one day, with physicians and other Providers permanently available to deliver service around the clock'},
    "EMERGENCY_ROOM_VISIT": {'description': 'Person visiting dedicated healthcare institution for treating emergencies, at a Care Site, within one day, with physicians and Providers permanently available to deliver service around the clock'},
    "EMERGENCY_ROOM_AND_INPATIENT_VISIT": {'description': 'Person visiting ER followed by a subsequent Inpatient Visit, where Emergency department is part of hospital, and transition from the ER to other hospital departments is undefined'},
    "NON_HOSPITAL_INSTITUTION_VISIT": {'description': 'Person visiting dedicated institution for reasons of poor health, at a Care Site, long-term or permanently, with no physician but possibly other Providers permanently available to deliver service around the clock'},
    "OUTPATIENT_VISIT": {'description': 'Person visiting dedicated ambulatory healthcare institution, at a Care Site, within one day, without bed, with physicians or medical Providers delivering service during Visit'},
    "HOME_VISIT": {'description': 'Provider visiting Person, without a Care Site, within one day, delivering service'},
    "TELEHEALTH_VISIT": {'description': 'Patient engages with Provider through communication media'},
    "PHARMACY_VISIT": {'description': 'Person visiting pharmacy for dispensing of Drug, at a Care Site, within one day'},
    "LABORATORY_VISIT": {'description': 'Patient visiting dedicated institution, at a Care Site, within one day, for the purpose of a Measurement.'},
    "AMBULANCE_VISIT": {'description': 'Person using transportation service for the purpose of initiating one of the other Visits, without a Care Site, within one day, potentially with Providers accompanying the Visit and delivering service'},
    "CASE_MANAGEMENT_VISIT": {'description': 'Person interacting with healthcare system, without a Care Site, within a day, with no Providers involved, for administrative purposes'},
}

class EducationLevel(RichEnum):
    """
    Years of education that a person has completed
    """
    # Enum members
    ELEM = "ELEM"
    SEC = "SEC"
    HS = "HS"
    SCOL = "SCOL"
    ASSOC = "ASSOC"
    BD = "BD"
    PB = "PB"
    GD = "GD"
    POSTG = "POSTG"

# Set metadata after class creation to avoid it becoming an enum member
EducationLevel._metadata = {
    "ELEM": {'description': 'Elementary School', 'meaning': 'HL7:v3-EducationLevel#ELEM'},
    "SEC": {'description': 'Some secondary or high school education', 'meaning': 'HL7:v3-EducationLevel#SEC'},
    "HS": {'description': 'High School or secondary school degree complete', 'meaning': 'HL7:v3-EducationLevel#HS'},
    "SCOL": {'description': 'Some College education', 'meaning': 'HL7:v3-EducationLevel#SCOL'},
    "ASSOC": {'description': "Associate's or technical degree complete", 'meaning': 'HL7:v3-EducationLevel#ASSOC'},
    "BD": {'description': 'College or baccalaureate degree complete', 'meaning': 'HL7:v3-EducationLevel#BD'},
    "PB": {'description': 'Some post-baccalaureate education', 'meaning': 'HL7:v3-EducationLevel#PB'},
    "GD": {'description': 'Graduate or professional Degree complete', 'meaning': 'HL7:v3-EducationLevel#GD'},
    "POSTG": {'description': 'Doctoral or post graduate education', 'meaning': 'HL7:v3-EducationLevel#POSTG'},
}

class MaritalStatus(RichEnum):
    """
    The domestic partnership status of a person
    """
    # Enum members
    ANNULLED = "ANNULLED"
    DIVORCED = "DIVORCED"
    INTERLOCUTORY = "INTERLOCUTORY"
    LEGALLY_SEPARATED = "LEGALLY_SEPARATED"
    MARRIED = "MARRIED"
    COMMON_LAW = "COMMON_LAW"
    POLYGAMOUS = "POLYGAMOUS"
    DOMESTIC_PARTNER = "DOMESTIC_PARTNER"
    UNMARRIED = "UNMARRIED"
    NEVER_MARRIED = "NEVER_MARRIED"
    WIDOWED = "WIDOWED"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
MaritalStatus._metadata = {
    "ANNULLED": {'description': 'Marriage contract has been declared null and to not have existed', 'meaning': 'HL7:marital-status#A'},
    "DIVORCED": {'description': 'Marriage contract has been declared dissolved and inactive', 'meaning': 'HL7:marital-status#D'},
    "INTERLOCUTORY": {'description': 'Subject to an Interlocutory Decree', 'meaning': 'HL7:marital-status#I'},
    "LEGALLY_SEPARATED": {'description': 'Legally Separated', 'meaning': 'HL7:marital-status#L'},
    "MARRIED": {'description': 'A current marriage contract is active', 'meaning': 'HL7:marital-status#M'},
    "COMMON_LAW": {'description': "Marriage recognized in some jurisdictions based on parties' agreement", 'meaning': 'HL7:marital-status#C'},
    "POLYGAMOUS": {'description': 'More than 1 current spouse', 'meaning': 'HL7:marital-status#P'},
    "DOMESTIC_PARTNER": {'description': 'Person declares that a domestic partner relationship exists', 'meaning': 'HL7:marital-status#T'},
    "UNMARRIED": {'description': 'Currently not in a marriage contract', 'meaning': 'HL7:marital-status#U'},
    "NEVER_MARRIED": {'description': 'No marriage contract has ever been entered', 'meaning': 'HL7:marital-status#S'},
    "WIDOWED": {'description': 'The spouse has died', 'meaning': 'HL7:marital-status#W'},
    "UNKNOWN": {'description': 'A proper value is applicable, but not known', 'meaning': 'HL7:marital-status#UNK'},
}

class EmploymentStatus(RichEnum):
    """
    Employment status of a person
    """
    # Enum members
    FULL_TIME_EMPLOYED = "FULL_TIME_EMPLOYED"
    PART_TIME_EMPLOYED = "PART_TIME_EMPLOYED"
    UNEMPLOYED = "UNEMPLOYED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    RETIRED = "RETIRED"
    ACTIVE_MILITARY = "ACTIVE_MILITARY"
    CONTRACT = "CONTRACT"
    PER_DIEM = "PER_DIEM"
    LEAVE_OF_ABSENCE = "LEAVE_OF_ABSENCE"
    OTHER = "OTHER"
    TEMPORARILY_UNEMPLOYED = "TEMPORARILY_UNEMPLOYED"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
EmploymentStatus._metadata = {
    "FULL_TIME_EMPLOYED": {'description': 'Full time employed', 'meaning': 'HL7:v2-0066#1'},
    "PART_TIME_EMPLOYED": {'description': 'Part time employed', 'meaning': 'HL7:v2-0066#2'},
    "UNEMPLOYED": {'description': 'Unemployed', 'meaning': 'HL7:v2-0066#3'},
    "SELF_EMPLOYED": {'description': 'Self-employed', 'meaning': 'HL7:v2-0066#4'},
    "RETIRED": {'description': 'Retired', 'meaning': 'HL7:v2-0066#5'},
    "ACTIVE_MILITARY": {'description': 'On active military duty', 'meaning': 'HL7:v2-0066#6'},
    "CONTRACT": {'description': 'Contract, per diem', 'meaning': 'HL7:v2-0066#C'},
    "PER_DIEM": {'description': 'Per Diem', 'meaning': 'HL7:v2-0066#D'},
    "LEAVE_OF_ABSENCE": {'description': 'Leave of absence', 'meaning': 'HL7:v2-0066#L'},
    "OTHER": {'description': 'Other', 'meaning': 'HL7:v2-0066#O'},
    "TEMPORARILY_UNEMPLOYED": {'description': 'Temporarily unemployed', 'meaning': 'HL7:v2-0066#T'},
    "UNKNOWN": {'description': 'Unknown', 'meaning': 'HL7:v2-0066#9'},
}

class HousingStatus(RichEnum):
    """
    Housing status of patients per UDS Plus HRSA standards
    """
    # Enum members
    HOMELESS_SHELTER = "HOMELESS_SHELTER"
    TRANSITIONAL = "TRANSITIONAL"
    DOUBLING_UP = "DOUBLING_UP"
    STREET = "STREET"
    PERMANENT_SUPPORTIVE_HOUSING = "PERMANENT_SUPPORTIVE_HOUSING"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
HousingStatus._metadata = {
    "HOMELESS_SHELTER": {'description': 'Patients who are living in a homeless shelter', 'meaning': 'HL7:udsplus-housing-status-codes#homeless-shelter'},
    "TRANSITIONAL": {'description': 'Patients who do not have a house and are in a transitional state', 'meaning': 'HL7:udsplus-housing-status-codes#transitional'},
    "DOUBLING_UP": {'description': 'Patients who are doubling up with others', 'meaning': 'HL7:udsplus-housing-status-codes#doubling-up'},
    "STREET": {'description': 'Patients who do not have a house and are living on the streets', 'meaning': 'HL7:udsplus-housing-status-codes#street'},
    "PERMANENT_SUPPORTIVE_HOUSING": {'description': 'Patients who are living in a permanent supportive housing', 'meaning': 'HL7:udsplus-housing-status-codes#permanent-supportive-housing'},
    "OTHER": {'description': 'Patients who have other kinds of accommodation', 'meaning': 'HL7:udsplus-housing-status-codes#other'},
    "UNKNOWN": {'description': 'Patients with Unknown accommodation', 'meaning': 'HL7:udsplus-housing-status-codes#unknown'},
}

class GenderIdentity(RichEnum):
    """
    Gender identity codes indicating an individual's personal sense of gender
    """
    # Enum members
    FEMALE = "FEMALE"
    MALE = "MALE"
    NON_BINARY = "NON_BINARY"
    ASKED_DECLINED = "ASKED_DECLINED"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
GenderIdentity._metadata = {
    "FEMALE": {'description': 'Identifies as female gender (finding)', 'meaning': 'SNOMED:446141000124107'},
    "MALE": {'description': 'Identifies as male gender (finding)', 'meaning': 'SNOMED:446151000124109'},
    "NON_BINARY": {'description': 'Identifies as gender nonbinary', 'meaning': 'SNOMED:33791000087105'},
    "ASKED_DECLINED": {'description': 'Asked But Declined', 'meaning': 'HL7:asked-declined'},
    "UNKNOWN": {'description': 'A proper value is applicable, but not known', 'meaning': 'HL7:UNK'},
}

class OmbRaceCategory(RichEnum):
    """
    Office of Management and Budget (OMB) race category codes
    """
    # Enum members
    AMERICAN_INDIAN_OR_ALASKA_NATIVE = "AMERICAN_INDIAN_OR_ALASKA_NATIVE"
    ASIAN = "ASIAN"
    BLACK_OR_AFRICAN_AMERICAN = "BLACK_OR_AFRICAN_AMERICAN"
    NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = "NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER"
    WHITE = "WHITE"
    OTHER_RACE = "OTHER_RACE"
    ASKED_BUT_UNKNOWN = "ASKED_BUT_UNKNOWN"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
OmbRaceCategory._metadata = {
    "AMERICAN_INDIAN_OR_ALASKA_NATIVE": {'description': 'American Indian or Alaska Native', 'meaning': 'HL7:CDCREC#1002-5'},
    "ASIAN": {'description': 'Asian', 'meaning': 'HL7:CDCREC#2028-9'},
    "BLACK_OR_AFRICAN_AMERICAN": {'description': 'Black or African American', 'meaning': 'HL7:CDCREC#2054-5'},
    "NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER": {'description': 'Native Hawaiian or Other Pacific Islander', 'meaning': 'HL7:CDCREC#2076-8'},
    "WHITE": {'description': 'White', 'meaning': 'HL7:CDCREC#2106-3'},
    "OTHER_RACE": {'description': 'Other Race (discouraged for statistical analysis)', 'meaning': 'HL7:CDCREC#2131-1'},
    "ASKED_BUT_UNKNOWN": {'description': 'asked but unknown', 'meaning': 'HL7:ASKU'},
    "UNKNOWN": {'description': 'unknown', 'meaning': 'HL7:UNK'},
}

class OmbEthnicityCategory(RichEnum):
    """
    Office of Management and Budget (OMB) ethnicity category codes
    """
    # Enum members
    HISPANIC_OR_LATINO = "HISPANIC_OR_LATINO"
    NOT_HISPANIC_OR_LATINO = "NOT_HISPANIC_OR_LATINO"
    ASKED_BUT_UNKNOWN = "ASKED_BUT_UNKNOWN"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
OmbEthnicityCategory._metadata = {
    "HISPANIC_OR_LATINO": {'description': 'Hispanic or Latino', 'meaning': 'HL7:CDCREC#2135-2'},
    "NOT_HISPANIC_OR_LATINO": {'description': 'Not Hispanic or Latino', 'meaning': 'HL7:CDCREC#2186-5'},
    "ASKED_BUT_UNKNOWN": {'description': 'asked but unknown', 'meaning': 'HL7:ASKU'},
    "UNKNOWN": {'description': 'unknown', 'meaning': 'HL7:UNK'},
}

class CaseOrControlEnum(RichEnum):
    # Enum members
    CASE = "CASE"
    CONTROL = "CONTROL"

# Set metadata after class creation to avoid it becoming an enum member
CaseOrControlEnum._metadata = {
    "CASE": {'meaning': 'OBI:0002492'},
    "CONTROL": {'meaning': 'OBI:0002493'},
}

class GOEvidenceCode(RichEnum):
    """
    Gene Ontology evidence codes mapped to Evidence and Conclusion Ontology (ECO) terms
    """
    # Enum members
    EXP = "EXP"
    IDA = "IDA"
    IPI = "IPI"
    IMP = "IMP"
    IGI = "IGI"
    IEP = "IEP"
    HTP = "HTP"
    HDA = "HDA"
    HMP = "HMP"
    HGI = "HGI"
    HEP = "HEP"
    IBA = "IBA"
    IBD = "IBD"
    IKR = "IKR"
    IRD = "IRD"
    ISS = "ISS"
    ISO = "ISO"
    ISA = "ISA"
    ISM = "ISM"
    IGC = "IGC"
    RCA = "RCA"
    TAS = "TAS"
    NAS = "NAS"
    IC = "IC"
    ND = "ND"
    IEA = "IEA"

# Set metadata after class creation to avoid it becoming an enum member
GOEvidenceCode._metadata = {
    "EXP": {'meaning': 'ECO:0000269', 'aliases': ['experimental evidence used in manual assertion']},
    "IDA": {'meaning': 'ECO:0000314', 'aliases': ['direct assay evidence used in manual assertion']},
    "IPI": {'meaning': 'ECO:0000353', 'aliases': ['physical interaction evidence used in manual assertion']},
    "IMP": {'meaning': 'ECO:0000315', 'aliases': ['mutant phenotype evidence used in manual assertion']},
    "IGI": {'meaning': 'ECO:0000316', 'aliases': ['genetic interaction evidence used in manual assertion']},
    "IEP": {'meaning': 'ECO:0000270', 'aliases': ['expression pattern evidence used in manual assertion']},
    "HTP": {'meaning': 'ECO:0006056', 'aliases': ['high throughput evidence used in manual assertion']},
    "HDA": {'meaning': 'ECO:0007005', 'aliases': ['high throughput direct assay evidence used in manual assertion']},
    "HMP": {'meaning': 'ECO:0007001', 'aliases': ['high throughput mutant phenotypic evidence used in manual assertion']},
    "HGI": {'meaning': 'ECO:0007003', 'aliases': ['high throughput genetic interaction phenotypic evidence used in manual assertion']},
    "HEP": {'meaning': 'ECO:0007007', 'aliases': ['high throughput expression pattern evidence used in manual assertion']},
    "IBA": {'meaning': 'ECO:0000318', 'aliases': ['biological aspect of ancestor evidence used in manual assertion']},
    "IBD": {'meaning': 'ECO:0000319', 'aliases': ['biological aspect of descendant evidence used in manual assertion']},
    "IKR": {'meaning': 'ECO:0000320', 'aliases': ['phylogenetic determination of loss of key residues evidence used in manual assertion']},
    "IRD": {'meaning': 'ECO:0000321', 'aliases': ['rapid divergence from ancestral sequence evidence used in manual assertion']},
    "ISS": {'meaning': 'ECO:0000250', 'aliases': ['sequence similarity evidence used in manual assertion']},
    "ISO": {'meaning': 'ECO:0000266', 'aliases': ['sequence orthology evidence used in manual assertion']},
    "ISA": {'meaning': 'ECO:0000247', 'aliases': ['sequence alignment evidence used in manual assertion']},
    "ISM": {'meaning': 'ECO:0000255', 'aliases': ['match to sequence model evidence used in manual assertion']},
    "IGC": {'meaning': 'ECO:0000317', 'aliases': ['genomic context evidence used in manual assertion']},
    "RCA": {'meaning': 'ECO:0000245', 'aliases': ['automatically integrated combinatorial evidence used in manual assertion']},
    "TAS": {'meaning': 'ECO:0000304', 'aliases': ['author statement supported by traceable reference used in manual assertion']},
    "NAS": {'meaning': 'ECO:0000303', 'aliases': ['author statement without traceable support used in manual assertion']},
    "IC": {'meaning': 'ECO:0000305', 'aliases': ['curator inference used in manual assertion']},
    "ND": {'meaning': 'ECO:0000307', 'aliases': ['no evidence data found used in manual assertion']},
    "IEA": {'meaning': 'ECO:0000501', 'aliases': ['evidence used in automatic assertion']},
}

class GOElectronicMethods(RichEnum):
    """
    Electronic annotation methods used in Gene Ontology, identified by GO_REF codes
    """
    # Enum members
    INTERPRO2GO = "INTERPRO2GO"
    EC2GO = "EC2GO"
    UNIPROTKB_KW2GO = "UNIPROTKB_KW2GO"
    UNIPROTKB_SUBCELL2GO = "UNIPROTKB_SUBCELL2GO"
    HAMAP_RULE2GO = "HAMAP_RULE2GO"
    UNIPATHWAY2GO = "UNIPATHWAY2GO"
    UNIRULE2GO = "UNIRULE2GO"
    RHEA2GO = "RHEA2GO"
    ENSEMBL_COMPARA = "ENSEMBL_COMPARA"
    PANTHER = "PANTHER"
    REACTOME = "REACTOME"
    RFAM2GO = "RFAM2GO"
    DICTYBASE = "DICTYBASE"
    MGI = "MGI"
    ZFIN = "ZFIN"
    FLYBASE = "FLYBASE"
    WORMBASE = "WORMBASE"
    SGD = "SGD"
    POMBASE = "POMBASE"
    METACYC2GO = "METACYC2GO"

# Set metadata after class creation to avoid it becoming an enum member
GOElectronicMethods._metadata = {
    "INTERPRO2GO": {'meaning': 'GO_REF:0000002'},
    "EC2GO": {'meaning': 'GO_REF:0000003'},
    "UNIPROTKB_KW2GO": {'meaning': 'GO_REF:0000004'},
    "UNIPROTKB_SUBCELL2GO": {'meaning': 'GO_REF:0000023'},
    "HAMAP_RULE2GO": {'meaning': 'GO_REF:0000020'},
    "UNIPATHWAY2GO": {'meaning': 'GO_REF:0000041'},
    "UNIRULE2GO": {'meaning': 'GO_REF:0000104'},
    "RHEA2GO": {'meaning': 'GO_REF:0000116'},
    "ENSEMBL_COMPARA": {'meaning': 'GO_REF:0000107'},
    "PANTHER": {'meaning': 'GO_REF:0000033'},
    "REACTOME": {'meaning': 'GO_REF:0000018'},
    "RFAM2GO": {'meaning': 'GO_REF:0000115'},
    "DICTYBASE": {'meaning': 'GO_REF:0000015'},
    "MGI": {'meaning': 'GO_REF:0000096'},
    "ZFIN": {'meaning': 'GO_REF:0000031'},
    "FLYBASE": {'meaning': 'GO_REF:0000047'},
    "WORMBASE": {'meaning': 'GO_REF:0000003'},
    "SGD": {'meaning': 'GO_REF:0000100'},
    "POMBASE": {'meaning': 'GO_REF:0000024'},
    "METACYC2GO": {'meaning': 'GO_REF:0000112'},
}

class CommonOrganismTaxaEnum(RichEnum):
    """
    Common model organisms used in biological research, mapped to NCBI Taxonomy IDs
    """
    # Enum members
    BACTERIA = "BACTERIA"
    ARCHAEA = "ARCHAEA"
    EUKARYOTA = "EUKARYOTA"
    VIRUSES = "VIRUSES"
    VERTEBRATA = "VERTEBRATA"
    MAMMALIA = "MAMMALIA"
    PRIMATES = "PRIMATES"
    RODENTIA = "RODENTIA"
    CARNIVORA = "CARNIVORA"
    ARTIODACTYLA = "ARTIODACTYLA"
    AVES = "AVES"
    ACTINOPTERYGII = "ACTINOPTERYGII"
    AMPHIBIA = "AMPHIBIA"
    ARTHROPODA = "ARTHROPODA"
    INSECTA = "INSECTA"
    NEMATODA = "NEMATODA"
    FUNGI = "FUNGI"
    ASCOMYCOTA = "ASCOMYCOTA"
    VIRIDIPLANTAE = "VIRIDIPLANTAE"
    MAGNOLIOPHYTA = "MAGNOLIOPHYTA"
    PROTEOBACTERIA = "PROTEOBACTERIA"
    GAMMAPROTEOBACTERIA = "GAMMAPROTEOBACTERIA"
    FIRMICUTES = "FIRMICUTES"
    ACTINOBACTERIA = "ACTINOBACTERIA"
    EURYARCHAEOTA = "EURYARCHAEOTA"
    APICOMPLEXA = "APICOMPLEXA"
    HUMAN = "HUMAN"
    MOUSE = "MOUSE"
    RAT = "RAT"
    RHESUS = "RHESUS"
    CHIMP = "CHIMP"
    DOG = "DOG"
    COW = "COW"
    PIG = "PIG"
    CHICKEN = "CHICKEN"
    ZEBRAFISH = "ZEBRAFISH"
    MEDAKA = "MEDAKA"
    PUFFERFISH = "PUFFERFISH"
    XENOPUS_TROPICALIS = "XENOPUS_TROPICALIS"
    XENOPUS_LAEVIS = "XENOPUS_LAEVIS"
    DROSOPHILA = "DROSOPHILA"
    C_ELEGANS = "C_ELEGANS"
    S_CEREVISIAE = "S_CEREVISIAE"
    S_CEREVISIAE_S288C = "S_CEREVISIAE_S288C"
    S_POMBE = "S_POMBE"
    C_ALBICANS = "C_ALBICANS"
    A_NIDULANS = "A_NIDULANS"
    N_CRASSA = "N_CRASSA"
    ARABIDOPSIS = "ARABIDOPSIS"
    RICE = "RICE"
    MAIZE = "MAIZE"
    TOMATO = "TOMATO"
    TOBACCO = "TOBACCO"
    E_COLI = "E_COLI"
    E_COLI_K12 = "E_COLI_K12"
    B_SUBTILIS = "B_SUBTILIS"
    M_TUBERCULOSIS = "M_TUBERCULOSIS"
    P_AERUGINOSA = "P_AERUGINOSA"
    S_AUREUS = "S_AUREUS"
    S_PNEUMONIAE = "S_PNEUMONIAE"
    H_PYLORI = "H_PYLORI"
    M_JANNASCHII = "M_JANNASCHII"
    H_SALINARUM = "H_SALINARUM"
    P_FALCIPARUM = "P_FALCIPARUM"
    T_GONDII = "T_GONDII"
    T_BRUCEI = "T_BRUCEI"
    DICTYOSTELIUM = "DICTYOSTELIUM"
    TETRAHYMENA = "TETRAHYMENA"
    PARAMECIUM = "PARAMECIUM"
    CHLAMYDOMONAS = "CHLAMYDOMONAS"
    PHAGE_LAMBDA = "PHAGE_LAMBDA"
    HIV1 = "HIV1"
    INFLUENZA_A = "INFLUENZA_A"
    SARS_COV_2 = "SARS_COV_2"

# Set metadata after class creation to avoid it becoming an enum member
CommonOrganismTaxaEnum._metadata = {
    "BACTERIA": {'description': 'Bacteria domain', 'meaning': 'NCBITaxon:2'},
    "ARCHAEA": {'description': 'Archaea domain', 'meaning': 'NCBITaxon:2157'},
    "EUKARYOTA": {'description': 'Eukaryota domain', 'meaning': 'NCBITaxon:2759'},
    "VIRUSES": {'description': 'Viruses (not a true domain)', 'meaning': 'NCBITaxon:10239'},
    "VERTEBRATA": {'description': 'Vertebrates', 'meaning': 'NCBITaxon:7742'},
    "MAMMALIA": {'description': 'Mammals', 'meaning': 'NCBITaxon:40674'},
    "PRIMATES": {'description': 'Primates', 'meaning': 'NCBITaxon:9443'},
    "RODENTIA": {'description': 'Rodents', 'meaning': 'NCBITaxon:9989'},
    "CARNIVORA": {'description': 'Carnivores', 'meaning': 'NCBITaxon:33554'},
    "ARTIODACTYLA": {'description': 'Even-toed ungulates', 'meaning': 'NCBITaxon:91561'},
    "AVES": {'description': 'Birds', 'meaning': 'NCBITaxon:8782'},
    "ACTINOPTERYGII": {'description': 'Ray-finned fishes', 'meaning': 'NCBITaxon:7898'},
    "AMPHIBIA": {'description': 'Amphibians', 'meaning': 'NCBITaxon:8292'},
    "ARTHROPODA": {'description': 'Arthropods', 'meaning': 'NCBITaxon:6656'},
    "INSECTA": {'description': 'Insects', 'meaning': 'NCBITaxon:50557'},
    "NEMATODA": {'description': 'Roundworms', 'meaning': 'NCBITaxon:6231'},
    "FUNGI": {'description': 'Fungal kingdom', 'meaning': 'NCBITaxon:4751'},
    "ASCOMYCOTA": {'description': 'Sac fungi', 'meaning': 'NCBITaxon:4890'},
    "VIRIDIPLANTAE": {'description': 'Green plants', 'meaning': 'NCBITaxon:33090'},
    "MAGNOLIOPHYTA": {'description': 'Flowering plants', 'meaning': 'NCBITaxon:3398'},
    "PROTEOBACTERIA": {'description': 'Proteobacteria', 'meaning': 'NCBITaxon:1224'},
    "GAMMAPROTEOBACTERIA": {'description': 'Gamma proteobacteria', 'meaning': 'NCBITaxon:1236'},
    "FIRMICUTES": {'description': 'Firmicutes (Gram-positive bacteria)', 'meaning': 'NCBITaxon:1239'},
    "ACTINOBACTERIA": {'description': 'Actinobacteria', 'meaning': 'NCBITaxon:201174'},
    "EURYARCHAEOTA": {'description': 'Euryarchaeota', 'meaning': 'NCBITaxon:28890'},
    "APICOMPLEXA": {'description': 'Apicomplexan parasites', 'meaning': 'NCBITaxon:5794'},
    "HUMAN": {'description': 'Homo sapiens (human)', 'meaning': 'NCBITaxon:9606'},
    "MOUSE": {'description': 'Mus musculus (house mouse)', 'meaning': 'NCBITaxon:10090'},
    "RAT": {'description': 'Rattus norvegicus (Norway rat)', 'meaning': 'NCBITaxon:10116'},
    "RHESUS": {'description': 'Macaca mulatta (rhesus macaque)', 'meaning': 'NCBITaxon:9544'},
    "CHIMP": {'description': 'Pan troglodytes (chimpanzee)', 'meaning': 'NCBITaxon:9598'},
    "DOG": {'description': 'Canis lupus familiaris (dog)', 'meaning': 'NCBITaxon:9615'},
    "COW": {'description': 'Bos taurus (cattle)', 'meaning': 'NCBITaxon:9913'},
    "PIG": {'description': 'Sus scrofa (pig)', 'meaning': 'NCBITaxon:9823'},
    "CHICKEN": {'description': 'Gallus gallus (chicken)', 'meaning': 'NCBITaxon:9031'},
    "ZEBRAFISH": {'description': 'Danio rerio (zebrafish)', 'meaning': 'NCBITaxon:7955'},
    "MEDAKA": {'description': 'Oryzias latipes (Japanese medaka)', 'meaning': 'NCBITaxon:8090'},
    "PUFFERFISH": {'description': 'Takifugu rubripes (torafugu)', 'meaning': 'NCBITaxon:31033'},
    "XENOPUS_TROPICALIS": {'description': 'Xenopus tropicalis (western clawed frog)', 'meaning': 'NCBITaxon:8364'},
    "XENOPUS_LAEVIS": {'description': 'Xenopus laevis (African clawed frog)', 'meaning': 'NCBITaxon:8355'},
    "DROSOPHILA": {'description': 'Drosophila melanogaster (fruit fly)', 'meaning': 'NCBITaxon:7227'},
    "C_ELEGANS": {'description': 'Caenorhabditis elegans (roundworm)', 'meaning': 'NCBITaxon:6239'},
    "S_CEREVISIAE": {'description': "Saccharomyces cerevisiae (baker's yeast)", 'meaning': 'NCBITaxon:4932'},
    "S_CEREVISIAE_S288C": {'description': 'Saccharomyces cerevisiae S288C (reference strain)', 'meaning': 'NCBITaxon:559292'},
    "S_POMBE": {'description': 'Schizosaccharomyces pombe (fission yeast)', 'meaning': 'NCBITaxon:4896'},
    "C_ALBICANS": {'description': 'Candida albicans (pathogenic yeast)', 'meaning': 'NCBITaxon:5476'},
    "A_NIDULANS": {'description': 'Aspergillus nidulans (filamentous fungus)', 'meaning': 'NCBITaxon:162425'},
    "N_CRASSA": {'description': 'Neurospora crassa (red bread mold)', 'meaning': 'NCBITaxon:5141'},
    "ARABIDOPSIS": {'description': 'Arabidopsis thaliana (thale cress)', 'meaning': 'NCBITaxon:3702'},
    "RICE": {'description': 'Oryza sativa (rice)', 'meaning': 'NCBITaxon:4530'},
    "MAIZE": {'description': 'Zea mays (corn)', 'meaning': 'NCBITaxon:4577'},
    "TOMATO": {'description': 'Solanum lycopersicum (tomato)', 'meaning': 'NCBITaxon:4081'},
    "TOBACCO": {'description': 'Nicotiana tabacum (tobacco)', 'meaning': 'NCBITaxon:4097'},
    "E_COLI": {'description': 'Escherichia coli', 'meaning': 'NCBITaxon:562'},
    "E_COLI_K12": {'description': 'Escherichia coli str. K-12', 'meaning': 'NCBITaxon:83333'},
    "B_SUBTILIS": {'description': 'Bacillus subtilis', 'meaning': 'NCBITaxon:1423'},
    "M_TUBERCULOSIS": {'description': 'Mycobacterium tuberculosis', 'meaning': 'NCBITaxon:1773'},
    "P_AERUGINOSA": {'description': 'Pseudomonas aeruginosa', 'meaning': 'NCBITaxon:287'},
    "S_AUREUS": {'description': 'Staphylococcus aureus', 'meaning': 'NCBITaxon:1280'},
    "S_PNEUMONIAE": {'description': 'Streptococcus pneumoniae', 'meaning': 'NCBITaxon:1313'},
    "H_PYLORI": {'description': 'Helicobacter pylori', 'meaning': 'NCBITaxon:210'},
    "M_JANNASCHII": {'description': 'Methanocaldococcus jannaschii', 'meaning': 'NCBITaxon:2190'},
    "H_SALINARUM": {'description': 'Halobacterium salinarum', 'meaning': 'NCBITaxon:2242'},
    "P_FALCIPARUM": {'description': 'Plasmodium falciparum (malaria parasite)', 'meaning': 'NCBITaxon:5833'},
    "T_GONDII": {'description': 'Toxoplasma gondii', 'meaning': 'NCBITaxon:5811'},
    "T_BRUCEI": {'description': 'Trypanosoma brucei', 'meaning': 'NCBITaxon:5691'},
    "DICTYOSTELIUM": {'description': 'Dictyostelium discoideum (slime mold)', 'meaning': 'NCBITaxon:44689'},
    "TETRAHYMENA": {'description': 'Tetrahymena thermophila', 'meaning': 'NCBITaxon:5911'},
    "PARAMECIUM": {'description': 'Paramecium tetraurelia', 'meaning': 'NCBITaxon:5888'},
    "CHLAMYDOMONAS": {'description': 'Chlamydomonas reinhardtii (green alga)', 'meaning': 'NCBITaxon:3055'},
    "PHAGE_LAMBDA": {'description': 'Escherichia phage lambda', 'meaning': 'NCBITaxon:10710'},
    "HIV1": {'description': 'Human immunodeficiency virus 1', 'meaning': 'NCBITaxon:11676'},
    "INFLUENZA_A": {'description': 'Influenza A virus', 'meaning': 'NCBITaxon:11320'},
    "SARS_COV_2": {'description': 'Severe acute respiratory syndrome coronavirus 2', 'meaning': 'NCBITaxon:2697049'},
}

class TaxonomicRank(RichEnum):
    """
    Standard taxonomic ranks used in biological classification
    """
    # Enum members
    DOMAIN = "DOMAIN"
    KINGDOM = "KINGDOM"
    PHYLUM = "PHYLUM"
    CLASS = "CLASS"
    ORDER = "ORDER"
    FAMILY = "FAMILY"
    GENUS = "GENUS"
    SPECIES = "SPECIES"
    SUBSPECIES = "SUBSPECIES"
    STRAIN = "STRAIN"
    VARIETY = "VARIETY"
    FORM = "FORM"
    CULTIVAR = "CULTIVAR"

# Set metadata after class creation to avoid it becoming an enum member
TaxonomicRank._metadata = {
    "DOMAIN": {'description': 'Domain (highest rank)', 'meaning': 'TAXRANK:0000037'},
    "KINGDOM": {'description': 'Kingdom', 'meaning': 'TAXRANK:0000017'},
    "PHYLUM": {'description': 'Phylum (animals, plants, fungi) or Division (plants)', 'meaning': 'TAXRANK:0000001'},
    "CLASS": {'description': 'Class', 'meaning': 'TAXRANK:0000002'},
    "ORDER": {'description': 'Order', 'meaning': 'TAXRANK:0000003'},
    "FAMILY": {'description': 'Family', 'meaning': 'TAXRANK:0000004'},
    "GENUS": {'description': 'Genus', 'meaning': 'TAXRANK:0000005'},
    "SPECIES": {'description': 'Species', 'meaning': 'TAXRANK:0000006'},
    "SUBSPECIES": {'description': 'Subspecies', 'meaning': 'TAXRANK:0000023'},
    "STRAIN": {'description': 'Strain (especially for microorganisms)', 'meaning': 'TAXRANK:0001001'},
    "VARIETY": {'description': 'Variety (mainly plants)', 'meaning': 'TAXRANK:0000016'},
    "FORM": {'description': 'Form (mainly plants)', 'meaning': 'TAXRANK:0000026'},
    "CULTIVAR": {'description': 'Cultivar (cultivated variety)', 'meaning': 'TAXRANK:0000034'},
}

class BiologicalKingdom(RichEnum):
    """
    Major kingdoms/domains of life
    """
    # Enum members
    BACTERIA = "BACTERIA"
    ARCHAEA = "ARCHAEA"
    EUKARYOTA = "EUKARYOTA"
    ANIMALIA = "ANIMALIA"
    PLANTAE = "PLANTAE"
    FUNGI = "FUNGI"
    PROTISTA = "PROTISTA"
    VIRUSES = "VIRUSES"

# Set metadata after class creation to avoid it becoming an enum member
BiologicalKingdom._metadata = {
    "BACTERIA": {'description': 'Bacteria domain', 'meaning': 'NCBITaxon:2'},
    "ARCHAEA": {'description': 'Archaea domain', 'meaning': 'NCBITaxon:2157'},
    "EUKARYOTA": {'description': 'Eukaryota domain', 'meaning': 'NCBITaxon:2759'},
    "ANIMALIA": {'description': 'Animal kingdom', 'meaning': 'NCBITaxon:33208'},
    "PLANTAE": {'description': 'Plant kingdom (Viridiplantae)', 'meaning': 'NCBITaxon:33090'},
    "FUNGI": {'description': 'Fungal kingdom', 'meaning': 'NCBITaxon:4751'},
    "PROTISTA": {'description': 'Protist kingdom (polyphyletic group)'},
    "VIRUSES": {'description': 'Viruses (not a true kingdom)', 'meaning': 'NCBITaxon:10239'},
}

class CellCyclePhase(RichEnum):
    """
    Major phases of the eukaryotic cell cycle
    """
    # Enum members
    G0 = "G0"
    G1 = "G1"
    S = "S"
    G2 = "G2"
    M = "M"
    INTERPHASE = "INTERPHASE"

# Set metadata after class creation to avoid it becoming an enum member
CellCyclePhase._metadata = {
    "G0": {'description': 'G0 phase (quiescent/resting phase)', 'meaning': 'GO:0044838', 'annotations': {'aliases': 'quiescent phase, resting phase'}},
    "G1": {'description': 'G1 phase (Gap 1)', 'meaning': 'GO:0051318', 'annotations': {'aliases': 'Gap 1, first gap phase', 'duration': 'variable (hours to years)'}},
    "S": {'description': 'S phase (DNA synthesis)', 'meaning': 'GO:0051320', 'annotations': {'aliases': 'synthesis phase, DNA replication phase', 'duration': '6-8 hours'}},
    "G2": {'description': 'G2 phase (Gap 2)', 'meaning': 'GO:0051319', 'annotations': {'aliases': 'Gap 2, second gap phase', 'duration': '3-4 hours'}},
    "M": {'description': 'M phase (mitosis and cytokinesis)', 'meaning': 'GO:0000279', 'annotations': {'aliases': 'mitotic phase, division phase', 'duration': '~1 hour'}},
    "INTERPHASE": {'description': 'Interphase (G1, S, and G2 phases combined)', 'meaning': 'GO:0051325', 'annotations': {'includes': 'G1, S, G2'}},
}

class MitoticPhase(RichEnum):
    """
    Stages of mitosis (M phase)
    """
    # Enum members
    PROPHASE = "PROPHASE"
    PROMETAPHASE = "PROMETAPHASE"
    METAPHASE = "METAPHASE"
    ANAPHASE = "ANAPHASE"
    TELOPHASE = "TELOPHASE"
    CYTOKINESIS = "CYTOKINESIS"

# Set metadata after class creation to avoid it becoming an enum member
MitoticPhase._metadata = {
    "PROPHASE": {'description': 'Prophase', 'meaning': 'GO:0051324', 'annotations': {'order': 1, 'features': 'chromatin condensation, spindle formation begins'}},
    "PROMETAPHASE": {'description': 'Prometaphase', 'meaning': 'GO:0007080', 'annotations': {'order': 2, 'features': 'nuclear envelope breakdown, kinetochore attachment'}},
    "METAPHASE": {'description': 'Metaphase', 'meaning': 'GO:0051323', 'annotations': {'order': 3, 'features': 'chromosomes aligned at metaphase plate'}},
    "ANAPHASE": {'description': 'Anaphase', 'meaning': 'GO:0051322', 'annotations': {'order': 4, 'features': 'sister chromatid separation'}},
    "TELOPHASE": {'description': 'Telophase', 'meaning': 'GO:0051326', 'annotations': {'order': 5, 'features': 'nuclear envelope reformation'}},
    "CYTOKINESIS": {'description': 'Cytokinesis', 'meaning': 'GO:0000910', 'annotations': {'order': 6, 'features': 'cytoplasmic division'}},
}

class CellCycleCheckpoint(RichEnum):
    """
    Cell cycle checkpoints that regulate progression
    """
    # Enum members
    G1_S_CHECKPOINT = "G1_S_CHECKPOINT"
    INTRA_S_CHECKPOINT = "INTRA_S_CHECKPOINT"
    G2_M_CHECKPOINT = "G2_M_CHECKPOINT"
    SPINDLE_CHECKPOINT = "SPINDLE_CHECKPOINT"

# Set metadata after class creation to avoid it becoming an enum member
CellCycleCheckpoint._metadata = {
    "G1_S_CHECKPOINT": {'description': 'G1/S checkpoint (Restriction point)', 'meaning': 'GO:0000082', 'annotations': {'aliases': 'Start checkpoint, Restriction point, R point', 'regulator': 'p53, Rb'}},
    "INTRA_S_CHECKPOINT": {'description': 'Intra-S checkpoint', 'meaning': 'GO:0031573', 'annotations': {'function': 'monitors DNA replication', 'regulator': 'ATR, CHK1'}},
    "G2_M_CHECKPOINT": {'description': 'G2/M checkpoint', 'meaning': 'GO:0031571', 'annotations': {'function': 'ensures DNA properly replicated', 'regulator': 'p53, CHK1, CHK2'}},
    "SPINDLE_CHECKPOINT": {'description': 'Spindle checkpoint (M checkpoint)', 'meaning': 'GO:0031577', 'annotations': {'aliases': 'SAC, spindle assembly checkpoint', 'function': 'ensures proper chromosome attachment', 'regulator': 'MAD2, BubR1'}},
}

class MeioticPhase(RichEnum):
    """
    Phases specific to meiotic cell division
    """
    # Enum members
    MEIOSIS_I = "MEIOSIS_I"
    PROPHASE_I = "PROPHASE_I"
    METAPHASE_I = "METAPHASE_I"
    ANAPHASE_I = "ANAPHASE_I"
    TELOPHASE_I = "TELOPHASE_I"
    MEIOSIS_II = "MEIOSIS_II"
    PROPHASE_II = "PROPHASE_II"
    METAPHASE_II = "METAPHASE_II"
    ANAPHASE_II = "ANAPHASE_II"
    TELOPHASE_II = "TELOPHASE_II"

# Set metadata after class creation to avoid it becoming an enum member
MeioticPhase._metadata = {
    "MEIOSIS_I": {'description': 'Meiosis I (reductional division)', 'meaning': 'GO:0007127', 'annotations': {'result': 'reduction from diploid to haploid'}},
    "PROPHASE_I": {'description': 'Prophase I', 'meaning': 'GO:0007128', 'annotations': {'substages': 'leptotene, zygotene, pachytene, diplotene, diakinesis'}},
    "METAPHASE_I": {'description': 'Metaphase I', 'meaning': 'GO:0007132', 'annotations': {'feature': 'homologous pairs align'}},
    "ANAPHASE_I": {'description': 'Anaphase I', 'meaning': 'GO:0007133', 'annotations': {'feature': 'homologous chromosomes separate'}},
    "TELOPHASE_I": {'description': 'Telophase I', 'meaning': 'GO:0007134'},
    "MEIOSIS_II": {'description': 'Meiosis II (equational division)', 'meaning': 'GO:0007135', 'annotations': {'similarity': 'similar to mitosis'}},
    "PROPHASE_II": {'description': 'Prophase II', 'meaning': 'GO:0007136'},
    "METAPHASE_II": {'description': 'Metaphase II', 'meaning': 'GO:0007137'},
    "ANAPHASE_II": {'description': 'Anaphase II', 'meaning': 'GO:0007138', 'annotations': {'feature': 'sister chromatids separate'}},
    "TELOPHASE_II": {'description': 'Telophase II', 'meaning': 'GO:0007139'},
}

class CellCycleRegulator(RichEnum):
    """
    Types of cell cycle regulatory molecules
    """
    # Enum members
    CYCLIN = "CYCLIN"
    CDK = "CDK"
    CDK_INHIBITOR = "CDK_INHIBITOR"
    CHECKPOINT_KINASE = "CHECKPOINT_KINASE"
    TUMOR_SUPPRESSOR = "TUMOR_SUPPRESSOR"
    E3_UBIQUITIN_LIGASE = "E3_UBIQUITIN_LIGASE"
    PHOSPHATASE = "PHOSPHATASE"

# Set metadata after class creation to avoid it becoming an enum member
CellCycleRegulator._metadata = {
    "CYCLIN": {'description': 'Cyclin proteins', 'meaning': 'GO:0016538', 'annotations': {'examples': 'Cyclin A, B, D, E'}},
    "CDK": {'description': 'Cyclin-dependent kinase', 'meaning': 'GO:0004693', 'annotations': {'examples': 'CDK1, CDK2, CDK4, CDK6'}},
    "CDK_INHIBITOR": {'description': 'CDK inhibitor', 'meaning': 'GO:0004861', 'annotations': {'examples': 'p21, p27, p57'}},
    "CHECKPOINT_KINASE": {'description': 'Checkpoint kinase', 'meaning': 'GO:0000077', 'annotations': {'examples': 'CHK1, CHK2, ATR, ATM'}},
    "TUMOR_SUPPRESSOR": {'description': 'Tumor suppressor involved in cell cycle', 'meaning': 'GO:0051726', 'annotations': {'examples': 'p53, Rb, BRCA1, BRCA2'}},
    "E3_UBIQUITIN_LIGASE": {'description': 'E3 ubiquitin ligase (cell cycle)', 'meaning': 'GO:0051437', 'annotations': {'examples': 'APC/C, SCF'}},
    "PHOSPHATASE": {'description': 'Cell cycle phosphatase', 'meaning': 'GO:0004721', 'annotations': {'examples': 'CDC25A, CDC25B, CDC25C'}},
}

class CellProliferationState(RichEnum):
    """
    Cell proliferation and growth states
    """
    # Enum members
    PROLIFERATING = "PROLIFERATING"
    QUIESCENT = "QUIESCENT"
    SENESCENT = "SENESCENT"
    DIFFERENTIATED = "DIFFERENTIATED"
    APOPTOTIC = "APOPTOTIC"
    NECROTIC = "NECROTIC"

# Set metadata after class creation to avoid it becoming an enum member
CellProliferationState._metadata = {
    "PROLIFERATING": {'description': 'Actively proliferating cells', 'meaning': 'GO:0008283'},
    "QUIESCENT": {'description': 'Quiescent cells (reversibly non-dividing)', 'meaning': 'GO:0044838', 'annotations': {'phase': 'G0', 'reversible': True}},
    "SENESCENT": {'description': 'Senescent cells (permanently non-dividing)', 'meaning': 'GO:0090398', 'annotations': {'reversible': False, 'markers': 'SA-β-gal, p16'}},
    "DIFFERENTIATED": {'description': 'Terminally differentiated cells', 'meaning': 'GO:0030154', 'annotations': {'examples': 'neurons, cardiomyocytes'}},
    "APOPTOTIC": {'description': 'Cells undergoing apoptosis', 'meaning': 'GO:0006915', 'annotations': {'aliases': 'programmed cell death'}},
    "NECROTIC": {'description': 'Cells undergoing necrosis', 'meaning': 'GO:0070265', 'annotations': {'type': 'uncontrolled cell death'}},
}

class DNADamageResponse(RichEnum):
    """
    DNA damage response pathways during cell cycle
    """
    # Enum members
    CELL_CYCLE_ARREST = "CELL_CYCLE_ARREST"
    DNA_REPAIR = "DNA_REPAIR"
    APOPTOSIS_INDUCTION = "APOPTOSIS_INDUCTION"
    SENESCENCE_INDUCTION = "SENESCENCE_INDUCTION"
    CHECKPOINT_ADAPTATION = "CHECKPOINT_ADAPTATION"

# Set metadata after class creation to avoid it becoming an enum member
DNADamageResponse._metadata = {
    "CELL_CYCLE_ARREST": {'description': 'Cell cycle arrest', 'meaning': 'GO:0051726', 'aliases': ['regulation of cell cycle']},
    "DNA_REPAIR": {'description': 'DNA repair', 'meaning': 'GO:0006281'},
    "APOPTOSIS_INDUCTION": {'description': 'Induction of apoptosis', 'meaning': 'GO:0043065', 'aliases': ['positive regulation of apoptotic process']},
    "SENESCENCE_INDUCTION": {'description': 'Induction of senescence', 'meaning': 'GO:0090400'},
    "CHECKPOINT_ADAPTATION": {'description': 'Checkpoint adaptation', 'annotations': {'description': 'override of checkpoint despite damage'}},
}

class GenomeFeatureType(RichEnum):
    """
    Genome feature types from SOFA (Sequence Ontology Feature Annotation).
This is the subset of Sequence Ontology terms used in GFF3 files.
Organized hierarchically following the Sequence Ontology structure.
    """
    # Enum members
    REGION = "REGION"
    BIOLOGICAL_REGION = "BIOLOGICAL_REGION"
    GENE = "GENE"
    TRANSCRIPT = "TRANSCRIPT"
    PRIMARY_TRANSCRIPT = "PRIMARY_TRANSCRIPT"
    MRNA = "MRNA"
    EXON = "EXON"
    CDS = "CDS"
    INTRON = "INTRON"
    FIVE_PRIME_UTR = "FIVE_PRIME_UTR"
    THREE_PRIME_UTR = "THREE_PRIME_UTR"
    NCRNA = "NCRNA"
    RRNA = "RRNA"
    TRNA = "TRNA"
    SNRNA = "SNRNA"
    SNORNA = "SNORNA"
    MIRNA = "MIRNA"
    LNCRNA = "LNCRNA"
    RIBOZYME = "RIBOZYME"
    ANTISENSE_RNA = "ANTISENSE_RNA"
    PSEUDOGENE = "PSEUDOGENE"
    PROCESSED_PSEUDOGENE = "PROCESSED_PSEUDOGENE"
    REGULATORY_REGION = "REGULATORY_REGION"
    PROMOTER = "PROMOTER"
    ENHANCER = "ENHANCER"
    SILENCER = "SILENCER"
    TERMINATOR = "TERMINATOR"
    ATTENUATOR = "ATTENUATOR"
    POLYA_SIGNAL_SEQUENCE = "POLYA_SIGNAL_SEQUENCE"
    BINDING_SITE = "BINDING_SITE"
    TFBS = "TFBS"
    RIBOSOME_ENTRY_SITE = "RIBOSOME_ENTRY_SITE"
    POLYA_SITE = "POLYA_SITE"
    REPEAT_REGION = "REPEAT_REGION"
    DISPERSED_REPEAT = "DISPERSED_REPEAT"
    TANDEM_REPEAT = "TANDEM_REPEAT"
    INVERTED_REPEAT = "INVERTED_REPEAT"
    TRANSPOSABLE_ELEMENT = "TRANSPOSABLE_ELEMENT"
    MOBILE_ELEMENT = "MOBILE_ELEMENT"
    SEQUENCE_ALTERATION = "SEQUENCE_ALTERATION"
    INSERTION = "INSERTION"
    DELETION = "DELETION"
    INVERSION = "INVERSION"
    DUPLICATION = "DUPLICATION"
    SUBSTITUTION = "SUBSTITUTION"
    ORIGIN_OF_REPLICATION = "ORIGIN_OF_REPLICATION"
    POLYC_TRACT = "POLYC_TRACT"
    GAP = "GAP"
    ASSEMBLY_GAP = "ASSEMBLY_GAP"
    CHROMOSOME = "CHROMOSOME"
    SUPERCONTIG = "SUPERCONTIG"
    CONTIG = "CONTIG"
    SCAFFOLD = "SCAFFOLD"
    CLONE = "CLONE"
    PLASMID = "PLASMID"
    POLYPEPTIDE = "POLYPEPTIDE"
    MATURE_PROTEIN_REGION = "MATURE_PROTEIN_REGION"
    SIGNAL_PEPTIDE = "SIGNAL_PEPTIDE"
    TRANSIT_PEPTIDE = "TRANSIT_PEPTIDE"
    PROPEPTIDE = "PROPEPTIDE"
    OPERON = "OPERON"
    STEM_LOOP = "STEM_LOOP"
    D_LOOP = "D_LOOP"
    MATCH = "MATCH"
    CDNA_MATCH = "CDNA_MATCH"
    EST_MATCH = "EST_MATCH"
    PROTEIN_MATCH = "PROTEIN_MATCH"
    NUCLEOTIDE_MATCH = "NUCLEOTIDE_MATCH"
    JUNCTION_FEATURE = "JUNCTION_FEATURE"
    SPLICE_SITE = "SPLICE_SITE"
    FIVE_PRIME_SPLICE_SITE = "FIVE_PRIME_SPLICE_SITE"
    THREE_PRIME_SPLICE_SITE = "THREE_PRIME_SPLICE_SITE"
    START_CODON = "START_CODON"
    STOP_CODON = "STOP_CODON"
    CENTROMERE = "CENTROMERE"
    TELOMERE = "TELOMERE"

# Set metadata after class creation to avoid it becoming an enum member
GenomeFeatureType._metadata = {
    "REGION": {'description': 'A sequence feature with an extent greater than zero', 'meaning': 'SO:0000001'},
    "BIOLOGICAL_REGION": {'description': 'A region defined by its biological properties', 'meaning': 'SO:0001411'},
    "GENE": {'description': 'A region (or regions) that includes all of the sequence elements necessary to encode a functional transcript', 'meaning': 'SO:0000704'},
    "TRANSCRIPT": {'description': 'An RNA synthesized on a DNA or RNA template by an RNA polymerase', 'meaning': 'SO:0000673'},
    "PRIMARY_TRANSCRIPT": {'description': 'A transcript that has not been processed', 'meaning': 'SO:0000185'},
    "MRNA": {'description': "Messenger RNA; includes 5'UTR, coding sequences and 3'UTR", 'meaning': 'SO:0000234'},
    "EXON": {'description': 'A region of the transcript sequence within a gene which is not removed from the primary RNA transcript by RNA splicing', 'meaning': 'SO:0000147'},
    "CDS": {'description': 'Coding sequence; sequence of nucleotides that corresponds with the sequence of amino acids in a protein', 'meaning': 'SO:0000316'},
    "INTRON": {'description': 'A region of a primary transcript that is transcribed, but removed from within the transcript by splicing', 'meaning': 'SO:0000188'},
    "FIVE_PRIME_UTR": {'description': "5' untranslated region", 'meaning': 'SO:0000204'},
    "THREE_PRIME_UTR": {'description': "3' untranslated region", 'meaning': 'SO:0000205'},
    "NCRNA": {'description': 'Non-protein coding RNA', 'meaning': 'SO:0000655'},
    "RRNA": {'description': 'Ribosomal RNA', 'meaning': 'SO:0000252'},
    "TRNA": {'description': 'Transfer RNA', 'meaning': 'SO:0000253'},
    "SNRNA": {'description': 'Small nuclear RNA', 'meaning': 'SO:0000274'},
    "SNORNA": {'description': 'Small nucleolar RNA', 'meaning': 'SO:0000275'},
    "MIRNA": {'description': 'MicroRNA', 'meaning': 'SO:0000276'},
    "LNCRNA": {'description': 'Long non-coding RNA', 'meaning': 'SO:0001877'},
    "RIBOZYME": {'description': 'An RNA with catalytic activity', 'meaning': 'SO:0000374'},
    "ANTISENSE_RNA": {'description': 'RNA that is complementary to other RNA', 'meaning': 'SO:0000644'},
    "PSEUDOGENE": {'description': 'A sequence that closely resembles a known functional gene but does not produce a functional product', 'meaning': 'SO:0000336'},
    "PROCESSED_PSEUDOGENE": {'description': 'A pseudogene arising from reverse transcription of mRNA', 'meaning': 'SO:0000043'},
    "REGULATORY_REGION": {'description': 'A region involved in the control of the process of gene expression', 'meaning': 'SO:0005836'},
    "PROMOTER": {'description': 'A regulatory region initiating transcription', 'meaning': 'SO:0000167'},
    "ENHANCER": {'description': 'A cis-acting sequence that increases transcription', 'meaning': 'SO:0000165'},
    "SILENCER": {'description': 'A regulatory region which upon binding of transcription factors, suppresses transcription', 'meaning': 'SO:0000625'},
    "TERMINATOR": {'description': 'The sequence of DNA located either at the end of the transcript that causes RNA polymerase to terminate transcription', 'meaning': 'SO:0000141'},
    "ATTENUATOR": {'description': 'A sequence that causes transcription termination', 'meaning': 'SO:0000140'},
    "POLYA_SIGNAL_SEQUENCE": {'description': 'The recognition sequence for the cleavage and polyadenylation machinery', 'meaning': 'SO:0000551'},
    "BINDING_SITE": {'description': 'A region on a molecule that binds to another molecule', 'meaning': 'SO:0000409'},
    "TFBS": {'description': 'Transcription factor binding site', 'meaning': 'SO:0000235'},
    "RIBOSOME_ENTRY_SITE": {'description': 'Region where ribosome assembles on mRNA', 'meaning': 'SO:0000139'},
    "POLYA_SITE": {'description': 'Polyadenylation site', 'meaning': 'SO:0000553'},
    "REPEAT_REGION": {'description': 'A region of sequence containing one or more repeat units', 'meaning': 'SO:0000657'},
    "DISPERSED_REPEAT": {'description': 'A repeat that is interspersed in the genome', 'meaning': 'SO:0000658'},
    "TANDEM_REPEAT": {'description': 'A repeat where the same sequence is repeated in the same orientation', 'meaning': 'SO:0000705'},
    "INVERTED_REPEAT": {'description': 'A repeat where the sequence is repeated in the opposite orientation', 'meaning': 'SO:0000294'},
    "TRANSPOSABLE_ELEMENT": {'description': 'A DNA segment that can change its position within the genome', 'meaning': 'SO:0000101'},
    "MOBILE_ELEMENT": {'description': 'A nucleotide region with the ability to move from one place in the genome to another', 'meaning': 'SO:0001037'},
    "SEQUENCE_ALTERATION": {'description': 'A sequence that deviates from the reference sequence', 'meaning': 'SO:0001059'},
    "INSERTION": {'description': 'The sequence of one or more nucleotides added between two adjacent nucleotides', 'meaning': 'SO:0000667'},
    "DELETION": {'description': 'The removal of a sequences of nucleotides from the genome', 'meaning': 'SO:0000159'},
    "INVERSION": {'description': 'A continuous nucleotide sequence is inverted in the same position', 'meaning': 'SO:1000036'},
    "DUPLICATION": {'description': 'One or more nucleotides are added between two adjacent nucleotides', 'meaning': 'SO:1000035'},
    "SUBSTITUTION": {'description': 'A sequence alteration where one nucleotide replaced by another', 'meaning': 'SO:1000002'},
    "ORIGIN_OF_REPLICATION": {'description': 'The origin of replication; starting site for duplication of a nucleic acid molecule', 'meaning': 'SO:0000296'},
    "POLYC_TRACT": {'description': 'A sequence of Cs'},
    "GAP": {'description': 'A gap in the sequence', 'meaning': 'SO:0000730'},
    "ASSEMBLY_GAP": {'description': 'A gap between two sequences in an assembly', 'meaning': 'SO:0000730'},
    "CHROMOSOME": {'description': 'Structural unit composed of DNA and proteins', 'meaning': 'SO:0000340'},
    "SUPERCONTIG": {'description': 'One or more contigs that have been ordered and oriented using end-read information', 'meaning': 'SO:0000148'},
    "CONTIG": {'description': 'A contiguous sequence derived from sequence assembly', 'meaning': 'SO:0000149'},
    "SCAFFOLD": {'description': 'One or more contigs that have been ordered and oriented', 'meaning': 'SO:0000148'},
    "CLONE": {'description': 'A piece of DNA that has been inserted into a vector', 'meaning': 'SO:0000151'},
    "PLASMID": {'description': 'A self-replicating circular DNA molecule', 'meaning': 'SO:0000155'},
    "POLYPEPTIDE": {'description': 'A sequence of amino acids linked by peptide bonds', 'meaning': 'SO:0000104'},
    "MATURE_PROTEIN_REGION": {'description': 'The polypeptide sequence that remains after post-translational processing', 'meaning': 'SO:0000419'},
    "SIGNAL_PEPTIDE": {'description': 'A peptide region that targets a polypeptide to a specific location', 'meaning': 'SO:0000418'},
    "TRANSIT_PEPTIDE": {'description': 'A peptide that directs the transport of a protein to an organelle', 'meaning': 'SO:0000725'},
    "PROPEPTIDE": {'description': 'A peptide region that is cleaved during maturation', 'meaning': 'SO:0001062'},
    "OPERON": {'description': 'A group of contiguous genes transcribed as a single unit', 'meaning': 'SO:0000178'},
    "STEM_LOOP": {'description': 'A double-helical region formed by base-pairing between adjacent sequences', 'meaning': 'SO:0000313'},
    "D_LOOP": {'description': 'Displacement loop; a region where DNA is displaced by an invading strand', 'meaning': 'SO:0000297'},
    "MATCH": {'description': 'A region of sequence similarity', 'meaning': 'SO:0000343'},
    "CDNA_MATCH": {'description': 'A match to a cDNA sequence', 'meaning': 'SO:0000689'},
    "EST_MATCH": {'description': 'A match to an EST sequence', 'meaning': 'SO:0000668'},
    "PROTEIN_MATCH": {'description': 'A match to a protein sequence', 'meaning': 'SO:0000349'},
    "NUCLEOTIDE_MATCH": {'description': 'A match to a nucleotide sequence', 'meaning': 'SO:0000347'},
    "JUNCTION_FEATURE": {'description': 'A boundary or junction between sequence regions', 'meaning': 'SO:0000699'},
    "SPLICE_SITE": {'description': 'The position where intron is excised', 'meaning': 'SO:0000162'},
    "FIVE_PRIME_SPLICE_SITE": {'description': "The 5' splice site (donor site)", 'meaning': 'SO:0000163'},
    "THREE_PRIME_SPLICE_SITE": {'description': "The 3' splice site (acceptor site)", 'meaning': 'SO:0000164'},
    "START_CODON": {'description': 'The first codon to be translated', 'meaning': 'SO:0000318'},
    "STOP_CODON": {'description': 'The codon that terminates translation', 'meaning': 'SO:0000319'},
    "CENTROMERE": {'description': 'A region where chromatids are held together', 'meaning': 'SO:0000577'},
    "TELOMERE": {'description': 'The terminal region of a linear chromosome', 'meaning': 'SO:0000624'},
}

class SampleType(RichEnum):
    """
    Types of biological samples used in structural biology
    """
    # Enum members
    PROTEIN = "PROTEIN"
    NUCLEIC_ACID = "NUCLEIC_ACID"
    PROTEIN_COMPLEX = "PROTEIN_COMPLEX"
    MEMBRANE_PROTEIN = "MEMBRANE_PROTEIN"
    VIRUS = "VIRUS"
    ORGANELLE = "ORGANELLE"
    CELL = "CELL"
    TISSUE = "TISSUE"

# Set metadata after class creation to avoid it becoming an enum member
SampleType._metadata = {
    "PROTEIN": {'description': 'Purified protein sample'},
    "NUCLEIC_ACID": {'description': 'Nucleic acid sample (DNA or RNA)'},
    "PROTEIN_COMPLEX": {'description': 'Protein-protein or protein-nucleic acid complex'},
    "MEMBRANE_PROTEIN": {'description': 'Membrane-associated protein sample'},
    "VIRUS": {'description': 'Viral particle or capsid'},
    "ORGANELLE": {'description': 'Cellular organelle (mitochondria, chloroplast, etc.)'},
    "CELL": {'description': 'Whole cell sample'},
    "TISSUE": {'description': 'Tissue sample'},
}

class StructuralBiologyTechnique(RichEnum):
    """
    Structural biology experimental techniques
    """
    # Enum members
    CRYO_EM = "CRYO_EM"
    CRYO_ET = "CRYO_ET"
    X_RAY_CRYSTALLOGRAPHY = "X_RAY_CRYSTALLOGRAPHY"
    NEUTRON_CRYSTALLOGRAPHY = "NEUTRON_CRYSTALLOGRAPHY"
    SAXS = "SAXS"
    SANS = "SANS"
    WAXS = "WAXS"
    NMR = "NMR"
    MASS_SPECTROMETRY = "MASS_SPECTROMETRY"
    NEGATIVE_STAIN_EM = "NEGATIVE_STAIN_EM"

# Set metadata after class creation to avoid it becoming an enum member
StructuralBiologyTechnique._metadata = {
    "CRYO_EM": {'description': 'Cryo-electron microscopy', 'meaning': 'CHMO:0002413', 'annotations': {'resolution_range': '2-30 Å typical', 'aliases': 'cryoEM, electron cryo-microscopy'}},
    "CRYO_ET": {'description': 'Cryo-electron tomography', 'annotations': {'resolution_range': '20-100 Å typical', 'aliases': 'cryoET, electron cryo-tomography'}},
    "X_RAY_CRYSTALLOGRAPHY": {'description': 'X-ray crystallography', 'meaning': 'CHMO:0000159', 'annotations': {'resolution_range': '1-4 Å typical', 'aliases': 'XRC, macromolecular crystallography'}},
    "NEUTRON_CRYSTALLOGRAPHY": {'description': 'Neutron crystallography', 'annotations': {'advantages': 'hydrogen positions, deuteration studies'}},
    "SAXS": {'description': 'Small-angle X-ray scattering', 'meaning': 'CHMO:0000204', 'annotations': {'information': 'low-resolution structure, conformational changes'}},
    "SANS": {'description': 'Small-angle neutron scattering', 'annotations': {'advantages': 'contrast variation with deuteration'}},
    "WAXS": {'description': 'Wide-angle X-ray scattering'},
    "NMR": {'description': 'Nuclear magnetic resonance spectroscopy', 'meaning': 'CHMO:0000591', 'annotations': {'information': 'solution structure, dynamics'}},
    "MASS_SPECTROMETRY": {'description': 'Mass spectrometry', 'meaning': 'CHMO:0000470', 'annotations': {'applications': 'native MS, crosslinking, HDX'}},
    "NEGATIVE_STAIN_EM": {'description': 'Negative stain electron microscopy', 'annotations': {'resolution_range': '15-30 Å typical'}},
}

class CryoEMPreparationType(RichEnum):
    """
    Types of cryo-EM sample preparation
    """
    # Enum members
    VITREOUS_ICE = "VITREOUS_ICE"
    CRYO_SECTIONING = "CRYO_SECTIONING"
    FREEZE_SUBSTITUTION = "FREEZE_SUBSTITUTION"
    HIGH_PRESSURE_FREEZING = "HIGH_PRESSURE_FREEZING"

# Set metadata after class creation to avoid it becoming an enum member
CryoEMPreparationType._metadata = {
    "VITREOUS_ICE": {'description': 'Sample embedded in vitreous ice'},
    "CRYO_SECTIONING": {'description': 'Cryo-sectioned sample'},
    "FREEZE_SUBSTITUTION": {'description': 'Freeze-substituted sample'},
    "HIGH_PRESSURE_FREEZING": {'description': 'High-pressure frozen sample'},
}

class CryoEMGridType(RichEnum):
    """
    Types of electron microscopy grids
    """
    # Enum members
    C_FLAT = "C_FLAT"
    QUANTIFOIL = "QUANTIFOIL"
    LACEY_CARBON = "LACEY_CARBON"
    ULTRATHIN_CARBON = "ULTRATHIN_CARBON"
    GOLD_GRID = "GOLD_GRID"
    GRAPHENE_OXIDE = "GRAPHENE_OXIDE"

# Set metadata after class creation to avoid it becoming an enum member
CryoEMGridType._metadata = {
    "C_FLAT": {'description': 'C-flat holey carbon grid', 'annotations': {'hole_sizes': '1.2/1.3, 2/1, 2/2 μm common', 'manufacturer': 'Protochips'}},
    "QUANTIFOIL": {'description': 'Quantifoil holey carbon grid', 'annotations': {'hole_sizes': '1.2/1.3, 2/1, 2/2 μm common', 'manufacturer': 'Quantifoil'}},
    "LACEY_CARBON": {'description': 'Lacey carbon support film', 'annotations': {'structure': 'irregular holes, thin carbon film'}},
    "ULTRATHIN_CARBON": {'description': 'Ultrathin carbon film on holey support', 'annotations': {'thickness': '3-5 nm typical'}},
    "GOLD_GRID": {'description': 'Pure gold grid', 'annotations': {'advantages': 'inert, high-resolution imaging'}},
    "GRAPHENE_OXIDE": {'description': 'Graphene oxide support', 'annotations': {'advantages': 'atomically thin, good contrast'}},
}

class VitrificationMethod(RichEnum):
    """
    Methods for sample vitrification
    """
    # Enum members
    PLUNGE_FREEZING = "PLUNGE_FREEZING"
    HIGH_PRESSURE_FREEZING = "HIGH_PRESSURE_FREEZING"
    SLAM_FREEZING = "SLAM_FREEZING"
    SPRAY_FREEZING = "SPRAY_FREEZING"

# Set metadata after class creation to avoid it becoming an enum member
VitrificationMethod._metadata = {
    "PLUNGE_FREEZING": {'description': 'Plunge freezing in liquid ethane', 'annotations': {'temperature': '-180°C ethane', 'equipment': 'Vitrobot, Leica GP'}},
    "HIGH_PRESSURE_FREEZING": {'description': 'High pressure freezing', 'annotations': {'pressure': '2100 bar typical', 'advantages': 'thick samples, no ice crystals'}},
    "SLAM_FREEZING": {'description': 'Slam freezing against metal block', 'annotations': {'cooling_rate': '10,000 K/s'}},
    "SPRAY_FREEZING": {'description': 'Spray freezing into liquid nitrogen', 'annotations': {'applications': 'large samples, tissues'}},
}

class CrystallizationMethod(RichEnum):
    """
    Methods for protein crystallization
    """
    # Enum members
    VAPOR_DIFFUSION_HANGING = "VAPOR_DIFFUSION_HANGING"
    VAPOR_DIFFUSION_SITTING = "VAPOR_DIFFUSION_SITTING"
    MICROBATCH = "MICROBATCH"
    DIALYSIS = "DIALYSIS"
    FREE_INTERFACE_DIFFUSION = "FREE_INTERFACE_DIFFUSION"
    LCP = "LCP"

# Set metadata after class creation to avoid it becoming an enum member
CrystallizationMethod._metadata = {
    "VAPOR_DIFFUSION_HANGING": {'description': 'Vapor diffusion hanging drop method', 'annotations': {'volume': '2-10 μL drops typical', 'advantages': 'visual monitoring, easy optimization'}},
    "VAPOR_DIFFUSION_SITTING": {'description': 'Vapor diffusion sitting drop method', 'annotations': {'advantages': 'automated setup, stable drops'}},
    "MICROBATCH": {'description': 'Microbatch under oil method', 'annotations': {'oil_type': 'paraffin, silicone oil', 'advantages': 'prevents evaporation'}},
    "DIALYSIS": {'description': 'Dialysis crystallization', 'annotations': {'applications': 'large volume samples, gentle conditions'}},
    "FREE_INTERFACE_DIFFUSION": {'description': 'Free interface diffusion', 'annotations': {'setup': 'capillary tubes, gel interface'}},
    "LCP": {'description': 'Lipidic cubic phase crystallization', 'annotations': {'applications': 'membrane proteins', 'lipid': 'monoolein most common'}},
}

class XRaySource(RichEnum):
    """
    Types of X-ray sources
    """
    # Enum members
    SYNCHROTRON = "SYNCHROTRON"
    ROTATING_ANODE = "ROTATING_ANODE"
    MICROFOCUS = "MICROFOCUS"
    METAL_JET = "METAL_JET"

# Set metadata after class creation to avoid it becoming an enum member
XRaySource._metadata = {
    "SYNCHROTRON": {'description': 'Synchrotron radiation source', 'annotations': {'advantages': 'high intensity, tunable wavelength', 'brightness': '10^15-10^18 photons/s/mm²/mrad²'}},
    "ROTATING_ANODE": {'description': 'Rotating anode generator', 'annotations': {'power': '3-18 kW typical', 'target': 'copper, molybdenum common'}},
    "MICROFOCUS": {'description': 'Microfocus sealed tube', 'annotations': {'spot_size': '10-50 μm', 'applications': 'small crystals, in-house screening'}},
    "METAL_JET": {'description': 'Liquid metal jet source', 'annotations': {'advantages': 'higher power density, longer lifetime', 'metals': 'gallium, indium'}},
}

class Detector(RichEnum):
    """
    Types of detectors for structural biology
    """
    # Enum members
    DIRECT_ELECTRON = "DIRECT_ELECTRON"
    CCD = "CCD"
    CMOS = "CMOS"
    HYBRID_PIXEL = "HYBRID_PIXEL"
    PHOTOSTIMULABLE_PHOSPHOR = "PHOTOSTIMULABLE_PHOSPHOR"

# Set metadata after class creation to avoid it becoming an enum member
Detector._metadata = {
    "DIRECT_ELECTRON": {'description': 'Direct electron detector (DED)', 'annotations': {'examples': 'K2, K3, Falcon, DE-series', 'advantages': 'high DQE, fast readout'}},
    "CCD": {'description': 'Charge-coupled device camera', 'annotations': {'applications': 'legacy EM, some crystallography'}},
    "CMOS": {'description': 'Complementary metal-oxide semiconductor detector', 'annotations': {'advantages': 'fast readout, low noise'}},
    "HYBRID_PIXEL": {'description': 'Hybrid pixel detector', 'annotations': {'examples': 'Pilatus, Eiger', 'advantages': 'photon counting, zero noise'}},
    "PHOTOSTIMULABLE_PHOSPHOR": {'description': 'Photostimulable phosphor (image plate)', 'annotations': {'applications': 'legacy crystallography'}},
}

class WorkflowType(RichEnum):
    """
    Types of computational processing workflows
    """
    # Enum members
    MOTION_CORRECTION = "MOTION_CORRECTION"
    CTF_ESTIMATION = "CTF_ESTIMATION"
    PARTICLE_PICKING = "PARTICLE_PICKING"
    CLASSIFICATION_2D = "CLASSIFICATION_2D"
    CLASSIFICATION_3D = "CLASSIFICATION_3D"
    REFINEMENT_3D = "REFINEMENT_3D"
    MODEL_BUILDING = "MODEL_BUILDING"
    MODEL_REFINEMENT = "MODEL_REFINEMENT"
    PHASING = "PHASING"
    DATA_INTEGRATION = "DATA_INTEGRATION"
    DATA_SCALING = "DATA_SCALING"
    SAXS_ANALYSIS = "SAXS_ANALYSIS"

# Set metadata after class creation to avoid it becoming an enum member
WorkflowType._metadata = {
    "MOTION_CORRECTION": {'description': 'Motion correction for cryo-EM movies', 'annotations': {'software': 'MotionCorr, Unblur, RELION'}},
    "CTF_ESTIMATION": {'description': 'Contrast transfer function estimation', 'annotations': {'software': 'CTFFIND, Gctf, RELION'}},
    "PARTICLE_PICKING": {'description': 'Particle picking from micrographs', 'annotations': {'methods': 'template matching, deep learning', 'software': 'RELION, cryoSPARC, Topaz'}},
    "CLASSIFICATION_2D": {'description': '2D classification of particles', 'annotations': {'purpose': 'sorting, cleaning particle dataset'}},
    "CLASSIFICATION_3D": {'description': '3D classification of particles', 'annotations': {'purpose': 'conformational sorting, resolution improvement'}},
    "REFINEMENT_3D": {'description': '3D refinement of particle orientations', 'annotations': {'algorithms': 'expectation maximization, gradient descent'}},
    "MODEL_BUILDING": {'description': 'Atomic model building into density', 'annotations': {'software': 'Coot, ChimeraX, Isolde'}},
    "MODEL_REFINEMENT": {'description': 'Atomic model refinement', 'annotations': {'software': 'PHENIX, REFMAC, Buster'}},
    "PHASING": {'description': 'Phase determination for crystallography', 'annotations': {'methods': 'SAD, MAD, MR, MIR'}},
    "DATA_INTEGRATION": {'description': 'Integration of diffraction data', 'annotations': {'software': 'XDS, DIALS, HKL'}},
    "DATA_SCALING": {'description': 'Scaling and merging of diffraction data', 'annotations': {'software': 'SCALA, AIMLESS, XSCALE'}},
    "SAXS_ANALYSIS": {'description': 'SAXS data analysis and modeling', 'annotations': {'software': 'PRIMUS, CRYSOL, FoXS'}},
}

class FileFormat(RichEnum):
    """
    File formats used in structural biology
    """
    # Enum members
    MRC = "MRC"
    TIFF = "TIFF"
    HDF5 = "HDF5"
    STAR = "STAR"
    PDB = "PDB"
    MMCIF = "MMCIF"
    MTZ = "MTZ"
    CBF = "CBF"
    DM3 = "DM3"
    SER = "SER"

# Set metadata after class creation to avoid it becoming an enum member
FileFormat._metadata = {
    "MRC": {'description': 'MRC format for EM density maps', 'annotations': {'extension': '.mrc, .map', 'applications': 'EM volumes, tomograms'}},
    "TIFF": {'description': 'Tagged Image File Format', 'annotations': {'extension': '.tif, .tiff', 'applications': 'micrographs, general imaging'}},
    "HDF5": {'description': 'Hierarchical Data Format 5', 'annotations': {'extension': '.h5, .hdf5', 'applications': 'large datasets, metadata storage'}},
    "STAR": {'description': 'Self-defining Text Archival and Retrieval format', 'annotations': {'extension': '.star', 'applications': 'RELION metadata, particle parameters'}},
    "PDB": {'description': 'Protein Data Bank coordinate format', 'annotations': {'extension': '.pdb', 'applications': 'atomic coordinates, legacy format'}},
    "MMCIF": {'description': 'Macromolecular Crystallographic Information File', 'annotations': {'extension': '.cif', 'applications': 'atomic coordinates, modern PDB format'}},
    "MTZ": {'description': 'MTZ reflection data format', 'annotations': {'extension': '.mtz', 'applications': 'crystallographic reflections, phases'}},
    "CBF": {'description': 'Crystallographic Binary Format', 'annotations': {'extension': '.cbf', 'applications': 'detector images, diffraction data'}},
    "DM3": {'description': 'Digital Micrograph format', 'annotations': {'extension': '.dm3, .dm4', 'applications': 'FEI/Thermo Fisher EM data'}},
    "SER": {'description': 'FEI series format', 'annotations': {'extension': '.ser', 'applications': 'FEI movie stacks'}},
}

class DataType(RichEnum):
    """
    Types of structural biology data
    """
    # Enum members
    MICROGRAPH = "MICROGRAPH"
    MOVIE = "MOVIE"
    DIFFRACTION = "DIFFRACTION"
    SCATTERING = "SCATTERING"
    PARTICLES = "PARTICLES"
    VOLUME = "VOLUME"
    TOMOGRAM = "TOMOGRAM"
    MODEL = "MODEL"
    METADATA = "METADATA"

# Set metadata after class creation to avoid it becoming an enum member
DataType._metadata = {
    "MICROGRAPH": {'description': 'Electron micrograph image', 'annotations': {'typical_size': '4k x 4k pixels'}},
    "MOVIE": {'description': 'Movie stack of frames', 'annotations': {'applications': 'motion correction, dose fractionation'}},
    "DIFFRACTION": {'description': 'X-ray diffraction pattern', 'annotations': {'information': 'structure factors, crystal lattice'}},
    "SCATTERING": {'description': 'Small-angle scattering data', 'annotations': {'information': 'I(q) vs scattering vector'}},
    "PARTICLES": {'description': 'Particle stack for single particle analysis', 'annotations': {'format': 'boxed particles, aligned'}},
    "VOLUME": {'description': '3D electron density volume', 'annotations': {'applications': 'cryo-EM maps, crystallographic maps'}},
    "TOMOGRAM": {'description': '3D tomographic reconstruction', 'annotations': {'resolution': '5-50 Å typical'}},
    "MODEL": {'description': 'Atomic coordinate model', 'annotations': {'formats': 'PDB, mmCIF'}},
    "METADATA": {'description': 'Associated metadata file', 'annotations': {'formats': 'STAR, XML, JSON'}},
}

class ProcessingStatus(RichEnum):
    """
    Status of data processing workflows
    """
    # Enum members
    RAW = "RAW"
    PREPROCESSING = "PREPROCESSING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    QUEUED = "QUEUED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"

# Set metadata after class creation to avoid it becoming an enum member
ProcessingStatus._metadata = {
    "RAW": {'description': 'Raw unprocessed data'},
    "PREPROCESSING": {'description': 'Initial preprocessing in progress'},
    "PROCESSING": {'description': 'Main processing workflow running'},
    "COMPLETED": {'description': 'Processing completed successfully'},
    "FAILED": {'description': 'Processing failed with errors'},
    "QUEUED": {'description': 'Queued for processing'},
    "PAUSED": {'description': 'Processing paused by user'},
    "CANCELLED": {'description': 'Processing cancelled by user'},
}

class InsdcMissingValueEnum(RichEnum):
    """
    INSDC (International Nucleotide Sequence Database Collaboration) controlled vocabulary for missing values in sequence records
    """
    # Enum members
    NOT_APPLICABLE = "NOT_APPLICABLE"
    MISSING = "MISSING"
    NOT_COLLECTED = "NOT_COLLECTED"
    NOT_PROVIDED = "NOT_PROVIDED"
    RESTRICTED_ACCESS = "RESTRICTED_ACCESS"
    MISSING_CONTROL_SAMPLE = "MISSING_CONTROL_SAMPLE"
    MISSING_SAMPLE_GROUP = "MISSING_SAMPLE_GROUP"
    MISSING_SYNTHETIC_CONSTRUCT = "MISSING_SYNTHETIC_CONSTRUCT"
    MISSING_LAB_STOCK = "MISSING_LAB_STOCK"
    MISSING_THIRD_PARTY_DATA = "MISSING_THIRD_PARTY_DATA"
    MISSING_DATA_AGREEMENT_ESTABLISHED_PRE_2023 = "MISSING_DATA_AGREEMENT_ESTABLISHED_PRE_2023"
    MISSING_ENDANGERED_SPECIES = "MISSING_ENDANGERED_SPECIES"
    MISSING_HUMAN_IDENTIFIABLE = "MISSING_HUMAN_IDENTIFIABLE"

# Set metadata after class creation to avoid it becoming an enum member
InsdcMissingValueEnum._metadata = {
    "NOT_APPLICABLE": {'description': 'Information is inappropriate to report, can indicate that the standard itself fails to model or represent the information appropriately', 'meaning': 'NCIT:C48660'},
    "MISSING": {'description': 'Not stated explicitly or implied by any other means', 'meaning': 'NCIT:C54031'},
    "NOT_COLLECTED": {'description': 'Information of an expected format was not given because it has never been collected', 'meaning': 'NCIT:C142610', 'annotations': {'note': 'NCIT:C142610 represents Missing Data which encompasses data not collected'}},
    "NOT_PROVIDED": {'description': 'Information of an expected format was not given, a value may be given at the later stage', 'meaning': 'NCIT:C126101', 'annotations': {'note': 'Using NCIT:C126101 (Not Available) as a general term for data not provided'}},
    "RESTRICTED_ACCESS": {'description': 'Information exists but cannot be released openly because of privacy concerns', 'meaning': 'NCIT:C67110', 'annotations': {'note': 'NCIT:C67110 represents Data Not Releasable due to confidentiality'}},
    "MISSING_CONTROL_SAMPLE": {'description': 'Information is not applicable to control samples, negative control samples (e.g. blank sample or clear sample)', 'annotations': {'note': 'No specific ontology term found for missing control sample data'}},
    "MISSING_SAMPLE_GROUP": {'description': 'Information can not be provided for a sample group where a selection of samples is used to represent a species, location or some other attribute/metric', 'annotations': {'note': 'No specific ontology term found for missing sample group data'}},
    "MISSING_SYNTHETIC_CONSTRUCT": {'description': 'Information does not exist for a synthetic construct', 'annotations': {'note': 'No specific ontology term found for missing synthetic construct data'}},
    "MISSING_LAB_STOCK": {'description': 'Information is not collected for a lab stock and its cultivation, e.g. stock centers, culture collections, seed banks', 'annotations': {'note': 'No specific ontology term found for missing lab stock data'}},
    "MISSING_THIRD_PARTY_DATA": {'description': 'Information has not been revealed by another party', 'meaning': 'NCIT:C67329', 'annotations': {'note': 'NCIT:C67329 represents Source Data Not Available'}},
    "MISSING_DATA_AGREEMENT_ESTABLISHED_PRE_2023": {'description': 'Information can not be reported due to a data agreement established before metadata standards were introduced in 2023', 'annotations': {'note': 'No specific ontology term for data missing due to pre-2023 agreements'}},
    "MISSING_ENDANGERED_SPECIES": {'description': 'Information can not be reported due to endangered species concerns', 'annotations': {'note': 'No specific ontology term for data withheld due to endangered species'}},
    "MISSING_HUMAN_IDENTIFIABLE": {'description': 'Information can not be reported due to identifiable human data concerns', 'annotations': {'note': 'No specific ontology term for data withheld due to human identifiability'}},
}

class InsdcGeographicLocationEnum(RichEnum):
    """
    INSDC controlled vocabulary for geographic locations of collected samples.
Includes countries, oceans, seas, and other geographic regions as defined by INSDC.
Countries use ISO 3166-1 alpha-2 codes from Library of Congress as canonical identifiers.
    """
    # Enum members
    AFGHANISTAN = "AFGHANISTAN"
    ALBANIA = "ALBANIA"
    ALGERIA = "ALGERIA"
    AMERICAN_SAMOA = "AMERICAN_SAMOA"
    ANDORRA = "ANDORRA"
    ANGOLA = "ANGOLA"
    ANGUILLA = "ANGUILLA"
    ANTARCTICA = "ANTARCTICA"
    ANTIGUA_AND_BARBUDA = "ANTIGUA_AND_BARBUDA"
    ARCTIC_OCEAN = "ARCTIC_OCEAN"
    ARGENTINA = "ARGENTINA"
    ARMENIA = "ARMENIA"
    ARUBA = "ARUBA"
    ASHMORE_AND_CARTIER_ISLANDS = "ASHMORE_AND_CARTIER_ISLANDS"
    ATLANTIC_OCEAN = "ATLANTIC_OCEAN"
    AUSTRALIA = "AUSTRALIA"
    AUSTRIA = "AUSTRIA"
    AZERBAIJAN = "AZERBAIJAN"
    BAHAMAS = "BAHAMAS"
    BAHRAIN = "BAHRAIN"
    BALTIC_SEA = "BALTIC_SEA"
    BAKER_ISLAND = "BAKER_ISLAND"
    BANGLADESH = "BANGLADESH"
    BARBADOS = "BARBADOS"
    BASSAS_DA_INDIA = "BASSAS_DA_INDIA"
    BELARUS = "BELARUS"
    BELGIUM = "BELGIUM"
    BELIZE = "BELIZE"
    BENIN = "BENIN"
    BERMUDA = "BERMUDA"
    BHUTAN = "BHUTAN"
    BOLIVIA = "BOLIVIA"
    BORNEO = "BORNEO"
    BOSNIA_AND_HERZEGOVINA = "BOSNIA_AND_HERZEGOVINA"
    BOTSWANA = "BOTSWANA"
    BOUVET_ISLAND = "BOUVET_ISLAND"
    BRAZIL = "BRAZIL"
    BRITISH_VIRGIN_ISLANDS = "BRITISH_VIRGIN_ISLANDS"
    BRUNEI = "BRUNEI"
    BULGARIA = "BULGARIA"
    BURKINA_FASO = "BURKINA_FASO"
    BURUNDI = "BURUNDI"
    CAMBODIA = "CAMBODIA"
    CAMEROON = "CAMEROON"
    CANADA = "CANADA"
    CAPE_VERDE = "CAPE_VERDE"
    CAYMAN_ISLANDS = "CAYMAN_ISLANDS"
    CENTRAL_AFRICAN_REPUBLIC = "CENTRAL_AFRICAN_REPUBLIC"
    CHAD = "CHAD"
    CHILE = "CHILE"
    CHINA = "CHINA"
    CHRISTMAS_ISLAND = "CHRISTMAS_ISLAND"
    CLIPPERTON_ISLAND = "CLIPPERTON_ISLAND"
    COCOS_ISLANDS = "COCOS_ISLANDS"
    COLOMBIA = "COLOMBIA"
    COMOROS = "COMOROS"
    COOK_ISLANDS = "COOK_ISLANDS"
    CORAL_SEA_ISLANDS = "CORAL_SEA_ISLANDS"
    COSTA_RICA = "COSTA_RICA"
    COTE_DIVOIRE = "COTE_DIVOIRE"
    CROATIA = "CROATIA"
    CUBA = "CUBA"
    CURACAO = "CURACAO"
    CYPRUS = "CYPRUS"
    CZECHIA = "CZECHIA"
    DEMOCRATIC_REPUBLIC_OF_THE_CONGO = "DEMOCRATIC_REPUBLIC_OF_THE_CONGO"
    DENMARK = "DENMARK"
    DJIBOUTI = "DJIBOUTI"
    DOMINICA = "DOMINICA"
    DOMINICAN_REPUBLIC = "DOMINICAN_REPUBLIC"
    ECUADOR = "ECUADOR"
    EGYPT = "EGYPT"
    EL_SALVADOR = "EL_SALVADOR"
    EQUATORIAL_GUINEA = "EQUATORIAL_GUINEA"
    ERITREA = "ERITREA"
    ESTONIA = "ESTONIA"
    ESWATINI = "ESWATINI"
    ETHIOPIA = "ETHIOPIA"
    EUROPA_ISLAND = "EUROPA_ISLAND"
    FALKLAND_ISLANDS = "FALKLAND_ISLANDS"
    FAROE_ISLANDS = "FAROE_ISLANDS"
    FIJI = "FIJI"
    FINLAND = "FINLAND"
    FRANCE = "FRANCE"
    FRENCH_GUIANA = "FRENCH_GUIANA"
    FRENCH_POLYNESIA = "FRENCH_POLYNESIA"
    FRENCH_SOUTHERN_AND_ANTARCTIC_LANDS = "FRENCH_SOUTHERN_AND_ANTARCTIC_LANDS"
    GABON = "GABON"
    GAMBIA = "GAMBIA"
    GAZA_STRIP = "GAZA_STRIP"
    GEORGIA = "GEORGIA"
    GERMANY = "GERMANY"
    GHANA = "GHANA"
    GIBRALTAR = "GIBRALTAR"
    GLORIOSO_ISLANDS = "GLORIOSO_ISLANDS"
    GREECE = "GREECE"
    GREENLAND = "GREENLAND"
    GRENADA = "GRENADA"
    GUADELOUPE = "GUADELOUPE"
    GUAM = "GUAM"
    GUATEMALA = "GUATEMALA"
    GUERNSEY = "GUERNSEY"
    GUINEA = "GUINEA"
    GUINEA_BISSAU = "GUINEA_BISSAU"
    GUYANA = "GUYANA"
    HAITI = "HAITI"
    HEARD_ISLAND_AND_MCDONALD_ISLANDS = "HEARD_ISLAND_AND_MCDONALD_ISLANDS"
    HONDURAS = "HONDURAS"
    HONG_KONG = "HONG_KONG"
    HOWLAND_ISLAND = "HOWLAND_ISLAND"
    HUNGARY = "HUNGARY"
    ICELAND = "ICELAND"
    INDIA = "INDIA"
    INDIAN_OCEAN = "INDIAN_OCEAN"
    INDONESIA = "INDONESIA"
    IRAN = "IRAN"
    IRAQ = "IRAQ"
    IRELAND = "IRELAND"
    ISLE_OF_MAN = "ISLE_OF_MAN"
    ISRAEL = "ISRAEL"
    ITALY = "ITALY"
    JAMAICA = "JAMAICA"
    JAN_MAYEN = "JAN_MAYEN"
    JAPAN = "JAPAN"
    JARVIS_ISLAND = "JARVIS_ISLAND"
    JERSEY = "JERSEY"
    JOHNSTON_ATOLL = "JOHNSTON_ATOLL"
    JORDAN = "JORDAN"
    JUAN_DE_NOVA_ISLAND = "JUAN_DE_NOVA_ISLAND"
    KAZAKHSTAN = "KAZAKHSTAN"
    KENYA = "KENYA"
    KERGUELEN_ARCHIPELAGO = "KERGUELEN_ARCHIPELAGO"
    KINGMAN_REEF = "KINGMAN_REEF"
    KIRIBATI = "KIRIBATI"
    KOSOVO = "KOSOVO"
    KUWAIT = "KUWAIT"
    KYRGYZSTAN = "KYRGYZSTAN"
    LAOS = "LAOS"
    LATVIA = "LATVIA"
    LEBANON = "LEBANON"
    LESOTHO = "LESOTHO"
    LIBERIA = "LIBERIA"
    LIBYA = "LIBYA"
    LIECHTENSTEIN = "LIECHTENSTEIN"
    LINE_ISLANDS = "LINE_ISLANDS"
    LITHUANIA = "LITHUANIA"
    LUXEMBOURG = "LUXEMBOURG"
    MACAU = "MACAU"
    MADAGASCAR = "MADAGASCAR"
    MALAWI = "MALAWI"
    MALAYSIA = "MALAYSIA"
    MALDIVES = "MALDIVES"
    MALI = "MALI"
    MALTA = "MALTA"
    MARSHALL_ISLANDS = "MARSHALL_ISLANDS"
    MARTINIQUE = "MARTINIQUE"
    MAURITANIA = "MAURITANIA"
    MAURITIUS = "MAURITIUS"
    MAYOTTE = "MAYOTTE"
    MEDITERRANEAN_SEA = "MEDITERRANEAN_SEA"
    MEXICO = "MEXICO"
    MICRONESIA_FEDERATED_STATES_OF = "MICRONESIA_FEDERATED_STATES_OF"
    MIDWAY_ISLANDS = "MIDWAY_ISLANDS"
    MOLDOVA = "MOLDOVA"
    MONACO = "MONACO"
    MONGOLIA = "MONGOLIA"
    MONTENEGRO = "MONTENEGRO"
    MONTSERRAT = "MONTSERRAT"
    MOROCCO = "MOROCCO"
    MOZAMBIQUE = "MOZAMBIQUE"
    MYANMAR = "MYANMAR"
    NAMIBIA = "NAMIBIA"
    NAURU = "NAURU"
    NAVASSA_ISLAND = "NAVASSA_ISLAND"
    NEPAL = "NEPAL"
    NETHERLANDS = "NETHERLANDS"
    NEW_CALEDONIA = "NEW_CALEDONIA"
    NEW_ZEALAND = "NEW_ZEALAND"
    NICARAGUA = "NICARAGUA"
    NIGER = "NIGER"
    NIGERIA = "NIGERIA"
    NIUE = "NIUE"
    NORFOLK_ISLAND = "NORFOLK_ISLAND"
    NORTH_KOREA = "NORTH_KOREA"
    NORTH_MACEDONIA = "NORTH_MACEDONIA"
    NORTH_SEA = "NORTH_SEA"
    NORTHERN_MARIANA_ISLANDS = "NORTHERN_MARIANA_ISLANDS"
    NORWAY = "NORWAY"
    OMAN = "OMAN"
    PACIFIC_OCEAN = "PACIFIC_OCEAN"
    PAKISTAN = "PAKISTAN"
    PALAU = "PALAU"
    PALMYRA_ATOLL = "PALMYRA_ATOLL"
    PANAMA = "PANAMA"
    PAPUA_NEW_GUINEA = "PAPUA_NEW_GUINEA"
    PARACEL_ISLANDS = "PARACEL_ISLANDS"
    PARAGUAY = "PARAGUAY"
    PERU = "PERU"
    PHILIPPINES = "PHILIPPINES"
    PITCAIRN_ISLANDS = "PITCAIRN_ISLANDS"
    POLAND = "POLAND"
    PORTUGAL = "PORTUGAL"
    PUERTO_RICO = "PUERTO_RICO"
    QATAR = "QATAR"
    REPUBLIC_OF_THE_CONGO = "REPUBLIC_OF_THE_CONGO"
    REUNION = "REUNION"
    ROMANIA = "ROMANIA"
    ROSS_SEA = "ROSS_SEA"
    RUSSIA = "RUSSIA"
    RWANDA = "RWANDA"
    SAINT_BARTHELEMY = "SAINT_BARTHELEMY"
    SAINT_HELENA = "SAINT_HELENA"
    SAINT_KITTS_AND_NEVIS = "SAINT_KITTS_AND_NEVIS"
    SAINT_LUCIA = "SAINT_LUCIA"
    SAINT_MARTIN = "SAINT_MARTIN"
    SAINT_PIERRE_AND_MIQUELON = "SAINT_PIERRE_AND_MIQUELON"
    SAINT_VINCENT_AND_THE_GRENADINES = "SAINT_VINCENT_AND_THE_GRENADINES"
    SAMOA = "SAMOA"
    SAN_MARINO = "SAN_MARINO"
    SAO_TOME_AND_PRINCIPE = "SAO_TOME_AND_PRINCIPE"
    SAUDI_ARABIA = "SAUDI_ARABIA"
    SENEGAL = "SENEGAL"
    SERBIA = "SERBIA"
    SEYCHELLES = "SEYCHELLES"
    SIERRA_LEONE = "SIERRA_LEONE"
    SINGAPORE = "SINGAPORE"
    SINT_MAARTEN = "SINT_MAARTEN"
    SLOVAKIA = "SLOVAKIA"
    SLOVENIA = "SLOVENIA"
    SOLOMON_ISLANDS = "SOLOMON_ISLANDS"
    SOMALIA = "SOMALIA"
    SOUTH_AFRICA = "SOUTH_AFRICA"
    SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS = "SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS"
    SOUTH_KOREA = "SOUTH_KOREA"
    SOUTH_SUDAN = "SOUTH_SUDAN"
    SOUTHERN_OCEAN = "SOUTHERN_OCEAN"
    SPAIN = "SPAIN"
    SPRATLY_ISLANDS = "SPRATLY_ISLANDS"
    SRI_LANKA = "SRI_LANKA"
    STATE_OF_PALESTINE = "STATE_OF_PALESTINE"
    SUDAN = "SUDAN"
    SURINAME = "SURINAME"
    SVALBARD = "SVALBARD"
    SWEDEN = "SWEDEN"
    SWITZERLAND = "SWITZERLAND"
    SYRIA = "SYRIA"
    TAIWAN = "TAIWAN"
    TAJIKISTAN = "TAJIKISTAN"
    TANZANIA = "TANZANIA"
    TASMAN_SEA = "TASMAN_SEA"
    THAILAND = "THAILAND"
    TIMOR_LESTE = "TIMOR_LESTE"
    TOGO = "TOGO"
    TOKELAU = "TOKELAU"
    TONGA = "TONGA"
    TRINIDAD_AND_TOBAGO = "TRINIDAD_AND_TOBAGO"
    TROMELIN_ISLAND = "TROMELIN_ISLAND"
    TUNISIA = "TUNISIA"
    TURKEY = "TURKEY"
    TURKMENISTAN = "TURKMENISTAN"
    TURKS_AND_CAICOS_ISLANDS = "TURKS_AND_CAICOS_ISLANDS"
    TUVALU = "TUVALU"
    UGANDA = "UGANDA"
    UKRAINE = "UKRAINE"
    UNITED_ARAB_EMIRATES = "UNITED_ARAB_EMIRATES"
    UNITED_KINGDOM = "UNITED_KINGDOM"
    URUGUAY = "URUGUAY"
    USA = "USA"
    UZBEKISTAN = "UZBEKISTAN"
    VANUATU = "VANUATU"
    VENEZUELA = "VENEZUELA"
    VIET_NAM = "VIET_NAM"
    VIRGIN_ISLANDS = "VIRGIN_ISLANDS"
    WAKE_ISLAND = "WAKE_ISLAND"
    WALLIS_AND_FUTUNA = "WALLIS_AND_FUTUNA"
    WEST_BANK = "WEST_BANK"
    WESTERN_SAHARA = "WESTERN_SAHARA"
    YEMEN = "YEMEN"
    ZAMBIA = "ZAMBIA"
    ZIMBABWE = "ZIMBABWE"

# Set metadata after class creation to avoid it becoming an enum member
InsdcGeographicLocationEnum._metadata = {
    "AFGHANISTAN": {'description': 'Afghanistan', 'meaning': 'iso3166loc:af'},
    "ALBANIA": {'description': 'Albania', 'meaning': 'iso3166loc:al'},
    "ALGERIA": {'description': 'Algeria', 'meaning': 'iso3166loc:dz'},
    "AMERICAN_SAMOA": {'description': 'American Samoa', 'meaning': 'iso3166loc:as'},
    "ANDORRA": {'description': 'Andorra', 'meaning': 'iso3166loc:ad'},
    "ANGOLA": {'description': 'Angola', 'meaning': 'iso3166loc:ao'},
    "ANGUILLA": {'description': 'Anguilla', 'meaning': 'iso3166loc:ai'},
    "ANTARCTICA": {'description': 'Antarctica', 'meaning': 'iso3166loc:aq'},
    "ANTIGUA_AND_BARBUDA": {'description': 'Antigua and Barbuda', 'meaning': 'iso3166loc:ag'},
    "ARCTIC_OCEAN": {'description': 'Arctic Ocean', 'meaning': 'geonames:3371123/'},
    "ARGENTINA": {'description': 'Argentina', 'meaning': 'iso3166loc:ar'},
    "ARMENIA": {'description': 'Armenia', 'meaning': 'iso3166loc:am'},
    "ARUBA": {'description': 'Aruba', 'meaning': 'iso3166loc:aw'},
    "ASHMORE_AND_CARTIER_ISLANDS": {'description': 'Ashmore and Cartier Islands', 'annotations': {'note': 'Australian external territory'}},
    "ATLANTIC_OCEAN": {'description': 'Atlantic Ocean', 'meaning': 'geonames:3411923/'},
    "AUSTRALIA": {'description': 'Australia', 'meaning': 'iso3166loc:au'},
    "AUSTRIA": {'description': 'Austria', 'meaning': 'iso3166loc:at'},
    "AZERBAIJAN": {'description': 'Azerbaijan', 'meaning': 'iso3166loc:az'},
    "BAHAMAS": {'description': 'Bahamas', 'meaning': 'iso3166loc:bs'},
    "BAHRAIN": {'description': 'Bahrain', 'meaning': 'iso3166loc:bh'},
    "BALTIC_SEA": {'description': 'Baltic Sea', 'meaning': 'geonames:2673730/'},
    "BAKER_ISLAND": {'description': 'Baker Island', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "BANGLADESH": {'description': 'Bangladesh', 'meaning': 'iso3166loc:bd'},
    "BARBADOS": {'description': 'Barbados', 'meaning': 'iso3166loc:bb'},
    "BASSAS_DA_INDIA": {'description': 'Bassas da India', 'annotations': {'note': 'French Southern and Antarctic Lands territory'}},
    "BELARUS": {'description': 'Belarus', 'meaning': 'iso3166loc:by'},
    "BELGIUM": {'description': 'Belgium', 'meaning': 'iso3166loc:be'},
    "BELIZE": {'description': 'Belize', 'meaning': 'iso3166loc:bz'},
    "BENIN": {'description': 'Benin', 'meaning': 'iso3166loc:bj'},
    "BERMUDA": {'description': 'Bermuda', 'meaning': 'iso3166loc:bm'},
    "BHUTAN": {'description': 'Bhutan', 'meaning': 'iso3166loc:bt'},
    "BOLIVIA": {'description': 'Bolivia', 'meaning': 'iso3166loc:bo'},
    "BORNEO": {'description': 'Borneo', 'meaning': 'geonames:1642188/', 'annotations': {'note': 'Island shared by Brunei, Indonesia, and Malaysia'}},
    "BOSNIA_AND_HERZEGOVINA": {'description': 'Bosnia and Herzegovina', 'meaning': 'iso3166loc:ba'},
    "BOTSWANA": {'description': 'Botswana', 'meaning': 'iso3166loc:bw'},
    "BOUVET_ISLAND": {'description': 'Bouvet Island', 'meaning': 'iso3166loc:bv'},
    "BRAZIL": {'description': 'Brazil', 'meaning': 'iso3166loc:br'},
    "BRITISH_VIRGIN_ISLANDS": {'description': 'British Virgin Islands', 'meaning': 'iso3166loc:vg'},
    "BRUNEI": {'description': 'Brunei', 'meaning': 'iso3166loc:bn'},
    "BULGARIA": {'description': 'Bulgaria', 'meaning': 'iso3166loc:bg'},
    "BURKINA_FASO": {'description': 'Burkina Faso', 'meaning': 'iso3166loc:bf'},
    "BURUNDI": {'description': 'Burundi', 'meaning': 'iso3166loc:bi'},
    "CAMBODIA": {'description': 'Cambodia', 'meaning': 'iso3166loc:kh'},
    "CAMEROON": {'description': 'Cameroon', 'meaning': 'iso3166loc:cm'},
    "CANADA": {'description': 'Canada', 'meaning': 'iso3166loc:ca'},
    "CAPE_VERDE": {'description': 'Cape Verde', 'meaning': 'iso3166loc:cv'},
    "CAYMAN_ISLANDS": {'description': 'Cayman Islands', 'meaning': 'iso3166loc:ky'},
    "CENTRAL_AFRICAN_REPUBLIC": {'description': 'Central African Republic', 'meaning': 'iso3166loc:cf'},
    "CHAD": {'description': 'Chad', 'meaning': 'iso3166loc:td'},
    "CHILE": {'description': 'Chile', 'meaning': 'iso3166loc:cl'},
    "CHINA": {'description': 'China', 'meaning': 'iso3166loc:cn'},
    "CHRISTMAS_ISLAND": {'description': 'Christmas Island', 'meaning': 'iso3166loc:cx'},
    "CLIPPERTON_ISLAND": {'description': 'Clipperton Island', 'annotations': {'note': 'French overseas territory'}},
    "COCOS_ISLANDS": {'description': 'Cocos Islands', 'meaning': 'iso3166loc:cc'},
    "COLOMBIA": {'description': 'Colombia', 'meaning': 'iso3166loc:co'},
    "COMOROS": {'description': 'Comoros', 'meaning': 'iso3166loc:km'},
    "COOK_ISLANDS": {'description': 'Cook Islands', 'meaning': 'iso3166loc:ck'},
    "CORAL_SEA_ISLANDS": {'description': 'Coral Sea Islands', 'annotations': {'note': 'Australian external territory'}},
    "COSTA_RICA": {'description': 'Costa Rica', 'meaning': 'iso3166loc:cr'},
    "COTE_DIVOIRE": {'description': "Cote d'Ivoire", 'meaning': 'iso3166loc:ci'},
    "CROATIA": {'description': 'Croatia', 'meaning': 'iso3166loc:hr'},
    "CUBA": {'description': 'Cuba', 'meaning': 'iso3166loc:cu'},
    "CURACAO": {'description': 'Curacao', 'meaning': 'iso3166loc:cw'},
    "CYPRUS": {'description': 'Cyprus', 'meaning': 'iso3166loc:cy'},
    "CZECHIA": {'description': 'Czechia', 'meaning': 'iso3166loc:cz'},
    "DEMOCRATIC_REPUBLIC_OF_THE_CONGO": {'description': 'Democratic Republic of the Congo', 'meaning': 'iso3166loc:cd'},
    "DENMARK": {'description': 'Denmark', 'meaning': 'iso3166loc:dk'},
    "DJIBOUTI": {'description': 'Djibouti', 'meaning': 'iso3166loc:dj'},
    "DOMINICA": {'description': 'Dominica', 'meaning': 'iso3166loc:dm'},
    "DOMINICAN_REPUBLIC": {'description': 'Dominican Republic', 'meaning': 'iso3166loc:do'},
    "ECUADOR": {'description': 'Ecuador', 'meaning': 'iso3166loc:ec'},
    "EGYPT": {'description': 'Egypt', 'meaning': 'iso3166loc:eg'},
    "EL_SALVADOR": {'description': 'El Salvador', 'meaning': 'iso3166loc:sv'},
    "EQUATORIAL_GUINEA": {'description': 'Equatorial Guinea', 'meaning': 'iso3166loc:gq'},
    "ERITREA": {'description': 'Eritrea', 'meaning': 'iso3166loc:er'},
    "ESTONIA": {'description': 'Estonia', 'meaning': 'iso3166loc:ee'},
    "ESWATINI": {'description': 'Eswatini', 'meaning': 'iso3166loc:sz'},
    "ETHIOPIA": {'description': 'Ethiopia', 'meaning': 'iso3166loc:et'},
    "EUROPA_ISLAND": {'description': 'Europa Island', 'annotations': {'note': 'French Southern and Antarctic Lands territory'}},
    "FALKLAND_ISLANDS": {'description': 'Falkland Islands (Islas Malvinas)', 'meaning': 'iso3166loc:fk'},
    "FAROE_ISLANDS": {'description': 'Faroe Islands', 'meaning': 'iso3166loc:fo'},
    "FIJI": {'description': 'Fiji', 'meaning': 'iso3166loc:fj'},
    "FINLAND": {'description': 'Finland', 'meaning': 'iso3166loc:fi'},
    "FRANCE": {'description': 'France', 'meaning': 'iso3166loc:fr'},
    "FRENCH_GUIANA": {'description': 'French Guiana', 'meaning': 'iso3166loc:gf'},
    "FRENCH_POLYNESIA": {'description': 'French Polynesia', 'meaning': 'iso3166loc:pf'},
    "FRENCH_SOUTHERN_AND_ANTARCTIC_LANDS": {'description': 'French Southern and Antarctic Lands', 'meaning': 'iso3166loc:tf'},
    "GABON": {'description': 'Gabon', 'meaning': 'iso3166loc:ga'},
    "GAMBIA": {'description': 'Gambia', 'meaning': 'iso3166loc:gm'},
    "GAZA_STRIP": {'description': 'Gaza Strip', 'annotations': {'note': 'Palestinian territory'}},
    "GEORGIA": {'description': 'Georgia', 'meaning': 'iso3166loc:ge'},
    "GERMANY": {'description': 'Germany', 'meaning': 'iso3166loc:de'},
    "GHANA": {'description': 'Ghana', 'meaning': 'iso3166loc:gh'},
    "GIBRALTAR": {'description': 'Gibraltar', 'meaning': 'iso3166loc:gi'},
    "GLORIOSO_ISLANDS": {'description': 'Glorioso Islands', 'annotations': {'note': 'French Southern and Antarctic Lands territory'}},
    "GREECE": {'description': 'Greece', 'meaning': 'iso3166loc:gr'},
    "GREENLAND": {'description': 'Greenland', 'meaning': 'iso3166loc:gl'},
    "GRENADA": {'description': 'Grenada', 'meaning': 'iso3166loc:gd'},
    "GUADELOUPE": {'description': 'Guadeloupe', 'meaning': 'iso3166loc:gp'},
    "GUAM": {'description': 'Guam', 'meaning': 'iso3166loc:gu'},
    "GUATEMALA": {'description': 'Guatemala', 'meaning': 'iso3166loc:gt'},
    "GUERNSEY": {'description': 'Guernsey', 'meaning': 'iso3166loc:gg'},
    "GUINEA": {'description': 'Guinea', 'meaning': 'iso3166loc:gn'},
    "GUINEA_BISSAU": {'description': 'Guinea-Bissau', 'meaning': 'iso3166loc:gw'},
    "GUYANA": {'description': 'Guyana', 'meaning': 'iso3166loc:gy'},
    "HAITI": {'description': 'Haiti', 'meaning': 'iso3166loc:ht'},
    "HEARD_ISLAND_AND_MCDONALD_ISLANDS": {'description': 'Heard Island and McDonald Islands', 'meaning': 'iso3166loc:hm'},
    "HONDURAS": {'description': 'Honduras', 'meaning': 'iso3166loc:hn'},
    "HONG_KONG": {'description': 'Hong Kong', 'meaning': 'iso3166loc:hk'},
    "HOWLAND_ISLAND": {'description': 'Howland Island', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "HUNGARY": {'description': 'Hungary', 'meaning': 'iso3166loc:hu'},
    "ICELAND": {'description': 'Iceland', 'meaning': 'iso3166loc:is'},
    "INDIA": {'description': 'India', 'meaning': 'iso3166loc:in'},
    "INDIAN_OCEAN": {'description': 'Indian Ocean', 'meaning': 'geonames:1545739/'},
    "INDONESIA": {'description': 'Indonesia', 'meaning': 'iso3166loc:id'},
    "IRAN": {'description': 'Iran', 'meaning': 'iso3166loc:ir'},
    "IRAQ": {'description': 'Iraq', 'meaning': 'iso3166loc:iq'},
    "IRELAND": {'description': 'Ireland', 'meaning': 'iso3166loc:ie'},
    "ISLE_OF_MAN": {'description': 'Isle of Man', 'meaning': 'iso3166loc:im'},
    "ISRAEL": {'description': 'Israel', 'meaning': 'iso3166loc:il'},
    "ITALY": {'description': 'Italy', 'meaning': 'iso3166loc:it'},
    "JAMAICA": {'description': 'Jamaica', 'meaning': 'iso3166loc:jm'},
    "JAN_MAYEN": {'description': 'Jan Mayen', 'annotations': {'note': 'Norwegian territory'}},
    "JAPAN": {'description': 'Japan', 'meaning': 'iso3166loc:jp'},
    "JARVIS_ISLAND": {'description': 'Jarvis Island', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "JERSEY": {'description': 'Jersey', 'meaning': 'iso3166loc:je'},
    "JOHNSTON_ATOLL": {'description': 'Johnston Atoll', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "JORDAN": {'description': 'Jordan', 'meaning': 'iso3166loc:jo'},
    "JUAN_DE_NOVA_ISLAND": {'description': 'Juan de Nova Island', 'annotations': {'note': 'French Southern and Antarctic Lands territory'}},
    "KAZAKHSTAN": {'description': 'Kazakhstan', 'meaning': 'iso3166loc:kz'},
    "KENYA": {'description': 'Kenya', 'meaning': 'iso3166loc:ke'},
    "KERGUELEN_ARCHIPELAGO": {'description': 'Kerguelen Archipelago', 'annotations': {'note': 'French Southern and Antarctic Lands territory'}},
    "KINGMAN_REEF": {'description': 'Kingman Reef', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "KIRIBATI": {'description': 'Kiribati', 'meaning': 'iso3166loc:ki'},
    "KOSOVO": {'description': 'Kosovo', 'meaning': 'iso3166loc:xk', 'annotations': {'note': 'Provisional ISO 3166 code'}},
    "KUWAIT": {'description': 'Kuwait', 'meaning': 'iso3166loc:kw'},
    "KYRGYZSTAN": {'description': 'Kyrgyzstan', 'meaning': 'iso3166loc:kg'},
    "LAOS": {'description': 'Laos', 'meaning': 'iso3166loc:la'},
    "LATVIA": {'description': 'Latvia', 'meaning': 'iso3166loc:lv'},
    "LEBANON": {'description': 'Lebanon', 'meaning': 'iso3166loc:lb'},
    "LESOTHO": {'description': 'Lesotho', 'meaning': 'iso3166loc:ls'},
    "LIBERIA": {'description': 'Liberia', 'meaning': 'iso3166loc:lr'},
    "LIBYA": {'description': 'Libya', 'meaning': 'iso3166loc:ly'},
    "LIECHTENSTEIN": {'description': 'Liechtenstein', 'meaning': 'iso3166loc:li'},
    "LINE_ISLANDS": {'description': 'Line Islands', 'annotations': {'note': 'Island group in Pacific Ocean (part of Kiribati)'}},
    "LITHUANIA": {'description': 'Lithuania', 'meaning': 'iso3166loc:lt'},
    "LUXEMBOURG": {'description': 'Luxembourg', 'meaning': 'iso3166loc:lu'},
    "MACAU": {'description': 'Macau', 'meaning': 'iso3166loc:mo'},
    "MADAGASCAR": {'description': 'Madagascar', 'meaning': 'iso3166loc:mg'},
    "MALAWI": {'description': 'Malawi', 'meaning': 'iso3166loc:mw'},
    "MALAYSIA": {'description': 'Malaysia', 'meaning': 'iso3166loc:my'},
    "MALDIVES": {'description': 'Maldives', 'meaning': 'iso3166loc:mv'},
    "MALI": {'description': 'Mali', 'meaning': 'iso3166loc:ml'},
    "MALTA": {'description': 'Malta', 'meaning': 'iso3166loc:mt'},
    "MARSHALL_ISLANDS": {'description': 'Marshall Islands', 'meaning': 'iso3166loc:mh'},
    "MARTINIQUE": {'description': 'Martinique', 'meaning': 'iso3166loc:mq'},
    "MAURITANIA": {'description': 'Mauritania', 'meaning': 'iso3166loc:mr'},
    "MAURITIUS": {'description': 'Mauritius', 'meaning': 'iso3166loc:mu'},
    "MAYOTTE": {'description': 'Mayotte', 'meaning': 'iso3166loc:yt'},
    "MEDITERRANEAN_SEA": {'description': 'Mediterranean Sea', 'meaning': 'geonames:2593778/'},
    "MEXICO": {'description': 'Mexico', 'meaning': 'iso3166loc:mx'},
    "MICRONESIA_FEDERATED_STATES_OF": {'description': 'Micronesia, Federated States of', 'meaning': 'iso3166loc:fm'},
    "MIDWAY_ISLANDS": {'description': 'Midway Islands', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "MOLDOVA": {'description': 'Moldova', 'meaning': 'iso3166loc:md'},
    "MONACO": {'description': 'Monaco', 'meaning': 'iso3166loc:mc'},
    "MONGOLIA": {'description': 'Mongolia', 'meaning': 'iso3166loc:mn'},
    "MONTENEGRO": {'description': 'Montenegro', 'meaning': 'iso3166loc:me'},
    "MONTSERRAT": {'description': 'Montserrat', 'meaning': 'iso3166loc:ms'},
    "MOROCCO": {'description': 'Morocco', 'meaning': 'iso3166loc:ma'},
    "MOZAMBIQUE": {'description': 'Mozambique', 'meaning': 'iso3166loc:mz'},
    "MYANMAR": {'description': 'Myanmar', 'meaning': 'iso3166loc:mm'},
    "NAMIBIA": {'description': 'Namibia', 'meaning': 'iso3166loc:na'},
    "NAURU": {'description': 'Nauru', 'meaning': 'iso3166loc:nr'},
    "NAVASSA_ISLAND": {'description': 'Navassa Island', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "NEPAL": {'description': 'Nepal', 'meaning': 'iso3166loc:np'},
    "NETHERLANDS": {'description': 'Netherlands', 'meaning': 'iso3166loc:nl'},
    "NEW_CALEDONIA": {'description': 'New Caledonia', 'meaning': 'iso3166loc:nc'},
    "NEW_ZEALAND": {'description': 'New Zealand', 'meaning': 'iso3166loc:nz'},
    "NICARAGUA": {'description': 'Nicaragua', 'meaning': 'iso3166loc:ni'},
    "NIGER": {'description': 'Niger', 'meaning': 'iso3166loc:ne'},
    "NIGERIA": {'description': 'Nigeria', 'meaning': 'iso3166loc:ng'},
    "NIUE": {'description': 'Niue', 'meaning': 'iso3166loc:nu'},
    "NORFOLK_ISLAND": {'description': 'Norfolk Island', 'meaning': 'iso3166loc:nf'},
    "NORTH_KOREA": {'description': 'North Korea', 'meaning': 'iso3166loc:kp'},
    "NORTH_MACEDONIA": {'description': 'North Macedonia', 'meaning': 'iso3166loc:mk'},
    "NORTH_SEA": {'description': 'North Sea', 'meaning': 'geonames:2960848/'},
    "NORTHERN_MARIANA_ISLANDS": {'description': 'Northern Mariana Islands', 'meaning': 'iso3166loc:mp'},
    "NORWAY": {'description': 'Norway', 'meaning': 'iso3166loc:no'},
    "OMAN": {'description': 'Oman', 'meaning': 'iso3166loc:om'},
    "PACIFIC_OCEAN": {'description': 'Pacific Ocean', 'meaning': 'geonames:2363254/'},
    "PAKISTAN": {'description': 'Pakistan', 'meaning': 'iso3166loc:pk'},
    "PALAU": {'description': 'Palau', 'meaning': 'iso3166loc:pw'},
    "PALMYRA_ATOLL": {'description': 'Palmyra Atoll', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "PANAMA": {'description': 'Panama', 'meaning': 'iso3166loc:pa'},
    "PAPUA_NEW_GUINEA": {'description': 'Papua New Guinea', 'meaning': 'iso3166loc:pg'},
    "PARACEL_ISLANDS": {'description': 'Paracel Islands', 'annotations': {'note': 'Disputed territory in South China Sea'}},
    "PARAGUAY": {'description': 'Paraguay', 'meaning': 'iso3166loc:py'},
    "PERU": {'description': 'Peru', 'meaning': 'iso3166loc:pe'},
    "PHILIPPINES": {'description': 'Philippines', 'meaning': 'iso3166loc:ph'},
    "PITCAIRN_ISLANDS": {'description': 'Pitcairn Islands', 'meaning': 'iso3166loc:pn'},
    "POLAND": {'description': 'Poland', 'meaning': 'iso3166loc:pl'},
    "PORTUGAL": {'description': 'Portugal', 'meaning': 'iso3166loc:pt'},
    "PUERTO_RICO": {'description': 'Puerto Rico', 'meaning': 'iso3166loc:pr'},
    "QATAR": {'description': 'Qatar', 'meaning': 'iso3166loc:qa'},
    "REPUBLIC_OF_THE_CONGO": {'description': 'Republic of the Congo', 'meaning': 'iso3166loc:cg'},
    "REUNION": {'description': 'Reunion', 'meaning': 'iso3166loc:re'},
    "ROMANIA": {'description': 'Romania', 'meaning': 'iso3166loc:ro'},
    "ROSS_SEA": {'description': 'Ross Sea', 'meaning': 'geonames:4036621/'},
    "RUSSIA": {'description': 'Russia', 'meaning': 'iso3166loc:ru'},
    "RWANDA": {'description': 'Rwanda', 'meaning': 'iso3166loc:rw'},
    "SAINT_BARTHELEMY": {'description': 'Saint Barthelemy', 'meaning': 'iso3166loc:bl'},
    "SAINT_HELENA": {'description': 'Saint Helena', 'meaning': 'iso3166loc:sh'},
    "SAINT_KITTS_AND_NEVIS": {'description': 'Saint Kitts and Nevis', 'meaning': 'iso3166loc:kn'},
    "SAINT_LUCIA": {'description': 'Saint Lucia', 'meaning': 'iso3166loc:lc'},
    "SAINT_MARTIN": {'description': 'Saint Martin', 'meaning': 'iso3166loc:mf'},
    "SAINT_PIERRE_AND_MIQUELON": {'description': 'Saint Pierre and Miquelon', 'meaning': 'iso3166loc:pm'},
    "SAINT_VINCENT_AND_THE_GRENADINES": {'description': 'Saint Vincent and the Grenadines', 'meaning': 'iso3166loc:vc'},
    "SAMOA": {'description': 'Samoa', 'meaning': 'iso3166loc:ws'},
    "SAN_MARINO": {'description': 'San Marino', 'meaning': 'iso3166loc:sm'},
    "SAO_TOME_AND_PRINCIPE": {'description': 'Sao Tome and Principe', 'meaning': 'iso3166loc:st'},
    "SAUDI_ARABIA": {'description': 'Saudi Arabia', 'meaning': 'iso3166loc:sa'},
    "SENEGAL": {'description': 'Senegal', 'meaning': 'iso3166loc:sn'},
    "SERBIA": {'description': 'Serbia', 'meaning': 'iso3166loc:rs'},
    "SEYCHELLES": {'description': 'Seychelles', 'meaning': 'iso3166loc:sc'},
    "SIERRA_LEONE": {'description': 'Sierra Leone', 'meaning': 'iso3166loc:sl'},
    "SINGAPORE": {'description': 'Singapore', 'meaning': 'iso3166loc:sg'},
    "SINT_MAARTEN": {'description': 'Sint Maarten', 'meaning': 'iso3166loc:sx'},
    "SLOVAKIA": {'description': 'Slovakia', 'meaning': 'iso3166loc:sk'},
    "SLOVENIA": {'description': 'Slovenia', 'meaning': 'iso3166loc:si'},
    "SOLOMON_ISLANDS": {'description': 'Solomon Islands', 'meaning': 'iso3166loc:sb'},
    "SOMALIA": {'description': 'Somalia', 'meaning': 'iso3166loc:so'},
    "SOUTH_AFRICA": {'description': 'South Africa', 'meaning': 'iso3166loc:za'},
    "SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS": {'description': 'South Georgia and the South Sandwich Islands', 'meaning': 'iso3166loc:gs'},
    "SOUTH_KOREA": {'description': 'South Korea', 'meaning': 'iso3166loc:kr'},
    "SOUTH_SUDAN": {'description': 'South Sudan', 'meaning': 'iso3166loc:ss'},
    "SOUTHERN_OCEAN": {'description': 'Southern Ocean', 'meaning': 'geonames:4036776/'},
    "SPAIN": {'description': 'Spain', 'meaning': 'iso3166loc:es'},
    "SPRATLY_ISLANDS": {'description': 'Spratly Islands', 'annotations': {'note': 'Disputed territory in South China Sea'}},
    "SRI_LANKA": {'description': 'Sri Lanka', 'meaning': 'iso3166loc:lk'},
    "STATE_OF_PALESTINE": {'description': 'State of Palestine', 'meaning': 'iso3166loc:ps'},
    "SUDAN": {'description': 'Sudan', 'meaning': 'iso3166loc:sd'},
    "SURINAME": {'description': 'Suriname', 'meaning': 'iso3166loc:sr'},
    "SVALBARD": {'description': 'Svalbard', 'annotations': {'note': 'Norwegian territory (part of Svalbard and Jan Mayen - SJ)'}},
    "SWEDEN": {'description': 'Sweden', 'meaning': 'iso3166loc:se'},
    "SWITZERLAND": {'description': 'Switzerland', 'meaning': 'iso3166loc:ch'},
    "SYRIA": {'description': 'Syria', 'meaning': 'iso3166loc:sy'},
    "TAIWAN": {'description': 'Taiwan', 'meaning': 'iso3166loc:tw'},
    "TAJIKISTAN": {'description': 'Tajikistan', 'meaning': 'iso3166loc:tj'},
    "TANZANIA": {'description': 'Tanzania', 'meaning': 'iso3166loc:tz'},
    "TASMAN_SEA": {'description': 'Tasman Sea', 'meaning': 'geonames:2363247/'},
    "THAILAND": {'description': 'Thailand', 'meaning': 'iso3166loc:th'},
    "TIMOR_LESTE": {'description': 'Timor-Leste', 'meaning': 'iso3166loc:tl'},
    "TOGO": {'description': 'Togo', 'meaning': 'iso3166loc:tg'},
    "TOKELAU": {'description': 'Tokelau', 'meaning': 'iso3166loc:tk'},
    "TONGA": {'description': 'Tonga', 'meaning': 'iso3166loc:to'},
    "TRINIDAD_AND_TOBAGO": {'description': 'Trinidad and Tobago', 'meaning': 'iso3166loc:tt'},
    "TROMELIN_ISLAND": {'description': 'Tromelin Island', 'annotations': {'note': 'French Southern and Antarctic Lands territory'}},
    "TUNISIA": {'description': 'Tunisia', 'meaning': 'iso3166loc:tn'},
    "TURKEY": {'description': 'Turkey', 'meaning': 'iso3166loc:tr'},
    "TURKMENISTAN": {'description': 'Turkmenistan', 'meaning': 'iso3166loc:tm'},
    "TURKS_AND_CAICOS_ISLANDS": {'description': 'Turks and Caicos Islands', 'meaning': 'iso3166loc:tc'},
    "TUVALU": {'description': 'Tuvalu', 'meaning': 'iso3166loc:tv'},
    "UGANDA": {'description': 'Uganda', 'meaning': 'iso3166loc:ug'},
    "UKRAINE": {'description': 'Ukraine', 'meaning': 'iso3166loc:ua'},
    "UNITED_ARAB_EMIRATES": {'description': 'United Arab Emirates', 'meaning': 'iso3166loc:ae'},
    "UNITED_KINGDOM": {'description': 'United Kingdom', 'meaning': 'iso3166loc:gb'},
    "URUGUAY": {'description': 'Uruguay', 'meaning': 'iso3166loc:uy'},
    "USA": {'description': 'USA', 'meaning': 'iso3166loc:us'},
    "UZBEKISTAN": {'description': 'Uzbekistan', 'meaning': 'iso3166loc:uz'},
    "VANUATU": {'description': 'Vanuatu', 'meaning': 'iso3166loc:vu'},
    "VENEZUELA": {'description': 'Venezuela', 'meaning': 'iso3166loc:ve'},
    "VIET_NAM": {'description': 'Viet Nam', 'meaning': 'iso3166loc:vn'},
    "VIRGIN_ISLANDS": {'description': 'Virgin Islands', 'meaning': 'iso3166loc:vi'},
    "WAKE_ISLAND": {'description': 'Wake Island', 'meaning': 'iso3166loc:um', 'annotations': {'note': 'US Minor Outlying Islands'}},
    "WALLIS_AND_FUTUNA": {'description': 'Wallis and Futuna', 'meaning': 'iso3166loc:wf'},
    "WEST_BANK": {'description': 'West Bank', 'annotations': {'note': 'Palestinian territory'}},
    "WESTERN_SAHARA": {'description': 'Western Sahara', 'meaning': 'iso3166loc:eh'},
    "YEMEN": {'description': 'Yemen', 'meaning': 'iso3166loc:ye'},
    "ZAMBIA": {'description': 'Zambia', 'meaning': 'iso3166loc:zm'},
    "ZIMBABWE": {'description': 'Zimbabwe', 'meaning': 'iso3166loc:zw'},
}

class ViralGenomeTypeEnum(RichEnum):
    """
    Types of viral genomes based on Baltimore classification
    """
    # Enum members
    DNA = "DNA"
    DSDNA = "DSDNA"
    SSDNA = "SSDNA"
    RNA = "RNA"
    DSRNA = "DSRNA"
    SSRNA = "SSRNA"
    SSRNA_POSITIVE = "SSRNA_POSITIVE"
    SSRNA_NEGATIVE = "SSRNA_NEGATIVE"
    SSRNA_RT = "SSRNA_RT"
    DSDNA_RT = "DSDNA_RT"
    MIXED = "MIXED"
    UNCHARACTERIZED = "UNCHARACTERIZED"

# Set metadata after class creation to avoid it becoming an enum member
ViralGenomeTypeEnum._metadata = {
    "DNA": {'description': 'Viral genome composed of DNA', 'meaning': 'CHEBI:16991'},
    "DSDNA": {'description': 'Double-stranded DNA viral genome', 'meaning': 'NCIT:C14348', 'aliases': ['Baltimore Group I', 'Group I']},
    "SSDNA": {'description': 'Single-stranded DNA viral genome', 'meaning': 'NCIT:C14350', 'aliases': ['Baltimore Group II', 'Group II']},
    "RNA": {'description': 'Viral genome composed of RNA', 'meaning': 'CHEBI:33697'},
    "DSRNA": {'description': 'Double-stranded RNA viral genome', 'meaning': 'NCIT:C28518', 'aliases': ['Baltimore Group III', 'Group III']},
    "SSRNA": {'description': 'Single-stranded RNA viral genome', 'meaning': 'NCIT:C95939'},
    "SSRNA_POSITIVE": {'description': 'Positive-sense single-stranded RNA viral genome', 'meaning': 'NCIT:C14351', 'aliases': ['Baltimore Group IV', 'Group IV', '(+)ssRNA']},
    "SSRNA_NEGATIVE": {'description': 'Negative-sense single-stranded RNA viral genome', 'meaning': 'NCIT:C14346', 'aliases': ['Baltimore Group V', 'Group V', '(-)ssRNA']},
    "SSRNA_RT": {'description': 'Single-stranded RNA viruses that replicate through a DNA intermediate (retroviruses)', 'meaning': 'NCIT:C14347', 'aliases': ['Baltimore Group VI', 'Group VI', 'Retroviruses']},
    "DSDNA_RT": {'description': 'Double-stranded DNA viruses that replicate through a single-stranded RNA intermediate (pararetroviruses)', 'meaning': 'NCIT:C14349', 'aliases': ['Baltimore Group VII', 'Group VII', 'Pararetroviruses']},
    "MIXED": {'description': 'Mixed or hybrid viral genome type', 'meaning': 'NCIT:C128790'},
    "UNCHARACTERIZED": {'description': 'Viral genome type not yet characterized', 'meaning': 'NCIT:C17998'},
}

class PlantSexEnum(RichEnum):
    """
    Plant reproductive and sexual system types
    """
    # Enum members
    ANDRODIOECIOUS = "ANDRODIOECIOUS"
    ANDROECIOUS = "ANDROECIOUS"
    ANDROGYNOMONOECIOUS = "ANDROGYNOMONOECIOUS"
    ANDROGYNOUS = "ANDROGYNOUS"
    ANDROMONOECIOUS = "ANDROMONOECIOUS"
    BISEXUAL = "BISEXUAL"
    DICHOGAMOUS = "DICHOGAMOUS"
    DICLINOUS = "DICLINOUS"
    DIOECIOUS = "DIOECIOUS"
    GYNODIOECIOUS = "GYNODIOECIOUS"
    GYNOECIOUS = "GYNOECIOUS"
    GYNOMONOECIOUS = "GYNOMONOECIOUS"
    HERMAPHRODITIC = "HERMAPHRODITIC"
    IMPERFECT = "IMPERFECT"
    MONOCLINOUS = "MONOCLINOUS"
    MONOECIOUS = "MONOECIOUS"
    PERFECT = "PERFECT"
    POLYGAMODIOECIOUS = "POLYGAMODIOECIOUS"
    POLYGAMOMONOECIOUS = "POLYGAMOMONOECIOUS"
    POLYGAMOUS = "POLYGAMOUS"
    PROTANDROUS = "PROTANDROUS"
    PROTOGYNOUS = "PROTOGYNOUS"
    SUBANDROECIOUS = "SUBANDROECIOUS"
    SUBDIOECIOUS = "SUBDIOECIOUS"
    SUBGYNOECIOUS = "SUBGYNOECIOUS"
    SYNOECIOUS = "SYNOECIOUS"
    TRIMONOECIOUS = "TRIMONOECIOUS"
    TRIOECIOUS = "TRIOECIOUS"
    UNISEXUAL = "UNISEXUAL"

# Set metadata after class creation to avoid it becoming an enum member
PlantSexEnum._metadata = {
    "ANDRODIOECIOUS": {'description': 'Having male and hermaphrodite flowers on separate plants'},
    "ANDROECIOUS": {'description': 'Having only male flowers'},
    "ANDROGYNOMONOECIOUS": {'description': 'Having male, female, and hermaphrodite flowers on the same plant'},
    "ANDROGYNOUS": {'description': 'Having both male and female reproductive organs in the same flower'},
    "ANDROMONOECIOUS": {'description': 'Having male and hermaphrodite flowers on the same plant'},
    "BISEXUAL": {'description': 'Having both male and female reproductive organs'},
    "DICHOGAMOUS": {'description': 'Male and female organs mature at different times'},
    "DICLINOUS": {'description': 'Having male and female reproductive organs in separate flowers'},
    "DIOECIOUS": {'description': 'Having male and female flowers on separate plants', 'meaning': 'GSSO:011872'},
    "GYNODIOECIOUS": {'description': 'Having female and hermaphrodite flowers on separate plants'},
    "GYNOECIOUS": {'description': 'Having only female flowers'},
    "GYNOMONOECIOUS": {'description': 'Having female and hermaphrodite flowers on the same plant'},
    "HERMAPHRODITIC": {'description': 'Having both male and female reproductive organs', 'meaning': 'UBERON:0007197'},
    "IMPERFECT": {'description': 'Flower lacking either male or female reproductive organs'},
    "MONOCLINOUS": {'description': 'Having both male and female reproductive organs in the same flower'},
    "MONOECIOUS": {'description': 'Having male and female flowers on the same plant', 'meaning': 'GSSO:011868'},
    "PERFECT": {'description': 'Flower having both male and female reproductive organs'},
    "POLYGAMODIOECIOUS": {'description': 'Having male, female, and hermaphrodite flowers on separate plants'},
    "POLYGAMOMONOECIOUS": {'description': 'Having male, female, and hermaphrodite flowers on the same plant'},
    "POLYGAMOUS": {'description': 'Having male, female, and hermaphrodite flowers'},
    "PROTANDROUS": {'description': 'Male organs mature before female organs'},
    "PROTOGYNOUS": {'description': 'Female organs mature before male organs'},
    "SUBANDROECIOUS": {'description': 'Mostly male flowers with occasional hermaphrodite flowers'},
    "SUBDIOECIOUS": {'description': 'Mostly dioecious with occasional hermaphrodite flowers'},
    "SUBGYNOECIOUS": {'description': 'Mostly female flowers with occasional hermaphrodite flowers'},
    "SYNOECIOUS": {'description': 'Having male and female organs fused together'},
    "TRIMONOECIOUS": {'description': 'Having male, female, and hermaphrodite flowers on the same plant'},
    "TRIOECIOUS": {'description': 'Having male, female, and hermaphrodite flowers on separate plants'},
    "UNISEXUAL": {'description': 'Having only one sex of reproductive organs'},
}

class RelToOxygenEnum(RichEnum):
    """
    Organism's relationship to oxygen for growth and survival
    """
    # Enum members
    AEROBE = "AEROBE"
    ANAEROBE = "ANAEROBE"
    FACULTATIVE = "FACULTATIVE"
    MICROAEROPHILIC = "MICROAEROPHILIC"
    MICROANAEROBE = "MICROANAEROBE"
    OBLIGATE_AEROBE = "OBLIGATE_AEROBE"
    OBLIGATE_ANAEROBE = "OBLIGATE_ANAEROBE"

# Set metadata after class creation to avoid it becoming an enum member
RelToOxygenEnum._metadata = {
    "AEROBE": {'description': 'Organism that can survive and grow in an oxygenated environment', 'meaning': 'ECOCORE:00000173'},
    "ANAEROBE": {'description': 'Organism that does not require oxygen for growth', 'meaning': 'ECOCORE:00000172'},
    "FACULTATIVE": {'description': 'Organism that can grow with or without oxygen', 'meaning': 'ECOCORE:00000177', 'annotations': {'note': 'Maps to facultative anaerobe in ECOCORE'}},
    "MICROAEROPHILIC": {'description': 'Organism that requires oxygen at lower concentrations than atmospheric', 'meaning': 'MICRO:0000515'},
    "MICROANAEROBE": {'description': 'Organism that can tolerate very small amounts of oxygen'},
    "OBLIGATE_AEROBE": {'description': 'Organism that requires oxygen to grow', 'meaning': 'ECOCORE:00000179'},
    "OBLIGATE_ANAEROBE": {'description': 'Organism that cannot grow in the presence of oxygen', 'meaning': 'ECOCORE:00000178'},
}

class TrophicLevelEnum(RichEnum):
    """
    Trophic levels are the feeding position in a food chain
    """
    # Enum members
    AUTOTROPH = "AUTOTROPH"
    CARBOXYDOTROPH = "CARBOXYDOTROPH"
    CHEMOAUTOLITHOTROPH = "CHEMOAUTOLITHOTROPH"
    CHEMOAUTOTROPH = "CHEMOAUTOTROPH"
    CHEMOHETEROTROPH = "CHEMOHETEROTROPH"
    CHEMOLITHOAUTOTROPH = "CHEMOLITHOAUTOTROPH"
    CHEMOLITHOTROPH = "CHEMOLITHOTROPH"
    CHEMOORGANOHETEROTROPH = "CHEMOORGANOHETEROTROPH"
    CHEMOORGANOTROPH = "CHEMOORGANOTROPH"
    CHEMOSYNTHETIC = "CHEMOSYNTHETIC"
    CHEMOTROPH = "CHEMOTROPH"
    COPIOTROPH = "COPIOTROPH"
    DIAZOTROPH = "DIAZOTROPH"
    FACULTATIVE = "FACULTATIVE"
    HETEROTROPH = "HETEROTROPH"
    LITHOAUTOTROPH = "LITHOAUTOTROPH"
    LITHOHETEROTROPH = "LITHOHETEROTROPH"
    LITHOTROPH = "LITHOTROPH"
    METHANOTROPH = "METHANOTROPH"
    METHYLOTROPH = "METHYLOTROPH"
    MIXOTROPH = "MIXOTROPH"
    OBLIGATE = "OBLIGATE"
    OLIGOTROPH = "OLIGOTROPH"
    ORGANOHETEROTROPH = "ORGANOHETEROTROPH"
    ORGANOTROPH = "ORGANOTROPH"
    PHOTOAUTOTROPH = "PHOTOAUTOTROPH"
    PHOTOHETEROTROPH = "PHOTOHETEROTROPH"
    PHOTOLITHOAUTOTROPH = "PHOTOLITHOAUTOTROPH"
    PHOTOLITHOTROPH = "PHOTOLITHOTROPH"
    PHOTOSYNTHETIC = "PHOTOSYNTHETIC"
    PHOTOTROPH = "PHOTOTROPH"

# Set metadata after class creation to avoid it becoming an enum member
TrophicLevelEnum._metadata = {
    "AUTOTROPH": {'description': 'Organism capable of synthesizing its own food from inorganic substances', 'meaning': 'ECOCORE:00000023'},
    "CARBOXYDOTROPH": {'description': 'Organism that uses carbon monoxide as a source of carbon and energy'},
    "CHEMOAUTOLITHOTROPH": {'description': 'Autotroph that obtains energy from inorganic compounds'},
    "CHEMOAUTOTROPH": {'description': 'Organism that obtains energy by oxidizing inorganic compounds', 'meaning': 'ECOCORE:00000129'},
    "CHEMOHETEROTROPH": {'description': 'Organism that obtains energy from organic compounds', 'meaning': 'ECOCORE:00000132'},
    "CHEMOLITHOAUTOTROPH": {'description': 'Organism that uses inorganic compounds as electron donors'},
    "CHEMOLITHOTROPH": {'description': 'Organism that obtains energy from oxidation of inorganic compounds'},
    "CHEMOORGANOHETEROTROPH": {'description': 'Organism that uses organic compounds as both carbon and energy source'},
    "CHEMOORGANOTROPH": {'description': 'Organism that obtains energy from organic compounds', 'meaning': 'ECOCORE:00000133'},
    "CHEMOSYNTHETIC": {'description': 'Relating to organisms that produce organic matter through chemosynthesis'},
    "CHEMOTROPH": {'description': 'Organism that obtains energy from chemical compounds'},
    "COPIOTROPH": {'description': 'Organism that thrives in nutrient-rich environments'},
    "DIAZOTROPH": {'description': 'Organism capable of fixing atmospheric nitrogen'},
    "FACULTATIVE": {'description': 'Organism that can switch between different metabolic modes'},
    "HETEROTROPH": {'description': 'Organism that obtains carbon from organic compounds', 'meaning': 'ECOCORE:00000010'},
    "LITHOAUTOTROPH": {'description': 'Autotroph that uses inorganic compounds as electron donors'},
    "LITHOHETEROTROPH": {'description': 'Heterotroph that uses inorganic compounds as electron donors'},
    "LITHOTROPH": {'description': 'Organism that uses inorganic substrates as electron donors'},
    "METHANOTROPH": {'description': 'Organism that uses methane as carbon and energy source'},
    "METHYLOTROPH": {'description': 'Organism that uses single-carbon compounds'},
    "MIXOTROPH": {'description': 'Organism that can use both autotrophic and heterotrophic methods'},
    "OBLIGATE": {'description': 'Organism restricted to a particular metabolic mode'},
    "OLIGOTROPH": {'description': 'Organism that thrives in nutrient-poor environments', 'meaning': 'ECOCORE:00000138'},
    "ORGANOHETEROTROPH": {'description': 'Organism that uses organic compounds as carbon source'},
    "ORGANOTROPH": {'description': 'Organism that uses organic compounds as electron donors'},
    "PHOTOAUTOTROPH": {'description': 'Organism that uses light energy to synthesize organic compounds', 'meaning': 'ECOCORE:00000130'},
    "PHOTOHETEROTROPH": {'description': 'Organism that uses light for energy but organic compounds for carbon', 'meaning': 'ECOCORE:00000131'},
    "PHOTOLITHOAUTOTROPH": {'description': 'Photoautotroph that uses inorganic electron donors'},
    "PHOTOLITHOTROPH": {'description': 'Organism that uses light energy and inorganic electron donors'},
    "PHOTOSYNTHETIC": {'description': 'Relating to organisms that produce organic matter through photosynthesis'},
    "PHOTOTROPH": {'description': 'Organism that obtains energy from light'},
}

class HumanDevelopmentalStage(RichEnum):
    # Enum members
    ZYGOTE_STAGE = "ZYGOTE_STAGE"
    CLEAVAGE_STAGE = "CLEAVAGE_STAGE"
    MORULA_STAGE = "MORULA_STAGE"
    BLASTOCYST_STAGE = "BLASTOCYST_STAGE"
    GASTRULA_STAGE = "GASTRULA_STAGE"
    NEURULA_STAGE = "NEURULA_STAGE"
    ORGANOGENESIS_STAGE = "ORGANOGENESIS_STAGE"
    FETAL_STAGE = "FETAL_STAGE"
    NEONATAL_STAGE = "NEONATAL_STAGE"
    INFANT_STAGE = "INFANT_STAGE"
    TODDLER_STAGE = "TODDLER_STAGE"
    CHILD_STAGE = "CHILD_STAGE"
    ADOLESCENT_STAGE = "ADOLESCENT_STAGE"
    ADULT_STAGE = "ADULT_STAGE"
    AGED_STAGE = "AGED_STAGE"
    EMBRYONIC_STAGE = "EMBRYONIC_STAGE"
    PRENATAL_STAGE = "PRENATAL_STAGE"
    POSTNATAL_STAGE = "POSTNATAL_STAGE"

# Set metadata after class creation to avoid it becoming an enum member
HumanDevelopmentalStage._metadata = {
    "ZYGOTE_STAGE": {'description': 'Embryonic stage defined by a fertilized oocyte and presence of pronuclei. Starts at day 1 post-fertilization.', 'meaning': 'HsapDv:0000003'},
    "CLEAVAGE_STAGE": {'description': 'Embryonic stage during which cell division occurs with reduction in cytoplasmic volume, and formation of inner and outer cell mass. 2-8 cells. Usually starts between day 2-3 post-fertilization.', 'meaning': 'HsapDv:0000005'},
    "MORULA_STAGE": {'description': 'The later part of Carnegie stage 02 when the cells have coalesced into a mass but the blastocystic cavity has not formed.', 'meaning': 'HsapDv:0000205'},
    "BLASTOCYST_STAGE": {'description': 'Blastula stage with the loss of the zona pellucida and the definition of a free blastocyst. Usually starts between day 4-5 post-fertilization.', 'meaning': 'HsapDv:0000007'},
    "GASTRULA_STAGE": {'description': 'Embryonic stage defined by a complex and coordinated series of cellular movements that occurs at the end of cleavage.', 'meaning': 'HsapDv:0000010'},
    "NEURULA_STAGE": {'description': 'Embryonic stage defined by the formation of a tube from the flat layer of ectodermal cells known as the neural plate. This stage starts the emergence of the central nervous system.', 'meaning': 'HsapDv:0000012'},
    "ORGANOGENESIS_STAGE": {'description': 'Embryonic stage at which the ectoderm, endoderm, and mesoderm develop into the internal organs of the organism.', 'meaning': 'HsapDv:0000015'},
    "FETAL_STAGE": {'description': 'Prenatal stage that starts with the fully formed embryo and ends at birth. Generally from 8 weeks post-fertilization until birth.', 'meaning': 'HsapDv:0000037'},
    "NEONATAL_STAGE": {'description': 'Immature stage that refers to a human newborn within the first 28 days of life.', 'meaning': 'HsapDv:0000262'},
    "INFANT_STAGE": {'description': 'Immature stage that refers to an infant who is over 28 days and is under 12 months old.', 'meaning': 'HsapDv:0000261'},
    "TODDLER_STAGE": {'description': 'Human stage that refers to a child who is over 12 months and under 5 years old. Often divided into early toddler (1-2 years) and late toddler (2-3 years).', 'meaning': 'HsapDv:0000265'},
    "CHILD_STAGE": {'description': 'Pediatric stage that refers to a human who is over 5 and under 15 years old. Covers elementary and middle school ages.', 'meaning': 'HsapDv:0000271'},
    "ADOLESCENT_STAGE": {'description': 'A young adult stage that refers to an individual who is over 15 and under 20 years old. Period of transition from childhood to adulthood.', 'meaning': 'HsapDv:0000268'},
    "ADULT_STAGE": {'description': 'Human developmental stage that refers to a sexually mature human. Starts at approximately 15 years according to HPO definitions.', 'meaning': 'HsapDv:0000258'},
    "AGED_STAGE": {'description': 'Late adult stage that refers to an individual who is over 60 and starts to have some age-related impairments. Often subdivided into young-old (60-79) and old-old (80+).', 'meaning': 'HsapDv:0000227'},
    "EMBRYONIC_STAGE": {'description': 'Prenatal stage that starts with fertilization and ends with a fully formed embryo, before undergoing last development during the fetal stage. Up to 8 weeks post-fertilization.', 'meaning': 'HsapDv:0000002'},
    "PRENATAL_STAGE": {'description': 'Prenatal stage that starts with fertilization and ends at birth. Encompasses both embryonic and fetal stages.', 'meaning': 'HsapDv:0000045'},
    "POSTNATAL_STAGE": {'description': 'Human developmental stage that covers the whole of human life post birth.', 'meaning': 'HsapDv:0010000'},
}

class MouseDevelopmentalStage(RichEnum):
    # Enum members
    ZYGOTE_STAGE = "ZYGOTE_STAGE"
    TWO_CELL_STAGE = "TWO_CELL_STAGE"
    FOUR_CELL_STAGE = "FOUR_CELL_STAGE"
    EIGHT_CELL_STAGE = "EIGHT_CELL_STAGE"
    MORULA_STAGE = "MORULA_STAGE"
    BLASTOCYST_STAGE = "BLASTOCYST_STAGE"
    GASTRULA_STAGE = "GASTRULA_STAGE"
    NEURULA_STAGE = "NEURULA_STAGE"
    ORGANOGENESIS_STAGE = "ORGANOGENESIS_STAGE"
    E0_5 = "E0_5"
    E9_5 = "E9_5"
    E14_5 = "E14_5"
    P0_NEWBORN = "P0_NEWBORN"
    P21_WEANING = "P21_WEANING"
    P42_JUVENILE = "P42_JUVENILE"
    P56_ADULT = "P56_ADULT"
    AGED_12_MONTHS = "AGED_12_MONTHS"
    THEILER_STAGE = "THEILER_STAGE"

# Set metadata after class creation to avoid it becoming an enum member
MouseDevelopmentalStage._metadata = {
    "ZYGOTE_STAGE": {'description': 'Embryonic stage defined by a one-cell embryo (fertilised egg) with zona pellucida present. Embryonic age 0-0.9 dpc (days post coitum).', 'meaning': 'MmusDv:0000003'},
    "TWO_CELL_STAGE": {'description': 'Embryonic cleavage stage defined by a dividing 2-4 cells egg. Embryonic age 1 dpc.', 'meaning': 'MmusDv:0000005'},
    "FOUR_CELL_STAGE": {'description': 'Part of Theiler stage 02 - dividing egg with 4 cells. Embryonic age approximately 1 dpc.', 'meaning': 'MmusDv:0000005'},
    "EIGHT_CELL_STAGE": {'description': 'Part of early morula stage - dividing egg with 8 cells. Embryonic age approximately 2 dpc.', 'meaning': 'MmusDv:0000006'},
    "MORULA_STAGE": {'description': 'Embryonic cleavage stage defined by a dividing 4-16 cells egg, early to fully compacted morula. Embryonic age 2 dpc.', 'meaning': 'MmusDv:0000006'},
    "BLASTOCYST_STAGE": {'description': 'Embryonic blastula stage defined by a zona free blastocyst (zona pellucida absent). Embryonic age 4 dpc.', 'meaning': 'MmusDv:0000009'},
    "GASTRULA_STAGE": {'description': 'Embryonic stage defined by complex and coordinated series of cellular movements that occurs at the end of cleavage.', 'meaning': 'MmusDv:0000013'},
    "NEURULA_STAGE": {'description': 'Embryonic stage called presomite stage and defined by the formation of the neural plate. This stage starts the emergence of the central nervous system at embryonic age 7.5 dpc.', 'meaning': 'MmusDv:0000017'},
    "ORGANOGENESIS_STAGE": {'description': 'Embryonic stage at which the ectoderm, endoderm, and mesoderm develop into the internal organs of the organism.', 'meaning': 'MmusDv:0000018'},
    "E0_5": {'description': 'Embryonic day 0.5 - one-cell embryo stage. Corresponds to Theiler stage 01.', 'meaning': 'MmusDv:0000003'},
    "E9_5": {'description': 'Embryonic day 9.5 - organogenesis stage with visible hind limb buds. Between Theiler stages 15 and 16.', 'meaning': 'MmusDv:0000023'},
    "E14_5": {'description': 'Embryonic day 14.5 - late organogenesis with clearly visible fingers and long bones of the limbs present.', 'meaning': 'MmusDv:0000029'},
    "P0_NEWBORN": {'description': 'Stage that refers to the newborn mouse, aged E19-20, P0. Used for postnatal days 0 through 3.', 'meaning': 'MmusDv:0000036'},
    "P21_WEANING": {'description': 'Weaning stage at approximately 21-22 days old. Transition from nursing to independent feeding.', 'meaning': 'MmusDv:0000141'},
    "P42_JUVENILE": {'description': 'Prime adult stage at 6 weeks (42 days) old. Commonly considered the milestone for sexual maturity.', 'meaning': 'MmusDv:0000151'},
    "P56_ADULT": {'description': 'Adult stage at 8 weeks (56 days) old. Fully mature adult mouse.', 'meaning': 'MmusDv:0000154'},
    "AGED_12_MONTHS": {'description': 'Middle aged stage for mice over 10 and under 18 months old. Shows progressive age-related changes.', 'meaning': 'MmusDv:0000135'},
    "THEILER_STAGE": {'description': 'Reference to any Theiler stage (TS1-TS28) which provides standardized morphological staging for mouse development.'},
}

class DayOfWeek(RichEnum):
    """
    Days of the week following ISO 8601 standard (Monday = 1)
    """
    # Enum members
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

# Set metadata after class creation to avoid it becoming an enum member
DayOfWeek._metadata = {
    "MONDAY": {'description': 'Monday (first day of week in ISO 8601)', 'meaning': 'TIME:Monday', 'annotations': {'iso_number': 1, 'abbreviation': 'Mon'}},
    "TUESDAY": {'description': 'Tuesday', 'meaning': 'TIME:Tuesday', 'annotations': {'iso_number': 2, 'abbreviation': 'Tue'}},
    "WEDNESDAY": {'description': 'Wednesday', 'meaning': 'TIME:Wednesday', 'annotations': {'iso_number': 3, 'abbreviation': 'Wed'}},
    "THURSDAY": {'description': 'Thursday', 'meaning': 'TIME:Thursday', 'annotations': {'iso_number': 4, 'abbreviation': 'Thu'}},
    "FRIDAY": {'description': 'Friday', 'meaning': 'TIME:Friday', 'annotations': {'iso_number': 5, 'abbreviation': 'Fri'}},
    "SATURDAY": {'description': 'Saturday', 'meaning': 'TIME:Saturday', 'annotations': {'iso_number': 6, 'abbreviation': 'Sat'}},
    "SUNDAY": {'description': 'Sunday (last day of week in ISO 8601)', 'meaning': 'TIME:Sunday', 'annotations': {'iso_number': 7, 'abbreviation': 'Sun'}},
}

class Month(RichEnum):
    """
    Months of the year
    """
    # Enum members
    JANUARY = "JANUARY"
    FEBRUARY = "FEBRUARY"
    MARCH = "MARCH"
    APRIL = "APRIL"
    MAY = "MAY"
    JUNE = "JUNE"
    JULY = "JULY"
    AUGUST = "AUGUST"
    SEPTEMBER = "SEPTEMBER"
    OCTOBER = "OCTOBER"
    NOVEMBER = "NOVEMBER"
    DECEMBER = "DECEMBER"

# Set metadata after class creation to avoid it becoming an enum member
Month._metadata = {
    "JANUARY": {'description': 'January', 'meaning': 'greg:January', 'annotations': {'month_number': 1, 'abbreviation': 'Jan', 'days': 31}},
    "FEBRUARY": {'description': 'February', 'meaning': 'greg:February', 'annotations': {'month_number': 2, 'abbreviation': 'Feb', 'days': '28/29'}},
    "MARCH": {'description': 'March', 'meaning': 'greg:March', 'annotations': {'month_number': 3, 'abbreviation': 'Mar', 'days': 31}},
    "APRIL": {'description': 'April', 'meaning': 'greg:April', 'annotations': {'month_number': 4, 'abbreviation': 'Apr', 'days': 30}},
    "MAY": {'description': 'May', 'meaning': 'greg:May', 'annotations': {'month_number': 5, 'abbreviation': 'May', 'days': 31}},
    "JUNE": {'description': 'June', 'meaning': 'greg:June', 'annotations': {'month_number': 6, 'abbreviation': 'Jun', 'days': 30}},
    "JULY": {'description': 'July', 'meaning': 'greg:July', 'annotations': {'month_number': 7, 'abbreviation': 'Jul', 'days': 31}},
    "AUGUST": {'description': 'August', 'meaning': 'greg:August', 'annotations': {'month_number': 8, 'abbreviation': 'Aug', 'days': 31}},
    "SEPTEMBER": {'description': 'September', 'meaning': 'greg:September', 'annotations': {'month_number': 9, 'abbreviation': 'Sep', 'days': 30}},
    "OCTOBER": {'description': 'October', 'meaning': 'greg:October', 'annotations': {'month_number': 10, 'abbreviation': 'Oct', 'days': 31}},
    "NOVEMBER": {'description': 'November', 'meaning': 'greg:November', 'annotations': {'month_number': 11, 'abbreviation': 'Nov', 'days': 30}},
    "DECEMBER": {'description': 'December', 'meaning': 'greg:December', 'annotations': {'month_number': 12, 'abbreviation': 'Dec', 'days': 31}},
}

class Quarter(RichEnum):
    """
    Calendar quarters
    """
    # Enum members
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"

# Set metadata after class creation to avoid it becoming an enum member
Quarter._metadata = {
    "Q1": {'description': 'First quarter (January-March)', 'annotations': {'months': 'Jan-Mar'}},
    "Q2": {'description': 'Second quarter (April-June)', 'annotations': {'months': 'Apr-Jun'}},
    "Q3": {'description': 'Third quarter (July-September)', 'annotations': {'months': 'Jul-Sep'}},
    "Q4": {'description': 'Fourth quarter (October-December)', 'annotations': {'months': 'Oct-Dec'}},
}

class Season(RichEnum):
    """
    Seasons of the year (Northern Hemisphere)
    """
    # Enum members
    SPRING = "SPRING"
    SUMMER = "SUMMER"
    AUTUMN = "AUTUMN"
    WINTER = "WINTER"

# Set metadata after class creation to avoid it becoming an enum member
Season._metadata = {
    "SPRING": {'description': 'Spring season', 'meaning': 'NCIT:C94731', 'annotations': {'months': 'Mar-May', 'astronomical_start': '~Mar 20'}},
    "SUMMER": {'description': 'Summer season', 'meaning': 'NCIT:C94732', 'annotations': {'months': 'Jun-Aug', 'astronomical_start': '~Jun 21'}},
    "AUTUMN": {'description': 'Autumn/Fall season', 'meaning': 'NCIT:C94733', 'annotations': {'months': 'Sep-Nov', 'astronomical_start': '~Sep 22', 'aliases': 'Fall'}},
    "WINTER": {'description': 'Winter season', 'meaning': 'NCIT:C94730', 'annotations': {'months': 'Dec-Feb', 'astronomical_start': '~Dec 21'}},
}

class TimePeriod(RichEnum):
    """
    Common time periods and intervals
    """
    # Enum members
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    SEMIANNUALLY = "SEMIANNUALLY"
    ANNUALLY = "ANNUALLY"
    BIANNUALLY = "BIANNUALLY"

# Set metadata after class creation to avoid it becoming an enum member
TimePeriod._metadata = {
    "HOURLY": {'description': 'Every hour', 'annotations': {'ucum': 'h'}},
    "DAILY": {'description': 'Every day', 'annotations': {'ucum': 'd'}},
    "WEEKLY": {'description': 'Every week', 'annotations': {'ucum': 'wk'}},
    "BIWEEKLY": {'description': 'Every two weeks', 'annotations': {'ucum': '2.wk'}},
    "MONTHLY": {'description': 'Every month', 'annotations': {'ucum': 'mo'}},
    "QUARTERLY": {'description': 'Every quarter (3 months)', 'annotations': {'ucum': '3.mo'}},
    "SEMIANNUALLY": {'description': 'Every six months', 'annotations': {'ucum': '6.mo'}},
    "ANNUALLY": {'description': 'Every year', 'annotations': {'ucum': 'a'}},
    "BIANNUALLY": {'description': 'Every two years', 'annotations': {'ucum': '2.a'}},
}

class TimeOfDay(RichEnum):
    """
    Common times of day
    """
    # Enum members
    DAWN = "DAWN"
    MORNING = "MORNING"
    NOON = "NOON"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    NIGHT = "NIGHT"
    MIDNIGHT = "MIDNIGHT"

# Set metadata after class creation to avoid it becoming an enum member
TimeOfDay._metadata = {
    "DAWN": {'description': 'Dawn (first light)', 'annotations': {'typical_time': '05:00-06:00'}},
    "MORNING": {'description': 'Morning', 'annotations': {'typical_time': '06:00-12:00'}},
    "NOON": {'description': 'Noon/Midday', 'annotations': {'typical_time': 720}},
    "AFTERNOON": {'description': 'Afternoon', 'annotations': {'typical_time': '12:00-18:00'}},
    "EVENING": {'description': 'Evening', 'annotations': {'typical_time': '18:00-21:00'}},
    "NIGHT": {'description': 'Night', 'annotations': {'typical_time': '21:00-05:00'}},
    "MIDNIGHT": {'description': 'Midnight', 'annotations': {'typical_time': '00:00'}},
}

class BusinessTimeFrame(RichEnum):
    """
    Common business and financial time frames
    """
    # Enum members
    REAL_TIME = "REAL_TIME"
    INTRADAY = "INTRADAY"
    T_PLUS_1 = "T_PLUS_1"
    T_PLUS_2 = "T_PLUS_2"
    T_PLUS_3 = "T_PLUS_3"
    END_OF_DAY = "END_OF_DAY"
    END_OF_WEEK = "END_OF_WEEK"
    END_OF_MONTH = "END_OF_MONTH"
    END_OF_QUARTER = "END_OF_QUARTER"
    END_OF_YEAR = "END_OF_YEAR"
    YEAR_TO_DATE = "YEAR_TO_DATE"
    MONTH_TO_DATE = "MONTH_TO_DATE"
    QUARTER_TO_DATE = "QUARTER_TO_DATE"

# Set metadata after class creation to avoid it becoming an enum member
BusinessTimeFrame._metadata = {
    "REAL_TIME": {'description': 'Real-time/instantaneous'},
    "INTRADAY": {'description': 'Within the same day'},
    "T_PLUS_1": {'description': 'Trade date plus one business day', 'annotations': {'abbreviation': 'T+1'}},
    "T_PLUS_2": {'description': 'Trade date plus two business days', 'annotations': {'abbreviation': 'T+2'}},
    "T_PLUS_3": {'description': 'Trade date plus three business days', 'annotations': {'abbreviation': 'T+3'}},
    "END_OF_DAY": {'description': 'End of business day', 'annotations': {'abbreviation': 'EOD'}},
    "END_OF_WEEK": {'description': 'End of business week', 'annotations': {'abbreviation': 'EOW'}},
    "END_OF_MONTH": {'description': 'End of calendar month', 'annotations': {'abbreviation': 'EOM'}},
    "END_OF_QUARTER": {'description': 'End of calendar quarter', 'annotations': {'abbreviation': 'EOQ'}},
    "END_OF_YEAR": {'description': 'End of calendar year', 'annotations': {'abbreviation': 'EOY'}},
    "YEAR_TO_DATE": {'description': 'From beginning of year to current date', 'annotations': {'abbreviation': 'YTD'}},
    "MONTH_TO_DATE": {'description': 'From beginning of month to current date', 'annotations': {'abbreviation': 'MTD'}},
    "QUARTER_TO_DATE": {'description': 'From beginning of quarter to current date', 'annotations': {'abbreviation': 'QTD'}},
}

class GeologicalEra(RichEnum):
    """
    Major geological eras
    """
    # Enum members
    PRECAMBRIAN = "PRECAMBRIAN"
    PALEOZOIC = "PALEOZOIC"
    MESOZOIC = "MESOZOIC"
    CENOZOIC = "CENOZOIC"

# Set metadata after class creation to avoid it becoming an enum member
GeologicalEra._metadata = {
    "PRECAMBRIAN": {'description': 'Precambrian (4.6 billion - 541 million years ago)'},
    "PALEOZOIC": {'description': 'Paleozoic Era (541 - 252 million years ago)'},
    "MESOZOIC": {'description': 'Mesozoic Era (252 - 66 million years ago)'},
    "CENOZOIC": {'description': 'Cenozoic Era (66 million years ago - present)'},
}

class HistoricalPeriod(RichEnum):
    """
    Major historical periods
    """
    # Enum members
    PREHISTORIC = "PREHISTORIC"
    ANCIENT = "ANCIENT"
    CLASSICAL_ANTIQUITY = "CLASSICAL_ANTIQUITY"
    MIDDLE_AGES = "MIDDLE_AGES"
    RENAISSANCE = "RENAISSANCE"
    EARLY_MODERN = "EARLY_MODERN"
    INDUSTRIAL_AGE = "INDUSTRIAL_AGE"
    MODERN = "MODERN"
    CONTEMPORARY = "CONTEMPORARY"
    DIGITAL_AGE = "DIGITAL_AGE"

# Set metadata after class creation to avoid it becoming an enum member
HistoricalPeriod._metadata = {
    "PREHISTORIC": {'description': 'Before written records'},
    "ANCIENT": {'description': 'Ancient history (3000 BCE - 500 CE)'},
    "CLASSICAL_ANTIQUITY": {'description': 'Classical antiquity (8th century BCE - 6th century CE)'},
    "MIDDLE_AGES": {'description': 'Middle Ages (5th - 15th century)'},
    "RENAISSANCE": {'description': 'Renaissance (14th - 17th century)'},
    "EARLY_MODERN": {'description': 'Early modern period (15th - 18th century)'},
    "INDUSTRIAL_AGE": {'description': 'Industrial age (1760 - 1840)'},
    "MODERN": {'description': 'Modern era (19th century - mid 20th century)'},
    "CONTEMPORARY": {'description': 'Contemporary period (mid 20th century - present)'},
    "DIGITAL_AGE": {'description': 'Digital/Information age (1950s - present)'},
}

class PublicationType(RichEnum):
    """
    Types of academic and research publications
    """
    # Enum members
    JOURNAL_ARTICLE = "JOURNAL_ARTICLE"
    REVIEW_ARTICLE = "REVIEW_ARTICLE"
    RESEARCH_ARTICLE = "RESEARCH_ARTICLE"
    SHORT_COMMUNICATION = "SHORT_COMMUNICATION"
    EDITORIAL = "EDITORIAL"
    LETTER = "LETTER"
    COMMENTARY = "COMMENTARY"
    PERSPECTIVE = "PERSPECTIVE"
    CASE_REPORT = "CASE_REPORT"
    TECHNICAL_NOTE = "TECHNICAL_NOTE"
    BOOK = "BOOK"
    BOOK_CHAPTER = "BOOK_CHAPTER"
    EDITED_BOOK = "EDITED_BOOK"
    REFERENCE_BOOK = "REFERENCE_BOOK"
    TEXTBOOK = "TEXTBOOK"
    CONFERENCE_PAPER = "CONFERENCE_PAPER"
    CONFERENCE_ABSTRACT = "CONFERENCE_ABSTRACT"
    CONFERENCE_POSTER = "CONFERENCE_POSTER"
    CONFERENCE_PROCEEDINGS = "CONFERENCE_PROCEEDINGS"
    PHD_THESIS = "PHD_THESIS"
    MASTERS_THESIS = "MASTERS_THESIS"
    BACHELORS_THESIS = "BACHELORS_THESIS"
    TECHNICAL_REPORT = "TECHNICAL_REPORT"
    WORKING_PAPER = "WORKING_PAPER"
    WHITE_PAPER = "WHITE_PAPER"
    POLICY_BRIEF = "POLICY_BRIEF"
    DATASET = "DATASET"
    SOFTWARE = "SOFTWARE"
    DATA_PAPER = "DATA_PAPER"
    SOFTWARE_PAPER = "SOFTWARE_PAPER"
    PROTOCOL = "PROTOCOL"
    PREPRINT = "PREPRINT"
    POSTPRINT = "POSTPRINT"
    PUBLISHED_VERSION = "PUBLISHED_VERSION"
    PATENT = "PATENT"
    STANDARD = "STANDARD"
    BLOG_POST = "BLOG_POST"
    PRESENTATION = "PRESENTATION"
    LECTURE = "LECTURE"
    ANNOTATION = "ANNOTATION"

# Set metadata after class creation to avoid it becoming an enum member
PublicationType._metadata = {
    "JOURNAL_ARTICLE": {'description': 'Peer-reviewed journal article', 'meaning': 'FABIO:JournalArticle'},
    "REVIEW_ARTICLE": {'description': 'Review article synthesizing existing research', 'meaning': 'FABIO:ReviewArticle'},
    "RESEARCH_ARTICLE": {'description': 'Original research article', 'meaning': 'FABIO:ResearchPaper'},
    "SHORT_COMMUNICATION": {'description': 'Brief communication or short report', 'meaning': 'FABIO:BriefCommunication'},
    "EDITORIAL": {'description': 'Editorial or opinion piece', 'meaning': 'FABIO:Editorial'},
    "LETTER": {'description': 'Letter to the editor', 'meaning': 'FABIO:Letter'},
    "COMMENTARY": {'description': 'Commentary on existing work', 'meaning': 'FABIO:Comment'},
    "PERSPECTIVE": {'description': 'Perspective or viewpoint article', 'meaning': 'FABIO:Comment'},
    "CASE_REPORT": {'description': 'Clinical or scientific case report', 'meaning': 'FABIO:CaseReport'},
    "TECHNICAL_NOTE": {'description': 'Technical or methodological note', 'meaning': 'FABIO:BriefCommunication'},
    "BOOK": {'description': 'Complete book or monograph', 'meaning': 'FABIO:Book'},
    "BOOK_CHAPTER": {'description': 'Chapter in an edited book', 'meaning': 'FABIO:BookChapter'},
    "EDITED_BOOK": {'description': 'Edited collection or anthology', 'meaning': 'FABIO:EditedBook'},
    "REFERENCE_BOOK": {'description': 'Reference work or encyclopedia', 'meaning': 'FABIO:ReferenceBook'},
    "TEXTBOOK": {'description': 'Educational textbook', 'meaning': 'FABIO:Textbook'},
    "CONFERENCE_PAPER": {'description': 'Full conference paper', 'meaning': 'FABIO:ConferencePaper'},
    "CONFERENCE_ABSTRACT": {'description': 'Conference abstract', 'meaning': 'FABIO:ConferenceAbstract'},
    "CONFERENCE_POSTER": {'description': 'Conference poster', 'meaning': 'FABIO:ConferencePoster'},
    "CONFERENCE_PROCEEDINGS": {'description': 'Complete conference proceedings', 'meaning': 'FABIO:ConferenceProceedings'},
    "PHD_THESIS": {'description': 'Doctoral dissertation', 'meaning': 'FABIO:DoctoralThesis'},
    "MASTERS_THESIS": {'description': "Master's thesis", 'meaning': 'FABIO:MastersThesis'},
    "BACHELORS_THESIS": {'description': "Bachelor's or undergraduate thesis", 'meaning': 'FABIO:BachelorsThesis'},
    "TECHNICAL_REPORT": {'description': 'Technical or research report', 'meaning': 'FABIO:TechnicalReport'},
    "WORKING_PAPER": {'description': 'Working paper or discussion paper', 'meaning': 'FABIO:WorkingPaper'},
    "WHITE_PAPER": {'description': 'White paper or position paper', 'meaning': 'FABIO:WhitePaper'},
    "POLICY_BRIEF": {'description': 'Policy brief or recommendation', 'meaning': 'FABIO:PolicyBrief'},
    "DATASET": {'description': 'Research dataset', 'meaning': 'DCMITYPE:Dataset'},
    "SOFTWARE": {'description': 'Research software or code', 'meaning': 'DCMITYPE:Software'},
    "DATA_PAPER": {'description': 'Data descriptor or data paper', 'meaning': 'FABIO:DataPaper'},
    "SOFTWARE_PAPER": {'description': 'Software or tools paper', 'meaning': 'FABIO:ResearchPaper'},
    "PROTOCOL": {'description': 'Research protocol or methodology', 'meaning': 'FABIO:Protocol'},
    "PREPRINT": {'description': 'Preprint or unrefereed manuscript', 'meaning': 'FABIO:Preprint'},
    "POSTPRINT": {'description': 'Accepted manuscript after peer review', 'meaning': 'FABIO:Preprint'},
    "PUBLISHED_VERSION": {'description': 'Final published version', 'meaning': 'IAO:0000311'},
    "PATENT": {'description': 'Patent or patent application', 'meaning': 'FABIO:Patent'},
    "STANDARD": {'description': 'Technical standard or specification', 'meaning': 'FABIO:Standard'},
    "BLOG_POST": {'description': 'Academic blog post', 'meaning': 'FABIO:BlogPost'},
    "PRESENTATION": {'description': 'Presentation slides or talk', 'meaning': 'FABIO:Presentation'},
    "LECTURE": {'description': 'Lecture or educational material', 'meaning': 'FABIO:Presentation'},
    "ANNOTATION": {'description': 'Annotation or scholarly note', 'meaning': 'FABIO:Annotation'},
}

class PeerReviewStatus(RichEnum):
    """
    Status of peer review process
    """
    # Enum members
    NOT_PEER_REVIEWED = "NOT_PEER_REVIEWED"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REVIEW_COMPLETE = "REVIEW_COMPLETE"
    MAJOR_REVISION = "MAJOR_REVISION"
    MINOR_REVISION = "MINOR_REVISION"
    ACCEPTED = "ACCEPTED"
    ACCEPTED_WITH_REVISIONS = "ACCEPTED_WITH_REVISIONS"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    PUBLISHED = "PUBLISHED"

# Set metadata after class creation to avoid it becoming an enum member
PeerReviewStatus._metadata = {
    "NOT_PEER_REVIEWED": {'description': 'Not peer reviewed'},
    "SUBMITTED": {'description': 'Submitted for review'},
    "UNDER_REVIEW": {'description': 'Currently under peer review', 'meaning': 'SIO:000035'},
    "REVIEW_COMPLETE": {'description': 'Peer review complete', 'meaning': 'SIO:000034'},
    "MAJOR_REVISION": {'description': 'Major revisions requested'},
    "MINOR_REVISION": {'description': 'Minor revisions requested'},
    "ACCEPTED": {'description': 'Accepted for publication'},
    "ACCEPTED_WITH_REVISIONS": {'description': 'Conditionally accepted pending revisions'},
    "REJECTED": {'description': 'Rejected after review'},
    "WITHDRAWN": {'description': 'Withdrawn by authors'},
    "PUBLISHED": {'description': 'Published after review', 'meaning': 'IAO:0000311'},
}

class AcademicDegree(RichEnum):
    """
    Academic degrees and qualifications
    """
    # Enum members
    BA = "BA"
    BS = "BS"
    BSC = "BSC"
    BENG = "BENG"
    BFA = "BFA"
    LLB = "LLB"
    MBBS = "MBBS"
    MA = "MA"
    MS = "MS"
    MSC = "MSC"
    MBA = "MBA"
    MFA = "MFA"
    MPH = "MPH"
    MENG = "MENG"
    MED = "MED"
    LLM = "LLM"
    MPHIL = "MPHIL"
    PHD = "PHD"
    MD = "MD"
    JD = "JD"
    EDD = "EDD"
    PSYD = "PSYD"
    DBA = "DBA"
    DPHIL = "DPHIL"
    SCD = "SCD"
    POSTDOC = "POSTDOC"

# Set metadata after class creation to avoid it becoming an enum member
AcademicDegree._metadata = {
    "BA": {'meaning': 'NCIT:C71345', 'annotations': {'level': 'undergraduate'}},
    "BS": {'description': 'Bachelor of Science', 'meaning': 'NCIT:C71351', 'annotations': {'level': 'undergraduate'}, 'aliases': ['Bachelor of Science']},
    "BSC": {'description': 'Bachelor of Science (British)', 'meaning': 'NCIT:C71351', 'annotations': {'level': 'undergraduate'}, 'aliases': ['Bachelor of Science']},
    "BENG": {'description': 'Bachelor of Engineering', 'meaning': 'NCIT:C71347', 'annotations': {'level': 'undergraduate'}, 'aliases': ['Bachelor of Engineering']},
    "BFA": {'description': 'Bachelor of Fine Arts', 'meaning': 'NCIT:C71349', 'annotations': {'level': 'undergraduate'}, 'aliases': ['Bachelor of Fine Arts']},
    "LLB": {'description': 'Bachelor of Laws', 'meaning': 'NCIT:C71352', 'annotations': {'level': 'undergraduate'}, 'aliases': ['Bachelor of Science in Law']},
    "MBBS": {'description': 'Bachelor of Medicine, Bachelor of Surgery', 'meaning': 'NCIT:C39383', 'annotations': {'level': 'undergraduate'}, 'aliases': ['Doctor of Medicine']},
    "MA": {'description': 'Master of Arts', 'meaning': 'NCIT:C71364', 'annotations': {'level': 'graduate'}, 'aliases': ['Master of Arts']},
    "MS": {'description': 'Master of Science', 'meaning': 'NCIT:C39452', 'annotations': {'level': 'graduate'}, 'aliases': ['Master of Science']},
    "MSC": {'description': 'Master of Science (British)', 'meaning': 'NCIT:C39452', 'annotations': {'level': 'graduate'}, 'aliases': ['Master of Science']},
    "MBA": {'description': 'Master of Business Administration', 'meaning': 'NCIT:C39449', 'annotations': {'level': 'graduate'}, 'aliases': ['Master of Business Administration']},
    "MFA": {'description': 'Master of Fine Arts', 'annotations': {'level': 'graduate'}},
    "MPH": {'description': 'Master of Public Health', 'meaning': 'NCIT:C39451', 'annotations': {'level': 'graduate'}, 'aliases': ['Master of Public Health']},
    "MENG": {'description': 'Master of Engineering', 'meaning': 'NCIT:C71368', 'annotations': {'level': 'graduate'}, 'aliases': ['Master of Engineering']},
    "MED": {'description': 'Master of Education', 'meaning': 'NCIT:C71369', 'annotations': {'level': 'graduate'}, 'aliases': ['Master of Education']},
    "LLM": {'description': 'Master of Laws', 'meaning': 'NCIT:C71363', 'annotations': {'level': 'graduate'}, 'aliases': ['Master of Law']},
    "MPHIL": {'description': 'Master of Philosophy', 'annotations': {'level': 'graduate'}},
    "PHD": {'description': 'Doctor of Philosophy', 'meaning': 'NCIT:C39387', 'annotations': {'level': 'doctoral'}, 'aliases': ['Doctor of Philosophy']},
    "MD": {'description': 'Doctor of Medicine', 'meaning': 'NCIT:C39383', 'annotations': {'level': 'doctoral'}, 'aliases': ['Doctor of Medicine']},
    "JD": {'description': 'Juris Doctor', 'meaning': 'NCIT:C71361', 'annotations': {'level': 'doctoral'}, 'aliases': ['Doctor of Law']},
    "EDD": {'description': 'Doctor of Education', 'meaning': 'NCIT:C71359', 'annotations': {'level': 'doctoral'}, 'aliases': ['Doctor of Education']},
    "PSYD": {'description': 'Doctor of Psychology', 'annotations': {'level': 'doctoral'}},
    "DBA": {'description': 'Doctor of Business Administration', 'annotations': {'level': 'doctoral'}},
    "DPHIL": {'description': 'Doctor of Philosophy (Oxford/Sussex)', 'meaning': 'NCIT:C39387', 'annotations': {'level': 'doctoral'}, 'aliases': ['Doctor of Philosophy']},
    "SCD": {'description': 'Doctor of Science', 'meaning': 'NCIT:C71379', 'annotations': {'level': 'doctoral'}, 'aliases': ['Doctor of Science']},
    "POSTDOC": {'description': 'Postdoctoral researcher', 'annotations': {'level': 'postdoctoral'}},
}

class LicenseType(RichEnum):
    """
    Common software and content licenses
    """
    # Enum members
    MIT = "MIT"
    APACHE_2_0 = "APACHE_2_0"
    BSD_3_CLAUSE = "BSD_3_CLAUSE"
    BSD_2_CLAUSE = "BSD_2_CLAUSE"
    ISC = "ISC"
    GPL_3_0 = "GPL_3_0"
    GPL_2_0 = "GPL_2_0"
    LGPL_3_0 = "LGPL_3_0"
    LGPL_2_1 = "LGPL_2_1"
    AGPL_3_0 = "AGPL_3_0"
    MPL_2_0 = "MPL_2_0"
    CC_BY_4_0 = "CC_BY_4_0"
    CC_BY_SA_4_0 = "CC_BY_SA_4_0"
    CC_BY_NC_4_0 = "CC_BY_NC_4_0"
    CC_BY_NC_SA_4_0 = "CC_BY_NC_SA_4_0"
    CC_BY_ND_4_0 = "CC_BY_ND_4_0"
    CC0_1_0 = "CC0_1_0"
    UNLICENSE = "UNLICENSE"
    PROPRIETARY = "PROPRIETARY"
    CUSTOM = "CUSTOM"

# Set metadata after class creation to avoid it becoming an enum member
LicenseType._metadata = {
    "MIT": {'description': 'MIT License', 'meaning': 'SPDX:MIT'},
    "APACHE_2_0": {'description': 'Apache License 2.0', 'meaning': 'SPDX:Apache-2.0'},
    "BSD_3_CLAUSE": {'description': 'BSD 3-Clause License', 'meaning': 'SPDX:BSD-3-Clause'},
    "BSD_2_CLAUSE": {'description': 'BSD 2-Clause License', 'meaning': 'SPDX:BSD-2-Clause'},
    "ISC": {'description': 'ISC License', 'meaning': 'SPDX:ISC'},
    "GPL_3_0": {'description': 'GNU General Public License v3.0', 'meaning': 'SPDX:GPL-3.0'},
    "GPL_2_0": {'description': 'GNU General Public License v2.0', 'meaning': 'SPDX:GPL-2.0'},
    "LGPL_3_0": {'description': 'GNU Lesser General Public License v3.0', 'meaning': 'SPDX:LGPL-3.0'},
    "LGPL_2_1": {'description': 'GNU Lesser General Public License v2.1', 'meaning': 'SPDX:LGPL-2.1'},
    "AGPL_3_0": {'description': 'GNU Affero General Public License v3.0', 'meaning': 'SPDX:AGPL-3.0'},
    "MPL_2_0": {'description': 'Mozilla Public License 2.0', 'meaning': 'SPDX:MPL-2.0'},
    "CC_BY_4_0": {'description': 'Creative Commons Attribution 4.0', 'meaning': 'SPDX:CC-BY-4.0'},
    "CC_BY_SA_4_0": {'description': 'Creative Commons Attribution-ShareAlike 4.0', 'meaning': 'SPDX:CC-BY-SA-4.0'},
    "CC_BY_NC_4_0": {'description': 'Creative Commons Attribution-NonCommercial 4.0', 'meaning': 'SPDX:CC-BY-NC-4.0'},
    "CC_BY_NC_SA_4_0": {'description': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0', 'meaning': 'SPDX:CC-BY-NC-SA-4.0'},
    "CC_BY_ND_4_0": {'description': 'Creative Commons Attribution-NoDerivatives 4.0', 'meaning': 'SPDX:CC-BY-ND-4.0'},
    "CC0_1_0": {'description': 'Creative Commons Zero v1.0 Universal', 'meaning': 'SPDX:CC0-1.0'},
    "UNLICENSE": {'description': 'The Unlicense', 'meaning': 'SPDX:Unlicense'},
    "PROPRIETARY": {'description': 'Proprietary/All rights reserved'},
    "CUSTOM": {'description': 'Custom license terms'},
}

class ResearchField(RichEnum):
    """
    Major research fields and disciplines
    """
    # Enum members
    PHYSICS = "PHYSICS"
    CHEMISTRY = "CHEMISTRY"
    BIOLOGY = "BIOLOGY"
    MATHEMATICS = "MATHEMATICS"
    EARTH_SCIENCES = "EARTH_SCIENCES"
    ASTRONOMY = "ASTRONOMY"
    MEDICINE = "MEDICINE"
    NEUROSCIENCE = "NEUROSCIENCE"
    GENETICS = "GENETICS"
    ECOLOGY = "ECOLOGY"
    MICROBIOLOGY = "MICROBIOLOGY"
    BIOCHEMISTRY = "BIOCHEMISTRY"
    COMPUTER_SCIENCE = "COMPUTER_SCIENCE"
    ENGINEERING = "ENGINEERING"
    MATERIALS_SCIENCE = "MATERIALS_SCIENCE"
    ARTIFICIAL_INTELLIGENCE = "ARTIFICIAL_INTELLIGENCE"
    ROBOTICS = "ROBOTICS"
    PSYCHOLOGY = "PSYCHOLOGY"
    SOCIOLOGY = "SOCIOLOGY"
    ECONOMICS = "ECONOMICS"
    POLITICAL_SCIENCE = "POLITICAL_SCIENCE"
    ANTHROPOLOGY = "ANTHROPOLOGY"
    EDUCATION = "EDUCATION"
    HISTORY = "HISTORY"
    PHILOSOPHY = "PHILOSOPHY"
    LITERATURE = "LITERATURE"
    LINGUISTICS = "LINGUISTICS"
    ART = "ART"
    MUSIC = "MUSIC"
    BIOINFORMATICS = "BIOINFORMATICS"
    COMPUTATIONAL_BIOLOGY = "COMPUTATIONAL_BIOLOGY"
    DATA_SCIENCE = "DATA_SCIENCE"
    COGNITIVE_SCIENCE = "COGNITIVE_SCIENCE"
    ENVIRONMENTAL_SCIENCE = "ENVIRONMENTAL_SCIENCE"
    PUBLIC_HEALTH = "PUBLIC_HEALTH"

# Set metadata after class creation to avoid it becoming an enum member
ResearchField._metadata = {
    "PHYSICS": {'description': 'Physics', 'meaning': 'NCIT:C16989'},
    "CHEMISTRY": {'description': 'Chemistry', 'meaning': 'NCIT:C16414'},
    "BIOLOGY": {'description': 'Biology', 'meaning': 'NCIT:C16345'},
    "MATHEMATICS": {'description': 'Mathematics', 'meaning': 'NCIT:C16825'},
    "EARTH_SCIENCES": {'description': 'Earth sciences and geology'},
    "ASTRONOMY": {'description': 'Astronomy and astrophysics'},
    "MEDICINE": {'description': 'Medicine and health sciences', 'meaning': 'NCIT:C16833'},
    "NEUROSCIENCE": {'description': 'Neuroscience', 'meaning': 'NCIT:C15817'},
    "GENETICS": {'description': 'Genetics and genomics', 'meaning': 'NCIT:C16624'},
    "ECOLOGY": {'description': 'Ecology and environmental science', 'meaning': 'NCIT:C16526'},
    "MICROBIOLOGY": {'meaning': 'NCIT:C16851'},
    "BIOCHEMISTRY": {'meaning': 'NCIT:C16337'},
    "COMPUTER_SCIENCE": {'description': 'Computer science'},
    "ENGINEERING": {'description': 'Engineering'},
    "MATERIALS_SCIENCE": {'description': 'Materials science'},
    "ARTIFICIAL_INTELLIGENCE": {'description': 'Artificial intelligence and machine learning'},
    "ROBOTICS": {'description': 'Robotics'},
    "PSYCHOLOGY": {'description': 'Psychology'},
    "SOCIOLOGY": {'description': 'Sociology'},
    "ECONOMICS": {'description': 'Economics'},
    "POLITICAL_SCIENCE": {'description': 'Political science'},
    "ANTHROPOLOGY": {'description': 'Anthropology'},
    "EDUCATION": {'description': 'Education'},
    "HISTORY": {'description': 'History'},
    "PHILOSOPHY": {'description': 'Philosophy'},
    "LITERATURE": {'description': 'Literature'},
    "LINGUISTICS": {'description': 'Linguistics'},
    "ART": {'description': 'Art and art history'},
    "MUSIC": {'description': 'Music and musicology'},
    "BIOINFORMATICS": {'description': 'Bioinformatics'},
    "COMPUTATIONAL_BIOLOGY": {'description': 'Computational biology'},
    "DATA_SCIENCE": {'description': 'Data science'},
    "COGNITIVE_SCIENCE": {'description': 'Cognitive science'},
    "ENVIRONMENTAL_SCIENCE": {'description': 'Environmental science'},
    "PUBLIC_HEALTH": {'description': 'Public health'},
}

class FundingType(RichEnum):
    """
    Types of research funding
    """
    # Enum members
    GRANT = "GRANT"
    CONTRACT = "CONTRACT"
    FELLOWSHIP = "FELLOWSHIP"
    AWARD = "AWARD"
    GIFT = "GIFT"
    INTERNAL = "INTERNAL"
    INDUSTRY = "INDUSTRY"
    GOVERNMENT = "GOVERNMENT"
    FOUNDATION = "FOUNDATION"
    CROWDFUNDING = "CROWDFUNDING"

# Set metadata after class creation to avoid it becoming an enum member
FundingType._metadata = {
    "GRANT": {'description': 'Research grant'},
    "CONTRACT": {'description': 'Research contract'},
    "FELLOWSHIP": {'description': 'Fellowship or scholarship', 'meaning': 'NCIT:C20003'},
    "AWARD": {'description': 'Prize or award'},
    "GIFT": {'description': 'Gift or donation'},
    "INTERNAL": {'description': 'Internal/institutional funding'},
    "INDUSTRY": {'description': 'Industry sponsorship'},
    "GOVERNMENT": {'description': 'Government funding'},
    "FOUNDATION": {'description': 'Foundation or charity funding'},
    "CROWDFUNDING": {'description': 'Crowdfunded research'},
}

class ManuscriptSection(RichEnum):
    """
    Sections of a scientific manuscript or publication
    """
    # Enum members
    TITLE = "TITLE"
    AUTHORS = "AUTHORS"
    ABSTRACT = "ABSTRACT"
    KEYWORDS = "KEYWORDS"
    INTRODUCTION = "INTRODUCTION"
    LITERATURE_REVIEW = "LITERATURE_REVIEW"
    METHODS = "METHODS"
    RESULTS = "RESULTS"
    DISCUSSION = "DISCUSSION"
    CONCLUSIONS = "CONCLUSIONS"
    RESULTS_AND_DISCUSSION = "RESULTS_AND_DISCUSSION"
    ACKNOWLEDGMENTS = "ACKNOWLEDGMENTS"
    REFERENCES = "REFERENCES"
    APPENDICES = "APPENDICES"
    SUPPLEMENTARY_MATERIAL = "SUPPLEMENTARY_MATERIAL"
    DATA_AVAILABILITY = "DATA_AVAILABILITY"
    CODE_AVAILABILITY = "CODE_AVAILABILITY"
    AUTHOR_CONTRIBUTIONS = "AUTHOR_CONTRIBUTIONS"
    CONFLICT_OF_INTEREST = "CONFLICT_OF_INTEREST"
    FUNDING = "FUNDING"
    ETHICS_STATEMENT = "ETHICS_STATEMENT"
    SYSTEMATIC_REVIEW_METHODS = "SYSTEMATIC_REVIEW_METHODS"
    META_ANALYSIS = "META_ANALYSIS"
    STUDY_PROTOCOL = "STUDY_PROTOCOL"
    CONSORT_FLOW_DIAGRAM = "CONSORT_FLOW_DIAGRAM"
    HIGHLIGHTS = "HIGHLIGHTS"
    GRAPHICAL_ABSTRACT = "GRAPHICAL_ABSTRACT"
    LAY_SUMMARY = "LAY_SUMMARY"
    BOX = "BOX"
    CASE_PRESENTATION = "CASE_PRESENTATION"
    LIMITATIONS = "LIMITATIONS"
    FUTURE_DIRECTIONS = "FUTURE_DIRECTIONS"
    GLOSSARY = "GLOSSARY"
    ABBREVIATIONS = "ABBREVIATIONS"
    OTHER_MAIN_TEXT = "OTHER_MAIN_TEXT"
    OTHER_SUPPLEMENTARY = "OTHER_SUPPLEMENTARY"

# Set metadata after class creation to avoid it becoming an enum member
ManuscriptSection._metadata = {
    "TITLE": {'meaning': 'IAO:0000305', 'annotations': {'order': 1}},
    "AUTHORS": {'description': 'Authors and affiliations', 'meaning': 'IAO:0000321', 'annotations': {'order': 2}},
    "ABSTRACT": {'description': 'Abstract', 'meaning': 'IAO:0000315', 'annotations': {'order': 3, 'typical_length': '150-300 words'}},
    "KEYWORDS": {'meaning': 'IAO:0000630', 'annotations': {'order': 4}},
    "INTRODUCTION": {'description': 'Introduction/Background', 'meaning': 'IAO:0000316', 'annotations': {'order': 5}, 'aliases': ['Background']},
    "LITERATURE_REVIEW": {'description': 'Literature review', 'meaning': 'IAO:0000639', 'annotations': {'order': 6, 'optional': True}},
    "METHODS": {'description': 'Methods/Materials and Methods', 'meaning': 'IAO:0000317', 'annotations': {'order': 7}, 'aliases': ['Materials and Methods', 'Methodology', 'Experimental']},
    "RESULTS": {'meaning': 'IAO:0000318', 'annotations': {'order': 8}, 'aliases': ['Findings']},
    "DISCUSSION": {'meaning': 'IAO:0000319', 'annotations': {'order': 9}},
    "CONCLUSIONS": {'description': 'Conclusions', 'meaning': 'IAO:0000615', 'annotations': {'order': 10}, 'aliases': ['Conclusion']},
    "RESULTS_AND_DISCUSSION": {'description': 'Combined Results and Discussion', 'annotations': {'order': 8, 'note': 'alternative to separate sections'}},
    "ACKNOWLEDGMENTS": {'description': 'Acknowledgments', 'meaning': 'IAO:0000324', 'annotations': {'order': 11}, 'aliases': ['Acknowledgements']},
    "REFERENCES": {'description': 'References/Bibliography', 'meaning': 'IAO:0000320', 'annotations': {'order': 12}, 'aliases': ['Bibliography', 'Literature Cited', 'Works Cited']},
    "APPENDICES": {'description': 'Appendices', 'meaning': 'IAO:0000326', 'annotations': {'order': 13}, 'aliases': ['Appendix']},
    "SUPPLEMENTARY_MATERIAL": {'description': 'Supplementary material', 'meaning': 'IAO:0000326', 'annotations': {'order': 14, 'location': 'often online-only'}, 'aliases': ['Supporting Information', 'Supplemental Data']},
    "DATA_AVAILABILITY": {'description': 'Data availability statement', 'meaning': 'IAO:0000611', 'annotations': {'order': 11.1, 'required_by': 'many journals'}},
    "CODE_AVAILABILITY": {'description': 'Code availability statement', 'meaning': 'IAO:0000611', 'annotations': {'order': 11.2}},
    "AUTHOR_CONTRIBUTIONS": {'description': 'Author contributions', 'meaning': 'IAO:0000323', 'annotations': {'order': 11.3}, 'aliases': ['CRediT statement']},
    "CONFLICT_OF_INTEREST": {'description': 'Conflict of interest statement', 'meaning': 'IAO:0000616', 'annotations': {'order': 11.4}, 'aliases': ['Competing Interests', 'Declaration of Interests']},
    "FUNDING": {'description': 'Funding information', 'meaning': 'IAO:0000623', 'annotations': {'order': 11.5}, 'aliases': ['Financial Support', 'Grant Information']},
    "ETHICS_STATEMENT": {'description': 'Ethics approval statement', 'meaning': 'IAO:0000620', 'annotations': {'order': 11.6}},
    "SYSTEMATIC_REVIEW_METHODS": {'description': 'Systematic review methodology (PRISMA)', 'annotations': {'specific_to': 'systematic reviews'}},
    "META_ANALYSIS": {'description': 'Meta-analysis section', 'annotations': {'specific_to': 'meta-analyses'}},
    "STUDY_PROTOCOL": {'description': 'Study protocol', 'annotations': {'specific_to': 'clinical trials'}},
    "CONSORT_FLOW_DIAGRAM": {'description': 'CONSORT flow diagram', 'annotations': {'specific_to': 'randomized trials'}},
    "HIGHLIGHTS": {'description': 'Highlights/Key points', 'annotations': {'order': 3.5, 'typical_length': '3-5 bullet points'}},
    "GRAPHICAL_ABSTRACT": {'description': 'Graphical abstract', 'meaning': 'IAO:0000707', 'annotations': {'order': 3.6, 'format': 'visual'}},
    "LAY_SUMMARY": {'description': 'Lay summary/Plain language summary', 'meaning': 'IAO:0000609', 'annotations': {'order': 3.7, 'audience': 'general public'}},
    "BOX": {'description': 'Box/Sidebar with supplementary information', 'annotations': {'placement': 'variable'}},
    "CASE_PRESENTATION": {'description': 'Case presentation (for case reports)', 'meaning': 'IAO:0000613', 'annotations': {'specific_to': 'case reports'}},
    "LIMITATIONS": {'description': 'Limitations section', 'meaning': 'IAO:0000631', 'annotations': {'often_part_of': 'Discussion'}},
    "FUTURE_DIRECTIONS": {'description': 'Future directions/Future work', 'meaning': 'IAO:0000625', 'annotations': {'often_part_of': 'Discussion or Conclusions'}},
    "GLOSSARY": {'description': 'Glossary of terms', 'annotations': {'placement': 'front or back matter'}},
    "ABBREVIATIONS": {'description': 'List of abbreviations', 'meaning': 'IAO:0000606', 'annotations': {'placement': 'front matter'}},
    "OTHER_MAIN_TEXT": {'description': 'Other main text section', 'annotations': {'catch_all': True}},
    "OTHER_SUPPLEMENTARY": {'description': 'Other supplementary section', 'annotations': {'catch_all': True}},
}

class ResearchRole(RichEnum):
    """
    Roles in research and authorship
    """
    # Enum members
    CONCEPTUALIZATION = "CONCEPTUALIZATION"
    DATA_CURATION = "DATA_CURATION"
    FORMAL_ANALYSIS = "FORMAL_ANALYSIS"
    FUNDING_ACQUISITION = "FUNDING_ACQUISITION"
    INVESTIGATION = "INVESTIGATION"
    METHODOLOGY = "METHODOLOGY"
    PROJECT_ADMINISTRATION = "PROJECT_ADMINISTRATION"
    RESOURCES = "RESOURCES"
    SOFTWARE = "SOFTWARE"
    SUPERVISION = "SUPERVISION"
    VALIDATION = "VALIDATION"
    VISUALIZATION = "VISUALIZATION"
    WRITING_ORIGINAL = "WRITING_ORIGINAL"
    WRITING_REVIEW = "WRITING_REVIEW"
    FIRST_AUTHOR = "FIRST_AUTHOR"
    CORRESPONDING_AUTHOR = "CORRESPONDING_AUTHOR"
    SENIOR_AUTHOR = "SENIOR_AUTHOR"
    CO_AUTHOR = "CO_AUTHOR"
    PRINCIPAL_INVESTIGATOR = "PRINCIPAL_INVESTIGATOR"
    CO_INVESTIGATOR = "CO_INVESTIGATOR"
    COLLABORATOR = "COLLABORATOR"

# Set metadata after class creation to avoid it becoming an enum member
ResearchRole._metadata = {
    "CONCEPTUALIZATION": {'description': 'Ideas; formulation of research goals', 'meaning': 'CRediT:conceptualization'},
    "DATA_CURATION": {'description': 'Data management and annotation', 'meaning': 'CRediT:data-curation'},
    "FORMAL_ANALYSIS": {'description': 'Statistical and mathematical analysis', 'meaning': 'CRediT:formal-analysis'},
    "FUNDING_ACQUISITION": {'description': 'Acquisition of financial support', 'meaning': 'CRediT:funding-acquisition'},
    "INVESTIGATION": {'description': 'Conducting research and data collection', 'meaning': 'CRediT:investigation'},
    "METHODOLOGY": {'description': 'Development of methodology', 'meaning': 'CRediT:methodology'},
    "PROJECT_ADMINISTRATION": {'description': 'Project management and coordination', 'meaning': 'CRediT:project-administration'},
    "RESOURCES": {'description': 'Provision of materials and tools', 'meaning': 'CRediT:resources'},
    "SOFTWARE": {'description': 'Programming and software development', 'meaning': 'CRediT:software'},
    "SUPERVISION": {'description': 'Oversight and mentorship', 'meaning': 'CRediT:supervision'},
    "VALIDATION": {'description': 'Verification of results', 'meaning': 'CRediT:validation'},
    "VISUALIZATION": {'description': 'Data presentation and visualization', 'meaning': 'CRediT:visualization'},
    "WRITING_ORIGINAL": {'description': 'Writing - original draft', 'meaning': 'CRediT:writing-original-draft'},
    "WRITING_REVIEW": {'description': 'Writing - review and editing', 'meaning': 'CRediT:writing-review-editing'},
    "FIRST_AUTHOR": {'description': 'First/lead author', 'meaning': 'MS:1002034'},
    "CORRESPONDING_AUTHOR": {'meaning': 'NCIT:C164481'},
    "SENIOR_AUTHOR": {'description': 'Senior/last author', 'annotations': {'note': 'Often the PI or lab head'}},
    "CO_AUTHOR": {'description': 'Co-author', 'meaning': 'NCIT:C42781'},
    "PRINCIPAL_INVESTIGATOR": {'description': 'Principal investigator (PI)', 'meaning': 'NCIT:C19924'},
    "CO_INVESTIGATOR": {'meaning': 'NCIT:C51812'},
    "COLLABORATOR": {'meaning': 'NCIT:C84336'},
}

class OpenAccessType(RichEnum):
    """
    Types of open access publishing
    """
    # Enum members
    GOLD = "GOLD"
    GREEN = "GREEN"
    HYBRID = "HYBRID"
    DIAMOND = "DIAMOND"
    BRONZE = "BRONZE"
    CLOSED = "CLOSED"
    EMBARGO = "EMBARGO"

# Set metadata after class creation to avoid it becoming an enum member
OpenAccessType._metadata = {
    "GOLD": {'description': 'Gold open access (published OA)'},
    "GREEN": {'description': 'Green open access (self-archived)'},
    "HYBRID": {'description': 'Hybrid journal with OA option'},
    "DIAMOND": {'description': 'Diamond/platinum OA (no fees)'},
    "BRONZE": {'description': 'Free to read but no license'},
    "CLOSED": {'description': 'Closed access/subscription only'},
    "EMBARGO": {'description': 'Under embargo period'},
}

class CitationStyle(RichEnum):
    """
    Common citation and reference styles
    """
    # Enum members
    APA = "APA"
    MLA = "MLA"
    CHICAGO = "CHICAGO"
    HARVARD = "HARVARD"
    VANCOUVER = "VANCOUVER"
    IEEE = "IEEE"
    ACS = "ACS"
    AMA = "AMA"
    NATURE = "NATURE"
    SCIENCE = "SCIENCE"
    CELL = "CELL"

# Set metadata after class creation to avoid it becoming an enum member
CitationStyle._metadata = {
    "APA": {'description': 'American Psychological Association'},
    "MLA": {'description': 'Modern Language Association'},
    "CHICAGO": {'description': 'Chicago Manual of Style'},
    "HARVARD": {'description': 'Harvard referencing'},
    "VANCOUVER": {'description': 'Vancouver style (biomedical)'},
    "IEEE": {'description': 'Institute of Electrical and Electronics Engineers'},
    "ACS": {'description': 'American Chemical Society'},
    "AMA": {'description': 'American Medical Association'},
    "NATURE": {'description': 'Nature style'},
    "SCIENCE": {'description': 'Science style'},
    "CELL": {'description': 'Cell Press style'},
}

class EnergySource(RichEnum):
    """
    Types of energy sources and generation methods
    """
    # Enum members
    SOLAR = "SOLAR"
    WIND = "WIND"
    HYDROELECTRIC = "HYDROELECTRIC"
    GEOTHERMAL = "GEOTHERMAL"
    BIOMASS = "BIOMASS"
    BIOFUEL = "BIOFUEL"
    TIDAL = "TIDAL"
    HYDROGEN = "HYDROGEN"
    COAL = "COAL"
    NATURAL_GAS = "NATURAL_GAS"
    PETROLEUM = "PETROLEUM"
    DIESEL = "DIESEL"
    GASOLINE = "GASOLINE"
    PROPANE = "PROPANE"
    NUCLEAR_FISSION = "NUCLEAR_FISSION"
    NUCLEAR_FUSION = "NUCLEAR_FUSION"
    GRID_MIX = "GRID_MIX"
    BATTERY_STORAGE = "BATTERY_STORAGE"

# Set metadata after class creation to avoid it becoming an enum member
EnergySource._metadata = {
    "SOLAR": {'meaning': 'ENVO:01001862', 'annotations': {'renewable': True, 'emission_free': True}, 'aliases': ['Solar radiation']},
    "WIND": {'annotations': {'renewable': True, 'emission_free': True}, 'aliases': ['wind wave energy']},
    "HYDROELECTRIC": {'annotations': {'renewable': True, 'emission_free': True}, 'aliases': ['hydroelectric dam']},
    "GEOTHERMAL": {'meaning': 'ENVO:2000034', 'annotations': {'renewable': True, 'emission_free': True}, 'aliases': ['geothermal energy']},
    "BIOMASS": {'annotations': {'renewable': True, 'emission_free': False}, 'aliases': ['organic material']},
    "BIOFUEL": {'annotations': {'renewable': True, 'emission_free': False}},
    "TIDAL": {'annotations': {'renewable': True, 'emission_free': True}},
    "HYDROGEN": {'meaning': 'CHEBI:18276', 'annotations': {'renewable': 'depends', 'emission_free': True}, 'aliases': ['dihydrogen']},
    "COAL": {'meaning': 'ENVO:02000091', 'annotations': {'renewable': False, 'emission_free': False, 'fossil_fuel': True}},
    "NATURAL_GAS": {'meaning': 'ENVO:01000552', 'annotations': {'renewable': False, 'emission_free': False, 'fossil_fuel': True}},
    "PETROLEUM": {'meaning': 'ENVO:00002984', 'annotations': {'renewable': False, 'emission_free': False, 'fossil_fuel': True}},
    "DIESEL": {'meaning': 'ENVO:03510006', 'annotations': {'renewable': False, 'emission_free': False, 'fossil_fuel': True}, 'aliases': ['diesel fuel']},
    "GASOLINE": {'annotations': {'renewable': False, 'emission_free': False, 'fossil_fuel': True}, 'aliases': ['fuel oil']},
    "PROPANE": {'meaning': 'ENVO:01000553', 'annotations': {'renewable': False, 'emission_free': False, 'fossil_fuel': True}, 'aliases': ['liquefied petroleum gas']},
    "NUCLEAR_FISSION": {'annotations': {'renewable': False, 'emission_free': True}, 'aliases': ['nuclear energy']},
    "NUCLEAR_FUSION": {'annotations': {'renewable': False, 'emission_free': True}, 'aliases': ['nuclear energy']},
    "GRID_MIX": {'annotations': {'renewable': 'partial'}},
    "BATTERY_STORAGE": {'description': 'Battery storage systems', 'annotations': {'storage': True}},
}

class EnergyUnit(RichEnum):
    """
    Units for measuring energy
    """
    # Enum members
    JOULE = "JOULE"
    KILOJOULE = "KILOJOULE"
    MEGAJOULE = "MEGAJOULE"
    GIGAJOULE = "GIGAJOULE"
    WATT_HOUR = "WATT_HOUR"
    KILOWATT_HOUR = "KILOWATT_HOUR"
    MEGAWATT_HOUR = "MEGAWATT_HOUR"
    GIGAWATT_HOUR = "GIGAWATT_HOUR"
    TERAWATT_HOUR = "TERAWATT_HOUR"
    CALORIE = "CALORIE"
    KILOCALORIE = "KILOCALORIE"
    BTU = "BTU"
    THERM = "THERM"
    ELECTRON_VOLT = "ELECTRON_VOLT"
    TOE = "TOE"
    TCE = "TCE"

# Set metadata after class creation to avoid it becoming an enum member
EnergyUnit._metadata = {
    "JOULE": {'description': 'Joule (J)', 'meaning': 'QUDT:J', 'annotations': {'symbol': 'J', 'ucum': 'J', 'si_base': True}},
    "KILOJOULE": {'description': 'Kilojoule (kJ)', 'meaning': 'QUDT:KiloJ', 'annotations': {'symbol': 'kJ', 'ucum': 'kJ', 'joules': 1000}},
    "MEGAJOULE": {'description': 'Megajoule (MJ)', 'meaning': 'QUDT:MegaJ', 'annotations': {'symbol': 'MJ', 'ucum': 'MJ', 'joules': '1e6'}},
    "GIGAJOULE": {'description': 'Gigajoule (GJ)', 'meaning': 'QUDT:GigaJ', 'annotations': {'symbol': 'GJ', 'ucum': 'GJ', 'joules': '1e9'}},
    "WATT_HOUR": {'description': 'Watt-hour (Wh)', 'meaning': 'QUDT:W-HR', 'annotations': {'symbol': 'Wh', 'ucum': 'W.h', 'joules': 3600}},
    "KILOWATT_HOUR": {'description': 'Kilowatt-hour (kWh)', 'meaning': 'QUDT:KiloW-HR', 'annotations': {'symbol': 'kWh', 'ucum': 'kW.h', 'joules': '3.6e6'}},
    "MEGAWATT_HOUR": {'description': 'Megawatt-hour (MWh)', 'meaning': 'QUDT:MegaW-HR', 'annotations': {'symbol': 'MWh', 'ucum': 'MW.h', 'joules': '3.6e9'}},
    "GIGAWATT_HOUR": {'description': 'Gigawatt-hour (GWh)', 'meaning': 'QUDT:GigaW-HR', 'annotations': {'symbol': 'GWh', 'ucum': 'GW.h', 'joules': '3.6e12'}},
    "TERAWATT_HOUR": {'description': 'Terawatt-hour (TWh)', 'meaning': 'QUDT:TeraW-HR', 'annotations': {'symbol': 'TWh', 'ucum': 'TW.h', 'joules': '3.6e15'}},
    "CALORIE": {'description': 'Calorie (cal)', 'meaning': 'QUDT:CAL', 'annotations': {'symbol': 'cal', 'ucum': 'cal', 'joules': 4.184}},
    "KILOCALORIE": {'description': 'Kilocalorie (kcal)', 'meaning': 'QUDT:KiloCAL', 'annotations': {'symbol': 'kcal', 'ucum': 'kcal', 'joules': 4184}},
    "BTU": {'description': 'British thermal unit', 'meaning': 'QUDT:BTU_IT', 'annotations': {'symbol': 'BTU', 'ucum': '[Btu_IT]', 'joules': 1055.06}},
    "THERM": {'description': 'Therm', 'meaning': 'QUDT:THM_US', 'annotations': {'symbol': 'thm', 'ucum': '[thm_us]', 'joules': '1.055e8'}},
    "ELECTRON_VOLT": {'description': 'Electron volt (eV)', 'meaning': 'QUDT:EV', 'annotations': {'symbol': 'eV', 'ucum': 'eV', 'joules': 1.602e-19}},
    "TOE": {'description': 'Tonne of oil equivalent', 'meaning': 'QUDT:TOE', 'annotations': {'symbol': 'toe', 'ucum': 'toe', 'joules': '4.187e10'}},
    "TCE": {'description': 'Tonne of coal equivalent', 'annotations': {'symbol': 'tce', 'ucum': 'tce', 'joules': '2.93e10'}},
}

class PowerUnit(RichEnum):
    """
    Units for measuring power (energy per time)
    """
    # Enum members
    WATT = "WATT"
    KILOWATT = "KILOWATT"
    MEGAWATT = "MEGAWATT"
    GIGAWATT = "GIGAWATT"
    TERAWATT = "TERAWATT"
    HORSEPOWER = "HORSEPOWER"
    BTU_PER_HOUR = "BTU_PER_HOUR"

# Set metadata after class creation to avoid it becoming an enum member
PowerUnit._metadata = {
    "WATT": {'description': 'Watt (W)', 'meaning': 'QUDT:W', 'annotations': {'symbol': 'W', 'ucum': 'W', 'si_base': True}},
    "KILOWATT": {'description': 'Kilowatt (kW)', 'meaning': 'QUDT:KiloW', 'annotations': {'symbol': 'kW', 'ucum': 'kW', 'watts': 1000}},
    "MEGAWATT": {'description': 'Megawatt (MW)', 'meaning': 'QUDT:MegaW', 'annotations': {'symbol': 'MW', 'ucum': 'MW', 'watts': '1e6'}},
    "GIGAWATT": {'description': 'Gigawatt (GW)', 'meaning': 'QUDT:GigaW', 'annotations': {'symbol': 'GW', 'ucum': 'GW', 'watts': '1e9'}},
    "TERAWATT": {'description': 'Terawatt (TW)', 'meaning': 'QUDT:TeraW', 'annotations': {'symbol': 'TW', 'ucum': 'TW', 'watts': '1e12'}},
    "HORSEPOWER": {'description': 'Horsepower', 'meaning': 'QUDT:HP', 'annotations': {'symbol': 'hp', 'ucum': '[HP]', 'watts': 745.7}},
    "BTU_PER_HOUR": {'description': 'BTU per hour', 'annotations': {'symbol': 'BTU/h', 'ucum': '[Btu_IT]/h', 'watts': 0.293}},
}

class EnergyEfficiencyRating(RichEnum):
    """
    Energy efficiency ratings and standards
    """
    # Enum members
    A_PLUS_PLUS_PLUS = "A_PLUS_PLUS_PLUS"
    A_PLUS_PLUS = "A_PLUS_PLUS"
    A_PLUS = "A_PLUS"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    ENERGY_STAR = "ENERGY_STAR"
    ENERGY_STAR_MOST_EFFICIENT = "ENERGY_STAR_MOST_EFFICIENT"

# Set metadata after class creation to avoid it becoming an enum member
EnergyEfficiencyRating._metadata = {
    "A_PLUS_PLUS_PLUS": {'description': 'A+++ (highest efficiency)', 'annotations': {'rank': 1, 'region': 'EU'}},
    "A_PLUS_PLUS": {'description': 'A++', 'annotations': {'rank': 2, 'region': 'EU'}},
    "A_PLUS": {'description': 'A+', 'annotations': {'rank': 3, 'region': 'EU'}},
    "A": {'description': 'A', 'annotations': {'rank': 4, 'region': 'EU'}},
    "B": {'description': 'B', 'annotations': {'rank': 5, 'region': 'EU'}},
    "C": {'description': 'C', 'annotations': {'rank': 6, 'region': 'EU'}},
    "D": {'description': 'D', 'annotations': {'rank': 7, 'region': 'EU'}},
    "E": {'description': 'E', 'annotations': {'rank': 8, 'region': 'EU'}},
    "F": {'description': 'F', 'annotations': {'rank': 9, 'region': 'EU'}},
    "G": {'description': 'G (lowest efficiency)', 'annotations': {'rank': 10, 'region': 'EU'}},
    "ENERGY_STAR": {'description': 'Energy Star certified', 'annotations': {'region': 'US'}},
    "ENERGY_STAR_MOST_EFFICIENT": {'description': 'Energy Star Most Efficient', 'annotations': {'region': 'US'}},
}

class BuildingEnergyStandard(RichEnum):
    """
    Building energy efficiency standards and certifications
    """
    # Enum members
    PASSIVE_HOUSE = "PASSIVE_HOUSE"
    LEED_PLATINUM = "LEED_PLATINUM"
    LEED_GOLD = "LEED_GOLD"
    LEED_SILVER = "LEED_SILVER"
    LEED_CERTIFIED = "LEED_CERTIFIED"
    BREEAM_OUTSTANDING = "BREEAM_OUTSTANDING"
    BREEAM_EXCELLENT = "BREEAM_EXCELLENT"
    BREEAM_VERY_GOOD = "BREEAM_VERY_GOOD"
    BREEAM_GOOD = "BREEAM_GOOD"
    BREEAM_PASS = "BREEAM_PASS"
    NET_ZERO = "NET_ZERO"
    ENERGY_POSITIVE = "ENERGY_POSITIVE"
    ZERO_CARBON = "ZERO_CARBON"

# Set metadata after class creation to avoid it becoming an enum member
BuildingEnergyStandard._metadata = {
    "PASSIVE_HOUSE": {'description': 'Passive House (Passivhaus) standard'},
    "LEED_PLATINUM": {'description': 'LEED Platinum certification'},
    "LEED_GOLD": {'description': 'LEED Gold certification'},
    "LEED_SILVER": {'description': 'LEED Silver certification'},
    "LEED_CERTIFIED": {'description': 'LEED Certified'},
    "BREEAM_OUTSTANDING": {'description': 'BREEAM Outstanding'},
    "BREEAM_EXCELLENT": {'description': 'BREEAM Excellent'},
    "BREEAM_VERY_GOOD": {'description': 'BREEAM Very Good'},
    "BREEAM_GOOD": {'description': 'BREEAM Good'},
    "BREEAM_PASS": {'description': 'BREEAM Pass'},
    "NET_ZERO": {'description': 'Net Zero Energy Building'},
    "ENERGY_POSITIVE": {'description': 'Energy Positive Building'},
    "ZERO_CARBON": {'description': 'Zero Carbon Building'},
}

class GridType(RichEnum):
    """
    Types of electrical grid systems
    """
    # Enum members
    MAIN_GRID = "MAIN_GRID"
    MICROGRID = "MICROGRID"
    OFF_GRID = "OFF_GRID"
    SMART_GRID = "SMART_GRID"
    MINI_GRID = "MINI_GRID"
    VIRTUAL_POWER_PLANT = "VIRTUAL_POWER_PLANT"

# Set metadata after class creation to avoid it becoming an enum member
GridType._metadata = {
    "MAIN_GRID": {'description': 'Main utility grid'},
    "MICROGRID": {'description': 'Microgrid'},
    "OFF_GRID": {'description': 'Off-grid/standalone'},
    "SMART_GRID": {'description': 'Smart grid'},
    "MINI_GRID": {'description': 'Mini-grid'},
    "VIRTUAL_POWER_PLANT": {'description': 'Virtual power plant'},
}

class EnergyStorageType(RichEnum):
    """
    Types of energy storage systems
    """
    # Enum members
    LITHIUM_ION_BATTERY = "LITHIUM_ION_BATTERY"
    LEAD_ACID_BATTERY = "LEAD_ACID_BATTERY"
    FLOW_BATTERY = "FLOW_BATTERY"
    SOLID_STATE_BATTERY = "SOLID_STATE_BATTERY"
    SODIUM_ION_BATTERY = "SODIUM_ION_BATTERY"
    PUMPED_HYDRO = "PUMPED_HYDRO"
    COMPRESSED_AIR = "COMPRESSED_AIR"
    FLYWHEEL = "FLYWHEEL"
    GRAVITY_STORAGE = "GRAVITY_STORAGE"
    MOLTEN_SALT = "MOLTEN_SALT"
    ICE_STORAGE = "ICE_STORAGE"
    PHASE_CHANGE = "PHASE_CHANGE"
    HYDROGEN_STORAGE = "HYDROGEN_STORAGE"
    SYNTHETIC_FUEL = "SYNTHETIC_FUEL"
    SUPERCAPACITOR = "SUPERCAPACITOR"
    SUPERCONDUCTING = "SUPERCONDUCTING"

# Set metadata after class creation to avoid it becoming an enum member
EnergyStorageType._metadata = {
    "LITHIUM_ION_BATTERY": {'description': 'Lithium-ion battery', 'annotations': {'category': 'electrochemical'}},
    "LEAD_ACID_BATTERY": {'description': 'Lead-acid battery', 'annotations': {'category': 'electrochemical'}},
    "FLOW_BATTERY": {'description': 'Flow battery (e.g., vanadium redox)', 'annotations': {'category': 'electrochemical'}},
    "SOLID_STATE_BATTERY": {'description': 'Solid-state battery', 'annotations': {'category': 'electrochemical'}},
    "SODIUM_ION_BATTERY": {'description': 'Sodium-ion battery', 'annotations': {'category': 'electrochemical'}},
    "PUMPED_HYDRO": {'description': 'Pumped hydroelectric storage', 'annotations': {'category': 'mechanical'}},
    "COMPRESSED_AIR": {'description': 'Compressed air energy storage (CAES)', 'annotations': {'category': 'mechanical'}},
    "FLYWHEEL": {'description': 'Flywheel energy storage', 'annotations': {'category': 'mechanical'}},
    "GRAVITY_STORAGE": {'description': 'Gravity-based storage', 'annotations': {'category': 'mechanical'}},
    "MOLTEN_SALT": {'description': 'Molten salt thermal storage', 'annotations': {'category': 'thermal'}},
    "ICE_STORAGE": {'description': 'Ice thermal storage', 'annotations': {'category': 'thermal'}},
    "PHASE_CHANGE": {'description': 'Phase change materials', 'annotations': {'category': 'thermal'}},
    "HYDROGEN_STORAGE": {'description': 'Hydrogen storage', 'annotations': {'category': 'chemical'}},
    "SYNTHETIC_FUEL": {'description': 'Synthetic fuel storage', 'annotations': {'category': 'chemical'}},
    "SUPERCAPACITOR": {'description': 'Supercapacitor', 'annotations': {'category': 'electrical'}},
    "SUPERCONDUCTING": {'description': 'Superconducting magnetic energy storage (SMES)', 'annotations': {'category': 'electrical'}},
}

class EmissionScope(RichEnum):
    """
    Greenhouse gas emission scopes (GHG Protocol)
    """
    # Enum members
    SCOPE_1 = "SCOPE_1"
    SCOPE_2 = "SCOPE_2"
    SCOPE_3 = "SCOPE_3"
    SCOPE_3_UPSTREAM = "SCOPE_3_UPSTREAM"
    SCOPE_3_DOWNSTREAM = "SCOPE_3_DOWNSTREAM"

# Set metadata after class creation to avoid it becoming an enum member
EmissionScope._metadata = {
    "SCOPE_1": {'description': 'Direct emissions from owned or controlled sources', 'annotations': {'ghg_protocol': 'Scope 1'}},
    "SCOPE_2": {'description': 'Indirect emissions from purchased energy', 'annotations': {'ghg_protocol': 'Scope 2'}},
    "SCOPE_3": {'description': 'All other indirect emissions in value chain', 'annotations': {'ghg_protocol': 'Scope 3'}},
    "SCOPE_3_UPSTREAM": {'description': 'Upstream Scope 3 emissions', 'annotations': {'ghg_protocol': 'Scope 3'}},
    "SCOPE_3_DOWNSTREAM": {'description': 'Downstream Scope 3 emissions', 'annotations': {'ghg_protocol': 'Scope 3'}},
}

class CarbonIntensity(RichEnum):
    """
    Carbon intensity levels for energy sources
    """
    # Enum members
    ZERO_CARBON = "ZERO_CARBON"
    VERY_LOW_CARBON = "VERY_LOW_CARBON"
    LOW_CARBON = "LOW_CARBON"
    MEDIUM_CARBON = "MEDIUM_CARBON"
    HIGH_CARBON = "HIGH_CARBON"
    VERY_HIGH_CARBON = "VERY_HIGH_CARBON"

# Set metadata after class creation to avoid it becoming an enum member
CarbonIntensity._metadata = {
    "ZERO_CARBON": {'description': 'Zero carbon emissions', 'annotations': {'gCO2_per_kWh': 0}},
    "VERY_LOW_CARBON": {'description': 'Very low carbon (< 50 gCO2/kWh)', 'annotations': {'gCO2_per_kWh': '0-50'}},
    "LOW_CARBON": {'description': 'Low carbon (50-200 gCO2/kWh)', 'annotations': {'gCO2_per_kWh': '50-200'}},
    "MEDIUM_CARBON": {'description': 'Medium carbon (200-500 gCO2/kWh)', 'annotations': {'gCO2_per_kWh': '200-500'}},
    "HIGH_CARBON": {'description': 'High carbon (500-1000 gCO2/kWh)', 'annotations': {'gCO2_per_kWh': '500-1000'}},
    "VERY_HIGH_CARBON": {'description': 'Very high carbon (> 1000 gCO2/kWh)', 'annotations': {'gCO2_per_kWh': '1000+'}},
}

class ElectricityMarket(RichEnum):
    """
    Types of electricity markets and pricing
    """
    # Enum members
    SPOT_MARKET = "SPOT_MARKET"
    DAY_AHEAD = "DAY_AHEAD"
    INTRADAY = "INTRADAY"
    FUTURES = "FUTURES"
    CAPACITY_MARKET = "CAPACITY_MARKET"
    ANCILLARY_SERVICES = "ANCILLARY_SERVICES"
    BILATERAL = "BILATERAL"
    FEED_IN_TARIFF = "FEED_IN_TARIFF"
    NET_METERING = "NET_METERING"
    POWER_PURCHASE_AGREEMENT = "POWER_PURCHASE_AGREEMENT"

# Set metadata after class creation to avoid it becoming an enum member
ElectricityMarket._metadata = {
    "SPOT_MARKET": {'description': 'Spot market/real-time pricing'},
    "DAY_AHEAD": {'description': 'Day-ahead market'},
    "INTRADAY": {'description': 'Intraday market'},
    "FUTURES": {'description': 'Futures market'},
    "CAPACITY_MARKET": {'description': 'Capacity market'},
    "ANCILLARY_SERVICES": {'description': 'Ancillary services market'},
    "BILATERAL": {'description': 'Bilateral contracts'},
    "FEED_IN_TARIFF": {'description': 'Feed-in tariff'},
    "NET_METERING": {'description': 'Net metering'},
    "POWER_PURCHASE_AGREEMENT": {'description': 'Power purchase agreement (PPA)'},
}

class FossilFuelTypeEnum(RichEnum):
    """
    Types of fossil fuels used for energy generation
    """
    # Enum members
    COAL = "COAL"
    NATURAL_GAS = "NATURAL_GAS"
    PETROLEUM = "PETROLEUM"

# Set metadata after class creation to avoid it becoming an enum member
FossilFuelTypeEnum._metadata = {
    "COAL": {'description': 'Coal', 'meaning': 'ENVO:02000091'},
    "NATURAL_GAS": {'description': 'Natural gas', 'meaning': 'ENVO:01000552'},
    "PETROLEUM": {'description': 'Petroleum', 'meaning': 'ENVO:00002984'},
}

class ReactorTypeEnum(RichEnum):
    """
    Nuclear reactor types based on design and operational characteristics
    """
    # Enum members
    PWR = "PWR"
    BWR = "BWR"
    PHWR = "PHWR"
    LWGR = "LWGR"
    AGR = "AGR"
    GCR = "GCR"
    FBR = "FBR"
    HTGR = "HTGR"
    MSR = "MSR"
    SMR = "SMR"
    VHTR = "VHTR"
    SFR = "SFR"
    LFR = "LFR"
    GFR = "GFR"
    SCWR = "SCWR"

# Set metadata after class creation to avoid it becoming an enum member
ReactorTypeEnum._metadata = {
    "PWR": {'description': 'Most common reactor type using light water under pressure', 'annotations': {'coolant': 'light water', 'moderator': 'light water', 'pressure': 'high', 'steam_generation': 'indirect', 'worldwide_count': '~300', 'fuel_enrichment': '3-5%'}, 'aliases': ['Pressurized Water Reactor']},
    "BWR": {'description': 'Light water reactor where water boils directly in core', 'annotations': {'coolant': 'light water', 'moderator': 'light water', 'pressure': 'medium', 'steam_generation': 'direct', 'worldwide_count': '~60', 'fuel_enrichment': '3-5%'}, 'aliases': ['Boiling Water Reactor']},
    "PHWR": {'description': 'Heavy water moderated and cooled reactor (CANDU type)', 'annotations': {'coolant': 'heavy water', 'moderator': 'heavy water', 'pressure': 'high', 'steam_generation': 'indirect', 'worldwide_count': '~47', 'fuel_enrichment': 'natural uranium'}, 'aliases': ['CANDU', 'Pressurized Heavy Water Reactor']},
    "LWGR": {'description': 'Graphite moderated, light water cooled reactor (RBMK type)', 'annotations': {'coolant': 'light water', 'moderator': 'graphite', 'pressure': 'medium', 'steam_generation': 'direct', 'worldwide_count': '~10', 'fuel_enrichment': '1.8-2.4%'}, 'aliases': ['RBMK', 'Light Water Graphite Reactor']},
    "AGR": {'description': 'Graphite moderated, CO2 gas cooled reactor', 'annotations': {'coolant': 'carbon dioxide', 'moderator': 'graphite', 'pressure': 'high', 'steam_generation': 'indirect', 'worldwide_count': '~8', 'fuel_enrichment': '2.5-3.5%'}, 'aliases': ['Advanced Gas-Cooled Reactor']},
    "GCR": {'description': 'Early gas-cooled reactor design (Magnox type)', 'annotations': {'coolant': 'carbon dioxide', 'moderator': 'graphite', 'pressure': 'low', 'fuel_enrichment': 'natural uranium'}, 'aliases': ['Magnox', 'Gas-Cooled Reactor']},
    "FBR": {'description': 'Fast neutron reactor that breeds fissile material', 'annotations': {'coolant': 'liquid metal', 'moderator': 'none', 'neutron_spectrum': 'fast', 'worldwide_count': '~2', 'fuel_enrichment': '15-20%'}, 'aliases': ['Fast Breeder Reactor', 'Liquid Metal Fast Breeder Reactor']},
    "HTGR": {'description': 'Helium-cooled reactor with TRISO fuel', 'annotations': {'coolant': 'helium', 'moderator': 'graphite', 'temperature': 'very high', 'fuel_type': 'TRISO'}, 'aliases': ['High Temperature Gas-Cooled Reactor']},
    "MSR": {'description': 'Reactor using molten salt as coolant and/or fuel', 'annotations': {'coolant': 'molten salt', 'fuel_form': 'liquid', 'generation': 'IV'}, 'aliases': ['Molten Salt Reactor']},
    "SMR": {'description': 'Small reactors designed for modular construction', 'annotations': {'power_output': '<300 MWe', 'modularity': 'high', 'generation': 'III+/IV'}, 'aliases': ['Small Modular Reactor']},
    "VHTR": {'description': 'Generation IV reactor for very high temperature applications', 'annotations': {'temperature': '>950°C', 'generation': 'IV', 'coolant': 'helium'}, 'aliases': ['Very High Temperature Reactor']},
    "SFR": {'description': 'Fast reactor cooled by liquid sodium', 'annotations': {'coolant': 'liquid sodium', 'neutron_spectrum': 'fast', 'generation': 'IV'}, 'aliases': ['Sodium-Cooled Fast Reactor']},
    "LFR": {'description': 'Fast reactor cooled by liquid lead or lead-bismuth', 'annotations': {'coolant': 'liquid lead', 'neutron_spectrum': 'fast', 'generation': 'IV'}, 'aliases': ['Lead-Cooled Fast Reactor']},
    "GFR": {'description': 'Fast reactor with gas cooling', 'annotations': {'coolant': 'helium', 'neutron_spectrum': 'fast', 'generation': 'IV'}, 'aliases': ['Gas-Cooled Fast Reactor']},
    "SCWR": {'description': 'Reactor using supercritical water as coolant', 'annotations': {'coolant': 'supercritical water', 'generation': 'IV'}, 'aliases': ['Supercritical Water-Cooled Reactor']},
}

class ReactorGenerationEnum(RichEnum):
    """
    Nuclear reactor generational classifications
    """
    # Enum members
    GENERATION_I = "GENERATION_I"
    GENERATION_II = "GENERATION_II"
    GENERATION_III = "GENERATION_III"
    GENERATION_III_PLUS = "GENERATION_III_PLUS"
    GENERATION_IV = "GENERATION_IV"

# Set metadata after class creation to avoid it becoming an enum member
ReactorGenerationEnum._metadata = {
    "GENERATION_I": {'description': 'Early commercial reactors (1950s-1960s)', 'annotations': {'period': '1950s-1960s', 'status': 'retired', 'examples': 'Shippingport, Dresden-1'}},
    "GENERATION_II": {'description': 'Current operating commercial reactors', 'annotations': {'period': '1970s-1990s', 'status': 'operating', 'examples': 'PWR, BWR, CANDU', 'design_life': '40 years'}},
    "GENERATION_III": {'description': 'Advanced reactors with enhanced safety', 'annotations': {'period': '1990s-2010s', 'status': 'some operating', 'improvements': 'passive safety, standardization', 'examples': 'AP1000, EPR, ABWR'}},
    "GENERATION_III_PLUS": {'description': 'Evolutionary improvements to Generation III', 'annotations': {'period': '2000s-present', 'status': 'deployment', 'improvements': 'enhanced passive safety', 'examples': 'AP1000, APR1400'}},
    "GENERATION_IV": {'description': 'Next generation advanced reactor concepts', 'annotations': {'period': '2030s and beyond', 'status': 'development', 'goals': 'sustainability, economics, safety, proliferation resistance', 'examples': 'VHTR, SFR, LFR, GFR, SCWR, MSR'}},
}

class ReactorCoolantEnum(RichEnum):
    """
    Primary coolant types used in nuclear reactors
    """
    # Enum members
    LIGHT_WATER = "LIGHT_WATER"
    HEAVY_WATER = "HEAVY_WATER"
    CARBON_DIOXIDE = "CARBON_DIOXIDE"
    HELIUM = "HELIUM"
    LIQUID_SODIUM = "LIQUID_SODIUM"
    LIQUID_LEAD = "LIQUID_LEAD"
    MOLTEN_SALT = "MOLTEN_SALT"
    SUPERCRITICAL_WATER = "SUPERCRITICAL_WATER"

# Set metadata after class creation to avoid it becoming an enum member
ReactorCoolantEnum._metadata = {
    "LIGHT_WATER": {'description': 'Ordinary water as primary coolant', 'annotations': {'chemical_formula': 'H2O', 'density': '1.0 g/cm³', 'neutron_absorption': 'moderate'}},
    "HEAVY_WATER": {'description': 'Deuterium oxide as primary coolant', 'annotations': {'chemical_formula': 'D2O', 'density': '1.1 g/cm³', 'neutron_absorption': 'low'}},
    "CARBON_DIOXIDE": {'description': 'CO2 gas as primary coolant', 'annotations': {'chemical_formula': 'CO2', 'phase': 'gas', 'pressure': 'high'}},
    "HELIUM": {'description': 'Helium gas as primary coolant', 'annotations': {'chemical_formula': 'He', 'phase': 'gas', 'neutron_absorption': 'very low', 'temperature_capability': 'very high'}},
    "LIQUID_SODIUM": {'description': 'Molten sodium metal as coolant', 'annotations': {'chemical_formula': 'Na', 'phase': 'liquid', 'melting_point': '98°C', 'neutron_absorption': 'low'}},
    "LIQUID_LEAD": {'description': 'Molten lead or lead-bismuth as coolant', 'annotations': {'chemical_formula': 'Pb', 'phase': 'liquid', 'melting_point': '327°C', 'neutron_absorption': 'low'}},
    "MOLTEN_SALT": {'description': 'Molten fluoride or chloride salts', 'annotations': {'phase': 'liquid', 'temperature_capability': 'very high', 'neutron_absorption': 'variable'}},
    "SUPERCRITICAL_WATER": {'description': 'Water above critical point', 'annotations': {'chemical_formula': 'H2O', 'pressure': '>221 bar', 'temperature': '>374°C'}},
}

class ReactorModeratorEnum(RichEnum):
    """
    Neutron moderator types used in nuclear reactors
    """
    # Enum members
    LIGHT_WATER = "LIGHT_WATER"
    HEAVY_WATER = "HEAVY_WATER"
    GRAPHITE = "GRAPHITE"
    BERYLLIUM = "BERYLLIUM"
    NONE = "NONE"

# Set metadata after class creation to avoid it becoming an enum member
ReactorModeratorEnum._metadata = {
    "LIGHT_WATER": {'description': 'Ordinary water as neutron moderator', 'annotations': {'chemical_formula': 'H2O', 'moderation_effectiveness': 'good', 'neutron_absorption': 'moderate'}},
    "HEAVY_WATER": {'description': 'Deuterium oxide as neutron moderator', 'annotations': {'chemical_formula': 'D2O', 'moderation_effectiveness': 'excellent', 'neutron_absorption': 'very low'}},
    "GRAPHITE": {'description': 'Carbon graphite as neutron moderator', 'annotations': {'chemical_formula': 'C', 'moderation_effectiveness': 'good', 'neutron_absorption': 'low', 'temperature_resistance': 'high'}},
    "BERYLLIUM": {'description': 'Beryllium metal as neutron moderator', 'annotations': {'chemical_formula': 'Be', 'moderation_effectiveness': 'good', 'neutron_absorption': 'very low'}},
    "NONE": {'description': 'Fast reactors with no neutron moderation', 'annotations': {'neutron_spectrum': 'fast', 'moderation': 'none'}},
}

class ReactorNeutronSpectrumEnum(RichEnum):
    """
    Neutron energy spectrum classifications
    """
    # Enum members
    THERMAL = "THERMAL"
    EPITHERMAL = "EPITHERMAL"
    FAST = "FAST"

# Set metadata after class creation to avoid it becoming an enum member
ReactorNeutronSpectrumEnum._metadata = {
    "THERMAL": {'description': 'Low energy neutrons in thermal equilibrium', 'annotations': {'energy_range': '<1 eV', 'temperature_equivalent': 'room temperature', 'fission_probability': 'high for U-235'}},
    "EPITHERMAL": {'description': 'Intermediate energy neutrons', 'annotations': {'energy_range': '1 eV - 1 keV', 'temperature_equivalent': 'elevated'}},
    "FAST": {'description': 'High energy neutrons from fission', 'annotations': {'energy_range': '>1 keV', 'moderation': 'minimal or none', 'breeding_capability': 'high'}},
}

class ReactorSizeCategoryEnum(RichEnum):
    """
    Nuclear reactor size classifications
    """
    # Enum members
    LARGE = "LARGE"
    MEDIUM = "MEDIUM"
    SMALL = "SMALL"
    MICRO = "MICRO"
    RESEARCH = "RESEARCH"

# Set metadata after class creation to avoid it becoming an enum member
ReactorSizeCategoryEnum._metadata = {
    "LARGE": {'description': 'Traditional large-scale commercial reactors', 'annotations': {'power_output': '>700 MWe', 'construction': 'custom on-site'}},
    "MEDIUM": {'description': 'Mid-scale reactors', 'annotations': {'power_output': '300-700 MWe', 'construction': 'semi-modular'}},
    "SMALL": {'description': 'Small modular reactors', 'annotations': {'power_output': '50-300 MWe', 'construction': 'modular', 'transport': 'potentially transportable'}},
    "MICRO": {'description': 'Very small reactors for remote applications', 'annotations': {'power_output': '<50 MWe', 'construction': 'factory-built', 'transport': 'transportable'}},
    "RESEARCH": {'description': 'Small reactors for research and isotope production', 'annotations': {'power_output': '<100 MWt', 'primary_use': 'research, isotopes, training'}},
}

class NuclearFuelTypeEnum(RichEnum):
    """
    Types of nuclear fuel materials and compositions
    """
    # Enum members
    NATURAL_URANIUM = "NATURAL_URANIUM"
    LOW_ENRICHED_URANIUM = "LOW_ENRICHED_URANIUM"
    HIGH_ASSAY_LEU = "HIGH_ASSAY_LEU"
    HIGHLY_ENRICHED_URANIUM = "HIGHLY_ENRICHED_URANIUM"
    WEAPONS_GRADE_URANIUM = "WEAPONS_GRADE_URANIUM"
    REACTOR_GRADE_PLUTONIUM = "REACTOR_GRADE_PLUTONIUM"
    WEAPONS_GRADE_PLUTONIUM = "WEAPONS_GRADE_PLUTONIUM"
    MOX_FUEL = "MOX_FUEL"
    THORIUM_FUEL = "THORIUM_FUEL"
    TRISO_FUEL = "TRISO_FUEL"
    LIQUID_FUEL = "LIQUID_FUEL"
    METALLIC_FUEL = "METALLIC_FUEL"
    CARBIDE_FUEL = "CARBIDE_FUEL"
    NITRIDE_FUEL = "NITRIDE_FUEL"

# Set metadata after class creation to avoid it becoming an enum member
NuclearFuelTypeEnum._metadata = {
    "NATURAL_URANIUM": {'description': 'Uranium as found in nature (0.711% U-235)', 'meaning': 'CHEBI:27214', 'annotations': {'u235_content': '0.711%', 'u238_content': '99.289%', 'enrichment_required': False, 'typical_use': 'PHWR, some research reactors'}, 'aliases': ['Natural U', 'Unat', 'uranium atom']},
    "LOW_ENRICHED_URANIUM": {'description': 'Uranium enriched to 0.7%-20% U-235', 'annotations': {'u235_content': '0.7-20%', 'proliferation_risk': 'low', 'typical_use': 'commercial power reactors', 'iaea_category': 'indirect use material'}, 'aliases': ['LEU']},
    "HIGH_ASSAY_LEU": {'description': 'Uranium enriched to 5%-20% U-235', 'annotations': {'u235_content': '5-20%', 'typical_use': 'advanced reactors, SMRs', 'proliferation_risk': 'moderate'}, 'aliases': ['HALEU', 'LEU+']},
    "HIGHLY_ENRICHED_URANIUM": {'description': 'Uranium enriched to 20% or more U-235', 'annotations': {'u235_content': '≥20%', 'proliferation_risk': 'high', 'typical_use': 'research reactors, naval propulsion', 'iaea_category': 'direct use material'}, 'aliases': ['HEU']},
    "WEAPONS_GRADE_URANIUM": {'description': 'Uranium enriched to 90% or more U-235', 'annotations': {'u235_content': '≥90%', 'proliferation_risk': 'very high', 'typical_use': 'nuclear weapons, some naval reactors'}, 'aliases': ['WGU']},
    "REACTOR_GRADE_PLUTONIUM": {'description': 'Plutonium with high Pu-240 content from spent fuel', 'annotations': {'pu239_content': '<93%', 'pu240_content': '>7%', 'source': 'spent nuclear fuel', 'typical_use': 'MOX fuel'}, 'aliases': ['RGPu']},
    "WEAPONS_GRADE_PLUTONIUM": {'description': 'Plutonium with low Pu-240 content', 'annotations': {'pu239_content': '≥93%', 'pu240_content': '<7%', 'proliferation_risk': 'very high'}, 'aliases': ['WGPu']},
    "MOX_FUEL": {'description': 'Mixture of plutonium and uranium oxides', 'annotations': {'composition': 'UO2 + PuO2', 'plutonium_content': '3-10%', 'typical_use': 'thermal reactors', 'recycling': 'enables plutonium recycling'}, 'aliases': ['MOX', 'Mixed Oxide']},
    "THORIUM_FUEL": {'description': 'Fuel containing thorium-232 as fertile material', 'meaning': 'CHEBI:33385', 'annotations': {'fertile_isotope': 'Th-232', 'fissile_product': 'U-233', 'abundance': 'more abundant than uranium', 'proliferation_resistance': 'high'}, 'aliases': ['Thorium fuel', 'thorium']},
    "TRISO_FUEL": {'description': 'Coated particle fuel with multiple containment layers', 'annotations': {'form': 'coated particles', 'containment_layers': 4, 'meltdown_resistance': 'very high', 'typical_use': 'HTGR, some SMRs'}, 'aliases': ['TRISO']},
    "LIQUID_FUEL": {'description': 'Fuel dissolved in liquid medium', 'annotations': {'phase': 'liquid', 'typical_use': 'molten salt reactors', 'reprocessing': 'online'}},
    "METALLIC_FUEL": {'description': 'Fuel in metallic form', 'annotations': {'form': 'metal alloy', 'typical_use': 'fast reactors', 'thermal_conductivity': 'high'}},
    "CARBIDE_FUEL": {'description': 'Uranium or plutonium carbide fuel', 'annotations': {'chemical_form': 'carbide', 'melting_point': 'very high', 'typical_use': 'advanced reactors'}},
    "NITRIDE_FUEL": {'description': 'Uranium or plutonium nitride fuel', 'annotations': {'chemical_form': 'nitride', 'density': 'high', 'typical_use': 'fast reactors'}},
}

class UraniumEnrichmentLevelEnum(RichEnum):
    """
    Standard uranium-235 enrichment level classifications
    """
    # Enum members
    NATURAL = "NATURAL"
    SLIGHTLY_ENRICHED = "SLIGHTLY_ENRICHED"
    LOW_ENRICHED = "LOW_ENRICHED"
    HIGH_ASSAY_LOW_ENRICHED = "HIGH_ASSAY_LOW_ENRICHED"
    HIGHLY_ENRICHED = "HIGHLY_ENRICHED"
    WEAPONS_GRADE = "WEAPONS_GRADE"

# Set metadata after class creation to avoid it becoming an enum member
UraniumEnrichmentLevelEnum._metadata = {
    "NATURAL": {'description': 'Natural uranium enrichment (0.711% U-235)', 'annotations': {'u235_percentage': 0.711, 'category': 'natural', 'separative_work': 0}},
    "SLIGHTLY_ENRICHED": {'description': 'Minimal enrichment above natural levels', 'annotations': {'u235_percentage': '0.8-2.0', 'category': 'SEU', 'typical_use': 'some heavy water reactors'}},
    "LOW_ENRICHED": {'description': 'Standard commercial reactor enrichment', 'annotations': {'u235_percentage': '2.0-5.0', 'category': 'LEU', 'typical_use': 'PWR, BWR commercial reactors'}},
    "HIGH_ASSAY_LOW_ENRICHED": {'description': 'Higher enrichment for advanced reactors', 'annotations': {'u235_percentage': '5.0-20.0', 'category': 'HALEU', 'typical_use': 'advanced reactors, SMRs'}},
    "HIGHLY_ENRICHED": {'description': 'High enrichment for research and naval reactors', 'annotations': {'u235_percentage': '20.0-90.0', 'category': 'HEU', 'typical_use': 'research reactors, naval propulsion'}},
    "WEAPONS_GRADE": {'description': 'Very high enrichment for weapons', 'annotations': {'u235_percentage': '90.0+', 'category': 'WGU', 'proliferation_concern': 'extreme'}},
}

class FuelFormEnum(RichEnum):
    """
    Physical forms of nuclear fuel
    """
    # Enum members
    OXIDE_PELLETS = "OXIDE_PELLETS"
    METAL_SLUGS = "METAL_SLUGS"
    COATED_PARTICLES = "COATED_PARTICLES"
    LIQUID_SOLUTION = "LIQUID_SOLUTION"
    DISPERSION_FUEL = "DISPERSION_FUEL"
    CERMET_FUEL = "CERMET_FUEL"
    PLATE_FUEL = "PLATE_FUEL"
    ROD_FUEL = "ROD_FUEL"

# Set metadata after class creation to avoid it becoming an enum member
FuelFormEnum._metadata = {
    "OXIDE_PELLETS": {'description': 'Ceramic uranium dioxide pellets', 'annotations': {'chemical_form': 'UO2', 'shape': 'cylindrical pellets', 'typical_use': 'PWR, BWR fuel rods'}},
    "METAL_SLUGS": {'description': 'Metallic uranium fuel elements', 'annotations': {'chemical_form': 'metallic uranium', 'shape': 'cylindrical slugs', 'typical_use': 'production reactors'}},
    "COATED_PARTICLES": {'description': 'Microspheres with protective coatings', 'annotations': {'structure': 'TRISO or BISO coated', 'size': 'microscopic spheres', 'typical_use': 'HTGR'}},
    "LIQUID_SOLUTION": {'description': 'Fuel dissolved in liquid carrier', 'annotations': {'phase': 'liquid', 'typical_use': 'molten salt reactors'}},
    "DISPERSION_FUEL": {'description': 'Fuel particles dispersed in matrix', 'annotations': {'structure': 'particles in matrix', 'typical_use': 'research reactors'}},
    "CERMET_FUEL": {'description': 'Ceramic-metal composite fuel', 'annotations': {'structure': 'ceramic in metal matrix', 'typical_use': 'advanced reactors'}},
    "PLATE_FUEL": {'description': 'Flat plate fuel elements', 'annotations': {'geometry': 'flat plates', 'typical_use': 'research reactors'}},
    "ROD_FUEL": {'description': 'Cylindrical fuel rods', 'annotations': {'geometry': 'long cylinders', 'typical_use': 'commercial power reactors'}},
}

class FuelAssemblyTypeEnum(RichEnum):
    """
    Types of fuel assembly configurations
    """
    # Enum members
    PWR_ASSEMBLY = "PWR_ASSEMBLY"
    BWR_ASSEMBLY = "BWR_ASSEMBLY"
    CANDU_BUNDLE = "CANDU_BUNDLE"
    RBMK_ASSEMBLY = "RBMK_ASSEMBLY"
    AGR_ASSEMBLY = "AGR_ASSEMBLY"
    HTGR_BLOCK = "HTGR_BLOCK"
    FAST_REACTOR_ASSEMBLY = "FAST_REACTOR_ASSEMBLY"

# Set metadata after class creation to avoid it becoming an enum member
FuelAssemblyTypeEnum._metadata = {
    "PWR_ASSEMBLY": {'description': 'Square array fuel assembly for PWR', 'annotations': {'geometry': 'square array', 'rod_count': '264-289 typical', 'control_method': 'control rod clusters'}},
    "BWR_ASSEMBLY": {'description': 'Square array fuel assembly for BWR', 'annotations': {'geometry': 'square array with channel', 'rod_count': '49-100 typical', 'control_method': 'control blades'}},
    "CANDU_BUNDLE": {'description': 'Cylindrical fuel bundle for PHWR', 'annotations': {'geometry': 'cylindrical bundle', 'rod_count': '28-43 typical', 'length': '~50 cm'}},
    "RBMK_ASSEMBLY": {'description': 'Fuel assembly for RBMK reactors', 'annotations': {'geometry': '18-rod bundle', 'length': '~3.5 m', 'control_method': 'control rods'}},
    "AGR_ASSEMBLY": {'description': 'Fuel stringer for AGR', 'annotations': {'geometry': 'stacked pins', 'cladding': 'stainless steel'}},
    "HTGR_BLOCK": {'description': 'Graphite block with TRISO fuel', 'annotations': {'geometry': 'hexagonal or cylindrical blocks', 'fuel_form': 'TRISO particles'}},
    "FAST_REACTOR_ASSEMBLY": {'description': 'Fuel assembly for fast reactors', 'annotations': {'geometry': 'hexagonal wrapper', 'coolant_flow': 'axial'}},
}

class FuelCycleStageEnum(RichEnum):
    """
    Stages in the nuclear fuel cycle
    """
    # Enum members
    MINING = "MINING"
    CONVERSION = "CONVERSION"
    ENRICHMENT = "ENRICHMENT"
    FUEL_FABRICATION = "FUEL_FABRICATION"
    REACTOR_OPERATION = "REACTOR_OPERATION"
    INTERIM_STORAGE = "INTERIM_STORAGE"
    REPROCESSING = "REPROCESSING"
    DISPOSAL = "DISPOSAL"

# Set metadata after class creation to avoid it becoming an enum member
FuelCycleStageEnum._metadata = {
    "MINING": {'description': 'Extraction of uranium ore from deposits', 'annotations': {'process': 'mining and milling', 'product': 'uranium ore concentrate (yellowcake)'}},
    "CONVERSION": {'description': 'Conversion of uranium concentrate to UF6', 'annotations': {'input': 'U3O8 yellowcake', 'output': 'uranium hexafluoride (UF6)'}},
    "ENRICHMENT": {'description': 'Increase of U-235 concentration', 'annotations': {'input': 'natural UF6', 'output': 'enriched UF6', 'waste': 'depleted uranium tails'}},
    "FUEL_FABRICATION": {'description': 'Manufacturing of fuel assemblies', 'annotations': {'input': 'enriched UF6', 'output': 'fuel assemblies', 'process': 'pellet and rod manufacturing'}},
    "REACTOR_OPERATION": {'description': 'Power generation in nuclear reactor', 'annotations': {'input': 'fresh fuel assemblies', 'output': 'electricity and spent fuel', 'duration': '12-24 months per cycle'}},
    "INTERIM_STORAGE": {'description': 'Temporary storage of spent fuel', 'annotations': {'purpose': 'cooling and decay', 'duration': '5-40+ years', 'location': 'reactor pools or dry casks'}},
    "REPROCESSING": {'description': 'Chemical separation of spent fuel components', 'annotations': {'input': 'spent nuclear fuel', 'output': 'uranium, plutonium, waste', 'status': 'practiced in some countries'}},
    "DISPOSAL": {'description': 'Permanent disposal of nuclear waste', 'annotations': {'method': 'geological repository', 'duration': 'permanent', 'status': 'under development globally'}},
}

class FissileIsotopeEnum(RichEnum):
    """
    Fissile isotopes used in nuclear fuel
    """
    # Enum members
    URANIUM_233 = "URANIUM_233"
    URANIUM_235 = "URANIUM_235"
    PLUTONIUM_239 = "PLUTONIUM_239"
    PLUTONIUM_241 = "PLUTONIUM_241"

# Set metadata after class creation to avoid it becoming an enum member
FissileIsotopeEnum._metadata = {
    "URANIUM_233": {'description': 'Fissile isotope produced from thorium', 'annotations': {'mass_number': 233, 'half_life': '159,200 years', 'thermal_fission': True, 'breeding_from': 'Th-232'}, 'aliases': ['U-233']},
    "URANIUM_235": {'description': 'Naturally occurring fissile uranium isotope', 'annotations': {'mass_number': 235, 'half_life': '703,800,000 years', 'natural_abundance': '0.711%', 'thermal_fission': True}, 'aliases': ['U-235']},
    "PLUTONIUM_239": {'description': 'Fissile plutonium isotope from U-238 breeding', 'annotations': {'mass_number': 239, 'half_life': '24,110 years', 'thermal_fission': True, 'breeding_from': 'U-238'}, 'aliases': ['Pu-239']},
    "PLUTONIUM_241": {'description': 'Fissile plutonium isotope with short half-life', 'annotations': {'mass_number': 241, 'half_life': '14.3 years', 'thermal_fission': True, 'decay_product': 'Am-241'}, 'aliases': ['Pu-241']},
}

class IAEAWasteClassificationEnum(RichEnum):
    """
    IAEA General Safety Requirements radioactive waste classification scheme
    """
    # Enum members
    EXEMPT_WASTE = "EXEMPT_WASTE"
    VERY_SHORT_LIVED_WASTE = "VERY_SHORT_LIVED_WASTE"
    VERY_LOW_LEVEL_WASTE = "VERY_LOW_LEVEL_WASTE"
    LOW_LEVEL_WASTE = "LOW_LEVEL_WASTE"
    INTERMEDIATE_LEVEL_WASTE = "INTERMEDIATE_LEVEL_WASTE"
    HIGH_LEVEL_WASTE = "HIGH_LEVEL_WASTE"

# Set metadata after class creation to avoid it becoming an enum member
IAEAWasteClassificationEnum._metadata = {
    "EXEMPT_WASTE": {'description': 'Waste with negligible radioactivity requiring no regulatory control', 'annotations': {'regulatory_control': 'none required', 'clearance': 'can be cleared from regulatory control', 'disposal': 'as ordinary waste', 'activity_level': 'negligible'}, 'aliases': ['EW']},
    "VERY_SHORT_LIVED_WASTE": {'description': 'Waste stored for decay to exempt levels within few years', 'annotations': {'storage_period': 'up to few years', 'decay_strategy': 'storage for decay', 'clearance': 'after decay period', 'typical_sources': 'medical, research isotopes'}, 'aliases': ['VSLW']},
    "VERY_LOW_LEVEL_WASTE": {'description': 'Waste requiring limited containment and isolation', 'annotations': {'containment_requirement': 'limited', 'disposal': 'near-surface landfill-type', 'activity_level': 'very low but above exempt', 'isolation_period': 'limited'}, 'aliases': ['VLLW']},
    "LOW_LEVEL_WASTE": {'description': 'Waste requiring containment for up to hundreds of years', 'annotations': {'containment_period': 'up to few hundred years', 'disposal': 'near-surface disposal', 'activity_level': 'low', 'heat_generation': 'negligible'}, 'aliases': ['LLW']},
    "INTERMEDIATE_LEVEL_WASTE": {'description': 'Waste requiring containment for thousands of years', 'annotations': {'containment_period': 'up to thousands of years', 'disposal': 'geological disposal', 'activity_level': 'intermediate', 'heat_generation': 'low (<2 kW/m³)', 'shielding': 'required'}, 'aliases': ['ILW']},
    "HIGH_LEVEL_WASTE": {'description': 'Waste requiring containment for thousands to hundreds of thousands of years', 'annotations': {'containment_period': 'thousands to hundreds of thousands of years', 'disposal': 'geological disposal', 'activity_level': 'high', 'heat_generation': 'significant (>2 kW/m³)', 'cooling': 'required', 'shielding': 'heavy shielding required'}, 'aliases': ['HLW']},
}

class NRCWasteClassEnum(RichEnum):
    """
    US NRC 10 CFR 61 low-level radioactive waste classification
    """
    # Enum members
    CLASS_A = "CLASS_A"
    CLASS_B = "CLASS_B"
    CLASS_C = "CLASS_C"
    GREATER_THAN_CLASS_C = "GREATER_THAN_CLASS_C"

# Set metadata after class creation to avoid it becoming an enum member
NRCWasteClassEnum._metadata = {
    "CLASS_A": {'description': 'Lowest radioactivity waste suitable for shallow land burial', 'annotations': {'disposal_method': 'shallow land burial', 'segregation_requirements': 'minimal', 'waste_form_requirements': 'none', 'typical_sources': 'medical, industrial, power plants', 'concentration_limits': 'lowest of three classes'}},
    "CLASS_B": {'description': 'Intermediate radioactivity requiring waste form stability', 'annotations': {'disposal_method': 'shallow land burial', 'segregation_requirements': 'from Class A', 'waste_form_requirements': 'structural stability', 'institutional_control': '100 years minimum', 'concentration_limits': 'intermediate'}},
    "CLASS_C": {'description': 'Highest concentration suitable for shallow land burial', 'annotations': {'disposal_method': 'shallow land burial', 'segregation_requirements': 'enhanced', 'waste_form_requirements': 'structural stability', 'institutional_control': '100 years minimum', 'intruder_barriers': 'required', 'concentration_limits': 'highest for shallow burial'}},
    "GREATER_THAN_CLASS_C": {'description': 'Waste exceeding Class C limits, generally unsuitable for shallow burial', 'annotations': {'disposal_method': 'case-by-case evaluation', 'shallow_burial': 'generally not acceptable', 'deep_disposal': 'may be required', 'nrc_evaluation': 'required', 'concentration_limits': 'exceeds Class C'}, 'aliases': ['GTCC']},
}

class WasteHeatGenerationEnum(RichEnum):
    """
    Heat generation categories for radioactive waste
    """
    # Enum members
    NEGLIGIBLE_HEAT = "NEGLIGIBLE_HEAT"
    LOW_HEAT = "LOW_HEAT"
    HIGH_HEAT = "HIGH_HEAT"

# Set metadata after class creation to avoid it becoming an enum member
WasteHeatGenerationEnum._metadata = {
    "NEGLIGIBLE_HEAT": {'description': 'Waste generating negligible heat', 'annotations': {'heat_output': '<0.1 kW/m³', 'cooling_required': False, 'thermal_consideration': 'minimal'}},
    "LOW_HEAT": {'description': 'Waste generating low but measurable heat', 'annotations': {'heat_output': '0.1-2 kW/m³', 'cooling_required': 'minimal', 'thermal_consideration': 'some design consideration'}},
    "HIGH_HEAT": {'description': 'Waste generating significant heat requiring thermal management', 'annotations': {'heat_output': '>2 kW/m³', 'cooling_required': True, 'thermal_consideration': 'major design factor', 'typical_waste': 'spent nuclear fuel, HLW glass'}},
}

class WasteHalfLifeCategoryEnum(RichEnum):
    """
    Half-life categories for radioactive waste classification
    """
    # Enum members
    VERY_SHORT_LIVED = "VERY_SHORT_LIVED"
    SHORT_LIVED = "SHORT_LIVED"
    LONG_LIVED = "LONG_LIVED"

# Set metadata after class creation to avoid it becoming an enum member
WasteHalfLifeCategoryEnum._metadata = {
    "VERY_SHORT_LIVED": {'description': 'Radionuclides with very short half-lives', 'annotations': {'half_life_range': 'seconds to days', 'decay_strategy': 'storage for decay', 'typical_examples': 'medical isotopes, some activation products'}},
    "SHORT_LIVED": {'description': 'Radionuclides with short half-lives', 'annotations': {'half_life_range': '<30 years', 'containment_period': 'hundreds of years', 'decay_significance': 'significant over containment period'}},
    "LONG_LIVED": {'description': 'Radionuclides with long half-lives', 'annotations': {'half_life_range': '>30 years', 'containment_period': 'thousands to millions of years', 'decay_significance': 'minimal over human timescales', 'examples': 'actinides, some fission products'}},
}

class WasteDisposalMethodEnum(RichEnum):
    """
    Methods for radioactive waste disposal
    """
    # Enum members
    CLEARANCE = "CLEARANCE"
    DECAY_STORAGE = "DECAY_STORAGE"
    NEAR_SURFACE_DISPOSAL = "NEAR_SURFACE_DISPOSAL"
    GEOLOGICAL_DISPOSAL = "GEOLOGICAL_DISPOSAL"
    BOREHOLE_DISPOSAL = "BOREHOLE_DISPOSAL"
    TRANSMUTATION = "TRANSMUTATION"

# Set metadata after class creation to avoid it becoming an enum member
WasteDisposalMethodEnum._metadata = {
    "CLEARANCE": {'description': 'Release from regulatory control as ordinary waste', 'annotations': {'regulatory_oversight': 'none after clearance', 'waste_category': 'exempt waste', 'disposal_location': 'conventional facilities'}},
    "DECAY_STORAGE": {'description': 'Storage for radioactive decay to exempt levels', 'annotations': {'storage_duration': 'typically <10 years', 'waste_category': 'very short-lived waste', 'final_disposal': 'as ordinary waste after decay'}},
    "NEAR_SURFACE_DISPOSAL": {'description': 'Disposal in engineered near-surface facilities', 'annotations': {'depth': 'typically <30 meters', 'waste_categories': 'VLLW, LLW, some ILW', 'institutional_control': '100-300 years', 'barriers': 'engineered barriers'}},
    "GEOLOGICAL_DISPOSAL": {'description': 'Deep underground disposal in stable geological formations', 'annotations': {'depth': 'typically >300 meters', 'waste_categories': 'HLW, long-lived ILW, spent fuel', 'containment_period': 'thousands to millions of years', 'barriers': 'multiple barriers including geology'}},
    "BOREHOLE_DISPOSAL": {'description': 'Disposal in deep boreholes', 'annotations': {'depth': '1-5 kilometers', 'waste_categories': 'disused sealed sources, some HLW', 'isolation': 'extreme depth isolation'}},
    "TRANSMUTATION": {'description': 'Nuclear transformation to shorter-lived or stable isotopes', 'annotations': {'method': 'accelerator-driven systems or fast reactors', 'waste_categories': 'long-lived actinides', 'status': 'research and development'}},
}

class WasteSourceEnum(RichEnum):
    """
    Sources of radioactive waste generation
    """
    # Enum members
    NUCLEAR_POWER_PLANTS = "NUCLEAR_POWER_PLANTS"
    MEDICAL_APPLICATIONS = "MEDICAL_APPLICATIONS"
    INDUSTRIAL_APPLICATIONS = "INDUSTRIAL_APPLICATIONS"
    RESEARCH_FACILITIES = "RESEARCH_FACILITIES"
    NUCLEAR_WEAPONS_PROGRAM = "NUCLEAR_WEAPONS_PROGRAM"
    DECOMMISSIONING = "DECOMMISSIONING"
    URANIUM_MINING = "URANIUM_MINING"
    FUEL_CYCLE_FACILITIES = "FUEL_CYCLE_FACILITIES"

# Set metadata after class creation to avoid it becoming an enum member
WasteSourceEnum._metadata = {
    "NUCLEAR_POWER_PLANTS": {'description': 'Waste from commercial nuclear power generation', 'annotations': {'waste_types': 'spent fuel, operational waste, decommissioning waste', 'volume_fraction': 'largest single source', 'waste_classes': 'all classes including HLW'}},
    "MEDICAL_APPLICATIONS": {'description': 'Waste from nuclear medicine and radiotherapy', 'annotations': {'waste_types': 'short-lived medical isotopes, sealed sources', 'typical_classification': 'Class A, VSLW', 'decay_strategy': 'often storage for decay'}},
    "INDUSTRIAL_APPLICATIONS": {'description': 'Waste from industrial use of radioactive materials', 'annotations': {'applications': 'gauging, radiography, sterilization', 'waste_types': 'sealed sources, contaminated equipment', 'typical_classification': 'Class A and B'}},
    "RESEARCH_FACILITIES": {'description': 'Waste from research reactors and laboratories', 'annotations': {'waste_types': 'activation products, contaminated materials', 'typical_classification': 'Class A, B, and C', 'fuel_type': 'often HEU spent fuel'}},
    "NUCLEAR_WEAPONS_PROGRAM": {'description': 'Waste from defense nuclear activities', 'annotations': {'waste_types': 'TRU waste, HLW, contaminated equipment', 'legacy_waste': 'significant volumes from past activities', 'classification': 'all classes including TRU'}},
    "DECOMMISSIONING": {'description': 'Waste from dismantling nuclear facilities', 'annotations': {'waste_types': 'activated concrete, contaminated metal', 'volume': 'large volumes of VLLW and LLW', 'activity_level': 'generally low level'}},
    "URANIUM_MINING": {'description': 'Waste from uranium extraction and processing', 'annotations': {'waste_types': 'tailings, contaminated equipment', 'volume': 'very large volumes', 'activity_level': 'naturally occurring radioactivity'}},
    "FUEL_CYCLE_FACILITIES": {'description': 'Waste from fuel fabrication, enrichment, and reprocessing', 'annotations': {'waste_types': 'contaminated equipment, process waste', 'classification': 'variable depending on process', 'uranium_content': 'often contains enriched uranium'}},
}

class TransuranicWasteCategoryEnum(RichEnum):
    """
    Transuranic waste classifications (US system)
    """
    # Enum members
    CONTACT_HANDLED_TRU = "CONTACT_HANDLED_TRU"
    REMOTE_HANDLED_TRU = "REMOTE_HANDLED_TRU"
    TRU_MIXED_WASTE = "TRU_MIXED_WASTE"

# Set metadata after class creation to avoid it becoming an enum member
TransuranicWasteCategoryEnum._metadata = {
    "CONTACT_HANDLED_TRU": {'description': 'TRU waste with surface dose rate ≤200 mrem/hr', 'annotations': {'dose_rate': '≤200 mrem/hr at surface', 'handling': 'direct contact possible with protection', 'disposal': 'geological repository (WIPP)', 'plutonium_content': '>100 nCi/g'}, 'aliases': ['CH-TRU']},
    "REMOTE_HANDLED_TRU": {'description': 'TRU waste with surface dose rate >200 mrem/hr', 'annotations': {'dose_rate': '>200 mrem/hr at surface', 'handling': 'remote handling required', 'disposal': 'geological repository with additional shielding', 'plutonium_content': '>100 nCi/g'}, 'aliases': ['RH-TRU']},
    "TRU_MIXED_WASTE": {'description': 'TRU waste also containing hazardous chemical components', 'annotations': {'regulation': 'both radiological and chemical hazard regulations', 'treatment': 'may require chemical treatment before disposal', 'disposal': 'geological repository after treatment', 'complexity': 'dual regulatory framework'}},
}

class INESLevelEnum(RichEnum):
    """
    International Nuclear and Radiological Event Scale (INES) levels
    """
    # Enum members
    LEVEL_0 = "LEVEL_0"
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
    LEVEL_4 = "LEVEL_4"
    LEVEL_5 = "LEVEL_5"
    LEVEL_6 = "LEVEL_6"
    LEVEL_7 = "LEVEL_7"

# Set metadata after class creation to avoid it becoming an enum member
INESLevelEnum._metadata = {
    "LEVEL_0": {'description': 'Events without safety significance', 'annotations': {'scale_position': 'below scale', 'safety_significance': 'no safety significance', 'public_impact': 'none', 'examples': 'minor technical issues'}},
    "LEVEL_1": {'description': 'Anomaly beyond authorized operating regime', 'annotations': {'scale_position': 'incidents', 'safety_significance': 'minor', 'public_impact': 'none', 'examples': 'minor contamination, minor safety system failure'}},
    "LEVEL_2": {'description': 'Incident with significant defenses remaining', 'annotations': {'scale_position': 'incidents', 'safety_significance': 'minor', 'public_impact': 'none', 'radiation_dose': '<10 mSv to workers'}},
    "LEVEL_3": {'description': 'Serious incident with some defense degradation', 'annotations': {'scale_position': 'incidents', 'safety_significance': 'minor', 'public_impact': 'very minor', 'radiation_dose': '<100 mSv to workers', 'examples': 'near accident, serious contamination'}},
    "LEVEL_4": {'description': 'Accident with minor off-site releases', 'annotations': {'scale_position': 'accidents', 'safety_significance': 'moderate', 'public_impact': 'minor local impact', 'evacuation': 'not required', 'examples': 'partial core damage'}},
    "LEVEL_5": {'description': 'Accident with limited off-site releases', 'annotations': {'scale_position': 'accidents', 'safety_significance': 'moderate to major', 'public_impact': 'limited wider impact', 'protective_actions': 'limited evacuation', 'examples': 'Three Mile Island (1979)'}},
    "LEVEL_6": {'description': 'Serious accident with significant releases', 'annotations': {'scale_position': 'accidents', 'safety_significance': 'major', 'public_impact': 'significant', 'protective_actions': 'extensive evacuation and countermeasures'}},
    "LEVEL_7": {'description': 'Major accident with widespread health and environmental effects', 'annotations': {'scale_position': 'accidents', 'safety_significance': 'major', 'public_impact': 'widespread', 'examples': 'Chernobyl (1986), Fukushima (2011)', 'consequences': 'long-term environmental contamination'}},
}

class EmergencyClassificationEnum(RichEnum):
    """
    Nuclear emergency action levels and classifications
    """
    # Enum members
    NOTIFICATION_UNUSUAL_EVENT = "NOTIFICATION_UNUSUAL_EVENT"
    ALERT = "ALERT"
    SITE_AREA_EMERGENCY = "SITE_AREA_EMERGENCY"
    GENERAL_EMERGENCY = "GENERAL_EMERGENCY"

# Set metadata after class creation to avoid it becoming an enum member
EmergencyClassificationEnum._metadata = {
    "NOTIFICATION_UNUSUAL_EVENT": {'description': 'Events that are in process or have occurred which indicate potential degradation', 'annotations': {'severity': 'lowest emergency level', 'off_site_response': 'notification only', 'public_protective_actions': 'none required', 'emergency_response': 'minimal activation'}, 'aliases': ['NOUE', 'Unusual Event']},
    "ALERT": {'description': 'Events involving actual or potential substantial degradation of plant safety', 'annotations': {'severity': 'second emergency level', 'off_site_response': 'notification and standby', 'public_protective_actions': 'none required, but preparation', 'emergency_response': 'partial activation', 'plant_status': 'substantial safety degradation possible'}},
    "SITE_AREA_EMERGENCY": {'description': 'Events with actual or likely major failures of plant protective systems', 'annotations': {'severity': 'third emergency level', 'off_site_response': 'offsite centers activated', 'public_protective_actions': 'may be required near site', 'emergency_response': 'full activation', 'plant_status': 'major plant safety systems failure'}, 'aliases': ['SAE']},
    "GENERAL_EMERGENCY": {'description': 'Events involving actual or imminent substantial core degradation', 'annotations': {'severity': 'highest emergency level', 'off_site_response': 'full activation', 'public_protective_actions': 'implementation likely', 'emergency_response': 'maximum response', 'plant_status': 'core degradation or containment failure'}},
}

class NuclearSecurityCategoryEnum(RichEnum):
    """
    IAEA nuclear material security categories (INFCIRC/225)
    """
    # Enum members
    CATEGORY_I = "CATEGORY_I"
    CATEGORY_II = "CATEGORY_II"
    CATEGORY_III = "CATEGORY_III"
    CATEGORY_IV = "CATEGORY_IV"

# Set metadata after class creation to avoid it becoming an enum member
NuclearSecurityCategoryEnum._metadata = {
    "CATEGORY_I": {'description': 'Material that can be used directly to manufacture nuclear explosive devices', 'annotations': {'direct_use': True, 'proliferation_risk': 'highest', 'protection_requirements': 'maximum', 'examples': 'HEU ≥20%, Pu ≥2kg, U-233 ≥2kg', 'physical_protection': 'multiple independent physical barriers'}},
    "CATEGORY_II": {'description': 'Material requiring further processing to manufacture nuclear explosive devices', 'annotations': {'direct_use': 'requires processing', 'proliferation_risk': 'moderate', 'protection_requirements': 'substantial', 'examples': 'HEU <20% but >5%, natural uranium >500kg', 'physical_protection': 'significant barriers required'}},
    "CATEGORY_III": {'description': 'Material posing radiation hazard but minimal proliferation risk', 'annotations': {'direct_use': False, 'proliferation_risk': 'low', 'protection_requirements': 'basic', 'examples': 'natural uranium 10-500kg, depleted uranium', 'physical_protection': 'basic measures sufficient'}},
    "CATEGORY_IV": {'description': 'Material with minimal security significance', 'annotations': {'direct_use': False, 'proliferation_risk': 'minimal', 'protection_requirements': 'administrative', 'examples': 'small quantities of natural uranium'}},
}

class SafetySystemClassEnum(RichEnum):
    """
    Nuclear safety system classifications (based on IEEE and ASME standards)
    """
    # Enum members
    CLASS_1E = "CLASS_1E"
    SAFETY_RELATED = "SAFETY_RELATED"
    SAFETY_SIGNIFICANT = "SAFETY_SIGNIFICANT"
    NON_SAFETY_RELATED = "NON_SAFETY_RELATED"

# Set metadata after class creation to avoid it becoming an enum member
SafetySystemClassEnum._metadata = {
    "CLASS_1E": {'description': 'Safety systems essential to emergency reactor shutdown and core cooling', 'annotations': {'safety_function': 'essential to safety', 'redundancy': 'required', 'independence': 'required', 'power_supply': 'independent emergency power', 'seismic_qualification': 'required', 'examples': 'reactor protection system, emergency core cooling'}},
    "SAFETY_RELATED": {'description': 'Systems important to safety but not classified as Class 1E', 'annotations': {'safety_function': 'important to safety', 'quality_requirements': 'enhanced', 'testing_requirements': 'extensive', 'examples': 'some support systems, barriers'}},
    "SAFETY_SIGNIFICANT": {'description': 'Systems with risk significance but not safety-related', 'annotations': {'safety_function': 'risk-significant', 'quality_requirements': 'graded approach', 'risk_informed': 'classification based on risk assessment'}},
    "NON_SAFETY_RELATED": {'description': 'Systems not required for nuclear safety functions', 'annotations': {'safety_function': 'not required for safety', 'quality_requirements': 'commercial standards', 'failure_impact': 'minimal safety impact'}},
}

class ReactorSafetyFunctionEnum(RichEnum):
    """
    Fundamental nuclear reactor safety functions
    """
    # Enum members
    REACTIVITY_CONTROL = "REACTIVITY_CONTROL"
    HEAT_REMOVAL = "HEAT_REMOVAL"
    CONTAINMENT_INTEGRITY = "CONTAINMENT_INTEGRITY"
    CORE_COOLING = "CORE_COOLING"
    SHUTDOWN_CAPABILITY = "SHUTDOWN_CAPABILITY"

# Set metadata after class creation to avoid it becoming an enum member
ReactorSafetyFunctionEnum._metadata = {
    "REACTIVITY_CONTROL": {'description': 'Control of nuclear chain reaction', 'annotations': {'function': 'maintain reactor subcritical when required', 'systems': 'control rods, neutron absorbers', 'failure_consequence': 'criticality accident', 'defense_category': 'prevent accidents'}},
    "HEAT_REMOVAL": {'description': 'Removal of decay heat from reactor core', 'annotations': {'function': 'prevent fuel overheating', 'systems': 'cooling systems, heat exchangers', 'failure_consequence': 'core damage, meltdown', 'defense_category': 'mitigate consequences'}},
    "CONTAINMENT_INTEGRITY": {'description': 'Confinement of radioactive materials', 'annotations': {'function': 'prevent radioactive release', 'systems': 'containment structure, isolation systems', 'failure_consequence': 'environmental contamination', 'defense_category': 'mitigate consequences'}},
    "CORE_COOLING": {'description': 'Maintenance of adequate core cooling', 'annotations': {'function': 'prevent fuel damage', 'systems': 'primary cooling, emergency cooling', 'failure_consequence': 'fuel damage', 'time_sensitivity': 'immediate to long-term'}},
    "SHUTDOWN_CAPABILITY": {'description': 'Ability to shut down and maintain shutdown', 'annotations': {'function': 'terminate power operation safely', 'systems': 'control systems, shutdown systems', 'time_requirement': 'rapid response capability'}},
}

class DefenseInDepthLevelEnum(RichEnum):
    """
    Defense in depth barrier levels for nuclear safety
    """
    # Enum members
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
    LEVEL_4 = "LEVEL_4"
    LEVEL_5 = "LEVEL_5"

# Set metadata after class creation to avoid it becoming an enum member
DefenseInDepthLevelEnum._metadata = {
    "LEVEL_1": {'description': 'Conservative design and high quality in construction and operation', 'annotations': {'objective': 'prevent deviations from normal operation', 'approach': 'conservative design, quality assurance', 'examples': 'design margins, quality construction'}},
    "LEVEL_2": {'description': 'Control of abnormal operation and detection of failures', 'annotations': {'objective': 'control abnormal operation and failures', 'approach': 'control systems, protection systems', 'examples': 'reactor protection systems, safety systems'}},
    "LEVEL_3": {'description': 'Control of accidents to prevent progression to severe conditions', 'annotations': {'objective': 'control design basis accidents', 'approach': 'engineered safety features', 'examples': 'emergency core cooling, containment systems'}},
    "LEVEL_4": {'description': 'Control of severe accidents including prevention of core melt progression', 'annotations': {'objective': 'control severe accidents', 'approach': 'severe accident management', 'examples': 'cavity flooding, filtered venting'}},
    "LEVEL_5": {'description': 'Mitigation of off-site radiological consequences', 'annotations': {'objective': 'protect public and environment', 'approach': 'emergency planning and response', 'examples': 'evacuation plans, protective actions'}},
}

class RadiationProtectionZoneEnum(RichEnum):
    """
    Radiation protection zone classifications for nuclear facilities
    """
    # Enum members
    EXCLUSION_AREA = "EXCLUSION_AREA"
    LOW_POPULATION_ZONE = "LOW_POPULATION_ZONE"
    EMERGENCY_PLANNING_ZONE = "EMERGENCY_PLANNING_ZONE"
    INGESTION_PATHWAY_ZONE = "INGESTION_PATHWAY_ZONE"
    CONTROLLED_AREA = "CONTROLLED_AREA"
    SUPERVISED_AREA = "SUPERVISED_AREA"

# Set metadata after class creation to avoid it becoming an enum member
RadiationProtectionZoneEnum._metadata = {
    "EXCLUSION_AREA": {'description': 'Area under control of reactor operator with restricted access', 'annotations': {'control': 'reactor operator', 'public_access': 'restricted', 'size': 'typically few hundred meters radius', 'purpose': 'immediate accident response control'}},
    "LOW_POPULATION_ZONE": {'description': 'Area with low population density surrounding exclusion area', 'annotations': {'population_density': 'low', 'evacuation': 'feasible if needed', 'size': 'typically few kilometers radius', 'dose_limit': 'design basis for accident consequences'}},
    "EMERGENCY_PLANNING_ZONE": {'description': 'Area for which emergency planning is conducted', 'annotations': {'planning_required': 'comprehensive emergency plans', 'size': 'typically 10-mile (16 km) radius', 'protective_actions': 'evacuation and sheltering plans'}},
    "INGESTION_PATHWAY_ZONE": {'description': 'Area for controlling food and water contamination', 'annotations': {'contamination_control': 'food and water supplies', 'size': 'typically 50-mile (80 km) radius', 'monitoring': 'food chain monitoring required'}},
    "CONTROLLED_AREA": {'description': 'Area within facility boundary with access control', 'annotations': {'access_control': 'personnel monitoring required', 'radiation_monitoring': 'continuous monitoring', 'training_required': 'radiation safety training'}},
    "SUPERVISED_AREA": {'description': 'Area with potential for radiation exposure but lower than controlled', 'annotations': {'monitoring': 'periodic monitoring', 'access_control': 'limited restrictions', 'training_required': 'basic radiation awareness'}},
}

class NuclearFacilityTypeEnum(RichEnum):
    """
    Types of nuclear facilities and infrastructure
    """
    # Enum members
    COMMERCIAL_POWER_PLANT = "COMMERCIAL_POWER_PLANT"
    RESEARCH_REACTOR = "RESEARCH_REACTOR"
    TEST_REACTOR = "TEST_REACTOR"
    PROTOTYPE_REACTOR = "PROTOTYPE_REACTOR"
    NAVAL_REACTOR = "NAVAL_REACTOR"
    SPACE_REACTOR = "SPACE_REACTOR"
    PRODUCTION_REACTOR = "PRODUCTION_REACTOR"
    URANIUM_MINE = "URANIUM_MINE"
    URANIUM_MILL = "URANIUM_MILL"
    CONVERSION_FACILITY = "CONVERSION_FACILITY"
    ENRICHMENT_FACILITY = "ENRICHMENT_FACILITY"
    FUEL_FABRICATION_FACILITY = "FUEL_FABRICATION_FACILITY"
    REPROCESSING_FACILITY = "REPROCESSING_FACILITY"
    INTERIM_STORAGE_FACILITY = "INTERIM_STORAGE_FACILITY"
    GEOLOGICAL_REPOSITORY = "GEOLOGICAL_REPOSITORY"
    DECOMMISSIONING_SITE = "DECOMMISSIONING_SITE"
    NUCLEAR_LABORATORY = "NUCLEAR_LABORATORY"
    RADIOISOTOPE_PRODUCTION_FACILITY = "RADIOISOTOPE_PRODUCTION_FACILITY"

# Set metadata after class creation to avoid it becoming an enum member
NuclearFacilityTypeEnum._metadata = {
    "COMMERCIAL_POWER_PLANT": {'description': 'Large-scale commercial reactor for electricity generation', 'annotations': {'primary_purpose': 'electricity generation', 'power_output': 'typically 300-1600 MWe', 'operator_type': 'utility company', 'regulatory_oversight': 'extensive'}},
    "RESEARCH_REACTOR": {'description': 'Reactor designed for research, training, and isotope production', 'annotations': {'primary_purpose': 'research, training, isotope production', 'power_output': 'typically <100 MWt', 'neutron_flux': 'optimized for research needs', 'fuel_type': 'various, often HEU or LEU'}},
    "TEST_REACTOR": {'description': 'Reactor for testing materials and components', 'annotations': {'primary_purpose': 'materials and component testing', 'test_capabilities': 'irradiation testing', 'neutron_spectrum': 'variable for testing needs'}},
    "PROTOTYPE_REACTOR": {'description': 'Reactor for demonstrating new technology', 'annotations': {'primary_purpose': 'technology demonstration', 'scale': 'smaller than commercial', 'innovation_focus': 'new reactor concepts'}},
    "NAVAL_REACTOR": {'description': 'Reactor for ship or submarine propulsion', 'annotations': {'primary_purpose': 'vessel propulsion', 'compactness': 'highly compact design', 'fuel_enrichment': 'typically HEU', 'operation_mode': 'mobile platform'}},
    "SPACE_REACTOR": {'description': 'Reactor designed for space applications', 'annotations': {'primary_purpose': 'space power or propulsion', 'mass_constraints': 'extremely lightweight', 'cooling': 'radiative cooling', 'power_output': 'typically <10 MWt'}},
    "PRODUCTION_REACTOR": {'description': 'Reactor for producing nuclear materials', 'annotations': {'primary_purpose': 'isotope or material production', 'products': 'tritium, plutonium, medical isotopes', 'operation_mode': 'specialized for production'}},
    "URANIUM_MINE": {'description': 'Facility for extracting uranium ore', 'annotations': {'extraction_method': 'underground or open pit', 'product': 'uranium ore', 'processing': 'may include milling'}},
    "URANIUM_MILL": {'description': 'Facility for processing uranium ore into yellowcake', 'annotations': {'input_material': 'uranium ore', 'output_product': 'uranium concentrate (U3O8)', 'process': 'chemical extraction and purification'}},
    "CONVERSION_FACILITY": {'description': 'Facility for converting yellowcake to UF6', 'annotations': {'input_material': 'uranium concentrate (U3O8)', 'output_product': 'uranium hexafluoride (UF6)', 'process': 'chemical conversion'}},
    "ENRICHMENT_FACILITY": {'description': 'Facility for increasing U-235 concentration', 'annotations': {'input_material': 'natural UF6', 'output_product': 'enriched UF6', 'process': 'isotope separation (centrifuge, diffusion)', 'sensitive_technology': 'proliferation-sensitive'}},
    "FUEL_FABRICATION_FACILITY": {'description': 'Facility for manufacturing nuclear fuel assemblies', 'annotations': {'input_material': 'enriched UF6', 'output_product': 'fuel assemblies', 'process': 'pellet and rod manufacturing'}},
    "REPROCESSING_FACILITY": {'description': 'Facility for separating spent fuel components', 'annotations': {'input_material': 'spent nuclear fuel', 'output_products': 'uranium, plutonium, waste', 'process': 'chemical separation (PUREX, UREX+)', 'proliferation_sensitivity': 'high'}},
    "INTERIM_STORAGE_FACILITY": {'description': 'Facility for temporary storage of nuclear materials', 'annotations': {'storage_duration': 'intermediate term (5-100 years)', 'storage_medium': 'pools, dry casks', 'typical_materials': 'spent fuel, waste'}},
    "GEOLOGICAL_REPOSITORY": {'description': 'Deep underground facility for permanent waste disposal', 'annotations': {'storage_duration': 'permanent (thousands of years)', 'depth': 'typically >300 meters underground', 'waste_types': 'high-level waste, spent fuel'}},
    "DECOMMISSIONING_SITE": {'description': 'Nuclear facility undergoing dismantlement', 'annotations': {'facility_status': 'being dismantled', 'activities': 'decontamination, demolition', 'duration': 'typically 10-50 years'}},
    "NUCLEAR_LABORATORY": {'description': 'Laboratory facility handling radioactive materials', 'annotations': {'activities': 'research, analysis, small-scale production', 'materials': 'various radioactive substances', 'scale': 'laboratory scale'}},
    "RADIOISOTOPE_PRODUCTION_FACILITY": {'description': 'Facility for producing medical and industrial isotopes', 'annotations': {'products': 'medical isotopes, industrial tracers', 'production_methods': 'reactor irradiation, accelerator', 'market': 'medical and industrial applications'}},
}

class PowerPlantStatusEnum(RichEnum):
    """
    Operational status of nuclear power plants
    """
    # Enum members
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    COMMISSIONING = "COMMISSIONING"
    COMMERCIAL_OPERATION = "COMMERCIAL_OPERATION"
    REFUELING_OUTAGE = "REFUELING_OUTAGE"
    EXTENDED_OUTAGE = "EXTENDED_OUTAGE"
    PERMANENTLY_SHUTDOWN = "PERMANENTLY_SHUTDOWN"
    DECOMMISSIONING = "DECOMMISSIONING"
    DECOMMISSIONED = "DECOMMISSIONED"

# Set metadata after class creation to avoid it becoming an enum member
PowerPlantStatusEnum._metadata = {
    "UNDER_CONSTRUCTION": {'description': 'Plant currently being built', 'annotations': {'construction_phase': 'civil and mechanical work ongoing', 'licensing_status': 'construction permit issued', 'commercial_operation': 'not yet started'}},
    "COMMISSIONING": {'description': 'Plant undergoing testing before commercial operation', 'annotations': {'testing_phase': 'systems testing and startup', 'fuel_loading': 'may have occurred', 'commercial_operation': 'not yet achieved'}},
    "COMMERCIAL_OPERATION": {'description': 'Plant operating commercially for electricity generation', 'annotations': {'operational_status': 'fully operational', 'power_generation': 'commercial electricity production', 'licensing_status': 'operating license active'}},
    "REFUELING_OUTAGE": {'description': 'Plant temporarily shut down for fuel replacement and maintenance', 'annotations': {'shutdown_reason': 'scheduled refueling', 'duration': 'typically 30-60 days', 'activities': 'fuel replacement, maintenance, inspection'}},
    "EXTENDED_OUTAGE": {'description': 'Plant shut down for extended period for major work', 'annotations': {'shutdown_duration': 'months to years', 'work_scope': 'major modifications or repairs', 'return_to_service': 'planned'}},
    "PERMANENTLY_SHUTDOWN": {'description': 'Plant permanently ceased operation', 'annotations': {'operational_status': 'permanently ceased', 'fuel_removal': 'may be ongoing or completed', 'decommissioning': 'may be planned or ongoing'}},
    "DECOMMISSIONING": {'description': 'Plant undergoing dismantlement', 'annotations': {'decommissioning_phase': 'active dismantlement', 'radioactive_cleanup': 'ongoing', 'site_restoration': 'planned'}},
    "DECOMMISSIONED": {'description': 'Plant completely dismantled and site restored', 'annotations': {'dismantlement_status': 'completed', 'site_condition': 'restored for unrestricted use', 'radioactive_materials': 'removed'}},
}

class ResearchReactorTypeEnum(RichEnum):
    """
    Types of research reactors
    """
    # Enum members
    POOL_TYPE = "POOL_TYPE"
    TANK_TYPE = "TANK_TYPE"
    HOMOGENEOUS = "HOMOGENEOUS"
    FAST_RESEARCH_REACTOR = "FAST_RESEARCH_REACTOR"
    PULSED_REACTOR = "PULSED_REACTOR"
    CRITICAL_ASSEMBLY = "CRITICAL_ASSEMBLY"
    SUBCRITICAL_ASSEMBLY = "SUBCRITICAL_ASSEMBLY"

# Set metadata after class creation to avoid it becoming an enum member
ResearchReactorTypeEnum._metadata = {
    "POOL_TYPE": {'description': 'Reactor with fuel in open pool of water', 'annotations': {'design': 'open pool with underwater fuel', 'power_level': 'typically 1-20 MW', 'applications': 'neutron beam experiments, training'}},
    "TANK_TYPE": {'description': 'Reactor with fuel in enclosed tank', 'annotations': {'design': 'fuel in pressurized or unpressurized tank', 'power_level': 'variable', 'containment': 'more enclosed than pool type'}},
    "HOMOGENEOUS": {'description': 'Reactor with fuel in liquid form', 'annotations': {'fuel_form': 'aqueous solution', 'design': 'fuel dissolved in moderator', 'power_level': 'typically low'}},
    "FAST_RESEARCH_REACTOR": {'description': 'Research reactor using fast neutrons', 'annotations': {'neutron_spectrum': 'fast neutrons', 'moderator': 'none or minimal', 'applications': 'fast neutron research'}},
    "PULSED_REACTOR": {'description': 'Reactor designed for pulsed operation', 'annotations': {'operation_mode': 'short intense pulses', 'power_level': 'very high peak power', 'applications': 'transient testing, physics research'}},
    "CRITICAL_ASSEMBLY": {'description': 'Minimal reactor for criticality studies', 'annotations': {'power_level': 'essentially zero', 'purpose': 'criticality experiments, training', 'design': 'minimal critical configuration'}},
    "SUBCRITICAL_ASSEMBLY": {'description': 'Neutron source-driven subcritical system', 'annotations': {'criticality': 'subcritical', 'neutron_source': 'external source required', 'applications': 'research, training, transmutation studies'}},
}

class FuelCycleFacilityTypeEnum(RichEnum):
    """
    Types of nuclear fuel cycle facilities
    """
    # Enum members
    IN_SITU_LEACH_MINE = "IN_SITU_LEACH_MINE"
    CONVENTIONAL_MINE = "CONVENTIONAL_MINE"
    HEAP_LEACH_FACILITY = "HEAP_LEACH_FACILITY"
    GASEOUS_DIFFUSION_PLANT = "GASEOUS_DIFFUSION_PLANT"
    GAS_CENTRIFUGE_PLANT = "GAS_CENTRIFUGE_PLANT"
    LASER_ENRICHMENT_FACILITY = "LASER_ENRICHMENT_FACILITY"
    MOX_FUEL_FABRICATION = "MOX_FUEL_FABRICATION"
    AQUEOUS_REPROCESSING = "AQUEOUS_REPROCESSING"
    PYROPROCESSING_FACILITY = "PYROPROCESSING_FACILITY"

# Set metadata after class creation to avoid it becoming an enum member
FuelCycleFacilityTypeEnum._metadata = {
    "IN_SITU_LEACH_MINE": {'description': 'Uranium extraction by solution mining', 'annotations': {'extraction_method': 'chemical leaching in ground', 'environmental_impact': 'lower surface disturbance', 'geology_requirement': 'permeable ore deposits'}},
    "CONVENTIONAL_MINE": {'description': 'Traditional underground or open-pit uranium mining', 'annotations': {'extraction_method': 'physical excavation', 'mine_types': 'underground or open pit', 'ore_grade': 'variable'}},
    "HEAP_LEACH_FACILITY": {'description': 'Uranium extraction from low-grade ores by heap leaching', 'annotations': {'ore_grade': 'low-grade ores', 'process': 'chemical leaching of ore piles', 'economics': 'cost-effective for low grades'}},
    "GASEOUS_DIFFUSION_PLANT": {'description': 'Uranium enrichment using gaseous diffusion', 'annotations': {'enrichment_method': 'gaseous diffusion', 'energy_consumption': 'very high', 'status': 'mostly retired technology'}},
    "GAS_CENTRIFUGE_PLANT": {'description': 'Uranium enrichment using centrifuge technology', 'annotations': {'enrichment_method': 'gas centrifuge', 'energy_consumption': 'lower than diffusion', 'technology_status': 'current standard technology'}},
    "LASER_ENRICHMENT_FACILITY": {'description': 'Uranium enrichment using laser isotope separation', 'annotations': {'enrichment_method': 'laser isotope separation', 'technology_status': 'under development', 'energy_consumption': 'potentially lower'}},
    "MOX_FUEL_FABRICATION": {'description': 'Facility for manufacturing mixed oxide fuel', 'annotations': {'fuel_type': 'mixed oxide (uranium and plutonium)', 'input_materials': 'plutonium dioxide, uranium dioxide', 'special_handling': 'plutonium handling required'}},
    "AQUEOUS_REPROCESSING": {'description': 'Spent fuel reprocessing using aqueous methods', 'annotations': {'process_type': 'PUREX or similar aqueous process', 'separation_products': 'uranium, plutonium, waste', 'technology_maturity': 'commercially proven'}},
    "PYROPROCESSING_FACILITY": {'description': 'Spent fuel reprocessing using electrochemical methods', 'annotations': {'process_type': 'electrochemical separation', 'temperature': 'high temperature operation', 'technology_status': 'under development'}},
}

class WasteFacilityTypeEnum(RichEnum):
    """
    Types of nuclear waste management facilities
    """
    # Enum members
    SPENT_FUEL_POOL = "SPENT_FUEL_POOL"
    DRY_CASK_STORAGE = "DRY_CASK_STORAGE"
    CENTRALIZED_INTERIM_STORAGE = "CENTRALIZED_INTERIM_STORAGE"
    LOW_LEVEL_WASTE_DISPOSAL = "LOW_LEVEL_WASTE_DISPOSAL"
    GREATER_THAN_CLASS_C_STORAGE = "GREATER_THAN_CLASS_C_STORAGE"
    TRANSURANIC_WASTE_REPOSITORY = "TRANSURANIC_WASTE_REPOSITORY"
    HIGH_LEVEL_WASTE_REPOSITORY = "HIGH_LEVEL_WASTE_REPOSITORY"
    WASTE_TREATMENT_FACILITY = "WASTE_TREATMENT_FACILITY"
    DECONTAMINATION_FACILITY = "DECONTAMINATION_FACILITY"

# Set metadata after class creation to avoid it becoming an enum member
WasteFacilityTypeEnum._metadata = {
    "SPENT_FUEL_POOL": {'description': 'Water-filled pool for cooling spent fuel', 'annotations': {'cooling_medium': 'water', 'location': 'typically at reactor site', 'storage_duration': '5-10 years typical'}},
    "DRY_CASK_STORAGE": {'description': 'Air-cooled storage in sealed containers', 'annotations': {'cooling_medium': 'air circulation', 'storage_duration': '20-100 years', 'location': 'on-site or centralized'}},
    "CENTRALIZED_INTERIM_STORAGE": {'description': 'Large-scale interim storage away from reactor sites', 'annotations': {'scale': "multiple reactor's worth of fuel", 'storage_duration': 'decades', 'transportation': 'rail or truck access required'}},
    "LOW_LEVEL_WASTE_DISPOSAL": {'description': 'Near-surface disposal for low-level waste', 'annotations': {'waste_category': 'Class A, B, C low-level waste', 'disposal_depth': 'near-surface (<30 meters)', 'institutional_control': '100 years minimum'}},
    "GREATER_THAN_CLASS_C_STORAGE": {'description': 'Storage for waste exceeding Class C limits', 'annotations': {'waste_category': 'greater than Class C waste', 'storage_type': 'interim storage pending disposal', 'disposal_requirements': 'deep disposal likely required'}},
    "TRANSURANIC_WASTE_REPOSITORY": {'description': 'Deep geological repository for TRU waste', 'annotations': {'waste_category': 'transuranic waste', 'disposal_depth': 'deep underground', 'example': 'Waste Isolation Pilot Plant (WIPP)'}},
    "HIGH_LEVEL_WASTE_REPOSITORY": {'description': 'Deep geological repository for high-level waste', 'annotations': {'waste_category': 'high-level waste, spent fuel', 'disposal_depth': 'typically >300 meters', 'containment_period': 'thousands of years'}},
    "WASTE_TREATMENT_FACILITY": {'description': 'Facility for processing and conditioning waste', 'annotations': {'purpose': 'volume reduction, stabilization', 'processes': 'incineration, compaction, solidification', 'output': 'treated waste for disposal'}},
    "DECONTAMINATION_FACILITY": {'description': 'Facility for cleaning contaminated materials', 'annotations': {'purpose': 'remove radioactive contamination', 'materials': 'equipment, clothing, tools', 'methods': 'chemical, physical decontamination'}},
}

class NuclearShipTypeEnum(RichEnum):
    """
    Types of nuclear-powered vessels
    """
    # Enum members
    AIRCRAFT_CARRIER = "AIRCRAFT_CARRIER"
    SUBMARINE = "SUBMARINE"
    CRUISER = "CRUISER"
    ICEBREAKER = "ICEBREAKER"
    MERCHANT_SHIP = "MERCHANT_SHIP"
    RESEARCH_VESSEL = "RESEARCH_VESSEL"

# Set metadata after class creation to avoid it becoming an enum member
NuclearShipTypeEnum._metadata = {
    "AIRCRAFT_CARRIER": {'description': 'Large naval vessel with nuclear propulsion and aircraft operations', 'annotations': {'propulsion': 'nuclear steam turbine', 'size': 'very large (>80,000 tons)', 'mission': 'power projection, aircraft operations', 'reactor_count': 'typically 2'}},
    "SUBMARINE": {'description': 'Underwater vessel with nuclear propulsion', 'annotations': {'propulsion': 'nuclear steam turbine', 'operational_environment': 'submerged', 'mission': 'various (attack, ballistic missile, cruise missile)', 'reactor_count': 'typically 1'}},
    "CRUISER": {'description': 'Large surface combatant with nuclear propulsion', 'annotations': {'propulsion': 'nuclear steam turbine', 'mission': 'escort, surface warfare', 'size': 'large surface vessel', 'status': 'mostly retired'}},
    "ICEBREAKER": {'description': 'Vessel designed to break ice using nuclear power', 'annotations': {'propulsion': 'nuclear steam turbine or electric', 'mission': 'ice breaking, Arctic operations', 'operational_environment': 'polar regions', 'reactor_count': '1-3'}},
    "MERCHANT_SHIP": {'description': 'Commercial cargo vessel with nuclear propulsion', 'annotations': {'propulsion': 'nuclear steam turbine', 'mission': 'cargo transport', 'commercial_viability': 'limited due to costs', 'examples': 'NS Savannah, few others'}},
    "RESEARCH_VESSEL": {'description': 'Ship designed for oceanographic research with nuclear power', 'annotations': {'propulsion': 'nuclear', 'mission': 'scientific research', 'duration': 'extended operations without refueling', 'examples': 'limited number built'}},
}

class ReactorOperatingStateEnum(RichEnum):
    """
    Operational states of nuclear reactors
    """
    # Enum members
    STARTUP = "STARTUP"
    CRITICAL = "CRITICAL"
    POWER_ESCALATION = "POWER_ESCALATION"
    FULL_POWER_OPERATION = "FULL_POWER_OPERATION"
    LOAD_FOLLOWING = "LOAD_FOLLOWING"
    REDUCED_POWER = "REDUCED_POWER"
    HOT_STANDBY = "HOT_STANDBY"
    COLD_SHUTDOWN = "COLD_SHUTDOWN"
    REFUELING = "REFUELING"
    REACTOR_TRIP = "REACTOR_TRIP"
    SCRAM = "SCRAM"
    EMERGENCY_SHUTDOWN = "EMERGENCY_SHUTDOWN"

# Set metadata after class creation to avoid it becoming an enum member
ReactorOperatingStateEnum._metadata = {
    "STARTUP": {'description': 'Reactor transitioning from shutdown to power operation', 'annotations': {'neutron_level': 'increasing', 'control_rod_position': 'withdrawing', 'power_level': 'rising from zero', 'duration': 'hours to days', 'operator_attention': 'high'}},
    "CRITICAL": {'description': 'Reactor achieving self-sustaining chain reaction', 'annotations': {'neutron_multiplication': 'k-effective = 1.0', 'power_level': 'minimal but self-sustaining', 'control_rod_position': 'critical position', 'milestone': 'first criticality achievement'}},
    "POWER_ESCALATION": {'description': 'Reactor increasing power toward full power operation', 'annotations': {'power_level': 'increasing incrementally', 'testing': 'ongoing at each power level', 'duration': 'days to weeks', 'procedures': 'systematic power increases'}},
    "FULL_POWER_OPERATION": {'description': 'Reactor operating at rated thermal power', 'annotations': {'power_level': '100% rated power', 'operation_mode': 'commercial electricity generation', 'duration': 'typically 12-24 months', 'fuel_burnup': 'accumulating'}},
    "LOAD_FOLLOWING": {'description': 'Reactor adjusting power to match electrical demand', 'annotations': {'power_level': 'variable based on demand', 'control_mode': 'automatic load following', 'flexibility': 'grid demand responsive', 'frequency': 'daily power variations'}},
    "REDUCED_POWER": {'description': 'Reactor operating below rated power', 'annotations': {'power_level': '<100% rated power', 'reasons': 'maintenance, grid demand, testing', 'control_rod_position': 'partially inserted'}},
    "HOT_STANDBY": {'description': 'Reactor subcritical but at operating temperature', 'annotations': {'criticality': 'subcritical', 'temperature': 'operating temperature maintained', 'pressure': 'operating pressure maintained', 'ready_time': 'rapid return to power possible'}},
    "COLD_SHUTDOWN": {'description': 'Reactor subcritical and cooled below operating temperature', 'annotations': {'criticality': 'subcritical with margin', 'temperature': '<200°F (93°C) typically', 'refueling': 'possible in this state', 'maintenance': 'major maintenance possible'}},
    "REFUELING": {'description': 'Reactor shut down for fuel replacement', 'annotations': {'reactor_head': 'removed', 'fuel_handling': 'active fuel movement', 'criticality_control': 'strict procedures', 'duration': 'typically 30-60 days'}},
    "REACTOR_TRIP": {'description': 'Rapid automatic shutdown due to safety system actuation', 'annotations': {'shutdown_speed': 'seconds', 'cause': 'safety system activation', 'control_rods': 'fully inserted rapidly', 'investigation': 'cause determination required'}},
    "SCRAM": {'description': 'Emergency rapid shutdown of reactor', 'annotations': {'shutdown_type': 'emergency shutdown', 'control_rod_insertion': 'fastest possible', 'operator_action': 'manual or automatic', 'follow_up': 'immediate safety assessment'}},
    "EMERGENCY_SHUTDOWN": {'description': 'Shutdown due to emergency conditions', 'annotations': {'urgency': 'immediate shutdown required', 'safety_systems': 'may be activated', 'investigation': 'extensive post-event analysis', 'recovery': 'detailed restart procedures'}},
}

class MaintenanceTypeEnum(RichEnum):
    """
    Types of nuclear facility maintenance activities
    """
    # Enum members
    PREVENTIVE_MAINTENANCE = "PREVENTIVE_MAINTENANCE"
    CORRECTIVE_MAINTENANCE = "CORRECTIVE_MAINTENANCE"
    PREDICTIVE_MAINTENANCE = "PREDICTIVE_MAINTENANCE"
    CONDITION_BASED_MAINTENANCE = "CONDITION_BASED_MAINTENANCE"
    REFUELING_OUTAGE_MAINTENANCE = "REFUELING_OUTAGE_MAINTENANCE"
    FORCED_OUTAGE_MAINTENANCE = "FORCED_OUTAGE_MAINTENANCE"
    IN_SERVICE_INSPECTION = "IN_SERVICE_INSPECTION"
    MODIFICATION_WORK = "MODIFICATION_WORK"

# Set metadata after class creation to avoid it becoming an enum member
MaintenanceTypeEnum._metadata = {
    "PREVENTIVE_MAINTENANCE": {'description': 'Scheduled maintenance to prevent equipment failure', 'annotations': {'schedule': 'predetermined intervals', 'purpose': 'prevent failures', 'planning': 'extensive advance planning', 'outage_type': 'planned outage'}},
    "CORRECTIVE_MAINTENANCE": {'description': 'Maintenance to repair failed or degraded equipment', 'annotations': {'trigger': 'equipment failure or degradation', 'urgency': 'varies by safety significance', 'planning': 'may be immediate', 'schedule': 'unplanned'}},
    "PREDICTIVE_MAINTENANCE": {'description': 'Maintenance based on condition monitoring', 'annotations': {'basis': 'condition monitoring data', 'timing': 'based on predicted failure', 'efficiency': 'optimized maintenance timing', 'technology': 'condition monitoring systems'}},
    "CONDITION_BASED_MAINTENANCE": {'description': 'Maintenance triggered by equipment condition assessment', 'annotations': {'assessment': 'continuous condition monitoring', 'trigger': 'condition degradation', 'optimization': 'resource optimization', 'safety': 'maintains safety margins'}},
    "REFUELING_OUTAGE_MAINTENANCE": {'description': 'Major maintenance during scheduled refueling', 'annotations': {'frequency': 'every 12-24 months', 'scope': 'major equipment inspection and repair', 'duration': '30-60 days typical', 'access': 'full plant access available'}},
    "FORCED_OUTAGE_MAINTENANCE": {'description': 'Unplanned maintenance due to equipment failure', 'annotations': {'cause': 'unexpected equipment failure', 'urgency': 'immediate attention required', 'duration': 'variable', 'safety_significance': 'may affect safety systems'}},
    "IN_SERVICE_INSPECTION": {'description': 'Required inspection of safety-related components', 'annotations': {'regulatory_requirement': 'mandated by regulations', 'frequency': 'specified intervals (typically 10 years)', 'scope': 'pressure vessels, piping, supports', 'techniques': 'non-destructive testing'}},
    "MODIFICATION_WORK": {'description': 'Changes to plant design or configuration', 'annotations': {'purpose': 'plant improvement or regulatory compliance', 'approval': 'requires design change approval', 'testing': 'extensive post-modification testing', 'documentation': 'comprehensive documentation updates'}},
}

class LicensingStageEnum(RichEnum):
    """
    Nuclear facility licensing stages
    """
    # Enum members
    SITE_PERMIT = "SITE_PERMIT"
    DESIGN_CERTIFICATION = "DESIGN_CERTIFICATION"
    CONSTRUCTION_PERMIT = "CONSTRUCTION_PERMIT"
    OPERATING_LICENSE = "OPERATING_LICENSE"
    LICENSE_RENEWAL = "LICENSE_RENEWAL"
    COMBINED_LICENSE = "COMBINED_LICENSE"
    DECOMMISSIONING_PLAN = "DECOMMISSIONING_PLAN"
    LICENSE_TERMINATION = "LICENSE_TERMINATION"

# Set metadata after class creation to avoid it becoming an enum member
LicensingStageEnum._metadata = {
    "SITE_PERMIT": {'description': 'Early site permit for nuclear facility', 'annotations': {'scope': 'site suitability evaluation', 'duration': '10-20 years typically', 'flexibility': 'technology-neutral', 'advantage': 'reduced licensing risk'}},
    "DESIGN_CERTIFICATION": {'description': 'Certification of standardized reactor design', 'annotations': {'scope': 'reactor design approval', 'duration': '15-20 years typically', 'advantage': 'reduced construction licensing time', 'standardization': 'enables multiple deployments'}},
    "CONSTRUCTION_PERMIT": {'description': 'Authorization to begin nuclear facility construction', 'annotations': {'authorization': 'construction activities', 'requirements': 'detailed design and safety analysis', 'oversight': 'construction inspection program', 'milestone': 'major licensing milestone'}},
    "OPERATING_LICENSE": {'description': 'Authorization for commercial reactor operation', 'annotations': {'authorization': 'power operation and fuel loading', 'duration': 'initially 40 years', 'renewal': 'possible for additional 20 years', 'testing': 'extensive pre-operational testing'}},
    "LICENSE_RENEWAL": {'description': 'Extension of operating license beyond initial term', 'annotations': {'extension': 'additional 20 years typical', 'review': 'aging management program review', 'basis': 'demonstrated safe operation', 'economics': 'enables continued operation'}},
    "COMBINED_LICENSE": {'description': 'Combined construction and operating license', 'annotations': {'scope': 'construction and operation authorization', 'advantage': 'single licensing process', 'requirements': 'complete design and safety analysis', 'efficiency': 'streamlined licensing approach'}},
    "DECOMMISSIONING_PLAN": {'description': 'Approval of facility decommissioning plan', 'annotations': {'scope': 'facility dismantlement plan', 'funding': 'decommissioning funding assurance', 'schedule': 'decommissioning timeline', 'end_state': 'final site condition'}},
    "LICENSE_TERMINATION": {'description': 'Final termination of nuclear facility license', 'annotations': {'completion': 'decommissioning completion', 'survey': 'final radiological survey', 'release': 'site release for unrestricted use', 'finality': 'end of regulatory oversight'}},
}

class FuelCycleOperationEnum(RichEnum):
    """
    Nuclear fuel cycle operational activities
    """
    # Enum members
    URANIUM_EXPLORATION = "URANIUM_EXPLORATION"
    URANIUM_EXTRACTION = "URANIUM_EXTRACTION"
    URANIUM_MILLING = "URANIUM_MILLING"
    URANIUM_CONVERSION = "URANIUM_CONVERSION"
    URANIUM_ENRICHMENT = "URANIUM_ENRICHMENT"
    FUEL_FABRICATION = "FUEL_FABRICATION"
    REACTOR_FUEL_LOADING = "REACTOR_FUEL_LOADING"
    REACTOR_OPERATION = "REACTOR_OPERATION"
    SPENT_FUEL_DISCHARGE = "SPENT_FUEL_DISCHARGE"
    SPENT_FUEL_STORAGE = "SPENT_FUEL_STORAGE"
    SPENT_FUEL_REPROCESSING = "SPENT_FUEL_REPROCESSING"
    WASTE_CONDITIONING = "WASTE_CONDITIONING"
    WASTE_DISPOSAL = "WASTE_DISPOSAL"

# Set metadata after class creation to avoid it becoming an enum member
FuelCycleOperationEnum._metadata = {
    "URANIUM_EXPLORATION": {'description': 'Search and evaluation of uranium deposits', 'annotations': {'activities': 'geological surveys, drilling, sampling', 'purpose': 'locate economically viable deposits', 'methods': 'airborne surveys, ground exploration'}},
    "URANIUM_EXTRACTION": {'description': 'Mining and extraction of uranium ore', 'annotations': {'methods': 'open pit, underground, in-situ leaching', 'output': 'uranium ore', 'processing': 'crushing and grinding'}},
    "URANIUM_MILLING": {'description': 'Processing of uranium ore to produce yellowcake', 'annotations': {'input': 'uranium ore', 'output': 'uranium concentrate (U3O8)', 'process': 'acid or alkaline leaching'}},
    "URANIUM_CONVERSION": {'description': 'Conversion of yellowcake to uranium hexafluoride', 'annotations': {'input': 'uranium concentrate (U3O8)', 'output': 'uranium hexafluoride (UF6)', 'purpose': 'prepare for enrichment'}},
    "URANIUM_ENRICHMENT": {'description': 'Increase U-235 concentration in uranium', 'annotations': {'input': 'natural uranium (0.711% U-235)', 'output': 'enriched uranium (3-5% typical)', 'waste': 'depleted uranium tails', 'methods': 'gas centrifuge, gaseous diffusion'}},
    "FUEL_FABRICATION": {'description': 'Manufacturing of nuclear fuel assemblies', 'annotations': {'input': 'enriched uranium', 'output': 'fuel assemblies', 'process': 'pellet production, rod assembly'}},
    "REACTOR_FUEL_LOADING": {'description': 'Installation of fresh fuel in reactor', 'annotations': {'frequency': 'every 12-24 months', 'procedure': 'careful criticality control', 'configuration': 'specific loading pattern'}},
    "REACTOR_OPERATION": {'description': 'Power generation and fuel burnup', 'annotations': {'duration': '12-24 months typical cycle', 'burnup': 'fuel depletion over time', 'output': 'electricity and fission products'}},
    "SPENT_FUEL_DISCHARGE": {'description': 'Removal of used fuel from reactor', 'annotations': {'timing': 'end of fuel cycle', 'handling': 'underwater fuel handling', 'destination': 'spent fuel pool storage'}},
    "SPENT_FUEL_STORAGE": {'description': 'Interim storage of discharged fuel', 'annotations': {'cooling': 'decay heat removal', 'duration': '5-100+ years', 'methods': 'pools, dry casks'}},
    "SPENT_FUEL_REPROCESSING": {'description': 'Chemical separation of spent fuel components', 'annotations': {'separation': 'uranium, plutonium, waste', 'recovery': 'recovers usable materials', 'waste': 'high-level waste production'}},
    "WASTE_CONDITIONING": {'description': 'Preparation of waste for storage or disposal', 'annotations': {'treatment': 'solidification, encapsulation', 'purpose': 'stable waste form', 'standards': 'waste acceptance criteria'}},
    "WASTE_DISPOSAL": {'description': 'Permanent disposal of nuclear waste', 'annotations': {'method': 'geological repository', 'isolation': 'long-term containment', 'safety': 'protect public and environment'}},
}

class ReactorControlModeEnum(RichEnum):
    """
    Reactor control and safety system operational modes
    """
    # Enum members
    MANUAL_CONTROL = "MANUAL_CONTROL"
    AUTOMATIC_CONTROL = "AUTOMATIC_CONTROL"
    REACTOR_PROTECTION_SYSTEM = "REACTOR_PROTECTION_SYSTEM"
    ENGINEERED_SAFEGUARDS = "ENGINEERED_SAFEGUARDS"
    EMERGENCY_OPERATING_PROCEDURES = "EMERGENCY_OPERATING_PROCEDURES"
    SEVERE_ACCIDENT_MANAGEMENT = "SEVERE_ACCIDENT_MANAGEMENT"

# Set metadata after class creation to avoid it becoming an enum member
ReactorControlModeEnum._metadata = {
    "MANUAL_CONTROL": {'description': 'Direct operator control of reactor systems', 'annotations': {'operator_role': 'direct manual operation', 'automation': 'minimal automation', 'response_time': 'depends on operator', 'application': 'startup, shutdown, testing'}},
    "AUTOMATIC_CONTROL": {'description': 'Automated reactor control systems', 'annotations': {'automation': 'high level automation', 'operator_role': 'supervisory', 'response_time': 'rapid automatic response', 'application': 'normal power operation'}},
    "REACTOR_PROTECTION_SYSTEM": {'description': 'Safety system monitoring for trip conditions', 'annotations': {'function': 'automatic reactor trip on unsafe conditions', 'redundancy': 'multiple independent channels', 'response_time': 'milliseconds to seconds', 'priority': 'overrides operator actions'}},
    "ENGINEERED_SAFEGUARDS": {'description': 'Safety systems for accident mitigation', 'annotations': {'function': 'mitigate consequences of accidents', 'activation': 'automatic on accident conditions', 'systems': 'emergency core cooling, containment', 'redundancy': 'multiple trains'}},
    "EMERGENCY_OPERATING_PROCEDURES": {'description': 'Operator actions for emergency conditions', 'annotations': {'guidance': 'symptom-based procedures', 'training': 'extensive operator training', 'decision_making': 'structured approach', 'coordination': 'with emergency response'}},
    "SEVERE_ACCIDENT_MANAGEMENT": {'description': 'Procedures for beyond design basis accidents', 'annotations': {'scope': 'core damage mitigation', 'guidance': 'severe accident management guidelines', 'equipment': 'portable emergency equipment', 'coordination': 'multi-unit considerations'}},
}

class OperationalProcedureEnum(RichEnum):
    """
    Standard nuclear facility operational procedures
    """
    # Enum members
    STARTUP_PROCEDURE = "STARTUP_PROCEDURE"
    SHUTDOWN_PROCEDURE = "SHUTDOWN_PROCEDURE"
    REFUELING_PROCEDURE = "REFUELING_PROCEDURE"
    SURVEILLANCE_TESTING = "SURVEILLANCE_TESTING"
    MAINTENANCE_PROCEDURE = "MAINTENANCE_PROCEDURE"
    EMERGENCY_RESPONSE = "EMERGENCY_RESPONSE"
    RADIOLOGICAL_PROTECTION = "RADIOLOGICAL_PROTECTION"
    SECURITY_PROCEDURE = "SECURITY_PROCEDURE"

# Set metadata after class creation to avoid it becoming an enum member
OperationalProcedureEnum._metadata = {
    "STARTUP_PROCEDURE": {'description': 'Systematic procedure for bringing reactor to power', 'annotations': {'phases': 'multiple phases with hold points', 'testing': 'system testing at each phase', 'authorization': 'management authorization required', 'duration': 'hours to days'}},
    "SHUTDOWN_PROCEDURE": {'description': 'Systematic procedure for shutting down reactor', 'annotations': {'control_rod_insertion': 'gradual or rapid', 'cooling': 'controlled cooldown', 'systems': 'systematic system shutdown', 'verification': 'shutdown margin verification'}},
    "REFUELING_PROCEDURE": {'description': 'Procedure for fuel handling and replacement', 'annotations': {'criticality_control': 'strict criticality prevention', 'handling': 'underwater fuel handling', 'documentation': 'detailed records', 'verification': 'independent verification'}},
    "SURVEILLANCE_TESTING": {'description': 'Regular testing of safety systems', 'annotations': {'frequency': 'specified by technical specifications', 'scope': 'functionality verification', 'documentation': 'test result documentation', 'corrective_action': 'if performance degraded'}},
    "MAINTENANCE_PROCEDURE": {'description': 'Systematic approach to equipment maintenance', 'annotations': {'work_control': 'work order control process', 'safety_tagging': 'equipment isolation', 'testing': 'post-maintenance testing', 'documentation': 'maintenance records'}},
    "EMERGENCY_RESPONSE": {'description': 'Response to emergency conditions', 'annotations': {'classification': 'event classification', 'notification': 'offsite notification', 'mitigation': 'protective action implementation', 'coordination': 'with offsite authorities'}},
    "RADIOLOGICAL_PROTECTION": {'description': 'Procedures for radiation protection', 'annotations': {'monitoring': 'radiation monitoring', 'contamination_control': 'contamination prevention', 'dose_control': 'personnel dose limits', 'emergency': 'radiological emergency response'}},
    "SECURITY_PROCEDURE": {'description': 'Physical security and access control procedures', 'annotations': {'access_control': 'personnel access authorization', 'detection': 'intrusion detection systems', 'response': 'security force response', 'coordination': 'with law enforcement'}},
}

class MiningType(RichEnum):
    """
    Types of mining operations
    """
    # Enum members
    OPEN_PIT = "OPEN_PIT"
    STRIP_MINING = "STRIP_MINING"
    MOUNTAINTOP_REMOVAL = "MOUNTAINTOP_REMOVAL"
    QUARRYING = "QUARRYING"
    PLACER = "PLACER"
    DREDGING = "DREDGING"
    SHAFT_MINING = "SHAFT_MINING"
    DRIFT_MINING = "DRIFT_MINING"
    SLOPE_MINING = "SLOPE_MINING"
    ROOM_AND_PILLAR = "ROOM_AND_PILLAR"
    LONGWALL = "LONGWALL"
    BLOCK_CAVING = "BLOCK_CAVING"
    SOLUTION_MINING = "SOLUTION_MINING"
    HYDRAULIC_MINING = "HYDRAULIC_MINING"
    ARTISANAL = "ARTISANAL"
    DEEP_SEA = "DEEP_SEA"

# Set metadata after class creation to avoid it becoming an enum member
MiningType._metadata = {
    "OPEN_PIT": {'description': 'Open-pit mining', 'meaning': 'ENVO:00000284', 'annotations': {'category': 'surface', 'depth': 'shallow to deep'}},
    "STRIP_MINING": {'description': 'Strip mining', 'meaning': 'ENVO:01001441', 'annotations': {'category': 'surface', 'aliases': 'surface mining, opencast mining'}},
    "MOUNTAINTOP_REMOVAL": {'description': 'Mountaintop removal mining', 'annotations': {'category': 'surface', 'region': 'primarily Appalachian'}},
    "QUARRYING": {'description': 'Quarrying', 'meaning': 'ENVO:00000284', 'annotations': {'category': 'surface', 'materials': 'stone, sand, gravel'}},
    "PLACER": {'description': 'Placer mining', 'meaning': 'ENVO:01001204', 'annotations': {'category': 'surface', 'target': 'alluvial deposits'}},
    "DREDGING": {'description': 'Dredging', 'annotations': {'category': 'surface/underwater', 'environment': 'rivers, harbors, seas'}},
    "SHAFT_MINING": {'description': 'Shaft mining', 'annotations': {'category': 'underground', 'access': 'vertical shaft'}},
    "DRIFT_MINING": {'description': 'Drift mining', 'annotations': {'category': 'underground', 'access': 'horizontal tunnel'}},
    "SLOPE_MINING": {'description': 'Slope mining', 'annotations': {'category': 'underground', 'access': 'inclined shaft'}},
    "ROOM_AND_PILLAR": {'description': 'Room and pillar mining', 'annotations': {'category': 'underground', 'method': 'leaves pillars for support'}},
    "LONGWALL": {'description': 'Longwall mining', 'annotations': {'category': 'underground', 'method': 'progressive slice extraction'}},
    "BLOCK_CAVING": {'description': 'Block caving', 'annotations': {'category': 'underground', 'method': 'gravity-assisted'}},
    "SOLUTION_MINING": {'description': 'Solution mining (in-situ leaching)', 'annotations': {'category': 'specialized', 'method': 'chemical dissolution'}},
    "HYDRAULIC_MINING": {'description': 'Hydraulic mining', 'annotations': {'category': 'specialized', 'method': 'high-pressure water'}},
    "ARTISANAL": {'description': 'Artisanal and small-scale mining', 'annotations': {'category': 'small-scale', 'equipment': 'minimal mechanization'}},
    "DEEP_SEA": {'description': 'Deep sea mining', 'annotations': {'category': 'marine', 'depth': 'ocean floor'}},
}

class MineralCategory(RichEnum):
    """
    Categories of minerals and materials
    """
    # Enum members
    PRECIOUS_METALS = "PRECIOUS_METALS"
    BASE_METALS = "BASE_METALS"
    FERROUS_METALS = "FERROUS_METALS"
    RARE_EARTH_ELEMENTS = "RARE_EARTH_ELEMENTS"
    RADIOACTIVE = "RADIOACTIVE"
    INDUSTRIAL_MINERALS = "INDUSTRIAL_MINERALS"
    GEMSTONES = "GEMSTONES"
    ENERGY_MINERALS = "ENERGY_MINERALS"
    CONSTRUCTION_MATERIALS = "CONSTRUCTION_MATERIALS"
    CHEMICAL_MINERALS = "CHEMICAL_MINERALS"

# Set metadata after class creation to avoid it becoming an enum member
MineralCategory._metadata = {
    "PRECIOUS_METALS": {'description': 'Precious metals', 'annotations': {'examples': 'gold, silver, platinum'}},
    "BASE_METALS": {'description': 'Base metals', 'annotations': {'examples': 'copper, lead, zinc, tin'}},
    "FERROUS_METALS": {'description': 'Ferrous metals', 'annotations': {'examples': 'iron, steel, manganese'}},
    "RARE_EARTH_ELEMENTS": {'description': 'Rare earth elements', 'annotations': {'examples': 'neodymium, dysprosium, cerium', 'count': '17 elements'}},
    "RADIOACTIVE": {'description': 'Radioactive minerals', 'annotations': {'examples': 'uranium, thorium, radium'}},
    "INDUSTRIAL_MINERALS": {'description': 'Industrial minerals', 'annotations': {'examples': 'limestone, gypsum, salt'}},
    "GEMSTONES": {'description': 'Gemstones', 'annotations': {'examples': 'diamond, ruby, emerald'}},
    "ENERGY_MINERALS": {'description': 'Energy minerals', 'annotations': {'examples': 'coal, oil shale, tar sands'}},
    "CONSTRUCTION_MATERIALS": {'description': 'Construction materials', 'annotations': {'examples': 'sand, gravel, crushed stone'}},
    "CHEMICAL_MINERALS": {'description': 'Chemical and fertilizer minerals', 'annotations': {'examples': 'phosphate, potash, sulfur'}},
}

class CriticalMineral(RichEnum):
    """
    Critical minerals essential for economic and national security,
particularly for clean energy, defense, and technology applications.
Based on US Geological Survey and EU critical raw materials lists.
    """
    # Enum members
    LITHIUM = "LITHIUM"
    COBALT = "COBALT"
    NICKEL = "NICKEL"
    GRAPHITE = "GRAPHITE"
    MANGANESE = "MANGANESE"
    NEODYMIUM = "NEODYMIUM"
    DYSPROSIUM = "DYSPROSIUM"
    PRASEODYMIUM = "PRASEODYMIUM"
    TERBIUM = "TERBIUM"
    EUROPIUM = "EUROPIUM"
    YTTRIUM = "YTTRIUM"
    CERIUM = "CERIUM"
    LANTHANUM = "LANTHANUM"
    GALLIUM = "GALLIUM"
    GERMANIUM = "GERMANIUM"
    INDIUM = "INDIUM"
    TELLURIUM = "TELLURIUM"
    ARSENIC = "ARSENIC"
    TITANIUM = "TITANIUM"
    VANADIUM = "VANADIUM"
    CHROMIUM = "CHROMIUM"
    TUNGSTEN = "TUNGSTEN"
    TANTALUM = "TANTALUM"
    NIOBIUM = "NIOBIUM"
    ZIRCONIUM = "ZIRCONIUM"
    HAFNIUM = "HAFNIUM"
    PLATINUM = "PLATINUM"
    PALLADIUM = "PALLADIUM"
    RHODIUM = "RHODIUM"
    IRIDIUM = "IRIDIUM"
    RUTHENIUM = "RUTHENIUM"
    ANTIMONY = "ANTIMONY"
    BISMUTH = "BISMUTH"
    BERYLLIUM = "BERYLLIUM"
    MAGNESIUM = "MAGNESIUM"
    ALUMINUM = "ALUMINUM"
    TIN = "TIN"
    FLUORSPAR = "FLUORSPAR"
    BARITE = "BARITE"
    HELIUM = "HELIUM"
    POTASH = "POTASH"
    PHOSPHATE_ROCK = "PHOSPHATE_ROCK"
    SCANDIUM = "SCANDIUM"
    STRONTIUM = "STRONTIUM"

# Set metadata after class creation to avoid it becoming an enum member
CriticalMineral._metadata = {
    "LITHIUM": {'description': 'Lithium (Li) - essential for batteries', 'meaning': 'CHEBI:30145', 'annotations': {'symbol': 'Li', 'atomic_number': 3, 'applications': 'batteries, ceramics, glass'}},
    "COBALT": {'description': 'Cobalt (Co) - battery cathodes and superalloys', 'meaning': 'CHEBI:27638', 'annotations': {'symbol': 'Co', 'atomic_number': 27, 'applications': 'batteries, superalloys, magnets'}},
    "NICKEL": {'description': 'Nickel (Ni) - stainless steel and batteries', 'meaning': 'CHEBI:28112', 'annotations': {'symbol': 'Ni', 'atomic_number': 28, 'applications': 'stainless steel, batteries, alloys'}},
    "GRAPHITE": {'description': 'Graphite - battery anodes and refractories', 'meaning': 'CHEBI:33418', 'annotations': {'formula': 'C', 'applications': 'batteries, lubricants, refractories'}},
    "MANGANESE": {'description': 'Manganese (Mn) - steel and battery production', 'meaning': 'CHEBI:18291', 'annotations': {'symbol': 'Mn', 'atomic_number': 25, 'applications': 'steel, batteries, aluminum alloys'}},
    "NEODYMIUM": {'description': 'Neodymium (Nd) - permanent magnets', 'meaning': 'CHEBI:33372', 'annotations': {'symbol': 'Nd', 'atomic_number': 60, 'category': 'light rare earth', 'applications': 'magnets, lasers, glass'}},
    "DYSPROSIUM": {'description': 'Dysprosium (Dy) - high-performance magnets', 'meaning': 'CHEBI:33377', 'annotations': {'symbol': 'Dy', 'atomic_number': 66, 'category': 'heavy rare earth', 'applications': 'magnets, nuclear control rods'}},
    "PRASEODYMIUM": {'description': 'Praseodymium (Pr) - magnets and alloys', 'meaning': 'CHEBI:49828', 'annotations': {'symbol': 'Pr', 'atomic_number': 59, 'category': 'light rare earth', 'applications': 'magnets, aircraft engines, glass'}},
    "TERBIUM": {'description': 'Terbium (Tb) - phosphors and magnets', 'meaning': 'CHEBI:33376', 'annotations': {'symbol': 'Tb', 'atomic_number': 65, 'category': 'heavy rare earth', 'applications': 'solid-state devices, fuel cells'}},
    "EUROPIUM": {'description': 'Europium (Eu) - phosphors and nuclear control', 'meaning': 'CHEBI:32999', 'annotations': {'symbol': 'Eu', 'atomic_number': 63, 'category': 'heavy rare earth', 'applications': 'LED phosphors, lasers'}},
    "YTTRIUM": {'description': 'Yttrium (Y) - phosphors and ceramics', 'meaning': 'CHEBI:33331', 'annotations': {'symbol': 'Y', 'atomic_number': 39, 'applications': 'LEDs, superconductors, ceramics'}},
    "CERIUM": {'description': 'Cerium (Ce) - catalysts and glass polishing', 'meaning': 'CHEBI:33369', 'annotations': {'symbol': 'Ce', 'atomic_number': 58, 'category': 'light rare earth', 'applications': 'catalysts, glass polishing, alloys'}},
    "LANTHANUM": {'description': 'Lanthanum (La) - catalysts and optics', 'meaning': 'CHEBI:33336', 'annotations': {'symbol': 'La', 'atomic_number': 57, 'category': 'light rare earth', 'applications': 'catalysts, optical glass, batteries'}},
    "GALLIUM": {'description': 'Gallium (Ga) - semiconductors and LEDs', 'meaning': 'CHEBI:49631', 'annotations': {'symbol': 'Ga', 'atomic_number': 31, 'applications': 'semiconductors, LEDs, solar cells'}},
    "GERMANIUM": {'description': 'Germanium (Ge) - fiber optics and infrared', 'meaning': 'CHEBI:30441', 'annotations': {'symbol': 'Ge', 'atomic_number': 32, 'applications': 'fiber optics, infrared optics, solar cells'}},
    "INDIUM": {'description': 'Indium (In) - displays and semiconductors', 'meaning': 'CHEBI:30430', 'annotations': {'symbol': 'In', 'atomic_number': 49, 'applications': 'LCD displays, semiconductors, solar panels'}},
    "TELLURIUM": {'description': 'Tellurium (Te) - solar panels and thermoelectrics', 'meaning': 'CHEBI:30452', 'annotations': {'symbol': 'Te', 'atomic_number': 52, 'applications': 'solar panels, thermoelectrics, alloys'}},
    "ARSENIC": {'description': 'Arsenic (As) - semiconductors and alloys', 'meaning': 'CHEBI:27563', 'annotations': {'symbol': 'As', 'atomic_number': 33, 'applications': 'semiconductors, wood preservatives'}},
    "TITANIUM": {'description': 'Titanium (Ti) - aerospace and defense', 'meaning': 'CHEBI:33341', 'annotations': {'symbol': 'Ti', 'atomic_number': 22, 'applications': 'aerospace, medical implants, pigments'}},
    "VANADIUM": {'description': 'Vanadium (V) - steel alloys and batteries', 'meaning': 'CHEBI:27698', 'annotations': {'symbol': 'V', 'atomic_number': 23, 'applications': 'steel alloys, flow batteries, catalysts'}},
    "CHROMIUM": {'description': 'Chromium (Cr) - stainless steel and alloys', 'meaning': 'CHEBI:28073', 'annotations': {'symbol': 'Cr', 'atomic_number': 24, 'applications': 'stainless steel, superalloys, plating'}},
    "TUNGSTEN": {'description': 'Tungsten (W) - hard metals and electronics', 'meaning': 'CHEBI:27998', 'annotations': {'symbol': 'W', 'atomic_number': 74, 'applications': 'cutting tools, electronics, alloys'}},
    "TANTALUM": {'description': 'Tantalum (Ta) - capacitors and superalloys', 'meaning': 'CHEBI:33348', 'annotations': {'symbol': 'Ta', 'atomic_number': 73, 'applications': 'capacitors, medical implants, superalloys'}},
    "NIOBIUM": {'description': 'Niobium (Nb) - steel alloys and superconductors', 'meaning': 'CHEBI:33344', 'annotations': {'symbol': 'Nb', 'atomic_number': 41, 'applications': 'steel alloys, superconductors, capacitors'}},
    "ZIRCONIUM": {'description': 'Zirconium (Zr) - nuclear and ceramics', 'meaning': 'CHEBI:33342', 'annotations': {'symbol': 'Zr', 'atomic_number': 40, 'applications': 'nuclear reactors, ceramics, alloys'}},
    "HAFNIUM": {'description': 'Hafnium (Hf) - nuclear and semiconductors', 'meaning': 'CHEBI:33343', 'annotations': {'symbol': 'Hf', 'atomic_number': 72, 'applications': 'nuclear control rods, superalloys'}},
    "PLATINUM": {'description': 'Platinum (Pt) - catalysts and electronics', 'meaning': 'CHEBI:33400', 'annotations': {'symbol': 'Pt', 'atomic_number': 78, 'category': 'PGM', 'applications': 'catalysts, jewelry, electronics'}},
    "PALLADIUM": {'description': 'Palladium (Pd) - catalysts and electronics', 'meaning': 'CHEBI:33363', 'annotations': {'symbol': 'Pd', 'atomic_number': 46, 'category': 'PGM', 'applications': 'catalysts, electronics, dentistry'}},
    "RHODIUM": {'description': 'Rhodium (Rh) - catalysts and electronics', 'meaning': 'CHEBI:33359', 'annotations': {'symbol': 'Rh', 'atomic_number': 45, 'category': 'PGM', 'applications': 'catalysts, electronics, glass'}},
    "IRIDIUM": {'description': 'Iridium (Ir) - electronics and catalysts', 'meaning': 'CHEBI:49666', 'annotations': {'symbol': 'Ir', 'atomic_number': 77, 'category': 'PGM', 'applications': 'spark plugs, electronics, catalysts'}},
    "RUTHENIUM": {'description': 'Ruthenium (Ru) - electronics and catalysts', 'meaning': 'CHEBI:30682', 'annotations': {'symbol': 'Ru', 'atomic_number': 44, 'category': 'PGM', 'applications': 'electronics, catalysts, solar cells'}},
    "ANTIMONY": {'description': 'Antimony (Sb) - flame retardants and batteries', 'meaning': 'CHEBI:30513', 'annotations': {'symbol': 'Sb', 'atomic_number': 51, 'applications': 'flame retardants, batteries, alloys'}},
    "BISMUTH": {'description': 'Bismuth (Bi) - pharmaceuticals and alloys', 'meaning': 'CHEBI:33301', 'annotations': {'symbol': 'Bi', 'atomic_number': 83, 'applications': 'pharmaceuticals, cosmetics, alloys'}},
    "BERYLLIUM": {'description': 'Beryllium (Be) - aerospace and defense', 'meaning': 'CHEBI:30501', 'annotations': {'symbol': 'Be', 'atomic_number': 4, 'applications': 'aerospace, defense, nuclear'}},
    "MAGNESIUM": {'description': 'Magnesium (Mg) - lightweight alloys', 'meaning': 'CHEBI:25107', 'annotations': {'symbol': 'Mg', 'atomic_number': 12, 'applications': 'alloys, automotive, aerospace'}},
    "ALUMINUM": {'description': 'Aluminum (Al) - construction and transportation', 'meaning': 'CHEBI:28984', 'annotations': {'symbol': 'Al', 'atomic_number': 13, 'applications': 'construction, transportation, packaging'}},
    "TIN": {'description': 'Tin (Sn) - solders and coatings', 'meaning': 'CHEBI:27007', 'annotations': {'symbol': 'Sn', 'atomic_number': 50, 'applications': 'solders, coatings, alloys'}},
    "FLUORSPAR": {'description': 'Fluorspar (CaF2) - steel and aluminum production', 'meaning': 'CHEBI:35437', 'annotations': {'formula': 'CaF2', 'mineral_name': 'fluorite', 'applications': 'steel, aluminum, refrigerants'}},
    "BARITE": {'description': 'Barite (BaSO4) - drilling and chemicals', 'meaning': 'CHEBI:133326', 'annotations': {'formula': 'BaSO4', 'applications': 'oil drilling, chemicals, radiation shielding'}},
    "HELIUM": {'description': 'Helium (He) - cryogenics and electronics', 'meaning': 'CHEBI:33681', 'annotations': {'symbol': 'He', 'atomic_number': 2, 'applications': 'MRI, semiconductors, aerospace'}},
    "POTASH": {'description': 'Potash (K2O) - fertilizers and chemicals', 'meaning': 'CHEBI:88321', 'annotations': {'formula': 'K2O', 'applications': 'fertilizers, chemicals, glass'}},
    "PHOSPHATE_ROCK": {'description': 'Phosphate rock - fertilizers and chemicals', 'meaning': 'CHEBI:26020', 'annotations': {'applications': 'fertilizers, food additives, chemicals'}},
    "SCANDIUM": {'description': 'Scandium (Sc) - aerospace alloys', 'meaning': 'CHEBI:33330', 'annotations': {'symbol': 'Sc', 'atomic_number': 21, 'applications': 'aerospace alloys, solid oxide fuel cells'}},
    "STRONTIUM": {'description': 'Strontium (Sr) - magnets and pyrotechnics', 'meaning': 'CHEBI:33324', 'annotations': {'symbol': 'Sr', 'atomic_number': 38, 'applications': 'magnets, pyrotechnics, medical'}},
}

class CommonMineral(RichEnum):
    """
    Common minerals extracted through mining
    """
    # Enum members
    GOLD = "GOLD"
    SILVER = "SILVER"
    PLATINUM = "PLATINUM"
    COPPER = "COPPER"
    IRON = "IRON"
    ALUMINUM = "ALUMINUM"
    ZINC = "ZINC"
    LEAD = "LEAD"
    NICKEL = "NICKEL"
    TIN = "TIN"
    COAL = "COAL"
    URANIUM = "URANIUM"
    LIMESTONE = "LIMESTONE"
    SALT = "SALT"
    PHOSPHATE = "PHOSPHATE"
    POTASH = "POTASH"
    LITHIUM = "LITHIUM"
    COBALT = "COBALT"
    DIAMOND = "DIAMOND"

# Set metadata after class creation to avoid it becoming an enum member
CommonMineral._metadata = {
    "GOLD": {'description': 'Gold (Au)', 'meaning': 'CHEBI:29287', 'annotations': {'symbol': 'Au', 'atomic_number': 79}},
    "SILVER": {'description': 'Silver (Ag)', 'meaning': 'CHEBI:30512', 'annotations': {'symbol': 'Ag', 'atomic_number': 47}},
    "PLATINUM": {'description': 'Platinum (Pt)', 'meaning': 'CHEBI:49202', 'annotations': {'symbol': 'Pt', 'atomic_number': 78}},
    "COPPER": {'description': 'Copper (Cu)', 'meaning': 'CHEBI:28694', 'annotations': {'symbol': 'Cu', 'atomic_number': 29}},
    "IRON": {'description': 'Iron (Fe)', 'meaning': 'CHEBI:18248', 'annotations': {'symbol': 'Fe', 'atomic_number': 26}},
    "ALUMINUM": {'description': 'Aluminum (Al)', 'meaning': 'CHEBI:28984', 'annotations': {'symbol': 'Al', 'atomic_number': 13, 'ore': 'bauxite'}},
    "ZINC": {'description': 'Zinc (Zn)', 'meaning': 'CHEBI:27363', 'annotations': {'symbol': 'Zn', 'atomic_number': 30}},
    "LEAD": {'description': 'Lead (Pb)', 'meaning': 'CHEBI:25016', 'annotations': {'symbol': 'Pb', 'atomic_number': 82}},
    "NICKEL": {'description': 'Nickel (Ni)', 'meaning': 'CHEBI:28112', 'annotations': {'symbol': 'Ni', 'atomic_number': 28}},
    "TIN": {'description': 'Tin (Sn)', 'meaning': 'CHEBI:27007', 'annotations': {'symbol': 'Sn', 'atomic_number': 50}},
    "COAL": {'description': 'Coal', 'meaning': 'ENVO:02000091', 'annotations': {'types': 'anthracite, bituminous, lignite'}},
    "URANIUM": {'description': 'Uranium (U)', 'meaning': 'CHEBI:27214', 'annotations': {'symbol': 'U', 'atomic_number': 92}},
    "LIMESTONE": {'description': 'Limestone (CaCO3)', 'meaning': 'ENVO:00002053', 'annotations': {'formula': 'CaCO3', 'use': 'cement, steel production'}},
    "SALT": {'description': 'Salt (NaCl)', 'meaning': 'CHEBI:24866', 'annotations': {'formula': 'NaCl', 'aliases': 'halite, rock salt'}},
    "PHOSPHATE": {'description': 'Phosphate rock', 'meaning': 'CHEBI:26020', 'annotations': {'use': 'fertilizer production'}},
    "POTASH": {'description': 'Potash (K2O)', 'meaning': 'CHEBI:88321', 'annotations': {'formula': 'K2O', 'use': 'fertilizer'}},
    "LITHIUM": {'description': 'Lithium (Li)', 'meaning': 'CHEBI:30145', 'annotations': {'symbol': 'Li', 'atomic_number': 3, 'use': 'batteries'}},
    "COBALT": {'description': 'Cobalt (Co)', 'meaning': 'CHEBI:27638', 'annotations': {'symbol': 'Co', 'atomic_number': 27, 'use': 'batteries, alloys'}},
    "DIAMOND": {'description': 'Diamond (C)', 'meaning': 'CHEBI:33417', 'annotations': {'formula': 'C', 'use': 'gemstone, industrial'}},
}

class MiningEquipment(RichEnum):
    """
    Types of mining equipment
    """
    # Enum members
    DRILL_RIG = "DRILL_RIG"
    JUMBO_DRILL = "JUMBO_DRILL"
    EXCAVATOR = "EXCAVATOR"
    DRAGLINE = "DRAGLINE"
    BUCKET_WHEEL_EXCAVATOR = "BUCKET_WHEEL_EXCAVATOR"
    HAUL_TRUCK = "HAUL_TRUCK"
    LOADER = "LOADER"
    CONVEYOR = "CONVEYOR"
    CRUSHER = "CRUSHER"
    BALL_MILL = "BALL_MILL"
    FLOTATION_CELL = "FLOTATION_CELL"
    CONTINUOUS_MINER = "CONTINUOUS_MINER"
    ROOF_BOLTER = "ROOF_BOLTER"
    SHUTTLE_CAR = "SHUTTLE_CAR"

# Set metadata after class creation to avoid it becoming an enum member
MiningEquipment._metadata = {
    "DRILL_RIG": {'description': 'Drilling rig', 'annotations': {'category': 'drilling'}},
    "JUMBO_DRILL": {'description': 'Jumbo drill', 'annotations': {'category': 'drilling', 'use': 'underground'}},
    "EXCAVATOR": {'description': 'Excavator', 'annotations': {'category': 'excavation'}},
    "DRAGLINE": {'description': 'Dragline excavator', 'annotations': {'category': 'excavation', 'size': 'large-scale'}},
    "BUCKET_WHEEL_EXCAVATOR": {'description': 'Bucket-wheel excavator', 'annotations': {'category': 'excavation', 'use': 'continuous mining'}},
    "HAUL_TRUCK": {'description': 'Haul truck', 'annotations': {'category': 'hauling', 'capacity': 'up to 400 tons'}},
    "LOADER": {'description': 'Loader', 'annotations': {'category': 'loading'}},
    "CONVEYOR": {'description': 'Conveyor system', 'annotations': {'category': 'transport'}},
    "CRUSHER": {'description': 'Crusher', 'annotations': {'category': 'processing', 'types': 'jaw, cone, impact'}},
    "BALL_MILL": {'description': 'Ball mill', 'annotations': {'category': 'processing', 'use': 'grinding'}},
    "FLOTATION_CELL": {'description': 'Flotation cell', 'annotations': {'category': 'processing', 'use': 'mineral separation'}},
    "CONTINUOUS_MINER": {'description': 'Continuous miner', 'annotations': {'category': 'underground'}},
    "ROOF_BOLTER": {'description': 'Roof bolter', 'annotations': {'category': 'underground', 'use': 'support installation'}},
    "SHUTTLE_CAR": {'description': 'Shuttle car', 'annotations': {'category': 'underground transport'}},
}

class OreGrade(RichEnum):
    """
    Classification of ore grades
    """
    # Enum members
    HIGH_GRADE = "HIGH_GRADE"
    MEDIUM_GRADE = "MEDIUM_GRADE"
    LOW_GRADE = "LOW_GRADE"
    MARGINAL = "MARGINAL"
    SUB_ECONOMIC = "SUB_ECONOMIC"
    WASTE = "WASTE"

# Set metadata after class creation to avoid it becoming an enum member
OreGrade._metadata = {
    "HIGH_GRADE": {'description': 'High-grade ore', 'annotations': {'concentration': 'high', 'processing': 'minimal required'}},
    "MEDIUM_GRADE": {'description': 'Medium-grade ore', 'annotations': {'concentration': 'moderate'}},
    "LOW_GRADE": {'description': 'Low-grade ore', 'annotations': {'concentration': 'low', 'processing': 'extensive required'}},
    "MARGINAL": {'description': 'Marginal ore', 'annotations': {'economics': 'borderline profitable'}},
    "SUB_ECONOMIC": {'description': 'Sub-economic ore', 'annotations': {'economics': 'not currently profitable'}},
    "WASTE": {'description': 'Waste rock', 'annotations': {'concentration': 'below cutoff'}},
}

class MiningPhase(RichEnum):
    """
    Phases of mining operations
    """
    # Enum members
    EXPLORATION = "EXPLORATION"
    DEVELOPMENT = "DEVELOPMENT"
    PRODUCTION = "PRODUCTION"
    PROCESSING = "PROCESSING"
    CLOSURE = "CLOSURE"
    RECLAMATION = "RECLAMATION"
    POST_CLOSURE = "POST_CLOSURE"

# Set metadata after class creation to avoid it becoming an enum member
MiningPhase._metadata = {
    "EXPLORATION": {'description': 'Exploration phase', 'annotations': {'activities': 'prospecting, sampling, drilling'}},
    "DEVELOPMENT": {'description': 'Development phase', 'annotations': {'activities': 'infrastructure, access roads'}},
    "PRODUCTION": {'description': 'Production/extraction phase', 'annotations': {'activities': 'active mining'}},
    "PROCESSING": {'description': 'Processing/beneficiation phase', 'annotations': {'activities': 'crushing, milling, concentration'}},
    "CLOSURE": {'description': 'Closure phase', 'annotations': {'activities': 'decommissioning, capping'}},
    "RECLAMATION": {'description': 'Reclamation phase', 'annotations': {'activities': 'restoration, revegetation'}},
    "POST_CLOSURE": {'description': 'Post-closure monitoring', 'annotations': {'activities': 'long-term monitoring'}},
}

class MiningHazard(RichEnum):
    """
    Mining-related hazards and risks
    """
    # Enum members
    CAVE_IN = "CAVE_IN"
    GAS_EXPLOSION = "GAS_EXPLOSION"
    FLOODING = "FLOODING"
    DUST_EXPOSURE = "DUST_EXPOSURE"
    CHEMICAL_EXPOSURE = "CHEMICAL_EXPOSURE"
    RADIATION = "RADIATION"
    NOISE = "NOISE"
    VIBRATION = "VIBRATION"
    HEAT_STRESS = "HEAT_STRESS"
    EQUIPMENT_ACCIDENT = "EQUIPMENT_ACCIDENT"

# Set metadata after class creation to avoid it becoming an enum member
MiningHazard._metadata = {
    "CAVE_IN": {'description': 'Cave-in/roof collapse', 'annotations': {'type': 'structural'}},
    "GAS_EXPLOSION": {'description': 'Gas explosion', 'annotations': {'type': 'chemical', 'gases': 'methane, coal dust'}},
    "FLOODING": {'description': 'Mine flooding', 'annotations': {'type': 'water'}},
    "DUST_EXPOSURE": {'description': 'Dust exposure', 'annotations': {'type': 'respiratory', 'diseases': 'silicosis, pneumoconiosis'}},
    "CHEMICAL_EXPOSURE": {'description': 'Chemical exposure', 'annotations': {'type': 'toxic', 'chemicals': 'mercury, cyanide, acids'}},
    "RADIATION": {'description': 'Radiation exposure', 'annotations': {'type': 'radioactive', 'source': 'uranium, radon'}},
    "NOISE": {'description': 'Noise exposure', 'annotations': {'type': 'physical'}},
    "VIBRATION": {'description': 'Vibration exposure', 'annotations': {'type': 'physical'}},
    "HEAT_STRESS": {'description': 'Heat stress', 'annotations': {'type': 'thermal'}},
    "EQUIPMENT_ACCIDENT": {'description': 'Equipment-related accident', 'annotations': {'type': 'mechanical'}},
}

class EnvironmentalImpact(RichEnum):
    """
    Environmental impacts of mining
    """
    # Enum members
    HABITAT_DESTRUCTION = "HABITAT_DESTRUCTION"
    WATER_POLLUTION = "WATER_POLLUTION"
    AIR_POLLUTION = "AIR_POLLUTION"
    SOIL_CONTAMINATION = "SOIL_CONTAMINATION"
    DEFORESTATION = "DEFORESTATION"
    EROSION = "EROSION"
    ACID_MINE_DRAINAGE = "ACID_MINE_DRAINAGE"
    TAILINGS = "TAILINGS"
    SUBSIDENCE = "SUBSIDENCE"
    BIODIVERSITY_LOSS = "BIODIVERSITY_LOSS"

# Set metadata after class creation to avoid it becoming an enum member
EnvironmentalImpact._metadata = {
    "HABITAT_DESTRUCTION": {'description': 'Habitat destruction', 'meaning': 'ExO:0000012'},
    "WATER_POLLUTION": {'description': 'Water pollution', 'meaning': 'ENVO:02500039', 'annotations': {'types': 'acid mine drainage, heavy metals'}},
    "AIR_POLLUTION": {'description': 'Air pollution', 'meaning': 'ENVO:02500037', 'annotations': {'sources': 'dust, emissions'}},
    "SOIL_CONTAMINATION": {'description': 'Soil contamination', 'meaning': 'ENVO:00002116'},
    "DEFORESTATION": {'description': 'Deforestation', 'meaning': 'ENVO:02500012'},
    "EROSION": {'description': 'Erosion and sedimentation', 'meaning': 'ENVO:01001346'},
    "ACID_MINE_DRAINAGE": {'description': 'Acid mine drainage', 'meaning': 'ENVO:00001997'},
    "TAILINGS": {'description': 'Tailings contamination', 'annotations': {'storage': 'tailings ponds, dams'}},
    "SUBSIDENCE": {'description': 'Ground subsidence', 'annotations': {'cause': 'underground voids'}},
    "BIODIVERSITY_LOSS": {'description': 'Biodiversity loss', 'annotations': {'impact': 'species extinction, ecosystem disruption'}},
}

class ExtractiveIndustryFacilityTypeEnum(RichEnum):
    """
    Types of extractive industry facilities
    """
    # Enum members
    MINING_FACILITY = "MINING_FACILITY"
    WELL_FACILITY = "WELL_FACILITY"
    QUARRY_FACILITY = "QUARRY_FACILITY"

# Set metadata after class creation to avoid it becoming an enum member
ExtractiveIndustryFacilityTypeEnum._metadata = {
    "MINING_FACILITY": {'description': 'A facility where mineral resources are extracted'},
    "WELL_FACILITY": {'description': 'A facility where fluid resources are extracted'},
    "QUARRY_FACILITY": {'description': 'A facility where stone, sand, or gravel are extracted'},
}

class ExtractiveIndustryProductTypeEnum(RichEnum):
    """
    Types of products extracted from extractive industry facilities
    """
    # Enum members
    MINERAL = "MINERAL"
    METAL = "METAL"
    COAL = "COAL"
    OIL = "OIL"
    GAS = "GAS"
    STONE = "STONE"
    SAND = "SAND"
    GRAVEL = "GRAVEL"

# Set metadata after class creation to avoid it becoming an enum member
ExtractiveIndustryProductTypeEnum._metadata = {
    "MINERAL": {'description': 'A solid inorganic substance'},
    "METAL": {'description': 'A solid metallic substance'},
    "COAL": {'description': 'A combustible black or brownish-black sedimentary rock'},
    "OIL": {'description': 'A liquid petroleum resource'},
    "GAS": {'description': 'A gaseous petroleum resource'},
    "STONE": {'description': 'A solid aggregate of minerals'},
    "SAND": {'description': 'A granular material composed of finely divided rock and mineral particles'},
    "GRAVEL": {'description': 'A loose aggregation of rock fragments'},
}

class MiningMethodEnum(RichEnum):
    """
    Methods used for extracting minerals from the earth
    """
    # Enum members
    UNDERGROUND = "UNDERGROUND"
    OPEN_PIT = "OPEN_PIT"
    PLACER = "PLACER"
    IN_SITU = "IN_SITU"

# Set metadata after class creation to avoid it becoming an enum member
MiningMethodEnum._metadata = {
    "UNDERGROUND": {'description': "Extraction occurs beneath the earth's surface"},
    "OPEN_PIT": {'description': "Extraction occurs on the earth's surface"},
    "PLACER": {'description': 'Extraction of valuable minerals from alluvial deposits'},
    "IN_SITU": {'description': 'Extraction without removing the ore from its original location'},
}

class WellTypeEnum(RichEnum):
    """
    Types of wells used for extracting fluid resources
    """
    # Enum members
    OIL = "OIL"
    GAS = "GAS"
    WATER = "WATER"
    INJECTION = "INJECTION"

# Set metadata after class creation to avoid it becoming an enum member
WellTypeEnum._metadata = {
    "OIL": {'description': 'A well that primarily extracts crude oil'},
    "GAS": {'description': 'A well that primarily extracts natural gas'},
    "WATER": {'description': 'A well that extracts water for various purposes'},
    "INJECTION": {'description': 'A well used to inject fluids into underground formations'},
}

class OutcomeTypeEnum(RichEnum):
    """
    Types of prediction outcomes for classification tasks
    """
    # Enum members
    TP = "TP"
    FP = "FP"
    TN = "TN"
    FN = "FN"

# Set metadata after class creation to avoid it becoming an enum member
OutcomeTypeEnum._metadata = {
    "TP": {'description': 'True Positive'},
    "FP": {'description': 'False Positive'},
    "TN": {'description': 'True Negative'},
    "FN": {'description': 'False Negative'},
}

class PersonStatusEnum(RichEnum):
    """
    Vital status of a person (living or deceased)
    """
    # Enum members
    ALIVE = "ALIVE"
    DEAD = "DEAD"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
PersonStatusEnum._metadata = {
    "ALIVE": {'description': 'The person is living', 'meaning': 'PATO:0001421'},
    "DEAD": {'description': 'The person is deceased', 'meaning': 'PATO:0001422'},
    "UNKNOWN": {'description': 'The vital status is not known', 'meaning': 'NCIT:C17998'},
}

class MimeType(RichEnum):
    """
    Common MIME types for various file formats
    """
    # Enum members
    APPLICATION_JSON = "APPLICATION_JSON"
    APPLICATION_XML = "APPLICATION_XML"
    APPLICATION_PDF = "APPLICATION_PDF"
    APPLICATION_ZIP = "APPLICATION_ZIP"
    APPLICATION_GZIP = "APPLICATION_GZIP"
    APPLICATION_OCTET_STREAM = "APPLICATION_OCTET_STREAM"
    APPLICATION_X_WWW_FORM_URLENCODED = "APPLICATION_X_WWW_FORM_URLENCODED"
    APPLICATION_VND_MS_EXCEL = "APPLICATION_VND_MS_EXCEL"
    APPLICATION_VND_OPENXMLFORMATS_SPREADSHEET = "APPLICATION_VND_OPENXMLFORMATS_SPREADSHEET"
    APPLICATION_VND_MS_POWERPOINT = "APPLICATION_VND_MS_POWERPOINT"
    APPLICATION_MSWORD = "APPLICATION_MSWORD"
    APPLICATION_VND_OPENXMLFORMATS_DOCUMENT = "APPLICATION_VND_OPENXMLFORMATS_DOCUMENT"
    APPLICATION_JAVASCRIPT = "APPLICATION_JAVASCRIPT"
    APPLICATION_TYPESCRIPT = "APPLICATION_TYPESCRIPT"
    APPLICATION_SQL = "APPLICATION_SQL"
    APPLICATION_GRAPHQL = "APPLICATION_GRAPHQL"
    APPLICATION_LD_JSON = "APPLICATION_LD_JSON"
    APPLICATION_WASM = "APPLICATION_WASM"
    TEXT_PLAIN = "TEXT_PLAIN"
    TEXT_HTML = "TEXT_HTML"
    TEXT_CSS = "TEXT_CSS"
    TEXT_CSV = "TEXT_CSV"
    TEXT_MARKDOWN = "TEXT_MARKDOWN"
    TEXT_YAML = "TEXT_YAML"
    TEXT_X_PYTHON = "TEXT_X_PYTHON"
    TEXT_X_JAVA = "TEXT_X_JAVA"
    TEXT_X_C = "TEXT_X_C"
    TEXT_X_CPP = "TEXT_X_CPP"
    TEXT_X_CSHARP = "TEXT_X_CSHARP"
    TEXT_X_GO = "TEXT_X_GO"
    TEXT_X_RUST = "TEXT_X_RUST"
    TEXT_X_RUBY = "TEXT_X_RUBY"
    TEXT_X_SHELLSCRIPT = "TEXT_X_SHELLSCRIPT"
    IMAGE_JPEG = "IMAGE_JPEG"
    IMAGE_PNG = "IMAGE_PNG"
    IMAGE_GIF = "IMAGE_GIF"
    IMAGE_SVG_XML = "IMAGE_SVG_XML"
    IMAGE_WEBP = "IMAGE_WEBP"
    IMAGE_BMP = "IMAGE_BMP"
    IMAGE_ICO = "IMAGE_ICO"
    IMAGE_TIFF = "IMAGE_TIFF"
    IMAGE_AVIF = "IMAGE_AVIF"
    AUDIO_MPEG = "AUDIO_MPEG"
    AUDIO_WAV = "AUDIO_WAV"
    AUDIO_OGG = "AUDIO_OGG"
    AUDIO_WEBM = "AUDIO_WEBM"
    AUDIO_AAC = "AUDIO_AAC"
    VIDEO_MP4 = "VIDEO_MP4"
    VIDEO_MPEG = "VIDEO_MPEG"
    VIDEO_WEBM = "VIDEO_WEBM"
    VIDEO_OGG = "VIDEO_OGG"
    VIDEO_QUICKTIME = "VIDEO_QUICKTIME"
    VIDEO_AVI = "VIDEO_AVI"
    FONT_WOFF = "FONT_WOFF"
    FONT_WOFF2 = "FONT_WOFF2"
    FONT_TTF = "FONT_TTF"
    FONT_OTF = "FONT_OTF"
    MULTIPART_FORM_DATA = "MULTIPART_FORM_DATA"
    MULTIPART_MIXED = "MULTIPART_MIXED"

# Set metadata after class creation to avoid it becoming an enum member
MimeType._metadata = {
    "APPLICATION_JSON": {'description': 'JSON format', 'meaning': 'iana:application/json'},
    "APPLICATION_XML": {'description': 'XML format', 'meaning': 'iana:application/xml'},
    "APPLICATION_PDF": {'description': 'Adobe Portable Document Format', 'meaning': 'iana:application/pdf'},
    "APPLICATION_ZIP": {'description': 'ZIP archive', 'meaning': 'iana:application/zip'},
    "APPLICATION_GZIP": {'description': 'GZIP compressed archive', 'meaning': 'iana:application/gzip'},
    "APPLICATION_OCTET_STREAM": {'description': 'Binary data', 'meaning': 'iana:application/octet-stream'},
    "APPLICATION_X_WWW_FORM_URLENCODED": {'description': 'Form data encoded', 'meaning': 'iana:application/x-www-form-urlencoded'},
    "APPLICATION_VND_MS_EXCEL": {'description': 'Microsoft Excel', 'meaning': 'iana:application/vnd.ms-excel'},
    "APPLICATION_VND_OPENXMLFORMATS_SPREADSHEET": {'description': 'Microsoft Excel (OpenXML)', 'meaning': 'iana:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
    "APPLICATION_VND_MS_POWERPOINT": {'description': 'Microsoft PowerPoint', 'meaning': 'iana:application/vnd.ms-powerpoint'},
    "APPLICATION_MSWORD": {'description': 'Microsoft Word', 'meaning': 'iana:application/msword'},
    "APPLICATION_VND_OPENXMLFORMATS_DOCUMENT": {'description': 'Microsoft Word (OpenXML)', 'meaning': 'iana:application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
    "APPLICATION_JAVASCRIPT": {'description': 'JavaScript', 'meaning': 'iana:application/javascript'},
    "APPLICATION_TYPESCRIPT": {'description': 'TypeScript source code', 'meaning': 'iana:application/typescript'},
    "APPLICATION_SQL": {'description': 'SQL database format', 'meaning': 'iana:application/sql'},
    "APPLICATION_GRAPHQL": {'description': 'GraphQL query language', 'meaning': 'iana:application/graphql'},
    "APPLICATION_LD_JSON": {'description': 'JSON-LD format', 'meaning': 'iana:application/ld+json'},
    "APPLICATION_WASM": {'description': 'WebAssembly binary format', 'meaning': 'iana:application/wasm'},
    "TEXT_PLAIN": {'description': 'Plain text', 'meaning': 'iana:text/plain'},
    "TEXT_HTML": {'description': 'HTML document', 'meaning': 'iana:text/html'},
    "TEXT_CSS": {'description': 'Cascading Style Sheets', 'meaning': 'iana:text/css'},
    "TEXT_CSV": {'description': 'Comma-separated values', 'meaning': 'iana:text/csv'},
    "TEXT_MARKDOWN": {'description': 'Markdown format', 'meaning': 'iana:text/markdown'},
    "TEXT_YAML": {'description': 'YAML format', 'meaning': 'iana:text/yaml'},
    "TEXT_X_PYTHON": {'description': 'Python source code', 'meaning': 'iana:text/x-python'},
    "TEXT_X_JAVA": {'description': 'Java source code', 'meaning': 'iana:text/x-java-source'},
    "TEXT_X_C": {'description': 'C source code', 'meaning': 'iana:text/x-c'},
    "TEXT_X_CPP": {'description': 'C++ source code', 'meaning': 'iana:text/x-c++'},
    "TEXT_X_CSHARP": {'description': 'C# source code', 'meaning': 'iana:text/x-csharp'},
    "TEXT_X_GO": {'description': 'Go source code', 'meaning': 'iana:text/x-go'},
    "TEXT_X_RUST": {'description': 'Rust source code', 'meaning': 'iana:text/x-rust'},
    "TEXT_X_RUBY": {'description': 'Ruby source code', 'meaning': 'iana:text/x-ruby'},
    "TEXT_X_SHELLSCRIPT": {'description': 'Shell script', 'meaning': 'iana:text/x-shellscript'},
    "IMAGE_JPEG": {'description': 'JPEG image', 'meaning': 'iana:image/jpeg'},
    "IMAGE_PNG": {'description': 'PNG image', 'meaning': 'iana:image/png'},
    "IMAGE_GIF": {'description': 'GIF image', 'meaning': 'iana:image/gif'},
    "IMAGE_SVG_XML": {'description': 'SVG vector image', 'meaning': 'iana:image/svg+xml'},
    "IMAGE_WEBP": {'description': 'WebP image', 'meaning': 'iana:image/webp'},
    "IMAGE_BMP": {'description': 'Bitmap image', 'meaning': 'iana:image/bmp'},
    "IMAGE_ICO": {'description': 'Icon format', 'meaning': 'iana:image/vnd.microsoft.icon'},
    "IMAGE_TIFF": {'description': 'TIFF image', 'meaning': 'iana:image/tiff'},
    "IMAGE_AVIF": {'description': 'AVIF image format', 'meaning': 'iana:image/avif'},
    "AUDIO_MPEG": {'description': 'MP3 audio', 'meaning': 'iana:audio/mpeg'},
    "AUDIO_WAV": {'description': 'WAV audio', 'meaning': 'iana:audio/wav'},
    "AUDIO_OGG": {'description': 'OGG audio', 'meaning': 'iana:audio/ogg'},
    "AUDIO_WEBM": {'description': 'WebM audio', 'meaning': 'iana:audio/webm'},
    "AUDIO_AAC": {'description': 'AAC audio', 'meaning': 'iana:audio/aac'},
    "VIDEO_MP4": {'description': 'MP4 video', 'meaning': 'iana:video/mp4'},
    "VIDEO_MPEG": {'description': 'MPEG video', 'meaning': 'iana:video/mpeg'},
    "VIDEO_WEBM": {'description': 'WebM video', 'meaning': 'iana:video/webm'},
    "VIDEO_OGG": {'description': 'OGG video', 'meaning': 'iana:video/ogg'},
    "VIDEO_QUICKTIME": {'description': 'QuickTime video', 'meaning': 'iana:video/quicktime'},
    "VIDEO_AVI": {'description': 'AVI video', 'meaning': 'iana:video/x-msvideo'},
    "FONT_WOFF": {'description': 'Web Open Font Format', 'meaning': 'iana:font/woff'},
    "FONT_WOFF2": {'description': 'Web Open Font Format 2', 'meaning': 'iana:font/woff2'},
    "FONT_TTF": {'description': 'TrueType Font', 'meaning': 'iana:font/ttf'},
    "FONT_OTF": {'description': 'OpenType Font', 'meaning': 'iana:font/otf'},
    "MULTIPART_FORM_DATA": {'description': 'Form data with file upload', 'meaning': 'iana:multipart/form-data'},
    "MULTIPART_MIXED": {'description': 'Mixed multipart message', 'meaning': 'iana:multipart/mixed'},
}

class MimeTypeCategory(RichEnum):
    """
    Categories of MIME types
    """
    # Enum members
    APPLICATION = "APPLICATION"
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    FONT = "FONT"
    MULTIPART = "MULTIPART"
    MESSAGE = "MESSAGE"
    MODEL = "MODEL"

# Set metadata after class creation to avoid it becoming an enum member
MimeTypeCategory._metadata = {
    "APPLICATION": {'description': 'Application data'},
    "TEXT": {'description': 'Text documents'},
    "IMAGE": {'description': 'Image files'},
    "AUDIO": {'description': 'Audio files'},
    "VIDEO": {'description': 'Video files'},
    "FONT": {'description': 'Font files'},
    "MULTIPART": {'description': 'Multipart messages'},
    "MESSAGE": {'description': 'Message formats'},
    "MODEL": {'description': '3D models and similar'},
}

class TextCharset(RichEnum):
    """
    Character encodings for text content
    """
    # Enum members
    UTF_8 = "UTF_8"
    UTF_16 = "UTF_16"
    UTF_32 = "UTF_32"
    ASCII = "ASCII"
    ISO_8859_1 = "ISO_8859_1"
    ISO_8859_2 = "ISO_8859_2"
    WINDOWS_1252 = "WINDOWS_1252"
    GB2312 = "GB2312"
    SHIFT_JIS = "SHIFT_JIS"
    EUC_KR = "EUC_KR"
    BIG5 = "BIG5"

# Set metadata after class creation to avoid it becoming an enum member
TextCharset._metadata = {
    "UTF_8": {'description': 'UTF-8 Unicode encoding'},
    "UTF_16": {'description': 'UTF-16 Unicode encoding'},
    "UTF_32": {'description': 'UTF-32 Unicode encoding'},
    "ASCII": {'description': 'ASCII encoding'},
    "ISO_8859_1": {'description': 'ISO-8859-1 (Latin-1) encoding'},
    "ISO_8859_2": {'description': 'ISO-8859-2 (Latin-2) encoding'},
    "WINDOWS_1252": {'description': 'Windows-1252 encoding'},
    "GB2312": {'description': 'Simplified Chinese encoding'},
    "SHIFT_JIS": {'description': 'Japanese encoding'},
    "EUC_KR": {'description': 'Korean encoding'},
    "BIG5": {'description': 'Traditional Chinese encoding'},
}

class CompressionType(RichEnum):
    """
    Compression types used with Content-Encoding
    """
    # Enum members
    GZIP = "GZIP"
    DEFLATE = "DEFLATE"
    BR = "BR"
    COMPRESS = "COMPRESS"
    IDENTITY = "IDENTITY"

# Set metadata after class creation to avoid it becoming an enum member
CompressionType._metadata = {
    "GZIP": {'description': 'GZIP compression'},
    "DEFLATE": {'description': 'DEFLATE compression'},
    "BR": {'description': 'Brotli compression'},
    "COMPRESS": {'description': 'Unix compress'},
    "IDENTITY": {'description': 'No compression'},
}

class StateOfMatterEnum(RichEnum):
    """
    The physical state or phase of matter
    """
    # Enum members
    SOLID = "SOLID"
    LIQUID = "LIQUID"
    GAS = "GAS"
    PLASMA = "PLASMA"
    BOSE_EINSTEIN_CONDENSATE = "BOSE_EINSTEIN_CONDENSATE"
    FERMIONIC_CONDENSATE = "FERMIONIC_CONDENSATE"
    SUPERCRITICAL_FLUID = "SUPERCRITICAL_FLUID"
    SUPERFLUID = "SUPERFLUID"
    SUPERSOLID = "SUPERSOLID"
    QUARK_GLUON_PLASMA = "QUARK_GLUON_PLASMA"

# Set metadata after class creation to avoid it becoming an enum member
StateOfMatterEnum._metadata = {
    "SOLID": {'description': 'A state of matter where particles are closely packed together with fixed positions', 'meaning': 'AFO:AFQ_0000112'},
    "LIQUID": {'description': 'A nearly incompressible fluid that conforms to the shape of its container', 'meaning': 'AFO:AFQ_0000113'},
    "GAS": {'description': 'A compressible fluid that expands to fill its container', 'meaning': 'AFO:AFQ_0000114'},
    "PLASMA": {'description': 'An ionized gas with freely moving charged particles', 'meaning': 'AFO:AFQ_0000115'},
    "BOSE_EINSTEIN_CONDENSATE": {'description': 'A state of matter formed at extremely low temperatures where particles occupy the same quantum state'},
    "FERMIONIC_CONDENSATE": {'description': 'A superfluid phase formed by fermionic particles at extremely low temperatures'},
    "SUPERCRITICAL_FLUID": {'description': 'A state where distinct liquid and gas phases do not exist'},
    "SUPERFLUID": {'description': 'A phase of matter with zero viscosity'},
    "SUPERSOLID": {'description': 'A spatially ordered material with superfluid properties'},
    "QUARK_GLUON_PLASMA": {'description': 'An extremely hot phase where quarks and gluons are not confined'},
}

class AirPollutantEnum(RichEnum):
    """
    Common air pollutants and air quality indicators
    """
    # Enum members
    PM2_5 = "PM2_5"
    PM10 = "PM10"
    ULTRAFINE_PARTICLES = "ULTRAFINE_PARTICLES"
    OZONE = "OZONE"
    NITROGEN_DIOXIDE = "NITROGEN_DIOXIDE"
    SULFUR_DIOXIDE = "SULFUR_DIOXIDE"
    CARBON_MONOXIDE = "CARBON_MONOXIDE"
    LEAD = "LEAD"
    BENZENE = "BENZENE"
    FORMALDEHYDE = "FORMALDEHYDE"
    VOLATILE_ORGANIC_COMPOUNDS = "VOLATILE_ORGANIC_COMPOUNDS"
    POLYCYCLIC_AROMATIC_HYDROCARBONS = "POLYCYCLIC_AROMATIC_HYDROCARBONS"

# Set metadata after class creation to avoid it becoming an enum member
AirPollutantEnum._metadata = {
    "PM2_5": {'description': 'Fine particulate matter with diameter less than 2.5 micrometers', 'meaning': 'ENVO:01000415'},
    "PM10": {'description': 'Respirable particulate matter with diameter less than 10 micrometers', 'meaning': 'ENVO:01000405'},
    "ULTRAFINE_PARTICLES": {'description': 'Ultrafine particles with diameter less than 100 nanometers', 'meaning': 'ENVO:01000416'},
    "OZONE": {'description': 'Ground-level ozone (O3)', 'meaning': 'CHEBI:25812'},
    "NITROGEN_DIOXIDE": {'description': 'Nitrogen dioxide (NO2)', 'meaning': 'CHEBI:33101'},
    "SULFUR_DIOXIDE": {'description': 'Sulfur dioxide (SO2)', 'meaning': 'CHEBI:18422'},
    "CARBON_MONOXIDE": {'description': 'Carbon monoxide (CO)', 'meaning': 'CHEBI:17245'},
    "LEAD": {'description': 'Airborne lead particles', 'meaning': 'NCIT:C44396'},
    "BENZENE": {'description': 'Benzene vapor', 'meaning': 'CHEBI:16716'},
    "FORMALDEHYDE": {'description': 'Formaldehyde gas', 'meaning': 'CHEBI:16842'},
    "VOLATILE_ORGANIC_COMPOUNDS": {'description': 'Volatile organic compounds (VOCs)', 'meaning': 'CHEBI:134179'},
    "POLYCYCLIC_AROMATIC_HYDROCARBONS": {'description': 'Polycyclic aromatic hydrocarbons (PAHs)', 'meaning': 'CHEBI:33848'},
}

class PesticideTypeEnum(RichEnum):
    """
    Categories of pesticides by target organism or chemical class
    """
    # Enum members
    HERBICIDE = "HERBICIDE"
    INSECTICIDE = "INSECTICIDE"
    FUNGICIDE = "FUNGICIDE"
    RODENTICIDE = "RODENTICIDE"
    ORGANOPHOSPHATE = "ORGANOPHOSPHATE"
    ORGANOCHLORINE = "ORGANOCHLORINE"
    PYRETHROID = "PYRETHROID"
    CARBAMATE = "CARBAMATE"
    NEONICOTINOID = "NEONICOTINOID"
    GLYPHOSATE = "GLYPHOSATE"

# Set metadata after class creation to avoid it becoming an enum member
PesticideTypeEnum._metadata = {
    "HERBICIDE": {'description': 'Chemical used to kill unwanted plants', 'meaning': 'CHEBI:24527'},
    "INSECTICIDE": {'description': 'Chemical used to kill insects', 'meaning': 'CHEBI:24852'},
    "FUNGICIDE": {'description': 'Chemical used to kill fungi', 'meaning': 'CHEBI:24127'},
    "RODENTICIDE": {'description': 'Chemical used to kill rodents', 'meaning': 'CHEBI:33288'},
    "ORGANOPHOSPHATE": {'description': 'Organophosphate pesticide', 'meaning': 'CHEBI:25708'},
    "ORGANOCHLORINE": {'description': 'Organochlorine pesticide', 'meaning': 'CHEBI:25705'},
    "PYRETHROID": {'description': 'Pyrethroid pesticide', 'meaning': 'CHEBI:26413'},
    "CARBAMATE": {'description': 'Carbamate pesticide', 'meaning': 'CHEBI:38461'},
    "NEONICOTINOID": {'description': 'Neonicotinoid pesticide', 'meaning': 'CHEBI:25540'},
    "GLYPHOSATE": {'description': 'Glyphosate herbicide', 'meaning': 'CHEBI:27744'},
}

class HeavyMetalEnum(RichEnum):
    """
    Heavy metals of environmental health concern
    """
    # Enum members
    LEAD = "LEAD"
    MERCURY = "MERCURY"
    CADMIUM = "CADMIUM"
    ARSENIC = "ARSENIC"
    CHROMIUM = "CHROMIUM"
    NICKEL = "NICKEL"
    COPPER = "COPPER"
    ZINC = "ZINC"
    MANGANESE = "MANGANESE"
    COBALT = "COBALT"

# Set metadata after class creation to avoid it becoming an enum member
HeavyMetalEnum._metadata = {
    "LEAD": {'description': 'Lead (Pb)', 'meaning': 'NCIT:C44396'},
    "MERCURY": {'description': 'Mercury (Hg)', 'meaning': 'NCIT:C66842'},
    "CADMIUM": {'description': 'Cadmium (Cd)', 'meaning': 'NCIT:C44348'},
    "ARSENIC": {'description': 'Arsenic (As)', 'meaning': 'NCIT:C28131'},
    "CHROMIUM": {'description': 'Chromium (Cr)', 'meaning': 'NCIT:C370'},
    "NICKEL": {'description': 'Nickel (Ni)', 'meaning': 'CHEBI:28112'},
    "COPPER": {'description': 'Copper (Cu)', 'meaning': 'CHEBI:28694'},
    "ZINC": {'description': 'Zinc (Zn)', 'meaning': 'CHEBI:27363'},
    "MANGANESE": {'description': 'Manganese (Mn)', 'meaning': 'CHEBI:18291'},
    "COBALT": {'description': 'Cobalt (Co)', 'meaning': 'CHEBI:27638'},
}

class ExposureRouteEnum(RichEnum):
    """
    Routes by which exposure to environmental agents occurs
    """
    # Enum members
    INHALATION = "INHALATION"
    INGESTION = "INGESTION"
    DERMAL = "DERMAL"
    INJECTION = "INJECTION"
    TRANSPLACENTAL = "TRANSPLACENTAL"
    OCULAR = "OCULAR"
    MULTIPLE_ROUTES = "MULTIPLE_ROUTES"

# Set metadata after class creation to avoid it becoming an enum member
ExposureRouteEnum._metadata = {
    "INHALATION": {'description': 'Exposure through breathing', 'meaning': 'NCIT:C38284'},
    "INGESTION": {'description': 'Exposure through eating or drinking', 'meaning': 'NCIT:C38288'},
    "DERMAL": {'description': 'Exposure through skin contact', 'meaning': 'NCIT:C38675'},
    "INJECTION": {'description': 'Exposure through injection', 'meaning': 'NCIT:C38276'},
    "TRANSPLACENTAL": {'description': 'Exposure through placental transfer', 'meaning': 'NCIT:C38307'},
    "OCULAR": {'description': 'Exposure through the eyes', 'meaning': 'NCIT:C38287'},
    "MULTIPLE_ROUTES": {'description': 'Exposure through multiple pathways'},
}

class ExposureSourceEnum(RichEnum):
    """
    Common sources of environmental exposures
    """
    # Enum members
    AMBIENT_AIR = "AMBIENT_AIR"
    INDOOR_AIR = "INDOOR_AIR"
    DRINKING_WATER = "DRINKING_WATER"
    SOIL = "SOIL"
    FOOD = "FOOD"
    OCCUPATIONAL = "OCCUPATIONAL"
    CONSUMER_PRODUCTS = "CONSUMER_PRODUCTS"
    INDUSTRIAL_EMISSIONS = "INDUSTRIAL_EMISSIONS"
    AGRICULTURAL = "AGRICULTURAL"
    TRAFFIC = "TRAFFIC"
    TOBACCO_SMOKE = "TOBACCO_SMOKE"
    CONSTRUCTION = "CONSTRUCTION"
    MINING = "MINING"

# Set metadata after class creation to avoid it becoming an enum member
ExposureSourceEnum._metadata = {
    "AMBIENT_AIR": {'description': 'Outdoor air pollution'},
    "INDOOR_AIR": {'description': 'Indoor air pollution'},
    "DRINKING_WATER": {'description': 'Contaminated drinking water'},
    "SOIL": {'description': 'Contaminated soil', 'meaning': 'ENVO:00002116'},
    "FOOD": {'description': 'Contaminated food'},
    "OCCUPATIONAL": {'description': 'Workplace exposure', 'meaning': 'ENVO:03501332'},
    "CONSUMER_PRODUCTS": {'description': 'Household and consumer products'},
    "INDUSTRIAL_EMISSIONS": {'description': 'Industrial facility emissions'},
    "AGRICULTURAL": {'description': 'Agricultural activities'},
    "TRAFFIC": {'description': 'Traffic-related pollution'},
    "TOBACCO_SMOKE": {'description': 'Active or passive tobacco smoke exposure', 'meaning': 'NCIT:C17140'},
    "CONSTRUCTION": {'description': 'Construction-related exposure'},
    "MINING": {'description': 'Mining-related exposure'},
}

class WaterContaminantEnum(RichEnum):
    """
    Common water contaminants
    """
    # Enum members
    LEAD = "LEAD"
    ARSENIC = "ARSENIC"
    NITRATES = "NITRATES"
    FLUORIDE = "FLUORIDE"
    CHLORINE = "CHLORINE"
    BACTERIA = "BACTERIA"
    VIRUSES = "VIRUSES"
    PARASITES = "PARASITES"
    PFAS = "PFAS"
    MICROPLASTICS = "MICROPLASTICS"
    PHARMACEUTICALS = "PHARMACEUTICALS"
    PESTICIDES = "PESTICIDES"

# Set metadata after class creation to avoid it becoming an enum member
WaterContaminantEnum._metadata = {
    "LEAD": {'description': 'Lead contamination', 'meaning': 'NCIT:C44396'},
    "ARSENIC": {'description': 'Arsenic contamination', 'meaning': 'NCIT:C28131'},
    "NITRATES": {'description': 'Nitrate contamination', 'meaning': 'CHEBI:17632'},
    "FLUORIDE": {'description': 'Fluoride levels', 'meaning': 'CHEBI:17051'},
    "CHLORINE": {'description': 'Chlorine and chlorination byproducts', 'meaning': 'NCIT:C28140'},
    "BACTERIA": {'description': 'Bacterial contamination', 'meaning': 'NCIT:C14187'},
    "VIRUSES": {'description': 'Viral contamination', 'meaning': 'NCIT:C14283'},
    "PARASITES": {'description': 'Parasitic contamination', 'meaning': 'NCIT:C28176'},
    "PFAS": {'description': 'Per- and polyfluoroalkyl substances', 'meaning': 'CHEBI:172397'},
    "MICROPLASTICS": {'description': 'Microplastic particles', 'meaning': 'ENVO:01000944'},
    "PHARMACEUTICALS": {'description': 'Pharmaceutical residues', 'meaning': 'CHEBI:52217'},
    "PESTICIDES": {'description': 'Pesticide residues', 'meaning': 'CHEBI:25944'},
}

class EndocrineDisruptorEnum(RichEnum):
    """
    Common endocrine disrupting chemicals
    """
    # Enum members
    BPA = "BPA"
    PHTHALATES = "PHTHALATES"
    PFAS = "PFAS"
    PCB = "PCB"
    DIOXINS = "DIOXINS"
    DDT = "DDT"
    PARABENS = "PARABENS"
    TRICLOSAN = "TRICLOSAN"
    FLAME_RETARDANTS = "FLAME_RETARDANTS"

# Set metadata after class creation to avoid it becoming an enum member
EndocrineDisruptorEnum._metadata = {
    "BPA": {'description': 'Bisphenol A', 'meaning': 'CHEBI:33216'},
    "PHTHALATES": {'description': 'Phthalates', 'meaning': 'CHEBI:26092'},
    "PFAS": {'description': 'Per- and polyfluoroalkyl substances', 'meaning': 'CHEBI:172397'},
    "PCB": {'description': 'Polychlorinated biphenyls', 'meaning': 'CHEBI:53156'},
    "DIOXINS": {'description': 'Dioxins', 'meaning': 'NCIT:C442'},
    "DDT": {'description': 'Dichlorodiphenyltrichloroethane and metabolites', 'meaning': 'CHEBI:16130'},
    "PARABENS": {'description': 'Parabens', 'meaning': 'CHEBI:85122'},
    "TRICLOSAN": {'description': 'Triclosan', 'meaning': 'CHEBI:164200'},
    "FLAME_RETARDANTS": {'description': 'Brominated flame retardants', 'meaning': 'CHEBI:172368'},
}

class ExposureDurationEnum(RichEnum):
    """
    Duration categories for environmental exposures
    """
    # Enum members
    ACUTE = "ACUTE"
    SUBACUTE = "SUBACUTE"
    SUBCHRONIC = "SUBCHRONIC"
    CHRONIC = "CHRONIC"
    LIFETIME = "LIFETIME"
    PRENATAL = "PRENATAL"
    POSTNATAL = "POSTNATAL"
    DEVELOPMENTAL = "DEVELOPMENTAL"

# Set metadata after class creation to avoid it becoming an enum member
ExposureDurationEnum._metadata = {
    "ACUTE": {'description': 'Single or short-term exposure (hours to days)'},
    "SUBACUTE": {'description': 'Repeated exposure over weeks'},
    "SUBCHRONIC": {'description': 'Repeated exposure over months'},
    "CHRONIC": {'description': 'Long-term exposure over years'},
    "LIFETIME": {'description': 'Exposure over entire lifetime'},
    "PRENATAL": {'description': 'Exposure during pregnancy'},
    "POSTNATAL": {'description': 'Exposure after birth'},
    "DEVELOPMENTAL": {'description': 'Exposure during critical developmental periods'},
}

class CountryCodeISO2Enum(RichEnum):
    """
    ISO 3166-1 alpha-2 country codes (2-letter codes)
    """
    # Enum members
    US = "US"
    CA = "CA"
    MX = "MX"
    GB = "GB"
    FR = "FR"
    DE = "DE"
    IT = "IT"
    ES = "ES"
    PT = "PT"
    NL = "NL"
    BE = "BE"
    CH = "CH"
    AT = "AT"
    SE = "SE"
    FALSE = "False"
    DK = "DK"
    FI = "FI"
    PL = "PL"
    RU = "RU"
    UA = "UA"
    CN = "CN"
    JP = "JP"
    KR = "KR"
    IN = "IN"
    AU = "AU"
    NZ = "NZ"
    BR = "BR"
    AR = "AR"
    CL = "CL"
    CO = "CO"
    PE = "PE"
    VE = "VE"
    ZA = "ZA"
    EG = "EG"
    NG = "NG"
    KE = "KE"
    IL = "IL"
    SA = "SA"
    AE = "AE"
    TR = "TR"
    GR = "GR"
    IE = "IE"
    SG = "SG"
    MY = "MY"
    TH = "TH"
    ID = "ID"
    PH = "PH"
    VN = "VN"
    PK = "PK"
    BD = "BD"

# Set metadata after class creation to avoid it becoming an enum member
CountryCodeISO2Enum._metadata = {
    "US": {'description': 'United States of America', 'meaning': 'iso3166loc:us'},
    "CA": {'description': 'Canada', 'meaning': 'iso3166loc:ca'},
    "MX": {'description': 'Mexico', 'meaning': 'iso3166loc:mx'},
    "GB": {'description': 'United Kingdom', 'meaning': 'iso3166loc:gb'},
    "FR": {'description': 'France', 'meaning': 'iso3166loc:fr'},
    "DE": {'description': 'Germany', 'meaning': 'iso3166loc:de'},
    "IT": {'description': 'Italy', 'meaning': 'iso3166loc:it'},
    "ES": {'description': 'Spain', 'meaning': 'iso3166loc:es'},
    "PT": {'description': 'Portugal', 'meaning': 'iso3166loc:pt'},
    "NL": {'description': 'Netherlands', 'meaning': 'iso3166loc:nl'},
    "BE": {'description': 'Belgium', 'meaning': 'iso3166loc:be'},
    "CH": {'description': 'Switzerland', 'meaning': 'iso3166loc:ch'},
    "AT": {'description': 'Austria', 'meaning': 'iso3166loc:at'},
    "SE": {'description': 'Sweden', 'meaning': 'iso3166loc:se'},
    "FALSE": {'description': 'Norway', 'meaning': 'iso3166loc:no'},
    "DK": {'description': 'Denmark', 'meaning': 'iso3166loc:dk'},
    "FI": {'description': 'Finland', 'meaning': 'iso3166loc:fi'},
    "PL": {'description': 'Poland', 'meaning': 'iso3166loc:pl'},
    "RU": {'description': 'Russian Federation', 'meaning': 'iso3166loc:ru'},
    "UA": {'description': 'Ukraine', 'meaning': 'iso3166loc:ua'},
    "CN": {'description': 'China', 'meaning': 'iso3166loc:cn'},
    "JP": {'description': 'Japan', 'meaning': 'iso3166loc:jp'},
    "KR": {'description': 'South Korea', 'meaning': 'iso3166loc:kr'},
    "IN": {'description': 'India', 'meaning': 'iso3166loc:in'},
    "AU": {'description': 'Australia', 'meaning': 'iso3166loc:au'},
    "NZ": {'description': 'New Zealand', 'meaning': 'iso3166loc:nz'},
    "BR": {'description': 'Brazil', 'meaning': 'iso3166loc:br'},
    "AR": {'description': 'Argentina', 'meaning': 'iso3166loc:ar'},
    "CL": {'description': 'Chile', 'meaning': 'iso3166loc:cl'},
    "CO": {'description': 'Colombia', 'meaning': 'iso3166loc:co'},
    "PE": {'description': 'Peru', 'meaning': 'iso3166loc:pe'},
    "VE": {'description': 'Venezuela', 'meaning': 'iso3166loc:ve'},
    "ZA": {'description': 'South Africa', 'meaning': 'iso3166loc:za'},
    "EG": {'description': 'Egypt', 'meaning': 'iso3166loc:eg'},
    "NG": {'description': 'Nigeria', 'meaning': 'iso3166loc:ng'},
    "KE": {'description': 'Kenya', 'meaning': 'iso3166loc:ke'},
    "IL": {'description': 'Israel', 'meaning': 'iso3166loc:il'},
    "SA": {'description': 'Saudi Arabia', 'meaning': 'iso3166loc:sa'},
    "AE": {'description': 'United Arab Emirates', 'meaning': 'iso3166loc:ae'},
    "TR": {'description': 'Turkey', 'meaning': 'iso3166loc:tr'},
    "GR": {'description': 'Greece', 'meaning': 'iso3166loc:gr'},
    "IE": {'description': 'Ireland', 'meaning': 'iso3166loc:ie'},
    "SG": {'description': 'Singapore', 'meaning': 'iso3166loc:sg'},
    "MY": {'description': 'Malaysia', 'meaning': 'iso3166loc:my'},
    "TH": {'description': 'Thailand', 'meaning': 'iso3166loc:th'},
    "ID": {'description': 'Indonesia', 'meaning': 'iso3166loc:id'},
    "PH": {'description': 'Philippines', 'meaning': 'iso3166loc:ph'},
    "VN": {'description': 'Vietnam', 'meaning': 'iso3166loc:vn'},
    "PK": {'description': 'Pakistan', 'meaning': 'iso3166loc:pk'},
    "BD": {'description': 'Bangladesh', 'meaning': 'iso3166loc:bd'},
}

class CountryCodeISO3Enum(RichEnum):
    """
    ISO 3166-1 alpha-3 country codes (3-letter codes)
    """
    # Enum members
    USA = "USA"
    CAN = "CAN"
    MEX = "MEX"
    GBR = "GBR"
    FRA = "FRA"
    DEU = "DEU"
    ITA = "ITA"
    ESP = "ESP"
    PRT = "PRT"
    NLD = "NLD"
    BEL = "BEL"
    CHE = "CHE"
    AUT = "AUT"
    SWE = "SWE"
    NOR = "NOR"
    DNK = "DNK"
    FIN = "FIN"
    POL = "POL"
    RUS = "RUS"
    UKR = "UKR"
    CHN = "CHN"
    JPN = "JPN"
    KOR = "KOR"
    IND = "IND"
    AUS = "AUS"
    NZL = "NZL"
    BRA = "BRA"
    ARG = "ARG"
    CHL = "CHL"
    COL = "COL"

# Set metadata after class creation to avoid it becoming an enum member
CountryCodeISO3Enum._metadata = {
    "USA": {'description': 'United States of America', 'meaning': 'iso3166loc:us'},
    "CAN": {'description': 'Canada', 'meaning': 'iso3166loc:ca'},
    "MEX": {'description': 'Mexico', 'meaning': 'iso3166loc:mx'},
    "GBR": {'description': 'United Kingdom', 'meaning': 'iso3166loc:gb'},
    "FRA": {'description': 'France', 'meaning': 'iso3166loc:fr'},
    "DEU": {'description': 'Germany', 'meaning': 'iso3166loc:de'},
    "ITA": {'description': 'Italy', 'meaning': 'iso3166loc:it'},
    "ESP": {'description': 'Spain', 'meaning': 'iso3166loc:es'},
    "PRT": {'description': 'Portugal', 'meaning': 'iso3166loc:pt'},
    "NLD": {'description': 'Netherlands', 'meaning': 'iso3166loc:nl'},
    "BEL": {'description': 'Belgium', 'meaning': 'iso3166loc:be'},
    "CHE": {'description': 'Switzerland', 'meaning': 'iso3166loc:ch'},
    "AUT": {'description': 'Austria', 'meaning': 'iso3166loc:at'},
    "SWE": {'description': 'Sweden', 'meaning': 'iso3166loc:se'},
    "NOR": {'description': 'Norway', 'meaning': 'iso3166loc:no'},
    "DNK": {'description': 'Denmark', 'meaning': 'iso3166loc:dk'},
    "FIN": {'description': 'Finland', 'meaning': 'iso3166loc:fi'},
    "POL": {'description': 'Poland', 'meaning': 'iso3166loc:pl'},
    "RUS": {'description': 'Russian Federation', 'meaning': 'iso3166loc:ru'},
    "UKR": {'description': 'Ukraine', 'meaning': 'iso3166loc:ua'},
    "CHN": {'description': 'China', 'meaning': 'iso3166loc:cn'},
    "JPN": {'description': 'Japan', 'meaning': 'iso3166loc:jp'},
    "KOR": {'description': 'South Korea', 'meaning': 'iso3166loc:kr'},
    "IND": {'description': 'India', 'meaning': 'iso3166loc:in'},
    "AUS": {'description': 'Australia', 'meaning': 'iso3166loc:au'},
    "NZL": {'description': 'New Zealand', 'meaning': 'iso3166loc:nz'},
    "BRA": {'description': 'Brazil', 'meaning': 'iso3166loc:br'},
    "ARG": {'description': 'Argentina', 'meaning': 'iso3166loc:ar'},
    "CHL": {'description': 'Chile', 'meaning': 'iso3166loc:cl'},
    "COL": {'description': 'Colombia', 'meaning': 'iso3166loc:co'},
}

class USStateCodeEnum(RichEnum):
    """
    United States state and territory codes
    """
    # Enum members
    AL = "AL"
    AK = "AK"
    AZ = "AZ"
    AR = "AR"
    CA = "CA"
    CO = "CO"
    CT = "CT"
    DE = "DE"
    FL = "FL"
    GA = "GA"
    HI = "HI"
    ID = "ID"
    IL = "IL"
    IN = "IN"
    IA = "IA"
    KS = "KS"
    KY = "KY"
    LA = "LA"
    ME = "ME"
    MD = "MD"
    MA = "MA"
    MI = "MI"
    MN = "MN"
    MS = "MS"
    MO = "MO"
    MT = "MT"
    NE = "NE"
    NV = "NV"
    NH = "NH"
    NJ = "NJ"
    NM = "NM"
    NY = "NY"
    NC = "NC"
    ND = "ND"
    OH = "OH"
    OK = "OK"
    OR = "OR"
    PA = "PA"
    RI = "RI"
    SC = "SC"
    SD = "SD"
    TN = "TN"
    TX = "TX"
    UT = "UT"
    VT = "VT"
    VA = "VA"
    WA = "WA"
    WV = "WV"
    WI = "WI"
    WY = "WY"
    DC = "DC"
    PR = "PR"
    VI = "VI"
    GU = "GU"
    AS = "AS"
    MP = "MP"

# Set metadata after class creation to avoid it becoming an enum member
USStateCodeEnum._metadata = {
    "AL": {'description': 'Alabama'},
    "AK": {'description': 'Alaska'},
    "AZ": {'description': 'Arizona'},
    "AR": {'description': 'Arkansas'},
    "CA": {'description': 'California'},
    "CO": {'description': 'Colorado'},
    "CT": {'description': 'Connecticut'},
    "DE": {'description': 'Delaware'},
    "FL": {'description': 'Florida'},
    "GA": {'description': 'Georgia'},
    "HI": {'description': 'Hawaii'},
    "ID": {'description': 'Idaho'},
    "IL": {'description': 'Illinois'},
    "IN": {'description': 'Indiana'},
    "IA": {'description': 'Iowa'},
    "KS": {'description': 'Kansas'},
    "KY": {'description': 'Kentucky'},
    "LA": {'description': 'Louisiana'},
    "ME": {'description': 'Maine'},
    "MD": {'description': 'Maryland'},
    "MA": {'description': 'Massachusetts'},
    "MI": {'description': 'Michigan'},
    "MN": {'description': 'Minnesota'},
    "MS": {'description': 'Mississippi'},
    "MO": {'description': 'Missouri'},
    "MT": {'description': 'Montana'},
    "NE": {'description': 'Nebraska'},
    "NV": {'description': 'Nevada'},
    "NH": {'description': 'New Hampshire'},
    "NJ": {'description': 'New Jersey'},
    "NM": {'description': 'New Mexico'},
    "NY": {'description': 'New York'},
    "NC": {'description': 'North Carolina'},
    "ND": {'description': 'North Dakota'},
    "OH": {'description': 'Ohio'},
    "OK": {'description': 'Oklahoma'},
    "OR": {'description': 'Oregon'},
    "PA": {'description': 'Pennsylvania'},
    "RI": {'description': 'Rhode Island'},
    "SC": {'description': 'South Carolina'},
    "SD": {'description': 'South Dakota'},
    "TN": {'description': 'Tennessee'},
    "TX": {'description': 'Texas'},
    "UT": {'description': 'Utah'},
    "VT": {'description': 'Vermont'},
    "VA": {'description': 'Virginia'},
    "WA": {'description': 'Washington'},
    "WV": {'description': 'West Virginia'},
    "WI": {'description': 'Wisconsin'},
    "WY": {'description': 'Wyoming'},
    "DC": {'description': 'District of Columbia'},
    "PR": {'description': 'Puerto Rico'},
    "VI": {'description': 'U.S. Virgin Islands'},
    "GU": {'description': 'Guam'},
    "AS": {'description': 'American Samoa'},
    "MP": {'description': 'Northern Mariana Islands'},
}

class CanadianProvinceCodeEnum(RichEnum):
    """
    Canadian province and territory codes
    """
    # Enum members
    AB = "AB"
    BC = "BC"
    MB = "MB"
    NB = "NB"
    NL = "NL"
    NS = "NS"
    NT = "NT"
    NU = "NU"
    TRUE = "True"
    PE = "PE"
    QC = "QC"
    SK = "SK"
    YT = "YT"

# Set metadata after class creation to avoid it becoming an enum member
CanadianProvinceCodeEnum._metadata = {
    "AB": {'description': 'Alberta'},
    "BC": {'description': 'British Columbia'},
    "MB": {'description': 'Manitoba'},
    "NB": {'description': 'New Brunswick'},
    "NL": {'description': 'Newfoundland and Labrador'},
    "NS": {'description': 'Nova Scotia'},
    "NT": {'description': 'Northwest Territories'},
    "NU": {'description': 'Nunavut'},
    "TRUE": {'description': 'Ontario'},
    "PE": {'description': 'Prince Edward Island'},
    "QC": {'description': 'Quebec'},
    "SK": {'description': 'Saskatchewan'},
    "YT": {'description': 'Yukon'},
}

class CompassDirection(RichEnum):
    """
    Cardinal and intercardinal compass directions
    """
    # Enum members
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"
    NORTHEAST = "NORTHEAST"
    SOUTHEAST = "SOUTHEAST"
    SOUTHWEST = "SOUTHWEST"
    NORTHWEST = "NORTHWEST"
    NORTH_NORTHEAST = "NORTH_NORTHEAST"
    EAST_NORTHEAST = "EAST_NORTHEAST"
    EAST_SOUTHEAST = "EAST_SOUTHEAST"
    SOUTH_SOUTHEAST = "SOUTH_SOUTHEAST"
    SOUTH_SOUTHWEST = "SOUTH_SOUTHWEST"
    WEST_SOUTHWEST = "WEST_SOUTHWEST"
    WEST_NORTHWEST = "WEST_NORTHWEST"
    NORTH_NORTHWEST = "NORTH_NORTHWEST"

# Set metadata after class creation to avoid it becoming an enum member
CompassDirection._metadata = {
    "NORTH": {'description': 'North (0°/360°)', 'annotations': {'abbreviation': 'N', 'degrees': 0}},
    "EAST": {'description': 'East (90°)', 'annotations': {'abbreviation': 'E', 'degrees': 90}},
    "SOUTH": {'description': 'South (180°)', 'annotations': {'abbreviation': 'S', 'degrees': 180}},
    "WEST": {'description': 'West (270°)', 'annotations': {'abbreviation': 'W', 'degrees': 270}},
    "NORTHEAST": {'description': 'Northeast (45°)', 'annotations': {'abbreviation': 'NE', 'degrees': 45}},
    "SOUTHEAST": {'description': 'Southeast (135°)', 'annotations': {'abbreviation': 'SE', 'degrees': 135}},
    "SOUTHWEST": {'description': 'Southwest (225°)', 'annotations': {'abbreviation': 'SW', 'degrees': 225}},
    "NORTHWEST": {'description': 'Northwest (315°)', 'annotations': {'abbreviation': 'NW', 'degrees': 315}},
    "NORTH_NORTHEAST": {'description': 'North-northeast (22.5°)', 'annotations': {'abbreviation': 'NNE', 'degrees': 22.5}},
    "EAST_NORTHEAST": {'description': 'East-northeast (67.5°)', 'annotations': {'abbreviation': 'ENE', 'degrees': 67.5}},
    "EAST_SOUTHEAST": {'description': 'East-southeast (112.5°)', 'annotations': {'abbreviation': 'ESE', 'degrees': 112.5}},
    "SOUTH_SOUTHEAST": {'description': 'South-southeast (157.5°)', 'annotations': {'abbreviation': 'SSE', 'degrees': 157.5}},
    "SOUTH_SOUTHWEST": {'description': 'South-southwest (202.5°)', 'annotations': {'abbreviation': 'SSW', 'degrees': 202.5}},
    "WEST_SOUTHWEST": {'description': 'West-southwest (247.5°)', 'annotations': {'abbreviation': 'WSW', 'degrees': 247.5}},
    "WEST_NORTHWEST": {'description': 'West-northwest (292.5°)', 'annotations': {'abbreviation': 'WNW', 'degrees': 292.5}},
    "NORTH_NORTHWEST": {'description': 'North-northwest (337.5°)', 'annotations': {'abbreviation': 'NNW', 'degrees': 337.5}},
}

class RelativeDirection(RichEnum):
    """
    Relative directional terms
    """
    # Enum members
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"
    INWARD = "INWARD"
    OUTWARD = "OUTWARD"
    CLOCKWISE = "CLOCKWISE"
    COUNTERCLOCKWISE = "COUNTERCLOCKWISE"

# Set metadata after class creation to avoid it becoming an enum member
RelativeDirection._metadata = {
    "FORWARD": {'description': 'Forward/Ahead', 'annotations': {'aliases': 'ahead, front'}},
    "BACKWARD": {'description': 'Backward/Behind', 'annotations': {'aliases': 'behind, back, rear'}},
    "LEFT": {'description': 'Left', 'annotations': {'aliases': 'port (nautical)'}},
    "RIGHT": {'description': 'Right', 'annotations': {'aliases': 'starboard (nautical)'}},
    "UP": {'description': 'Up/Above', 'annotations': {'aliases': 'above, upward'}},
    "DOWN": {'description': 'Down/Below', 'annotations': {'aliases': 'below, downward'}},
    "INWARD": {'description': 'Inward/Toward center', 'annotations': {'aliases': 'toward center, centripetal'}},
    "OUTWARD": {'description': 'Outward/Away from center', 'annotations': {'aliases': 'away from center, centrifugal'}},
    "CLOCKWISE": {'description': 'Clockwise rotation', 'annotations': {'abbreviation': 'CW'}},
    "COUNTERCLOCKWISE": {'description': 'Counterclockwise rotation', 'annotations': {'abbreviation': 'CCW', 'aliases': 'anticlockwise'}},
}

class WindDirection(RichEnum):
    """
    Wind direction nomenclature (named for where wind comes FROM)
    """
    # Enum members
    NORTHERLY = "NORTHERLY"
    NORTHEASTERLY = "NORTHEASTERLY"
    EASTERLY = "EASTERLY"
    SOUTHEASTERLY = "SOUTHEASTERLY"
    SOUTHERLY = "SOUTHERLY"
    SOUTHWESTERLY = "SOUTHWESTERLY"
    WESTERLY = "WESTERLY"
    NORTHWESTERLY = "NORTHWESTERLY"
    VARIABLE = "VARIABLE"

# Set metadata after class creation to avoid it becoming an enum member
WindDirection._metadata = {
    "NORTHERLY": {'description': 'Wind from the north', 'annotations': {'from_direction': 'north', 'toward_direction': 'south'}},
    "NORTHEASTERLY": {'description': 'Wind from the northeast', 'annotations': {'from_direction': 'northeast', 'toward_direction': 'southwest'}},
    "EASTERLY": {'description': 'Wind from the east', 'annotations': {'from_direction': 'east', 'toward_direction': 'west'}},
    "SOUTHEASTERLY": {'description': 'Wind from the southeast', 'annotations': {'from_direction': 'southeast', 'toward_direction': 'northwest'}},
    "SOUTHERLY": {'description': 'Wind from the south', 'annotations': {'from_direction': 'south', 'toward_direction': 'north'}},
    "SOUTHWESTERLY": {'description': 'Wind from the southwest', 'annotations': {'from_direction': 'southwest', 'toward_direction': 'northeast'}},
    "WESTERLY": {'description': 'Wind from the west', 'annotations': {'from_direction': 'west', 'toward_direction': 'east'}},
    "NORTHWESTERLY": {'description': 'Wind from the northwest', 'annotations': {'from_direction': 'northwest', 'toward_direction': 'southeast'}},
    "VARIABLE": {'description': 'Variable wind direction', 'annotations': {'note': 'changing or inconsistent direction'}},
}

class ContinentEnum(RichEnum):
    """
    Continental regions
    """
    # Enum members
    AFRICA = "AFRICA"
    ANTARCTICA = "ANTARCTICA"
    ASIA = "ASIA"
    EUROPE = "EUROPE"
    NORTH_AMERICA = "NORTH_AMERICA"
    OCEANIA = "OCEANIA"
    SOUTH_AMERICA = "SOUTH_AMERICA"

# Set metadata after class creation to avoid it becoming an enum member
ContinentEnum._metadata = {
    "AFRICA": {'description': 'Africa'},
    "ANTARCTICA": {'description': 'Antarctica'},
    "ASIA": {'description': 'Asia'},
    "EUROPE": {'description': 'Europe'},
    "NORTH_AMERICA": {'description': 'North America'},
    "OCEANIA": {'description': 'Oceania (including Australia)'},
    "SOUTH_AMERICA": {'description': 'South America'},
}

class UNRegionEnum(RichEnum):
    """
    United Nations regional classifications
    """
    # Enum members
    EASTERN_AFRICA = "EASTERN_AFRICA"
    MIDDLE_AFRICA = "MIDDLE_AFRICA"
    NORTHERN_AFRICA = "NORTHERN_AFRICA"
    SOUTHERN_AFRICA = "SOUTHERN_AFRICA"
    WESTERN_AFRICA = "WESTERN_AFRICA"
    CARIBBEAN = "CARIBBEAN"
    CENTRAL_AMERICA = "CENTRAL_AMERICA"
    NORTHERN_AMERICA = "NORTHERN_AMERICA"
    SOUTH_AMERICA = "SOUTH_AMERICA"
    CENTRAL_ASIA = "CENTRAL_ASIA"
    EASTERN_ASIA = "EASTERN_ASIA"
    SOUTHERN_ASIA = "SOUTHERN_ASIA"
    SOUTH_EASTERN_ASIA = "SOUTH_EASTERN_ASIA"
    WESTERN_ASIA = "WESTERN_ASIA"
    EASTERN_EUROPE = "EASTERN_EUROPE"
    NORTHERN_EUROPE = "NORTHERN_EUROPE"
    SOUTHERN_EUROPE = "SOUTHERN_EUROPE"
    WESTERN_EUROPE = "WESTERN_EUROPE"
    AUSTRALIA_NEW_ZEALAND = "AUSTRALIA_NEW_ZEALAND"
    MELANESIA = "MELANESIA"
    MICRONESIA = "MICRONESIA"
    POLYNESIA = "POLYNESIA"

# Set metadata after class creation to avoid it becoming an enum member
UNRegionEnum._metadata = {
    "EASTERN_AFRICA": {'description': 'Eastern Africa'},
    "MIDDLE_AFRICA": {'description': 'Middle Africa'},
    "NORTHERN_AFRICA": {'description': 'Northern Africa'},
    "SOUTHERN_AFRICA": {'description': 'Southern Africa'},
    "WESTERN_AFRICA": {'description': 'Western Africa'},
    "CARIBBEAN": {'description': 'Caribbean'},
    "CENTRAL_AMERICA": {'description': 'Central America'},
    "NORTHERN_AMERICA": {'description': 'Northern America'},
    "SOUTH_AMERICA": {'description': 'South America'},
    "CENTRAL_ASIA": {'description': 'Central Asia'},
    "EASTERN_ASIA": {'description': 'Eastern Asia'},
    "SOUTHERN_ASIA": {'description': 'Southern Asia'},
    "SOUTH_EASTERN_ASIA": {'description': 'South-Eastern Asia'},
    "WESTERN_ASIA": {'description': 'Western Asia'},
    "EASTERN_EUROPE": {'description': 'Eastern Europe'},
    "NORTHERN_EUROPE": {'description': 'Northern Europe'},
    "SOUTHERN_EUROPE": {'description': 'Southern Europe'},
    "WESTERN_EUROPE": {'description': 'Western Europe'},
    "AUSTRALIA_NEW_ZEALAND": {'description': 'Australia and New Zealand'},
    "MELANESIA": {'description': 'Melanesia'},
    "MICRONESIA": {'description': 'Micronesia'},
    "POLYNESIA": {'description': 'Polynesia'},
}

class LanguageCodeISO6391enum(RichEnum):
    """
    ISO 639-1 two-letter language codes
    """
    # Enum members
    EN = "EN"
    ES = "ES"
    FR = "FR"
    DE = "DE"
    IT = "IT"
    PT = "PT"
    RU = "RU"
    ZH = "ZH"
    JA = "JA"
    KO = "KO"
    AR = "AR"
    HI = "HI"
    BN = "BN"
    PA = "PA"
    UR = "UR"
    NL = "NL"
    PL = "PL"
    TR = "TR"
    VI = "VI"
    TH = "TH"
    SV = "SV"
    DA = "DA"
    FALSE = "False"
    FI = "FI"
    EL = "EL"
    HE = "HE"
    CS = "CS"
    HU = "HU"
    RO = "RO"
    UK = "UK"

# Set metadata after class creation to avoid it becoming an enum member
LanguageCodeISO6391enum._metadata = {
    "EN": {'description': 'English'},
    "ES": {'description': 'Spanish'},
    "FR": {'description': 'French'},
    "DE": {'description': 'German'},
    "IT": {'description': 'Italian'},
    "PT": {'description': 'Portuguese'},
    "RU": {'description': 'Russian'},
    "ZH": {'description': 'Chinese'},
    "JA": {'description': 'Japanese'},
    "KO": {'description': 'Korean'},
    "AR": {'description': 'Arabic'},
    "HI": {'description': 'Hindi'},
    "BN": {'description': 'Bengali'},
    "PA": {'description': 'Punjabi'},
    "UR": {'description': 'Urdu'},
    "NL": {'description': 'Dutch'},
    "PL": {'description': 'Polish'},
    "TR": {'description': 'Turkish'},
    "VI": {'description': 'Vietnamese'},
    "TH": {'description': 'Thai'},
    "SV": {'description': 'Swedish'},
    "DA": {'description': 'Danish'},
    "FALSE": {'description': 'Norwegian'},
    "FI": {'description': 'Finnish'},
    "EL": {'description': 'Greek'},
    "HE": {'description': 'Hebrew'},
    "CS": {'description': 'Czech'},
    "HU": {'description': 'Hungarian'},
    "RO": {'description': 'Romanian'},
    "UK": {'description': 'Ukrainian'},
}

class TimeZoneEnum(RichEnum):
    """
    Common time zones
    """
    # Enum members
    UTC = "UTC"
    EST = "EST"
    EDT = "EDT"
    CST = "CST"
    CDT = "CDT"
    MST = "MST"
    MDT = "MDT"
    PST = "PST"
    PDT = "PDT"
    GMT = "GMT"
    BST = "BST"
    CET = "CET"
    CEST = "CEST"
    EET = "EET"
    EEST = "EEST"
    JST = "JST"
    CST_CHINA = "CST_CHINA"
    IST = "IST"
    AEST = "AEST"
    AEDT = "AEDT"
    NZST = "NZST"
    NZDT = "NZDT"

# Set metadata after class creation to avoid it becoming an enum member
TimeZoneEnum._metadata = {
    "UTC": {'description': 'Coordinated Universal Time'},
    "EST": {'description': 'Eastern Standard Time (UTC-5)'},
    "EDT": {'description': 'Eastern Daylight Time (UTC-4)'},
    "CST": {'description': 'Central Standard Time (UTC-6)'},
    "CDT": {'description': 'Central Daylight Time (UTC-5)'},
    "MST": {'description': 'Mountain Standard Time (UTC-7)'},
    "MDT": {'description': 'Mountain Daylight Time (UTC-6)'},
    "PST": {'description': 'Pacific Standard Time (UTC-8)'},
    "PDT": {'description': 'Pacific Daylight Time (UTC-7)'},
    "GMT": {'description': 'Greenwich Mean Time (UTC+0)'},
    "BST": {'description': 'British Summer Time (UTC+1)'},
    "CET": {'description': 'Central European Time (UTC+1)'},
    "CEST": {'description': 'Central European Summer Time (UTC+2)'},
    "EET": {'description': 'Eastern European Time (UTC+2)'},
    "EEST": {'description': 'Eastern European Summer Time (UTC+3)'},
    "JST": {'description': 'Japan Standard Time (UTC+9)'},
    "CST_CHINA": {'description': 'China Standard Time (UTC+8)'},
    "IST": {'description': 'India Standard Time (UTC+5:30)'},
    "AEST": {'description': 'Australian Eastern Standard Time (UTC+10)'},
    "AEDT": {'description': 'Australian Eastern Daylight Time (UTC+11)'},
    "NZST": {'description': 'New Zealand Standard Time (UTC+12)'},
    "NZDT": {'description': 'New Zealand Daylight Time (UTC+13)'},
}

class CurrencyCodeISO4217Enum(RichEnum):
    """
    ISO 4217 currency codes
    """
    # Enum members
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"
    CHF = "CHF"
    CAD = "CAD"
    AUD = "AUD"
    NZD = "NZD"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    RUB = "RUB"
    INR = "INR"
    BRL = "BRL"
    MXN = "MXN"
    ZAR = "ZAR"
    KRW = "KRW"
    SGD = "SGD"
    HKD = "HKD"
    TWD = "TWD"
    THB = "THB"
    MYR = "MYR"
    IDR = "IDR"
    PHP = "PHP"
    VND = "VND"
    TRY = "TRY"
    AED = "AED"
    SAR = "SAR"
    ILS = "ILS"
    EGP = "EGP"

# Set metadata after class creation to avoid it becoming an enum member
CurrencyCodeISO4217Enum._metadata = {
    "USD": {'description': 'United States Dollar'},
    "EUR": {'description': 'Euro'},
    "GBP": {'description': 'British Pound Sterling'},
    "JPY": {'description': 'Japanese Yen'},
    "CNY": {'description': 'Chinese Yuan Renminbi'},
    "CHF": {'description': 'Swiss Franc'},
    "CAD": {'description': 'Canadian Dollar'},
    "AUD": {'description': 'Australian Dollar'},
    "NZD": {'description': 'New Zealand Dollar'},
    "SEK": {'description': 'Swedish Krona'},
    "NOK": {'description': 'Norwegian Krone'},
    "DKK": {'description': 'Danish Krone'},
    "PLN": {'description': 'Polish Zloty'},
    "RUB": {'description': 'Russian Ruble'},
    "INR": {'description': 'Indian Rupee'},
    "BRL": {'description': 'Brazilian Real'},
    "MXN": {'description': 'Mexican Peso'},
    "ZAR": {'description': 'South African Rand'},
    "KRW": {'description': 'South Korean Won'},
    "SGD": {'description': 'Singapore Dollar'},
    "HKD": {'description': 'Hong Kong Dollar'},
    "TWD": {'description': 'Taiwan Dollar'},
    "THB": {'description': 'Thai Baht'},
    "MYR": {'description': 'Malaysian Ringgit'},
    "IDR": {'description': 'Indonesian Rupiah'},
    "PHP": {'description': 'Philippine Peso'},
    "VND": {'description': 'Vietnamese Dong'},
    "TRY": {'description': 'Turkish Lira'},
    "AED": {'description': 'UAE Dirham'},
    "SAR": {'description': 'Saudi Riyal'},
    "ILS": {'description': 'Israeli Shekel'},
    "EGP": {'description': 'Egyptian Pound'},
}

class SentimentClassificationEnum(RichEnum):
    """
    Standard labels for sentiment analysis classification tasks
    """
    # Enum members
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"

# Set metadata after class creation to avoid it becoming an enum member
SentimentClassificationEnum._metadata = {
    "POSITIVE": {'description': 'Positive sentiment or opinion', 'meaning': 'NCIT:C38758', 'aliases': ['pos', '1', '+']},
    "NEGATIVE": {'description': 'Negative sentiment or opinion', 'meaning': 'NCIT:C35681', 'aliases': ['neg', '0', '-']},
    "NEUTRAL": {'description': 'Neutral sentiment, neither positive nor negative', 'meaning': 'NCIT:C14165', 'aliases': ['neu', '2']},
}

class FineSentimentClassificationEnum(RichEnum):
    """
    Fine-grained sentiment analysis labels with intensity levels
    """
    # Enum members
    VERY_POSITIVE = "VERY_POSITIVE"
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    VERY_NEGATIVE = "VERY_NEGATIVE"

# Set metadata after class creation to avoid it becoming an enum member
FineSentimentClassificationEnum._metadata = {
    "VERY_POSITIVE": {'description': 'Strongly positive sentiment', 'meaning': 'NCIT:C38758', 'aliases': ['5', '++']},
    "POSITIVE": {'description': 'Positive sentiment', 'meaning': 'NCIT:C38758', 'aliases': ['4', '+']},
    "NEUTRAL": {'description': 'Neutral sentiment', 'meaning': 'NCIT:C14165', 'aliases': ['3', '0']},
    "NEGATIVE": {'description': 'Negative sentiment', 'meaning': 'NCIT:C35681', 'aliases': ['2', '-']},
    "VERY_NEGATIVE": {'description': 'Strongly negative sentiment', 'meaning': 'NCIT:C35681', 'aliases': ['1', '--']},
}

class BinaryClassificationEnum(RichEnum):
    """
    Generic binary classification labels
    """
    # Enum members
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"

# Set metadata after class creation to avoid it becoming an enum member
BinaryClassificationEnum._metadata = {
    "POSITIVE": {'description': 'Positive class', 'meaning': 'NCIT:C38758', 'aliases': ['1', 'true', 'yes', 'T']},
    "NEGATIVE": {'description': 'Negative class', 'meaning': 'NCIT:C35681', 'aliases': ['0', 'false', 'no', 'F']},
}

class SpamClassificationEnum(RichEnum):
    """
    Standard labels for spam/ham email classification
    """
    # Enum members
    SPAM = "SPAM"
    HAM = "HAM"

# Set metadata after class creation to avoid it becoming an enum member
SpamClassificationEnum._metadata = {
    "SPAM": {'description': 'Unwanted or unsolicited message', 'annotations': {'note': 'No appropriate ontology term found for spam concept'}, 'aliases': ['junk', '1']},
    "HAM": {'description': 'Legitimate, wanted message', 'annotations': {'note': 'No appropriate ontology term found for ham concept'}, 'aliases': ['not_spam', 'legitimate', '0']},
}

class AnomalyDetectionEnum(RichEnum):
    """
    Labels for anomaly detection tasks
    """
    # Enum members
    NORMAL = "NORMAL"
    ANOMALY = "ANOMALY"

# Set metadata after class creation to avoid it becoming an enum member
AnomalyDetectionEnum._metadata = {
    "NORMAL": {'description': 'Normal, expected behavior or pattern', 'meaning': 'NCIT:C14165', 'aliases': ['inlier', 'regular', '0']},
    "ANOMALY": {'description': 'Abnormal, unexpected behavior or pattern', 'meaning': 'STATO:0000036', 'aliases': ['outlier', 'abnormal', 'irregular', '1']},
}

class ChurnClassificationEnum(RichEnum):
    """
    Customer churn prediction labels
    """
    # Enum members
    RETAINED = "RETAINED"
    CHURNED = "CHURNED"

# Set metadata after class creation to avoid it becoming an enum member
ChurnClassificationEnum._metadata = {
    "RETAINED": {'description': 'Customer continues using the service', 'annotations': {'note': 'No appropriate ontology term found for customer retention'}, 'aliases': ['active', 'staying', '0']},
    "CHURNED": {'description': 'Customer stopped using the service', 'annotations': {'note': 'No appropriate ontology term found for customer churn'}, 'aliases': ['lost', 'inactive', 'attrited', '1']},
}

class FraudDetectionEnum(RichEnum):
    """
    Fraud detection classification labels
    """
    # Enum members
    LEGITIMATE = "LEGITIMATE"
    FRAUDULENT = "FRAUDULENT"

# Set metadata after class creation to avoid it becoming an enum member
FraudDetectionEnum._metadata = {
    "LEGITIMATE": {'description': 'Legitimate, non-fraudulent transaction or activity', 'meaning': 'NCIT:C14165', 'aliases': ['genuine', 'valid', '0']},
    "FRAUDULENT": {'description': 'Fraudulent transaction or activity', 'meaning': 'NCIT:C121839', 'aliases': ['fraud', 'invalid', '1']},
}

class QualityControlEnum(RichEnum):
    """
    Quality control classification labels
    """
    # Enum members
    PASS = "PASS"
    FAIL = "FAIL"

# Set metadata after class creation to avoid it becoming an enum member
QualityControlEnum._metadata = {
    "PASS": {'description': 'Item meets quality standards', 'meaning': 'NCIT:C81275', 'aliases': ['passed', 'acceptable', 'ok', '1']},
    "FAIL": {'description': 'Item does not meet quality standards', 'meaning': 'NCIT:C44281', 'aliases': ['failed', 'reject', 'defective', '0']},
}

class DefectClassificationEnum(RichEnum):
    """
    Manufacturing defect classification
    """
    # Enum members
    NO_DEFECT = "NO_DEFECT"
    MINOR_DEFECT = "MINOR_DEFECT"
    MAJOR_DEFECT = "MAJOR_DEFECT"
    CRITICAL_DEFECT = "CRITICAL_DEFECT"

# Set metadata after class creation to avoid it becoming an enum member
DefectClassificationEnum._metadata = {
    "NO_DEFECT": {'description': 'No defect detected', 'meaning': 'NCIT:C14165', 'aliases': ['good', 'normal', '0']},
    "MINOR_DEFECT": {'description': "Minor defect that doesn't affect functionality", 'aliases': ['minor', 'cosmetic', '1']},
    "MAJOR_DEFECT": {'description': 'Major defect affecting functionality', 'aliases': ['major', 'functional', '2']},
    "CRITICAL_DEFECT": {'description': 'Critical defect rendering item unusable or unsafe', 'aliases': ['critical', 'severe', '3']},
}

class BasicEmotionEnum(RichEnum):
    """
    Ekman's six basic emotions commonly used in emotion recognition
    """
    # Enum members
    ANGER = "ANGER"
    DISGUST = "DISGUST"
    FEAR = "FEAR"
    HAPPINESS = "HAPPINESS"
    SADNESS = "SADNESS"
    SURPRISE = "SURPRISE"

# Set metadata after class creation to avoid it becoming an enum member
BasicEmotionEnum._metadata = {
    "ANGER": {'description': 'Feeling of displeasure or hostility', 'meaning': 'MFOEM:000009', 'aliases': ['angry', 'mad']},
    "DISGUST": {'description': 'Feeling of revulsion or strong disapproval', 'meaning': 'MFOEM:000019', 'aliases': ['disgusted', 'repulsed']},
    "FEAR": {'description': 'Feeling of anxiety or apprehension', 'meaning': 'MFOEM:000026', 'aliases': ['afraid', 'scared']},
    "HAPPINESS": {'description': 'Feeling of pleasure or contentment', 'meaning': 'MFOEM:000042', 'aliases': ['happy', 'joy', 'joyful']},
    "SADNESS": {'description': 'Feeling of sorrow or unhappiness', 'meaning': 'MFOEM:000056', 'aliases': ['sad', 'sorrow']},
    "SURPRISE": {'description': 'Feeling of mild astonishment or shock', 'meaning': 'MFOEM:000032', 'aliases': ['surprised', 'shocked']},
}

class ExtendedEmotionEnum(RichEnum):
    """
    Extended emotion set including complex emotions
    """
    # Enum members
    ANGER = "ANGER"
    DISGUST = "DISGUST"
    FEAR = "FEAR"
    HAPPINESS = "HAPPINESS"
    SADNESS = "SADNESS"
    SURPRISE = "SURPRISE"
    CONTEMPT = "CONTEMPT"
    ANTICIPATION = "ANTICIPATION"
    TRUST = "TRUST"
    LOVE = "LOVE"

# Set metadata after class creation to avoid it becoming an enum member
ExtendedEmotionEnum._metadata = {
    "ANGER": {'description': 'Feeling of displeasure or hostility', 'meaning': 'MFOEM:000009'},
    "DISGUST": {'description': 'Feeling of revulsion', 'meaning': 'MFOEM:000019'},
    "FEAR": {'description': 'Feeling of anxiety', 'meaning': 'MFOEM:000026'},
    "HAPPINESS": {'description': 'Feeling of pleasure', 'meaning': 'MFOEM:000042'},
    "SADNESS": {'description': 'Feeling of sorrow', 'meaning': 'MFOEM:000056'},
    "SURPRISE": {'description': 'Feeling of astonishment', 'meaning': 'MFOEM:000032'},
    "CONTEMPT": {'description': 'Feeling that something is worthless', 'meaning': 'MFOEM:000018'},
    "ANTICIPATION": {'description': 'Feeling of excitement about something that will happen', 'meaning': 'MFOEM:000175', 'aliases': ['expectation', 'expectant']},
    "TRUST": {'description': 'Feeling of confidence in someone or something', 'meaning': 'MFOEM:000224'},
    "LOVE": {'description': 'Feeling of deep affection', 'meaning': 'MFOEM:000048'},
}

class PriorityLevelEnum(RichEnum):
    """
    Standard priority levels for task/issue classification
    """
    # Enum members
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    TRIVIAL = "TRIVIAL"

# Set metadata after class creation to avoid it becoming an enum member
PriorityLevelEnum._metadata = {
    "CRITICAL": {'description': 'Highest priority, requires immediate attention', 'aliases': ['P0', 'urgent', 'blocker', '1']},
    "HIGH": {'description': 'High priority, should be addressed soon', 'aliases': ['P1', 'important', '2']},
    "MEDIUM": {'description': 'Medium priority, normal workflow', 'aliases': ['P2', 'normal', '3']},
    "LOW": {'description': 'Low priority, can be deferred', 'aliases': ['P3', 'minor', '4']},
    "TRIVIAL": {'description': 'Lowest priority, nice to have', 'aliases': ['P4', 'cosmetic', '5']},
}

class SeverityLevelEnum(RichEnum):
    """
    Severity levels for incident/bug classification
    """
    # Enum members
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    TRIVIAL = "TRIVIAL"

# Set metadata after class creation to avoid it becoming an enum member
SeverityLevelEnum._metadata = {
    "CRITICAL": {'description': 'System is unusable, data loss possible', 'aliases': ['S1', 'blocker', 'showstopper']},
    "MAJOR": {'description': 'Major functionality impaired', 'aliases': ['S2', 'severe', 'high']},
    "MINOR": {'description': 'Minor functionality impaired', 'aliases': ['S3', 'moderate', 'medium']},
    "TRIVIAL": {'description': 'Cosmetic issue, minimal impact', 'aliases': ['S4', 'cosmetic', 'low']},
}

class ConfidenceLevelEnum(RichEnum):
    """
    Confidence levels for predictions and classifications
    """
    # Enum members
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"

# Set metadata after class creation to avoid it becoming an enum member
ConfidenceLevelEnum._metadata = {
    "VERY_HIGH": {'description': 'Very high confidence (>95%)', 'aliases': ['certain', '5']},
    "HIGH": {'description': 'High confidence (80-95%)', 'aliases': ['confident', '4']},
    "MEDIUM": {'description': 'Medium confidence (60-80%)', 'aliases': ['moderate', '3']},
    "LOW": {'description': 'Low confidence (40-60%)', 'aliases': ['uncertain', '2']},
    "VERY_LOW": {'description': 'Very low confidence (<40%)', 'aliases': ['guess', '1']},
}

class NewsTopicCategoryEnum(RichEnum):
    """
    Common news article topic categories
    """
    # Enum members
    POLITICS = "POLITICS"
    BUSINESS = "BUSINESS"
    TECHNOLOGY = "TECHNOLOGY"
    SPORTS = "SPORTS"
    ENTERTAINMENT = "ENTERTAINMENT"
    SCIENCE = "SCIENCE"
    HEALTH = "HEALTH"
    WORLD = "WORLD"
    LOCAL = "LOCAL"

# Set metadata after class creation to avoid it becoming an enum member
NewsTopicCategoryEnum._metadata = {
    "POLITICS": {'description': 'Political news and government affairs'},
    "BUSINESS": {'description': 'Business, finance, and economic news', 'aliases': ['finance', 'economy']},
    "TECHNOLOGY": {'description': 'Technology and computing news', 'aliases': ['tech', 'IT']},
    "SPORTS": {'description': 'Sports news and events'},
    "ENTERTAINMENT": {'description': 'Entertainment and celebrity news', 'aliases': ['showbiz']},
    "SCIENCE": {'description': 'Scientific discoveries and research'},
    "HEALTH": {'description': 'Health, medicine, and wellness news', 'aliases': ['medical']},
    "WORLD": {'description': 'International news and events', 'aliases': ['international', 'global']},
    "LOCAL": {'description': 'Local and regional news', 'aliases': ['regional']},
}

class ToxicityClassificationEnum(RichEnum):
    """
    Text toxicity classification labels
    """
    # Enum members
    NON_TOXIC = "NON_TOXIC"
    TOXIC = "TOXIC"
    SEVERE_TOXIC = "SEVERE_TOXIC"
    OBSCENE = "OBSCENE"
    THREAT = "THREAT"
    INSULT = "INSULT"
    IDENTITY_HATE = "IDENTITY_HATE"

# Set metadata after class creation to avoid it becoming an enum member
ToxicityClassificationEnum._metadata = {
    "NON_TOXIC": {'description': 'Text is appropriate and non-harmful', 'meaning': 'SIO:001010', 'aliases': ['safe', 'clean', '0']},
    "TOXIC": {'description': 'Text contains harmful or inappropriate content', 'aliases': ['harmful', 'inappropriate', '1']},
    "SEVERE_TOXIC": {'description': 'Text contains severely harmful content'},
    "OBSCENE": {'description': 'Text contains obscene content'},
    "THREAT": {'description': 'Text contains threatening content'},
    "INSULT": {'description': 'Text contains insulting content'},
    "IDENTITY_HATE": {'description': 'Text contains identity-based hate'},
}

class IntentClassificationEnum(RichEnum):
    """
    Common chatbot/NLU intent categories
    """
    # Enum members
    GREETING = "GREETING"
    GOODBYE = "GOODBYE"
    THANKS = "THANKS"
    HELP = "HELP"
    INFORMATION = "INFORMATION"
    COMPLAINT = "COMPLAINT"
    FEEDBACK = "FEEDBACK"
    PURCHASE = "PURCHASE"
    CANCEL = "CANCEL"
    REFUND = "REFUND"

# Set metadata after class creation to avoid it becoming an enum member
IntentClassificationEnum._metadata = {
    "GREETING": {'description': 'User greeting or hello'},
    "GOODBYE": {'description': 'User saying goodbye'},
    "THANKS": {'description': 'User expressing gratitude'},
    "HELP": {'description': 'User requesting help or assistance'},
    "INFORMATION": {'description': 'User requesting information'},
    "COMPLAINT": {'description': 'User expressing dissatisfaction'},
    "FEEDBACK": {'description': 'User providing feedback'},
    "PURCHASE": {'description': 'User intent to buy or purchase'},
    "CANCEL": {'description': 'User intent to cancel'},
    "REFUND": {'description': 'User requesting refund'},
}

class SimpleSpatialDirection(RichEnum):
    """
    Basic spatial directional terms for general use
    """
    # Enum members
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    UP = "UP"
    DOWN = "DOWN"
    INWARD = "INWARD"
    OUTWARD = "OUTWARD"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    MIDDLE = "MIDDLE"

# Set metadata after class creation to avoid it becoming an enum member
SimpleSpatialDirection._metadata = {
    "LEFT": {'description': 'To the left side'},
    "RIGHT": {'description': 'To the right side'},
    "FORWARD": {'description': 'In the forward direction', 'annotations': {'aliases': 'ahead, front'}},
    "BACKWARD": {'description': 'In the backward direction', 'annotations': {'aliases': 'back, behind, rear'}},
    "UP": {'description': 'In the upward direction', 'annotations': {'aliases': 'above, upward'}},
    "DOWN": {'description': 'In the downward direction', 'annotations': {'aliases': 'below, downward'}},
    "INWARD": {'description': 'Toward the center or interior', 'annotations': {'aliases': 'medial, toward center'}},
    "OUTWARD": {'description': 'Away from the center or exterior', 'annotations': {'aliases': 'peripheral, away from center'}},
    "TOP": {'description': 'At or toward the top', 'annotations': {'aliases': 'upper, uppermost'}},
    "BOTTOM": {'description': 'At or toward the bottom', 'annotations': {'aliases': 'lower, lowermost'}},
    "MIDDLE": {'description': 'At or toward the middle', 'annotations': {'aliases': 'center, central'}},
}

class AnatomicalSide(RichEnum):
    """
    Anatomical sides as defined in the Biological Spatial Ontology (BSPO).
An anatomical region bounded by a plane perpendicular to an axis through the middle.
    """
    # Enum members
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ANTERIOR = "ANTERIOR"
    POSTERIOR = "POSTERIOR"
    DORSAL = "DORSAL"
    VENTRAL = "VENTRAL"
    LATERAL = "LATERAL"
    MEDIAL = "MEDIAL"
    PROXIMAL = "PROXIMAL"
    DISTAL = "DISTAL"
    APICAL = "APICAL"
    BASAL = "BASAL"
    SUPERFICIAL = "SUPERFICIAL"
    DEEP = "DEEP"
    SUPERIOR = "SUPERIOR"
    INFERIOR = "INFERIOR"
    IPSILATERAL = "IPSILATERAL"
    CONTRALATERAL = "CONTRALATERAL"
    CENTRAL = "CENTRAL"

# Set metadata after class creation to avoid it becoming an enum member
AnatomicalSide._metadata = {
    "LEFT": {'meaning': 'BSPO:0000000', 'aliases': ['left side']},
    "RIGHT": {'meaning': 'BSPO:0000007', 'aliases': ['right side']},
    "ANTERIOR": {'meaning': 'BSPO:0000055', 'annotations': {'aliases': 'front, rostral, cranial (in head region)'}, 'aliases': ['anterior side']},
    "POSTERIOR": {'meaning': 'BSPO:0000056', 'annotations': {'aliases': 'back, caudal'}, 'aliases': ['posterior side']},
    "DORSAL": {'meaning': 'BSPO:0000063', 'annotations': {'aliases': 'back (in vertebrates), upper (in humans)'}, 'aliases': ['dorsal side']},
    "VENTRAL": {'meaning': 'BSPO:0000068', 'annotations': {'aliases': 'belly, front (in vertebrates), lower (in humans)'}, 'aliases': ['ventral side']},
    "LATERAL": {'meaning': 'BSPO:0000066', 'annotations': {'aliases': 'side, outer'}, 'aliases': ['lateral side']},
    "MEDIAL": {'meaning': 'BSPO:0000067', 'annotations': {'aliases': 'inner, middle'}, 'aliases': ['medial side']},
    "PROXIMAL": {'meaning': 'BSPO:0000061', 'annotations': {'context': 'commonly used for limbs'}, 'aliases': ['proximal side']},
    "DISTAL": {'meaning': 'BSPO:0000062', 'annotations': {'context': 'commonly used for limbs'}, 'aliases': ['distal side']},
    "APICAL": {'meaning': 'BSPO:0000057', 'annotations': {'context': 'cells, organs, organisms'}, 'aliases': ['apical side']},
    "BASAL": {'meaning': 'BSPO:0000058', 'annotations': {'context': 'cells, organs, organisms'}, 'aliases': ['basal side']},
    "SUPERFICIAL": {'meaning': 'BSPO:0000004', 'annotations': {'aliases': 'external, outer'}, 'aliases': ['superficial side']},
    "DEEP": {'meaning': 'BSPO:0000003', 'annotations': {'aliases': 'internal, inner'}, 'aliases': ['deep side']},
    "SUPERIOR": {'meaning': 'BSPO:0000022', 'annotations': {'aliases': 'cranial (toward head), upper'}, 'aliases': ['superior side']},
    "INFERIOR": {'meaning': 'BSPO:0000025', 'annotations': {'aliases': 'caudal (toward tail), lower'}, 'aliases': ['inferior side']},
    "IPSILATERAL": {'meaning': 'BSPO:0000065', 'annotations': {'context': 'relative to a reference point'}, 'aliases': ['ipsilateral side']},
    "CONTRALATERAL": {'meaning': 'BSPO:0000060', 'annotations': {'context': 'relative to a reference point'}, 'aliases': ['contralateral side']},
    "CENTRAL": {'meaning': 'BSPO:0000059', 'annotations': {'aliases': 'middle'}, 'aliases': ['central side']},
}

class AnatomicalRegion(RichEnum):
    """
    Anatomical regions based on spatial position
    """
    # Enum members
    ANTERIOR_REGION = "ANTERIOR_REGION"
    POSTERIOR_REGION = "POSTERIOR_REGION"
    DORSAL_REGION = "DORSAL_REGION"
    VENTRAL_REGION = "VENTRAL_REGION"
    LATERAL_REGION = "LATERAL_REGION"
    MEDIAL_REGION = "MEDIAL_REGION"
    PROXIMAL_REGION = "PROXIMAL_REGION"
    DISTAL_REGION = "DISTAL_REGION"
    APICAL_REGION = "APICAL_REGION"
    BASAL_REGION = "BASAL_REGION"
    CENTRAL_REGION = "CENTRAL_REGION"
    PERIPHERAL_REGION = "PERIPHERAL_REGION"

# Set metadata after class creation to avoid it becoming an enum member
AnatomicalRegion._metadata = {
    "ANTERIOR_REGION": {'meaning': 'BSPO:0000071', 'aliases': ['anterior region']},
    "POSTERIOR_REGION": {'meaning': 'BSPO:0000072', 'aliases': ['posterior region']},
    "DORSAL_REGION": {'meaning': 'BSPO:0000079', 'aliases': ['dorsal region']},
    "VENTRAL_REGION": {'meaning': 'BSPO:0000084', 'aliases': ['ventral region']},
    "LATERAL_REGION": {'meaning': 'BSPO:0000082', 'aliases': ['lateral region']},
    "MEDIAL_REGION": {'meaning': 'BSPO:0000083', 'aliases': ['medial region']},
    "PROXIMAL_REGION": {'meaning': 'BSPO:0000077', 'aliases': ['proximal region']},
    "DISTAL_REGION": {'meaning': 'BSPO:0000078', 'aliases': ['distal region']},
    "APICAL_REGION": {'meaning': 'BSPO:0000073', 'aliases': ['apical region']},
    "BASAL_REGION": {'meaning': 'BSPO:0000074', 'aliases': ['basal region']},
    "CENTRAL_REGION": {'meaning': 'BSPO:0000075', 'aliases': ['central region']},
    "PERIPHERAL_REGION": {'meaning': 'BSPO:0000127', 'aliases': ['peripheral region']},
}

class AnatomicalAxis(RichEnum):
    """
    Anatomical axes defining spatial organization
    """
    # Enum members
    ANTERIOR_POSTERIOR = "ANTERIOR_POSTERIOR"
    DORSAL_VENTRAL = "DORSAL_VENTRAL"
    LEFT_RIGHT = "LEFT_RIGHT"
    PROXIMAL_DISTAL = "PROXIMAL_DISTAL"
    APICAL_BASAL = "APICAL_BASAL"

# Set metadata after class creation to avoid it becoming an enum member
AnatomicalAxis._metadata = {
    "ANTERIOR_POSTERIOR": {'meaning': 'BSPO:0000013', 'annotations': {'aliases': 'AP axis, rostrocaudal axis'}, 'aliases': ['anterior-posterior axis']},
    "DORSAL_VENTRAL": {'meaning': 'BSPO:0000016', 'annotations': {'aliases': 'DV axis'}, 'aliases': ['dorsal-ventral axis']},
    "LEFT_RIGHT": {'meaning': 'BSPO:0000017', 'annotations': {'aliases': 'LR axis, mediolateral axis'}, 'aliases': ['left-right axis']},
    "PROXIMAL_DISTAL": {'meaning': 'BSPO:0000018', 'annotations': {'context': 'commonly used for appendages'}, 'aliases': ['transverse plane']},
    "APICAL_BASAL": {'meaning': 'BSPO:0000023', 'annotations': {'context': 'epithelial cells, plant structures'}, 'aliases': ['apical-basal gradient']},
}

class AnatomicalPlane(RichEnum):
    """
    Standard anatomical planes for sectioning
    """
    # Enum members
    SAGITTAL = "SAGITTAL"
    MIDSAGITTAL = "MIDSAGITTAL"
    PARASAGITTAL = "PARASAGITTAL"
    CORONAL = "CORONAL"
    TRANSVERSE = "TRANSVERSE"
    OBLIQUE = "OBLIQUE"

# Set metadata after class creation to avoid it becoming an enum member
AnatomicalPlane._metadata = {
    "SAGITTAL": {'meaning': 'BSPO:0000417', 'annotations': {'orientation': 'parallel to the median plane'}, 'aliases': ['sagittal plane']},
    "MIDSAGITTAL": {'meaning': 'BSPO:0000009', 'annotations': {'aliases': 'median plane', 'note': 'divides body into equal left and right halves'}, 'aliases': ['midsagittal plane']},
    "PARASAGITTAL": {'meaning': 'BSPO:0000008', 'annotations': {'note': 'any sagittal plane not at midline'}, 'aliases': ['parasagittal plane']},
    "CORONAL": {'meaning': 'BSPO:0000019', 'annotations': {'aliases': 'frontal plane', 'orientation': 'perpendicular to sagittal plane'}, 'aliases': ['horizontal plane']},
    "TRANSVERSE": {'meaning': 'BSPO:0000018', 'annotations': {'aliases': 'horizontal plane, axial plane', 'orientation': 'perpendicular to longitudinal axis'}, 'aliases': ['transverse plane']},
    "OBLIQUE": {'description': 'Any plane not parallel to sagittal, coronal, or transverse planes', 'annotations': {'note': 'angled section'}},
}

class SpatialRelationship(RichEnum):
    """
    Spatial relationships between anatomical structures
    """
    # Enum members
    ADJACENT_TO = "ADJACENT_TO"
    ANTERIOR_TO = "ANTERIOR_TO"
    POSTERIOR_TO = "POSTERIOR_TO"
    DORSAL_TO = "DORSAL_TO"
    VENTRAL_TO = "VENTRAL_TO"
    LATERAL_TO = "LATERAL_TO"
    MEDIAL_TO = "MEDIAL_TO"
    PROXIMAL_TO = "PROXIMAL_TO"
    DISTAL_TO = "DISTAL_TO"
    SUPERFICIAL_TO = "SUPERFICIAL_TO"
    DEEP_TO = "DEEP_TO"
    SURROUNDS = "SURROUNDS"
    WITHIN = "WITHIN"
    BETWEEN = "BETWEEN"

# Set metadata after class creation to avoid it becoming an enum member
SpatialRelationship._metadata = {
    "ADJACENT_TO": {'meaning': 'RO:0002220', 'aliases': ['adjacent to']},
    "ANTERIOR_TO": {'meaning': 'BSPO:0000096', 'aliases': ['anterior to']},
    "POSTERIOR_TO": {'meaning': 'BSPO:0000099', 'aliases': ['posterior to']},
    "DORSAL_TO": {'meaning': 'BSPO:0000098', 'aliases': ['dorsal to']},
    "VENTRAL_TO": {'meaning': 'BSPO:0000102', 'aliases': ['ventral to']},
    "LATERAL_TO": {'meaning': 'BSPO:0000114', 'aliases': ['lateral to']},
    "MEDIAL_TO": {'meaning': 'BSPO:0000115', 'aliases': ['X medial to y if x is closer to the midsagittal plane than y.']},
    "PROXIMAL_TO": {'meaning': 'BSPO:0000100', 'aliases': ['proximal to']},
    "DISTAL_TO": {'meaning': 'BSPO:0000097', 'aliases': ['distal to']},
    "SUPERFICIAL_TO": {'meaning': 'BSPO:0000108', 'aliases': ['superficial to']},
    "DEEP_TO": {'meaning': 'BSPO:0000107', 'aliases': ['deep to']},
    "SURROUNDS": {'meaning': 'RO:0002221', 'aliases': ['surrounds']},
    "WITHIN": {'description': 'Inside or contained by', 'annotations': {'inverse_of': 'contains'}},
    "BETWEEN": {'description': 'In the space separating two structures', 'annotations': {'note': 'requires two reference points'}},
}

class CellPolarity(RichEnum):
    """
    Spatial polarity in cells and tissues
    """
    # Enum members
    APICAL = "APICAL"
    BASAL = "BASAL"
    LATERAL = "LATERAL"
    APICAL_LATERAL = "APICAL_LATERAL"
    BASAL_LATERAL = "BASAL_LATERAL"
    LEADING_EDGE = "LEADING_EDGE"
    TRAILING_EDGE = "TRAILING_EDGE"
    PROXIMAL_POLE = "PROXIMAL_POLE"
    DISTAL_POLE = "DISTAL_POLE"

# Set metadata after class creation to avoid it becoming an enum member
CellPolarity._metadata = {
    "APICAL": {'description': 'The free surface of an epithelial cell', 'annotations': {'location': 'typically faces lumen or external environment'}},
    "BASAL": {'description': 'The attached surface of an epithelial cell', 'annotations': {'location': 'typically attached to basement membrane'}},
    "LATERAL": {'description': 'The sides of an epithelial cell', 'annotations': {'location': 'faces neighboring cells'}},
    "APICAL_LATERAL": {'description': 'Junction between apical and lateral surfaces'},
    "BASAL_LATERAL": {'description': 'Junction between basal and lateral surfaces'},
    "LEADING_EDGE": {'description': 'Front of a migrating cell', 'annotations': {'context': 'cell migration'}},
    "TRAILING_EDGE": {'description': 'Rear of a migrating cell', 'annotations': {'context': 'cell migration'}},
    "PROXIMAL_POLE": {'description': 'Pole closer to the cell body', 'annotations': {'context': 'neurons, polarized cells'}},
    "DISTAL_POLE": {'description': 'Pole further from the cell body', 'annotations': {'context': 'neurons, polarized cells'}},
}

class CrystalSystemEnum(RichEnum):
    """
    The seven crystal systems in crystallography
    """
    # Enum members
    TRICLINIC = "TRICLINIC"
    MONOCLINIC = "MONOCLINIC"
    ORTHORHOMBIC = "ORTHORHOMBIC"
    TETRAGONAL = "TETRAGONAL"
    TRIGONAL = "TRIGONAL"
    HEXAGONAL = "HEXAGONAL"
    CUBIC = "CUBIC"

# Set metadata after class creation to avoid it becoming an enum member
CrystalSystemEnum._metadata = {
    "TRICLINIC": {'description': 'Crystal system with no symmetry constraints (a≠b≠c, α≠β≠γ≠90°)', 'meaning': 'ENM:9000022', 'aliases': ['anorthic']},
    "MONOCLINIC": {'description': 'Crystal system with one twofold axis of symmetry (a≠b≠c, α=γ=90°≠β)', 'meaning': 'ENM:9000029'},
    "ORTHORHOMBIC": {'description': 'Crystal system with three mutually perpendicular axes (a≠b≠c, α=β=γ=90°)', 'meaning': 'ENM:9000031', 'aliases': ['rhombic']},
    "TETRAGONAL": {'description': 'Crystal system with one fourfold axis (a=b≠c, α=β=γ=90°)', 'meaning': 'ENM:9000032'},
    "TRIGONAL": {'description': 'Crystal system with one threefold axis (a=b=c, α=β=γ≠90°)', 'meaning': 'ENM:9000054', 'aliases': ['rhombohedral']},
    "HEXAGONAL": {'description': 'Crystal system with one sixfold axis (a=b≠c, α=β=90°, γ=120°)', 'meaning': 'PATO:0002509'},
    "CUBIC": {'description': 'Crystal system with four threefold axes (a=b=c, α=β=γ=90°)', 'meaning': 'ENM:9000035', 'aliases': ['isometric']},
}

class BravaisLatticeEnum(RichEnum):
    """
    The 14 Bravais lattices describing all possible crystal lattices
    """
    # Enum members
    PRIMITIVE_TRICLINIC = "PRIMITIVE_TRICLINIC"
    PRIMITIVE_MONOCLINIC = "PRIMITIVE_MONOCLINIC"
    BASE_CENTERED_MONOCLINIC = "BASE_CENTERED_MONOCLINIC"
    PRIMITIVE_ORTHORHOMBIC = "PRIMITIVE_ORTHORHOMBIC"
    BASE_CENTERED_ORTHORHOMBIC = "BASE_CENTERED_ORTHORHOMBIC"
    BODY_CENTERED_ORTHORHOMBIC = "BODY_CENTERED_ORTHORHOMBIC"
    FACE_CENTERED_ORTHORHOMBIC = "FACE_CENTERED_ORTHORHOMBIC"
    PRIMITIVE_TETRAGONAL = "PRIMITIVE_TETRAGONAL"
    BODY_CENTERED_TETRAGONAL = "BODY_CENTERED_TETRAGONAL"
    PRIMITIVE_TRIGONAL = "PRIMITIVE_TRIGONAL"
    PRIMITIVE_HEXAGONAL = "PRIMITIVE_HEXAGONAL"
    PRIMITIVE_CUBIC = "PRIMITIVE_CUBIC"
    BODY_CENTERED_CUBIC = "BODY_CENTERED_CUBIC"
    FACE_CENTERED_CUBIC = "FACE_CENTERED_CUBIC"

# Set metadata after class creation to avoid it becoming an enum member
BravaisLatticeEnum._metadata = {
    "PRIMITIVE_TRICLINIC": {'description': 'Primitive triclinic lattice (aP)', 'aliases': ['aP']},
    "PRIMITIVE_MONOCLINIC": {'description': 'Primitive monoclinic lattice (mP)', 'aliases': ['mP']},
    "BASE_CENTERED_MONOCLINIC": {'description': 'Base-centered monoclinic lattice (mC)', 'aliases': ['mC', 'mS']},
    "PRIMITIVE_ORTHORHOMBIC": {'description': 'Primitive orthorhombic lattice (oP)', 'aliases': ['oP']},
    "BASE_CENTERED_ORTHORHOMBIC": {'description': 'Base-centered orthorhombic lattice (oC)', 'aliases': ['oC', 'oS']},
    "BODY_CENTERED_ORTHORHOMBIC": {'description': 'Body-centered orthorhombic lattice (oI)', 'aliases': ['oI']},
    "FACE_CENTERED_ORTHORHOMBIC": {'description': 'Face-centered orthorhombic lattice (oF)', 'aliases': ['oF']},
    "PRIMITIVE_TETRAGONAL": {'description': 'Primitive tetragonal lattice (tP)', 'aliases': ['tP']},
    "BODY_CENTERED_TETRAGONAL": {'description': 'Body-centered tetragonal lattice (tI)', 'aliases': ['tI']},
    "PRIMITIVE_TRIGONAL": {'description': 'Primitive trigonal/rhombohedral lattice (hR)', 'aliases': ['hR']},
    "PRIMITIVE_HEXAGONAL": {'description': 'Primitive hexagonal lattice (hP)', 'aliases': ['hP']},
    "PRIMITIVE_CUBIC": {'description': 'Simple cubic lattice (cP)', 'aliases': ['cP', 'SC']},
    "BODY_CENTERED_CUBIC": {'description': 'Body-centered cubic lattice (cI)', 'aliases': ['cI', 'BCC']},
    "FACE_CENTERED_CUBIC": {'description': 'Face-centered cubic lattice (cF)', 'aliases': ['cF', 'FCC']},
}

class ElectricalConductivityEnum(RichEnum):
    """
    Classification of materials by electrical conductivity
    """
    # Enum members
    CONDUCTOR = "CONDUCTOR"
    SEMICONDUCTOR = "SEMICONDUCTOR"
    INSULATOR = "INSULATOR"
    SUPERCONDUCTOR = "SUPERCONDUCTOR"

# Set metadata after class creation to avoid it becoming an enum member
ElectricalConductivityEnum._metadata = {
    "CONDUCTOR": {'description': 'Material with high electrical conductivity (resistivity < 10^-5 Ω·m)', 'aliases': ['metal']},
    "SEMICONDUCTOR": {'description': 'Material with intermediate electrical conductivity (10^-5 to 10^8 Ω·m)', 'meaning': 'NCIT:C172788', 'aliases': ['semi']},
    "INSULATOR": {'description': 'Material with very low electrical conductivity (resistivity > 10^8 Ω·m)', 'aliases': ['dielectric']},
    "SUPERCONDUCTOR": {'description': 'Material with zero electrical resistance below critical temperature'},
}

class MagneticPropertyEnum(RichEnum):
    """
    Classification of materials by magnetic properties
    """
    # Enum members
    DIAMAGNETIC = "DIAMAGNETIC"
    PARAMAGNETIC = "PARAMAGNETIC"
    FERROMAGNETIC = "FERROMAGNETIC"
    FERRIMAGNETIC = "FERRIMAGNETIC"
    ANTIFERROMAGNETIC = "ANTIFERROMAGNETIC"

# Set metadata after class creation to avoid it becoming an enum member
MagneticPropertyEnum._metadata = {
    "DIAMAGNETIC": {'description': 'Weakly repelled by magnetic fields'},
    "PARAMAGNETIC": {'description': 'Weakly attracted to magnetic fields'},
    "FERROMAGNETIC": {'description': 'Strongly attracted to magnetic fields, can be permanently magnetized'},
    "FERRIMAGNETIC": {'description': 'Similar to ferromagnetic but with opposing magnetic moments'},
    "ANTIFERROMAGNETIC": {'description': 'Adjacent magnetic moments cancel each other'},
}

class OpticalPropertyEnum(RichEnum):
    """
    Optical properties of materials
    """
    # Enum members
    TRANSPARENT = "TRANSPARENT"
    TRANSLUCENT = "TRANSLUCENT"
    OPAQUE = "OPAQUE"
    REFLECTIVE = "REFLECTIVE"
    ABSORBING = "ABSORBING"
    FLUORESCENT = "FLUORESCENT"
    PHOSPHORESCENT = "PHOSPHORESCENT"

# Set metadata after class creation to avoid it becoming an enum member
OpticalPropertyEnum._metadata = {
    "TRANSPARENT": {'description': 'Allows light to pass through with minimal scattering', 'meaning': 'PATO:0000964'},
    "TRANSLUCENT": {'description': 'Allows light to pass through but with significant scattering'},
    "OPAQUE": {'description': 'Does not allow light to pass through', 'meaning': 'PATO:0000963'},
    "REFLECTIVE": {'description': 'Reflects most incident light'},
    "ABSORBING": {'description': 'Absorbs most incident light'},
    "FLUORESCENT": {'description': 'Emits light when excited by radiation'},
    "PHOSPHORESCENT": {'description': 'Continues to emit light after excitation stops'},
}

class ThermalConductivityEnum(RichEnum):
    """
    Classification by thermal conductivity
    """
    # Enum members
    HIGH_THERMAL_CONDUCTOR = "HIGH_THERMAL_CONDUCTOR"
    MODERATE_THERMAL_CONDUCTOR = "MODERATE_THERMAL_CONDUCTOR"
    THERMAL_INSULATOR = "THERMAL_INSULATOR"

# Set metadata after class creation to avoid it becoming an enum member
ThermalConductivityEnum._metadata = {
    "HIGH_THERMAL_CONDUCTOR": {'description': 'High thermal conductivity (>100 W/m·K)', 'aliases': ['thermal conductor']},
    "MODERATE_THERMAL_CONDUCTOR": {'description': 'Moderate thermal conductivity (1-100 W/m·K)'},
    "THERMAL_INSULATOR": {'description': 'Low thermal conductivity (<1 W/m·K)', 'aliases': ['thermal barrier']},
}

class MechanicalBehaviorEnum(RichEnum):
    """
    Mechanical behavior of materials under stress
    """
    # Enum members
    ELASTIC = "ELASTIC"
    PLASTIC = "PLASTIC"
    BRITTLE = "BRITTLE"
    DUCTILE = "DUCTILE"
    MALLEABLE = "MALLEABLE"
    TOUGH = "TOUGH"
    VISCOELASTIC = "VISCOELASTIC"

# Set metadata after class creation to avoid it becoming an enum member
MechanicalBehaviorEnum._metadata = {
    "ELASTIC": {'description': 'Returns to original shape after stress removal', 'meaning': 'PATO:0001171'},
    "PLASTIC": {'description': 'Undergoes permanent deformation under stress', 'meaning': 'PATO:0001172'},
    "BRITTLE": {'description': 'Breaks without significant plastic deformation', 'meaning': 'PATO:0002477'},
    "DUCTILE": {'description': 'Can be drawn into wires, undergoes large plastic deformation'},
    "MALLEABLE": {'description': 'Can be hammered into sheets'},
    "TOUGH": {'description': 'High resistance to fracture'},
    "VISCOELASTIC": {'description': 'Exhibits both viscous and elastic characteristics'},
}

class MicroscopyMethodEnum(RichEnum):
    """
    Microscopy techniques for material characterization
    """
    # Enum members
    SEM = "SEM"
    TEM = "TEM"
    STEM = "STEM"
    AFM = "AFM"
    STM = "STM"
    OPTICAL = "OPTICAL"
    CONFOCAL = "CONFOCAL"

# Set metadata after class creation to avoid it becoming an enum member
MicroscopyMethodEnum._metadata = {
    "SEM": {'description': 'Scanning Electron Microscopy', 'meaning': 'CHMO:0000073', 'aliases': ['Scanning Electron Microscopy', 'SEM']},
    "TEM": {'description': 'Transmission Electron Microscopy', 'meaning': 'CHMO:0000080', 'aliases': ['Transmission Electron Microscopy', 'TEM']},
    "STEM": {'description': 'Scanning Transmission Electron Microscopy', 'aliases': ['Scanning Transmission Electron Microscopy']},
    "AFM": {'description': 'Atomic Force Microscopy', 'meaning': 'CHMO:0000113', 'aliases': ['Atomic Force Microscopy', 'AFM']},
    "STM": {'description': 'Scanning Tunneling Microscopy', 'meaning': 'CHMO:0000132', 'aliases': ['Scanning Tunneling Microscopy', 'STM']},
    "OPTICAL": {'description': 'Optical/Light Microscopy', 'meaning': 'CHMO:0000102', 'aliases': ['Light Microscopy', 'Optical Microscopy', 'OPTICAL']},
    "CONFOCAL": {'description': 'Confocal Laser Scanning Microscopy', 'meaning': 'CHMO:0000089', 'aliases': ['CLSM', 'CONFOCAL', 'Confocal']},
}

class SpectroscopyMethodEnum(RichEnum):
    """
    Spectroscopy techniques for material analysis
    """
    # Enum members
    XRD = "XRD"
    XPS = "XPS"
    EDS = "EDS"
    FTIR = "FTIR"
    RAMAN = "RAMAN"
    UV_VIS = "UV_VIS"
    NMR = "NMR"
    XRF = "XRF"

# Set metadata after class creation to avoid it becoming an enum member
SpectroscopyMethodEnum._metadata = {
    "XRD": {'description': 'X-ray Diffraction', 'meaning': 'CHMO:0000156', 'aliases': ['X-ray Diffraction']},
    "XPS": {'description': 'X-ray Photoelectron Spectroscopy', 'meaning': 'CHMO:0000404', 'aliases': ['ESCA', 'X-ray Photoelectron Spectroscopy']},
    "EDS": {'description': 'Energy Dispersive X-ray Spectroscopy', 'meaning': 'CHMO:0000309', 'aliases': ['EDX', 'EDXS', 'EDS']},
    "FTIR": {'description': 'Fourier Transform Infrared Spectroscopy', 'meaning': 'CHMO:0000636', 'aliases': ['FT-IR', 'FTIR']},
    "RAMAN": {'description': 'Raman Spectroscopy', 'meaning': 'CHMO:0000656', 'aliases': ['Raman Spectroscopy']},
    "UV_VIS": {'description': 'Ultraviolet-Visible Spectroscopy', 'meaning': 'CHMO:0000292', 'aliases': ['UV-Visible', 'UV-Vis', 'UV_VIS']},
    "NMR": {'description': 'Nuclear Magnetic Resonance Spectroscopy', 'meaning': 'CHMO:0000591', 'aliases': ['Nuclear Magnetic Resonance', 'NMR']},
    "XRF": {'description': 'X-ray Fluorescence Spectroscopy', 'meaning': 'CHMO:0000307', 'aliases': ['X-ray Fluorescence', 'XRF']},
}

class ThermalAnalysisMethodEnum(RichEnum):
    """
    Thermal analysis techniques
    """
    # Enum members
    DSC = "DSC"
    TGA = "TGA"
    DTA = "DTA"
    TMA = "TMA"
    DMTA = "DMTA"

# Set metadata after class creation to avoid it becoming an enum member
ThermalAnalysisMethodEnum._metadata = {
    "DSC": {'description': 'Differential Scanning Calorimetry', 'meaning': 'CHMO:0000684', 'aliases': ['Differential Scanning Calorimetry']},
    "TGA": {'description': 'Thermogravimetric Analysis', 'meaning': 'CHMO:0000690', 'aliases': ['Thermogravimetric Analysis', 'TGA']},
    "DTA": {'description': 'Differential Thermal Analysis', 'meaning': 'CHMO:0000687', 'aliases': ['Differential Thermal Analysis']},
    "TMA": {'description': 'Thermomechanical Analysis', 'aliases': ['Thermomechanical Analysis']},
    "DMTA": {'description': 'Dynamic Mechanical Thermal Analysis', 'aliases': ['DMA', 'Dynamic Mechanical Analysis']},
}

class MechanicalTestingMethodEnum(RichEnum):
    """
    Mechanical testing methods
    """
    # Enum members
    TENSILE = "TENSILE"
    COMPRESSION = "COMPRESSION"
    HARDNESS = "HARDNESS"
    IMPACT = "IMPACT"
    FATIGUE = "FATIGUE"
    CREEP = "CREEP"
    FRACTURE_TOUGHNESS = "FRACTURE_TOUGHNESS"
    NANOINDENTATION = "NANOINDENTATION"

# Set metadata after class creation to avoid it becoming an enum member
MechanicalTestingMethodEnum._metadata = {
    "TENSILE": {'description': 'Tensile strength testing'},
    "COMPRESSION": {'description': 'Compression strength testing'},
    "HARDNESS": {'description': 'Hardness testing (Vickers, Rockwell, Brinell)'},
    "IMPACT": {'description': 'Impact resistance testing (Charpy, Izod)'},
    "FATIGUE": {'description': 'Fatigue testing under cyclic loading'},
    "CREEP": {'description': 'Creep testing under sustained load'},
    "FRACTURE_TOUGHNESS": {'description': 'Fracture toughness testing'},
    "NANOINDENTATION": {'description': 'Nanoindentation for nanoscale mechanical properties'},
}

class MaterialClassEnum(RichEnum):
    """
    Major classes of materials
    """
    # Enum members
    METAL = "METAL"
    CERAMIC = "CERAMIC"
    POLYMER = "POLYMER"
    COMPOSITE = "COMPOSITE"
    SEMICONDUCTOR = "SEMICONDUCTOR"
    BIOMATERIAL = "BIOMATERIAL"
    NANOMATERIAL = "NANOMATERIAL"

# Set metadata after class creation to avoid it becoming an enum member
MaterialClassEnum._metadata = {
    "METAL": {'description': 'Metallic materials with metallic bonding', 'meaning': 'ENVO:01001069', 'aliases': ['Metal', 'METAL']},
    "CERAMIC": {'description': 'Inorganic non-metallic materials', 'meaning': 'ENVO:03501307'},
    "POLYMER": {'description': 'Large molecules composed of repeating units', 'meaning': 'CHEBI:60027'},
    "COMPOSITE": {'description': 'Materials made from two or more constituent materials', 'meaning': 'NCIT:C61520'},
    "SEMICONDUCTOR": {'description': 'Materials with electrical conductivity between conductors and insulators', 'meaning': 'NCIT:C172788'},
    "BIOMATERIAL": {'description': 'Materials designed to interact with biological systems', 'meaning': 'NCIT:C16338', 'aliases': ['Biomaterial', 'BIOMATERIAL']},
    "NANOMATERIAL": {'description': 'Materials with at least one dimension in nanoscale (1-100 nm)', 'meaning': 'NCIT:C62371'},
}

class PolymerTypeEnum(RichEnum):
    """
    Types of polymer materials
    """
    # Enum members
    THERMOPLASTIC = "THERMOPLASTIC"
    THERMOSET = "THERMOSET"
    ELASTOMER = "ELASTOMER"
    BIOPOLYMER = "BIOPOLYMER"
    CONDUCTING_POLYMER = "CONDUCTING_POLYMER"

# Set metadata after class creation to avoid it becoming an enum member
PolymerTypeEnum._metadata = {
    "THERMOPLASTIC": {'description': 'Polymer that becomes moldable above specific temperature', 'meaning': 'PATO:0040070'},
    "THERMOSET": {'description': 'Polymer that irreversibly hardens when cured', 'meaning': 'ENVO:06105005', 'aliases': ['thermosetting polymer', 'Thermoset', 'THERMOSET']},
    "ELASTOMER": {'description': 'Polymer with elastic properties', 'meaning': 'SNOMED:261777007', 'aliases': ['rubber']},
    "BIOPOLYMER": {'description': 'Polymer produced by living organisms', 'meaning': 'NCIT:C73478'},
    "CONDUCTING_POLYMER": {'description': 'Polymer that conducts electricity', 'aliases': ['conducting polymer']},
}

class MetalTypeEnum(RichEnum):
    """
    Types of metallic materials
    """
    # Enum members
    FERROUS = "FERROUS"
    NON_FERROUS = "NON_FERROUS"
    NOBLE_METAL = "NOBLE_METAL"
    REFRACTORY_METAL = "REFRACTORY_METAL"
    LIGHT_METAL = "LIGHT_METAL"
    HEAVY_METAL = "HEAVY_METAL"

# Set metadata after class creation to avoid it becoming an enum member
MetalTypeEnum._metadata = {
    "FERROUS": {'description': 'Iron-based metals and alloys', 'meaning': 'SNOMED:264354006', 'aliases': ['iron-based']},
    "NON_FERROUS": {'description': 'Metals and alloys not containing iron', 'meaning': 'SNOMED:264879001'},
    "NOBLE_METAL": {'description': 'Metals resistant to corrosion and oxidation'},
    "REFRACTORY_METAL": {'description': 'Metals with very high melting points (>2000°C)'},
    "LIGHT_METAL": {'description': 'Low density metals (density < 5 g/cm³)', 'meaning': 'SNOMED:65436002'},
    "HEAVY_METAL": {'description': 'High density metals (density > 5 g/cm³)', 'meaning': 'CHEBI:5631'},
}

class CompositeTypeEnum(RichEnum):
    """
    Types of composite materials
    """
    # Enum members
    FIBER_REINFORCED = "FIBER_REINFORCED"
    PARTICLE_REINFORCED = "PARTICLE_REINFORCED"
    LAMINAR_COMPOSITE = "LAMINAR_COMPOSITE"
    METAL_MATRIX_COMPOSITE = "METAL_MATRIX_COMPOSITE"
    CERAMIC_MATRIX_COMPOSITE = "CERAMIC_MATRIX_COMPOSITE"
    POLYMER_MATRIX_COMPOSITE = "POLYMER_MATRIX_COMPOSITE"

# Set metadata after class creation to avoid it becoming an enum member
CompositeTypeEnum._metadata = {
    "FIBER_REINFORCED": {'description': 'Composite with fiber reinforcement', 'aliases': ['FRC']},
    "PARTICLE_REINFORCED": {'description': 'Composite with particle reinforcement'},
    "LAMINAR_COMPOSITE": {'description': 'Composite with layered structure', 'aliases': ['laminate']},
    "METAL_MATRIX_COMPOSITE": {'description': 'Composite with metal matrix', 'aliases': ['MMC']},
    "CERAMIC_MATRIX_COMPOSITE": {'description': 'Composite with ceramic matrix', 'aliases': ['CMC']},
    "POLYMER_MATRIX_COMPOSITE": {'description': 'Composite with polymer matrix', 'aliases': ['PMC']},
}

class SynthesisMethodEnum(RichEnum):
    """
    Common material synthesis and processing methods
    """
    # Enum members
    SOL_GEL = "SOL_GEL"
    HYDROTHERMAL = "HYDROTHERMAL"
    SOLVOTHERMAL = "SOLVOTHERMAL"
    CVD = "CVD"
    PVD = "PVD"
    ALD = "ALD"
    ELECTRODEPOSITION = "ELECTRODEPOSITION"
    BALL_MILLING = "BALL_MILLING"
    PRECIPITATION = "PRECIPITATION"
    SINTERING = "SINTERING"
    MELT_PROCESSING = "MELT_PROCESSING"
    SOLUTION_CASTING = "SOLUTION_CASTING"
    SPIN_COATING = "SPIN_COATING"
    DIP_COATING = "DIP_COATING"
    SPRAY_COATING = "SPRAY_COATING"

# Set metadata after class creation to avoid it becoming an enum member
SynthesisMethodEnum._metadata = {
    "SOL_GEL": {'description': 'Synthesis from solution through gel formation', 'aliases': ['sol-gel process']},
    "HYDROTHERMAL": {'description': 'Synthesis using high temperature aqueous solutions', 'aliases': ['hydrothermal synthesis']},
    "SOLVOTHERMAL": {'description': 'Synthesis using non-aqueous solvents at high temperature/pressure'},
    "CVD": {'description': 'Chemical Vapor Deposition', 'meaning': 'CHMO:0001314', 'aliases': ['Chemical Vapor Deposition', 'CVD']},
    "PVD": {'description': 'Physical Vapor Deposition', 'meaning': 'CHMO:0001356', 'aliases': ['Physical Vapor Deposition', 'PVD']},
    "ALD": {'description': 'Atomic Layer Deposition', 'aliases': ['Atomic Layer Deposition']},
    "ELECTRODEPOSITION": {'description': 'Deposition using electric current', 'meaning': 'CHMO:0001331', 'aliases': ['electroplating', 'Electrodeposition', 'ELECTRODEPOSITION']},
    "BALL_MILLING": {'description': 'Mechanical alloying using ball mill', 'aliases': ['mechanical alloying']},
    "PRECIPITATION": {'description': 'Formation of solid from solution', 'meaning': 'CHMO:0001688', 'aliases': ['Precipitation', 'PRECIPITATION']},
    "SINTERING": {'description': 'Compacting and forming solid mass by heat/pressure'},
    "MELT_PROCESSING": {'description': 'Processing from molten state', 'aliases': ['melt casting']},
    "SOLUTION_CASTING": {'description': 'Casting from solution'},
    "SPIN_COATING": {'description': 'Coating by spinning substrate', 'meaning': 'CHMO:0001472'},
    "DIP_COATING": {'description': 'Coating by dipping in solution', 'meaning': 'CHMO:0001471'},
    "SPRAY_COATING": {'description': 'Coating by spraying'},
}

class CrystalGrowthMethodEnum(RichEnum):
    """
    Methods for growing single crystals
    """
    # Enum members
    CZOCHRALSKI = "CZOCHRALSKI"
    BRIDGMAN = "BRIDGMAN"
    FLOAT_ZONE = "FLOAT_ZONE"
    FLUX_GROWTH = "FLUX_GROWTH"
    VAPOR_TRANSPORT = "VAPOR_TRANSPORT"
    HYDROTHERMAL_GROWTH = "HYDROTHERMAL_GROWTH"
    LPE = "LPE"
    MBE = "MBE"
    MOCVD = "MOCVD"

# Set metadata after class creation to avoid it becoming an enum member
CrystalGrowthMethodEnum._metadata = {
    "CZOCHRALSKI": {'description': 'Crystal pulling from melt', 'aliases': ['CZ', 'crystal pulling']},
    "BRIDGMAN": {'description': 'Directional solidification method', 'aliases': ['Bridgman-Stockbarger']},
    "FLOAT_ZONE": {'description': 'Zone melting without crucible', 'aliases': ['FZ', 'zone refining']},
    "FLUX_GROWTH": {'description': 'Crystal growth from high temperature solution'},
    "VAPOR_TRANSPORT": {'description': 'Crystal growth via vapor phase transport', 'aliases': ['CVT']},
    "HYDROTHERMAL_GROWTH": {'description': 'Crystal growth in aqueous solution under pressure'},
    "LPE": {'description': 'Liquid Phase Epitaxy', 'aliases': ['Liquid Phase Epitaxy']},
    "MBE": {'description': 'Molecular Beam Epitaxy', 'meaning': 'CHMO:0001341', 'aliases': ['Molecular Beam Epitaxy', 'MBE']},
    "MOCVD": {'description': 'Metal-Organic Chemical Vapor Deposition', 'aliases': ['MOVPE']},
}

class AdditiveManufacturingEnum(RichEnum):
    """
    3D printing and additive manufacturing methods
    """
    # Enum members
    FDM = "FDM"
    SLA = "SLA"
    SLS = "SLS"
    SLM = "SLM"
    EBM = "EBM"
    BINDER_JETTING = "BINDER_JETTING"
    MATERIAL_JETTING = "MATERIAL_JETTING"
    DED = "DED"

# Set metadata after class creation to avoid it becoming an enum member
AdditiveManufacturingEnum._metadata = {
    "FDM": {'description': 'Fused Deposition Modeling', 'aliases': ['FFF', 'Fused Filament Fabrication']},
    "SLA": {'description': 'Stereolithography', 'aliases': ['Stereolithography']},
    "SLS": {'description': 'Selective Laser Sintering', 'aliases': ['Selective Laser Sintering']},
    "SLM": {'description': 'Selective Laser Melting', 'aliases': ['Selective Laser Melting']},
    "EBM": {'description': 'Electron Beam Melting', 'aliases': ['Electron Beam Melting']},
    "BINDER_JETTING": {'description': 'Powder bed with liquid binder'},
    "MATERIAL_JETTING": {'description': 'Droplet deposition of materials', 'aliases': ['PolyJet']},
    "DED": {'description': 'Directed Energy Deposition', 'aliases': ['Directed Energy Deposition']},
}

class TraditionalPigmentEnum(RichEnum):
    """
    Traditional artist pigments and their colors
    """
    # Enum members
    TITANIUM_WHITE = "TITANIUM_WHITE"
    ZINC_WHITE = "ZINC_WHITE"
    LEAD_WHITE = "LEAD_WHITE"
    CADMIUM_YELLOW = "CADMIUM_YELLOW"
    CHROME_YELLOW = "CHROME_YELLOW"
    NAPLES_YELLOW = "NAPLES_YELLOW"
    YELLOW_OCHRE = "YELLOW_OCHRE"
    CADMIUM_ORANGE = "CADMIUM_ORANGE"
    CADMIUM_RED = "CADMIUM_RED"
    VERMILION = "VERMILION"
    ALIZARIN_CRIMSON = "ALIZARIN_CRIMSON"
    CARMINE = "CARMINE"
    BURNT_SIENNA = "BURNT_SIENNA"
    RAW_SIENNA = "RAW_SIENNA"
    BURNT_UMBER = "BURNT_UMBER"
    RAW_UMBER = "RAW_UMBER"
    VAN_DYKE_BROWN = "VAN_DYKE_BROWN"
    PRUSSIAN_BLUE = "PRUSSIAN_BLUE"
    ULTRAMARINE = "ULTRAMARINE"
    COBALT_BLUE = "COBALT_BLUE"
    CERULEAN_BLUE = "CERULEAN_BLUE"
    PHTHALO_BLUE = "PHTHALO_BLUE"
    VIRIDIAN = "VIRIDIAN"
    CHROME_GREEN = "CHROME_GREEN"
    PHTHALO_GREEN = "PHTHALO_GREEN"
    TERRE_VERTE = "TERRE_VERTE"
    TYRIAN_PURPLE = "TYRIAN_PURPLE"
    MANGANESE_VIOLET = "MANGANESE_VIOLET"
    MARS_BLACK = "MARS_BLACK"
    IVORY_BLACK = "IVORY_BLACK"
    LAMP_BLACK = "LAMP_BLACK"

# Set metadata after class creation to avoid it becoming an enum member
TraditionalPigmentEnum._metadata = {
    "TITANIUM_WHITE": {'description': 'Titanium white (Titanium dioxide)', 'meaning': 'CHEBI:51050', 'annotations': {'hex': 'FFFFFF', 'chemical': 'TiO2', 'discovered': '1916'}},
    "ZINC_WHITE": {'description': 'Zinc white (Zinc oxide)', 'meaning': 'CHEBI:36560', 'annotations': {'hex': 'FEFEFE', 'chemical': 'ZnO'}},
    "LEAD_WHITE": {'description': 'Lead white (Basic lead carbonate) - toxic', 'annotations': {'hex': 'F8F8F8', 'chemical': '2PbCO3·Pb(OH)2', 'warning': 'highly toxic, historical use'}},
    "CADMIUM_YELLOW": {'description': 'Cadmium yellow (Cadmium sulfide)', 'meaning': 'CHEBI:50834', 'annotations': {'hex': 'FFF600', 'chemical': 'CdS', 'warning': 'toxic'}},
    "CHROME_YELLOW": {'description': 'Chrome yellow (Lead chromate) - toxic', 'annotations': {'hex': 'FFC200', 'chemical': 'PbCrO4', 'warning': 'highly toxic'}},
    "NAPLES_YELLOW": {'description': 'Naples yellow (Lead antimonate)', 'annotations': {'hex': 'FDD5B1', 'chemical': 'Pb(SbO3)2', 'historical': 'ancient pigment'}},
    "YELLOW_OCHRE": {'description': 'Yellow ochre (Iron oxide hydroxide)', 'annotations': {'hex': 'CC7722', 'chemical': 'FeO(OH)·nH2O', 'natural': 'earth pigment'}},
    "CADMIUM_ORANGE": {'description': 'Cadmium orange (Cadmium selenide)', 'annotations': {'hex': 'FF6600', 'chemical': 'CdS·CdSe', 'warning': 'toxic'}},
    "CADMIUM_RED": {'description': 'Cadmium red (Cadmium selenide)', 'meaning': 'CHEBI:50835', 'annotations': {'hex': 'E30022', 'chemical': 'CdSe', 'warning': 'toxic'}},
    "VERMILION": {'description': 'Vermilion/Cinnabar (Mercury sulfide)', 'annotations': {'hex': 'E34234', 'chemical': 'HgS', 'warning': 'highly toxic'}},
    "ALIZARIN_CRIMSON": {'description': 'Alizarin crimson (synthetic)', 'meaning': 'CHEBI:16866', 'annotations': {'hex': 'E32636', 'chemical': 'C14H8O4', 'organic': 'synthetic organic'}},
    "CARMINE": {'description': 'Carmine (from cochineal insects)', 'annotations': {'hex': '960018', 'source': 'cochineal insects', 'natural': 'organic pigment'}},
    "BURNT_SIENNA": {'description': 'Burnt sienna (heated iron oxide)', 'annotations': {'hex': 'E97451', 'chemical': 'Fe2O3', 'process': 'calcined raw sienna'}},
    "RAW_SIENNA": {'description': 'Raw sienna (Iron oxide with clay)', 'annotations': {'hex': 'C69D52', 'chemical': 'Fe2O3 with clay', 'natural': 'earth pigment'}},
    "BURNT_UMBER": {'description': 'Burnt umber (heated iron/manganese oxide)', 'annotations': {'hex': '8B4513', 'chemical': 'Fe2O3 + MnO2', 'process': 'calcined raw umber'}},
    "RAW_UMBER": {'description': 'Raw umber (Iron/manganese oxide)', 'annotations': {'hex': '734A12', 'chemical': 'Fe2O3 + MnO2', 'natural': 'earth pigment'}},
    "VAN_DYKE_BROWN": {'description': 'Van Dyke brown (organic earth)', 'annotations': {'hex': '664228', 'source': 'peat, lignite', 'warning': 'fugitive color'}},
    "PRUSSIAN_BLUE": {'description': 'Prussian blue (Ferric ferrocyanide)', 'meaning': 'CHEBI:30069', 'annotations': {'hex': '003153', 'chemical': 'Fe4[Fe(CN)6]3', 'discovered': '1706'}},
    "ULTRAMARINE": {'description': 'Ultramarine blue (originally lapis lazuli)', 'annotations': {'hex': '120A8F', 'chemical': 'Na8[Al6Si6O24]Sn', 'historical': 'most expensive pigment'}},
    "COBALT_BLUE": {'description': 'Cobalt blue (Cobalt aluminate)', 'annotations': {'hex': '0047AB', 'chemical': 'CoAl2O4'}},
    "CERULEAN_BLUE": {'description': 'Cerulean blue (Cobalt stannate)', 'annotations': {'hex': '2A52BE', 'chemical': 'Co2SnO4'}},
    "PHTHALO_BLUE": {'description': 'Phthalocyanine blue', 'annotations': {'hex': '000F89', 'chemical': 'C32H16CuN8', 'modern': 'synthetic organic'}},
    "VIRIDIAN": {'description': 'Viridian (Chromium oxide green)', 'annotations': {'hex': '40826D', 'chemical': 'Cr2O3·2H2O'}},
    "CHROME_GREEN": {'description': 'Chrome oxide green', 'annotations': {'hex': '2E5E26', 'chemical': 'Cr2O3'}},
    "PHTHALO_GREEN": {'description': 'Phthalocyanine green', 'annotations': {'hex': '123524', 'chemical': 'C32H16ClCuN8', 'modern': 'synthetic organic'}},
    "TERRE_VERTE": {'description': 'Terre verte/Green earth', 'annotations': {'hex': '6B7F59', 'chemical': 'complex silicate', 'natural': 'earth pigment'}},
    "TYRIAN_PURPLE": {'description': 'Tyrian purple (from murex snails)', 'annotations': {'hex': '66023C', 'source': 'murex snails', 'historical': 'ancient royal purple'}},
    "MANGANESE_VIOLET": {'description': 'Manganese violet', 'annotations': {'hex': '8B3E5F', 'chemical': 'NH4MnP2O7'}},
    "MARS_BLACK": {'description': 'Mars black (Synthetic iron oxide)', 'annotations': {'hex': '010101', 'chemical': 'Fe3O4', 'synthetic': 'iron oxide'}},
    "IVORY_BLACK": {'description': 'Ivory black (Bone char)', 'annotations': {'hex': '1B1B1B', 'source': 'charred bones'}},
    "LAMP_BLACK": {'description': 'Lamp black (Carbon black)', 'annotations': {'hex': '2B2B2B', 'chemical': 'C', 'source': 'soot'}},
}

class IndustrialDyeEnum(RichEnum):
    """
    Industrial and textile dyes
    """
    # Enum members
    INDIGO = "INDIGO"
    ANILINE_BLACK = "ANILINE_BLACK"
    METHYLENE_BLUE = "METHYLENE_BLUE"
    CONGO_RED = "CONGO_RED"
    MALACHITE_GREEN = "MALACHITE_GREEN"
    CRYSTAL_VIOLET = "CRYSTAL_VIOLET"
    EOSIN = "EOSIN"
    SAFRANIN = "SAFRANIN"
    ACID_ORANGE_7 = "ACID_ORANGE_7"
    REACTIVE_BLACK_5 = "REACTIVE_BLACK_5"
    DISPERSE_BLUE_1 = "DISPERSE_BLUE_1"
    VAT_BLUE_1 = "VAT_BLUE_1"

# Set metadata after class creation to avoid it becoming an enum member
IndustrialDyeEnum._metadata = {
    "INDIGO": {'description': 'Indigo dye', 'annotations': {'hex': '4B0082', 'source': 'originally plant-based, now synthetic', 'use': 'denim, textiles'}},
    "ANILINE_BLACK": {'description': 'Aniline black', 'annotations': {'hex': '000000', 'chemical': 'polyaniline', 'use': 'cotton dyeing'}},
    "METHYLENE_BLUE": {'description': 'Methylene blue', 'annotations': {'hex': '1E90FF', 'chemical': 'C16H18ClN3S', 'use': 'biological stain, medical'}},
    "CONGO_RED": {'description': 'Congo red', 'meaning': 'CHEBI:34653', 'annotations': {'hex': 'CC0000', 'chemical': 'C32H22N6Na2O6S2', 'use': 'pH indicator, textile'}},
    "MALACHITE_GREEN": {'description': 'Malachite green', 'meaning': 'CHEBI:72449', 'annotations': {'hex': '0BDA51', 'chemical': 'C23H25ClN2', 'use': 'biological stain'}},
    "CRYSTAL_VIOLET": {'description': 'Crystal violet/Gentian violet', 'meaning': 'CHEBI:41688', 'annotations': {'hex': '9400D3', 'chemical': 'C25H30ClN3', 'use': 'gram staining'}},
    "EOSIN": {'description': 'Eosin Y', 'meaning': 'CHEBI:52053', 'annotations': {'hex': 'FF6B6B', 'chemical': 'C20H6Br4Na2O5', 'use': 'histology stain'}, 'aliases': ['eosin YS dye']},
    "SAFRANIN": {'description': 'Safranin O', 'annotations': {'hex': 'FF0066', 'chemical': 'C20H19ClN4', 'use': 'biological stain'}},
    "ACID_ORANGE_7": {'description': 'Acid Orange 7 (Orange II)', 'annotations': {'hex': 'FF7F00', 'chemical': 'C16H11N2NaO4S', 'use': 'wool, silk dyeing'}},
    "REACTIVE_BLACK_5": {'description': 'Reactive Black 5', 'annotations': {'hex': '000000', 'use': 'cotton reactive dye'}},
    "DISPERSE_BLUE_1": {'description': 'Disperse Blue 1', 'annotations': {'hex': '1560BD', 'use': 'polyester dyeing'}},
    "VAT_BLUE_1": {'description': 'Vat Blue 1 (Indanthrene blue)', 'annotations': {'hex': '002F5C', 'use': 'cotton vat dyeing'}},
}

class FoodColoringEnum(RichEnum):
    """
    Food coloring and natural food dyes
    """
    # Enum members
    FD_C_RED_40 = "FD_C_RED_40"
    FD_C_YELLOW_5 = "FD_C_YELLOW_5"
    FD_C_YELLOW_6 = "FD_C_YELLOW_6"
    FD_C_BLUE_1 = "FD_C_BLUE_1"
    FD_C_BLUE_2 = "FD_C_BLUE_2"
    FD_C_GREEN_3 = "FD_C_GREEN_3"
    CARAMEL_COLOR = "CARAMEL_COLOR"
    ANNATTO = "ANNATTO"
    TURMERIC = "TURMERIC"
    BEETROOT_RED = "BEETROOT_RED"
    CHLOROPHYLL = "CHLOROPHYLL"
    ANTHOCYANINS = "ANTHOCYANINS"
    PAPRIKA_EXTRACT = "PAPRIKA_EXTRACT"
    SPIRULINA_BLUE = "SPIRULINA_BLUE"

# Set metadata after class creation to avoid it becoming an enum member
FoodColoringEnum._metadata = {
    "FD_C_RED_40": {'description': 'FD&C Red No. 40 (Allura Red)', 'annotations': {'hex': 'E40000', 'E_number': 'E129', 'use': 'beverages, candies'}},
    "FD_C_YELLOW_5": {'description': 'FD&C Yellow No. 5 (Tartrazine)', 'annotations': {'hex': 'FFFF00', 'E_number': 'E102', 'use': 'beverages, desserts'}},
    "FD_C_YELLOW_6": {'description': 'FD&C Yellow No. 6 (Sunset Yellow)', 'annotations': {'hex': 'FFA500', 'E_number': 'E110', 'use': 'snacks, beverages'}},
    "FD_C_BLUE_1": {'description': 'FD&C Blue No. 1 (Brilliant Blue)', 'meaning': 'CHEBI:82411', 'annotations': {'hex': '0033FF', 'E_number': 'E133', 'use': 'beverages, candies'}},
    "FD_C_BLUE_2": {'description': 'FD&C Blue No. 2 (Indigo Carmine)', 'annotations': {'hex': '4B0082', 'E_number': 'E132', 'use': 'beverages, confections'}},
    "FD_C_GREEN_3": {'description': 'FD&C Green No. 3 (Fast Green)', 'annotations': {'hex': '00FF00', 'E_number': 'E143', 'use': 'beverages, desserts'}},
    "CARAMEL_COLOR": {'description': 'Caramel coloring', 'annotations': {'hex': '8B4513', 'E_number': 'E150', 'use': 'cola, sauces'}},
    "ANNATTO": {'description': 'Annatto (natural orange)', 'meaning': 'CHEBI:3136', 'annotations': {'hex': 'FF6600', 'E_number': 'E160b', 'source': 'achiote seeds'}, 'aliases': ['bixin']},
    "TURMERIC": {'description': 'Turmeric/Curcumin (natural yellow)', 'meaning': 'CHEBI:3962', 'annotations': {'hex': 'F0E442', 'E_number': 'E100', 'source': 'turmeric root'}},
    "BEETROOT_RED": {'description': 'Beetroot red/Betanin', 'meaning': 'CHEBI:3080', 'annotations': {'hex': 'BC2A4D', 'E_number': 'E162', 'source': 'beets'}, 'aliases': ['Betanin']},
    "CHLOROPHYLL": {'description': 'Chlorophyll (natural green)', 'meaning': 'CHEBI:28966', 'annotations': {'hex': '4D7C0F', 'E_number': 'E140', 'source': 'plants'}},
    "ANTHOCYANINS": {'description': 'Anthocyanins (natural purple/red)', 'annotations': {'hex': '6B3AA0', 'E_number': 'E163', 'source': 'berries, grapes'}},
    "PAPRIKA_EXTRACT": {'description': 'Paprika extract', 'annotations': {'hex': 'E85D00', 'E_number': 'E160c', 'source': 'paprika peppers'}},
    "SPIRULINA_BLUE": {'description': 'Spirulina extract (phycocyanin)', 'annotations': {'hex': '1E88E5', 'source': 'spirulina algae', 'natural': 'true'}},
}

class AutomobilePaintColorEnum(RichEnum):
    """
    Common automobile paint colors
    """
    # Enum members
    ARCTIC_WHITE = "ARCTIC_WHITE"
    MIDNIGHT_BLACK = "MIDNIGHT_BLACK"
    SILVER_METALLIC = "SILVER_METALLIC"
    GUNMETAL_GRAY = "GUNMETAL_GRAY"
    RACING_RED = "RACING_RED"
    CANDY_APPLE_RED = "CANDY_APPLE_RED"
    ELECTRIC_BLUE = "ELECTRIC_BLUE"
    BRITISH_RACING_GREEN = "BRITISH_RACING_GREEN"
    PEARL_WHITE = "PEARL_WHITE"
    CHAMPAGNE_GOLD = "CHAMPAGNE_GOLD"
    COPPER_BRONZE = "COPPER_BRONZE"
    MIAMI_BLUE = "MIAMI_BLUE"

# Set metadata after class creation to avoid it becoming an enum member
AutomobilePaintColorEnum._metadata = {
    "ARCTIC_WHITE": {'description': 'Arctic White', 'meaning': 'HEX:FFFFFF', 'annotations': {'type': 'solid'}},
    "MIDNIGHT_BLACK": {'description': 'Midnight Black', 'meaning': 'HEX:000000', 'annotations': {'type': 'metallic'}},
    "SILVER_METALLIC": {'description': 'Silver Metallic', 'meaning': 'HEX:C0C0C0', 'annotations': {'type': 'metallic'}},
    "GUNMETAL_GRAY": {'description': 'Gunmetal Gray', 'meaning': 'HEX:2A3439', 'annotations': {'type': 'metallic'}},
    "RACING_RED": {'description': 'Racing Red', 'meaning': 'HEX:CE1620', 'annotations': {'type': 'solid'}},
    "CANDY_APPLE_RED": {'description': 'Candy Apple Red', 'meaning': 'HEX:FF0800', 'annotations': {'type': 'metallic'}},
    "ELECTRIC_BLUE": {'description': 'Electric Blue', 'meaning': 'HEX:7DF9FF', 'annotations': {'type': 'metallic'}},
    "BRITISH_RACING_GREEN": {'description': 'British Racing Green', 'meaning': 'HEX:004225', 'annotations': {'type': 'solid', 'historical': 'British racing color'}},
    "PEARL_WHITE": {'description': 'Pearl White', 'meaning': 'HEX:F8F8FF', 'annotations': {'type': 'pearl', 'finish': 'pearlescent'}},
    "CHAMPAGNE_GOLD": {'description': 'Champagne Gold', 'meaning': 'HEX:D4AF37', 'annotations': {'type': 'metallic'}},
    "COPPER_BRONZE": {'description': 'Copper Bronze', 'meaning': 'HEX:B87333', 'annotations': {'type': 'metallic'}},
    "MIAMI_BLUE": {'description': 'Miami Blue', 'meaning': 'HEX:00BFFF', 'annotations': {'type': 'metallic', 'brand': 'Porsche'}},
}

class BasicColorEnum(RichEnum):
    """
    Basic color names commonly used in everyday language
    """
    # Enum members
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    PURPLE = "PURPLE"
    BLACK = "BLACK"
    WHITE = "WHITE"
    GRAY = "GRAY"
    BROWN = "BROWN"
    PINK = "PINK"
    CYAN = "CYAN"
    MAGENTA = "MAGENTA"

# Set metadata after class creation to avoid it becoming an enum member
BasicColorEnum._metadata = {
    "RED": {'description': 'Primary red color', 'meaning': 'HEX:FF0000', 'annotations': {'wavelength': '700 nm', 'rgb': '255,0,0'}},
    "GREEN": {'description': 'Primary green color', 'meaning': 'HEX:008000', 'annotations': {'wavelength': '550 nm', 'rgb': '0,128,0'}},
    "BLUE": {'description': 'Primary blue color', 'meaning': 'HEX:0000FF', 'annotations': {'wavelength': '450 nm', 'rgb': '0,0,255'}},
    "YELLOW": {'description': 'Secondary yellow color', 'meaning': 'HEX:FFFF00', 'annotations': {'wavelength': '580 nm', 'rgb': '255,255,0'}},
    "ORANGE": {'description': 'Secondary orange color', 'meaning': 'HEX:FFA500', 'annotations': {'wavelength': '600 nm', 'rgb': '255,165,0'}},
    "PURPLE": {'description': 'Secondary purple color', 'meaning': 'HEX:800080', 'annotations': {'wavelength': '420 nm', 'rgb': '128,0,128'}},
    "BLACK": {'description': 'Absence of color', 'meaning': 'HEX:000000', 'annotations': {'rgb': '0,0,0'}},
    "WHITE": {'description': 'All colors combined', 'meaning': 'HEX:FFFFFF', 'annotations': {'rgb': '255,255,255'}},
    "GRAY": {'description': 'Neutral gray', 'meaning': 'HEX:808080', 'annotations': {'rgb': '128,128,128', 'aliases': 'grey'}},
    "BROWN": {'description': 'Brown color', 'meaning': 'HEX:A52A2A', 'annotations': {'rgb': '165,42,42'}},
    "PINK": {'description': 'Light red/pink color', 'meaning': 'HEX:FFC0CB', 'annotations': {'rgb': '255,192,203'}},
    "CYAN": {'description': 'Cyan/aqua color', 'meaning': 'HEX:00FFFF', 'annotations': {'wavelength': '490 nm', 'rgb': '0,255,255'}},
    "MAGENTA": {'description': 'Magenta color', 'meaning': 'HEX:FF00FF', 'annotations': {'rgb': '255,0,255'}},
}

class WebColorEnum(RichEnum):
    """
    Standard HTML/CSS named colors (147 colors)
    """
    # Enum members
    INDIAN_RED = "INDIAN_RED"
    LIGHT_CORAL = "LIGHT_CORAL"
    SALMON = "SALMON"
    DARK_SALMON = "DARK_SALMON"
    CRIMSON = "CRIMSON"
    FIREBRICK = "FIREBRICK"
    DARK_RED = "DARK_RED"
    HOT_PINK = "HOT_PINK"
    DEEP_PINK = "DEEP_PINK"
    LIGHT_PINK = "LIGHT_PINK"
    PALE_VIOLET_RED = "PALE_VIOLET_RED"
    CORAL = "CORAL"
    TOMATO = "TOMATO"
    ORANGE_RED = "ORANGE_RED"
    DARK_ORANGE = "DARK_ORANGE"
    GOLD = "GOLD"
    LIGHT_YELLOW = "LIGHT_YELLOW"
    LEMON_CHIFFON = "LEMON_CHIFFON"
    PAPAYA_WHIP = "PAPAYA_WHIP"
    MOCCASIN = "MOCCASIN"
    PEACH_PUFF = "PEACH_PUFF"
    KHAKI = "KHAKI"
    LAVENDER = "LAVENDER"
    THISTLE = "THISTLE"
    PLUM = "PLUM"
    VIOLET = "VIOLET"
    ORCHID = "ORCHID"
    FUCHSIA = "FUCHSIA"
    MEDIUM_ORCHID = "MEDIUM_ORCHID"
    MEDIUM_PURPLE = "MEDIUM_PURPLE"
    BLUE_VIOLET = "BLUE_VIOLET"
    DARK_VIOLET = "DARK_VIOLET"
    DARK_ORCHID = "DARK_ORCHID"
    DARK_MAGENTA = "DARK_MAGENTA"
    INDIGO = "INDIGO"
    GREEN_YELLOW = "GREEN_YELLOW"
    CHARTREUSE = "CHARTREUSE"
    LAWN_GREEN = "LAWN_GREEN"
    LIME = "LIME"
    LIME_GREEN = "LIME_GREEN"
    PALE_GREEN = "PALE_GREEN"
    LIGHT_GREEN = "LIGHT_GREEN"
    MEDIUM_SPRING_GREEN = "MEDIUM_SPRING_GREEN"
    SPRING_GREEN = "SPRING_GREEN"
    MEDIUM_SEA_GREEN = "MEDIUM_SEA_GREEN"
    SEA_GREEN = "SEA_GREEN"
    FOREST_GREEN = "FOREST_GREEN"
    DARK_GREEN = "DARK_GREEN"
    YELLOW_GREEN = "YELLOW_GREEN"
    OLIVE_DRAB = "OLIVE_DRAB"
    OLIVE = "OLIVE"
    DARK_OLIVE_GREEN = "DARK_OLIVE_GREEN"
    AQUA = "AQUA"
    CYAN = "CYAN"
    LIGHT_CYAN = "LIGHT_CYAN"
    PALE_TURQUOISE = "PALE_TURQUOISE"
    AQUAMARINE = "AQUAMARINE"
    TURQUOISE = "TURQUOISE"
    MEDIUM_TURQUOISE = "MEDIUM_TURQUOISE"
    DARK_TURQUOISE = "DARK_TURQUOISE"
    LIGHT_SEA_GREEN = "LIGHT_SEA_GREEN"
    CADET_BLUE = "CADET_BLUE"
    DARK_CYAN = "DARK_CYAN"
    TEAL = "TEAL"
    LIGHT_STEEL_BLUE = "LIGHT_STEEL_BLUE"
    POWDER_BLUE = "POWDER_BLUE"
    LIGHT_BLUE = "LIGHT_BLUE"
    SKY_BLUE = "SKY_BLUE"
    LIGHT_SKY_BLUE = "LIGHT_SKY_BLUE"
    DEEP_SKY_BLUE = "DEEP_SKY_BLUE"
    DODGER_BLUE = "DODGER_BLUE"
    CORNFLOWER_BLUE = "CORNFLOWER_BLUE"
    STEEL_BLUE = "STEEL_BLUE"
    ROYAL_BLUE = "ROYAL_BLUE"
    MEDIUM_BLUE = "MEDIUM_BLUE"
    DARK_BLUE = "DARK_BLUE"
    NAVY = "NAVY"
    MIDNIGHT_BLUE = "MIDNIGHT_BLUE"
    CORNSILK = "CORNSILK"
    BLANCHED_ALMOND = "BLANCHED_ALMOND"
    BISQUE = "BISQUE"
    NAVAJO_WHITE = "NAVAJO_WHITE"
    WHEAT = "WHEAT"
    BURLYWOOD = "BURLYWOOD"
    TAN = "TAN"
    ROSY_BROWN = "ROSY_BROWN"
    SANDY_BROWN = "SANDY_BROWN"
    GOLDENROD = "GOLDENROD"
    DARK_GOLDENROD = "DARK_GOLDENROD"
    PERU = "PERU"
    CHOCOLATE = "CHOCOLATE"
    SADDLE_BROWN = "SADDLE_BROWN"
    SIENNA = "SIENNA"
    MAROON = "MAROON"
    SNOW = "SNOW"
    HONEYDEW = "HONEYDEW"
    MINT_CREAM = "MINT_CREAM"
    AZURE = "AZURE"
    ALICE_BLUE = "ALICE_BLUE"
    GHOST_WHITE = "GHOST_WHITE"
    WHITE_SMOKE = "WHITE_SMOKE"
    SEASHELL = "SEASHELL"
    BEIGE = "BEIGE"
    OLD_LACE = "OLD_LACE"
    FLORAL_WHITE = "FLORAL_WHITE"
    IVORY = "IVORY"
    ANTIQUE_WHITE = "ANTIQUE_WHITE"
    LINEN = "LINEN"
    LAVENDER_BLUSH = "LAVENDER_BLUSH"
    MISTY_ROSE = "MISTY_ROSE"
    GAINSBORO = "GAINSBORO"
    LIGHT_GRAY = "LIGHT_GRAY"
    SILVER = "SILVER"
    DARK_GRAY = "DARK_GRAY"
    DIM_GRAY = "DIM_GRAY"
    LIGHT_SLATE_GRAY = "LIGHT_SLATE_GRAY"
    SLATE_GRAY = "SLATE_GRAY"
    DARK_SLATE_GRAY = "DARK_SLATE_GRAY"

# Set metadata after class creation to avoid it becoming an enum member
WebColorEnum._metadata = {
    "INDIAN_RED": {'description': 'Indian red', 'meaning': 'HEX:CD5C5C', 'annotations': {'rgb': '205,92,92'}},
    "LIGHT_CORAL": {'description': 'Light coral', 'meaning': 'HEX:F08080', 'annotations': {'rgb': '240,128,128'}},
    "SALMON": {'description': 'Salmon', 'meaning': 'HEX:FA8072', 'annotations': {'rgb': '250,128,114'}},
    "DARK_SALMON": {'description': 'Dark salmon', 'meaning': 'HEX:E9967A', 'annotations': {'rgb': '233,150,122'}},
    "CRIMSON": {'description': 'Crimson', 'meaning': 'HEX:DC143C', 'annotations': {'rgb': '220,20,60'}},
    "FIREBRICK": {'description': 'Firebrick', 'meaning': 'HEX:B22222', 'annotations': {'rgb': '178,34,34'}},
    "DARK_RED": {'description': 'Dark red', 'meaning': 'HEX:8B0000', 'annotations': {'rgb': '139,0,0'}},
    "HOT_PINK": {'description': 'Hot pink', 'meaning': 'HEX:FF69B4', 'annotations': {'rgb': '255,105,180'}},
    "DEEP_PINK": {'description': 'Deep pink', 'meaning': 'HEX:FF1493', 'annotations': {'rgb': '255,20,147'}},
    "LIGHT_PINK": {'description': 'Light pink', 'meaning': 'HEX:FFB6C1', 'annotations': {'rgb': '255,182,193'}},
    "PALE_VIOLET_RED": {'description': 'Pale violet red', 'meaning': 'HEX:DB7093', 'annotations': {'rgb': '219,112,147'}},
    "CORAL": {'description': 'Coral', 'meaning': 'HEX:FF7F50', 'annotations': {'rgb': '255,127,80'}},
    "TOMATO": {'description': 'Tomato', 'meaning': 'HEX:FF6347', 'annotations': {'rgb': '255,99,71'}},
    "ORANGE_RED": {'description': 'Orange red', 'meaning': 'HEX:FF4500', 'annotations': {'rgb': '255,69,0'}},
    "DARK_ORANGE": {'description': 'Dark orange', 'meaning': 'HEX:FF8C00', 'annotations': {'rgb': '255,140,0'}},
    "GOLD": {'description': 'Gold', 'meaning': 'HEX:FFD700', 'annotations': {'rgb': '255,215,0'}},
    "LIGHT_YELLOW": {'description': 'Light yellow', 'meaning': 'HEX:FFFFE0', 'annotations': {'rgb': '255,255,224'}},
    "LEMON_CHIFFON": {'description': 'Lemon chiffon', 'meaning': 'HEX:FFFACD', 'annotations': {'rgb': '255,250,205'}},
    "PAPAYA_WHIP": {'description': 'Papaya whip', 'meaning': 'HEX:FFEFD5', 'annotations': {'rgb': '255,239,213'}},
    "MOCCASIN": {'description': 'Moccasin', 'meaning': 'HEX:FFE4B5', 'annotations': {'rgb': '255,228,181'}},
    "PEACH_PUFF": {'description': 'Peach puff', 'meaning': 'HEX:FFDAB9', 'annotations': {'rgb': '255,218,185'}},
    "KHAKI": {'description': 'Khaki', 'meaning': 'HEX:F0E68C', 'annotations': {'rgb': '240,230,140'}},
    "LAVENDER": {'description': 'Lavender', 'meaning': 'HEX:E6E6FA', 'annotations': {'rgb': '230,230,250'}},
    "THISTLE": {'description': 'Thistle', 'meaning': 'HEX:D8BFD8', 'annotations': {'rgb': '216,191,216'}},
    "PLUM": {'description': 'Plum', 'meaning': 'HEX:DDA0DD', 'annotations': {'rgb': '221,160,221'}},
    "VIOLET": {'description': 'Violet', 'meaning': 'HEX:EE82EE', 'annotations': {'rgb': '238,130,238'}},
    "ORCHID": {'description': 'Orchid', 'meaning': 'HEX:DA70D6', 'annotations': {'rgb': '218,112,214'}},
    "FUCHSIA": {'description': 'Fuchsia', 'meaning': 'HEX:FF00FF', 'annotations': {'rgb': '255,0,255'}},
    "MEDIUM_ORCHID": {'description': 'Medium orchid', 'meaning': 'HEX:BA55D3', 'annotations': {'rgb': '186,85,211'}},
    "MEDIUM_PURPLE": {'description': 'Medium purple', 'meaning': 'HEX:9370DB', 'annotations': {'rgb': '147,112,219'}},
    "BLUE_VIOLET": {'description': 'Blue violet', 'meaning': 'HEX:8A2BE2', 'annotations': {'rgb': '138,43,226'}},
    "DARK_VIOLET": {'description': 'Dark violet', 'meaning': 'HEX:9400D3', 'annotations': {'rgb': '148,0,211'}},
    "DARK_ORCHID": {'description': 'Dark orchid', 'meaning': 'HEX:9932CC', 'annotations': {'rgb': '153,50,204'}},
    "DARK_MAGENTA": {'description': 'Dark magenta', 'meaning': 'HEX:8B008B', 'annotations': {'rgb': '139,0,139'}},
    "INDIGO": {'description': 'Indigo', 'meaning': 'HEX:4B0082', 'annotations': {'rgb': '75,0,130'}},
    "GREEN_YELLOW": {'description': 'Green yellow', 'meaning': 'HEX:ADFF2F', 'annotations': {'rgb': '173,255,47'}},
    "CHARTREUSE": {'description': 'Chartreuse', 'meaning': 'HEX:7FFF00', 'annotations': {'rgb': '127,255,0'}},
    "LAWN_GREEN": {'description': 'Lawn green', 'meaning': 'HEX:7CFC00', 'annotations': {'rgb': '124,252,0'}},
    "LIME": {'description': 'Lime', 'meaning': 'HEX:00FF00', 'annotations': {'rgb': '0,255,0'}},
    "LIME_GREEN": {'description': 'Lime green', 'meaning': 'HEX:32CD32', 'annotations': {'rgb': '50,205,50'}},
    "PALE_GREEN": {'description': 'Pale green', 'meaning': 'HEX:98FB98', 'annotations': {'rgb': '152,251,152'}},
    "LIGHT_GREEN": {'description': 'Light green', 'meaning': 'HEX:90EE90', 'annotations': {'rgb': '144,238,144'}},
    "MEDIUM_SPRING_GREEN": {'description': 'Medium spring green', 'meaning': 'HEX:00FA9A', 'annotations': {'rgb': '0,250,154'}},
    "SPRING_GREEN": {'description': 'Spring green', 'meaning': 'HEX:00FF7F', 'annotations': {'rgb': '0,255,127'}},
    "MEDIUM_SEA_GREEN": {'description': 'Medium sea green', 'meaning': 'HEX:3CB371', 'annotations': {'rgb': '60,179,113'}},
    "SEA_GREEN": {'description': 'Sea green', 'meaning': 'HEX:2E8B57', 'annotations': {'rgb': '46,139,87'}},
    "FOREST_GREEN": {'description': 'Forest green', 'meaning': 'HEX:228B22', 'annotations': {'rgb': '34,139,34'}},
    "DARK_GREEN": {'description': 'Dark green', 'meaning': 'HEX:006400', 'annotations': {'rgb': '0,100,0'}},
    "YELLOW_GREEN": {'description': 'Yellow green', 'meaning': 'HEX:9ACD32', 'annotations': {'rgb': '154,205,50'}},
    "OLIVE_DRAB": {'description': 'Olive drab', 'meaning': 'HEX:6B8E23', 'annotations': {'rgb': '107,142,35'}},
    "OLIVE": {'description': 'Olive', 'meaning': 'HEX:808000', 'annotations': {'rgb': '128,128,0'}},
    "DARK_OLIVE_GREEN": {'description': 'Dark olive green', 'meaning': 'HEX:556B2F', 'annotations': {'rgb': '85,107,47'}},
    "AQUA": {'description': 'Aqua', 'meaning': 'HEX:00FFFF', 'annotations': {'rgb': '0,255,255'}},
    "CYAN": {'description': 'Cyan', 'meaning': 'HEX:00FFFF', 'annotations': {'rgb': '0,255,255'}},
    "LIGHT_CYAN": {'description': 'Light cyan', 'meaning': 'HEX:E0FFFF', 'annotations': {'rgb': '224,255,255'}},
    "PALE_TURQUOISE": {'description': 'Pale turquoise', 'meaning': 'HEX:AFEEEE', 'annotations': {'rgb': '175,238,238'}},
    "AQUAMARINE": {'description': 'Aquamarine', 'meaning': 'HEX:7FFFD4', 'annotations': {'rgb': '127,255,212'}},
    "TURQUOISE": {'description': 'Turquoise', 'meaning': 'HEX:40E0D0', 'annotations': {'rgb': '64,224,208'}},
    "MEDIUM_TURQUOISE": {'description': 'Medium turquoise', 'meaning': 'HEX:48D1CC', 'annotations': {'rgb': '72,209,204'}},
    "DARK_TURQUOISE": {'description': 'Dark turquoise', 'meaning': 'HEX:00CED1', 'annotations': {'rgb': '0,206,209'}},
    "LIGHT_SEA_GREEN": {'description': 'Light sea green', 'meaning': 'HEX:20B2AA', 'annotations': {'rgb': '32,178,170'}},
    "CADET_BLUE": {'description': 'Cadet blue', 'meaning': 'HEX:5F9EA0', 'annotations': {'rgb': '95,158,160'}},
    "DARK_CYAN": {'description': 'Dark cyan', 'meaning': 'HEX:008B8B', 'annotations': {'rgb': '0,139,139'}},
    "TEAL": {'description': 'Teal', 'meaning': 'HEX:008080', 'annotations': {'rgb': '0,128,128'}},
    "LIGHT_STEEL_BLUE": {'description': 'Light steel blue', 'meaning': 'HEX:B0C4DE', 'annotations': {'rgb': '176,196,222'}},
    "POWDER_BLUE": {'description': 'Powder blue', 'meaning': 'HEX:B0E0E6', 'annotations': {'rgb': '176,224,230'}},
    "LIGHT_BLUE": {'description': 'Light blue', 'meaning': 'HEX:ADD8E6', 'annotations': {'rgb': '173,216,230'}},
    "SKY_BLUE": {'description': 'Sky blue', 'meaning': 'HEX:87CEEB', 'annotations': {'rgb': '135,206,235'}},
    "LIGHT_SKY_BLUE": {'description': 'Light sky blue', 'meaning': 'HEX:87CEFA', 'annotations': {'rgb': '135,206,250'}},
    "DEEP_SKY_BLUE": {'description': 'Deep sky blue', 'meaning': 'HEX:00BFFF', 'annotations': {'rgb': '0,191,255'}},
    "DODGER_BLUE": {'description': 'Dodger blue', 'meaning': 'HEX:1E90FF', 'annotations': {'rgb': '30,144,255'}},
    "CORNFLOWER_BLUE": {'description': 'Cornflower blue', 'meaning': 'HEX:6495ED', 'annotations': {'rgb': '100,149,237'}},
    "STEEL_BLUE": {'description': 'Steel blue', 'meaning': 'HEX:4682B4', 'annotations': {'rgb': '70,130,180'}},
    "ROYAL_BLUE": {'description': 'Royal blue', 'meaning': 'HEX:4169E1', 'annotations': {'rgb': '65,105,225'}},
    "MEDIUM_BLUE": {'description': 'Medium blue', 'meaning': 'HEX:0000CD', 'annotations': {'rgb': '0,0,205'}},
    "DARK_BLUE": {'description': 'Dark blue', 'meaning': 'HEX:00008B', 'annotations': {'rgb': '0,0,139'}},
    "NAVY": {'description': 'Navy', 'meaning': 'HEX:000080', 'annotations': {'rgb': '0,0,128'}},
    "MIDNIGHT_BLUE": {'description': 'Midnight blue', 'meaning': 'HEX:191970', 'annotations': {'rgb': '25,25,112'}},
    "CORNSILK": {'description': 'Cornsilk', 'meaning': 'HEX:FFF8DC', 'annotations': {'rgb': '255,248,220'}},
    "BLANCHED_ALMOND": {'description': 'Blanched almond', 'meaning': 'HEX:FFEBCD', 'annotations': {'rgb': '255,235,205'}},
    "BISQUE": {'description': 'Bisque', 'meaning': 'HEX:FFE4C4', 'annotations': {'rgb': '255,228,196'}},
    "NAVAJO_WHITE": {'description': 'Navajo white', 'meaning': 'HEX:FFDEAD', 'annotations': {'rgb': '255,222,173'}},
    "WHEAT": {'description': 'Wheat', 'meaning': 'HEX:F5DEB3', 'annotations': {'rgb': '245,222,179'}},
    "BURLYWOOD": {'description': 'Burlywood', 'meaning': 'HEX:DEB887', 'annotations': {'rgb': '222,184,135'}},
    "TAN": {'description': 'Tan', 'meaning': 'HEX:D2B48C', 'annotations': {'rgb': '210,180,140'}},
    "ROSY_BROWN": {'description': 'Rosy brown', 'meaning': 'HEX:BC8F8F', 'annotations': {'rgb': '188,143,143'}},
    "SANDY_BROWN": {'description': 'Sandy brown', 'meaning': 'HEX:F4A460', 'annotations': {'rgb': '244,164,96'}},
    "GOLDENROD": {'description': 'Goldenrod', 'meaning': 'HEX:DAA520', 'annotations': {'rgb': '218,165,32'}},
    "DARK_GOLDENROD": {'description': 'Dark goldenrod', 'meaning': 'HEX:B8860B', 'annotations': {'rgb': '184,134,11'}},
    "PERU": {'description': 'Peru', 'meaning': 'HEX:CD853F', 'annotations': {'rgb': '205,133,63'}},
    "CHOCOLATE": {'description': 'Chocolate', 'meaning': 'HEX:D2691E', 'annotations': {'rgb': '210,105,30'}},
    "SADDLE_BROWN": {'description': 'Saddle brown', 'meaning': 'HEX:8B4513', 'annotations': {'rgb': '139,69,19'}},
    "SIENNA": {'description': 'Sienna', 'meaning': 'HEX:A0522D', 'annotations': {'rgb': '160,82,45'}},
    "MAROON": {'description': 'Maroon', 'meaning': 'HEX:800000', 'annotations': {'rgb': '128,0,0'}},
    "SNOW": {'description': 'Snow', 'meaning': 'HEX:FFFAFA', 'annotations': {'rgb': '255,250,250'}},
    "HONEYDEW": {'description': 'Honeydew', 'meaning': 'HEX:F0FFF0', 'annotations': {'rgb': '240,255,240'}},
    "MINT_CREAM": {'description': 'Mint cream', 'meaning': 'HEX:F5FFFA', 'annotations': {'rgb': '245,255,250'}},
    "AZURE": {'description': 'Azure', 'meaning': 'HEX:F0FFFF', 'annotations': {'rgb': '240,255,255'}},
    "ALICE_BLUE": {'description': 'Alice blue', 'meaning': 'HEX:F0F8FF', 'annotations': {'rgb': '240,248,255'}},
    "GHOST_WHITE": {'description': 'Ghost white', 'meaning': 'HEX:F8F8FF', 'annotations': {'rgb': '248,248,255'}},
    "WHITE_SMOKE": {'description': 'White smoke', 'meaning': 'HEX:F5F5F5', 'annotations': {'rgb': '245,245,245'}},
    "SEASHELL": {'description': 'Seashell', 'meaning': 'HEX:FFF5EE', 'annotations': {'rgb': '255,245,238'}},
    "BEIGE": {'description': 'Beige', 'meaning': 'HEX:F5F5DC', 'annotations': {'rgb': '245,245,220'}},
    "OLD_LACE": {'description': 'Old lace', 'meaning': 'HEX:FDF5E6', 'annotations': {'rgb': '253,245,230'}},
    "FLORAL_WHITE": {'description': 'Floral white', 'meaning': 'HEX:FFFAF0', 'annotations': {'rgb': '255,250,240'}},
    "IVORY": {'description': 'Ivory', 'meaning': 'HEX:FFFFF0', 'annotations': {'rgb': '255,255,240'}},
    "ANTIQUE_WHITE": {'description': 'Antique white', 'meaning': 'HEX:FAEBD7', 'annotations': {'rgb': '250,235,215'}},
    "LINEN": {'description': 'Linen', 'meaning': 'HEX:FAF0E6', 'annotations': {'rgb': '250,240,230'}},
    "LAVENDER_BLUSH": {'description': 'Lavender blush', 'meaning': 'HEX:FFF0F5', 'annotations': {'rgb': '255,240,245'}},
    "MISTY_ROSE": {'description': 'Misty rose', 'meaning': 'HEX:FFE4E1', 'annotations': {'rgb': '255,228,225'}},
    "GAINSBORO": {'description': 'Gainsboro', 'meaning': 'HEX:DCDCDC', 'annotations': {'rgb': '220,220,220'}},
    "LIGHT_GRAY": {'description': 'Light gray', 'meaning': 'HEX:D3D3D3', 'annotations': {'rgb': '211,211,211'}},
    "SILVER": {'description': 'Silver', 'meaning': 'HEX:C0C0C0', 'annotations': {'rgb': '192,192,192'}},
    "DARK_GRAY": {'description': 'Dark gray', 'meaning': 'HEX:A9A9A9', 'annotations': {'rgb': '169,169,169'}},
    "DIM_GRAY": {'description': 'Dim gray', 'meaning': 'HEX:696969', 'annotations': {'rgb': '105,105,105'}},
    "LIGHT_SLATE_GRAY": {'description': 'Light slate gray', 'meaning': 'HEX:778899', 'annotations': {'rgb': '119,136,153'}},
    "SLATE_GRAY": {'description': 'Slate gray', 'meaning': 'HEX:708090', 'annotations': {'rgb': '112,128,144'}},
    "DARK_SLATE_GRAY": {'description': 'Dark slate gray', 'meaning': 'HEX:2F4F4F', 'annotations': {'rgb': '47,79,79'}},
}

class X11ColorEnum(RichEnum):
    """
    X11/Unix system colors (extended set)
    """
    # Enum members
    X11_AQUA = "X11_AQUA"
    X11_GRAY0 = "X11_GRAY0"
    X11_GRAY25 = "X11_GRAY25"
    X11_GRAY50 = "X11_GRAY50"
    X11_GRAY75 = "X11_GRAY75"
    X11_GRAY100 = "X11_GRAY100"
    X11_GREEN1 = "X11_GREEN1"
    X11_GREEN2 = "X11_GREEN2"
    X11_GREEN3 = "X11_GREEN3"
    X11_GREEN4 = "X11_GREEN4"
    X11_BLUE1 = "X11_BLUE1"
    X11_BLUE2 = "X11_BLUE2"
    X11_BLUE3 = "X11_BLUE3"
    X11_BLUE4 = "X11_BLUE4"
    X11_RED1 = "X11_RED1"
    X11_RED2 = "X11_RED2"
    X11_RED3 = "X11_RED3"
    X11_RED4 = "X11_RED4"

# Set metadata after class creation to avoid it becoming an enum member
X11ColorEnum._metadata = {
    "X11_AQUA": {'description': 'X11 Aqua', 'meaning': 'HEX:00FFFF'},
    "X11_GRAY0": {'description': 'X11 Gray 0 (black)', 'meaning': 'HEX:000000'},
    "X11_GRAY25": {'description': 'X11 Gray 25%', 'meaning': 'HEX:404040'},
    "X11_GRAY50": {'description': 'X11 Gray 50%', 'meaning': 'HEX:808080'},
    "X11_GRAY75": {'description': 'X11 Gray 75%', 'meaning': 'HEX:BFBFBF'},
    "X11_GRAY100": {'description': 'X11 Gray 100 (white)', 'meaning': 'HEX:FFFFFF'},
    "X11_GREEN1": {'description': 'X11 Green 1', 'meaning': 'HEX:00FF00'},
    "X11_GREEN2": {'description': 'X11 Green 2', 'meaning': 'HEX:00EE00'},
    "X11_GREEN3": {'description': 'X11 Green 3', 'meaning': 'HEX:00CD00'},
    "X11_GREEN4": {'description': 'X11 Green 4', 'meaning': 'HEX:008B00'},
    "X11_BLUE1": {'description': 'X11 Blue 1', 'meaning': 'HEX:0000FF'},
    "X11_BLUE2": {'description': 'X11 Blue 2', 'meaning': 'HEX:0000EE'},
    "X11_BLUE3": {'description': 'X11 Blue 3', 'meaning': 'HEX:0000CD'},
    "X11_BLUE4": {'description': 'X11 Blue 4', 'meaning': 'HEX:00008B'},
    "X11_RED1": {'description': 'X11 Red 1', 'meaning': 'HEX:FF0000'},
    "X11_RED2": {'description': 'X11 Red 2', 'meaning': 'HEX:EE0000'},
    "X11_RED3": {'description': 'X11 Red 3', 'meaning': 'HEX:CD0000'},
    "X11_RED4": {'description': 'X11 Red 4', 'meaning': 'HEX:8B0000'},
}

class ColorSpaceEnum(RichEnum):
    """
    Color space and model types
    """
    # Enum members
    RGB = "RGB"
    CMYK = "CMYK"
    HSL = "HSL"
    HSV = "HSV"
    LAB = "LAB"
    PANTONE = "PANTONE"
    RAL = "RAL"
    NCS = "NCS"
    MUNSELL = "MUNSELL"

# Set metadata after class creation to avoid it becoming an enum member
ColorSpaceEnum._metadata = {
    "RGB": {'description': 'Red Green Blue color model'},
    "CMYK": {'description': 'Cyan Magenta Yellow Key (black) color model'},
    "HSL": {'description': 'Hue Saturation Lightness color model'},
    "HSV": {'description': 'Hue Saturation Value color model'},
    "LAB": {'description': 'CIELAB color space'},
    "PANTONE": {'description': 'Pantone Matching System'},
    "RAL": {'description': 'RAL color standard'},
    "NCS": {'description': 'Natural Color System'},
    "MUNSELL": {'description': 'Munsell color system'},
}

class EyeColorEnum(RichEnum):
    """
    Human eye color phenotypes
    """
    # Enum members
    BROWN = "BROWN"
    BLUE = "BLUE"
    GREEN = "GREEN"
    HAZEL = "HAZEL"
    AMBER = "AMBER"
    GRAY = "GRAY"
    HETEROCHROMIA = "HETEROCHROMIA"
    RED_PINK = "RED_PINK"
    VIOLET = "VIOLET"

# Set metadata after class creation to avoid it becoming an enum member
EyeColorEnum._metadata = {
    "BROWN": {'description': 'Brown eyes', 'annotations': {'hex_range': '663300-8B4513', 'prevalence': '79% worldwide'}},
    "BLUE": {'description': 'Blue eyes', 'meaning': 'HP:0000635', 'annotations': {'hex_range': '4169E1-87CEEB', 'prevalence': '8-10% worldwide'}},
    "GREEN": {'description': 'Green eyes', 'annotations': {'hex_range': '2E8B57-90EE90', 'prevalence': '2% worldwide'}},
    "HAZEL": {'description': 'Hazel eyes (brown-green mix)', 'annotations': {'hex_range': '8B7355-C9A878', 'prevalence': '5% worldwide'}},
    "AMBER": {'description': 'Amber/golden eyes', 'annotations': {'hex_range': 'FFBF00-FFB300', 'prevalence': 'rare'}},
    "GRAY": {'description': 'Gray eyes', 'meaning': 'HP:0007730', 'annotations': {'hex_range': '778899-C0C0C0', 'prevalence': '<1% worldwide'}},
    "HETEROCHROMIA": {'description': 'Different colored eyes', 'meaning': 'HP:0001100', 'annotations': {'note': 'complete or sectoral heterochromia'}},
    "RED_PINK": {'description': 'Red/pink eyes (albinism)', 'annotations': {'condition': 'associated with albinism'}},
    "VIOLET": {'description': 'Violet eyes (extremely rare)', 'annotations': {'hex_range': '8B7AB8-9370DB', 'prevalence': 'extremely rare'}},
}

class HairColorEnum(RichEnum):
    """
    Human hair color phenotypes
    """
    # Enum members
    BLACK = "BLACK"
    BROWN = "BROWN"
    DARK_BROWN = "DARK_BROWN"
    LIGHT_BROWN = "LIGHT_BROWN"
    BLONDE = "BLONDE"
    DARK_BLONDE = "DARK_BLONDE"
    LIGHT_BLONDE = "LIGHT_BLONDE"
    PLATINUM_BLONDE = "PLATINUM_BLONDE"
    STRAWBERRY_BLONDE = "STRAWBERRY_BLONDE"
    RED = "RED"
    AUBURN = "AUBURN"
    GINGER = "GINGER"
    GRAY = "GRAY"
    WHITE = "WHITE"
    SILVER = "SILVER"

# Set metadata after class creation to avoid it becoming an enum member
HairColorEnum._metadata = {
    "BLACK": {'description': 'Black hair', 'annotations': {'hex': '000000', 'prevalence': 'most common worldwide'}},
    "BROWN": {'description': 'Brown hair', 'annotations': {'hex_range': '654321-8B4513'}},
    "DARK_BROWN": {'description': 'Dark brown hair', 'annotations': {'hex': '3B2F2F'}},
    "LIGHT_BROWN": {'description': 'Light brown hair', 'annotations': {'hex': '977961'}},
    "BLONDE": {'description': 'Blonde/blond hair', 'meaning': 'HP:0002286', 'annotations': {'hex_range': 'FAF0BE-FFF8DC'}},
    "DARK_BLONDE": {'description': 'Dark blonde hair', 'annotations': {'hex': '9F8F71'}},
    "LIGHT_BLONDE": {'description': 'Light blonde hair', 'annotations': {'hex': 'FFF8DC'}},
    "PLATINUM_BLONDE": {'description': 'Platinum blonde hair', 'annotations': {'hex': 'E5E5E5'}},
    "STRAWBERRY_BLONDE": {'description': 'Strawberry blonde hair', 'annotations': {'hex': 'FF9966'}},
    "RED": {'description': 'Red hair', 'meaning': 'HP:0002297', 'annotations': {'hex_range': '922724-FF4500', 'prevalence': '1-2% worldwide'}},
    "AUBURN": {'description': 'Auburn hair (reddish-brown)', 'annotations': {'hex': 'A52A2A'}},
    "GINGER": {'description': 'Ginger hair (orange-red)', 'annotations': {'hex': 'FF6600'}},
    "GRAY": {'description': 'Gray hair', 'meaning': 'HP:0002216', 'annotations': {'hex_range': '808080-C0C0C0'}},
    "WHITE": {'description': 'White hair', 'meaning': 'HP:0011364', 'annotations': {'hex': 'FFFFFF'}},
    "SILVER": {'description': 'Silver hair', 'annotations': {'hex': 'C0C0C0'}},
}

class FlowerColorEnum(RichEnum):
    """
    Common flower colors
    """
    # Enum members
    RED = "RED"
    PINK = "PINK"
    ORANGE = "ORANGE"
    YELLOW = "YELLOW"
    WHITE = "WHITE"
    PURPLE = "PURPLE"
    VIOLET = "VIOLET"
    BLUE = "BLUE"
    LAVENDER = "LAVENDER"
    MAGENTA = "MAGENTA"
    BURGUNDY = "BURGUNDY"
    CORAL = "CORAL"
    PEACH = "PEACH"
    CREAM = "CREAM"
    BICOLOR = "BICOLOR"
    MULTICOLOR = "MULTICOLOR"

# Set metadata after class creation to avoid it becoming an enum member
FlowerColorEnum._metadata = {
    "RED": {'description': 'Red flowers', 'annotations': {'hex': 'FF0000', 'examples': 'roses, tulips, poppies'}},
    "PINK": {'description': 'Pink flowers', 'annotations': {'hex': 'FFC0CB', 'examples': 'peonies, cherry blossoms'}},
    "ORANGE": {'description': 'Orange flowers', 'annotations': {'hex': 'FFA500', 'examples': 'marigolds, zinnias'}},
    "YELLOW": {'description': 'Yellow flowers', 'annotations': {'hex': 'FFFF00', 'examples': 'sunflowers, daffodils'}},
    "WHITE": {'description': 'White flowers', 'annotations': {'hex': 'FFFFFF', 'examples': 'lilies, daisies'}},
    "PURPLE": {'description': 'Purple flowers', 'annotations': {'hex': '800080', 'examples': 'lavender, violets'}},
    "VIOLET": {'description': 'Violet flowers', 'annotations': {'hex': '7F00FF', 'examples': 'violets, pansies'}},
    "BLUE": {'description': 'Blue flowers', 'annotations': {'hex': '0000FF', 'examples': 'forget-me-nots, cornflowers'}},
    "LAVENDER": {'description': 'Lavender flowers', 'annotations': {'hex': 'E6E6FA', 'examples': 'lavender, wisteria'}},
    "MAGENTA": {'description': 'Magenta flowers', 'annotations': {'hex': 'FF00FF', 'examples': 'fuchsias, bougainvillea'}},
    "BURGUNDY": {'description': 'Burgundy/deep red flowers', 'annotations': {'hex': '800020', 'examples': 'dahlias, chrysanthemums'}},
    "CORAL": {'description': 'Coral flowers', 'annotations': {'hex': 'FF7F50', 'examples': 'coral bells, begonias'}},
    "PEACH": {'description': 'Peach flowers', 'annotations': {'hex': 'FFDAB9', 'examples': 'roses, dahlias'}},
    "CREAM": {'description': 'Cream flowers', 'annotations': {'hex': 'FFFDD0', 'examples': 'roses, tulips'}},
    "BICOLOR": {'description': 'Two-colored flowers', 'annotations': {'note': 'flowers with two distinct colors'}},
    "MULTICOLOR": {'description': 'Multi-colored flowers', 'annotations': {'note': 'flowers with more than two colors'}},
}

class AnimalCoatColorEnum(RichEnum):
    """
    Animal coat/fur colors
    """
    # Enum members
    BLACK = "BLACK"
    WHITE = "WHITE"
    BROWN = "BROWN"
    TAN = "TAN"
    CREAM = "CREAM"
    GRAY = "GRAY"
    RED = "RED"
    GOLDEN = "GOLDEN"
    FAWN = "FAWN"
    BRINDLE = "BRINDLE"
    SPOTTED = "SPOTTED"
    MERLE = "MERLE"
    PIEBALD = "PIEBALD"
    CALICO = "CALICO"
    TABBY = "TABBY"
    TORTOISESHELL = "TORTOISESHELL"
    ROAN = "ROAN"
    PALOMINO = "PALOMINO"
    CHESTNUT = "CHESTNUT"
    BAY = "BAY"

# Set metadata after class creation to avoid it becoming an enum member
AnimalCoatColorEnum._metadata = {
    "BLACK": {'description': 'Black coat', 'annotations': {'hex': '000000'}},
    "WHITE": {'description': 'White coat', 'annotations': {'hex': 'FFFFFF'}},
    "BROWN": {'description': 'Brown coat', 'annotations': {'hex': '964B00'}},
    "TAN": {'description': 'Tan coat', 'annotations': {'hex': 'D2B48C'}},
    "CREAM": {'description': 'Cream coat', 'annotations': {'hex': 'FFFDD0'}},
    "GRAY": {'description': 'Gray coat', 'annotations': {'hex': '808080'}},
    "RED": {'description': 'Red/rust coat', 'annotations': {'hex': 'B22222'}},
    "GOLDEN": {'description': 'Golden coat', 'annotations': {'hex': 'FFD700'}},
    "FAWN": {'description': 'Fawn coat', 'annotations': {'hex': 'E5AA70'}},
    "BRINDLE": {'description': 'Brindle pattern (striped)', 'annotations': {'pattern': 'striped mixture of colors'}},
    "SPOTTED": {'description': 'Spotted pattern', 'annotations': {'pattern': 'spots on base color'}},
    "MERLE": {'description': 'Merle pattern (mottled)', 'annotations': {'pattern': 'mottled patches'}},
    "PIEBALD": {'description': 'Piebald pattern (patches)', 'annotations': {'pattern': 'irregular patches'}},
    "CALICO": {'description': 'Calico pattern (tri-color)', 'annotations': {'pattern': 'tri-color patches', 'species': 'primarily cats'}},
    "TABBY": {'description': 'Tabby pattern (striped)', 'annotations': {'pattern': 'striped or spotted', 'species': 'primarily cats'}},
    "TORTOISESHELL": {'description': 'Tortoiseshell pattern', 'annotations': {'pattern': 'mottled orange and black', 'species': 'primarily cats'}},
    "ROAN": {'description': 'Roan pattern (mixed white)', 'annotations': {'pattern': 'white mixed with base color', 'species': 'primarily horses'}},
    "PALOMINO": {'description': 'Palomino (golden with white mane)', 'annotations': {'hex': 'DEC05F', 'species': 'horses'}},
    "CHESTNUT": {'description': 'Chestnut/sorrel', 'annotations': {'hex': 'CD5C5C', 'species': 'horses'}},
    "BAY": {'description': 'Bay (brown with black points)', 'annotations': {'species': 'horses'}},
}

class SkinToneEnum(RichEnum):
    """
    Human skin tone classifications (Fitzpatrick scale based)
    """
    # Enum members
    TYPE_I = "TYPE_I"
    TYPE_II = "TYPE_II"
    TYPE_III = "TYPE_III"
    TYPE_IV = "TYPE_IV"
    TYPE_V = "TYPE_V"
    TYPE_VI = "TYPE_VI"

# Set metadata after class creation to avoid it becoming an enum member
SkinToneEnum._metadata = {
    "TYPE_I": {'description': 'Very pale white skin', 'annotations': {'fitzpatrick': 'Type I', 'hex_range': 'FFE0BD-FFDFC4', 'sun_reaction': 'always burns, never tans'}},
    "TYPE_II": {'description': 'Fair white skin', 'annotations': {'fitzpatrick': 'Type II', 'hex_range': 'F0D5BE-E8C5A0', 'sun_reaction': 'burns easily, tans minimally'}},
    "TYPE_III": {'description': 'Light brown skin', 'annotations': {'fitzpatrick': 'Type III', 'hex_range': 'DDA582-CD9766', 'sun_reaction': 'burns moderately, tans gradually'}},
    "TYPE_IV": {'description': 'Moderate brown skin', 'annotations': {'fitzpatrick': 'Type IV', 'hex_range': 'B87659-A47148', 'sun_reaction': 'burns minimally, tans easily'}},
    "TYPE_V": {'description': 'Dark brown skin', 'annotations': {'fitzpatrick': 'Type V', 'hex_range': '935D37-7C4E2A', 'sun_reaction': 'rarely burns, tans darkly'}},
    "TYPE_VI": {'description': 'Very dark brown to black skin', 'annotations': {'fitzpatrick': 'Type VI', 'hex_range': '5C3A1E-3D2314', 'sun_reaction': 'never burns, always tans darkly'}},
}

class PlantLeafColorEnum(RichEnum):
    """
    Plant leaf colors (including seasonal changes)
    """
    # Enum members
    GREEN = "GREEN"
    DARK_GREEN = "DARK_GREEN"
    LIGHT_GREEN = "LIGHT_GREEN"
    YELLOW_GREEN = "YELLOW_GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"
    PURPLE = "PURPLE"
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    VARIEGATED = "VARIEGATED"
    BROWN = "BROWN"

# Set metadata after class creation to avoid it becoming an enum member
PlantLeafColorEnum._metadata = {
    "GREEN": {'description': 'Green leaves (healthy/summer)', 'meaning': 'PATO:0000320', 'annotations': {'hex_range': '228B22-90EE90', 'season': 'spring/summer'}},
    "DARK_GREEN": {'description': 'Dark green leaves', 'annotations': {'hex': '006400'}},
    "LIGHT_GREEN": {'description': 'Light green leaves', 'annotations': {'hex': '90EE90'}},
    "YELLOW_GREEN": {'description': 'Yellow-green leaves', 'annotations': {'hex': '9ACD32', 'condition': 'new growth or nutrient deficiency'}},
    "YELLOW": {'description': 'Yellow leaves (autumn or chlorosis)', 'meaning': 'PATO:0000324', 'annotations': {'hex': 'FFD700', 'season': 'autumn'}},
    "ORANGE": {'description': 'Orange leaves (autumn)', 'annotations': {'hex': 'FF8C00', 'season': 'autumn'}},
    "RED": {'description': 'Red leaves (autumn or certain species)', 'meaning': 'PATO:0000322', 'annotations': {'hex': 'DC143C', 'season': 'autumn'}},
    "PURPLE": {'description': 'Purple leaves (certain species)', 'annotations': {'hex': '800080', 'examples': 'purple basil, Japanese maple'}},
    "BRONZE": {'description': 'Bronze leaves', 'annotations': {'hex': 'CD7F32'}},
    "SILVER": {'description': 'Silver/gray leaves', 'annotations': {'hex': 'C0C0C0', 'examples': 'dusty miller, artemisia'}},
    "VARIEGATED": {'description': 'Variegated leaves (multiple colors)', 'annotations': {'pattern': 'mixed colors/patterns'}},
    "BROWN": {'description': 'Brown leaves (dead/dying)', 'annotations': {'hex': '964B00', 'condition': 'senescent or dead'}},
}

class DNABaseEnum(RichEnum):
    """
    Standard DNA nucleotide bases (canonical)
    """
    # Enum members
    A = "A"
    C = "C"
    G = "G"
    T = "T"

# Set metadata after class creation to avoid it becoming an enum member
DNABaseEnum._metadata = {
    "A": {'meaning': 'CHEBI:16708', 'annotations': {'complement': 'T', 'purine': 'true', 'chemical_formula': 'C5H5N5'}, 'aliases': ['adenine']},
    "C": {'meaning': 'CHEBI:16040', 'annotations': {'complement': 'G', 'pyrimidine': 'true', 'chemical_formula': 'C4H5N3O'}, 'aliases': ['cytosine']},
    "G": {'meaning': 'CHEBI:16235', 'annotations': {'complement': 'C', 'purine': 'true', 'chemical_formula': 'C5H5N5O'}, 'aliases': ['guanine']},
    "T": {'meaning': 'CHEBI:17821', 'annotations': {'complement': 'A', 'pyrimidine': 'true', 'chemical_formula': 'C5H6N2O2'}, 'aliases': ['thymine']},
}

class DNABaseExtendedEnum(RichEnum):
    """
    Extended DNA alphabet with IUPAC ambiguity codes
    """
    # Enum members
    A = "A"
    C = "C"
    G = "G"
    T = "T"
    R = "R"
    Y = "Y"
    S = "S"
    W = "W"
    K = "K"
    M = "M"
    B = "B"
    D = "D"
    H = "H"
    V = "V"
    N = "N"
    GAP = "GAP"

# Set metadata after class creation to avoid it becoming an enum member
DNABaseExtendedEnum._metadata = {
    "A": {'meaning': 'CHEBI:16708', 'annotations': {'represents': 'A'}, 'aliases': ['adenine']},
    "C": {'meaning': 'CHEBI:16040', 'annotations': {'represents': 'C'}, 'aliases': ['cytosine']},
    "G": {'meaning': 'CHEBI:16235', 'annotations': {'represents': 'G'}, 'aliases': ['guanine']},
    "T": {'meaning': 'CHEBI:17821', 'annotations': {'represents': 'T'}, 'aliases': ['thymine']},
    "R": {'annotations': {'represents': 'A,G', 'iupac': 'true'}},
    "Y": {'annotations': {'represents': 'C,T', 'iupac': 'true'}},
    "S": {'annotations': {'represents': 'G,C', 'iupac': 'true', 'bond_strength': 'strong (3 H-bonds)'}},
    "W": {'annotations': {'represents': 'A,T', 'iupac': 'true', 'bond_strength': 'weak (2 H-bonds)'}},
    "K": {'annotations': {'represents': 'G,T', 'iupac': 'true'}},
    "M": {'annotations': {'represents': 'A,C', 'iupac': 'true'}},
    "B": {'annotations': {'represents': 'C,G,T', 'iupac': 'true'}},
    "D": {'annotations': {'represents': 'A,G,T', 'iupac': 'true'}},
    "H": {'annotations': {'represents': 'A,C,T', 'iupac': 'true'}},
    "V": {'annotations': {'represents': 'A,C,G', 'iupac': 'true'}},
    "N": {'annotations': {'represents': 'A,C,G,T', 'iupac': 'true'}},
    "GAP": {'annotations': {'symbol': '-', 'represents': 'gap'}},
}

class RNABaseEnum(RichEnum):
    """
    Standard RNA nucleotide bases (canonical)
    """
    # Enum members
    A = "A"
    C = "C"
    G = "G"
    U = "U"

# Set metadata after class creation to avoid it becoming an enum member
RNABaseEnum._metadata = {
    "A": {'meaning': 'CHEBI:16708', 'annotations': {'complement': 'U', 'purine': 'true', 'chemical_formula': 'C5H5N5'}, 'aliases': ['adenine']},
    "C": {'meaning': 'CHEBI:16040', 'annotations': {'complement': 'G', 'pyrimidine': 'true', 'chemical_formula': 'C4H5N3O'}, 'aliases': ['cytosine']},
    "G": {'meaning': 'CHEBI:16235', 'annotations': {'complement': 'C', 'purine': 'true', 'chemical_formula': 'C5H5N5O'}, 'aliases': ['guanine']},
    "U": {'meaning': 'CHEBI:17568', 'annotations': {'complement': 'A', 'pyrimidine': 'true', 'chemical_formula': 'C4H4N2O2'}, 'aliases': ['uracil']},
}

class RNABaseExtendedEnum(RichEnum):
    """
    Extended RNA alphabet with IUPAC ambiguity codes
    """
    # Enum members
    A = "A"
    C = "C"
    G = "G"
    U = "U"
    R = "R"
    Y = "Y"
    S = "S"
    W = "W"
    K = "K"
    M = "M"
    B = "B"
    D = "D"
    H = "H"
    V = "V"
    N = "N"
    GAP = "GAP"

# Set metadata after class creation to avoid it becoming an enum member
RNABaseExtendedEnum._metadata = {
    "A": {'meaning': 'CHEBI:16708', 'annotations': {'represents': 'A'}, 'aliases': ['adenine']},
    "C": {'meaning': 'CHEBI:16040', 'annotations': {'represents': 'C'}, 'aliases': ['cytosine']},
    "G": {'meaning': 'CHEBI:16235', 'annotations': {'represents': 'G'}, 'aliases': ['guanine']},
    "U": {'meaning': 'CHEBI:17568', 'annotations': {'represents': 'U'}, 'aliases': ['uracil']},
    "R": {'annotations': {'represents': 'A,G', 'iupac': 'true'}},
    "Y": {'annotations': {'represents': 'C,U', 'iupac': 'true'}},
    "S": {'annotations': {'represents': 'G,C', 'iupac': 'true'}},
    "W": {'annotations': {'represents': 'A,U', 'iupac': 'true'}},
    "K": {'annotations': {'represents': 'G,U', 'iupac': 'true'}},
    "M": {'annotations': {'represents': 'A,C', 'iupac': 'true'}},
    "B": {'annotations': {'represents': 'C,G,U', 'iupac': 'true'}},
    "D": {'annotations': {'represents': 'A,G,U', 'iupac': 'true'}},
    "H": {'annotations': {'represents': 'A,C,U', 'iupac': 'true'}},
    "V": {'annotations': {'represents': 'A,C,G', 'iupac': 'true'}},
    "N": {'annotations': {'represents': 'A,C,G,U', 'iupac': 'true'}},
    "GAP": {'annotations': {'symbol': '-', 'represents': 'gap'}},
}

class AminoAcidEnum(RichEnum):
    """
    Standard amino acid single letter codes
    """
    # Enum members
    A = "A"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    K = "K"
    L = "L"
    M = "M"
    N = "N"
    P = "P"
    Q = "Q"
    R = "R"
    S = "S"
    T = "T"
    V = "V"
    W = "W"
    Y = "Y"

# Set metadata after class creation to avoid it becoming an enum member
AminoAcidEnum._metadata = {
    "A": {'meaning': 'CHEBI:16449', 'annotations': {'three_letter': 'Ala', 'polarity': 'nonpolar', 'essential': 'false', 'molecular_weight': '89.09'}, 'aliases': ['alanine']},
    "C": {'meaning': 'CHEBI:17561', 'annotations': {'three_letter': 'Cys', 'polarity': 'polar', 'essential': 'false', 'molecular_weight': '121.15', 'special': 'forms disulfide bonds'}, 'aliases': ['L-cysteine']},
    "D": {'meaning': 'CHEBI:17053', 'annotations': {'three_letter': 'Asp', 'polarity': 'acidic', 'essential': 'false', 'molecular_weight': '133.10', 'charge': 'negative'}, 'aliases': ['L-aspartic acid']},
    "E": {'meaning': 'CHEBI:16015', 'annotations': {'three_letter': 'Glu', 'polarity': 'acidic', 'essential': 'false', 'molecular_weight': '147.13', 'charge': 'negative'}, 'aliases': ['L-glutamic acid']},
    "F": {'meaning': 'CHEBI:17295', 'annotations': {'three_letter': 'Phe', 'polarity': 'nonpolar', 'essential': 'true', 'molecular_weight': '165.19', 'aromatic': 'true'}, 'aliases': ['L-phenylalanine']},
    "G": {'meaning': 'CHEBI:15428', 'annotations': {'three_letter': 'Gly', 'polarity': 'nonpolar', 'essential': 'false', 'molecular_weight': '75.07', 'special': 'smallest, most flexible'}, 'aliases': ['glycine']},
    "H": {'meaning': 'CHEBI:15971', 'annotations': {'three_letter': 'His', 'polarity': 'basic', 'essential': 'true', 'molecular_weight': '155.16', 'charge': 'positive'}, 'aliases': ['L-histidine']},
    "I": {'meaning': 'CHEBI:17191', 'annotations': {'three_letter': 'Ile', 'polarity': 'nonpolar', 'essential': 'true', 'molecular_weight': '131.17', 'branched': 'true'}, 'aliases': ['L-isoleucine']},
    "K": {'meaning': 'CHEBI:18019', 'annotations': {'three_letter': 'Lys', 'polarity': 'basic', 'essential': 'true', 'molecular_weight': '146.19', 'charge': 'positive'}, 'aliases': ['L-lysine']},
    "L": {'meaning': 'CHEBI:15603', 'annotations': {'three_letter': 'Leu', 'polarity': 'nonpolar', 'essential': 'true', 'molecular_weight': '131.17', 'branched': 'true'}, 'aliases': ['L-leucine']},
    "M": {'meaning': 'CHEBI:16643', 'annotations': {'three_letter': 'Met', 'polarity': 'nonpolar', 'essential': 'true', 'molecular_weight': '149.21', 'special': 'start codon'}, 'aliases': ['L-methionine']},
    "N": {'meaning': 'CHEBI:17196', 'annotations': {'three_letter': 'Asn', 'polarity': 'polar', 'essential': 'false', 'molecular_weight': '132.12'}, 'aliases': ['L-asparagine']},
    "P": {'meaning': 'CHEBI:17203', 'annotations': {'three_letter': 'Pro', 'polarity': 'nonpolar', 'essential': 'false', 'molecular_weight': '115.13', 'special': 'helix breaker, rigid'}, 'aliases': ['L-proline']},
    "Q": {'meaning': 'CHEBI:18050', 'annotations': {'three_letter': 'Gln', 'polarity': 'polar', 'essential': 'false', 'molecular_weight': '146.15'}, 'aliases': ['L-glutamine']},
    "R": {'meaning': 'CHEBI:16467', 'annotations': {'three_letter': 'Arg', 'polarity': 'basic', 'essential': 'false', 'molecular_weight': '174.20', 'charge': 'positive'}, 'aliases': ['L-arginine']},
    "S": {'meaning': 'CHEBI:17115', 'annotations': {'three_letter': 'Ser', 'polarity': 'polar', 'essential': 'false', 'molecular_weight': '105.09', 'hydroxyl': 'true'}, 'aliases': ['L-serine']},
    "T": {'meaning': 'CHEBI:16857', 'annotations': {'three_letter': 'Thr', 'polarity': 'polar', 'essential': 'true', 'molecular_weight': '119.12', 'hydroxyl': 'true'}, 'aliases': ['L-threonine']},
    "V": {'meaning': 'CHEBI:16414', 'annotations': {'three_letter': 'Val', 'polarity': 'nonpolar', 'essential': 'true', 'molecular_weight': '117.15', 'branched': 'true'}, 'aliases': ['L-valine']},
    "W": {'meaning': 'CHEBI:16828', 'annotations': {'three_letter': 'Trp', 'polarity': 'nonpolar', 'essential': 'true', 'molecular_weight': '204.23', 'aromatic': 'true', 'special': 'largest'}, 'aliases': ['L-tryptophan']},
    "Y": {'meaning': 'CHEBI:17895', 'annotations': {'three_letter': 'Tyr', 'polarity': 'polar', 'essential': 'false', 'molecular_weight': '181.19', 'aromatic': 'true', 'hydroxyl': 'true'}, 'aliases': ['L-tyrosine']},
}

class AminoAcidExtendedEnum(RichEnum):
    """
    Extended amino acid alphabet with ambiguity codes and special characters
    """
    # Enum members
    A = "A"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    K = "K"
    L = "L"
    M = "M"
    N = "N"
    P = "P"
    Q = "Q"
    R = "R"
    S = "S"
    T = "T"
    V = "V"
    W = "W"
    Y = "Y"
    B = "B"
    Z = "Z"
    J = "J"
    X = "X"
    STOP = "STOP"
    GAP = "GAP"
    U = "U"
    O = "O"

# Set metadata after class creation to avoid it becoming an enum member
AminoAcidExtendedEnum._metadata = {
    "A": {'meaning': 'CHEBI:16449', 'annotations': {'three_letter': 'Ala'}, 'aliases': ['alanine']},
    "C": {'meaning': 'CHEBI:17561', 'annotations': {'three_letter': 'Cys'}, 'aliases': ['L-cysteine']},
    "D": {'meaning': 'CHEBI:17053', 'annotations': {'three_letter': 'Asp'}, 'aliases': ['L-aspartic acid']},
    "E": {'meaning': 'CHEBI:16015', 'annotations': {'three_letter': 'Glu'}, 'aliases': ['L-glutamic acid']},
    "F": {'meaning': 'CHEBI:17295', 'annotations': {'three_letter': 'Phe'}, 'aliases': ['L-phenylalanine']},
    "G": {'meaning': 'CHEBI:15428', 'annotations': {'three_letter': 'Gly'}, 'aliases': ['glycine']},
    "H": {'meaning': 'CHEBI:15971', 'annotations': {'three_letter': 'His'}, 'aliases': ['L-histidine']},
    "I": {'meaning': 'CHEBI:17191', 'annotations': {'three_letter': 'Ile'}, 'aliases': ['L-isoleucine']},
    "K": {'meaning': 'CHEBI:18019', 'annotations': {'three_letter': 'Lys'}, 'aliases': ['L-lysine']},
    "L": {'meaning': 'CHEBI:15603', 'annotations': {'three_letter': 'Leu'}, 'aliases': ['L-leucine']},
    "M": {'meaning': 'CHEBI:16643', 'annotations': {'three_letter': 'Met'}, 'aliases': ['L-methionine']},
    "N": {'meaning': 'CHEBI:17196', 'annotations': {'three_letter': 'Asn'}, 'aliases': ['L-asparagine']},
    "P": {'meaning': 'CHEBI:17203', 'annotations': {'three_letter': 'Pro'}, 'aliases': ['L-proline']},
    "Q": {'meaning': 'CHEBI:18050', 'annotations': {'three_letter': 'Gln'}, 'aliases': ['L-glutamine']},
    "R": {'meaning': 'CHEBI:16467', 'annotations': {'three_letter': 'Arg'}, 'aliases': ['L-arginine']},
    "S": {'meaning': 'CHEBI:17115', 'annotations': {'three_letter': 'Ser'}, 'aliases': ['L-serine']},
    "T": {'meaning': 'CHEBI:16857', 'annotations': {'three_letter': 'Thr'}, 'aliases': ['L-threonine']},
    "V": {'meaning': 'CHEBI:16414', 'annotations': {'three_letter': 'Val'}, 'aliases': ['L-valine']},
    "W": {'meaning': 'CHEBI:16828', 'annotations': {'three_letter': 'Trp'}, 'aliases': ['L-tryptophan']},
    "Y": {'meaning': 'CHEBI:17895', 'annotations': {'three_letter': 'Tyr'}, 'aliases': ['L-tyrosine']},
    "B": {'annotations': {'three_letter': 'Asx', 'represents': 'D,N', 'ambiguity': 'true'}, 'aliases': ['L-aspartic acid or Asparagine (D or N)']},
    "Z": {'annotations': {'three_letter': 'Glx', 'represents': 'E,Q', 'ambiguity': 'true'}, 'aliases': ['L-glutamic acid or Glutamine (E or Q)']},
    "J": {'annotations': {'three_letter': 'Xle', 'represents': 'L,I', 'ambiguity': 'true'}, 'aliases': ['L-leucine or Isoleucine (L or I)']},
    "X": {'annotations': {'three_letter': 'Xaa', 'represents': 'any', 'ambiguity': 'true'}},
    "STOP": {'annotations': {'symbol': '*', 'three_letter': 'Ter', 'represents': 'stop codon'}},
    "GAP": {'annotations': {'symbol': '-', 'represents': 'gap'}},
    "U": {'meaning': 'CHEBI:16633', 'annotations': {'three_letter': 'Sec', 'special': '21st amino acid', 'codon': 'UGA with SECIS element'}, 'aliases': ['L-selenocysteine']},
    "O": {'meaning': 'CHEBI:21860', 'annotations': {'three_letter': 'Pyl', 'special': '22nd amino acid', 'codon': 'UAG in certain archaea/bacteria'}, 'aliases': ['L-pyrrolysine']},
}

class CodonEnum(RichEnum):
    """
    Standard genetic code codons (DNA)
    """
    # Enum members
    TTT = "TTT"
    TTC = "TTC"
    TTA = "TTA"
    TTG = "TTG"
    CTT = "CTT"
    CTC = "CTC"
    CTA = "CTA"
    CTG = "CTG"
    ATT = "ATT"
    ATC = "ATC"
    ATA = "ATA"
    ATG = "ATG"
    GTT = "GTT"
    GTC = "GTC"
    GTA = "GTA"
    GTG = "GTG"
    TCT = "TCT"
    TCC = "TCC"
    TCA = "TCA"
    TCG = "TCG"
    AGT = "AGT"
    AGC = "AGC"
    CCT = "CCT"
    CCC = "CCC"
    CCA = "CCA"
    CCG = "CCG"
    ACT = "ACT"
    ACC = "ACC"
    ACA = "ACA"
    ACG = "ACG"
    GCT = "GCT"
    GCC = "GCC"
    GCA = "GCA"
    GCG = "GCG"
    TAT = "TAT"
    TAC = "TAC"
    TAA = "TAA"
    TAG = "TAG"
    TGA = "TGA"
    CAT = "CAT"
    CAC = "CAC"
    CAA = "CAA"
    CAG = "CAG"
    AAT = "AAT"
    AAC = "AAC"
    AAA = "AAA"
    AAG = "AAG"
    GAT = "GAT"
    GAC = "GAC"
    GAA = "GAA"
    GAG = "GAG"
    TGT = "TGT"
    TGC = "TGC"
    TGG = "TGG"
    CGT = "CGT"
    CGC = "CGC"
    CGA = "CGA"
    CGG = "CGG"
    AGA = "AGA"
    AGG = "AGG"
    GGT = "GGT"
    GGC = "GGC"
    GGA = "GGA"
    GGG = "GGG"

# Set metadata after class creation to avoid it becoming an enum member
CodonEnum._metadata = {
    "TTT": {'annotations': {'amino_acid': 'F', 'amino_acid_name': 'Phenylalanine'}},
    "TTC": {'annotations': {'amino_acid': 'F', 'amino_acid_name': 'Phenylalanine'}},
    "TTA": {'annotations': {'amino_acid': 'L', 'amino_acid_name': 'Leucine'}},
    "TTG": {'annotations': {'amino_acid': 'L', 'amino_acid_name': 'Leucine'}},
    "CTT": {'annotations': {'amino_acid': 'L', 'amino_acid_name': 'Leucine'}},
    "CTC": {'annotations': {'amino_acid': 'L', 'amino_acid_name': 'Leucine'}},
    "CTA": {'annotations': {'amino_acid': 'L', 'amino_acid_name': 'Leucine'}},
    "CTG": {'annotations': {'amino_acid': 'L', 'amino_acid_name': 'Leucine'}},
    "ATT": {'annotations': {'amino_acid': 'I', 'amino_acid_name': 'Isoleucine'}},
    "ATC": {'annotations': {'amino_acid': 'I', 'amino_acid_name': 'Isoleucine'}},
    "ATA": {'annotations': {'amino_acid': 'I', 'amino_acid_name': 'Isoleucine'}},
    "ATG": {'annotations': {'amino_acid': 'M', 'amino_acid_name': 'Methionine', 'special': 'start codon'}},
    "GTT": {'annotations': {'amino_acid': 'V', 'amino_acid_name': 'Valine'}},
    "GTC": {'annotations': {'amino_acid': 'V', 'amino_acid_name': 'Valine'}},
    "GTA": {'annotations': {'amino_acid': 'V', 'amino_acid_name': 'Valine'}},
    "GTG": {'annotations': {'amino_acid': 'V', 'amino_acid_name': 'Valine'}},
    "TCT": {'annotations': {'amino_acid': 'S', 'amino_acid_name': 'Serine'}},
    "TCC": {'annotations': {'amino_acid': 'S', 'amino_acid_name': 'Serine'}},
    "TCA": {'annotations': {'amino_acid': 'S', 'amino_acid_name': 'Serine'}},
    "TCG": {'annotations': {'amino_acid': 'S', 'amino_acid_name': 'Serine'}},
    "AGT": {'annotations': {'amino_acid': 'S', 'amino_acid_name': 'Serine'}},
    "AGC": {'annotations': {'amino_acid': 'S', 'amino_acid_name': 'Serine'}},
    "CCT": {'annotations': {'amino_acid': 'P', 'amino_acid_name': 'Proline'}},
    "CCC": {'annotations': {'amino_acid': 'P', 'amino_acid_name': 'Proline'}},
    "CCA": {'annotations': {'amino_acid': 'P', 'amino_acid_name': 'Proline'}},
    "CCG": {'annotations': {'amino_acid': 'P', 'amino_acid_name': 'Proline'}},
    "ACT": {'annotations': {'amino_acid': 'T', 'amino_acid_name': 'Threonine'}},
    "ACC": {'annotations': {'amino_acid': 'T', 'amino_acid_name': 'Threonine'}},
    "ACA": {'annotations': {'amino_acid': 'T', 'amino_acid_name': 'Threonine'}},
    "ACG": {'annotations': {'amino_acid': 'T', 'amino_acid_name': 'Threonine'}},
    "GCT": {'annotations': {'amino_acid': 'A', 'amino_acid_name': 'Alanine'}},
    "GCC": {'annotations': {'amino_acid': 'A', 'amino_acid_name': 'Alanine'}},
    "GCA": {'annotations': {'amino_acid': 'A', 'amino_acid_name': 'Alanine'}},
    "GCG": {'annotations': {'amino_acid': 'A', 'amino_acid_name': 'Alanine'}},
    "TAT": {'annotations': {'amino_acid': 'Y', 'amino_acid_name': 'Tyrosine'}},
    "TAC": {'annotations': {'amino_acid': 'Y', 'amino_acid_name': 'Tyrosine'}},
    "TAA": {'annotations': {'amino_acid': '*', 'name': 'ochre', 'special': 'stop codon'}},
    "TAG": {'annotations': {'amino_acid': '*', 'name': 'amber', 'special': 'stop codon'}},
    "TGA": {'annotations': {'amino_acid': '*', 'name': 'opal', 'special': 'stop codon or selenocysteine'}},
    "CAT": {'annotations': {'amino_acid': 'H', 'amino_acid_name': 'Histidine'}},
    "CAC": {'annotations': {'amino_acid': 'H', 'amino_acid_name': 'Histidine'}},
    "CAA": {'annotations': {'amino_acid': 'Q', 'amino_acid_name': 'Glutamine'}},
    "CAG": {'annotations': {'amino_acid': 'Q', 'amino_acid_name': 'Glutamine'}},
    "AAT": {'annotations': {'amino_acid': 'N', 'amino_acid_name': 'Asparagine'}},
    "AAC": {'annotations': {'amino_acid': 'N', 'amino_acid_name': 'Asparagine'}},
    "AAA": {'annotations': {'amino_acid': 'K', 'amino_acid_name': 'Lysine'}},
    "AAG": {'annotations': {'amino_acid': 'K', 'amino_acid_name': 'Lysine'}},
    "GAT": {'annotations': {'amino_acid': 'D', 'amino_acid_name': 'Aspartic acid'}},
    "GAC": {'annotations': {'amino_acid': 'D', 'amino_acid_name': 'Aspartic acid'}},
    "GAA": {'annotations': {'amino_acid': 'E', 'amino_acid_name': 'Glutamic acid'}},
    "GAG": {'annotations': {'amino_acid': 'E', 'amino_acid_name': 'Glutamic acid'}},
    "TGT": {'annotations': {'amino_acid': 'C', 'amino_acid_name': 'Cysteine'}},
    "TGC": {'annotations': {'amino_acid': 'C', 'amino_acid_name': 'Cysteine'}},
    "TGG": {'annotations': {'amino_acid': 'W', 'amino_acid_name': 'Tryptophan'}},
    "CGT": {'annotations': {'amino_acid': 'R', 'amino_acid_name': 'Arginine'}},
    "CGC": {'annotations': {'amino_acid': 'R', 'amino_acid_name': 'Arginine'}},
    "CGA": {'annotations': {'amino_acid': 'R', 'amino_acid_name': 'Arginine'}},
    "CGG": {'annotations': {'amino_acid': 'R', 'amino_acid_name': 'Arginine'}},
    "AGA": {'annotations': {'amino_acid': 'R', 'amino_acid_name': 'Arginine'}},
    "AGG": {'annotations': {'amino_acid': 'R', 'amino_acid_name': 'Arginine'}},
    "GGT": {'annotations': {'amino_acid': 'G', 'amino_acid_name': 'Glycine'}},
    "GGC": {'annotations': {'amino_acid': 'G', 'amino_acid_name': 'Glycine'}},
    "GGA": {'annotations': {'amino_acid': 'G', 'amino_acid_name': 'Glycine'}},
    "GGG": {'annotations': {'amino_acid': 'G', 'amino_acid_name': 'Glycine'}},
}

class NucleotideModificationEnum(RichEnum):
    """
    Common nucleotide modifications
    """
    # Enum members
    FIVE_METHYL_C = "FIVE_METHYL_C"
    SIX_METHYL_A = "SIX_METHYL_A"
    PSEUDOURIDINE = "PSEUDOURIDINE"
    INOSINE = "INOSINE"
    DIHYDROURIDINE = "DIHYDROURIDINE"
    SEVEN_METHYL_G = "SEVEN_METHYL_G"
    FIVE_HYDROXY_METHYL_C = "FIVE_HYDROXY_METHYL_C"
    EIGHT_OXO_G = "EIGHT_OXO_G"

# Set metadata after class creation to avoid it becoming an enum member
NucleotideModificationEnum._metadata = {
    "FIVE_METHYL_C": {'description': '5-methylcytosine', 'meaning': 'CHEBI:27551', 'annotations': {'symbol': 'm5C', 'type': 'DNA methylation', 'function': 'gene regulation'}},
    "SIX_METHYL_A": {'description': 'N6-methyladenosine', 'meaning': 'CHEBI:21891', 'annotations': {'symbol': 'm6A', 'type': 'RNA modification', 'function': 'RNA stability, translation'}},
    "PSEUDOURIDINE": {'description': 'Pseudouridine', 'meaning': 'CHEBI:17802', 'annotations': {'symbol': 'Ψ', 'type': 'RNA modification', 'function': 'RNA stability'}},
    "INOSINE": {'description': 'Inosine', 'meaning': 'CHEBI:17596', 'annotations': {'symbol': 'I', 'type': 'RNA editing', 'pairs_with': 'A, C, U'}},
    "DIHYDROURIDINE": {'description': 'Dihydrouridine', 'meaning': 'CHEBI:23774', 'annotations': {'symbol': 'D', 'type': 'tRNA modification'}},
    "SEVEN_METHYL_G": {'description': '7-methylguanosine', 'meaning': 'CHEBI:20794', 'annotations': {'symbol': 'm7G', 'type': 'mRNA cap', 'function': 'translation initiation'}},
    "FIVE_HYDROXY_METHYL_C": {'description': '5-hydroxymethylcytosine', 'meaning': 'CHEBI:76792', 'annotations': {'symbol': 'hmC', 'type': 'DNA modification', 'function': 'demethylation intermediate'}},
    "EIGHT_OXO_G": {'description': '8-oxoguanine', 'meaning': 'CHEBI:44605', 'annotations': {'symbol': '8-oxoG', 'type': 'oxidative damage', 'pairs_with': 'A or C'}},
}

class SequenceQualityEnum(RichEnum):
    """
    Sequence quality indicators (Phred scores)
    """
    # Enum members
    Q0 = "Q0"
    Q10 = "Q10"
    Q20 = "Q20"
    Q30 = "Q30"
    Q40 = "Q40"
    Q50 = "Q50"
    Q60 = "Q60"

# Set metadata after class creation to avoid it becoming an enum member
SequenceQualityEnum._metadata = {
    "Q0": {'description': 'Phred quality 0 (100% error probability)', 'annotations': {'phred_score': '0', 'error_probability': '1.0', 'ascii_char': '!'}},
    "Q10": {'description': 'Phred quality 10 (10% error probability)', 'annotations': {'phred_score': '10', 'error_probability': '0.1', 'ascii_char': '+'}},
    "Q20": {'description': 'Phred quality 20 (1% error probability)', 'annotations': {'phred_score': '20', 'error_probability': '0.01', 'ascii_char': '5'}},
    "Q30": {'description': 'Phred quality 30 (0.1% error probability)', 'annotations': {'phred_score': '30', 'error_probability': '0.001', 'ascii_char': '?'}},
    "Q40": {'description': 'Phred quality 40 (0.01% error probability)', 'annotations': {'phred_score': '40', 'error_probability': '0.0001', 'ascii_char': 'I'}},
    "Q50": {'description': 'Phred quality 50 (0.001% error probability)', 'annotations': {'phred_score': '50', 'error_probability': '0.00001', 'ascii_char': 'S'}},
    "Q60": {'description': 'Phred quality 60 (0.0001% error probability)', 'annotations': {'phred_score': '60', 'error_probability': '0.000001', 'ascii_char': ']'}},
}

class IUPACNucleotideCode(RichEnum):
    """
    Complete IUPAC nucleotide codes including ambiguous bases for DNA/RNA sequences.
Used in FASTA and other sequence formats to represent uncertain nucleotides.
    """
    # Enum members
    A = "A"
    T = "T"
    U = "U"
    G = "G"
    C = "C"
    R = "R"
    Y = "Y"
    S = "S"
    W = "W"
    K = "K"
    M = "M"
    B = "B"
    D = "D"
    H = "H"
    V = "V"
    N = "N"
    GAP = "GAP"

# Set metadata after class creation to avoid it becoming an enum member
IUPACNucleotideCode._metadata = {
    "A": {'description': 'Adenine'},
    "T": {'description': 'Thymine (DNA)'},
    "U": {'description': 'Uracil (RNA)'},
    "G": {'description': 'Guanine'},
    "C": {'description': 'Cytosine'},
    "R": {'description': 'Purine (A or G)'},
    "Y": {'description': 'Pyrimidine (C or T/U)'},
    "S": {'description': 'Strong interaction (G or C)'},
    "W": {'description': 'Weak interaction (A or T/U)'},
    "K": {'description': 'Keto (G or T/U)'},
    "M": {'description': 'Amino (A or C)'},
    "B": {'description': 'Not A (C or G or T/U)'},
    "D": {'description': 'Not C (A or G or T/U)'},
    "H": {'description': 'Not G (A or C or T/U)'},
    "V": {'description': 'Not T/U (A or C or G)'},
    "N": {'description': 'Any nucleotide (A or C or G or T/U)'},
    "GAP": {'description': 'Gap or deletion in alignment'},
}

class StandardAminoAcid(RichEnum):
    """
    The 20 standard proteinogenic amino acids with IUPAC single-letter codes
    """
    # Enum members
    A = "A"
    R = "R"
    N = "N"
    D = "D"
    C = "C"
    E = "E"
    Q = "Q"
    G = "G"
    H = "H"
    I = "I"
    L = "L"
    K = "K"
    M = "M"
    F = "F"
    P = "P"
    S = "S"
    T = "T"
    W = "W"
    Y = "Y"
    V = "V"

# Set metadata after class creation to avoid it becoming an enum member
StandardAminoAcid._metadata = {
    "A": {'description': 'Alanine'},
    "R": {'description': 'Arginine'},
    "N": {'description': 'Asparagine'},
    "D": {'description': 'Aspartic acid'},
    "C": {'description': 'Cysteine'},
    "E": {'description': 'Glutamic acid'},
    "Q": {'description': 'Glutamine'},
    "G": {'description': 'Glycine'},
    "H": {'description': 'Histidine'},
    "I": {'description': 'Isoleucine'},
    "L": {'description': 'Leucine'},
    "K": {'description': 'Lysine'},
    "M": {'description': 'Methionine'},
    "F": {'description': 'Phenylalanine'},
    "P": {'description': 'Proline'},
    "S": {'description': 'Serine'},
    "T": {'description': 'Threonine'},
    "W": {'description': 'Tryptophan'},
    "Y": {'description': 'Tyrosine'},
    "V": {'description': 'Valine'},
}

class IUPACAminoAcidCode(RichEnum):
    """
    Complete IUPAC amino acid codes including standard amino acids,
rare amino acids, and ambiguity codes
    """
    # Enum members
    A = "A"
    R = "R"
    N = "N"
    D = "D"
    C = "C"
    E = "E"
    Q = "Q"
    G = "G"
    H = "H"
    I = "I"
    L = "L"
    K = "K"
    M = "M"
    F = "F"
    P = "P"
    S = "S"
    T = "T"
    W = "W"
    Y = "Y"
    V = "V"
    U = "U"
    O = "O"
    B = "B"
    Z = "Z"
    J = "J"
    X = "X"
    STOP = "STOP"
    GAP = "GAP"

# Set metadata after class creation to avoid it becoming an enum member
IUPACAminoAcidCode._metadata = {
    "A": {'description': 'Alanine'},
    "R": {'description': 'Arginine'},
    "N": {'description': 'Asparagine'},
    "D": {'description': 'Aspartic acid'},
    "C": {'description': 'Cysteine'},
    "E": {'description': 'Glutamic acid'},
    "Q": {'description': 'Glutamine'},
    "G": {'description': 'Glycine'},
    "H": {'description': 'Histidine'},
    "I": {'description': 'Isoleucine'},
    "L": {'description': 'Leucine'},
    "K": {'description': 'Lysine'},
    "M": {'description': 'Methionine'},
    "F": {'description': 'Phenylalanine'},
    "P": {'description': 'Proline'},
    "S": {'description': 'Serine'},
    "T": {'description': 'Threonine'},
    "W": {'description': 'Tryptophan'},
    "Y": {'description': 'Tyrosine'},
    "V": {'description': 'Valine'},
    "U": {'description': 'Selenocysteine (21st amino acid)', 'aliases': ['Sec']},
    "O": {'description': 'Pyrrolysine (22nd amino acid)', 'aliases': ['Pyl']},
    "B": {'description': 'Asparagine or Aspartic acid (N or D)'},
    "Z": {'description': 'Glutamine or Glutamic acid (Q or E)'},
    "J": {'description': 'Leucine or Isoleucine (L or I)'},
    "X": {'description': 'Any amino acid'},
    "STOP": {'description': 'Translation stop codon'},
    "GAP": {'description': 'Gap or deletion in alignment'},
}

class SequenceAlphabet(RichEnum):
    """
    Types of sequence alphabets used in bioinformatics
    """
    # Enum members
    DNA = "DNA"
    RNA = "RNA"
    PROTEIN = "PROTEIN"
    IUPAC_DNA = "IUPAC_DNA"
    IUPAC_RNA = "IUPAC_RNA"
    IUPAC_PROTEIN = "IUPAC_PROTEIN"
    RESTRICTED_DNA = "RESTRICTED_DNA"
    RESTRICTED_RNA = "RESTRICTED_RNA"
    BINARY = "BINARY"

# Set metadata after class creation to avoid it becoming an enum member
SequenceAlphabet._metadata = {
    "DNA": {'description': 'Deoxyribonucleic acid alphabet (A, T, G, C)'},
    "RNA": {'description': 'Ribonucleic acid alphabet (A, U, G, C)'},
    "PROTEIN": {'description': 'Protein/amino acid alphabet (20 standard AAs)'},
    "IUPAC_DNA": {'description': 'Extended DNA with IUPAC ambiguity codes'},
    "IUPAC_RNA": {'description': 'Extended RNA with IUPAC ambiguity codes'},
    "IUPAC_PROTEIN": {'description': 'Extended protein with ambiguity codes and rare AAs'},
    "RESTRICTED_DNA": {'description': 'Unambiguous DNA bases only (A, T, G, C)'},
    "RESTRICTED_RNA": {'description': 'Unambiguous RNA bases only (A, U, G, C)'},
    "BINARY": {'description': 'Binary encoding of sequences'},
}

class SequenceQualityEncoding(RichEnum):
    """
    Quality score encoding standards used in FASTQ files and sequencing data.
Different platforms and software versions use different ASCII offsets.
    """
    # Enum members
    SANGER = "SANGER"
    SOLEXA = "SOLEXA"
    ILLUMINA_1_3 = "ILLUMINA_1_3"
    ILLUMINA_1_5 = "ILLUMINA_1_5"
    ILLUMINA_1_8 = "ILLUMINA_1_8"

# Set metadata after class creation to avoid it becoming an enum member
SequenceQualityEncoding._metadata = {
    "SANGER": {'description': 'Sanger/Phred+33 (PHRED scores, ASCII offset 33)', 'annotations': {'ascii_offset': 33, 'score_range': '0-93', 'platforms': 'NCBI SRA, Illumina 1.8+'}},
    "SOLEXA": {'description': 'Solexa+64 (Solexa scores, ASCII offset 64)', 'annotations': {'ascii_offset': 64, 'score_range': '-5-62', 'platforms': 'Early Solexa/Illumina'}},
    "ILLUMINA_1_3": {'description': 'Illumina 1.3+ (PHRED+64, ASCII offset 64)', 'annotations': {'ascii_offset': 64, 'score_range': '0-62', 'platforms': 'Illumina 1.3-1.7'}},
    "ILLUMINA_1_5": {'description': 'Illumina 1.5+ (PHRED+64, special handling for 0-2)', 'annotations': {'ascii_offset': 64, 'score_range': '3-62', 'platforms': 'Illumina 1.5-1.7'}},
    "ILLUMINA_1_8": {'description': 'Illumina 1.8+ (PHRED+33, modern standard)', 'annotations': {'ascii_offset': 33, 'score_range': '0-41', 'platforms': 'Illumina 1.8+, modern sequencers'}},
}

class GeneticCodeTable(RichEnum):
    """
    NCBI genetic code translation tables for different organisms.
Table 1 is the universal genetic code used by most organisms.
    """
    # Enum members
    TABLE_1 = "TABLE_1"
    TABLE_2 = "TABLE_2"
    TABLE_3 = "TABLE_3"
    TABLE_4 = "TABLE_4"
    TABLE_5 = "TABLE_5"
    TABLE_6 = "TABLE_6"
    TABLE_9 = "TABLE_9"
    TABLE_10 = "TABLE_10"
    TABLE_11 = "TABLE_11"
    TABLE_12 = "TABLE_12"
    TABLE_13 = "TABLE_13"
    TABLE_14 = "TABLE_14"
    TABLE_16 = "TABLE_16"
    TABLE_21 = "TABLE_21"
    TABLE_22 = "TABLE_22"
    TABLE_23 = "TABLE_23"
    TABLE_24 = "TABLE_24"
    TABLE_25 = "TABLE_25"
    TABLE_26 = "TABLE_26"
    TABLE_27 = "TABLE_27"
    TABLE_28 = "TABLE_28"
    TABLE_29 = "TABLE_29"
    TABLE_30 = "TABLE_30"
    TABLE_31 = "TABLE_31"

# Set metadata after class creation to avoid it becoming an enum member
GeneticCodeTable._metadata = {
    "TABLE_1": {'description': 'Standard genetic code (universal)', 'annotations': {'ncbi_id': 1, 'name': 'Standard'}},
    "TABLE_2": {'description': 'Vertebrate mitochondrial code', 'annotations': {'ncbi_id': 2, 'name': 'Vertebrate Mitochondrial'}},
    "TABLE_3": {'description': 'Yeast mitochondrial code', 'annotations': {'ncbi_id': 3, 'name': 'Yeast Mitochondrial'}},
    "TABLE_4": {'description': 'Mold, protozoan, coelenterate mitochondrial', 'annotations': {'ncbi_id': 4, 'name': 'Mold Mitochondrial'}},
    "TABLE_5": {'description': 'Invertebrate mitochondrial code', 'annotations': {'ncbi_id': 5, 'name': 'Invertebrate Mitochondrial'}},
    "TABLE_6": {'description': 'Ciliate, dasycladacean, hexamita nuclear code', 'annotations': {'ncbi_id': 6, 'name': 'Ciliate Nuclear'}},
    "TABLE_9": {'description': 'Echinoderm and flatworm mitochondrial code', 'annotations': {'ncbi_id': 9, 'name': 'Echinoderm Mitochondrial'}},
    "TABLE_10": {'description': 'Euplotid nuclear code', 'annotations': {'ncbi_id': 10, 'name': 'Euplotid Nuclear'}},
    "TABLE_11": {'description': 'Bacterial, archaeal and plant plastid code', 'annotations': {'ncbi_id': 11, 'name': 'Bacterial'}},
    "TABLE_12": {'description': 'Alternative yeast nuclear code', 'annotations': {'ncbi_id': 12, 'name': 'Alternative Yeast Nuclear'}},
    "TABLE_13": {'description': 'Ascidian mitochondrial code', 'annotations': {'ncbi_id': 13, 'name': 'Ascidian Mitochondrial'}},
    "TABLE_14": {'description': 'Alternative flatworm mitochondrial code', 'annotations': {'ncbi_id': 14, 'name': 'Alternative Flatworm Mitochondrial'}},
    "TABLE_16": {'description': 'Chlorophycean mitochondrial code', 'annotations': {'ncbi_id': 16, 'name': 'Chlorophycean Mitochondrial'}},
    "TABLE_21": {'description': 'Trematode mitochondrial code', 'annotations': {'ncbi_id': 21, 'name': 'Trematode Mitochondrial'}},
    "TABLE_22": {'description': 'Scenedesmus obliquus mitochondrial code', 'annotations': {'ncbi_id': 22, 'name': 'Scenedesmus Mitochondrial'}},
    "TABLE_23": {'description': 'Thraustochytrium mitochondrial code', 'annotations': {'ncbi_id': 23, 'name': 'Thraustochytrium Mitochondrial'}},
    "TABLE_24": {'description': 'Rhabdopleuridae mitochondrial code', 'annotations': {'ncbi_id': 24, 'name': 'Rhabdopleuridae Mitochondrial'}},
    "TABLE_25": {'description': 'Candidate division SR1 and gracilibacteria code', 'annotations': {'ncbi_id': 25, 'name': 'Candidate Division SR1'}},
    "TABLE_26": {'description': 'Pachysolen tannophilus nuclear code', 'annotations': {'ncbi_id': 26, 'name': 'Pachysolen Nuclear'}},
    "TABLE_27": {'description': 'Karyorelict nuclear code', 'annotations': {'ncbi_id': 27, 'name': 'Karyorelict Nuclear'}},
    "TABLE_28": {'description': 'Condylostoma nuclear code', 'annotations': {'ncbi_id': 28, 'name': 'Condylostoma Nuclear'}},
    "TABLE_29": {'description': 'Mesodinium nuclear code', 'annotations': {'ncbi_id': 29, 'name': 'Mesodinium Nuclear'}},
    "TABLE_30": {'description': 'Peritrich nuclear code', 'annotations': {'ncbi_id': 30, 'name': 'Peritrich Nuclear'}},
    "TABLE_31": {'description': 'Blastocrithidia nuclear code', 'annotations': {'ncbi_id': 31, 'name': 'Blastocrithidia Nuclear'}},
}

class SequenceStrand(RichEnum):
    """
    Strand orientation for nucleic acid sequences
    """
    # Enum members
    PLUS = "PLUS"
    MINUS = "MINUS"
    BOTH = "BOTH"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
SequenceStrand._metadata = {
    "PLUS": {'description': "Plus/forward/sense strand (5' to 3')"},
    "MINUS": {'description': "Minus/reverse/antisense strand (3' to 5')"},
    "BOTH": {'description': 'Both strands'},
    "UNKNOWN": {'description': 'Strand not specified or unknown'},
}

class SequenceTopology(RichEnum):
    """
    Topological structure of nucleic acid molecules
    """
    # Enum members
    LINEAR = "LINEAR"
    CIRCULAR = "CIRCULAR"
    BRANCHED = "BRANCHED"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
SequenceTopology._metadata = {
    "LINEAR": {'description': 'Linear sequence molecule', 'meaning': 'SO:0000987'},
    "CIRCULAR": {'description': 'Circular sequence molecule', 'meaning': 'SO:0000988'},
    "BRANCHED": {'description': 'Branched sequence structure'},
    "UNKNOWN": {'description': 'Topology not specified'},
}

class SequenceModality(RichEnum):
    """
    Types of sequence data based on experimental method
    """
    # Enum members
    SINGLE_CELL = "SINGLE_CELL"
    BULK = "BULK"
    SPATIAL = "SPATIAL"
    LONG_READ = "LONG_READ"
    SHORT_READ = "SHORT_READ"
    PAIRED_END = "PAIRED_END"
    SINGLE_END = "SINGLE_END"
    MATE_PAIR = "MATE_PAIR"

# Set metadata after class creation to avoid it becoming an enum member
SequenceModality._metadata = {
    "SINGLE_CELL": {'description': 'Single-cell sequencing data'},
    "BULK": {'description': 'Bulk/population sequencing data'},
    "SPATIAL": {'description': 'Spatially-resolved sequencing'},
    "LONG_READ": {'description': 'Long-read sequencing (PacBio, Oxford Nanopore)'},
    "SHORT_READ": {'description': 'Short-read sequencing (Illumina)'},
    "PAIRED_END": {'description': 'Paired-end sequencing reads'},
    "SINGLE_END": {'description': 'Single-end sequencing reads'},
    "MATE_PAIR": {'description': 'Mate-pair sequencing libraries'},
}

class SequencingPlatform(RichEnum):
    """
    Major DNA/RNA sequencing platforms and instruments used in genomics research
    """
    # Enum members
    ILLUMINA_HISEQ_2000 = "ILLUMINA_HISEQ_2000"
    ILLUMINA_HISEQ_2500 = "ILLUMINA_HISEQ_2500"
    ILLUMINA_HISEQ_3000 = "ILLUMINA_HISEQ_3000"
    ILLUMINA_HISEQ_4000 = "ILLUMINA_HISEQ_4000"
    ILLUMINA_HISEQ_X = "ILLUMINA_HISEQ_X"
    ILLUMINA_NOVASEQ_6000 = "ILLUMINA_NOVASEQ_6000"
    ILLUMINA_NEXTSEQ_500 = "ILLUMINA_NEXTSEQ_500"
    ILLUMINA_NEXTSEQ_550 = "ILLUMINA_NEXTSEQ_550"
    ILLUMINA_NEXTSEQ_1000 = "ILLUMINA_NEXTSEQ_1000"
    ILLUMINA_NEXTSEQ_2000 = "ILLUMINA_NEXTSEQ_2000"
    ILLUMINA_MISEQ = "ILLUMINA_MISEQ"
    ILLUMINA_ISEQ_100 = "ILLUMINA_ISEQ_100"
    PACBIO_RS = "PACBIO_RS"
    PACBIO_RS_II = "PACBIO_RS_II"
    PACBIO_SEQUEL = "PACBIO_SEQUEL"
    PACBIO_SEQUEL_II = "PACBIO_SEQUEL_II"
    PACBIO_REVIO = "PACBIO_REVIO"
    NANOPORE_MINION = "NANOPORE_MINION"
    NANOPORE_GRIDION = "NANOPORE_GRIDION"
    NANOPORE_PROMETHION = "NANOPORE_PROMETHION"
    NANOPORE_FLONGLE = "NANOPORE_FLONGLE"
    ELEMENT_AVITI = "ELEMENT_AVITI"
    MGI_DNBSEQ_T7 = "MGI_DNBSEQ_T7"
    MGI_DNBSEQ_G400 = "MGI_DNBSEQ_G400"
    MGI_DNBSEQ_G50 = "MGI_DNBSEQ_G50"
    SANGER_SEQUENCING = "SANGER_SEQUENCING"
    ROCHE_454_GS = "ROCHE_454_GS"
    LIFE_TECHNOLOGIES_ION_TORRENT = "LIFE_TECHNOLOGIES_ION_TORRENT"
    ABI_SOLID = "ABI_SOLID"

# Set metadata after class creation to avoid it becoming an enum member
SequencingPlatform._metadata = {
    "ILLUMINA_HISEQ_2000": {'description': 'Illumina HiSeq 2000', 'meaning': 'OBI:0002001', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_HISEQ_2500": {'description': 'Illumina HiSeq 2500', 'meaning': 'OBI:0002002', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_HISEQ_3000": {'description': 'Illumina HiSeq 3000', 'meaning': 'OBI:0002048', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_HISEQ_4000": {'description': 'Illumina HiSeq 4000', 'meaning': 'OBI:0002049', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_HISEQ_X": {'description': 'Illumina HiSeq X', 'meaning': 'OBI:0002129', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}, 'aliases': ['Illumina HiSeq X Ten']},
    "ILLUMINA_NOVASEQ_6000": {'description': 'Illumina NovaSeq 6000', 'meaning': 'OBI:0002630', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_NEXTSEQ_500": {'description': 'Illumina NextSeq 500', 'meaning': 'OBI:0002021', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_NEXTSEQ_550": {'description': 'Illumina NextSeq 550', 'meaning': 'OBI:0003387', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_NEXTSEQ_1000": {'description': 'Illumina NextSeq 1000', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_NEXTSEQ_2000": {'description': 'Illumina NextSeq 2000', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_MISEQ": {'description': 'Illumina MiSeq', 'meaning': 'OBI:0002003', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "ILLUMINA_ISEQ_100": {'description': 'Illumina iSeq 100', 'annotations': {'manufacturer': 'Illumina', 'read_type': 'short', 'chemistry': 'sequencing by synthesis'}},
    "PACBIO_RS": {'description': 'PacBio RS', 'annotations': {'manufacturer': 'Pacific Biosciences', 'read_type': 'long', 'chemistry': 'single molecule real time'}},
    "PACBIO_RS_II": {'description': 'PacBio RS II', 'meaning': 'OBI:0002012', 'annotations': {'manufacturer': 'Pacific Biosciences', 'read_type': 'long', 'chemistry': 'single molecule real time'}},
    "PACBIO_SEQUEL": {'description': 'PacBio Sequel', 'meaning': 'OBI:0002632', 'annotations': {'manufacturer': 'Pacific Biosciences', 'read_type': 'long', 'chemistry': 'single molecule real time'}},
    "PACBIO_SEQUEL_II": {'description': 'PacBio Sequel II', 'meaning': 'OBI:0002633', 'annotations': {'manufacturer': 'Pacific Biosciences', 'read_type': 'long', 'chemistry': 'single molecule real time'}},
    "PACBIO_REVIO": {'description': 'PacBio Revio', 'annotations': {'manufacturer': 'Pacific Biosciences', 'read_type': 'long', 'chemistry': 'single molecule real time'}},
    "NANOPORE_MINION": {'description': 'Oxford Nanopore MinION', 'meaning': 'OBI:0002750', 'annotations': {'manufacturer': 'Oxford Nanopore Technologies', 'read_type': 'long', 'chemistry': 'nanopore sequencing'}, 'aliases': ['Oxford Nanopore MinION']},
    "NANOPORE_GRIDION": {'description': 'Oxford Nanopore GridION', 'meaning': 'OBI:0002751', 'annotations': {'manufacturer': 'Oxford Nanopore Technologies', 'read_type': 'long', 'chemistry': 'nanopore sequencing'}, 'aliases': ['Oxford Nanopore GridION Mk1']},
    "NANOPORE_PROMETHION": {'description': 'Oxford Nanopore PromethION', 'meaning': 'OBI:0002752', 'annotations': {'manufacturer': 'Oxford Nanopore Technologies', 'read_type': 'long', 'chemistry': 'nanopore sequencing'}, 'aliases': ['Oxford Nanopore PromethION']},
    "NANOPORE_FLONGLE": {'description': 'Oxford Nanopore Flongle', 'annotations': {'manufacturer': 'Oxford Nanopore Technologies', 'read_type': 'long', 'chemistry': 'nanopore sequencing'}},
    "ELEMENT_AVITI": {'description': 'Element Biosciences AVITI', 'annotations': {'manufacturer': 'Element Biosciences', 'read_type': 'short', 'chemistry': 'sequencing by avidity'}},
    "MGI_DNBSEQ_T7": {'description': 'MGI DNBSEQ-T7', 'annotations': {'manufacturer': 'MGI/BGI', 'read_type': 'short', 'chemistry': 'DNA nanoball sequencing'}},
    "MGI_DNBSEQ_G400": {'description': 'MGI DNBSEQ-G400', 'annotations': {'manufacturer': 'MGI/BGI', 'read_type': 'short', 'chemistry': 'DNA nanoball sequencing'}},
    "MGI_DNBSEQ_G50": {'description': 'MGI DNBSEQ-G50', 'annotations': {'manufacturer': 'MGI/BGI', 'read_type': 'short', 'chemistry': 'DNA nanoball sequencing'}},
    "SANGER_SEQUENCING": {'description': 'Sanger chain termination sequencing', 'meaning': 'OBI:0000695', 'annotations': {'manufacturer': 'Various', 'read_type': 'short', 'chemistry': 'chain termination'}, 'aliases': ['chain termination sequencing assay']},
    "ROCHE_454_GS": {'description': 'Roche 454 Genome Sequencer', 'meaning': 'OBI:0000702', 'annotations': {'manufacturer': 'Roche/454', 'read_type': 'short', 'chemistry': 'pyrosequencing', 'status': 'discontinued'}, 'aliases': ['454 Genome Sequencer FLX']},
    "LIFE_TECHNOLOGIES_ION_TORRENT": {'description': 'Life Technologies Ion Torrent', 'annotations': {'manufacturer': 'Life Technologies/Thermo Fisher', 'read_type': 'short', 'chemistry': 'semiconductor sequencing'}},
    "ABI_SOLID": {'description': 'ABI SOLiD', 'annotations': {'manufacturer': 'Life Technologies/Applied Biosystems', 'read_type': 'short', 'chemistry': 'sequencing by ligation', 'status': 'discontinued'}},
}

class SequencingChemistry(RichEnum):
    """
    Fundamental chemical methods used for DNA/RNA sequencing
    """
    # Enum members
    SEQUENCING_BY_SYNTHESIS = "SEQUENCING_BY_SYNTHESIS"
    SINGLE_MOLECULE_REAL_TIME = "SINGLE_MOLECULE_REAL_TIME"
    NANOPORE_SEQUENCING = "NANOPORE_SEQUENCING"
    PYROSEQUENCING = "PYROSEQUENCING"
    SEQUENCING_BY_LIGATION = "SEQUENCING_BY_LIGATION"
    CHAIN_TERMINATION = "CHAIN_TERMINATION"
    SEMICONDUCTOR_SEQUENCING = "SEMICONDUCTOR_SEQUENCING"
    DNA_NANOBALL_SEQUENCING = "DNA_NANOBALL_SEQUENCING"
    SEQUENCING_BY_AVIDITY = "SEQUENCING_BY_AVIDITY"

# Set metadata after class creation to avoid it becoming an enum member
SequencingChemistry._metadata = {
    "SEQUENCING_BY_SYNTHESIS": {'description': 'Sequencing by synthesis (Illumina)', 'meaning': 'OBI:0000734', 'aliases': ['DNA sequencing by synthesis assay']},
    "SINGLE_MOLECULE_REAL_TIME": {'description': 'Single molecule real-time sequencing (PacBio)'},
    "NANOPORE_SEQUENCING": {'description': 'Nanopore sequencing (Oxford Nanopore)'},
    "PYROSEQUENCING": {'description': 'Pyrosequencing (454)'},
    "SEQUENCING_BY_LIGATION": {'description': 'Sequencing by ligation (SOLiD)', 'meaning': 'OBI:0000723', 'aliases': ['DNA sequencing by ligation assay']},
    "CHAIN_TERMINATION": {'description': 'Chain termination method (Sanger)', 'meaning': 'OBI:0000695', 'aliases': ['chain termination sequencing assay']},
    "SEMICONDUCTOR_SEQUENCING": {'description': 'Semiconductor/Ion semiconductor sequencing'},
    "DNA_NANOBALL_SEQUENCING": {'description': 'DNA nanoball sequencing (MGI/BGI)'},
    "SEQUENCING_BY_AVIDITY": {'description': 'Sequencing by avidity (Element Biosciences)'},
}

class LibraryPreparation(RichEnum):
    """
    Methods for preparing sequencing libraries from nucleic acid samples
    """
    # Enum members
    GENOMIC_DNA = "GENOMIC_DNA"
    WHOLE_GENOME_AMPLIFICATION = "WHOLE_GENOME_AMPLIFICATION"
    PCR_AMPLICON = "PCR_AMPLICON"
    RNA_SEQ = "RNA_SEQ"
    SMALL_RNA_SEQ = "SMALL_RNA_SEQ"
    SINGLE_CELL_RNA_SEQ = "SINGLE_CELL_RNA_SEQ"
    ATAC_SEQ = "ATAC_SEQ"
    CHIP_SEQ = "CHIP_SEQ"
    BISULFITE_SEQ = "BISULFITE_SEQ"
    HI_C = "HI_C"
    CUT_AND_RUN = "CUT_AND_RUN"
    CUT_AND_TAG = "CUT_AND_TAG"
    CAPTURE_SEQUENCING = "CAPTURE_SEQUENCING"
    EXOME_SEQUENCING = "EXOME_SEQUENCING"
    METAGENOMICS = "METAGENOMICS"
    AMPLICON_SEQUENCING = "AMPLICON_SEQUENCING"
    DIRECT_RNA = "DIRECT_RNA"
    CDNA_SEQUENCING = "CDNA_SEQUENCING"
    RIBOSOME_PROFILING = "RIBOSOME_PROFILING"

# Set metadata after class creation to avoid it becoming an enum member
LibraryPreparation._metadata = {
    "GENOMIC_DNA": {'description': 'Genomic DNA library preparation'},
    "WHOLE_GENOME_AMPLIFICATION": {'description': 'Whole genome amplification (WGA)'},
    "PCR_AMPLICON": {'description': 'PCR amplicon sequencing'},
    "RNA_SEQ": {'description': 'RNA sequencing library prep'},
    "SMALL_RNA_SEQ": {'description': 'Small RNA sequencing'},
    "SINGLE_CELL_RNA_SEQ": {'description': 'Single-cell RNA sequencing'},
    "ATAC_SEQ": {'description': 'ATAC-seq (chromatin accessibility)'},
    "CHIP_SEQ": {'description': 'ChIP-seq (chromatin immunoprecipitation)'},
    "BISULFITE_SEQ": {'description': 'Bisulfite sequencing (methylation)'},
    "HI_C": {'description': 'Hi-C (chromosome conformation capture)'},
    "CUT_AND_RUN": {'description': 'CUT&RUN (chromatin profiling)'},
    "CUT_AND_TAG": {'description': 'CUT&Tag (chromatin profiling)'},
    "CAPTURE_SEQUENCING": {'description': 'Target capture/enrichment sequencing'},
    "EXOME_SEQUENCING": {'description': 'Whole exome sequencing'},
    "METAGENOMICS": {'description': 'Metagenomic sequencing'},
    "AMPLICON_SEQUENCING": {'description': '16S/ITS amplicon sequencing'},
    "DIRECT_RNA": {'description': 'Direct RNA sequencing (nanopore)'},
    "CDNA_SEQUENCING": {'description': 'cDNA sequencing'},
    "RIBOSOME_PROFILING": {'description': 'Ribosome profiling (Ribo-seq)'},
}

class SequencingApplication(RichEnum):
    """
    Primary applications or assays using DNA/RNA sequencing
    """
    # Enum members
    WHOLE_GENOME_SEQUENCING = "WHOLE_GENOME_SEQUENCING"
    WHOLE_EXOME_SEQUENCING = "WHOLE_EXOME_SEQUENCING"
    TRANSCRIPTOME_SEQUENCING = "TRANSCRIPTOME_SEQUENCING"
    TARGETED_SEQUENCING = "TARGETED_SEQUENCING"
    EPIGENOMICS = "EPIGENOMICS"
    METAGENOMICS = "METAGENOMICS"
    SINGLE_CELL_GENOMICS = "SINGLE_CELL_GENOMICS"
    SINGLE_CELL_TRANSCRIPTOMICS = "SINGLE_CELL_TRANSCRIPTOMICS"
    CHROMATIN_IMMUNOPRECIPITATION = "CHROMATIN_IMMUNOPRECIPITATION"
    CHROMATIN_ACCESSIBILITY = "CHROMATIN_ACCESSIBILITY"
    DNA_METHYLATION = "DNA_METHYLATION"
    CHROMOSOME_CONFORMATION = "CHROMOSOME_CONFORMATION"
    VARIANT_CALLING = "VARIANT_CALLING"
    PHARMACOGENOMICS = "PHARMACOGENOMICS"
    CLINICAL_DIAGNOSTICS = "CLINICAL_DIAGNOSTICS"
    POPULATION_GENOMICS = "POPULATION_GENOMICS"

# Set metadata after class creation to avoid it becoming an enum member
SequencingApplication._metadata = {
    "WHOLE_GENOME_SEQUENCING": {'description': 'Whole genome sequencing (WGS)', 'meaning': 'EDAM:topic_3673'},
    "WHOLE_EXOME_SEQUENCING": {'description': 'Whole exome sequencing (WES)', 'meaning': 'EDAM:topic_3676', 'aliases': ['Exome sequencing']},
    "TRANSCRIPTOME_SEQUENCING": {'description': 'RNA sequencing (RNA-seq)', 'meaning': 'EDAM:topic_3170', 'aliases': ['RNA-Seq']},
    "TARGETED_SEQUENCING": {'description': 'Targeted gene panel sequencing'},
    "EPIGENOMICS": {'description': 'Epigenomic profiling'},
    "METAGENOMICS": {'description': 'Metagenomic sequencing', 'meaning': 'EDAM:topic_3837', 'aliases': ['Metagenomic sequencing']},
    "SINGLE_CELL_GENOMICS": {'description': 'Single-cell genomics'},
    "SINGLE_CELL_TRANSCRIPTOMICS": {'description': 'Single-cell transcriptomics', 'meaning': 'EDAM:topic_4028', 'aliases': ['Single-cell sequencing']},
    "CHROMATIN_IMMUNOPRECIPITATION": {'description': 'ChIP-seq', 'meaning': 'EDAM:topic_3656', 'aliases': ['Immunoprecipitation experiment']},
    "CHROMATIN_ACCESSIBILITY": {'description': 'ATAC-seq/FAIRE-seq'},
    "DNA_METHYLATION": {'description': 'Bisulfite/methylation sequencing'},
    "CHROMOSOME_CONFORMATION": {'description': 'Hi-C/3C-seq'},
    "VARIANT_CALLING": {'description': 'Genetic variant discovery'},
    "PHARMACOGENOMICS": {'description': 'Pharmacogenomic sequencing'},
    "CLINICAL_DIAGNOSTICS": {'description': 'Clinical diagnostic sequencing'},
    "POPULATION_GENOMICS": {'description': 'Population-scale genomics'},
}

class ReadType(RichEnum):
    """
    Configuration of sequencing reads generated by different platforms
    """
    # Enum members
    SINGLE_END = "SINGLE_END"
    PAIRED_END = "PAIRED_END"
    MATE_PAIR = "MATE_PAIR"
    LONG_READ = "LONG_READ"
    ULTRA_LONG_READ = "ULTRA_LONG_READ"
    CONTINUOUS_LONG_READ = "CONTINUOUS_LONG_READ"

# Set metadata after class creation to avoid it becoming an enum member
ReadType._metadata = {
    "SINGLE_END": {'description': 'Single-end reads'},
    "PAIRED_END": {'description': 'Paired-end reads'},
    "MATE_PAIR": {'description': 'Mate-pair reads (large insert)'},
    "LONG_READ": {'description': 'Long reads (>1kb typical)'},
    "ULTRA_LONG_READ": {'description': 'Ultra-long reads (>10kb)'},
    "CONTINUOUS_LONG_READ": {'description': 'Continuous long reads (nanopore)'},
}

class SequenceFileFormat(RichEnum):
    """
    Standard file formats used for storing sequence data
    """
    # Enum members
    FASTA = "FASTA"
    FASTQ = "FASTQ"
    SAM = "SAM"
    BAM = "BAM"
    CRAM = "CRAM"
    VCF = "VCF"
    BCF = "BCF"
    GFF3 = "GFF3"
    GTF = "GTF"
    BED = "BED"
    BIGWIG = "BIGWIG"
    BIGBED = "BIGBED"
    HDF5 = "HDF5"
    SFF = "SFF"
    FAST5 = "FAST5"
    POD5 = "POD5"

# Set metadata after class creation to avoid it becoming an enum member
SequenceFileFormat._metadata = {
    "FASTA": {'description': 'FASTA sequence format', 'meaning': 'EDAM:format_1929', 'annotations': {'extensions': '.fa, .fasta, .fna, .ffn, .faa, .frn', 'content': 'sequences only'}},
    "FASTQ": {'description': 'FASTQ sequence with quality format', 'meaning': 'EDAM:format_1930', 'annotations': {'extensions': '.fq, .fastq', 'content': 'sequences and quality scores'}},
    "SAM": {'description': 'Sequence Alignment Map format', 'meaning': 'EDAM:format_2573', 'annotations': {'extensions': '.sam', 'content': 'aligned sequences (text)'}},
    "BAM": {'description': 'Binary Alignment Map format', 'meaning': 'EDAM:format_2572', 'annotations': {'extensions': '.bam', 'content': 'aligned sequences (binary)'}},
    "CRAM": {'description': 'Compressed Reference-oriented Alignment Map', 'annotations': {'extensions': '.cram', 'content': 'compressed aligned sequences'}},
    "VCF": {'description': 'Variant Call Format', 'meaning': 'EDAM:format_3016', 'annotations': {'extensions': '.vcf', 'content': 'genetic variants'}},
    "BCF": {'description': 'Binary Variant Call Format', 'meaning': 'EDAM:format_3020', 'annotations': {'extensions': '.bcf', 'content': 'genetic variants (binary)'}},
    "GFF3": {'description': 'Generic Feature Format version 3', 'annotations': {'extensions': '.gff, .gff3', 'content': 'genomic annotations'}},
    "GTF": {'description': 'Gene Transfer Format', 'annotations': {'extensions': '.gtf', 'content': 'gene annotations'}},
    "BED": {'description': 'Browser Extensible Data format', 'annotations': {'extensions': '.bed', 'content': 'genomic intervals'}},
    "BIGWIG": {'description': 'BigWig format for continuous data', 'annotations': {'extensions': '.bw, .bigwig', 'content': 'continuous genomic data'}},
    "BIGBED": {'description': 'BigBed format for interval data', 'annotations': {'extensions': '.bb, .bigbed', 'content': 'genomic intervals (indexed)'}},
    "HDF5": {'description': 'Hierarchical Data Format 5', 'annotations': {'extensions': '.h5, .hdf5', 'content': 'multi-dimensional arrays'}},
    "SFF": {'description': 'Standard Flowgram Format (454)', 'meaning': 'EDAM:format_3284', 'annotations': {'extensions': '.sff', 'content': '454 sequencing data', 'status': 'legacy'}},
    "FAST5": {'description': 'Fast5 format (Oxford Nanopore)', 'annotations': {'extensions': '.fast5', 'content': 'nanopore raw signal data'}},
    "POD5": {'description': 'POD5 format (Oxford Nanopore, newer)', 'annotations': {'extensions': '.pod5', 'content': 'nanopore raw signal data (compressed)'}},
}

class DataProcessingLevel(RichEnum):
    """
    Levels of processing applied to raw sequencing data
    """
    # Enum members
    RAW = "RAW"
    QUALITY_FILTERED = "QUALITY_FILTERED"
    TRIMMED = "TRIMMED"
    ALIGNED = "ALIGNED"
    DEDUPLICATED = "DEDUPLICATED"
    RECALIBRATED = "RECALIBRATED"
    VARIANT_CALLED = "VARIANT_CALLED"
    NORMALIZED = "NORMALIZED"
    ASSEMBLED = "ASSEMBLED"
    ANNOTATED = "ANNOTATED"

# Set metadata after class creation to avoid it becoming an enum member
DataProcessingLevel._metadata = {
    "RAW": {'description': 'Raw unprocessed sequencing reads'},
    "QUALITY_FILTERED": {'description': 'Quality filtered reads'},
    "TRIMMED": {'description': 'Adapter/quality trimmed reads'},
    "ALIGNED": {'description': 'Aligned to reference genome'},
    "DEDUPLICATED": {'description': 'PCR duplicates removed'},
    "RECALIBRATED": {'description': 'Base quality score recalibrated'},
    "VARIANT_CALLED": {'description': 'Variants called from alignments'},
    "NORMALIZED": {'description': 'Expression normalized (RNA-seq)'},
    "ASSEMBLED": {'description': 'De novo assembled sequences'},
    "ANNOTATED": {'description': 'Functionally annotated sequences'},
}

class CdsPhaseType(RichEnum):
    """
    For features of type CDS (coding sequence), the phase indicates where the feature begins with reference to the reading frame. The phase is one of the integers 0, 1, or 2, indicating the number of bases that should be removed from the beginning of this feature to reach the first base of the next codon.
    """
    # Enum members
    PHASE_0 = "PHASE_0"
    PHASE_1 = "PHASE_1"
    PHASE_2 = "PHASE_2"

# Set metadata after class creation to avoid it becoming an enum member
CdsPhaseType._metadata = {
    "PHASE_0": {'description': 'Zero bases from reading frame to feature start.'},
    "PHASE_1": {'description': 'One base from reading frame to feature start.'},
    "PHASE_2": {'description': 'Two bases from reading frame to feature start.'},
}

class ContigCollectionType(RichEnum):
    """
    The type of the contig set; the type of the 'omics data set. Terms are taken from the Genomics Standards Consortium where possible. See the GSC checklists at https://genomicsstandardsconsortium.github.io/mixs/ for the controlled vocabularies used.
    """
    # Enum members
    ISOLATE = "ISOLATE"
    MAG = "MAG"
    METAGENOME = "METAGENOME"
    METATRANSCRIPTOME = "METATRANSCRIPTOME"
    SAG = "SAG"
    VIRUS = "VIRUS"
    MARKER = "MARKER"

# Set metadata after class creation to avoid it becoming an enum member
ContigCollectionType._metadata = {
    "ISOLATE": {'description': 'Sequences assembled from DNA of isolated organism. Bacteria/Archaea: https://genomicsstandardsconsortium.github.io/mixs/0010003/ Euk: https://genomicsstandardsconsortium.github.io/mixs/0010002/ Virus: https://genomicsstandardsconsortium.github.io/mixs/0010005/ Organelle: https://genomicsstandardsconsortium.github.io/mixs/0010006/ Plasmid: https://genomicsstandardsconsortium.github.io/mixs/0010004/'},
    "MAG": {'description': 'Sequences assembled from DNA of mixed community and binned. MAGs are likely to represent a single taxonomic origin. See checkm2 scores for quality assessment.', 'meaning': 'mixs:0010011', 'aliases': ['Mimag']},
    "METAGENOME": {'description': 'Sequences assembled from DNA of mixed community.', 'meaning': 'mixs:0010007', 'aliases': ['Mims']},
    "METATRANSCRIPTOME": {'description': 'Sequences assembled from RNA of mixed community. Currently not represented by GSC.'},
    "SAG": {'description': 'Sequences assembled from DNA of single cell.', 'meaning': 'mixs:0010010', 'aliases': ['Misag']},
    "VIRUS": {'description': 'Sequences assembled from uncultivated virus genome (DNA/RNA).', 'meaning': 'mixs:0010012', 'aliases': ['Miuvig']},
    "MARKER": {'description': 'Sequences from targeted region of DNA; see protocol for information on targeted region. specimen: https://genomicsstandardsconsortium.github.io/mixs/0010009/ survey: https://genomicsstandardsconsortium.github.io/mixs/0010008/'},
}

class StrandType(RichEnum):
    """
    The strand that a feature appears on relative to a landmark. Also encompasses unknown or irrelevant strandedness.
    """
    # Enum members
    NEGATIVE = "NEGATIVE"
    POSITIVE = "POSITIVE"
    UNKNOWN = "UNKNOWN"
    UNSTRANDED = "UNSTRANDED"

# Set metadata after class creation to avoid it becoming an enum member
StrandType._metadata = {
    "NEGATIVE": {'description': 'Represented by "-" in a GFF file; the strand is negative wrt the landmark.'},
    "POSITIVE": {'description': 'Represented by "+" in a GFF file; the strand is positive with relation to the landmark.'},
    "UNKNOWN": {'description': 'Represented by "?" in a GFF file. The strandedness is relevant but unknown.'},
    "UNSTRANDED": {'description': 'Represented by "." in a GFF file; the feature is not stranded.'},
}

class SequenceType(RichEnum):
    """
    The type of sequence being represented.
    """
    # Enum members
    NUCLEIC_ACID = "NUCLEIC_ACID"
    AMINO_ACID = "AMINO_ACID"

# Set metadata after class creation to avoid it becoming an enum member
SequenceType._metadata = {
    "NUCLEIC_ACID": {'description': 'A nucleic acid sequence, as found in an FNA file.'},
    "AMINO_ACID": {'description': 'An amino acid sequence, as would be found in an FAA file.'},
}

class ProteinEvidenceForExistence(RichEnum):
    """
    The evidence for the existence of a biological entity. See https://www.uniprot.org/help/protein_existence and https://www.ncbi.nlm.nih.gov/genbank/evidence/.
    """
    # Enum members
    EXPERIMENTAL_EVIDENCE_AT_PROTEIN_LEVEL = "EXPERIMENTAL_EVIDENCE_AT_PROTEIN_LEVEL"
    EXPERIMENTAL_EVIDENCE_AT_TRANSCRIPT_LEVEL = "EXPERIMENTAL_EVIDENCE_AT_TRANSCRIPT_LEVEL"
    PROTEIN_INFERRED_BY_HOMOLOGY = "PROTEIN_INFERRED_BY_HOMOLOGY"
    PROTEIN_PREDICTED = "PROTEIN_PREDICTED"
    PROTEIN_UNCERTAIN = "PROTEIN_UNCERTAIN"

# Set metadata after class creation to avoid it becoming an enum member
ProteinEvidenceForExistence._metadata = {
    "EXPERIMENTAL_EVIDENCE_AT_PROTEIN_LEVEL": {'description': 'Indicates that there is clear experimental evidence for the existence of the protein. The criteria include partial or complete Edman sequencing, clear identification by mass spectrometry, X-ray or NMR structure, good quality protein-protein interaction or detection of the protein by antibodies.'},
    "EXPERIMENTAL_EVIDENCE_AT_TRANSCRIPT_LEVEL": {'description': 'Indicates that the existence of a protein has not been strictly proven but that expression data (such as existence of cDNA(s), RT-PCR or Northern blots) indicate the existence of a transcript.'},
    "PROTEIN_INFERRED_BY_HOMOLOGY": {'description': 'Indicates that the existence of a protein is probable because clear orthologs exist in closely related species.'},
    "PROTEIN_PREDICTED": {'description': 'Used for entries without evidence at protein, transcript, or homology levels.'},
    "PROTEIN_UNCERTAIN": {'description': 'Indicates that the existence of the protein is unsure.'},
}

class RefSeqStatusType(RichEnum):
    """
    RefSeq status codes, taken from https://www.ncbi.nlm.nih.gov/genbank/evidence/.
    """
    # Enum members
    MODEL = "MODEL"
    INFERRED = "INFERRED"
    PREDICTED = "PREDICTED"
    PROVISIONAL = "PROVISIONAL"
    REVIEWED = "REVIEWED"
    VALIDATED = "VALIDATED"
    WGS = "WGS"

# Set metadata after class creation to avoid it becoming an enum member
RefSeqStatusType._metadata = {
    "MODEL": {'description': 'The RefSeq record is provided by the NCBI Genome Annotation pipeline and is not subject to individual review or revision between annotation runs.'},
    "INFERRED": {'description': 'The RefSeq record has been predicted by genome sequence analysis, but it is not yet supported by experimental evidence. The record may be partially supported by homology data.'},
    "PREDICTED": {'description': 'The RefSeq record has not yet been subject to individual review, and some aspect of the RefSeq record is predicted.'},
    "PROVISIONAL": {'description': 'The RefSeq record has not yet been subject to individual review. The initial sequence-to-gene association has been established by outside collaborators or NCBI staff.'},
    "REVIEWED": {'description': 'The RefSeq record has been reviewed by NCBI staff or by a collaborator. The NCBI review process includes assessing available sequence data and the literature. Some RefSeq records may incorporate expanded sequence and annotation information.'},
    "VALIDATED": {'description': 'The RefSeq record has undergone an initial review to provide the preferred sequence standard. The record has not yet been subject to final review at which time additional functional information may be provided.'},
    "WGS": {'description': 'The RefSeq record is provided to represent a collection of whole genome shotgun sequences. These records are not subject to individual review or revisions between genome updates.'},
}

class CurrencyChemical(RichEnum):
    """
    Common metabolic currency molecules and cofactors that serve as energy carriers, electron donors/acceptors, and group transfer agents in cellular metabolism.
    """
    # Enum members
    ATP = "ATP"
    ADP = "ADP"
    AMP = "AMP"
    GTP = "GTP"
    GDP = "GDP"
    NAD_PLUS = "NAD_PLUS"
    NADH = "NADH"
    NADP_PLUS = "NADP_PLUS"
    NADPH = "NADPH"
    FAD = "FAD"
    FADH2 = "FADH2"
    COA = "COA"
    ACETYL_COA = "ACETYL_COA"

# Set metadata after class creation to avoid it becoming an enum member
CurrencyChemical._metadata = {
    "ATP": {'description': 'Adenosine triphosphate - primary energy currency molecule in cells', 'meaning': 'CHEBI:15422'},
    "ADP": {'description': 'Adenosine diphosphate - product of ATP hydrolysis, energy acceptor', 'meaning': 'CHEBI:16761'},
    "AMP": {'description': 'Adenosine monophosphate - nucleotide, product of ADP hydrolysis', 'meaning': 'CHEBI:16027', 'aliases': ["adenosine 5'-monophosphate"]},
    "GTP": {'description': 'Guanosine triphosphate - energy molecule, protein synthesis and signaling', 'meaning': 'CHEBI:15996'},
    "GDP": {'description': 'Guanosine diphosphate - product of GTP hydrolysis', 'meaning': 'CHEBI:17552'},
    "NAD_PLUS": {'description': 'Nicotinamide adenine dinucleotide (oxidized) - electron acceptor in catabolism', 'meaning': 'CHEBI:15846'},
    "NADH": {'description': 'Nicotinamide adenine dinucleotide (reduced) - electron donor, reducing agent', 'meaning': 'CHEBI:16908'},
    "NADP_PLUS": {'description': 'Nicotinamide adenine dinucleotide phosphate (oxidized) - electron acceptor', 'meaning': 'CHEBI:18009'},
    "NADPH": {'description': 'Nicotinamide adenine dinucleotide phosphate (reduced) - anabolic reducing agent', 'meaning': 'CHEBI:16474'},
    "FAD": {'description': 'Flavin adenine dinucleotide (oxidized) - electron acceptor in oxidation reactions', 'meaning': 'CHEBI:16238'},
    "FADH2": {'description': 'Flavin adenine dinucleotide (reduced) - electron donor in electron transport chain', 'meaning': 'CHEBI:17877'},
    "COA": {'description': 'Coenzyme A - acyl group carrier in fatty acid metabolism', 'meaning': 'CHEBI:15346', 'aliases': ['coenzyme A']},
    "ACETYL_COA": {'description': 'Acetyl coenzyme A - central metabolic intermediate, links glycolysis to citric acid cycle', 'meaning': 'CHEBI:15351'},
}

class PlantDevelopmentalStage(RichEnum):
    """
    Major developmental stages in the plant life cycle, from seed germination through senescence. Based on the Plant Ontology (PO) standardized stages.
    """
    # Enum members
    SEED_GERMINATION_STAGE = "SEED_GERMINATION_STAGE"
    SEEDLING_STAGE = "SEEDLING_STAGE"
    VEGETATIVE_GROWTH_STAGE = "VEGETATIVE_GROWTH_STAGE"
    FLOWERING_STAGE = "FLOWERING_STAGE"
    FRUIT_DEVELOPMENT_STAGE = "FRUIT_DEVELOPMENT_STAGE"
    SEED_DEVELOPMENT_STAGE = "SEED_DEVELOPMENT_STAGE"
    SENESCENCE_STAGE = "SENESCENCE_STAGE"
    DORMANCY_STAGE = "DORMANCY_STAGE"
    EMBRYO_DEVELOPMENT_STAGE = "EMBRYO_DEVELOPMENT_STAGE"
    ROOT_DEVELOPMENT_STAGE = "ROOT_DEVELOPMENT_STAGE"
    LEAF_DEVELOPMENT_STAGE = "LEAF_DEVELOPMENT_STAGE"
    REPRODUCTIVE_STAGE = "REPRODUCTIVE_STAGE"
    MATURITY_STAGE = "MATURITY_STAGE"
    POST_HARVEST_STAGE = "POST_HARVEST_STAGE"

# Set metadata after class creation to avoid it becoming an enum member
PlantDevelopmentalStage._metadata = {
    "SEED_GERMINATION_STAGE": {'description': 'Stage beginning with seed imbibition and ending with radicle emergence', 'meaning': 'PO:0007057'},
    "SEEDLING_STAGE": {'description': 'Stage from germination until development of first adult vascular leaf', 'meaning': 'PO:0007131', 'aliases': ['seedling development stage']},
    "VEGETATIVE_GROWTH_STAGE": {'description': 'Stage of growth before reproductive structure formation', 'meaning': 'PO:0007134', 'aliases': ['sporophyte vegetative stage']},
    "FLOWERING_STAGE": {'description': 'Stage when flowers open with pollen release and/or receptive stigma', 'meaning': 'PO:0007616'},
    "FRUIT_DEVELOPMENT_STAGE": {'description': 'Stage of fruit formation through ripening', 'meaning': 'PO:0001002'},
    "SEED_DEVELOPMENT_STAGE": {'description': 'Stage from fertilization to mature seed', 'meaning': 'PO:0001170'},
    "SENESCENCE_STAGE": {'description': 'Stage of aging with loss of function and organ deterioration', 'meaning': 'PO:0007017', 'aliases': ['sporophyte senescent stage']},
    "DORMANCY_STAGE": {'description': 'Stage of suspended physiological activity and growth', 'meaning': 'PO:0007132', 'aliases': ['sporophyte dormant stage']},
    "EMBRYO_DEVELOPMENT_STAGE": {'description': 'Stage from zygote first division to seed germination initiation', 'meaning': 'PO:0007631', 'aliases': ['plant embryo development stage']},
    "ROOT_DEVELOPMENT_STAGE": {'description': 'Stages in root growth and development', 'meaning': 'PO:0007520'},
    "LEAF_DEVELOPMENT_STAGE": {'description': 'Stages in leaf formation and expansion', 'meaning': 'PO:0001050'},
    "REPRODUCTIVE_STAGE": {'description': 'Stage from reproductive structure initiation to senescence onset', 'meaning': 'PO:0007130', 'aliases': ['sporophyte reproductive stage']},
    "MATURITY_STAGE": {'description': 'Stage when plant or plant embryo reaches full development', 'meaning': 'PO:0001081', 'aliases': ['mature plant embryo stage']},
    "POST_HARVEST_STAGE": {'description': 'Stage after harvest when plant parts are detached from parent plant'},
}

class UniProtSpeciesCode(RichEnum):
    """
    UniProt species mnemonic codes for reference proteomes with associated metadata
    """
    # Enum members
    SP_9ABAC = "SP_9ABAC"
    SP_9ACAR = "SP_9ACAR"
    SP_9ACTN = "SP_9ACTN"
    SP_9ACTO = "SP_9ACTO"
    SP_9ADEN = "SP_9ADEN"
    SP_9AGAM = "SP_9AGAM"
    SP_9AGAR = "SP_9AGAR"
    SP_9ALPC = "SP_9ALPC"
    SP_9ALPH = "SP_9ALPH"
    SP_9ALTE = "SP_9ALTE"
    SP_9ALVE = "SP_9ALVE"
    SP_9AMPH = "SP_9AMPH"
    SP_9ANNE = "SP_9ANNE"
    SP_9ANUR = "SP_9ANUR"
    SP_9APHY = "SP_9APHY"
    SP_9APIA = "SP_9APIA"
    SP_9APIC = "SP_9APIC"
    SP_9AQUI = "SP_9AQUI"
    SP_9ARAC = "SP_9ARAC"
    SP_9ARCH = "SP_9ARCH"
    SP_9ASCO = "SP_9ASCO"
    SP_9ASPA = "SP_9ASPA"
    SP_9ASTE = "SP_9ASTE"
    SP_9ASTR = "SP_9ASTR"
    SP_9AVES = "SP_9AVES"
    SP_9BACE = "SP_9BACE"
    SP_9BACI = "SP_9BACI"
    SP_9BACL = "SP_9BACL"
    SP_9BACT = "SP_9BACT"
    SP_9BACU = "SP_9BACU"
    SP_9BASI = "SP_9BASI"
    SP_9BBAC = "SP_9BBAC"
    SP_9BETA = "SP_9BETA"
    SP_9BETC = "SP_9BETC"
    SP_9BIFI = "SP_9BIFI"
    SP_9BILA = "SP_9BILA"
    SP_9BIVA = "SP_9BIVA"
    SP_9BORD = "SP_9BORD"
    SP_9BRAD = "SP_9BRAD"
    SP_9BRAS = "SP_9BRAS"
    SP_9BROM = "SP_9BROM"
    SP_9BURK = "SP_9BURK"
    SP_9CARY = "SP_9CARY"
    SP_9CAUD = "SP_9CAUD"
    SP_9CAUL = "SP_9CAUL"
    SP_9CBAC = "SP_9CBAC"
    SP_9CELL = "SP_9CELL"
    SP_9CERV = "SP_9CERV"
    SP_9CETA = "SP_9CETA"
    SP_9CHAR = "SP_9CHAR"
    SP_9CHIR = "SP_9CHIR"
    SP_9CHLA = "SP_9CHLA"
    SP_9CHLB = "SP_9CHLB"
    SP_9CHLO = "SP_9CHLO"
    SP_9CHLR = "SP_9CHLR"
    SP_9CHRO = "SP_9CHRO"
    SP_9CICH = "SP_9CICH"
    SP_9CILI = "SP_9CILI"
    SP_9CIRC = "SP_9CIRC"
    SP_9CLOS = "SP_9CLOS"
    SP_9CLOT = "SP_9CLOT"
    SP_9CNID = "SP_9CNID"
    SP_9COLU = "SP_9COLU"
    SP_9CORV = "SP_9CORV"
    SP_9CORY = "SP_9CORY"
    SP_9COXI = "SP_9COXI"
    SP_9CREN = "SP_9CREN"
    SP_9CRUS = "SP_9CRUS"
    SP_9CUCU = "SP_9CUCU"
    SP_9CYAN = "SP_9CYAN"
    SP_9DEIN = "SP_9DEIN"
    SP_9DEIO = "SP_9DEIO"
    SP_9DELA = "SP_9DELA"
    SP_9DELT = "SP_9DELT"
    SP_9DEND = "SP_9DEND"
    SP_9DINO = "SP_9DINO"
    SP_9DIPT = "SP_9DIPT"
    SP_9EIME = "SP_9EIME"
    SP_9EMBE = "SP_9EMBE"
    SP_9ENTE = "SP_9ENTE"
    SP_9ENTR = "SP_9ENTR"
    SP_9ERIC = "SP_9ERIC"
    SP_9EUCA = "SP_9EUCA"
    SP_9EUGL = "SP_9EUGL"
    SP_9EUKA = "SP_9EUKA"
    SP_9EUPU = "SP_9EUPU"
    SP_9EURO = "SP_9EURO"
    SP_9EURY = "SP_9EURY"
    SP_9FABA = "SP_9FABA"
    SP_9FIRM = "SP_9FIRM"
    SP_9FLAO = "SP_9FLAO"
    SP_9FLAV = "SP_9FLAV"
    SP_9FLOR = "SP_9FLOR"
    SP_9FRIN = "SP_9FRIN"
    SP_9FUNG = "SP_9FUNG"
    SP_9FURN = "SP_9FURN"
    SP_9FUSO = "SP_9FUSO"
    SP_9GALL = "SP_9GALL"
    SP_9GAMA = "SP_9GAMA"
    SP_9GAMC = "SP_9GAMC"
    SP_9GAMM = "SP_9GAMM"
    SP_9GAST = "SP_9GAST"
    SP_9GEMI = "SP_9GEMI"
    SP_9GLOM = "SP_9GLOM"
    SP_9GOBI = "SP_9GOBI"
    SP_9GRUI = "SP_9GRUI"
    SP_9HELI = "SP_9HELI"
    SP_9HELO = "SP_9HELO"
    SP_9HEMI = "SP_9HEMI"
    SP_9HEPA = "SP_9HEPA"
    SP_9HEXA = "SP_9HEXA"
    SP_9HYME = "SP_9HYME"
    SP_9HYPH = "SP_9HYPH"
    SP_9HYPO = "SP_9HYPO"
    SP_9INFA = "SP_9INFA"
    SP_9INSE = "SP_9INSE"
    SP_9LABR = "SP_9LABR"
    SP_ARATH = "SP_ARATH"
    SP_BACSU = "SP_BACSU"
    SP_BOVIN = "SP_BOVIN"
    SP_CAEEL = "SP_CAEEL"
    SP_CANLF = "SP_CANLF"
    SP_CHICK = "SP_CHICK"
    SP_DANRE = "SP_DANRE"
    SP_DROME = "SP_DROME"
    SP_ECOLI = "SP_ECOLI"
    SP_FELCA = "SP_FELCA"
    SP_GORGO = "SP_GORGO"
    SP_HORSE = "SP_HORSE"
    SP_HUMAN = "SP_HUMAN"
    SP_MACMU = "SP_MACMU"
    SP_MAIZE = "SP_MAIZE"
    SP_MOUSE = "SP_MOUSE"
    SP_ORYSJ = "SP_ORYSJ"
    SP_PANTR = "SP_PANTR"
    SP_PIG = "SP_PIG"
    SP_RABIT = "SP_RABIT"
    SP_RAT = "SP_RAT"
    SP_SCHPO = "SP_SCHPO"
    SP_SHEEP = "SP_SHEEP"
    SP_XENLA = "SP_XENLA"
    SP_XENTR = "SP_XENTR"
    SP_YEAST = "SP_YEAST"
    SP_DICDI = "SP_DICDI"
    SP_HELPY = "SP_HELPY"
    SP_LEIMA = "SP_LEIMA"
    SP_MEDTR = "SP_MEDTR"
    SP_MYCTU = "SP_MYCTU"
    SP_NEIME = "SP_NEIME"
    SP_PLAF7 = "SP_PLAF7"
    SP_PSEAE = "SP_PSEAE"
    SP_SOYBN = "SP_SOYBN"
    SP_STAAU = "SP_STAAU"
    SP_STRPN = "SP_STRPN"
    SP_TOXGO = "SP_TOXGO"
    SP_TRYB2 = "SP_TRYB2"
    SP_WHEAT = "SP_WHEAT"
    SP_PEA = "SP_PEA"
    SP_TOBAC = "SP_TOBAC"

# Set metadata after class creation to avoid it becoming an enum member
UniProtSpeciesCode._metadata = {
    "SP_9ABAC": {'description': 'Lambdina fiscellaria nucleopolyhedrovirus - Proteome: UP000201190', 'meaning': 'NCBITaxon:1642929'},
    "SP_9ACAR": {'description': 'Tropilaelaps mercedesae - Proteome: UP000192247', 'meaning': 'NCBITaxon:418985'},
    "SP_9ACTN": {'description': 'Candidatus Protofrankia datiscae - Proteome: UP000001549', 'meaning': 'NCBITaxon:2716812'},
    "SP_9ACTO": {'description': 'Actinomyces massiliensis F0489 - Proteome: UP000002941', 'meaning': 'NCBITaxon:1125718'},
    "SP_9ADEN": {'description': 'Human adenovirus 53 - Proteome: UP000463865', 'meaning': 'NCBITaxon:556926'},
    "SP_9AGAM": {'description': 'Jaapia argillacea MUCL 33604 - Proteome: UP000027265', 'meaning': 'NCBITaxon:933084'},
    "SP_9AGAR": {'description': 'Collybiopsis luxurians FD-317 M1 - Proteome: UP000053593', 'meaning': 'NCBITaxon:944289'},
    "SP_9ALPC": {'description': 'Feline coronavirus - Proteome: UP000141821', 'meaning': 'NCBITaxon:12663'},
    "SP_9ALPH": {'description': 'Testudinid alphaherpesvirus 3 - Proteome: UP000100290', 'meaning': 'NCBITaxon:2560801'},
    "SP_9ALTE": {'description': 'Paraglaciecola arctica BSs20135 - Proteome: UP000006327', 'meaning': 'NCBITaxon:493475'},
    "SP_9ALVE": {'description': 'Perkinsus sp. BL_2016 - Proteome: UP000298064', 'meaning': 'NCBITaxon:2494336'},
    "SP_9AMPH": {'description': 'Microcaecilia unicolor - Proteome: UP000515156', 'meaning': 'NCBITaxon:1415580'},
    "SP_9ANNE": {'description': 'Dimorphilus gyrociliatus - Proteome: UP000549394', 'meaning': 'NCBITaxon:2664684'},
    "SP_9ANUR": {'description': 'Leptobrachium leishanense (Leishan spiny toad) - Proteome: UP000694569', 'meaning': 'NCBITaxon:445787'},
    "SP_9APHY": {'description': 'Fibroporia radiculosa - Proteome: UP000006352', 'meaning': 'NCBITaxon:599839'},
    "SP_9APIA": {'description': 'Heracleum sosnowskyi - Proteome: UP001237642', 'meaning': 'NCBITaxon:360622'},
    "SP_9APIC": {'description': 'Babesia sp. Xinjiang - Proteome: UP000193856', 'meaning': 'NCBITaxon:462227'},
    "SP_9AQUI": {'description': 'Sulfurihydrogenibium yellowstonense SS-5 - Proteome: UP000005540', 'meaning': 'NCBITaxon:432331'},
    "SP_9ARAC": {'description': 'Trichonephila inaurata madagascariensis - Proteome: UP000886998', 'meaning': 'NCBITaxon:2747483'},
    "SP_9ARCH": {'description': 'Candidatus Nitrosarchaeum limnium BG20 - Proteome: UP000014065', 'meaning': 'NCBITaxon:859192'},
    "SP_9ASCO": {'description': 'Kuraishia capsulata CBS 1993 - Proteome: UP000019384', 'meaning': 'NCBITaxon:1382522'},
    "SP_9ASPA": {'description': 'Dendrobium catenatum - Proteome: UP000233837', 'meaning': 'NCBITaxon:906689'},
    "SP_9ASTE": {'description': 'Cuscuta australis - Proteome: UP000249390', 'meaning': 'NCBITaxon:267555'},
    "SP_9ASTR": {'description': 'Mikania micrantha - Proteome: UP000326396', 'meaning': 'NCBITaxon:192012'},
    "SP_9AVES": {'description': 'Anser brachyrhynchus (Pink-footed goose) - Proteome: UP000694426', 'meaning': 'NCBITaxon:132585'},
    "SP_9BACE": {'description': 'Bacteroides caccae CL03T12C61 - Proteome: UP000002965', 'meaning': 'NCBITaxon:997873'},
    "SP_9BACI": {'description': 'Fictibacillus macauensis ZFHKF-1 - Proteome: UP000004080', 'meaning': 'NCBITaxon:1196324'},
    "SP_9BACL": {'description': 'Paenibacillus sp. HGF7 - Proteome: UP000003445', 'meaning': 'NCBITaxon:944559'},
    "SP_9BACT": {'description': 'Parabacteroides johnsonii CL02T12C29 - Proteome: UP000001218', 'meaning': 'NCBITaxon:999419'},
    "SP_9BACU": {'description': 'Samia ricini nucleopolyhedrovirus - Proteome: UP001226138', 'meaning': 'NCBITaxon:1920700'},
    "SP_9BASI": {'description': 'Malassezia pachydermatis - Proteome: UP000037751', 'meaning': 'NCBITaxon:77020'},
    "SP_9BBAC": {'description': 'Plutella xylostella granulovirus - Proteome: UP000201310', 'meaning': 'NCBITaxon:98383'},
    "SP_9BETA": {'description': 'Saimiriine betaherpesvirus 4 - Proteome: UP000097892', 'meaning': 'NCBITaxon:1535247'},
    "SP_9BETC": {'description': 'Coronavirus BtRt-BetaCoV/GX2018 - Proteome: UP001228689', 'meaning': 'NCBITaxon:2591238'},
    "SP_9BIFI": {'description': 'Scardovia wiggsiae F0424 - Proteome: UP000006415', 'meaning': 'NCBITaxon:857290'},
    "SP_9BILA": {'description': 'Ancylostoma ceylanicum - Proteome: UP000024635', 'meaning': 'NCBITaxon:53326'},
    "SP_9BIVA": {'description': 'Potamilus streckersoni - Proteome: UP001195483', 'meaning': 'NCBITaxon:2493646'},
    "SP_9BORD": {'description': 'Bordetella sp. N - Proteome: UP000064621', 'meaning': 'NCBITaxon:1746199'},
    "SP_9BRAD": {'description': 'Afipia broomeae ATCC 49717 - Proteome: UP000001096', 'meaning': 'NCBITaxon:883078'},
    "SP_9BRAS": {'description': 'Capsella rubella - Proteome: UP000029121', 'meaning': 'NCBITaxon:81985'},
    "SP_9BROM": {'description': 'Prune dwarf virus - Proteome: UP000202132', 'meaning': 'NCBITaxon:33760'},
    "SP_9BURK": {'description': 'Candidatus Paraburkholderia kirkii UZHbot1 - Proteome: UP000003511', 'meaning': 'NCBITaxon:1055526'},
    "SP_9CARY": {'description': 'Carnegiea gigantea - Proteome: UP001153076', 'meaning': 'NCBITaxon:171969'},
    "SP_9CAUD": {'description': 'Salmonella phage Vi06 - Proteome: UP000000335', 'meaning': 'NCBITaxon:866889'},
    "SP_9CAUL": {'description': 'Brevundimonas abyssalis TAR-001 - Proteome: UP000016569', 'meaning': 'NCBITaxon:1391729'},
    "SP_9CBAC": {'description': 'Neodiprion sertifer nucleopolyhedrovirus - Proteome: UP000243697', 'meaning': 'NCBITaxon:111874'},
    "SP_9CELL": {'description': 'Actinotalea ferrariae CF5-4 - Proteome: UP000019753', 'meaning': 'NCBITaxon:948458'},
    "SP_9CERV": {'description': 'Cervus hanglu yarkandensis (Yarkand deer) - Proteome: UP000631465', 'meaning': 'NCBITaxon:84702'},
    "SP_9CETA": {'description': 'Catagonus wagneri (Chacoan peccary) - Proteome: UP000694540', 'meaning': 'NCBITaxon:51154'},
    "SP_9CHAR": {'description': 'Rostratula benghalensis (greater painted-snipe) - Proteome: UP000545435', 'meaning': 'NCBITaxon:118793'},
    "SP_9CHIR": {'description': 'Phyllostomus discolor (pale spear-nosed bat) - Proteome: UP000504628', 'meaning': 'NCBITaxon:89673'},
    "SP_9CHLA": {'description': 'Chlamydiales bacterium SCGC AG-110-P3 - Proteome: UP000196763', 'meaning': 'NCBITaxon:1871323'},
    "SP_9CHLB": {'description': 'Chlorobium ferrooxidans DSM 13031 - Proteome: UP000004162', 'meaning': 'NCBITaxon:377431'},
    "SP_9CHLO": {'description': 'Helicosporidium sp. ATCC 50920 - Proteome: UP000026042', 'meaning': 'NCBITaxon:1291522'},
    "SP_9CHLR": {'description': 'Ardenticatena maritima - Proteome: UP000037784', 'meaning': 'NCBITaxon:872965'},
    "SP_9CHRO": {'description': 'Gloeocapsa sp. PCC 7428 - Proteome: UP000010476', 'meaning': 'NCBITaxon:1173026'},
    "SP_9CICH": {'description': 'Maylandia zebra (zebra mbuna) - Proteome: UP000265160', 'meaning': 'NCBITaxon:106582'},
    "SP_9CILI": {'description': 'Stentor coeruleus - Proteome: UP000187209', 'meaning': 'NCBITaxon:5963'},
    "SP_9CIRC": {'description': 'Raven circovirus - Proteome: UP000097131', 'meaning': 'NCBITaxon:345250'},
    "SP_9CLOS": {'description': 'Grapevine leafroll-associated virus 10 - Proteome: UP000203128', 'meaning': 'NCBITaxon:367121'},
    "SP_9CLOT": {'description': 'Candidatus Arthromitus sp. SFB-rat-Yit - Proteome: UP000001273', 'meaning': 'NCBITaxon:1041504'},
    "SP_9CNID": {'description': 'Clytia hemisphaerica - Proteome: UP000594262', 'meaning': 'NCBITaxon:252671'},
    "SP_9COLU": {'description': 'Pampusana beccarii (Western bronze ground-dove) - Proteome: UP000541332', 'meaning': 'NCBITaxon:2953425'},
    "SP_9CORV": {'description': "Cnemophilus loriae (Loria's bird-of-paradise) - Proteome: UP000517678", 'meaning': 'NCBITaxon:254448'},
    "SP_9CORY": {'description': 'Corynebacterium genitalium ATCC 33030 - Proteome: UP000004208', 'meaning': 'NCBITaxon:585529'},
    "SP_9COXI": {'description': 'Coxiella endosymbiont of Amblyomma americanum - Proteome: UP000059222', 'meaning': 'NCBITaxon:325775'},
    "SP_9CREN": {'description': 'Metallosphaera yellowstonensis MK1 - Proteome: UP000003980', 'meaning': 'NCBITaxon:671065'},
    "SP_9CRUS": {'description': 'Daphnia magna - Proteome: UP000076858', 'meaning': 'NCBITaxon:35525'},
    "SP_9CUCU": {'description': 'Ceutorhynchus assimilis (cabbage seed weevil) - Proteome: UP001152799', 'meaning': 'NCBITaxon:467358'},
    "SP_9CYAN": {'description': 'Leptolyngbyaceae cyanobacterium JSC-12 - Proteome: UP000001332', 'meaning': 'NCBITaxon:864702'},
    "SP_9DEIN": {'description': 'Meiothermus sp. QL-1 - Proteome: UP000255346', 'meaning': 'NCBITaxon:2058095'},
    "SP_9DEIO": {'description': 'Deinococcus sp. RL - Proteome: UP000027898', 'meaning': 'NCBITaxon:1489678'},
    "SP_9DELA": {'description': 'Human T-cell leukemia virus type I - Proteome: UP000108043', 'meaning': 'NCBITaxon:11908'},
    "SP_9DELT": {'description': 'Lujinxingia litoralis - Proteome: UP000249169', 'meaning': 'NCBITaxon:2211119'},
    "SP_9DEND": {'description': 'Xiphorhynchus elegans (elegant woodcreeper) - Proteome: UP000551443', 'meaning': 'NCBITaxon:269412'},
    "SP_9DINO": {'description': 'Symbiodinium necroappetens - Proteome: UP000601435', 'meaning': 'NCBITaxon:1628268'},
    "SP_9DIPT": {'description': 'Clunio marinus - Proteome: UP000183832', 'meaning': 'NCBITaxon:568069'},
    "SP_9EIME": {'description': 'Eimeria praecox - Proteome: UP000018201', 'meaning': 'NCBITaxon:51316'},
    "SP_9EMBE": {'description': 'Emberiza fucata - Proteome: UP000580681', 'meaning': 'NCBITaxon:337179'},
    "SP_9ENTE": {'description': 'Enterococcus asini ATCC 700915 - Proteome: UP000013777', 'meaning': 'NCBITaxon:1158606'},
    "SP_9ENTR": {'description': 'secondary endosymbiont of Heteropsylla cubana - Proteome: UP000003937', 'meaning': 'NCBITaxon:134287'},
    "SP_9ERIC": {'description': 'Rhododendron williamsianum - Proteome: UP000428333', 'meaning': 'NCBITaxon:262921'},
    "SP_9EUCA": {'description': 'Petrolisthes manimaculis - Proteome: UP001292094', 'meaning': 'NCBITaxon:1843537'},
    "SP_9EUGL": {'description': 'Perkinsela sp. CCAP 1560/4 - Proteome: UP000036983', 'meaning': 'NCBITaxon:1314962'},
    "SP_9EUKA": {'description': 'Chrysochromulina tobinii - Proteome: UP000037460', 'meaning': 'NCBITaxon:1460289'},
    "SP_9EUPU": {'description': 'Candidula unifasciata - Proteome: UP000678393', 'meaning': 'NCBITaxon:100452'},
    "SP_9EURO": {'description': 'Cladophialophora psammophila CBS 110553 - Proteome: UP000019471', 'meaning': 'NCBITaxon:1182543'},
    "SP_9EURY": {'description': 'Methanoplanus limicola DSM 2279 - Proteome: UP000005741', 'meaning': 'NCBITaxon:937775'},
    "SP_9FABA": {'description': 'Senna tora - Proteome: UP000634136', 'meaning': 'NCBITaxon:362788'},
    "SP_9FIRM": {'description': 'Ruminococcaceae bacterium D16 - Proteome: UP000002801', 'meaning': 'NCBITaxon:552398'},
    "SP_9FLAO": {'description': 'Capnocytophaga sp. oral taxon 338 str. F0234 - Proteome: UP000003023', 'meaning': 'NCBITaxon:888059'},
    "SP_9FLAV": {'description': 'Tunisian sheep-like pestivirus - Proteome: UP001157330', 'meaning': 'NCBITaxon:3071305'},
    "SP_9FLOR": {'description': 'Gracilariopsis chorda - Proteome: UP000247409', 'meaning': 'NCBITaxon:448386'},
    "SP_9FRIN": {'description': 'Urocynchramus pylzowi - Proteome: UP000524542', 'meaning': 'NCBITaxon:571890'},
    "SP_9FUNG": {'description': 'Lichtheimia corymbifera JMRC:FSU:9682 - Proteome: UP000027586', 'meaning': 'NCBITaxon:1263082'},
    "SP_9FURN": {'description': 'Furnarius figulus - Proteome: UP000529852', 'meaning': 'NCBITaxon:463165'},
    "SP_9FUSO": {'description': 'Fusobacterium gonidiaformans 3-1-5R - Proteome: UP000002975', 'meaning': 'NCBITaxon:469605'},
    "SP_9GALL": {'description': 'Odontophorus gujanensis (marbled wood quail) - Proteome: UP000522663', 'meaning': 'NCBITaxon:886794'},
    "SP_9GAMA": {'description': 'Bovine gammaherpesvirus 6 - Proteome: UP000121539', 'meaning': 'NCBITaxon:1504288'},
    "SP_9GAMC": {'description': 'Anser fabalis coronavirus NCN2 - Proteome: UP001251675', 'meaning': 'NCBITaxon:2860474'},
    "SP_9GAMM": {'description': 'Buchnera aphidicola (Cinara tujafilina) - Proteome: UP000006811', 'meaning': 'NCBITaxon:261317', 'aliases': ['Buchnera aphidicola (Cinara tujafilina)']},
    "SP_9GAST": {'description': 'Elysia crispata (lettuce slug) - Proteome: UP001283361', 'meaning': 'NCBITaxon:231223'},
    "SP_9GEMI": {'description': 'East African cassava mosaic Zanzibar virus - Proteome: UP000201107', 'meaning': 'NCBITaxon:223275'},
    "SP_9GLOM": {'description': 'Paraglomus occultum - Proteome: UP000789572', 'meaning': 'NCBITaxon:144539'},
    "SP_9GOBI": {'description': 'Neogobius melanostomus (round goby) - Proteome: UP000694523', 'meaning': 'NCBITaxon:47308'},
    "SP_9GRUI": {'description': 'Atlantisia rogersi (Inaccessible Island rail) - Proteome: UP000518911', 'meaning': 'NCBITaxon:2478892'},
    "SP_9HELI": {'description': 'Helicobacter bilis ATCC 43879 - Proteome: UP000005085', 'meaning': 'NCBITaxon:613026'},
    "SP_9HELO": {'description': 'Rhynchosporium graminicola - Proteome: UP000178129', 'meaning': 'NCBITaxon:2792576'},
    "SP_9HEMI": {'description': 'Cinara cedri - Proteome: UP000325440', 'meaning': 'NCBITaxon:506608'},
    "SP_9HEPA": {'description': 'Duck hepatitis B virus - Proteome: UP000137229', 'meaning': 'NCBITaxon:12639'},
    "SP_9HEXA": {'description': 'Allacma fusca - Proteome: UP000708208', 'meaning': 'NCBITaxon:39272'},
    "SP_9HYME": {'description': 'Melipona quadrifasciata - Proteome: UP000053105', 'meaning': 'NCBITaxon:166423'},
    "SP_9HYPH": {'description': 'Mesorhizobium amorphae CCNWGS0123 - Proteome: UP000002949', 'meaning': 'NCBITaxon:1082933'},
    "SP_9HYPO": {'description': '[Torrubiella] hemipterigena - Proteome: UP000039046', 'meaning': 'NCBITaxon:1531966'},
    "SP_9INFA": {'description': 'Influenza A virus (A/California/VRDL364/2009 (mixed) - Proteome: UP000109975', 'meaning': 'NCBITaxon:1049605', 'aliases': ['Influenza A virus (A/California/VRDL364/2009(mixed))']},
    "SP_9INSE": {'description': 'Cloeon dipterum - Proteome: UP000494165', 'meaning': 'NCBITaxon:197152'},
    "SP_9LABR": {'description': 'Labrus bergylta (ballan wrasse) - Proteome: UP000261660', 'meaning': 'NCBITaxon:56723'},
    "SP_ARATH": {'description': 'Arabidopsis thaliana (Thale cress) - Proteome: UP000006548', 'meaning': 'NCBITaxon:3702', 'aliases': ['Thale cress']},
    "SP_BACSU": {'description': 'Bacillus subtilis subsp. subtilis str. 168 - Proteome: UP000001570', 'meaning': 'NCBITaxon:224308'},
    "SP_BOVIN": {'description': 'Bos taurus (Cattle) - Proteome: UP000009136', 'meaning': 'NCBITaxon:9913', 'aliases': ['Cattle']},
    "SP_CAEEL": {'description': 'Caenorhabditis elegans - Proteome: UP000001940', 'meaning': 'NCBITaxon:6239'},
    "SP_CANLF": {'description': 'Canis lupus familiaris (Dog) - Proteome: UP000805418', 'meaning': 'NCBITaxon:9615', 'aliases': ['Dog']},
    "SP_CHICK": {'description': 'Gallus gallus (Chicken) - Proteome: UP000000539', 'meaning': 'NCBITaxon:9031', 'aliases': ['Chicken']},
    "SP_DANRE": {'description': 'Danio rerio (Zebrafish) - Proteome: UP000000437', 'meaning': 'NCBITaxon:7955', 'aliases': ['Zebrafish']},
    "SP_DROME": {'description': 'Drosophila melanogaster (Fruit fly) - Proteome: UP000000803', 'meaning': 'NCBITaxon:7227', 'aliases': ['Fruit fly']},
    "SP_ECOLI": {'description': 'Escherichia coli K-12 - Proteome: UP000000625', 'meaning': 'NCBITaxon:83333'},
    "SP_FELCA": {'description': 'Felis catus (Cat) - Proteome: UP000011712', 'meaning': 'NCBITaxon:9685', 'aliases': ['Cat']},
    "SP_GORGO": {'description': 'Gorilla gorilla gorilla (Western lowland gorilla) - Proteome: UP000001519', 'meaning': 'NCBITaxon:9593', 'aliases': ['Western lowland gorilla', 'Gorilla gorilla']},
    "SP_HORSE": {'description': 'Equus caballus (Horse) - Proteome: UP000002281', 'meaning': 'NCBITaxon:9796', 'aliases': ['Horse']},
    "SP_HUMAN": {'description': 'Homo sapiens (Human) - Proteome: UP000005640', 'meaning': 'NCBITaxon:9606', 'aliases': ['Human']},
    "SP_MACMU": {'description': 'Macaca mulatta (Rhesus macaque) - Proteome: UP000006718', 'meaning': 'NCBITaxon:9544', 'aliases': ['Rhesus macaque']},
    "SP_MAIZE": {'description': 'Zea mays (Maize) - Proteome: UP000007305', 'meaning': 'NCBITaxon:4577', 'aliases': ['Maize']},
    "SP_MOUSE": {'description': 'Mus musculus (Mouse) - Proteome: UP000000589', 'meaning': 'NCBITaxon:10090', 'aliases': ['Mouse']},
    "SP_ORYSJ": {'description': 'Oryza sativa subsp. japonica (Rice) - Proteome: UP000059680', 'meaning': 'NCBITaxon:39947', 'aliases': ['Rice', 'Oryza sativa Japonica Group']},
    "SP_PANTR": {'description': 'Pan troglodytes (Chimpanzee) - Proteome: UP000002277', 'meaning': 'NCBITaxon:9598', 'aliases': ['Chimpanzee']},
    "SP_PIG": {'description': 'Sus scrofa (Pig) - Proteome: UP000008227', 'meaning': 'NCBITaxon:9823', 'aliases': ['Pig']},
    "SP_RABIT": {'description': 'Oryctolagus cuniculus (Rabbit) - Proteome: UP000001811', 'meaning': 'NCBITaxon:9986', 'aliases': ['Rabbit']},
    "SP_RAT": {'description': 'Rattus norvegicus (Rat) - Proteome: UP000002494', 'meaning': 'NCBITaxon:10116', 'aliases': ['Rat']},
    "SP_SCHPO": {'description': 'Schizosaccharomyces pombe 972h- (Fission yeast) - Proteome: UP000002485', 'meaning': 'NCBITaxon:284812', 'aliases': ['Fission yeast']},
    "SP_SHEEP": {'description': 'Ovis aries (Sheep) - Proteome: UP000002356', 'meaning': 'NCBITaxon:9940', 'aliases': ['Sheep']},
    "SP_XENLA": {'description': 'Xenopus laevis (African clawed frog) - Proteome: UP000186698', 'meaning': 'NCBITaxon:8355', 'aliases': ['African clawed frog']},
    "SP_XENTR": {'description': 'Xenopus tropicalis (Western clawed frog) - Proteome: UP000008143', 'meaning': 'NCBITaxon:8364', 'aliases': ['Western clawed frog']},
    "SP_YEAST": {'description': "Saccharomyces cerevisiae S288C (Baker's yeast) - Proteome: UP000002311", 'meaning': 'NCBITaxon:559292', 'aliases': ["Baker's yeast"]},
    "SP_DICDI": {'description': 'Dictyostelium discoideum (Slime mold) - Proteome: UP000002195', 'meaning': 'NCBITaxon:44689', 'aliases': ['Slime mold']},
    "SP_HELPY": {'description': 'Helicobacter pylori 26695 - Proteome: UP000000429', 'meaning': 'NCBITaxon:85962'},
    "SP_LEIMA": {'description': 'Leishmania major strain Friedlin', 'meaning': 'NCBITaxon:347515'},
    "SP_MEDTR": {'description': 'Medicago truncatula (Barrel medic) - Proteome: UP000002051', 'meaning': 'NCBITaxon:3880', 'aliases': ['Barrel medic']},
    "SP_MYCTU": {'description': 'Mycobacterium tuberculosis H37Rv - Proteome: UP000001584', 'meaning': 'NCBITaxon:83332'},
    "SP_NEIME": {'description': 'Neisseria meningitidis MC58 - Proteome: UP000000425', 'meaning': 'NCBITaxon:122586'},
    "SP_PLAF7": {'description': 'Plasmodium falciparum 3D7 (Malaria parasite) - Proteome: UP000001450', 'meaning': 'NCBITaxon:36329', 'aliases': ['Malaria parasite']},
    "SP_PSEAE": {'description': 'Pseudomonas aeruginosa PAO1 - Proteome: UP000002438', 'meaning': 'NCBITaxon:208964'},
    "SP_SOYBN": {'description': 'Glycine max (Soybean) - Proteome: UP000008827', 'meaning': 'NCBITaxon:3847', 'aliases': ['Soybean']},
    "SP_STAAU": {'description': 'Staphylococcus aureus subsp. aureus NCTC 8325 - Proteome: UP000008816', 'meaning': 'NCBITaxon:93061'},
    "SP_STRPN": {'description': 'Streptococcus pneumoniae R6 - Proteome: UP000000586', 'meaning': 'NCBITaxon:171101'},
    "SP_TOXGO": {'description': 'Toxoplasma gondii ME49 - Proteome: UP000001529', 'meaning': 'NCBITaxon:508771'},
    "SP_TRYB2": {'description': 'Trypanosoma brucei brucei TREU927 - Proteome: UP000008524', 'meaning': 'NCBITaxon:185431'},
    "SP_WHEAT": {'description': 'Triticum aestivum (Wheat) - Proteome: UP000019116', 'meaning': 'NCBITaxon:4565', 'aliases': ['Wheat']},
    "SP_PEA": {'description': 'Pisum sativum (Garden pea) - Proteome: UP001058974', 'meaning': 'NCBITaxon:3888', 'aliases': ['Garden pea', 'Lathyrus oleraceus']},
    "SP_TOBAC": {'description': 'Nicotiana tabacum (Common tobacco) - Proteome: UP000084051', 'meaning': 'NCBITaxon:4097', 'aliases': ['Common tobacco']},
}

class LipidCategory(RichEnum):
    """
    Major categories of lipids based on SwissLipids classification
    """
    # Enum members
    LIPID = "LIPID"
    FATTY_ACYLS_AND_DERIVATIVES = "FATTY_ACYLS_AND_DERIVATIVES"
    GLYCEROLIPIDS = "GLYCEROLIPIDS"
    GLYCEROPHOSPHOLIPIDS = "GLYCEROPHOSPHOLIPIDS"
    SPHINGOLIPIDS = "SPHINGOLIPIDS"
    STEROIDS_AND_DERIVATIVES = "STEROIDS_AND_DERIVATIVES"
    PRENOL_LIPIDS = "PRENOL_LIPIDS"

# Set metadata after class creation to avoid it becoming an enum member
LipidCategory._metadata = {
    "LIPID": {'description': 'Lipid', 'meaning': 'CHEBI:18059'},
    "FATTY_ACYLS_AND_DERIVATIVES": {'description': 'Fatty acyls and derivatives', 'meaning': 'CHEBI:24027', 'aliases': ['fatty-acyl group']},
    "GLYCEROLIPIDS": {'description': 'Glycerolipids', 'meaning': 'CHEBI:35741', 'aliases': ['glycerolipid']},
    "GLYCEROPHOSPHOLIPIDS": {'description': 'Glycerophospholipids', 'meaning': 'CHEBI:37739', 'aliases': ['glycerophospholipid']},
    "SPHINGOLIPIDS": {'description': 'Sphingolipids', 'meaning': 'CHEBI:26739', 'aliases': ['sphingolipid']},
    "STEROIDS_AND_DERIVATIVES": {'description': 'Steroids and derivatives', 'meaning': 'CHEBI:35341', 'aliases': ['steroid']},
    "PRENOL_LIPIDS": {'description': 'Prenol Lipids', 'meaning': 'CHEBI:24913', 'aliases': ['isoprenoid']},
}

class PeakAnnotationSeriesLabel(RichEnum):
    """
    Types of peak annotations in mass spectrometry data
    """
    # Enum members
    PEPTIDE = "PEPTIDE"
    INTERNAL = "INTERNAL"
    PRECURSOR = "PRECURSOR"
    IMMONIUM = "IMMONIUM"
    REFERENCE = "REFERENCE"
    NAMED_COMPOUND = "NAMED_COMPOUND"
    FORMULA = "FORMULA"
    SMILES = "SMILES"
    UNANNOTATED = "UNANNOTATED"

# Set metadata after class creation to avoid it becoming an enum member
PeakAnnotationSeriesLabel._metadata = {
    "PEPTIDE": {'description': 'Peptide fragment ion'},
    "INTERNAL": {'description': 'Internal fragment ion'},
    "PRECURSOR": {'description': 'Precursor ion'},
    "IMMONIUM": {'description': 'Immonium ion'},
    "REFERENCE": {'description': 'Reference peak or calibrant'},
    "NAMED_COMPOUND": {'description': 'Named chemical compound'},
    "FORMULA": {'description': 'Chemical formula'},
    "SMILES": {'description': 'SMILES structure notation'},
    "UNANNOTATED": {'description': 'Unannotated peak'},
}

class PeptideIonSeries(RichEnum):
    """
    Types of peptide fragment ion series in mass spectrometry
    """
    # Enum members
    B = "B"
    Y = "Y"
    A = "A"
    X = "X"
    C = "C"
    Z = "Z"
    D = "D"
    V = "V"
    W = "W"
    DA = "DA"
    DB = "DB"
    WA = "WA"
    WB = "WB"

# Set metadata after class creation to avoid it becoming an enum member
PeptideIonSeries._metadata = {
    "B": {'description': 'B ion series - N-terminal fragment with CO'},
    "Y": {'description': 'Y ion series - C-terminal fragment with H'},
    "A": {'description': 'A ion series - N-terminal fragment minus CO'},
    "X": {'description': 'X ion series - C-terminal fragment plus CO'},
    "C": {'description': 'C ion series - N-terminal fragment with NH3'},
    "Z": {'description': 'Z ion series - C-terminal fragment minus NH'},
    "D": {'description': 'D ion series - partial side chain cleavage'},
    "V": {'description': 'V ion series - side chain loss from y ion'},
    "W": {'description': 'W ion series - side chain loss from z ion'},
    "DA": {'description': 'DA ion series - a ion with side chain loss'},
    "DB": {'description': 'DB ion series - b ion with side chain loss'},
    "WA": {'description': 'WA ion series - a ion with tryptophan side chain loss'},
    "WB": {'description': 'WB ion series - b ion with tryptophan side chain loss'},
}

class MassErrorUnit(RichEnum):
    """
    Units for expressing mass error in mass spectrometry
    """
    # Enum members
    PPM = "PPM"
    DA = "DA"

# Set metadata after class creation to avoid it becoming an enum member
MassErrorUnit._metadata = {
    "PPM": {'description': 'Parts per million - relative mass error'},
    "DA": {'description': 'Dalton - absolute mass error', 'aliases': ['Dalton', 'u', 'amu']},
}

class InteractionDetectionMethod(RichEnum):
    """
    Methods used to detect molecular interactions
    """
    # Enum members
    TWO_HYBRID = "TWO_HYBRID"
    COIMMUNOPRECIPITATION = "COIMMUNOPRECIPITATION"
    PULL_DOWN = "PULL_DOWN"
    TANDEM_AFFINITY_PURIFICATION = "TANDEM_AFFINITY_PURIFICATION"
    FLUORESCENCE_RESONANCE_ENERGY_TRANSFER = "FLUORESCENCE_RESONANCE_ENERGY_TRANSFER"
    SURFACE_PLASMON_RESONANCE = "SURFACE_PLASMON_RESONANCE"
    CROSS_LINKING = "CROSS_LINKING"
    X_RAY_CRYSTALLOGRAPHY = "X_RAY_CRYSTALLOGRAPHY"
    NMR = "NMR"
    ELECTRON_MICROSCOPY = "ELECTRON_MICROSCOPY"
    MASS_SPECTROMETRY = "MASS_SPECTROMETRY"
    PROXIMITY_LIGATION_ASSAY = "PROXIMITY_LIGATION_ASSAY"
    BIMOLECULAR_FLUORESCENCE_COMPLEMENTATION = "BIMOLECULAR_FLUORESCENCE_COMPLEMENTATION"
    YEAST_TWO_HYBRID = "YEAST_TWO_HYBRID"
    MAMMALIAN_TWO_HYBRID = "MAMMALIAN_TWO_HYBRID"

# Set metadata after class creation to avoid it becoming an enum member
InteractionDetectionMethod._metadata = {
    "TWO_HYBRID": {'description': 'Classical two-hybrid system using transcriptional activity', 'meaning': 'MI:0018'},
    "COIMMUNOPRECIPITATION": {'description': 'Using antibody to capture bait and its ligands', 'meaning': 'MI:0019'},
    "PULL_DOWN": {'description': 'Affinity capture using immobilized bait', 'meaning': 'MI:0096'},
    "TANDEM_AFFINITY_PURIFICATION": {'description': 'TAP tagging for protein complex purification', 'meaning': 'MI:0676'},
    "FLUORESCENCE_RESONANCE_ENERGY_TRANSFER": {'description': 'FRET for detecting proximity between molecules', 'meaning': 'MI:0055', 'aliases': ['fluorescent resonance energy transfer']},
    "SURFACE_PLASMON_RESONANCE": {'description': 'SPR for real-time binding analysis', 'meaning': 'MI:0107'},
    "CROSS_LINKING": {'description': 'Chemical cross-linking of interacting proteins', 'meaning': 'MI:0030', 'aliases': ['cross-linking study']},
    "X_RAY_CRYSTALLOGRAPHY": {'description': 'Crystal structure determination', 'meaning': 'MI:0114'},
    "NMR": {'description': 'Nuclear magnetic resonance spectroscopy', 'meaning': 'MI:0077', 'aliases': ['nuclear magnetic resonance']},
    "ELECTRON_MICROSCOPY": {'description': 'EM for structural determination', 'meaning': 'MI:0040'},
    "MASS_SPECTROMETRY": {'description': 'MS-based interaction detection', 'meaning': 'MI:0943', 'aliases': ['detection by mass spectrometry']},
    "PROXIMITY_LIGATION_ASSAY": {'description': 'PLA for detecting protein proximity', 'meaning': 'MI:0813'},
    "BIMOLECULAR_FLUORESCENCE_COMPLEMENTATION": {'description': 'BiFC split fluorescent protein assay', 'meaning': 'MI:0809'},
    "YEAST_TWO_HYBRID": {'description': 'Y2H screening in yeast', 'meaning': 'MI:0018', 'aliases': ['two hybrid']},
    "MAMMALIAN_TWO_HYBRID": {'description': 'Two-hybrid in mammalian cells', 'meaning': 'MI:2413', 'aliases': ['mammalian membrane two hybrid']},
}

class InteractionType(RichEnum):
    """
    Types of molecular interactions
    """
    # Enum members
    PHYSICAL_ASSOCIATION = "PHYSICAL_ASSOCIATION"
    DIRECT_INTERACTION = "DIRECT_INTERACTION"
    ASSOCIATION = "ASSOCIATION"
    COLOCALIZATION = "COLOCALIZATION"
    FUNCTIONAL_ASSOCIATION = "FUNCTIONAL_ASSOCIATION"
    ENZYMATIC_REACTION = "ENZYMATIC_REACTION"
    PHOSPHORYLATION_REACTION = "PHOSPHORYLATION_REACTION"
    UBIQUITINATION_REACTION = "UBIQUITINATION_REACTION"
    ACETYLATION_REACTION = "ACETYLATION_REACTION"
    METHYLATION_REACTION = "METHYLATION_REACTION"
    CLEAVAGE_REACTION = "CLEAVAGE_REACTION"
    GENETIC_INTERACTION = "GENETIC_INTERACTION"
    SELF_INTERACTION = "SELF_INTERACTION"

# Set metadata after class creation to avoid it becoming an enum member
InteractionType._metadata = {
    "PHYSICAL_ASSOCIATION": {'description': 'Molecules within the same physical complex', 'meaning': 'MI:0915'},
    "DIRECT_INTERACTION": {'description': 'Direct physical contact between molecules', 'meaning': 'MI:0407'},
    "ASSOCIATION": {'description': 'May form one or more physical complexes', 'meaning': 'MI:0914'},
    "COLOCALIZATION": {'description': 'Coincident occurrence in subcellular location', 'meaning': 'MI:0403'},
    "FUNCTIONAL_ASSOCIATION": {'description': 'Functional modulation without direct contact', 'meaning': 'MI:2286'},
    "ENZYMATIC_REACTION": {'description': 'Enzyme-substrate relationship', 'meaning': 'MI:0414'},
    "PHOSPHORYLATION_REACTION": {'description': 'Kinase-substrate phosphorylation', 'meaning': 'MI:0217'},
    "UBIQUITINATION_REACTION": {'description': 'Ubiquitin ligase-substrate relationship', 'meaning': 'MI:0220'},
    "ACETYLATION_REACTION": {'description': 'Acetyltransferase-substrate relationship', 'meaning': 'MI:0192'},
    "METHYLATION_REACTION": {'description': 'Methyltransferase-substrate relationship', 'meaning': 'MI:0213'},
    "CLEAVAGE_REACTION": {'description': 'Protease-substrate relationship', 'meaning': 'MI:0194'},
    "GENETIC_INTERACTION": {'description': 'Genetic epistatic relationship', 'meaning': 'MI:0208', 'aliases': ['genetic interaction (sensu unexpected)']},
    "SELF_INTERACTION": {'description': 'Intra-molecular interaction', 'meaning': 'MI:1126'},
}

class ExperimentalRole(RichEnum):
    """
    Role played by a participant in the experiment
    """
    # Enum members
    BAIT = "BAIT"
    PREY = "PREY"
    NEUTRAL_COMPONENT = "NEUTRAL_COMPONENT"
    ENZYME = "ENZYME"
    ENZYME_TARGET = "ENZYME_TARGET"
    SELF = "SELF"
    PUTATIVE_SELF = "PUTATIVE_SELF"
    ANCILLARY = "ANCILLARY"
    COFACTOR = "COFACTOR"
    INHIBITOR = "INHIBITOR"
    STIMULATOR = "STIMULATOR"
    COMPETITOR = "COMPETITOR"

# Set metadata after class creation to avoid it becoming an enum member
ExperimentalRole._metadata = {
    "BAIT": {'description': 'Molecule used to capture interacting partners', 'meaning': 'MI:0496'},
    "PREY": {'description': 'Molecule captured by the bait', 'meaning': 'MI:0498'},
    "NEUTRAL_COMPONENT": {'description': 'Participant with no specific role', 'meaning': 'MI:0497'},
    "ENZYME": {'description': 'Catalytically active participant', 'meaning': 'MI:0501'},
    "ENZYME_TARGET": {'description': 'Target of enzymatic activity', 'meaning': 'MI:0502'},
    "SELF": {'description': 'Self-interaction participant', 'meaning': 'MI:0503'},
    "PUTATIVE_SELF": {'description': 'Potentially self-interacting', 'meaning': 'MI:0898'},
    "ANCILLARY": {'description': 'Supporting but not directly interacting', 'meaning': 'MI:0684'},
    "COFACTOR": {'description': 'Required cofactor for interaction', 'meaning': 'MI:0682'},
    "INHIBITOR": {'description': 'Inhibitor of the interaction', 'meaning': 'MI:0586'},
    "STIMULATOR": {'description': 'Enhancer of the interaction', 'meaning': 'MI:0840'},
    "COMPETITOR": {'description': 'Competitive inhibitor', 'meaning': 'MI:0941'},
}

class BiologicalRole(RichEnum):
    """
    Physiological role of an interactor
    """
    # Enum members
    ENZYME = "ENZYME"
    ENZYME_TARGET = "ENZYME_TARGET"
    ELECTRON_DONOR = "ELECTRON_DONOR"
    ELECTRON_ACCEPTOR = "ELECTRON_ACCEPTOR"
    INHIBITOR = "INHIBITOR"
    COFACTOR = "COFACTOR"
    LIGAND = "LIGAND"
    AGONIST = "AGONIST"
    ANTAGONIST = "ANTAGONIST"
    PHOSPHATE_DONOR = "PHOSPHATE_DONOR"
    PHOSPHATE_ACCEPTOR = "PHOSPHATE_ACCEPTOR"

# Set metadata after class creation to avoid it becoming an enum member
BiologicalRole._metadata = {
    "ENZYME": {'description': 'Catalytically active molecule', 'meaning': 'MI:0501'},
    "ENZYME_TARGET": {'description': 'Substrate of enzymatic activity', 'meaning': 'MI:0502'},
    "ELECTRON_DONOR": {'description': 'Donates electrons in reaction', 'meaning': 'MI:0579'},
    "ELECTRON_ACCEPTOR": {'description': 'Accepts electrons in reaction', 'meaning': 'MI:0580'},
    "INHIBITOR": {'description': 'Inhibits activity or interaction', 'meaning': 'MI:0586'},
    "COFACTOR": {'description': 'Required for activity', 'meaning': 'MI:0682'},
    "LIGAND": {'description': 'Small molecule binding partner'},
    "AGONIST": {'description': 'Activates receptor', 'meaning': 'MI:0625'},
    "ANTAGONIST": {'description': 'Blocks receptor activation', 'meaning': 'MI:0626'},
    "PHOSPHATE_DONOR": {'description': 'Provides phosphate group', 'meaning': 'MI:0842'},
    "PHOSPHATE_ACCEPTOR": {'description': 'Receives phosphate group', 'meaning': 'MI:0843'},
}

class ParticipantIdentificationMethod(RichEnum):
    """
    Methods to identify interaction participants
    """
    # Enum members
    MASS_SPECTROMETRY = "MASS_SPECTROMETRY"
    WESTERN_BLOT = "WESTERN_BLOT"
    SEQUENCE_TAG_IDENTIFICATION = "SEQUENCE_TAG_IDENTIFICATION"
    ANTIBODY_DETECTION = "ANTIBODY_DETECTION"
    PREDETERMINED = "PREDETERMINED"
    NUCLEIC_ACID_SEQUENCING = "NUCLEIC_ACID_SEQUENCING"
    PROTEIN_SEQUENCING = "PROTEIN_SEQUENCING"

# Set metadata after class creation to avoid it becoming an enum member
ParticipantIdentificationMethod._metadata = {
    "MASS_SPECTROMETRY": {'description': 'MS-based protein identification', 'meaning': 'MI:0943', 'aliases': ['detection by mass spectrometry']},
    "WESTERN_BLOT": {'description': 'Antibody-based detection', 'meaning': 'MI:0113'},
    "SEQUENCE_TAG_IDENTIFICATION": {'description': 'Using affinity tags', 'meaning': 'MI:0102'},
    "ANTIBODY_DETECTION": {'description': 'Direct antibody recognition', 'meaning': 'MI:0678', 'aliases': ['antibody array']},
    "PREDETERMINED": {'description': 'Known from experimental design', 'meaning': 'MI:0396', 'aliases': ['predetermined participant']},
    "NUCLEIC_ACID_SEQUENCING": {'description': 'DNA/RNA sequencing', 'meaning': 'MI:0078', 'aliases': ['nucleotide sequence identification']},
    "PROTEIN_SEQUENCING": {'description': 'Direct protein sequencing'},
}

class FeatureType(RichEnum):
    """
    Molecular features affecting interactions
    """
    # Enum members
    BINDING_SITE = "BINDING_SITE"
    MUTATION = "MUTATION"
    POST_TRANSLATIONAL_MODIFICATION = "POST_TRANSLATIONAL_MODIFICATION"
    TAG = "TAG"
    CROSS_LINK = "CROSS_LINK"
    LIPIDATION_SITE = "LIPIDATION_SITE"
    PHOSPHORYLATION_SITE = "PHOSPHORYLATION_SITE"
    UBIQUITINATION_SITE = "UBIQUITINATION_SITE"
    METHYLATION_SITE = "METHYLATION_SITE"
    ACETYLATION_SITE = "ACETYLATION_SITE"
    SUMOYLATION_SITE = "SUMOYLATION_SITE"
    NECESSARY_BINDING_REGION = "NECESSARY_BINDING_REGION"
    SUFFICIENT_BINDING_REGION = "SUFFICIENT_BINDING_REGION"

# Set metadata after class creation to avoid it becoming an enum member
FeatureType._metadata = {
    "BINDING_SITE": {'description': 'Region involved in binding', 'meaning': 'MI:0117', 'aliases': ['binding-associated region']},
    "MUTATION": {'description': 'Sequence alteration', 'meaning': 'MI:0118'},
    "POST_TRANSLATIONAL_MODIFICATION": {'description': 'PTM site', 'meaning': 'MI:0121', 'aliases': ['acetylated residue']},
    "TAG": {'description': 'Affinity or epitope tag', 'meaning': 'MI:0507'},
    "CROSS_LINK": {'description': 'Cross-linking site'},
    "LIPIDATION_SITE": {'description': 'Lipid modification site'},
    "PHOSPHORYLATION_SITE": {'description': 'Phosphorylated residue', 'meaning': 'MI:0170', 'aliases': ['phosphorylated residue']},
    "UBIQUITINATION_SITE": {'description': 'Ubiquitinated residue'},
    "METHYLATION_SITE": {'description': 'Methylated residue'},
    "ACETYLATION_SITE": {'description': 'Acetylated residue'},
    "SUMOYLATION_SITE": {'description': 'SUMOylated residue'},
    "NECESSARY_BINDING_REGION": {'description': 'Required for binding', 'meaning': 'MI:0429'},
    "SUFFICIENT_BINDING_REGION": {'description': 'Sufficient for binding', 'meaning': 'MI:0442'},
}

class InteractorType(RichEnum):
    """
    Types of molecular species in interactions
    """
    # Enum members
    PROTEIN = "PROTEIN"
    PEPTIDE = "PEPTIDE"
    SMALL_MOLECULE = "SMALL_MOLECULE"
    DNA = "DNA"
    RNA = "RNA"
    PROTEIN_COMPLEX = "PROTEIN_COMPLEX"
    GENE = "GENE"
    BIOPOLYMER = "BIOPOLYMER"
    POLYSACCHARIDE = "POLYSACCHARIDE"
    LIPID = "LIPID"
    NUCLEIC_ACID = "NUCLEIC_ACID"
    SYNTHETIC_POLYMER = "SYNTHETIC_POLYMER"
    METAL_ION = "METAL_ION"

# Set metadata after class creation to avoid it becoming an enum member
InteractorType._metadata = {
    "PROTEIN": {'description': 'Polypeptide molecule', 'meaning': 'MI:0326'},
    "PEPTIDE": {'description': 'Short polypeptide', 'meaning': 'MI:0327'},
    "SMALL_MOLECULE": {'description': 'Small chemical compound', 'meaning': 'MI:0328'},
    "DNA": {'description': 'Deoxyribonucleic acid', 'meaning': 'MI:0319', 'aliases': ['deoxyribonucleic acid']},
    "RNA": {'description': 'Ribonucleic acid', 'meaning': 'MI:0320', 'aliases': ['ribonucleic acid']},
    "PROTEIN_COMPLEX": {'description': 'Multi-protein assembly', 'meaning': 'MI:0314', 'aliases': ['complex']},
    "GENE": {'description': 'Gene locus', 'meaning': 'MI:0250'},
    "BIOPOLYMER": {'description': 'Biological polymer', 'meaning': 'MI:0383'},
    "POLYSACCHARIDE": {'description': 'Carbohydrate polymer', 'meaning': 'MI:0904'},
    "LIPID": {'description': 'Lipid molecule'},
    "NUCLEIC_ACID": {'description': 'DNA or RNA', 'meaning': 'MI:0318'},
    "SYNTHETIC_POLYMER": {'description': 'Artificial polymer'},
    "METAL_ION": {'description': 'Metal ion cofactor'},
}

class ConfidenceScore(RichEnum):
    """
    Types of confidence scoring methods
    """
    # Enum members
    INTACT_MISCORE = "INTACT_MISCORE"
    AUTHOR_CONFIDENCE = "AUTHOR_CONFIDENCE"
    INTACT_CONFIDENCE = "INTACT_CONFIDENCE"
    MINT_SCORE = "MINT_SCORE"
    MATRIXDB_SCORE = "MATRIXDB_SCORE"

# Set metadata after class creation to avoid it becoming an enum member
ConfidenceScore._metadata = {
    "INTACT_MISCORE": {'description': 'IntAct molecular interaction score'},
    "AUTHOR_CONFIDENCE": {'description': 'Author-provided confidence', 'meaning': 'MI:0621'},
    "INTACT_CONFIDENCE": {'description': 'IntAct curation confidence'},
    "MINT_SCORE": {'description': 'MINT database score'},
    "MATRIXDB_SCORE": {'description': 'MatrixDB confidence score'},
}

class ExperimentalPreparation(RichEnum):
    """
    Sample preparation methods
    """
    # Enum members
    RECOMBINANT_EXPRESSION = "RECOMBINANT_EXPRESSION"
    NATIVE_SOURCE = "NATIVE_SOURCE"
    IN_VITRO_EXPRESSION = "IN_VITRO_EXPRESSION"
    OVEREXPRESSION = "OVEREXPRESSION"
    KNOCKDOWN = "KNOCKDOWN"
    KNOCKOUT = "KNOCKOUT"
    ENDOGENOUS_LEVEL = "ENDOGENOUS_LEVEL"

# Set metadata after class creation to avoid it becoming an enum member
ExperimentalPreparation._metadata = {
    "RECOMBINANT_EXPRESSION": {'description': 'Expressed in heterologous system'},
    "NATIVE_SOURCE": {'description': 'From original organism'},
    "IN_VITRO_EXPRESSION": {'description': 'Cell-free expression'},
    "OVEREXPRESSION": {'description': 'Above physiological levels', 'meaning': 'MI:0506', 'aliases': ['over expressed level']},
    "KNOCKDOWN": {'description': 'Reduced expression'},
    "KNOCKOUT": {'description': 'Gene deletion', 'meaning': 'MI:0788', 'aliases': ['knock out']},
    "ENDOGENOUS_LEVEL": {'description': 'Physiological expression'},
}

class BioticInteractionType(RichEnum):
    """
    Types of biotic interactions between organisms, based on RO:0002437 (biotically interacts with). These represent ecological relationships where at least one partner is an organism.

    """
    # Enum members
    BIOTICALLY_INTERACTS_WITH = "BIOTICALLY_INTERACTS_WITH"
    TROPHICALLY_INTERACTS_WITH = "TROPHICALLY_INTERACTS_WITH"
    PREYS_ON = "PREYS_ON"
    PREYED_UPON_BY = "PREYED_UPON_BY"
    EATS = "EATS"
    IS_EATEN_BY = "IS_EATEN_BY"
    ACQUIRES_NUTRIENTS_FROM = "ACQUIRES_NUTRIENTS_FROM"
    PROVIDES_NUTRIENTS_FOR = "PROVIDES_NUTRIENTS_FOR"
    SYMBIOTICALLY_INTERACTS_WITH = "SYMBIOTICALLY_INTERACTS_WITH"
    COMMENSUALLY_INTERACTS_WITH = "COMMENSUALLY_INTERACTS_WITH"
    MUTUALISTICALLY_INTERACTS_WITH = "MUTUALISTICALLY_INTERACTS_WITH"
    INTERACTS_VIA_PARASITE_HOST = "INTERACTS_VIA_PARASITE_HOST"
    SYMBIOTROPHICALLY_INTERACTS_WITH = "SYMBIOTROPHICALLY_INTERACTS_WITH"
    PARASITE_OF = "PARASITE_OF"
    HOST_OF = "HOST_OF"
    HAS_HOST = "HAS_HOST"
    PARASITOID_OF = "PARASITOID_OF"
    ECTOPARASITE_OF = "ECTOPARASITE_OF"
    ENDOPARASITE_OF = "ENDOPARASITE_OF"
    INTRACELLULAR_ENDOPARASITE_OF = "INTRACELLULAR_ENDOPARASITE_OF"
    INTERCELLULAR_ENDOPARASITE_OF = "INTERCELLULAR_ENDOPARASITE_OF"
    HEMIPARASITE_OF = "HEMIPARASITE_OF"
    STEM_PARASITE_OF = "STEM_PARASITE_OF"
    ROOT_PARASITE_OF = "ROOT_PARASITE_OF"
    OBLIGATE_PARASITE_OF = "OBLIGATE_PARASITE_OF"
    FACULTATIVE_PARASITE_OF = "FACULTATIVE_PARASITE_OF"
    TROPHIC_PARASITE_OF = "TROPHIC_PARASITE_OF"
    PATHOGEN_OF = "PATHOGEN_OF"
    HAS_PATHOGEN = "HAS_PATHOGEN"
    RESERVOIR_HOST_OF = "RESERVOIR_HOST_OF"
    HAS_RESERVOIR_HOST = "HAS_RESERVOIR_HOST"
    IS_VECTOR_FOR = "IS_VECTOR_FOR"
    POLLINATES = "POLLINATES"
    PARTICIPATES_IN_ABIOTIC_BIOTIC_INTERACTION_WITH = "PARTICIPATES_IN_ABIOTIC_BIOTIC_INTERACTION_WITH"
    ECOLOGICALLY_CO_OCCURS_WITH = "ECOLOGICALLY_CO_OCCURS_WITH"
    HYPERPARASITE_OF = "HYPERPARASITE_OF"
    MESOPARASITE_OF = "MESOPARASITE_OF"
    KLEPTOPARASITE_OF = "KLEPTOPARASITE_OF"
    EPIPHYTE_OF = "EPIPHYTE_OF"
    ALLELOPATH_OF = "ALLELOPATH_OF"
    VISITS = "VISITS"
    VISITS_FLOWERS_OF = "VISITS_FLOWERS_OF"
    HAS_FLOWERS_VISITED_BY = "HAS_FLOWERS_VISITED_BY"
    LAYS_EGGS_IN = "LAYS_EGGS_IN"
    HAS_EGGS_LAID_IN_BY = "HAS_EGGS_LAID_IN_BY"
    LAYS_EGGS_ON = "LAYS_EGGS_ON"
    HAS_EGGS_LAID_ON_BY = "HAS_EGGS_LAID_ON_BY"
    CREATES_HABITAT_FOR = "CREATES_HABITAT_FOR"

# Set metadata after class creation to avoid it becoming an enum member
BioticInteractionType._metadata = {
    "BIOTICALLY_INTERACTS_WITH": {'description': 'An interaction relationship in which at least one of the partners is an organism and the other is either an organism or an abiotic entity with which the organism interacts.\n', 'meaning': 'RO:0002437'},
    "TROPHICALLY_INTERACTS_WITH": {'description': 'An interaction relationship in which the partners are related via a feeding relationship.', 'meaning': 'RO:0002438'},
    "PREYS_ON": {'description': 'An interaction relationship involving a predation process, where the subject kills the target in order to eat it or to feed to siblings, offspring or group members.\n', 'meaning': 'RO:0002439'},
    "PREYED_UPON_BY": {'description': 'Inverse of preys on', 'meaning': 'RO:0002458'},
    "EATS": {'description': 'A biotic interaction where one organism consumes a material entity through a type of mouth or other oral opening.\n', 'meaning': 'RO:0002470'},
    "IS_EATEN_BY": {'description': 'Inverse of eats', 'meaning': 'RO:0002471'},
    "ACQUIRES_NUTRIENTS_FROM": {'description': 'Inverse of provides nutrients for', 'meaning': 'RO:0002457'},
    "PROVIDES_NUTRIENTS_FOR": {'description': 'A biotic interaction where a material entity provides nutrition for an organism.', 'meaning': 'RO:0002469'},
    "SYMBIOTICALLY_INTERACTS_WITH": {'description': 'A biotic interaction in which the two organisms live together in more or less intimate association.\n', 'meaning': 'RO:0002440'},
    "COMMENSUALLY_INTERACTS_WITH": {'description': 'An interaction relationship between two organisms living together in more or less intimate association in a relationship in which one benefits and the other is unaffected.\n', 'meaning': 'RO:0002441'},
    "MUTUALISTICALLY_INTERACTS_WITH": {'description': 'An interaction relationship between two organisms living together in more or less intimate association in a relationship in which both organisms benefit from each other.\n', 'meaning': 'RO:0002442'},
    "INTERACTS_VIA_PARASITE_HOST": {'description': 'An interaction relationship between two organisms living together in more or less intimate association in a relationship in which association is disadvantageous or destructive to one of the organisms.\n', 'meaning': 'RO:0002443'},
    "SYMBIOTROPHICALLY_INTERACTS_WITH": {'description': 'A trophic interaction in which one organism acquires nutrients through a symbiotic relationship with another organism.\n', 'meaning': 'RO:0008510'},
    "PARASITE_OF": {'description': 'A parasite-host relationship where an organism benefits at the expense of another.', 'meaning': 'RO:0002444'},
    "HOST_OF": {'description': 'Inverse of has host', 'meaning': 'RO:0002453'},
    "HAS_HOST": {'description': "X 'has host' y if and only if: x is an organism, y is an organism, and x can live on the surface of or within the body of y.\n", 'meaning': 'RO:0002454'},
    "PARASITOID_OF": {'description': 'A parasite that kills or sterilizes its host', 'meaning': 'RO:0002208'},
    "ECTOPARASITE_OF": {'description': 'A sub-relation of parasite-of in which the parasite lives on or in the integumental system of the host.\n', 'meaning': 'RO:0002632'},
    "ENDOPARASITE_OF": {'description': 'A parasite that lives inside its host', 'meaning': 'RO:0002634'},
    "INTRACELLULAR_ENDOPARASITE_OF": {'description': 'A sub-relation of endoparasite-of in which the parasite inhabits host cells.', 'meaning': 'RO:0002640'},
    "INTERCELLULAR_ENDOPARASITE_OF": {'description': 'A sub-relation of endoparasite-of in which the parasite inhabits the spaces between host cells.\n', 'meaning': 'RO:0002638'},
    "HEMIPARASITE_OF": {'description': 'A sub-relation of parasite-of in which the parasite is a plant, and the parasite is parasitic under natural conditions and is also photosynthetic to some degree.\n', 'meaning': 'RO:0002237'},
    "STEM_PARASITE_OF": {'description': 'A parasite-of relationship in which the host is a plant and the parasite that attaches to the host stem.\n', 'meaning': 'RO:0002235'},
    "ROOT_PARASITE_OF": {'description': 'A parasite-of relationship in which the host is a plant and the parasite that attaches to the host root.\n', 'meaning': 'RO:0002236'},
    "OBLIGATE_PARASITE_OF": {'description': 'A sub-relation of parasite-of in which the parasite that cannot complete its life cycle without a host.\n', 'meaning': 'RO:0002227'},
    "FACULTATIVE_PARASITE_OF": {'description': 'A sub-relations of parasite-of in which the parasite that can complete its life cycle independent of a host.\n', 'meaning': 'RO:0002228'},
    "TROPHIC_PARASITE_OF": {'description': 'A symbiotrophic interaction in which one organism acquires nutrients through a parasitic relationship with another organism.\n', 'meaning': 'RO:0008511'},
    "PATHOGEN_OF": {'description': 'Inverse of has pathogen', 'meaning': 'RO:0002556'},
    "HAS_PATHOGEN": {'description': 'A host interaction where the smaller of the two members of a symbiosis causes a disease in the larger member.\n', 'meaning': 'RO:0002557'},
    "RESERVOIR_HOST_OF": {'description': 'A relation between a host organism and a hosted organism in which the hosted organism naturally occurs in an indefinitely maintained reservoir provided by the host.\n', 'meaning': 'RO:0002802'},
    "HAS_RESERVOIR_HOST": {'description': 'Inverse of reservoir host of', 'meaning': 'RO:0002803'},
    "IS_VECTOR_FOR": {'description': 'Organism acts as a vector for transmitting another organism', 'meaning': 'RO:0002459'},
    "POLLINATES": {'description': 'An interaction where an organism transfers pollen to a plant', 'meaning': 'RO:0002455'},
    "PARTICIPATES_IN_ABIOTIC_BIOTIC_INTERACTION_WITH": {'description': 'A biotic interaction relationship in which one partner is an organism and the other partner is inorganic. For example, the relationship between a sponge and the substrate to which is it anchored.\n', 'meaning': 'RO:0002446'},
    "ECOLOGICALLY_CO_OCCURS_WITH": {'description': 'An interaction relationship describing organisms that often occur together at the same time and space or in the same environment.\n', 'meaning': 'RO:0008506'},
    "HYPERPARASITE_OF": {'description': 'x is a hyperparasite of y iff x is a parasite of a parasite of the target organism y', 'meaning': 'RO:0002553'},
    "MESOPARASITE_OF": {'description': 'A sub-relation of parasite-of in which the parasite is partially an endoparasite and partially an ectoparasite.\n', 'meaning': 'RO:0002636'},
    "KLEPTOPARASITE_OF": {'description': 'A sub-relation of parasite of in which a parasite steals resources from another organism, usually food or nest material.\n', 'meaning': 'RO:0008503'},
    "EPIPHYTE_OF": {'description': 'An interaction relationship wherein a plant or algae is living on the outside surface of another plant.\n', 'meaning': 'RO:0008501'},
    "ALLELOPATH_OF": {'description': 'A relationship between organisms where one organism is influenced by the biochemicals produced by another. Allelopathy is a phenomenon in which one organism releases chemicals to positively or negatively influence the growth, survival or reproduction of other organisms in its vicinity.\n', 'meaning': 'RO:0002555'},
    "VISITS": {'description': 'An interaction where an organism visits another organism or location', 'meaning': 'RO:0002618'},
    "VISITS_FLOWERS_OF": {'description': 'An interaction where an organism visits the flowers of a plant', 'meaning': 'RO:0002622'},
    "HAS_FLOWERS_VISITED_BY": {'description': 'Inverse of visits flowers of', 'meaning': 'RO:0002623'},
    "LAYS_EGGS_IN": {'description': 'An interaction where an organism deposits eggs inside another organism', 'meaning': 'RO:0002624'},
    "HAS_EGGS_LAID_IN_BY": {'description': 'Inverse of lays eggs in', 'meaning': 'RO:0002625'},
    "LAYS_EGGS_ON": {'description': 'An interaction relationship in which organism a lays eggs on the outside surface of organism b. Organism b is neither helped nor harmed in the process of egg laying or incubation.\n', 'meaning': 'RO:0008507'},
    "HAS_EGGS_LAID_ON_BY": {'description': 'Inverse of lays eggs on', 'meaning': 'RO:0008508'},
    "CREATES_HABITAT_FOR": {'description': 'An interaction relationship wherein one organism creates a structure or environment that is lived in by another organism.\n', 'meaning': 'RO:0008505'},
}

class MineralogyFeedstockClass(RichEnum):
    """
    Types of mineral feedstock sources for extraction and processing operations, including primary and secondary sources.

    """
    # Enum members
    HARDROCK_PRIMARY = "HARDROCK_PRIMARY"
    TAILINGS_LEGACY = "TAILINGS_LEGACY"
    WASTE_PILES = "WASTE_PILES"
    COAL_BYPRODUCT = "COAL_BYPRODUCT"
    E_WASTE = "E_WASTE"
    BRINES = "BRINES"

# Set metadata after class creation to avoid it becoming an enum member
MineralogyFeedstockClass._metadata = {
    "HARDROCK_PRIMARY": {'description': 'Primary ore from hardrock mining operations'},
    "TAILINGS_LEGACY": {'description': 'Historical mine tailings available for reprocessing'},
    "WASTE_PILES": {'description': 'Accumulated mining waste materials'},
    "COAL_BYPRODUCT": {'description': 'Byproducts from coal mining and processing'},
    "E_WASTE": {'description': 'Electronic waste containing recoverable metals'},
    "BRINES": {'description': 'Saline water sources containing dissolved minerals'},
}

class BeneficiationPathway(RichEnum):
    """
    Methods for mineral separation and concentration aligned with advanced ore processing initiatives (AOI-2).

    """
    # Enum members
    ORE_SORTING = "ORE_SORTING"
    DENSE_MEDIUM_SEPARATION = "DENSE_MEDIUM_SEPARATION"
    MICROWAVE_PREWEAKENING = "MICROWAVE_PREWEAKENING"
    ELECTRIC_PULSE_PREWEAKENING = "ELECTRIC_PULSE_PREWEAKENING"
    GRINDING_DYNAMIC = "GRINDING_DYNAMIC"
    ELECTROSTATIC_SEP = "ELECTROSTATIC_SEP"
    MAGNETIC_SEP = "MAGNETIC_SEP"
    FLOTATION_LOW_H2O = "FLOTATION_LOW_H2O"
    BIO_BENEFICIATION = "BIO_BENEFICIATION"

# Set metadata after class creation to avoid it becoming an enum member
BeneficiationPathway._metadata = {
    "ORE_SORTING": {'description': 'Sensor-based sorting of ore particles'},
    "DENSE_MEDIUM_SEPARATION": {'description': 'Gravity separation using dense media'},
    "MICROWAVE_PREWEAKENING": {'description': 'Microwave treatment to weaken ore structure'},
    "ELECTRIC_PULSE_PREWEAKENING": {'description': 'High-voltage electric pulse fragmentation'},
    "GRINDING_DYNAMIC": {'description': 'Dynamic grinding optimization systems'},
    "ELECTROSTATIC_SEP": {'description': 'Electrostatic separation of minerals'},
    "MAGNETIC_SEP": {'description': 'Magnetic separation of ferromagnetic minerals'},
    "FLOTATION_LOW_H2O": {'description': 'Low-water flotation processes'},
    "BIO_BENEFICIATION": {'description': 'Biological methods for mineral beneficiation'},
}

class InSituChemistryRegime(RichEnum):
    """
    Chemical leaching systems for in-situ extraction with associated parameters including pH, Eh, temperature, and ionic strength.

    """
    # Enum members
    ACIDIC_SULFATE = "ACIDIC_SULFATE"
    ACIDIC_CHLORIDE = "ACIDIC_CHLORIDE"
    AMMONIA_BASED = "AMMONIA_BASED"
    ORGANIC_ACID = "ORGANIC_ACID"
    BIOLEACH_SULFUR_OXIDIZING = "BIOLEACH_SULFUR_OXIDIZING"
    BIOLEACH_IRON_OXIDIZING = "BIOLEACH_IRON_OXIDIZING"

# Set metadata after class creation to avoid it becoming an enum member
InSituChemistryRegime._metadata = {
    "ACIDIC_SULFATE": {'description': 'Sulfuric acid-based leaching system'},
    "ACIDIC_CHLORIDE": {'description': 'Hydrochloric acid or chloride-based leaching'},
    "AMMONIA_BASED": {'description': 'Ammonia or ammonium-based leaching system'},
    "ORGANIC_ACID": {'description': 'Organic acid leaching (citric, oxalic, etc.)'},
    "BIOLEACH_SULFUR_OXIDIZING": {'description': 'Bioleaching using sulfur-oxidizing bacteria'},
    "BIOLEACH_IRON_OXIDIZING": {'description': 'Bioleaching using iron-oxidizing bacteria'},
}

class ExtractableTargetElement(RichEnum):
    """
    Target elements for extraction, particularly rare earth elements (REE) and critical minerals.

    """
    # Enum members
    REE_LA = "REE_LA"
    REE_CE = "REE_CE"
    REE_PR = "REE_PR"
    REE_ND = "REE_ND"
    REE_PM = "REE_PM"
    REE_SM = "REE_SM"
    REE_EU = "REE_EU"
    REE_GD = "REE_GD"
    REE_TB = "REE_TB"
    REE_DY = "REE_DY"
    REE_HO = "REE_HO"
    REE_ER = "REE_ER"
    REE_TM = "REE_TM"
    REE_YB = "REE_YB"
    REE_LU = "REE_LU"
    SC = "SC"
    CO = "CO"
    NI = "NI"
    LI = "LI"

# Set metadata after class creation to avoid it becoming an enum member
ExtractableTargetElement._metadata = {
    "REE_LA": {'description': 'Lanthanum'},
    "REE_CE": {'description': 'Cerium'},
    "REE_PR": {'description': 'Praseodymium'},
    "REE_ND": {'description': 'Neodymium'},
    "REE_PM": {'description': 'Promethium'},
    "REE_SM": {'description': 'Samarium'},
    "REE_EU": {'description': 'Europium'},
    "REE_GD": {'description': 'Gadolinium'},
    "REE_TB": {'description': 'Terbium'},
    "REE_DY": {'description': 'Dysprosium'},
    "REE_HO": {'description': 'Holmium'},
    "REE_ER": {'description': 'Erbium'},
    "REE_TM": {'description': 'Thulium'},
    "REE_YB": {'description': 'Ytterbium'},
    "REE_LU": {'description': 'Lutetium'},
    "SC": {'description': 'Scandium'},
    "CO": {'description': 'Cobalt'},
    "NI": {'description': 'Nickel'},
    "LI": {'description': 'Lithium'},
}

class SensorWhileDrillingFeature(RichEnum):
    """
    Measurement while drilling (MWD) and logging while drilling (LWD) features for orebody ML and geosteering applications.

    """
    # Enum members
    WOB = "WOB"
    ROP = "ROP"
    TORQUE = "TORQUE"
    MWD_GAMMA = "MWD_GAMMA"
    MWD_RESISTIVITY = "MWD_RESISTIVITY"
    MUD_LOSS = "MUD_LOSS"
    VIBRATION = "VIBRATION"
    RSS_ANGLE = "RSS_ANGLE"

# Set metadata after class creation to avoid it becoming an enum member
SensorWhileDrillingFeature._metadata = {
    "WOB": {'description': 'Weight on bit measurement'},
    "ROP": {'description': 'Rate of penetration'},
    "TORQUE": {'description': 'Rotational torque measurement'},
    "MWD_GAMMA": {'description': 'Gamma ray logging while drilling'},
    "MWD_RESISTIVITY": {'description': 'Resistivity logging while drilling'},
    "MUD_LOSS": {'description': 'Drilling mud loss measurement'},
    "VIBRATION": {'description': 'Drill string vibration monitoring'},
    "RSS_ANGLE": {'description': 'Rotary steerable system angle'},
}

class ProcessPerformanceMetric(RichEnum):
    """
    Key performance indicators for mining and processing operations tied to SMART milestones and sustainability goals.

    """
    # Enum members
    RECOVERY_PCT = "RECOVERY_PCT"
    SELECTIVITY_INDEX = "SELECTIVITY_INDEX"
    SPECIFIC_ENERGY_KWH_T = "SPECIFIC_ENERGY_KWH_T"
    WATER_INTENSITY_L_T = "WATER_INTENSITY_L_T"
    REAGENT_INTENSITY_KG_T = "REAGENT_INTENSITY_KG_T"
    CO2E_KG_T = "CO2E_KG_T"
    TAILINGS_MASS_REDUCTION_PCT = "TAILINGS_MASS_REDUCTION_PCT"

# Set metadata after class creation to avoid it becoming an enum member
ProcessPerformanceMetric._metadata = {
    "RECOVERY_PCT": {'description': 'Percentage recovery of target material'},
    "SELECTIVITY_INDEX": {'description': 'Selectivity index for separation processes'},
    "SPECIFIC_ENERGY_KWH_T": {'description': 'Specific energy consumption in kWh per tonne'},
    "WATER_INTENSITY_L_T": {'description': 'Water usage intensity in liters per tonne'},
    "REAGENT_INTENSITY_KG_T": {'description': 'Reagent consumption in kg per tonne'},
    "CO2E_KG_T": {'description': 'CO2 equivalent emissions in kg per tonne'},
    "TAILINGS_MASS_REDUCTION_PCT": {'description': 'Percentage reduction in tailings mass'},
}

class BioleachOrganism(RichEnum):
    """
    Microorganisms used in bioleaching and biomining operations, including engineered strains.

    """
    # Enum members
    ACIDITHIOBACILLUS_FERROOXIDANS = "ACIDITHIOBACILLUS_FERROOXIDANS"
    LEPTOSPIRILLUM_FERROOXIDANS = "LEPTOSPIRILLUM_FERROOXIDANS"
    ASPERGILLUS_NIGER = "ASPERGILLUS_NIGER"
    ENGINEERED_STRAIN = "ENGINEERED_STRAIN"

# Set metadata after class creation to avoid it becoming an enum member
BioleachOrganism._metadata = {
    "ACIDITHIOBACILLUS_FERROOXIDANS": {'description': 'Iron and sulfur oxidizing bacterium', 'meaning': 'NCBITaxon:920'},
    "LEPTOSPIRILLUM_FERROOXIDANS": {'description': 'Iron oxidizing bacterium', 'meaning': 'NCBITaxon:180'},
    "ASPERGILLUS_NIGER": {'description': 'Organic acid producing fungus', 'meaning': 'NCBITaxon:5061'},
    "ENGINEERED_STRAIN": {'description': 'Genetically modified organism for enhanced bioleaching'},
}

class BioleachMode(RichEnum):
    """
    Mechanisms of bioleaching including indirect and direct bacterial action.

    """
    # Enum members
    INDIRECT_BIOLEACH_ORGANIC_ACIDS = "INDIRECT_BIOLEACH_ORGANIC_ACIDS"
    SULFUR_OXIDATION = "SULFUR_OXIDATION"
    IRON_OXIDATION = "IRON_OXIDATION"

# Set metadata after class creation to avoid it becoming an enum member
BioleachMode._metadata = {
    "INDIRECT_BIOLEACH_ORGANIC_ACIDS": {'description': 'Indirect bioleaching through organic acid production'},
    "SULFUR_OXIDATION": {'description': 'Direct bacterial oxidation of sulfur compounds'},
    "IRON_OXIDATION": {'description': 'Direct bacterial oxidation of iron compounds'},
}

class AutonomyLevel(RichEnum):
    """
    Levels of autonomy for mining systems including drilling, hauling, and sorting robots (relevant for Topic 1 initiatives).

    """
    # Enum members
    ASSISTIVE = "ASSISTIVE"
    SUPERVISED_AUTONOMY = "SUPERVISED_AUTONOMY"
    SEMI_AUTONOMOUS = "SEMI_AUTONOMOUS"
    FULLY_AUTONOMOUS = "FULLY_AUTONOMOUS"

# Set metadata after class creation to avoid it becoming an enum member
AutonomyLevel._metadata = {
    "ASSISTIVE": {'description': 'Human operator with assistive technologies'},
    "SUPERVISED_AUTONOMY": {'description': 'Autonomous operation with human supervision'},
    "SEMI_AUTONOMOUS": {'description': 'Partial autonomy with human intervention capability'},
    "FULLY_AUTONOMOUS": {'description': 'Complete autonomous operation without human intervention'},
}

class RegulatoryConstraint(RichEnum):
    """
    Regulatory and community constraints affecting mining operations, particularly for in-situ extraction and community engagement.

    """
    # Enum members
    AQUIFER_PROTECTION = "AQUIFER_PROTECTION"
    EMISSIONS_CAP = "EMISSIONS_CAP"
    CULTURAL_HERITAGE_ZONE = "CULTURAL_HERITAGE_ZONE"
    WATER_RIGHTS_LIMIT = "WATER_RIGHTS_LIMIT"

# Set metadata after class creation to avoid it becoming an enum member
RegulatoryConstraint._metadata = {
    "AQUIFER_PROTECTION": {'description': 'Requirements for groundwater and aquifer protection'},
    "EMISSIONS_CAP": {'description': 'Limits on atmospheric emissions'},
    "CULTURAL_HERITAGE_ZONE": {'description': 'Protection of cultural heritage sites'},
    "WATER_RIGHTS_LIMIT": {'description': 'Restrictions based on water usage rights'},
}

class SubatomicParticleEnum(RichEnum):
    """
    Fundamental and composite subatomic particles
    """
    # Enum members
    ELECTRON = "ELECTRON"
    POSITRON = "POSITRON"
    MUON = "MUON"
    TAU_LEPTON = "TAU_LEPTON"
    ELECTRON_NEUTRINO = "ELECTRON_NEUTRINO"
    MUON_NEUTRINO = "MUON_NEUTRINO"
    TAU_NEUTRINO = "TAU_NEUTRINO"
    UP_QUARK = "UP_QUARK"
    DOWN_QUARK = "DOWN_QUARK"
    CHARM_QUARK = "CHARM_QUARK"
    STRANGE_QUARK = "STRANGE_QUARK"
    TOP_QUARK = "TOP_QUARK"
    BOTTOM_QUARK = "BOTTOM_QUARK"
    PHOTON = "PHOTON"
    W_BOSON = "W_BOSON"
    Z_BOSON = "Z_BOSON"
    GLUON = "GLUON"
    HIGGS_BOSON = "HIGGS_BOSON"
    PROTON = "PROTON"
    NEUTRON = "NEUTRON"
    ALPHA_PARTICLE = "ALPHA_PARTICLE"
    DEUTERON = "DEUTERON"
    TRITON = "TRITON"

# Set metadata after class creation to avoid it becoming an enum member
SubatomicParticleEnum._metadata = {
    "ELECTRON": {'description': 'Elementary particle with -1 charge, spin 1/2', 'meaning': 'CHEBI:10545', 'annotations': {'mass': '0.51099895 MeV/c²', 'charge': '-1', 'spin': '1/2', 'type': 'lepton'}},
    "POSITRON": {'description': 'Antiparticle of electron with +1 charge', 'meaning': 'CHEBI:30225', 'annotations': {'mass': '0.51099895 MeV/c²', 'charge': '+1', 'spin': '1/2', 'type': 'lepton'}},
    "MUON": {'description': 'Heavy lepton with -1 charge', 'meaning': 'CHEBI:36356', 'annotations': {'mass': '105.658 MeV/c²', 'charge': '-1', 'spin': '1/2', 'type': 'lepton'}},
    "TAU_LEPTON": {'description': 'Heaviest lepton with -1 charge', 'meaning': 'CHEBI:36355', 'annotations': {'mass': '1777.05 MeV/c²', 'charge': '-1', 'spin': '1/2', 'type': 'lepton'}},
    "ELECTRON_NEUTRINO": {'description': 'Electron neutrino, nearly massless', 'meaning': 'CHEBI:30223', 'annotations': {'mass': '<2.2 eV/c²', 'charge': '0', 'spin': '1/2', 'type': 'lepton'}},
    "MUON_NEUTRINO": {'description': 'Muon neutrino', 'meaning': 'CHEBI:36353', 'annotations': {'mass': '<0.17 MeV/c²', 'charge': '0', 'spin': '1/2', 'type': 'lepton'}},
    "TAU_NEUTRINO": {'description': 'Tau neutrino', 'meaning': 'CHEBI:36354', 'annotations': {'mass': '<15.5 MeV/c²', 'charge': '0', 'spin': '1/2', 'type': 'lepton'}},
    "UP_QUARK": {'description': 'First generation quark with +2/3 charge', 'meaning': 'CHEBI:36366', 'annotations': {'mass': '2.16 MeV/c²', 'charge': '+2/3', 'spin': '1/2', 'type': 'quark', 'generation': '1'}},
    "DOWN_QUARK": {'description': 'First generation quark with -1/3 charge', 'meaning': 'CHEBI:36367', 'annotations': {'mass': '4.67 MeV/c²', 'charge': '-1/3', 'spin': '1/2', 'type': 'quark', 'generation': '1'}},
    "CHARM_QUARK": {'description': 'Second generation quark with +2/3 charge', 'meaning': 'CHEBI:36369', 'annotations': {'mass': '1.27 GeV/c²', 'charge': '+2/3', 'spin': '1/2', 'type': 'quark', 'generation': '2'}},
    "STRANGE_QUARK": {'description': 'Second generation quark with -1/3 charge', 'meaning': 'CHEBI:36368', 'annotations': {'mass': '93.4 MeV/c²', 'charge': '-1/3', 'spin': '1/2', 'type': 'quark', 'generation': '2'}},
    "TOP_QUARK": {'description': 'Third generation quark with +2/3 charge', 'meaning': 'CHEBI:36371', 'annotations': {'mass': '172.76 GeV/c²', 'charge': '+2/3', 'spin': '1/2', 'type': 'quark', 'generation': '3'}},
    "BOTTOM_QUARK": {'description': 'Third generation quark with -1/3 charge', 'meaning': 'CHEBI:36370', 'annotations': {'mass': '4.18 GeV/c²', 'charge': '-1/3', 'spin': '1/2', 'type': 'quark', 'generation': '3'}},
    "PHOTON": {'description': 'Force carrier for electromagnetic interaction', 'meaning': 'CHEBI:30212', 'annotations': {'mass': '0', 'charge': '0', 'spin': '1', 'type': 'gauge boson'}},
    "W_BOSON": {'description': 'Force carrier for weak interaction', 'meaning': 'CHEBI:36343', 'annotations': {'mass': '80.379 GeV/c²', 'charge': '±1', 'spin': '1', 'type': 'gauge boson'}},
    "Z_BOSON": {'description': 'Force carrier for weak interaction', 'meaning': 'CHEBI:36344', 'annotations': {'mass': '91.1876 GeV/c²', 'charge': '0', 'spin': '1', 'type': 'gauge boson'}},
    "GLUON": {'description': 'Force carrier for strong interaction', 'annotations': {'mass': '0', 'charge': '0', 'spin': '1', 'type': 'gauge boson', 'color_charge': 'yes'}},
    "HIGGS_BOSON": {'description': 'Scalar boson responsible for mass', 'meaning': 'CHEBI:146278', 'annotations': {'mass': '125.25 GeV/c²', 'charge': '0', 'spin': '0', 'type': 'scalar boson'}},
    "PROTON": {'description': 'Positively charged nucleon', 'meaning': 'CHEBI:24636', 'annotations': {'mass': '938.272 MeV/c²', 'charge': '+1', 'spin': '1/2', 'type': 'baryon', 'composition': 'uud'}},
    "NEUTRON": {'description': 'Neutral nucleon', 'meaning': 'CHEBI:30222', 'annotations': {'mass': '939.565 MeV/c²', 'charge': '0', 'spin': '1/2', 'type': 'baryon', 'composition': 'udd'}},
    "ALPHA_PARTICLE": {'description': 'Helium-4 nucleus', 'meaning': 'CHEBI:30216', 'annotations': {'mass': '3727.379 MeV/c²', 'charge': '+2', 'composition': '2 protons, 2 neutrons'}},
    "DEUTERON": {'description': 'Hydrogen-2 nucleus', 'meaning': 'CHEBI:29233', 'annotations': {'mass': '1875.613 MeV/c²', 'charge': '+1', 'composition': '1 proton, 1 neutron'}},
    "TRITON": {'description': 'Hydrogen-3 nucleus', 'meaning': 'CHEBI:29234', 'annotations': {'mass': '2808.921 MeV/c²', 'charge': '+1', 'composition': '1 proton, 2 neutrons'}},
}

class BondTypeEnum(RichEnum):
    """
    Types of chemical bonds
    """
    # Enum members
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    TRIPLE = "TRIPLE"
    QUADRUPLE = "QUADRUPLE"
    AROMATIC = "AROMATIC"
    IONIC = "IONIC"
    HYDROGEN = "HYDROGEN"
    METALLIC = "METALLIC"
    VAN_DER_WAALS = "VAN_DER_WAALS"
    COORDINATE = "COORDINATE"
    PI = "PI"
    SIGMA = "SIGMA"

# Set metadata after class creation to avoid it becoming an enum member
BondTypeEnum._metadata = {
    "SINGLE": {'description': 'Single covalent bond', 'meaning': 'gc:Single', 'annotations': {'bond_order': '1', 'electrons_shared': '2'}},
    "DOUBLE": {'description': 'Double covalent bond', 'meaning': 'gc:Double', 'annotations': {'bond_order': '2', 'electrons_shared': '4'}},
    "TRIPLE": {'description': 'Triple covalent bond', 'meaning': 'gc:Triple', 'annotations': {'bond_order': '3', 'electrons_shared': '6'}},
    "QUADRUPLE": {'description': 'Quadruple bond (rare, in transition metals)', 'meaning': 'gc:Quadruple', 'annotations': {'bond_order': '4', 'electrons_shared': '8'}},
    "AROMATIC": {'description': 'Aromatic bond', 'meaning': 'gc:AromaticBond', 'annotations': {'bond_order': '1.5', 'delocalized': 'true'}},
    "IONIC": {'description': 'Ionic bond', 'meaning': 'CHEBI:50860', 'annotations': {'type': 'electrostatic'}},
    "HYDROGEN": {'description': 'Hydrogen bond', 'annotations': {'type': 'weak interaction', 'energy': '5-30 kJ/mol'}},
    "METALLIC": {'description': 'Metallic bond', 'annotations': {'type': 'delocalized electrons'}},
    "VAN_DER_WAALS": {'description': 'Van der Waals interaction', 'annotations': {'type': 'weak interaction', 'energy': '0.4-4 kJ/mol'}},
    "COORDINATE": {'description': 'Coordinate/dative covalent bond', 'meaning': 'CHEBI:33240', 'annotations': {'electrons_from': 'one atom'}},
    "PI": {'description': 'Pi bond', 'annotations': {'orbital_overlap': 'side-to-side'}},
    "SIGMA": {'description': 'Sigma bond', 'annotations': {'orbital_overlap': 'head-to-head'}},
}

class PeriodicTableBlockEnum(RichEnum):
    """
    Blocks of the periodic table
    """
    # Enum members
    S_BLOCK = "S_BLOCK"
    P_BLOCK = "P_BLOCK"
    D_BLOCK = "D_BLOCK"
    F_BLOCK = "F_BLOCK"

# Set metadata after class creation to avoid it becoming an enum member
PeriodicTableBlockEnum._metadata = {
    "S_BLOCK": {'description': 's-block elements (groups 1 and 2)', 'meaning': 'CHEBI:33674', 'annotations': {'valence_orbital': 's', 'groups': '1,2'}},
    "P_BLOCK": {'description': 'p-block elements (groups 13-18)', 'meaning': 'CHEBI:33675', 'annotations': {'valence_orbital': 'p', 'groups': '13,14,15,16,17,18'}},
    "D_BLOCK": {'description': 'd-block elements (transition metals)', 'meaning': 'CHEBI:33561', 'annotations': {'valence_orbital': 'd', 'groups': '3-12'}},
    "F_BLOCK": {'description': 'f-block elements (lanthanides and actinides)', 'meaning': 'CHEBI:33562', 'annotations': {'valence_orbital': 'f', 'series': 'lanthanides, actinides'}},
}

class ElementFamilyEnum(RichEnum):
    """
    Chemical element families/groups
    """
    # Enum members
    ALKALI_METALS = "ALKALI_METALS"
    ALKALINE_EARTH_METALS = "ALKALINE_EARTH_METALS"
    TRANSITION_METALS = "TRANSITION_METALS"
    LANTHANIDES = "LANTHANIDES"
    ACTINIDES = "ACTINIDES"
    CHALCOGENS = "CHALCOGENS"
    HALOGENS = "HALOGENS"
    NOBLE_GASES = "NOBLE_GASES"
    METALLOIDS = "METALLOIDS"
    POST_TRANSITION_METALS = "POST_TRANSITION_METALS"
    NONMETALS = "NONMETALS"

# Set metadata after class creation to avoid it becoming an enum member
ElementFamilyEnum._metadata = {
    "ALKALI_METALS": {'description': 'Group 1 elements (except hydrogen)', 'meaning': 'CHEBI:22314', 'annotations': {'group': '1', 'elements': 'Li, Na, K, Rb, Cs, Fr'}},
    "ALKALINE_EARTH_METALS": {'description': 'Group 2 elements', 'meaning': 'CHEBI:22315', 'annotations': {'group': '2', 'elements': 'Be, Mg, Ca, Sr, Ba, Ra'}},
    "TRANSITION_METALS": {'description': 'd-block elements', 'meaning': 'CHEBI:27081', 'annotations': {'groups': '3-12'}},
    "LANTHANIDES": {'description': 'Lanthanide series', 'meaning': 'CHEBI:33768', 'annotations': {'atomic_numbers': '57-71'}},
    "ACTINIDES": {'description': 'Actinide series', 'meaning': 'CHEBI:33769', 'annotations': {'atomic_numbers': '89-103'}},
    "CHALCOGENS": {'description': 'Group 16 elements', 'meaning': 'CHEBI:33303', 'annotations': {'group': '16', 'elements': 'O, S, Se, Te, Po'}},
    "HALOGENS": {'description': 'Group 17 elements', 'meaning': 'CHEBI:47902', 'annotations': {'group': '17', 'elements': 'F, Cl, Br, I, At'}},
    "NOBLE_GASES": {'description': 'Group 18 elements', 'meaning': 'CHEBI:33310', 'annotations': {'group': '18', 'elements': 'He, Ne, Ar, Kr, Xe, Rn'}},
    "METALLOIDS": {'description': 'Elements with intermediate properties', 'meaning': 'CHEBI:33559', 'annotations': {'elements': 'B, Si, Ge, As, Sb, Te, Po'}},
    "POST_TRANSITION_METALS": {'description': 'Metals after the transition series', 'annotations': {'elements': 'Al, Ga, In, Tl, Sn, Pb, Bi'}},
    "NONMETALS": {'description': 'Non-metallic elements', 'meaning': 'CHEBI:25585', 'annotations': {'elements': 'H, C, N, O, F, P, S, Cl, Se, Br, I'}},
}

class ElementMetallicClassificationEnum(RichEnum):
    """
    Metallic character classification
    """
    # Enum members
    METALLIC = "METALLIC"
    NON_METALLIC = "NON_METALLIC"
    SEMI_METALLIC = "SEMI_METALLIC"

# Set metadata after class creation to avoid it becoming an enum member
ElementMetallicClassificationEnum._metadata = {
    "METALLIC": {'description': 'Metallic elements', 'meaning': 'damlpt:Metallic', 'annotations': {'properties': 'conductive, malleable, ductile'}},
    "NON_METALLIC": {'description': 'Non-metallic elements', 'meaning': 'damlpt:Non-Metallic', 'annotations': {'properties': 'poor conductors, brittle'}},
    "SEMI_METALLIC": {'description': 'Semi-metallic/metalloid elements', 'meaning': 'damlpt:Semi-Metallic', 'annotations': {'properties': 'intermediate properties'}},
}

class HardOrSoftEnum(RichEnum):
    """
    HSAB (Hard Soft Acid Base) classification
    """
    # Enum members
    HARD = "HARD"
    SOFT = "SOFT"
    BORDERLINE = "BORDERLINE"

# Set metadata after class creation to avoid it becoming an enum member
HardOrSoftEnum._metadata = {
    "HARD": {'description': 'Hard acids/bases (small, high charge density)', 'annotations': {'examples': 'H+, Li+, Mg2+, Al3+, F-, OH-', 'polarizability': 'low'}},
    "SOFT": {'description': 'Soft acids/bases (large, low charge density)', 'annotations': {'examples': 'Cu+, Ag+, Au+, I-, S2-', 'polarizability': 'high'}},
    "BORDERLINE": {'description': 'Borderline acids/bases', 'annotations': {'examples': 'Fe2+, Co2+, Ni2+, Cu2+, Zn2+', 'polarizability': 'intermediate'}},
}

class BronstedAcidBaseRoleEnum(RichEnum):
    """
    Brønsted-Lowry acid-base roles
    """
    # Enum members
    ACID = "ACID"
    BASE = "BASE"
    AMPHOTERIC = "AMPHOTERIC"

# Set metadata after class creation to avoid it becoming an enum member
BronstedAcidBaseRoleEnum._metadata = {
    "ACID": {'description': 'Proton donor', 'meaning': 'CHEBI:39141', 'annotations': {'definition': 'species that donates H+'}},
    "BASE": {'description': 'Proton acceptor', 'meaning': 'CHEBI:39142', 'annotations': {'definition': 'species that accepts H+'}},
    "AMPHOTERIC": {'description': 'Can act as both acid and base', 'annotations': {'definition': 'species that can donate or accept H+', 'examples': 'H2O, HSO4-, H2PO4-'}},
}

class LewisAcidBaseRoleEnum(RichEnum):
    """
    Lewis acid-base roles
    """
    # Enum members
    LEWIS_ACID = "LEWIS_ACID"
    LEWIS_BASE = "LEWIS_BASE"

# Set metadata after class creation to avoid it becoming an enum member
LewisAcidBaseRoleEnum._metadata = {
    "LEWIS_ACID": {'description': 'Electron pair acceptor', 'annotations': {'definition': 'species that accepts electron pair', 'examples': 'BF3, AlCl3, H+'}},
    "LEWIS_BASE": {'description': 'Electron pair donor', 'annotations': {'definition': 'species that donates electron pair', 'examples': 'NH3, OH-, H2O'}},
}

class OxidationStateEnum(RichEnum):
    """
    Common oxidation states
    """
    # Enum members
    MINUS_4 = "MINUS_4"
    MINUS_3 = "MINUS_3"
    MINUS_2 = "MINUS_2"
    MINUS_1 = "MINUS_1"
    ZERO = "ZERO"
    PLUS_1 = "PLUS_1"
    PLUS_2 = "PLUS_2"
    PLUS_3 = "PLUS_3"
    PLUS_4 = "PLUS_4"
    PLUS_5 = "PLUS_5"
    PLUS_6 = "PLUS_6"
    PLUS_7 = "PLUS_7"
    PLUS_8 = "PLUS_8"

# Set metadata after class creation to avoid it becoming an enum member
OxidationStateEnum._metadata = {
    "MINUS_4": {'description': 'Oxidation state -4', 'annotations': {'value': '-4', 'example': 'C in CH4'}},
    "MINUS_3": {'description': 'Oxidation state -3', 'annotations': {'value': '-3', 'example': 'N in NH3'}},
    "MINUS_2": {'description': 'Oxidation state -2', 'annotations': {'value': '-2', 'example': 'O in H2O'}},
    "MINUS_1": {'description': 'Oxidation state -1', 'annotations': {'value': '-1', 'example': 'Cl in NaCl'}},
    "ZERO": {'description': 'Oxidation state 0', 'annotations': {'value': '0', 'example': 'elemental forms'}},
    "PLUS_1": {'description': 'Oxidation state +1', 'annotations': {'value': '+1', 'example': 'Na in NaCl'}},
    "PLUS_2": {'description': 'Oxidation state +2', 'annotations': {'value': '+2', 'example': 'Ca in CaCl2'}},
    "PLUS_3": {'description': 'Oxidation state +3', 'annotations': {'value': '+3', 'example': 'Al in Al2O3'}},
    "PLUS_4": {'description': 'Oxidation state +4', 'annotations': {'value': '+4', 'example': 'C in CO2'}},
    "PLUS_5": {'description': 'Oxidation state +5', 'annotations': {'value': '+5', 'example': 'P in PO4³⁻'}},
    "PLUS_6": {'description': 'Oxidation state +6', 'annotations': {'value': '+6', 'example': 'S in SO4²⁻'}},
    "PLUS_7": {'description': 'Oxidation state +7', 'annotations': {'value': '+7', 'example': 'Mn in MnO4⁻'}},
    "PLUS_8": {'description': 'Oxidation state +8', 'annotations': {'value': '+8', 'example': 'Os in OsO4'}},
}

class ChiralityEnum(RichEnum):
    """
    Chirality/stereochemistry descriptors
    """
    # Enum members
    R = "R"
    S = "S"
    D = "D"
    L = "L"
    RACEMIC = "RACEMIC"
    MESO = "MESO"
    E = "E"
    Z = "Z"

# Set metadata after class creation to avoid it becoming an enum member
ChiralityEnum._metadata = {
    "R": {'description': 'Rectus (right) configuration', 'annotations': {'cahn_ingold_prelog': 'true'}},
    "S": {'description': 'Sinister (left) configuration', 'annotations': {'cahn_ingold_prelog': 'true'}},
    "D": {'description': 'Dextrorotatory', 'annotations': {'fischer_projection': 'true', 'optical_rotation': 'positive'}},
    "L": {'description': 'Levorotatory', 'annotations': {'fischer_projection': 'true', 'optical_rotation': 'negative'}},
    "RACEMIC": {'description': 'Racemic mixture (50:50 of enantiomers)', 'annotations': {'optical_rotation': 'zero'}},
    "MESO": {'description': 'Meso compound (achiral despite stereocenters)', 'annotations': {'internal_symmetry': 'true'}},
    "E": {'description': 'Entgegen (opposite) configuration', 'annotations': {'geometric_isomer': 'true'}},
    "Z": {'description': 'Zusammen (together) configuration', 'annotations': {'geometric_isomer': 'true'}},
}

class NanostructureMorphologyEnum(RichEnum):
    """
    Types of nanostructure morphologies
    """
    # Enum members
    NANOTUBE = "NANOTUBE"
    NANOPARTICLE = "NANOPARTICLE"
    NANOROD = "NANOROD"
    QUANTUM_DOT = "QUANTUM_DOT"
    NANOWIRE = "NANOWIRE"
    NANOSHEET = "NANOSHEET"
    NANOFIBER = "NANOFIBER"

# Set metadata after class creation to avoid it becoming an enum member
NanostructureMorphologyEnum._metadata = {
    "NANOTUBE": {'description': 'Cylindrical nanostructure', 'meaning': 'CHEBI:50796', 'annotations': {'dimensions': '1D', 'examples': 'carbon nanotubes'}},
    "NANOPARTICLE": {'description': 'Particle with nanoscale dimensions', 'meaning': 'CHEBI:50803', 'annotations': {'dimensions': '0D', 'size_range': '1-100 nm'}},
    "NANOROD": {'description': 'Rod-shaped nanostructure', 'meaning': 'CHEBI:50805', 'annotations': {'dimensions': '1D', 'aspect_ratio': '3-20'}},
    "QUANTUM_DOT": {'description': 'Semiconductor nanocrystal', 'meaning': 'CHEBI:50853', 'annotations': {'dimensions': '0D', 'property': 'quantum confinement'}},
    "NANOWIRE": {'description': 'Wire with nanoscale diameter', 'annotations': {'dimensions': '1D', 'diameter': '<100 nm'}},
    "NANOSHEET": {'description': 'Two-dimensional nanostructure', 'annotations': {'dimensions': '2D', 'thickness': '<100 nm'}},
    "NANOFIBER": {'description': 'Fiber with nanoscale diameter', 'annotations': {'dimensions': '1D', 'diameter': '<1000 nm'}},
}

class ReactionTypeEnum(RichEnum):
    """
    Types of chemical reactions
    """
    # Enum members
    SYNTHESIS = "SYNTHESIS"
    DECOMPOSITION = "DECOMPOSITION"
    SINGLE_DISPLACEMENT = "SINGLE_DISPLACEMENT"
    DOUBLE_DISPLACEMENT = "DOUBLE_DISPLACEMENT"
    COMBUSTION = "COMBUSTION"
    SUBSTITUTION = "SUBSTITUTION"
    ELIMINATION = "ELIMINATION"
    ADDITION = "ADDITION"
    REARRANGEMENT = "REARRANGEMENT"
    OXIDATION = "OXIDATION"
    REDUCTION = "REDUCTION"
    DIELS_ALDER = "DIELS_ALDER"
    FRIEDEL_CRAFTS = "FRIEDEL_CRAFTS"
    GRIGNARD = "GRIGNARD"
    WITTIG = "WITTIG"
    ALDOL = "ALDOL"
    MICHAEL_ADDITION = "MICHAEL_ADDITION"

# Set metadata after class creation to avoid it becoming an enum member
ReactionTypeEnum._metadata = {
    "SYNTHESIS": {'description': 'Combination reaction (A + B → AB)', 'annotations': {'aliases': 'combination, addition', 'pattern': 'A + B → AB'}},
    "DECOMPOSITION": {'description': 'Breakdown reaction (AB → A + B)', 'annotations': {'aliases': 'analysis', 'pattern': 'AB → A + B'}},
    "SINGLE_DISPLACEMENT": {'description': 'Single replacement reaction (A + BC → AC + B)', 'annotations': {'aliases': 'single replacement', 'pattern': 'A + BC → AC + B'}},
    "DOUBLE_DISPLACEMENT": {'description': 'Double replacement reaction (AB + CD → AD + CB)', 'annotations': {'aliases': 'double replacement, metathesis', 'pattern': 'AB + CD → AD + CB'}},
    "COMBUSTION": {'description': 'Reaction with oxygen producing heat and light', 'annotations': {'reactant': 'oxygen', 'products': 'usually CO2 and H2O'}},
    "SUBSTITUTION": {'description': 'Replacement of one group by another', 'meaning': 'MOP:0000790', 'annotations': {'subtypes': 'SN1, SN2, SNAr'}},
    "ELIMINATION": {'description': 'Removal of atoms/groups forming double bond', 'meaning': 'MOP:0000656', 'annotations': {'subtypes': 'E1, E2, E1cB'}},
    "ADDITION": {'description': 'Addition to multiple bond', 'meaning': 'MOP:0000642', 'annotations': {'subtypes': 'electrophilic, nucleophilic, radical'}},
    "REARRANGEMENT": {'description': 'Reorganization of molecular structure', 'annotations': {'examples': 'Claisen, Cope, Wagner-Meerwein'}},
    "OXIDATION": {'description': 'Loss of electrons or increase in oxidation state', 'annotations': {'electron_change': 'loss'}},
    "REDUCTION": {'description': 'Gain of electrons or decrease in oxidation state', 'annotations': {'electron_change': 'gain'}},
    "DIELS_ALDER": {'description': '[4+2] cycloaddition reaction', 'meaning': 'RXNO:0000006', 'annotations': {'type': 'pericyclic', 'components': 'diene + dienophile'}},
    "FRIEDEL_CRAFTS": {'description': 'Electrophilic aromatic substitution', 'meaning': 'RXNO:0000369', 'annotations': {'subtypes': 'alkylation, acylation'}},
    "GRIGNARD": {'description': 'Organometallic addition reaction', 'meaning': 'RXNO:0000014', 'annotations': {'reagent': 'RMgX'}},
    "WITTIG": {'description': 'Alkene formation from phosphonium ylide', 'meaning': 'RXNO:0000015', 'annotations': {'product': 'alkene'}},
    "ALDOL": {'description': 'Condensation forming β-hydroxy carbonyl', 'meaning': 'RXNO:0000017', 'annotations': {'mechanism': 'enolate addition'}},
    "MICHAEL_ADDITION": {'description': '1,4-addition to α,β-unsaturated carbonyl', 'meaning': 'RXNO:0000009', 'annotations': {'type': 'conjugate addition'}},
}

class ReactionMechanismEnum(RichEnum):
    """
    Reaction mechanism types
    """
    # Enum members
    SN1 = "SN1"
    SN2 = "SN2"
    E1 = "E1"
    E2 = "E2"
    E1CB = "E1CB"
    RADICAL = "RADICAL"
    PERICYCLIC = "PERICYCLIC"
    ELECTROPHILIC_AROMATIC = "ELECTROPHILIC_AROMATIC"
    NUCLEOPHILIC_AROMATIC = "NUCLEOPHILIC_AROMATIC"
    ADDITION_ELIMINATION = "ADDITION_ELIMINATION"

# Set metadata after class creation to avoid it becoming an enum member
ReactionMechanismEnum._metadata = {
    "SN1": {'description': 'Unimolecular nucleophilic substitution', 'annotations': {'rate_determining': 'carbocation formation', 'stereochemistry': 'racemization'}},
    "SN2": {'description': 'Bimolecular nucleophilic substitution', 'annotations': {'rate_determining': 'concerted', 'stereochemistry': 'inversion'}},
    "E1": {'description': 'Unimolecular elimination', 'annotations': {'intermediate': 'carbocation'}},
    "E2": {'description': 'Bimolecular elimination', 'annotations': {'requirement': 'antiperiplanar'}},
    "E1CB": {'description': 'Elimination via conjugate base', 'annotations': {'intermediate': 'carbanion'}},
    "RADICAL": {'description': 'Free radical mechanism', 'annotations': {'initiation': 'homolytic cleavage'}},
    "PERICYCLIC": {'description': 'Concerted cyclic electron reorganization', 'annotations': {'examples': 'Diels-Alder, Cope'}},
    "ELECTROPHILIC_AROMATIC": {'description': 'Electrophilic aromatic substitution', 'annotations': {'intermediate': 'arenium ion'}},
    "NUCLEOPHILIC_AROMATIC": {'description': 'Nucleophilic aromatic substitution', 'annotations': {'requirement': 'electron-withdrawing groups'}},
    "ADDITION_ELIMINATION": {'description': 'Addition followed by elimination', 'annotations': {'intermediate': 'tetrahedral'}},
}

class CatalystTypeEnum(RichEnum):
    """
    Types of catalysts
    """
    # Enum members
    HOMOGENEOUS = "HOMOGENEOUS"
    HETEROGENEOUS = "HETEROGENEOUS"
    ENZYME = "ENZYME"
    ORGANOCATALYST = "ORGANOCATALYST"
    PHOTOCATALYST = "PHOTOCATALYST"
    PHASE_TRANSFER = "PHASE_TRANSFER"
    ACID = "ACID"
    BASE = "BASE"
    METAL = "METAL"
    BIFUNCTIONAL = "BIFUNCTIONAL"

# Set metadata after class creation to avoid it becoming an enum member
CatalystTypeEnum._metadata = {
    "HOMOGENEOUS": {'description': 'Catalyst in same phase as reactants', 'annotations': {'phase': 'same as reactants', 'examples': 'acid, base, metal complexes'}},
    "HETEROGENEOUS": {'description': 'Catalyst in different phase from reactants', 'annotations': {'phase': 'different from reactants', 'examples': 'Pt/Pd on carbon, zeolites'}},
    "ENZYME": {'description': 'Biological catalyst', 'meaning': 'CHEBI:23357', 'annotations': {'type': 'protein', 'specificity': 'high'}},
    "ORGANOCATALYST": {'description': 'Small organic molecule catalyst', 'annotations': {'metal_free': 'true', 'examples': 'proline, thiourea'}},
    "PHOTOCATALYST": {'description': 'Light-activated catalyst', 'annotations': {'activation': 'light', 'examples': 'TiO2, Ru complexes'}},
    "PHASE_TRANSFER": {'description': 'Catalyst facilitating reaction between phases', 'annotations': {'function': 'transfers reactant between phases'}},
    "ACID": {'description': 'Acid catalyst', 'annotations': {'mechanism': 'proton donation'}},
    "BASE": {'description': 'Base catalyst', 'annotations': {'mechanism': 'proton abstraction'}},
    "METAL": {'description': 'Metal catalyst', 'annotations': {'examples': 'Pd, Pt, Ni, Ru'}},
    "BIFUNCTIONAL": {'description': 'Catalyst with two active sites', 'annotations': {'sites': 'multiple'}},
}

class ReactionConditionEnum(RichEnum):
    """
    Reaction conditions
    """
    # Enum members
    ROOM_TEMPERATURE = "ROOM_TEMPERATURE"
    REFLUX = "REFLUX"
    CRYOGENIC = "CRYOGENIC"
    HIGH_PRESSURE = "HIGH_PRESSURE"
    VACUUM = "VACUUM"
    INERT_ATMOSPHERE = "INERT_ATMOSPHERE"
    MICROWAVE = "MICROWAVE"
    ULTRASOUND = "ULTRASOUND"
    PHOTOCHEMICAL = "PHOTOCHEMICAL"
    ELECTROCHEMICAL = "ELECTROCHEMICAL"
    FLOW = "FLOW"
    BATCH = "BATCH"

# Set metadata after class creation to avoid it becoming an enum member
ReactionConditionEnum._metadata = {
    "ROOM_TEMPERATURE": {'description': 'Standard room temperature (20-25°C)', 'annotations': {'temperature': '20-25°C'}},
    "REFLUX": {'description': 'Boiling with condensation return', 'annotations': {'temperature': 'solvent boiling point'}},
    "CRYOGENIC": {'description': 'Very low temperature conditions', 'annotations': {'temperature': '<-150°C', 'examples': 'liquid N2, liquid He'}},
    "HIGH_PRESSURE": {'description': 'Elevated pressure conditions', 'annotations': {'pressure': '>10 atm'}},
    "VACUUM": {'description': 'Reduced pressure conditions', 'annotations': {'pressure': '<1 atm'}},
    "INERT_ATMOSPHERE": {'description': 'Non-reactive gas atmosphere', 'annotations': {'gases': 'N2, Ar'}},
    "MICROWAVE": {'description': 'Microwave heating', 'annotations': {'heating': 'microwave irradiation'}},
    "ULTRASOUND": {'description': 'Ultrasonic conditions', 'annotations': {'activation': 'ultrasound'}},
    "PHOTOCHEMICAL": {'description': 'Light-induced conditions', 'annotations': {'activation': 'UV or visible light'}},
    "ELECTROCHEMICAL": {'description': 'Electrically driven conditions', 'annotations': {'activation': 'electric current'}},
    "FLOW": {'description': 'Continuous flow conditions', 'annotations': {'type': 'continuous process'}},
    "BATCH": {'description': 'Batch reaction conditions', 'annotations': {'type': 'batch process'}},
}

class ReactionRateOrderEnum(RichEnum):
    """
    Reaction rate orders
    """
    # Enum members
    ZERO_ORDER = "ZERO_ORDER"
    FIRST_ORDER = "FIRST_ORDER"
    SECOND_ORDER = "SECOND_ORDER"
    PSEUDO_FIRST_ORDER = "PSEUDO_FIRST_ORDER"
    FRACTIONAL_ORDER = "FRACTIONAL_ORDER"
    MIXED_ORDER = "MIXED_ORDER"

# Set metadata after class creation to avoid it becoming an enum member
ReactionRateOrderEnum._metadata = {
    "ZERO_ORDER": {'description': 'Rate independent of concentration', 'annotations': {'rate_law': 'rate = k', 'integrated': '[A] = [A]₀ - kt'}},
    "FIRST_ORDER": {'description': 'Rate proportional to concentration', 'annotations': {'rate_law': 'rate = k[A]', 'integrated': 'ln[A] = ln[A]₀ - kt'}},
    "SECOND_ORDER": {'description': 'Rate proportional to concentration squared', 'annotations': {'rate_law': 'rate = k[A]²', 'integrated': '1/[A] = 1/[A]₀ + kt'}},
    "PSEUDO_FIRST_ORDER": {'description': 'Apparent first order (excess reagent)', 'annotations': {'condition': 'one reagent in large excess'}},
    "FRACTIONAL_ORDER": {'description': 'Non-integer order', 'annotations': {'indicates': 'complex mechanism'}},
    "MIXED_ORDER": {'description': 'Different orders for different reactants', 'annotations': {'example': 'rate = k[A][B]²'}},
}

class EnzymeClassEnum(RichEnum):
    """
    EC enzyme classification
    """
    # Enum members
    OXIDOREDUCTASE = "OXIDOREDUCTASE"
    TRANSFERASE = "TRANSFERASE"
    HYDROLASE = "HYDROLASE"
    LYASE = "LYASE"
    ISOMERASE = "ISOMERASE"
    LIGASE = "LIGASE"
    TRANSLOCASE = "TRANSLOCASE"

# Set metadata after class creation to avoid it becoming an enum member
EnzymeClassEnum._metadata = {
    "OXIDOREDUCTASE": {'description': 'Catalyzes oxidation-reduction reactions', 'meaning': 'EC:1', 'annotations': {'EC_class': '1', 'examples': 'dehydrogenases, oxidases'}},
    "TRANSFERASE": {'description': 'Catalyzes group transfer reactions', 'meaning': 'EC:2', 'annotations': {'EC_class': '2', 'examples': 'kinases, transaminases'}},
    "HYDROLASE": {'description': 'Catalyzes hydrolysis reactions', 'meaning': 'EC:3', 'annotations': {'EC_class': '3', 'examples': 'proteases, lipases'}},
    "LYASE": {'description': 'Catalyzes non-hydrolytic additions/removals', 'meaning': 'EC:4', 'annotations': {'EC_class': '4', 'examples': 'decarboxylases, aldolases'}},
    "ISOMERASE": {'description': 'Catalyzes isomerization reactions', 'meaning': 'EC:5', 'annotations': {'EC_class': '5', 'examples': 'racemases, epimerases'}},
    "LIGASE": {'description': 'Catalyzes formation of bonds with ATP', 'meaning': 'EC:6', 'annotations': {'EC_class': '6', 'examples': 'synthetases, carboxylases'}},
    "TRANSLOCASE": {'description': 'Catalyzes movement across membranes', 'meaning': 'EC:7', 'annotations': {'EC_class': '7', 'examples': 'ATPases, ion pumps'}},
}

class SolventClassEnum(RichEnum):
    """
    Classes of solvents
    """
    # Enum members
    PROTIC = "PROTIC"
    APROTIC_POLAR = "APROTIC_POLAR"
    APROTIC_NONPOLAR = "APROTIC_NONPOLAR"
    IONIC_LIQUID = "IONIC_LIQUID"
    SUPERCRITICAL = "SUPERCRITICAL"
    AQUEOUS = "AQUEOUS"
    ORGANIC = "ORGANIC"
    GREEN = "GREEN"

# Set metadata after class creation to avoid it becoming an enum member
SolventClassEnum._metadata = {
    "PROTIC": {'description': 'Solvents with acidic hydrogen', 'annotations': {'H_bonding': 'donor', 'examples': 'water, alcohols, acids'}},
    "APROTIC_POLAR": {'description': 'Polar solvents without acidic H', 'annotations': {'H_bonding': 'acceptor only', 'examples': 'DMSO, DMF, acetone'}},
    "APROTIC_NONPOLAR": {'description': 'Nonpolar solvents', 'annotations': {'H_bonding': 'none', 'examples': 'hexane, benzene, CCl4'}},
    "IONIC_LIQUID": {'description': 'Room temperature ionic liquids', 'annotations': {'state': 'liquid salt', 'examples': 'imidazolium salts'}},
    "SUPERCRITICAL": {'description': 'Supercritical fluids', 'annotations': {'state': 'supercritical', 'examples': 'scCO2, scH2O'}},
    "AQUEOUS": {'description': 'Water-based solvents', 'annotations': {'base': 'water'}},
    "ORGANIC": {'description': 'Organic solvents', 'annotations': {'base': 'organic compounds'}},
    "GREEN": {'description': 'Environmentally friendly solvents', 'annotations': {'property': 'low environmental impact', 'examples': 'water, ethanol, scCO2'}},
}

class ThermodynamicParameterEnum(RichEnum):
    """
    Thermodynamic parameters
    """
    # Enum members
    ENTHALPY = "ENTHALPY"
    ENTROPY = "ENTROPY"
    GIBBS_ENERGY = "GIBBS_ENERGY"
    ACTIVATION_ENERGY = "ACTIVATION_ENERGY"
    HEAT_CAPACITY = "HEAT_CAPACITY"
    INTERNAL_ENERGY = "INTERNAL_ENERGY"

# Set metadata after class creation to avoid it becoming an enum member
ThermodynamicParameterEnum._metadata = {
    "ENTHALPY": {'description': 'Heat content (ΔH)', 'annotations': {'symbol': 'ΔH', 'units': 'kJ/mol'}},
    "ENTROPY": {'description': 'Disorder (ΔS)', 'annotations': {'symbol': 'ΔS', 'units': 'J/mol·K'}},
    "GIBBS_ENERGY": {'description': 'Free energy (ΔG)', 'annotations': {'symbol': 'ΔG', 'units': 'kJ/mol'}},
    "ACTIVATION_ENERGY": {'description': 'Energy barrier (Ea)', 'annotations': {'symbol': 'Ea', 'units': 'kJ/mol'}},
    "HEAT_CAPACITY": {'description': 'Heat capacity (Cp)', 'annotations': {'symbol': 'Cp', 'units': 'J/mol·K'}},
    "INTERNAL_ENERGY": {'description': 'Internal energy (ΔU)', 'annotations': {'symbol': 'ΔU', 'units': 'kJ/mol'}},
}

class ReactionDirectionality(RichEnum):
    """
    The directionality of a chemical reaction or process
    """
    # Enum members
    LEFT_TO_RIGHT = "LEFT_TO_RIGHT"
    RIGHT_TO_LEFT = "RIGHT_TO_LEFT"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    AGNOSTIC = "AGNOSTIC"
    IRREVERSIBLE_LEFT_TO_RIGHT = "IRREVERSIBLE_LEFT_TO_RIGHT"
    IRREVERSIBLE_RIGHT_TO_LEFT = "IRREVERSIBLE_RIGHT_TO_LEFT"

# Set metadata after class creation to avoid it becoming an enum member
ReactionDirectionality._metadata = {
    "LEFT_TO_RIGHT": {'description': 'Reaction proceeds from left to right (forward direction)', 'aliases': ['LR', 'forward', '-->']},
    "RIGHT_TO_LEFT": {'description': 'Reaction proceeds from right to left (reverse direction)', 'aliases': ['RL', 'reverse', 'backward', '<--']},
    "BIDIRECTIONAL": {'description': 'Reaction can proceed in both directions', 'aliases': ['BIDI', 'reversible', '<-->']},
    "AGNOSTIC": {'description': 'Direction is unknown or not specified', 'aliases': ['unknown', 'unspecified']},
    "IRREVERSIBLE_LEFT_TO_RIGHT": {'description': 'Reaction proceeds only from left to right and cannot be reversed', 'aliases': ['irreversible forward', '->>']},
    "IRREVERSIBLE_RIGHT_TO_LEFT": {'description': 'Reaction proceeds only from right to left and cannot be reversed', 'aliases': ['irreversible reverse', '<<-']},
}

class SafetyColorEnum(RichEnum):
    """
    ANSI/ISO standard safety colors
    """
    # Enum members
    SAFETY_RED = "SAFETY_RED"
    SAFETY_ORANGE = "SAFETY_ORANGE"
    SAFETY_YELLOW = "SAFETY_YELLOW"
    SAFETY_GREEN = "SAFETY_GREEN"
    SAFETY_BLUE = "SAFETY_BLUE"
    SAFETY_PURPLE = "SAFETY_PURPLE"
    SAFETY_BLACK = "SAFETY_BLACK"
    SAFETY_WHITE = "SAFETY_WHITE"
    SAFETY_GRAY = "SAFETY_GRAY"
    SAFETY_BROWN = "SAFETY_BROWN"

# Set metadata after class creation to avoid it becoming an enum member
SafetyColorEnum._metadata = {
    "SAFETY_RED": {'description': 'Safety red - danger, stop, prohibition', 'meaning': 'HEX:C8102E', 'annotations': {'standard': 'ANSI Z535.1', 'pantone': 'PMS 186 C', 'usage': 'fire equipment, stop signs, danger signs'}},
    "SAFETY_ORANGE": {'description': 'Safety orange - warning of dangerous parts', 'meaning': 'HEX:FF6900', 'annotations': {'standard': 'ANSI Z535.1', 'pantone': 'PMS 151 C', 'usage': 'machine parts, exposed edges'}},
    "SAFETY_YELLOW": {'description': 'Safety yellow - caution, physical hazards', 'meaning': 'HEX:F6D04D', 'annotations': {'standard': 'ANSI Z535.1', 'pantone': 'PMS 116 C', 'usage': 'caution signs, physical hazards, stumbling'}},
    "SAFETY_GREEN": {'description': 'Safety green - safety, first aid, emergency egress', 'meaning': 'HEX:00843D', 'annotations': {'standard': 'ANSI Z535.1', 'pantone': 'PMS 355 C', 'usage': 'first aid, safety equipment, emergency exits'}},
    "SAFETY_BLUE": {'description': 'Safety blue - mandatory, information', 'meaning': 'HEX:005EB8', 'annotations': {'standard': 'ANSI Z535.1', 'pantone': 'PMS 285 C', 'usage': 'mandatory signs, information signs'}},
    "SAFETY_PURPLE": {'description': 'Safety purple - radiation hazards', 'meaning': 'HEX:652D90', 'annotations': {'standard': 'ANSI Z535.1', 'pantone': 'PMS 2685 C', 'usage': 'radiation hazards, x-ray equipment'}},
    "SAFETY_BLACK": {'description': 'Safety black - traffic/housekeeping markings', 'meaning': 'HEX:000000', 'annotations': {'standard': 'ANSI Z535.1', 'usage': 'traffic control, housekeeping markers'}},
    "SAFETY_WHITE": {'description': 'Safety white - traffic/housekeeping markings', 'meaning': 'HEX:FFFFFF', 'annotations': {'standard': 'ANSI Z535.1', 'usage': 'traffic lanes, housekeeping boundaries'}},
    "SAFETY_GRAY": {'description': 'Safety gray - inactive/out of service', 'meaning': 'HEX:919191', 'annotations': {'standard': 'ANSI Z535.1', 'usage': 'out of service equipment'}},
    "SAFETY_BROWN": {'description': 'Safety brown - no special hazard (background)', 'meaning': 'HEX:795548', 'annotations': {'usage': 'background color for signs'}},
}

class TrafficLightColorEnum(RichEnum):
    """
    Traffic signal colors (international)
    """
    # Enum members
    RED = "RED"
    AMBER = "AMBER"
    GREEN = "GREEN"
    FLASHING_RED = "FLASHING_RED"
    FLASHING_AMBER = "FLASHING_AMBER"
    WHITE = "WHITE"

# Set metadata after class creation to avoid it becoming an enum member
TrafficLightColorEnum._metadata = {
    "RED": {'description': 'Red - stop', 'meaning': 'HEX:FF0000', 'annotations': {'wavelength': '630-700 nm', 'meaning_universal': 'stop, do not proceed'}},
    "AMBER": {'description': 'Amber/yellow - caution', 'meaning': 'HEX:FFBF00', 'annotations': {'wavelength': '590 nm', 'meaning_universal': 'prepare to stop, caution'}},
    "GREEN": {'description': 'Green - go', 'meaning': 'HEX:00FF00', 'annotations': {'wavelength': '510-570 nm', 'meaning_universal': 'proceed, safe to go'}},
    "FLASHING_RED": {'description': 'Flashing red - stop then proceed', 'meaning': 'HEX:FF0000', 'annotations': {'pattern': 'flashing', 'meaning_universal': 'stop, then proceed when safe'}},
    "FLASHING_AMBER": {'description': 'Flashing amber - proceed with caution', 'meaning': 'HEX:FFBF00', 'annotations': {'pattern': 'flashing', 'meaning_universal': 'proceed with caution'}},
    "WHITE": {'description': 'White - special situations (transit)', 'meaning': 'HEX:FFFFFF', 'annotations': {'usage': 'transit priority signals'}},
}

class HazmatColorEnum(RichEnum):
    """
    Hazardous materials placarding colors (DOT/UN)
    """
    # Enum members
    ORANGE = "ORANGE"
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    WHITE = "WHITE"
    BLACK_WHITE_STRIPES = "BLACK_WHITE_STRIPES"
    BLUE = "BLUE"
    WHITE_RED_STRIPES = "WHITE_RED_STRIPES"

# Set metadata after class creation to avoid it becoming an enum member
HazmatColorEnum._metadata = {
    "ORANGE": {'description': 'Orange - explosives (Class 1)', 'meaning': 'HEX:FF6600', 'annotations': {'class': '1', 'hazard': 'explosives'}},
    "RED": {'description': 'Red - flammable (Classes 2.1, 3)', 'meaning': 'HEX:FF0000', 'annotations': {'class': '2.1, 3', 'hazard': 'flammable gas, flammable liquid'}},
    "GREEN": {'description': 'Green - non-flammable gas (Class 2.2)', 'meaning': 'HEX:00FF00', 'annotations': {'class': '2.2', 'hazard': 'non-flammable gas'}},
    "YELLOW": {'description': 'Yellow - oxidizer, organic peroxide (Classes 5.1, 5.2)', 'meaning': 'HEX:FFFF00', 'annotations': {'class': '5.1, 5.2', 'hazard': 'oxidizing substances, organic peroxides'}},
    "WHITE": {'description': 'White - poison/toxic (Class 6.1)', 'meaning': 'HEX:FFFFFF', 'annotations': {'class': '6.1', 'hazard': 'toxic/poisonous substances'}},
    "BLACK_WHITE_STRIPES": {'description': 'Black and white stripes - corrosive (Class 8)', 'annotations': {'class': '8', 'hazard': 'corrosive substances', 'pattern': 'black and white vertical stripes'}},
    "BLUE": {'description': 'Blue - dangerous when wet (Class 4.3)', 'meaning': 'HEX:0000FF', 'annotations': {'class': '4.3', 'hazard': 'dangerous when wet'}},
    "WHITE_RED_STRIPES": {'description': 'White with red stripes - flammable solid (Class 4.1)', 'annotations': {'class': '4.1', 'hazard': 'flammable solid', 'pattern': 'white with red vertical stripes'}},
}

class FireSafetyColorEnum(RichEnum):
    """
    Fire safety equipment and signage colors
    """
    # Enum members
    FIRE_RED = "FIRE_RED"
    PHOTOLUMINESCENT_GREEN = "PHOTOLUMINESCENT_GREEN"
    YELLOW_BLACK_STRIPES = "YELLOW_BLACK_STRIPES"
    WHITE = "WHITE"
    BLUE = "BLUE"

# Set metadata after class creation to avoid it becoming an enum member
FireSafetyColorEnum._metadata = {
    "FIRE_RED": {'description': 'Fire red - fire equipment', 'meaning': 'HEX:C8102E', 'annotations': {'usage': 'fire extinguishers, alarms, hose reels', 'standard': 'ISO 7010'}},
    "PHOTOLUMINESCENT_GREEN": {'description': 'Photoluminescent green - emergency escape', 'meaning': 'HEX:7FFF00', 'annotations': {'usage': 'emergency exit signs, escape routes', 'property': 'glows in dark'}},
    "YELLOW_BLACK_STRIPES": {'description': 'Yellow with black stripes - fire hazard area', 'annotations': {'pattern': 'diagonal stripes', 'usage': 'fire hazard zones'}},
    "WHITE": {'description': 'White - fire protection water', 'meaning': 'HEX:FFFFFF', 'annotations': {'usage': 'water for fire protection'}},
    "BLUE": {'description': 'Blue - mandatory fire safety', 'meaning': 'HEX:005EB8', 'annotations': {'usage': 'mandatory fire safety equipment'}},
}

class MaritimeSignalColorEnum(RichEnum):
    """
    Maritime signal and navigation colors
    """
    # Enum members
    PORT_RED = "PORT_RED"
    STARBOARD_GREEN = "STARBOARD_GREEN"
    STERN_WHITE = "STERN_WHITE"
    MASTHEAD_WHITE = "MASTHEAD_WHITE"
    ALL_ROUND_WHITE = "ALL_ROUND_WHITE"
    YELLOW_TOWING = "YELLOW_TOWING"
    BLUE_FLASHING = "BLUE_FLASHING"

# Set metadata after class creation to avoid it becoming an enum member
MaritimeSignalColorEnum._metadata = {
    "PORT_RED": {'description': 'Port (left) red light', 'meaning': 'HEX:FF0000', 'annotations': {'side': 'port (left)', 'wavelength': '625-740 nm'}},
    "STARBOARD_GREEN": {'description': 'Starboard (right) green light', 'meaning': 'HEX:00FF00', 'annotations': {'side': 'starboard (right)', 'wavelength': '500-565 nm'}},
    "STERN_WHITE": {'description': 'Stern white light', 'meaning': 'HEX:FFFFFF', 'annotations': {'position': 'stern (rear)'}},
    "MASTHEAD_WHITE": {'description': 'Masthead white light', 'meaning': 'HEX:FFFFFF', 'annotations': {'position': 'masthead (forward)'}},
    "ALL_ROUND_WHITE": {'description': 'All-round white light', 'meaning': 'HEX:FFFFFF', 'annotations': {'visibility': '360 degrees'}},
    "YELLOW_TOWING": {'description': 'Yellow towing light', 'meaning': 'HEX:FFFF00', 'annotations': {'usage': 'vessel towing'}},
    "BLUE_FLASHING": {'description': 'Blue flashing light', 'meaning': 'HEX:0000FF', 'annotations': {'usage': 'law enforcement vessels', 'pattern': 'flashing'}},
}

class AviationLightColorEnum(RichEnum):
    """
    Aviation lighting colors
    """
    # Enum members
    RED_BEACON = "RED_BEACON"
    WHITE_STROBE = "WHITE_STROBE"
    GREEN_NAVIGATION = "GREEN_NAVIGATION"
    RED_NAVIGATION = "RED_NAVIGATION"
    WHITE_NAVIGATION = "WHITE_NAVIGATION"
    BLUE_TAXIWAY = "BLUE_TAXIWAY"
    YELLOW_RUNWAY = "YELLOW_RUNWAY"
    GREEN_THRESHOLD = "GREEN_THRESHOLD"
    RED_RUNWAY_END = "RED_RUNWAY_END"

# Set metadata after class creation to avoid it becoming an enum member
AviationLightColorEnum._metadata = {
    "RED_BEACON": {'description': 'Red obstruction light', 'meaning': 'HEX:FF0000', 'annotations': {'usage': 'obstruction marking', 'intensity': 'high intensity'}},
    "WHITE_STROBE": {'description': 'White anti-collision strobe', 'meaning': 'HEX:FFFFFF', 'annotations': {'usage': 'anti-collision', 'pattern': 'strobe'}},
    "GREEN_NAVIGATION": {'description': 'Green navigation light (right wing)', 'meaning': 'HEX:00FF00', 'annotations': {'position': 'right wing tip'}},
    "RED_NAVIGATION": {'description': 'Red navigation light (left wing)', 'meaning': 'HEX:FF0000', 'annotations': {'position': 'left wing tip'}},
    "WHITE_NAVIGATION": {'description': 'White navigation light (tail)', 'meaning': 'HEX:FFFFFF', 'annotations': {'position': 'tail'}},
    "BLUE_TAXIWAY": {'description': 'Blue taxiway edge lights', 'meaning': 'HEX:0000FF', 'annotations': {'usage': 'taxiway edges'}},
    "YELLOW_RUNWAY": {'description': 'Yellow runway markings', 'meaning': 'HEX:FFFF00', 'annotations': {'usage': 'runway centerline, hold positions'}},
    "GREEN_THRESHOLD": {'description': 'Green runway threshold lights', 'meaning': 'HEX:00FF00', 'annotations': {'usage': 'runway threshold'}},
    "RED_RUNWAY_END": {'description': 'Red runway end lights', 'meaning': 'HEX:FF0000', 'annotations': {'usage': 'runway end'}},
}

class ElectricalWireColorEnum(RichEnum):
    """
    Electrical wire color codes (US/International)
    """
    # Enum members
    BLACK_HOT = "BLACK_HOT"
    RED_HOT = "RED_HOT"
    BLUE_HOT = "BLUE_HOT"
    WHITE_NEUTRAL = "WHITE_NEUTRAL"
    GREEN_GROUND = "GREEN_GROUND"
    GREEN_YELLOW_GROUND = "GREEN_YELLOW_GROUND"
    BROWN_LIVE = "BROWN_LIVE"
    BLUE_NEUTRAL = "BLUE_NEUTRAL"
    GRAY_NEUTRAL = "GRAY_NEUTRAL"

# Set metadata after class creation to avoid it becoming an enum member
ElectricalWireColorEnum._metadata = {
    "BLACK_HOT": {'description': 'Black - hot/live wire (US)', 'meaning': 'HEX:000000', 'annotations': {'voltage': '120/240V', 'region': 'North America'}},
    "RED_HOT": {'description': 'Red - hot/live wire (US secondary)', 'meaning': 'HEX:FF0000', 'annotations': {'voltage': '120/240V', 'region': 'North America'}},
    "BLUE_HOT": {'description': 'Blue - hot/live wire (US tertiary)', 'meaning': 'HEX:0000FF', 'annotations': {'voltage': '120/240V', 'region': 'North America'}},
    "WHITE_NEUTRAL": {'description': 'White - neutral wire (US)', 'meaning': 'HEX:FFFFFF', 'annotations': {'function': 'neutral', 'region': 'North America'}},
    "GREEN_GROUND": {'description': 'Green - ground/earth wire', 'meaning': 'HEX:00FF00', 'annotations': {'function': 'ground/earth', 'region': 'universal'}},
    "GREEN_YELLOW_GROUND": {'description': 'Green with yellow stripe - ground/earth (International)', 'annotations': {'function': 'ground/earth', 'region': 'IEC standard', 'pattern': 'green with yellow stripe'}},
    "BROWN_LIVE": {'description': 'Brown - live wire (EU/IEC)', 'meaning': 'HEX:964B00', 'annotations': {'voltage': '230V', 'region': 'Europe/IEC'}},
    "BLUE_NEUTRAL": {'description': 'Blue - neutral wire (EU/IEC)', 'meaning': 'HEX:0000FF', 'annotations': {'function': 'neutral', 'region': 'Europe/IEC'}},
    "GRAY_NEUTRAL": {'description': 'Gray - neutral wire (alternative)', 'meaning': 'HEX:808080', 'annotations': {'function': 'neutral', 'region': 'some installations'}},
}

class BloodTypeEnum(RichEnum):
    """
    ABO and Rh blood group classifications
    """
    # Enum members
    A_POSITIVE = "A_POSITIVE"
    A_NEGATIVE = "A_NEGATIVE"
    B_POSITIVE = "B_POSITIVE"
    B_NEGATIVE = "B_NEGATIVE"
    AB_POSITIVE = "AB_POSITIVE"
    AB_NEGATIVE = "AB_NEGATIVE"
    O_POSITIVE = "O_POSITIVE"
    O_NEGATIVE = "O_NEGATIVE"

# Set metadata after class creation to avoid it becoming an enum member
BloodTypeEnum._metadata = {
    "A_POSITIVE": {'description': 'Blood type A, Rh positive', 'meaning': 'SNOMED:278149003', 'annotations': {'abo': 'A', 'rh': 'positive', 'can_receive': 'A+, A-, O+, O-', 'can_donate': 'A+, AB+'}},
    "A_NEGATIVE": {'description': 'Blood type A, Rh negative', 'meaning': 'SNOMED:278152006', 'annotations': {'abo': 'A', 'rh': 'negative', 'can_receive': 'A-, O-', 'can_donate': 'A+, A-, AB+, AB-'}},
    "B_POSITIVE": {'description': 'Blood type B, Rh positive', 'meaning': 'SNOMED:278150003', 'annotations': {'abo': 'B', 'rh': 'positive', 'can_receive': 'B+, B-, O+, O-', 'can_donate': 'B+, AB+'}},
    "B_NEGATIVE": {'description': 'Blood type B, Rh negative', 'meaning': 'SNOMED:278153001', 'annotations': {'abo': 'B', 'rh': 'negative', 'can_receive': 'B-, O-', 'can_donate': 'B+, B-, AB+, AB-'}},
    "AB_POSITIVE": {'description': 'Blood type AB, Rh positive (universal recipient)', 'meaning': 'SNOMED:278151004', 'annotations': {'abo': 'AB', 'rh': 'positive', 'can_receive': 'all types', 'can_donate': 'AB+', 'special': 'universal recipient'}},
    "AB_NEGATIVE": {'description': 'Blood type AB, Rh negative', 'meaning': 'SNOMED:278154007', 'annotations': {'abo': 'AB', 'rh': 'negative', 'can_receive': 'A-, B-, AB-, O-', 'can_donate': 'AB+, AB-'}},
    "O_POSITIVE": {'description': 'Blood type O, Rh positive', 'meaning': 'SNOMED:278147001', 'annotations': {'abo': 'O', 'rh': 'positive', 'can_receive': 'O+, O-', 'can_donate': 'A+, B+, AB+, O+'}},
    "O_NEGATIVE": {'description': 'Blood type O, Rh negative (universal donor)', 'meaning': 'SNOMED:278148006', 'annotations': {'abo': 'O', 'rh': 'negative', 'can_receive': 'O-', 'can_donate': 'all types', 'special': 'universal donor'}},
}

class AnatomicalSystemEnum(RichEnum):
    """
    Major anatomical systems of the body
    """
    # Enum members
    CARDIOVASCULAR = "CARDIOVASCULAR"
    RESPIRATORY = "RESPIRATORY"
    NERVOUS = "NERVOUS"
    DIGESTIVE = "DIGESTIVE"
    MUSCULOSKELETAL = "MUSCULOSKELETAL"
    INTEGUMENTARY = "INTEGUMENTARY"
    ENDOCRINE = "ENDOCRINE"
    URINARY = "URINARY"
    REPRODUCTIVE = "REPRODUCTIVE"
    IMMUNE = "IMMUNE"
    HEMATOLOGIC = "HEMATOLOGIC"

# Set metadata after class creation to avoid it becoming an enum member
AnatomicalSystemEnum._metadata = {
    "CARDIOVASCULAR": {'meaning': 'UBERON:0004535', 'annotations': {'components': 'heart, arteries, veins, capillaries'}, 'aliases': ['cardiovascular system']},
    "RESPIRATORY": {'meaning': 'UBERON:0001004', 'annotations': {'components': 'lungs, trachea, bronchi, diaphragm'}, 'aliases': ['respiratory system']},
    "NERVOUS": {'meaning': 'UBERON:0001016', 'annotations': {'components': 'brain, spinal cord, nerves'}, 'aliases': ['nervous system']},
    "DIGESTIVE": {'meaning': 'UBERON:0001007', 'annotations': {'components': 'mouth, esophagus, stomach, intestines, liver, pancreas'}, 'aliases': ['digestive system']},
    "MUSCULOSKELETAL": {'meaning': 'UBERON:0002204', 'annotations': {'components': 'bones, muscles, tendons, ligaments, cartilage'}, 'aliases': ['musculoskeletal system']},
    "INTEGUMENTARY": {'meaning': 'UBERON:0002416', 'annotations': {'components': 'skin, hair, nails, glands'}, 'aliases': ['integumental system']},
    "ENDOCRINE": {'meaning': 'UBERON:0000949', 'annotations': {'components': 'pituitary, thyroid, adrenals, pancreas'}, 'aliases': ['endocrine system']},
    "URINARY": {'meaning': 'UBERON:0001008', 'annotations': {'components': 'kidneys, ureters, bladder, urethra'}, 'aliases': ['renal system']},
    "REPRODUCTIVE": {'meaning': 'UBERON:0000990', 'annotations': {'components': 'gonads, ducts, external genitalia'}, 'aliases': ['reproductive system']},
    "IMMUNE": {'meaning': 'UBERON:0002405', 'annotations': {'components': 'lymph nodes, spleen, thymus, bone marrow'}, 'aliases': ['immune system']},
    "HEMATOLOGIC": {'meaning': 'UBERON:0002390', 'annotations': {'components': 'blood, bone marrow, spleen'}, 'aliases': ['hematopoietic system']},
}

class MedicalSpecialtyEnum(RichEnum):
    # Enum members
    ANESTHESIOLOGY = "ANESTHESIOLOGY"
    CARDIOLOGY = "CARDIOLOGY"
    DERMATOLOGY = "DERMATOLOGY"
    EMERGENCY_MEDICINE = "EMERGENCY_MEDICINE"
    ENDOCRINOLOGY = "ENDOCRINOLOGY"
    FAMILY_MEDICINE = "FAMILY_MEDICINE"
    GASTROENTEROLOGY = "GASTROENTEROLOGY"
    HEMATOLOGY = "HEMATOLOGY"
    INFECTIOUS_DISEASE = "INFECTIOUS_DISEASE"
    INTERNAL_MEDICINE = "INTERNAL_MEDICINE"
    NEPHROLOGY = "NEPHROLOGY"
    NEUROLOGY = "NEUROLOGY"
    OBSTETRICS_GYNECOLOGY = "OBSTETRICS_GYNECOLOGY"
    ONCOLOGY = "ONCOLOGY"
    OPHTHALMOLOGY = "OPHTHALMOLOGY"
    ORTHOPEDICS = "ORTHOPEDICS"
    OTOLARYNGOLOGY = "OTOLARYNGOLOGY"
    PATHOLOGY = "PATHOLOGY"
    PEDIATRICS = "PEDIATRICS"
    PSYCHIATRY = "PSYCHIATRY"
    PULMONOLOGY = "PULMONOLOGY"
    RADIOLOGY = "RADIOLOGY"
    RHEUMATOLOGY = "RHEUMATOLOGY"
    SURGERY = "SURGERY"
    UROLOGY = "UROLOGY"

# Set metadata after class creation to avoid it becoming an enum member
MedicalSpecialtyEnum._metadata = {
}

class DrugRouteEnum(RichEnum):
    # Enum members
    ORAL = "ORAL"
    INTRAVENOUS = "INTRAVENOUS"
    INTRAMUSCULAR = "INTRAMUSCULAR"
    SUBCUTANEOUS = "SUBCUTANEOUS"
    TOPICAL = "TOPICAL"
    INHALATION = "INHALATION"
    RECTAL = "RECTAL"
    INTRANASAL = "INTRANASAL"
    TRANSDERMAL = "TRANSDERMAL"
    SUBLINGUAL = "SUBLINGUAL"
    EPIDURAL = "EPIDURAL"
    INTRATHECAL = "INTRATHECAL"
    OPHTHALMIC = "OPHTHALMIC"
    OTIC = "OTIC"

# Set metadata after class creation to avoid it becoming an enum member
DrugRouteEnum._metadata = {
    "ORAL": {'meaning': 'NCIT:C38288', 'annotations': {'abbreviation': 'PO', 'absorption': 'GI tract'}, 'aliases': ['Oral Route of Administration']},
    "INTRAVENOUS": {'meaning': 'NCIT:C38276', 'annotations': {'abbreviation': 'IV', 'onset': 'immediate'}, 'aliases': ['Intravenous Route of Administration']},
    "INTRAMUSCULAR": {'meaning': 'NCIT:C28161', 'annotations': {'abbreviation': 'IM', 'sites': 'deltoid, gluteus, vastus lateralis'}, 'aliases': ['Intramuscular Route of Administration']},
    "SUBCUTANEOUS": {'meaning': 'NCIT:C38299', 'annotations': {'abbreviation': 'SC, SubQ', 'absorption': 'slow'}, 'aliases': ['Subcutaneous Route of Administration']},
    "TOPICAL": {'meaning': 'NCIT:C38304', 'annotations': {'forms': 'cream, ointment, gel'}, 'aliases': ['Topical Route of Administration']},
    "INHALATION": {'meaning': 'NCIT:C38216', 'annotations': {'devices': 'inhaler, nebulizer'}, 'aliases': ['Inhalation Route of Administration']},
    "RECTAL": {'meaning': 'NCIT:C38295', 'annotations': {'forms': 'suppository, enema'}, 'aliases': ['Rectal Route of Administration']},
    "INTRANASAL": {'meaning': 'NCIT:C38284', 'annotations': {'forms': 'spray, drops'}, 'aliases': ['Nasal Route of Administration']},
    "TRANSDERMAL": {'meaning': 'NCIT:C38305', 'annotations': {'forms': 'patch'}, 'aliases': ['Transdermal Route of Administration']},
    "SUBLINGUAL": {'meaning': 'NCIT:C38300', 'annotations': {'absorption': 'rapid'}, 'aliases': ['Sublingual Route of Administration']},
    "EPIDURAL": {'meaning': 'NCIT:C38243', 'annotations': {'use': 'anesthesia, analgesia'}, 'aliases': ['Intraepidermal Route of Administration']},
    "INTRATHECAL": {'meaning': 'NCIT:C38277', 'annotations': {'use': 'CNS drugs'}, 'aliases': ['Intraventricular Route of Administration']},
    "OPHTHALMIC": {'meaning': 'NCIT:C38287', 'annotations': {'forms': 'drops, ointment'}, 'aliases': ['Ophthalmic Route of Administration']},
    "OTIC": {'meaning': 'NCIT:C38192', 'annotations': {'forms': 'drops'}, 'aliases': ['Auricular Route of Administration']},
}

class VitalSignEnum(RichEnum):
    # Enum members
    HEART_RATE = "HEART_RATE"
    BLOOD_PRESSURE_SYSTOLIC = "BLOOD_PRESSURE_SYSTOLIC"
    BLOOD_PRESSURE_DIASTOLIC = "BLOOD_PRESSURE_DIASTOLIC"
    RESPIRATORY_RATE = "RESPIRATORY_RATE"
    TEMPERATURE = "TEMPERATURE"
    OXYGEN_SATURATION = "OXYGEN_SATURATION"
    PAIN_SCALE = "PAIN_SCALE"

# Set metadata after class creation to avoid it becoming an enum member
VitalSignEnum._metadata = {
    "HEART_RATE": {'meaning': 'LOINC:8867-4', 'annotations': {'normal_range': '60-100 bpm', 'units': 'beats/min'}},
    "BLOOD_PRESSURE_SYSTOLIC": {'meaning': 'LOINC:8480-6', 'annotations': {'normal_range': '<120 mmHg', 'units': 'mmHg'}},
    "BLOOD_PRESSURE_DIASTOLIC": {'meaning': 'LOINC:8462-4', 'annotations': {'normal_range': '<80 mmHg', 'units': 'mmHg'}},
    "RESPIRATORY_RATE": {'meaning': 'LOINC:9279-1', 'annotations': {'normal_range': '12-20 breaths/min', 'units': 'breaths/min'}},
    "TEMPERATURE": {'meaning': 'LOINC:8310-5', 'annotations': {'normal_range': '36.5-37.5°C', 'units': '°C or °F'}},
    "OXYGEN_SATURATION": {'meaning': 'LOINC:2708-6', 'annotations': {'normal_range': '95-100%', 'units': '%'}},
    "PAIN_SCALE": {'meaning': 'LOINC:38208-5', 'annotations': {'scale': '0-10', 'type': 'subjective'}},
}

class DiagnosticTestTypeEnum(RichEnum):
    # Enum members
    BLOOD_TEST = "BLOOD_TEST"
    URINE_TEST = "URINE_TEST"
    IMAGING_XRAY = "IMAGING_XRAY"
    IMAGING_CT = "IMAGING_CT"
    IMAGING_MRI = "IMAGING_MRI"
    IMAGING_ULTRASOUND = "IMAGING_ULTRASOUND"
    IMAGING_PET = "IMAGING_PET"
    ECG = "ECG"
    EEG = "EEG"
    BIOPSY = "BIOPSY"
    ENDOSCOPY = "ENDOSCOPY"
    GENETIC_TEST = "GENETIC_TEST"

# Set metadata after class creation to avoid it becoming an enum member
DiagnosticTestTypeEnum._metadata = {
    "BLOOD_TEST": {'meaning': 'NCIT:C15189', 'annotations': {'samples': 'serum, plasma, whole blood'}, 'aliases': ['Biopsy Procedure']},
    "URINE_TEST": {'annotations': {'types': 'urinalysis, culture, drug screen'}, 'aliases': ['Tissue Factor']},
    "IMAGING_XRAY": {'meaning': 'NCIT:C17262', 'annotations': {'radiation': 'yes'}, 'aliases': ['X-Ray']},
    "IMAGING_CT": {'meaning': 'NCIT:C17204', 'annotations': {'radiation': 'yes'}, 'aliases': ['Computed Tomography']},
    "IMAGING_MRI": {'meaning': 'NCIT:C16809', 'annotations': {'radiation': 'no'}, 'aliases': ['Magnetic Resonance Imaging']},
    "IMAGING_ULTRASOUND": {'meaning': 'NCIT:C17230', 'annotations': {'radiation': 'no'}, 'aliases': ['Ultrasound Imaging']},
    "IMAGING_PET": {'meaning': 'NCIT:C17007', 'annotations': {'uses': 'radiotracer'}, 'aliases': ['Positron Emission Tomography']},
    "ECG": {'meaning': 'NCIT:C38054', 'annotations': {'measures': 'heart electrical activity'}, 'aliases': ['Electroencephalography']},
    "EEG": {'annotations': {'measures': 'brain electrical activity'}, 'aliases': ['Djibouti']},
    "BIOPSY": {'meaning': 'NCIT:C15189', 'annotations': {'invasive': 'yes'}, 'aliases': ['Biopsy Procedure']},
    "ENDOSCOPY": {'meaning': 'NCIT:C16546', 'annotations': {'types': 'colonoscopy, gastroscopy, bronchoscopy'}, 'aliases': ['Endoscopic Procedure']},
    "GENETIC_TEST": {'meaning': 'NCIT:C15709', 'annotations': {'types': 'karyotype, sequencing, PCR'}, 'aliases': ['Genetic Testing']},
}

class SymptomSeverityEnum(RichEnum):
    # Enum members
    ABSENT = "ABSENT"
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    LIFE_THREATENING = "LIFE_THREATENING"

# Set metadata after class creation to avoid it becoming an enum member
SymptomSeverityEnum._metadata = {
    "ABSENT": {'annotations': {'grade': '0'}, 'aliases': ['Blood group B']},
    "MILD": {'meaning': 'HP:0012825', 'annotations': {'grade': '1', 'impact': 'minimal daily activity limitation'}},
    "MODERATE": {'meaning': 'HP:0012826', 'annotations': {'grade': '2', 'impact': 'some daily activity limitation'}},
    "SEVERE": {'meaning': 'HP:0012828', 'annotations': {'grade': '3', 'impact': 'significant daily activity limitation'}},
    "LIFE_THREATENING": {'annotations': {'grade': '4', 'impact': 'urgent intervention required'}, 'aliases': ['Profound']},
}

class AllergyTypeEnum(RichEnum):
    # Enum members
    DRUG = "DRUG"
    FOOD = "FOOD"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    CONTACT = "CONTACT"
    INSECT = "INSECT"
    ANAPHYLAXIS = "ANAPHYLAXIS"

# Set metadata after class creation to avoid it becoming an enum member
AllergyTypeEnum._metadata = {
    "DRUG": {'meaning': 'NCIT:C3114', 'annotations': {'examples': 'penicillin, sulfa drugs'}, 'aliases': ['Hypersensitivity']},
    "FOOD": {'annotations': {'common': 'nuts, shellfish, eggs, milk'}},
    "ENVIRONMENTAL": {'annotations': {'examples': 'pollen, dust, mold'}},
    "CONTACT": {'annotations': {'examples': 'latex, nickel, poison ivy'}},
    "INSECT": {'annotations': {'examples': 'bee, wasp, hornet'}},
    "ANAPHYLAXIS": {'annotations': {'severity': 'life-threatening'}},
}

class VaccineTypeEnum(RichEnum):
    # Enum members
    LIVE_ATTENUATED = "LIVE_ATTENUATED"
    INACTIVATED = "INACTIVATED"
    SUBUNIT = "SUBUNIT"
    TOXOID = "TOXOID"
    MRNA = "MRNA"
    VIRAL_VECTOR = "VIRAL_VECTOR"

# Set metadata after class creation to avoid it becoming an enum member
VaccineTypeEnum._metadata = {
    "LIVE_ATTENUATED": {'annotations': {'examples': 'MMR, varicella, yellow fever'}},
    "INACTIVATED": {'annotations': {'examples': 'flu shot, hepatitis A, rabies'}},
    "SUBUNIT": {'annotations': {'examples': 'hepatitis B, HPV, pertussis'}},
    "TOXOID": {'annotations': {'examples': 'diphtheria, tetanus'}},
    "MRNA": {'annotations': {'examples': 'COVID-19 (Pfizer, Moderna)'}},
    "VIRAL_VECTOR": {'annotations': {'examples': 'COVID-19 (J&J, AstraZeneca)'}},
}

class BMIClassificationEnum(RichEnum):
    # Enum members
    UNDERWEIGHT = "UNDERWEIGHT"
    NORMAL_WEIGHT = "NORMAL_WEIGHT"
    OVERWEIGHT = "OVERWEIGHT"
    OBESE_CLASS_I = "OBESE_CLASS_I"
    OBESE_CLASS_II = "OBESE_CLASS_II"
    OBESE_CLASS_III = "OBESE_CLASS_III"

# Set metadata after class creation to avoid it becoming an enum member
BMIClassificationEnum._metadata = {
    "UNDERWEIGHT": {'annotations': {'bmi_range': '<18.5'}},
    "NORMAL_WEIGHT": {'annotations': {'bmi_range': '18.5-24.9'}},
    "OVERWEIGHT": {'annotations': {'bmi_range': '25.0-29.9'}},
    "OBESE_CLASS_I": {'annotations': {'bmi_range': '30.0-34.9'}},
    "OBESE_CLASS_II": {'annotations': {'bmi_range': '35.0-39.9'}},
    "OBESE_CLASS_III": {'annotations': {'bmi_range': '≥40.0', 'aliases': 'morbid obesity'}},
}

class MRIModalityEnum(RichEnum):
    """
    MRI imaging modalities and techniques
    """
    # Enum members
    STRUCTURAL_T1 = "STRUCTURAL_T1"
    STRUCTURAL_T2 = "STRUCTURAL_T2"
    FLAIR = "FLAIR"
    BOLD_FMRI = "BOLD_FMRI"
    ASL = "ASL"
    DWI = "DWI"
    DTI = "DTI"
    PERFUSION_DSC = "PERFUSION_DSC"
    PERFUSION_DCE = "PERFUSION_DCE"
    SWI = "SWI"
    TASK_FMRI = "TASK_FMRI"
    RESTING_STATE_FMRI = "RESTING_STATE_FMRI"
    FUNCTIONAL_CONNECTIVITY = "FUNCTIONAL_CONNECTIVITY"

# Set metadata after class creation to avoid it becoming an enum member
MRIModalityEnum._metadata = {
    "STRUCTURAL_T1": {'description': 'High-resolution anatomical imaging with T1 contrast', 'meaning': 'NCIT:C116455', 'annotations': {'contrast_mechanism': 'T1 relaxation', 'typical_use': 'anatomical reference, volumetric analysis', 'tissue_contrast': 'good gray/white matter contrast'}, 'aliases': ['High Field Strength Magnetic Resonance Imaging']},
    "STRUCTURAL_T2": {'description': 'Structural imaging with T2 contrast', 'meaning': 'NCIT:C116456', 'annotations': {'contrast_mechanism': 'T2 relaxation', 'typical_use': 'pathology detection, CSF visualization', 'tissue_contrast': 'good fluid contrast'}, 'aliases': ['Low Field Strength Magnetic Resonance Imaging']},
    "FLAIR": {'description': 'T2-weighted sequence with CSF signal suppressed', 'meaning': 'NCIT:C82392', 'annotations': {'contrast_mechanism': 'T2 with fluid suppression', 'typical_use': 'lesion detection, periventricular pathology', 'advantage': 'suppresses CSF signal'}},
    "BOLD_FMRI": {'description': 'Functional MRI based on blood oxygenation changes', 'meaning': 'NCIT:C17958', 'annotations': {'contrast_mechanism': 'BOLD signal', 'typical_use': 'brain activation mapping', 'temporal_resolution': 'seconds'}, 'aliases': ['Functional Magnetic Resonance Imaging']},
    "ASL": {'description': 'Perfusion imaging using magnetically labeled blood', 'meaning': 'NCIT:C116450', 'annotations': {'contrast_mechanism': 'arterial blood labeling', 'typical_use': 'cerebral blood flow measurement', 'advantage': 'no contrast agent required'}, 'aliases': ['Arterial Spin Labeling Magnetic Resonance Imaging']},
    "DWI": {'description': 'Imaging sensitive to water molecule diffusion', 'meaning': 'mesh:D038524', 'annotations': {'contrast_mechanism': 'water diffusion', 'typical_use': 'stroke detection, fiber tracking', 'parameter': 'apparent diffusion coefficient'}},
    "DTI": {'description': 'Advanced diffusion imaging with directional information', 'meaning': 'NCIT:C64862', 'annotations': {'contrast_mechanism': 'directional diffusion', 'typical_use': 'white matter tractography', 'parameters': 'fractional anisotropy, mean diffusivity'}},
    "PERFUSION_DSC": {'description': 'Perfusion imaging using contrast agent bolus', 'meaning': 'NCIT:C116459', 'annotations': {'contrast_mechanism': 'contrast agent dynamics', 'typical_use': 'cerebral blood flow, blood volume', 'requires': 'gadolinium contrast'}, 'aliases': ['Secretin-Enhanced Magnetic Resonance Imaging']},
    "PERFUSION_DCE": {'description': 'Perfusion imaging with pharmacokinetic modeling', 'meaning': 'NCIT:C116458', 'annotations': {'contrast_mechanism': 'contrast enhancement kinetics', 'typical_use': 'blood-brain barrier permeability', 'analysis': 'pharmacokinetic modeling'}, 'aliases': ['Multiparametric Magnetic Resonance Imaging']},
    "SWI": {'description': 'High-resolution venography and iron detection', 'meaning': 'NCIT:C121377', 'annotations': {'contrast_mechanism': 'magnetic susceptibility', 'typical_use': 'venography, microbleeds, iron deposits', 'strength': 'high field preferred'}},
    "TASK_FMRI": {'description': 'fMRI during specific cognitive or motor tasks', 'meaning': 'NCIT:C178023', 'annotations': {'paradigm': 'stimulus-response', 'typical_use': 'localization of brain functions', 'analysis': 'statistical parametric mapping'}, 'aliases': ['Task Functional Magnetic Resonance Imaging']},
    "RESTING_STATE_FMRI": {'description': 'fMRI acquired at rest without explicit tasks', 'meaning': 'NCIT:C178024', 'annotations': {'paradigm': 'no task', 'typical_use': 'functional connectivity analysis', 'networks': 'default mode, attention, executive'}, 'aliases': ['Resting Functional Magnetic Resonance Imaging']},
    "FUNCTIONAL_CONNECTIVITY": {'description': 'Analysis of temporal correlations between brain regions', 'meaning': 'NCIT:C116454', 'annotations': {'analysis_type': 'connectivity mapping', 'typical_use': 'network analysis', 'metric': 'correlation coefficients'}, 'aliases': ['Functional Connectivity Magnetic Resonance Imaging']},
}

class MRISequenceTypeEnum(RichEnum):
    """
    MRI pulse sequence types
    """
    # Enum members
    GRADIENT_ECHO = "GRADIENT_ECHO"
    SPIN_ECHO = "SPIN_ECHO"
    EPI = "EPI"
    MPRAGE = "MPRAGE"
    SPACE = "SPACE"
    TRUFI = "TRUFI"

# Set metadata after class creation to avoid it becoming an enum member
MRISequenceTypeEnum._metadata = {
    "GRADIENT_ECHO": {'description': 'Fast imaging sequence using gradient reversal', 'meaning': 'NCIT:C154542', 'annotations': {'speed': 'fast', 'typical_use': 'T2*, functional imaging', 'artifact_sensitivity': 'susceptible to magnetic field inhomogeneity'}, 'aliases': ['Gradient Echo MRI']},
    "SPIN_ECHO": {'description': 'Sequence using 180-degree refocusing pulse', 'meaning': 'CHMO:0001868', 'annotations': {'speed': 'slower', 'typical_use': 'T2 imaging, reduced artifacts', 'artifact_resistance': 'good'}, 'aliases': ['spin echo pulse sequence']},
    "EPI": {'description': 'Ultrafast imaging sequence', 'meaning': 'NCIT:C17558', 'annotations': {'speed': 'very fast', 'typical_use': 'functional MRI, diffusion imaging', 'temporal_resolution': 'subsecond'}},
    "MPRAGE": {'description': 'T1-weighted 3D sequence with preparation pulse', 'meaning': 'NCIT:C118462', 'annotations': {'image_type': 'T1-weighted', 'typical_use': 'high-resolution anatomical imaging', 'dimension': '3D'}, 'aliases': ['Magnetization-Prepared Rapid Gradient Echo MRI']},
    "SPACE": {'description': '3D turbo spin echo sequence', 'annotations': {'image_type': 'T2-weighted', 'typical_use': 'high-resolution T2 imaging', 'dimension': '3D'}},
    "TRUFI": {'description': 'Balanced steady-state free precession sequence', 'meaning': 'NCIT:C200534', 'annotations': {'contrast': 'mixed T1/T2', 'typical_use': 'cardiac imaging, fast scanning', 'signal': 'high'}, 'aliases': ['Constructive Interference In Steady State']},
}

class MRIContrastTypeEnum(RichEnum):
    """
    MRI image contrast mechanisms
    """
    # Enum members
    T1_WEIGHTED = "T1_WEIGHTED"
    T2_WEIGHTED = "T2_WEIGHTED"
    T2_STAR = "T2_STAR"
    PROTON_DENSITY = "PROTON_DENSITY"
    DIFFUSION_WEIGHTED = "DIFFUSION_WEIGHTED"
    PERFUSION_WEIGHTED = "PERFUSION_WEIGHTED"

# Set metadata after class creation to avoid it becoming an enum member
MRIContrastTypeEnum._metadata = {
    "T1_WEIGHTED": {'description': 'Image contrast based on T1 relaxation times', 'meaning': 'NCIT:C180727', 'annotations': {'tissue_contrast': 'gray matter darker than white matter', 'typical_use': 'anatomical structure'}, 'aliases': ['T1-Weighted Magnetic Resonance Imaging']},
    "T2_WEIGHTED": {'description': 'Image contrast based on T2 relaxation times', 'meaning': 'NCIT:C180729', 'annotations': {'tissue_contrast': 'CSF bright, gray matter brighter than white', 'typical_use': 'pathology detection'}, 'aliases': ['T2-Weighted Magnetic Resonance Imaging']},
    "T2_STAR": {'description': 'Image contrast sensitive to magnetic susceptibility', 'meaning': 'NCIT:C156447', 'annotations': {'sensitivity': 'blood, iron, air-tissue interfaces', 'typical_use': 'functional imaging, venography'}, 'aliases': ['T2 (Observed)-Weighted Imaging']},
    "PROTON_DENSITY": {'description': 'Image contrast based on hydrogen density', 'meaning': 'NCIT:C170797', 'annotations': {'tissue_contrast': 'proportional to water content', 'typical_use': 'joint imaging, some brain pathology'}, 'aliases': ['Proton Density MRI']},
    "DIFFUSION_WEIGHTED": {'description': 'Image contrast based on water diffusion', 'meaning': 'NCIT:C111116', 'annotations': {'sensitivity': 'molecular motion', 'typical_use': 'stroke, tumor cellularity'}, 'aliases': ['Diffusion Weighted Imaging']},
    "PERFUSION_WEIGHTED": {'description': 'Image contrast based on blood flow dynamics', 'meaning': 'mesh:D000098642', 'annotations': {'measurement': 'cerebral blood flow/volume', 'typical_use': 'stroke, tumor vascularity'}},
}

class FMRIParadigmTypeEnum(RichEnum):
    """
    fMRI experimental paradigm types
    """
    # Enum members
    BLOCK_DESIGN = "BLOCK_DESIGN"
    EVENT_RELATED = "EVENT_RELATED"
    MIXED_DESIGN = "MIXED_DESIGN"
    RESTING_STATE = "RESTING_STATE"
    NATURALISTIC = "NATURALISTIC"

# Set metadata after class creation to avoid it becoming an enum member
FMRIParadigmTypeEnum._metadata = {
    "BLOCK_DESIGN": {'description': 'Alternating blocks of task and rest conditions', 'meaning': 'STATO:0000046', 'annotations': {'duration': 'typically 15-30 seconds per block', 'advantage': 'high statistical power', 'typical_use': 'robust activation detection'}},
    "EVENT_RELATED": {'description': 'Brief stimuli presented at varying intervals', 'meaning': 'EDAM:topic_3678', 'annotations': {'duration': 'single events (seconds)', 'advantage': 'flexible timing, event separation', 'typical_use': 'studying cognitive processes'}, 'aliases': ['Experimental design and studies']},
    "MIXED_DESIGN": {'description': 'Combination of block and event-related elements', 'meaning': 'EDAM:topic_3678', 'annotations': {'flexibility': 'high', 'advantage': 'sustained and transient responses', 'complexity': 'high'}, 'aliases': ['Experimental design and studies']},
    "RESTING_STATE": {'description': 'No explicit task, spontaneous brain activity', 'meaning': 'NCIT:C178024', 'annotations': {'instruction': 'rest, eyes open/closed', 'duration': 'typically 5-10 minutes', 'analysis': 'functional connectivity'}, 'aliases': ['Resting Functional Magnetic Resonance Imaging']},
    "NATURALISTIC": {'description': 'Ecologically valid stimuli (movies, stories)', 'meaning': 'EDAM:topic_3678', 'annotations': {'stimulus_type': 'complex, realistic', 'advantage': 'ecological validity', 'analysis': 'inter-subject correlation'}, 'aliases': ['Experimental design and studies']},
}

class RaceOMB1997Enum(RichEnum):
    """
    Race categories following OMB 1997 standards used by NIH and federal agencies.
Respondents may select multiple races.
    """
    # Enum members
    AMERICAN_INDIAN_OR_ALASKA_NATIVE = "AMERICAN_INDIAN_OR_ALASKA_NATIVE"
    ASIAN = "ASIAN"
    BLACK_OR_AFRICAN_AMERICAN = "BLACK_OR_AFRICAN_AMERICAN"
    NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = "NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER"
    WHITE = "WHITE"
    MORE_THAN_ONE_RACE = "MORE_THAN_ONE_RACE"
    UNKNOWN_OR_NOT_REPORTED = "UNKNOWN_OR_NOT_REPORTED"

# Set metadata after class creation to avoid it becoming an enum member
RaceOMB1997Enum._metadata = {
    "AMERICAN_INDIAN_OR_ALASKA_NATIVE": {'description': 'A person having origins in any of the original peoples of North and South America (including Central America), and who maintains tribal affiliation or community attachment', 'meaning': 'NCIT:C41259', 'annotations': {'omb_code': '1002-5'}},
    "ASIAN": {'description': 'A person having origins in any of the original peoples of the Far East, Southeast Asia, or the Indian subcontinent', 'meaning': 'NCIT:C41260', 'annotations': {'omb_code': '2028-9', 'includes': 'Cambodia, China, India, Japan, Korea, Malaysia, Pakistan, Philippine Islands, Thailand, Vietnam'}},
    "BLACK_OR_AFRICAN_AMERICAN": {'description': 'A person having origins in any of the black racial groups of Africa', 'meaning': 'NCIT:C16352', 'annotations': {'omb_code': '2054-5'}},
    "NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER": {'description': 'A person having origins in any of the original peoples of Hawaii, Guam, Samoa, or other Pacific Islands', 'meaning': 'NCIT:C41219', 'annotations': {'omb_code': '2076-8'}},
    "WHITE": {'description': 'A person having origins in any of the original peoples of Europe, the Middle East, or North Africa', 'meaning': 'NCIT:C41261', 'annotations': {'omb_code': '2106-3'}},
    "MORE_THAN_ONE_RACE": {'description': 'Person identifies with more than one race category', 'meaning': 'NCIT:C67109', 'annotations': {'note': 'Added after 1997 revision to allow multiple race reporting'}},
    "UNKNOWN_OR_NOT_REPORTED": {'description': 'Race not known, not reported, or declined to answer', 'meaning': 'NCIT:C17998', 'annotations': {'aliases': 'Unknown, Not Reported, Prefer not to answer'}},
}

class EthnicityOMB1997Enum(RichEnum):
    """
    Ethnicity categories following OMB 1997 standards used by NIH and federal agencies
    """
    # Enum members
    HISPANIC_OR_LATINO = "HISPANIC_OR_LATINO"
    NOT_HISPANIC_OR_LATINO = "NOT_HISPANIC_OR_LATINO"
    UNKNOWN_OR_NOT_REPORTED = "UNKNOWN_OR_NOT_REPORTED"

# Set metadata after class creation to avoid it becoming an enum member
EthnicityOMB1997Enum._metadata = {
    "HISPANIC_OR_LATINO": {'description': 'A person of Cuban, Mexican, Puerto Rican, South or Central American, or other Spanish culture or origin, regardless of race', 'meaning': 'NCIT:C17459', 'annotations': {'omb_code': '2135-2'}},
    "NOT_HISPANIC_OR_LATINO": {'description': 'A person not of Hispanic or Latino origin', 'meaning': 'NCIT:C41222', 'annotations': {'omb_code': '2186-5'}},
    "UNKNOWN_OR_NOT_REPORTED": {'description': 'Ethnicity not known, not reported, or declined to answer', 'meaning': 'NCIT:C17998', 'annotations': {'aliases': 'Unknown, Not Reported, Prefer not to answer'}},
}

class BiologicalSexEnum(RichEnum):
    """
    Biological sex assigned at birth based on anatomical and physiological traits.
Required by NIH as a biological variable in research.
    """
    # Enum members
    MALE = "MALE"
    FEMALE = "FEMALE"
    INTERSEX = "INTERSEX"
    UNKNOWN_OR_NOT_REPORTED = "UNKNOWN_OR_NOT_REPORTED"

# Set metadata after class creation to avoid it becoming an enum member
BiologicalSexEnum._metadata = {
    "MALE": {'description': 'Male sex assigned at birth', 'meaning': 'PATO:0000384'},
    "FEMALE": {'description': 'Female sex assigned at birth', 'meaning': 'PATO:0000383'},
    "INTERSEX": {'description': "Born with reproductive or sexual anatomy that doesn't fit typical definitions of male or female", 'meaning': 'NCIT:C45908', 'annotations': {'prevalence': '0.018% to 1.7%', 'note': 'May be assigned male or female at birth'}},
    "UNKNOWN_OR_NOT_REPORTED": {'description': 'Sex not known, not reported, or declined to answer', 'meaning': 'NCIT:C17998'},
}

class AgeGroupEnum(RichEnum):
    """
    Standard age groups used in NIH clinical research, particularly NINDS CDEs
    """
    # Enum members
    NEONATE = "NEONATE"
    INFANT = "INFANT"
    YOUNG_PEDIATRIC = "YOUNG_PEDIATRIC"
    PEDIATRIC = "PEDIATRIC"
    ADOLESCENT = "ADOLESCENT"
    YOUNG_ADULT = "YOUNG_ADULT"
    ADULT = "ADULT"
    OLDER_ADULT = "OLDER_ADULT"

# Set metadata after class creation to avoid it becoming an enum member
AgeGroupEnum._metadata = {
    "NEONATE": {'description': 'Birth to 28 days', 'meaning': 'NCIT:C16731', 'annotations': {'max_age_days': 28}},
    "INFANT": {'description': '29 days to less than 1 year', 'meaning': 'NCIT:C27956', 'annotations': {'min_age_days': 29, 'max_age_years': 1}},
    "YOUNG_PEDIATRIC": {'description': '0 to 5 years (NINDS CDE definition)', 'meaning': 'NCIT:C39299', 'annotations': {'min_age_years': 0, 'max_age_years': 5, 'ninds_category': True}},
    "PEDIATRIC": {'description': '6 to 12 years (NINDS CDE definition)', 'meaning': 'NCIT:C16423', 'annotations': {'min_age_years': 6, 'max_age_years': 12, 'ninds_category': True}},
    "ADOLESCENT": {'description': '13 to 17 years', 'meaning': 'NCIT:C27954', 'annotations': {'min_age_years': 13, 'max_age_years': 17}},
    "YOUNG_ADULT": {'description': '18 to 24 years', 'meaning': 'NCIT:C91107', 'annotations': {'min_age_years': 18, 'max_age_years': 24}},
    "ADULT": {'description': '25 to 64 years', 'meaning': 'NCIT:C17600', 'annotations': {'min_age_years': 25, 'max_age_years': 64}},
    "OLDER_ADULT": {'description': '65 years and older', 'meaning': 'NCIT:C16268', 'annotations': {'min_age_years': 65, 'aliases': 'Geriatric, Elderly, Senior'}},
}

class ParticipantVitalStatusEnum(RichEnum):
    """
    Vital status of a research participant in clinical studies
    """
    # Enum members
    ALIVE = "ALIVE"
    DECEASED = "DECEASED"
    UNKNOWN = "UNKNOWN"

# Set metadata after class creation to avoid it becoming an enum member
ParticipantVitalStatusEnum._metadata = {
    "ALIVE": {'description': 'Participant is living', 'meaning': 'NCIT:C37987'},
    "DECEASED": {'description': 'Participant is deceased', 'meaning': 'NCIT:C28554'},
    "UNKNOWN": {'description': 'Vital status unknown or lost to follow-up', 'meaning': 'NCIT:C17998'},
}

class RecruitmentStatusEnum(RichEnum):
    """
    Clinical trial or study recruitment status per NIH/ClinicalTrials.gov
    """
    # Enum members
    NOT_YET_RECRUITING = "NOT_YET_RECRUITING"
    RECRUITING = "RECRUITING"
    ENROLLING_BY_INVITATION = "ENROLLING_BY_INVITATION"
    ACTIVE_NOT_RECRUITING = "ACTIVE_NOT_RECRUITING"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    COMPLETED = "COMPLETED"
    WITHDRAWN = "WITHDRAWN"

# Set metadata after class creation to avoid it becoming an enum member
RecruitmentStatusEnum._metadata = {
    "NOT_YET_RECRUITING": {'description': 'Study has not started recruiting participants', 'meaning': 'NCIT:C211610'},
    "RECRUITING": {'description': 'Currently recruiting participants', 'meaning': 'NCIT:C142621'},
    "ENROLLING_BY_INVITATION": {'description': 'Enrolling participants by invitation only', 'meaning': 'NCIT:C211611'},
    "ACTIVE_NOT_RECRUITING": {'description': 'Study ongoing but not recruiting new participants', 'meaning': 'NCIT:C211612'},
    "SUSPENDED": {'description': 'Study temporarily stopped', 'meaning': 'NCIT:C211613'},
    "TERMINATED": {'description': 'Study stopped early and will not resume', 'meaning': 'NCIT:C70757'},
    "COMPLETED": {'description': 'Study has ended normally', 'meaning': 'NCIT:C70756'},
    "WITHDRAWN": {'description': 'Study withdrawn before enrollment', 'meaning': 'NCIT:C70758'},
}

class StudyPhaseEnum(RichEnum):
    """
    Clinical trial phases per FDA and NIH definitions
    """
    # Enum members
    EARLY_PHASE_1 = "EARLY_PHASE_1"
    PHASE_1 = "PHASE_1"
    PHASE_1_2 = "PHASE_1_2"
    PHASE_2 = "PHASE_2"
    PHASE_2_3 = "PHASE_2_3"
    PHASE_3 = "PHASE_3"
    PHASE_4 = "PHASE_4"
    NOT_APPLICABLE = "NOT_APPLICABLE"

# Set metadata after class creation to avoid it becoming an enum member
StudyPhaseEnum._metadata = {
    "EARLY_PHASE_1": {'description': 'Exploratory trials before traditional Phase 1', 'meaning': 'NCIT:C54721', 'annotations': {'aliases': 'Phase 0'}},
    "PHASE_1": {'description': 'Initial safety and dosage studies', 'meaning': 'NCIT:C15600', 'annotations': {'participants': '20-100'}},
    "PHASE_1_2": {'description': 'Combined Phase 1 and Phase 2 trial', 'meaning': 'NCIT:C15694'},
    "PHASE_2": {'description': 'Efficacy and side effects studies', 'meaning': 'NCIT:C15601', 'annotations': {'participants': '100-300'}},
    "PHASE_2_3": {'description': 'Combined Phase 2 and Phase 3 trial', 'meaning': 'NCIT:C49686'},
    "PHASE_3": {'description': 'Efficacy comparison with standard treatment', 'meaning': 'NCIT:C15602', 'annotations': {'participants': '300-3000'}},
    "PHASE_4": {'description': 'Post-marketing surveillance', 'meaning': 'NCIT:C15603', 'annotations': {'note': 'After FDA approval'}},
    "NOT_APPLICABLE": {'description': 'Not a phased clinical trial', 'meaning': 'NCIT:C48660', 'annotations': {'note': 'For observational studies, device trials, etc.'}},
}

class KaryotypicSexEnum(RichEnum):
    """
    Karyotypic sex of an individual based on chromosome composition
    """
    # Enum members
    XX = "XX"
    XY = "XY"
    XO = "XO"
    XXY = "XXY"
    XXX = "XXX"
    XXXY = "XXXY"
    XXXX = "XXXX"
    XXYY = "XXYY"
    XYY = "XYY"
    OTHER_KARYOTYPE = "OTHER_KARYOTYPE"
    UNKNOWN_KARYOTYPE = "UNKNOWN_KARYOTYPE"

# Set metadata after class creation to avoid it becoming an enum member
KaryotypicSexEnum._metadata = {
    "XX": {'description': 'Female karyotype (46,XX)', 'meaning': 'NCIT:C45976', 'annotations': {'chromosome_count': 46, 'typical_phenotypic_sex': 'female'}},
    "XY": {'description': 'Male karyotype (46,XY)', 'meaning': 'NCIT:C45977', 'annotations': {'chromosome_count': 46, 'typical_phenotypic_sex': 'male'}},
    "XO": {'description': 'Turner syndrome karyotype (45,X)', 'meaning': 'NCIT:C176780', 'annotations': {'chromosome_count': 45, 'condition': 'Turner syndrome'}},
    "XXY": {'description': 'Klinefelter syndrome karyotype (47,XXY)', 'meaning': 'NCIT:C176784', 'annotations': {'chromosome_count': 47, 'condition': 'Klinefelter syndrome'}},
    "XXX": {'description': 'Triple X syndrome karyotype (47,XXX)', 'meaning': 'NCIT:C176785', 'annotations': {'chromosome_count': 47, 'condition': 'Triple X syndrome'}},
    "XXXY": {'description': 'XXXY syndrome karyotype (48,XXXY)', 'meaning': 'NCIT:C176786', 'annotations': {'chromosome_count': 48, 'condition': 'XXXY syndrome'}},
    "XXXX": {'description': 'Tetrasomy X karyotype (48,XXXX)', 'meaning': 'NCIT:C176787', 'annotations': {'chromosome_count': 48, 'condition': 'Tetrasomy X'}},
    "XXYY": {'description': 'XXYY syndrome karyotype (48,XXYY)', 'meaning': 'NCIT:C89801', 'annotations': {'chromosome_count': 48, 'condition': 'XXYY syndrome'}},
    "XYY": {'description': "Jacob's syndrome karyotype (47,XYY)", 'meaning': 'NCIT:C176782', 'annotations': {'chromosome_count': 47, 'condition': "Jacob's syndrome"}},
    "OTHER_KARYOTYPE": {'description': 'Other karyotypic sex not listed', 'annotations': {'note': 'May include complex chromosomal arrangements'}},
    "UNKNOWN_KARYOTYPE": {'description': 'Karyotype not determined or unknown', 'meaning': 'NCIT:C17998'},
}

class PhenotypicSexEnum(RichEnum):
    """
    Phenotypic sex of an individual based on observable characteristics.
FHIR mapping: AdministrativeGender
    """
    # Enum members
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER_SEX = "OTHER_SEX"
    UNKNOWN_SEX = "UNKNOWN_SEX"

# Set metadata after class creation to avoid it becoming an enum member
PhenotypicSexEnum._metadata = {
    "MALE": {'description': 'Male phenotypic sex', 'meaning': 'PATO:0000384'},
    "FEMALE": {'description': 'Female phenotypic sex', 'meaning': 'PATO:0000383'},
    "OTHER_SEX": {'description': 'Sex characteristics not clearly male or female', 'meaning': 'NCIT:C45908', 'annotations': {'note': 'Includes differences of sex development (DSD)'}},
    "UNKNOWN_SEX": {'description': 'Sex not assessed or not available', 'meaning': 'NCIT:C17998'},
}

class AllelicStateEnum(RichEnum):
    """
    Allelic state/zygosity of a variant or genetic feature
    """
    # Enum members
    HETEROZYGOUS = "HETEROZYGOUS"
    HOMOZYGOUS = "HOMOZYGOUS"
    HEMIZYGOUS = "HEMIZYGOUS"
    COMPOUND_HETEROZYGOUS = "COMPOUND_HETEROZYGOUS"
    HOMOZYGOUS_REFERENCE = "HOMOZYGOUS_REFERENCE"
    HOMOZYGOUS_ALTERNATE = "HOMOZYGOUS_ALTERNATE"

# Set metadata after class creation to avoid it becoming an enum member
AllelicStateEnum._metadata = {
    "HETEROZYGOUS": {'description': 'Different alleles at a locus', 'meaning': 'GENO:0000135', 'annotations': {'symbol': 'het'}},
    "HOMOZYGOUS": {'description': 'Identical alleles at a locus', 'meaning': 'GENO:0000136', 'annotations': {'symbol': 'hom'}},
    "HEMIZYGOUS": {'description': 'Only one allele present (e.g., X-linked in males)', 'meaning': 'GENO:0000134', 'annotations': {'symbol': 'hemi', 'note': 'Common for X-linked genes in males'}},
    "COMPOUND_HETEROZYGOUS": {'description': 'Two different heterozygous variants in same gene', 'meaning': 'GENO:0000402', 'annotations': {'symbol': 'comp het'}},
    "HOMOZYGOUS_REFERENCE": {'description': 'Two reference/wild-type alleles', 'meaning': 'GENO:0000036', 'annotations': {'symbol': 'hom ref'}},
    "HOMOZYGOUS_ALTERNATE": {'description': 'Two alternate/variant alleles', 'meaning': 'GENO:0000002', 'annotations': {'symbol': 'hom alt'}},
}

class LateralityEnum(RichEnum):
    """
    Laterality/sidedness of a finding or anatomical structure
    """
    # Enum members
    RIGHT = "RIGHT"
    LEFT = "LEFT"
    BILATERAL = "BILATERAL"
    UNILATERAL = "UNILATERAL"
    MIDLINE = "MIDLINE"

# Set metadata after class creation to avoid it becoming an enum member
LateralityEnum._metadata = {
    "RIGHT": {'description': 'Right side', 'meaning': 'HP:0012834', 'annotations': {'anatomical_term': 'dexter'}},
    "LEFT": {'description': 'Left side', 'meaning': 'HP:0012835', 'annotations': {'anatomical_term': 'sinister'}},
    "BILATERAL": {'description': 'Both sides', 'meaning': 'HP:0012832', 'annotations': {'note': 'Affecting both left and right'}},
    "UNILATERAL": {'description': 'One side (unspecified which)', 'meaning': 'HP:0012833', 'annotations': {'note': 'Affecting only one side'}},
    "MIDLINE": {'description': 'In the midline/center', 'annotations': {'note': "Along the body's central axis"}},
}

class OnsetTimingEnum(RichEnum):
    """
    Timing of disease or phenotype onset relative to developmental stages
    """
    # Enum members
    ANTENATAL_ONSET = "ANTENATAL_ONSET"
    EMBRYONAL_ONSET = "EMBRYONAL_ONSET"
    FETAL_ONSET = "FETAL_ONSET"
    CONGENITAL_ONSET = "CONGENITAL_ONSET"
    NEONATAL_ONSET = "NEONATAL_ONSET"
    INFANTILE_ONSET = "INFANTILE_ONSET"
    CHILDHOOD_ONSET = "CHILDHOOD_ONSET"
    JUVENILE_ONSET = "JUVENILE_ONSET"
    YOUNG_ADULT_ONSET = "YOUNG_ADULT_ONSET"
    MIDDLE_AGE_ONSET = "MIDDLE_AGE_ONSET"
    LATE_ONSET = "LATE_ONSET"

# Set metadata after class creation to avoid it becoming an enum member
OnsetTimingEnum._metadata = {
    "ANTENATAL_ONSET": {'description': 'Before birth (prenatal)', 'meaning': 'HP:0030674', 'annotations': {'period': 'Before birth'}},
    "EMBRYONAL_ONSET": {'description': 'During embryonic period (0-8 weeks)', 'meaning': 'HP:0011460', 'annotations': {'period': '0-8 weeks gestation'}},
    "FETAL_ONSET": {'description': 'During fetal period (8 weeks to birth)', 'meaning': 'HP:0011461', 'annotations': {'period': '8 weeks to birth'}},
    "CONGENITAL_ONSET": {'description': 'Present at birth', 'meaning': 'HP:0003577', 'annotations': {'period': 'At birth'}},
    "NEONATAL_ONSET": {'description': 'Within first 28 days of life', 'meaning': 'HP:0003623', 'annotations': {'period': '0-28 days'}},
    "INFANTILE_ONSET": {'description': 'Between 28 days and 1 year', 'meaning': 'HP:0003593', 'annotations': {'period': '28 days to 1 year'}},
    "CHILDHOOD_ONSET": {'description': 'Between 1 year and 16 years', 'meaning': 'HP:0011463', 'annotations': {'period': '1-16 years'}},
    "JUVENILE_ONSET": {'description': 'Between 5 years and 16 years', 'meaning': 'HP:0003621', 'annotations': {'period': '5-16 years'}},
    "YOUNG_ADULT_ONSET": {'description': 'Between 16 years and 40 years', 'meaning': 'HP:0011462', 'annotations': {'period': '16-40 years'}},
    "MIDDLE_AGE_ONSET": {'description': 'Between 40 years and 60 years', 'meaning': 'HP:0003596', 'annotations': {'period': '40-60 years'}},
    "LATE_ONSET": {'description': 'After 60 years', 'meaning': 'HP:0003584', 'annotations': {'period': '>60 years'}},
}

class ACMGPathogenicityEnum(RichEnum):
    """
    ACMG/AMP variant pathogenicity classification for clinical genetics
    """
    # Enum members
    PATHOGENIC = "PATHOGENIC"
    LIKELY_PATHOGENIC = "LIKELY_PATHOGENIC"
    UNCERTAIN_SIGNIFICANCE = "UNCERTAIN_SIGNIFICANCE"
    LIKELY_BENIGN = "LIKELY_BENIGN"
    BENIGN = "BENIGN"

# Set metadata after class creation to avoid it becoming an enum member
ACMGPathogenicityEnum._metadata = {
    "PATHOGENIC": {'description': 'Pathogenic variant', 'meaning': 'NCIT:C168799', 'annotations': {'abbreviation': 'P', 'clinical_significance': 'Disease-causing'}},
    "LIKELY_PATHOGENIC": {'description': 'Likely pathogenic variant', 'meaning': 'NCIT:C168800', 'annotations': {'abbreviation': 'LP', 'probability': '>90% certain'}},
    "UNCERTAIN_SIGNIFICANCE": {'description': 'Variant of uncertain significance', 'meaning': 'NCIT:C94187', 'annotations': {'abbreviation': 'VUS', 'note': 'Insufficient evidence'}},
    "LIKELY_BENIGN": {'description': 'Likely benign variant', 'meaning': 'NCIT:C168801', 'annotations': {'abbreviation': 'LB', 'probability': '>90% certain benign'}},
    "BENIGN": {'description': 'Benign variant', 'meaning': 'NCIT:C168802', 'annotations': {'abbreviation': 'B', 'clinical_significance': 'Not disease-causing'}},
}

class TherapeuticActionabilityEnum(RichEnum):
    """
    Clinical actionability of a genetic finding for treatment decisions
    """
    # Enum members
    ACTIONABLE = "ACTIONABLE"
    NOT_ACTIONABLE = "NOT_ACTIONABLE"
    UNKNOWN_ACTIONABILITY = "UNKNOWN_ACTIONABILITY"

# Set metadata after class creation to avoid it becoming an enum member
TherapeuticActionabilityEnum._metadata = {
    "ACTIONABLE": {'description': 'Finding has direct therapeutic implications', 'meaning': 'NCIT:C206303', 'annotations': {'note': 'Can guide treatment selection'}},
    "NOT_ACTIONABLE": {'description': 'No current therapeutic implications', 'meaning': 'NCIT:C206304', 'annotations': {'note': 'No treatment changes indicated'}},
    "UNKNOWN_ACTIONABILITY": {'description': 'Therapeutic implications unclear', 'meaning': 'NCIT:C17998'},
}

class InterpretationProgressEnum(RichEnum):
    """
    Progress status of clinical interpretation or diagnosis
    """
    # Enum members
    SOLVED = "SOLVED"
    UNSOLVED = "UNSOLVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    UNKNOWN_PROGRESS = "UNKNOWN_PROGRESS"

# Set metadata after class creation to avoid it becoming an enum member
InterpretationProgressEnum._metadata = {
    "SOLVED": {'description': 'Diagnosis achieved/case solved', 'meaning': 'NCIT:C20826', 'annotations': {'note': 'Molecular cause identified'}},
    "UNSOLVED": {'description': 'No diagnosis achieved', 'meaning': 'NCIT:C125009', 'annotations': {'note': 'Molecular cause not identified'}},
    "IN_PROGRESS": {'description': 'Analysis ongoing', 'meaning': 'NCIT:C25630'},
    "COMPLETED": {'description': 'Analysis completed', 'meaning': 'NCIT:C216251', 'annotations': {'note': 'May be solved or unsolved'}},
    "UNKNOWN_PROGRESS": {'description': 'Progress status unknown', 'meaning': 'NCIT:C17998'},
}

class RegimenStatusEnum(RichEnum):
    """
    Status of a therapeutic regimen or treatment protocol
    """
    # Enum members
    NOT_STARTED = "NOT_STARTED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    DISCONTINUED_ADVERSE_EVENT = "DISCONTINUED_ADVERSE_EVENT"
    DISCONTINUED_LACK_OF_EFFICACY = "DISCONTINUED_LACK_OF_EFFICACY"
    DISCONTINUED_PHYSICIAN_DECISION = "DISCONTINUED_PHYSICIAN_DECISION"
    DISCONTINUED_PATIENT_DECISION = "DISCONTINUED_PATIENT_DECISION"
    UNKNOWN_STATUS = "UNKNOWN_STATUS"

# Set metadata after class creation to avoid it becoming an enum member
RegimenStatusEnum._metadata = {
    "NOT_STARTED": {'description': 'Treatment not yet begun', 'meaning': 'NCIT:C53601'},
    "STARTED": {'description': 'Treatment initiated', 'meaning': 'NCIT:C165209'},
    "COMPLETED": {'description': 'Treatment finished as planned', 'meaning': 'NCIT:C105740'},
    "DISCONTINUED_ADVERSE_EVENT": {'description': 'Stopped due to adverse event', 'meaning': 'NCIT:C41331', 'annotations': {'reason': 'Toxicity or side effects'}},
    "DISCONTINUED_LACK_OF_EFFICACY": {'description': 'Stopped due to lack of efficacy', 'meaning': 'NCIT:C49502', 'annotations': {'reason': 'Treatment not effective'}},
    "DISCONTINUED_PHYSICIAN_DECISION": {'description': 'Stopped by physician decision', 'meaning': 'NCIT:C49502'},
    "DISCONTINUED_PATIENT_DECISION": {'description': 'Stopped by patient choice', 'meaning': 'NCIT:C48271'},
    "UNKNOWN_STATUS": {'description': 'Treatment status unknown', 'meaning': 'NCIT:C17998'},
}

class DrugResponseEnum(RichEnum):
    """
    Response categories for drug treatment outcomes
    """
    # Enum members
    FAVORABLE = "FAVORABLE"
    UNFAVORABLE = "UNFAVORABLE"
    RESPONSIVE = "RESPONSIVE"
    RESISTANT = "RESISTANT"
    PARTIALLY_RESPONSIVE = "PARTIALLY_RESPONSIVE"
    UNKNOWN_RESPONSE = "UNKNOWN_RESPONSE"

# Set metadata after class creation to avoid it becoming an enum member
DrugResponseEnum._metadata = {
    "FAVORABLE": {'description': 'Favorable response to treatment', 'meaning': 'NCIT:C123584', 'annotations': {'note': 'Better than expected response'}},
    "UNFAVORABLE": {'description': 'Unfavorable response to treatment', 'meaning': 'NCIT:C102561', 'annotations': {'note': 'Worse than expected response'}},
    "RESPONSIVE": {'description': 'Responsive to treatment', 'meaning': 'NCIT:C165206', 'annotations': {'note': 'Shows expected response'}},
    "RESISTANT": {'description': 'Resistant to treatment', 'meaning': 'NCIT:C16523', 'annotations': {'note': 'No response to treatment'}},
    "PARTIALLY_RESPONSIVE": {'description': 'Partial response to treatment', 'meaning': 'NCIT:C18213', 'annotations': {'note': 'Some but not complete response'}},
    "UNKNOWN_RESPONSE": {'description': 'Treatment response unknown', 'meaning': 'NCIT:C17998'},
}

class ProcessScaleEnum(RichEnum):
    """
    Scale of bioprocessing operations from lab bench to commercial production
    """
    # Enum members
    BENCH_SCALE = "BENCH_SCALE"
    PILOT_SCALE = "PILOT_SCALE"
    DEMONSTRATION_SCALE = "DEMONSTRATION_SCALE"
    PRODUCTION_SCALE = "PRODUCTION_SCALE"
    MICROFLUIDIC_SCALE = "MICROFLUIDIC_SCALE"

# Set metadata after class creation to avoid it becoming an enum member
ProcessScaleEnum._metadata = {
    "BENCH_SCALE": {'description': 'Laboratory bench scale (typically < 10 L)', 'annotations': {'volume_range': '0.1-10 L', 'typical_volume': '1-5 L', 'purpose': 'Initial development and screening'}},
    "PILOT_SCALE": {'description': 'Pilot plant scale (10-1000 L)', 'annotations': {'volume_range': '10-1000 L', 'typical_volume': '50-500 L', 'purpose': 'Process development and optimization'}},
    "DEMONSTRATION_SCALE": {'description': 'Demonstration scale (1000-10000 L)', 'annotations': {'volume_range': '1000-10000 L', 'typical_volume': '2000-5000 L', 'purpose': 'Technology demonstration and validation'}},
    "PRODUCTION_SCALE": {'description': 'Commercial production scale (>10000 L)', 'annotations': {'volume_range': '>10000 L', 'typical_volume': '20000-200000 L', 'purpose': 'Commercial manufacturing'}},
    "MICROFLUIDIC_SCALE": {'description': 'Microfluidic scale (<1 mL)', 'annotations': {'volume_range': '<1 mL', 'typical_volume': '1-1000 μL', 'purpose': 'High-throughput screening'}},
}

class BioreactorTypeEnum(RichEnum):
    """
    Types of bioreactors used in fermentation and cell culture
    """
    # Enum members
    STIRRED_TANK = "STIRRED_TANK"
    AIRLIFT = "AIRLIFT"
    BUBBLE_COLUMN = "BUBBLE_COLUMN"
    PACKED_BED = "PACKED_BED"
    FLUIDIZED_BED = "FLUIDIZED_BED"
    MEMBRANE = "MEMBRANE"
    WAVE_BAG = "WAVE_BAG"
    HOLLOW_FIBER = "HOLLOW_FIBER"
    PHOTOBIOREACTOR = "PHOTOBIOREACTOR"

# Set metadata after class creation to avoid it becoming an enum member
BioreactorTypeEnum._metadata = {
    "STIRRED_TANK": {'description': 'Stirred tank reactor (STR/CSTR)', 'annotations': {'mixing': 'Mechanical agitation', 'common_volumes': '1-200000 L'}},
    "AIRLIFT": {'description': 'Airlift bioreactor', 'annotations': {'mixing': 'Gas sparging', 'advantages': 'Low shear, no mechanical parts'}},
    "BUBBLE_COLUMN": {'description': 'Bubble column bioreactor', 'annotations': {'mixing': 'Gas bubbling', 'advantages': 'Simple design, good mass transfer'}},
    "PACKED_BED": {'description': 'Packed bed bioreactor', 'annotations': {'configuration': 'Fixed bed of immobilized cells/enzymes', 'flow': 'Continuous'}},
    "FLUIDIZED_BED": {'description': 'Fluidized bed bioreactor', 'annotations': {'configuration': 'Suspended solid particles', 'mixing': 'Fluid flow'}},
    "MEMBRANE": {'description': 'Membrane bioreactor', 'meaning': 'ENVO:03600010', 'annotations': {'feature': 'Integrated membrane separation', 'application': 'Cell retention, product separation'}},
    "WAVE_BAG": {'description': 'Wave/rocking bioreactor', 'annotations': {'mixing': 'Rocking motion', 'advantages': 'Single-use, low shear'}},
    "HOLLOW_FIBER": {'description': 'Hollow fiber bioreactor', 'annotations': {'configuration': 'Hollow fiber membranes', 'application': 'High-density cell culture'}},
    "PHOTOBIOREACTOR": {'description': 'Photobioreactor for photosynthetic organisms', 'annotations': {'light_source': 'Required', 'organisms': 'Algae, cyanobacteria'}},
}

class FermentationModeEnum(RichEnum):
    """
    Modes of fermentation operation
    """
    # Enum members
    BATCH = "BATCH"
    FED_BATCH = "FED_BATCH"
    CONTINUOUS = "CONTINUOUS"
    PERFUSION = "PERFUSION"
    REPEATED_BATCH = "REPEATED_BATCH"
    SEMI_CONTINUOUS = "SEMI_CONTINUOUS"

# Set metadata after class creation to avoid it becoming an enum member
FermentationModeEnum._metadata = {
    "BATCH": {'description': 'Batch fermentation', 'meaning': 'MSIO:0000181', 'annotations': {'operation': 'All nutrients added at start', 'duration': 'Fixed time period'}},
    "FED_BATCH": {'description': 'Fed-batch fermentation', 'annotations': {'operation': 'Nutrients added during run', 'advantage': 'Control of growth rate'}},
    "CONTINUOUS": {'description': 'Continuous fermentation (chemostat)', 'meaning': 'MSIO:0000155', 'annotations': {'operation': 'Continuous feed and harvest', 'steady_state': True}},
    "PERFUSION": {'description': 'Perfusion culture', 'annotations': {'operation': 'Continuous media exchange with cell retention', 'application': 'High-density cell culture'}},
    "REPEATED_BATCH": {'description': 'Repeated batch fermentation', 'annotations': {'operation': 'Sequential batches with partial harvest', 'advantage': 'Reduced downtime'}},
    "SEMI_CONTINUOUS": {'description': 'Semi-continuous operation', 'annotations': {'operation': 'Periodic harvest and refill', 'advantage': 'Extended production'}},
}

class OxygenationStrategyEnum(RichEnum):
    """
    Oxygen supply strategies for fermentation
    """
    # Enum members
    AEROBIC = "AEROBIC"
    ANAEROBIC = "ANAEROBIC"
    MICROAEROBIC = "MICROAEROBIC"
    FACULTATIVE = "FACULTATIVE"

# Set metadata after class creation to avoid it becoming an enum member
OxygenationStrategyEnum._metadata = {
    "AEROBIC": {'description': 'Aerobic with active aeration', 'annotations': {'oxygen': 'Required', 'typical_DO': '20-80% saturation'}},
    "ANAEROBIC": {'description': 'Anaerobic (no oxygen)', 'annotations': {'oxygen': 'Excluded', 'atmosphere': 'N2 or CO2'}},
    "MICROAEROBIC": {'description': 'Microaerobic (limited oxygen)', 'annotations': {'oxygen': 'Limited', 'typical_DO': '<5% saturation'}},
    "FACULTATIVE": {'description': 'Facultative (with/without oxygen)', 'annotations': {'oxygen': 'Optional', 'flexibility': 'Organism-dependent'}},
}

class AgitationTypeEnum(RichEnum):
    """
    Types of agitation/mixing in bioreactors
    """
    # Enum members
    RUSHTON_TURBINE = "RUSHTON_TURBINE"
    PITCHED_BLADE = "PITCHED_BLADE"
    MARINE_PROPELLER = "MARINE_PROPELLER"
    ANCHOR = "ANCHOR"
    HELICAL_RIBBON = "HELICAL_RIBBON"
    MAGNETIC_BAR = "MAGNETIC_BAR"
    ORBITAL_SHAKING = "ORBITAL_SHAKING"
    NO_AGITATION = "NO_AGITATION"

# Set metadata after class creation to avoid it becoming an enum member
AgitationTypeEnum._metadata = {
    "RUSHTON_TURBINE": {'description': 'Rushton turbine impeller', 'annotations': {'type': 'Radial flow', 'power_number': '5-6'}},
    "PITCHED_BLADE": {'description': 'Pitched blade turbine', 'annotations': {'type': 'Axial flow', 'angle': '45 degrees'}},
    "MARINE_PROPELLER": {'description': 'Marine propeller', 'annotations': {'type': 'Axial flow', 'low_shear': True}},
    "ANCHOR": {'description': 'Anchor impeller', 'annotations': {'type': 'Close clearance', 'viscous_fluids': True}},
    "HELICAL_RIBBON": {'description': 'Helical ribbon impeller', 'annotations': {'type': 'Close clearance', 'high_viscosity': True}},
    "MAGNETIC_BAR": {'description': 'Magnetic stir bar', 'annotations': {'scale': 'Laboratory', 'volume': '<5 L'}},
    "ORBITAL_SHAKING": {'description': 'Orbital shaking', 'annotations': {'type': 'Platform shaker', 'application': 'Shake flasks'}},
    "NO_AGITATION": {'description': 'No mechanical agitation', 'annotations': {'mixing': 'Gas sparging or static'}},
}

class DownstreamProcessEnum(RichEnum):
    """
    Downstream processing unit operations
    """
    # Enum members
    CENTRIFUGATION = "CENTRIFUGATION"
    FILTRATION = "FILTRATION"
    CHROMATOGRAPHY = "CHROMATOGRAPHY"
    EXTRACTION = "EXTRACTION"
    PRECIPITATION = "PRECIPITATION"
    EVAPORATION = "EVAPORATION"
    DISTILLATION = "DISTILLATION"
    DRYING = "DRYING"
    HOMOGENIZATION = "HOMOGENIZATION"

# Set metadata after class creation to avoid it becoming an enum member
DownstreamProcessEnum._metadata = {
    "CENTRIFUGATION": {'description': 'Centrifugal separation', 'meaning': 'CHMO:0002010', 'annotations': {'principle': 'Density difference', 'types': 'Disk stack, tubular, decanter'}},
    "FILTRATION": {'description': 'Filtration (micro/ultra/nano)', 'meaning': 'CHMO:0001640', 'annotations': {'types': 'Dead-end, crossflow, depth'}},
    "CHROMATOGRAPHY": {'description': 'Chromatographic separation', 'meaning': 'CHMO:0001000', 'annotations': {'types': 'Ion exchange, affinity, size exclusion'}},
    "EXTRACTION": {'description': 'Liquid-liquid extraction', 'meaning': 'CHMO:0001577', 'annotations': {'principle': 'Partitioning between phases'}},
    "PRECIPITATION": {'description': 'Precipitation/crystallization', 'meaning': 'CHMO:0001688', 'annotations': {'agents': 'Salts, solvents, pH'}},
    "EVAPORATION": {'description': 'Evaporation/concentration', 'meaning': 'CHMO:0001574', 'annotations': {'types': 'Falling film, MVR, TVR'}},
    "DISTILLATION": {'description': 'Distillation', 'meaning': 'CHMO:0001534', 'annotations': {'principle': 'Boiling point difference'}},
    "DRYING": {'description': 'Drying operations', 'meaning': 'CHMO:0001551', 'annotations': {'types': 'Spray, freeze, vacuum'}},
    "HOMOGENIZATION": {'description': 'Cell disruption/homogenization', 'annotations': {'methods': 'High pressure, bead mill'}},
}

class FeedstockTypeEnum(RichEnum):
    """
    Types of feedstocks for bioprocessing
    """
    # Enum members
    GLUCOSE = "GLUCOSE"
    SUCROSE = "SUCROSE"
    GLYCEROL = "GLYCEROL"
    MOLASSES = "MOLASSES"
    CORN_STEEP_LIQUOR = "CORN_STEEP_LIQUOR"
    YEAST_EXTRACT = "YEAST_EXTRACT"
    LIGNOCELLULOSIC = "LIGNOCELLULOSIC"
    METHANOL = "METHANOL"
    WASTE_STREAM = "WASTE_STREAM"

# Set metadata after class creation to avoid it becoming an enum member
FeedstockTypeEnum._metadata = {
    "GLUCOSE": {'description': 'Glucose/dextrose', 'meaning': 'CHEBI:17234', 'annotations': {'source': 'Corn, sugarcane', 'carbon_source': True}},
    "SUCROSE": {'description': 'Sucrose', 'meaning': 'CHEBI:17992', 'annotations': {'source': 'Sugarcane, sugar beet', 'carbon_source': True}},
    "GLYCEROL": {'description': 'Glycerol', 'meaning': 'CHEBI:17754', 'annotations': {'source': 'Biodiesel byproduct', 'carbon_source': True}},
    "MOLASSES": {'description': 'Molasses', 'meaning': 'CHEBI:83163', 'annotations': {'source': 'Sugar processing byproduct', 'complex_medium': True}},
    "CORN_STEEP_LIQUOR": {'description': 'Corn steep liquor', 'annotations': {'source': 'Corn wet milling', 'nitrogen_source': True}},
    "YEAST_EXTRACT": {'description': 'Yeast extract', 'meaning': 'FOODON:03315426', 'annotations': {'source': 'Autolyzed yeast', 'complex_nutrient': True}},
    "LIGNOCELLULOSIC": {'description': 'Lignocellulosic biomass', 'annotations': {'source': 'Agricultural residues, wood', 'pretreatment': 'Required'}},
    "METHANOL": {'description': 'Methanol', 'meaning': 'CHEBI:17790', 'annotations': {'carbon_source': True, 'methylotrophic': True}},
    "WASTE_STREAM": {'description': 'Industrial waste stream', 'annotations': {'variable_composition': True, 'sustainability': 'Circular economy'}},
}

class ProductTypeEnum(RichEnum):
    """
    Types of products from bioprocessing
    """
    # Enum members
    BIOFUEL = "BIOFUEL"
    PROTEIN = "PROTEIN"
    ENZYME = "ENZYME"
    ORGANIC_ACID = "ORGANIC_ACID"
    AMINO_ACID = "AMINO_ACID"
    ANTIBIOTIC = "ANTIBIOTIC"
    VITAMIN = "VITAMIN"
    BIOPOLYMER = "BIOPOLYMER"
    BIOMASS = "BIOMASS"
    SECONDARY_METABOLITE = "SECONDARY_METABOLITE"

# Set metadata after class creation to avoid it becoming an enum member
ProductTypeEnum._metadata = {
    "BIOFUEL": {'description': 'Biofuel (ethanol, biodiesel, etc.)', 'meaning': 'CHEBI:33292', 'annotations': {'category': 'Energy'}},
    "PROTEIN": {'description': 'Recombinant protein', 'meaning': 'NCIT:C17021', 'annotations': {'category': 'Biopharmaceutical'}},
    "ENZYME": {'description': 'Industrial enzyme', 'meaning': 'NCIT:C16554', 'annotations': {'category': 'Biocatalyst'}},
    "ORGANIC_ACID": {'description': 'Organic acid (citric, lactic, etc.)', 'meaning': 'CHEBI:64709', 'annotations': {'category': 'Chemical'}},
    "AMINO_ACID": {'description': 'Amino acid', 'meaning': 'CHEBI:33709', 'annotations': {'category': 'Nutritional'}},
    "ANTIBIOTIC": {'description': 'Antibiotic', 'meaning': 'CHEBI:33281', 'annotations': {'category': 'Pharmaceutical'}},
    "VITAMIN": {'description': 'Vitamin', 'meaning': 'CHEBI:33229', 'annotations': {'category': 'Nutritional'}},
    "BIOPOLYMER": {'description': 'Biopolymer (PHA, PLA, etc.)', 'meaning': 'CHEBI:33694', 'annotations': {'category': 'Material'}},
    "BIOMASS": {'description': 'Microbial biomass', 'meaning': 'ENVO:01000155', 'annotations': {'category': 'Feed/food'}},
    "SECONDARY_METABOLITE": {'description': 'Secondary metabolite', 'meaning': 'CHEBI:25212', 'annotations': {'category': 'Specialty chemical'}},
}

class SterilizationMethodEnum(RichEnum):
    """
    Methods for sterilization in bioprocessing
    """
    # Enum members
    STEAM_IN_PLACE = "STEAM_IN_PLACE"
    AUTOCLAVE = "AUTOCLAVE"
    FILTER_STERILIZATION = "FILTER_STERILIZATION"
    GAMMA_IRRADIATION = "GAMMA_IRRADIATION"
    ETHYLENE_OXIDE = "ETHYLENE_OXIDE"
    UV_STERILIZATION = "UV_STERILIZATION"
    CHEMICAL_STERILIZATION = "CHEMICAL_STERILIZATION"

# Set metadata after class creation to avoid it becoming an enum member
SterilizationMethodEnum._metadata = {
    "STEAM_IN_PLACE": {'description': 'Steam in place (SIP)', 'annotations': {'temperature': '121-134°C', 'time': '15-30 min'}},
    "AUTOCLAVE": {'description': 'Autoclave sterilization', 'meaning': 'CHMO:0002846', 'annotations': {'temperature': '121°C', 'pressure': '15 psi'}},
    "FILTER_STERILIZATION": {'description': 'Filter sterilization (0.2 μm)', 'annotations': {'pore_size': '0.2 μm', 'heat_labile': True}},
    "GAMMA_IRRADIATION": {'description': 'Gamma irradiation', 'annotations': {'dose': '25-40 kGy', 'single_use': True}},
    "ETHYLENE_OXIDE": {'description': 'Ethylene oxide sterilization', 'annotations': {'temperature': '30-60°C', 'plastic_compatible': True}},
    "UV_STERILIZATION": {'description': 'UV sterilization', 'annotations': {'wavelength': '254 nm', 'surface_only': True}},
    "CHEMICAL_STERILIZATION": {'description': 'Chemical sterilization', 'annotations': {'agents': 'Bleach, alcohol, peroxide', 'contact_time': 'Variable'}},
}

class LengthUnitEnum(RichEnum):
    """
    Units of length/distance measurement
    """
    # Enum members
    METER = "METER"
    KILOMETER = "KILOMETER"
    CENTIMETER = "CENTIMETER"
    MILLIMETER = "MILLIMETER"
    MICROMETER = "MICROMETER"
    NANOMETER = "NANOMETER"
    ANGSTROM = "ANGSTROM"
    INCH = "INCH"
    FOOT = "FOOT"
    YARD = "YARD"
    MILE = "MILE"
    NAUTICAL_MILE = "NAUTICAL_MILE"

# Set metadata after class creation to avoid it becoming an enum member
LengthUnitEnum._metadata = {
    "METER": {'description': 'Meter (SI base unit)', 'meaning': 'UO:0000008', 'annotations': {'symbol': 'm', 'system': 'SI'}},
    "KILOMETER": {'description': 'Kilometer (1000 meters)', 'meaning': 'UO:0010066', 'annotations': {'symbol': 'km', 'conversion_to_meter': '1000'}},
    "CENTIMETER": {'description': 'Centimeter (0.01 meter)', 'meaning': 'UO:0000015', 'annotations': {'symbol': 'cm', 'conversion_to_meter': '0.01'}},
    "MILLIMETER": {'description': 'Millimeter (0.001 meter)', 'meaning': 'UO:0000016', 'annotations': {'symbol': 'mm', 'conversion_to_meter': '0.001'}},
    "MICROMETER": {'description': 'Micrometer/micron (10^-6 meter)', 'meaning': 'UO:0000017', 'annotations': {'symbol': 'μm', 'conversion_to_meter': '1e-6'}},
    "NANOMETER": {'description': 'Nanometer (10^-9 meter)', 'meaning': 'UO:0000018', 'annotations': {'symbol': 'nm', 'conversion_to_meter': '1e-9'}},
    "ANGSTROM": {'description': 'Angstrom (10^-10 meter)', 'meaning': 'UO:0000019', 'annotations': {'symbol': 'Å', 'conversion_to_meter': '1e-10'}},
    "INCH": {'description': 'Inch (imperial)', 'meaning': 'UO:0010011', 'annotations': {'symbol': 'in', 'conversion_to_meter': '0.0254', 'system': 'imperial'}},
    "FOOT": {'description': 'Foot (imperial)', 'meaning': 'UO:0010013', 'annotations': {'symbol': 'ft', 'conversion_to_meter': '0.3048', 'system': 'imperial'}},
    "YARD": {'description': 'Yard (imperial)', 'meaning': 'UO:0010014', 'annotations': {'symbol': 'yd', 'conversion_to_meter': '0.9144', 'system': 'imperial'}},
    "MILE": {'description': 'Mile (imperial)', 'meaning': 'UO:0010017', 'annotations': {'symbol': 'mi', 'conversion_to_meter': '1609.344', 'system': 'imperial'}},
    "NAUTICAL_MILE": {'description': 'Nautical mile', 'meaning': 'UO:0010022', 'annotations': {'symbol': 'nmi', 'conversion_to_meter': '1852'}},
}

class MassUnitEnum(RichEnum):
    """
    Units of mass measurement
    """
    # Enum members
    KILOGRAM = "KILOGRAM"
    GRAM = "GRAM"
    MILLIGRAM = "MILLIGRAM"
    MICROGRAM = "MICROGRAM"
    NANOGRAM = "NANOGRAM"
    METRIC_TON = "METRIC_TON"
    POUND = "POUND"
    OUNCE = "OUNCE"
    STONE = "STONE"
    DALTON = "DALTON"

# Set metadata after class creation to avoid it becoming an enum member
MassUnitEnum._metadata = {
    "KILOGRAM": {'description': 'Kilogram (SI base unit)', 'meaning': 'UO:0000009', 'annotations': {'symbol': 'kg', 'system': 'SI'}},
    "GRAM": {'description': 'Gram (0.001 kilogram)', 'meaning': 'UO:0000021', 'annotations': {'symbol': 'g', 'conversion_to_kg': '0.001'}},
    "MILLIGRAM": {'description': 'Milligram (10^-6 kilogram)', 'meaning': 'UO:0000022', 'annotations': {'symbol': 'mg', 'conversion_to_kg': '1e-6'}},
    "MICROGRAM": {'description': 'Microgram (10^-9 kilogram)', 'meaning': 'UO:0000023', 'annotations': {'symbol': 'μg', 'conversion_to_kg': '1e-9'}},
    "NANOGRAM": {'description': 'Nanogram (10^-12 kilogram)', 'meaning': 'UO:0000024', 'annotations': {'symbol': 'ng', 'conversion_to_kg': '1e-12'}},
    "METRIC_TON": {'description': 'Metric ton/tonne (1000 kilograms)', 'meaning': 'UO:0010038', 'annotations': {'symbol': 't', 'conversion_to_kg': '1000'}, 'aliases': ['ton']},
    "POUND": {'description': 'Pound (imperial)', 'meaning': 'UO:0010034', 'annotations': {'symbol': 'lb', 'conversion_to_kg': '0.453592', 'system': 'imperial'}},
    "OUNCE": {'description': 'Ounce (imperial)', 'meaning': 'UO:0010033', 'annotations': {'symbol': 'oz', 'conversion_to_kg': '0.0283495', 'system': 'imperial'}},
    "STONE": {'description': 'Stone (imperial)', 'meaning': 'UO:0010035', 'annotations': {'symbol': 'st', 'conversion_to_kg': '6.35029', 'system': 'imperial'}},
    "DALTON": {'description': 'Dalton/atomic mass unit', 'meaning': 'UO:0000221', 'annotations': {'symbol': 'Da', 'conversion_to_kg': '1.66054e-27', 'use': 'molecular mass'}},
}

class VolumeUnitEnum(RichEnum):
    """
    Units of volume measurement
    """
    # Enum members
    LITER = "LITER"
    MILLILITER = "MILLILITER"
    MICROLITER = "MICROLITER"
    CUBIC_METER = "CUBIC_METER"
    CUBIC_CENTIMETER = "CUBIC_CENTIMETER"
    GALLON_US = "GALLON_US"
    GALLON_UK = "GALLON_UK"
    FLUID_OUNCE_US = "FLUID_OUNCE_US"
    PINT_US = "PINT_US"
    QUART_US = "QUART_US"
    CUP_US = "CUP_US"
    TABLESPOON = "TABLESPOON"
    TEASPOON = "TEASPOON"

# Set metadata after class creation to avoid it becoming an enum member
VolumeUnitEnum._metadata = {
    "LITER": {'description': 'Liter (SI derived)', 'meaning': 'UO:0000099', 'annotations': {'symbol': 'L', 'conversion_to_m3': '0.001'}},
    "MILLILITER": {'description': 'Milliliter (0.001 liter)', 'meaning': 'UO:0000098', 'annotations': {'symbol': 'mL', 'conversion_to_m3': '1e-6'}},
    "MICROLITER": {'description': 'Microliter (10^-6 liter)', 'meaning': 'UO:0000101', 'annotations': {'symbol': 'μL', 'conversion_to_m3': '1e-9'}},
    "CUBIC_METER": {'description': 'Cubic meter (SI derived)', 'meaning': 'UO:0000096', 'annotations': {'symbol': 'm³', 'system': 'SI'}},
    "CUBIC_CENTIMETER": {'description': 'Cubic centimeter', 'meaning': 'UO:0000097', 'annotations': {'symbol': 'cm³', 'conversion_to_m3': '1e-6'}},
    "GALLON_US": {'description': 'US gallon', 'annotations': {'symbol': 'gal', 'conversion_to_m3': '0.00378541', 'system': 'US'}},
    "GALLON_UK": {'description': 'UK/Imperial gallon', 'meaning': 'UO:0010030', 'annotations': {'symbol': 'gal', 'conversion_to_m3': '0.00454609', 'system': 'imperial'}, 'aliases': ['imperial gallon']},
    "FLUID_OUNCE_US": {'description': 'US fluid ounce', 'meaning': 'UO:0010026', 'annotations': {'symbol': 'fl oz', 'conversion_to_m3': '2.95735e-5', 'system': 'US'}, 'aliases': ['imperial fluid ounce']},
    "PINT_US": {'description': 'US pint', 'meaning': 'UO:0010028', 'annotations': {'symbol': 'pt', 'conversion_to_m3': '0.000473176', 'system': 'US'}, 'aliases': ['imperial pint']},
    "QUART_US": {'description': 'US quart', 'meaning': 'UO:0010029', 'annotations': {'symbol': 'qt', 'conversion_to_m3': '0.000946353', 'system': 'US'}, 'aliases': ['imperial quart']},
    "CUP_US": {'description': 'US cup', 'meaning': 'UO:0010046', 'annotations': {'symbol': 'cup', 'conversion_to_m3': '0.000236588', 'system': 'US'}},
    "TABLESPOON": {'description': 'Tablespoon', 'meaning': 'UO:0010044', 'annotations': {'symbol': 'tbsp', 'conversion_to_m3': '1.47868e-5'}},
    "TEASPOON": {'description': 'Teaspoon', 'meaning': 'UO:0010041', 'annotations': {'symbol': 'tsp', 'conversion_to_m3': '4.92892e-6'}},
}

class TemperatureUnitEnum(RichEnum):
    """
    Units of temperature measurement
    """
    # Enum members
    KELVIN = "KELVIN"
    CELSIUS = "CELSIUS"
    FAHRENHEIT = "FAHRENHEIT"
    RANKINE = "RANKINE"

# Set metadata after class creation to avoid it becoming an enum member
TemperatureUnitEnum._metadata = {
    "KELVIN": {'description': 'Kelvin (SI base unit)', 'meaning': 'UO:0000012', 'annotations': {'symbol': 'K', 'system': 'SI', 'absolute': 'true'}},
    "CELSIUS": {'description': 'Celsius/Centigrade', 'meaning': 'UO:0000027', 'annotations': {'symbol': '°C', 'conversion': 'K - 273.15'}},
    "FAHRENHEIT": {'description': 'Fahrenheit', 'meaning': 'UO:0000195', 'annotations': {'symbol': '°F', 'conversion': '(K - 273.15) * 9/5 + 32', 'system': 'imperial'}},
    "RANKINE": {'description': 'Rankine', 'annotations': {'symbol': '°R', 'conversion': 'K * 9/5', 'absolute': 'true'}},
}

class TimeUnitEnum(RichEnum):
    """
    Units of time measurement
    """
    # Enum members
    SECOND = "SECOND"
    MILLISECOND = "MILLISECOND"
    MICROSECOND = "MICROSECOND"
    NANOSECOND = "NANOSECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"

# Set metadata after class creation to avoid it becoming an enum member
TimeUnitEnum._metadata = {
    "SECOND": {'description': 'Second (SI base unit)', 'meaning': 'UO:0000010', 'annotations': {'symbol': 's', 'system': 'SI'}},
    "MILLISECOND": {'description': 'Millisecond (0.001 second)', 'meaning': 'UO:0000028', 'annotations': {'symbol': 'ms', 'conversion_to_second': '0.001'}},
    "MICROSECOND": {'description': 'Microsecond (10^-6 second)', 'meaning': 'UO:0000029', 'annotations': {'symbol': 'μs', 'conversion_to_second': '1e-6'}},
    "NANOSECOND": {'description': 'Nanosecond (10^-9 second)', 'meaning': 'UO:0000150', 'annotations': {'symbol': 'ns', 'conversion_to_second': '1e-9'}},
    "MINUTE": {'description': 'Minute (60 seconds)', 'meaning': 'UO:0000031', 'annotations': {'symbol': 'min', 'conversion_to_second': '60'}},
    "HOUR": {'description': 'Hour (3600 seconds)', 'meaning': 'UO:0000032', 'annotations': {'symbol': 'h', 'conversion_to_second': '3600'}},
    "DAY": {'description': 'Day (86400 seconds)', 'meaning': 'UO:0000033', 'annotations': {'symbol': 'd', 'conversion_to_second': '86400'}},
    "WEEK": {'description': 'Week (7 days)', 'meaning': 'UO:0000034', 'annotations': {'symbol': 'wk', 'conversion_to_second': '604800'}},
    "MONTH": {'description': 'Month (approximately 30 days)', 'meaning': 'UO:0000035', 'annotations': {'symbol': 'mo', 'conversion_to_second': '2592000', 'note': 'approximate, varies by month'}},
    "YEAR": {'description': 'Year (365.25 days)', 'meaning': 'UO:0000036', 'annotations': {'symbol': 'yr', 'conversion_to_second': '31557600', 'note': 'accounts for leap years'}},
}

class PressureUnitEnum(RichEnum):
    """
    Units of pressure measurement
    """
    # Enum members
    PASCAL = "PASCAL"
    KILOPASCAL = "KILOPASCAL"
    MEGAPASCAL = "MEGAPASCAL"
    BAR = "BAR"
    MILLIBAR = "MILLIBAR"
    ATMOSPHERE = "ATMOSPHERE"
    TORR = "TORR"
    PSI = "PSI"
    MM_HG = "MM_HG"

# Set metadata after class creation to avoid it becoming an enum member
PressureUnitEnum._metadata = {
    "PASCAL": {'description': 'Pascal (SI derived unit)', 'meaning': 'UO:0000110', 'annotations': {'symbol': 'Pa', 'system': 'SI', 'definition': 'N/m²'}},
    "KILOPASCAL": {'description': 'Kilopascal (1000 pascals)', 'annotations': {'symbol': 'kPa', 'conversion_to_pascal': '1000'}},
    "MEGAPASCAL": {'description': 'Megapascal (10^6 pascals)', 'annotations': {'symbol': 'MPa', 'conversion_to_pascal': '1e6'}},
    "BAR": {'description': 'Bar', 'annotations': {'symbol': 'bar', 'conversion_to_pascal': '100000'}},
    "MILLIBAR": {'description': 'Millibar', 'annotations': {'symbol': 'mbar', 'conversion_to_pascal': '100'}},
    "ATMOSPHERE": {'description': 'Standard atmosphere', 'annotations': {'symbol': 'atm', 'conversion_to_pascal': '101325'}},
    "TORR": {'description': 'Torr (millimeter of mercury)', 'annotations': {'symbol': 'Torr', 'conversion_to_pascal': '133.322'}},
    "PSI": {'description': 'Pounds per square inch', 'meaning': 'UO:0010052', 'annotations': {'symbol': 'psi', 'conversion_to_pascal': '6894.76', 'system': 'imperial'}, 'aliases': ['pound-force per square inch']},
    "MM_HG": {'description': 'Millimeters of mercury', 'meaning': 'UO:0000272', 'annotations': {'symbol': 'mmHg', 'conversion_to_pascal': '133.322', 'use': 'medical blood pressure'}},
}

class ConcentrationUnitEnum(RichEnum):
    """
    Units of concentration measurement
    """
    # Enum members
    MOLAR = "MOLAR"
    MILLIMOLAR = "MILLIMOLAR"
    MICROMOLAR = "MICROMOLAR"
    NANOMOLAR = "NANOMOLAR"
    PICOMOLAR = "PICOMOLAR"
    MG_PER_ML = "MG_PER_ML"
    UG_PER_ML = "UG_PER_ML"
    NG_PER_ML = "NG_PER_ML"
    PERCENT = "PERCENT"
    PPM = "PPM"
    PPB = "PPB"

# Set metadata after class creation to avoid it becoming an enum member
ConcentrationUnitEnum._metadata = {
    "MOLAR": {'description': 'Molar (moles per liter)', 'meaning': 'UO:0000062', 'annotations': {'symbol': 'M', 'definition': 'mol/L'}},
    "MILLIMOLAR": {'description': 'Millimolar (10^-3 molar)', 'meaning': 'UO:0000063', 'annotations': {'symbol': 'mM', 'conversion_to_molar': '0.001'}},
    "MICROMOLAR": {'description': 'Micromolar (10^-6 molar)', 'meaning': 'UO:0000064', 'annotations': {'symbol': 'μM', 'conversion_to_molar': '1e-6'}},
    "NANOMOLAR": {'description': 'Nanomolar (10^-9 molar)', 'meaning': 'UO:0000065', 'annotations': {'symbol': 'nM', 'conversion_to_molar': '1e-9'}},
    "PICOMOLAR": {'description': 'Picomolar (10^-12 molar)', 'meaning': 'UO:0000066', 'annotations': {'symbol': 'pM', 'conversion_to_molar': '1e-12'}},
    "MG_PER_ML": {'description': 'Milligrams per milliliter', 'meaning': 'UO:0000176', 'annotations': {'symbol': 'mg/mL'}},
    "UG_PER_ML": {'description': 'Micrograms per milliliter', 'meaning': 'UO:0000274', 'annotations': {'symbol': 'μg/mL'}},
    "NG_PER_ML": {'description': 'Nanograms per milliliter', 'meaning': 'UO:0000275', 'annotations': {'symbol': 'ng/mL'}},
    "PERCENT": {'description': 'Percent (parts per hundred)', 'meaning': 'UO:0000187', 'annotations': {'symbol': '%', 'conversion_to_fraction': '0.01'}},
    "PPM": {'description': 'Parts per million', 'meaning': 'UO:0000169', 'annotations': {'symbol': 'ppm', 'conversion_to_fraction': '1e-6'}},
    "PPB": {'description': 'Parts per billion', 'meaning': 'UO:0000170', 'annotations': {'symbol': 'ppb', 'conversion_to_fraction': '1e-9'}},
}

class FrequencyUnitEnum(RichEnum):
    """
    Units of frequency measurement
    """
    # Enum members
    HERTZ = "HERTZ"
    KILOHERTZ = "KILOHERTZ"
    MEGAHERTZ = "MEGAHERTZ"
    GIGAHERTZ = "GIGAHERTZ"
    RPM = "RPM"
    BPM = "BPM"

# Set metadata after class creation to avoid it becoming an enum member
FrequencyUnitEnum._metadata = {
    "HERTZ": {'description': 'Hertz (cycles per second)', 'meaning': 'UO:0000106', 'annotations': {'symbol': 'Hz', 'system': 'SI'}},
    "KILOHERTZ": {'description': 'Kilohertz (1000 Hz)', 'annotations': {'symbol': 'kHz', 'conversion_to_hz': '1000'}},
    "MEGAHERTZ": {'description': 'Megahertz (10^6 Hz)', 'meaning': 'UO:0000325', 'annotations': {'symbol': 'MHz', 'conversion_to_hz': '1e6'}},
    "GIGAHERTZ": {'description': 'Gigahertz (10^9 Hz)', 'annotations': {'symbol': 'GHz', 'conversion_to_hz': '1e9'}},
    "RPM": {'description': 'Revolutions per minute', 'annotations': {'symbol': 'rpm', 'conversion_to_hz': '0.0166667'}},
    "BPM": {'description': 'Beats per minute', 'annotations': {'symbol': 'bpm', 'conversion_to_hz': '0.0166667', 'use': 'heart rate'}},
}

class AngleUnitEnum(RichEnum):
    """
    Units of angle measurement
    """
    # Enum members
    RADIAN = "RADIAN"
    DEGREE = "DEGREE"
    MINUTE_OF_ARC = "MINUTE_OF_ARC"
    SECOND_OF_ARC = "SECOND_OF_ARC"
    GRADIAN = "GRADIAN"
    TURN = "TURN"

# Set metadata after class creation to avoid it becoming an enum member
AngleUnitEnum._metadata = {
    "RADIAN": {'description': 'Radian (SI derived unit)', 'meaning': 'UO:0000123', 'annotations': {'symbol': 'rad', 'system': 'SI'}},
    "DEGREE": {'description': 'Degree', 'meaning': 'UO:0000185', 'annotations': {'symbol': '°', 'conversion_to_radian': '0.0174533'}},
    "MINUTE_OF_ARC": {'description': 'Minute of arc/arcminute', 'annotations': {'symbol': "'", 'conversion_to_degree': '0.0166667'}},
    "SECOND_OF_ARC": {'description': 'Second of arc/arcsecond', 'annotations': {'symbol': '"', 'conversion_to_degree': '0.000277778'}},
    "GRADIAN": {'description': 'Gradian/gon', 'annotations': {'symbol': 'gon', 'conversion_to_degree': '0.9'}},
    "TURN": {'description': 'Turn/revolution', 'annotations': {'symbol': 'turn', 'conversion_to_radian': '6.28319'}},
}

class DataSizeUnitEnum(RichEnum):
    """
    Units of digital data size
    """
    # Enum members
    BIT = "BIT"
    BYTE = "BYTE"
    KILOBYTE = "KILOBYTE"
    MEGABYTE = "MEGABYTE"
    GIGABYTE = "GIGABYTE"
    TERABYTE = "TERABYTE"
    PETABYTE = "PETABYTE"
    KIBIBYTE = "KIBIBYTE"
    MEBIBYTE = "MEBIBYTE"
    GIBIBYTE = "GIBIBYTE"
    TEBIBYTE = "TEBIBYTE"

# Set metadata after class creation to avoid it becoming an enum member
DataSizeUnitEnum._metadata = {
    "BIT": {'description': 'Bit (binary digit)', 'annotations': {'symbol': 'bit', 'base': 'binary'}},
    "BYTE": {'description': 'Byte (8 bits)', 'meaning': 'UO:0000233', 'annotations': {'symbol': 'B', 'conversion_to_bit': '8'}},
    "KILOBYTE": {'description': 'Kilobyte (1000 bytes)', 'meaning': 'UO:0000234', 'annotations': {'symbol': 'KB', 'conversion_to_byte': '1000', 'standard': 'decimal'}},
    "MEGABYTE": {'description': 'Megabyte (10^6 bytes)', 'meaning': 'UO:0000235', 'annotations': {'symbol': 'MB', 'conversion_to_byte': '1e6', 'standard': 'decimal'}},
    "GIGABYTE": {'description': 'Gigabyte (10^9 bytes)', 'annotations': {'symbol': 'GB', 'conversion_to_byte': '1e9', 'standard': 'decimal'}},
    "TERABYTE": {'description': 'Terabyte (10^12 bytes)', 'annotations': {'symbol': 'TB', 'conversion_to_byte': '1e12', 'standard': 'decimal'}},
    "PETABYTE": {'description': 'Petabyte (10^15 bytes)', 'annotations': {'symbol': 'PB', 'conversion_to_byte': '1e15', 'standard': 'decimal'}},
    "KIBIBYTE": {'description': 'Kibibyte (1024 bytes)', 'annotations': {'symbol': 'KiB', 'conversion_to_byte': '1024', 'standard': 'binary'}},
    "MEBIBYTE": {'description': 'Mebibyte (2^20 bytes)', 'annotations': {'symbol': 'MiB', 'conversion_to_byte': '1048576', 'standard': 'binary'}},
    "GIBIBYTE": {'description': 'Gibibyte (2^30 bytes)', 'annotations': {'symbol': 'GiB', 'conversion_to_byte': '1073741824', 'standard': 'binary'}},
    "TEBIBYTE": {'description': 'Tebibyte (2^40 bytes)', 'annotations': {'symbol': 'TiB', 'conversion_to_byte': '1099511627776', 'standard': 'binary'}},
}

class ImageFileFormatEnum(RichEnum):
    """
    Common image file formats
    """
    # Enum members
    JPEG = "JPEG"
    PNG = "PNG"
    GIF = "GIF"
    BMP = "BMP"
    TIFF = "TIFF"
    SVG = "SVG"
    WEBP = "WEBP"
    HEIC = "HEIC"
    RAW = "RAW"
    ICO = "ICO"

# Set metadata after class creation to avoid it becoming an enum member
ImageFileFormatEnum._metadata = {
    "JPEG": {'description': 'Joint Photographic Experts Group', 'meaning': 'EDAM:format_3579', 'annotations': {'extension': '.jpg, .jpeg', 'mime_type': 'image/jpeg', 'compression': 'lossy'}, 'aliases': ['JPG']},
    "PNG": {'description': 'Portable Network Graphics', 'meaning': 'EDAM:format_3603', 'annotations': {'extension': '.png', 'mime_type': 'image/png', 'compression': 'lossless'}},
    "GIF": {'description': 'Graphics Interchange Format', 'meaning': 'EDAM:format_3467', 'annotations': {'extension': '.gif', 'mime_type': 'image/gif', 'features': 'animation support'}},
    "BMP": {'description': 'Bitmap Image File', 'meaning': 'EDAM:format_3592', 'annotations': {'extension': '.bmp', 'mime_type': 'image/bmp', 'compression': 'uncompressed'}},
    "TIFF": {'description': 'Tagged Image File Format', 'meaning': 'EDAM:format_3591', 'annotations': {'extension': '.tif, .tiff', 'mime_type': 'image/tiff', 'use': 'professional photography, scanning'}},
    "SVG": {'description': 'Scalable Vector Graphics', 'meaning': 'EDAM:format_3604', 'annotations': {'extension': '.svg', 'mime_type': 'image/svg+xml', 'type': 'vector'}},
    "WEBP": {'description': 'WebP image format', 'annotations': {'extension': '.webp', 'mime_type': 'image/webp', 'compression': 'lossy and lossless'}},
    "HEIC": {'description': 'High Efficiency Image Container', 'annotations': {'extension': '.heic, .heif', 'mime_type': 'image/heic', 'use': 'Apple devices'}},
    "RAW": {'description': 'Raw image format', 'annotations': {'extension': '.raw, .cr2, .nef, .arw', 'type': 'unprocessed sensor data'}},
    "ICO": {'description': 'Icon file format', 'annotations': {'extension': '.ico', 'mime_type': 'image/x-icon', 'use': 'favicons, app icons'}},
}

class DocumentFormatEnum(RichEnum):
    """
    Document and text file formats
    """
    # Enum members
    PDF = "PDF"
    DOCX = "DOCX"
    DOC = "DOC"
    TXT = "TXT"
    RTF = "RTF"
    ODT = "ODT"
    LATEX = "LATEX"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"
    XML = "XML"
    EPUB = "EPUB"

# Set metadata after class creation to avoid it becoming an enum member
DocumentFormatEnum._metadata = {
    "PDF": {'description': 'Portable Document Format', 'meaning': 'EDAM:format_3508', 'annotations': {'extension': '.pdf', 'mime_type': 'application/pdf', 'creator': 'Adobe'}},
    "DOCX": {'description': 'Microsoft Word Open XML', 'annotations': {'extension': '.docx', 'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application': 'Microsoft Word'}},
    "DOC": {'description': 'Microsoft Word legacy format', 'annotations': {'extension': '.doc', 'mime_type': 'application/msword', 'application': 'Microsoft Word (legacy)'}},
    "TXT": {'description': 'Plain text file', 'meaning': 'EDAM:format_1964', 'annotations': {'extension': '.txt', 'mime_type': 'text/plain', 'encoding': 'UTF-8, ASCII'}, 'aliases': ['plain text format (unformatted)']},
    "RTF": {'description': 'Rich Text Format', 'annotations': {'extension': '.rtf', 'mime_type': 'application/rtf'}},
    "ODT": {'description': 'OpenDocument Text', 'annotations': {'extension': '.odt', 'mime_type': 'application/vnd.oasis.opendocument.text', 'application': 'LibreOffice, OpenOffice'}},
    "LATEX": {'description': 'LaTeX document', 'meaning': 'EDAM:format_3817', 'annotations': {'extension': '.tex', 'mime_type': 'application/x-latex', 'use': 'scientific documents'}, 'aliases': ['latex', 'LaTeX']},
    "MARKDOWN": {'description': 'Markdown formatted text', 'annotations': {'extension': '.md, .markdown', 'mime_type': 'text/markdown'}},
    "HTML": {'description': 'HyperText Markup Language', 'meaning': 'EDAM:format_2331', 'annotations': {'extension': '.html, .htm', 'mime_type': 'text/html'}},
    "XML": {'description': 'Extensible Markup Language', 'meaning': 'EDAM:format_2332', 'annotations': {'extension': '.xml', 'mime_type': 'application/xml'}},
    "EPUB": {'description': 'Electronic Publication', 'annotations': {'extension': '.epub', 'mime_type': 'application/epub+zip', 'use': 'e-books'}},
}

class DataFormatEnum(RichEnum):
    """
    Structured data file formats
    """
    # Enum members
    JSON = "JSON"
    CSV = "CSV"
    TSV = "TSV"
    YAML = "YAML"
    TOML = "TOML"
    XLSX = "XLSX"
    XLS = "XLS"
    ODS = "ODS"
    PARQUET = "PARQUET"
    AVRO = "AVRO"
    HDF5 = "HDF5"
    NETCDF = "NETCDF"
    SQLITE = "SQLITE"

# Set metadata after class creation to avoid it becoming an enum member
DataFormatEnum._metadata = {
    "JSON": {'description': 'JavaScript Object Notation', 'meaning': 'EDAM:format_3464', 'annotations': {'extension': '.json', 'mime_type': 'application/json', 'type': 'text-based'}},
    "CSV": {'description': 'Comma-Separated Values', 'meaning': 'EDAM:format_3752', 'annotations': {'extension': '.csv', 'mime_type': 'text/csv', 'delimiter': 'comma'}},
    "TSV": {'description': 'Tab-Separated Values', 'meaning': 'EDAM:format_3475', 'annotations': {'extension': '.tsv, .tab', 'mime_type': 'text/tab-separated-values', 'delimiter': 'tab'}},
    "YAML": {'description': "YAML Ain't Markup Language", 'meaning': 'EDAM:format_3750', 'annotations': {'extension': '.yaml, .yml', 'mime_type': 'application/x-yaml'}},
    "TOML": {'description': "Tom's Obvious Minimal Language", 'annotations': {'extension': '.toml', 'mime_type': 'application/toml', 'use': 'configuration files'}},
    "XLSX": {'description': 'Microsoft Excel Open XML', 'annotations': {'extension': '.xlsx', 'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}},
    "XLS": {'description': 'Microsoft Excel legacy format', 'annotations': {'extension': '.xls', 'mime_type': 'application/vnd.ms-excel'}},
    "ODS": {'description': 'OpenDocument Spreadsheet', 'annotations': {'extension': '.ods', 'mime_type': 'application/vnd.oasis.opendocument.spreadsheet'}},
    "PARQUET": {'description': 'Apache Parquet columnar format', 'annotations': {'extension': '.parquet', 'mime_type': 'application/parquet', 'type': 'columnar storage'}},
    "AVRO": {'description': 'Apache Avro data serialization', 'annotations': {'extension': '.avro', 'mime_type': 'application/avro', 'features': 'schema evolution'}},
    "HDF5": {'description': 'Hierarchical Data Format version 5', 'meaning': 'EDAM:format_3590', 'annotations': {'extension': '.h5, .hdf5', 'mime_type': 'application/x-hdf', 'use': 'scientific data'}},
    "NETCDF": {'description': 'Network Common Data Form', 'meaning': 'EDAM:format_3650', 'annotations': {'extension': '.nc, .nc4', 'mime_type': 'application/x-netcdf', 'use': 'array-oriented scientific data'}},
    "SQLITE": {'description': 'SQLite database', 'annotations': {'extension': '.db, .sqlite, .sqlite3', 'mime_type': 'application/x-sqlite3', 'type': 'embedded database'}},
}

class ArchiveFormatEnum(RichEnum):
    """
    Archive and compression formats
    """
    # Enum members
    ZIP = "ZIP"
    TAR = "TAR"
    GZIP = "GZIP"
    TAR_GZ = "TAR_GZ"
    BZIP2 = "BZIP2"
    TAR_BZ2 = "TAR_BZ2"
    XZ = "XZ"
    TAR_XZ = "TAR_XZ"
    SEVEN_ZIP = "SEVEN_ZIP"
    RAR = "RAR"

# Set metadata after class creation to avoid it becoming an enum member
ArchiveFormatEnum._metadata = {
    "ZIP": {'description': 'ZIP archive', 'annotations': {'extension': '.zip', 'mime_type': 'application/zip', 'compression': 'DEFLATE'}},
    "TAR": {'description': 'Tape Archive', 'annotations': {'extension': '.tar', 'mime_type': 'application/x-tar', 'compression': 'none (archive only)'}},
    "GZIP": {'description': 'GNU zip', 'annotations': {'extension': '.gz', 'mime_type': 'application/gzip', 'compression': 'DEFLATE'}},
    "TAR_GZ": {'description': 'Gzipped tar archive', 'annotations': {'extension': '.tar.gz, .tgz', 'mime_type': 'application/x-gtar', 'compression': 'tar + gzip'}},
    "BZIP2": {'description': 'Bzip2 compression', 'annotations': {'extension': '.bz2', 'mime_type': 'application/x-bzip2', 'compression': 'Burrows-Wheeler'}},
    "TAR_BZ2": {'description': 'Bzip2 compressed tar archive', 'annotations': {'extension': '.tar.bz2, .tbz2', 'mime_type': 'application/x-bzip2'}},
    "XZ": {'description': 'XZ compression', 'annotations': {'extension': '.xz', 'mime_type': 'application/x-xz', 'compression': 'LZMA2'}},
    "TAR_XZ": {'description': 'XZ compressed tar archive', 'annotations': {'extension': '.tar.xz, .txz', 'mime_type': 'application/x-xz'}},
    "SEVEN_ZIP": {'description': '7-Zip archive', 'annotations': {'extension': '.7z', 'mime_type': 'application/x-7z-compressed', 'compression': 'LZMA'}},
    "RAR": {'description': 'RAR archive', 'annotations': {'extension': '.rar', 'mime_type': 'application/vnd.rar', 'proprietary': 'true'}},
}

class VideoFormatEnum(RichEnum):
    """
    Video file formats
    """
    # Enum members
    MP4 = "MP4"
    AVI = "AVI"
    MOV = "MOV"
    MKV = "MKV"
    WEBM = "WEBM"
    FLV = "FLV"
    WMV = "WMV"
    MPEG = "MPEG"

# Set metadata after class creation to avoid it becoming an enum member
VideoFormatEnum._metadata = {
    "MP4": {'description': 'MPEG-4 Part 14', 'annotations': {'extension': '.mp4', 'mime_type': 'video/mp4', 'codec': 'H.264, H.265'}},
    "AVI": {'description': 'Audio Video Interleave', 'annotations': {'extension': '.avi', 'mime_type': 'video/x-msvideo', 'creator': 'Microsoft'}},
    "MOV": {'description': 'QuickTime Movie', 'annotations': {'extension': '.mov', 'mime_type': 'video/quicktime', 'creator': 'Apple'}},
    "MKV": {'description': 'Matroska Video', 'annotations': {'extension': '.mkv', 'mime_type': 'video/x-matroska', 'features': 'multiple tracks'}},
    "WEBM": {'description': 'WebM video', 'annotations': {'extension': '.webm', 'mime_type': 'video/webm', 'codec': 'VP8, VP9'}},
    "FLV": {'description': 'Flash Video', 'annotations': {'extension': '.flv', 'mime_type': 'video/x-flv', 'status': 'legacy'}},
    "WMV": {'description': 'Windows Media Video', 'annotations': {'extension': '.wmv', 'mime_type': 'video/x-ms-wmv', 'creator': 'Microsoft'}},
    "MPEG": {'description': 'Moving Picture Experts Group', 'annotations': {'extension': '.mpeg, .mpg', 'mime_type': 'video/mpeg'}},
}

class AudioFormatEnum(RichEnum):
    """
    Audio file formats
    """
    # Enum members
    MP3 = "MP3"
    WAV = "WAV"
    FLAC = "FLAC"
    AAC = "AAC"
    OGG = "OGG"
    M4A = "M4A"
    WMA = "WMA"
    OPUS = "OPUS"
    AIFF = "AIFF"

# Set metadata after class creation to avoid it becoming an enum member
AudioFormatEnum._metadata = {
    "MP3": {'description': 'MPEG Audio Layer 3', 'annotations': {'extension': '.mp3', 'mime_type': 'audio/mpeg', 'compression': 'lossy'}},
    "WAV": {'description': 'Waveform Audio File Format', 'annotations': {'extension': '.wav', 'mime_type': 'audio/wav', 'compression': 'uncompressed'}},
    "FLAC": {'description': 'Free Lossless Audio Codec', 'annotations': {'extension': '.flac', 'mime_type': 'audio/flac', 'compression': 'lossless'}},
    "AAC": {'description': 'Advanced Audio Coding', 'annotations': {'extension': '.aac', 'mime_type': 'audio/aac', 'compression': 'lossy'}},
    "OGG": {'description': 'Ogg Vorbis', 'annotations': {'extension': '.ogg', 'mime_type': 'audio/ogg', 'compression': 'lossy'}},
    "M4A": {'description': 'MPEG-4 Audio', 'annotations': {'extension': '.m4a', 'mime_type': 'audio/mp4', 'compression': 'lossy or lossless'}},
    "WMA": {'description': 'Windows Media Audio', 'annotations': {'extension': '.wma', 'mime_type': 'audio/x-ms-wma', 'creator': 'Microsoft'}},
    "OPUS": {'description': 'Opus Interactive Audio Codec', 'annotations': {'extension': '.opus', 'mime_type': 'audio/opus', 'use': 'streaming, VoIP'}},
    "AIFF": {'description': 'Audio Interchange File Format', 'annotations': {'extension': '.aiff, .aif', 'mime_type': 'audio/aiff', 'creator': 'Apple'}},
}

class ProgrammingLanguageFileEnum(RichEnum):
    """
    Programming language source file extensions
    """
    # Enum members
    PYTHON = "PYTHON"
    JAVASCRIPT = "JAVASCRIPT"
    TYPESCRIPT = "TYPESCRIPT"
    JAVA = "JAVA"
    C = "C"
    CPP = "CPP"
    C_SHARP = "C_SHARP"
    GO = "GO"
    RUST = "RUST"
    RUBY = "RUBY"
    PHP = "PHP"
    SWIFT = "SWIFT"
    KOTLIN = "KOTLIN"
    R = "R"
    MATLAB = "MATLAB"
    JULIA = "JULIA"
    SHELL = "SHELL"

# Set metadata after class creation to avoid it becoming an enum member
ProgrammingLanguageFileEnum._metadata = {
    "PYTHON": {'description': 'Python source file', 'annotations': {'extension': '.py', 'mime_type': 'text/x-python'}},
    "JAVASCRIPT": {'description': 'JavaScript source file', 'annotations': {'extension': '.js', 'mime_type': 'text/javascript'}},
    "TYPESCRIPT": {'description': 'TypeScript source file', 'annotations': {'extension': '.ts', 'mime_type': 'text/typescript'}},
    "JAVA": {'description': 'Java source file', 'annotations': {'extension': '.java', 'mime_type': 'text/x-java-source'}},
    "C": {'description': 'C source file', 'annotations': {'extension': '.c', 'mime_type': 'text/x-c'}},
    "CPP": {'description': 'C++ source file', 'annotations': {'extension': '.cpp, .cc, .cxx', 'mime_type': 'text/x-c++'}},
    "C_SHARP": {'description': 'C# source file', 'annotations': {'extension': '.cs', 'mime_type': 'text/x-csharp'}},
    "GO": {'description': 'Go source file', 'annotations': {'extension': '.go', 'mime_type': 'text/x-go'}},
    "RUST": {'description': 'Rust source file', 'annotations': {'extension': '.rs', 'mime_type': 'text/x-rust'}},
    "RUBY": {'description': 'Ruby source file', 'annotations': {'extension': '.rb', 'mime_type': 'text/x-ruby'}},
    "PHP": {'description': 'PHP source file', 'annotations': {'extension': '.php', 'mime_type': 'text/x-php'}},
    "SWIFT": {'description': 'Swift source file', 'annotations': {'extension': '.swift', 'mime_type': 'text/x-swift'}},
    "KOTLIN": {'description': 'Kotlin source file', 'annotations': {'extension': '.kt', 'mime_type': 'text/x-kotlin'}},
    "R": {'description': 'R source file', 'annotations': {'extension': '.r, .R', 'mime_type': 'text/x-r'}},
    "MATLAB": {'description': 'MATLAB source file', 'annotations': {'extension': '.m', 'mime_type': 'text/x-matlab'}},
    "JULIA": {'description': 'Julia source file', 'annotations': {'extension': '.jl', 'mime_type': 'text/x-julia'}},
    "SHELL": {'description': 'Shell script', 'annotations': {'extension': '.sh, .bash', 'mime_type': 'text/x-shellscript'}},
}

class NetworkProtocolEnum(RichEnum):
    """
    Network communication protocols
    """
    # Enum members
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    FTP = "FTP"
    SFTP = "SFTP"
    SSH = "SSH"
    TELNET = "TELNET"
    SMTP = "SMTP"
    POP3 = "POP3"
    IMAP = "IMAP"
    DNS = "DNS"
    DHCP = "DHCP"
    TCP = "TCP"
    UDP = "UDP"
    WEBSOCKET = "WEBSOCKET"
    MQTT = "MQTT"
    AMQP = "AMQP"
    GRPC = "GRPC"

# Set metadata after class creation to avoid it becoming an enum member
NetworkProtocolEnum._metadata = {
    "HTTP": {'description': 'Hypertext Transfer Protocol', 'annotations': {'port': '80', 'layer': 'application', 'version': '1.0, 1.1, 2, 3'}},
    "HTTPS": {'description': 'HTTP Secure', 'annotations': {'port': '443', 'layer': 'application', 'encryption': 'TLS/SSL'}},
    "FTP": {'description': 'File Transfer Protocol', 'annotations': {'port': '21', 'layer': 'application', 'use': 'file transfer'}},
    "SFTP": {'description': 'SSH File Transfer Protocol', 'annotations': {'port': '22', 'layer': 'application', 'encryption': 'SSH'}},
    "SSH": {'description': 'Secure Shell', 'annotations': {'port': '22', 'layer': 'application', 'use': 'secure remote access'}},
    "TELNET": {'description': 'Telnet protocol', 'annotations': {'port': '23', 'layer': 'application', 'security': 'unencrypted'}},
    "SMTP": {'description': 'Simple Mail Transfer Protocol', 'annotations': {'port': '25, 587', 'layer': 'application', 'use': 'email sending'}},
    "POP3": {'description': 'Post Office Protocol version 3', 'annotations': {'port': '110, 995', 'layer': 'application', 'use': 'email retrieval'}},
    "IMAP": {'description': 'Internet Message Access Protocol', 'annotations': {'port': '143, 993', 'layer': 'application', 'use': 'email access'}},
    "DNS": {'description': 'Domain Name System', 'annotations': {'port': '53', 'layer': 'application', 'use': 'name resolution'}},
    "DHCP": {'description': 'Dynamic Host Configuration Protocol', 'annotations': {'port': '67, 68', 'layer': 'application', 'use': 'IP assignment'}},
    "TCP": {'description': 'Transmission Control Protocol', 'annotations': {'layer': 'transport', 'type': 'connection-oriented'}},
    "UDP": {'description': 'User Datagram Protocol', 'annotations': {'layer': 'transport', 'type': 'connectionless'}},
    "WEBSOCKET": {'description': 'WebSocket protocol', 'annotations': {'port': '80, 443', 'layer': 'application', 'use': 'bidirectional communication'}},
    "MQTT": {'description': 'Message Queuing Telemetry Transport', 'annotations': {'port': '1883, 8883', 'layer': 'application', 'use': 'IoT messaging'}},
    "AMQP": {'description': 'Advanced Message Queuing Protocol', 'annotations': {'port': '5672', 'layer': 'application', 'use': 'message queuing'}},
    "GRPC": {'description': 'gRPC Remote Procedure Call', 'annotations': {'transport': 'HTTP/2', 'use': 'RPC framework'}},
}

class TechnologyReadinessLevel(RichEnum):
    """
    NASA's Technology Readiness Level scale for assessing the maturity of technologies from basic research through operational deployment
    """
    # Enum members
    TRL_1 = "TRL_1"
    TRL_2 = "TRL_2"
    TRL_3 = "TRL_3"
    TRL_4 = "TRL_4"
    TRL_5 = "TRL_5"
    TRL_6 = "TRL_6"
    TRL_7 = "TRL_7"
    TRL_8 = "TRL_8"
    TRL_9 = "TRL_9"

# Set metadata after class creation to avoid it becoming an enum member
TechnologyReadinessLevel._metadata = {
    "TRL_1": {'description': 'Basic principles observed and reported'},
    "TRL_2": {'description': 'Technology concept and/or application formulated'},
    "TRL_3": {'description': 'Analytical and experimental critical function and/or characteristic proof of concept'},
    "TRL_4": {'description': 'Component and/or breadboard validation in laboratory environment'},
    "TRL_5": {'description': 'Component and/or breadboard validation in relevant environment'},
    "TRL_6": {'description': 'System/subsystem model or prototype demonstration in a relevant environment'},
    "TRL_7": {'description': 'System prototype demonstration in an operational environment'},
    "TRL_8": {'description': 'Actual system completed and qualified through test and demonstration'},
    "TRL_9": {'description': 'Actual system proven through successful mission operations'},
}

class SoftwareMaturityLevel(RichEnum):
    """
    General software maturity assessment levels
    """
    # Enum members
    ALPHA = "ALPHA"
    BETA = "BETA"
    RELEASE_CANDIDATE = "RELEASE_CANDIDATE"
    STABLE = "STABLE"
    MATURE = "MATURE"
    LEGACY = "LEGACY"
    DEPRECATED = "DEPRECATED"
    OBSOLETE = "OBSOLETE"

# Set metadata after class creation to avoid it becoming an enum member
SoftwareMaturityLevel._metadata = {
    "ALPHA": {'description': 'Early development stage with basic functionality, may be unstable'},
    "BETA": {'description': 'Feature-complete but may contain bugs, ready for testing'},
    "RELEASE_CANDIDATE": {'description': 'Stable version ready for final testing before release'},
    "STABLE": {'description': 'Production-ready with proven stability and reliability'},
    "MATURE": {'description': 'Well-established with extensive usage and proven track record'},
    "LEGACY": {'description': 'Older version still in use but no longer actively developed'},
    "DEPRECATED": {'description': 'No longer recommended for use, superseded by newer versions'},
    "OBSOLETE": {'description': 'No longer supported or maintained'},
}

class CapabilityMaturityLevel(RichEnum):
    """
    CMMI levels for assessing organizational process maturity in software development
    """
    # Enum members
    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
    LEVEL_4 = "LEVEL_4"
    LEVEL_5 = "LEVEL_5"

# Set metadata after class creation to avoid it becoming an enum member
CapabilityMaturityLevel._metadata = {
    "LEVEL_1": {'description': 'Initial - Processes are unpredictable, poorly controlled, and reactive'},
    "LEVEL_2": {'description': 'Managed - Processes are characterized for projects and reactive'},
    "LEVEL_3": {'description': 'Defined - Processes are characterized for the organization and proactive'},
    "LEVEL_4": {'description': 'Quantitatively Managed - Processes are measured and controlled'},
    "LEVEL_5": {'description': 'Optimizing - Focus on continuous process improvement'},
}

class StandardsMaturityLevel(RichEnum):
    """
    Maturity levels for standards and specifications
    """
    # Enum members
    DRAFT = "DRAFT"
    WORKING_DRAFT = "WORKING_DRAFT"
    COMMITTEE_DRAFT = "COMMITTEE_DRAFT"
    CANDIDATE_RECOMMENDATION = "CANDIDATE_RECOMMENDATION"
    PROPOSED_STANDARD = "PROPOSED_STANDARD"
    STANDARD = "STANDARD"
    MATURE_STANDARD = "MATURE_STANDARD"
    SUPERSEDED = "SUPERSEDED"
    WITHDRAWN = "WITHDRAWN"

# Set metadata after class creation to avoid it becoming an enum member
StandardsMaturityLevel._metadata = {
    "DRAFT": {'description': 'Initial draft under development'},
    "WORKING_DRAFT": {'description': 'Work in progress by working group'},
    "COMMITTEE_DRAFT": {'description': 'Draft reviewed by committee'},
    "CANDIDATE_RECOMMENDATION": {'description': 'Mature draft ready for implementation testing'},
    "PROPOSED_STANDARD": {'description': 'Stable specification ready for adoption'},
    "STANDARD": {'description': 'Approved and published standard'},
    "MATURE_STANDARD": {'description': 'Well-established standard with wide adoption'},
    "SUPERSEDED": {'description': 'Replaced by a newer version'},
    "WITHDRAWN": {'description': 'No longer valid or recommended'},
}

class ProjectMaturityLevel(RichEnum):
    """
    General project development maturity assessment
    """
    # Enum members
    CONCEPT = "CONCEPT"
    PLANNING = "PLANNING"
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    PILOT = "PILOT"
    PRODUCTION = "PRODUCTION"
    MAINTENANCE = "MAINTENANCE"
    END_OF_LIFE = "END_OF_LIFE"

# Set metadata after class creation to avoid it becoming an enum member
ProjectMaturityLevel._metadata = {
    "CONCEPT": {'description': 'Initial idea or concept stage'},
    "PLANNING": {'description': 'Project planning and design phase'},
    "DEVELOPMENT": {'description': 'Active development in progress'},
    "TESTING": {'description': 'Testing and quality assurance phase'},
    "PILOT": {'description': 'Limited deployment or pilot testing'},
    "PRODUCTION": {'description': 'Full production deployment'},
    "MAINTENANCE": {'description': 'Maintenance and support mode'},
    "END_OF_LIFE": {'description': 'Project reaching end of lifecycle'},
}

class DataMaturityLevel(RichEnum):
    """
    Levels of data quality, governance, and organizational maturity
    """
    # Enum members
    RAW = "RAW"
    CLEANED = "CLEANED"
    STANDARDIZED = "STANDARDIZED"
    INTEGRATED = "INTEGRATED"
    CURATED = "CURATED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"

# Set metadata after class creation to avoid it becoming an enum member
DataMaturityLevel._metadata = {
    "RAW": {'description': 'Unprocessed, uncleaned data'},
    "CLEANED": {'description': 'Basic cleaning and validation applied'},
    "STANDARDIZED": {'description': 'Conforms to defined standards and formats'},
    "INTEGRATED": {'description': 'Combined with other data sources'},
    "CURATED": {'description': 'Expert-reviewed and validated'},
    "PUBLISHED": {'description': 'Publicly available with proper metadata'},
    "ARCHIVED": {'description': 'Long-term preservation with access controls'},
}

class OpenSourceMaturityLevel(RichEnum):
    """
    Maturity assessment for open source projects
    """
    # Enum members
    EXPERIMENTAL = "EXPERIMENTAL"
    EMERGING = "EMERGING"
    ESTABLISHED = "ESTABLISHED"
    MATURE = "MATURE"
    DECLINING = "DECLINING"
    ARCHIVED = "ARCHIVED"

# Set metadata after class creation to avoid it becoming an enum member
OpenSourceMaturityLevel._metadata = {
    "EXPERIMENTAL": {'description': 'Early experimental project'},
    "EMERGING": {'description': 'Gaining traction and contributors'},
    "ESTABLISHED": {'description': 'Stable with active community'},
    "MATURE": {'description': 'Well-established with proven governance'},
    "DECLINING": {'description': 'Decreasing activity and maintenance'},
    "ARCHIVED": {'description': 'No longer actively maintained'},
}

class LegalEntityTypeEnum(RichEnum):
    """
    Legal entity types for business organizations
    """
    # Enum members
    SOLE_PROPRIETORSHIP = "SOLE_PROPRIETORSHIP"
    GENERAL_PARTNERSHIP = "GENERAL_PARTNERSHIP"
    LIMITED_PARTNERSHIP = "LIMITED_PARTNERSHIP"
    LIMITED_LIABILITY_PARTNERSHIP = "LIMITED_LIABILITY_PARTNERSHIP"
    LIMITED_LIABILITY_COMPANY = "LIMITED_LIABILITY_COMPANY"
    SINGLE_MEMBER_LLC = "SINGLE_MEMBER_LLC"
    MULTI_MEMBER_LLC = "MULTI_MEMBER_LLC"
    C_CORPORATION = "C_CORPORATION"
    S_CORPORATION = "S_CORPORATION"
    B_CORPORATION = "B_CORPORATION"
    PUBLIC_CORPORATION = "PUBLIC_CORPORATION"
    PRIVATE_CORPORATION = "PRIVATE_CORPORATION"
    NONPROFIT_CORPORATION = "NONPROFIT_CORPORATION"
    COOPERATIVE = "COOPERATIVE"
    JOINT_VENTURE = "JOINT_VENTURE"
    HOLDING_COMPANY = "HOLDING_COMPANY"
    SUBSIDIARY = "SUBSIDIARY"
    FRANCHISE = "FRANCHISE"
    GOVERNMENT_ENTITY = "GOVERNMENT_ENTITY"

# Set metadata after class creation to avoid it becoming an enum member
LegalEntityTypeEnum._metadata = {
    "SOLE_PROPRIETORSHIP": {'description': 'Business owned and operated by single individual', 'annotations': {'legal_separation': 'no separation from owner', 'liability': 'unlimited personal liability', 'taxation': 'pass-through to personal returns', 'complexity': 'simplest structure', 'registration': 'minimal requirements'}},
    "GENERAL_PARTNERSHIP": {'description': 'Business owned by two or more partners sharing responsibilities', 'annotations': {'ownership': 'shared among general partners', 'liability': 'unlimited personal liability for all partners', 'taxation': 'pass-through to partners', 'management': 'shared management responsibilities'}},
    "LIMITED_PARTNERSHIP": {'description': 'Partnership with general and limited partners', 'annotations': {'partner_types': 'general partners and limited partners', 'liability': 'general partners have unlimited liability', 'limited_liability': 'limited partners have liability protection', 'management': 'general partners manage operations'}},
    "LIMITED_LIABILITY_PARTNERSHIP": {'description': 'Partnership providing liability protection to all partners', 'annotations': {'liability': 'limited liability for all partners', 'professional_use': 'often used by professional services', 'taxation': 'pass-through taxation', 'management': 'flexible management structure'}},
    "LIMITED_LIABILITY_COMPANY": {'description': 'Hybrid entity combining corporation and partnership features', 'annotations': {'liability': 'limited liability protection', 'taxation': 'flexible tax election options', 'management': 'flexible management structure', 'formality': 'fewer formal requirements than corporations'}},
    "SINGLE_MEMBER_LLC": {'description': 'LLC with only one owner/member', 'annotations': {'ownership': 'single member', 'liability': 'limited liability protection', 'taxation': 'disregarded entity for tax purposes', 'simplicity': 'simpler than multi-member LLC'}},
    "MULTI_MEMBER_LLC": {'description': 'LLC with multiple owners/members', 'annotations': {'ownership': 'multiple members', 'liability': 'limited liability protection', 'taxation': 'partnership taxation by default', 'operating_agreement': 'recommended operating agreement'}},
    "C_CORPORATION": {'description': 'Traditional corporation with double taxation', 'annotations': {'legal_status': 'separate legal entity', 'liability': 'limited liability for shareholders', 'taxation': 'double taxation (corporate and dividend)', 'governance': 'formal board and officer structure', 'stock': 'can issue multiple classes of stock'}},
    "S_CORPORATION": {'description': 'Corporation electing pass-through taxation', 'annotations': {'taxation': 'pass-through to shareholders', 'shareholders': 'limited to 100 shareholders', 'stock_types': 'single class of stock only', 'eligibility': 'restrictions on shareholder types'}},
    "B_CORPORATION": {'description': 'Corporation with social and environmental mission', 'annotations': {'purpose': 'profit and public benefit', 'accountability': 'stakeholder governance requirements', 'transparency': 'annual benefit reporting', 'certification': 'optional third-party certification'}},
    "PUBLIC_CORPORATION": {'description': 'Corporation with publicly traded shares', 'annotations': {'shares': 'publicly traded on stock exchanges', 'regulation': 'SEC reporting requirements', 'governance': 'extensive governance requirements', 'liquidity': 'high share liquidity'}},
    "PRIVATE_CORPORATION": {'description': 'Corporation with privately held shares', 'annotations': {'shares': 'privately held shares', 'shareholders': 'limited number of shareholders', 'regulation': 'fewer regulatory requirements', 'liquidity': 'limited share liquidity'}},
    "NONPROFIT_CORPORATION": {'description': 'Corporation organized for charitable or public purposes', 'annotations': {'purpose': 'charitable, educational, or public benefit', 'taxation': 'tax-exempt status possible', 'profit_distribution': 'no profit distribution to members', 'governance': 'board of directors governance'}},
    "COOPERATIVE": {'description': 'Member-owned and democratically controlled organization', 'annotations': {'ownership': 'member ownership', 'control': 'democratic member control', 'benefits': 'benefits proportional to participation', 'purpose': 'mutual benefit of members'}},
    "JOINT_VENTURE": {'description': 'Temporary partnership for specific project or purpose', 'annotations': {'duration': 'temporary or project-specific', 'purpose': 'specific business objective', 'ownership': 'shared ownership of venture', 'liability': 'depends on structure chosen'}},
    "HOLDING_COMPANY": {'description': 'Company that owns controlling interests in other companies', 'annotations': {'purpose': 'own and control subsidiary companies', 'operations': 'minimal direct operations', 'structure': 'parent-subsidiary relationships', 'control': 'controls subsidiaries through ownership'}},
    "SUBSIDIARY": {'description': 'Company controlled by another company (parent)', 'annotations': {'control': 'controlled by parent company', 'ownership': 'majority owned by parent', 'operations': 'may operate independently', 'liability': 'separate legal entity'}},
    "FRANCHISE": {'description': "Business operating under franchisor's brand and system", 'annotations': {'relationship': 'franchisor-franchisee relationship', 'brand': 'operates under established brand', 'system': "follows franchisor's business system", 'fees': 'pays franchise fees and royalties'}},
    "GOVERNMENT_ENTITY": {'description': 'Entity owned and operated by government', 'annotations': {'ownership': 'government ownership', 'purpose': 'public service or policy implementation', 'regulation': 'government regulations and oversight', 'funding': 'government funding sources'}},
}

class OrganizationalStructureEnum(RichEnum):
    """
    Types of organizational hierarchy and reporting structures
    """
    # Enum members
    HIERARCHICAL = "HIERARCHICAL"
    FLAT = "FLAT"
    MATRIX = "MATRIX"
    FUNCTIONAL = "FUNCTIONAL"
    DIVISIONAL = "DIVISIONAL"
    NETWORK = "NETWORK"
    TEAM_BASED = "TEAM_BASED"
    VIRTUAL = "VIRTUAL"
    HYBRID = "HYBRID"

# Set metadata after class creation to avoid it becoming an enum member
OrganizationalStructureEnum._metadata = {
    "HIERARCHICAL": {'description': 'Traditional pyramid structure with clear chain of command', 'annotations': {'authority_flow': 'top-down authority', 'communication': 'vertical communication channels', 'levels': 'multiple management levels', 'control': 'centralized control', 'decision_making': 'centralized decision making'}},
    "FLAT": {'description': 'Minimal hierarchical levels with broader spans of control', 'annotations': {'levels': 'few hierarchical levels', 'span_of_control': 'broad spans of control', 'communication': 'direct communication', 'decision_making': 'decentralized decision making', 'flexibility': 'high flexibility'}},
    "MATRIX": {'description': 'Dual reporting relationships combining functional and project lines', 'annotations': {'reporting': 'dual reporting relationships', 'authority': 'shared authority between managers', 'flexibility': 'high project flexibility', 'complexity': 'increased complexity', 'communication': 'multidirectional communication'}},
    "FUNCTIONAL": {'description': 'Organization by business functions or departments', 'annotations': {'grouping': 'by business function', 'specialization': 'functional specialization', 'efficiency': 'operational efficiency', 'coordination': 'vertical coordination', 'expertise': 'concentrated expertise'}},
    "DIVISIONAL": {'description': 'Organization by product lines, markets, or geography', 'annotations': {'grouping': 'by products, markets, or geography', 'autonomy': 'divisional autonomy', 'focus': 'market or product focus', 'coordination': 'horizontal coordination', 'responsibility': 'profit center responsibility'}},
    "NETWORK": {'description': 'Flexible structure with interconnected relationships', 'annotations': {'relationships': 'network of relationships', 'flexibility': 'high flexibility', 'boundaries': 'blurred organizational boundaries', 'collaboration': 'extensive collaboration', 'adaptability': 'high adaptability'}},
    "TEAM_BASED": {'description': 'Organization around self-managing teams', 'annotations': {'unit': 'teams as basic organizational unit', 'management': 'self-managing teams', 'collaboration': 'high collaboration', 'decision_making': 'team-based decision making', 'flexibility': 'operational flexibility'}},
    "VIRTUAL": {'description': 'Geographically dispersed organization connected by technology', 'annotations': {'location': 'geographically dispersed', 'technology': 'technology-enabled communication', 'flexibility': 'location flexibility', 'coordination': 'virtual coordination', 'boundaries': 'minimal physical boundaries'}},
    "HYBRID": {'description': 'Combination of multiple organizational structures', 'annotations': {'combination': 'multiple structure types', 'flexibility': 'structural flexibility', 'adaptation': 'adaptable to different needs', 'complexity': 'increased structural complexity', 'customization': 'customized to organization needs'}},
}

class ManagementLevelEnum(RichEnum):
    """
    Hierarchical levels within organizational management structure
    """
    # Enum members
    BOARD_OF_DIRECTORS = "BOARD_OF_DIRECTORS"
    C_SUITE = "C_SUITE"
    SENIOR_EXECUTIVE = "SENIOR_EXECUTIVE"
    VICE_PRESIDENT = "VICE_PRESIDENT"
    DIRECTOR = "DIRECTOR"
    MANAGER = "MANAGER"
    SUPERVISOR = "SUPERVISOR"
    TEAM_LEAD = "TEAM_LEAD"
    SENIOR_INDIVIDUAL_CONTRIBUTOR = "SENIOR_INDIVIDUAL_CONTRIBUTOR"
    INDIVIDUAL_CONTRIBUTOR = "INDIVIDUAL_CONTRIBUTOR"
    ENTRY_LEVEL = "ENTRY_LEVEL"

# Set metadata after class creation to avoid it becoming an enum member
ManagementLevelEnum._metadata = {
    "BOARD_OF_DIRECTORS": {'description': 'Governing body elected by shareholders', 'annotations': {'authority': 'highest governance authority', 'responsibility': 'fiduciary responsibility to shareholders', 'oversight': 'strategic oversight and control', 'composition': 'independent and inside directors'}},
    "C_SUITE": {'description': 'Top executive leadership team', 'annotations': {'level': 'top executive level', 'scope': 'organization-wide responsibility', 'titles': 'CEO, CFO, COO, CTO, etc.', 'accountability': 'accountable to board of directors'}},
    "SENIOR_EXECUTIVE": {'description': 'Senior leadership below C-suite level', 'annotations': {'level': 'senior leadership', 'scope': 'major business unit or function', 'titles': 'EVP, SVP, General Manager', 'reporting': 'reports to C-suite'}},
    "VICE_PRESIDENT": {'description': 'Senior management responsible for major divisions', 'annotations': {'level': 'senior management', 'scope': 'division or major function', 'authority': 'significant decision-making authority', 'titles': 'VP, Assistant VP'}},
    "DIRECTOR": {'description': 'Management responsible for departments or major programs', 'annotations': {'level': 'middle management', 'scope': 'department or program', 'responsibility': 'departmental leadership', 'oversight': 'manages multiple managers'}},
    "MANAGER": {'description': 'Supervisory role managing teams or operations', 'annotations': {'level': 'middle management', 'scope': 'team or operational unit', 'responsibility': 'day-to-day operations', 'supervision': 'manages individual contributors'}},
    "SUPERVISOR": {'description': 'First-line management overseeing frontline employees', 'annotations': {'level': 'first-line management', 'scope': 'small team or shift', 'responsibility': 'direct supervision', 'interface': 'employee-management interface'}},
    "TEAM_LEAD": {'description': 'Lead role within team without formal management authority', 'annotations': {'level': 'senior individual contributor', 'authority': 'informal authority', 'responsibility': 'team coordination', 'expertise': 'technical or project leadership'}},
    "SENIOR_INDIVIDUAL_CONTRIBUTOR": {'description': 'Experienced professional without management responsibilities', 'annotations': {'level': 'senior professional', 'expertise': 'specialized expertise', 'mentoring': 'may mentor junior staff', 'projects': 'leads complex projects'}},
    "INDIVIDUAL_CONTRIBUTOR": {'description': 'Professional or specialist role', 'annotations': {'level': 'professional', 'responsibility': 'individual work output', 'specialization': 'functional specialization', 'career_path': 'professional career track'}},
    "ENTRY_LEVEL": {'description': 'Beginning professional or support roles', 'annotations': {'experience': 'minimal professional experience', 'development': 'learning and development focus', 'supervision': 'close supervision', 'growth_potential': 'career growth opportunities'}},
}

class CorporateGovernanceRoleEnum(RichEnum):
    """
    Roles within corporate governance structure
    """
    # Enum members
    CHAIRMAN_OF_BOARD = "CHAIRMAN_OF_BOARD"
    LEAD_INDEPENDENT_DIRECTOR = "LEAD_INDEPENDENT_DIRECTOR"
    INDEPENDENT_DIRECTOR = "INDEPENDENT_DIRECTOR"
    INSIDE_DIRECTOR = "INSIDE_DIRECTOR"
    AUDIT_COMMITTEE_CHAIR = "AUDIT_COMMITTEE_CHAIR"
    COMPENSATION_COMMITTEE_CHAIR = "COMPENSATION_COMMITTEE_CHAIR"
    NOMINATING_COMMITTEE_CHAIR = "NOMINATING_COMMITTEE_CHAIR"
    CHIEF_EXECUTIVE_OFFICER = "CHIEF_EXECUTIVE_OFFICER"
    CHIEF_FINANCIAL_OFFICER = "CHIEF_FINANCIAL_OFFICER"
    CHIEF_OPERATING_OFFICER = "CHIEF_OPERATING_OFFICER"
    CORPORATE_SECRETARY = "CORPORATE_SECRETARY"

# Set metadata after class creation to avoid it becoming an enum member
CorporateGovernanceRoleEnum._metadata = {
    "CHAIRMAN_OF_BOARD": {'description': 'Leader of board of directors', 'annotations': {'leadership': 'board leadership', 'meetings': 'chairs board meetings', 'interface': 'shareholder interface', 'governance': 'governance oversight'}},
    "LEAD_INDEPENDENT_DIRECTOR": {'description': 'Senior independent director when chairman is not independent', 'annotations': {'independence': 'independent from management', 'leadership': 'leads independent directors', 'oversight': 'additional oversight role', 'communication': 'shareholder communication'}},
    "INDEPENDENT_DIRECTOR": {'description': 'Board member independent from company management', 'annotations': {'independence': 'independent from management', 'objectivity': 'objective oversight', 'committees': 'serves on key committees', 'governance': 'independent governance perspective'}},
    "INSIDE_DIRECTOR": {'description': 'Board member who is also company employee or has material relationship', 'annotations': {'relationship': 'material relationship with company', 'expertise': 'insider knowledge', 'perspective': 'management perspective', 'potential_conflicts': 'potential conflicts of interest'}},
    "AUDIT_COMMITTEE_CHAIR": {'description': "Chair of board's audit committee", 'annotations': {'committee': 'audit committee leadership', 'oversight': 'financial oversight', 'independence': 'must be independent', 'expertise': 'financial expertise required'}},
    "COMPENSATION_COMMITTEE_CHAIR": {'description': "Chair of board's compensation committee", 'annotations': {'committee': 'compensation committee leadership', 'responsibility': 'executive compensation oversight', 'independence': 'must be independent', 'alignment': 'shareholder interest alignment'}},
    "NOMINATING_COMMITTEE_CHAIR": {'description': "Chair of board's nominating and governance committee", 'annotations': {'committee': 'nominating committee leadership', 'responsibility': 'board composition and governance', 'succession': 'leadership succession planning', 'governance': 'governance best practices'}},
    "CHIEF_EXECUTIVE_OFFICER": {'description': 'Highest-ranking executive officer', 'annotations': {'authority': 'highest executive authority', 'strategy': 'strategic leadership', 'accountability': 'accountable to board', 'representation': 'company representation'}},
    "CHIEF_FINANCIAL_OFFICER": {'description': 'Senior executive responsible for financial management', 'annotations': {'responsibility': 'financial management', 'reporting': 'financial reporting oversight', 'compliance': 'financial compliance', 'strategy': 'financial strategy'}},
    "CHIEF_OPERATING_OFFICER": {'description': 'Senior executive responsible for operations', 'annotations': {'responsibility': 'operational management', 'execution': 'strategy execution', 'efficiency': 'operational efficiency', 'coordination': 'cross-functional coordination'}},
    "CORPORATE_SECRETARY": {'description': 'Officer responsible for corporate records and governance compliance', 'annotations': {'records': 'corporate records maintenance', 'compliance': 'governance compliance', 'meetings': 'board meeting coordination', 'legal': 'legal compliance oversight'}},
}

class BusinessOwnershipTypeEnum(RichEnum):
    """
    Types of business ownership structures
    """
    # Enum members
    PRIVATE_OWNERSHIP = "PRIVATE_OWNERSHIP"
    PUBLIC_OWNERSHIP = "PUBLIC_OWNERSHIP"
    FAMILY_OWNERSHIP = "FAMILY_OWNERSHIP"
    EMPLOYEE_OWNERSHIP = "EMPLOYEE_OWNERSHIP"
    INSTITUTIONAL_OWNERSHIP = "INSTITUTIONAL_OWNERSHIP"
    GOVERNMENT_OWNERSHIP = "GOVERNMENT_OWNERSHIP"
    FOREIGN_OWNERSHIP = "FOREIGN_OWNERSHIP"
    JOINT_OWNERSHIP = "JOINT_OWNERSHIP"

# Set metadata after class creation to avoid it becoming an enum member
BusinessOwnershipTypeEnum._metadata = {
    "PRIVATE_OWNERSHIP": {'description': 'Business owned by private individuals or entities', 'annotations': {'ownership': 'private individuals or entities', 'control': 'private control', 'capital': 'private capital sources', 'disclosure': 'limited disclosure requirements'}},
    "PUBLIC_OWNERSHIP": {'description': 'Business with publicly traded ownership shares', 'annotations': {'ownership': 'public shareholders', 'trading': 'publicly traded shares', 'regulation': 'extensive regulatory requirements', 'disclosure': 'public disclosure requirements'}},
    "FAMILY_OWNERSHIP": {'description': 'Business owned and controlled by family members', 'annotations': {'ownership': 'family members', 'succession': 'family succession planning', 'values': 'family values integration', 'long_term': 'long-term orientation'}},
    "EMPLOYEE_OWNERSHIP": {'description': 'Business owned by employees through stock or cooperative structure', 'annotations': {'ownership': 'employee owners', 'participation': 'employee participation', 'alignment': 'ownership-management alignment', 'structure': 'ESOP or cooperative structure'}},
    "INSTITUTIONAL_OWNERSHIP": {'description': 'Business owned by institutional investors', 'annotations': {'ownership': 'institutional investors', 'professional': 'professional management', 'capital': 'institutional capital', 'governance': 'institutional governance'}},
    "GOVERNMENT_OWNERSHIP": {'description': 'Business owned by government entities', 'annotations': {'ownership': 'government entities', 'purpose': 'public policy objectives', 'regulation': 'government oversight', 'funding': 'public funding'}},
    "FOREIGN_OWNERSHIP": {'description': 'Business owned by foreign individuals or entities', 'annotations': {'ownership': 'foreign entities', 'regulation': 'foreign investment regulations', 'capital': 'foreign capital', 'compliance': 'international compliance'}},
    "JOINT_OWNERSHIP": {'description': 'Business owned jointly by multiple parties', 'annotations': {'ownership': 'multiple ownership parties', 'agreements': 'joint ownership agreements', 'governance': 'shared governance', 'coordination': 'ownership coordination'}},
}

class BusinessSizeClassificationEnum(RichEnum):
    """
    Size classifications for business entities
    """
    # Enum members
    MICRO_BUSINESS = "MICRO_BUSINESS"
    SMALL_BUSINESS = "SMALL_BUSINESS"
    MEDIUM_BUSINESS = "MEDIUM_BUSINESS"
    LARGE_BUSINESS = "LARGE_BUSINESS"
    MULTINATIONAL_CORPORATION = "MULTINATIONAL_CORPORATION"
    FORTUNE_500 = "FORTUNE_500"

# Set metadata after class creation to avoid it becoming an enum member
BusinessSizeClassificationEnum._metadata = {
    "MICRO_BUSINESS": {'description': 'Very small business with minimal employees and revenue', 'annotations': {'employees': 'typically 1-9 employees', 'revenue': 'very low revenue', 'characteristics': 'home-based or small office', 'support': 'minimal administrative support'}},
    "SMALL_BUSINESS": {'description': 'Small business as defined by SBA standards', 'annotations': {'employees': 'varies by industry (typically <500)', 'revenue': 'varies by industry', 'sba_definition': 'meets SBA size standards', 'characteristics': 'independently owned and operated'}},
    "MEDIUM_BUSINESS": {'description': 'Mid-sized business between small and large classifications', 'annotations': {'employees': 'typically 500-1500 employees', 'revenue': 'moderate revenue levels', 'characteristics': 'regional or specialized market presence', 'structure': 'more formal organizational structure'}},
    "LARGE_BUSINESS": {'description': 'Major corporation with significant operations', 'annotations': {'employees': '>1500 employees', 'revenue': 'high revenue levels', 'market_presence': 'national or international presence', 'structure': 'complex organizational structure'}},
    "MULTINATIONAL_CORPORATION": {'description': 'Large corporation operating in multiple countries', 'annotations': {'geographic_scope': 'multiple countries', 'complexity': 'high operational complexity', 'structure': 'global organizational structure', 'coordination': 'international coordination'}},
    "FORTUNE_500": {'description': 'Among the 500 largest US corporations by revenue', 'annotations': {'ranking': 'Fortune 500 list', 'revenue': 'highest revenue levels', 'market_position': 'market leadership positions', 'recognition': 'prestigious business recognition'}},
}

class BusinessLifecycleStageEnum(RichEnum):
    """
    Stages in business development lifecycle
    """
    # Enum members
    CONCEPT_STAGE = "CONCEPT_STAGE"
    STARTUP_STAGE = "STARTUP_STAGE"
    GROWTH_STAGE = "GROWTH_STAGE"
    EXPANSION_STAGE = "EXPANSION_STAGE"
    MATURITY_STAGE = "MATURITY_STAGE"
    DECLINE_STAGE = "DECLINE_STAGE"
    TURNAROUND_STAGE = "TURNAROUND_STAGE"
    EXIT_STAGE = "EXIT_STAGE"

# Set metadata after class creation to avoid it becoming an enum member
BusinessLifecycleStageEnum._metadata = {
    "CONCEPT_STAGE": {'description': 'Initial business idea development and validation', 'annotations': {'focus': 'idea development and validation', 'activities': 'market research, business planning', 'funding': 'personal or angel funding', 'risk': 'highest risk level'}},
    "STARTUP_STAGE": {'description': 'Business launch and early operations', 'annotations': {'focus': 'product development and market entry', 'activities': 'building initial customer base', 'funding': 'seed funding, early investments', 'growth': 'rapid learning and adaptation'}},
    "GROWTH_STAGE": {'description': 'Rapid expansion and scaling operations', 'annotations': {'focus': 'scaling operations and market expansion', 'activities': 'increasing market share', 'funding': 'venture capital, growth financing', 'challenges': 'scaling challenges'}},
    "EXPANSION_STAGE": {'description': 'Market expansion and diversification', 'annotations': {'focus': 'market expansion and diversification', 'activities': 'new markets, products, or services', 'funding': 'growth capital, strategic investments', 'sophistication': 'increased operational sophistication'}},
    "MATURITY_STAGE": {'description': 'Stable operations with established market position', 'annotations': {'focus': 'operational efficiency and market defense', 'activities': 'defending market position', 'funding': 'self-funding, debt financing', 'stability': 'stable cash flows'}},
    "DECLINE_STAGE": {'description': 'Decreasing market relevance or performance', 'annotations': {'focus': 'cost reduction and restructuring', 'activities': 'turnaround efforts or exit planning', 'challenges': 'declining revenues or relevance', 'options': 'restructuring, sale, or closure'}},
    "TURNAROUND_STAGE": {'description': 'Recovery efforts from decline or crisis', 'annotations': {'focus': 'crisis management and recovery', 'activities': 'restructuring and repositioning', 'leadership': 'turnaround management', 'urgency': 'urgent transformation needs'}},
    "EXIT_STAGE": {'description': 'Business sale, merger, or closure', 'annotations': {'focus': 'exit strategy execution', 'activities': 'sale, merger, or liquidation', 'valuation': 'business valuation', 'transition': 'ownership transition'}},
}

class NAICSSectorEnum(RichEnum):
    """
    NAICS two-digit sector codes (North American Industry Classification System)
    """
    # Enum members
    SECTOR_11 = "SECTOR_11"
    SECTOR_21 = "SECTOR_21"
    SECTOR_22 = "SECTOR_22"
    SECTOR_23 = "SECTOR_23"
    SECTOR_31_33 = "SECTOR_31_33"
    SECTOR_42 = "SECTOR_42"
    SECTOR_44_45 = "SECTOR_44_45"
    SECTOR_48_49 = "SECTOR_48_49"
    SECTOR_51 = "SECTOR_51"
    SECTOR_52 = "SECTOR_52"
    SECTOR_53 = "SECTOR_53"
    SECTOR_54 = "SECTOR_54"
    SECTOR_55 = "SECTOR_55"
    SECTOR_56 = "SECTOR_56"
    SECTOR_61 = "SECTOR_61"
    SECTOR_62 = "SECTOR_62"
    SECTOR_71 = "SECTOR_71"
    SECTOR_72 = "SECTOR_72"
    SECTOR_81 = "SECTOR_81"
    SECTOR_92 = "SECTOR_92"

# Set metadata after class creation to avoid it becoming an enum member
NAICSSectorEnum._metadata = {
    "SECTOR_11": {'description': 'Establishments engaged in agriculture, forestry, fishing, and hunting', 'annotations': {'naics_code': '11', 'activities': 'crop production, animal production, forestry, fishing', 'economic_base': 'natural resource extraction and production'}},
    "SECTOR_21": {'description': 'Establishments engaged in extracting natural resources', 'annotations': {'naics_code': '21', 'activities': 'oil and gas extraction, mining, support activities', 'economic_base': 'natural resource extraction'}},
    "SECTOR_22": {'description': 'Establishments engaged in providing utilities', 'annotations': {'naics_code': '22', 'activities': 'electric power, natural gas, water, sewage, waste management', 'regulation': 'heavily regulated'}},
    "SECTOR_23": {'description': 'Establishments engaged in construction activities', 'annotations': {'naics_code': '23', 'activities': 'building construction, heavy construction, specialty trade contractors', 'cyclical': 'highly cyclical industry'}},
    "SECTOR_31_33": {'description': 'Establishments engaged in manufacturing goods', 'annotations': {'naics_code': '31-33', 'activities': 'food, chemicals, machinery, transportation equipment', 'value_added': 'transforms materials into finished goods'}},
    "SECTOR_42": {'description': 'Establishments engaged in wholesale distribution', 'annotations': {'naics_code': '42', 'activities': 'merchant wholesalers, agents and brokers', 'function': 'intermediary between manufacturers and retailers'}},
    "SECTOR_44_45": {'description': 'Establishments engaged in retail sales to consumers', 'annotations': {'naics_code': '44-45', 'activities': 'motor vehicle dealers, food stores, general merchandise', 'customer': 'sells to final consumers'}},
    "SECTOR_48_49": {'description': 'Establishments providing transportation and warehousing services', 'annotations': {'naics_code': '48-49', 'activities': 'air, rail, water, truck transportation, warehousing', 'infrastructure': 'transportation infrastructure dependent'}},
    "SECTOR_51": {'description': 'Establishments in information industries', 'annotations': {'naics_code': '51', 'activities': 'publishing, broadcasting, telecommunications, data processing', 'technology': 'information technology and content'}},
    "SECTOR_52": {'description': 'Establishments providing financial services', 'annotations': {'naics_code': '52', 'activities': 'banking, securities, insurance, funds and trusts', 'regulation': 'highly regulated financial sector'}},
    "SECTOR_53": {'description': 'Establishments engaged in real estate and rental activities', 'annotations': {'naics_code': '53', 'activities': 'real estate, rental and leasing services', 'asset_type': 'real and personal property'}},
    "SECTOR_54": {'description': 'Establishments providing professional services', 'annotations': {'naics_code': '54', 'activities': 'legal, accounting, engineering, consulting, research', 'knowledge_based': 'knowledge and skill intensive'}},
    "SECTOR_55": {'description': 'Establishments serving as holding companies or managing enterprises', 'annotations': {'naics_code': '55', 'activities': 'holding companies, corporate management', 'function': 'corporate ownership and management'}},
    "SECTOR_56": {'description': 'Establishments providing administrative and support services', 'annotations': {'naics_code': '56', 'activities': 'administrative services, waste management, remediation', 'support_function': 'business support services'}},
    "SECTOR_61": {'description': 'Establishments providing educational instruction', 'annotations': {'naics_code': '61', 'activities': 'schools, colleges, training programs', 'public_private': 'public and private education'}},
    "SECTOR_62": {'description': 'Establishments providing health care and social assistance', 'annotations': {'naics_code': '62', 'activities': 'hospitals, medical practices, social assistance', 'essential_services': 'essential public services'}},
    "SECTOR_71": {'description': 'Establishments in arts, entertainment, and recreation', 'annotations': {'naics_code': '71', 'activities': 'performing arts, spectator sports, museums, recreation', 'discretionary': 'discretionary consumer spending'}},
    "SECTOR_72": {'description': 'Establishments providing accommodation and food services', 'annotations': {'naics_code': '72', 'activities': 'hotels, restaurants, food services', 'consumer_services': 'consumer hospitality services'}},
    "SECTOR_81": {'description': 'Establishments providing other services', 'annotations': {'naics_code': '81', 'activities': 'repair, personal care, religious organizations', 'diverse': 'diverse service activities'}},
    "SECTOR_92": {'description': 'Government establishments', 'annotations': {'naics_code': '92', 'activities': 'executive, legislative, judicial, public safety', 'sector': 'government sector'}},
}

class EconomicSectorEnum(RichEnum):
    """
    Broad economic sector classifications
    """
    # Enum members
    PRIMARY_SECTOR = "PRIMARY_SECTOR"
    SECONDARY_SECTOR = "SECONDARY_SECTOR"
    TERTIARY_SECTOR = "TERTIARY_SECTOR"
    QUATERNARY_SECTOR = "QUATERNARY_SECTOR"
    QUINARY_SECTOR = "QUINARY_SECTOR"

# Set metadata after class creation to avoid it becoming an enum member
EconomicSectorEnum._metadata = {
    "PRIMARY_SECTOR": {'description': 'Economic activities extracting natural resources', 'annotations': {'activities': 'agriculture, mining, forestry, fishing', 'output': 'raw materials and natural resources', 'employment': 'typically lower employment share in developed economies', 'development_stage': 'dominant in early economic development'}},
    "SECONDARY_SECTOR": {'description': 'Economic activities manufacturing and processing goods', 'annotations': {'activities': 'manufacturing, construction, utilities', 'output': 'processed and manufactured goods', 'value_added': 'transforms raw materials into finished products', 'employment': 'historically significant in industrial economies'}},
    "TERTIARY_SECTOR": {'description': 'Economic activities providing services', 'annotations': {'activities': 'retail, hospitality, transportation, finance, healthcare', 'output': 'services to consumers and businesses', 'growth': 'largest and fastest growing sector in developed economies', 'employment': 'dominant employment sector'}},
    "QUATERNARY_SECTOR": {'description': 'Knowledge-based economic activities', 'annotations': {'activities': 'research, education, information technology, consulting', 'output': 'knowledge, information, and intellectual services', 'characteristics': 'high skill and education requirements', 'growth': 'rapidly growing in knowledge economies'}},
    "QUINARY_SECTOR": {'description': 'High-level decision-making and policy services', 'annotations': {'activities': 'top-level government, healthcare, education, culture', 'output': 'highest level services and decision-making', 'characteristics': 'elite services and leadership roles', 'scope': 'limited to highest level activities'}},
}

class BusinessActivityTypeEnum(RichEnum):
    """
    Types of primary business activities
    """
    # Enum members
    PRODUCTION = "PRODUCTION"
    DISTRIBUTION = "DISTRIBUTION"
    SERVICES = "SERVICES"
    TECHNOLOGY = "TECHNOLOGY"
    FINANCE = "FINANCE"
    INFORMATION = "INFORMATION"
    EDUCATION = "EDUCATION"
    HEALTHCARE = "HEALTHCARE"
    ENTERTAINMENT = "ENTERTAINMENT"
    PROFESSIONAL_SERVICES = "PROFESSIONAL_SERVICES"

# Set metadata after class creation to avoid it becoming an enum member
BusinessActivityTypeEnum._metadata = {
    "PRODUCTION": {'description': 'Creating or manufacturing physical goods', 'annotations': {'output': 'physical products and goods', 'process': 'transformation of materials', 'assets': 'physical assets and equipment intensive', 'examples': 'factories, farms, mines'}},
    "DISTRIBUTION": {'description': 'Moving goods from producers to consumers', 'annotations': {'function': 'intermediary between producers and consumers', 'value_added': 'place and time utility', 'examples': 'wholesalers, retailers, logistics companies', 'efficiency': 'improves market efficiency'}},
    "SERVICES": {'description': 'Providing intangible services to customers', 'annotations': {'output': 'intangible services', 'characteristics': 'labor intensive, customized', 'examples': 'consulting, healthcare, hospitality', 'customer_interaction': 'high customer interaction'}},
    "TECHNOLOGY": {'description': 'Developing and applying technology solutions', 'annotations': {'focus': 'technology development and application', 'innovation': 'research and development intensive', 'examples': 'software companies, biotech, engineering', 'intellectual_property': 'high intellectual property content'}},
    "FINANCE": {'description': 'Providing financial and investment services', 'annotations': {'function': 'financial intermediation and services', 'regulation': 'highly regulated', 'examples': 'banks, insurance, investment firms', 'capital': 'capital intensive'}},
    "INFORMATION": {'description': 'Creating, processing, and distributing information', 'annotations': {'output': 'information and content', 'channels': 'various distribution channels', 'examples': 'media companies, publishers, data processors', 'technology_dependent': 'technology platform dependent'}},
    "EDUCATION": {'description': 'Providing educational and training services', 'annotations': {'function': 'knowledge and skill development', 'public_private': 'public and private providers', 'examples': 'schools, universities, training companies', 'social_impact': 'high social impact'}},
    "HEALTHCARE": {'description': 'Providing health and medical services', 'annotations': {'function': 'health and medical care', 'regulation': 'highly regulated', 'examples': 'hospitals, clinics, pharmaceutical companies', 'essential': 'essential service'}},
    "ENTERTAINMENT": {'description': 'Providing entertainment and recreational services', 'annotations': {'output': 'entertainment and leisure experiences', 'discretionary': 'discretionary consumer spending', 'examples': 'media, sports, tourism, gaming', 'experience_based': 'experience and emotion based'}},
    "PROFESSIONAL_SERVICES": {'description': 'Providing specialized professional expertise', 'annotations': {'characteristics': 'high skill and knowledge requirements', 'customization': 'highly customized services', 'examples': 'law firms, consulting, accounting', 'expertise': 'specialized professional expertise'}},
}

class IndustryMaturityEnum(RichEnum):
    """
    Industry lifecycle and maturity stages
    """
    # Enum members
    EMERGING = "EMERGING"
    GROWTH = "GROWTH"
    MATURE = "MATURE"
    DECLINING = "DECLINING"
    TRANSFORMING = "TRANSFORMING"

# Set metadata after class creation to avoid it becoming an enum member
IndustryMaturityEnum._metadata = {
    "EMERGING": {'description': 'New industry in early development stage', 'annotations': {'characteristics': 'high uncertainty, rapid change', 'growth': 'high growth potential', 'technology': 'new or evolving technology', 'competition': 'few competitors, unclear standards', 'investment': 'high investment requirements'}},
    "GROWTH": {'description': 'Industry experiencing rapid expansion', 'annotations': {'characteristics': 'rapid market expansion', 'competition': 'increasing competition', 'standardization': 'emerging standards', 'investment': 'significant investment opportunities', 'profitability': 'improving profitability'}},
    "MATURE": {'description': 'Established industry with stable growth', 'annotations': {'characteristics': 'stable market conditions', 'growth': 'slower, steady growth', 'competition': 'established competitive structure', 'efficiency': 'focus on operational efficiency', 'consolidation': 'potential for consolidation'}},
    "DECLINING": {'description': 'Industry experiencing contraction', 'annotations': {'characteristics': 'decreasing demand', 'competition': 'intensifying competition for shrinking market', 'cost_focus': 'focus on cost reduction', 'consolidation': 'significant consolidation', 'exit': 'companies exiting industry'}},
    "TRANSFORMING": {'description': 'Industry undergoing fundamental change', 'annotations': {'characteristics': 'disruptive change and innovation', 'technology': 'technology-driven transformation', 'business_models': 'evolving business models', 'uncertainty': 'high uncertainty about future structure', 'opportunity': 'opportunities for innovation and disruption'}},
}

class MarketStructureEnum(RichEnum):
    """
    Competitive structure of industry markets
    """
    # Enum members
    PERFECT_COMPETITION = "PERFECT_COMPETITION"
    MONOPOLISTIC_COMPETITION = "MONOPOLISTIC_COMPETITION"
    OLIGOPOLY = "OLIGOPOLY"
    MONOPOLY = "MONOPOLY"
    DUOPOLY = "DUOPOLY"

# Set metadata after class creation to avoid it becoming an enum member
MarketStructureEnum._metadata = {
    "PERFECT_COMPETITION": {'description': 'Many small firms with identical products', 'annotations': {'competitors': 'many small competitors', 'products': 'homogeneous products', 'barriers': 'no barriers to entry', 'pricing': 'price takers', 'examples': 'agricultural commodities'}},
    "MONOPOLISTIC_COMPETITION": {'description': 'Many firms with differentiated products', 'annotations': {'competitors': 'many competitors', 'products': 'differentiated products', 'barriers': 'low barriers to entry', 'pricing': 'some pricing power', 'examples': 'restaurants, retail clothing'}},
    "OLIGOPOLY": {'description': 'Few large firms dominating the market', 'annotations': {'competitors': 'few large competitors', 'concentration': 'high market concentration', 'barriers': 'significant barriers to entry', 'interdependence': 'strategic interdependence', 'examples': 'automobiles, telecommunications'}},
    "MONOPOLY": {'description': 'Single firm controlling the market', 'annotations': {'competitors': 'single market leader', 'barriers': 'very high barriers to entry', 'pricing': 'price maker', 'regulation': 'often regulated', 'examples': 'utilities, patented products'}},
    "DUOPOLY": {'description': 'Two firms dominating the market', 'annotations': {'competitors': 'two dominant competitors', 'competition': 'head-to-head competition', 'barriers': 'high barriers to entry', 'strategy': 'strategic competition', 'examples': 'aircraft manufacturing, some software markets'}},
}

class IndustryRegulationLevelEnum(RichEnum):
    """
    Level of government regulation in different industries
    """
    # Enum members
    HIGHLY_REGULATED = "HIGHLY_REGULATED"
    MODERATELY_REGULATED = "MODERATELY_REGULATED"
    LIGHTLY_REGULATED = "LIGHTLY_REGULATED"
    SELF_REGULATED = "SELF_REGULATED"
    DEREGULATED = "DEREGULATED"

# Set metadata after class creation to avoid it becoming an enum member
IndustryRegulationLevelEnum._metadata = {
    "HIGHLY_REGULATED": {'description': 'Industries subject to extensive government oversight', 'annotations': {'oversight': 'extensive government oversight', 'compliance': 'complex compliance requirements', 'barriers': 'regulatory barriers to entry', 'examples': 'banking, healthcare, utilities, pharmaceuticals', 'reason': 'public safety, market power, or systemic risk'}},
    "MODERATELY_REGULATED": {'description': 'Industries with significant but focused regulation', 'annotations': {'oversight': 'focused regulatory oversight', 'compliance': 'specific compliance requirements', 'areas': 'targeted regulatory areas', 'examples': 'food service, transportation, insurance', 'balance': 'balance between oversight and flexibility'}},
    "LIGHTLY_REGULATED": {'description': 'Industries with minimal regulatory oversight', 'annotations': {'oversight': 'minimal regulatory oversight', 'compliance': 'basic compliance requirements', 'flexibility': 'high operational flexibility', 'examples': 'technology, consulting, retail', 'approach': 'market-based approach'}},
    "SELF_REGULATED": {'description': 'Industries primarily regulated by industry organizations', 'annotations': {'oversight': 'industry self-regulation', 'standards': 'industry-developed standards', 'compliance': 'voluntary compliance', 'examples': 'professional services, trade associations', 'effectiveness': 'varies by industry'}},
    "DEREGULATED": {'description': 'Industries formerly regulated but now market-based', 'annotations': {'history': 'formerly regulated industries', 'competition': 'market-based competition', 'transition': 'transition from regulation to competition', 'examples': 'airlines, telecommunications, energy', 'benefits': 'increased competition and efficiency'}},
}

class ManagementMethodologyEnum(RichEnum):
    """
    Management approaches and methodologies
    """
    # Enum members
    TRADITIONAL_MANAGEMENT = "TRADITIONAL_MANAGEMENT"
    AGILE_MANAGEMENT = "AGILE_MANAGEMENT"
    LEAN_MANAGEMENT = "LEAN_MANAGEMENT"
    PARTICIPATIVE_MANAGEMENT = "PARTICIPATIVE_MANAGEMENT"
    MATRIX_MANAGEMENT = "MATRIX_MANAGEMENT"
    PROJECT_MANAGEMENT = "PROJECT_MANAGEMENT"
    RESULTS_ORIENTED_MANAGEMENT = "RESULTS_ORIENTED_MANAGEMENT"
    SERVANT_LEADERSHIP = "SERVANT_LEADERSHIP"
    TRANSFORMATIONAL_MANAGEMENT = "TRANSFORMATIONAL_MANAGEMENT"
    DEMOCRATIC_MANAGEMENT = "DEMOCRATIC_MANAGEMENT"

# Set metadata after class creation to avoid it becoming an enum member
ManagementMethodologyEnum._metadata = {
    "TRADITIONAL_MANAGEMENT": {'description': 'Hierarchical command-and-control management approach', 'annotations': {'structure': 'hierarchical structure', 'authority': 'centralized authority', 'communication': 'top-down communication', 'control': 'direct supervision and control'}},
    "AGILE_MANAGEMENT": {'description': 'Flexible, iterative management approach', 'annotations': {'flexibility': 'adaptive and flexible', 'iteration': 'iterative approach', 'collaboration': 'cross-functional collaboration', 'customer_focus': 'customer-centric'}},
    "LEAN_MANAGEMENT": {'description': 'Waste elimination and value optimization approach', 'annotations': {'focus': 'waste elimination', 'value': 'value stream optimization', 'continuous_improvement': 'kaizen and continuous improvement', 'efficiency': 'operational efficiency'}},
    "PARTICIPATIVE_MANAGEMENT": {'description': 'Employee involvement in decision-making', 'annotations': {'involvement': 'employee participation', 'decision_making': 'shared decision-making', 'empowerment': 'employee empowerment', 'engagement': 'increased employee engagement'}},
    "MATRIX_MANAGEMENT": {'description': 'Dual reporting relationships and shared authority', 'annotations': {'structure': 'matrix reporting structure', 'authority': 'shared authority', 'flexibility': 'organizational flexibility', 'complexity': 'increased complexity'}},
    "PROJECT_MANAGEMENT": {'description': 'Structured approach to managing projects', 'annotations': {'methodology': 'project management methodology', 'lifecycle': 'project lifecycle management', 'deliverables': 'deliverable-focused', 'temporary': 'temporary organizational structure'}},
    "RESULTS_ORIENTED_MANAGEMENT": {'description': 'Focus on outcomes and performance results', 'annotations': {'focus': 'results and outcomes', 'measurement': 'performance measurement', 'accountability': 'accountability for results', 'goals': 'goal-oriented approach'}},
    "SERVANT_LEADERSHIP": {'description': 'Leader serves and supports team members', 'annotations': {'philosophy': 'service-oriented leadership', 'support': 'leader supports team', 'development': 'people development focus', 'empowerment': 'team empowerment'}},
    "TRANSFORMATIONAL_MANAGEMENT": {'description': 'Change-oriented and inspirational management', 'annotations': {'change': 'transformation and change focus', 'inspiration': 'inspirational leadership', 'vision': 'vision-driven', 'development': 'follower development'}},
    "DEMOCRATIC_MANAGEMENT": {'description': 'Collaborative and consensus-building approach', 'annotations': {'participation': 'democratic participation', 'consensus': 'consensus-building', 'equality': 'equal voice in decisions', 'transparency': 'transparent processes'}},
}

class StrategicFrameworkEnum(RichEnum):
    """
    Strategic planning and analysis frameworks
    """
    # Enum members
    SWOT_ANALYSIS = "SWOT_ANALYSIS"
    PORTERS_FIVE_FORCES = "PORTERS_FIVE_FORCES"
    BALANCED_SCORECARD = "BALANCED_SCORECARD"
    BLUE_OCEAN_STRATEGY = "BLUE_OCEAN_STRATEGY"
    ANSOFF_MATRIX = "ANSOFF_MATRIX"
    BCG_MATRIX = "BCG_MATRIX"
    VALUE_CHAIN_ANALYSIS = "VALUE_CHAIN_ANALYSIS"
    SCENARIO_PLANNING = "SCENARIO_PLANNING"
    STRATEGIC_CANVAS = "STRATEGIC_CANVAS"
    CORE_COMPETENCY_ANALYSIS = "CORE_COMPETENCY_ANALYSIS"

# Set metadata after class creation to avoid it becoming an enum member
StrategicFrameworkEnum._metadata = {
    "SWOT_ANALYSIS": {'description': 'Strengths, Weaknesses, Opportunities, Threats analysis', 'annotations': {'components': 'strengths, weaknesses, opportunities, threats', 'purpose': 'strategic positioning analysis', 'simplicity': 'simple and widely used', 'application': 'strategic planning and decision-making'}},
    "PORTERS_FIVE_FORCES": {'description': 'Industry competitiveness analysis framework', 'annotations': {'forces': 'competitive rivalry, supplier power, buyer power, substitutes, barriers', 'purpose': 'industry attractiveness analysis', 'competition': 'competitive strategy framework', 'application': 'industry analysis and strategy formulation'}},
    "BALANCED_SCORECARD": {'description': 'Performance measurement from multiple perspectives', 'annotations': {'perspectives': 'financial, customer, internal process, learning', 'purpose': 'strategic performance measurement', 'balance': 'balanced view of performance', 'alignment': 'strategy alignment tool'}},
    "BLUE_OCEAN_STRATEGY": {'description': 'Creating uncontested market space strategy', 'annotations': {'concept': 'value innovation and market creation', 'competition': 'competition avoidance', 'differentiation': 'differentiation and low cost', 'innovation': 'strategic innovation'}},
    "ANSOFF_MATRIX": {'description': 'Product and market growth strategy framework', 'annotations': {'dimensions': 'products and markets', 'strategies': 'market penetration, development, diversification', 'growth': 'growth strategy framework', 'risk': 'risk assessment of growth options'}},
    "BCG_MATRIX": {'description': 'Portfolio analysis of business units', 'annotations': {'dimensions': 'market growth and market share', 'categories': 'stars, cash cows, question marks, dogs', 'portfolio': 'business portfolio analysis', 'resource_allocation': 'resource allocation decisions'}},
    "VALUE_CHAIN_ANALYSIS": {'description': 'Analysis of value-creating activities', 'annotations': {'activities': 'primary and support activities', 'value': 'value creation analysis', 'advantage': 'competitive advantage source identification', 'optimization': 'value chain optimization'}},
    "SCENARIO_PLANNING": {'description': 'Multiple future scenario development and planning', 'annotations': {'scenarios': 'multiple future scenarios', 'uncertainty': 'uncertainty management', 'planning': 'strategic contingency planning', 'flexibility': 'strategic flexibility'}},
    "STRATEGIC_CANVAS": {'description': 'Visual representation of competitive factors', 'annotations': {'visualization': 'visual strategy representation', 'factors': 'competitive factors analysis', 'comparison': 'competitor comparison', 'innovation': 'value innovation identification'}},
    "CORE_COMPETENCY_ANALYSIS": {'description': 'Identification and development of core competencies', 'annotations': {'competencies': 'unique organizational capabilities', 'advantage': 'sustainable competitive advantage', 'focus': 'competency-based strategy', 'development': 'capability development'}},
}

class OperationalModelEnum(RichEnum):
    """
    Business operational models and approaches
    """
    # Enum members
    CENTRALIZED_OPERATIONS = "CENTRALIZED_OPERATIONS"
    DECENTRALIZED_OPERATIONS = "DECENTRALIZED_OPERATIONS"
    HYBRID_OPERATIONS = "HYBRID_OPERATIONS"
    OUTSOURCED_OPERATIONS = "OUTSOURCED_OPERATIONS"
    SHARED_SERVICES = "SHARED_SERVICES"
    NETWORK_OPERATIONS = "NETWORK_OPERATIONS"
    PLATFORM_OPERATIONS = "PLATFORM_OPERATIONS"
    AGILE_OPERATIONS = "AGILE_OPERATIONS"
    LEAN_OPERATIONS = "LEAN_OPERATIONS"
    DIGITAL_OPERATIONS = "DIGITAL_OPERATIONS"

# Set metadata after class creation to avoid it becoming an enum member
OperationalModelEnum._metadata = {
    "CENTRALIZED_OPERATIONS": {'description': 'Centralized operational control and decision-making', 'annotations': {'control': 'centralized control', 'efficiency': 'operational efficiency', 'standardization': 'standardized processes', 'coordination': 'central coordination'}},
    "DECENTRALIZED_OPERATIONS": {'description': 'Distributed operational control and autonomy', 'annotations': {'autonomy': 'local autonomy', 'responsiveness': 'market responsiveness', 'flexibility': 'operational flexibility', 'empowerment': 'local empowerment'}},
    "HYBRID_OPERATIONS": {'description': 'Combination of centralized and decentralized elements', 'annotations': {'combination': 'mixed centralized and decentralized', 'balance': 'balance between control and flexibility', 'optimization': 'situational optimization', 'complexity': 'increased complexity'}},
    "OUTSOURCED_OPERATIONS": {'description': 'External service provider operational model', 'annotations': {'provider': 'external service providers', 'focus': 'core competency focus', 'cost': 'cost optimization', 'expertise': 'specialized expertise'}},
    "SHARED_SERVICES": {'description': 'Centralized services shared across business units', 'annotations': {'sharing': 'shared service delivery', 'efficiency': 'scale efficiency', 'standardization': 'service standardization', 'cost_effectiveness': 'cost-effective service delivery'}},
    "NETWORK_OPERATIONS": {'description': 'Collaborative network of partners and suppliers', 'annotations': {'network': 'partner and supplier network', 'collaboration': 'collaborative operations', 'flexibility': 'network flexibility', 'coordination': 'network coordination'}},
    "PLATFORM_OPERATIONS": {'description': 'Platform-based business operational model', 'annotations': {'platform': 'platform-based operations', 'ecosystem': 'business ecosystem', 'scalability': 'scalable operations', 'network_effects': 'network effects'}},
    "AGILE_OPERATIONS": {'description': 'Flexible and responsive operational approach', 'annotations': {'agility': 'operational agility', 'responsiveness': 'market responsiveness', 'adaptation': 'rapid adaptation', 'iteration': 'iterative improvement'}},
    "LEAN_OPERATIONS": {'description': 'Waste elimination and value-focused operations', 'annotations': {'waste': 'waste elimination', 'value': 'value stream focus', 'efficiency': 'operational efficiency', 'continuous_improvement': 'continuous improvement'}},
    "DIGITAL_OPERATIONS": {'description': 'Technology-enabled and digital-first operations', 'annotations': {'technology': 'digital technology enabled', 'automation': 'process automation', 'data_driven': 'data-driven operations', 'scalability': 'digital scalability'}},
}

class PerformanceMeasurementEnum(RichEnum):
    """
    Performance measurement systems and approaches
    """
    # Enum members
    KEY_PERFORMANCE_INDICATORS = "KEY_PERFORMANCE_INDICATORS"
    OBJECTIVES_KEY_RESULTS = "OBJECTIVES_KEY_RESULTS"
    BALANCED_SCORECARD_MEASUREMENT = "BALANCED_SCORECARD_MEASUREMENT"
    RETURN_ON_INVESTMENT = "RETURN_ON_INVESTMENT"
    ECONOMIC_VALUE_ADDED = "ECONOMIC_VALUE_ADDED"
    CUSTOMER_SATISFACTION_METRICS = "CUSTOMER_SATISFACTION_METRICS"
    EMPLOYEE_ENGAGEMENT_METRICS = "EMPLOYEE_ENGAGEMENT_METRICS"
    OPERATIONAL_EFFICIENCY_METRICS = "OPERATIONAL_EFFICIENCY_METRICS"
    INNOVATION_METRICS = "INNOVATION_METRICS"
    SUSTAINABILITY_METRICS = "SUSTAINABILITY_METRICS"

# Set metadata after class creation to avoid it becoming an enum member
PerformanceMeasurementEnum._metadata = {
    "KEY_PERFORMANCE_INDICATORS": {'description': 'Specific metrics measuring critical performance areas', 'annotations': {'specificity': 'specific performance metrics', 'critical': 'critical success factors', 'measurement': 'quantitative measurement', 'tracking': 'performance tracking'}},
    "OBJECTIVES_KEY_RESULTS": {'description': 'Goal-setting framework with measurable outcomes', 'annotations': {'objectives': 'qualitative objectives', 'results': 'quantitative key results', 'alignment': 'organizational alignment', 'transparency': 'transparent goal setting'}},
    "BALANCED_SCORECARD_MEASUREMENT": {'description': 'Multi-perspective performance measurement system', 'annotations': {'perspectives': 'multiple performance perspectives', 'balance': 'balanced performance view', 'strategy': 'strategy-linked measurement', 'cause_effect': 'cause-and-effect relationships'}},
    "RETURN_ON_INVESTMENT": {'description': 'Financial return measurement relative to investment', 'annotations': {'financial': 'financial performance measure', 'investment': 'investment-based measurement', 'efficiency': 'capital efficiency', 'comparison': 'investment comparison'}},
    "ECONOMIC_VALUE_ADDED": {'description': 'Value creation measurement after cost of capital', 'annotations': {'value': 'economic value creation', 'capital_cost': 'cost of capital consideration', 'shareholder': 'shareholder value focus', 'performance': 'true economic performance'}},
    "CUSTOMER_SATISFACTION_METRICS": {'description': 'Customer experience and satisfaction measurement', 'annotations': {'customer': 'customer-focused measurement', 'satisfaction': 'satisfaction and loyalty', 'experience': 'customer experience', 'retention': 'customer retention'}},
    "EMPLOYEE_ENGAGEMENT_METRICS": {'description': 'Employee satisfaction and engagement measurement', 'annotations': {'engagement': 'employee engagement', 'satisfaction': 'employee satisfaction', 'retention': 'employee retention', 'productivity': 'employee productivity'}},
    "OPERATIONAL_EFFICIENCY_METRICS": {'description': 'Operational performance and efficiency measurement', 'annotations': {'efficiency': 'operational efficiency', 'productivity': 'process productivity', 'quality': 'quality metrics', 'cost': 'cost efficiency'}},
    "INNOVATION_METRICS": {'description': 'Innovation performance and capability measurement', 'annotations': {'innovation': 'innovation performance', 'development': 'new product development', 'improvement': 'process improvement', 'creativity': 'organizational creativity'}},
    "SUSTAINABILITY_METRICS": {'description': 'Environmental and social sustainability measurement', 'annotations': {'sustainability': 'sustainability performance', 'environmental': 'environmental impact', 'social': 'social responsibility', 'governance': 'governance effectiveness'}},
}

class DecisionMakingStyleEnum(RichEnum):
    """
    Decision-making approaches and styles
    """
    # Enum members
    AUTOCRATIC = "AUTOCRATIC"
    DEMOCRATIC = "DEMOCRATIC"
    CONSULTATIVE = "CONSULTATIVE"
    CONSENSUS = "CONSENSUS"
    DELEGATED = "DELEGATED"
    DATA_DRIVEN = "DATA_DRIVEN"
    INTUITIVE = "INTUITIVE"
    COMMITTEE = "COMMITTEE"
    COLLABORATIVE = "COLLABORATIVE"
    CRISIS = "CRISIS"

# Set metadata after class creation to avoid it becoming an enum member
DecisionMakingStyleEnum._metadata = {
    "AUTOCRATIC": {'description': 'Single decision-maker with full authority', 'annotations': {'authority': 'centralized decision authority', 'speed': 'fast decision making', 'control': 'complete control', 'input': 'limited input from others'}},
    "DEMOCRATIC": {'description': 'Group participation in decision-making process', 'annotations': {'participation': 'group participation', 'consensus': 'consensus building', 'input': 'diverse input and perspectives', 'ownership': 'shared ownership of decisions'}},
    "CONSULTATIVE": {'description': 'Leader consults others before deciding', 'annotations': {'consultation': 'stakeholder consultation', 'input': 'seeks input and advice', 'authority': 'leader retains decision authority', 'informed': 'informed decision making'}},
    "CONSENSUS": {'description': 'Agreement reached through group discussion', 'annotations': {'agreement': 'group agreement required', 'discussion': 'extensive group discussion', 'unanimous': 'unanimous or near-unanimous agreement', 'time': 'time-intensive process'}},
    "DELEGATED": {'description': 'Decision authority delegated to others', 'annotations': {'delegation': 'decision authority delegation', 'empowerment': 'employee empowerment', 'autonomy': 'decision autonomy', 'accountability': 'delegated accountability'}},
    "DATA_DRIVEN": {'description': 'Decisions based on data analysis and evidence', 'annotations': {'data': 'data and analytics based', 'evidence': 'evidence-based decisions', 'objectivity': 'objective decision making', 'analysis': 'analytical approach'}},
    "INTUITIVE": {'description': 'Decisions based on experience and gut feeling', 'annotations': {'intuition': 'intuition and experience based', 'speed': 'rapid decision making', 'experience': 'leverages experience', 'creativity': 'creative and innovative'}},
    "COMMITTEE": {'description': 'Formal group decision-making structure', 'annotations': {'structure': 'formal committee structure', 'representation': 'stakeholder representation', 'process': 'structured decision process', 'accountability': 'shared accountability'}},
    "COLLABORATIVE": {'description': 'Joint decision-making with shared responsibility', 'annotations': {'collaboration': 'collaborative approach', 'shared': 'shared responsibility', 'teamwork': 'team-based decisions', 'synergy': 'collective wisdom'}},
    "CRISIS": {'description': 'Rapid decision-making under crisis conditions', 'annotations': {'urgency': 'urgent decision making', 'limited_info': 'limited information available', 'speed': 'rapid response required', 'risk': 'high-risk decision making'}},
}

class LeadershipStyleEnum(RichEnum):
    """
    Leadership approaches and styles
    """
    # Enum members
    TRANSFORMATIONAL = "TRANSFORMATIONAL"
    TRANSACTIONAL = "TRANSACTIONAL"
    SERVANT = "SERVANT"
    AUTHENTIC = "AUTHENTIC"
    CHARISMATIC = "CHARISMATIC"
    SITUATIONAL = "SITUATIONAL"
    DEMOCRATIC = "DEMOCRATIC"
    AUTOCRATIC = "AUTOCRATIC"
    LAISSEZ_FAIRE = "LAISSEZ_FAIRE"
    COACHING = "COACHING"

# Set metadata after class creation to avoid it becoming an enum member
LeadershipStyleEnum._metadata = {
    "TRANSFORMATIONAL": {'description': 'Inspirational leadership that motivates change', 'annotations': {'inspiration': 'inspirational motivation', 'vision': 'visionary leadership', 'development': 'follower development', 'change': 'change-oriented'}},
    "TRANSACTIONAL": {'description': 'Exchange-based leadership with rewards and consequences', 'annotations': {'exchange': 'reward and consequence based', 'structure': 'structured approach', 'performance': 'performance-based', 'management': 'management by exception'}},
    "SERVANT": {'description': 'Leader serves followers and facilitates their growth', 'annotations': {'service': 'service to followers', 'empowerment': 'follower empowerment', 'development': 'personal development focus', 'humility': 'humble leadership approach'}},
    "AUTHENTIC": {'description': 'Genuine and self-aware leadership approach', 'annotations': {'authenticity': 'genuine and authentic', 'self_awareness': 'high self-awareness', 'values': 'values-based leadership', 'integrity': 'personal integrity'}},
    "CHARISMATIC": {'description': 'Inspiring leadership through personal charisma', 'annotations': {'charisma': 'personal charisma', 'inspiration': 'inspirational influence', 'emotion': 'emotional appeal', 'following': 'devoted following'}},
    "SITUATIONAL": {'description': 'Adaptive leadership based on situation requirements', 'annotations': {'adaptation': 'situational adaptation', 'flexibility': 'flexible approach', 'assessment': 'situation assessment', 'style_variation': 'varying leadership styles'}},
    "DEMOCRATIC": {'description': 'Participative leadership with shared decision-making', 'annotations': {'participation': 'follower participation', 'shared': 'shared decision making', 'empowerment': 'team empowerment', 'collaboration': 'collaborative approach'}},
    "AUTOCRATIC": {'description': 'Directive leadership with centralized control', 'annotations': {'control': 'centralized control', 'directive': 'directive approach', 'authority': 'strong authority', 'efficiency': 'decision efficiency'}},
    "LAISSEZ_FAIRE": {'description': 'Hands-off leadership with minimal interference', 'annotations': {'autonomy': 'high follower autonomy', 'minimal': 'minimal leadership intervention', 'freedom': 'freedom to operate', 'self_direction': 'self-directed teams'}},
    "COACHING": {'description': 'Development-focused leadership approach', 'annotations': {'development': 'skill and capability development', 'guidance': 'mentoring and guidance', 'growth': 'personal and professional growth', 'support': 'supportive leadership'}},
}

class BusinessProcessTypeEnum(RichEnum):
    """
    Types of business processes
    """
    # Enum members
    CORE_PROCESS = "CORE_PROCESS"
    SUPPORT_PROCESS = "SUPPORT_PROCESS"
    MANAGEMENT_PROCESS = "MANAGEMENT_PROCESS"
    OPERATIONAL_PROCESS = "OPERATIONAL_PROCESS"
    STRATEGIC_PROCESS = "STRATEGIC_PROCESS"
    INNOVATION_PROCESS = "INNOVATION_PROCESS"
    CUSTOMER_PROCESS = "CUSTOMER_PROCESS"
    FINANCIAL_PROCESS = "FINANCIAL_PROCESS"

# Set metadata after class creation to avoid it becoming an enum member
BusinessProcessTypeEnum._metadata = {
    "CORE_PROCESS": {'description': 'Primary processes that create customer value', 'annotations': {'value': 'direct customer value creation', 'primary': 'primary business activities', 'competitive': 'competitive advantage source', 'strategic': 'strategic importance'}},
    "SUPPORT_PROCESS": {'description': 'Processes that enable core business activities', 'annotations': {'support': 'supports core processes', 'enabling': 'enabling activities', 'infrastructure': 'business infrastructure', 'indirect': 'indirect value contribution'}},
    "MANAGEMENT_PROCESS": {'description': 'Processes for planning, controlling, and improving', 'annotations': {'management': 'management and governance', 'planning': 'planning and control', 'improvement': 'process improvement', 'oversight': 'organizational oversight'}},
    "OPERATIONAL_PROCESS": {'description': 'Day-to-day operational activities', 'annotations': {'operations': 'daily operations', 'routine': 'routine activities', 'execution': 'operational execution', 'efficiency': 'operational efficiency'}},
    "STRATEGIC_PROCESS": {'description': 'Long-term planning and strategic activities', 'annotations': {'strategy': 'strategic planning', 'long_term': 'long-term focus', 'direction': 'organizational direction', 'competitive': 'competitive positioning'}},
    "INNOVATION_PROCESS": {'description': 'Processes for developing new products or services', 'annotations': {'innovation': 'innovation and development', 'creativity': 'creative processes', 'new_development': 'new product/service development', 'competitive': 'competitive innovation'}},
    "CUSTOMER_PROCESS": {'description': 'Processes focused on customer interaction and service', 'annotations': {'customer': 'customer-facing processes', 'service': 'customer service', 'relationship': 'customer relationship', 'satisfaction': 'customer satisfaction'}},
    "FINANCIAL_PROCESS": {'description': 'Processes related to financial management', 'annotations': {'financial': 'financial management', 'accounting': 'accounting and reporting', 'control': 'financial control', 'compliance': 'financial compliance'}},
}

class QualityStandardEnum(RichEnum):
    """
    Quality management standards and frameworks
    """
    # Enum members
    ISO_9001 = "ISO_9001"
    ISO_14001 = "ISO_14001"
    ISO_45001 = "ISO_45001"
    ISO_27001 = "ISO_27001"
    TQM = "TQM"
    EFQM = "EFQM"
    MALCOLM_BALDRIGE = "MALCOLM_BALDRIGE"
    SIX_SIGMA = "SIX_SIGMA"
    LEAN_QUALITY = "LEAN_QUALITY"
    AS9100 = "AS9100"
    TS16949 = "TS16949"
    ISO_13485 = "ISO_13485"

# Set metadata after class creation to avoid it becoming an enum member
QualityStandardEnum._metadata = {
    "ISO_9001": {'description': 'International standard for quality management systems', 'annotations': {'standard': 'ISO 9001:2015', 'focus': 'quality management systems', 'approach': 'process-based approach', 'certification': 'third-party certification available', 'scope': 'applicable to all organizations'}},
    "ISO_14001": {'description': 'International standard for environmental management systems', 'annotations': {'standard': 'ISO 14001:2015', 'focus': 'environmental management', 'integration': 'integrates with quality management', 'compliance': 'environmental compliance', 'sustainability': 'environmental sustainability'}},
    "ISO_45001": {'description': 'International standard for occupational health and safety', 'annotations': {'standard': 'ISO 45001:2018', 'focus': 'occupational health and safety', 'integration': 'integrates with other management systems', 'prevention': 'injury and illness prevention', 'workplace': 'workplace safety'}},
    "ISO_27001": {'description': 'International standard for information security management', 'annotations': {'standard': 'ISO 27001:2013', 'focus': 'information security', 'risk': 'risk-based approach', 'confidentiality': 'confidentiality, integrity, availability', 'compliance': 'regulatory compliance'}},
    "TQM": {'description': 'Comprehensive quality management philosophy', 'annotations': {'philosophy': 'total quality philosophy', 'scope': 'organization-wide approach', 'customer': 'customer focus', 'improvement': 'continuous improvement', 'involvement': 'total employee involvement'}},
    "EFQM": {'description': 'European excellence model for organizational performance', 'annotations': {'model': 'excellence model', 'assessment': 'self-assessment framework', 'improvement': 'organizational improvement', 'excellence': 'business excellence', 'europe': 'European standard'}},
    "MALCOLM_BALDRIGE": {'description': 'US national quality framework and award', 'annotations': {'framework': 'performance excellence framework', 'award': 'national quality award', 'assessment': 'organizational assessment', 'excellence': 'performance excellence', 'united_states': 'US standard'}},
    "SIX_SIGMA": {'description': 'Data-driven quality improvement methodology', 'annotations': {'methodology': 'statistical quality improvement', 'data_driven': 'data and measurement focused', 'defect_reduction': 'defect and variation reduction', 'belt_system': 'belt certification system', 'tools': 'statistical tools and techniques'}},
    "LEAN_QUALITY": {'description': 'Waste elimination and value-focused quality approach', 'annotations': {'philosophy': 'lean philosophy', 'waste': 'waste elimination', 'value': 'value stream focus', 'efficiency': 'operational efficiency', 'improvement': 'continuous improvement'}},
    "AS9100": {'description': 'Quality standard for aerospace industry', 'annotations': {'industry': 'aerospace and defense', 'based_on': 'based on ISO 9001', 'requirements': 'additional aerospace requirements', 'certification': 'aerospace certification', 'safety': 'safety and reliability focus'}},
    "TS16949": {'description': 'Quality standard for automotive industry', 'annotations': {'industry': 'automotive industry', 'based_on': 'based on ISO 9001', 'requirements': 'automotive-specific requirements', 'supply_chain': 'automotive supply chain', 'defect_prevention': 'defect prevention focus'}},
    "ISO_13485": {'description': 'Quality standard for medical device industry', 'annotations': {'industry': 'medical device industry', 'regulatory': 'regulatory compliance', 'safety': 'patient safety focus', 'design_controls': 'design controls', 'risk_management': 'risk management'}},
}

class QualityMethodologyEnum(RichEnum):
    """
    Quality improvement methodologies and approaches
    """
    # Enum members
    DMAIC = "DMAIC"
    DMADV = "DMADV"
    PDCA = "PDCA"
    KAIZEN = "KAIZEN"
    LEAN_SIX_SIGMA = "LEAN_SIX_SIGMA"
    FIVE_S = "FIVE_S"
    ROOT_CAUSE_ANALYSIS = "ROOT_CAUSE_ANALYSIS"
    STATISTICAL_PROCESS_CONTROL = "STATISTICAL_PROCESS_CONTROL"
    FAILURE_MODE_ANALYSIS = "FAILURE_MODE_ANALYSIS"
    BENCHMARKING = "BENCHMARKING"

# Set metadata after class creation to avoid it becoming an enum member
QualityMethodologyEnum._metadata = {
    "DMAIC": {'description': 'Six Sigma problem-solving methodology', 'annotations': {'phases': 'Define, Measure, Analyze, Improve, Control', 'approach': 'data-driven problem solving', 'structured': 'structured improvement process', 'statistical': 'statistical analysis', 'six_sigma': 'Six Sigma methodology'}},
    "DMADV": {'description': 'Six Sigma design methodology for new processes', 'annotations': {'phases': 'Define, Measure, Analyze, Design, Verify', 'purpose': 'new process or product design', 'design': 'design for Six Sigma', 'verification': 'design verification', 'prevention': 'defect prevention'}},
    "PDCA": {'description': 'Continuous improvement cycle methodology', 'annotations': {'cycle': 'Plan, Do, Check, Act', 'continuous': 'continuous improvement', 'iterative': 'iterative process', 'deming': 'Deming cycle', 'simple': 'simple and versatile'}},
    "KAIZEN": {'description': 'Japanese philosophy of continuous improvement', 'annotations': {'philosophy': 'continuous improvement philosophy', 'incremental': 'small incremental improvements', 'employee': 'employee-driven improvement', 'culture': 'improvement culture', 'daily': 'daily improvement activities'}},
    "LEAN_SIX_SIGMA": {'description': 'Combined methodology integrating Lean and Six Sigma', 'annotations': {'combination': 'Lean and Six Sigma integration', 'waste': 'waste elimination', 'variation': 'variation reduction', 'speed': 'speed and quality', 'comprehensive': 'comprehensive improvement'}},
    "FIVE_S": {'description': 'Workplace organization and standardization methodology', 'annotations': {'components': 'Sort, Set in Order, Shine, Standardize, Sustain', 'workplace': 'workplace organization', 'visual': 'visual management', 'foundation': 'improvement foundation', 'safety': 'safety and efficiency'}},
    "ROOT_CAUSE_ANALYSIS": {'description': 'Systematic approach to identifying problem root causes', 'annotations': {'systematic': 'systematic problem analysis', 'causes': 'root cause identification', 'prevention': 'problem prevention', 'tools': 'various analytical tools', 'thorough': 'thorough investigation'}},
    "STATISTICAL_PROCESS_CONTROL": {'description': 'Statistical methods for process monitoring and control', 'annotations': {'statistical': 'statistical monitoring', 'control_charts': 'control charts', 'variation': 'variation monitoring', 'prevention': 'problem prevention', 'real_time': 'real-time monitoring'}},
    "FAILURE_MODE_ANALYSIS": {'description': 'Systematic analysis of potential failure modes', 'annotations': {'analysis': 'failure mode analysis', 'prevention': 'failure prevention', 'risk': 'risk assessment', 'systematic': 'systematic approach', 'design': 'design and process FMEA'}},
    "BENCHMARKING": {'description': 'Performance comparison with best practices', 'annotations': {'comparison': 'performance comparison', 'best_practices': 'best practice identification', 'improvement': 'improvement opportunities', 'external': 'external benchmarking', 'internal': 'internal benchmarking'}},
}

class QualityControlTechniqueEnum(RichEnum):
    """
    Quality control techniques and tools
    """
    # Enum members
    CONTROL_CHARTS = "CONTROL_CHARTS"
    PARETO_ANALYSIS = "PARETO_ANALYSIS"
    FISHBONE_DIAGRAM = "FISHBONE_DIAGRAM"
    HISTOGRAM = "HISTOGRAM"
    SCATTER_DIAGRAM = "SCATTER_DIAGRAM"
    CHECK_SHEET = "CHECK_SHEET"
    FLOW_CHART = "FLOW_CHART"
    DESIGN_OF_EXPERIMENTS = "DESIGN_OF_EXPERIMENTS"
    SAMPLING_PLANS = "SAMPLING_PLANS"
    GAUGE_R_AND_R = "GAUGE_R_AND_R"

# Set metadata after class creation to avoid it becoming an enum member
QualityControlTechniqueEnum._metadata = {
    "CONTROL_CHARTS": {'description': 'Statistical charts for monitoring process variation', 'annotations': {'statistical': 'statistical process monitoring', 'variation': 'variation tracking', 'limits': 'control limits', 'trends': 'trend identification', 'real_time': 'real-time monitoring'}},
    "PARETO_ANALYSIS": {'description': '80/20 rule analysis for problem prioritization', 'annotations': {'prioritization': 'problem prioritization', 'rule': '80/20 rule', 'focus': 'focus on vital few', 'impact': 'impact analysis', 'resources': 'resource allocation'}},
    "FISHBONE_DIAGRAM": {'description': 'Cause-and-effect analysis diagram', 'annotations': {'cause_effect': 'cause and effect analysis', 'brainstorming': 'structured brainstorming', 'categories': 'cause categories', 'visual': 'visual analysis tool', 'team': 'team analysis tool'}},
    "HISTOGRAM": {'description': 'Frequency distribution chart for data analysis', 'annotations': {'distribution': 'data distribution', 'frequency': 'frequency analysis', 'patterns': 'pattern identification', 'visual': 'visual data representation', 'analysis': 'statistical analysis'}},
    "SCATTER_DIAGRAM": {'description': 'Correlation analysis between two variables', 'annotations': {'correlation': 'correlation analysis', 'relationship': 'variable relationship', 'pattern': 'pattern identification', 'statistical': 'statistical relationship', 'visual': 'visual correlation'}},
    "CHECK_SHEET": {'description': 'Data collection and recording tool', 'annotations': {'collection': 'data collection', 'recording': 'systematic recording', 'tracking': 'problem tracking', 'simple': 'simple data tool', 'standardized': 'standardized format'}},
    "FLOW_CHART": {'description': 'Process flow visualization and analysis', 'annotations': {'process': 'process visualization', 'flow': 'workflow analysis', 'steps': 'process steps', 'improvement': 'process improvement', 'understanding': 'process understanding'}},
    "DESIGN_OF_EXPERIMENTS": {'description': 'Statistical method for process optimization', 'annotations': {'statistical': 'statistical experimentation', 'optimization': 'process optimization', 'factors': 'factor analysis', 'interaction': 'interaction effects', 'efficiency': 'experimental efficiency'}},
    "SAMPLING_PLANS": {'description': 'Systematic approach to quality sampling', 'annotations': {'sampling': 'statistical sampling', 'plans': 'sampling plans', 'acceptance': 'acceptance sampling', 'risk': 'risk control', 'efficiency': 'sampling efficiency'}},
    "GAUGE_R_AND_R": {'description': 'Measurement system analysis technique', 'annotations': {'measurement': 'measurement system analysis', 'repeatability': 'measurement repeatability', 'reproducibility': 'measurement reproducibility', 'variation': 'measurement variation', 'capability': 'measurement capability'}},
}

class QualityAssuranceLevelEnum(RichEnum):
    """
    Levels of quality assurance implementation
    """
    # Enum members
    BASIC_QA = "BASIC_QA"
    INTERMEDIATE_QA = "INTERMEDIATE_QA"
    ADVANCED_QA = "ADVANCED_QA"
    WORLD_CLASS_QA = "WORLD_CLASS_QA"
    TOTAL_QUALITY = "TOTAL_QUALITY"

# Set metadata after class creation to avoid it becoming an enum member
QualityAssuranceLevelEnum._metadata = {
    "BASIC_QA": {'description': 'Fundamental quality assurance practices', 'annotations': {'level': 'basic implementation', 'practices': 'fundamental QA practices', 'inspection': 'inspection-based approach', 'reactive': 'reactive quality approach', 'compliance': 'basic compliance'}},
    "INTERMEDIATE_QA": {'description': 'Systematic quality assurance with documented processes', 'annotations': {'level': 'intermediate implementation', 'systematic': 'systematic approach', 'documentation': 'documented processes', 'prevention': 'some prevention focus', 'training': 'quality training programs'}},
    "ADVANCED_QA": {'description': 'Comprehensive quality management system', 'annotations': {'level': 'advanced implementation', 'comprehensive': 'comprehensive QMS', 'integration': 'integrated approach', 'prevention': 'prevention-focused', 'measurement': 'quality measurement systems'}},
    "WORLD_CLASS_QA": {'description': 'Excellence-oriented quality management', 'annotations': {'level': 'world-class implementation', 'excellence': 'quality excellence', 'innovation': 'quality innovation', 'leadership': 'quality leadership', 'benchmarking': 'best practice benchmarking'}},
    "TOTAL_QUALITY": {'description': 'Organization-wide quality culture and commitment', 'annotations': {'level': 'total quality implementation', 'culture': 'quality culture', 'organization_wide': 'entire organization', 'customer': 'customer-focused', 'continuous': 'continuous improvement'}},
}

class ProcessImprovementApproachEnum(RichEnum):
    """
    Process improvement methodologies and approaches
    """
    # Enum members
    BUSINESS_PROCESS_REENGINEERING = "BUSINESS_PROCESS_REENGINEERING"
    CONTINUOUS_IMPROVEMENT = "CONTINUOUS_IMPROVEMENT"
    PROCESS_STANDARDIZATION = "PROCESS_STANDARDIZATION"
    AUTOMATION = "AUTOMATION"
    DIGITALIZATION = "DIGITALIZATION"
    OUTSOURCING = "OUTSOURCING"
    SHARED_SERVICES = "SHARED_SERVICES"
    AGILE_PROCESS_IMPROVEMENT = "AGILE_PROCESS_IMPROVEMENT"

# Set metadata after class creation to avoid it becoming an enum member
ProcessImprovementApproachEnum._metadata = {
    "BUSINESS_PROCESS_REENGINEERING": {'description': 'Radical redesign of business processes', 'annotations': {'approach': 'radical process redesign', 'dramatic': 'dramatic improvement', 'technology': 'technology-enabled', 'fundamental': 'fundamental rethinking', 'breakthrough': 'breakthrough performance'}},
    "CONTINUOUS_IMPROVEMENT": {'description': 'Ongoing incremental process improvement', 'annotations': {'approach': 'incremental improvement', 'ongoing': 'continuous effort', 'culture': 'improvement culture', 'employee': 'employee involvement', 'sustainable': 'sustainable improvement'}},
    "PROCESS_STANDARDIZATION": {'description': 'Establishing consistent process standards', 'annotations': {'standardization': 'process standardization', 'consistency': 'consistent execution', 'documentation': 'process documentation', 'training': 'standard training', 'compliance': 'standard compliance'}},
    "AUTOMATION": {'description': 'Technology-driven process automation', 'annotations': {'technology': 'automation technology', 'efficiency': 'operational efficiency', 'consistency': 'consistent execution', 'cost': 'cost reduction', 'quality': 'quality improvement'}},
    "DIGITALIZATION": {'description': 'Digital technology-enabled process transformation', 'annotations': {'digital': 'digital transformation', 'technology': 'digital technology', 'data': 'data-driven processes', 'integration': 'system integration', 'innovation': 'digital innovation'}},
    "OUTSOURCING": {'description': 'External provider process management', 'annotations': {'external': 'external process management', 'specialization': 'specialized providers', 'cost': 'cost optimization', 'focus': 'core competency focus', 'expertise': 'external expertise'}},
    "SHARED_SERVICES": {'description': 'Centralized shared process delivery', 'annotations': {'centralization': 'centralized delivery', 'sharing': 'shared across units', 'efficiency': 'scale efficiency', 'standardization': 'service standardization', 'optimization': 'cost optimization'}},
    "AGILE_PROCESS_IMPROVEMENT": {'description': 'Flexible and iterative process improvement', 'annotations': {'agile': 'agile methodology', 'iterative': 'iterative improvement', 'flexible': 'flexible approach', 'responsive': 'responsive to change', 'collaboration': 'collaborative improvement'}},
}

class QualityMaturityLevelEnum(RichEnum):
    """
    Organizational quality maturity levels
    """
    # Enum members
    AD_HOC = "AD_HOC"
    DEFINED = "DEFINED"
    MANAGED = "MANAGED"
    OPTIMIZED = "OPTIMIZED"
    WORLD_CLASS = "WORLD_CLASS"

# Set metadata after class creation to avoid it becoming an enum member
QualityMaturityLevelEnum._metadata = {
    "AD_HOC": {'description': 'Informal and unstructured quality practices', 'annotations': {'maturity': 'initial maturity level', 'structure': 'unstructured approach', 'informal': 'informal practices', 'reactive': 'reactive quality', 'inconsistent': 'inconsistent results'}},
    "DEFINED": {'description': 'Documented and standardized quality processes', 'annotations': {'maturity': 'defined maturity level', 'documentation': 'documented processes', 'standardization': 'standardized approach', 'training': 'process training', 'consistency': 'consistent execution'}},
    "MANAGED": {'description': 'Measured and controlled quality management', 'annotations': {'maturity': 'managed maturity level', 'measurement': 'quality measurement', 'control': 'process control', 'monitoring': 'performance monitoring', 'improvement': 'targeted improvement'}},
    "OPTIMIZED": {'description': 'Continuously improving quality excellence', 'annotations': {'maturity': 'optimized maturity level', 'optimization': 'continuous optimization', 'innovation': 'quality innovation', 'excellence': 'quality excellence', 'benchmarking': 'best practice adoption'}},
    "WORLD_CLASS": {'description': 'Industry-leading quality performance and innovation', 'annotations': {'maturity': 'world-class maturity level', 'leadership': 'industry leadership', 'innovation': 'quality innovation', 'excellence': 'sustained excellence', 'recognition': 'external recognition'}},
}

class ProcurementTypeEnum(RichEnum):
    """
    Types of procurement activities and approaches
    """
    # Enum members
    DIRECT_PROCUREMENT = "DIRECT_PROCUREMENT"
    INDIRECT_PROCUREMENT = "INDIRECT_PROCUREMENT"
    SERVICES_PROCUREMENT = "SERVICES_PROCUREMENT"
    CAPITAL_PROCUREMENT = "CAPITAL_PROCUREMENT"
    STRATEGIC_PROCUREMENT = "STRATEGIC_PROCUREMENT"
    TACTICAL_PROCUREMENT = "TACTICAL_PROCUREMENT"
    EMERGENCY_PROCUREMENT = "EMERGENCY_PROCUREMENT"
    FRAMEWORK_PROCUREMENT = "FRAMEWORK_PROCUREMENT"
    E_PROCUREMENT = "E_PROCUREMENT"
    SUSTAINABLE_PROCUREMENT = "SUSTAINABLE_PROCUREMENT"

# Set metadata after class creation to avoid it becoming an enum member
ProcurementTypeEnum._metadata = {
    "DIRECT_PROCUREMENT": {'description': 'Procurement of materials directly used in production', 'annotations': {'category': 'direct materials', 'purpose': 'production input', 'impact': 'direct impact on product', 'examples': 'raw materials, components, subassemblies', 'strategic': 'strategically important'}},
    "INDIRECT_PROCUREMENT": {'description': 'Procurement of goods and services supporting operations', 'annotations': {'category': 'indirect materials and services', 'purpose': 'operational support', 'impact': 'indirect impact on product', 'examples': 'office supplies, maintenance, professional services', 'cost_focus': 'cost optimization focus'}},
    "SERVICES_PROCUREMENT": {'description': 'Procurement of professional and business services', 'annotations': {'category': 'services', 'intangible': 'intangible deliverables', 'examples': 'consulting, IT services, maintenance', 'relationship': 'relationship-based', 'management': 'service level management'}},
    "CAPITAL_PROCUREMENT": {'description': 'Procurement of capital equipment and assets', 'annotations': {'category': 'capital expenditure', 'long_term': 'long-term assets', 'high_value': 'high value purchases', 'examples': 'machinery, equipment, facilities', 'approval': 'capital approval process'}},
    "STRATEGIC_PROCUREMENT": {'description': 'Procurement of strategically important items', 'annotations': {'importance': 'strategic importance', 'risk': 'high business risk', 'value': 'high value impact', 'partnership': 'strategic partnerships', 'long_term': 'long-term relationships'}},
    "TACTICAL_PROCUREMENT": {'description': 'Routine procurement of standard items', 'annotations': {'routine': 'routine purchases', 'standard': 'standardized items', 'efficiency': 'efficiency focused', 'transactional': 'transactional approach', 'volume': 'volume-based'}},
    "EMERGENCY_PROCUREMENT": {'description': 'Urgent procurement due to immediate needs', 'annotations': {'urgency': 'urgent requirements', 'expedited': 'expedited process', 'higher_cost': 'potentially higher costs', 'risk_mitigation': 'business continuity', 'limited_sourcing': 'limited supplier options'}},
    "FRAMEWORK_PROCUREMENT": {'description': 'Pre-negotiated procurement agreements', 'annotations': {'agreement': 'pre-negotiated terms', 'efficiency': 'procurement efficiency', 'compliance': 'standardized compliance', 'multiple_suppliers': 'multiple approved suppliers', 'call_off': 'call-off contracts'}},
    "E_PROCUREMENT": {'description': 'Technology-enabled procurement processes', 'annotations': {'technology': 'electronic platforms', 'automation': 'process automation', 'efficiency': 'operational efficiency', 'transparency': 'process transparency', 'data': 'procurement data analytics'}},
    "SUSTAINABLE_PROCUREMENT": {'description': 'Environmentally and socially responsible procurement', 'annotations': {'sustainability': 'environmental and social criteria', 'responsibility': 'corporate responsibility', 'lifecycle': 'lifecycle considerations', 'certification': 'sustainability certifications', 'stakeholder': 'stakeholder value'}},
}

class VendorCategoryEnum(RichEnum):
    """
    Vendor classification categories
    """
    # Enum members
    STRATEGIC_SUPPLIER = "STRATEGIC_SUPPLIER"
    PREFERRED_SUPPLIER = "PREFERRED_SUPPLIER"
    APPROVED_SUPPLIER = "APPROVED_SUPPLIER"
    TRANSACTIONAL_SUPPLIER = "TRANSACTIONAL_SUPPLIER"
    SINGLE_SOURCE = "SINGLE_SOURCE"
    SOLE_SOURCE = "SOLE_SOURCE"
    MINORITY_SUPPLIER = "MINORITY_SUPPLIER"
    LOCAL_SUPPLIER = "LOCAL_SUPPLIER"
    GLOBAL_SUPPLIER = "GLOBAL_SUPPLIER"
    SPOT_SUPPLIER = "SPOT_SUPPLIER"

# Set metadata after class creation to avoid it becoming an enum member
VendorCategoryEnum._metadata = {
    "STRATEGIC_SUPPLIER": {'description': 'Critical suppliers with strategic importance', 'annotations': {'importance': 'strategic business importance', 'relationship': 'partnership relationship', 'risk': 'high business risk if disrupted', 'collaboration': 'collaborative planning', 'long_term': 'long-term agreements'}},
    "PREFERRED_SUPPLIER": {'description': 'Suppliers with proven performance and preferred status', 'annotations': {'performance': 'proven performance history', 'preferred': 'preferred supplier status', 'reliability': 'reliable delivery', 'quality': 'consistent quality', 'relationship': 'ongoing relationship'}},
    "APPROVED_SUPPLIER": {'description': 'Suppliers meeting qualification requirements', 'annotations': {'qualification': 'meets qualification criteria', 'approved': 'approved for business', 'standards': 'meets quality standards', 'compliance': 'regulatory compliance', 'monitoring': 'performance monitoring'}},
    "TRANSACTIONAL_SUPPLIER": {'description': 'Suppliers for routine, low-risk purchases', 'annotations': {'routine': 'routine transactions', 'low_risk': 'low business risk', 'standard': 'standard products/services', 'efficiency': 'cost and efficiency focus', 'limited_relationship': 'limited relationship'}},
    "SINGLE_SOURCE": {'description': 'Only available supplier for specific requirement', 'annotations': {'uniqueness': 'unique product or service', 'monopoly': 'single source situation', 'dependency': 'high dependency', 'risk': 'supply risk concentration', 'relationship': 'close relationship management'}},
    "SOLE_SOURCE": {'description': 'Deliberately chosen single supplier', 'annotations': {'choice': 'deliberate single supplier choice', 'partnership': 'strategic partnership', 'specialization': 'specialized capability', 'integration': 'integrated operations', 'exclusive': 'exclusive relationship'}},
    "MINORITY_SUPPLIER": {'description': 'Suppliers meeting diversity criteria', 'annotations': {'diversity': 'supplier diversity program', 'certification': 'diversity certification', 'inclusion': 'supplier inclusion', 'social_responsibility': 'corporate social responsibility', 'development': 'supplier development'}},
    "LOCAL_SUPPLIER": {'description': 'Geographically local suppliers', 'annotations': {'geography': 'local geographic proximity', 'community': 'local community support', 'logistics': 'reduced logistics costs', 'responsiveness': 'quick response capability', 'sustainability': 'reduced carbon footprint'}},
    "GLOBAL_SUPPLIER": {'description': 'Suppliers with global capabilities', 'annotations': {'global': 'global presence and capability', 'scale': 'economies of scale', 'standardization': 'global standardization', 'complexity': 'complex management', 'risk': 'global supply chain risk'}},
    "SPOT_SUPPLIER": {'description': 'Suppliers for one-time or spot purchases', 'annotations': {'spot_market': 'spot market transactions', 'one_time': 'one-time purchases', 'price_driven': 'price-driven selection', 'no_relationship': 'no ongoing relationship', 'market_based': 'market-based pricing'}},
}

class SupplyChainStrategyEnum(RichEnum):
    """
    Supply chain strategic approaches
    """
    # Enum members
    LEAN_SUPPLY_CHAIN = "LEAN_SUPPLY_CHAIN"
    AGILE_SUPPLY_CHAIN = "AGILE_SUPPLY_CHAIN"
    RESILIENT_SUPPLY_CHAIN = "RESILIENT_SUPPLY_CHAIN"
    SUSTAINABLE_SUPPLY_CHAIN = "SUSTAINABLE_SUPPLY_CHAIN"
    GLOBAL_SUPPLY_CHAIN = "GLOBAL_SUPPLY_CHAIN"
    LOCAL_SUPPLY_CHAIN = "LOCAL_SUPPLY_CHAIN"
    DIGITAL_SUPPLY_CHAIN = "DIGITAL_SUPPLY_CHAIN"
    COLLABORATIVE_SUPPLY_CHAIN = "COLLABORATIVE_SUPPLY_CHAIN"
    COST_FOCUSED_SUPPLY_CHAIN = "COST_FOCUSED_SUPPLY_CHAIN"
    CUSTOMER_FOCUSED_SUPPLY_CHAIN = "CUSTOMER_FOCUSED_SUPPLY_CHAIN"

# Set metadata after class creation to avoid it becoming an enum member
SupplyChainStrategyEnum._metadata = {
    "LEAN_SUPPLY_CHAIN": {'description': 'Waste elimination and efficiency-focused supply chain', 'annotations': {'philosophy': 'lean philosophy', 'waste': 'waste elimination', 'efficiency': 'operational efficiency', 'flow': 'smooth material flow', 'inventory': 'minimal inventory'}},
    "AGILE_SUPPLY_CHAIN": {'description': 'Flexible and responsive supply chain', 'annotations': {'flexibility': 'high flexibility', 'responsiveness': 'rapid response capability', 'adaptation': 'quick adaptation', 'variability': 'handles demand variability', 'customer': 'customer responsiveness'}},
    "RESILIENT_SUPPLY_CHAIN": {'description': 'Risk-resistant and robust supply chain', 'annotations': {'resilience': 'supply chain resilience', 'risk_management': 'comprehensive risk management', 'redundancy': 'built-in redundancy', 'recovery': 'quick recovery capability', 'continuity': 'business continuity focus'}},
    "SUSTAINABLE_SUPPLY_CHAIN": {'description': 'Environmentally and socially responsible supply chain', 'annotations': {'sustainability': 'environmental and social sustainability', 'responsibility': 'corporate responsibility', 'lifecycle': 'lifecycle assessment', 'circular': 'circular economy principles', 'stakeholder': 'stakeholder value'}},
    "GLOBAL_SUPPLY_CHAIN": {'description': 'Internationally distributed supply chain', 'annotations': {'global': 'global geographic distribution', 'scale': 'economies of scale', 'complexity': 'increased complexity', 'risk': 'global risks', 'coordination': 'global coordination'}},
    "LOCAL_SUPPLY_CHAIN": {'description': 'Geographically concentrated supply chain', 'annotations': {'local': 'local or regional focus', 'proximity': 'geographic proximity', 'responsiveness': 'local responsiveness', 'community': 'community support', 'sustainability': 'reduced transportation'}},
    "DIGITAL_SUPPLY_CHAIN": {'description': 'Technology-enabled and data-driven supply chain', 'annotations': {'digital': 'digital transformation', 'technology': 'advanced technology', 'data': 'data-driven decisions', 'automation': 'process automation', 'visibility': 'end-to-end visibility'}},
    "COLLABORATIVE_SUPPLY_CHAIN": {'description': 'Partnership-based collaborative supply chain', 'annotations': {'collaboration': 'supply chain collaboration', 'partnership': 'strategic partnerships', 'integration': 'process integration', 'sharing': 'information sharing', 'joint_planning': 'collaborative planning'}},
    "COST_FOCUSED_SUPPLY_CHAIN": {'description': 'Cost optimization-focused supply chain', 'annotations': {'cost': 'cost optimization', 'efficiency': 'cost efficiency', 'standardization': 'process standardization', 'scale': 'economies of scale', 'procurement': 'cost-focused procurement'}},
    "CUSTOMER_FOCUSED_SUPPLY_CHAIN": {'description': 'Customer service-oriented supply chain', 'annotations': {'customer': 'customer-centric', 'service': 'customer service focus', 'customization': 'product customization', 'responsiveness': 'customer responsiveness', 'satisfaction': 'customer satisfaction'}},
}

class LogisticsOperationEnum(RichEnum):
    """
    Types of logistics operations
    """
    # Enum members
    INBOUND_LOGISTICS = "INBOUND_LOGISTICS"
    OUTBOUND_LOGISTICS = "OUTBOUND_LOGISTICS"
    REVERSE_LOGISTICS = "REVERSE_LOGISTICS"
    THIRD_PARTY_LOGISTICS = "THIRD_PARTY_LOGISTICS"
    FOURTH_PARTY_LOGISTICS = "FOURTH_PARTY_LOGISTICS"
    WAREHOUSING = "WAREHOUSING"
    TRANSPORTATION = "TRANSPORTATION"
    CROSS_DOCKING = "CROSS_DOCKING"
    DISTRIBUTION = "DISTRIBUTION"
    FREIGHT_FORWARDING = "FREIGHT_FORWARDING"

# Set metadata after class creation to avoid it becoming an enum member
LogisticsOperationEnum._metadata = {
    "INBOUND_LOGISTICS": {'description': 'Management of incoming materials and supplies', 'annotations': {'direction': 'inbound to organization', 'materials': 'raw materials and supplies', 'suppliers': 'supplier coordination', 'receiving': 'receiving operations', 'quality': 'incoming quality control'}},
    "OUTBOUND_LOGISTICS": {'description': 'Management of finished goods distribution', 'annotations': {'direction': 'outbound from organization', 'products': 'finished goods', 'customers': 'customer delivery', 'distribution': 'distribution management', 'service': 'customer service'}},
    "REVERSE_LOGISTICS": {'description': 'Management of product returns and recycling', 'annotations': {'direction': 'reverse flow', 'returns': 'product returns', 'recycling': 'recycling and disposal', 'recovery': 'value recovery', 'sustainability': 'environmental responsibility'}},
    "THIRD_PARTY_LOGISTICS": {'description': 'Outsourced logistics services', 'annotations': {'outsourcing': 'logistics outsourcing', 'service_provider': 'third-party provider', 'specialization': 'logistics specialization', 'cost': 'cost optimization', 'expertise': 'logistics expertise'}},
    "FOURTH_PARTY_LOGISTICS": {'description': 'Supply chain integration and management services', 'annotations': {'integration': 'supply chain integration', 'management': 'end-to-end management', 'coordination': 'multi-provider coordination', 'strategy': 'strategic logistics', 'technology': 'technology integration'}},
    "WAREHOUSING": {'description': 'Storage and inventory management operations', 'annotations': {'storage': 'product storage', 'inventory': 'inventory management', 'handling': 'material handling', 'distribution': 'distribution center', 'automation': 'warehouse automation'}},
    "TRANSPORTATION": {'description': 'Movement of goods between locations', 'annotations': {'movement': 'goods movement', 'modes': 'transportation modes', 'routing': 'route optimization', 'scheduling': 'delivery scheduling', 'cost': 'transportation cost'}},
    "CROSS_DOCKING": {'description': 'Direct transfer without storage', 'annotations': {'transfer': 'direct transfer', 'minimal_storage': 'minimal inventory storage', 'efficiency': 'operational efficiency', 'speed': 'fast throughput', 'consolidation': 'shipment consolidation'}},
    "DISTRIBUTION": {'description': 'Product distribution and delivery operations', 'annotations': {'distribution': 'product distribution', 'network': 'distribution network', 'delivery': 'customer delivery', 'service': 'delivery service', 'coverage': 'market coverage'}},
    "FREIGHT_FORWARDING": {'description': 'International shipping and customs management', 'annotations': {'international': 'international shipping', 'customs': 'customs clearance', 'documentation': 'shipping documentation', 'coordination': 'multi-modal coordination', 'compliance': 'regulatory compliance'}},
}

class SourcingStrategyEnum(RichEnum):
    """
    Sourcing strategy approaches
    """
    # Enum members
    SINGLE_SOURCING = "SINGLE_SOURCING"
    MULTIPLE_SOURCING = "MULTIPLE_SOURCING"
    DUAL_SOURCING = "DUAL_SOURCING"
    GLOBAL_SOURCING = "GLOBAL_SOURCING"
    DOMESTIC_SOURCING = "DOMESTIC_SOURCING"
    NEAR_SOURCING = "NEAR_SOURCING"
    VERTICAL_INTEGRATION = "VERTICAL_INTEGRATION"
    OUTSOURCING = "OUTSOURCING"
    INSOURCING = "INSOURCING"
    CONSORTIUM_SOURCING = "CONSORTIUM_SOURCING"

# Set metadata after class creation to avoid it becoming an enum member
SourcingStrategyEnum._metadata = {
    "SINGLE_SOURCING": {'description': 'Deliberate use of one supplier for strategic reasons', 'annotations': {'suppliers': 'single supplier', 'strategic': 'strategic decision', 'partnership': 'close partnership', 'risk': 'supply concentration risk', 'benefits': 'economies of scale'}},
    "MULTIPLE_SOURCING": {'description': 'Use of multiple suppliers for risk mitigation', 'annotations': {'suppliers': 'multiple suppliers', 'risk_mitigation': 'supply risk mitigation', 'competition': 'supplier competition', 'flexibility': 'sourcing flexibility', 'management': 'complex supplier management'}},
    "DUAL_SOURCING": {'description': 'Use of two suppliers for balance of risk and efficiency', 'annotations': {'suppliers': 'two suppliers', 'balance': 'risk and efficiency balance', 'backup': 'backup supply capability', 'competition': 'limited competition', 'management': 'manageable complexity'}},
    "GLOBAL_SOURCING": {'description': 'Worldwide sourcing for best value', 'annotations': {'geographic': 'global geographic scope', 'cost': 'cost optimization', 'capability': 'access to capabilities', 'complexity': 'increased complexity', 'risk': 'global supply risks'}},
    "DOMESTIC_SOURCING": {'description': 'Sourcing within domestic market', 'annotations': {'geographic': 'domestic market only', 'proximity': 'geographic proximity', 'responsiveness': 'local responsiveness', 'compliance': 'regulatory compliance', 'support': 'domestic economy support'}},
    "NEAR_SOURCING": {'description': 'Sourcing from nearby geographic regions', 'annotations': {'geographic': 'nearby regions', 'balance': 'cost and proximity balance', 'risk': 'reduced supply chain risk', 'responsiveness': 'improved responsiveness', 'cost': 'moderate cost advantage'}},
    "VERTICAL_INTEGRATION": {'description': 'Internal production instead of external sourcing', 'annotations': {'internal': 'internal production', 'control': 'direct control', 'capability': 'internal capability development', 'investment': 'significant investment', 'flexibility': 'reduced flexibility'}},
    "OUTSOURCING": {'description': 'External sourcing of non-core activities', 'annotations': {'external': 'external providers', 'focus': 'core competency focus', 'cost': 'cost optimization', 'expertise': 'access to expertise', 'dependency': 'external dependency'}},
    "INSOURCING": {'description': 'Bringing previously outsourced activities internal', 'annotations': {'internal': 'bring activities internal', 'control': 'increased control', 'capability': 'internal capability building', 'cost': 'potential cost increase', 'strategic': 'strategic importance'}},
    "CONSORTIUM_SOURCING": {'description': 'Collaborative sourcing with other organizations', 'annotations': {'collaboration': 'multi-organization collaboration', 'leverage': 'increased buying leverage', 'cost': 'cost reduction through scale', 'complexity': 'coordination complexity', 'relationships': 'multi-party relationships'}},
}

class SupplierRelationshipTypeEnum(RichEnum):
    """
    Types of supplier relationship management
    """
    # Enum members
    TRANSACTIONAL = "TRANSACTIONAL"
    PREFERRED_SUPPLIER = "PREFERRED_SUPPLIER"
    STRATEGIC_PARTNERSHIP = "STRATEGIC_PARTNERSHIP"
    ALLIANCE = "ALLIANCE"
    JOINT_VENTURE = "JOINT_VENTURE"
    VENDOR_MANAGED_INVENTORY = "VENDOR_MANAGED_INVENTORY"
    CONSIGNMENT = "CONSIGNMENT"
    COLLABORATIVE_PLANNING = "COLLABORATIVE_PLANNING"
    DEVELOPMENT_PARTNERSHIP = "DEVELOPMENT_PARTNERSHIP"
    RISK_SHARING = "RISK_SHARING"

# Set metadata after class creation to avoid it becoming an enum member
SupplierRelationshipTypeEnum._metadata = {
    "TRANSACTIONAL": {'description': 'Arms-length, price-focused supplier relationship', 'annotations': {'focus': 'price and terms focus', 'interaction': 'minimal interaction', 'duration': 'short-term orientation', 'switching': 'easy supplier switching', 'competition': 'competitive bidding'}},
    "PREFERRED_SUPPLIER": {'description': 'Ongoing relationship with proven suppliers', 'annotations': {'status': 'preferred supplier status', 'performance': 'proven performance', 'priority': 'priority consideration', 'benefits': 'preferential treatment', 'stability': 'stable relationship'}},
    "STRATEGIC_PARTNERSHIP": {'description': 'Collaborative long-term strategic relationship', 'annotations': {'collaboration': 'strategic collaboration', 'integration': 'business integration', 'planning': 'joint planning', 'development': 'joint development', 'mutual_benefit': 'mutual value creation'}},
    "ALLIANCE": {'description': 'Formal alliance with shared objectives', 'annotations': {'formal': 'formal alliance agreement', 'objectives': 'shared strategic objectives', 'resources': 'shared resources', 'risks': 'shared risks and rewards', 'governance': 'joint governance'}},
    "JOINT_VENTURE": {'description': 'Separate entity created with supplier', 'annotations': {'entity': 'separate legal entity', 'ownership': 'shared ownership', 'investment': 'joint investment', 'control': 'shared control', 'separate': 'separate business unit'}},
    "VENDOR_MANAGED_INVENTORY": {'description': 'Supplier manages customer inventory', 'annotations': {'management': 'supplier manages inventory', 'visibility': 'demand visibility', 'responsibility': 'supplier responsibility', 'efficiency': 'inventory efficiency', 'integration': 'systems integration'}},
    "CONSIGNMENT": {'description': 'Supplier owns inventory until consumption', 'annotations': {'ownership': 'supplier retains ownership', 'location': 'customer location', 'payment': 'payment on consumption', 'cash_flow': 'improved customer cash flow', 'risk': 'supplier inventory risk'}},
    "COLLABORATIVE_PLANNING": {'description': 'Joint planning and forecasting relationship', 'annotations': {'planning': 'collaborative planning', 'forecasting': 'joint forecasting', 'information': 'information sharing', 'coordination': 'demand coordination', 'efficiency': 'supply chain efficiency'}},
    "DEVELOPMENT_PARTNERSHIP": {'description': 'Investment in supplier capability development', 'annotations': {'development': 'supplier capability development', 'investment': 'customer investment', 'improvement': 'supplier improvement', 'capability': 'capability building', 'long_term': 'long-term commitment'}},
    "RISK_SHARING": {'description': 'Shared risk and reward relationship', 'annotations': {'risk': 'shared risk and reward', 'incentives': 'aligned incentives', 'performance': 'performance-based', 'outcomes': 'shared outcomes', 'collaboration': 'collaborative approach'}},
}

class InventoryManagementApproachEnum(RichEnum):
    """
    Inventory management methodologies
    """
    # Enum members
    JUST_IN_TIME = "JUST_IN_TIME"
    ECONOMIC_ORDER_QUANTITY = "ECONOMIC_ORDER_QUANTITY"
    ABC_ANALYSIS = "ABC_ANALYSIS"
    SAFETY_STOCK = "SAFETY_STOCK"
    VENDOR_MANAGED_INVENTORY = "VENDOR_MANAGED_INVENTORY"
    CONSIGNMENT_INVENTORY = "CONSIGNMENT_INVENTORY"
    KANBAN = "KANBAN"
    TWO_BIN_SYSTEM = "TWO_BIN_SYSTEM"
    CONTINUOUS_REVIEW = "CONTINUOUS_REVIEW"
    PERIODIC_REVIEW = "PERIODIC_REVIEW"

# Set metadata after class creation to avoid it becoming an enum member
InventoryManagementApproachEnum._metadata = {
    "JUST_IN_TIME": {'description': 'Minimal inventory with precise timing', 'annotations': {'timing': 'precise delivery timing', 'waste': 'inventory waste elimination', 'flow': 'continuous flow', 'supplier': 'supplier integration', 'quality': 'zero defect requirement'}},
    "ECONOMIC_ORDER_QUANTITY": {'description': 'Optimal order quantity calculation', 'annotations': {'optimization': 'cost optimization', 'calculation': 'mathematical calculation', 'trade_off': 'ordering vs holding cost trade-off', 'static': 'static demand assumption', 'classical': 'classical inventory model'}},
    "ABC_ANALYSIS": {'description': 'Inventory classification by value importance', 'annotations': {'classification': 'value-based classification', 'focus': 'priority focus on high-value items', 'management': 'differentiated management', 'efficiency': 'resource allocation efficiency', 'pareto': 'Pareto principle application'}},
    "SAFETY_STOCK": {'description': 'Buffer inventory for demand/supply uncertainty', 'annotations': {'buffer': 'inventory buffer', 'uncertainty': 'demand and supply uncertainty', 'service_level': 'service level protection', 'cost': 'additional holding cost', 'risk': 'stockout risk mitigation'}},
    "VENDOR_MANAGED_INVENTORY": {'description': 'Supplier-controlled inventory management', 'annotations': {'control': 'supplier inventory control', 'visibility': 'demand visibility', 'automation': 'automated replenishment', 'efficiency': 'inventory efficiency', 'partnership': 'supplier partnership'}},
    "CONSIGNMENT_INVENTORY": {'description': 'Supplier-owned inventory at customer location', 'annotations': {'ownership': 'supplier ownership', 'location': 'customer location', 'cash_flow': 'improved cash flow', 'availability': 'immediate availability', 'risk': 'supplier risk'}},
    "KANBAN": {'description': 'Visual pull-based inventory system', 'annotations': {'visual': 'visual control system', 'pull': 'pull-based replenishment', 'lean': 'lean methodology', 'signals': 'kanban signals', 'flow': 'smooth material flow'}},
    "TWO_BIN_SYSTEM": {'description': 'Simple reorder point system using two bins', 'annotations': {'simplicity': 'simple reorder system', 'visual': 'visual reorder point', 'bins': 'two-bin methodology', 'automatic': 'automatic reordering', 'low_cost': 'low-cost implementation'}},
    "CONTINUOUS_REVIEW": {'description': 'Continuous monitoring with fixed reorder point', 'annotations': {'monitoring': 'continuous inventory monitoring', 'reorder_point': 'fixed reorder point', 'quantity': 'fixed order quantity', 'responsiveness': 'responsive to demand', 'cost': 'higher monitoring cost'}},
    "PERIODIC_REVIEW": {'description': 'Periodic inventory review with variable order quantity', 'annotations': {'periodic': 'periodic review intervals', 'variable': 'variable order quantity', 'target': 'target inventory level', 'aggregation': 'order aggregation', 'efficiency': 'administrative efficiency'}},
}

class EmploymentTypeEnum(RichEnum):
    """
    Types of employment arrangements and contracts
    """
    # Enum members
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    FREELANCE = "FREELANCE"
    INTERN = "INTERN"
    SEASONAL = "SEASONAL"
    CONSULTANT = "CONSULTANT"
    VOLUNTEER = "VOLUNTEER"

# Set metadata after class creation to avoid it becoming an enum member
EmploymentTypeEnum._metadata = {
    "FULL_TIME": {'description': 'Regular full-time employment status', 'annotations': {'hours': 'typically 40 hours per week', 'benefits': 'full benefits package', 'classification': 'exempt or non-exempt', 'stability': 'permanent position', 'commitment': 'full organizational commitment'}},
    "PART_TIME": {'description': 'Regular part-time employment status', 'annotations': {'hours': 'less than full-time hours', 'benefits': 'limited or prorated benefits', 'flexibility': 'flexible scheduling', 'classification': 'typically non-exempt', 'commitment': 'ongoing but reduced hours'}},
    "CONTRACT": {'description': 'Fixed-term contractual employment', 'annotations': {'duration': 'defined contract period', 'relationship': 'contractual relationship', 'benefits': 'limited benefits', 'termination': 'defined end date', 'purpose': 'specific project or duration'}},
    "TEMPORARY": {'description': 'Short-term temporary employment', 'annotations': {'duration': 'short-term assignment', 'agency': 'often through staffing agency', 'benefits': 'minimal benefits', 'purpose': 'seasonal or project work', 'flexibility': 'high flexibility'}},
    "FREELANCE": {'description': 'Independent contractor or freelance work', 'annotations': {'relationship': 'independent contractor', 'benefits': 'no traditional benefits', 'control': 'high work autonomy', 'taxes': 'responsible for own taxes', 'projects': 'project-based work'}},
    "INTERN": {'description': 'Student or entry-level internship program', 'annotations': {'purpose': 'learning and experience', 'duration': 'limited duration', 'compensation': 'may be paid or unpaid', 'education': 'educational component', 'supervision': 'mentorship and guidance'}},
    "SEASONAL": {'description': 'Employment tied to seasonal business needs', 'annotations': {'pattern': 'recurring seasonal pattern', 'duration': 'specific seasons', 'industry': 'retail, agriculture, tourism', 'return': 'potential for seasonal return', 'benefits': 'limited benefits'}},
    "CONSULTANT": {'description': 'Professional consulting services', 'annotations': {'expertise': 'specialized expertise', 'relationship': 'advisory relationship', 'independence': 'independent professional', 'project': 'project or retainer basis', 'value': 'strategic value-add'}},
    "VOLUNTEER": {'description': 'Unpaid volunteer service', 'annotations': {'compensation': 'unpaid service', 'motivation': 'altruistic motivation', 'commitment': 'voluntary commitment', 'purpose': 'mission-driven work', 'recognition': 'non-monetary recognition'}},
}

class JobLevelEnum(RichEnum):
    """
    Organizational job levels and career progression
    """
    # Enum members
    ENTRY_LEVEL = "ENTRY_LEVEL"
    JUNIOR = "JUNIOR"
    MID_LEVEL = "MID_LEVEL"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
    MANAGER = "MANAGER"
    DIRECTOR = "DIRECTOR"
    VP = "VP"
    C_LEVEL = "C_LEVEL"

# Set metadata after class creation to avoid it becoming an enum member
JobLevelEnum._metadata = {
    "ENTRY_LEVEL": {'description': 'Beginning career level positions', 'annotations': {'experience': '0-2 years experience', 'responsibilities': 'basic operational tasks', 'supervision': 'high supervision required', 'development': 'learning and development focus', 'career_stage': 'career beginning'}},
    "JUNIOR": {'description': 'Junior professional level', 'annotations': {'experience': '2-4 years experience', 'responsibilities': 'routine professional tasks', 'independence': 'some independence', 'mentorship': 'receiving mentorship', 'skill_building': 'skill development phase'}},
    "MID_LEVEL": {'description': 'Experienced professional level', 'annotations': {'experience': '4-8 years experience', 'responsibilities': 'complex project work', 'independence': 'high independence', 'mentorship': 'providing and receiving mentorship', 'expertise': 'developing expertise'}},
    "SENIOR": {'description': 'Senior professional level', 'annotations': {'experience': '8+ years experience', 'responsibilities': 'strategic project leadership', 'expertise': 'subject matter expertise', 'mentorship': 'mentoring others', 'influence': 'organizational influence'}},
    "LEAD": {'description': 'Team leadership role', 'annotations': {'responsibility': 'team leadership', 'people_management': 'direct reports', 'coordination': 'team coordination', 'accountability': 'team results', 'development': 'team development'}},
    "MANAGER": {'description': 'Management level position', 'annotations': {'scope': 'departmental management', 'people_management': 'multiple direct reports', 'budget': 'budget responsibility', 'strategy': 'tactical strategy', 'operations': 'operational management'}},
    "DIRECTOR": {'description': 'Director level executive', 'annotations': {'scope': 'multi-departmental oversight', 'strategy': 'strategic planning', 'leadership': 'organizational leadership', 'stakeholders': 'senior stakeholder management', 'results': 'business results accountability'}},
    "VP": {'description': 'Vice President executive level', 'annotations': {'scope': 'business unit or functional area', 'strategy': 'strategic leadership', 'board': 'board interaction', 'organization': 'organizational impact', 'succession': 'succession planning'}},
    "C_LEVEL": {'description': 'Chief executive level', 'annotations': {'scope': 'enterprise-wide responsibility', 'governance': 'corporate governance', 'vision': 'organizational vision', 'stakeholders': 'external stakeholder management', 'fiduciary': 'fiduciary responsibility'}},
}

class HRFunctionEnum(RichEnum):
    """
    Human resources functional areas and specializations
    """
    # Enum members
    TALENT_ACQUISITION = "TALENT_ACQUISITION"
    EMPLOYEE_RELATIONS = "EMPLOYEE_RELATIONS"
    COMPENSATION_BENEFITS = "COMPENSATION_BENEFITS"
    PERFORMANCE_MANAGEMENT = "PERFORMANCE_MANAGEMENT"
    LEARNING_DEVELOPMENT = "LEARNING_DEVELOPMENT"
    HR_ANALYTICS = "HR_ANALYTICS"
    ORGANIZATIONAL_DEVELOPMENT = "ORGANIZATIONAL_DEVELOPMENT"
    HR_COMPLIANCE = "HR_COMPLIANCE"
    HRIS_TECHNOLOGY = "HRIS_TECHNOLOGY"

# Set metadata after class creation to avoid it becoming an enum member
HRFunctionEnum._metadata = {
    "TALENT_ACQUISITION": {'description': 'Recruitment and hiring functions', 'annotations': {'activities': 'sourcing, screening, interviewing, hiring', 'focus': 'attracting and selecting talent', 'metrics': 'time to hire, quality of hire', 'strategy': 'workforce planning', 'technology': 'ATS and recruitment tools'}},
    "EMPLOYEE_RELATIONS": {'description': 'Managing employee relationships and workplace issues', 'annotations': {'activities': 'conflict resolution, grievance handling', 'focus': 'positive employee relations', 'communication': 'employee communication', 'culture': 'workplace culture', 'mediation': 'dispute resolution'}},
    "COMPENSATION_BENEFITS": {'description': 'Managing compensation and benefits programs', 'annotations': {'activities': 'salary administration, benefits design', 'analysis': 'market analysis and benchmarking', 'compliance': 'regulatory compliance', 'cost': 'cost management', 'competitiveness': 'market competitiveness'}},
    "PERFORMANCE_MANAGEMENT": {'description': 'Employee performance evaluation and improvement', 'annotations': {'activities': 'performance reviews, goal setting', 'development': 'performance improvement', 'measurement': 'performance metrics', 'feedback': 'continuous feedback', 'coaching': 'performance coaching'}},
    "LEARNING_DEVELOPMENT": {'description': 'Employee training and development programs', 'annotations': {'activities': 'training design, skill development', 'career': 'career development', 'leadership': 'leadership development', 'compliance': 'compliance training', 'technology': 'learning management systems'}},
    "HR_ANALYTICS": {'description': 'HR data analysis and workforce metrics', 'annotations': {'activities': 'data analysis, metrics reporting', 'insights': 'workforce insights', 'predictive': 'predictive analytics', 'dashboard': 'HR dashboards', 'decision_support': 'data-driven decisions'}},
    "ORGANIZATIONAL_DEVELOPMENT": {'description': 'Organizational design and change management', 'annotations': {'activities': 'change management, culture transformation', 'design': 'organizational design', 'effectiveness': 'organizational effectiveness', 'culture': 'culture development', 'transformation': 'business transformation'}},
    "HR_COMPLIANCE": {'description': 'Employment law compliance and risk management', 'annotations': {'activities': 'policy development, compliance monitoring', 'legal': 'employment law compliance', 'risk': 'HR risk management', 'auditing': 'compliance auditing', 'documentation': 'record keeping'}},
    "HRIS_TECHNOLOGY": {'description': 'HR information systems and technology', 'annotations': {'activities': 'system administration, data management', 'systems': 'HRIS implementation', 'automation': 'process automation', 'integration': 'system integration', 'security': 'data security'}},
}

class CompensationTypeEnum(RichEnum):
    """
    Types of employee compensation structures
    """
    # Enum members
    BASE_SALARY = "BASE_SALARY"
    HOURLY_WAGE = "HOURLY_WAGE"
    COMMISSION = "COMMISSION"
    BONUS = "BONUS"
    STOCK_OPTIONS = "STOCK_OPTIONS"
    PROFIT_SHARING = "PROFIT_SHARING"
    PIECE_RATE = "PIECE_RATE"
    STIPEND = "STIPEND"

# Set metadata after class creation to avoid it becoming an enum member
CompensationTypeEnum._metadata = {
    "BASE_SALARY": {'description': 'Fixed annual salary compensation', 'annotations': {'structure': 'fixed annual amount', 'payment': 'regular pay periods', 'exemption': 'often exempt from overtime', 'predictability': 'predictable income', 'market': 'market benchmarked'}},
    "HOURLY_WAGE": {'description': 'Compensation paid per hour worked', 'annotations': {'structure': 'rate per hour', 'overtime': 'overtime eligible', 'tracking': 'time tracking required', 'variability': 'variable based on hours', 'classification': 'non-exempt employees'}},
    "COMMISSION": {'description': 'Performance-based sales commission', 'annotations': {'structure': 'percentage of sales', 'performance': 'performance-based', 'variability': 'highly variable', 'motivation': 'sales motivation', 'risk': 'income risk'}},
    "BONUS": {'description': 'Additional compensation for performance', 'annotations': {'timing': 'annual or periodic', 'criteria': 'performance criteria', 'discretionary': 'may be discretionary', 'recognition': 'performance recognition', 'retention': 'retention tool'}},
    "STOCK_OPTIONS": {'description': 'Equity compensation through stock options', 'annotations': {'equity': 'equity participation', 'vesting': 'vesting schedule', 'retention': 'long-term retention', 'upside': 'company growth upside', 'risk': 'market risk'}},
    "PROFIT_SHARING": {'description': 'Sharing of company profits with employees', 'annotations': {'structure': 'percentage of profits', 'performance': 'company performance based', 'culture': 'ownership culture', 'variability': 'variable based on profits', 'alignment': 'interest alignment'}},
    "PIECE_RATE": {'description': 'Compensation based on units produced', 'annotations': {'structure': 'rate per unit produced', 'productivity': 'productivity-based', 'manufacturing': 'common in manufacturing', 'measurement': 'output measurement', 'efficiency': 'efficiency incentive'}},
    "STIPEND": {'description': 'Fixed regular allowance or payment', 'annotations': {'purpose': 'specific purpose payment', 'amount': 'modest fixed amount', 'regularity': 'regular payment', 'supplemental': 'supplemental income', 'categories': 'interns, volunteers, board members'}},
}

class PerformanceRatingEnum(RichEnum):
    """
    Employee performance evaluation ratings
    """
    # Enum members
    EXCEEDS_EXPECTATIONS = "EXCEEDS_EXPECTATIONS"
    MEETS_EXPECTATIONS = "MEETS_EXPECTATIONS"
    PARTIALLY_MEETS = "PARTIALLY_MEETS"
    DOES_NOT_MEET = "DOES_NOT_MEET"
    OUTSTANDING = "OUTSTANDING"

# Set metadata after class creation to avoid it becoming an enum member
PerformanceRatingEnum._metadata = {
    "EXCEEDS_EXPECTATIONS": {'description': 'Performance significantly above expected standards', 'annotations': {'level': 'top performance tier', 'impact': 'significant business impact', 'recognition': 'high recognition', 'development': 'stretch assignments', 'percentage': 'typically 10-20% of population'}},
    "MEETS_EXPECTATIONS": {'description': 'Performance meets all expected standards', 'annotations': {'level': 'satisfactory performance', 'standards': 'meets all job requirements', 'competency': 'demonstrates required competencies', 'consistency': 'consistent performance', 'percentage': 'typically 60-70% of population'}},
    "PARTIALLY_MEETS": {'description': 'Performance meets some but not all standards', 'annotations': {'level': 'below standard performance', 'improvement': 'improvement needed', 'support': 'additional support required', 'development': 'focused development plan', 'percentage': 'typically 10-15% of population'}},
    "DOES_NOT_MEET": {'description': 'Performance below acceptable standards', 'annotations': {'level': 'unsatisfactory performance', 'action': 'performance improvement plan', 'timeline': 'improvement timeline', 'consequences': 'potential consequences', 'percentage': 'typically 5-10% of population'}},
    "OUTSTANDING": {'description': 'Exceptional performance far exceeding standards', 'annotations': {'level': 'exceptional performance', 'impact': 'transformational impact', 'leadership': 'demonstrates leadership', 'innovation': 'innovation and excellence', 'rarity': 'rare rating'}},
}

class RecruitmentSourceEnum(RichEnum):
    """
    Sources for candidate recruitment and sourcing
    """
    # Enum members
    INTERNAL_REFERRAL = "INTERNAL_REFERRAL"
    JOB_BOARDS = "JOB_BOARDS"
    COMPANY_WEBSITE = "COMPANY_WEBSITE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    RECRUITMENT_AGENCIES = "RECRUITMENT_AGENCIES"
    CAMPUS_RECRUITING = "CAMPUS_RECRUITING"
    PROFESSIONAL_NETWORKS = "PROFESSIONAL_NETWORKS"
    HEADHUNTERS = "HEADHUNTERS"

# Set metadata after class creation to avoid it becoming an enum member
RecruitmentSourceEnum._metadata = {
    "INTERNAL_REFERRAL": {'description': 'Candidates referred by current employees', 'annotations': {'source': 'employee networks', 'quality': 'typically high quality', 'cost': 'low cost per hire', 'cultural_fit': 'good cultural fit', 'retention': 'higher retention rates'}},
    "JOB_BOARDS": {'description': 'Candidates from online job posting sites', 'annotations': {'reach': 'broad candidate reach', 'cost': 'moderate cost', 'volume': 'high application volume', 'screening': 'requires screening', 'examples': 'Indeed, LinkedIn, Monster'}},
    "COMPANY_WEBSITE": {'description': 'Candidates applying through company website', 'annotations': {'interest': 'high company interest', 'brand': 'employer brand driven', 'quality': 'targeted candidates', 'direct': 'direct application', 'cost': 'low incremental cost'}},
    "SOCIAL_MEDIA": {'description': 'Candidates sourced through social media platforms', 'annotations': {'platforms': 'LinkedIn, Facebook, Twitter', 'active': 'active sourcing', 'networking': 'professional networking', 'targeting': 'targeted approach', 'engagement': 'relationship building'}},
    "RECRUITMENT_AGENCIES": {'description': 'Candidates sourced through recruitment firms', 'annotations': {'expertise': 'specialized expertise', 'cost': 'higher cost', 'speed': 'faster time to hire', 'screening': 'pre-screened candidates', 'specialization': 'industry specialization'}},
    "CAMPUS_RECRUITING": {'description': 'Recruitment from educational institutions', 'annotations': {'target': 'students and new graduates', 'programs': 'internship and graduate programs', 'relationships': 'university relationships', 'pipeline': 'talent pipeline', 'early_career': 'early career focus'}},
    "PROFESSIONAL_NETWORKS": {'description': 'Recruitment through professional associations', 'annotations': {'industry': 'industry-specific networks', 'expertise': 'specialized expertise', 'relationships': 'professional relationships', 'credibility': 'professional credibility', 'targeted': 'targeted recruitment'}},
    "HEADHUNTERS": {'description': 'Executive-level recruitment specialists', 'annotations': {'level': 'senior and executive roles', 'expertise': 'specialized search expertise', 'network': 'extensive professional networks', 'confidential': 'confidential searches', 'cost': 'premium cost'}},
}

class TrainingTypeEnum(RichEnum):
    """
    Types of employee training and development programs
    """
    # Enum members
    ONBOARDING = "ONBOARDING"
    TECHNICAL_SKILLS = "TECHNICAL_SKILLS"
    LEADERSHIP_DEVELOPMENT = "LEADERSHIP_DEVELOPMENT"
    COMPLIANCE_TRAINING = "COMPLIANCE_TRAINING"
    SOFT_SKILLS = "SOFT_SKILLS"
    SAFETY_TRAINING = "SAFETY_TRAINING"
    DIVERSITY_INCLUSION = "DIVERSITY_INCLUSION"
    CROSS_TRAINING = "CROSS_TRAINING"

# Set metadata after class creation to avoid it becoming an enum member
TrainingTypeEnum._metadata = {
    "ONBOARDING": {'description': 'Orientation and integration training for new hires', 'annotations': {'timing': 'first days/weeks of employment', 'purpose': 'integration and orientation', 'content': 'company culture, policies, role basics', 'delivery': 'structured program', 'outcome': 'successful integration'}},
    "TECHNICAL_SKILLS": {'description': 'Job-specific technical competency development', 'annotations': {'focus': 'technical competencies', 'relevance': 'job-specific skills', 'methods': 'hands-on training', 'certification': 'may include certification', 'updating': 'continuous skill updates'}},
    "LEADERSHIP_DEVELOPMENT": {'description': 'Management and leadership capability building', 'annotations': {'target': 'managers and high-potential employees', 'skills': 'leadership and management skills', 'development': 'long-term development', 'mentorship': 'coaching and mentorship', 'succession': 'succession planning'}},
    "COMPLIANCE_TRAINING": {'description': 'Required training for regulatory compliance', 'annotations': {'requirement': 'mandatory training', 'regulation': 'regulatory compliance', 'documentation': 'completion tracking', 'frequency': 'periodic updates', 'risk': 'risk mitigation'}},
    "SOFT_SKILLS": {'description': 'Communication and interpersonal skills training', 'annotations': {'skills': 'communication, teamwork, problem-solving', 'application': 'broadly applicable', 'development': 'personal development', 'effectiveness': 'workplace effectiveness', 'collaboration': 'collaboration skills'}},
    "SAFETY_TRAINING": {'description': 'Workplace safety and health training', 'annotations': {'focus': 'safety procedures and practices', 'compliance': 'OSHA compliance', 'prevention': 'accident prevention', 'emergency': 'emergency procedures', 'culture': 'safety culture'}},
    "DIVERSITY_INCLUSION": {'description': 'Training on diversity, equity, and inclusion', 'annotations': {'awareness': 'cultural awareness', 'bias': 'unconscious bias training', 'inclusion': 'inclusive practices', 'culture': 'inclusive culture', 'behavior': 'behavior change'}},
    "CROSS_TRAINING": {'description': 'Training in multiple roles or departments', 'annotations': {'flexibility': 'workforce flexibility', 'coverage': 'backup coverage', 'development': 'career development', 'understanding': 'broader understanding', 'collaboration': 'improved collaboration'}},
}

class EmployeeStatusEnum(RichEnum):
    """
    Current employment status classifications
    """
    # Enum members
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    PROBATIONARY = "PROBATIONARY"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    RETIRED = "RETIRED"

# Set metadata after class creation to avoid it becoming an enum member
EmployeeStatusEnum._metadata = {
    "ACTIVE": {'description': 'Currently employed and working', 'annotations': {'status': 'actively working', 'benefits': 'receiving full benefits', 'responsibilities': 'fulfilling job responsibilities', 'engagement': 'expected engagement', 'performance': 'subject to performance management'}},
    "ON_LEAVE": {'description': 'Temporarily away from work on approved leave', 'annotations': {'temporary': 'temporary absence', 'approval': 'approved leave', 'return': 'expected return date', 'benefits': 'may retain benefits', 'types': 'medical, family, personal leave'}},
    "PROBATIONARY": {'description': 'New employee in probationary period', 'annotations': {'duration': 'defined probationary period', 'evaluation': 'ongoing evaluation', 'benefits': 'limited or delayed benefits', 'termination': 'easier termination', 'assessment': 'performance assessment'}},
    "SUSPENDED": {'description': 'Temporarily suspended from work', 'annotations': {'disciplinary': 'disciplinary action', 'investigation': 'pending investigation', 'pay': 'with or without pay', 'temporary': 'temporary status', 'review': 'pending review'}},
    "TERMINATED": {'description': 'Employment has been terminated', 'annotations': {'end': 'employment ended', 'voluntary': 'voluntary or involuntary', 'benefits': 'benefits cessation', 'final': 'final status', 'documentation': 'termination documentation'}},
    "RETIRED": {'description': 'Retired from employment', 'annotations': {'voluntary': 'voluntary departure', 'age': 'retirement age', 'benefits': 'retirement benefits', 'service': 'completed service', 'transition': 'career transition'}},
}

class WorkArrangementEnum(RichEnum):
    """
    Work location and arrangement types
    """
    # Enum members
    ON_SITE = "ON_SITE"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    FIELD_WORK = "FIELD_WORK"
    TELECOMMUTE = "TELECOMMUTE"

# Set metadata after class creation to avoid it becoming an enum member
WorkArrangementEnum._metadata = {
    "ON_SITE": {'description': 'Work performed at company facilities', 'annotations': {'location': 'company premises', 'collaboration': 'in-person collaboration', 'supervision': 'direct supervision', 'equipment': 'company-provided equipment', 'culture': 'office culture participation'}},
    "REMOTE": {'description': 'Work performed away from company facilities', 'annotations': {'location': 'home or remote location', 'technology': 'technology-enabled work', 'flexibility': 'location flexibility', 'independence': 'high independence', 'communication': 'virtual communication'}},
    "HYBRID": {'description': 'Combination of on-site and remote work', 'annotations': {'flexibility': 'location flexibility', 'balance': 'office and remote balance', 'collaboration': 'mixed collaboration modes', 'scheduling': 'flexible scheduling', 'adaptation': 'adaptive work style'}},
    "FIELD_WORK": {'description': 'Work performed at client or field locations', 'annotations': {'location': 'customer or field locations', 'travel': 'travel requirements', 'independence': 'field independence', 'client': 'client interaction', 'mobility': 'mobile work style'}},
    "TELECOMMUTE": {'description': 'Regular remote work arrangement', 'annotations': {'arrangement': 'formal remote arrangement', 'technology': 'telecommunication technology', 'productivity': 'productivity focus', 'work_life': 'work-life integration', 'communication': 'virtual team communication'}},
}

class BenefitsCategoryEnum(RichEnum):
    """
    Categories of employee benefits and compensation
    """
    # Enum members
    HEALTH_INSURANCE = "HEALTH_INSURANCE"
    RETIREMENT_BENEFITS = "RETIREMENT_BENEFITS"
    PAID_TIME_OFF = "PAID_TIME_OFF"
    LIFE_INSURANCE = "LIFE_INSURANCE"
    FLEXIBLE_BENEFITS = "FLEXIBLE_BENEFITS"
    WELLNESS_PROGRAMS = "WELLNESS_PROGRAMS"
    PROFESSIONAL_DEVELOPMENT = "PROFESSIONAL_DEVELOPMENT"
    WORK_LIFE_BALANCE = "WORK_LIFE_BALANCE"

# Set metadata after class creation to avoid it becoming an enum member
BenefitsCategoryEnum._metadata = {
    "HEALTH_INSURANCE": {'description': 'Medical, dental, and vision insurance coverage', 'annotations': {'coverage': 'medical coverage', 'family': 'family coverage options', 'cost_sharing': 'employer contribution', 'networks': 'provider networks', 'essential': 'essential benefit'}},
    "RETIREMENT_BENEFITS": {'description': 'Retirement savings and pension plans', 'annotations': {'savings': '401(k) or retirement savings', 'matching': 'employer matching', 'vesting': 'vesting schedules', 'planning': 'retirement planning', 'long_term': 'long-term benefit'}},
    "PAID_TIME_OFF": {'description': 'Vacation, sick leave, and personal time', 'annotations': {'vacation': 'vacation time', 'sick': 'sick leave', 'personal': 'personal days', 'accrual': 'accrual systems', 'work_life': 'work-life balance'}},
    "LIFE_INSURANCE": {'description': 'Life and disability insurance coverage', 'annotations': {'protection': 'financial protection', 'beneficiaries': 'beneficiary designation', 'disability': 'disability coverage', 'group': 'group coverage', 'peace_of_mind': 'financial security'}},
    "FLEXIBLE_BENEFITS": {'description': 'Flexible spending and benefit choice options', 'annotations': {'choice': 'benefit choice', 'spending': 'flexible spending accounts', 'customization': 'personalized benefits', 'tax_advantage': 'tax advantages', 'lifestyle': 'lifestyle accommodation'}},
    "WELLNESS_PROGRAMS": {'description': 'Employee health and wellness initiatives', 'annotations': {'health': 'health promotion', 'fitness': 'fitness programs', 'mental_health': 'mental health support', 'prevention': 'preventive care', 'culture': 'wellness culture'}},
    "PROFESSIONAL_DEVELOPMENT": {'description': 'Training, education, and career development benefits', 'annotations': {'education': 'continuing education', 'training': 'professional training', 'career': 'career development', 'skill': 'skill enhancement', 'growth': 'professional growth'}},
    "WORK_LIFE_BALANCE": {'description': 'Benefits supporting work-life integration', 'annotations': {'flexibility': 'work flexibility', 'family': 'family support', 'childcare': 'childcare assistance', 'elder_care': 'elder care support', 'balance': 'life balance'}},
}

class MassSpectrometerFileFormat(RichEnum):
    """
    Standard file formats used in mass spectrometry
    """
    # Enum members
    MZML = "MZML"
    MZXML = "MZXML"
    MGF = "MGF"
    THERMO_RAW = "THERMO_RAW"
    WATERS_RAW = "WATERS_RAW"
    WIFF = "WIFF"
    MZDATA = "MZDATA"
    PKL = "PKL"
    DTA = "DTA"
    MS2 = "MS2"
    BRUKER_BAF = "BRUKER_BAF"
    BRUKER_TDF = "BRUKER_TDF"
    BRUKER_TSF = "BRUKER_TSF"
    MZ5 = "MZ5"
    MZMLB = "MZMLB"
    UIMF = "UIMF"

# Set metadata after class creation to avoid it becoming an enum member
MassSpectrometerFileFormat._metadata = {
    "MZML": {'description': 'mzML format - PSI standard for mass spectrometry data', 'meaning': 'MS:1000584'},
    "MZXML": {'description': 'ISB mzXML format', 'meaning': 'MS:1000566'},
    "MGF": {'description': 'Mascot Generic Format', 'meaning': 'MS:1001062'},
    "THERMO_RAW": {'description': 'Thermo RAW format', 'meaning': 'MS:1000563'},
    "WATERS_RAW": {'description': 'Waters raw format', 'meaning': 'MS:1000526'},
    "WIFF": {'description': 'ABI WIFF format', 'meaning': 'MS:1000562'},
    "MZDATA": {'description': 'PSI mzData format', 'meaning': 'MS:1000564'},
    "PKL": {'description': 'Micromass PKL format', 'meaning': 'MS:1000565'},
    "DTA": {'description': 'DTA format', 'meaning': 'MS:1000613'},
    "MS2": {'description': 'MS2 format', 'meaning': 'MS:1001466'},
    "BRUKER_BAF": {'description': 'Bruker BAF format', 'meaning': 'MS:1000815'},
    "BRUKER_TDF": {'description': 'Bruker TDF format', 'meaning': 'MS:1002817'},
    "BRUKER_TSF": {'description': 'Bruker TSF format', 'meaning': 'MS:1003282'},
    "MZ5": {'description': 'mz5 format', 'meaning': 'MS:1001881'},
    "MZMLB": {'description': 'mzMLb format', 'meaning': 'MS:1002838'},
    "UIMF": {'description': 'UIMF format', 'meaning': 'MS:1002531'},
}

class MassSpectrometerVendor(RichEnum):
    """
    Major mass spectrometer manufacturers
    """
    # Enum members
    THERMO_FISHER_SCIENTIFIC = "THERMO_FISHER_SCIENTIFIC"
    WATERS = "WATERS"
    BRUKER_DALTONICS = "BRUKER_DALTONICS"
    SCIEX = "SCIEX"
    AGILENT = "AGILENT"
    SHIMADZU = "SHIMADZU"
    LECO = "LECO"

# Set metadata after class creation to avoid it becoming an enum member
MassSpectrometerVendor._metadata = {
    "THERMO_FISHER_SCIENTIFIC": {'description': 'Thermo Fisher Scientific', 'meaning': 'MS:1000483'},
    "WATERS": {'description': 'Waters Corporation', 'meaning': 'MS:1000126'},
    "BRUKER_DALTONICS": {'description': 'Bruker Daltonics', 'meaning': 'MS:1000122'},
    "SCIEX": {'description': 'SCIEX (formerly Applied Biosystems)', 'meaning': 'MS:1000121'},
    "AGILENT": {'description': 'Agilent Technologies', 'meaning': 'MS:1000490'},
    "SHIMADZU": {'description': 'Shimadzu Corporation', 'meaning': 'MS:1000124'},
    "LECO": {'description': 'LECO Corporation', 'meaning': 'MS:1001800'},
}

class ChromatographyType(RichEnum):
    """
    Types of chromatographic separation methods
    """
    # Enum members
    GAS_CHROMATOGRAPHY = "GAS_CHROMATOGRAPHY"
    HIGH_PERFORMANCE_LIQUID_CHROMATOGRAPHY = "HIGH_PERFORMANCE_LIQUID_CHROMATOGRAPHY"
    LIQUID_CHROMATOGRAPHY_MASS_SPECTROMETRY = "LIQUID_CHROMATOGRAPHY_MASS_SPECTROMETRY"
    GAS_CHROMATOGRAPHY_MASS_SPECTROMETRY = "GAS_CHROMATOGRAPHY_MASS_SPECTROMETRY"
    TANDEM_MASS_SPECTROMETRY = "TANDEM_MASS_SPECTROMETRY"
    ISOTOPE_RATIO_MASS_SPECTROMETRY = "ISOTOPE_RATIO_MASS_SPECTROMETRY"

# Set metadata after class creation to avoid it becoming an enum member
ChromatographyType._metadata = {
    "GAS_CHROMATOGRAPHY": {'description': 'Gas chromatography', 'meaning': 'MSIO:0000147'},
    "HIGH_PERFORMANCE_LIQUID_CHROMATOGRAPHY": {'description': 'High performance liquid chromatography', 'meaning': 'MSIO:0000148'},
    "LIQUID_CHROMATOGRAPHY_MASS_SPECTROMETRY": {'description': 'Liquid chromatography-mass spectrometry', 'meaning': 'CHMO:0000524'},
    "GAS_CHROMATOGRAPHY_MASS_SPECTROMETRY": {'description': 'Gas chromatography-mass spectrometry', 'meaning': 'CHMO:0000497'},
    "TANDEM_MASS_SPECTROMETRY": {'description': 'Tandem mass spectrometry', 'meaning': 'CHMO:0000575'},
    "ISOTOPE_RATIO_MASS_SPECTROMETRY": {'description': 'Isotope ratio mass spectrometry', 'meaning': 'CHMO:0000506'},
}

class DerivatizationMethod(RichEnum):
    """
    Chemical derivatization methods for sample preparation
    """
    # Enum members
    SILYLATION = "SILYLATION"
    METHYLATION = "METHYLATION"
    ACETYLATION = "ACETYLATION"
    TRIFLUOROACETYLATION = "TRIFLUOROACETYLATION"
    ALKYLATION = "ALKYLATION"
    OXIMATION = "OXIMATION"

# Set metadata after class creation to avoid it becoming an enum member
DerivatizationMethod._metadata = {
    "SILYLATION": {'description': 'Addition of silyl groups for improved volatility', 'meaning': 'MSIO:0000117'},
    "METHYLATION": {'description': 'Addition of methyl groups', 'meaning': 'MSIO:0000115'},
    "ACETYLATION": {'description': 'Addition of acetyl groups', 'meaning': 'MSIO:0000112'},
    "TRIFLUOROACETYLATION": {'description': 'Addition of trifluoroacetyl groups', 'meaning': 'MSIO:0000113'},
    "ALKYLATION": {'description': 'Addition of alkyl groups', 'meaning': 'MSIO:0000114'},
    "OXIMATION": {'description': 'Addition of oxime groups', 'meaning': 'MSIO:0000116'},
}

class MetabolomicsAssayType(RichEnum):
    """
    Types of metabolomics assays and profiling approaches
    """
    # Enum members
    TARGETED_METABOLITE_PROFILING = "TARGETED_METABOLITE_PROFILING"
    UNTARGETED_METABOLITE_PROFILING = "UNTARGETED_METABOLITE_PROFILING"
    METABOLITE_QUANTITATION_HPLC = "METABOLITE_QUANTITATION_HPLC"

# Set metadata after class creation to avoid it becoming an enum member
MetabolomicsAssayType._metadata = {
    "TARGETED_METABOLITE_PROFILING": {'description': 'Assay targeting specific known metabolites', 'meaning': 'MSIO:0000100'},
    "UNTARGETED_METABOLITE_PROFILING": {'description': 'Assay profiling all detectable metabolites', 'meaning': 'MSIO:0000101'},
    "METABOLITE_QUANTITATION_HPLC": {'description': 'Metabolite quantitation using HPLC', 'meaning': 'MSIO:0000099'},
}

class AnalyticalControlType(RichEnum):
    """
    Types of control samples used in analytical chemistry
    """
    # Enum members
    INTERNAL_STANDARD = "INTERNAL_STANDARD"
    EXTERNAL_STANDARD = "EXTERNAL_STANDARD"
    POSITIVE_CONTROL = "POSITIVE_CONTROL"
    NEGATIVE_CONTROL = "NEGATIVE_CONTROL"
    LONG_TERM_REFERENCE = "LONG_TERM_REFERENCE"
    BLANK = "BLANK"
    QUALITY_CONTROL = "QUALITY_CONTROL"

# Set metadata after class creation to avoid it becoming an enum member
AnalyticalControlType._metadata = {
    "INTERNAL_STANDARD": {'description': 'Known amount of standard added to analytical sample', 'meaning': 'MSIO:0000005'},
    "EXTERNAL_STANDARD": {'description': 'Reference standard used as external reference point', 'meaning': 'MSIO:0000004'},
    "POSITIVE_CONTROL": {'description': 'Control providing known positive signal', 'meaning': 'MSIO:0000008'},
    "NEGATIVE_CONTROL": {'description': 'Control providing baseline/no signal reference', 'meaning': 'MSIO:0000007'},
    "LONG_TERM_REFERENCE": {'description': 'Stable reference for cross-batch comparisons', 'meaning': 'MSIO:0000006'},
    "BLANK": {'description': 'Sample containing only solvent/matrix without analyte'},
    "QUALITY_CONTROL": {'description': 'Sample with known composition for system performance monitoring'},
}

class Fake(ConfiguredBaseModel):
    pass  # TODO: Implement class slots
