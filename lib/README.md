# HTB Attack Graph Library

Graph-based penetration testing tracker for HTB autopwn workflows.

## Overview

The `attack_graph` module models penetration testing as **graph traversal**:

- **Nodes** = Entities discovered (hosts, services, vulns, shells, credentials, flags)
- **Edges** = Relationships between entities (runs_on, vulnerable_to, yields, etc.)
- **Weights** = Priority scores for intelligent target selection

## Installation

No external dependencies required - uses Python 3 standard library.

```bash
# Make scripts executable
chmod +x lib/*.py
chmod +x lib/examples/*.py
```

## Quick Start

### 1. Run the Example

See a complete workflow demonstration:

```bash
cd /home/user/htb
python3 lib/examples/graph_example.py
```

This creates a sample graph for the "editor" challenge showing:
- Recon phase (adding hosts, services, ports)
- Research phase (adding vulnerabilities)
- Exploitation phase (obtaining shells)
- Post-exploitation (finding credentials)
- Frontier queries (what to investigate next)

### 2. Migrate Existing Data

Convert your existing `services.json` and `vulns.json` to graph format:

```bash
python3 lib/migrate_to_graph.py htb-targets/editor
```

This reads flat JSON files and creates `attack-graph.json` with full relationships.

## Usage in Python

### Creating a Graph

```python
from lib.attack_graph import AttackGraph, NodeType, EdgeType

# Initialize
graph = AttackGraph(target="10.10.11.80", challenge="editor")

# Add a host
host_id = graph.add_node(NodeType.HOST, label="10.10.11.80")

# Add a service
service_id = graph.add_node(
    NodeType.SERVICE,
    label="XWiki 15.10.8",
    properties={"port": 8080, "version": "15.10.8"},
    weight={"severity": 8.0, "confidence": 7.0, "centrality": 0, "freshness": 10.0}
)

# Link service to host
graph.add_edge(EdgeType.RUNS_ON, service_id, host_id)
```

### Querying the Frontier

Get the highest-priority unexplored targets:

```python
# Get top 5 targets
frontier = graph.get_frontier(limit=5)

for node_id, score, reason in frontier:
    node = graph.get_node(node_id)
    print(f"[{node['type']}] {node['label']} - score={score:.1f}")
    print(f"  Reason: {reason}")
```

### Updating Node State

Track investigation progress:

```python
from lib.attack_graph import NodeState

# Mark vulnerability as exploited
graph.update_node_state(vuln_id, NodeState.EXPLOITED, result="shell obtained")

# Mark as failed
graph.update_node_state(vuln_id, NodeState.FAILED, result="exploit timeout")
```

### Saving and Loading

```python
from pathlib import Path

# Save
graph.save(Path("htb-targets/editor/attack-graph.json"))

# Load
loaded = AttackGraph.load(Path("htb-targets/editor/attack-graph.json"))
```

### Visualization

```python
# ASCII tree
print(graph.render_ascii())

# Frontier list
print(graph.render_frontier())
```

## Integration with FlowCoder

### In PROMPT Blocks

Claude can read/write graphs in prompt blocks:

```json
{
  "id": "exploit-001",
  "type": "prompt",
  "name": "SELECT TARGET",
  "prompt": "Read attack-graph.json and select the highest priority unexplored node.\n\nUse Python:\n```python\nfrom lib.attack_graph import AttackGraph\ngraph = AttackGraph.load('attack-graph.json')\nfrontier = graph.get_frontier(limit=1)\ntarget = frontier[0] if frontier else None\n```\n\nExploit the selected target and update the graph.",
  "output_schema": {
    "type": "object",
    "properties": {
      "selectedTarget": {"type": "string"},
      "priorityScore": {"type": "number"}
    }
  }
}
```

### Workflow Pattern

```
START
  ↓
RECON (add services to graph)
  ↓
RESEARCH (add vulns to graph)
  ↓
EXPLOIT LOOP:
  - Query frontier for next target
  - Attempt exploitation
  - Update graph state
  - Add new nodes (shells, creds)
  ↓
BRANCH (continue if frontier not empty)
```

## Node Types

| Type | Description | Example |
|------|-------------|---------|
| `HOST` | Target machine | 10.10.11.80 |
| `SERVICE` | Running service | XWiki 15.10.8 |
| `PORT` | Network port | 8080/tcp |
| `VULN` | Vulnerability | CVE-2025-24893 |
| `CREDENTIAL` | Auth material | admin:password |
| `SHELL` | Obtained access | www-data shell |
| `FLAG` | Captured loot | user.txt contents |
| `PATH` | File/directory | /etc/passwd |
| `TECHNIQUE` | Attack method | Groovy injection |

## Edge Types

| Edge | Meaning | Example |
|------|---------|---------|
| `RUNS_ON` | Service on host | nginx → host |
| `LISTENS_ON` | Service on port | nginx → 80/tcp |
| `VULNERABLE_TO` | Service has vuln | XWiki → CVE-2025-24893 |
| `YIELDS` | Exploit gives access | CVE → shell |
| `AUTHENTICATES` | Creds work on service | admin:pass → SSH |
| `CONTAINS` | File has data | .ssh/id_rsa → credential |
| `ACCESSES` | Shell can reach path | shell → /etc/passwd |

## Weight Calculation

Priority score formula:

```
priority = (severity × 0.4) + (confidence × 0.3) + (centrality × 0.2) + (freshness × 0.1)
```

Where:
- **severity** (0-10): Impact/CVSS score
- **confidence** (0-10): Likelihood of success
- **centrality** (0-10): Number of edges (auto-calculated)
- **freshness** (0-10): Recently discovered = higher priority (decays over time)

## Helper Functions

```python
from lib.attack_graph import cvss_to_score, confidence_to_score

# Convert severity string to score
score = cvss_to_score("critical")  # returns 10.0

# Convert confidence string to score
conf = confidence_to_score("high")  # returns 9.0
```

## File Format

The graph is stored as JSON:

```json
{
  "target": "10.10.11.80",
  "challenge": "editor",
  "created": "2026-01-02T08:30:00",
  "last_updated": "2026-01-02T09:15:00",
  "nodes": [
    {
      "id": "service-001",
      "type": "SERVICE",
      "label": "XWiki 15.10.8",
      "properties": {"port": 8080},
      "weight": {"severity": 8.0, "confidence": 7.0, "centrality": 2, "freshness": 10.0},
      "state": "discovered",
      "investigated": false
    }
  ],
  "edges": [
    {
      "id": "edge-001",
      "type": "VULNERABLE_TO",
      "source": "service-001",
      "target": "vuln-001",
      "weight": {"probability": 0.95, "effort": 2}
    }
  ],
  "frontier": {
    "unexplored": ["vuln-001"],
    "next_targets": [
      {
        "node_id": "vuln-001",
        "priority_score": 7.8,
        "reason": "Untested critical vulnerability"
      }
    ]
  }
}
```

## API Reference

See docstrings in `attack_graph.py` for complete API documentation:

```bash
python3 -c "from lib.attack_graph import AttackGraph; help(AttackGraph)"
```

## Examples

See `lib/examples/` directory:
- `graph_example.py` - Complete workflow demonstration
- (more examples to come)

## Migration from Flat JSON

If you have existing `services.json` and `vulns.json`:

```bash
# Migrate to graph format
python3 lib/migrate_to_graph.py htb-targets/editor

# Output: htb-targets/editor/attack-graph.json
```

## Development

### Running Tests

```bash
# Run example (serves as integration test)
python3 lib/examples/graph_example.py

# Test migration
python3 lib/migrate_to_graph.py htb-targets/editor
```

### Adding New Node/Edge Types

Edit enums in `attack_graph.py`:

```python
class NodeType(str, Enum):
    # Add new type
    CONTAINER = "CONTAINER"

class EdgeType(str, Enum):
    # Add new relationship
    HOSTS = "HOSTS"
```

## Future Enhancements

Potential additions:
- NetworkX integration for advanced pathfinding
- SQLite backend for complex queries
- Real-time TUI visualization
- Attack chain recommendations based on historical success
- Multi-target graphs for pivot scenarios

## References

- Research doc: `thoughts/shared/research/2026-01-02-graph-based-pentesting-tracker.md`
- FlowCoder guide: `flowcoder/FLOWCODER_CHART_GUIDE.md`
