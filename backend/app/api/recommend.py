"""
Recommendation endpoints.

Endpoints:
  GET  /api/recommend/{learner_id}              - top course/project recommendations
  POST /api/recommend/{learner_id}/explain      - explain why a specific course was recommended
  POST /api/recommend/{learner_id}/ask          - free-form Q&A about recommendations

TODO:
- Add POST /api/recommend/{learner_id}/feedback so learners can upvote/
  dismiss a recommendation, feeding back into recommendation_engine scoring.
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    RecommendationResponse, ExplainRequest, AssistantQueryRequest, AssistantQueryResponse,
)
from app.services.recommendation_engine import recommend_courses, load_courses
from app.services.ai_assistant import explain_recommendation, answer_question
from app.db import get_or_create_profile

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


@router.get("/{learner_id}", response_model=RecommendationResponse)
def get_recommendations(learner_id: str, limit: int = 5):
    profile = get_or_create_profile(learner_id)
    recs = recommend_courses(profile, limit=limit)
    return RecommendationResponse(learner_id=learner_id, recommendations=recs)


@router.post("/{learner_id}/explain")
def explain(learner_id: str, req: ExplainRequest):
    courses = {c["course_id"]: c for c in load_courses()}
    course = courses.get(req.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    profile = get_or_create_profile(learner_id)
    recs = recommend_courses(profile, limit=len(courses))
    matched = next((r for r in recs if r.course_id == req.course_id), None)
    reason = matched.reason if matched else "it fills a gap in your current skill set"
    return {"explanation": explain_recommendation(course["title"], reason)}


@router.post("/{learner_id}/ask", response_model=AssistantQueryResponse)
def ask(learner_id: str, req: AssistantQueryRequest):
    profile = get_or_create_profile(learner_id)
    recs = recommend_courses(profile, limit=10)
    answer = answer_question(profile, req.question, recs)
    return AssistantQueryResponse(answer=answer)
