# ============================================================
# MOODBLOOM 4.0 — SMART NOTIFICATIONS SYSTEM
# ============================================================
#
# Features:
#   • Notification preferences
#   • Morning wishes/reminder
#   • Mood check reminder
#   • Daily goals reminder
#   • Daily reward reminder
#   • Birthday reminders
#   • Study reminder support
#   • Custom reminders
#   • Enable / disable notifications
#   • Quiet hours
#   • Duplicate protection
#   • Notification history
#   • Notification statistics
#   • Last sent tracking
#   • Scheduler-friendly APIs
#   • Backward-compatible storage
#
# ============================================================

from datetime import datetime, timedelta
from copy import deepcopy

import config
import v4_data


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_NOTIFICATION_TYPES = [
    "morning",
    "mood_check",
    "daily_goals",
    "daily_reward",
    "birthday",
    "study",
    "custom",
]

DEFAULT_SETTINGS = {
    "enabled": True,

    "morning": True,
    "mood_check": True,
    "daily_goals": True,
    "daily_reward": True,
    "birthday": True,
    "study": True,
    "custom": True,

    "quiet_hours": {
        "enabled": False,
        "start": "23:00",
        "end": "07:00",
    },

    "morning_time": "08:00",
    "mood_check_time": "12:00",
    "daily_goals_time": "18:00",
    "daily_reward_time": "09:00",
    "birthday_time": "08:30",

    "timezone": None,
}

MAX_HISTORY_ITEMS = 365
MAX_CUSTOM_REMINDERS = 50


# ============================================================
# TIME HELPERS
# ============================================================

def _now():
    """Return current timezone-aware datetime."""

    try:
        return datetime.now(
            config.TIMEZONE
        )
    except Exception:
        return datetime.now()


def today_key():
    """Return today's date."""

    return _now().strftime(
        "%Y-%m-%d"
    )


def current_time_key():
    """Return current time as HH:MM."""

    return _now().strftime(
        "%H:%M"
    )


def current_hour():
    """Return current hour."""

    return _now().hour


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


def _safe_bool(value, default=False):
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, str):
        value = value.strip().lower()

        if value in (
            "true",
            "1",
            "yes",
            "on",
            "enable",
            "enabled",
        ):
            return True

        if value in (
            "false",
            "0",
            "no",
            "off",
            "disable",
            "disabled",
        ):
            return False

    return bool(value)


def _deepcopy(value):
    try:
        return deepcopy(value)
    except Exception:
        return value


# ============================================================
# DEFAULT SETTINGS
# ============================================================

def get_default_settings():
    """Return a fresh copy of default notification settings."""

    return _deepcopy(
        DEFAULT_SETTINGS
    )


# ============================================================
# TIME VALIDATION
# ============================================================

def _parse_time(value):
    """
    Validate HH:MM time.

    Returns:
        normalized HH:MM string or None
    """

    value = _safe_string(value)

    if not value:
        return None

    try:
        parsed = datetime.strptime(
            value,
            "%H:%M"
        )

        return parsed.strftime(
            "%H:%M"
        )

    except Exception:
        return None


def _time_to_minutes(value):
    """Convert HH:MM to minutes from midnight."""

    parsed = _parse_time(value)

    if parsed is None:
        return None

    hour, minute = (
        parsed.split(":")
    )

    return (
        int(hour) * 60
        + int(minute)
    )


# ============================================================
# QUIET HOURS
# ============================================================

def is_quiet_hours(
    settings=None
):
    """
    Check whether the current time falls inside
    configured quiet hours.
    """

    if settings is None:
        settings = get_notification_settings(
            None
        )

    if not isinstance(settings, dict):
        settings = get_default_settings()

    quiet = settings.get(
        "quiet_hours",
        {}
    )

    if not isinstance(quiet, dict):
        return False

    if not _safe_bool(
        quiet.get("enabled"),
        False
    ):
        return False

    start = _time_to_minutes(
        quiet.get(
            "start",
            "23:00"
        )
    )

    end = _time_to_minutes(
        quiet.get(
            "end",
            "07:00"
        )
    )

    if start is None or end is None:
        return False

    now_minutes = (
        _now().hour * 60
        + _now().minute
    )

    # Same start/end means the whole day is quiet.
    if start == end:
        return True

    # Normal range, e.g. 09:00 -> 17:00
    if start < end:

        return (
            start
            <= now_minutes
            < end
        )

    # Overnight range, e.g. 23:00 -> 07:00
    return (
        now_minutes >= start
        or now_minutes < end
    )


# ============================================================
# STORAGE HELPERS
# ============================================================

def _initialize_notification_storage(
    storage
):
    """
    Initialize notification storage while preserving
    existing history and custom reminders.
    """

    if not isinstance(storage, dict):
        storage = {}

    storage.setdefault(
        "settings",
        get_default_settings()
    )

    if not isinstance(
        storage.get("settings"),
        dict
    ):
        storage["settings"] = (
            get_default_settings()
        )

    # --------------------------------------------------------
    # Merge missing default settings
    # --------------------------------------------------------

    defaults = get_default_settings()

    settings = storage["settings"]

    for key, value in defaults.items():

        if key not in settings:
            settings[key] = _deepcopy(value)

    quiet = settings.get(
        "quiet_hours"
    )

    if not isinstance(quiet, dict):
        quiet = {}

    for key, value in defaults[
        "quiet_hours"
    ].items():

        quiet.setdefault(
            key,
            value
        )

    settings["quiet_hours"] = quiet

    # --------------------------------------------------------
    # History
    # --------------------------------------------------------

    history = storage.setdefault(
        "history",
        []
    )

    if not isinstance(history, list):
        history = []
        storage["history"] = history

    if len(history) > MAX_HISTORY_ITEMS:
        del history[:-MAX_HISTORY_ITEMS]

    # --------------------------------------------------------
    # Sent tracking
    # --------------------------------------------------------

    sent = storage.setdefault(
        "sent",
        {}
    )

    if not isinstance(sent, dict):
        storage["sent"] = {}

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    stats = storage.setdefault(
        "stats",
        {}
    )

    if not isinstance(stats, dict):
        stats = {}
        storage["stats"] = stats

    stats.setdefault(
        "total_sent",
        0
    )

    stats.setdefault(
        "total_skipped",
        0
    )

    stats.setdefault(
        "total_failed",
        0
    )

    stats.setdefault(
        "by_type",
        {}
    )

    if not isinstance(
        stats["by_type"],
        dict
    ):
        stats["by_type"] = {}

    # --------------------------------------------------------
    # Custom reminders
    # --------------------------------------------------------

    custom = storage.setdefault(
        "custom_reminders",
        []
    )

    if not isinstance(custom, list):
        custom = []
        storage["custom_reminders"] = custom

    if len(custom) > MAX_CUSTOM_REMINDERS:
        del custom[
            :-MAX_CUSTOM_REMINDERS
        ]

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    storage.setdefault(
        "created_at",
        _now().isoformat()
    )

    storage.setdefault(
        "updated_at",
        _now().isoformat()
    )

    return storage


# ============================================================
# GET STORAGE
# ============================================================

def _get_storage(user_id):
    """
    Get notification storage for one user.
    """

    data = v4_data.load_v4_data()

    user_id = str(user_id)

    notifications = data.setdefault(
        "notifications",
        {}
    )

    storage = notifications.setdefault(
        user_id,
        {}
    )

    _initialize_notification_storage(
        storage
    )

    storage["updated_at"] = (
        _now().isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return storage


# ============================================================
# INTERNAL STORAGE LOADER
# ============================================================

def _load_storage_from_data(
    data,
    user_id
):
    """
    Load notification storage when database is
    already loaded.
    """

    user_id = str(user_id)

    notifications = data.setdefault(
        "notifications",
        {}
    )

    storage = notifications.setdefault(
        user_id,
        {}
    )

    return _initialize_notification_storage(
        storage
    )


# ============================================================
# SETTINGS
# ============================================================

def get_notification_settings(
    user_id
):
    """
    Return notification settings.

    If user_id is None, return defaults.
    """

    if user_id is None:
        return get_default_settings()

    storage = _get_storage(
        user_id
    )

    return _deepcopy(
        storage.get(
            "settings",
            get_default_settings()
        )
    )


# ============================================================
# UPDATE SETTINGS
# ============================================================

def update_notification_settings(
    user_id,
    **kwargs
):
    """
    Update one or more notification settings.

    Example:
        update_notification_settings(
            user_id,
            enabled=False,
            mood_check=True
        )
    """

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    settings = storage.setdefault(
        "settings",
        get_default_settings()
    )

    changed = {}

    # --------------------------------------------------------
    # Boolean notification settings
    # --------------------------------------------------------

    boolean_keys = {
        "enabled",
        "morning",
        "mood_check",
        "daily_goals",
        "daily_reward",
        "birthday",
        "study",
        "custom",
    }

    for key in boolean_keys:

        if key not in kwargs:
            continue

        settings[key] = _safe_bool(
            kwargs[key]
        )

        changed[key] = settings[key]

    # --------------------------------------------------------
    # Time settings
    # --------------------------------------------------------

    time_keys = {
        "morning_time",
        "mood_check_time",
        "daily_goals_time",
        "daily_reward_time",
        "birthday_time",
    }

    for key in time_keys:

        if key not in kwargs:
            continue

        parsed = _parse_time(
            kwargs[key]
        )

        if parsed is None:
            continue

        settings[key] = parsed
        changed[key] = parsed

    # --------------------------------------------------------
    # Quiet hours
    # --------------------------------------------------------

    if "quiet_hours_enabled" in kwargs:

        quiet = settings.setdefault(
            "quiet_hours",
            {}
        )

        quiet["enabled"] = _safe_bool(
            kwargs[
                "quiet_hours_enabled"
            ]
        )

        changed[
            "quiet_hours_enabled"
        ] = quiet["enabled"]

    if "quiet_start" in kwargs:

        parsed = _parse_time(
            kwargs["quiet_start"]
        )

        if parsed is not None:

            settings.setdefault(
                "quiet_hours",
                {}
            )["start"] = parsed

            changed[
                "quiet_start"
            ] = parsed

    if "quiet_end" in kwargs:

        parsed = _parse_time(
            kwargs["quiet_end"]
        )

        if parsed is not None:

            settings.setdefault(
                "quiet_hours",
                {}
            )["end"] = parsed

            changed[
                "quiet_end"
            ] = parsed

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    storage["updated_at"] = (
        _now().isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return {
        "success": True,
        "changed": changed,
        "settings": _deepcopy(
            settings
        ),
    }


# ============================================================
# ENABLE / DISABLE
# ============================================================

def set_notifications_enabled(
    user_id,
    enabled=True
):
    """Enable or disable all notifications."""

    return update_notification_settings(
        user_id,
        enabled=enabled
    )


def notifications_enabled(
    user_id
):
    """Return whether notifications are enabled."""

    settings = get_notification_settings(
        user_id
    )

    return _safe_bool(
        settings.get(
            "enabled",
            True
        ),
        True
    )


# ============================================================
# TYPE ENABLE CHECK
# ============================================================

def notification_type_enabled(
    user_id,
    notification_type
):
    """
    Check whether a specific notification type
    is enabled.
    """

    notification_type = _safe_string(
        notification_type
    ).lower()

    if notification_type not in (
        DEFAULT_NOTIFICATION_TYPES
    ):
        return False

    settings = get_notification_settings(
        user_id
    )

    if not _safe_bool(
        settings.get(
            "enabled",
            True
        ),
        True
    ):
        return False

    return _safe_bool(
        settings.get(
            notification_type,
            True
        ),
        True
    )


# ============================================================
# CAN SEND
# ============================================================

def can_send_notification(
    user_id,
    notification_type,
    ignore_quiet_hours=False
):
    """
    Check whether a notification can be sent.
    """

    notification_type = _safe_string(
        notification_type
    ).lower()

    if not notification_type_enabled(
        user_id,
        notification_type
    ):
        return {
            "allowed": False,
            "reason": "disabled",
        }

    if (
        not ignore_quiet_hours
        and is_quiet_hours(
            get_notification_settings(
                user_id
            )
        )
    ):
        return {
            "allowed": False,
            "reason": "quiet_hours",
        }

    return {
        "allowed": True,
        "reason": None,
    }


# ============================================================
# DUPLICATE PROTECTION
# ============================================================

def _notification_key(
    notification_type,
    date=None
):
    if date is None:
        date = today_key()

    return (
        f"{notification_type}:"
        f"{date}"
    )


def was_sent_today(
    user_id,
    notification_type
):
    """
    Check whether this notification type
    was already sent today.
    """

    notification_type = _safe_string(
        notification_type
    ).lower()

    storage = _get_storage(
        user_id
    )

    sent = storage.get(
        "sent",
        {}
    )

    key = _notification_key(
        notification_type
    )

    return key in sent


# ============================================================
# RECORD SENT
# ============================================================

def record_notification_sent(
    user_id,
    notification_type,
    message_id=None,
    metadata=None
):
    """
    Record a successfully sent notification.
    """

    user_id = str(user_id)

    notification_type = _safe_string(
        notification_type
    ).lower()

    if not notification_type:
        return False

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    now = _now()

    key = _notification_key(
        notification_type,
        now.strftime("%Y-%m-%d")
    )

    sent = storage.setdefault(
        "sent",
        {}
    )

    sent[key] = {
        "type": notification_type,
        "date": now.strftime(
            "%Y-%m-%d"
        ),
        "time": now.strftime(
            "%H:%M"
        ),
        "timestamp": now.isoformat(),
        "message_id": message_id,
        "metadata": (
            metadata
            if isinstance(metadata, dict)
            else {}
        ),
    }

    # --------------------------------------------------------
    # History
    # --------------------------------------------------------

    history = storage.setdefault(
        "history",
        []
    )

    history.append(
        {
            "type": notification_type,
            "date": now.strftime(
                "%Y-%m-%d"
            ),
            "time": now.strftime(
                "%H:%M"
            ),
            "timestamp": now.isoformat(),
            "message_id": message_id,
            "metadata": (
                metadata
                if isinstance(metadata, dict)
                else {}
            ),
            "status": "sent",
        }
    )

    if len(history) > MAX_HISTORY_ITEMS:
        del history[:-MAX_HISTORY_ITEMS]

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    stats = storage.setdefault(
        "stats",
        {}
    )

    stats["total_sent"] = (
        _safe_int(
            stats.get(
                "total_sent",
                0
            )
        )
        + 1
    )

    by_type = stats.setdefault(
        "by_type",
        {}
    )

    by_type[notification_type] = (
        _safe_int(
            by_type.get(
                notification_type,
                0
            )
        )
        + 1
    )

    storage["last_sent"] = {
        "type": notification_type,
        "timestamp": now.isoformat(),
    }

    storage["updated_at"] = (
        now.isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return True


# ============================================================
# RECORD SKIPPED
# ============================================================

def record_notification_skipped(
    user_id,
    notification_type,
    reason="unknown"
):
    """Record a skipped notification."""

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    stats = storage.setdefault(
        "stats",
        {}
    )

    stats["total_skipped"] = (
        _safe_int(
            stats.get(
                "total_skipped",
                0
            )
        )
        + 1
    )

    history = storage.setdefault(
        "history",
        []
    )

    now = _now()

    history.append(
        {
            "type": _safe_string(
                notification_type
            ),
            "timestamp": now.isoformat(),
            "status": "skipped",
            "reason": _safe_string(
                reason
            ),
        }
    )

    if len(history) > MAX_HISTORY_ITEMS:
        del history[:-MAX_HISTORY_ITEMS]

    storage["updated_at"] = (
        now.isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return True


# ============================================================
# RECORD FAILED
# ============================================================

def record_notification_failed(
    user_id,
    notification_type,
    error=""
):
    """Record a failed notification."""

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    stats = storage.setdefault(
        "stats",
        {}
    )

    stats["total_failed"] = (
        _safe_int(
            stats.get(
                "total_failed",
                0
            )
        )
        + 1
    )

    history = storage.setdefault(
        "history",
        []
    )

    now = _now()

    history.append(
        {
            "type": _safe_string(
                notification_type
            ),
            "timestamp": now.isoformat(),
            "status": "failed",
            "error": _safe_string(
                error
            )[:500],
        }
    )

    if len(history) > MAX_HISTORY_ITEMS:
        del history[:-MAX_HISTORY_ITEMS]

    storage["updated_at"] = (
        now.isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return True


# ============================================================
# NOTIFICATION STATUS
# ============================================================

def get_notification_status(
    user_id,
    notification_type
):
    """
    Return complete status for a notification type.
    """

    notification_type = _safe_string(
        notification_type
    ).lower()

    settings = get_notification_settings(
        user_id
    )

    enabled = notification_type_enabled(
        user_id,
        notification_type
    )

    quiet = is_quiet_hours(
        settings
    )

    sent_today = was_sent_today(
        user_id,
        notification_type
    )

    return {
        "type": notification_type,
        "enabled": enabled,
        "quiet_hours": quiet,
        "sent_today": sent_today,
        "can_send": (
            enabled
            and not quiet
            and not sent_today
        ),
    }


# ============================================================
# DAILY NOTIFICATION CHECK
# ============================================================

def should_send_daily_notification(
    user_id,
    notification_type,
    scheduled_time=None
):
    """
    Scheduler-friendly check.

    Returns True when:
      • notification is enabled
      • quiet hours are not active
      • it hasn't already been sent today
      • scheduled time has arrived
    """

    notification_type = _safe_string(
        notification_type
    ).lower()

    if not notification_type_enabled(
        user_id,
        notification_type
    ):
        return False

    settings = get_notification_settings(
        user_id
    )

    if is_quiet_hours(settings):
        return False

    if was_sent_today(
        user_id,
        notification_type
    ):
        return False

    if scheduled_time is None:
        return True

    scheduled_time = _parse_time(
        scheduled_time
    )

    if scheduled_time is None:
        return False

    current = _time_to_minutes(
        current_time_key()
    )

    scheduled = _time_to_minutes(
        scheduled_time
    )

    if current is None or scheduled is None:
        return False

    return current >= scheduled


# ============================================================
# MORNING NOTIFICATION
# ============================================================

def should_send_morning(
    user_id
):
    settings = get_notification_settings(
        user_id
    )

    return should_send_daily_notification(
        user_id,
        "morning",
        settings.get(
            "morning_time",
            "08:00"
        )
    )


# ============================================================
# MOOD CHECK NOTIFICATION
# ============================================================

def should_send_mood_check(
    user_id
):
    settings = get_notification_settings(
        user_id
    )

    return should_send_daily_notification(
        user_id,
        "mood_check",
        settings.get(
            "mood_check_time",
            "12:00"
        )
    )


# ============================================================
# DAILY GOALS NOTIFICATION
# ============================================================

def should_send_daily_goals(
    user_id
):
    settings = get_notification_settings(
        user_id
    )

    return should_send_daily_notification(
        user_id,
        "daily_goals",
        settings.get(
            "daily_goals_time",
            "18:00"
        )
    )


# ============================================================
# DAILY REWARD NOTIFICATION
# ============================================================

def should_send_daily_reward(
    user_id
):
    settings = get_notification_settings(
        user_id
    )

    return should_send_daily_notification(
        user_id,
        "daily_reward",
        settings.get(
            "daily_reward_time",
            "09:00"
        )
    )


# ============================================================
# BIRTHDAY NOTIFICATION
# ============================================================

def should_send_birthday(
    user_id
):
    settings = get_notification_settings(
        user_id
    )

    return should_send_daily_notification(
        user_id,
        "birthday",
        settings.get(
            "birthday_time",
            "08:30"
        )
    )


# ============================================================
# STUDY NOTIFICATION
# ============================================================

def should_send_study(
    user_id,
    scheduled_time=None
):
    """
    Study reminder support.

    A scheduler can provide a specific time.
    """

    return should_send_daily_notification(
        user_id,
        "study",
        scheduled_time
    )


# ============================================================
# CUSTOM REMINDERS
# ============================================================

def add_custom_reminder(
    user_id,
    title,
    reminder_time,
    message="",
    repeat_daily=True,
    enabled=True,
):
    """
    Add a custom daily reminder.
    """

    title = _safe_string(title)
    reminder_time = _parse_time(
        reminder_time
    )
    message = _safe_string(message)

    if not title:
        return None

    if reminder_time is None:
        return None

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    reminders = storage.setdefault(
        "custom_reminders",
        []
    )

    if len(reminders) >= MAX_CUSTOM_REMINDERS:
        return None

    existing_ids = {
        str(item.get("id"))
        for item in reminders
        if isinstance(item, dict)
    }

    counter = len(reminders) + 1

    reminder_id = (
        f"reminder_{counter}"
    )

    while reminder_id in existing_ids:

        counter += 1

        reminder_id = (
            f"reminder_{counter}"
        )

    now = _now()

    reminder = {
        "id": reminder_id,
        "title": title[:120],
        "time": reminder_time,
        "message": message[:500],
        "repeat_daily": _safe_bool(
            repeat_daily,
            True
        ),
        "enabled": _safe_bool(
            enabled,
            True
        ),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    reminders.append(reminder)

    storage["updated_at"] = (
        now.isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return _deepcopy(
        reminder
    )


# ============================================================
# GET CUSTOM REMINDERS
# ============================================================

def get_custom_reminders(
    user_id,
    include_disabled=True
):
    storage = _get_storage(
        user_id
    )

    reminders = storage.get(
        "custom_reminders",
        []
    )

    if not isinstance(reminders, list):
        return []

    result = []

    for reminder in reminders:

        if not isinstance(
            reminder,
            dict
        ):
            continue

        if (
            not include_disabled
            and not _safe_bool(
                reminder.get(
                    "enabled",
                    True
                ),
                True
            )
        ):
            continue

        result.append(
            _deepcopy(
                reminder
            )
        )

    return result


# ============================================================
# GET CUSTOM REMINDER
# ============================================================

def get_custom_reminder(
    user_id,
    reminder_id
):
    reminder_id = _safe_string(
        reminder_id
    )

    if not reminder_id:
        return None

    reminders = get_custom_reminders(
        user_id
    )

    for reminder in reminders:

        if str(
            reminder.get("id")
        ) == reminder_id:

            return reminder

    return None


# ============================================================
# UPDATE CUSTOM REMINDER
# ============================================================

def update_custom_reminder(
    user_id,
    reminder_id,
    **kwargs
):
    """
    Update an existing custom reminder.
    """

    reminder_id = _safe_string(
        reminder_id
    )

    if not reminder_id:
        return {
            "success": False,
            "reason": "invalid_id",
        }

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    reminders = storage.get(
        "custom_reminders",
        []
    )

    if not isinstance(reminders, list):
        return {
            "success": False,
            "reason": "no_reminders",
        }

    for reminder in reminders:

        if not isinstance(
            reminder,
            dict
        ):
            continue

        if str(
            reminder.get("id")
        ) != reminder_id:
            continue

        if "title" in kwargs:

            title = _safe_string(
                kwargs["title"]
            )

            if title:
                reminder["title"] = title[:120]

        if "message" in kwargs:

            reminder["message"] = (
                _safe_string(
                    kwargs["message"]
                )[:500]
            )

        if "time" in kwargs:

            parsed = _parse_time(
                kwargs["time"]
            )

            if parsed is not None:
                reminder["time"] = parsed

        if "enabled" in kwargs:

            reminder["enabled"] = _safe_bool(
                kwargs["enabled"]
            )

        if "repeat_daily" in kwargs:

            reminder["repeat_daily"] = (
                _safe_bool(
                    kwargs["repeat_daily"]
                )
            )

        reminder["updated_at"] = (
            _now().isoformat()
        )

        storage["updated_at"] = (
            _now().isoformat()
        )

        v4_data.save_v4_data(
            data
        )

        return {
            "success": True,
            "reminder": _deepcopy(
                reminder
            ),
        }

    return {
        "success": False,
        "reason": "not_found",
    }


# ============================================================
# DELETE CUSTOM REMINDER
# ============================================================

def delete_custom_reminder(
    user_id,
    reminder_id
):
    reminder_id = _safe_string(
        reminder_id
    )

    if not reminder_id:
        return False

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    reminders = storage.get(
        "custom_reminders",
        []
    )

    if not isinstance(reminders, list):
        return False

    for index, reminder in enumerate(
        reminders
    ):

        if not isinstance(
            reminder,
            dict
        ):
            continue

        if str(
            reminder.get("id")
        ) != reminder_id:
            continue

        reminders.pop(index)

        storage["updated_at"] = (
            _now().isoformat()
        )

        v4_data.save_v4_data(
            data
        )

        return True

    return False


# ============================================================
# CUSTOM REMINDER CHECK
# ============================================================

def get_due_custom_reminders(
    user_id
):
    """
    Return enabled custom reminders whose time
    has arrived and haven't been sent today.
    """

    if not notification_type_enabled(
        user_id,
        "custom"
    ):
        return []

    settings = get_notification_settings(
        user_id
    )

    if is_quiet_hours(settings):
        return []

    reminders = get_custom_reminders(
        user_id,
        include_disabled=False
    )

    current_minutes = _time_to_minutes(
        current_time_key()
    )

    if current_minutes is None:
        return []

    due = []

    for reminder in reminders:

        reminder_time = _time_to_minutes(
            reminder.get("time")
        )

        if reminder_time is None:
            continue

        if current_minutes < reminder_time:
            continue

        reminder_id = reminder.get(
            "id"
        )

        key = _notification_key(
            f"custom:{reminder_id}"
        )

        storage = _get_storage(
            user_id
        )

        sent = storage.get(
            "sent",
            {}
        )

        if key in sent:
            continue

        due.append(reminder)

    return due


# ============================================================
# RECORD CUSTOM REMINDER SENT
# ============================================================

def record_custom_reminder_sent(
    user_id,
    reminder_id,
    message_id=None
):
    return record_notification_sent(
        user_id,
        f"custom:{_safe_string(reminder_id)}",
        message_id=message_id,
        metadata={
            "reminder_id": _safe_string(
                reminder_id
            )
        },
    )


# ============================================================
# HISTORY
# ============================================================

def get_notification_history(
    user_id,
    limit=30,
    notification_type=None
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

    notification_type = (
        _safe_string(
            notification_type
        ).lower()
        if notification_type
        else None
    )

    storage = _get_storage(
        user_id
    )

    history = storage.get(
        "history",
        []
    )

    if not isinstance(history, list):
        return []

    filtered = []

    for item in reversed(history):

        if not isinstance(item, dict):
            continue

        if (
            notification_type
            and item.get("type")
            != notification_type
        ):
            continue

        filtered.append(
            _deepcopy(item)
        )

        if len(filtered) >= limit:
            break

    return filtered


# ============================================================
# STATISTICS
# ============================================================

def get_notification_stats(
    user_id
):
    storage = _get_storage(
        user_id
    )

    stats = storage.get(
        "stats",
        {}
    )

    if not isinstance(stats, dict):
        stats = {}

    by_type = stats.get(
        "by_type",
        {}
    )

    if not isinstance(by_type, dict):
        by_type = {}

    return {
        "total_sent": _safe_int(
            stats.get(
                "total_sent",
                0
            )
        ),

        "total_skipped": _safe_int(
            stats.get(
                "total_skipped",
                0
            )
        ),

        "total_failed": _safe_int(
            stats.get(
                "total_failed",
                0
            )
        ),

        "by_type": dict(
            by_type
        ),

        "last_sent": _deepcopy(
            storage.get(
                "last_sent"
            )
        ),
    }


# ============================================================
# TODAY'S SENT COUNT
# ============================================================

def get_today_sent_count(
    user_id
):
    history = get_notification_history(
        user_id,
        limit=MAX_HISTORY_ITEMS
    )

    today = today_key()

    return sum(
        1
        for item in history
        if (
            isinstance(item, dict)
            and item.get("status") == "sent"
            and str(
                item.get("date", "")
            ) == today
        )
    )


# ============================================================
# CLEAN OLD SENT DATA
# ============================================================

def cleanup_old_notification_data(
    user_id,
    days=30
):
    """
    Remove old sent markers.

    History is retained separately.
    """

    try:
        days = int(days)
    except Exception:
        days = 30

    days = max(
        1,
        min(days, 3650)
    )

    cutoff = (
        _now()
        - timedelta(days=days)
    )

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    sent = storage.get(
        "sent",
        {}
    )

    if not isinstance(sent, dict):
        return 0

    removed = 0

    for key, value in list(
        sent.items()
    ):

        if not isinstance(value, dict):
            continue

        timestamp = value.get(
            "timestamp"
        )

        if not timestamp:
            continue

        try:
            parsed = datetime.fromisoformat(
                timestamp
            )
        except Exception:
            continue

        if parsed < cutoff:
            del sent[key]
            removed += 1

    storage["updated_at"] = (
        _now().isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return removed


# ============================================================
# RESET TODAY'S SENT STATE
# ============================================================

def reset_today_notifications(
    user_id
):
    """
    Remove today's sent markers.

    Useful for testing.
    """

    data = v4_data.load_v4_data()

    storage = _load_storage_from_data(
        data,
        user_id
    )

    sent = storage.get(
        "sent",
        {}
    )

    if not isinstance(sent, dict):
        return False

    today = today_key()

    removed = False

    for key, value in list(
        sent.items()
    ):

        if not isinstance(value, dict):
            continue

        if value.get("date") == today:

            del sent[key]
            removed = True

    storage["updated_at"] = (
        _now().isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return removed


# ============================================================
# RESET ALL NOTIFICATION DATA
# ============================================================

def reset_all_notification_data(
    user_id
):
    """
    Completely reset notification data.

    Does not modify XP, goals, moods, rewards,
    birthdays, or other systems.
    """

    data = v4_data.load_v4_data()

    user_id = str(user_id)

    notifications = data.setdefault(
        "notifications",
        {}
    )

    notifications.pop(
        user_id,
        None
    )

    v4_data.save_v4_data(
        data
    )

    return True


# ============================================================
# FORMAT SETTINGS
# ============================================================

def format_notification_settings(
    user_id
):
    settings = get_notification_settings(
        user_id
    )

    enabled = (
        "ON 🟢"
        if settings.get(
            "enabled",
            True
        )
        else "OFF 🔴"
    )

    quiet = settings.get(
        "quiet_hours",
        {}
    )

    if not isinstance(quiet, dict):
        quiet = {}

    quiet_status = (
        "ON 🔕"
        if quiet.get(
            "enabled",
            False
        )
        else "OFF 🔔"
    )

    return (
        "🔔 *Notification Settings*\n\n"
        f"Global: {enabled}\n\n"

        f"🌅 Morning: "
        f"{'ON' if settings.get('morning') else 'OFF'} "
        f"({settings.get('morning_time', '08:00')})\n"

        f"💭 Mood Check: "
        f"{'ON' if settings.get('mood_check') else 'OFF'} "
        f"({settings.get('mood_check_time', '12:00')})\n"

        f"🎯 Daily Goals: "
        f"{'ON' if settings.get('daily_goals') else 'OFF'} "
        f"({settings.get('daily_goals_time', '18:00')})\n"

        f"🎁 Daily Reward: "
        f"{'ON' if settings.get('daily_reward') else 'OFF'} "
        f"({settings.get('daily_reward_time', '09:00')})\n"

        f"🎂 Birthday: "
        f"{'ON' if settings.get('birthday') else 'OFF'} "
        f"({settings.get('birthday_time', '08:30')})\n"

        f"📚 Study: "
        f"{'ON' if settings.get('study') else 'OFF'}\n"

        f"📝 Custom: "
        f"{'ON' if settings.get('custom') else 'OFF'}\n\n"

        f"🔕 Quiet Hours: {quiet_status}\n"
        f"   {quiet.get('start', '23:00')} "
        f"→ {quiet.get('end', '07:00')}"
    )


# ============================================================
# FORMAT STATS
# ============================================================

def format_notification_stats(
    user_id
):
    stats = get_notification_stats(
        user_id
    )

    by_type = stats.get(
        "by_type",
        {}
    )

    lines = [
        "🔔 *Notification Statistics*",
        "",
        f"📨 Total Sent: "
        f"{stats['total_sent']}",
        f"⏭️ Skipped: "
        f"{stats['total_skipped']}",
        f"❌ Failed: "
        f"{stats['total_failed']}",
        "",
        "📊 *By Type:*",
    ]

    if by_type:

        names = {
            "morning": "🌅 Morning",
            "mood_check": "💭 Mood Check",
            "daily_goals": "🎯 Daily Goals",
            "daily_reward": "🎁 Daily Reward",
            "birthday": "🎂 Birthday",
            "study": "📚 Study",
            "custom": "📝 Custom",
        }

        for key, count in sorted(
            by_type.items(),
            key=lambda item: item[1],
            reverse=True
        ):

            lines.append(
                f"{names.get(key, key)}: "
                f"{_safe_int(count)}"
            )

    else:

        lines.append(
            "No notifications sent yet."
        )

    return "\n".join(lines)


# ============================================================
# CLEAN USER NOTIFICATION STATE
# ============================================================

def ensure_user_notifications(
    user_id
):
    """
    Public initialization helper.
    """

    _get_storage(
        user_id
    )

    return True


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    # Constants
    "DEFAULT_NOTIFICATION_TYPES",
    "DEFAULT_SETTINGS",
    "MAX_HISTORY_ITEMS",
    "MAX_CUSTOM_REMINDERS",

    # Time
    "today_key",
    "current_time_key",
    "current_hour",

    # Settings
    "get_default_settings",
    "get_notification_settings",
    "update_notification_settings",
    "set_notifications_enabled",
    "notifications_enabled",

    # Quiet hours
    "is_quiet_hours",

    # Permission checks
    "notification_type_enabled",
    "can_send_notification",

    # Sent tracking
    "was_sent_today",
    "record_notification_sent",
    "record_notification_skipped",
    "record_notification_failed",

    # Status
    "get_notification_status",

    # Daily scheduler checks
    "should_send_daily_notification",
    "should_send_morning",
    "should_send_mood_check",
    "should_send_daily_goals",
    "should_send_daily_reward",
    "should_send_birthday",
    "should_send_study",

    # Custom reminders
    "add_custom_reminder",
    "get_custom_reminders",
    "get_custom_reminder",
    "update_custom_reminder",
    "delete_custom_reminder",
    "get_due_custom_reminders",
    "record_custom_reminder_sent",

    # History / stats
    "get_notification_history",
    "get_notification_stats",
    "get_today_sent_count",

    # Maintenance
    "cleanup_old_notification_data",
    "reset_today_notifications",
    "reset_all_notification_data",

    # Formatting
    "format_notification_settings",
    "format_notification_stats",

    # Initialization
    "ensure_user_notifications",
]

