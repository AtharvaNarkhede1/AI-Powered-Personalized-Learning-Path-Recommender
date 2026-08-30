"""
Deterministic synthetic course-catalog generator.

Writes `backend/app/data/courses.csv` -- a PathWise-style engineering course
dataset that the ML engine (app/ml/) fits its TF-IDF+SVD semantic space and
prerequisite DAG on.

Run:  python -m scripts.generate_dataset
"""
from __future__ import annotations

import csv
import os
import random
import sys

# allow `python scripts/generate_dataset.py` as well as `-m scripts.generate_dataset`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.taxonomy_data import CAREERS_DATABASE, SKILLS_DATABASE  # noqa: E402

SEED = 42
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "app", "data", "courses.csv")

COLUMNS = [
    "course_id", "branch", "track", "course_title", "difficulty_level", "provider",
    "format", "description", "skills_taught", "tools_covered",
    "prerequisite_course_title", "estimated_hours", "rating", "num_reviews",
    "career_paths", "industry_sectors",
]

PROVIDERS = ["NPTEL", "Coursera", "edX", "Udacity", "Pluralsight", "MITx", "Udemy", "LinkedIn Learning"]
FORMATS = ["Video Course", "Interactive Lab", "Project-Based", "Instructor-led Live", "Self-paced Reading"]

TIERS = ["Beginner", "Intermediate", "Advanced", "Capstone"]
TIER_TITLE = {
    "Beginner": "{t}: Foundations",
    "Intermediate": "{t} in Practice",
    "Advanced": "{t}: Deep Dive",
    "Capstone": "{t} Capstone Project",
}
TIER_HOURS = {"Beginner": 12, "Intermediate": 22, "Advanced": 36, "Capstone": 46}

# skill category -> (engineering branch, tools, industry sectors)
CATEGORY_MAP = {
    "Software": ("Computer Engineering / IT", ["python", "git", "vs code"], ["software", "technology"]),
    "Web": ("Computer Engineering / IT", ["javascript", "react", "node.js", "docker"], ["software", "web", "startups"]),
    "Data": ("Computer Engineering / IT", ["python", "sql", "spark", "airflow"], ["analytics", "technology", "finance"]),
    "AI/ML": ("Computer Engineering / IT", ["python", "pytorch", "scikit-learn", "numpy"], ["artificial intelligence", "technology"]),
    "AI/Hardware": ("Electronics & Communication Engineering", ["python", "tensorrt", "c++"], ["edge ai", "robotics"]),
    "Mathematics": ("Computer Engineering / IT", ["numpy", "matlab"], ["research", "analytics"]),
    "Security": ("Computer Engineering / IT", ["linux", "wireshark", "python", "burp suite"], ["cybersecurity", "technology"]),
    "Systems": ("Computer Engineering / IT", ["linux", "bash", "docker"], ["cloud", "infrastructure"]),
    "DevOps": ("Computer Engineering / IT", ["docker", "kubernetes", "terraform", "aws"], ["cloud", "infrastructure"]),
    "Cloud": ("Computer Engineering / IT", ["aws", "terraform", "kubernetes"], ["cloud", "infrastructure"]),
    "Hardware": ("Electronics & Communication Engineering", ["c", "stm32", "oscilloscope", "keil"], ["embedded", "hardware"]),
    "Semiconductors": ("Electronics & Communication Engineering", ["verilog", "modelsim", "vivado"], ["semiconductors", "hardware"]),
    "Robotics": ("Robotics / Mechatronics", ["ros 2", "c++", "gazebo", "python"], ["robotics", "automation"]),
    "Robotics/EE": ("Robotics / Mechatronics", ["matlab", "simulink", "python"], ["robotics", "control systems"]),
    "IoT": ("Electronics & Communication Engineering", ["esp32", "mqtt", "c", "aws iot"], ["iot", "smart devices"]),
    "Quality": ("Computer Engineering / IT", ["playwright", "selenium", "pytest", "github actions"], ["software", "quality"]),
    "Energy": ("Electrical Engineering", ["etap", "matlab", "pvsyst"], ["energy", "utilities", "sustainability"]),
    "Automotive": ("Automobile Engineering", ["matlab", "simulink", "canalyzer"], ["automotive", "mobility"]),
    "Automotive/EE": ("Automobile Engineering", ["matlab", "simulink"], ["automotive", "mobility"]),
    "Mechanical": ("Mechanical Engineering", ["solidworks", "ansys", "fusion360"], ["manufacturing", "product design"]),
    "Civil": ("Civil Engineering", ["etabs", "staad pro", "revit", "autocad"], ["construction", "infrastructure"]),
    "Aerospace": ("Aerospace Engineering", ["matlab", "ansys fluent", "xflr5"], ["aerospace", "defense"]),
    "Chemical": ("Chemical Engineering", ["aspen plus", "dwsim", "matlab"], ["chemical", "process industry"]),
    "Biomedical": ("Biomedical Engineering", ["matlab", "labview", "python"], ["medical devices", "healthcare"]),
    "General": ("Computer Engineering / IT", ["python"], ["technology"]),
}

DESC_TMPL = (
    "{tier_adj} {track} for engineering learners. Covers {skills}. "
    "Hands-on work with {tools}. Prepares you for roles such as {careers}."
)
TIER_ADJ = {"Beginner": "A foundational introduction to", "Intermediate": "A practical, applied course on",
            "Advanced": "An in-depth advanced treatment of", "Capstone": "A portfolio capstone built around"}


def _careers_for_skill(skill_id: str) -> list[str]:
    out = []
    for c in CAREERS_DATABASE:
        if any(r["skill_id"] == skill_id for r in c["required_skills"]):
            out.append(c["title"])
    return out


def _skill_name(skill_id: str) -> str:
    return SKILLS_DATABASE.get(skill_id, {}).get("name", skill_id)


def generate_rows() -> list[dict]:
    rnd = random.Random(SEED)
    rows: list[dict] = []
    seen_ids: set[str] = set()

    # index: skill_id -> its Beginner-tier course title, used for cross-track
    # prerequisite edges ("Intro to ML" requires "Intro to Python", NOT advanced Python)
    beg_title_of: dict[str, str] = {}
    for sid, s in SKILLS_DATABASE.items():
        beg_title_of[sid] = TIER_TITLE["Beginner"].format(t=s.get("name", sid))

    def emit_track(track: str, branch: str, cat: str, skills_cum: dict, career_paths: list[str],
                   cross_prereq_title: str | None, id_prefix: str):
        tools = CATEGORY_MAP.get(cat, CATEGORY_MAP["General"])[1]
        sectors = CATEGORY_MAP.get(cat, CATEGORY_MAP["General"])[2]
        prev_title = ""
        for ti, tier in enumerate(TIERS):
            title = TIER_TITLE[tier].format(t=track)
            if tier == "Beginner":
                prereq = cross_prereq_title or ""
            else:
                prereq = prev_title
            n_providers = rnd.randint(3, 6)
            for prov in rnd.sample(PROVIDERS, n_providers):
                cid = f"{id_prefix}-{ti}-{abs(hash(prov)) % 1000:03d}"
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)
                hours = max(6, int(rnd.gauss(TIER_HOURS[tier], 6)))
                skills_taught = "; ".join(skills_cum[tier])
                rows.append({
                    "course_id": cid,
                    "branch": branch,
                    "track": track,
                    "course_title": title,
                    "difficulty_level": tier,
                    "provider": prov,
                    "format": rnd.choice(FORMATS),
                    "description": DESC_TMPL.format(
                        tier_adj=TIER_ADJ[tier], track=track,
                        skills=", ".join(skills_cum[tier][:4]),
                        tools=", ".join(tools[:3]),
                        careers=", ".join(career_paths[:3]) if career_paths else "engineering practice"),
                    "skills_taught": skills_taught,
                    "tools_covered": "; ".join(tools),
                    "prerequisite_course_title": prereq,
                    "estimated_hours": hours,
                    "rating": round(min(4.9, max(3.5, rnd.gauss(4.3, 0.32))), 1),
                    "num_reviews": rnd.randint(120, 6000),
                    "career_paths": "; ".join(career_paths),
                    "industry_sectors": "; ".join(sectors),
                })
            prev_title = title

    # 1) one 4-tier track per skill in the taxonomy
    for idx, (sid, s) in enumerate(sorted(SKILLS_DATABASE.items())):
        cat = s.get("category", "General")
        branch = CATEGORY_MAP.get(cat, CATEGORY_MAP["General"])[0]
        name = s.get("name", sid)
        prereq_names = [_skill_name(p) for p in s.get("prerequisites", [])]
        base = [name] + prereq_names
        skills_cum = {
            "Beginner": prereq_names[:1] + [name] if prereq_names else [name],
            "Intermediate": base,
            "Advanced": base + [f"{name} optimization"],
            "Capstone": base + [f"{name} system design", f"{name} portfolio project"],
        }
        # dedupe preserve order
        for k in skills_cum:
            skills_cum[k] = list(dict.fromkeys([x for x in skills_cum[k] if x]))
        cross = None
        prereqs = s.get("prerequisites", [])
        if prereqs:
            cross = beg_title_of.get(prereqs[0])
        emit_track(name, branch, cat, skills_cum, _careers_for_skill(sid), cross, f"SK{idx:03d}")

    # 2) per-career applied specialization tracks
    for cidx, c in enumerate(CAREERS_DATABASE):
        branch = c["branch_primary"]
        crit = [r for r in c["required_skills"] if r.get("critical")] or c["required_skills"]
        specs = [
            (f"{c['title']} Foundations", [r["name"] for r in crit[:3]]),
            (f"{c['title']} Systems Practicum", [r["name"] for r in c["required_skills"][:4]]),
            (f"{c['title']} Industry Capstone", [r["name"] for r in c["required_skills"]]),
        ]
        # infer a category for tools from the first required skill
        first_cat = SKILLS_DATABASE.get(c["required_skills"][0]["skill_id"], {}).get("category", "General")
        for si, (track, sk) in enumerate(specs):
            sk = list(dict.fromkeys(sk)) or [c["title"]]
            skills_cum = {
                "Beginner": sk[:2],
                "Intermediate": sk,
                "Advanced": sk + ["system integration"],
                "Capstone": sk + ["end-to-end portfolio project", "job-readiness review"],
            }
            emit_track(track, branch, first_cat, skills_cum, [c["title"]], None, f"CR{cidx:02d}{si}")

    return rows


def main():
    rows = generate_rows()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    branches = sorted({r["branch"] for r in rows})
    print(f"wrote {len(rows)} courses -> {OUT_PATH}")
    print(f"tracks: {len({r['track'] for r in rows})} | branches: {len(branches)}")
    print(f"careers referenced: {len({p for r in rows for p in r['career_paths'].split('; ') if p})}")


if __name__ == "__main__":
    main()
