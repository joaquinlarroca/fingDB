"""
Database Models for fingDB

This file defines all the database models (tables) for the fingDB API.
Each class represents a table in the database.

Key Concepts:
- SQLAlchemy ORM: Maps Python classes to database tables
- Relationships: Links between tables (one-to-many, many-to-many)
- Enums: Fixed sets of values for certain fields

The main entities are:
- Carrera (Career/degree program)
- Perfil (Profile/specialization within a career)
- Materia (Course/subject)
- Instituto (Institute/department)
- MateriaPrevia (Prerequisite relationship between courses)
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Enum as SAEnum,
    ForeignKey,
    DateTime,
    UniqueConstraint,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.schemas.materia import PeriodoEnum


# ============================================================================
# ENUMS
# ============================================================================


class TipoPreviaEnum(str, Enum):
    """
    Enum representing the type of prerequisite.

    Values:
    - aprobado (approved): Course must be passed
    - exonerado (exempted): Course can be exempted
    """

    aprobado = "aprobado"
    exonerado = "exonerado"


# ============================================================================
# MANY-TO-MANY RELATIONSHIP TABLES
# ============================================================================


class MateriaPrevia(Base):
    """
    Many-to-many relationship table representing course prerequisites.

    This creates a many-to-many relationship between Materia and itself,
    allowing courses to have multiple prerequisites of different types.

    Example: "Cálculo 1" might have no prerequisites,
            while "Cálculo 2" has "Cálculo 1" as "aprobado"
    """

    __tablename__ = "materia_previas"
    __table_args__ = (
        # Composite primary key: combination of materia_id, previa_id, and tipo
        PrimaryKeyConstraint("materia_id", "previa_id", "tipo"),
        # Prevent duplicate prerequisite entries
        UniqueConstraint("materia_id", "previa_id", "tipo"),
    )

    # Foreign key to the course that has a prerequisite
    materia_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id", ondelete="CASCADE"),
    )

    # Foreign key to the prerequisite course
    previa_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id", ondelete="CASCADE"),
    )

    # Type of prerequisite (aprobado or exonerado)
    tipo: Mapped[TipoPreviaEnum] = mapped_column(
        SAEnum(TipoPreviaEnum, name="tipo_previa_enum"),
    )

    # Relationships to access the actual course objects
    materia: Mapped["Materia"] = relationship(
        "Materia",
        foreign_keys=[materia_id],
        back_populates="previas_rel",
    )

    previa: Mapped["Materia"] = relationship(
        "Materia",
        foreign_keys=[previa_id],
    )


# ============================================================================
# MAIN ENTITY TABLES
# ============================================================================


class Materia(Base):
    """
    Model representing a course/subject in the curriculum.

    Fields:
    - id: Unique identifier
    - name: Course name (e.g., "Cálculo 1")
    - codigo: Course code (e.g., "MAT111")
    - periodo: Semester when the course is offered
    - creditos: Credits/points the course is worth
    - min_creditos: Minimum credits required to enroll
    - active: Whether the course is currently active
    - created_at/updated_at: Timestamps
    - instituto_id: Foreign key to the institute
    """

    __tablename__ = "materias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    periodo: Mapped[PeriodoEnum] = mapped_column(
        SAEnum(PeriodoEnum, name="periodo_enum"),
        nullable=False,
    )
    creditos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_creditos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, nullable=True
    )

    # Foreign key to the institute offering this course
    instituto_id: Mapped[int] = mapped_column(
        ForeignKey("institutos.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationship to the institute
    instituto: Mapped["Instituto"] = relationship(
        "Instituto",
        back_populates="materias",
    )

    # Relationship to prerequisites (courses that must be completed before this one)
    previas_rel: Mapped[List["MateriaPrevia"]] = relationship(
        "MateriaPrevia",
        foreign_keys="[MateriaPrevia.materia_id]",
        back_populates="materia",
        cascade="all, delete-orphan",  # Delete prerequisites if course is deleted
    )

    @property
    def prev_aprobado(self) -> List["Materia"]:
        """Get list of courses that must be APPROVED (passed) before this one."""
        return [
            rel.previa
            for rel in self.previas_rel
            if rel.tipo == TipoPreviaEnum.aprobado
        ]

    @property
    def prev_exonerado(self) -> List["Materia"]:
        """Get list of courses that must be EXONERATED (exempted) before this one."""
        return [
            rel.previa
            for rel in self.previas_rel
            if rel.tipo == TipoPreviaEnum.exonerado
        ]


class Perfil(Base):
    """
    Model representing a specialization/profile within a career.

    In many engineering programs, students choose a specialization
    (e.g., "Industrial", "Electrical", "Software") after completing
    common courses.

    Fields:
    - id: Unique identifier
    - name: Profile name (e.g., "Ingeniería de Software")
    - carrera_id: Foreign key to the parent career
    - created_at: Timestamp
    """

    __tablename__ = "perfiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    carrera_id: Mapped[int] = mapped_column(
        ForeignKey("carreras.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationship to the parent career
    carrera: Mapped["Carrera"] = relationship(
        "Carrera",
        back_populates="perfiles",
    )

    # Relationship to courses required for this profile
    materias_rel: Mapped[List["PerfilMateria"]] = relationship(
        "PerfilMateria",
        back_populates="perfil",
        cascade="all, delete-orphan",
    )

    @property
    def materias_obligatorias(self) -> List["Materia"]:
        """Get list of mandatory courses for this profile."""
        return [rel.materia for rel in self.materias_rel if rel.tipo == "obligatoria"]


class Instituto(Base):
    """
    Model representing an institute/department at the faculty.

    Institutes are organizational units that group related courses
    (e.g., "Instituto de Matemática", "Instituto de Computación")

    Fields:
    - id: Unique identifier
    - name: Institute name
    - created_at: Timestamp
    """

    __tablename__ = "institutos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationship to courses offered by this institute
    materias: Mapped[List["Materia"]] = relationship(
        "Materia",
        back_populates="instituto",
        cascade="all, delete-orphan",
    )


# ============================================================================
# INTERMEDIATE TABLES FOR MANY-TO-MANY RELATIONSHIPS
# ============================================================================


class CarreraMateria(Base):
    """
    Many-to-many relationship between Carrera (career) and Materia (course).

    This defines which courses belong to which career and whether they
    are mandatory ("obligatoria") or optional ("opcional").
    """

    __tablename__ = "carrera_materias"
    __table_args__ = (UniqueConstraint("carrera_id", "materia_id", "tipo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    carrera_id: Mapped[int] = mapped_column(
        ForeignKey("carreras.id", ondelete="CASCADE"),
        nullable=False,
    )
    materia_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "obligatoria" or "opcional"

    carrera: Mapped["Carrera"] = relationship("Carrera", back_populates="materias_rel")
    materia: Mapped["Materia"] = relationship("Materia")


class PerfilMateria(Base):
    """
    Many-to-many relationship between Perfil (profile) and Materia (course).

    Similar to CarreraMateria but for profiles within a career.
    """

    __tablename__ = "perfil_materias"
    __table_args__ = (UniqueConstraint("perfil_id", "materia_id", "tipo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    perfil_id: Mapped[int] = mapped_column(
        ForeignKey("perfiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    materia_id: Mapped[int] = mapped_column(
        ForeignKey("materias.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)

    perfil: Mapped["Perfil"] = relationship("Perfil", back_populates="materias_rel")
    materia: Mapped["Materia"] = relationship("Materia")


class Carrera(Base):
    """
    Model representing a career/degree program at the faculty.

    Examples: "Ingeniería en Computación", "Ingeniería Eléctrica"

    Fields:
    - id: Unique identifier
    - name: Career name
    - created_at: Timestamp
    """

    __tablename__ = "carreras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationship to courses in this career
    materias_rel: Mapped[List["CarreraMateria"]] = relationship(
        "CarreraMateria",
        back_populates="carrera",
        cascade="all, delete-orphan",
    )

    # Relationship to profiles/specializations within this career
    perfiles: Mapped[List["Perfil"]] = relationship(
        "Perfil",
        back_populates="carrera",
        cascade="all, delete-orphan",
    )

    @property
    def materias_opcionales(self) -> List["Materia"]:
        """Get list of optional courses for this career."""
        return [rel.materia for rel in self.materias_rel if rel.tipo == "opcional"]

    @property
    def materias_obligatorias(self) -> List["Materia"]:
        """Get list of mandatory courses for this career."""
        return [rel.materia for rel in self.materias_rel if rel.tipo == "obligatoria"]
