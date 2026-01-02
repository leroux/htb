---
date: 2026-01-02T08:43:50-06:00
researcher: Claude
git_commit: fc493294a9c2cf8774368c2bb2d62762faeb3e52
branch: main
repository: htb
topic: "HTB Autopwn Workflow Design - Vulns/Vectors File & Exploitation Phase"
tags: [research, htb, autopwn, workflow, exploitation, recon]
status: complete
last_updated: 2026-01-02
last_updated_by: Claude
---

# Research: HTB Autopwn Workflow Design

**Date**: 2026-01-02T08:43:50-06:00
**Researcher**: Claude
**Git Commit**: fc493294a9c2cf8774368c2bb2d62762faeb3e52
**Branch**: main
**Repository**: htb

## Research Question

Design autopwn workflow where:
1. Recon writes possible vulns/vectors to a file
2. All progress and learnings logged to a file per autopwn session
3. After vulns/vectors identification, start exploitation phase
4. Use Python scripts for exploitation

## Summary

The current codebase has foundational FlowCoder workflows for recon (`htb-recon.json`) and a master workflow (`htb-autopwn.json`), but they lack:
- A structured vulns/vectors output file
- Comprehensive session logging
- An exploitation phase after recon
- Python exploit generation/execution capability

Below is the documented current state and the proposed design for the complete autopwn workflow.

---

## Current State

### Directory Structure

```
/home/user/htb/
├── .claude/commands/           # Claude Code skills (26 commands)
├── flowcoder/
│   └── commands/               # FlowCoder workflows
│       ├── htb-recon.json      # Recon workflow (exists)
│       └── htb-autopwn.json    # Master workflow (partial)
├── htb-targets/                # Per-target workspaces
│   └── editor/                 # Example: "editor" challenge
│       ├── scans/              # Scan outputs
│       └── notes/              # Session notes
├── workflow.md                 # Quick reference commands
└── HTB_AUTOPWNER_SESSION.md    # Project context document
```

### Existing Workflows

#### `htb-recon.json` (409 lines)
**Purpose:** Scan target and enumerate services

**Flow:**
```
START → RUSTSCAN RECON → HAS WEB? → WEB ENUM → HAS SMB? → SMB ENUM → HAS FTP? → FTP ENUM → GENERATE REPORT → END
```

**Output Schema (from RUSTSCAN RECON):**
```json
{
  "services": [{"port": int, "service": str, "version": str}],
  "hasWeb": bool,
  "hasSMB": bool,
  "hasSSH": bool,
  "hasFTP": bool,
  "potentialVectors": [string]
}
```

**Current Limitations:**
- `potentialVectors` is output but NOT written to a dedicated file
- No CVE lookup or exploit-db searching
- No confidence scoring for vectors

#### `htb-autopwn.json` (129 lines)
**Purpose:** Master workflow orchestrating the full attack chain

**Current Flow:**
```
START → SETUP WORKSPACE → RUN RECON (htb-recon) → SAVE RECON → END
```

**What's Missing:**
- No vulns.md or vectors.md file output
- No exploitation phase
- No session logging beyond basic notes
- No Python exploit generation

### What Recon Discovered

From `htb-targets/editor/notes/web-enumeration.md:136-179`:

**CVE-2025-24893: XWiki Unauthenticated RCE**
- Severity: CRITICAL (CVSS 9.8)
- Target: XWiki 15.10.8 on port 8080
- Attack: Groovy code injection via SolrSearch macro
- Auth required: None
- Public POCs: Available on GitHub and Exploit-DB

This is what the recon phase discovered and wrote to the notes - this is what should drive exploitation.

---

## Proposed Design

### 1. Vulns/Vectors File Structure

**Location:** `htb-targets/{challenge}/vulns.json`

```json
{
  "target": "10.10.11.80",
  "challenge": "editor",
  "scan_timestamp": "2026-01-02T08:30:00",
  "vectors": [
    {
      "id": "vec-001",
      "type": "cve",
      "name": "CVE-2025-24893",
      "service": "XWiki 15.10.8",
      "port": 8080,
      "severity": "critical",
      "confidence": "high",
      "description": "Unauthenticated RCE via SolrSearch Groovy injection",
      "references": [
        "https://github.com/dollarboysushil/CVE-2025-24893",
        "https://exploit-db.com/exploits/52136"
      ],
      "exploit_available": true,
      "tested": false,
      "result": null
    },
    {
      "id": "vec-002",
      "type": "misconfiguration",
      "name": "WebDAV Methods Enabled",
      "service": "Jetty/XWiki",
      "port": 8080,
      "severity": "medium",
      "confidence": "medium",
      "description": "PROPFIND, LOCK, UNLOCK methods may allow file manipulation",
      "references": [],
      "exploit_available": false,
      "tested": false,
      "result": null
    }
  ]
}
```

### 2. Session Log Structure

**Location:** `htb-targets/{challenge}/session-log.md`

```markdown
# HTB Session Log: {challenge}

## Target Information
- IP: {target}
- Challenge: {challenge}
- Started: {timestamp}

## Progress Log

### [2026-01-02 08:32:08] SETUP WORKSPACE
- Created directory structure
- Initialized session files

### [2026-01-02 08:33:17] NMAP RECON
- Discovered ports: 22, 80, 8080
- Services: SSH, nginx, Jetty/XWiki
- Finding: XWiki 15.10.8 detected

### [2026-01-02 08:39:06] WEB ENUM
- Port 80: SimplistCode Pro (React SPA)
- Port 8080: XWiki wiki application
- CVE-2025-24893 identified (CRITICAL)

### [2026-01-02 08:45:00] EXPLOITATION ATTEMPT
- Vector: CVE-2025-24893
- Script: exploits/cve-2025-24893.py
- Result: SUCCESS - reverse shell obtained
- User: www-data

## Learnings
- XWiki 15.x before 15.10.11 vulnerable to Groovy injection
- SolrSearch endpoint doesn't require authentication
```

### 3. Exploitation Phase Workflow

Add to `htb-autopwn.json` after SAVE RECON:

```
SAVE RECON → EXPLOIT LOOP → SUCCESS? → POST EXPLOIT → END
                   ↑_____________|
                      (max 5 attempts)
```

**Single PROMPT Block: EXPLOIT LOOP**

Claude SDK handles everything:
- Read vulns.json
- Select highest priority untested vector
- Research CVE/POC details
- Generate Python exploit script
- Execute exploit
- Analyze result
- Update vulns.json (mark tested)
- Log to session-log.md
- Decide: success? try next? give up?

**Output Schema:**
```json
{
  "exploitSuccess": boolean,
  "flagCaptured": boolean,
  "shellObtained": boolean,
  "attemptNumber": integer,
  "continueLoop": boolean
}
```

Claude decides when to stop via `continueLoop` field.

### 4. Claude SDK-Driven Exploitation

**All decisions made by Claude via PROMPT blocks:**

```
PROMPT: "EXPLOIT LOOP"

  Claude actions:
  1. Read vulns.json to find untested vector
  2. If no vectors or max attempts reached → return continueLoop: false
  3. Research the CVE and find POC details
  4. Write Python exploit to htb-targets/{challenge}/exploits/
  5. Execute: python3 exploit.py
  6. Analyze output for success indicators
  7. Update vulns.json with result
  8. Append to session-log.md
  9. Return structured output with continueLoop decision
```

**No BASH blocks** - Claude uses Bash tool within the PROMPT execution context.

**No manual workflow steps** - Claude decides everything autonomously.

### 5. Required Workflow Changes

#### A. Update `htb-recon.json`

Modify **GENERATE REPORT** block to also write vulns.json:

```json
{
  "id": "report-001",
  "type": "prompt",
  "name": "GENERATE REPORT",
  "prompt": "Generate comprehensive recon report and vulns file for $1 ($2).\n\nSummarize findings:\n- Services: {{services}}\n- Potential vectors: {{potentialVectors}}\n- Web findings: {{webFindings}}\n- SMB findings: {{smbFindings}}\n- FTP findings: {{ftpFindings}}\n\nTasks:\n1. Write detailed report to ./htb-targets/$2/scans/recon-summary.md\n2. For each potential vector, research CVEs and public exploits\n3. Write prioritized vulns.json to ./htb-targets/$2/vulns.json with structure:\n   - target, challenge, scan_timestamp\n   - vectors array with: id, type, name, severity, confidence, service, port, description, exploit_available, tested=false\n4. Update session notes\n\nProvide summary.",
  "output_schema": {
    "type": "object",
    "properties": {
      "vulnsWritten": {"type": "boolean"},
      "vectorCount": {"type": "integer"},
      "topVector": {"type": "string"}
    },
    "required": ["vulnsWritten", "vectorCount", "topVector"]
  }
}
```

#### B. Update `htb-autopwn.json`

Add exploitation phase - single PROMPT block with loop:

```json
{
  "id": "exploit-loop-001",
  "type": "prompt",
  "name": "EXPLOIT LOOP",
  "prompt": "Exploitation phase for $1 ($2).\n\nYou have up to 5 attempts to exploit the target.\n\nFor each attempt:\n1. Read ./htb-targets/$2/vulns.json\n2. Select highest priority untested vector (critical>high>medium>low, then confidence)\n3. Research the CVE/vulnerability and find public POCs\n4. Generate Python exploit script in ./htb-targets/$2/exploits/\n5. Run the exploit: python3 exploit.py\n6. Analyze output for success (shell obtained? flag found?)\n7. Update vulns.json marking vector as tested with result\n8. Log attempt to ./htb-targets/$2/session-log.md\n9. If successful OR max attempts reached: set continueLoop=false\n10. Otherwise try next vector\n\nBe autonomous - make all decisions yourself.",
  "output_schema": {
    "type": "object",
    "properties": {
      "exploitSuccess": {"type": "boolean"},
      "flagCaptured": {"type": "boolean"},
      "shellObtained": {"type": "boolean"},
      "attemptNumber": {"type": "integer"},
      "continueLoop": {"type": "boolean"},
      "summary": {"type": "string"}
    },
    "required": ["exploitSuccess", "attemptNumber", "continueLoop", "summary"]
  }
}
```

Add BRANCH and loop back:

```json
{
  "id": "branch-continue-001",
  "type": "branch",
  "name": "CONTINUE?",
  "condition": "continueLoop"
}
```

True path loops back to EXPLOIT LOOP, false path goes to END.

### 6. FlowCoder Architecture

**ONLY use PROMPT blocks** - no BASH blocks in workflows.

**Flow:**
```
START → PROMPT (setup) → PROMPT (recon) → PROMPT (exploit loop) → BRANCH (continue?) → END
                                                                        ↑_______________|
```

Claude SDK (via PROMPT blocks) handles:
- All file I/O (Read, Write, Edit tools)
- All command execution (Bash tool)
- All decision making
- Loop control via output_schema

FlowCoder handles:
- High-level orchestration
- Passing variables between phases
- Loop branching based on continueLoop boolean

---

## Code References

- `flowcoder/commands/htb-recon.json:1-409` - Current recon workflow
- `flowcoder/commands/htb-autopwn.json:1-129` - Current master workflow
- `htb-targets/editor/notes/web-enumeration.md:136-179` - CVE documentation example (what recon discovered)
- `htb-targets/editor/notes/session.md:54-81` - Potential attack vectors list
- `flowcoder/FLOWCODER_CHART_GUIDE.md:1-547` - Workflow authoring guide

---

## Architecture Documentation

### Workflow Composition Pattern
```
htb-autopwn (master - FlowCoder orchestration)
  ├── PROMPT: SETUP (Claude SDK)
  ├── PROMPT: RECON (Claude SDK)
  │     └── writes vulns.json
  ├── PROMPT: EXPLOIT LOOP (Claude SDK, up to 5 iterations)
  │     ├── reads vulns.json
  │     ├── generates Python exploits
  │     ├── executes and logs results
  │     └── returns continueLoop boolean
  └── BRANCH: continueLoop? → loop or end
```

### Data Flow
```
FlowCoder START
    ↓
Claude SDK: Do recon, write vulns.json
    ↓
FlowCoder: Pass to exploit phase
    ↓
Claude SDK: Read vulns, exploit, log, decide to continue
    ↓
FlowCoder: Branch on continueLoop
    ↓
Loop or END
```

### Separation of Concerns
- **FlowCoder**: State machine, variable passing, loop control
- **Claude SDK**: All intelligence, file ops, command execution, decisions

### File Outputs Per Challenge
```
htb-targets/{challenge}/
├── vulns.json              # Prioritized attack vectors
├── session-log.md          # Timestamped progress log
├── scans/                  # Raw scan outputs
├── exploits/               # Generated Python scripts
├── loot/                   # Captured credentials, files
└── notes/                  # Manual notes, session.md
```

---

## Implementation Decisions

1. **Exploit execution mode:** Automatic - scripts should attempt to capture flags without human interaction

2. **Vector loop:** Maximum 5 attempts before stopping

3. **Exploit generation:** Generate fresh each time based on CVE/vector details - no pre-built templates

4. **Shell handling:** Claude SDK runs Python exploits via Bash tool - exploits handle TTY/pwntools

5. **FlowCoder blocks:** ONLY PROMPT blocks - never BASH blocks. Let Claude SDK decide when/how to execute commands.

6. **Decision making:** Claude SDK autonomous - FlowCoder just orchestrates phases and loops based on boolean outputs
