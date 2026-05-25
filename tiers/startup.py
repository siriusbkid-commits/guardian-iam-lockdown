# ============================================================
# GUARDIAN — tiers/startup.py
# Tier 2: Startup (2-50 users)
#
# Agents that run for a startup:
# - ProfileAgent (always runs)
# - PIMAgent (Entra ID / Azure AD PIM configuration)
# - GRCAgent (Governance, Risk, Compliance)
# - TeachingAgent (explains everything + exam objectives)
#
# Output: Startup Lockdown Playbook
# Covers: Entra ID, PIM, access reviews, least privilege
# ============================================================

from config import TIER_STARTUP

TIER_NAME = "Startup"
TIER_ID = TIER_STARTUP

# Agents to run for this tier (in order)
AGENT_PIPELINE = [
    "ProfileAgent",
    # "PIMAgent",        # coming soon
    # "GRCAgent",        # coming soon
    # "TeachingAgent",   # coming soon
]

# Playbook sections for this tier
PLAYBOOK_SECTIONS = [
    "Organisation Profile",
    "Entra ID Baseline Configuration",
    "PIM Lockdown",
    "Access Reviews",
    "Least Privilege Implementation",
    "Governance & Compliance",
    "Plain English Summary",
    "Exam Objectives Covered"
]


class StartupTier:
    """
    Tier 2 — Startup configuration.
    Manages the agent pipeline and playbook structure for startups.
    """

    def __init__(self, llm_client, context: dict):
        self.llm_client = llm_client
        self.context = context
        self.tier_name = TIER_NAME

    def get_agent_pipeline(self) -> list:
        return AGENT_PIPELINE

    def get_playbook_sections(self) -> list:
        return PLAYBOOK_SECTIONS

    def tier_intro(self) -> str:
        return (
            "## Startup Lockdown Plan\n\n"
            "This playbook is designed for a startup or small organisation using "
            "Microsoft 365 and Entra ID. It covers the essential PIM and identity "
            "governance steps to protect your privileged accounts and meet "
            "baseline compliance requirements.\n\n"
            "> **SC-300 Note:** Every step in this playbook maps directly to "
            "SC-300 exam objectives. Implementing this playbook is the best "
            "possible exam preparation.\n"
        )