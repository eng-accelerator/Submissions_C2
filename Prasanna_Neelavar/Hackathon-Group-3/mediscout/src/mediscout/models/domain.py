"""
Domain models for MediScout.

These Pydantic models define the core business entities and their relationships.
All models include validation, type safety, and serialization capabilities.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# Enums
# ============================================================================


class SessionStatus(str, Enum):
    """Research session lifecycle states."""

    INITIALIZING = "initializing"
    INDEXING = "indexing"
    RETRIEVING = "retrieving"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentSource(str, Enum):
    """Source of a research document."""

    USER_UPLOAD = "user_upload"
    PUBMED = "pubmed"
    CLINICAL_TRIALS = "clinical_trials"
    GOOGLE_SCHOLAR = "google_scholar"


class StudyDesign(str, Enum):
    """Medical study design types for analysis."""

    RCT = "rct"  # Randomized Controlled Trial
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    CASE_STUDY = "case_study"
    META_ANALYSIS = "meta_analysis"
    SYSTEMATIC_REVIEW = "systematic_review"
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    """Confidence level for hypotheses and findings."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ============================================================================
# Core Domain Models
# ============================================================================


class Document(BaseModel):
    """
    A research document from any source.

    Represents a single paper, article, or user-uploaded file.
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    document_id: UUID = Field(default_factory=uuid4)
    source: DocumentSource
    title: str = Field(..., min_length=1, max_length=500)
    authors: list[str] = Field(default_factory=list)
    abstract: str = Field(default="", max_length=5000)
    content: str = Field(..., min_length=1)
    url: Optional[str] = None
    doi: Optional[str] = None
    publication_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Document content cannot be empty")
        return v

    @property
    def word_count(self) -> int:
        """Calculate approximate word count."""
        return len(self.content.split())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return self.model_dump(mode="json")


class Chunk(BaseModel):
    """
    A text chunk with embedding vector.

    Documents are split into chunks for efficient retrieval.
    """

    model_config = ConfigDict(validate_assignment=True)

    chunk_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str = Field(..., min_length=1, max_length=2000)
    embedding: Optional[list[float]] = None
    sequence_number: int = Field(ge=0)
    start_char: int = Field(ge=0)
    end_char: int = Field(gt=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("end_char")
    @classmethod
    def end_after_start(cls, v: int, info: Any) -> int:
        if "start_char" in info.data and v <= info.data["start_char"]:
            raise ValueError("end_char must be greater than start_char")
        return v

    @property
    def char_count(self) -> int:
        """Get character count."""
        return self.end_char - self.start_char

    @property
    def has_embedding(self) -> bool:
        """Check if chunk has been embedded."""
        return self.embedding is not None and len(self.embedding) > 0


class RetrievalResult(BaseModel):
    """
    Result of a retrieval query with ranked documents.

    Contains documents and their relevance scores.
    """

    model_config = ConfigDict(validate_assignment=True)

    retrieval_id: UUID = Field(default_factory=uuid4)
    query: str = Field(..., min_length=1)
    results: list[tuple[Chunk, float]] = Field(default_factory=list)  # (chunk, score)
    total_results: int = Field(ge=0)
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    sources: dict[DocumentSource, int] = Field(default_factory=dict)  # Source distribution

    @field_validator("results")
    @classmethod
    def validate_scores(cls, v: list[tuple[Chunk, float]]) -> list[tuple[Chunk, float]]:
        for chunk, score in v:
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"Score must be between 0 and 1, got {score}")
        return v

    @property
    def top_k_chunks(self) -> list[Chunk]:
        """Get only the chunks without scores."""
        return [chunk for chunk, _ in self.results]

    @property
    def average_score(self) -> float:
        """Calculate average relevance score."""
        if not self.results:
            return 0.0
        return sum(score for _, score in self.results) / len(self.results)


class AnalysisResult(BaseModel):
    """
    Critical analysis result for a document.

    Generated by the Analysis Agent.
    """

    model_config = ConfigDict(validate_assignment=True)

    analysis_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    summary: str = Field(..., min_length=10)
    study_design: StudyDesign = StudyDesign.UNKNOWN
    outcomes: list[str] = Field(default_factory=list)
    reliability_score: float = Field(ge=0.0, le=1.0)
    key_findings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_high_quality(self) -> bool:
        """Check if study is high quality (RCT or Meta-analysis)."""
        return self.study_design in (StudyDesign.RCT, StudyDesign.META_ANALYSIS)


class Hypothesis(BaseModel):
    """
    A novel hypothesis generated from research findings.

    Generated by the Insight Agent.
    """

    model_config = ConfigDict(validate_assignment=True)

    hypothesis_id: UUID = Field(default_factory=uuid4)
    statement: str = Field(..., min_length=10, max_length=1000)
    reasoning_chain: list[str] = Field(..., min_length=2)
    supporting_docs: list[UUID] = Field(..., min_length=2)
    confidence: ConfidenceLevel
    novelty_score: float = Field(ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("supporting_docs")
    @classmethod
    def min_two_sources(cls, v: list[UUID]) -> list[UUID]:
        if len(v) < 2:
            raise ValueError("Hypotheses require minimum 2 supporting documents")
        return v


class Report(BaseModel):
    """
    Final research report with findings and hypotheses.

    Generated by the Report Builder Agent.
    """

    model_config = ConfigDict(validate_assignment=True)

    report_id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., min_length=1, max_length=200)
    exec_summary: str = Field(..., min_length=50)
    detailed_findings: str = Field(..., min_length=100)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    medical_disclaimer: str = Field(
        default=(
            "This report is for informational purposes only and does not constitute "
            "medical advice. Always consult with qualified healthcare professionals."
        )
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def citation_count(self) -> int:
        """Get number of citations."""
        return len(self.citations)

    @property
    def hypothesis_count(self) -> int:
        """Get number of hypotheses."""
        return len(self.hypotheses)

    def export_markdown(self) -> str:
        """Export report as markdown."""
        md = f"# {self.title}\n\n"
        md += f"**Generated:** {self.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        md += f"## Executive Summary\n\n{self.exec_summary}\n\n"
        md += f"## Detailed Findings\n\n{self.detailed_findings}\n\n"

        if self.hypotheses:
            md += "## Novel Hypotheses\n\n"
            for i, hyp in enumerate(self.hypotheses, 1):
                md += f"### Hypothesis {i} (Confidence: {hyp.confidence.value})\n\n"
                md += f"{hyp.statement}\n\n"
                md += f"**Novelty Score:** {hyp.novelty_score:.2f}\n\n"

        if self.citations:
            md += "## References\n\n"
            for i, cite in enumerate(self.citations, 1):
                md += f"{i}. {cite}\n"
            md += "\n"

        md += f"---\n\n*{self.medical_disclaimer}*\n"
        return md


# ============================================================================
# Configuration Models
# ============================================================================


class EmbeddingConfig(BaseModel):
    """Configuration for embedding service."""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"
    batch_size: int = 32
    dimension: int = 384  # For all-MiniLM-L6-v2


class ChunkingConfig(BaseModel):
    """Configuration for text chunking."""

    chunk_size: int = Field(default=500, ge=100, le=2000)
    chunk_overlap: int = Field(default=100, ge=0, le=500)
    
    @field_validator("chunk_overlap")
    @classmethod
    def overlap_less_than_size(cls, v: int, info: Any) -> int:
        if "chunk_size" in info.data and v >= info.data["chunk_size"]:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v

