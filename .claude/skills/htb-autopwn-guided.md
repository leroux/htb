---
description: Master HTB workflow - orchestrates full attack chain from recon to root
allowed-tools: "*"
model: sonnet
argument-hint: <target> <challenge>
---

# Htb Autopwn

## Arguments

- **$2 (target)**: Target IP address (required)
- **$3 (challenge)**: Challenge/box name (e.g., 'editor', 'lame') (required)


## Workflow Graph (Reference)

```
START
  ↓
[PROMPT] SETUP WORKSPACE
  ↓
[PROMPT] CHECK STATE
  ↓
[REFRESH] REFRESH STATE
  ↓
BRANCH: NEEDS RECON? (needsRecon)
  ├─ TRUE →
  [COMMAND] RUN RECON
    ↓
  [PROMPT] SAVE RECON
    ↓
  [REFRESH] REFRESH STATE
    ↓
  BRANCH: NEEDS RESEARCH? (needsResearch)
    ├─ TRUE →
    [COMMAND] RUN RESEARCH
      ↓
    [PROMPT] EXPLOIT LOOP
      ↓
    [REFRESH] REFRESH STATE
      ↓
    BRANCH: CONTINUE? (continueLoop)
      ├─ TRUE →
      ↑ (loop back)
      └─ FALSE →
      [PROMPT] POST EXPLOIT
        ↓
      END
    └─ FALSE →
    ↑ (loop back)
  └─ FALSE →
  ↑ (loop back)
```

## Step Details

Below are the blocks/steps from the original workflow. Use these as a **guide**, not rigid instructions.

### Step: SETUP WORKSPACE
**Type:** prompt
**Prompt:**
```
Setting up workspace for HTB challenge.

Target: $1
Challenge name: $2

Create any missing directories:
  ./htb-targets/$2/
  ./htb-targets/$2/scans/
  ./htb-targets/$2/loot/
  ./htb-targets/$2/exploits/
  ./htb-targets/$2/notes/
  ./htb-targets/$2/.venv/

Set up Python environment:
- Use uv to crea...

(See full prompt in original workflow)
```
**Expected Output:** Structured (JSON schema defined)

### Step: CHECK STATE
**Type:** prompt
**Prompt:**
```
Check what work has already been completed for $2.

Check for these files:
1. ./htb-targets/$2/services.json - if exists, recon is done
2. ./htb-targets/$2/vulns.json - if exists, research is done
3. ./htb-targets/$2/session-log.md - read to see previous attempts

If files exist, read them to load c...

(See full prompt in original workflow)
```
**Expected Output:** Structured (JSON schema defined)

### Step: REFRESH STATE
**Type:** refresh

### Step: NEEDS RECON?
**Type:** branch
**Condition:** `needsRecon`
**Branches:** TRUE path / FALSE path

### Step: RUN RECON
**Type:** command
**Calls workflow:** `htb-recon`
**Arguments:** `$1`
**Inherits variables:** Yes
**Merges output:** Yes

### Step: SAVE RECON
**Type:** prompt
**Prompt:**
```
Recon phase complete for $1 ($2).

Tasks:
1. Move services.json to ./htb-targets/$2/services.json if not already there
2. Move recon-report-$1.md to ./htb-targets/$2/scans/recon-summary.md
3. Check if ./htb-targets/$2/session-log.md exists:
   - If it exists: Read it to see previous progress, then a...

(See full prompt in original workflow)
```
**Expected Output:** Structured (JSON schema defined)

### Step: REFRESH STATE
**Type:** refresh

### Step: NEEDS RESEARCH?
**Type:** branch
**Condition:** `needsResearch`
**Branches:** TRUE path / FALSE path

### Step: RUN RESEARCH
**Type:** command
**Calls workflow:** `htb-research`
**Arguments:** `$1`
**Inherits variables:** Yes
**Merges output:** Yes

### Step: EXPLOIT LOOP
**Type:** prompt
**Prompt:**
```
Exploitation phase for $1 (challenge: $2).

You have up to 5 attempts to exploit the target. Current attempt: {{attemptNumber}} (default 1 if not set).

First, load context from target directory:
1. Read ./htb-targets/$2/vulns.json to see available vectors
2. Read ./htb-targets/$2/session-log.md to ...

(See full prompt in original workflow)
```
**Expected Output:** Structured (JSON schema defined)

### Step: REFRESH STATE
**Type:** refresh

### Step: CONTINUE?
**Type:** branch
**Condition:** `continueLoop`
**Branches:** TRUE path / FALSE path

### Step: POST EXPLOIT
**Type:** prompt
**Prompt:**
```
Exploitation succeeded for $1 ($2)!

Current state:
- Shell obtained: {{shellObtained}}
- Flags captured: {{flagCaptured}}
- Current user: {{currentUser}}

Tasks:
1. If we have a shell, enumerate the system:
   - whoami, id, hostname, uname -a
   - Look for user.txt and root.txt
   - Check sudo perm...

(See full prompt in original workflow)
```
**Expected Output:** Structured (JSON schema defined)


---

## Orchestration Guidance

**You have full autonomy to:**
- Skip steps that aren't needed
- Repeat steps that require iteration
- Modify approach based on results
- Make intelligent decisions about flow

**Use the workflow above as a reference guide, not a rigid script.**

**Your goal:** Complete the objective efficiently.

**Your advantage:** Context awareness and intelligent decision-making.
