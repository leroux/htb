#!/usr/bin/env python3
"""
Migrate flat JSON files to AttackGraph format

Converts existing services.json and vulns.json into a unified attack-graph.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from attack_graph import (
    AttackGraph,
    NodeType,
    EdgeType,
    NodeState,
    cvss_to_score,
    confidence_to_score
)


def load_json_file(filepath: Path) -> Dict[str, Any]:
    """Load JSON file, return empty dict if not found"""
    if not filepath.exists():
        print(f"Warning: {filepath} not found, skipping")
        return {}

    with open(filepath, 'r') as f:
        return json.load(f)


def migrate_services(graph: AttackGraph, services_data: Dict) -> Dict[str, str]:
    """
    Migrate services.json to graph nodes.

    Returns mapping of port -> service_node_id for later use
    """
    if not services_data:
        return {}

    print("Migrating services.json...")

    # Add host node
    target = services_data.get("target", graph.target)
    host_id = graph.add_node(
        NodeType.HOST,
        label=target,
        properties={"scan_timestamp": services_data.get("scan_timestamp")}
    )
    print(f"  Added host: {host_id}")

    port_to_service = {}

    # Add services
    for service in services_data.get("services", []):
        port = service.get("port")
        protocol = service.get("protocol", "tcp")
        service_name = service.get("service", "unknown")
        version = service.get("version", "")
        product = service.get("product", service_name)

        # Create label
        if version:
            label = f"{product} {version}"
        else:
            label = product

        # Calculate weight based on service exposure
        severity = 0
        if service_name in ["http", "https"]:
            severity = 5  # Web services are common targets
        elif service_name in ["smb", "ftp", "telnet"]:
            severity = 6  # Often misconfigured
        elif service_name == "ssh":
            severity = 2  # Lower risk if up to date

        # Add service node
        service_id = graph.add_node(
            NodeType.SERVICE,
            label=label,
            properties={
                "port": port,
                "protocol": protocol,
                "service": service_name,
                "version": version,
                "product": product,
                "extraInfo": service.get("extraInfo", "")
            },
            weight={
                "severity": severity,
                "confidence": 7 if version else 5,
                "centrality": 0,
                "freshness": 10
            }
        )

        # Add port node
        port_id = graph.add_node(
            NodeType.PORT,
            label=f"{port}/{protocol}"
        )

        # Add edges
        graph.add_edge(EdgeType.RUNS_ON, service_id, host_id)
        graph.add_edge(EdgeType.LISTENS_ON, service_id, port_id)

        port_to_service[port] = service_id
        print(f"  Added service: {service_id} ({label}) on port {port}")

    # Add web services if present
    for web_service in services_data.get("webServices", []):
        port = web_service.get("port")
        if port in port_to_service:
            # Update existing service node with web details
            service_id = port_to_service[port]
            service_node = graph.get_node(service_id)
            if service_node:
                service_node["properties"]["url"] = web_service.get("url")
                service_node["properties"]["title"] = web_service.get("title")
                service_node["properties"]["technologies"] = web_service.get("technologies", [])
                service_node["properties"]["directories"] = web_service.get("directories", [])
                print(f"  Updated {service_id} with web details")

    return port_to_service


def migrate_vulns(graph: AttackGraph, vulns_data: Dict, port_to_service: Dict[str, str]):
    """Migrate vulns.json to graph nodes"""
    if not vulns_data:
        return

    print("Migrating vulns.json...")

    for vector in vulns_data.get("vectors", []):
        vector_id = vector.get("id")
        vector_type = vector.get("type", "unknown")
        name = vector.get("name")
        service_name = vector.get("service", "")
        port = vector.get("port")
        severity = vector.get("severity", "medium")
        confidence = vector.get("confidence", "medium")
        description = vector.get("description", "")
        references = vector.get("references", [])
        exploit_available = vector.get("exploit_available", False)
        auth_required = vector.get("auth_required", False)
        tested = vector.get("tested", False)
        result = vector.get("result")

        # Map to node type
        if vector_type == "cve":
            node_type = NodeType.VULN
        elif vector_type == "default_creds":
            node_type = NodeType.CREDENTIAL
        else:
            node_type = NodeType.VULN

        # Create vuln node
        vuln_id = graph.add_node(
            node_type,
            label=name,
            properties={
                "original_id": vector_id,
                "type": vector_type,
                "service": service_name,
                "port": port,
                "description": description,
                "references": references,
                "exploit_available": exploit_available,
                "auth_required": auth_required,
                "cve": name if vector_type == "cve" else None
            },
            weight={
                "severity": cvss_to_score(severity),
                "confidence": confidence_to_score(confidence),
                "centrality": 0,
                "freshness": 5 if tested else 10
            },
            state=NodeState.INVESTIGATED if tested else NodeState.DISCOVERED
        )

        # Link to service if port mapping exists
        if port and port in port_to_service:
            service_id = port_to_service[port]
            probability = 0.95 if exploit_available else 0.5
            graph.add_edge(
                EdgeType.VULNERABLE_TO,
                service_id,
                vuln_id,
                probability=probability,
                effort=1 if not auth_required else 3
            )
            print(f"  Added vuln: {vuln_id} ({name}) -> {service_id}")
        else:
            print(f"  Added vuln: {vuln_id} ({name}) [orphaned - no service link]")

        # Update with result if tested
        if tested and result:
            graph.update_node_state(
                vuln_id,
                NodeState.EXPLOITED if "success" in result.lower() else NodeState.FAILED,
                result=result
            )


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 migrate_to_graph.py <target_dir>")
        print()
        print("Example:")
        print("  python3 migrate_to_graph.py htb-targets/editor")
        print()
        print("Reads:")
        print("  - <target_dir>/services.json")
        print("  - <target_dir>/vulns.json")
        print()
        print("Writes:")
        print("  - <target_dir>/attack-graph.json")
        sys.exit(1)

    target_dir = Path(sys.argv[1])

    if not target_dir.exists():
        print(f"Error: Directory {target_dir} does not exist")
        sys.exit(1)

    # Extract target info from directory structure
    challenge = target_dir.name
    target_ip = "unknown"

    # Try to read target from existing files
    vulns_file = target_dir / "vulns.json"
    if vulns_file.exists():
        with open(vulns_file) as f:
            data = json.load(f)
            target_ip = data.get("target", target_ip)

    print("=" * 70)
    print(f"Migrating to AttackGraph: {challenge}")
    print("=" * 70)
    print()

    # Load existing data
    services_data = load_json_file(target_dir / "services.json")
    vulns_data = load_json_file(target_dir / "vulns.json")

    if not services_data and not vulns_data:
        print("Error: No services.json or vulns.json found")
        sys.exit(1)

    # Create graph
    graph = AttackGraph(target=target_ip, challenge=challenge)

    # Migrate services
    port_to_service = migrate_services(graph, services_data)

    # Migrate vulnerabilities
    migrate_vulns(graph, vulns_data, port_to_service)

    # Save graph
    output_file = target_dir / "attack-graph.json"
    graph.save(output_file)

    print()
    print("=" * 70)
    print(f"Migration complete!")
    print("=" * 70)
    print()
    print(f"Output: {output_file}")
    print()
    print(f"Statistics:")
    print(f"  - Total nodes: {len(graph.nodes)}")
    print(f"  - Total edges: {len(graph.edges)}")
    print(f"  - Services: {len(graph.find_nodes(NodeType.SERVICE))}")
    print(f"  - Vulnerabilities: {len(graph.find_nodes(NodeType.VULN))}")
    print()

    # Display frontier
    print("Frontier (top 5 targets):")
    print()
    for i, (node_id, score, reason) in enumerate(graph.get_frontier(5), 1):
        node = graph.get_node(node_id)
        print(f"  {i}. [{node['type']}] {node['label']:30s} score={score:.1f}")
        print(f"     {reason}")
    print()


if __name__ == "__main__":
    main()
