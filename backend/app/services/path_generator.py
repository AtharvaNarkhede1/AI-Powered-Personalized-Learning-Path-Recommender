"""
Learning Path Generator.

Turns a learner's goal + profile into an ordered sequence of milestones,
each grouping one or more courses, respecting prerequisite chains, and
finishing with a capstone project where one exists for the goal.

Algorithm (prototype-level, deterministic):
  1. Resolve the target skill set for the learner's goal.
  2. Pull every course relevant to those skills (incl. prerequisite chains,
     even if a prerequisite isn't itself "on topic").
  3. Topologically sort by prerequisites so earlier milestones unlock later
     ones.
  4. Group into milestones of ~1-2 courses each; attach a capstone project
     course as the final milestone if the dataset has one tagged "project".

TODO:
- Replace the fixed grouping (courses-per-milestone) with pacing based on
  profile.hours_per_week so milestones map to realistic calendar weeks.
- Support re-generating a path mid-course when progress/feedback signals
  the learner needs remediation (see api/progress.py TODO).
"""
from typing import List
from app.models.schemas import LearnerProfile, LearningPath, Milestone
from app.services.recommendation_engine import load_courses, goal_required_skills


def _topological_course_order(courses: List[dict]) -> List[dict]:
    by_id = {c["course_id"]: c for c in courses}
    visited = set()
    ordered = []

    def visit(course_id):
        if course_id in visited or course_id not in by_id:
            return
        visited.add(course_id)
        for prereq_id in by_id[course_id].get("prerequisites", []):
            visit(prereq_id)
        ordered.append(by_id[course_id])

    for c in courses:
        visit(c["course_id"])

    return ordered


def generate_learning_path(profile: LearnerProfile) -> LearningPath:
    all_courses = load_courses()
    target_skills = set(goal_required_skills(profile.goal) or [i.lower() for i in profile.interests])

    relevant = [c for c in all_courses if set(c["skill_tags"]) & target_skills]
    relevant_ids = {c["course_id"] for c in relevant}

    # pull in prerequisite courses even if not directly "on topic"
    by_id = {c["course_id"]: c for c in all_courses}
    expanded = dict((c["course_id"], c) for c in relevant)
    frontier = list(relevant)
    while frontier:
        course = frontier.pop()
        for prereq_id in course.get("prerequisites", []):
            if prereq_id not in expanded and prereq_id in by_id:
                expanded[prereq_id] = by_id[prereq_id]
                frontier.append(by_id[prereq_id])

    ordered = _topological_course_order(list(expanded.values()))
    ordered = [c for c in ordered if c["course_id"] not in profile.completed_courses]

    projects = [c for c in ordered if "project" in c["skill_tags"]]
    non_projects = [c for c in ordered if "project" not in c["skill_tags"]]

    milestones: List[Milestone] = []
    group_size = 2
    for i in range(0, len(non_projects), group_size):
        group = non_projects[i:i + group_size]
        milestones.append(
            Milestone(
                milestone_id=f"m{len(milestones) + 1}",
                title=" + ".join(c["title"] for c in group),
                course_ids=[c["course_id"] for c in group],
                prerequisites=[
                    p for c in group for p in c.get("prerequisites", [])
                    if p not in [g["course_id"] for g in group]
                ],
                assessment=f"Quiz: {', '.join(c['title'] for c in group)}",
            )
        )

    for project in projects:
        milestones.append(
            Milestone(
                milestone_id=f"m{len(milestones) + 1}",
                title=project["title"],
                course_ids=[project["course_id"]],
                project=project["title"],
                prerequisites=project.get("prerequisites", []),
                assessment="Project submission & peer review",
            )
        )

    total_hours = sum(
        by_id[cid]["estimated_hours"]
        for m in milestones
        for cid in m.course_ids
        if cid in by_id
    )

    return LearningPath(
        learner_id=profile.learner_id,
        goal=profile.goal or "General skill growth",
        milestones=milestones,
        total_estimated_hours=total_hours,
    )
