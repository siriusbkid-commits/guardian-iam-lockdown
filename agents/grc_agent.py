# ============================================================
# GUARDIAN — IAM Lockdown Template
# agents/grc_agent.py — Governance, Risk and Compliance Agent
#
# PURPOSE:
# Generates tailored GRC recommendations aligned to:
# - NIST AI RMF
# - ISO 27001
# - SOC 2
# - SC-300 Identity Governance objectives
# - CyberArk Defender governance objectives
#
# Reads sc300_objectives.json to map governance objectives
# automatically into the playbook output.
#
# SECURITY GUARDRAILS:
# - All inputs sanitised before passing to LLM
# - All LLM outputs validated before presenting to user
# - No sensitive data passed to LLM
# - OWASP LLM Top 10 protections applied
#
# TIERS:
# - Home: Personal data protection + basic compliance habits
# - Startup: JML process + access reviews + NIST basics
# - SMB: Full GRC framework + audit evidence + compliance mapping
#
# SC-300 OBJECTIVES COVERED:
# - Plan and implement entitlement management
# - Plan and implement access reviews
# - Plan and implement privileged access
# - Monitor Microsoft Entra activity
# ============================================================

import re
import json
import os
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from config import TIER_HOME, TIER_STARTUP, TIER_SMB


# ============================================================
# GRC CONSTANTS
# ============================================================

# Joiner/Mover/Leaver process steps
JML_PROCESS = {
    "joiner": [
        "Create named user account — never reuse old accounts",
        "Assign minimum required permissions only (least privilege)",
        "Enrol in MFA before first login",
        "Complete security awareness training before access granted",
        "Document account purpose and owner",
        "Set account review date (90 days for privileged, 180 days standard)",
    ],
    "mover": [
        "Review all current permissions — remove what is no longer needed",
        "Assign new role permissions based on new job function",
        "Revoke access to previous department systems within 24 hours",
        "Update account ownership and manager records",
        "Trigger access review for new privileged assignments",
    ],
    "leaver": [
        "Disable account immediately on last day — do not delete",
        "Revoke all privileged role assignments via PIM",
        "Transfer ownership of files and mailbox to manager",
        "Rotate all passwords the leaver knew (shared service accounts)",
        "Review and reassign any approver roles they held",
        "Delete account after 90 day retention period",
        "Document offboarding in audit log",
    ]
}

# Access review schedule by risk level
ACCESS_REVIEW_SCHEDULE = {
    "high_risk": {
        "roles": "Global Administrator, Privileged Role Administrator",
        "frequency": "Every 90 days",
        "reviewer": "Security team + manager",
        "auto_remove": "Yes — remove if no response in 14 days"
    },
    "medium_risk": {
        "roles": "Security Administrator, Exchange Administrator",
        "frequency": "Every 180 days",
        "reviewer": "Manager",
        "auto_remove": "Yes — remove if no response in 21 days"
    },
    "standard": {
        "roles": "All other role assignments",
        "frequency": "Annually",
        "reviewer": "Manager",
        "auto_remove": "No — escalate to security team"
    }
}

# Dangerous patterns to detect in LLM output
DANGEROUS_PATTERNS = [
    r"disable.*audit",
    r"remove.*logging",
    r"bypass.*review",
    r"skip.*compliance",
    r"ignore.*policy",
    r"disable.*mfa",
]


# ============================================================
# GRC AGENT
# ============================================================

class GRCAgent(BaseAgent):
    """
    Generates GRC recommendations tailored to the
    organisation's tier and detected environment.

    Reads sc300_objectives.json to automatically map
    governance objectives into the playbook output.
    """

    def __init__(self, llm_client, context: Dict[str, Any]):
        super().__init__(llm_client, context)
        self.tier = context.get("tier", TIER_HOME)
        self.org_name = context.get("org_name", "Your Organisation")
        self.systems = context.get("systems", [])
        self.posture = context.get("current_posture", "none")
        self.sc300_objectives = self._load_sc300_objectives()
        self.grc_recommendations = {}

    # --------------------------------------------------------
    # SC-300 OBJECTIVES LOADER
    # --------------------------------------------------------

    def _load_sc300_objectives(self) -> Dict[str, Any]:
        """
        Load SC-300 objectives from sc300_objectives.json.
        Returns governance domain objectives for use in output.
        """
        objectives_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "sc300_objectives.json"
        )

        try:
            with open(objectives_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract governance domain (domain 4)
            for domain in data.get("domains", []):
                if "governance" in domain.get("name", "").lower():
                    return {
                        "domain": domain.get("name"),
                        "weight": domain.get("weight"),
                        "objectives": domain.get("objectives", []),
                        "exam_tips": data.get("exam_tips", [])
                    }

        except Exception as e:
            print(f"[GUARDIAN] Note: Could not load sc300_objectives.json: {e}")

        # Fallback if file not found
        return {
            "domain": "Plan and Implement Identity Governance",
            "weight": "25-30%",
            "objectives": [],
            "exam_tips": []
        }

    # --------------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        print("\n[GUARDIAN] Running GRC Agent...")
        print(f"[GUARDIAN] Tier: {self.tier.title()}")
        print(f"[GUARDIAN] Loading SC-300 governance objectives...")
        print(f"[GUARDIAN] Generating GRC recommendations...\n")

        if self.tier == TIER_HOME:
            self.result = self._run_home()
        elif self.tier == TIER_STARTUP:
            self.result = self._run_startup()
        elif self.tier == TIER_SMB:
            self.result = self._run_smb()

        print("[GUARDIAN] GRC Agent complete. ✅\n")
        return self.result

    # --------------------------------------------------------
    # TIER RUNNERS
    # --------------------------------------------------------

    def _run_home(self) -> Dict[str, Any]:
        """Home tier — personal data protection + basic compliance."""
        prompt = self._build_prompt_home()
        raw = self._safe_llm_call(prompt)

        return {
            "tier": TIER_HOME,
            "type": "educational",
            "content": raw,
            "sc300_objectives": self.sc300_objectives
        }

    def _run_startup(self) -> Dict[str, Any]:
        """Startup tier — JML process + access reviews + NIST basics."""
        prompt = self._build_prompt_startup()
        raw = self._safe_llm_call(prompt)

        return {
            "tier": TIER_STARTUP,
            "type": "implementation",
            "content": raw,
            "jml_process": JML_PROCESS,
            "access_review_schedule": ACCESS_REVIEW_SCHEDULE,
            "sc300_objectives": self.sc300_objectives
        }

    def _run_smb(self) -> Dict[str, Any]:
        """SMB tier — full GRC framework + audit evidence + compliance mapping."""
        prompt = self._build_prompt_smb()
        raw = self._safe_llm_call(prompt)

        return {
            "tier": TIER_SMB,
            "type": "full_implementation",
            "content": raw,
            "jml_process": JML_PROCESS,
            "access_review_schedule": ACCESS_REVIEW_SCHEDULE,
            "sc300_objectives": self.sc300_objectives
        }

    # --------------------------------------------------------
    # PROMPT BUILDERS
    # --------------------------------------------------------

    def _build_prompt_home(self) -> str:
        return (
            "You are a cybersecurity expert writing a GRC section of a security playbook "
            "for a home user.\n\n"
            "Write a friendly, plain English guide to personal data protection and "
            "basic compliance habits.\n\n"
            "STRICT RULES:\n"
            "- Plain text only. No HTML. No URLs.\n"
            "- Keep it simple and encouraging.\n"
            "- Do not use technical jargon without explaining it.\n"
            "- Do not recommend disabling any security features.\n\n"
            "COVER THESE POINTS:\n"
            "1. Why personal data governance matters\n"
            "   - What data do you have that needs protecting?\n"
            "   - Photos, financial records, passwords, personal documents\n"
            "2. The 3-2-1 Backup Rule\n"
            "   - 3 copies of important data\n"
            "   - 2 different storage types\n"
            "   - 1 offsite or cloud backup\n"
            "3. Software update policy\n"
            "   - Why updates matter for security\n"
            "   - Enable automatic updates\n"
            "4. Personal incident response\n"
            "   - What to do if you think you have been hacked\n"
            "   - Who to contact\n"
            "5. Privacy review\n"
            "   - Review app permissions annually\n"
            "   - Check what data Microsoft/Google holds about you\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n\n"
            "Write in a warm encouraging tone. "
            "End each point with why it matters in one sentence.\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    def _build_prompt_startup(self) -> str:
        # Extract governance objectives from sc300_objectives.json
        gov_objectives = []
        for obj in self.sc300_objectives.get("objectives", []):
            gov_objectives.append(f"- {obj.get('objective', '')}")
        objectives_text = "\n".join(gov_objectives) if gov_objectives else "- Identity governance best practices"

        return (
            "You are a Microsoft SC-300 certified expert writing a GRC section "
            "of a security playbook for a startup.\n\n"
            "STRICT SECURITY RULES — NEVER VIOLATE THESE:\n"
            "- Never recommend skipping access reviews.\n"
            "- Never recommend keeping stale accounts active.\n"
            "- Never recommend disabling audit logging.\n"
            "- Always recommend least privilege.\n"
            "- Plain text only. No HTML. No URLs.\n\n"
            "COVER THESE SECTIONS:\n"
            "1. Identity Governance Overview\n"
            "   - What governance means for a startup\n"
            "   - Why it matters even at small scale\n"
            "2. Joiner Process\n"
            "   - Step by step new employee/contractor onboarding\n"
            "   - Minimum access principle from day one\n"
            "   - MFA enrolment before first login\n"
            "3. Mover Process\n"
            "   - Role change procedure\n"
            "   - Access review triggered by every role change\n"
            "   - 24 hour window to revoke old access\n"
            "4. Leaver Process\n"
            "   - Account disable on last day\n"
            "   - PIM role revocation\n"
            "   - 90 day retention then delete\n"
            "5. Access Review Schedule\n"
            "   - High risk roles: every 90 days\n"
            "   - Standard roles: annually\n"
            "   - How to run an access review in Entra ID\n"
            "6. Incident Response Basics\n"
            "   - What to do if a privileged account is compromised\n"
            "   - Who to contact\n"
            "   - How to revoke access quickly\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n"
            f"Systems: {', '.join(self.systems)}\n\n"
            f"SC-300 Governance Objectives to cover:\n{objectives_text}\n\n"
            "After EACH step add:\n"
            "📚 SC-300 Objective: [relevant objective from the list above]\n"
            "⚠️ Security Note: [why this matters]\n\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    def _build_prompt_smb(self) -> str:
        # Extract governance objectives
        gov_objectives = []
        for obj in self.sc300_objectives.get("objectives", []):
            gov_objectives.append(f"- {obj.get('objective', '')}")
        objectives_text = "\n".join(gov_objectives) if gov_objectives else "- Identity governance best practices"

        return (
            "You are a Microsoft SC-300 certified expert writing a comprehensive GRC section "
            "of a security playbook for an SMB.\n\n"
            "STRICT SECURITY RULES — NEVER VIOLATE THESE:\n"
            "- Never recommend skipping access reviews.\n"
            "- Never recommend keeping stale accounts active.\n"
            "- Never recommend disabling audit logging.\n"
            "- Always recommend least privilege.\n"
            "- Plain text only. No HTML. No URLs.\n\n"
            "COVER THESE SECTIONS:\n"
            "1. Identity Governance Framework\n"
            "   - NIST AI RMF alignment\n"
            "   - ISO 27001 A.9 access control alignment\n"
            "   - SOC 2 common criteria alignment\n"
            "2. Entitlement Management\n"
            "   - Access packages in Entra ID\n"
            "   - Catalogue configuration\n"
            "   - Approval workflows\n"
            "   - Terms of use enforcement\n"
            "3. Full JML Process\n"
            "   - Joiner: onboarding checklist\n"
            "   - Mover: role change procedure\n"
            "   - Leaver: offboarding checklist\n"
            "4. Access Review Programme\n"
            "   - High risk roles: 90 days\n"
            "   - Medium risk: 180 days\n"
            "   - Standard: annually\n"
            "   - Evidence collection for audit\n"
            "5. Privileged Access Governance\n"
            "   - PIM and PAM governance alignment\n"
            "   - Separation of duties\n"
            "   - Dual control for critical actions\n"
            "6. Audit and Evidence Collection\n"
            "   - What evidence to collect for ISO 27001\n"
            "   - Azure audit log retention policy\n"
            "   - Monthly governance review checklist\n"
            "7. Incident Response Plan\n"
            "   - Privileged account compromise procedure\n"
            "   - Escalation path\n"
            "   - Evidence preservation\n"
            "   - Post-incident review\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n"
            f"Systems: {', '.join(self.systems)}\n\n"
            f"SC-300 Governance Objectives to cover:\n{objectives_text}\n\n"
            "After EACH step add:\n"
            "📚 SC-300 Objective: [relevant objective]\n"
            "⚠️ Security Note: [why this matters]\n"
            "🏛️ Framework: [NIST/ISO/SOC2 alignment where relevant]\n\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    # --------------------------------------------------------
    # SECURE LLM CALL
    # --------------------------------------------------------

    def _safe_llm_call(self, prompt: str) -> str:
        """Sanitise input, call LLM, validate output."""
        safe_prompt = self._sanitise_input(prompt)
        print("[GUARDIAN] Calling LLM for GRC recommendations...")
        raw_output = self.call_llm(safe_prompt)
        validated = self._validate_output(raw_output)
        return validated

    def _sanitise_input(self, text: str) -> str:
        """OWASP LLM01: Prompt Injection protection."""
        injection_patterns = [
            r"ignore previous instructions",
            r"disregard.*above",
            r"you are now",
            r"act as",
            r"jailbreak",
            r"<\|.*\|>",
            r"\[INST\]",
            r"\[/INST\]",
        ]
        sanitised = text
        for pattern in injection_patterns:
            sanitised = re.sub(pattern, "", sanitised, flags=re.IGNORECASE)
        return sanitised

    def _validate_output(self, output: str) -> str:
        """OWASP LLM02: Insecure Output Handling."""
        if not output or output.startswith("ERROR"):
            return self._fallback_content()

        warnings = []
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, output, re.IGNORECASE):
                warnings.append(f"Dangerous pattern detected: {pattern}")

        if warnings:
            print(f"[GUARDIAN] ⚠️ Security validation flagged issues:")
            for w in warnings:
                print(f"  - {w}")
            return self._fallback_content()

        disclaimer = (
            "\n\n---\n"
            "⚠️ GUARDIAN Security Notice: These recommendations are AI-generated "
            "and should be reviewed by a qualified security professional before "
            "implementation. Always validate against your organisation's specific "
            "compliance requirements and applicable regulations."
        )

        return output + disclaimer

    def _fallback_content(self) -> str:
        """Safe fallback content if LLM output fails validation."""
        return (
            "GRC Recommendations\n\n"
            "1. Implement Joiner/Mover/Leaver Process\n"
            "Ensure all identity lifecycle events are managed consistently.\n"
            "📚 SC-300 Objective: Plan and implement entitlement management\n"
            "⚠️ Security Note: Stale accounts are a primary attack vector.\n\n"
            "2. Schedule Regular Access Reviews\n"
            "Review privileged access every 90 days minimum.\n"
            "📚 SC-300 Objective: Plan and implement access reviews\n"
            "⚠️ Security Note: Regular reviews ensure least privilege is maintained.\n\n"
            "3. Enable Comprehensive Audit Logging\n"
            "Ensure all privileged activity is logged and retained.\n"
            "📚 SC-300 Objective: Monitor Microsoft Entra activity\n"
            "⚠️ Security Note: Audit logs are essential for incident investigation.\n\n"
            "---\n"
            "⚠️ GUARDIAN Security Notice: These are baseline recommendations."
        )

    # --------------------------------------------------------
    # MARKDOWN OUTPUT
    # --------------------------------------------------------

    def to_markdown(self) -> str:
        tier = self.result.get("tier", TIER_HOME)
        content = self.result.get("content", "")
        jml = self.result.get("jml_process", {})
        reviews = self.result.get("access_review_schedule", {})
        sc300 = self.result.get("sc300_objectives", {})

        lines = [
            "## Governance, Risk and Compliance\n",
            f"> 📚 **SC-300 Domain:** {sc300.get('domain', 'Identity Governance')} "
            f"({sc300.get('weight', '25-30%')} of exam)\n",
        ]

        if tier == TIER_HOME:
            lines.append("### Personal Data Governance\n")
            lines.append(content)

        else:
            lines.append("### GRC Implementation Guide\n")
            lines.append(content)

            # JML Process table
            if jml:
                lines.append("\n### Joiner / Mover / Leaver Quick Reference\n")

                lines.append("#### Joiner Checklist")
                for step in jml.get("joiner", []):
                    lines.append(f"- [ ] {step}")
                lines.append("")

                lines.append("#### Mover Checklist")
                for step in jml.get("mover", []):
                    lines.append(f"- [ ] {step}")
                lines.append("")

                lines.append("#### Leaver Checklist")
                for step in jml.get("leaver", []):
                    lines.append(f"- [ ] {step}")
                lines.append("")

            # Access review schedule table
            if reviews:
                lines.append("\n### Access Review Schedule\n")
                lines.append("| Risk Level | Roles | Frequency | Auto-Remove |")
                lines.append("|------------|-------|-----------|-------------|")
                for level, details in reviews.items():
                    lines.append(
                        f"| {level.replace('_', ' ').title()} "
                        f"| {details['roles']} "
                        f"| {details['frequency']} "
                        f"| {details['auto_remove']} |"
                    )
                lines.append("")

            # SC-300 objectives from JSON file
            if sc300.get("objectives"):
                lines.append("\n### SC-300 Governance Objectives Covered\n")
                for obj in sc300["objectives"]:
                    lines.append(f"- 📚 **{obj.get('id')}** — {obj.get('objective')}")
                    lines.append(f"  - Weight: {obj.get('sc300_weight', 'medium').title()}")
                    lines.append(f"  - Azure Portal: `{obj.get('azure_portal_path', 'N/A')}`")
                    lines.append("")

            # Exam tips from JSON file
            if sc300.get("exam_tips"):
                lines.append("\n### SC-300 Exam Tips for Governance\n")
                for tip in sc300["exam_tips"][:4]:
                    lines.append(f"- 💡 {tip}")
                lines.append("")

        lines.append("\n### GRC Exam Objectives\n")
        for obj in self.exam_objectives():
            lines.append(f"- 📚 {obj}")

        return "\n".join(lines)

    # --------------------------------------------------------
    # EXAM OBJECTIVES
    # --------------------------------------------------------

    def exam_objectives(self) -> List[str]:
        base = [
            "SC-300: Plan and implement entitlement management",
            "SC-300: Plan and implement access reviews",
            "SC-300: Plan and implement privileged access governance",
            "SC-300: Monitor Microsoft Entra identity activity",
            "SC-300: Implement identity lifecycle management (JML)",
        ]

        if self.tier == TIER_SMB:
            base.extend([
                "SC-300: Configure access packages and catalogues",
                "SC-300: Implement terms of use policies",
                "CyberArk Defender: Integrate PAM with identity governance",
                "Framework: NIST AI RMF — Govern function",
                "Framework: ISO 27001 — A.9 Access Control",
            ])

        return base