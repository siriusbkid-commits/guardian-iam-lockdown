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
import os
from llm_factory import get_llm
from agents.profile_agent import ProfileAgent
from agents.study_agent import StudyAgent
from orchestrator import Orchestrator


def print_banner():
    print("\n" + "=" * 55)
    print("  GUARDIAN — AI-Powered IAM Lockdown Template")
    print("  Companion to GIDEON IAM Simulator")
    print("=" * 55)
    print()


def print_main_menu():
    print("\n" + "=" * 55)
    print("  GUARDIAN — Main Menu")
    print("=" * 55)
    print()
    print("  1. Generate Lockdown Playbook")
    print("     Run the full agent team for your organisation")
    print()
    print("  2. Study Mode")
    print("     Deep dive into any SC-300 or CyberArk Defender objective")
    print()
    print("  3. Exit")
    print()
    print("=" * 55)
    print()


def run_lockdown_playbook(llm):
    """Run the full GUARDIAN lockdown playbook pipeline."""
    print("\n[GUARDIAN] Starting Lockdown Playbook generation...\n")

    # Run Profile Agent
    profile_agent = ProfileAgent(llm)
    profile = profile_agent.run()

    if not profile:
        print("[GUARDIAN] Profile setup failed. Returning to menu.")
        return

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
    print("  1. Read the PowerShell Safety Guide before running scripts")
    print("  2. Implement PIM controls first — highest security impact")
    print("  3. Run Study Mode to learn the exam objectives you just implemented")
    print("  4. Run GIDEON to practice PBQ questions")
    print()


def run_study_mode(llm):
    """Run Study Mode — deep dive into exam objectives."""
    study_agent = StudyAgent(llm)
    result = study_agent.run()

    if not result:
        print("\n[GUARDIAN] Returning to main menu.\n")
        return

    output_path = result.get("output_path", "")

    if output_path and os.path.exists(output_path):
        print("\n" + "=" * 55)
        print("  Study Guide Complete!")
        print(f"  Objective : {result.get('objective_id')} — {result.get('objective')}")
        print(f"  Saved to  : {output_path}")
        print("=" * 55)
        print()
        print("  Next steps:")
        print("  1. Open the study guide and read it carefully")
        print("  2. Implement the steps in your Azure lab environment")
        print("  3. Run GIDEON to practice PBQ questions on this topic")
        print("  4. Come back and study the next objective")
        print()

        # Ask if they want to study another objective
        again = input("Study another objective? (y/n): ").strip().lower()
        if again == "y":
            run_study_mode(llm)
    else:
        print("\n[GUARDIAN] Study guide generation failed. Please try again.\n")


def main():
    print_banner()

    # Initialise LLM once — reused for all modes
    llm = get_llm()

    while True:
        print_main_menu()

        while True:
            choice = input("Select (1/2/3): ").strip()
            if choice in ["1", "2", "3"]:
                break
            print("Please enter 1, 2 or 3.")

        if choice == "1":
            run_lockdown_playbook(llm)

        elif choice == "2":
            run_study_mode(llm)

        elif choice == "3":
            print("\nThanks for using GUARDIAN. Stay secure! 🛡️\n")
            sys.exit(0)


if __name__ == "__main__":
    main()