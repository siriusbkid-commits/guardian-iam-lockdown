# ============================================================
# GUARDIAN — IAM Lockdown Template
# orchestrator.py — Agent Orchestrator
#
# PURPOSE:
# Coordinates the agent team based on the organisation tier.
# Runs agents sequentially and assembles the master playbook.
#
# AGENTS:
# - ProfileAgent ✅
# - PIMAgent ✅
# - PAMAgent ✅
# - GRCAgent ✅
# - TeachingAgent ✅
#
# EXTENSIBILITY:
# To add a new agent:
# 1. Build your agent in agents/your_agent.py
# 2. Import it here
# 3. Add it to the correct tier pipeline below
# ============================================================

import os
import json
from datetime import datetime
from typing import Dict, Any

from config import (
    TIER_HOME, TIER_STARTUP, TIER_SMB,
    OUTPUT_DIR, GUARDIAN_VERSION
)
from tiers.home import HomeTier
from tiers.startup import StartupTier
from tiers.smb import SMBTier
from agents.profile_agent import ProfileAgent
from agents.pim_agent import PIMAgent
from agents.pam_agent import PAMAgent
from agents.grc_agent import GRCAgent
from agents.teaching_agent import TeachingAgent


class Orchestrator:
    """
    Coordinates the GUARDIAN agent team.
    Selects the correct tier, runs agents in sequence,
    and assembles the master playbook.
    """

    def __init__(self, llm_client, profile: Dict[str, Any]):
        self.llm_client = llm_client
        self.profile = profile
        self.tier = profile.get("tier", TIER_HOME)
        self.results = {}
        self.playbook_sections = []

    def run(self) -> Dict[str, Any]:
        """
        Main orchestration loop.
        Runs the correct agent pipeline for the detected tier.
        """
        print(f"\n[GUARDIAN] Starting {self.tier.title()} tier pipeline...\n")

        tier_handler = self._get_tier_handler()

        # Tier intro
        self.playbook_sections.append(tier_handler.tier_intro())

        # Profile section
        profile_agent = ProfileAgent(self.llm_client)
        profile_agent.profile = self.profile
        self.playbook_sections.append(profile_agent.to_markdown())

        # PowerShell Safety Guide
        self.playbook_sections.append(self._load_powershell_safety())

        # PIM Agent — runs for all tiers
        print("[GUARDIAN] Running PIM Agent...")
        pim_agent = PIMAgent(self.llm_client, self.profile)
        pim_result = pim_agent.run()
        self.playbook_sections.append(pim_agent.to_markdown())
        self.results["pim"] = pim_result

        # PAM Agent — runs for all tiers
        print("[GUARDIAN] Running PAM Agent...")
        pam_agent = PAMAgent(self.llm_client, self.profile)
        pam_result = pam_agent.run()
        self.playbook_sections.append(pam_agent.to_markdown())
        self.results["pam"] = pam_result

        # GRC Agent — runs for all tiers
        print("[GUARDIAN] Running GRC Agent...")
        grc_agent = GRCAgent(self.llm_client, self.profile)
        grc_result = grc_agent.run()
        self.playbook_sections.append(grc_agent.to_markdown())
        self.results["grc"] = grc_result

        # Teaching Agent — always runs last
        print("[GUARDIAN] Running Teaching Agent...")
        teaching_agent = TeachingAgent(self.llm_client, self.profile, self.results)
        teaching_result = teaching_agent.run()
        self.playbook_sections.append(teaching_agent.to_markdown())
        self.results["teaching"] = teaching_result

        print("\n[GUARDIAN] All agents complete. Assembling playbook...\n")
        return self.results

    def _get_tier_handler(self):
        if self.tier == TIER_HOME:
            return HomeTier(self.llm_client, self.profile)
        elif self.tier == TIER_STARTUP:
            return StartupTier(self.llm_client, self.profile)
        elif self.tier == TIER_SMB:
            return SMBTier(self.llm_client, self.profile)
        else:
            return HomeTier(self.llm_client, self.profile)

    def _load_powershell_safety(self) -> str:
        """Load PowerShell safety guide from file."""
        safety_path = os.path.join(
            os.path.dirname(__file__),
            "powershell_safety.md"
        )

        if os.path.exists(safety_path):
            with open(safety_path, "r", encoding="utf-8") as f:
                return f.read()

        return (
            "## PowerShell Safety Guide\n\n"
            "> ⚠️ **Before running any script:** Always use `-WhatIf` first.\n\n"
            "| Risk | Type | Makes Changes? |\n"
            "|------|------|----------------|\n"
            "| 🟢 Low | Get-* | No |\n"
            "| 🟡 Medium | Set-*, Update-* | Yes |\n"
            "| 🔴 High | Remove-*, Disable-* | Yes |\n"
            "| ⚫ Critical | Tenant-wide | Yes |\n"
        )

    def save_playbook(self) -> str:
        """Saves the assembled playbook as Markdown and JSON."""
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        org_name = self.profile.get("org_name", "organisation").lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = GUARDIAN_VERSION
        base_name = f"guardian_{org_name}_v{version}_{timestamp}"

        # Assemble full playbook
        header = self._playbook_header()
        footer = self._playbook_footer()
        full_playbook = header + "\n\n".join(self.playbook_sections) + footer

        # Save Markdown
        md_path = os.path.join(OUTPUT_DIR, f"{base_name}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_playbook)

        # Save JSON
        json_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")
        output_data = {
            "guardian_version": version,
            "generated": timestamp,
            "profile": self.profile,
            "results": self._serialise_results()
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

        print(f"[GUARDIAN] Playbook saved:")
        print(f"  Markdown : {md_path}")
        print(f"  JSON     : {json_path}\n")

        return md_path

    def _serialise_results(self) -> Dict[str, Any]:
        """Safely serialise results for JSON output."""
        safe = {}
        for key, value in self.results.items():
            try:
                json.dumps(value)
                safe[key] = value
            except (TypeError, ValueError):
                safe[key] = str(value)
        return safe

    def _playbook_header(self) -> str:
        org = self.profile.get("org_name", "Your Organisation")
        tier = self.profile.get("tier", "").title()
        date = datetime.now().strftime("%d %B %Y")

        return (
            f"# GUARDIAN Lockdown Playbook\n"
            f"## {org}\n\n"
            f"- **Tier:** {tier}\n"
            f"- **Generated:** {date}\n"
            f"- **GUARDIAN Version:** {GUARDIAN_VERSION}\n\n"
            f"> *Generated by GUARDIAN — AI-powered IAM Lockdown Template*\n"
            f"> *Companion project to GIDEON IAM Simulator*\n\n"
            f"---\n\n"
        )

    def _playbook_footer(self) -> str:
        return (
            "\n\n---\n\n"
            "## Next Steps\n\n"
            "1. Read the PowerShell Safety Guide before running any scripts\n"
            "2. Run the backup script before making any changes\n"
            "3. Execute PowerShell scripts in `-WhatIf` mode first\n"
            "4. Implement PIM controls first — highest security impact\n"
            "5. Implement PAM controls second\n"
            "6. Follow the JML process for all new starters\n"
            "7. Schedule access reviews as per the GRC schedule\n"
            "8. Use [GIDEON](https://github.com/siriusbkid-commits/gideon-pbq-generator) "
            "to test your knowledge with practice questions\n"
            "9. Re-run GUARDIAN after implementation to update your profile\n\n"
            "> ⚠️ *This playbook was generated as a baseline. "
            "Always validate recommendations against your organisation's "
            "specific requirements and applicable regulations. "
            "Test all changes in a non-production environment first.*\n\n"
            "> 💼 *Need GUARDIAN customised for your business? "
            "Book a consultation: "
            "[guardian-iam-lockdown](https://github.com/siriusbkid-commits/guardian-iam-lockdown)*\n"
        )