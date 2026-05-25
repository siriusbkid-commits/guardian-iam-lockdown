# ============================================================
# GUARDIAN — IAM Lockdown Template
# agents/base_agent.py — Base class for all agents
#
# PURPOSE:
# Every GUARDIAN agent inherits from BaseAgent.
# This enforces a standard interface so:
# - The orchestrator can run any agent the same way
# - Community agents plug in without modifying core code
# - Consultants can add custom agents by inheriting this class
#
# TO CREATE A CUSTOM AGENT:
# 1. Create agents/your_agent.py
# 2. class YourAgent(BaseAgent):
# 3. Implement run(), to_markdown(), exam_objectives()
# 4. Register in orchestrator.py
# ============================================================

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAgent(ABC):
    """
    Abstract base class for all GUARDIAN agents.
    All agents must implement run(), to_markdown(), and exam_objectives().
    """

    def __init__(self, llm_client, context: Dict[str, Any]):
        """
        Args:
            llm_client: LLM client (offline or online) from llm_factory
            context: Organisation profile dict from ProfileAgent
        """
        self.llm = llm_client
        self.context = context
        self.result = {}
        self.raw_output = ""

    # --------------------------------------------------------
    # REQUIRED — every agent must implement these
    # --------------------------------------------------------

    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """
        Execute the agent and return structured results.
        Must populate self.result before returning.
        """
        pass

    @abstractmethod
    def to_markdown(self) -> str:
        """
        Return the agent's output as a markdown section
        for inclusion in the master playbook.
        """
        pass

    @abstractmethod
    def exam_objectives(self) -> List[str]:
        """
        Return a list of SC-300 / CyberArk Defender exam objectives
        covered by this agent's output.
        """
        pass

    # --------------------------------------------------------
    # OPTIONAL — agents can override these
    # --------------------------------------------------------

    def to_json(self) -> Dict[str, Any]:
        """
        Return the agent's output as a JSON-serialisable dict.
        Defaults to self.result — override for custom structure.
        """
        return self.result

    def agent_name(self) -> str:
        """
        Return the agent's display name.
        Defaults to class name — override for custom name.
        """
        return self.__class__.__name__

    def validate_context(self, required_keys: List[str]) -> bool:
        """
        Helper to validate required context keys are present.
        Call at start of run() to catch missing profile data early.
        """
        missing = [k for k in required_keys if k not in self.context]
        if missing:
            print(f"[{self.agent_name()}] WARNING: Missing context keys: {missing}")
            return False
        return True

    def call_llm(self, prompt: str) -> str:
        """
        Wrapper around LLM call with basic error handling.
        Stores raw output for debugging.
        """
        self.raw_output = self.llm.call(prompt)
        return self.raw_output