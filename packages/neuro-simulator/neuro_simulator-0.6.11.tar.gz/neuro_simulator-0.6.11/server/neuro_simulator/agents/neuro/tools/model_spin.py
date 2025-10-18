# neuro_simulator/agent/tools/model_spin.py
import logging
from typing import Dict, Any, List

from neuro_simulator.agents.tools.base import BaseTool
from neuro_simulator.services.stream import live_stream_manager
from neuro_simulator.utils import console

logger = logging.getLogger(__name__)


class ModelSpinTool(BaseTool):
    """A tool to make the client-side avatar spin."""

    def __init__(self, **kwargs):
        # The base class might pass memory_manager, so we accept it but don't use it.
        pass

    @property
    def name(self) -> str:
        return "model_spin"

    @property
    def description(self) -> str:
        return "Makes model spin once, dont got too dizzy when spining lol."

    @property
    def parameters(self) -> List[Dict[str, Any]]:
        return []

    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Sends a WebSocket command to the client to trigger the avatar spin animation.
        """
        logger.debug(f"Executing {self.name} tool.")
        try:
            await live_stream_manager.event_queue.put({"type": "model_spin"})
            console.box_it_up(
                ["Command: model_spin"],
                title="Executed Model Tool",
                border_color=console.THEME["TOOL"],
            )
            return {"status": "success", "message": "Spin command sent."}
        except Exception as e:
            logger.error(f"Error in {self.name} tool: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
