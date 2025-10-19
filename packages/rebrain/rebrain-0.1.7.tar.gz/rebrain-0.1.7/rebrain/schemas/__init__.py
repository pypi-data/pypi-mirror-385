"""
Unified schema module for rebrain pipeline.

All data models for observations, learnings, cognitions, and persona.
"""

from rebrain.schemas.observation import Observation, ObservationExtraction
from rebrain.schemas.learning import Learning, LearningSynthesis
from rebrain.schemas.cognition import Cognition, CognitionSynthesis
from rebrain.schemas.persona import Persona
from rebrain.schemas.relationship import (
    MemoryRelationship,
    LearningCognitionRelationship,  # Backward compatibility alias
)

__all__ = [
    "Observation",
    "ObservationExtraction",
    "Learning",
    "LearningSynthesis",
    "Cognition",
    "CognitionSynthesis",
    "Persona",
    "MemoryRelationship",
    "LearningCognitionRelationship",
]

