# ============================================================
# MOODBLOOM 4.0 — GROUP DATA
# ============================================================

import json
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import DATA_FILE


# ============================================================
# PATHS
# ============================================================

GROUP_DATA_PATH = Path(DATA_FILE).with_name("groups.json")
IST = ZoneInfo("Asia/Kolkata")


# ============================================================
# DATABASE
# ============================================================

def ensure_group_database():
    GROUP_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not GROUP_DATA_PATH.exists():
        with open(GROUP_DATA_PATH, "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4, ensure_ascii=False)


def load_groups():
    ensure_group_database()

    try:
        with open(GROUP_DATA_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
    except (json.JSONDecodeError, OSError):
        pass

    return {}


def save_groups(groups):
    ensure_group_database()
    temp_path = GROUP_DATA_PATH.with_suffix(".tmp")

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(groups, file, indent=4, ensure_ascii=False)

    temp_path.replace(GROUP_DATA_PATH)


# ============================================================
# TIME
# ============================================================

def now():
    return datetime.now(IST)


def today():
    return now().strftime("%Y-%m-%d")


def current_time():
    return now().strftime("%H:%M")


def timestamp():
    return now().isoformat()


# ============================================================
# GROUP CREATE
# ============================================================

def create_group(chat_id, group_name="This Group"):
    return {
        "chat_id": chat_id,
        "name": group_name,
        "created_at": timestamp(),
        "members": {},
        "moods": [],
        "daily_questions": {},
        "activity": {
            "messages": 0,
            "mood_checkins": 0,
            "games_played": 0,
            "questions_answered": 0,
        },
        "settings": {
            "welcome_enabled": True,
            "welcome_message": None,
            "goodbye_message": None,
            "reminder_enabled": False,
            "reminder_time": None,
            "announcement_enabled": True,
        },
    }


def get_group(groups, chat_id, group_name="This Group"):
    key = str(chat_id)

    if key not in groups:
        groups[key] = create_group(chat_id, group_name)
    else:
        if group_name and groups[key].get("name") != group_name:
            groups[key]["name"] = group_name

        # Ensure settings defaults exist
        settings = groups[key].setdefault("settings", {})
        settings.setdefault("welcome_enabled", True)
        settings.setdefault("welcome_message", None)
        settings.setdefault("goodbye_message", None)
        settings.setdefault("reminder_enabled", False)
        settings.setdefault("reminder_time", None)
        settings.setdefault("announcement_enabled", True)

    return groups[key]


# ============================================================
# MEMBERS
# ============================================================

def add_member(groups, chat_id, user_id, username=None, first_name=None,
               group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    member_key = str(user_id)

    if member_key not in group["members"]:
        group["members"][member_key] = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name or "User",
            "joined_at": timestamp(),
            "checkins": 0,
            "points": 0,
        }
    else:
        member = group["members"][member_key]

        if username is not None:
            member["username"] = username
        if first_name is not None:
            member["first_name"] = first_name

    return group["members"][member_key]


def remove_member(groups, chat_id, user_id):
    """
    Removes a member from the group record.
    Returns True if removed, False if not found.
    """
    group = groups.get(str(chat_id))
    if not group:
        return False

    member_key = str(user_id)

    if member_key in group.get("members", {}):
        del group["members"][member_key]
        return True

    return False


def get_member(groups, chat_id, user_id):
    group = groups.get(str(chat_id))
    if not group:
        return None

    return group["members"].get(str(user_id))


def get_group_member_count(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return 0

    return len(group.get("members", {}))


def get_group_members_list(groups, chat_id):
    """
    Returns list of member dicts for mention-all.
    Format: [{"user_id": ..., "first_name": ...}, ...]
    """
    group = groups.get(str(chat_id))
    if not group:
        return []

    result = []
    for user_id, info in group.get("members", {}).items():
        result.append({
            "user_id": user_id,
            "first_name": info.get("first_name", "User"),
            "username": info.get("username", ""),
        })

    return result


# ============================================================
# MOODS
# ============================================================

def record_group_mood(groups, chat_id, user_id, mood_key, user_name=None,
                      group_name="This Group"):
    group = get_group(groups, chat_id, group_name)

    member = add_member(
        groups, chat_id, user_id,
        first_name=user_name,
        group_name=group_name,
    )

    entry = {
        "user_id": user_id,
        "user_name": user_name or member.get("first_name", "User"),
        "mood": mood_key,
        "date": today(),
        "time": current_time(),
        "timestamp": timestamp(),
    }

    group["moods"].append(entry)

    member["checkins"] = member.get("checkins", 0) + 1
    member["points"] = member.get("points", 0) + 10

    group["activity"]["mood_checkins"] = (
        group["activity"].get("mood_checkins", 0) + 1
    )

    return entry


def get_group_moods(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return []

    return group.get("moods", [])


def get_group_total_checkins(groups, chat_id):
    return len(get_group_moods(groups, chat_id))


# ============================================================
# MOOD COUNTS
# ============================================================

def get_group_mood_counts(groups, chat_id):
    counts = {}

    for entry in get_group_moods(groups, chat_id):
        mood = entry.get("mood", "unknown")
        counts[mood] = counts.get(mood, 0) + 1

    return counts


def get_group_dominant_mood(groups, chat_id):
    counts = get_group_mood_counts(groups, chat_id)

    if not counts:
        return None

    return max(counts, key=counts.get)


# ============================================================
# MOOD SCORES
# ============================================================

MOOD_SCORES = {
    "happy": 5,
    "excited": 5,
    "calm": 4,
    "good": 4,
    "neutral": 3,
    "okay": 3,
    "tired": 2,
    "sad": 2,
    "angry": 1,
    "stressed": 1,
    "anxious": 1,
}


def get_mood_score(mood_key):
    return MOOD_SCORES.get(str(mood_key).lower(), 3)


def get_group_average_score(groups, chat_id):
    moods = get_group_moods(groups, chat_id)

    if not moods:
        return None

    total = sum(get_mood_score(entry.get("mood")) for entry in moods)

    return round(total / len(moods), 2)


# ============================================================
# LEADERBOARD
# ============================================================

def get_group_leaderboard(groups, chat_id, limit=10):
    group = groups.get(str(chat_id))
    if not group:
        return []

    members = []

    for member in group.get("members", {}).values():
        members.append({
            "user_id": member.get("user_id"),
            "name": member.get("first_name", "User"),
            "username": member.get("username"),
            "points": member.get("points", 0),
            "checkins": member.get("checkins", 0),
        })

    members.sort(
        key=lambda x: (x["points"], x["checkins"]),
        reverse=True,
    )

    return members[:limit]


# ============================================================
# STREAK
# ============================================================

def _get_unique_mood_dates(groups, chat_id):
    dates = set()

    for entry in get_group_moods(groups, chat_id):
        date_value = entry.get("date")
        if date_value:
            dates.add(date_value)

    return dates


def calculate_group_streak(groups, chat_id):
    date_strings = _get_unique_mood_dates(groups, chat_id)

    if not date_strings:
        return 0

    dates = sorted(
        datetime.strptime(d, "%Y-%m-%d").date()
        for d in date_strings
    )

    current = dates[-1]
    streak = 1

    for i in range(len(dates) - 1, 0, -1):
        if dates[i] - dates[i - 1] == timedelta(days=1):
            streak += 1
        else:
            break

    if current != now().date():
        return 0

    return streak


def calculate_best_group_streak(groups, chat_id):
    date_strings = _get_unique_mood_dates(groups, chat_id)

    if not date_strings:
        return 0

    dates = sorted(
        datetime.strptime(d, "%Y-%m-%d").date()
        for d in date_strings
    )

    best = 1
    current = 1

    for i in range(1, len(dates)):
        if dates[i] - dates[i - 1] == timedelta(days=1):
            current += 1
        else:
            current = 1

        best = max(best, current)

    return best


# ============================================================
# DAILY QUESTION
# ============================================================

def get_daily_question_data(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return None

    return group.get("daily_questions", {}).get(today())


def set_daily_question(groups, chat_id, question, group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    date_value = today()

    group["daily_questions"][date_value] = {
        "question": question,
        "participants": [],
        "created_at": timestamp(),
    }

    return group["daily_questions"][date_value]


def record_question_participation(groups, chat_id, user_id, question=None,
                                  group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    date_value = today()

    if date_value not in group["daily_questions"]:
        group["daily_questions"][date_value] = {
            "question": question,
            "participants": [],
            "created_at": timestamp(),
        }

    participants = group["daily_questions"][date_value]["participants"]

    if user_id not in participants:
        participants.append(user_id)
        group["activity"]["questions_answered"] = (
            group["activity"].get("questions_answered", 0) + 1
        )


# ============================================================
# ACTIVITY
# ============================================================

def record_group_activity(groups, chat_id, activity_type, amount=1,
                          group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    group["activity"][activity_type] = (
        group["activity"].get(activity_type, 0) + amount
    )


def get_group_activity(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return {}

    return group.get("activity", {})


# ============================================================
# WELCOME SETTINGS
# ============================================================

def is_welcome_enabled(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return True

    return group.get("settings", {}).get("welcome_enabled", True)


def set_welcome_enabled(groups, chat_id, enabled, group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    group["settings"]["welcome_enabled"] = bool(enabled)


# ============================================================
# CUSTOM WELCOME / GOODBYE
# ============================================================

def get_custom_welcome_message(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return None

    return group.get("settings", {}).get("welcome_message")


def set_custom_welcome_message(groups, chat_id, message, group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    group["settings"]["welcome_message"] = message


def get_custom_goodbye_message(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return None

    return group.get("settings", {}).get("goodbye_message")


def set_custom_goodbye_message(groups, chat_id, message, group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    group["settings"]["goodbye_message"] = message


def reset_custom_messages(groups, chat_id, group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    group["settings"]["welcome_message"] = None
    group["settings"]["goodbye_message"] = None


# ============================================================
# GROUP REMINDER
# ============================================================

def get_group_reminder(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return {"enabled": False, "time": None}

    settings = group.get("settings", {})

    return {
        "enabled": settings.get("reminder_enabled", False),
        "time": settings.get("reminder_time"),
    }


def set_group_reminder(groups, chat_id, enabled, reminder_time=None,
                       group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    group["settings"]["reminder_enabled"] = bool(enabled)
    group["settings"]["reminder_time"] = reminder_time


# ============================================================
# SETTINGS
# ============================================================

def get_group_settings(groups, chat_id):
    group = groups.get(str(chat_id))
    if not group:
        return {}

    return group.get("settings", {})


def update_group_setting(groups, chat_id, setting, value,
                         group_name="This Group"):
    group = get_group(groups, chat_id, group_name)
    group["settings"][setting] = value


# ============================================================
# SUMMARY
# ============================================================

def get_group_summary(groups, chat_id):
    return {
        "member_count": get_group_member_count(groups, chat_id),
        "total_checkins": get_group_total_checkins(groups, chat_id),
        "mood_counts": get_group_mood_counts(groups, chat_id),
        "dominant_mood": get_group_dominant_mood(groups, chat_id),
        "average_score": get_group_average_score(groups, chat_id),
        "current_streak": calculate_group_streak(groups, chat_id),
        "best_streak": calculate_best_group_streak(groups, chat_id),
        "leaderboard": get_group_leaderboard(groups, chat_id),
        "activity": get_group_activity(groups, chat_id),
    }


# ============================================================
# CLEANUP
# ============================================================

def cleanup_old_questions(groups, days=30):
    cutoff = now().date() - timedelta(days=days)

    for group in groups.values():
        questions = group.get("daily_questions", {})
        old_dates = []

        for date_string in questions:
            try:
                date_value = datetime.strptime(date_string, "%Y-%m-%d").date()
                if date_value < cutoff:
                    old_dates.append(date_string)
            except ValueError:
                old_dates.append(date_string)

        for date_string in old_dates:
            del questions[date_string]


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "ensure_group_database", "load_groups", "save_groups",
    "now", "today", "current_time", "timestamp",
    "create_group", "get_group",
    "add_member", "remove_member", "get_member",
    "get_group_member_count", "get_group_members_list",
    "record_group_mood", "get_group_moods", "get_group_total_checkins",
    "get_group_mood_counts", "get_group_dominant_mood",
    "get_mood_score", "get_group_average_score",
    "get_group_leaderboard",
    "calculate_group_streak", "calculate_best_group_streak",
    "get_daily_question_data", "set_daily_question", "record_question_participation",
    "record_group_activity", "get_group_activity",
    "is_welcome_enabled", "set_welcome_enabled",
    "get_custom_welcome_message", "set_custom_welcome_message",
    "get_custom_goodbye_message", "set_custom_goodbye_message",
    "reset_custom_messages",
    "get_group_reminder", "set_group_reminder",
    "get_group_settings", "update_group_setting",
    "get_group_summary", "cleanup_old_questions",
]