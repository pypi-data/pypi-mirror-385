"""
Relationship schema for semantic edges between memory nodes.

Generic schema - works for any memory type pairs.
Prompt templates control the specific guidance.
"""

from pydantic import BaseModel, Field


class MemoryRelationship(BaseModel):
    """
    Generic semantic relationship between any two memory nodes.
    
    Works for: Learning→Cognition, Learning→Learning, Observation→Learning, etc.
    Prompt template defines the specific relationship criteria.
    """
    
    is_related: bool = Field(
        ...,
        description="Does source have meaningful semantic relationship to target?"
    )
    
    relation_context: str = Field(
        default="",
        description="Relationship quality/nature for semantic queries (e.g., 'is explained in detail by', 'contradicts')"
    )
    
    inverse_context: str = Field(
        default="",
        description="Inverse relationship quality/nature for semantic queries"
    )
    
    relation_keyword: str = Field(
        default="",
        description="Structured edge type (UPPERCASE_WITH_UNDERSCORES)"
    )
    
    inverse_keyword: str = Field(
        default="",
        description="Reverse edge type (UPPERCASE_WITH_UNDERSCORES)"
    )


# Backward compatibility alias
LearningCognitionRelationship = MemoryRelationship

