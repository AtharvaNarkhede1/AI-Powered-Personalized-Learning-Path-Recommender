"""
Authentication & Demo User Session API Endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, LearnerProfileDB
from app.models.schemas import UserCreate, UserLogin, TokenResponse, ProfileResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user account."""
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        hashed_password=f"hashed_{user_in.password}",  # Simple hash for hackathon demo
        full_name=user_in.full_name or "Engineering Learner"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize default profile
    profile = LearnerProfileDB(
        user_id=user.id,
        user_status="Engineering Student",
        engineering_branch="Computer Engineering / IT",
        interests=["AI", "Software", "Robotics"],
        known_skills=["Python", "HTML/CSS"]
    )
    db.add(profile)
    db.commit()

    return TokenResponse(
        access_token=f"demo_token_{user.id}",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )


@router.post("/login", response_model=TokenResponse)
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    """Logs in an existing user."""
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user:
        # Create quick demo account if not exists for easy testing
        user = User(
            email=user_in.email,
            hashed_password=f"hashed_{user_in.password}",
            full_name="Engineering Learner"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        profile = LearnerProfileDB(user_id=user.id)
        db.add(profile)
        db.commit()

    return TokenResponse(
        access_token=f"demo_token_{user.id}",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )


@router.post("/demo-login", response_model=TokenResponse)
def demo_login(db: Session = Depends(get_db)):
    """Instant one-click Hackathon Demo login."""
    demo_email = "demo.learner@hcl.edu"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        user = User(
            email=demo_email,
            hashed_password="demo_password",
            full_name="Alex Rivera (Mechanical & Robotics Student)"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = LearnerProfileDB(
            user_id=user.id,
            user_status="Engineering Student",
            engineering_branch="Mechanical Engineering",
            college_name="HCL Institute of Technology",
            current_year="3rd Year",
            graduation_year=2026,
            interests=["Robotics", "AI", "Embedded Systems"],
            known_skills=["Python", "SolidWorks", "Basic Electronics"],
            hours_per_week=10,
            preferred_format="project-based"
        )
        db.add(profile)
        db.commit()

    return TokenResponse(
        access_token=f"demo_token_{user.id}",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name
    )
