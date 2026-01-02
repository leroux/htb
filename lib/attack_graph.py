#!/usr/bin/env python3
"""
AttackGraph - Graph-based penetration testing tracker

Models pentesting as graph traversal where:
- Nodes = discovered entities (hosts, services, vulns, shells, etc.)
- Edges = relationships between entities
- Weights = priority scores for decision making
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from pathlib import Path


class NodeType(str, Enum):
    """Types of nodes in the attack graph"""
    HOST = "HOST"
    SERVICE = "SERVICE"
    PORT = "PORT"
    VULN = "VULN"
    CREDENTIAL = "CREDENTIAL"
    SHELL = "SHELL"
    FLAG = "FLAG"
    PATH = "PATH"
    TECHNIQUE = "TECHNIQUE"


class EdgeType(str, Enum):
    """Types of edges (relationships) in the attack graph"""
    RUNS_ON = "RUNS_ON"
    LISTENS_ON = "LISTENS_ON"
    VULNERABLE_TO = "VULNERABLE_TO"
    EXPLOITS = "EXPLOITS"
    REQUIRES = "REQUIRES"
    YIELDS = "YIELDS"
    ACCESSES = "ACCESSES"
    CONTAINS = "CONTAINS"
    AUTHENTICATES = "AUTHENTICATES"
    PIVOTS_TO = "PIVOTS_TO"
    HAS_FLAG = "HAS_FLAG"


class NodeState(str, Enum):
    """Investigation state of a node"""
    DISCOVERED = "discovered"      # Found but not investigated
    INVESTIGATED = "investigated"  # Examined, may have children
    EXPLOITED = "exploited"        # Successfully exploited
    FAILED = "failed"              # Exploitation failed
    EXHAUSTED = "exhausted"        # No more paths to explore


class AttackGraph:
    """
    Attack graph for tracking penetration testing progress.

    Stores nodes (entities), edges (relationships), and provides
    graph operations for target selection and path analysis.
    """

    def __init__(self, target: str, challenge: str):
        self.target = target
        self.challenge = challenge
        self.created = datetime.now().isoformat()
        self.last_updated = self.created
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
        self.attack_chains: List[Dict] = []
        self._node_counter = 0
        self._edge_counter = 0

    def add_node(
        self,
        node_type: NodeType,
        label: str,
        properties: Optional[Dict] = None,
        weight: Optional[Dict[str, float]] = None,
        state: NodeState = NodeState.DISCOVERED
    ) -> str:
        """
        Add a node to the graph.

        Args:
            node_type: Type of node (HOST, SERVICE, VULN, etc.)
            label: Human-readable label
            properties: Additional properties dict
            weight: Weight dict with severity, confidence, centrality, freshness
            state: Investigation state

        Returns:
            node_id: Unique identifier for the node
        """
        self._node_counter += 1
        node_id = f"{node_type.value.lower()}-{self._node_counter:03d}"

        # Default weights if not provided
        if weight is None:
            weight = {
                "severity": 0.0,
                "confidence": 5.0,
                "centrality": 0.0,
                "freshness": 10.0
            }

        node = {
            "id": node_id,
            "type": node_type.value,
            "label": label,
            "properties": properties or {},
            "weight": weight,
            "state": state.value,
            "discovered_at": datetime.now().isoformat(),
            "investigated": False
        }

        self.nodes[node_id] = node
        self.last_updated = datetime.now().isoformat()
        return node_id

    def add_edge(
        self,
        edge_type: EdgeType,
        source_id: str,
        target_id: str,
        properties: Optional[Dict] = None,
        probability: float = 1.0,
        effort: int = 1
    ) -> str:
        """
        Add an edge between two nodes.

        Args:
            edge_type: Type of relationship
            source_id: Source node ID
            target_id: Target node ID
            properties: Additional properties
            probability: Likelihood this edge is valid (0-1)
            effort: Relative difficulty to traverse (1-10)

        Returns:
            edge_id: Unique identifier for the edge
        """
        if source_id not in self.nodes:
            raise ValueError(f"Source node {source_id} not found")
        if target_id not in self.nodes:
            raise ValueError(f"Target node {target_id} not found")

        self._edge_counter += 1
        edge_id = f"edge-{self._edge_counter:03d}"

        edge = {
            "id": edge_id,
            "type": edge_type.value,
            "source": source_id,
            "target": target_id,
            "properties": properties or {},
            "weight": {
                "probability": probability,
                "effort": effort
            }
        }

        self.edges.append(edge)

        # Update centrality for both nodes
        self._update_centrality(source_id)
        self._update_centrality(target_id)

        self.last_updated = datetime.now().isoformat()
        return edge_id

    def update_node_state(self, node_id: str, state: NodeState, result: Optional[str] = None):
        """Update the state of a node after investigation/exploitation"""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        self.nodes[node_id]["state"] = state.value
        self.nodes[node_id]["investigated"] = True

        if result:
            self.nodes[node_id]["properties"]["result"] = result

        # Decrease freshness after investigation
        self.nodes[node_id]["weight"]["freshness"] = max(
            0, self.nodes[node_id]["weight"]["freshness"] - 2
        )

        self.last_updated = datetime.now().isoformat()

    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def find_nodes(self, node_type: Optional[NodeType] = None, state: Optional[NodeState] = None) -> List[Dict]:
        """
        Find nodes matching criteria.

        Args:
            node_type: Filter by node type
            state: Filter by investigation state

        Returns:
            List of matching nodes
        """
        results = list(self.nodes.values())

        if node_type:
            results = [n for n in results if n["type"] == node_type.value]

        if state:
            results = [n for n in results if n["state"] == state.value]

        return results

    def get_edges_from(self, node_id: str) -> List[Dict]:
        """Get all edges originating from a node"""
        return [e for e in self.edges if e["source"] == node_id]

    def get_edges_to(self, node_id: str) -> List[Dict]:
        """Get all edges pointing to a node"""
        return [e for e in self.edges if e["target"] == node_id]

    def calculate_priority_score(self, node_id: str) -> float:
        """
        Calculate priority score for a node.

        Formula: (severity * 0.4) + (confidence * 0.3) + (centrality * 0.2) + (freshness * 0.1)

        Returns:
            Priority score (0-10)
        """
        node = self.nodes.get(node_id)
        if not node:
            return 0.0

        w = node["weight"]
        score = (
            w["severity"] * 0.4 +
            w["confidence"] * 0.3 +
            w["centrality"] * 0.2 +
            w["freshness"] * 0.1
        )
        return round(score, 2)

    def get_frontier(self, limit: int = 10) -> List[Tuple[str, float, str]]:
        """
        Get the frontier: unexplored high-value nodes.

        Args:
            limit: Maximum number of nodes to return

        Returns:
            List of (node_id, priority_score, reason) tuples, sorted by priority
        """
        candidates = []

        for node_id, node in self.nodes.items():
            # Skip exhausted or failed nodes
            if node["state"] in [NodeState.EXHAUSTED.value, NodeState.FAILED.value]:
                continue

            # Prioritize unexplored nodes
            if not node["investigated"]:
                score = self.calculate_priority_score(node_id)
                reason = self._generate_reason(node)
                candidates.append((node_id, score, reason))

        # Sort by priority score descending
        candidates.sort(key=lambda x: x[1], reverse=True)

        return candidates[:limit]

    def add_attack_chain(self, name: str, node_ids: List[str], status: str, total_effort: int):
        """Record a successful attack chain"""
        chain = {
            "id": f"chain-{len(self.attack_chains) + 1:03d}",
            "name": name,
            "nodes": node_ids,
            "status": status,
            "total_effort": total_effort,
            "timestamp": datetime.now().isoformat()
        }
        self.attack_chains.append(chain)
        self.last_updated = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Export graph to dictionary"""
        return {
            "target": self.target,
            "challenge": self.challenge,
            "created": self.created,
            "last_updated": self.last_updated,
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "paths": {
                "attack_chains": self.attack_chains
            },
            "frontier": {
                "unexplored": [n["id"] for n in self.nodes.values() if not n["investigated"]],
                "next_targets": [
                    {"node_id": nid, "priority_score": score, "reason": reason}
                    for nid, score, reason in self.get_frontier(5)
                ]
            }
        }

    def save(self, filepath: Path):
        """Save graph to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> 'AttackGraph':
        """Load graph from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)

        graph = cls(data["target"], data["challenge"])
        graph.created = data["created"]
        graph.last_updated = data["last_updated"]

        # Rebuild nodes dict
        for node in data["nodes"]:
            graph.nodes[node["id"]] = node
            # Update counter to avoid ID collisions
            node_num = int(node["id"].split("-")[-1])
            graph._node_counter = max(graph._node_counter, node_num)

        # Rebuild edges
        graph.edges = data["edges"]
        for edge in graph.edges:
            edge_num = int(edge["id"].split("-")[-1])
            graph._edge_counter = max(graph._edge_counter, edge_num)

        # Rebuild attack chains
        if "paths" in data and "attack_chains" in data["paths"]:
            graph.attack_chains = data["paths"]["attack_chains"]

        return graph

    def render_ascii(self) -> str:
        """Render graph as ASCII tree"""
        lines = [
            f"Attack Graph: {self.challenge} ({self.target})",
            "━" * 60,
            ""
        ]

        # Find root hosts
        hosts = self.find_nodes(NodeType.HOST)

        for host in hosts:
            lines.append(f"[HOST] {host['label']}")
            self._render_children(host["id"], lines, indent=1)
            lines.append("")

        return "\n".join(lines)

    def render_frontier(self) -> str:
        """Render frontier as formatted list"""
        frontier = self.get_frontier()

        lines = [
            "Frontier (Next Targets):",
            "━" * 60
        ]

        for i, (node_id, score, reason) in enumerate(frontier, 1):
            node = self.nodes[node_id]
            lines.append(f"{i}. [{node['type']}] {node['label']:20s} score={score:.1f}  {reason}")

        return "\n".join(lines)

    # Private helper methods

    def _update_centrality(self, node_id: str):
        """Update centrality based on edge count"""
        in_edges = len(self.get_edges_to(node_id))
        out_edges = len(self.get_edges_from(node_id))
        total_edges = in_edges + out_edges

        # Centrality score: 0-10 based on edge count
        self.nodes[node_id]["weight"]["centrality"] = min(10, total_edges)

    def _generate_reason(self, node: Dict) -> str:
        """Generate human-readable reason for investigating node"""
        node_type = node["type"]
        state = node["state"]

        if node_type == "VULN" and state == "discovered":
            severity = node["properties"].get("severity", "unknown")
            return f"Untested {severity} vulnerability"
        elif node_type == "SHELL" and state == "exploited":
            return "Fresh shell, check for privesc"
        elif node_type == "CREDENTIAL" and state == "discovered":
            return "Try credential on other services"
        elif node_type == "SERVICE" and state == "discovered":
            return "Unexplored service, enumerate for vulns"
        elif node_type == "PATH" and state == "discovered":
            return "Unexplored path, may contain loot"
        else:
            return "High priority target"

    def _render_children(self, node_id: str, lines: List[str], indent: int):
        """Recursively render child nodes"""
        edges = self.get_edges_from(node_id)

        for i, edge in enumerate(edges):
            target_id = edge["target"]
            target = self.nodes[target_id]

            is_last = (i == len(edges) - 1)
            prefix = "  " * indent + ("└─" if is_last else "├─")

            # State indicator
            state = target["state"]
            indicator = {
                "discovered": "⚪",
                "investigated": "○",
                "exploited": "✓",
                "failed": "✗",
                "exhausted": "◌"
            }.get(state, "?")

            label = f"[{target['type']}] {target['label']} {indicator}"
            lines.append(f"{prefix}{label}")

            # Recurse
            if target["state"] not in ["failed", "exhausted"]:
                self._render_children(target_id, lines, indent + 1)


# Convenience functions

def cvss_to_score(severity: str) -> float:
    """Convert severity string to numeric score"""
    mapping = {
        "critical": 10.0,
        "high": 8.0,
        "medium": 5.0,
        "low": 2.0,
        "info": 0.5
    }
    return mapping.get(severity.lower(), 0.0)


def confidence_to_score(confidence: str) -> float:
    """Convert confidence string to numeric score"""
    mapping = {
        "high": 9.0,
        "medium": 6.0,
        "low": 3.0
    }
    return mapping.get(confidence.lower(), 5.0)
