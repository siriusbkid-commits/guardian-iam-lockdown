# ============================================================
# GUARDIAN — IAM Lockdown Template
# agents/teaching_agent.py — Teaching Agent
#
# PURPOSE:
# The final agent to run. Reads all previous agent results
# and produces:
# - Plain English summary of everything implemented
# - Risk reduction summary
# - SC-300 exam topics covered (from sc300_objectives.json)
# - CyberArk Defender topics covered (from cyberark_objectives.json)
# - Prioritised study plan based on exam weights
# - Suggested GIDEON PBQ topics to practice
#
# This agent ties the whole playbook together and makes it
# accessible to beginners while still being valuable to
# experienced practitioners.
#
# SECURITY GUARDRAILS:
# - All inputs sanitised before passing to LLM
# - All LLM outputs validated before presenting to user
# - OWASP LLM Top 10 protections applied
#
# SC-300 OBJECTIVES COVERED:
# - All domains covered via summary and study plan
# ============================================================

import re
import json
import os
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from config import TIER_HOME, TIER_STARTUP, TIER_SMB


# ============================================================
# DANGEROUS PATTERNS
# ============================================================

DANGEROUS_PATTERNS = [
    r"disable.*security",
    r"bypass.*mfa",
    r"ignore.*policy",
    r"skip.*review",
    r"remove.*audit",
]


# ============================================================
# TEACHING AGENT
# ============================================================

class TeachingAgent(BaseAgent):
    """
    The final agent. Reads all previous results and produces
    a plain English teaching summary with exam study guide.
    """

    def __init__(self, llm_client, context: Dict[str, Any], all_results: Dict[str, Any]):
        super().__init__(llm_client, context)
        self.tier = context.get("tier", TIER_HOME)
        self.org_name = context.get("org_name", "Your Organisation")
        self.all_results = all_results
        self.sc300_objectives = self._load_objectives("sc300_objectives.json")
        self.cyberark_objectives = self._load_objectives("cyberark_objectives.json")

    # --------------------------------------------------------
    # OBJECTIVES LOADERS
    # --------------------------------------------------------

    def _load_objectives(self, filename: str) -> Dict[str, Any]:
        """Load objectives from JSON file."""
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            filename
        )

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[GUARDIAN] Note: Could not load {filename}: {e}")
            return {}

    # --------------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        print("\n[GUARDIAN] Running Teaching Agent...")
        print(f"[GUARDIAN] Summarising all agent results...")
        print(f"[GUARDIAN] Mapping exam objectives...\n")

        # Build summary of what was implemented
        implemented_summary = self._build_implemented_summary()

        # Call LLM for plain English explanation
        prompt = self._build_prompt(implemented_summary)
        plain_english = self._safe_llm_call(prompt)

        # Map exam objectives automatically
        sc300_covered = self._map_sc300_objectives()
        cyberark_covered = self._map_cyberark_objectives()

        # Build study plan
        study_plan = self._build_study_plan(sc300_covered, cyberark_covered)

        # Build GIDEON suggestions
        gideon_topics = self._build_gideon_topics()

        self.result = {
            "tier": self.tier,
            "plain_english": plain_english,
            "implemented_summary": implemented_summary,
            "sc300_covered": sc300_covered,
            "cyberark_covered": cyberark_covered,
            "study_plan": study_plan,
            "gideon_topics": gideon_topics
        }

        print("[GUARDIAN] Teaching Agent complete. ✅\n")
        return self.result

    # --------------------------------------------------------
    # SUMMARY BUILDER
    # --------------------------------------------------------

    def _build_implemented_summary(self) -> str:
        """Build a summary of what all agents implemented."""
        summary_parts = []

        if "pim" in self.all_results:
            pim = self.all_results["pim"]
            tier = pim.get("tier", "")
            if pim.get("type") == "educational":
                summary_parts.append("PIM: Educational overview provided")
            else:
                roles = pim.get("roles_covered", [])
                summary_parts.append(
                    f"PIM: Configured for {len(roles)} privileged roles "
                    f"with MFA, approval workflows and access reviews"
                )

        if "pam" in self.all_results:
            pam = self.all_results["pam"]
            deployment = pam.get("deployment", "basic")
            controls = pam.get("core_controls", [])
            summary_parts.append(
                f"PAM: {len(controls)} core controls implemented "
                f"(deployment: {deployment})"
            )

        if "grc" in self.all_results:
            summary_parts.append(
                "GRC: JML process defined, access review schedule set, "
                "governance framework aligned"
            )

        return ". ".join(summary_parts) if summary_parts else "Security baseline configured"

    # --------------------------------------------------------
    # PROMPT BUILDER
    # --------------------------------------------------------

    def _build_prompt(self, implemented_summary: str) -> str:
        tier_context = {
            TIER_HOME: "home user with a personal computer",
            TIER_STARTUP: "startup using Microsoft 365 and Entra ID",
            TIER_SMB: "SMB using Microsoft 365, Entra ID and CyberArk"
        }.get(self.tier, "organisation")

        return (
            "You are a friendly cybersecurity teacher writing the final summary section "
            "of a security playbook.\n\n"
            "STRICT RULES:\n"
            "- Plain text only. No HTML. No URLs.\n"
            "- Use simple, encouraging language.\n"
            "- Explain technical terms when you use them.\n"
            "- Do not recommend disabling any security features.\n"
            "- Keep each section concise — 3-5 sentences maximum.\n\n"
            f"The playbook was generated for a {tier_context}.\n"
            f"Organisation name: {self.org_name}\n\n"
            f"What was implemented:\n{implemented_summary}\n\n"
            "Write these four sections:\n\n"
            "SECTION 1 — WHAT WE JUST DID\n"
            "Explain in plain English what was configured in this playbook. "
            "Imagine you are explaining it to someone with no technical background. "
            "Use an analogy if it helps.\n\n"
            "SECTION 2 — HOW THIS MAKES YOU SAFER\n"
            "Explain specifically what risks have been reduced. "
            "Give a concrete example of an attack that is now harder to carry out.\n\n"
            "SECTION 3 — WHAT TO DO NEXT\n"
            "Three practical next steps the organisation should take "
            "after implementing this playbook.\n\n"
            "SECTION 4 — A NOTE FOR STUDENTS\n"
            "A short encouraging message for anyone studying SC-300 or CyberArk Defender "
            "who is using this playbook as a study tool. "
            "Explain how implementing this playbook maps to real exam experience.\n\n"
            "Output plain text only. No JSON. Use the section headings exactly as written above."
        )

    # --------------------------------------------------------
    # EXAM OBJECTIVE MAPPERS
    # --------------------------------------------------------

    def _map_sc300_objectives(self) -> List[Dict[str, Any]]:
        """
        Map SC-300 objectives covered by this playbook run.
        Based on which agents ran and what tier was used.
        """
        covered = []

        for domain in self.sc300_objectives.get("domains", []):
            for obj in domain.get("objectives", []):
                # Map objectives to agents that covered them
                agent = domain.get("guardian_agent", "")
                covered_by = []

                if agent == "PIMAgent" and "pim" in self.all_results:
                    covered_by.append("PIM Agent")
                if agent == "GRCAgent" and "grc" in self.all_results:
                    covered_by.append("GRC Agent")
                if agent == "PAMAgent" and "pam" in self.all_results:
                    covered_by.append("PAM Agent")

                if covered_by:
                    covered.append({
                        "id": obj.get("id"),
                        "objective": obj.get("objective"),
                        "weight": obj.get("sc300_weight", "medium"),
                        "domain": domain.get("name"),
                        "covered_by": covered_by,
                        "portal_path": obj.get("azure_portal_path", "")
                    })

        return covered

    def _map_cyberark_objectives(self) -> List[Dict[str, Any]]:
        """
        Map CyberArk Defender objectives covered by this playbook run.
        Only relevant for SMB tier or when CyberArk is detected.
        """
        covered = []

        # Only map CyberArk objectives if PAM agent ran
        if "pam" not in self.all_results:
            return covered

        pam_deployment = self.all_results.get("pam", {}).get("deployment", "")

        for domain in self.cyberark_objectives.get("domains", []):
            for obj in domain.get("objectives", []):
                # For non-CyberArk deployments only include fundamentals
                if pam_deployment not in ["cloud", "self_hosted"]:
                    if domain.get("id") != "domain-1":
                        continue

                covered.append({
                    "id": obj.get("id"),
                    "objective": obj.get("objective"),
                    "weight": obj.get("defender_weight", "medium"),
                    "domain": domain.get("name"),
                    "component": obj.get("cyberark_component", "")
                })

        return covered

    # --------------------------------------------------------
    # STUDY PLAN BUILDER
    # --------------------------------------------------------

    def _build_study_plan(
        self,
        sc300_covered: List[Dict],
        cyberark_covered: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Build a prioritised study plan based on exam weights.
        High weight objectives first.
        """
        study_items = []

        # SC-300 high weight items first
        for obj in sc300_covered:
            if obj.get("weight") == "high":
                study_items.append({
                    "exam": "SC-300",
                    "priority": "🔴 High",
                    "objective": obj.get("objective"),
                    "domain": obj.get("domain"),
                    "action": f"Practice in Azure Portal: {obj.get('portal_path', 'Entra ID')}"
                })

        # CyberArk high weight items
        for obj in cyberark_covered:
            if obj.get("weight") == "high":
                study_items.append({
                    "exam": "CyberArk Defender",
                    "priority": "🔴 High",
                    "objective": obj.get("objective"),
                    "domain": obj.get("domain"),
                    "action": f"Practice in CyberArk: {obj.get('component', 'PVWA')}"
                })

        # Medium weight items
        for obj in sc300_covered:
            if obj.get("weight") == "medium":
                study_items.append({
                    "exam": "SC-300",
                    "priority": "🟡 Medium",
                    "objective": obj.get("objective"),
                    "domain": obj.get("domain"),
                    "action": f"Review in Azure Portal: {obj.get('portal_path', 'Entra ID')}"
                })

        return study_items

    # --------------------------------------------------------
    # GIDEON TOPICS BUILDER
    # --------------------------------------------------------

    def _build_gideon_topics(self) -> List[str]:
        """
        Build suggested GIDEON PBQ topics based on what was implemented.
        """
        topics = []

        if "pim" in self.all_results:
            topics.extend([
                "Configure Privileged Identity Management in Entra ID",
                "Implement just-in-time privileged access",
                "Configure PIM access reviews for high-risk roles",
                "Monitor PIM activity and alerts",
            ])

        if "pam" in self.all_results:
            topics.extend([
                "Privileged Account Management fundamentals",
                "CyberArk PSM session recording and monitoring",
                "CPM credential rotation configuration",
                "Dual control workflow for privileged access",
            ])

        if "grc" in self.all_results:
            topics.extend([
                "Joiner Mover Leaver identity lifecycle process",
                "Plan and implement access reviews",
                "Identity governance and entitlement management",
                "Monitor Microsoft Entra identity activity",
            ])

        return topics

    # --------------------------------------------------------
    # SECURE LLM CALL
    # --------------------------------------------------------

    def _safe_llm_call(self, prompt: str) -> str:
        """Sanitise input, call LLM, validate output."""
        safe_prompt = self._sanitise_input(prompt)
        print("[GUARDIAN] Calling LLM for plain English summary...")
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

        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, output, re.IGNORECASE):
                print(f"[GUARDIAN] ⚠️ Security validation flagged: {pattern}")
                return self._fallback_content()

        return output

    def _fallback_content(self) -> str:
        """Safe fallback content."""
        return (
            "WHAT WE JUST DID\n"
            "This playbook configured privileged identity and access management "
            "controls for your organisation. Think of it as putting locks on your "
            "most sensitive doors and keeping a log of everyone who enters.\n\n"
            "HOW THIS MAKES YOU SAFER\n"
            "Privileged accounts are the most targeted by attackers. "
            "By implementing PIM, PAM and GRC controls you have significantly "
            "reduced the risk of a privileged account being compromised and misused.\n\n"
            "WHAT TO DO NEXT\n"
            "1. Implement the controls in this playbook starting with PIM.\n"
            "2. Run the access review process quarterly.\n"
            "3. Use GIDEON to test your knowledge with practice questions.\n\n"
            "A NOTE FOR STUDENTS\n"
            "Every step in this playbook maps to real SC-300 and CyberArk Defender "
            "exam objectives. By implementing this playbook you have gained hands-on "
            "experience that no textbook can provide. You are ready to sit the exam."
        )

    # --------------------------------------------------------
    # MARKDOWN OUTPUT
    # --------------------------------------------------------

    def to_markdown(self) -> str:
        plain_english = self.result.get("plain_english", "")
        sc300_covered = self.result.get("sc300_covered", [])
        cyberark_covered = self.result.get("cyberark_covered", [])
        study_plan = self.result.get("study_plan", [])
        gideon_topics = self.result.get("gideon_topics", [])

        lines = [
            "## Teaching Summary\n",
            "> 🎓 *This section explains what was implemented, "
            "what it means for your security, and how it maps to your exam.*\n",
        ]

        # Plain English summary from LLM
        lines.append(plain_english)
        lines.append("")

        # SC-300 objectives covered
        if sc300_covered:
            lines.append("\n### SC-300 Objectives Covered in This Playbook\n")
            lines.append(f"> 📚 Total objectives covered: {len(sc300_covered)}\n")

            high = [o for o in sc300_covered if o.get("weight") == "high"]
            medium = [o for o in sc300_covered if o.get("weight") == "medium"]

            if high:
                lines.append("**High Weight Objectives (prioritise these for exam):**")
                for obj in high:
                    lines.append(
                        f"- ✅ **{obj.get('id')}** — {obj.get('objective')} "
                        f"*(covered by: {', '.join(obj.get('covered_by', []))})*"
                    )
                lines.append("")

            if medium:
                lines.append("**Medium Weight Objectives:**")
                for obj in medium:
                    lines.append(
                        f"- ✅ **{obj.get('id')}** — {obj.get('objective')} "
                        f"*(covered by: {', '.join(obj.get('covered_by', []))})*"
                    )
                lines.append("")

        # CyberArk objectives covered
        if cyberark_covered:
            lines.append("\n### CyberArk Defender Objectives Covered\n")
            lines.append(f"> 📚 Total objectives covered: {len(cyberark_covered)}\n")

            high = [o for o in cyberark_covered if o.get("weight") == "high"]
            medium = [o for o in cyberark_covered if o.get("weight") == "medium"]

            if high:
                lines.append("**High Weight Objectives:**")
                for obj in high:
                    lines.append(
                        f"- ✅ **{obj.get('id')}** — {obj.get('objective')} "
                        f"*({obj.get('component', '')})*"
                    )
                lines.append("")

            if medium:
                lines.append("**Medium Weight Objectives:**")
                for obj in medium:
                    lines.append(
                        f"- ✅ **{obj.get('id')}** — {obj.get('objective')} "
                        f"*({obj.get('component', '')})*"
                    )
                lines.append("")

        # Study plan
        if study_plan:
            lines.append("\n### Your Prioritised Study Plan\n")
            lines.append(
                "> Focus on 🔴 High priority items first — "
                "they carry the most exam weight.\n"
            )

            high_items = [s for s in study_plan if "High" in s.get("priority", "")]
            medium_items = [s for s in study_plan if "Medium" in s.get("priority", "")]

            if high_items:
                lines.append("**🔴 High Priority — Study First:**")
                for item in high_items[:6]:
                    lines.append(
                        f"- **[{item.get('exam')}]** {item.get('objective')}\n"
                        f"  - {item.get('action')}"
                    )
                lines.append("")

            if medium_items:
                lines.append("**🟡 Medium Priority — Study After High:**")
                for item in medium_items[:4]:
                    lines.append(
                        f"- **[{item.get('exam')}]** {item.get('objective')}\n"
                        f"  - {item.get('action')}"
                    )
                lines.append("")

        # GIDEON integration
        if gideon_topics:
            lines.append("\n### Practice with GIDEON 🎯\n")
            lines.append(
                "> Use [GIDEON](https://github.com/siriusbkid-commits/gideon-pbq-generator) "
                "to generate PBQ practice questions on these topics:\n"
            )
            for topic in gideon_topics:
                lines.append(f"- 🎯 {topic}")
            lines.append("")
            lines.append(
                "> 💡 **Tip:** Generate a PBQ for each topic immediately after "
                "implementing it in Azure or CyberArk. "
                "The combination of doing + testing is the fastest path to exam success.\n"
            )

        # SC-300 exam tips
        sc300_tips = self.sc300_objectives.get("exam_tips", [])
        cyberark_tips = self.cyberark_objectives.get("exam_tips", [])

        if sc300_tips or cyberark_tips:
            lines.append("\n### Exam Tips\n")

            if sc300_tips:
                lines.append("**SC-300 Tips:**")
                for tip in sc300_tips[:4]:
                    lines.append(f"- 💡 {tip}")
                lines.append("")

            if cyberark_tips:
                lines.append("**CyberArk Defender Tips:**")
                for tip in cyberark_tips[:4]:
                    lines.append(f"- 💡 {tip}")
                lines.append("")

        lines.append("\n### Teaching Summary Exam Objectives\n")
        for obj in self.exam_objectives():
            lines.append(f"- 📚 {obj}")

        return "\n".join(lines)

    # --------------------------------------------------------
    # EXAM OBJECTIVES
    # --------------------------------------------------------

    def exam_objectives(self) -> List[str]:
        return [
            "SC-300: All identity governance domains covered",
            "SC-300: Implement an identity management solution",
            "SC-300: Implement authentication and access management",
            "SC-300: Plan and implement an identity governance strategy",
            "CyberArk Defender: PAM fundamentals and solution architecture",
            "CyberArk Defender: Vault, CPM, PSM and PVWA administration",
        ]