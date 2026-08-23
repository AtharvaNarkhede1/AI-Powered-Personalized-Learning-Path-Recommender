"""
Pydantic schemas for API request validation, response serialization, and data transport.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ---------- Auth & User ----------

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: Optional[str] = None


# ---------- Learner Profile ----------

class ProfileOnboardingRequest(BaseModel):
    # Step 1
    user_status: str = "Engineering Student"
    # Step 2
    engineering_branch: str = "Computer Engineering / IT"
    college_name: Optional[str] = None
    current_year: str = "3rd Year"
    graduation_year: int = 2026
    # Step 3
    interests: List[str] = Field(default_factory=list)
    career_goal_status: str = "I have 2-3 careers in mind"
    target_career_id: Optional[str] = None
    # Step 4
    known_skills: List[str] = Field(default_factory=list)
    experience_level: str = "Intermediate"
    # Step 5
    hours_per_week: int = 10
    preferred_format: str = "project-based"
    learning_style: str = "practical"
    max_budget: str = "free-and-paid"
    target_timeline_months: int = 6


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    user_status: str
    engineering_branch: str
    college_name: Optional[str] = None
    current_year: str
    graduation_year: int
    interests: List[str]
    career_goal_status: str
    target_career_id: Optional[str] = None
    known_skills: List[str]
    experience_level: str
    hours_per_week: int
    preferred_format: str
    learning_style: str
    max_budget: str
    target_timeline_months: int
    updated_at: Optional[datetime] = None


# ---------- Career Discovery & Matching ----------

class CareerMatchScore(BaseModel):
    career_id: str
    title: str
    branch_primary: str
    match_percentage: float  # e.g. 92.5
    match_reason: str
    skill_alignment_score: float
    interest_alignment_score: float
    branch_compatibility_score: float
    missing_critical_skills: List[str]
    transferable_skills: List[str]
    is_top_match: bool = False


class CareerClarificationQuestion(BaseModel):
    question_id: str
    question_text: str
    options: List[Dict[str, str]]  # [{'label': 'Physical systems', 'impact_career': 'robotics_eng'}, ...]


class CareerDiscoveryResponse(BaseModel):
    top_matches: List[CareerMatchScore]
    clarification_needed: bool = False
    clarification_question: Optional[CareerClarificationQuestion] = None
    cross_branch_advice: Optional[str] = None


class CareerComparisonRequest(BaseModel):
    career_ids: List[str] = Field(min_items=2, max_items=3)


class CareerDetail(BaseModel):
    career_id: str
    title: str
    category: str
    branch_primary: str
    description: str
    avg_salary_range: str
    job_demand: str  # High, Very High, Medium
    key_responsibilities: List[str]
    required_skills: List[Dict[str, Any]]  # [{'name': 'Python', 'level': 0.8, 'critical': True}]
    day_in_the_life: str
    hard_realities: List[str]
    common_misconceptions: List[str]
    future_evolution: List[str]
    emerging_specializations: List[str]
    what_not_to_do: List[str]


# ---------- Skill Gap Analysis ----------

class SkillGapItem(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    current_level: float  # 0.0 to 1.0
    required_level: float  # 0.0 to 1.0
    gap_delta: float  # max(0, required - current)
    status: str  # Mastered | Minor Gap | Major Gap | Missing
    is_prerequisite: bool = False
    dependencies: List[str] = Field(default_factory=list)


class SkillGapAnalysisResponse(BaseModel):
    career_id: str
    career_title: str
    overall_readiness_pct: float
    gaps: List[SkillGapItem]
    prerequisite_warnings: List[str]


# ---------- Recommendations & Resources ----------

class ResourceItem(BaseModel):
    id: str
    title: str
    type: str  # course, tutorial, project, documentation, video
    provider: str
    url: str
    duration_hours: float
    difficulty: str  # beginner, intermediate, advanced
    skills_covered: List[str]
    rating: float = 4.8
    is_free: bool = True
    match_reason: Optional[str] = None
    upvotes: int = 0
    downvotes: int = 0


class RecommendationRequest(BaseModel):
    career_id: Optional[str] = None
    skill_filter: Optional[str] = None
    type_filter: Optional[str] = None
    max_duration_hours: Optional[float] = None


class ResourceFeedbackRequest(BaseModel):
    resource_id: str
    feedback_type: str  # upvote, downvote, dismiss, completed
    comment: Optional[str] = None


# ---------- Learning Path & Milestones ----------

class Milestone(BaseModel):
    id: str
    sequence_order: int
    title: str
    description: str
    estimated_hours: int
    estimated_weeks: int
    status: str = "not_started"  # not_started, in_progress, completed
    target_skills: List[str]
    resources: List[ResourceItem]
    project: Optional[Dict[str, Any]] = None
    assessment: Optional[Dict[str, Any]] = None


class NextRecommendedAction(BaseModel):
    action_type: str  # start_course, complete_quiz, build_project, review_prerequisite
    title: str
    description: str
    milestone_id: str
    resource_id: Optional[str] = None
    estimated_minutes: int = 30
    urgency: str = "normal"  # high, normal, stretch


class LearningPathResponse(BaseModel):
    id: str
    career_id: str
    career_title: str
    job_readiness_score: float
    estimated_total_hours: int
    estimated_weeks: int
    hours_per_week: int
    milestones: List[Milestone]
    next_action: NextRecommendedAction
    what_not_to_do_warnings: List[str]


# ---------- Quiz & Assessments ----------

class QuizQuestion(BaseModel):
    id: str
    question_text: str
    options: List[str]
    correct_option_index: int
    explanation: str


class AssessmentDetail(BaseModel):
    id: str
    skill_id: str
    skill_name: str
    title: str
    description: str
    questions: List[QuizQuestion]


class QuizSubmissionRequest(BaseModel):
    assessment_id: str
    answers: Dict[str, int]  # question_id -> chosen option index


class QuizSubmissionResponse(BaseModel):
    assessment_id: str
    skill_id: str
    score_percentage: float
    passed: bool
    new_proficiency_level: float
    feedback: str
    detailed_results: List[Dict[str, Any]]


# ---------- AI Assistant & RAG ----------

class ChatMessageSchema(BaseModel):
    sender: str  # user | assistant
    content: str
    created_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    context_career_id: Optional[str] = None
    chat_history: Optional[List[ChatMessageSchema]] = None


class ChatResponse(BaseModel):
    reply: str
    suggested_followups: List[str] = Field(default_factory=list)
    referenced_resources: List[ResourceItem] = Field(default_factory=list)
    referenced_warnings: List[str] = Field(default_factory=list)


# ---------- Dashboard & Analytics ----------

class DashboardMetricsResponse(BaseModel):
    user_name: str
    engineering_branch: str
    target_career_title: str
    job_readiness_pct: float
    completed_milestones_count: int
    total_milestones_count: int
    hours_logged: float
    estimated_total_hours: float
    estimated_months_remaining: float
    next_action: NextRecommendedAction
    skill_radar_data: List[Dict[str, Any]]  # [{'skill': 'Python', 'current': 80, 'required': 90}]
    active_path: Optional[LearningPathResponse] = None
