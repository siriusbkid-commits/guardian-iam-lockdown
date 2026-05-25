# ============================================================
# GUARDIAN — IAM Lockdown Template
# agents/profile_agent.py — Organisation Profile Agent
#
# PURPOSE:
# First agent to run. Builds the organisation profile through
# a hybrid approach:
# 1. Auto-detects what it can (OS, domain, software, cloud)
# 2. Asks the user to confirm and fill in the gaps
# 3. Determines the correct tier (Home / Startup / SMB)
# 4. Saves profile for future runs (upgrade detection)
#
# DETECTION METHODS:
# - OneDrive presence (strong M365 indicator)
# - Teams installation
# - Office registry keys
# - Azure AD join status (dsregcmd)
# - CyberArk install paths + service check
# - Domain join status (wmic)
#
# OUTPUT:
# A context dict that feeds into every other agent.
# ============================================================

import os
import json
import platform
import subprocess
import winreg
from datetime import datetime
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from config import (
    TIER_HOME, TIER_STARTUP, TIER_SMB,
    MODE_STANDARD, MODE_CONSULTANT, MODE_AUDIT,
    PROFILES_DIR, GUARDIAN_VERSION
)


class ProfileAgent(BaseAgent):
    """
    Builds the organisation profile through auto-detection + questionnaire.
    Determines tier and mode for the current run.
    """

    def __init__(self, llm_client):
        super().__init__(llm_client, context={})
        self.profile = {}

    # --------------------------------------------------------
    # MAIN RUN
    # --------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        print("\n" + "=" * 50)
        print(" GUARDIAN — Organisation Profile")
        print("=" * 50)

        # Check for existing profile
        existing = self._load_existing_profile()
        if existing:
            if self._confirm_existing_profile(existing):
                self.profile = existing
                self.result = self.profile
                return self.result

        # Auto detection
        print("\n[GUARDIAN] Scanning your system...\n")
        detected = self._auto_detect()
        confirmed = self._confirm_detected(detected)

        # Questionnaire
        org_name = self._ask_org_name()
        tier = self._ask_tier(detected)
        mode = self._ask_mode()
        systems = self._ask_systems(confirmed)
        posture = self._ask_current_posture()

        # Build profile
        self.profile = {
            "org_name": org_name,
            "tier": tier,
            "mode": mode,
            "systems": systems,
            "current_posture": posture,
            "detected": confirmed,
            "guardian_version": GUARDIAN_VERSION,
            "created": datetime.now().isoformat(),
            "last_run": datetime.now().isoformat()
        }

        # Save profile for future runs
        self._save_profile(self.profile, org_name)

        self.result = self.profile
        self.context = self.profile
        return self.result

    # --------------------------------------------------------
    # AUTO DETECTION — SMARTER VERSION
    # --------------------------------------------------------

    def _auto_detect(self) -> Dict[str, Any]:
        detected = {}

        # OS Detection
        detected["os"] = platform.system()
        detected["os_version"] = platform.version()
        detected["machine"] = platform.machine()
        detected["python_version"] = platform.python_version()

        # Only run Windows-specific checks on Windows
        if platform.system() != "Windows":
            detected["domain_joined"] = False
            detected["azure_ad_joined"] = False
            detected["microsoft_365"] = False
            detected["teams"] = False
            detected["onedrive"] = False
            detected["cyberark"] = False
            return detected

        # Domain join detection
        try:
            result = subprocess.run(
                ["wmic", "computersystem", "get", "partofdomain"],
                capture_output=True, text=True, timeout=5
            )
            detected["domain_joined"] = "TRUE" in result.stdout.upper()
        except Exception:
            detected["domain_joined"] = False

        # Azure AD join detection (most reliable method)
        detected["azure_ad_joined"] = self._check_azure_ad_joined()

        # OneDrive detection (strong M365 indicator)
        onedrive_path = os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Microsoft", "OneDrive"
        )
        detected["onedrive"] = os.path.exists(onedrive_path)

        # Microsoft Teams detection
        teams_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Teams"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft Teams"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft Teams"),
        ]
        detected["teams"] = any(os.path.exists(p) for p in teams_paths)

        # Microsoft 365 / Office detection via multiple methods
        detected["microsoft_365"] = self._check_microsoft_365()

        # CyberArk detection via paths + service
        detected["cyberark"] = self._check_cyberark()

        return detected

    def _check_azure_ad_joined(self) -> bool:
        """Check Azure AD join status using dsregcmd."""
        try:
            result = subprocess.run(
                ["dsregcmd", "/status"],
                capture_output=True, text=True, timeout=10
            )
            return "AzureAdJoined : YES" in result.stdout
        except Exception:
            return False

    def _check_microsoft_365(self) -> bool:
        """
        Check for M365 using multiple methods:
        1. OneDrive presence (most reliable for home/personal)
        2. Office install paths
        3. Registry keys
        """
        # Method 1: OneDrive (strong personal M365 signal)
        onedrive = os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Microsoft", "OneDrive"
        )
        if os.path.exists(onedrive):
            return True

        # Method 2: Office install paths
        office_paths = [
            r"C:\Program Files\Microsoft Office",
            r"C:\Program Files (x86)\Microsoft Office",
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft Office"),
        ]
        if any(os.path.exists(p) for p in office_paths):
            return True

        # Method 3: Registry check
        try:
            reg_paths = [
                r"Software\Microsoft\Office",
                r"Software\Microsoft\Office\16.0",
            ]
            for reg_path in reg_paths:
                try:
                    winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
                    return True
                except FileNotFoundError:
                    continue
        except Exception:
            pass

        return False

    def _check_cyberark(self) -> bool:
        """
        Check for CyberArk via install paths and Windows service.
        """
        # Check install paths
        cyberark_paths = [
            r"C:\Program Files (x86)\CyberArk",
            r"C:\Program Files\CyberArk",
        ]
        if any(os.path.exists(p) for p in cyberark_paths):
            return True

        # Check for CyberArk Windows service
        try:
            result = subprocess.run(
                ["sc", "query", "CyberArk"],
                capture_output=True, text=True, timeout=5
            )
            return "RUNNING" in result.stdout or "STOPPED" in result.stdout
        except Exception:
            pass

        return False

    def _confirm_detected(self, detected: Dict[str, Any]) -> Dict[str, Any]:
        print("[GUARDIAN] I detected the following about your system:\n")
        print(f"  Operating System  : {detected.get('os')} {detected.get('os_version', '')[:30]}")
        print(f"  Domain Joined     : {'Yes' if detected.get('domain_joined') else 'No'}")
        print(f"  Azure AD Joined   : {'Yes' if detected.get('azure_ad_joined') else 'No'}")
        print(f"  Microsoft 365     : {'Detected' if detected.get('microsoft_365') else 'Not detected'}")
        print(f"  OneDrive          : {'Detected' if detected.get('onedrive') else 'Not detected'}")
        print(f"  Microsoft Teams   : {'Detected' if detected.get('teams') else 'Not detected'}")
        print(f"  CyberArk          : {'Detected' if detected.get('cyberark') else 'Not detected'}")

        print("\nIs this correct? (y/n): ", end="")
        ans = input().strip().lower()

        if ans != "y":
            print("\nNo problem — we will use your answers in the next section.\n")
            detected["confirmed"] = False
        else:
            detected["confirmed"] = True

        return detected

    # --------------------------------------------------------
    # SMART TIER SUGGESTION
    # --------------------------------------------------------

    def _suggest_tier(self, detected: Dict[str, Any]) -> str:
        """
        Suggest a tier based on detected environment.
        """
        if detected.get("cyberark"):
            return TIER_SMB
        if detected.get("azure_ad_joined") or detected.get("domain_joined"):
            return TIER_STARTUP
        return TIER_HOME

    # --------------------------------------------------------
    # QUESTIONNAIRE
    # --------------------------------------------------------

    def _ask_org_name(self) -> str:
        print("\nWhat is your organisation or home name?")
        print("(e.g. 'Acme Startup', 'Smith Household', 'My Home PC'): ", end="")
        name = input().strip()
        return name if name else "My Organisation"

    def _ask_tier(self, detected: Dict[str, Any]) -> str:
        suggested = self._suggest_tier(detected)
        suggested_label = {
            TIER_HOME: "Home User",
            TIER_STARTUP: "Startup",
            TIER_SMB: "SMB"
        }.get(suggested, "Home User")

        print(f"\n[GUARDIAN] Based on your system I suggest: {suggested_label}\n")
        print("[GUARDIAN] What type of user are you?\n")
        print("  1. Home User     — single computer, personal Microsoft account")
        print("  2. Startup       — 2-50 users, Microsoft 365, Entra ID")
        print("  3. SMB           — 50+ users, Entra ID + CyberArk\n")

        while True:
            choice = input("Select (1/2/3): ").strip()
            if choice == "1":
                return TIER_HOME
            elif choice == "2":
                return TIER_STARTUP
            elif choice == "3":
                return TIER_SMB
            print("Please enter 1, 2 or 3.")

    def _ask_mode(self) -> str:
        print("\n[GUARDIAN] Select mode:\n")
        print("  1. Standard    — guided, step by step (recommended for most users)")
        print("  2. Consultant  — advanced options for security professionals")
        print("  3. Audit       — review and update an existing playbook\n")

        while True:
            choice = input("Select (1/2/3): ").strip()
            if choice == "1":
                return MODE_STANDARD
            elif choice == "2":
                return MODE_CONSULTANT
            elif choice == "3":
                return MODE_AUDIT
            print("Please enter 1, 2 or 3.")

    def _ask_systems(self, detected: Dict[str, Any]) -> List[str]:
        print("\n[GUARDIAN] Which systems are you using? (select all that apply)\n")
        print("  1. Microsoft 365 / Entra ID")
        print("  2. CyberArk")
        print("  3. Windows Active Directory (on-premise)")
        print("  4. Google Workspace")
        print("  5. Other / Not sure\n")

        systems = []
        choices = input("Enter numbers separated by commas (e.g. 1,2): ").strip()

        mapping = {
            "1": "Microsoft 365 / Entra ID",
            "2": "CyberArk",
            "3": "Windows Active Directory",
            "4": "Google Workspace",
            "5": "Other"
        }

        for c in choices.split(","):
            c = c.strip()
            if c in mapping:
                systems.append(mapping[c])

        # Add auto-detected systems not already listed
        if detected.get("microsoft_365") and "Microsoft 365 / Entra ID" not in systems:
            systems.append("Microsoft 365 / Entra ID (auto-detected)")

        if detected.get("cyberark") and "CyberArk" not in systems:
            systems.append("CyberArk (auto-detected)")

        return systems if systems else ["Not specified"]

    def _ask_current_posture(self) -> str:
        print("\n[GUARDIAN] What is your current security posture?\n")
        print("  1. None         — no security controls in place")
        print("  2. Basic        — some passwords and antivirus")
        print("  3. Intermediate — MFA enabled, some policies in place\n")

        while True:
            choice = input("Select (1/2/3): ").strip()
            if choice == "1":
                return "none"
            elif choice == "2":
                return "basic"
            elif choice == "3":
                return "intermediate"
            print("Please enter 1, 2 or 3.")

    # --------------------------------------------------------
    # PROFILE PERSISTENCE
    # --------------------------------------------------------

    def _profile_path(self, org_name: str) -> str:
        safe_name = org_name.lower().replace(" ", "_").replace("/", "_")
        os.makedirs(PROFILES_DIR, exist_ok=True)
        return os.path.join(PROFILES_DIR, f"{safe_name}_profile.json")

    def _save_profile(self, profile: Dict[str, Any], org_name: str):
        path = self._profile_path(org_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
        print(f"\n[GUARDIAN] Profile saved to {path}")

    def _load_existing_profile(self) -> Dict[str, Any]:
        if not os.path.exists(PROFILES_DIR):
            return {}

        profiles = [f for f in os.listdir(PROFILES_DIR) if f.endswith("_profile.json")]
        if not profiles:
            return {}

        print("\n[GUARDIAN] I found existing organisation profiles:\n")
        for i, p in enumerate(profiles, start=1):
            print(f"  {i}. {p.replace('_profile.json', '').replace('_', ' ').title()}")
        print(f"  {len(profiles) + 1}. Start fresh\n")

        while True:
            choice = input("Select a profile or start fresh: ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(profiles):
                    path = os.path.join(PROFILES_DIR, profiles[idx - 1])
                    with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
                elif idx == len(profiles) + 1:
                    return {}
            print("Invalid selection.")

    def _confirm_existing_profile(self, profile: Dict[str, Any]) -> bool:
        print(f"\n[GUARDIAN] Found existing profile for: {profile.get('org_name')}")
        print(f"  Tier        : {profile.get('tier')}")
        print(f"  Last run    : {profile.get('last_run', 'Unknown')[:10]}")
        print(f"  Systems     : {', '.join(profile.get('systems', []))}")

        # Check for upgrade opportunity
        tier = profile.get("tier")
        systems = profile.get("systems", [])

        if tier == TIER_STARTUP and any("CyberArk" in s for s in systems):
            print("\n[GUARDIAN] I notice you now have CyberArk.")
            print("  Would you like to upgrade to SMB tier? (y/n): ", end="")
            if input().strip().lower() == "y":
                profile["tier"] = TIER_SMB
                print("[GUARDIAN] Upgraded to SMB tier!")

        print("\nUse this profile? (y/n): ", end="")
        return input().strip().lower() == "y"

    # --------------------------------------------------------
    # REQUIRED BaseAgent implementations
    # --------------------------------------------------------

    def to_markdown(self) -> str:
        p = self.profile
        detected = p.get("detected", {})

        lines = [
            "## Organisation Profile\n",
            f"- **Organisation:** {p.get('org_name', 'Unknown')}",
            f"- **Tier:** {p.get('tier', 'Unknown').title()}",
            f"- **Mode:** {p.get('mode', 'Unknown').title()}",
            f"- **Systems:** {', '.join(p.get('systems', []))}",
            f"- **Current Posture:** {p.get('current_posture', 'Unknown').title()}",
            f"- **GUARDIAN Version:** {p.get('guardian_version', '1.0')}",
            f"- **Generated:** {p.get('last_run', '')[:10]}",
            "",
            "### Detected Environment",
            f"- **OS:** {detected.get('os', 'Unknown')}",
            f"- **Domain Joined:** {'Yes' if detected.get('domain_joined') else 'No'}",
            f"- **Azure AD Joined:** {'Yes' if detected.get('azure_ad_joined') else 'No'}",
            f"- **Microsoft 365:** {'Detected' if detected.get('microsoft_365') else 'Not detected'}",
            f"- **OneDrive:** {'Detected' if detected.get('onedrive') else 'Not detected'}",
            f"- **Teams:** {'Detected' if detected.get('teams') else 'Not detected'}",
            f"- **CyberArk:** {'Detected' if detected.get('cyberark') else 'Not detected'}",
            ""
        ]
        return "\n".join(lines)

    def exam_objectives(self) -> List[str]:
        return [
            "SC-300: Implement an identity management solution",
            "SC-300: Plan and implement a privileged access strategy",
            "CyberArk Defender: Understand PAM fundamentals"
        ]