from typing import Dict, Optional
from pydantic import BaseModel, Field

class PostInput(BaseModel):
    content: str = Field(description="The content to create a post about")
    style: Optional[str] = Field(
        description="Style of the post (professional, casual, technical)", 
        default="professional"
    )

class FeedbackAnalysis(BaseModel):
    sentiment: str
    reasoning: str
    action: str
