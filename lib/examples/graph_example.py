#!/usr/bin/env python3
"""
Example: Using AttackGraph for HTB Challenge

This demonstrates the complete workflow:
1. Initialize empty graph
2. Add nodes during recon (hosts, services)
3. Add vulnerabilities during research
4. Update state during exploitation
5. Query frontier for next targets
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from attack_graph import (
    AttackGraph,
    NodeType,
    EdgeType,
    NodeState,
    cvss_to_score,
    confidence_to_score
)


def main():
    print("=" * 70)
    print("AttackGraph Example: HTB Editor Challenge")
    print("=" * 70)
    print()

    # Initialize graph
    graph = AttackGraph(target="10.10.11.80", challenge="editor")
    print(f"Created graph for {graph.challenge} ({graph.target})")
    print()

    # === PHASE 1: RECON ===
    print("### PHASE 1: RECON ###")
    print()

    # Add host
    host_id = graph.add_node(
        NodeType.HOST,
        label="10.10.11.80",
        properties={"os": "Linux", "hostname": "editor.htb"}
    )
    print(f"Added host: {host_id}")

    # Add ports
    port_22 = graph.add_node(NodeType.PORT, label="22/tcp")
    port_80 = graph.add_node(NodeType.PORT, label="80/tcp")
    port_8080 = graph.add_node(NodeType.PORT, label="8080/tcp")
    print(f"Added ports: {port_22}, {port_80}, {port_8080}")

    # Add services
    ssh_id = graph.add_node(
        NodeType.SERVICE,
        label="OpenSSH 8.9p1",
        properties={"product": "OpenSSH", "version": "8.9p1", "port": 22},
        weight={"severity": 0, "confidence": 5, "centrality": 0, "freshness": 10}
    )
    graph.add_edge(EdgeType.RUNS_ON, ssh_id, host_id)
    graph.add_edge(EdgeType.LISTENS_ON, ssh_id, port_22)

    nginx_id = graph.add_node(
        NodeType.SERVICE,
        label="nginx 1.18.0",
        properties={"product": "nginx", "version": "1.18.0", "port": 80},
        weight={"severity": 2, "confidence": 6, "centrality": 0, "freshness": 10}
    )
    graph.add_edge(EdgeType.RUNS_ON, nginx_id, host_id)
    graph.add_edge(EdgeType.LISTENS_ON, nginx_id, port_80)

    xwiki_id = graph.add_node(
        NodeType.SERVICE,
        label="XWiki 15.10.8",
        properties={"product": "XWiki", "version": "15.10.8", "port": 8080},
        weight={"severity": 8, "confidence": 7, "centrality": 0, "freshness": 10}
    )
    graph.add_edge(EdgeType.RUNS_ON, xwiki_id, host_id)
    graph.add_edge(EdgeType.LISTENS_ON, xwiki_id, port_8080)

    print(f"Added services: {ssh_id}, {nginx_id}, {xwiki_id}")
    print()

    # === PHASE 2: RESEARCH ===
    print("### PHASE 2: RESEARCH ###")
    print()

    # Research found CVE for XWiki
    cve_id = graph.add_node(
        NodeType.VULN,
        label="CVE-2025-24893",
        properties={
            "cve": "CVE-2025-24893",
            "cvss": 9.8,
            "type": "RCE",
            "description": "Unauthenticated RCE via SolrSearch Groovy injection",
            "auth_required": False,
            "exploit_available": True,
            "references": [
                "https://github.com/dollarboysushil/CVE-2025-24893",
                "https://exploit-db.com/exploits/52136"
            ]
        },
        weight={
            "severity": cvss_to_score("critical"),
            "confidence": confidence_to_score("high"),
            "centrality": 0,
            "freshness": 10
        }
    )
    graph.add_edge(EdgeType.VULNERABLE_TO, xwiki_id, cve_id, probability=0.95)
    print(f"Added vulnerability: {cve_id}")

    # Add exploitation technique
    technique_id = graph.add_node(
        NodeType.TECHNIQUE,
        label="Groovy Injection",
        properties={
            "method": "SolrSearch macro exploitation",
            "complexity": "low",
            "detection_risk": "medium"
        }
    )
    graph.add_edge(EdgeType.EXPLOITS, technique_id, cve_id)
    print(f"Added technique: {technique_id}")
    print()

    # === DISPLAY FRONTIER ===
    print("### FRONTIER (Before Exploitation) ###")
    print()
    print(graph.render_frontier())
    print()

    # === PHASE 3: EXPLOITATION ===
    print("### PHASE 3: EXPLOITATION ###")
    print()

    # Select target from frontier
    frontier = graph.get_frontier(limit=1)
    if frontier:
        target_node_id, score, reason = frontier[0]
        print(f"Selected target: {target_node_id} (score={score}, reason={reason})")
        print()

        # Simulate successful exploitation
        graph.update_node_state(target_node_id, NodeState.EXPLOITED, result="success")

        # Add shell node
        shell_id = graph.add_node(
            NodeType.SHELL,
            label="www-data shell",
            properties={
                "user": "www-data",
                "method": "reverse_shell",
                "stability": "stable"
            },
            weight={"severity": 7, "confidence": 10, "centrality": 0, "freshness": 10},
            state=NodeState.EXPLOITED
        )
        graph.add_edge(EdgeType.YIELDS, cve_id, shell_id, probability=0.85, effort=3)
        print(f"Shell obtained: {shell_id}")

        # Record attack chain
        graph.add_attack_chain(
            name="XWiki RCE to www-data",
            node_ids=[host_id, xwiki_id, cve_id, shell_id],
            status="successful",
            total_effort=3
        )
        print("Attack chain recorded")
        print()

    # === PHASE 4: POST-EXPLOITATION ===
    print("### PHASE 4: POST-EXPLOITATION ###")
    print()

    # Enumerate from shell
    path_id = graph.add_node(
        NodeType.PATH,
        label="/home/dev/.ssh/id_rsa",
        properties={"type": "file", "permissions": "600", "owner": "dev"}
    )
    graph.add_edge(EdgeType.ACCESSES, shell_id, path_id)

    cred_id = graph.add_node(
        NodeType.CREDENTIAL,
        label="dev:ssh_key",
        properties={"type": "ssh_key", "user": "dev"},
        weight={"severity": 7, "confidence": 8, "centrality": 0, "freshness": 10}
    )
    graph.add_edge(EdgeType.CONTAINS, path_id, cred_id)

    # Credential can authenticate to SSH
    graph.add_edge(EdgeType.AUTHENTICATES, cred_id, ssh_id, probability=0.9, effort=1)

    print(f"Found credential: {cred_id}")
    print(f"Path: {path_id}")
    print()

    # === DISPLAY UPDATED STATE ===
    print("### ASCII GRAPH VISUALIZATION ###")
    print()
    print(graph.render_ascii())
    print()

    print("### UPDATED FRONTIER ###")
    print()
    print(graph.render_frontier())
    print()

    # === SAVE GRAPH ===
    output_file = Path("htb-targets/editor/attack-graph.json")
    graph.save(output_file)
    print(f"Graph saved to: {output_file}")
    print()

    # === GRAPH STATISTICS ===
    print("### GRAPH STATISTICS ###")
    print()
    print(f"Total nodes: {len(graph.nodes)}")
    print(f"Total edges: {len(graph.edges)}")
    print(f"Node types:")
    for node_type in NodeType:
        count = len(graph.find_nodes(node_type))
        if count > 0:
            print(f"  - {node_type.value}: {count}")
    print(f"Attack chains: {len(graph.attack_chains)}")
    print()

    # === LOAD TEST ===
    print("### TESTING PERSISTENCE ###")
    print()
    print(f"Loading graph from {output_file}...")
    loaded_graph = AttackGraph.load(output_file)
    print(f"Loaded successfully!")
    print(f"  - Target: {loaded_graph.target}")
    print(f"  - Challenge: {loaded_graph.challenge}")
    print(f"  - Nodes: {len(loaded_graph.nodes)}")
    print(f"  - Edges: {len(loaded_graph.edges)}")
    print()

    print("=" * 70)
    print("Example complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
