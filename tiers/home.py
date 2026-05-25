# ============================================================
# GUARDIAN — tiers/home.py
# Tier 1: Home User
#
# Agents that run for a home user:
# - ProfileAgent (always runs)
# - TeachingAgent (explains everything in plain English)
#
# Output: Home Lockdown Playbook
# Covers: Windows security, Microsoft account, network basics
# ============================================================

from config import TIER_HOME

TIER_NAME = "Home User"
TIER_ID = TIER_HOME

# Agents to run for this tier (in order)
# TeachingAgent will be added when built
AGENT_PIPELINE = [
    "ProfileAgent",
    # "TeachingAgent",   # coming soon
]

# Playbook sections for this tier
PLAYBOOK_SECTIONS = [
    "Organisation Profile",
    "Windows Account Security",
    "Microsoft Account Protection",
    "Network Security Basics",
    "Device Hardening",
    "Plain English Summary"
]


class HomeTier:
    """
    Tier 1 — Home User configuration.
    Manages the agent pipeline and playbook structure for home users.
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
            "## Home User Lockdown Plan\n\n"
            "This playbook is designed for a single home computer or small household setup. "
            "It covers the essential security steps to protect your Windows device, "
            "Microsoft account, and home network without requiring enterprise tools.\n\n"
            "> **SC-300 Note:** The principles in this playbook directly map to "
            "Identity Protection concepts covered in the SC-300 exam — "
            "just applied at a personal scale.\n"
        )