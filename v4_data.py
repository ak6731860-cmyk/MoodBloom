import json
import os
import shutil
import tempfile
from datetime import datetime
from copy import deepcopy

import config


# ============================================================
# MOODBLOOM 4.0 — V4 DATA LAYER
# ============================================================
#
# Central persistent data layer for MoodBloom 4.0.
#
# Responsibilities:
#   • Safe JSON database handling
#   • Backward-compatible schema migration
#   • User data
#   • Group data
#   • Group member analytics
#   • Quiz data
#   • Goals data
#   • Rewards data
#   • Birthday data
#   • Notification data
#   • Analytics data
#   • Backup / recovery helpers
#
# Study Mode is intentionally NOT implemented here.
# The "study" section is retained only for compatibility with
# older MoodBloom data.
# ============================================================


# ============================================================
# DATABASE PATH
# ============================================================

V4_DATA_FILE = os.path.join(
    os.path.dirname(config.DATA_FILE),
    "moodbloom_v4.json"
)

V4_BACKUP_DIR = os.path.join(
    os.path.dirname(V4_DATA_FILE),
    "v4_backups"
)

V4_VERSION = "4.0"


# ============================================================
# DEFAULT DATABASE STRUCTURE
# ============================================================

DEFAULT_DATA = {
    "users": {},
    "groups": {},
    "quiz": {},
    "goals": {},
    "rewards": {},
    "birthdays": {},
    "study": {},
    "notifications": {},
    "analytics": {},

    "system": {
        "version": V4_VERSION,
        "created_at": None,
        "updated_at": None,
        "last_backup_at": None,
        "database_recoveries": 0,
    },
}


# ============================================================
# DEFAULT USER STRUCTURE
# ============================================================

DEFAULT_USER = {
    "created_at": None,
    "updated_at": None,

    # Identity
    "user_id": None,
    "first_name": "",
    "last_name": "",
    "username": "",

    # XP / Level
    "xp": 0,
    "level": 1,
    "total_xp_earned": 0,
    "xp_today": 0,
    "xp_this_week": 0,
    "xp_this_month": 0,

    # Goals
    "daily_goals_completed": 0,
    "total_goals_completed": 0,
    "goals_created": 0,
    "goals_failed": 0,

    # Quiz
    "quiz_played": 0,
    "quiz_correct": 0,
    "quiz_wrong": 0,
    "quiz_xp": 0,
    "quiz_streak": 0,
    "best_quiz_streak": 0,

    # Rewards
    "reward_claims": 0,
    "reward_xp": 0,
    "rewards_unlocked": 0,

    # Streaks
    "current_streak": 0,
    "best_streak": 0,
    "last_active_date": None,

    # Mood
    "mood_checkins": 0,
    "last_mood": None,
    "mood_history": [],

    # Badges / achievements
    "badges": [],
    "achievements": [],

    # Journey
    "journey_day": 1,
    "journey_xp": 0,
    "journey_completed": 0,

    # Settings
    "settings": {
        "morning_wishes": True,
        "smart_notifications": True,

        # Kept for compatibility only.
        # Study Mode itself is not implemented.
        "study_notifications": False,

        "birthday_notifications": True,
        "goal_notifications": True,
        "reward_notifications": True,
        "quiz_notifications": True,
        "analytics_notifications": True,
    },

    # General statistics
    "stats": {
        "messages_sent": 0,
        "group_messages": 0,
        "private_messages": 0,
        "mood_checkins": 0,
        "goals_completed": 0,
        "quizzes_played": 0,
        "quiz_correct": 0,
        "rewards_claimed": 0,
        "birthdays_added": 0,
    },

    # Activity
    "activity": {
        "active_days": [],
        "daily_activity": {},
        "weekly_activity": {},
        "monthly_activity": {},
    },

    # User metadata
    "metadata": {},
}


# ============================================================
# DEFAULT GROUP STRUCTURE
# ============================================================

DEFAULT_GROUP = {
    "created_at": None,
    "updated_at": None,

    "group_id": None,
    "title": "",
    "username": "",
    "total_messages": 0,

    # Message analytics
    "daily": {},
    "weekly": {},
    "monthly": {},

    # Message timing
    "hourly": {},
    "weekday": {},

    # Members
    "members": {},

    # Group quiz
    "quiz": {
        "played": 0,
        "participants": 0,
        "questions_answered": 0,
        "correct_answers": 0,
        "wrong_answers": 0,
        "total_xp": 0,
        "leaderboard": {},
    },

    # Group mood intelligence
    "mood": {
        "checkins": 0,
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "history": {},
    },

    # Group activity intelligence
    "analytics": {
        "active_days": [],
        "peak_hour": None,
        "peak_weekday": None,
        "average_daily_messages": 0,
        "last_analysis": None,
    },

    # Group settings
    "settings": {
        "analytics_enabled": True,
        "quiz_enabled": True,
        "birthday_enabled": True,
        "leaderboard_enabled": True,
        "smart_notifications": True,
        "mood_insights_enabled": True,
    },

    # Group metadata
    "metadata": {},
}


# ============================================================
# DEFAULT GROUP MEMBER STRUCTURE
# ============================================================

DEFAULT_GROUP_MEMBER = {
    "user_id": None,

    "first_name": "",
    "last_name": "",
    "username": "",

    "messages": 0,

    "daily_messages": {},
    "weekly_messages": {},
    "monthly_messages": {},

    "hourly_messages": {},
    "weekday_messages": {},

    "quiz_answered": 0,
    "quiz_correct": 0,
    "quiz_wrong": 0,

    "mood_checkins": 0,

    "points": 0,
    "xp": 0,

    "active_days": [],

    "last_seen": None,
    "first_seen": None,

    "metadata": {},
}


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _now():
    """
    Return timezone-aware current timestamp when possible.
    """

    try:
        return datetime.now(config.TIMEZONE).isoformat()

    except Exception:
        return datetime.now().isoformat()


def _today():
    """
    Return current date as YYYY-MM-DD.
    """

    return _now()[:10]


def _deep_copy_default():
    """
    Return a completely independent copy of DEFAULT_DATA.
    """

    return deepcopy(DEFAULT_DATA)


def _copy_user_default():
    return deepcopy(DEFAULT_USER)


def _copy_group_default():
    return deepcopy(DEFAULT_GROUP)


def _copy_member_default():
    return deepcopy(DEFAULT_GROUP_MEMBER)


def _merge_dict(target, defaults):
    """
    Recursively merge missing default values into target.

    Existing user data is preserved.
    """

    if not isinstance(target, dict):
        target = {}

    for key, default_value in defaults.items():

        if key not in target:
            target[key] = deepcopy(default_value)

        elif isinstance(default_value, dict):

            if not isinstance(target[key], dict):
                target[key] = deepcopy(default_value)

            else:
                target[key] = _merge_dict(
                    target[key],
                    default_value
                )

    return target


def _merge_defaults(data):
    """
    Apply the current V4 schema to existing database data.

    This is intentionally backward compatible so older
    MoodBloom V4 databases can continue working.
    """

    if not isinstance(data, dict):
        data = {}

    data = _merge_dict(
        data,
        DEFAULT_DATA
    )

    # --------------------------------------------------------
    # System metadata
    # --------------------------------------------------------

    if not data["system"].get("created_at"):
        data["system"]["created_at"] = _now()

    data["system"]["version"] = V4_VERSION
    data["system"]["updated_at"] = _now()

    # --------------------------------------------------------
    # Existing users
    # --------------------------------------------------------

    if isinstance(data.get("users"), dict):

        for user_id, user in data["users"].items():

            if not isinstance(user, dict):
                user = {}

            user = _merge_dict(
                user,
                DEFAULT_USER
            )

            user["user_id"] = str(
                user.get("user_id") or user_id
            )

            data["users"][user_id] = user

    # --------------------------------------------------------
    # Existing groups
    # --------------------------------------------------------

    if isinstance(data.get("groups"), dict):

        for group_id, group in data["groups"].items():

            if not isinstance(group, dict):
                group = {}

            group = _merge_dict(
                group,
                DEFAULT_GROUP
            )

            group["group_id"] = str(
                group.get("group_id") or group_id
            )

            # Existing members
            if isinstance(group.get("members"), dict):

                for user_id, member in group["members"].items():

                    if not isinstance(member, dict):
                        member = {}

                    member = _merge_dict(
                        member,
                        DEFAULT_GROUP_MEMBER
                    )

                    member["user_id"] = str(
                        member.get("user_id") or user_id
                    )

                    group["members"][user_id] = member

            data["groups"][group_id] = group

    return data


def _ensure_folder(path):
    """
    Create parent directory if required.
    """

    folder = os.path.dirname(path)

    if folder:
        os.makedirs(
            folder,
            exist_ok=True
        )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def ensure_v4_database():
    """
    Make sure the V4 database exists.
    """

    _ensure_folder(V4_DATA_FILE)

    if not os.path.exists(V4_DATA_FILE):

        data = _deep_copy_default()

        data["system"]["created_at"] = _now()
        data["system"]["updated_at"] = _now()

        save_v4_data(data)

        print(
            "✅ MoodBloom 4.0 database created."
        )

        return True

    return True


# ============================================================
# LOAD DATABASE
# ============================================================

def load_v4_data():
    """
    Load the complete V4 database.

    If the database is corrupted, the broken file is preserved
    and a fresh database is created.
    """

    ensure_v4_database()

    try:

        with open(
            V4_DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return _merge_defaults(data)

    except (
        json.JSONDecodeError,
        OSError,
        TypeError,
        ValueError
    ) as error:

        print(
            "⚠️ V4 database read error:",
            error
        )

        broken_file = (
            V4_DATA_FILE + ".broken"
        )

        try:

            if os.path.exists(
                V4_DATA_FILE
            ):

                # Avoid overwriting an existing broken copy.
                if os.path.exists(
                    broken_file
                ):

                    timestamp = (
                        datetime.now()
                        .strftime("%Y%m%d_%H%M%S")
                    )

                    broken_file = (
                        V4_DATA_FILE
                        + f".broken_{timestamp}"
                    )

                os.replace(
                    V4_DATA_FILE,
                    broken_file
                )

        except Exception as backup_error:

            print(
                "⚠️ Could not preserve broken database:",
                backup_error
            )

        data = _deep_copy_default()

        data["system"]["created_at"] = _now()
        data["system"]["updated_at"] = _now()
        data["system"]["database_recoveries"] = 1

        save_v4_data(data)

        print(
            "♻️ MoodBloom V4 database recovered."
        )

        return data


# ============================================================
# SAVE DATABASE
# ============================================================

def save_v4_data(data):
    """
    Atomically save the complete V4 database.

    A temporary file is written first and then replaced over
    the original database. This helps prevent partial writes.
    """

    _ensure_folder(V4_DATA_FILE)

    data = _merge_defaults(data)

    temp_file = None

    try:

        folder = os.path.dirname(
            V4_DATA_FILE
        )

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=folder or None,
            prefix="moodbloom_v4_",
            suffix=".tmp"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

            file.flush()

            try:
                os.fsync(
                    file.fileno()
                )
            except Exception:
                pass

            temp_file = file.name

        os.replace(
            temp_file,
            V4_DATA_FILE
        )

        return True

    except Exception as error:

        print(
            "⚠️ V4 database save error:",
            error
        )

        if temp_file:

            try:
                os.remove(
                    temp_file
                )
            except Exception:
                pass

        return False


# ============================================================
# GENERIC SECTION ACCESS
# ============================================================

def get_section(section_name):
    """
    Get any top-level V4 data section.

    Example:
        get_section("goals")
        get_section("rewards")
    """

    data = load_v4_data()

    section = data.get(
        section_name
    )

    if not isinstance(
        section,
        dict
    ):

        section = {}

        data[section_name] = section
        save_v4_data(data)

    return section


def set_section(section_name, value):
    """
    Replace a complete top-level V4 section.
    """

    data = load_v4_data()

    if not isinstance(
        value,
        dict
    ):
        value = {}

    data[section_name] = value

    save_v4_data(data)

    return value


# ============================================================
# USER DATA
# ============================================================

def get_user(user_id):
    """
    Get or create a MoodBloom user.
    """

    data = load_v4_data()

    user_id = str(user_id)

    if user_id not in data["users"]:

        user = _copy_user_default()

        user["user_id"] = user_id
        user["created_at"] = _now()
        user["updated_at"] = _now()

        data["users"][user_id] = user

        save_v4_data(data)

    else:

        user = data["users"][user_id]

        if not isinstance(
            user,
            dict
        ):
            user = _copy_user_default()

        user = _merge_dict(
            user,
            DEFAULT_USER
        )

        user["user_id"] = user_id

        data["users"][user_id] = user

        save_v4_data(data)

    return data["users"][user_id]


def update_user(user_id, updates):
    """
    Update selected user fields.

    Nested dictionaries supplied in updates are merged rather
    than blindly destroying existing nested values.
    """

    data = load_v4_data()

    user_id = str(user_id)

    user = data["users"].get(
        user_id
    )

    if not isinstance(
        user,
        dict
    ):
        user = _copy_user_default()

    user = _merge_dict(
        user,
        DEFAULT_USER
    )

    if isinstance(
        updates,
        dict
    ):

        for key, value in updates.items():

            if (
                isinstance(value, dict)
                and isinstance(
                    user.get(key),
                    dict
                )
            ):

                user[key] = _merge_dict(
                    user[key],
                    value
                )

            else:
                user[key] = value

    user["user_id"] = user_id
    user["updated_at"] = _now()

    data["users"][user_id] = user

    save_v4_data(data)

    return user


def update_user_stats(
    user_id,
    stat_name,
    amount=1
):
    """
    Increment a user statistic safely.
    """

    data = load_v4_data()

    user_id = str(user_id)

    user = data["users"].get(
        user_id
    )

    if not isinstance(
        user,
        dict
    ):
        user = _copy_user_default()

    user = _merge_dict(
        user,
        DEFAULT_USER
    )

    stats = user.setdefault(
        "stats",
        {}
    )

    current = stats.get(
        stat_name,
        0
    )

    if not isinstance(
        current,
        (int, float)
    ):
        current = 0

    stats[stat_name] = (
        current + amount
    )

    user["updated_at"] = _now()

    data["users"][user_id] = user

    save_v4_data(data)

    return stats[stat_name]


def add_user_xp(
    user_id,
    amount
):
    """
    Add XP to a user.

    Level calculation is intentionally kept simple here.
    xp_system.py remains the authority for advanced XP rules.
    """

    try:
        amount = int(amount)
    except Exception:
        amount = 0

    if amount < 0:
        amount = 0

    data = load_v4_data()

    user_id = str(user_id)

    user = data["users"].get(
        user_id
    )

    if not isinstance(
        user,
        dict
    ):
        user = _copy_user_default()

    user = _merge_dict(
        user,
        DEFAULT_USER
    )

    user["xp"] = max(
        0,
        int(user.get("xp", 0)) + amount
    )

    user["total_xp_earned"] = max(
        0,
        int(
            user.get(
                "total_xp_earned",
                0
            )
        ) + amount
    )

    user["xp_today"] = max(
        0,
        int(
            user.get(
                "xp_today",
                0
            )
        ) + amount
    )

    user["journey_xp"] = max(
        0,
        int(
            user.get(
                "journey_xp",
                0
            )
        ) + amount
    )

    user["updated_at"] = _now()

    data["users"][user_id] = user

    save_v4_data(data)

    return user


def add_badge(
    user_id,
    badge
):
    """
    Add a badge without creating duplicates.
    """

    data = load_v4_data()

    user_id = str(user_id)

    user = data["users"].get(
        user_id
    )

    if not isinstance(
        user,
        dict
    ):
        user = _copy_user_default()

    user = _merge_dict(
        user,
        DEFAULT_USER
    )

    badges = user.setdefault(
        "badges",
        []
    )

    if badge not in badges:
        badges.append(badge)

    user["updated_at"] = _now()

    data["users"][user_id] = user

    save_v4_data(data)

    return badges


def add_achievement(
    user_id,
    achievement
):
    """
    Add an achievement without duplicates.
    """

    data = load_v4_data()

    user_id = str(user_id)

    user = data["users"].get(
        user_id
    )

    if not isinstance(
        user,
        dict
    ):
        user = _copy_user_default()

    user = _merge_dict(
        user,
        DEFAULT_USER
    )

    achievements = user.setdefault(
        "achievements",
        []
    )

    if achievement not in achievements:
        achievements.append(
            achievement
        )

    user["updated_at"] = _now()

    data["users"][user_id] = user

    save_v4_data(data)

    return achievements


# ============================================================
# MOOD DATA
# ============================================================

def record_user_mood(
    user_id,
    mood
):
    """
    Store a user's mood check-in.

    Mood value is stored exactly as supplied while maintaining
    a timestamped history.
    """

    data = load_v4_data()

    user_id = str(user_id)

    user = data["users"].get(
        user_id
    )

    if not isinstance(
        user,
        dict
    ):
        user = _copy_user_default()

    user = _merge_dict(
        user,
        DEFAULT_USER
    )

    timestamp = _now()
    date_key = timestamp[:10]

    user["last_mood"] = mood
    user["mood_checkins"] = (
        int(
            user.get(
                "mood_checkins",
                0
            )
        ) + 1
    )

    history = user.setdefault(
        "mood_history",
        []
    )

    history.append(
        {
            "mood": mood,
            "timestamp": timestamp,
        }
    )

    # Prevent uncontrolled JSON growth.
    if len(history) > 1000:
        del history[:-1000]

    user["stats"]["mood_checkins"] = (
        int(
            user["stats"].get(
                "mood_checkins",
                0
            )
        ) + 1
    )

    user["updated_at"] = timestamp

    data["users"][user_id] = user

    # Keep date available for analytics consumers.
    data.setdefault(
        "analytics",
        {}
    ).setdefault(
        "mood",
        {}
    ).setdefault(
        date_key,
        []
    ).append(
        {
            "user_id": user_id,
            "mood": mood,
            "timestamp": timestamp,
        }
    )

    save_v4_data(data)

    return user


# ============================================================
# GROUP DATA
# ============================================================

def get_group(group_id):
    """
    Get or create a group.
    """

    data = load_v4_data()

    group_id = str(group_id)

    if group_id not in data["groups"]:

        group = _copy_group_default()

        group["group_id"] = group_id
        group["created_at"] = _now()
        group["updated_at"] = _now()

        data["groups"][group_id] = group

        save_v4_data(data)

    else:

        group = data["groups"][group_id]

        if not isinstance(
            group,
            dict
        ):
            group = _copy_group_default()

        group = _merge_dict(
            group,
            DEFAULT_GROUP
        )

        group["group_id"] = group_id

        data["groups"][group_id] = group

        save_v4_data(data)

    return data["groups"][group_id]


def update_group(
    group_id,
    updates
):
    """
    Update group fields while preserving nested data.
    """

    data = load_v4_data()

    group_id = str(group_id)

    group = data["groups"].get(
        group_id
    )

    if not isinstance(
        group,
        dict
    ):
        group = _copy_group_default()

    group = _merge_dict(
        group,
        DEFAULT_GROUP
    )

    if isinstance(
        updates,
        dict
    ):

        for key, value in updates.items():

            if (
                isinstance(value, dict)
                and isinstance(
                    group.get(key),
                    dict
                )
            ):

                group[key] = _merge_dict(
                    group[key],
                    value
                )

            else:
                group[key] = value

    group["group_id"] = group_id
    group["updated_at"] = _now()

    data["groups"][group_id] = group

    save_v4_data(data)

    return group


# ============================================================
# GROUP MEMBER DATA
# ============================================================

def get_group_member(
    group_id,
    user_id
):
    """
    Get or create a group member record.
    """

    data = load_v4_data()

    group_id = str(group_id)
    user_id = str(user_id)

    group = data["groups"].get(
        group_id
    )

    if not isinstance(
        group,
        dict
    ):
        group = _copy_group_default()

    group = _merge_dict(
        group,
        DEFAULT_GROUP
    )

    members = group.setdefault(
        "members",
        {}
    )

    if user_id not in members:

        member = _copy_member_default()

        member["user_id"] = user_id
        member["first_seen"] = _now()

        members[user_id] = member

        data["groups"][group_id] = group

        save_v4_data(data)

    else:

        member = members[user_id]

        if not isinstance(
            member,
            dict
        ):
            member = _copy_member_default()

        member = _merge_dict(
            member,
            DEFAULT_GROUP_MEMBER
        )

        member["user_id"] = user_id

        members[user_id] = member

        data["groups"][group_id] = group

        save_v4_data(data)

    return members[user_id]


def update_group_member(
    group_id,
    user_id,
    updates
):
    """
    Update a group member safely.
    """

    data = load_v4_data()

    group_id = str(group_id)
    user_id = str(user_id)

    group = data["groups"].get(
        group_id
    )

    if not isinstance(
        group,
        dict
    ):
        group = _copy_group_default()

    group = _merge_dict(
        group,
        DEFAULT_GROUP
    )

    member = group["members"].get(
        user_id
    )

    if not isinstance(
        member,
        dict
    ):
        member = _copy_member_default()

    member = _merge_dict(
        member,
        DEFAULT_GROUP_MEMBER
    )

    if isinstance(
        updates,
        dict
    ):

        for key, value in updates.items():

            if (
                isinstance(value, dict)
                and isinstance(
                    member.get(key),
                    dict
                )
            ):

                member[key] = _merge_dict(
                    member[key],
                    value
                )

            else:
                member[key] = value

    member["user_id"] = user_id
    member["last_seen"] = (
        member.get("last_seen")
        or _now()
    )

    group["members"][user_id] = member
    group["updated_at"] = _now()

    data["groups"][group_id] = group

    save_v4_data(data)

    return member


# ============================================================
# GROUP MESSAGE ANALYTICS
# ============================================================

def record_group_message(
    group_id,
    user_id,
    date_key=None,
    week_key=None,
    month_key=None,
    hour=None,
    weekday=None
):
    """
    Record one group message.

    Supports:
        • daily analytics
        • weekly analytics
        • monthly analytics
        • hourly analytics
        • weekday analytics
        • member activity
        • group total messages
        • active days
    """

    data = load_v4_data()

    group_id = str(group_id)
    user_id = str(user_id)

    timestamp = _now()

    if not date_key:
        date_key = timestamp[:10]

    if not week_key:

        try:
            date_object = datetime.fromisoformat(
                date_key
            )

            iso_year, iso_week, _ = (
                date_object.isocalendar()
            )

            week_key = (
                f"{iso_year}-W{iso_week:02d}"
            )

        except Exception:

            week_key = (
                date_key[:7]
                + "-week"
            )

    if not month_key:
        month_key = date_key[:7]

    if hour is None:

        try:
            hour = datetime.fromisoformat(
                timestamp
            ).hour
        except Exception:
            hour = datetime.now().hour

    if weekday is None:

        try:
            weekday = datetime.fromisoformat(
                timestamp
            ).strftime("%A")
        except Exception:
            weekday = "Unknown"

    # --------------------------------------------------------
    # Group
    # --------------------------------------------------------

    group = data["groups"].get(
        group_id
    )

    if not isinstance(
        group,
        dict
    ):
        group = _copy_group_default()

    group = _merge_dict(
        group,
        DEFAULT_GROUP
    )

    # --------------------------------------------------------
    # Group totals
    # --------------------------------------------------------

    group["total_messages"] = (
        int(
            group.get(
                "total_messages",
                0
            )
        ) + 1
    )

    group["daily"][date_key] = (
        int(
            group["daily"].get(
                date_key,
                0
            )
        ) + 1
    )

    group["weekly"][week_key] = (
        int(
            group["weekly"].get(
                week_key,
                0
            )
        ) + 1
    )

    group["monthly"][month_key] = (
        int(
            group["monthly"].get(
                month_key,
                0
            )
        ) + 1
    )

    hour_key = str(hour)

    group["hourly"][hour_key] = (
        int(
            group["hourly"].get(
                hour_key,
                0
            )
        ) + 1
    )

    group["weekday"][weekday] = (
        int(
            group["weekday"].get(
                weekday,
                0
            )
        ) + 1
    )

    # --------------------------------------------------------
    # Active group days
    # --------------------------------------------------------

    active_days = group["analytics"].setdefault(
        "active_days",
        []
    )

    if date_key not in active_days:
        active_days.append(date_key)

    # --------------------------------------------------------
    # Member
    # --------------------------------------------------------

    member = group["members"].get(
        user_id
    )

    if not isinstance(
        member,
        dict
    ):
        member = _copy_member_default()

    member = _merge_dict(
        member,
        DEFAULT_GROUP_MEMBER
    )

    member["user_id"] = user_id

    member["messages"] = (
        int(
            member.get(
                "messages",
                0
            )
        ) + 1
    )

    member["daily_messages"][date_key] = (
        int(
            member["daily_messages"].get(
                date_key,
                0
            )
        ) + 1
    )

    member["weekly_messages"][week_key] = (
        int(
            member["weekly_messages"].get(
                week_key,
                0
            )
        ) + 1
    )

    member["monthly_messages"][month_key] = (
        int(
            member["monthly_messages"].get(
                month_key,
                0
            )
        ) + 1
    )

    member["hourly_messages"][hour_key] = (
        int(
            member["hourly_messages"].get(
                hour_key,
                0
            )
        ) + 1
    )

    member["weekday_messages"][weekday] = (
        int(
            member["weekday_messages"].get(
                weekday,
                0
            )
        ) + 1
    )

    member["last_seen"] = timestamp

    if not member.get("first_seen"):
        member["first_seen"] = timestamp

    if date_key not in member["active_days"]:
        member["active_days"].append(
            date_key
        )

    group["members"][user_id] = member

    group["updated_at"] = timestamp

    data["groups"][group_id] = group

    # --------------------------------------------------------
    # User statistics
    # --------------------------------------------------------

    user = data["users"].get(
        user_id
    )

    if not isinstance(
        user,
        dict
    ):
        user = _copy_user_default()

    user = _merge_dict(
        user,
        DEFAULT_USER
    )

    user["user_id"] = user_id

    user["stats"]["messages_sent"] = (
        int(
            user["stats"].get(
                "messages_sent",
                0
            )
        ) + 1
    )

    user["stats"]["group_messages"] = (
        int(
            user["stats"].get(
                "group_messages",
                0
            )
        ) + 1
    )

    user["activity"]["daily_activity"][date_key] = (
        int(
            user["activity"]["daily_activity"].get(
                date_key,
                0
            )
        ) + 1
    )

    user["activity"]["weekly_activity"][week_key] = (
        int(
            user["activity"]["weekly_activity"].get(
                week_key,
                0
            )
        ) + 1
    )

    user["activity"]["monthly_activity"][month_key] = (
        int(
            user["activity"]["monthly_activity"].get(
                month_key,
                0
            )
        ) + 1
    )

    if date_key not in user["activity"]["active_days"]:
        user["activity"]["active_days"].append(
            date_key
        )

    user["last_active_date"] = date_key
    user["updated_at"] = timestamp

    data["users"][user_id] = user

    save_v4_data(data)

    return member


# ============================================================
# GROUP QUIZ DATA
# ============================================================

def record_group_quiz_answer(
    group_id,
    user_id,
    correct=False
):
    """
    Record one group quiz answer.
    """

    data = load_v4_data()

    group_id = str(group_id)
    user_id = str(user_id)

    group = data["groups"].get(
        group_id
    )

    if not isinstance(
        group,
        dict
    ):
        group = _copy_group_default()

    group = _merge_dict(
        group,
        DEFAULT_GROUP
    )

    member = group["members"].get(
        user_id
    )

    if not isinstance(
        member,
        dict
    ):
        member = _copy_member_default()

    member = _merge_dict(
        member,
        DEFAULT_GROUP_MEMBER
    )

    group["quiz"]["questions_answered"] += 1

    member["quiz_answered"] += 1

    if correct:

        group["quiz"]["correct_answers"] += 1
        member["quiz_correct"] += 1

    else:

        group["quiz"]["wrong_answers"] += 1
        member["quiz_wrong"] += 1

    group["members"][user_id] = member
    group["updated_at"] = _now()

    data["groups"][group_id] = group

    save_v4_data(data)

    return group["quiz"]


# ============================================================
# QUIZ GLOBAL DATA
# ============================================================

def get_quiz_data(quiz_id):
    """
    Get or create global quiz data.
    """

    data = load_v4_data()

    quiz_id = str(quiz_id)

    quiz = data["quiz"].get(
        quiz_id
    )

    if not isinstance(
        quiz,
        dict
    ):
        quiz = {
            "quiz_id": quiz_id,
            "created_at": _now(),
            "updated_at": _now(),
            "played": 0,
            "participants": 0,
            "questions": 0,
            "correct": 0,
            "wrong": 0,
            "leaderboard": {},
            "metadata": {},
        }

        data["quiz"][quiz_id] = quiz
        save_v4_data(data)

    return quiz


def update_quiz_data(
    quiz_id,
    updates
):
    """
    Update global quiz data.
    """

    data = load_v4_data()

    quiz_id = str(quiz_id)

    quiz = data["quiz"].get(
        quiz_id
    )

    if not isinstance(
        quiz,
        dict
    ):
        quiz = {
            "quiz_id": quiz_id,
            "created_at": _now(),
        }

    if isinstance(
        updates,
        dict
    ):

        quiz.update(updates)

    quiz["quiz_id"] = quiz_id
    quiz["updated_at"] = _now()

    data["quiz"][quiz_id] = quiz

    save_v4_data(data)

    return quiz


# ============================================================
# GOALS DATA
# ============================================================

def get_goals_data(user_id):
    """
    Get the goal container for a user.
    """

    data = load_v4_data()

    user_id = str(user_id)

    goals = data["goals"].setdefault(
        user_id,
        {
            "active": {},
            "completed": {},
            "history": [],
            "daily": {},
            "weekly": {},
            "metadata": {},
        }
    )

    if not isinstance(
        goals,
        dict
    ):
        goals = {
            "active": {},
            "completed": {},
            "history": [],
            "daily": {},
            "weekly": {},
            "metadata": {},
        }

        data["goals"][user_id] = goals

    save_v4_data(data)

    return goals


def update_goals_data(
    user_id,
    updates
):
    """
    Update a user's goals container.
    """

    data = load_v4_data()

    user_id = str(user_id)

    goals = data["goals"].setdefault(
        user_id,
        {}
    )

    if not isinstance(
        goals,
        dict
    ):
        goals = {}

    goals = _merge_dict(
        goals,
        {
            "active": {},
            "completed": {},
            "history": [],
            "daily": {},
            "weekly": {},
            "metadata": {},
        }
    )

    if isinstance(
        updates,
        dict
    ):

        for key, value in updates.items():

            if (
                isinstance(value, dict)
                and isinstance(
                    goals.get(key),
                    dict
                )
            ):

                goals[key] = _merge_dict(
                    goals[key],
                    value
                )

            else:
                goals[key] = value

    data["goals"][user_id] = goals

    save_v4_data(data)

    return goals


# ============================================================
# REWARDS DATA
# ============================================================

def get_rewards_data(user_id):
    """
    Get reward data for a user.
    """

    data = load_v4_data()

    user_id = str(user_id)

    rewards = data["rewards"].setdefault(
        user_id,
        {
            "claimed": [],
            "unlocked": [],
            "available": [],
            "total_claims": 0,
            "total_xp": 0,
            "history": [],
            "metadata": {},
        }
    )

    if not isinstance(
        rewards,
        dict
    ):
        rewards = {
            "claimed": [],
            "unlocked": [],
            "available": [],
            "total_claims": 0,
            "total_xp": 0,
            "history": [],
            "metadata": {},
        }

        data["rewards"][user_id] = rewards

    save_v4_data(data)

    return rewards


def update_rewards_data(
    user_id,
    updates
):
    """
    Update a user's reward data.
    """

    data = load_v4_data()

    user_id = str(user_id)

    rewards = data["rewards"].setdefault(
        user_id,
        {}
    )

    if not isinstance(
        rewards,
        dict
    ):
        rewards = {}

    rewards = _merge_dict(
        rewards,
        {
            "claimed": [],
            "unlocked": [],
            "available": [],
            "total_claims": 0,
            "total_xp": 0,
            "history": [],
            "metadata": {},
        }
    )

    if isinstance(
        updates,
        dict
    ):
        rewards.update(updates)

    data["rewards"][user_id] = rewards

    save_v4_data(data)

    return rewards


# ============================================================
# BIRTHDAY DATA
# ============================================================

def get_birthday_data(
    user_id=None
):
    """
    Get birthday data.

    If user_id is supplied, returns that user's birthday record.
    Otherwise returns the complete birthday section.
    """

    data = load_v4_data()

    if user_id is None:
        return data["birthdays"]

    user_id = str(user_id)

    birthday = data["birthdays"].setdefault(
        user_id,
        {
            "date": None,
            "name": "",
            "enabled": True,
            "last_notified": None,
            "metadata": {},
        }
    )

    if not isinstance(
        birthday,
        dict
    ):
        birthday = {
            "date": None,
            "name": "",
            "enabled": True,
            "last_notified": None,
            "metadata": {},
        }

        data["birthdays"][user_id] = birthday

    save_v4_data(data)

    return birthday


def update_birthday_data(
    user_id,
    updates
):
    """
    Update birthday information for a user.
    """

    data = load_v4_data()

    user_id = str(user_id)

    birthday = data["birthdays"].setdefault(
        user_id,
        {}
    )

    birthday = _merge_dict(
        birthday,
        {
            "date": None,
            "name": "",
            "enabled": True,
            "last_notified": None,
            "metadata": {},
        }
    )

    if isinstance(
        updates,
        dict
    ):
        birthday.update(updates)

    data["birthdays"][user_id] = birthday

    save_v4_data(data)

    return birthday


# ============================================================
# NOTIFICATION DATA
# ============================================================

def get_notification_data(
    user_id
):
    """
    Get notification state for a user.
    """

    data = load_v4_data()

    user_id = str(user_id)

    notifications = data["notifications"].setdefault(
        user_id,
        {
            "history": [],
            "last_sent": {},
            "scheduled": [],
            "failed": [],
            "metadata": {},
        }
    )

    if not isinstance(
        notifications,
        dict
    ):
        notifications = {
            "history": [],
            "last_sent": {},
            "scheduled": [],
            "failed": [],
            "metadata": {},
        }

        data["notifications"][user_id] = notifications

    save_v4_data(data)

    return notifications


def update_notification_data(
    user_id,
    updates
):
    """
    Update notification state.
    """

    data = load_v4_data()

    user_id = str(user_id)

    notifications = data["notifications"].setdefault(
        user_id,
        {}
    )

    notifications = _merge_dict(
        notifications,
        {
            "history": [],
            "last_sent": {},
            "scheduled": [],
            "failed": [],
            "metadata": {},
        }
    )

    if isinstance(
        updates,
        dict
    ):
        notifications.update(updates)

    data["notifications"][user_id] = notifications

    save_v4_data(data)

    return notifications


# ============================================================
# ANALYTICS DATA
# ============================================================

def get_analytics_data(
    key=None
):
    """
    Get global analytics data or one analytics section.
    """

    data = load_v4_data()

    if key is None:
        return data["analytics"]

    value = data["analytics"].setdefault(
        str(key),
        {}
    )

    save_v4_data(data)

    return value


def update_analytics_data(
    key,
    updates
):
    """
    Update a global analytics section.
    """

    data = load_v4_data()

    key = str(key)

    analytics = data["analytics"].setdefault(
        key,
        {}
    )

    if not isinstance(
        analytics,
        dict
    ):
        analytics = {}

    if isinstance(
        updates,
        dict
    ):
        analytics = _merge_dict(
            analytics,
            updates
        )

    data["analytics"][key] = analytics

    save_v4_data(data)

    return analytics


# ============================================================
# DATABASE STATUS
# ============================================================

def get_database_status():
    """
    Return useful database health information.
    """

    data = load_v4_data()

    try:
        file_size = os.path.getsize(
            V4_DATA_FILE
        )
    except Exception:
        file_size = 0

    return {
        "file": V4_DATA_FILE,
        "exists": os.path.exists(
            V4_DATA_FILE
        ),
        "version": data["system"]["version"],
        "users": len(
            data["users"]
        ),
        "groups": len(
            data["groups"]
        ),
        "quiz_records": len(
            data["quiz"]
        ),
        "goal_records": len(
            data["goals"]
        ),
        "reward_records": len(
            data["rewards"]
        ),
        "birthday_records": len(
            data["birthdays"]
        ),
        "notification_records": len(
            data["notifications"]
        ),
        "file_size": file_size,
        "created_at": data["system"].get(
            "created_at"
        ),
        "updated_at": data["system"].get(
            "updated_at"
        ),
        "last_backup_at": data["system"].get(
            "last_backup_at"
        ),
        "database_recoveries": data["system"].get(
            "database_recoveries",
            0
        ),
    }


# ============================================================
# BACKUP
# ============================================================

def create_v4_backup(
    destination=None
):
    """
    Create a complete JSON backup.

    If destination is omitted, a timestamped backup is created
    inside the V4 backup directory.
    """

    data = load_v4_data()

    if destination is None:

        os.makedirs(
            V4_BACKUP_DIR,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        destination = os.path.join(
            V4_BACKUP_DIR,
            f"moodbloom_v4_{timestamp}.json"
        )

    try:

        folder = os.path.dirname(
            destination
        )

        if folder:
            os.makedirs(
                folder,
                exist_ok=True
            )

        with open(
            destination,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        # Update metadata in the main database.
        try:

            fresh_data = load_v4_data()

            fresh_data["system"][
                "last_backup_at"
            ] = _now()

            save_v4_data(
                fresh_data
            )

        except Exception:
            pass

        return True

    except Exception as error:

        print(
            "⚠️ V4 backup error:",
            error
        )

        return False


# ============================================================
# RESTORE BACKUP
# ============================================================

def restore_v4_backup(
    backup_file
):
    """
    Restore the V4 database from a backup file.

    The current database is backed up first whenever possible.
    """

    if not backup_file:
        return False

    if not os.path.exists(
        backup_file
    ):
        print(
            "⚠️ Backup file does not exist:",
            backup_file
        )
        return False

    try:

        with open(
            backup_file,
            "r",
            encoding="utf-8"
        ) as file:

            restored_data = json.load(
                file
            )

        restored_data = _merge_defaults(
            restored_data
        )

        # Preserve the current database before restoring.
        try:
            create_v4_backup()
        except Exception:
            pass

        if save_v4_data(
            restored_data
        ):

            print(
                "♻️ MoodBloom V4 database restored."
            )

            return True

        return False

    except Exception as error:

        print(
            "⚠️ V4 restore error:",
            error
        )

        return False


# ============================================================
# COPY DATABASE
# ============================================================

def copy_v4_database(
    destination
):
    """
    Make a direct filesystem copy of the V4 database.

    Useful for external backup/recovery workflows.
    """

    try:

        ensure_v4_database()

        folder = os.path.dirname(
            destination
        )

        if folder:
            os.makedirs(
                folder,
                exist_ok=True
            )

        shutil.copy2(
            V4_DATA_FILE,
            destination
        )

        return True

    except Exception as error:

        print(
            "⚠️ V4 database copy error:",
            error
        )

        return False


# ============================================================
# DATABASE VALIDATION
# ============================================================

def validate_v4_database():
    """
    Validate basic V4 database structure.

    Returns:
        {
            "valid": bool,
            "errors": [...]
        }
    """

    errors = []

    try:

        data = load_v4_data()

        required_sections = [
            "users",
            "groups",
            "quiz",
            "goals",
            "rewards",
            "birthdays",
            "study",
            "notifications",
            "analytics",
            "system",
        ]

        for section in required_sections:

            if section not in data:
                errors.append(
                    f"Missing section: {section}"
                )

        if not isinstance(
            data.get("users"),
            dict
        ):
            errors.append(
                "users must be a dictionary"
            )

        if not isinstance(
            data.get("groups"),
            dict
        ):
            errors.append(
                "groups must be a dictionary"
            )

        if not isinstance(
            data.get("system"),
            dict
        ):
            errors.append(
                "system must be a dictionary"
            )

    except Exception as error:

        errors.append(
            str(error)
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


# ============================================================
# DATABASE RESET
# ============================================================

def reset_v4_database(
    create_backup=True
):
    """
    Reset V4 database to a fresh default state.

    A backup is created first by default.
    """

    try:

        if create_backup and os.path.exists(
            V4_DATA_FILE
        ):

            try:
                create_v4_backup()
            except Exception:
                pass

        data = _deep_copy_default()

        data["system"]["created_at"] = _now()
        data["system"]["updated_at"] = _now()

        return save_v4_data(
            data
        )

    except Exception as error:

        print(
            "⚠️ V4 database reset error:",
            error
        )

        return False


# ============================================================
# MODULE INITIALIZATION
# ============================================================

try:
    ensure_v4_database()
except Exception as initialization_error:

    print(
        "⚠️ MoodBloom V4 initialization warning:",
        initialization_error
    )

