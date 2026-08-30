"""Pre-fit the TF-IDF+SVD semantic space and pickle it so the first API
request is fast.  Run:  python -m scripts.build_cache
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.engine import engine  # noqa: E402

if __name__ == "__main__":
    engine.warm()
    print(f"cache ready: {len(engine.catalog)} courses, {len(engine.graph.g)} rungs")
