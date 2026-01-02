# HTB Autopwn - Usage Examples

All workflows now accept a **single string argument** that Claude parses to extract target info and initialize the attack graph.

---

## Basic Usage

### Simple: IP + Name
```bash
flowcoder htb-autopwn-hybrid "10.10.11.80 editor"
```

Claude extracts:
- Target: `10.10.11.80`
- Challenge: `editor`
- Initializes graph with HOST node

---

## Advanced Usage

### With Context Notes
```bash
flowcoder htb-autopwn-hybrid "10.10.11.80 editor - XWiki 15.10.8 suspected"
```

Claude extracts:
- Target: `10.10.11.80`
- Challenge: `editor`
- Context: `XWiki 15.10.8 suspected`
- Initializes graph with HOST + suspected SERVICE node (low confidence)

### Structured Format
```bash
flowcoder htb-autopwn-hybrid "target: 10.10.11.80, challenge: editor, notes: web app on port 8080"
```

Claude extracts:
- Target: `10.10.11.80`
- Challenge: `editor`
- Context: `web app on port 8080`
- Initializes graph with HOST + PORT nodes

### Rich Context
```bash
flowcoder htb-autopwn-hybrid "editor box at 10.10.11.80, seems to be running XWiki based on robots.txt, port 8080 open"
```

Claude extracts:
- Target: `10.10.11.80`
- Challenge: `editor`
- Context: Full notes about XWiki and port 8080
- Initializes graph with HOST, SERVICE (XWiki), PORT (8080) nodes

---

## What Happens

### 1. Parse Phase
FlowCoder block: `PARSE TARGET INFO`

Claude reads the string and extracts:
```python
{
  "targetIp": "10.10.11.80",
  "challengeName": "editor",
  "contextNotes": "XWiki 15.10.8 suspected",
  "graphInitialized": true
}
```

### 2. Graph Initialization
```python
from lib.attack_graph import AttackGraph, NodeType

graph = AttackGraph(target="10.10.11.80", challenge="editor")

# Always add host
host_id = graph.add_node(NodeType.HOST, label="10.10.11.80")

# If context mentions services/vulns, add as low-confidence nodes
if "XWiki" in context:
    service_id = graph.add_node(
        NodeType.SERVICE,
        label="XWiki 15.10.8",
        weight={"severity": 5, "confidence": 3, "centrality": 0, "freshness": 10}
    )
    graph.add_edge(EdgeType.RUNS_ON, service_id, host_id)

graph.save('htb-targets/editor/attack-graph.json')
```

### 3. Autopwn Execution
Claude-guided workflow loads the graph and proceeds with:
- Recon (confirm/update suspected services)
- Research (find vulns)
- Exploitation (use graph frontier)
- Post-exploit (expand graph)

---

## Example Session

```bash
$ flowcoder htb-autopwn-hybrid "10.10.11.80 editor - suspected XWiki, port 8080"

[PARSE TARGET INFO]
✓ Extracted: 10.10.11.80, editor
✓ Context: suspected XWiki, port 8080
✓ Graph initialized with 3 nodes (HOST, SERVICE, PORT)

[RUN AUTOPWN GUIDED - Attempt 1]
✓ Loading graph...
✓ Frontier: SERVICE(XWiki) - score 5.0
✓ Running recon to confirm XWiki...
✓ Confirmed: XWiki 15.10.8 on port 8080
✓ Updated graph (confidence: 3 → 9)
✓ Researching vulnerabilities...
✓ Found: CVE-2025-24893 (CVSS 9.8)
✓ Generating exploit...
✓ Exploiting...
✓ SUCCESS! Shell obtained as www-data
✓ Flags captured

[FINAL REPORT]
✓ Session complete in 1 attempt
✓ Report saved to htb-targets/editor/REPORT.md
✓ Graph saved with 12 nodes, 15 edges
```

---

## Comparison

### Old Way (Multiple Args)
```bash
flowcoder htb-autopwn 10.10.11.80 editor
# Only passes IP and name
# No context, no initial graph seeding
```

### New Way (Single String)
```bash
flowcoder htb-autopwn-hybrid "10.10.11.80 editor - XWiki suspected"
# Passes everything in one string
# Claude extracts what's needed
# Initializes graph with context
# More flexible and natural
```

---

## Graph Benefits

The initial graph from parsed context gives you:

**Before recon even starts:**
```json
{
  "nodes": [
    {"id": "host-001", "type": "HOST", "label": "10.10.11.80"},
    {"id": "service-001", "type": "SERVICE", "label": "XWiki", "confidence": 3},
    {"id": "port-001", "type": "PORT", "label": "8080/tcp"}
  ],
  "edges": [
    {"type": "RUNS_ON", "source": "service-001", "target": "host-001"},
    {"type": "LISTENS_ON", "source": "service-001", "target": "port-001"}
  ]
}
```

**Recon confirms and updates:**
- Increases confidence: 3 → 9
- Adds version: "XWiki" → "XWiki 15.10.8"
- Adds more discovered services

**Research adds:**
- VULN nodes linked to services
- Priority scores for targeting

**Exploitation expands:**
- SHELL nodes when exploited
- CREDENTIAL nodes when found
- PATH nodes during enumeration

---

## Tips

### Be Natural
```bash
# All of these work:
"10.10.11.80 editor"
"editor at 10.10.11.80"
"target: 10.10.11.80, box: editor"
"10.10.11.80 (editor) - web app"
```

### Include Context
```bash
# More context = better initial graph
"10.10.11.80 editor - XWiki 15.10.8, port 8080, looks vulnerable to CVE-2025-24893"
```
Claude will seed the graph with XWiki service and suspected CVE!

### Resume Sessions
```bash
# Same command works for resume
flowcoder htb-autopwn-hybrid "10.10.11.80 editor"
# Claude checks for existing graph and session-log.md
# Resumes from where you left off
```

---

## Summary

**Single string argument** = Simpler + More flexible + Graph initialization

Claude handles:
- ✅ Parsing natural language input
- ✅ Extracting target IP and challenge name
- ✅ Understanding context notes
- ✅ Initializing attack graph with suspected info
- ✅ Starting with intelligent priors

You provide:
- 🎯 Target info in whatever format is natural
- 🎯 Any context you already know
- 🎯 Let Claude figure out the details
