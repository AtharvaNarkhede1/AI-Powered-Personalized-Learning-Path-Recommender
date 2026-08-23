"""
Personalized 'What NOT to Do' Guidance Engine.
Generates tailored warnings based on:
- Engineering branch & career choice mismatches
- Missing prerequisite gaps
- Learning style traps (e.g. certificate hoarding without hands-on projects)
- Trend chasing vs foundational understanding
"""
from typing import List
from app.models.schemas import ProfileOnboardingRequest, SkillGapItem
from app.data.taxonomy_data import CAREERS_DATABASE


def generate_what_not_to_do_warnings(
    profile: ProfileOnboardingRequest,
    target_career_id: str,
    skill_gaps: List[SkillGapItem]
) -> List[str]:
    """Generates 3 to 5 targeted, highly actionable personalized warnings."""
    warnings: List[str] = []

    target_career = next((c for c in CAREERS_DATABASE if c["career_id"] == target_career_id), None)
    career_title = target_career["title"] if target_career else "your chosen career"

    # Rule 1: Specific career warnings from dataset taxonomy
    if target_career and "what_not_to_do" in target_career:
        warnings.extend(target_career["what_not_to_do"][:2])

    # Rule 2: Prerequisite skip warnings
    missing_prereqs = [g for g in skill_gaps if g.status in ["Missing", "Major Gap"] and g.is_prerequisite]
    if missing_prereqs:
        p_names = ", ".join([g.skill_name for g in missing_prereqs[:2]])
        warnings.append(f"DON'T jump directly into advanced {career_title} projects while foundational skills ({p_names}) remain unmastered.")

    # Rule 3: Certificate vs Project trap
    if profile.preferred_format in ["video", "text"]:
        warnings.append("DON'T collect online course certificates without building at least 2 end-to-end practical, portfolio-ready projects.")

    # Rule 4: Weekly pacing warning
    if profile.hours_per_week < 5:
        warnings.append("DON'T schedule less than 5 hours per week if targeting job-readiness within 6 months—consistency is critical.")

    # Deduplicate while preserving order
    unique_warnings = []
    for w in warnings:
        if w not in unique_warnings:
            unique_warnings.append(w)

    return unique_warnings[:4]
