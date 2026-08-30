from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.data.taxonomy_data import QUIZZES_DATABASE, SKILLS_DATABASE
from app.db import repository
from app.models.schemas import (
    AssessmentDetail, QuizSubmissionRequest, QuizSubmissionResponse,
)
from app.services.course_quiz import get_course_quiz
from app.services.progress import apply_progress
from app.services.skill_gap_engine import analyze_skill_gaps
router = APIRouter(prefix="/api/assessments", tags=["Assessments & Diagnostic Quizzes"])
@router.get("/quiz/{skill_id}", response_model=AssessmentDetail)
def get_quiz_by_skill(skill_id: str):
    if skill_id not in QUIZZES_DATABASE:
        skill_id = "python_core"
    data = QUIZZES_DATABASE[skill_id]
    return AssessmentDetail(
        id=data["assessment_id"], skill_id=data["skill_id"], skill_name=data["skill_name"],
        title=data["title"], description=data["description"], questions=data["questions"],
    )
@router.get("/course-quiz/{course_id}", response_model=AssessmentDetail)
def get_quiz_for_course(course_id: str, user=Depends(get_current_user)):
    quiz = get_course_quiz(course_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Course not found.")
    return AssessmentDetail(
        id=quiz["id"], skill_id=quiz["skill_id"], skill_name=quiz["skill_name"],
        title=quiz["title"], description=quiz["description"], questions=quiz["questions"],
    )
import re as _re
_NORM = _re.compile(r"[^a-z0-9]+")
def _skill_by_name(name: str):
    """(skill_id, skill_name) for a taxonomy skill matching `name`, else None."""
    target = _NORM.sub(" ", (name or "").lower()).strip()
    if not target:
        return None
    for sid, s in SKILLS_DATABASE.items():
        if _NORM.sub(" ", s["name"].lower()).strip() == target:
            return sid, s["name"]
    tw = set(target.split())
    for sid, s in SKILLS_DATABASE.items():
        sw = set(_NORM.sub(" ", s["name"].lower()).strip().split())
        if sw and len(tw & sw) / len(sw) >= 0.6:
            return sid, s["name"]
    return None
@router.post("/submit", response_model=QuizSubmissionResponse)
def submit_quiz_answers(payload: QuizSubmissionRequest, user=Depends(get_current_user)):
    is_course_quiz = payload.assessment_id.startswith("cq_")
    if is_course_quiz:
        course_id = payload.course_id or payload.assessment_id[3:]
        quiz = repository.get_course_quiz(course_id) or get_course_quiz(course_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Course quiz not found.")
        skill_id, skill_name = payload.assessment_id, quiz["skill_name"]
        questions = quiz["questions"]
        mapped = _skill_by_name(quiz.get("matched_skill") or quiz["skill_name"])
    else:
        quiz = next((q for q in QUIZZES_DATABASE.values() if q["assessment_id"] == payload.assessment_id),
                    QUIZZES_DATABASE["python_core"])
        skill_id, skill_name = quiz["skill_id"], quiz["skill_name"]
        questions = quiz["questions"]
        mapped = (skill_id, skill_name)
    correct = 0
    detailed = []
    for q in questions:
        chosen = payload.answers.get(q["id"], -1)
        ok = chosen == q["correct_option_index"]
        correct += int(ok)
        detailed.append({
            "question_id": q["id"], "chosen_index": chosen,
            "correct_index": q["correct_option_index"], "is_correct": ok,
            "explanation": q.get("explanation", ""),
        })
    score_pct = round((correct / len(questions)) * 100, 1) if questions else 100.0
    passed = score_pct >= 60.0
    new_prof = 0.85 if score_pct >= 80.0 else (0.65 if score_pct >= 60.0 else 0.4)
    feedback = (
        f"You scored {score_pct}%. Nice work on {skill_name}."
        if passed else
        f"You scored {score_pct}%. Review this course's material before re-testing."
    )
    repository.record_submission(user["_id"], payload.assessment_id, skill_id, score_pct, payload.answers)
    if mapped:
        repository.upsert_skill_proficiency(user["_id"], mapped[0], mapped[1], new_prof)
    career_id = payload.career_id or repository.profile_request_for(user["_id"]).target_career_id
    if career_id and mapped:
        path = repository.get_active_path(user["_id"], career_id)
        if path:
            try:
                gap = analyze_skill_gaps(career_id, repository.profile_request_for(user["_id"]), user_id=user["_id"])
                total_req = sum(g.required_level for g in gap.gaps) or 0.1
                total_acq = sum(min(g.current_level, g.required_level) for g in gap.gaps)
                path.base_readiness_score = round(min(100.0, max(15.0, (total_acq / total_req) * 100)), 1)
            except Exception:
                pass
            completed = repository.get_completed_resource_ids(user["_id"], career_id)
            path = apply_progress(path, set(completed))
            repository.save_path(user["_id"], path)
    return QuizSubmissionResponse(
        assessment_id=payload.assessment_id, skill_id=skill_id,
        score_percentage=score_pct, passed=passed, new_proficiency_level=new_prof,
        feedback=feedback, detailed_results=detailed,
    )