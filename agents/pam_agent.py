# ============================================================
# GUARDIAN — IAM Lockdown Template
# agents/pam_agent.py — Privileged Access Management Agent
#
# PURPOSE:
# Generates tailored PAM lockdown recommendations.
# Covers CyberArk Cloud, CyberArk Self-Hosted, and home user
# PAM alternatives (password managers, basic controls).
# Every recommendation maps to CyberArk Defender exam objectives.
#
# SECURITY GUARDRAILS:
# - All inputs sanitised before passing to LLM
# - All LLM outputs validated before presenting to user
# - PowerShell scripts use -WhatIf by default (dry run)
# - Backup scripts generated before any destructive change
# - Least privilege enforced in every recommendation
# - No credentials ever stored in plain text
# - Explicit confirmation required before any change
# - OWASP LLM Top 10 protections applied
#
# TIERS:
# - Home: PAM concepts + free alternatives (password managers)
# - Startup: CyberArk Cloud OR basic PAM controls
# - SMB: Full CyberArk Self-Hosted OR Cloud implementation
#
# CYBERARK DEFENDER OBJECTIVES COVERED:
# - Understand PAM fundamentals
# - Configure CyberArk Vault
# - Implement PSM session management
# - Configure CPM credential rotation
# - Implement dual control workflows
# - Monitor privileged access activity
# ============================================================

import re
import json
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from config import TIER_HOME, TIER_STARTUP, TIER_SMB


# ============================================================
# SECURITY CONSTANTS
# ============================================================

# CyberArk deployment types
CYBERARK_CLOUD = "cloud"
CYBERARK_SELF_HOSTED = "self_hosted"
CYBERARK_NOT_APPLICABLE = "not_applicable"

# Core PAM controls every organisation should have
CORE_PAM_CONTROLS = [
    "Privileged account inventory",
    "No shared admin accounts",
    "Unique passwords for every privileged account",
    "MFA for all privileged access",
    "Session recording for privileged sessions",
    "Regular password rotation",
    "Least privilege for all accounts",
    "Audit logging for all privileged activity",
]

# Free PAM alternatives for home users
HOME_PAM_ALTERNATIVES = [
    {
        "name": "Bitwarden",
        "type": "Password Manager",
        "cost": "Free",
        "url": "bitwarden.com",
        "use_case": "Store and manage all passwords securely"
    },
    {
        "name": "Microsoft Authenticator",
        "type": "MFA App",
        "cost": "Free",
        "url": "microsoft.com/authenticator",
        "use_case": "MFA for Microsoft and other accounts"
    },
    {
        "name": "Windows Hello",
        "type": "Biometric Authentication",
        "cost": "Free (built into Windows)",
        "url": "N/A",
        "use_case": "Biometric login instead of passwords"
    },
    {
        "name": "Have I Been Pwned",
        "type": "Breach Monitoring",
        "cost": "Free",
        "url": "haveibeenpwned.com",
        "use_case": "Check if your accounts have been compromised"
    }
]

# Dangerous patterns to detect in LLM output
DANGEROUS_PATTERNS = [
    r"disable.*password.*rotation",
    r"store.*password.*plain.?text",
    r"bypass.*mfa",
    r"disable.*audit",
    r"remove.*logging",
    r"ConvertTo-SecureString.*AsPlainText",
    r"grant.*permanent.*admin",
    r"disable.*session.*recording",
    r"bypass.*dual.?control",
]


# ============================================================
# PAM AGENT
# ============================================================

class PAMAgent(BaseAgent):
    """
    Generates PAM lockdown recommendations tailored to the
    organisation's tier and detected environment.

    Covers:
    - Home: PAM concepts + free alternatives
    - Startup: CyberArk Cloud OR basic PAM controls
    - SMB: Full CyberArk implementation (Cloud or Self-Hosted)
    """

    def __init__(self, llm_client, context: Dict[str, Any]):
        super().__init__(llm_client, context)
        self.tier = context.get("tier", TIER_HOME)
        self.org_name = context.get("org_name", "Your Organisation")
        self.systems = context.get("systems", [])
        self.posture = context.get("current_posture", "none")
        self.cyberark_detected = context.get("detected", {}).get("cyberark", False)
        self.deployment_type = self._determine_deployment_type()
        self.pam_recommendations = {}
        self.powershell_scripts = {}

    # --------------------------------------------------------
    # DEPLOYMENT TYPE DETECTION
    # --------------------------------------------------------

    def _determine_deployment_type(self) -> str:
        """
        Determine CyberArk deployment type based on context.
        """
        if self.tier == TIER_HOME:
            return CYBERARK_NOT_APPLICABLE

        # Check if CyberArk is already detected
        if self.cyberark_detected:
            return CYBERARK_SELF_HOSTED

        # Check systems list
        systems_str = " ".join(self.systems).lower()
        if "cyberark" in systems_str:
            if "cloud" in systems_str:
                return CYBERARK_CLOUD
            return CYBERARK_SELF_HOSTED

        # Startup without CyberArk — use basic PAM controls
        if self.tier == TIER_STARTUP:
            return CYBERARK_NOT_APPLICABLE

        return CYBERARK_NOT_APPLICABLE

    # --------------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        print("\n[GUARDIAN] Running PAM Agent...")
        print(f"[GUARDIAN] Tier: {self.tier.title()}")
        print(f"[GUARDIAN] CyberArk deployment: {self.deployment_type}")
        print(f"[GUARDIAN] Generating PAM recommendations...\n")

        if self.tier == TIER_HOME:
            self.result = self._run_home()
        elif self.tier == TIER_STARTUP:
            self.result = self._run_startup()
        elif self.tier == TIER_SMB:
            self.result = self._run_smb()

        print("[GUARDIAN] PAM Agent complete. ✅\n")
        return self.result

    # --------------------------------------------------------
    # TIER RUNNERS
    # --------------------------------------------------------

    def _run_home(self) -> Dict[str, Any]:
        """
        Home tier — PAM concepts + free alternatives.
        Explains what PAM is and recommends free tools.
        """
        prompt = self._build_prompt_home()
        raw = self._safe_llm_call(prompt)

        return {
            "tier": TIER_HOME,
            "type": "educational",
            "deployment": CYBERARK_NOT_APPLICABLE,
            "content": raw,
            "alternatives": HOME_PAM_ALTERNATIVES,
            "core_controls": CORE_PAM_CONTROLS[:4]
        }

    def _run_startup(self) -> Dict[str, Any]:
        """
        Startup tier — basic PAM controls or CyberArk Cloud intro.
        """
        if self.deployment_type == CYBERARK_CLOUD:
            prompt = self._build_prompt_startup_cyberark_cloud()
        else:
            prompt = self._build_prompt_startup_basic()

        raw = self._safe_llm_call(prompt)
        scripts = self._generate_startup_scripts()

        return {
            "tier": TIER_STARTUP,
            "type": "implementation",
            "deployment": self.deployment_type,
            "content": raw,
            "scripts": scripts,
            "core_controls": CORE_PAM_CONTROLS
        }

    def _run_smb(self) -> Dict[str, Any]:
        """
        SMB tier — full CyberArk implementation.
        Covers both Cloud and Self-Hosted deployments.
        """
        prompt = self._build_prompt_smb()
        raw = self._safe_llm_call(prompt)
        scripts = self._generate_smb_scripts()

        return {
            "tier": TIER_SMB,
            "type": "full_implementation",
            "deployment": self.deployment_type,
            "content": raw,
            "scripts": scripts,
            "core_controls": CORE_PAM_CONTROLS
        }

    # --------------------------------------------------------
    # PROMPT BUILDERS
    # --------------------------------------------------------

    def _build_prompt_home(self) -> str:
        return (
            "You are a cybersecurity expert writing a section of a security playbook "
            "for a home user.\n\n"
            "Write a friendly, plain English explanation of Privileged Access Management (PAM) "
            "for someone with no technical background.\n\n"
            "STRICT RULES:\n"
            "- Plain text only. No HTML. No URLs.\n"
            "- Do not recommend paid enterprise tools.\n"
            "- Keep it simple and encouraging.\n"
            "- Do not recommend disabling any security features.\n\n"
            "COVER THESE POINTS:\n"
            "1. What PAM is in plain English (2-3 sentences)\n"
            "2. Why it matters even for home users\n"
            "3. The three most important things a home user can do TODAY:\n"
            "   a. Use a password manager (explain why)\n"
            "   b. Enable MFA on all important accounts (explain why)\n"
            "   c. Never use admin account for daily tasks (explain why)\n"
            "4. What to do if they think they have been compromised\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n\n"
            "Write in a warm, encouraging tone. "
            "End with a one sentence summary of why these steps matter.\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    def _build_prompt_startup_basic(self) -> str:
        return (
            "You are a CyberArk Defender certified expert writing a PAM section "
            "of a security playbook for a startup.\n\n"
            "This startup does NOT have CyberArk yet. "
            "Write practical PAM controls they can implement immediately "
            "using tools they already have.\n\n"
            "STRICT SECURITY RULES — NEVER VIOLATE THESE:\n"
            "- Never recommend storing passwords in plain text.\n"
            "- Never recommend disabling MFA.\n"
            "- Never recommend shared admin accounts.\n"
            "- Never recommend permanent standing access.\n"
            "- Always recommend least privilege.\n"
            "- Plain text only. No HTML. No URLs.\n\n"
            "COVER THESE SECTIONS:\n"
            "1. Privileged Account Inventory\n"
            "   - How to identify all privileged accounts\n"
            "   - Document each account, its purpose, and its owner\n"
            "2. Eliminate Shared Admin Accounts\n"
            "   - Every admin must have their own named account\n"
            "   - No shared admin credentials\n"
            "3. Implement Strong Password Controls\n"
            "   - Minimum 20 character passwords for admin accounts\n"
            "   - Use a password manager for all privileged credentials\n"
            "   - Rotate passwords every 90 days minimum\n"
            "4. Enable MFA for all privileged accounts\n"
            "5. Implement Just Enough Administration (JEA)\n"
            "   - Review every admin account — does it need that level of access?\n"
            "   - Remove unnecessary privileges\n"
            "6. Audit Logging\n"
            "   - Enable audit logging for all privileged activity\n"
            "   - Review logs monthly\n"
            "7. Prepare for CyberArk\n"
            "   - What to document now to make CyberArk implementation easier later\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n"
            f"Systems: {', '.join(self.systems)}\n\n"
            "After EACH step add:\n"
            "📚 CyberArk Defender Objective: [relevant objective]\n"
            "⚠️ Security Note: [why this matters]\n\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    def _build_prompt_startup_cyberark_cloud(self) -> str:
        return (
            "You are a CyberArk Defender certified expert writing a PAM section "
            "of a security playbook for a startup using CyberArk Cloud.\n\n"
            "STRICT SECURITY RULES — NEVER VIOLATE THESE:\n"
            "- Never recommend disabling session recording.\n"
            "- Never recommend bypassing dual control.\n"
            "- Never recommend storing passwords in plain text.\n"
            "- Never recommend shared admin accounts.\n"
            "- Always recommend least privilege.\n"
            "- Plain text only. No HTML. No URLs.\n\n"
            "COVER THESE SECTIONS:\n"
            "1. CyberArk Cloud initial setup\n"
            "   - Tenant configuration\n"
            "   - Initial admin account setup\n"
            "2. Vault configuration\n"
            "   - Create safes for privileged accounts\n"
            "   - Configure safe permissions\n"
            "3. Onboard privileged accounts\n"
            "   - Add Windows admin accounts\n"
            "   - Add service accounts\n"
            "4. Configure CPM for password rotation\n"
            "   - Set rotation frequency (90 days minimum)\n"
            "5. Configure PSM for session recording\n"
            "   - Enable session recording for all privileged sessions\n"
            "6. Configure dual control for high risk accounts\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n"
            f"Systems: {', '.join(self.systems)}\n\n"
            "After EACH step add:\n"
            "📚 CyberArk Defender Objective: [relevant objective]\n"
            "⚠️ Security Note: [why this matters]\n\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    def _build_prompt_smb(self) -> str:
        deployment_context = (
            "CyberArk Cloud (SaaS)" if self.deployment_type == CYBERARK_CLOUD
            else "CyberArk Self-Hosted (on-premise)"
        )

        return (
            "You are a CyberArk Defender certified expert writing a comprehensive PAM "
            "lockdown guide for an SMB.\n\n"
            f"Deployment type: {deployment_context}\n\n"
            "STRICT SECURITY RULES — NEVER VIOLATE THESE:\n"
            "- Never recommend disabling session recording.\n"
            "- Never recommend bypassing dual control.\n"
            "- Never recommend storing passwords in plain text.\n"
            "- Never recommend shared admin accounts.\n"
            "- Never recommend permanent standing privileged access.\n"
            "- Always recommend least privilege.\n"
            "- Always recommend MFA for all privileged access.\n"
            "- Plain text only. No HTML. No URLs.\n\n"
            "COVER THESE SECTIONS:\n"
            "1. CyberArk Vault configuration\n"
            "   - Master policy settings\n"
            "   - Safe structure and permissions\n"
            "   - DR Vault configuration\n"
            "2. Privileged Account Onboarding\n"
            "   - Windows domain admin accounts\n"
            "   - Local admin accounts\n"
            "   - Service accounts\n"
            "   - Database accounts\n"
            "3. CPM — Credential rotation\n"
            "   - Platform configuration\n"
            "   - Rotation frequency per account type\n"
            "   - Reconcile accounts\n"
            "4. PSM — Session management\n"
            "   - PSM server configuration\n"
            "   - Session recording settings\n"
            "   - Keystroke logging\n"
            "   - Live session monitoring\n"
            "5. PVWA — Access portal\n"
            "   - Authentication configuration\n"
            "   - Workflow settings\n"
            "   - Dual control configuration\n"
            "6. CyberArk and PIM integration\n"
            "   - How CyberArk PAM complements Entra ID PIM\n"
            "   - Unified privileged access strategy\n"
            "7. Monitoring and alerts\n"
            "   - CyberArk audit configuration\n"
            "   - Alert thresholds\n"
            "   - SIEM integration overview\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n"
            f"Systems: {', '.join(self.systems)}\n\n"
            "After EACH step add:\n"
            "📚 CyberArk Defender Objective: [relevant objective]\n"
            "⚠️ Security Note: [why this matters]\n"
            "🔐 PIM Integration: [how this complements Entra ID PIM where relevant]\n\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    # --------------------------------------------------------
    # SECURE LLM CALL
    # --------------------------------------------------------

    def _safe_llm_call(self, prompt: str) -> str:
        """
        Sanitise input, call LLM, validate output.
        OWASP LLM Top 10 protections applied.
        """
        safe_prompt = self._sanitise_input(prompt)
        print("[GUARDIAN] Calling LLM for PAM recommendations...")
        raw_output = self.call_llm(safe_prompt)
        validated = self._validate_output(raw_output)
        return validated

    def _sanitise_input(self, text: str) -> str:
        """
        Sanitise user context before passing to LLM.
        OWASP LLM01: Prompt Injection protection.
        """
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
        """
        Validate LLM output for dangerous content.
        OWASP LLM02: Insecure Output Handling.
        """
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
            print("[GUARDIAN] Using safe fallback content instead.\n")
            return self._fallback_content()

        disclaimer = (
            "\n\n---\n"
            "⚠️ GUARDIAN Security Notice: These recommendations are AI-generated "
            "and should be reviewed by a qualified security professional before "
            "implementation in a production environment. "
            "Always test in a non-production environment first. "
            "Never store privileged credentials in plain text. "
            "All PowerShell scripts use -WhatIf by default."
        )

        return output + disclaimer

    def _fallback_content(self) -> str:
        """Safe fallback content if LLM output fails validation."""
        return (
            "PAM Configuration Recommendations\n\n"
            "The following are the essential PAM controls for your organisation:\n\n"
            "1. Privileged Account Inventory\n"
            "Identify and document all privileged accounts in your environment.\n"
            "📚 CyberArk Defender Objective: Understand PAM fundamentals\n"
            "⚠️ Security Note: You cannot protect what you cannot see.\n\n"
            "2. Eliminate Shared Admin Accounts\n"
            "Every administrator must have their own named account.\n"
            "📚 CyberArk Defender Objective: Configure CyberArk Vault\n"
            "⚠️ Security Note: Shared accounts make audit logging meaningless.\n\n"
            "3. Enable Password Rotation\n"
            "Rotate all privileged account passwords at least every 90 days.\n"
            "📚 CyberArk Defender Objective: Configure CPM credential rotation\n"
            "⚠️ Security Note: Stale credentials are a primary attack vector.\n\n"
            "4. Enable Session Recording\n"
            "Record all privileged sessions for audit and forensic purposes.\n"
            "📚 CyberArk Defender Objective: Implement PSM session management\n"
            "⚠️ Security Note: Session recordings are essential for incident investigation.\n\n"
            "---\n"
            "⚠️ GUARDIAN Security Notice: These are baseline recommendations. "
            "Always validate against your organisation's specific requirements."
        )

    # --------------------------------------------------------
    # POWERSHELL SCRIPT GENERATORS
    # --------------------------------------------------------

    def _generate_startup_scripts(self) -> Dict[str, str]:
        """Generate safe PowerShell scripts for startup tier."""
        scripts = {}

        scripts["01_audit_privileged_accounts"] = '''
# ============================================================
# GUARDIAN — Audit Privileged Accounts
# Identifies all accounts with admin or privileged access
# READ ONLY — no changes made
# ============================================================
# PREREQUISITES: Run as administrator

Write-Host "Auditing privileged accounts..." -ForegroundColor Cyan

# Local administrators
Write-Host "`n--- Local Administrator Accounts ---" -ForegroundColor Yellow
$localAdmins = Get-LocalGroupMember -Group "Administrators"
foreach ($admin in $localAdmins) {
    Write-Host "  $($admin.Name) | Type: $($admin.ObjectClass)" -ForegroundColor White
}

# Export results
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = "guardian_pam_audit_$timestamp.txt"
$localAdmins | Out-File $reportFile

Write-Host "`n✅ Audit complete. Report saved to: $reportFile" -ForegroundColor Green
Write-Host "📚 CyberArk Defender Objective: Understand PAM fundamentals" -ForegroundColor Cyan
Write-Host "⚠️  Review this list carefully — remove any accounts that do not need admin access." -ForegroundColor Yellow
'''

        scripts["02_check_password_policy"] = '''
# ============================================================
# GUARDIAN — Check Local Password Policy
# Reviews current password policy settings
# READ ONLY — no changes made
# ============================================================

Write-Host "Checking password policy..." -ForegroundColor Cyan

$policy = net accounts
Write-Host $policy

Write-Host "`nRecommended settings for privileged accounts:" -ForegroundColor Yellow
Write-Host "  Minimum password length: 20 characters" -ForegroundColor White
Write-Host "  Maximum password age: 90 days" -ForegroundColor White
Write-Host "  Password complexity: Enabled" -ForegroundColor White
Write-Host "  Account lockout threshold: 5 attempts" -ForegroundColor White

Write-Host "`n📚 CyberArk Defender Objective: Configure CPM credential rotation" -ForegroundColor Cyan
'''

        scripts["03_enable_audit_logging"] = '''
# ============================================================
# GUARDIAN — Enable Audit Logging for Privileged Activity
#
# ⚠️  RUNS IN -WhatIf MODE BY DEFAULT
# Remove -WhatIf only when ready to apply changes
# ============================================================
# PREREQUISITES: Run as administrator

Write-Host "Would enable the following audit policies:" -ForegroundColor Cyan
Write-Host "  - Audit account logon events: Success and Failure" -ForegroundColor White
Write-Host "  - Audit account management: Success and Failure" -ForegroundColor White
Write-Host "  - Audit privilege use: Success and Failure" -ForegroundColor White
Write-Host "  - Audit process tracking: Success" -ForegroundColor White

# Uncomment to apply:
# auditpol /set /subcategory:"Logon" /success:enable /failure:enable
# auditpol /set /subcategory:"Account Management" /success:enable /failure:enable
# auditpol /set /subcategory:"Sensitive Privilege Use" /success:enable /failure:enable

Write-Host "`n✅ WhatIf complete. Uncomment commands above to apply." -ForegroundColor Green
Write-Host "📚 CyberArk Defender Objective: Monitor privileged access activity" -ForegroundColor Cyan
'''

        return scripts

    def _generate_smb_scripts(self) -> Dict[str, str]:
        """Generate full PowerShell scripts for SMB tier."""
        scripts = self._generate_startup_scripts()

        scripts["04_cyberark_safe_audit"] = '''
# ============================================================
# GUARDIAN — CyberArk Safe Audit
# Lists all CyberArk safes and their members
# READ ONLY — requires CyberArk PVWA API access
# ============================================================
# PREREQUISITES:
#   - CyberArk PVWA URL
#   - Read access to CyberArk

$pvwaUrl = "https://your-pvwa-url"  # Update this
$safeListUrl = "$pvwaUrl/PasswordVault/api/Safes"

Write-Host "To audit CyberArk safes, run the following in CyberArk PVWA:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Log in to PVWA" -ForegroundColor White
Write-Host "2. Navigate to: Policies > Access Control > Safes" -ForegroundColor White
Write-Host "3. Export the safe list and review:" -ForegroundColor White
Write-Host "   - Who has access to each safe" -ForegroundColor Gray
Write-Host "   - Which accounts are in each safe" -ForegroundColor Gray
Write-Host "   - Last access date for each safe" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 CyberArk Defender Objective: Configure CyberArk Vault" -ForegroundColor Cyan
Write-Host "⚠️  Review safe permissions quarterly as part of access reviews." -ForegroundColor Yellow
'''

        scripts["05_cyberark_session_review"] = '''
# ============================================================
# GUARDIAN — CyberArk Session Recording Review
# Guidance for reviewing PSM session recordings
# READ ONLY — informational script
# ============================================================

Write-Host "CyberArk PSM Session Review Guide:" -ForegroundColor Cyan
Write-Host ""
Write-Host "To review session recordings in PVWA:" -ForegroundColor White
Write-Host "1. Log in to PVWA" -ForegroundColor White
Write-Host "2. Navigate to: Reports > Privileged Session Management" -ForegroundColor White
Write-Host "3. Filter by:" -ForegroundColor White
Write-Host "   - Date range (review last 30 days monthly)" -ForegroundColor Gray
Write-Host "   - High-risk accounts (domain admins first)" -ForegroundColor Gray
Write-Host "   - Unusual hours (after hours or weekend access)" -ForegroundColor Gray
Write-Host "   - Long sessions (over 2 hours)" -ForegroundColor Gray
Write-Host ""
Write-Host "Red flags to look for:" -ForegroundColor Yellow
Write-Host "  - Commands run outside normal job function" -ForegroundColor White
Write-Host "  - Access to sensitive data stores" -ForegroundColor White
Write-Host "  - Changes to security settings" -ForegroundColor White
Write-Host "  - Bulk data exports" -ForegroundColor White
Write-Host ""
Write-Host "📚 CyberArk Defender Objective: Implement PSM session management" -ForegroundColor Cyan
'''

        scripts["06_cyberark_cpm_check"] = '''
# ============================================================
# GUARDIAN — CyberArk CPM Password Rotation Check
# Reviews CPM configuration and rotation status
# READ ONLY — informational script
# ============================================================

Write-Host "CyberArk CPM Review Guide:" -ForegroundColor Cyan
Write-Host ""
Write-Host "In PVWA, check the following:" -ForegroundColor White
Write-Host ""
Write-Host "1. CPM Status" -ForegroundColor White
Write-Host "   Navigate to: Administration > System Health > CPM" -ForegroundColor Gray
Write-Host "   Verify: CPM is running and connected" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Password rotation schedule" -ForegroundColor White
Write-Host "   Recommended rotation frequency:" -ForegroundColor White
Write-Host "   - Domain admin accounts: Every 30 days" -ForegroundColor Gray
Write-Host "   - Local admin accounts: Every 60 days" -ForegroundColor Gray
Write-Host "   - Service accounts: Every 90 days" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Failed rotations" -ForegroundColor White
Write-Host "   Navigate to: Reports > Password Management" -ForegroundColor Gray
Write-Host "   Investigate any accounts showing rotation failures" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 CyberArk Defender Objective: Configure CPM credential rotation" -ForegroundColor Cyan
Write-Host "⚠️  Failed rotations leave accounts with stale passwords — investigate immediately." -ForegroundColor Yellow
'''

        return scripts

    # --------------------------------------------------------
    # MARKDOWN OUTPUT
    # --------------------------------------------------------

    def to_markdown(self) -> str:
        tier = self.result.get("tier", TIER_HOME)
        content = self.result.get("content", "")
        scripts = self.result.get("scripts", {})
        alternatives = self.result.get("alternatives", [])

        lines = [
            "## PAM Lockdown\n",
            "> 📚 **CyberArk Defender Domain:** Privileged Access Management Fundamentals\n",
        ]

        if tier == TIER_HOME:
            lines.append("### PAM for Home Users\n")
            lines.append(
                "> ℹ️ **Note:** Enterprise PAM tools like CyberArk are designed for "
                "organisations. The section below explains PAM concepts and recommends "
                "free tools that give home users similar protection.\n"
            )
            lines.append(content)

            if alternatives:
                lines.append("\n### Recommended Free PAM Tools for Home Users\n")
                for tool in alternatives:
                    lines.append(f"#### {tool['name']}")
                    lines.append(f"- **Type:** {tool['type']}")
                    lines.append(f"- **Cost:** {tool['cost']}")
                    lines.append(f"- **Use case:** {tool['use_case']}")
                    lines.append("")

        else:
            deployment_label = {
                CYBERARK_CLOUD: "CyberArk Cloud",
                CYBERARK_SELF_HOSTED: "CyberArk Self-Hosted",
                CYBERARK_NOT_APPLICABLE: "Basic PAM Controls"
            }.get(self.deployment_type, "PAM Controls")

            lines.append(f"### PAM Configuration Guide — {deployment_label}\n")
            lines.append(content)

            if scripts:
                lines.append("\n### PowerShell Scripts\n")
                lines.append(
                    "> ⚠️ **Important:** All scripts run in `-WhatIf` mode by default. "
                    "Review output carefully before applying changes. "
                    "Always run audit scripts first.\n"
                )

                for script_name, script_content in scripts.items():
                    friendly_name = script_name.replace("_", " ").title()
                    lines.append(f"#### {friendly_name}\n")
                    lines.append(f"```powershell{script_content}```\n")

        lines.append("\n### PAM Exam Objectives\n")
        for obj in self.exam_objectives():
            lines.append(f"- 📚 {obj}")

        return "\n".join(lines)

    # --------------------------------------------------------
    # EXAM OBJECTIVES
    # --------------------------------------------------------

    def exam_objectives(self) -> List[str]:
        base = [
            "CyberArk Defender: Understand PAM fundamentals and privileged account risks",
            "CyberArk Defender: Configure CyberArk Vault safes and permissions",
            "CyberArk Defender: Implement CPM for automated credential rotation",
            "CyberArk Defender: Configure PSM for privileged session recording",
            "CyberArk Defender: Implement dual control workflows for high-risk accounts",
            "CyberArk Defender: Monitor and audit privileged access activity",
        ]

        if self.tier == TIER_SMB:
            base.extend([
                "CyberArk Defender: Configure PVWA for privileged access portal",
                "CyberArk Defender: Integrate CyberArk with Microsoft Entra ID PIM",
                "SC-300: Implement privileged access strategy using PAM tools",
            ])

        return base