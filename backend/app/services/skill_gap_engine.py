from typing import List, Dict, Any, Optional
from app.data.taxonomy_data import CAREERS_DATABASE, SKILLS_DATABASE
from app.models.schemas import SkillGapItem, SkillGapAnalysisResponse, ProfileOnboardingRequest
from app.ml.engine import engine
SEMANTIC_MATCH_THRESHOLD = 0.55
def _best_match(name: str, candidates) -> float:
    try:
        return engine.best_text_sim(name, candidates or [])
    except Exception:
        n = name.lower()
        best = 0.0
        for c in (candidates or []):
            cl = str(c).lower()
            if cl in n or n in cl:
                best = max(best, 0.75)
            else:
                ta, tb = set(n.split()), set(cl.split())
                if ta and tb:
                    best = max(best, len(ta & tb) / len(ta | tb))
        return best
def _verified_proficiency(user_id: Optional[str], skill_id: str) -> Optional[float]:
    """Looks up a quiz/assessment-verified proficiency for this skill, if one exists."""
    if not user_id:
        return None
    try:
        from app.db import repository
        return repository.get_verified_proficiency(user_id, skill_id)
    except Exception:
        return None
def analyze_skill_gaps(
    career_id: str,
    profile: ProfileOnboardingRequest,
    user_id: Optional[str] = None,
) -> SkillGapAnalysisResponse:
    """Computes individual skill gaps for a target career given user's known skills and experience."""
    target_career = next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), CAREERS_DATABASE[0])
    exp_level = profile.experience_level.lower()
    base_prof = 0.5 if "intermediate" in exp_level else (0.75 if "advanced" in exp_level else 0.25)
    gaps: List[SkillGapItem] = []
    total_required = 0.0
    total_acquired = 0.0
    prereq_warnings: List[str] = []
    for req in target_career["required_skills"]:
        s_id = req["skill_id"]
        s_name = req["name"]
        req_level = req["level"]
        total_required += req_level
        tax_info = SKILLS_DATABASE.get(s_id, {})
        category = tax_info.get("category", "Technical")
        prereqs = tax_info.get("prerequisites", [])
        verified = _verified_proficiency(user_id, s_id)
        if verified is not None:
            curr_level = verified
        else:
            match_score = _best_match(s_name, profile.known_skills)
            if match_score >= SEMANTIC_MATCH_THRESHOLD:
                curr_level = min(1.0, base_prof + 0.2 * match_score)
            else:
                curr_level = 0.0
        total_acquired += min(curr_level, req_level)
        gap_delta = round(max(0.0, req_level - curr_level), 2)
        if gap_delta == 0.0:
            status = "Mastered"
        elif curr_level == 0.0:
            status = "Missing"
        elif gap_delta <= 0.3:
            status = "Minor Gap"
        else:
            status = "Major Gap"
        for prereq in prereqs:
            prereq_info = SKILLS_DATABASE.get(prereq, {})
            prereq_name = prereq_info.get("name", prereq)
            if curr_level < 0.3:
                prereq_warnings.append(f"Prerequisite '{prereq_name}' must be mastered before advancing in '{s_name}'.")
        gaps.append(SkillGapItem(
            skill_id=s_id,
            skill_name=s_name,
            category=category,
            current_level=round(curr_level, 2),
            required_level=req_level,
            gap_delta=gap_delta,
            status=status,
            is_prerequisite=req.get("critical", False),
            dependencies=prereqs
        ))
    overall_pct = round((total_acquired / max(0.1, total_required)) * 100, 1)
    return SkillGapAnalysisResponse(
        career_id=target_career["career_id"],
        career_title=target_career["title"],
        overall_readiness_pct=min(100.0, overall_pct),
        gaps=gaps,
        prerequisite_warnings=list(set(prereq_warnings))[:3]
    )