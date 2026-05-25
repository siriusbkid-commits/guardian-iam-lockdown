# ============================================================
# GUARDIAN — IAM Lockdown Template
# config.py — Central configuration
# ============================================================

# LLM Mode: "offline" (Ollama) or "online" (Anthropic/OpenAI)
GUARDIAN_MODE = "offline"

# Local Ollama model (offline mode)
LOCAL_MODEL = "mistral-nemo"

# Online model (online mode) — set your preferred API model here
ONLINE_MODEL = "claude-sonnet-4-20250514"

# Guardian version — used for playbook versioning
GUARDIAN_VERSION = "1.0"

# Output directory for generated playbooks
OUTPUT_DIR = "output"

# Profiles directory for saved organisation profiles
PROFILES_DIR = "profiles"

# Tiers
TIER_HOME = "home"
TIER_STARTUP = "startup"
TIER_SMB = "smb"

# Modes
MODE_STANDARD = "standard"
MODE_CONSULTANT = "consultant"
MODE_AUDIT = "audit"
