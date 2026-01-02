# Orchestration Architecture Guide

## Two Approaches to Workflow Automation

You have two ways to orchestrate HTB autopwn workflows:

1. **FlowCoder-Driven** (Rigid, Structured)
2. **Claude-Guided** (Flexible, Intelligent)

---

## Approach 1: FlowCoder-Driven

### Architecture

```
FlowCoder (orchestrator)
    ↓
  Flowchart (JSON)
    ↓
  PROMPT blocks → Claude SDK executes
    ↓
  BRANCH blocks → Fixed routing
    ↓
  Rigid flow control
```

### When to Use

✅ **Use FlowCoder when you need:**

1. **Strict Loop Limits**
   ```json
   "EXPLOIT LOOP" → attempt 1-5 times MAX → "CONTINUE?" branch
   ```

2. **Guaranteed Execution Order**
   - Must run recon before research before exploit
   - Dependencies between steps

3. **Output Validation**
   - Require specific JSON schema
   - Type-safe variable passing

4. **Visual Workflow Design**
   - Non-programmers designing workflows
   - Complex branching logic that benefits from visualization

5. **Audit Trail**
   - Every block execution logged
   - Replay capability

### Example: Strict Exploit Loop

```json
{
  "EXPLOIT LOOP": {
    "type": "prompt",
    "prompt": "Try exploit (attempt {{attemptNumber}}/5)..."
  },
  "INCREMENT": {
    "type": "variable",
    "variable_name": "attemptNumber",
    "variable_value": "{{attemptNumber}} + 1"
  },
  "CONTINUE?": {
    "type": "branch",
    "condition": "attemptNumber < 5 && !success"
  }
}
```

FlowCoder guarantees exactly 5 attempts, no more, no less.

### Limitations

❌ **FlowCoder struggles with:**
- Dynamic decision-making
- Backtracking/non-linear flow
- Debugging failed steps
- Adapting to unexpected situations
- Context-aware skipping

---

## Approach 2: Claude-Guided

### Architecture

```
Claude Code (orchestrator)
    ↓
  Skill with embedded flowchart
    ↓
  Claude reads flowchart as guide
    ↓
  Claude decides: skip, repeat, modify, backtrack
    ↓
  Intelligent context-aware execution
```

### When to Use

✅ **Use Claude-Guided when you need:**

1. **Intelligent Adaptation**
   - Skip unnecessary steps
   - Retry with modifications
   - Backtrack when stuck

2. **Context Awareness**
   - "If I find critical RCE in recon, skip other enumeration"
   - "If exploit needs debugging, fix and retry"

3. **Fuzzy Requirements**
   - "Get flags however you can"
   - "Try different approaches until something works"

4. **Real-time Problem Solving**
   - Missing dependencies → install them
   - Exploit needs tweaking → debug and fix
   - Path blocked → find alternate route

5. **Efficient Execution**
   - Don't waste time on low-value targets
   - Jump ahead when you find shortcuts

### Example: Autonomous Exploitation

```markdown
## Workflow (Guide, Not Rules)

1. Recon → Find services
2. Research → Find vulns
3. Exploit Loop → Try vectors
4. Post-exploit → Enum system

**Your decisions:**
- Found admin panel in step 1? Jump to step 3
- All exploits in step 3 failing? Back to step 2 for more research
- Exploit needs debugging? Fix it and retry
- Hit a dead end? Try alternate approach
```

Claude autonomously navigates based on results.

### Benefits

✅ **Claude-Guided excels at:**
- Adaptive problem-solving
- Efficiency (skipping useless work)
- Debugging and iteration
- Context-aware decisions
- Natural language workflows

---

## Hybrid Approach (Recommended)

Use **both** together strategically:

### Pattern: Claude-Guided with FlowCoder Checkpoints

```
Claude-Guided Workflow
    ↓
  [Most steps: autonomous]
    ↓
  Critical validation point
    ↓
  Call FlowCoder for strict loop
    ↓
  Back to Claude for next phase
```

### Example: HTB Autopwn Hybrid

**Main orchestration:** Claude skill (`/htb-autopwn-guided`)
- Recon phase (autonomous)
- Research phase (autonomous)
- Target selection (graph-based)

**Specific validation:** FlowCoder workflow
- Exploit loop with max 5 attempts
- Structured output schema
- Loop counter enforcement

```markdown
# htb-autopwn-guided.md

## Step 4: Exploitation

For strict attempt limiting, use FlowCoder:

```bash
flowcoder htb-exploit-loop $TARGET $CHALLENGE
```

Otherwise, handle exploitation autonomously with graph guidance.
```

---

## Converting FlowCoder → Claude Skills

### Translator Tool

```bash
python3 lib/flowcoder_to_skill.py flowcoder/commands/htb-recon.json
# Output: .claude/commands/htb-recon-guided.md
```

### What Gets Translated

**FlowCoder JSON:**
```json
{
  "blocks": {
    "recon-001": {"type": "prompt", "name": "SCAN TARGET", "prompt": "..."},
    "branch-001": {"type": "branch", "condition": "hasWeb"},
    "enum-001": {"type": "prompt", "name": "WEB ENUM", "prompt": "..."}
  }
}
```

**Claude Skill:**
```markdown
## Workflow Graph

START → [SCAN TARGET] → BRANCH(hasWeb) → [WEB ENUM] → END

## Step Details

### [SCAN TARGET]
Scan the target...
(Details from prompt)

### Your Decisions
- Skip web enum if no web service found
- Repeat scan if results unclear
```

---

## Decision Matrix

| Scenario | Use FlowCoder | Use Claude-Guided |
|----------|---------------|-------------------|
| Need exact loop count | ✅ Yes | ❌ No |
| Need JSON schema validation | ✅ Yes | ❌ No |
| Want adaptive flow | ❌ No | ✅ Yes |
| Complex debugging needed | ❌ No | ✅ Yes |
| Visual workflow design | ✅ Yes | ❌ No |
| Natural language tasks | ❌ No | ✅ Yes |
| Strict audit requirements | ✅ Yes | ⚠️ Partial |
| Efficiency critical | ❌ No | ✅ Yes |

---

## Migration Path

### Phase 1: Identify Workflow Type

For each workflow, ask:
1. Does it need strict validation? → Keep in FlowCoder
2. Does it need intelligence? → Convert to Claude skill
3. Both? → Hybrid approach

### Phase 2: Convert Appropriate Workflows

```bash
# Convert recon (mostly autonomous)
python3 lib/flowcoder_to_skill.py flowcoder/commands/htb-recon.json

# Convert autopwn (main orchestrator)
python3 lib/flowcoder_to_skill.py flowcoder/commands/htb-autopwn.json

# KEEP exploit-loop in FlowCoder (needs strict limits)
# → Called from Claude skill when needed
```

### Phase 3: Test Hybrid Approach

```bash
# Claude-guided main workflow
/htb-autopwn-guided 10.10.11.80 editor

# Claude decides when to invoke FlowCoder for validation
# Uses graph for intelligent target selection
# Adapts to findings in real-time
```

---

## Real-World Example

### Scenario: HTB Challenge "Editor"

**Old Way (Pure FlowCoder):**
```
htb-autopwn.json:
  START → SETUP → RECON → RESEARCH → EXPLOIT(×5 max) → POST → END

Result:
  - Runs all 5 exploit attempts even if #1 succeeds
  - Can't debug failing exploits
  - Can't skip unnecessary enumeration
```

**New Way (Claude-Guided + FlowCoder):**
```
/htb-autopwn-guided 10.10.11.80 editor

Claude decides:
  1. Run recon
  2. Found XWiki 15.10.8 → immediate research
  3. CVE-2025-24893 found → skip other enum
  4. Generate exploit
  5. Exploit needs fixing → debug
  6. SUCCESS on attempt 1 → skip remaining attempts
  7. Post-exploit enumeration
  8. Flags captured → DONE

Result:
  - 1 attempt instead of 5 (4x faster)
  - Auto-debugging
  - Skipped unnecessary work
  - Still maintains session log
```

---

## Graph Integration

Both approaches can use the attack graph:

### FlowCoder PROMPT Block

```json
{
  "prompt": "Load attack-graph.json, query frontier, exploit highest-priority node"
}
```

### Claude-Guided Skill

```markdown
## Step: Select Target

```python
from lib.attack_graph import AttackGraph
graph = AttackGraph.load('attack-graph.json')
frontier = graph.get_frontier(1)
# You decide what to do with the target
```
```

Same graph, different orchestration.

---

## Best Practices

### 1. Start with Claude-Guided

Default to Claude skills unless you specifically need FlowCoder features.

### 2. Use FlowCoder for Validation

Keep FlowCoder workflows for:
- Max attempt loops
- Schema validation
- Audit checkpoints

### 3. Document Decision Points

In Claude skills, explain **why** each step matters:

```markdown
### Step: Recon

**Decision point:**
- Skip if you already have service list
- Deep scan if initial scan inconclusive
- Stop early if critical vuln found
```

### 4. Leverage Graph Intelligence

Let the graph guide decisions:

```python
# Not: "try CVE-2025-24893"
# But: "query frontier, get highest priority, investigate that"
```

### 5. Log Decisions

Claude should document **why** it made choices:

```markdown
### [TIMESTAMP] SKIPPED WEB ENUM
Reason: Found critical RCE in initial scan, no need for deep enum
Saved: ~10 minutes of gobuster scans
```

---

## Summary

**FlowCoder:** Rigid state machine with guaranteed behavior
**Claude-Guided:** Intelligent agent with adaptive problem-solving

**Hybrid:** Use both where each excels:
- Claude for orchestration and intelligence
- FlowCoder for validation and limits
- Graph for shared state and decision-making

**Result:** Faster, smarter, more robust autopwn system.

---

## Quick Reference

### Create Claude-Guided Skill

```bash
# Convert existing workflow
python3 lib/flowcoder_to_skill.py flowcoder/commands/WORKFLOW.json

# Or write from scratch
nvim .claude/commands/my-workflow.md
```

### Run Claude-Guided Workflow

```bash
/my-workflow arg1 arg2
```

### Call FlowCoder from Claude Skill

```markdown
When you need strict validation, invoke FlowCoder:

```bash
flowcoder workflow-name args
```

Then resume autonomous execution.
```

### Use Graph in Both

```python
from lib.attack_graph import AttackGraph
graph = AttackGraph.load('attack-graph.json')
frontier = graph.get_frontier()
# FlowCoder or Claude can both use this
```

---

## Files Created

- `.claude/commands/htb-autopwn-guided.md` - Main autopwn skill (Claude-guided)
- `.claude/commands/htb-recon-guided.md` - Recon skill (auto-generated)
- `lib/flowcoder_to_skill.py` - Translation tool
- `ORCHESTRATION_GUIDE.md` - This document

## Next Steps

1. Run the guided skill: `/htb-autopwn-guided 10.10.11.80 editor`
2. Convert more workflows as needed
3. Keep FlowCoder for validation-critical tasks
4. Let Claude navigate intelligently
