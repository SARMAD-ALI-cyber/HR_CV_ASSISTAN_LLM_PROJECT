from pydantic import BaseModel, Field
from typing import List
'''This file defines the schema for our JSON files it is a universal
truth for our JSONs so in future if we have to change anything for JSONs
we have to just make changes here'''
class EducationItem(BaseModel):
    degree: str = Field(
        description=(
            "Degree name of the applicant. Example: 'BSc', 'BS Computer Science', "
            "'MSc', 'MBA', 'PhD', etc."
        )
    )
    field: str = Field(
        description=(
            "Field or major of study. Example: 'Computer Science', 'Electrical Engineering', "
            "'Data Science', 'Economics', etc."
        )
    )
    university: str = Field(
        description=(
            "Full official name of the university or institution. "
            "Example: 'University of Lahore', 'Harvard University', "
            "'National University of Singapore'."
        )
    )
    country: str = Field(
        description=(
            'Country where the university is located. Example: "Pakistan", '
            '"United States", "Germany", etc.'
        )
    )
    start: str = Field(
        description=(
            "Start date of degree. Format example: '12/09/2022', '2018', or 'Sep 2020'. "
            "Use any date found in CV."
        )
    )
    end: str = Field(
        description=(
            "End or expected graduation date. Example: '30/05/2026', '2023', 'Jun 2024'."
        )
    )
    gpa: float = Field(
        description=(
            "Obtained GPA/CGPA. Example: In '3.22/4.0', GPA is 3.22. "
            "In '7.5/10', GPA is 7.5."
        )
    )
    scale: float = Field(
        description=(
            "GPA scale. Example: In '3.22/4.0', scale is 4.0. In '7.5/10', scale is 10."
        )
    )


class ExperienceItem(BaseModel):
    title: str = Field(
        description=(
            "Job title or position held. Example: 'Software Engineer', 'Research Intern', "
            "'Teaching Assistant', 'Data Analyst'."
        )
    )
    org: str = Field(
        description=(
            "Organization name. Example: 'Google', 'Microsoft', 'NVIDIA', "
            "'FAST University', 'ABC Pvt. Ltd.'."
        )
    )
    start: str = Field(
        description=(
            "Start date of the job/internship. Examples: 'Jan 2021', '2020', '01/03/2019'."
        )
    )
    end: str = Field(
        description=(
            "End date of the job/internship. Examples: 'Mar 2023', '2021', 'Present', "
            "'Currently Working'."
        )
    )
    duration_months: int = Field(
        description=(
            "Total duration in months. Example: 24 → 2 years, 6 → 6 months. "
            "If duration cannot be computed, leave null."
        )
    )
    domain: str = Field(
        description=(
            "Work domain or specialization extracted from role. "
            "Example: 'NLP', 'Backend Development', 'Machine Learning', 'Finance', etc."
        )
    )

class PublicationItem(BaseModel):
    title: str = Field(
        description=(
            "Full title of the publication. Example: 'Deep Learning for Medical Imaging'."
        )
    )
    venue: str = Field(
        description=(
            "Publication venue or conference/journal name. Example: "
            "'IEEE Transactions on Medical Imaging', 'ACL 2023', 'Nature', 'ICLR'."
        )
    )
    year: int = Field(
        description="Year of publication. Example: 2021, 2023, etc."
    )
    type: str = Field(
        description=(
            "Type of publication. Examples: 'Journal', 'Conference', 'Workshop', 'Preprint'."
        )
    )
    authors: List[str] = Field(
        default=[],
        description=(
            "List of authors exactly as written. Example: ['John Doe', 'Alice Smith', "
            "'Ahmed Khan']."
        )
    )
    author_position: int = Field(
        description=(
            "Index of the applicant’s position in the author list. Example: "
            "1 for first author, 2 for second author, etc."
        )
    )
    journal_if: float = Field(
        description=(
            "Journal Impact Factor (if available). Example: 3.7, 9.1, etc. "
            "Leave null if not present in CV."
        )
    )
    domain: str = Field(
        description=(
            "Research area inferred from publication. Example: 'Computer Vision', "
            "'NLP', 'Bioinformatics', etc."
        )
    )
    evidence_span: str = Field(
        description=(
            "Exact text span from the CV used as evidence for this extracted publication. "
            "Example: raw paragraph extracted from CV."
        )
    )



class AwardItem(BaseModel):
    title: str = Field(
        description=(
            "Award or achievement title. Example: 'Dean's List', 'Gold Medalist', "
            "'Employee of the Month'."
        )
    )
    issuer: str = Field(
        description=(
            "Organization, institution, or authority that issued the award. "
            "Example: 'FAST University', 'Google', 'ACM'."
        )
    )
    year: int = Field(
        description="Year award was received. Example: 2022, 2021."
    )
    type: str = Field(
        description=(
            "Award type or category. Example: 'Academic', 'Professional', 'Research', "
            "'Sports'."
        )
    )
    evidence_span: str = Field(
        description="Exact text snippet from CV supporting this award."
    )


class CVSchema(BaseModel):
    education: List[EducationItem] = Field(
        default=[],
        description="List of extracted education entries."
    )
    experience: List[ExperienceItem] = Field(
        default=[],
        description="List of extracted work experiences."
    )
    publications: List[PublicationItem] = Field(
        default=[],
        description="List of extracted publications."
    )
    awards: List[AwardItem] = Field(
        default=[],
        description="List of extracted awards and achievements."
    )


# class CVMetadata(BaseModel):
#     filename: str
#     language: str
#     ocr_used: bool = False
#     pages: int
#     corrupted: bool = False
#     parse_confidence: float = 0.0