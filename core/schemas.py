# core/schemas.py
from pydantic import BaseModel, Field
from typing import List


class SuggestedContact(BaseModel):
    name: str = Field(description="The name of the employee.")
    department: str = Field(description="The department they work in.")
    email: str = Field(description="The employee's contact email.")


class AgentOutput(BaseModel):
    conversational_reply: str = Field(
        description="The main text response answering the user's question."
    )
    documents_cited: List[str] = Field(
        default_factory=list,
        description="A list of document names or policy sections referenced.",
    )
    suggested_contacts: List[SuggestedContact] = Field(
        default_factory=list,
        description="A list of relevant employees the user can contact.",
    )
