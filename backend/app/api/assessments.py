from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import AssessmentSubmissionDB, SkillProficiencyDB, LearnerProfileDB
from app.models.schemas import AssessmentDetail, QuizSubmissionRequest, QuizSubmissionResponse, ProfileOnboardingRequest
from app.data.taxonomy_data import QUIZZES_DATABASE
from app.services.skill_gap_engine import analyze_skill_gaps
from app.services.path_store import get_active_path, save_path
router = APIRouter(prefix='/api/assessments', tags=['Assessments & Diagnostic Quizzes'])

@router.get('/quiz/{skill_id}', response_model=AssessmentDetail)
def get_quiz_by_skill(skill_id: str):
    if skill_id not in QUIZZES_DATABASE:
        skill_id = 'python_core'
    data = QUIZZES_DATABASE[skill_id]
    return AssessmentDetail(id=data['assessment_id'], skill_id=data['skill_id'], skill_name=data['skill_name'], title=data['title'], description=data['description'], questions=data['questions'])

@router.post('/submit', response_model=QuizSubmissionResponse)
def submit_quiz_answers(payload: QuizSubmissionRequest, db: Session=Depends(get_db)):
    quiz_data = None
    for sid, qdata in QUIZZES_DATABASE.items():
        if qdata['assessment_id'] == payload.assessment_id:
            quiz_data = qdata
            break
    if not quiz_data:
        quiz_data = QUIZZES_DATABASE['python_core']
    questions = quiz_data['questions']
    correct_count = 0
    detailed_results = []
    for q in questions:
        q_id = q['id']
        chosen_idx = payload.answers.get(q_id, -1)
        is_correct = chosen_idx == q['correct_option_index']
        if is_correct:
            correct_count += 1
        detailed_results.append({'question_id': q_id, 'chosen_index': chosen_idx, 'correct_index': q['correct_option_index'], 'is_correct': is_correct, 'explanation': q['explanation']})
    score_pct = round(correct_count / len(questions) * 100, 1) if questions else 100.0
    passed = score_pct >= 60.0
    new_prof = 0.85 if score_pct >= 80.0 else 0.65 if score_pct >= 60.0 else 0.4
    feedback = f'Excellent! You scored {score_pct}%. Your proficiency level in {quiz_data['skill_name']} is updated.' if passed else f'You scored {score_pct}%. We recommend reviewing prerequisite modules before re-testing.'
    db.add(AssessmentSubmissionDB(user_id=payload.user_id, assessment_id=quiz_data['assessment_id'], skill_id=quiz_data['skill_id'], score_percentage=score_pct, answers=payload.answers))
    profile_row = db.query(LearnerProfileDB).filter(LearnerProfileDB.user_id == payload.user_id).first()
    if profile_row:
        prof_row = db.query(SkillProficiencyDB).filter(SkillProficiencyDB.profile_id == profile_row.id, SkillProficiencyDB.skill_id == quiz_data['skill_id']).first()
        if not prof_row:
            prof_row = SkillProficiencyDB(profile_id=profile_row.id, skill_id=quiz_data['skill_id'], skill_name=quiz_data['skill_name'])
            db.add(prof_row)
        prof_row.current_proficiency = new_prof
        prof_row.confidence = 0.9
        prof_row.evidence_source = 'assessment'
    db.commit()
    if profile_row:
        career_id = payload.career_id or profile_row.target_career_id
        if career_id:
            path = get_active_path(db, profile_row.id, career_id)
            if path:
                context_profile = ProfileOnboardingRequest(user_id=payload.user_id, engineering_branch=profile_row.engineering_branch, known_skills=profile_row.known_skills or [], experience_level=profile_row.experience_level, hours_per_week=profile_row.hours_per_week)
                try:
                    gap = analyze_skill_gaps(career_id, context_profile, db=db, profile_id=profile_row.id)
                    total_req = sum((g.required_level for g in gap.gaps)) or 0.1
                    total_acq = sum((min(g.current_level, g.required_level) for g in gap.gaps))
                    path.job_readiness_score = round(min(100.0, max(15.0, total_acq / total_req * 100)), 1)
                except Exception:
                    boost = 5.0 if score_pct >= 80 else 2.5 if score_pct >= 60 else 0.0
                    path.job_readiness_score = round(min(100.0, path.job_readiness_score + boost), 1)
                path.next_action.action_type = 'build_project'
                path.next_action.title = 'Build the milestone portfolio project'
                path.next_action.description = f'You scored {score_pct}% -- apply it in the milestone project.'
                save_path(db, profile_row.id, path)
    return QuizSubmissionResponse(assessment_id=quiz_data['assessment_id'], skill_id=quiz_data['skill_id'], score_percentage=score_pct, passed=passed, new_proficiency_level=new_prof, feedback=feedback, detailed_results=detailed_results)
