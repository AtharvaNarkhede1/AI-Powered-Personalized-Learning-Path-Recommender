from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
class UserLogin(BaseModel):
    email: str
    password: str
class PasswordResetRequest(BaseModel):
    email: str
    new_password: str
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: Optional[str] = None
class MeResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
class ResumeParseRequest(BaseModel):
    text: str
    exclude: List[str] = Field(default_factory=list)
class DetectedSkill(BaseModel):
    name: str
    confidence: float
    source: str
class ResumeParseResponse(BaseModel):
    detected_skills: List[DetectedSkill]
class IntakeParseRequest(BaseModel):
    text: str
    exclude_skills: List[str] = Field(default_factory=list)
    exclude_interests: List[str] = Field(default_factory=list)
class IntakeParseResponse(BaseModel):
    detected_skills: List[DetectedSkill]
    detected_interests: List[str]
    new_keywords: List[str]
    hours_per_week: Optional[int] = None
    experience_level: Optional[str] = None
    user_status: Optional[str] = None
    engineering_branch: Optional[str] = None
    target_timeline_months: Optional[int] = None
    summary: List[str]
class ProfileOnboardingRequest(BaseModel):
    user_id: str = "demo_user_1"
    user_status: str = "Engineering Student"
    engineering_branch: str = "Computer Engineering / IT"
    college_name: Optional[str] = None
    current_year: str = "3rd Year"
    graduation_year: int = 2026
    interests: List[str] = Field(default_factory=list)
    career_goal_status: str = "I have 2-3 careers in mind"
    target_career_id: Optional[str] = None
    known_skills: List[str] = Field(default_factory=list)
    experience_level: str = "Intermediate"
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
class CareerMatchScore(BaseModel):
    career_id: str
    title: str
    branch_primary: str
    match_percentage: float  
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
    options: List[Dict[str, str]] 
class CareerDiscoveryResponse(BaseModel):
    top_matches: List[CareerMatchScore]
    clarification_needed: bool = False
    clarification_question: Optional[CareerClarificationQuestion] = None
    cross_branch_advice: Optional[str] = None
class CareerComparisonRequest(BaseModel):
    career_ids: List[str] = Field(min_length=2, max_length=3)
class CareerDetail(BaseModel):
    career_id: str
    title: str
    category: str
    branch_primary: str
    description: str
    avg_salary_range: str
    job_demand: str 
    key_responsibilities: List[str]
    required_skills: List[Dict[str, Any]] 
    day_in_the_life: str
    hard_realities: List[str]
    common_misconceptions: List[str]
    future_evolution: List[str]
    emerging_specializations: List[str]
    what_not_to_do: List[str]
class SkillGapItem(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    current_level: float 
    required_level: float
    gap_delta: float
    status: str 
    is_prerequisite: bool = False
    dependencies: List[str] = Field(default_factory=list)
class SkillGapAnalysisResponse(BaseModel):
    career_id: str
    career_title: str
    overall_readiness_pct: float
    gaps: List[SkillGapItem]
    prerequisite_warnings: List[str]
class ResourceItem(BaseModel):
    id: str
    title: str
    type: str 
    provider: str
    url: str
    duration_hours: float
    difficulty: str 
    skills_covered: List[str]
    rating: float = 4.8
    is_free: bool = True
    completed: bool = False
    match_reason: Optional[str] = None
    upvotes: int = 0
    downvotes: int = 0
    course_id: Optional[str] = None
    track: Optional[str] = None
    branch: Optional[str] = None
    num_reviews: int = 0
    why_now: Optional[str] = None
    unlocks: List[str] = Field(default_factory=list)
    factor_contributions: Optional[Dict[str, float]] = None
class RecommendationRequest(BaseModel):
    goal_text: Optional[str] = None
    career_id: Optional[str] = None
    limit: int = 12
    exclude_planned: bool = False
    user_id: str = "demo_user_1"
    skill_filter: Optional[str] = None
    type_filter: Optional[str] = None
    max_duration_hours: Optional[float] = None
class CourseRecommendationResponse(BaseModel):
    goal: str
    count: int
    results: List[ResourceItem]
class ResourceFeedbackRequest(BaseModel):
    resource_id: str
    feedback_type: str 
    comment: Optional[str] = None
    user_id: str = "demo_user_1"
class Milestone(BaseModel):
    id: str
    sequence_order: int
    title: str
    description: str
    estimated_hours: int
    estimated_weeks: int
    status: str = "not_started"
    target_skills: List[str]
    resources: List[ResourceItem]
    project: Optional[Dict[str, Any]] = None
    assessment: Optional[Dict[str, Any]] = None
    youtube_extras: List[ResourceItem] = Field(default_factory=list)
class NextRecommendedAction(BaseModel):
    action_type: str  
    title: str
    description: str
    milestone_id: str
    resource_id: Optional[str] = None
    estimated_minutes: int = 30
    urgency: str = "normal" 
class AddCourseRequest(BaseModel):
    course_id: str
    milestone_key: Optional[str] = None
class RemoveCourseRequest(BaseModel):
    resource_id: str
    milestone_key: str
class PhaseExplanation(BaseModel):
    milestone_key: str
    title: str
    explanation: str
class PathExplanationResponse(BaseModel):
    overview: str
    phases: List[PhaseExplanation]
class LearningPathResponse(BaseModel):
    id: str
    career_id: str
    career_title: str
    job_readiness_score: float
    base_readiness_score: float = 0.0
    estimated_total_hours: int
    estimated_weeks: int
    hours_per_week: int
    milestones: List[Milestone]
    next_action: NextRecommendedAction
    what_not_to_do_warnings: List[str]
    track_names: List[str] = Field(default_factory=list)
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
    answers: Dict[str, int] 
    user_id: str = "demo_user_1"
    career_id: Optional[str] = None 
    course_id: Optional[str] = None 
class QuizSubmissionResponse(BaseModel):
    assessment_id: str
    skill_id: str
    score_percentage: float
    passed: bool
    new_proficiency_level: float
    feedback: str
    detailed_results: List[Dict[str, Any]]
class ChatMessageSchema(BaseModel):
    sender: str  # user | assistant
    content: str
    created_at: Optional[datetime] = None
class ChatRequest(BaseModel):
    message: str
    context_career_id: Optional[str] = None
    chat_history: Optional[List[ChatMessageSchema]] = None
    user_id: str = "demo_user_1"
class ChatResponse(BaseModel):
    reply: str
    suggested_followups: List[str] = Field(default_factory=list)
    referenced_resources: List[ResourceItem] = Field(default_factory=list)
    referenced_warnings: List[str] = Field(default_factory=list)
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
    skill_radar_data: List[Dict[str, Any]] 
    active_path: Optional[LearningPathResponse] = None
    recent_courses: List[ResourceItem] = Field(default_factory=list)
    has_path: bool = True