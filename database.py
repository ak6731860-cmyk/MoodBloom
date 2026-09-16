import json
from pathlib import Path
from datetime import datetime

from config import DATA_FILE


# ============================================================
# DATABASE PATH
# ============================================================

DATA_PATH = Path(DATA_FILE)


# ============================================================
# DATABASE SETUP
# ============================================================

def ensure_database():
    """Create the database folder/file if it does not exist."""

    DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not DATA_PATH.exists():

        with open(
            DATA_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {},
                file,
                indent=4,
                ensure_ascii=False
            )


# ============================================================
# LOAD / SAVE
# ============================================================

def load_data():
    """Load complete JSON database safely."""

    ensure_database()

    try:

        with open(
            DATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, dict):
                return data

            return {}

    except (
        json.JSONDecodeError,
        OSError
    ):

        return {}


def save_data(data):
    """Save complete database safely."""

    ensure_database()

    with open(
        DATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# USER HISTORY
# ============================================================

def get_user_history(user_id):

    data = load_data()

    history = data.get(
        str(user_id),
        []
    )

    if not isinstance(history, list):
        return []

    return history


def save_user_history(
    user_id,
    user_history
):

    data = load_data()

    data[str(user_id)] = user_history

    save_data(data)


# ============================================================
# ADD MOOD
# ============================================================

def add_mood(
    user_id,
    mood,
    note=""
):

    history = get_user_history(user_id)

    now = datetime.now()

    entry = {

        "mood": mood,

        "date": now.strftime(
            "%Y-%m-%d"
        ),

        "time": now.strftime(
            "%d %b %Y, %I:%M %p"
        )
    }

    # Optional journal/note support
    if note:

        entry["note"] = str(note).strip()

    history.append(entry)

    save_user_history(
        user_id,
        history
    )

    return entry


# ============================================================
# CLEAR USER HISTORY
# ============================================================

def clear_user_history(user_id):

    data = load_data()

    data.pop(
        str(user_id),
        None
    )

    save_data(data)


# ============================================================
# USER SETTINGS
# ============================================================

def get_user_settings(user_id):

    data = load_data()

    settings = data.get(
        f"{user_id}_settings",
        {}
    )

    if not isinstance(
        settings,
        dict
    ):
        return {}

    return settings


def save_user_settings(
    user_id,
    settings
):

    data = load_data()

    data[f"{user_id}_settings"] = settings

    save_data(data)


# ============================================================
# REMINDER SETTINGS
# ============================================================

def set_user_reminder(
    user_id,
    hour,
    minute
):

    settings = get_user_settings(
        user_id
    )

    settings.update({

        "reminder_enabled": True,

        "reminder_hour": int(hour),

        "reminder_minute": int(minute)
    })

    save_user_settings(
        user_id,
        settings
    )


def get_user_reminder(user_id):

    settings = get_user_settings(
        user_id
    )

    if not settings.get(
        "reminder_enabled",
        False
    ):
        return None

    return settings


def disable_user_reminder(user_id):

    settings = get_user_settings(
        user_id
    )

    settings["reminder_enabled"] = False

    save_user_settings(
        user_id,
        settings
    )


# ============================================================
# USER PROFILE
# ============================================================

def get_user_profile(user_id):

    settings = get_user_settings(
        user_id
    )

    profile = settings.get(
        "profile",
        {}
    )

    if not isinstance(
        profile,
        dict
    ):
        profile = {}

    return profile


def save_user_profile(
    user_id,
    profile
):

    settings = get_user_settings(
        user_id
    )

    settings["profile"] = profile

    save_user_settings(
        user_id,
        settings
    )


# ============================================================
# XP / LEVEL
# ============================================================

def get_user_xp(user_id):

    profile = get_user_profile(
        user_id
    )

    try:

        return int(
            profile.get(
                "xp",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return 0


def set_user_xp(
    user_id,
    xp
):

    profile = get_user_profile(
        user_id
    )

    profile["xp"] = max(
        0,
        int(xp)
    )

    save_user_profile(
        user_id,
        profile
    )


def add_user_xp(
    user_id,
    amount
):

    current_xp = get_user_xp(
        user_id
    )

    new_xp = current_xp + int(amount)

    set_user_xp(
        user_id,
        new_xp
    )

    return new_xp


def get_user_level(user_id):

    xp = get_user_xp(
        user_id
    )

    return max(
        1,
        (xp // 100) + 1
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

def get_user_achievements(user_id):

    profile = get_user_profile(
        user_id
    )

    achievements = profile.get(
        "achievements",
        []
    )

    if not isinstance(
        achievements,
        list
    ):
        return []

    return achievements


def add_user_achievement(
    user_id,
    achievement
):

    achievements = get_user_achievements(
        user_id
    )

    if achievement not in achievements:

        achievements.append(
            achievement
        )

    profile = get_user_profile(
        user_id
    )

    profile["achievements"] = achievements

    save_user_profile(
        user_id,
        profile
    )

    return achievements


# ============================================================
# USER GOALS
# ============================================================

def get_user_goals(user_id):

    profile = get_user_profile(
        user_id
    )

    goals = profile.get(
        "goals",
        []
    )

    if not isinstance(
        goals,
        list
    ):
        return []

    return goals


def save_user_goals(
    user_id,
    goals
):

    profile = get_user_profile(
        user_id
    )

    profile["goals"] = goals

    save_user_profile(
        user_id,
        profile
    )


def add_user_goal(
    user_id,
    goal
):

    goals = get_user_goals(
        user_id
    )

    goals.append(
        goal
    )

    save_user_goals(
        user_id,
        goals
    )

    return goal


# ============================================================
# USER REGISTRY
# ============================================================

def register_user(
    user_id,
    username="",
    first_name=""
):
    """
    Register a private user for automated features.

    Used later for:
    - Morning wishes
    - Night reflection
    - Notifications
    - Daily questions
    - User analytics
    """

    data = load_data()

    key = f"user_registry_{user_id}"

    existing = data.get(
        key,
        {}
    )

    if not isinstance(
        existing,
        dict
    ):
        existing = {}

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if not existing.get(
        "registered_at"
    ):
        existing["registered_at"] = now

    existing.update({

        "user_id": str(user_id),

        "username": username or "",

        "first_name": first_name or "",

        "last_seen": now,

        "active": True
    })

    data[key] = existing

    save_data(data)

    return existing


def get_registered_user(user_id):

    data = load_data()

    user = data.get(
        f"user_registry_{user_id}",
        {}
    )

    if not isinstance(
        user,
        dict
    ):
        return {}

    return user


def get_all_registered_users(
    active_only=True
):

    data = load_data()

    users = []

    prefix = "user_registry_"

    for key, value in data.items():

        if not key.startswith(prefix):
            continue

        if not isinstance(
            value,
            dict
        ):
            continue

        if active_only and not value.get(
            "active",
            True
        ):
            continue

        users.append(value)

    return users


def deactivate_user(user_id):

    data = load_data()

    key = f"user_registry_{user_id}"

    user = data.get(
        key,
        {}
    )

    if isinstance(
        user,
        dict
    ):

        user["active"] = False

        data[key] = user

        save_data(data)


def update_user_last_seen(user_id):

    data = load_data()

    key = f"user_registry_{user_id}"

    user = data.get(
        key,
        {}
    )

    if not isinstance(
        user,
        dict
    ):
        return

    user["last_seen"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    user["active"] = True

    data[key] = user

    save_data(data)


# ============================================================
# GROUP DATABASE
# ============================================================

def get_group_data(chat_id):

    data = load_data()

    key = f"group_{chat_id}"

    group = data.get(
        key,
        {}
    )

    if not isinstance(
        group,
        dict
    ):
        group = {}

    return group


def save_group_data(
    chat_id,
    group_data
):

    data = load_data()

    data[f"group_{chat_id}"] = group_data

    save_data(data)


# ============================================================
# GROUP REGISTRY
# ============================================================

def register_group(
    chat_id,
    title="",
    username=""
):
    """
    Register a group for automated GC features.

    Used later for:
    - Morning wishes
    - Night reports
    - GC vibe analysis
    - Emoji analytics
    - Rankings
    """

    data = load_data()

    key = f"group_registry_{chat_id}"

    existing = data.get(
        key,
        {}
    )

    if not isinstance(
        existing,
        dict
    ):
        existing = {}

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if not existing.get(
        "registered_at"
    ):
        existing["registered_at"] = now

    existing.update({

        "chat_id": str(chat_id),

        "title": title or "",

        "username": username or "",

        "last_seen": now,

        "active": True
    })

    data[key] = existing

    save_data(data)

    return existing


def get_registered_group(chat_id):

    data = load_data()

    group = data.get(
        f"group_registry_{chat_id}",
        {}
    )

    if not isinstance(
        group,
        dict
    ):
        return {}

    return group


def get_all_registered_groups(
    active_only=True
):

    data = load_data()

    groups = []

    prefix = "group_registry_"

    for key, value in data.items():

        if not key.startswith(prefix):
            continue

        if not isinstance(
            value,
            dict
        ):
            continue

        if active_only and not value.get(
            "active",
            True
        ):
            continue

        groups.append(value)

    return groups


def deactivate_group(chat_id):

    data = load_data()

    key = f"group_registry_{chat_id}"

    group = data.get(
        key,
        {}
    )

    if isinstance(
        group,
        dict
    ):

        group["active"] = False

        data[key] = group

        save_data(data)


def update_group_last_seen(chat_id):

    data = load_data()

    key = f"group_registry_{chat_id}"

    group = data.get(
        key,
        {}
    )

    if not isinstance(
        group,
        dict
    ):
        return

    group["last_seen"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    group["active"] = True

    data[key] = group

    save_data(data)


# ============================================================
# GROUP SETTINGS
# ============================================================

def get_group_settings(chat_id):

    group = get_group_data(
        chat_id
    )

    settings = group.get(
        "settings",
        {}
    )

    if not isinstance(
        settings,
        dict
    ):
        settings = {}

    return settings


def save_group_settings(
    chat_id,
    settings
):

    group = get_group_data(
        chat_id
    )

    group["settings"] = settings

    save_group_data(
        chat_id,
        group
    )


# ============================================================
# GROUP MEMBERS
# ============================================================

def get_group_members(chat_id):

    group = get_group_data(
        chat_id
    )

    members = group.get(
        "members",
        {}
    )

    if not isinstance(
        members,
        dict
    ):
        members = {}

    return members


def save_group_members(
    chat_id,
    members
):

    group = get_group_data(
        chat_id
    )

    group["members"] = members

    save_group_data(
        chat_id,
        group
    )


def add_group_member(
    chat_id,
    user_id,
    username="",
    first_name=""
):

    members = get_group_members(
        chat_id
    )

    user_id = str(user_id)

    member = members.get(
        user_id,
        {}
    )

    if not isinstance(
        member,
        dict
    ):
        member = {}

    member.update({

        "username": username,

        "first_name": first_name,

        "last_seen": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    })

    if "xp" not in member:
        member["xp"] = 0

    if "messages" not in member:
        member["messages"] = 0

    members[user_id] = member

    save_group_members(
        chat_id,
        members
    )

    return member


# ============================================================
# GROUP MEMBER XP
# ============================================================

def get_group_member_xp(
    chat_id,
    user_id
):

    members = get_group_members(
        chat_id
    )

    member = members.get(
        str(user_id),
        {}
    )

    try:

        return int(
            member.get(
                "xp",
                0
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return 0


def add_group_member_xp(
    chat_id,
    user_id,
    amount
):

    members = get_group_members(
        chat_id
    )

    user_id = str(user_id)

    if user_id not in members:

        members[user_id] = {
            "xp": 0,
            "messages": 0
        }

    member = members[user_id]

    if not isinstance(
        member,
        dict
    ):
        member = {
            "xp": 0,
            "messages": 0
        }

    member["xp"] = max(
        0,
        int(
            member.get(
                "xp",
                0
            )
        ) + int(amount)
    )

    members[user_id] = member

    save_group_members(
        chat_id,
        members
    )

    return member["xp"]


# ============================================================
# GROUP MOOD HISTORY
# ============================================================

def get_group_mood_history(chat_id):

    group = get_group_data(
        chat_id
    )

    history = group.get(
        "mood_history",
        []
    )

    if not isinstance(
        history,
        list
    ):
        return []

    return history


def add_group_mood(
    chat_id,
    user_id,
    mood,
    username="",
    first_name=""
):

    group = get_group_data(
        chat_id
    )

    history = group.get(
        "mood_history",
        []
    )

    if not isinstance(
        history,
        list
    ):
        history = []

    now = datetime.now()

    entry = {

        "user_id": str(user_id),

        "username": username,

        "first_name": first_name,

        "mood": mood,

        "date": now.strftime(
            "%Y-%m-%d"
        ),

        "time": now.strftime(
            "%d %b %Y, %I:%M %p"
        )
    }

    history.append(
        entry
    )

    group["mood_history"] = history

    save_group_data(
        chat_id,
        group
    )

    return entry


# ============================================================
# GROUP VIBE / EMOJI ANALYTICS
# ============================================================

def get_group_vibe_data(chat_id):

    group = get_group_data(
        chat_id
    )

    vibe_data = group.get(
        "vibe",
        {}
    )

    if not isinstance(
        vibe_data,
        dict
    ):
        vibe_data = {}

    return vibe_data


def save_group_vibe_data(
    chat_id,
    vibe_data
):

    group = get_group_data(
        chat_id
    )

    group["vibe"] = vibe_data

    save_group_data(
        chat_id,
        group
    )


def get_group_daily_vibe(
    chat_id,
    date=None
):

    if date is None:

        date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    vibe_data = get_group_vibe_data(
        chat_id
    )

    daily = vibe_data.get(
        date,
        {}
    )

    if not isinstance(
        daily,
        dict
    ):
        daily = {}

    return daily


def save_group_daily_vibe(
    chat_id,
    date,
    daily_data
):

    vibe_data = get_group_vibe_data(
        chat_id
    )

    vibe_data[date] = daily_data

    save_group_vibe_data(
        chat_id,
        vibe_data
    )


def ensure_group_daily_vibe(
    chat_id,
    date=None
):

    if date is None:

        date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    daily = get_group_daily_vibe(
        chat_id,
        date
    )

    changed = False

    defaults = {

        "date": date,

        "messages": 0,

        "emoji_total": 0,

        "reaction_total": 0,

        "emoji_counts": {},

        "reaction_counts": {},

        "positive_score": 0,

        "low_vibe_score": 0,

        "fun_score": 0,

        "calm_score": 0,

        "energy_score": 0,

        "angry_score": 0,

        "neutral_score": 0
    }

    for key, value in defaults.items():

        if key not in daily:

            daily[key] = value

            changed = True

    if changed:

        save_group_daily_vibe(
            chat_id,
            date,
            daily
        )

    return daily


def increment_group_messages(
    chat_id,
    amount=1,
    date=None
):

    daily = ensure_group_daily_vibe(
        chat_id,
        date
    )

    daily["messages"] = max(
        0,
        int(
            daily.get(
                "messages",
                0
            )
        ) + int(amount)
    )

    save_group_daily_vibe(
        chat_id,
        daily["date"],
        daily
    )

    return daily["messages"]


def record_group_emoji(
    chat_id,
    emoji,
    count=1,
    date=None
):

    daily = ensure_group_daily_vibe(
        chat_id,
        date
    )

    emoji = str(emoji)

    counts = daily.get(
        "emoji_counts",
        {}
    )

    if not isinstance(
        counts,
        dict
    ):
        counts = {}

    counts[emoji] = max(
        0,
        int(
            counts.get(
                emoji,
                0
            )
        ) + int(count)
    )

    daily["emoji_counts"] = counts

    daily["emoji_total"] = max(
        0,
        int(
            daily.get(
                "emoji_total",
                0
            )
        ) + int(count)
    )

    save_group_daily_vibe(
        chat_id,
        daily["date"],
        daily
    )

    return daily


def record_group_reaction(
    chat_id,
    reaction,
    count=1,
    date=None
):

    daily = ensure_group_daily_vibe(
        chat_id,
        date
    )

    reaction = str(reaction)

    counts = daily.get(
        "reaction_counts",
        {}
    )

    if not isinstance(
        counts,
        dict
    ):
        counts = {}

    counts[reaction] = max(
        0,
        int(
            counts.get(
                reaction,
                0
            )
        ) + int(count)
    )

    daily["reaction_counts"] = counts

    daily["reaction_total"] = max(
        0,
        int(
            daily.get(
                "reaction_total",
                0
            )
        ) + int(count)
    )

    save_group_daily_vibe(
        chat_id,
        daily["date"],
        daily
    )

    return daily


def update_group_vibe_scores(
    chat_id,
    positive=0,
    low_vibe=0,
    fun=0,
    calm=0,
    energy=0,
    angry=0,
    neutral=0,
    date=None
):

    daily = ensure_group_daily_vibe(
        chat_id,
        date
    )

    score_updates = {

        "positive_score": positive,

        "low_vibe_score": low_vibe,

        "fun_score": fun,

        "calm_score": calm,

        "energy_score": energy,

        "angry_score": angry,

        "neutral_score": neutral
    }

    for key, amount in score_updates.items():

        try:
            amount = int(amount)
        except (
            TypeError,
            ValueError
        ):
            amount = 0

        daily[key] = max(
            0,
            int(
                daily.get(
                    key,
                    0
                )
            ) + amount
        )

    save_group_daily_vibe(
        chat_id,
        daily["date"],
        daily
    )

    return daily


def get_group_vibe_history(chat_id):

    vibe_data = get_group_vibe_data(
        chat_id
    )

    history = []

    for date, daily in vibe_data.items():

        if not isinstance(
            daily,
            dict
        ):
            continue

        entry = dict(daily)

        if "date" not in entry:

            entry["date"] = date

        history.append(entry)

    history.sort(
        key=lambda item: item.get(
            "date",
            ""
        )
    )

    return history


def get_group_vibe_period(
    chat_id,
    start_date,
    end_date
):

    history = get_group_vibe_history(
        chat_id
    )

    result = []

    for entry in history:

        date = entry.get(
            "date",
            ""
        )

        if start_date <= date <= end_date:

            result.append(entry)

    return result


# ============================================================
# GROUP REMINDERS
# ============================================================

def get_group_reminder(chat_id):

    settings = get_group_settings(
        chat_id
    )

    reminder = settings.get(
        "reminder",
        {}
    )

    if not isinstance(
        reminder,
        dict
    ):
        return None

    if not reminder.get(
        "enabled",
        False
    ):
        return None

    return reminder


def set_group_reminder(
    chat_id,
    hour,
    minute,
    text=""
):

    settings = get_group_settings(
        chat_id
    )

    settings["reminder"] = {

        "enabled": True,

        "hour": int(hour),

        "minute": int(minute),

        "text": text
    }

    save_group_settings(
        chat_id,
        settings
    )


def disable_group_reminder(chat_id):

    settings = get_group_settings(
        chat_id
    )

    reminder = settings.get(
        "reminder",
        {}
    )

    if isinstance(
        reminder,
        dict
    ):
        reminder["enabled"] = False

    settings["reminder"] = reminder

    save_group_settings(
        chat_id,
        settings
    )


# ============================================================
# MODERATION SETTINGS
# ============================================================

def get_moderation_settings(chat_id):

    settings = get_group_settings(
        chat_id
    )

    moderation = settings.get(
        "moderation",
        {}
    )

    if not isinstance(
        moderation,
        dict
    ):
        moderation = {}

    return moderation


def save_moderation_settings(
    chat_id,
    moderation
):

    settings = get_group_settings(
        chat_id
    )

    settings["moderation"] = moderation

    save_group_settings(
        chat_id,
        settings
    )


def set_moderation_setting(
    chat_id,
    setting,
    value
):

    moderation = get_moderation_settings(
        chat_id
    )

    moderation[setting] = value

    save_moderation_settings(
        chat_id,
        moderation
    )


# ============================================================
# WELCOME SETTINGS
# ============================================================

def get_welcome_settings(chat_id):

    settings = get_group_settings(
        chat_id
    )

    welcome = settings.get(
        "welcome",
        {}
    )

    if not isinstance(
        welcome,
        dict
    ):
        welcome = {}

    return welcome


def save_welcome_settings(
    chat_id,
    welcome
):

    settings = get_group_settings(
        chat_id
    )

    settings["welcome"] = welcome

    save_group_settings(
        chat_id,
        settings
    )


# ============================================================
# GROUP DAILY QUESTION
# ============================================================

def get_group_daily_question(chat_id):

    group = get_group_data(
        chat_id
    )

    return group.get(
        "daily_question",
        {}
    )


def save_group_daily_question(
    chat_id,
    question_data
):

    group = get_group_data(
        chat_id
    )

    group["daily_question"] = question_data

    save_group_data(
        chat_id,
        group
    )


# ============================================================
# GROUP POLLS
# ============================================================

def get_group_polls(chat_id):

    group = get_group_data(
        chat_id
    )

    polls = group.get(
        "polls",
        []
    )

    if not isinstance(
        polls,
        list
    ):
        return []

    return polls


def save_group_polls(
    chat_id,
    polls
):

    group = get_group_data(
        chat_id
    )

    group["polls"] = polls

    save_group_data(
        chat_id,
        group
    )


def add_group_poll(
    chat_id,
    poll_data
):

    polls = get_group_polls(
        chat_id
    )

    polls.append(
        poll_data
    )

    save_group_polls(
        chat_id,
        polls
    )

    return poll_data


# ============================================================
# GROUP BIRTHDAYS
# ============================================================

def get_group_birthdays(chat_id):

    group = get_group_data(
        chat_id
    )

    birthdays = group.get(
        "birthdays",
        {}
    )

    if not isinstance(
        birthdays,
        dict
    ):
        birthdays = {}

    return birthdays


def save_group_birthdays(
    chat_id,
    birthdays
):

    group = get_group_data(
        chat_id
    )

    group["birthdays"] = birthdays

    save_group_data(
        chat_id,
        group
    )


def set_group_birthday(
    chat_id,
    user_id,
    birthday
):

    birthdays = get_group_birthdays(
        chat_id
    )

    birthdays[str(user_id)] = birthday

    save_group_birthdays(
        chat_id,
        birthdays
    )


# ============================================================
# GROUP STUDY REMINDERS
# ============================================================

def get_group_study_reminders(chat_id):

    group = get_group_data(
        chat_id
    )

    reminders = group.get(
        "study_reminders",
        []
    )

    if not isinstance(
        reminders,
        list
    ):
        return []

    return reminders


def save_group_study_reminders(
    chat_id,
    reminders
):

    group = get_group_data(
        chat_id
    )

    group["study_reminders"] = reminders

    save_group_data(
        chat_id,
        group
    )


def add_group_study_reminder(
    chat_id,
    reminder
):

    reminders = get_group_study_reminders(
        chat_id
    )

    reminders.append(
        reminder
    )

    save_group_study_reminders(
        chat_id,
        reminders
    )

    return reminder


# ============================================================
# GROUP ANNOUNCEMENTS
# ============================================================

def get_group_announcements(chat_id):

    group = get_group_data(
        chat_id
    )

    announcements = group.get(
        "announcements",
        []
    )

    if not isinstance(
        announcements,
        list
    ):
        return []

    return announcements


def add_group_announcement(
    chat_id,
    announcement
):

    announcements = get_group_announcements(
        chat_id
    )

    announcements.append(
        announcement
    )

    group = get_group_data(
        chat_id
    )

    group["announcements"] = announcements

    save_group_data(
        chat_id,
        group
    )

    return announcement


# ============================================================
# DATABASE RESET / GROUP RESET
# ============================================================

def clear_group_data(chat_id):

    data = load_data()

    data.pop(
        f"group_{chat_id}",
        None
    )

    save_data(data)


def clear_all_data():

    save_data({})
    # ============================================================
# GROUP MEMBERS LIST (for /all mention)
# ============================================================

def get_group_members_list(chat_id):
    """
    Returns list of group members for mention-all.
    Format: [{"user_id": str, "first_name": str, "username": str}, ...]
    """
    members = get_group_members(chat_id)

    if not isinstance(members, dict):
        return []

    result = []
    for user_id, info in members.items():
        if not isinstance(info, dict):
            continue

        result.append({
            "user_id": str(user_id),
            "first_name": info.get("first_name", "User"),
            "username": info.get("username", ""),
        })

    return result