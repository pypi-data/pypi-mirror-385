"""Pydantic models for AI processing responses."""

from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductLabel(str, Enum):
    """Available product labels."""

    KOTS = "product::kots"
    TROUBLESHOOT = "product::troubleshoot"
    KURL = "product::kurl"
    EMBEDDED_CLUSTER = "product::embedded-cluster"
    SDK = "product::sdk"
    DOCS = "product::docs"
    VENDOR = "product::vendor"
    DOWNLOADPORTAL = "product::downloadportal"
    COMPATIBILITY_MATRIX = "product::compatibility-matrix"


class RecommendedLabel(BaseModel):
    """A recommended product label with reasoning (no individual confidence)."""

    label: ProductLabel
    reasoning: str = Field(description="Explanation for this recommendation")


class LabelAssessment(BaseModel):
    """Assessment of an existing label."""

    label: str
    correct: bool = Field(description="Whether this label is correctly applied")
    reasoning: str = Field(description="Explanation of the assessment")


class ImageAnalysis(BaseModel):
    """Analysis of an individual image."""

    filename: str
    source: str = Field(description="Source location: 'issue_body' or 'comment_{id}'")
    description: str = Field(
        description="What the image shows relevant to product classification"
    )
    relevance_score: float = Field(
        ge=0.0, le=1.0, description="How relevant this image is to classification"
    )


class ProductLabelingResponse(BaseModel):
    """Structured response for product labeling analysis."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        # Allow arbitrary types for Union handling
        arbitrary_types_allowed=True,
    )

    root_cause_analysis: str = Field(
        default="Root cause unclear",
        description="Root cause analysis of the issue. "
        "State 'Root cause unclear' if unable to determine.",
    )
    root_cause_confidence: float | None = Field(
        default=None,
        description="Confidence in identified root cause (0-1). "
        "Only provide if a specific root cause is defined.",
    )
    recommendation_confidence: float = Field(
        description="Overall confidence in the complete label recommendation (0-1)"
    )
    recommended_labels: list[RecommendedLabel] = Field(
        description="Suggested product labels"
    )
    current_labels_assessment: list[LabelAssessment] = Field(
        description="Assessment of existing labels"
    )
    summary: str = Field(
        description="Brief summary of the issue's product classification"
    )
    reasoning: str = Field(description="Detailed reasoning for label recommendations")

    # Image-related fields for Phase 2
    images_analyzed: list[ImageAnalysis] = Field(
        default_factory=list,
        description="Analysis of images found in issue. "
        "MUST be empty if no images were provided.",
    )
    image_impact: str = Field(
        default="",
        description="How images influenced the classification decision. "
        "MUST be empty if no images were provided.",
    )

    @field_validator("images_analyzed")
    @classmethod
    def validate_images_analyzed(cls, v: list[ImageAnalysis]) -> list[ImageAnalysis]:
        """Validate that images_analyzed is only populated when images are present."""
        # Note: This validator will be enhanced with context in the processor
        return v

    @field_validator("image_impact")
    @classmethod
    def validate_image_impact(cls, v: str) -> str:
        """Validate that image_impact is only populated when images are present."""
        # Note: This validator will be enhanced with context in the processor
        return v


class ResolvedAnalysis(BaseModel):
    """Analysis result when root cause is identified."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )

    status: Literal["resolved"] = "resolved"
    root_cause: str = Field(
        description="The fundamental underlying cause identified through analysis"
    )
    evidence: list[str] = Field(
        description="Specific findings from multiple sources that support conclusion"
    )
    solution: str = Field(
        description="Recommended corrective actions with specific commands and steps"
    )
    validation: str = Field(
        description="How evidence supports root cause and what was ruled out"
    )


class NeedsDataAnalysis(BaseModel):
    """Analysis result when insufficient data is available for definitive conclusion."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )

    status: Literal["needs_data"] = "needs_data"
    current_hypothesis: str = Field(
        description="Best assessment based on available evidence with confidence level"
    )
    missing_evidence: list[str] = Field(
        description="Specific data needed to confirm or deny potential root causes"
    )
    next_steps: list[str] = Field(
        description="Prioritized investigation actions with exact commands"
    )
    eliminated: list[str] = Field(
        description="Ruled-out possibilities and the evidence that eliminated them"
    )


# Discriminated union for the two analysis types
TechnicalAnalysis = Union[ResolvedAnalysis, NeedsDataAnalysis]


class TroubleshootingResponse(BaseModel):
    """Response model for troubleshooting analysis."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        # Allow arbitrary types for Union handling
        arbitrary_types_allowed=True,
    )

    analysis: TechnicalAnalysis
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence in analysis"
    )
    tools_used: list[str] = Field(
        default_factory=list, description="MCP tools utilized"
    )
    processing_time_seconds: float = Field(description="Time taken for analysis")


class InteractiveTroubleshootingResponse(BaseModel):
    """Response model for interactive follow-up questions."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        # Allow arbitrary types for Union handling
        arbitrary_types_allowed=True,
    )

    answer: str = Field(description="Direct answer to the user's question")
    additional_findings: list[str] = Field(
        default_factory=list, description="Any new findings discovered while answering"
    )
    references_used: list[str] = Field(
        default_factory=list,
        description="References to initial analysis or new tools used",
    )


class ProductResult(BaseModel):
    """Product identification result."""

    product: list[str] = Field(
        description="List of products directly involved in the evidence, symptoms, or cause"
    )


class SymptomsResult(BaseModel):
    """Symptoms identification result."""

    symptoms: list[str] = Field(
        description="High-level, human-observable failure descriptions"
    )


# Future: Easy to add new response types for different analysis tasks
class IssueClassificationResponse(BaseModel):
    """Future: General issue classification beyond just product labels."""

    pass
