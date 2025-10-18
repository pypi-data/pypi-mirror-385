# neuro_simulator/agent/tools/add_temp_memory.py
"""The Add Temp Memory tool for the agent."""

from typing import Any, Dict, List

from neuro_simulator.agents.tools.base import BaseTool
from neuro_simulator.agents.memory.manager import MemoryManager
from neuro_simulator.utils import console


class AddTempMemoryTool(BaseTool):
    """Tool to add an entry to the agent's temporary memory."""

    def __init__(self, memory_manager: MemoryManager):
        """Initializes the AddTempMemoryTool."""
        self.memory_manager = memory_manager

    @property
    def name(self) -> str:
        return "add_temp_memory"

    @property
    def description(self) -> str:
        return "Adds a non-empty entry to the temporary memory. Use for short-term observations, recent facts, or topics to bring up soon. The 'content' parameter is mandatory."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "content",
                "type": "string",
                "description": "The specific, non-empty text content of the memory entry. Cannot be an empty string or contain only whitespace.",
                "required": True,
            },
            {
                "name": "role",
                "type": "string",
                "description": "The role associated with the memory (e.g., 'system', 'user'). Defaults to 'system'.",
                "required": False,
            },
        ]

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Executes the action to add an entry to temporary memory.

        Args:
            **kwargs: Must contain 'content' and optionally 'role'.

        Returns:
            A dictionary confirming the action.
        """
        content = kwargs.get("content")
        if not isinstance(content, str) or not content:
            raise ValueError("The 'content' parameter must be a non-empty string.")

        role = kwargs.get("role", "system")
        if not isinstance(role, str):
            raise ValueError("The 'role' parameter must be a string.")

        await self.memory_manager.add_temp_memory(content=content, role=role)

        console.box_it_up(
            [f"Role: {role}", f"Content: {content}"],
            title="Added to Temporary Memory",
            border_color=console.THEME["MEMORY"],
        )

        return {
            "status": "success",
            "message": f"Added entry to temporary memory with role '{role}'.",
        }
