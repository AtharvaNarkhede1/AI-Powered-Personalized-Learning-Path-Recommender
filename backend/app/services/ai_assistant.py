import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.data.taxonomy_data import CAREERS_DATABASE
from app.models.schemas import ChatResponse, LearningPathResponse, ProfileOnboardingRequest, ResourceItem
logger = logging.getLogger(__name__)
_FACTOR_PHRASE = {'goal_fit': 'how closely a course matches your stated goal', 'skill_gain': 'how much of your skill gap a course closes', 'level_fit': 'matching your current level', 'quality': 'course rating and review volume', 'prereq_ready': "whether you're ready for the prerequisites", 'effort_fit': 'fitting your weekly time budget', 'format_pref': 'your preferred learning format'}

@dataclass
class Grounding:
    profile: Optional[ProfileOnboardingRequest]
    path: Optional[LearningPathResponse]
    career: Optional[Dict[str, Any]]
    gaps: List[Any] = field(default_factory=list)
    readiness_pct: Optional[float] = None
    top_factors: List[tuple] = field(default_factory=list)
    personalised: bool = False

    @property
    def career_title(self) -> str:
        if self.career:
            return self.career['title']
        if self.path:
            return self.path.career_title
        return 'your target career'

    @property
    def hours(self) -> int:
        return int(self.profile.hours_per_week) if self.profile and self.profile.hours_per_week else 10

    def ordered_courses(self, limit: int=6) -> List[ResourceItem]:
        if not self.path:
            return []
        out: List[ResourceItem] = []
        for m in self.path.milestones:
            out.extend(m.resources)
        return out[:limit]

    def next_course(self) -> Optional[tuple]:
        if not self.path:
            return None
        for m in self.path.milestones:
            if m.status != 'completed' and m.resources:
                return (m, m.resources[0])
        for m in self.path.milestones:
            if m.resources:
                return (m, m.resources[0])
        return None

def _career_for(career_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not career_id:
        return None
    return next((c for c in CAREERS_DATABASE if c['career_id'] == career_id), None)

def _collect_grounding(profile: Optional[ProfileOnboardingRequest], current_path: Optional[LearningPathResponse], context_career_id: Optional[str], db=None, profile_id: Optional[str]=None) -> Grounding:
    career_id = (current_path.career_id if current_path else None) or context_career_id
    if not career_id and profile is not None:
        career_id = getattr(profile, 'target_career_id', None)
    career = _career_for(career_id)
    g = Grounding(profile=profile, path=current_path, career=career)
    if current_path:
        g.readiness_pct = current_path.job_readiness_score
    if career_id and profile is not None:
        try:
            from app.services.skill_gap_engine import analyze_skill_gaps
            analysis = analyze_skill_gaps(career_id, profile, db=db, profile_id=profile_id)
            g.gaps = sorted(analysis.gaps, key=lambda x: x.gap_delta, reverse=True)
            if g.readiness_pct is None:
                g.readiness_pct = analysis.overall_readiness_pct
        except Exception as e:
            logger.debug('skill gap grounding unavailable: %s', e)
    if db is not None and profile_id:
        try:
            from app.ml.engine import engine
            snap = engine.model_snapshot(db, profile_id)
            g.personalised = bool(snap.get('personalised'))
            weights = sorted(snap.get('weights', []), key=lambda w: w['weight'], reverse=True)
            g.top_factors = [(w['factor'], w['weight']) for w in weights[:3]]
        except Exception as e:
            logger.debug('model grounding unavailable: %s', e)
    return g

def _grounding_text(g: Grounding) -> str:
    L: List[str] = []
    if g.profile:
        L.append(f'Learner: {g.profile.engineering_branch} background, {g.profile.experience_level} level, {g.hours} hrs/week available. Known skills: {', '.join(g.profile.known_skills) or 'none reported'}.')
    if g.career:
        L.append(f'Target career: {g.career['title']} — {g.career['description']}')
        L.append(f'A typical day: {g.career['day_in_the_life']}')
        if g.career.get('hard_realities'):
            L.append('Hard realities: ' + ' '.join(g.career['hard_realities'][:2]))
        if g.career.get('what_not_to_do'):
            L.append('What NOT to do: ' + ' | '.join(g.career['what_not_to_do'][:3]))
    if g.readiness_pct is not None and g.path:
        L.append(f'Current job-readiness: {g.readiness_pct}%. Estimated {g.path.estimated_weeks} weeks ({round(g.path.estimated_weeks / 4.2, 1)} months) at {g.path.hours_per_week} hrs/week.')
    if g.path:
        L.append(f'Path tracks: {', '.join(g.path.track_names) or 'n/a'}.')
        for m in g.path.milestones:
            titles = '; '.join((f'{r.title}' for r in m.resources[:4]))
            L.append(f'  {m.title} [{m.status}] — courses: {titles}')
        first = g.ordered_courses(3)
        for r in first:
            if r.why_now:
                L.append(f"  Rationale for '{r.title}': {r.why_now}")
    if g.gaps:
        gap_lines = [f'{gp.skill_name}: {round(gp.current_level * 100)}% now vs {round(gp.required_level * 100)}% needed ({gp.status})' for gp in g.gaps[:6]]
        L.append('Skill gaps (largest first): ' + '; '.join(gap_lines))
    if g.top_factors:
        fac = ', '.join((f'{f} ({_FACTOR_PHRASE.get(f, f)})' for f, _ in g.top_factors))
        L.append(f"This learner's recommendations are currently weighted most toward: {fac}.")
    return '\n'.join(L) if L else 'No learner context available yet.'
_SYSTEM_RULES = "You are CareerPath AI, an engineering career & learning-path advisor. Answer ONLY from the learner context below. Do NOT invent course names, numbers, timelines, or facts that are not in the context. If the context doesn't contain the answer, say so and suggest what the learner should do in the app to get it. Be concise, specific, and encouraging. Use short bullet points and cite the learner's real course titles / gap numbers."

def _try_llm(message: str, context: str) -> Optional[str]:
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=_SYSTEM_RULES)
            resp = model.generate_content(f'LEARNER CONTEXT:\n{context}\n\nQUESTION: {message}')
            if resp and getattr(resp, 'text', None):
                return resp.text.strip()
        except Exception as e:
            logger.warning('Gemini failed, using grounded offline engine: %s', e)
    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            res = client.chat.completions.create(model='gpt-4o-mini', messages=[{'role': 'system', 'content': f'{_SYSTEM_RULES}\n\nLEARNER CONTEXT:\n{context}'}, {'role': 'user', 'content': message}], temperature=0.4)
            if res.choices and res.choices[0].message.content:
                return res.choices[0].message.content.strip()
        except Exception as e:
            logger.warning('OpenAI failed, using grounded offline engine: %s', e)
    return None

def _classify(msg: str) -> str:
    m = msg.lower()
    if any((k in m for k in ('why', 'reason', 'explain'))) and any((k in m for k in ('path', 'course', 'recommend', 'order', 'roadmap'))):
        return 'why_path'
    if any((k in m for k in ('next', 'start with', 'first course', 'what should i do', 'where do i begin', 'what now'))):
        return 'next_step'
    if any((k in m for k in ('how long', 'timeline', 'weeks', 'months', 'ready', 'readiness', 'faster', 'accelerate'))):
        return 'timeline'
    if any((k in m for k in ('weak', 'gap', 'behind', 'missing', 'improve', 'worst'))):
        return 'weak_areas'
    if any((k in m for k in ('avoid', 'not to do', 'mistake', "don't", 'dont', 'trap', 'pitfall'))):
        return 'avoid'
    if any((k in m for k in ('day', 'life', 'typical', 'what do', 'role look'))):
        return 'day'
    if any((k in m for k in ('project', 'build', 'portfolio', 'capstone'))):
        return 'projects'
    if any((k in m for k in ('compare', 'difference', 'vs ', 'versus', 'instead'))):
        return 'compare'
    return 'default'

def _bullets(items: List[str]) -> str:
    return '\n'.join((f'• {i}' for i in items if i))

def _offline_answer(message: str, g: Grounding) -> ChatResponse:
    intent = _classify(message)
    refs: List[ResourceItem] = []
    ref_warnings: List[str] = []
    followups: List[str] = []
    ct = g.career_title
    if intent == 'why_path':
        if not g.path:
            reply = "You don't have a learning path yet. Pick a career in **Career Discovery** and I'll explain exactly why each course is ordered the way it is."
            followups = ['How do I pick a career?', 'What careers match my profile?']
        else:
            first = g.ordered_courses(3)
            refs = first
            lines = [f'Your path for **{ct}** is built from {len(g.path.track_names)} track(s): {', '.join(g.path.track_names)}.', '']
            lines.append('The first steps and *why they come first*:')
            for r in first:
                lines.append(f'• **{r.title}** — {r.why_now or 'foundational for what follows.'}')
            if g.top_factors:
                fac = ', '.join((f'{_FACTOR_PHRASE.get(f, f)}' for f, _ in g.top_factors))
                lines += ['', f'Right now your picks are weighted most toward: {fac}. Thumbs-up / thumbs-down on courses shifts this.']
            reply = '\n'.join(lines)
            followups = ['What should I start with today?', f'What are my weak areas for {ct}?', "How long until I'm job ready?"]
    elif intent == 'next_step':
        nxt = g.next_course()
        if not nxt:
            reply = "Generate a learning path first (Career Discovery → pick a career) and I'll point you to the exact next course."
            followups = ['What careers match me?']
        else:
            m, r = nxt
            refs = [r]
            reply = f'Your next step is **{r.title}** ({r.provider}, ~{r.duration_hours:g} hrs, {r.difficulty}).\n\n• Why now: {r.why_now or 'it unlocks the rest of ' + m.title}.\n• It sits in **{m.title}**' + (f', which targets: {', '.join(m.target_skills[:4])}.' if m.target_skills else '.')
            if getattr(r, 'unlocks', None):
                reply += f'\n• Finishing it prepares you for: {', '.join(r.unlocks[:2])}.'
            followups = ['Why is this course first?', 'What project should I build in this milestone?', 'How long will this milestone take?']
    elif intent == 'timeline':
        if not g.path:
            reply = 'I need a generated path to estimate your timeline. Pick a career in Career Discovery first.'
            followups = ['What careers match me?']
        else:
            weeks = g.path.estimated_weeks
            months = round(weeks / 4.2, 1)
            done = sum((1 for m in g.path.milestones if m.status == 'completed'))
            reply = f"At **{g.path.hours_per_week} hrs/week** you're about **{weeks} weeks (~{months} months)** from job-readiness for **{ct}**.\n\n• Current readiness: **{g.readiness_pct}%**\n• Milestones done: {done}/{len(g.path.milestones)}\n• Biggest lever to go faster: raise weekly hours, and clear the top gap below."
            if g.gaps:
                reply += f'\n• Largest remaining gap: **{g.gaps[0].skill_name}** ({g.gaps[0].status}).'
            followups = ['What are my weak areas?', 'What should I start with today?', 'How can I accelerate my path?']
    elif intent == 'weak_areas':
        if not g.gaps:
            reply = "I don't have a skill-gap analysis for you yet — pick a target career and I'll compare your known skills against what the role needs."
            followups = ['What careers match me?']
        else:
            top = g.gaps[:3]
            reply = f'Your biggest gaps for **{ct}** right now:\n\n' + _bullets([f'**{gp.skill_name}** — {round(gp.current_level * 100)}% vs {round(gp.required_level * 100)}% needed ({gp.status})' for gp in top])
            match_courses = [r for r in g.ordered_courses(12) if any((gp.skill_name.split('(')[0].strip().lower() in (r.title + ' ' + ' '.join(r.skills_covered)).lower() for gp in top))]
            if match_courses:
                refs = match_courses[:3]
                reply += '\n\nCourses in your path that close these: ' + ', '.join((f'*{r.title}*' for r in refs))
            followups = ['What should I start with today?', "How long until I'm job ready?"]
    elif intent == 'avoid':
        warns = (g.career or {}).get('what_not_to_do', [])
        if not warns and g.path:
            warns = g.path.what_not_to_do_warnings
        if not warns:
            warns = ["Don't collect course completions without shipping end-to-end projects.", "Don't skip prerequisites to rush into advanced material."]
        ref_warnings = warns[:4]
        reply = f'**What NOT to do while training for {ct}:**\n\n' + _bullets(ref_warnings)
        followups = ['What are my weak areas?', 'What project should I build?', "What's a typical day in this role?"]
    elif intent == 'day':
        if g.career:
            reply = f'**A typical day as a {ct}:**\n\n{g.career['day_in_the_life']}'
            if g.career.get('key_responsibilities'):
                reply += '\n\nCore responsibilities:\n' + _bullets(g.career['key_responsibilities'][:4])
        else:
            reply = "Pick a target career and I'll describe a real day in that role."
        followups = ['What NOT to do in this field?', 'What are my weak areas?']
    elif intent == 'projects':
        projs = []
        if g.path:
            projs = [m.project for m in g.path.milestones if m.project]
        if projs:
            reply = f'**Portfolio projects in your {ct} path:**\n\n' + _bullets([f'**{p['title']}** — {p['description']} (deliverable: {p['required_deliverable']})' for p in projs[:4]])
        else:
            reply = 'Generate a path and each milestone will come with a concrete portfolio project to build.'
        followups = ['What should I start with today?', 'How long will the path take?']
    elif intent == 'compare':
        others = [c for c in CAREERS_DATABASE if not g.career or c['career_id'] != g.career['career_id']][:2]
        picks = ([g.career] if g.career else []) + others
        picks = [c for c in picks if c][:3]
        reply = '**Comparing on real role data:**\n\n' + '\n\n'.join((f'**{c['title']}** ({c['job_demand']} demand, {c['avg_salary_range']})\n{c['description']}\nWatch out: {c['what_not_to_do'][0]}' for c in picks))
        followups = [f'Why was {ct} recommended for me?', 'What are my weak areas?']
    else:
        parts = [f"I'm your **CareerPath AI** assistant, working from your real profile" + (f' and **{ct}** path.' if g.path else '.')]
        if g.gaps:
            parts.append(f'Your top gap right now is **{g.gaps[0].skill_name}** ({g.gaps[0].status}).')
        if g.path:
            nxt = g.next_course()
            if nxt:
                parts.append(f'Your next course is **{nxt[1].title}**.')
        parts.append('\nTry asking:\n' + _bullets(['Why is my path ordered this way?', 'What should I start with today?', f"How long until I'm job ready at {g.hours} hrs/week?", 'What are my weakest skills?']))
        reply = '\n'.join(parts)
        followups = ['Why is my path ordered this way?', 'What should I start with today?', 'What are my weak areas?']
    if not followups:
        followups = ['Why is my path ordered this way?', 'What are my weak areas?', "How long until I'm job ready?"]
    return ChatResponse(reply=reply, suggested_followups=followups[:4], referenced_resources=refs, referenced_warnings=ref_warnings)

def generate_ai_reply(message: str, profile: Optional[ProfileOnboardingRequest]=None, current_path: Optional[LearningPathResponse]=None, context_career_id: Optional[str]=None, db=None, profile_id: Optional[str]=None) -> ChatResponse:
    g = _collect_grounding(profile, current_path, context_career_id, db=db, profile_id=profile_id)
    llm_text = _try_llm(message, _grounding_text(g))
    if llm_text:
        base = _offline_answer(message, g)
        return ChatResponse(reply=llm_text, suggested_followups=base.suggested_followups, referenced_resources=base.referenced_resources, referenced_warnings=base.referenced_warnings)
    return _offline_answer(message, g)
