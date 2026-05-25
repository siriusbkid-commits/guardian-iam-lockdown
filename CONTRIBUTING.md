\# Contributing to GUARDIAN



First off — thank you for considering contributing to GUARDIAN! 🎉



Every contribution makes GUARDIAN more useful for businesses, students and security professionals around the world. Whether you're fixing a bug, adding a new agent, or updating exam objectives — it all matters.



\---



\## Table of Contents



\- \[Code of Conduct](#code-of-conduct)

\- \[Ways to Contribute](#ways-to-contribute)

\- \[Adding a Custom Agent](#adding-a-custom-agent)

\- \[Updating Exam Objectives](#updating-exam-objectives)

\- \[Reporting Bugs](#reporting-bugs)

\- \[Submitting a Pull Request](#submitting-a-pull-request)

\- \[Development Setup](#development-setup)



\---



\## Code of Conduct



GUARDIAN is a welcoming, inclusive project. We expect all contributors to:



\- Be respectful and constructive

\- Welcome people of all backgrounds and experience levels

\- Focus on what is best for the community

\- Show empathy towards other contributors



\---



\## Ways to Contribute



There are many ways to contribute — you don't need to be an expert:



| Contribution | Skill needed | Impact |

|-------------|-------------|--------|

| Update exam objectives JSON | None — just JSON editing | High |

| Fix a bug | Python basics | High |

| Add a new agent | Python intermediate | Very high |

| Improve documentation | Writing | Medium |

| Add a new scenario | JSON editing | Medium |

| Translate to another language | Language skills | High |

| Test on different environments | None | Medium |

| Share feedback | None | High |



\---



\## Adding a Custom Agent



This is the most impactful contribution you can make. Every new agent extends GUARDIAN's coverage to new tools, platforms or compliance frameworks.



\### Step 1 — Create your agent file



Create `agents/your\_agent\_name.py` following the BaseAgent interface:



```python

from agents.base\_agent import BaseAgent

from typing import Dict, Any, List



class YourAgent(BaseAgent):

&#x20;   """

&#x20;   Brief description of what your agent does.

&#x20;   """



&#x20;   def \_\_init\_\_(self, llm\_client, context: Dict\[str, Any]):

&#x20;       super().\_\_init\_\_(llm\_client, context)

&#x20;       self.tier = context.get("tier", "home")

&#x20;       self.org\_name = context.get("org\_name", "Your Organisation")



&#x20;   def run(self) -> Dict\[str, Any]:

&#x20;       """

&#x20;       Execute the agent and return structured results.

&#x20;       """

&#x20;       prompt = self.\_build\_prompt()

&#x20;       raw = self.call\_llm(prompt)



&#x20;       self.result = {

&#x20;           "tier": self.tier,

&#x20;           "content": raw

&#x20;       }

&#x20;       return self.result



&#x20;   def \_build\_prompt(self) -> str:

&#x20;       return f"""

You are a security expert writing a section of a security playbook.



STRICT RULES:

\- Plain text only. No HTML. No URLs.

\- Never recommend disabling security features.

\- Always recommend least privilege.



Organisation: {self.org\_name}



\[Your prompt content here]



Output plain text only.

"""



&#x20;   def to\_markdown(self) -> str:

&#x20;       """

&#x20;       Return your agent's output as a markdown section.

&#x20;       """

&#x20;       lines = \[

&#x20;           "## Your Section Title\\n",

&#x20;           self.result.get("content", ""),

&#x20;           "\\n### Exam Objectives\\n"

&#x20;       ]

&#x20;       for obj in self.exam\_objectives():

&#x20;           lines.append(f"- 📚 {obj}")

&#x20;       return "\\n".join(lines)



&#x20;   def exam\_objectives(self) -> List\[str]:

&#x20;       """

&#x20;       Return exam objectives covered by your agent.

&#x20;       """

&#x20;       return \[

&#x20;           "SC-300: Relevant objective here",

&#x20;           "CyberArk Defender: Relevant objective here"

&#x20;       ]

```



\### Step 2 — Add security guardrails



Every agent MUST include:



```python

\# Input sanitisation — protects against prompt injection

def \_sanitise\_input(self, text: str) -> str:

&#x20;   import re

&#x20;   injection\_patterns = \[

&#x20;       r"ignore previous instructions",

&#x20;       r"disregard.\*above",

&#x20;       r"you are now",

&#x20;       r"act as",

&#x20;       r"jailbreak",

&#x20;   ]

&#x20;   sanitised = text

&#x20;   for pattern in injection\_patterns:

&#x20;       sanitised = re.sub(pattern, "", sanitised, flags=re.IGNORECASE)

&#x20;   return sanitised



\# Output validation — protects against dangerous content

def \_validate\_output(self, output: str) -> str:

&#x20;   dangerous = \[

&#x20;       r"disable.\*security",

&#x20;       r"bypass.\*mfa",

&#x20;       r"remove.\*audit",

&#x20;   ]

&#x20;   import re

&#x20;   for pattern in dangerous:

&#x20;       if re.search(pattern, output, re.IGNORECASE):

&#x20;           return self.\_fallback\_content()

&#x20;   return output



\# Fallback — always provide safe content if LLM fails

def \_fallback\_content(self) -> str:

&#x20;   return "Safe fallback recommendations for your agent."

```



\### Step 3 — Register your agent



Add your agent to `agents/\_\_init\_\_.py`:



```python

from .your\_agent\_name import YourAgent

```



\### Step 4 — Wire into orchestrator



Add your agent to `orchestrator.py` in the correct tier section:



```python

from agents.your\_agent\_name import YourAgent



\# In the run() method:

if self.tier in \[TIER\_STARTUP, TIER\_SMB]:

&#x20;   your\_agent = YourAgent(self.llm\_client, self.profile)

&#x20;   your\_result = your\_agent.run()

&#x20;   self.playbook\_sections.append(your\_agent.to\_markdown())

&#x20;   self.results\["your\_agent"] = your\_result

```



\### Step 5 — Test your agent



```powershell

\# Syntax check

python -m py\_compile agents/your\_agent\_name.py



\# Full run test

python start.py

```



\---



\## Updating Exam Objectives



SC-300 and CyberArk Defender objectives change periodically. If you notice outdated objectives:



\### SC-300 objectives



1\. Check the current objectives at:

&#x20;  `https://learn.microsoft.com/credentials/certifications/exams/sc-300`

2\. Update `sc300\_objectives.json`

3\. Update the `last\_verified` date

4\. Submit a PR with a note about what changed



\### CyberArk Defender objectives



1\. Check the current objectives at:

&#x20;  `https://www.cyberark.com/services/training-certification/`

2\. Update `cyberark\_objectives.json`

3\. Update the `last\_verified` date

4\. Submit a PR with a note about what changed



\---



\## Reporting Bugs



Found a bug? Please open an issue with:



\- \*\*What happened\*\* — describe the bug

\- \*\*What you expected\*\* — what should have happened

\- \*\*Steps to reproduce\*\* — how to make it happen again

\- \*\*Your environment\*\* — OS, Python version, Ollama model

\- \*\*Error message\*\* — paste the full traceback if available



\---



\## Submitting a Pull Request



1\. \*\*Fork the repo\*\* — click Fork on GitHub

2\. \*\*Create a branch\*\* — `git checkout -b feature/your-feature-name`

3\. \*\*Make your changes\*\*

4\. \*\*Run the syntax check:\*\*

&#x20;  ```powershell

&#x20;  Get-ChildItem -Recurse -Filter "\*.py" | ForEach-Object { python -m py\_compile $\_.FullName; if ($LASTEXITCODE -ne 0) { Write-Host "ERROR in $($\_.FullName)" } }

&#x20;  ```

5\. \*\*Test with `python start.py`\*\* — confirm it runs end to end

6\. \*\*Submit the PR\*\* — describe what you changed and why



\---



\## Development Setup



```bash

\# Clone the repo

git clone https://github.com/siriusbkid-commits/guardian-iam-lockdown.git

cd guardian-iam-lockdown



\# Install dependencies

pip install -r requirements.txt



\# Install and start Ollama

\# Download from https://ollama.com

ollama pull mistral-nemo

ollama serve



\# Run GUARDIAN

python start.py

```



\---



\## Ideas for New Agents



Looking for inspiration? Here are some agents the community could build:



| Agent | Description | Difficulty |

|-------|-------------|------------|

| `okta\_agent.py` | Okta Identity Cloud configuration | Medium |

| `google\_workspace\_agent.py` | Google Workspace IAM | Medium |

| `aws\_iam\_agent.py` | AWS IAM and SCP configuration | Medium |

| `sailpoint\_agent.py` | SailPoint IIQ governance | Hard |

| `beyondtrust\_agent.py` | BeyondTrust PAM configuration | Hard |

| `zero\_trust\_agent.py` | Zero Trust architecture guide | Medium |

| `siem\_agent.py` | SIEM integration recommendations | Medium |

| `hipaa\_agent.py` | HIPAA compliance mapping | Medium |

| `gdpr\_agent.py` | GDPR identity compliance | Medium |

| `nist\_agent.py` | Full NIST CSF alignment | Hard |



\---



\## Recognition



All contributors are recognised in the project. Your GitHub profile becomes part of GUARDIAN's story — and every business that uses an agent you built is a real world impact of your contribution.



> \*"Your fork is your portfolio."\*



\---



Thank you for contributing to GUARDIAN! 🛡️

