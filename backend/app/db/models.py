"""
SQLAlchemy ORM models representing persistent domain entities.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.db.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("LearnerProfileDB", back_populates="user", uselist=False, cascade="all, delete-orphan")


class LearnerProfileDB(Base):
    __tablename__ = "learner_profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Step 1: Current status
    user_status = Column(String, default="Engineering Student")  # Student, Graduate, Professional, Switcher
    
    # Step 2: Education
    engineering_branch = Column(String, default="Computer Engineering / IT")
    college_name = Column(String, nullable=True)
    current_year = Column(String, default="3rd Year")
    graduation_year = Column(Integer, default=2026)
    
    # Step 3: Interests & Aspirations
    interests = Column(JSON, default=list)  # list of strings
    career_goal_status = Column(String, default="I have 2-3 careers in mind")
    target_career_id = Column(String, nullable=True)
    
    # Step 4: Known Skills & Experience
    known_skills = Column(JSON, default=list)  # list of strings or dicts
    experience_level = Column(String, default="Intermediate")
    
    # Step 5: Preferences & Constraints
    hours_per_week = Column(Integer, default=10)
    preferred_format = Column(String, default="project-based")  # video, text, project-based, mixed
    learning_style = Column(String, default="practical")  # math-heavy, hands-on, conceptual
    max_budget = Column(String, default="free-and-paid")  # free-only, budget, flexible
    target_timeline_months = Column(Integer, default=6)
    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")
    skill_proficiencies = relationship("SkillProficiencyDB", back_populates="profile", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPathDB", back_populates="profile", cascade="all, delete-orphan")


class SkillProficiencyDB(Base):
    __tablename__ = "skill_proficiencies"

    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    skill_id = Column(String, nullable=False)
    skill_name = Column(String, nullable=False)
    current_proficiency = Column(Float, default=0.0)  # 0.0 to 1.0 (or 0 to 100%)
    target_proficiency = Column(Float, default=0.8)
    confidence = Column(Float, default=0.7)
    evidence_source = Column(String, default="self_report")  # self_report, assessment, project
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("LearnerProfileDB", back_populates="skill_proficiencies")


class LearningPathDB(Base):
    __tablename__ = "learning_paths"

    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    career_id = Column(String, nullable=False)
    career_title = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    estimated_total_hours = Column(Integer, default=120)
    estimated_weeks = Column(Integer, default=12)
    job_readiness_score = Column(Float, default=35.0)
    next_action = Column(JSON, nullable=True)
    what_not_to_do_warnings = Column(JSON, default=list)
    track_names = Column(JSON, default=list)

    profile = relationship("LearnerProfileDB", back_populates="learning_paths")
    milestones = relationship("MilestoneDB", back_populates="path", cascade="all, delete-orphan", order_by="MilestoneDB.sequence_order")


class MilestoneDB(Base):
    __tablename__ = "milestones"

    id = Column(String, primary_key=True, default=generate_uuid)
    path_id = Column(String, ForeignKey("learning_paths.id"), nullable=False)
    milestone_key = Column(String, nullable=False)  # e.g. "ms_1" -- stable within a path, NOT globally unique (unlike `id`)
    sequence_order = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_skills = Column(JSON, default=list)
    status = Column(String, default="not_started")  # not_started, in_progress, completed
    estimated_hours = Column(Integer, default=15)
    resources = Column(JSON, default=list)  # list of resource objects
    project = Column(JSON, nullable=True)
    assessment = Column(JSON, nullable=True)
    youtube_extras = Column(JSON, default=list)  # secondary "also on YouTube" list

    path = relationship("LearningPathDB", back_populates="milestones")


class LearnerModelDB(Base):
    """Per-learner adaptive ranker state (weights + affinities) updated from feedback."""
    __tablename__ = "learner_models"

    id = Column(String, primary_key=True, default=generate_uuid)
    profile_id = Column(String, ForeignKey("learner_profiles.id"), unique=True, nullable=False)
    weights = Column(JSON, default=dict)       # factor -> weight
    affinities = Column(JSON, default=dict)    # "track:X" / "provider:Y" -> delta
    update_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserFeedbackDB(Base):
    __tablename__ = "user_feedback"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    feedback_type = Column(String, nullable=False)  # upvote, downvote, dismiss, completed
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AssessmentSubmissionDB(Base):
    __tablename__ = "assessment_submissions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)
    assessment_id = Column(String, nullable=False)
    skill_id = Column(String, nullable=False)
    score_percentage = Column(Float, nullable=False)
    answers = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)
    sender = Column(String, nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
