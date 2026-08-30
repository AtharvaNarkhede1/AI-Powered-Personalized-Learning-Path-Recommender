from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
DIFFICULTY_TIER = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2, 'Capstone': 3}
TIER_NAME = {v: k for k, v in DIFFICULTY_TIER.items()}
LIST_COLUMNS = ('skills_taught', 'tools_covered', 'career_paths', 'industry_sectors')
RATING_PRIOR_WEIGHT = 150.0
Rung = Tuple[str, str, int]

def _split(cell: str) -> List[str]:
    if not isinstance(cell, str):
        return []
    return [tok.strip().lower() for tok in cell.split(';') if tok.strip()]

@dataclass
class Catalog:
    df: pd.DataFrame
    docs: List[str]
    quality: np.ndarray
    tiers: np.ndarray
    skill_lists: List[List[str]]
    career_lists: List[List[str]]
    variant_index: Dict[Rung, List[int]] = field(default_factory=dict)
    track_index: Dict[Tuple[str, str], List[int]] = field(default_factory=dict)
    title_index: Dict[str, List[int]] = field(default_factory=dict)
    career_index: Dict[str, List[int]] = field(default_factory=dict)
    skills_vocab: List[str] = field(default_factory=list)
    careers_vocab: List[str] = field(default_factory=list)
    tracks_vocab: List[str] = field(default_factory=list)
    branches_vocab: List[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.df)

    def row(self, pos: int) -> pd.Series:
        return self.df.iloc[pos]
FIELD_WEIGHTS = {'course_title': 3, 'track': 3, 'skills_taught': 2, 'career_paths': 2, 'tools_covered': 1, 'branch': 1, 'industry_sectors': 1, 'description': 1}

def _build_doc(row: pd.Series) -> str:
    parts: List[str] = []
    for col, w in FIELD_WEIGHTS.items():
        val = row.get(col, '')
        if not isinstance(val, str):
            continue
        parts.extend([val.replace(';', ' ').lower()] * w)
    return ' '.join(parts)

def load_catalog(csv_path: str) -> Catalog:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'course dataset not found: {csv_path}\nrun  python -m scripts.generate_dataset  first.')
    df = pd.read_csv(csv_path).fillna('')
    df['estimated_hours'] = pd.to_numeric(df['estimated_hours'], errors='coerce').fillna(20.0)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(4.0)
    df['num_reviews'] = pd.to_numeric(df['num_reviews'], errors='coerce').fillna(0).astype(int)
    df = df.reset_index(drop=True)
    docs = [_build_doc(r) for _, r in df.iterrows()]
    tiers = df['difficulty_level'].map(lambda x: DIFFICULTY_TIER.get(x, 1)).to_numpy()
    global_mean = float(df['rating'].mean())
    v = df['num_reviews'].to_numpy()
    r = df['rating'].to_numpy()
    shrunk = (v * r + RATING_PRIOR_WEIGHT * global_mean) / (v + RATING_PRIOR_WEIGHT)
    quality = np.clip((shrunk - 3.0) / 2.0, 0.0, 1.0)
    skill_lists = [_split(c) for c in df['skills_taught']]
    career_lists = [_split(c) for c in df['career_paths']]
    cat = Catalog(df=df, docs=docs, quality=quality, tiers=tiers, skill_lists=skill_lists, career_lists=career_lists)
    for pos, row in df.iterrows():
        rung: Rung = (row['branch'], row['track'], int(tiers[pos]))
        cat.variant_index.setdefault(rung, []).append(pos)
        cat.track_index.setdefault((row['branch'], row['track']), []).append(pos)
        cat.title_index.setdefault(str(row['course_title']).strip().lower(), []).append(pos)
        for c in career_lists[pos]:
            cat.career_index.setdefault(c, []).append(pos)
    cat.skills_vocab = sorted({s for lst in skill_lists for s in lst})
    cat.careers_vocab = sorted(cat.career_index.keys())
    cat.tracks_vocab = sorted(df['track'].str.lower().unique().tolist())
    cat.branches_vocab = sorted(df['branch'].unique().tolist())
    return cat
