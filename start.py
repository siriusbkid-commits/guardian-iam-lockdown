# ============================================================
# GUARDIAN — IAM Lockdown Template
# start.py — Main entry point
#
# USAGE:
#   python start.py
#
# PREREQUISITES:
#   - Python 3.10+
#   - Ollama running: ollama serve
#   - mistral-nemo pulled: ollama pull mistral-nemo
#   - pip install -r requirements.txt
# ============================================================

import sys
from llm_factory import get_llm
from agents.profile_agent import ProfileAgent
from orchestrator import Orchestrator


def print_banner():
    print("\n" + "=" * 55)
    print("  GUARDIAN — AI-Powered IAM Lockdown Template")
    print("  Companion to GIDEON IAM Simulator")
    print("=" * 55)
    print()
    print("  GUARDIAN will:")
    print("  1. Scan your system and build your organisation profile")
    print("  2. Determine your security tier (Home / Startup / SMB)")
    print("  3. Run the appropriate agent team")
    print("  4. Generate your personalised Lockdown Playbook")
    print("  5. Map every step to SC-300 / CyberArk Defender objectives")
    print()
    print("=" * 55)
    print()


def main():
    print_banner()

    # Initialise LLM
    llm = get_llm()

    # Run Profile Agent — always first
    profile_agent = ProfileAgent(llm)
    profile = profile_agent.run()

    if not profile:
        print("[GUARDIAN] Profile setup failed. Exiting.")
        sys.exit(1)

    print(f"\n[GUARDIAN] Profile complete!")
    print(f"  Organisation : {profile.get('org_name')}")
    print(f"  Tier         : {profile.get('tier').title()}")
    print(f"  Mode         : {profile.get('mode').title()}")
    print(f"  Systems      : {', '.join(profile.get('systems', []))}")

    # Run Orchestrator
    orchestrator = Orchestrator(llm, profile)
    orchestrator.run()

    # Save Playbook
    playbook_path = orchestrator.save_playbook()

    print("\n" + "=" * 55)
    print("  GUARDIAN Complete!")
    print(f"  Your Lockdown Playbook is ready:")
    print(f"  {playbook_path}")
    print("=" * 55)
    print()
    print("  Next steps:")
    print("  1. Open your playbook and review each section")
    print("  2. Implement the controls in order of priority")
    print("  3. Run GIDEON to test your knowledge")
    print("  4. Re-run GUARDIAN after implementation")
    print()


if __name__ == "__main__":
    main()