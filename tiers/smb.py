# ============================================================
# GUARDIAN — tiers/smb.py
# Tier 3: SMB (50+ users)
#
# Agents that run for an SMB:
# - ProfileAgent (always runs)
# - PIMAgent (Entra ID / Azure AD PIM configuration)
# - PAMAgent (CyberArk configuration)
# - GRCAgent (Governance, Risk, Compliance)
# - TeachingAgent (explains everything + exam objectives)
#
# Output: SMB Lockdown Playbook
# Covers: Full PIM/PAM, CyberArk, GRC, compliance
# ============================================================

from config import TIER_SMB

TIER_NAME = "SMB"
TIER_ID = TIER_SMB

# Agents to run for this tier (in order)
AGENT_PIPELINE = [
    "ProfileAgent",
    # "PIMAgent",        # coming soon
    # "PAMAgent",        # coming soon
    # "GRCAgent",        # coming soon
    # "TeachingAgent",   # coming soon
]

# Playbook sections for this tier
PLAYBOOK_SECTIONS = [
    "Organisation Profile",
    "Entra ID Baseline Configuration",
    "PIM Lockdown",
    "CyberArk PAM Configuration",
    "Privileged Account Inventory",
    "Session Monitoring",
    "Access Reviews",
    "Governance & Compliance",
    "Plain English Summary",
    "Exam Objectives Covered"
]


class SMBTier:
    """
    Tier 3 — SMB configuration.
    Manages the agent pipeline and playbook structure for SMBs.
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
            "## SMB Lockdown Plan\n\n"
            "This playbook is designed for a medium-sized organisation using "
            "Microsoft 365, Entra ID, and CyberArk. It covers full PIM and PAM "
            "implementation, CyberArk configuration, and governance controls "
            "to meet enterprise security and compliance requirements.\n\n"
            "> **SC-300 + CyberArk Defender Note:** This playbook covers objectives "
            "from both the SC-300 and CyberArk Defender exams. "
            "Implementing it gives you hands-on experience with every major "
            "exam topic.\n"
        )