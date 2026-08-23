"""
Graph Processing Engine using NetworkX.
Constructs a Directed Acyclic Graph (DAG) of skills and prerequisites to generate topologically sorted, prerequisite-aware learning sequences.
"""
import networkx as nx
from typing import List, Dict, Any
from app.data.taxonomy_data import SKILLS_DATABASE


def build_skill_prerequisite_graph() -> nx.DiGraph:
    """Builds a NetworkX Directed Graph where edges represent prerequisite dependencies (A -> B means A is prereq for B)."""
    G = nx.DiGraph()

    for skill_id, info in SKILLS_DATABASE.items():
        G.add_node(skill_id, name=info["name"], category=info.get("category", "General"))
        for prereq in info.get("prerequisites", []):
            G.add_edge(prereq, skill_id)

    return G


def get_topologically_sorted_skills(target_skill_ids: List[str]) -> List[str]:
    """Given a set of target skill IDs, resolves all required ancestors (prerequisites) and returns a topologically sorted execution order."""
    G = build_skill_prerequisite_graph()

    # Expand target skills to include all upstream prerequisite dependencies
    needed_nodes = set(target_skill_ids)
    for target in list(needed_nodes):
        if target in G:
            ancestors = nx.ancestors(G, target)
            needed_nodes.update(ancestors)

    subgraph = G.subgraph(needed_nodes)

    try:
        sorted_order = list(nx.topological_sort(subgraph))
    except nx.NetworkXUnfeasible:
        # Cycle detected fallback
        sorted_order = list(needed_nodes)

    return sorted_order
