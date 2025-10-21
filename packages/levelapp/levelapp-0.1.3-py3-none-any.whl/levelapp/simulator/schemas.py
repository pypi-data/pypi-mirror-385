"""
levelapp/simulator/schemas.py

Defines Pydantic models for simulator-related data structures,
including test configurations, batch metadata, and evaluation results.
"""
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime

from typing import Dict, Any, List
from pydantic import BaseModel, Field, computed_field, field_validator

from levelapp.evaluator.evaluator import JudgeEvaluationResults


class InteractionLevel(str, Enum):
    """Enum representing the type of interaction."""
    INITIAL = "initial"
    INTERMEDIATE = "intermediate"
    FINAL = "final"


class Interaction(BaseModel):
    """Represents a single interaction within a conversation."""
    id: UUID = Field(default_factory=uuid4, description="Interaction identifier")
    user_message: str = Field(..., description="The user's query message")
    # generated_reply: str = Field(..., description="The agent's reply message")
    reference_reply: str = Field(..., description="The preset reference message")
    interaction_type: InteractionLevel = Field(default=InteractionLevel.INITIAL, description="Type of interaction")
    reference_metadata: Dict[str, Any] = Field(default_factory=dict, description="Expected metadata")
    # generated_metadata: Dict[str, Any] = Field(default_factory=dict, description="Extracted metadata")
    guardrail_flag: bool = Field(default=False, description="Flag for guardrail signaling")
    request_payload: Dict[str, Any] = Field(default_factory=dict, description="Additional request payload")


class ConversationScript(BaseModel):
    """Represents a basic conversation with multiple interactions."""
    id: UUID = Field(default_factory=uuid4, description="Conversation identifier")
    interactions: List[Interaction] = Field(default_factory=list, description="List of interactions")
    description: str = Field(default="no-description", description="A short description of the conversation")
    details: Dict[str, str] = Field(default_factory=dict, description="Conversation details")


class ScriptsBatch(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Batch identifier")
    scripts: List[ConversationScript] = Field(default_factory=list, description="List of conversation scripts")


# ---- Interaction Details Models ----
class InteractionResults(BaseModel):
    """Represents metadata extracted from a VLA interaction."""
    generated_reply: str | None = "No response"
    generated_metadata: Dict[str, Any] | None = {}
    guardrail_flag: Any | None = False
    interaction_type: str | None = ""


class InteractionEvaluationResults(BaseModel):
    """Model representing the evaluation result of an interaction."""
    judge_evaluations: Dict[str, JudgeEvaluationResults] | None = Field(default_factory=dict)
    metadata_evaluation: Dict[str, float] | None = Field(default_factory=dict)
    guardrail_flag: int = Field(default=0)


class SimulationResults(BaseModel):
    # Collected data
    started_at: datetime = datetime.now()
    finished_at: datetime
    # Collected Results
    evaluation_summary: Dict[str, Any] | None = Field(default_factory=dict, description="Evaluation result")
    average_scores: Dict[str, Any] | None = Field(default_factory=dict, description="Average scores")
    interaction_results: List[Dict[str, Any]] | None = Field(default_factory=list, description="detailed results")

    @computed_field
    @property
    def batch_id(self) -> str:
        return str(uuid4())

    @computed_field
    @property
    def elapsed_time(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()
