from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    __name__: str

    # Generate __tablename__ automatically
    # @declared_attr
    # def __tablename__(cls) -> str:
    #     return cls.__name__.lower()


class Study(BaseModel):
    __tablename__ = "studies"

    id: BaseModel.id
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
    # annotations: Mapped[list[Annotation]] = relationship(
    #     "Annotation", back_populates="studies_id"
    # )
    # distributions: Mapped[list[Distribution]] = relationship(
    #     "Distribution", back_populates="studies_id"
    # )


class Theme(BaseModel):
    __tablename__ = "themes"

    id: BaseModel.id
    created_at: BaseModel.created_at
    updated_at: BaseModel.updated_at
    color: Mapped[str] = mapped_column(index=True, nullable=False)
    term: Mapped[str] = mapped_column(index=True, nullable=False)
    hex: Mapped[str] = mapped_column(index=True, nullable=False)


class Annotation(BaseModel):
    __tablename__ = "annotations"

    id: BaseModel.id
    created_at: BaseModel.created_at
    updated_at: BaseModel.updated_at
    studies_id: Mapped[UUID] = mapped_column("Study", ForeignKey("studies.id"))
    theme_id: Mapped[UUID] = mapped_column("Theme", ForeignKey("themes.id"))
    count: Mapped[int] = mapped_column(index=True, nullable=False)
    page_number: Mapped[int] = mapped_column(index=True, nullable=False)
    annot_rgb_color: Mapped[str] = mapped_column(index=True, nullable=False)
    annot_hex_color: Mapped[str] = mapped_column(index=True, nullable=False)
    text: Mapped[str] = mapped_column(index=True, nullable=False)


class Distribution(BaseModel):
    __tablename__ = "distribution"

    id: Mapped[UUID]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    studies_id: Mapped[UUID] = mapped_column("Study", ForeignKey("studies.id"))
    theme_id: Mapped[UUID] = mapped_column("Theme", ForeignKey("themes.id"))
    count: Mapped[int] = mapped_column(index=True, nullable=False)
    page_number: Mapped[int] = mapped_column(index=True, nullable=False)
    term: Mapped[str] = mapped_column(index=True, nullable=False)
    text: Mapped[str] = mapped_column(index=True, nullable=False)
