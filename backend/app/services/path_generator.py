"""
Learning Path & Prerequisite-Aware Roadmap Generator.
Generates an ordered milestone sequence respecting skill prerequisites, attaching courses, hands-on projects, diagnostic assessments, and calculating the Next Recommended Action.
"""
from typing import List, Dict, Any, Optional
from app.data.taxonomy_data import CAREERS_DATABASE, SKILLS_DATABASE, QUIZZES_DATABASE
from app.models.schemas import (
    LearningPathResponse, Milestone, ResourceItem, NextRecommendedAction,
    ProfileOnboardingRequest, SkillGapItem
)
from app.services.graph_engine import get_topologically_sorted_skills
from app.services.skill_gap_engine import analyze_skill_gaps
from app.services.recommendation_engine import retrieve_and_rank_resources
from app.services.what_not_to_do_engine import generate_what_not_to_do_warnings
from app.services.readiness_calculator import calculate_job_readiness_and_timeline


def generate_learning_path(
    career_id: str,
    profile: ProfileOnboardingRequest,
    feedback_history: Optional[Dict[str, str]] = None
) -> LearningPathResponse:
    """Generates a complete prerequisite-aware milestone roadmap for a selected career."""
    target_career = next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), CAREERS_DATABASE[0])
    
    # 1. Analyze skill gaps
    gap_analysis = analyze_skill_gaps(target_career["career_id"], profile)
    skill_gaps = gap_analysis.gaps

    # 2. Get target skill IDs
    target_skill_ids = [g.skill_id for g in skill_gaps if g.gap_delta > 0.0]
    if not target_skill_ids:
        target_skill_ids = [g.skill_id for g in skill_gaps]

    # 3. Topologically sort skills by prerequisites
    ordered_skill_ids = get_topologically_sorted_skills(target_skill_ids)

    # 4. Group into 3 to 5 structured Milestones
    milestones: List[Milestone] = []
    chunk_size = max(1, len(ordered_skill_ids) // 4 + (1 if len(ordered_skill_ids) % 4 != 0 else 0))
    
    hours_per_week = max(4, profile.hours_per_week)

    for i in range(0, len(ordered_skill_ids), chunk_size):
        milestone_skills = ordered_skill_ids[i:i + chunk_size]
        seq_num = len(milestones) + 1

        # Fetch resources for these skills
        m_resources: List[ResourceItem] = []
        for s_id in milestone_skills:
            ranked = retrieve_and_rank_resources(profile, target_career_id=career_id, skill_filter=s_id, feedback_history=feedback_history)
            if ranked:
                m_resources.extend(ranked[:2])

        # Deduplicate resources
        unique_res = []
        seen_ids = set()
        for r in m_resources:
            if r.id not in seen_ids:
                unique_res.append(r)
                seen_ids.add(r.id)

        # Milestone titles based on phase
        if seq_num == 1:
            title = f"Phase 1: Foundations & Core Tools"
            desc = "Master basic syntax, foundational math, and core development tools before advancing."
        elif seq_num == 2:
            title = f"Phase 2: Core Engineering & Systems"
            desc = "Build core technical proficiency, architecture understanding, and algorithm design."
        elif seq_num == 3:
            title = f"Phase 3: Advanced Applications & Frameworks"
            desc = "Implement complex models, control systems, pipelines, and industry frameworks."
        else:
            title = f"Phase 4: Industry Capstone & Readiness"
            desc = "Deliver end-to-end production systems, edge optimizations, and portfolio projects."

        est_hours = sum(r.duration_hours for r in unique_res) + 10
        est_weeks = max(1, round(est_hours / hours_per_week))

        # Attach project & assessment
        s_names = [SKILLS_DATABASE.get(sid, {}).get("name", sid) for sid in milestone_skills]
        project_obj = {
            "title": f"Hands-on Project: {s_names[0] if s_names else 'Engineering'} Implementation",
            "description": f"Build a practical working portfolio project demonstrating proficiency in {', '.join(s_names[:2])}.",
            "required_deliverable": "GitHub repo link + demo video"
        }

        quiz_obj = None
        for sid in milestone_skills:
            if sid in QUIZZES_DATABASE:
                quiz_info = QUIZZES_DATABASE[sid]
                quiz_obj = {
                    "assessment_id": quiz_info["assessment_id"],
                    "title": quiz_info["title"],
                    "description": quiz_info["description"]
                }
                break

        milestones.append(Milestone(
            id=f"ms_{seq_num}",
            sequence_order=seq_num,
            title=title,
            description=desc,
            estimated_hours=int(est_hours),
            estimated_weeks=int(est_weeks),
            status="in_progress" if seq_num == 1 else "not_started",
            target_skills=s_names,
            resources=unique_res[:3],
            project=project_obj,
            assessment=quiz_obj
        ))

    # 5. Job readiness and timeline calculations
    readiness_data = calculate_job_readiness_and_timeline(skill_gaps, profile)

    # 6. Next Recommended Action
    first_res = milestones[0].resources[0] if milestones and milestones[0].resources else None
    next_action = NextRecommendedAction(
        action_type="start_course",
        title=f"Start '{first_res.title}'" if first_res else "Begin Phase 1 Diagnostic Quiz",
        description=f"Complete your first resource in {milestones[0].title} to build momentum." if milestones else "Start onboarding quiz.",
        milestone_id=milestones[0].id if milestones else "ms_1",
        resource_id=first_res.id if first_res else None,
        estimated_minutes=45,
        urgency="high"
    )

    # 7. What NOT to do warnings
    warnings = generate_what_not_to_do_warnings(profile, target_career["career_id"], skill_gaps)

    return LearningPathResponse(
        id=f"path_{target_career['career_id']}",
        career_id=target_career["career_id"],
        career_title=target_career["title"],
        job_readiness_score=readiness_data["job_readiness_score"],
        estimated_total_hours=readiness_data["estimated_total_hours"],
        estimated_weeks=readiness_data["estimated_weeks"],
        hours_per_week=profile.hours_per_week,
        milestones=milestones,
        next_action=next_action,
        what_not_to_do_warnings=warnings
    )
