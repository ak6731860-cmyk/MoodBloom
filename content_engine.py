# ============================================================
# MOODBLOOM — CONTENT ENGINE
# ============================================================
# Handles:
#   📖 Stories
#   🕵️ Mysteries
#   🎁 Mystery Box Rewards
#   📊 User content history
#
# Works with:
#   story_engine.py
#   mystery_engine.py
#   reward_engine.py
#
# Data is stored inside:
#   data/content/
#   data/user_content/
# ============================================================

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

CONTENT_DIR = DATA_DIR / "content"

USER_CONTENT_DIR = DATA_DIR / "user_content"

STORIES_FILE = CONTENT_DIR / "stories.json"

MYSTERIES_FILE = CONTENT_DIR / "mysteries.json"

REWARDS_FILE = CONTENT_DIR / "rewards.json"

HISTORY_FILE = USER_CONTENT_DIR / "history.json"


# ============================================================
# DEFAULT STORIES
# ============================================================

DEFAULT_STORIES = [
    {
        "id": "moonlight_secret",
        "title": "🌙 The Secret of Moonlight",
        "description": (
            "A mysterious flower, a forgotten garden and a secret "
            "that appears only after midnight."
        ),
        "difficulty": "medium",
        "moods": [
            "calm",
            "curious",
            "sad",
            "mysterious",
        ],
        "parts": 10,
        "story_engine": True,
    },
    {
        "id": "door_213",
        "title": "🚪 The Door at 2:13 AM",
        "description": (
            "Every night at 2:13 AM, a locked door appears "
            "in an empty hallway."
        ),
        "difficulty": "medium",
        "moods": [
            "curious",
            "mysterious",
            "scared",
            "excited",
        ],
        "parts": 10,
        "story_engine": True,
    },
    {
        "id": "last_train",
        "title": "🚂 The Last Train",
        "description": (
            "A train arrives at a station that does not exist "
            "on any map."
        ),
        "difficulty": "hard",
        "moods": [
            "curious",
            "sad",
            "mysterious",
            "adventurous",
        ],
        "parts": 12,
        "story_engine": True,
    },
]


# ============================================================
# DEFAULT MYSTERIES
# ============================================================

DEFAULT_MYSTERIES = [
    {
        "id": "three_flowers",
        "title": "🌸 The Three Flowers",
        "description": (
            "Three flowers are placed on a table. "
            "Only one contains the hidden clue."
        ),
        "difficulty": "easy",
        "reward_xp": 30,
        "answer": 2,
        "hint": (
            "Look carefully at the order of the flowers."
        ),
    },
    {
        "id": "missing_book",
        "title": "📖 The Missing Book",
        "description": (
            "A book disappears from a locked room. "
            "There are three possible suspects."
        ),
        "difficulty": "medium",
        "reward_xp": 50,
        "answer": 1,
        "hint": (
            "Think about who had access to the room."
        ),
    },
    {
        "id": "silent_clock",
        "title": "🕰️ The Silent Clock",
        "description": (
            "A clock stops at exactly 12:12 every night. "
            "What is causing it?"
        ),
        "difficulty": "medium",
        "reward_xp": 60,
        "answer": 3,
        "hint": (
            "The time itself is part of the clue."
        ),
    },
]


# ============================================================
# DEFAULT REWARDS
# ============================================================

DEFAULT_REWARDS = [
    {
        "id": "tiny_bloom",
        "name": "🌱 Tiny Bloom",
        "description": "A small reward for a small win.",
        "type": "xp",
        "value": 10,
        "rarity": "common",
        "weight": 40,
    },
    {
        "id": "happy_bloom",
        "name": "🌸 Happy Bloom",
        "description": "A little extra positivity.",
        "type": "xp",
        "value": 25,
        "rarity": "common",
        "weight": 30,
    },
    {
        "id": "golden_bloom",
        "name": "✨ Golden Bloom",
        "description": "A rare and valuable bloom.",
        "type": "xp",
        "value": 50,
        "rarity": "rare",
        "weight": 15,
    },
    {
        "id": "mystery_seed",
        "name": "🌱 Mystery Seed",
        "description": (
            "A mysterious seed. Something may grow from it later."
        ),
        "type": "item",
        "value": 1,
        "rarity": "rare",
        "weight": 8,
    },
    {
        "id": "mystery_token",
        "name": "🔮 Mystery Token",
        "description": (
            "A token connected to the Mystery system."
        ),
        "type": "item",
        "value": 1,
        "rarity": "epic",
        "weight": 5,
    },
    {
        "id": "story_ticket",
        "name": "📖 Story Ticket",
        "description": (
            "A special ticket for future story content."
        ),
        "type": "item",
        "value": 1,
        "rarity": "legendary",
        "weight": 2,
    },
]


# ============================================================
# CONTENT ENGINE
# ============================================================

class ContentEngine:
    """
    Central content manager for MoodBloom.

    Responsible for:
        - stories
        - mysteries
        - rewards
        - user history
    """

    def __init__(self) -> None:

        self._ensure_directories()

        self.stories = self._load_or_create(
            STORIES_FILE,
            DEFAULT_STORIES,
        )

        self.mysteries = self._load_or_create(
            MYSTERIES_FILE,
            DEFAULT_MYSTERIES,
        )

        self.rewards = self._load_or_create(
            REWARDS_FILE,
            DEFAULT_REWARDS,
        )

        self.history = self._load_or_create(
            HISTORY_FILE,
            {},
        )

    # ========================================================
    # DIRECTORY SETUP
    # ========================================================

    @staticmethod
    def _ensure_directories() -> None:

        CONTENT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        USER_CONTENT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ========================================================
    # FILE HELPERS
    # ========================================================

    @staticmethod
    def _load_or_create(
        path: Path,
        default: Any,
    ) -> Any:

        if not path.exists():

            ContentEngine._save_file(
                path,
                default,
            )

            return default

        try:

            with open(
                path,
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
            TypeError,
        ):

            ContentEngine._save_file(
                path,
                default,
            )

            return default

    @staticmethod
    def _save_file(
        path: Path,
        data: Any,
    ) -> None:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary = path.with_suffix(
            path.suffix + ".tmp"
        )

        with open(
            temporary,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary.replace(path)

    # ========================================================
    # SAVE METHODS
    # ========================================================

    def _save_stories(self) -> None:

        self._save_file(
            STORIES_FILE,
            self.stories,
        )

    def _save_mysteries(self) -> None:

        self._save_file(
            MYSTERIES_FILE,
            self.mysteries,
        )

    def _save_rewards(self) -> None:

        self._save_file(
            REWARDS_FILE,
            self.rewards,
        )

    def _save_history(self) -> None:

        self._save_file(
            HISTORY_FILE,
            self.history,
        )

    # ========================================================
    # USER HISTORY
    # ========================================================

    def _user_key(
        self,
        user_id: int,
    ) -> str:

        return str(user_id)

    def _new_user_history(self) -> Dict[str, Any]:

        return {
            "stories_seen": [],
            "story_completions": [],
            "mysteries_seen": [],
            "mystery_completions": [],
            "box_opens": 0,
            "rewards_received": [],
        }

    def get_user_history(
        self,
        user_id: int,
    ) -> Dict[str, Any]:

        key = self._user_key(user_id)

        if key not in self.history:

            self.history[key] = self._new_user_history()

            self._save_history()

        history = self.history[key]

        # Backward compatibility.
        defaults = self._new_user_history()

        for field, value in defaults.items():

            if field not in history:

                history[field] = value

        return history

    # ========================================================
    # STORIES
    # ========================================================

    def get_all_stories(self) -> List[Dict[str, Any]]:

        return list(self.stories)

    def get_story_by_id(
        self,
        story_id: str,
    ) -> Optional[Dict[str, Any]]:

        for story in self.stories:

            if story.get("id") == story_id:

                return story

        return None

    def get_story(
        self,
        user_id: Optional[int] = None,
        mood: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:

        stories = list(self.stories)

        if mood:

            mood = mood.lower().strip()

            matching = [
                story
                for story in stories
                if mood in [
                    str(item).lower()
                    for item in story.get(
                        "moods",
                        [],
                    )
                ]
            ]

            if matching:

                stories = matching

        if difficulty:

            difficulty = difficulty.lower().strip()

            matching = [
                story
                for story in stories
                if str(
                    story.get(
                        "difficulty",
                        "",
                    )
                ).lower() == difficulty
            ]

            if matching:

                stories = matching

        # Prefer unseen stories for a user.
        if user_id is not None:

            history = self.get_user_history(
                user_id
            )

            seen = set(
                history.get(
                    "stories_seen",
                    [],
                )
            )

            unseen = [
                story
                for story in stories
                if story.get("id") not in seen
            ]

            if unseen:

                stories = unseen

        if not stories:

            return None

        selected = random.choice(
            stories
        )

        if user_id is not None:

            history = self.get_user_history(
                user_id
            )

            story_id = selected.get("id")

            if (
                story_id
                and story_id
                not in history["stories_seen"]
            ):

                history["stories_seen"].append(
                    story_id
                )

                self._save_history()

        return selected

    def mark_story_seen(
        self,
        user_id: int,
        story_id: str,
    ) -> None:

        history = self.get_user_history(
            user_id
        )

        if story_id not in history["stories_seen"]:

            history["stories_seen"].append(
                story_id
            )

            self._save_history()

    def complete_story(
        self,
        user_id: int,
        story_id: str,
        ending_type: Optional[str] = None,
        reward_xp: Optional[int] = None,
    ) -> Dict[str, Any]:

        history = self.get_user_history(
            user_id
        )

        completion = {
            "story_id": story_id,
            "ending_type": ending_type,
            "reward_xp": int(
                reward_xp or 0
            ),
        }

        history["story_completions"].append(
            completion
        )

        self._save_history()

        return {
            "success": True,
            "story_id": story_id,
            "ending_type": ending_type,
            "xp": int(
                reward_xp or 0
            ),
        }

    # ========================================================
    # MYSTERIES
    # ========================================================

    def get_all_mysteries(
        self,
    ) -> List[Dict[str, Any]]:

        return list(self.mysteries)

    def get_mystery_by_id(
        self,
        mystery_id: str,
    ) -> Optional[Dict[str, Any]]:

        for mystery in self.mysteries:

            if mystery.get("id") == mystery_id:

                return mystery

        return None

    def get_mystery(
        self,
        user_id: Optional[int] = None,
        difficulty: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:

        mysteries = list(
            self.mysteries
        )

        if difficulty:

            difficulty = difficulty.lower().strip()

            matching = [
                mystery
                for mystery in mysteries
                if str(
                    mystery.get(
                        "difficulty",
                        "",
                    )
                ).lower() == difficulty
            ]

            if matching:

                mysteries = matching

        if user_id is not None:

            history = self.get_user_history(
                user_id
            )

            seen = set(
                history.get(
                    "mysteries_seen",
                    [],
                )
            )

            unseen = [
                mystery
                for mystery in mysteries
                if mystery.get("id") not in seen
            ]

            if unseen:

                mysteries = unseen

        if not mysteries:

            return None

        selected = random.choice(
            mysteries
        )

        if user_id is not None:

            history = self.get_user_history(
                user_id
            )

            mystery_id = selected.get("id")

            if (
                mystery_id
                and mystery_id
                not in history["mysteries_seen"]
            ):

                history["mysteries_seen"].append(
                    mystery_id
                )

                self._save_history()

        return selected

    def mark_mystery_seen(
        self,
        user_id: int,
        mystery_id: str,
    ) -> None:

        history = self.get_user_history(
            user_id
        )

        if (
            mystery_id
            not in history["mysteries_seen"]
        ):

            history["mysteries_seen"].append(
                mystery_id
            )

            self._save_history()

    def check_mystery_answer(
        self,
        mystery_id: str,
        answer_index: int,
    ) -> Dict[str, Any]:

        mystery = self.get_mystery_by_id(
            mystery_id
        )

        if not mystery:

            return {
                "success": False,
                "correct": False,
                "message": "Mystery not found.",
            }

        try:

            correct_answer = int(
                mystery.get(
                    "answer",
                    -1,
                )
            )

            selected_answer = int(
                answer_index
            )

        except (
            TypeError,
            ValueError,
        ):

            return {
                "success": False,
                "correct": False,
                "message": "Invalid answer.",
            }

        correct = (
            selected_answer
            == correct_answer
        )

        return {
            "success": True,
            "correct": correct,
            "xp": int(
                mystery.get(
                    "reward_xp",
                    0,
                )
            ) if correct else 0,
            "hint": mystery.get(
                "hint",
                "",
            ),
        }

    def complete_mystery(
        self,
        user_id: int,
        mystery_id: str,
        correct: bool = True,
        reward_xp: Optional[int] = None,
    ) -> Dict[str, Any]:

        history = self.get_user_history(
            user_id
        )

        completion = {
            "mystery_id": mystery_id,
            "correct": bool(correct),
            "reward_xp": int(
                reward_xp or 0
            ),
        }

        history["mystery_completions"].append(
            completion
        )

        self._save_history()

        return {
            "success": True,
            "mystery_id": mystery_id,
            "correct": bool(correct),
            "xp": int(
                reward_xp or 0
            ),
        }

    # ========================================================
    # MYSTERY BOX
    # ========================================================

    def get_mystery_box_reward(
        self,
        user_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:

        if not self.rewards:

            return None

        valid_rewards = []

        weights = []

        for reward in self.rewards:

            try:

                weight = float(
                    reward.get(
                        "weight",
                        1,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                weight = 1

            if weight > 0:

                valid_rewards.append(
                    reward
                )

                weights.append(
                    weight
                )

        if not valid_rewards:

            return None

        reward = random.choices(
            valid_rewards,
            weights=weights,
            k=1,
        )[0]

        if user_id is not None:

            history = self.get_user_history(
                user_id
            )

            history["box_opens"] = (
                int(
                    history.get(
                        "box_opens",
                        0,
                    )
                )
                + 1
            )

            history["rewards_received"].append(
                {
                    "reward_id": reward.get(
                        "id"
                    ),
                    "name": reward.get(
                        "name"
                    ),
                    "type": reward.get(
                        "type"
                    ),
                    "value": reward.get(
                        "value",
                        0,
                    ),
                }
            )

            self._save_history()

        return dict(reward)

    # ========================================================
    # REWARDS
    # ========================================================

    def get_all_rewards(
        self,
    ) -> List[Dict[str, Any]]:

        return list(self.rewards)

    def get_reward_by_id(
        self,
        reward_id: str,
    ) -> Optional[Dict[str, Any]]:

        for reward in self.rewards:

            if reward.get("id") == reward_id:

                return reward

        return None

    # ========================================================
    # ADD CONTENT
    # ========================================================

    def add_story(
        self,
        story: Dict[str, Any],
    ) -> bool:

        story_id = story.get("id")

        if not story_id:

            return False

        existing = self.get_story_by_id(
            story_id
        )

        if existing:

            return False

        self.stories.append(
            story
        )

        self._save_stories()

        return True

    def add_mystery(
        self,
        mystery: Dict[str, Any],
    ) -> bool:

        mystery_id = mystery.get(
            "id"
        )

        if not mystery_id:

            return False

        existing = self.get_mystery_by_id(
            mystery_id
        )

        if existing:

            return False

        self.mysteries.append(
            mystery
        )

        self._save_mysteries()

        return True

    def add_reward(
        self,
        reward: Dict[str, Any],
    ) -> bool:

        reward_id = reward.get(
            "id"
        )

        if not reward_id:

            return False

        existing = self.get_reward_by_id(
            reward_id
        )

        if existing:

            return False

        self.rewards.append(
            reward
        )

        self._save_rewards()

        return True

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(self) -> Dict[str, int]:

        total_completions = 0
        total_mystery_completions = 0
        total_box_opens = 0

        for history in self.history.values():

            if not isinstance(
                history,
                dict,
            ):
                continue

            total_completions += len(
                history.get(
                    "story_completions",
                    [],
                )
            )

            total_mystery_completions += len(
                history.get(
                    "mystery_completions",
                    [],
                )
            )

            total_box_opens += int(
                history.get(
                    "box_opens",
                    0,
                )
            )

        return {
            "stories": len(
                self.stories
            ),
            "mysteries": len(
                self.mysteries
            ),
            "rewards": len(
                self.rewards
            ),
            "users": len(
                self.history
            ),
            "story_completions": (
                total_completions
            ),
            "mystery_completions": (
                total_mystery_completions
            ),
            "box_opens": (
                total_box_opens
            ),
        }

    # ========================================================
    # RESET USER HISTORY
    # ========================================================

    def reset_user_history(
        self,
        user_id: int,
    ) -> None:

        key = self._user_key(
            user_id
        )

        self.history[key] = (
            self._new_user_history()
        )

        self._save_history()

    # ========================================================
    # RESET CONTENT
    # ========================================================

    def reset_content_to_defaults(
        self,
    ) -> None:

        self.stories = list(
            DEFAULT_STORIES
        )

        self.mysteries = list(
            DEFAULT_MYSTERIES
        )

        self.rewards = list(
            DEFAULT_REWARDS
        )

        self._save_stories()
        self._save_mysteries()
        self._save_rewards()


# ============================================================
# GLOBAL ENGINE
# ============================================================

content_engine = ContentEngine()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_story(
    user_id: Optional[int] = None,
    mood: Optional[str] = None,
    difficulty: Optional[str] = None,
) -> Optional[Dict[str, Any]]:

    return content_engine.get_story(
        user_id=user_id,
        mood=mood,
        difficulty=difficulty,
    )


def get_mystery(
    user_id: Optional[int] = None,
    difficulty: Optional[str] = None,
) -> Optional[Dict[str, Any]]:

    return content_engine.get_mystery(
        user_id=user_id,
        difficulty=difficulty,
    )


def get_mystery_box_reward(
    user_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:

    return content_engine.get_mystery_box_reward(
        user_id=user_id,
    )


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    "ContentEngine",
    "content_engine",
    "get_story",
    "get_mystery",
    "get_mystery_box_reward",
    "LONG_STORIES" if False else "DEFAULT_STORIES",
    "DEFAULT_MYSTERIES",
    "DEFAULT_REWARDS",
]