from typing import List, Dict, Any, Optional
from app.data.taxonomy_data import CAREERS_DATABASE, ENGINEERING_BRANCHES
from app.models.schemas import CareerMatchScore, CareerDiscoveryResponse, CareerClarificationQuestion, CareerDetail, ProfileOnboardingRequest
from app.ml.engine import engine
EXPERIENCE_RANK = {'beginner': 0.3, 'intermediate': 0.6, 'advanced': 0.9}

def _token_overlap(a: str, b: str) -> float:
    ta, tb = (set(a.lower().split()), set(b.lower().split()))
    if not ta or not tb:
        return 0.0
    if a.lower() in b.lower() or b.lower() in a.lower():
        return 0.8
    return len(ta & tb) / len(ta | tb)

def _sim(a: str, b: str) -> float:
    try:
        return engine.text_sim(a, b)
    except Exception:
        return _token_overlap(a, b)

def _best(query: str, candidates) -> float:
    return max((_sim(query, c) for c in candidates or []), default=0.0)

def calculate_career_matches(profile: ProfileOnboardingRequest) -> CareerDiscoveryResponse:
    user_branch = profile.engineering_branch
    user_interests = [i.lower() for i in profile.interests]
    user_skills = [s.lower() for s in profile.known_skills]
    user_goal = profile.career_goal_status.lower()
    scored_careers: List[Dict[str, Any]] = []
    for career in CAREERS_DATABASE:
        is_primary = user_branch == career['branch_primary']
        is_compatible = any((b == user_branch for b in career['branches_compatible']))
        if is_primary:
            branch_score = 1.0
        elif is_compatible:
            branch_score = 0.85
        else:
            branch_score = 0.55
        career_text = f'{career['title']} {career['category']} {career['description']} {' '.join(career['key_responsibilities'])}'
        if user_interests:
            interest_score = sum((_sim(i, career_text) for i in user_interests)) / len(user_interests)
        else:
            interest_score = 0.5
        req_skills = career['required_skills']
        skill_matches = 0.0
        missing_critical = []
        transferable = []
        for req in req_skills:
            req_name = req['name']
            match_score = _best(req_name, profile.known_skills) if user_skills else 0.0
            if match_score >= 0.55:
                skill_matches += 1
                transferable.append(req['name'])
            elif req.get('critical', False):
                missing_critical.append(req['name'])
        skill_score = skill_matches / len(req_skills) if req_skills else 0.5
        avg_required_level = sum((r['level'] for r in req_skills)) / len(req_skills) if req_skills else 0.5
        user_exp_rank = EXPERIENCE_RANK.get(profile.experience_level.lower(), 0.5)
        goal_score = max(0.0, 1.0 - abs(user_exp_rank - avg_required_level))
        raw_score = branch_score * 0.3 + interest_score * 0.35 + skill_score * 0.25 + goal_score * 0.1
        match_pct = round(min(99.0, max(5.0, raw_score * 100)), 1)
        if is_primary:
            reason = f'Direct alignment with your {user_branch} background and interest in {(', '.join(user_interests[:2]) if user_interests else 'tech')}.'
        elif is_compatible:
            reason = f'Strong cross-disciplinary fit from {user_branch} into {career['category']}.'
        else:
            reason = f'Emerging cross-branch career path leverageable with targeted bridge skills.'
        scored_careers.append({'career': career, 'match_pct': match_pct, 'branch_score': round(branch_score * 100, 1), 'interest_score': round(interest_score * 100, 1), 'skill_score': round(skill_score * 100, 1), 'missing_critical': missing_critical, 'transferable': transferable, 'reason': reason})
    scored_careers.sort(key=lambda x: x['match_pct'], reverse=True)
    top_3_raw = scored_careers[:3]
    top_matches: List[CareerMatchScore] = []
    for idx, item in enumerate(top_3_raw):
        c = item['career']
        top_matches.append(CareerMatchScore(career_id=c['career_id'], title=c['title'], branch_primary=c['branch_primary'], match_percentage=item['match_pct'], match_reason=item['reason'], skill_alignment_score=item['skill_score'], interest_alignment_score=item['interest_score'], branch_compatibility_score=item['branch_score'], missing_critical_skills=item['missing_critical'], transferable_skills=item['transferable'], is_top_match=idx == 0))
    clarification_needed = False
    clarification_question = None
    if len(top_matches) >= 2:
        diff = top_matches[0].match_percentage - top_matches[1].match_percentage
        if diff <= 7.0:
            clarification_needed = True
            c1 = top_matches[0]
            c2 = top_matches[1]
            clarification_question = CareerClarificationQuestion(question_id='clarify_01', question_text=f"Your profile strongly aligns with both '{c1.title}' ({c1.match_percentage}%) and '{c2.title}' ({c2.match_percentage}%). Which type of challenge excites you more?", options=[{'label': f'Focus on {c1.title}: Practical hands-on hardware integration & real-time physical control.', 'impact_career': c1.career_id}, {'label': f'Focus on {c2.title}: Abstract algorithms, software architecture & model optimization.', 'impact_career': c2.career_id}])
    cross_advice = None
    if top_matches:
        target_career_obj = next((c for c in CAREERS_DATABASE if c['career_id'] == top_matches[0].career_id), None)
        if target_career_obj and top_matches[0].branch_primary != user_branch:
            bridge_skills = [s['name'] for s in target_career_obj['required_skills'] if s.get('critical')][:2]
            bridge_text = ' and '.join(bridge_skills) if bridge_skills else 'the core foundational skills for this field'
            cross_advice = f'Transitioning from {user_branch} to {top_matches[0].title} is feasible! We recommend starting with foundation bridge modules in {bridge_text} before advanced coursework.'
    return CareerDiscoveryResponse(top_matches=top_matches, clarification_needed=clarification_needed, clarification_question=clarification_question, cross_branch_advice=cross_advice)

def get_career_detail(career_id: str) -> Optional[CareerDetail]:
    for c in CAREERS_DATABASE:
        if c['career_id'] == career_id:
            return CareerDetail(career_id=c['career_id'], title=c['title'], category=c['category'], branch_primary=c['branch_primary'], description=c['description'], avg_salary_range=c['avg_salary_range'], job_demand=c['job_demand'], key_responsibilities=c['key_responsibilities'], required_skills=c['required_skills'], day_in_the_life=c['day_in_the_life'], hard_realities=c['hard_realities'], common_misconceptions=c['common_misconceptions'], future_evolution=c['future_evolution'], emerging_specializations=c['emerging_specializations'], what_not_to_do=c['what_not_to_do'])
    return None
