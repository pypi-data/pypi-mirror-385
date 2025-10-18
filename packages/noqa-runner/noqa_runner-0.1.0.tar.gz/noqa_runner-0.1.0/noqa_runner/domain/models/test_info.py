"""Domain models for test information"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RunnerTestInfo(BaseModel):
    """Test case information for runner"""

    test_id: str = Field(description="Unique test identifier")
    case_instructions: str = Field(description="Natural language test instructions")
    case_name: str = Field(default="", description="Test case name")
