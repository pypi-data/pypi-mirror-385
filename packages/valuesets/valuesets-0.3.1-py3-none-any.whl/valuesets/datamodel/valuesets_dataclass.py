# Auto generated from valuesets.yaml by pythongen.py version: 0.0.1
# Generation date: 2025-10-20T12:22:45
# Schema: valuesets
#
# id: https://w3id.org/linkml/valuesets
# description: A collection of commonly used value sets
# license: Apache-2.0

import dataclasses
import re
from dataclasses import dataclass
from datetime import (
    date,
    datetime,
    time
)
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Union
)

from jsonasobj2 import (
    JsonObj,
    as_dict
)
from linkml_runtime.linkml_model.meta import (
    EnumDefinition,
    PermissibleValue,
    PvFormulaOptions
)
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from linkml_runtime.utils.formatutils import (
    camelcase,
    sfx,
    underscore
)
from linkml_runtime.utils.metamodelcore import (
    bnode,
    empty_dict,
    empty_list
)
from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.yamlutils import (
    YAMLRoot,
    extended_float,
    extended_int,
    extended_str
)
from rdflib import (
    Namespace,
    URIRef
)



metamodel_version = "1.7.0"
version = None

# Namespaces
VALUESETS = CurieNamespace('valuesets', 'https://w3id.org/valuesets/')
DEFAULT_ = VALUESETS


# Types

# Class references



class Fake(YAMLRoot):
    _inherited_slots: ClassVar[list[str]] = []

    class_class_uri: ClassVar[URIRef] = VALUESETS["Fake"]
    class_class_curie: ClassVar[str] = "valuesets:Fake"
    class_name: ClassVar[str] = "Fake"
    class_model_uri: ClassVar[URIRef] = VALUESETS.Fake


# Enumerations
class RelativeTimeEnum(EnumDefinitionImpl):

    BEFORE = PermissibleValue(text="BEFORE")
    AFTER = PermissibleValue(text="AFTER")
    AT_SAME_TIME_AS = PermissibleValue(text="AT_SAME_TIME_AS")

    _defn = EnumDefinition(
        name="RelativeTimeEnum",
    )

class PresenceEnum(EnumDefinitionImpl):

    PRESENT = PermissibleValue(
        text="PRESENT",
        description="The entity is present")
    ABSENT = PermissibleValue(
        text="ABSENT",
        description="The entity is absent")
    BELOW_DETECTION_LIMIT = PermissibleValue(
        text="BELOW_DETECTION_LIMIT",
        description="The entity is below the detection limit")
    ABOVE_DETECTION_LIMIT = PermissibleValue(
        text="ABOVE_DETECTION_LIMIT",
        description="The entity is above the detection limit")

    _defn = EnumDefinition(
        name="PresenceEnum",
    )

class ContributorType(EnumDefinitionImpl):
    """
    The type of contributor being represented.
    """
    PERSON = PermissibleValue(
        text="PERSON",
        description="A person.",
        meaning=NCIT["C25190"])
    ORGANIZATION = PermissibleValue(
        text="ORGANIZATION",
        description="An organization.",
        meaning=NCIT["C41206"])

    _defn = EnumDefinition(
        name="ContributorType",
        description="The type of contributor being represented.",
    )

class DataAbsentEnum(EnumDefinitionImpl):
    """
    Used to specify why the normally expected content of the data element is missing.
    """
    unknown = PermissibleValue(
        text="unknown",
        title="Unknown",
        description="The value is expected to exist but is not known.",
        meaning=FHIR_DATA_ABSENT_REASON["unknown"])
    masked = PermissibleValue(
        text="masked",
        title="Masked",
        description="The information is not available due to security, privacy or related reasons.",
        meaning=FHIR_DATA_ABSENT_REASON["masked"])
    unsupported = PermissibleValue(
        text="unsupported",
        title="Unsupported",
        description="The source system wasn't capable of supporting this element.",
        meaning=FHIR_DATA_ABSENT_REASON["unsupported"])
    error = PermissibleValue(
        text="error",
        title="Error",
        description="Some system or workflow process error means that the information is not available.",
        meaning=FHIR_DATA_ABSENT_REASON["error"])

    _defn = EnumDefinition(
        name="DataAbsentEnum",
        description="Used to specify why the normally expected content of the data element is missing.",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "asked-unknown",
            PermissibleValue(
                text="asked-unknown",
                title="Asked But Unknown",
                description="The source was asked but does not know the value.",
                meaning=FHIR_DATA_ABSENT_REASON["asked-unknown"]))
        setattr(cls, "temp-unknown",
            PermissibleValue(
                text="temp-unknown",
                title="Temporarily Unknown",
                description="There is reason to expect (from the workflow) that the value may become known.",
                meaning=FHIR_DATA_ABSENT_REASON["temp-unknown"]))
        setattr(cls, "not-asked",
            PermissibleValue(
                text="not-asked",
                title="Not Asked",
                description="The workflow didn't lead to this value being known.",
                meaning=FHIR_DATA_ABSENT_REASON["not-asked"]))
        setattr(cls, "asked-declined",
            PermissibleValue(
                text="asked-declined",
                title="Asked But Declined",
                description="The source was asked but declined to answer.",
                meaning=FHIR_DATA_ABSENT_REASON["asked-declined"]))
        setattr(cls, "not-applicable",
            PermissibleValue(
                text="not-applicable",
                title="Not Applicable",
                description="There is no proper value for this element (e.g. last menstrual period for a male).",
                meaning=FHIR_DATA_ABSENT_REASON["not-applicable"]))
        setattr(cls, "as-text",
            PermissibleValue(
                text="as-text",
                title="As Text",
                description="The content of the data is represented in the resource narrative.",
                meaning=FHIR_DATA_ABSENT_REASON["as-text"]))
        setattr(cls, "not-a-number",
            PermissibleValue(
                text="not-a-number",
                title="Not a Number (NaN)",
                description="""The numeric value is undefined or unrepresentable due to a floating point processing error.""",
                meaning=FHIR_DATA_ABSENT_REASON["not-a-number"]))
        setattr(cls, "negative-infinity",
            PermissibleValue(
                text="negative-infinity",
                title="Negative Infinity (NINF)",
                description="""The numeric value is excessively low and unrepresentable due to a floating point processing        error.""",
                meaning=FHIR_DATA_ABSENT_REASON["negative-infinity"]))
        setattr(cls, "positive-infinity",
            PermissibleValue(
                text="positive-infinity",
                title="Positive Infinity (PINF)",
                description="""The numeric value is excessively high and unrepresentable due to a floating point processing        error.""",
                meaning=FHIR_DATA_ABSENT_REASON["positive-infinity"]))
        setattr(cls, "not-performed",
            PermissibleValue(
                text="not-performed",
                title="Not Performed",
                description="""The value is not available because the observation procedure (test, etc.) was not performed.""",
                meaning=FHIR_DATA_ABSENT_REASON["not-performed"]))
        setattr(cls, "not-permitted",
            PermissibleValue(
                text="not-permitted",
                title="Not Permitted",
                description="""The value is not permitted in this context (e.g. due to profiles, or the base data types).""",
                meaning=FHIR_DATA_ABSENT_REASON["not-permitted"]))

class PredictionOutcomeType(EnumDefinitionImpl):

    TP = PermissibleValue(
        text="TP",
        description="True Positive")
    FP = PermissibleValue(
        text="FP",
        description="False Positive")
    TN = PermissibleValue(
        text="TN",
        description="True Negative")
    FN = PermissibleValue(
        text="FN",
        description="False Negative")

    _defn = EnumDefinition(
        name="PredictionOutcomeType",
    )

class VitalStatusEnum(EnumDefinitionImpl):
    """
    The vital status of a person or organism
    """
    ALIVE = PermissibleValue(
        text="ALIVE",
        description="The person is living",
        meaning=NCIT["C37987"])
    DECEASED = PermissibleValue(
        text="DECEASED",
        title="Dead",
        description="The person has died",
        meaning=NCIT["C28554"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="The vital status is not known",
        meaning=NCIT["C17998"])
    PRESUMED_ALIVE = PermissibleValue(
        text="PRESUMED_ALIVE",
        description="The person is presumed to be alive based on available information")
    PRESUMED_DECEASED = PermissibleValue(
        text="PRESUMED_DECEASED",
        description="The person is presumed to be deceased based on available information")

    _defn = EnumDefinition(
        name="VitalStatusEnum",
        description="The vital status of a person or organism",
    )

class VaccinationStatusEnum(EnumDefinitionImpl):
    """
    The vaccination status of an individual
    """
    VACCINATED = PermissibleValue(
        text="VACCINATED",
        description="A status indicating that an individual has received a vaccination",
        meaning=NCIT["C28385"])
    NOT_VACCINATED = PermissibleValue(
        text="NOT_VACCINATED",
        description="A status indicating that an individual has not received any of the required vaccinations",
        meaning=NCIT["C183125"])
    FULLY_VACCINATED = PermissibleValue(
        text="FULLY_VACCINATED",
        description="A status indicating that an individual has received all the required vaccinations",
        meaning=NCIT["C183123"])
    PARTIALLY_VACCINATED = PermissibleValue(
        text="PARTIALLY_VACCINATED",
        description="A status indicating that an individual has received some of the required vaccinations",
        meaning=NCIT["C183124"])
    BOOSTER = PermissibleValue(
        text="BOOSTER",
        description="A status indicating that an individual has received a booster vaccination",
        meaning=NCIT["C28320"])
    UNVACCINATED = PermissibleValue(
        text="UNVACCINATED",
        description="An organismal quality that indicates an organism is unvaccinated with any vaccine",
        meaning=VO["0001377"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="The vaccination status is not known",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="VaccinationStatusEnum",
        description="The vaccination status of an individual",
    )

class VaccinationPeriodicityEnum(EnumDefinitionImpl):
    """
    The periodicity or frequency of vaccination
    """
    SINGLE_DOSE = PermissibleValue(
        text="SINGLE_DOSE",
        description="A vaccination regimen requiring only one dose")
    ANNUAL = PermissibleValue(
        text="ANNUAL",
        description="Vaccination occurring once per year",
        meaning=NCIT["C54647"])
    SEASONAL = PermissibleValue(
        text="SEASONAL",
        description="Vaccination occurring seasonally (e.g., for influenza)")
    BOOSTER = PermissibleValue(
        text="BOOSTER",
        description="A second or later vaccine dose to maintain immune response",
        meaning=NCIT["C28320"])
    PRIMARY_SERIES = PermissibleValue(
        text="PRIMARY_SERIES",
        description="The initial series of vaccine doses")
    PERIODIC = PermissibleValue(
        text="PERIODIC",
        description="Vaccination occurring at regular intervals")
    ONE_TIME = PermissibleValue(
        text="ONE_TIME",
        description="A vaccination given only once in a lifetime")
    AS_NEEDED = PermissibleValue(
        text="AS_NEEDED",
        description="Vaccination given as needed based on exposure risk or other factors")

    _defn = EnumDefinition(
        name="VaccinationPeriodicityEnum",
        description="The periodicity or frequency of vaccination",
    )

class VaccineCategoryEnum(EnumDefinitionImpl):
    """
    The broad category or type of vaccine
    """
    LIVE_ATTENUATED_VACCINE = PermissibleValue(
        text="LIVE_ATTENUATED_VACCINE",
        description="A vaccine made from microbes that have been weakened in the laboratory",
        meaning=VO["0000367"])
    INACTIVATED_VACCINE = PermissibleValue(
        text="INACTIVATED_VACCINE",
        description="A preparation of killed microorganisms intended to prevent infectious disease",
        meaning=NCIT["C29694"])
    CONJUGATE_VACCINE = PermissibleValue(
        text="CONJUGATE_VACCINE",
        description="A vaccine created by covalently attaching an antigen to a carrier protein",
        meaning=NCIT["C1455"])
    MRNA_VACCINE = PermissibleValue(
        text="MRNA_VACCINE",
        description="A vaccine based on mRNA that encodes the antigen of interest",
        meaning=NCIT["C172787"])
    DNA_VACCINE = PermissibleValue(
        text="DNA_VACCINE",
        description="A vaccine using DNA to produce protein that promotes immune responses",
        meaning=NCIT["C39619"])
    PEPTIDE_VACCINE = PermissibleValue(
        text="PEPTIDE_VACCINE",
        description="A vaccine based on synthetic peptides",
        meaning=NCIT["C1752"])
    VIRAL_VECTOR = PermissibleValue(
        text="VIRAL_VECTOR",
        description="A vaccine using a modified virus as a delivery system")
    SUBUNIT = PermissibleValue(
        text="SUBUNIT",
        description="A vaccine containing purified pieces of the pathogen")
    TOXOID = PermissibleValue(
        text="TOXOID",
        description="A vaccine made from a toxin that has been made harmless")
    RECOMBINANT = PermissibleValue(
        text="RECOMBINANT",
        description="A vaccine produced using recombinant DNA technology")

    _defn = EnumDefinition(
        name="VaccineCategoryEnum",
        description="The broad category or type of vaccine",
    )

class HealthcareEncounterClassification(EnumDefinitionImpl):

    _defn = EnumDefinition(
        name="HealthcareEncounterClassification",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "Inpatient Visit",
            PermissibleValue(
                text="Inpatient Visit",
                description="""Person visiting hospital, at a Care Site, in bed, for duration of more than one day, with physicians and other Providers permanently available to deliver service around the clock"""))
        setattr(cls, "Emergency Room Visit",
            PermissibleValue(
                text="Emergency Room Visit",
                description="""Person visiting dedicated healthcare institution for treating emergencies, at a Care Site, within one day, with physicians and Providers permanently available to deliver service around the clock"""))
        setattr(cls, "Emergency Room and Inpatient Visit",
            PermissibleValue(
                text="Emergency Room and Inpatient Visit",
                description="""Person visiting ER followed by a subsequent Inpatient Visit, where Emergency department is part of hospital, and transition from the ER to other hospital departments is undefined"""))
        setattr(cls, "Non-hospital institution Visit",
            PermissibleValue(
                text="Non-hospital institution Visit",
                description="""Person visiting dedicated institution for reasons of poor health, at a Care Site, long-term or permanently, with no physician but possibly other Providers permanently available to deliver service around the clock"""))
        setattr(cls, "Outpatient Visit",
            PermissibleValue(
                text="Outpatient Visit",
                description="""Person visiting dedicated ambulatory healthcare institution, at a Care Site, within one day, without bed, with physicians or medical Providers delivering service during Visit"""))
        setattr(cls, "Home Visit",
            PermissibleValue(
                text="Home Visit",
                description="Provider visiting Person, without a Care Site, within one day, delivering service"))
        setattr(cls, "Telehealth Visit",
            PermissibleValue(
                text="Telehealth Visit",
                description="Patient engages with Provider through communication media"))
        setattr(cls, "Pharmacy Visit",
            PermissibleValue(
                text="Pharmacy Visit",
                description="Person visiting pharmacy for dispensing of Drug, at a Care Site, within one day"))
        setattr(cls, "Laboratory Visit",
            PermissibleValue(
                text="Laboratory Visit",
                description="""Patient visiting dedicated institution, at a Care Site, within one day, for the purpose of a Measurement."""))
        setattr(cls, "Ambulance Visit",
            PermissibleValue(
                text="Ambulance Visit",
                description="""Person using transportation service for the purpose of initiating one of the other Visits, without a Care Site, within one day, potentially with Providers accompanying the Visit and delivering service"""))
        setattr(cls, "Case Management Visit",
            PermissibleValue(
                text="Case Management Visit",
                description="""Person interacting with healthcare system, without a Care Site, within a day, with no Providers involved, for administrative purposes"""))

class EducationLevel(EnumDefinitionImpl):
    """
    Years of education that a person has completed
    """
    ELEM = PermissibleValue(
        text="ELEM",
        description="Elementary School",
        meaning=HL7["v3-EducationLevel#ELEM"])
    SEC = PermissibleValue(
        text="SEC",
        description="Some secondary or high school education",
        meaning=HL7["v3-EducationLevel#SEC"])
    HS = PermissibleValue(
        text="HS",
        description="High School or secondary school degree complete",
        meaning=HL7["v3-EducationLevel#HS"])
    SCOL = PermissibleValue(
        text="SCOL",
        description="Some College education",
        meaning=HL7["v3-EducationLevel#SCOL"])
    ASSOC = PermissibleValue(
        text="ASSOC",
        description="Associate's or technical degree complete",
        meaning=HL7["v3-EducationLevel#ASSOC"])
    BD = PermissibleValue(
        text="BD",
        description="College or baccalaureate degree complete",
        meaning=HL7["v3-EducationLevel#BD"])
    PB = PermissibleValue(
        text="PB",
        description="Some post-baccalaureate education",
        meaning=HL7["v3-EducationLevel#PB"])
    GD = PermissibleValue(
        text="GD",
        description="Graduate or professional Degree complete",
        meaning=HL7["v3-EducationLevel#GD"])
    POSTG = PermissibleValue(
        text="POSTG",
        description="Doctoral or post graduate education",
        meaning=HL7["v3-EducationLevel#POSTG"])

    _defn = EnumDefinition(
        name="EducationLevel",
        description="Years of education that a person has completed",
    )

class MaritalStatus(EnumDefinitionImpl):
    """
    The domestic partnership status of a person
    """
    ANNULLED = PermissibleValue(
        text="ANNULLED",
        description="Marriage contract has been declared null and to not have existed",
        meaning=HL7["marital-status#A"])
    DIVORCED = PermissibleValue(
        text="DIVORCED",
        description="Marriage contract has been declared dissolved and inactive",
        meaning=HL7["marital-status#D"])
    INTERLOCUTORY = PermissibleValue(
        text="INTERLOCUTORY",
        description="Subject to an Interlocutory Decree",
        meaning=HL7["marital-status#I"])
    LEGALLY_SEPARATED = PermissibleValue(
        text="LEGALLY_SEPARATED",
        description="Legally Separated",
        meaning=HL7["marital-status#L"])
    MARRIED = PermissibleValue(
        text="MARRIED",
        description="A current marriage contract is active",
        meaning=HL7["marital-status#M"])
    COMMON_LAW = PermissibleValue(
        text="COMMON_LAW",
        description="Marriage recognized in some jurisdictions based on parties' agreement",
        meaning=HL7["marital-status#C"])
    POLYGAMOUS = PermissibleValue(
        text="POLYGAMOUS",
        description="More than 1 current spouse",
        meaning=HL7["marital-status#P"])
    DOMESTIC_PARTNER = PermissibleValue(
        text="DOMESTIC_PARTNER",
        description="Person declares that a domestic partner relationship exists",
        meaning=HL7["marital-status#T"])
    UNMARRIED = PermissibleValue(
        text="UNMARRIED",
        description="Currently not in a marriage contract",
        meaning=HL7["marital-status#U"])
    NEVER_MARRIED = PermissibleValue(
        text="NEVER_MARRIED",
        description="No marriage contract has ever been entered",
        meaning=HL7["marital-status#S"])
    WIDOWED = PermissibleValue(
        text="WIDOWED",
        description="The spouse has died",
        meaning=HL7["marital-status#W"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="A proper value is applicable, but not known",
        meaning=HL7["marital-status#UNK"])

    _defn = EnumDefinition(
        name="MaritalStatus",
        description="The domestic partnership status of a person",
    )

class EmploymentStatus(EnumDefinitionImpl):
    """
    Employment status of a person
    """
    FULL_TIME_EMPLOYED = PermissibleValue(
        text="FULL_TIME_EMPLOYED",
        description="Full time employed",
        meaning=HL7["v2-0066#1"])
    PART_TIME_EMPLOYED = PermissibleValue(
        text="PART_TIME_EMPLOYED",
        description="Part time employed",
        meaning=HL7["v2-0066#2"])
    UNEMPLOYED = PermissibleValue(
        text="UNEMPLOYED",
        description="Unemployed",
        meaning=HL7["v2-0066#3"])
    SELF_EMPLOYED = PermissibleValue(
        text="SELF_EMPLOYED",
        description="Self-employed",
        meaning=HL7["v2-0066#4"])
    RETIRED = PermissibleValue(
        text="RETIRED",
        description="Retired",
        meaning=HL7["v2-0066#5"])
    ACTIVE_MILITARY = PermissibleValue(
        text="ACTIVE_MILITARY",
        description="On active military duty",
        meaning=HL7["v2-0066#6"])
    CONTRACT = PermissibleValue(
        text="CONTRACT",
        description="Contract, per diem",
        meaning=HL7["v2-0066#C"])
    PER_DIEM = PermissibleValue(
        text="PER_DIEM",
        description="Per Diem",
        meaning=HL7["v2-0066#D"])
    LEAVE_OF_ABSENCE = PermissibleValue(
        text="LEAVE_OF_ABSENCE",
        description="Leave of absence",
        meaning=HL7["v2-0066#L"])
    OTHER = PermissibleValue(
        text="OTHER",
        description="Other",
        meaning=HL7["v2-0066#O"])
    TEMPORARILY_UNEMPLOYED = PermissibleValue(
        text="TEMPORARILY_UNEMPLOYED",
        description="Temporarily unemployed",
        meaning=HL7["v2-0066#T"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="Unknown",
        meaning=HL7["v2-0066#9"])

    _defn = EnumDefinition(
        name="EmploymentStatus",
        description="Employment status of a person",
    )

class HousingStatus(EnumDefinitionImpl):
    """
    Housing status of patients per UDS Plus HRSA standards
    """
    HOMELESS_SHELTER = PermissibleValue(
        text="HOMELESS_SHELTER",
        description="Patients who are living in a homeless shelter",
        meaning=HL7["udsplus-housing-status-codes#homeless-shelter"])
    TRANSITIONAL = PermissibleValue(
        text="TRANSITIONAL",
        description="Patients who do not have a house and are in a transitional state",
        meaning=HL7["udsplus-housing-status-codes#transitional"])
    DOUBLING_UP = PermissibleValue(
        text="DOUBLING_UP",
        description="Patients who are doubling up with others",
        meaning=HL7["udsplus-housing-status-codes#doubling-up"])
    STREET = PermissibleValue(
        text="STREET",
        description="Patients who do not have a house and are living on the streets",
        meaning=HL7["udsplus-housing-status-codes#street"])
    PERMANENT_SUPPORTIVE_HOUSING = PermissibleValue(
        text="PERMANENT_SUPPORTIVE_HOUSING",
        description="Patients who are living in a permanent supportive housing",
        meaning=HL7["udsplus-housing-status-codes#permanent-supportive-housing"])
    OTHER = PermissibleValue(
        text="OTHER",
        description="Patients who have other kinds of accommodation",
        meaning=HL7["udsplus-housing-status-codes#other"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="Patients with Unknown accommodation",
        meaning=HL7["udsplus-housing-status-codes#unknown"])

    _defn = EnumDefinition(
        name="HousingStatus",
        description="Housing status of patients per UDS Plus HRSA standards",
    )

class GenderIdentity(EnumDefinitionImpl):
    """
    Gender identity codes indicating an individual's personal sense of gender
    """
    FEMALE = PermissibleValue(
        text="FEMALE",
        description="Identifies as female gender (finding)",
        meaning=SNOMED["446141000124107"])
    MALE = PermissibleValue(
        text="MALE",
        description="Identifies as male gender (finding)",
        meaning=SNOMED["446151000124109"])
    NON_BINARY = PermissibleValue(
        text="NON_BINARY",
        description="Identifies as gender nonbinary",
        meaning=SNOMED["33791000087105"])
    ASKED_DECLINED = PermissibleValue(
        text="ASKED_DECLINED",
        description="Asked But Declined",
        meaning=HL7["asked-declined"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="A proper value is applicable, but not known",
        meaning=HL7["UNK"])

    _defn = EnumDefinition(
        name="GenderIdentity",
        description="Gender identity codes indicating an individual's personal sense of gender",
    )

class OmbRaceCategory(EnumDefinitionImpl):
    """
    Office of Management and Budget (OMB) race category codes
    """
    AMERICAN_INDIAN_OR_ALASKA_NATIVE = PermissibleValue(
        text="AMERICAN_INDIAN_OR_ALASKA_NATIVE",
        description="American Indian or Alaska Native",
        meaning=HL7["CDCREC#1002-5"])
    ASIAN = PermissibleValue(
        text="ASIAN",
        description="Asian",
        meaning=HL7["CDCREC#2028-9"])
    BLACK_OR_AFRICAN_AMERICAN = PermissibleValue(
        text="BLACK_OR_AFRICAN_AMERICAN",
        description="Black or African American",
        meaning=HL7["CDCREC#2054-5"])
    NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = PermissibleValue(
        text="NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER",
        description="Native Hawaiian or Other Pacific Islander",
        meaning=HL7["CDCREC#2076-8"])
    WHITE = PermissibleValue(
        text="WHITE",
        description="White",
        meaning=HL7["CDCREC#2106-3"])
    OTHER_RACE = PermissibleValue(
        text="OTHER_RACE",
        description="Other Race (discouraged for statistical analysis)",
        meaning=HL7["CDCREC#2131-1"])
    ASKED_BUT_UNKNOWN = PermissibleValue(
        text="ASKED_BUT_UNKNOWN",
        description="asked but unknown",
        meaning=HL7["ASKU"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="unknown",
        meaning=HL7["UNK"])

    _defn = EnumDefinition(
        name="OmbRaceCategory",
        description="Office of Management and Budget (OMB) race category codes",
    )

class OmbEthnicityCategory(EnumDefinitionImpl):
    """
    Office of Management and Budget (OMB) ethnicity category codes
    """
    HISPANIC_OR_LATINO = PermissibleValue(
        text="HISPANIC_OR_LATINO",
        description="Hispanic or Latino",
        meaning=HL7["CDCREC#2135-2"])
    NOT_HISPANIC_OR_LATINO = PermissibleValue(
        text="NOT_HISPANIC_OR_LATINO",
        description="Not Hispanic or Latino",
        meaning=HL7["CDCREC#2186-5"])
    ASKED_BUT_UNKNOWN = PermissibleValue(
        text="ASKED_BUT_UNKNOWN",
        description="asked but unknown",
        meaning=HL7["ASKU"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="unknown",
        meaning=HL7["UNK"])

    _defn = EnumDefinition(
        name="OmbEthnicityCategory",
        description="Office of Management and Budget (OMB) ethnicity category codes",
    )

class CaseOrControlEnum(EnumDefinitionImpl):

    CASE = PermissibleValue(
        text="CASE",
        title="case role in case-control study",
        meaning=OBI["0002492"])
    CONTROL = PermissibleValue(
        text="CONTROL",
        title="control role in case-control study",
        meaning=OBI["0002493"])

    _defn = EnumDefinition(
        name="CaseOrControlEnum",
    )

class StudyDesignEnum(EnumDefinitionImpl):

    _defn = EnumDefinition(
        name="StudyDesignEnum",
    )

class InvestigativeProtocolEnum(EnumDefinitionImpl):

    _defn = EnumDefinition(
        name="InvestigativeProtocolEnum",
    )

class SampleProcessingEnum(EnumDefinitionImpl):

    _defn = EnumDefinition(
        name="SampleProcessingEnum",
    )

class GOEvidenceCode(EnumDefinitionImpl):
    """
    Gene Ontology evidence codes mapped to Evidence and Conclusion Ontology (ECO) terms
    """
    EXP = PermissibleValue(
        text="EXP",
        title="Inferred from Experiment",
        meaning=ECO["0000269"])
    IDA = PermissibleValue(
        text="IDA",
        title="Inferred from Direct Assay",
        meaning=ECO["0000314"])
    IPI = PermissibleValue(
        text="IPI",
        title="Inferred from Physical Interaction",
        meaning=ECO["0000353"])
    IMP = PermissibleValue(
        text="IMP",
        title="Inferred from Mutant Phenotype",
        meaning=ECO["0000315"])
    IGI = PermissibleValue(
        text="IGI",
        title="Inferred from Genetic Interaction",
        meaning=ECO["0000316"])
    IEP = PermissibleValue(
        text="IEP",
        title="Inferred from Expression Pattern",
        meaning=ECO["0000270"])
    HTP = PermissibleValue(
        text="HTP",
        title="Inferred from High Throughput Experiment",
        meaning=ECO["0006056"])
    HDA = PermissibleValue(
        text="HDA",
        title="Inferred from High Throughput Direct Assay",
        meaning=ECO["0007005"])
    HMP = PermissibleValue(
        text="HMP",
        title="Inferred from High Throughput Mutant Phenotype",
        meaning=ECO["0007001"])
    HGI = PermissibleValue(
        text="HGI",
        title="Inferred from High Throughput Genetic Interaction",
        meaning=ECO["0007003"])
    HEP = PermissibleValue(
        text="HEP",
        title="Inferred from High Throughput Expression Pattern",
        meaning=ECO["0007007"])
    IBA = PermissibleValue(
        text="IBA",
        title="Inferred from Biological aspect of Ancestor",
        meaning=ECO["0000318"])
    IBD = PermissibleValue(
        text="IBD",
        title="Inferred from Biological aspect of Descendant",
        meaning=ECO["0000319"])
    IKR = PermissibleValue(
        text="IKR",
        title="Inferred from Key Residues",
        meaning=ECO["0000320"])
    IRD = PermissibleValue(
        text="IRD",
        title="Inferred from Rapid Divergence",
        meaning=ECO["0000321"])
    ISS = PermissibleValue(
        text="ISS",
        title="Inferred from Sequence or structural Similarity",
        meaning=ECO["0000250"])
    ISO = PermissibleValue(
        text="ISO",
        title="Inferred from Sequence Orthology",
        meaning=ECO["0000266"])
    ISA = PermissibleValue(
        text="ISA",
        title="Inferred from Sequence Alignment",
        meaning=ECO["0000247"])
    ISM = PermissibleValue(
        text="ISM",
        title="Inferred from Sequence Model",
        meaning=ECO["0000255"])
    IGC = PermissibleValue(
        text="IGC",
        title="Inferred from Genomic Context",
        meaning=ECO["0000317"])
    RCA = PermissibleValue(
        text="RCA",
        title="Inferred from Reviewed Computational Analysis",
        meaning=ECO["0000245"])
    TAS = PermissibleValue(
        text="TAS",
        title="Traceable Author Statement",
        meaning=ECO["0000304"])
    NAS = PermissibleValue(
        text="NAS",
        title="Non-traceable Author Statement",
        meaning=ECO["0000303"])
    IC = PermissibleValue(
        text="IC",
        title="Inferred by Curator",
        meaning=ECO["0000305"])
    ND = PermissibleValue(
        text="ND",
        title="No biological Data available",
        meaning=ECO["0000307"])
    IEA = PermissibleValue(
        text="IEA",
        title="Inferred from Electronic Annotation",
        meaning=ECO["0000501"])

    _defn = EnumDefinition(
        name="GOEvidenceCode",
        description="Gene Ontology evidence codes mapped to Evidence and Conclusion Ontology (ECO) terms",
    )

class GOElectronicMethods(EnumDefinitionImpl):
    """
    Electronic annotation methods used in Gene Ontology, identified by GO_REF codes
    """
    INTERPRO2GO = PermissibleValue(
        text="INTERPRO2GO",
        title="Gene Ontology annotation based on InterPro classification",
        meaning=GO_REF["0000002"])
    EC2GO = PermissibleValue(
        text="EC2GO",
        title="Gene Ontology annotation based on Enzyme Commission mapping",
        meaning=GO_REF["0000003"])
    UNIPROTKB_KW2GO = PermissibleValue(
        text="UNIPROTKB_KW2GO",
        title="Gene Ontology annotation based on UniProtKB keywords",
        meaning=GO_REF["0000004"])
    UNIPROTKB_SUBCELL2GO = PermissibleValue(
        text="UNIPROTKB_SUBCELL2GO",
        title="Gene Ontology annotation based on UniProtKB Subcellular Location vocabulary",
        meaning=GO_REF["0000023"])
    HAMAP_RULE2GO = PermissibleValue(
        text="HAMAP_RULE2GO",
        title="Gene Ontology annotation based on HAMAP family rules",
        meaning=GO_REF["0000020"])
    UNIPATHWAY2GO = PermissibleValue(
        text="UNIPATHWAY2GO",
        title="Gene Ontology annotation based on UniPathway vocabulary",
        meaning=GO_REF["0000041"])
    UNIRULE2GO = PermissibleValue(
        text="UNIRULE2GO",
        title="Gene Ontology annotation based on UniRule rules",
        meaning=GO_REF["0000104"])
    RHEA2GO = PermissibleValue(
        text="RHEA2GO",
        title="Gene Ontology annotation based on Rhea mapping",
        meaning=GO_REF["0000116"])
    ENSEMBL_COMPARA = PermissibleValue(
        text="ENSEMBL_COMPARA",
        title="Gene Ontology annotation based on Ensembl Compara orthology",
        meaning=GO_REF["0000107"])
    PANTHER = PermissibleValue(
        text="PANTHER",
        title="Gene Ontology annotation based on PANTHER phylogenetic trees",
        meaning=GO_REF["0000033"])
    REACTOME = PermissibleValue(
        text="REACTOME",
        title="Gene Ontology annotation based on Reactome pathways",
        meaning=GO_REF["0000018"])
    RFAM2GO = PermissibleValue(
        text="RFAM2GO",
        title="Gene Ontology annotation based on Rfam classification",
        meaning=GO_REF["0000115"])
    DICTYBASE = PermissibleValue(
        text="DICTYBASE",
        title="Gene Ontology annotation by DictyBase",
        meaning=GO_REF["0000015"])
    MGI = PermissibleValue(
        text="MGI",
        title="Gene Ontology annotation by Mouse Genome Informatics",
        meaning=GO_REF["0000096"])
    ZFIN = PermissibleValue(
        text="ZFIN",
        title="Gene Ontology annotation by Zebrafish Information Network",
        meaning=GO_REF["0000031"])
    FLYBASE = PermissibleValue(
        text="FLYBASE",
        title="Gene Ontology annotation by FlyBase",
        meaning=GO_REF["0000047"])
    WORMBASE = PermissibleValue(
        text="WORMBASE",
        title="Gene Ontology annotation by WormBase",
        meaning=GO_REF["0000003"])
    SGD = PermissibleValue(
        text="SGD",
        title="Gene Ontology annotation by Saccharomyces Genome Database",
        meaning=GO_REF["0000100"])
    POMBASE = PermissibleValue(
        text="POMBASE",
        title="Gene Ontology annotation by PomBase",
        meaning=GO_REF["0000024"])
    METACYC2GO = PermissibleValue(
        text="METACYC2GO",
        title="Gene Ontology annotation based on MetaCyc pathways",
        meaning=GO_REF["0000112"])

    _defn = EnumDefinition(
        name="GOElectronicMethods",
        description="Electronic annotation methods used in Gene Ontology, identified by GO_REF codes",
    )

class OrganismTaxonEnum(EnumDefinitionImpl):

    _defn = EnumDefinition(
        name="OrganismTaxonEnum",
    )

class CommonOrganismTaxaEnum(EnumDefinitionImpl):
    """
    Common model organisms used in biological research, mapped to NCBI Taxonomy IDs
    """
    BACTERIA = PermissibleValue(
        text="BACTERIA",
        description="Bacteria domain",
        meaning=NCBITAXON["2"])
    ARCHAEA = PermissibleValue(
        text="ARCHAEA",
        description="Archaea domain",
        meaning=NCBITAXON["2157"])
    EUKARYOTA = PermissibleValue(
        text="EUKARYOTA",
        description="Eukaryota domain",
        meaning=NCBITAXON["2759"])
    VIRUSES = PermissibleValue(
        text="VIRUSES",
        description="Viruses (not a true domain)",
        meaning=NCBITAXON["10239"])
    VERTEBRATA = PermissibleValue(
        text="VERTEBRATA",
        title="Vertebrata <vertebrates>",
        description="Vertebrates",
        meaning=NCBITAXON["7742"])
    MAMMALIA = PermissibleValue(
        text="MAMMALIA",
        description="Mammals",
        meaning=NCBITAXON["40674"])
    PRIMATES = PermissibleValue(
        text="PRIMATES",
        description="Primates",
        meaning=NCBITAXON["9443"])
    RODENTIA = PermissibleValue(
        text="RODENTIA",
        description="Rodents",
        meaning=NCBITAXON["9989"])
    CARNIVORA = PermissibleValue(
        text="CARNIVORA",
        description="Carnivores",
        meaning=NCBITAXON["33554"])
    ARTIODACTYLA = PermissibleValue(
        text="ARTIODACTYLA",
        description="Even-toed ungulates",
        meaning=NCBITAXON["91561"])
    AVES = PermissibleValue(
        text="AVES",
        description="Birds",
        meaning=NCBITAXON["8782"])
    ACTINOPTERYGII = PermissibleValue(
        text="ACTINOPTERYGII",
        description="Ray-finned fishes",
        meaning=NCBITAXON["7898"])
    AMPHIBIA = PermissibleValue(
        text="AMPHIBIA",
        description="Amphibians",
        meaning=NCBITAXON["8292"])
    ARTHROPODA = PermissibleValue(
        text="ARTHROPODA",
        description="Arthropods",
        meaning=NCBITAXON["6656"])
    INSECTA = PermissibleValue(
        text="INSECTA",
        description="Insects",
        meaning=NCBITAXON["50557"])
    NEMATODA = PermissibleValue(
        text="NEMATODA",
        description="Roundworms",
        meaning=NCBITAXON["6231"])
    FUNGI = PermissibleValue(
        text="FUNGI",
        description="Fungal kingdom",
        meaning=NCBITAXON["4751"])
    ASCOMYCOTA = PermissibleValue(
        text="ASCOMYCOTA",
        description="Sac fungi",
        meaning=NCBITAXON["4890"])
    VIRIDIPLANTAE = PermissibleValue(
        text="VIRIDIPLANTAE",
        description="Green plants",
        meaning=NCBITAXON["33090"])
    MAGNOLIOPHYTA = PermissibleValue(
        text="MAGNOLIOPHYTA",
        title="Magnoliopsida",
        description="Flowering plants",
        meaning=NCBITAXON["3398"])
    PROTEOBACTERIA = PermissibleValue(
        text="PROTEOBACTERIA",
        title="Pseudomonadota",
        description="Proteobacteria",
        meaning=NCBITAXON["1224"])
    GAMMAPROTEOBACTERIA = PermissibleValue(
        text="GAMMAPROTEOBACTERIA",
        description="Gamma proteobacteria",
        meaning=NCBITAXON["1236"])
    FIRMICUTES = PermissibleValue(
        text="FIRMICUTES",
        title="Bacillota",
        description="Firmicutes (Gram-positive bacteria)",
        meaning=NCBITAXON["1239"])
    ACTINOBACTERIA = PermissibleValue(
        text="ACTINOBACTERIA",
        title="Actinomycetota",
        description="Actinobacteria",
        meaning=NCBITAXON["201174"])
    EURYARCHAEOTA = PermissibleValue(
        text="EURYARCHAEOTA",
        title="Methanobacteriota",
        description="Euryarchaeota",
        meaning=NCBITAXON["28890"])
    APICOMPLEXA = PermissibleValue(
        text="APICOMPLEXA",
        description="Apicomplexan parasites",
        meaning=NCBITAXON["5794"])
    HUMAN = PermissibleValue(
        text="HUMAN",
        title="Homo sapiens",
        description="Homo sapiens (human)",
        meaning=NCBITAXON["9606"])
    MOUSE = PermissibleValue(
        text="MOUSE",
        title="Mus musculus",
        description="Mus musculus (house mouse)",
        meaning=NCBITAXON["10090"])
    RAT = PermissibleValue(
        text="RAT",
        title="Rattus norvegicus",
        description="Rattus norvegicus (Norway rat)",
        meaning=NCBITAXON["10116"])
    RHESUS = PermissibleValue(
        text="RHESUS",
        title="Macaca mulatta",
        description="Macaca mulatta (rhesus macaque)",
        meaning=NCBITAXON["9544"])
    CHIMP = PermissibleValue(
        text="CHIMP",
        title="Pan troglodytes",
        description="Pan troglodytes (chimpanzee)",
        meaning=NCBITAXON["9598"])
    DOG = PermissibleValue(
        text="DOG",
        title="Canis lupus familiaris",
        description="Canis lupus familiaris (dog)",
        meaning=NCBITAXON["9615"])
    COW = PermissibleValue(
        text="COW",
        title="Bos taurus",
        description="Bos taurus (cattle)",
        meaning=NCBITAXON["9913"])
    PIG = PermissibleValue(
        text="PIG",
        title="Sus scrofa",
        description="Sus scrofa (pig)",
        meaning=NCBITAXON["9823"])
    CHICKEN = PermissibleValue(
        text="CHICKEN",
        title="Gallus gallus",
        description="Gallus gallus (chicken)",
        meaning=NCBITAXON["9031"])
    ZEBRAFISH = PermissibleValue(
        text="ZEBRAFISH",
        title="Danio rerio",
        description="Danio rerio (zebrafish)",
        meaning=NCBITAXON["7955"])
    MEDAKA = PermissibleValue(
        text="MEDAKA",
        title="Oryzias latipes",
        description="Oryzias latipes (Japanese medaka)",
        meaning=NCBITAXON["8090"])
    PUFFERFISH = PermissibleValue(
        text="PUFFERFISH",
        title="Takifugu rubripes",
        description="Takifugu rubripes (torafugu)",
        meaning=NCBITAXON["31033"])
    XENOPUS_TROPICALIS = PermissibleValue(
        text="XENOPUS_TROPICALIS",
        description="Xenopus tropicalis (western clawed frog)",
        meaning=NCBITAXON["8364"])
    XENOPUS_LAEVIS = PermissibleValue(
        text="XENOPUS_LAEVIS",
        description="Xenopus laevis (African clawed frog)",
        meaning=NCBITAXON["8355"])
    DROSOPHILA = PermissibleValue(
        text="DROSOPHILA",
        title="Drosophila melanogaster",
        description="Drosophila melanogaster (fruit fly)",
        meaning=NCBITAXON["7227"])
    C_ELEGANS = PermissibleValue(
        text="C_ELEGANS",
        title="Caenorhabditis elegans",
        description="Caenorhabditis elegans (roundworm)",
        meaning=NCBITAXON["6239"])
    S_CEREVISIAE = PermissibleValue(
        text="S_CEREVISIAE",
        title="Saccharomyces cerevisiae",
        description="Saccharomyces cerevisiae (baker's yeast)",
        meaning=NCBITAXON["4932"])
    S_CEREVISIAE_S288C = PermissibleValue(
        text="S_CEREVISIAE_S288C",
        title="Saccharomyces cerevisiae S288C",
        description="Saccharomyces cerevisiae S288C (reference strain)",
        meaning=NCBITAXON["559292"])
    S_POMBE = PermissibleValue(
        text="S_POMBE",
        title="Schizosaccharomyces pombe",
        description="Schizosaccharomyces pombe (fission yeast)",
        meaning=NCBITAXON["4896"])
    C_ALBICANS = PermissibleValue(
        text="C_ALBICANS",
        title="Candida albicans",
        description="Candida albicans (pathogenic yeast)",
        meaning=NCBITAXON["5476"])
    A_NIDULANS = PermissibleValue(
        text="A_NIDULANS",
        title="Aspergillus nidulans",
        description="Aspergillus nidulans (filamentous fungus)",
        meaning=NCBITAXON["162425"])
    N_CRASSA = PermissibleValue(
        text="N_CRASSA",
        title="Neurospora crassa",
        description="Neurospora crassa (red bread mold)",
        meaning=NCBITAXON["5141"])
    ARABIDOPSIS = PermissibleValue(
        text="ARABIDOPSIS",
        title="Arabidopsis thaliana",
        description="Arabidopsis thaliana (thale cress)",
        meaning=NCBITAXON["3702"])
    RICE = PermissibleValue(
        text="RICE",
        title="Oryza sativa",
        description="Oryza sativa (rice)",
        meaning=NCBITAXON["4530"])
    MAIZE = PermissibleValue(
        text="MAIZE",
        title="Zea mays",
        description="Zea mays (corn)",
        meaning=NCBITAXON["4577"])
    TOMATO = PermissibleValue(
        text="TOMATO",
        title="Solanum lycopersicum",
        description="Solanum lycopersicum (tomato)",
        meaning=NCBITAXON["4081"])
    TOBACCO = PermissibleValue(
        text="TOBACCO",
        title="Nicotiana tabacum",
        description="Nicotiana tabacum (tobacco)",
        meaning=NCBITAXON["4097"])
    E_COLI = PermissibleValue(
        text="E_COLI",
        title="Escherichia coli",
        description="Escherichia coli",
        meaning=NCBITAXON["562"])
    E_COLI_K12 = PermissibleValue(
        text="E_COLI_K12",
        title="Escherichia coli K-12",
        description="Escherichia coli str. K-12",
        meaning=NCBITAXON["83333"])
    B_SUBTILIS = PermissibleValue(
        text="B_SUBTILIS",
        title="Bacillus subtilis",
        description="Bacillus subtilis",
        meaning=NCBITAXON["1423"])
    M_TUBERCULOSIS = PermissibleValue(
        text="M_TUBERCULOSIS",
        title="Mycobacterium tuberculosis",
        description="Mycobacterium tuberculosis",
        meaning=NCBITAXON["1773"])
    P_AERUGINOSA = PermissibleValue(
        text="P_AERUGINOSA",
        title="Pseudomonas aeruginosa",
        description="Pseudomonas aeruginosa",
        meaning=NCBITAXON["287"])
    S_AUREUS = PermissibleValue(
        text="S_AUREUS",
        title="Staphylococcus aureus",
        description="Staphylococcus aureus",
        meaning=NCBITAXON["1280"])
    S_PNEUMONIAE = PermissibleValue(
        text="S_PNEUMONIAE",
        title="Streptococcus pneumoniae",
        description="Streptococcus pneumoniae",
        meaning=NCBITAXON["1313"])
    H_PYLORI = PermissibleValue(
        text="H_PYLORI",
        title="Helicobacter pylori",
        description="Helicobacter pylori",
        meaning=NCBITAXON["210"])
    M_JANNASCHII = PermissibleValue(
        text="M_JANNASCHII",
        title="Methanocaldococcus jannaschii",
        description="Methanocaldococcus jannaschii",
        meaning=NCBITAXON["2190"])
    H_SALINARUM = PermissibleValue(
        text="H_SALINARUM",
        title="Halobacterium salinarum",
        description="Halobacterium salinarum",
        meaning=NCBITAXON["2242"])
    P_FALCIPARUM = PermissibleValue(
        text="P_FALCIPARUM",
        title="Plasmodium falciparum",
        description="Plasmodium falciparum (malaria parasite)",
        meaning=NCBITAXON["5833"])
    T_GONDII = PermissibleValue(
        text="T_GONDII",
        title="Toxoplasma gondii",
        description="Toxoplasma gondii",
        meaning=NCBITAXON["5811"])
    T_BRUCEI = PermissibleValue(
        text="T_BRUCEI",
        title="Trypanosoma brucei",
        description="Trypanosoma brucei",
        meaning=NCBITAXON["5691"])
    DICTYOSTELIUM = PermissibleValue(
        text="DICTYOSTELIUM",
        title="Dictyostelium discoideum",
        description="Dictyostelium discoideum (slime mold)",
        meaning=NCBITAXON["44689"])
    TETRAHYMENA = PermissibleValue(
        text="TETRAHYMENA",
        title="Tetrahymena thermophila",
        description="Tetrahymena thermophila",
        meaning=NCBITAXON["5911"])
    PARAMECIUM = PermissibleValue(
        text="PARAMECIUM",
        title="Paramecium tetraurelia",
        description="Paramecium tetraurelia",
        meaning=NCBITAXON["5888"])
    CHLAMYDOMONAS = PermissibleValue(
        text="CHLAMYDOMONAS",
        title="Chlamydomonas reinhardtii",
        description="Chlamydomonas reinhardtii (green alga)",
        meaning=NCBITAXON["3055"])
    PHAGE_LAMBDA = PermissibleValue(
        text="PHAGE_LAMBDA",
        title="Lambdavirus lambda",
        description="Escherichia phage lambda",
        meaning=NCBITAXON["10710"])
    HIV1 = PermissibleValue(
        text="HIV1",
        title="Human immunodeficiency virus 1",
        description="Human immunodeficiency virus 1",
        meaning=NCBITAXON["11676"])
    INFLUENZA_A = PermissibleValue(
        text="INFLUENZA_A",
        title="Influenza A virus",
        description="Influenza A virus",
        meaning=NCBITAXON["11320"])
    SARS_COV_2 = PermissibleValue(
        text="SARS_COV_2",
        title="Severe acute respiratory syndrome coronavirus 2",
        description="Severe acute respiratory syndrome coronavirus 2",
        meaning=NCBITAXON["2697049"])

    _defn = EnumDefinition(
        name="CommonOrganismTaxaEnum",
        description="Common model organisms used in biological research, mapped to NCBI Taxonomy IDs",
    )

class TaxonomicRank(EnumDefinitionImpl):
    """
    Standard taxonomic ranks used in biological classification
    """
    DOMAIN = PermissibleValue(
        text="DOMAIN",
        description="Domain (highest rank)",
        meaning=TAXRANK["0000037"])
    KINGDOM = PermissibleValue(
        text="KINGDOM",
        description="Kingdom",
        meaning=TAXRANK["0000017"])
    PHYLUM = PermissibleValue(
        text="PHYLUM",
        description="Phylum (animals, plants, fungi) or Division (plants)",
        meaning=TAXRANK["0000001"])
    CLASS = PermissibleValue(
        text="CLASS",
        description="Class",
        meaning=TAXRANK["0000002"])
    ORDER = PermissibleValue(
        text="ORDER",
        description="Order",
        meaning=TAXRANK["0000003"])
    FAMILY = PermissibleValue(
        text="FAMILY",
        description="Family",
        meaning=TAXRANK["0000004"])
    GENUS = PermissibleValue(
        text="GENUS",
        description="Genus",
        meaning=TAXRANK["0000005"])
    SPECIES = PermissibleValue(
        text="SPECIES",
        description="Species",
        meaning=TAXRANK["0000006"])
    SUBSPECIES = PermissibleValue(
        text="SUBSPECIES",
        description="Subspecies",
        meaning=TAXRANK["0000023"])
    STRAIN = PermissibleValue(
        text="STRAIN",
        description="Strain (especially for microorganisms)",
        meaning=TAXRANK["0001001"])
    VARIETY = PermissibleValue(
        text="VARIETY",
        title="varietas",
        description="Variety (mainly plants)",
        meaning=TAXRANK["0000016"])
    FORM = PermissibleValue(
        text="FORM",
        title="forma",
        description="Form (mainly plants)",
        meaning=TAXRANK["0000026"])
    CULTIVAR = PermissibleValue(
        text="CULTIVAR",
        description="Cultivar (cultivated variety)",
        meaning=TAXRANK["0000034"])

    _defn = EnumDefinition(
        name="TaxonomicRank",
        description="Standard taxonomic ranks used in biological classification",
    )

class BiologicalKingdom(EnumDefinitionImpl):
    """
    Major kingdoms/domains of life
    """
    BACTERIA = PermissibleValue(
        text="BACTERIA",
        description="Bacteria domain",
        meaning=NCBITAXON["2"])
    ARCHAEA = PermissibleValue(
        text="ARCHAEA",
        description="Archaea domain",
        meaning=NCBITAXON["2157"])
    EUKARYOTA = PermissibleValue(
        text="EUKARYOTA",
        description="Eukaryota domain",
        meaning=NCBITAXON["2759"])
    ANIMALIA = PermissibleValue(
        text="ANIMALIA",
        title="Metazoa",
        description="Animal kingdom",
        meaning=NCBITAXON["33208"])
    PLANTAE = PermissibleValue(
        text="PLANTAE",
        title="Viridiplantae",
        description="Plant kingdom (Viridiplantae)",
        meaning=NCBITAXON["33090"])
    FUNGI = PermissibleValue(
        text="FUNGI",
        description="Fungal kingdom",
        meaning=NCBITAXON["4751"])
    PROTISTA = PermissibleValue(
        text="PROTISTA",
        description="Protist kingdom (polyphyletic group)")
    VIRUSES = PermissibleValue(
        text="VIRUSES",
        description="Viruses (not a true kingdom)",
        meaning=NCBITAXON["10239"])

    _defn = EnumDefinition(
        name="BiologicalKingdom",
        description="Major kingdoms/domains of life",
    )

class CellCyclePhase(EnumDefinitionImpl):
    """
    Major phases of the eukaryotic cell cycle
    """
    G0 = PermissibleValue(
        text="G0",
        title="cell quiescence",
        description="G0 phase (quiescent/resting phase)",
        meaning=GO["0044838"])
    G1 = PermissibleValue(
        text="G1",
        title="G1 phase",
        description="G1 phase (Gap 1)",
        meaning=GO["0051318"])
    S = PermissibleValue(
        text="S",
        title="S phase",
        description="S phase (DNA synthesis)",
        meaning=GO["0051320"])
    G2 = PermissibleValue(
        text="G2",
        title="G2 phase",
        description="G2 phase (Gap 2)",
        meaning=GO["0051319"])
    M = PermissibleValue(
        text="M",
        title="M phase",
        description="M phase (mitosis and cytokinesis)",
        meaning=GO["0000279"])
    INTERPHASE = PermissibleValue(
        text="INTERPHASE",
        description="Interphase (G1, S, and G2 phases combined)",
        meaning=GO["0051325"])

    _defn = EnumDefinition(
        name="CellCyclePhase",
        description="Major phases of the eukaryotic cell cycle",
    )

class MitoticPhase(EnumDefinitionImpl):
    """
    Stages of mitosis (M phase)
    """
    PROPHASE = PermissibleValue(
        text="PROPHASE",
        description="Prophase",
        meaning=GO["0051324"])
    PROMETAPHASE = PermissibleValue(
        text="PROMETAPHASE",
        title="mitotic metaphase chromosome alignment",
        description="Prometaphase",
        meaning=GO["0007080"])
    METAPHASE = PermissibleValue(
        text="METAPHASE",
        description="Metaphase",
        meaning=GO["0051323"])
    ANAPHASE = PermissibleValue(
        text="ANAPHASE",
        description="Anaphase",
        meaning=GO["0051322"])
    TELOPHASE = PermissibleValue(
        text="TELOPHASE",
        description="Telophase",
        meaning=GO["0051326"])
    CYTOKINESIS = PermissibleValue(
        text="CYTOKINESIS",
        description="Cytokinesis",
        meaning=GO["0000910"])

    _defn = EnumDefinition(
        name="MitoticPhase",
        description="Stages of mitosis (M phase)",
    )

class CellCycleCheckpoint(EnumDefinitionImpl):
    """
    Cell cycle checkpoints that regulate progression
    """
    G1_S_CHECKPOINT = PermissibleValue(
        text="G1_S_CHECKPOINT",
        title="G1/S transition of mitotic cell cycle",
        description="G1/S checkpoint (Restriction point)",
        meaning=GO["0000082"])
    INTRA_S_CHECKPOINT = PermissibleValue(
        text="INTRA_S_CHECKPOINT",
        title="mitotic intra-S DNA damage checkpoint signaling",
        description="Intra-S checkpoint",
        meaning=GO["0031573"])
    G2_M_CHECKPOINT = PermissibleValue(
        text="G2_M_CHECKPOINT",
        title="mitotic G1 DNA damage checkpoint signaling",
        description="G2/M checkpoint",
        meaning=GO["0031571"])
    SPINDLE_CHECKPOINT = PermissibleValue(
        text="SPINDLE_CHECKPOINT",
        title="spindle checkpoint signaling",
        description="Spindle checkpoint (M checkpoint)",
        meaning=GO["0031577"])

    _defn = EnumDefinition(
        name="CellCycleCheckpoint",
        description="Cell cycle checkpoints that regulate progression",
    )

class MeioticPhase(EnumDefinitionImpl):
    """
    Phases specific to meiotic cell division
    """
    MEIOSIS_I = PermissibleValue(
        text="MEIOSIS_I",
        description="Meiosis I (reductional division)",
        meaning=GO["0007127"])
    PROPHASE_I = PermissibleValue(
        text="PROPHASE_I",
        title="meiotic prophase I",
        description="Prophase I",
        meaning=GO["0007128"])
    METAPHASE_I = PermissibleValue(
        text="METAPHASE_I",
        title="meiotic metaphase I",
        description="Metaphase I",
        meaning=GO["0007132"])
    ANAPHASE_I = PermissibleValue(
        text="ANAPHASE_I",
        title="meiotic anaphase I",
        description="Anaphase I",
        meaning=GO["0007133"])
    TELOPHASE_I = PermissibleValue(
        text="TELOPHASE_I",
        title="meiotic telophase I",
        description="Telophase I",
        meaning=GO["0007134"])
    MEIOSIS_II = PermissibleValue(
        text="MEIOSIS_II",
        description="Meiosis II (equational division)",
        meaning=GO["0007135"])
    PROPHASE_II = PermissibleValue(
        text="PROPHASE_II",
        title="meiotic prophase II",
        description="Prophase II",
        meaning=GO["0007136"])
    METAPHASE_II = PermissibleValue(
        text="METAPHASE_II",
        title="meiotic metaphase II",
        description="Metaphase II",
        meaning=GO["0007137"])
    ANAPHASE_II = PermissibleValue(
        text="ANAPHASE_II",
        title="meiotic anaphase II",
        description="Anaphase II",
        meaning=GO["0007138"])
    TELOPHASE_II = PermissibleValue(
        text="TELOPHASE_II",
        title="meiotic telophase II",
        description="Telophase II",
        meaning=GO["0007139"])

    _defn = EnumDefinition(
        name="MeioticPhase",
        description="Phases specific to meiotic cell division",
    )

class CellCycleRegulator(EnumDefinitionImpl):
    """
    Types of cell cycle regulatory molecules
    """
    CYCLIN = PermissibleValue(
        text="CYCLIN",
        title="cyclin-dependent protein serine/threonine kinase regulator activity",
        description="Cyclin proteins",
        meaning=GO["0016538"])
    CDK = PermissibleValue(
        text="CDK",
        title="cyclin-dependent protein serine/threonine kinase activity",
        description="Cyclin-dependent kinase",
        meaning=GO["0004693"])
    CDK_INHIBITOR = PermissibleValue(
        text="CDK_INHIBITOR",
        title="cyclin-dependent protein serine/threonine kinase inhibitor activity",
        description="CDK inhibitor",
        meaning=GO["0004861"])
    CHECKPOINT_KINASE = PermissibleValue(
        text="CHECKPOINT_KINASE",
        title="DNA damage checkpoint signaling",
        description="Checkpoint kinase",
        meaning=GO["0000077"])
    TUMOR_SUPPRESSOR = PermissibleValue(
        text="TUMOR_SUPPRESSOR",
        title="regulation of cell cycle",
        description="Tumor suppressor involved in cell cycle",
        meaning=GO["0051726"])
    E3_UBIQUITIN_LIGASE = PermissibleValue(
        text="E3_UBIQUITIN_LIGASE",
        title="obsolete positive regulation of ubiquitin-protein ligase activity involved in regulation of mitotic cell cycle transition",
        description="E3 ubiquitin ligase (cell cycle)",
        meaning=GO["0051437"])
    PHOSPHATASE = PermissibleValue(
        text="PHOSPHATASE",
        title="phosphoprotein phosphatase activity",
        description="Cell cycle phosphatase",
        meaning=GO["0004721"])

    _defn = EnumDefinition(
        name="CellCycleRegulator",
        description="Types of cell cycle regulatory molecules",
    )

class CellProliferationState(EnumDefinitionImpl):
    """
    Cell proliferation and growth states
    """
    PROLIFERATING = PermissibleValue(
        text="PROLIFERATING",
        title="cell population proliferation",
        description="Actively proliferating cells",
        meaning=GO["0008283"])
    QUIESCENT = PermissibleValue(
        text="QUIESCENT",
        title="cell quiescence",
        description="Quiescent cells (reversibly non-dividing)",
        meaning=GO["0044838"])
    SENESCENT = PermissibleValue(
        text="SENESCENT",
        title="cellular senescence",
        description="Senescent cells (permanently non-dividing)",
        meaning=GO["0090398"])
    DIFFERENTIATED = PermissibleValue(
        text="DIFFERENTIATED",
        title="cell differentiation",
        description="Terminally differentiated cells",
        meaning=GO["0030154"])
    APOPTOTIC = PermissibleValue(
        text="APOPTOTIC",
        title="apoptotic process",
        description="Cells undergoing apoptosis",
        meaning=GO["0006915"])
    NECROTIC = PermissibleValue(
        text="NECROTIC",
        title="obsolete necrotic cell death",
        description="Cells undergoing necrosis",
        meaning=GO["0070265"])

    _defn = EnumDefinition(
        name="CellProliferationState",
        description="Cell proliferation and growth states",
    )

class DNADamageResponse(EnumDefinitionImpl):
    """
    DNA damage response pathways during cell cycle
    """
    CELL_CYCLE_ARREST = PermissibleValue(
        text="CELL_CYCLE_ARREST",
        description="Cell cycle arrest",
        meaning=GO["0051726"])
    DNA_REPAIR = PermissibleValue(
        text="DNA_REPAIR",
        description="DNA repair",
        meaning=GO["0006281"])
    APOPTOSIS_INDUCTION = PermissibleValue(
        text="APOPTOSIS_INDUCTION",
        description="Induction of apoptosis",
        meaning=GO["0043065"])
    SENESCENCE_INDUCTION = PermissibleValue(
        text="SENESCENCE_INDUCTION",
        title="stress-induced premature senescence",
        description="Induction of senescence",
        meaning=GO["0090400"])
    CHECKPOINT_ADAPTATION = PermissibleValue(
        text="CHECKPOINT_ADAPTATION",
        description="Checkpoint adaptation")

    _defn = EnumDefinition(
        name="DNADamageResponse",
        description="DNA damage response pathways during cell cycle",
    )

class GenomeFeatureType(EnumDefinitionImpl):
    """
    Genome feature types from SOFA (Sequence Ontology Feature Annotation).
    This is the subset of Sequence Ontology terms used in GFF3 files.
    Organized hierarchically following the Sequence Ontology structure.
    """
    REGION = PermissibleValue(
        text="REGION",
        description="A sequence feature with an extent greater than zero",
        meaning=SO["0000001"])
    BIOLOGICAL_REGION = PermissibleValue(
        text="BIOLOGICAL_REGION",
        description="A region defined by its biological properties",
        meaning=SO["0001411"])
    GENE = PermissibleValue(
        text="GENE",
        description="""A region (or regions) that includes all of the sequence elements necessary to encode a functional transcript""",
        meaning=SO["0000704"])
    TRANSCRIPT = PermissibleValue(
        text="TRANSCRIPT",
        description="An RNA synthesized on a DNA or RNA template by an RNA polymerase",
        meaning=SO["0000673"])
    PRIMARY_TRANSCRIPT = PermissibleValue(
        text="PRIMARY_TRANSCRIPT",
        description="A transcript that has not been processed",
        meaning=SO["0000185"])
    MRNA = PermissibleValue(
        text="MRNA",
        description="Messenger RNA; includes 5'UTR, coding sequences and 3'UTR",
        meaning=SO["0000234"])
    EXON = PermissibleValue(
        text="EXON",
        description="""A region of the transcript sequence within a gene which is not removed from the primary RNA transcript by RNA splicing""",
        meaning=SO["0000147"])
    CDS = PermissibleValue(
        text="CDS",
        description="""Coding sequence; sequence of nucleotides that corresponds with the sequence of amino acids in a protein""",
        meaning=SO["0000316"])
    INTRON = PermissibleValue(
        text="INTRON",
        description="""A region of a primary transcript that is transcribed, but removed from within the transcript by splicing""",
        meaning=SO["0000188"])
    FIVE_PRIME_UTR = PermissibleValue(
        text="FIVE_PRIME_UTR",
        description="5' untranslated region",
        meaning=SO["0000204"])
    THREE_PRIME_UTR = PermissibleValue(
        text="THREE_PRIME_UTR",
        description="3' untranslated region",
        meaning=SO["0000205"])
    NCRNA = PermissibleValue(
        text="NCRNA",
        description="Non-protein coding RNA",
        meaning=SO["0000655"])
    RRNA = PermissibleValue(
        text="RRNA",
        description="Ribosomal RNA",
        meaning=SO["0000252"])
    TRNA = PermissibleValue(
        text="TRNA",
        description="Transfer RNA",
        meaning=SO["0000253"])
    SNRNA = PermissibleValue(
        text="SNRNA",
        description="Small nuclear RNA",
        meaning=SO["0000274"])
    SNORNA = PermissibleValue(
        text="SNORNA",
        description="Small nucleolar RNA",
        meaning=SO["0000275"])
    MIRNA = PermissibleValue(
        text="MIRNA",
        description="MicroRNA",
        meaning=SO["0000276"])
    LNCRNA = PermissibleValue(
        text="LNCRNA",
        description="Long non-coding RNA",
        meaning=SO["0001877"])
    RIBOZYME = PermissibleValue(
        text="RIBOZYME",
        description="An RNA with catalytic activity",
        meaning=SO["0000374"])
    ANTISENSE_RNA = PermissibleValue(
        text="ANTISENSE_RNA",
        description="RNA that is complementary to other RNA",
        meaning=SO["0000644"])
    PSEUDOGENE = PermissibleValue(
        text="PSEUDOGENE",
        description="""A sequence that closely resembles a known functional gene but does not produce a functional product""",
        meaning=SO["0000336"])
    PROCESSED_PSEUDOGENE = PermissibleValue(
        text="PROCESSED_PSEUDOGENE",
        description="A pseudogene arising from reverse transcription of mRNA",
        meaning=SO["0000043"])
    REGULATORY_REGION = PermissibleValue(
        text="REGULATORY_REGION",
        description="A region involved in the control of the process of gene expression",
        meaning=SO["0005836"])
    PROMOTER = PermissibleValue(
        text="PROMOTER",
        description="A regulatory region initiating transcription",
        meaning=SO["0000167"])
    ENHANCER = PermissibleValue(
        text="ENHANCER",
        description="A cis-acting sequence that increases transcription",
        meaning=SO["0000165"])
    SILENCER = PermissibleValue(
        text="SILENCER",
        description="A regulatory region which upon binding of transcription factors, suppresses transcription",
        meaning=SO["0000625"])
    TERMINATOR = PermissibleValue(
        text="TERMINATOR",
        description="""The sequence of DNA located either at the end of the transcript that causes RNA polymerase to terminate transcription""",
        meaning=SO["0000141"])
    ATTENUATOR = PermissibleValue(
        text="ATTENUATOR",
        description="A sequence that causes transcription termination",
        meaning=SO["0000140"])
    POLYA_SIGNAL_SEQUENCE = PermissibleValue(
        text="POLYA_SIGNAL_SEQUENCE",
        description="The recognition sequence for the cleavage and polyadenylation machinery",
        meaning=SO["0000551"])
    BINDING_SITE = PermissibleValue(
        text="BINDING_SITE",
        description="A region on a molecule that binds to another molecule",
        meaning=SO["0000409"])
    TFBS = PermissibleValue(
        text="TFBS",
        title="TF_binding_site",
        description="Transcription factor binding site",
        meaning=SO["0000235"])
    RIBOSOME_ENTRY_SITE = PermissibleValue(
        text="RIBOSOME_ENTRY_SITE",
        description="Region where ribosome assembles on mRNA",
        meaning=SO["0000139"])
    POLYA_SITE = PermissibleValue(
        text="POLYA_SITE",
        description="Polyadenylation site",
        meaning=SO["0000553"])
    REPEAT_REGION = PermissibleValue(
        text="REPEAT_REGION",
        description="A region of sequence containing one or more repeat units",
        meaning=SO["0000657"])
    DISPERSED_REPEAT = PermissibleValue(
        text="DISPERSED_REPEAT",
        description="A repeat that is interspersed in the genome",
        meaning=SO["0000658"])
    TANDEM_REPEAT = PermissibleValue(
        text="TANDEM_REPEAT",
        description="A repeat where the same sequence is repeated in the same orientation",
        meaning=SO["0000705"])
    INVERTED_REPEAT = PermissibleValue(
        text="INVERTED_REPEAT",
        description="A repeat where the sequence is repeated in the opposite orientation",
        meaning=SO["0000294"])
    TRANSPOSABLE_ELEMENT = PermissibleValue(
        text="TRANSPOSABLE_ELEMENT",
        description="A DNA segment that can change its position within the genome",
        meaning=SO["0000101"])
    MOBILE_ELEMENT = PermissibleValue(
        text="MOBILE_ELEMENT",
        title="mobile_genetic_element",
        description="A nucleotide region with the ability to move from one place in the genome to another",
        meaning=SO["0001037"])
    SEQUENCE_ALTERATION = PermissibleValue(
        text="SEQUENCE_ALTERATION",
        description="A sequence that deviates from the reference sequence",
        meaning=SO["0001059"])
    INSERTION = PermissibleValue(
        text="INSERTION",
        description="The sequence of one or more nucleotides added between two adjacent nucleotides",
        meaning=SO["0000667"])
    DELETION = PermissibleValue(
        text="DELETION",
        description="The removal of a sequences of nucleotides from the genome",
        meaning=SO["0000159"])
    INVERSION = PermissibleValue(
        text="INVERSION",
        description="A continuous nucleotide sequence is inverted in the same position",
        meaning=SO["1000036"])
    DUPLICATION = PermissibleValue(
        text="DUPLICATION",
        description="One or more nucleotides are added between two adjacent nucleotides",
        meaning=SO["1000035"])
    SUBSTITUTION = PermissibleValue(
        text="SUBSTITUTION",
        description="A sequence alteration where one nucleotide replaced by another",
        meaning=SO["1000002"])
    ORIGIN_OF_REPLICATION = PermissibleValue(
        text="ORIGIN_OF_REPLICATION",
        description="The origin of replication; starting site for duplication of a nucleic acid molecule",
        meaning=SO["0000296"])
    POLYC_TRACT = PermissibleValue(
        text="POLYC_TRACT",
        description="A sequence of Cs")
    GAP = PermissibleValue(
        text="GAP",
        description="A gap in the sequence",
        meaning=SO["0000730"])
    ASSEMBLY_GAP = PermissibleValue(
        text="ASSEMBLY_GAP",
        title="gap",
        description="A gap between two sequences in an assembly",
        meaning=SO["0000730"])
    CHROMOSOME = PermissibleValue(
        text="CHROMOSOME",
        description="Structural unit composed of DNA and proteins",
        meaning=SO["0000340"])
    SUPERCONTIG = PermissibleValue(
        text="SUPERCONTIG",
        description="One or more contigs that have been ordered and oriented using end-read information",
        meaning=SO["0000148"])
    CONTIG = PermissibleValue(
        text="CONTIG",
        description="A contiguous sequence derived from sequence assembly",
        meaning=SO["0000149"])
    SCAFFOLD = PermissibleValue(
        text="SCAFFOLD",
        title="supercontig",
        description="One or more contigs that have been ordered and oriented",
        meaning=SO["0000148"])
    CLONE = PermissibleValue(
        text="CLONE",
        description="A piece of DNA that has been inserted into a vector",
        meaning=SO["0000151"])
    PLASMID = PermissibleValue(
        text="PLASMID",
        description="A self-replicating circular DNA molecule",
        meaning=SO["0000155"])
    POLYPEPTIDE = PermissibleValue(
        text="POLYPEPTIDE",
        description="A sequence of amino acids linked by peptide bonds",
        meaning=SO["0000104"])
    MATURE_PROTEIN_REGION = PermissibleValue(
        text="MATURE_PROTEIN_REGION",
        description="The polypeptide sequence that remains after post-translational processing",
        meaning=SO["0000419"])
    SIGNAL_PEPTIDE = PermissibleValue(
        text="SIGNAL_PEPTIDE",
        description="A peptide region that targets a polypeptide to a specific location",
        meaning=SO["0000418"])
    TRANSIT_PEPTIDE = PermissibleValue(
        text="TRANSIT_PEPTIDE",
        description="A peptide that directs the transport of a protein to an organelle",
        meaning=SO["0000725"])
    PROPEPTIDE = PermissibleValue(
        text="PROPEPTIDE",
        title="propeptide",
        description="A peptide region that is cleaved during maturation",
        meaning=SO["0001062"])
    OPERON = PermissibleValue(
        text="OPERON",
        description="A group of contiguous genes transcribed as a single unit",
        meaning=SO["0000178"])
    STEM_LOOP = PermissibleValue(
        text="STEM_LOOP",
        description="A double-helical region formed by base-pairing between adjacent sequences",
        meaning=SO["0000313"])
    D_LOOP = PermissibleValue(
        text="D_LOOP",
        description="Displacement loop; a region where DNA is displaced by an invading strand",
        meaning=SO["0000297"])
    MATCH = PermissibleValue(
        text="MATCH",
        description="A region of sequence similarity",
        meaning=SO["0000343"])
    CDNA_MATCH = PermissibleValue(
        text="CDNA_MATCH",
        description="A match to a cDNA sequence",
        meaning=SO["0000689"])
    EST_MATCH = PermissibleValue(
        text="EST_MATCH",
        description="A match to an EST sequence",
        meaning=SO["0000668"])
    PROTEIN_MATCH = PermissibleValue(
        text="PROTEIN_MATCH",
        description="A match to a protein sequence",
        meaning=SO["0000349"])
    NUCLEOTIDE_MATCH = PermissibleValue(
        text="NUCLEOTIDE_MATCH",
        description="A match to a nucleotide sequence",
        meaning=SO["0000347"])
    JUNCTION_FEATURE = PermissibleValue(
        text="JUNCTION_FEATURE",
        title="junction",
        description="A boundary or junction between sequence regions",
        meaning=SO["0000699"])
    SPLICE_SITE = PermissibleValue(
        text="SPLICE_SITE",
        description="The position where intron is excised",
        meaning=SO["0000162"])
    FIVE_PRIME_SPLICE_SITE = PermissibleValue(
        text="FIVE_PRIME_SPLICE_SITE",
        title="five_prime_cis_splice_site",
        description="The 5' splice site (donor site)",
        meaning=SO["0000163"])
    THREE_PRIME_SPLICE_SITE = PermissibleValue(
        text="THREE_PRIME_SPLICE_SITE",
        title="three_prime_cis_splice_site",
        description="The 3' splice site (acceptor site)",
        meaning=SO["0000164"])
    START_CODON = PermissibleValue(
        text="START_CODON",
        description="The first codon to be translated",
        meaning=SO["0000318"])
    STOP_CODON = PermissibleValue(
        text="STOP_CODON",
        description="The codon that terminates translation",
        meaning=SO["0000319"])
    CENTROMERE = PermissibleValue(
        text="CENTROMERE",
        description="A region where chromatids are held together",
        meaning=SO["0000577"])
    TELOMERE = PermissibleValue(
        text="TELOMERE",
        description="The terminal region of a linear chromosome",
        meaning=SO["0000624"])

    _defn = EnumDefinition(
        name="GenomeFeatureType",
        description="""Genome feature types from SOFA (Sequence Ontology Feature Annotation).
This is the subset of Sequence Ontology terms used in GFF3 files.
Organized hierarchically following the Sequence Ontology structure.""",
    )

class MetazoanAnatomicalStructure(EnumDefinitionImpl):
    """
    Any anatomical structure found in metazoan organisms,
    including organs, tissues, and body parts
    """
    _defn = EnumDefinition(
        name="MetazoanAnatomicalStructure",
        description="""Any anatomical structure found in metazoan organisms,
including organs, tissues, and body parts""",
    )

class HumanAnatomicalStructure(EnumDefinitionImpl):
    """
    Anatomical structures specific to humans (Homo sapiens)
    """
    _defn = EnumDefinition(
        name="HumanAnatomicalStructure",
        description="Anatomical structures specific to humans (Homo sapiens)",
    )

class PlantAnatomicalStructure(EnumDefinitionImpl):
    """
    Any anatomical structure found in plant organisms
    """
    _defn = EnumDefinition(
        name="PlantAnatomicalStructure",
        description="Any anatomical structure found in plant organisms",
    )

class CellType(EnumDefinitionImpl):
    """
    Any cell type from the Cell Ontology (CL),
    including native and experimentally modified cells
    """
    _defn = EnumDefinition(
        name="CellType",
        description="""Any cell type from the Cell Ontology (CL),
including native and experimentally modified cells""",
    )

class NeuronType(EnumDefinitionImpl):
    """
    Neuron cell types from the Cell Ontology
    """
    _defn = EnumDefinition(
        name="NeuronType",
        description="Neuron cell types from the Cell Ontology",
    )

class ImmuneCell(EnumDefinitionImpl):
    """
    Immune system cell types (leukocytes and their subtypes)
    """
    _defn = EnumDefinition(
        name="ImmuneCell",
        description="Immune system cell types (leukocytes and their subtypes)",
    )

class StemCell(EnumDefinitionImpl):
    """
    Stem cell types and progenitor cells
    """
    _defn = EnumDefinition(
        name="StemCell",
        description="Stem cell types and progenitor cells",
    )

class Disease(EnumDefinitionImpl):
    """
    Human diseases from the Mondo Disease Ontology
    """
    _defn = EnumDefinition(
        name="Disease",
        description="Human diseases from the Mondo Disease Ontology",
    )

class InfectiousDisease(EnumDefinitionImpl):
    """
    Infectious diseases caused by pathogenic organisms
    """
    _defn = EnumDefinition(
        name="InfectiousDisease",
        description="Infectious diseases caused by pathogenic organisms",
    )

class Cancer(EnumDefinitionImpl):
    """
    Neoplastic and cancerous diseases
    """
    _defn = EnumDefinition(
        name="Cancer",
        description="Neoplastic and cancerous diseases",
    )

class GeneticDisease(EnumDefinitionImpl):
    """
    Hereditary and genetic diseases
    """
    _defn = EnumDefinition(
        name="GeneticDisease",
        description="Hereditary and genetic diseases",
    )

class ChemicalEntity(EnumDefinitionImpl):
    """
    Any chemical entity from ChEBI ontology
    """
    _defn = EnumDefinition(
        name="ChemicalEntity",
        description="Any chemical entity from ChEBI ontology",
    )

class Drug(EnumDefinitionImpl):
    """
    Pharmaceutical drugs and medications
    """
    _defn = EnumDefinition(
        name="Drug",
        description="Pharmaceutical drugs and medications",
    )

class Metabolite(EnumDefinitionImpl):
    """
    Metabolites and metabolic intermediates
    """
    _defn = EnumDefinition(
        name="Metabolite",
        description="Metabolites and metabolic intermediates",
    )

class Protein(EnumDefinitionImpl):
    """
    Proteins and protein complexes
    """
    _defn = EnumDefinition(
        name="Protein",
        description="Proteins and protein complexes",
    )

class Phenotype(EnumDefinitionImpl):
    """
    Phenotypic abnormalities from Human Phenotype Ontology
    """
    _defn = EnumDefinition(
        name="Phenotype",
        description="Phenotypic abnormalities from Human Phenotype Ontology",
    )

class ClinicalFinding(EnumDefinitionImpl):
    """
    Clinical findings and observations
    """
    _defn = EnumDefinition(
        name="ClinicalFinding",
        description="Clinical findings and observations",
    )

class BiologicalProcess(EnumDefinitionImpl):
    """
    Biological processes from Gene Ontology
    """
    _defn = EnumDefinition(
        name="BiologicalProcess",
        description="Biological processes from Gene Ontology",
    )

class MetabolicProcess(EnumDefinitionImpl):
    """
    Metabolic processes and pathways
    """
    _defn = EnumDefinition(
        name="MetabolicProcess",
        description="Metabolic processes and pathways",
    )

class MolecularFunction(EnumDefinitionImpl):
    """
    Molecular functions from Gene Ontology
    """
    _defn = EnumDefinition(
        name="MolecularFunction",
        description="Molecular functions from Gene Ontology",
    )

class CellularComponent(EnumDefinitionImpl):
    """
    Cellular components and locations from Gene Ontology
    """
    _defn = EnumDefinition(
        name="CellularComponent",
        description="Cellular components and locations from Gene Ontology",
    )

class SequenceFeature(EnumDefinitionImpl):
    """
    Sequence features from the Sequence Ontology
    """
    _defn = EnumDefinition(
        name="SequenceFeature",
        description="Sequence features from the Sequence Ontology",
    )

class GeneFeature(EnumDefinitionImpl):
    """
    Gene-related sequence features
    """
    _defn = EnumDefinition(
        name="GeneFeature",
        description="Gene-related sequence features",
    )

class Environment(EnumDefinitionImpl):
    """
    Environmental systems and biomes
    """
    _defn = EnumDefinition(
        name="Environment",
        description="Environmental systems and biomes",
    )

class EnvironmentalMaterial(EnumDefinitionImpl):
    """
    Environmental materials and substances
    """
    _defn = EnumDefinition(
        name="EnvironmentalMaterial",
        description="Environmental materials and substances",
    )

class Quality(EnumDefinitionImpl):
    """
    Phenotypic qualities and attributes from PATO
    """
    _defn = EnumDefinition(
        name="Quality",
        description="Phenotypic qualities and attributes from PATO",
    )

class PhysicalQuality(EnumDefinitionImpl):
    """
    Physical qualities like size, shape, color
    """
    _defn = EnumDefinition(
        name="PhysicalQuality",
        description="Physical qualities like size, shape, color",
    )

class SampleType(EnumDefinitionImpl):
    """
    Types of biological samples used in structural biology
    """
    PROTEIN = PermissibleValue(
        text="PROTEIN",
        description="Purified protein sample")
    NUCLEIC_ACID = PermissibleValue(
        text="NUCLEIC_ACID",
        description="Nucleic acid sample (DNA or RNA)")
    PROTEIN_COMPLEX = PermissibleValue(
        text="PROTEIN_COMPLEX",
        description="Protein-protein or protein-nucleic acid complex")
    MEMBRANE_PROTEIN = PermissibleValue(
        text="MEMBRANE_PROTEIN",
        description="Membrane-associated protein sample")
    VIRUS = PermissibleValue(
        text="VIRUS",
        description="Viral particle or capsid")
    ORGANELLE = PermissibleValue(
        text="ORGANELLE",
        description="Cellular organelle (mitochondria, chloroplast, etc.)")
    CELL = PermissibleValue(
        text="CELL",
        description="Whole cell sample")
    TISSUE = PermissibleValue(
        text="TISSUE",
        description="Tissue sample")

    _defn = EnumDefinition(
        name="SampleType",
        description="Types of biological samples used in structural biology",
    )

class StructuralBiologyTechnique(EnumDefinitionImpl):
    """
    Structural biology experimental techniques
    """
    CRYO_EM = PermissibleValue(
        text="CRYO_EM",
        title="cryogenic electron microscopy",
        description="Cryo-electron microscopy",
        meaning=CHMO["0002413"])
    CRYO_ET = PermissibleValue(
        text="CRYO_ET",
        description="Cryo-electron tomography")
    X_RAY_CRYSTALLOGRAPHY = PermissibleValue(
        text="X_RAY_CRYSTALLOGRAPHY",
        title="single crystal X-ray diffraction",
        description="X-ray crystallography",
        meaning=CHMO["0000159"])
    NEUTRON_CRYSTALLOGRAPHY = PermissibleValue(
        text="NEUTRON_CRYSTALLOGRAPHY",
        description="Neutron crystallography")
    SAXS = PermissibleValue(
        text="SAXS",
        title="small-angle X-ray scattering",
        description="Small-angle X-ray scattering",
        meaning=CHMO["0000204"])
    SANS = PermissibleValue(
        text="SANS",
        description="Small-angle neutron scattering")
    WAXS = PermissibleValue(
        text="WAXS",
        description="Wide-angle X-ray scattering")
    NMR = PermissibleValue(
        text="NMR",
        title="nuclear magnetic resonance spectroscopy",
        description="Nuclear magnetic resonance spectroscopy",
        meaning=CHMO["0000591"])
    MASS_SPECTROMETRY = PermissibleValue(
        text="MASS_SPECTROMETRY",
        description="Mass spectrometry",
        meaning=CHMO["0000470"])
    NEGATIVE_STAIN_EM = PermissibleValue(
        text="NEGATIVE_STAIN_EM",
        description="Negative stain electron microscopy")

    _defn = EnumDefinition(
        name="StructuralBiologyTechnique",
        description="Structural biology experimental techniques",
    )

class CryoEMPreparationType(EnumDefinitionImpl):
    """
    Types of cryo-EM sample preparation
    """
    VITREOUS_ICE = PermissibleValue(
        text="VITREOUS_ICE",
        description="Sample embedded in vitreous ice")
    CRYO_SECTIONING = PermissibleValue(
        text="CRYO_SECTIONING",
        description="Cryo-sectioned sample")
    FREEZE_SUBSTITUTION = PermissibleValue(
        text="FREEZE_SUBSTITUTION",
        description="Freeze-substituted sample")
    HIGH_PRESSURE_FREEZING = PermissibleValue(
        text="HIGH_PRESSURE_FREEZING",
        description="High-pressure frozen sample")

    _defn = EnumDefinition(
        name="CryoEMPreparationType",
        description="Types of cryo-EM sample preparation",
    )

class CryoEMGridType(EnumDefinitionImpl):
    """
    Types of electron microscopy grids
    """
    C_FLAT = PermissibleValue(
        text="C_FLAT",
        description="C-flat holey carbon grid")
    QUANTIFOIL = PermissibleValue(
        text="QUANTIFOIL",
        description="Quantifoil holey carbon grid")
    LACEY_CARBON = PermissibleValue(
        text="LACEY_CARBON",
        description="Lacey carbon support film")
    ULTRATHIN_CARBON = PermissibleValue(
        text="ULTRATHIN_CARBON",
        description="Ultrathin carbon film on holey support")
    GOLD_GRID = PermissibleValue(
        text="GOLD_GRID",
        description="Pure gold grid")
    GRAPHENE_OXIDE = PermissibleValue(
        text="GRAPHENE_OXIDE",
        description="Graphene oxide support")

    _defn = EnumDefinition(
        name="CryoEMGridType",
        description="Types of electron microscopy grids",
    )

class VitrificationMethod(EnumDefinitionImpl):
    """
    Methods for sample vitrification
    """
    PLUNGE_FREEZING = PermissibleValue(
        text="PLUNGE_FREEZING",
        description="Plunge freezing in liquid ethane")
    HIGH_PRESSURE_FREEZING = PermissibleValue(
        text="HIGH_PRESSURE_FREEZING",
        description="High pressure freezing")
    SLAM_FREEZING = PermissibleValue(
        text="SLAM_FREEZING",
        description="Slam freezing against metal block")
    SPRAY_FREEZING = PermissibleValue(
        text="SPRAY_FREEZING",
        description="Spray freezing into liquid nitrogen")

    _defn = EnumDefinition(
        name="VitrificationMethod",
        description="Methods for sample vitrification",
    )

class CrystallizationMethod(EnumDefinitionImpl):
    """
    Methods for protein crystallization
    """
    VAPOR_DIFFUSION_HANGING = PermissibleValue(
        text="VAPOR_DIFFUSION_HANGING",
        description="Vapor diffusion hanging drop method")
    VAPOR_DIFFUSION_SITTING = PermissibleValue(
        text="VAPOR_DIFFUSION_SITTING",
        description="Vapor diffusion sitting drop method")
    MICROBATCH = PermissibleValue(
        text="MICROBATCH",
        description="Microbatch under oil method")
    DIALYSIS = PermissibleValue(
        text="DIALYSIS",
        description="Dialysis crystallization")
    FREE_INTERFACE_DIFFUSION = PermissibleValue(
        text="FREE_INTERFACE_DIFFUSION",
        description="Free interface diffusion")
    LCP = PermissibleValue(
        text="LCP",
        description="Lipidic cubic phase crystallization")

    _defn = EnumDefinition(
        name="CrystallizationMethod",
        description="Methods for protein crystallization",
    )

class XRaySource(EnumDefinitionImpl):
    """
    Types of X-ray sources
    """
    SYNCHROTRON = PermissibleValue(
        text="SYNCHROTRON",
        description="Synchrotron radiation source")
    ROTATING_ANODE = PermissibleValue(
        text="ROTATING_ANODE",
        description="Rotating anode generator")
    MICROFOCUS = PermissibleValue(
        text="MICROFOCUS",
        description="Microfocus sealed tube")
    METAL_JET = PermissibleValue(
        text="METAL_JET",
        description="Liquid metal jet source")

    _defn = EnumDefinition(
        name="XRaySource",
        description="Types of X-ray sources",
    )

class Detector(EnumDefinitionImpl):
    """
    Types of detectors for structural biology
    """
    DIRECT_ELECTRON = PermissibleValue(
        text="DIRECT_ELECTRON",
        description="Direct electron detector (DED)")
    CCD = PermissibleValue(
        text="CCD",
        description="Charge-coupled device camera")
    CMOS = PermissibleValue(
        text="CMOS",
        description="Complementary metal-oxide semiconductor detector")
    HYBRID_PIXEL = PermissibleValue(
        text="HYBRID_PIXEL",
        description="Hybrid pixel detector")
    PHOTOSTIMULABLE_PHOSPHOR = PermissibleValue(
        text="PHOTOSTIMULABLE_PHOSPHOR",
        description="Photostimulable phosphor (image plate)")

    _defn = EnumDefinition(
        name="Detector",
        description="Types of detectors for structural biology",
    )

class WorkflowType(EnumDefinitionImpl):
    """
    Types of computational processing workflows
    """
    MOTION_CORRECTION = PermissibleValue(
        text="MOTION_CORRECTION",
        description="Motion correction for cryo-EM movies")
    CTF_ESTIMATION = PermissibleValue(
        text="CTF_ESTIMATION",
        description="Contrast transfer function estimation")
    PARTICLE_PICKING = PermissibleValue(
        text="PARTICLE_PICKING",
        description="Particle picking from micrographs")
    CLASSIFICATION_2D = PermissibleValue(
        text="CLASSIFICATION_2D",
        description="2D classification of particles")
    CLASSIFICATION_3D = PermissibleValue(
        text="CLASSIFICATION_3D",
        description="3D classification of particles")
    REFINEMENT_3D = PermissibleValue(
        text="REFINEMENT_3D",
        description="3D refinement of particle orientations")
    MODEL_BUILDING = PermissibleValue(
        text="MODEL_BUILDING",
        description="Atomic model building into density")
    MODEL_REFINEMENT = PermissibleValue(
        text="MODEL_REFINEMENT",
        description="Atomic model refinement")
    PHASING = PermissibleValue(
        text="PHASING",
        description="Phase determination for crystallography")
    DATA_INTEGRATION = PermissibleValue(
        text="DATA_INTEGRATION",
        description="Integration of diffraction data")
    DATA_SCALING = PermissibleValue(
        text="DATA_SCALING",
        description="Scaling and merging of diffraction data")
    SAXS_ANALYSIS = PermissibleValue(
        text="SAXS_ANALYSIS",
        description="SAXS data analysis and modeling")

    _defn = EnumDefinition(
        name="WorkflowType",
        description="Types of computational processing workflows",
    )

class FileFormat(EnumDefinitionImpl):
    """
    File formats used in structural biology
    """
    MRC = PermissibleValue(
        text="MRC",
        description="MRC format for EM density maps")
    TIFF = PermissibleValue(
        text="TIFF",
        description="Tagged Image File Format")
    HDF5 = PermissibleValue(
        text="HDF5",
        description="Hierarchical Data Format 5")
    STAR = PermissibleValue(
        text="STAR",
        description="Self-defining Text Archival and Retrieval format")
    PDB = PermissibleValue(
        text="PDB",
        description="Protein Data Bank coordinate format")
    MMCIF = PermissibleValue(
        text="MMCIF",
        description="Macromolecular Crystallographic Information File")
    MTZ = PermissibleValue(
        text="MTZ",
        description="MTZ reflection data format")
    CBF = PermissibleValue(
        text="CBF",
        description="Crystallographic Binary Format")
    DM3 = PermissibleValue(
        text="DM3",
        description="Digital Micrograph format")
    SER = PermissibleValue(
        text="SER",
        description="FEI series format")

    _defn = EnumDefinition(
        name="FileFormat",
        description="File formats used in structural biology",
    )

class DataType(EnumDefinitionImpl):
    """
    Types of structural biology data
    """
    MICROGRAPH = PermissibleValue(
        text="MICROGRAPH",
        description="Electron micrograph image")
    MOVIE = PermissibleValue(
        text="MOVIE",
        description="Movie stack of frames")
    DIFFRACTION = PermissibleValue(
        text="DIFFRACTION",
        description="X-ray diffraction pattern")
    SCATTERING = PermissibleValue(
        text="SCATTERING",
        description="Small-angle scattering data")
    PARTICLES = PermissibleValue(
        text="PARTICLES",
        description="Particle stack for single particle analysis")
    VOLUME = PermissibleValue(
        text="VOLUME",
        description="3D electron density volume")
    TOMOGRAM = PermissibleValue(
        text="TOMOGRAM",
        description="3D tomographic reconstruction")
    MODEL = PermissibleValue(
        text="MODEL",
        description="Atomic coordinate model")
    METADATA = PermissibleValue(
        text="METADATA",
        description="Associated metadata file")

    _defn = EnumDefinition(
        name="DataType",
        description="Types of structural biology data",
    )

class ProcessingStatus(EnumDefinitionImpl):
    """
    Status of data processing workflows
    """
    RAW = PermissibleValue(
        text="RAW",
        description="Raw unprocessed data")
    PREPROCESSING = PermissibleValue(
        text="PREPROCESSING",
        description="Initial preprocessing in progress")
    PROCESSING = PermissibleValue(
        text="PROCESSING",
        description="Main processing workflow running")
    COMPLETED = PermissibleValue(
        text="COMPLETED",
        description="Processing completed successfully")
    FAILED = PermissibleValue(
        text="FAILED",
        description="Processing failed with errors")
    QUEUED = PermissibleValue(
        text="QUEUED",
        description="Queued for processing")
    PAUSED = PermissibleValue(
        text="PAUSED",
        description="Processing paused by user")
    CANCELLED = PermissibleValue(
        text="CANCELLED",
        description="Processing cancelled by user")

    _defn = EnumDefinition(
        name="ProcessingStatus",
        description="Status of data processing workflows",
    )

class InsdcMissingValueEnum(EnumDefinitionImpl):
    """
    INSDC (International Nucleotide Sequence Database Collaboration) controlled vocabulary for missing values in
    sequence records
    """
    NOT_APPLICABLE = PermissibleValue(
        text="NOT_APPLICABLE",
        title="not applicable",
        description="""Information is inappropriate to report, can indicate that the standard itself fails to model or represent the information appropriately""",
        meaning=NCIT["C48660"])
    MISSING = PermissibleValue(
        text="MISSING",
        title="missing",
        description="Not stated explicitly or implied by any other means",
        meaning=NCIT["C54031"])
    NOT_COLLECTED = PermissibleValue(
        text="NOT_COLLECTED",
        title="Missing Data",
        description="Information of an expected format was not given because it has never been collected",
        meaning=NCIT["C142610"])
    NOT_PROVIDED = PermissibleValue(
        text="NOT_PROVIDED",
        title="Not Available",
        description="Information of an expected format was not given, a value may be given at the later stage",
        meaning=NCIT["C126101"])
    RESTRICTED_ACCESS = PermissibleValue(
        text="RESTRICTED_ACCESS",
        title="Data Not Releasable",
        description="Information exists but cannot be released openly because of privacy concerns",
        meaning=NCIT["C67110"])
    MISSING_CONTROL_SAMPLE = PermissibleValue(
        text="MISSING_CONTROL_SAMPLE",
        description="""Information is not applicable to control samples, negative control samples (e.g. blank sample or clear sample)""")
    MISSING_SAMPLE_GROUP = PermissibleValue(
        text="MISSING_SAMPLE_GROUP",
        description="""Information can not be provided for a sample group where a selection of samples is used to represent a species, location or some other attribute/metric""")
    MISSING_SYNTHETIC_CONSTRUCT = PermissibleValue(
        text="MISSING_SYNTHETIC_CONSTRUCT",
        description="Information does not exist for a synthetic construct")
    MISSING_LAB_STOCK = PermissibleValue(
        text="MISSING_LAB_STOCK",
        description="""Information is not collected for a lab stock and its cultivation, e.g. stock centers, culture collections, seed banks""")
    MISSING_THIRD_PARTY_DATA = PermissibleValue(
        text="MISSING_THIRD_PARTY_DATA",
        title="Source Data Not Available",
        description="Information has not been revealed by another party",
        meaning=NCIT["C67329"])
    MISSING_DATA_AGREEMENT_ESTABLISHED_PRE_2023 = PermissibleValue(
        text="MISSING_DATA_AGREEMENT_ESTABLISHED_PRE_2023",
        description="""Information can not be reported due to a data agreement established before metadata standards were introduced in 2023""")
    MISSING_ENDANGERED_SPECIES = PermissibleValue(
        text="MISSING_ENDANGERED_SPECIES",
        description="Information can not be reported due to endangered species concerns")
    MISSING_HUMAN_IDENTIFIABLE = PermissibleValue(
        text="MISSING_HUMAN_IDENTIFIABLE",
        description="Information can not be reported due to identifiable human data concerns")

    _defn = EnumDefinition(
        name="InsdcMissingValueEnum",
        description="""INSDC (International Nucleotide Sequence Database Collaboration) controlled vocabulary for missing values in sequence records""",
    )

class InsdcGeographicLocationEnum(EnumDefinitionImpl):
    """
    INSDC controlled vocabulary for geographic locations of collected samples.
    Includes countries, oceans, seas, and other geographic regions as defined by INSDC.
    Countries use ISO 3166-1 alpha-2 codes from Library of Congress as canonical identifiers.
    """
    AFGHANISTAN = PermissibleValue(
        text="AFGHANISTAN",
        description="Afghanistan",
        meaning=ISO3166LOC["af"])
    ALBANIA = PermissibleValue(
        text="ALBANIA",
        description="Albania",
        meaning=ISO3166LOC["al"])
    ALGERIA = PermissibleValue(
        text="ALGERIA",
        description="Algeria",
        meaning=ISO3166LOC["dz"])
    AMERICAN_SAMOA = PermissibleValue(
        text="AMERICAN_SAMOA",
        description="American Samoa",
        meaning=ISO3166LOC["as"])
    ANDORRA = PermissibleValue(
        text="ANDORRA",
        description="Andorra",
        meaning=ISO3166LOC["ad"])
    ANGOLA = PermissibleValue(
        text="ANGOLA",
        description="Angola",
        meaning=ISO3166LOC["ao"])
    ANGUILLA = PermissibleValue(
        text="ANGUILLA",
        description="Anguilla",
        meaning=ISO3166LOC["ai"])
    ANTARCTICA = PermissibleValue(
        text="ANTARCTICA",
        description="Antarctica",
        meaning=ISO3166LOC["aq"])
    ANTIGUA_AND_BARBUDA = PermissibleValue(
        text="ANTIGUA_AND_BARBUDA",
        description="Antigua and Barbuda",
        meaning=ISO3166LOC["ag"])
    ARCTIC_OCEAN = PermissibleValue(
        text="ARCTIC_OCEAN",
        description="Arctic Ocean",
        meaning=GEONAMES["3371123/"])
    ARGENTINA = PermissibleValue(
        text="ARGENTINA",
        description="Argentina",
        meaning=ISO3166LOC["ar"])
    ARMENIA = PermissibleValue(
        text="ARMENIA",
        description="Armenia",
        meaning=ISO3166LOC["am"])
    ARUBA = PermissibleValue(
        text="ARUBA",
        description="Aruba",
        meaning=ISO3166LOC["aw"])
    ASHMORE_AND_CARTIER_ISLANDS = PermissibleValue(
        text="ASHMORE_AND_CARTIER_ISLANDS",
        description="Ashmore and Cartier Islands")
    ATLANTIC_OCEAN = PermissibleValue(
        text="ATLANTIC_OCEAN",
        description="Atlantic Ocean",
        meaning=GEONAMES["3411923/"])
    AUSTRALIA = PermissibleValue(
        text="AUSTRALIA",
        description="Australia",
        meaning=ISO3166LOC["au"])
    AUSTRIA = PermissibleValue(
        text="AUSTRIA",
        description="Austria",
        meaning=ISO3166LOC["at"])
    AZERBAIJAN = PermissibleValue(
        text="AZERBAIJAN",
        description="Azerbaijan",
        meaning=ISO3166LOC["az"])
    BAHAMAS = PermissibleValue(
        text="BAHAMAS",
        description="Bahamas",
        meaning=ISO3166LOC["bs"])
    BAHRAIN = PermissibleValue(
        text="BAHRAIN",
        description="Bahrain",
        meaning=ISO3166LOC["bh"])
    BALTIC_SEA = PermissibleValue(
        text="BALTIC_SEA",
        description="Baltic Sea",
        meaning=GEONAMES["2673730/"])
    BAKER_ISLAND = PermissibleValue(
        text="BAKER_ISLAND",
        description="Baker Island",
        meaning=ISO3166LOC["um"])
    BANGLADESH = PermissibleValue(
        text="BANGLADESH",
        description="Bangladesh",
        meaning=ISO3166LOC["bd"])
    BARBADOS = PermissibleValue(
        text="BARBADOS",
        description="Barbados",
        meaning=ISO3166LOC["bb"])
    BASSAS_DA_INDIA = PermissibleValue(
        text="BASSAS_DA_INDIA",
        description="Bassas da India")
    BELARUS = PermissibleValue(
        text="BELARUS",
        description="Belarus",
        meaning=ISO3166LOC["by"])
    BELGIUM = PermissibleValue(
        text="BELGIUM",
        description="Belgium",
        meaning=ISO3166LOC["be"])
    BELIZE = PermissibleValue(
        text="BELIZE",
        description="Belize",
        meaning=ISO3166LOC["bz"])
    BENIN = PermissibleValue(
        text="BENIN",
        description="Benin",
        meaning=ISO3166LOC["bj"])
    BERMUDA = PermissibleValue(
        text="BERMUDA",
        description="Bermuda",
        meaning=ISO3166LOC["bm"])
    BHUTAN = PermissibleValue(
        text="BHUTAN",
        description="Bhutan",
        meaning=ISO3166LOC["bt"])
    BOLIVIA = PermissibleValue(
        text="BOLIVIA",
        description="Bolivia",
        meaning=ISO3166LOC["bo"])
    BORNEO = PermissibleValue(
        text="BORNEO",
        description="Borneo",
        meaning=GEONAMES["1642188/"])
    BOSNIA_AND_HERZEGOVINA = PermissibleValue(
        text="BOSNIA_AND_HERZEGOVINA",
        description="Bosnia and Herzegovina",
        meaning=ISO3166LOC["ba"])
    BOTSWANA = PermissibleValue(
        text="BOTSWANA",
        description="Botswana",
        meaning=ISO3166LOC["bw"])
    BOUVET_ISLAND = PermissibleValue(
        text="BOUVET_ISLAND",
        description="Bouvet Island",
        meaning=ISO3166LOC["bv"])
    BRAZIL = PermissibleValue(
        text="BRAZIL",
        description="Brazil",
        meaning=ISO3166LOC["br"])
    BRITISH_VIRGIN_ISLANDS = PermissibleValue(
        text="BRITISH_VIRGIN_ISLANDS",
        description="British Virgin Islands",
        meaning=ISO3166LOC["vg"])
    BRUNEI = PermissibleValue(
        text="BRUNEI",
        description="Brunei",
        meaning=ISO3166LOC["bn"])
    BULGARIA = PermissibleValue(
        text="BULGARIA",
        description="Bulgaria",
        meaning=ISO3166LOC["bg"])
    BURKINA_FASO = PermissibleValue(
        text="BURKINA_FASO",
        description="Burkina Faso",
        meaning=ISO3166LOC["bf"])
    BURUNDI = PermissibleValue(
        text="BURUNDI",
        description="Burundi",
        meaning=ISO3166LOC["bi"])
    CAMBODIA = PermissibleValue(
        text="CAMBODIA",
        description="Cambodia",
        meaning=ISO3166LOC["kh"])
    CAMEROON = PermissibleValue(
        text="CAMEROON",
        description="Cameroon",
        meaning=ISO3166LOC["cm"])
    CANADA = PermissibleValue(
        text="CANADA",
        description="Canada",
        meaning=ISO3166LOC["ca"])
    CAPE_VERDE = PermissibleValue(
        text="CAPE_VERDE",
        description="Cape Verde",
        meaning=ISO3166LOC["cv"])
    CAYMAN_ISLANDS = PermissibleValue(
        text="CAYMAN_ISLANDS",
        description="Cayman Islands",
        meaning=ISO3166LOC["ky"])
    CENTRAL_AFRICAN_REPUBLIC = PermissibleValue(
        text="CENTRAL_AFRICAN_REPUBLIC",
        description="Central African Republic",
        meaning=ISO3166LOC["cf"])
    CHAD = PermissibleValue(
        text="CHAD",
        description="Chad",
        meaning=ISO3166LOC["td"])
    CHILE = PermissibleValue(
        text="CHILE",
        description="Chile",
        meaning=ISO3166LOC["cl"])
    CHINA = PermissibleValue(
        text="CHINA",
        description="China",
        meaning=ISO3166LOC["cn"])
    CHRISTMAS_ISLAND = PermissibleValue(
        text="CHRISTMAS_ISLAND",
        description="Christmas Island",
        meaning=ISO3166LOC["cx"])
    CLIPPERTON_ISLAND = PermissibleValue(
        text="CLIPPERTON_ISLAND",
        description="Clipperton Island")
    COCOS_ISLANDS = PermissibleValue(
        text="COCOS_ISLANDS",
        description="Cocos Islands",
        meaning=ISO3166LOC["cc"])
    COLOMBIA = PermissibleValue(
        text="COLOMBIA",
        description="Colombia",
        meaning=ISO3166LOC["co"])
    COMOROS = PermissibleValue(
        text="COMOROS",
        description="Comoros",
        meaning=ISO3166LOC["km"])
    COOK_ISLANDS = PermissibleValue(
        text="COOK_ISLANDS",
        description="Cook Islands",
        meaning=ISO3166LOC["ck"])
    CORAL_SEA_ISLANDS = PermissibleValue(
        text="CORAL_SEA_ISLANDS",
        description="Coral Sea Islands")
    COSTA_RICA = PermissibleValue(
        text="COSTA_RICA",
        description="Costa Rica",
        meaning=ISO3166LOC["cr"])
    COTE_DIVOIRE = PermissibleValue(
        text="COTE_DIVOIRE",
        description="Cote d'Ivoire",
        meaning=ISO3166LOC["ci"])
    CROATIA = PermissibleValue(
        text="CROATIA",
        description="Croatia",
        meaning=ISO3166LOC["hr"])
    CUBA = PermissibleValue(
        text="CUBA",
        description="Cuba",
        meaning=ISO3166LOC["cu"])
    CURACAO = PermissibleValue(
        text="CURACAO",
        description="Curacao",
        meaning=ISO3166LOC["cw"])
    CYPRUS = PermissibleValue(
        text="CYPRUS",
        description="Cyprus",
        meaning=ISO3166LOC["cy"])
    CZECHIA = PermissibleValue(
        text="CZECHIA",
        description="Czechia",
        meaning=ISO3166LOC["cz"])
    DEMOCRATIC_REPUBLIC_OF_THE_CONGO = PermissibleValue(
        text="DEMOCRATIC_REPUBLIC_OF_THE_CONGO",
        description="Democratic Republic of the Congo",
        meaning=ISO3166LOC["cd"])
    DENMARK = PermissibleValue(
        text="DENMARK",
        description="Denmark",
        meaning=ISO3166LOC["dk"])
    DJIBOUTI = PermissibleValue(
        text="DJIBOUTI",
        description="Djibouti",
        meaning=ISO3166LOC["dj"])
    DOMINICA = PermissibleValue(
        text="DOMINICA",
        description="Dominica",
        meaning=ISO3166LOC["dm"])
    DOMINICAN_REPUBLIC = PermissibleValue(
        text="DOMINICAN_REPUBLIC",
        description="Dominican Republic",
        meaning=ISO3166LOC["do"])
    ECUADOR = PermissibleValue(
        text="ECUADOR",
        description="Ecuador",
        meaning=ISO3166LOC["ec"])
    EGYPT = PermissibleValue(
        text="EGYPT",
        description="Egypt",
        meaning=ISO3166LOC["eg"])
    EL_SALVADOR = PermissibleValue(
        text="EL_SALVADOR",
        description="El Salvador",
        meaning=ISO3166LOC["sv"])
    EQUATORIAL_GUINEA = PermissibleValue(
        text="EQUATORIAL_GUINEA",
        description="Equatorial Guinea",
        meaning=ISO3166LOC["gq"])
    ERITREA = PermissibleValue(
        text="ERITREA",
        description="Eritrea",
        meaning=ISO3166LOC["er"])
    ESTONIA = PermissibleValue(
        text="ESTONIA",
        description="Estonia",
        meaning=ISO3166LOC["ee"])
    ESWATINI = PermissibleValue(
        text="ESWATINI",
        description="Eswatini",
        meaning=ISO3166LOC["sz"])
    ETHIOPIA = PermissibleValue(
        text="ETHIOPIA",
        description="Ethiopia",
        meaning=ISO3166LOC["et"])
    EUROPA_ISLAND = PermissibleValue(
        text="EUROPA_ISLAND",
        description="Europa Island")
    FALKLAND_ISLANDS = PermissibleValue(
        text="FALKLAND_ISLANDS",
        description="Falkland Islands (Islas Malvinas)",
        meaning=ISO3166LOC["fk"])
    FAROE_ISLANDS = PermissibleValue(
        text="FAROE_ISLANDS",
        description="Faroe Islands",
        meaning=ISO3166LOC["fo"])
    FIJI = PermissibleValue(
        text="FIJI",
        description="Fiji",
        meaning=ISO3166LOC["fj"])
    FINLAND = PermissibleValue(
        text="FINLAND",
        description="Finland",
        meaning=ISO3166LOC["fi"])
    FRANCE = PermissibleValue(
        text="FRANCE",
        description="France",
        meaning=ISO3166LOC["fr"])
    FRENCH_GUIANA = PermissibleValue(
        text="FRENCH_GUIANA",
        description="French Guiana",
        meaning=ISO3166LOC["gf"])
    FRENCH_POLYNESIA = PermissibleValue(
        text="FRENCH_POLYNESIA",
        description="French Polynesia",
        meaning=ISO3166LOC["pf"])
    FRENCH_SOUTHERN_AND_ANTARCTIC_LANDS = PermissibleValue(
        text="FRENCH_SOUTHERN_AND_ANTARCTIC_LANDS",
        description="French Southern and Antarctic Lands",
        meaning=ISO3166LOC["tf"])
    GABON = PermissibleValue(
        text="GABON",
        description="Gabon",
        meaning=ISO3166LOC["ga"])
    GAMBIA = PermissibleValue(
        text="GAMBIA",
        description="Gambia",
        meaning=ISO3166LOC["gm"])
    GAZA_STRIP = PermissibleValue(
        text="GAZA_STRIP",
        description="Gaza Strip")
    GEORGIA = PermissibleValue(
        text="GEORGIA",
        description="Georgia",
        meaning=ISO3166LOC["ge"])
    GERMANY = PermissibleValue(
        text="GERMANY",
        description="Germany",
        meaning=ISO3166LOC["de"])
    GHANA = PermissibleValue(
        text="GHANA",
        description="Ghana",
        meaning=ISO3166LOC["gh"])
    GIBRALTAR = PermissibleValue(
        text="GIBRALTAR",
        description="Gibraltar",
        meaning=ISO3166LOC["gi"])
    GLORIOSO_ISLANDS = PermissibleValue(
        text="GLORIOSO_ISLANDS",
        description="Glorioso Islands")
    GREECE = PermissibleValue(
        text="GREECE",
        description="Greece",
        meaning=ISO3166LOC["gr"])
    GREENLAND = PermissibleValue(
        text="GREENLAND",
        description="Greenland",
        meaning=ISO3166LOC["gl"])
    GRENADA = PermissibleValue(
        text="GRENADA",
        description="Grenada",
        meaning=ISO3166LOC["gd"])
    GUADELOUPE = PermissibleValue(
        text="GUADELOUPE",
        description="Guadeloupe",
        meaning=ISO3166LOC["gp"])
    GUAM = PermissibleValue(
        text="GUAM",
        description="Guam",
        meaning=ISO3166LOC["gu"])
    GUATEMALA = PermissibleValue(
        text="GUATEMALA",
        description="Guatemala",
        meaning=ISO3166LOC["gt"])
    GUERNSEY = PermissibleValue(
        text="GUERNSEY",
        description="Guernsey",
        meaning=ISO3166LOC["gg"])
    GUINEA = PermissibleValue(
        text="GUINEA",
        description="Guinea",
        meaning=ISO3166LOC["gn"])
    GUINEA_BISSAU = PermissibleValue(
        text="GUINEA_BISSAU",
        description="Guinea-Bissau",
        meaning=ISO3166LOC["gw"])
    GUYANA = PermissibleValue(
        text="GUYANA",
        description="Guyana",
        meaning=ISO3166LOC["gy"])
    HAITI = PermissibleValue(
        text="HAITI",
        description="Haiti",
        meaning=ISO3166LOC["ht"])
    HEARD_ISLAND_AND_MCDONALD_ISLANDS = PermissibleValue(
        text="HEARD_ISLAND_AND_MCDONALD_ISLANDS",
        description="Heard Island and McDonald Islands",
        meaning=ISO3166LOC["hm"])
    HONDURAS = PermissibleValue(
        text="HONDURAS",
        description="Honduras",
        meaning=ISO3166LOC["hn"])
    HONG_KONG = PermissibleValue(
        text="HONG_KONG",
        description="Hong Kong",
        meaning=ISO3166LOC["hk"])
    HOWLAND_ISLAND = PermissibleValue(
        text="HOWLAND_ISLAND",
        description="Howland Island",
        meaning=ISO3166LOC["um"])
    HUNGARY = PermissibleValue(
        text="HUNGARY",
        description="Hungary",
        meaning=ISO3166LOC["hu"])
    ICELAND = PermissibleValue(
        text="ICELAND",
        description="Iceland",
        meaning=ISO3166LOC["is"])
    INDIA = PermissibleValue(
        text="INDIA",
        description="India",
        meaning=ISO3166LOC["in"])
    INDIAN_OCEAN = PermissibleValue(
        text="INDIAN_OCEAN",
        description="Indian Ocean",
        meaning=GEONAMES["1545739/"])
    INDONESIA = PermissibleValue(
        text="INDONESIA",
        description="Indonesia",
        meaning=ISO3166LOC["id"])
    IRAN = PermissibleValue(
        text="IRAN",
        description="Iran",
        meaning=ISO3166LOC["ir"])
    IRAQ = PermissibleValue(
        text="IRAQ",
        description="Iraq",
        meaning=ISO3166LOC["iq"])
    IRELAND = PermissibleValue(
        text="IRELAND",
        description="Ireland",
        meaning=ISO3166LOC["ie"])
    ISLE_OF_MAN = PermissibleValue(
        text="ISLE_OF_MAN",
        description="Isle of Man",
        meaning=ISO3166LOC["im"])
    ISRAEL = PermissibleValue(
        text="ISRAEL",
        description="Israel",
        meaning=ISO3166LOC["il"])
    ITALY = PermissibleValue(
        text="ITALY",
        description="Italy",
        meaning=ISO3166LOC["it"])
    JAMAICA = PermissibleValue(
        text="JAMAICA",
        description="Jamaica",
        meaning=ISO3166LOC["jm"])
    JAN_MAYEN = PermissibleValue(
        text="JAN_MAYEN",
        description="Jan Mayen")
    JAPAN = PermissibleValue(
        text="JAPAN",
        description="Japan",
        meaning=ISO3166LOC["jp"])
    JARVIS_ISLAND = PermissibleValue(
        text="JARVIS_ISLAND",
        description="Jarvis Island",
        meaning=ISO3166LOC["um"])
    JERSEY = PermissibleValue(
        text="JERSEY",
        description="Jersey",
        meaning=ISO3166LOC["je"])
    JOHNSTON_ATOLL = PermissibleValue(
        text="JOHNSTON_ATOLL",
        description="Johnston Atoll",
        meaning=ISO3166LOC["um"])
    JORDAN = PermissibleValue(
        text="JORDAN",
        description="Jordan",
        meaning=ISO3166LOC["jo"])
    JUAN_DE_NOVA_ISLAND = PermissibleValue(
        text="JUAN_DE_NOVA_ISLAND",
        description="Juan de Nova Island")
    KAZAKHSTAN = PermissibleValue(
        text="KAZAKHSTAN",
        description="Kazakhstan",
        meaning=ISO3166LOC["kz"])
    KENYA = PermissibleValue(
        text="KENYA",
        description="Kenya",
        meaning=ISO3166LOC["ke"])
    KERGUELEN_ARCHIPELAGO = PermissibleValue(
        text="KERGUELEN_ARCHIPELAGO",
        description="Kerguelen Archipelago")
    KINGMAN_REEF = PermissibleValue(
        text="KINGMAN_REEF",
        description="Kingman Reef",
        meaning=ISO3166LOC["um"])
    KIRIBATI = PermissibleValue(
        text="KIRIBATI",
        description="Kiribati",
        meaning=ISO3166LOC["ki"])
    KOSOVO = PermissibleValue(
        text="KOSOVO",
        description="Kosovo",
        meaning=ISO3166LOC["xk"])
    KUWAIT = PermissibleValue(
        text="KUWAIT",
        description="Kuwait",
        meaning=ISO3166LOC["kw"])
    KYRGYZSTAN = PermissibleValue(
        text="KYRGYZSTAN",
        description="Kyrgyzstan",
        meaning=ISO3166LOC["kg"])
    LAOS = PermissibleValue(
        text="LAOS",
        description="Laos",
        meaning=ISO3166LOC["la"])
    LATVIA = PermissibleValue(
        text="LATVIA",
        description="Latvia",
        meaning=ISO3166LOC["lv"])
    LEBANON = PermissibleValue(
        text="LEBANON",
        description="Lebanon",
        meaning=ISO3166LOC["lb"])
    LESOTHO = PermissibleValue(
        text="LESOTHO",
        description="Lesotho",
        meaning=ISO3166LOC["ls"])
    LIBERIA = PermissibleValue(
        text="LIBERIA",
        description="Liberia",
        meaning=ISO3166LOC["lr"])
    LIBYA = PermissibleValue(
        text="LIBYA",
        description="Libya",
        meaning=ISO3166LOC["ly"])
    LIECHTENSTEIN = PermissibleValue(
        text="LIECHTENSTEIN",
        description="Liechtenstein",
        meaning=ISO3166LOC["li"])
    LINE_ISLANDS = PermissibleValue(
        text="LINE_ISLANDS",
        description="Line Islands")
    LITHUANIA = PermissibleValue(
        text="LITHUANIA",
        description="Lithuania",
        meaning=ISO3166LOC["lt"])
    LUXEMBOURG = PermissibleValue(
        text="LUXEMBOURG",
        description="Luxembourg",
        meaning=ISO3166LOC["lu"])
    MACAU = PermissibleValue(
        text="MACAU",
        description="Macau",
        meaning=ISO3166LOC["mo"])
    MADAGASCAR = PermissibleValue(
        text="MADAGASCAR",
        description="Madagascar",
        meaning=ISO3166LOC["mg"])
    MALAWI = PermissibleValue(
        text="MALAWI",
        description="Malawi",
        meaning=ISO3166LOC["mw"])
    MALAYSIA = PermissibleValue(
        text="MALAYSIA",
        description="Malaysia",
        meaning=ISO3166LOC["my"])
    MALDIVES = PermissibleValue(
        text="MALDIVES",
        description="Maldives",
        meaning=ISO3166LOC["mv"])
    MALI = PermissibleValue(
        text="MALI",
        description="Mali",
        meaning=ISO3166LOC["ml"])
    MALTA = PermissibleValue(
        text="MALTA",
        description="Malta",
        meaning=ISO3166LOC["mt"])
    MARSHALL_ISLANDS = PermissibleValue(
        text="MARSHALL_ISLANDS",
        description="Marshall Islands",
        meaning=ISO3166LOC["mh"])
    MARTINIQUE = PermissibleValue(
        text="MARTINIQUE",
        description="Martinique",
        meaning=ISO3166LOC["mq"])
    MAURITANIA = PermissibleValue(
        text="MAURITANIA",
        description="Mauritania",
        meaning=ISO3166LOC["mr"])
    MAURITIUS = PermissibleValue(
        text="MAURITIUS",
        description="Mauritius",
        meaning=ISO3166LOC["mu"])
    MAYOTTE = PermissibleValue(
        text="MAYOTTE",
        description="Mayotte",
        meaning=ISO3166LOC["yt"])
    MEDITERRANEAN_SEA = PermissibleValue(
        text="MEDITERRANEAN_SEA",
        description="Mediterranean Sea",
        meaning=GEONAMES["2593778/"])
    MEXICO = PermissibleValue(
        text="MEXICO",
        description="Mexico",
        meaning=ISO3166LOC["mx"])
    MICRONESIA_FEDERATED_STATES_OF = PermissibleValue(
        text="MICRONESIA_FEDERATED_STATES_OF",
        description="Micronesia, Federated States of",
        meaning=ISO3166LOC["fm"])
    MIDWAY_ISLANDS = PermissibleValue(
        text="MIDWAY_ISLANDS",
        description="Midway Islands",
        meaning=ISO3166LOC["um"])
    MOLDOVA = PermissibleValue(
        text="MOLDOVA",
        description="Moldova",
        meaning=ISO3166LOC["md"])
    MONACO = PermissibleValue(
        text="MONACO",
        description="Monaco",
        meaning=ISO3166LOC["mc"])
    MONGOLIA = PermissibleValue(
        text="MONGOLIA",
        description="Mongolia",
        meaning=ISO3166LOC["mn"])
    MONTENEGRO = PermissibleValue(
        text="MONTENEGRO",
        description="Montenegro",
        meaning=ISO3166LOC["me"])
    MONTSERRAT = PermissibleValue(
        text="MONTSERRAT",
        description="Montserrat",
        meaning=ISO3166LOC["ms"])
    MOROCCO = PermissibleValue(
        text="MOROCCO",
        description="Morocco",
        meaning=ISO3166LOC["ma"])
    MOZAMBIQUE = PermissibleValue(
        text="MOZAMBIQUE",
        description="Mozambique",
        meaning=ISO3166LOC["mz"])
    MYANMAR = PermissibleValue(
        text="MYANMAR",
        description="Myanmar",
        meaning=ISO3166LOC["mm"])
    NAMIBIA = PermissibleValue(
        text="NAMIBIA",
        description="Namibia",
        meaning=ISO3166LOC["na"])
    NAURU = PermissibleValue(
        text="NAURU",
        description="Nauru",
        meaning=ISO3166LOC["nr"])
    NAVASSA_ISLAND = PermissibleValue(
        text="NAVASSA_ISLAND",
        description="Navassa Island",
        meaning=ISO3166LOC["um"])
    NEPAL = PermissibleValue(
        text="NEPAL",
        description="Nepal",
        meaning=ISO3166LOC["np"])
    NETHERLANDS = PermissibleValue(
        text="NETHERLANDS",
        description="Netherlands",
        meaning=ISO3166LOC["nl"])
    NEW_CALEDONIA = PermissibleValue(
        text="NEW_CALEDONIA",
        description="New Caledonia",
        meaning=ISO3166LOC["nc"])
    NEW_ZEALAND = PermissibleValue(
        text="NEW_ZEALAND",
        description="New Zealand",
        meaning=ISO3166LOC["nz"])
    NICARAGUA = PermissibleValue(
        text="NICARAGUA",
        description="Nicaragua",
        meaning=ISO3166LOC["ni"])
    NIGER = PermissibleValue(
        text="NIGER",
        description="Niger",
        meaning=ISO3166LOC["ne"])
    NIGERIA = PermissibleValue(
        text="NIGERIA",
        description="Nigeria",
        meaning=ISO3166LOC["ng"])
    NIUE = PermissibleValue(
        text="NIUE",
        description="Niue",
        meaning=ISO3166LOC["nu"])
    NORFOLK_ISLAND = PermissibleValue(
        text="NORFOLK_ISLAND",
        description="Norfolk Island",
        meaning=ISO3166LOC["nf"])
    NORTH_KOREA = PermissibleValue(
        text="NORTH_KOREA",
        description="North Korea",
        meaning=ISO3166LOC["kp"])
    NORTH_MACEDONIA = PermissibleValue(
        text="NORTH_MACEDONIA",
        description="North Macedonia",
        meaning=ISO3166LOC["mk"])
    NORTH_SEA = PermissibleValue(
        text="NORTH_SEA",
        description="North Sea",
        meaning=GEONAMES["2960848/"])
    NORTHERN_MARIANA_ISLANDS = PermissibleValue(
        text="NORTHERN_MARIANA_ISLANDS",
        description="Northern Mariana Islands",
        meaning=ISO3166LOC["mp"])
    NORWAY = PermissibleValue(
        text="NORWAY",
        description="Norway",
        meaning=ISO3166LOC["no"])
    OMAN = PermissibleValue(
        text="OMAN",
        description="Oman",
        meaning=ISO3166LOC["om"])
    PACIFIC_OCEAN = PermissibleValue(
        text="PACIFIC_OCEAN",
        description="Pacific Ocean",
        meaning=GEONAMES["2363254/"])
    PAKISTAN = PermissibleValue(
        text="PAKISTAN",
        description="Pakistan",
        meaning=ISO3166LOC["pk"])
    PALAU = PermissibleValue(
        text="PALAU",
        description="Palau",
        meaning=ISO3166LOC["pw"])
    PALMYRA_ATOLL = PermissibleValue(
        text="PALMYRA_ATOLL",
        description="Palmyra Atoll",
        meaning=ISO3166LOC["um"])
    PANAMA = PermissibleValue(
        text="PANAMA",
        description="Panama",
        meaning=ISO3166LOC["pa"])
    PAPUA_NEW_GUINEA = PermissibleValue(
        text="PAPUA_NEW_GUINEA",
        description="Papua New Guinea",
        meaning=ISO3166LOC["pg"])
    PARACEL_ISLANDS = PermissibleValue(
        text="PARACEL_ISLANDS",
        description="Paracel Islands")
    PARAGUAY = PermissibleValue(
        text="PARAGUAY",
        description="Paraguay",
        meaning=ISO3166LOC["py"])
    PERU = PermissibleValue(
        text="PERU",
        description="Peru",
        meaning=ISO3166LOC["pe"])
    PHILIPPINES = PermissibleValue(
        text="PHILIPPINES",
        description="Philippines",
        meaning=ISO3166LOC["ph"])
    PITCAIRN_ISLANDS = PermissibleValue(
        text="PITCAIRN_ISLANDS",
        description="Pitcairn Islands",
        meaning=ISO3166LOC["pn"])
    POLAND = PermissibleValue(
        text="POLAND",
        description="Poland",
        meaning=ISO3166LOC["pl"])
    PORTUGAL = PermissibleValue(
        text="PORTUGAL",
        description="Portugal",
        meaning=ISO3166LOC["pt"])
    PUERTO_RICO = PermissibleValue(
        text="PUERTO_RICO",
        description="Puerto Rico",
        meaning=ISO3166LOC["pr"])
    QATAR = PermissibleValue(
        text="QATAR",
        description="Qatar",
        meaning=ISO3166LOC["qa"])
    REPUBLIC_OF_THE_CONGO = PermissibleValue(
        text="REPUBLIC_OF_THE_CONGO",
        description="Republic of the Congo",
        meaning=ISO3166LOC["cg"])
    REUNION = PermissibleValue(
        text="REUNION",
        description="Reunion",
        meaning=ISO3166LOC["re"])
    ROMANIA = PermissibleValue(
        text="ROMANIA",
        description="Romania",
        meaning=ISO3166LOC["ro"])
    ROSS_SEA = PermissibleValue(
        text="ROSS_SEA",
        description="Ross Sea",
        meaning=GEONAMES["4036621/"])
    RUSSIA = PermissibleValue(
        text="RUSSIA",
        description="Russia",
        meaning=ISO3166LOC["ru"])
    RWANDA = PermissibleValue(
        text="RWANDA",
        description="Rwanda",
        meaning=ISO3166LOC["rw"])
    SAINT_BARTHELEMY = PermissibleValue(
        text="SAINT_BARTHELEMY",
        description="Saint Barthelemy",
        meaning=ISO3166LOC["bl"])
    SAINT_HELENA = PermissibleValue(
        text="SAINT_HELENA",
        description="Saint Helena",
        meaning=ISO3166LOC["sh"])
    SAINT_KITTS_AND_NEVIS = PermissibleValue(
        text="SAINT_KITTS_AND_NEVIS",
        description="Saint Kitts and Nevis",
        meaning=ISO3166LOC["kn"])
    SAINT_LUCIA = PermissibleValue(
        text="SAINT_LUCIA",
        description="Saint Lucia",
        meaning=ISO3166LOC["lc"])
    SAINT_MARTIN = PermissibleValue(
        text="SAINT_MARTIN",
        description="Saint Martin",
        meaning=ISO3166LOC["mf"])
    SAINT_PIERRE_AND_MIQUELON = PermissibleValue(
        text="SAINT_PIERRE_AND_MIQUELON",
        description="Saint Pierre and Miquelon",
        meaning=ISO3166LOC["pm"])
    SAINT_VINCENT_AND_THE_GRENADINES = PermissibleValue(
        text="SAINT_VINCENT_AND_THE_GRENADINES",
        description="Saint Vincent and the Grenadines",
        meaning=ISO3166LOC["vc"])
    SAMOA = PermissibleValue(
        text="SAMOA",
        description="Samoa",
        meaning=ISO3166LOC["ws"])
    SAN_MARINO = PermissibleValue(
        text="SAN_MARINO",
        description="San Marino",
        meaning=ISO3166LOC["sm"])
    SAO_TOME_AND_PRINCIPE = PermissibleValue(
        text="SAO_TOME_AND_PRINCIPE",
        description="Sao Tome and Principe",
        meaning=ISO3166LOC["st"])
    SAUDI_ARABIA = PermissibleValue(
        text="SAUDI_ARABIA",
        description="Saudi Arabia",
        meaning=ISO3166LOC["sa"])
    SENEGAL = PermissibleValue(
        text="SENEGAL",
        description="Senegal",
        meaning=ISO3166LOC["sn"])
    SERBIA = PermissibleValue(
        text="SERBIA",
        description="Serbia",
        meaning=ISO3166LOC["rs"])
    SEYCHELLES = PermissibleValue(
        text="SEYCHELLES",
        description="Seychelles",
        meaning=ISO3166LOC["sc"])
    SIERRA_LEONE = PermissibleValue(
        text="SIERRA_LEONE",
        description="Sierra Leone",
        meaning=ISO3166LOC["sl"])
    SINGAPORE = PermissibleValue(
        text="SINGAPORE",
        description="Singapore",
        meaning=ISO3166LOC["sg"])
    SINT_MAARTEN = PermissibleValue(
        text="SINT_MAARTEN",
        description="Sint Maarten",
        meaning=ISO3166LOC["sx"])
    SLOVAKIA = PermissibleValue(
        text="SLOVAKIA",
        description="Slovakia",
        meaning=ISO3166LOC["sk"])
    SLOVENIA = PermissibleValue(
        text="SLOVENIA",
        description="Slovenia",
        meaning=ISO3166LOC["si"])
    SOLOMON_ISLANDS = PermissibleValue(
        text="SOLOMON_ISLANDS",
        description="Solomon Islands",
        meaning=ISO3166LOC["sb"])
    SOMALIA = PermissibleValue(
        text="SOMALIA",
        description="Somalia",
        meaning=ISO3166LOC["so"])
    SOUTH_AFRICA = PermissibleValue(
        text="SOUTH_AFRICA",
        description="South Africa",
        meaning=ISO3166LOC["za"])
    SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS = PermissibleValue(
        text="SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS",
        description="South Georgia and the South Sandwich Islands",
        meaning=ISO3166LOC["gs"])
    SOUTH_KOREA = PermissibleValue(
        text="SOUTH_KOREA",
        description="South Korea",
        meaning=ISO3166LOC["kr"])
    SOUTH_SUDAN = PermissibleValue(
        text="SOUTH_SUDAN",
        description="South Sudan",
        meaning=ISO3166LOC["ss"])
    SOUTHERN_OCEAN = PermissibleValue(
        text="SOUTHERN_OCEAN",
        description="Southern Ocean",
        meaning=GEONAMES["4036776/"])
    SPAIN = PermissibleValue(
        text="SPAIN",
        description="Spain",
        meaning=ISO3166LOC["es"])
    SPRATLY_ISLANDS = PermissibleValue(
        text="SPRATLY_ISLANDS",
        description="Spratly Islands")
    SRI_LANKA = PermissibleValue(
        text="SRI_LANKA",
        description="Sri Lanka",
        meaning=ISO3166LOC["lk"])
    STATE_OF_PALESTINE = PermissibleValue(
        text="STATE_OF_PALESTINE",
        description="State of Palestine",
        meaning=ISO3166LOC["ps"])
    SUDAN = PermissibleValue(
        text="SUDAN",
        description="Sudan",
        meaning=ISO3166LOC["sd"])
    SURINAME = PermissibleValue(
        text="SURINAME",
        description="Suriname",
        meaning=ISO3166LOC["sr"])
    SVALBARD = PermissibleValue(
        text="SVALBARD",
        description="Svalbard")
    SWEDEN = PermissibleValue(
        text="SWEDEN",
        description="Sweden",
        meaning=ISO3166LOC["se"])
    SWITZERLAND = PermissibleValue(
        text="SWITZERLAND",
        description="Switzerland",
        meaning=ISO3166LOC["ch"])
    SYRIA = PermissibleValue(
        text="SYRIA",
        description="Syria",
        meaning=ISO3166LOC["sy"])
    TAIWAN = PermissibleValue(
        text="TAIWAN",
        description="Taiwan",
        meaning=ISO3166LOC["tw"])
    TAJIKISTAN = PermissibleValue(
        text="TAJIKISTAN",
        description="Tajikistan",
        meaning=ISO3166LOC["tj"])
    TANZANIA = PermissibleValue(
        text="TANZANIA",
        description="Tanzania",
        meaning=ISO3166LOC["tz"])
    TASMAN_SEA = PermissibleValue(
        text="TASMAN_SEA",
        description="Tasman Sea",
        meaning=GEONAMES["2363247/"])
    THAILAND = PermissibleValue(
        text="THAILAND",
        description="Thailand",
        meaning=ISO3166LOC["th"])
    TIMOR_LESTE = PermissibleValue(
        text="TIMOR_LESTE",
        description="Timor-Leste",
        meaning=ISO3166LOC["tl"])
    TOGO = PermissibleValue(
        text="TOGO",
        description="Togo",
        meaning=ISO3166LOC["tg"])
    TOKELAU = PermissibleValue(
        text="TOKELAU",
        description="Tokelau",
        meaning=ISO3166LOC["tk"])
    TONGA = PermissibleValue(
        text="TONGA",
        description="Tonga",
        meaning=ISO3166LOC["to"])
    TRINIDAD_AND_TOBAGO = PermissibleValue(
        text="TRINIDAD_AND_TOBAGO",
        description="Trinidad and Tobago",
        meaning=ISO3166LOC["tt"])
    TROMELIN_ISLAND = PermissibleValue(
        text="TROMELIN_ISLAND",
        description="Tromelin Island")
    TUNISIA = PermissibleValue(
        text="TUNISIA",
        description="Tunisia",
        meaning=ISO3166LOC["tn"])
    TURKEY = PermissibleValue(
        text="TURKEY",
        description="Turkey",
        meaning=ISO3166LOC["tr"])
    TURKMENISTAN = PermissibleValue(
        text="TURKMENISTAN",
        description="Turkmenistan",
        meaning=ISO3166LOC["tm"])
    TURKS_AND_CAICOS_ISLANDS = PermissibleValue(
        text="TURKS_AND_CAICOS_ISLANDS",
        description="Turks and Caicos Islands",
        meaning=ISO3166LOC["tc"])
    TUVALU = PermissibleValue(
        text="TUVALU",
        description="Tuvalu",
        meaning=ISO3166LOC["tv"])
    UGANDA = PermissibleValue(
        text="UGANDA",
        description="Uganda",
        meaning=ISO3166LOC["ug"])
    UKRAINE = PermissibleValue(
        text="UKRAINE",
        description="Ukraine",
        meaning=ISO3166LOC["ua"])
    UNITED_ARAB_EMIRATES = PermissibleValue(
        text="UNITED_ARAB_EMIRATES",
        description="United Arab Emirates",
        meaning=ISO3166LOC["ae"])
    UNITED_KINGDOM = PermissibleValue(
        text="UNITED_KINGDOM",
        description="United Kingdom",
        meaning=ISO3166LOC["gb"])
    URUGUAY = PermissibleValue(
        text="URUGUAY",
        description="Uruguay",
        meaning=ISO3166LOC["uy"])
    USA = PermissibleValue(
        text="USA",
        description="USA",
        meaning=ISO3166LOC["us"])
    UZBEKISTAN = PermissibleValue(
        text="UZBEKISTAN",
        description="Uzbekistan",
        meaning=ISO3166LOC["uz"])
    VANUATU = PermissibleValue(
        text="VANUATU",
        description="Vanuatu",
        meaning=ISO3166LOC["vu"])
    VENEZUELA = PermissibleValue(
        text="VENEZUELA",
        description="Venezuela",
        meaning=ISO3166LOC["ve"])
    VIET_NAM = PermissibleValue(
        text="VIET_NAM",
        description="Viet Nam",
        meaning=ISO3166LOC["vn"])
    VIRGIN_ISLANDS = PermissibleValue(
        text="VIRGIN_ISLANDS",
        description="Virgin Islands",
        meaning=ISO3166LOC["vi"])
    WAKE_ISLAND = PermissibleValue(
        text="WAKE_ISLAND",
        description="Wake Island",
        meaning=ISO3166LOC["um"])
    WALLIS_AND_FUTUNA = PermissibleValue(
        text="WALLIS_AND_FUTUNA",
        description="Wallis and Futuna",
        meaning=ISO3166LOC["wf"])
    WEST_BANK = PermissibleValue(
        text="WEST_BANK",
        description="West Bank")
    WESTERN_SAHARA = PermissibleValue(
        text="WESTERN_SAHARA",
        description="Western Sahara",
        meaning=ISO3166LOC["eh"])
    YEMEN = PermissibleValue(
        text="YEMEN",
        description="Yemen",
        meaning=ISO3166LOC["ye"])
    ZAMBIA = PermissibleValue(
        text="ZAMBIA",
        description="Zambia",
        meaning=ISO3166LOC["zm"])
    ZIMBABWE = PermissibleValue(
        text="ZIMBABWE",
        description="Zimbabwe",
        meaning=ISO3166LOC["zw"])

    _defn = EnumDefinition(
        name="InsdcGeographicLocationEnum",
        description="""INSDC controlled vocabulary for geographic locations of collected samples.
Includes countries, oceans, seas, and other geographic regions as defined by INSDC.
Countries use ISO 3166-1 alpha-2 codes from Library of Congress as canonical identifiers.""",
    )

class ViralGenomeTypeEnum(EnumDefinitionImpl):
    """
    Types of viral genomes based on Baltimore classification
    """
    DNA = PermissibleValue(
        text="DNA",
        title="deoxyribonucleic acid",
        description="Viral genome composed of DNA",
        meaning=CHEBI["16991"])
    DSDNA = PermissibleValue(
        text="DSDNA",
        title="Double Stranded DNA Virus",
        description="Double-stranded DNA viral genome",
        meaning=NCIT["C14348"])
    SSDNA = PermissibleValue(
        text="SSDNA",
        title="Single Stranded DNA Virus",
        description="Single-stranded DNA viral genome",
        meaning=NCIT["C14350"])
    RNA = PermissibleValue(
        text="RNA",
        title="ribonucleic acid",
        description="Viral genome composed of RNA",
        meaning=CHEBI["33697"])
    DSRNA = PermissibleValue(
        text="DSRNA",
        title="Double Stranded RNA Virus",
        description="Double-stranded RNA viral genome",
        meaning=NCIT["C28518"])
    SSRNA = PermissibleValue(
        text="SSRNA",
        title="Single-Stranded RNA",
        description="Single-stranded RNA viral genome",
        meaning=NCIT["C95939"])
    SSRNA_POSITIVE = PermissibleValue(
        text="SSRNA_POSITIVE",
        title="Positive Sense ssRNA Virus",
        description="Positive-sense single-stranded RNA viral genome",
        meaning=NCIT["C14351"])
    SSRNA_NEGATIVE = PermissibleValue(
        text="SSRNA_NEGATIVE",
        title="Negative Sense ssRNA Virus",
        description="Negative-sense single-stranded RNA viral genome",
        meaning=NCIT["C14346"])
    SSRNA_RT = PermissibleValue(
        text="SSRNA_RT",
        title="Deltaretrovirus",
        description="Single-stranded RNA viruses that replicate through a DNA intermediate (retroviruses)",
        meaning=NCIT["C14347"])
    DSDNA_RT = PermissibleValue(
        text="DSDNA_RT",
        title="Other Virus Grouping",
        description="""Double-stranded DNA viruses that replicate through a single-stranded RNA intermediate (pararetroviruses)""",
        meaning=NCIT["C14349"])
    MIXED = PermissibleValue(
        text="MIXED",
        title="Hybrid",
        description="Mixed or hybrid viral genome type",
        meaning=NCIT["C128790"])
    UNCHARACTERIZED = PermissibleValue(
        text="UNCHARACTERIZED",
        title="Unknown",
        description="Viral genome type not yet characterized",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="ViralGenomeTypeEnum",
        description="Types of viral genomes based on Baltimore classification",
    )

class PlantSexEnum(EnumDefinitionImpl):
    """
    Plant reproductive and sexual system types
    """
    ANDRODIOECIOUS = PermissibleValue(
        text="ANDRODIOECIOUS",
        title="Androdioecious",
        description="Having male and hermaphrodite flowers on separate plants")
    ANDROECIOUS = PermissibleValue(
        text="ANDROECIOUS",
        title="Androecious",
        description="Having only male flowers")
    ANDROGYNOMONOECIOUS = PermissibleValue(
        text="ANDROGYNOMONOECIOUS",
        title="Androgynomonoecious",
        description="Having male, female, and hermaphrodite flowers on the same plant")
    ANDROGYNOUS = PermissibleValue(
        text="ANDROGYNOUS",
        title="Androgynous",
        description="Having both male and female reproductive organs in the same flower")
    ANDROMONOECIOUS = PermissibleValue(
        text="ANDROMONOECIOUS",
        title="Andromonoecious",
        description="Having male and hermaphrodite flowers on the same plant")
    BISEXUAL = PermissibleValue(
        text="BISEXUAL",
        title="Bisexual",
        description="Having both male and female reproductive organs")
    DICHOGAMOUS = PermissibleValue(
        text="DICHOGAMOUS",
        title="Dichogamous",
        description="Male and female organs mature at different times")
    DICLINOUS = PermissibleValue(
        text="DICLINOUS",
        title="Diclinous",
        description="Having male and female reproductive organs in separate flowers")
    DIOECIOUS = PermissibleValue(
        text="DIOECIOUS",
        title="Dioecious",
        description="Having male and female flowers on separate plants",
        meaning=GSSO["011872"])
    GYNODIOECIOUS = PermissibleValue(
        text="GYNODIOECIOUS",
        title="Gynodioecious",
        description="Having female and hermaphrodite flowers on separate plants")
    GYNOECIOUS = PermissibleValue(
        text="GYNOECIOUS",
        title="Gynoecious",
        description="Having only female flowers")
    GYNOMONOECIOUS = PermissibleValue(
        text="GYNOMONOECIOUS",
        title="Gynomonoecious",
        description="Having female and hermaphrodite flowers on the same plant")
    HERMAPHRODITIC = PermissibleValue(
        text="HERMAPHRODITIC",
        title="hermaphroditic organism",
        description="Having both male and female reproductive organs",
        meaning=UBERON["0007197"])
    IMPERFECT = PermissibleValue(
        text="IMPERFECT",
        title="Imperfect",
        description="Flower lacking either male or female reproductive organs")
    MONOCLINOUS = PermissibleValue(
        text="MONOCLINOUS",
        title="Monoclinous",
        description="Having both male and female reproductive organs in the same flower")
    MONOECIOUS = PermissibleValue(
        text="MONOECIOUS",
        title="Monoecious",
        description="Having male and female flowers on the same plant",
        meaning=GSSO["011868"])
    PERFECT = PermissibleValue(
        text="PERFECT",
        title="Perfect",
        description="Flower having both male and female reproductive organs")
    POLYGAMODIOECIOUS = PermissibleValue(
        text="POLYGAMODIOECIOUS",
        title="Polygamodioecious",
        description="Having male, female, and hermaphrodite flowers on separate plants")
    POLYGAMOMONOECIOUS = PermissibleValue(
        text="POLYGAMOMONOECIOUS",
        title="Polygamomonoecious",
        description="Having male, female, and hermaphrodite flowers on the same plant")
    POLYGAMOUS = PermissibleValue(
        text="POLYGAMOUS",
        title="Polygamous",
        description="Having male, female, and hermaphrodite flowers")
    PROTANDROUS = PermissibleValue(
        text="PROTANDROUS",
        title="Protandrous",
        description="Male organs mature before female organs")
    PROTOGYNOUS = PermissibleValue(
        text="PROTOGYNOUS",
        title="Protogynous",
        description="Female organs mature before male organs")
    SUBANDROECIOUS = PermissibleValue(
        text="SUBANDROECIOUS",
        title="Subandroecious",
        description="Mostly male flowers with occasional hermaphrodite flowers")
    SUBDIOECIOUS = PermissibleValue(
        text="SUBDIOECIOUS",
        title="Subdioecious",
        description="Mostly dioecious with occasional hermaphrodite flowers")
    SUBGYNOECIOUS = PermissibleValue(
        text="SUBGYNOECIOUS",
        title="Subgynoecious",
        description="Mostly female flowers with occasional hermaphrodite flowers")
    SYNOECIOUS = PermissibleValue(
        text="SYNOECIOUS",
        title="Synoecious",
        description="Having male and female organs fused together")
    TRIMONOECIOUS = PermissibleValue(
        text="TRIMONOECIOUS",
        title="Trimonoecious",
        description="Having male, female, and hermaphrodite flowers on the same plant")
    TRIOECIOUS = PermissibleValue(
        text="TRIOECIOUS",
        title="Trioecious",
        description="Having male, female, and hermaphrodite flowers on separate plants")
    UNISEXUAL = PermissibleValue(
        text="UNISEXUAL",
        title="Unisexual",
        description="Having only one sex of reproductive organs")

    _defn = EnumDefinition(
        name="PlantSexEnum",
        description="Plant reproductive and sexual system types",
    )

class RelToOxygenEnum(EnumDefinitionImpl):
    """
    Organism's relationship to oxygen for growth and survival
    """
    AEROBE = PermissibleValue(
        text="AEROBE",
        title="aerobe",
        description="Organism that can survive and grow in an oxygenated environment",
        meaning=ECOCORE["00000173"])
    ANAEROBE = PermissibleValue(
        text="ANAEROBE",
        title="anaerobe",
        description="Organism that does not require oxygen for growth",
        meaning=ECOCORE["00000172"])
    FACULTATIVE = PermissibleValue(
        text="FACULTATIVE",
        title="facultative anaerobe",
        description="Organism that can grow with or without oxygen",
        meaning=ECOCORE["00000177"])
    MICROAEROPHILIC = PermissibleValue(
        text="MICROAEROPHILIC",
        title="microaerophilic",
        description="Organism that requires oxygen at lower concentrations than atmospheric",
        meaning=MICRO["0000515"])
    MICROANAEROBE = PermissibleValue(
        text="MICROANAEROBE",
        title="microanaerobe",
        description="Organism that can tolerate very small amounts of oxygen")
    OBLIGATE_AEROBE = PermissibleValue(
        text="OBLIGATE_AEROBE",
        title="obligate aerobe",
        description="Organism that requires oxygen to grow",
        meaning=ECOCORE["00000179"])
    OBLIGATE_ANAEROBE = PermissibleValue(
        text="OBLIGATE_ANAEROBE",
        title="obligate anaerobe",
        description="Organism that cannot grow in the presence of oxygen",
        meaning=ECOCORE["00000178"])

    _defn = EnumDefinition(
        name="RelToOxygenEnum",
        description="Organism's relationship to oxygen for growth and survival",
    )

class TrophicLevelEnum(EnumDefinitionImpl):
    """
    Trophic levels are the feeding position in a food chain
    """
    AUTOTROPH = PermissibleValue(
        text="AUTOTROPH",
        title="autotroph",
        description="Organism capable of synthesizing its own food from inorganic substances",
        meaning=ECOCORE["00000023"])
    CARBOXYDOTROPH = PermissibleValue(
        text="CARBOXYDOTROPH",
        title="carboxydotroph",
        description="Organism that uses carbon monoxide as a source of carbon and energy")
    CHEMOAUTOLITHOTROPH = PermissibleValue(
        text="CHEMOAUTOLITHOTROPH",
        title="chemoautolithotroph",
        description="Autotroph that obtains energy from inorganic compounds")
    CHEMOAUTOTROPH = PermissibleValue(
        text="CHEMOAUTOTROPH",
        title="chemoautotroph",
        description="Organism that obtains energy by oxidizing inorganic compounds",
        meaning=ECOCORE["00000129"])
    CHEMOHETEROTROPH = PermissibleValue(
        text="CHEMOHETEROTROPH",
        title="chemoheterotroph",
        description="Organism that obtains energy from organic compounds",
        meaning=ECOCORE["00000132"])
    CHEMOLITHOAUTOTROPH = PermissibleValue(
        text="CHEMOLITHOAUTOTROPH",
        title="chemolithoautotroph",
        description="Organism that uses inorganic compounds as electron donors")
    CHEMOLITHOTROPH = PermissibleValue(
        text="CHEMOLITHOTROPH",
        title="chemolithotroph",
        description="Organism that obtains energy from oxidation of inorganic compounds")
    CHEMOORGANOHETEROTROPH = PermissibleValue(
        text="CHEMOORGANOHETEROTROPH",
        title="chemoorganoheterotroph",
        description="Organism that uses organic compounds as both carbon and energy source")
    CHEMOORGANOTROPH = PermissibleValue(
        text="CHEMOORGANOTROPH",
        title="chemoorganotroph",
        description="Organism that obtains energy from organic compounds",
        meaning=ECOCORE["00000133"])
    CHEMOSYNTHETIC = PermissibleValue(
        text="CHEMOSYNTHETIC",
        title="chemosynthetic",
        description="Relating to organisms that produce organic matter through chemosynthesis")
    CHEMOTROPH = PermissibleValue(
        text="CHEMOTROPH",
        title="chemotroph",
        description="Organism that obtains energy from chemical compounds")
    COPIOTROPH = PermissibleValue(
        text="COPIOTROPH",
        title="copiotroph",
        description="Organism that thrives in nutrient-rich environments")
    DIAZOTROPH = PermissibleValue(
        text="DIAZOTROPH",
        title="diazotroph",
        description="Organism capable of fixing atmospheric nitrogen")
    FACULTATIVE = PermissibleValue(
        text="FACULTATIVE",
        title="facultative",
        description="Organism that can switch between different metabolic modes")
    HETEROTROPH = PermissibleValue(
        text="HETEROTROPH",
        title="heterotroph",
        description="Organism that obtains carbon from organic compounds",
        meaning=ECOCORE["00000010"])
    LITHOAUTOTROPH = PermissibleValue(
        text="LITHOAUTOTROPH",
        title="lithoautotroph",
        description="Autotroph that uses inorganic compounds as electron donors")
    LITHOHETEROTROPH = PermissibleValue(
        text="LITHOHETEROTROPH",
        title="lithoheterotroph",
        description="Heterotroph that uses inorganic compounds as electron donors")
    LITHOTROPH = PermissibleValue(
        text="LITHOTROPH",
        title="lithotroph",
        description="Organism that uses inorganic substrates as electron donors")
    METHANOTROPH = PermissibleValue(
        text="METHANOTROPH",
        title="methanotroph",
        description="Organism that uses methane as carbon and energy source")
    METHYLOTROPH = PermissibleValue(
        text="METHYLOTROPH",
        title="methylotroph",
        description="Organism that uses single-carbon compounds")
    MIXOTROPH = PermissibleValue(
        text="MIXOTROPH",
        title="mixotroph",
        description="Organism that can use both autotrophic and heterotrophic methods")
    OBLIGATE = PermissibleValue(
        text="OBLIGATE",
        title="obligate",
        description="Organism restricted to a particular metabolic mode")
    OLIGOTROPH = PermissibleValue(
        text="OLIGOTROPH",
        title="oligotroph",
        description="Organism that thrives in nutrient-poor environments",
        meaning=ECOCORE["00000138"])
    ORGANOHETEROTROPH = PermissibleValue(
        text="ORGANOHETEROTROPH",
        title="organoheterotroph",
        description="Organism that uses organic compounds as carbon source")
    ORGANOTROPH = PermissibleValue(
        text="ORGANOTROPH",
        title="organotroph",
        description="Organism that uses organic compounds as electron donors")
    PHOTOAUTOTROPH = PermissibleValue(
        text="PHOTOAUTOTROPH",
        title="photoautotroph",
        description="Organism that uses light energy to synthesize organic compounds",
        meaning=ECOCORE["00000130"])
    PHOTOHETEROTROPH = PermissibleValue(
        text="PHOTOHETEROTROPH",
        title="photoheterotroph",
        description="Organism that uses light for energy but organic compounds for carbon",
        meaning=ECOCORE["00000131"])
    PHOTOLITHOAUTOTROPH = PermissibleValue(
        text="PHOTOLITHOAUTOTROPH",
        title="photolithoautotroph",
        description="Photoautotroph that uses inorganic electron donors")
    PHOTOLITHOTROPH = PermissibleValue(
        text="PHOTOLITHOTROPH",
        title="photolithotroph",
        description="Organism that uses light energy and inorganic electron donors")
    PHOTOSYNTHETIC = PermissibleValue(
        text="PHOTOSYNTHETIC",
        title="photosynthetic",
        description="Relating to organisms that produce organic matter through photosynthesis")
    PHOTOTROPH = PermissibleValue(
        text="PHOTOTROPH",
        title="phototroph",
        description="Organism that obtains energy from light")

    _defn = EnumDefinition(
        name="TrophicLevelEnum",
        description="Trophic levels are the feeding position in a food chain",
    )

class HumanDevelopmentalStage(EnumDefinitionImpl):

    ZYGOTE_STAGE = PermissibleValue(
        text="ZYGOTE_STAGE",
        title="Carnegie stage 01",
        description="""Embryonic stage defined by a fertilized oocyte and presence of pronuclei. Starts at day 1 post-fertilization.""",
        meaning=HSAPDV["0000003"])
    CLEAVAGE_STAGE = PermissibleValue(
        text="CLEAVAGE_STAGE",
        title="Carnegie stage 02",
        description="""Embryonic stage during which cell division occurs with reduction in cytoplasmic volume, and formation of inner and outer cell mass. 2-8 cells. Usually starts between day 2-3 post-fertilization.""",
        meaning=HSAPDV["0000005"])
    MORULA_STAGE = PermissibleValue(
        text="MORULA_STAGE",
        title="morula stage",
        description="""The later part of Carnegie stage 02 when the cells have coalesced into a mass but the blastocystic cavity has not formed.""",
        meaning=HSAPDV["0000205"])
    BLASTOCYST_STAGE = PermissibleValue(
        text="BLASTOCYST_STAGE",
        title="Carnegie stage 03",
        description="""Blastula stage with the loss of the zona pellucida and the definition of a free blastocyst. Usually starts between day 4-5 post-fertilization.""",
        meaning=HSAPDV["0000007"])
    GASTRULA_STAGE = PermissibleValue(
        text="GASTRULA_STAGE",
        title="gastrula stage",
        description="""Embryonic stage defined by a complex and coordinated series of cellular movements that occurs at the end of cleavage.""",
        meaning=HSAPDV["0000010"])
    NEURULA_STAGE = PermissibleValue(
        text="NEURULA_STAGE",
        title="neurula stage",
        description="""Embryonic stage defined by the formation of a tube from the flat layer of ectodermal cells known as the neural plate. This stage starts the emergence of the central nervous system.""",
        meaning=HSAPDV["0000012"])
    ORGANOGENESIS_STAGE = PermissibleValue(
        text="ORGANOGENESIS_STAGE",
        title="organogenesis stage",
        description="""Embryonic stage at which the ectoderm, endoderm, and mesoderm develop into the internal organs of the organism.""",
        meaning=HSAPDV["0000015"])
    FETAL_STAGE = PermissibleValue(
        text="FETAL_STAGE",
        title="fetal stage",
        description="""Prenatal stage that starts with the fully formed embryo and ends at birth. Generally from 8 weeks post-fertilization until birth.""",
        meaning=HSAPDV["0000037"])
    NEONATAL_STAGE = PermissibleValue(
        text="NEONATAL_STAGE",
        title="newborn stage (0-28 days)",
        description="Immature stage that refers to a human newborn within the first 28 days of life.",
        meaning=HSAPDV["0000262"])
    INFANT_STAGE = PermissibleValue(
        text="INFANT_STAGE",
        title="infant stage",
        description="Immature stage that refers to an infant who is over 28 days and is under 12 months old.",
        meaning=HSAPDV["0000261"])
    TODDLER_STAGE = PermissibleValue(
        text="TODDLER_STAGE",
        title="child stage (1-4 yo)",
        description="""Human stage that refers to a child who is over 12 months and under 5 years old. Often divided into early toddler (1-2 years) and late toddler (2-3 years).""",
        meaning=HSAPDV["0000265"])
    CHILD_STAGE = PermissibleValue(
        text="CHILD_STAGE",
        title="juvenile stage (5-14 yo)",
        description="""Pediatric stage that refers to a human who is over 5 and under 15 years old. Covers elementary and middle school ages.""",
        meaning=HSAPDV["0000271"])
    ADOLESCENT_STAGE = PermissibleValue(
        text="ADOLESCENT_STAGE",
        title="15-19 year-old",
        description="""A young adult stage that refers to an individual who is over 15 and under 20 years old. Period of transition from childhood to adulthood.""",
        meaning=HSAPDV["0000268"])
    ADULT_STAGE = PermissibleValue(
        text="ADULT_STAGE",
        title="adult stage",
        description="""Human developmental stage that refers to a sexually mature human. Starts at approximately 15 years according to HPO definitions.""",
        meaning=HSAPDV["0000258"])
    AGED_STAGE = PermissibleValue(
        text="AGED_STAGE",
        title="late adult stage",
        description="""Late adult stage that refers to an individual who is over 60 and starts to have some age-related impairments. Often subdivided into young-old (60-79) and old-old (80+).""",
        meaning=HSAPDV["0000227"])
    EMBRYONIC_STAGE = PermissibleValue(
        text="EMBRYONIC_STAGE",
        title="embryonic stage",
        description="""Prenatal stage that starts with fertilization and ends with a fully formed embryo, before undergoing last development during the fetal stage. Up to 8 weeks post-fertilization.""",
        meaning=HSAPDV["0000002"])
    PRENATAL_STAGE = PermissibleValue(
        text="PRENATAL_STAGE",
        title="prenatal stage",
        description="""Prenatal stage that starts with fertilization and ends at birth. Encompasses both embryonic and fetal stages.""",
        meaning=HSAPDV["0000045"])
    POSTNATAL_STAGE = PermissibleValue(
        text="POSTNATAL_STAGE",
        title="postnatal stage",
        description="Human developmental stage that covers the whole of human life post birth.",
        meaning=HSAPDV["0010000"])

    _defn = EnumDefinition(
        name="HumanDevelopmentalStage",
    )

class MouseDevelopmentalStage(EnumDefinitionImpl):

    ZYGOTE_STAGE = PermissibleValue(
        text="ZYGOTE_STAGE",
        title="Theiler stage 01",
        description="""Embryonic stage defined by a one-cell embryo (fertilised egg) with zona pellucida present. Embryonic age 0-0.9 dpc (days post coitum).""",
        meaning=MMUSDV["0000003"])
    TWO_CELL_STAGE = PermissibleValue(
        text="TWO_CELL_STAGE",
        title="Theiler stage 02",
        description="Embryonic cleavage stage defined by a dividing 2-4 cells egg. Embryonic age 1 dpc.",
        meaning=MMUSDV["0000005"])
    FOUR_CELL_STAGE = PermissibleValue(
        text="FOUR_CELL_STAGE",
        title="Theiler stage 02",
        description="Part of Theiler stage 02 - dividing egg with 4 cells. Embryonic age approximately 1 dpc.",
        meaning=MMUSDV["0000005"])
    EIGHT_CELL_STAGE = PermissibleValue(
        text="EIGHT_CELL_STAGE",
        title="Theiler stage 03",
        description="Part of early morula stage - dividing egg with 8 cells. Embryonic age approximately 2 dpc.",
        meaning=MMUSDV["0000006"])
    MORULA_STAGE = PermissibleValue(
        text="MORULA_STAGE",
        title="Theiler stage 03",
        description="""Embryonic cleavage stage defined by a dividing 4-16 cells egg, early to fully compacted morula. Embryonic age 2 dpc.""",
        meaning=MMUSDV["0000006"])
    BLASTOCYST_STAGE = PermissibleValue(
        text="BLASTOCYST_STAGE",
        title="Theiler stage 05",
        description="""Embryonic blastula stage defined by a zona free blastocyst (zona pellucida absent). Embryonic age 4 dpc.""",
        meaning=MMUSDV["0000009"])
    GASTRULA_STAGE = PermissibleValue(
        text="GASTRULA_STAGE",
        title="gastrula stage",
        description="""Embryonic stage defined by complex and coordinated series of cellular movements that occurs at the end of cleavage.""",
        meaning=MMUSDV["0000013"])
    NEURULA_STAGE = PermissibleValue(
        text="NEURULA_STAGE",
        title="Theiler stage 11",
        description="""Embryonic stage called presomite stage and defined by the formation of the neural plate. This stage starts the emergence of the central nervous system at embryonic age 7.5 dpc.""",
        meaning=MMUSDV["0000017"])
    ORGANOGENESIS_STAGE = PermissibleValue(
        text="ORGANOGENESIS_STAGE",
        title="organogenesis stage",
        description="""Embryonic stage at which the ectoderm, endoderm, and mesoderm develop into the internal organs of the organism.""",
        meaning=MMUSDV["0000018"])
    E0_5 = PermissibleValue(
        text="E0_5",
        title="Theiler stage 01",
        description="Embryonic day 0.5 - one-cell embryo stage. Corresponds to Theiler stage 01.",
        meaning=MMUSDV["0000003"])
    E9_5 = PermissibleValue(
        text="E9_5",
        title="Theiler stage 16",
        description="""Embryonic day 9.5 - organogenesis stage with visible hind limb buds. Between Theiler stages 15 and 16.""",
        meaning=MMUSDV["0000023"])
    E14_5 = PermissibleValue(
        text="E14_5",
        title="Theiler stage 22",
        description="""Embryonic day 14.5 - late organogenesis with clearly visible fingers and long bones of the limbs present.""",
        meaning=MMUSDV["0000029"])
    P0_NEWBORN = PermissibleValue(
        text="P0_NEWBORN",
        title="Theiler stage 27",
        description="Stage that refers to the newborn mouse, aged E19-20, P0. Used for postnatal days 0 through 3.",
        meaning=MMUSDV["0000036"])
    P21_WEANING = PermissibleValue(
        text="P21_WEANING",
        title="2-week-old stage",
        description="Weaning stage at approximately 21-22 days old. Transition from nursing to independent feeding.",
        meaning=MMUSDV["0000141"])
    P42_JUVENILE = PermissibleValue(
        text="P42_JUVENILE",
        title="6-week-old stage",
        description="""Prime adult stage at 6 weeks (42 days) old. Commonly considered the milestone for sexual maturity.""",
        meaning=MMUSDV["0000151"])
    P56_ADULT = PermissibleValue(
        text="P56_ADULT",
        title="8-week-old stage",
        description="Adult stage at 8 weeks (56 days) old. Fully mature adult mouse.",
        meaning=MMUSDV["0000154"])
    AGED_12_MONTHS = PermissibleValue(
        text="AGED_12_MONTHS",
        title="middle aged stage",
        description="""Middle aged stage for mice over 10 and under 18 months old. Shows progressive age-related changes.""",
        meaning=MMUSDV["0000135"])
    THEILER_STAGE = PermissibleValue(
        text="THEILER_STAGE",
        description="""Reference to any Theiler stage (TS1-TS28) which provides standardized morphological staging for mouse development.""")

    _defn = EnumDefinition(
        name="MouseDevelopmentalStage",
    )

class DayOfWeek(EnumDefinitionImpl):
    """
    Days of the week following ISO 8601 standard (Monday = 1)
    """
    MONDAY = PermissibleValue(
        text="MONDAY",
        description="Monday (first day of week in ISO 8601)",
        meaning=TIME["Monday"])
    TUESDAY = PermissibleValue(
        text="TUESDAY",
        description="Tuesday",
        meaning=TIME["Tuesday"])
    WEDNESDAY = PermissibleValue(
        text="WEDNESDAY",
        description="Wednesday",
        meaning=TIME["Wednesday"])
    THURSDAY = PermissibleValue(
        text="THURSDAY",
        description="Thursday",
        meaning=TIME["Thursday"])
    FRIDAY = PermissibleValue(
        text="FRIDAY",
        description="Friday",
        meaning=TIME["Friday"])
    SATURDAY = PermissibleValue(
        text="SATURDAY",
        description="Saturday",
        meaning=TIME["Saturday"])
    SUNDAY = PermissibleValue(
        text="SUNDAY",
        description="Sunday (last day of week in ISO 8601)",
        meaning=TIME["Sunday"])

    _defn = EnumDefinition(
        name="DayOfWeek",
        description="Days of the week following ISO 8601 standard (Monday = 1)",
    )

class Month(EnumDefinitionImpl):
    """
    Months of the year
    """
    JANUARY = PermissibleValue(
        text="JANUARY",
        description="January",
        meaning=GREG["January"])
    FEBRUARY = PermissibleValue(
        text="FEBRUARY",
        description="February",
        meaning=GREG["February"])
    MARCH = PermissibleValue(
        text="MARCH",
        description="March",
        meaning=GREG["March"])
    APRIL = PermissibleValue(
        text="APRIL",
        description="April",
        meaning=GREG["April"])
    MAY = PermissibleValue(
        text="MAY",
        description="May",
        meaning=GREG["May"])
    JUNE = PermissibleValue(
        text="JUNE",
        description="June",
        meaning=GREG["June"])
    JULY = PermissibleValue(
        text="JULY",
        description="July",
        meaning=GREG["July"])
    AUGUST = PermissibleValue(
        text="AUGUST",
        description="August",
        meaning=GREG["August"])
    SEPTEMBER = PermissibleValue(
        text="SEPTEMBER",
        description="September",
        meaning=GREG["September"])
    OCTOBER = PermissibleValue(
        text="OCTOBER",
        description="October",
        meaning=GREG["October"])
    NOVEMBER = PermissibleValue(
        text="NOVEMBER",
        description="November",
        meaning=GREG["November"])
    DECEMBER = PermissibleValue(
        text="DECEMBER",
        description="December",
        meaning=GREG["December"])

    _defn = EnumDefinition(
        name="Month",
        description="Months of the year",
    )

class Quarter(EnumDefinitionImpl):
    """
    Calendar quarters
    """
    Q1 = PermissibleValue(
        text="Q1",
        description="First quarter (January-March)")
    Q2 = PermissibleValue(
        text="Q2",
        description="Second quarter (April-June)")
    Q3 = PermissibleValue(
        text="Q3",
        description="Third quarter (July-September)")
    Q4 = PermissibleValue(
        text="Q4",
        description="Fourth quarter (October-December)")

    _defn = EnumDefinition(
        name="Quarter",
        description="Calendar quarters",
    )

class Season(EnumDefinitionImpl):
    """
    Seasons of the year (Northern Hemisphere)
    """
    SPRING = PermissibleValue(
        text="SPRING",
        description="Spring season",
        meaning=NCIT["C94731"])
    SUMMER = PermissibleValue(
        text="SUMMER",
        description="Summer season",
        meaning=NCIT["C94732"])
    AUTUMN = PermissibleValue(
        text="AUTUMN",
        description="Autumn/Fall season",
        meaning=NCIT["C94733"])
    WINTER = PermissibleValue(
        text="WINTER",
        description="Winter season",
        meaning=NCIT["C94730"])

    _defn = EnumDefinition(
        name="Season",
        description="Seasons of the year (Northern Hemisphere)",
    )

class TimePeriod(EnumDefinitionImpl):
    """
    Common time periods and intervals
    """
    HOURLY = PermissibleValue(
        text="HOURLY",
        description="Every hour")
    DAILY = PermissibleValue(
        text="DAILY",
        description="Every day")
    WEEKLY = PermissibleValue(
        text="WEEKLY",
        description="Every week")
    BIWEEKLY = PermissibleValue(
        text="BIWEEKLY",
        description="Every two weeks")
    MONTHLY = PermissibleValue(
        text="MONTHLY",
        description="Every month")
    QUARTERLY = PermissibleValue(
        text="QUARTERLY",
        description="Every quarter (3 months)")
    SEMIANNUALLY = PermissibleValue(
        text="SEMIANNUALLY",
        description="Every six months")
    ANNUALLY = PermissibleValue(
        text="ANNUALLY",
        description="Every year")
    BIANNUALLY = PermissibleValue(
        text="BIANNUALLY",
        description="Every two years")

    _defn = EnumDefinition(
        name="TimePeriod",
        description="Common time periods and intervals",
    )

class TimeOfDay(EnumDefinitionImpl):
    """
    Common times of day
    """
    DAWN = PermissibleValue(
        text="DAWN",
        description="Dawn (first light)")
    MORNING = PermissibleValue(
        text="MORNING",
        description="Morning")
    NOON = PermissibleValue(
        text="NOON",
        description="Noon/Midday")
    AFTERNOON = PermissibleValue(
        text="AFTERNOON",
        description="Afternoon")
    EVENING = PermissibleValue(
        text="EVENING",
        description="Evening")
    NIGHT = PermissibleValue(
        text="NIGHT",
        description="Night")
    MIDNIGHT = PermissibleValue(
        text="MIDNIGHT",
        description="Midnight")

    _defn = EnumDefinition(
        name="TimeOfDay",
        description="Common times of day",
    )

class BusinessTimeFrame(EnumDefinitionImpl):
    """
    Common business and financial time frames
    """
    REAL_TIME = PermissibleValue(
        text="REAL_TIME",
        description="Real-time/instantaneous")
    INTRADAY = PermissibleValue(
        text="INTRADAY",
        description="Within the same day")
    T_PLUS_1 = PermissibleValue(
        text="T_PLUS_1",
        description="Trade date plus one business day")
    T_PLUS_2 = PermissibleValue(
        text="T_PLUS_2",
        description="Trade date plus two business days")
    T_PLUS_3 = PermissibleValue(
        text="T_PLUS_3",
        description="Trade date plus three business days")
    END_OF_DAY = PermissibleValue(
        text="END_OF_DAY",
        description="End of business day")
    END_OF_WEEK = PermissibleValue(
        text="END_OF_WEEK",
        description="End of business week")
    END_OF_MONTH = PermissibleValue(
        text="END_OF_MONTH",
        description="End of calendar month")
    END_OF_QUARTER = PermissibleValue(
        text="END_OF_QUARTER",
        description="End of calendar quarter")
    END_OF_YEAR = PermissibleValue(
        text="END_OF_YEAR",
        description="End of calendar year")
    YEAR_TO_DATE = PermissibleValue(
        text="YEAR_TO_DATE",
        description="From beginning of year to current date")
    MONTH_TO_DATE = PermissibleValue(
        text="MONTH_TO_DATE",
        description="From beginning of month to current date")
    QUARTER_TO_DATE = PermissibleValue(
        text="QUARTER_TO_DATE",
        description="From beginning of quarter to current date")

    _defn = EnumDefinition(
        name="BusinessTimeFrame",
        description="Common business and financial time frames",
    )

class GeologicalEra(EnumDefinitionImpl):
    """
    Major geological eras
    """
    PRECAMBRIAN = PermissibleValue(
        text="PRECAMBRIAN",
        description="Precambrian (4.6 billion - 541 million years ago)")
    PALEOZOIC = PermissibleValue(
        text="PALEOZOIC",
        description="Paleozoic Era (541 - 252 million years ago)")
    MESOZOIC = PermissibleValue(
        text="MESOZOIC",
        description="Mesozoic Era (252 - 66 million years ago)")
    CENOZOIC = PermissibleValue(
        text="CENOZOIC",
        description="Cenozoic Era (66 million years ago - present)")

    _defn = EnumDefinition(
        name="GeologicalEra",
        description="Major geological eras",
    )

class HistoricalPeriod(EnumDefinitionImpl):
    """
    Major historical periods
    """
    PREHISTORIC = PermissibleValue(
        text="PREHISTORIC",
        description="Before written records")
    ANCIENT = PermissibleValue(
        text="ANCIENT",
        description="Ancient history (3000 BCE - 500 CE)")
    CLASSICAL_ANTIQUITY = PermissibleValue(
        text="CLASSICAL_ANTIQUITY",
        description="Classical antiquity (8th century BCE - 6th century CE)")
    MIDDLE_AGES = PermissibleValue(
        text="MIDDLE_AGES",
        description="Middle Ages (5th - 15th century)")
    RENAISSANCE = PermissibleValue(
        text="RENAISSANCE",
        description="Renaissance (14th - 17th century)")
    EARLY_MODERN = PermissibleValue(
        text="EARLY_MODERN",
        description="Early modern period (15th - 18th century)")
    INDUSTRIAL_AGE = PermissibleValue(
        text="INDUSTRIAL_AGE",
        description="Industrial age (1760 - 1840)")
    MODERN = PermissibleValue(
        text="MODERN",
        description="Modern era (19th century - mid 20th century)")
    CONTEMPORARY = PermissibleValue(
        text="CONTEMPORARY",
        description="Contemporary period (mid 20th century - present)")
    DIGITAL_AGE = PermissibleValue(
        text="DIGITAL_AGE",
        description="Digital/Information age (1950s - present)")

    _defn = EnumDefinition(
        name="HistoricalPeriod",
        description="Major historical periods",
    )

class PublicationType(EnumDefinitionImpl):
    """
    Types of academic and research publications
    """
    JOURNAL_ARTICLE = PermissibleValue(
        text="JOURNAL_ARTICLE",
        description="Peer-reviewed journal article",
        meaning=FABIO["JournalArticle"])
    REVIEW_ARTICLE = PermissibleValue(
        text="REVIEW_ARTICLE",
        description="Review article synthesizing existing research",
        meaning=FABIO["ReviewArticle"])
    RESEARCH_ARTICLE = PermissibleValue(
        text="RESEARCH_ARTICLE",
        description="Original research article",
        meaning=FABIO["ResearchPaper"])
    SHORT_COMMUNICATION = PermissibleValue(
        text="SHORT_COMMUNICATION",
        description="Brief communication or short report",
        meaning=FABIO["BriefCommunication"])
    EDITORIAL = PermissibleValue(
        text="EDITORIAL",
        description="Editorial or opinion piece",
        meaning=FABIO["Editorial"])
    LETTER = PermissibleValue(
        text="LETTER",
        description="Letter to the editor",
        meaning=FABIO["Letter"])
    COMMENTARY = PermissibleValue(
        text="COMMENTARY",
        description="Commentary on existing work",
        meaning=FABIO["Comment"])
    PERSPECTIVE = PermissibleValue(
        text="PERSPECTIVE",
        description="Perspective or viewpoint article",
        meaning=FABIO["Comment"])
    CASE_REPORT = PermissibleValue(
        text="CASE_REPORT",
        description="Clinical or scientific case report",
        meaning=FABIO["CaseReport"])
    TECHNICAL_NOTE = PermissibleValue(
        text="TECHNICAL_NOTE",
        description="Technical or methodological note",
        meaning=FABIO["BriefCommunication"])
    BOOK = PermissibleValue(
        text="BOOK",
        description="Complete book or monograph",
        meaning=FABIO["Book"])
    BOOK_CHAPTER = PermissibleValue(
        text="BOOK_CHAPTER",
        description="Chapter in an edited book",
        meaning=FABIO["BookChapter"])
    EDITED_BOOK = PermissibleValue(
        text="EDITED_BOOK",
        description="Edited collection or anthology",
        meaning=FABIO["EditedBook"])
    REFERENCE_BOOK = PermissibleValue(
        text="REFERENCE_BOOK",
        description="Reference work or encyclopedia",
        meaning=FABIO["ReferenceBook"])
    TEXTBOOK = PermissibleValue(
        text="TEXTBOOK",
        description="Educational textbook",
        meaning=FABIO["Textbook"])
    CONFERENCE_PAPER = PermissibleValue(
        text="CONFERENCE_PAPER",
        description="Full conference paper",
        meaning=FABIO["ConferencePaper"])
    CONFERENCE_ABSTRACT = PermissibleValue(
        text="CONFERENCE_ABSTRACT",
        description="Conference abstract",
        meaning=FABIO["ConferenceAbstract"])
    CONFERENCE_POSTER = PermissibleValue(
        text="CONFERENCE_POSTER",
        description="Conference poster",
        meaning=FABIO["ConferencePoster"])
    CONFERENCE_PROCEEDINGS = PermissibleValue(
        text="CONFERENCE_PROCEEDINGS",
        description="Complete conference proceedings",
        meaning=FABIO["ConferenceProceedings"])
    PHD_THESIS = PermissibleValue(
        text="PHD_THESIS",
        description="Doctoral dissertation",
        meaning=FABIO["DoctoralThesis"])
    MASTERS_THESIS = PermissibleValue(
        text="MASTERS_THESIS",
        description="Master's thesis",
        meaning=FABIO["MastersThesis"])
    BACHELORS_THESIS = PermissibleValue(
        text="BACHELORS_THESIS",
        description="Bachelor's or undergraduate thesis",
        meaning=FABIO["BachelorsThesis"])
    TECHNICAL_REPORT = PermissibleValue(
        text="TECHNICAL_REPORT",
        description="Technical or research report",
        meaning=FABIO["TechnicalReport"])
    WORKING_PAPER = PermissibleValue(
        text="WORKING_PAPER",
        description="Working paper or discussion paper",
        meaning=FABIO["WorkingPaper"])
    WHITE_PAPER = PermissibleValue(
        text="WHITE_PAPER",
        description="White paper or position paper",
        meaning=FABIO["WhitePaper"])
    POLICY_BRIEF = PermissibleValue(
        text="POLICY_BRIEF",
        description="Policy brief or recommendation",
        meaning=FABIO["PolicyBrief"])
    DATASET = PermissibleValue(
        text="DATASET",
        description="Research dataset",
        meaning=DCMITYPE["Dataset"])
    SOFTWARE = PermissibleValue(
        text="SOFTWARE",
        description="Research software or code",
        meaning=DCMITYPE["Software"])
    DATA_PAPER = PermissibleValue(
        text="DATA_PAPER",
        description="Data descriptor or data paper",
        meaning=FABIO["DataPaper"])
    SOFTWARE_PAPER = PermissibleValue(
        text="SOFTWARE_PAPER",
        description="Software or tools paper",
        meaning=FABIO["ResearchPaper"])
    PROTOCOL = PermissibleValue(
        text="PROTOCOL",
        description="Research protocol or methodology",
        meaning=FABIO["Protocol"])
    PREPRINT = PermissibleValue(
        text="PREPRINT",
        description="Preprint or unrefereed manuscript",
        meaning=FABIO["Preprint"])
    POSTPRINT = PermissibleValue(
        text="POSTPRINT",
        description="Accepted manuscript after peer review",
        meaning=FABIO["Preprint"])
    PUBLISHED_VERSION = PermissibleValue(
        text="PUBLISHED_VERSION",
        title="publication",
        description="Final published version",
        meaning=IAO["0000311"])
    PATENT = PermissibleValue(
        text="PATENT",
        description="Patent or patent application",
        meaning=FABIO["Patent"])
    STANDARD = PermissibleValue(
        text="STANDARD",
        description="Technical standard or specification",
        meaning=FABIO["Standard"])
    BLOG_POST = PermissibleValue(
        text="BLOG_POST",
        description="Academic blog post",
        meaning=FABIO["BlogPost"])
    PRESENTATION = PermissibleValue(
        text="PRESENTATION",
        description="Presentation slides or talk",
        meaning=FABIO["Presentation"])
    LECTURE = PermissibleValue(
        text="LECTURE",
        description="Lecture or educational material",
        meaning=FABIO["Presentation"])
    ANNOTATION = PermissibleValue(
        text="ANNOTATION",
        description="Annotation or scholarly note",
        meaning=FABIO["Annotation"])

    _defn = EnumDefinition(
        name="PublicationType",
        description="Types of academic and research publications",
    )

class PeerReviewStatus(EnumDefinitionImpl):
    """
    Status of peer review process
    """
    NOT_PEER_REVIEWED = PermissibleValue(
        text="NOT_PEER_REVIEWED",
        description="Not peer reviewed")
    SUBMITTED = PermissibleValue(
        text="SUBMITTED",
        description="Submitted for review")
    UNDER_REVIEW = PermissibleValue(
        text="UNDER_REVIEW",
        title="ongoing",
        description="Currently under peer review",
        meaning=SIO["000035"])
    REVIEW_COMPLETE = PermissibleValue(
        text="REVIEW_COMPLETE",
        title="completed",
        description="Peer review complete",
        meaning=SIO["000034"])
    MAJOR_REVISION = PermissibleValue(
        text="MAJOR_REVISION",
        description="Major revisions requested")
    MINOR_REVISION = PermissibleValue(
        text="MINOR_REVISION",
        description="Minor revisions requested")
    ACCEPTED = PermissibleValue(
        text="ACCEPTED",
        description="Accepted for publication")
    ACCEPTED_WITH_REVISIONS = PermissibleValue(
        text="ACCEPTED_WITH_REVISIONS",
        description="Conditionally accepted pending revisions")
    REJECTED = PermissibleValue(
        text="REJECTED",
        description="Rejected after review")
    WITHDRAWN = PermissibleValue(
        text="WITHDRAWN",
        description="Withdrawn by authors")
    PUBLISHED = PermissibleValue(
        text="PUBLISHED",
        title="publication",
        description="Published after review",
        meaning=IAO["0000311"])

    _defn = EnumDefinition(
        name="PeerReviewStatus",
        description="Status of peer review process",
    )

class AcademicDegree(EnumDefinitionImpl):
    """
    Academic degrees and qualifications
    """
    BA = PermissibleValue(
        text="BA",
        title="Bachelor of Arts",
        meaning=NCIT["C71345"])
    BS = PermissibleValue(
        text="BS",
        description="Bachelor of Science",
        meaning=NCIT["C71351"])
    BSC = PermissibleValue(
        text="BSC",
        description="Bachelor of Science (British)",
        meaning=NCIT["C71351"])
    BENG = PermissibleValue(
        text="BENG",
        description="Bachelor of Engineering",
        meaning=NCIT["C71347"])
    BFA = PermissibleValue(
        text="BFA",
        description="Bachelor of Fine Arts",
        meaning=NCIT["C71349"])
    LLB = PermissibleValue(
        text="LLB",
        description="Bachelor of Laws",
        meaning=NCIT["C71352"])
    MBBS = PermissibleValue(
        text="MBBS",
        description="Bachelor of Medicine, Bachelor of Surgery",
        meaning=NCIT["C39383"])
    MA = PermissibleValue(
        text="MA",
        description="Master of Arts",
        meaning=NCIT["C71364"])
    MS = PermissibleValue(
        text="MS",
        description="Master of Science",
        meaning=NCIT["C39452"])
    MSC = PermissibleValue(
        text="MSC",
        description="Master of Science (British)",
        meaning=NCIT["C39452"])
    MBA = PermissibleValue(
        text="MBA",
        description="Master of Business Administration",
        meaning=NCIT["C39449"])
    MFA = PermissibleValue(
        text="MFA",
        description="Master of Fine Arts")
    MPH = PermissibleValue(
        text="MPH",
        description="Master of Public Health",
        meaning=NCIT["C39451"])
    MENG = PermissibleValue(
        text="MENG",
        description="Master of Engineering",
        meaning=NCIT["C71368"])
    MED = PermissibleValue(
        text="MED",
        description="Master of Education",
        meaning=NCIT["C71369"])
    LLM = PermissibleValue(
        text="LLM",
        description="Master of Laws",
        meaning=NCIT["C71363"])
    MPHIL = PermissibleValue(
        text="MPHIL",
        description="Master of Philosophy")
    PHD = PermissibleValue(
        text="PHD",
        description="Doctor of Philosophy",
        meaning=NCIT["C39387"])
    MD = PermissibleValue(
        text="MD",
        description="Doctor of Medicine",
        meaning=NCIT["C39383"])
    JD = PermissibleValue(
        text="JD",
        description="Juris Doctor",
        meaning=NCIT["C71361"])
    EDD = PermissibleValue(
        text="EDD",
        description="Doctor of Education",
        meaning=NCIT["C71359"])
    PSYD = PermissibleValue(
        text="PSYD",
        description="Doctor of Psychology")
    DBA = PermissibleValue(
        text="DBA",
        description="Doctor of Business Administration")
    DPHIL = PermissibleValue(
        text="DPHIL",
        description="Doctor of Philosophy (Oxford/Sussex)",
        meaning=NCIT["C39387"])
    SCD = PermissibleValue(
        text="SCD",
        description="Doctor of Science",
        meaning=NCIT["C71379"])
    POSTDOC = PermissibleValue(
        text="POSTDOC",
        description="Postdoctoral researcher")

    _defn = EnumDefinition(
        name="AcademicDegree",
        description="Academic degrees and qualifications",
    )

class LicenseType(EnumDefinitionImpl):
    """
    Common software and content licenses
    """
    MIT = PermissibleValue(
        text="MIT",
        description="MIT License",
        meaning=SPDX["MIT"])
    APACHE_2_0 = PermissibleValue(
        text="APACHE_2_0",
        description="Apache License 2.0",
        meaning=SPDX["Apache-2.0"])
    BSD_3_CLAUSE = PermissibleValue(
        text="BSD_3_CLAUSE",
        description="BSD 3-Clause License",
        meaning=SPDX["BSD-3-Clause"])
    BSD_2_CLAUSE = PermissibleValue(
        text="BSD_2_CLAUSE",
        description="BSD 2-Clause License",
        meaning=SPDX["BSD-2-Clause"])
    ISC = PermissibleValue(
        text="ISC",
        description="ISC License",
        meaning=SPDX["ISC"])
    GPL_3_0 = PermissibleValue(
        text="GPL_3_0",
        description="GNU General Public License v3.0",
        meaning=SPDX["GPL-3.0"])
    GPL_2_0 = PermissibleValue(
        text="GPL_2_0",
        description="GNU General Public License v2.0",
        meaning=SPDX["GPL-2.0"])
    LGPL_3_0 = PermissibleValue(
        text="LGPL_3_0",
        description="GNU Lesser General Public License v3.0",
        meaning=SPDX["LGPL-3.0"])
    LGPL_2_1 = PermissibleValue(
        text="LGPL_2_1",
        description="GNU Lesser General Public License v2.1",
        meaning=SPDX["LGPL-2.1"])
    AGPL_3_0 = PermissibleValue(
        text="AGPL_3_0",
        description="GNU Affero General Public License v3.0",
        meaning=SPDX["AGPL-3.0"])
    MPL_2_0 = PermissibleValue(
        text="MPL_2_0",
        description="Mozilla Public License 2.0",
        meaning=SPDX["MPL-2.0"])
    CC_BY_4_0 = PermissibleValue(
        text="CC_BY_4_0",
        description="Creative Commons Attribution 4.0",
        meaning=SPDX["CC-BY-4.0"])
    CC_BY_SA_4_0 = PermissibleValue(
        text="CC_BY_SA_4_0",
        description="Creative Commons Attribution-ShareAlike 4.0",
        meaning=SPDX["CC-BY-SA-4.0"])
    CC_BY_NC_4_0 = PermissibleValue(
        text="CC_BY_NC_4_0",
        description="Creative Commons Attribution-NonCommercial 4.0",
        meaning=SPDX["CC-BY-NC-4.0"])
    CC_BY_NC_SA_4_0 = PermissibleValue(
        text="CC_BY_NC_SA_4_0",
        description="Creative Commons Attribution-NonCommercial-ShareAlike 4.0",
        meaning=SPDX["CC-BY-NC-SA-4.0"])
    CC_BY_ND_4_0 = PermissibleValue(
        text="CC_BY_ND_4_0",
        description="Creative Commons Attribution-NoDerivatives 4.0",
        meaning=SPDX["CC-BY-ND-4.0"])
    CC0_1_0 = PermissibleValue(
        text="CC0_1_0",
        description="Creative Commons Zero v1.0 Universal",
        meaning=SPDX["CC0-1.0"])
    UNLICENSE = PermissibleValue(
        text="UNLICENSE",
        description="The Unlicense",
        meaning=SPDX["Unlicense"])
    PROPRIETARY = PermissibleValue(
        text="PROPRIETARY",
        description="Proprietary/All rights reserved")
    CUSTOM = PermissibleValue(
        text="CUSTOM",
        description="Custom license terms")

    _defn = EnumDefinition(
        name="LicenseType",
        description="Common software and content licenses",
    )

class ResearchField(EnumDefinitionImpl):
    """
    Major research fields and disciplines
    """
    PHYSICS = PermissibleValue(
        text="PHYSICS",
        description="Physics",
        meaning=NCIT["C16989"])
    CHEMISTRY = PermissibleValue(
        text="CHEMISTRY",
        description="Chemistry",
        meaning=NCIT["C16414"])
    BIOLOGY = PermissibleValue(
        text="BIOLOGY",
        description="Biology",
        meaning=NCIT["C16345"])
    MATHEMATICS = PermissibleValue(
        text="MATHEMATICS",
        description="Mathematics",
        meaning=NCIT["C16825"])
    EARTH_SCIENCES = PermissibleValue(
        text="EARTH_SCIENCES",
        description="Earth sciences and geology")
    ASTRONOMY = PermissibleValue(
        text="ASTRONOMY",
        description="Astronomy and astrophysics")
    MEDICINE = PermissibleValue(
        text="MEDICINE",
        description="Medicine and health sciences",
        meaning=NCIT["C16833"])
    NEUROSCIENCE = PermissibleValue(
        text="NEUROSCIENCE",
        title="Neuroscience and Neuropsychiatric Research",
        description="Neuroscience",
        meaning=NCIT["C15817"])
    GENETICS = PermissibleValue(
        text="GENETICS",
        description="Genetics and genomics",
        meaning=NCIT["C16624"])
    ECOLOGY = PermissibleValue(
        text="ECOLOGY",
        title="Ecology",
        description="Ecology and environmental science",
        meaning=NCIT["C16526"])
    MICROBIOLOGY = PermissibleValue(
        text="MICROBIOLOGY",
        title="Microbiology",
        meaning=NCIT["C16851"])
    BIOCHEMISTRY = PermissibleValue(
        text="BIOCHEMISTRY",
        title="Biochemistry",
        meaning=NCIT["C16337"])
    COMPUTER_SCIENCE = PermissibleValue(
        text="COMPUTER_SCIENCE",
        description="Computer science")
    ENGINEERING = PermissibleValue(
        text="ENGINEERING",
        description="Engineering")
    MATERIALS_SCIENCE = PermissibleValue(
        text="MATERIALS_SCIENCE",
        description="Materials science")
    ARTIFICIAL_INTELLIGENCE = PermissibleValue(
        text="ARTIFICIAL_INTELLIGENCE",
        description="Artificial intelligence and machine learning")
    ROBOTICS = PermissibleValue(
        text="ROBOTICS",
        description="Robotics")
    PSYCHOLOGY = PermissibleValue(
        text="PSYCHOLOGY",
        description="Psychology")
    SOCIOLOGY = PermissibleValue(
        text="SOCIOLOGY",
        description="Sociology")
    ECONOMICS = PermissibleValue(
        text="ECONOMICS",
        description="Economics")
    POLITICAL_SCIENCE = PermissibleValue(
        text="POLITICAL_SCIENCE",
        description="Political science")
    ANTHROPOLOGY = PermissibleValue(
        text="ANTHROPOLOGY",
        description="Anthropology")
    EDUCATION = PermissibleValue(
        text="EDUCATION",
        description="Education")
    HISTORY = PermissibleValue(
        text="HISTORY",
        description="History")
    PHILOSOPHY = PermissibleValue(
        text="PHILOSOPHY",
        description="Philosophy")
    LITERATURE = PermissibleValue(
        text="LITERATURE",
        description="Literature")
    LINGUISTICS = PermissibleValue(
        text="LINGUISTICS",
        description="Linguistics")
    ART = PermissibleValue(
        text="ART",
        description="Art and art history")
    MUSIC = PermissibleValue(
        text="MUSIC",
        description="Music and musicology")
    BIOINFORMATICS = PermissibleValue(
        text="BIOINFORMATICS",
        description="Bioinformatics")
    COMPUTATIONAL_BIOLOGY = PermissibleValue(
        text="COMPUTATIONAL_BIOLOGY",
        description="Computational biology")
    DATA_SCIENCE = PermissibleValue(
        text="DATA_SCIENCE",
        description="Data science")
    COGNITIVE_SCIENCE = PermissibleValue(
        text="COGNITIVE_SCIENCE",
        description="Cognitive science")
    ENVIRONMENTAL_SCIENCE = PermissibleValue(
        text="ENVIRONMENTAL_SCIENCE",
        description="Environmental science")
    PUBLIC_HEALTH = PermissibleValue(
        text="PUBLIC_HEALTH",
        description="Public health")

    _defn = EnumDefinition(
        name="ResearchField",
        description="Major research fields and disciplines",
    )

class FundingType(EnumDefinitionImpl):
    """
    Types of research funding
    """
    GRANT = PermissibleValue(
        text="GRANT",
        description="Research grant")
    CONTRACT = PermissibleValue(
        text="CONTRACT",
        description="Research contract")
    FELLOWSHIP = PermissibleValue(
        text="FELLOWSHIP",
        title="Fellowship Program",
        description="Fellowship or scholarship",
        meaning=NCIT["C20003"])
    AWARD = PermissibleValue(
        text="AWARD",
        description="Prize or award")
    GIFT = PermissibleValue(
        text="GIFT",
        description="Gift or donation")
    INTERNAL = PermissibleValue(
        text="INTERNAL",
        description="Internal/institutional funding")
    INDUSTRY = PermissibleValue(
        text="INDUSTRY",
        description="Industry sponsorship")
    GOVERNMENT = PermissibleValue(
        text="GOVERNMENT",
        description="Government funding")
    FOUNDATION = PermissibleValue(
        text="FOUNDATION",
        description="Foundation or charity funding")
    CROWDFUNDING = PermissibleValue(
        text="CROWDFUNDING",
        description="Crowdfunded research")

    _defn = EnumDefinition(
        name="FundingType",
        description="Types of research funding",
    )

class ManuscriptSection(EnumDefinitionImpl):
    """
    Sections of a scientific manuscript or publication
    """
    TITLE = PermissibleValue(
        text="TITLE",
        title="document title",
        meaning=IAO["0000305"])
    AUTHORS = PermissibleValue(
        text="AUTHORS",
        title="author list",
        description="Authors and affiliations",
        meaning=IAO["0000321"])
    ABSTRACT = PermissibleValue(
        text="ABSTRACT",
        description="Abstract",
        meaning=IAO["0000315"])
    KEYWORDS = PermissibleValue(
        text="KEYWORDS",
        title="keywords section",
        meaning=IAO["0000630"])
    INTRODUCTION = PermissibleValue(
        text="INTRODUCTION",
        title="introduction to a publication about an investigation",
        description="Introduction/Background",
        meaning=IAO["0000316"])
    LITERATURE_REVIEW = PermissibleValue(
        text="LITERATURE_REVIEW",
        title="related work section",
        description="Literature review",
        meaning=IAO["0000639"])
    METHODS = PermissibleValue(
        text="METHODS",
        title="methods section",
        description="Methods/Materials and Methods",
        meaning=IAO["0000317"])
    RESULTS = PermissibleValue(
        text="RESULTS",
        title="results section",
        meaning=IAO["0000318"])
    DISCUSSION = PermissibleValue(
        text="DISCUSSION",
        title="discussion section of a publication about an investigation",
        meaning=IAO["0000319"])
    CONCLUSIONS = PermissibleValue(
        text="CONCLUSIONS",
        title="conclusion section",
        description="Conclusions",
        meaning=IAO["0000615"])
    RESULTS_AND_DISCUSSION = PermissibleValue(
        text="RESULTS_AND_DISCUSSION",
        description="Combined Results and Discussion")
    ACKNOWLEDGMENTS = PermissibleValue(
        text="ACKNOWLEDGMENTS",
        title="acknowledgements section",
        description="Acknowledgments",
        meaning=IAO["0000324"])
    REFERENCES = PermissibleValue(
        text="REFERENCES",
        title="references section",
        description="References/Bibliography",
        meaning=IAO["0000320"])
    APPENDICES = PermissibleValue(
        text="APPENDICES",
        title="supplementary material to a document",
        description="Appendices",
        meaning=IAO["0000326"])
    SUPPLEMENTARY_MATERIAL = PermissibleValue(
        text="SUPPLEMENTARY_MATERIAL",
        title="supplementary material to a document",
        description="Supplementary material",
        meaning=IAO["0000326"])
    DATA_AVAILABILITY = PermissibleValue(
        text="DATA_AVAILABILITY",
        title="availability section",
        description="Data availability statement",
        meaning=IAO["0000611"])
    CODE_AVAILABILITY = PermissibleValue(
        text="CODE_AVAILABILITY",
        title="availability section",
        description="Code availability statement",
        meaning=IAO["0000611"])
    AUTHOR_CONTRIBUTIONS = PermissibleValue(
        text="AUTHOR_CONTRIBUTIONS",
        title="author contributions section",
        description="Author contributions",
        meaning=IAO["0000323"])
    CONFLICT_OF_INTEREST = PermissibleValue(
        text="CONFLICT_OF_INTEREST",
        title="conflict of interest section",
        description="Conflict of interest statement",
        meaning=IAO["0000616"])
    FUNDING = PermissibleValue(
        text="FUNDING",
        title="funding source declaration section",
        description="Funding information",
        meaning=IAO["0000623"])
    ETHICS_STATEMENT = PermissibleValue(
        text="ETHICS_STATEMENT",
        title="ethical approval section",
        description="Ethics approval statement",
        meaning=IAO["0000620"])
    SYSTEMATIC_REVIEW_METHODS = PermissibleValue(
        text="SYSTEMATIC_REVIEW_METHODS",
        description="Systematic review methodology (PRISMA)")
    META_ANALYSIS = PermissibleValue(
        text="META_ANALYSIS",
        description="Meta-analysis section")
    STUDY_PROTOCOL = PermissibleValue(
        text="STUDY_PROTOCOL",
        description="Study protocol")
    CONSORT_FLOW_DIAGRAM = PermissibleValue(
        text="CONSORT_FLOW_DIAGRAM",
        description="CONSORT flow diagram")
    HIGHLIGHTS = PermissibleValue(
        text="HIGHLIGHTS",
        description="Highlights/Key points")
    GRAPHICAL_ABSTRACT = PermissibleValue(
        text="GRAPHICAL_ABSTRACT",
        description="Graphical abstract",
        meaning=IAO["0000707"])
    LAY_SUMMARY = PermissibleValue(
        text="LAY_SUMMARY",
        title="author summary section",
        description="Lay summary/Plain language summary",
        meaning=IAO["0000609"])
    BOX = PermissibleValue(
        text="BOX",
        description="Box/Sidebar with supplementary information")
    CASE_PRESENTATION = PermissibleValue(
        text="CASE_PRESENTATION",
        title="case report section",
        description="Case presentation (for case reports)",
        meaning=IAO["0000613"])
    LIMITATIONS = PermissibleValue(
        text="LIMITATIONS",
        title="study limitations section",
        description="Limitations section",
        meaning=IAO["0000631"])
    FUTURE_DIRECTIONS = PermissibleValue(
        text="FUTURE_DIRECTIONS",
        title="future directions section",
        description="Future directions/Future work",
        meaning=IAO["0000625"])
    GLOSSARY = PermissibleValue(
        text="GLOSSARY",
        description="Glossary of terms")
    ABBREVIATIONS = PermissibleValue(
        text="ABBREVIATIONS",
        title="abbreviations section",
        description="List of abbreviations",
        meaning=IAO["0000606"])
    OTHER_MAIN_TEXT = PermissibleValue(
        text="OTHER_MAIN_TEXT",
        description="Other main text section")
    OTHER_SUPPLEMENTARY = PermissibleValue(
        text="OTHER_SUPPLEMENTARY",
        description="Other supplementary section")

    _defn = EnumDefinition(
        name="ManuscriptSection",
        description="Sections of a scientific manuscript or publication",
    )

class ResearchRole(EnumDefinitionImpl):
    """
    Roles in research and authorship
    """
    CONCEPTUALIZATION = PermissibleValue(
        text="CONCEPTUALIZATION",
        description="Ideas; formulation of research goals",
        meaning=CREDIT["conceptualization"])
    DATA_CURATION = PermissibleValue(
        text="DATA_CURATION",
        description="Data management and annotation",
        meaning=CREDIT["data-curation"])
    FORMAL_ANALYSIS = PermissibleValue(
        text="FORMAL_ANALYSIS",
        description="Statistical and mathematical analysis",
        meaning=CREDIT["formal-analysis"])
    FUNDING_ACQUISITION = PermissibleValue(
        text="FUNDING_ACQUISITION",
        description="Acquisition of financial support",
        meaning=CREDIT["funding-acquisition"])
    INVESTIGATION = PermissibleValue(
        text="INVESTIGATION",
        description="Conducting research and data collection",
        meaning=CREDIT["investigation"])
    METHODOLOGY = PermissibleValue(
        text="METHODOLOGY",
        description="Development of methodology",
        meaning=CREDIT["methodology"])
    PROJECT_ADMINISTRATION = PermissibleValue(
        text="PROJECT_ADMINISTRATION",
        description="Project management and coordination",
        meaning=CREDIT["project-administration"])
    RESOURCES = PermissibleValue(
        text="RESOURCES",
        description="Provision of materials and tools",
        meaning=CREDIT["resources"])
    SOFTWARE = PermissibleValue(
        text="SOFTWARE",
        description="Programming and software development",
        meaning=CREDIT["software"])
    SUPERVISION = PermissibleValue(
        text="SUPERVISION",
        description="Oversight and mentorship",
        meaning=CREDIT["supervision"])
    VALIDATION = PermissibleValue(
        text="VALIDATION",
        description="Verification of results",
        meaning=CREDIT["validation"])
    VISUALIZATION = PermissibleValue(
        text="VISUALIZATION",
        description="Data presentation and visualization",
        meaning=CREDIT["visualization"])
    WRITING_ORIGINAL = PermissibleValue(
        text="WRITING_ORIGINAL",
        description="Writing - original draft",
        meaning=CREDIT["writing-original-draft"])
    WRITING_REVIEW = PermissibleValue(
        text="WRITING_REVIEW",
        description="Writing - review and editing",
        meaning=CREDIT["writing-review-editing"])
    FIRST_AUTHOR = PermissibleValue(
        text="FIRST_AUTHOR",
        description="First/lead author",
        meaning=MS["1002034"])
    CORRESPONDING_AUTHOR = PermissibleValue(
        text="CORRESPONDING_AUTHOR",
        title="Corresponding Author indicator",
        meaning=NCIT["C164481"])
    SENIOR_AUTHOR = PermissibleValue(
        text="SENIOR_AUTHOR",
        description="Senior/last author")
    CO_AUTHOR = PermissibleValue(
        text="CO_AUTHOR",
        title="Author",
        description="Co-author",
        meaning=NCIT["C42781"])
    PRINCIPAL_INVESTIGATOR = PermissibleValue(
        text="PRINCIPAL_INVESTIGATOR",
        description="Principal investigator (PI)",
        meaning=NCIT["C19924"])
    CO_INVESTIGATOR = PermissibleValue(
        text="CO_INVESTIGATOR",
        title="Co-Investigator",
        meaning=NCIT["C51812"])
    COLLABORATOR = PermissibleValue(
        text="COLLABORATOR",
        title="Collaborator",
        meaning=NCIT["C84336"])

    _defn = EnumDefinition(
        name="ResearchRole",
        description="Roles in research and authorship",
    )

class OpenAccessType(EnumDefinitionImpl):
    """
    Types of open access publishing
    """
    GOLD = PermissibleValue(
        text="GOLD",
        description="Gold open access (published OA)")
    GREEN = PermissibleValue(
        text="GREEN",
        description="Green open access (self-archived)")
    HYBRID = PermissibleValue(
        text="HYBRID",
        description="Hybrid journal with OA option")
    DIAMOND = PermissibleValue(
        text="DIAMOND",
        description="Diamond/platinum OA (no fees)")
    BRONZE = PermissibleValue(
        text="BRONZE",
        description="Free to read but no license")
    CLOSED = PermissibleValue(
        text="CLOSED",
        description="Closed access/subscription only")
    EMBARGO = PermissibleValue(
        text="EMBARGO",
        description="Under embargo period")

    _defn = EnumDefinition(
        name="OpenAccessType",
        description="Types of open access publishing",
    )

class CitationStyle(EnumDefinitionImpl):
    """
    Common citation and reference styles
    """
    APA = PermissibleValue(
        text="APA",
        description="American Psychological Association")
    MLA = PermissibleValue(
        text="MLA",
        description="Modern Language Association")
    CHICAGO = PermissibleValue(
        text="CHICAGO",
        description="Chicago Manual of Style")
    HARVARD = PermissibleValue(
        text="HARVARD",
        description="Harvard referencing")
    VANCOUVER = PermissibleValue(
        text="VANCOUVER",
        description="Vancouver style (biomedical)")
    IEEE = PermissibleValue(
        text="IEEE",
        description="Institute of Electrical and Electronics Engineers")
    ACS = PermissibleValue(
        text="ACS",
        description="American Chemical Society")
    AMA = PermissibleValue(
        text="AMA",
        description="American Medical Association")
    NATURE = PermissibleValue(
        text="NATURE",
        description="Nature style")
    SCIENCE = PermissibleValue(
        text="SCIENCE",
        description="Science style")
    CELL = PermissibleValue(
        text="CELL",
        description="Cell Press style")

    _defn = EnumDefinition(
        name="CitationStyle",
        description="Common citation and reference styles",
    )

class EnergySource(EnumDefinitionImpl):
    """
    Types of energy sources and generation methods
    """
    SOLAR = PermissibleValue(
        text="SOLAR",
        title="Solar energy (photovoltaic and thermal)",
        meaning=ENVO["01001862"])
    WIND = PermissibleValue(
        text="WIND",
        title="Wind power")
    HYDROELECTRIC = PermissibleValue(
        text="HYDROELECTRIC",
        title="Hydroelectric power")
    GEOTHERMAL = PermissibleValue(
        text="GEOTHERMAL",
        title="Geothermal energy",
        meaning=ENVO["2000034"])
    BIOMASS = PermissibleValue(
        text="BIOMASS",
        title="Biomass and bioenergy")
    BIOFUEL = PermissibleValue(
        text="BIOFUEL",
        title="Biofuels (ethanol, biodiesel)")
    TIDAL = PermissibleValue(
        text="TIDAL",
        title="Tidal and wave energy")
    HYDROGEN = PermissibleValue(
        text="HYDROGEN",
        title="Hydrogen fuel",
        meaning=CHEBI["18276"])
    COAL = PermissibleValue(
        text="COAL",
        title="Coal",
        meaning=ENVO["02000091"])
    NATURAL_GAS = PermissibleValue(
        text="NATURAL_GAS",
        title="Natural gas",
        meaning=ENVO["01000552"])
    PETROLEUM = PermissibleValue(
        text="PETROLEUM",
        title="Petroleum/oil",
        meaning=ENVO["00002984"])
    DIESEL = PermissibleValue(
        text="DIESEL",
        title="Diesel fuel",
        meaning=ENVO["03510006"])
    GASOLINE = PermissibleValue(
        text="GASOLINE",
        title="Gasoline/petrol")
    PROPANE = PermissibleValue(
        text="PROPANE",
        title="Propane/LPG",
        meaning=ENVO["01000553"])
    NUCLEAR_FISSION = PermissibleValue(
        text="NUCLEAR_FISSION",
        title="Nuclear fission")
    NUCLEAR_FUSION = PermissibleValue(
        text="NUCLEAR_FUSION",
        title="Nuclear fusion (experimental)")
    GRID_MIX = PermissibleValue(
        text="GRID_MIX",
        title="Grid electricity (mixed sources)")
    BATTERY_STORAGE = PermissibleValue(
        text="BATTERY_STORAGE",
        description="Battery storage systems")

    _defn = EnumDefinition(
        name="EnergySource",
        description="Types of energy sources and generation methods",
    )

class EnergyUnit(EnumDefinitionImpl):
    """
    Units for measuring energy
    """
    JOULE = PermissibleValue(
        text="JOULE",
        description="Joule (J)",
        meaning=QUDT["J"])
    KILOJOULE = PermissibleValue(
        text="KILOJOULE",
        description="Kilojoule (kJ)",
        meaning=QUDT["KiloJ"])
    MEGAJOULE = PermissibleValue(
        text="MEGAJOULE",
        description="Megajoule (MJ)",
        meaning=QUDT["MegaJ"])
    GIGAJOULE = PermissibleValue(
        text="GIGAJOULE",
        description="Gigajoule (GJ)",
        meaning=QUDT["GigaJ"])
    WATT_HOUR = PermissibleValue(
        text="WATT_HOUR",
        description="Watt-hour (Wh)",
        meaning=QUDT["W-HR"])
    KILOWATT_HOUR = PermissibleValue(
        text="KILOWATT_HOUR",
        description="Kilowatt-hour (kWh)",
        meaning=QUDT["KiloW-HR"])
    MEGAWATT_HOUR = PermissibleValue(
        text="MEGAWATT_HOUR",
        description="Megawatt-hour (MWh)",
        meaning=QUDT["MegaW-HR"])
    GIGAWATT_HOUR = PermissibleValue(
        text="GIGAWATT_HOUR",
        description="Gigawatt-hour (GWh)",
        meaning=QUDT["GigaW-HR"])
    TERAWATT_HOUR = PermissibleValue(
        text="TERAWATT_HOUR",
        description="Terawatt-hour (TWh)",
        meaning=QUDT["TeraW-HR"])
    CALORIE = PermissibleValue(
        text="CALORIE",
        description="Calorie (cal)",
        meaning=QUDT["CAL"])
    KILOCALORIE = PermissibleValue(
        text="KILOCALORIE",
        description="Kilocalorie (kcal)",
        meaning=QUDT["KiloCAL"])
    BTU = PermissibleValue(
        text="BTU",
        description="British thermal unit",
        meaning=QUDT["BTU_IT"])
    THERM = PermissibleValue(
        text="THERM",
        description="Therm",
        meaning=QUDT["THM_US"])
    ELECTRON_VOLT = PermissibleValue(
        text="ELECTRON_VOLT",
        description="Electron volt (eV)",
        meaning=QUDT["EV"])
    TOE = PermissibleValue(
        text="TOE",
        description="Tonne of oil equivalent",
        meaning=QUDT["TOE"])
    TCE = PermissibleValue(
        text="TCE",
        description="Tonne of coal equivalent")

    _defn = EnumDefinition(
        name="EnergyUnit",
        description="Units for measuring energy",
    )

class PowerUnit(EnumDefinitionImpl):
    """
    Units for measuring power (energy per time)
    """
    WATT = PermissibleValue(
        text="WATT",
        description="Watt (W)",
        meaning=QUDT["W"])
    KILOWATT = PermissibleValue(
        text="KILOWATT",
        description="Kilowatt (kW)",
        meaning=QUDT["KiloW"])
    MEGAWATT = PermissibleValue(
        text="MEGAWATT",
        description="Megawatt (MW)",
        meaning=QUDT["MegaW"])
    GIGAWATT = PermissibleValue(
        text="GIGAWATT",
        description="Gigawatt (GW)",
        meaning=QUDT["GigaW"])
    TERAWATT = PermissibleValue(
        text="TERAWATT",
        description="Terawatt (TW)",
        meaning=QUDT["TeraW"])
    HORSEPOWER = PermissibleValue(
        text="HORSEPOWER",
        description="Horsepower",
        meaning=QUDT["HP"])
    BTU_PER_HOUR = PermissibleValue(
        text="BTU_PER_HOUR",
        description="BTU per hour")

    _defn = EnumDefinition(
        name="PowerUnit",
        description="Units for measuring power (energy per time)",
    )

class EnergyEfficiencyRating(EnumDefinitionImpl):
    """
    Energy efficiency ratings and standards
    """
    A_PLUS_PLUS_PLUS = PermissibleValue(
        text="A_PLUS_PLUS_PLUS",
        description="A+++ (highest efficiency)")
    A_PLUS_PLUS = PermissibleValue(
        text="A_PLUS_PLUS",
        description="A++")
    A_PLUS = PermissibleValue(
        text="A_PLUS",
        description="A+")
    A = PermissibleValue(
        text="A",
        description="A")
    B = PermissibleValue(
        text="B",
        description="B")
    C = PermissibleValue(
        text="C",
        description="C")
    D = PermissibleValue(
        text="D",
        description="D")
    E = PermissibleValue(
        text="E",
        description="E")
    F = PermissibleValue(
        text="F",
        description="F")
    G = PermissibleValue(
        text="G",
        description="G (lowest efficiency)")
    ENERGY_STAR = PermissibleValue(
        text="ENERGY_STAR",
        description="Energy Star certified")
    ENERGY_STAR_MOST_EFFICIENT = PermissibleValue(
        text="ENERGY_STAR_MOST_EFFICIENT",
        description="Energy Star Most Efficient")

    _defn = EnumDefinition(
        name="EnergyEfficiencyRating",
        description="Energy efficiency ratings and standards",
    )

class BuildingEnergyStandard(EnumDefinitionImpl):
    """
    Building energy efficiency standards and certifications
    """
    PASSIVE_HOUSE = PermissibleValue(
        text="PASSIVE_HOUSE",
        description="Passive House (Passivhaus) standard")
    LEED_PLATINUM = PermissibleValue(
        text="LEED_PLATINUM",
        description="LEED Platinum certification")
    LEED_GOLD = PermissibleValue(
        text="LEED_GOLD",
        description="LEED Gold certification")
    LEED_SILVER = PermissibleValue(
        text="LEED_SILVER",
        description="LEED Silver certification")
    LEED_CERTIFIED = PermissibleValue(
        text="LEED_CERTIFIED",
        description="LEED Certified")
    BREEAM_OUTSTANDING = PermissibleValue(
        text="BREEAM_OUTSTANDING",
        description="BREEAM Outstanding")
    BREEAM_EXCELLENT = PermissibleValue(
        text="BREEAM_EXCELLENT",
        description="BREEAM Excellent")
    BREEAM_VERY_GOOD = PermissibleValue(
        text="BREEAM_VERY_GOOD",
        description="BREEAM Very Good")
    BREEAM_GOOD = PermissibleValue(
        text="BREEAM_GOOD",
        description="BREEAM Good")
    BREEAM_PASS = PermissibleValue(
        text="BREEAM_PASS",
        description="BREEAM Pass")
    NET_ZERO = PermissibleValue(
        text="NET_ZERO",
        description="Net Zero Energy Building")
    ENERGY_POSITIVE = PermissibleValue(
        text="ENERGY_POSITIVE",
        description="Energy Positive Building")
    ZERO_CARBON = PermissibleValue(
        text="ZERO_CARBON",
        description="Zero Carbon Building")

    _defn = EnumDefinition(
        name="BuildingEnergyStandard",
        description="Building energy efficiency standards and certifications",
    )

class GridType(EnumDefinitionImpl):
    """
    Types of electrical grid systems
    """
    MAIN_GRID = PermissibleValue(
        text="MAIN_GRID",
        description="Main utility grid")
    MICROGRID = PermissibleValue(
        text="MICROGRID",
        description="Microgrid")
    OFF_GRID = PermissibleValue(
        text="OFF_GRID",
        description="Off-grid/standalone")
    SMART_GRID = PermissibleValue(
        text="SMART_GRID",
        description="Smart grid")
    MINI_GRID = PermissibleValue(
        text="MINI_GRID",
        description="Mini-grid")
    VIRTUAL_POWER_PLANT = PermissibleValue(
        text="VIRTUAL_POWER_PLANT",
        description="Virtual power plant")

    _defn = EnumDefinition(
        name="GridType",
        description="Types of electrical grid systems",
    )

class EnergyStorageType(EnumDefinitionImpl):
    """
    Types of energy storage systems
    """
    LITHIUM_ION_BATTERY = PermissibleValue(
        text="LITHIUM_ION_BATTERY",
        description="Lithium-ion battery")
    LEAD_ACID_BATTERY = PermissibleValue(
        text="LEAD_ACID_BATTERY",
        description="Lead-acid battery")
    FLOW_BATTERY = PermissibleValue(
        text="FLOW_BATTERY",
        description="Flow battery (e.g., vanadium redox)")
    SOLID_STATE_BATTERY = PermissibleValue(
        text="SOLID_STATE_BATTERY",
        description="Solid-state battery")
    SODIUM_ION_BATTERY = PermissibleValue(
        text="SODIUM_ION_BATTERY",
        description="Sodium-ion battery")
    PUMPED_HYDRO = PermissibleValue(
        text="PUMPED_HYDRO",
        description="Pumped hydroelectric storage")
    COMPRESSED_AIR = PermissibleValue(
        text="COMPRESSED_AIR",
        description="Compressed air energy storage (CAES)")
    FLYWHEEL = PermissibleValue(
        text="FLYWHEEL",
        description="Flywheel energy storage")
    GRAVITY_STORAGE = PermissibleValue(
        text="GRAVITY_STORAGE",
        description="Gravity-based storage")
    MOLTEN_SALT = PermissibleValue(
        text="MOLTEN_SALT",
        description="Molten salt thermal storage")
    ICE_STORAGE = PermissibleValue(
        text="ICE_STORAGE",
        description="Ice thermal storage")
    PHASE_CHANGE = PermissibleValue(
        text="PHASE_CHANGE",
        description="Phase change materials")
    HYDROGEN_STORAGE = PermissibleValue(
        text="HYDROGEN_STORAGE",
        description="Hydrogen storage")
    SYNTHETIC_FUEL = PermissibleValue(
        text="SYNTHETIC_FUEL",
        description="Synthetic fuel storage")
    SUPERCAPACITOR = PermissibleValue(
        text="SUPERCAPACITOR",
        description="Supercapacitor")
    SUPERCONDUCTING = PermissibleValue(
        text="SUPERCONDUCTING",
        description="Superconducting magnetic energy storage (SMES)")

    _defn = EnumDefinition(
        name="EnergyStorageType",
        description="Types of energy storage systems",
    )

class EmissionScope(EnumDefinitionImpl):
    """
    Greenhouse gas emission scopes (GHG Protocol)
    """
    SCOPE_1 = PermissibleValue(
        text="SCOPE_1",
        description="Direct emissions from owned or controlled sources")
    SCOPE_2 = PermissibleValue(
        text="SCOPE_2",
        description="Indirect emissions from purchased energy")
    SCOPE_3 = PermissibleValue(
        text="SCOPE_3",
        description="All other indirect emissions in value chain")
    SCOPE_3_UPSTREAM = PermissibleValue(
        text="SCOPE_3_UPSTREAM",
        description="Upstream Scope 3 emissions")
    SCOPE_3_DOWNSTREAM = PermissibleValue(
        text="SCOPE_3_DOWNSTREAM",
        description="Downstream Scope 3 emissions")

    _defn = EnumDefinition(
        name="EmissionScope",
        description="Greenhouse gas emission scopes (GHG Protocol)",
    )

class CarbonIntensity(EnumDefinitionImpl):
    """
    Carbon intensity levels for energy sources
    """
    ZERO_CARBON = PermissibleValue(
        text="ZERO_CARBON",
        description="Zero carbon emissions")
    VERY_LOW_CARBON = PermissibleValue(
        text="VERY_LOW_CARBON",
        description="Very low carbon (< 50 gCO2/kWh)")
    LOW_CARBON = PermissibleValue(
        text="LOW_CARBON",
        description="Low carbon (50-200 gCO2/kWh)")
    MEDIUM_CARBON = PermissibleValue(
        text="MEDIUM_CARBON",
        description="Medium carbon (200-500 gCO2/kWh)")
    HIGH_CARBON = PermissibleValue(
        text="HIGH_CARBON",
        description="High carbon (500-1000 gCO2/kWh)")
    VERY_HIGH_CARBON = PermissibleValue(
        text="VERY_HIGH_CARBON",
        description="Very high carbon (> 1000 gCO2/kWh)")

    _defn = EnumDefinition(
        name="CarbonIntensity",
        description="Carbon intensity levels for energy sources",
    )

class ElectricityMarket(EnumDefinitionImpl):
    """
    Types of electricity markets and pricing
    """
    SPOT_MARKET = PermissibleValue(
        text="SPOT_MARKET",
        description="Spot market/real-time pricing")
    DAY_AHEAD = PermissibleValue(
        text="DAY_AHEAD",
        description="Day-ahead market")
    INTRADAY = PermissibleValue(
        text="INTRADAY",
        description="Intraday market")
    FUTURES = PermissibleValue(
        text="FUTURES",
        description="Futures market")
    CAPACITY_MARKET = PermissibleValue(
        text="CAPACITY_MARKET",
        description="Capacity market")
    ANCILLARY_SERVICES = PermissibleValue(
        text="ANCILLARY_SERVICES",
        description="Ancillary services market")
    BILATERAL = PermissibleValue(
        text="BILATERAL",
        description="Bilateral contracts")
    FEED_IN_TARIFF = PermissibleValue(
        text="FEED_IN_TARIFF",
        description="Feed-in tariff")
    NET_METERING = PermissibleValue(
        text="NET_METERING",
        description="Net metering")
    POWER_PURCHASE_AGREEMENT = PermissibleValue(
        text="POWER_PURCHASE_AGREEMENT",
        description="Power purchase agreement (PPA)")

    _defn = EnumDefinition(
        name="ElectricityMarket",
        description="Types of electricity markets and pricing",
    )

class FossilFuelTypeEnum(EnumDefinitionImpl):
    """
    Types of fossil fuels used for energy generation
    """
    COAL = PermissibleValue(
        text="COAL",
        title="Coal",
        description="Coal",
        meaning=ENVO["02000091"])
    NATURAL_GAS = PermissibleValue(
        text="NATURAL_GAS",
        title="Natural Gas",
        description="Natural gas",
        meaning=ENVO["01000552"])
    PETROLEUM = PermissibleValue(
        text="PETROLEUM",
        title="Petroleum",
        description="Petroleum",
        meaning=ENVO["00002984"])

    _defn = EnumDefinition(
        name="FossilFuelTypeEnum",
        description="Types of fossil fuels used for energy generation",
    )

class ReactorTypeEnum(EnumDefinitionImpl):
    """
    Nuclear reactor types based on design and operational characteristics
    """
    PWR = PermissibleValue(
        text="PWR",
        title="Pressurized Water Reactor",
        description="Most common reactor type using light water under pressure")
    BWR = PermissibleValue(
        text="BWR",
        title="Boiling Water Reactor",
        description="Light water reactor where water boils directly in core")
    PHWR = PermissibleValue(
        text="PHWR",
        title="Pressurized Heavy Water Reactor",
        description="Heavy water moderated and cooled reactor (CANDU type)")
    LWGR = PermissibleValue(
        text="LWGR",
        title="Light Water Graphite Reactor",
        description="Graphite moderated, light water cooled reactor (RBMK type)")
    AGR = PermissibleValue(
        text="AGR",
        title="Advanced Gas-Cooled Reactor",
        description="Graphite moderated, CO2 gas cooled reactor")
    GCR = PermissibleValue(
        text="GCR",
        title="Gas-Cooled Reactor",
        description="Early gas-cooled reactor design (Magnox type)")
    FBR = PermissibleValue(
        text="FBR",
        title="Fast Breeder Reactor",
        description="Fast neutron reactor that breeds fissile material")
    HTGR = PermissibleValue(
        text="HTGR",
        title="High Temperature Gas-Cooled Reactor",
        description="Helium-cooled reactor with TRISO fuel")
    MSR = PermissibleValue(
        text="MSR",
        title="Molten Salt Reactor",
        description="Reactor using molten salt as coolant and/or fuel")
    SMR = PermissibleValue(
        text="SMR",
        title="Small Modular Reactor",
        description="Small reactors designed for modular construction")
    VHTR = PermissibleValue(
        text="VHTR",
        title="Very High Temperature Reactor",
        description="Generation IV reactor for very high temperature applications")
    SFR = PermissibleValue(
        text="SFR",
        title="Sodium-Cooled Fast Reactor",
        description="Fast reactor cooled by liquid sodium")
    LFR = PermissibleValue(
        text="LFR",
        title="Lead-Cooled Fast Reactor",
        description="Fast reactor cooled by liquid lead or lead-bismuth")
    GFR = PermissibleValue(
        text="GFR",
        title="Gas-Cooled Fast Reactor",
        description="Fast reactor with gas cooling")
    SCWR = PermissibleValue(
        text="SCWR",
        title="Supercritical Water-Cooled Reactor",
        description="Reactor using supercritical water as coolant")

    _defn = EnumDefinition(
        name="ReactorTypeEnum",
        description="Nuclear reactor types based on design and operational characteristics",
    )

class ReactorGenerationEnum(EnumDefinitionImpl):
    """
    Nuclear reactor generational classifications
    """
    GENERATION_I = PermissibleValue(
        text="GENERATION_I",
        title="Generation I",
        description="Early commercial reactors (1950s-1960s)")
    GENERATION_II = PermissibleValue(
        text="GENERATION_II",
        title="Generation II",
        description="Current operating commercial reactors")
    GENERATION_III = PermissibleValue(
        text="GENERATION_III",
        title="Generation III",
        description="Advanced reactors with enhanced safety")
    GENERATION_III_PLUS = PermissibleValue(
        text="GENERATION_III_PLUS",
        title="Generation III+",
        description="Evolutionary improvements to Generation III")
    GENERATION_IV = PermissibleValue(
        text="GENERATION_IV",
        title="Generation IV",
        description="Next generation advanced reactor concepts")

    _defn = EnumDefinition(
        name="ReactorGenerationEnum",
        description="Nuclear reactor generational classifications",
    )

class ReactorCoolantEnum(EnumDefinitionImpl):
    """
    Primary coolant types used in nuclear reactors
    """
    LIGHT_WATER = PermissibleValue(
        text="LIGHT_WATER",
        title="Light Water (H2O)",
        description="Ordinary water as primary coolant")
    HEAVY_WATER = PermissibleValue(
        text="HEAVY_WATER",
        title="Heavy Water (D2O)",
        description="Deuterium oxide as primary coolant")
    CARBON_DIOXIDE = PermissibleValue(
        text="CARBON_DIOXIDE",
        title="Carbon Dioxide",
        description="CO2 gas as primary coolant")
    HELIUM = PermissibleValue(
        text="HELIUM",
        title="Helium",
        description="Helium gas as primary coolant")
    LIQUID_SODIUM = PermissibleValue(
        text="LIQUID_SODIUM",
        title="Liquid Sodium",
        description="Molten sodium metal as coolant")
    LIQUID_LEAD = PermissibleValue(
        text="LIQUID_LEAD",
        title="Liquid Lead",
        description="Molten lead or lead-bismuth as coolant")
    MOLTEN_SALT = PermissibleValue(
        text="MOLTEN_SALT",
        title="Molten Salt",
        description="Molten fluoride or chloride salts")
    SUPERCRITICAL_WATER = PermissibleValue(
        text="SUPERCRITICAL_WATER",
        title="Supercritical Water",
        description="Water above critical point")

    _defn = EnumDefinition(
        name="ReactorCoolantEnum",
        description="Primary coolant types used in nuclear reactors",
    )

class ReactorModeratorEnum(EnumDefinitionImpl):
    """
    Neutron moderator types used in nuclear reactors
    """
    LIGHT_WATER = PermissibleValue(
        text="LIGHT_WATER",
        title="Light Water (H2O)",
        description="Ordinary water as neutron moderator")
    HEAVY_WATER = PermissibleValue(
        text="HEAVY_WATER",
        title="Heavy Water (D2O)",
        description="Deuterium oxide as neutron moderator")
    GRAPHITE = PermissibleValue(
        text="GRAPHITE",
        title="Graphite",
        description="Carbon graphite as neutron moderator")
    BERYLLIUM = PermissibleValue(
        text="BERYLLIUM",
        title="Beryllium",
        description="Beryllium metal as neutron moderator")
    NONE = PermissibleValue(
        text="NONE",
        title="No Moderator",
        description="Fast reactors with no neutron moderation")

    _defn = EnumDefinition(
        name="ReactorModeratorEnum",
        description="Neutron moderator types used in nuclear reactors",
    )

class ReactorNeutronSpectrumEnum(EnumDefinitionImpl):
    """
    Neutron energy spectrum classifications
    """
    THERMAL = PermissibleValue(
        text="THERMAL",
        title="Thermal Neutron Spectrum",
        description="Low energy neutrons in thermal equilibrium")
    EPITHERMAL = PermissibleValue(
        text="EPITHERMAL",
        title="Epithermal Neutron Spectrum",
        description="Intermediate energy neutrons")
    FAST = PermissibleValue(
        text="FAST",
        title="Fast Neutron Spectrum",
        description="High energy neutrons from fission")

    _defn = EnumDefinition(
        name="ReactorNeutronSpectrumEnum",
        description="Neutron energy spectrum classifications",
    )

class ReactorSizeCategoryEnum(EnumDefinitionImpl):
    """
    Nuclear reactor size classifications
    """
    LARGE = PermissibleValue(
        text="LARGE",
        title="Large Reactor",
        description="Traditional large-scale commercial reactors")
    MEDIUM = PermissibleValue(
        text="MEDIUM",
        title="Medium Reactor",
        description="Mid-scale reactors")
    SMALL = PermissibleValue(
        text="SMALL",
        title="Small Reactor",
        description="Small modular reactors")
    MICRO = PermissibleValue(
        text="MICRO",
        title="Micro Reactor",
        description="Very small reactors for remote applications")
    RESEARCH = PermissibleValue(
        text="RESEARCH",
        title="Research Reactor",
        description="Small reactors for research and isotope production")

    _defn = EnumDefinition(
        name="ReactorSizeCategoryEnum",
        description="Nuclear reactor size classifications",
    )

class NuclearFuelTypeEnum(EnumDefinitionImpl):
    """
    Types of nuclear fuel materials and compositions
    """
    NATURAL_URANIUM = PermissibleValue(
        text="NATURAL_URANIUM",
        title="Natural Uranium",
        description="Uranium as found in nature (0.711% U-235)",
        meaning=CHEBI["27214"])
    LOW_ENRICHED_URANIUM = PermissibleValue(
        text="LOW_ENRICHED_URANIUM",
        title="Low Enriched Uranium (LEU)",
        description="Uranium enriched to 0.7%-20% U-235")
    HIGH_ASSAY_LEU = PermissibleValue(
        text="HIGH_ASSAY_LEU",
        title="High-Assay Low Enriched Uranium (HALEU)",
        description="Uranium enriched to 5%-20% U-235")
    HIGHLY_ENRICHED_URANIUM = PermissibleValue(
        text="HIGHLY_ENRICHED_URANIUM",
        title="Highly Enriched Uranium (HEU)",
        description="Uranium enriched to 20% or more U-235")
    WEAPONS_GRADE_URANIUM = PermissibleValue(
        text="WEAPONS_GRADE_URANIUM",
        title="Weapons-Grade Uranium",
        description="Uranium enriched to 90% or more U-235")
    REACTOR_GRADE_PLUTONIUM = PermissibleValue(
        text="REACTOR_GRADE_PLUTONIUM",
        title="Reactor-Grade Plutonium",
        description="Plutonium with high Pu-240 content from spent fuel")
    WEAPONS_GRADE_PLUTONIUM = PermissibleValue(
        text="WEAPONS_GRADE_PLUTONIUM",
        title="Weapons-Grade Plutonium",
        description="Plutonium with low Pu-240 content")
    MOX_FUEL = PermissibleValue(
        text="MOX_FUEL",
        title="Mixed Oxide Fuel",
        description="Mixture of plutonium and uranium oxides")
    THORIUM_FUEL = PermissibleValue(
        text="THORIUM_FUEL",
        title="Thorium-Based Fuel",
        description="Fuel containing thorium-232 as fertile material",
        meaning=CHEBI["33385"])
    TRISO_FUEL = PermissibleValue(
        text="TRISO_FUEL",
        title="Tri-structural Isotropic Fuel",
        description="Coated particle fuel with multiple containment layers")
    LIQUID_FUEL = PermissibleValue(
        text="LIQUID_FUEL",
        title="Liquid Nuclear Fuel",
        description="Fuel dissolved in liquid medium")
    METALLIC_FUEL = PermissibleValue(
        text="METALLIC_FUEL",
        title="Metallic Nuclear Fuel",
        description="Fuel in metallic form")
    CARBIDE_FUEL = PermissibleValue(
        text="CARBIDE_FUEL",
        title="Carbide Nuclear Fuel",
        description="Uranium or plutonium carbide fuel")
    NITRIDE_FUEL = PermissibleValue(
        text="NITRIDE_FUEL",
        title="Nitride Nuclear Fuel",
        description="Uranium or plutonium nitride fuel")

    _defn = EnumDefinition(
        name="NuclearFuelTypeEnum",
        description="Types of nuclear fuel materials and compositions",
    )

class UraniumEnrichmentLevelEnum(EnumDefinitionImpl):
    """
    Standard uranium-235 enrichment level classifications
    """
    NATURAL = PermissibleValue(
        text="NATURAL",
        title="Natural Uranium",
        description="Natural uranium enrichment (0.711% U-235)")
    SLIGHTLY_ENRICHED = PermissibleValue(
        text="SLIGHTLY_ENRICHED",
        title="Slightly Enriched Uranium",
        description="Minimal enrichment above natural levels")
    LOW_ENRICHED = PermissibleValue(
        text="LOW_ENRICHED",
        title="Low Enriched Uranium",
        description="Standard commercial reactor enrichment")
    HIGH_ASSAY_LOW_ENRICHED = PermissibleValue(
        text="HIGH_ASSAY_LOW_ENRICHED",
        title="High-Assay Low Enriched Uranium",
        description="Higher enrichment for advanced reactors")
    HIGHLY_ENRICHED = PermissibleValue(
        text="HIGHLY_ENRICHED",
        title="Highly Enriched Uranium",
        description="High enrichment for research and naval reactors")
    WEAPONS_GRADE = PermissibleValue(
        text="WEAPONS_GRADE",
        title="Weapons-Grade Uranium",
        description="Very high enrichment for weapons")

    _defn = EnumDefinition(
        name="UraniumEnrichmentLevelEnum",
        description="Standard uranium-235 enrichment level classifications",
    )

class FuelFormEnum(EnumDefinitionImpl):
    """
    Physical forms of nuclear fuel
    """
    OXIDE_PELLETS = PermissibleValue(
        text="OXIDE_PELLETS",
        title="Oxide Pellets",
        description="Ceramic uranium dioxide pellets")
    METAL_SLUGS = PermissibleValue(
        text="METAL_SLUGS",
        title="Metal Slugs",
        description="Metallic uranium fuel elements")
    COATED_PARTICLES = PermissibleValue(
        text="COATED_PARTICLES",
        title="Coated Particles",
        description="Microspheres with protective coatings")
    LIQUID_SOLUTION = PermissibleValue(
        text="LIQUID_SOLUTION",
        title="Liquid Solution",
        description="Fuel dissolved in liquid carrier")
    DISPERSION_FUEL = PermissibleValue(
        text="DISPERSION_FUEL",
        title="Dispersion Fuel",
        description="Fuel particles dispersed in matrix")
    CERMET_FUEL = PermissibleValue(
        text="CERMET_FUEL",
        title="Cermet Fuel",
        description="Ceramic-metal composite fuel")
    PLATE_FUEL = PermissibleValue(
        text="PLATE_FUEL",
        title="Plate Fuel",
        description="Flat plate fuel elements")
    ROD_FUEL = PermissibleValue(
        text="ROD_FUEL",
        title="Rod Fuel",
        description="Cylindrical fuel rods")

    _defn = EnumDefinition(
        name="FuelFormEnum",
        description="Physical forms of nuclear fuel",
    )

class FuelAssemblyTypeEnum(EnumDefinitionImpl):
    """
    Types of fuel assembly configurations
    """
    PWR_ASSEMBLY = PermissibleValue(
        text="PWR_ASSEMBLY",
        title="PWR Fuel Assembly",
        description="Square array fuel assembly for PWR")
    BWR_ASSEMBLY = PermissibleValue(
        text="BWR_ASSEMBLY",
        title="BWR Fuel Assembly",
        description="Square array fuel assembly for BWR")
    CANDU_BUNDLE = PermissibleValue(
        text="CANDU_BUNDLE",
        title="CANDU Fuel Bundle",
        description="Cylindrical fuel bundle for PHWR")
    RBMK_ASSEMBLY = PermissibleValue(
        text="RBMK_ASSEMBLY",
        title="RBMK Fuel Assembly",
        description="Fuel assembly for RBMK reactors")
    AGR_ASSEMBLY = PermissibleValue(
        text="AGR_ASSEMBLY",
        title="AGR Fuel Assembly",
        description="Fuel stringer for AGR")
    HTGR_BLOCK = PermissibleValue(
        text="HTGR_BLOCK",
        title="HTGR Fuel Block",
        description="Graphite block with TRISO fuel")
    FAST_REACTOR_ASSEMBLY = PermissibleValue(
        text="FAST_REACTOR_ASSEMBLY",
        title="Fast Reactor Assembly",
        description="Fuel assembly for fast reactors")

    _defn = EnumDefinition(
        name="FuelAssemblyTypeEnum",
        description="Types of fuel assembly configurations",
    )

class FuelCycleStageEnum(EnumDefinitionImpl):
    """
    Stages in the nuclear fuel cycle
    """
    MINING = PermissibleValue(
        text="MINING",
        title="Uranium Mining",
        description="Extraction of uranium ore from deposits")
    CONVERSION = PermissibleValue(
        text="CONVERSION",
        title="Conversion",
        description="Conversion of uranium concentrate to UF6")
    ENRICHMENT = PermissibleValue(
        text="ENRICHMENT",
        title="Enrichment",
        description="Increase of U-235 concentration")
    FUEL_FABRICATION = PermissibleValue(
        text="FUEL_FABRICATION",
        title="Fuel Fabrication",
        description="Manufacturing of fuel assemblies")
    REACTOR_OPERATION = PermissibleValue(
        text="REACTOR_OPERATION",
        title="Reactor Operation",
        description="Power generation in nuclear reactor")
    INTERIM_STORAGE = PermissibleValue(
        text="INTERIM_STORAGE",
        title="Interim Storage",
        description="Temporary storage of spent fuel")
    REPROCESSING = PermissibleValue(
        text="REPROCESSING",
        title="Reprocessing",
        description="Chemical separation of spent fuel components")
    DISPOSAL = PermissibleValue(
        text="DISPOSAL",
        title="Disposal",
        description="Permanent disposal of nuclear waste")

    _defn = EnumDefinition(
        name="FuelCycleStageEnum",
        description="Stages in the nuclear fuel cycle",
    )

class FissileIsotopeEnum(EnumDefinitionImpl):
    """
    Fissile isotopes used in nuclear fuel
    """
    URANIUM_233 = PermissibleValue(
        text="URANIUM_233",
        title="Uranium-233",
        description="Fissile isotope produced from thorium")
    URANIUM_235 = PermissibleValue(
        text="URANIUM_235",
        title="Uranium-235",
        description="Naturally occurring fissile uranium isotope")
    PLUTONIUM_239 = PermissibleValue(
        text="PLUTONIUM_239",
        title="Plutonium-239",
        description="Fissile plutonium isotope from U-238 breeding")
    PLUTONIUM_241 = PermissibleValue(
        text="PLUTONIUM_241",
        title="Plutonium-241",
        description="Fissile plutonium isotope with short half-life")

    _defn = EnumDefinition(
        name="FissileIsotopeEnum",
        description="Fissile isotopes used in nuclear fuel",
    )

class IAEAWasteClassificationEnum(EnumDefinitionImpl):
    """
    IAEA General Safety Requirements radioactive waste classification scheme
    """
    EXEMPT_WASTE = PermissibleValue(
        text="EXEMPT_WASTE",
        title="Exempt Waste (EW)",
        description="Waste with negligible radioactivity requiring no regulatory control")
    VERY_SHORT_LIVED_WASTE = PermissibleValue(
        text="VERY_SHORT_LIVED_WASTE",
        title="Very Short-Lived Waste (VSLW)",
        description="Waste stored for decay to exempt levels within few years")
    VERY_LOW_LEVEL_WASTE = PermissibleValue(
        text="VERY_LOW_LEVEL_WASTE",
        title="Very Low Level Waste (VLLW)",
        description="Waste requiring limited containment and isolation")
    LOW_LEVEL_WASTE = PermissibleValue(
        text="LOW_LEVEL_WASTE",
        title="Low Level Waste (LLW)",
        description="Waste requiring containment for up to hundreds of years")
    INTERMEDIATE_LEVEL_WASTE = PermissibleValue(
        text="INTERMEDIATE_LEVEL_WASTE",
        title="Intermediate Level Waste (ILW)",
        description="Waste requiring containment for thousands of years")
    HIGH_LEVEL_WASTE = PermissibleValue(
        text="HIGH_LEVEL_WASTE",
        title="High Level Waste (HLW)",
        description="Waste requiring containment for thousands to hundreds of thousands of years")

    _defn = EnumDefinition(
        name="IAEAWasteClassificationEnum",
        description="IAEA General Safety Requirements radioactive waste classification scheme",
    )

class NRCWasteClassEnum(EnumDefinitionImpl):
    """
    US NRC 10 CFR 61 low-level radioactive waste classification
    """
    CLASS_A = PermissibleValue(
        text="CLASS_A",
        title="Class A Low-Level Waste",
        description="Lowest radioactivity waste suitable for shallow land burial")
    CLASS_B = PermissibleValue(
        text="CLASS_B",
        title="Class B Low-Level Waste",
        description="Intermediate radioactivity requiring waste form stability")
    CLASS_C = PermissibleValue(
        text="CLASS_C",
        title="Class C Low-Level Waste",
        description="Highest concentration suitable for shallow land burial")
    GREATER_THAN_CLASS_C = PermissibleValue(
        text="GREATER_THAN_CLASS_C",
        title="Greater Than Class C Waste (GTCC)",
        description="Waste exceeding Class C limits, generally unsuitable for shallow burial")

    _defn = EnumDefinition(
        name="NRCWasteClassEnum",
        description="US NRC 10 CFR 61 low-level radioactive waste classification",
    )

class WasteHeatGenerationEnum(EnumDefinitionImpl):
    """
    Heat generation categories for radioactive waste
    """
    NEGLIGIBLE_HEAT = PermissibleValue(
        text="NEGLIGIBLE_HEAT",
        title="Negligible Heat Generation",
        description="Waste generating negligible heat")
    LOW_HEAT = PermissibleValue(
        text="LOW_HEAT",
        title="Low Heat Generation",
        description="Waste generating low but measurable heat")
    HIGH_HEAT = PermissibleValue(
        text="HIGH_HEAT",
        title="High Heat Generation",
        description="Waste generating significant heat requiring thermal management")

    _defn = EnumDefinition(
        name="WasteHeatGenerationEnum",
        description="Heat generation categories for radioactive waste",
    )

class WasteHalfLifeCategoryEnum(EnumDefinitionImpl):
    """
    Half-life categories for radioactive waste classification
    """
    VERY_SHORT_LIVED = PermissibleValue(
        text="VERY_SHORT_LIVED",
        title="Very Short-Lived",
        description="Radionuclides with very short half-lives")
    SHORT_LIVED = PermissibleValue(
        text="SHORT_LIVED",
        title="Short-Lived",
        description="Radionuclides with short half-lives")
    LONG_LIVED = PermissibleValue(
        text="LONG_LIVED",
        title="Long-Lived",
        description="Radionuclides with long half-lives")

    _defn = EnumDefinition(
        name="WasteHalfLifeCategoryEnum",
        description="Half-life categories for radioactive waste classification",
    )

class WasteDisposalMethodEnum(EnumDefinitionImpl):
    """
    Methods for radioactive waste disposal
    """
    CLEARANCE = PermissibleValue(
        text="CLEARANCE",
        title="Clearance for Unrestricted Use",
        description="Release from regulatory control as ordinary waste")
    DECAY_STORAGE = PermissibleValue(
        text="DECAY_STORAGE",
        title="Decay Storage",
        description="Storage for radioactive decay to exempt levels")
    NEAR_SURFACE_DISPOSAL = PermissibleValue(
        text="NEAR_SURFACE_DISPOSAL",
        title="Near-Surface Disposal",
        description="Disposal in engineered near-surface facilities")
    GEOLOGICAL_DISPOSAL = PermissibleValue(
        text="GEOLOGICAL_DISPOSAL",
        title="Geological Disposal",
        description="Deep underground disposal in stable geological formations")
    BOREHOLE_DISPOSAL = PermissibleValue(
        text="BOREHOLE_DISPOSAL",
        title="Borehole Disposal",
        description="Disposal in deep boreholes")
    TRANSMUTATION = PermissibleValue(
        text="TRANSMUTATION",
        title="Transmutation",
        description="Nuclear transformation to shorter-lived or stable isotopes")

    _defn = EnumDefinition(
        name="WasteDisposalMethodEnum",
        description="Methods for radioactive waste disposal",
    )

class WasteSourceEnum(EnumDefinitionImpl):
    """
    Sources of radioactive waste generation
    """
    NUCLEAR_POWER_PLANTS = PermissibleValue(
        text="NUCLEAR_POWER_PLANTS",
        title="Nuclear Power Plants",
        description="Waste from commercial nuclear power generation")
    MEDICAL_APPLICATIONS = PermissibleValue(
        text="MEDICAL_APPLICATIONS",
        title="Medical Applications",
        description="Waste from nuclear medicine and radiotherapy")
    INDUSTRIAL_APPLICATIONS = PermissibleValue(
        text="INDUSTRIAL_APPLICATIONS",
        title="Industrial Applications",
        description="Waste from industrial use of radioactive materials")
    RESEARCH_FACILITIES = PermissibleValue(
        text="RESEARCH_FACILITIES",
        title="Research Facilities",
        description="Waste from research reactors and laboratories")
    NUCLEAR_WEAPONS_PROGRAM = PermissibleValue(
        text="NUCLEAR_WEAPONS_PROGRAM",
        title="Nuclear Weapons Program",
        description="Waste from defense nuclear activities")
    DECOMMISSIONING = PermissibleValue(
        text="DECOMMISSIONING",
        title="Facility Decommissioning",
        description="Waste from dismantling nuclear facilities")
    URANIUM_MINING = PermissibleValue(
        text="URANIUM_MINING",
        title="Uranium Mining and Milling",
        description="Waste from uranium extraction and processing")
    FUEL_CYCLE_FACILITIES = PermissibleValue(
        text="FUEL_CYCLE_FACILITIES",
        title="Fuel Cycle Facilities",
        description="Waste from fuel fabrication, enrichment, and reprocessing")

    _defn = EnumDefinition(
        name="WasteSourceEnum",
        description="Sources of radioactive waste generation",
    )

class TransuranicWasteCategoryEnum(EnumDefinitionImpl):
    """
    Transuranic waste classifications (US system)
    """
    CONTACT_HANDLED_TRU = PermissibleValue(
        text="CONTACT_HANDLED_TRU",
        title="Contact-Handled Transuranic Waste",
        description="TRU waste with surface dose rate ≤200 mrem/hr")
    REMOTE_HANDLED_TRU = PermissibleValue(
        text="REMOTE_HANDLED_TRU",
        title="Remote-Handled Transuranic Waste",
        description="TRU waste with surface dose rate >200 mrem/hr")
    TRU_MIXED_WASTE = PermissibleValue(
        text="TRU_MIXED_WASTE",
        title="TRU Mixed Waste",
        description="TRU waste also containing hazardous chemical components")

    _defn = EnumDefinition(
        name="TransuranicWasteCategoryEnum",
        description="Transuranic waste classifications (US system)",
    )

class INESLevelEnum(EnumDefinitionImpl):
    """
    International Nuclear and Radiological Event Scale (INES) levels
    """
    LEVEL_0 = PermissibleValue(
        text="LEVEL_0",
        title="Level 0 - Below Scale/Deviation",
        description="Events without safety significance")
    LEVEL_1 = PermissibleValue(
        text="LEVEL_1",
        title="Level 1 - Anomaly",
        description="Anomaly beyond authorized operating regime")
    LEVEL_2 = PermissibleValue(
        text="LEVEL_2",
        title="Level 2 - Incident",
        description="Incident with significant defenses remaining")
    LEVEL_3 = PermissibleValue(
        text="LEVEL_3",
        title="Level 3 - Serious Incident",
        description="Serious incident with some defense degradation")
    LEVEL_4 = PermissibleValue(
        text="LEVEL_4",
        title="Level 4 - Accident with Local Consequences",
        description="Accident with minor off-site releases")
    LEVEL_5 = PermissibleValue(
        text="LEVEL_5",
        title="Level 5 - Accident with Wider Consequences",
        description="Accident with limited off-site releases")
    LEVEL_6 = PermissibleValue(
        text="LEVEL_6",
        title="Level 6 - Serious Accident",
        description="Serious accident with significant releases")
    LEVEL_7 = PermissibleValue(
        text="LEVEL_7",
        title="Level 7 - Major Accident",
        description="Major accident with widespread health and environmental effects")

    _defn = EnumDefinition(
        name="INESLevelEnum",
        description="International Nuclear and Radiological Event Scale (INES) levels",
    )

class EmergencyClassificationEnum(EnumDefinitionImpl):
    """
    Nuclear emergency action levels and classifications
    """
    NOTIFICATION_UNUSUAL_EVENT = PermissibleValue(
        text="NOTIFICATION_UNUSUAL_EVENT",
        title="Notification of Unusual Event (NOUE)",
        description="Events that are in process or have occurred which indicate potential degradation")
    ALERT = PermissibleValue(
        text="ALERT",
        title="Alert",
        description="Events involving actual or potential substantial degradation of plant safety")
    SITE_AREA_EMERGENCY = PermissibleValue(
        text="SITE_AREA_EMERGENCY",
        title="Site Area Emergency (SAE)",
        description="Events with actual or likely major failures of plant protective systems")
    GENERAL_EMERGENCY = PermissibleValue(
        text="GENERAL_EMERGENCY",
        title="General Emergency",
        description="Events involving actual or imminent substantial core degradation")

    _defn = EnumDefinition(
        name="EmergencyClassificationEnum",
        description="Nuclear emergency action levels and classifications",
    )

class NuclearSecurityCategoryEnum(EnumDefinitionImpl):
    """
    IAEA nuclear material security categories (INFCIRC/225)
    """
    CATEGORY_I = PermissibleValue(
        text="CATEGORY_I",
        title="Category I Nuclear Material",
        description="Material that can be used directly to manufacture nuclear explosive devices")
    CATEGORY_II = PermissibleValue(
        text="CATEGORY_II",
        title="Category II Nuclear Material",
        description="Material requiring further processing to manufacture nuclear explosive devices")
    CATEGORY_III = PermissibleValue(
        text="CATEGORY_III",
        title="Category III Nuclear Material",
        description="Material posing radiation hazard but minimal proliferation risk")
    CATEGORY_IV = PermissibleValue(
        text="CATEGORY_IV",
        title="Category IV Nuclear Material",
        description="Material with minimal security significance")

    _defn = EnumDefinition(
        name="NuclearSecurityCategoryEnum",
        description="IAEA nuclear material security categories (INFCIRC/225)",
    )

class SafetySystemClassEnum(EnumDefinitionImpl):
    """
    Nuclear safety system classifications (based on IEEE and ASME standards)
    """
    CLASS_1E = PermissibleValue(
        text="CLASS_1E",
        title="Class 1E Safety Systems",
        description="Safety systems essential to emergency reactor shutdown and core cooling")
    SAFETY_RELATED = PermissibleValue(
        text="SAFETY_RELATED",
        title="Safety-Related Systems",
        description="Systems important to safety but not classified as Class 1E")
    SAFETY_SIGNIFICANT = PermissibleValue(
        text="SAFETY_SIGNIFICANT",
        title="Safety-Significant Systems",
        description="Systems with risk significance but not safety-related")
    NON_SAFETY_RELATED = PermissibleValue(
        text="NON_SAFETY_RELATED",
        title="Non-Safety-Related Systems",
        description="Systems not required for nuclear safety functions")

    _defn = EnumDefinition(
        name="SafetySystemClassEnum",
        description="Nuclear safety system classifications (based on IEEE and ASME standards)",
    )

class ReactorSafetyFunctionEnum(EnumDefinitionImpl):
    """
    Fundamental nuclear reactor safety functions
    """
    REACTIVITY_CONTROL = PermissibleValue(
        text="REACTIVITY_CONTROL",
        title="Reactivity Control",
        description="Control of nuclear chain reaction")
    HEAT_REMOVAL = PermissibleValue(
        text="HEAT_REMOVAL",
        title="Heat Removal",
        description="Removal of decay heat from reactor core")
    CONTAINMENT_INTEGRITY = PermissibleValue(
        text="CONTAINMENT_INTEGRITY",
        title="Containment Integrity",
        description="Confinement of radioactive materials")
    CORE_COOLING = PermissibleValue(
        text="CORE_COOLING",
        title="Core Cooling",
        description="Maintenance of adequate core cooling")
    SHUTDOWN_CAPABILITY = PermissibleValue(
        text="SHUTDOWN_CAPABILITY",
        title="Shutdown Capability",
        description="Ability to shut down and maintain shutdown")

    _defn = EnumDefinition(
        name="ReactorSafetyFunctionEnum",
        description="Fundamental nuclear reactor safety functions",
    )

class DefenseInDepthLevelEnum(EnumDefinitionImpl):
    """
    Defense in depth barrier levels for nuclear safety
    """
    LEVEL_1 = PermissibleValue(
        text="LEVEL_1",
        title="Level 1 - Prevention of Abnormal Operation",
        description="Conservative design and high quality in construction and operation")
    LEVEL_2 = PermissibleValue(
        text="LEVEL_2",
        title="Level 2 - Control of Abnormal Operation",
        description="Control of abnormal operation and detection of failures")
    LEVEL_3 = PermissibleValue(
        text="LEVEL_3",
        title="Level 3 - Control of Accidents Within Design Basis",
        description="Control of accidents to prevent progression to severe conditions")
    LEVEL_4 = PermissibleValue(
        text="LEVEL_4",
        title="Level 4 - Control of Severe Plant Conditions",
        description="Control of severe accidents including prevention of core melt progression")
    LEVEL_5 = PermissibleValue(
        text="LEVEL_5",
        title="Level 5 - Mitigation of Radiological Consequences",
        description="Mitigation of off-site radiological consequences")

    _defn = EnumDefinition(
        name="DefenseInDepthLevelEnum",
        description="Defense in depth barrier levels for nuclear safety",
    )

class RadiationProtectionZoneEnum(EnumDefinitionImpl):
    """
    Radiation protection zone classifications for nuclear facilities
    """
    EXCLUSION_AREA = PermissibleValue(
        text="EXCLUSION_AREA",
        title="Exclusion Area",
        description="Area under control of reactor operator with restricted access")
    LOW_POPULATION_ZONE = PermissibleValue(
        text="LOW_POPULATION_ZONE",
        title="Low Population Zone (LPZ)",
        description="Area with low population density surrounding exclusion area")
    EMERGENCY_PLANNING_ZONE = PermissibleValue(
        text="EMERGENCY_PLANNING_ZONE",
        title="Emergency Planning Zone (EPZ)",
        description="Area for which emergency planning is conducted")
    INGESTION_PATHWAY_ZONE = PermissibleValue(
        text="INGESTION_PATHWAY_ZONE",
        title="Ingestion Pathway Zone",
        description="Area for controlling food and water contamination")
    CONTROLLED_AREA = PermissibleValue(
        text="CONTROLLED_AREA",
        title="Controlled Area",
        description="Area within facility boundary with access control")
    SUPERVISED_AREA = PermissibleValue(
        text="SUPERVISED_AREA",
        title="Supervised Area",
        description="Area with potential for radiation exposure but lower than controlled")

    _defn = EnumDefinition(
        name="RadiationProtectionZoneEnum",
        description="Radiation protection zone classifications for nuclear facilities",
    )

class NuclearFacilityTypeEnum(EnumDefinitionImpl):
    """
    Types of nuclear facilities and infrastructure
    """
    COMMERCIAL_POWER_PLANT = PermissibleValue(
        text="COMMERCIAL_POWER_PLANT",
        title="Commercial Nuclear Power Plant",
        description="Large-scale commercial reactor for electricity generation")
    RESEARCH_REACTOR = PermissibleValue(
        text="RESEARCH_REACTOR",
        title="Research Reactor",
        description="Reactor designed for research, training, and isotope production")
    TEST_REACTOR = PermissibleValue(
        text="TEST_REACTOR",
        title="Test Reactor",
        description="Reactor for testing materials and components")
    PROTOTYPE_REACTOR = PermissibleValue(
        text="PROTOTYPE_REACTOR",
        title="Prototype Reactor",
        description="Reactor for demonstrating new technology")
    NAVAL_REACTOR = PermissibleValue(
        text="NAVAL_REACTOR",
        title="Naval Reactor",
        description="Reactor for ship or submarine propulsion")
    SPACE_REACTOR = PermissibleValue(
        text="SPACE_REACTOR",
        title="Space Nuclear Reactor",
        description="Reactor designed for space applications")
    PRODUCTION_REACTOR = PermissibleValue(
        text="PRODUCTION_REACTOR",
        title="Production Reactor",
        description="Reactor for producing nuclear materials")
    URANIUM_MINE = PermissibleValue(
        text="URANIUM_MINE",
        title="Uranium Mine",
        description="Facility for extracting uranium ore")
    URANIUM_MILL = PermissibleValue(
        text="URANIUM_MILL",
        title="Uranium Mill",
        description="Facility for processing uranium ore into yellowcake")
    CONVERSION_FACILITY = PermissibleValue(
        text="CONVERSION_FACILITY",
        title="Conversion Facility",
        description="Facility for converting yellowcake to UF6")
    ENRICHMENT_FACILITY = PermissibleValue(
        text="ENRICHMENT_FACILITY",
        title="Enrichment Facility",
        description="Facility for increasing U-235 concentration")
    FUEL_FABRICATION_FACILITY = PermissibleValue(
        text="FUEL_FABRICATION_FACILITY",
        title="Fuel Fabrication Facility",
        description="Facility for manufacturing nuclear fuel assemblies")
    REPROCESSING_FACILITY = PermissibleValue(
        text="REPROCESSING_FACILITY",
        title="Reprocessing Facility",
        description="Facility for separating spent fuel components")
    INTERIM_STORAGE_FACILITY = PermissibleValue(
        text="INTERIM_STORAGE_FACILITY",
        title="Interim Storage Facility",
        description="Facility for temporary storage of nuclear materials")
    GEOLOGICAL_REPOSITORY = PermissibleValue(
        text="GEOLOGICAL_REPOSITORY",
        title="Geological Repository",
        description="Deep underground facility for permanent waste disposal")
    DECOMMISSIONING_SITE = PermissibleValue(
        text="DECOMMISSIONING_SITE",
        title="Decommissioning Site",
        description="Nuclear facility undergoing dismantlement")
    NUCLEAR_LABORATORY = PermissibleValue(
        text="NUCLEAR_LABORATORY",
        title="Nuclear Laboratory",
        description="Laboratory facility handling radioactive materials")
    RADIOISOTOPE_PRODUCTION_FACILITY = PermissibleValue(
        text="RADIOISOTOPE_PRODUCTION_FACILITY",
        title="Radioisotope Production Facility",
        description="Facility for producing medical and industrial isotopes")

    _defn = EnumDefinition(
        name="NuclearFacilityTypeEnum",
        description="Types of nuclear facilities and infrastructure",
    )

class PowerPlantStatusEnum(EnumDefinitionImpl):
    """
    Operational status of nuclear power plants
    """
    UNDER_CONSTRUCTION = PermissibleValue(
        text="UNDER_CONSTRUCTION",
        title="Under Construction",
        description="Plant currently being built")
    COMMISSIONING = PermissibleValue(
        text="COMMISSIONING",
        title="Commissioning",
        description="Plant undergoing testing before commercial operation")
    COMMERCIAL_OPERATION = PermissibleValue(
        text="COMMERCIAL_OPERATION",
        title="Commercial Operation",
        description="Plant operating commercially for electricity generation")
    REFUELING_OUTAGE = PermissibleValue(
        text="REFUELING_OUTAGE",
        title="Refueling Outage",
        description="Plant temporarily shut down for fuel replacement and maintenance")
    EXTENDED_OUTAGE = PermissibleValue(
        text="EXTENDED_OUTAGE",
        title="Extended Outage",
        description="Plant shut down for extended period for major work")
    PERMANENTLY_SHUTDOWN = PermissibleValue(
        text="PERMANENTLY_SHUTDOWN",
        title="Permanently Shutdown",
        description="Plant permanently ceased operation")
    DECOMMISSIONING = PermissibleValue(
        text="DECOMMISSIONING",
        title="Decommissioning",
        description="Plant undergoing dismantlement")
    DECOMMISSIONED = PermissibleValue(
        text="DECOMMISSIONED",
        title="Decommissioned",
        description="Plant completely dismantled and site restored")

    _defn = EnumDefinition(
        name="PowerPlantStatusEnum",
        description="Operational status of nuclear power plants",
    )

class ResearchReactorTypeEnum(EnumDefinitionImpl):
    """
    Types of research reactors
    """
    POOL_TYPE = PermissibleValue(
        text="POOL_TYPE",
        title="Pool-Type Research Reactor",
        description="Reactor with fuel in open pool of water")
    TANK_TYPE = PermissibleValue(
        text="TANK_TYPE",
        title="Tank-Type Research Reactor",
        description="Reactor with fuel in enclosed tank")
    HOMOGENEOUS = PermissibleValue(
        text="HOMOGENEOUS",
        title="Homogeneous Research Reactor",
        description="Reactor with fuel in liquid form")
    FAST_RESEARCH_REACTOR = PermissibleValue(
        text="FAST_RESEARCH_REACTOR",
        title="Fast Research Reactor",
        description="Research reactor using fast neutrons")
    PULSED_REACTOR = PermissibleValue(
        text="PULSED_REACTOR",
        title="Pulsed Research Reactor",
        description="Reactor designed for pulsed operation")
    CRITICAL_ASSEMBLY = PermissibleValue(
        text="CRITICAL_ASSEMBLY",
        title="Critical Assembly",
        description="Minimal reactor for criticality studies")
    SUBCRITICAL_ASSEMBLY = PermissibleValue(
        text="SUBCRITICAL_ASSEMBLY",
        title="Subcritical Assembly",
        description="Neutron source-driven subcritical system")

    _defn = EnumDefinition(
        name="ResearchReactorTypeEnum",
        description="Types of research reactors",
    )

class FuelCycleFacilityTypeEnum(EnumDefinitionImpl):
    """
    Types of nuclear fuel cycle facilities
    """
    IN_SITU_LEACH_MINE = PermissibleValue(
        text="IN_SITU_LEACH_MINE",
        title="In-Situ Leach Mine",
        description="Uranium extraction by solution mining")
    CONVENTIONAL_MINE = PermissibleValue(
        text="CONVENTIONAL_MINE",
        title="Conventional Mine",
        description="Traditional underground or open-pit uranium mining")
    HEAP_LEACH_FACILITY = PermissibleValue(
        text="HEAP_LEACH_FACILITY",
        title="Heap Leach Facility",
        description="Uranium extraction from low-grade ores by heap leaching")
    GASEOUS_DIFFUSION_PLANT = PermissibleValue(
        text="GASEOUS_DIFFUSION_PLANT",
        title="Gaseous Diffusion Enrichment Plant",
        description="Uranium enrichment using gaseous diffusion")
    GAS_CENTRIFUGE_PLANT = PermissibleValue(
        text="GAS_CENTRIFUGE_PLANT",
        title="Gas Centrifuge Enrichment Plant",
        description="Uranium enrichment using centrifuge technology")
    LASER_ENRICHMENT_FACILITY = PermissibleValue(
        text="LASER_ENRICHMENT_FACILITY",
        title="Laser Enrichment Facility",
        description="Uranium enrichment using laser isotope separation")
    MOX_FUEL_FABRICATION = PermissibleValue(
        text="MOX_FUEL_FABRICATION",
        title="MOX Fuel Fabrication Facility",
        description="Facility for manufacturing mixed oxide fuel")
    AQUEOUS_REPROCESSING = PermissibleValue(
        text="AQUEOUS_REPROCESSING",
        title="Aqueous Reprocessing Plant",
        description="Spent fuel reprocessing using aqueous methods")
    PYROPROCESSING_FACILITY = PermissibleValue(
        text="PYROPROCESSING_FACILITY",
        title="Pyroprocessing Facility",
        description="Spent fuel reprocessing using electrochemical methods")

    _defn = EnumDefinition(
        name="FuelCycleFacilityTypeEnum",
        description="Types of nuclear fuel cycle facilities",
    )

class WasteFacilityTypeEnum(EnumDefinitionImpl):
    """
    Types of nuclear waste management facilities
    """
    SPENT_FUEL_POOL = PermissibleValue(
        text="SPENT_FUEL_POOL",
        title="Spent Fuel Pool",
        description="Water-filled pool for cooling spent fuel")
    DRY_CASK_STORAGE = PermissibleValue(
        text="DRY_CASK_STORAGE",
        title="Dry Cask Storage",
        description="Air-cooled storage in sealed containers")
    CENTRALIZED_INTERIM_STORAGE = PermissibleValue(
        text="CENTRALIZED_INTERIM_STORAGE",
        title="Centralized Interim Storage Facility",
        description="Large-scale interim storage away from reactor sites")
    LOW_LEVEL_WASTE_DISPOSAL = PermissibleValue(
        text="LOW_LEVEL_WASTE_DISPOSAL",
        title="Low-Level Waste Disposal Site",
        description="Near-surface disposal for low-level waste")
    GREATER_THAN_CLASS_C_STORAGE = PermissibleValue(
        text="GREATER_THAN_CLASS_C_STORAGE",
        title="Greater Than Class C Storage",
        description="Storage for waste exceeding Class C limits")
    TRANSURANIC_WASTE_REPOSITORY = PermissibleValue(
        text="TRANSURANIC_WASTE_REPOSITORY",
        title="Transuranic Waste Repository",
        description="Deep geological repository for TRU waste")
    HIGH_LEVEL_WASTE_REPOSITORY = PermissibleValue(
        text="HIGH_LEVEL_WASTE_REPOSITORY",
        title="High-Level Waste Repository",
        description="Deep geological repository for high-level waste")
    WASTE_TREATMENT_FACILITY = PermissibleValue(
        text="WASTE_TREATMENT_FACILITY",
        title="Waste Treatment Facility",
        description="Facility for processing and conditioning waste")
    DECONTAMINATION_FACILITY = PermissibleValue(
        text="DECONTAMINATION_FACILITY",
        title="Decontamination Facility",
        description="Facility for cleaning contaminated materials")

    _defn = EnumDefinition(
        name="WasteFacilityTypeEnum",
        description="Types of nuclear waste management facilities",
    )

class NuclearShipTypeEnum(EnumDefinitionImpl):
    """
    Types of nuclear-powered vessels
    """
    AIRCRAFT_CARRIER = PermissibleValue(
        text="AIRCRAFT_CARRIER",
        title="Nuclear Aircraft Carrier",
        description="Large naval vessel with nuclear propulsion and aircraft operations")
    SUBMARINE = PermissibleValue(
        text="SUBMARINE",
        title="Nuclear Submarine",
        description="Underwater vessel with nuclear propulsion")
    CRUISER = PermissibleValue(
        text="CRUISER",
        title="Nuclear Cruiser",
        description="Large surface combatant with nuclear propulsion")
    ICEBREAKER = PermissibleValue(
        text="ICEBREAKER",
        title="Nuclear Icebreaker",
        description="Vessel designed to break ice using nuclear power")
    MERCHANT_SHIP = PermissibleValue(
        text="MERCHANT_SHIP",
        title="Nuclear Merchant Ship",
        description="Commercial cargo vessel with nuclear propulsion")
    RESEARCH_VESSEL = PermissibleValue(
        text="RESEARCH_VESSEL",
        title="Nuclear Research Vessel",
        description="Ship designed for oceanographic research with nuclear power")

    _defn = EnumDefinition(
        name="NuclearShipTypeEnum",
        description="Types of nuclear-powered vessels",
    )

class ReactorOperatingStateEnum(EnumDefinitionImpl):
    """
    Operational states of nuclear reactors
    """
    STARTUP = PermissibleValue(
        text="STARTUP",
        title="Startup",
        description="Reactor transitioning from shutdown to power operation")
    CRITICAL = PermissibleValue(
        text="CRITICAL",
        title="Critical",
        description="Reactor achieving self-sustaining chain reaction")
    POWER_ESCALATION = PermissibleValue(
        text="POWER_ESCALATION",
        title="Power Escalation",
        description="Reactor increasing power toward full power operation")
    FULL_POWER_OPERATION = PermissibleValue(
        text="FULL_POWER_OPERATION",
        title="Full Power Operation",
        description="Reactor operating at rated thermal power")
    LOAD_FOLLOWING = PermissibleValue(
        text="LOAD_FOLLOWING",
        title="Load Following",
        description="Reactor adjusting power to match electrical demand")
    REDUCED_POWER = PermissibleValue(
        text="REDUCED_POWER",
        title="Reduced Power Operation",
        description="Reactor operating below rated power")
    HOT_STANDBY = PermissibleValue(
        text="HOT_STANDBY",
        title="Hot Standby",
        description="Reactor subcritical but at operating temperature")
    COLD_SHUTDOWN = PermissibleValue(
        text="COLD_SHUTDOWN",
        title="Cold Shutdown",
        description="Reactor subcritical and cooled below operating temperature")
    REFUELING = PermissibleValue(
        text="REFUELING",
        title="Refueling",
        description="Reactor shut down for fuel replacement")
    REACTOR_TRIP = PermissibleValue(
        text="REACTOR_TRIP",
        title="Reactor Trip",
        description="Rapid automatic shutdown due to safety system actuation")
    SCRAM = PermissibleValue(
        text="SCRAM",
        title="Scram",
        description="Emergency rapid shutdown of reactor")
    EMERGENCY_SHUTDOWN = PermissibleValue(
        text="EMERGENCY_SHUTDOWN",
        title="Emergency Shutdown",
        description="Shutdown due to emergency conditions")

    _defn = EnumDefinition(
        name="ReactorOperatingStateEnum",
        description="Operational states of nuclear reactors",
    )

class MaintenanceTypeEnum(EnumDefinitionImpl):
    """
    Types of nuclear facility maintenance activities
    """
    PREVENTIVE_MAINTENANCE = PermissibleValue(
        text="PREVENTIVE_MAINTENANCE",
        title="Preventive Maintenance",
        description="Scheduled maintenance to prevent equipment failure")
    CORRECTIVE_MAINTENANCE = PermissibleValue(
        text="CORRECTIVE_MAINTENANCE",
        title="Corrective Maintenance",
        description="Maintenance to repair failed or degraded equipment")
    PREDICTIVE_MAINTENANCE = PermissibleValue(
        text="PREDICTIVE_MAINTENANCE",
        title="Predictive Maintenance",
        description="Maintenance based on condition monitoring")
    CONDITION_BASED_MAINTENANCE = PermissibleValue(
        text="CONDITION_BASED_MAINTENANCE",
        title="Condition-Based Maintenance",
        description="Maintenance triggered by equipment condition assessment")
    REFUELING_OUTAGE_MAINTENANCE = PermissibleValue(
        text="REFUELING_OUTAGE_MAINTENANCE",
        title="Refueling Outage Maintenance",
        description="Major maintenance during scheduled refueling")
    FORCED_OUTAGE_MAINTENANCE = PermissibleValue(
        text="FORCED_OUTAGE_MAINTENANCE",
        title="Forced Outage Maintenance",
        description="Unplanned maintenance due to equipment failure")
    IN_SERVICE_INSPECTION = PermissibleValue(
        text="IN_SERVICE_INSPECTION",
        title="In-Service Inspection",
        description="Required inspection of safety-related components")
    MODIFICATION_WORK = PermissibleValue(
        text="MODIFICATION_WORK",
        title="Modification Work",
        description="Changes to plant design or configuration")

    _defn = EnumDefinition(
        name="MaintenanceTypeEnum",
        description="Types of nuclear facility maintenance activities",
    )

class LicensingStageEnum(EnumDefinitionImpl):
    """
    Nuclear facility licensing stages
    """
    SITE_PERMIT = PermissibleValue(
        text="SITE_PERMIT",
        title="Site Permit",
        description="Early site permit for nuclear facility")
    DESIGN_CERTIFICATION = PermissibleValue(
        text="DESIGN_CERTIFICATION",
        title="Design Certification",
        description="Certification of standardized reactor design")
    CONSTRUCTION_PERMIT = PermissibleValue(
        text="CONSTRUCTION_PERMIT",
        title="Construction Permit",
        description="Authorization to begin nuclear facility construction")
    OPERATING_LICENSE = PermissibleValue(
        text="OPERATING_LICENSE",
        title="Operating License",
        description="Authorization for commercial reactor operation")
    LICENSE_RENEWAL = PermissibleValue(
        text="LICENSE_RENEWAL",
        title="License Renewal",
        description="Extension of operating license beyond initial term")
    COMBINED_LICENSE = PermissibleValue(
        text="COMBINED_LICENSE",
        title="Combined License (COL)",
        description="Combined construction and operating license")
    DECOMMISSIONING_PLAN = PermissibleValue(
        text="DECOMMISSIONING_PLAN",
        title="Decommissioning Plan Approval",
        description="Approval of facility decommissioning plan")
    LICENSE_TERMINATION = PermissibleValue(
        text="LICENSE_TERMINATION",
        title="License Termination",
        description="Final termination of nuclear facility license")

    _defn = EnumDefinition(
        name="LicensingStageEnum",
        description="Nuclear facility licensing stages",
    )

class FuelCycleOperationEnum(EnumDefinitionImpl):
    """
    Nuclear fuel cycle operational activities
    """
    URANIUM_EXPLORATION = PermissibleValue(
        text="URANIUM_EXPLORATION",
        title="Uranium Exploration",
        description="Search and evaluation of uranium deposits")
    URANIUM_EXTRACTION = PermissibleValue(
        text="URANIUM_EXTRACTION",
        title="Uranium Extraction",
        description="Mining and extraction of uranium ore")
    URANIUM_MILLING = PermissibleValue(
        text="URANIUM_MILLING",
        title="Uranium Milling",
        description="Processing of uranium ore to produce yellowcake")
    URANIUM_CONVERSION = PermissibleValue(
        text="URANIUM_CONVERSION",
        title="Uranium Conversion",
        description="Conversion of yellowcake to uranium hexafluoride")
    URANIUM_ENRICHMENT = PermissibleValue(
        text="URANIUM_ENRICHMENT",
        title="Uranium Enrichment",
        description="Increase U-235 concentration in uranium")
    FUEL_FABRICATION = PermissibleValue(
        text="FUEL_FABRICATION",
        title="Fuel Fabrication",
        description="Manufacturing of nuclear fuel assemblies")
    REACTOR_FUEL_LOADING = PermissibleValue(
        text="REACTOR_FUEL_LOADING",
        title="Reactor Fuel Loading",
        description="Installation of fresh fuel in reactor")
    REACTOR_OPERATION = PermissibleValue(
        text="REACTOR_OPERATION",
        title="Reactor Operation",
        description="Power generation and fuel burnup")
    SPENT_FUEL_DISCHARGE = PermissibleValue(
        text="SPENT_FUEL_DISCHARGE",
        title="Spent Fuel Discharge",
        description="Removal of used fuel from reactor")
    SPENT_FUEL_STORAGE = PermissibleValue(
        text="SPENT_FUEL_STORAGE",
        title="Spent Fuel Storage",
        description="Interim storage of discharged fuel")
    SPENT_FUEL_REPROCESSING = PermissibleValue(
        text="SPENT_FUEL_REPROCESSING",
        title="Spent Fuel Reprocessing",
        description="Chemical separation of spent fuel components")
    WASTE_CONDITIONING = PermissibleValue(
        text="WASTE_CONDITIONING",
        title="Waste Conditioning",
        description="Preparation of waste for storage or disposal")
    WASTE_DISPOSAL = PermissibleValue(
        text="WASTE_DISPOSAL",
        title="Waste Disposal",
        description="Permanent disposal of nuclear waste")

    _defn = EnumDefinition(
        name="FuelCycleOperationEnum",
        description="Nuclear fuel cycle operational activities",
    )

class ReactorControlModeEnum(EnumDefinitionImpl):
    """
    Reactor control and safety system operational modes
    """
    MANUAL_CONTROL = PermissibleValue(
        text="MANUAL_CONTROL",
        title="Manual Control",
        description="Direct operator control of reactor systems")
    AUTOMATIC_CONTROL = PermissibleValue(
        text="AUTOMATIC_CONTROL",
        title="Automatic Control",
        description="Automated reactor control systems")
    REACTOR_PROTECTION_SYSTEM = PermissibleValue(
        text="REACTOR_PROTECTION_SYSTEM",
        title="Reactor Protection System Active",
        description="Safety system monitoring for trip conditions")
    ENGINEERED_SAFEGUARDS = PermissibleValue(
        text="ENGINEERED_SAFEGUARDS",
        title="Engineered Safeguards Active",
        description="Safety systems for accident mitigation")
    EMERGENCY_OPERATING_PROCEDURES = PermissibleValue(
        text="EMERGENCY_OPERATING_PROCEDURES",
        title="Emergency Operating Procedures",
        description="Operator actions for emergency conditions")
    SEVERE_ACCIDENT_MANAGEMENT = PermissibleValue(
        text="SEVERE_ACCIDENT_MANAGEMENT",
        title="Severe Accident Management",
        description="Procedures for beyond design basis accidents")

    _defn = EnumDefinition(
        name="ReactorControlModeEnum",
        description="Reactor control and safety system operational modes",
    )

class OperationalProcedureEnum(EnumDefinitionImpl):
    """
    Standard nuclear facility operational procedures
    """
    STARTUP_PROCEDURE = PermissibleValue(
        text="STARTUP_PROCEDURE",
        title="Reactor Startup Procedure",
        description="Systematic procedure for bringing reactor to power")
    SHUTDOWN_PROCEDURE = PermissibleValue(
        text="SHUTDOWN_PROCEDURE",
        title="Reactor Shutdown Procedure",
        description="Systematic procedure for shutting down reactor")
    REFUELING_PROCEDURE = PermissibleValue(
        text="REFUELING_PROCEDURE",
        title="Refueling Procedure",
        description="Procedure for fuel handling and replacement")
    SURVEILLANCE_TESTING = PermissibleValue(
        text="SURVEILLANCE_TESTING",
        title="Surveillance Testing",
        description="Regular testing of safety systems")
    MAINTENANCE_PROCEDURE = PermissibleValue(
        text="MAINTENANCE_PROCEDURE",
        title="Maintenance Procedure",
        description="Systematic approach to equipment maintenance")
    EMERGENCY_RESPONSE = PermissibleValue(
        text="EMERGENCY_RESPONSE",
        title="Emergency Response Procedure",
        description="Response to emergency conditions")
    RADIOLOGICAL_PROTECTION = PermissibleValue(
        text="RADIOLOGICAL_PROTECTION",
        title="Radiological Protection Procedure",
        description="Procedures for radiation protection")
    SECURITY_PROCEDURE = PermissibleValue(
        text="SECURITY_PROCEDURE",
        title="Security Procedure",
        description="Physical security and access control procedures")

    _defn = EnumDefinition(
        name="OperationalProcedureEnum",
        description="Standard nuclear facility operational procedures",
    )

class MiningType(EnumDefinitionImpl):
    """
    Types of mining operations
    """
    OPEN_PIT = PermissibleValue(
        text="OPEN_PIT",
        title="quarry",
        description="Open-pit mining",
        meaning=ENVO["00000284"])
    STRIP_MINING = PermissibleValue(
        text="STRIP_MINING",
        title="opencast mining",
        description="Strip mining",
        meaning=ENVO["01001441"])
    MOUNTAINTOP_REMOVAL = PermissibleValue(
        text="MOUNTAINTOP_REMOVAL",
        description="Mountaintop removal mining")
    QUARRYING = PermissibleValue(
        text="QUARRYING",
        title="quarry",
        description="Quarrying",
        meaning=ENVO["00000284"])
    PLACER = PermissibleValue(
        text="PLACER",
        title="alluvial deposit",
        description="Placer mining",
        meaning=ENVO["01001204"])
    DREDGING = PermissibleValue(
        text="DREDGING",
        description="Dredging")
    SHAFT_MINING = PermissibleValue(
        text="SHAFT_MINING",
        description="Shaft mining")
    DRIFT_MINING = PermissibleValue(
        text="DRIFT_MINING",
        description="Drift mining")
    SLOPE_MINING = PermissibleValue(
        text="SLOPE_MINING",
        description="Slope mining")
    ROOM_AND_PILLAR = PermissibleValue(
        text="ROOM_AND_PILLAR",
        description="Room and pillar mining")
    LONGWALL = PermissibleValue(
        text="LONGWALL",
        description="Longwall mining")
    BLOCK_CAVING = PermissibleValue(
        text="BLOCK_CAVING",
        description="Block caving")
    SOLUTION_MINING = PermissibleValue(
        text="SOLUTION_MINING",
        description="Solution mining (in-situ leaching)")
    HYDRAULIC_MINING = PermissibleValue(
        text="HYDRAULIC_MINING",
        description="Hydraulic mining")
    ARTISANAL = PermissibleValue(
        text="ARTISANAL",
        description="Artisanal and small-scale mining")
    DEEP_SEA = PermissibleValue(
        text="DEEP_SEA",
        description="Deep sea mining")

    _defn = EnumDefinition(
        name="MiningType",
        description="Types of mining operations",
    )

class MineralCategory(EnumDefinitionImpl):
    """
    Categories of minerals and materials
    """
    PRECIOUS_METALS = PermissibleValue(
        text="PRECIOUS_METALS",
        description="Precious metals")
    BASE_METALS = PermissibleValue(
        text="BASE_METALS",
        description="Base metals")
    FERROUS_METALS = PermissibleValue(
        text="FERROUS_METALS",
        description="Ferrous metals")
    RARE_EARTH_ELEMENTS = PermissibleValue(
        text="RARE_EARTH_ELEMENTS",
        description="Rare earth elements")
    RADIOACTIVE = PermissibleValue(
        text="RADIOACTIVE",
        description="Radioactive minerals")
    INDUSTRIAL_MINERALS = PermissibleValue(
        text="INDUSTRIAL_MINERALS",
        description="Industrial minerals")
    GEMSTONES = PermissibleValue(
        text="GEMSTONES",
        description="Gemstones")
    ENERGY_MINERALS = PermissibleValue(
        text="ENERGY_MINERALS",
        description="Energy minerals")
    CONSTRUCTION_MATERIALS = PermissibleValue(
        text="CONSTRUCTION_MATERIALS",
        description="Construction materials")
    CHEMICAL_MINERALS = PermissibleValue(
        text="CHEMICAL_MINERALS",
        description="Chemical and fertilizer minerals")

    _defn = EnumDefinition(
        name="MineralCategory",
        description="Categories of minerals and materials",
    )

class CriticalMineral(EnumDefinitionImpl):
    """
    Critical minerals essential for economic and national security,
    particularly for clean energy, defense, and technology applications.
    Based on US Geological Survey and EU critical raw materials lists.
    """
    LITHIUM = PermissibleValue(
        text="LITHIUM",
        title="lithium atom",
        description="Lithium (Li) - essential for batteries",
        meaning=CHEBI["30145"])
    COBALT = PermissibleValue(
        text="COBALT",
        title="cobalt atom",
        description="Cobalt (Co) - battery cathodes and superalloys",
        meaning=CHEBI["27638"])
    NICKEL = PermissibleValue(
        text="NICKEL",
        title="nickel atom",
        description="Nickel (Ni) - stainless steel and batteries",
        meaning=CHEBI["28112"])
    GRAPHITE = PermissibleValue(
        text="GRAPHITE",
        description="Graphite - battery anodes and refractories",
        meaning=CHEBI["33418"])
    MANGANESE = PermissibleValue(
        text="MANGANESE",
        title="manganese atom",
        description="Manganese (Mn) - steel and battery production",
        meaning=CHEBI["18291"])
    NEODYMIUM = PermissibleValue(
        text="NEODYMIUM",
        title="neodymium atom",
        description="Neodymium (Nd) - permanent magnets",
        meaning=CHEBI["33372"])
    DYSPROSIUM = PermissibleValue(
        text="DYSPROSIUM",
        title="dysprosium atom",
        description="Dysprosium (Dy) - high-performance magnets",
        meaning=CHEBI["33377"])
    PRASEODYMIUM = PermissibleValue(
        text="PRASEODYMIUM",
        title="praseodymium atom",
        description="Praseodymium (Pr) - magnets and alloys",
        meaning=CHEBI["49828"])
    TERBIUM = PermissibleValue(
        text="TERBIUM",
        title="terbium atom",
        description="Terbium (Tb) - phosphors and magnets",
        meaning=CHEBI["33376"])
    EUROPIUM = PermissibleValue(
        text="EUROPIUM",
        title="europium atom",
        description="Europium (Eu) - phosphors and nuclear control",
        meaning=CHEBI["32999"])
    YTTRIUM = PermissibleValue(
        text="YTTRIUM",
        title="yttrium atom",
        description="Yttrium (Y) - phosphors and ceramics",
        meaning=CHEBI["33331"])
    CERIUM = PermissibleValue(
        text="CERIUM",
        description="Cerium (Ce) - catalysts and glass polishing",
        meaning=CHEBI["33369"])
    LANTHANUM = PermissibleValue(
        text="LANTHANUM",
        title="lanthanum atom",
        description="Lanthanum (La) - catalysts and optics",
        meaning=CHEBI["33336"])
    GALLIUM = PermissibleValue(
        text="GALLIUM",
        title="gallium atom",
        description="Gallium (Ga) - semiconductors and LEDs",
        meaning=CHEBI["49631"])
    GERMANIUM = PermissibleValue(
        text="GERMANIUM",
        title="germanium atom",
        description="Germanium (Ge) - fiber optics and infrared",
        meaning=CHEBI["30441"])
    INDIUM = PermissibleValue(
        text="INDIUM",
        title="indium atom",
        description="Indium (In) - displays and semiconductors",
        meaning=CHEBI["30430"])
    TELLURIUM = PermissibleValue(
        text="TELLURIUM",
        title="tellurium atom",
        description="Tellurium (Te) - solar panels and thermoelectrics",
        meaning=CHEBI["30452"])
    ARSENIC = PermissibleValue(
        text="ARSENIC",
        title="arsenic atom",
        description="Arsenic (As) - semiconductors and alloys",
        meaning=CHEBI["27563"])
    TITANIUM = PermissibleValue(
        text="TITANIUM",
        title="titanium atom",
        description="Titanium (Ti) - aerospace and defense",
        meaning=CHEBI["33341"])
    VANADIUM = PermissibleValue(
        text="VANADIUM",
        title="vanadium atom",
        description="Vanadium (V) - steel alloys and batteries",
        meaning=CHEBI["27698"])
    CHROMIUM = PermissibleValue(
        text="CHROMIUM",
        title="chromium atom",
        description="Chromium (Cr) - stainless steel and alloys",
        meaning=CHEBI["28073"])
    TUNGSTEN = PermissibleValue(
        text="TUNGSTEN",
        description="Tungsten (W) - hard metals and electronics",
        meaning=CHEBI["27998"])
    TANTALUM = PermissibleValue(
        text="TANTALUM",
        title="tantalum atom",
        description="Tantalum (Ta) - capacitors and superalloys",
        meaning=CHEBI["33348"])
    NIOBIUM = PermissibleValue(
        text="NIOBIUM",
        title="niobium atom",
        description="Niobium (Nb) - steel alloys and superconductors",
        meaning=CHEBI["33344"])
    ZIRCONIUM = PermissibleValue(
        text="ZIRCONIUM",
        title="zirconium atom",
        description="Zirconium (Zr) - nuclear and ceramics",
        meaning=CHEBI["33342"])
    HAFNIUM = PermissibleValue(
        text="HAFNIUM",
        title="hafnium atom",
        description="Hafnium (Hf) - nuclear and semiconductors",
        meaning=CHEBI["33343"])
    PLATINUM = PermissibleValue(
        text="PLATINUM",
        title="platinum(0)",
        description="Platinum (Pt) - catalysts and electronics",
        meaning=CHEBI["33400"])
    PALLADIUM = PermissibleValue(
        text="PALLADIUM",
        description="Palladium (Pd) - catalysts and electronics",
        meaning=CHEBI["33363"])
    RHODIUM = PermissibleValue(
        text="RHODIUM",
        title="rhodium atom",
        description="Rhodium (Rh) - catalysts and electronics",
        meaning=CHEBI["33359"])
    IRIDIUM = PermissibleValue(
        text="IRIDIUM",
        title="iridium atom",
        description="Iridium (Ir) - electronics and catalysts",
        meaning=CHEBI["49666"])
    RUTHENIUM = PermissibleValue(
        text="RUTHENIUM",
        title="ruthenium atom",
        description="Ruthenium (Ru) - electronics and catalysts",
        meaning=CHEBI["30682"])
    ANTIMONY = PermissibleValue(
        text="ANTIMONY",
        title="antimony atom",
        description="Antimony (Sb) - flame retardants and batteries",
        meaning=CHEBI["30513"])
    BISMUTH = PermissibleValue(
        text="BISMUTH",
        title="bismuth atom",
        description="Bismuth (Bi) - pharmaceuticals and alloys",
        meaning=CHEBI["33301"])
    BERYLLIUM = PermissibleValue(
        text="BERYLLIUM",
        title="beryllium atom",
        description="Beryllium (Be) - aerospace and defense",
        meaning=CHEBI["30501"])
    MAGNESIUM = PermissibleValue(
        text="MAGNESIUM",
        title="magnesium atom",
        description="Magnesium (Mg) - lightweight alloys",
        meaning=CHEBI["25107"])
    ALUMINUM = PermissibleValue(
        text="ALUMINUM",
        title="aluminium atom",
        description="Aluminum (Al) - construction and transportation",
        meaning=CHEBI["28984"])
    TIN = PermissibleValue(
        text="TIN",
        title="tin atom",
        description="Tin (Sn) - solders and coatings",
        meaning=CHEBI["27007"])
    FLUORSPAR = PermissibleValue(
        text="FLUORSPAR",
        title="calcium difluoride",
        description="Fluorspar (CaF2) - steel and aluminum production",
        meaning=CHEBI["35437"])
    BARITE = PermissibleValue(
        text="BARITE",
        title="barium sulfate",
        description="Barite (BaSO4) - drilling and chemicals",
        meaning=CHEBI["133326"])
    HELIUM = PermissibleValue(
        text="HELIUM",
        title="helium(0)",
        description="Helium (He) - cryogenics and electronics",
        meaning=CHEBI["33681"])
    POTASH = PermissibleValue(
        text="POTASH",
        title="potassium oxide",
        description="Potash (K2O) - fertilizers and chemicals",
        meaning=CHEBI["88321"])
    PHOSPHATE_ROCK = PermissibleValue(
        text="PHOSPHATE_ROCK",
        title="phosphate",
        description="Phosphate rock - fertilizers and chemicals",
        meaning=CHEBI["26020"])
    SCANDIUM = PermissibleValue(
        text="SCANDIUM",
        title="scandium atom",
        description="Scandium (Sc) - aerospace alloys",
        meaning=CHEBI["33330"])
    STRONTIUM = PermissibleValue(
        text="STRONTIUM",
        title="strontium atom",
        description="Strontium (Sr) - magnets and pyrotechnics",
        meaning=CHEBI["33324"])

    _defn = EnumDefinition(
        name="CriticalMineral",
        description="""Critical minerals essential for economic and national security,
particularly for clean energy, defense, and technology applications.
Based on US Geological Survey and EU critical raw materials lists.""",
    )

class CommonMineral(EnumDefinitionImpl):
    """
    Common minerals extracted through mining
    """
    GOLD = PermissibleValue(
        text="GOLD",
        title="gold atom",
        description="Gold (Au)",
        meaning=CHEBI["29287"])
    SILVER = PermissibleValue(
        text="SILVER",
        title="silver atom",
        description="Silver (Ag)",
        meaning=CHEBI["30512"])
    PLATINUM = PermissibleValue(
        text="PLATINUM",
        title="elemental platinum",
        description="Platinum (Pt)",
        meaning=CHEBI["49202"])
    COPPER = PermissibleValue(
        text="COPPER",
        title="copper atom",
        description="Copper (Cu)",
        meaning=CHEBI["28694"])
    IRON = PermissibleValue(
        text="IRON",
        title="iron atom",
        description="Iron (Fe)",
        meaning=CHEBI["18248"])
    ALUMINUM = PermissibleValue(
        text="ALUMINUM",
        title="aluminium atom",
        description="Aluminum (Al)",
        meaning=CHEBI["28984"])
    ZINC = PermissibleValue(
        text="ZINC",
        title="zinc atom",
        description="Zinc (Zn)",
        meaning=CHEBI["27363"])
    LEAD = PermissibleValue(
        text="LEAD",
        title="lead atom",
        description="Lead (Pb)",
        meaning=CHEBI["25016"])
    NICKEL = PermissibleValue(
        text="NICKEL",
        title="nickel atom",
        description="Nickel (Ni)",
        meaning=CHEBI["28112"])
    TIN = PermissibleValue(
        text="TIN",
        title="tin atom",
        description="Tin (Sn)",
        meaning=CHEBI["27007"])
    COAL = PermissibleValue(
        text="COAL",
        description="Coal",
        meaning=ENVO["02000091"])
    URANIUM = PermissibleValue(
        text="URANIUM",
        title="uranium atom",
        description="Uranium (U)",
        meaning=CHEBI["27214"])
    LIMESTONE = PermissibleValue(
        text="LIMESTONE",
        description="Limestone (CaCO3)",
        meaning=ENVO["00002053"])
    SALT = PermissibleValue(
        text="SALT",
        description="Salt (NaCl)",
        meaning=CHEBI["24866"])
    PHOSPHATE = PermissibleValue(
        text="PHOSPHATE",
        description="Phosphate rock",
        meaning=CHEBI["26020"])
    POTASH = PermissibleValue(
        text="POTASH",
        title="potassium oxide",
        description="Potash (K2O)",
        meaning=CHEBI["88321"])
    LITHIUM = PermissibleValue(
        text="LITHIUM",
        title="lithium atom",
        description="Lithium (Li)",
        meaning=CHEBI["30145"])
    COBALT = PermissibleValue(
        text="COBALT",
        title="cobalt atom",
        description="Cobalt (Co)",
        meaning=CHEBI["27638"])
    DIAMOND = PermissibleValue(
        text="DIAMOND",
        description="Diamond (C)",
        meaning=CHEBI["33417"])

    _defn = EnumDefinition(
        name="CommonMineral",
        description="Common minerals extracted through mining",
    )

class MiningEquipment(EnumDefinitionImpl):
    """
    Types of mining equipment
    """
    DRILL_RIG = PermissibleValue(
        text="DRILL_RIG",
        description="Drilling rig")
    JUMBO_DRILL = PermissibleValue(
        text="JUMBO_DRILL",
        description="Jumbo drill")
    EXCAVATOR = PermissibleValue(
        text="EXCAVATOR",
        description="Excavator")
    DRAGLINE = PermissibleValue(
        text="DRAGLINE",
        description="Dragline excavator")
    BUCKET_WHEEL_EXCAVATOR = PermissibleValue(
        text="BUCKET_WHEEL_EXCAVATOR",
        description="Bucket-wheel excavator")
    HAUL_TRUCK = PermissibleValue(
        text="HAUL_TRUCK",
        description="Haul truck")
    LOADER = PermissibleValue(
        text="LOADER",
        description="Loader")
    CONVEYOR = PermissibleValue(
        text="CONVEYOR",
        description="Conveyor system")
    CRUSHER = PermissibleValue(
        text="CRUSHER",
        description="Crusher")
    BALL_MILL = PermissibleValue(
        text="BALL_MILL",
        description="Ball mill")
    FLOTATION_CELL = PermissibleValue(
        text="FLOTATION_CELL",
        description="Flotation cell")
    CONTINUOUS_MINER = PermissibleValue(
        text="CONTINUOUS_MINER",
        description="Continuous miner")
    ROOF_BOLTER = PermissibleValue(
        text="ROOF_BOLTER",
        description="Roof bolter")
    SHUTTLE_CAR = PermissibleValue(
        text="SHUTTLE_CAR",
        description="Shuttle car")

    _defn = EnumDefinition(
        name="MiningEquipment",
        description="Types of mining equipment",
    )

class OreGrade(EnumDefinitionImpl):
    """
    Classification of ore grades
    """
    HIGH_GRADE = PermissibleValue(
        text="HIGH_GRADE",
        description="High-grade ore")
    MEDIUM_GRADE = PermissibleValue(
        text="MEDIUM_GRADE",
        description="Medium-grade ore")
    LOW_GRADE = PermissibleValue(
        text="LOW_GRADE",
        description="Low-grade ore")
    MARGINAL = PermissibleValue(
        text="MARGINAL",
        description="Marginal ore")
    SUB_ECONOMIC = PermissibleValue(
        text="SUB_ECONOMIC",
        description="Sub-economic ore")
    WASTE = PermissibleValue(
        text="WASTE",
        description="Waste rock")

    _defn = EnumDefinition(
        name="OreGrade",
        description="Classification of ore grades",
    )

class MiningPhase(EnumDefinitionImpl):
    """
    Phases of mining operations
    """
    EXPLORATION = PermissibleValue(
        text="EXPLORATION",
        description="Exploration phase")
    DEVELOPMENT = PermissibleValue(
        text="DEVELOPMENT",
        description="Development phase")
    PRODUCTION = PermissibleValue(
        text="PRODUCTION",
        description="Production/extraction phase")
    PROCESSING = PermissibleValue(
        text="PROCESSING",
        description="Processing/beneficiation phase")
    CLOSURE = PermissibleValue(
        text="CLOSURE",
        description="Closure phase")
    RECLAMATION = PermissibleValue(
        text="RECLAMATION",
        description="Reclamation phase")
    POST_CLOSURE = PermissibleValue(
        text="POST_CLOSURE",
        description="Post-closure monitoring")

    _defn = EnumDefinition(
        name="MiningPhase",
        description="Phases of mining operations",
    )

class MiningHazard(EnumDefinitionImpl):
    """
    Mining-related hazards and risks
    """
    CAVE_IN = PermissibleValue(
        text="CAVE_IN",
        description="Cave-in/roof collapse")
    GAS_EXPLOSION = PermissibleValue(
        text="GAS_EXPLOSION",
        description="Gas explosion")
    FLOODING = PermissibleValue(
        text="FLOODING",
        description="Mine flooding")
    DUST_EXPOSURE = PermissibleValue(
        text="DUST_EXPOSURE",
        description="Dust exposure")
    CHEMICAL_EXPOSURE = PermissibleValue(
        text="CHEMICAL_EXPOSURE",
        description="Chemical exposure")
    RADIATION = PermissibleValue(
        text="RADIATION",
        description="Radiation exposure")
    NOISE = PermissibleValue(
        text="NOISE",
        description="Noise exposure")
    VIBRATION = PermissibleValue(
        text="VIBRATION",
        description="Vibration exposure")
    HEAT_STRESS = PermissibleValue(
        text="HEAT_STRESS",
        description="Heat stress")
    EQUIPMENT_ACCIDENT = PermissibleValue(
        text="EQUIPMENT_ACCIDENT",
        description="Equipment-related accident")

    _defn = EnumDefinition(
        name="MiningHazard",
        description="Mining-related hazards and risks",
    )

class EnvironmentalImpact(EnumDefinitionImpl):
    """
    Environmental impacts of mining
    """
    HABITAT_DESTRUCTION = PermissibleValue(
        text="HABITAT_DESTRUCTION",
        title="habitat degradation",
        description="Habitat destruction",
        meaning=EXO["0000012"])
    WATER_POLLUTION = PermissibleValue(
        text="WATER_POLLUTION",
        description="Water pollution",
        meaning=ENVO["02500039"])
    AIR_POLLUTION = PermissibleValue(
        text="AIR_POLLUTION",
        description="Air pollution",
        meaning=ENVO["02500037"])
    SOIL_CONTAMINATION = PermissibleValue(
        text="SOIL_CONTAMINATION",
        title="contaminated soil",
        description="Soil contamination",
        meaning=ENVO["00002116"])
    DEFORESTATION = PermissibleValue(
        text="DEFORESTATION",
        description="Deforestation",
        meaning=ENVO["02500012"])
    EROSION = PermissibleValue(
        text="EROSION",
        description="Erosion and sedimentation",
        meaning=ENVO["01001346"])
    ACID_MINE_DRAINAGE = PermissibleValue(
        text="ACID_MINE_DRAINAGE",
        description="Acid mine drainage",
        meaning=ENVO["00001997"])
    TAILINGS = PermissibleValue(
        text="TAILINGS",
        description="Tailings contamination")
    SUBSIDENCE = PermissibleValue(
        text="SUBSIDENCE",
        description="Ground subsidence")
    BIODIVERSITY_LOSS = PermissibleValue(
        text="BIODIVERSITY_LOSS",
        description="Biodiversity loss")

    _defn = EnumDefinition(
        name="EnvironmentalImpact",
        description="Environmental impacts of mining",
    )

class ExtractiveIndustryFacilityTypeEnum(EnumDefinitionImpl):
    """
    Types of extractive industry facilities
    """
    MINING_FACILITY = PermissibleValue(
        text="MINING_FACILITY",
        title="Mining Facility",
        description="A facility where mineral resources are extracted")
    WELL_FACILITY = PermissibleValue(
        text="WELL_FACILITY",
        title="Well Facility",
        description="A facility where fluid resources are extracted")
    QUARRY_FACILITY = PermissibleValue(
        text="QUARRY_FACILITY",
        title="Quarry Facility",
        description="A facility where stone, sand, or gravel are extracted")

    _defn = EnumDefinition(
        name="ExtractiveIndustryFacilityTypeEnum",
        description="Types of extractive industry facilities",
    )

class ExtractiveIndustryProductTypeEnum(EnumDefinitionImpl):
    """
    Types of products extracted from extractive industry facilities
    """
    MINERAL = PermissibleValue(
        text="MINERAL",
        title="Mineral",
        description="A solid inorganic substance")
    METAL = PermissibleValue(
        text="METAL",
        title="Metal",
        description="A solid metallic substance")
    COAL = PermissibleValue(
        text="COAL",
        title="Coal",
        description="A combustible black or brownish-black sedimentary rock")
    OIL = PermissibleValue(
        text="OIL",
        title="Oil",
        description="A liquid petroleum resource")
    GAS = PermissibleValue(
        text="GAS",
        title="Gas",
        description="A gaseous petroleum resource")
    STONE = PermissibleValue(
        text="STONE",
        title="Stone",
        description="A solid aggregate of minerals")
    SAND = PermissibleValue(
        text="SAND",
        title="Sand",
        description="A granular material composed of finely divided rock and mineral particles")
    GRAVEL = PermissibleValue(
        text="GRAVEL",
        title="Gravel",
        description="A loose aggregation of rock fragments")

    _defn = EnumDefinition(
        name="ExtractiveIndustryProductTypeEnum",
        description="Types of products extracted from extractive industry facilities",
    )

class MiningMethodEnum(EnumDefinitionImpl):
    """
    Methods used for extracting minerals from the earth
    """
    UNDERGROUND = PermissibleValue(
        text="UNDERGROUND",
        title="Underground",
        description="Extraction occurs beneath the earth's surface")
    OPEN_PIT = PermissibleValue(
        text="OPEN_PIT",
        title="Open Pit",
        description="Extraction occurs on the earth's surface")
    PLACER = PermissibleValue(
        text="PLACER",
        title="Placer",
        description="Extraction of valuable minerals from alluvial deposits")
    IN_SITU = PermissibleValue(
        text="IN_SITU",
        title="In Situ",
        description="Extraction without removing the ore from its original location")

    _defn = EnumDefinition(
        name="MiningMethodEnum",
        description="Methods used for extracting minerals from the earth",
    )

class WellTypeEnum(EnumDefinitionImpl):
    """
    Types of wells used for extracting fluid resources
    """
    OIL = PermissibleValue(
        text="OIL",
        title="Oil",
        description="A well that primarily extracts crude oil")
    GAS = PermissibleValue(
        text="GAS",
        title="Gas",
        description="A well that primarily extracts natural gas")
    WATER = PermissibleValue(
        text="WATER",
        title="Water",
        description="A well that extracts water for various purposes")
    INJECTION = PermissibleValue(
        text="INJECTION",
        title="Injection",
        description="A well used to inject fluids into underground formations")

    _defn = EnumDefinition(
        name="WellTypeEnum",
        description="Types of wells used for extracting fluid resources",
    )

class OutcomeTypeEnum(EnumDefinitionImpl):
    """
    Types of prediction outcomes for classification tasks
    """
    TP = PermissibleValue(
        text="TP",
        title="True Positive",
        description="True Positive")
    FP = PermissibleValue(
        text="FP",
        title="False Positive",
        description="False Positive")
    TN = PermissibleValue(
        text="TN",
        title="True Negative",
        description="True Negative")
    FN = PermissibleValue(
        text="FN",
        title="False Negative",
        description="False Negative")

    _defn = EnumDefinition(
        name="OutcomeTypeEnum",
        description="Types of prediction outcomes for classification tasks",
    )

class PersonStatusEnum(EnumDefinitionImpl):
    """
    Vital status of a person (living or deceased)
    """
    ALIVE = PermissibleValue(
        text="ALIVE",
        title="Alive",
        description="The person is living",
        meaning=PATO["0001421"])
    DEAD = PermissibleValue(
        text="DEAD",
        title="Dead",
        description="The person is deceased",
        meaning=PATO["0001422"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        title="Unknown",
        description="The vital status is not known",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="PersonStatusEnum",
        description="Vital status of a person (living or deceased)",
    )

class MimeType(EnumDefinitionImpl):
    """
    Common MIME types for various file formats
    """
    APPLICATION_JSON = PermissibleValue(
        text="APPLICATION_JSON",
        description="JSON format",
        meaning=IANA["application/json"])
    APPLICATION_XML = PermissibleValue(
        text="APPLICATION_XML",
        description="XML format",
        meaning=IANA["application/xml"])
    APPLICATION_PDF = PermissibleValue(
        text="APPLICATION_PDF",
        description="Adobe Portable Document Format",
        meaning=IANA["application/pdf"])
    APPLICATION_ZIP = PermissibleValue(
        text="APPLICATION_ZIP",
        description="ZIP archive",
        meaning=IANA["application/zip"])
    APPLICATION_GZIP = PermissibleValue(
        text="APPLICATION_GZIP",
        description="GZIP compressed archive",
        meaning=IANA["application/gzip"])
    APPLICATION_OCTET_STREAM = PermissibleValue(
        text="APPLICATION_OCTET_STREAM",
        description="Binary data",
        meaning=IANA["application/octet-stream"])
    APPLICATION_X_WWW_FORM_URLENCODED = PermissibleValue(
        text="APPLICATION_X_WWW_FORM_URLENCODED",
        description="Form data encoded",
        meaning=IANA["application/x-www-form-urlencoded"])
    APPLICATION_VND_MS_EXCEL = PermissibleValue(
        text="APPLICATION_VND_MS_EXCEL",
        description="Microsoft Excel",
        meaning=IANA["application/vnd.ms-excel"])
    APPLICATION_VND_OPENXMLFORMATS_SPREADSHEET = PermissibleValue(
        text="APPLICATION_VND_OPENXMLFORMATS_SPREADSHEET",
        description="Microsoft Excel (OpenXML)",
        meaning=IANA["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"])
    APPLICATION_VND_MS_POWERPOINT = PermissibleValue(
        text="APPLICATION_VND_MS_POWERPOINT",
        description="Microsoft PowerPoint",
        meaning=IANA["application/vnd.ms-powerpoint"])
    APPLICATION_MSWORD = PermissibleValue(
        text="APPLICATION_MSWORD",
        description="Microsoft Word",
        meaning=IANA["application/msword"])
    APPLICATION_VND_OPENXMLFORMATS_DOCUMENT = PermissibleValue(
        text="APPLICATION_VND_OPENXMLFORMATS_DOCUMENT",
        description="Microsoft Word (OpenXML)",
        meaning=IANA["application/vnd.openxmlformats-officedocument.wordprocessingml.document"])
    APPLICATION_JAVASCRIPT = PermissibleValue(
        text="APPLICATION_JAVASCRIPT",
        description="JavaScript",
        meaning=IANA["application/javascript"])
    APPLICATION_TYPESCRIPT = PermissibleValue(
        text="APPLICATION_TYPESCRIPT",
        description="TypeScript source code",
        meaning=IANA["application/typescript"])
    APPLICATION_SQL = PermissibleValue(
        text="APPLICATION_SQL",
        description="SQL database format",
        meaning=IANA["application/sql"])
    APPLICATION_GRAPHQL = PermissibleValue(
        text="APPLICATION_GRAPHQL",
        description="GraphQL query language",
        meaning=IANA["application/graphql"])
    APPLICATION_LD_JSON = PermissibleValue(
        text="APPLICATION_LD_JSON",
        description="JSON-LD format",
        meaning=IANA["application/ld+json"])
    APPLICATION_WASM = PermissibleValue(
        text="APPLICATION_WASM",
        description="WebAssembly binary format",
        meaning=IANA["application/wasm"])
    TEXT_PLAIN = PermissibleValue(
        text="TEXT_PLAIN",
        description="Plain text",
        meaning=IANA["text/plain"])
    TEXT_HTML = PermissibleValue(
        text="TEXT_HTML",
        description="HTML document",
        meaning=IANA["text/html"])
    TEXT_CSS = PermissibleValue(
        text="TEXT_CSS",
        description="Cascading Style Sheets",
        meaning=IANA["text/css"])
    TEXT_CSV = PermissibleValue(
        text="TEXT_CSV",
        description="Comma-separated values",
        meaning=IANA["text/csv"])
    TEXT_MARKDOWN = PermissibleValue(
        text="TEXT_MARKDOWN",
        description="Markdown format",
        meaning=IANA["text/markdown"])
    TEXT_YAML = PermissibleValue(
        text="TEXT_YAML",
        description="YAML format",
        meaning=IANA["text/yaml"])
    TEXT_X_PYTHON = PermissibleValue(
        text="TEXT_X_PYTHON",
        description="Python source code",
        meaning=IANA["text/x-python"])
    TEXT_X_JAVA = PermissibleValue(
        text="TEXT_X_JAVA",
        description="Java source code",
        meaning=IANA["text/x-java-source"])
    TEXT_X_C = PermissibleValue(
        text="TEXT_X_C",
        description="C source code",
        meaning=IANA["text/x-c"])
    TEXT_X_CPP = PermissibleValue(
        text="TEXT_X_CPP",
        description="C++ source code",
        meaning=IANA["text/x-c++"])
    TEXT_X_CSHARP = PermissibleValue(
        text="TEXT_X_CSHARP",
        description="C# source code",
        meaning=IANA["text/x-csharp"])
    TEXT_X_GO = PermissibleValue(
        text="TEXT_X_GO",
        description="Go source code",
        meaning=IANA["text/x-go"])
    TEXT_X_RUST = PermissibleValue(
        text="TEXT_X_RUST",
        description="Rust source code",
        meaning=IANA["text/x-rust"])
    TEXT_X_RUBY = PermissibleValue(
        text="TEXT_X_RUBY",
        description="Ruby source code",
        meaning=IANA["text/x-ruby"])
    TEXT_X_SHELLSCRIPT = PermissibleValue(
        text="TEXT_X_SHELLSCRIPT",
        description="Shell script",
        meaning=IANA["text/x-shellscript"])
    IMAGE_JPEG = PermissibleValue(
        text="IMAGE_JPEG",
        description="JPEG image",
        meaning=IANA["image/jpeg"])
    IMAGE_PNG = PermissibleValue(
        text="IMAGE_PNG",
        description="PNG image",
        meaning=IANA["image/png"])
    IMAGE_GIF = PermissibleValue(
        text="IMAGE_GIF",
        description="GIF image",
        meaning=IANA["image/gif"])
    IMAGE_SVG_XML = PermissibleValue(
        text="IMAGE_SVG_XML",
        description="SVG vector image",
        meaning=IANA["image/svg+xml"])
    IMAGE_WEBP = PermissibleValue(
        text="IMAGE_WEBP",
        description="WebP image",
        meaning=IANA["image/webp"])
    IMAGE_BMP = PermissibleValue(
        text="IMAGE_BMP",
        description="Bitmap image",
        meaning=IANA["image/bmp"])
    IMAGE_ICO = PermissibleValue(
        text="IMAGE_ICO",
        description="Icon format",
        meaning=IANA["image/vnd.microsoft.icon"])
    IMAGE_TIFF = PermissibleValue(
        text="IMAGE_TIFF",
        description="TIFF image",
        meaning=IANA["image/tiff"])
    IMAGE_AVIF = PermissibleValue(
        text="IMAGE_AVIF",
        description="AVIF image format",
        meaning=IANA["image/avif"])
    AUDIO_MPEG = PermissibleValue(
        text="AUDIO_MPEG",
        description="MP3 audio",
        meaning=IANA["audio/mpeg"])
    AUDIO_WAV = PermissibleValue(
        text="AUDIO_WAV",
        description="WAV audio",
        meaning=IANA["audio/wav"])
    AUDIO_OGG = PermissibleValue(
        text="AUDIO_OGG",
        description="OGG audio",
        meaning=IANA["audio/ogg"])
    AUDIO_WEBM = PermissibleValue(
        text="AUDIO_WEBM",
        description="WebM audio",
        meaning=IANA["audio/webm"])
    AUDIO_AAC = PermissibleValue(
        text="AUDIO_AAC",
        description="AAC audio",
        meaning=IANA["audio/aac"])
    VIDEO_MP4 = PermissibleValue(
        text="VIDEO_MP4",
        description="MP4 video",
        meaning=IANA["video/mp4"])
    VIDEO_MPEG = PermissibleValue(
        text="VIDEO_MPEG",
        description="MPEG video",
        meaning=IANA["video/mpeg"])
    VIDEO_WEBM = PermissibleValue(
        text="VIDEO_WEBM",
        description="WebM video",
        meaning=IANA["video/webm"])
    VIDEO_OGG = PermissibleValue(
        text="VIDEO_OGG",
        description="OGG video",
        meaning=IANA["video/ogg"])
    VIDEO_QUICKTIME = PermissibleValue(
        text="VIDEO_QUICKTIME",
        description="QuickTime video",
        meaning=IANA["video/quicktime"])
    VIDEO_AVI = PermissibleValue(
        text="VIDEO_AVI",
        description="AVI video",
        meaning=IANA["video/x-msvideo"])
    FONT_WOFF = PermissibleValue(
        text="FONT_WOFF",
        description="Web Open Font Format",
        meaning=IANA["font/woff"])
    FONT_WOFF2 = PermissibleValue(
        text="FONT_WOFF2",
        description="Web Open Font Format 2",
        meaning=IANA["font/woff2"])
    FONT_TTF = PermissibleValue(
        text="FONT_TTF",
        description="TrueType Font",
        meaning=IANA["font/ttf"])
    FONT_OTF = PermissibleValue(
        text="FONT_OTF",
        description="OpenType Font",
        meaning=IANA["font/otf"])
    MULTIPART_FORM_DATA = PermissibleValue(
        text="MULTIPART_FORM_DATA",
        description="Form data with file upload",
        meaning=IANA["multipart/form-data"])
    MULTIPART_MIXED = PermissibleValue(
        text="MULTIPART_MIXED",
        description="Mixed multipart message",
        meaning=IANA["multipart/mixed"])

    _defn = EnumDefinition(
        name="MimeType",
        description="Common MIME types for various file formats",
    )

class MimeTypeCategory(EnumDefinitionImpl):
    """
    Categories of MIME types
    """
    APPLICATION = PermissibleValue(
        text="APPLICATION",
        description="Application data")
    TEXT = PermissibleValue(
        text="TEXT",
        description="Text documents")
    IMAGE = PermissibleValue(
        text="IMAGE",
        description="Image files")
    AUDIO = PermissibleValue(
        text="AUDIO",
        description="Audio files")
    VIDEO = PermissibleValue(
        text="VIDEO",
        description="Video files")
    FONT = PermissibleValue(
        text="FONT",
        description="Font files")
    MULTIPART = PermissibleValue(
        text="MULTIPART",
        description="Multipart messages")
    MESSAGE = PermissibleValue(
        text="MESSAGE",
        description="Message formats")
    MODEL = PermissibleValue(
        text="MODEL",
        description="3D models and similar")

    _defn = EnumDefinition(
        name="MimeTypeCategory",
        description="Categories of MIME types",
    )

class TextCharset(EnumDefinitionImpl):
    """
    Character encodings for text content
    """
    UTF_8 = PermissibleValue(
        text="UTF_8",
        description="UTF-8 Unicode encoding")
    UTF_16 = PermissibleValue(
        text="UTF_16",
        description="UTF-16 Unicode encoding")
    UTF_32 = PermissibleValue(
        text="UTF_32",
        description="UTF-32 Unicode encoding")
    ASCII = PermissibleValue(
        text="ASCII",
        description="ASCII encoding")
    ISO_8859_1 = PermissibleValue(
        text="ISO_8859_1",
        description="ISO-8859-1 (Latin-1) encoding")
    ISO_8859_2 = PermissibleValue(
        text="ISO_8859_2",
        description="ISO-8859-2 (Latin-2) encoding")
    WINDOWS_1252 = PermissibleValue(
        text="WINDOWS_1252",
        description="Windows-1252 encoding")
    GB2312 = PermissibleValue(
        text="GB2312",
        description="Simplified Chinese encoding")
    SHIFT_JIS = PermissibleValue(
        text="SHIFT_JIS",
        description="Japanese encoding")
    EUC_KR = PermissibleValue(
        text="EUC_KR",
        description="Korean encoding")
    BIG5 = PermissibleValue(
        text="BIG5",
        description="Traditional Chinese encoding")

    _defn = EnumDefinition(
        name="TextCharset",
        description="Character encodings for text content",
    )

class CompressionType(EnumDefinitionImpl):
    """
    Compression types used with Content-Encoding
    """
    GZIP = PermissibleValue(
        text="GZIP",
        description="GZIP compression")
    DEFLATE = PermissibleValue(
        text="DEFLATE",
        description="DEFLATE compression")
    BR = PermissibleValue(
        text="BR",
        description="Brotli compression")
    COMPRESS = PermissibleValue(
        text="COMPRESS",
        description="Unix compress")
    IDENTITY = PermissibleValue(
        text="IDENTITY",
        description="No compression")

    _defn = EnumDefinition(
        name="CompressionType",
        description="Compression types used with Content-Encoding",
    )

class StateOfMatterEnum(EnumDefinitionImpl):
    """
    The physical state or phase of matter
    """
    SOLID = PermissibleValue(
        text="SOLID",
        description="A state of matter where particles are closely packed together with fixed positions",
        meaning=AFO["AFQ_0000112"])
    LIQUID = PermissibleValue(
        text="LIQUID",
        description="A nearly incompressible fluid that conforms to the shape of its container",
        meaning=AFO["AFQ_0000113"])
    GAS = PermissibleValue(
        text="GAS",
        description="A compressible fluid that expands to fill its container",
        meaning=AFO["AFQ_0000114"])
    PLASMA = PermissibleValue(
        text="PLASMA",
        description="An ionized gas with freely moving charged particles",
        meaning=AFO["AFQ_0000115"])
    BOSE_EINSTEIN_CONDENSATE = PermissibleValue(
        text="BOSE_EINSTEIN_CONDENSATE",
        description="""A state of matter formed at extremely low temperatures where particles occupy the same quantum state""")
    FERMIONIC_CONDENSATE = PermissibleValue(
        text="FERMIONIC_CONDENSATE",
        description="A superfluid phase formed by fermionic particles at extremely low temperatures")
    SUPERCRITICAL_FLUID = PermissibleValue(
        text="SUPERCRITICAL_FLUID",
        description="A state where distinct liquid and gas phases do not exist")
    SUPERFLUID = PermissibleValue(
        text="SUPERFLUID",
        description="A phase of matter with zero viscosity")
    SUPERSOLID = PermissibleValue(
        text="SUPERSOLID",
        description="A spatially ordered material with superfluid properties")
    QUARK_GLUON_PLASMA = PermissibleValue(
        text="QUARK_GLUON_PLASMA",
        description="An extremely hot phase where quarks and gluons are not confined")

    _defn = EnumDefinition(
        name="StateOfMatterEnum",
        description="The physical state or phase of matter",
    )

class AirPollutantEnum(EnumDefinitionImpl):
    """
    Common air pollutants and air quality indicators
    """
    PM2_5 = PermissibleValue(
        text="PM2_5",
        title="fine respirable suspended particulate matter",
        description="Fine particulate matter with diameter less than 2.5 micrometers",
        meaning=ENVO["01000415"])
    PM10 = PermissibleValue(
        text="PM10",
        title="respirable suspended particulate matter",
        description="Respirable particulate matter with diameter less than 10 micrometers",
        meaning=ENVO["01000405"])
    ULTRAFINE_PARTICLES = PermissibleValue(
        text="ULTRAFINE_PARTICLES",
        title="ultrafine respirable suspended particulate matter",
        description="Ultrafine particles with diameter less than 100 nanometers",
        meaning=ENVO["01000416"])
    OZONE = PermissibleValue(
        text="OZONE",
        description="Ground-level ozone (O3)",
        meaning=CHEBI["25812"])
    NITROGEN_DIOXIDE = PermissibleValue(
        text="NITROGEN_DIOXIDE",
        description="Nitrogen dioxide (NO2)",
        meaning=CHEBI["33101"])
    SULFUR_DIOXIDE = PermissibleValue(
        text="SULFUR_DIOXIDE",
        description="Sulfur dioxide (SO2)",
        meaning=CHEBI["18422"])
    CARBON_MONOXIDE = PermissibleValue(
        text="CARBON_MONOXIDE",
        description="Carbon monoxide (CO)",
        meaning=CHEBI["17245"])
    LEAD = PermissibleValue(
        text="LEAD",
        title="Lead Metal",
        description="Airborne lead particles",
        meaning=NCIT["C44396"])
    BENZENE = PermissibleValue(
        text="BENZENE",
        description="Benzene vapor",
        meaning=CHEBI["16716"])
    FORMALDEHYDE = PermissibleValue(
        text="FORMALDEHYDE",
        description="Formaldehyde gas",
        meaning=CHEBI["16842"])
    VOLATILE_ORGANIC_COMPOUNDS = PermissibleValue(
        text="VOLATILE_ORGANIC_COMPOUNDS",
        title="volatile organic compound",
        description="Volatile organic compounds (VOCs)",
        meaning=CHEBI["134179"])
    POLYCYCLIC_AROMATIC_HYDROCARBONS = PermissibleValue(
        text="POLYCYCLIC_AROMATIC_HYDROCARBONS",
        title="polycyclic arene",
        description="Polycyclic aromatic hydrocarbons (PAHs)",
        meaning=CHEBI["33848"])

    _defn = EnumDefinition(
        name="AirPollutantEnum",
        description="Common air pollutants and air quality indicators",
    )

class PesticideTypeEnum(EnumDefinitionImpl):
    """
    Categories of pesticides by target organism or chemical class
    """
    HERBICIDE = PermissibleValue(
        text="HERBICIDE",
        description="Chemical used to kill unwanted plants",
        meaning=CHEBI["24527"])
    INSECTICIDE = PermissibleValue(
        text="INSECTICIDE",
        description="Chemical used to kill insects",
        meaning=CHEBI["24852"])
    FUNGICIDE = PermissibleValue(
        text="FUNGICIDE",
        description="Chemical used to kill fungi",
        meaning=CHEBI["24127"])
    RODENTICIDE = PermissibleValue(
        text="RODENTICIDE",
        description="Chemical used to kill rodents",
        meaning=CHEBI["33288"])
    ORGANOPHOSPHATE = PermissibleValue(
        text="ORGANOPHOSPHATE",
        title="organophosphate insecticide",
        description="Organophosphate pesticide",
        meaning=CHEBI["25708"])
    ORGANOCHLORINE = PermissibleValue(
        text="ORGANOCHLORINE",
        title="organochlorine insecticide",
        description="Organochlorine pesticide",
        meaning=CHEBI["25705"])
    PYRETHROID = PermissibleValue(
        text="PYRETHROID",
        title="pyrethroid insecticide",
        description="Pyrethroid pesticide",
        meaning=CHEBI["26413"])
    CARBAMATE = PermissibleValue(
        text="CARBAMATE",
        title="carbamate insecticide",
        description="Carbamate pesticide",
        meaning=CHEBI["38461"])
    NEONICOTINOID = PermissibleValue(
        text="NEONICOTINOID",
        title="neonicotinoid insectide",
        description="Neonicotinoid pesticide",
        meaning=CHEBI["25540"])
    GLYPHOSATE = PermissibleValue(
        text="GLYPHOSATE",
        description="Glyphosate herbicide",
        meaning=CHEBI["27744"])

    _defn = EnumDefinition(
        name="PesticideTypeEnum",
        description="Categories of pesticides by target organism or chemical class",
    )

class HeavyMetalEnum(EnumDefinitionImpl):
    """
    Heavy metals of environmental health concern
    """
    LEAD = PermissibleValue(
        text="LEAD",
        title="Lead Metal",
        description="Lead (Pb)",
        meaning=NCIT["C44396"])
    MERCURY = PermissibleValue(
        text="MERCURY",
        description="Mercury (Hg)",
        meaning=NCIT["C66842"])
    CADMIUM = PermissibleValue(
        text="CADMIUM",
        description="Cadmium (Cd)",
        meaning=NCIT["C44348"])
    ARSENIC = PermissibleValue(
        text="ARSENIC",
        description="Arsenic (As)",
        meaning=NCIT["C28131"])
    CHROMIUM = PermissibleValue(
        text="CHROMIUM",
        description="Chromium (Cr)",
        meaning=NCIT["C370"])
    NICKEL = PermissibleValue(
        text="NICKEL",
        title="nickel atom",
        description="Nickel (Ni)",
        meaning=CHEBI["28112"])
    COPPER = PermissibleValue(
        text="COPPER",
        title="copper atom",
        description="Copper (Cu)",
        meaning=CHEBI["28694"])
    ZINC = PermissibleValue(
        text="ZINC",
        title="zinc atom",
        description="Zinc (Zn)",
        meaning=CHEBI["27363"])
    MANGANESE = PermissibleValue(
        text="MANGANESE",
        title="manganese atom",
        description="Manganese (Mn)",
        meaning=CHEBI["18291"])
    COBALT = PermissibleValue(
        text="COBALT",
        title="cobalt atom",
        description="Cobalt (Co)",
        meaning=CHEBI["27638"])

    _defn = EnumDefinition(
        name="HeavyMetalEnum",
        description="Heavy metals of environmental health concern",
    )

class ExposureRouteEnum(EnumDefinitionImpl):
    """
    Routes by which exposure to environmental agents occurs
    """
    INHALATION = PermissibleValue(
        text="INHALATION",
        title="Nasal Route of Administration",
        description="Exposure through breathing",
        meaning=NCIT["C38284"])
    INGESTION = PermissibleValue(
        text="INGESTION",
        title="Oral Route of Administration",
        description="Exposure through eating or drinking",
        meaning=NCIT["C38288"])
    DERMAL = PermissibleValue(
        text="DERMAL",
        title="Cutaneous Route of Administration",
        description="Exposure through skin contact",
        meaning=NCIT["C38675"])
    INJECTION = PermissibleValue(
        text="INJECTION",
        title="Intravenous Route of Administration",
        description="Exposure through injection",
        meaning=NCIT["C38276"])
    TRANSPLACENTAL = PermissibleValue(
        text="TRANSPLACENTAL",
        title="Transplacental Route of Administration",
        description="Exposure through placental transfer",
        meaning=NCIT["C38307"])
    OCULAR = PermissibleValue(
        text="OCULAR",
        title="Ophthalmic Route of Administration",
        description="Exposure through the eyes",
        meaning=NCIT["C38287"])
    MULTIPLE_ROUTES = PermissibleValue(
        text="MULTIPLE_ROUTES",
        description="Exposure through multiple pathways")

    _defn = EnumDefinition(
        name="ExposureRouteEnum",
        description="Routes by which exposure to environmental agents occurs",
    )

class ExposureSourceEnum(EnumDefinitionImpl):
    """
    Common sources of environmental exposures
    """
    AMBIENT_AIR = PermissibleValue(
        text="AMBIENT_AIR",
        description="Outdoor air pollution")
    INDOOR_AIR = PermissibleValue(
        text="INDOOR_AIR",
        description="Indoor air pollution")
    DRINKING_WATER = PermissibleValue(
        text="DRINKING_WATER",
        description="Contaminated drinking water")
    SOIL = PermissibleValue(
        text="SOIL",
        title="contaminated soil",
        description="Contaminated soil",
        meaning=ENVO["00002116"])
    FOOD = PermissibleValue(
        text="FOOD",
        description="Contaminated food")
    OCCUPATIONAL = PermissibleValue(
        text="OCCUPATIONAL",
        title="occupational environment",
        description="Workplace exposure",
        meaning=ENVO["03501332"])
    CONSUMER_PRODUCTS = PermissibleValue(
        text="CONSUMER_PRODUCTS",
        description="Household and consumer products")
    INDUSTRIAL_EMISSIONS = PermissibleValue(
        text="INDUSTRIAL_EMISSIONS",
        description="Industrial facility emissions")
    AGRICULTURAL = PermissibleValue(
        text="AGRICULTURAL",
        description="Agricultural activities")
    TRAFFIC = PermissibleValue(
        text="TRAFFIC",
        description="Traffic-related pollution")
    TOBACCO_SMOKE = PermissibleValue(
        text="TOBACCO_SMOKE",
        title="Passive Smoke Exposure",
        description="Active or passive tobacco smoke exposure",
        meaning=NCIT["C17140"])
    CONSTRUCTION = PermissibleValue(
        text="CONSTRUCTION",
        description="Construction-related exposure")
    MINING = PermissibleValue(
        text="MINING",
        description="Mining-related exposure")

    _defn = EnumDefinition(
        name="ExposureSourceEnum",
        description="Common sources of environmental exposures",
    )

class WaterContaminantEnum(EnumDefinitionImpl):
    """
    Common water contaminants
    """
    LEAD = PermissibleValue(
        text="LEAD",
        title="Lead Metal",
        description="Lead contamination",
        meaning=NCIT["C44396"])
    ARSENIC = PermissibleValue(
        text="ARSENIC",
        description="Arsenic contamination",
        meaning=NCIT["C28131"])
    NITRATES = PermissibleValue(
        text="NITRATES",
        title="nitrate",
        description="Nitrate contamination",
        meaning=CHEBI["17632"])
    FLUORIDE = PermissibleValue(
        text="FLUORIDE",
        description="Fluoride levels",
        meaning=CHEBI["17051"])
    CHLORINE = PermissibleValue(
        text="CHLORINE",
        description="Chlorine and chlorination byproducts",
        meaning=NCIT["C28140"])
    BACTERIA = PermissibleValue(
        text="BACTERIA",
        description="Bacterial contamination",
        meaning=NCIT["C14187"])
    VIRUSES = PermissibleValue(
        text="VIRUSES",
        title="Virus",
        description="Viral contamination",
        meaning=NCIT["C14283"])
    PARASITES = PermissibleValue(
        text="PARASITES",
        title="Parasite",
        description="Parasitic contamination",
        meaning=NCIT["C28176"])
    PFAS = PermissibleValue(
        text="PFAS",
        title="perfluoroalkyl substance",
        description="Per- and polyfluoroalkyl substances",
        meaning=CHEBI["172397"])
    MICROPLASTICS = PermissibleValue(
        text="MICROPLASTICS",
        title="microplastic particle",
        description="Microplastic particles",
        meaning=ENVO["01000944"])
    PHARMACEUTICALS = PermissibleValue(
        text="PHARMACEUTICALS",
        title="pharmaceutical",
        description="Pharmaceutical residues",
        meaning=CHEBI["52217"])
    PESTICIDES = PermissibleValue(
        text="PESTICIDES",
        title="pesticide",
        description="Pesticide residues",
        meaning=CHEBI["25944"])

    _defn = EnumDefinition(
        name="WaterContaminantEnum",
        description="Common water contaminants",
    )

class EndocrineDisruptorEnum(EnumDefinitionImpl):
    """
    Common endocrine disrupting chemicals
    """
    BPA = PermissibleValue(
        text="BPA",
        title="bisphenol A",
        description="Bisphenol A",
        meaning=CHEBI["33216"])
    PHTHALATES = PermissibleValue(
        text="PHTHALATES",
        title="phthalate",
        description="Phthalates",
        meaning=CHEBI["26092"])
    PFAS = PermissibleValue(
        text="PFAS",
        title="perfluoroalkyl substance",
        description="Per- and polyfluoroalkyl substances",
        meaning=CHEBI["172397"])
    PCB = PermissibleValue(
        text="PCB",
        title="polychlorobiphenyl",
        description="Polychlorinated biphenyls",
        meaning=CHEBI["53156"])
    DIOXINS = PermissibleValue(
        text="DIOXINS",
        title="Dioxin Compound",
        description="Dioxins",
        meaning=NCIT["C442"])
    DDT = PermissibleValue(
        text="DDT",
        description="Dichlorodiphenyltrichloroethane and metabolites",
        meaning=CHEBI["16130"])
    PARABENS = PermissibleValue(
        text="PARABENS",
        title="paraben",
        description="Parabens",
        meaning=CHEBI["85122"])
    TRICLOSAN = PermissibleValue(
        text="TRICLOSAN",
        description="Triclosan",
        meaning=CHEBI["164200"])
    FLAME_RETARDANTS = PermissibleValue(
        text="FLAME_RETARDANTS",
        title="brominated flame retardant",
        description="Brominated flame retardants",
        meaning=CHEBI["172368"])

    _defn = EnumDefinition(
        name="EndocrineDisruptorEnum",
        description="Common endocrine disrupting chemicals",
    )

class ExposureDurationEnum(EnumDefinitionImpl):
    """
    Duration categories for environmental exposures
    """
    ACUTE = PermissibleValue(
        text="ACUTE",
        description="Single or short-term exposure (hours to days)")
    SUBACUTE = PermissibleValue(
        text="SUBACUTE",
        description="Repeated exposure over weeks")
    SUBCHRONIC = PermissibleValue(
        text="SUBCHRONIC",
        description="Repeated exposure over months")
    CHRONIC = PermissibleValue(
        text="CHRONIC",
        description="Long-term exposure over years")
    LIFETIME = PermissibleValue(
        text="LIFETIME",
        description="Exposure over entire lifetime")
    PRENATAL = PermissibleValue(
        text="PRENATAL",
        description="Exposure during pregnancy")
    POSTNATAL = PermissibleValue(
        text="POSTNATAL",
        description="Exposure after birth")
    DEVELOPMENTAL = PermissibleValue(
        text="DEVELOPMENTAL",
        description="Exposure during critical developmental periods")

    _defn = EnumDefinition(
        name="ExposureDurationEnum",
        description="Duration categories for environmental exposures",
    )

class CountryCodeISO2Enum(EnumDefinitionImpl):
    """
    ISO 3166-1 alpha-2 country codes (2-letter codes)
    """
    US = PermissibleValue(
        text="US",
        description="United States of America",
        meaning=ISO3166LOC["us"])
    CA = PermissibleValue(
        text="CA",
        description="Canada",
        meaning=ISO3166LOC["ca"])
    MX = PermissibleValue(
        text="MX",
        description="Mexico",
        meaning=ISO3166LOC["mx"])
    GB = PermissibleValue(
        text="GB",
        description="United Kingdom",
        meaning=ISO3166LOC["gb"])
    FR = PermissibleValue(
        text="FR",
        description="France",
        meaning=ISO3166LOC["fr"])
    DE = PermissibleValue(
        text="DE",
        description="Germany",
        meaning=ISO3166LOC["de"])
    IT = PermissibleValue(
        text="IT",
        description="Italy",
        meaning=ISO3166LOC["it"])
    ES = PermissibleValue(
        text="ES",
        description="Spain",
        meaning=ISO3166LOC["es"])
    PT = PermissibleValue(
        text="PT",
        description="Portugal",
        meaning=ISO3166LOC["pt"])
    NL = PermissibleValue(
        text="NL",
        description="Netherlands",
        meaning=ISO3166LOC["nl"])
    BE = PermissibleValue(
        text="BE",
        description="Belgium",
        meaning=ISO3166LOC["be"])
    CH = PermissibleValue(
        text="CH",
        description="Switzerland",
        meaning=ISO3166LOC["ch"])
    AT = PermissibleValue(
        text="AT",
        description="Austria",
        meaning=ISO3166LOC["at"])
    SE = PermissibleValue(
        text="SE",
        description="Sweden",
        meaning=ISO3166LOC["se"])
    DK = PermissibleValue(
        text="DK",
        description="Denmark",
        meaning=ISO3166LOC["dk"])
    FI = PermissibleValue(
        text="FI",
        description="Finland",
        meaning=ISO3166LOC["fi"])
    PL = PermissibleValue(
        text="PL",
        description="Poland",
        meaning=ISO3166LOC["pl"])
    RU = PermissibleValue(
        text="RU",
        description="Russian Federation",
        meaning=ISO3166LOC["ru"])
    UA = PermissibleValue(
        text="UA",
        description="Ukraine",
        meaning=ISO3166LOC["ua"])
    CN = PermissibleValue(
        text="CN",
        description="China",
        meaning=ISO3166LOC["cn"])
    JP = PermissibleValue(
        text="JP",
        description="Japan",
        meaning=ISO3166LOC["jp"])
    KR = PermissibleValue(
        text="KR",
        description="South Korea",
        meaning=ISO3166LOC["kr"])
    IN = PermissibleValue(
        text="IN",
        description="India",
        meaning=ISO3166LOC["in"])
    AU = PermissibleValue(
        text="AU",
        description="Australia",
        meaning=ISO3166LOC["au"])
    NZ = PermissibleValue(
        text="NZ",
        description="New Zealand",
        meaning=ISO3166LOC["nz"])
    BR = PermissibleValue(
        text="BR",
        description="Brazil",
        meaning=ISO3166LOC["br"])
    AR = PermissibleValue(
        text="AR",
        description="Argentina",
        meaning=ISO3166LOC["ar"])
    CL = PermissibleValue(
        text="CL",
        description="Chile",
        meaning=ISO3166LOC["cl"])
    CO = PermissibleValue(
        text="CO",
        description="Colombia",
        meaning=ISO3166LOC["co"])
    PE = PermissibleValue(
        text="PE",
        description="Peru",
        meaning=ISO3166LOC["pe"])
    VE = PermissibleValue(
        text="VE",
        description="Venezuela",
        meaning=ISO3166LOC["ve"])
    ZA = PermissibleValue(
        text="ZA",
        description="South Africa",
        meaning=ISO3166LOC["za"])
    EG = PermissibleValue(
        text="EG",
        description="Egypt",
        meaning=ISO3166LOC["eg"])
    NG = PermissibleValue(
        text="NG",
        description="Nigeria",
        meaning=ISO3166LOC["ng"])
    KE = PermissibleValue(
        text="KE",
        description="Kenya",
        meaning=ISO3166LOC["ke"])
    IL = PermissibleValue(
        text="IL",
        description="Israel",
        meaning=ISO3166LOC["il"])
    SA = PermissibleValue(
        text="SA",
        description="Saudi Arabia",
        meaning=ISO3166LOC["sa"])
    AE = PermissibleValue(
        text="AE",
        description="United Arab Emirates",
        meaning=ISO3166LOC["ae"])
    TR = PermissibleValue(
        text="TR",
        description="Turkey",
        meaning=ISO3166LOC["tr"])
    GR = PermissibleValue(
        text="GR",
        description="Greece",
        meaning=ISO3166LOC["gr"])
    IE = PermissibleValue(
        text="IE",
        description="Ireland",
        meaning=ISO3166LOC["ie"])
    SG = PermissibleValue(
        text="SG",
        description="Singapore",
        meaning=ISO3166LOC["sg"])
    MY = PermissibleValue(
        text="MY",
        description="Malaysia",
        meaning=ISO3166LOC["my"])
    TH = PermissibleValue(
        text="TH",
        description="Thailand",
        meaning=ISO3166LOC["th"])
    ID = PermissibleValue(
        text="ID",
        description="Indonesia",
        meaning=ISO3166LOC["id"])
    PH = PermissibleValue(
        text="PH",
        description="Philippines",
        meaning=ISO3166LOC["ph"])
    VN = PermissibleValue(
        text="VN",
        description="Vietnam",
        meaning=ISO3166LOC["vn"])
    PK = PermissibleValue(
        text="PK",
        description="Pakistan",
        meaning=ISO3166LOC["pk"])
    BD = PermissibleValue(
        text="BD",
        description="Bangladesh",
        meaning=ISO3166LOC["bd"])

    _defn = EnumDefinition(
        name="CountryCodeISO2Enum",
        description="ISO 3166-1 alpha-2 country codes (2-letter codes)",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "False",
            PermissibleValue(
                text="False",
                description="Norway",
                meaning=ISO3166LOC["no"]))

class CountryCodeISO3Enum(EnumDefinitionImpl):
    """
    ISO 3166-1 alpha-3 country codes (3-letter codes)
    """
    USA = PermissibleValue(
        text="USA",
        description="United States of America",
        meaning=ISO3166LOC["us"])
    CAN = PermissibleValue(
        text="CAN",
        description="Canada",
        meaning=ISO3166LOC["ca"])
    MEX = PermissibleValue(
        text="MEX",
        description="Mexico",
        meaning=ISO3166LOC["mx"])
    GBR = PermissibleValue(
        text="GBR",
        description="United Kingdom",
        meaning=ISO3166LOC["gb"])
    FRA = PermissibleValue(
        text="FRA",
        description="France",
        meaning=ISO3166LOC["fr"])
    DEU = PermissibleValue(
        text="DEU",
        description="Germany",
        meaning=ISO3166LOC["de"])
    ITA = PermissibleValue(
        text="ITA",
        description="Italy",
        meaning=ISO3166LOC["it"])
    ESP = PermissibleValue(
        text="ESP",
        description="Spain",
        meaning=ISO3166LOC["es"])
    PRT = PermissibleValue(
        text="PRT",
        description="Portugal",
        meaning=ISO3166LOC["pt"])
    NLD = PermissibleValue(
        text="NLD",
        description="Netherlands",
        meaning=ISO3166LOC["nl"])
    BEL = PermissibleValue(
        text="BEL",
        description="Belgium",
        meaning=ISO3166LOC["be"])
    CHE = PermissibleValue(
        text="CHE",
        description="Switzerland",
        meaning=ISO3166LOC["ch"])
    AUT = PermissibleValue(
        text="AUT",
        description="Austria",
        meaning=ISO3166LOC["at"])
    SWE = PermissibleValue(
        text="SWE",
        description="Sweden",
        meaning=ISO3166LOC["se"])
    NOR = PermissibleValue(
        text="NOR",
        description="Norway",
        meaning=ISO3166LOC["no"])
    DNK = PermissibleValue(
        text="DNK",
        description="Denmark",
        meaning=ISO3166LOC["dk"])
    FIN = PermissibleValue(
        text="FIN",
        description="Finland",
        meaning=ISO3166LOC["fi"])
    POL = PermissibleValue(
        text="POL",
        description="Poland",
        meaning=ISO3166LOC["pl"])
    RUS = PermissibleValue(
        text="RUS",
        description="Russian Federation",
        meaning=ISO3166LOC["ru"])
    UKR = PermissibleValue(
        text="UKR",
        description="Ukraine",
        meaning=ISO3166LOC["ua"])
    CHN = PermissibleValue(
        text="CHN",
        description="China",
        meaning=ISO3166LOC["cn"])
    JPN = PermissibleValue(
        text="JPN",
        description="Japan",
        meaning=ISO3166LOC["jp"])
    KOR = PermissibleValue(
        text="KOR",
        description="South Korea",
        meaning=ISO3166LOC["kr"])
    IND = PermissibleValue(
        text="IND",
        description="India",
        meaning=ISO3166LOC["in"])
    AUS = PermissibleValue(
        text="AUS",
        description="Australia",
        meaning=ISO3166LOC["au"])
    NZL = PermissibleValue(
        text="NZL",
        description="New Zealand",
        meaning=ISO3166LOC["nz"])
    BRA = PermissibleValue(
        text="BRA",
        description="Brazil",
        meaning=ISO3166LOC["br"])
    ARG = PermissibleValue(
        text="ARG",
        description="Argentina",
        meaning=ISO3166LOC["ar"])
    CHL = PermissibleValue(
        text="CHL",
        description="Chile",
        meaning=ISO3166LOC["cl"])
    COL = PermissibleValue(
        text="COL",
        description="Colombia",
        meaning=ISO3166LOC["co"])

    _defn = EnumDefinition(
        name="CountryCodeISO3Enum",
        description="ISO 3166-1 alpha-3 country codes (3-letter codes)",
    )

class USStateCodeEnum(EnumDefinitionImpl):
    """
    United States state and territory codes
    """
    AL = PermissibleValue(
        text="AL",
        description="Alabama")
    AK = PermissibleValue(
        text="AK",
        description="Alaska")
    AZ = PermissibleValue(
        text="AZ",
        description="Arizona")
    AR = PermissibleValue(
        text="AR",
        description="Arkansas")
    CA = PermissibleValue(
        text="CA",
        description="California")
    CO = PermissibleValue(
        text="CO",
        description="Colorado")
    CT = PermissibleValue(
        text="CT",
        description="Connecticut")
    DE = PermissibleValue(
        text="DE",
        description="Delaware")
    FL = PermissibleValue(
        text="FL",
        description="Florida")
    GA = PermissibleValue(
        text="GA",
        description="Georgia")
    HI = PermissibleValue(
        text="HI",
        description="Hawaii")
    ID = PermissibleValue(
        text="ID",
        description="Idaho")
    IL = PermissibleValue(
        text="IL",
        description="Illinois")
    IN = PermissibleValue(
        text="IN",
        description="Indiana")
    IA = PermissibleValue(
        text="IA",
        description="Iowa")
    KS = PermissibleValue(
        text="KS",
        description="Kansas")
    KY = PermissibleValue(
        text="KY",
        description="Kentucky")
    LA = PermissibleValue(
        text="LA",
        description="Louisiana")
    ME = PermissibleValue(
        text="ME",
        description="Maine")
    MD = PermissibleValue(
        text="MD",
        description="Maryland")
    MA = PermissibleValue(
        text="MA",
        description="Massachusetts")
    MI = PermissibleValue(
        text="MI",
        description="Michigan")
    MN = PermissibleValue(
        text="MN",
        description="Minnesota")
    MS = PermissibleValue(
        text="MS",
        description="Mississippi")
    MO = PermissibleValue(
        text="MO",
        description="Missouri")
    MT = PermissibleValue(
        text="MT",
        description="Montana")
    NE = PermissibleValue(
        text="NE",
        description="Nebraska")
    NV = PermissibleValue(
        text="NV",
        description="Nevada")
    NH = PermissibleValue(
        text="NH",
        description="New Hampshire")
    NJ = PermissibleValue(
        text="NJ",
        description="New Jersey")
    NM = PermissibleValue(
        text="NM",
        description="New Mexico")
    NY = PermissibleValue(
        text="NY",
        description="New York")
    NC = PermissibleValue(
        text="NC",
        description="North Carolina")
    ND = PermissibleValue(
        text="ND",
        description="North Dakota")
    OH = PermissibleValue(
        text="OH",
        description="Ohio")
    OK = PermissibleValue(
        text="OK",
        description="Oklahoma")
    OR = PermissibleValue(
        text="OR",
        description="Oregon")
    PA = PermissibleValue(
        text="PA",
        description="Pennsylvania")
    RI = PermissibleValue(
        text="RI",
        description="Rhode Island")
    SC = PermissibleValue(
        text="SC",
        description="South Carolina")
    SD = PermissibleValue(
        text="SD",
        description="South Dakota")
    TN = PermissibleValue(
        text="TN",
        description="Tennessee")
    TX = PermissibleValue(
        text="TX",
        description="Texas")
    UT = PermissibleValue(
        text="UT",
        description="Utah")
    VT = PermissibleValue(
        text="VT",
        description="Vermont")
    VA = PermissibleValue(
        text="VA",
        description="Virginia")
    WA = PermissibleValue(
        text="WA",
        description="Washington")
    WV = PermissibleValue(
        text="WV",
        description="West Virginia")
    WI = PermissibleValue(
        text="WI",
        description="Wisconsin")
    WY = PermissibleValue(
        text="WY",
        description="Wyoming")
    DC = PermissibleValue(
        text="DC",
        description="District of Columbia")
    PR = PermissibleValue(
        text="PR",
        description="Puerto Rico")
    VI = PermissibleValue(
        text="VI",
        description="U.S. Virgin Islands")
    GU = PermissibleValue(
        text="GU",
        description="Guam")
    AS = PermissibleValue(
        text="AS",
        description="American Samoa")
    MP = PermissibleValue(
        text="MP",
        description="Northern Mariana Islands")

    _defn = EnumDefinition(
        name="USStateCodeEnum",
        description="United States state and territory codes",
    )

class CanadianProvinceCodeEnum(EnumDefinitionImpl):
    """
    Canadian province and territory codes
    """
    AB = PermissibleValue(
        text="AB",
        description="Alberta")
    BC = PermissibleValue(
        text="BC",
        description="British Columbia")
    MB = PermissibleValue(
        text="MB",
        description="Manitoba")
    NB = PermissibleValue(
        text="NB",
        description="New Brunswick")
    NL = PermissibleValue(
        text="NL",
        description="Newfoundland and Labrador")
    NS = PermissibleValue(
        text="NS",
        description="Nova Scotia")
    NT = PermissibleValue(
        text="NT",
        description="Northwest Territories")
    NU = PermissibleValue(
        text="NU",
        description="Nunavut")
    PE = PermissibleValue(
        text="PE",
        description="Prince Edward Island")
    QC = PermissibleValue(
        text="QC",
        description="Quebec")
    SK = PermissibleValue(
        text="SK",
        description="Saskatchewan")
    YT = PermissibleValue(
        text="YT",
        description="Yukon")

    _defn = EnumDefinition(
        name="CanadianProvinceCodeEnum",
        description="Canadian province and territory codes",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "True",
            PermissibleValue(
                text="True",
                description="Ontario"))

class CompassDirection(EnumDefinitionImpl):
    """
    Cardinal and intercardinal compass directions
    """
    NORTH = PermissibleValue(
        text="NORTH",
        description="North (0°/360°)")
    EAST = PermissibleValue(
        text="EAST",
        description="East (90°)")
    SOUTH = PermissibleValue(
        text="SOUTH",
        description="South (180°)")
    WEST = PermissibleValue(
        text="WEST",
        description="West (270°)")
    NORTHEAST = PermissibleValue(
        text="NORTHEAST",
        description="Northeast (45°)")
    SOUTHEAST = PermissibleValue(
        text="SOUTHEAST",
        description="Southeast (135°)")
    SOUTHWEST = PermissibleValue(
        text="SOUTHWEST",
        description="Southwest (225°)")
    NORTHWEST = PermissibleValue(
        text="NORTHWEST",
        description="Northwest (315°)")
    NORTH_NORTHEAST = PermissibleValue(
        text="NORTH_NORTHEAST",
        description="North-northeast (22.5°)")
    EAST_NORTHEAST = PermissibleValue(
        text="EAST_NORTHEAST",
        description="East-northeast (67.5°)")
    EAST_SOUTHEAST = PermissibleValue(
        text="EAST_SOUTHEAST",
        description="East-southeast (112.5°)")
    SOUTH_SOUTHEAST = PermissibleValue(
        text="SOUTH_SOUTHEAST",
        description="South-southeast (157.5°)")
    SOUTH_SOUTHWEST = PermissibleValue(
        text="SOUTH_SOUTHWEST",
        description="South-southwest (202.5°)")
    WEST_SOUTHWEST = PermissibleValue(
        text="WEST_SOUTHWEST",
        description="West-southwest (247.5°)")
    WEST_NORTHWEST = PermissibleValue(
        text="WEST_NORTHWEST",
        description="West-northwest (292.5°)")
    NORTH_NORTHWEST = PermissibleValue(
        text="NORTH_NORTHWEST",
        description="North-northwest (337.5°)")

    _defn = EnumDefinition(
        name="CompassDirection",
        description="Cardinal and intercardinal compass directions",
    )

class RelativeDirection(EnumDefinitionImpl):
    """
    Relative directional terms
    """
    FORWARD = PermissibleValue(
        text="FORWARD",
        description="Forward/Ahead")
    BACKWARD = PermissibleValue(
        text="BACKWARD",
        description="Backward/Behind")
    LEFT = PermissibleValue(
        text="LEFT",
        description="Left")
    RIGHT = PermissibleValue(
        text="RIGHT",
        description="Right")
    UP = PermissibleValue(
        text="UP",
        description="Up/Above")
    DOWN = PermissibleValue(
        text="DOWN",
        description="Down/Below")
    INWARD = PermissibleValue(
        text="INWARD",
        description="Inward/Toward center")
    OUTWARD = PermissibleValue(
        text="OUTWARD",
        description="Outward/Away from center")
    CLOCKWISE = PermissibleValue(
        text="CLOCKWISE",
        description="Clockwise rotation")
    COUNTERCLOCKWISE = PermissibleValue(
        text="COUNTERCLOCKWISE",
        description="Counterclockwise rotation")

    _defn = EnumDefinition(
        name="RelativeDirection",
        description="Relative directional terms",
    )

class WindDirection(EnumDefinitionImpl):
    """
    Wind direction nomenclature (named for where wind comes FROM)
    """
    NORTHERLY = PermissibleValue(
        text="NORTHERLY",
        description="Wind from the north")
    NORTHEASTERLY = PermissibleValue(
        text="NORTHEASTERLY",
        description="Wind from the northeast")
    EASTERLY = PermissibleValue(
        text="EASTERLY",
        description="Wind from the east")
    SOUTHEASTERLY = PermissibleValue(
        text="SOUTHEASTERLY",
        description="Wind from the southeast")
    SOUTHERLY = PermissibleValue(
        text="SOUTHERLY",
        description="Wind from the south")
    SOUTHWESTERLY = PermissibleValue(
        text="SOUTHWESTERLY",
        description="Wind from the southwest")
    WESTERLY = PermissibleValue(
        text="WESTERLY",
        description="Wind from the west")
    NORTHWESTERLY = PermissibleValue(
        text="NORTHWESTERLY",
        description="Wind from the northwest")
    VARIABLE = PermissibleValue(
        text="VARIABLE",
        description="Variable wind direction")

    _defn = EnumDefinition(
        name="WindDirection",
        description="Wind direction nomenclature (named for where wind comes FROM)",
    )

class ContinentEnum(EnumDefinitionImpl):
    """
    Continental regions
    """
    AFRICA = PermissibleValue(
        text="AFRICA",
        description="Africa")
    ANTARCTICA = PermissibleValue(
        text="ANTARCTICA",
        description="Antarctica")
    ASIA = PermissibleValue(
        text="ASIA",
        description="Asia")
    EUROPE = PermissibleValue(
        text="EUROPE",
        description="Europe")
    NORTH_AMERICA = PermissibleValue(
        text="NORTH_AMERICA",
        description="North America")
    OCEANIA = PermissibleValue(
        text="OCEANIA",
        description="Oceania (including Australia)")
    SOUTH_AMERICA = PermissibleValue(
        text="SOUTH_AMERICA",
        description="South America")

    _defn = EnumDefinition(
        name="ContinentEnum",
        description="Continental regions",
    )

class UNRegionEnum(EnumDefinitionImpl):
    """
    United Nations regional classifications
    """
    EASTERN_AFRICA = PermissibleValue(
        text="EASTERN_AFRICA",
        description="Eastern Africa")
    MIDDLE_AFRICA = PermissibleValue(
        text="MIDDLE_AFRICA",
        description="Middle Africa")
    NORTHERN_AFRICA = PermissibleValue(
        text="NORTHERN_AFRICA",
        description="Northern Africa")
    SOUTHERN_AFRICA = PermissibleValue(
        text="SOUTHERN_AFRICA",
        description="Southern Africa")
    WESTERN_AFRICA = PermissibleValue(
        text="WESTERN_AFRICA",
        description="Western Africa")
    CARIBBEAN = PermissibleValue(
        text="CARIBBEAN",
        description="Caribbean")
    CENTRAL_AMERICA = PermissibleValue(
        text="CENTRAL_AMERICA",
        description="Central America")
    NORTHERN_AMERICA = PermissibleValue(
        text="NORTHERN_AMERICA",
        description="Northern America")
    SOUTH_AMERICA = PermissibleValue(
        text="SOUTH_AMERICA",
        description="South America")
    CENTRAL_ASIA = PermissibleValue(
        text="CENTRAL_ASIA",
        description="Central Asia")
    EASTERN_ASIA = PermissibleValue(
        text="EASTERN_ASIA",
        description="Eastern Asia")
    SOUTHERN_ASIA = PermissibleValue(
        text="SOUTHERN_ASIA",
        description="Southern Asia")
    SOUTH_EASTERN_ASIA = PermissibleValue(
        text="SOUTH_EASTERN_ASIA",
        description="South-Eastern Asia")
    WESTERN_ASIA = PermissibleValue(
        text="WESTERN_ASIA",
        description="Western Asia")
    EASTERN_EUROPE = PermissibleValue(
        text="EASTERN_EUROPE",
        description="Eastern Europe")
    NORTHERN_EUROPE = PermissibleValue(
        text="NORTHERN_EUROPE",
        description="Northern Europe")
    SOUTHERN_EUROPE = PermissibleValue(
        text="SOUTHERN_EUROPE",
        description="Southern Europe")
    WESTERN_EUROPE = PermissibleValue(
        text="WESTERN_EUROPE",
        description="Western Europe")
    AUSTRALIA_NEW_ZEALAND = PermissibleValue(
        text="AUSTRALIA_NEW_ZEALAND",
        description="Australia and New Zealand")
    MELANESIA = PermissibleValue(
        text="MELANESIA",
        description="Melanesia")
    MICRONESIA = PermissibleValue(
        text="MICRONESIA",
        description="Micronesia")
    POLYNESIA = PermissibleValue(
        text="POLYNESIA",
        description="Polynesia")

    _defn = EnumDefinition(
        name="UNRegionEnum",
        description="United Nations regional classifications",
    )

class LanguageCodeISO6391Enum(EnumDefinitionImpl):
    """
    ISO 639-1 two-letter language codes
    """
    EN = PermissibleValue(
        text="EN",
        description="English")
    ES = PermissibleValue(
        text="ES",
        description="Spanish")
    FR = PermissibleValue(
        text="FR",
        description="French")
    DE = PermissibleValue(
        text="DE",
        description="German")
    IT = PermissibleValue(
        text="IT",
        description="Italian")
    PT = PermissibleValue(
        text="PT",
        description="Portuguese")
    RU = PermissibleValue(
        text="RU",
        description="Russian")
    ZH = PermissibleValue(
        text="ZH",
        description="Chinese")
    JA = PermissibleValue(
        text="JA",
        description="Japanese")
    KO = PermissibleValue(
        text="KO",
        description="Korean")
    AR = PermissibleValue(
        text="AR",
        description="Arabic")
    HI = PermissibleValue(
        text="HI",
        description="Hindi")
    BN = PermissibleValue(
        text="BN",
        description="Bengali")
    PA = PermissibleValue(
        text="PA",
        description="Punjabi")
    UR = PermissibleValue(
        text="UR",
        description="Urdu")
    NL = PermissibleValue(
        text="NL",
        description="Dutch")
    PL = PermissibleValue(
        text="PL",
        description="Polish")
    TR = PermissibleValue(
        text="TR",
        description="Turkish")
    VI = PermissibleValue(
        text="VI",
        description="Vietnamese")
    TH = PermissibleValue(
        text="TH",
        description="Thai")
    SV = PermissibleValue(
        text="SV",
        description="Swedish")
    DA = PermissibleValue(
        text="DA",
        description="Danish")
    FI = PermissibleValue(
        text="FI",
        description="Finnish")
    EL = PermissibleValue(
        text="EL",
        description="Greek")
    HE = PermissibleValue(
        text="HE",
        description="Hebrew")
    CS = PermissibleValue(
        text="CS",
        description="Czech")
    HU = PermissibleValue(
        text="HU",
        description="Hungarian")
    RO = PermissibleValue(
        text="RO",
        description="Romanian")
    UK = PermissibleValue(
        text="UK",
        description="Ukrainian")

    _defn = EnumDefinition(
        name="LanguageCodeISO6391Enum",
        description="ISO 639-1 two-letter language codes",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "False",
            PermissibleValue(
                text="False",
                description="Norwegian"))

class TimeZoneEnum(EnumDefinitionImpl):
    """
    Common time zones
    """
    UTC = PermissibleValue(
        text="UTC",
        description="Coordinated Universal Time")
    EST = PermissibleValue(
        text="EST",
        description="Eastern Standard Time (UTC-5)")
    EDT = PermissibleValue(
        text="EDT",
        description="Eastern Daylight Time (UTC-4)")
    CST = PermissibleValue(
        text="CST",
        description="Central Standard Time (UTC-6)")
    CDT = PermissibleValue(
        text="CDT",
        description="Central Daylight Time (UTC-5)")
    MST = PermissibleValue(
        text="MST",
        description="Mountain Standard Time (UTC-7)")
    MDT = PermissibleValue(
        text="MDT",
        description="Mountain Daylight Time (UTC-6)")
    PST = PermissibleValue(
        text="PST",
        description="Pacific Standard Time (UTC-8)")
    PDT = PermissibleValue(
        text="PDT",
        description="Pacific Daylight Time (UTC-7)")
    GMT = PermissibleValue(
        text="GMT",
        description="Greenwich Mean Time (UTC+0)")
    BST = PermissibleValue(
        text="BST",
        description="British Summer Time (UTC+1)")
    CET = PermissibleValue(
        text="CET",
        description="Central European Time (UTC+1)")
    CEST = PermissibleValue(
        text="CEST",
        description="Central European Summer Time (UTC+2)")
    EET = PermissibleValue(
        text="EET",
        description="Eastern European Time (UTC+2)")
    EEST = PermissibleValue(
        text="EEST",
        description="Eastern European Summer Time (UTC+3)")
    JST = PermissibleValue(
        text="JST",
        description="Japan Standard Time (UTC+9)")
    CST_CHINA = PermissibleValue(
        text="CST_CHINA",
        description="China Standard Time (UTC+8)")
    IST = PermissibleValue(
        text="IST",
        description="India Standard Time (UTC+5:30)")
    AEST = PermissibleValue(
        text="AEST",
        description="Australian Eastern Standard Time (UTC+10)")
    AEDT = PermissibleValue(
        text="AEDT",
        description="Australian Eastern Daylight Time (UTC+11)")
    NZST = PermissibleValue(
        text="NZST",
        description="New Zealand Standard Time (UTC+12)")
    NZDT = PermissibleValue(
        text="NZDT",
        description="New Zealand Daylight Time (UTC+13)")

    _defn = EnumDefinition(
        name="TimeZoneEnum",
        description="Common time zones",
    )

class CurrencyCodeISO4217Enum(EnumDefinitionImpl):
    """
    ISO 4217 currency codes
    """
    USD = PermissibleValue(
        text="USD",
        description="United States Dollar")
    EUR = PermissibleValue(
        text="EUR",
        description="Euro")
    GBP = PermissibleValue(
        text="GBP",
        description="British Pound Sterling")
    JPY = PermissibleValue(
        text="JPY",
        description="Japanese Yen")
    CNY = PermissibleValue(
        text="CNY",
        description="Chinese Yuan Renminbi")
    CHF = PermissibleValue(
        text="CHF",
        description="Swiss Franc")
    CAD = PermissibleValue(
        text="CAD",
        description="Canadian Dollar")
    AUD = PermissibleValue(
        text="AUD",
        description="Australian Dollar")
    NZD = PermissibleValue(
        text="NZD",
        description="New Zealand Dollar")
    SEK = PermissibleValue(
        text="SEK",
        description="Swedish Krona")
    NOK = PermissibleValue(
        text="NOK",
        description="Norwegian Krone")
    DKK = PermissibleValue(
        text="DKK",
        description="Danish Krone")
    PLN = PermissibleValue(
        text="PLN",
        description="Polish Zloty")
    RUB = PermissibleValue(
        text="RUB",
        description="Russian Ruble")
    INR = PermissibleValue(
        text="INR",
        description="Indian Rupee")
    BRL = PermissibleValue(
        text="BRL",
        description="Brazilian Real")
    MXN = PermissibleValue(
        text="MXN",
        description="Mexican Peso")
    ZAR = PermissibleValue(
        text="ZAR",
        description="South African Rand")
    KRW = PermissibleValue(
        text="KRW",
        description="South Korean Won")
    SGD = PermissibleValue(
        text="SGD",
        description="Singapore Dollar")
    HKD = PermissibleValue(
        text="HKD",
        description="Hong Kong Dollar")
    TWD = PermissibleValue(
        text="TWD",
        description="Taiwan Dollar")
    THB = PermissibleValue(
        text="THB",
        description="Thai Baht")
    MYR = PermissibleValue(
        text="MYR",
        description="Malaysian Ringgit")
    IDR = PermissibleValue(
        text="IDR",
        description="Indonesian Rupiah")
    PHP = PermissibleValue(
        text="PHP",
        description="Philippine Peso")
    VND = PermissibleValue(
        text="VND",
        description="Vietnamese Dong")
    TRY = PermissibleValue(
        text="TRY",
        description="Turkish Lira")
    AED = PermissibleValue(
        text="AED",
        description="UAE Dirham")
    SAR = PermissibleValue(
        text="SAR",
        description="Saudi Riyal")
    ILS = PermissibleValue(
        text="ILS",
        description="Israeli Shekel")
    EGP = PermissibleValue(
        text="EGP",
        description="Egyptian Pound")

    _defn = EnumDefinition(
        name="CurrencyCodeISO4217Enum",
        description="ISO 4217 currency codes",
    )

class SentimentClassificationEnum(EnumDefinitionImpl):
    """
    Standard labels for sentiment analysis classification tasks
    """
    POSITIVE = PermissibleValue(
        text="POSITIVE",
        title="Positive Finding",
        description="Positive sentiment or opinion",
        meaning=NCIT["C38758"])
    NEGATIVE = PermissibleValue(
        text="NEGATIVE",
        title="Negative Test Result",
        description="Negative sentiment or opinion",
        meaning=NCIT["C35681"])
    NEUTRAL = PermissibleValue(
        text="NEUTRAL",
        title="Normal",
        description="Neutral sentiment, neither positive nor negative",
        meaning=NCIT["C14165"])

    _defn = EnumDefinition(
        name="SentimentClassificationEnum",
        description="Standard labels for sentiment analysis classification tasks",
    )

class FineSentimentClassificationEnum(EnumDefinitionImpl):
    """
    Fine-grained sentiment analysis labels with intensity levels
    """
    VERY_POSITIVE = PermissibleValue(
        text="VERY_POSITIVE",
        title="Positive Finding",
        description="Strongly positive sentiment",
        meaning=NCIT["C38758"])
    POSITIVE = PermissibleValue(
        text="POSITIVE",
        title="Positive Finding",
        description="Positive sentiment",
        meaning=NCIT["C38758"])
    NEUTRAL = PermissibleValue(
        text="NEUTRAL",
        title="Normal",
        description="Neutral sentiment",
        meaning=NCIT["C14165"])
    NEGATIVE = PermissibleValue(
        text="NEGATIVE",
        title="Negative Test Result",
        description="Negative sentiment",
        meaning=NCIT["C35681"])
    VERY_NEGATIVE = PermissibleValue(
        text="VERY_NEGATIVE",
        title="Negative Test Result",
        description="Strongly negative sentiment",
        meaning=NCIT["C35681"])

    _defn = EnumDefinition(
        name="FineSentimentClassificationEnum",
        description="Fine-grained sentiment analysis labels with intensity levels",
    )

class BinaryClassificationEnum(EnumDefinitionImpl):
    """
    Generic binary classification labels
    """
    POSITIVE = PermissibleValue(
        text="POSITIVE",
        title="Positive Finding",
        description="Positive class",
        meaning=NCIT["C38758"])
    NEGATIVE = PermissibleValue(
        text="NEGATIVE",
        title="Negative Test Result",
        description="Negative class",
        meaning=NCIT["C35681"])

    _defn = EnumDefinition(
        name="BinaryClassificationEnum",
        description="Generic binary classification labels",
    )

class SpamClassificationEnum(EnumDefinitionImpl):
    """
    Standard labels for spam/ham email classification
    """
    SPAM = PermissibleValue(
        text="SPAM",
        description="Unwanted or unsolicited message")
    HAM = PermissibleValue(
        text="HAM",
        description="Legitimate, wanted message")

    _defn = EnumDefinition(
        name="SpamClassificationEnum",
        description="Standard labels for spam/ham email classification",
    )

class AnomalyDetectionEnum(EnumDefinitionImpl):
    """
    Labels for anomaly detection tasks
    """
    NORMAL = PermissibleValue(
        text="NORMAL",
        title="Normal",
        description="Normal, expected behavior or pattern",
        meaning=NCIT["C14165"])
    ANOMALY = PermissibleValue(
        text="ANOMALY",
        title="Anomaly",
        description="Abnormal, unexpected behavior or pattern",
        meaning=STATO["0000036"])

    _defn = EnumDefinition(
        name="AnomalyDetectionEnum",
        description="Labels for anomaly detection tasks",
    )

class ChurnClassificationEnum(EnumDefinitionImpl):
    """
    Customer churn prediction labels
    """
    RETAINED = PermissibleValue(
        text="RETAINED",
        description="Customer continues using the service")
    CHURNED = PermissibleValue(
        text="CHURNED",
        description="Customer stopped using the service")

    _defn = EnumDefinition(
        name="ChurnClassificationEnum",
        description="Customer churn prediction labels",
    )

class FraudDetectionEnum(EnumDefinitionImpl):
    """
    Fraud detection classification labels
    """
    LEGITIMATE = PermissibleValue(
        text="LEGITIMATE",
        title="Normal",
        description="Legitimate, non-fraudulent transaction or activity",
        meaning=NCIT["C14165"])
    FRAUDULENT = PermissibleValue(
        text="FRAUDULENT",
        title="Fraudulently Obtained Product",
        description="Fraudulent transaction or activity",
        meaning=NCIT["C121839"])

    _defn = EnumDefinition(
        name="FraudDetectionEnum",
        description="Fraud detection classification labels",
    )

class QualityControlEnum(EnumDefinitionImpl):
    """
    Quality control classification labels
    """
    PASS = PermissibleValue(
        text="PASS",
        title="Pass",
        description="Item meets quality standards",
        meaning=NCIT["C81275"])
    FAIL = PermissibleValue(
        text="FAIL",
        title="Fail",
        description="Item does not meet quality standards",
        meaning=NCIT["C44281"])

    _defn = EnumDefinition(
        name="QualityControlEnum",
        description="Quality control classification labels",
    )

class DefectClassificationEnum(EnumDefinitionImpl):
    """
    Manufacturing defect classification
    """
    NO_DEFECT = PermissibleValue(
        text="NO_DEFECT",
        title="No Defect",
        description="No defect detected",
        meaning=NCIT["C14165"])
    MINOR_DEFECT = PermissibleValue(
        text="MINOR_DEFECT",
        title="Minor Defect",
        description="Minor defect that doesn't affect functionality")
    MAJOR_DEFECT = PermissibleValue(
        text="MAJOR_DEFECT",
        title="Major Defect",
        description="Major defect affecting functionality")
    CRITICAL_DEFECT = PermissibleValue(
        text="CRITICAL_DEFECT",
        title="Critical Defect",
        description="Critical defect rendering item unusable or unsafe")

    _defn = EnumDefinition(
        name="DefectClassificationEnum",
        description="Manufacturing defect classification",
    )

class BasicEmotionEnum(EnumDefinitionImpl):
    """
    Ekman's six basic emotions commonly used in emotion recognition
    """
    ANGER = PermissibleValue(
        text="ANGER",
        title="Anger",
        description="Feeling of displeasure or hostility",
        meaning=MFOEM["000009"])
    DISGUST = PermissibleValue(
        text="DISGUST",
        title="Disgust",
        description="Feeling of revulsion or strong disapproval",
        meaning=MFOEM["000019"])
    FEAR = PermissibleValue(
        text="FEAR",
        title="Fear",
        description="Feeling of anxiety or apprehension",
        meaning=MFOEM["000026"])
    HAPPINESS = PermissibleValue(
        text="HAPPINESS",
        title="Happiness",
        description="Feeling of pleasure or contentment",
        meaning=MFOEM["000042"])
    SADNESS = PermissibleValue(
        text="SADNESS",
        title="Sadness",
        description="Feeling of sorrow or unhappiness",
        meaning=MFOEM["000056"])
    SURPRISE = PermissibleValue(
        text="SURPRISE",
        title="Surprise",
        description="Feeling of mild astonishment or shock",
        meaning=MFOEM["000032"])

    _defn = EnumDefinition(
        name="BasicEmotionEnum",
        description="Ekman's six basic emotions commonly used in emotion recognition",
    )

class ExtendedEmotionEnum(EnumDefinitionImpl):
    """
    Extended emotion set including complex emotions
    """
    ANGER = PermissibleValue(
        text="ANGER",
        title="Anger",
        description="Feeling of displeasure or hostility",
        meaning=MFOEM["000009"])
    DISGUST = PermissibleValue(
        text="DISGUST",
        title="Disgust",
        description="Feeling of revulsion",
        meaning=MFOEM["000019"])
    FEAR = PermissibleValue(
        text="FEAR",
        title="Fear",
        description="Feeling of anxiety",
        meaning=MFOEM["000026"])
    HAPPINESS = PermissibleValue(
        text="HAPPINESS",
        title="Happiness",
        description="Feeling of pleasure",
        meaning=MFOEM["000042"])
    SADNESS = PermissibleValue(
        text="SADNESS",
        title="Sadness",
        description="Feeling of sorrow",
        meaning=MFOEM["000056"])
    SURPRISE = PermissibleValue(
        text="SURPRISE",
        title="Surprise",
        description="Feeling of astonishment",
        meaning=MFOEM["000032"])
    CONTEMPT = PermissibleValue(
        text="CONTEMPT",
        title="Contempt",
        description="Feeling that something is worthless",
        meaning=MFOEM["000018"])
    ANTICIPATION = PermissibleValue(
        text="ANTICIPATION",
        title="Erwartung",
        description="Feeling of excitement about something that will happen",
        meaning=MFOEM["000175"])
    TRUST = PermissibleValue(
        text="TRUST",
        title="Trust",
        description="Feeling of confidence in someone or something",
        meaning=MFOEM["000224"])
    LOVE = PermissibleValue(
        text="LOVE",
        title="Love",
        description="Feeling of deep affection",
        meaning=MFOEM["000048"])

    _defn = EnumDefinition(
        name="ExtendedEmotionEnum",
        description="Extended emotion set including complex emotions",
    )

class PriorityLevelEnum(EnumDefinitionImpl):
    """
    Standard priority levels for task/issue classification
    """
    CRITICAL = PermissibleValue(
        text="CRITICAL",
        title="Critical",
        description="Highest priority, requires immediate attention")
    HIGH = PermissibleValue(
        text="HIGH",
        title="High",
        description="High priority, should be addressed soon")
    MEDIUM = PermissibleValue(
        text="MEDIUM",
        title="Medium",
        description="Medium priority, normal workflow")
    LOW = PermissibleValue(
        text="LOW",
        title="Low",
        description="Low priority, can be deferred")
    TRIVIAL = PermissibleValue(
        text="TRIVIAL",
        title="Trivial",
        description="Lowest priority, nice to have")

    _defn = EnumDefinition(
        name="PriorityLevelEnum",
        description="Standard priority levels for task/issue classification",
    )

class SeverityLevelEnum(EnumDefinitionImpl):
    """
    Severity levels for incident/bug classification
    """
    CRITICAL = PermissibleValue(
        text="CRITICAL",
        title="Critical",
        description="System is unusable, data loss possible")
    MAJOR = PermissibleValue(
        text="MAJOR",
        title="Major",
        description="Major functionality impaired")
    MINOR = PermissibleValue(
        text="MINOR",
        title="Minor",
        description="Minor functionality impaired")
    TRIVIAL = PermissibleValue(
        text="TRIVIAL",
        title="Trivial",
        description="Cosmetic issue, minimal impact")

    _defn = EnumDefinition(
        name="SeverityLevelEnum",
        description="Severity levels for incident/bug classification",
    )

class ConfidenceLevelEnum(EnumDefinitionImpl):
    """
    Confidence levels for predictions and classifications
    """
    VERY_HIGH = PermissibleValue(
        text="VERY_HIGH",
        title="Very High",
        description="Very high confidence (>95%)")
    HIGH = PermissibleValue(
        text="HIGH",
        title="High",
        description="High confidence (80-95%)")
    MEDIUM = PermissibleValue(
        text="MEDIUM",
        title="Medium",
        description="Medium confidence (60-80%)")
    LOW = PermissibleValue(
        text="LOW",
        title="Low",
        description="Low confidence (40-60%)")
    VERY_LOW = PermissibleValue(
        text="VERY_LOW",
        title="Very Low",
        description="Very low confidence (<40%)")

    _defn = EnumDefinition(
        name="ConfidenceLevelEnum",
        description="Confidence levels for predictions and classifications",
    )

class NewsTopicCategoryEnum(EnumDefinitionImpl):
    """
    Common news article topic categories
    """
    POLITICS = PermissibleValue(
        text="POLITICS",
        title="Politics",
        description="Political news and government affairs")
    BUSINESS = PermissibleValue(
        text="BUSINESS",
        title="Business",
        description="Business, finance, and economic news")
    TECHNOLOGY = PermissibleValue(
        text="TECHNOLOGY",
        title="Technology",
        description="Technology and computing news")
    SPORTS = PermissibleValue(
        text="SPORTS",
        title="Sports",
        description="Sports news and events")
    ENTERTAINMENT = PermissibleValue(
        text="ENTERTAINMENT",
        title="Entertainment",
        description="Entertainment and celebrity news")
    SCIENCE = PermissibleValue(
        text="SCIENCE",
        title="Science",
        description="Scientific discoveries and research")
    HEALTH = PermissibleValue(
        text="HEALTH",
        title="Health",
        description="Health, medicine, and wellness news")
    WORLD = PermissibleValue(
        text="WORLD",
        title="World",
        description="International news and events")
    LOCAL = PermissibleValue(
        text="LOCAL",
        title="Local",
        description="Local and regional news")

    _defn = EnumDefinition(
        name="NewsTopicCategoryEnum",
        description="Common news article topic categories",
    )

class ToxicityClassificationEnum(EnumDefinitionImpl):
    """
    Text toxicity classification labels
    """
    NON_TOXIC = PermissibleValue(
        text="NON_TOXIC",
        title="Non-Toxic",
        description="Text is appropriate and non-harmful",
        meaning=SIO["001010"])
    TOXIC = PermissibleValue(
        text="TOXIC",
        title="Toxic",
        description="Text contains harmful or inappropriate content")
    SEVERE_TOXIC = PermissibleValue(
        text="SEVERE_TOXIC",
        title="Severe Toxic",
        description="Text contains severely harmful content")
    OBSCENE = PermissibleValue(
        text="OBSCENE",
        title="Obscene",
        description="Text contains obscene content")
    THREAT = PermissibleValue(
        text="THREAT",
        title="Threat",
        description="Text contains threatening content")
    INSULT = PermissibleValue(
        text="INSULT",
        title="Insult",
        description="Text contains insulting content")
    IDENTITY_HATE = PermissibleValue(
        text="IDENTITY_HATE",
        title="Identity Hate",
        description="Text contains identity-based hate")

    _defn = EnumDefinition(
        name="ToxicityClassificationEnum",
        description="Text toxicity classification labels",
    )

class IntentClassificationEnum(EnumDefinitionImpl):
    """
    Common chatbot/NLU intent categories
    """
    GREETING = PermissibleValue(
        text="GREETING",
        title="Greeting",
        description="User greeting or hello")
    GOODBYE = PermissibleValue(
        text="GOODBYE",
        title="Goodbye",
        description="User saying goodbye")
    THANKS = PermissibleValue(
        text="THANKS",
        title="Thanks",
        description="User expressing gratitude")
    HELP = PermissibleValue(
        text="HELP",
        title="Help",
        description="User requesting help or assistance")
    INFORMATION = PermissibleValue(
        text="INFORMATION",
        title="Information",
        description="User requesting information")
    COMPLAINT = PermissibleValue(
        text="COMPLAINT",
        title="Complaint",
        description="User expressing dissatisfaction")
    FEEDBACK = PermissibleValue(
        text="FEEDBACK",
        title="Feedback",
        description="User providing feedback")
    PURCHASE = PermissibleValue(
        text="PURCHASE",
        title="Purchase",
        description="User intent to buy or purchase")
    CANCEL = PermissibleValue(
        text="CANCEL",
        title="Cancel",
        description="User intent to cancel")
    REFUND = PermissibleValue(
        text="REFUND",
        title="Refund",
        description="User requesting refund")

    _defn = EnumDefinition(
        name="IntentClassificationEnum",
        description="Common chatbot/NLU intent categories",
    )

class SimpleSpatialDirection(EnumDefinitionImpl):
    """
    Basic spatial directional terms for general use
    """
    LEFT = PermissibleValue(
        text="LEFT",
        description="To the left side")
    RIGHT = PermissibleValue(
        text="RIGHT",
        description="To the right side")
    FORWARD = PermissibleValue(
        text="FORWARD",
        description="In the forward direction")
    BACKWARD = PermissibleValue(
        text="BACKWARD",
        description="In the backward direction")
    UP = PermissibleValue(
        text="UP",
        description="In the upward direction")
    DOWN = PermissibleValue(
        text="DOWN",
        description="In the downward direction")
    INWARD = PermissibleValue(
        text="INWARD",
        description="Toward the center or interior")
    OUTWARD = PermissibleValue(
        text="OUTWARD",
        description="Away from the center or exterior")
    TOP = PermissibleValue(
        text="TOP",
        description="At or toward the top")
    BOTTOM = PermissibleValue(
        text="BOTTOM",
        description="At or toward the bottom")
    MIDDLE = PermissibleValue(
        text="MIDDLE",
        description="At or toward the middle")

    _defn = EnumDefinition(
        name="SimpleSpatialDirection",
        description="Basic spatial directional terms for general use",
    )

class AnatomicalSide(EnumDefinitionImpl):
    """
    Anatomical sides as defined in the Biological Spatial Ontology (BSPO).
    An anatomical region bounded by a plane perpendicular to an axis through the middle.
    """
    LEFT = PermissibleValue(
        text="LEFT",
        title="Left side of a bilaterally symmetric organism",
        meaning=BSPO["0000000"])
    RIGHT = PermissibleValue(
        text="RIGHT",
        title="Right side of a bilaterally symmetric organism",
        meaning=BSPO["0000007"])
    ANTERIOR = PermissibleValue(
        text="ANTERIOR",
        title="Front/ventral side in most animals, toward the head",
        meaning=BSPO["0000055"])
    POSTERIOR = PermissibleValue(
        text="POSTERIOR",
        title="Back/dorsal side in most animals, toward the tail",
        meaning=BSPO["0000056"])
    DORSAL = PermissibleValue(
        text="DORSAL",
        title="Back side of organism (top in humans when standing)",
        meaning=BSPO["0000063"])
    VENTRAL = PermissibleValue(
        text="VENTRAL",
        title="Belly side of organism (front in humans when standing)",
        meaning=BSPO["0000068"])
    LATERAL = PermissibleValue(
        text="LATERAL",
        title="Away from the midline",
        meaning=BSPO["0000066"])
    MEDIAL = PermissibleValue(
        text="MEDIAL",
        title="Toward the midline",
        meaning=BSPO["0000067"])
    PROXIMAL = PermissibleValue(
        text="PROXIMAL",
        title="Closer to the point of attachment or origin",
        meaning=BSPO["0000061"])
    DISTAL = PermissibleValue(
        text="DISTAL",
        title="Further from the point of attachment or origin",
        meaning=BSPO["0000062"])
    APICAL = PermissibleValue(
        text="APICAL",
        title="At or toward the apex or tip",
        meaning=BSPO["0000057"])
    BASAL = PermissibleValue(
        text="BASAL",
        title="At or toward the base",
        meaning=BSPO["0000058"])
    SUPERFICIAL = PermissibleValue(
        text="SUPERFICIAL",
        title="Near the surface",
        meaning=BSPO["0000004"])
    DEEP = PermissibleValue(
        text="DEEP",
        title="Away from the surface",
        meaning=BSPO["0000003"])
    SUPERIOR = PermissibleValue(
        text="SUPERIOR",
        title="Above or upper (in standard anatomical position)",
        meaning=BSPO["0000022"])
    INFERIOR = PermissibleValue(
        text="INFERIOR",
        title="Below or lower (in standard anatomical position)",
        meaning=BSPO["0000025"])
    IPSILATERAL = PermissibleValue(
        text="IPSILATERAL",
        title="On the same side",
        meaning=BSPO["0000065"])
    CONTRALATERAL = PermissibleValue(
        text="CONTRALATERAL",
        title="On the opposite side",
        meaning=BSPO["0000060"])
    CENTRAL = PermissibleValue(
        text="CENTRAL",
        title="At or near the center",
        meaning=BSPO["0000059"])

    _defn = EnumDefinition(
        name="AnatomicalSide",
        description="""Anatomical sides as defined in the Biological Spatial Ontology (BSPO).
An anatomical region bounded by a plane perpendicular to an axis through the middle.""",
    )

class AnatomicalRegion(EnumDefinitionImpl):
    """
    Anatomical regions based on spatial position
    """
    ANTERIOR_REGION = PermissibleValue(
        text="ANTERIOR_REGION",
        title="Region in the anterior portion",
        meaning=BSPO["0000071"])
    POSTERIOR_REGION = PermissibleValue(
        text="POSTERIOR_REGION",
        title="Region in the posterior portion",
        meaning=BSPO["0000072"])
    DORSAL_REGION = PermissibleValue(
        text="DORSAL_REGION",
        title="Region in the dorsal portion",
        meaning=BSPO["0000079"])
    VENTRAL_REGION = PermissibleValue(
        text="VENTRAL_REGION",
        title="Region in the ventral portion",
        meaning=BSPO["0000084"])
    LATERAL_REGION = PermissibleValue(
        text="LATERAL_REGION",
        title="Region in the lateral portion",
        meaning=BSPO["0000082"])
    MEDIAL_REGION = PermissibleValue(
        text="MEDIAL_REGION",
        title="Region in the medial portion",
        meaning=BSPO["0000083"])
    PROXIMAL_REGION = PermissibleValue(
        text="PROXIMAL_REGION",
        title="Region in the proximal portion",
        meaning=BSPO["0000077"])
    DISTAL_REGION = PermissibleValue(
        text="DISTAL_REGION",
        title="Region in the distal portion",
        meaning=BSPO["0000078"])
    APICAL_REGION = PermissibleValue(
        text="APICAL_REGION",
        title="Region in the apical portion",
        meaning=BSPO["0000073"])
    BASAL_REGION = PermissibleValue(
        text="BASAL_REGION",
        title="Region in the basal portion",
        meaning=BSPO["0000074"])
    CENTRAL_REGION = PermissibleValue(
        text="CENTRAL_REGION",
        title="Region in the central portion",
        meaning=BSPO["0000075"])
    PERIPHERAL_REGION = PermissibleValue(
        text="PERIPHERAL_REGION",
        title="Region in the peripheral portion",
        meaning=BSPO["0000127"])

    _defn = EnumDefinition(
        name="AnatomicalRegion",
        description="Anatomical regions based on spatial position",
    )

class AnatomicalAxis(EnumDefinitionImpl):
    """
    Anatomical axes defining spatial organization
    """
    ANTERIOR_POSTERIOR = PermissibleValue(
        text="ANTERIOR_POSTERIOR",
        title="Anterior-posterior axis (head-tail axis)",
        meaning=BSPO["0000013"])
    DORSAL_VENTRAL = PermissibleValue(
        text="DORSAL_VENTRAL",
        title="Dorsal-ventral axis (back-belly axis)",
        meaning=BSPO["0000016"])
    LEFT_RIGHT = PermissibleValue(
        text="LEFT_RIGHT",
        title="Left-right axis (lateral axis)",
        meaning=BSPO["0000017"])
    PROXIMAL_DISTAL = PermissibleValue(
        text="PROXIMAL_DISTAL",
        title="Proximal-distal axis",
        meaning=BSPO["0000018"])
    APICAL_BASAL = PermissibleValue(
        text="APICAL_BASAL",
        title="Apical-basal axis",
        meaning=BSPO["0000023"])

    _defn = EnumDefinition(
        name="AnatomicalAxis",
        description="Anatomical axes defining spatial organization",
    )

class AnatomicalPlane(EnumDefinitionImpl):
    """
    Standard anatomical planes for sectioning
    """
    SAGITTAL = PermissibleValue(
        text="SAGITTAL",
        title="Vertical plane dividing body into left and right",
        meaning=BSPO["0000417"])
    MIDSAGITTAL = PermissibleValue(
        text="MIDSAGITTAL",
        title="Sagittal plane through the midline",
        meaning=BSPO["0000009"])
    PARASAGITTAL = PermissibleValue(
        text="PARASAGITTAL",
        title="Sagittal plane parallel to midline",
        meaning=BSPO["0000008"])
    CORONAL = PermissibleValue(
        text="CORONAL",
        title="Vertical plane dividing body into anterior and posterior",
        meaning=BSPO["0000019"])
    TRANSVERSE = PermissibleValue(
        text="TRANSVERSE",
        title="Horizontal plane dividing body into superior and inferior",
        meaning=BSPO["0000018"])
    OBLIQUE = PermissibleValue(
        text="OBLIQUE",
        description="Any plane not parallel to sagittal, coronal, or transverse planes")

    _defn = EnumDefinition(
        name="AnatomicalPlane",
        description="Standard anatomical planes for sectioning",
    )

class SpatialRelationship(EnumDefinitionImpl):
    """
    Spatial relationships between anatomical structures
    """
    ADJACENT_TO = PermissibleValue(
        text="ADJACENT_TO",
        title="Next to or adjoining",
        meaning=RO["0002220"])
    ANTERIOR_TO = PermissibleValue(
        text="ANTERIOR_TO",
        title="In front of",
        meaning=BSPO["0000096"])
    POSTERIOR_TO = PermissibleValue(
        text="POSTERIOR_TO",
        title="Behind",
        meaning=BSPO["0000099"])
    DORSAL_TO = PermissibleValue(
        text="DORSAL_TO",
        title="Above/on the back side of",
        meaning=BSPO["0000098"])
    VENTRAL_TO = PermissibleValue(
        text="VENTRAL_TO",
        title="Below/on the belly side of",
        meaning=BSPO["0000102"])
    LATERAL_TO = PermissibleValue(
        text="LATERAL_TO",
        title="To the side of",
        meaning=BSPO["0000114"])
    MEDIAL_TO = PermissibleValue(
        text="MEDIAL_TO",
        title="Toward the midline from",
        meaning=BSPO["0000115"])
    PROXIMAL_TO = PermissibleValue(
        text="PROXIMAL_TO",
        title="Closer to the origin than",
        meaning=BSPO["0000100"])
    DISTAL_TO = PermissibleValue(
        text="DISTAL_TO",
        title="Further from the origin than",
        meaning=BSPO["0000097"])
    SUPERFICIAL_TO = PermissibleValue(
        text="SUPERFICIAL_TO",
        title="Closer to the surface than",
        meaning=BSPO["0000108"])
    DEEP_TO = PermissibleValue(
        text="DEEP_TO",
        title="Further from the surface than",
        meaning=BSPO["0000107"])
    SURROUNDS = PermissibleValue(
        text="SURROUNDS",
        title="Encircles or encompasses",
        meaning=RO["0002221"])
    WITHIN = PermissibleValue(
        text="WITHIN",
        description="Inside or contained by")
    BETWEEN = PermissibleValue(
        text="BETWEEN",
        description="In the space separating two structures")

    _defn = EnumDefinition(
        name="SpatialRelationship",
        description="Spatial relationships between anatomical structures",
    )

class CellPolarity(EnumDefinitionImpl):
    """
    Spatial polarity in cells and tissues
    """
    APICAL = PermissibleValue(
        text="APICAL",
        description="The free surface of an epithelial cell")
    BASAL = PermissibleValue(
        text="BASAL",
        description="The attached surface of an epithelial cell")
    LATERAL = PermissibleValue(
        text="LATERAL",
        description="The sides of an epithelial cell")
    APICAL_LATERAL = PermissibleValue(
        text="APICAL_LATERAL",
        description="Junction between apical and lateral surfaces")
    BASAL_LATERAL = PermissibleValue(
        text="BASAL_LATERAL",
        description="Junction between basal and lateral surfaces")
    LEADING_EDGE = PermissibleValue(
        text="LEADING_EDGE",
        description="Front of a migrating cell")
    TRAILING_EDGE = PermissibleValue(
        text="TRAILING_EDGE",
        description="Rear of a migrating cell")
    PROXIMAL_POLE = PermissibleValue(
        text="PROXIMAL_POLE",
        description="Pole closer to the cell body")
    DISTAL_POLE = PermissibleValue(
        text="DISTAL_POLE",
        description="Pole further from the cell body")

    _defn = EnumDefinition(
        name="CellPolarity",
        description="Spatial polarity in cells and tissues",
    )

class CrystalSystemEnum(EnumDefinitionImpl):
    """
    The seven crystal systems in crystallography
    """
    TRICLINIC = PermissibleValue(
        text="TRICLINIC",
        title="Triclinic",
        description="Crystal system with no symmetry constraints (a≠b≠c, α≠β≠γ≠90°)",
        meaning=ENM["9000022"])
    MONOCLINIC = PermissibleValue(
        text="MONOCLINIC",
        title="Monoclinic",
        description="Crystal system with one twofold axis of symmetry (a≠b≠c, α=γ=90°≠β)",
        meaning=ENM["9000029"])
    ORTHORHOMBIC = PermissibleValue(
        text="ORTHORHOMBIC",
        title="Orthorhombic",
        description="Crystal system with three mutually perpendicular axes (a≠b≠c, α=β=γ=90°)",
        meaning=ENM["9000031"])
    TETRAGONAL = PermissibleValue(
        text="TETRAGONAL",
        title="Tetragonal",
        description="Crystal system with one fourfold axis (a=b≠c, α=β=γ=90°)",
        meaning=ENM["9000032"])
    TRIGONAL = PermissibleValue(
        text="TRIGONAL",
        title="Trigonal",
        description="Crystal system with one threefold axis (a=b=c, α=β=γ≠90°)",
        meaning=ENM["9000054"])
    HEXAGONAL = PermissibleValue(
        text="HEXAGONAL",
        title="Hexagonal",
        description="Crystal system with one sixfold axis (a=b≠c, α=β=90°, γ=120°)",
        meaning=PATO["0002509"])
    CUBIC = PermissibleValue(
        text="CUBIC",
        title="Cubic",
        description="Crystal system with four threefold axes (a=b=c, α=β=γ=90°)",
        meaning=ENM["9000035"])

    _defn = EnumDefinition(
        name="CrystalSystemEnum",
        description="The seven crystal systems in crystallography",
    )

class BravaisLatticeEnum(EnumDefinitionImpl):
    """
    The 14 Bravais lattices describing all possible crystal lattices
    """
    PRIMITIVE_TRICLINIC = PermissibleValue(
        text="PRIMITIVE_TRICLINIC",
        title="Primitive Triclinic",
        description="Primitive triclinic lattice (aP)")
    PRIMITIVE_MONOCLINIC = PermissibleValue(
        text="PRIMITIVE_MONOCLINIC",
        title="Primitive Monoclinic",
        description="Primitive monoclinic lattice (mP)")
    BASE_CENTERED_MONOCLINIC = PermissibleValue(
        text="BASE_CENTERED_MONOCLINIC",
        title="Base-Centered Monoclinic",
        description="Base-centered monoclinic lattice (mC)")
    PRIMITIVE_ORTHORHOMBIC = PermissibleValue(
        text="PRIMITIVE_ORTHORHOMBIC",
        title="Primitive Orthorhombic",
        description="Primitive orthorhombic lattice (oP)")
    BASE_CENTERED_ORTHORHOMBIC = PermissibleValue(
        text="BASE_CENTERED_ORTHORHOMBIC",
        title="Base-Centered Orthorhombic",
        description="Base-centered orthorhombic lattice (oC)")
    BODY_CENTERED_ORTHORHOMBIC = PermissibleValue(
        text="BODY_CENTERED_ORTHORHOMBIC",
        title="Body-Centered Orthorhombic",
        description="Body-centered orthorhombic lattice (oI)")
    FACE_CENTERED_ORTHORHOMBIC = PermissibleValue(
        text="FACE_CENTERED_ORTHORHOMBIC",
        title="Face-Centered Orthorhombic",
        description="Face-centered orthorhombic lattice (oF)")
    PRIMITIVE_TETRAGONAL = PermissibleValue(
        text="PRIMITIVE_TETRAGONAL",
        title="Primitive Tetragonal",
        description="Primitive tetragonal lattice (tP)")
    BODY_CENTERED_TETRAGONAL = PermissibleValue(
        text="BODY_CENTERED_TETRAGONAL",
        title="Body-Centered Tetragonal",
        description="Body-centered tetragonal lattice (tI)")
    PRIMITIVE_TRIGONAL = PermissibleValue(
        text="PRIMITIVE_TRIGONAL",
        title="Primitive Trigonal",
        description="Primitive trigonal/rhombohedral lattice (hR)")
    PRIMITIVE_HEXAGONAL = PermissibleValue(
        text="PRIMITIVE_HEXAGONAL",
        title="Primitive Hexagonal",
        description="Primitive hexagonal lattice (hP)")
    PRIMITIVE_CUBIC = PermissibleValue(
        text="PRIMITIVE_CUBIC",
        title="Primitive Cubic",
        description="Simple cubic lattice (cP)")
    BODY_CENTERED_CUBIC = PermissibleValue(
        text="BODY_CENTERED_CUBIC",
        title="Body-Centered Cubic",
        description="Body-centered cubic lattice (cI)")
    FACE_CENTERED_CUBIC = PermissibleValue(
        text="FACE_CENTERED_CUBIC",
        title="Face-Centered Cubic",
        description="Face-centered cubic lattice (cF)")

    _defn = EnumDefinition(
        name="BravaisLatticeEnum",
        description="The 14 Bravais lattices describing all possible crystal lattices",
    )

class ElectricalConductivityEnum(EnumDefinitionImpl):
    """
    Classification of materials by electrical conductivity
    """
    CONDUCTOR = PermissibleValue(
        text="CONDUCTOR",
        title="Conductor",
        description="Material with high electrical conductivity (resistivity < 10^-5 Ω·m)")
    SEMICONDUCTOR = PermissibleValue(
        text="SEMICONDUCTOR",
        title="Semiconductor",
        description="Material with intermediate electrical conductivity (10^-5 to 10^8 Ω·m)",
        meaning=NCIT["C172788"])
    INSULATOR = PermissibleValue(
        text="INSULATOR",
        title="Insulator",
        description="Material with very low electrical conductivity (resistivity > 10^8 Ω·m)")
    SUPERCONDUCTOR = PermissibleValue(
        text="SUPERCONDUCTOR",
        title="Superconductor",
        description="Material with zero electrical resistance below critical temperature")

    _defn = EnumDefinition(
        name="ElectricalConductivityEnum",
        description="Classification of materials by electrical conductivity",
    )

class MagneticPropertyEnum(EnumDefinitionImpl):
    """
    Classification of materials by magnetic properties
    """
    DIAMAGNETIC = PermissibleValue(
        text="DIAMAGNETIC",
        title="Diamagnetic",
        description="Weakly repelled by magnetic fields")
    PARAMAGNETIC = PermissibleValue(
        text="PARAMAGNETIC",
        title="Paramagnetic",
        description="Weakly attracted to magnetic fields")
    FERROMAGNETIC = PermissibleValue(
        text="FERROMAGNETIC",
        title="Ferromagnetic",
        description="Strongly attracted to magnetic fields, can be permanently magnetized")
    FERRIMAGNETIC = PermissibleValue(
        text="FERRIMAGNETIC",
        title="Ferrimagnetic",
        description="Similar to ferromagnetic but with opposing magnetic moments")
    ANTIFERROMAGNETIC = PermissibleValue(
        text="ANTIFERROMAGNETIC",
        title="Antiferromagnetic",
        description="Adjacent magnetic moments cancel each other")

    _defn = EnumDefinition(
        name="MagneticPropertyEnum",
        description="Classification of materials by magnetic properties",
    )

class OpticalPropertyEnum(EnumDefinitionImpl):
    """
    Optical properties of materials
    """
    TRANSPARENT = PermissibleValue(
        text="TRANSPARENT",
        title="Transparent",
        description="Allows light to pass through with minimal scattering",
        meaning=PATO["0000964"])
    TRANSLUCENT = PermissibleValue(
        text="TRANSLUCENT",
        title="Translucent",
        description="Allows light to pass through but with significant scattering")
    OPAQUE = PermissibleValue(
        text="OPAQUE",
        title="Opaque",
        description="Does not allow light to pass through",
        meaning=PATO["0000963"])
    REFLECTIVE = PermissibleValue(
        text="REFLECTIVE",
        title="Reflective",
        description="Reflects most incident light")
    ABSORBING = PermissibleValue(
        text="ABSORBING",
        title="Absorbing",
        description="Absorbs most incident light")
    FLUORESCENT = PermissibleValue(
        text="FLUORESCENT",
        title="Fluorescent",
        description="Emits light when excited by radiation")
    PHOSPHORESCENT = PermissibleValue(
        text="PHOSPHORESCENT",
        title="Phosphorescent",
        description="Continues to emit light after excitation stops")

    _defn = EnumDefinition(
        name="OpticalPropertyEnum",
        description="Optical properties of materials",
    )

class ThermalConductivityEnum(EnumDefinitionImpl):
    """
    Classification by thermal conductivity
    """
    HIGH_THERMAL_CONDUCTOR = PermissibleValue(
        text="HIGH_THERMAL_CONDUCTOR",
        title="High Thermal Conductor",
        description="High thermal conductivity (>100 W/m·K)")
    MODERATE_THERMAL_CONDUCTOR = PermissibleValue(
        text="MODERATE_THERMAL_CONDUCTOR",
        title="Moderate Thermal Conductor",
        description="Moderate thermal conductivity (1-100 W/m·K)")
    THERMAL_INSULATOR = PermissibleValue(
        text="THERMAL_INSULATOR",
        title="Thermal Insulator",
        description="Low thermal conductivity (<1 W/m·K)")

    _defn = EnumDefinition(
        name="ThermalConductivityEnum",
        description="Classification by thermal conductivity",
    )

class MechanicalBehaviorEnum(EnumDefinitionImpl):
    """
    Mechanical behavior of materials under stress
    """
    ELASTIC = PermissibleValue(
        text="ELASTIC",
        title="Elastic",
        description="Returns to original shape after stress removal",
        meaning=PATO["0001171"])
    PLASTIC = PermissibleValue(
        text="PLASTIC",
        title="inelastic",
        description="Undergoes permanent deformation under stress",
        meaning=PATO["0001172"])
    BRITTLE = PermissibleValue(
        text="BRITTLE",
        title="Brittle",
        description="Breaks without significant plastic deformation",
        meaning=PATO["0002477"])
    DUCTILE = PermissibleValue(
        text="DUCTILE",
        title="Ductile",
        description="Can be drawn into wires, undergoes large plastic deformation")
    MALLEABLE = PermissibleValue(
        text="MALLEABLE",
        title="Malleable",
        description="Can be hammered into sheets")
    TOUGH = PermissibleValue(
        text="TOUGH",
        title="Tough",
        description="High resistance to fracture")
    VISCOELASTIC = PermissibleValue(
        text="VISCOELASTIC",
        title="Viscoelastic",
        description="Exhibits both viscous and elastic characteristics")

    _defn = EnumDefinition(
        name="MechanicalBehaviorEnum",
        description="Mechanical behavior of materials under stress",
    )

class MicroscopyMethodEnum(EnumDefinitionImpl):
    """
    Microscopy techniques for material characterization
    """
    SEM = PermissibleValue(
        text="SEM",
        title="scanning electron microscopy",
        description="Scanning Electron Microscopy",
        meaning=CHMO["0000073"])
    TEM = PermissibleValue(
        text="TEM",
        title="transmission electron microscopy",
        description="Transmission Electron Microscopy",
        meaning=CHMO["0000080"])
    STEM = PermissibleValue(
        text="STEM",
        title="STEM",
        description="Scanning Transmission Electron Microscopy")
    AFM = PermissibleValue(
        text="AFM",
        title="atomic force microscopy",
        description="Atomic Force Microscopy",
        meaning=CHMO["0000113"])
    STM = PermissibleValue(
        text="STM",
        title="scanning tunnelling microscopy",
        description="Scanning Tunneling Microscopy",
        meaning=CHMO["0000132"])
    OPTICAL = PermissibleValue(
        text="OPTICAL",
        title="light microscopy assay",
        description="Optical/Light Microscopy",
        meaning=CHMO["0000102"])
    CONFOCAL = PermissibleValue(
        text="CONFOCAL",
        title="confocal fluorescence microscopy assay",
        description="Confocal Laser Scanning Microscopy",
        meaning=CHMO["0000089"])

    _defn = EnumDefinition(
        name="MicroscopyMethodEnum",
        description="Microscopy techniques for material characterization",
    )

class SpectroscopyMethodEnum(EnumDefinitionImpl):
    """
    Spectroscopy techniques for material analysis
    """
    XRD = PermissibleValue(
        text="XRD",
        title="XRD",
        description="X-ray Diffraction",
        meaning=CHMO["0000156"])
    XPS = PermissibleValue(
        text="XPS",
        title="XPS",
        description="X-ray Photoelectron Spectroscopy",
        meaning=CHMO["0000404"])
    EDS = PermissibleValue(
        text="EDS",
        title="energy-dispersive X-ray emission spectroscopy",
        description="Energy Dispersive X-ray Spectroscopy",
        meaning=CHMO["0000309"])
    FTIR = PermissibleValue(
        text="FTIR",
        title="Fourier transform infrared spectroscopy",
        description="Fourier Transform Infrared Spectroscopy",
        meaning=CHMO["0000636"])
    RAMAN = PermissibleValue(
        text="RAMAN",
        title="Raman",
        description="Raman Spectroscopy",
        meaning=CHMO["0000656"])
    UV_VIS = PermissibleValue(
        text="UV_VIS",
        title="ultraviolet-visible spectrophotometry",
        description="Ultraviolet-Visible Spectroscopy",
        meaning=CHMO["0000292"])
    NMR = PermissibleValue(
        text="NMR",
        title="nuclear magnetic resonance spectroscopy",
        description="Nuclear Magnetic Resonance Spectroscopy",
        meaning=CHMO["0000591"])
    XRF = PermissibleValue(
        text="XRF",
        title="X-ray emission spectroscopy",
        description="X-ray Fluorescence Spectroscopy",
        meaning=CHMO["0000307"])

    _defn = EnumDefinition(
        name="SpectroscopyMethodEnum",
        description="Spectroscopy techniques for material analysis",
    )

class ThermalAnalysisMethodEnum(EnumDefinitionImpl):
    """
    Thermal analysis techniques
    """
    DSC = PermissibleValue(
        text="DSC",
        title="DSC",
        description="Differential Scanning Calorimetry",
        meaning=CHMO["0000684"])
    TGA = PermissibleValue(
        text="TGA",
        title="thermogravimetry",
        description="Thermogravimetric Analysis",
        meaning=CHMO["0000690"])
    DTA = PermissibleValue(
        text="DTA",
        title="DTA",
        description="Differential Thermal Analysis",
        meaning=CHMO["0000687"])
    TMA = PermissibleValue(
        text="TMA",
        title="TMA",
        description="Thermomechanical Analysis")
    DMTA = PermissibleValue(
        text="DMTA",
        title="DMTA",
        description="Dynamic Mechanical Thermal Analysis")

    _defn = EnumDefinition(
        name="ThermalAnalysisMethodEnum",
        description="Thermal analysis techniques",
    )

class MechanicalTestingMethodEnum(EnumDefinitionImpl):
    """
    Mechanical testing methods
    """
    TENSILE = PermissibleValue(
        text="TENSILE",
        title="Tensile Test",
        description="Tensile strength testing")
    COMPRESSION = PermissibleValue(
        text="COMPRESSION",
        title="Compression Test",
        description="Compression strength testing")
    HARDNESS = PermissibleValue(
        text="HARDNESS",
        title="Hardness Test",
        description="Hardness testing (Vickers, Rockwell, Brinell)")
    IMPACT = PermissibleValue(
        text="IMPACT",
        title="Impact Test",
        description="Impact resistance testing (Charpy, Izod)")
    FATIGUE = PermissibleValue(
        text="FATIGUE",
        title="Fatigue Test",
        description="Fatigue testing under cyclic loading")
    CREEP = PermissibleValue(
        text="CREEP",
        title="Creep Test",
        description="Creep testing under sustained load")
    FRACTURE_TOUGHNESS = PermissibleValue(
        text="FRACTURE_TOUGHNESS",
        title="Fracture Toughness",
        description="Fracture toughness testing")
    NANOINDENTATION = PermissibleValue(
        text="NANOINDENTATION",
        title="Nanoindentation",
        description="Nanoindentation for nanoscale mechanical properties")

    _defn = EnumDefinition(
        name="MechanicalTestingMethodEnum",
        description="Mechanical testing methods",
    )

class MaterialClassEnum(EnumDefinitionImpl):
    """
    Major classes of materials
    """
    METAL = PermissibleValue(
        text="METAL",
        title="metallic material",
        description="Metallic materials with metallic bonding",
        meaning=ENVO["01001069"])
    CERAMIC = PermissibleValue(
        text="CERAMIC",
        title="Ceramic",
        description="Inorganic non-metallic materials",
        meaning=ENVO["03501307"])
    POLYMER = PermissibleValue(
        text="POLYMER",
        title="Polymer",
        description="Large molecules composed of repeating units",
        meaning=CHEBI["60027"])
    COMPOSITE = PermissibleValue(
        text="COMPOSITE",
        title="Composite",
        description="Materials made from two or more constituent materials",
        meaning=NCIT["C61520"])
    SEMICONDUCTOR = PermissibleValue(
        text="SEMICONDUCTOR",
        title="Semiconductor",
        description="Materials with electrical conductivity between conductors and insulators",
        meaning=NCIT["C172788"])
    BIOMATERIAL = PermissibleValue(
        text="BIOMATERIAL",
        title="Biomedical Material",
        description="Materials designed to interact with biological systems",
        meaning=NCIT["C16338"])
    NANOMATERIAL = PermissibleValue(
        text="NANOMATERIAL",
        title="Nanomaterial",
        description="Materials with at least one dimension in nanoscale (1-100 nm)",
        meaning=NCIT["C62371"])

    _defn = EnumDefinition(
        name="MaterialClassEnum",
        description="Major classes of materials",
    )

class PolymerTypeEnum(EnumDefinitionImpl):
    """
    Types of polymer materials
    """
    THERMOPLASTIC = PermissibleValue(
        text="THERMOPLASTIC",
        title="Thermoplastic",
        description="Polymer that becomes moldable above specific temperature",
        meaning=PATO["0040070"])
    THERMOSET = PermissibleValue(
        text="THERMOSET",
        title="thermoset polymer",
        description="Polymer that irreversibly hardens when cured",
        meaning=ENVO["06105005"])
    ELASTOMER = PermissibleValue(
        text="ELASTOMER",
        title="Elastomer",
        description="Polymer with elastic properties",
        meaning=SNOMED["261777007"])
    BIOPOLYMER = PermissibleValue(
        text="BIOPOLYMER",
        title="Biopolymer",
        description="Polymer produced by living organisms",
        meaning=NCIT["C73478"])
    CONDUCTING_POLYMER = PermissibleValue(
        text="CONDUCTING_POLYMER",
        title="Conducting Polymer",
        description="Polymer that conducts electricity")

    _defn = EnumDefinition(
        name="PolymerTypeEnum",
        description="Types of polymer materials",
    )

class MetalTypeEnum(EnumDefinitionImpl):
    """
    Types of metallic materials
    """
    FERROUS = PermissibleValue(
        text="FERROUS",
        title="Ferrous Metal",
        description="Iron-based metals and alloys",
        meaning=SNOMED["264354006"])
    NON_FERROUS = PermissibleValue(
        text="NON_FERROUS",
        title="Non-Ferrous Metal",
        description="Metals and alloys not containing iron",
        meaning=SNOMED["264879001"])
    NOBLE_METAL = PermissibleValue(
        text="NOBLE_METAL",
        title="Noble Metal",
        description="Metals resistant to corrosion and oxidation")
    REFRACTORY_METAL = PermissibleValue(
        text="REFRACTORY_METAL",
        title="Refractory Metal",
        description="Metals with very high melting points (>2000°C)")
    LIGHT_METAL = PermissibleValue(
        text="LIGHT_METAL",
        title="Light Metal",
        description="Low density metals (density < 5 g/cm³)",
        meaning=SNOMED["65436002"])
    HEAVY_METAL = PermissibleValue(
        text="HEAVY_METAL",
        title="Heavy Metal",
        description="High density metals (density > 5 g/cm³)",
        meaning=CHEBI["5631"])

    _defn = EnumDefinition(
        name="MetalTypeEnum",
        description="Types of metallic materials",
    )

class CompositeTypeEnum(EnumDefinitionImpl):
    """
    Types of composite materials
    """
    FIBER_REINFORCED = PermissibleValue(
        text="FIBER_REINFORCED",
        title="Fiber-Reinforced Composite",
        description="Composite with fiber reinforcement")
    PARTICLE_REINFORCED = PermissibleValue(
        text="PARTICLE_REINFORCED",
        title="Particle-Reinforced Composite",
        description="Composite with particle reinforcement")
    LAMINAR_COMPOSITE = PermissibleValue(
        text="LAMINAR_COMPOSITE",
        title="Laminar Composite",
        description="Composite with layered structure")
    METAL_MATRIX_COMPOSITE = PermissibleValue(
        text="METAL_MATRIX_COMPOSITE",
        title="Metal Matrix Composite",
        description="Composite with metal matrix")
    CERAMIC_MATRIX_COMPOSITE = PermissibleValue(
        text="CERAMIC_MATRIX_COMPOSITE",
        title="Ceramic Matrix Composite",
        description="Composite with ceramic matrix")
    POLYMER_MATRIX_COMPOSITE = PermissibleValue(
        text="POLYMER_MATRIX_COMPOSITE",
        title="Polymer Matrix Composite",
        description="Composite with polymer matrix")

    _defn = EnumDefinition(
        name="CompositeTypeEnum",
        description="Types of composite materials",
    )

class SynthesisMethodEnum(EnumDefinitionImpl):
    """
    Common material synthesis and processing methods
    """
    SOL_GEL = PermissibleValue(
        text="SOL_GEL",
        title="Sol-Gel",
        description="Synthesis from solution through gel formation")
    HYDROTHERMAL = PermissibleValue(
        text="HYDROTHERMAL",
        title="Hydrothermal",
        description="Synthesis using high temperature aqueous solutions")
    SOLVOTHERMAL = PermissibleValue(
        text="SOLVOTHERMAL",
        title="Solvothermal",
        description="Synthesis using non-aqueous solvents at high temperature/pressure")
    CVD = PermissibleValue(
        text="CVD",
        title="chemical vapour deposition",
        description="Chemical Vapor Deposition",
        meaning=CHMO["0001314"])
    PVD = PermissibleValue(
        text="PVD",
        title="physical vapour deposition",
        description="Physical Vapor Deposition",
        meaning=CHMO["0001356"])
    ALD = PermissibleValue(
        text="ALD",
        title="ALD",
        description="Atomic Layer Deposition")
    ELECTRODEPOSITION = PermissibleValue(
        text="ELECTRODEPOSITION",
        title="electrochemical deposition",
        description="Deposition using electric current",
        meaning=CHMO["0001331"])
    BALL_MILLING = PermissibleValue(
        text="BALL_MILLING",
        title="Ball Milling",
        description="Mechanical alloying using ball mill")
    PRECIPITATION = PermissibleValue(
        text="PRECIPITATION",
        title="precipitation",
        description="Formation of solid from solution",
        meaning=CHMO["0001688"])
    SINTERING = PermissibleValue(
        text="SINTERING",
        title="Sintering",
        description="Compacting and forming solid mass by heat/pressure")
    MELT_PROCESSING = PermissibleValue(
        text="MELT_PROCESSING",
        title="Melt Processing",
        description="Processing from molten state")
    SOLUTION_CASTING = PermissibleValue(
        text="SOLUTION_CASTING",
        title="Solution Casting",
        description="Casting from solution")
    SPIN_COATING = PermissibleValue(
        text="SPIN_COATING",
        title="Spin Coating",
        description="Coating by spinning substrate",
        meaning=CHMO["0001472"])
    DIP_COATING = PermissibleValue(
        text="DIP_COATING",
        title="Dip Coating",
        description="Coating by dipping in solution",
        meaning=CHMO["0001471"])
    SPRAY_COATING = PermissibleValue(
        text="SPRAY_COATING",
        title="Spray Coating",
        description="Coating by spraying")

    _defn = EnumDefinition(
        name="SynthesisMethodEnum",
        description="Common material synthesis and processing methods",
    )

class CrystalGrowthMethodEnum(EnumDefinitionImpl):
    """
    Methods for growing single crystals
    """
    CZOCHRALSKI = PermissibleValue(
        text="CZOCHRALSKI",
        title="Czochralski Method",
        description="Crystal pulling from melt")
    BRIDGMAN = PermissibleValue(
        text="BRIDGMAN",
        title="Bridgman Method",
        description="Directional solidification method")
    FLOAT_ZONE = PermissibleValue(
        text="FLOAT_ZONE",
        title="Float Zone",
        description="Zone melting without crucible")
    FLUX_GROWTH = PermissibleValue(
        text="FLUX_GROWTH",
        title="Flux Growth",
        description="Crystal growth from high temperature solution")
    VAPOR_TRANSPORT = PermissibleValue(
        text="VAPOR_TRANSPORT",
        title="Vapor Transport",
        description="Crystal growth via vapor phase transport")
    HYDROTHERMAL_GROWTH = PermissibleValue(
        text="HYDROTHERMAL_GROWTH",
        title="Hydrothermal Growth",
        description="Crystal growth in aqueous solution under pressure")
    LPE = PermissibleValue(
        text="LPE",
        title="LPE",
        description="Liquid Phase Epitaxy")
    MBE = PermissibleValue(
        text="MBE",
        title="molecular beam epitaxy",
        description="Molecular Beam Epitaxy",
        meaning=CHMO["0001341"])
    MOCVD = PermissibleValue(
        text="MOCVD",
        title="MOCVD",
        description="Metal-Organic Chemical Vapor Deposition")

    _defn = EnumDefinition(
        name="CrystalGrowthMethodEnum",
        description="Methods for growing single crystals",
    )

class AdditiveManufacturingEnum(EnumDefinitionImpl):
    """
    3D printing and additive manufacturing methods
    """
    FDM = PermissibleValue(
        text="FDM",
        title="FDM",
        description="Fused Deposition Modeling")
    SLA = PermissibleValue(
        text="SLA",
        title="SLA",
        description="Stereolithography")
    SLS = PermissibleValue(
        text="SLS",
        title="SLS",
        description="Selective Laser Sintering")
    SLM = PermissibleValue(
        text="SLM",
        title="SLM",
        description="Selective Laser Melting")
    EBM = PermissibleValue(
        text="EBM",
        title="EBM",
        description="Electron Beam Melting")
    BINDER_JETTING = PermissibleValue(
        text="BINDER_JETTING",
        title="Binder Jetting",
        description="Powder bed with liquid binder")
    MATERIAL_JETTING = PermissibleValue(
        text="MATERIAL_JETTING",
        title="Material Jetting",
        description="Droplet deposition of materials")
    DED = PermissibleValue(
        text="DED",
        title="DED",
        description="Directed Energy Deposition")

    _defn = EnumDefinition(
        name="AdditiveManufacturingEnum",
        description="3D printing and additive manufacturing methods",
    )

class TraditionalPigmentEnum(EnumDefinitionImpl):
    """
    Traditional artist pigments and their colors
    """
    TITANIUM_WHITE = PermissibleValue(
        text="TITANIUM_WHITE",
        title="titanium dioxide nanoparticle",
        description="Titanium white (Titanium dioxide)",
        meaning=CHEBI["51050"])
    ZINC_WHITE = PermissibleValue(
        text="ZINC_WHITE",
        title="zinc oxide",
        description="Zinc white (Zinc oxide)",
        meaning=CHEBI["36560"])
    LEAD_WHITE = PermissibleValue(
        text="LEAD_WHITE",
        description="Lead white (Basic lead carbonate) - toxic")
    CADMIUM_YELLOW = PermissibleValue(
        text="CADMIUM_YELLOW",
        title="cadmium selenide",
        description="Cadmium yellow (Cadmium sulfide)",
        meaning=CHEBI["50834"])
    CHROME_YELLOW = PermissibleValue(
        text="CHROME_YELLOW",
        description="Chrome yellow (Lead chromate) - toxic")
    NAPLES_YELLOW = PermissibleValue(
        text="NAPLES_YELLOW",
        description="Naples yellow (Lead antimonate)")
    YELLOW_OCHRE = PermissibleValue(
        text="YELLOW_OCHRE",
        description="Yellow ochre (Iron oxide hydroxide)")
    CADMIUM_ORANGE = PermissibleValue(
        text="CADMIUM_ORANGE",
        description="Cadmium orange (Cadmium selenide)")
    CADMIUM_RED = PermissibleValue(
        text="CADMIUM_RED",
        title="cadmium selenide nanoparticle",
        description="Cadmium red (Cadmium selenide)",
        meaning=CHEBI["50835"])
    VERMILION = PermissibleValue(
        text="VERMILION",
        description="Vermilion/Cinnabar (Mercury sulfide)")
    ALIZARIN_CRIMSON = PermissibleValue(
        text="ALIZARIN_CRIMSON",
        title="alizarin",
        description="Alizarin crimson (synthetic)",
        meaning=CHEBI["16866"])
    CARMINE = PermissibleValue(
        text="CARMINE",
        description="Carmine (from cochineal insects)")
    BURNT_SIENNA = PermissibleValue(
        text="BURNT_SIENNA",
        description="Burnt sienna (heated iron oxide)")
    RAW_SIENNA = PermissibleValue(
        text="RAW_SIENNA",
        description="Raw sienna (Iron oxide with clay)")
    BURNT_UMBER = PermissibleValue(
        text="BURNT_UMBER",
        description="Burnt umber (heated iron/manganese oxide)")
    RAW_UMBER = PermissibleValue(
        text="RAW_UMBER",
        description="Raw umber (Iron/manganese oxide)")
    VAN_DYKE_BROWN = PermissibleValue(
        text="VAN_DYKE_BROWN",
        description="Van Dyke brown (organic earth)")
    PRUSSIAN_BLUE = PermissibleValue(
        text="PRUSSIAN_BLUE",
        title="ferric ferrocyanide",
        description="Prussian blue (Ferric ferrocyanide)",
        meaning=CHEBI["30069"])
    ULTRAMARINE = PermissibleValue(
        text="ULTRAMARINE",
        description="Ultramarine blue (originally lapis lazuli)")
    COBALT_BLUE = PermissibleValue(
        text="COBALT_BLUE",
        description="Cobalt blue (Cobalt aluminate)")
    CERULEAN_BLUE = PermissibleValue(
        text="CERULEAN_BLUE",
        description="Cerulean blue (Cobalt stannate)")
    PHTHALO_BLUE = PermissibleValue(
        text="PHTHALO_BLUE",
        description="Phthalocyanine blue")
    VIRIDIAN = PermissibleValue(
        text="VIRIDIAN",
        description="Viridian (Chromium oxide green)")
    CHROME_GREEN = PermissibleValue(
        text="CHROME_GREEN",
        description="Chrome oxide green")
    PHTHALO_GREEN = PermissibleValue(
        text="PHTHALO_GREEN",
        description="Phthalocyanine green")
    TERRE_VERTE = PermissibleValue(
        text="TERRE_VERTE",
        description="Terre verte/Green earth")
    TYRIAN_PURPLE = PermissibleValue(
        text="TYRIAN_PURPLE",
        description="Tyrian purple (from murex snails)")
    MANGANESE_VIOLET = PermissibleValue(
        text="MANGANESE_VIOLET",
        description="Manganese violet")
    MARS_BLACK = PermissibleValue(
        text="MARS_BLACK",
        description="Mars black (Synthetic iron oxide)")
    IVORY_BLACK = PermissibleValue(
        text="IVORY_BLACK",
        description="Ivory black (Bone char)")
    LAMP_BLACK = PermissibleValue(
        text="LAMP_BLACK",
        description="Lamp black (Carbon black)")

    _defn = EnumDefinition(
        name="TraditionalPigmentEnum",
        description="Traditional artist pigments and their colors",
    )

class IndustrialDyeEnum(EnumDefinitionImpl):
    """
    Industrial and textile dyes
    """
    INDIGO = PermissibleValue(
        text="INDIGO",
        description="Indigo dye")
    ANILINE_BLACK = PermissibleValue(
        text="ANILINE_BLACK",
        description="Aniline black")
    METHYLENE_BLUE = PermissibleValue(
        text="METHYLENE_BLUE",
        description="Methylene blue")
    CONGO_RED = PermissibleValue(
        text="CONGO_RED",
        description="Congo red",
        meaning=CHEBI["34653"])
    MALACHITE_GREEN = PermissibleValue(
        text="MALACHITE_GREEN",
        description="Malachite green",
        meaning=CHEBI["72449"])
    CRYSTAL_VIOLET = PermissibleValue(
        text="CRYSTAL_VIOLET",
        description="Crystal violet/Gentian violet",
        meaning=CHEBI["41688"])
    EOSIN = PermissibleValue(
        text="EOSIN",
        description="Eosin Y",
        meaning=CHEBI["52053"])
    SAFRANIN = PermissibleValue(
        text="SAFRANIN",
        description="Safranin O")
    ACID_ORANGE_7 = PermissibleValue(
        text="ACID_ORANGE_7",
        description="Acid Orange 7 (Orange II)")
    REACTIVE_BLACK_5 = PermissibleValue(
        text="REACTIVE_BLACK_5",
        description="Reactive Black 5")
    DISPERSE_BLUE_1 = PermissibleValue(
        text="DISPERSE_BLUE_1",
        description="Disperse Blue 1")
    VAT_BLUE_1 = PermissibleValue(
        text="VAT_BLUE_1",
        description="Vat Blue 1 (Indanthrene blue)")

    _defn = EnumDefinition(
        name="IndustrialDyeEnum",
        description="Industrial and textile dyes",
    )

class FoodColoringEnum(EnumDefinitionImpl):
    """
    Food coloring and natural food dyes
    """
    FD_C_RED_40 = PermissibleValue(
        text="FD_C_RED_40",
        description="FD&C Red No. 40 (Allura Red)")
    FD_C_YELLOW_5 = PermissibleValue(
        text="FD_C_YELLOW_5",
        description="FD&C Yellow No. 5 (Tartrazine)")
    FD_C_YELLOW_6 = PermissibleValue(
        text="FD_C_YELLOW_6",
        description="FD&C Yellow No. 6 (Sunset Yellow)")
    FD_C_BLUE_1 = PermissibleValue(
        text="FD_C_BLUE_1",
        title="Brilliant Blue",
        description="FD&C Blue No. 1 (Brilliant Blue)",
        meaning=CHEBI["82411"])
    FD_C_BLUE_2 = PermissibleValue(
        text="FD_C_BLUE_2",
        description="FD&C Blue No. 2 (Indigo Carmine)")
    FD_C_GREEN_3 = PermissibleValue(
        text="FD_C_GREEN_3",
        description="FD&C Green No. 3 (Fast Green)")
    CARAMEL_COLOR = PermissibleValue(
        text="CARAMEL_COLOR",
        description="Caramel coloring")
    ANNATTO = PermissibleValue(
        text="ANNATTO",
        description="Annatto (natural orange)",
        meaning=CHEBI["3136"])
    TURMERIC = PermissibleValue(
        text="TURMERIC",
        title="curcumin",
        description="Turmeric/Curcumin (natural yellow)",
        meaning=CHEBI["3962"])
    BEETROOT_RED = PermissibleValue(
        text="BEETROOT_RED",
        description="Beetroot red/Betanin",
        meaning=CHEBI["3080"])
    CHLOROPHYLL = PermissibleValue(
        text="CHLOROPHYLL",
        description="Chlorophyll (natural green)",
        meaning=CHEBI["28966"])
    ANTHOCYANINS = PermissibleValue(
        text="ANTHOCYANINS",
        description="Anthocyanins (natural purple/red)")
    PAPRIKA_EXTRACT = PermissibleValue(
        text="PAPRIKA_EXTRACT",
        description="Paprika extract")
    SPIRULINA_BLUE = PermissibleValue(
        text="SPIRULINA_BLUE",
        description="Spirulina extract (phycocyanin)")

    _defn = EnumDefinition(
        name="FoodColoringEnum",
        description="Food coloring and natural food dyes",
    )

class AutomobilePaintColorEnum(EnumDefinitionImpl):
    """
    Common automobile paint colors
    """
    ARCTIC_WHITE = PermissibleValue(
        text="ARCTIC_WHITE",
        description="Arctic White",
        meaning=HEX["FFFFFF"])
    MIDNIGHT_BLACK = PermissibleValue(
        text="MIDNIGHT_BLACK",
        description="Midnight Black",
        meaning=HEX["000000"])
    SILVER_METALLIC = PermissibleValue(
        text="SILVER_METALLIC",
        description="Silver Metallic",
        meaning=HEX["C0C0C0"])
    GUNMETAL_GRAY = PermissibleValue(
        text="GUNMETAL_GRAY",
        description="Gunmetal Gray",
        meaning=HEX["2A3439"])
    RACING_RED = PermissibleValue(
        text="RACING_RED",
        description="Racing Red",
        meaning=HEX["CE1620"])
    CANDY_APPLE_RED = PermissibleValue(
        text="CANDY_APPLE_RED",
        description="Candy Apple Red",
        meaning=HEX["FF0800"])
    ELECTRIC_BLUE = PermissibleValue(
        text="ELECTRIC_BLUE",
        description="Electric Blue",
        meaning=HEX["7DF9FF"])
    BRITISH_RACING_GREEN = PermissibleValue(
        text="BRITISH_RACING_GREEN",
        description="British Racing Green",
        meaning=HEX["004225"])
    PEARL_WHITE = PermissibleValue(
        text="PEARL_WHITE",
        description="Pearl White",
        meaning=HEX["F8F8FF"])
    CHAMPAGNE_GOLD = PermissibleValue(
        text="CHAMPAGNE_GOLD",
        description="Champagne Gold",
        meaning=HEX["D4AF37"])
    COPPER_BRONZE = PermissibleValue(
        text="COPPER_BRONZE",
        description="Copper Bronze",
        meaning=HEX["B87333"])
    MIAMI_BLUE = PermissibleValue(
        text="MIAMI_BLUE",
        description="Miami Blue",
        meaning=HEX["00BFFF"])

    _defn = EnumDefinition(
        name="AutomobilePaintColorEnum",
        description="Common automobile paint colors",
    )

class BasicColorEnum(EnumDefinitionImpl):
    """
    Basic color names commonly used in everyday language
    """
    RED = PermissibleValue(
        text="RED",
        description="Primary red color",
        meaning=HEX["FF0000"])
    GREEN = PermissibleValue(
        text="GREEN",
        description="Primary green color",
        meaning=HEX["008000"])
    BLUE = PermissibleValue(
        text="BLUE",
        description="Primary blue color",
        meaning=HEX["0000FF"])
    YELLOW = PermissibleValue(
        text="YELLOW",
        description="Secondary yellow color",
        meaning=HEX["FFFF00"])
    ORANGE = PermissibleValue(
        text="ORANGE",
        description="Secondary orange color",
        meaning=HEX["FFA500"])
    PURPLE = PermissibleValue(
        text="PURPLE",
        description="Secondary purple color",
        meaning=HEX["800080"])
    BLACK = PermissibleValue(
        text="BLACK",
        description="Absence of color",
        meaning=HEX["000000"])
    WHITE = PermissibleValue(
        text="WHITE",
        description="All colors combined",
        meaning=HEX["FFFFFF"])
    GRAY = PermissibleValue(
        text="GRAY",
        description="Neutral gray",
        meaning=HEX["808080"])
    BROWN = PermissibleValue(
        text="BROWN",
        description="Brown color",
        meaning=HEX["A52A2A"])
    PINK = PermissibleValue(
        text="PINK",
        description="Light red/pink color",
        meaning=HEX["FFC0CB"])
    CYAN = PermissibleValue(
        text="CYAN",
        description="Cyan/aqua color",
        meaning=HEX["00FFFF"])
    MAGENTA = PermissibleValue(
        text="MAGENTA",
        description="Magenta color",
        meaning=HEX["FF00FF"])

    _defn = EnumDefinition(
        name="BasicColorEnum",
        description="Basic color names commonly used in everyday language",
    )

class WebColorEnum(EnumDefinitionImpl):
    """
    Standard HTML/CSS named colors (147 colors)
    """
    INDIAN_RED = PermissibleValue(
        text="INDIAN_RED",
        description="Indian red",
        meaning=HEX["CD5C5C"])
    LIGHT_CORAL = PermissibleValue(
        text="LIGHT_CORAL",
        description="Light coral",
        meaning=HEX["F08080"])
    SALMON = PermissibleValue(
        text="SALMON",
        description="Salmon",
        meaning=HEX["FA8072"])
    DARK_SALMON = PermissibleValue(
        text="DARK_SALMON",
        description="Dark salmon",
        meaning=HEX["E9967A"])
    CRIMSON = PermissibleValue(
        text="CRIMSON",
        description="Crimson",
        meaning=HEX["DC143C"])
    FIREBRICK = PermissibleValue(
        text="FIREBRICK",
        description="Firebrick",
        meaning=HEX["B22222"])
    DARK_RED = PermissibleValue(
        text="DARK_RED",
        description="Dark red",
        meaning=HEX["8B0000"])
    HOT_PINK = PermissibleValue(
        text="HOT_PINK",
        description="Hot pink",
        meaning=HEX["FF69B4"])
    DEEP_PINK = PermissibleValue(
        text="DEEP_PINK",
        description="Deep pink",
        meaning=HEX["FF1493"])
    LIGHT_PINK = PermissibleValue(
        text="LIGHT_PINK",
        description="Light pink",
        meaning=HEX["FFB6C1"])
    PALE_VIOLET_RED = PermissibleValue(
        text="PALE_VIOLET_RED",
        description="Pale violet red",
        meaning=HEX["DB7093"])
    CORAL = PermissibleValue(
        text="CORAL",
        description="Coral",
        meaning=HEX["FF7F50"])
    TOMATO = PermissibleValue(
        text="TOMATO",
        description="Tomato",
        meaning=HEX["FF6347"])
    ORANGE_RED = PermissibleValue(
        text="ORANGE_RED",
        description="Orange red",
        meaning=HEX["FF4500"])
    DARK_ORANGE = PermissibleValue(
        text="DARK_ORANGE",
        description="Dark orange",
        meaning=HEX["FF8C00"])
    GOLD = PermissibleValue(
        text="GOLD",
        description="Gold",
        meaning=HEX["FFD700"])
    LIGHT_YELLOW = PermissibleValue(
        text="LIGHT_YELLOW",
        description="Light yellow",
        meaning=HEX["FFFFE0"])
    LEMON_CHIFFON = PermissibleValue(
        text="LEMON_CHIFFON",
        description="Lemon chiffon",
        meaning=HEX["FFFACD"])
    PAPAYA_WHIP = PermissibleValue(
        text="PAPAYA_WHIP",
        description="Papaya whip",
        meaning=HEX["FFEFD5"])
    MOCCASIN = PermissibleValue(
        text="MOCCASIN",
        description="Moccasin",
        meaning=HEX["FFE4B5"])
    PEACH_PUFF = PermissibleValue(
        text="PEACH_PUFF",
        description="Peach puff",
        meaning=HEX["FFDAB9"])
    KHAKI = PermissibleValue(
        text="KHAKI",
        description="Khaki",
        meaning=HEX["F0E68C"])
    LAVENDER = PermissibleValue(
        text="LAVENDER",
        description="Lavender",
        meaning=HEX["E6E6FA"])
    THISTLE = PermissibleValue(
        text="THISTLE",
        description="Thistle",
        meaning=HEX["D8BFD8"])
    PLUM = PermissibleValue(
        text="PLUM",
        description="Plum",
        meaning=HEX["DDA0DD"])
    VIOLET = PermissibleValue(
        text="VIOLET",
        description="Violet",
        meaning=HEX["EE82EE"])
    ORCHID = PermissibleValue(
        text="ORCHID",
        description="Orchid",
        meaning=HEX["DA70D6"])
    FUCHSIA = PermissibleValue(
        text="FUCHSIA",
        description="Fuchsia",
        meaning=HEX["FF00FF"])
    MEDIUM_ORCHID = PermissibleValue(
        text="MEDIUM_ORCHID",
        description="Medium orchid",
        meaning=HEX["BA55D3"])
    MEDIUM_PURPLE = PermissibleValue(
        text="MEDIUM_PURPLE",
        description="Medium purple",
        meaning=HEX["9370DB"])
    BLUE_VIOLET = PermissibleValue(
        text="BLUE_VIOLET",
        description="Blue violet",
        meaning=HEX["8A2BE2"])
    DARK_VIOLET = PermissibleValue(
        text="DARK_VIOLET",
        description="Dark violet",
        meaning=HEX["9400D3"])
    DARK_ORCHID = PermissibleValue(
        text="DARK_ORCHID",
        description="Dark orchid",
        meaning=HEX["9932CC"])
    DARK_MAGENTA = PermissibleValue(
        text="DARK_MAGENTA",
        description="Dark magenta",
        meaning=HEX["8B008B"])
    INDIGO = PermissibleValue(
        text="INDIGO",
        description="Indigo",
        meaning=HEX["4B0082"])
    GREEN_YELLOW = PermissibleValue(
        text="GREEN_YELLOW",
        description="Green yellow",
        meaning=HEX["ADFF2F"])
    CHARTREUSE = PermissibleValue(
        text="CHARTREUSE",
        description="Chartreuse",
        meaning=HEX["7FFF00"])
    LAWN_GREEN = PermissibleValue(
        text="LAWN_GREEN",
        description="Lawn green",
        meaning=HEX["7CFC00"])
    LIME = PermissibleValue(
        text="LIME",
        description="Lime",
        meaning=HEX["00FF00"])
    LIME_GREEN = PermissibleValue(
        text="LIME_GREEN",
        description="Lime green",
        meaning=HEX["32CD32"])
    PALE_GREEN = PermissibleValue(
        text="PALE_GREEN",
        description="Pale green",
        meaning=HEX["98FB98"])
    LIGHT_GREEN = PermissibleValue(
        text="LIGHT_GREEN",
        description="Light green",
        meaning=HEX["90EE90"])
    MEDIUM_SPRING_GREEN = PermissibleValue(
        text="MEDIUM_SPRING_GREEN",
        description="Medium spring green",
        meaning=HEX["00FA9A"])
    SPRING_GREEN = PermissibleValue(
        text="SPRING_GREEN",
        description="Spring green",
        meaning=HEX["00FF7F"])
    MEDIUM_SEA_GREEN = PermissibleValue(
        text="MEDIUM_SEA_GREEN",
        description="Medium sea green",
        meaning=HEX["3CB371"])
    SEA_GREEN = PermissibleValue(
        text="SEA_GREEN",
        description="Sea green",
        meaning=HEX["2E8B57"])
    FOREST_GREEN = PermissibleValue(
        text="FOREST_GREEN",
        description="Forest green",
        meaning=HEX["228B22"])
    DARK_GREEN = PermissibleValue(
        text="DARK_GREEN",
        description="Dark green",
        meaning=HEX["006400"])
    YELLOW_GREEN = PermissibleValue(
        text="YELLOW_GREEN",
        description="Yellow green",
        meaning=HEX["9ACD32"])
    OLIVE_DRAB = PermissibleValue(
        text="OLIVE_DRAB",
        description="Olive drab",
        meaning=HEX["6B8E23"])
    OLIVE = PermissibleValue(
        text="OLIVE",
        description="Olive",
        meaning=HEX["808000"])
    DARK_OLIVE_GREEN = PermissibleValue(
        text="DARK_OLIVE_GREEN",
        description="Dark olive green",
        meaning=HEX["556B2F"])
    AQUA = PermissibleValue(
        text="AQUA",
        description="Aqua",
        meaning=HEX["00FFFF"])
    CYAN = PermissibleValue(
        text="CYAN",
        description="Cyan",
        meaning=HEX["00FFFF"])
    LIGHT_CYAN = PermissibleValue(
        text="LIGHT_CYAN",
        description="Light cyan",
        meaning=HEX["E0FFFF"])
    PALE_TURQUOISE = PermissibleValue(
        text="PALE_TURQUOISE",
        description="Pale turquoise",
        meaning=HEX["AFEEEE"])
    AQUAMARINE = PermissibleValue(
        text="AQUAMARINE",
        description="Aquamarine",
        meaning=HEX["7FFFD4"])
    TURQUOISE = PermissibleValue(
        text="TURQUOISE",
        description="Turquoise",
        meaning=HEX["40E0D0"])
    MEDIUM_TURQUOISE = PermissibleValue(
        text="MEDIUM_TURQUOISE",
        description="Medium turquoise",
        meaning=HEX["48D1CC"])
    DARK_TURQUOISE = PermissibleValue(
        text="DARK_TURQUOISE",
        description="Dark turquoise",
        meaning=HEX["00CED1"])
    LIGHT_SEA_GREEN = PermissibleValue(
        text="LIGHT_SEA_GREEN",
        description="Light sea green",
        meaning=HEX["20B2AA"])
    CADET_BLUE = PermissibleValue(
        text="CADET_BLUE",
        description="Cadet blue",
        meaning=HEX["5F9EA0"])
    DARK_CYAN = PermissibleValue(
        text="DARK_CYAN",
        description="Dark cyan",
        meaning=HEX["008B8B"])
    TEAL = PermissibleValue(
        text="TEAL",
        description="Teal",
        meaning=HEX["008080"])
    LIGHT_STEEL_BLUE = PermissibleValue(
        text="LIGHT_STEEL_BLUE",
        description="Light steel blue",
        meaning=HEX["B0C4DE"])
    POWDER_BLUE = PermissibleValue(
        text="POWDER_BLUE",
        description="Powder blue",
        meaning=HEX["B0E0E6"])
    LIGHT_BLUE = PermissibleValue(
        text="LIGHT_BLUE",
        description="Light blue",
        meaning=HEX["ADD8E6"])
    SKY_BLUE = PermissibleValue(
        text="SKY_BLUE",
        description="Sky blue",
        meaning=HEX["87CEEB"])
    LIGHT_SKY_BLUE = PermissibleValue(
        text="LIGHT_SKY_BLUE",
        description="Light sky blue",
        meaning=HEX["87CEFA"])
    DEEP_SKY_BLUE = PermissibleValue(
        text="DEEP_SKY_BLUE",
        description="Deep sky blue",
        meaning=HEX["00BFFF"])
    DODGER_BLUE = PermissibleValue(
        text="DODGER_BLUE",
        description="Dodger blue",
        meaning=HEX["1E90FF"])
    CORNFLOWER_BLUE = PermissibleValue(
        text="CORNFLOWER_BLUE",
        description="Cornflower blue",
        meaning=HEX["6495ED"])
    STEEL_BLUE = PermissibleValue(
        text="STEEL_BLUE",
        description="Steel blue",
        meaning=HEX["4682B4"])
    ROYAL_BLUE = PermissibleValue(
        text="ROYAL_BLUE",
        description="Royal blue",
        meaning=HEX["4169E1"])
    MEDIUM_BLUE = PermissibleValue(
        text="MEDIUM_BLUE",
        description="Medium blue",
        meaning=HEX["0000CD"])
    DARK_BLUE = PermissibleValue(
        text="DARK_BLUE",
        description="Dark blue",
        meaning=HEX["00008B"])
    NAVY = PermissibleValue(
        text="NAVY",
        description="Navy",
        meaning=HEX["000080"])
    MIDNIGHT_BLUE = PermissibleValue(
        text="MIDNIGHT_BLUE",
        description="Midnight blue",
        meaning=HEX["191970"])
    CORNSILK = PermissibleValue(
        text="CORNSILK",
        description="Cornsilk",
        meaning=HEX["FFF8DC"])
    BLANCHED_ALMOND = PermissibleValue(
        text="BLANCHED_ALMOND",
        description="Blanched almond",
        meaning=HEX["FFEBCD"])
    BISQUE = PermissibleValue(
        text="BISQUE",
        description="Bisque",
        meaning=HEX["FFE4C4"])
    NAVAJO_WHITE = PermissibleValue(
        text="NAVAJO_WHITE",
        description="Navajo white",
        meaning=HEX["FFDEAD"])
    WHEAT = PermissibleValue(
        text="WHEAT",
        description="Wheat",
        meaning=HEX["F5DEB3"])
    BURLYWOOD = PermissibleValue(
        text="BURLYWOOD",
        description="Burlywood",
        meaning=HEX["DEB887"])
    TAN = PermissibleValue(
        text="TAN",
        description="Tan",
        meaning=HEX["D2B48C"])
    ROSY_BROWN = PermissibleValue(
        text="ROSY_BROWN",
        description="Rosy brown",
        meaning=HEX["BC8F8F"])
    SANDY_BROWN = PermissibleValue(
        text="SANDY_BROWN",
        description="Sandy brown",
        meaning=HEX["F4A460"])
    GOLDENROD = PermissibleValue(
        text="GOLDENROD",
        description="Goldenrod",
        meaning=HEX["DAA520"])
    DARK_GOLDENROD = PermissibleValue(
        text="DARK_GOLDENROD",
        description="Dark goldenrod",
        meaning=HEX["B8860B"])
    PERU = PermissibleValue(
        text="PERU",
        description="Peru",
        meaning=HEX["CD853F"])
    CHOCOLATE = PermissibleValue(
        text="CHOCOLATE",
        description="Chocolate",
        meaning=HEX["D2691E"])
    SADDLE_BROWN = PermissibleValue(
        text="SADDLE_BROWN",
        description="Saddle brown",
        meaning=HEX["8B4513"])
    SIENNA = PermissibleValue(
        text="SIENNA",
        description="Sienna",
        meaning=HEX["A0522D"])
    MAROON = PermissibleValue(
        text="MAROON",
        description="Maroon",
        meaning=HEX["800000"])
    SNOW = PermissibleValue(
        text="SNOW",
        description="Snow",
        meaning=HEX["FFFAFA"])
    HONEYDEW = PermissibleValue(
        text="HONEYDEW",
        description="Honeydew",
        meaning=HEX["F0FFF0"])
    MINT_CREAM = PermissibleValue(
        text="MINT_CREAM",
        description="Mint cream",
        meaning=HEX["F5FFFA"])
    AZURE = PermissibleValue(
        text="AZURE",
        description="Azure",
        meaning=HEX["F0FFFF"])
    ALICE_BLUE = PermissibleValue(
        text="ALICE_BLUE",
        description="Alice blue",
        meaning=HEX["F0F8FF"])
    GHOST_WHITE = PermissibleValue(
        text="GHOST_WHITE",
        description="Ghost white",
        meaning=HEX["F8F8FF"])
    WHITE_SMOKE = PermissibleValue(
        text="WHITE_SMOKE",
        description="White smoke",
        meaning=HEX["F5F5F5"])
    SEASHELL = PermissibleValue(
        text="SEASHELL",
        description="Seashell",
        meaning=HEX["FFF5EE"])
    BEIGE = PermissibleValue(
        text="BEIGE",
        description="Beige",
        meaning=HEX["F5F5DC"])
    OLD_LACE = PermissibleValue(
        text="OLD_LACE",
        description="Old lace",
        meaning=HEX["FDF5E6"])
    FLORAL_WHITE = PermissibleValue(
        text="FLORAL_WHITE",
        description="Floral white",
        meaning=HEX["FFFAF0"])
    IVORY = PermissibleValue(
        text="IVORY",
        description="Ivory",
        meaning=HEX["FFFFF0"])
    ANTIQUE_WHITE = PermissibleValue(
        text="ANTIQUE_WHITE",
        description="Antique white",
        meaning=HEX["FAEBD7"])
    LINEN = PermissibleValue(
        text="LINEN",
        description="Linen",
        meaning=HEX["FAF0E6"])
    LAVENDER_BLUSH = PermissibleValue(
        text="LAVENDER_BLUSH",
        description="Lavender blush",
        meaning=HEX["FFF0F5"])
    MISTY_ROSE = PermissibleValue(
        text="MISTY_ROSE",
        description="Misty rose",
        meaning=HEX["FFE4E1"])
    GAINSBORO = PermissibleValue(
        text="GAINSBORO",
        description="Gainsboro",
        meaning=HEX["DCDCDC"])
    LIGHT_GRAY = PermissibleValue(
        text="LIGHT_GRAY",
        description="Light gray",
        meaning=HEX["D3D3D3"])
    SILVER = PermissibleValue(
        text="SILVER",
        description="Silver",
        meaning=HEX["C0C0C0"])
    DARK_GRAY = PermissibleValue(
        text="DARK_GRAY",
        description="Dark gray",
        meaning=HEX["A9A9A9"])
    DIM_GRAY = PermissibleValue(
        text="DIM_GRAY",
        description="Dim gray",
        meaning=HEX["696969"])
    LIGHT_SLATE_GRAY = PermissibleValue(
        text="LIGHT_SLATE_GRAY",
        description="Light slate gray",
        meaning=HEX["778899"])
    SLATE_GRAY = PermissibleValue(
        text="SLATE_GRAY",
        description="Slate gray",
        meaning=HEX["708090"])
    DARK_SLATE_GRAY = PermissibleValue(
        text="DARK_SLATE_GRAY",
        description="Dark slate gray",
        meaning=HEX["2F4F4F"])

    _defn = EnumDefinition(
        name="WebColorEnum",
        description="Standard HTML/CSS named colors (147 colors)",
    )

class X11ColorEnum(EnumDefinitionImpl):
    """
    X11/Unix system colors (extended set)
    """
    X11_AQUA = PermissibleValue(
        text="X11_AQUA",
        description="X11 Aqua",
        meaning=HEX["00FFFF"])
    X11_GRAY0 = PermissibleValue(
        text="X11_GRAY0",
        description="X11 Gray 0 (black)",
        meaning=HEX["000000"])
    X11_GRAY25 = PermissibleValue(
        text="X11_GRAY25",
        description="X11 Gray 25%",
        meaning=HEX["404040"])
    X11_GRAY50 = PermissibleValue(
        text="X11_GRAY50",
        description="X11 Gray 50%",
        meaning=HEX["808080"])
    X11_GRAY75 = PermissibleValue(
        text="X11_GRAY75",
        description="X11 Gray 75%",
        meaning=HEX["BFBFBF"])
    X11_GRAY100 = PermissibleValue(
        text="X11_GRAY100",
        description="X11 Gray 100 (white)",
        meaning=HEX["FFFFFF"])
    X11_GREEN1 = PermissibleValue(
        text="X11_GREEN1",
        description="X11 Green 1",
        meaning=HEX["00FF00"])
    X11_GREEN2 = PermissibleValue(
        text="X11_GREEN2",
        description="X11 Green 2",
        meaning=HEX["00EE00"])
    X11_GREEN3 = PermissibleValue(
        text="X11_GREEN3",
        description="X11 Green 3",
        meaning=HEX["00CD00"])
    X11_GREEN4 = PermissibleValue(
        text="X11_GREEN4",
        description="X11 Green 4",
        meaning=HEX["008B00"])
    X11_BLUE1 = PermissibleValue(
        text="X11_BLUE1",
        description="X11 Blue 1",
        meaning=HEX["0000FF"])
    X11_BLUE2 = PermissibleValue(
        text="X11_BLUE2",
        description="X11 Blue 2",
        meaning=HEX["0000EE"])
    X11_BLUE3 = PermissibleValue(
        text="X11_BLUE3",
        description="X11 Blue 3",
        meaning=HEX["0000CD"])
    X11_BLUE4 = PermissibleValue(
        text="X11_BLUE4",
        description="X11 Blue 4",
        meaning=HEX["00008B"])
    X11_RED1 = PermissibleValue(
        text="X11_RED1",
        description="X11 Red 1",
        meaning=HEX["FF0000"])
    X11_RED2 = PermissibleValue(
        text="X11_RED2",
        description="X11 Red 2",
        meaning=HEX["EE0000"])
    X11_RED3 = PermissibleValue(
        text="X11_RED3",
        description="X11 Red 3",
        meaning=HEX["CD0000"])
    X11_RED4 = PermissibleValue(
        text="X11_RED4",
        description="X11 Red 4",
        meaning=HEX["8B0000"])

    _defn = EnumDefinition(
        name="X11ColorEnum",
        description="X11/Unix system colors (extended set)",
    )

class ColorSpaceEnum(EnumDefinitionImpl):
    """
    Color space and model types
    """
    RGB = PermissibleValue(
        text="RGB",
        description="Red Green Blue color model")
    CMYK = PermissibleValue(
        text="CMYK",
        description="Cyan Magenta Yellow Key (black) color model")
    HSL = PermissibleValue(
        text="HSL",
        description="Hue Saturation Lightness color model")
    HSV = PermissibleValue(
        text="HSV",
        description="Hue Saturation Value color model")
    LAB = PermissibleValue(
        text="LAB",
        description="CIELAB color space")
    PANTONE = PermissibleValue(
        text="PANTONE",
        description="Pantone Matching System")
    RAL = PermissibleValue(
        text="RAL",
        description="RAL color standard")
    NCS = PermissibleValue(
        text="NCS",
        description="Natural Color System")
    MUNSELL = PermissibleValue(
        text="MUNSELL",
        description="Munsell color system")

    _defn = EnumDefinition(
        name="ColorSpaceEnum",
        description="Color space and model types",
    )

class EyeColorEnum(EnumDefinitionImpl):
    """
    Human eye color phenotypes
    """
    BROWN = PermissibleValue(
        text="BROWN",
        description="Brown eyes")
    BLUE = PermissibleValue(
        text="BLUE",
        title="Blue irides",
        description="Blue eyes",
        meaning=HP["0000635"])
    GREEN = PermissibleValue(
        text="GREEN",
        description="Green eyes")
    HAZEL = PermissibleValue(
        text="HAZEL",
        description="Hazel eyes (brown-green mix)")
    AMBER = PermissibleValue(
        text="AMBER",
        description="Amber/golden eyes")
    GRAY = PermissibleValue(
        text="GRAY",
        title="Iris hypopigmentation",
        description="Gray eyes",
        meaning=HP["0007730"])
    HETEROCHROMIA = PermissibleValue(
        text="HETEROCHROMIA",
        title="Heterochromia iridis",
        description="Different colored eyes",
        meaning=HP["0001100"])
    RED_PINK = PermissibleValue(
        text="RED_PINK",
        description="Red/pink eyes (albinism)")
    VIOLET = PermissibleValue(
        text="VIOLET",
        description="Violet eyes (extremely rare)")

    _defn = EnumDefinition(
        name="EyeColorEnum",
        description="Human eye color phenotypes",
    )

class HairColorEnum(EnumDefinitionImpl):
    """
    Human hair color phenotypes
    """
    BLACK = PermissibleValue(
        text="BLACK",
        description="Black hair")
    BROWN = PermissibleValue(
        text="BROWN",
        description="Brown hair")
    DARK_BROWN = PermissibleValue(
        text="DARK_BROWN",
        description="Dark brown hair")
    LIGHT_BROWN = PermissibleValue(
        text="LIGHT_BROWN",
        description="Light brown hair")
    BLONDE = PermissibleValue(
        text="BLONDE",
        title="Fair hair",
        description="Blonde/blond hair",
        meaning=HP["0002286"])
    DARK_BLONDE = PermissibleValue(
        text="DARK_BLONDE",
        description="Dark blonde hair")
    LIGHT_BLONDE = PermissibleValue(
        text="LIGHT_BLONDE",
        description="Light blonde hair")
    PLATINUM_BLONDE = PermissibleValue(
        text="PLATINUM_BLONDE",
        description="Platinum blonde hair")
    STRAWBERRY_BLONDE = PermissibleValue(
        text="STRAWBERRY_BLONDE",
        description="Strawberry blonde hair")
    RED = PermissibleValue(
        text="RED",
        title="Red hair",
        description="Red hair",
        meaning=HP["0002297"])
    AUBURN = PermissibleValue(
        text="AUBURN",
        description="Auburn hair (reddish-brown)")
    GINGER = PermissibleValue(
        text="GINGER",
        description="Ginger hair (orange-red)")
    GRAY = PermissibleValue(
        text="GRAY",
        title="Premature graying of hair",
        description="Gray hair",
        meaning=HP["0002216"])
    WHITE = PermissibleValue(
        text="WHITE",
        title="White hair",
        description="White hair",
        meaning=HP["0011364"])
    SILVER = PermissibleValue(
        text="SILVER",
        description="Silver hair")

    _defn = EnumDefinition(
        name="HairColorEnum",
        description="Human hair color phenotypes",
    )

class FlowerColorEnum(EnumDefinitionImpl):
    """
    Common flower colors
    """
    RED = PermissibleValue(
        text="RED",
        description="Red flowers")
    PINK = PermissibleValue(
        text="PINK",
        description="Pink flowers")
    ORANGE = PermissibleValue(
        text="ORANGE",
        description="Orange flowers")
    YELLOW = PermissibleValue(
        text="YELLOW",
        description="Yellow flowers")
    WHITE = PermissibleValue(
        text="WHITE",
        description="White flowers")
    PURPLE = PermissibleValue(
        text="PURPLE",
        description="Purple flowers")
    VIOLET = PermissibleValue(
        text="VIOLET",
        description="Violet flowers")
    BLUE = PermissibleValue(
        text="BLUE",
        description="Blue flowers")
    LAVENDER = PermissibleValue(
        text="LAVENDER",
        description="Lavender flowers")
    MAGENTA = PermissibleValue(
        text="MAGENTA",
        description="Magenta flowers")
    BURGUNDY = PermissibleValue(
        text="BURGUNDY",
        description="Burgundy/deep red flowers")
    CORAL = PermissibleValue(
        text="CORAL",
        description="Coral flowers")
    PEACH = PermissibleValue(
        text="PEACH",
        description="Peach flowers")
    CREAM = PermissibleValue(
        text="CREAM",
        description="Cream flowers")
    BICOLOR = PermissibleValue(
        text="BICOLOR",
        description="Two-colored flowers")
    MULTICOLOR = PermissibleValue(
        text="MULTICOLOR",
        description="Multi-colored flowers")

    _defn = EnumDefinition(
        name="FlowerColorEnum",
        description="Common flower colors",
    )

class AnimalCoatColorEnum(EnumDefinitionImpl):
    """
    Animal coat/fur colors
    """
    BLACK = PermissibleValue(
        text="BLACK",
        description="Black coat")
    WHITE = PermissibleValue(
        text="WHITE",
        description="White coat")
    BROWN = PermissibleValue(
        text="BROWN",
        description="Brown coat")
    TAN = PermissibleValue(
        text="TAN",
        description="Tan coat")
    CREAM = PermissibleValue(
        text="CREAM",
        description="Cream coat")
    GRAY = PermissibleValue(
        text="GRAY",
        description="Gray coat")
    RED = PermissibleValue(
        text="RED",
        description="Red/rust coat")
    GOLDEN = PermissibleValue(
        text="GOLDEN",
        description="Golden coat")
    FAWN = PermissibleValue(
        text="FAWN",
        description="Fawn coat")
    BRINDLE = PermissibleValue(
        text="BRINDLE",
        description="Brindle pattern (striped)")
    SPOTTED = PermissibleValue(
        text="SPOTTED",
        description="Spotted pattern")
    MERLE = PermissibleValue(
        text="MERLE",
        description="Merle pattern (mottled)")
    PIEBALD = PermissibleValue(
        text="PIEBALD",
        description="Piebald pattern (patches)")
    CALICO = PermissibleValue(
        text="CALICO",
        description="Calico pattern (tri-color)")
    TABBY = PermissibleValue(
        text="TABBY",
        description="Tabby pattern (striped)")
    TORTOISESHELL = PermissibleValue(
        text="TORTOISESHELL",
        description="Tortoiseshell pattern")
    ROAN = PermissibleValue(
        text="ROAN",
        description="Roan pattern (mixed white)")
    PALOMINO = PermissibleValue(
        text="PALOMINO",
        description="Palomino (golden with white mane)")
    CHESTNUT = PermissibleValue(
        text="CHESTNUT",
        description="Chestnut/sorrel")
    BAY = PermissibleValue(
        text="BAY",
        description="Bay (brown with black points)")

    _defn = EnumDefinition(
        name="AnimalCoatColorEnum",
        description="Animal coat/fur colors",
    )

class SkinToneEnum(EnumDefinitionImpl):
    """
    Human skin tone classifications (Fitzpatrick scale based)
    """
    TYPE_I = PermissibleValue(
        text="TYPE_I",
        description="Very pale white skin")
    TYPE_II = PermissibleValue(
        text="TYPE_II",
        description="Fair white skin")
    TYPE_III = PermissibleValue(
        text="TYPE_III",
        description="Light brown skin")
    TYPE_IV = PermissibleValue(
        text="TYPE_IV",
        description="Moderate brown skin")
    TYPE_V = PermissibleValue(
        text="TYPE_V",
        description="Dark brown skin")
    TYPE_VI = PermissibleValue(
        text="TYPE_VI",
        description="Very dark brown to black skin")

    _defn = EnumDefinition(
        name="SkinToneEnum",
        description="Human skin tone classifications (Fitzpatrick scale based)",
    )

class PlantLeafColorEnum(EnumDefinitionImpl):
    """
    Plant leaf colors (including seasonal changes)
    """
    GREEN = PermissibleValue(
        text="GREEN",
        description="Green leaves (healthy/summer)",
        meaning=PATO["0000320"])
    DARK_GREEN = PermissibleValue(
        text="DARK_GREEN",
        description="Dark green leaves")
    LIGHT_GREEN = PermissibleValue(
        text="LIGHT_GREEN",
        description="Light green leaves")
    YELLOW_GREEN = PermissibleValue(
        text="YELLOW_GREEN",
        description="Yellow-green leaves")
    YELLOW = PermissibleValue(
        text="YELLOW",
        description="Yellow leaves (autumn or chlorosis)",
        meaning=PATO["0000324"])
    ORANGE = PermissibleValue(
        text="ORANGE",
        description="Orange leaves (autumn)")
    RED = PermissibleValue(
        text="RED",
        description="Red leaves (autumn or certain species)",
        meaning=PATO["0000322"])
    PURPLE = PermissibleValue(
        text="PURPLE",
        description="Purple leaves (certain species)")
    BRONZE = PermissibleValue(
        text="BRONZE",
        description="Bronze leaves")
    SILVER = PermissibleValue(
        text="SILVER",
        description="Silver/gray leaves")
    VARIEGATED = PermissibleValue(
        text="VARIEGATED",
        description="Variegated leaves (multiple colors)")
    BROWN = PermissibleValue(
        text="BROWN",
        description="Brown leaves (dead/dying)")

    _defn = EnumDefinition(
        name="PlantLeafColorEnum",
        description="Plant leaf colors (including seasonal changes)",
    )

class DNABaseEnum(EnumDefinitionImpl):
    """
    Standard DNA nucleotide bases (canonical)
    """
    A = PermissibleValue(
        text="A",
        title="Adenine",
        meaning=CHEBI["16708"])
    C = PermissibleValue(
        text="C",
        title="Cytosine",
        meaning=CHEBI["16040"])
    G = PermissibleValue(
        text="G",
        title="Guanine",
        meaning=CHEBI["16235"])
    T = PermissibleValue(
        text="T",
        title="Thymine",
        meaning=CHEBI["17821"])

    _defn = EnumDefinition(
        name="DNABaseEnum",
        description="Standard DNA nucleotide bases (canonical)",
    )

class DNABaseExtendedEnum(EnumDefinitionImpl):
    """
    Extended DNA alphabet with IUPAC ambiguity codes
    """
    A = PermissibleValue(
        text="A",
        title="Adenine",
        meaning=CHEBI["16708"])
    C = PermissibleValue(
        text="C",
        title="Cytosine",
        meaning=CHEBI["16040"])
    G = PermissibleValue(
        text="G",
        title="Guanine",
        meaning=CHEBI["16235"])
    T = PermissibleValue(
        text="T",
        title="Thymine",
        meaning=CHEBI["17821"])
    R = PermissibleValue(
        text="R",
        title="Purine (A or G)")
    Y = PermissibleValue(
        text="Y",
        title="Pyrimidine (C or T)")
    S = PermissibleValue(
        text="S",
        title="Strong (G or C)")
    W = PermissibleValue(
        text="W",
        title="Weak (A or T)")
    K = PermissibleValue(
        text="K",
        title="Keto (G or T)")
    M = PermissibleValue(
        text="M",
        title="Amino (A or C)")
    B = PermissibleValue(
        text="B",
        title="Not A (C, G, or T)")
    D = PermissibleValue(
        text="D",
        title="Not C (A, G, or T)")
    H = PermissibleValue(
        text="H",
        title="Not G (A, C, or T)")
    V = PermissibleValue(
        text="V",
        title="Not T (A, C, or G)")
    N = PermissibleValue(
        text="N",
        title="Any nucleotide (A, C, G, or T)")
    GAP = PermissibleValue(
        text="GAP",
        title="Gap character")

    _defn = EnumDefinition(
        name="DNABaseExtendedEnum",
        description="Extended DNA alphabet with IUPAC ambiguity codes",
    )

class RNABaseEnum(EnumDefinitionImpl):
    """
    Standard RNA nucleotide bases (canonical)
    """
    A = PermissibleValue(
        text="A",
        title="Adenine",
        meaning=CHEBI["16708"])
    C = PermissibleValue(
        text="C",
        title="Cytosine",
        meaning=CHEBI["16040"])
    G = PermissibleValue(
        text="G",
        title="Guanine",
        meaning=CHEBI["16235"])
    U = PermissibleValue(
        text="U",
        title="Uracil",
        meaning=CHEBI["17568"])

    _defn = EnumDefinition(
        name="RNABaseEnum",
        description="Standard RNA nucleotide bases (canonical)",
    )

class RNABaseExtendedEnum(EnumDefinitionImpl):
    """
    Extended RNA alphabet with IUPAC ambiguity codes
    """
    A = PermissibleValue(
        text="A",
        title="Adenine",
        meaning=CHEBI["16708"])
    C = PermissibleValue(
        text="C",
        title="Cytosine",
        meaning=CHEBI["16040"])
    G = PermissibleValue(
        text="G",
        title="Guanine",
        meaning=CHEBI["16235"])
    U = PermissibleValue(
        text="U",
        title="Uracil",
        meaning=CHEBI["17568"])
    R = PermissibleValue(
        text="R",
        title="Purine (A or G)")
    Y = PermissibleValue(
        text="Y",
        title="Pyrimidine (C or U)")
    S = PermissibleValue(
        text="S",
        title="Strong (G or C)")
    W = PermissibleValue(
        text="W",
        title="Weak (A or U)")
    K = PermissibleValue(
        text="K",
        title="Keto (G or U)")
    M = PermissibleValue(
        text="M",
        title="Amino (A or C)")
    B = PermissibleValue(
        text="B",
        title="Not A (C, G, or U)")
    D = PermissibleValue(
        text="D",
        title="Not C (A, G, or U)")
    H = PermissibleValue(
        text="H",
        title="Not G (A, C, or U)")
    V = PermissibleValue(
        text="V",
        title="Not U (A, C, or G)")
    N = PermissibleValue(
        text="N",
        title="Any nucleotide (A, C, G, or U)")
    GAP = PermissibleValue(
        text="GAP",
        title="Gap character")

    _defn = EnumDefinition(
        name="RNABaseExtendedEnum",
        description="Extended RNA alphabet with IUPAC ambiguity codes",
    )

class AminoAcidEnum(EnumDefinitionImpl):
    """
    Standard amino acid single letter codes
    """
    A = PermissibleValue(
        text="A",
        title="Alanine",
        meaning=CHEBI["16449"])
    C = PermissibleValue(
        text="C",
        title="Cysteine",
        meaning=CHEBI["17561"])
    D = PermissibleValue(
        text="D",
        title="Aspartic acid",
        meaning=CHEBI["17053"])
    E = PermissibleValue(
        text="E",
        title="Glutamic acid",
        meaning=CHEBI["16015"])
    F = PermissibleValue(
        text="F",
        title="Phenylalanine",
        meaning=CHEBI["17295"])
    G = PermissibleValue(
        text="G",
        title="Glycine",
        meaning=CHEBI["15428"])
    H = PermissibleValue(
        text="H",
        title="Histidine",
        meaning=CHEBI["15971"])
    I = PermissibleValue(
        text="I",
        title="Isoleucine",
        meaning=CHEBI["17191"])
    K = PermissibleValue(
        text="K",
        title="Lysine",
        meaning=CHEBI["18019"])
    L = PermissibleValue(
        text="L",
        title="Leucine",
        meaning=CHEBI["15603"])
    M = PermissibleValue(
        text="M",
        title="Methionine",
        meaning=CHEBI["16643"])
    N = PermissibleValue(
        text="N",
        title="Asparagine",
        meaning=CHEBI["17196"])
    P = PermissibleValue(
        text="P",
        title="Proline",
        meaning=CHEBI["17203"])
    Q = PermissibleValue(
        text="Q",
        title="Glutamine",
        meaning=CHEBI["18050"])
    R = PermissibleValue(
        text="R",
        title="Arginine",
        meaning=CHEBI["16467"])
    S = PermissibleValue(
        text="S",
        title="Serine",
        meaning=CHEBI["17115"])
    T = PermissibleValue(
        text="T",
        title="Threonine",
        meaning=CHEBI["16857"])
    V = PermissibleValue(
        text="V",
        title="Valine",
        meaning=CHEBI["16414"])
    W = PermissibleValue(
        text="W",
        title="Tryptophan",
        meaning=CHEBI["16828"])
    Y = PermissibleValue(
        text="Y",
        title="Tyrosine",
        meaning=CHEBI["17895"])

    _defn = EnumDefinition(
        name="AminoAcidEnum",
        description="Standard amino acid single letter codes",
    )

class AminoAcidExtendedEnum(EnumDefinitionImpl):
    """
    Extended amino acid alphabet with ambiguity codes and special characters
    """
    A = PermissibleValue(
        text="A",
        title="Alanine",
        meaning=CHEBI["16449"])
    C = PermissibleValue(
        text="C",
        title="Cysteine",
        meaning=CHEBI["17561"])
    D = PermissibleValue(
        text="D",
        title="Aspartic acid",
        meaning=CHEBI["17053"])
    E = PermissibleValue(
        text="E",
        title="Glutamic acid",
        meaning=CHEBI["16015"])
    F = PermissibleValue(
        text="F",
        title="Phenylalanine",
        meaning=CHEBI["17295"])
    G = PermissibleValue(
        text="G",
        title="Glycine",
        meaning=CHEBI["15428"])
    H = PermissibleValue(
        text="H",
        title="Histidine",
        meaning=CHEBI["15971"])
    I = PermissibleValue(
        text="I",
        title="Isoleucine",
        meaning=CHEBI["17191"])
    K = PermissibleValue(
        text="K",
        title="Lysine",
        meaning=CHEBI["18019"])
    L = PermissibleValue(
        text="L",
        title="Leucine",
        meaning=CHEBI["15603"])
    M = PermissibleValue(
        text="M",
        title="Methionine",
        meaning=CHEBI["16643"])
    N = PermissibleValue(
        text="N",
        title="Asparagine",
        meaning=CHEBI["17196"])
    P = PermissibleValue(
        text="P",
        title="Proline",
        meaning=CHEBI["17203"])
    Q = PermissibleValue(
        text="Q",
        title="Glutamine",
        meaning=CHEBI["18050"])
    R = PermissibleValue(
        text="R",
        title="Arginine",
        meaning=CHEBI["16467"])
    S = PermissibleValue(
        text="S",
        title="Serine",
        meaning=CHEBI["17115"])
    T = PermissibleValue(
        text="T",
        title="Threonine",
        meaning=CHEBI["16857"])
    V = PermissibleValue(
        text="V",
        title="Valine",
        meaning=CHEBI["16414"])
    W = PermissibleValue(
        text="W",
        title="Tryptophan",
        meaning=CHEBI["16828"])
    Y = PermissibleValue(
        text="Y",
        title="Tyrosine",
        meaning=CHEBI["17895"])
    B = PermissibleValue(
        text="B",
        title="Aspartic acid")
    Z = PermissibleValue(
        text="Z",
        title="Glutamic acid")
    J = PermissibleValue(
        text="J",
        title="Leucine")
    X = PermissibleValue(
        text="X",
        title="Any amino acid")
    STOP = PermissibleValue(
        text="STOP",
        title="Translation stop/termination")
    GAP = PermissibleValue(
        text="GAP",
        title="Gap character")
    U = PermissibleValue(
        text="U",
        title="Selenocysteine",
        meaning=CHEBI["16633"])
    O = PermissibleValue(
        text="O",
        title="Pyrrolysine (22nd amino acid)",
        meaning=CHEBI["21860"])

    _defn = EnumDefinition(
        name="AminoAcidExtendedEnum",
        description="Extended amino acid alphabet with ambiguity codes and special characters",
    )

class CodonEnum(EnumDefinitionImpl):
    """
    Standard genetic code codons (DNA)
    """
    TTT = PermissibleValue(
        text="TTT",
        title="Phenylalanine codon")
    TTC = PermissibleValue(
        text="TTC",
        title="Phenylalanine codon")
    TTA = PermissibleValue(
        text="TTA",
        title="Leucine codon")
    TTG = PermissibleValue(
        text="TTG",
        title="Leucine codon")
    CTT = PermissibleValue(
        text="CTT",
        title="Leucine codon")
    CTC = PermissibleValue(
        text="CTC",
        title="Leucine codon")
    CTA = PermissibleValue(
        text="CTA",
        title="Leucine codon")
    CTG = PermissibleValue(
        text="CTG",
        title="Leucine codon")
    ATT = PermissibleValue(
        text="ATT",
        title="Isoleucine codon")
    ATC = PermissibleValue(
        text="ATC",
        title="Isoleucine codon")
    ATA = PermissibleValue(
        text="ATA",
        title="Isoleucine codon")
    ATG = PermissibleValue(
        text="ATG",
        title="Methionine codon (start codon)")
    GTT = PermissibleValue(
        text="GTT",
        title="Valine codon")
    GTC = PermissibleValue(
        text="GTC",
        title="Valine codon")
    GTA = PermissibleValue(
        text="GTA",
        title="Valine codon")
    GTG = PermissibleValue(
        text="GTG",
        title="Valine codon")
    TCT = PermissibleValue(
        text="TCT",
        title="Serine codon")
    TCC = PermissibleValue(
        text="TCC",
        title="Serine codon")
    TCA = PermissibleValue(
        text="TCA",
        title="Serine codon")
    TCG = PermissibleValue(
        text="TCG",
        title="Serine codon")
    AGT = PermissibleValue(
        text="AGT",
        title="Serine codon")
    AGC = PermissibleValue(
        text="AGC",
        title="Serine codon")
    CCT = PermissibleValue(
        text="CCT",
        title="Proline codon")
    CCC = PermissibleValue(
        text="CCC",
        title="Proline codon")
    CCA = PermissibleValue(
        text="CCA",
        title="Proline codon")
    CCG = PermissibleValue(
        text="CCG",
        title="Proline codon")
    ACT = PermissibleValue(
        text="ACT",
        title="Threonine codon")
    ACC = PermissibleValue(
        text="ACC",
        title="Threonine codon")
    ACA = PermissibleValue(
        text="ACA",
        title="Threonine codon")
    ACG = PermissibleValue(
        text="ACG",
        title="Threonine codon")
    GCT = PermissibleValue(
        text="GCT",
        title="Alanine codon")
    GCC = PermissibleValue(
        text="GCC",
        title="Alanine codon")
    GCA = PermissibleValue(
        text="GCA",
        title="Alanine codon")
    GCG = PermissibleValue(
        text="GCG",
        title="Alanine codon")
    TAT = PermissibleValue(
        text="TAT",
        title="Tyrosine codon")
    TAC = PermissibleValue(
        text="TAC",
        title="Tyrosine codon")
    TAA = PermissibleValue(
        text="TAA",
        title="Stop codon (ochre)")
    TAG = PermissibleValue(
        text="TAG",
        title="Stop codon (amber)")
    TGA = PermissibleValue(
        text="TGA",
        title="Stop codon (opal/umber)")
    CAT = PermissibleValue(
        text="CAT",
        title="Histidine codon")
    CAC = PermissibleValue(
        text="CAC",
        title="Histidine codon")
    CAA = PermissibleValue(
        text="CAA",
        title="Glutamine codon")
    CAG = PermissibleValue(
        text="CAG",
        title="Glutamine codon")
    AAT = PermissibleValue(
        text="AAT",
        title="Asparagine codon")
    AAC = PermissibleValue(
        text="AAC",
        title="Asparagine codon")
    AAA = PermissibleValue(
        text="AAA",
        title="Lysine codon")
    AAG = PermissibleValue(
        text="AAG",
        title="Lysine codon")
    GAT = PermissibleValue(
        text="GAT",
        title="Aspartic acid codon")
    GAC = PermissibleValue(
        text="GAC",
        title="Aspartic acid codon")
    GAA = PermissibleValue(
        text="GAA",
        title="Glutamic acid codon")
    GAG = PermissibleValue(
        text="GAG",
        title="Glutamic acid codon")
    TGT = PermissibleValue(
        text="TGT",
        title="Cysteine codon")
    TGC = PermissibleValue(
        text="TGC",
        title="Cysteine codon")
    TGG = PermissibleValue(
        text="TGG",
        title="Tryptophan codon")
    CGT = PermissibleValue(
        text="CGT",
        title="Arginine codon")
    CGC = PermissibleValue(
        text="CGC",
        title="Arginine codon")
    CGA = PermissibleValue(
        text="CGA",
        title="Arginine codon")
    CGG = PermissibleValue(
        text="CGG",
        title="Arginine codon")
    AGA = PermissibleValue(
        text="AGA",
        title="Arginine codon")
    AGG = PermissibleValue(
        text="AGG",
        title="Arginine codon")
    GGT = PermissibleValue(
        text="GGT",
        title="Glycine codon")
    GGC = PermissibleValue(
        text="GGC",
        title="Glycine codon")
    GGA = PermissibleValue(
        text="GGA",
        title="Glycine codon")
    GGG = PermissibleValue(
        text="GGG",
        title="Glycine codon")

    _defn = EnumDefinition(
        name="CodonEnum",
        description="Standard genetic code codons (DNA)",
    )

class NucleotideModificationEnum(EnumDefinitionImpl):
    """
    Common nucleotide modifications
    """
    FIVE_METHYL_C = PermissibleValue(
        text="FIVE_METHYL_C",
        title="5-methylcytosine",
        description="5-methylcytosine",
        meaning=CHEBI["27551"])
    SIX_METHYL_A = PermissibleValue(
        text="SIX_METHYL_A",
        title="N(6)-methyladenosine",
        description="N6-methyladenosine",
        meaning=CHEBI["21891"])
    PSEUDOURIDINE = PermissibleValue(
        text="PSEUDOURIDINE",
        description="Pseudouridine",
        meaning=CHEBI["17802"])
    INOSINE = PermissibleValue(
        text="INOSINE",
        description="Inosine",
        meaning=CHEBI["17596"])
    DIHYDROURIDINE = PermissibleValue(
        text="DIHYDROURIDINE",
        title="dihydrouridine",
        description="Dihydrouridine",
        meaning=CHEBI["23774"])
    SEVEN_METHYL_G = PermissibleValue(
        text="SEVEN_METHYL_G",
        title="7-methylguanosine",
        description="7-methylguanosine",
        meaning=CHEBI["20794"])
    FIVE_HYDROXY_METHYL_C = PermissibleValue(
        text="FIVE_HYDROXY_METHYL_C",
        title="5-(hydroxymethyl)cytosine",
        description="5-hydroxymethylcytosine",
        meaning=CHEBI["76792"])
    EIGHT_OXO_G = PermissibleValue(
        text="EIGHT_OXO_G",
        title="8-oxoguanine",
        description="8-oxoguanine",
        meaning=CHEBI["44605"])

    _defn = EnumDefinition(
        name="NucleotideModificationEnum",
        description="Common nucleotide modifications",
    )

class SequenceQualityEnum(EnumDefinitionImpl):
    """
    Sequence quality indicators (Phred scores)
    """
    Q0 = PermissibleValue(
        text="Q0",
        description="Phred quality 0 (100% error probability)")
    Q10 = PermissibleValue(
        text="Q10",
        description="Phred quality 10 (10% error probability)")
    Q20 = PermissibleValue(
        text="Q20",
        description="Phred quality 20 (1% error probability)")
    Q30 = PermissibleValue(
        text="Q30",
        description="Phred quality 30 (0.1% error probability)")
    Q40 = PermissibleValue(
        text="Q40",
        description="Phred quality 40 (0.01% error probability)")
    Q50 = PermissibleValue(
        text="Q50",
        description="Phred quality 50 (0.001% error probability)")
    Q60 = PermissibleValue(
        text="Q60",
        description="Phred quality 60 (0.0001% error probability)")

    _defn = EnumDefinition(
        name="SequenceQualityEnum",
        description="Sequence quality indicators (Phred scores)",
    )

class IUPACNucleotideCode(EnumDefinitionImpl):
    """
    Complete IUPAC nucleotide codes including ambiguous bases for DNA/RNA sequences.
    Used in FASTA and other sequence formats to represent uncertain nucleotides.
    """
    A = PermissibleValue(
        text="A",
        title="A",
        description="Adenine")
    T = PermissibleValue(
        text="T",
        title="T",
        description="Thymine (DNA)")
    U = PermissibleValue(
        text="U",
        title="U",
        description="Uracil (RNA)")
    G = PermissibleValue(
        text="G",
        title="G",
        description="Guanine")
    C = PermissibleValue(
        text="C",
        title="C",
        description="Cytosine")
    R = PermissibleValue(
        text="R",
        title="R",
        description="Purine (A or G)")
    Y = PermissibleValue(
        text="Y",
        title="Y",
        description="Pyrimidine (C or T/U)")
    S = PermissibleValue(
        text="S",
        description="Strong interaction (G or C)")
    W = PermissibleValue(
        text="W",
        description="Weak interaction (A or T/U)")
    K = PermissibleValue(
        text="K",
        description="Keto (G or T/U)")
    M = PermissibleValue(
        text="M",
        description="Amino (A or C)")
    B = PermissibleValue(
        text="B",
        description="Not A (C or G or T/U)")
    D = PermissibleValue(
        text="D",
        description="Not C (A or G or T/U)")
    H = PermissibleValue(
        text="H",
        description="Not G (A or C or T/U)")
    V = PermissibleValue(
        text="V",
        description="Not T/U (A or C or G)")
    N = PermissibleValue(
        text="N",
        description="Any nucleotide (A or C or G or T/U)")
    GAP = PermissibleValue(
        text="GAP",
        title="-",
        description="Gap or deletion in alignment")

    _defn = EnumDefinition(
        name="IUPACNucleotideCode",
        description="""Complete IUPAC nucleotide codes including ambiguous bases for DNA/RNA sequences.
Used in FASTA and other sequence formats to represent uncertain nucleotides.""",
    )

class StandardAminoAcid(EnumDefinitionImpl):
    """
    The 20 standard proteinogenic amino acids with IUPAC single-letter codes
    """
    A = PermissibleValue(
        text="A",
        title="A",
        description="Alanine")
    R = PermissibleValue(
        text="R",
        title="R",
        description="Arginine")
    N = PermissibleValue(
        text="N",
        title="N",
        description="Asparagine")
    D = PermissibleValue(
        text="D",
        title="D",
        description="Aspartic acid")
    C = PermissibleValue(
        text="C",
        title="C",
        description="Cysteine")
    E = PermissibleValue(
        text="E",
        title="E",
        description="Glutamic acid")
    Q = PermissibleValue(
        text="Q",
        title="Q",
        description="Glutamine")
    G = PermissibleValue(
        text="G",
        title="G",
        description="Glycine")
    H = PermissibleValue(
        text="H",
        title="H",
        description="Histidine")
    I = PermissibleValue(
        text="I",
        title="I",
        description="Isoleucine")
    L = PermissibleValue(
        text="L",
        title="L",
        description="Leucine")
    K = PermissibleValue(
        text="K",
        title="K",
        description="Lysine")
    M = PermissibleValue(
        text="M",
        title="M",
        description="Methionine")
    F = PermissibleValue(
        text="F",
        title="F",
        description="Phenylalanine")
    P = PermissibleValue(
        text="P",
        title="P",
        description="Proline")
    S = PermissibleValue(
        text="S",
        title="S",
        description="Serine")
    T = PermissibleValue(
        text="T",
        title="T",
        description="Threonine")
    W = PermissibleValue(
        text="W",
        title="W",
        description="Tryptophan")
    Y = PermissibleValue(
        text="Y",
        title="Y",
        description="Tyrosine")
    V = PermissibleValue(
        text="V",
        title="V",
        description="Valine")

    _defn = EnumDefinition(
        name="StandardAminoAcid",
        description="The 20 standard proteinogenic amino acids with IUPAC single-letter codes",
    )

class IUPACAminoAcidCode(EnumDefinitionImpl):
    """
    Complete IUPAC amino acid codes including standard amino acids,
    rare amino acids, and ambiguity codes
    """
    A = PermissibleValue(
        text="A",
        title="A",
        description="Alanine")
    R = PermissibleValue(
        text="R",
        title="R",
        description="Arginine")
    N = PermissibleValue(
        text="N",
        title="N",
        description="Asparagine")
    D = PermissibleValue(
        text="D",
        title="D",
        description="Aspartic acid")
    C = PermissibleValue(
        text="C",
        title="C",
        description="Cysteine")
    E = PermissibleValue(
        text="E",
        title="E",
        description="Glutamic acid")
    Q = PermissibleValue(
        text="Q",
        title="Q",
        description="Glutamine")
    G = PermissibleValue(
        text="G",
        title="G",
        description="Glycine")
    H = PermissibleValue(
        text="H",
        title="H",
        description="Histidine")
    I = PermissibleValue(
        text="I",
        title="I",
        description="Isoleucine")
    L = PermissibleValue(
        text="L",
        title="L",
        description="Leucine")
    K = PermissibleValue(
        text="K",
        title="K",
        description="Lysine")
    M = PermissibleValue(
        text="M",
        title="M",
        description="Methionine")
    F = PermissibleValue(
        text="F",
        title="F",
        description="Phenylalanine")
    P = PermissibleValue(
        text="P",
        title="P",
        description="Proline")
    S = PermissibleValue(
        text="S",
        title="S",
        description="Serine")
    T = PermissibleValue(
        text="T",
        title="T",
        description="Threonine")
    W = PermissibleValue(
        text="W",
        title="W",
        description="Tryptophan")
    Y = PermissibleValue(
        text="Y",
        title="Y",
        description="Tyrosine")
    V = PermissibleValue(
        text="V",
        title="V",
        description="Valine")
    U = PermissibleValue(
        text="U",
        title="U",
        description="Selenocysteine (21st amino acid)")
    O = PermissibleValue(
        text="O",
        title="O",
        description="Pyrrolysine (22nd amino acid)")
    B = PermissibleValue(
        text="B",
        description="Asparagine or Aspartic acid (N or D)")
    Z = PermissibleValue(
        text="Z",
        description="Glutamine or Glutamic acid (Q or E)")
    J = PermissibleValue(
        text="J",
        description="Leucine or Isoleucine (L or I)")
    X = PermissibleValue(
        text="X",
        description="Any amino acid")
    STOP = PermissibleValue(
        text="STOP",
        title="*",
        description="Translation stop codon")
    GAP = PermissibleValue(
        text="GAP",
        title="-",
        description="Gap or deletion in alignment")

    _defn = EnumDefinition(
        name="IUPACAminoAcidCode",
        description="""Complete IUPAC amino acid codes including standard amino acids,
rare amino acids, and ambiguity codes""",
    )

class SequenceAlphabet(EnumDefinitionImpl):
    """
    Types of sequence alphabets used in bioinformatics
    """
    DNA = PermissibleValue(
        text="DNA",
        description="Deoxyribonucleic acid alphabet (A, T, G, C)")
    RNA = PermissibleValue(
        text="RNA",
        description="Ribonucleic acid alphabet (A, U, G, C)")
    PROTEIN = PermissibleValue(
        text="PROTEIN",
        description="Protein/amino acid alphabet (20 standard AAs)")
    IUPAC_DNA = PermissibleValue(
        text="IUPAC_DNA",
        description="Extended DNA with IUPAC ambiguity codes")
    IUPAC_RNA = PermissibleValue(
        text="IUPAC_RNA",
        description="Extended RNA with IUPAC ambiguity codes")
    IUPAC_PROTEIN = PermissibleValue(
        text="IUPAC_PROTEIN",
        description="Extended protein with ambiguity codes and rare AAs")
    RESTRICTED_DNA = PermissibleValue(
        text="RESTRICTED_DNA",
        description="Unambiguous DNA bases only (A, T, G, C)")
    RESTRICTED_RNA = PermissibleValue(
        text="RESTRICTED_RNA",
        description="Unambiguous RNA bases only (A, U, G, C)")
    BINARY = PermissibleValue(
        text="BINARY",
        description="Binary encoding of sequences")

    _defn = EnumDefinition(
        name="SequenceAlphabet",
        description="Types of sequence alphabets used in bioinformatics",
    )

class SequenceQualityEncoding(EnumDefinitionImpl):
    """
    Quality score encoding standards used in FASTQ files and sequencing data.
    Different platforms and software versions use different ASCII offsets.
    """
    SANGER = PermissibleValue(
        text="SANGER",
        description="Sanger/Phred+33 (PHRED scores, ASCII offset 33)")
    SOLEXA = PermissibleValue(
        text="SOLEXA",
        description="Solexa+64 (Solexa scores, ASCII offset 64)")
    ILLUMINA_1_3 = PermissibleValue(
        text="ILLUMINA_1_3",
        description="Illumina 1.3+ (PHRED+64, ASCII offset 64)")
    ILLUMINA_1_5 = PermissibleValue(
        text="ILLUMINA_1_5",
        description="Illumina 1.5+ (PHRED+64, special handling for 0-2)")
    ILLUMINA_1_8 = PermissibleValue(
        text="ILLUMINA_1_8",
        description="Illumina 1.8+ (PHRED+33, modern standard)")

    _defn = EnumDefinition(
        name="SequenceQualityEncoding",
        description="""Quality score encoding standards used in FASTQ files and sequencing data.
Different platforms and software versions use different ASCII offsets.""",
    )

class GeneticCodeTable(EnumDefinitionImpl):
    """
    NCBI genetic code translation tables for different organisms.
    Table 1 is the universal genetic code used by most organisms.
    """
    TABLE_1 = PermissibleValue(
        text="TABLE_1",
        description="Standard genetic code (universal)")
    TABLE_2 = PermissibleValue(
        text="TABLE_2",
        description="Vertebrate mitochondrial code")
    TABLE_3 = PermissibleValue(
        text="TABLE_3",
        description="Yeast mitochondrial code")
    TABLE_4 = PermissibleValue(
        text="TABLE_4",
        description="Mold, protozoan, coelenterate mitochondrial")
    TABLE_5 = PermissibleValue(
        text="TABLE_5",
        description="Invertebrate mitochondrial code")
    TABLE_6 = PermissibleValue(
        text="TABLE_6",
        description="Ciliate, dasycladacean, hexamita nuclear code")
    TABLE_9 = PermissibleValue(
        text="TABLE_9",
        description="Echinoderm and flatworm mitochondrial code")
    TABLE_10 = PermissibleValue(
        text="TABLE_10",
        description="Euplotid nuclear code")
    TABLE_11 = PermissibleValue(
        text="TABLE_11",
        description="Bacterial, archaeal and plant plastid code")
    TABLE_12 = PermissibleValue(
        text="TABLE_12",
        description="Alternative yeast nuclear code")
    TABLE_13 = PermissibleValue(
        text="TABLE_13",
        description="Ascidian mitochondrial code")
    TABLE_14 = PermissibleValue(
        text="TABLE_14",
        description="Alternative flatworm mitochondrial code")
    TABLE_16 = PermissibleValue(
        text="TABLE_16",
        description="Chlorophycean mitochondrial code")
    TABLE_21 = PermissibleValue(
        text="TABLE_21",
        description="Trematode mitochondrial code")
    TABLE_22 = PermissibleValue(
        text="TABLE_22",
        description="Scenedesmus obliquus mitochondrial code")
    TABLE_23 = PermissibleValue(
        text="TABLE_23",
        description="Thraustochytrium mitochondrial code")
    TABLE_24 = PermissibleValue(
        text="TABLE_24",
        description="Rhabdopleuridae mitochondrial code")
    TABLE_25 = PermissibleValue(
        text="TABLE_25",
        description="Candidate division SR1 and gracilibacteria code")
    TABLE_26 = PermissibleValue(
        text="TABLE_26",
        description="Pachysolen tannophilus nuclear code")
    TABLE_27 = PermissibleValue(
        text="TABLE_27",
        description="Karyorelict nuclear code")
    TABLE_28 = PermissibleValue(
        text="TABLE_28",
        description="Condylostoma nuclear code")
    TABLE_29 = PermissibleValue(
        text="TABLE_29",
        description="Mesodinium nuclear code")
    TABLE_30 = PermissibleValue(
        text="TABLE_30",
        description="Peritrich nuclear code")
    TABLE_31 = PermissibleValue(
        text="TABLE_31",
        description="Blastocrithidia nuclear code")

    _defn = EnumDefinition(
        name="GeneticCodeTable",
        description="""NCBI genetic code translation tables for different organisms.
Table 1 is the universal genetic code used by most organisms.""",
    )

class SequenceStrand(EnumDefinitionImpl):
    """
    Strand orientation for nucleic acid sequences
    """
    PLUS = PermissibleValue(
        text="PLUS",
        title="PLUS",
        description="Plus/forward/sense strand (5' to 3')")
    MINUS = PermissibleValue(
        text="MINUS",
        title="MINUS",
        description="Minus/reverse/antisense strand (3' to 5')")
    BOTH = PermissibleValue(
        text="BOTH",
        description="Both strands")
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="Strand not specified or unknown")

    _defn = EnumDefinition(
        name="SequenceStrand",
        description="Strand orientation for nucleic acid sequences",
    )

class SequenceTopology(EnumDefinitionImpl):
    """
    Topological structure of nucleic acid molecules
    """
    LINEAR = PermissibleValue(
        text="LINEAR",
        description="Linear sequence molecule",
        meaning=SO["0000987"])
    CIRCULAR = PermissibleValue(
        text="CIRCULAR",
        description="Circular sequence molecule",
        meaning=SO["0000988"])
    BRANCHED = PermissibleValue(
        text="BRANCHED",
        description="Branched sequence structure")
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="Topology not specified")

    _defn = EnumDefinition(
        name="SequenceTopology",
        description="Topological structure of nucleic acid molecules",
    )

class SequenceModality(EnumDefinitionImpl):
    """
    Types of sequence data based on experimental method
    """
    SINGLE_CELL = PermissibleValue(
        text="SINGLE_CELL",
        description="Single-cell sequencing data")
    BULK = PermissibleValue(
        text="BULK",
        description="Bulk/population sequencing data")
    SPATIAL = PermissibleValue(
        text="SPATIAL",
        description="Spatially-resolved sequencing")
    LONG_READ = PermissibleValue(
        text="LONG_READ",
        description="Long-read sequencing (PacBio, Oxford Nanopore)")
    SHORT_READ = PermissibleValue(
        text="SHORT_READ",
        description="Short-read sequencing (Illumina)")
    PAIRED_END = PermissibleValue(
        text="PAIRED_END",
        description="Paired-end sequencing reads")
    SINGLE_END = PermissibleValue(
        text="SINGLE_END",
        description="Single-end sequencing reads")
    MATE_PAIR = PermissibleValue(
        text="MATE_PAIR",
        description="Mate-pair sequencing libraries")

    _defn = EnumDefinition(
        name="SequenceModality",
        description="Types of sequence data based on experimental method",
    )

class SequencingPlatform(EnumDefinitionImpl):
    """
    Major DNA/RNA sequencing platforms and instruments used in genomics research
    """
    ILLUMINA_HISEQ_2000 = PermissibleValue(
        text="ILLUMINA_HISEQ_2000",
        description="Illumina HiSeq 2000",
        meaning=OBI["0002001"])
    ILLUMINA_HISEQ_2500 = PermissibleValue(
        text="ILLUMINA_HISEQ_2500",
        description="Illumina HiSeq 2500",
        meaning=OBI["0002002"])
    ILLUMINA_HISEQ_3000 = PermissibleValue(
        text="ILLUMINA_HISEQ_3000",
        description="Illumina HiSeq 3000",
        meaning=OBI["0002048"])
    ILLUMINA_HISEQ_4000 = PermissibleValue(
        text="ILLUMINA_HISEQ_4000",
        description="Illumina HiSeq 4000",
        meaning=OBI["0002049"])
    ILLUMINA_HISEQ_X = PermissibleValue(
        text="ILLUMINA_HISEQ_X",
        description="Illumina HiSeq X",
        meaning=OBI["0002129"])
    ILLUMINA_NOVASEQ_6000 = PermissibleValue(
        text="ILLUMINA_NOVASEQ_6000",
        description="Illumina NovaSeq 6000",
        meaning=OBI["0002630"])
    ILLUMINA_NEXTSEQ_500 = PermissibleValue(
        text="ILLUMINA_NEXTSEQ_500",
        description="Illumina NextSeq 500",
        meaning=OBI["0002021"])
    ILLUMINA_NEXTSEQ_550 = PermissibleValue(
        text="ILLUMINA_NEXTSEQ_550",
        description="Illumina NextSeq 550",
        meaning=OBI["0003387"])
    ILLUMINA_NEXTSEQ_1000 = PermissibleValue(
        text="ILLUMINA_NEXTSEQ_1000",
        description="Illumina NextSeq 1000")
    ILLUMINA_NEXTSEQ_2000 = PermissibleValue(
        text="ILLUMINA_NEXTSEQ_2000",
        description="Illumina NextSeq 2000")
    ILLUMINA_MISEQ = PermissibleValue(
        text="ILLUMINA_MISEQ",
        description="Illumina MiSeq",
        meaning=OBI["0002003"])
    ILLUMINA_ISEQ_100 = PermissibleValue(
        text="ILLUMINA_ISEQ_100",
        description="Illumina iSeq 100")
    PACBIO_RS = PermissibleValue(
        text="PACBIO_RS",
        description="PacBio RS")
    PACBIO_RS_II = PermissibleValue(
        text="PACBIO_RS_II",
        description="PacBio RS II",
        meaning=OBI["0002012"])
    PACBIO_SEQUEL = PermissibleValue(
        text="PACBIO_SEQUEL",
        description="PacBio Sequel",
        meaning=OBI["0002632"])
    PACBIO_SEQUEL_II = PermissibleValue(
        text="PACBIO_SEQUEL_II",
        description="PacBio Sequel II",
        meaning=OBI["0002633"])
    PACBIO_REVIO = PermissibleValue(
        text="PACBIO_REVIO",
        description="PacBio Revio")
    NANOPORE_MINION = PermissibleValue(
        text="NANOPORE_MINION",
        description="Oxford Nanopore MinION",
        meaning=OBI["0002750"])
    NANOPORE_GRIDION = PermissibleValue(
        text="NANOPORE_GRIDION",
        description="Oxford Nanopore GridION",
        meaning=OBI["0002751"])
    NANOPORE_PROMETHION = PermissibleValue(
        text="NANOPORE_PROMETHION",
        description="Oxford Nanopore PromethION",
        meaning=OBI["0002752"])
    NANOPORE_FLONGLE = PermissibleValue(
        text="NANOPORE_FLONGLE",
        description="Oxford Nanopore Flongle")
    ELEMENT_AVITI = PermissibleValue(
        text="ELEMENT_AVITI",
        description="Element Biosciences AVITI")
    MGI_DNBSEQ_T7 = PermissibleValue(
        text="MGI_DNBSEQ_T7",
        description="MGI DNBSEQ-T7")
    MGI_DNBSEQ_G400 = PermissibleValue(
        text="MGI_DNBSEQ_G400",
        description="MGI DNBSEQ-G400")
    MGI_DNBSEQ_G50 = PermissibleValue(
        text="MGI_DNBSEQ_G50",
        description="MGI DNBSEQ-G50")
    SANGER_SEQUENCING = PermissibleValue(
        text="SANGER_SEQUENCING",
        description="Sanger chain termination sequencing",
        meaning=OBI["0000695"])
    ROCHE_454_GS = PermissibleValue(
        text="ROCHE_454_GS",
        description="Roche 454 Genome Sequencer",
        meaning=OBI["0000702"])
    LIFE_TECHNOLOGIES_ION_TORRENT = PermissibleValue(
        text="LIFE_TECHNOLOGIES_ION_TORRENT",
        description="Life Technologies Ion Torrent")
    ABI_SOLID = PermissibleValue(
        text="ABI_SOLID",
        description="ABI SOLiD")

    _defn = EnumDefinition(
        name="SequencingPlatform",
        description="Major DNA/RNA sequencing platforms and instruments used in genomics research",
    )

class SequencingChemistry(EnumDefinitionImpl):
    """
    Fundamental chemical methods used for DNA/RNA sequencing
    """
    SEQUENCING_BY_SYNTHESIS = PermissibleValue(
        text="SEQUENCING_BY_SYNTHESIS",
        title="SEQUENCING_BY_SYNTHESIS",
        description="Sequencing by synthesis (Illumina)",
        meaning=OBI["0000734"])
    SINGLE_MOLECULE_REAL_TIME = PermissibleValue(
        text="SINGLE_MOLECULE_REAL_TIME",
        title="SINGLE_MOLECULE_REAL_TIME",
        description="Single molecule real-time sequencing (PacBio)")
    NANOPORE_SEQUENCING = PermissibleValue(
        text="NANOPORE_SEQUENCING",
        title="NANOPORE_SEQUENCING",
        description="Nanopore sequencing (Oxford Nanopore)")
    PYROSEQUENCING = PermissibleValue(
        text="PYROSEQUENCING",
        title="PYROSEQUENCING",
        description="Pyrosequencing (454)")
    SEQUENCING_BY_LIGATION = PermissibleValue(
        text="SEQUENCING_BY_LIGATION",
        title="SEQUENCING_BY_LIGATION",
        description="Sequencing by ligation (SOLiD)",
        meaning=OBI["0000723"])
    CHAIN_TERMINATION = PermissibleValue(
        text="CHAIN_TERMINATION",
        title="CHAIN_TERMINATION",
        description="Chain termination method (Sanger)",
        meaning=OBI["0000695"])
    SEMICONDUCTOR_SEQUENCING = PermissibleValue(
        text="SEMICONDUCTOR_SEQUENCING",
        description="Semiconductor/Ion semiconductor sequencing")
    DNA_NANOBALL_SEQUENCING = PermissibleValue(
        text="DNA_NANOBALL_SEQUENCING",
        description="DNA nanoball sequencing (MGI/BGI)")
    SEQUENCING_BY_AVIDITY = PermissibleValue(
        text="SEQUENCING_BY_AVIDITY",
        description="Sequencing by avidity (Element Biosciences)")

    _defn = EnumDefinition(
        name="SequencingChemistry",
        description="Fundamental chemical methods used for DNA/RNA sequencing",
    )

class LibraryPreparation(EnumDefinitionImpl):
    """
    Methods for preparing sequencing libraries from nucleic acid samples
    """
    GENOMIC_DNA = PermissibleValue(
        text="GENOMIC_DNA",
        description="Genomic DNA library preparation")
    WHOLE_GENOME_AMPLIFICATION = PermissibleValue(
        text="WHOLE_GENOME_AMPLIFICATION",
        description="Whole genome amplification (WGA)")
    PCR_AMPLICON = PermissibleValue(
        text="PCR_AMPLICON",
        description="PCR amplicon sequencing")
    RNA_SEQ = PermissibleValue(
        text="RNA_SEQ",
        description="RNA sequencing library prep")
    SMALL_RNA_SEQ = PermissibleValue(
        text="SMALL_RNA_SEQ",
        description="Small RNA sequencing")
    SINGLE_CELL_RNA_SEQ = PermissibleValue(
        text="SINGLE_CELL_RNA_SEQ",
        description="Single-cell RNA sequencing")
    ATAC_SEQ = PermissibleValue(
        text="ATAC_SEQ",
        description="ATAC-seq (chromatin accessibility)")
    CHIP_SEQ = PermissibleValue(
        text="CHIP_SEQ",
        description="ChIP-seq (chromatin immunoprecipitation)")
    BISULFITE_SEQ = PermissibleValue(
        text="BISULFITE_SEQ",
        description="Bisulfite sequencing (methylation)")
    HI_C = PermissibleValue(
        text="HI_C",
        description="Hi-C (chromosome conformation capture)")
    CUT_AND_RUN = PermissibleValue(
        text="CUT_AND_RUN",
        description="CUT&RUN (chromatin profiling)")
    CUT_AND_TAG = PermissibleValue(
        text="CUT_AND_TAG",
        description="CUT&Tag (chromatin profiling)")
    CAPTURE_SEQUENCING = PermissibleValue(
        text="CAPTURE_SEQUENCING",
        description="Target capture/enrichment sequencing")
    EXOME_SEQUENCING = PermissibleValue(
        text="EXOME_SEQUENCING",
        description="Whole exome sequencing")
    METAGENOMICS = PermissibleValue(
        text="METAGENOMICS",
        description="Metagenomic sequencing")
    AMPLICON_SEQUENCING = PermissibleValue(
        text="AMPLICON_SEQUENCING",
        description="16S/ITS amplicon sequencing")
    DIRECT_RNA = PermissibleValue(
        text="DIRECT_RNA",
        description="Direct RNA sequencing (nanopore)")
    CDNA_SEQUENCING = PermissibleValue(
        text="CDNA_SEQUENCING",
        description="cDNA sequencing")
    RIBOSOME_PROFILING = PermissibleValue(
        text="RIBOSOME_PROFILING",
        description="Ribosome profiling (Ribo-seq)")

    _defn = EnumDefinition(
        name="LibraryPreparation",
        description="Methods for preparing sequencing libraries from nucleic acid samples",
    )

class SequencingApplication(EnumDefinitionImpl):
    """
    Primary applications or assays using DNA/RNA sequencing
    """
    WHOLE_GENOME_SEQUENCING = PermissibleValue(
        text="WHOLE_GENOME_SEQUENCING",
        title="WHOLE_GENOME_SEQUENCING",
        description="Whole genome sequencing (WGS)",
        meaning=EDAM["topic_3673"])
    WHOLE_EXOME_SEQUENCING = PermissibleValue(
        text="WHOLE_EXOME_SEQUENCING",
        title="WHOLE_EXOME_SEQUENCING",
        description="Whole exome sequencing (WES)",
        meaning=EDAM["topic_3676"])
    TRANSCRIPTOME_SEQUENCING = PermissibleValue(
        text="TRANSCRIPTOME_SEQUENCING",
        title="TRANSCRIPTOME_SEQUENCING",
        description="RNA sequencing (RNA-seq)",
        meaning=EDAM["topic_3170"])
    TARGETED_SEQUENCING = PermissibleValue(
        text="TARGETED_SEQUENCING",
        description="Targeted gene panel sequencing")
    EPIGENOMICS = PermissibleValue(
        text="EPIGENOMICS",
        description="Epigenomic profiling")
    METAGENOMICS = PermissibleValue(
        text="METAGENOMICS",
        title="METAGENOMICS",
        description="Metagenomic sequencing",
        meaning=EDAM["topic_3837"])
    SINGLE_CELL_GENOMICS = PermissibleValue(
        text="SINGLE_CELL_GENOMICS",
        description="Single-cell genomics")
    SINGLE_CELL_TRANSCRIPTOMICS = PermissibleValue(
        text="SINGLE_CELL_TRANSCRIPTOMICS",
        title="SINGLE_CELL_TRANSCRIPTOMICS",
        description="Single-cell transcriptomics",
        meaning=EDAM["topic_4028"])
    CHROMATIN_IMMUNOPRECIPITATION = PermissibleValue(
        text="CHROMATIN_IMMUNOPRECIPITATION",
        title="CHROMATIN_IMMUNOPRECIPITATION",
        description="ChIP-seq",
        meaning=EDAM["topic_3656"])
    CHROMATIN_ACCESSIBILITY = PermissibleValue(
        text="CHROMATIN_ACCESSIBILITY",
        description="ATAC-seq/FAIRE-seq")
    DNA_METHYLATION = PermissibleValue(
        text="DNA_METHYLATION",
        description="Bisulfite/methylation sequencing")
    CHROMOSOME_CONFORMATION = PermissibleValue(
        text="CHROMOSOME_CONFORMATION",
        description="Hi-C/3C-seq")
    VARIANT_CALLING = PermissibleValue(
        text="VARIANT_CALLING",
        description="Genetic variant discovery")
    PHARMACOGENOMICS = PermissibleValue(
        text="PHARMACOGENOMICS",
        description="Pharmacogenomic sequencing")
    CLINICAL_DIAGNOSTICS = PermissibleValue(
        text="CLINICAL_DIAGNOSTICS",
        description="Clinical diagnostic sequencing")
    POPULATION_GENOMICS = PermissibleValue(
        text="POPULATION_GENOMICS",
        description="Population-scale genomics")

    _defn = EnumDefinition(
        name="SequencingApplication",
        description="Primary applications or assays using DNA/RNA sequencing",
    )

class ReadType(EnumDefinitionImpl):
    """
    Configuration of sequencing reads generated by different platforms
    """
    SINGLE_END = PermissibleValue(
        text="SINGLE_END",
        title="SINGLE_END",
        description="Single-end reads")
    PAIRED_END = PermissibleValue(
        text="PAIRED_END",
        title="PAIRED_END",
        description="Paired-end reads")
    MATE_PAIR = PermissibleValue(
        text="MATE_PAIR",
        description="Mate-pair reads (large insert)")
    LONG_READ = PermissibleValue(
        text="LONG_READ",
        description="Long reads (>1kb typical)")
    ULTRA_LONG_READ = PermissibleValue(
        text="ULTRA_LONG_READ",
        description="Ultra-long reads (>10kb)")
    CONTINUOUS_LONG_READ = PermissibleValue(
        text="CONTINUOUS_LONG_READ",
        description="Continuous long reads (nanopore)")

    _defn = EnumDefinition(
        name="ReadType",
        description="Configuration of sequencing reads generated by different platforms",
    )

class SequenceFileFormat(EnumDefinitionImpl):
    """
    Standard file formats used for storing sequence data
    """
    FASTA = PermissibleValue(
        text="FASTA",
        description="FASTA sequence format",
        meaning=EDAM["format_1929"])
    FASTQ = PermissibleValue(
        text="FASTQ",
        description="FASTQ sequence with quality format",
        meaning=EDAM["format_1930"])
    SAM = PermissibleValue(
        text="SAM",
        description="Sequence Alignment Map format",
        meaning=EDAM["format_2573"])
    BAM = PermissibleValue(
        text="BAM",
        description="Binary Alignment Map format",
        meaning=EDAM["format_2572"])
    CRAM = PermissibleValue(
        text="CRAM",
        description="Compressed Reference-oriented Alignment Map")
    VCF = PermissibleValue(
        text="VCF",
        description="Variant Call Format",
        meaning=EDAM["format_3016"])
    BCF = PermissibleValue(
        text="BCF",
        description="Binary Variant Call Format",
        meaning=EDAM["format_3020"])
    GFF3 = PermissibleValue(
        text="GFF3",
        description="Generic Feature Format version 3")
    GTF = PermissibleValue(
        text="GTF",
        description="Gene Transfer Format")
    BED = PermissibleValue(
        text="BED",
        description="Browser Extensible Data format")
    BIGWIG = PermissibleValue(
        text="BIGWIG",
        description="BigWig format for continuous data")
    BIGBED = PermissibleValue(
        text="BIGBED",
        description="BigBed format for interval data")
    HDF5 = PermissibleValue(
        text="HDF5",
        description="Hierarchical Data Format 5")
    SFF = PermissibleValue(
        text="SFF",
        description="Standard Flowgram Format (454)",
        meaning=EDAM["format_3284"])
    FAST5 = PermissibleValue(
        text="FAST5",
        description="Fast5 format (Oxford Nanopore)")
    POD5 = PermissibleValue(
        text="POD5",
        description="POD5 format (Oxford Nanopore, newer)")

    _defn = EnumDefinition(
        name="SequenceFileFormat",
        description="Standard file formats used for storing sequence data",
    )

class DataProcessingLevel(EnumDefinitionImpl):
    """
    Levels of processing applied to raw sequencing data
    """
    RAW = PermissibleValue(
        text="RAW",
        description="Raw unprocessed sequencing reads")
    QUALITY_FILTERED = PermissibleValue(
        text="QUALITY_FILTERED",
        description="Quality filtered reads")
    TRIMMED = PermissibleValue(
        text="TRIMMED",
        description="Adapter/quality trimmed reads")
    ALIGNED = PermissibleValue(
        text="ALIGNED",
        description="Aligned to reference genome")
    DEDUPLICATED = PermissibleValue(
        text="DEDUPLICATED",
        description="PCR duplicates removed")
    RECALIBRATED = PermissibleValue(
        text="RECALIBRATED",
        description="Base quality score recalibrated")
    VARIANT_CALLED = PermissibleValue(
        text="VARIANT_CALLED",
        description="Variants called from alignments")
    NORMALIZED = PermissibleValue(
        text="NORMALIZED",
        description="Expression normalized (RNA-seq)")
    ASSEMBLED = PermissibleValue(
        text="ASSEMBLED",
        description="De novo assembled sequences")
    ANNOTATED = PermissibleValue(
        text="ANNOTATED",
        description="Functionally annotated sequences")

    _defn = EnumDefinition(
        name="DataProcessingLevel",
        description="Levels of processing applied to raw sequencing data",
    )

class CdsPhaseType(EnumDefinitionImpl):
    """
    For features of type CDS (coding sequence), the phase indicates where the feature begins with reference to the
    reading frame. The phase is one of the integers 0, 1, or 2, indicating the number of bases that should be removed
    from the beginning of this feature to reach the first base of the next codon.
    """
    PHASE_0 = PermissibleValue(
        text="PHASE_0",
        title="0",
        description="Zero bases from reading frame to feature start.")
    PHASE_1 = PermissibleValue(
        text="PHASE_1",
        title="1",
        description="One base from reading frame to feature start.")
    PHASE_2 = PermissibleValue(
        text="PHASE_2",
        title="2",
        description="Two bases from reading frame to feature start.")

    _defn = EnumDefinition(
        name="CdsPhaseType",
        description="""For features of type CDS (coding sequence), the phase indicates where the feature begins with reference to the reading frame. The phase is one of the integers 0, 1, or 2, indicating the number of bases that should be removed from the beginning of this feature to reach the first base of the next codon.""",
    )

class ContigCollectionType(EnumDefinitionImpl):
    """
    The type of the contig set; the type of the 'omics data set. Terms are taken from the Genomics Standards
    Consortium where possible. See the GSC checklists at https://genomicsstandardsconsortium.github.io/mixs/ for the
    controlled vocabularies used.
    """
    ISOLATE = PermissibleValue(
        text="ISOLATE",
        description="""Sequences assembled from DNA of isolated organism. Bacteria/Archaea: https://genomicsstandardsconsortium.github.io/mixs/0010003/ Euk: https://genomicsstandardsconsortium.github.io/mixs/0010002/ Virus: https://genomicsstandardsconsortium.github.io/mixs/0010005/ Organelle: https://genomicsstandardsconsortium.github.io/mixs/0010006/ Plasmid: https://genomicsstandardsconsortium.github.io/mixs/0010004/""")
    MAG = PermissibleValue(
        text="MAG",
        title="Metagenome-Assembled Genome",
        description="""Sequences assembled from DNA of mixed community and binned. MAGs are likely to represent a single taxonomic origin. See checkm2 scores for quality assessment.""",
        meaning=MIXS["0010011"])
    METAGENOME = PermissibleValue(
        text="METAGENOME",
        description="Sequences assembled from DNA of mixed community.",
        meaning=MIXS["0010007"])
    METATRANSCRIPTOME = PermissibleValue(
        text="METATRANSCRIPTOME",
        description="Sequences assembled from RNA of mixed community. Currently not represented by GSC.")
    SAG = PermissibleValue(
        text="SAG",
        title="Single Amplified Genome",
        description="Sequences assembled from DNA of single cell.",
        meaning=MIXS["0010010"])
    VIRUS = PermissibleValue(
        text="VIRUS",
        description="Sequences assembled from uncultivated virus genome (DNA/RNA).",
        meaning=MIXS["0010012"])
    MARKER = PermissibleValue(
        text="MARKER",
        description="""Sequences from targeted region of DNA; see protocol for information on targeted region. specimen: https://genomicsstandardsconsortium.github.io/mixs/0010009/ survey: https://genomicsstandardsconsortium.github.io/mixs/0010008/""")

    _defn = EnumDefinition(
        name="ContigCollectionType",
        description="""The type of the contig set; the type of the 'omics data set. Terms are taken from the Genomics Standards Consortium where possible. See the GSC checklists at https://genomicsstandardsconsortium.github.io/mixs/ for the controlled vocabularies used.""",
    )

class StrandType(EnumDefinitionImpl):
    """
    The strand that a feature appears on relative to a landmark. Also encompasses unknown or irrelevant strandedness.
    """
    NEGATIVE = PermissibleValue(
        text="NEGATIVE",
        title="negative",
        description="Represented by \"-\" in a GFF file; the strand is negative wrt the landmark.")
    POSITIVE = PermissibleValue(
        text="POSITIVE",
        title="positive",
        description="Represented by \"+\" in a GFF file; the strand is positive with relation to the landmark.")
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        title="unknown",
        description="Represented by \"?\" in a GFF file. The strandedness is relevant but unknown.")
    UNSTRANDED = PermissibleValue(
        text="UNSTRANDED",
        title="unstranded",
        description="Represented by \".\" in a GFF file; the feature is not stranded.")

    _defn = EnumDefinition(
        name="StrandType",
        description="""The strand that a feature appears on relative to a landmark. Also encompasses unknown or irrelevant strandedness.""",
    )

class SequenceType(EnumDefinitionImpl):
    """
    The type of sequence being represented.
    """
    NUCLEIC_ACID = PermissibleValue(
        text="NUCLEIC_ACID",
        description="A nucleic acid sequence, as found in an FNA file.")
    AMINO_ACID = PermissibleValue(
        text="AMINO_ACID",
        description="An amino acid sequence, as would be found in an FAA file.")

    _defn = EnumDefinition(
        name="SequenceType",
        description="The type of sequence being represented.",
    )

class ProteinEvidenceForExistence(EnumDefinitionImpl):
    """
    The evidence for the existence of a biological entity. See https://www.uniprot.org/help/protein_existence and
    https://www.ncbi.nlm.nih.gov/genbank/evidence/.
    """
    EXPERIMENTAL_EVIDENCE_AT_PROTEIN_LEVEL = PermissibleValue(
        text="EXPERIMENTAL_EVIDENCE_AT_PROTEIN_LEVEL",
        description="""Indicates that there is clear experimental evidence for the existence of the protein. The criteria include partial or complete Edman sequencing, clear identification by mass spectrometry, X-ray or NMR structure, good quality protein-protein interaction or detection of the protein by antibodies.""")
    EXPERIMENTAL_EVIDENCE_AT_TRANSCRIPT_LEVEL = PermissibleValue(
        text="EXPERIMENTAL_EVIDENCE_AT_TRANSCRIPT_LEVEL",
        description="""Indicates that the existence of a protein has not been strictly proven but that expression data (such as existence of cDNA(s), RT-PCR or Northern blots) indicate the existence of a transcript.""")
    PROTEIN_INFERRED_BY_HOMOLOGY = PermissibleValue(
        text="PROTEIN_INFERRED_BY_HOMOLOGY",
        description="""Indicates that the existence of a protein is probable because clear orthologs exist in closely related species.""")
    PROTEIN_PREDICTED = PermissibleValue(
        text="PROTEIN_PREDICTED",
        description="Used for entries without evidence at protein, transcript, or homology levels.")
    PROTEIN_UNCERTAIN = PermissibleValue(
        text="PROTEIN_UNCERTAIN",
        description="Indicates that the existence of the protein is unsure.")

    _defn = EnumDefinition(
        name="ProteinEvidenceForExistence",
        description="""The evidence for the existence of a biological entity. See https://www.uniprot.org/help/protein_existence and https://www.ncbi.nlm.nih.gov/genbank/evidence/.""",
    )

class RefSeqStatusType(EnumDefinitionImpl):
    """
    RefSeq status codes, taken from https://www.ncbi.nlm.nih.gov/genbank/evidence/.
    """
    MODEL = PermissibleValue(
        text="MODEL",
        description="""The RefSeq record is provided by the NCBI Genome Annotation pipeline and is not subject to individual review or revision between annotation runs.""")
    INFERRED = PermissibleValue(
        text="INFERRED",
        description="""The RefSeq record has been predicted by genome sequence analysis, but it is not yet supported by experimental evidence. The record may be partially supported by homology data.""")
    PREDICTED = PermissibleValue(
        text="PREDICTED",
        description="""The RefSeq record has not yet been subject to individual review, and some aspect of the RefSeq record is predicted.""")
    PROVISIONAL = PermissibleValue(
        text="PROVISIONAL",
        description="""The RefSeq record has not yet been subject to individual review. The initial sequence-to-gene association has been established by outside collaborators or NCBI staff.""")
    REVIEWED = PermissibleValue(
        text="REVIEWED",
        description="""The RefSeq record has been reviewed by NCBI staff or by a collaborator. The NCBI review process includes assessing available sequence data and the literature. Some RefSeq records may incorporate expanded sequence and annotation information.""")
    VALIDATED = PermissibleValue(
        text="VALIDATED",
        description="""The RefSeq record has undergone an initial review to provide the preferred sequence standard. The record has not yet been subject to final review at which time additional functional information may be provided.""")
    WGS = PermissibleValue(
        text="WGS",
        description="""The RefSeq record is provided to represent a collection of whole genome shotgun sequences. These records are not subject to individual review or revisions between genome updates.""")

    _defn = EnumDefinition(
        name="RefSeqStatusType",
        description="RefSeq status codes, taken from https://www.ncbi.nlm.nih.gov/genbank/evidence/.",
    )

class CurrencyChemical(EnumDefinitionImpl):
    """
    Common metabolic currency molecules and cofactors that serve as energy carriers, electron donors/acceptors, and
    group transfer agents in cellular metabolism.
    """
    ATP = PermissibleValue(
        text="ATP",
        description="Adenosine triphosphate - primary energy currency molecule in cells",
        meaning=CHEBI["15422"])
    ADP = PermissibleValue(
        text="ADP",
        description="Adenosine diphosphate - product of ATP hydrolysis, energy acceptor",
        meaning=CHEBI["16761"])
    AMP = PermissibleValue(
        text="AMP",
        description="Adenosine monophosphate - nucleotide, product of ADP hydrolysis",
        meaning=CHEBI["16027"])
    GTP = PermissibleValue(
        text="GTP",
        description="Guanosine triphosphate - energy molecule, protein synthesis and signaling",
        meaning=CHEBI["15996"])
    GDP = PermissibleValue(
        text="GDP",
        description="Guanosine diphosphate - product of GTP hydrolysis",
        meaning=CHEBI["17552"])
    NAD_PLUS = PermissibleValue(
        text="NAD_PLUS",
        title="NAD+",
        description="Nicotinamide adenine dinucleotide (oxidized) - electron acceptor in catabolism",
        meaning=CHEBI["15846"])
    NADH = PermissibleValue(
        text="NADH",
        description="Nicotinamide adenine dinucleotide (reduced) - electron donor, reducing agent",
        meaning=CHEBI["16908"])
    NADP_PLUS = PermissibleValue(
        text="NADP_PLUS",
        title="NADP+",
        description="Nicotinamide adenine dinucleotide phosphate (oxidized) - electron acceptor",
        meaning=CHEBI["18009"])
    NADPH = PermissibleValue(
        text="NADPH",
        description="Nicotinamide adenine dinucleotide phosphate (reduced) - anabolic reducing agent",
        meaning=CHEBI["16474"])
    FAD = PermissibleValue(
        text="FAD",
        description="Flavin adenine dinucleotide (oxidized) - electron acceptor in oxidation reactions",
        meaning=CHEBI["16238"])
    FADH2 = PermissibleValue(
        text="FADH2",
        description="Flavin adenine dinucleotide (reduced) - electron donor in electron transport chain",
        meaning=CHEBI["17877"])
    COA = PermissibleValue(
        text="COA",
        title="CoA",
        description="Coenzyme A - acyl group carrier in fatty acid metabolism",
        meaning=CHEBI["15346"])
    ACETYL_COA = PermissibleValue(
        text="ACETYL_COA",
        title="Acetyl-CoA",
        description="Acetyl coenzyme A - central metabolic intermediate, links glycolysis to citric acid cycle",
        meaning=CHEBI["15351"])

    _defn = EnumDefinition(
        name="CurrencyChemical",
        description="""Common metabolic currency molecules and cofactors that serve as energy carriers, electron donors/acceptors, and group transfer agents in cellular metabolism.""",
    )

class PlantDevelopmentalStage(EnumDefinitionImpl):
    """
    Major developmental stages in the plant life cycle, from seed germination through senescence. Based on the Plant
    Ontology (PO) standardized stages.
    """
    SEED_GERMINATION_STAGE = PermissibleValue(
        text="SEED_GERMINATION_STAGE",
        description="Stage beginning with seed imbibition and ending with radicle emergence",
        meaning=PO["0007057"])
    SEEDLING_STAGE = PermissibleValue(
        text="SEEDLING_STAGE",
        description="Stage from germination until development of first adult vascular leaf",
        meaning=PO["0007131"])
    VEGETATIVE_GROWTH_STAGE = PermissibleValue(
        text="VEGETATIVE_GROWTH_STAGE",
        description="Stage of growth before reproductive structure formation",
        meaning=PO["0007134"])
    FLOWERING_STAGE = PermissibleValue(
        text="FLOWERING_STAGE",
        description="Stage when flowers open with pollen release and/or receptive stigma",
        meaning=PO["0007616"])
    FRUIT_DEVELOPMENT_STAGE = PermissibleValue(
        text="FRUIT_DEVELOPMENT_STAGE",
        description="Stage of fruit formation through ripening",
        meaning=PO["0001002"])
    SEED_DEVELOPMENT_STAGE = PermissibleValue(
        text="SEED_DEVELOPMENT_STAGE",
        description="Stage from fertilization to mature seed",
        meaning=PO["0001170"])
    SENESCENCE_STAGE = PermissibleValue(
        text="SENESCENCE_STAGE",
        description="Stage of aging with loss of function and organ deterioration",
        meaning=PO["0007017"])
    DORMANCY_STAGE = PermissibleValue(
        text="DORMANCY_STAGE",
        description="Stage of suspended physiological activity and growth",
        meaning=PO["0007132"])
    EMBRYO_DEVELOPMENT_STAGE = PermissibleValue(
        text="EMBRYO_DEVELOPMENT_STAGE",
        description="Stage from zygote first division to seed germination initiation",
        meaning=PO["0007631"])
    ROOT_DEVELOPMENT_STAGE = PermissibleValue(
        text="ROOT_DEVELOPMENT_STAGE",
        description="Stages in root growth and development",
        meaning=PO["0007520"])
    LEAF_DEVELOPMENT_STAGE = PermissibleValue(
        text="LEAF_DEVELOPMENT_STAGE",
        description="Stages in leaf formation and expansion",
        meaning=PO["0001050"])
    REPRODUCTIVE_STAGE = PermissibleValue(
        text="REPRODUCTIVE_STAGE",
        description="Stage from reproductive structure initiation to senescence onset",
        meaning=PO["0007130"])
    MATURITY_STAGE = PermissibleValue(
        text="MATURITY_STAGE",
        description="Stage when plant or plant embryo reaches full development",
        meaning=PO["0001081"])
    POST_HARVEST_STAGE = PermissibleValue(
        text="POST_HARVEST_STAGE",
        description="Stage after harvest when plant parts are detached from parent plant")

    _defn = EnumDefinition(
        name="PlantDevelopmentalStage",
        description="""Major developmental stages in the plant life cycle, from seed germination through senescence. Based on the Plant Ontology (PO) standardized stages.""",
    )

class UniProtSpeciesCode(EnumDefinitionImpl):
    """
    UniProt species mnemonic codes for reference proteomes with associated metadata
    """
    SP_9ABAC = PermissibleValue(
        text="SP_9ABAC",
        title="Lambdina fiscellaria nucleopolyhedrovirus",
        description="Lambdina fiscellaria nucleopolyhedrovirus - Proteome: UP000201190",
        meaning=NCBITAXON["1642929"])
    SP_9ACAR = PermissibleValue(
        text="SP_9ACAR",
        title="Tropilaelaps mercedesae",
        description="Tropilaelaps mercedesae - Proteome: UP000192247",
        meaning=NCBITAXON["418985"])
    SP_9ACTN = PermissibleValue(
        text="SP_9ACTN",
        title="Candidatus Protofrankia datiscae",
        description="Candidatus Protofrankia datiscae - Proteome: UP000001549",
        meaning=NCBITAXON["2716812"])
    SP_9ACTO = PermissibleValue(
        text="SP_9ACTO",
        title="Actinomyces massiliensis F0489",
        description="Actinomyces massiliensis F0489 - Proteome: UP000002941",
        meaning=NCBITAXON["1125718"])
    SP_9ADEN = PermissibleValue(
        text="SP_9ADEN",
        title="Human adenovirus 53",
        description="Human adenovirus 53 - Proteome: UP000463865",
        meaning=NCBITAXON["556926"])
    SP_9AGAM = PermissibleValue(
        text="SP_9AGAM",
        title="Jaapia argillacea MUCL 33604",
        description="Jaapia argillacea MUCL 33604 - Proteome: UP000027265",
        meaning=NCBITAXON["933084"])
    SP_9AGAR = PermissibleValue(
        text="SP_9AGAR",
        title="Collybiopsis luxurians FD-317 M1",
        description="Collybiopsis luxurians FD-317 M1 - Proteome: UP000053593",
        meaning=NCBITAXON["944289"])
    SP_9ALPC = PermissibleValue(
        text="SP_9ALPC",
        title="Feline coronavirus",
        description="Feline coronavirus - Proteome: UP000141821",
        meaning=NCBITAXON["12663"])
    SP_9ALPH = PermissibleValue(
        text="SP_9ALPH",
        title="Testudinid alphaherpesvirus 3",
        description="Testudinid alphaherpesvirus 3 - Proteome: UP000100290",
        meaning=NCBITAXON["2560801"])
    SP_9ALTE = PermissibleValue(
        text="SP_9ALTE",
        title="Paraglaciecola arctica BSs20135",
        description="Paraglaciecola arctica BSs20135 - Proteome: UP000006327",
        meaning=NCBITAXON["493475"])
    SP_9ALVE = PermissibleValue(
        text="SP_9ALVE",
        title="Perkinsus sp. BL_2016",
        description="Perkinsus sp. BL_2016 - Proteome: UP000298064",
        meaning=NCBITAXON["2494336"])
    SP_9AMPH = PermissibleValue(
        text="SP_9AMPH",
        title="Microcaecilia unicolor",
        description="Microcaecilia unicolor - Proteome: UP000515156",
        meaning=NCBITAXON["1415580"])
    SP_9ANNE = PermissibleValue(
        text="SP_9ANNE",
        title="Dimorphilus gyrociliatus",
        description="Dimorphilus gyrociliatus - Proteome: UP000549394",
        meaning=NCBITAXON["2664684"])
    SP_9ANUR = PermissibleValue(
        text="SP_9ANUR",
        title="Leptobrachium leishanense",
        description="Leptobrachium leishanense (Leishan spiny toad) - Proteome: UP000694569",
        meaning=NCBITAXON["445787"])
    SP_9APHY = PermissibleValue(
        text="SP_9APHY",
        title="Fibroporia radiculosa",
        description="Fibroporia radiculosa - Proteome: UP000006352",
        meaning=NCBITAXON["599839"])
    SP_9APIA = PermissibleValue(
        text="SP_9APIA",
        title="Heracleum sosnowskyi",
        description="Heracleum sosnowskyi - Proteome: UP001237642",
        meaning=NCBITAXON["360622"])
    SP_9APIC = PermissibleValue(
        text="SP_9APIC",
        title="Babesia sp. Xinjiang",
        description="Babesia sp. Xinjiang - Proteome: UP000193856",
        meaning=NCBITAXON["462227"])
    SP_9AQUI = PermissibleValue(
        text="SP_9AQUI",
        title="Sulfurihydrogenibium yellowstonense SS-5",
        description="Sulfurihydrogenibium yellowstonense SS-5 - Proteome: UP000005540",
        meaning=NCBITAXON["432331"])
    SP_9ARAC = PermissibleValue(
        text="SP_9ARAC",
        title="Trichonephila inaurata madagascariensis",
        description="Trichonephila inaurata madagascariensis - Proteome: UP000886998",
        meaning=NCBITAXON["2747483"])
    SP_9ARCH = PermissibleValue(
        text="SP_9ARCH",
        title="Candidatus Nitrosarchaeum limnium BG20",
        description="Candidatus Nitrosarchaeum limnium BG20 - Proteome: UP000014065",
        meaning=NCBITAXON["859192"])
    SP_9ASCO = PermissibleValue(
        text="SP_9ASCO",
        title="Kuraishia capsulata CBS 1993",
        description="Kuraishia capsulata CBS 1993 - Proteome: UP000019384",
        meaning=NCBITAXON["1382522"])
    SP_9ASPA = PermissibleValue(
        text="SP_9ASPA",
        title="Dendrobium catenatum",
        description="Dendrobium catenatum - Proteome: UP000233837",
        meaning=NCBITAXON["906689"])
    SP_9ASTE = PermissibleValue(
        text="SP_9ASTE",
        title="Cuscuta australis",
        description="Cuscuta australis - Proteome: UP000249390",
        meaning=NCBITAXON["267555"])
    SP_9ASTR = PermissibleValue(
        text="SP_9ASTR",
        title="Mikania micrantha",
        description="Mikania micrantha - Proteome: UP000326396",
        meaning=NCBITAXON["192012"])
    SP_9AVES = PermissibleValue(
        text="SP_9AVES",
        title="Anser brachyrhynchus",
        description="Anser brachyrhynchus (Pink-footed goose) - Proteome: UP000694426",
        meaning=NCBITAXON["132585"])
    SP_9BACE = PermissibleValue(
        text="SP_9BACE",
        title="Bacteroides caccae CL03T12C61",
        description="Bacteroides caccae CL03T12C61 - Proteome: UP000002965",
        meaning=NCBITAXON["997873"])
    SP_9BACI = PermissibleValue(
        text="SP_9BACI",
        title="Fictibacillus macauensis ZFHKF-1",
        description="Fictibacillus macauensis ZFHKF-1 - Proteome: UP000004080",
        meaning=NCBITAXON["1196324"])
    SP_9BACL = PermissibleValue(
        text="SP_9BACL",
        title="Paenibacillus sp. HGF7",
        description="Paenibacillus sp. HGF7 - Proteome: UP000003445",
        meaning=NCBITAXON["944559"])
    SP_9BACT = PermissibleValue(
        text="SP_9BACT",
        title="Parabacteroides johnsonii CL02T12C29",
        description="Parabacteroides johnsonii CL02T12C29 - Proteome: UP000001218",
        meaning=NCBITAXON["999419"])
    SP_9BACU = PermissibleValue(
        text="SP_9BACU",
        title="Samia ricini nucleopolyhedrovirus",
        description="Samia ricini nucleopolyhedrovirus - Proteome: UP001226138",
        meaning=NCBITAXON["1920700"])
    SP_9BASI = PermissibleValue(
        text="SP_9BASI",
        title="Malassezia pachydermatis",
        description="Malassezia pachydermatis - Proteome: UP000037751",
        meaning=NCBITAXON["77020"])
    SP_9BBAC = PermissibleValue(
        text="SP_9BBAC",
        title="Plutella xylostella granulovirus",
        description="Plutella xylostella granulovirus - Proteome: UP000201310",
        meaning=NCBITAXON["98383"])
    SP_9BETA = PermissibleValue(
        text="SP_9BETA",
        title="Saimiriine betaherpesvirus 4",
        description="Saimiriine betaherpesvirus 4 - Proteome: UP000097892",
        meaning=NCBITAXON["1535247"])
    SP_9BETC = PermissibleValue(
        text="SP_9BETC",
        title="Coronavirus BtRt-BetaCoV/GX2018",
        description="Coronavirus BtRt-BetaCoV/GX2018 - Proteome: UP001228689",
        meaning=NCBITAXON["2591238"])
    SP_9BIFI = PermissibleValue(
        text="SP_9BIFI",
        title="Scardovia wiggsiae F0424",
        description="Scardovia wiggsiae F0424 - Proteome: UP000006415",
        meaning=NCBITAXON["857290"])
    SP_9BILA = PermissibleValue(
        text="SP_9BILA",
        title="Ancylostoma ceylanicum",
        description="Ancylostoma ceylanicum - Proteome: UP000024635",
        meaning=NCBITAXON["53326"])
    SP_9BIVA = PermissibleValue(
        text="SP_9BIVA",
        title="Potamilus streckersoni",
        description="Potamilus streckersoni - Proteome: UP001195483",
        meaning=NCBITAXON["2493646"])
    SP_9BORD = PermissibleValue(
        text="SP_9BORD",
        title="Bordetella sp. N",
        description="Bordetella sp. N - Proteome: UP000064621",
        meaning=NCBITAXON["1746199"])
    SP_9BRAD = PermissibleValue(
        text="SP_9BRAD",
        title="Afipia broomeae ATCC 49717",
        description="Afipia broomeae ATCC 49717 - Proteome: UP000001096",
        meaning=NCBITAXON["883078"])
    SP_9BRAS = PermissibleValue(
        text="SP_9BRAS",
        title="Capsella rubella",
        description="Capsella rubella - Proteome: UP000029121",
        meaning=NCBITAXON["81985"])
    SP_9BROM = PermissibleValue(
        text="SP_9BROM",
        title="Prune dwarf virus",
        description="Prune dwarf virus - Proteome: UP000202132",
        meaning=NCBITAXON["33760"])
    SP_9BURK = PermissibleValue(
        text="SP_9BURK",
        title="Candidatus Paraburkholderia kirkii UZHbot1",
        description="Candidatus Paraburkholderia kirkii UZHbot1 - Proteome: UP000003511",
        meaning=NCBITAXON["1055526"])
    SP_9CARY = PermissibleValue(
        text="SP_9CARY",
        title="Carnegiea gigantea",
        description="Carnegiea gigantea - Proteome: UP001153076",
        meaning=NCBITAXON["171969"])
    SP_9CAUD = PermissibleValue(
        text="SP_9CAUD",
        title="Salmonella phage Vi06",
        description="Salmonella phage Vi06 - Proteome: UP000000335",
        meaning=NCBITAXON["866889"])
    SP_9CAUL = PermissibleValue(
        text="SP_9CAUL",
        title="Brevundimonas abyssalis TAR-001",
        description="Brevundimonas abyssalis TAR-001 - Proteome: UP000016569",
        meaning=NCBITAXON["1391729"])
    SP_9CBAC = PermissibleValue(
        text="SP_9CBAC",
        title="Neodiprion sertifer nucleopolyhedrovirus",
        description="Neodiprion sertifer nucleopolyhedrovirus - Proteome: UP000243697",
        meaning=NCBITAXON["111874"])
    SP_9CELL = PermissibleValue(
        text="SP_9CELL",
        title="Actinotalea ferrariae CF5-4",
        description="Actinotalea ferrariae CF5-4 - Proteome: UP000019753",
        meaning=NCBITAXON["948458"])
    SP_9CERV = PermissibleValue(
        text="SP_9CERV",
        title="Cervus hanglu yarkandensis",
        description="Cervus hanglu yarkandensis (Yarkand deer) - Proteome: UP000631465",
        meaning=NCBITAXON["84702"])
    SP_9CETA = PermissibleValue(
        text="SP_9CETA",
        title="Catagonus wagneri",
        description="Catagonus wagneri (Chacoan peccary) - Proteome: UP000694540",
        meaning=NCBITAXON["51154"])
    SP_9CHAR = PermissibleValue(
        text="SP_9CHAR",
        title="Rostratula benghalensis",
        description="Rostratula benghalensis (greater painted-snipe) - Proteome: UP000545435",
        meaning=NCBITAXON["118793"])
    SP_9CHIR = PermissibleValue(
        text="SP_9CHIR",
        title="Phyllostomus discolor",
        description="Phyllostomus discolor (pale spear-nosed bat) - Proteome: UP000504628",
        meaning=NCBITAXON["89673"])
    SP_9CHLA = PermissibleValue(
        text="SP_9CHLA",
        title="Chlamydiales bacterium SCGC AG-110-P3",
        description="Chlamydiales bacterium SCGC AG-110-P3 - Proteome: UP000196763",
        meaning=NCBITAXON["1871323"])
    SP_9CHLB = PermissibleValue(
        text="SP_9CHLB",
        title="Chlorobium ferrooxidans DSM 13031",
        description="Chlorobium ferrooxidans DSM 13031 - Proteome: UP000004162",
        meaning=NCBITAXON["377431"])
    SP_9CHLO = PermissibleValue(
        text="SP_9CHLO",
        title="Helicosporidium sp. ATCC 50920",
        description="Helicosporidium sp. ATCC 50920 - Proteome: UP000026042",
        meaning=NCBITAXON["1291522"])
    SP_9CHLR = PermissibleValue(
        text="SP_9CHLR",
        title="Ardenticatena maritima",
        description="Ardenticatena maritima - Proteome: UP000037784",
        meaning=NCBITAXON["872965"])
    SP_9CHRO = PermissibleValue(
        text="SP_9CHRO",
        title="Gloeocapsa sp. PCC 7428",
        description="Gloeocapsa sp. PCC 7428 - Proteome: UP000010476",
        meaning=NCBITAXON["1173026"])
    SP_9CICH = PermissibleValue(
        text="SP_9CICH",
        title="Maylandia zebra",
        description="Maylandia zebra (zebra mbuna) - Proteome: UP000265160",
        meaning=NCBITAXON["106582"])
    SP_9CILI = PermissibleValue(
        text="SP_9CILI",
        title="Stentor coeruleus",
        description="Stentor coeruleus - Proteome: UP000187209",
        meaning=NCBITAXON["5963"])
    SP_9CIRC = PermissibleValue(
        text="SP_9CIRC",
        title="Raven circovirus",
        description="Raven circovirus - Proteome: UP000097131",
        meaning=NCBITAXON["345250"])
    SP_9CLOS = PermissibleValue(
        text="SP_9CLOS",
        title="Grapevine leafroll-associated virus 10",
        description="Grapevine leafroll-associated virus 10 - Proteome: UP000203128",
        meaning=NCBITAXON["367121"])
    SP_9CLOT = PermissibleValue(
        text="SP_9CLOT",
        title="Candidatus Arthromitus sp. SFB-rat-Yit",
        description="Candidatus Arthromitus sp. SFB-rat-Yit - Proteome: UP000001273",
        meaning=NCBITAXON["1041504"])
    SP_9CNID = PermissibleValue(
        text="SP_9CNID",
        title="Clytia hemisphaerica",
        description="Clytia hemisphaerica - Proteome: UP000594262",
        meaning=NCBITAXON["252671"])
    SP_9COLU = PermissibleValue(
        text="SP_9COLU",
        title="Pampusana beccarii",
        description="Pampusana beccarii (Western bronze ground-dove) - Proteome: UP000541332",
        meaning=NCBITAXON["2953425"])
    SP_9CORV = PermissibleValue(
        text="SP_9CORV",
        title="Cnemophilus loriae",
        description="Cnemophilus loriae (Loria's bird-of-paradise) - Proteome: UP000517678",
        meaning=NCBITAXON["254448"])
    SP_9CORY = PermissibleValue(
        text="SP_9CORY",
        title="Corynebacterium genitalium ATCC 33030",
        description="Corynebacterium genitalium ATCC 33030 - Proteome: UP000004208",
        meaning=NCBITAXON["585529"])
    SP_9COXI = PermissibleValue(
        text="SP_9COXI",
        title="Coxiella endosymbiont of Amblyomma americanum",
        description="Coxiella endosymbiont of Amblyomma americanum - Proteome: UP000059222",
        meaning=NCBITAXON["325775"])
    SP_9CREN = PermissibleValue(
        text="SP_9CREN",
        title="Metallosphaera yellowstonensis MK1",
        description="Metallosphaera yellowstonensis MK1 - Proteome: UP000003980",
        meaning=NCBITAXON["671065"])
    SP_9CRUS = PermissibleValue(
        text="SP_9CRUS",
        title="Daphnia magna",
        description="Daphnia magna - Proteome: UP000076858",
        meaning=NCBITAXON["35525"])
    SP_9CUCU = PermissibleValue(
        text="SP_9CUCU",
        title="Ceutorhynchus assimilis",
        description="Ceutorhynchus assimilis (cabbage seed weevil) - Proteome: UP001152799",
        meaning=NCBITAXON["467358"])
    SP_9CYAN = PermissibleValue(
        text="SP_9CYAN",
        title="Leptolyngbyaceae cyanobacterium JSC-12",
        description="Leptolyngbyaceae cyanobacterium JSC-12 - Proteome: UP000001332",
        meaning=NCBITAXON["864702"])
    SP_9DEIN = PermissibleValue(
        text="SP_9DEIN",
        title="Meiothermus sp. QL-1",
        description="Meiothermus sp. QL-1 - Proteome: UP000255346",
        meaning=NCBITAXON["2058095"])
    SP_9DEIO = PermissibleValue(
        text="SP_9DEIO",
        title="Deinococcus sp. RL",
        description="Deinococcus sp. RL - Proteome: UP000027898",
        meaning=NCBITAXON["1489678"])
    SP_9DELA = PermissibleValue(
        text="SP_9DELA",
        title="Human T-cell leukemia virus type I",
        description="Human T-cell leukemia virus type I - Proteome: UP000108043",
        meaning=NCBITAXON["11908"])
    SP_9DELT = PermissibleValue(
        text="SP_9DELT",
        title="Lujinxingia litoralis",
        description="Lujinxingia litoralis - Proteome: UP000249169",
        meaning=NCBITAXON["2211119"])
    SP_9DEND = PermissibleValue(
        text="SP_9DEND",
        title="Xiphorhynchus elegans",
        description="Xiphorhynchus elegans (elegant woodcreeper) - Proteome: UP000551443",
        meaning=NCBITAXON["269412"])
    SP_9DINO = PermissibleValue(
        text="SP_9DINO",
        title="Symbiodinium necroappetens",
        description="Symbiodinium necroappetens - Proteome: UP000601435",
        meaning=NCBITAXON["1628268"])
    SP_9DIPT = PermissibleValue(
        text="SP_9DIPT",
        title="Clunio marinus",
        description="Clunio marinus - Proteome: UP000183832",
        meaning=NCBITAXON["568069"])
    SP_9EIME = PermissibleValue(
        text="SP_9EIME",
        title="Eimeria praecox",
        description="Eimeria praecox - Proteome: UP000018201",
        meaning=NCBITAXON["51316"])
    SP_9EMBE = PermissibleValue(
        text="SP_9EMBE",
        title="Emberiza fucata",
        description="Emberiza fucata - Proteome: UP000580681",
        meaning=NCBITAXON["337179"])
    SP_9ENTE = PermissibleValue(
        text="SP_9ENTE",
        title="Enterococcus asini ATCC 700915",
        description="Enterococcus asini ATCC 700915 - Proteome: UP000013777",
        meaning=NCBITAXON["1158606"])
    SP_9ENTR = PermissibleValue(
        text="SP_9ENTR",
        title="secondary endosymbiont of Heteropsylla cubana",
        description="secondary endosymbiont of Heteropsylla cubana - Proteome: UP000003937",
        meaning=NCBITAXON["134287"])
    SP_9ERIC = PermissibleValue(
        text="SP_9ERIC",
        title="Rhododendron williamsianum",
        description="Rhododendron williamsianum - Proteome: UP000428333",
        meaning=NCBITAXON["262921"])
    SP_9EUCA = PermissibleValue(
        text="SP_9EUCA",
        title="Petrolisthes manimaculis",
        description="Petrolisthes manimaculis - Proteome: UP001292094",
        meaning=NCBITAXON["1843537"])
    SP_9EUGL = PermissibleValue(
        text="SP_9EUGL",
        title="Perkinsela sp. CCAP 1560/4",
        description="Perkinsela sp. CCAP 1560/4 - Proteome: UP000036983",
        meaning=NCBITAXON["1314962"])
    SP_9EUKA = PermissibleValue(
        text="SP_9EUKA",
        title="Chrysochromulina tobinii",
        description="Chrysochromulina tobinii - Proteome: UP000037460",
        meaning=NCBITAXON["1460289"])
    SP_9EUPU = PermissibleValue(
        text="SP_9EUPU",
        title="Candidula unifasciata",
        description="Candidula unifasciata - Proteome: UP000678393",
        meaning=NCBITAXON["100452"])
    SP_9EURO = PermissibleValue(
        text="SP_9EURO",
        title="Cladophialophora psammophila CBS 110553",
        description="Cladophialophora psammophila CBS 110553 - Proteome: UP000019471",
        meaning=NCBITAXON["1182543"])
    SP_9EURY = PermissibleValue(
        text="SP_9EURY",
        title="Methanoplanus limicola DSM 2279",
        description="Methanoplanus limicola DSM 2279 - Proteome: UP000005741",
        meaning=NCBITAXON["937775"])
    SP_9FABA = PermissibleValue(
        text="SP_9FABA",
        title="Senna tora",
        description="Senna tora - Proteome: UP000634136",
        meaning=NCBITAXON["362788"])
    SP_9FIRM = PermissibleValue(
        text="SP_9FIRM",
        title="Ruminococcaceae bacterium D16",
        description="Ruminococcaceae bacterium D16 - Proteome: UP000002801",
        meaning=NCBITAXON["552398"])
    SP_9FLAO = PermissibleValue(
        text="SP_9FLAO",
        title="Capnocytophaga sp. oral taxon 338 str. F0234",
        description="Capnocytophaga sp. oral taxon 338 str. F0234 - Proteome: UP000003023",
        meaning=NCBITAXON["888059"])
    SP_9FLAV = PermissibleValue(
        text="SP_9FLAV",
        title="Tunisian sheep-like pestivirus",
        description="Tunisian sheep-like pestivirus - Proteome: UP001157330",
        meaning=NCBITAXON["3071305"])
    SP_9FLOR = PermissibleValue(
        text="SP_9FLOR",
        title="Gracilariopsis chorda",
        description="Gracilariopsis chorda - Proteome: UP000247409",
        meaning=NCBITAXON["448386"])
    SP_9FRIN = PermissibleValue(
        text="SP_9FRIN",
        title="Urocynchramus pylzowi",
        description="Urocynchramus pylzowi - Proteome: UP000524542",
        meaning=NCBITAXON["571890"])
    SP_9FUNG = PermissibleValue(
        text="SP_9FUNG",
        title="Lichtheimia corymbifera JMRC:FSU:9682",
        description="Lichtheimia corymbifera JMRC:FSU:9682 - Proteome: UP000027586",
        meaning=NCBITAXON["1263082"])
    SP_9FURN = PermissibleValue(
        text="SP_9FURN",
        title="Furnarius figulus",
        description="Furnarius figulus - Proteome: UP000529852",
        meaning=NCBITAXON["463165"])
    SP_9FUSO = PermissibleValue(
        text="SP_9FUSO",
        title="Fusobacterium gonidiaformans 3-1-5R",
        description="Fusobacterium gonidiaformans 3-1-5R - Proteome: UP000002975",
        meaning=NCBITAXON["469605"])
    SP_9GALL = PermissibleValue(
        text="SP_9GALL",
        title="Odontophorus gujanensis",
        description="Odontophorus gujanensis (marbled wood quail) - Proteome: UP000522663",
        meaning=NCBITAXON["886794"])
    SP_9GAMA = PermissibleValue(
        text="SP_9GAMA",
        title="Bovine gammaherpesvirus 6",
        description="Bovine gammaherpesvirus 6 - Proteome: UP000121539",
        meaning=NCBITAXON["1504288"])
    SP_9GAMC = PermissibleValue(
        text="SP_9GAMC",
        title="Anser fabalis coronavirus NCN2",
        description="Anser fabalis coronavirus NCN2 - Proteome: UP001251675",
        meaning=NCBITAXON["2860474"])
    SP_9GAMM = PermissibleValue(
        text="SP_9GAMM",
        title="Buchnera aphidicola",
        description="Buchnera aphidicola (Cinara tujafilina) - Proteome: UP000006811",
        meaning=NCBITAXON["261317"])
    SP_9GAST = PermissibleValue(
        text="SP_9GAST",
        title="Elysia crispata",
        description="Elysia crispata (lettuce slug) - Proteome: UP001283361",
        meaning=NCBITAXON["231223"])
    SP_9GEMI = PermissibleValue(
        text="SP_9GEMI",
        title="East African cassava mosaic Zanzibar virus",
        description="East African cassava mosaic Zanzibar virus - Proteome: UP000201107",
        meaning=NCBITAXON["223275"])
    SP_9GLOM = PermissibleValue(
        text="SP_9GLOM",
        title="Paraglomus occultum",
        description="Paraglomus occultum - Proteome: UP000789572",
        meaning=NCBITAXON["144539"])
    SP_9GOBI = PermissibleValue(
        text="SP_9GOBI",
        title="Neogobius melanostomus",
        description="Neogobius melanostomus (round goby) - Proteome: UP000694523",
        meaning=NCBITAXON["47308"])
    SP_9GRUI = PermissibleValue(
        text="SP_9GRUI",
        title="Atlantisia rogersi",
        description="Atlantisia rogersi (Inaccessible Island rail) - Proteome: UP000518911",
        meaning=NCBITAXON["2478892"])
    SP_9HELI = PermissibleValue(
        text="SP_9HELI",
        title="Helicobacter bilis ATCC 43879",
        description="Helicobacter bilis ATCC 43879 - Proteome: UP000005085",
        meaning=NCBITAXON["613026"])
    SP_9HELO = PermissibleValue(
        text="SP_9HELO",
        title="Rhynchosporium graminicola",
        description="Rhynchosporium graminicola - Proteome: UP000178129",
        meaning=NCBITAXON["2792576"])
    SP_9HEMI = PermissibleValue(
        text="SP_9HEMI",
        title="Cinara cedri",
        description="Cinara cedri - Proteome: UP000325440",
        meaning=NCBITAXON["506608"])
    SP_9HEPA = PermissibleValue(
        text="SP_9HEPA",
        title="Duck hepatitis B virus",
        description="Duck hepatitis B virus - Proteome: UP000137229",
        meaning=NCBITAXON["12639"])
    SP_9HEXA = PermissibleValue(
        text="SP_9HEXA",
        title="Allacma fusca",
        description="Allacma fusca - Proteome: UP000708208",
        meaning=NCBITAXON["39272"])
    SP_9HYME = PermissibleValue(
        text="SP_9HYME",
        title="Melipona quadrifasciata",
        description="Melipona quadrifasciata - Proteome: UP000053105",
        meaning=NCBITAXON["166423"])
    SP_9HYPH = PermissibleValue(
        text="SP_9HYPH",
        title="Mesorhizobium amorphae CCNWGS0123",
        description="Mesorhizobium amorphae CCNWGS0123 - Proteome: UP000002949",
        meaning=NCBITAXON["1082933"])
    SP_9HYPO = PermissibleValue(
        text="SP_9HYPO",
        title="[Torrubiella] hemipterigena",
        description="[Torrubiella] hemipterigena - Proteome: UP000039046",
        meaning=NCBITAXON["1531966"])
    SP_9INFA = PermissibleValue(
        text="SP_9INFA",
        title="Influenza A virus (A/California/VRDL364/2009",
        description="Influenza A virus (A/California/VRDL364/2009 (mixed) - Proteome: UP000109975",
        meaning=NCBITAXON["1049605"])
    SP_9INSE = PermissibleValue(
        text="SP_9INSE",
        title="Cloeon dipterum",
        description="Cloeon dipterum - Proteome: UP000494165",
        meaning=NCBITAXON["197152"])
    SP_9LABR = PermissibleValue(
        text="SP_9LABR",
        title="Labrus bergylta",
        description="Labrus bergylta (ballan wrasse) - Proteome: UP000261660",
        meaning=NCBITAXON["56723"])
    SP_ARATH = PermissibleValue(
        text="SP_ARATH",
        title="Arabidopsis thaliana",
        description="Arabidopsis thaliana (Thale cress) - Proteome: UP000006548",
        meaning=NCBITAXON["3702"])
    SP_BACSU = PermissibleValue(
        text="SP_BACSU",
        title="Bacillus subtilis subsp. subtilis str. 168",
        description="Bacillus subtilis subsp. subtilis str. 168 - Proteome: UP000001570",
        meaning=NCBITAXON["224308"])
    SP_BOVIN = PermissibleValue(
        text="SP_BOVIN",
        title="Bos taurus",
        description="Bos taurus (Cattle) - Proteome: UP000009136",
        meaning=NCBITAXON["9913"])
    SP_CAEEL = PermissibleValue(
        text="SP_CAEEL",
        title="Caenorhabditis elegans",
        description="Caenorhabditis elegans - Proteome: UP000001940",
        meaning=NCBITAXON["6239"])
    SP_CANLF = PermissibleValue(
        text="SP_CANLF",
        title="Canis lupus familiaris",
        description="Canis lupus familiaris (Dog) - Proteome: UP000805418",
        meaning=NCBITAXON["9615"])
    SP_CHICK = PermissibleValue(
        text="SP_CHICK",
        title="Gallus gallus",
        description="Gallus gallus (Chicken) - Proteome: UP000000539",
        meaning=NCBITAXON["9031"])
    SP_DANRE = PermissibleValue(
        text="SP_DANRE",
        title="Danio rerio",
        description="Danio rerio (Zebrafish) - Proteome: UP000000437",
        meaning=NCBITAXON["7955"])
    SP_DROME = PermissibleValue(
        text="SP_DROME",
        title="Drosophila melanogaster",
        description="Drosophila melanogaster (Fruit fly) - Proteome: UP000000803",
        meaning=NCBITAXON["7227"])
    SP_ECOLI = PermissibleValue(
        text="SP_ECOLI",
        title="Escherichia coli K-12",
        description="Escherichia coli K-12 - Proteome: UP000000625",
        meaning=NCBITAXON["83333"])
    SP_FELCA = PermissibleValue(
        text="SP_FELCA",
        title="Felis catus",
        description="Felis catus (Cat) - Proteome: UP000011712",
        meaning=NCBITAXON["9685"])
    SP_GORGO = PermissibleValue(
        text="SP_GORGO",
        title="Gorilla gorilla gorilla",
        description="Gorilla gorilla gorilla (Western lowland gorilla) - Proteome: UP000001519",
        meaning=NCBITAXON["9593"])
    SP_HORSE = PermissibleValue(
        text="SP_HORSE",
        title="Equus caballus",
        description="Equus caballus (Horse) - Proteome: UP000002281",
        meaning=NCBITAXON["9796"])
    SP_HUMAN = PermissibleValue(
        text="SP_HUMAN",
        title="Homo sapiens",
        description="Homo sapiens (Human) - Proteome: UP000005640",
        meaning=NCBITAXON["9606"])
    SP_MACMU = PermissibleValue(
        text="SP_MACMU",
        title="Macaca mulatta",
        description="Macaca mulatta (Rhesus macaque) - Proteome: UP000006718",
        meaning=NCBITAXON["9544"])
    SP_MAIZE = PermissibleValue(
        text="SP_MAIZE",
        title="Zea mays",
        description="Zea mays (Maize) - Proteome: UP000007305",
        meaning=NCBITAXON["4577"])
    SP_MOUSE = PermissibleValue(
        text="SP_MOUSE",
        title="Mus musculus",
        description="Mus musculus (Mouse) - Proteome: UP000000589",
        meaning=NCBITAXON["10090"])
    SP_ORYSJ = PermissibleValue(
        text="SP_ORYSJ",
        title="Oryza sativa subsp. japonica",
        description="Oryza sativa subsp. japonica (Rice) - Proteome: UP000059680",
        meaning=NCBITAXON["39947"])
    SP_PANTR = PermissibleValue(
        text="SP_PANTR",
        title="Pan troglodytes",
        description="Pan troglodytes (Chimpanzee) - Proteome: UP000002277",
        meaning=NCBITAXON["9598"])
    SP_PIG = PermissibleValue(
        text="SP_PIG",
        title="Sus scrofa",
        description="Sus scrofa (Pig) - Proteome: UP000008227",
        meaning=NCBITAXON["9823"])
    SP_RABIT = PermissibleValue(
        text="SP_RABIT",
        title="Oryctolagus cuniculus",
        description="Oryctolagus cuniculus (Rabbit) - Proteome: UP000001811",
        meaning=NCBITAXON["9986"])
    SP_RAT = PermissibleValue(
        text="SP_RAT",
        title="Rattus norvegicus",
        description="Rattus norvegicus (Rat) - Proteome: UP000002494",
        meaning=NCBITAXON["10116"])
    SP_SCHPO = PermissibleValue(
        text="SP_SCHPO",
        title="Schizosaccharomyces pombe 972h-",
        description="Schizosaccharomyces pombe 972h- (Fission yeast) - Proteome: UP000002485",
        meaning=NCBITAXON["284812"])
    SP_SHEEP = PermissibleValue(
        text="SP_SHEEP",
        title="Ovis aries",
        description="Ovis aries (Sheep) - Proteome: UP000002356",
        meaning=NCBITAXON["9940"])
    SP_XENLA = PermissibleValue(
        text="SP_XENLA",
        title="Xenopus laevis",
        description="Xenopus laevis (African clawed frog) - Proteome: UP000186698",
        meaning=NCBITAXON["8355"])
    SP_XENTR = PermissibleValue(
        text="SP_XENTR",
        title="Xenopus tropicalis",
        description="Xenopus tropicalis (Western clawed frog) - Proteome: UP000008143",
        meaning=NCBITAXON["8364"])
    SP_YEAST = PermissibleValue(
        text="SP_YEAST",
        title="Saccharomyces cerevisiae S288C",
        description="Saccharomyces cerevisiae S288C (Baker's yeast) - Proteome: UP000002311",
        meaning=NCBITAXON["559292"])
    SP_DICDI = PermissibleValue(
        text="SP_DICDI",
        title="Dictyostelium discoideum",
        description="Dictyostelium discoideum (Slime mold) - Proteome: UP000002195",
        meaning=NCBITAXON["44689"])
    SP_HELPY = PermissibleValue(
        text="SP_HELPY",
        title="Helicobacter pylori 26695",
        description="Helicobacter pylori 26695 - Proteome: UP000000429",
        meaning=NCBITAXON["85962"])
    SP_LEIMA = PermissibleValue(
        text="SP_LEIMA",
        title="Leishmania major strain Friedlin",
        description="Leishmania major strain Friedlin",
        meaning=NCBITAXON["347515"])
    SP_MEDTR = PermissibleValue(
        text="SP_MEDTR",
        title="Medicago truncatula",
        description="Medicago truncatula (Barrel medic) - Proteome: UP000002051",
        meaning=NCBITAXON["3880"])
    SP_MYCTU = PermissibleValue(
        text="SP_MYCTU",
        title="Mycobacterium tuberculosis H37Rv",
        description="Mycobacterium tuberculosis H37Rv - Proteome: UP000001584",
        meaning=NCBITAXON["83332"])
    SP_NEIME = PermissibleValue(
        text="SP_NEIME",
        title="Neisseria meningitidis MC58",
        description="Neisseria meningitidis MC58 - Proteome: UP000000425",
        meaning=NCBITAXON["122586"])
    SP_PLAF7 = PermissibleValue(
        text="SP_PLAF7",
        title="Plasmodium falciparum 3D7",
        description="Plasmodium falciparum 3D7 (Malaria parasite) - Proteome: UP000001450",
        meaning=NCBITAXON["36329"])
    SP_PSEAE = PermissibleValue(
        text="SP_PSEAE",
        title="Pseudomonas aeruginosa PAO1",
        description="Pseudomonas aeruginosa PAO1 - Proteome: UP000002438",
        meaning=NCBITAXON["208964"])
    SP_SOYBN = PermissibleValue(
        text="SP_SOYBN",
        title="Glycine max",
        description="Glycine max (Soybean) - Proteome: UP000008827",
        meaning=NCBITAXON["3847"])
    SP_STAAU = PermissibleValue(
        text="SP_STAAU",
        title="Staphylococcus aureus subsp. aureus NCTC 8325",
        description="Staphylococcus aureus subsp. aureus NCTC 8325 - Proteome: UP000008816",
        meaning=NCBITAXON["93061"])
    SP_STRPN = PermissibleValue(
        text="SP_STRPN",
        title="Streptococcus pneumoniae R6",
        description="Streptococcus pneumoniae R6 - Proteome: UP000000586",
        meaning=NCBITAXON["171101"])
    SP_TOXGO = PermissibleValue(
        text="SP_TOXGO",
        title="Toxoplasma gondii ME49",
        description="Toxoplasma gondii ME49 - Proteome: UP000001529",
        meaning=NCBITAXON["508771"])
    SP_TRYB2 = PermissibleValue(
        text="SP_TRYB2",
        title="Trypanosoma brucei brucei TREU927",
        description="Trypanosoma brucei brucei TREU927 - Proteome: UP000008524",
        meaning=NCBITAXON["185431"])
    SP_WHEAT = PermissibleValue(
        text="SP_WHEAT",
        title="Triticum aestivum",
        description="Triticum aestivum (Wheat) - Proteome: UP000019116",
        meaning=NCBITAXON["4565"])
    SP_PEA = PermissibleValue(
        text="SP_PEA",
        title="Pisum sativum",
        description="Pisum sativum (Garden pea) - Proteome: UP001058974",
        meaning=NCBITAXON["3888"])
    SP_TOBAC = PermissibleValue(
        text="SP_TOBAC",
        title="Nicotiana tabacum",
        description="Nicotiana tabacum (Common tobacco) - Proteome: UP000084051",
        meaning=NCBITAXON["4097"])

    _defn = EnumDefinition(
        name="UniProtSpeciesCode",
        description="UniProt species mnemonic codes for reference proteomes with associated metadata",
    )

class LipidCategory(EnumDefinitionImpl):
    """
    Major categories of lipids based on SwissLipids classification
    """
    LIPID = PermissibleValue(
        text="LIPID",
        description="Lipid",
        meaning=CHEBI["18059"])
    FATTY_ACYLS_AND_DERIVATIVES = PermissibleValue(
        text="FATTY_ACYLS_AND_DERIVATIVES",
        description="Fatty acyls and derivatives",
        meaning=CHEBI["24027"])
    GLYCEROLIPIDS = PermissibleValue(
        text="GLYCEROLIPIDS",
        description="Glycerolipids",
        meaning=CHEBI["35741"])
    GLYCEROPHOSPHOLIPIDS = PermissibleValue(
        text="GLYCEROPHOSPHOLIPIDS",
        description="Glycerophospholipids",
        meaning=CHEBI["37739"])
    SPHINGOLIPIDS = PermissibleValue(
        text="SPHINGOLIPIDS",
        description="Sphingolipids",
        meaning=CHEBI["26739"])
    STEROIDS_AND_DERIVATIVES = PermissibleValue(
        text="STEROIDS_AND_DERIVATIVES",
        description="Steroids and derivatives",
        meaning=CHEBI["35341"])
    PRENOL_LIPIDS = PermissibleValue(
        text="PRENOL_LIPIDS",
        description="Prenol Lipids",
        meaning=CHEBI["24913"])

    _defn = EnumDefinition(
        name="LipidCategory",
        description="Major categories of lipids based on SwissLipids classification",
    )

class PeakAnnotationSeriesLabel(EnumDefinitionImpl):
    """
    Types of peak annotations in mass spectrometry data
    """
    PEPTIDE = PermissibleValue(
        text="PEPTIDE",
        description="Peptide fragment ion")
    INTERNAL = PermissibleValue(
        text="INTERNAL",
        description="Internal fragment ion")
    PRECURSOR = PermissibleValue(
        text="PRECURSOR",
        description="Precursor ion")
    IMMONIUM = PermissibleValue(
        text="IMMONIUM",
        description="Immonium ion")
    REFERENCE = PermissibleValue(
        text="REFERENCE",
        description="Reference peak or calibrant")
    NAMED_COMPOUND = PermissibleValue(
        text="NAMED_COMPOUND",
        description="Named chemical compound")
    FORMULA = PermissibleValue(
        text="FORMULA",
        description="Chemical formula")
    SMILES = PermissibleValue(
        text="SMILES",
        description="SMILES structure notation")
    UNANNOTATED = PermissibleValue(
        text="UNANNOTATED",
        description="Unannotated peak")

    _defn = EnumDefinition(
        name="PeakAnnotationSeriesLabel",
        description="Types of peak annotations in mass spectrometry data",
    )

class PeptideIonSeries(EnumDefinitionImpl):
    """
    Types of peptide fragment ion series in mass spectrometry
    """
    B = PermissibleValue(
        text="B",
        description="B ion series - N-terminal fragment with CO")
    Y = PermissibleValue(
        text="Y",
        description="Y ion series - C-terminal fragment with H")
    A = PermissibleValue(
        text="A",
        description="A ion series - N-terminal fragment minus CO")
    X = PermissibleValue(
        text="X",
        description="X ion series - C-terminal fragment plus CO")
    C = PermissibleValue(
        text="C",
        description="C ion series - N-terminal fragment with NH3")
    Z = PermissibleValue(
        text="Z",
        description="Z ion series - C-terminal fragment minus NH")
    D = PermissibleValue(
        text="D",
        description="D ion series - partial side chain cleavage")
    V = PermissibleValue(
        text="V",
        description="V ion series - side chain loss from y ion")
    W = PermissibleValue(
        text="W",
        description="W ion series - side chain loss from z ion")
    DA = PermissibleValue(
        text="DA",
        description="DA ion series - a ion with side chain loss")
    DB = PermissibleValue(
        text="DB",
        description="DB ion series - b ion with side chain loss")
    WA = PermissibleValue(
        text="WA",
        description="WA ion series - a ion with tryptophan side chain loss")
    WB = PermissibleValue(
        text="WB",
        description="WB ion series - b ion with tryptophan side chain loss")

    _defn = EnumDefinition(
        name="PeptideIonSeries",
        description="Types of peptide fragment ion series in mass spectrometry",
    )

class MassErrorUnit(EnumDefinitionImpl):
    """
    Units for expressing mass error in mass spectrometry
    """
    PPM = PermissibleValue(
        text="PPM",
        description="Parts per million - relative mass error")
    DA = PermissibleValue(
        text="DA",
        description="Dalton - absolute mass error")

    _defn = EnumDefinition(
        name="MassErrorUnit",
        description="Units for expressing mass error in mass spectrometry",
    )

class InteractionDetectionMethod(EnumDefinitionImpl):
    """
    Methods used to detect molecular interactions
    """
    TWO_HYBRID = PermissibleValue(
        text="TWO_HYBRID",
        description="Classical two-hybrid system using transcriptional activity",
        meaning=MI["0018"])
    COIMMUNOPRECIPITATION = PermissibleValue(
        text="COIMMUNOPRECIPITATION",
        description="Using antibody to capture bait and its ligands",
        meaning=MI["0019"])
    PULL_DOWN = PermissibleValue(
        text="PULL_DOWN",
        description="Affinity capture using immobilized bait",
        meaning=MI["0096"])
    TANDEM_AFFINITY_PURIFICATION = PermissibleValue(
        text="TANDEM_AFFINITY_PURIFICATION",
        description="TAP tagging for protein complex purification",
        meaning=MI["0676"])
    FLUORESCENCE_RESONANCE_ENERGY_TRANSFER = PermissibleValue(
        text="FLUORESCENCE_RESONANCE_ENERGY_TRANSFER",
        description="FRET for detecting proximity between molecules",
        meaning=MI["0055"])
    SURFACE_PLASMON_RESONANCE = PermissibleValue(
        text="SURFACE_PLASMON_RESONANCE",
        description="SPR for real-time binding analysis",
        meaning=MI["0107"])
    CROSS_LINKING = PermissibleValue(
        text="CROSS_LINKING",
        description="Chemical cross-linking of interacting proteins",
        meaning=MI["0030"])
    X_RAY_CRYSTALLOGRAPHY = PermissibleValue(
        text="X_RAY_CRYSTALLOGRAPHY",
        description="Crystal structure determination",
        meaning=MI["0114"])
    NMR = PermissibleValue(
        text="NMR",
        description="Nuclear magnetic resonance spectroscopy",
        meaning=MI["0077"])
    ELECTRON_MICROSCOPY = PermissibleValue(
        text="ELECTRON_MICROSCOPY",
        description="EM for structural determination",
        meaning=MI["0040"])
    MASS_SPECTROMETRY = PermissibleValue(
        text="MASS_SPECTROMETRY",
        description="MS-based interaction detection",
        meaning=MI["0943"])
    PROXIMITY_LIGATION_ASSAY = PermissibleValue(
        text="PROXIMITY_LIGATION_ASSAY",
        description="PLA for detecting protein proximity",
        meaning=MI["0813"])
    BIMOLECULAR_FLUORESCENCE_COMPLEMENTATION = PermissibleValue(
        text="BIMOLECULAR_FLUORESCENCE_COMPLEMENTATION",
        description="BiFC split fluorescent protein assay",
        meaning=MI["0809"])
    YEAST_TWO_HYBRID = PermissibleValue(
        text="YEAST_TWO_HYBRID",
        description="Y2H screening in yeast",
        meaning=MI["0018"])
    MAMMALIAN_TWO_HYBRID = PermissibleValue(
        text="MAMMALIAN_TWO_HYBRID",
        description="Two-hybrid in mammalian cells",
        meaning=MI["2413"])

    _defn = EnumDefinition(
        name="InteractionDetectionMethod",
        description="Methods used to detect molecular interactions",
    )

class InteractionType(EnumDefinitionImpl):
    """
    Types of molecular interactions
    """
    PHYSICAL_ASSOCIATION = PermissibleValue(
        text="PHYSICAL_ASSOCIATION",
        description="Molecules within the same physical complex",
        meaning=MI["0915"])
    DIRECT_INTERACTION = PermissibleValue(
        text="DIRECT_INTERACTION",
        description="Direct physical contact between molecules",
        meaning=MI["0407"])
    ASSOCIATION = PermissibleValue(
        text="ASSOCIATION",
        description="May form one or more physical complexes",
        meaning=MI["0914"])
    COLOCALIZATION = PermissibleValue(
        text="COLOCALIZATION",
        description="Coincident occurrence in subcellular location",
        meaning=MI["0403"])
    FUNCTIONAL_ASSOCIATION = PermissibleValue(
        text="FUNCTIONAL_ASSOCIATION",
        description="Functional modulation without direct contact",
        meaning=MI["2286"])
    ENZYMATIC_REACTION = PermissibleValue(
        text="ENZYMATIC_REACTION",
        description="Enzyme-substrate relationship",
        meaning=MI["0414"])
    PHOSPHORYLATION_REACTION = PermissibleValue(
        text="PHOSPHORYLATION_REACTION",
        description="Kinase-substrate phosphorylation",
        meaning=MI["0217"])
    UBIQUITINATION_REACTION = PermissibleValue(
        text="UBIQUITINATION_REACTION",
        description="Ubiquitin ligase-substrate relationship",
        meaning=MI["0220"])
    ACETYLATION_REACTION = PermissibleValue(
        text="ACETYLATION_REACTION",
        description="Acetyltransferase-substrate relationship",
        meaning=MI["0192"])
    METHYLATION_REACTION = PermissibleValue(
        text="METHYLATION_REACTION",
        description="Methyltransferase-substrate relationship",
        meaning=MI["0213"])
    CLEAVAGE_REACTION = PermissibleValue(
        text="CLEAVAGE_REACTION",
        description="Protease-substrate relationship",
        meaning=MI["0194"])
    GENETIC_INTERACTION = PermissibleValue(
        text="GENETIC_INTERACTION",
        description="Genetic epistatic relationship",
        meaning=MI["0208"])
    SELF_INTERACTION = PermissibleValue(
        text="SELF_INTERACTION",
        description="Intra-molecular interaction",
        meaning=MI["1126"])

    _defn = EnumDefinition(
        name="InteractionType",
        description="Types of molecular interactions",
    )

class ExperimentalRole(EnumDefinitionImpl):
    """
    Role played by a participant in the experiment
    """
    BAIT = PermissibleValue(
        text="BAIT",
        description="Molecule used to capture interacting partners",
        meaning=MI["0496"])
    PREY = PermissibleValue(
        text="PREY",
        description="Molecule captured by the bait",
        meaning=MI["0498"])
    NEUTRAL_COMPONENT = PermissibleValue(
        text="NEUTRAL_COMPONENT",
        description="Participant with no specific role",
        meaning=MI["0497"])
    ENZYME = PermissibleValue(
        text="ENZYME",
        description="Catalytically active participant",
        meaning=MI["0501"])
    ENZYME_TARGET = PermissibleValue(
        text="ENZYME_TARGET",
        description="Target of enzymatic activity",
        meaning=MI["0502"])
    SELF = PermissibleValue(
        text="SELF",
        description="Self-interaction participant",
        meaning=MI["0503"])
    PUTATIVE_SELF = PermissibleValue(
        text="PUTATIVE_SELF",
        description="Potentially self-interacting",
        meaning=MI["0898"])
    ANCILLARY = PermissibleValue(
        text="ANCILLARY",
        description="Supporting but not directly interacting",
        meaning=MI["0684"])
    COFACTOR = PermissibleValue(
        text="COFACTOR",
        description="Required cofactor for interaction",
        meaning=MI["0682"])
    INHIBITOR = PermissibleValue(
        text="INHIBITOR",
        description="Inhibitor of the interaction",
        meaning=MI["0586"])
    STIMULATOR = PermissibleValue(
        text="STIMULATOR",
        description="Enhancer of the interaction",
        meaning=MI["0840"])
    COMPETITOR = PermissibleValue(
        text="COMPETITOR",
        description="Competitive inhibitor",
        meaning=MI["0941"])

    _defn = EnumDefinition(
        name="ExperimentalRole",
        description="Role played by a participant in the experiment",
    )

class BiologicalRole(EnumDefinitionImpl):
    """
    Physiological role of an interactor
    """
    ENZYME = PermissibleValue(
        text="ENZYME",
        description="Catalytically active molecule",
        meaning=MI["0501"])
    ENZYME_TARGET = PermissibleValue(
        text="ENZYME_TARGET",
        description="Substrate of enzymatic activity",
        meaning=MI["0502"])
    ELECTRON_DONOR = PermissibleValue(
        text="ELECTRON_DONOR",
        description="Donates electrons in reaction",
        meaning=MI["0579"])
    ELECTRON_ACCEPTOR = PermissibleValue(
        text="ELECTRON_ACCEPTOR",
        description="Accepts electrons in reaction",
        meaning=MI["0580"])
    INHIBITOR = PermissibleValue(
        text="INHIBITOR",
        description="Inhibits activity or interaction",
        meaning=MI["0586"])
    COFACTOR = PermissibleValue(
        text="COFACTOR",
        description="Required for activity",
        meaning=MI["0682"])
    LIGAND = PermissibleValue(
        text="LIGAND",
        description="Small molecule binding partner")
    AGONIST = PermissibleValue(
        text="AGONIST",
        description="Activates receptor",
        meaning=MI["0625"])
    ANTAGONIST = PermissibleValue(
        text="ANTAGONIST",
        description="Blocks receptor activation",
        meaning=MI["0626"])
    PHOSPHATE_DONOR = PermissibleValue(
        text="PHOSPHATE_DONOR",
        description="Provides phosphate group",
        meaning=MI["0842"])
    PHOSPHATE_ACCEPTOR = PermissibleValue(
        text="PHOSPHATE_ACCEPTOR",
        description="Receives phosphate group",
        meaning=MI["0843"])

    _defn = EnumDefinition(
        name="BiologicalRole",
        description="Physiological role of an interactor",
    )

class ParticipantIdentificationMethod(EnumDefinitionImpl):
    """
    Methods to identify interaction participants
    """
    MASS_SPECTROMETRY = PermissibleValue(
        text="MASS_SPECTROMETRY",
        description="MS-based protein identification",
        meaning=MI["0943"])
    WESTERN_BLOT = PermissibleValue(
        text="WESTERN_BLOT",
        description="Antibody-based detection",
        meaning=MI["0113"])
    SEQUENCE_TAG_IDENTIFICATION = PermissibleValue(
        text="SEQUENCE_TAG_IDENTIFICATION",
        description="Using affinity tags",
        meaning=MI["0102"])
    ANTIBODY_DETECTION = PermissibleValue(
        text="ANTIBODY_DETECTION",
        description="Direct antibody recognition",
        meaning=MI["0678"])
    PREDETERMINED = PermissibleValue(
        text="PREDETERMINED",
        description="Known from experimental design",
        meaning=MI["0396"])
    NUCLEIC_ACID_SEQUENCING = PermissibleValue(
        text="NUCLEIC_ACID_SEQUENCING",
        description="DNA/RNA sequencing",
        meaning=MI["0078"])
    PROTEIN_SEQUENCING = PermissibleValue(
        text="PROTEIN_SEQUENCING",
        description="Direct protein sequencing")

    _defn = EnumDefinition(
        name="ParticipantIdentificationMethod",
        description="Methods to identify interaction participants",
    )

class FeatureType(EnumDefinitionImpl):
    """
    Molecular features affecting interactions
    """
    BINDING_SITE = PermissibleValue(
        text="BINDING_SITE",
        description="Region involved in binding",
        meaning=MI["0117"])
    MUTATION = PermissibleValue(
        text="MUTATION",
        description="Sequence alteration",
        meaning=MI["0118"])
    POST_TRANSLATIONAL_MODIFICATION = PermissibleValue(
        text="POST_TRANSLATIONAL_MODIFICATION",
        description="PTM site",
        meaning=MI["0121"])
    TAG = PermissibleValue(
        text="TAG",
        description="Affinity or epitope tag",
        meaning=MI["0507"])
    CROSS_LINK = PermissibleValue(
        text="CROSS_LINK",
        description="Cross-linking site")
    LIPIDATION_SITE = PermissibleValue(
        text="LIPIDATION_SITE",
        description="Lipid modification site")
    PHOSPHORYLATION_SITE = PermissibleValue(
        text="PHOSPHORYLATION_SITE",
        description="Phosphorylated residue",
        meaning=MI["0170"])
    UBIQUITINATION_SITE = PermissibleValue(
        text="UBIQUITINATION_SITE",
        description="Ubiquitinated residue")
    METHYLATION_SITE = PermissibleValue(
        text="METHYLATION_SITE",
        description="Methylated residue")
    ACETYLATION_SITE = PermissibleValue(
        text="ACETYLATION_SITE",
        description="Acetylated residue")
    SUMOYLATION_SITE = PermissibleValue(
        text="SUMOYLATION_SITE",
        description="SUMOylated residue")
    NECESSARY_BINDING_REGION = PermissibleValue(
        text="NECESSARY_BINDING_REGION",
        description="Required for binding",
        meaning=MI["0429"])
    SUFFICIENT_BINDING_REGION = PermissibleValue(
        text="SUFFICIENT_BINDING_REGION",
        description="Sufficient for binding",
        meaning=MI["0442"])

    _defn = EnumDefinition(
        name="FeatureType",
        description="Molecular features affecting interactions",
    )

class InteractorType(EnumDefinitionImpl):
    """
    Types of molecular species in interactions
    """
    PROTEIN = PermissibleValue(
        text="PROTEIN",
        description="Polypeptide molecule",
        meaning=MI["0326"])
    PEPTIDE = PermissibleValue(
        text="PEPTIDE",
        description="Short polypeptide",
        meaning=MI["0327"])
    SMALL_MOLECULE = PermissibleValue(
        text="SMALL_MOLECULE",
        description="Small chemical compound",
        meaning=MI["0328"])
    DNA = PermissibleValue(
        text="DNA",
        description="Deoxyribonucleic acid",
        meaning=MI["0319"])
    RNA = PermissibleValue(
        text="RNA",
        description="Ribonucleic acid",
        meaning=MI["0320"])
    PROTEIN_COMPLEX = PermissibleValue(
        text="PROTEIN_COMPLEX",
        description="Multi-protein assembly",
        meaning=MI["0314"])
    GENE = PermissibleValue(
        text="GENE",
        description="Gene locus",
        meaning=MI["0250"])
    BIOPOLYMER = PermissibleValue(
        text="BIOPOLYMER",
        description="Biological polymer",
        meaning=MI["0383"])
    POLYSACCHARIDE = PermissibleValue(
        text="POLYSACCHARIDE",
        description="Carbohydrate polymer",
        meaning=MI["0904"])
    LIPID = PermissibleValue(
        text="LIPID",
        description="Lipid molecule")
    NUCLEIC_ACID = PermissibleValue(
        text="NUCLEIC_ACID",
        description="DNA or RNA",
        meaning=MI["0318"])
    SYNTHETIC_POLYMER = PermissibleValue(
        text="SYNTHETIC_POLYMER",
        description="Artificial polymer")
    METAL_ION = PermissibleValue(
        text="METAL_ION",
        description="Metal ion cofactor")

    _defn = EnumDefinition(
        name="InteractorType",
        description="Types of molecular species in interactions",
    )

class ConfidenceScore(EnumDefinitionImpl):
    """
    Types of confidence scoring methods
    """
    INTACT_MISCORE = PermissibleValue(
        text="INTACT_MISCORE",
        description="IntAct molecular interaction score")
    AUTHOR_CONFIDENCE = PermissibleValue(
        text="AUTHOR_CONFIDENCE",
        description="Author-provided confidence",
        meaning=MI["0621"])
    INTACT_CONFIDENCE = PermissibleValue(
        text="INTACT_CONFIDENCE",
        description="IntAct curation confidence")
    MINT_SCORE = PermissibleValue(
        text="MINT_SCORE",
        description="MINT database score")
    MATRIXDB_SCORE = PermissibleValue(
        text="MATRIXDB_SCORE",
        description="MatrixDB confidence score")

    _defn = EnumDefinition(
        name="ConfidenceScore",
        description="Types of confidence scoring methods",
    )

class ExperimentalPreparation(EnumDefinitionImpl):
    """
    Sample preparation methods
    """
    RECOMBINANT_EXPRESSION = PermissibleValue(
        text="RECOMBINANT_EXPRESSION",
        description="Expressed in heterologous system")
    NATIVE_SOURCE = PermissibleValue(
        text="NATIVE_SOURCE",
        description="From original organism")
    IN_VITRO_EXPRESSION = PermissibleValue(
        text="IN_VITRO_EXPRESSION",
        description="Cell-free expression")
    OVEREXPRESSION = PermissibleValue(
        text="OVEREXPRESSION",
        description="Above physiological levels",
        meaning=MI["0506"])
    KNOCKDOWN = PermissibleValue(
        text="KNOCKDOWN",
        description="Reduced expression")
    KNOCKOUT = PermissibleValue(
        text="KNOCKOUT",
        description="Gene deletion",
        meaning=MI["0788"])
    ENDOGENOUS_LEVEL = PermissibleValue(
        text="ENDOGENOUS_LEVEL",
        description="Physiological expression")

    _defn = EnumDefinition(
        name="ExperimentalPreparation",
        description="Sample preparation methods",
    )

class BioticInteractionType(EnumDefinitionImpl):
    """
    Types of biotic interactions between organisms, based on RO:0002437 (biotically interacts with). These represent
    ecological relationships where at least one partner is an organism.
    """
    BIOTICALLY_INTERACTS_WITH = PermissibleValue(
        text="BIOTICALLY_INTERACTS_WITH",
        description="""An interaction relationship in which at least one of the partners is an organism and the other is either an organism or an abiotic entity with which the organism interacts.""",
        meaning=RO["0002437"])
    TROPHICALLY_INTERACTS_WITH = PermissibleValue(
        text="TROPHICALLY_INTERACTS_WITH",
        description="An interaction relationship in which the partners are related via a feeding relationship.",
        meaning=RO["0002438"])
    PREYS_ON = PermissibleValue(
        text="PREYS_ON",
        description="""An interaction relationship involving a predation process, where the subject kills the target in order to eat it or to feed to siblings, offspring or group members.""",
        meaning=RO["0002439"])
    PREYED_UPON_BY = PermissibleValue(
        text="PREYED_UPON_BY",
        description="Inverse of preys on",
        meaning=RO["0002458"])
    EATS = PermissibleValue(
        text="EATS",
        description="""A biotic interaction where one organism consumes a material entity through a type of mouth or other oral opening.""",
        meaning=RO["0002470"])
    IS_EATEN_BY = PermissibleValue(
        text="IS_EATEN_BY",
        description="Inverse of eats",
        meaning=RO["0002471"])
    ACQUIRES_NUTRIENTS_FROM = PermissibleValue(
        text="ACQUIRES_NUTRIENTS_FROM",
        description="Inverse of provides nutrients for",
        meaning=RO["0002457"])
    PROVIDES_NUTRIENTS_FOR = PermissibleValue(
        text="PROVIDES_NUTRIENTS_FOR",
        description="A biotic interaction where a material entity provides nutrition for an organism.",
        meaning=RO["0002469"])
    SYMBIOTICALLY_INTERACTS_WITH = PermissibleValue(
        text="SYMBIOTICALLY_INTERACTS_WITH",
        description="""A biotic interaction in which the two organisms live together in more or less intimate association.""",
        meaning=RO["0002440"])
    COMMENSUALLY_INTERACTS_WITH = PermissibleValue(
        text="COMMENSUALLY_INTERACTS_WITH",
        description="""An interaction relationship between two organisms living together in more or less intimate association in a relationship in which one benefits and the other is unaffected.""",
        meaning=RO["0002441"])
    MUTUALISTICALLY_INTERACTS_WITH = PermissibleValue(
        text="MUTUALISTICALLY_INTERACTS_WITH",
        description="""An interaction relationship between two organisms living together in more or less intimate association in a relationship in which both organisms benefit from each other.""",
        meaning=RO["0002442"])
    INTERACTS_VIA_PARASITE_HOST = PermissibleValue(
        text="INTERACTS_VIA_PARASITE_HOST",
        title="interacts with via parasite-host interaction",
        description="""An interaction relationship between two organisms living together in more or less intimate association in a relationship in which association is disadvantageous or destructive to one of the organisms.""",
        meaning=RO["0002443"])
    SYMBIOTROPHICALLY_INTERACTS_WITH = PermissibleValue(
        text="SYMBIOTROPHICALLY_INTERACTS_WITH",
        description="""A trophic interaction in which one organism acquires nutrients through a symbiotic relationship with another organism.""",
        meaning=RO["0008510"])
    PARASITE_OF = PermissibleValue(
        text="PARASITE_OF",
        description="A parasite-host relationship where an organism benefits at the expense of another.",
        meaning=RO["0002444"])
    HOST_OF = PermissibleValue(
        text="HOST_OF",
        description="Inverse of has host",
        meaning=RO["0002453"])
    HAS_HOST = PermissibleValue(
        text="HAS_HOST",
        description="""X 'has host' y if and only if: x is an organism, y is an organism, and x can live on the surface of or within the body of y.""",
        meaning=RO["0002454"])
    PARASITOID_OF = PermissibleValue(
        text="PARASITOID_OF",
        description="A parasite that kills or sterilizes its host",
        meaning=RO["0002208"])
    ECTOPARASITE_OF = PermissibleValue(
        text="ECTOPARASITE_OF",
        description="""A sub-relation of parasite-of in which the parasite lives on or in the integumental system of the host.""",
        meaning=RO["0002632"])
    ENDOPARASITE_OF = PermissibleValue(
        text="ENDOPARASITE_OF",
        description="A parasite that lives inside its host",
        meaning=RO["0002634"])
    INTRACELLULAR_ENDOPARASITE_OF = PermissibleValue(
        text="INTRACELLULAR_ENDOPARASITE_OF",
        description="A sub-relation of endoparasite-of in which the parasite inhabits host cells.",
        meaning=RO["0002640"])
    INTERCELLULAR_ENDOPARASITE_OF = PermissibleValue(
        text="INTERCELLULAR_ENDOPARASITE_OF",
        description="""A sub-relation of endoparasite-of in which the parasite inhabits the spaces between host cells.""",
        meaning=RO["0002638"])
    HEMIPARASITE_OF = PermissibleValue(
        text="HEMIPARASITE_OF",
        description="""A sub-relation of parasite-of in which the parasite is a plant, and the parasite is parasitic under natural conditions and is also photosynthetic to some degree.""",
        meaning=RO["0002237"])
    STEM_PARASITE_OF = PermissibleValue(
        text="STEM_PARASITE_OF",
        description="""A parasite-of relationship in which the host is a plant and the parasite that attaches to the host stem.""",
        meaning=RO["0002235"])
    ROOT_PARASITE_OF = PermissibleValue(
        text="ROOT_PARASITE_OF",
        description="""A parasite-of relationship in which the host is a plant and the parasite that attaches to the host root.""",
        meaning=RO["0002236"])
    OBLIGATE_PARASITE_OF = PermissibleValue(
        text="OBLIGATE_PARASITE_OF",
        description="""A sub-relation of parasite-of in which the parasite that cannot complete its life cycle without a host.""",
        meaning=RO["0002227"])
    FACULTATIVE_PARASITE_OF = PermissibleValue(
        text="FACULTATIVE_PARASITE_OF",
        description="""A sub-relations of parasite-of in which the parasite that can complete its life cycle independent of a host.""",
        meaning=RO["0002228"])
    TROPHIC_PARASITE_OF = PermissibleValue(
        text="TROPHIC_PARASITE_OF",
        description="""A symbiotrophic interaction in which one organism acquires nutrients through a parasitic relationship with another organism.""",
        meaning=RO["0008511"])
    PATHOGEN_OF = PermissibleValue(
        text="PATHOGEN_OF",
        description="Inverse of has pathogen",
        meaning=RO["0002556"])
    HAS_PATHOGEN = PermissibleValue(
        text="HAS_PATHOGEN",
        description="""A host interaction where the smaller of the two members of a symbiosis causes a disease in the larger member.""",
        meaning=RO["0002557"])
    RESERVOIR_HOST_OF = PermissibleValue(
        text="RESERVOIR_HOST_OF",
        description="""A relation between a host organism and a hosted organism in which the hosted organism naturally occurs in an indefinitely maintained reservoir provided by the host.""",
        meaning=RO["0002802"])
    HAS_RESERVOIR_HOST = PermissibleValue(
        text="HAS_RESERVOIR_HOST",
        description="Inverse of reservoir host of",
        meaning=RO["0002803"])
    IS_VECTOR_FOR = PermissibleValue(
        text="IS_VECTOR_FOR",
        description="Organism acts as a vector for transmitting another organism",
        meaning=RO["0002459"])
    POLLINATES = PermissibleValue(
        text="POLLINATES",
        description="An interaction where an organism transfers pollen to a plant",
        meaning=RO["0002455"])
    PARTICIPATES_IN_ABIOTIC_BIOTIC_INTERACTION_WITH = PermissibleValue(
        text="PARTICIPATES_IN_ABIOTIC_BIOTIC_INTERACTION_WITH",
        title="participates in a abiotic-biotic interaction with",
        description="""A biotic interaction relationship in which one partner is an organism and the other partner is inorganic. For example, the relationship between a sponge and the substrate to which is it anchored.""",
        meaning=RO["0002446"])
    ECOLOGICALLY_CO_OCCURS_WITH = PermissibleValue(
        text="ECOLOGICALLY_CO_OCCURS_WITH",
        description="""An interaction relationship describing organisms that often occur together at the same time and space or in the same environment.""",
        meaning=RO["0008506"])
    HYPERPARASITE_OF = PermissibleValue(
        text="HYPERPARASITE_OF",
        description="x is a hyperparasite of y iff x is a parasite of a parasite of the target organism y",
        meaning=RO["0002553"])
    MESOPARASITE_OF = PermissibleValue(
        text="MESOPARASITE_OF",
        description="""A sub-relation of parasite-of in which the parasite is partially an endoparasite and partially an ectoparasite.""",
        meaning=RO["0002636"])
    KLEPTOPARASITE_OF = PermissibleValue(
        text="KLEPTOPARASITE_OF",
        description="""A sub-relation of parasite of in which a parasite steals resources from another organism, usually food or nest material.""",
        meaning=RO["0008503"])
    EPIPHYTE_OF = PermissibleValue(
        text="EPIPHYTE_OF",
        description="""An interaction relationship wherein a plant or algae is living on the outside surface of another plant.""",
        meaning=RO["0008501"])
    ALLELOPATH_OF = PermissibleValue(
        text="ALLELOPATH_OF",
        description="""A relationship between organisms where one organism is influenced by the biochemicals produced by another. Allelopathy is a phenomenon in which one organism releases chemicals to positively or negatively influence the growth, survival or reproduction of other organisms in its vicinity.""",
        meaning=RO["0002555"])
    VISITS = PermissibleValue(
        text="VISITS",
        description="An interaction where an organism visits another organism or location",
        meaning=RO["0002618"])
    VISITS_FLOWERS_OF = PermissibleValue(
        text="VISITS_FLOWERS_OF",
        description="An interaction where an organism visits the flowers of a plant",
        meaning=RO["0002622"])
    HAS_FLOWERS_VISITED_BY = PermissibleValue(
        text="HAS_FLOWERS_VISITED_BY",
        description="Inverse of visits flowers of",
        meaning=RO["0002623"])
    LAYS_EGGS_IN = PermissibleValue(
        text="LAYS_EGGS_IN",
        description="An interaction where an organism deposits eggs inside another organism",
        meaning=RO["0002624"])
    HAS_EGGS_LAID_IN_BY = PermissibleValue(
        text="HAS_EGGS_LAID_IN_BY",
        description="Inverse of lays eggs in",
        meaning=RO["0002625"])
    LAYS_EGGS_ON = PermissibleValue(
        text="LAYS_EGGS_ON",
        description="""An interaction relationship in which organism a lays eggs on the outside surface of organism b. Organism b is neither helped nor harmed in the process of egg laying or incubation.""",
        meaning=RO["0008507"])
    HAS_EGGS_LAID_ON_BY = PermissibleValue(
        text="HAS_EGGS_LAID_ON_BY",
        description="Inverse of lays eggs on",
        meaning=RO["0008508"])
    CREATES_HABITAT_FOR = PermissibleValue(
        text="CREATES_HABITAT_FOR",
        description="""An interaction relationship wherein one organism creates a structure or environment that is lived in by another organism.""",
        meaning=RO["0008505"])

    _defn = EnumDefinition(
        name="BioticInteractionType",
        description="""Types of biotic interactions between organisms, based on RO:0002437 (biotically interacts with). These represent ecological relationships where at least one partner is an organism.""",
    )

class MineralogyFeedstockClass(EnumDefinitionImpl):
    """
    Types of mineral feedstock sources for extraction and processing operations, including primary and secondary
    sources.
    """
    HARDROCK_PRIMARY = PermissibleValue(
        text="HARDROCK_PRIMARY",
        title="HARDROCK_PRIMARY",
        description="Primary ore from hardrock mining operations")
    TAILINGS_LEGACY = PermissibleValue(
        text="TAILINGS_LEGACY",
        title="TAILINGS_LEGACY",
        description="Historical mine tailings available for reprocessing")
    WASTE_PILES = PermissibleValue(
        text="WASTE_PILES",
        title="WASTE_PILES",
        description="Accumulated mining waste materials")
    COAL_BYPRODUCT = PermissibleValue(
        text="COAL_BYPRODUCT",
        title="COAL_BYPRODUCT",
        description="Byproducts from coal mining and processing")
    E_WASTE = PermissibleValue(
        text="E_WASTE",
        title="E_WASTE",
        description="Electronic waste containing recoverable metals")
    BRINES = PermissibleValue(
        text="BRINES",
        title="BRINES",
        description="Saline water sources containing dissolved minerals")

    _defn = EnumDefinition(
        name="MineralogyFeedstockClass",
        description="""Types of mineral feedstock sources for extraction and processing operations, including primary and secondary sources.""",
    )

class BeneficiationPathway(EnumDefinitionImpl):
    """
    Methods for mineral separation and concentration aligned with advanced ore processing initiatives (AOI-2).
    """
    ORE_SORTING = PermissibleValue(
        text="ORE_SORTING",
        description="Sensor-based sorting of ore particles")
    DENSE_MEDIUM_SEPARATION = PermissibleValue(
        text="DENSE_MEDIUM_SEPARATION",
        description="Gravity separation using dense media")
    MICROWAVE_PREWEAKENING = PermissibleValue(
        text="MICROWAVE_PREWEAKENING",
        description="Microwave treatment to weaken ore structure")
    ELECTRIC_PULSE_PREWEAKENING = PermissibleValue(
        text="ELECTRIC_PULSE_PREWEAKENING",
        description="High-voltage electric pulse fragmentation")
    GRINDING_DYNAMIC = PermissibleValue(
        text="GRINDING_DYNAMIC",
        description="Dynamic grinding optimization systems")
    ELECTROSTATIC_SEP = PermissibleValue(
        text="ELECTROSTATIC_SEP",
        description="Electrostatic separation of minerals")
    MAGNETIC_SEP = PermissibleValue(
        text="MAGNETIC_SEP",
        description="Magnetic separation of ferromagnetic minerals")
    FLOTATION_LOW_H2O = PermissibleValue(
        text="FLOTATION_LOW_H2O",
        description="Low-water flotation processes")
    BIO_BENEFICIATION = PermissibleValue(
        text="BIO_BENEFICIATION",
        description="Biological methods for mineral beneficiation")

    _defn = EnumDefinition(
        name="BeneficiationPathway",
        description="""Methods for mineral separation and concentration aligned with advanced ore processing initiatives (AOI-2).""",
    )

class InSituChemistryRegime(EnumDefinitionImpl):
    """
    Chemical leaching systems for in-situ extraction with associated parameters including pH, Eh, temperature, and
    ionic strength.
    """
    ACIDIC_SULFATE = PermissibleValue(
        text="ACIDIC_SULFATE",
        title="ACIDIC_SULFATE",
        description="Sulfuric acid-based leaching system")
    ACIDIC_CHLORIDE = PermissibleValue(
        text="ACIDIC_CHLORIDE",
        title="ACIDIC_CHLORIDE",
        description="Hydrochloric acid or chloride-based leaching")
    AMMONIA_BASED = PermissibleValue(
        text="AMMONIA_BASED",
        title="AMMONIA_BASED",
        description="Ammonia or ammonium-based leaching system")
    ORGANIC_ACID = PermissibleValue(
        text="ORGANIC_ACID",
        description="Organic acid leaching (citric, oxalic, etc.)")
    BIOLEACH_SULFUR_OXIDIZING = PermissibleValue(
        text="BIOLEACH_SULFUR_OXIDIZING",
        description="Bioleaching using sulfur-oxidizing bacteria")
    BIOLEACH_IRON_OXIDIZING = PermissibleValue(
        text="BIOLEACH_IRON_OXIDIZING",
        description="Bioleaching using iron-oxidizing bacteria")

    _defn = EnumDefinition(
        name="InSituChemistryRegime",
        description="""Chemical leaching systems for in-situ extraction with associated parameters including pH, Eh, temperature, and ionic strength.""",
    )

class ExtractableTargetElement(EnumDefinitionImpl):
    """
    Target elements for extraction, particularly rare earth elements (REE) and critical minerals.
    """
    REE_LA = PermissibleValue(
        text="REE_LA",
        title="REE_LA",
        description="Lanthanum")
    REE_CE = PermissibleValue(
        text="REE_CE",
        title="REE_CE",
        description="Cerium")
    REE_PR = PermissibleValue(
        text="REE_PR",
        title="REE_PR",
        description="Praseodymium")
    REE_ND = PermissibleValue(
        text="REE_ND",
        title="REE_ND",
        description="Neodymium")
    REE_PM = PermissibleValue(
        text="REE_PM",
        title="REE_PM",
        description="Promethium")
    REE_SM = PermissibleValue(
        text="REE_SM",
        title="REE_SM",
        description="Samarium")
    REE_EU = PermissibleValue(
        text="REE_EU",
        title="REE_EU",
        description="Europium")
    REE_GD = PermissibleValue(
        text="REE_GD",
        title="REE_GD",
        description="Gadolinium")
    REE_TB = PermissibleValue(
        text="REE_TB",
        title="REE_TB",
        description="Terbium")
    REE_DY = PermissibleValue(
        text="REE_DY",
        title="REE_DY",
        description="Dysprosium")
    REE_HO = PermissibleValue(
        text="REE_HO",
        title="REE_HO",
        description="Holmium")
    REE_ER = PermissibleValue(
        text="REE_ER",
        title="REE_ER",
        description="Erbium")
    REE_TM = PermissibleValue(
        text="REE_TM",
        title="REE_TM",
        description="Thulium")
    REE_YB = PermissibleValue(
        text="REE_YB",
        title="REE_YB",
        description="Ytterbium")
    REE_LU = PermissibleValue(
        text="REE_LU",
        title="REE_LU",
        description="Lutetium")
    SC = PermissibleValue(
        text="SC",
        title="SC",
        description="Scandium")
    CO = PermissibleValue(
        text="CO",
        title="CO",
        description="Cobalt")
    NI = PermissibleValue(
        text="NI",
        title="NI",
        description="Nickel")
    LI = PermissibleValue(
        text="LI",
        title="LI",
        description="Lithium")

    _defn = EnumDefinition(
        name="ExtractableTargetElement",
        description="""Target elements for extraction, particularly rare earth elements (REE) and critical minerals.""",
    )

class SensorWhileDrillingFeature(EnumDefinitionImpl):
    """
    Measurement while drilling (MWD) and logging while drilling (LWD) features for orebody ML and geosteering
    applications.
    """
    WOB = PermissibleValue(
        text="WOB",
        description="Weight on bit measurement")
    ROP = PermissibleValue(
        text="ROP",
        description="Rate of penetration")
    TORQUE = PermissibleValue(
        text="TORQUE",
        description="Rotational torque measurement")
    MWD_GAMMA = PermissibleValue(
        text="MWD_GAMMA",
        description="Gamma ray logging while drilling")
    MWD_RESISTIVITY = PermissibleValue(
        text="MWD_RESISTIVITY",
        description="Resistivity logging while drilling")
    MUD_LOSS = PermissibleValue(
        text="MUD_LOSS",
        description="Drilling mud loss measurement")
    VIBRATION = PermissibleValue(
        text="VIBRATION",
        description="Drill string vibration monitoring")
    RSS_ANGLE = PermissibleValue(
        text="RSS_ANGLE",
        description="Rotary steerable system angle")

    _defn = EnumDefinition(
        name="SensorWhileDrillingFeature",
        description="""Measurement while drilling (MWD) and logging while drilling (LWD) features for orebody ML and geosteering applications.""",
    )

class ProcessPerformanceMetric(EnumDefinitionImpl):
    """
    Key performance indicators for mining and processing operations tied to SMART milestones and sustainability goals.
    """
    RECOVERY_PCT = PermissibleValue(
        text="RECOVERY_PCT",
        description="Percentage recovery of target material")
    SELECTIVITY_INDEX = PermissibleValue(
        text="SELECTIVITY_INDEX",
        description="Selectivity index for separation processes")
    SPECIFIC_ENERGY_KWH_T = PermissibleValue(
        text="SPECIFIC_ENERGY_KWH_T",
        description="Specific energy consumption in kWh per tonne")
    WATER_INTENSITY_L_T = PermissibleValue(
        text="WATER_INTENSITY_L_T",
        description="Water usage intensity in liters per tonne")
    REAGENT_INTENSITY_KG_T = PermissibleValue(
        text="REAGENT_INTENSITY_KG_T",
        description="Reagent consumption in kg per tonne")
    CO2E_KG_T = PermissibleValue(
        text="CO2E_KG_T",
        description="CO2 equivalent emissions in kg per tonne")
    TAILINGS_MASS_REDUCTION_PCT = PermissibleValue(
        text="TAILINGS_MASS_REDUCTION_PCT",
        description="Percentage reduction in tailings mass")

    _defn = EnumDefinition(
        name="ProcessPerformanceMetric",
        description="""Key performance indicators for mining and processing operations tied to SMART milestones and sustainability goals.""",
    )

class BioleachOrganism(EnumDefinitionImpl):
    """
    Microorganisms used in bioleaching and biomining operations, including engineered strains.
    """
    ACIDITHIOBACILLUS_FERROOXIDANS = PermissibleValue(
        text="ACIDITHIOBACILLUS_FERROOXIDANS",
        description="Iron and sulfur oxidizing bacterium",
        meaning=NCBITAXON["920"])
    LEPTOSPIRILLUM_FERROOXIDANS = PermissibleValue(
        text="LEPTOSPIRILLUM_FERROOXIDANS",
        description="Iron oxidizing bacterium",
        meaning=NCBITAXON["180"])
    ASPERGILLUS_NIGER = PermissibleValue(
        text="ASPERGILLUS_NIGER",
        description="Organic acid producing fungus",
        meaning=NCBITAXON["5061"])
    ENGINEERED_STRAIN = PermissibleValue(
        text="ENGINEERED_STRAIN",
        description="Genetically modified organism for enhanced bioleaching")

    _defn = EnumDefinition(
        name="BioleachOrganism",
        description="""Microorganisms used in bioleaching and biomining operations, including engineered strains.""",
    )

class BioleachMode(EnumDefinitionImpl):
    """
    Mechanisms of bioleaching including indirect and direct bacterial action.
    """
    INDIRECT_BIOLEACH_ORGANIC_ACIDS = PermissibleValue(
        text="INDIRECT_BIOLEACH_ORGANIC_ACIDS",
        description="Indirect bioleaching through organic acid production")
    SULFUR_OXIDATION = PermissibleValue(
        text="SULFUR_OXIDATION",
        description="Direct bacterial oxidation of sulfur compounds")
    IRON_OXIDATION = PermissibleValue(
        text="IRON_OXIDATION",
        description="Direct bacterial oxidation of iron compounds")

    _defn = EnumDefinition(
        name="BioleachMode",
        description="""Mechanisms of bioleaching including indirect and direct bacterial action.""",
    )

class AutonomyLevel(EnumDefinitionImpl):
    """
    Levels of autonomy for mining systems including drilling, hauling, and sorting robots (relevant for Topic 1
    initiatives).
    """
    ASSISTIVE = PermissibleValue(
        text="ASSISTIVE",
        description="Human operator with assistive technologies")
    SUPERVISED_AUTONOMY = PermissibleValue(
        text="SUPERVISED_AUTONOMY",
        description="Autonomous operation with human supervision")
    SEMI_AUTONOMOUS = PermissibleValue(
        text="SEMI_AUTONOMOUS",
        description="Partial autonomy with human intervention capability")
    FULLY_AUTONOMOUS = PermissibleValue(
        text="FULLY_AUTONOMOUS",
        description="Complete autonomous operation without human intervention")

    _defn = EnumDefinition(
        name="AutonomyLevel",
        description="""Levels of autonomy for mining systems including drilling, hauling, and sorting robots (relevant for Topic 1 initiatives).""",
    )

class RegulatoryConstraint(EnumDefinitionImpl):
    """
    Regulatory and community constraints affecting mining operations, particularly for in-situ extraction and
    community engagement.
    """
    AQUIFER_PROTECTION = PermissibleValue(
        text="AQUIFER_PROTECTION",
        title="AQUIFER_PROTECTION",
        description="Requirements for groundwater and aquifer protection")
    EMISSIONS_CAP = PermissibleValue(
        text="EMISSIONS_CAP",
        description="Limits on atmospheric emissions")
    CULTURAL_HERITAGE_ZONE = PermissibleValue(
        text="CULTURAL_HERITAGE_ZONE",
        description="Protection of cultural heritage sites")
    WATER_RIGHTS_LIMIT = PermissibleValue(
        text="WATER_RIGHTS_LIMIT",
        description="Restrictions based on water usage rights")

    _defn = EnumDefinition(
        name="RegulatoryConstraint",
        description="""Regulatory and community constraints affecting mining operations, particularly for in-situ extraction and community engagement.""",
    )

class SubatomicParticleEnum(EnumDefinitionImpl):
    """
    Fundamental and composite subatomic particles
    """
    ELECTRON = PermissibleValue(
        text="ELECTRON",
        description="Elementary particle with -1 charge, spin 1/2",
        meaning=CHEBI["10545"])
    POSITRON = PermissibleValue(
        text="POSITRON",
        description="Antiparticle of electron with +1 charge",
        meaning=CHEBI["30225"])
    MUON = PermissibleValue(
        text="MUON",
        description="Heavy lepton with -1 charge",
        meaning=CHEBI["36356"])
    TAU_LEPTON = PermissibleValue(
        text="TAU_LEPTON",
        description="Heaviest lepton with -1 charge",
        meaning=CHEBI["36355"])
    ELECTRON_NEUTRINO = PermissibleValue(
        text="ELECTRON_NEUTRINO",
        description="Electron neutrino, nearly massless",
        meaning=CHEBI["30223"])
    MUON_NEUTRINO = PermissibleValue(
        text="MUON_NEUTRINO",
        description="Muon neutrino",
        meaning=CHEBI["36353"])
    TAU_NEUTRINO = PermissibleValue(
        text="TAU_NEUTRINO",
        description="Tau neutrino",
        meaning=CHEBI["36354"])
    UP_QUARK = PermissibleValue(
        text="UP_QUARK",
        title="up quark",
        description="First generation quark with +2/3 charge",
        meaning=CHEBI["36366"])
    DOWN_QUARK = PermissibleValue(
        text="DOWN_QUARK",
        description="First generation quark with -1/3 charge",
        meaning=CHEBI["36367"])
    CHARM_QUARK = PermissibleValue(
        text="CHARM_QUARK",
        title="charm quark",
        description="Second generation quark with +2/3 charge",
        meaning=CHEBI["36369"])
    STRANGE_QUARK = PermissibleValue(
        text="STRANGE_QUARK",
        title="strange quark",
        description="Second generation quark with -1/3 charge",
        meaning=CHEBI["36368"])
    TOP_QUARK = PermissibleValue(
        text="TOP_QUARK",
        description="Third generation quark with +2/3 charge",
        meaning=CHEBI["36371"])
    BOTTOM_QUARK = PermissibleValue(
        text="BOTTOM_QUARK",
        title="bottom quark",
        description="Third generation quark with -1/3 charge",
        meaning=CHEBI["36370"])
    PHOTON = PermissibleValue(
        text="PHOTON",
        description="Force carrier for electromagnetic interaction",
        meaning=CHEBI["30212"])
    W_BOSON = PermissibleValue(
        text="W_BOSON",
        title="composite particle",
        description="Force carrier for weak interaction",
        meaning=CHEBI["36343"])
    Z_BOSON = PermissibleValue(
        text="Z_BOSON",
        title="hadron",
        description="Force carrier for weak interaction",
        meaning=CHEBI["36344"])
    GLUON = PermissibleValue(
        text="GLUON",
        description="Force carrier for strong interaction")
    HIGGS_BOSON = PermissibleValue(
        text="HIGGS_BOSON",
        description="Scalar boson responsible for mass",
        meaning=CHEBI["146278"])
    PROTON = PermissibleValue(
        text="PROTON",
        description="Positively charged nucleon",
        meaning=CHEBI["24636"])
    NEUTRON = PermissibleValue(
        text="NEUTRON",
        description="Neutral nucleon",
        meaning=CHEBI["30222"])
    ALPHA_PARTICLE = PermissibleValue(
        text="ALPHA_PARTICLE",
        description="Helium-4 nucleus",
        meaning=CHEBI["30216"])
    DEUTERON = PermissibleValue(
        text="DEUTERON",
        description="Hydrogen-2 nucleus",
        meaning=CHEBI["29233"])
    TRITON = PermissibleValue(
        text="TRITON",
        description="Hydrogen-3 nucleus",
        meaning=CHEBI["29234"])

    _defn = EnumDefinition(
        name="SubatomicParticleEnum",
        description="Fundamental and composite subatomic particles",
    )

class BondTypeEnum(EnumDefinitionImpl):
    """
    Types of chemical bonds
    """
    SINGLE = PermissibleValue(
        text="SINGLE",
        description="Single covalent bond",
        meaning=GC["Single"])
    DOUBLE = PermissibleValue(
        text="DOUBLE",
        description="Double covalent bond",
        meaning=GC["Double"])
    TRIPLE = PermissibleValue(
        text="TRIPLE",
        description="Triple covalent bond",
        meaning=GC["Triple"])
    QUADRUPLE = PermissibleValue(
        text="QUADRUPLE",
        description="Quadruple bond (rare, in transition metals)",
        meaning=GC["Quadruple"])
    AROMATIC = PermissibleValue(
        text="AROMATIC",
        description="Aromatic bond",
        meaning=GC["AromaticBond"])
    IONIC = PermissibleValue(
        text="IONIC",
        title="organic molecular entity",
        description="Ionic bond",
        meaning=CHEBI["50860"])
    HYDROGEN = PermissibleValue(
        text="HYDROGEN",
        description="Hydrogen bond")
    METALLIC = PermissibleValue(
        text="METALLIC",
        description="Metallic bond")
    VAN_DER_WAALS = PermissibleValue(
        text="VAN_DER_WAALS",
        description="Van der Waals interaction")
    COORDINATE = PermissibleValue(
        text="COORDINATE",
        title="coordination entity",
        description="Coordinate/dative covalent bond",
        meaning=CHEBI["33240"])
    PI = PermissibleValue(
        text="PI",
        description="Pi bond")
    SIGMA = PermissibleValue(
        text="SIGMA",
        description="Sigma bond")

    _defn = EnumDefinition(
        name="BondTypeEnum",
        description="Types of chemical bonds",
    )

class PeriodicTableBlockEnum(EnumDefinitionImpl):
    """
    Blocks of the periodic table
    """
    S_BLOCK = PermissibleValue(
        text="S_BLOCK",
        title="s-block molecular entity",
        description="s-block elements (groups 1 and 2)",
        meaning=CHEBI["33674"])
    P_BLOCK = PermissibleValue(
        text="P_BLOCK",
        title="p-block molecular entity",
        description="p-block elements (groups 13-18)",
        meaning=CHEBI["33675"])
    D_BLOCK = PermissibleValue(
        text="D_BLOCK",
        title="d-block element atom",
        description="d-block elements (transition metals)",
        meaning=CHEBI["33561"])
    F_BLOCK = PermissibleValue(
        text="F_BLOCK",
        title="f-block element atom",
        description="f-block elements (lanthanides and actinides)",
        meaning=CHEBI["33562"])

    _defn = EnumDefinition(
        name="PeriodicTableBlockEnum",
        description="Blocks of the periodic table",
    )

class ElementFamilyEnum(EnumDefinitionImpl):
    """
    Chemical element families/groups
    """
    ALKALI_METALS = PermissibleValue(
        text="ALKALI_METALS",
        title="alkali metal atom",
        description="Group 1 elements (except hydrogen)",
        meaning=CHEBI["22314"])
    ALKALINE_EARTH_METALS = PermissibleValue(
        text="ALKALINE_EARTH_METALS",
        title="alkaloid",
        description="Group 2 elements",
        meaning=CHEBI["22315"])
    TRANSITION_METALS = PermissibleValue(
        text="TRANSITION_METALS",
        title="transition element atom",
        description="d-block elements",
        meaning=CHEBI["27081"])
    LANTHANIDES = PermissibleValue(
        text="LANTHANIDES",
        title="titanium group molecular entity",
        description="Lanthanide series",
        meaning=CHEBI["33768"])
    ACTINIDES = PermissibleValue(
        text="ACTINIDES",
        title="fuconates",
        description="Actinide series",
        meaning=CHEBI["33769"])
    CHALCOGENS = PermissibleValue(
        text="CHALCOGENS",
        title="chalcogen",
        description="Group 16 elements",
        meaning=CHEBI["33303"])
    HALOGENS = PermissibleValue(
        text="HALOGENS",
        title="idopyranuronic acid",
        description="Group 17 elements",
        meaning=CHEBI["47902"])
    NOBLE_GASES = PermissibleValue(
        text="NOBLE_GASES",
        title="neon atom",
        description="Group 18 elements",
        meaning=CHEBI["33310"])
    METALLOIDS = PermissibleValue(
        text="METALLOIDS",
        title="s-block element atom",
        description="Elements with intermediate properties",
        meaning=CHEBI["33559"])
    POST_TRANSITION_METALS = PermissibleValue(
        text="POST_TRANSITION_METALS",
        description="Metals after the transition series")
    NONMETALS = PermissibleValue(
        text="NONMETALS",
        title="nonmetal atom",
        description="Non-metallic elements",
        meaning=CHEBI["25585"])

    _defn = EnumDefinition(
        name="ElementFamilyEnum",
        description="Chemical element families/groups",
    )

class ElementMetallicClassificationEnum(EnumDefinitionImpl):
    """
    Metallic character classification
    """
    METALLIC = PermissibleValue(
        text="METALLIC",
        description="Metallic elements",
        meaning=DAMLPT["Metallic"])
    NON_METALLIC = PermissibleValue(
        text="NON_METALLIC",
        description="Non-metallic elements",
        meaning=DAMLPT["Non-Metallic"])
    SEMI_METALLIC = PermissibleValue(
        text="SEMI_METALLIC",
        description="Semi-metallic/metalloid elements",
        meaning=DAMLPT["Semi-Metallic"])

    _defn = EnumDefinition(
        name="ElementMetallicClassificationEnum",
        description="Metallic character classification",
    )

class HardOrSoftEnum(EnumDefinitionImpl):
    """
    HSAB (Hard Soft Acid Base) classification
    """
    HARD = PermissibleValue(
        text="HARD",
        description="Hard acids/bases (small, high charge density)")
    SOFT = PermissibleValue(
        text="SOFT",
        description="Soft acids/bases (large, low charge density)")
    BORDERLINE = PermissibleValue(
        text="BORDERLINE",
        description="Borderline acids/bases")

    _defn = EnumDefinition(
        name="HardOrSoftEnum",
        description="HSAB (Hard Soft Acid Base) classification",
    )

class BronstedAcidBaseRoleEnum(EnumDefinitionImpl):
    """
    Brønsted-Lowry acid-base roles
    """
    ACID = PermissibleValue(
        text="ACID",
        title="Bronsted acid",
        description="Proton donor",
        meaning=CHEBI["39141"])
    BASE = PermissibleValue(
        text="BASE",
        title="Bronsted base",
        description="Proton acceptor",
        meaning=CHEBI["39142"])
    AMPHOTERIC = PermissibleValue(
        text="AMPHOTERIC",
        description="Can act as both acid and base")

    _defn = EnumDefinition(
        name="BronstedAcidBaseRoleEnum",
        description="Brønsted-Lowry acid-base roles",
    )

class LewisAcidBaseRoleEnum(EnumDefinitionImpl):
    """
    Lewis acid-base roles
    """
    LEWIS_ACID = PermissibleValue(
        text="LEWIS_ACID",
        description="Electron pair acceptor")
    LEWIS_BASE = PermissibleValue(
        text="LEWIS_BASE",
        description="Electron pair donor")

    _defn = EnumDefinition(
        name="LewisAcidBaseRoleEnum",
        description="Lewis acid-base roles",
    )

class OxidationStateEnum(EnumDefinitionImpl):
    """
    Common oxidation states
    """
    MINUS_4 = PermissibleValue(
        text="MINUS_4",
        description="Oxidation state -4")
    MINUS_3 = PermissibleValue(
        text="MINUS_3",
        description="Oxidation state -3")
    MINUS_2 = PermissibleValue(
        text="MINUS_2",
        description="Oxidation state -2")
    MINUS_1 = PermissibleValue(
        text="MINUS_1",
        description="Oxidation state -1")
    ZERO = PermissibleValue(
        text="ZERO",
        description="Oxidation state 0")
    PLUS_1 = PermissibleValue(
        text="PLUS_1",
        description="Oxidation state +1")
    PLUS_2 = PermissibleValue(
        text="PLUS_2",
        description="Oxidation state +2")
    PLUS_3 = PermissibleValue(
        text="PLUS_3",
        description="Oxidation state +3")
    PLUS_4 = PermissibleValue(
        text="PLUS_4",
        description="Oxidation state +4")
    PLUS_5 = PermissibleValue(
        text="PLUS_5",
        description="Oxidation state +5")
    PLUS_6 = PermissibleValue(
        text="PLUS_6",
        description="Oxidation state +6")
    PLUS_7 = PermissibleValue(
        text="PLUS_7",
        description="Oxidation state +7")
    PLUS_8 = PermissibleValue(
        text="PLUS_8",
        description="Oxidation state +8")

    _defn = EnumDefinition(
        name="OxidationStateEnum",
        description="Common oxidation states",
    )

class ChiralityEnum(EnumDefinitionImpl):
    """
    Chirality/stereochemistry descriptors
    """
    R = PermissibleValue(
        text="R",
        description="Rectus (right) configuration")
    S = PermissibleValue(
        text="S",
        description="Sinister (left) configuration")
    D = PermissibleValue(
        text="D",
        description="Dextrorotatory")
    L = PermissibleValue(
        text="L",
        description="Levorotatory")
    RACEMIC = PermissibleValue(
        text="RACEMIC",
        description="Racemic mixture (50:50 of enantiomers)")
    MESO = PermissibleValue(
        text="MESO",
        description="Meso compound (achiral despite stereocenters)")
    E = PermissibleValue(
        text="E",
        description="Entgegen (opposite) configuration")
    Z = PermissibleValue(
        text="Z",
        description="Zusammen (together) configuration")

    _defn = EnumDefinition(
        name="ChiralityEnum",
        description="Chirality/stereochemistry descriptors",
    )

class NanostructureMorphologyEnum(EnumDefinitionImpl):
    """
    Types of nanostructure morphologies
    """
    NANOTUBE = PermissibleValue(
        text="NANOTUBE",
        description="Cylindrical nanostructure",
        meaning=CHEBI["50796"])
    NANOPARTICLE = PermissibleValue(
        text="NANOPARTICLE",
        description="Particle with nanoscale dimensions",
        meaning=CHEBI["50803"])
    NANOROD = PermissibleValue(
        text="NANOROD",
        description="Rod-shaped nanostructure",
        meaning=CHEBI["50805"])
    QUANTUM_DOT = PermissibleValue(
        text="QUANTUM_DOT",
        description="Semiconductor nanocrystal",
        meaning=CHEBI["50853"])
    NANOWIRE = PermissibleValue(
        text="NANOWIRE",
        description="Wire with nanoscale diameter")
    NANOSHEET = PermissibleValue(
        text="NANOSHEET",
        description="Two-dimensional nanostructure")
    NANOFIBER = PermissibleValue(
        text="NANOFIBER",
        description="Fiber with nanoscale diameter")

    _defn = EnumDefinition(
        name="NanostructureMorphologyEnum",
        description="Types of nanostructure morphologies",
    )

class ReactionTypeEnum(EnumDefinitionImpl):
    """
    Types of chemical reactions
    """
    SYNTHESIS = PermissibleValue(
        text="SYNTHESIS",
        description="Combination reaction (A + B → AB)")
    DECOMPOSITION = PermissibleValue(
        text="DECOMPOSITION",
        description="Breakdown reaction (AB → A + B)")
    SINGLE_DISPLACEMENT = PermissibleValue(
        text="SINGLE_DISPLACEMENT",
        description="Single replacement reaction (A + BC → AC + B)")
    DOUBLE_DISPLACEMENT = PermissibleValue(
        text="DOUBLE_DISPLACEMENT",
        description="Double replacement reaction (AB + CD → AD + CB)")
    COMBUSTION = PermissibleValue(
        text="COMBUSTION",
        description="Reaction with oxygen producing heat and light")
    SUBSTITUTION = PermissibleValue(
        text="SUBSTITUTION",
        title="substitution reaction",
        description="Replacement of one group by another",
        meaning=MOP["0000790"])
    ELIMINATION = PermissibleValue(
        text="ELIMINATION",
        title="elimination reaction",
        description="Removal of atoms/groups forming double bond",
        meaning=MOP["0000656"])
    ADDITION = PermissibleValue(
        text="ADDITION",
        title="addition reaction",
        description="Addition to multiple bond",
        meaning=MOP["0000642"])
    REARRANGEMENT = PermissibleValue(
        text="REARRANGEMENT",
        description="Reorganization of molecular structure")
    OXIDATION = PermissibleValue(
        text="OXIDATION",
        description="Loss of electrons or increase in oxidation state")
    REDUCTION = PermissibleValue(
        text="REDUCTION",
        description="Gain of electrons or decrease in oxidation state")
    DIELS_ALDER = PermissibleValue(
        text="DIELS_ALDER",
        title="Diels-Alder reaction",
        description="[4+2] cycloaddition reaction",
        meaning=RXNO["0000006"])
    FRIEDEL_CRAFTS = PermissibleValue(
        text="FRIEDEL_CRAFTS",
        title="Friedel-Crafts reaction",
        description="Electrophilic aromatic substitution",
        meaning=RXNO["0000369"])
    GRIGNARD = PermissibleValue(
        text="GRIGNARD",
        title="Grignard reaction",
        description="Organometallic addition reaction",
        meaning=RXNO["0000014"])
    WITTIG = PermissibleValue(
        text="WITTIG",
        title="Wittig reaction",
        description="Alkene formation from phosphonium ylide",
        meaning=RXNO["0000015"])
    ALDOL = PermissibleValue(
        text="ALDOL",
        title="aldol condensation",
        description="Condensation forming β-hydroxy carbonyl",
        meaning=RXNO["0000017"])
    MICHAEL_ADDITION = PermissibleValue(
        text="MICHAEL_ADDITION",
        title="Michael addition",
        description="1,4-addition to α,β-unsaturated carbonyl",
        meaning=RXNO["0000009"])

    _defn = EnumDefinition(
        name="ReactionTypeEnum",
        description="Types of chemical reactions",
    )

class ReactionMechanismEnum(EnumDefinitionImpl):
    """
    Reaction mechanism types
    """
    SN1 = PermissibleValue(
        text="SN1",
        description="Unimolecular nucleophilic substitution")
    SN2 = PermissibleValue(
        text="SN2",
        description="Bimolecular nucleophilic substitution")
    E1 = PermissibleValue(
        text="E1",
        description="Unimolecular elimination")
    E2 = PermissibleValue(
        text="E2",
        description="Bimolecular elimination")
    E1CB = PermissibleValue(
        text="E1CB",
        description="Elimination via conjugate base")
    RADICAL = PermissibleValue(
        text="RADICAL",
        description="Free radical mechanism")
    PERICYCLIC = PermissibleValue(
        text="PERICYCLIC",
        description="Concerted cyclic electron reorganization")
    ELECTROPHILIC_AROMATIC = PermissibleValue(
        text="ELECTROPHILIC_AROMATIC",
        description="Electrophilic aromatic substitution")
    NUCLEOPHILIC_AROMATIC = PermissibleValue(
        text="NUCLEOPHILIC_AROMATIC",
        description="Nucleophilic aromatic substitution")
    ADDITION_ELIMINATION = PermissibleValue(
        text="ADDITION_ELIMINATION",
        description="Addition followed by elimination")

    _defn = EnumDefinition(
        name="ReactionMechanismEnum",
        description="Reaction mechanism types",
    )

class CatalystTypeEnum(EnumDefinitionImpl):
    """
    Types of catalysts
    """
    HOMOGENEOUS = PermissibleValue(
        text="HOMOGENEOUS",
        description="Catalyst in same phase as reactants")
    HETEROGENEOUS = PermissibleValue(
        text="HETEROGENEOUS",
        description="Catalyst in different phase from reactants")
    ENZYME = PermissibleValue(
        text="ENZYME",
        title="cofactor",
        description="Biological catalyst",
        meaning=CHEBI["23357"])
    ORGANOCATALYST = PermissibleValue(
        text="ORGANOCATALYST",
        description="Small organic molecule catalyst")
    PHOTOCATALYST = PermissibleValue(
        text="PHOTOCATALYST",
        description="Light-activated catalyst")
    PHASE_TRANSFER = PermissibleValue(
        text="PHASE_TRANSFER",
        description="Catalyst facilitating reaction between phases")
    ACID = PermissibleValue(
        text="ACID",
        description="Acid catalyst")
    BASE = PermissibleValue(
        text="BASE",
        description="Base catalyst")
    METAL = PermissibleValue(
        text="METAL",
        description="Metal catalyst")
    BIFUNCTIONAL = PermissibleValue(
        text="BIFUNCTIONAL",
        description="Catalyst with two active sites")

    _defn = EnumDefinition(
        name="CatalystTypeEnum",
        description="Types of catalysts",
    )

class ReactionConditionEnum(EnumDefinitionImpl):
    """
    Reaction conditions
    """
    ROOM_TEMPERATURE = PermissibleValue(
        text="ROOM_TEMPERATURE",
        description="Standard room temperature (20-25°C)")
    REFLUX = PermissibleValue(
        text="REFLUX",
        description="Boiling with condensation return")
    CRYOGENIC = PermissibleValue(
        text="CRYOGENIC",
        description="Very low temperature conditions")
    HIGH_PRESSURE = PermissibleValue(
        text="HIGH_PRESSURE",
        description="Elevated pressure conditions")
    VACUUM = PermissibleValue(
        text="VACUUM",
        description="Reduced pressure conditions")
    INERT_ATMOSPHERE = PermissibleValue(
        text="INERT_ATMOSPHERE",
        description="Non-reactive gas atmosphere")
    MICROWAVE = PermissibleValue(
        text="MICROWAVE",
        description="Microwave heating")
    ULTRASOUND = PermissibleValue(
        text="ULTRASOUND",
        description="Ultrasonic conditions")
    PHOTOCHEMICAL = PermissibleValue(
        text="PHOTOCHEMICAL",
        description="Light-induced conditions")
    ELECTROCHEMICAL = PermissibleValue(
        text="ELECTROCHEMICAL",
        description="Electrically driven conditions")
    FLOW = PermissibleValue(
        text="FLOW",
        description="Continuous flow conditions")
    BATCH = PermissibleValue(
        text="BATCH",
        description="Batch reaction conditions")

    _defn = EnumDefinition(
        name="ReactionConditionEnum",
        description="Reaction conditions",
    )

class ReactionRateOrderEnum(EnumDefinitionImpl):
    """
    Reaction rate orders
    """
    ZERO_ORDER = PermissibleValue(
        text="ZERO_ORDER",
        description="Rate independent of concentration")
    FIRST_ORDER = PermissibleValue(
        text="FIRST_ORDER",
        description="Rate proportional to concentration")
    SECOND_ORDER = PermissibleValue(
        text="SECOND_ORDER",
        description="Rate proportional to concentration squared")
    PSEUDO_FIRST_ORDER = PermissibleValue(
        text="PSEUDO_FIRST_ORDER",
        description="Apparent first order (excess reagent)")
    FRACTIONAL_ORDER = PermissibleValue(
        text="FRACTIONAL_ORDER",
        description="Non-integer order")
    MIXED_ORDER = PermissibleValue(
        text="MIXED_ORDER",
        description="Different orders for different reactants")

    _defn = EnumDefinition(
        name="ReactionRateOrderEnum",
        description="Reaction rate orders",
    )

class EnzymeClassEnum(EnumDefinitionImpl):
    """
    EC enzyme classification
    """
    OXIDOREDUCTASE = PermissibleValue(
        text="OXIDOREDUCTASE",
        title="Oxidoreductases",
        description="Catalyzes oxidation-reduction reactions",
        meaning=EC["1"])
    TRANSFERASE = PermissibleValue(
        text="TRANSFERASE",
        title="Transferases",
        description="Catalyzes group transfer reactions",
        meaning=EC["2"])
    HYDROLASE = PermissibleValue(
        text="HYDROLASE",
        title="Hydrolases",
        description="Catalyzes hydrolysis reactions",
        meaning=EC["3"])
    LYASE = PermissibleValue(
        text="LYASE",
        title="Lyases",
        description="Catalyzes non-hydrolytic additions/removals",
        meaning=EC["4"])
    ISOMERASE = PermissibleValue(
        text="ISOMERASE",
        title="Isomerases",
        description="Catalyzes isomerization reactions",
        meaning=EC["5"])
    LIGASE = PermissibleValue(
        text="LIGASE",
        title="Ligases",
        description="Catalyzes formation of bonds with ATP",
        meaning=EC["6"])
    TRANSLOCASE = PermissibleValue(
        text="TRANSLOCASE",
        title="Translocases",
        description="Catalyzes movement across membranes",
        meaning=EC["7"])

    _defn = EnumDefinition(
        name="EnzymeClassEnum",
        description="EC enzyme classification",
    )

class SolventClassEnum(EnumDefinitionImpl):
    """
    Classes of solvents
    """
    PROTIC = PermissibleValue(
        text="PROTIC",
        description="Solvents with acidic hydrogen")
    APROTIC_POLAR = PermissibleValue(
        text="APROTIC_POLAR",
        description="Polar solvents without acidic H")
    APROTIC_NONPOLAR = PermissibleValue(
        text="APROTIC_NONPOLAR",
        description="Nonpolar solvents")
    IONIC_LIQUID = PermissibleValue(
        text="IONIC_LIQUID",
        description="Room temperature ionic liquids")
    SUPERCRITICAL = PermissibleValue(
        text="SUPERCRITICAL",
        description="Supercritical fluids")
    AQUEOUS = PermissibleValue(
        text="AQUEOUS",
        description="Water-based solvents")
    ORGANIC = PermissibleValue(
        text="ORGANIC",
        description="Organic solvents")
    GREEN = PermissibleValue(
        text="GREEN",
        description="Environmentally friendly solvents")

    _defn = EnumDefinition(
        name="SolventClassEnum",
        description="Classes of solvents",
    )

class ThermodynamicParameterEnum(EnumDefinitionImpl):
    """
    Thermodynamic parameters
    """
    ENTHALPY = PermissibleValue(
        text="ENTHALPY",
        description="Heat content (ΔH)")
    ENTROPY = PermissibleValue(
        text="ENTROPY",
        description="Disorder (ΔS)")
    GIBBS_ENERGY = PermissibleValue(
        text="GIBBS_ENERGY",
        description="Free energy (ΔG)")
    ACTIVATION_ENERGY = PermissibleValue(
        text="ACTIVATION_ENERGY",
        description="Energy barrier (Ea)")
    HEAT_CAPACITY = PermissibleValue(
        text="HEAT_CAPACITY",
        description="Heat capacity (Cp)")
    INTERNAL_ENERGY = PermissibleValue(
        text="INTERNAL_ENERGY",
        description="Internal energy (ΔU)")

    _defn = EnumDefinition(
        name="ThermodynamicParameterEnum",
        description="Thermodynamic parameters",
    )

class ReactionDirectionality(EnumDefinitionImpl):
    """
    The directionality of a chemical reaction or process
    """
    LEFT_TO_RIGHT = PermissibleValue(
        text="LEFT_TO_RIGHT",
        description="Reaction proceeds from left to right (forward direction)")
    RIGHT_TO_LEFT = PermissibleValue(
        text="RIGHT_TO_LEFT",
        description="Reaction proceeds from right to left (reverse direction)")
    BIDIRECTIONAL = PermissibleValue(
        text="BIDIRECTIONAL",
        description="Reaction can proceed in both directions")
    AGNOSTIC = PermissibleValue(
        text="AGNOSTIC",
        description="Direction is unknown or not specified")
    IRREVERSIBLE_LEFT_TO_RIGHT = PermissibleValue(
        text="IRREVERSIBLE_LEFT_TO_RIGHT",
        description="Reaction proceeds only from left to right and cannot be reversed")
    IRREVERSIBLE_RIGHT_TO_LEFT = PermissibleValue(
        text="IRREVERSIBLE_RIGHT_TO_LEFT",
        description="Reaction proceeds only from right to left and cannot be reversed")

    _defn = EnumDefinition(
        name="ReactionDirectionality",
        description="The directionality of a chemical reaction or process",
    )

class SafetyColorEnum(EnumDefinitionImpl):
    """
    ANSI/ISO standard safety colors
    """
    SAFETY_RED = PermissibleValue(
        text="SAFETY_RED",
        description="Safety red - danger, stop, prohibition",
        meaning=HEX["C8102E"])
    SAFETY_ORANGE = PermissibleValue(
        text="SAFETY_ORANGE",
        description="Safety orange - warning of dangerous parts",
        meaning=HEX["FF6900"])
    SAFETY_YELLOW = PermissibleValue(
        text="SAFETY_YELLOW",
        description="Safety yellow - caution, physical hazards",
        meaning=HEX["F6D04D"])
    SAFETY_GREEN = PermissibleValue(
        text="SAFETY_GREEN",
        description="Safety green - safety, first aid, emergency egress",
        meaning=HEX["00843D"])
    SAFETY_BLUE = PermissibleValue(
        text="SAFETY_BLUE",
        description="Safety blue - mandatory, information",
        meaning=HEX["005EB8"])
    SAFETY_PURPLE = PermissibleValue(
        text="SAFETY_PURPLE",
        description="Safety purple - radiation hazards",
        meaning=HEX["652D90"])
    SAFETY_BLACK = PermissibleValue(
        text="SAFETY_BLACK",
        description="Safety black - traffic/housekeeping markings",
        meaning=HEX["000000"])
    SAFETY_WHITE = PermissibleValue(
        text="SAFETY_WHITE",
        description="Safety white - traffic/housekeeping markings",
        meaning=HEX["FFFFFF"])
    SAFETY_GRAY = PermissibleValue(
        text="SAFETY_GRAY",
        description="Safety gray - inactive/out of service",
        meaning=HEX["919191"])
    SAFETY_BROWN = PermissibleValue(
        text="SAFETY_BROWN",
        description="Safety brown - no special hazard (background)",
        meaning=HEX["795548"])

    _defn = EnumDefinition(
        name="SafetyColorEnum",
        description="ANSI/ISO standard safety colors",
    )

class TrafficLightColorEnum(EnumDefinitionImpl):
    """
    Traffic signal colors (international)
    """
    RED = PermissibleValue(
        text="RED",
        description="Red - stop",
        meaning=HEX["FF0000"])
    AMBER = PermissibleValue(
        text="AMBER",
        description="Amber/yellow - caution",
        meaning=HEX["FFBF00"])
    GREEN = PermissibleValue(
        text="GREEN",
        description="Green - go",
        meaning=HEX["00FF00"])
    FLASHING_RED = PermissibleValue(
        text="FLASHING_RED",
        description="Flashing red - stop then proceed",
        meaning=HEX["FF0000"])
    FLASHING_AMBER = PermissibleValue(
        text="FLASHING_AMBER",
        description="Flashing amber - proceed with caution",
        meaning=HEX["FFBF00"])
    WHITE = PermissibleValue(
        text="WHITE",
        description="White - special situations (transit)",
        meaning=HEX["FFFFFF"])

    _defn = EnumDefinition(
        name="TrafficLightColorEnum",
        description="Traffic signal colors (international)",
    )

class HazmatColorEnum(EnumDefinitionImpl):
    """
    Hazardous materials placarding colors (DOT/UN)
    """
    ORANGE = PermissibleValue(
        text="ORANGE",
        description="Orange - explosives (Class 1)",
        meaning=HEX["FF6600"])
    RED = PermissibleValue(
        text="RED",
        description="Red - flammable (Classes 2.1, 3)",
        meaning=HEX["FF0000"])
    GREEN = PermissibleValue(
        text="GREEN",
        description="Green - non-flammable gas (Class 2.2)",
        meaning=HEX["00FF00"])
    YELLOW = PermissibleValue(
        text="YELLOW",
        description="Yellow - oxidizer, organic peroxide (Classes 5.1, 5.2)",
        meaning=HEX["FFFF00"])
    WHITE = PermissibleValue(
        text="WHITE",
        description="White - poison/toxic (Class 6.1)",
        meaning=HEX["FFFFFF"])
    BLACK_WHITE_STRIPES = PermissibleValue(
        text="BLACK_WHITE_STRIPES",
        description="Black and white stripes - corrosive (Class 8)")
    BLUE = PermissibleValue(
        text="BLUE",
        description="Blue - dangerous when wet (Class 4.3)",
        meaning=HEX["0000FF"])
    WHITE_RED_STRIPES = PermissibleValue(
        text="WHITE_RED_STRIPES",
        description="White with red stripes - flammable solid (Class 4.1)")

    _defn = EnumDefinition(
        name="HazmatColorEnum",
        description="Hazardous materials placarding colors (DOT/UN)",
    )

class FireSafetyColorEnum(EnumDefinitionImpl):
    """
    Fire safety equipment and signage colors
    """
    FIRE_RED = PermissibleValue(
        text="FIRE_RED",
        description="Fire red - fire equipment",
        meaning=HEX["C8102E"])
    PHOTOLUMINESCENT_GREEN = PermissibleValue(
        text="PHOTOLUMINESCENT_GREEN",
        description="Photoluminescent green - emergency escape",
        meaning=HEX["7FFF00"])
    YELLOW_BLACK_STRIPES = PermissibleValue(
        text="YELLOW_BLACK_STRIPES",
        description="Yellow with black stripes - fire hazard area")
    WHITE = PermissibleValue(
        text="WHITE",
        description="White - fire protection water",
        meaning=HEX["FFFFFF"])
    BLUE = PermissibleValue(
        text="BLUE",
        description="Blue - mandatory fire safety",
        meaning=HEX["005EB8"])

    _defn = EnumDefinition(
        name="FireSafetyColorEnum",
        description="Fire safety equipment and signage colors",
    )

class MaritimeSignalColorEnum(EnumDefinitionImpl):
    """
    Maritime signal and navigation colors
    """
    PORT_RED = PermissibleValue(
        text="PORT_RED",
        description="Port (left) red light",
        meaning=HEX["FF0000"])
    STARBOARD_GREEN = PermissibleValue(
        text="STARBOARD_GREEN",
        description="Starboard (right) green light",
        meaning=HEX["00FF00"])
    STERN_WHITE = PermissibleValue(
        text="STERN_WHITE",
        description="Stern white light",
        meaning=HEX["FFFFFF"])
    MASTHEAD_WHITE = PermissibleValue(
        text="MASTHEAD_WHITE",
        description="Masthead white light",
        meaning=HEX["FFFFFF"])
    ALL_ROUND_WHITE = PermissibleValue(
        text="ALL_ROUND_WHITE",
        description="All-round white light",
        meaning=HEX["FFFFFF"])
    YELLOW_TOWING = PermissibleValue(
        text="YELLOW_TOWING",
        description="Yellow towing light",
        meaning=HEX["FFFF00"])
    BLUE_FLASHING = PermissibleValue(
        text="BLUE_FLASHING",
        description="Blue flashing light",
        meaning=HEX["0000FF"])

    _defn = EnumDefinition(
        name="MaritimeSignalColorEnum",
        description="Maritime signal and navigation colors",
    )

class AviationLightColorEnum(EnumDefinitionImpl):
    """
    Aviation lighting colors
    """
    RED_BEACON = PermissibleValue(
        text="RED_BEACON",
        description="Red obstruction light",
        meaning=HEX["FF0000"])
    WHITE_STROBE = PermissibleValue(
        text="WHITE_STROBE",
        description="White anti-collision strobe",
        meaning=HEX["FFFFFF"])
    GREEN_NAVIGATION = PermissibleValue(
        text="GREEN_NAVIGATION",
        description="Green navigation light (right wing)",
        meaning=HEX["00FF00"])
    RED_NAVIGATION = PermissibleValue(
        text="RED_NAVIGATION",
        description="Red navigation light (left wing)",
        meaning=HEX["FF0000"])
    WHITE_NAVIGATION = PermissibleValue(
        text="WHITE_NAVIGATION",
        description="White navigation light (tail)",
        meaning=HEX["FFFFFF"])
    BLUE_TAXIWAY = PermissibleValue(
        text="BLUE_TAXIWAY",
        description="Blue taxiway edge lights",
        meaning=HEX["0000FF"])
    YELLOW_RUNWAY = PermissibleValue(
        text="YELLOW_RUNWAY",
        description="Yellow runway markings",
        meaning=HEX["FFFF00"])
    GREEN_THRESHOLD = PermissibleValue(
        text="GREEN_THRESHOLD",
        description="Green runway threshold lights",
        meaning=HEX["00FF00"])
    RED_RUNWAY_END = PermissibleValue(
        text="RED_RUNWAY_END",
        description="Red runway end lights",
        meaning=HEX["FF0000"])

    _defn = EnumDefinition(
        name="AviationLightColorEnum",
        description="Aviation lighting colors",
    )

class ElectricalWireColorEnum(EnumDefinitionImpl):
    """
    Electrical wire color codes (US/International)
    """
    BLACK_HOT = PermissibleValue(
        text="BLACK_HOT",
        description="Black - hot/live wire (US)",
        meaning=HEX["000000"])
    RED_HOT = PermissibleValue(
        text="RED_HOT",
        description="Red - hot/live wire (US secondary)",
        meaning=HEX["FF0000"])
    BLUE_HOT = PermissibleValue(
        text="BLUE_HOT",
        description="Blue - hot/live wire (US tertiary)",
        meaning=HEX["0000FF"])
    WHITE_NEUTRAL = PermissibleValue(
        text="WHITE_NEUTRAL",
        description="White - neutral wire (US)",
        meaning=HEX["FFFFFF"])
    GREEN_GROUND = PermissibleValue(
        text="GREEN_GROUND",
        description="Green - ground/earth wire",
        meaning=HEX["00FF00"])
    GREEN_YELLOW_GROUND = PermissibleValue(
        text="GREEN_YELLOW_GROUND",
        description="Green with yellow stripe - ground/earth (International)")
    BROWN_LIVE = PermissibleValue(
        text="BROWN_LIVE",
        description="Brown - live wire (EU/IEC)",
        meaning=HEX["964B00"])
    BLUE_NEUTRAL = PermissibleValue(
        text="BLUE_NEUTRAL",
        description="Blue - neutral wire (EU/IEC)",
        meaning=HEX["0000FF"])
    GRAY_NEUTRAL = PermissibleValue(
        text="GRAY_NEUTRAL",
        description="Gray - neutral wire (alternative)",
        meaning=HEX["808080"])

    _defn = EnumDefinition(
        name="ElectricalWireColorEnum",
        description="Electrical wire color codes (US/International)",
    )

class BloodTypeEnum(EnumDefinitionImpl):
    """
    ABO and Rh blood group classifications
    """
    A_POSITIVE = PermissibleValue(
        text="A_POSITIVE",
        description="Blood type A, Rh positive",
        meaning=SNOMED["278149003"])
    A_NEGATIVE = PermissibleValue(
        text="A_NEGATIVE",
        description="Blood type A, Rh negative",
        meaning=SNOMED["278152006"])
    B_POSITIVE = PermissibleValue(
        text="B_POSITIVE",
        description="Blood type B, Rh positive",
        meaning=SNOMED["278150003"])
    B_NEGATIVE = PermissibleValue(
        text="B_NEGATIVE",
        description="Blood type B, Rh negative",
        meaning=SNOMED["278153001"])
    AB_POSITIVE = PermissibleValue(
        text="AB_POSITIVE",
        description="Blood type AB, Rh positive (universal recipient)",
        meaning=SNOMED["278151004"])
    AB_NEGATIVE = PermissibleValue(
        text="AB_NEGATIVE",
        description="Blood type AB, Rh negative",
        meaning=SNOMED["278154007"])
    O_POSITIVE = PermissibleValue(
        text="O_POSITIVE",
        description="Blood type O, Rh positive",
        meaning=SNOMED["278147001"])
    O_NEGATIVE = PermissibleValue(
        text="O_NEGATIVE",
        description="Blood type O, Rh negative (universal donor)",
        meaning=SNOMED["278148006"])

    _defn = EnumDefinition(
        name="BloodTypeEnum",
        description="ABO and Rh blood group classifications",
    )

class AnatomicalSystemEnum(EnumDefinitionImpl):
    """
    Major anatomical systems of the body
    """
    CARDIOVASCULAR = PermissibleValue(
        text="CARDIOVASCULAR",
        title="Heart and blood vessels",
        meaning=UBERON["0004535"])
    RESPIRATORY = PermissibleValue(
        text="RESPIRATORY",
        title="Lungs and airways",
        meaning=UBERON["0001004"])
    NERVOUS = PermissibleValue(
        text="NERVOUS",
        title="Brain, spinal cord, and nerves",
        meaning=UBERON["0001016"])
    DIGESTIVE = PermissibleValue(
        text="DIGESTIVE",
        title="GI tract and accessory organs",
        meaning=UBERON["0001007"])
    MUSCULOSKELETAL = PermissibleValue(
        text="MUSCULOSKELETAL",
        title="Bones, muscles, and connective tissue",
        meaning=UBERON["0002204"])
    INTEGUMENTARY = PermissibleValue(
        text="INTEGUMENTARY",
        title="Skin and related structures",
        meaning=UBERON["0002416"])
    ENDOCRINE = PermissibleValue(
        text="ENDOCRINE",
        title="Hormone-producing glands",
        meaning=UBERON["0000949"])
    URINARY = PermissibleValue(
        text="URINARY",
        title="Kidneys and urinary tract",
        meaning=UBERON["0001008"])
    REPRODUCTIVE = PermissibleValue(
        text="REPRODUCTIVE",
        title="Reproductive organs",
        meaning=UBERON["0000990"])
    IMMUNE = PermissibleValue(
        text="IMMUNE",
        title="Immune and lymphatic system",
        meaning=UBERON["0002405"])
    HEMATOLOGIC = PermissibleValue(
        text="HEMATOLOGIC",
        title="Blood and blood-forming organs",
        meaning=UBERON["0002390"])

    _defn = EnumDefinition(
        name="AnatomicalSystemEnum",
        description="Major anatomical systems of the body",
    )

class MedicalSpecialtyEnum(EnumDefinitionImpl):

    ANESTHESIOLOGY = PermissibleValue(
        text="ANESTHESIOLOGY",
        title="Anesthesia and perioperative medicine")
    CARDIOLOGY = PermissibleValue(
        text="CARDIOLOGY",
        title="Heart and cardiovascular diseases")
    DERMATOLOGY = PermissibleValue(
        text="DERMATOLOGY",
        title="Skin diseases")
    EMERGENCY_MEDICINE = PermissibleValue(
        text="EMERGENCY_MEDICINE",
        title="Emergency and acute care")
    ENDOCRINOLOGY = PermissibleValue(
        text="ENDOCRINOLOGY",
        title="Hormonal and metabolic disorders")
    FAMILY_MEDICINE = PermissibleValue(
        text="FAMILY_MEDICINE",
        title="Primary care for all ages")
    GASTROENTEROLOGY = PermissibleValue(
        text="GASTROENTEROLOGY",
        title="Digestive system disorders")
    HEMATOLOGY = PermissibleValue(
        text="HEMATOLOGY",
        title="Blood disorders")
    INFECTIOUS_DISEASE = PermissibleValue(
        text="INFECTIOUS_DISEASE",
        title="Infectious diseases")
    INTERNAL_MEDICINE = PermissibleValue(
        text="INTERNAL_MEDICINE",
        title="Adult internal medicine")
    NEPHROLOGY = PermissibleValue(
        text="NEPHROLOGY",
        title="Kidney diseases")
    NEUROLOGY = PermissibleValue(
        text="NEUROLOGY",
        title="Nervous system disorders")
    OBSTETRICS_GYNECOLOGY = PermissibleValue(
        text="OBSTETRICS_GYNECOLOGY",
        title="Women's health and childbirth")
    ONCOLOGY = PermissibleValue(
        text="ONCOLOGY",
        title="Cancer treatment")
    OPHTHALMOLOGY = PermissibleValue(
        text="OPHTHALMOLOGY",
        title="Eye diseases")
    ORTHOPEDICS = PermissibleValue(
        text="ORTHOPEDICS",
        title="Musculoskeletal disorders")
    OTOLARYNGOLOGY = PermissibleValue(
        text="OTOLARYNGOLOGY",
        title="Ear, nose, and throat")
    PATHOLOGY = PermissibleValue(
        text="PATHOLOGY",
        title="Disease diagnosis through lab analysis")
    PEDIATRICS = PermissibleValue(
        text="PEDIATRICS",
        title="Children's health")
    PSYCHIATRY = PermissibleValue(
        text="PSYCHIATRY",
        title="Mental health disorders")
    PULMONOLOGY = PermissibleValue(
        text="PULMONOLOGY",
        title="Lung and respiratory diseases")
    RADIOLOGY = PermissibleValue(
        text="RADIOLOGY",
        title="Medical imaging")
    RHEUMATOLOGY = PermissibleValue(
        text="RHEUMATOLOGY",
        title="Joint and autoimmune diseases")
    SURGERY = PermissibleValue(
        text="SURGERY",
        title="Surgical procedures")
    UROLOGY = PermissibleValue(
        text="UROLOGY",
        title="Urinary and male reproductive system")

    _defn = EnumDefinition(
        name="MedicalSpecialtyEnum",
    )

class DrugRouteEnum(EnumDefinitionImpl):

    ORAL = PermissibleValue(
        text="ORAL",
        title="By mouth",
        meaning=NCIT["C38288"])
    INTRAVENOUS = PermissibleValue(
        text="INTRAVENOUS",
        title="Into a vein",
        meaning=NCIT["C38276"])
    INTRAMUSCULAR = PermissibleValue(
        text="INTRAMUSCULAR",
        title="Into muscle",
        meaning=NCIT["C28161"])
    SUBCUTANEOUS = PermissibleValue(
        text="SUBCUTANEOUS",
        title="Under the skin",
        meaning=NCIT["C38299"])
    TOPICAL = PermissibleValue(
        text="TOPICAL",
        title="On the skin surface",
        meaning=NCIT["C38304"])
    INHALATION = PermissibleValue(
        text="INHALATION",
        title="By breathing in",
        meaning=NCIT["C38216"])
    RECTAL = PermissibleValue(
        text="RECTAL",
        title="Into the rectum",
        meaning=NCIT["C38295"])
    INTRANASAL = PermissibleValue(
        text="INTRANASAL",
        title="Into the nose",
        meaning=NCIT["C38284"])
    TRANSDERMAL = PermissibleValue(
        text="TRANSDERMAL",
        title="Through the skin",
        meaning=NCIT["C38305"])
    SUBLINGUAL = PermissibleValue(
        text="SUBLINGUAL",
        title="Under the tongue",
        meaning=NCIT["C38300"])
    EPIDURAL = PermissibleValue(
        text="EPIDURAL",
        title="Into epidural space",
        meaning=NCIT["C38243"])
    INTRATHECAL = PermissibleValue(
        text="INTRATHECAL",
        title="Into spinal fluid",
        meaning=NCIT["C38277"])
    OPHTHALMIC = PermissibleValue(
        text="OPHTHALMIC",
        title="Into the eye",
        meaning=NCIT["C38287"])
    OTIC = PermissibleValue(
        text="OTIC",
        title="Into the ear",
        meaning=NCIT["C38192"])

    _defn = EnumDefinition(
        name="DrugRouteEnum",
    )

class VitalSignEnum(EnumDefinitionImpl):

    HEART_RATE = PermissibleValue(
        text="HEART_RATE",
        title="Heart beats per minute",
        meaning=LOINC["8867-4"])
    BLOOD_PRESSURE_SYSTOLIC = PermissibleValue(
        text="BLOOD_PRESSURE_SYSTOLIC",
        title="Systolic blood pressure",
        meaning=LOINC["8480-6"])
    BLOOD_PRESSURE_DIASTOLIC = PermissibleValue(
        text="BLOOD_PRESSURE_DIASTOLIC",
        title="Diastolic blood pressure",
        meaning=LOINC["8462-4"])
    RESPIRATORY_RATE = PermissibleValue(
        text="RESPIRATORY_RATE",
        title="Breaths per minute",
        meaning=LOINC["9279-1"])
    TEMPERATURE = PermissibleValue(
        text="TEMPERATURE",
        title="Body temperature",
        meaning=LOINC["8310-5"])
    OXYGEN_SATURATION = PermissibleValue(
        text="OXYGEN_SATURATION",
        title="Blood oxygen saturation",
        meaning=LOINC["2708-6"])
    PAIN_SCALE = PermissibleValue(
        text="PAIN_SCALE",
        title="Pain level (0-10)",
        meaning=LOINC["38208-5"])

    _defn = EnumDefinition(
        name="VitalSignEnum",
    )

class DiagnosticTestTypeEnum(EnumDefinitionImpl):

    BLOOD_TEST = PermissibleValue(
        text="BLOOD_TEST",
        title="Blood sample analysis",
        meaning=NCIT["C15189"])
    URINE_TEST = PermissibleValue(
        text="URINE_TEST",
        title="Urine sample analysis")
    IMAGING_XRAY = PermissibleValue(
        text="IMAGING_XRAY",
        title="X-ray imaging",
        meaning=NCIT["C17262"])
    IMAGING_CT = PermissibleValue(
        text="IMAGING_CT",
        title="Computed tomography scan",
        meaning=NCIT["C17204"])
    IMAGING_MRI = PermissibleValue(
        text="IMAGING_MRI",
        title="Magnetic resonance imaging",
        meaning=NCIT["C16809"])
    IMAGING_ULTRASOUND = PermissibleValue(
        text="IMAGING_ULTRASOUND",
        title="Ultrasound imaging",
        meaning=NCIT["C17230"])
    IMAGING_PET = PermissibleValue(
        text="IMAGING_PET",
        title="Positron emission tomography",
        meaning=NCIT["C17007"])
    ECG = PermissibleValue(
        text="ECG",
        title="Electrocardiogram",
        meaning=NCIT["C38054"])
    EEG = PermissibleValue(
        text="EEG",
        title="Electroencephalogram")
    BIOPSY = PermissibleValue(
        text="BIOPSY",
        title="Tissue sample analysis",
        meaning=NCIT["C15189"])
    ENDOSCOPY = PermissibleValue(
        text="ENDOSCOPY",
        title="Internal visualization",
        meaning=NCIT["C16546"])
    GENETIC_TEST = PermissibleValue(
        text="GENETIC_TEST",
        title="DNA/RNA analysis",
        meaning=NCIT["C15709"])

    _defn = EnumDefinition(
        name="DiagnosticTestTypeEnum",
    )

class SymptomSeverityEnum(EnumDefinitionImpl):

    ABSENT = PermissibleValue(
        text="ABSENT",
        title="No symptoms")
    MILD = PermissibleValue(
        text="MILD",
        title="Mild symptoms, minimal impact",
        meaning=HP["0012825"])
    MODERATE = PermissibleValue(
        text="MODERATE",
        title="Moderate symptoms, some limitation",
        meaning=HP["0012826"])
    SEVERE = PermissibleValue(
        text="SEVERE",
        title="Severe symptoms, significant limitation",
        meaning=HP["0012828"])
    LIFE_THREATENING = PermissibleValue(
        text="LIFE_THREATENING",
        title="Life-threatening symptoms")

    _defn = EnumDefinition(
        name="SymptomSeverityEnum",
    )

class AllergyTypeEnum(EnumDefinitionImpl):

    DRUG = PermissibleValue(
        text="DRUG",
        title="Drug allergy",
        meaning=NCIT["C3114"])
    FOOD = PermissibleValue(
        text="FOOD",
        title="Food allergy")
    ENVIRONMENTAL = PermissibleValue(
        text="ENVIRONMENTAL",
        title="Environmental allergy")
    CONTACT = PermissibleValue(
        text="CONTACT",
        title="Contact dermatitis")
    INSECT = PermissibleValue(
        text="INSECT",
        title="Insect sting allergy")
    ANAPHYLAXIS = PermissibleValue(
        text="ANAPHYLAXIS",
        title="Severe systemic reaction")

    _defn = EnumDefinition(
        name="AllergyTypeEnum",
    )

class VaccineTypeEnum(EnumDefinitionImpl):

    LIVE_ATTENUATED = PermissibleValue(
        text="LIVE_ATTENUATED",
        title="Weakened live pathogen")
    INACTIVATED = PermissibleValue(
        text="INACTIVATED",
        title="Killed pathogen")
    SUBUNIT = PermissibleValue(
        text="SUBUNIT",
        title="Pathogen pieces")
    TOXOID = PermissibleValue(
        text="TOXOID",
        title="Inactivated toxin")
    MRNA = PermissibleValue(
        text="MRNA",
        title="mRNA vaccine")
    VIRAL_VECTOR = PermissibleValue(
        text="VIRAL_VECTOR",
        title="Modified virus carrier")

    _defn = EnumDefinition(
        name="VaccineTypeEnum",
    )

class BMIClassificationEnum(EnumDefinitionImpl):

    UNDERWEIGHT = PermissibleValue(
        text="UNDERWEIGHT",
        title="BMI less than 18.5")
    NORMAL_WEIGHT = PermissibleValue(
        text="NORMAL_WEIGHT",
        title="BMI 18.5-24.9")
    OVERWEIGHT = PermissibleValue(
        text="OVERWEIGHT",
        title="BMI 25.0-29.9")
    OBESE_CLASS_I = PermissibleValue(
        text="OBESE_CLASS_I",
        title="BMI 30.0-34.9")
    OBESE_CLASS_II = PermissibleValue(
        text="OBESE_CLASS_II",
        title="BMI 35.0-39.9")
    OBESE_CLASS_III = PermissibleValue(
        text="OBESE_CLASS_III",
        title="BMI 40.0 or greater")

    _defn = EnumDefinition(
        name="BMIClassificationEnum",
    )

class MRIModalityEnum(EnumDefinitionImpl):
    """
    MRI imaging modalities and techniques
    """
    STRUCTURAL_T1 = PermissibleValue(
        text="STRUCTURAL_T1",
        title="T1-weighted structural MRI",
        description="High-resolution anatomical imaging with T1 contrast",
        meaning=NCIT["C116455"])
    STRUCTURAL_T2 = PermissibleValue(
        text="STRUCTURAL_T2",
        title="T2-weighted structural MRI",
        description="Structural imaging with T2 contrast",
        meaning=NCIT["C116456"])
    FLAIR = PermissibleValue(
        text="FLAIR",
        title="Fluid-attenuated inversion recovery",
        description="T2-weighted sequence with CSF signal suppressed",
        meaning=NCIT["C82392"])
    BOLD_FMRI = PermissibleValue(
        text="BOLD_FMRI",
        title="Blood oxygen level dependent fMRI",
        description="Functional MRI based on blood oxygenation changes",
        meaning=NCIT["C17958"])
    ASL = PermissibleValue(
        text="ASL",
        title="Arterial spin labeling",
        description="Perfusion imaging using magnetically labeled blood",
        meaning=NCIT["C116450"])
    DWI = PermissibleValue(
        text="DWI",
        title="Diffusion-weighted imaging",
        description="Imaging sensitive to water molecule diffusion",
        meaning=MESH["D038524"])
    DTI = PermissibleValue(
        text="DTI",
        title="Diffusion tensor imaging",
        description="Advanced diffusion imaging with directional information",
        meaning=NCIT["C64862"])
    PERFUSION_DSC = PermissibleValue(
        text="PERFUSION_DSC",
        title="Dynamic susceptibility contrast perfusion",
        description="Perfusion imaging using contrast agent bolus",
        meaning=NCIT["C116459"])
    PERFUSION_DCE = PermissibleValue(
        text="PERFUSION_DCE",
        title="Dynamic contrast-enhanced perfusion",
        description="Perfusion imaging with pharmacokinetic modeling",
        meaning=NCIT["C116458"])
    SWI = PermissibleValue(
        text="SWI",
        title="Susceptibility-weighted imaging",
        description="High-resolution venography and iron detection",
        meaning=NCIT["C121377"])
    TASK_FMRI = PermissibleValue(
        text="TASK_FMRI",
        title="Task-based functional MRI",
        description="fMRI during specific cognitive or motor tasks",
        meaning=NCIT["C178023"])
    RESTING_STATE_FMRI = PermissibleValue(
        text="RESTING_STATE_FMRI",
        title="Resting-state functional MRI",
        description="fMRI acquired at rest without explicit tasks",
        meaning=NCIT["C178024"])
    FUNCTIONAL_CONNECTIVITY = PermissibleValue(
        text="FUNCTIONAL_CONNECTIVITY",
        title="Functional connectivity MRI",
        description="Analysis of temporal correlations between brain regions",
        meaning=NCIT["C116454"])

    _defn = EnumDefinition(
        name="MRIModalityEnum",
        description="MRI imaging modalities and techniques",
    )

class MRISequenceTypeEnum(EnumDefinitionImpl):
    """
    MRI pulse sequence types
    """
    GRADIENT_ECHO = PermissibleValue(
        text="GRADIENT_ECHO",
        title="Gradient echo sequence",
        description="Fast imaging sequence using gradient reversal",
        meaning=NCIT["C154542"])
    SPIN_ECHO = PermissibleValue(
        text="SPIN_ECHO",
        title="Spin echo sequence",
        description="Sequence using 180-degree refocusing pulse",
        meaning=CHMO["0001868"])
    EPI = PermissibleValue(
        text="EPI",
        title="Echo planar imaging",
        description="Ultrafast imaging sequence",
        meaning=NCIT["C17558"])
    MPRAGE = PermissibleValue(
        text="MPRAGE",
        title="Magnetization prepared rapid gradient echo",
        description="T1-weighted 3D sequence with preparation pulse",
        meaning=NCIT["C118462"])
    SPACE = PermissibleValue(
        text="SPACE",
        title="Sampling perfection with application optimized contrasts",
        description="3D turbo spin echo sequence")
    TRUFI = PermissibleValue(
        text="TRUFI",
        title="True fast imaging with steady-state precession",
        description="Balanced steady-state free precession sequence",
        meaning=NCIT["C200534"])

    _defn = EnumDefinition(
        name="MRISequenceTypeEnum",
        description="MRI pulse sequence types",
    )

class MRIContrastTypeEnum(EnumDefinitionImpl):
    """
    MRI image contrast mechanisms
    """
    T1_WEIGHTED = PermissibleValue(
        text="T1_WEIGHTED",
        title="T1-weighted contrast",
        description="Image contrast based on T1 relaxation times",
        meaning=NCIT["C180727"])
    T2_WEIGHTED = PermissibleValue(
        text="T2_WEIGHTED",
        title="T2-weighted contrast",
        description="Image contrast based on T2 relaxation times",
        meaning=NCIT["C180729"])
    T2_STAR = PermissibleValue(
        text="T2_STAR",
        title="T2*-weighted contrast",
        description="Image contrast sensitive to magnetic susceptibility",
        meaning=NCIT["C156447"])
    PROTON_DENSITY = PermissibleValue(
        text="PROTON_DENSITY",
        title="Proton density weighted",
        description="Image contrast based on hydrogen density",
        meaning=NCIT["C170797"])
    DIFFUSION_WEIGHTED = PermissibleValue(
        text="DIFFUSION_WEIGHTED",
        title="Diffusion-weighted contrast",
        description="Image contrast based on water diffusion",
        meaning=NCIT["C111116"])
    PERFUSION_WEIGHTED = PermissibleValue(
        text="PERFUSION_WEIGHTED",
        title="Perfusion-weighted contrast",
        description="Image contrast based on blood flow dynamics",
        meaning=MESH["D000098642"])

    _defn = EnumDefinition(
        name="MRIContrastTypeEnum",
        description="MRI image contrast mechanisms",
    )

class FMRIParadigmTypeEnum(EnumDefinitionImpl):
    """
    fMRI experimental paradigm types
    """
    BLOCK_DESIGN = PermissibleValue(
        text="BLOCK_DESIGN",
        title="Block design paradigm",
        description="Alternating blocks of task and rest conditions",
        meaning=STATO["0000046"])
    EVENT_RELATED = PermissibleValue(
        text="EVENT_RELATED",
        title="Event-related design",
        description="Brief stimuli presented at varying intervals",
        meaning=EDAM["topic_3678"])
    MIXED_DESIGN = PermissibleValue(
        text="MIXED_DESIGN",
        title="Mixed block and event-related design",
        description="Combination of block and event-related elements",
        meaning=EDAM["topic_3678"])
    RESTING_STATE = PermissibleValue(
        text="RESTING_STATE",
        title="Resting state paradigm",
        description="No explicit task, spontaneous brain activity",
        meaning=NCIT["C178024"])
    NATURALISTIC = PermissibleValue(
        text="NATURALISTIC",
        title="Naturalistic paradigm",
        description="Ecologically valid stimuli (movies, stories)",
        meaning=EDAM["topic_3678"])

    _defn = EnumDefinition(
        name="FMRIParadigmTypeEnum",
        description="fMRI experimental paradigm types",
    )

class RaceOMB1997Enum(EnumDefinitionImpl):
    """
    Race categories following OMB 1997 standards used by NIH and federal agencies.
    Respondents may select multiple races.
    """
    AMERICAN_INDIAN_OR_ALASKA_NATIVE = PermissibleValue(
        text="AMERICAN_INDIAN_OR_ALASKA_NATIVE",
        description="""A person having origins in any of the original peoples of North and South America (including Central America), and who maintains tribal affiliation or community attachment""",
        meaning=NCIT["C41259"])
    ASIAN = PermissibleValue(
        text="ASIAN",
        description="""A person having origins in any of the original peoples of the Far East, Southeast Asia, or the Indian subcontinent""",
        meaning=NCIT["C41260"])
    BLACK_OR_AFRICAN_AMERICAN = PermissibleValue(
        text="BLACK_OR_AFRICAN_AMERICAN",
        description="A person having origins in any of the black racial groups of Africa",
        meaning=NCIT["C16352"])
    NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = PermissibleValue(
        text="NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER",
        description="""A person having origins in any of the original peoples of Hawaii, Guam, Samoa, or other Pacific Islands""",
        meaning=NCIT["C41219"])
    WHITE = PermissibleValue(
        text="WHITE",
        description="""A person having origins in any of the original peoples of Europe, the Middle East, or North Africa""",
        meaning=NCIT["C41261"])
    MORE_THAN_ONE_RACE = PermissibleValue(
        text="MORE_THAN_ONE_RACE",
        title="Multiracial",
        description="Person identifies with more than one race category",
        meaning=NCIT["C67109"])
    UNKNOWN_OR_NOT_REPORTED = PermissibleValue(
        text="UNKNOWN_OR_NOT_REPORTED",
        title="Unknown",
        description="Race not known, not reported, or declined to answer",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="RaceOMB1997Enum",
        description="""Race categories following OMB 1997 standards used by NIH and federal agencies.
Respondents may select multiple races.""",
    )

class EthnicityOMB1997Enum(EnumDefinitionImpl):
    """
    Ethnicity categories following OMB 1997 standards used by NIH and federal agencies
    """
    HISPANIC_OR_LATINO = PermissibleValue(
        text="HISPANIC_OR_LATINO",
        description="""A person of Cuban, Mexican, Puerto Rican, South or Central American, or other Spanish culture or origin, regardless of race""",
        meaning=NCIT["C17459"])
    NOT_HISPANIC_OR_LATINO = PermissibleValue(
        text="NOT_HISPANIC_OR_LATINO",
        description="A person not of Hispanic or Latino origin",
        meaning=NCIT["C41222"])
    UNKNOWN_OR_NOT_REPORTED = PermissibleValue(
        text="UNKNOWN_OR_NOT_REPORTED",
        title="Unknown",
        description="Ethnicity not known, not reported, or declined to answer",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="EthnicityOMB1997Enum",
        description="Ethnicity categories following OMB 1997 standards used by NIH and federal agencies",
    )

class BiologicalSexEnum(EnumDefinitionImpl):
    """
    Biological sex assigned at birth based on anatomical and physiological traits.
    Required by NIH as a biological variable in research.
    """
    MALE = PermissibleValue(
        text="MALE",
        description="Male sex assigned at birth",
        meaning=PATO["0000384"])
    FEMALE = PermissibleValue(
        text="FEMALE",
        description="Female sex assigned at birth",
        meaning=PATO["0000383"])
    INTERSEX = PermissibleValue(
        text="INTERSEX",
        description="""Born with reproductive or sexual anatomy that doesn't fit typical definitions of male or female""",
        meaning=NCIT["C45908"])
    UNKNOWN_OR_NOT_REPORTED = PermissibleValue(
        text="UNKNOWN_OR_NOT_REPORTED",
        title="Unknown",
        description="Sex not known, not reported, or declined to answer",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="BiologicalSexEnum",
        description="""Biological sex assigned at birth based on anatomical and physiological traits.
Required by NIH as a biological variable in research.""",
    )

class AgeGroupEnum(EnumDefinitionImpl):
    """
    Standard age groups used in NIH clinical research, particularly NINDS CDEs
    """
    NEONATE = PermissibleValue(
        text="NEONATE",
        title="Newborn",
        description="Birth to 28 days",
        meaning=NCIT["C16731"])
    INFANT = PermissibleValue(
        text="INFANT",
        description="29 days to less than 1 year",
        meaning=NCIT["C27956"])
    YOUNG_PEDIATRIC = PermissibleValue(
        text="YOUNG_PEDIATRIC",
        title="Pediatric",
        description="0 to 5 years (NINDS CDE definition)",
        meaning=NCIT["C39299"])
    PEDIATRIC = PermissibleValue(
        text="PEDIATRIC",
        title="Child",
        description="6 to 12 years (NINDS CDE definition)",
        meaning=NCIT["C16423"])
    ADOLESCENT = PermissibleValue(
        text="ADOLESCENT",
        description="13 to 17 years",
        meaning=NCIT["C27954"])
    YOUNG_ADULT = PermissibleValue(
        text="YOUNG_ADULT",
        description="18 to 24 years",
        meaning=NCIT["C91107"])
    ADULT = PermissibleValue(
        text="ADULT",
        description="25 to 64 years",
        meaning=NCIT["C17600"])
    OLDER_ADULT = PermissibleValue(
        text="OLDER_ADULT",
        title="Elderly",
        description="65 years and older",
        meaning=NCIT["C16268"])

    _defn = EnumDefinition(
        name="AgeGroupEnum",
        description="Standard age groups used in NIH clinical research, particularly NINDS CDEs",
    )

class ParticipantVitalStatusEnum(EnumDefinitionImpl):
    """
    Vital status of a research participant in clinical studies
    """
    ALIVE = PermissibleValue(
        text="ALIVE",
        description="Participant is living",
        meaning=NCIT["C37987"])
    DECEASED = PermissibleValue(
        text="DECEASED",
        title="Dead",
        description="Participant is deceased",
        meaning=NCIT["C28554"])
    UNKNOWN = PermissibleValue(
        text="UNKNOWN",
        description="Vital status unknown or lost to follow-up",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="ParticipantVitalStatusEnum",
        description="Vital status of a research participant in clinical studies",
    )

class RecruitmentStatusEnum(EnumDefinitionImpl):
    """
    Clinical trial or study recruitment status per NIH/ClinicalTrials.gov
    """
    NOT_YET_RECRUITING = PermissibleValue(
        text="NOT_YET_RECRUITING",
        title="Not Yet Enrolling",
        description="Study has not started recruiting participants",
        meaning=NCIT["C211610"])
    RECRUITING = PermissibleValue(
        text="RECRUITING",
        title="Open To Enrollment",
        description="Currently recruiting participants",
        meaning=NCIT["C142621"])
    ENROLLING_BY_INVITATION = PermissibleValue(
        text="ENROLLING_BY_INVITATION",
        description="Enrolling participants by invitation only",
        meaning=NCIT["C211611"])
    ACTIVE_NOT_RECRUITING = PermissibleValue(
        text="ACTIVE_NOT_RECRUITING",
        title="Study Active, Not Enrolling",
        description="Study ongoing but not recruiting new participants",
        meaning=NCIT["C211612"])
    SUSPENDED = PermissibleValue(
        text="SUSPENDED",
        title="Study Enrollment Suspended",
        description="Study temporarily stopped",
        meaning=NCIT["C211613"])
    TERMINATED = PermissibleValue(
        text="TERMINATED",
        title="Study Terminated",
        description="Study stopped early and will not resume",
        meaning=NCIT["C70757"])
    COMPLETED = PermissibleValue(
        text="COMPLETED",
        title="Completed Clinical Study",
        description="Study has ended normally",
        meaning=NCIT["C70756"])
    WITHDRAWN = PermissibleValue(
        text="WITHDRAWN",
        title="Study Withdrawn",
        description="Study withdrawn before enrollment",
        meaning=NCIT["C70758"])

    _defn = EnumDefinition(
        name="RecruitmentStatusEnum",
        description="Clinical trial or study recruitment status per NIH/ClinicalTrials.gov",
    )

class StudyPhaseEnum(EnumDefinitionImpl):
    """
    Clinical trial phases per FDA and NIH definitions
    """
    EARLY_PHASE_1 = PermissibleValue(
        text="EARLY_PHASE_1",
        title="Phase 0 Trial",
        description="Exploratory trials before traditional Phase 1",
        meaning=NCIT["C54721"])
    PHASE_1 = PermissibleValue(
        text="PHASE_1",
        title="Phase I Trial",
        description="Initial safety and dosage studies",
        meaning=NCIT["C15600"])
    PHASE_1_2 = PermissibleValue(
        text="PHASE_1_2",
        title="Phase II/III Trial",
        description="Combined Phase 1 and Phase 2 trial",
        meaning=NCIT["C15694"])
    PHASE_2 = PermissibleValue(
        text="PHASE_2",
        title="Phase II Trial",
        description="Efficacy and side effects studies",
        meaning=NCIT["C15601"])
    PHASE_2_3 = PermissibleValue(
        text="PHASE_2_3",
        title="Phase IIa Trial",
        description="Combined Phase 2 and Phase 3 trial",
        meaning=NCIT["C49686"])
    PHASE_3 = PermissibleValue(
        text="PHASE_3",
        title="Phase III Trial",
        description="Efficacy comparison with standard treatment",
        meaning=NCIT["C15602"])
    PHASE_4 = PermissibleValue(
        text="PHASE_4",
        title="Phase IV Trial",
        description="Post-marketing surveillance",
        meaning=NCIT["C15603"])
    NOT_APPLICABLE = PermissibleValue(
        text="NOT_APPLICABLE",
        description="Not a phased clinical trial",
        meaning=NCIT["C48660"])

    _defn = EnumDefinition(
        name="StudyPhaseEnum",
        description="Clinical trial phases per FDA and NIH definitions",
    )

class KaryotypicSexEnum(EnumDefinitionImpl):
    """
    Karyotypic sex of an individual based on chromosome composition
    """
    XX = PermissibleValue(
        text="XX",
        title="XX Genotype",
        description="Female karyotype (46,XX)",
        meaning=NCIT["C45976"])
    XY = PermissibleValue(
        text="XY",
        title="XY Genotype",
        description="Male karyotype (46,XY)",
        meaning=NCIT["C45977"])
    XO = PermissibleValue(
        text="XO",
        title="45,XO Karyotype",
        description="Turner syndrome karyotype (45,X)",
        meaning=NCIT["C176780"])
    XXY = PermissibleValue(
        text="XXY",
        title="47,XXY Karyotype",
        description="Klinefelter syndrome karyotype (47,XXY)",
        meaning=NCIT["C176784"])
    XXX = PermissibleValue(
        text="XXX",
        title="47,XXX Karyotype",
        description="Triple X syndrome karyotype (47,XXX)",
        meaning=NCIT["C176785"])
    XXXY = PermissibleValue(
        text="XXXY",
        title="48,XXXY Karyotype",
        description="XXXY syndrome karyotype (48,XXXY)",
        meaning=NCIT["C176786"])
    XXXX = PermissibleValue(
        text="XXXX",
        title="48,XXXX Karyotype",
        description="Tetrasomy X karyotype (48,XXXX)",
        meaning=NCIT["C176787"])
    XXYY = PermissibleValue(
        text="XXYY",
        title="XXYY Syndrome",
        description="XXYY syndrome karyotype (48,XXYY)",
        meaning=NCIT["C89801"])
    XYY = PermissibleValue(
        text="XYY",
        title="47,XYY Karyotype",
        description="Jacob's syndrome karyotype (47,XYY)",
        meaning=NCIT["C176782"])
    OTHER_KARYOTYPE = PermissibleValue(
        text="OTHER_KARYOTYPE",
        description="Other karyotypic sex not listed")
    UNKNOWN_KARYOTYPE = PermissibleValue(
        text="UNKNOWN_KARYOTYPE",
        title="Unknown",
        description="Karyotype not determined or unknown",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="KaryotypicSexEnum",
        description="Karyotypic sex of an individual based on chromosome composition",
    )

class PhenotypicSexEnum(EnumDefinitionImpl):
    """
    Phenotypic sex of an individual based on observable characteristics.
    FHIR mapping: AdministrativeGender
    """
    MALE = PermissibleValue(
        text="MALE",
        description="Male phenotypic sex",
        meaning=PATO["0000384"])
    FEMALE = PermissibleValue(
        text="FEMALE",
        description="Female phenotypic sex",
        meaning=PATO["0000383"])
    OTHER_SEX = PermissibleValue(
        text="OTHER_SEX",
        title="Intersex",
        description="Sex characteristics not clearly male or female",
        meaning=NCIT["C45908"])
    UNKNOWN_SEX = PermissibleValue(
        text="UNKNOWN_SEX",
        title="Unknown",
        description="Sex not assessed or not available",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="PhenotypicSexEnum",
        description="""Phenotypic sex of an individual based on observable characteristics.
FHIR mapping: AdministrativeGender""",
    )

class AllelicStateEnum(EnumDefinitionImpl):
    """
    Allelic state/zygosity of a variant or genetic feature
    """
    HETEROZYGOUS = PermissibleValue(
        text="HETEROZYGOUS",
        description="Different alleles at a locus",
        meaning=GENO["0000135"])
    HOMOZYGOUS = PermissibleValue(
        text="HOMOZYGOUS",
        description="Identical alleles at a locus",
        meaning=GENO["0000136"])
    HEMIZYGOUS = PermissibleValue(
        text="HEMIZYGOUS",
        description="Only one allele present (e.g., X-linked in males)",
        meaning=GENO["0000134"])
    COMPOUND_HETEROZYGOUS = PermissibleValue(
        text="COMPOUND_HETEROZYGOUS",
        description="Two different heterozygous variants in same gene",
        meaning=GENO["0000402"])
    HOMOZYGOUS_REFERENCE = PermissibleValue(
        text="HOMOZYGOUS_REFERENCE",
        title="reference allele",
        description="Two reference/wild-type alleles",
        meaning=GENO["0000036"])
    HOMOZYGOUS_ALTERNATE = PermissibleValue(
        text="HOMOZYGOUS_ALTERNATE",
        title="variant allele",
        description="Two alternate/variant alleles",
        meaning=GENO["0000002"])

    _defn = EnumDefinition(
        name="AllelicStateEnum",
        description="Allelic state/zygosity of a variant or genetic feature",
    )

class LateralityEnum(EnumDefinitionImpl):
    """
    Laterality/sidedness of a finding or anatomical structure
    """
    RIGHT = PermissibleValue(
        text="RIGHT",
        description="Right side",
        meaning=HP["0012834"])
    LEFT = PermissibleValue(
        text="LEFT",
        description="Left side",
        meaning=HP["0012835"])
    BILATERAL = PermissibleValue(
        text="BILATERAL",
        description="Both sides",
        meaning=HP["0012832"])
    UNILATERAL = PermissibleValue(
        text="UNILATERAL",
        description="One side (unspecified which)",
        meaning=HP["0012833"])
    MIDLINE = PermissibleValue(
        text="MIDLINE",
        description="In the midline/center")

    _defn = EnumDefinition(
        name="LateralityEnum",
        description="Laterality/sidedness of a finding or anatomical structure",
    )

class OnsetTimingEnum(EnumDefinitionImpl):
    """
    Timing of disease or phenotype onset relative to developmental stages
    """
    ANTENATAL_ONSET = PermissibleValue(
        text="ANTENATAL_ONSET",
        description="Before birth (prenatal)",
        meaning=HP["0030674"])
    EMBRYONAL_ONSET = PermissibleValue(
        text="EMBRYONAL_ONSET",
        description="During embryonic period (0-8 weeks)",
        meaning=HP["0011460"])
    FETAL_ONSET = PermissibleValue(
        text="FETAL_ONSET",
        description="During fetal period (8 weeks to birth)",
        meaning=HP["0011461"])
    CONGENITAL_ONSET = PermissibleValue(
        text="CONGENITAL_ONSET",
        description="Present at birth",
        meaning=HP["0003577"])
    NEONATAL_ONSET = PermissibleValue(
        text="NEONATAL_ONSET",
        description="Within first 28 days of life",
        meaning=HP["0003623"])
    INFANTILE_ONSET = PermissibleValue(
        text="INFANTILE_ONSET",
        description="Between 28 days and 1 year",
        meaning=HP["0003593"])
    CHILDHOOD_ONSET = PermissibleValue(
        text="CHILDHOOD_ONSET",
        description="Between 1 year and 16 years",
        meaning=HP["0011463"])
    JUVENILE_ONSET = PermissibleValue(
        text="JUVENILE_ONSET",
        description="Between 5 years and 16 years",
        meaning=HP["0003621"])
    YOUNG_ADULT_ONSET = PermissibleValue(
        text="YOUNG_ADULT_ONSET",
        description="Between 16 years and 40 years",
        meaning=HP["0011462"])
    MIDDLE_AGE_ONSET = PermissibleValue(
        text="MIDDLE_AGE_ONSET",
        description="Between 40 years and 60 years",
        meaning=HP["0003596"])
    LATE_ONSET = PermissibleValue(
        text="LATE_ONSET",
        description="After 60 years",
        meaning=HP["0003584"])

    _defn = EnumDefinition(
        name="OnsetTimingEnum",
        description="Timing of disease or phenotype onset relative to developmental stages",
    )

class ACMGPathogenicityEnum(EnumDefinitionImpl):
    """
    ACMG/AMP variant pathogenicity classification for clinical genetics
    """
    PATHOGENIC = PermissibleValue(
        text="PATHOGENIC",
        title="Pathogenic Variant",
        description="Pathogenic variant",
        meaning=NCIT["C168799"])
    LIKELY_PATHOGENIC = PermissibleValue(
        text="LIKELY_PATHOGENIC",
        title="Likely Pathogenic Variant",
        description="Likely pathogenic variant",
        meaning=NCIT["C168800"])
    UNCERTAIN_SIGNIFICANCE = PermissibleValue(
        text="UNCERTAIN_SIGNIFICANCE",
        title="Variant of Unknown Significance",
        description="Variant of uncertain significance",
        meaning=NCIT["C94187"])
    LIKELY_BENIGN = PermissibleValue(
        text="LIKELY_BENIGN",
        title="Variant Likely Benign",
        description="Likely benign variant",
        meaning=NCIT["C168801"])
    BENIGN = PermissibleValue(
        text="BENIGN",
        title="Variant Benign",
        description="Benign variant",
        meaning=NCIT["C168802"])

    _defn = EnumDefinition(
        name="ACMGPathogenicityEnum",
        description="ACMG/AMP variant pathogenicity classification for clinical genetics",
    )

class TherapeuticActionabilityEnum(EnumDefinitionImpl):
    """
    Clinical actionability of a genetic finding for treatment decisions
    """
    ACTIONABLE = PermissibleValue(
        text="ACTIONABLE",
        title="Actionable Variation",
        description="Finding has direct therapeutic implications",
        meaning=NCIT["C206303"])
    NOT_ACTIONABLE = PermissibleValue(
        text="NOT_ACTIONABLE",
        title="Non-Actionable Variation",
        description="No current therapeutic implications",
        meaning=NCIT["C206304"])
    UNKNOWN_ACTIONABILITY = PermissibleValue(
        text="UNKNOWN_ACTIONABILITY",
        title="Unknown",
        description="Therapeutic implications unclear",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="TherapeuticActionabilityEnum",
        description="Clinical actionability of a genetic finding for treatment decisions",
    )

class InterpretationProgressEnum(EnumDefinitionImpl):
    """
    Progress status of clinical interpretation or diagnosis
    """
    SOLVED = PermissibleValue(
        text="SOLVED",
        title="Molecular Diagnosis",
        description="Diagnosis achieved/case solved",
        meaning=NCIT["C20826"])
    UNSOLVED = PermissibleValue(
        text="UNSOLVED",
        title="Clinical Interpretation",
        description="No diagnosis achieved",
        meaning=NCIT["C125009"])
    IN_PROGRESS = PermissibleValue(
        text="IN_PROGRESS",
        title="Progress",
        description="Analysis ongoing",
        meaning=NCIT["C25630"])
    COMPLETED = PermissibleValue(
        text="COMPLETED",
        title="Procedure Completed",
        description="Analysis completed",
        meaning=NCIT["C216251"])
    UNKNOWN_PROGRESS = PermissibleValue(
        text="UNKNOWN_PROGRESS",
        title="Unknown",
        description="Progress status unknown",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="InterpretationProgressEnum",
        description="Progress status of clinical interpretation or diagnosis",
    )

class RegimenStatusEnum(EnumDefinitionImpl):
    """
    Status of a therapeutic regimen or treatment protocol
    """
    NOT_STARTED = PermissibleValue(
        text="NOT_STARTED",
        title="Device Evaluation Anticipated But Not Yet Begun",
        description="Treatment not yet begun",
        meaning=NCIT["C53601"])
    STARTED = PermissibleValue(
        text="STARTED",
        title="Treatment Ongoing",
        description="Treatment initiated",
        meaning=NCIT["C165209"])
    COMPLETED = PermissibleValue(
        text="COMPLETED",
        title="Treatment Completed as Prescribed",
        description="Treatment finished as planned",
        meaning=NCIT["C105740"])
    DISCONTINUED_ADVERSE_EVENT = PermissibleValue(
        text="DISCONTINUED_ADVERSE_EVENT",
        title="Adverse Event",
        description="Stopped due to adverse event",
        meaning=NCIT["C41331"])
    DISCONTINUED_LACK_OF_EFFICACY = PermissibleValue(
        text="DISCONTINUED_LACK_OF_EFFICACY",
        title="Drug Withdrawn",
        description="Stopped due to lack of efficacy",
        meaning=NCIT["C49502"])
    DISCONTINUED_PHYSICIAN_DECISION = PermissibleValue(
        text="DISCONTINUED_PHYSICIAN_DECISION",
        title="Drug Withdrawn",
        description="Stopped by physician decision",
        meaning=NCIT["C49502"])
    DISCONTINUED_PATIENT_DECISION = PermissibleValue(
        text="DISCONTINUED_PATIENT_DECISION",
        title="Consent Withdrawn",
        description="Stopped by patient choice",
        meaning=NCIT["C48271"])
    UNKNOWN_STATUS = PermissibleValue(
        text="UNKNOWN_STATUS",
        title="Unknown",
        description="Treatment status unknown",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="RegimenStatusEnum",
        description="Status of a therapeutic regimen or treatment protocol",
    )

class DrugResponseEnum(EnumDefinitionImpl):
    """
    Response categories for drug treatment outcomes
    """
    FAVORABLE = PermissibleValue(
        text="FAVORABLE",
        title="Favorable Response",
        description="Favorable response to treatment",
        meaning=NCIT["C123584"])
    UNFAVORABLE = PermissibleValue(
        text="UNFAVORABLE",
        description="Unfavorable response to treatment",
        meaning=NCIT["C102561"])
    RESPONSIVE = PermissibleValue(
        text="RESPONSIVE",
        title="Responsive Disease",
        description="Responsive to treatment",
        meaning=NCIT["C165206"])
    RESISTANT = PermissibleValue(
        text="RESISTANT",
        title="Drug Resistance Process",
        description="Resistant to treatment",
        meaning=NCIT["C16523"])
    PARTIALLY_RESPONSIVE = PermissibleValue(
        text="PARTIALLY_RESPONSIVE",
        title="Stable Disease",
        description="Partial response to treatment",
        meaning=NCIT["C18213"])
    UNKNOWN_RESPONSE = PermissibleValue(
        text="UNKNOWN_RESPONSE",
        title="Unknown",
        description="Treatment response unknown",
        meaning=NCIT["C17998"])

    _defn = EnumDefinition(
        name="DrugResponseEnum",
        description="Response categories for drug treatment outcomes",
    )

class ProcessScaleEnum(EnumDefinitionImpl):
    """
    Scale of bioprocessing operations from lab bench to commercial production
    """
    BENCH_SCALE = PermissibleValue(
        text="BENCH_SCALE",
        description="Laboratory bench scale (typically < 10 L)")
    PILOT_SCALE = PermissibleValue(
        text="PILOT_SCALE",
        description="Pilot plant scale (10-1000 L)")
    DEMONSTRATION_SCALE = PermissibleValue(
        text="DEMONSTRATION_SCALE",
        description="Demonstration scale (1000-10000 L)")
    PRODUCTION_SCALE = PermissibleValue(
        text="PRODUCTION_SCALE",
        description="Commercial production scale (>10000 L)")
    MICROFLUIDIC_SCALE = PermissibleValue(
        text="MICROFLUIDIC_SCALE",
        description="Microfluidic scale (<1 mL)")

    _defn = EnumDefinition(
        name="ProcessScaleEnum",
        description="Scale of bioprocessing operations from lab bench to commercial production",
    )

class BioreactorTypeEnum(EnumDefinitionImpl):
    """
    Types of bioreactors used in fermentation and cell culture
    """
    STIRRED_TANK = PermissibleValue(
        text="STIRRED_TANK",
        description="Stirred tank reactor (STR/CSTR)")
    AIRLIFT = PermissibleValue(
        text="AIRLIFT",
        description="Airlift bioreactor")
    BUBBLE_COLUMN = PermissibleValue(
        text="BUBBLE_COLUMN",
        description="Bubble column bioreactor")
    PACKED_BED = PermissibleValue(
        text="PACKED_BED",
        description="Packed bed bioreactor")
    FLUIDIZED_BED = PermissibleValue(
        text="FLUIDIZED_BED",
        description="Fluidized bed bioreactor")
    MEMBRANE = PermissibleValue(
        text="MEMBRANE",
        title="membrane bioreactor",
        description="Membrane bioreactor",
        meaning=ENVO["03600010"])
    WAVE_BAG = PermissibleValue(
        text="WAVE_BAG",
        description="Wave/rocking bioreactor")
    HOLLOW_FIBER = PermissibleValue(
        text="HOLLOW_FIBER",
        description="Hollow fiber bioreactor")
    PHOTOBIOREACTOR = PermissibleValue(
        text="PHOTOBIOREACTOR",
        description="Photobioreactor for photosynthetic organisms")

    _defn = EnumDefinition(
        name="BioreactorTypeEnum",
        description="Types of bioreactors used in fermentation and cell culture",
    )

class FermentationModeEnum(EnumDefinitionImpl):
    """
    Modes of fermentation operation
    """
    BATCH = PermissibleValue(
        text="BATCH",
        title="batch cell culture",
        description="Batch fermentation",
        meaning=MSIO["0000181"])
    FED_BATCH = PermissibleValue(
        text="FED_BATCH",
        description="Fed-batch fermentation")
    CONTINUOUS = PermissibleValue(
        text="CONTINUOUS",
        title="continuous fermentation cell culture",
        description="Continuous fermentation (chemostat)",
        meaning=MSIO["0000155"])
    PERFUSION = PermissibleValue(
        text="PERFUSION",
        description="Perfusion culture")
    REPEATED_BATCH = PermissibleValue(
        text="REPEATED_BATCH",
        description="Repeated batch fermentation")
    SEMI_CONTINUOUS = PermissibleValue(
        text="SEMI_CONTINUOUS",
        description="Semi-continuous operation")

    _defn = EnumDefinition(
        name="FermentationModeEnum",
        description="Modes of fermentation operation",
    )

class OxygenationStrategyEnum(EnumDefinitionImpl):
    """
    Oxygen supply strategies for fermentation
    """
    AEROBIC = PermissibleValue(
        text="AEROBIC",
        description="Aerobic with active aeration")
    ANAEROBIC = PermissibleValue(
        text="ANAEROBIC",
        description="Anaerobic (no oxygen)")
    MICROAEROBIC = PermissibleValue(
        text="MICROAEROBIC",
        description="Microaerobic (limited oxygen)")
    FACULTATIVE = PermissibleValue(
        text="FACULTATIVE",
        description="Facultative (with/without oxygen)")

    _defn = EnumDefinition(
        name="OxygenationStrategyEnum",
        description="Oxygen supply strategies for fermentation",
    )

class AgitationTypeEnum(EnumDefinitionImpl):
    """
    Types of agitation/mixing in bioreactors
    """
    RUSHTON_TURBINE = PermissibleValue(
        text="RUSHTON_TURBINE",
        description="Rushton turbine impeller")
    PITCHED_BLADE = PermissibleValue(
        text="PITCHED_BLADE",
        description="Pitched blade turbine")
    MARINE_PROPELLER = PermissibleValue(
        text="MARINE_PROPELLER",
        description="Marine propeller")
    ANCHOR = PermissibleValue(
        text="ANCHOR",
        description="Anchor impeller")
    HELICAL_RIBBON = PermissibleValue(
        text="HELICAL_RIBBON",
        description="Helical ribbon impeller")
    MAGNETIC_BAR = PermissibleValue(
        text="MAGNETIC_BAR",
        description="Magnetic stir bar")
    ORBITAL_SHAKING = PermissibleValue(
        text="ORBITAL_SHAKING",
        description="Orbital shaking")
    NO_AGITATION = PermissibleValue(
        text="NO_AGITATION",
        description="No mechanical agitation")

    _defn = EnumDefinition(
        name="AgitationTypeEnum",
        description="Types of agitation/mixing in bioreactors",
    )

class DownstreamProcessEnum(EnumDefinitionImpl):
    """
    Downstream processing unit operations
    """
    CENTRIFUGATION = PermissibleValue(
        text="CENTRIFUGATION",
        title="analytical centrifugation",
        description="Centrifugal separation",
        meaning=CHMO["0002010"])
    FILTRATION = PermissibleValue(
        text="FILTRATION",
        description="Filtration (micro/ultra/nano)",
        meaning=CHMO["0001640"])
    CHROMATOGRAPHY = PermissibleValue(
        text="CHROMATOGRAPHY",
        description="Chromatographic separation",
        meaning=CHMO["0001000"])
    EXTRACTION = PermissibleValue(
        text="EXTRACTION",
        description="Liquid-liquid extraction",
        meaning=CHMO["0001577"])
    PRECIPITATION = PermissibleValue(
        text="PRECIPITATION",
        description="Precipitation/crystallization",
        meaning=CHMO["0001688"])
    EVAPORATION = PermissibleValue(
        text="EVAPORATION",
        description="Evaporation/concentration",
        meaning=CHMO["0001574"])
    DISTILLATION = PermissibleValue(
        text="DISTILLATION",
        title="continuous distillation",
        description="Distillation",
        meaning=CHMO["0001534"])
    DRYING = PermissibleValue(
        text="DRYING",
        title="direct drying",
        description="Drying operations",
        meaning=CHMO["0001551"])
    HOMOGENIZATION = PermissibleValue(
        text="HOMOGENIZATION",
        description="Cell disruption/homogenization")

    _defn = EnumDefinition(
        name="DownstreamProcessEnum",
        description="Downstream processing unit operations",
    )

class FeedstockTypeEnum(EnumDefinitionImpl):
    """
    Types of feedstocks for bioprocessing
    """
    GLUCOSE = PermissibleValue(
        text="GLUCOSE",
        description="Glucose/dextrose",
        meaning=CHEBI["17234"])
    SUCROSE = PermissibleValue(
        text="SUCROSE",
        description="Sucrose",
        meaning=CHEBI["17992"])
    GLYCEROL = PermissibleValue(
        text="GLYCEROL",
        description="Glycerol",
        meaning=CHEBI["17754"])
    MOLASSES = PermissibleValue(
        text="MOLASSES",
        description="Molasses",
        meaning=CHEBI["83163"])
    CORN_STEEP_LIQUOR = PermissibleValue(
        text="CORN_STEEP_LIQUOR",
        description="Corn steep liquor")
    YEAST_EXTRACT = PermissibleValue(
        text="YEAST_EXTRACT",
        description="Yeast extract",
        meaning=FOODON["03315426"])
    LIGNOCELLULOSIC = PermissibleValue(
        text="LIGNOCELLULOSIC",
        description="Lignocellulosic biomass")
    METHANOL = PermissibleValue(
        text="METHANOL",
        description="Methanol",
        meaning=CHEBI["17790"])
    WASTE_STREAM = PermissibleValue(
        text="WASTE_STREAM",
        description="Industrial waste stream")

    _defn = EnumDefinition(
        name="FeedstockTypeEnum",
        description="Types of feedstocks for bioprocessing",
    )

class ProductTypeEnum(EnumDefinitionImpl):
    """
    Types of products from bioprocessing
    """
    BIOFUEL = PermissibleValue(
        text="BIOFUEL",
        title="fuel",
        description="Biofuel (ethanol, biodiesel, etc.)",
        meaning=CHEBI["33292"])
    PROTEIN = PermissibleValue(
        text="PROTEIN",
        description="Recombinant protein",
        meaning=NCIT["C17021"])
    ENZYME = PermissibleValue(
        text="ENZYME",
        description="Industrial enzyme",
        meaning=NCIT["C16554"])
    ORGANIC_ACID = PermissibleValue(
        text="ORGANIC_ACID",
        description="Organic acid (citric, lactic, etc.)",
        meaning=CHEBI["64709"])
    AMINO_ACID = PermissibleValue(
        text="AMINO_ACID",
        description="Amino acid",
        meaning=CHEBI["33709"])
    ANTIBIOTIC = PermissibleValue(
        text="ANTIBIOTIC",
        title="antimicrobial agent",
        description="Antibiotic",
        meaning=CHEBI["33281"])
    VITAMIN = PermissibleValue(
        text="VITAMIN",
        title="vitamin (role)",
        description="Vitamin",
        meaning=CHEBI["33229"])
    BIOPOLYMER = PermissibleValue(
        text="BIOPOLYMER",
        title="biomacromolecule",
        description="Biopolymer (PHA, PLA, etc.)",
        meaning=CHEBI["33694"])
    BIOMASS = PermissibleValue(
        text="BIOMASS",
        title="organic material",
        description="Microbial biomass",
        meaning=ENVO["01000155"])
    SECONDARY_METABOLITE = PermissibleValue(
        text="SECONDARY_METABOLITE",
        title="metabolite",
        description="Secondary metabolite",
        meaning=CHEBI["25212"])

    _defn = EnumDefinition(
        name="ProductTypeEnum",
        description="Types of products from bioprocessing",
    )

class SterilizationMethodEnum(EnumDefinitionImpl):
    """
    Methods for sterilization in bioprocessing
    """
    STEAM_IN_PLACE = PermissibleValue(
        text="STEAM_IN_PLACE",
        description="Steam in place (SIP)")
    AUTOCLAVE = PermissibleValue(
        text="AUTOCLAVE",
        title="autoclaving",
        description="Autoclave sterilization",
        meaning=CHMO["0002846"])
    FILTER_STERILIZATION = PermissibleValue(
        text="FILTER_STERILIZATION",
        description="Filter sterilization (0.2 μm)")
    GAMMA_IRRADIATION = PermissibleValue(
        text="GAMMA_IRRADIATION",
        description="Gamma irradiation")
    ETHYLENE_OXIDE = PermissibleValue(
        text="ETHYLENE_OXIDE",
        description="Ethylene oxide sterilization")
    UV_STERILIZATION = PermissibleValue(
        text="UV_STERILIZATION",
        description="UV sterilization")
    CHEMICAL_STERILIZATION = PermissibleValue(
        text="CHEMICAL_STERILIZATION",
        description="Chemical sterilization")

    _defn = EnumDefinition(
        name="SterilizationMethodEnum",
        description="Methods for sterilization in bioprocessing",
    )

class LengthUnitEnum(EnumDefinitionImpl):
    """
    Units of length/distance measurement
    """
    METER = PermissibleValue(
        text="METER",
        title="meter",
        description="Meter (SI base unit)",
        meaning=UO["0000008"])
    KILOMETER = PermissibleValue(
        text="KILOMETER",
        title="kilometer",
        description="Kilometer (1000 meters)",
        meaning=UO["0010066"])
    CENTIMETER = PermissibleValue(
        text="CENTIMETER",
        description="Centimeter (0.01 meter)",
        meaning=UO["0000015"])
    MILLIMETER = PermissibleValue(
        text="MILLIMETER",
        description="Millimeter (0.001 meter)",
        meaning=UO["0000016"])
    MICROMETER = PermissibleValue(
        text="MICROMETER",
        description="Micrometer/micron (10^-6 meter)",
        meaning=UO["0000017"])
    NANOMETER = PermissibleValue(
        text="NANOMETER",
        description="Nanometer (10^-9 meter)",
        meaning=UO["0000018"])
    ANGSTROM = PermissibleValue(
        text="ANGSTROM",
        description="Angstrom (10^-10 meter)",
        meaning=UO["0000019"])
    INCH = PermissibleValue(
        text="INCH",
        title="inch",
        description="Inch (imperial)",
        meaning=UO["0010011"])
    FOOT = PermissibleValue(
        text="FOOT",
        title="foot",
        description="Foot (imperial)",
        meaning=UO["0010013"])
    YARD = PermissibleValue(
        text="YARD",
        title="yard",
        description="Yard (imperial)",
        meaning=UO["0010014"])
    MILE = PermissibleValue(
        text="MILE",
        title="mile",
        description="Mile (imperial)",
        meaning=UO["0010017"])
    NAUTICAL_MILE = PermissibleValue(
        text="NAUTICAL_MILE",
        title="nautical mile",
        description="Nautical mile",
        meaning=UO["0010022"])

    _defn = EnumDefinition(
        name="LengthUnitEnum",
        description="Units of length/distance measurement",
    )

class MassUnitEnum(EnumDefinitionImpl):
    """
    Units of mass measurement
    """
    KILOGRAM = PermissibleValue(
        text="KILOGRAM",
        description="Kilogram (SI base unit)",
        meaning=UO["0000009"])
    GRAM = PermissibleValue(
        text="GRAM",
        description="Gram (0.001 kilogram)",
        meaning=UO["0000021"])
    MILLIGRAM = PermissibleValue(
        text="MILLIGRAM",
        description="Milligram (10^-6 kilogram)",
        meaning=UO["0000022"])
    MICROGRAM = PermissibleValue(
        text="MICROGRAM",
        description="Microgram (10^-9 kilogram)",
        meaning=UO["0000023"])
    NANOGRAM = PermissibleValue(
        text="NANOGRAM",
        description="Nanogram (10^-12 kilogram)",
        meaning=UO["0000024"])
    METRIC_TON = PermissibleValue(
        text="METRIC_TON",
        description="Metric ton/tonne (1000 kilograms)",
        meaning=UO["0010038"])
    POUND = PermissibleValue(
        text="POUND",
        title="pound",
        description="Pound (imperial)",
        meaning=UO["0010034"])
    OUNCE = PermissibleValue(
        text="OUNCE",
        title="ounce",
        description="Ounce (imperial)",
        meaning=UO["0010033"])
    STONE = PermissibleValue(
        text="STONE",
        title="stone",
        description="Stone (imperial)",
        meaning=UO["0010035"])
    DALTON = PermissibleValue(
        text="DALTON",
        description="Dalton/atomic mass unit",
        meaning=UO["0000221"])

    _defn = EnumDefinition(
        name="MassUnitEnum",
        description="Units of mass measurement",
    )

class VolumeUnitEnum(EnumDefinitionImpl):
    """
    Units of volume measurement
    """
    LITER = PermissibleValue(
        text="LITER",
        description="Liter (SI derived)",
        meaning=UO["0000099"])
    MILLILITER = PermissibleValue(
        text="MILLILITER",
        description="Milliliter (0.001 liter)",
        meaning=UO["0000098"])
    MICROLITER = PermissibleValue(
        text="MICROLITER",
        description="Microliter (10^-6 liter)",
        meaning=UO["0000101"])
    CUBIC_METER = PermissibleValue(
        text="CUBIC_METER",
        description="Cubic meter (SI derived)",
        meaning=UO["0000096"])
    CUBIC_CENTIMETER = PermissibleValue(
        text="CUBIC_CENTIMETER",
        description="Cubic centimeter",
        meaning=UO["0000097"])
    GALLON_US = PermissibleValue(
        text="GALLON_US",
        description="US gallon")
    GALLON_UK = PermissibleValue(
        text="GALLON_UK",
        title="gallon",
        description="UK/Imperial gallon",
        meaning=UO["0010030"])
    FLUID_OUNCE_US = PermissibleValue(
        text="FLUID_OUNCE_US",
        title="fluid ounce",
        description="US fluid ounce",
        meaning=UO["0010026"])
    PINT_US = PermissibleValue(
        text="PINT_US",
        title="pint",
        description="US pint",
        meaning=UO["0010028"])
    QUART_US = PermissibleValue(
        text="QUART_US",
        title="quart",
        description="US quart",
        meaning=UO["0010029"])
    CUP_US = PermissibleValue(
        text="CUP_US",
        title="united states customary cup",
        description="US cup",
        meaning=UO["0010046"])
    TABLESPOON = PermissibleValue(
        text="TABLESPOON",
        title="united states customary tablespoon",
        description="Tablespoon",
        meaning=UO["0010044"])
    TEASPOON = PermissibleValue(
        text="TEASPOON",
        title="united states customary teaspoon",
        description="Teaspoon",
        meaning=UO["0010041"])

    _defn = EnumDefinition(
        name="VolumeUnitEnum",
        description="Units of volume measurement",
    )

class TemperatureUnitEnum(EnumDefinitionImpl):
    """
    Units of temperature measurement
    """
    KELVIN = PermissibleValue(
        text="KELVIN",
        description="Kelvin (SI base unit)",
        meaning=UO["0000012"])
    CELSIUS = PermissibleValue(
        text="CELSIUS",
        title="degree Celsius",
        description="Celsius/Centigrade",
        meaning=UO["0000027"])
    FAHRENHEIT = PermissibleValue(
        text="FAHRENHEIT",
        title="degree Fahrenheit",
        description="Fahrenheit",
        meaning=UO["0000195"])
    RANKINE = PermissibleValue(
        text="RANKINE",
        description="Rankine")

    _defn = EnumDefinition(
        name="TemperatureUnitEnum",
        description="Units of temperature measurement",
    )

class TimeUnitEnum(EnumDefinitionImpl):
    """
    Units of time measurement
    """
    SECOND = PermissibleValue(
        text="SECOND",
        description="Second (SI base unit)",
        meaning=UO["0000010"])
    MILLISECOND = PermissibleValue(
        text="MILLISECOND",
        description="Millisecond (0.001 second)",
        meaning=UO["0000028"])
    MICROSECOND = PermissibleValue(
        text="MICROSECOND",
        description="Microsecond (10^-6 second)",
        meaning=UO["0000029"])
    NANOSECOND = PermissibleValue(
        text="NANOSECOND",
        title="nanosecond",
        description="Nanosecond (10^-9 second)",
        meaning=UO["0000150"])
    MINUTE = PermissibleValue(
        text="MINUTE",
        description="Minute (60 seconds)",
        meaning=UO["0000031"])
    HOUR = PermissibleValue(
        text="HOUR",
        description="Hour (3600 seconds)",
        meaning=UO["0000032"])
    DAY = PermissibleValue(
        text="DAY",
        description="Day (86400 seconds)",
        meaning=UO["0000033"])
    WEEK = PermissibleValue(
        text="WEEK",
        description="Week (7 days)",
        meaning=UO["0000034"])
    MONTH = PermissibleValue(
        text="MONTH",
        description="Month (approximately 30 days)",
        meaning=UO["0000035"])
    YEAR = PermissibleValue(
        text="YEAR",
        description="Year (365.25 days)",
        meaning=UO["0000036"])

    _defn = EnumDefinition(
        name="TimeUnitEnum",
        description="Units of time measurement",
    )

class PressureUnitEnum(EnumDefinitionImpl):
    """
    Units of pressure measurement
    """
    PASCAL = PermissibleValue(
        text="PASCAL",
        description="Pascal (SI derived unit)",
        meaning=UO["0000110"])
    KILOPASCAL = PermissibleValue(
        text="KILOPASCAL",
        description="Kilopascal (1000 pascals)")
    MEGAPASCAL = PermissibleValue(
        text="MEGAPASCAL",
        description="Megapascal (10^6 pascals)")
    BAR = PermissibleValue(
        text="BAR",
        description="Bar")
    MILLIBAR = PermissibleValue(
        text="MILLIBAR",
        description="Millibar")
    ATMOSPHERE = PermissibleValue(
        text="ATMOSPHERE",
        description="Standard atmosphere")
    TORR = PermissibleValue(
        text="TORR",
        description="Torr (millimeter of mercury)")
    PSI = PermissibleValue(
        text="PSI",
        title="pounds per square inch",
        description="Pounds per square inch",
        meaning=UO["0010052"])
    MM_HG = PermissibleValue(
        text="MM_HG",
        title="millimetres of mercury",
        description="Millimeters of mercury",
        meaning=UO["0000272"])

    _defn = EnumDefinition(
        name="PressureUnitEnum",
        description="Units of pressure measurement",
    )

class ConcentrationUnitEnum(EnumDefinitionImpl):
    """
    Units of concentration measurement
    """
    MOLAR = PermissibleValue(
        text="MOLAR",
        description="Molar (moles per liter)",
        meaning=UO["0000062"])
    MILLIMOLAR = PermissibleValue(
        text="MILLIMOLAR",
        description="Millimolar (10^-3 molar)",
        meaning=UO["0000063"])
    MICROMOLAR = PermissibleValue(
        text="MICROMOLAR",
        description="Micromolar (10^-6 molar)",
        meaning=UO["0000064"])
    NANOMOLAR = PermissibleValue(
        text="NANOMOLAR",
        description="Nanomolar (10^-9 molar)",
        meaning=UO["0000065"])
    PICOMOLAR = PermissibleValue(
        text="PICOMOLAR",
        description="Picomolar (10^-12 molar)",
        meaning=UO["0000066"])
    MG_PER_ML = PermissibleValue(
        text="MG_PER_ML",
        title="milligram per milliliter",
        description="Milligrams per milliliter",
        meaning=UO["0000176"])
    UG_PER_ML = PermissibleValue(
        text="UG_PER_ML",
        title="microgram per milliliter",
        description="Micrograms per milliliter",
        meaning=UO["0000274"])
    NG_PER_ML = PermissibleValue(
        text="NG_PER_ML",
        title="nanogram per milliliter",
        description="Nanograms per milliliter",
        meaning=UO["0000275"])
    PERCENT = PermissibleValue(
        text="PERCENT",
        description="Percent (parts per hundred)",
        meaning=UO["0000187"])
    PPM = PermissibleValue(
        text="PPM",
        title="parts per million",
        description="Parts per million",
        meaning=UO["0000169"])
    PPB = PermissibleValue(
        text="PPB",
        title="parts per billion",
        description="Parts per billion",
        meaning=UO["0000170"])

    _defn = EnumDefinition(
        name="ConcentrationUnitEnum",
        description="Units of concentration measurement",
    )

class FrequencyUnitEnum(EnumDefinitionImpl):
    """
    Units of frequency measurement
    """
    HERTZ = PermissibleValue(
        text="HERTZ",
        description="Hertz (cycles per second)",
        meaning=UO["0000106"])
    KILOHERTZ = PermissibleValue(
        text="KILOHERTZ",
        description="Kilohertz (1000 Hz)")
    MEGAHERTZ = PermissibleValue(
        text="MEGAHERTZ",
        title="megaHertz",
        description="Megahertz (10^6 Hz)",
        meaning=UO["0000325"])
    GIGAHERTZ = PermissibleValue(
        text="GIGAHERTZ",
        description="Gigahertz (10^9 Hz)")
    RPM = PermissibleValue(
        text="RPM",
        description="Revolutions per minute")
    BPM = PermissibleValue(
        text="BPM",
        description="Beats per minute")

    _defn = EnumDefinition(
        name="FrequencyUnitEnum",
        description="Units of frequency measurement",
    )

class AngleUnitEnum(EnumDefinitionImpl):
    """
    Units of angle measurement
    """
    RADIAN = PermissibleValue(
        text="RADIAN",
        description="Radian (SI derived unit)",
        meaning=UO["0000123"])
    DEGREE = PermissibleValue(
        text="DEGREE",
        description="Degree",
        meaning=UO["0000185"])
    MINUTE_OF_ARC = PermissibleValue(
        text="MINUTE_OF_ARC",
        description="Minute of arc/arcminute")
    SECOND_OF_ARC = PermissibleValue(
        text="SECOND_OF_ARC",
        description="Second of arc/arcsecond")
    GRADIAN = PermissibleValue(
        text="GRADIAN",
        description="Gradian/gon")
    TURN = PermissibleValue(
        text="TURN",
        description="Turn/revolution")

    _defn = EnumDefinition(
        name="AngleUnitEnum",
        description="Units of angle measurement",
    )

class DataSizeUnitEnum(EnumDefinitionImpl):
    """
    Units of digital data size
    """
    BIT = PermissibleValue(
        text="BIT",
        description="Bit (binary digit)")
    BYTE = PermissibleValue(
        text="BYTE",
        description="Byte (8 bits)",
        meaning=UO["0000233"])
    KILOBYTE = PermissibleValue(
        text="KILOBYTE",
        description="Kilobyte (1000 bytes)",
        meaning=UO["0000234"])
    MEGABYTE = PermissibleValue(
        text="MEGABYTE",
        description="Megabyte (10^6 bytes)",
        meaning=UO["0000235"])
    GIGABYTE = PermissibleValue(
        text="GIGABYTE",
        description="Gigabyte (10^9 bytes)")
    TERABYTE = PermissibleValue(
        text="TERABYTE",
        description="Terabyte (10^12 bytes)")
    PETABYTE = PermissibleValue(
        text="PETABYTE",
        description="Petabyte (10^15 bytes)")
    KIBIBYTE = PermissibleValue(
        text="KIBIBYTE",
        description="Kibibyte (1024 bytes)")
    MEBIBYTE = PermissibleValue(
        text="MEBIBYTE",
        description="Mebibyte (2^20 bytes)")
    GIBIBYTE = PermissibleValue(
        text="GIBIBYTE",
        description="Gibibyte (2^30 bytes)")
    TEBIBYTE = PermissibleValue(
        text="TEBIBYTE",
        description="Tebibyte (2^40 bytes)")

    _defn = EnumDefinition(
        name="DataSizeUnitEnum",
        description="Units of digital data size",
    )

class ImageFileFormatEnum(EnumDefinitionImpl):
    """
    Common image file formats
    """
    JPEG = PermissibleValue(
        text="JPEG",
        title="JPEG",
        description="Joint Photographic Experts Group",
        meaning=EDAM["format_3579"])
    PNG = PermissibleValue(
        text="PNG",
        description="Portable Network Graphics",
        meaning=EDAM["format_3603"])
    GIF = PermissibleValue(
        text="GIF",
        description="Graphics Interchange Format",
        meaning=EDAM["format_3467"])
    BMP = PermissibleValue(
        text="BMP",
        description="Bitmap Image File",
        meaning=EDAM["format_3592"])
    TIFF = PermissibleValue(
        text="TIFF",
        description="Tagged Image File Format",
        meaning=EDAM["format_3591"])
    SVG = PermissibleValue(
        text="SVG",
        description="Scalable Vector Graphics",
        meaning=EDAM["format_3604"])
    WEBP = PermissibleValue(
        text="WEBP",
        description="WebP image format")
    HEIC = PermissibleValue(
        text="HEIC",
        description="High Efficiency Image Container")
    RAW = PermissibleValue(
        text="RAW",
        description="Raw image format")
    ICO = PermissibleValue(
        text="ICO",
        description="Icon file format")

    _defn = EnumDefinition(
        name="ImageFileFormatEnum",
        description="Common image file formats",
    )

class DocumentFormatEnum(EnumDefinitionImpl):
    """
    Document and text file formats
    """
    PDF = PermissibleValue(
        text="PDF",
        description="Portable Document Format",
        meaning=EDAM["format_3508"])
    DOCX = PermissibleValue(
        text="DOCX",
        description="Microsoft Word Open XML")
    DOC = PermissibleValue(
        text="DOC",
        description="Microsoft Word legacy format")
    TXT = PermissibleValue(
        text="TXT",
        title="TXT",
        description="Plain text file",
        meaning=EDAM["format_1964"])
    RTF = PermissibleValue(
        text="RTF",
        description="Rich Text Format")
    ODT = PermissibleValue(
        text="ODT",
        description="OpenDocument Text")
    LATEX = PermissibleValue(
        text="LATEX",
        title="LATEX",
        description="LaTeX document",
        meaning=EDAM["format_3817"])
    MARKDOWN = PermissibleValue(
        text="MARKDOWN",
        description="Markdown formatted text")
    HTML = PermissibleValue(
        text="HTML",
        description="HyperText Markup Language",
        meaning=EDAM["format_2331"])
    XML = PermissibleValue(
        text="XML",
        description="Extensible Markup Language",
        meaning=EDAM["format_2332"])
    EPUB = PermissibleValue(
        text="EPUB",
        description="Electronic Publication")

    _defn = EnumDefinition(
        name="DocumentFormatEnum",
        description="Document and text file formats",
    )

class DataFormatEnum(EnumDefinitionImpl):
    """
    Structured data file formats
    """
    JSON = PermissibleValue(
        text="JSON",
        description="JavaScript Object Notation",
        meaning=EDAM["format_3464"])
    CSV = PermissibleValue(
        text="CSV",
        title="CSV",
        description="Comma-Separated Values",
        meaning=EDAM["format_3752"])
    TSV = PermissibleValue(
        text="TSV",
        description="Tab-Separated Values",
        meaning=EDAM["format_3475"])
    YAML = PermissibleValue(
        text="YAML",
        description="YAML Ain't Markup Language",
        meaning=EDAM["format_3750"])
    TOML = PermissibleValue(
        text="TOML",
        description="Tom's Obvious Minimal Language")
    XLSX = PermissibleValue(
        text="XLSX",
        description="Microsoft Excel Open XML")
    XLS = PermissibleValue(
        text="XLS",
        description="Microsoft Excel legacy format")
    ODS = PermissibleValue(
        text="ODS",
        description="OpenDocument Spreadsheet")
    PARQUET = PermissibleValue(
        text="PARQUET",
        description="Apache Parquet columnar format")
    AVRO = PermissibleValue(
        text="AVRO",
        description="Apache Avro data serialization")
    HDF5 = PermissibleValue(
        text="HDF5",
        description="Hierarchical Data Format version 5",
        meaning=EDAM["format_3590"])
    NETCDF = PermissibleValue(
        text="NETCDF",
        description="Network Common Data Form",
        meaning=EDAM["format_3650"])
    SQLITE = PermissibleValue(
        text="SQLITE",
        description="SQLite database")

    _defn = EnumDefinition(
        name="DataFormatEnum",
        description="Structured data file formats",
    )

class ArchiveFormatEnum(EnumDefinitionImpl):
    """
    Archive and compression formats
    """
    ZIP = PermissibleValue(
        text="ZIP",
        description="ZIP archive")
    TAR = PermissibleValue(
        text="TAR",
        description="Tape Archive")
    GZIP = PermissibleValue(
        text="GZIP",
        description="GNU zip")
    TAR_GZ = PermissibleValue(
        text="TAR_GZ",
        description="Gzipped tar archive")
    BZIP2 = PermissibleValue(
        text="BZIP2",
        description="Bzip2 compression")
    TAR_BZ2 = PermissibleValue(
        text="TAR_BZ2",
        description="Bzip2 compressed tar archive")
    XZ = PermissibleValue(
        text="XZ",
        description="XZ compression")
    TAR_XZ = PermissibleValue(
        text="TAR_XZ",
        description="XZ compressed tar archive")
    SEVEN_ZIP = PermissibleValue(
        text="SEVEN_ZIP",
        description="7-Zip archive")
    RAR = PermissibleValue(
        text="RAR",
        description="RAR archive")

    _defn = EnumDefinition(
        name="ArchiveFormatEnum",
        description="Archive and compression formats",
    )

class VideoFormatEnum(EnumDefinitionImpl):
    """
    Video file formats
    """
    MP4 = PermissibleValue(
        text="MP4",
        description="MPEG-4 Part 14")
    AVI = PermissibleValue(
        text="AVI",
        description="Audio Video Interleave")
    MOV = PermissibleValue(
        text="MOV",
        description="QuickTime Movie")
    MKV = PermissibleValue(
        text="MKV",
        description="Matroska Video")
    WEBM = PermissibleValue(
        text="WEBM",
        description="WebM video")
    FLV = PermissibleValue(
        text="FLV",
        description="Flash Video")
    WMV = PermissibleValue(
        text="WMV",
        description="Windows Media Video")
    MPEG = PermissibleValue(
        text="MPEG",
        description="Moving Picture Experts Group")

    _defn = EnumDefinition(
        name="VideoFormatEnum",
        description="Video file formats",
    )

class AudioFormatEnum(EnumDefinitionImpl):
    """
    Audio file formats
    """
    MP3 = PermissibleValue(
        text="MP3",
        description="MPEG Audio Layer 3")
    WAV = PermissibleValue(
        text="WAV",
        description="Waveform Audio File Format")
    FLAC = PermissibleValue(
        text="FLAC",
        description="Free Lossless Audio Codec")
    AAC = PermissibleValue(
        text="AAC",
        description="Advanced Audio Coding")
    OGG = PermissibleValue(
        text="OGG",
        description="Ogg Vorbis")
    M4A = PermissibleValue(
        text="M4A",
        description="MPEG-4 Audio")
    WMA = PermissibleValue(
        text="WMA",
        description="Windows Media Audio")
    OPUS = PermissibleValue(
        text="OPUS",
        description="Opus Interactive Audio Codec")
    AIFF = PermissibleValue(
        text="AIFF",
        description="Audio Interchange File Format")

    _defn = EnumDefinition(
        name="AudioFormatEnum",
        description="Audio file formats",
    )

class ProgrammingLanguageFileEnum(EnumDefinitionImpl):
    """
    Programming language source file extensions
    """
    PYTHON = PermissibleValue(
        text="PYTHON",
        description="Python source file")
    JAVASCRIPT = PermissibleValue(
        text="JAVASCRIPT",
        description="JavaScript source file")
    TYPESCRIPT = PermissibleValue(
        text="TYPESCRIPT",
        description="TypeScript source file")
    JAVA = PermissibleValue(
        text="JAVA",
        description="Java source file")
    C = PermissibleValue(
        text="C",
        description="C source file")
    CPP = PermissibleValue(
        text="CPP",
        description="C++ source file")
    C_SHARP = PermissibleValue(
        text="C_SHARP",
        description="C# source file")
    GO = PermissibleValue(
        text="GO",
        description="Go source file")
    RUST = PermissibleValue(
        text="RUST",
        description="Rust source file")
    RUBY = PermissibleValue(
        text="RUBY",
        description="Ruby source file")
    PHP = PermissibleValue(
        text="PHP",
        description="PHP source file")
    SWIFT = PermissibleValue(
        text="SWIFT",
        description="Swift source file")
    KOTLIN = PermissibleValue(
        text="KOTLIN",
        description="Kotlin source file")
    R = PermissibleValue(
        text="R",
        description="R source file")
    MATLAB = PermissibleValue(
        text="MATLAB",
        description="MATLAB source file")
    JULIA = PermissibleValue(
        text="JULIA",
        description="Julia source file")
    SHELL = PermissibleValue(
        text="SHELL",
        description="Shell script")

    _defn = EnumDefinition(
        name="ProgrammingLanguageFileEnum",
        description="Programming language source file extensions",
    )

class NetworkProtocolEnum(EnumDefinitionImpl):
    """
    Network communication protocols
    """
    HTTP = PermissibleValue(
        text="HTTP",
        description="Hypertext Transfer Protocol")
    HTTPS = PermissibleValue(
        text="HTTPS",
        description="HTTP Secure")
    FTP = PermissibleValue(
        text="FTP",
        description="File Transfer Protocol")
    SFTP = PermissibleValue(
        text="SFTP",
        description="SSH File Transfer Protocol")
    SSH = PermissibleValue(
        text="SSH",
        description="Secure Shell")
    TELNET = PermissibleValue(
        text="TELNET",
        description="Telnet protocol")
    SMTP = PermissibleValue(
        text="SMTP",
        description="Simple Mail Transfer Protocol")
    POP3 = PermissibleValue(
        text="POP3",
        description="Post Office Protocol version 3")
    IMAP = PermissibleValue(
        text="IMAP",
        description="Internet Message Access Protocol")
    DNS = PermissibleValue(
        text="DNS",
        description="Domain Name System")
    DHCP = PermissibleValue(
        text="DHCP",
        description="Dynamic Host Configuration Protocol")
    TCP = PermissibleValue(
        text="TCP",
        description="Transmission Control Protocol")
    UDP = PermissibleValue(
        text="UDP",
        description="User Datagram Protocol")
    WEBSOCKET = PermissibleValue(
        text="WEBSOCKET",
        description="WebSocket protocol")
    MQTT = PermissibleValue(
        text="MQTT",
        description="Message Queuing Telemetry Transport")
    AMQP = PermissibleValue(
        text="AMQP",
        description="Advanced Message Queuing Protocol")
    GRPC = PermissibleValue(
        text="GRPC",
        description="gRPC Remote Procedure Call")

    _defn = EnumDefinition(
        name="NetworkProtocolEnum",
        description="Network communication protocols",
    )

class TechnologyReadinessLevel(EnumDefinitionImpl):
    """
    NASA's Technology Readiness Level scale for assessing the maturity of technologies from basic research through
    operational deployment
    """
    TRL_1 = PermissibleValue(
        text="TRL_1",
        title="TRL 1 - Basic Principles",
        description="Basic principles observed and reported")
    TRL_2 = PermissibleValue(
        text="TRL_2",
        title="TRL 2 - Technology Concept",
        description="Technology concept and/or application formulated")
    TRL_3 = PermissibleValue(
        text="TRL_3",
        title="TRL 3 - Experimental Proof of Concept",
        description="Analytical and experimental critical function and/or characteristic proof of concept")
    TRL_4 = PermissibleValue(
        text="TRL_4",
        title="TRL 4 - Lab Validation",
        description="Component and/or breadboard validation in laboratory environment")
    TRL_5 = PermissibleValue(
        text="TRL_5",
        title="TRL 5 - Relevant Environment Validation",
        description="Component and/or breadboard validation in relevant environment")
    TRL_6 = PermissibleValue(
        text="TRL_6",
        title="TRL 6 - Prototype Demonstration",
        description="System/subsystem model or prototype demonstration in a relevant environment")
    TRL_7 = PermissibleValue(
        text="TRL_7",
        title="TRL 7 - Operational Prototype",
        description="System prototype demonstration in an operational environment")
    TRL_8 = PermissibleValue(
        text="TRL_8",
        title="TRL 8 - System Complete",
        description="Actual system completed and qualified through test and demonstration")
    TRL_9 = PermissibleValue(
        text="TRL_9",
        title="TRL 9 - Mission Proven",
        description="Actual system proven through successful mission operations")

    _defn = EnumDefinition(
        name="TechnologyReadinessLevel",
        description="""NASA's Technology Readiness Level scale for assessing the maturity of technologies from basic research through operational deployment""",
    )

class SoftwareMaturityLevel(EnumDefinitionImpl):
    """
    General software maturity assessment levels
    """
    ALPHA = PermissibleValue(
        text="ALPHA",
        title="Alpha",
        description="Early development stage with basic functionality, may be unstable")
    BETA = PermissibleValue(
        text="BETA",
        title="Beta",
        description="Feature-complete but may contain bugs, ready for testing")
    RELEASE_CANDIDATE = PermissibleValue(
        text="RELEASE_CANDIDATE",
        title="Release Candidate",
        description="Stable version ready for final testing before release")
    STABLE = PermissibleValue(
        text="STABLE",
        title="Stable",
        description="Production-ready with proven stability and reliability")
    MATURE = PermissibleValue(
        text="MATURE",
        title="Mature",
        description="Well-established with extensive usage and proven track record")
    LEGACY = PermissibleValue(
        text="LEGACY",
        title="Legacy",
        description="Older version still in use but no longer actively developed")
    DEPRECATED = PermissibleValue(
        text="DEPRECATED",
        title="Deprecated",
        description="No longer recommended for use, superseded by newer versions")
    OBSOLETE = PermissibleValue(
        text="OBSOLETE",
        title="Obsolete",
        description="No longer supported or maintained")

    _defn = EnumDefinition(
        name="SoftwareMaturityLevel",
        description="General software maturity assessment levels",
    )

class CapabilityMaturityLevel(EnumDefinitionImpl):
    """
    CMMI levels for assessing organizational process maturity in software development
    """
    LEVEL_1 = PermissibleValue(
        text="LEVEL_1",
        title="Level 1 - Initial",
        description="Initial - Processes are unpredictable, poorly controlled, and reactive")
    LEVEL_2 = PermissibleValue(
        text="LEVEL_2",
        title="Level 2 - Managed",
        description="Managed - Processes are characterized for projects and reactive")
    LEVEL_3 = PermissibleValue(
        text="LEVEL_3",
        title="Level 3 - Defined",
        description="Defined - Processes are characterized for the organization and proactive")
    LEVEL_4 = PermissibleValue(
        text="LEVEL_4",
        title="Level 4 - Quantitatively Managed",
        description="Quantitatively Managed - Processes are measured and controlled")
    LEVEL_5 = PermissibleValue(
        text="LEVEL_5",
        title="Level 5 - Optimizing",
        description="Optimizing - Focus on continuous process improvement")

    _defn = EnumDefinition(
        name="CapabilityMaturityLevel",
        description="CMMI levels for assessing organizational process maturity in software development",
    )

class StandardsMaturityLevel(EnumDefinitionImpl):
    """
    Maturity levels for standards and specifications
    """
    DRAFT = PermissibleValue(
        text="DRAFT",
        title="Draft",
        description="Initial draft under development")
    WORKING_DRAFT = PermissibleValue(
        text="WORKING_DRAFT",
        title="Working Draft",
        description="Work in progress by working group")
    COMMITTEE_DRAFT = PermissibleValue(
        text="COMMITTEE_DRAFT",
        title="Committee Draft",
        description="Draft reviewed by committee")
    CANDIDATE_RECOMMENDATION = PermissibleValue(
        text="CANDIDATE_RECOMMENDATION",
        title="Candidate Recommendation",
        description="Mature draft ready for implementation testing")
    PROPOSED_STANDARD = PermissibleValue(
        text="PROPOSED_STANDARD",
        title="Proposed Standard",
        description="Stable specification ready for adoption")
    STANDARD = PermissibleValue(
        text="STANDARD",
        title="Standard",
        description="Approved and published standard")
    MATURE_STANDARD = PermissibleValue(
        text="MATURE_STANDARD",
        title="Mature Standard",
        description="Well-established standard with wide adoption")
    SUPERSEDED = PermissibleValue(
        text="SUPERSEDED",
        title="Superseded",
        description="Replaced by a newer version")
    WITHDRAWN = PermissibleValue(
        text="WITHDRAWN",
        title="Withdrawn",
        description="No longer valid or recommended")

    _defn = EnumDefinition(
        name="StandardsMaturityLevel",
        description="Maturity levels for standards and specifications",
    )

class ProjectMaturityLevel(EnumDefinitionImpl):
    """
    General project development maturity assessment
    """
    CONCEPT = PermissibleValue(
        text="CONCEPT",
        title="Concept",
        description="Initial idea or concept stage")
    PLANNING = PermissibleValue(
        text="PLANNING",
        title="Planning",
        description="Project planning and design phase")
    DEVELOPMENT = PermissibleValue(
        text="DEVELOPMENT",
        title="Development",
        description="Active development in progress")
    TESTING = PermissibleValue(
        text="TESTING",
        title="Testing",
        description="Testing and quality assurance phase")
    PILOT = PermissibleValue(
        text="PILOT",
        title="Pilot",
        description="Limited deployment or pilot testing")
    PRODUCTION = PermissibleValue(
        text="PRODUCTION",
        title="Production",
        description="Full production deployment")
    MAINTENANCE = PermissibleValue(
        text="MAINTENANCE",
        title="Maintenance",
        description="Maintenance and support mode")
    END_OF_LIFE = PermissibleValue(
        text="END_OF_LIFE",
        title="End of Life",
        description="Project reaching end of lifecycle")

    _defn = EnumDefinition(
        name="ProjectMaturityLevel",
        description="General project development maturity assessment",
    )

class DataMaturityLevel(EnumDefinitionImpl):
    """
    Levels of data quality, governance, and organizational maturity
    """
    RAW = PermissibleValue(
        text="RAW",
        title="Raw Data",
        description="Unprocessed, uncleaned data")
    CLEANED = PermissibleValue(
        text="CLEANED",
        title="Cleaned Data",
        description="Basic cleaning and validation applied")
    STANDARDIZED = PermissibleValue(
        text="STANDARDIZED",
        title="Standardized Data",
        description="Conforms to defined standards and formats")
    INTEGRATED = PermissibleValue(
        text="INTEGRATED",
        title="Integrated Data",
        description="Combined with other data sources")
    CURATED = PermissibleValue(
        text="CURATED",
        title="Curated Data",
        description="Expert-reviewed and validated")
    PUBLISHED = PermissibleValue(
        text="PUBLISHED",
        title="Published Data",
        description="Publicly available with proper metadata")
    ARCHIVED = PermissibleValue(
        text="ARCHIVED",
        title="Archived Data",
        description="Long-term preservation with access controls")

    _defn = EnumDefinition(
        name="DataMaturityLevel",
        description="Levels of data quality, governance, and organizational maturity",
    )

class OpenSourceMaturityLevel(EnumDefinitionImpl):
    """
    Maturity assessment for open source projects
    """
    EXPERIMENTAL = PermissibleValue(
        text="EXPERIMENTAL",
        title="Experimental",
        description="Early experimental project")
    EMERGING = PermissibleValue(
        text="EMERGING",
        title="Emerging",
        description="Gaining traction and contributors")
    ESTABLISHED = PermissibleValue(
        text="ESTABLISHED",
        title="Established",
        description="Stable with active community")
    MATURE = PermissibleValue(
        text="MATURE",
        title="Mature",
        description="Well-established with proven governance")
    DECLINING = PermissibleValue(
        text="DECLINING",
        title="Declining",
        description="Decreasing activity and maintenance")
    ARCHIVED = PermissibleValue(
        text="ARCHIVED",
        title="Archived",
        description="No longer actively maintained")

    _defn = EnumDefinition(
        name="OpenSourceMaturityLevel",
        description="Maturity assessment for open source projects",
    )

class LegalEntityTypeEnum(EnumDefinitionImpl):
    """
    Legal entity types for business organizations
    """
    SOLE_PROPRIETORSHIP = PermissibleValue(
        text="SOLE_PROPRIETORSHIP",
        title="Sole Proprietorship",
        description="Business owned and operated by single individual")
    GENERAL_PARTNERSHIP = PermissibleValue(
        text="GENERAL_PARTNERSHIP",
        title="General Partnership",
        description="Business owned by two or more partners sharing responsibilities")
    LIMITED_PARTNERSHIP = PermissibleValue(
        text="LIMITED_PARTNERSHIP",
        title="Limited Partnership (LP)",
        description="Partnership with general and limited partners")
    LIMITED_LIABILITY_PARTNERSHIP = PermissibleValue(
        text="LIMITED_LIABILITY_PARTNERSHIP",
        title="Limited Liability Partnership (LLP)",
        description="Partnership providing liability protection to all partners")
    LIMITED_LIABILITY_COMPANY = PermissibleValue(
        text="LIMITED_LIABILITY_COMPANY",
        title="Limited Liability Company (LLC)",
        description="Hybrid entity combining corporation and partnership features")
    SINGLE_MEMBER_LLC = PermissibleValue(
        text="SINGLE_MEMBER_LLC",
        title="Single Member LLC",
        description="LLC with only one owner/member")
    MULTI_MEMBER_LLC = PermissibleValue(
        text="MULTI_MEMBER_LLC",
        title="Multi-Member LLC",
        description="LLC with multiple owners/members")
    C_CORPORATION = PermissibleValue(
        text="C_CORPORATION",
        title="C Corporation",
        description="Traditional corporation with double taxation")
    S_CORPORATION = PermissibleValue(
        text="S_CORPORATION",
        title="S Corporation",
        description="Corporation electing pass-through taxation")
    B_CORPORATION = PermissibleValue(
        text="B_CORPORATION",
        title="Benefit Corporation (B-Corp)",
        description="Corporation with social and environmental mission")
    PUBLIC_CORPORATION = PermissibleValue(
        text="PUBLIC_CORPORATION",
        title="Public Corporation",
        description="Corporation with publicly traded shares")
    PRIVATE_CORPORATION = PermissibleValue(
        text="PRIVATE_CORPORATION",
        title="Private Corporation",
        description="Corporation with privately held shares")
    NONPROFIT_CORPORATION = PermissibleValue(
        text="NONPROFIT_CORPORATION",
        title="Nonprofit Corporation",
        description="Corporation organized for charitable or public purposes")
    COOPERATIVE = PermissibleValue(
        text="COOPERATIVE",
        title="Cooperative",
        description="Member-owned and democratically controlled organization")
    JOINT_VENTURE = PermissibleValue(
        text="JOINT_VENTURE",
        title="Joint Venture",
        description="Temporary partnership for specific project or purpose")
    HOLDING_COMPANY = PermissibleValue(
        text="HOLDING_COMPANY",
        title="Holding Company",
        description="Company that owns controlling interests in other companies")
    SUBSIDIARY = PermissibleValue(
        text="SUBSIDIARY",
        title="Subsidiary",
        description="Company controlled by another company (parent)")
    FRANCHISE = PermissibleValue(
        text="FRANCHISE",
        title="Franchise",
        description="Business operating under franchisor's brand and system")
    GOVERNMENT_ENTITY = PermissibleValue(
        text="GOVERNMENT_ENTITY",
        title="Government Entity",
        description="Entity owned and operated by government")

    _defn = EnumDefinition(
        name="LegalEntityTypeEnum",
        description="Legal entity types for business organizations",
    )

class OrganizationalStructureEnum(EnumDefinitionImpl):
    """
    Types of organizational hierarchy and reporting structures
    """
    HIERARCHICAL = PermissibleValue(
        text="HIERARCHICAL",
        title="Hierarchical Structure",
        description="Traditional pyramid structure with clear chain of command")
    FLAT = PermissibleValue(
        text="FLAT",
        title="Flat Structure",
        description="Minimal hierarchical levels with broader spans of control")
    MATRIX = PermissibleValue(
        text="MATRIX",
        title="Matrix Structure",
        description="Dual reporting relationships combining functional and project lines")
    FUNCTIONAL = PermissibleValue(
        text="FUNCTIONAL",
        title="Functional Structure",
        description="Organization by business functions or departments")
    DIVISIONAL = PermissibleValue(
        text="DIVISIONAL",
        title="Divisional Structure",
        description="Organization by product lines, markets, or geography")
    NETWORK = PermissibleValue(
        text="NETWORK",
        title="Network Structure",
        description="Flexible structure with interconnected relationships")
    TEAM_BASED = PermissibleValue(
        text="TEAM_BASED",
        title="Team-Based Structure",
        description="Organization around self-managing teams")
    VIRTUAL = PermissibleValue(
        text="VIRTUAL",
        title="Virtual Structure",
        description="Geographically dispersed organization connected by technology")
    HYBRID = PermissibleValue(
        text="HYBRID",
        title="Hybrid Structure",
        description="Combination of multiple organizational structures")

    _defn = EnumDefinition(
        name="OrganizationalStructureEnum",
        description="Types of organizational hierarchy and reporting structures",
    )

class ManagementLevelEnum(EnumDefinitionImpl):
    """
    Hierarchical levels within organizational management structure
    """
    BOARD_OF_DIRECTORS = PermissibleValue(
        text="BOARD_OF_DIRECTORS",
        title="Board of Directors",
        description="Governing body elected by shareholders")
    C_SUITE = PermissibleValue(
        text="C_SUITE",
        title="C-Suite/Chief Officers",
        description="Top executive leadership team")
    SENIOR_EXECUTIVE = PermissibleValue(
        text="SENIOR_EXECUTIVE",
        title="Senior Executive",
        description="Senior leadership below C-suite level")
    VICE_PRESIDENT = PermissibleValue(
        text="VICE_PRESIDENT",
        title="Vice President",
        description="Senior management responsible for major divisions")
    DIRECTOR = PermissibleValue(
        text="DIRECTOR",
        title="Director",
        description="Management responsible for departments or major programs")
    MANAGER = PermissibleValue(
        text="MANAGER",
        title="Manager",
        description="Supervisory role managing teams or operations")
    SUPERVISOR = PermissibleValue(
        text="SUPERVISOR",
        title="Supervisor",
        description="First-line management overseeing frontline employees")
    TEAM_LEAD = PermissibleValue(
        text="TEAM_LEAD",
        title="Team Lead",
        description="Lead role within team without formal management authority")
    SENIOR_INDIVIDUAL_CONTRIBUTOR = PermissibleValue(
        text="SENIOR_INDIVIDUAL_CONTRIBUTOR",
        title="Senior Individual Contributor",
        description="Experienced professional without management responsibilities")
    INDIVIDUAL_CONTRIBUTOR = PermissibleValue(
        text="INDIVIDUAL_CONTRIBUTOR",
        title="Individual Contributor",
        description="Professional or specialist role")
    ENTRY_LEVEL = PermissibleValue(
        text="ENTRY_LEVEL",
        title="Entry Level",
        description="Beginning professional or support roles")

    _defn = EnumDefinition(
        name="ManagementLevelEnum",
        description="Hierarchical levels within organizational management structure",
    )

class CorporateGovernanceRoleEnum(EnumDefinitionImpl):
    """
    Roles within corporate governance structure
    """
    CHAIRMAN_OF_BOARD = PermissibleValue(
        text="CHAIRMAN_OF_BOARD",
        title="Chairman of the Board",
        description="Leader of board of directors")
    LEAD_INDEPENDENT_DIRECTOR = PermissibleValue(
        text="LEAD_INDEPENDENT_DIRECTOR",
        title="Lead Independent Director",
        description="Senior independent director when chairman is not independent")
    INDEPENDENT_DIRECTOR = PermissibleValue(
        text="INDEPENDENT_DIRECTOR",
        title="Independent Director",
        description="Board member independent from company management")
    INSIDE_DIRECTOR = PermissibleValue(
        text="INSIDE_DIRECTOR",
        title="Inside Director",
        description="Board member who is also company employee or has material relationship")
    AUDIT_COMMITTEE_CHAIR = PermissibleValue(
        text="AUDIT_COMMITTEE_CHAIR",
        title="Audit Committee Chair",
        description="Chair of board's audit committee")
    COMPENSATION_COMMITTEE_CHAIR = PermissibleValue(
        text="COMPENSATION_COMMITTEE_CHAIR",
        title="Compensation Committee Chair",
        description="Chair of board's compensation committee")
    NOMINATING_COMMITTEE_CHAIR = PermissibleValue(
        text="NOMINATING_COMMITTEE_CHAIR",
        title="Nominating Committee Chair",
        description="Chair of board's nominating and governance committee")
    CHIEF_EXECUTIVE_OFFICER = PermissibleValue(
        text="CHIEF_EXECUTIVE_OFFICER",
        title="Chief Executive Officer (CEO)",
        description="Highest-ranking executive officer")
    CHIEF_FINANCIAL_OFFICER = PermissibleValue(
        text="CHIEF_FINANCIAL_OFFICER",
        title="Chief Financial Officer (CFO)",
        description="Senior executive responsible for financial management")
    CHIEF_OPERATING_OFFICER = PermissibleValue(
        text="CHIEF_OPERATING_OFFICER",
        title="Chief Operating Officer (COO)",
        description="Senior executive responsible for operations")
    CORPORATE_SECRETARY = PermissibleValue(
        text="CORPORATE_SECRETARY",
        title="Corporate Secretary",
        description="Officer responsible for corporate records and governance compliance")

    _defn = EnumDefinition(
        name="CorporateGovernanceRoleEnum",
        description="Roles within corporate governance structure",
    )

class BusinessOwnershipTypeEnum(EnumDefinitionImpl):
    """
    Types of business ownership structures
    """
    PRIVATE_OWNERSHIP = PermissibleValue(
        text="PRIVATE_OWNERSHIP",
        title="Private Ownership",
        description="Business owned by private individuals or entities")
    PUBLIC_OWNERSHIP = PermissibleValue(
        text="PUBLIC_OWNERSHIP",
        title="Public Ownership",
        description="Business with publicly traded ownership shares")
    FAMILY_OWNERSHIP = PermissibleValue(
        text="FAMILY_OWNERSHIP",
        title="Family Ownership",
        description="Business owned and controlled by family members")
    EMPLOYEE_OWNERSHIP = PermissibleValue(
        text="EMPLOYEE_OWNERSHIP",
        title="Employee Ownership",
        description="Business owned by employees through stock or cooperative structure")
    INSTITUTIONAL_OWNERSHIP = PermissibleValue(
        text="INSTITUTIONAL_OWNERSHIP",
        title="Institutional Ownership",
        description="Business owned by institutional investors")
    GOVERNMENT_OWNERSHIP = PermissibleValue(
        text="GOVERNMENT_OWNERSHIP",
        title="Government Ownership",
        description="Business owned by government entities")
    FOREIGN_OWNERSHIP = PermissibleValue(
        text="FOREIGN_OWNERSHIP",
        title="Foreign Ownership",
        description="Business owned by foreign individuals or entities")
    JOINT_OWNERSHIP = PermissibleValue(
        text="JOINT_OWNERSHIP",
        title="Joint Ownership",
        description="Business owned jointly by multiple parties")

    _defn = EnumDefinition(
        name="BusinessOwnershipTypeEnum",
        description="Types of business ownership structures",
    )

class BusinessSizeClassificationEnum(EnumDefinitionImpl):
    """
    Size classifications for business entities
    """
    MICRO_BUSINESS = PermissibleValue(
        text="MICRO_BUSINESS",
        title="Micro Business",
        description="Very small business with minimal employees and revenue")
    SMALL_BUSINESS = PermissibleValue(
        text="SMALL_BUSINESS",
        title="Small Business",
        description="Small business as defined by SBA standards")
    MEDIUM_BUSINESS = PermissibleValue(
        text="MEDIUM_BUSINESS",
        title="Medium Business",
        description="Mid-sized business between small and large classifications")
    LARGE_BUSINESS = PermissibleValue(
        text="LARGE_BUSINESS",
        title="Large Business",
        description="Major corporation with significant operations")
    MULTINATIONAL_CORPORATION = PermissibleValue(
        text="MULTINATIONAL_CORPORATION",
        title="Multinational Corporation",
        description="Large corporation operating in multiple countries")
    FORTUNE_500 = PermissibleValue(
        text="FORTUNE_500",
        title="Fortune 500 Company",
        description="Among the 500 largest US corporations by revenue")

    _defn = EnumDefinition(
        name="BusinessSizeClassificationEnum",
        description="Size classifications for business entities",
    )

class BusinessLifecycleStageEnum(EnumDefinitionImpl):
    """
    Stages in business development lifecycle
    """
    CONCEPT_STAGE = PermissibleValue(
        text="CONCEPT_STAGE",
        title="Concept Stage",
        description="Initial business idea development and validation")
    STARTUP_STAGE = PermissibleValue(
        text="STARTUP_STAGE",
        title="Startup Stage",
        description="Business launch and early operations")
    GROWTH_STAGE = PermissibleValue(
        text="GROWTH_STAGE",
        title="Growth Stage",
        description="Rapid expansion and scaling operations")
    EXPANSION_STAGE = PermissibleValue(
        text="EXPANSION_STAGE",
        title="Expansion Stage",
        description="Market expansion and diversification")
    MATURITY_STAGE = PermissibleValue(
        text="MATURITY_STAGE",
        title="Maturity Stage",
        description="Stable operations with established market position")
    DECLINE_STAGE = PermissibleValue(
        text="DECLINE_STAGE",
        title="Decline Stage",
        description="Decreasing market relevance or performance")
    TURNAROUND_STAGE = PermissibleValue(
        text="TURNAROUND_STAGE",
        title="Turnaround Stage",
        description="Recovery efforts from decline or crisis")
    EXIT_STAGE = PermissibleValue(
        text="EXIT_STAGE",
        title="Exit Stage",
        description="Business sale, merger, or closure")

    _defn = EnumDefinition(
        name="BusinessLifecycleStageEnum",
        description="Stages in business development lifecycle",
    )

class NAICSSectorEnum(EnumDefinitionImpl):
    """
    NAICS two-digit sector codes (North American Industry Classification System)
    """
    SECTOR_11 = PermissibleValue(
        text="SECTOR_11",
        title="Agriculture, Forestry, Fishing and Hunting",
        description="Establishments engaged in agriculture, forestry, fishing, and hunting")
    SECTOR_21 = PermissibleValue(
        text="SECTOR_21",
        title="Mining, Quarrying, and Oil and Gas Extraction",
        description="Establishments engaged in extracting natural resources")
    SECTOR_22 = PermissibleValue(
        text="SECTOR_22",
        title="Utilities",
        description="Establishments engaged in providing utilities")
    SECTOR_23 = PermissibleValue(
        text="SECTOR_23",
        title="Construction",
        description="Establishments engaged in construction activities")
    SECTOR_31_33 = PermissibleValue(
        text="SECTOR_31_33",
        title="Manufacturing",
        description="Establishments engaged in manufacturing goods")
    SECTOR_42 = PermissibleValue(
        text="SECTOR_42",
        title="Wholesale Trade",
        description="Establishments engaged in wholesale distribution")
    SECTOR_44_45 = PermissibleValue(
        text="SECTOR_44_45",
        title="Retail Trade",
        description="Establishments engaged in retail sales to consumers")
    SECTOR_48_49 = PermissibleValue(
        text="SECTOR_48_49",
        title="Transportation and Warehousing",
        description="Establishments providing transportation and warehousing services")
    SECTOR_51 = PermissibleValue(
        text="SECTOR_51",
        title="Information",
        description="Establishments in information industries")
    SECTOR_52 = PermissibleValue(
        text="SECTOR_52",
        title="Finance and Insurance",
        description="Establishments providing financial services")
    SECTOR_53 = PermissibleValue(
        text="SECTOR_53",
        title="Real Estate and Rental and Leasing",
        description="Establishments engaged in real estate and rental activities")
    SECTOR_54 = PermissibleValue(
        text="SECTOR_54",
        title="Professional, Scientific, and Technical Services",
        description="Establishments providing professional services")
    SECTOR_55 = PermissibleValue(
        text="SECTOR_55",
        title="Management of Companies and Enterprises",
        description="Establishments serving as holding companies or managing enterprises")
    SECTOR_56 = PermissibleValue(
        text="SECTOR_56",
        title="Administrative and Support and Waste Management",
        description="Establishments providing administrative and support services")
    SECTOR_61 = PermissibleValue(
        text="SECTOR_61",
        title="Educational Services",
        description="Establishments providing educational instruction")
    SECTOR_62 = PermissibleValue(
        text="SECTOR_62",
        title="Health Care and Social Assistance",
        description="Establishments providing health care and social assistance")
    SECTOR_71 = PermissibleValue(
        text="SECTOR_71",
        title="Arts, Entertainment, and Recreation",
        description="Establishments in arts, entertainment, and recreation")
    SECTOR_72 = PermissibleValue(
        text="SECTOR_72",
        title="Accommodation and Food Services",
        description="Establishments providing accommodation and food services")
    SECTOR_81 = PermissibleValue(
        text="SECTOR_81",
        title="Other Services (except Public Administration)",
        description="Establishments providing other services")
    SECTOR_92 = PermissibleValue(
        text="SECTOR_92",
        title="Public Administration",
        description="Government establishments")

    _defn = EnumDefinition(
        name="NAICSSectorEnum",
        description="NAICS two-digit sector codes (North American Industry Classification System)",
    )

class EconomicSectorEnum(EnumDefinitionImpl):
    """
    Broad economic sector classifications
    """
    PRIMARY_SECTOR = PermissibleValue(
        text="PRIMARY_SECTOR",
        title="Primary Sector",
        description="Economic activities extracting natural resources")
    SECONDARY_SECTOR = PermissibleValue(
        text="SECONDARY_SECTOR",
        title="Secondary Sector",
        description="Economic activities manufacturing and processing goods")
    TERTIARY_SECTOR = PermissibleValue(
        text="TERTIARY_SECTOR",
        title="Tertiary Sector",
        description="Economic activities providing services")
    QUATERNARY_SECTOR = PermissibleValue(
        text="QUATERNARY_SECTOR",
        title="Quaternary Sector",
        description="Knowledge-based economic activities")
    QUINARY_SECTOR = PermissibleValue(
        text="QUINARY_SECTOR",
        title="Quinary Sector",
        description="High-level decision-making and policy services")

    _defn = EnumDefinition(
        name="EconomicSectorEnum",
        description="Broad economic sector classifications",
    )

class BusinessActivityTypeEnum(EnumDefinitionImpl):
    """
    Types of primary business activities
    """
    PRODUCTION = PermissibleValue(
        text="PRODUCTION",
        title="Production/Manufacturing",
        description="Creating or manufacturing physical goods")
    DISTRIBUTION = PermissibleValue(
        text="DISTRIBUTION",
        title="Distribution/Trade",
        description="Moving goods from producers to consumers")
    SERVICES = PermissibleValue(
        text="SERVICES",
        title="Service Provision",
        description="Providing intangible services to customers")
    TECHNOLOGY = PermissibleValue(
        text="TECHNOLOGY",
        title="Technology/Innovation",
        description="Developing and applying technology solutions")
    FINANCE = PermissibleValue(
        text="FINANCE",
        title="Financial Services",
        description="Providing financial and investment services")
    INFORMATION = PermissibleValue(
        text="INFORMATION",
        title="Information/Media",
        description="Creating, processing, and distributing information")
    EDUCATION = PermissibleValue(
        text="EDUCATION",
        title="Education/Training",
        description="Providing educational and training services")
    HEALTHCARE = PermissibleValue(
        text="HEALTHCARE",
        title="Healthcare/Medical",
        description="Providing health and medical services")
    ENTERTAINMENT = PermissibleValue(
        text="ENTERTAINMENT",
        title="Entertainment/Recreation",
        description="Providing entertainment and recreational services")
    PROFESSIONAL_SERVICES = PermissibleValue(
        text="PROFESSIONAL_SERVICES",
        title="Professional Services",
        description="Providing specialized professional expertise")

    _defn = EnumDefinition(
        name="BusinessActivityTypeEnum",
        description="Types of primary business activities",
    )

class IndustryMaturityEnum(EnumDefinitionImpl):
    """
    Industry lifecycle and maturity stages
    """
    EMERGING = PermissibleValue(
        text="EMERGING",
        title="Emerging Industry",
        description="New industry in early development stage")
    GROWTH = PermissibleValue(
        text="GROWTH",
        title="Growth Industry",
        description="Industry experiencing rapid expansion")
    MATURE = PermissibleValue(
        text="MATURE",
        title="Mature Industry",
        description="Established industry with stable growth")
    DECLINING = PermissibleValue(
        text="DECLINING",
        title="Declining Industry",
        description="Industry experiencing contraction")
    TRANSFORMING = PermissibleValue(
        text="TRANSFORMING",
        title="Transforming Industry",
        description="Industry undergoing fundamental change")

    _defn = EnumDefinition(
        name="IndustryMaturityEnum",
        description="Industry lifecycle and maturity stages",
    )

class MarketStructureEnum(EnumDefinitionImpl):
    """
    Competitive structure of industry markets
    """
    PERFECT_COMPETITION = PermissibleValue(
        text="PERFECT_COMPETITION",
        title="Perfect Competition",
        description="Many small firms with identical products")
    MONOPOLISTIC_COMPETITION = PermissibleValue(
        text="MONOPOLISTIC_COMPETITION",
        title="Monopolistic Competition",
        description="Many firms with differentiated products")
    OLIGOPOLY = PermissibleValue(
        text="OLIGOPOLY",
        title="Oligopoly",
        description="Few large firms dominating the market")
    MONOPOLY = PermissibleValue(
        text="MONOPOLY",
        title="Monopoly",
        description="Single firm controlling the market")
    DUOPOLY = PermissibleValue(
        text="DUOPOLY",
        title="Duopoly",
        description="Two firms dominating the market")

    _defn = EnumDefinition(
        name="MarketStructureEnum",
        description="Competitive structure of industry markets",
    )

class IndustryRegulationLevelEnum(EnumDefinitionImpl):
    """
    Level of government regulation in different industries
    """
    HIGHLY_REGULATED = PermissibleValue(
        text="HIGHLY_REGULATED",
        title="Highly Regulated",
        description="Industries subject to extensive government oversight")
    MODERATELY_REGULATED = PermissibleValue(
        text="MODERATELY_REGULATED",
        title="Moderately Regulated",
        description="Industries with significant but focused regulation")
    LIGHTLY_REGULATED = PermissibleValue(
        text="LIGHTLY_REGULATED",
        title="Lightly Regulated",
        description="Industries with minimal regulatory oversight")
    SELF_REGULATED = PermissibleValue(
        text="SELF_REGULATED",
        title="Self-Regulated",
        description="Industries primarily regulated by industry organizations")
    DEREGULATED = PermissibleValue(
        text="DEREGULATED",
        title="Deregulated",
        description="Industries formerly regulated but now market-based")

    _defn = EnumDefinition(
        name="IndustryRegulationLevelEnum",
        description="Level of government regulation in different industries",
    )

class ManagementMethodologyEnum(EnumDefinitionImpl):
    """
    Management approaches and methodologies
    """
    TRADITIONAL_MANAGEMENT = PermissibleValue(
        text="TRADITIONAL_MANAGEMENT",
        title="Traditional Management",
        description="Hierarchical command-and-control management approach")
    AGILE_MANAGEMENT = PermissibleValue(
        text="AGILE_MANAGEMENT",
        title="Agile Management",
        description="Flexible, iterative management approach")
    LEAN_MANAGEMENT = PermissibleValue(
        text="LEAN_MANAGEMENT",
        title="Lean Management",
        description="Waste elimination and value optimization approach")
    PARTICIPATIVE_MANAGEMENT = PermissibleValue(
        text="PARTICIPATIVE_MANAGEMENT",
        title="Participative Management",
        description="Employee involvement in decision-making")
    MATRIX_MANAGEMENT = PermissibleValue(
        text="MATRIX_MANAGEMENT",
        title="Matrix Management",
        description="Dual reporting relationships and shared authority")
    PROJECT_MANAGEMENT = PermissibleValue(
        text="PROJECT_MANAGEMENT",
        title="Project Management",
        description="Structured approach to managing projects")
    RESULTS_ORIENTED_MANAGEMENT = PermissibleValue(
        text="RESULTS_ORIENTED_MANAGEMENT",
        title="Results-Oriented Management",
        description="Focus on outcomes and performance results")
    SERVANT_LEADERSHIP = PermissibleValue(
        text="SERVANT_LEADERSHIP",
        title="Servant Leadership",
        description="Leader serves and supports team members")
    TRANSFORMATIONAL_MANAGEMENT = PermissibleValue(
        text="TRANSFORMATIONAL_MANAGEMENT",
        title="Transformational Management",
        description="Change-oriented and inspirational management")
    DEMOCRATIC_MANAGEMENT = PermissibleValue(
        text="DEMOCRATIC_MANAGEMENT",
        title="Democratic Management",
        description="Collaborative and consensus-building approach")

    _defn = EnumDefinition(
        name="ManagementMethodologyEnum",
        description="Management approaches and methodologies",
    )

class StrategicFrameworkEnum(EnumDefinitionImpl):
    """
    Strategic planning and analysis frameworks
    """
    SWOT_ANALYSIS = PermissibleValue(
        text="SWOT_ANALYSIS",
        title="SWOT Analysis",
        description="Strengths, Weaknesses, Opportunities, Threats analysis")
    PORTERS_FIVE_FORCES = PermissibleValue(
        text="PORTERS_FIVE_FORCES",
        title="Porter's Five Forces",
        description="Industry competitiveness analysis framework")
    BALANCED_SCORECARD = PermissibleValue(
        text="BALANCED_SCORECARD",
        title="Balanced Scorecard",
        description="Performance measurement from multiple perspectives")
    BLUE_OCEAN_STRATEGY = PermissibleValue(
        text="BLUE_OCEAN_STRATEGY",
        title="Blue Ocean Strategy",
        description="Creating uncontested market space strategy")
    ANSOFF_MATRIX = PermissibleValue(
        text="ANSOFF_MATRIX",
        title="Ansoff Matrix",
        description="Product and market growth strategy framework")
    BCG_MATRIX = PermissibleValue(
        text="BCG_MATRIX",
        title="BCG Matrix",
        description="Portfolio analysis of business units")
    VALUE_CHAIN_ANALYSIS = PermissibleValue(
        text="VALUE_CHAIN_ANALYSIS",
        title="Value Chain Analysis",
        description="Analysis of value-creating activities")
    SCENARIO_PLANNING = PermissibleValue(
        text="SCENARIO_PLANNING",
        title="Scenario Planning",
        description="Multiple future scenario development and planning")
    STRATEGIC_CANVAS = PermissibleValue(
        text="STRATEGIC_CANVAS",
        title="Strategy Canvas",
        description="Visual representation of competitive factors")
    CORE_COMPETENCY_ANALYSIS = PermissibleValue(
        text="CORE_COMPETENCY_ANALYSIS",
        title="Core Competency Analysis",
        description="Identification and development of core competencies")

    _defn = EnumDefinition(
        name="StrategicFrameworkEnum",
        description="Strategic planning and analysis frameworks",
    )

class OperationalModelEnum(EnumDefinitionImpl):
    """
    Business operational models and approaches
    """
    CENTRALIZED_OPERATIONS = PermissibleValue(
        text="CENTRALIZED_OPERATIONS",
        title="Centralized Operations",
        description="Centralized operational control and decision-making")
    DECENTRALIZED_OPERATIONS = PermissibleValue(
        text="DECENTRALIZED_OPERATIONS",
        title="Decentralized Operations",
        description="Distributed operational control and autonomy")
    HYBRID_OPERATIONS = PermissibleValue(
        text="HYBRID_OPERATIONS",
        title="Hybrid Operations",
        description="Combination of centralized and decentralized elements")
    OUTSOURCED_OPERATIONS = PermissibleValue(
        text="OUTSOURCED_OPERATIONS",
        title="Outsourced Operations",
        description="External service provider operational model")
    SHARED_SERVICES = PermissibleValue(
        text="SHARED_SERVICES",
        title="Shared Services",
        description="Centralized services shared across business units")
    NETWORK_OPERATIONS = PermissibleValue(
        text="NETWORK_OPERATIONS",
        title="Network Operations",
        description="Collaborative network of partners and suppliers")
    PLATFORM_OPERATIONS = PermissibleValue(
        text="PLATFORM_OPERATIONS",
        title="Platform Operations",
        description="Platform-based business operational model")
    AGILE_OPERATIONS = PermissibleValue(
        text="AGILE_OPERATIONS",
        title="Agile Operations",
        description="Flexible and responsive operational approach")
    LEAN_OPERATIONS = PermissibleValue(
        text="LEAN_OPERATIONS",
        title="Lean Operations",
        description="Waste elimination and value-focused operations")
    DIGITAL_OPERATIONS = PermissibleValue(
        text="DIGITAL_OPERATIONS",
        title="Digital Operations",
        description="Technology-enabled and digital-first operations")

    _defn = EnumDefinition(
        name="OperationalModelEnum",
        description="Business operational models and approaches",
    )

class PerformanceMeasurementEnum(EnumDefinitionImpl):
    """
    Performance measurement systems and approaches
    """
    KEY_PERFORMANCE_INDICATORS = PermissibleValue(
        text="KEY_PERFORMANCE_INDICATORS",
        title="Key Performance Indicators (KPIs)",
        description="Specific metrics measuring critical performance areas")
    OBJECTIVES_KEY_RESULTS = PermissibleValue(
        text="OBJECTIVES_KEY_RESULTS",
        title="Objectives and Key Results (OKRs)",
        description="Goal-setting framework with measurable outcomes")
    BALANCED_SCORECARD_MEASUREMENT = PermissibleValue(
        text="BALANCED_SCORECARD_MEASUREMENT",
        title="Balanced Scorecard Measurement",
        description="Multi-perspective performance measurement system")
    RETURN_ON_INVESTMENT = PermissibleValue(
        text="RETURN_ON_INVESTMENT",
        title="Return on Investment (ROI)",
        description="Financial return measurement relative to investment")
    ECONOMIC_VALUE_ADDED = PermissibleValue(
        text="ECONOMIC_VALUE_ADDED",
        title="Economic Value Added (EVA)",
        description="Value creation measurement after cost of capital")
    CUSTOMER_SATISFACTION_METRICS = PermissibleValue(
        text="CUSTOMER_SATISFACTION_METRICS",
        title="Customer Satisfaction Metrics",
        description="Customer experience and satisfaction measurement")
    EMPLOYEE_ENGAGEMENT_METRICS = PermissibleValue(
        text="EMPLOYEE_ENGAGEMENT_METRICS",
        title="Employee Engagement Metrics",
        description="Employee satisfaction and engagement measurement")
    OPERATIONAL_EFFICIENCY_METRICS = PermissibleValue(
        text="OPERATIONAL_EFFICIENCY_METRICS",
        title="Operational Efficiency Metrics",
        description="Operational performance and efficiency measurement")
    INNOVATION_METRICS = PermissibleValue(
        text="INNOVATION_METRICS",
        title="Innovation Metrics",
        description="Innovation performance and capability measurement")
    SUSTAINABILITY_METRICS = PermissibleValue(
        text="SUSTAINABILITY_METRICS",
        title="Sustainability Metrics",
        description="Environmental and social sustainability measurement")

    _defn = EnumDefinition(
        name="PerformanceMeasurementEnum",
        description="Performance measurement systems and approaches",
    )

class DecisionMakingStyleEnum(EnumDefinitionImpl):
    """
    Decision-making approaches and styles
    """
    AUTOCRATIC = PermissibleValue(
        text="AUTOCRATIC",
        title="Autocratic Decision Making",
        description="Single decision-maker with full authority")
    DEMOCRATIC = PermissibleValue(
        text="DEMOCRATIC",
        title="Democratic Decision Making",
        description="Group participation in decision-making process")
    CONSULTATIVE = PermissibleValue(
        text="CONSULTATIVE",
        title="Consultative Decision Making",
        description="Leader consults others before deciding")
    CONSENSUS = PermissibleValue(
        text="CONSENSUS",
        title="Consensus Decision Making",
        description="Agreement reached through group discussion")
    DELEGATED = PermissibleValue(
        text="DELEGATED",
        title="Delegated Decision Making",
        description="Decision authority delegated to others")
    DATA_DRIVEN = PermissibleValue(
        text="DATA_DRIVEN",
        title="Data-Driven Decision Making",
        description="Decisions based on data analysis and evidence")
    INTUITIVE = PermissibleValue(
        text="INTUITIVE",
        title="Intuitive Decision Making",
        description="Decisions based on experience and gut feeling")
    COMMITTEE = PermissibleValue(
        text="COMMITTEE",
        title="Committee Decision Making",
        description="Formal group decision-making structure")
    COLLABORATIVE = PermissibleValue(
        text="COLLABORATIVE",
        title="Collaborative Decision Making",
        description="Joint decision-making with shared responsibility")
    CRISIS = PermissibleValue(
        text="CRISIS",
        title="Crisis Decision Making",
        description="Rapid decision-making under crisis conditions")

    _defn = EnumDefinition(
        name="DecisionMakingStyleEnum",
        description="Decision-making approaches and styles",
    )

class LeadershipStyleEnum(EnumDefinitionImpl):
    """
    Leadership approaches and styles
    """
    TRANSFORMATIONAL = PermissibleValue(
        text="TRANSFORMATIONAL",
        title="Transformational Leadership",
        description="Inspirational leadership that motivates change")
    TRANSACTIONAL = PermissibleValue(
        text="TRANSACTIONAL",
        title="Transactional Leadership",
        description="Exchange-based leadership with rewards and consequences")
    SERVANT = PermissibleValue(
        text="SERVANT",
        title="Servant Leadership",
        description="Leader serves followers and facilitates their growth")
    AUTHENTIC = PermissibleValue(
        text="AUTHENTIC",
        title="Authentic Leadership",
        description="Genuine and self-aware leadership approach")
    CHARISMATIC = PermissibleValue(
        text="CHARISMATIC",
        title="Charismatic Leadership",
        description="Inspiring leadership through personal charisma")
    SITUATIONAL = PermissibleValue(
        text="SITUATIONAL",
        title="Situational Leadership",
        description="Adaptive leadership based on situation requirements")
    DEMOCRATIC = PermissibleValue(
        text="DEMOCRATIC",
        title="Democratic Leadership",
        description="Participative leadership with shared decision-making")
    AUTOCRATIC = PermissibleValue(
        text="AUTOCRATIC",
        title="Autocratic Leadership",
        description="Directive leadership with centralized control")
    LAISSEZ_FAIRE = PermissibleValue(
        text="LAISSEZ_FAIRE",
        title="Laissez-Faire Leadership",
        description="Hands-off leadership with minimal interference")
    COACHING = PermissibleValue(
        text="COACHING",
        title="Coaching Leadership",
        description="Development-focused leadership approach")

    _defn = EnumDefinition(
        name="LeadershipStyleEnum",
        description="Leadership approaches and styles",
    )

class BusinessProcessTypeEnum(EnumDefinitionImpl):
    """
    Types of business processes
    """
    CORE_PROCESS = PermissibleValue(
        text="CORE_PROCESS",
        title="Core Business Process",
        description="Primary processes that create customer value")
    SUPPORT_PROCESS = PermissibleValue(
        text="SUPPORT_PROCESS",
        title="Support Process",
        description="Processes that enable core business activities")
    MANAGEMENT_PROCESS = PermissibleValue(
        text="MANAGEMENT_PROCESS",
        title="Management Process",
        description="Processes for planning, controlling, and improving")
    OPERATIONAL_PROCESS = PermissibleValue(
        text="OPERATIONAL_PROCESS",
        title="Operational Process",
        description="Day-to-day operational activities")
    STRATEGIC_PROCESS = PermissibleValue(
        text="STRATEGIC_PROCESS",
        title="Strategic Process",
        description="Long-term planning and strategic activities")
    INNOVATION_PROCESS = PermissibleValue(
        text="INNOVATION_PROCESS",
        title="Innovation Process",
        description="Processes for developing new products or services")
    CUSTOMER_PROCESS = PermissibleValue(
        text="CUSTOMER_PROCESS",
        title="Customer Process",
        description="Processes focused on customer interaction and service")
    FINANCIAL_PROCESS = PermissibleValue(
        text="FINANCIAL_PROCESS",
        title="Financial Process",
        description="Processes related to financial management")

    _defn = EnumDefinition(
        name="BusinessProcessTypeEnum",
        description="Types of business processes",
    )

class QualityStandardEnum(EnumDefinitionImpl):
    """
    Quality management standards and frameworks
    """
    ISO_9001 = PermissibleValue(
        text="ISO_9001",
        title="ISO 9001 Quality Management Systems",
        description="International standard for quality management systems")
    ISO_14001 = PermissibleValue(
        text="ISO_14001",
        title="ISO 14001 Environmental Management",
        description="International standard for environmental management systems")
    ISO_45001 = PermissibleValue(
        text="ISO_45001",
        title="ISO 45001 Occupational Health and Safety",
        description="International standard for occupational health and safety")
    ISO_27001 = PermissibleValue(
        text="ISO_27001",
        title="ISO 27001 Information Security Management",
        description="International standard for information security management")
    TQM = PermissibleValue(
        text="TQM",
        title="Total Quality Management",
        description="Comprehensive quality management philosophy")
    EFQM = PermissibleValue(
        text="EFQM",
        title="European Foundation for Quality Management",
        description="European excellence model for organizational performance")
    MALCOLM_BALDRIGE = PermissibleValue(
        text="MALCOLM_BALDRIGE",
        title="Malcolm Baldrige National Quality Award",
        description="US national quality framework and award")
    SIX_SIGMA = PermissibleValue(
        text="SIX_SIGMA",
        title="Six Sigma Quality Management",
        description="Data-driven quality improvement methodology")
    LEAN_QUALITY = PermissibleValue(
        text="LEAN_QUALITY",
        title="Lean Quality Management",
        description="Waste elimination and value-focused quality approach")
    AS9100 = PermissibleValue(
        text="AS9100",
        title="AS9100 Aerospace Quality Standard",
        description="Quality standard for aerospace industry")
    TS16949 = PermissibleValue(
        text="TS16949",
        title="TS 16949 Automotive Quality Standard",
        description="Quality standard for automotive industry")
    ISO_13485 = PermissibleValue(
        text="ISO_13485",
        title="ISO 13485 Medical Device Quality",
        description="Quality standard for medical device industry")

    _defn = EnumDefinition(
        name="QualityStandardEnum",
        description="Quality management standards and frameworks",
    )

class QualityMethodologyEnum(EnumDefinitionImpl):
    """
    Quality improvement methodologies and approaches
    """
    DMAIC = PermissibleValue(
        text="DMAIC",
        title="DMAIC (Define, Measure, Analyze, Improve, Control)",
        description="Six Sigma problem-solving methodology")
    DMADV = PermissibleValue(
        text="DMADV",
        title="DMADV (Define, Measure, Analyze, Design, Verify)",
        description="Six Sigma design methodology for new processes")
    PDCA = PermissibleValue(
        text="PDCA",
        title="PDCA (Plan, Do, Check, Act)",
        description="Continuous improvement cycle methodology")
    KAIZEN = PermissibleValue(
        text="KAIZEN",
        title="Kaizen Continuous Improvement",
        description="Japanese philosophy of continuous improvement")
    LEAN_SIX_SIGMA = PermissibleValue(
        text="LEAN_SIX_SIGMA",
        title="Lean Six Sigma",
        description="Combined methodology integrating Lean and Six Sigma")
    FIVE_S = PermissibleValue(
        text="FIVE_S",
        title="5S Workplace Organization",
        description="Workplace organization and standardization methodology")
    ROOT_CAUSE_ANALYSIS = PermissibleValue(
        text="ROOT_CAUSE_ANALYSIS",
        title="Root Cause Analysis",
        description="Systematic approach to identifying problem root causes")
    STATISTICAL_PROCESS_CONTROL = PermissibleValue(
        text="STATISTICAL_PROCESS_CONTROL",
        title="Statistical Process Control (SPC)",
        description="Statistical methods for process monitoring and control")
    FAILURE_MODE_ANALYSIS = PermissibleValue(
        text="FAILURE_MODE_ANALYSIS",
        title="Failure Mode and Effects Analysis (FMEA)",
        description="Systematic analysis of potential failure modes")
    BENCHMARKING = PermissibleValue(
        text="BENCHMARKING",
        title="Benchmarking",
        description="Performance comparison with best practices")

    _defn = EnumDefinition(
        name="QualityMethodologyEnum",
        description="Quality improvement methodologies and approaches",
    )

class QualityControlTechniqueEnum(EnumDefinitionImpl):
    """
    Quality control techniques and tools
    """
    CONTROL_CHARTS = PermissibleValue(
        text="CONTROL_CHARTS",
        title="Control Charts",
        description="Statistical charts for monitoring process variation")
    PARETO_ANALYSIS = PermissibleValue(
        text="PARETO_ANALYSIS",
        title="Pareto Analysis",
        description="80/20 rule analysis for problem prioritization")
    FISHBONE_DIAGRAM = PermissibleValue(
        text="FISHBONE_DIAGRAM",
        title="Fishbone Diagram (Ishikawa)",
        description="Cause-and-effect analysis diagram")
    HISTOGRAM = PermissibleValue(
        text="HISTOGRAM",
        title="Histogram",
        description="Frequency distribution chart for data analysis")
    SCATTER_DIAGRAM = PermissibleValue(
        text="SCATTER_DIAGRAM",
        title="Scatter Diagram",
        description="Correlation analysis between two variables")
    CHECK_SHEET = PermissibleValue(
        text="CHECK_SHEET",
        title="Check Sheet",
        description="Data collection and recording tool")
    FLOW_CHART = PermissibleValue(
        text="FLOW_CHART",
        title="Flow Chart",
        description="Process flow visualization and analysis")
    DESIGN_OF_EXPERIMENTS = PermissibleValue(
        text="DESIGN_OF_EXPERIMENTS",
        title="Design of Experiments (DOE)",
        description="Statistical method for process optimization")
    SAMPLING_PLANS = PermissibleValue(
        text="SAMPLING_PLANS",
        title="Statistical Sampling Plans",
        description="Systematic approach to quality sampling")
    GAUGE_R_AND_R = PermissibleValue(
        text="GAUGE_R_AND_R",
        title="Gauge R&R (Repeatability and Reproducibility)",
        description="Measurement system analysis technique")

    _defn = EnumDefinition(
        name="QualityControlTechniqueEnum",
        description="Quality control techniques and tools",
    )

class QualityAssuranceLevelEnum(EnumDefinitionImpl):
    """
    Levels of quality assurance implementation
    """
    BASIC_QA = PermissibleValue(
        text="BASIC_QA",
        title="Basic Quality Assurance",
        description="Fundamental quality assurance practices")
    INTERMEDIATE_QA = PermissibleValue(
        text="INTERMEDIATE_QA",
        title="Intermediate Quality Assurance",
        description="Systematic quality assurance with documented processes")
    ADVANCED_QA = PermissibleValue(
        text="ADVANCED_QA",
        title="Advanced Quality Assurance",
        description="Comprehensive quality management system")
    WORLD_CLASS_QA = PermissibleValue(
        text="WORLD_CLASS_QA",
        title="World-Class Quality Assurance",
        description="Excellence-oriented quality management")
    TOTAL_QUALITY = PermissibleValue(
        text="TOTAL_QUALITY",
        title="Total Quality Management",
        description="Organization-wide quality culture and commitment")

    _defn = EnumDefinition(
        name="QualityAssuranceLevelEnum",
        description="Levels of quality assurance implementation",
    )

class ProcessImprovementApproachEnum(EnumDefinitionImpl):
    """
    Process improvement methodologies and approaches
    """
    BUSINESS_PROCESS_REENGINEERING = PermissibleValue(
        text="BUSINESS_PROCESS_REENGINEERING",
        title="Business Process Reengineering (BPR)",
        description="Radical redesign of business processes")
    CONTINUOUS_IMPROVEMENT = PermissibleValue(
        text="CONTINUOUS_IMPROVEMENT",
        title="Continuous Improvement",
        description="Ongoing incremental process improvement")
    PROCESS_STANDARDIZATION = PermissibleValue(
        text="PROCESS_STANDARDIZATION",
        title="Process Standardization",
        description="Establishing consistent process standards")
    AUTOMATION = PermissibleValue(
        text="AUTOMATION",
        title="Process Automation",
        description="Technology-driven process automation")
    DIGITALIZATION = PermissibleValue(
        text="DIGITALIZATION",
        title="Digital Process Transformation",
        description="Digital technology-enabled process transformation")
    OUTSOURCING = PermissibleValue(
        text="OUTSOURCING",
        title="Process Outsourcing",
        description="External provider process management")
    SHARED_SERVICES = PermissibleValue(
        text="SHARED_SERVICES",
        title="Shared Services Model",
        description="Centralized shared process delivery")
    AGILE_PROCESS_IMPROVEMENT = PermissibleValue(
        text="AGILE_PROCESS_IMPROVEMENT",
        title="Agile Process Improvement",
        description="Flexible and iterative process improvement")

    _defn = EnumDefinition(
        name="ProcessImprovementApproachEnum",
        description="Process improvement methodologies and approaches",
    )

class QualityMaturityLevelEnum(EnumDefinitionImpl):
    """
    Organizational quality maturity levels
    """
    AD_HOC = PermissibleValue(
        text="AD_HOC",
        title="Ad Hoc Quality Approach",
        description="Informal and unstructured quality practices")
    DEFINED = PermissibleValue(
        text="DEFINED",
        title="Defined Quality Processes",
        description="Documented and standardized quality processes")
    MANAGED = PermissibleValue(
        text="MANAGED",
        title="Managed Quality System",
        description="Measured and controlled quality management")
    OPTIMIZED = PermissibleValue(
        text="OPTIMIZED",
        title="Optimized Quality Performance",
        description="Continuously improving quality excellence")
    WORLD_CLASS = PermissibleValue(
        text="WORLD_CLASS",
        title="World-Class Quality Leadership",
        description="Industry-leading quality performance and innovation")

    _defn = EnumDefinition(
        name="QualityMaturityLevelEnum",
        description="Organizational quality maturity levels",
    )

class ProcurementTypeEnum(EnumDefinitionImpl):
    """
    Types of procurement activities and approaches
    """
    DIRECT_PROCUREMENT = PermissibleValue(
        text="DIRECT_PROCUREMENT",
        title="Direct Procurement",
        description="Procurement of materials directly used in production")
    INDIRECT_PROCUREMENT = PermissibleValue(
        text="INDIRECT_PROCUREMENT",
        title="Indirect Procurement",
        description="Procurement of goods and services supporting operations")
    SERVICES_PROCUREMENT = PermissibleValue(
        text="SERVICES_PROCUREMENT",
        title="Services Procurement",
        description="Procurement of professional and business services")
    CAPITAL_PROCUREMENT = PermissibleValue(
        text="CAPITAL_PROCUREMENT",
        title="Capital Procurement",
        description="Procurement of capital equipment and assets")
    STRATEGIC_PROCUREMENT = PermissibleValue(
        text="STRATEGIC_PROCUREMENT",
        title="Strategic Procurement",
        description="Procurement of strategically important items")
    TACTICAL_PROCUREMENT = PermissibleValue(
        text="TACTICAL_PROCUREMENT",
        title="Tactical Procurement",
        description="Routine procurement of standard items")
    EMERGENCY_PROCUREMENT = PermissibleValue(
        text="EMERGENCY_PROCUREMENT",
        title="Emergency Procurement",
        description="Urgent procurement due to immediate needs")
    FRAMEWORK_PROCUREMENT = PermissibleValue(
        text="FRAMEWORK_PROCUREMENT",
        title="Framework Procurement",
        description="Pre-negotiated procurement agreements")
    E_PROCUREMENT = PermissibleValue(
        text="E_PROCUREMENT",
        title="Electronic Procurement",
        description="Technology-enabled procurement processes")
    SUSTAINABLE_PROCUREMENT = PermissibleValue(
        text="SUSTAINABLE_PROCUREMENT",
        title="Sustainable Procurement",
        description="Environmentally and socially responsible procurement")

    _defn = EnumDefinition(
        name="ProcurementTypeEnum",
        description="Types of procurement activities and approaches",
    )

class VendorCategoryEnum(EnumDefinitionImpl):
    """
    Vendor classification categories
    """
    STRATEGIC_SUPPLIER = PermissibleValue(
        text="STRATEGIC_SUPPLIER",
        title="Strategic Supplier",
        description="Critical suppliers with strategic importance")
    PREFERRED_SUPPLIER = PermissibleValue(
        text="PREFERRED_SUPPLIER",
        title="Preferred Supplier",
        description="Suppliers with proven performance and preferred status")
    APPROVED_SUPPLIER = PermissibleValue(
        text="APPROVED_SUPPLIER",
        title="Approved Supplier",
        description="Suppliers meeting qualification requirements")
    TRANSACTIONAL_SUPPLIER = PermissibleValue(
        text="TRANSACTIONAL_SUPPLIER",
        title="Transactional Supplier",
        description="Suppliers for routine, low-risk purchases")
    SINGLE_SOURCE = PermissibleValue(
        text="SINGLE_SOURCE",
        title="Single Source Supplier",
        description="Only available supplier for specific requirement")
    SOLE_SOURCE = PermissibleValue(
        text="SOLE_SOURCE",
        title="Sole Source Supplier",
        description="Deliberately chosen single supplier")
    MINORITY_SUPPLIER = PermissibleValue(
        text="MINORITY_SUPPLIER",
        title="Minority/Diverse Supplier",
        description="Suppliers meeting diversity criteria")
    LOCAL_SUPPLIER = PermissibleValue(
        text="LOCAL_SUPPLIER",
        title="Local Supplier",
        description="Geographically local suppliers")
    GLOBAL_SUPPLIER = PermissibleValue(
        text="GLOBAL_SUPPLIER",
        title="Global Supplier",
        description="Suppliers with global capabilities")
    SPOT_SUPPLIER = PermissibleValue(
        text="SPOT_SUPPLIER",
        title="Spot Market Supplier",
        description="Suppliers for one-time or spot purchases")

    _defn = EnumDefinition(
        name="VendorCategoryEnum",
        description="Vendor classification categories",
    )

class SupplyChainStrategyEnum(EnumDefinitionImpl):
    """
    Supply chain strategic approaches
    """
    LEAN_SUPPLY_CHAIN = PermissibleValue(
        text="LEAN_SUPPLY_CHAIN",
        title="Lean Supply Chain",
        description="Waste elimination and efficiency-focused supply chain")
    AGILE_SUPPLY_CHAIN = PermissibleValue(
        text="AGILE_SUPPLY_CHAIN",
        title="Agile Supply Chain",
        description="Flexible and responsive supply chain")
    RESILIENT_SUPPLY_CHAIN = PermissibleValue(
        text="RESILIENT_SUPPLY_CHAIN",
        title="Resilient Supply Chain",
        description="Risk-resistant and robust supply chain")
    SUSTAINABLE_SUPPLY_CHAIN = PermissibleValue(
        text="SUSTAINABLE_SUPPLY_CHAIN",
        title="Sustainable Supply Chain",
        description="Environmentally and socially responsible supply chain")
    GLOBAL_SUPPLY_CHAIN = PermissibleValue(
        text="GLOBAL_SUPPLY_CHAIN",
        title="Global Supply Chain",
        description="Internationally distributed supply chain")
    LOCAL_SUPPLY_CHAIN = PermissibleValue(
        text="LOCAL_SUPPLY_CHAIN",
        title="Local/Regional Supply Chain",
        description="Geographically concentrated supply chain")
    DIGITAL_SUPPLY_CHAIN = PermissibleValue(
        text="DIGITAL_SUPPLY_CHAIN",
        title="Digital Supply Chain",
        description="Technology-enabled and data-driven supply chain")
    COLLABORATIVE_SUPPLY_CHAIN = PermissibleValue(
        text="COLLABORATIVE_SUPPLY_CHAIN",
        title="Collaborative Supply Chain",
        description="Partnership-based collaborative supply chain")
    COST_FOCUSED_SUPPLY_CHAIN = PermissibleValue(
        text="COST_FOCUSED_SUPPLY_CHAIN",
        title="Cost-Focused Supply Chain",
        description="Cost optimization-focused supply chain")
    CUSTOMER_FOCUSED_SUPPLY_CHAIN = PermissibleValue(
        text="CUSTOMER_FOCUSED_SUPPLY_CHAIN",
        title="Customer-Focused Supply Chain",
        description="Customer service-oriented supply chain")

    _defn = EnumDefinition(
        name="SupplyChainStrategyEnum",
        description="Supply chain strategic approaches",
    )

class LogisticsOperationEnum(EnumDefinitionImpl):
    """
    Types of logistics operations
    """
    INBOUND_LOGISTICS = PermissibleValue(
        text="INBOUND_LOGISTICS",
        title="Inbound Logistics",
        description="Management of incoming materials and supplies")
    OUTBOUND_LOGISTICS = PermissibleValue(
        text="OUTBOUND_LOGISTICS",
        title="Outbound Logistics",
        description="Management of finished goods distribution")
    REVERSE_LOGISTICS = PermissibleValue(
        text="REVERSE_LOGISTICS",
        title="Reverse Logistics",
        description="Management of product returns and recycling")
    THIRD_PARTY_LOGISTICS = PermissibleValue(
        text="THIRD_PARTY_LOGISTICS",
        title="Third-Party Logistics (3PL)",
        description="Outsourced logistics services")
    FOURTH_PARTY_LOGISTICS = PermissibleValue(
        text="FOURTH_PARTY_LOGISTICS",
        title="Fourth-Party Logistics (4PL)",
        description="Supply chain integration and management services")
    WAREHOUSING = PermissibleValue(
        text="WAREHOUSING",
        title="Warehousing Operations",
        description="Storage and inventory management operations")
    TRANSPORTATION = PermissibleValue(
        text="TRANSPORTATION",
        title="Transportation Management",
        description="Movement of goods between locations")
    CROSS_DOCKING = PermissibleValue(
        text="CROSS_DOCKING",
        title="Cross-Docking Operations",
        description="Direct transfer without storage")
    DISTRIBUTION = PermissibleValue(
        text="DISTRIBUTION",
        title="Distribution Management",
        description="Product distribution and delivery operations")
    FREIGHT_FORWARDING = PermissibleValue(
        text="FREIGHT_FORWARDING",
        title="Freight Forwarding",
        description="International shipping and customs management")

    _defn = EnumDefinition(
        name="LogisticsOperationEnum",
        description="Types of logistics operations",
    )

class SourcingStrategyEnum(EnumDefinitionImpl):
    """
    Sourcing strategy approaches
    """
    SINGLE_SOURCING = PermissibleValue(
        text="SINGLE_SOURCING",
        title="Single Sourcing",
        description="Deliberate use of one supplier for strategic reasons")
    MULTIPLE_SOURCING = PermissibleValue(
        text="MULTIPLE_SOURCING",
        title="Multiple Sourcing",
        description="Use of multiple suppliers for risk mitigation")
    DUAL_SOURCING = PermissibleValue(
        text="DUAL_SOURCING",
        title="Dual Sourcing",
        description="Use of two suppliers for balance of risk and efficiency")
    GLOBAL_SOURCING = PermissibleValue(
        text="GLOBAL_SOURCING",
        title="Global Sourcing",
        description="Worldwide sourcing for best value")
    DOMESTIC_SOURCING = PermissibleValue(
        text="DOMESTIC_SOURCING",
        title="Domestic Sourcing",
        description="Sourcing within domestic market")
    NEAR_SOURCING = PermissibleValue(
        text="NEAR_SOURCING",
        title="Near Sourcing",
        description="Sourcing from nearby geographic regions")
    VERTICAL_INTEGRATION = PermissibleValue(
        text="VERTICAL_INTEGRATION",
        title="Vertical Integration",
        description="Internal production instead of external sourcing")
    OUTSOURCING = PermissibleValue(
        text="OUTSOURCING",
        title="Outsourcing",
        description="External sourcing of non-core activities")
    INSOURCING = PermissibleValue(
        text="INSOURCING",
        title="Insourcing",
        description="Bringing previously outsourced activities internal")
    CONSORTIUM_SOURCING = PermissibleValue(
        text="CONSORTIUM_SOURCING",
        title="Consortium Sourcing",
        description="Collaborative sourcing with other organizations")

    _defn = EnumDefinition(
        name="SourcingStrategyEnum",
        description="Sourcing strategy approaches",
    )

class SupplierRelationshipTypeEnum(EnumDefinitionImpl):
    """
    Types of supplier relationship management
    """
    TRANSACTIONAL = PermissibleValue(
        text="TRANSACTIONAL",
        title="Transactional Relationship",
        description="Arms-length, price-focused supplier relationship")
    PREFERRED_SUPPLIER = PermissibleValue(
        text="PREFERRED_SUPPLIER",
        title="Preferred Supplier Relationship",
        description="Ongoing relationship with proven suppliers")
    STRATEGIC_PARTNERSHIP = PermissibleValue(
        text="STRATEGIC_PARTNERSHIP",
        title="Strategic Partnership",
        description="Collaborative long-term strategic relationship")
    ALLIANCE = PermissibleValue(
        text="ALLIANCE",
        title="Strategic Alliance",
        description="Formal alliance with shared objectives")
    JOINT_VENTURE = PermissibleValue(
        text="JOINT_VENTURE",
        title="Joint Venture",
        description="Separate entity created with supplier")
    VENDOR_MANAGED_INVENTORY = PermissibleValue(
        text="VENDOR_MANAGED_INVENTORY",
        title="Vendor Managed Inventory (VMI)",
        description="Supplier manages customer inventory")
    CONSIGNMENT = PermissibleValue(
        text="CONSIGNMENT",
        title="Consignment Relationship",
        description="Supplier owns inventory until consumption")
    COLLABORATIVE_PLANNING = PermissibleValue(
        text="COLLABORATIVE_PLANNING",
        title="Collaborative Planning Relationship",
        description="Joint planning and forecasting relationship")
    DEVELOPMENT_PARTNERSHIP = PermissibleValue(
        text="DEVELOPMENT_PARTNERSHIP",
        title="Supplier Development Partnership",
        description="Investment in supplier capability development")
    RISK_SHARING = PermissibleValue(
        text="RISK_SHARING",
        title="Risk Sharing Partnership",
        description="Shared risk and reward relationship")

    _defn = EnumDefinition(
        name="SupplierRelationshipTypeEnum",
        description="Types of supplier relationship management",
    )

class InventoryManagementApproachEnum(EnumDefinitionImpl):
    """
    Inventory management methodologies
    """
    JUST_IN_TIME = PermissibleValue(
        text="JUST_IN_TIME",
        title="Just-in-Time (JIT)",
        description="Minimal inventory with precise timing")
    ECONOMIC_ORDER_QUANTITY = PermissibleValue(
        text="ECONOMIC_ORDER_QUANTITY",
        title="Economic Order Quantity (EOQ)",
        description="Optimal order quantity calculation")
    ABC_ANALYSIS = PermissibleValue(
        text="ABC_ANALYSIS",
        title="ABC Analysis",
        description="Inventory classification by value importance")
    SAFETY_STOCK = PermissibleValue(
        text="SAFETY_STOCK",
        title="Safety Stock Management",
        description="Buffer inventory for demand/supply uncertainty")
    VENDOR_MANAGED_INVENTORY = PermissibleValue(
        text="VENDOR_MANAGED_INVENTORY",
        title="Vendor Managed Inventory (VMI)",
        description="Supplier-controlled inventory management")
    CONSIGNMENT_INVENTORY = PermissibleValue(
        text="CONSIGNMENT_INVENTORY",
        title="Consignment Inventory",
        description="Supplier-owned inventory at customer location")
    KANBAN = PermissibleValue(
        text="KANBAN",
        title="Kanban System",
        description="Visual pull-based inventory system")
    TWO_BIN_SYSTEM = PermissibleValue(
        text="TWO_BIN_SYSTEM",
        title="Two-Bin System",
        description="Simple reorder point system using two bins")
    CONTINUOUS_REVIEW = PermissibleValue(
        text="CONTINUOUS_REVIEW",
        title="Continuous Review System",
        description="Continuous monitoring with fixed reorder point")
    PERIODIC_REVIEW = PermissibleValue(
        text="PERIODIC_REVIEW",
        title="Periodic Review System",
        description="Periodic inventory review with variable order quantity")

    _defn = EnumDefinition(
        name="InventoryManagementApproachEnum",
        description="Inventory management methodologies",
    )

class EmploymentTypeEnum(EnumDefinitionImpl):
    """
    Types of employment arrangements and contracts
    """
    FULL_TIME = PermissibleValue(
        text="FULL_TIME",
        title="Full-Time Employment",
        description="Regular full-time employment status")
    PART_TIME = PermissibleValue(
        text="PART_TIME",
        title="Part-Time Employment",
        description="Regular part-time employment status")
    CONTRACT = PermissibleValue(
        text="CONTRACT",
        title="Contract Employment",
        description="Fixed-term contractual employment")
    TEMPORARY = PermissibleValue(
        text="TEMPORARY",
        title="Temporary Employment",
        description="Short-term temporary employment")
    FREELANCE = PermissibleValue(
        text="FREELANCE",
        title="Freelance/Independent Contractor",
        description="Independent contractor or freelance work")
    INTERN = PermissibleValue(
        text="INTERN",
        title="Internship",
        description="Student or entry-level internship program")
    SEASONAL = PermissibleValue(
        text="SEASONAL",
        title="Seasonal Employment",
        description="Employment tied to seasonal business needs")
    CONSULTANT = PermissibleValue(
        text="CONSULTANT",
        title="Consultant",
        description="Professional consulting services")
    VOLUNTEER = PermissibleValue(
        text="VOLUNTEER",
        title="Volunteer",
        description="Unpaid volunteer service")

    _defn = EnumDefinition(
        name="EmploymentTypeEnum",
        description="Types of employment arrangements and contracts",
    )

class JobLevelEnum(EnumDefinitionImpl):
    """
    Organizational job levels and career progression
    """
    ENTRY_LEVEL = PermissibleValue(
        text="ENTRY_LEVEL",
        title="Entry Level",
        description="Beginning career level positions")
    JUNIOR = PermissibleValue(
        text="JUNIOR",
        title="Junior Level",
        description="Junior professional level")
    MID_LEVEL = PermissibleValue(
        text="MID_LEVEL",
        title="Mid-Level",
        description="Experienced professional level")
    SENIOR = PermissibleValue(
        text="SENIOR",
        title="Senior Level",
        description="Senior professional level")
    LEAD = PermissibleValue(
        text="LEAD",
        title="Team Lead",
        description="Team leadership role")
    MANAGER = PermissibleValue(
        text="MANAGER",
        title="Manager",
        description="Management level position")
    DIRECTOR = PermissibleValue(
        text="DIRECTOR",
        title="Director",
        description="Director level executive")
    VP = PermissibleValue(
        text="VP",
        title="Vice President",
        description="Vice President executive level")
    C_LEVEL = PermissibleValue(
        text="C_LEVEL",
        title="C-Level Executive",
        description="Chief executive level")

    _defn = EnumDefinition(
        name="JobLevelEnum",
        description="Organizational job levels and career progression",
    )

class HRFunctionEnum(EnumDefinitionImpl):
    """
    Human resources functional areas and specializations
    """
    TALENT_ACQUISITION = PermissibleValue(
        text="TALENT_ACQUISITION",
        title="Talent Acquisition",
        description="Recruitment and hiring functions")
    EMPLOYEE_RELATIONS = PermissibleValue(
        text="EMPLOYEE_RELATIONS",
        title="Employee Relations",
        description="Managing employee relationships and workplace issues")
    COMPENSATION_BENEFITS = PermissibleValue(
        text="COMPENSATION_BENEFITS",
        title="Compensation and Benefits",
        description="Managing compensation and benefits programs")
    PERFORMANCE_MANAGEMENT = PermissibleValue(
        text="PERFORMANCE_MANAGEMENT",
        title="Performance Management",
        description="Employee performance evaluation and improvement")
    LEARNING_DEVELOPMENT = PermissibleValue(
        text="LEARNING_DEVELOPMENT",
        title="Learning and Development",
        description="Employee training and development programs")
    HR_ANALYTICS = PermissibleValue(
        text="HR_ANALYTICS",
        title="HR Analytics",
        description="HR data analysis and workforce metrics")
    ORGANIZATIONAL_DEVELOPMENT = PermissibleValue(
        text="ORGANIZATIONAL_DEVELOPMENT",
        title="Organizational Development",
        description="Organizational design and change management")
    HR_COMPLIANCE = PermissibleValue(
        text="HR_COMPLIANCE",
        title="HR Compliance",
        description="Employment law compliance and risk management")
    HRIS_TECHNOLOGY = PermissibleValue(
        text="HRIS_TECHNOLOGY",
        title="HRIS and Technology",
        description="HR information systems and technology")

    _defn = EnumDefinition(
        name="HRFunctionEnum",
        description="Human resources functional areas and specializations",
    )

class CompensationTypeEnum(EnumDefinitionImpl):
    """
    Types of employee compensation structures
    """
    BASE_SALARY = PermissibleValue(
        text="BASE_SALARY",
        title="Base Salary",
        description="Fixed annual salary compensation")
    HOURLY_WAGE = PermissibleValue(
        text="HOURLY_WAGE",
        title="Hourly Wage",
        description="Compensation paid per hour worked")
    COMMISSION = PermissibleValue(
        text="COMMISSION",
        title="Commission",
        description="Performance-based sales commission")
    BONUS = PermissibleValue(
        text="BONUS",
        title="Performance Bonus",
        description="Additional compensation for performance")
    STOCK_OPTIONS = PermissibleValue(
        text="STOCK_OPTIONS",
        title="Stock Options",
        description="Equity compensation through stock options")
    PROFIT_SHARING = PermissibleValue(
        text="PROFIT_SHARING",
        title="Profit Sharing",
        description="Sharing of company profits with employees")
    PIECE_RATE = PermissibleValue(
        text="PIECE_RATE",
        title="Piece Rate",
        description="Compensation based on units produced")
    STIPEND = PermissibleValue(
        text="STIPEND",
        title="Stipend",
        description="Fixed regular allowance or payment")

    _defn = EnumDefinition(
        name="CompensationTypeEnum",
        description="Types of employee compensation structures",
    )

class PerformanceRatingEnum(EnumDefinitionImpl):
    """
    Employee performance evaluation ratings
    """
    EXCEEDS_EXPECTATIONS = PermissibleValue(
        text="EXCEEDS_EXPECTATIONS",
        title="Exceeds Expectations",
        description="Performance significantly above expected standards")
    MEETS_EXPECTATIONS = PermissibleValue(
        text="MEETS_EXPECTATIONS",
        title="Meets Expectations",
        description="Performance meets all expected standards")
    PARTIALLY_MEETS = PermissibleValue(
        text="PARTIALLY_MEETS",
        title="Partially Meets Expectations",
        description="Performance meets some but not all standards")
    DOES_NOT_MEET = PermissibleValue(
        text="DOES_NOT_MEET",
        title="Does Not Meet Expectations",
        description="Performance below acceptable standards")
    OUTSTANDING = PermissibleValue(
        text="OUTSTANDING",
        title="Outstanding",
        description="Exceptional performance far exceeding standards")

    _defn = EnumDefinition(
        name="PerformanceRatingEnum",
        description="Employee performance evaluation ratings",
    )

class RecruitmentSourceEnum(EnumDefinitionImpl):
    """
    Sources for candidate recruitment and sourcing
    """
    INTERNAL_REFERRAL = PermissibleValue(
        text="INTERNAL_REFERRAL",
        title="Internal Employee Referral",
        description="Candidates referred by current employees")
    JOB_BOARDS = PermissibleValue(
        text="JOB_BOARDS",
        title="Online Job Boards",
        description="Candidates from online job posting sites")
    COMPANY_WEBSITE = PermissibleValue(
        text="COMPANY_WEBSITE",
        title="Company Career Website",
        description="Candidates applying through company website")
    SOCIAL_MEDIA = PermissibleValue(
        text="SOCIAL_MEDIA",
        title="Social Media Recruiting",
        description="Candidates sourced through social media platforms")
    RECRUITMENT_AGENCIES = PermissibleValue(
        text="RECRUITMENT_AGENCIES",
        title="External Recruitment Agencies",
        description="Candidates sourced through recruitment firms")
    CAMPUS_RECRUITING = PermissibleValue(
        text="CAMPUS_RECRUITING",
        title="Campus and University Recruiting",
        description="Recruitment from educational institutions")
    PROFESSIONAL_NETWORKS = PermissibleValue(
        text="PROFESSIONAL_NETWORKS",
        title="Professional Networks",
        description="Recruitment through professional associations")
    HEADHUNTERS = PermissibleValue(
        text="HEADHUNTERS",
        title="Executive Search/Headhunters",
        description="Executive-level recruitment specialists")

    _defn = EnumDefinition(
        name="RecruitmentSourceEnum",
        description="Sources for candidate recruitment and sourcing",
    )

class TrainingTypeEnum(EnumDefinitionImpl):
    """
    Types of employee training and development programs
    """
    ONBOARDING = PermissibleValue(
        text="ONBOARDING",
        title="New Employee Onboarding",
        description="Orientation and integration training for new hires")
    TECHNICAL_SKILLS = PermissibleValue(
        text="TECHNICAL_SKILLS",
        title="Technical Skills Training",
        description="Job-specific technical competency development")
    LEADERSHIP_DEVELOPMENT = PermissibleValue(
        text="LEADERSHIP_DEVELOPMENT",
        title="Leadership Development",
        description="Management and leadership capability building")
    COMPLIANCE_TRAINING = PermissibleValue(
        text="COMPLIANCE_TRAINING",
        title="Compliance Training",
        description="Required training for regulatory compliance")
    SOFT_SKILLS = PermissibleValue(
        text="SOFT_SKILLS",
        title="Soft Skills Development",
        description="Communication and interpersonal skills training")
    SAFETY_TRAINING = PermissibleValue(
        text="SAFETY_TRAINING",
        title="Safety Training",
        description="Workplace safety and health training")
    DIVERSITY_INCLUSION = PermissibleValue(
        text="DIVERSITY_INCLUSION",
        title="Diversity and Inclusion Training",
        description="Training on diversity, equity, and inclusion")
    CROSS_TRAINING = PermissibleValue(
        text="CROSS_TRAINING",
        title="Cross-Training",
        description="Training in multiple roles or departments")

    _defn = EnumDefinition(
        name="TrainingTypeEnum",
        description="Types of employee training and development programs",
    )

class EmployeeStatusEnum(EnumDefinitionImpl):
    """
    Current employment status classifications
    """
    ACTIVE = PermissibleValue(
        text="ACTIVE",
        title="Active Employment",
        description="Currently employed and working")
    ON_LEAVE = PermissibleValue(
        text="ON_LEAVE",
        title="On Leave",
        description="Temporarily away from work on approved leave")
    PROBATIONARY = PermissibleValue(
        text="PROBATIONARY",
        title="Probationary Period",
        description="New employee in probationary period")
    SUSPENDED = PermissibleValue(
        text="SUSPENDED",
        title="Suspended",
        description="Temporarily suspended from work")
    TERMINATED = PermissibleValue(
        text="TERMINATED",
        title="Terminated",
        description="Employment has been terminated")
    RETIRED = PermissibleValue(
        text="RETIRED",
        title="Retired",
        description="Retired from employment")

    _defn = EnumDefinition(
        name="EmployeeStatusEnum",
        description="Current employment status classifications",
    )

class WorkArrangementEnum(EnumDefinitionImpl):
    """
    Work location and arrangement types
    """
    ON_SITE = PermissibleValue(
        text="ON_SITE",
        title="On-Site Work",
        description="Work performed at company facilities")
    REMOTE = PermissibleValue(
        text="REMOTE",
        title="Remote Work",
        description="Work performed away from company facilities")
    HYBRID = PermissibleValue(
        text="HYBRID",
        title="Hybrid Work",
        description="Combination of on-site and remote work")
    FIELD_WORK = PermissibleValue(
        text="FIELD_WORK",
        title="Field Work",
        description="Work performed at client or field locations")
    TELECOMMUTE = PermissibleValue(
        text="TELECOMMUTE",
        title="Telecommuting",
        description="Regular remote work arrangement")

    _defn = EnumDefinition(
        name="WorkArrangementEnum",
        description="Work location and arrangement types",
    )

class BenefitsCategoryEnum(EnumDefinitionImpl):
    """
    Categories of employee benefits and compensation
    """
    HEALTH_INSURANCE = PermissibleValue(
        text="HEALTH_INSURANCE",
        title="Health Insurance",
        description="Medical, dental, and vision insurance coverage")
    RETIREMENT_BENEFITS = PermissibleValue(
        text="RETIREMENT_BENEFITS",
        title="Retirement Benefits",
        description="Retirement savings and pension plans")
    PAID_TIME_OFF = PermissibleValue(
        text="PAID_TIME_OFF",
        title="Paid Time Off",
        description="Vacation, sick leave, and personal time")
    LIFE_INSURANCE = PermissibleValue(
        text="LIFE_INSURANCE",
        title="Life Insurance",
        description="Life and disability insurance coverage")
    FLEXIBLE_BENEFITS = PermissibleValue(
        text="FLEXIBLE_BENEFITS",
        title="Flexible Benefits",
        description="Flexible spending and benefit choice options")
    WELLNESS_PROGRAMS = PermissibleValue(
        text="WELLNESS_PROGRAMS",
        title="Wellness Programs",
        description="Employee health and wellness initiatives")
    PROFESSIONAL_DEVELOPMENT = PermissibleValue(
        text="PROFESSIONAL_DEVELOPMENT",
        title="Professional Development",
        description="Training, education, and career development benefits")
    WORK_LIFE_BALANCE = PermissibleValue(
        text="WORK_LIFE_BALANCE",
        title="Work-Life Balance Benefits",
        description="Benefits supporting work-life integration")

    _defn = EnumDefinition(
        name="BenefitsCategoryEnum",
        description="Categories of employee benefits and compensation",
    )

class MassSpectrometerFileFormat(EnumDefinitionImpl):
    """
    Standard file formats used in mass spectrometry
    """
    MZML = PermissibleValue(
        text="MZML",
        title="mzML format",
        description="mzML format - PSI standard for mass spectrometry data",
        meaning=MS["1000584"])
    MZXML = PermissibleValue(
        text="MZXML",
        title="ISB mzXML format",
        description="ISB mzXML format",
        meaning=MS["1000566"])
    MGF = PermissibleValue(
        text="MGF",
        title="Mascot MGF format",
        description="Mascot Generic Format",
        meaning=MS["1001062"])
    THERMO_RAW = PermissibleValue(
        text="THERMO_RAW",
        title="Thermo RAW format",
        description="Thermo RAW format",
        meaning=MS["1000563"])
    WATERS_RAW = PermissibleValue(
        text="WATERS_RAW",
        title="Waters raw format",
        description="Waters raw format",
        meaning=MS["1000526"])
    WIFF = PermissibleValue(
        text="WIFF",
        title="ABI WIFF format",
        description="ABI WIFF format",
        meaning=MS["1000562"])
    MZDATA = PermissibleValue(
        text="MZDATA",
        title="PSI mzData format",
        description="PSI mzData format",
        meaning=MS["1000564"])
    PKL = PermissibleValue(
        text="PKL",
        title="Micromass PKL format",
        description="Micromass PKL format",
        meaning=MS["1000565"])
    DTA = PermissibleValue(
        text="DTA",
        title="DTA format",
        description="DTA format",
        meaning=MS["1000613"])
    MS2 = PermissibleValue(
        text="MS2",
        title="MS2 format",
        description="MS2 format",
        meaning=MS["1001466"])
    BRUKER_BAF = PermissibleValue(
        text="BRUKER_BAF",
        title="Bruker BAF format",
        description="Bruker BAF format",
        meaning=MS["1000815"])
    BRUKER_TDF = PermissibleValue(
        text="BRUKER_TDF",
        title="Bruker TDF format",
        description="Bruker TDF format",
        meaning=MS["1002817"])
    BRUKER_TSF = PermissibleValue(
        text="BRUKER_TSF",
        title="Bruker TSF format",
        description="Bruker TSF format",
        meaning=MS["1003282"])
    MZ5 = PermissibleValue(
        text="MZ5",
        title="mz5 format",
        description="mz5 format",
        meaning=MS["1001881"])
    MZMLB = PermissibleValue(
        text="MZMLB",
        title="mzMLb format",
        description="mzMLb format",
        meaning=MS["1002838"])
    UIMF = PermissibleValue(
        text="UIMF",
        title="UIMF format",
        description="UIMF format",
        meaning=MS["1002531"])

    _defn = EnumDefinition(
        name="MassSpectrometerFileFormat",
        description="Standard file formats used in mass spectrometry",
    )

class MassSpectrometerVendor(EnumDefinitionImpl):
    """
    Major mass spectrometer manufacturers
    """
    THERMO_FISHER_SCIENTIFIC = PermissibleValue(
        text="THERMO_FISHER_SCIENTIFIC",
        title="Thermo Fisher Scientific instrument model",
        description="Thermo Fisher Scientific",
        meaning=MS["1000483"])
    WATERS = PermissibleValue(
        text="WATERS",
        title="Waters instrument model",
        description="Waters Corporation",
        meaning=MS["1000126"])
    BRUKER_DALTONICS = PermissibleValue(
        text="BRUKER_DALTONICS",
        title="Bruker Daltonics instrument model",
        description="Bruker Daltonics",
        meaning=MS["1000122"])
    SCIEX = PermissibleValue(
        text="SCIEX",
        title="SCIEX instrument model",
        description="SCIEX (formerly Applied Biosystems)",
        meaning=MS["1000121"])
    AGILENT = PermissibleValue(
        text="AGILENT",
        title="Agilent instrument model",
        description="Agilent Technologies",
        meaning=MS["1000490"])
    SHIMADZU = PermissibleValue(
        text="SHIMADZU",
        title="Shimadzu instrument model",
        description="Shimadzu Corporation",
        meaning=MS["1000124"])
    LECO = PermissibleValue(
        text="LECO",
        title="LECO instrument model",
        description="LECO Corporation",
        meaning=MS["1001800"])

    _defn = EnumDefinition(
        name="MassSpectrometerVendor",
        description="Major mass spectrometer manufacturers",
    )

class ChromatographyType(EnumDefinitionImpl):
    """
    Types of chromatographic separation methods
    """
    GAS_CHROMATOGRAPHY = PermissibleValue(
        text="GAS_CHROMATOGRAPHY",
        description="Gas chromatography",
        meaning=MSIO["0000147"])
    HIGH_PERFORMANCE_LIQUID_CHROMATOGRAPHY = PermissibleValue(
        text="HIGH_PERFORMANCE_LIQUID_CHROMATOGRAPHY",
        description="High performance liquid chromatography",
        meaning=MSIO["0000148"])
    LIQUID_CHROMATOGRAPHY_MASS_SPECTROMETRY = PermissibleValue(
        text="LIQUID_CHROMATOGRAPHY_MASS_SPECTROMETRY",
        description="Liquid chromatography-mass spectrometry",
        meaning=CHMO["0000524"])
    GAS_CHROMATOGRAPHY_MASS_SPECTROMETRY = PermissibleValue(
        text="GAS_CHROMATOGRAPHY_MASS_SPECTROMETRY",
        description="Gas chromatography-mass spectrometry",
        meaning=CHMO["0000497"])
    TANDEM_MASS_SPECTROMETRY = PermissibleValue(
        text="TANDEM_MASS_SPECTROMETRY",
        description="Tandem mass spectrometry",
        meaning=CHMO["0000575"])
    ISOTOPE_RATIO_MASS_SPECTROMETRY = PermissibleValue(
        text="ISOTOPE_RATIO_MASS_SPECTROMETRY",
        description="Isotope ratio mass spectrometry",
        meaning=CHMO["0000506"])

    _defn = EnumDefinition(
        name="ChromatographyType",
        description="Types of chromatographic separation methods",
    )

class DerivatizationMethod(EnumDefinitionImpl):
    """
    Chemical derivatization methods for sample preparation
    """
    SILYLATION = PermissibleValue(
        text="SILYLATION",
        description="Addition of silyl groups for improved volatility",
        meaning=MSIO["0000117"])
    METHYLATION = PermissibleValue(
        text="METHYLATION",
        description="Addition of methyl groups",
        meaning=MSIO["0000115"])
    ACETYLATION = PermissibleValue(
        text="ACETYLATION",
        description="Addition of acetyl groups",
        meaning=MSIO["0000112"])
    TRIFLUOROACETYLATION = PermissibleValue(
        text="TRIFLUOROACETYLATION",
        description="Addition of trifluoroacetyl groups",
        meaning=MSIO["0000113"])
    ALKYLATION = PermissibleValue(
        text="ALKYLATION",
        description="Addition of alkyl groups",
        meaning=MSIO["0000114"])
    OXIMATION = PermissibleValue(
        text="OXIMATION",
        description="Addition of oxime groups",
        meaning=MSIO["0000116"])

    _defn = EnumDefinition(
        name="DerivatizationMethod",
        description="Chemical derivatization methods for sample preparation",
    )

class MetabolomicsAssayType(EnumDefinitionImpl):
    """
    Types of metabolomics assays and profiling approaches
    """
    TARGETED_METABOLITE_PROFILING = PermissibleValue(
        text="TARGETED_METABOLITE_PROFILING",
        title="targeted metabolite profiling",
        description="Assay targeting specific known metabolites",
        meaning=MSIO["0000100"])
    UNTARGETED_METABOLITE_PROFILING = PermissibleValue(
        text="UNTARGETED_METABOLITE_PROFILING",
        title="untargeted metabolite profiling",
        description="Assay profiling all detectable metabolites",
        meaning=MSIO["0000101"])
    METABOLITE_QUANTITATION_HPLC = PermissibleValue(
        text="METABOLITE_QUANTITATION_HPLC",
        title="metabolite quantitation using high performance liquid chromatography",
        description="Metabolite quantitation using HPLC",
        meaning=MSIO["0000099"])

    _defn = EnumDefinition(
        name="MetabolomicsAssayType",
        description="Types of metabolomics assays and profiling approaches",
    )

class AnalyticalControlType(EnumDefinitionImpl):
    """
    Types of control samples used in analytical chemistry
    """
    INTERNAL_STANDARD = PermissibleValue(
        text="INTERNAL_STANDARD",
        title="internal standard role",
        description="Known amount of standard added to analytical sample",
        meaning=MSIO["0000005"])
    EXTERNAL_STANDARD = PermissibleValue(
        text="EXTERNAL_STANDARD",
        title="external standard role",
        description="Reference standard used as external reference point",
        meaning=MSIO["0000004"])
    POSITIVE_CONTROL = PermissibleValue(
        text="POSITIVE_CONTROL",
        title="positive control role",
        description="Control providing known positive signal",
        meaning=MSIO["0000008"])
    NEGATIVE_CONTROL = PermissibleValue(
        text="NEGATIVE_CONTROL",
        title="negative control role",
        description="Control providing baseline/no signal reference",
        meaning=MSIO["0000007"])
    LONG_TERM_REFERENCE = PermissibleValue(
        text="LONG_TERM_REFERENCE",
        title="long term reference role",
        description="Stable reference for cross-batch comparisons",
        meaning=MSIO["0000006"])
    BLANK = PermissibleValue(
        text="BLANK",
        description="Sample containing only solvent/matrix without analyte")
    QUALITY_CONTROL = PermissibleValue(
        text="QUALITY_CONTROL",
        description="Sample with known composition for system performance monitoring")

    _defn = EnumDefinition(
        name="AnalyticalControlType",
        description="Types of control samples used in analytical chemistry",
    )

# Slots
class slots:
    pass

slots.relative_time = Slot(uri=VALUESETS.relative_time, name="relative_time", curie=VALUESETS.curie('relative_time'),
                   model_uri=VALUESETS.relative_time, domain=None, range=Optional[Union[str, "RelativeTimeEnum"]])

slots.presence = Slot(uri=VALUESETS.presence, name="presence", curie=VALUESETS.curie('presence'),
                   model_uri=VALUESETS.presence, domain=None, range=Optional[Union[str, "PresenceEnum"]])

slots.contributor = Slot(uri=VALUESETS.contributor, name="contributor", curie=VALUESETS.curie('contributor'),
                   model_uri=VALUESETS.contributor, domain=None, range=Optional[Union[str, "ContributorType"]])

slots.data_absent = Slot(uri=VALUESETS.data_absent, name="data_absent", curie=VALUESETS.curie('data_absent'),
                   model_uri=VALUESETS.data_absent, domain=None, range=Optional[Union[str, "DataAbsentEnum"]])

slots.prediction_outcome = Slot(uri=VALUESETS.prediction_outcome, name="prediction_outcome", curie=VALUESETS.curie('prediction_outcome'),
                   model_uri=VALUESETS.prediction_outcome, domain=None, range=Optional[Union[str, "PredictionOutcomeType"]])

slots.vital_status = Slot(uri=VALUESETS.vital_status, name="vital_status", curie=VALUESETS.curie('vital_status'),
                   model_uri=VALUESETS.vital_status, domain=None, range=Optional[Union[str, "VitalStatusEnum"]])

slots.vaccination_status = Slot(uri=VALUESETS.vaccination_status, name="vaccination_status", curie=VALUESETS.curie('vaccination_status'),
                   model_uri=VALUESETS.vaccination_status, domain=None, range=Optional[Union[str, "VaccinationStatusEnum"]])

slots.vaccination_periodicity = Slot(uri=VALUESETS.vaccination_periodicity, name="vaccination_periodicity", curie=VALUESETS.curie('vaccination_periodicity'),
                   model_uri=VALUESETS.vaccination_periodicity, domain=None, range=Optional[Union[str, "VaccinationPeriodicityEnum"]])

slots.vaccine_category = Slot(uri=VALUESETS.vaccine_category, name="vaccine_category", curie=VALUESETS.curie('vaccine_category'),
                   model_uri=VALUESETS.vaccine_category, domain=None, range=Optional[Union[str, "VaccineCategoryEnum"]])

slots.healthcare_encounter_classification = Slot(uri=VALUESETS.healthcare_encounter_classification, name="healthcare_encounter_classification", curie=VALUESETS.curie('healthcare_encounter_classification'),
                   model_uri=VALUESETS.healthcare_encounter_classification, domain=None, range=Optional[Union[str, "HealthcareEncounterClassification"]])

slots.education_level = Slot(uri=VALUESETS.education_level, name="education_level", curie=VALUESETS.curie('education_level'),
                   model_uri=VALUESETS.education_level, domain=None, range=Optional[Union[str, "EducationLevel"]])

slots.marital_status = Slot(uri=VALUESETS.marital_status, name="marital_status", curie=VALUESETS.curie('marital_status'),
                   model_uri=VALUESETS.marital_status, domain=None, range=Optional[Union[str, "MaritalStatus"]])

slots.employment_status = Slot(uri=VALUESETS.employment_status, name="employment_status", curie=VALUESETS.curie('employment_status'),
                   model_uri=VALUESETS.employment_status, domain=None, range=Optional[Union[str, "EmploymentStatus"]])

slots.housing_status = Slot(uri=VALUESETS.housing_status, name="housing_status", curie=VALUESETS.curie('housing_status'),
                   model_uri=VALUESETS.housing_status, domain=None, range=Optional[Union[str, "HousingStatus"]])

slots.gender_identity = Slot(uri=VALUESETS.gender_identity, name="gender_identity", curie=VALUESETS.curie('gender_identity'),
                   model_uri=VALUESETS.gender_identity, domain=None, range=Optional[Union[str, "GenderIdentity"]])

slots.omb_race_category = Slot(uri=VALUESETS.omb_race_category, name="omb_race_category", curie=VALUESETS.curie('omb_race_category'),
                   model_uri=VALUESETS.omb_race_category, domain=None, range=Optional[Union[str, "OmbRaceCategory"]])

slots.omb_ethnicity_category = Slot(uri=VALUESETS.omb_ethnicity_category, name="omb_ethnicity_category", curie=VALUESETS.curie('omb_ethnicity_category'),
                   model_uri=VALUESETS.omb_ethnicity_category, domain=None, range=Optional[Union[str, "OmbEthnicityCategory"]])

slots.case_or_control = Slot(uri=VALUESETS.case_or_control, name="case_or_control", curie=VALUESETS.curie('case_or_control'),
                   model_uri=VALUESETS.case_or_control, domain=None, range=Optional[Union[str, "CaseOrControlEnum"]])

slots.study_design = Slot(uri=VALUESETS.study_design, name="study_design", curie=VALUESETS.curie('study_design'),
                   model_uri=VALUESETS.study_design, domain=None, range=Optional[Union[str, "StudyDesignEnum"]])

slots.investigative_protocol = Slot(uri=VALUESETS.investigative_protocol, name="investigative_protocol", curie=VALUESETS.curie('investigative_protocol'),
                   model_uri=VALUESETS.investigative_protocol, domain=None, range=Optional[Union[str, "InvestigativeProtocolEnum"]])

slots.sample_processing = Slot(uri=VALUESETS.sample_processing, name="sample_processing", curie=VALUESETS.curie('sample_processing'),
                   model_uri=VALUESETS.sample_processing, domain=None, range=Optional[Union[str, "SampleProcessingEnum"]])

slots.go_evidence = Slot(uri=VALUESETS.go_evidence, name="go_evidence", curie=VALUESETS.curie('go_evidence'),
                   model_uri=VALUESETS.go_evidence, domain=None, range=Optional[Union[str, "GOEvidenceCode"]])

slots.go_electronic_methods = Slot(uri=VALUESETS.go_electronic_methods, name="go_electronic_methods", curie=VALUESETS.curie('go_electronic_methods'),
                   model_uri=VALUESETS.go_electronic_methods, domain=None, range=Optional[Union[str, "GOElectronicMethods"]])

slots.organism_taxon = Slot(uri=VALUESETS.organism_taxon, name="organism_taxon", curie=VALUESETS.curie('organism_taxon'),
                   model_uri=VALUESETS.organism_taxon, domain=None, range=Optional[Union[str, "OrganismTaxonEnum"]])

slots.common_organism_taxa = Slot(uri=VALUESETS.common_organism_taxa, name="common_organism_taxa", curie=VALUESETS.curie('common_organism_taxa'),
                   model_uri=VALUESETS.common_organism_taxa, domain=None, range=Optional[Union[str, "CommonOrganismTaxaEnum"]])

slots.taxonomic_rank = Slot(uri=VALUESETS.taxonomic_rank, name="taxonomic_rank", curie=VALUESETS.curie('taxonomic_rank'),
                   model_uri=VALUESETS.taxonomic_rank, domain=None, range=Optional[Union[str, "TaxonomicRank"]])

slots.biological_kingdom = Slot(uri=VALUESETS.biological_kingdom, name="biological_kingdom", curie=VALUESETS.curie('biological_kingdom'),
                   model_uri=VALUESETS.biological_kingdom, domain=None, range=Optional[Union[str, "BiologicalKingdom"]])

slots.cell_cycle_phase = Slot(uri=VALUESETS.cell_cycle_phase, name="cell_cycle_phase", curie=VALUESETS.curie('cell_cycle_phase'),
                   model_uri=VALUESETS.cell_cycle_phase, domain=None, range=Optional[Union[str, "CellCyclePhase"]])

slots.mitotic_phase = Slot(uri=VALUESETS.mitotic_phase, name="mitotic_phase", curie=VALUESETS.curie('mitotic_phase'),
                   model_uri=VALUESETS.mitotic_phase, domain=None, range=Optional[Union[str, "MitoticPhase"]])

slots.cell_cycle_checkpoint = Slot(uri=VALUESETS.cell_cycle_checkpoint, name="cell_cycle_checkpoint", curie=VALUESETS.curie('cell_cycle_checkpoint'),
                   model_uri=VALUESETS.cell_cycle_checkpoint, domain=None, range=Optional[Union[str, "CellCycleCheckpoint"]])

slots.meiotic_phase = Slot(uri=VALUESETS.meiotic_phase, name="meiotic_phase", curie=VALUESETS.curie('meiotic_phase'),
                   model_uri=VALUESETS.meiotic_phase, domain=None, range=Optional[Union[str, "MeioticPhase"]])

slots.cell_cycle_regulator = Slot(uri=VALUESETS.cell_cycle_regulator, name="cell_cycle_regulator", curie=VALUESETS.curie('cell_cycle_regulator'),
                   model_uri=VALUESETS.cell_cycle_regulator, domain=None, range=Optional[Union[str, "CellCycleRegulator"]])

slots.cell_proliferation_state = Slot(uri=VALUESETS.cell_proliferation_state, name="cell_proliferation_state", curie=VALUESETS.curie('cell_proliferation_state'),
                   model_uri=VALUESETS.cell_proliferation_state, domain=None, range=Optional[Union[str, "CellProliferationState"]])

slots.dna_damage_response = Slot(uri=VALUESETS.dna_damage_response, name="dna_damage_response", curie=VALUESETS.curie('dna_damage_response'),
                   model_uri=VALUESETS.dna_damage_response, domain=None, range=Optional[Union[str, "DNADamageResponse"]])

slots.genome_feature = Slot(uri=VALUESETS.genome_feature, name="genome_feature", curie=VALUESETS.curie('genome_feature'),
                   model_uri=VALUESETS.genome_feature, domain=None, range=Optional[Union[Union[str, "GenomeFeatureType"], list[Union[str, "GenomeFeatureType"]]]])

slots.metazoan_anatomical_structure = Slot(uri=VALUESETS.metazoan_anatomical_structure, name="metazoan_anatomical_structure", curie=VALUESETS.curie('metazoan_anatomical_structure'),
                   model_uri=VALUESETS.metazoan_anatomical_structure, domain=None, range=Optional[Union[str, "MetazoanAnatomicalStructure"]])

slots.human_anatomical_structure = Slot(uri=VALUESETS.human_anatomical_structure, name="human_anatomical_structure", curie=VALUESETS.curie('human_anatomical_structure'),
                   model_uri=VALUESETS.human_anatomical_structure, domain=None, range=Optional[Union[str, "HumanAnatomicalStructure"]])

slots.plant_anatomical_structure = Slot(uri=VALUESETS.plant_anatomical_structure, name="plant_anatomical_structure", curie=VALUESETS.curie('plant_anatomical_structure'),
                   model_uri=VALUESETS.plant_anatomical_structure, domain=None, range=Optional[Union[str, "PlantAnatomicalStructure"]])

slots.cell = Slot(uri=VALUESETS.cell, name="cell", curie=VALUESETS.curie('cell'),
                   model_uri=VALUESETS.cell, domain=None, range=Optional[Union[str, "CellType"]])

slots.neuron = Slot(uri=VALUESETS.neuron, name="neuron", curie=VALUESETS.curie('neuron'),
                   model_uri=VALUESETS.neuron, domain=None, range=Optional[Union[str, "NeuronType"]])

slots.immune_cell = Slot(uri=VALUESETS.immune_cell, name="immune_cell", curie=VALUESETS.curie('immune_cell'),
                   model_uri=VALUESETS.immune_cell, domain=None, range=Optional[Union[str, "ImmuneCell"]])

slots.stem_cell = Slot(uri=VALUESETS.stem_cell, name="stem_cell", curie=VALUESETS.curie('stem_cell'),
                   model_uri=VALUESETS.stem_cell, domain=None, range=Optional[Union[str, "StemCell"]])

slots.disease = Slot(uri=VALUESETS.disease, name="disease", curie=VALUESETS.curie('disease'),
                   model_uri=VALUESETS.disease, domain=None, range=Optional[Union[str, "Disease"]])

slots.infectious_disease = Slot(uri=VALUESETS.infectious_disease, name="infectious_disease", curie=VALUESETS.curie('infectious_disease'),
                   model_uri=VALUESETS.infectious_disease, domain=None, range=Optional[Union[str, "InfectiousDisease"]])

slots.cancer = Slot(uri=VALUESETS.cancer, name="cancer", curie=VALUESETS.curie('cancer'),
                   model_uri=VALUESETS.cancer, domain=None, range=Optional[Union[str, "Cancer"]])

slots.genetic_disease = Slot(uri=VALUESETS.genetic_disease, name="genetic_disease", curie=VALUESETS.curie('genetic_disease'),
                   model_uri=VALUESETS.genetic_disease, domain=None, range=Optional[Union[str, "GeneticDisease"]])

slots.chemical_entity = Slot(uri=VALUESETS.chemical_entity, name="chemical_entity", curie=VALUESETS.curie('chemical_entity'),
                   model_uri=VALUESETS.chemical_entity, domain=None, range=Optional[Union[str, "ChemicalEntity"]])

slots.drug = Slot(uri=VALUESETS.drug, name="drug", curie=VALUESETS.curie('drug'),
                   model_uri=VALUESETS.drug, domain=None, range=Optional[Union[str, "Drug"]])

slots.metabolite = Slot(uri=VALUESETS.metabolite, name="metabolite", curie=VALUESETS.curie('metabolite'),
                   model_uri=VALUESETS.metabolite, domain=None, range=Optional[Union[str, "Metabolite"]])

slots.protein = Slot(uri=VALUESETS.protein, name="protein", curie=VALUESETS.curie('protein'),
                   model_uri=VALUESETS.protein, domain=None, range=Optional[Union[str, "Protein"]])

slots.phenotype = Slot(uri=VALUESETS.phenotype, name="phenotype", curie=VALUESETS.curie('phenotype'),
                   model_uri=VALUESETS.phenotype, domain=None, range=Optional[Union[str, "Phenotype"]])

slots.clinical_finding = Slot(uri=VALUESETS.clinical_finding, name="clinical_finding", curie=VALUESETS.curie('clinical_finding'),
                   model_uri=VALUESETS.clinical_finding, domain=None, range=Optional[Union[str, "ClinicalFinding"]])

slots.biological_process = Slot(uri=VALUESETS.biological_process, name="biological_process", curie=VALUESETS.curie('biological_process'),
                   model_uri=VALUESETS.biological_process, domain=None, range=Optional[Union[str, "BiologicalProcess"]])

slots.metabolic_process = Slot(uri=VALUESETS.metabolic_process, name="metabolic_process", curie=VALUESETS.curie('metabolic_process'),
                   model_uri=VALUESETS.metabolic_process, domain=None, range=Optional[Union[str, "MetabolicProcess"]])

slots.molecular_function = Slot(uri=VALUESETS.molecular_function, name="molecular_function", curie=VALUESETS.curie('molecular_function'),
                   model_uri=VALUESETS.molecular_function, domain=None, range=Optional[Union[str, "MolecularFunction"]])

slots.cellular_component = Slot(uri=VALUESETS.cellular_component, name="cellular_component", curie=VALUESETS.curie('cellular_component'),
                   model_uri=VALUESETS.cellular_component, domain=None, range=Optional[Union[str, "CellularComponent"]])

slots.sequence_feature = Slot(uri=VALUESETS.sequence_feature, name="sequence_feature", curie=VALUESETS.curie('sequence_feature'),
                   model_uri=VALUESETS.sequence_feature, domain=None, range=Optional[Union[Union[str, "SequenceFeature"], list[Union[str, "SequenceFeature"]]]])

slots.gene_feature = Slot(uri=VALUESETS.gene_feature, name="gene_feature", curie=VALUESETS.curie('gene_feature'),
                   model_uri=VALUESETS.gene_feature, domain=None, range=Optional[Union[Union[str, "GeneFeature"], list[Union[str, "GeneFeature"]]]])

slots.environment = Slot(uri=VALUESETS.environment, name="environment", curie=VALUESETS.curie('environment'),
                   model_uri=VALUESETS.environment, domain=None, range=Optional[Union[str, "Environment"]])

slots.environmental_material = Slot(uri=VALUESETS.environmental_material, name="environmental_material", curie=VALUESETS.curie('environmental_material'),
                   model_uri=VALUESETS.environmental_material, domain=None, range=Optional[Union[str, "EnvironmentalMaterial"]])

slots.quality = Slot(uri=VALUESETS.quality, name="quality", curie=VALUESETS.curie('quality'),
                   model_uri=VALUESETS.quality, domain=None, range=Optional[Union[str, "Quality"]])

slots.physical_quality = Slot(uri=VALUESETS.physical_quality, name="physical_quality", curie=VALUESETS.curie('physical_quality'),
                   model_uri=VALUESETS.physical_quality, domain=None, range=Optional[Union[str, "PhysicalQuality"]])

slots.sample = Slot(uri=VALUESETS.sample, name="sample", curie=VALUESETS.curie('sample'),
                   model_uri=VALUESETS.sample, domain=None, range=Optional[Union[str, "SampleType"]])

slots.structural_biology_technique = Slot(uri=VALUESETS.structural_biology_technique, name="structural_biology_technique", curie=VALUESETS.curie('structural_biology_technique'),
                   model_uri=VALUESETS.structural_biology_technique, domain=None, range=Optional[Union[str, "StructuralBiologyTechnique"]])

slots.cryo_em_preparation = Slot(uri=VALUESETS.cryo_em_preparation, name="cryo_em_preparation", curie=VALUESETS.curie('cryo_em_preparation'),
                   model_uri=VALUESETS.cryo_em_preparation, domain=None, range=Optional[Union[str, "CryoEMPreparationType"]])

slots.cryo_em_grid = Slot(uri=VALUESETS.cryo_em_grid, name="cryo_em_grid", curie=VALUESETS.curie('cryo_em_grid'),
                   model_uri=VALUESETS.cryo_em_grid, domain=None, range=Optional[Union[str, "CryoEMGridType"]])

slots.vitrification_method = Slot(uri=VALUESETS.vitrification_method, name="vitrification_method", curie=VALUESETS.curie('vitrification_method'),
                   model_uri=VALUESETS.vitrification_method, domain=None, range=Optional[Union[str, "VitrificationMethod"]])

slots.crystallization_method = Slot(uri=VALUESETS.crystallization_method, name="crystallization_method", curie=VALUESETS.curie('crystallization_method'),
                   model_uri=VALUESETS.crystallization_method, domain=None, range=Optional[Union[str, "CrystallizationMethod"]])

slots.x_ray_source = Slot(uri=VALUESETS.x_ray_source, name="x_ray_source", curie=VALUESETS.curie('x_ray_source'),
                   model_uri=VALUESETS.x_ray_source, domain=None, range=Optional[Union[str, "XRaySource"]])

slots.detector = Slot(uri=VALUESETS.detector, name="detector", curie=VALUESETS.curie('detector'),
                   model_uri=VALUESETS.detector, domain=None, range=Optional[Union[str, "Detector"]])

slots.workflow = Slot(uri=VALUESETS.workflow, name="workflow", curie=VALUESETS.curie('workflow'),
                   model_uri=VALUESETS.workflow, domain=None, range=Optional[Union[str, "WorkflowType"]])

slots.file_format = Slot(uri=VALUESETS.file_format, name="file_format", curie=VALUESETS.curie('file_format'),
                   model_uri=VALUESETS.file_format, domain=None, range=Optional[Union[str, "FileFormat"]])

slots.data = Slot(uri=VALUESETS.data, name="data", curie=VALUESETS.curie('data'),
                   model_uri=VALUESETS.data, domain=None, range=Optional[Union[str, "DataType"]])

slots.processing_status = Slot(uri=VALUESETS.processing_status, name="processing_status", curie=VALUESETS.curie('processing_status'),
                   model_uri=VALUESETS.processing_status, domain=None, range=Optional[Union[str, "ProcessingStatus"]])

slots.insdc_missing_value = Slot(uri=VALUESETS.insdc_missing_value, name="insdc_missing_value", curie=VALUESETS.curie('insdc_missing_value'),
                   model_uri=VALUESETS.insdc_missing_value, domain=None, range=Optional[Union[str, "InsdcMissingValueEnum"]])

slots.insdc_geographic_location = Slot(uri=VALUESETS.insdc_geographic_location, name="insdc_geographic_location", curie=VALUESETS.curie('insdc_geographic_location'),
                   model_uri=VALUESETS.insdc_geographic_location, domain=None, range=Optional[Union[str, "InsdcGeographicLocationEnum"]])

slots.viral_genome_type = Slot(uri=VALUESETS.viral_genome_type, name="viral_genome_type", curie=VALUESETS.curie('viral_genome_type'),
                   model_uri=VALUESETS.viral_genome_type, domain=None, range=Optional[Union[str, "ViralGenomeTypeEnum"]])

slots.plant_sex = Slot(uri=VALUESETS.plant_sex, name="plant_sex", curie=VALUESETS.curie('plant_sex'),
                   model_uri=VALUESETS.plant_sex, domain=None, range=Optional[Union[str, "PlantSexEnum"]])

slots.rel_to_oxygen = Slot(uri=VALUESETS.rel_to_oxygen, name="rel_to_oxygen", curie=VALUESETS.curie('rel_to_oxygen'),
                   model_uri=VALUESETS.rel_to_oxygen, domain=None, range=Optional[Union[str, "RelToOxygenEnum"]])

slots.trophic_level = Slot(uri=VALUESETS.trophic_level, name="trophic_level", curie=VALUESETS.curie('trophic_level'),
                   model_uri=VALUESETS.trophic_level, domain=None, range=Optional[Union[str, "TrophicLevelEnum"]])

slots.human_developmental_stage = Slot(uri=VALUESETS.human_developmental_stage, name="human_developmental_stage", curie=VALUESETS.curie('human_developmental_stage'),
                   model_uri=VALUESETS.human_developmental_stage, domain=None, range=Optional[Union[str, "HumanDevelopmentalStage"]])

slots.mouse_developmental_stage = Slot(uri=VALUESETS.mouse_developmental_stage, name="mouse_developmental_stage", curie=VALUESETS.curie('mouse_developmental_stage'),
                   model_uri=VALUESETS.mouse_developmental_stage, domain=None, range=Optional[Union[str, "MouseDevelopmentalStage"]])

slots.day_of_week = Slot(uri=VALUESETS.day_of_week, name="day_of_week", curie=VALUESETS.curie('day_of_week'),
                   model_uri=VALUESETS.day_of_week, domain=None, range=Optional[Union[str, "DayOfWeek"]])

slots.month = Slot(uri=VALUESETS.month, name="month", curie=VALUESETS.curie('month'),
                   model_uri=VALUESETS.month, domain=None, range=Optional[Union[str, "Month"]])

slots.quarter = Slot(uri=VALUESETS.quarter, name="quarter", curie=VALUESETS.curie('quarter'),
                   model_uri=VALUESETS.quarter, domain=None, range=Optional[Union[str, "Quarter"]])

slots.season = Slot(uri=VALUESETS.season, name="season", curie=VALUESETS.curie('season'),
                   model_uri=VALUESETS.season, domain=None, range=Optional[Union[str, "Season"]])

slots.time_period = Slot(uri=VALUESETS.time_period, name="time_period", curie=VALUESETS.curie('time_period'),
                   model_uri=VALUESETS.time_period, domain=None, range=Optional[Union[str, "TimePeriod"]])

slots.time_of_day = Slot(uri=VALUESETS.time_of_day, name="time_of_day", curie=VALUESETS.curie('time_of_day'),
                   model_uri=VALUESETS.time_of_day, domain=None, range=Optional[Union[str, "TimeOfDay"]])

slots.business_time_frame = Slot(uri=VALUESETS.business_time_frame, name="business_time_frame", curie=VALUESETS.curie('business_time_frame'),
                   model_uri=VALUESETS.business_time_frame, domain=None, range=Optional[Union[str, "BusinessTimeFrame"]])

slots.geological_era = Slot(uri=VALUESETS.geological_era, name="geological_era", curie=VALUESETS.curie('geological_era'),
                   model_uri=VALUESETS.geological_era, domain=None, range=Optional[Union[str, "GeologicalEra"]])

slots.historical_period = Slot(uri=VALUESETS.historical_period, name="historical_period", curie=VALUESETS.curie('historical_period'),
                   model_uri=VALUESETS.historical_period, domain=None, range=Optional[Union[str, "HistoricalPeriod"]])

slots.publication = Slot(uri=VALUESETS.publication, name="publication", curie=VALUESETS.curie('publication'),
                   model_uri=VALUESETS.publication, domain=None, range=Optional[Union[str, "PublicationType"]])

slots.peer_review_status = Slot(uri=VALUESETS.peer_review_status, name="peer_review_status", curie=VALUESETS.curie('peer_review_status'),
                   model_uri=VALUESETS.peer_review_status, domain=None, range=Optional[Union[str, "PeerReviewStatus"]])

slots.academic_degree = Slot(uri=VALUESETS.academic_degree, name="academic_degree", curie=VALUESETS.curie('academic_degree'),
                   model_uri=VALUESETS.academic_degree, domain=None, range=Optional[Union[str, "AcademicDegree"]])

slots.license = Slot(uri=VALUESETS.license, name="license", curie=VALUESETS.curie('license'),
                   model_uri=VALUESETS.license, domain=None, range=Optional[Union[str, "LicenseType"]])

slots.research_field = Slot(uri=VALUESETS.research_field, name="research_field", curie=VALUESETS.curie('research_field'),
                   model_uri=VALUESETS.research_field, domain=None, range=Optional[Union[str, "ResearchField"]])

slots.funding = Slot(uri=VALUESETS.funding, name="funding", curie=VALUESETS.curie('funding'),
                   model_uri=VALUESETS.funding, domain=None, range=Optional[Union[str, "FundingType"]])

slots.manuscript_section = Slot(uri=VALUESETS.manuscript_section, name="manuscript_section", curie=VALUESETS.curie('manuscript_section'),
                   model_uri=VALUESETS.manuscript_section, domain=None, range=Optional[Union[str, "ManuscriptSection"]])

slots.research_role = Slot(uri=VALUESETS.research_role, name="research_role", curie=VALUESETS.curie('research_role'),
                   model_uri=VALUESETS.research_role, domain=None, range=Optional[Union[str, "ResearchRole"]])

slots.open_access = Slot(uri=VALUESETS.open_access, name="open_access", curie=VALUESETS.curie('open_access'),
                   model_uri=VALUESETS.open_access, domain=None, range=Optional[Union[str, "OpenAccessType"]])

slots.citation_style = Slot(uri=VALUESETS.citation_style, name="citation_style", curie=VALUESETS.curie('citation_style'),
                   model_uri=VALUESETS.citation_style, domain=None, range=Optional[Union[str, "CitationStyle"]])

slots.energy_source = Slot(uri=VALUESETS.energy_source, name="energy_source", curie=VALUESETS.curie('energy_source'),
                   model_uri=VALUESETS.energy_source, domain=None, range=Optional[Union[str, "EnergySource"]])

slots.energy_unit = Slot(uri=VALUESETS.energy_unit, name="energy_unit", curie=VALUESETS.curie('energy_unit'),
                   model_uri=VALUESETS.energy_unit, domain=None, range=Optional[Union[str, "EnergyUnit"]])

slots.power_unit = Slot(uri=VALUESETS.power_unit, name="power_unit", curie=VALUESETS.curie('power_unit'),
                   model_uri=VALUESETS.power_unit, domain=None, range=Optional[Union[str, "PowerUnit"]])

slots.energy_efficiency_rating = Slot(uri=VALUESETS.energy_efficiency_rating, name="energy_efficiency_rating", curie=VALUESETS.curie('energy_efficiency_rating'),
                   model_uri=VALUESETS.energy_efficiency_rating, domain=None, range=Optional[Union[str, "EnergyEfficiencyRating"]])

slots.building_energy_standard = Slot(uri=VALUESETS.building_energy_standard, name="building_energy_standard", curie=VALUESETS.curie('building_energy_standard'),
                   model_uri=VALUESETS.building_energy_standard, domain=None, range=Optional[Union[str, "BuildingEnergyStandard"]])

slots.grid = Slot(uri=VALUESETS.grid, name="grid", curie=VALUESETS.curie('grid'),
                   model_uri=VALUESETS.grid, domain=None, range=Optional[Union[str, "GridType"]])

slots.energy_storage = Slot(uri=VALUESETS.energy_storage, name="energy_storage", curie=VALUESETS.curie('energy_storage'),
                   model_uri=VALUESETS.energy_storage, domain=None, range=Optional[Union[str, "EnergyStorageType"]])

slots.emission_scope = Slot(uri=VALUESETS.emission_scope, name="emission_scope", curie=VALUESETS.curie('emission_scope'),
                   model_uri=VALUESETS.emission_scope, domain=None, range=Optional[Union[str, "EmissionScope"]])

slots.carbon_intensity = Slot(uri=VALUESETS.carbon_intensity, name="carbon_intensity", curie=VALUESETS.curie('carbon_intensity'),
                   model_uri=VALUESETS.carbon_intensity, domain=None, range=Optional[Union[str, "CarbonIntensity"]])

slots.electricity_market = Slot(uri=VALUESETS.electricity_market, name="electricity_market", curie=VALUESETS.curie('electricity_market'),
                   model_uri=VALUESETS.electricity_market, domain=None, range=Optional[Union[str, "ElectricityMarket"]])

slots.fossil_fuel_type = Slot(uri=VALUESETS.fossil_fuel_type, name="fossil_fuel_type", curie=VALUESETS.curie('fossil_fuel_type'),
                   model_uri=VALUESETS.fossil_fuel_type, domain=None, range=Optional[Union[str, "FossilFuelTypeEnum"]])

slots.reactor_type = Slot(uri=VALUESETS.reactor_type, name="reactor_type", curie=VALUESETS.curie('reactor_type'),
                   model_uri=VALUESETS.reactor_type, domain=None, range=Optional[Union[str, "ReactorTypeEnum"]])

slots.reactor_generation = Slot(uri=VALUESETS.reactor_generation, name="reactor_generation", curie=VALUESETS.curie('reactor_generation'),
                   model_uri=VALUESETS.reactor_generation, domain=None, range=Optional[Union[str, "ReactorGenerationEnum"]])

slots.reactor_coolant = Slot(uri=VALUESETS.reactor_coolant, name="reactor_coolant", curie=VALUESETS.curie('reactor_coolant'),
                   model_uri=VALUESETS.reactor_coolant, domain=None, range=Optional[Union[str, "ReactorCoolantEnum"]])

slots.reactor_moderator = Slot(uri=VALUESETS.reactor_moderator, name="reactor_moderator", curie=VALUESETS.curie('reactor_moderator'),
                   model_uri=VALUESETS.reactor_moderator, domain=None, range=Optional[Union[str, "ReactorModeratorEnum"]])

slots.reactor_neutron_spectrum = Slot(uri=VALUESETS.reactor_neutron_spectrum, name="reactor_neutron_spectrum", curie=VALUESETS.curie('reactor_neutron_spectrum'),
                   model_uri=VALUESETS.reactor_neutron_spectrum, domain=None, range=Optional[Union[str, "ReactorNeutronSpectrumEnum"]])

slots.reactor_size_category = Slot(uri=VALUESETS.reactor_size_category, name="reactor_size_category", curie=VALUESETS.curie('reactor_size_category'),
                   model_uri=VALUESETS.reactor_size_category, domain=None, range=Optional[Union[str, "ReactorSizeCategoryEnum"]])

slots.nuclear_fuel_type = Slot(uri=VALUESETS.nuclear_fuel_type, name="nuclear_fuel_type", curie=VALUESETS.curie('nuclear_fuel_type'),
                   model_uri=VALUESETS.nuclear_fuel_type, domain=None, range=Optional[Union[str, "NuclearFuelTypeEnum"]])

slots.uranium_enrichment_level = Slot(uri=VALUESETS.uranium_enrichment_level, name="uranium_enrichment_level", curie=VALUESETS.curie('uranium_enrichment_level'),
                   model_uri=VALUESETS.uranium_enrichment_level, domain=None, range=Optional[Union[str, "UraniumEnrichmentLevelEnum"]])

slots.fuel_form = Slot(uri=VALUESETS.fuel_form, name="fuel_form", curie=VALUESETS.curie('fuel_form'),
                   model_uri=VALUESETS.fuel_form, domain=None, range=Optional[Union[str, "FuelFormEnum"]])

slots.fuel_assembly_type = Slot(uri=VALUESETS.fuel_assembly_type, name="fuel_assembly_type", curie=VALUESETS.curie('fuel_assembly_type'),
                   model_uri=VALUESETS.fuel_assembly_type, domain=None, range=Optional[Union[str, "FuelAssemblyTypeEnum"]])

slots.fuel_cycle_stage = Slot(uri=VALUESETS.fuel_cycle_stage, name="fuel_cycle_stage", curie=VALUESETS.curie('fuel_cycle_stage'),
                   model_uri=VALUESETS.fuel_cycle_stage, domain=None, range=Optional[Union[str, "FuelCycleStageEnum"]])

slots.fissile_material = Slot(uri=VALUESETS.fissile_material, name="fissile_material", curie=VALUESETS.curie('fissile_material'),
                   model_uri=VALUESETS.fissile_material, domain=None, range=Optional[Union[str, "FissileIsotopeEnum"]])

slots.waste_classification = Slot(uri=VALUESETS.waste_classification, name="waste_classification", curie=VALUESETS.curie('waste_classification'),
                   model_uri=VALUESETS.waste_classification, domain=None, range=Optional[Union[str, "IAEAWasteClassificationEnum"]])

slots.nrc_waste_class = Slot(uri=VALUESETS.nrc_waste_class, name="nrc_waste_class", curie=VALUESETS.curie('nrc_waste_class'),
                   model_uri=VALUESETS.nrc_waste_class, domain=None, range=Optional[Union[str, "NRCWasteClassEnum"]])

slots.waste_heat_generation = Slot(uri=VALUESETS.waste_heat_generation, name="waste_heat_generation", curie=VALUESETS.curie('waste_heat_generation'),
                   model_uri=VALUESETS.waste_heat_generation, domain=None, range=Optional[Union[str, "WasteHeatGenerationEnum"]])

slots.waste_half_life_category = Slot(uri=VALUESETS.waste_half_life_category, name="waste_half_life_category", curie=VALUESETS.curie('waste_half_life_category'),
                   model_uri=VALUESETS.waste_half_life_category, domain=None, range=Optional[Union[str, "WasteHalfLifeCategoryEnum"]])

slots.waste_disposal_method = Slot(uri=VALUESETS.waste_disposal_method, name="waste_disposal_method", curie=VALUESETS.curie('waste_disposal_method'),
                   model_uri=VALUESETS.waste_disposal_method, domain=None, range=Optional[Union[str, "WasteDisposalMethodEnum"]])

slots.waste_source = Slot(uri=VALUESETS.waste_source, name="waste_source", curie=VALUESETS.curie('waste_source'),
                   model_uri=VALUESETS.waste_source, domain=None, range=Optional[Union[str, "WasteSourceEnum"]])

slots.transuranic_category = Slot(uri=VALUESETS.transuranic_category, name="transuranic_category", curie=VALUESETS.curie('transuranic_category'),
                   model_uri=VALUESETS.transuranic_category, domain=None, range=Optional[Union[str, "TransuranicWasteCategoryEnum"]])

slots.ines_level = Slot(uri=VALUESETS.ines_level, name="ines_level", curie=VALUESETS.curie('ines_level'),
                   model_uri=VALUESETS.ines_level, domain=None, range=Optional[Union[str, "INESLevelEnum"]])

slots.emergency_classification = Slot(uri=VALUESETS.emergency_classification, name="emergency_classification", curie=VALUESETS.curie('emergency_classification'),
                   model_uri=VALUESETS.emergency_classification, domain=None, range=Optional[Union[str, "EmergencyClassificationEnum"]])

slots.nuclear_security_category = Slot(uri=VALUESETS.nuclear_security_category, name="nuclear_security_category", curie=VALUESETS.curie('nuclear_security_category'),
                   model_uri=VALUESETS.nuclear_security_category, domain=None, range=Optional[Union[str, "NuclearSecurityCategoryEnum"]])

slots.safety_system_class = Slot(uri=VALUESETS.safety_system_class, name="safety_system_class", curie=VALUESETS.curie('safety_system_class'),
                   model_uri=VALUESETS.safety_system_class, domain=None, range=Optional[Union[str, "SafetySystemClassEnum"]])

slots.reactor_safety_function = Slot(uri=VALUESETS.reactor_safety_function, name="reactor_safety_function", curie=VALUESETS.curie('reactor_safety_function'),
                   model_uri=VALUESETS.reactor_safety_function, domain=None, range=Optional[Union[str, "ReactorSafetyFunctionEnum"]])

slots.defense_in_depth_level = Slot(uri=VALUESETS.defense_in_depth_level, name="defense_in_depth_level", curie=VALUESETS.curie('defense_in_depth_level'),
                   model_uri=VALUESETS.defense_in_depth_level, domain=None, range=Optional[Union[str, "DefenseInDepthLevelEnum"]])

slots.radiation_protection_zone = Slot(uri=VALUESETS.radiation_protection_zone, name="radiation_protection_zone", curie=VALUESETS.curie('radiation_protection_zone'),
                   model_uri=VALUESETS.radiation_protection_zone, domain=None, range=Optional[Union[str, "RadiationProtectionZoneEnum"]])

slots.nuclear_facility_type = Slot(uri=VALUESETS.nuclear_facility_type, name="nuclear_facility_type", curie=VALUESETS.curie('nuclear_facility_type'),
                   model_uri=VALUESETS.nuclear_facility_type, domain=None, range=Optional[Union[str, "NuclearFacilityTypeEnum"]])

slots.power_plant_status = Slot(uri=VALUESETS.power_plant_status, name="power_plant_status", curie=VALUESETS.curie('power_plant_status'),
                   model_uri=VALUESETS.power_plant_status, domain=None, range=Optional[Union[str, "PowerPlantStatusEnum"]])

slots.research_reactor_type = Slot(uri=VALUESETS.research_reactor_type, name="research_reactor_type", curie=VALUESETS.curie('research_reactor_type'),
                   model_uri=VALUESETS.research_reactor_type, domain=None, range=Optional[Union[str, "ResearchReactorTypeEnum"]])

slots.fuel_cycle_facility_type = Slot(uri=VALUESETS.fuel_cycle_facility_type, name="fuel_cycle_facility_type", curie=VALUESETS.curie('fuel_cycle_facility_type'),
                   model_uri=VALUESETS.fuel_cycle_facility_type, domain=None, range=Optional[Union[str, "FuelCycleFacilityTypeEnum"]])

slots.waste_facility_type = Slot(uri=VALUESETS.waste_facility_type, name="waste_facility_type", curie=VALUESETS.curie('waste_facility_type'),
                   model_uri=VALUESETS.waste_facility_type, domain=None, range=Optional[Union[str, "WasteFacilityTypeEnum"]])

slots.nuclear_ship_type = Slot(uri=VALUESETS.nuclear_ship_type, name="nuclear_ship_type", curie=VALUESETS.curie('nuclear_ship_type'),
                   model_uri=VALUESETS.nuclear_ship_type, domain=None, range=Optional[Union[str, "NuclearShipTypeEnum"]])

slots.reactor_operating_state = Slot(uri=VALUESETS.reactor_operating_state, name="reactor_operating_state", curie=VALUESETS.curie('reactor_operating_state'),
                   model_uri=VALUESETS.reactor_operating_state, domain=None, range=Optional[Union[str, "ReactorOperatingStateEnum"]])

slots.maintenance_type = Slot(uri=VALUESETS.maintenance_type, name="maintenance_type", curie=VALUESETS.curie('maintenance_type'),
                   model_uri=VALUESETS.maintenance_type, domain=None, range=Optional[Union[str, "MaintenanceTypeEnum"]])

slots.licensing_stage = Slot(uri=VALUESETS.licensing_stage, name="licensing_stage", curie=VALUESETS.curie('licensing_stage'),
                   model_uri=VALUESETS.licensing_stage, domain=None, range=Optional[Union[str, "LicensingStageEnum"]])

slots.fuel_cycle_operation = Slot(uri=VALUESETS.fuel_cycle_operation, name="fuel_cycle_operation", curie=VALUESETS.curie('fuel_cycle_operation'),
                   model_uri=VALUESETS.fuel_cycle_operation, domain=None, range=Optional[Union[str, "FuelCycleOperationEnum"]])

slots.reactor_control_mode = Slot(uri=VALUESETS.reactor_control_mode, name="reactor_control_mode", curie=VALUESETS.curie('reactor_control_mode'),
                   model_uri=VALUESETS.reactor_control_mode, domain=None, range=Optional[Union[str, "ReactorControlModeEnum"]])

slots.operational_procedure = Slot(uri=VALUESETS.operational_procedure, name="operational_procedure", curie=VALUESETS.curie('operational_procedure'),
                   model_uri=VALUESETS.operational_procedure, domain=None, range=Optional[Union[str, "OperationalProcedureEnum"]])

slots.mining = Slot(uri=VALUESETS.mining, name="mining", curie=VALUESETS.curie('mining'),
                   model_uri=VALUESETS.mining, domain=None, range=Optional[Union[str, "MiningType"]])

slots.mineral_category = Slot(uri=VALUESETS.mineral_category, name="mineral_category", curie=VALUESETS.curie('mineral_category'),
                   model_uri=VALUESETS.mineral_category, domain=None, range=Optional[Union[str, "MineralCategory"]])

slots.critical_mineral = Slot(uri=VALUESETS.critical_mineral, name="critical_mineral", curie=VALUESETS.curie('critical_mineral'),
                   model_uri=VALUESETS.critical_mineral, domain=None, range=Optional[Union[str, "CriticalMineral"]])

slots.common_mineral = Slot(uri=VALUESETS.common_mineral, name="common_mineral", curie=VALUESETS.curie('common_mineral'),
                   model_uri=VALUESETS.common_mineral, domain=None, range=Optional[Union[str, "CommonMineral"]])

slots.mining_equipment = Slot(uri=VALUESETS.mining_equipment, name="mining_equipment", curie=VALUESETS.curie('mining_equipment'),
                   model_uri=VALUESETS.mining_equipment, domain=None, range=Optional[Union[str, "MiningEquipment"]])

slots.ore_grade = Slot(uri=VALUESETS.ore_grade, name="ore_grade", curie=VALUESETS.curie('ore_grade'),
                   model_uri=VALUESETS.ore_grade, domain=None, range=Optional[Union[str, "OreGrade"]])

slots.mining_phase = Slot(uri=VALUESETS.mining_phase, name="mining_phase", curie=VALUESETS.curie('mining_phase'),
                   model_uri=VALUESETS.mining_phase, domain=None, range=Optional[Union[str, "MiningPhase"]])

slots.mining_hazard = Slot(uri=VALUESETS.mining_hazard, name="mining_hazard", curie=VALUESETS.curie('mining_hazard'),
                   model_uri=VALUESETS.mining_hazard, domain=None, range=Optional[Union[str, "MiningHazard"]])

slots.environmental_impact = Slot(uri=VALUESETS.environmental_impact, name="environmental_impact", curie=VALUESETS.curie('environmental_impact'),
                   model_uri=VALUESETS.environmental_impact, domain=None, range=Optional[Union[str, "EnvironmentalImpact"]])

slots.extractive_industry_facility_type = Slot(uri=VALUESETS.extractive_industry_facility_type, name="extractive_industry_facility_type", curie=VALUESETS.curie('extractive_industry_facility_type'),
                   model_uri=VALUESETS.extractive_industry_facility_type, domain=None, range=Optional[Union[str, "ExtractiveIndustryFacilityTypeEnum"]])

slots.extractive_industry_product_type = Slot(uri=VALUESETS.extractive_industry_product_type, name="extractive_industry_product_type", curie=VALUESETS.curie('extractive_industry_product_type'),
                   model_uri=VALUESETS.extractive_industry_product_type, domain=None, range=Optional[Union[str, "ExtractiveIndustryProductTypeEnum"]])

slots.mining_method = Slot(uri=VALUESETS.mining_method, name="mining_method", curie=VALUESETS.curie('mining_method'),
                   model_uri=VALUESETS.mining_method, domain=None, range=Optional[Union[str, "MiningMethodEnum"]])

slots.well_type = Slot(uri=VALUESETS.well_type, name="well_type", curie=VALUESETS.curie('well_type'),
                   model_uri=VALUESETS.well_type, domain=None, range=Optional[Union[str, "WellTypeEnum"]])

slots.outcome_type = Slot(uri=VALUESETS.outcome_type, name="outcome_type", curie=VALUESETS.curie('outcome_type'),
                   model_uri=VALUESETS.outcome_type, domain=None, range=Optional[Union[str, "OutcomeTypeEnum"]])

slots.person_status = Slot(uri=VALUESETS.person_status, name="person_status", curie=VALUESETS.curie('person_status'),
                   model_uri=VALUESETS.person_status, domain=None, range=Optional[Union[str, "PersonStatusEnum"]])

slots.mime = Slot(uri=VALUESETS.mime, name="mime", curie=VALUESETS.curie('mime'),
                   model_uri=VALUESETS.mime, domain=None, range=Optional[Union[str, "MimeType"]])

slots.mime_type_category = Slot(uri=VALUESETS.mime_type_category, name="mime_type_category", curie=VALUESETS.curie('mime_type_category'),
                   model_uri=VALUESETS.mime_type_category, domain=None, range=Optional[Union[str, "MimeTypeCategory"]])

slots.text_charset = Slot(uri=VALUESETS.text_charset, name="text_charset", curie=VALUESETS.curie('text_charset'),
                   model_uri=VALUESETS.text_charset, domain=None, range=Optional[Union[str, "TextCharset"]])

slots.compression = Slot(uri=VALUESETS.compression, name="compression", curie=VALUESETS.curie('compression'),
                   model_uri=VALUESETS.compression, domain=None, range=Optional[Union[str, "CompressionType"]])

slots.state_of_matter = Slot(uri=VALUESETS.state_of_matter, name="state_of_matter", curie=VALUESETS.curie('state_of_matter'),
                   model_uri=VALUESETS.state_of_matter, domain=None, range=Optional[Union[str, "StateOfMatterEnum"]])

slots.air_pollutant = Slot(uri=VALUESETS.air_pollutant, name="air_pollutant", curie=VALUESETS.curie('air_pollutant'),
                   model_uri=VALUESETS.air_pollutant, domain=None, range=Optional[Union[str, "AirPollutantEnum"]])

slots.pesticide_type = Slot(uri=VALUESETS.pesticide_type, name="pesticide_type", curie=VALUESETS.curie('pesticide_type'),
                   model_uri=VALUESETS.pesticide_type, domain=None, range=Optional[Union[str, "PesticideTypeEnum"]])

slots.heavy_metal = Slot(uri=VALUESETS.heavy_metal, name="heavy_metal", curie=VALUESETS.curie('heavy_metal'),
                   model_uri=VALUESETS.heavy_metal, domain=None, range=Optional[Union[str, "HeavyMetalEnum"]])

slots.exposure_route = Slot(uri=VALUESETS.exposure_route, name="exposure_route", curie=VALUESETS.curie('exposure_route'),
                   model_uri=VALUESETS.exposure_route, domain=None, range=Optional[Union[str, "ExposureRouteEnum"]])

slots.exposure_source = Slot(uri=VALUESETS.exposure_source, name="exposure_source", curie=VALUESETS.curie('exposure_source'),
                   model_uri=VALUESETS.exposure_source, domain=None, range=Optional[Union[str, "ExposureSourceEnum"]])

slots.water_contaminant = Slot(uri=VALUESETS.water_contaminant, name="water_contaminant", curie=VALUESETS.curie('water_contaminant'),
                   model_uri=VALUESETS.water_contaminant, domain=None, range=Optional[Union[str, "WaterContaminantEnum"]])

slots.endocrine_disruptor = Slot(uri=VALUESETS.endocrine_disruptor, name="endocrine_disruptor", curie=VALUESETS.curie('endocrine_disruptor'),
                   model_uri=VALUESETS.endocrine_disruptor, domain=None, range=Optional[Union[str, "EndocrineDisruptorEnum"]])

slots.exposure_duration = Slot(uri=VALUESETS.exposure_duration, name="exposure_duration", curie=VALUESETS.curie('exposure_duration'),
                   model_uri=VALUESETS.exposure_duration, domain=None, range=Optional[Union[str, "ExposureDurationEnum"]])

slots.country_code_iso2 = Slot(uri=VALUESETS.country_code_iso2, name="country_code_iso2", curie=VALUESETS.curie('country_code_iso2'),
                   model_uri=VALUESETS.country_code_iso2, domain=None, range=Optional[Union[str, "CountryCodeISO2Enum"]])

slots.country_code_iso3 = Slot(uri=VALUESETS.country_code_iso3, name="country_code_iso3", curie=VALUESETS.curie('country_code_iso3'),
                   model_uri=VALUESETS.country_code_iso3, domain=None, range=Optional[Union[str, "CountryCodeISO3Enum"]])

slots.us_state_code = Slot(uri=VALUESETS.us_state_code, name="us_state_code", curie=VALUESETS.curie('us_state_code'),
                   model_uri=VALUESETS.us_state_code, domain=None, range=Optional[Union[str, "USStateCodeEnum"]])

slots.canadian_province_code = Slot(uri=VALUESETS.canadian_province_code, name="canadian_province_code", curie=VALUESETS.curie('canadian_province_code'),
                   model_uri=VALUESETS.canadian_province_code, domain=None, range=Optional[Union[str, "CanadianProvinceCodeEnum"]])

slots.compass_direction = Slot(uri=VALUESETS.compass_direction, name="compass_direction", curie=VALUESETS.curie('compass_direction'),
                   model_uri=VALUESETS.compass_direction, domain=None, range=Optional[Union[str, "CompassDirection"]])

slots.relative_direction = Slot(uri=VALUESETS.relative_direction, name="relative_direction", curie=VALUESETS.curie('relative_direction'),
                   model_uri=VALUESETS.relative_direction, domain=None, range=Optional[Union[str, "RelativeDirection"]])

slots.wind_direction = Slot(uri=VALUESETS.wind_direction, name="wind_direction", curie=VALUESETS.curie('wind_direction'),
                   model_uri=VALUESETS.wind_direction, domain=None, range=Optional[Union[str, "WindDirection"]])

slots.continent = Slot(uri=VALUESETS.continent, name="continent", curie=VALUESETS.curie('continent'),
                   model_uri=VALUESETS.continent, domain=None, range=Optional[Union[str, "ContinentEnum"]])

slots.un_region = Slot(uri=VALUESETS.un_region, name="un_region", curie=VALUESETS.curie('un_region'),
                   model_uri=VALUESETS.un_region, domain=None, range=Optional[Union[str, "UNRegionEnum"]])

slots.language_code_iso639_1 = Slot(uri=VALUESETS.language_code_iso639_1, name="language_code_iso639_1", curie=VALUESETS.curie('language_code_iso639_1'),
                   model_uri=VALUESETS.language_code_iso639_1, domain=None, range=Optional[Union[str, "LanguageCodeISO6391Enum"]])

slots.time_zone = Slot(uri=VALUESETS.time_zone, name="time_zone", curie=VALUESETS.curie('time_zone'),
                   model_uri=VALUESETS.time_zone, domain=None, range=Optional[Union[str, "TimeZoneEnum"]])

slots.currency_code_iso4217 = Slot(uri=VALUESETS.currency_code_iso4217, name="currency_code_iso4217", curie=VALUESETS.curie('currency_code_iso4217'),
                   model_uri=VALUESETS.currency_code_iso4217, domain=None, range=Optional[Union[str, "CurrencyCodeISO4217Enum"]])

slots.sentiment_classification = Slot(uri=VALUESETS.sentiment_classification, name="sentiment_classification", curie=VALUESETS.curie('sentiment_classification'),
                   model_uri=VALUESETS.sentiment_classification, domain=None, range=Optional[Union[str, "SentimentClassificationEnum"]])

slots.fine_sentiment_classification = Slot(uri=VALUESETS.fine_sentiment_classification, name="fine_sentiment_classification", curie=VALUESETS.curie('fine_sentiment_classification'),
                   model_uri=VALUESETS.fine_sentiment_classification, domain=None, range=Optional[Union[str, "FineSentimentClassificationEnum"]])

slots.binary_classification = Slot(uri=VALUESETS.binary_classification, name="binary_classification", curie=VALUESETS.curie('binary_classification'),
                   model_uri=VALUESETS.binary_classification, domain=None, range=Optional[Union[str, "BinaryClassificationEnum"]])

slots.spam_classification = Slot(uri=VALUESETS.spam_classification, name="spam_classification", curie=VALUESETS.curie('spam_classification'),
                   model_uri=VALUESETS.spam_classification, domain=None, range=Optional[Union[str, "SpamClassificationEnum"]])

slots.anomaly_detection = Slot(uri=VALUESETS.anomaly_detection, name="anomaly_detection", curie=VALUESETS.curie('anomaly_detection'),
                   model_uri=VALUESETS.anomaly_detection, domain=None, range=Optional[Union[str, "AnomalyDetectionEnum"]])

slots.churn_classification = Slot(uri=VALUESETS.churn_classification, name="churn_classification", curie=VALUESETS.curie('churn_classification'),
                   model_uri=VALUESETS.churn_classification, domain=None, range=Optional[Union[str, "ChurnClassificationEnum"]])

slots.fraud_detection = Slot(uri=VALUESETS.fraud_detection, name="fraud_detection", curie=VALUESETS.curie('fraud_detection'),
                   model_uri=VALUESETS.fraud_detection, domain=None, range=Optional[Union[str, "FraudDetectionEnum"]])

slots.quality_control = Slot(uri=VALUESETS.quality_control, name="quality_control", curie=VALUESETS.curie('quality_control'),
                   model_uri=VALUESETS.quality_control, domain=None, range=Optional[Union[str, "QualityControlEnum"]])

slots.defect_classification = Slot(uri=VALUESETS.defect_classification, name="defect_classification", curie=VALUESETS.curie('defect_classification'),
                   model_uri=VALUESETS.defect_classification, domain=None, range=Optional[Union[str, "DefectClassificationEnum"]])

slots.basic_emotion = Slot(uri=VALUESETS.basic_emotion, name="basic_emotion", curie=VALUESETS.curie('basic_emotion'),
                   model_uri=VALUESETS.basic_emotion, domain=None, range=Optional[Union[str, "BasicEmotionEnum"]])

slots.extended_emotion = Slot(uri=VALUESETS.extended_emotion, name="extended_emotion", curie=VALUESETS.curie('extended_emotion'),
                   model_uri=VALUESETS.extended_emotion, domain=None, range=Optional[Union[str, "ExtendedEmotionEnum"]])

slots.priority_level = Slot(uri=VALUESETS.priority_level, name="priority_level", curie=VALUESETS.curie('priority_level'),
                   model_uri=VALUESETS.priority_level, domain=None, range=Optional[Union[str, "PriorityLevelEnum"]])

slots.severity_level = Slot(uri=VALUESETS.severity_level, name="severity_level", curie=VALUESETS.curie('severity_level'),
                   model_uri=VALUESETS.severity_level, domain=None, range=Optional[Union[str, "SeverityLevelEnum"]])

slots.confidence_level = Slot(uri=VALUESETS.confidence_level, name="confidence_level", curie=VALUESETS.curie('confidence_level'),
                   model_uri=VALUESETS.confidence_level, domain=None, range=Optional[Union[str, "ConfidenceLevelEnum"]])

slots.news_topic_category = Slot(uri=VALUESETS.news_topic_category, name="news_topic_category", curie=VALUESETS.curie('news_topic_category'),
                   model_uri=VALUESETS.news_topic_category, domain=None, range=Optional[Union[str, "NewsTopicCategoryEnum"]])

slots.toxicity_classification = Slot(uri=VALUESETS.toxicity_classification, name="toxicity_classification", curie=VALUESETS.curie('toxicity_classification'),
                   model_uri=VALUESETS.toxicity_classification, domain=None, range=Optional[Union[str, "ToxicityClassificationEnum"]])

slots.intent_classification = Slot(uri=VALUESETS.intent_classification, name="intent_classification", curie=VALUESETS.curie('intent_classification'),
                   model_uri=VALUESETS.intent_classification, domain=None, range=Optional[Union[str, "IntentClassificationEnum"]])

slots.simple_spatial_direction = Slot(uri=VALUESETS.simple_spatial_direction, name="simple_spatial_direction", curie=VALUESETS.curie('simple_spatial_direction'),
                   model_uri=VALUESETS.simple_spatial_direction, domain=None, range=Optional[Union[str, "SimpleSpatialDirection"]])

slots.anatomical_side = Slot(uri=VALUESETS.anatomical_side, name="anatomical_side", curie=VALUESETS.curie('anatomical_side'),
                   model_uri=VALUESETS.anatomical_side, domain=None, range=Optional[Union[str, "AnatomicalSide"]])

slots.anatomical_region = Slot(uri=VALUESETS.anatomical_region, name="anatomical_region", curie=VALUESETS.curie('anatomical_region'),
                   model_uri=VALUESETS.anatomical_region, domain=None, range=Optional[Union[str, "AnatomicalRegion"]])

slots.anatomical_axis = Slot(uri=VALUESETS.anatomical_axis, name="anatomical_axis", curie=VALUESETS.curie('anatomical_axis'),
                   model_uri=VALUESETS.anatomical_axis, domain=None, range=Optional[Union[str, "AnatomicalAxis"]])

slots.anatomical_plane = Slot(uri=VALUESETS.anatomical_plane, name="anatomical_plane", curie=VALUESETS.curie('anatomical_plane'),
                   model_uri=VALUESETS.anatomical_plane, domain=None, range=Optional[Union[str, "AnatomicalPlane"]])

slots.spatial_relationship = Slot(uri=VALUESETS.spatial_relationship, name="spatial_relationship", curie=VALUESETS.curie('spatial_relationship'),
                   model_uri=VALUESETS.spatial_relationship, domain=None, range=Optional[Union[str, "SpatialRelationship"]])

slots.cell_polarity = Slot(uri=VALUESETS.cell_polarity, name="cell_polarity", curie=VALUESETS.curie('cell_polarity'),
                   model_uri=VALUESETS.cell_polarity, domain=None, range=Optional[Union[str, "CellPolarity"]])

slots.crystal_system = Slot(uri=VALUESETS.crystal_system, name="crystal_system", curie=VALUESETS.curie('crystal_system'),
                   model_uri=VALUESETS.crystal_system, domain=None, range=Optional[Union[str, "CrystalSystemEnum"]])

slots.bravais_lattice = Slot(uri=VALUESETS.bravais_lattice, name="bravais_lattice", curie=VALUESETS.curie('bravais_lattice'),
                   model_uri=VALUESETS.bravais_lattice, domain=None, range=Optional[Union[str, "BravaisLatticeEnum"]])

slots.electrical_conductivity = Slot(uri=VALUESETS.electrical_conductivity, name="electrical_conductivity", curie=VALUESETS.curie('electrical_conductivity'),
                   model_uri=VALUESETS.electrical_conductivity, domain=None, range=Optional[Union[str, "ElectricalConductivityEnum"]])

slots.magnetic_property = Slot(uri=VALUESETS.magnetic_property, name="magnetic_property", curie=VALUESETS.curie('magnetic_property'),
                   model_uri=VALUESETS.magnetic_property, domain=None, range=Optional[Union[str, "MagneticPropertyEnum"]])

slots.optical_property = Slot(uri=VALUESETS.optical_property, name="optical_property", curie=VALUESETS.curie('optical_property'),
                   model_uri=VALUESETS.optical_property, domain=None, range=Optional[Union[str, "OpticalPropertyEnum"]])

slots.thermal_conductivity = Slot(uri=VALUESETS.thermal_conductivity, name="thermal_conductivity", curie=VALUESETS.curie('thermal_conductivity'),
                   model_uri=VALUESETS.thermal_conductivity, domain=None, range=Optional[Union[str, "ThermalConductivityEnum"]])

slots.mechanical_behavior = Slot(uri=VALUESETS.mechanical_behavior, name="mechanical_behavior", curie=VALUESETS.curie('mechanical_behavior'),
                   model_uri=VALUESETS.mechanical_behavior, domain=None, range=Optional[Union[str, "MechanicalBehaviorEnum"]])

slots.microscopy_method = Slot(uri=VALUESETS.microscopy_method, name="microscopy_method", curie=VALUESETS.curie('microscopy_method'),
                   model_uri=VALUESETS.microscopy_method, domain=None, range=Optional[Union[str, "MicroscopyMethodEnum"]])

slots.spectroscopy_method = Slot(uri=VALUESETS.spectroscopy_method, name="spectroscopy_method", curie=VALUESETS.curie('spectroscopy_method'),
                   model_uri=VALUESETS.spectroscopy_method, domain=None, range=Optional[Union[str, "SpectroscopyMethodEnum"]])

slots.thermal_analysis_method = Slot(uri=VALUESETS.thermal_analysis_method, name="thermal_analysis_method", curie=VALUESETS.curie('thermal_analysis_method'),
                   model_uri=VALUESETS.thermal_analysis_method, domain=None, range=Optional[Union[str, "ThermalAnalysisMethodEnum"]])

slots.mechanical_testing_method = Slot(uri=VALUESETS.mechanical_testing_method, name="mechanical_testing_method", curie=VALUESETS.curie('mechanical_testing_method'),
                   model_uri=VALUESETS.mechanical_testing_method, domain=None, range=Optional[Union[str, "MechanicalTestingMethodEnum"]])

slots.material_class = Slot(uri=VALUESETS.material_class, name="material_class", curie=VALUESETS.curie('material_class'),
                   model_uri=VALUESETS.material_class, domain=None, range=Optional[Union[str, "MaterialClassEnum"]])

slots.polymer_type = Slot(uri=VALUESETS.polymer_type, name="polymer_type", curie=VALUESETS.curie('polymer_type'),
                   model_uri=VALUESETS.polymer_type, domain=None, range=Optional[Union[str, "PolymerTypeEnum"]])

slots.metal_type = Slot(uri=VALUESETS.metal_type, name="metal_type", curie=VALUESETS.curie('metal_type'),
                   model_uri=VALUESETS.metal_type, domain=None, range=Optional[Union[str, "MetalTypeEnum"]])

slots.composite_type = Slot(uri=VALUESETS.composite_type, name="composite_type", curie=VALUESETS.curie('composite_type'),
                   model_uri=VALUESETS.composite_type, domain=None, range=Optional[Union[str, "CompositeTypeEnum"]])

slots.synthesis_method = Slot(uri=VALUESETS.synthesis_method, name="synthesis_method", curie=VALUESETS.curie('synthesis_method'),
                   model_uri=VALUESETS.synthesis_method, domain=None, range=Optional[Union[str, "SynthesisMethodEnum"]])

slots.crystal_growth_method = Slot(uri=VALUESETS.crystal_growth_method, name="crystal_growth_method", curie=VALUESETS.curie('crystal_growth_method'),
                   model_uri=VALUESETS.crystal_growth_method, domain=None, range=Optional[Union[str, "CrystalGrowthMethodEnum"]])

slots.additive_manufacturing = Slot(uri=VALUESETS.additive_manufacturing, name="additive_manufacturing", curie=VALUESETS.curie('additive_manufacturing'),
                   model_uri=VALUESETS.additive_manufacturing, domain=None, range=Optional[Union[str, "AdditiveManufacturingEnum"]])

slots.traditional_pigment = Slot(uri=VALUESETS.traditional_pigment, name="traditional_pigment", curie=VALUESETS.curie('traditional_pigment'),
                   model_uri=VALUESETS.traditional_pigment, domain=None, range=Optional[Union[str, "TraditionalPigmentEnum"]])

slots.industrial_dye = Slot(uri=VALUESETS.industrial_dye, name="industrial_dye", curie=VALUESETS.curie('industrial_dye'),
                   model_uri=VALUESETS.industrial_dye, domain=None, range=Optional[Union[str, "IndustrialDyeEnum"]])

slots.food_coloring = Slot(uri=VALUESETS.food_coloring, name="food_coloring", curie=VALUESETS.curie('food_coloring'),
                   model_uri=VALUESETS.food_coloring, domain=None, range=Optional[Union[str, "FoodColoringEnum"]])

slots.automobile_paint_color = Slot(uri=VALUESETS.automobile_paint_color, name="automobile_paint_color", curie=VALUESETS.curie('automobile_paint_color'),
                   model_uri=VALUESETS.automobile_paint_color, domain=None, range=Optional[Union[str, "AutomobilePaintColorEnum"]])

slots.basic_color = Slot(uri=VALUESETS.basic_color, name="basic_color", curie=VALUESETS.curie('basic_color'),
                   model_uri=VALUESETS.basic_color, domain=None, range=Optional[Union[str, "BasicColorEnum"]])

slots.web_color = Slot(uri=VALUESETS.web_color, name="web_color", curie=VALUESETS.curie('web_color'),
                   model_uri=VALUESETS.web_color, domain=None, range=Optional[Union[str, "WebColorEnum"]])

slots.x11_color = Slot(uri=VALUESETS.x11_color, name="x11_color", curie=VALUESETS.curie('x11_color'),
                   model_uri=VALUESETS.x11_color, domain=None, range=Optional[Union[str, "X11ColorEnum"]])

slots.color_space = Slot(uri=VALUESETS.color_space, name="color_space", curie=VALUESETS.curie('color_space'),
                   model_uri=VALUESETS.color_space, domain=None, range=Optional[Union[str, "ColorSpaceEnum"]])

slots.eye_color = Slot(uri=VALUESETS.eye_color, name="eye_color", curie=VALUESETS.curie('eye_color'),
                   model_uri=VALUESETS.eye_color, domain=None, range=Optional[Union[str, "EyeColorEnum"]])

slots.hair_color = Slot(uri=VALUESETS.hair_color, name="hair_color", curie=VALUESETS.curie('hair_color'),
                   model_uri=VALUESETS.hair_color, domain=None, range=Optional[Union[str, "HairColorEnum"]])

slots.flower_color = Slot(uri=VALUESETS.flower_color, name="flower_color", curie=VALUESETS.curie('flower_color'),
                   model_uri=VALUESETS.flower_color, domain=None, range=Optional[Union[str, "FlowerColorEnum"]])

slots.animal_coat_color = Slot(uri=VALUESETS.animal_coat_color, name="animal_coat_color", curie=VALUESETS.curie('animal_coat_color'),
                   model_uri=VALUESETS.animal_coat_color, domain=None, range=Optional[Union[str, "AnimalCoatColorEnum"]])

slots.skin_tone = Slot(uri=VALUESETS.skin_tone, name="skin_tone", curie=VALUESETS.curie('skin_tone'),
                   model_uri=VALUESETS.skin_tone, domain=None, range=Optional[Union[str, "SkinToneEnum"]])

slots.plant_leaf_color = Slot(uri=VALUESETS.plant_leaf_color, name="plant_leaf_color", curie=VALUESETS.curie('plant_leaf_color'),
                   model_uri=VALUESETS.plant_leaf_color, domain=None, range=Optional[Union[str, "PlantLeafColorEnum"]])

slots.dna_base = Slot(uri=VALUESETS.dna_base, name="dna_base", curie=VALUESETS.curie('dna_base'),
                   model_uri=VALUESETS.dna_base, domain=None, range=Optional[Union[str, "DNABaseEnum"]])

slots.dna_base_extended = Slot(uri=VALUESETS.dna_base_extended, name="dna_base_extended", curie=VALUESETS.curie('dna_base_extended'),
                   model_uri=VALUESETS.dna_base_extended, domain=None, range=Optional[Union[str, "DNABaseExtendedEnum"]])

slots.rna_base = Slot(uri=VALUESETS.rna_base, name="rna_base", curie=VALUESETS.curie('rna_base'),
                   model_uri=VALUESETS.rna_base, domain=None, range=Optional[Union[str, "RNABaseEnum"]])

slots.rna_base_extended = Slot(uri=VALUESETS.rna_base_extended, name="rna_base_extended", curie=VALUESETS.curie('rna_base_extended'),
                   model_uri=VALUESETS.rna_base_extended, domain=None, range=Optional[Union[str, "RNABaseExtendedEnum"]])

slots.amino_acid = Slot(uri=VALUESETS.amino_acid, name="amino_acid", curie=VALUESETS.curie('amino_acid'),
                   model_uri=VALUESETS.amino_acid, domain=None, range=Optional[Union[str, "AminoAcidEnum"]])

slots.amino_acid_extended = Slot(uri=VALUESETS.amino_acid_extended, name="amino_acid_extended", curie=VALUESETS.curie('amino_acid_extended'),
                   model_uri=VALUESETS.amino_acid_extended, domain=None, range=Optional[Union[str, "AminoAcidExtendedEnum"]])

slots.codon = Slot(uri=VALUESETS.codon, name="codon", curie=VALUESETS.curie('codon'),
                   model_uri=VALUESETS.codon, domain=None, range=Optional[Union[str, "CodonEnum"]])

slots.nucleotide_modification = Slot(uri=VALUESETS.nucleotide_modification, name="nucleotide_modification", curie=VALUESETS.curie('nucleotide_modification'),
                   model_uri=VALUESETS.nucleotide_modification, domain=None, range=Optional[Union[str, "NucleotideModificationEnum"]])

slots.sequence_quality = Slot(uri=VALUESETS.sequence_quality, name="sequence_quality", curie=VALUESETS.curie('sequence_quality'),
                   model_uri=VALUESETS.sequence_quality, domain=None, range=Optional[Union[str, "SequenceQualityEnum"]])

slots.iupac_nucleotide = Slot(uri=VALUESETS.iupac_nucleotide, name="iupac_nucleotide", curie=VALUESETS.curie('iupac_nucleotide'),
                   model_uri=VALUESETS.iupac_nucleotide, domain=None, range=Optional[Union[str, "IUPACNucleotideCode"]])

slots.standard_amino_acid = Slot(uri=VALUESETS.standard_amino_acid, name="standard_amino_acid", curie=VALUESETS.curie('standard_amino_acid'),
                   model_uri=VALUESETS.standard_amino_acid, domain=None, range=Optional[Union[str, "StandardAminoAcid"]])

slots.iupac_amino_acid = Slot(uri=VALUESETS.iupac_amino_acid, name="iupac_amino_acid", curie=VALUESETS.curie('iupac_amino_acid'),
                   model_uri=VALUESETS.iupac_amino_acid, domain=None, range=Optional[Union[str, "IUPACAminoAcidCode"]])

slots.sequence_alphabet = Slot(uri=VALUESETS.sequence_alphabet, name="sequence_alphabet", curie=VALUESETS.curie('sequence_alphabet'),
                   model_uri=VALUESETS.sequence_alphabet, domain=None, range=Optional[Union[str, "SequenceAlphabet"]])

slots.sequence_quality_encoding = Slot(uri=VALUESETS.sequence_quality_encoding, name="sequence_quality_encoding", curie=VALUESETS.curie('sequence_quality_encoding'),
                   model_uri=VALUESETS.sequence_quality_encoding, domain=None, range=Optional[Union[str, "SequenceQualityEncoding"]])

slots.genetic_code_table = Slot(uri=VALUESETS.genetic_code_table, name="genetic_code_table", curie=VALUESETS.curie('genetic_code_table'),
                   model_uri=VALUESETS.genetic_code_table, domain=None, range=Optional[Union[str, "GeneticCodeTable"]])

slots.sequence_strand = Slot(uri=VALUESETS.sequence_strand, name="sequence_strand", curie=VALUESETS.curie('sequence_strand'),
                   model_uri=VALUESETS.sequence_strand, domain=None, range=Optional[Union[str, "SequenceStrand"]])

slots.sequence_topology = Slot(uri=VALUESETS.sequence_topology, name="sequence_topology", curie=VALUESETS.curie('sequence_topology'),
                   model_uri=VALUESETS.sequence_topology, domain=None, range=Optional[Union[str, "SequenceTopology"]])

slots.sequence_modality = Slot(uri=VALUESETS.sequence_modality, name="sequence_modality", curie=VALUESETS.curie('sequence_modality'),
                   model_uri=VALUESETS.sequence_modality, domain=None, range=Optional[Union[str, "SequenceModality"]])

slots.sequencing_platform = Slot(uri=VALUESETS.sequencing_platform, name="sequencing_platform", curie=VALUESETS.curie('sequencing_platform'),
                   model_uri=VALUESETS.sequencing_platform, domain=None, range=Optional[Union[str, "SequencingPlatform"]])

slots.sequencing_chemistry = Slot(uri=VALUESETS.sequencing_chemistry, name="sequencing_chemistry", curie=VALUESETS.curie('sequencing_chemistry'),
                   model_uri=VALUESETS.sequencing_chemistry, domain=None, range=Optional[Union[str, "SequencingChemistry"]])

slots.library_preparation = Slot(uri=VALUESETS.library_preparation, name="library_preparation", curie=VALUESETS.curie('library_preparation'),
                   model_uri=VALUESETS.library_preparation, domain=None, range=Optional[Union[str, "LibraryPreparation"]])

slots.sequencing_application = Slot(uri=VALUESETS.sequencing_application, name="sequencing_application", curie=VALUESETS.curie('sequencing_application'),
                   model_uri=VALUESETS.sequencing_application, domain=None, range=Optional[Union[str, "SequencingApplication"]])

slots.read = Slot(uri=VALUESETS.read, name="read", curie=VALUESETS.curie('read'),
                   model_uri=VALUESETS.read, domain=None, range=Optional[Union[str, "ReadType"]])

slots.sequence_file_format = Slot(uri=VALUESETS.sequence_file_format, name="sequence_file_format", curie=VALUESETS.curie('sequence_file_format'),
                   model_uri=VALUESETS.sequence_file_format, domain=None, range=Optional[Union[str, "SequenceFileFormat"]])

slots.data_processing_level = Slot(uri=VALUESETS.data_processing_level, name="data_processing_level", curie=VALUESETS.curie('data_processing_level'),
                   model_uri=VALUESETS.data_processing_level, domain=None, range=Optional[Union[str, "DataProcessingLevel"]])

slots.cds_phase = Slot(uri=VALUESETS.cds_phase, name="cds_phase", curie=VALUESETS.curie('cds_phase'),
                   model_uri=VALUESETS.cds_phase, domain=None, range=Optional[Union[str, "CdsPhaseType"]])

slots.contig_collection = Slot(uri=VALUESETS.contig_collection, name="contig_collection", curie=VALUESETS.curie('contig_collection'),
                   model_uri=VALUESETS.contig_collection, domain=None, range=Optional[Union[str, "ContigCollectionType"]])

slots.strand = Slot(uri=VALUESETS.strand, name="strand", curie=VALUESETS.curie('strand'),
                   model_uri=VALUESETS.strand, domain=None, range=Optional[Union[str, "StrandType"]])

slots.sequence = Slot(uri=VALUESETS.sequence, name="sequence", curie=VALUESETS.curie('sequence'),
                   model_uri=VALUESETS.sequence, domain=None, range=Optional[Union[str, "SequenceType"]])

slots.protein_evidence_for_existence = Slot(uri=VALUESETS.protein_evidence_for_existence, name="protein_evidence_for_existence", curie=VALUESETS.curie('protein_evidence_for_existence'),
                   model_uri=VALUESETS.protein_evidence_for_existence, domain=None, range=Optional[Union[str, "ProteinEvidenceForExistence"]])

slots.ref_seq_status = Slot(uri=VALUESETS.ref_seq_status, name="ref_seq_status", curie=VALUESETS.curie('ref_seq_status'),
                   model_uri=VALUESETS.ref_seq_status, domain=None, range=Optional[Union[str, "RefSeqStatusType"]])

slots.currency_chemical = Slot(uri=VALUESETS.currency_chemical, name="currency_chemical", curie=VALUESETS.curie('currency_chemical'),
                   model_uri=VALUESETS.currency_chemical, domain=None, range=Optional[Union[str, "CurrencyChemical"]])

slots.plant_developmental_stage = Slot(uri=VALUESETS.plant_developmental_stage, name="plant_developmental_stage", curie=VALUESETS.curie('plant_developmental_stage'),
                   model_uri=VALUESETS.plant_developmental_stage, domain=None, range=Optional[Union[str, "PlantDevelopmentalStage"]])

slots.uni_prot_species = Slot(uri=VALUESETS.uni_prot_species, name="uni_prot_species", curie=VALUESETS.curie('uni_prot_species'),
                   model_uri=VALUESETS.uni_prot_species, domain=None, range=Optional[Union[str, "UniProtSpeciesCode"]])

slots.lipid_category = Slot(uri=VALUESETS.lipid_category, name="lipid_category", curie=VALUESETS.curie('lipid_category'),
                   model_uri=VALUESETS.lipid_category, domain=None, range=Optional[Union[str, "LipidCategory"]])

slots.peak_annotation_series_label = Slot(uri=VALUESETS.peak_annotation_series_label, name="peak_annotation_series_label", curie=VALUESETS.curie('peak_annotation_series_label'),
                   model_uri=VALUESETS.peak_annotation_series_label, domain=None, range=Optional[Union[str, "PeakAnnotationSeriesLabel"]])

slots.peptide_ion_series = Slot(uri=VALUESETS.peptide_ion_series, name="peptide_ion_series", curie=VALUESETS.curie('peptide_ion_series'),
                   model_uri=VALUESETS.peptide_ion_series, domain=None, range=Optional[Union[str, "PeptideIonSeries"]])

slots.mass_error_unit = Slot(uri=VALUESETS.mass_error_unit, name="mass_error_unit", curie=VALUESETS.curie('mass_error_unit'),
                   model_uri=VALUESETS.mass_error_unit, domain=None, range=Optional[Union[str, "MassErrorUnit"]])

slots.interaction_detection_method = Slot(uri=VALUESETS.interaction_detection_method, name="interaction_detection_method", curie=VALUESETS.curie('interaction_detection_method'),
                   model_uri=VALUESETS.interaction_detection_method, domain=None, range=Optional[Union[str, "InteractionDetectionMethod"]])

slots.interaction = Slot(uri=VALUESETS.interaction, name="interaction", curie=VALUESETS.curie('interaction'),
                   model_uri=VALUESETS.interaction, domain=None, range=Optional[Union[str, "InteractionType"]])

slots.experimental_role = Slot(uri=VALUESETS.experimental_role, name="experimental_role", curie=VALUESETS.curie('experimental_role'),
                   model_uri=VALUESETS.experimental_role, domain=None, range=Optional[Union[str, "ExperimentalRole"]])

slots.biological_role = Slot(uri=VALUESETS.biological_role, name="biological_role", curie=VALUESETS.curie('biological_role'),
                   model_uri=VALUESETS.biological_role, domain=None, range=Optional[Union[str, "BiologicalRole"]])

slots.participant_identification_method = Slot(uri=VALUESETS.participant_identification_method, name="participant_identification_method", curie=VALUESETS.curie('participant_identification_method'),
                   model_uri=VALUESETS.participant_identification_method, domain=None, range=Optional[Union[str, "ParticipantIdentificationMethod"]])

slots.feature = Slot(uri=VALUESETS.feature, name="feature", curie=VALUESETS.curie('feature'),
                   model_uri=VALUESETS.feature, domain=None, range=Optional[Union[Union[str, "FeatureType"], list[Union[str, "FeatureType"]]]])

slots.interactor = Slot(uri=VALUESETS.interactor, name="interactor", curie=VALUESETS.curie('interactor'),
                   model_uri=VALUESETS.interactor, domain=None, range=Optional[Union[str, "InteractorType"]])

slots.confidence_score = Slot(uri=VALUESETS.confidence_score, name="confidence_score", curie=VALUESETS.curie('confidence_score'),
                   model_uri=VALUESETS.confidence_score, domain=None, range=Optional[Union[str, "ConfidenceScore"]])

slots.experimental_preparation = Slot(uri=VALUESETS.experimental_preparation, name="experimental_preparation", curie=VALUESETS.curie('experimental_preparation'),
                   model_uri=VALUESETS.experimental_preparation, domain=None, range=Optional[Union[str, "ExperimentalPreparation"]])

slots.biotic_interaction = Slot(uri=VALUESETS.biotic_interaction, name="biotic_interaction", curie=VALUESETS.curie('biotic_interaction'),
                   model_uri=VALUESETS.biotic_interaction, domain=None, range=Optional[Union[str, "BioticInteractionType"]])

slots.mineralogy_feedstock = Slot(uri=VALUESETS.mineralogy_feedstock, name="mineralogy_feedstock", curie=VALUESETS.curie('mineralogy_feedstock'),
                   model_uri=VALUESETS.mineralogy_feedstock, domain=None, range=Union[str, "MineralogyFeedstockClass"])

slots.beneficiation_pathway = Slot(uri=VALUESETS.beneficiation_pathway, name="beneficiation_pathway", curie=VALUESETS.curie('beneficiation_pathway'),
                   model_uri=VALUESETS.beneficiation_pathway, domain=None, range=Optional[Union[str, "BeneficiationPathway"]])

slots.in_situ_chemistry_regime = Slot(uri=VALUESETS.in_situ_chemistry_regime, name="in_situ_chemistry_regime", curie=VALUESETS.curie('in_situ_chemistry_regime'),
                   model_uri=VALUESETS.in_situ_chemistry_regime, domain=None, range=Optional[Union[str, "InSituChemistryRegime"]])

slots.extractable_target_element = Slot(uri=VALUESETS.extractable_target_element, name="extractable_target_element", curie=VALUESETS.curie('extractable_target_element'),
                   model_uri=VALUESETS.extractable_target_element, domain=None, range=Optional[Union[Union[str, "ExtractableTargetElement"], list[Union[str, "ExtractableTargetElement"]]]])

slots.sensor_while_drilling_feature = Slot(uri=VALUESETS.sensor_while_drilling_feature, name="sensor_while_drilling_feature", curie=VALUESETS.curie('sensor_while_drilling_feature'),
                   model_uri=VALUESETS.sensor_while_drilling_feature, domain=None, range=Optional[Union[Union[str, "SensorWhileDrillingFeature"], list[Union[str, "SensorWhileDrillingFeature"]]]])

slots.process_performance_metric = Slot(uri=VALUESETS.process_performance_metric, name="process_performance_metric", curie=VALUESETS.curie('process_performance_metric'),
                   model_uri=VALUESETS.process_performance_metric, domain=None, range=Optional[Union[Union[str, "ProcessPerformanceMetric"], list[Union[str, "ProcessPerformanceMetric"]]]])

slots.bioleach_organism = Slot(uri=VALUESETS.bioleach_organism, name="bioleach_organism", curie=VALUESETS.curie('bioleach_organism'),
                   model_uri=VALUESETS.bioleach_organism, domain=None, range=Optional[Union[str, "BioleachOrganism"]])

slots.bioleach_mode = Slot(uri=VALUESETS.bioleach_mode, name="bioleach_mode", curie=VALUESETS.curie('bioleach_mode'),
                   model_uri=VALUESETS.bioleach_mode, domain=None, range=Optional[Union[str, "BioleachMode"]])

slots.autonomy_level = Slot(uri=VALUESETS.autonomy_level, name="autonomy_level", curie=VALUESETS.curie('autonomy_level'),
                   model_uri=VALUESETS.autonomy_level, domain=None, range=Optional[Union[str, "AutonomyLevel"]])

slots.regulatory_constraint = Slot(uri=VALUESETS.regulatory_constraint, name="regulatory_constraint", curie=VALUESETS.curie('regulatory_constraint'),
                   model_uri=VALUESETS.regulatory_constraint, domain=None, range=Optional[Union[Union[str, "RegulatoryConstraint"], list[Union[str, "RegulatoryConstraint"]]]])

slots.subatomic_particle = Slot(uri=VALUESETS.subatomic_particle, name="subatomic_particle", curie=VALUESETS.curie('subatomic_particle'),
                   model_uri=VALUESETS.subatomic_particle, domain=None, range=Optional[Union[str, "SubatomicParticleEnum"]])

slots.bond_type = Slot(uri=VALUESETS.bond_type, name="bond_type", curie=VALUESETS.curie('bond_type'),
                   model_uri=VALUESETS.bond_type, domain=None, range=Optional[Union[str, "BondTypeEnum"]])

slots.periodic_table_block = Slot(uri=VALUESETS.periodic_table_block, name="periodic_table_block", curie=VALUESETS.curie('periodic_table_block'),
                   model_uri=VALUESETS.periodic_table_block, domain=None, range=Optional[Union[str, "PeriodicTableBlockEnum"]])

slots.element_family = Slot(uri=VALUESETS.element_family, name="element_family", curie=VALUESETS.curie('element_family'),
                   model_uri=VALUESETS.element_family, domain=None, range=Optional[Union[str, "ElementFamilyEnum"]])

slots.element_metallic_classification = Slot(uri=VALUESETS.element_metallic_classification, name="element_metallic_classification", curie=VALUESETS.curie('element_metallic_classification'),
                   model_uri=VALUESETS.element_metallic_classification, domain=None, range=Optional[Union[str, "ElementMetallicClassificationEnum"]])

slots.hard_or_soft = Slot(uri=VALUESETS.hard_or_soft, name="hard_or_soft", curie=VALUESETS.curie('hard_or_soft'),
                   model_uri=VALUESETS.hard_or_soft, domain=None, range=Optional[Union[str, "HardOrSoftEnum"]])

slots.bronsted_acid_base_role = Slot(uri=VALUESETS.bronsted_acid_base_role, name="bronsted_acid_base_role", curie=VALUESETS.curie('bronsted_acid_base_role'),
                   model_uri=VALUESETS.bronsted_acid_base_role, domain=None, range=Optional[Union[str, "BronstedAcidBaseRoleEnum"]])

slots.lewis_acid_base_role = Slot(uri=VALUESETS.lewis_acid_base_role, name="lewis_acid_base_role", curie=VALUESETS.curie('lewis_acid_base_role'),
                   model_uri=VALUESETS.lewis_acid_base_role, domain=None, range=Optional[Union[str, "LewisAcidBaseRoleEnum"]])

slots.oxidation_state = Slot(uri=VALUESETS.oxidation_state, name="oxidation_state", curie=VALUESETS.curie('oxidation_state'),
                   model_uri=VALUESETS.oxidation_state, domain=None, range=Optional[Union[str, "OxidationStateEnum"]])

slots.chirality = Slot(uri=VALUESETS.chirality, name="chirality", curie=VALUESETS.curie('chirality'),
                   model_uri=VALUESETS.chirality, domain=None, range=Optional[Union[str, "ChiralityEnum"]])

slots.nanostructure_morphology = Slot(uri=VALUESETS.nanostructure_morphology, name="nanostructure_morphology", curie=VALUESETS.curie('nanostructure_morphology'),
                   model_uri=VALUESETS.nanostructure_morphology, domain=None, range=Optional[Union[str, "NanostructureMorphologyEnum"]])

slots.reaction_type = Slot(uri=VALUESETS.reaction_type, name="reaction_type", curie=VALUESETS.curie('reaction_type'),
                   model_uri=VALUESETS.reaction_type, domain=None, range=Optional[Union[str, "ReactionTypeEnum"]])

slots.reaction_mechanism = Slot(uri=VALUESETS.reaction_mechanism, name="reaction_mechanism", curie=VALUESETS.curie('reaction_mechanism'),
                   model_uri=VALUESETS.reaction_mechanism, domain=None, range=Optional[Union[str, "ReactionMechanismEnum"]])

slots.catalyst_type = Slot(uri=VALUESETS.catalyst_type, name="catalyst_type", curie=VALUESETS.curie('catalyst_type'),
                   model_uri=VALUESETS.catalyst_type, domain=None, range=Optional[Union[str, "CatalystTypeEnum"]])

slots.reaction_condition = Slot(uri=VALUESETS.reaction_condition, name="reaction_condition", curie=VALUESETS.curie('reaction_condition'),
                   model_uri=VALUESETS.reaction_condition, domain=None, range=Optional[Union[str, "ReactionConditionEnum"]])

slots.reaction_rate_order = Slot(uri=VALUESETS.reaction_rate_order, name="reaction_rate_order", curie=VALUESETS.curie('reaction_rate_order'),
                   model_uri=VALUESETS.reaction_rate_order, domain=None, range=Optional[Union[str, "ReactionRateOrderEnum"]])

slots.enzyme_class = Slot(uri=VALUESETS.enzyme_class, name="enzyme_class", curie=VALUESETS.curie('enzyme_class'),
                   model_uri=VALUESETS.enzyme_class, domain=None, range=Optional[Union[str, "EnzymeClassEnum"]])

slots.solvent_class = Slot(uri=VALUESETS.solvent_class, name="solvent_class", curie=VALUESETS.curie('solvent_class'),
                   model_uri=VALUESETS.solvent_class, domain=None, range=Optional[Union[str, "SolventClassEnum"]])

slots.thermodynamic_parameter = Slot(uri=VALUESETS.thermodynamic_parameter, name="thermodynamic_parameter", curie=VALUESETS.curie('thermodynamic_parameter'),
                   model_uri=VALUESETS.thermodynamic_parameter, domain=None, range=Optional[Union[str, "ThermodynamicParameterEnum"]])

slots.reaction_directionality = Slot(uri=VALUESETS.reaction_directionality, name="reaction_directionality", curie=VALUESETS.curie('reaction_directionality'),
                   model_uri=VALUESETS.reaction_directionality, domain=None, range=Optional[Union[str, "ReactionDirectionality"]])

slots.safety_color = Slot(uri=VALUESETS.safety_color, name="safety_color", curie=VALUESETS.curie('safety_color'),
                   model_uri=VALUESETS.safety_color, domain=None, range=Optional[Union[str, "SafetyColorEnum"]])

slots.traffic_light_color = Slot(uri=VALUESETS.traffic_light_color, name="traffic_light_color", curie=VALUESETS.curie('traffic_light_color'),
                   model_uri=VALUESETS.traffic_light_color, domain=None, range=Optional[Union[str, "TrafficLightColorEnum"]])

slots.hazmat_color = Slot(uri=VALUESETS.hazmat_color, name="hazmat_color", curie=VALUESETS.curie('hazmat_color'),
                   model_uri=VALUESETS.hazmat_color, domain=None, range=Optional[Union[str, "HazmatColorEnum"]])

slots.fire_safety_color = Slot(uri=VALUESETS.fire_safety_color, name="fire_safety_color", curie=VALUESETS.curie('fire_safety_color'),
                   model_uri=VALUESETS.fire_safety_color, domain=None, range=Optional[Union[str, "FireSafetyColorEnum"]])

slots.maritime_signal_color = Slot(uri=VALUESETS.maritime_signal_color, name="maritime_signal_color", curie=VALUESETS.curie('maritime_signal_color'),
                   model_uri=VALUESETS.maritime_signal_color, domain=None, range=Optional[Union[str, "MaritimeSignalColorEnum"]])

slots.aviation_light_color = Slot(uri=VALUESETS.aviation_light_color, name="aviation_light_color", curie=VALUESETS.curie('aviation_light_color'),
                   model_uri=VALUESETS.aviation_light_color, domain=None, range=Optional[Union[str, "AviationLightColorEnum"]])

slots.electrical_wire_color = Slot(uri=VALUESETS.electrical_wire_color, name="electrical_wire_color", curie=VALUESETS.curie('electrical_wire_color'),
                   model_uri=VALUESETS.electrical_wire_color, domain=None, range=Optional[Union[str, "ElectricalWireColorEnum"]])

slots.blood_type = Slot(uri=VALUESETS.blood_type, name="blood_type", curie=VALUESETS.curie('blood_type'),
                   model_uri=VALUESETS.blood_type, domain=None, range=Optional[Union[str, "BloodTypeEnum"]])

slots.anatomical_system = Slot(uri=VALUESETS.anatomical_system, name="anatomical_system", curie=VALUESETS.curie('anatomical_system'),
                   model_uri=VALUESETS.anatomical_system, domain=None, range=Optional[Union[str, "AnatomicalSystemEnum"]])

slots.medical_specialty = Slot(uri=VALUESETS.medical_specialty, name="medical_specialty", curie=VALUESETS.curie('medical_specialty'),
                   model_uri=VALUESETS.medical_specialty, domain=None, range=Optional[Union[str, "MedicalSpecialtyEnum"]])

slots.drug_route = Slot(uri=VALUESETS.drug_route, name="drug_route", curie=VALUESETS.curie('drug_route'),
                   model_uri=VALUESETS.drug_route, domain=None, range=Optional[Union[str, "DrugRouteEnum"]])

slots.vital_sign = Slot(uri=VALUESETS.vital_sign, name="vital_sign", curie=VALUESETS.curie('vital_sign'),
                   model_uri=VALUESETS.vital_sign, domain=None, range=Optional[Union[str, "VitalSignEnum"]])

slots.diagnostic_test_type = Slot(uri=VALUESETS.diagnostic_test_type, name="diagnostic_test_type", curie=VALUESETS.curie('diagnostic_test_type'),
                   model_uri=VALUESETS.diagnostic_test_type, domain=None, range=Optional[Union[str, "DiagnosticTestTypeEnum"]])

slots.symptom_severity = Slot(uri=VALUESETS.symptom_severity, name="symptom_severity", curie=VALUESETS.curie('symptom_severity'),
                   model_uri=VALUESETS.symptom_severity, domain=None, range=Optional[Union[str, "SymptomSeverityEnum"]])

slots.allergy_type = Slot(uri=VALUESETS.allergy_type, name="allergy_type", curie=VALUESETS.curie('allergy_type'),
                   model_uri=VALUESETS.allergy_type, domain=None, range=Optional[Union[str, "AllergyTypeEnum"]])

slots.vaccine_type = Slot(uri=VALUESETS.vaccine_type, name="vaccine_type", curie=VALUESETS.curie('vaccine_type'),
                   model_uri=VALUESETS.vaccine_type, domain=None, range=Optional[Union[str, "VaccineTypeEnum"]])

slots.bmi_classification = Slot(uri=VALUESETS.bmi_classification, name="bmi_classification", curie=VALUESETS.curie('bmi_classification'),
                   model_uri=VALUESETS.bmi_classification, domain=None, range=Optional[Union[str, "BMIClassificationEnum"]])

slots.mri_modality = Slot(uri=VALUESETS.mri_modality, name="mri_modality", curie=VALUESETS.curie('mri_modality'),
                   model_uri=VALUESETS.mri_modality, domain=None, range=Optional[Union[str, "MRIModalityEnum"]])

slots.mri_sequence_type = Slot(uri=VALUESETS.mri_sequence_type, name="mri_sequence_type", curie=VALUESETS.curie('mri_sequence_type'),
                   model_uri=VALUESETS.mri_sequence_type, domain=None, range=Optional[Union[str, "MRISequenceTypeEnum"]])

slots.mri_contrast_type = Slot(uri=VALUESETS.mri_contrast_type, name="mri_contrast_type", curie=VALUESETS.curie('mri_contrast_type'),
                   model_uri=VALUESETS.mri_contrast_type, domain=None, range=Optional[Union[str, "MRIContrastTypeEnum"]])

slots.fmri_paradigm_type = Slot(uri=VALUESETS.fmri_paradigm_type, name="fmri_paradigm_type", curie=VALUESETS.curie('fmri_paradigm_type'),
                   model_uri=VALUESETS.fmri_paradigm_type, domain=None, range=Optional[Union[str, "FMRIParadigmTypeEnum"]])

slots.race_omb1997 = Slot(uri=VALUESETS.race_omb1997, name="race_omb1997", curie=VALUESETS.curie('race_omb1997'),
                   model_uri=VALUESETS.race_omb1997, domain=None, range=Optional[Union[str, "RaceOMB1997Enum"]])

slots.ethnicity_omb1997 = Slot(uri=VALUESETS.ethnicity_omb1997, name="ethnicity_omb1997", curie=VALUESETS.curie('ethnicity_omb1997'),
                   model_uri=VALUESETS.ethnicity_omb1997, domain=None, range=Optional[Union[str, "EthnicityOMB1997Enum"]])

slots.biological_sex = Slot(uri=VALUESETS.biological_sex, name="biological_sex", curie=VALUESETS.curie('biological_sex'),
                   model_uri=VALUESETS.biological_sex, domain=None, range=Optional[Union[str, "BiologicalSexEnum"]])

slots.age_group = Slot(uri=VALUESETS.age_group, name="age_group", curie=VALUESETS.curie('age_group'),
                   model_uri=VALUESETS.age_group, domain=None, range=Optional[Union[str, "AgeGroupEnum"]])

slots.participant_vital_status = Slot(uri=VALUESETS.participant_vital_status, name="participant_vital_status", curie=VALUESETS.curie('participant_vital_status'),
                   model_uri=VALUESETS.participant_vital_status, domain=None, range=Optional[Union[str, "ParticipantVitalStatusEnum"]])

slots.recruitment_status = Slot(uri=VALUESETS.recruitment_status, name="recruitment_status", curie=VALUESETS.curie('recruitment_status'),
                   model_uri=VALUESETS.recruitment_status, domain=None, range=Optional[Union[str, "RecruitmentStatusEnum"]])

slots.study_phase = Slot(uri=VALUESETS.study_phase, name="study_phase", curie=VALUESETS.curie('study_phase'),
                   model_uri=VALUESETS.study_phase, domain=None, range=Optional[Union[str, "StudyPhaseEnum"]])

slots.karyotypic_sex = Slot(uri=VALUESETS.karyotypic_sex, name="karyotypic_sex", curie=VALUESETS.curie('karyotypic_sex'),
                   model_uri=VALUESETS.karyotypic_sex, domain=None, range=Optional[Union[str, "KaryotypicSexEnum"]])

slots.phenotypic_sex = Slot(uri=VALUESETS.phenotypic_sex, name="phenotypic_sex", curie=VALUESETS.curie('phenotypic_sex'),
                   model_uri=VALUESETS.phenotypic_sex, domain=None, range=Optional[Union[str, "PhenotypicSexEnum"]])

slots.allelic_state = Slot(uri=VALUESETS.allelic_state, name="allelic_state", curie=VALUESETS.curie('allelic_state'),
                   model_uri=VALUESETS.allelic_state, domain=None, range=Optional[Union[str, "AllelicStateEnum"]])

slots.laterality = Slot(uri=VALUESETS.laterality, name="laterality", curie=VALUESETS.curie('laterality'),
                   model_uri=VALUESETS.laterality, domain=None, range=Optional[Union[str, "LateralityEnum"]])

slots.onset_timing = Slot(uri=VALUESETS.onset_timing, name="onset_timing", curie=VALUESETS.curie('onset_timing'),
                   model_uri=VALUESETS.onset_timing, domain=None, range=Optional[Union[str, "OnsetTimingEnum"]])

slots.acmg_pathogenicity = Slot(uri=VALUESETS.acmg_pathogenicity, name="acmg_pathogenicity", curie=VALUESETS.curie('acmg_pathogenicity'),
                   model_uri=VALUESETS.acmg_pathogenicity, domain=None, range=Optional[Union[str, "ACMGPathogenicityEnum"]])

slots.therapeutic_actionability = Slot(uri=VALUESETS.therapeutic_actionability, name="therapeutic_actionability", curie=VALUESETS.curie('therapeutic_actionability'),
                   model_uri=VALUESETS.therapeutic_actionability, domain=None, range=Optional[Union[str, "TherapeuticActionabilityEnum"]])

slots.interpretation_progress = Slot(uri=VALUESETS.interpretation_progress, name="interpretation_progress", curie=VALUESETS.curie('interpretation_progress'),
                   model_uri=VALUESETS.interpretation_progress, domain=None, range=Optional[Union[str, "InterpretationProgressEnum"]])

slots.regimen_status = Slot(uri=VALUESETS.regimen_status, name="regimen_status", curie=VALUESETS.curie('regimen_status'),
                   model_uri=VALUESETS.regimen_status, domain=None, range=Optional[Union[str, "RegimenStatusEnum"]])

slots.drug_response = Slot(uri=VALUESETS.drug_response, name="drug_response", curie=VALUESETS.curie('drug_response'),
                   model_uri=VALUESETS.drug_response, domain=None, range=Optional[Union[str, "DrugResponseEnum"]])

slots.process_scale = Slot(uri=VALUESETS.process_scale, name="process_scale", curie=VALUESETS.curie('process_scale'),
                   model_uri=VALUESETS.process_scale, domain=None, range=Optional[Union[str, "ProcessScaleEnum"]])

slots.bioreactor_type = Slot(uri=VALUESETS.bioreactor_type, name="bioreactor_type", curie=VALUESETS.curie('bioreactor_type'),
                   model_uri=VALUESETS.bioreactor_type, domain=None, range=Optional[Union[str, "BioreactorTypeEnum"]])

slots.fermentation_mode = Slot(uri=VALUESETS.fermentation_mode, name="fermentation_mode", curie=VALUESETS.curie('fermentation_mode'),
                   model_uri=VALUESETS.fermentation_mode, domain=None, range=Optional[Union[str, "FermentationModeEnum"]])

slots.oxygenation_strategy = Slot(uri=VALUESETS.oxygenation_strategy, name="oxygenation_strategy", curie=VALUESETS.curie('oxygenation_strategy'),
                   model_uri=VALUESETS.oxygenation_strategy, domain=None, range=Optional[Union[str, "OxygenationStrategyEnum"]])

slots.agitation_type = Slot(uri=VALUESETS.agitation_type, name="agitation_type", curie=VALUESETS.curie('agitation_type'),
                   model_uri=VALUESETS.agitation_type, domain=None, range=Optional[Union[str, "AgitationTypeEnum"]])

slots.downstream_process = Slot(uri=VALUESETS.downstream_process, name="downstream_process", curie=VALUESETS.curie('downstream_process'),
                   model_uri=VALUESETS.downstream_process, domain=None, range=Optional[Union[str, "DownstreamProcessEnum"]])

slots.feedstock_type = Slot(uri=VALUESETS.feedstock_type, name="feedstock_type", curie=VALUESETS.curie('feedstock_type'),
                   model_uri=VALUESETS.feedstock_type, domain=None, range=Optional[Union[str, "FeedstockTypeEnum"]])

slots.product_type = Slot(uri=VALUESETS.product_type, name="product_type", curie=VALUESETS.curie('product_type'),
                   model_uri=VALUESETS.product_type, domain=None, range=Optional[Union[str, "ProductTypeEnum"]])

slots.sterilization_method = Slot(uri=VALUESETS.sterilization_method, name="sterilization_method", curie=VALUESETS.curie('sterilization_method'),
                   model_uri=VALUESETS.sterilization_method, domain=None, range=Optional[Union[str, "SterilizationMethodEnum"]])

slots.length_unit = Slot(uri=VALUESETS.length_unit, name="length_unit", curie=VALUESETS.curie('length_unit'),
                   model_uri=VALUESETS.length_unit, domain=None, range=Optional[Union[str, "LengthUnitEnum"]])

slots.mass_unit = Slot(uri=VALUESETS.mass_unit, name="mass_unit", curie=VALUESETS.curie('mass_unit'),
                   model_uri=VALUESETS.mass_unit, domain=None, range=Optional[Union[str, "MassUnitEnum"]])

slots.volume_unit = Slot(uri=VALUESETS.volume_unit, name="volume_unit", curie=VALUESETS.curie('volume_unit'),
                   model_uri=VALUESETS.volume_unit, domain=None, range=Optional[Union[str, "VolumeUnitEnum"]])

slots.temperature_unit = Slot(uri=VALUESETS.temperature_unit, name="temperature_unit", curie=VALUESETS.curie('temperature_unit'),
                   model_uri=VALUESETS.temperature_unit, domain=None, range=Optional[Union[str, "TemperatureUnitEnum"]])

slots.time_unit = Slot(uri=VALUESETS.time_unit, name="time_unit", curie=VALUESETS.curie('time_unit'),
                   model_uri=VALUESETS.time_unit, domain=None, range=Optional[Union[str, "TimeUnitEnum"]])

slots.pressure_unit = Slot(uri=VALUESETS.pressure_unit, name="pressure_unit", curie=VALUESETS.curie('pressure_unit'),
                   model_uri=VALUESETS.pressure_unit, domain=None, range=Optional[Union[str, "PressureUnitEnum"]])

slots.concentration_unit = Slot(uri=VALUESETS.concentration_unit, name="concentration_unit", curie=VALUESETS.curie('concentration_unit'),
                   model_uri=VALUESETS.concentration_unit, domain=None, range=Optional[Union[str, "ConcentrationUnitEnum"]])

slots.frequency_unit = Slot(uri=VALUESETS.frequency_unit, name="frequency_unit", curie=VALUESETS.curie('frequency_unit'),
                   model_uri=VALUESETS.frequency_unit, domain=None, range=Optional[Union[str, "FrequencyUnitEnum"]])

slots.angle_unit = Slot(uri=VALUESETS.angle_unit, name="angle_unit", curie=VALUESETS.curie('angle_unit'),
                   model_uri=VALUESETS.angle_unit, domain=None, range=Optional[Union[str, "AngleUnitEnum"]])

slots.data_size_unit = Slot(uri=VALUESETS.data_size_unit, name="data_size_unit", curie=VALUESETS.curie('data_size_unit'),
                   model_uri=VALUESETS.data_size_unit, domain=None, range=Optional[Union[str, "DataSizeUnitEnum"]])

slots.image_file_format = Slot(uri=VALUESETS.image_file_format, name="image_file_format", curie=VALUESETS.curie('image_file_format'),
                   model_uri=VALUESETS.image_file_format, domain=None, range=Optional[Union[str, "ImageFileFormatEnum"]])

slots.document_format = Slot(uri=VALUESETS.document_format, name="document_format", curie=VALUESETS.curie('document_format'),
                   model_uri=VALUESETS.document_format, domain=None, range=Optional[Union[str, "DocumentFormatEnum"]])

slots.data_format = Slot(uri=VALUESETS.data_format, name="data_format", curie=VALUESETS.curie('data_format'),
                   model_uri=VALUESETS.data_format, domain=None, range=Optional[Union[str, "DataFormatEnum"]])

slots.archive_format = Slot(uri=VALUESETS.archive_format, name="archive_format", curie=VALUESETS.curie('archive_format'),
                   model_uri=VALUESETS.archive_format, domain=None, range=Optional[Union[str, "ArchiveFormatEnum"]])

slots.video_format = Slot(uri=VALUESETS.video_format, name="video_format", curie=VALUESETS.curie('video_format'),
                   model_uri=VALUESETS.video_format, domain=None, range=Optional[Union[str, "VideoFormatEnum"]])

slots.audio_format = Slot(uri=VALUESETS.audio_format, name="audio_format", curie=VALUESETS.curie('audio_format'),
                   model_uri=VALUESETS.audio_format, domain=None, range=Optional[Union[str, "AudioFormatEnum"]])

slots.programming_language_file = Slot(uri=VALUESETS.programming_language_file, name="programming_language_file", curie=VALUESETS.curie('programming_language_file'),
                   model_uri=VALUESETS.programming_language_file, domain=None, range=Optional[Union[str, "ProgrammingLanguageFileEnum"]])

slots.network_protocol = Slot(uri=VALUESETS.network_protocol, name="network_protocol", curie=VALUESETS.curie('network_protocol'),
                   model_uri=VALUESETS.network_protocol, domain=None, range=Optional[Union[str, "NetworkProtocolEnum"]])

slots.technology_readiness_level = Slot(uri=VALUESETS.technology_readiness_level, name="technology_readiness_level", curie=VALUESETS.curie('technology_readiness_level'),
                   model_uri=VALUESETS.technology_readiness_level, domain=None, range=Optional[Union[str, "TechnologyReadinessLevel"]])

slots.software_maturity_level = Slot(uri=VALUESETS.software_maturity_level, name="software_maturity_level", curie=VALUESETS.curie('software_maturity_level'),
                   model_uri=VALUESETS.software_maturity_level, domain=None, range=Optional[Union[str, "SoftwareMaturityLevel"]])

slots.capability_maturity_level = Slot(uri=VALUESETS.capability_maturity_level, name="capability_maturity_level", curie=VALUESETS.curie('capability_maturity_level'),
                   model_uri=VALUESETS.capability_maturity_level, domain=None, range=Optional[Union[str, "CapabilityMaturityLevel"]])

slots.standards_maturity_level = Slot(uri=VALUESETS.standards_maturity_level, name="standards_maturity_level", curie=VALUESETS.curie('standards_maturity_level'),
                   model_uri=VALUESETS.standards_maturity_level, domain=None, range=Optional[Union[str, "StandardsMaturityLevel"]])

slots.project_maturity_level = Slot(uri=VALUESETS.project_maturity_level, name="project_maturity_level", curie=VALUESETS.curie('project_maturity_level'),
                   model_uri=VALUESETS.project_maturity_level, domain=None, range=Optional[Union[str, "ProjectMaturityLevel"]])

slots.data_maturity_level = Slot(uri=VALUESETS.data_maturity_level, name="data_maturity_level", curie=VALUESETS.curie('data_maturity_level'),
                   model_uri=VALUESETS.data_maturity_level, domain=None, range=Optional[Union[str, "DataMaturityLevel"]])

slots.open_source_maturity_level = Slot(uri=VALUESETS.open_source_maturity_level, name="open_source_maturity_level", curie=VALUESETS.curie('open_source_maturity_level'),
                   model_uri=VALUESETS.open_source_maturity_level, domain=None, range=Optional[Union[str, "OpenSourceMaturityLevel"]])

slots.legal_entity_type = Slot(uri=VALUESETS.legal_entity_type, name="legal_entity_type", curie=VALUESETS.curie('legal_entity_type'),
                   model_uri=VALUESETS.legal_entity_type, domain=None, range=Optional[Union[str, "LegalEntityTypeEnum"]])

slots.organizational_structure = Slot(uri=VALUESETS.organizational_structure, name="organizational_structure", curie=VALUESETS.curie('organizational_structure'),
                   model_uri=VALUESETS.organizational_structure, domain=None, range=Optional[Union[str, "OrganizationalStructureEnum"]])

slots.management_level = Slot(uri=VALUESETS.management_level, name="management_level", curie=VALUESETS.curie('management_level'),
                   model_uri=VALUESETS.management_level, domain=None, range=Optional[Union[str, "ManagementLevelEnum"]])

slots.corporate_governance_role = Slot(uri=VALUESETS.corporate_governance_role, name="corporate_governance_role", curie=VALUESETS.curie('corporate_governance_role'),
                   model_uri=VALUESETS.corporate_governance_role, domain=None, range=Optional[Union[str, "CorporateGovernanceRoleEnum"]])

slots.business_ownership_type = Slot(uri=VALUESETS.business_ownership_type, name="business_ownership_type", curie=VALUESETS.curie('business_ownership_type'),
                   model_uri=VALUESETS.business_ownership_type, domain=None, range=Optional[Union[str, "BusinessOwnershipTypeEnum"]])

slots.business_size_classification = Slot(uri=VALUESETS.business_size_classification, name="business_size_classification", curie=VALUESETS.curie('business_size_classification'),
                   model_uri=VALUESETS.business_size_classification, domain=None, range=Optional[Union[str, "BusinessSizeClassificationEnum"]])

slots.business_lifecycle_stage = Slot(uri=VALUESETS.business_lifecycle_stage, name="business_lifecycle_stage", curie=VALUESETS.curie('business_lifecycle_stage'),
                   model_uri=VALUESETS.business_lifecycle_stage, domain=None, range=Optional[Union[str, "BusinessLifecycleStageEnum"]])

slots.naics_sector = Slot(uri=VALUESETS.naics_sector, name="naics_sector", curie=VALUESETS.curie('naics_sector'),
                   model_uri=VALUESETS.naics_sector, domain=None, range=Optional[Union[str, "NAICSSectorEnum"]])

slots.economic_sector = Slot(uri=VALUESETS.economic_sector, name="economic_sector", curie=VALUESETS.curie('economic_sector'),
                   model_uri=VALUESETS.economic_sector, domain=None, range=Optional[Union[str, "EconomicSectorEnum"]])

slots.business_activity_type = Slot(uri=VALUESETS.business_activity_type, name="business_activity_type", curie=VALUESETS.curie('business_activity_type'),
                   model_uri=VALUESETS.business_activity_type, domain=None, range=Optional[Union[str, "BusinessActivityTypeEnum"]])

slots.industry_maturity = Slot(uri=VALUESETS.industry_maturity, name="industry_maturity", curie=VALUESETS.curie('industry_maturity'),
                   model_uri=VALUESETS.industry_maturity, domain=None, range=Optional[Union[str, "IndustryMaturityEnum"]])

slots.market_structure = Slot(uri=VALUESETS.market_structure, name="market_structure", curie=VALUESETS.curie('market_structure'),
                   model_uri=VALUESETS.market_structure, domain=None, range=Optional[Union[str, "MarketStructureEnum"]])

slots.industry_regulation_level = Slot(uri=VALUESETS.industry_regulation_level, name="industry_regulation_level", curie=VALUESETS.curie('industry_regulation_level'),
                   model_uri=VALUESETS.industry_regulation_level, domain=None, range=Optional[Union[str, "IndustryRegulationLevelEnum"]])

slots.management_methodology = Slot(uri=VALUESETS.management_methodology, name="management_methodology", curie=VALUESETS.curie('management_methodology'),
                   model_uri=VALUESETS.management_methodology, domain=None, range=Optional[Union[str, "ManagementMethodologyEnum"]])

slots.strategic_framework = Slot(uri=VALUESETS.strategic_framework, name="strategic_framework", curie=VALUESETS.curie('strategic_framework'),
                   model_uri=VALUESETS.strategic_framework, domain=None, range=Optional[Union[str, "StrategicFrameworkEnum"]])

slots.operational_model = Slot(uri=VALUESETS.operational_model, name="operational_model", curie=VALUESETS.curie('operational_model'),
                   model_uri=VALUESETS.operational_model, domain=None, range=Optional[Union[str, "OperationalModelEnum"]])

slots.performance_measurement = Slot(uri=VALUESETS.performance_measurement, name="performance_measurement", curie=VALUESETS.curie('performance_measurement'),
                   model_uri=VALUESETS.performance_measurement, domain=None, range=Optional[Union[str, "PerformanceMeasurementEnum"]])

slots.decision_making_style = Slot(uri=VALUESETS.decision_making_style, name="decision_making_style", curie=VALUESETS.curie('decision_making_style'),
                   model_uri=VALUESETS.decision_making_style, domain=None, range=Optional[Union[str, "DecisionMakingStyleEnum"]])

slots.leadership_style = Slot(uri=VALUESETS.leadership_style, name="leadership_style", curie=VALUESETS.curie('leadership_style'),
                   model_uri=VALUESETS.leadership_style, domain=None, range=Optional[Union[str, "LeadershipStyleEnum"]])

slots.business_process_type = Slot(uri=VALUESETS.business_process_type, name="business_process_type", curie=VALUESETS.curie('business_process_type'),
                   model_uri=VALUESETS.business_process_type, domain=None, range=Optional[Union[str, "BusinessProcessTypeEnum"]])

slots.quality_standard = Slot(uri=VALUESETS.quality_standard, name="quality_standard", curie=VALUESETS.curie('quality_standard'),
                   model_uri=VALUESETS.quality_standard, domain=None, range=Optional[Union[str, "QualityStandardEnum"]])

slots.quality_methodology = Slot(uri=VALUESETS.quality_methodology, name="quality_methodology", curie=VALUESETS.curie('quality_methodology'),
                   model_uri=VALUESETS.quality_methodology, domain=None, range=Optional[Union[str, "QualityMethodologyEnum"]])

slots.quality_control_technique = Slot(uri=VALUESETS.quality_control_technique, name="quality_control_technique", curie=VALUESETS.curie('quality_control_technique'),
                   model_uri=VALUESETS.quality_control_technique, domain=None, range=Optional[Union[str, "QualityControlTechniqueEnum"]])

slots.quality_assurance_level = Slot(uri=VALUESETS.quality_assurance_level, name="quality_assurance_level", curie=VALUESETS.curie('quality_assurance_level'),
                   model_uri=VALUESETS.quality_assurance_level, domain=None, range=Optional[Union[str, "QualityAssuranceLevelEnum"]])

slots.process_improvement_approach = Slot(uri=VALUESETS.process_improvement_approach, name="process_improvement_approach", curie=VALUESETS.curie('process_improvement_approach'),
                   model_uri=VALUESETS.process_improvement_approach, domain=None, range=Optional[Union[str, "ProcessImprovementApproachEnum"]])

slots.quality_maturity_level = Slot(uri=VALUESETS.quality_maturity_level, name="quality_maturity_level", curie=VALUESETS.curie('quality_maturity_level'),
                   model_uri=VALUESETS.quality_maturity_level, domain=None, range=Optional[Union[str, "QualityMaturityLevelEnum"]])

slots.procurement_type = Slot(uri=VALUESETS.procurement_type, name="procurement_type", curie=VALUESETS.curie('procurement_type'),
                   model_uri=VALUESETS.procurement_type, domain=None, range=Optional[Union[str, "ProcurementTypeEnum"]])

slots.vendor_category = Slot(uri=VALUESETS.vendor_category, name="vendor_category", curie=VALUESETS.curie('vendor_category'),
                   model_uri=VALUESETS.vendor_category, domain=None, range=Optional[Union[str, "VendorCategoryEnum"]])

slots.supply_chain_strategy = Slot(uri=VALUESETS.supply_chain_strategy, name="supply_chain_strategy", curie=VALUESETS.curie('supply_chain_strategy'),
                   model_uri=VALUESETS.supply_chain_strategy, domain=None, range=Optional[Union[str, "SupplyChainStrategyEnum"]])

slots.logistics_operation = Slot(uri=VALUESETS.logistics_operation, name="logistics_operation", curie=VALUESETS.curie('logistics_operation'),
                   model_uri=VALUESETS.logistics_operation, domain=None, range=Optional[Union[str, "LogisticsOperationEnum"]])

slots.sourcing_strategy = Slot(uri=VALUESETS.sourcing_strategy, name="sourcing_strategy", curie=VALUESETS.curie('sourcing_strategy'),
                   model_uri=VALUESETS.sourcing_strategy, domain=None, range=Optional[Union[str, "SourcingStrategyEnum"]])

slots.supplier_relationship_type = Slot(uri=VALUESETS.supplier_relationship_type, name="supplier_relationship_type", curie=VALUESETS.curie('supplier_relationship_type'),
                   model_uri=VALUESETS.supplier_relationship_type, domain=None, range=Optional[Union[str, "SupplierRelationshipTypeEnum"]])

slots.inventory_management_approach = Slot(uri=VALUESETS.inventory_management_approach, name="inventory_management_approach", curie=VALUESETS.curie('inventory_management_approach'),
                   model_uri=VALUESETS.inventory_management_approach, domain=None, range=Optional[Union[str, "InventoryManagementApproachEnum"]])

slots.employment_type = Slot(uri=VALUESETS.employment_type, name="employment_type", curie=VALUESETS.curie('employment_type'),
                   model_uri=VALUESETS.employment_type, domain=None, range=Optional[Union[str, "EmploymentTypeEnum"]])

slots.job_level = Slot(uri=VALUESETS.job_level, name="job_level", curie=VALUESETS.curie('job_level'),
                   model_uri=VALUESETS.job_level, domain=None, range=Optional[Union[str, "JobLevelEnum"]])

slots.hr_function = Slot(uri=VALUESETS.hr_function, name="hr_function", curie=VALUESETS.curie('hr_function'),
                   model_uri=VALUESETS.hr_function, domain=None, range=Optional[Union[str, "HRFunctionEnum"]])

slots.compensation_type = Slot(uri=VALUESETS.compensation_type, name="compensation_type", curie=VALUESETS.curie('compensation_type'),
                   model_uri=VALUESETS.compensation_type, domain=None, range=Optional[Union[str, "CompensationTypeEnum"]])

slots.performance_rating = Slot(uri=VALUESETS.performance_rating, name="performance_rating", curie=VALUESETS.curie('performance_rating'),
                   model_uri=VALUESETS.performance_rating, domain=None, range=Optional[Union[str, "PerformanceRatingEnum"]])

slots.recruitment_source = Slot(uri=VALUESETS.recruitment_source, name="recruitment_source", curie=VALUESETS.curie('recruitment_source'),
                   model_uri=VALUESETS.recruitment_source, domain=None, range=Optional[Union[str, "RecruitmentSourceEnum"]])

slots.training_type = Slot(uri=VALUESETS.training_type, name="training_type", curie=VALUESETS.curie('training_type'),
                   model_uri=VALUESETS.training_type, domain=None, range=Optional[Union[str, "TrainingTypeEnum"]])

slots.employee_status = Slot(uri=VALUESETS.employee_status, name="employee_status", curie=VALUESETS.curie('employee_status'),
                   model_uri=VALUESETS.employee_status, domain=None, range=Optional[Union[str, "EmployeeStatusEnum"]])

slots.work_arrangement = Slot(uri=VALUESETS.work_arrangement, name="work_arrangement", curie=VALUESETS.curie('work_arrangement'),
                   model_uri=VALUESETS.work_arrangement, domain=None, range=Optional[Union[str, "WorkArrangementEnum"]])

slots.benefits_category = Slot(uri=VALUESETS.benefits_category, name="benefits_category", curie=VALUESETS.curie('benefits_category'),
                   model_uri=VALUESETS.benefits_category, domain=None, range=Optional[Union[str, "BenefitsCategoryEnum"]])
