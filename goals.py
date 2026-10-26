# ============================================================
# MOODBLOOM 4.0 — DAILY GOALS SYSTEM
# ============================================================
#
# Features:
#   • Daily default goals
#   • Custom goals
#   • Goal completion tracking
#   • XP integration
#   • Level-up detection
#   • Goal streaks
#   • Completion timestamps
#   • Daily progress
#   • Goal history
#   • Goal statistics
#   • Safe daily reset
#   • Backward-compatible storage
#
# ============================================================

from datetime import datetime, timedelta

import config
import v4_data
import xp_system


# ============================================================
# DEFAULT GOALS
# ============================================================

DEFAULT_GOALS = [
    {
        "id": "mood_check",
        "title": "Mood Check-in",
        "description": "Record your mood today.",
        "xp": 10,
        "icon": "💭",
    },
    {
        "id": "positive_activity",
        "title": "Positive Activity",
        "description": "Do one small activity that makes you feel good.",
        "xp": 15,
        "icon": "🌸",
    },
    {
        "id": "study",
        "title": "Study Session",
        "description": "Complete at least one focused study session.",
        "xp": 20,
        "icon": "📚",
    },
    {
        "id": "break",
        "title": "Take a Break",
        "description": "Take a proper short break today.",
        "xp": 10,
        "icon": "☕",
    },
]


# ============================================================
# CONSTANTS
# ============================================================

MIN_CUSTOM_XP = 5
MAX_CUSTOM_XP = 100
MAX_HISTORY_ITEMS = 365


# ============================================================
# TIME HELPERS
# ============================================================

def _now():
    try:
        return datetime.now(config.TIMEZONE)
    except Exception:
        return datetime.now()


def today_key():
    return _now().strftime("%Y-%m-%d")


def _week_key(date_obj=None):
    if date_obj is None:
        date_obj = _now()

    try:
        return date_obj.strftime("%G-W%V")
    except Exception:
        return date_obj.strftime("%Y-W%W")


def _month_key(date_obj=None):
    if date_obj is None:
        date_obj = _now()

    return date_obj.strftime("%Y-%m")


# ============================================================
# BASIC HELPERS
# ============================================================

def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _safe_string(value):
    try:
        return str(value).strip()
    except Exception:
        return ""


def _default_available_ids():
    return [goal["id"] for goal in DEFAULT_GOALS]


def _copy_goal(goal):
    if not isinstance(goal, dict):
        return {}

    return dict(goal)


# ============================================================
# DEFAULT GOALS
# ============================================================

def get_default_goals():
    return [
        _copy_goal(goal)
        for goal in DEFAULT_GOALS
    ]


# ============================================================
# HISTORY HELPER
# ============================================================

def _append_daily_history(storage):
    """
    Preserve the previous day's goal summary.

    Important:
    This must happen BEFORE today's storage is reset.
    """

    previous_date = storage.get("date")

    if not previous_date:
        return

    previous_completed = storage.get(
        "completed",
        []
    )

    if not isinstance(previous_completed, list):
        previous_completed = []

    previous_custom = storage.get(
        "custom",
        []
    )

    if not isinstance(previous_custom, list):
        previous_custom = []

    history = storage.get(
        "history",
        []
    )

    if not isinstance(history, list):
        history = []

    # Prevent duplicate history entry.
    for item in history:
        if (
            isinstance(item, dict)
            and item.get("date") == previous_date
        ):
            return

    total = (
        len(DEFAULT_GOALS)
        + len(previous_custom)
    )

    history.append(
        {
            "date": previous_date,
            "completed": len(previous_completed),
            "total": total,
            "percentage": (
                round(
                    len(previous_completed)
                    / total
                    * 100
                )
                if total
                else 0
            ),
            "completed_ids": list(
                previous_completed
            ),
            "custom_count": len(
                previous_custom
            ),
        }
    )

    if len(history) > MAX_HISTORY_ITEMS:
        del history[:-MAX_HISTORY_ITEMS]

    storage["history"] = history


# ============================================================
# STORAGE INITIALIZATION
# ============================================================

def _initialize_goal_storage(storage):
    """
    Initialize or migrate goal storage safely.

    Keeps historical data when a new day starts.
    """

    if not isinstance(storage, dict):
        storage = {}

    today = today_key()

    # --------------------------------------------------------
    # NEW DAY
    # --------------------------------------------------------

    if storage.get("date") != today:

        # Preserve old history BEFORE clearing daily fields.
        _append_daily_history(storage)

        old_history = storage.get(
            "history",
            []
        )

        if not isinstance(old_history, list):
            old_history = []

        old_goal_streak = storage.get(
            "goal_streak",
            {}
        )

        # Keep only storage-level persistent metadata.
        storage.clear()

        storage["date"] = today
        storage["completed"] = []
        storage["custom"] = []
        storage["available"] = _default_available_ids()
        storage["completion_times"] = {}
        storage["history"] = old_history

        if isinstance(old_goal_streak, dict):
            storage["goal_streak"] = old_goal_streak

        storage["created_at"] = _now().isoformat()
        storage["updated_at"] = _now().isoformat()

    # --------------------------------------------------------
    # EXISTING DAY / BACKWARD COMPATIBILITY
    # --------------------------------------------------------

    else:

        storage.setdefault("completed", [])
        storage.setdefault("custom", [])
        storage.setdefault(
            "available",
            _default_available_ids()
        )
        storage.setdefault(
            "completion_times",
            {}
        )
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
    # TYPE SAFETY
    # --------------------------------------------------------

    if not isinstance(
        storage.get("completed"),
        list
    ):
        storage["completed"] = []

    if not isinstance(
        storage.get("custom"),
        list
    ):
        storage["custom"] = []

    if not isinstance(
        storage.get("available"),
        list
    ):
        storage["available"] = _default_available_ids()

    if not isinstance(
        storage.get("completion_times"),
        dict
    ):
        storage["completion_times"] = {}

    if not isinstance(
        storage.get("history"),
        list
    ):
        storage["history"] = []

    return storage


# ============================================================
# GET USER GOAL STORAGE
# ============================================================

def _get_goal_storage(user_id):

    data = v4_data.load_v4_data()

    user_id = str(user_id)

    goals_root = data.setdefault(
        "goals",
        {}
    )

    storage = goals_root.setdefault(
        user_id,
        {}
    )

    _initialize_goal_storage(storage)

    storage["updated_at"] = _now().isoformat()

    v4_data.save_v4_data(data)

    return storage


# ============================================================
# INTERNAL STORAGE LOADER
# ============================================================

def _load_goal_storage_from_data(
    data,
    user_id
):

    user_id = str(user_id)

    goals_root = data.setdefault(
        "goals",
        {}
    )

    storage = goals_root.setdefault(
        user_id,
        {}
    )

    return _initialize_goal_storage(
        storage
    )


# ============================================================
# GET DAILY GOALS
# ============================================================

def get_daily_goals(user_id):

    storage = _get_goal_storage(
        user_id
    )

    completed = storage.get(
        "completed",
        []
    )

    available_ids = storage.get(
        "available",
        []
    )

    custom_goals = storage.get(
        "custom",
        []
    )

    completion_times = storage.get(
        "completion_times",
        {}
    )

    goals = []

    # --------------------------------------------------------
    # DEFAULT GOALS
    # --------------------------------------------------------

    for goal in DEFAULT_GOALS:

        if goal["id"] not in available_ids:
            continue

        item = _copy_goal(goal)

        item["completed"] = (
            goal["id"] in completed
        )

        item["completed_at"] = (
            completion_times.get(
                goal["id"]
            )
        )

        item["custom"] = False

        goals.append(item)

    # --------------------------------------------------------
    # CUSTOM GOALS
    # --------------------------------------------------------

    if isinstance(custom_goals, list):

        for goal in custom_goals:

            if not isinstance(goal, dict):
                continue

            goal_id = _safe_string(
                goal.get("id")
            )

            if not goal_id:
                continue

            item = _copy_goal(goal)

            item["completed"] = (
                goal_id in completed
            )

            item["completed_at"] = (
                completion_times.get(
                    goal_id
                )
            )

            item["custom"] = True

            goals.append(item)

    return goals


# ============================================================
# GET GOAL
# ============================================================

def get_goal(user_id, goal_id):

    goal_id = _safe_string(goal_id)

    if not goal_id:
        return None

    for goal in get_daily_goals(user_id):

        if goal.get("id") == goal_id:
            return goal

    return None


# ============================================================
# CHECK COMPLETION
# ============================================================

def is_goal_completed(user_id, goal_id):

    goal_id = _safe_string(goal_id)

    if not goal_id:
        return False

    storage = _get_goal_storage(
        user_id
    )

    return (
        goal_id
        in storage.get(
            "completed",
            []
        )
    )


# ============================================================
# COMPLETE GOAL
# ============================================================

def complete_goal(user_id, goal_id):

    user_id = str(user_id)
    goal_id = _safe_string(goal_id)

    if not goal_id:

        return {
            "success": False,
            "already_completed": False,
            "invalid_goal": True,
            "xp": 0,
        }

    # --------------------------------------------------------
    # LOAD DATABASE ONCE
    # --------------------------------------------------------

    data = v4_data.load_v4_data()

    storage = _load_goal_storage_from_data(
        data,
        user_id
    )

    # --------------------------------------------------------
    # ALREADY COMPLETED
    # --------------------------------------------------------

    completed = storage.setdefault(
        "completed",
        []
    )

    if goal_id in completed:

        return {
            "success": False,
            "already_completed": True,
            "invalid_goal": False,
            "xp": 0,
            "goal_id": goal_id,
        }

    # --------------------------------------------------------
    # FIND GOAL
    # --------------------------------------------------------

    available = storage.get(
        "available",
        []
    )

    all_goals = []

    for goal in DEFAULT_GOALS:

        if goal["id"] in available:
            all_goals.append(goal)

    custom = storage.get(
        "custom",
        []
    )

    if isinstance(custom, list):
        all_goals.extend(custom)

    goal = next(
        (
            item
            for item in all_goals
            if (
                isinstance(item, dict)
                and item.get("id") == goal_id
            )
        ),
        None
    )

    if not goal:

        return {
            "success": False,
            "already_completed": False,
            "invalid_goal": True,
            "xp": 0,
            "goal_id": goal_id,
        }

    # --------------------------------------------------------
    # XP
    # --------------------------------------------------------

    xp = _safe_int(
        goal.get("xp", 10),
        10
    )

    xp = max(0, xp)

    # --------------------------------------------------------
    # MARK COMPLETE
    # --------------------------------------------------------

    completed.append(goal_id)

    completion_time = _now().isoformat()

    completion_times = storage.setdefault(
        "completion_times",
        {}
    )

    completion_times[goal_id] = (
        completion_time
    )

    storage["updated_at"] = (
        completion_time
    )

    # --------------------------------------------------------
    # USER STATISTICS
    # --------------------------------------------------------

    users = data.setdefault(
        "users",
        {}
    )

    user = users.setdefault(
        user_id,
        {}
    )

    user["total_goals_completed"] = (
        _safe_int(
            user.get(
                "total_goals_completed",
                0
            )
        )
        + 1
    )

    user["daily_goals_completed"] = (
        len(completed)
    )

    user["updated_at"] = (
        completion_time
    )

    # --------------------------------------------------------
    # GOAL STATISTICS
    # --------------------------------------------------------

    goal_stats = user.setdefault(
        "goal_stats",
        {}
    )

    if not isinstance(goal_stats, dict):
        goal_stats = {}
        user["goal_stats"] = goal_stats

    goal_stats["total_completed"] = (
        _safe_int(
            goal_stats.get(
                "total_completed",
                0
            )
        )
        + 1
    )

    goal_stats["today_completed"] = (
        len(completed)
    )

    goal_stats["last_completed"] = {
        "goal_id": goal_id,
        "title": goal.get(
            "title",
            ""
        ),
        "xp": xp,
        "timestamp": completion_time,
    }

    # --------------------------------------------------------
    # COMPLETION HISTORY
    # --------------------------------------------------------

    completion_history = (
        goal_stats.setdefault(
            "history",
            []
        )
    )

    if not isinstance(
        completion_history,
        list
    ):
        completion_history = []
        goal_stats["history"] = (
            completion_history
        )

    completion_history.append(
        {
            "goal_id": goal_id,
            "title": goal.get(
                "title",
                ""
            ),
            "xp": xp,
            "date": today_key(),
            "timestamp": completion_time,
        }
    )

    if len(completion_history) > MAX_HISTORY_ITEMS:
        del completion_history[
            :-MAX_HISTORY_ITEMS
        ]

    # --------------------------------------------------------
    # SAVE BEFORE XP
    # --------------------------------------------------------

    v4_data.save_v4_data(data)

    # --------------------------------------------------------
    # XP SYSTEM
    # --------------------------------------------------------

    try:

        xp_result = xp_system.add_xp(
            user_id,
            xp,
            source=f"goal:{goal_id}",
        )

    except TypeError:

        # Backward compatibility
        xp_result = xp_system.add_xp(
            user_id,
            xp
        )

    except Exception as exc:

        xp_result = {
            "level_up": False,
            "old_level": None,
            "new_level": None,
            "new_title": None,
            "error": str(exc),
        }

    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    progress = get_goal_progress(
        user_id
    )

    all_completed = bool(
        progress.get(
            "all_completed",
            False
        )
    )

    # --------------------------------------------------------
    # STREAK
    # --------------------------------------------------------

    streak_result = update_goal_streak(
        user_id
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {
        "success": True,
        "already_completed": False,
        "invalid_goal": False,

        "goal_id": goal_id,
        "goal": goal,

        "xp": xp,

        "total_completed": progress[
            "completed"
        ],

        "total_goals": progress[
            "total"
        ],

        "remaining": progress[
            "remaining"
        ],

        "percentage": progress[
            "percentage"
        ],

        "daily_complete": all_completed,

        "level_up": xp_result.get(
            "level_up",
            False
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

        "streak": streak_result.get(
            "streak",
            0
        ),

        "new_streak": streak_result.get(
            "new_streak",
            False
        ),

        "completed_at": completion_time,
    }


# ============================================================
# GOAL PROGRESS
# ============================================================

def get_goal_progress(user_id):

    goals = get_daily_goals(
        user_id
    )

    total = len(goals)

    completed = sum(
        1
        for goal in goals
        if goal.get(
            "completed",
            False
        )
    )

    percentage = (
        round(
            completed / total * 100
        )
        if total
        else 0
    )

    xp_total = sum(
        _safe_int(
            goal.get("xp", 0)
        )
        for goal in goals
    )

    xp_earned = sum(
        _safe_int(
            goal.get("xp", 0)
        )
        for goal in goals
        if goal.get(
            "completed",
            False
        )
    )

    return {
        "completed": completed,
        "total": total,
        "remaining": max(
            0,
            total - completed
        ),
        "percentage": percentage,
        "xp_total": xp_total,
        "xp_earned": xp_earned,
        "all_completed": (
            total > 0
            and completed == total
        ),
    }


# ============================================================
# PROGRESS BAR
# ============================================================

def progress_bar(
    user_id,
    width=10
):

    try:
        width = int(width)
    except Exception:
        width = 10

    width = max(
        1,
        min(width, 50)
    )

    progress = get_goal_progress(
        user_id
    )

    total = progress["total"]
    completed = progress["completed"]

    filled = (
        round(
            completed / total * width
        )
        if total
        else 0
    )

    filled = max(
        0,
        min(width, filled)
    )

    return (
        "█" * filled
        + "░" * (width - filled)
    )


# ============================================================
# ADD CUSTOM GOAL
# ============================================================

def add_custom_goal(
    user_id,
    title,
    description="",
    xp=20,
):

    user_id = str(user_id)

    title = _safe_string(title)
    description = _safe_string(description)

    if not title:
        return None

    title = title[:120]
    description = description[:500]

    try:
        xp = int(xp)
    except Exception:
        xp = 20

    xp = max(
        MIN_CUSTOM_XP,
        min(xp, MAX_CUSTOM_XP)
    )

    data = v4_data.load_v4_data()

    storage = _load_goal_storage_from_data(
        data,
        user_id
    )

    custom = storage.setdefault(
        "custom",
        []
    )

    if not isinstance(custom, list):
        custom = []
        storage["custom"] = custom

    existing_ids = {
        str(goal.get("id"))
        for goal in custom
        if isinstance(goal, dict)
    }

    counter = len(custom) + 1

    date_part = today_key().replace(
        "-",
        ""
    )

    goal_id = (
        f"custom_{counter}_{date_part}"
    )

    while goal_id in existing_ids:

        counter += 1

        goal_id = (
            f"custom_{counter}_{date_part}"
        )

    timestamp = _now().isoformat()

    goal = {
        "id": goal_id,
        "title": title,
        "description": description,
        "xp": xp,
        "icon": "🎯",
        "custom": True,
        "created_at": timestamp,
    }

    custom.append(goal)

    storage["updated_at"] = timestamp

    v4_data.save_v4_data(data)

    return goal


# ============================================================
# DELETE CUSTOM GOAL
# ============================================================

def delete_custom_goal(
    user_id,
    goal_id
):

    user_id = str(user_id)
    goal_id = _safe_string(goal_id)

    if not goal_id:
        return False

    data = v4_data.load_v4_data()

    storage = _load_goal_storage_from_data(
        data,
        user_id
    )

    custom = storage.get(
        "custom",
        []
    )

    if not isinstance(custom, list):
        return False

    completed = storage.get(
        "completed",
        []
    )

    for index, goal in enumerate(custom):

        if not isinstance(goal, dict):
            continue

        if goal.get("id") != goal_id:
            continue

        # Completed goals cannot be deleted.
        if goal_id in completed:
            return False

        custom.pop(index)

        storage["updated_at"] = (
            _now().isoformat()
        )

        v4_data.save_v4_data(data)

        return True

    return False


# ============================================================
# GOAL STREAK
# ============================================================

def update_goal_streak(user_id):

    user_id = str(user_id)

    # We intentionally use the current user's
    # goal storage for today's completion state.
    storage = _get_goal_storage(user_id)

    progress = get_goal_progress(
        user_id
    )

    if not progress.get(
        "all_completed",
        False
    ):

        data = v4_data.load_v4_data()

        user = data.setdefault(
            "users",
            {}
        ).setdefault(
            user_id,
            {}
        )

        goal_streak = user.get(
            "goal_streak",
            {}
        )

        if not isinstance(goal_streak, dict):
            goal_streak = {}

        return {
            "streak": _safe_int(
                goal_streak.get(
                    "current",
                    0
                )
            ),
            "longest": _safe_int(
                goal_streak.get(
                    "longest",
                    0
                )
            ),
            "new_streak": False,
            "all_completed": False,
        }

    data = v4_data.load_v4_data()

    user = data.setdefault(
        "users",
        {}
    ).setdefault(
        user_id,
        {}
    )

    goal_streak = user.setdefault(
        "goal_streak",
        {}
    )

    if not isinstance(
        goal_streak,
        dict
    ):
        goal_streak = {}
        user["goal_streak"] = goal_streak

    today = today_key()

    last_completed = goal_streak.get(
        "last_completed_date"
    )

    current = _safe_int(
        goal_streak.get(
            "current",
            0
        )
    )

    longest = _safe_int(
        goal_streak.get(
            "longest",
            0
        )
    )

    # Already processed today.
    if last_completed == today:

        return {
            "streak": current,
            "longest": longest,
            "new_streak": False,
            "all_completed": True,
        }

    yesterday = (
        _now() - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    if last_completed == yesterday:
        current += 1
    else:
        current = 1

    longest = max(
        longest,
        current
    )

    now_iso = _now().isoformat()

    goal_streak["current"] = current
    goal_streak["longest"] = longest
    goal_streak["last_completed_date"] = today
    goal_streak["updated_at"] = now_iso

    user["updated_at"] = now_iso

    # Also keep a compact copy inside goal storage.
    storage["goal_streak"] = {
        "current": current,
        "longest": longest,
        "last_completed_date": today,
    }

    v4_data.save_v4_data(data)

    return {
        "streak": current,
        "longest": longest,
        "new_streak": True,
        "all_completed": True,
    }


# ============================================================
# GET GOAL STREAK
# ============================================================

def get_goal_streak(user_id):

    user = v4_data.get_user(
        user_id
    )

    streak = user.get(
        "goal_streak",
        {}
    )

    if not isinstance(streak, dict):
        streak = {}

    return {
        "current": _safe_int(
            streak.get(
                "current",
                0
            )
        ),
        "longest": _safe_int(
            streak.get(
                "longest",
                0
            )
        ),
        "last_completed_date": (
            streak.get(
                "last_completed_date"
            )
        ),
    }


# ============================================================
# GOAL HISTORY
# ============================================================

def get_goal_history(
    user_id,
    limit=30
):

    try:
        limit = int(limit)
    except Exception:
        limit = 30

    limit = max(
        1,
        min(
            limit,
            MAX_HISTORY_ITEMS
        )
    )

    storage = _get_goal_storage(
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
# GOAL STATISTICS
# ============================================================

def get_goal_stats(user_id):

    user = v4_data.get_user(
        user_id
    )

    stats = user.get(
        "goal_stats",
        {}
    )

    if not isinstance(stats, dict):
        stats = {}

    progress = get_goal_progress(
        user_id
    )

    streak = get_goal_streak(
        user_id
    )

    return {
        "total_completed": _safe_int(
            stats.get(
                "total_completed",
                user.get(
                    "total_goals_completed",
                    0
                )
            )
        ),

        "today_completed": progress[
            "completed"
        ],

        "today_total": progress[
            "total"
        ],

        "today_remaining": progress[
            "remaining"
        ],

        "today_percentage": progress[
            "percentage"
        ],

        "xp_earned_today": progress[
            "xp_earned"
        ],

        "xp_available_today": progress[
            "xp_total"
        ],

        "current_streak": streak[
            "current"
        ],

        "longest_streak": streak[
            "longest"
        ],

        "last_completed_date": streak[
            "last_completed_date"
        ],
    }


# ============================================================
# RESET DAILY GOALS
# ============================================================

def reset_daily_goals(user_id):

    data = v4_data.load_v4_data()

    user_id = str(user_id)

    goals_root = data.setdefault(
        "goals",
        {}
    )

    goals_root.pop(
        user_id,
        None
    )

    v4_data.save_v4_data(data)

    # Recreate today's storage.
    _get_goal_storage(user_id)

    return True


# ============================================================
# RESET ALL GOAL DATA
# ============================================================

def reset_all_goal_data(user_id):

    data = v4_data.load_v4_data()

    user_id = str(user_id)

    # Remove daily goal storage.
    data.setdefault(
        "goals",
        {}
    ).pop(
        user_id,
        None
    )

    # Remove goal statistics.
    user = data.setdefault(
        "users",
        {}
    ).get(
        user_id
    )

    if isinstance(user, dict):

        user.pop(
            "goal_stats",
            None
        )

        user.pop(
            "goal_streak",
            None
        )

        user.pop(
            "total_goals_completed",
            None
        )

        user.pop(
            "daily_goals_completed",
            None
        )

        user["updated_at"] = (
            _now().isoformat()
        )

    v4_data.save_v4_data(data)

    return True


# ============================================================
# FORMAT GOAL SUMMARY
# ============================================================

def format_goal_summary(user_id):

    progress = get_goal_progress(
        user_id
    )

    streak = get_goal_streak(
        user_id
    )

    bar = progress_bar(
        user_id,
        width=10
    )

    if progress["all_completed"]:

        status = (
            "🎉 All today's goals completed!"
        )

    elif progress["completed"] > 0:

        status = (
            "🌸 Keep going — you're doing great!"
        )

    else:

        status = (
            "🌱 Start with one small goal."
        )

    return (
        "🎯 *Daily Goals*\n\n"
        f"{bar} "
        f"{progress['percentage']}%\n\n"
        f"✅ Completed: "
        f"{progress['completed']}/"
        f"{progress['total']}\n"
        f"⏳ Remaining: "
        f"{progress['remaining']}\n"
        f"⭐ XP earned: "
        f"{progress['xp_earned']}/"
        f"{progress['xp_total']}\n"
        f"🔥 Goal streak: "
        f"{streak['current']} day(s)\n\n"
        f"{status}"
    )


# ============================================================
# FORMAT INDIVIDUAL GOAL
# ============================================================

def format_goal(goal):

    if not isinstance(goal, dict):
        return ""

    icon = goal.get(
        "icon",
        "🎯"
    )

    title = goal.get(
        "title",
        "Goal"
    )

    description = goal.get(
        "description",
        ""
    )

    xp = _safe_int(
        goal.get(
            "xp",
            0
        )
    )

    completed = bool(
        goal.get(
            "completed",
            False
        )
    )

    status = (
        "✅ Completed"
        if completed
        else "⬜ Pending"
    )

    custom_tag = (
        " • Custom"
        if goal.get("custom")
        else ""
    )

    return (
        f"{icon} *{title}*\n"
        f"{description}\n"
        f"⭐ +{xp} XP{custom_tag}\n"
        f"{status}"
    )


# ============================================================
# GET COMPLETED GOALS
# ============================================================

def get_completed_goals(user_id):

    return [
        goal
        for goal in get_daily_goals(user_id)
        if goal.get(
            "completed",
            False
        )
    ]


# ============================================================
# GET PENDING GOALS
# ============================================================

def get_pending_goals(user_id):

    return [
        goal
        for goal in get_daily_goals(user_id)
        if not goal.get(
            "completed",
            False
        )
    ]


# ============================================================
# GET TODAY'S GOAL XP
# ============================================================

def get_today_goal_xp(user_id):

    return get_goal_progress(
        user_id
    )["xp_earned"]


# ============================================================
# CHECK DAILY GOAL COMPLETION
# ============================================================

def all_daily_goals_completed(user_id):

    return get_goal_progress(
        user_id
    ).get(
        "all_completed",
        False
    )


# ============================================================
# GOAL COMPLETION COUNT
# ============================================================

def get_today_completed_count(user_id):

    return get_goal_progress(
        user_id
    )["completed"]


# ============================================================
# GOAL REMAINING COUNT
# ============================================================

def get_today_remaining_count(user_id):

    return get_goal_progress(
        user_id
    )["remaining"]


# ============================================================
# GOAL XP TOTAL
# ============================================================

def get_today_goal_xp_total(user_id):

    return get_goal_progress(
        user_id
    )["xp_total"]


# ============================================================
# GOAL COMPLETION PERCENTAGE
# ============================================================

def get_today_goal_percentage(user_id):

    return get_goal_progress(
        user_id
    )["percentage"]


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    "DEFAULT_GOALS",

    "MIN_CUSTOM_XP",
    "MAX_CUSTOM_XP",
    "MAX_HISTORY_ITEMS",

    "today_key",

    "get_default_goals",
    "get_daily_goals",
    "get_goal",

    "is_goal_completed",
    "complete_goal",

    "get_goal_progress",
    "progress_bar",

    "add_custom_goal",
    "delete_custom_goal",

    "update_goal_streak",
    "get_goal_streak",

    "get_goal_history",
    "get_goal_stats",

    "reset_daily_goals",
    "reset_all_goal_data",

    "format_goal_summary",
    "format_goal",

    "get_completed_goals",
    "get_pending_goals",

    "get_today_goal_xp",
    "get_today_completed_count",
    "get_today_remaining_count",
    "get_today_goal_xp_total",
    "get_today_goal_percentage",

    "all_daily_goals_completed",
]

