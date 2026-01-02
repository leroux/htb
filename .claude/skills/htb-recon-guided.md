---
description: HTB reconnaissance workflow - scans target and enumerates discovered services
allowed-tools: "*"
model: sonnet
argument-hint: <target>
---

# Htb Recon

## Arguments

- **$2 (target)**: Target IP address (required)


## Workflow Graph (Reference)

```
START
  ↓
[PROMPT] RUSTSCAN RECON
  ↓
BRANCH: HAS WEB? (hasWeb)
  ├─ TRUE →
  [PROMPT] WEB ENUM
    ↓
  BRANCH: HAS SMB? (hasSMB)
    ├─ TRUE →
    [PROMPT] SMB ENUM
      ↓
    BRANCH: HAS FTP? (hasFTP)
      ├─ TRUE →
      [PROMPT] FTP ENUM
        ↓
      [PROMPT] SAVE SERVICES
        ↓
      END
      └─ FALSE →
      ↑ (loop back)
    └─ FALSE →
    ↑ (loop back)
  └─ FALSE →
  ↑ (loop back)
```

## Step Details

Below are the blocks/steps from the original workflow. Use these as a **guide**, not rigid instructions.

### Step: RUSTSCAN RECON
**Type:** prompt
**Prompt:**
```
Run a comprehensive rustscan on target $1.

Run: rustscan -a $1 -- -sV -sC

Rustscan will quickly scan all 65535 ports and pass open ports to nmap for service detection. This is much faster than pure nmap.

If rustscan is not available, fall back to: nmap -sV -sC -p- $1

After the scan completes, an...

(See full prompt in original workflow)
```
**Expected Output:** Structured (JSON schema defined)

### Step: HAS WEB?
**Type:** branch
**Condition:** `hasWeb`
**Branches:** TRUE path / FALSE path

### Step: WEB ENUM
**Type:** prompt
**Prompt:**
```
Web service detected on $1. Perform web enumeration:

1. Check what's on the main page (curl or browser)
2. Look for robots.txt, sitemap.xml
3. Run directory enumeration: gobuster dir -u http://$1 -w /usr/share/wordlists/dirb/common.txt (or feroxbuster)
4. Check for common files: .git, .env, backup ...

(See full prompt in original workflow)
```
**Expected Output:** Structured (JSON schema defined)

### Step: HAS SMB?
**Type:** branch
**Condition:** `hasSMB`
**Branches:** TRUE path / FALSE path

### Step: SMB ENUM
**Type:** prompt
**Prompt:**
```
SMB service detected on $1. Perform SMB enumeration:

1. List shares: smbclient -L //$1 -N
2. Try anonymous access to shares
3. Run enum4linux: enum4linux -a $1
4. Check for known vulnerabilities (EternalBlue, etc.)
5. Look for accessible files, credentials, or sensitive info

Report your findings.
```
**Expected Output:** Structured (JSON schema defined)

### Step: HAS FTP?
**Type:** branch
**Condition:** `hasFTP`
**Branches:** TRUE path / FALSE path

### Step: FTP ENUM
**Type:** prompt
**Prompt:**
```
FTP service detected on $1. Perform FTP enumeration:

1. Try anonymous login: ftp $1 (user: anonymous)
2. List accessible files and directories
3. Check for writable directories
4. Download any interesting files
5. Check FTP version for known vulnerabilities

Report your findings.
```
**Expected Output:** Structured (JSON schema defined)

### Step: SAVE SERVICES
**Type:** prompt
**Prompt:**
```
Recon complete for $1.

Summarize all findings:
- Services discovered: {{services}}
- Web findings (if any): {{webFindings}}
- SMB findings (if any): {{smbFindings}}
- FTP findings (if any): {{ftpFindings}}

Tasks:
1. Write a structured services.json to the current directory:

{
  "target": "$1",
  ...

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
