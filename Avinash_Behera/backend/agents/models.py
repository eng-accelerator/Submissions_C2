"""
Pydantic models for structured output parsing from LLM responses.
These models ensure type safety and validation for agent outputs.
"""
from typing import List, Literal
from pydantic import BaseModel, Field


# ============ Visual Agent Models ============

class VisualIssue(BaseModel):
    """Individual visual design issue"""
    description: str = Field(description="Clear description of the issue")
    impact: Literal["High", "Medium", "Low"] = Field(description="Impact level on user experience")
    effort: Literal["High", "Medium", "Low"] = Field(description="Effort required to fix")
    recommendation: str = Field(description="Specific actionable recommendation")


class VisualAnalysisResult(BaseModel):
    """Complete visual analysis for a single screen"""
    strengths: List[str] = Field(description="List of design strengths", default_factory=list)
    issues: List[VisualIssue] = Field(description="List of design issues", default_factory=list)


class VisualBatchResult(BaseModel):
    """Batch visual analysis results for multiple screens"""
    screens: dict[str, VisualAnalysisResult] = Field(
        description="Dictionary mapping screen paths to analysis results"
    )


# ============ UX Agent Models ============

class UsabilityProblem(BaseModel):
    """Individual usability problem"""
    description: str = Field(description="Clear description of the usability issue")
    impact: Literal["High", "Medium", "Low"] = Field(description="Impact on user experience")
    effort: Literal["High", "Medium", "Low"] = Field(description="Effort to fix")
    improvement: str = Field(description="Suggested improvement")


class UXAnalysisResult(BaseModel):
    """Complete UX analysis for a single screen"""
    usability_problems: List[UsabilityProblem] = Field(
        description="List of usability problems",
        default_factory=list
    )
    confusing_elements: List[str] = Field(
        description="Elements that may confuse users",
        default_factory=list
    )
    improvements: List[str] = Field(
        description="General improvement suggestions",
        default_factory=list
    )


class UXBatchResult(BaseModel):
    """Batch UX analysis results for multiple screens"""
    screens: dict[str, UXAnalysisResult] = Field(
        description="Dictionary mapping screen paths to analysis results"
    )


# ============ Helper Functions ============

def get_visual_json_schema() -> str:
    """Returns JSON schema for visual analysis"""
    return VisualAnalysisResult.model_json_schema()


def get_ux_json_schema() -> str:
    """Returns JSON schema for UX analysis"""
    return UXAnalysisResult.model_json_schema()
