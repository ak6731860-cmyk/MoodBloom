# ============================================================
# MOODBLOOM 4.0 — BIRTHDAYS SYSTEM
# ============================================================

from datetime import datetime, date
from calendar import monthrange
from typing import Optional, List, Dict, Any

import config
import v4_data


# ============================================================
# CONSTANTS
# ============================================================

MAX_UPCOMING_RESULTS = 50
MAX_BIRTHDAY_RESULTS = 100
MAX_BIRTHDAY_HISTORY = 100

DATE_FORMAT = "%Y-%m-%d"

DEFAULT_BIRTHDAY_SETTINGS = {
    "enabled": True,
    "public": True,
    "reminder_enabled": True,
    "wish_enabled": True,
    "reminder_days_before": 1,
}


# ============================================================
# TIME HELPERS
# ============================================================

def _now() -> datetime:
    try:
        return datetime.now(config.TIMEZONE)
    except Exception:
        return datetime.now()


def today_key() -> str:
    return _now().strftime(DATE_FORMAT)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
            "on",
        }

    if isinstance(value, (int, float)):
        return bool(value)

    return default


# ============================================================
# DATE HELPERS
# ============================================================

def validate_birthday_date(month: int, day: int) -> bool:
    month = _safe_int(month, 0)
    day = _safe_int(day, 0)

    if month < 1 or month > 12:
        return False

    try:
        return 1 <= day <= monthrange(2024, month)[1]
    except Exception:
        return False


def parse_birthday(value: str) -> Optional[Dict[str, Any]]:
    """
    Supported:
        DD-MM
        DD/MM
        DD.MM
        YYYY-MM-DD
        YYYY/MM/DD
        YYYY.MM.DD
        DD-MM-YYYY
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    cleaned = value

    for separator in ["/", "."]:
        cleaned = cleaned.replace(separator, "-")

    parts = cleaned.split("-")

    try:
        if len(parts) == 2:
            day = int(parts[0])
            month = int(parts[1])
            year = None

        elif len(parts) == 3:
            if len(parts[0]) == 4:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
            else:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])

        else:
            return None

    except Exception:
        return None

    if not validate_birthday_date(month, day):
        return None

    if year is not None:
        current_year = _now().year

        if year < 1900 or year > current_year:
            return None

    return {
        "day": day,
        "month": month,
        "year": year,
    }


def format_birthday(
    month: int,
    day: int,
    year: Optional[int] = None,
) -> str:
    if year:
        return f"{day:02d}-{month:02d}-{year}"

    return f"{day:02d}-{month:02d}"


def birthday_date_for_year(
    month: int,
    day: int,
    year: Optional[int] = None,
) -> date:
    target_year = year or _now().year

    try:
        return date(target_year, month, day)
    except ValueError:
        if month == 2 and day == 29:
            return date(target_year, 2, 28)

        raise


def days_until_birthday(
    month: int,
    day: int,
    from_date: Optional[date] = None,
) -> int:
    current = from_date or _now().date()

    birthday = birthday_date_for_year(
        month,
        day,
        current.year,
    )

    if birthday < current:
        birthday = birthday_date_for_year(
            month,
            day,
            current.year + 1,
        )

    return (birthday - current).days


def age_from_birth_year(
    birth_year: Optional[int],
    birthday_month: int,
    birthday_day: int,
    current_date: Optional[date] = None,
) -> Optional[int]:
    if not birth_year:
        return None

    current = current_date or _now().date()

    age = current.year - int(birth_year)

    birthday_this_year = birthday_date_for_year(
        birthday_month,
        birthday_day,
        current.year,
    )

    if current < birthday_this_year:
        age -= 1

    return max(0, age)


# ============================================================
# STORAGE HELPERS
# ============================================================

def _birthday_defaults() -> Dict[str, Any]:
    now = _now().isoformat()

    return {
        "month": None,
        "day": None,
        "year": None,
        "name": "",
        "username": "",
        "first_name": "",
        "added_at": now,
        "updated_at": now,
        "enabled": True,
        "public": True,
        "reminder_enabled": True,
        "wish_enabled": True,
        "reminder_days_before": 1,
        "last_reminder_date": None,
        "last_wish_date": None,
        "history": [],
    }


def _normalize_record(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(record, dict):
        record = {}

    result = _birthday_defaults()
    result.update(record)

    if result.get("month") is not None:
        result["month"] = _safe_int(
            result["month"],
            0,
        )

    if result.get("day") is not None:
        result["day"] = _safe_int(
            result["day"],
            0,
        )

    if result.get("year") is not None:
        result["year"] = _safe_int(
            result["year"],
            0,
        )

    result["name"] = str(
        result.get("name") or ""
    ).strip()

    result["username"] = str(
        result.get("username") or ""
    ).strip()

    result["first_name"] = str(
        result.get("first_name") or ""
    ).strip()

    result["enabled"] = _safe_bool(
        result.get("enabled"),
        True,
    )

    result["public"] = _safe_bool(
        result.get("public"),
        True,
    )

    result["reminder_enabled"] = _safe_bool(
        result.get("reminder_enabled"),
        True,
    )

    result["wish_enabled"] = _safe_bool(
        result.get("wish_enabled"),
        True,
    )

    result["reminder_days_before"] = max(
        0,
        min(
            30,
            _safe_int(
                result.get("reminder_days_before"),
                1,
            ),
        ),
    )

    if not isinstance(
        result.get("history"),
        list,
    ):
        result["history"] = []

    result["history"] = result["history"][
        -MAX_BIRTHDAY_HISTORY:
    ]

    return result


def _load_birthdays_data() -> Dict[str, Any]:
    data = v4_data.load_v4_data()

    if not isinstance(data, dict):
        data = {}

    data.setdefault(
        "birthdays",
        {},
    )

    if not isinstance(
        data["birthdays"],
        dict,
    ):
        data["birthdays"] = {}

    return data


def _save_birthdays_data(
    data: Dict[str, Any],
) -> bool:
    try:
        return bool(
            v4_data.save_v4_data(data)
        )
    except Exception:
        return False


# ============================================================
# USER BIRTHDAY
# ============================================================

def set_birthday(
    user_id: Any,
    birthday: str,
    name: str = "",
    username: str = "",
    first_name: str = "",
    public: bool = True,
    reminder_enabled: bool = True,
    wish_enabled: bool = True,
    reminder_days_before: int = 1,
) -> Dict[str, Any]:

    parsed = parse_birthday(birthday)

    if not parsed:
        return {
            "success": False,
            "error": "invalid_date",
            "message": (
                "Invalid birthday. Use DD-MM, "
                "DD/MM or YYYY-MM-DD format."
            ),
        }

    user_id = str(user_id)

    data = _load_birthdays_data()

    storage = data["birthdays"].setdefault(
        user_id,
        {},
    )

    existing = storage.get("birthday")
    now = _now().isoformat()

    record = _normalize_record(
        existing or {}
    )

    if not existing:
        record["added_at"] = now

    record["updated_at"] = now
    record["month"] = parsed["month"]
    record["day"] = parsed["day"]
    record["year"] = parsed.get("year")

    if name:
        record["name"] = str(name).strip()

    if username:
        record["username"] = str(
            username
        ).strip()

    if first_name:
        record["first_name"] = str(
            first_name
        ).strip()

    record["public"] = bool(public)
    record["enabled"] = True
    record["reminder_enabled"] = bool(
        reminder_enabled
    )
    record["wish_enabled"] = bool(
        wish_enabled
    )

    record["reminder_days_before"] = max(
        0,
        min(
            30,
            _safe_int(
                reminder_days_before,
                1,
            ),
        ),
    )

    storage["birthday"] = record
    storage["updated_at"] = now

    if _save_birthdays_data(data):
        return {
            "success": True,
            "created": existing is None,
            "updated": existing is not None,
            "birthday": record,
            "formatted": format_birthday(
                record["month"],
                record["day"],
                record.get("year"),
            ),
        }

    return {
        "success": False,
        "error": "save_failed",
        "message": "Could not save birthday.",
    }


def add_birthday(
    user_id: Any,
    birthday: str,
    name: str = "",
    username: str = "",
    first_name: str = "",
    **kwargs,
) -> Dict[str, Any]:
    return set_birthday(
        user_id=user_id,
        birthday=birthday,
        name=name,
        username=username,
        first_name=first_name,
        **kwargs,
    )


def update_birthday(
    user_id: Any,
    birthday: str,
    **kwargs,
) -> Dict[str, Any]:
    return set_birthday(
        user_id=user_id,
        birthday=birthday,
        **kwargs,
    )


def get_birthday(
    user_id: Any,
) -> Optional[Dict[str, Any]]:

    data = _load_birthdays_data()

    storage = data["birthdays"].get(
        str(user_id),
        {},
    )

    record = storage.get("birthday")

    if not record:
        return None

    result = _normalize_record(record)

    result["user_id"] = str(user_id)

    return result


def has_birthday(user_id: Any) -> bool:
    return get_birthday(user_id) is not None


def remove_birthday(
    user_id: Any,
) -> Dict[str, Any]:

    user_id = str(user_id)

    data = _load_birthdays_data()

    storage = data["birthdays"].get(
        user_id
    )

    if not storage or not storage.get(
        "birthday"
    ):
        return {
            "success": False,
            "not_found": True,
        }

    old_record = storage.pop(
        "birthday"
    )

    storage["updated_at"] = (
        _now().isoformat()
    )

    _save_birthdays_data(data)

    return {
        "success": True,
        "not_found": False,
        "birthday": old_record,
    }


def delete_birthday(
    user_id: Any,
) -> Dict[str, Any]:
    return remove_birthday(user_id)


# ============================================================
# SETTINGS
# ============================================================

def update_birthday_settings(
    user_id: Any,
    enabled: Optional[bool] = None,
    public: Optional[bool] = None,
    reminder_enabled: Optional[bool] = None,
    wish_enabled: Optional[bool] = None,
    reminder_days_before: Optional[int] = None,
) -> Dict[str, Any]:

    user_id = str(user_id)

    data = _load_birthdays_data()

    storage = data["birthdays"].get(
        user_id
    )

    if not storage or not storage.get(
        "birthday"
    ):
        return {
            "success": False,
            "error": "birthday_not_found",
        }

    record = _normalize_record(
        storage["birthday"]
    )

    if enabled is not None:
        record["enabled"] = bool(enabled)

    if public is not None:
        record["public"] = bool(public)

    if reminder_enabled is not None:
        record["reminder_enabled"] = bool(
            reminder_enabled
        )

    if wish_enabled is not None:
        record["wish_enabled"] = bool(
            wish_enabled
        )

    if reminder_days_before is not None:
        record["reminder_days_before"] = max(
            0,
            min(
                30,
                _safe_int(
                    reminder_days_before,
                    1,
                ),
            ),
        )

    record["updated_at"] = (
        _now().isoformat()
    )

    storage["birthday"] = record

    _save_birthdays_data(data)

    return {
        "success": True,
        "birthday": record,
    }


def get_birthday_settings(
    user_id: Any,
) -> Dict[str, Any]:

    record = get_birthday(user_id)

    if not record:
        return DEFAULT_BIRTHDAY_SETTINGS.copy()

    return {
        "enabled": record.get(
            "enabled",
            True,
        ),
        "public": record.get(
            "public",
            True,
        ),
        "reminder_enabled": record.get(
            "reminder_enabled",
            True,
        ),
        "wish_enabled": record.get(
            "wish_enabled",
            True,
        ),
        "reminder_days_before": record.get(
            "reminder_days_before",
            1,
        ),
    }


# ============================================================
# DISPLAY
# ============================================================

def get_display_name(
    record: Dict[str, Any],
) -> str:

    if record.get("name"):
        return str(record["name"])

    if record.get("first_name"):
        return str(record["first_name"])

    username = str(
        record.get("username") or ""
    ).strip()

    if username:
        return f"@{username.lstrip('@')}"

    return "Bloom Friend"


def format_birthday_record(
    record: Optional[Dict[str, Any]],
    include_year: bool = False,
    include_age: bool = False,
) -> str:

    if not record:
        return "No birthday set."

    month = record.get("month")
    day = record.get("day")

    if not month or not day:
        return "No birthday set."

    year = record.get("year")

    result = format_birthday(
        month,
        day,
        year if include_year else None,
    )

    if include_age and year:
        age = age_from_birth_year(
            year,
            month,
            day,
        )

        if age is not None:
            result += f" ({age} years)"

    return result


# ============================================================
# COLLECTIONS
# ============================================================

def get_all_birthdays(
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    data = _load_birthdays_data()

    results = []

    for user_id, storage in data[
        "birthdays"
    ].items():

        # "groups" is a separate storage section.
        if user_id == "groups":
            continue

        if not isinstance(
            storage,
            dict,
        ):
            continue

        record = storage.get("birthday")

        if not record:
            continue

        record = _normalize_record(record)

        if not record.get(
            "enabled",
            True,
        ):
            continue

        if (
            not include_private
            and not record.get(
                "public",
                True,
            )
        ):
            continue

        item = record.copy()
        item["user_id"] = str(user_id)

        results.append(item)

    return results


def get_today_birthdays(
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    current = _now().date()

    results = []

    for record in get_all_birthdays(
        include_private=include_private,
    ):
        if (
            _safe_int(record.get("month"))
            == current.month
            and
            _safe_int(record.get("day"))
            == current.day
        ):
            results.append(record)

    return results[:MAX_BIRTHDAY_RESULTS]


def get_todays_birthdays(
    include_private: bool = False,
) -> List[Dict[str, Any]]:
    return get_today_birthdays(
        include_private=include_private,
    )


# ============================================================
# UPCOMING
# ============================================================

def get_upcoming_birthdays(
    days: int = 30,
    include_today: bool = True,
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    days = max(
        0,
        min(
            366,
            _safe_int(days, 30),
        ),
    )

    current = _now().date()

    results = []

    for record in get_all_birthdays(
        include_private=include_private,
    ):
        month = _safe_int(
            record.get("month"),
            0,
        )

        day = _safe_int(
            record.get("day"),
            0,
        )

        if not month or not day:
            continue

        birthday = birthday_date_for_year(
            month,
            day,
            current.year,
        )

        if birthday < current:
            birthday = birthday_date_for_year(
                month,
                day,
                current.year + 1,
            )

        delta = (
            birthday - current
        ).days

        if not include_today and delta == 0:
            continue

        if delta <= days:
            item = record.copy()
            item["days_until"] = delta
            item["birthday_date"] = (
                birthday.isoformat()
            )

            results.append(item)

    results.sort(
        key=lambda item: (
            item.get(
                "days_until",
                999999,
            ),
            str(
                item.get(
                    "name",
                    "",
                )
            ),
        )
    )

    return results[
        :MAX_UPCOMING_RESULTS
    ]


def get_next_birthday(
    include_private: bool = False,
) -> Optional[Dict[str, Any]]:

    upcoming = get_upcoming_birthdays(
        days=366,
        include_today=True,
        include_private=include_private,
    )

    return upcoming[0] if upcoming else None


# ============================================================
# SEARCH
# ============================================================

def search_birthdays(
    query: str,
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    query = str(
        query or ""
    ).strip().lower()

    if not query:
        return []

    results = []

    for record in get_all_birthdays(
        include_private=include_private,
    ):
        searchable = " ".join(
            [
                str(
                    record.get(
                        "user_id",
                        "",
                    )
                ),
                str(
                    record.get(
                        "name",
                        "",
                    )
                ),
                str(
                    record.get(
                        "username",
                        "",
                    )
                ),
                str(
                    record.get(
                        "first_name",
                        "",
                    )
                ),
            ]
        ).lower()

        if query in searchable:
            results.append(record)

    return results[
        :MAX_BIRTHDAY_RESULTS
    ]


# ============================================================
# REMINDERS
# ============================================================

def should_send_birthday_reminder(
    record: Dict[str, Any],
    current_date: Optional[date] = None,
) -> bool:

    if not record:
        return False

    if not record.get(
        "enabled",
        True,
    ):
        return False

    if not record.get(
        "reminder_enabled",
        True,
    ):
        return False

    current = (
        current_date
        or _now().date()
    )

    month = _safe_int(
        record.get("month"),
        0,
    )

    day = _safe_int(
        record.get("day"),
        0,
    )

    if not month or not day:
        return False

    reminder_days = _safe_int(
        record.get(
            "reminder_days_before",
            1,
        ),
        1,
    )

    birthday = birthday_date_for_year(
        month,
        day,
        current.year,
    )

    if birthday < current:
        birthday = birthday_date_for_year(
            month,
            day,
            current.year + 1,
        )

    if (
        birthday - current
    ).days != reminder_days:
        return False

    return (
        record.get(
            "last_reminder_date"
        )
        != current.isoformat()
    )


def mark_reminder_sent(
    user_id: Any,
) -> bool:

    user_id = str(user_id)

    data = _load_birthdays_data()

    storage = data["birthdays"].get(
        user_id
    )

    if not storage or not storage.get(
        "birthday"
    ):
        return False

    record = _normalize_record(
        storage["birthday"]
    )

    current = today_key()

    record["last_reminder_date"] = current

    history = record.setdefault(
        "history",
        [],
    )

    history.append(
        {
            "type": "reminder",
            "date": current,
        }
    )

    record["history"] = history[
        -MAX_BIRTHDAY_HISTORY:
    ]

    storage["birthday"] = record

    return _save_birthdays_data(data)


def get_birthday_reminders_due(
    current_date: Optional[date] = None,
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    current = (
        current_date
        or _now().date()
    )

    results = []

    for record in get_all_birthdays(
        include_private=include_private,
    ):
        if should_send_birthday_reminder(
            record,
            current,
        ):
            results.append(record)

    return results[
        :MAX_BIRTHDAY_RESULTS
    ]


# ============================================================
# BIRTHDAY WISHES
# ============================================================

BIRTHDAY_WISHES = [
    (
        "🎂 Happy Birthday, {name}! "
        "May your day be filled with happiness, "
        "smiles and beautiful moments. 🌸"
    ),
    (
        "🌷 Wishing you a very Happy Birthday, "
        "{name}! Keep blooming and shining. ✨"
    ),
    (
        "🎉 Happy Birthday, {name}! "
        "May this new year of your life bring "
        "lots of wonderful moments. 💖"
    ),
    (
        "🌸 Another year, another beautiful bloom! "
        "Happy Birthday, {name}! 🎂✨"
    ),
    (
        "💫 Happy Birthday, {name}! "
        "May your journey ahead be full of "
        "joy, growth and bright moments. 🌺"
    ),
]


def generate_birthday_wish(
    record: Dict[str, Any],
) -> str:

    import random

    name = get_display_name(record)

    return random.choice(
        BIRTHDAY_WISHES
    ).format(
        name=name
    )


def get_today_birthday_wishes(
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    results = []

    for record in get_today_birthdays(
        include_private=include_private,
    ):
        item = record.copy()

        if record.get(
            "wish_enabled",
            True,
        ):
            item["wish"] = (
                generate_birthday_wish(
                    record
                )
            )

        results.append(item)

    return results[
        :MAX_BIRTHDAY_RESULTS
    ]


def should_send_birthday_wish(
    record: Dict[str, Any],
    current_date: Optional[date] = None,
) -> bool:

    if not record:
        return False

    if not record.get(
        "enabled",
        True,
    ):
        return False

    if not record.get(
        "wish_enabled",
        True,
    ):
        return False

    current = (
        current_date
        or _now().date()
    )

    month = _safe_int(
        record.get("month"),
        0,
    )

    day = _safe_int(
        record.get("day"),
        0,
    )

    if not month or not day:
        return False

    if (
        month != current.month
        or day != current.day
    ):
        return False

    return (
        record.get(
            "last_wish_date"
        )
        != current.isoformat()
    )


def mark_wish_sent(
    user_id: Any,
) -> bool:

    user_id = str(user_id)

    data = _load_birthdays_data()

    storage = data["birthdays"].get(
        user_id
    )

    if not storage or not storage.get(
        "birthday"
    ):
        return False

    record = _normalize_record(
        storage["birthday"]
    )

    current = today_key()

    record["last_wish_date"] = current

    history = record.setdefault(
        "history",
        [],
    )

    history.append(
        {
            "type": "wish",
            "date": current,
        }
    )

    record["history"] = history[
        -MAX_BIRTHDAY_HISTORY:
    ]

    storage["birthday"] = record

    return _save_birthdays_data(data)


# ============================================================
# GROUP BIRTHDAYS
# ============================================================

def set_group_birthday(
    chat_id: Any,
    user_id: Any,
    birthday: str,
    name: str = "",
    username: str = "",
    first_name: str = "",
    public: bool = True,
) -> Dict[str, Any]:

    parsed = parse_birthday(birthday)

    if not parsed:
        return {
            "success": False,
            "error": "invalid_date",
        }

    data = _load_birthdays_data()

    group_id = str(chat_id)
    user_id = str(user_id)

    groups = data["birthdays"].setdefault(
        "groups",
        {},
    )

    group = groups.setdefault(
        group_id,
        {},
    )

    members = group.setdefault(
        "members",
        {},
    )

    now = _now().isoformat()

    existing = members.get(user_id)

    record = _normalize_record(
        existing or {}
    )

    record["month"] = parsed["month"]
    record["day"] = parsed["day"]
    record["year"] = parsed.get("year")

    if name:
        record["name"] = str(
            name
        ).strip()

    if username:
        record["username"] = str(
            username
        ).strip()

    if first_name:
        record["first_name"] = str(
            first_name
        ).strip()

    record["public"] = bool(public)
    record["enabled"] = True
    record["updated_at"] = now

    if not existing:
        record["added_at"] = now

    members[user_id] = record
    group["updated_at"] = now

    _save_birthdays_data(data)

    return {
        "success": True,
        "created": existing is None,
        "updated": existing is not None,
        "birthday": record,
        "chat_id": group_id,
        "user_id": user_id,
    }


def get_group_birthday(
    chat_id: Any,
    user_id: Any,
) -> Optional[Dict[str, Any]]:

    data = _load_birthdays_data()

    group = data["birthdays"].get(
        "groups",
        {},
    ).get(
        str(chat_id),
        {},
    )

    record = group.get(
        "members",
        {},
    ).get(
        str(user_id)
    )

    if not record:
        return None

    result = _normalize_record(record)

    result["chat_id"] = str(chat_id)
    result["user_id"] = str(user_id)

    return result


def remove_group_birthday(
    chat_id: Any,
    user_id: Any,
) -> Dict[str, Any]:

    data = _load_birthdays_data()

    groups = data["birthdays"].get(
        "groups",
        {},
    )

    group = groups.get(
        str(chat_id)
    )

    if not group:
        return {
            "success": False,
            "not_found": True,
        }

    members = group.get(
        "members",
        {},
    )

    user_id = str(user_id)

    if user_id not in members:
        return {
            "success": False,
            "not_found": True,
        }

    old = members.pop(user_id)

    group["updated_at"] = (
        _now().isoformat()
    )

    _save_birthdays_data(data)

    return {
        "success": True,
        "not_found": False,
        "birthday": old,
    }


def get_group_birthdays(
    chat_id: Any,
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    data = _load_birthdays_data()

    group = data["birthdays"].get(
        "groups",
        {},
    ).get(
        str(chat_id),
        {},
    )

    members = group.get(
        "members",
        {},
    )

    results = []

    for user_id, record in members.items():

        record = _normalize_record(record)

        if not record.get(
            "enabled",
            True,
        ):
            continue

        if (
            not include_private
            and not record.get(
                "public",
                True,
            )
        ):
            continue

        record["user_id"] = str(user_id)
        record["chat_id"] = str(chat_id)

        results.append(record)

    return results[
        :MAX_BIRTHDAY_RESULTS
    ]


def get_group_today_birthdays(
    chat_id: Any,
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    current = _now().date()

    results = []

    for record in get_group_birthdays(
        chat_id,
        include_private=include_private,
    ):
        if (
            _safe_int(record.get("month"))
            == current.month
            and
            _safe_int(record.get("day"))
            == current.day
        ):
            results.append(record)

    return results[
        :MAX_BIRTHDAY_RESULTS
    ]


def get_group_upcoming_birthdays(
    chat_id: Any,
    days: int = 30,
    include_private: bool = False,
) -> List[Dict[str, Any]]:

    current = _now().date()

    days = max(
        0,
        min(
            366,
            _safe_int(days, 30),
        ),
    )

    results = []

    for record in get_group_birthdays(
        chat_id,
        include_private=include_private,
    ):
        month = _safe_int(
            record.get("month"),
            0,
        )

        day = _safe_int(
            record.get("day"),
            0,
        )

        if not month or not day:
            continue

        birthday = birthday_date_for_year(
            month,
            day,
            current.year,
        )

        if birthday < current:
            birthday = birthday_date_for_year(
                month,
                day,
                current.year + 1,
            )

        delta = (
            birthday - current
        ).days

        if delta <= days:
            item = record.copy()
            item["days_until"] = delta
            item["birthday_date"] = (
                birthday.isoformat()
            )

            results.append(item)

    results.sort(
        key=lambda item: (
            item.get(
                "days_until",
                999999,
            ),
            str(
                item.get(
                    "name",
                    "",
                )
            ),
        )
    )

    return results[
        :MAX_UPCOMING_RESULTS
    ]


# ============================================================
# STATISTICS
# ============================================================

def get_birthday_stats() -> Dict[str, Any]:

    all_birthdays = get_all_birthdays(
        include_private=True,
    )

    today_birthdays = get_today_birthdays(
        include_private=True,
    )

    upcoming = get_upcoming_birthdays(
        days=30,
        include_private=True,
    )

    month_counts = {
        month: 0
        for month in range(1, 13)
    }

    for record in all_birthdays:
        month = _safe_int(
            record.get("month"),
            0,
        )

        if month in month_counts:
            month_counts[month] += 1

    return {
        "total": len(all_birthdays),
        "today": len(today_birthdays),
        "upcoming_30_days": len(upcoming),
        "month_counts": month_counts,
        "generated_at": _now().isoformat(),
    }


def get_group_birthday_stats(
    chat_id: Any,
) -> Dict[str, Any]:

    birthdays = get_group_birthdays(
        chat_id,
        include_private=True,
    )

    today = get_group_today_birthdays(
        chat_id,
        include_private=True,
    )

    upcoming = get_group_upcoming_birthdays(
        chat_id,
        days=30,
        include_private=True,
    )

    return {
        "chat_id": str(chat_id),
        "total": len(birthdays),
        "today": len(today),
        "upcoming_30_days": len(upcoming),
        "generated_at": _now().isoformat(),
    }


# ============================================================
# HISTORY
# ============================================================

def get_birthday_history(
    user_id: Any,
) -> List[Dict[str, Any]]:

    record = get_birthday(user_id)

    if not record:
        return []

    history = record.get(
        "history",
        [],
    )

    if not isinstance(history, list):
        return []

    return history[
        -MAX_BIRTHDAY_HISTORY:
    ]


# ============================================================
# RESET / CLEANUP
# ============================================================

def reset_birthday_notifications(
    user_id: Any,
) -> bool:

    user_id = str(user_id)

    data = _load_birthdays_data()

    storage = data["birthdays"].get(
        user_id
    )

    if not storage or not storage.get(
        "birthday"
    ):
        return False

    record = _normalize_record(
        storage["birthday"]
    )

    record["last_reminder_date"] = None
    record["last_wish_date"] = None

    storage["birthday"] = record

    return _save_birthdays_data(data)


def cleanup_birthday_history() -> int:

    data = _load_birthdays_data()

    changed = 0

    for user_id, storage in data[
        "birthdays"
    ].items():

        if user_id == "groups":
            continue

        if not isinstance(
            storage,
            dict,
        ):
            continue

        record = storage.get("birthday")

        if not isinstance(
            record,
            dict,
        ):
            continue

        history = record.get(
            "history"
        )

        if not isinstance(
            history,
            list,
        ):
            record["history"] = []
            changed += 1
            continue

        if len(history) > MAX_BIRTHDAY_HISTORY:
            record["history"] = history[
                -MAX_BIRTHDAY_HISTORY:
            ]
            changed += 1

    if changed:
        _save_birthdays_data(data)

    return changed


# ============================================================
# MESSAGE HELPERS
# ============================================================

def birthday_summary(
    user_id: Any,
) -> str:

    record = get_birthday(user_id)

    if not record:
        return "🎂 Birthday: Not set"

    name = get_display_name(record)

    birthday_text = format_birthday_record(
        record,
        include_year=False,
    )

    days = days_until_birthday(
        record["month"],
        record["day"],
    )

    if days == 0:
        status = "🎉 Today!"
    elif days == 1:
        status = "🌸 Tomorrow!"
    else:
        status = f"⏳ {days} days left"

    return (
        f"🎂 {name}\n"
        f"📅 {birthday_text}\n"
        f"{status}"
    )


def format_birthday_list(
    birthdays: List[Dict[str, Any]],
    title: str = "🎂 Birthdays",
) -> str:

    if not birthdays:
        return (
            f"{title}\n\n"
            "🌸 No birthdays found."
        )

    lines = [
        title,
        "",
    ]

    for index, record in enumerate(
        birthdays[
            :MAX_BIRTHDAY_RESULTS
        ],
        start=1,
    ):
        name = get_display_name(record)

        birthday_text = format_birthday(
            _safe_int(
                record.get("month")
            ),
            _safe_int(
                record.get("day")
            ),
        )

        days = record.get(
            "days_until"
        )

        if days is None:
            days = days_until_birthday(
                _safe_int(
                    record.get("month")
                ),
                _safe_int(
                    record.get("day")
                ),
            )

        if days == 0:
            status = "🎉 Today"
        elif days == 1:
            status = "🌸 Tomorrow"
        else:
            status = f"⏳ {days}d"

        lines.append(
            f"{index}. 🎂 {name} — "
            f"{birthday_text} ({status})"
        )

    return "\n".join(lines)


# ============================================================
# STORAGE INITIALIZATION
# ============================================================

def ensure_birthdays_storage() -> bool:

    try:
        data = _load_birthdays_data()

        if "birthdays" not in data:
            data["birthdays"] = {}

        if not isinstance(
            data["birthdays"],
            dict,
        ):
            data["birthdays"] = {}

        return _save_birthdays_data(data)

    except Exception:
        return False


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "today_key",
    "validate_birthday_date",
    "parse_birthday",
    "format_birthday",
    "birthday_date_for_year",
    "days_until_birthday",
    "age_from_birth_year",

    "set_birthday",
    "add_birthday",
    "update_birthday",
    "get_birthday",
    "has_birthday",
    "remove_birthday",
    "delete_birthday",

    "update_birthday_settings",
    "get_birthday_settings",

    "get_display_name",
    "format_birthday_record",

    "get_all_birthdays",
    "get_today_birthdays",
    "get_todays_birthdays",
    "get_upcoming_birthdays",
    "get_next_birthday",
    "search_birthdays",

    "should_send_birthday_reminder",
    "mark_reminder_sent",
    "get_birthday_reminders_due",

    "generate_birthday_wish",
    "get_today_birthday_wishes",
    "should_send_birthday_wish",
    "mark_wish_sent",

    "set_group_birthday",
    "get_group_birthday",
    "remove_group_birthday",
    "get_group_birthdays",
    "get_group_today_birthdays",
    "get_group_upcoming_birthdays",

    "get_birthday_stats",
    "get_group_birthday_stats",

    "get_birthday_history",

    "reset_birthday_notifications",
    "cleanup_birthday_history",

    "birthday_summary",
    "format_birthday_list",

    "ensure_birthdays_storage",
]


# ============================================================
# INITIALIZE
# ============================================================

try:
    ensure_birthdays_storage()
except Exception:
    pass

