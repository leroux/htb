---
description: Research CVEs and vulnerabilities for discovered services
allowed-tools: "*"
model: sonnet
argument-hint: <target>
---

# Htb Research

## Arguments

- **$2 (target)**: Target IP address (required)


## Workflow Graph (Reference)

```
START
  ↓
[PROMPT] CVE RESEARCH
  ↓
END
```

## Step Details

Below are the blocks/steps from the original workflow. Use these as a **guide**, not rigid instructions.

### Step: CVE RESEARCH
**Type:** prompt
**Prompt:**
```
Research vulnerabilities for target $1.

Read ./services.json to get the list of discovered services.

For EACH service with a version:
1. Search for CVEs affecting that exact version
2. Search exploit-db for public exploits
3. Search GitHub for POC code
4. Check if authentication is required
5. Ass...

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
