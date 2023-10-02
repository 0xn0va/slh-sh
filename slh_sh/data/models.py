from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey


from slh_sh.utils.db import BaseModel


class Study(BaseModel):
    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(
        index=True, primary_key=True, autoincrement=True, nullable=False
    )
    created_at: BaseModel.created_at
    updated_at: BaseModel.updated_at
    title: Mapped[str] = mapped_column(index=True, nullable=False)
    authors: Mapped[str] = mapped_column(index=True, nullable=False)
    abstract: Mapped[str] = mapped_column(index=True, nullable=False)
    published_year: Mapped[int] = mapped_column(index=True, nullable=False)
    published_month: Mapped[int] = mapped_column(index=True, nullable=True)
    journal: Mapped[str] = mapped_column(index=True, nullable=True)
    volume: Mapped[str] = mapped_column(index=True, nullable=True)
    issue: Mapped[str] = mapped_column(index=True, nullable=True)
    pages: Mapped[str] = mapped_column(index=True, nullable=True)
    accession_number: Mapped[str] = mapped_column(index=True, nullable=True)
    doi: Mapped[str] = mapped_column(index=True, nullable=True)
    ref: Mapped[str] = mapped_column(index=True, nullable=True)
    covidence_id: Mapped[int] = mapped_column(index=True, nullable=True)
    study: Mapped[str] = mapped_column(index=True, nullable=True)
    notes: Mapped[str] = mapped_column(index=True, nullable=True)
    tags: Mapped[str] = mapped_column(index=True, nullable=True)
    filename: Mapped[str] = mapped_column(index=True, nullable=True)
    keywords: Mapped[str] = mapped_column(index=True, nullable=True)
    citation: Mapped[str] = mapped_column(index=True, nullable=True)
    bibliography: Mapped[str] = mapped_column(index=True, nullable=True)
    full_text: Mapped[str] = mapped_column(index=True, nullable=True)
    total_annotations: Mapped[int] = mapped_column(index=True, nullable=True)
    total_distribution: Mapped[int] = mapped_column(index=True, nullable=True)


class Theme(BaseModel):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(
        index=True, primary_key=True, autoincrement=True, nullable=False
    )
    created_at: BaseModel.created_at
    updated_at: BaseModel.updated_at
    color: Mapped[str] = mapped_column(index=True, nullable=False)
    term: Mapped[str] = mapped_column(index=True, nullable=False)
    hex: Mapped[str] = mapped_column(index=True, nullable=False)


class Annotation(BaseModel):
    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(
        index=True, primary_key=True, autoincrement=True, nullable=False
    )
    created_at: BaseModel.created_at
    updated_at: BaseModel.updated_at
    studies_id: Mapped[int] = mapped_column("Study", ForeignKey("studies.id"))
    theme_id: Mapped[int] = mapped_column("Theme", ForeignKey("themes.id"))
    count: Mapped[int] = mapped_column(index=True, nullable=False)
    page_number: Mapped[int] = mapped_column(index=True, nullable=False)
    annot_rgb_color: Mapped[str] = mapped_column(index=True, nullable=False)
    annot_hex_color: Mapped[str] = mapped_column(index=True, nullable=False)
    text: Mapped[str] = mapped_column(index=True, nullable=False)


class Distribution(BaseModel):
    __tablename__ = "distribution"

    id: Mapped[int] = mapped_column(
        index=True, primary_key=True, autoincrement=True, nullable=False
    )
    created_at: BaseModel.created_at
    updated_at: BaseModel.updated_at
    studies_id: Mapped[int] = mapped_column("studies_id", ForeignKey("studies.id"))
    theme_id: Mapped[int] = mapped_column("theme_id", ForeignKey("themes.id"))
    count: Mapped[int] = mapped_column(index=True, nullable=False)
    page_number: Mapped[int] = mapped_column(index=True, nullable=False)
    term: Mapped[str] = mapped_column(index=True, nullable=False)
    text: Mapped[str] = mapped_column(index=True, nullable=False)
