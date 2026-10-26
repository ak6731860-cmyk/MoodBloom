# ============================================================
# MOODBLOOM 4.0 — XP & LEVEL SYSTEM
# ============================================================
#
# Handles:
#   • XP earning
#   • Level calculation
#   • Level-up detection
#   • XP progress
#   • XP history
#   • Daily / weekly / monthly XP
#   • Profile formatting
#   • Bloom Journey XP support
#
# Study Mode is intentionally NOT handled here.
# ============================================================

from datetime import datetime

import v4_data


# ============================================================
# LEVEL CONFIGURATION
# ============================================================

LEVELS = [
    (1, 0, "🌱 Seed"),
    (2, 100, "🌿 Sprout"),
    (3, 250, "🌷 Bud"),
    (4, 450, "🌸 Bloom"),
    (5, 700, "🌺 Flourish"),
    (6, 1000, "🌳 Evergreen"),
    (7, 1400, "✨ Radiant"),
    (8, 1900, "💫 Shining"),
    (9, 2500, "👑 Bloom Master"),
    (10, 3300, "🏆 Legendary Bloom"),
]


# ============================================================
# XP LIMITS
# ============================================================

MAX_LEVEL = LEVELS[-1][0]
MAX_XP = LEVELS[-1][1]


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _now():
    try:
        return datetime.now(
            v4_data.config.TIMEZONE
        )
    except Exception:
        return datetime.now()


def _today():
    return _now().strftime("%Y-%m-%d")


def _week_key():
    current = _now()

    return (
        f"{current.isocalendar().year}"
        f"-W{current.isocalendar().week:02d}"
    )


def _month_key():
    return _now().strftime("%Y-%m")


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


# ============================================================
# LEVEL INFORMATION
# ============================================================

def get_level_info(xp):
    """
    Return level information for a given XP value.

    Example:
        get_level_info(500)
    """

    xp = max(
        0,
        _safe_int(xp)
    )

    current = LEVELS[0]

    for level in LEVELS:

        if xp >= level[1]:
            current = level

        else:
            break

    return {
        "level": current[0],
        "required_xp": current[1],
        "title": current[2],
        "is_max_level": (
            current[0] >= MAX_LEVEL
        ),
    }


# ============================================================
# USER LEVEL
# ============================================================

def get_user_level(user_id):
    """
    Return the current level information of a user.
    """

    user = v4_data.get_user(
        user_id
    )

    xp = _safe_int(
        user.get("xp", 0)
    )

    return get_level_info(
        xp
    )


# ============================================================
# USER PROGRESS
# ============================================================

def get_progress(user_id):
    """
    Return detailed XP progress information.
    """

    user = v4_data.get_user(
        user_id
    )

    xp = max(
        0,
        _safe_int(
            user.get(
                "xp",
                0
            )
        )
    )

    current = get_level_info(
        xp
    )

    current_level = current["level"]

    if current_level >= MAX_LEVEL:

        return {
            "xp": xp,
            "level": current_level,
            "title": current["title"],

            "current_level_xp": current["required_xp"],
            "next_level_xp": None,

            "progress": 100,
            "remaining": 0,

            "is_max_level": True,
        }

    # LEVELS are 1-indexed by level number,
    # therefore the next level is at index current_level.
    next_level = LEVELS[
        current_level
    ]

    current_xp = current["required_xp"]
    next_xp = next_level[1]

    needed = next_xp - current_xp
    gained = xp - current_xp

    if needed <= 0:
        progress = 100

    else:
        progress = round(
            gained / needed * 100
        )

    progress = max(
        0,
        min(
            100,
            progress
        )
    )

    return {
        "xp": xp,
        "level": current_level,
        "title": current["title"],

        "current_level_xp": current_xp,
        "next_level_xp": next_xp,

        "progress": progress,
        "remaining": max(
            0,
            next_xp - xp
        ),

        "is_max_level": False,
    }


# ============================================================
# PROGRESS BAR
# ============================================================

def progress_bar(
    user_id,
    width=12
):
    """
    Return a text XP progress bar.
    """

    try:
        width = int(width)
    except Exception:
        width = 12

    width = max(
        1,
        min(
            50,
            width
        )
    )

    info = get_progress(
        user_id
    )

    filled = round(
        info["progress"]
        / 100
        * width
    )

    filled = max(
        0,
        min(
            width,
            filled
        )
    )

    return (
        "█" * filled
        + "░" * (
            width - filled
        )
    )


# ============================================================
# XP HISTORY
# ============================================================

def _record_xp_history(
    user,
    amount,
    source=None
):
    """
    Store a compact XP history record.

    History is capped to prevent unlimited database growth.
    """

    metadata = user.setdefault(
        "metadata",
        {}
    )

    history = metadata.setdefault(
        "xp_history",
        []
    )

    history.append(
        {
            "amount": amount,
            "source": source or "unknown",
            "timestamp": _now().isoformat(),
        }
    )

    # Keep most recent 500 records.
    if len(history) > 500:
        del history[:-500]


# ============================================================
# ADD XP
# ============================================================

def add_xp(
    user_id,
    amount,
    source=None
):
    """
    Add XP to a user.

    Returns detailed information about the XP transaction
    and any level-up that occurred.
    """

    amount = _safe_int(
        amount
    )

    if amount <= 0:

        current = get_user_level(
            user_id
        )

        user = v4_data.get_user(
            user_id
        )

        old_xp = _safe_int(
            user.get(
                "xp",
                0
            )
        )

        return {
            "success": False,
            "xp_added": 0,

            "old_xp": old_xp,
            "new_xp": old_xp,

            "old_level": current["level"],
            "new_level": current["level"],

            "level_up": False,
            "levels_gained": 0,

            "new_title": current["title"],
            "source": source or "unknown",
        }

    user = v4_data.get_user(
        user_id
    )

    old_xp = max(
        0,
        _safe_int(
            user.get(
                "xp",
                0
            )
        )
    )

    old_level_info = get_level_info(
        old_xp
    )

    old_level = old_level_info[
        "level"
    ]

    new_xp = old_xp + amount

    new_level_info = get_level_info(
        new_xp
    )

    new_level = new_level_info[
        "level"
    ]

    # --------------------------------------------------------
    # Update XP values
    # --------------------------------------------------------

    user["xp"] = new_xp

    user["total_xp_earned"] = (
        max(
            0,
            _safe_int(
                user.get(
                    "total_xp_earned",
                    0
                )
            )
        )
        + amount
    )

    user["xp_today"] = (
        max(
            0,
            _safe_int(
                user.get(
                    "xp_today",
                    0
                )
            )
        )
        + amount
    )

    user["xp_this_week"] = (
        max(
            0,
            _safe_int(
                user.get(
                    "xp_this_week",
                    0
                )
            )
        )
        + amount
    )

    user["xp_this_month"] = (
        max(
            0,
            _safe_int(
                user.get(
                    "xp_this_month",
                    0
                )
            )
        )
        + amount
    )

    user["journey_xp"] = (
        max(
            0,
            _safe_int(
                user.get(
                    "journey_xp",
                    0
                )
            )
        )
        + amount
    )

    user["level"] = new_level

    # --------------------------------------------------------
    # XP history
    # --------------------------------------------------------

    _record_xp_history(
        user,
        amount,
        source
    )

    # --------------------------------------------------------
    # Level-up metadata
    # --------------------------------------------------------

    if new_level > old_level:

        user.setdefault(
            "metadata",
            {}
        )["last_level_up"] = {
            "from_level": old_level,
            "to_level": new_level,
            "timestamp": _now().isoformat(),
        }

    # --------------------------------------------------------
    # Save complete user object
    # --------------------------------------------------------

    updated_user = v4_data.update_user(
        user_id,
        user
    )

    return {
        "success": True,

        "xp_added": amount,

        "old_xp": old_xp,
        "new_xp": new_xp,

        "old_level": old_level,
        "new_level": new_level,

        "level_up": (
            new_level > old_level
        ),

        "levels_gained": max(
            0,
            new_level - old_level
        ),

        "new_title": new_level_info[
            "title"
        ],

        "old_title": old_level_info[
            "title"
        ],

        "source": source or "unknown",

        "user": updated_user,
    }


# ============================================================
# REMOVE XP
# ============================================================

def remove_xp(
    user_id,
    amount
):
    """
    Remove XP safely.

    XP will never go below zero.

    This function is useful for corrections/admin systems.
    """

    amount = _safe_int(
        amount
    )

    if amount <= 0:

        user = v4_data.get_user(
            user_id
        )

        return {
            "success": False,
            "xp_removed": 0,
            "old_xp": _safe_int(
                user.get(
                    "xp",
                    0
                )
            ),
            "new_xp": _safe_int(
                user.get(
                    "xp",
                    0
                )
            ),
        }

    user = v4_data.get_user(
        user_id
    )

    old_xp = max(
        0,
        _safe_int(
            user.get(
                "xp",
                0
            )
        )
    )

    new_xp = max(
        0,
        old_xp - amount
    )

    actual_removed = (
        old_xp - new_xp
    )

    old_level = get_level_info(
        old_xp
    )["level"]

    new_level = get_level_info(
        new_xp
    )["level"]

    user["xp"] = new_xp
    user["level"] = new_level

    # Do not reduce lifetime earned XP.
    user["total_xp_earned"] = max(
        0,
        _safe_int(
            user.get(
                "total_xp_earned",
                0
            )
        )
    )

    v4_data.update_user(
        user_id,
        user
    )

    return {
        "success": actual_removed > 0,
        "xp_removed": actual_removed,

        "old_xp": old_xp,
        "new_xp": new_xp,

        "old_level": old_level,
        "new_level": new_level,

        "level_down": (
            new_level < old_level
        ),
    }


# ============================================================
# SET XP
# ============================================================

def set_xp(
    user_id,
    xp
):
    """
    Directly set current XP.

    Intended for admin/testing/recovery purposes.
    """

    xp = max(
        0,
        _safe_int(
            xp
        )
    )

    user = v4_data.get_user(
        user_id
    )

    old_xp = max(
        0,
        _safe_int(
            user.get(
                "xp",
                0
            )
        )
    )

    old_level = get_level_info(
        old_xp
    )["level"]

    new_level_info = get_level_info(
        xp
    )

    user["xp"] = xp
    user["level"] = new_level_info[
        "level"
    ]

    v4_data.update_user(
        user_id,
        user
    )

    return {
        "success": True,

        "old_xp": old_xp,
        "new_xp": xp,

        "old_level": old_level,
        "new_level": new_level_info[
            "level"
        ],

        "level_changed": (
            old_level
            != new_level_info["level"]
        ),

        "title": new_level_info[
            "title"
        ],
    }


# ============================================================
# XP SUMMARY
# ============================================================

def get_xp_summary(
    user_id
):
    """
    Return a complete XP summary for dashboards/profiles.
    """

    user = v4_data.get_user(
        user_id
    )

    progress = get_progress(
        user_id
    )

    return {
        "xp": _safe_int(
            user.get(
                "xp",
                0
            )
        ),

        "total_xp_earned": _safe_int(
            user.get(
                "total_xp_earned",
                0
            )
        ),

        "xp_today": _safe_int(
            user.get(
                "xp_today",
                0
            )
        ),

        "xp_this_week": _safe_int(
            user.get(
                "xp_this_week",
                0
            )
        ),

        "xp_this_month": _safe_int(
            user.get(
                "xp_this_month",
                0
            )
        ),

        "journey_xp": _safe_int(
            user.get(
                "journey_xp",
                0
            )
        ),

        "level": progress[
            "level"
        ],

        "title": progress[
            "title"
        ],

        "progress": progress[
            "progress"
        ],

        "remaining": progress[
            "remaining"
        ],

        "next_level_xp": progress[
            "next_level_xp"
        ],

        "is_max_level": progress[
            "is_max_level"
        ],
    }


# ============================================================
# RESET PERIOD XP
# ============================================================

def reset_daily_xp(
    user_id
):
    """
    Reset daily XP counter.
    """

    return v4_data.update_user(
        user_id,
        {
            "xp_today": 0
        }
    )


def reset_weekly_xp(
    user_id
):
    """
    Reset weekly XP counter.
    """

    return v4_data.update_user(
        user_id,
        {
            "xp_this_week": 0
        }
    )


def reset_monthly_xp(
    user_id
):
    """
    Reset monthly XP counter.
    """

    return v4_data.update_user(
        user_id,
        {
            "xp_this_month": 0
        }
    )


# ============================================================
# LEVEL-UP MESSAGE
# ============================================================

def format_level_up(
    result
):
    """
    Create a user-friendly level-up message.
    """

    if not result:
        return ""

    if not result.get(
        "level_up",
        False
    ):
        return ""

    new_level = result.get(
        "new_level",
        1
    )

    title = result.get(
        "new_title",
        "🌱 Seed"
    )

    return (
        "🎉 LEVEL UP!\n\n"
        f"🌸 You reached "
        f"Level {new_level}\n"
        f"✨ Title: {title}\n"
        f"💫 +{result.get('xp_added', 0)} XP"
    )


# ============================================================
# PROFILE FORMAT
# ============================================================

def format_profile(
    user_id
):
    """
    Return a compact profile XP display.
    """

    info = get_progress(
        user_id
    )

    bar = progress_bar(
        user_id
    )

    if info["next_level_xp"] is None:

        xp_line = (
            f"✨ {info['xp']} XP — "
            f"MAX LEVEL"
        )

    else:

        xp_line = (
            f"✨ {info['xp']} / "
            f"{info['next_level_xp']} XP"
        )

    return (
        f"⭐ Level {info['level']} "
        f"— {info['title']}\n"
        f"{xp_line}\n"
        f"{bar} "
        f"{info['progress']}%"
    )


# ============================================================
# DETAILED PROFILE
# ============================================================

def format_detailed_profile(
    user_id
):
    """
    Detailed XP profile for future profile/dashboard UI.
    """

    summary = get_xp_summary(
        user_id
    )

    bar = progress_bar(
        user_id,
        width=16
    )

    if summary["is_max_level"]:

        next_line = (
            "🏆 Maximum Bloom Level reached!"
        )

    else:

        next_line = (
            f"🎯 Next level: "
            f"{summary['next_level_xp']} XP\n"
            f"📌 Remaining: "
            f"{summary['remaining']} XP"
        )

    return (
        f"🌸 MOODBLOOM PROFILE\n\n"
        f"⭐ Level: {summary['level']}\n"
        f"🏷️ Title: {summary['title']}\n\n"
        f"{bar} {summary['progress']}%\n"
        f"✨ XP: "
        f"{summary['xp']}\n"
        f"📈 Total earned: "
        f"{summary['total_xp_earned']}\n\n"
        f"☀️ Today: "
        f"{summary['xp_today']} XP\n"
        f"📅 This week: "
        f"{summary['xp_this_week']} XP\n"
        f"🗓️ This month: "
        f"{summary['xp_this_month']} XP\n\n"
        f"{next_line}"
    )


# ============================================================
# LEVEL TABLE
# ============================================================

def get_all_levels():
    """
    Return all configured levels.
    """

    return [
        {
            "level": level,
            "xp": xp,
            "title": title,
        }
        for level, xp, title in LEVELS
    ]


# ============================================================
# XP REQUIRED FOR NEXT LEVEL
# ============================================================

def xp_required_for_next_level(
    user_id
):
    """
    Return XP required to reach the next level.
    """

    progress = get_progress(
        user_id
    )

    return progress[
        "remaining"
    ]


# ============================================================
# CURRENT TITLE
# ============================================================

def get_user_title(
    user_id
):
    """
    Return the current Bloom title.
    """

    return get_user_level(
        user_id
    )["title"]


# ============================================================
# LEVEL CHECK
# ============================================================

def check_level_up(
    user_id,
    previous_level=None
):
    """
    Check whether the current level is above a supplied
    previous level.

    If previous_level is omitted, returns current level info.
    """

    current = get_user_level(
        user_id
    )

    current_level = current[
        "level"
    ]

    if previous_level is None:

        return {
            "level_up": False,
            "level": current_level,
            "title": current["title"],
        }

    previous_level = _safe_int(
        previous_level
    )

    return {
        "level_up": (
            current_level
            > previous_level
        ),

        "old_level": previous_level,
        "new_level": current_level,

        "levels_gained": max(
            0,
            current_level
            - previous_level
        ),

        "title": current["title"],
    }


# ============================================================
# MODULE READY
# ============================================================

__all__ = [
    "LEVELS",
    "MAX_LEVEL",
    "MAX_XP",

    "get_level_info",
    "get_user_level",
    "get_progress",
    "progress_bar",

    "add_xp",
    "remove_xp",
    "set_xp",

    "get_xp_summary",

    "reset_daily_xp",
    "reset_weekly_xp",
    "reset_monthly_xp",

    "format_level_up",
    "format_profile",
    "format_detailed_profile",

    "get_all_levels",
    "xp_required_for_next_level",
    "get_user_title",
    "check_level_up",
]

