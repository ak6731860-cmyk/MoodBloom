# ============================================================
# MOODBLOOM 4.1 — SMART STUDY ENGINE
# ============================================================
#
# Major Study Upgrade:
#   • Selected duration is tracked automatically.
#   • Bot can ask for confirmation when the timer ends.
#   • "Haan" -> study XP reward.
#   • "Nahi" -> XP penalty.
#   • Active sessions are persisted in v4_data.json.
#   • Session state survives a bot restart; bot.py can restore
#     remaining timers on startup.
#   • Existing study statistics and daily goal integration kept.
#
# ============================================================

from datetime import datetime

import config
import v4_data
import goals


DEFAULT_STUDY_MINUTES = 25
MIN_CUSTOM_MINUTES = 1
MAX_CUSTOM_MINUTES = 180
DEFAULT_DAILY_TARGET_MINUTES = 100

# Smart Study verification XP.
# These are deliberately kept separate from the existing daily
# "study" goal XP so the verification itself has a clear reward.
STUDY_SUCCESS_XP = 10
STUDY_FAILURE_XP = 10


def now():
    try:
        return datetime.now(config.TIMEZONE).isoformat()
    except Exception:
        return datetime.now().isoformat()


def now_datetime():
    try:
        return datetime.now(config.TIMEZONE)
    except Exception:
        return datetime.now()


def today_key():
    try:
        return datetime.now(config.TIMEZONE).strftime("%Y-%m-%d")
    except Exception:
        return datetime.now().strftime("%Y-%m-%d")


def _default_record():
    return {
        "active": False,
        "awaiting_confirmation": False,
        "timer_notified": False,

        "started_at": None,
        "duration_minutes": 0,
        "chat_id": None,

        "completed_sessions": 0,
        "failed_sessions": 0,

        "total_minutes": 0,
        "verified_minutes": 0,

        "last_completed": None,
        "last_failed": None,
        "last_result": None,

        "daily_date": today_key(),
        "daily_minutes": 0,
        "daily_target_minutes": DEFAULT_DAILY_TARGET_MINUTES,
    }


def _get_or_create(data, user_id):
    user_id = str(user_id)

    study_root = data.setdefault("study", {})
    record = study_root.setdefault(
        user_id,
        _default_record(),
    )

    defaults = _default_record()

    for key, value in defaults.items():
        record.setdefault(key, value)

    if record.get("daily_date") != today_key():
        record["daily_date"] = today_key()
        record["daily_minutes"] = 0

    return record


def get_study_data(user_id):
    data = v4_data.load_v4_data()

    study = _get_or_create(
        data,
        user_id,
    )

    v4_data.save_v4_data(data)

    return study


def start_session(
    user_id,
    minutes=DEFAULT_STUDY_MINUTES,
    chat_id=None,
):
    data = v4_data.load_v4_data()

    study = _get_or_create(
        data,
        user_id,
    )

    if study.get("active"):
        return {
            "success": False,
            "already_active": True,
            "minutes": int(
                study.get(
                    "duration_minutes",
                    minutes,
                )
            ),
            "started_at": study.get("started_at"),
        }

    try:
        minutes = int(minutes)
    except Exception:
        minutes = DEFAULT_STUDY_MINUTES

    minutes = max(
        MIN_CUSTOM_MINUTES,
        min(
            minutes,
            MAX_CUSTOM_MINUTES,
        ),
    )

    study["active"] = True
    study["awaiting_confirmation"] = False
    study["timer_notified"] = False

    study["started_at"] = now()
    study["duration_minutes"] = minutes
    study["chat_id"] = (
        int(chat_id)
        if chat_id is not None
        else int(user_id)
    )

    study["last_result"] = None

    v4_data.save_v4_data(data)

    return {
        "success": True,
        "already_active": False,
        "minutes": minutes,
        "started_at": study["started_at"],
        "chat_id": study["chat_id"],
    }


def get_remaining_seconds(user_id):
    """
    Calculate the real remaining time from started_at + duration.

    This does not rely on a counter, so the result stays accurate
    even if the process was busy for a while.
    """
    study = get_study_data(user_id)

    if not study.get("active"):
        return 0

    started_at = study.get("started_at")
    duration_minutes = int(
        study.get(
            "duration_minutes",
            0,
        )
    )

    if not started_at or duration_minutes <= 0:
        return 0

    try:
        started = datetime.fromisoformat(
            started_at
        )

        if started.tzinfo is None:
            current = now_datetime().replace(
                tzinfo=None
            )
        else:
            current = now_datetime()

        elapsed = (
            current - started
        ).total_seconds()

        remaining = (
            duration_minutes * 60
            - elapsed
        )

        return max(
            0,
            int(round(remaining)),
        )

    except Exception:
        return duration_minutes * 60


def mark_timer_finished(user_id):
    """
    Mark the timer as finished and put the session into the
    confirmation state.

    The study is NOT recorded as successful yet.
    """
    data = v4_data.load_v4_data()

    study = _get_or_create(
        data,
        user_id,
    )

    if not study.get("active"):
        return {
            "success": False,
            "not_active": True,
        }

    study["awaiting_confirmation"] = True
    study["timer_notified"] = True

    v4_data.save_v4_data(data)

    return {
        "success": True,
        "minutes": int(
            study.get(
                "duration_minutes",
                DEFAULT_STUDY_MINUTES,
            )
        ),
        "chat_id": study.get("chat_id"),
    }


def cancel_session(user_id):
    data = v4_data.load_v4_data()

    study = data.setdefault(
        "study",
        {},
    ).get(
        str(user_id)
    )

    if not study:
        return False

    study["active"] = False
    study["awaiting_confirmation"] = False
    study["timer_notified"] = False

    study["started_at"] = None
    study["duration_minutes"] = 0
    study["chat_id"] = None

    study["last_result"] = "cancelled"

    v4_data.save_v4_data(data)

    return True


def _reset_session(study):
    study["active"] = False
    study["awaiting_confirmation"] = False
    study["timer_notified"] = False

    study["started_at"] = None
    study["duration_minutes"] = 0
    study["chat_id"] = None


def complete_session(user_id):
    """
    Backward-compatible successful completion.

    New code should prefer confirm_session(user_id, True).
    """
    return confirm_session(
        user_id,
        completed=True,
    )


def fail_session(user_id):
    """
    Mark the timed session as not completed.

    The selected duration is NOT added to study statistics.
    """
    data = v4_data.load_v4_data()

    study = _get_or_create(
        data,
        user_id,
    )

    if not study.get("active"):
        return {
            "success": False,
            "not_active": True,
        }

    minutes = int(
        study.get(
            "duration_minutes",
            DEFAULT_STUDY_MINUTES,
        )
    )

    _reset_session(study)

    study["failed_sessions"] = (
        int(
            study.get(
                "failed_sessions",
                0,
            )
        )
        + 1
    )

    study["last_failed"] = now()
    study["last_result"] = "no"

    v4_data.save_v4_data(data)

    return {
        "success": True,
        "minutes": minutes,
        "failed_sessions": int(
            study.get(
                "failed_sessions",
                0,
            )
        ),
        "result": "no",
    }


def confirm_session(
    user_id,
    completed=True,
):
    """
    Finalize a timed study session after the user answers
    the bot's confirmation question.

    completed=True:
        Records the selected study duration and completes the
        existing daily Study goal.

    completed=False:
        Ends the session without adding study minutes.
        bot.py can apply the XP penalty separately.
    """
    if not completed:
        return fail_session(user_id)

    data = v4_data.load_v4_data()

    study = _get_or_create(
        data,
        user_id,
    )

    if not study.get("active"):
        return {
            "success": False,
            "not_active": True,
        }

    minutes = int(
        study.get(
            "duration_minutes",
            DEFAULT_STUDY_MINUTES,
        )
    )

    _reset_session(study)

    study["completed_sessions"] = (
        int(
            study.get(
                "completed_sessions",
                0,
            )
        )
        + 1
    )

    study["total_minutes"] = (
        int(
            study.get(
                "total_minutes",
                0,
            )
        )
        + minutes
    )

    study["verified_minutes"] = (
        int(
            study.get(
                "verified_minutes",
                0,
            )
        )
        + minutes
    )

    study["daily_minutes"] = (
        int(
            study.get(
                "daily_minutes",
                0,
            )
        )
        + minutes
    )

    study["last_completed"] = now()
    study["last_result"] = "yes"

    user_id_str = str(user_id)

    users = data.setdefault(
        "users",
        {},
    )

    user = users.setdefault(
        user_id_str,
        {},
    )

    stats = user.setdefault(
        "stats",
        {},
    )

    stats["study_minutes"] = (
        int(
            stats.get(
                "study_minutes",
                0,
            )
        )
        + minutes
    )

    v4_data.save_v4_data(data)

    # Existing daily Study goal is preserved.
    goal_result = goals.complete_goal(
        user_id_str,
        "study",
    )

    return {
        "success": True,
        "minutes": minutes,

        "sessions": int(
            study.get(
                "completed_sessions",
                0,
            )
        ),

        "total_minutes": int(
            study.get(
                "total_minutes",
                0,
            )
        ),

        "verified_minutes": int(
            study.get(
                "verified_minutes",
                0,
            )
        ),

        "daily_minutes": int(
            study.get(
                "daily_minutes",
                0,
            )
        ),

        "daily_target_minutes": int(
            study.get(
                "daily_target_minutes",
                DEFAULT_DAILY_TARGET_MINUTES,
            )
        ),

        "goal": goal_result,
        "result": "yes",
    }


def get_active_sessions():
    """
    Return persisted active sessions.

    Used by bot.py during startup so a running study session is
    not silently forgotten after a process restart.
    """
    data = v4_data.load_v4_data()

    study_root = data.setdefault(
        "study",
        {},
    )

    active = []

    for user_id, record in study_root.items():

        if not isinstance(record, dict):
            continue

        if not record.get("active"):
            continue

        if not record.get("started_at"):
            continue

        active.append(
            {
                "user_id": int(user_id),
                "chat_id": record.get("chat_id") or int(user_id),
                "started_at": record.get("started_at"),
                "duration_minutes": int(
                    record.get(
                        "duration_minutes",
                        DEFAULT_STUDY_MINUTES,
                    )
                ),
                "awaiting_confirmation": bool(
                    record.get(
                        "awaiting_confirmation",
                        False,
                    )
                ),
                "timer_notified": bool(
                    record.get(
                        "timer_notified",
                        False,
                    )
                ),
            }
        )

    return active


def get_progress(user_id):
    study = get_study_data(user_id)

    target = max(
        1,
        int(
            study.get(
                "daily_target_minutes",
                DEFAULT_DAILY_TARGET_MINUTES,
            )
        ),
    )

    minutes = max(
        0,
        int(
            study.get(
                "daily_minutes",
                0,
            )
        ),
    )

    percent = min(
        100,
        round(
            minutes / target * 100
        ),
    )

    return {
        "minutes": minutes,
        "target": target,
        "percent": percent,
    }


def get_summary(user_id):
    study = get_study_data(user_id)

    progress = get_progress(
        user_id
    )

    return {
        "active": bool(
            study.get(
                "active",
                False,
            )
        ),

        "awaiting_confirmation": bool(
            study.get(
                "awaiting_confirmation",
                False,
            )
        ),

        "completed_sessions": int(
            study.get(
                "completed_sessions",
                0,
            )
        ),

        "failed_sessions": int(
            study.get(
                "failed_sessions",
                0,
            )
        ),

        "total_minutes": int(
            study.get(
                "total_minutes",
                0,
            )
        ),

        "verified_minutes": int(
            study.get(
                "verified_minutes",
                0,
            )
        ),

        "daily_minutes": progress["minutes"],
        "daily_target_minutes": progress["target"],
        "daily_percent": progress["percent"],

        "current_duration": int(
            study.get(
                "duration_minutes",
                0,
            )
        ),

        "started_at": study.get(
            "started_at"
        ),

        "last_result": study.get(
            "last_result"
        ),
    }
