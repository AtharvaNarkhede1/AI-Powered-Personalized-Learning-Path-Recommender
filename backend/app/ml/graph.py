from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import networkx as nx
from app.ml.catalog import Catalog, Rung

@dataclass
class PrereqGraph:
    g: nx.DiGraph
    depth: Dict[Rung, int] = field(default_factory=dict)
    unresolved: List[str] = field(default_factory=list)

    def prereq_rungs(self, rung: Rung) -> List[Rung]:
        return list(self.g.predecessors(rung)) if rung in self.g else []

    def ancestors(self, rung: Rung) -> set:
        return nx.ancestors(self.g, rung) if rung in self.g else set()

    def topo_order(self, rungs) -> List[Rung]:
        want = set(rungs)
        for r in list(want):
            want |= self.ancestors(r)
        sub = self.g.subgraph(want)
        try:
            return list(nx.topological_sort(sub))
        except nx.NetworkXUnfeasible:
            return sorted(want, key=lambda r: (self.depth.get(r, 0), r[2]))

def build_graph(catalog: Catalog) -> PrereqGraph:
    g = nx.DiGraph()
    for rung in catalog.variant_index:
        g.add_node(rung)
    title_to_rungs: Dict[str, List[Rung]] = {}
    for pos, title in enumerate(catalog.df['course_title'].str.strip().str.lower()):
        row = catalog.df.iloc[pos]
        rung: Rung = (row['branch'], row['track'], int(catalog.tiers[pos]))
        title_to_rungs.setdefault(title, [])
        if rung not in title_to_rungs[title]:
            title_to_rungs[title].append(rung)
    unresolved: List[str] = []
    for rung, positions in catalog.variant_index.items():
        branch, track, tier = rung
        seen_titles = set()
        for p in positions:
            pt = str(catalog.df.iloc[p]['prerequisite_course_title']).strip().lower()
            if not pt or pt in seen_titles:
                continue
            seen_titles.add(pt)
            targets = title_to_rungs.get(pt, [])
            same = [t for t in targets if t[1] == track]
            chosen = same[0] if same else targets[0] if targets else None
            if chosen is None:
                unresolved.append(f'{track} <- {pt}')
                if tier > 0:
                    chosen = (branch, track, tier - 1)
                else:
                    continue
            if chosen != rung:
                g.add_edge(chosen, rung)
    for (branch, track), _ in catalog.track_index.items():
        for tier in (1, 2, 3):
            lo, hi = ((branch, track, tier - 1), (branch, track, tier))
            if lo in g and hi in g and (not nx.has_path(g, hi, lo)):
                g.add_edge(lo, hi)
    while not nx.is_directed_acyclic_graph(g):
        cycle = nx.find_cycle(g, orientation='original')
        u, v, _ = max(cycle, key=lambda e: e[1][2])
        g.remove_edge(u, v)
    depth: Dict[Rung, int] = {}
    for rung in nx.topological_sort(g):
        preds = list(g.predecessors(rung))
        depth[rung] = 1 + max((depth[p] for p in preds), default=-1)
    return PrereqGraph(g=g, depth=depth, unresolved=unresolved)
