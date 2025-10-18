# neuro_simulator/chatbot/nickname_gen/generator.py
"""
Nickname generator for the chatbot agent.
Implements a dual-pool system (base and dynamic) with multiple generation strategies.
"""

import logging
import random
import json
from typing import Any, List, Dict, Callable, Optional

from ...llm import LLMClient
from ....core.config import config_manager
from ....core.path_manager import path_manager
from ....utils import console

logger = logging.getLogger(__name__)


class NicknameGenerator:
    """Generates diverse nicknames using a multi-strategy, dual-pool system."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        if not path_manager:
            raise RuntimeError(
                "PathManager must be initialized before NicknameGenerator."
            )

        self.base_adjectives: List[str] = []
        self.base_nouns: List[str] = []
        self.special_users: List[str] = []

        self.dynamic_adjectives: List[str] = []
        self.dynamic_nouns: List[str] = []

        self.llm_client = llm_client

    def _load_word_pool(self, filename: str) -> List[str]:
        """Loads a word pool from the nickname_gen/data directory."""
        assert path_manager is not None
        file_path = path_manager.chatbot_nickname_data_dir / filename
        if not file_path.exists():
            logger.warning(
                f"Nickname pool file not found: {file_path}. The pool will be empty."
            )
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    async def initialize(self):
        """Loads base pools and attempts to generate dynamic pools."""
        logger.info("Initializing NicknameGenerator...")
        self.base_adjectives = self._load_word_pool("adjectives.txt")
        self.base_nouns = self._load_word_pool("nouns.txt")
        self.special_users = self._load_word_pool("special_users.txt")

        if not self.base_adjectives or not self.base_nouns:
            logger.warning(
                "Base adjective or noun pools are empty. Nickname generation quality will be affected."
            )

        if config_manager.settings.chatbot.enable_dynamic_pool:
            await self._populate_dynamic_pools()

        logger.info("NicknameGenerator initialized.")

    async def _populate_dynamic_pools(self):
        """Uses an LLM to generate and populate the dynamic word pools."""
        if not self.llm_client:
            logger.warning(
                "LLM client not configured for NicknameGenerator. Skipping dynamic pool generation."
            )
            return

        logger.info("Attempting to populate dynamic nickname pools using LLM...")
        pool_size = (
            config_manager.settings.chatbot.dynamic_pool_size
        )
        try:
            adj_prompt = f"Generate a JSON array of {pool_size} diverse, cool-sounding English adjectives for online usernames. The output MUST be a single valid JSON array of strings. Example: [\"fast\", \"clever\", \"shiny\"]"
            noun_prompt = f"Generate a JSON array of {pool_size} diverse, cool-sounding English nouns for online usernames. The output MUST be a single valid JSON array of strings. Example: [\"river\", \"comet\", \"dream\"]"

            adj_list_str = await self.llm_client.generate(
                adj_prompt, max_tokens=pool_size * 15  # Increased token limit for JSON overhead
            )
            noun_list_str = await self.llm_client.generate(
                noun_prompt, max_tokens=pool_size * 15 # Increased token limit for JSON overhead
            )

            try:
                # Primary strategy: parse as JSON
                self.dynamic_adjectives = json.loads(adj_list_str)
                self.dynamic_nouns = json.loads(noun_list_str)
            except json.JSONDecodeError:
                logger.warning("LLM did not return valid JSON for nickname pools, falling back to line splitting.")
                # Fallback strategy: split by newline
                self.dynamic_adjectives = [
                    line.strip() for line in adj_list_str.split("\n") if line.strip()
                ]
                self.dynamic_nouns = [
                    line.strip() for line in noun_list_str.split("\n") if line.strip()
                ]

            # Robustness check: Flatten list if it's a list of lists
            if self.dynamic_adjectives and isinstance(self.dynamic_adjectives[0], list):
                logger.warning("Dynamic adjectives pool is a list of lists, flattening.")
                self.dynamic_adjectives = [item[0] for item in self.dynamic_adjectives if item and isinstance(item, list)]
            
            if self.dynamic_nouns and isinstance(self.dynamic_nouns[0], list):
                logger.warning("Dynamic nouns pool is a list of lists, flattening.")
                self.dynamic_nouns = [item[0] for item in self.dynamic_nouns if item and isinstance(item, list)]

            if self.dynamic_adjectives and self.dynamic_nouns:
                logger.info(
                    f"Successfully populated dynamic pools with {len(self.dynamic_adjectives)} adjectives and {len(self.dynamic_nouns)} nouns."
                )
                console.box_it_up(
                    [
                        f"Successfully populated dynamic pools with {len(self.dynamic_adjectives)} adjectives and {len(self.dynamic_nouns)} nouns."
                    ],
                    title="Nickname Pool Generated",
                    border_color=console.BLUE,
                )
            else:
                logger.warning("LLM generated empty lists for dynamic pools.")

        except Exception as e:
            logger.error(
                f"Failed to generate dynamic nickname pool: {e}. Falling back to base pool only.",
                exc_info=True,
            )
            self.dynamic_adjectives = []
            self.dynamic_nouns = []

    def _get_combined_pools(self) -> tuple[List[str], List[str]]:
        """Returns the combination of base and dynamic pools."""
        adjectives = self.base_adjectives + self.dynamic_adjectives
        nouns = self.base_nouns + self.dynamic_nouns
        return adjectives, nouns

    def _generate_from_word_pools(self) -> str:
        adjectives, nouns = self._get_combined_pools()
        if not adjectives or not nouns:
            return self._generate_random_numeric()  # Fallback

        def get_word(item: Any) -> str:
            """Safely get the word from a string or a dict."""
            if isinstance(item, dict):
                # Look for common keys for the word itself.
                for key in ["word", "noun", "adjective", "name"]:
                    if isinstance(item.get(key), str):
                        return item[key]
                # Fallback: stringify the whole dict if no suitable key is found.
                return str(item)
            return str(item)

        noun_item = random.choice(nouns)
        noun = get_word(noun_item)

        # 50% chance to add an adjective
        if random.random() < 0.5:
            adjective_item = random.choice(adjectives)
            adjective = get_word(adjective_item)
            # Formatting variations
            format_choice = random.random()
            if format_choice < 0.4:
                return f"{adjective.capitalize()}{noun.capitalize()}"
            elif format_choice < 0.7:
                return f"{adjective.lower()}_{noun.lower()}"
            else:
                return f"{adjective.lower()}{noun.lower()}"
        else:
            # Add a number suffix 30% of the time
            if random.random() < 0.3:
                return f"{noun.capitalize()}{random.randint(1, 999)}"
            return noun.capitalize()

    def _generate_from_special_pool(self) -> str:
        if not self.special_users:
            return self._generate_from_word_pools()  # Fallback
        return random.choice(self.special_users)

    def _generate_random_numeric(self) -> str:
        return f"user{random.randint(10000, 99999)}"

    def generate_nickname(self) -> str:
        """Generates a single nickname based on weighted strategies."""
        strategies: Dict[Callable[[], str], int] = {
            self._generate_from_word_pools: 70,
            self._generate_from_special_pool: 15,
            self._generate_random_numeric: 15,
        }

        # Filter out strategies that can't be run (e.g., empty special pool)
        if not self.special_users:
            strategies.pop(self._generate_from_special_pool, None)
            # Redistribute weight
            if strategies:
                total_weight = sum(strategies.values())
                strategies = {k: int(v / total_weight * 100) for k, v in strategies.items()}

        if not any(self._get_combined_pools()):
            strategies = {self._generate_random_numeric: 100}

        chosen_strategy = random.choices(
            population=list(strategies.keys()), weights=list(strategies.values()), k=1
        )[0]

        return chosen_strategy()
