"""
Skill Dependency Graph Engine.

Builds a Directed Acyclic Graph (DAG) of technical skills:
- Validates topological dependency order.
- Detects circular dependencies safely using cycle detection (DFS with coloring).
- Computes unmet prerequisite chains for any target skill.
"""

import logging
from collections import defaultdict, deque
from typing import Dict, List, Set

from app.ml.skill_knowledge_base import SKILL_KNOWLEDGE_BASE

logger = logging.getLogger("careerlens.dependency_graph")


class SkillDependencyGraph:
    """Directed graph representing technical skill dependencies and learning progressions."""

    def __init__(self):
        self.adj_list: Dict[str, List[str]] = defaultdict(list)  # prerequisite -> dependent skills
        self.prereqs: Dict[str, List[str]] = defaultdict(list)   # skill -> prerequisites
        self._build_graph()

    def _build_graph(self):
        """Constructs graph edges from the knowledge base."""
        for skill_name, defn in SKILL_KNOWLEDGE_BASE.items():
            for prereq in defn.prerequisites:
                self.prereqs[skill_name].append(prereq)
                self.adj_list[prereq].append(skill_name)

        # Validate no cycles exist in knowledge base
        has_cycle, cycle_path = self.detect_cycle()
        if has_cycle:
            logger.error("Circular dependency detected in SKILL_KNOWLEDGE_BASE: %s", cycle_path)
            raise ValueError(f"Circular dependency detected in knowledge base: {cycle_path}")

    def detect_cycle(self) -> (bool, List[str]):
        """
        Detects whether any circular dependencies exist in the graph using DFS coloring.
        White=0 (unvisited), Gray=1 (currently visiting in call stack), Black=2 (visited).
        """
        all_nodes = set(SKILL_KNOWLEDGE_BASE.keys()).union(self.adj_list.keys())
        color: Dict[str, int] = {node: 0 for node in all_nodes}
        path: List[str] = []

        def dfs(node: str) -> bool:
            color[node] = 1
            path.append(node)
            for neighbor in self.adj_list.get(node, []):
                if color.get(neighbor, 0) == 1:
                    path.append(neighbor)
                    return True
                if color.get(neighbor, 0) == 0:
                    if dfs(neighbor):
                        return True
            path.pop()
            color[node] = 2
            return False

        for node in all_nodes:
            if color[node] == 0:
                if dfs(node):
                    return True, path
        return False, []

    def get_unmet_prerequisites(
        self,
        target_skill: str,
        demonstrated_skills: Set[str],
    ) -> List[str]:
        """
        Recursively identifies all transitive prerequisites for a target skill that
        the candidate has NOT yet demonstrated, ordered from most foundational to advanced.
        """
        demonstrated_lower = {s.lower() for s in demonstrated_skills}
        unmet: List[str] = []
        visited: Set[str] = set()

        def collect(skill: str):
            for prereq in self.prereqs.get(skill, []):
                if prereq not in visited:
                    visited.add(prereq)
                    # Recurse first so deeper foundational skills come first
                    collect(prereq)
                    if prereq.lower() not in demonstrated_lower and prereq.lower() != target_skill.lower():
                        if prereq not in unmet:
                            unmet.append(prereq)

        collect(target_skill)
        return unmet

    def get_topological_sort(self, skills: List[str]) -> List[str]:
        """
        Given a list of skills, returns a valid learning sequence such that
        prerequisites always appear before dependent skills (Kahn's algorithm).
        """
        skill_set = set(skills)
        in_degree: Dict[str, int] = {s: 0 for s in skill_set}
        sub_adj: Dict[str, List[str]] = defaultdict(list)

        for s in skill_set:
            for prereq in self.prereqs.get(s, []):
                if prereq in skill_set:
                    sub_adj[prereq].append(s)
                    in_degree[s] += 1

        queue = deque([s for s in skill_set if in_degree[s] == 0])
        ordered: List[str] = []

        while queue:
            curr = queue.popleft()
            ordered.append(curr)
            for neighbor in sub_adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Append any remaining skills if not in cycle
        for s in skills:
            if s not in ordered:
                ordered.append(s)

        return ordered
