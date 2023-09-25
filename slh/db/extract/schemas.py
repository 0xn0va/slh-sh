from pydantic import BaseModel


class StudySchema(BaseModel):
    id: int
    title: str
    authors: list
    abstract: str
    published_year: int
    published_month: int
    journal: str
    volume: str
    issue: str
    pages: str
    accession_number: str
    doi: str
    ref: str
    covidence_id: int
    study: str
    notes: str
    tags: str
    filename: str
    keywords: str
    citation: str
    bibliography: str
    full_text: str
    total_annotations: int
    total_distribution: int


class ThemeSchema(BaseModel):
    id: int
    name: str
    description: str
    color: str
    studies: list
    annotations: list
    distribution: list


class AnnotationSchema(BaseModel):
    id: int
    studies_id: int
    theme_id: int
    count: int
    page_number: int
    annot_rgb_color: str
    annot_hex_color: str
    annotation: str
    text: str


class DistributionSchema(BaseModel):
    id: int
    studies_id: int
    theme_id: int
    count: int
    page_number: int
    term: str
    text: str
