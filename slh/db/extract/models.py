from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)


class Study(Base):
    __tablename__ = "studies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    authors = Column(String)
    abstract = Column(String)
    published_year = Column(Integer)
    published_month = Column(Integer)
    journal = Column(String)
    volume = Column(String)
    issue = Column(String)
    pages = Column(String)
    accession_number = Column(String)
    doi = Column(String)
    ref = Column(String)
    covidence_id = Column(Integer)
    study = Column(String)
    notes = Column(String)
    tags = Column(String)
    filename = Column(String)
    keywords = Column(String)
    citation = Column(String)
    bibliography = Column(String)
    full_text = Column(String)
    total_annotations = Column(Integer)
    total_distribution = Column(Integer)


class Theme(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    color = Column(String)
    studies = Column(String)
    annotations = Column(String)
    distribution = Column(String)


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True)
    studies_id = Column(Integer)
    theme_id = Column(Integer)
    count = Column(Integer)
    page_number = Column(Integer)
    annot_rgb_color = Column(String)
    annot_hex_color = Column(String)
    annotation = Column(String)
    text = Column(String)


class Distribution(Base):
    __tablename__ = "distribution"

    id = Column(Integer, primary_key=True)
    studies_id = Column(Integer)
    theme_id = Column(Integer)
    count = Column(Integer)
    page_number = Column(Integer)
    term = Column(String)
    text = Column(String)
