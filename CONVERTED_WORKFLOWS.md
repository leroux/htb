# Converted HTB Workflows

All HTB FlowCoder workflows have been converted to Claude-guided skills.

---

## Available Skills

### 1. `/htb-autopwn-guided` ⭐ Main Orchestrator
**File:** `.claude/commands/htb-autopwn-guided.md`
**Original:** `flowcoder/commands/htb-autopwn.json`
**Size:** 4.5K

**Usage:**
```bash
/htb-autopwn-guided <target-ip> <challenge-name>
```

**What it does:**
- Full end-to-end autopwn orchestration
- Checks existing state (resume capability)
- Calls recon and research workflows
- Autonomous exploitation loop
- Post-exploitation enumeration
- Flag capture

**Flowchart:**
```
START → SETUP → CHECK STATE → [RECON?] → RUN RECON → SAVE RECON →
[RESEARCH?] → RUN RESEARCH → EXPLOIT LOOP → [CONTINUE?] ↺ → POST EXPLOIT → END
```

**Autonomous decisions:**
- Skip recon if services.json exists
- Skip research if vulns.json exists
- Resume from session-log.md
- Dynamic exploit loop (stop on success)
- Intelligent post-exploitation

---

### 2. `/htb-recon-guided` 🔍 Reconnaissance
**File:** `.claude/commands/htb-recon-guided.md`
**Original:** `flowcoder/commands/htb-recon.json`
**Size:** 3.7K

**Usage:**
```bash
/htb-recon-guided <target-ip>
```

**What it does:**
- Port scanning (rustscan/nmap)
- Service enumeration per protocol:
  - Web (gobuster, curl)
  - SMB (smbclient, enum4linux)
  - FTP (anonymous access check)
- Saves services.json

**Flowchart:**
```
START → RUSTSCAN → [HAS WEB?] → WEB ENUM → [HAS SMB?] → SMB ENUM →
[HAS FTP?] → FTP ENUM → SAVE SERVICES → END
```

**Autonomous decisions:**
- Skip protocol-specific enum if service not found
- Fallback to nmap if rustscan unavailable
- Deep vs shallow enumeration based on findings
- Stop early if critical vuln discovered

---

### 3. `/htb-research-guided` 📚 Vulnerability Research
**File:** `.claude/commands/htb-research-guided.md`
**Original:** `flowcoder/commands/htb-research.json`
**Size:** 1.3K

**Usage:**
```bash
/htb-research-guided <target-ip>
```

**What it does:**
- Reads services.json
- CVE lookup for each service
- Exploit-db and GitHub POC search
- Prioritizes by severity + confidence
- Saves vulns.json

**Flowchart:**
```
START → READ SERVICES → CVE RESEARCH → WRITE VULNS → END
```

**Autonomous decisions:**
- Focus on services with version info
- Deep search for critical services
- Stop searching if high-confidence RCE found
- Adjust thoroughness based on findings

---

## Comparison: FlowCoder vs Claude-Guided

### FlowCoder (Rigid)
```bash
flowcoder htb-autopwn 10.10.11.80 editor
```

**Behavior:**
- ❌ Always runs full recon (even if done before)
- ❌ Always runs all enumeration steps
- ❌ Exactly 5 exploit attempts (even if #1 succeeds)
- ❌ Cannot debug failing exploits
- ❌ Fixed execution order
- ✅ Structured output validation
- ✅ Loop counting enforcement

### Claude-Guided (Intelligent)
```bash
/htb-autopwn-guided 10.10.11.80 editor
```

**Behavior:**
- ✅ Checks state, skips completed work
- ✅ Adaptive enumeration (skip if not needed)
- ✅ Stops on first successful exploit
- ✅ Debugs and retries failing exploits
- ✅ Context-aware flow decisions
- ✅ Efficient (skips unnecessary work)
- ⚠️ No rigid schema enforcement (more flexible)

---

## Usage Examples

### Quick Start (Full Autopwn)
```bash
/htb-autopwn-guided 10.10.11.80 editor
```
I'll orchestrate everything: recon → research → exploit → flags

### Recon Only
```bash
/htb-recon-guided 10.10.11.80
```
Scans and enumerates services, saves to services.json

### Research Only (After Recon)
```bash
cd htb-targets/editor
/htb-research-guided 10.10.11.80
```
Reads services.json, researches vulns, saves to vulns.json

### Resume Existing Session
```bash
/htb-autopwn-guided 10.10.11.80 editor
```
I'll detect existing work and resume from where you left off

---

## Integration with Graph

All skills can use the attack graph:

```markdown
# In any skill prompt, I can:

from lib.attack_graph import AttackGraph
graph = AttackGraph.load('htb-targets/editor/attack-graph.json')
frontier = graph.get_frontier(limit=5)

# Then make intelligent decisions based on graph state
```

---

## When to Use FlowCoder vs Skills

### Use FlowCoder When:
- Need strict loop limits (exactly N attempts)
- Need JSON schema validation
- Need audit trail with block-level logging
- Need visual workflow editing

### Use Claude Skills When: (Most of the time!)
- Want intelligent adaptation
- Need debugging capability
- Want efficiency (skip unnecessary work)
- Want context-aware decisions
- Want natural language workflows

### Hybrid Approach:
Use Claude skills as main orchestrator, call FlowCoder for validation:

```markdown
## In htb-autopwn-guided.md

For strict 5-attempt limiting, invoke FlowCoder:
```bash
flowcoder htb-exploit-loop $TARGET $CHALLENGE
```

Then resume autonomous execution.
```

---

## File Locations

**Claude Skills:**
```
.claude/commands/
├── htb-autopwn-guided.md    ⭐ Main entry point
├── htb-recon-guided.md       🔍 Recon phase
└── htb-research-guided.md    📚 Research phase
```

**FlowCoder Workflows (Still available):**
```
flowcoder/commands/
├── htb-autopwn.json          (Original rigid version)
├── htb-recon.json            (Original rigid version)
└── htb-research.json         (Original rigid version)
```

**Supporting Libraries:**
```
lib/
├── attack_graph.py           🎯 Graph-based tracking
├── flowcoder_to_skill.py     🔧 Translator tool
└── migrate_to_graph.py       📊 JSON → Graph converter
```

---

## Next Steps

1. **Try the main workflow:**
   ```bash
   /htb-autopwn-guided 10.10.11.80 editor
   ```

2. **Use graph tracking:**
   ```bash
   python3 lib/migrate_to_graph.py htb-targets/editor
   ```

3. **Let me orchestrate intelligently:**
   - I'll check existing state
   - Skip completed work
   - Make smart decisions
   - Debug and iterate
   - Capture flags efficiently

4. **Fall back to FlowCoder when needed:**
   ```bash
   # For strict validation
   flowcoder htb-exploit-loop 10.10.11.80 editor
   ```

---

## Summary

✅ **All HTB workflows converted**
✅ **Claude-guided skills ready to use**
✅ **Graph integration available**
✅ **FlowCoder still available for validation**

**Your vision implemented:** Flowcharts as guides, Claude as orchestrator! 🎯
