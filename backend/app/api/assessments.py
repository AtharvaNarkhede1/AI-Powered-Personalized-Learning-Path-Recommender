"""
Assessments & Diagnostic Quizzes Router.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.schemas import (
    AssessmentDetail, QuizSubmissionRequest, QuizSubmissionResponse
)
from app.data.taxonomy_data import QUIZZES_DATABASE
from app.api.paths import PATH_CACHE
from app.services.adaptive_engine import adapt_path_on_quiz_completion

router = APIRouter(prefix="/api/assessments", tags=["Assessments & Diagnostic Quizzes"])


@router.get("/quiz/{skill_id}", response_model=AssessmentDetail)
def get_quiz_by_skill(skill_id: str):
    """Retrieves diagnostic quiz for a specific skill."""
    if skill_id not in QUIZZES_DATABASE:
        # Fallback default quiz
        skill_id = "python_core"
    
    data = QUIZZES_DATABASE[skill_id]
    return AssessmentDetail(
        id=data["assessment_id"],
        skill_id=data["skill_id"],
        skill_name=data["skill_name"],
        title=data["title"],
        description=data["description"],
        questions=data["questions"]
    )


@router.post("/submit", response_model=QuizSubmissionResponse)
def submit_quiz_answers(payload: QuizSubmissionRequest):
    """Grades a quiz submission, updates skill proficiency, and triggers adaptive path updates."""
    # Find matching quiz
    quiz_data = None
    for sid, qdata in QUIZZES_DATABASE.items():
        if qdata["assessment_id"] == payload.assessment_id:
            quiz_data = qdata
            break

    if not quiz_data:
        quiz_data = QUIZZES_DATABASE["python_core"]

    questions = quiz_data["questions"]
    correct_count = 0
    detailed_results = []

    for q in questions:
        q_id = q["id"]
        chosen_idx = payload.answers.get(q_id, -1)
        is_correct = (chosen_idx == q["correct_option_index"])
        if is_correct:
            correct_count += 1
        detailed_results.append({
            "question_id": q_id,
            "chosen_index": chosen_idx,
            "correct_index": q["correct_option_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    score_pct = round((correct_count / len(questions)) * 100, 1) if questions else 100.0
    passed = score_pct >= 60.0
    new_prof = 0.85 if score_pct >= 80.0 else (0.65 if score_pct >= 60.0 else 0.4)

    feedback = f"Excellent! You scored {score_pct}%. Your proficiency level in {quiz_data['skill_name']} is updated." if passed else f"You scored {score_pct}%. We recommend reviewing prerequisite modules before re-testing."

    # Update path if active
    for cid, path in PATH_CACHE.items():
        adapt_path_on_quiz_completion(path, quiz_data["skill_id"], score_pct)

    return QuizSubmissionResponse(
        assessment_id=quiz_data["assessment_id"],
        skill_id=quiz_data["skill_id"],
        score_percentage=score_pct,
        passed=passed,
        new_proficiency_level=new_prof,
        feedback=feedback,
        detailed_results=detailed_results
    )
