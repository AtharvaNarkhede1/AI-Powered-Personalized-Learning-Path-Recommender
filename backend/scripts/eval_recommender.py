import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.ml.engine import engine  # noqa: E402
from app.models.schemas import ProfileOnboardingRequest  # noqa: E402
PASS, FAIL = "PASS", "FAIL"
results = []
def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"  [{PASS if ok else FAIL}] {name}" + (f" -- {detail}" if detail else ""))
t0 = time.time()
engine.warm()
warm_s = time.time() - t0
check("engine warms", engine._ready and engine.catalog is not None, f"{len(engine.catalog)} courses in {warm_s:.2f}s")
check("first-time fit under 120s", warm_s < 120.0, f"{warm_s:.2f}s (cached reloads are ~1s)")
GOALS = {
    "machine learning": ("machine learning", "pytorch", "deep learning", "scikit", "mlops",
                         "llm", "linear algebra", "probability", "statistics", "python"),
    "robotics and ros": ("ros", "robot", "kinematics", "control system", "computer vision",
                         "opencv", "embedded", "microcontroller", "c++", "cad", "linear algebra"),
    "vlsi chip design verilog": ("verilog", "vlsi", "fpga", "rtl", "systemverilog", "uvm",
                                 "digital logic", "timing analysis", "computer architecture", "semiconductor"),
    "cloud devops kubernetes": ("kubernetes", "docker", "cloud", "devops", "terraform",
                                "linux", "ci/cd", "aws", "infrastructure", "pipeline automation"),
    "structural civil engineering": ("structural", "civil", "concrete", "etabs", "staad",
                                     "bim", "revit", "seismic", "mechanics of materials", "steel"),
    "cybersecurity pen testing": ("security", "pen test", "cryptograph", "network", "linux",
                                  "offensive", "burp", "nmap", "penetration"),
    "full stack web react": ("react", "javascript", "typescript", "front-end", "web", "node",
                             "rest", "graphql", "api", "database", "sql & nosql"),
    "data engineering pipelines": ("etl", "elt", "data modeling", "spark", "sql & data",
                                   "distributed data", "warehouse", "airflow", "dbt", "data pipeline"),
}
precisions = []
for goal, needles in GOALS.items():
    p = ProfileOnboardingRequest(experience_level="Beginner")
    res = engine.recommend(None, p, goal_text=goal, limit=10)["results"]
    hits = sum(1 for r in res
               if any(n in (r["track"] + " " + " ".join(r["skills_covered"]) + " " + r["branch"]).lower() for n in needles))
    prec = hits / max(1, len(res))
    precisions.append(prec)
    check(f"goal '{goal}' -> >=65% on-topic", prec >= 0.65, f"{hits}/{len(res)} ({prec:.0%})")
check("mean precision >= 0.85", (sum(precisions) / len(precisions)) >= 0.85,
      f"{sum(precisions) / len(precisions):.0%}")
from app.data.taxonomy_data import CAREERS_DATABASE 
bad = []
for c in CAREERS_DATABASE[:8]:
    p = ProfileOnboardingRequest(experience_level="Beginner", target_career_id=c["career_id"], hours_per_week=10)
    path = engine.build_path(None, p, c["career_id"])
    seen_titles = set()
    for m in path.milestones:
        for r in m.resources:
            pre = None
            pos = engine.catalog.df.index[engine.catalog.df["course_id"] == r.course_id].tolist()
            if pos:
                pre = str(engine.catalog.df.iloc[pos[0]]["prerequisite_course_title"]).strip().lower()
            if pre and pre in engine.catalog.title_index and pre not in seen_titles:
                later = any(pre == rr.title.strip().lower() for mm in path.milestones[path.milestones.index(m):] for rr in mm.resources)
                if later:
                    bad.append(f"{c['career_id']}: {r.title} before {pre}")
            seen_titles.add(r.title.strip().lower())
check("paths are prerequisite-ordered", not bad, f"{len(bad)} violations" + (f" e.g. {bad[0]}" if bad else ""))
check("0 unresolved prereqs in catalog", len(engine.graph.unresolved) == 0, f"{len(engine.graph.unresolved)} unresolved")
class _FakeQ:
    def __init__(self): self._m = None
    def query(self, *a, **k): return self
    def filter(self, *a, **k): return self
    def first(self): return self._m
    def join(self, *a, **k): return self
    def all(self): return []
class _FakeDB:
    def __init__(self): self.added = []
    def query(self, *a, **k): return _FakeQ()
    def add(self, o): self.added.append(o)
    def commit(self): pass
db = _FakeDB()
before = dict(engine._learner_model(db, "pX")[0])
engine.record_feedback(db, "pX", "downvote", factors={"quality": 0.9, "goal_fit": 0.1})
added = [o for o in db.added if o.__class__.__name__ == "LearnerModelDB"]
ok = bool(added) and added[-1].weights["quality"] < before["quality"]
check("downvote lowers the driving factor weight", ok,
      f"quality {before['quality']:.3f} -> {(added[-1].weights['quality'] if added else 0):.3f}")
print()
failed = [n for n, ok, _ in results if not ok]
print(f"{len(results) - len(failed)}/{len(results)} checks passed")
sys.exit(1 if failed else 0)