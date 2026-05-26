# GUARDIAN — Architecture Documentation

> This is a living document. Updated as each agent is built.
> Current status: v1.0 — all five core agents complete.

---

## Overview

GUARDIAN is an AI-powered agentic security lockdown template generator.
It produces a personalised IAM lockdown playbook for home users, startups, and SMBs
using a team of specialist AI agents.

Every step maps to SC-300 and CyberArk Defender exam objectives,
making GUARDIAN both a practical security tool and a certification study aid.

---

## Design Principles

1. **Secure by default** — baseline security for anyone, not just enterprises
2. **Built to grow** — modular agents, versioned playbooks, upgrade paths
3. **Teach while implementing** — every decision explained, exam objectives mapped
4. **Offline first** — runs locally with Ollama, no API keys required
5. **Open and extensible** — community agents via BaseAgent interface
6. **Safe by design** — OWASP LLM Top 10 guardrails in every agent

---

## Three Tier System

| Tier | Users | Tools | Agents |
|------|-------|-------|--------|
| 🏠 Home | 1 | Windows + Microsoft Account | Profile, PIM (educational), PAM (alternatives), GRC, Teaching |
| 🚀 Startup | 2-50 | Microsoft 365 + Entra ID | Profile, PIM, PAM, GRC, Teaching |
| 🏢 SMB | 50+ | M365 + Entra ID + CyberArk | Profile, PIM, PAM (full CyberArk), GRC, Teaching |

---

## Agent Architecture

### BaseAgent (agents/base_agent.py) ✅
Abstract base class all agents inherit from.

**Required methods:**
- `run()` — execute agent, return structured results
- `to_markdown()` — return playbook section as markdown
- `exam_objectives()` — return list of exam objectives covered

**Optional methods:**
- `to_json()` — return JSON-serialisable results
- `agent_name()` — return display name
- `validate_context()` — check required context keys
- `call_llm()` — wrapper around LLM call

---

### ProfileAgent (agents/profile_agent.py) ✅
First agent to run. Builds organisation profile via hybrid auto-detection + questionnaire.

**Auto-detects:**
- OS and version
- Domain join status
- Azure AD join status (dsregcmd)
- Microsoft 365 / OneDrive presence
- Microsoft Teams
- CyberArk install paths and services

**Features:**
- Smart tier suggestion based on detected environment
- Profile persistence — saves and reloads between runs
- Upgrade detection (e.g. Startup → SMB when CyberArk detected)
- Consultant and Audit modes

---

### PIMAgent (agents/pim_agent.py) ✅
Generates PIM lockdown recommendations for Entra ID.

**Per tier:**
- Home: Educational overview of PIM concepts
- Startup: Essential roles (Global Admin, Security Admin) + basic policies
- SMB: All high-risk roles + break glass + full access reviews

**PowerShell scripts:**
- Check PIM licence availability
- List permanent admin assignments (read only)
- Configure Global Admin PIM settings (-WhatIf default)
- Backup current role assignments

**Security guardrails:**
- Prompt injection sanitisation
- Dangerous pattern detection
- Safe fallback content
- -WhatIf on all modifying scripts

---

### PAMAgent (agents/pam_agent.py) ✅
Generates PAM lockdown recommendations.

**Deployment types:**
- `not_applicable` — Home and Startup without CyberArk (basic PAM controls)
- `cloud` — CyberArk Cloud (SaaS)
- `self_hosted` — CyberArk Self-Hosted (on-premise)

**Per tier:**
- Home: PAM concepts + free alternatives (Bitwarden, Microsoft Authenticator)
- Startup: Basic PAM controls + prepare for CyberArk
- SMB: Full CyberArk configuration (Vault, CPM, PSM, PVWA)

**PowerShell scripts:**
- Audit privileged accounts (read only)
- Check password policy (read only)
- Enable audit logging (-WhatIf default)
- CyberArk safe audit (SMB only)
- CyberArk session review guide (SMB only)
- CyberArk CPM check (SMB only)

---

### GRCAgent (agents/grc_agent.py) ✅
Generates Governance, Risk and Compliance recommendations.

**Features:**
- Reads `sc300_objectives.json` to map governance objectives automatically
- JML process with actionable checklists (Joiner/Mover/Leaver)
- Access review schedule table by risk level
- Framework alignment: NIST AI RMF, ISO 27001, SOC 2

**Per tier:**
- Home: Personal data protection, backup strategy, privacy review
- Startup: JML process, access reviews, NIST basics, incident response
- SMB: Full GRC framework, entitlement management, audit evidence

---

### TeachingAgent (agents/teaching_agent.py) ✅
Final agent. Reads all previous results and produces teaching summary.

**Features:**
- Reads results from ALL previous agents
- Calls LLM for plain English summary
- Auto-maps SC-300 objectives from `sc300_objectives.json`
- Auto-maps CyberArk Defender objectives from `cyberark_objectives.json`
- Builds prioritised study plan by exam weight
- Suggests GIDEON PBQ topics
- Includes exam tips from both JSON files

**Output sections:**
- What We Just Did (plain English)
- How This Makes You Safer
- What To Do Next
- A Note For Students
- SC-300 Objectives Covered
- CyberArk Defender Objectives Covered
- Prioritised Study Plan
- Practice with GIDEON

---

## Orchestrator (orchestrator.py)

Coordinates the GUARDIAN agent team.

**Pipeline:**
```
start.py
↓
ProfileAgent → builds context
↓
Orchestrator → selects tier pipeline
↓
PowerShell Safety Guide loaded from file
↓
PIMAgent → PIM recommendations + scripts
↓
PAMAgent → PAM recommendations + scripts
↓
GRCAgent → GRC framework + JML + access reviews
↓
TeachingAgent → plain English + exam objectives + study plan
↓
Orchestrator assembles master playbook
↓
Save as guardian_[org]_v[version]_[timestamp].md + .json
```

---

## LLM Factory (llm_factory.py)

Supports offline and online modes:

| Mode | Class | Model | Cost |
|------|-------|-------|------|
| offline | LocalOllamaLLM | mistral-nemo | Free |
| online | OnlineAnthropicLLM | claude-sonnet-4 | API cost |

Switch in config.py: `GUARDIAN_MODE = "offline"` or `"online"`

---

## Exam Objectives Files

### sc300_objectives.json
SC-300 Microsoft Identity and Access Administrator objectives.
Four domains mapped to GUARDIAN agents.
Includes exam tips and recommended labs.

### cyberark_objectives.json
CyberArk Defender — PAM objectives.
Five domains: PAM Fundamentals, Vault, CPM, PSM, PVWA.
Includes exam tips and recommended labs.

Both files have `last_verified` date and link to official source.
Community maintained — submit a PR if objectives change.

---

## Security Architecture

Every agent implements OWASP LLM Top 10 protections:

| OWASP Risk | GUARDIAN Control |
|------------|-----------------|
| LLM01: Prompt Injection | Input sanitisation in every agent |
| LLM02: Insecure Output | Output validation + dangerous pattern detection |
| LLM06: Sensitive Info | No credentials or sensitive data passed to LLM |
| LLM09: Overreliance | Security disclaimers on all AI-generated content |

PowerShell scripts follow risk-tier model:
- 🟢 Low — read only, no changes
- 🟡 Medium — configuration changes, -WhatIf required
- 🔴 High — destructive, backup required
- ⚫ Critical — tenant-wide, approval required

---

## Playbook Output Structure

```
# GUARDIAN Lockdown Playbook
## [Organisation Name]

[Header — tier, date, version]

[Tier Introduction]

[Organisation Profile + Detected Environment]

[PowerShell Safety Guide]

[PIM Lockdown]
  - Configuration guide
  - PowerShell scripts

[PAM Lockdown]
  - Configuration guide
  - PowerShell scripts

[Governance, Risk and Compliance]
  - JML checklists
  - Access review schedule
  - SC-300 objectives from JSON

[Teaching Summary]
  - Plain English summary
  - SC-300 objectives covered
  - CyberArk objectives covered
  - Study plan
  - GIDEON topics

[Next Steps + Consulting CTA]
```

---

## Adding Custom Agents

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

Quick summary:
1. Create `agents/your_agent.py` inheriting `BaseAgent`
2. Implement `run()`, `to_markdown()`, `exam_objectives()`
3. Add security guardrails (sanitise input, validate output, fallback)
4. Register in `agents/__init__.py`
5. Wire into `orchestrator.py`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-25 | Full v1.0 — all five agents complete |
| 0.5 | 2026-05-24 | GRC Agent added |
| 0.4 | 2026-05-23 | PAM Agent added |
| 0.3 | 2026-05-23 | PIM Agent added |
| 0.2 | 2026-05-22 | PowerShell Safety Guide added |
| 0.1 | 2026-05-22 | Initial skeleton — ProfileAgent only |

---

## Companion Project

**GIDEON IAM Simulator**
https://github.com/siriusbkid-commits/gideon-pbq-generator

Generate unlimited PBQ practice questions based on the scenarios
covered in your GUARDIAN playbook. The Teaching Agent suggests
specific GIDEON topics after every playbook run.