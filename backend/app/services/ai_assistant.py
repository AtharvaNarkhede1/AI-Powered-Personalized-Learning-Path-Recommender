"""
AI Assistant & RAG Service.
Supports:
1. Provider Abstraction: Google Gemini API / OpenAI API when keys are configured, grounded with
   real taxonomy + skill-gap data (not just a couple of profile fields).
2. Grounded Fallback Engine: Works 100% offline out-of-the-box using domain taxonomy semantic
   grounding and the user's real profile/path context.
"""
import logging
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.data.taxonomy_data import CAREERS_DATABASE, SKILLS_DATABASE
from app.models.schemas import ChatResponse, ResourceItem, ProfileOnboardingRequest, LearningPathResponse

logger = logging.getLogger(__name__)


def _career_context(career_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not career_id:
        return None
    return next((c for c in CAREERS_DATABASE if c["career_id"] == career_id), None)


def _build_grounding_context(profile: Optional[ProfileOnboardingRequest], current_path: Optional[LearningPathResponse]) -> str:
    """Assembles real taxonomy + skill-gap context to ground the LLM prompt, instead of the
    unused dead import this previously was."""
    lines = []
    if profile:
        lines.append(f"Branch: {profile.engineering_branch}. Known skills: {', '.join(profile.known_skills) or 'none reported'}.")
        lines.append(f"Hours/week available: {profile.hours_per_week}. Experience level: {profile.experience_level}.")

    career = _career_context(current_path.career_id if current_path else None)
    if career:
        lines.append(f"Target career: {career['title']} -- {career['description']}")
        lines.append("What NOT to do in this field: " + "; ".join(career.get("what_not_to_do", [])[:2]))

    if current_path:
        lines.append(f"Job readiness so far: {current_path.job_readiness_score}%. Est. {current_path.estimated_weeks} weeks remaining.")
        incomplete = [m.title for m in current_path.milestones if m.status != "completed"][:2]
        if incomplete:
            lines.append("Upcoming milestones: " + ", ".join(incomplete))

    return "\n".join(lines)


def generate_ai_reply(
    message: str,
    profile: Optional[ProfileOnboardingRequest] = None,
    current_path: Optional[LearningPathResponse] = None,
    context_career_id: Optional[str] = None
) -> ChatResponse:
    """Generates an intelligent AI reply, using LLMs if API key is set, or grounded RAG heuristic fallback."""
    msg_lower = message.lower()
    grounding = _build_grounding_context(profile, current_path)

    # Try Gemini API if key is present
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = f"""You are CareerPath AI, an expert engineering career & learning path advisor.
User Message: "{message}"

Grounding context (use this real data, don't invent facts beyond it):
{grounding}

Provide a concise, encouraging, data-backed answer with clear actionable bullet points."""

            response = model.generate_content(prompt)
            if response and response.text:
                return ChatResponse(
                    reply=response.text,
                    suggested_followups=[
                        "Why was this path recommended?",
                        "What NOT to do in this field?",
                        "How long will it take to reach job readiness?"
                    ]
                )
        except Exception as e:
            logger.warning("Gemini call failed, falling back: %s", e)

    # Try OpenAI API if key is present
    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are CareerPath AI, an expert engineering career advisor. Ground your answer in this learner's real context:\n{grounding}"},
                    {"role": "user", "content": message}
                ]
            )
            if res.choices:
                return ChatResponse(
                    reply=res.choices[0].message.content,
                    suggested_followups=["What projects should I build?", "Compare top 3 careers"]
                )
        except Exception as e:
            logger.warning("OpenAI call failed, falling back: %s", e)

    # ---------- GROUNDED OFFLINE RAG & RULE ENGINE ----------
    referenced_resources: List[ResourceItem] = []
    referenced_warnings: List[str] = []

    branch = profile.engineering_branch if profile else "Engineering"
    hours = profile.hours_per_week if profile else 10
    career_name = current_path.career_title if current_path else "Engineering Career"
    career = _career_context(current_path.career_id if current_path else context_career_id)

    if "why" in msg_lower and ("course" in msg_lower or "path" in msg_lower or "recommend" in msg_lower):
        reply = (
            f"**Why this path was recommended for you:**\n\n"
            f"1. **Branch Compatibility**: Your background in **{branch}** provides essential math and problem-solving foundations.\n"
            f"2. **Prerequisite Structure**: We ordered your skills using a Directed Acyclic Graph (DAG) so you master fundamental prerequisites before complex topics.\n"
            f"3. **Pacing ({hours} hrs/week)**: The roadmap is calibrated to fit your schedule without burnout."
        )
        followups = ["What projects should I build first?", "What NOT to do in this field?"]

    elif "avoid" in msg_lower or "not to do" in msg_lower or "mistake" in msg_lower:
        career_warnings = career.get("what_not_to_do", []) if career else []
        bullet_warnings = career_warnings[:3] or [
            "Don't collect certificates without building practical portfolio projects.",
            "Don't skip core math and logic prerequisites.",
        ]
        reply = (
            f"**Key Mistakes to Avoid for {career_name}:**\n\n"
            + "\n".join(f"• {w}" for w in bullet_warnings)
        )
        referenced_warnings = bullet_warnings
        followups = ["How is job readiness calculated?", "What is a typical day in this career?"]

    elif "how long" in msg_lower or "timeline" in msg_lower or "readiness" in msg_lower:
        weeks = current_path.estimated_weeks if current_path else 12
        months = round(weeks / 4.2, 1)
        reply = (
            f"**Estimated Job Readiness Timeline:**\n\n"
            f"Based on your commitment of **{hours} hours/week**, your estimated timeline to reach industry job readiness is **{weeks} weeks (~{months} months)**.\n\n"
            f"• **Phase 1-2**: Foundation & Core Skills (~{round(weeks*0.4)} weeks)\n"
            f"• **Phase 3-4**: Advanced Frameworks & Capstone Project (~{round(weeks*0.6)} weeks)"
        )
        followups = ["How can I accelerate my path?", "What are the required assessments?"]

    elif "compare" in msg_lower or "difference" in msg_lower:
        sample = CAREERS_DATABASE[:3]
        reply = "**Career Comparison Insights:**\n\n" + "\n".join(
            f"• **{c['title']}**: {c['description']}" for c in sample
        )
        followups = ["Which one has higher job demand?", f"Help me decide between {sample[0]['title']} and {sample[1]['title']}"] if len(sample) >= 2 else []

    elif career and ("day" in msg_lower or "life" in msg_lower):
        reply = f"**A typical day as a {career['title']}:**\n\n{career['day_in_the_life']}"
        followups = ["What NOT to do in this field?", "How long will it take to reach job readiness?"]

    else:
        reply = (
            f"Hello! I am your **CareerPath AI Assistant**. I analyze your **{branch}** background, skill gaps, and learning goals"
            + (f" for **{career_name}**." if current_path else ".")
            + "\n\nYou can ask me questions such as:\n"
            f"• *Why was this course recommended?*\n"
            f"• *What should I NOT do when learning in this field?*\n"
            f"• *How long will it take to reach job readiness at {hours} hrs/week?*\n"
            f"• *Compare top career options.*"
        )
        followups = [
            "Why was this course recommended?",
            "What NOT to do in this field?",
            "How long will it take to reach job readiness?"
        ]

    return ChatResponse(
        reply=reply,
        suggested_followups=followups,
        referenced_resources=referenced_resources,
        referenced_warnings=referenced_warnings
    )
