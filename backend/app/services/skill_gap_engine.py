"""
Skill Gap Analysis Engine.
Calculates skill gap delta: Delta = max(0, Required_Level - Current_Level)
Categorizes skills into:
- Mastered (gap == 0)
- Minor Gap (gap <= 0.3)
- Major Gap (gap > 0.3)
- Missing (current == 0.0)
"""
from typing import List, Dict, Any
from app.data.taxonomy_data import CAREERS_DATABASE, SKILLS_DATABASE
from app.models.schemas import SkillGapItem, SkillGapAnalysisResponse, ProfileOnboardingRequest


def analyze_skill_gaps(career_id: str, profile: ProfileOnboardingRequest) -> SkillGapAnalysisResponse:
    """Computes individual skill gaps for a target career given user's known skills and experience."""
    target_career = next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), CAREERS_DATABASE[0])
    
    known_skills_lower = [s.lower() for s in profile.known_skills]
    exp_level = profile.experience_level.lower()

    # Base proficiency factor derived from experience level
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

        # Look up taxonomy metadata
        tax_info = SKILLS_DATABASE.get(s_id, {})
        category = tax_info.get("category", "Technical")
        prereqs = tax_info.get("prerequisites", [])

        # Estimate current user proficiency
        user_has_skill = any(ks in s_name.lower() or s_name.lower() in ks for ks in known_skills_lower)
        if user_has_skill:
            curr_level = min(1.0, base_prof + 0.2)
        else:
            curr_level = 0.0

        total_acquired += min(curr_level, req_level)
        gap_delta = round(max(0.0, req_level - curr_level), 2)

        # Status categorization
        if gap_delta == 0.0:
            status = "Mastered"
        elif curr_level == 0.0:
            status = "Missing"
        elif gap_delta <= 0.3:
            status = "Minor Gap"
        else:
            status = "Major Gap"

        # Prerequisite warning check
        for prereq in prereqs:
            prereq_info = SKILLS_DATABASE.get(prereq, {})
            prereq_name = prereq_info.get("name", prereq)
            # If prerequisite is missing but target skill is being attempted
            if curr_level < 0.3:
                prereq_warnings.append(f"Prerequisite '{prereq_name}' must be mastered before advancing in '{s_name}'.")

        gaps.append(SkillGapItem(
            skill_id=s_id,
            skill_name=s_name,
            category=category,
            current_level=curr_level,
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
