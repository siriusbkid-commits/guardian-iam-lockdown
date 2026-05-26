\# Installing GUARDIAN — Step by Step Guide



> This guide assumes \*\*zero technical knowledge\*\*.

> If you have never used Python, Git, or the command line before —

> this guide is written for you.

> Follow each step in order and you will have GUARDIAN running in about 15 minutes.



\---



\## What You Need



Before starting make sure you have:



\- A Windows, Mac, or Linux computer

\- Internet connection (for the initial download only)

\- About 8GB of free disk space

\- 15 minutes



\---



\## Overview



You will install four things:



1\. \*\*Python\*\* — the programming language GUARDIAN is written in

2\. \*\*Ollama\*\* — the tool that runs the AI model locally on your machine

3\. \*\*mistral-nemo\*\* — the AI model GUARDIAN uses

4\. \*\*GUARDIAN\*\* — the tool itself



\---



\## Step 1 — Install Python



Python is the programming language GUARDIAN runs on.



\### Windows:



1\. Go to \[https://www.python.org/downloads/](https://www.python.org/downloads/)

2\. Click the big yellow \*\*Download Python\*\* button

3\. Run the downloaded installer

4\. \*\*IMPORTANT:\*\* On the first screen tick the box that says \*\*"Add Python to PATH"\*\*

&#x20;  - This is easy to miss — make sure it is ticked before clicking Install

5\. Click \*\*Install Now\*\*

6\. Wait for it to finish — takes about 2 minutes



\### Mac:



1\. Go to \[https://www.python.org/downloads/](https://www.python.org/downloads/)

2\. Download the Mac installer

3\. Run it and follow the prompts



\### Verify Python installed correctly:



Open a terminal or command prompt and type:



```

python --version

```



You should see something like `Python 3.13.1` — any version 3.10 or higher is fine.



> \*\*What is a terminal?\*\*

> On Windows: press the Windows key, type \*\*PowerShell\*\*, press Enter.

> On Mac: press Cmd+Space, type \*\*Terminal\*\*, press Enter.



\---



\## Step 2 — Install Ollama



Ollama is the tool that runs the AI model locally on your machine.

This means GUARDIAN works completely offline — no data leaves your computer.



\### Windows and Mac:



1\. Go to \[https://ollama.com](https://ollama.com)

2\. Click \*\*Download\*\*

3\. Run the installer

4\. Follow the prompts — defaults are all fine



\### Verify Ollama installed correctly:



Open a new terminal window and type:



```

ollama --version

```



You should see a version number like `ollama version 0.23.1`



\---



\## Step 3 — Download the AI Model



GUARDIAN uses a model called \*\*mistral-nemo\*\* to generate security recommendations.

This is a one-time download of about 7GB.



In your terminal type:



```

ollama pull mistral-nemo

```



This will take a few minutes depending on your internet speed.

You will see a progress bar — just wait for it to complete.



> \*\*Why does it need a model?\*\*

> The model is the AI brain that generates your security playbook.

> Once downloaded it lives on your machine and works completely offline.



\---



\## Step 4 — Download GUARDIAN



You have two options — choose whichever feels more comfortable:



\### Option A — Download ZIP (easiest, no technical knowledge needed)



1\. Go to \[https://github.com/siriusbkid-commits/guardian-iam-lockdown](https://github.com/siriusbkid-commits/guardian-iam-lockdown)

2\. Click the green \*\*Code\*\* button

3\. Click \*\*Download ZIP\*\*

4\. Find the downloaded ZIP file (usually in your Downloads folder)

5\. Right click it and select \*\*Extract All\*\*

6\. Choose where to extract it — your Documents folder is a good choice

7\. You should now have a folder called `guardian-iam-lockdown`



\### Option B — Clone with Git (if you have Git installed)



```bash

git clone https://github.com/siriusbkid-commits/guardian-iam-lockdown.git

```



> \*\*Which should I choose?\*\*

> If you have never used Git before — choose Option A.

> Option A is simpler and works exactly the same way.



\---



\## Step 5 — Install GUARDIAN Dependencies



GUARDIAN needs one additional Python package. This takes about 30 seconds.



1\. Open a terminal

2\. Navigate to your GUARDIAN folder:



\*\*Windows:\*\*

```powershell

cd C:\\Users\\YourName\\Documents\\guardian-iam-lockdown

```

Replace `YourName` with your actual Windows username.



\*\*Mac/Linux:\*\*

```bash

cd \~/Documents/guardian-iam-lockdown

```



3\. Install dependencies:

```

pip install -r requirements.txt

```



> \*\*What is pip?\*\*

> pip is Python's package manager — it installs additional tools

> that GUARDIAN needs to run.



\---



\## Step 6 — Start Ollama



Before running GUARDIAN you need to start Ollama.

Open a terminal window and type:



```

ollama serve

```



You will see some text appear and then it will wait — that is normal.

\*\*Leave this terminal window open\*\* — Ollama needs to keep running in the background.



> \*\*Important:\*\* Every time you want to use GUARDIAN you need to start

> Ollama first. You can check if it is already running by looking for

> the Ollama icon in your system tray (bottom right of Windows taskbar).



\---



\## Step 7 — Run GUARDIAN



Open a \*\*new\*\* terminal window (leave the Ollama one open) and type:



\*\*Windows:\*\*

```powershell

cd C:\\Users\\YourName\\Documents\\guardian-iam-lockdown

python start.py

```



\*\*Mac/Linux:\*\*

```bash

cd \~/Documents/guardian-iam-lockdown

python start.py

```



You should see:



```

=======================================================

&#x20; GUARDIAN — AI-Powered IAM Lockdown Template

&#x20; Companion to GIDEON IAM Simulator

=======================================================



&#x20; GUARDIAN — Main Menu



&#x20; 1. Generate Lockdown Playbook

&#x20; 2. Study Mode

&#x20; 3. Exit

```



\*\*Congratulations — GUARDIAN is running!\*\* 🎉



\---



\## Choosing Your First Option



\*\*If you want to secure your organisation:\*\*

Choose option \*\*1 — Generate Lockdown Playbook\*\*

GUARDIAN will scan your system and guide you through the questionnaire.



\*\*If you are studying for SC-300 or CyberArk Defender:\*\*

Choose option \*\*2 — Study Mode\*\*

Pick any exam objective and get a focused study guide.



\---



\## Troubleshooting



\### "python is not recognized"

You forgot to tick \*\*Add Python to PATH\*\* during installation.

Uninstall Python and reinstall — make sure to tick that box.



\### "ollama is not recognized"

Ollama did not install correctly.

Close your terminal, reopen it, and try `ollama --version` again.

If still not working reinstall Ollama from ollama.com



\### "ERROR: Ollama API call failed"

Ollama is not running.

Open a terminal and run `ollama serve` then try again.



\### "No module named..."

You are not in the correct folder or dependencies are not installed.

Make sure you ran `pip install -r requirements.txt` from inside the

`guardian-iam-lockdown` folder.



\### GUARDIAN is very slow

The AI model takes time to generate responses — this is normal.

A full lockdown playbook takes 5-15 minutes on a standard laptop.

A single Study Mode guide takes 2-5 minutes.

This is expected behaviour — the model is working hard! 😊



\### I have a more powerful computer

If you have 16GB+ RAM you can use a larger model for better output.

See the \*\*Choosing Your Model\*\* section in README.md.



\---



\## What Happens to My Data?



\*\*Nothing leaves your computer.\*\*



GUARDIAN runs entirely offline using a local AI model.

Your organisation profile, generated playbooks and study guides

are all saved locally in your GUARDIAN folder.

No data is sent to any server, cloud service or third party.



\---



\## Getting Help



\- \*\*GitHub Issues:\*\* github.com/siriusbkid-commits/guardian-iam-lockdown/issues

\- \*\*CONTRIBUTING.md:\*\* How to contribute or report bugs

\- \*\*README.md:\*\* Full feature documentation



\---



\## Next Steps After Installation



1\. Run \*\*Generate Lockdown Playbook\*\* to secure your organisation

2\. Use \*\*Study Mode\*\* to learn SC-300 and CyberArk Defender objectives

3\. Install \*\*GIDEON\*\* to practice PBQ exam questions:

&#x20;  \[https://github.com/siriusbkid-commits/gideon-pbq-generator](https://github.com/siriusbkid-commits/gideon-pbq-generator)

4\. Join the community — fork the repo, add agents, submit PRs



\---



\*GUARDIAN — Because security shouldn't be a luxury.\* 🛡️

