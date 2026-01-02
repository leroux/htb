# HTB Autopwn Hybrid - Review & Analysis

## ✅ Strengths

### 1. **Clean Flow Structure**
```
START → PARSE → INIT → GUIDED (loop) → CHECK → REPORT → END
                          ↑______________|
```
Well-organized, easy to understand.

### 2. **Single String Argument**
- Flexible input format
- Claude extracts what's needed
- Natural language friendly

### 3. **Graph Initialization**
- Seeds graph with context from parse
- Low confidence nodes for suspected items
- Recon confirms/updates

### 4. **Hybrid Approach**
- FlowCoder: Loop control (max 3)
- Claude: Intelligence & adaptation
- Best of both worlds

---

## ⚠️ Issues Found

### 1. **Position Conflict** (Line 71)
```json
"increment-001": {
  "position": {"x": 200, "y": 350}  // ❌ Same as guided-001
}
```

**Fix:** Should be `y: 450` or similar to avoid overlap.

### 2. **Variable Arithmetic** (Line 73)
```json
"variable_value": "{{attemptNumber}} + 1"
```

**Issue:** FlowCoder might not support arithmetic in variable values.

**Possible solutions:**
- Check if FlowCoder evaluates expressions
- Or use a PROMPT block to increment (less clean)
- Or hardcode attempt numbers in loop iterations

### 3. **Branch Condition Syntax** (Line 81)
```json
"condition": "success || attemptNumber >= 3"
```

**Question:** Does FlowCoder support:
- Logical OR (`||`)
- Comparison operators (`>=`)
- Compound conditions

Need to verify FlowCoder's condition syntax capabilities.

### 4. **Skill Invocation in PROMPT** (Line 54)
```json
"prompt": "... Invoke the skill: /htb-autopwn-guided \"{{targetIp}} {{challengeName}}\"\n\n..."
```

**Issue:** Unclear execution model. In a PROMPT block:
- Is Claude SDK executing the skill directly?
- Should this be a BASH block instead?
- Or is the PROMPT asking Claude to invoke it?

**Recommendation:** Be more explicit about execution.

### 5. **Missing EdgeType Import** (Line 27)
```python
from lib.attack_graph import AttackGraph, NodeType
# Missing: EdgeType (needed if adding edges)
```

If parse block adds edges for context, needs `EdgeType`.

---

## 🔧 Suggested Fixes

### Fix 1: Position Conflict
```json
"increment-001": {
  "position": {"x": 200, "y": 450}  // ✅ After guided, before check
}
```

### Fix 2: Variable Increment
**Option A: If FlowCoder supports expressions (test first)**
```json
"variable_value": "{{attemptNumber}} + 1"  // Keep as-is
```

**Option B: If not, use PROMPT block**
```json
{
  "type": "prompt",
  "name": "INCREMENT",
  "prompt": "Increment attempt counter. Current: {{attemptNumber}}. Return current + 1.",
  "output_schema": {
    "type": "object",
    "properties": {
      "attemptNumber": {"type": "integer"}
    }
  }
}
```

### Fix 3: Branch Condition
**Test first, then simplify if needed:**
```json
// Current (might work):
"condition": "success || attemptNumber >= 3"

// Fallback if OR doesn't work:
"condition": "continueLoop"  // Have guided-001 return this
```

### Fix 4: Skill Invocation
**Make it explicit - use BASH block instead:**
```json
{
  "id": "guided-001",
  "type": "bash",
  "name": "RUN AUTOPWN GUIDED",
  "command": "claude /htb-autopwn-guided \"{{targetIp}} {{challengeName}}\"",
  "capture_output": true,
  "output_variable": "autopwnResult"
}
```

Then add parse block after to extract structured output.

**OR keep PROMPT but clarify:**
```json
"prompt": "You are executing within FlowCoder. Invoke the Claude Code skill by running it as if you were in a terminal.\n\nCommand to execute:\n/htb-autopwn-guided \"{{targetIp}} {{challengeName}}\"\n\n..."
```

### Fix 5: Import EdgeType
```python
from lib.attack_graph import AttackGraph, NodeType, EdgeType
```

---

## 🧪 Testing Checklist

### Syntax Tests
- [ ] Validate JSON: `python3 -c "import json; json.load(open('...'))"`
- [ ] Check all block IDs are unique
- [ ] Check all connections reference valid block IDs
- [ ] Verify no position overlaps

### Execution Tests
- [ ] Test variable increment: Does `{{attemptNumber}} + 1` work?
- [ ] Test branch condition: Does `success || attemptNumber >= 3` work?
- [ ] Test skill invocation: Does calling `/htb-autopwn-guided` from PROMPT work?
- [ ] Test graph initialization: Does parse block create valid graph?

### Integration Tests
- [ ] Run with simple input: `"10.10.11.80 editor"`
- [ ] Run with context: `"10.10.11.80 editor - XWiki suspected"`
- [ ] Verify loop behavior: Does it stop at success?
- [ ] Verify loop limit: Does it stop at 3 attempts?

---

## 🎯 Flow Logic Analysis

### Current Loop Logic
```
attempt = 0
do {
  attempt++
  run_autopwn()
  if (success || attempt >= 3) break
} while (true)
```

**Issue:** Counter increments AFTER run, so first run is attempt 1, but counter shows 0 during first run.

**Fix:** Initialize to 1 instead of 0, or move increment before guided block:
```
START → PARSE → [Set attempt=1] → GUIDED → CHECK → INCREMENT → LOOP
                                     ↑________________|
```

Or accept that attempt tracking is off-by-one (not critical).

---

## 📊 Variable Flow

### Variables Created
1. **parse-001 outputs:**
   - `targetIp`
   - `challengeName`
   - `contextNotes`
   - `graphInitialized`

2. **init-001 sets:**
   - `attemptNumber = 0`

3. **guided-001 outputs:**
   - `success`
   - `userFlag`
   - `rootFlag`
   - `summary`

4. **increment-001 sets:**
   - `attemptNumber = attemptNumber + 1`

### Variable Usage
- `{{targetIp}}` - Used in guided-001, report-001 ✅
- `{{challengeName}}` - Used in guided-001, report-001 ✅
- `{{contextNotes}}` - Used in guided-001 ✅
- `{{attemptNumber}}` - Used in increment-001, check-001, report-001 ✅
- `{{success}}` - Used in check-001, report-001 ✅
- `{{userFlag}}` - Used in report-001 ✅
- `{{rootFlag}}` - Used in report-001 ✅

All variable usage looks correct! ✅

---

## 🏗️ Recommended Changes

### Priority 1: Fix Position Conflict
```diff
"increment-001": {
-  "position": {"x": 200, "y": 350}
+  "position": {"x": 200, "y": 450}
}
```

### Priority 2: Clarify Skill Invocation
Either change to BASH block or clarify PROMPT instructions.

### Priority 3: Test Variable Arithmetic
If `{{attemptNumber}} + 1` doesn't work, switch to PROMPT-based increment.

### Priority 4: Add EdgeType Import
```diff
-from lib.attack_graph import AttackGraph, NodeType
+from lib.attack_graph import AttackGraph, NodeType, EdgeType
```

---

## 🎨 Visual Flow (Current)

```
START (y=50)
  ↓
PARSE TARGET INFO (y=150)
  ↓
INIT COUNTER (y=250)
  ↓
RUN AUTOPWN GUIDED (y=350) ←────┐
  ↓                              │
INCREMENT (y=350) ⚠️ OVERLAP     │
  ↓                              │
CHECK: SUCCESS OR MAX? (y=450)  │
  ├─ TRUE → REPORT (y=550)       │
  └─ FALSE ──────────────────────┘
              ↓
            END (y=650)
```

### Fixed Visual Flow
```
START (y=50)
  ↓
PARSE TARGET INFO (y=150)
  ↓
INIT COUNTER (y=250)
  ↓
RUN AUTOPWN GUIDED (y=350) ←────┐
  ↓                              │
INCREMENT (y=450) ✅              │
  ↓                              │
CHECK: SUCCESS OR MAX? (y=550)  │
  ├─ TRUE → REPORT (y=650)       │
  └─ FALSE ──────────────────────┘
              ↓
            END (y=750)
```

---

## ✅ Overall Assessment

**Score: 8/10**

**Strengths:**
- ✅ Clean architecture
- ✅ Good separation of concerns
- ✅ Flexible input parsing
- ✅ Graph integration
- ✅ Proper variable flow

**Issues:**
- ⚠️ Position overlap (easy fix)
- ⚠️ Untested arithmetic in variables
- ⚠️ Unclear skill invocation model
- ⚠️ Missing import in example

**Verdict:** Solid design, needs minor fixes and testing to validate assumptions about FlowCoder capabilities.

---

## 🚀 Next Steps

1. **Fix position conflict** (5 min)
2. **Test variable arithmetic** in FlowCoder (10 min)
3. **Clarify skill invocation** - decide BASH vs PROMPT (15 min)
4. **Add EdgeType import** (1 min)
5. **Run integration test** (30 min)
6. **Document final behavior** (10 min)

Total: ~70 minutes to production-ready
