"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ContextRequest(BaseModel):
    """Request model for /context/file endpoint"""
    repo_path: str = Field(..., description="Absolute path to Git repository root")
    file_path: str = Field(..., description="Absolute path to the file to analyze")
    selected_code: Optional[str] = Field(None, description="Optional selected code snippet to explain")
    commit_limit: int = Field(50, description="Maximum number of commits to analyze", ge=1, le=100)


class DesignDecision(BaseModel):
    """A single design decision extracted from commit history"""
    title: str = Field(..., description="Short title of the design decision")
    description: str = Field(..., description="One-line explanation of the decision")
    commits: List[str] = Field(default_factory=list, description="List of commit SHAs related to this decision")


class RelatedFile(BaseModel):
    """A related file that developers should read"""
    path: str = Field(..., description="Relative path to the related file")
    reason: str = Field(..., description="Why this file is related")


class ContextResponse(BaseModel):
    """Response model for /context/file endpoint"""
    summary: str = Field(..., description="2-3 sentence summary of what the file does")
    decisions: List[DesignDecision] = Field(default_factory=list, description="Key design decisions from Git history")
    related_files: List[RelatedFile] = Field(default_factory=list, description="Related files to read next")
    weird_code_explanation: Optional[str] = Field(None, description="Explanation of selected code if provided")
    metadata: dict = Field(default_factory=dict, description="Additional metadata about the analysis")
