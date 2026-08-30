from __future__ import annotations
from typing import Dict
from app.ml.ranker import FACTOR_LABEL, ScoredCourse
MENTION_FLOOR = 0.08
CAVEAT_FLOOR = 0.35
CAVEATS = {
    "prereq_ready": "some prerequisites aren't complete yet",
    "quality": "it has a thinner rating history than other options",
    "level_fit": "it's a step away from your current level",
    "effort_fit": "it's longer than your usual time budget",
}
def explain(sc: ScoredCourse, row) -> Dict:
    drivers = sorted(
        [(FACTOR_LABEL[f], share) for f, share in sc.contributions.items() if share >= MENTION_FLOOR],
        key=lambda x: -x[1],
    )[:3]
    if drivers:
        lead = " and ".join(d[0] for d in drivers[:2])
        headline = f"Recommended because it {lead}."
    else:
        headline = "Recommended as a solid overall match for your goal."
    caveats = [text for f, text in CAVEATS.items() if sc.factors.get(f, 1.0) < CAVEAT_FLOOR]
    return {
        "headline": headline,
        "drivers": [{"factor": name, "share": round(share, 3)} for name, share in drivers],
        "caveats": caveats,
    }