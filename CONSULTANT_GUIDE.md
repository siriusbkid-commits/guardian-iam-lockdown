\# GUARDIAN Consultant Guide



> \*This guide is for security consultants, IT professionals and students

> who want to run GUARDIAN for a client or another organisation remotely.\*

>

> It covers everything from setting up secure remote access to

> delivering the final playbook — step by step, assuming no prior

> consulting experience.



\---



\## Table of Contents



\- \[Before You Start](#before-you-start)

\- \[Remote Access Options](#remote-access-options)

\- \[Option 1 — Microsoft Teams Screen Share](#option-1--microsoft-teams-screen-share)

\- \[Option 2 — Windows Quick Assist](#option-2--windows-quick-assist)

\- \[Option 3 — Azure Delegated Admin Access](#option-3--azure-delegated-admin-access)

\- \[Pre-Session Checklist](#pre-session-checklist)

\- \[During the Session](#during-the-session)

\- \[Running GUARDIAN Remotely](#running-guardian-remotely)

\- \[After the Session](#after-the-session)

\- \[Handover Checklist](#handover-checklist)

\- \[Pricing and Invoicing](#pricing-and-invoicing)

\- \[What To Do If Something Goes Wrong](#what-to-do-if-something-goes-wrong)



\---



\## Before You Start



Before connecting to any client environment you need to agree on three things:



\*\*1. What you will do\*\*

Be specific. "I will run GUARDIAN, configure PIM for your top 3 admin roles,

and deliver a Lockdown Playbook" is better than "I will set up security."



\*\*2. What you will NOT do\*\*

Equally important. "I will not delete any accounts, change any passwords,

or modify anything without your approval first."



\*\*3. Who is responsible for what\*\*

You configure — they approve. Never make changes without the client

watching and confirming.



> ⚠️ \*\*Always have the client present during the session.\*\*

> Never work alone in a client environment — it protects both of you.



\---



\## Remote Access Options



There are three ways to connect to a client remotely. Choose based on

what the client is comfortable with:



| Option | Best For | Setup Difficulty | Cost |

|--------|----------|-----------------|------|

| Microsoft Teams Screen Share | Quick sessions, demos | Very easy | Free |

| Windows Quick Assist | Full remote control | Easy | Free (built into Windows) |

| Azure Delegated Admin | Professional engagements | Moderate | Free |



\---



\## Option 1 — Microsoft Teams Screen Share



\*\*Best for:\*\* Initial discovery calls, demos, guided walkthroughs

\*\*What it does:\*\* Client shares their screen — you guide them verbally

\*\*Limitation:\*\* You cannot control their mouse — they do all the clicking



\### How to set it up:



\*\*You (consultant):\*\*

1\. Have Microsoft Teams installed (free at teams.microsoft.com)

2\. Start a Teams meeting and send the client the join link



\*\*Client:\*\*

1\. Join the Teams meeting

2\. Click \*\*Share\*\* → \*\*Screen\*\* → select their browser or desktop

3\. You can now see their screen and guide them step by step



\### During the session:

\- You talk them through every step

\- They do the clicking

\- You watch and guide

\- This is actually the safest option — client stays in control



> 💡 \*\*Tip for beginners:\*\* This is the best option to start with.

> It builds trust because the client can see everything you are doing

> and they stay in control at all times.



\---



\## Option 2 — Windows Quick Assist



\*\*Best for:\*\* Hands-on configuration sessions where you need to type

\*\*What it does:\*\* Gives you full remote control of the client's computer

\*\*Limitation:\*\* Both machines must be running Windows



\### How to set it up:



\*\*You (consultant):\*\*

1\. Press \*\*Windows key\*\* and search for \*\*Quick Assist\*\*

2\. Open Quick Assist

3\. Click \*\*Help someone\*\*

4\. A 6-digit code will appear — share this with the client



\*\*Client:\*\*

1\. Press \*\*Windows key\*\* and search for \*\*Quick Assist\*\*

2\. Open Quick Assist

3\. Click \*\*Get help\*\*

4\. Enter the 6-digit code you sent them

5\. Click \*\*Share screen\*\*

6\. You now have full control of their machine



\### Security notes:

\- The 6-digit code expires after 10 minutes

\- The client can stop sharing at any time by pressing \*\*Stop sharing\*\*

\- Always tell the client what you are about to do before you do it

\- Never leave Quick Assist running unattended



> ⚠️ \*\*Important:\*\* Always narrate what you are doing.

> Say "I am now opening the Azure portal" or "I am about to click

> on Privileged Identity Management" — this keeps the client informed

> and builds trust.



\---



\## Option 3 — Azure Delegated Admin Access



\*\*Best for:\*\* Professional engagements, ongoing retainers

\*\*What it does:\*\* Gives you admin access to their Microsoft 365 tenant

without needing their password

\*\*Limitation:\*\* Requires more setup — best for longer engagements



\### How to set it up:



\*\*You (consultant) need:\*\*

\- A Microsoft Partner account (free at partner.microsoft.com)

\- Or a Microsoft 365 account of your own



\*\*Step 1 — Send a delegated admin invitation:\*\*

1\. Log in to your Microsoft 365 admin centre

2\. Navigate to: \*\*Settings\*\* → \*\*Partner relationships\*\*

3\. Click \*\*Add a partner\*\*

4\. Enter your partner ID or send an invitation link to the client



\*\*Step 2 — Client accepts the invitation:\*\*

1\. Client receives an email invitation

2\. They click \*\*Accept\*\* in the Microsoft 365 admin centre

3\. You now have delegated admin access to their tenant



\*\*Step 3 — Access their tenant:\*\*

1\. Log in to portal.azure.com with YOUR credentials

2\. Click your profile in the top right

3\. Select \*\*Switch directory\*\*

4\. Select the client's tenant



> 💡 \*\*This is the most professional option\*\* — you never see their

> passwords, access is logged, and it can be revoked instantly.

> This is how real Microsoft consultants work.



\---



\## Pre-Session Checklist



Send this to the client at least 24 hours before the session:



\### What the client needs to prepare:



```

Before our session please ensure:



\[ ] You have Global Administrator access to your Microsoft 365 tenant

\[ ] You can log in to portal.azure.com

\[ ] Microsoft Teams is installed on your computer (teams.microsoft.com)

\[ ] You have 2 hours available without interruptions

\[ ] A second person from your IT team is present if possible

\[ ] You have run the GUARDIAN backup script (we will do this together)



Please do NOT:

\[ ] Make any changes to admin accounts before our session

\[ ] Share your admin password with anyone

\[ ] Grant anyone else access before we speak

```



\### What you (consultant) need to prepare:



```

\[ ] GUARDIAN installed and tested on your machine

\[ ] Latest version pulled from GitHub

\[ ] Ollama running with mistral-nemo

\[ ] Note pad ready to document what you change

\[ ] This guide open and ready to reference

\[ ] Client's organisation name and tier (Home/Startup/SMB) confirmed

\[ ] Invoice template ready for after the session

```



\---



\## During the Session



\### Step 1 — Introduction (10 minutes)

\- Explain what you will do today

\- Explain what you will NOT do

\- Confirm they have Global Admin access

\- Run the backup script FIRST — before anything else



\### Step 2 — Run GUARDIAN (15 minutes)

\- Share your screen (you run GUARDIAN on your machine)

\- Or use Quick Assist to run it on their machine

\- Walk through the questionnaire together

\- Let them answer the questions — it's their organisation



\### Step 3 — Review the Playbook (15 minutes)

\- Open the generated Markdown playbook

\- Walk through each section with the client

\- Explain what each recommendation means in plain English

\- Let them ask questions



\### Step 4 — Implement PIM (30-45 minutes)

\- Open portal.azure.com

\- Follow the PIM section of the playbook step by step

\- Use -WhatIf on all PowerShell scripts first

\- Get client approval before applying each change

\- Document everything you change



\### Step 5 — Implement PAM basics (20-30 minutes)

\- Follow the PAM section of the playbook

\- Run the audit scripts first (read only — safe)

\- Review findings with the client

\- Implement agreed controls



\### Step 6 — Review GRC section (15 minutes)

\- Walk through the JML checklists

\- Set up the access review schedule

\- Agree on who owns each process



\### Step 7 — Handover (15 minutes)

\- Deliver the Lockdown Playbook

\- Walk through Next Steps

\- Schedule the follow up access review

\- Answer any questions



\---



\## Running GUARDIAN Remotely



\### Option A — You run GUARDIAN, share your screen



This is the simplest approach:



1\. You run GUARDIAN on your own machine

2\. Share your screen via Teams

3\. Ask the client questions from the questionnaire

4\. Type their answers in

5\. Deliver the generated playbook to them via email or Teams chat



\*\*Pros:\*\* Simple, fast, no setup on client machine

\*\*Cons:\*\* Playbook is generated on your machine, not theirs



\### Option B — Client runs GUARDIAN on their machine



For clients who want to run it themselves long term:



1\. Client downloads GUARDIAN from GitHub

2\. You guide them through installation via Teams screen share

3\. They run `python start.py` with you watching

4\. Playbook is saved on their machine

5\. They own the tool going forward



\*\*Pros:\*\* Client learns the tool, can re-run it independently

\*\*Cons:\*\* Takes longer — installation required



> 💡 \*\*Recommendation:\*\* Use Option A for the first session.

> If the client wants to run GUARDIAN themselves going forward,

> do Option B in a second session.



\---



\## After the Session



\### Immediately after:



```

\[ ] Save a copy of the generated Lockdown Playbook

\[ ] Email the playbook to the client (MD and JSON)

\[ ] Document every change you made in a session notes file

\[ ] Revoke Quick Assist or screen share access

\[ ] Send the client a follow up email summarising what was done

```



\### Follow up email template:



```

Subject: GUARDIAN Session Summary — \[Client Name]



Hi \[Name],



Thank you for today's session. Here is a summary of what we configured:



PIM:

\- Enabled PIM in Entra ID

\- Configured Global Administrator role (1 hour max, MFA required)

\- Configured Security Administrator role (4 hours max, MFA required)

\- Removed permanent admin assignments

\- Set up 90-day access reviews



PAM:

\- Completed privileged account inventory

\- Reviewed password policy

\- Enabled audit logging



Your Lockdown Playbook is attached. The Next Steps section outlines

what to do after today.



Your first access review is due in 90 days — I recommend scheduling

it now so it does not get forgotten.



Please reach out if you have any questions.



\[Your name]

```



\---



\## Handover Checklist



Before ending the engagement make sure the client has:



```

\[ ] A copy of the GUARDIAN Lockdown Playbook (MD format)

\[ ] A copy of the backup file (guardian\_role\_backup\_\[timestamp].json)

\[ ] Confirmed they can log in to PIM and activate a role

\[ ] Access review scheduled in their calendar

\[ ] Your contact details for follow up questions

\[ ] GIDEON link for practice questions (optional but recommended)

\[ ] Invoice paid or payment agreed

```



\---



\## Pricing and Invoicing



A simple starting rate card:



| Service | Duration | Suggested Rate |

|---------|----------|---------------|

| Discovery call | 30 mins | Free |

| GUARDIAN Assessment + Playbook | 2 hours | $500 - $1,500 |

| Implementation session | Per hour | $150 - $300/hr |

| Quarterly access review | 1 hour | $200 - $400 |

| Ongoing retainer | Per month | $300 - $600/month |



> 💡 \*\*Starting out tip:\*\* Offer the first client a reduced rate in

> exchange for a LinkedIn testimonial. A genuine testimonial from a

> real business is worth more than any advertising.



\### Simple invoice template:



```

INVOICE



From: \[Your name]

To: \[Client name]

Date: \[Date]

Invoice #: 001



Services:

GUARDIAN Security Assessment and PIM Configuration — $\[amount]



Payment due: 14 days

Payment method: \[Bank transfer / PayPal / Stripe]



Thank you for your business.

```



\---



\## What To Do If Something Goes Wrong



\### If you accidentally make an unintended change:



1\. \*\*Stop immediately\*\* — do not make more changes

2\. \*\*Tell the client\*\* — be honest and transparent

3\. \*\*Check the backup\*\* — restore from `guardian\_role\_backup\_\[timestamp].json`

4\. \*\*Review audit logs\*\* — Azure Portal > Entra ID > Monitoring > Audit Logs

5\. \*\*Document what happened\*\* — for your own records

6\. \*\*Contact Microsoft support\*\* if needed — portal.azure.com/support



\### If the client loses admin access:



1\. Use the \*\*break glass account\*\* (if configured)

2\. Contact Microsoft support immediately

3\. Have the client's account details ready



\### Prevention is better than cure:



\- Always run the backup script first

\- Always use -WhatIf before applying changes

\- Always have the client present and watching

\- Never rush — take your time with each step



> ⚠️ \*This guide is provided as a starting point.

> Always validate your approach against your professional

> obligations and your client's specific requirements.

> Consider professional indemnity insurance for paid engagements.\*



\---



\## A Note for First Time Consultants



Everyone starts somewhere. Your first client engagement will feel

nerve-wracking — that is completely normal.



Remember:

\- You built GUARDIAN — you understand it better than almost anyone

\- The client hired you because they do not know how to do this

\- You do not need to know everything — you need to know more than they do

\- GUARDIAN does the heavy lifting — you are the guide

\- It is completely fine to say "let me check that" during a session



The combination of GUARDIAN doing the technical work and you explaining

what it means in plain English is genuinely valuable. Do not underestimate

that value.



> \*"Your fork is your portfolio. Your first client is your proof of concept."\* 🛡️

