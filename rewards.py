# ============================================================
# MOODBLOOM 4.0 — DAILY REWARDS SYSTEM
# ============================================================
#
# Features:
#   • Daily random reward
#   • Same reward for the whole day
#   • One claim per day
#   • XP integration
#   • Level-up detection
#   • Reward claim streak
#   • Reward history
#   • Total reward statistics
#   • Total reward XP tracking
#   • Reward summary helpers
#   • Safe storage migration
#   • Backward compatibility
#
# ============================================================

import random
from datetime import datetime, timedelta

import config
import v4_data
import xp_system


# ============================================================
# REWARD DEFINITIONS
# ============================================================

REWARDS = [
    {
        "id": "small_bloom",
        "title": "Small Bloom",
        "message": "You completed another step today. 🌸",
        "xp": 10,
        "icon": "🌸",
        "rarity": "Common",
    },
    {
        "id": "bright_bloom",
        "title": "Bright Bloom",
        "message": "Nice work! Your consistency is growing. ✨",
        "xp": 15,
        "icon": "✨",
        "rarity": "Common",
    },
    {
        "id": "golden_bloom",
        "title": "Golden Bloom",
        "message": "You're building a beautiful habit. 🌟",
        "xp": 25,
        "icon": "🌟",
        "rarity": "Rare",
    },
    {
        "id": "super_bloom",
        "title": "Super Bloom",
        "message": "Amazing consistency! Keep blooming. 🌺",
        "xp": 40,
        "icon": "🌺",
        "rarity": "Epic",
    },
]


# ============================================================
# CONSTANTS
# ============================================================

MAX_REWARD_HISTORY = 365


# ============================================================
# TIME HELPERS
# ============================================================

def _now():
    """Return current timezone-aware datetime."""

    try:
        return datetime.now(config.TIMEZONE)
    except Exception:
        return datetime.now()


def today_key():
    """Return today's date as YYYY-MM-DD."""

    return _now().strftime("%Y-%m-%d")


# ============================================================
# BASIC HELPERS
# ============================================================

def _safe_int(value, default=0):
    """Safely convert a value to int."""

    try:
        return int(value)
    except Exception:
        return default


def _copy_reward(reward):
    """Return a safe reward copy."""

    if not isinstance(reward, dict):
        return {}

    return dict(reward)


def get_all_rewards():
    """Return all available reward definitions."""

    return [
        _copy_reward(reward)
        for reward in REWARDS
    ]


def get_reward_by_id(reward_id):
    """Find a reward by its ID."""

    reward_id = str(reward_id).strip()

    for reward in REWARDS:
        if reward.get("id") == reward_id:
            return _copy_reward(reward)

    return None


# ============================================================
# STORAGE INITIALIZATION
# ============================================================

def _initialize_reward_storage(storage):
    """
    Initialize today's reward storage.

    Existing history/statistics are preserved across days.
    """

    if not isinstance(storage, dict):
        storage = {}

    today = today_key()

    # --------------------------------------------------------
    # New day
    # --------------------------------------------------------

    if storage.get("date") != today:

        old_date = storage.get("date")
        old_reward = storage.get("reward")
        old_claimed = bool(
            storage.get("claimed", False)
        )

        history = storage.setdefault(
            "history",
            []
        )

        if not isinstance(history, list):
            history = []
            storage["history"] = history

        # Preserve previous day.
        if old_date and old_reward:
            history.append(
                {
                    "date": old_date,
                    "reward": _copy_reward(old_reward),
                    "claimed": old_claimed,
                }
            )

            if len(history) > MAX_REWARD_HISTORY:
                del history[:-MAX_REWARD_HISTORY]

        # Preserve long-term statistics.
        total_claims = _safe_int(
            storage.get("total_claims", 0)
        )

        total_xp = _safe_int(
            storage.get("total_xp", 0)
        )

        current_streak = _safe_int(
            storage.get("current_streak", 0)
        )

        longest_streak = _safe_int(
            storage.get("longest_streak", 0)
        )

        last_claim_date = storage.get(
            "last_claim_date"
        )

        created_at = storage.get(
            "created_at"
        ) or _now().isoformat()

        storage.clear()

        # Daily fields.
        storage["date"] = today
        storage["claimed"] = False
        storage["reward"] = None
        storage["claimed_at"] = None

        # Long-term fields.
        storage["total_claims"] = total_claims
        storage["total_xp"] = total_xp
        storage["current_streak"] = current_streak
        storage["longest_streak"] = longest_streak
        storage["last_claim_date"] = last_claim_date

        storage["history"] = history
        storage["created_at"] = created_at
        storage["updated_at"] = _now().isoformat()

    else:

        # ----------------------------------------------------
        # Existing day
        # ----------------------------------------------------

        storage.setdefault("claimed", False)
        storage.setdefault("reward", None)
        storage.setdefault("claimed_at", None)

        storage.setdefault("total_claims", 0)
        storage.setdefault("total_xp", 0)

        storage.setdefault("current_streak", 0)
        storage.setdefault("longest_streak", 0)

        storage.setdefault("last_claim_date", None)

        storage.setdefault("history", [])

        storage.setdefault(
            "created_at",
            _now().isoformat()
        )

        storage.setdefault(
            "updated_at",
            _now().isoformat()
        )

    # --------------------------------------------------------
    # Type safety
    # --------------------------------------------------------

    if not isinstance(
        storage.get("history"),
        list
    ):
        storage["history"] = []

    if len(storage["history"]) > MAX_REWARD_HISTORY:
        storage["history"] = storage["history"][
            -MAX_REWARD_HISTORY:
        ]

    return storage


# ============================================================
# GET REWARD STORAGE
# ============================================================

def _get_reward_storage(user_id):
    """
    Return today's reward storage.
    """

    data = v4_data.load_v4_data()

    user_id = str(user_id)

    rewards_root = data.setdefault(
        "rewards",
        {}
    )

    storage = rewards_root.setdefault(
        user_id,
        {}
    )

    _initialize_reward_storage(storage)

    storage["updated_at"] = _now().isoformat()

    v4_data.save_v4_data(data)

    return storage


# ============================================================
# INTERNAL DATA LOADER
# ============================================================

def _load_reward_storage_from_data(
    data,
    user_id
):
    """
    Internal helper when database is already loaded.
    """

    user_id = str(user_id)

    rewards_root = data.setdefault(
        "rewards",
        {}
    )

    storage = rewards_root.setdefault(
        user_id,
        {}
    )

    return _initialize_reward_storage(
        storage
    )


# ============================================================
# GENERATE / GET DAILY REWARD
# ============================================================

def get_daily_reward(user_id):
    """
    Get today's reward.

    The same reward remains assigned for the entire day.
    """

    data = v4_data.load_v4_data()

    storage = _load_reward_storage_from_data(
        data,
        user_id
    )

    # Existing reward.
    if storage.get("reward"):
        return_reward = _copy_reward(
            storage["reward"]
        )

        v4_data.save_v4_data(data)

        return return_reward

    # Generate new reward.
    reward = _copy_reward(
        random.choice(REWARDS)
    )

    reward["assigned_date"] = today_key()

    storage["reward"] = reward
    storage["updated_at"] = _now().isoformat()

    v4_data.save_v4_data(data)

    return _copy_reward(reward)


# ============================================================
# CLAIM DAILY REWARD
# ============================================================

def claim_daily_reward(user_id):
    """
    Claim today's reward.

    Only one claim is allowed per day.
    """

    user_id = str(user_id)

    data = v4_data.load_v4_data()

    storage = _load_reward_storage_from_data(
        data,
        user_id
    )

    # --------------------------------------------------------
    # Already claimed
    # --------------------------------------------------------

    if storage.get("claimed", False):

        return {
            "success": False,
            "already_claimed": True,
            "reward": _copy_reward(
                storage.get("reward")
            ),
            "xp": 0,
            "streak": _safe_int(
                storage.get(
                    "current_streak",
                    0
                )
            ),
            "longest_streak": _safe_int(
                storage.get(
                    "longest_streak",
                    0
                )
            ),
        }

    # --------------------------------------------------------
    # Get or create reward
    # --------------------------------------------------------

    reward = storage.get("reward")

    if not reward:

        reward = _copy_reward(
            random.choice(REWARDS)
        )

        reward["assigned_date"] = today_key()

        storage["reward"] = reward

    # --------------------------------------------------------
    # Validate XP
    # --------------------------------------------------------

    xp = _safe_int(
        reward.get("xp", 10),
        10
    )

    xp = max(0, xp)

    # --------------------------------------------------------
    # Mark claimed
    # --------------------------------------------------------

    claimed_at = _now().isoformat()

    storage["claimed"] = True
    storage["claimed_at"] = claimed_at

    # --------------------------------------------------------
    # Claim statistics
    # --------------------------------------------------------

    storage["total_claims"] = (
        _safe_int(
            storage.get("total_claims", 0)
        ) + 1
    )

    storage["total_xp"] = (
        _safe_int(
            storage.get("total_xp", 0)
        ) + xp
    )

    # --------------------------------------------------------
    # Reward streak
    # --------------------------------------------------------

    streak_result = _calculate_claim_streak(
        storage
    )

    storage["current_streak"] = (
        streak_result["current_streak"]
    )

    storage["longest_streak"] = (
        streak_result["longest_streak"]
    )

    storage["last_claim_date"] = today_key()

    storage["updated_at"] = claimed_at

    # --------------------------------------------------------
    # Reward history
    # --------------------------------------------------------

    history = storage.setdefault(
        "history",
        []
    )

    if not isinstance(history, list):
        history = []
        storage["history"] = history

    history.append(
        {
            "date": today_key(),
            "reward": _copy_reward(reward),
            "claimed": True,
            "xp": xp,
            "claimed_at": claimed_at,
        }
    )

    if len(history) > MAX_REWARD_HISTORY:
        del history[:-MAX_REWARD_HISTORY]

    # --------------------------------------------------------
    # Save reward state first.
    # --------------------------------------------------------

    v4_data.save_v4_data(data)

    # --------------------------------------------------------
    # Central XP system.
    # --------------------------------------------------------

    try:
        xp_result = xp_system.add_xp(
            user_id,
            xp,
            source=f"reward:{reward.get('id', 'daily')}",
        )
    except TypeError:
        # Backward compatibility with an older
        # xp_system.add_xp signature.
        xp_result = xp_system.add_xp(
            user_id,
            xp
        )

    if not isinstance(xp_result, dict):
        xp_result = {}

    # --------------------------------------------------------
    # Update user reward statistics.
    # --------------------------------------------------------

    data = v4_data.load_v4_data()

    users = data.setdefault(
        "users",
        {}
    )

    user = users.setdefault(
        user_id,
        {}
    )

    user["reward_claims"] = (
        _safe_int(
            user.get("reward_claims", 0)
        ) + 1
    )

    user["reward_xp_earned"] = (
        _safe_int(
            user.get(
                "reward_xp_earned",
                0
            )
        ) + xp
    )

    user["updated_at"] = _now().isoformat()

    reward_stats = user.setdefault(
        "reward_stats",
        {}
    )

    if not isinstance(
        reward_stats,
        dict
    ):
        reward_stats = {}
        user["reward_stats"] = reward_stats

    reward_stats["total_claims"] = (
        _safe_int(
            reward_stats.get(
                "total_claims",
                0
            )
        ) + 1
    )

    reward_stats["total_xp"] = (
        _safe_int(
            reward_stats.get(
                "total_xp",
                0
            )
        ) + xp
    )

    reward_stats["last_reward"] = (
        _copy_reward(reward)
    )

    reward_stats["last_claimed_at"] = (
        claimed_at
    )

    reward_stats["current_streak"] = (
        streak_result["current_streak"]
    )

    reward_stats["longest_streak"] = (
        streak_result["longest_streak"]
    )

    v4_data.save_v4_data(data)

    # --------------------------------------------------------
    # Final result.
    # --------------------------------------------------------

    return {
        "success": True,
        "already_claimed": False,

        "reward": _copy_reward(reward),

        "xp": xp,

        "streak": streak_result[
            "current_streak"
        ],

        "longest_streak": streak_result[
            "longest_streak"
        ],

        "new_streak": streak_result[
            "new_streak"
        ],

        "total_claims": _safe_int(
            storage.get(
                "total_claims",
                0
            )
        ),

        "total_reward_xp": _safe_int(
            storage.get(
                "total_xp",
                0
            )
        ),

        "level_up": bool(
            xp_result.get(
                "level_up",
                False
            )
        ),

        "old_level": xp_result.get(
            "old_level"
        ),

        "new_level": xp_result.get(
            "new_level"
        ),

        "new_title": xp_result.get(
            "new_title"
        ),

        "claimed_at": claimed_at,
    }


# ============================================================
# CLAIM STREAK CALCULATION
# ============================================================

def _calculate_claim_streak(storage):
    """
    Calculate reward claim streak.

    Called after today's reward is marked as claimed.
    """

    today = today_key()

    previous_date = storage.get(
        "last_claim_date"
    )

    current = _safe_int(
        storage.get(
            "current_streak",
            0
        )
    )

    longest = _safe_int(
        storage.get(
            "longest_streak",
            0
        )
    )

    # Already processed today.
    if previous_date == today:

        return {
            "current_streak": current,
            "longest_streak": longest,
            "new_streak": False,
        }

    yesterday = (
        _now() - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    if previous_date == yesterday:
        current += 1
    else:
        current = 1

    longest = max(
        longest,
        current
    )

    return {
        "current_streak": current,
        "longest_streak": longest,
        "new_streak": True,
    }


# ============================================================
# GET REWARD STREAK
# ============================================================

def get_reward_streak(user_id):
    """
    Return reward claim streak information.
    """

    storage = _get_reward_storage(
        user_id
    )

    return {
        "current": _safe_int(
            storage.get(
                "current_streak",
                0
            )
        ),
        "longest": _safe_int(
            storage.get(
                "longest_streak",
                0
            )
        ),
        "last_claim_date": storage.get(
            "last_claim_date"
        ),
    }


# ============================================================
# GET REWARD STATUS
# ============================================================

def get_reward_status(user_id):
    """
    Return today's reward status.
    """

    storage = _get_reward_storage(
        user_id
    )

    reward = storage.get(
        "reward"
    )

    return {
        "date": storage.get(
            "date"
        ),

        "reward": (
            _copy_reward(reward)
            if reward
            else None
        ),

        "claimed": bool(
            storage.get(
                "claimed",
                False
            )
        ),

        "claimed_at": storage.get(
            "claimed_at"
        ),

        "current_streak": _safe_int(
            storage.get(
                "current_streak",
                0
            )
        ),

        "longest_streak": _safe_int(
            storage.get(
                "longest_streak",
                0
            )
        ),
    }


# ============================================================
# GET REWARD HISTORY
# ============================================================

def get_reward_history(
    user_id,
    limit=30
):
    """
    Return recent reward history.
    """

    try:
        limit = int(limit)
    except Exception:
        limit = 30

    limit = max(
        1,
        min(
            limit,
            MAX_REWARD_HISTORY
        )
    )

    storage = _get_reward_storage(
        user_id
    )

    history = storage.get(
        "history",
        []
    )

    if not isinstance(history, list):
        return []

    return list(
        reversed(
            history[-limit:]
        )
    )


# ============================================================
# GET REWARD STATISTICS
# ============================================================

def get_reward_stats(user_id):
    """
    Return complete reward statistics.
    """

    storage = _get_reward_storage(
        user_id
    )

    try:
        user = v4_data.get_user(
            user_id
        )
    except Exception:
        user = {}

    if not isinstance(user, dict):
        user = {}

    reward_stats = user.get(
        "reward_stats",
        {}
    )

    if not isinstance(
        reward_stats,
        dict
    ):
        reward_stats = {}

    return {
        "total_claims": _safe_int(
            reward_stats.get(
                "total_claims",
                storage.get(
                    "total_claims",
                    0
                )
            )
        ),

        "total_xp": _safe_int(
            reward_stats.get(
                "total_xp",
                storage.get(
                    "total_xp",
                    0
                )
            )
        ),

        "current_streak": _safe_int(
            reward_stats.get(
                "current_streak",
                storage.get(
                    "current_streak",
                    0
                )
            )
        ),

        "longest_streak": _safe_int(
            reward_stats.get(
                "longest_streak",
                storage.get(
                    "longest_streak",
                    0
                )
            )
        ),

        "last_reward": reward_stats.get(
            "last_reward"
        ),

        "last_claimed_at": reward_stats.get(
            "last_claimed_at"
        ),
    }


# ============================================================
# CHECK IF CLAIMED
# ============================================================

def has_claimed_today(user_id):
    """
    Return True if today's reward was claimed.
    """

    storage = _get_reward_storage(
        user_id
    )

    return bool(
        storage.get(
            "claimed",
            False
        )
    )


# ============================================================
# GET TODAY'S REWARD XP
# ============================================================

def get_today_reward_xp(user_id):
    """
    Return today's reward XP.

    Returns 0 if reward has not been claimed.
    """

    storage = _get_reward_storage(
        user_id
    )

    if not storage.get(
        "claimed",
        False
    ):
        return 0

    reward = storage.get(
        "reward"
    )

    if not reward:
        return 0

    return _safe_int(
        reward.get(
            "xp",
            0
        )
    )


# ============================================================
# FORMAT REWARD
# ============================================================

def format_reward(
    reward,
    claimed=False
):
    """
    Format a reward for Telegram.
    """

    if not isinstance(
        reward,
        dict
    ):
        return ""

    icon = reward.get(
        "icon",
        "🎁"
    )

    title = reward.get(
        "title",
        "Daily Reward"
    )

    message = reward.get(
        "message",
        ""
    )

    xp = _safe_int(
        reward.get(
            "xp",
            0
        )
    )

    rarity = reward.get(
        "rarity",
        "Common"
    )

    status = (
        "✅ Claimed"
        if claimed
        else "🎁 Available"
    )

    return (
        f"{icon} *{title}*\n"
        f"{message}\n\n"
        f"⭐ +{xp} XP\n"
        f"💎 Rarity: {rarity}\n"
        f"{status}"
    )


# ============================================================
# FORMAT DAILY REWARD SUMMARY
# ============================================================

def format_reward_summary(user_id):
    """
    Return a user-friendly daily reward summary.
    """

    status = get_reward_status(
        user_id
    )

    reward = status.get(
        "reward"
    )

    if not reward:

        reward = get_daily_reward(
            user_id
        )

        status = get_reward_status(
            user_id
        )

    reward_text = format_reward(
        reward,
        claimed=status.get(
            "claimed",
            False
        )
    )

    streak = status.get(
        "current_streak",
        0
    )

    if status.get(
        "claimed",
        False
    ):

        footer = (
            f"🔥 Reward streak: "
            f"{streak} day(s)"
        )

    else:

        footer = (
            "🎁 Your reward is waiting!"
        )

    return (
        "🎁 *Daily Reward*\n\n"
        f"{reward_text}\n\n"
        f"{footer}"
    )


# ============================================================
# RESET DAILY REWARD
# ============================================================

def reset_daily_reward(user_id):
    """
    Reset only today's reward state.

    Historical reward statistics are preserved.
    """

    data = v4_data.load_v4_data()

    user_id = str(user_id)

    rewards_root = data.setdefault(
        "rewards",
        {}
    )

    storage = rewards_root.get(
        user_id
    )

    if not isinstance(
        storage,
        dict
    ):
        return True

    history = storage.get(
        "history",
        []
    )

    total_claims = storage.get(
        "total_claims",
        0
    )

    total_xp = storage.get(
        "total_xp",
        0
    )

    current_streak = storage.get(
        "current_streak",
        0
    )

    longest_streak = storage.get(
        "longest_streak",
        0
    )

    last_claim_date = storage.get(
        "last_claim_date"
    )

    created_at = storage.get(
        "created_at"
    ) or _now().isoformat()

    storage.clear()

    storage["date"] = today_key()
    storage["claimed"] = False
    storage["reward"] = None
    storage["claimed_at"] = None

    storage["history"] = history
    storage["total_claims"] = total_claims
    storage["total_xp"] = total_xp

    storage["current_streak"] = current_streak
    storage["longest_streak"] = longest_streak

    storage["last_claim_date"] = last_claim_date

    storage["created_at"] = created_at
    storage["updated_at"] = _now().isoformat()

    v4_data.save_v4_data(data)

    return True


# ============================================================
# RESET ALL REWARD DATA
# ============================================================

def reset_all_reward_data(user_id):
    """
    Completely remove reward data.

    XP already earned is intentionally NOT removed.
    """

    data = v4_data.load_v4_data()

    user_id = str(user_id)

    data.setdefault(
        "rewards",
        {}
    ).pop(
        user_id,
        None
    )

    user = data.setdefault(
        "users",
        {}
    ).get(
        user_id
    )

    if isinstance(
        user,
        dict
    ):

        user.pop(
            "reward_stats",
            None
        )

        user.pop(
            "reward_claims",
            None
        )

        user.pop(
            "reward_xp_earned",
            None
        )

        user["updated_at"] = (
            _now().isoformat()
        )

    v4_data.save_v4_data(data)

    return True


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "REWARDS",

    "today_key",

    "get_all_rewards",
    "get_reward_by_id",

    "get_daily_reward",
    "claim_daily_reward",

    "get_reward_streak",
    "get_reward_status",

    "get_reward_history",
    "get_reward_stats",

    "has_claimed_today",
    "get_today_reward_xp",

    "format_reward",
    "format_reward_summary",

    "reset_daily_reward",
    "reset_all_reward_data",
]

