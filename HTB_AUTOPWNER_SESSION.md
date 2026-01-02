# HTB Autopwner - Session Context

**Date**: 2025-01-02
**Status**: Research/Design Phase

---

## Project Goal

Build a system that learns common techniques for solving HackTheBox challenges. This is for educational purposes (paid HTB subscription).

**Key Requirements:**
- Initial steps are always recon (nmap, then dig into rest)
- May add MCP for AI browser use when necessary
- Python requests preferred over browser automation where possible
- Uses FlowCoder for workflow automation
- Uses Claude SDK for AI-powered decision making

---

## What We've Explored

### FlowCoder Codebase Understanding

FlowCoder is located at `/home/user/htb/flowcoder/`

**Architecture:**
- PyGame-based GUI for visual workflow design
- Python async controllers for execution
- JSON-based workflow storage in `/commands/`
- Supports Claude SDK and Codex SDK

**Key Files:**
- `src/services/claude_service.py` - Wraps `claude-agent-sdk`
- `src/services/codex_service.py` - Wraps OpenAI Codex
- `src/controllers/execution_controller.py` - Main orchestrator
- `src/models/blocks.py` - Block type definitions
- `commands/*.json` - Example workflows

### FlowCoder Block Types

1. **Start** - Entry point (required)
2. **End** - Completion marker
3. **Prompt** - Send prompt to Claude with optional JSON schema
4. **Branch** - Conditional routing (condition syntax: `field == value`, `field`, `!field`, etc.)
5. **Variable** - Set variables with type conversion
6. **Bash** - Execute shell commands, capture output/exit code
7. **Command** - Call another workflow (composition)
8. **Refresh** - Reset Claude session (clear context)

### Workflow JSON Structure

```json
{
  "id": "<uuid>",
  "name": "workflow-name",
  "description": "What it does",
  "arguments": [
    {"name": "target", "description": "Target IP", "required": true}
  ],
  "flowchart": {
    "start_block_id": "<uuid>",
    "blocks": { ... },
    "connections": [ ... ]
  }
}
```

### Variable Substitution
- `$1`, `$2`, etc. - Positional arguments
- `{{varname}}` - Named variables from previous blocks
- `$$` - Literal dollar sign

### Claude Skills (Slash Commands)

Located in `.claude/commands/` as Markdown files.

**Structure:**
```markdown
---
description: Brief description
allowed-tools: Read, Bash(git:*)
model: sonnet
argument-hint: [arg1] [arg2]
---

Prompt content with $1, $ARGUMENTS, @file references, !`bash commands`
```

**Key Features:**
- User-invoked via `/command-name`
- Can reference files with `@path`
- Inline bash with `!backtick` syntax
- Frontmatter for configuration

---

## Analysis: Skills vs FlowCoder

| Aspect | FlowCoder | Skills |
|--------|-----------|--------|
| **Execution** | Autonomous workflow engine | User-invoked commands |
| **State Machine** | Explicit branching, loops, variables | Linear prompt execution |
| **Session Control** | Full control (reset, multiple sessions) | Single session context |
| **Composition** | Workflows call other workflows | Commands are standalone |
| **Output Validation** | JSON schema enforcement | None |

### Recommendation: Use BOTH

**Skills for Interactive Mode:**
- `/htb-recon <target>` - Quick recon scan
- `/htb-enumerate <service>` - Dig into specific services
- `/htb-exploit <vuln>` - Try specific exploits

**FlowCoder for Autonomous Mode:**
- Full end-to-end autopwn workflow
- Handles decision trees
- Loops and retries
- State tracking

---

## Proposed Architecture

```
htb-autopwner/
├── .claude/
│   └── commands/           # Skills for interactive use
│       ├── htb-recon.md
│       ├── htb-web-enum.md
│       ├── htb-exploit.md
│       └── htb-privesc.md
├── flowcoder/
│   └── commands/           # Autonomous workflows
│       ├── htb-full-auto.json
│       ├── htb-recon-phase.json
│       └── htb-exploit-phase.json
└── lib/                    # Shared Python utilities
    ├── nmap_parser.py
    ├── exploit_db.py
    └── credential_store.py
```

---

## Open Questions (Need Your Input)

1. **Primary use case**: Autonomous "fire and forget" OR interactive human-in-the-loop?

2. **Learning system**: Should it:
   - Just execute known patterns?
   - Log/remember what worked for similar boxes?
   - Build a technique database over time?

3. **Scope of first version**:
   - Just recon phase (nmap → service enumeration → report)?
   - Full pipeline but only for one box type (e.g., Linux web boxes)?
   - Something else?

---

## Files Created This Session

1. `/home/user/htb/flowcoder/FLOWCODER_CHART_GUIDE.md` - Comprehensive guide to writing FlowCoder workflows

---

## Standard HTB Methodology (For Reference)

### Phase 1: Recon
- nmap service/version scan
- Directory enumeration (gobuster/feroxbuster)
- Subdomain enumeration
- Technology fingerprinting

### Phase 2: Enumeration
- Dig into discovered services (web, ssh, ftp, smb, etc.)
- Identify versions, potential CVEs
- Find credentials, config files, hidden endpoints

### Phase 3: Exploitation
- Exploit identified vulnerabilities
- Gain initial foothold
- Capture user flag

### Phase 4: Privilege Escalation
- Enumerate from inside (linpeas/winpeas)
- Find privesc vectors
- Root/Admin access
- Capture root flag

---

## Next Steps

1. Answer the open questions above
2. Design the workflow structure in detail
3. Create initial FlowCoder workflows for recon phase
4. Create corresponding skills for interactive use
5. Build shared Python utilities for parsing/state management

---

## How to Resume

To resume this session, read this file and the FlowCoder guide:
- `/home/user/htb/HTB_AUTOPWNER_SESSION.md` (this file)
- `/home/user/htb/flowcoder/FLOWCODER_CHART_GUIDE.md`

Then continue from "Next Steps" or answer the open questions to proceed.
