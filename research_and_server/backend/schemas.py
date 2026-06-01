"""
Pydantic schemas for Legal Case Knowledge Graph System.

This module defines all data models using Pydantic for validation:
- Case metadata
- Category structures
- Entities and relationships
- Graph components
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class EntityType(str, Enum):
    """Types of entities in legal documents."""

    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    COURT = "COURT"
    JUDGE = "JUDGE"
    LAW_STATUTE = "LAW_STATUTE"
    LEGAL_CONCEPT = "LEGAL_CONCEPT"
    CITATION = "CITATION"
    DATE = "DATE"
    LOCATION = "LOCATION"


class RelationshipType(str, Enum):
    """Types of relationships between entities."""

    CITES = "CITES"
    OVERRULES = "OVERRULES"
    FOLLOWS = "FOLLOWS"
    DISTINGUISHES = "DISTINGUISHES"
    PRESIDED_BY = "PRESIDED_BY"
    REPRESENTED_BY = "REPRESENTED_BY"
    FILED_BY = "FILED_BY"
    GOVERNED_BY = "GOVERNED_BY"
    INTERPRETS = "INTERPRETS"
    APPLIES = "APPLIES"
    MENTIONED_IN = "MENTIONED_IN"


class CategoryPath(BaseModel):
    """Hierarchical path for case categorization."""

    main_category: str = Field(
        ...,
        description="Main legal domain"
    )
    sub_category: str = Field(
        ...,
        description="Sub-category within domain"
    )
    year: int = Field(
        ...,
        ge=1950,
        le=2030,
        description="Year of the case"
    )

    def to_path_string(self) -> str:
        """Convert to file system path string."""
        return f"{self.main_category}/{self.sub_category}/{self.year}"

    @classmethod
    def from_path_string(cls, path_str: str) -> "CategoryPath":
        """Create CategoryPath from path string."""
        parts = path_str.split("/")
        return cls(
            main_category=parts[0],
            sub_category=parts[1],
            year=int(parts[2])
        )


class CaseMetadata(BaseModel):
    """Metadata for a legal case."""

    case_id: str = Field(
        ...,
        description="Unique identifier for the case"
    )
    case_number: str = Field(
        ...,
        description="Official case number"
    )
    title: str = Field(
        ...,
        description="Case title"
    )
    date: datetime = Field(
        ...,
        description="Date of judgment"
    )
    court: str = Field(
        ...,
        description="Court name"
    )
    judges: List[str] = Field(
        default_factory=list,
        description="List of judges"
    )
    petitioner: Optional[str] = Field(
        None,
        description="Petitioner/Appellant name"
    )
    respondent: Optional[str] = Field(
        None,
        description="Respondent name"
    )
    verdict: Optional[str] = Field(
        None,
        description="Case verdict"
    )
    main_category: str = Field(
        ...,
        description="Main legal domain"
    )
    sub_category: str = Field(
        ...,
        description="Sub-category within domain"
    )
    year: int = Field(
        ...,
        description="Year of the case"
    )
    case_type: Optional[str] = Field(
        None,
        description="Type of case"
    )
    bench_size: Optional[str] = Field(
        None,
        description="Bench size"
    )
    full_text_path: Optional[str] = Field(
        None,
        description="Path to full text file"
    )
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Confidence scores for categorization"
    )

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate year is within reasonable range."""
        if v < 1950 or v > 2030:
            raise ValueError("Year must be between 1950 and 2030")
        return v


class Entity(BaseModel):
    """An entity extracted from a legal document."""

    entity_id: str = Field(
        ...,
        description="Unique identifier"
    )
    entity_type: EntityType = Field(
        ...,
        description="Type of entity"
    )
    text: str = Field(
        ...,
        description="Entity text/name"
    )
    normalized_text: Optional[str] = Field(
        None,
        description="Normalized form of text"
    )
    context: Optional[str] = Field(
        None,
        description="Surrounding context"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score"
    )


class Relationship(BaseModel):
    """A relationship between two entities."""

    relationship_id: str = Field(
        ...,
        description="Unique identifier"
    )
    relationship_type: RelationshipType = Field(
        ...,
        description="Type of relationship"
    )
    source_entity_id: str = Field(
        ...,
        description="Source entity ID"
    )
    target_entity_id: str = Field(
        ...,
        description="Target entity ID"
    )
    context: Optional[str] = Field(
        None,
        description="Context of relationship"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score"
    )


class KnowledgeGraph(BaseModel):
    """A knowledge graph for a legal case."""

    case_id: str = Field(
        ...,
        description="Case identifier"
    )
    entities: List[Entity] = Field(
        default_factory=list,
        description="List of entities"
    )
    relationships: List[Relationship] = Field(
        default_factory=list,
        description="List of relationships"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Graph metadata"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp"
    )


class CategoryNode(BaseModel):
    """A node in the category hierarchy."""

    name: str = Field(
        ...,
        description="Category name"
    )
    level: int = Field(
        ...,
        ge=0,
        le=3,
        description="Hierarchy level (0=root, 1=main, 2=sub, 3=year)"
    )
    parent: Optional[str] = Field(
        None,
        description="Parent category name"
    )
    children: List[str] = Field(
        default_factory=list,
        description="Child category names"
    )
    case_count: int = Field(
        default=0,
        ge=0,
        description="Number of cases in this category"
    )
    year_range: Optional[tuple[int, int]] = Field(
        None,
        description="Year range for cases"
    )


class CategoryStatistics(BaseModel):
    """Statistics for a category."""

    category_path: str = Field(
        ...,
        description="Full category path"
    )
    total_cases: int = Field(
        default=0,
        description="Total number of cases"
    )
    year_distribution: Dict[int, int] = Field(
        default_factory=dict,
        description="Cases per year"
    )
    verdict_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Cases per verdict type"
    )
    bench_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Cases per bench size"
    )
