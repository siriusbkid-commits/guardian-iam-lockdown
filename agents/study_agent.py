# ============================================================
# GUARDIAN — IAM Lockdown Template
# agents/study_agent.py — Study Mode Agent
#
# PURPOSE:
# Generates focused study guides for individual SC-300 and
# CyberArk Defender exam objectives.
#
# The student picks one objective at a time and GUARDIAN
# generates a deep dive study guide covering:
# - Plain English explanation
# - Why it matters for the exam
# - Step by step Azure portal implementation
# - PowerShell snippet where applicable
# - Common exam traps
# - GIDEON practice topics
#
# Each guide is saved to study_output/ as a markdown file
# so students build up a personal study library over time.
#
# SECURITY GUARDRAILS:
# - All inputs sanitised before passing to LLM
# - All LLM outputs validated before presenting to user
# - OWASP LLM Top 10 protections applied
#
# SUPPORTED EXAMS:
# - SC-300 Microsoft Identity and Access Administrator
# - CyberArk Defender PAM
# ============================================================

import re
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent


# ============================================================
# CONSTANTS
# ============================================================

STUDY_OUTPUT_DIR = "study_output"

EXAM_SC300 = "sc300"
EXAM_CYBERARK = "cyberark"

DANGEROUS_PATTERNS = [
    r"disable.*security",
    r"bypass.*mfa",
    r"ignore.*policy",
    r"remove.*audit",
]


# ============================================================
# STUDY AGENT
# ============================================================

class StudyAgent(BaseAgent):
    """
    Generates focused study guides for individual exam objectives.
    Student picks one objective at a time for a deep dive session.
    """

    def __init__(self, llm_client):
        super().__init__(llm_client, context={})
        self.sc300_data = self._load_objectives("sc300_objectives.json")
        self.cyberark_data = self._load_objectives("cyberark_objectives.json")
        self.selected_exam = None
        self.selected_domain = None
        self.selected_objective = None

    # --------------------------------------------------------
    # OBJECTIVES LOADER
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
            print(f"[GUARDIAN] Could not load {filename}: {e}")
            return {}

    # --------------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        """
        Main study mode flow.
        Student selects exam → domain → objective → generates guide.
        """
        print("\n" + "=" * 50)
        print(" GUARDIAN — Study Mode")
        print("=" * 50)
        print("\nGenerate a focused study guide for any SC-300")
        print("or CyberArk Defender exam objective.\n")

        # Step 1 — Select exam
        exam = self._select_exam()
        if not exam:
            return {}

        # Step 2 — Select domain
        domain = self._select_domain(exam)
        if not domain:
            return {}

        # Step 3 — Select objective
        objective = self._select_objective(domain)
        if not objective:
            return {}

        self.selected_exam = exam
        self.selected_domain = domain
        self.selected_objective = objective

        # Step 4 — Generate study guide
        print(f"\n[GUARDIAN] Generating study guide for:")
        print(f"  {objective.get('id')} — {objective.get('objective')}")
        print("[GUARDIAN] This may take a minute or two...\n")

        guide_content = self._generate_guide(exam, domain, objective)

        # Step 5 — Save to file
        output_path = self._save_guide(exam, objective, guide_content)

        self.result = {
            "exam": exam.get("exam"),
            "domain": domain.get("name"),
            "objective_id": objective.get("id"),
            "objective": objective.get("objective"),
            "output_path": output_path
        }

        return self.result

    # --------------------------------------------------------
    # MENU SYSTEM
    # --------------------------------------------------------

    def _select_exam(self) -> Optional[Dict[str, Any]]:
        """Let student select which exam to study."""
        print("Which exam are you studying for?\n")
        print("  1. SC-300 — Microsoft Identity and Access Administrator")
        print("  2. CyberArk Defender — PAM")
        print("  3. Back to main menu\n")

        while True:
            choice = input("Select (1/2/3): ").strip()
            if choice == "1":
                return self.sc300_data
            elif choice == "2":
                return self.cyberark_data
            elif choice == "3":
                return None
            print("Please enter 1, 2 or 3.")

    def _select_domain(self, exam: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Let student select which domain to study."""
        domains = exam.get("domains", [])
        if not domains:
            print("[GUARDIAN] No domains found in objectives file.")
            return None

        print(f"\n{exam.get('exam_name', 'Exam')} — Select a domain:\n")
        for i, domain in enumerate(domains, start=1):
            print(f"  {i}. {domain.get('name')} ({domain.get('weight', '')})")
        print(f"  {len(domains) + 1}. Back\n")

        while True:
            choice = input("Select domain: ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(domains):
                    return domains[idx - 1]
                elif idx == len(domains) + 1:
                    return None
            print(f"Please enter a number between 1 and {len(domains) + 1}.")

    def _select_objective(self, domain: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Let student select which objective to study."""
        objectives = domain.get("objectives", [])
        if not objectives:
            print("[GUARDIAN] No objectives found in this domain.")
            return None

        print(f"\n{domain.get('name')} — Select an objective:\n")
        for i, obj in enumerate(objectives, start=1):
            weight_icon = "🔴" if obj.get("sc300_weight") == "high" or obj.get("defender_weight") == "high" else "🟡"
            print(f"  {i}. {weight_icon} {obj.get('id')} — {obj.get('objective')}")
        print(f"  {len(objectives) + 1}. Back\n")

        print("🔴 High priority  🟡 Medium priority\n")

        while True:
            choice = input("Select objective: ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(objectives):
                    return objectives[idx - 1]
                elif idx == len(objectives) + 1:
                    return None
            print(f"Please enter a number between 1 and {len(objectives) + 1}.")

    # --------------------------------------------------------
    # GUIDE GENERATOR
    # --------------------------------------------------------

    def _generate_guide(
        self,
        exam: Dict[str, Any],
        domain: Dict[str, Any],
        objective: Dict[str, Any]
    ) -> str:
        """Generate a focused study guide for the selected objective."""
        prompt = self._build_prompt(exam, domain, objective)
        safe_prompt = self._sanitise_input(prompt)
        raw = self.call_llm(safe_prompt)
        return self._validate_output(raw, objective)

    def _build_prompt(
        self,
        exam: Dict[str, Any],
        domain: Dict[str, Any],
        objective: Dict[str, Any]
    ) -> str:
        """Build a focused study guide prompt for one objective."""

        topics_text = "\n".join([f"- {t}" for t in objective.get("topics", [])])
        portal_path = objective.get("azure_portal_path", "Azure Portal > Microsoft Entra ID")
        exam_name = exam.get("exam_name", "SC-300")
        weight = objective.get("sc300_weight", objective.get("defender_weight", "medium"))

        return (
            f"You are a {exam_name} certified expert and teacher.\n\n"
            f"Generate a focused study guide for this exam objective:\n"
            f"Objective: {objective.get('id')} — {objective.get('objective')}\n"
            f"Domain: {domain.get('name')}\n"
            f"Exam weight: {weight}\n\n"
            f"Topics covered by this objective:\n{topics_text}\n\n"
            f"Azure Portal path: {portal_path}\n\n"
            "STRICT RULES:\n"
            "- Plain text only. No HTML.\n"
            "- Never recommend disabling security features.\n"
            "- Never recommend bypassing MFA or Conditional Access.\n"
            "- Always recommend least privilege.\n"
            "- Be specific and practical — students need to DO this, not just read about it.\n\n"
            "Write these FIVE sections using EXACTLY these headings:\n\n"
            "WHAT IS IT\n"
            "Explain this objective in plain English. Use an analogy if helpful. "
            "2-3 sentences maximum.\n\n"
            "WHY IT MATTERS FOR THE EXAM\n"
            "Explain specifically how this objective is tested. "
            "What types of questions appear? Scenario based? Configuration steps? "
            "2-3 sentences.\n\n"
            "HOW TO IMPLEMENT IT\n"
            "Step by step implementation guide. "
            "Be specific — include exact menu paths in the Azure portal. "
            "Number each step. Include at least 5 steps.\n\n"
            "COMMON EXAM TRAPS\n"
            "List 3-5 common mistakes students make on this objective. "
            "What do people get wrong? What are the tricky scenarios?\n\n"
            "PRACTICE WITH GIDEON\n"
            "List 3-5 specific PBQ topics a student should practice in GIDEON "
            "to test their understanding of this objective.\n\n"
            "Output plain text only. Use the section headings exactly as written above."
        )

    # --------------------------------------------------------
    # SECURE LLM CALL
    # --------------------------------------------------------

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

    def _validate_output(self, output: str, objective: Dict[str, Any]) -> str:
        """OWASP LLM02: Insecure Output Handling."""
        if not output or output.startswith("ERROR"):
            return self._fallback_content(objective)

        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, output, re.IGNORECASE):
                print(f"[GUARDIAN] ⚠️ Security validation flagged content.")
                return self._fallback_content(objective)

        return output

    def _fallback_content(self, objective: Dict[str, Any]) -> str:
        """Safe fallback if LLM fails."""
        return (
            f"WHAT IS IT\n"
            f"{objective.get('objective')} is a core SC-300 exam objective "
            f"covering identity and access management in Microsoft Entra ID.\n\n"
            f"WHY IT MATTERS FOR THE EXAM\n"
            f"This objective is tested through scenario-based questions "
            f"requiring you to choose the correct configuration approach.\n\n"
            f"HOW TO IMPLEMENT IT\n"
            f"1. Navigate to: {objective.get('azure_portal_path', 'Azure Portal > Microsoft Entra ID')}\n"
            f"2. Review the topics listed in sc300_objectives.json for this objective.\n"
            f"3. Practice each topic in a lab environment.\n\n"
            f"COMMON EXAM TRAPS\n"
            f"- Read each question carefully — small differences in wording matter.\n"
            f"- Know the difference between similar features.\n"
            f"- Understand when to use each configuration option.\n\n"
            f"PRACTICE WITH GIDEON\n"
            f"- Generate a PBQ on: {objective.get('objective')}\n"
            f"- Practice scenario questions on this topic.\n"
        )

    # --------------------------------------------------------
    # FILE SAVER
    # --------------------------------------------------------

    def _save_guide(
        self,
        exam: Dict[str, Any],
        objective: Dict[str, Any],
        content: str
    ) -> str:
        """Save the study guide as a markdown file."""
        os.makedirs(STUDY_OUTPUT_DIR, exist_ok=True)

        exam_prefix = "sc300" if "SC-300" in exam.get("exam", "") else "cyberark"
        obj_id = objective.get("id", "").replace(".", "_")
        obj_name = objective.get("objective", "")[:30].lower()
        obj_name = re.sub(r"[^a-z0-9]+", "_", obj_name).strip("_")

        filename = f"{exam_prefix}_{obj_id}_{obj_name}.md"
        filepath = os.path.join(STUDY_OUTPUT_DIR, filename)

        # Build full markdown document
        full_content = self._build_markdown(exam, objective, content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        return filepath

    def _build_markdown(
        self,
        exam: Dict[str, Any],
        objective: Dict[str, Any],
        content: str
    ) -> str:
        """Build the full markdown study guide document."""
        timestamp = datetime.now().strftime("%d %B %Y")
        topics = objective.get("topics", [])
        portal_path = objective.get("azure_portal_path", "")
        weight = objective.get("sc300_weight", objective.get("defender_weight", "medium"))
        weight_icon = "🔴 High" if weight == "high" else "🟡 Medium"

        lines = [
            f"# Study Guide: {objective.get('id')} — {objective.get('objective')}\n",
            f"**Exam:** {exam.get('exam_name')}\n",
            f"**Generated:** {timestamp}\n",
            f"**Exam Weight:** {weight_icon}\n",
            f"**Azure Portal Path:** `{portal_path}`\n",
            "\n---\n",
            "## Topics Covered\n"
        ]

        for topic in topics:
            lines.append(f"- {topic}")

        lines.append("\n---\n")
        lines.append(content)
        lines.append("\n---\n")
        lines.append("## Resources\n")
        lines.append(
            f"- 📚 **Official Microsoft Docs:** "
            f"https://learn.microsoft.com/credentials/certifications/exams/sc-300\n"
        )
        lines.append(
            f"- 🎯 **Practice with GIDEON:** "
            f"https://github.com/siriusbkid-commits/gideon-pbq-generator\n"
        )
        lines.append(
            f"- 🛡️ **GUARDIAN:** "
            f"https://github.com/siriusbkid-commits/guardian-iam-lockdown\n"
        )
        lines.append("\n---\n")
        lines.append(
            "> ⚠️ *This study guide was generated by GUARDIAN. "
            "Always validate against the official Microsoft Learn documentation.*\n"
        )

        return "\n".join(lines)

    # --------------------------------------------------------
    # REQUIRED BaseAgent implementations
    # --------------------------------------------------------

    def to_markdown(self) -> str:
        return ""

    def exam_objectives(self) -> List[str]:
        return []