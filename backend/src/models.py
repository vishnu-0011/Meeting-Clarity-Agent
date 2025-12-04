from pydantic import BaseModel, Field
from typing import List

class JargonTerm(BaseModel):
    """Schema for a single jargon term identified by the LLM."""
    term: str = Field(description="The specific jargon word or phrase identified.")
    speaker: str = Field(description="The speaker who used the term (e.g., A, B).")
    frequency: int = Field(description="How many times this term was used by this speaker.")
    clarity_critique: str = Field(description="A brief LLM-generated critique suggesting a simpler replacement.")
    penalty_weight: float = Field(description="A score from 0.0 (low penalty) to 1.0 (high penalty) reflecting the term's ambiguity.")


class ClarityReport(BaseModel):
    """Overall report containing all identified jargon."""
    total_jargon_count: int = Field(description="Total number of jargon/ambiguous terms found.")
    identified_jargon: List[JargonTerm]
    overall_clarity_summary: str = Field(description="A brief summary of the communication clarity (50 words max).")