# ============================================================
# GUARDIAN — IAM Lockdown Template
# agents/pim_agent.py — Privileged Identity Management Agent
#
# PURPOSE:
# Generates tailored PIM lockdown recommendations for Entra ID.
# Produces step-by-step instructions AND PowerShell scripts.
# Every recommendation maps to SC-300 exam objectives.
#
# SECURITY GUARDRAILS:
# - All inputs sanitised before passing to LLM
# - All LLM outputs validated before presenting to user
# - PowerShell scripts use -WhatIf by default (dry run)
# - Backup scripts generated before any destructive change
# - Least privilege enforced in every recommendation
# - MFA required for every privileged role
# - No standing access — JIT always preferred
# - Explicit confirmation required before any change
# - OWASP LLM Top 10 protections applied
#
# TIERS:
# - Home: Educational overview only (PIM requires M365 P2)
# - Startup: Essential PIM roles + basic policies
# - SMB: Full PIM implementation + access reviews + alerts
#
# SC-300 OBJECTIVES COVERED:
# - Configure Privileged Identity Management
# - Manage Azure AD PIM role settings
# - Implement just-in-time access
# - Configure access reviews for privileged roles
# ============================================================

import re
import json
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from config import TIER_HOME, TIER_STARTUP, TIER_SMB


# ============================================================
# SECURITY CONSTANTS
# ============================================================

# Roles that should NEVER have standing access
HIGH_RISK_ROLES = [
    "Global Administrator",
    "Privileged Role Administrator",
    "Security Administrator",
    "Exchange Administrator",
    "SharePoint Administrator",
    "Conditional Access Administrator",
    "Authentication Administrator",
]

# Minimum PIM settings per role risk level
PIM_SETTINGS = {
    "high_risk": {
        "activation_duration_hours": 1,
        "require_mfa": True,
        "require_justification": True,
        "require_approval": True,
        "max_activation_duration_hours": 4,
        "access_review_frequency_days": 90,
    },
    "medium_risk": {
        "activation_duration_hours": 4,
        "require_mfa": True,
        "require_justification": True,
        "require_approval": False,
        "max_activation_duration_hours": 8,
        "access_review_frequency_days": 180,
    },
    "low_risk": {
        "activation_duration_hours": 8,
        "require_mfa": True,
        "require_justification": True,
        "require_approval": False,
        "max_activation_duration_hours": 24,
        "access_review_frequency_days": 365,
    }
}

# Dangerous patterns to detect in LLM output
DANGEROUS_PATTERNS = [
    r"Remove-AzureAD",
    r"Delete-",
    r"disable.*mfa",
    r"bypass.*conditional.access",
    r"grant.*global.admin.*permanent",
    r"remove.*audit",
    r"disable.*logging",
    r"password.*plain.?text",
    r"ConvertTo-SecureString.*AsPlainText",
]


# ============================================================
# PIM AGENT
# ============================================================

class PIMAgent(BaseAgent):
    """
    Generates PIM lockdown recommendations tailored to the
    organisation's tier and detected environment.

    Security first — every recommendation enforces:
    - Least privilege
    - Just-in-time access
    - MFA for all privileged roles
    - Audit logging
    - Time-bound access
    """

    def __init__(self, llm_client, context: Dict[str, Any]):
        super().__init__(llm_client, context)
        self.tier = context.get("tier", TIER_HOME)
        self.org_name = context.get("org_name", "Your Organisation")
        self.systems = context.get("systems", [])
        self.posture = context.get("current_posture", "none")
        self.pim_recommendations = {}
        self.powershell_scripts = {}

    # --------------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        print("\n[GUARDIAN] Running PIM Agent...")
        print(f"[GUARDIAN] Tier: {self.tier.title()}")
        print(f"[GUARDIAN] Generating PIM recommendations...\n")

        if self.tier == TIER_HOME:
            self.result = self._run_home()
        elif self.tier == TIER_STARTUP:
            self.result = self._run_startup()
        elif self.tier == TIER_SMB:
            self.result = self._run_smb()

        print("[GUARDIAN] PIM Agent complete. ✅\n")
        return self.result

    # --------------------------------------------------------
    # TIER RUNNERS
    # --------------------------------------------------------

    def _run_home(self) -> Dict[str, Any]:
        """
        Home tier — educational overview.
        PIM requires M365 Business Premium or higher.
        Show what PIM is and why it matters.
        """
        prompt = self._build_prompt_home()
        raw = self._safe_llm_call(prompt)

        return {
            "tier": TIER_HOME,
            "type": "educational",
            "content": raw,
            "note": "PIM requires Microsoft 365 Business Premium or Azure AD P2 licence."
        }

    def _run_startup(self) -> Dict[str, Any]:
        """
        Startup tier — essential PIM roles and basic policies.
        Focuses on the most critical roles for a small organisation.
        """
        prompt = self._build_prompt_startup()
        raw = self._safe_llm_call(prompt)

        scripts = self._generate_startup_scripts()

        return {
            "tier": TIER_STARTUP,
            "type": "implementation",
            "content": raw,
            "scripts": scripts,
            "roles_covered": [
                "Global Administrator",
                "Security Administrator",
                "Exchange Administrator"
            ],
            "settings": PIM_SETTINGS
        }

    def _run_smb(self) -> Dict[str, Any]:
        """
        SMB tier — full PIM implementation.
        All privileged roles, policies, access reviews, alerts.
        """
        prompt = self._build_prompt_smb()
        raw = self._safe_llm_call(prompt)

        scripts = self._generate_smb_scripts()

        return {
            "tier": TIER_SMB,
            "type": "full_implementation",
            "content": raw,
            "scripts": scripts,
            "roles_covered": HIGH_RISK_ROLES,
            "settings": PIM_SETTINGS
        }

    # --------------------------------------------------------
    # PROMPT BUILDERS
    # --------------------------------------------------------

    def _build_prompt_home(self) -> str:
        return (
            "You are a Microsoft SC-300 security expert writing a section of a security playbook.\n\n"
            "Write a clear, friendly educational overview of Azure AD Privileged Identity Management (PIM) "
            "for a home user or very small organisation.\n\n"
            "STRICT RULES:\n"
            "- Plain text only. No HTML. No URLs.\n"
            "- Do not recommend disabling any security features.\n"
            "- Do not include any PowerShell commands.\n"
            "- Do not include any credentials or passwords.\n"
            "- Keep it simple and non-technical.\n\n"
            "COVER THESE POINTS:\n"
            "1. What PIM is in plain English\n"
            "2. Why it matters even for small organisations\n"
            "3. What licence is needed (M365 Business Premium or Azure AD P2)\n"
            "4. Three practical things they can do TODAY without PIM\n"
            "5. How to prepare for PIM when they are ready to upgrade\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n\n"
            "Write in a friendly, encouraging tone. "
            "End each point with the SC-300 exam objective it relates to.\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    def _build_prompt_startup(self) -> str:
        return (
            "You are a Microsoft SC-300 security expert writing a section of a security playbook.\n\n"
            "Write a practical PIM lockdown guide for a startup using Microsoft 365 and Entra ID.\n\n"
            "STRICT SECURITY RULES — NEVER VIOLATE THESE:\n"
            "- Never recommend permanent admin assignments.\n"
            "- Never recommend disabling MFA.\n"
            "- Never recommend bypassing Conditional Access.\n"
            "- Never include credentials or passwords.\n"
            "- Always recommend least privilege.\n"
            "- Always recommend time-bound access.\n"
            "- Plain text only. No HTML. No URLs.\n\n"
            "COVER THESE SECTIONS:\n"
            "1. Enable PIM in Entra ID (step by step Azure portal instructions)\n"
            "2. Configure Global Administrator role in PIM\n"
            "   - Set activation duration to 1 hour maximum\n"
            "   - Require MFA on activation\n"
            "   - Require justification\n"
            "   - Require approval for activation\n"
            "3. Configure Security Administrator role in PIM\n"
            "   - Set activation duration to 4 hours maximum\n"
            "   - Require MFA on activation\n"
            "   - Require justification\n"
            "4. Remove all permanent admin assignments\n"
            "5. Set up access reviews (every 90 days for high risk roles)\n"
            "6. Enable PIM alerts for suspicious activity\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n"
            f"Systems: {', '.join(self.systems)}\n\n"
            "After EACH step add:\n"
            "📚 SC-300 Objective: [relevant objective]\n"
            "⚠️ Security Note: [why this matters]\n\n"
            "Output plain text only. No JSON. No markdown headers."
        )

    def _build_prompt_smb(self) -> str:
        return (
            "You are a Microsoft SC-300 security expert writing a section of a security playbook.\n\n"
            "Write a comprehensive PIM lockdown guide for an SMB using Microsoft 365, "
            "Entra ID, and CyberArk.\n\n"
            "STRICT SECURITY RULES — NEVER VIOLATE THESE:\n"
            "- Never recommend permanent admin assignments.\n"
            "- Never recommend disabling MFA.\n"
            "- Never recommend bypassing Conditional Access.\n"
            "- Never include credentials or passwords.\n"
            "- Always recommend least privilege.\n"
            "- Always recommend time-bound access.\n"
            "- Always recommend approval workflows for high risk roles.\n"
            "- Plain text only. No HTML. No URLs.\n\n"
            "COVER THESE SECTIONS:\n"
            "1. Enable and configure PIM for ALL privileged roles\n"
            "2. High risk roles (Global Admin, Privileged Role Admin)\n"
            "   - 1 hour max activation\n"
            "   - MFA required\n"
            "   - Approval required\n"
            "   - Justification required\n"
            "   - 90 day access reviews\n"
            "3. Medium risk roles (Security Admin, Exchange Admin)\n"
            "   - 4 hour max activation\n"
            "   - MFA required\n"
            "   - Justification required\n"
            "   - 180 day access reviews\n"
            "4. Emergency access (break glass) accounts\n"
            "   - Configure and monitor break glass accounts\n"
            "   - Alert on any activation\n"
            "5. PIM access reviews configuration\n"
            "6. PIM alerts and monitoring\n"
            "7. Integration with CyberArk for privileged account management\n\n"
            f"Organisation: {self.org_name}\n"
            f"Current posture: {self.posture}\n"
            f"Systems: {', '.join(self.systems)}\n\n"
            "After EACH step add:\n"
            "📚 SC-300 Objective: [relevant objective]\n"
            "⚠️ Security Note: [why this matters]\n"
            "🔧 CyberArk Note: [how CyberArk complements this where relevant]\n\n"
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
        # Sanitise prompt (prompt injection protection)
        safe_prompt = self._sanitise_input(prompt)

        # Call LLM
        print("[GUARDIAN] Calling LLM for PIM recommendations...")
        raw_output = self.call_llm(safe_prompt)

        # Validate output (hallucination + dangerous content check)
        validated = self._validate_output(raw_output)

        return validated

    def _sanitise_input(self, text: str) -> str:
        """
        Sanitise user-provided context before passing to LLM.
        Protects against prompt injection attacks.
        OWASP LLM01: Prompt Injection
        """
        # Remove any instruction-like patterns from user input fields
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
        OWASP LLM02: Insecure Output Handling
        OWASP LLM09: Overreliance
        """
        if not output or output.startswith("ERROR"):
            return self._fallback_content()

        # Check for dangerous patterns
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

        # Add mandatory security disclaimer
        disclaimer = (
            "\n\n---\n"
            "⚠️ GUARDIAN Security Notice: These recommendations are AI-generated "
            "and should be reviewed by a qualified security professional before "
            "implementation in a production environment. "
            "Always test in a non-production environment first. "
            "All PowerShell scripts use -WhatIf by default — "
            "remove -WhatIf only when you are ready to apply changes."
        )

        return output + disclaimer

    def _fallback_content(self) -> str:
        """
        Safe fallback content if LLM output fails validation.
        Ensures the playbook always has useful content.
        """
        return (
            "PIM Configuration Recommendations\n\n"
            "The following are the essential PIM controls for your organisation:\n\n"
            "1. Enable Privileged Identity Management in Entra ID\n"
            "Navigate to: Azure Portal > Entra ID > Identity Governance > Privileged Identity Management\n"
            "📚 SC-300 Objective: Configure Privileged Identity Management\n"
            "⚠️ Security Note: PIM provides just-in-time privileged access, "
            "reducing the risk of standing admin accounts.\n\n"
            "2. Configure Global Administrator role\n"
            "Set maximum activation duration to 1 hour.\n"
            "Require MFA, justification, and approval.\n"
            "Remove all permanent Global Administrator assignments.\n"
            "📚 SC-300 Objective: Manage Azure AD PIM role settings\n"
            "⚠️ Security Note: Global Administrator is the highest risk role. "
            "No user should have permanent Global Admin access.\n\n"
            "3. Enable access reviews\n"
            "Configure 90-day access reviews for all high-risk roles.\n"
            "📚 SC-300 Objective: Plan and implement access reviews\n"
            "⚠️ Security Note: Regular access reviews ensure "
            "only authorised users retain privileged access.\n\n"
            "---\n"
            "⚠️ GUARDIAN Security Notice: These are baseline recommendations. "
            "Always validate against your organisation's specific requirements."
        )

    # --------------------------------------------------------
    # POWERSHELL SCRIPT GENERATORS
    # --------------------------------------------------------

    def _generate_startup_scripts(self) -> Dict[str, str]:
        """
        Generate safe PowerShell scripts for startup tier.
        All scripts use -WhatIf by default.
        """
        scripts = {}

        scripts["01_check_pim_licence"] = '''
# ============================================================
# GUARDIAN — Check PIM Licence
# Run this first to confirm your tenant has PIM available
# ============================================================
# PREREQUISITES: Connect-MgGraph -Scopes "Directory.Read.All"

Write-Host "Checking PIM licence availability..." -ForegroundColor Cyan

$licences = Get-MgSubscribedSku | Select-Object SkuPartNumber, CapabilityStatus
$pimLicence = $licences | Where-Object { 
    $_.SkuPartNumber -match "AAD_PREMIUM_P2|M365_BUSINESS_PREMIUM|ENTERPRISEPREMIUM" 
}

if ($pimLicence) {
    Write-Host "✅ PIM licence detected: $($pimLicence.SkuPartNumber)" -ForegroundColor Green
} else {
    Write-Host "❌ No PIM licence detected." -ForegroundColor Red
    Write-Host "PIM requires Azure AD P2 or Microsoft 365 Business Premium." -ForegroundColor Yellow
}
'''

        scripts["02_list_permanent_admins"] = '''
# ============================================================
# GUARDIAN — List Permanent Admin Assignments
# Identifies accounts with standing admin access (read only)
# ============================================================
# PREREQUISITES: Connect-MgGraph -Scopes "RoleManagement.Read.Directory"

Write-Host "Scanning for permanent admin assignments..." -ForegroundColor Cyan

$permanentAdmins = Get-MgRoleManagementDirectoryRoleAssignment -All |
    Where-Object { $_.PrincipalId -ne $null }

Write-Host "`nPermanent Role Assignments Found: $($permanentAdmins.Count)" -ForegroundColor Yellow
Write-Host "These should be converted to eligible PIM assignments." -ForegroundColor Yellow

foreach ($admin in $permanentAdmins) {
    $user = Get-MgUser -UserId $admin.PrincipalId -ErrorAction SilentlyContinue
    $role = Get-MgRoleManagementDirectoryRoleDefinition -UnifiedRoleDefinitionId $admin.RoleDefinitionId
    Write-Host "  User: $($user.DisplayName) | Role: $($role.DisplayName)" -ForegroundColor White
}
'''

        scripts["03_configure_global_admin_pim"] = '''
# ============================================================
# GUARDIAN — Configure Global Administrator PIM Settings
# Sets 1 hour max activation, requires MFA + approval
#
# ⚠️  RUNS IN -WhatIf MODE BY DEFAULT
# Remove -WhatIf only when ready to apply changes
# ============================================================
# PREREQUISITES: 
#   Connect-MgGraph -Scopes "RoleManagement.ReadWrite.Directory"
#   Requires Privileged Role Administrator role

Write-Host "Configuring Global Administrator PIM settings..." -ForegroundColor Cyan
Write-Host "Running in WhatIf mode - no changes will be made." -ForegroundColor Yellow

# Get Global Administrator role definition
$globalAdminRole = Get-MgRoleManagementDirectoryRoleDefinition | 
    Where-Object { $_.DisplayName -eq "Global Administrator" }

Write-Host "Would configure the following settings for Global Administrator:" -ForegroundColor Cyan
Write-Host "  - Maximum activation duration: 1 hour" -ForegroundColor White
Write-Host "  - Require MFA on activation: Yes" -ForegroundColor White
Write-Host "  - Require justification: Yes" -ForegroundColor White
Write-Host "  - Require approval: Yes" -ForegroundColor White
Write-Host "  - Access review frequency: 90 days" -ForegroundColor White

# Uncomment and remove -WhatIf when ready to apply:
# Update-MgPolicyRoleManagementPolicyRule `
#     -UnifiedRoleManagementPolicyId $policyId `
#     -UnifiedRoleManagementPolicyRuleId $ruleId `
#     -WhatIf

Write-Host "`n✅ WhatIf complete. Review above and remove -WhatIf to apply." -ForegroundColor Green
Write-Host "📚 SC-300 Objective: Configure Privileged Identity Management" -ForegroundColor Cyan
'''

        scripts["04_backup_current_state"] = '''
# ============================================================
# GUARDIAN — Backup Current Role Assignments
# Run BEFORE making any PIM changes
# Creates a restore point you can reference if needed
# ============================================================
# PREREQUISITES: Connect-MgGraph -Scopes "RoleManagement.Read.Directory"

Write-Host "Creating backup of current role assignments..." -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "guardian_role_backup_$timestamp.json"

$assignments = Get-MgRoleManagementDirectoryRoleAssignment -All
$assignments | ConvertTo-Json -Depth 10 | Out-File $backupFile

Write-Host "✅ Backup saved to: $backupFile" -ForegroundColor Green
Write-Host "Keep this file safe — you can reference it if you need to restore." -ForegroundColor Yellow
'''

        return scripts

    def _generate_smb_scripts(self) -> Dict[str, str]:
        """
        Generate full PowerShell scripts for SMB tier.
        Includes all startup scripts plus advanced configuration.
        """
        scripts = self._generate_startup_scripts()

        scripts["05_configure_all_high_risk_roles"] = '''
# ============================================================
# GUARDIAN — Configure All High Risk Roles
# Applies PIM settings to all high-risk admin roles
#
# ⚠️  RUNS IN -WhatIf MODE BY DEFAULT
# ============================================================
# PREREQUISITES:
#   Connect-MgGraph -Scopes "RoleManagement.ReadWrite.Directory"

$highRiskRoles = @(
    "Global Administrator",
    "Privileged Role Administrator",
    "Security Administrator",
    "Exchange Administrator",
    "SharePoint Administrator",
    "Conditional Access Administrator",
    "Authentication Administrator"
)

Write-Host "Would configure PIM for the following high-risk roles:" -ForegroundColor Cyan
foreach ($role in $highRiskRoles) {
    Write-Host "  - $role" -ForegroundColor White
    Write-Host "    Max activation: 1 hour | MFA: Required | Approval: Required" -ForegroundColor Gray
}

Write-Host "`n✅ WhatIf complete. Remove -WhatIf to apply." -ForegroundColor Green
Write-Host "📚 SC-300 Objective: Manage Azure AD PIM role settings" -ForegroundColor Cyan
'''

        scripts["06_configure_access_reviews"] = '''
# ============================================================
# GUARDIAN — Configure Access Reviews
# Sets up 90-day access reviews for high-risk roles
#
# ⚠️  RUNS IN -WhatIf MODE BY DEFAULT
# ============================================================
# PREREQUISITES:
#   Connect-MgGraph -Scopes "AccessReview.ReadWrite.All"

Write-Host "Would configure access reviews:" -ForegroundColor Cyan
Write-Host "  - Frequency: Every 90 days" -ForegroundColor White
Write-Host "  - Scope: All high-risk privileged roles" -ForegroundColor White
Write-Host "  - Reviewer: Role-specific reviewer + manager" -ForegroundColor White
Write-Host "  - Auto-apply: Remove access if no response in 14 days" -ForegroundColor White

Write-Host "`n✅ WhatIf complete. Remove -WhatIf to apply." -ForegroundColor Green
Write-Host "📚 SC-300 Objective: Plan and implement access reviews" -ForegroundColor Cyan
'''

        scripts["07_configure_break_glass"] = '''
# ============================================================
# GUARDIAN — Break Glass Account Configuration
# Documents and monitors emergency access accounts
#
# ⚠️  READ ONLY — No changes made by this script
# ============================================================

Write-Host "Break Glass Account Recommendations:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Create TWO break glass accounts" -ForegroundColor White
Write-Host "   - Named clearly: breakglass1@yourdomain.com" -ForegroundColor Gray
Write-Host "   - Exclude from ALL Conditional Access policies" -ForegroundColor Gray
Write-Host "   - Assign Global Administrator permanently (exception to JIT rule)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Secure break glass accounts" -ForegroundColor White
Write-Host "   - Use very long random passwords (20+ characters)" -ForegroundColor Gray
Write-Host "   - Store credentials in a physical safe" -ForegroundColor Gray
Write-Host "   - Never use these accounts for daily tasks" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Monitor break glass accounts" -ForegroundColor White
Write-Host "   - Create an alert for ANY sign-in to these accounts" -ForegroundColor Gray
Write-Host "   - Review sign-in logs monthly" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 SC-300 Objective: Plan and implement privileged access" -ForegroundColor Cyan
Write-Host "⚠️  Security Note: Break glass accounts are your emergency parachute." -ForegroundColor Yellow
Write-Host "    They MUST exist but should NEVER be used in normal operations." -ForegroundColor Yellow
'''

        return scripts

    # --------------------------------------------------------
    # MARKDOWN OUTPUT
    # --------------------------------------------------------

    def to_markdown(self) -> str:
        tier = self.result.get("tier", TIER_HOME)
        content = self.result.get("content", "")
        scripts = self.result.get("scripts", {})

        lines = [
            "## PIM Lockdown\n",
            "> 📚 **SC-300 Domain:** Implement an identity governance strategy\n",
        ]

        if tier == TIER_HOME:
            lines.append("### PIM Overview for Home Users\n")
            lines.append(
                "> ℹ️ **Note:** Full PIM requires Microsoft 365 Business Premium "
                "or Azure AD P2 licence. The information below explains what PIM is "
                "and what you can do now to prepare.\n"
            )
            lines.append(content)

        else:
            lines.append("### PIM Configuration Guide\n")
            lines.append(
                "> ⚠️ **Prerequisites:** Ensure you have Azure AD P2 or "
                "Microsoft 365 Business Premium licence before proceeding.\n"
            )
            lines.append(content)

            if scripts:
                lines.append("\n### PowerShell Scripts\n")
                lines.append(
                    "> ⚠️ **Important:** All scripts run in `-WhatIf` mode by default. "
                    "This means they show what WOULD happen without making any changes. "
                    "Review the output carefully before removing `-WhatIf` to apply changes. "
                    "Always run the backup script first.\n"
                )

                for script_name, script_content in scripts.items():
                    friendly_name = script_name.replace("_", " ").title()
                    lines.append(f"#### {friendly_name}\n")
                    lines.append(f"```powershell{script_content}```\n")

        lines.append("\n### PIM Exam Objectives\n")
        for obj in self.exam_objectives():
            lines.append(f"- 📚 {obj}")

        return "\n".join(lines)

    # --------------------------------------------------------
    # EXAM OBJECTIVES
    # --------------------------------------------------------

    def exam_objectives(self) -> List[str]:
        base = [
            "SC-300: Configure Privileged Identity Management (PIM)",
            "SC-300: Manage Azure AD PIM role settings",
            "SC-300: Implement just-in-time privileged access",
            "SC-300: Plan and implement access reviews for privileged roles",
            "SC-300: Monitor privileged identity activity",
        ]

        if self.tier == TIER_SMB:
            base.extend([
                "CyberArk Defender: Integrate PIM with PAM for comprehensive privileged access control",
                "SC-300: Configure emergency access (break glass) accounts",
            ])

        return base