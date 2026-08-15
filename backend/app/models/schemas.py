"""
Pydantic request/response models shared across the API routers.

TODO:
- Once a real DB is wired up (see db.py), mirror these with SQLAlchemy ORM
  models and add `from_attributes = True` config for ORM -> schema conversion.
- Add stricter validation (enum for skill_level, min/max on hours_per_week).
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------- Learner profile ----------

class LearnerProfile(BaseModel):
    learner_id: str
    name: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    goal: Optional[str] = None
    skill_level: str = "beginner"  # beginner | intermediate | advanced
    completed_courses: List[str] = Field(default_factory=list)
    known_skills: List[str] = Field(default_factory=list)
    hours_per_week: int = 5
    preferred_format: Optional[str] = None  # video | text | project-based


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    interests: Optional[List[str]] = None
    goal: Optional[str] = None
    skill_level: Optional[str] = None
    completed_courses: Optional[List[str]] = None
    known_skills: Optional[List[str]] = None
    hours_per_week: Optional[int] = None
    preferred_format: Optional[str] = None


# ---------- Chat ----------

class ChatMessageRequest(BaseModel):
    learner_id: str
    message: str


class ChatMessageResponse(BaseModel):
    reply: str
    extracted_profile_updates: dict = Field(default_factory=dict)


# ---------- Recommendations ----------

class RecommendationItem(BaseModel):
    course_id: str
    title: str
    provider: str
    skill_tags: List[str]
    difficulty: str
    estimated_hours: int
    reason: str  # explanation for why this was recommended


class RecommendationResponse(BaseModel):
    learner_id: str
    recommendations: List[RecommendationItem]


# ---------- Learning path ----------

class Milestone(BaseModel):
    milestone_id: str
    title: str
    course_ids: List[str]
    project: Optional[str] = None
    assessment: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)
    status: str = "not_started"  # not_started | in_progress | completed


class LearningPath(BaseModel):
    learner_id: str
    goal: str
    milestones: List[Milestone]
    total_estimated_hours: int


# ---------- Progress ----------

class ProgressUpdateRequest(BaseModel):
    learner_id: str
    milestone_id: str
    status: str  # not_started | in_progress | completed


class ProgressSnapshot(BaseModel):
    learner_id: str
    completed_milestones: int
    total_milestones: int
    completion_percent: float
    skill_growth: dict  # skill -> proficiency 0-100
    next_actions: List[str]


# ---------- Explanations / assistant Q&A ----------

class ExplainRequest(BaseModel):
    learner_id: str
    course_id: str


class AssistantQueryRequest(BaseModel):
    learner_id: str
    question: str


class AssistantQueryResponse(BaseModel):
    answer: str
