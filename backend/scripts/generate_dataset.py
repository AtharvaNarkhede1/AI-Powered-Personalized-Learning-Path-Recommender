from __future__ import annotations
import csv
import os
import random
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.data.taxonomy_data import (  
    CAREERS_DATABASE, SKILLS_DATABASE, ENGINEERING_BRANCHES as ENG_BRANCHES,
)
SEED = 42
OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "app", "data", "courses.csv")
TARGET_ROWS = 18000
COLUMNS = [
    "course_id", "branch", "track", "course_title", "difficulty_level", "provider",
    "format", "description", "skills_taught", "tools_covered",
    "prerequisite_course_title", "estimated_hours", "rating", "num_reviews",
    "career_paths", "industry_sectors",
]
PROVIDERS = ["NPTEL", "Coursera", "edX", "Udacity", "Pluralsight", "MITx", "Udemy",
             "LinkedIn Learning", "DataCamp", "Great Learning"]
FREE_PROVIDERS = {"NPTEL", "MITx", "edX"}
TIERS = ["Beginner", "Intermediate", "Advanced", "Capstone"]
TIER_LABEL = {"Beginner": "Foundations", "Intermediate": "Applied",
              "Advanced": "Advanced", "Capstone": "Capstone"}
TIER_HOURS = {"Beginner": 14, "Intermediate": 24, "Advanced": 38, "Capstone": 50}
TIER_ADJ = {"Beginner": "a foundational introduction to",
            "Intermediate": "a practical, applied treatment of",
            "Advanced": "an in-depth advanced study of",
            "Capstone": "a portfolio capstone built around"}
ANGLES = [
    {"name": "", "fmt": "Video Course", "hmul": 1.0, "extra": [],
     "blurb": "structured lectures with graded assignments and readings"},
    {"name": "Hands-On Lab", "fmt": "Interactive Lab", "hmul": 1.15, "extra": ["lab exercises", "debugging practice"],
     "blurb": "a lab-first course: you build and break things every module, guided walkthroughs, no long lectures"},
    {"name": "Project Track", "fmt": "Project-Based", "hmul": 1.3, "extra": ["portfolio project", "real-world scenario"],
     "blurb": "one large end-to-end project delivered in stages, code review, a shippable portfolio outcome"},
    {"name": "Deep Theory", "fmt": "Self-paced Reading", "hmul": 1.1, "extra": ["first principles", "derivations", "research context"],
     "blurb": "a rigorous first-principles course with proofs, derivations and links to current research"},
    {"name": "Crash Course", "fmt": "Video Course", "hmul": 0.55, "extra": ["essentials only", "weekend intensive"],
     "blurb": "a condensed, fast-paced overview of only the essentials, doable in a weekend"},
    {"name": "Interview & Exam Prep", "fmt": "Interactive Lab", "hmul": 0.8, "extra": ["interview preparation", "certification objectives", "timed practice"],
     "blurb": "problem sets, mock interviews and certification objectives with timed practice tests"},
    {"name": "Industry Practicum", "fmt": "Instructor-led Live", "hmul": 1.2, "extra": ["industry case studies", "production workflows", "tooling"],
     "blurb": "industry case studies and production workflows taught by practitioners, live cohort"},
]
DESC_TEMPLATES = [
    "This course is {adj} {track} for {branch} learners -- {blurb}. You practise {skills} using {tools}. Typical next roles: {careers}.",
    "{track} taught as {blurb}. Aimed at {branch} students and career changers. Core skills: {skills}. Tools: {tools}. Prepares you for work as {careers}.",
    "A {branch}-focused path through {track}. {Blurb_cap}. Covers {skills}; hands-on with {tools}. Graduates move into roles like {careers}.",
    "Learn {track} the applied way -- {blurb}. Skills built: {skills}. Toolchain: {tools}. Relevant careers: {careers}.",
]
CATEGORY_TOOLS = {
    "Software": (["python", "git", "vs code", "pytest"], ["software", "technology"]),
    "Web": (["javascript", "typescript", "react", "node.js", "docker", "postgres"], ["software", "web", "startups"]),
    "Data": (["python", "sql", "spark", "airflow", "dbt", "pandas"], ["analytics", "technology", "finance"]),
    "AI/ML": (["python", "pytorch", "scikit-learn", "numpy", "hugging face"], ["artificial intelligence", "technology"]),
    "AI/Hardware": (["python", "tensorrt", "c++", "onnx", "jetson"], ["edge ai", "robotics"]),
    "Mathematics": (["numpy", "matlab", "sympy"], ["research", "analytics"]),
    "Security": (["linux", "wireshark", "python", "burp suite", "nmap", "metasploit"], ["cybersecurity", "technology"]),
    "Systems": (["linux", "bash", "docker", "systemd"], ["cloud", "infrastructure"]),
    "DevOps": (["docker", "kubernetes", "terraform", "aws", "prometheus", "github actions"], ["cloud", "infrastructure"]),
    "Cloud": (["aws", "terraform", "kubernetes", "cloudformation"], ["cloud", "infrastructure"]),
    "Hardware": (["c", "stm32", "oscilloscope", "keil", "logic analyzer"], ["embedded", "hardware"]),
    "Semiconductors": (["verilog", "systemverilog", "modelsim", "vivado", "cadence"], ["semiconductors", "hardware"]),
    "Robotics": (["ros 2", "c++", "gazebo", "python", "moveit"], ["robotics", "automation"]),
    "Robotics/EE": (["matlab", "simulink", "python", "control toolbox"], ["robotics", "control systems"]),
    "IoT": (["esp32", "mqtt", "c", "aws iot", "zephyr"], ["iot", "smart devices"]),
    "Quality": (["playwright", "selenium", "pytest", "github actions", "k6"], ["software", "quality"]),
    "Energy": (["etap", "matlab", "pvsyst", "homer pro", "digsilent"], ["energy", "utilities", "sustainability"]),
    "Automotive": (["matlab", "simulink", "canalyzer", "dspace"], ["automotive", "mobility"]),
    "Automotive/EE": (["matlab", "simulink", "canoe"], ["automotive", "mobility"]),
    "Mechanical": (["solidworks", "ansys", "fusion360", "creo"], ["manufacturing", "product design"]),
    "Civil": (["etabs", "staad pro", "revit", "autocad", "sap2000"], ["construction", "infrastructure"]),
    "Aerospace": (["matlab", "ansys fluent", "xflr5", "openvsp"], ["aerospace", "defense"]),
    "Chemical": (["aspen plus", "dwsim", "matlab", "hysys"], ["chemical", "process industry"]),
    "Biomedical": (["matlab", "labview", "python", "comsol"], ["medical devices", "healthcare"]),
    "General": (["python", "excel"], ["technology"]),
}
CATEGORY_HOME_BRANCH = {
    "Software": "Computer Engineering / IT", "Web": "Computer Engineering / IT",
    "Data": "Computer Engineering / IT", "AI/ML": "Computer Engineering / IT",
    "AI/Hardware": "Electronics & Communication Engineering", "Mathematics": "Computer Engineering / IT",
    "Security": "Computer Engineering / IT", "Systems": "Computer Engineering / IT",
    "DevOps": "Computer Engineering / IT", "Cloud": "Computer Engineering / IT",
    "Hardware": "Electronics & Communication Engineering", "Semiconductors": "Electronics & Communication Engineering",
    "Robotics": "Robotics / Mechatronics", "Robotics/EE": "Robotics / Mechatronics",
    "IoT": "Electronics & Communication Engineering", "Quality": "Computer Engineering / IT",
    "Energy": "Electrical Engineering", "Automotive": "Automobile Engineering",
    "Automotive/EE": "Automobile Engineering", "Mechanical": "Mechanical Engineering",
    "Civil": "Civil Engineering", "Aerospace": "Aerospace Engineering",
    "Chemical": "Chemical Engineering", "Biomedical": "Biomedical Engineering",
    "General": "Computer Engineering / IT",
}
def _skill_name(sid: str) -> str:
    return SKILLS_DATABASE.get(sid, {}).get("name", sid)
def _careers_for_skill(sid: str) -> list[str]:
    return [c["title"] for c in CAREERS_DATABASE
            if any(r["skill_id"] == sid for r in c["required_skills"])]
def _branches_for_skill(sid: str) -> list[str]:
    """Ordered by importance: skill's home branch + primary branches of careers
    that require it first, then compatible branches. Capped so the dataset stays
    bounded but every skill still spans several branches."""
    s = SKILLS_DATABASE.get(sid, {})
    primary: list[str] = [CATEGORY_HOME_BRANCH.get(s.get("category", "General"), "Computer Engineering / IT")]
    secondary: list[str] = []
    for c in CAREERS_DATABASE:
        if any(r["skill_id"] == sid for r in c["required_skills"]):
            primary.append(c["branch_primary"])
            secondary.extend(b for b in c.get("branches_compatible", []) if b in ENG_BRANCHES)
    ordered: list[str] = []
    for b in primary + secondary:
        if b not in ordered:
            ordered.append(b)
    return ordered[:5]
def _canonical_title(skill: str, tier: str) -> str:
    return f"{skill}: {TIER_LABEL[tier]}"
def _course_title(skill: str, tier: str, angle: str) -> str:
    base = _canonical_title(skill, tier)
    return base if not angle else f"{base} — {angle}"
def generate_rows() -> list[dict]:
    rnd = random.Random(SEED)
    rows: list[dict] = []
    seen_ids: set[str] = set()
    counter = 0
    def new_id() -> str:
        nonlocal counter
        counter += 1
        return f"C{counter:06d}"
    def emit_track(track: str, branch: str, cat: str, career_paths: list[str],
                   skill_by_tier: dict, cross_prereq_title: str | None,
                   variants_per_rung: int):
        tools, sectors = CATEGORY_TOOLS.get(cat, CATEGORY_TOOLS["General"])
        prev_canonical = ""
        for tier in TIERS:
            canonical = _canonical_title(track, tier)
            prereq_for_tier = (cross_prereq_title or "") if tier == "Beginner" else prev_canonical
            combos = [(a, p) for a in ANGLES for p in PROVIDERS]
            rnd.shuffle(combos)
            std_prov = rnd.choice(PROVIDERS)
            picks = [(ANGLES[0], std_prov)]
            for a, p in combos:
                if len(picks) >= max(1, variants_per_rung):
                    break
                if (a["name"], p) == (ANGLES[0]["name"], std_prov):
                    continue
                picks.append((a, p))
            for angle, prov in picks:
                cid = new_id()
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)
                base_h = TIER_HOURS[tier] * angle["hmul"]
                hours = max(4, int(rnd.gauss(base_h, base_h * 0.15)))
                sk = list(dict.fromkeys(skill_by_tier[tier] + angle["extra"]))
                tset = list(dict.fromkeys(tools + rnd.sample(tools, 1)))
                tmpl = rnd.choice(DESC_TEMPLATES)
                blurb = angle["blurb"]
                desc = tmpl.format(
                    adj=TIER_ADJ[tier], track=track, branch=branch, blurb=blurb,
                    Blurb_cap=blurb[0].upper() + blurb[1:],
                    skills=", ".join(sk[:5]), tools=", ".join(tset[:4]),
                    careers=", ".join(career_paths[:3]) if career_paths else "engineering practice",
                )
                rows.append({
                    "course_id": cid, "branch": branch, "track": track,
                    "course_title": _course_title(track, tier, angle["name"]),
                    "difficulty_level": tier, "provider": prov, "format": angle["fmt"],
                    "description": desc,
                    "skills_taught": "; ".join(sk),
                    "tools_covered": "; ".join(tset),
                    "prerequisite_course_title": prereq_for_tier,
                    "estimated_hours": hours,
                    "rating": round(min(4.9, max(3.4, rnd.gauss(4.35, 0.33))), 1),
                    "num_reviews": int(abs(rnd.gauss(1500, 1400))) + 40,
                    "career_paths": "; ".join(career_paths),
                    "industry_sectors": "; ".join(sectors),
                })
            prev_canonical = canonical
    skill_ids = sorted(SKILLS_DATABASE.keys())
    n_skill_branch = sum(len(_branches_for_skill(s)) for s in skill_ids)
    n_career_specs = len(CAREERS_DATABASE)
    vpr = max(4, round(TARGET_ROWS / (4 * (n_skill_branch + n_career_specs))))
    vpr = min(vpr, len(ANGLES) * len(PROVIDERS))
    for sid in skill_ids:
        s = SKILLS_DATABASE[sid]
        name = s.get("name", sid)
        cat = s.get("category", "General")
        prereq_names = [_skill_name(p) for p in s.get("prerequisites", [])]
        cross = None
        if s.get("prerequisites"):
            cross = _canonical_title(_skill_name(s["prerequisites"][0]), "Beginner")
        base = [name] + prereq_names
        skill_by_tier = {
            "Beginner": list(dict.fromkeys(prereq_names[:1] + [name])),
            "Intermediate": list(dict.fromkeys(base)),
            "Advanced": list(dict.fromkeys(base + [f"{name} optimisation", "performance tuning"])),
            "Capstone": list(dict.fromkeys(base + [f"{name} system design", "end-to-end project"])),
        }
        for branch in _branches_for_skill(sid):
            emit_track(name, branch, cat, _careers_for_skill(sid), skill_by_tier, cross, vpr)
    for c in CAREERS_DATABASE:
        branch = c["branch_primary"]
        first_cat = SKILLS_DATABASE.get(c["required_skills"][0]["skill_id"], {}).get("category", "General")
        sk = list(dict.fromkeys(r["name"] for r in c["required_skills"]))
        track = f"{c['title']} Portfolio"
        skill_by_tier = {
            "Beginner": sk[:2] + ["engineering project workflow"],
            "Intermediate": sk[:4],
            "Advanced": sk + ["system integration"],
            "Capstone": sk + ["end-to-end portfolio project", "job-readiness review", "technical interview prep"],
        }
        emit_track(track, branch, first_cat, [c["title"]], skill_by_tier, None, vpr)
    return rows
def main():
    rows = generate_rows()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    branches = sorted({r["branch"] for r in rows})
    tracks = {r["track"] for r in rows}
    careers = {p for r in rows for p in r["career_paths"].split("; ") if p}
    print(f"wrote {len(rows)} courses -> {OUT_PATH}")
    print(f"tracks: {len(tracks)} | branches: {len(branches)} | careers referenced: {len(careers)}")
    print("branches:", ", ".join(branches))
if __name__ == "__main__":
    main()