\# GUARDIAN — AI-Powered IAM Lockdown Template



> \*"You're already paying for it. You're just not using it."\*



\*\*GUARDIAN\*\* is a free, open source, offline AI-powered security lockdown template generator. A team of specialist AI agents work together to produce a personalised \*\*IAM Lockdown Playbook\*\* — practical, step-by-step security guidance using tools you already own.



Every step maps to \*\*SC-300\*\* and \*\*CyberArk Defender\*\* exam objectives, making GUARDIAN both a practical security tool and a certification study aid.



> \*Companion project to \[GIDEON IAM Simulator](https://github.com/siriusbkid-commits/gideon-pbq-generator) — generate unlimited PBQ practice questions alongside your GUARDIAN playbook.\*



\---



\## The Problem GUARDIAN Solves



Most startups and small businesses are one compromised admin account away from a catastrophic breach. They already have the tools to prevent it. They just don't know how to turn them on.



A typical startup has:

\- ✅ Microsoft 365 — already paying for it

\- ✅ Entra ID (Azure AD) — included with M365, already there

\- ❌ No PIM configured

\- ❌ No PAM controls

\- ❌ No access reviews

\- ❌ No least privilege enforcement

\- ❌ Permanent Global Admin accounts



\*\*GUARDIAN fixes all of that in an afternoon — for free.\*\*



\---



\## Who Is GUARDIAN For?



| Audience | What GUARDIAN Does For You |

|----------|--------------------------|

| 🏢 \*\*Startup founder\*\* | Configures security you already own but haven't turned on |

| 🎓 \*\*SC-300 student\*\* | Teaches exam objectives by actually implementing them |

| 🛡️ \*\*CyberArk Defender student\*\* | Hands-on PAM experience mapped to exam objectives |

| 👨‍💻 \*\*Security consultant\*\* | Structured starting point for every client engagement |

| 🏠 \*\*Home user\*\* | Basic security baseline with free tools |

| 🔌 \*\*Developer\*\* | Extensible BaseAgent architecture — add your own agents |



\---



\## Three Tiers — One Tool



| Tier | Who | Tools | Output |

|------|-----|-------|--------|

| 🏠 \*\*Home\*\* | Single user | Windows + Microsoft Account | Home Lockdown Playbook |

| 🚀 \*\*Startup\*\* | 2-50 users | Microsoft 365 + Entra ID | Startup Lockdown Playbook |

| 🏢 \*\*SMB\*\* | 50+ users | Entra ID + CyberArk | Enterprise Lockdown Playbook |



\---



\## The Agent Team



GUARDIAN uses a team of specialist AI agents — each expert in one domain:



| Agent | Status | What It Does |

|-------|--------|-------------|

| 🔍 \*\*ProfileAgent\*\* | ✅ Ready | Auto-detects your environment, determines tier |

| 🔐 \*\*PIMAgent\*\* | ✅ Ready | Entra ID PIM lockdown + PowerShell scripts |

| 🛡️ \*\*PAMAgent\*\* | ✅ Ready | CyberArk PAM configuration + audit scripts |

| 📋 \*\*GRCAgent\*\* | ✅ Ready | Governance, JML process, access reviews, compliance |

| 🎓 \*\*TeachingAgent\*\* | ✅ Ready | Plain English summary + exam study plan + GIDEON topics |



\---



\## What GUARDIAN Produces



Every run generates a complete \*\*Lockdown Playbook\*\* containing:



\- ✅ \*\*Organisation Profile\*\* — auto-detected environment

\- ✅ \*\*PowerShell Safety Guide\*\* — 🟢🟡🔴⚫ risk levels, -WhatIf explained

\- ✅ \*\*PIM Lockdown\*\* — step by step Azure portal + PowerShell scripts

\- ✅ \*\*PAM Controls\*\* — CyberArk configuration or basic PAM baseline

\- ✅ \*\*GRC Framework\*\* — JML checklists, access review schedule, compliance mapping

\- ✅ \*\*Teaching Summary\*\* — plain English + SC-300 + CyberArk exam objectives

\- ✅ \*\*Study Plan\*\* — prioritised by exam weight

\- ✅ \*\*GIDEON Topics\*\* — suggested PBQ practice questions



Saved as both \*\*Markdown\*\* (human readable) and \*\*JSON\*\* (structured data).



\---



\## Five Gaps GUARDIAN Fills Simultaneously



1\. 🔒 \*\*Security Baseline\*\* — fixes real security gaps using tools you already own

2\. 🤖 \*\*AI Literacy\*\* — shows what agentic AI can do in a practical, tangible way

3\. 🎓 \*\*IAM Education\*\* — teaches concepts WHILE implementing them

4\. 📚 \*\*Exam Preparation\*\* — hands-on SC-300 and CyberArk Defender experience

5\. 💼 \*\*Consultant Enablement\*\* — structured framework for client engagements



\---



\## Prerequisites



\- Python 3.10+

\- \[Ollama](https://ollama.com) installed and running

\- `mistral-nemo` model pulled



\---



\## Installation



\### 1. Clone or download



```bash

git clone https://github.com/siriusbkid-commits/guardian-iam-lockdown.git

cd guardian-iam-lockdown

```



Or download the ZIP from GitHub and extract it.



\### 2. Install dependencies



```bash

pip install -r requirements.txt

```



\### 3. Install Ollama



Download from \[https://ollama.com](https://ollama.com) and install.



\### 4. Pull the model



```bash

ollama pull mistral-nemo

```



\### 5. Start Ollama



```bash

ollama serve

```



\### 6. Run GUARDIAN



```bash

python start.py

```



\---



\## Usage



GUARDIAN guides you through a simple questionnaire and then runs the agent team automatically:



```

================================================

&#x20; GUARDIAN — AI-Powered IAM Lockdown Template

================================================



&#x20; 1. Scan your system and build your organisation profile

&#x20; 2. Determine your security tier (Home / Startup / SMB)

&#x20; 3. Run the appropriate agent team

&#x20; 4. Generate your personalised Lockdown Playbook

&#x20; 5. Map every step to SC-300 / CyberArk Defender objectives

```



\---



\## Output Files



Each run produces versioned files in `output/`:



```

output/

└── guardian\_\[org]\_v1.0\_\[timestamp].md     ← Your Lockdown Playbook

└── guardian\_\[org]\_v1.0\_\[timestamp].json   ← Structured data

```



Profiles are saved in `profiles/` so returning users pick up where they left off — including automatic upgrade detection when your organisation grows.



\---



\## Choosing Your Model



> 💡 \*\*Accessibility note:\*\* GUARDIAN was built and tested on a standard

> consumer laptop with 16GB RAM using a free, locally-run AI model.

> No expensive hardware, no cloud subscriptions, no API costs required.

> If you have a laptop bought in the last 3-4 years you can run GUARDIAN

> right now for free.



GUARDIAN ships with `mistral-nemo` as the default model — it runs well on most machines with 8GB+ RAM and produces high quality, professional grade security recommendations.



\*\*If you have a more powerful machine\*\* (16GB+ RAM, dedicated GPU) you can upgrade to a larger model for even richer output:



```bash

\# Higher quality — recommended for 16GB+ RAM

ollama pull llama3.1:8b



\# Best quality — recommended for 32GB+ RAM

ollama pull llama3.1:70b

```



Then update `config.py`:



```python

LOCAL\_MODEL = "llama3.1:8b"

```



\*\*Or use online mode\*\* for the highest quality output regardless of your hardware — just add your Anthropic API key.



> 💡 `mistral-nemo` produces professional grade security playbooks. Larger models

> produce more detailed output but the security principles and exam objectives

> are identical regardless of model size.



\---



\## Configuration



Edit `config.py` to switch between offline and online modes:



```python

\# Offline (default) — free, private, no internet needed

GUARDIAN\_MODE = "offline"

LOCAL\_MODEL = "mistral-nemo"



\# Online — better quality, requires Anthropic API key

GUARDIAN\_MODE = "online"

ONLINE\_MODEL = "claude-sonnet-4-20250514"

```



For online mode set your API key:



```bash

\# Windows

set ANTHROPIC\_API\_KEY=your-key-here



\# Mac/Linux

export ANTHROPIC\_API\_KEY=your-key-here

```



\---



\## Keeping Exam Objectives Current



GUARDIAN ships with `sc300\_objectives.json` and `cyberark\_objectives.json`.

Each file has a `last\_verified` date and a link to the official source.



If objectives change, update the JSON file and submit a PR — see \[CONTRIBUTING.md](CONTRIBUTING.md).



\- SC-300 official page: `https://learn.microsoft.com/credentials/certifications/exams/sc-300`

\- CyberArk Defender official page: `https://www.cyberark.com/services/training-certification/`



\---



\## Extending GUARDIAN



GUARDIAN is built to grow. Every agent is modular — add new ones by inheriting `BaseAgent`:



```python

from agents.base\_agent import BaseAgent



class OktaAgent(BaseAgent):

&#x20;   def run(self): ...

&#x20;   def to\_markdown(self): ...

&#x20;   def exam\_objectives(self): ...

```



See \[CONTRIBUTING.md](CONTRIBUTING.md) for the full guide to adding agents.



\*\*Ideas for community agents:\*\*

\- `okta\_agent.py` — Okta Identity Cloud

\- `google\_workspace\_agent.py` — Google Workspace IAM

\- `aws\_iam\_agent.py` — AWS IAM and SCP

\- `zero\_trust\_agent.py` — Zero Trust architecture

\- `hipaa\_agent.py` — HIPAA compliance mapping



\---



\## GIDEON Integration



Use \[GIDEON](https://github.com/siriusbkid-commits/gideon-pbq-generator) alongside GUARDIAN:



1\. Run GUARDIAN → get your Lockdown Playbook

2\. See the suggested GIDEON topics in the Teaching Summary

3\. Run GIDEON → generate PBQ practice questions on those topics

4\. Implement → practice → test → repeat



Together they form a complete \*\*IAM learning and implementation ecosystem\*\*. 🎯



\---



\## Professional Services



\*\*Need GUARDIAN customised for your business?\*\*



GUARDIAN can be tailored to your specific environment, compliance requirements and existing security tools. A consultant can:



\- Run GUARDIAN against your actual environment

\- Add custom agents for your specific tools

\- Implement the recommendations with you

\- Leave you with a fully documented security baseline



📧 Book a consultation: \[guardian-iam-lockdown](https://github.com/siriusbkid-commits/guardian-iam-lockdown)



\---



\## Contributing



Pull requests welcome! See \[CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.



> \*"Your fork is your portfolio."\*



\---



\## Project Structure



```

guardian-iam-lockdown/

├── agents/

│   ├── base\_agent.py          # BaseAgent — extend this for custom agents

│   ├── profile\_agent.py       # Organisation profiling + auto-detection

│   ├── pim\_agent.py           # PIM lockdown

│   ├── pam\_agent.py           # PAM / CyberArk configuration

│   ├── grc\_agent.py           # Governance, Risk, Compliance

│   └── teaching\_agent.py      # Plain English summary + study plan

├── tiers/

│   ├── home.py                # Home user tier

│   ├── startup.py             # Startup tier

│   └── smb.py                 # SMB tier

├── output/                    # Generated playbooks (gitignored)

├── profiles/                  # Saved organisation profiles (gitignored)

├── sc300\_objectives.json      # SC-300 exam objectives

├── cyberark\_objectives.json   # CyberArk Defender exam objectives

├── powershell\_safety.md       # PowerShell safety guide

├── config.py                  # Mode and model configuration

├── llm\_factory.py             # Offline/online LLM factory

├── orchestrator.py            # Agent coordination

├── start.py                   # Entry point

├── ARCHITECTURE.md            # Technical documentation

├── CONTRIBUTING.md            # Contribution guide

└── README.md

```



\---



\## License



MIT License — free to use, modify, and distribute.



\---



\## Disclaimer



Generated playbooks are AI-produced and intended as a baseline security guide. Always validate recommendations against your organisation's specific requirements and applicable regulations. This is not a substitute for professional security advice.



\---



\*GUARDIAN — Because security shouldn't be a luxury.\* 🛡️

