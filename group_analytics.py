# ============================================================
# MOODBLOOM 4.0 — GROUP ANALYTICS SYSTEM
# ============================================================
#
# Features:
#   • Group message tracking
#   • Member activity tracking
#   • Daily / weekly / monthly analytics
#   • Hourly activity analytics
#   • Weekday activity analytics
#   • Top active members
#   • Member statistics
#   • Group statistics
#   • Activity percentage
#   • Peak hour detection
#   • Peak day detection
#   • Message milestones
#   • Group XP support
#   • Analytics summaries
#   • Safe data migration
#   • Backward compatibility
#
# ============================================================

from datetime import datetime

import config
import v4_data


# ============================================================
# CONSTANTS
# ============================================================

MAX_MEMBER_RESULTS = 100

MESSAGE_MILESTONES = [
    10,
    25,
    50,
    100,
    250,
    500,
    1000,
    2500,
    5000,
    10000,
    25000,
    50000,
    100000,
]


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


def current_hour():
    """Return current hour from 0-23."""

    return _now().hour


def current_weekday():
    """
    Return current weekday name.
    """

    return _now().strftime(
        "%A"
    )


def month_key():
    """Return current month as YYYY-MM."""

    return _now().strftime(
        "%Y-%m"
    )


def week_key():
    """Return current ISO-like week key."""

    return _now().strftime(
        "%Y-W%W"
    )


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_int(
    value,
    default=0
):
    """Safely convert value to int."""

    try:
        return int(
            value
        )

    except Exception:
        return default


def _safe_float(
    value,
    default=0.0
):
    """Safely convert value to float."""

    try:
        return float(
            value
        )

    except Exception:
        return default


def _safe_string(
    value
):
    """Safely convert value to string."""

    try:
        return str(
            value
        ).strip()

    except Exception:
        return ""


# ============================================================
# GROUP INITIALIZATION
# ============================================================

def _initialize_group(
    data,
    chat_id,
    title=None,
    chat_type=None
):
    """
    Make sure group data exists with all required fields.
    """

    chat_id = str(
        chat_id
    )

    groups = data.setdefault(
        "groups",
        {}
    )

    group = groups.setdefault(
        chat_id,
        {}
    )

    if not isinstance(
        group,
        dict
    ):
        group = {}
        groups[chat_id] = group

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    group.setdefault(
        "id",
        chat_id
    )

    if title:
        group["title"] = (
            _safe_string(title)
        )

    if chat_type:
        group["type"] = (
            _safe_string(chat_type)
        )

    # --------------------------------------------------------
    # Message counters
    # --------------------------------------------------------

    group.setdefault(
        "total_messages",
        0
    )

    group.setdefault(
        "daily",
        {}
    )

    group.setdefault(
        "weekly",
        {}
    )

    group.setdefault(
        "monthly",
        {}
    )

    group.setdefault(
        "hourly",
        {}
    )

    group.setdefault(
        "weekday",
        {}
    )

    # --------------------------------------------------------
    # Members
    # --------------------------------------------------------

    group.setdefault(
        "members",
        {}
    )

    # --------------------------------------------------------
    # Analytics
    # --------------------------------------------------------

    group.setdefault(
        "analytics",
        {}
    )

    # --------------------------------------------------------
    # Quiz
    # --------------------------------------------------------

    group.setdefault(
        "quiz",
        {}
    )

    # --------------------------------------------------------
    # Mood
    # --------------------------------------------------------

    group.setdefault(
        "mood",
        {}
    )

    # --------------------------------------------------------
    # Settings
    # --------------------------------------------------------

    group.setdefault(
        "settings",
        {}
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    group.setdefault(
        "created_at",
        _now().isoformat()
    )

    group["updated_at"] = (
        _now().isoformat()
    )

    return group


# ============================================================
# MEMBER INITIALIZATION
# ============================================================

def _initialize_member(
    group,
    user_id,
    username=None,
    first_name=None
):
    """
    Make sure member analytics data exists.
    """

    user_id = str(
        user_id
    )

    members = group.setdefault(
        "members",
        {}
    )

    member = members.setdefault(
        user_id,
        {}
    )

    if not isinstance(
        member,
        dict
    ):
        member = {}
        members[user_id] = member

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    member.setdefault(
        "id",
        user_id
    )

    if username is not None:
        member["username"] = (
            _safe_string(username)
        )

    if first_name is not None:
        member["first_name"] = (
            _safe_string(first_name)
        )

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    member.setdefault(
        "messages",
        0
    )

    member.setdefault(
        "daily",
        {}
    )

    member.setdefault(
        "weekly",
        {}
    )

    member.setdefault(
        "monthly",
        {}
    )

    member.setdefault(
        "hourly",
        {}
    )

    member.setdefault(
        "weekday",
        {}
    )

    member.setdefault(
        "quiz_correct",
        0
    )

    member.setdefault(
        "quiz_attempts",
        0
    )

    member.setdefault(
        "mood_checkins",
        0
    )

    member.setdefault(
        "points",
        0
    )

    member.setdefault(
        "xp",
        0
    )

    member.setdefault(
        "active_days",
        []
    )

    # --------------------------------------------------------
    # Activity timestamps
    # --------------------------------------------------------

    member.setdefault(
        "first_seen",
        _now().isoformat()
    )

    member["last_seen"] = (
        _now().isoformat()
    )

    return member


# ============================================================
# RECORD GROUP MESSAGE
# ============================================================

def record_message(
    chat_id,
    user_id,
    username=None,
    first_name=None,
    title=None,
    chat_type=None
):
    """
    Record one message from a group member.

    This is the main function that bot.py should call
    whenever a group message is received.
    """

    chat_id = str(
        chat_id
    )

    user_id = str(
        user_id
    )

    data = v4_data.load_v4_data()

    group = _initialize_group(
        data,
        chat_id,
        title=title,
        chat_type=chat_type
    )

    member = _initialize_member(
        group,
        user_id,
        username=username,
        first_name=first_name
    )

    now = _now()

    date = now.strftime(
        "%Y-%m-%d"
    )

    hour = str(
        now.hour
    )

    weekday = now.strftime(
        "%A"
    )

    week = now.strftime(
        "%Y-W%W"
    )

    month = now.strftime(
        "%Y-%m"
    )

    # ========================================================
    # GROUP TOTAL
    # ========================================================

    group["total_messages"] = (
        _safe_int(
            group.get(
                "total_messages",
                0
            )
        )
        + 1
    )

    # ========================================================
    # GROUP DAILY
    # ========================================================

    daily = group.setdefault(
        "daily",
        {}
    )

    daily[date] = (
        _safe_int(
            daily.get(
                date,
                0
            )
        )
        + 1
    )

    # ========================================================
    # GROUP WEEKLY
    # ========================================================

    weekly = group.setdefault(
        "weekly",
        {}
    )

    weekly[week] = (
        _safe_int(
            weekly.get(
                week,
                0
            )
        )
        + 1
    )

    # ========================================================
    # GROUP MONTHLY
    # ========================================================

    monthly = group.setdefault(
        "monthly",
        {}
    )

    monthly[month] = (
        _safe_int(
            monthly.get(
                month,
                0
            )
        )
        + 1
    )

    # ========================================================
    # HOURLY
    # ========================================================

    hourly = group.setdefault(
        "hourly",
        {}
    )

    hourly[hour] = (
        _safe_int(
            hourly.get(
                hour,
                0
            )
        )
        + 1
    )

    # ========================================================
    # WEEKDAY
    # ========================================================

    weekday_data = group.setdefault(
        "weekday",
        {}
    )

    weekday_data[weekday] = (
        _safe_int(
            weekday_data.get(
                weekday,
                0
            )
        )
        + 1
    )

    # ========================================================
    # MEMBER TOTAL
    # ========================================================

    member["messages"] = (
        _safe_int(
            member.get(
                "messages",
                0
            )
        )
        + 1
    )

    # ========================================================
    # MEMBER DAILY
    # ========================================================

    member_daily = member.setdefault(
        "daily",
        {}
    )

    member_daily[date] = (
        _safe_int(
            member_daily.get(
                date,
                0
            )
        )
        + 1
    )

    # ========================================================
    # MEMBER WEEKLY
    # ========================================================

    member_weekly = member.setdefault(
        "weekly",
        {}
    )

    member_weekly[week] = (
        _safe_int(
            member_weekly.get(
                week,
                0
            )
        )
        + 1
    )

    # ========================================================
    # MEMBER MONTHLY
    # ========================================================

    member_monthly = member.setdefault(
        "monthly",
        {}
    )

    member_monthly[month] = (
        _safe_int(
            member_monthly.get(
                month,
                0
            )
        )
        + 1
    )

    # ========================================================
    # MEMBER HOURLY
    # ========================================================

    member_hourly = member.setdefault(
        "hourly",
        {}
    )

    member_hourly[hour] = (
        _safe_int(
            member_hourly.get(
                hour,
                0
            )
        )
        + 1
    )

    # ========================================================
    # MEMBER WEEKDAY
    # ========================================================

    member_weekday = member.setdefault(
        "weekday",
        {}
    )

    member_weekday[weekday] = (
        _safe_int(
            member_weekday.get(
                weekday,
                0
            )
        )
        + 1
    )

    # ========================================================
    # ACTIVE DAYS
    # ========================================================

    active_days = member.setdefault(
        "active_days",
        []
    )

    if not isinstance(
        active_days,
        list
    ):
        active_days = []
        member["active_days"] = active_days

    if date not in active_days:

        active_days.append(
            date
        )

        # Keep recent active-day history manageable.
        if len(
            active_days
        ) > 366:

            del active_days[
                :-366
            ]

    # ========================================================
    # LAST SEEN
    # ========================================================

    member["last_seen"] = (
        now.isoformat()
    )

    group["updated_at"] = (
        now.isoformat()
    )

    # ========================================================
    # ANALYTICS METADATA
    # ========================================================

    analytics = group.setdefault(
        "analytics",
        {}
    )

    analytics["last_message_at"] = (
        now.isoformat()
    )

    analytics["last_active_user"] = (
        user_id
    )

    # ========================================================
    # SAVE
    # ========================================================

    v4_data.save_v4_data(
        data
    )

    return {
        "success": True,
        "chat_id": chat_id,
        "user_id": user_id,
        "total_messages": group[
            "total_messages"
        ],
        "member_messages": member[
            "messages"
        ],
        "date": date,
        "hour": now.hour,
        "weekday": weekday,
    }


# ============================================================
# ALIAS FOR EXISTING V4 DATA FUNCTION
# ============================================================

def record_group_message(
    chat_id,
    user_id,
    username=None,
    first_name=None,
    title=None,
    chat_type=None
):
    """
    Compatibility wrapper around record_message().
    """

    return record_message(
        chat_id=chat_id,
        user_id=user_id,
        username=username,
        first_name=first_name,
        title=title,
        chat_type=chat_type,
    )


# ============================================================
# GET GROUP
# ============================================================

def get_group(
    chat_id
):
    """
    Return complete group analytics data.
    """

    data = v4_data.load_v4_data()

    chat_id = str(
        chat_id
    )

    group = _initialize_group(
        data,
        chat_id
    )

    v4_data.save_v4_data(
        data
    )

    return group


# ============================================================
# GET MEMBER
# ============================================================

def get_member(
    chat_id,
    user_id
):
    """
    Return one member's analytics.
    """

    data = v4_data.load_v4_data()

    chat_id = str(
        chat_id
    )

    user_id = str(
        user_id
    )

    group = _initialize_group(
        data,
        chat_id
    )

    member = _initialize_member(
        group,
        user_id
    )

    v4_data.save_v4_data(
        data
    )

    return member


# ============================================================
# MEMBER STATISTICS
# ============================================================

def get_member_stats(
    chat_id,
    user_id
):
    """
    Return useful statistics for one member.
    """

    member = get_member(
        chat_id,
        user_id
    )

    active_days = member.get(
        "active_days",
        []
    )

    if not isinstance(
        active_days,
        list
    ):
        active_days = []

    return {
        "user_id": str(
            user_id
        ),
        "username": member.get(
            "username"
        ),
        "first_name": member.get(
            "first_name"
        ),
        "messages": _safe_int(
            member.get(
                "messages",
                0
            )
        ),
        "today_messages": _safe_int(
            member.get(
                "daily",
                {}
            ).get(
                today_key(),
                0
            )
        ),
        "this_week_messages": _safe_int(
            member.get(
                "weekly",
                {}
            ).get(
                week_key(),
                0
            )
        ),
        "this_month_messages": _safe_int(
            member.get(
                "monthly",
                {}
            ).get(
                month_key(),
                0
            )
        ),
        "active_days": len(
            active_days
        ),
        "points": _safe_int(
            member.get(
                "points",
                0
            )
        ),
        "xp": _safe_int(
            member.get(
                "xp",
                0
            )
        ),
        "quiz_correct": _safe_int(
            member.get(
                "quiz_correct",
                0
            )
        ),
        "quiz_attempts": _safe_int(
            member.get(
                "quiz_attempts",
                0
            )
        ),
        "mood_checkins": _safe_int(
            member.get(
                "mood_checkins",
                0
            )
        ),
        "first_seen": member.get(
            "first_seen"
        ),
        "last_seen": member.get(
            "last_seen"
        ),
    }


# ============================================================
# GROUP STATISTICS
# ============================================================

def get_group_stats(
    chat_id
):
    """
    Return high-level group statistics.
    """

    group = get_group(
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

    total_messages = _safe_int(
        group.get(
            "total_messages",
            0
        )
    )

    today_messages = _safe_int(
        group.get(
            "daily",
            {}
        ).get(
            today_key(),
            0
        )
    )

    this_week = _safe_int(
        group.get(
            "weekly",
            {}
        ).get(
            week_key(),
            0
        )
    )

    this_month = _safe_int(
        group.get(
            "monthly",
            {}
        ).get(
            month_key(),
            0
        )
    )

    return {
        "chat_id": str(
            chat_id
        ),
        "title": group.get(
            "title"
        ),
        "type": group.get(
            "type"
        ),
        "total_messages": total_messages,
        "today_messages": today_messages,
        "this_week_messages": this_week,
        "this_month_messages": this_month,
        "member_count": len(
            members
        ),
        "peak_hour": get_peak_hour(
            chat_id
        ),
        "peak_weekday": get_peak_weekday(
            chat_id
        ),
        "top_member": get_top_member(
            chat_id
        ),
    }


# ============================================================
# TOP MEMBERS
# ============================================================

def get_top_members(
    chat_id,
    limit=10
):
    """
    Return most active group members.
    """

    try:
        limit = int(
            limit
        )

    except Exception:
        limit = 10

    limit = max(
        1,
        min(
            limit,
            MAX_MEMBER_RESULTS
        )
    )

    group = get_group(
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
        return []

    result = []

    for user_id, member in members.items():

        if not isinstance(
            member,
            dict
        ):
            continue

        result.append(
            {
                "user_id": str(
                    user_id
                ),
                "username": member.get(
                    "username"
                ),
                "first_name": member.get(
                    "first_name"
                ),
                "messages": _safe_int(
                    member.get(
                        "messages",
                        0
                    )
                ),
                "today_messages": _safe_int(
                    member.get(
                        "daily",
                        {}
                    ).get(
                        today_key(),
                        0
                    )
                ),
                "points": _safe_int(
                    member.get(
                        "points",
                        0
                    )
                ),
                "xp": _safe_int(
                    member.get(
                        "xp",
                        0
                    )
                ),
            }
        )

    result.sort(
        key=lambda item: (
            item["messages"],
            item["today_messages"],
            item["xp"],
        ),
        reverse=True
    )

    return result[
        :limit
    ]


# ============================================================
# TOP MEMBER
# ============================================================

def get_top_member(
    chat_id
):
    """
    Return the most active member.
    """

    members = get_top_members(
        chat_id,
        limit=1
    )

    if not members:
        return None

    return members[0]


# ============================================================
# PEAK HOUR
# ============================================================

def get_peak_hour(
    chat_id
):
    """
    Return the hour with the most messages.
    """

    group = get_group(
        chat_id
    )

    hourly = group.get(
        "hourly",
        {}
    )

    if not isinstance(
        hourly,
        dict
    ) or not hourly:

        return None

    peak = max(
        hourly.items(),
        key=lambda item: _safe_int(
            item[1]
        )
    )

    try:
        hour = int(
            peak[0]
        )

    except Exception:
        hour = peak[0]

    return {
        "hour": hour,
        "messages": _safe_int(
            peak[1]
        ),
    }


# ============================================================
# PEAK WEEKDAY
# ============================================================

def get_peak_weekday(
    chat_id
):
    """
    Return weekday with the most messages.
    """

    group = get_group(
        chat_id
    )

    weekday = group.get(
        "weekday",
        {}
    )

    if not isinstance(
        weekday,
        dict
    ) or not weekday:

        return None

    peak = max(
        weekday.items(),
        key=lambda item: _safe_int(
            item[1]
        )
    )

    return {
        "day": peak[0],
        "messages": _safe_int(
            peak[1]
        ),
    }


# ============================================================
# DAILY MESSAGE COUNT
# ============================================================

def get_daily_messages(
    chat_id,
    date=None
):
    """
    Return message count for a specific date.
    """

    group = get_group(
        chat_id
    )

    if date is None:
        date = today_key()

    date = _safe_string(
        date
    )

    return _safe_int(
        group.get(
            "daily",
            {}
        ).get(
            date,
            0
        )
    )


# ============================================================
# WEEKLY MESSAGE COUNT
# ============================================================

def get_weekly_messages(
    chat_id,
    week=None
):
    """
    Return message count for a week.
    """

    group = get_group(
        chat_id
    )

    if week is None:
        week = week_key()

    return _safe_int(
        group.get(
            "weekly",
            {}
        ).get(
            str(week),
            0
        )
    )


# ============================================================
# MONTHLY MESSAGE COUNT
# ============================================================

def get_monthly_messages(
    chat_id,
    month=None
):
    """
    Return message count for a month.
    """

    group = get_group(
        chat_id
    )

    if month is None:
        month = month_key()

    return _safe_int(
        group.get(
            "monthly",
            {}
        ).get(
            str(month),
            0
        )
    )


# ============================================================
# ACTIVITY PERCENTAGE
# ============================================================

def get_member_activity_percentage(
    chat_id,
    user_id
):
    """
    Calculate a member's percentage of total group messages.
    """

    group = get_group(
        chat_id
    )

    member = group.get(
        "members",
        {}
    ).get(
        str(user_id),
        {}
    )

    total = _safe_int(
        group.get(
            "total_messages",
            0
        )
    )

    messages = _safe_int(
        member.get(
            "messages",
            0
        )
    )

    if total <= 0:
        return 0.0

    return round(
        messages
        / total
        * 100,
        2
    )


# ============================================================
# MEMBER RANK
# ============================================================

def get_member_rank(
    chat_id,
    user_id
):
    """
    Return member's rank based on total messages.
    """

    members = get_top_members(
        chat_id,
        limit=MAX_MEMBER_RESULTS
    )

    target_id = str(
        user_id
    )

    for index, member in enumerate(
        members,
        start=1
    ):

        if member.get(
            "user_id"
        ) == target_id:

            return {
                "rank": index,
                "total_members": len(
                    members
                ),
                "messages": member.get(
                    "messages",
                    0
                ),
            }

    return {
        "rank": None,
        "total_members": len(
            members
        ),
        "messages": 0,
    }


# ============================================================
# MESSAGE MILESTONE
# ============================================================

def get_next_message_milestone(
    chat_id
):
    """
    Return next group message milestone.
    """

    group = get_group(
        chat_id
    )

    total = _safe_int(
        group.get(
            "total_messages",
            0
        )
    )

    for milestone in MESSAGE_MILESTONES:

        if total < milestone:

            return {
                "current": total,
                "milestone": milestone,
                "remaining": milestone - total,
            }

    # Dynamic milestone after predefined list.
    next_milestone = (
        ((total // 10000) + 1)
        * 10000
    )

    return {
        "current": total,
        "milestone": next_milestone,
        "remaining": (
            next_milestone - total
        ),
    }


# ============================================================
# CHECK MESSAGE MILESTONE
# ============================================================

def check_message_milestone(
    chat_id
):
    """
    Check whether the group has just reached
    a predefined message milestone.
    """

    group = get_group(
        chat_id
    )

    total = _safe_int(
        group.get(
            "total_messages",
            0
        )
    )

    if total <= 0:
        return None

    if total in MESSAGE_MILESTONES:

        return {
            "reached": True,
            "milestone": total,
        }

    return {
        "reached": False,
        "milestone": None,
    }


# ============================================================
# GROUP ACTIVITY SCORE
# ============================================================

def get_activity_score(
    chat_id
):
    """
    Calculate a simple activity score.

    This is an analytics score, not a ranking of people's value.
    """

    stats = get_group_stats(
        chat_id
    )

    today = stats[
        "today_messages"
    ]

    weekly = stats[
        "this_week_messages"
    ]

    members = stats[
        "member_count"
    ]

    score = (
        today * 1.0
        + weekly * 0.15
        + members * 2.0
    )

    return round(
        score,
        2
    )


# ============================================================
# ANALYTICS SNAPSHOT
# ============================================================

def create_snapshot(
    chat_id
):
    """
    Create and save an analytics snapshot.
    """

    chat_id = str(
        chat_id
    )

    data = v4_data.load_v4_data()

    group = _initialize_group(
        data,
        chat_id
    )

    analytics = group.setdefault(
        "analytics",
        {}
    )

    snapshots = analytics.setdefault(
        "snapshots",
        []
    )

    if not isinstance(
        snapshots,
        list
    ):
        snapshots = []
        analytics["snapshots"] = snapshots

    stats = get_group_stats(
        chat_id
    )

    snapshot = {
        "date": today_key(),
        "timestamp": _now().isoformat(),
        "total_messages": stats[
            "total_messages"
        ],
        "today_messages": stats[
            "today_messages"
        ],
        "this_week_messages": stats[
            "this_week_messages"
        ],
        "this_month_messages": stats[
            "this_month_messages"
        ],
        "member_count": stats[
            "member_count"
        ],
        "activity_score": get_activity_score(
            chat_id
        ),
    }

    # Avoid duplicate snapshots for same day.
    if snapshots:

        last = snapshots[-1]

        if (
            isinstance(
                last,
                dict
            )
            and last.get(
                "date"
            ) == today_key()
        ):

            snapshots[-1] = snapshot

        else:

            snapshots.append(
                snapshot
            )

    else:

        snapshots.append(
            snapshot
        )

    # Keep storage bounded.
    if len(
        snapshots
    ) > 365:

        del snapshots[
            :-365
        ]

    analytics[
        "last_snapshot"
    ] = snapshot

    v4_data.save_v4_data(
        data
    )

    return snapshot


# ============================================================
# GET SNAPSHOTS
# ============================================================

def get_snapshots(
    chat_id,
    limit=30
):
    """
    Return recent analytics snapshots.
    """

    try:
        limit = int(
            limit
        )

    except Exception:
        limit = 30

    limit = max(
        1,
        min(
            limit,
            365
        )
    )

    group = get_group(
        chat_id
    )

    snapshots = group.get(
        "analytics",
        {}
    ).get(
        "snapshots",
        []
    )

    if not isinstance(
        snapshots,
        list
    ):
        return []

    return list(
        reversed(
            snapshots[-limit:]
        )
    )


# ============================================================
# FORMAT TOP MEMBERS
# ============================================================

def format_top_members(
    chat_id,
    limit=5
):
    """
    Format leaderboard-style group activity.
    """

    members = get_top_members(
        chat_id,
        limit=limit
    )

    if not members:

        return (
            "👥 No group activity recorded yet."
        )

    lines = [
        "🏆 *Most Active Members*",
        "",
    ]

    medals = [
        "🥇",
        "🥈",
        "🥉",
    ]

    for index, member in enumerate(
        members,
        start=1
    ):

        medal = (
            medals[index - 1]
            if index <= 3
            else f"{index}."
        )

        name = (
            member.get(
                "first_name"
            )
            or member.get(
                "username"
            )
            or member.get(
                "user_id"
            )
        )

        messages = member.get(
            "messages",
            0
        )

        lines.append(
            f"{medal} {name} — "
            f"💬 {messages}"
        )

    return "\n".join(
        lines
    )


# ============================================================
# FORMAT GROUP ANALYTICS
# ============================================================

def format_group_analytics(
    chat_id
):
    """
    Format complete group analytics summary.
    """

    stats = get_group_stats(
        chat_id
    )

    title = (
        stats.get(
            "title"
        )
        or "This Group"
    )

    peak_hour = stats.get(
        "peak_hour"
    )

    peak_day = stats.get(
        "peak_weekday"
    )

    top_member = stats.get(
        "top_member"
    )

    lines = [
        f"📊 *{title} — Group Analytics*",
        "",
        f"💬 Total messages: "
        f"{stats['total_messages']}",
        f"📅 Today: "
        f"{stats['today_messages']}",
        f"🗓 This week: "
        f"{stats['this_week_messages']}",
        f"📆 This month: "
        f"{stats['this_month_messages']}",
        f"👥 Members tracked: "
        f"{stats['member_count']}",
    ]

    if peak_hour:

        lines.append(
            f"⏰ Peak hour: "
            f"{peak_hour['hour']:02d}:00 "
            f"({peak_hour['messages']} messages)"
        )

    if peak_day:

        lines.append(
            f"📈 Most active day: "
            f"{peak_day['day']} "
            f"({peak_day['messages']} messages)"
        )

    if top_member:

        name = (
            top_member.get(
                "first_name"
            )
            or top_member.get(
                "username"
            )
            or top_member.get(
                "user_id"
            )
        )

        lines.append(
            f"🏆 Top member: "
            f"{name} "
            f"({top_member.get('messages', 0)} messages)"
        )

    milestone = get_next_message_milestone(
        chat_id
    )

    if milestone:

        lines.append(
            f"🎯 Next milestone: "
            f"{milestone['milestone']} messages "
            f"({milestone['remaining']} to go)"
        )

    lines.append(
        f"⚡ Activity score: "
        f"{get_activity_score(chat_id)}"
    )

    return "\n".join(
        lines
    )


# ============================================================
# FORMAT MEMBER ANALYTICS
# ============================================================

def format_member_analytics(
    chat_id,
    user_id
):
    """
    Format one member's group analytics.
    """

    stats = get_member_stats(
        chat_id,
        user_id
    )

    rank = get_member_rank(
        chat_id,
        user_id
    )

    percentage = (
        get_member_activity_percentage(
            chat_id,
            user_id
        )
    )

    name = (
        stats.get(
            "first_name"
        )
        or stats.get(
            "username"
        )
        or str(
            user_id
        )
    )

    return (
        f"👤 *{name} — Group Stats*\n\n"
        f"💬 Messages: "
        f"{stats['messages']}\n"
        f"📅 Today: "
        f"{stats['today_messages']}\n"
        f"🗓 This week: "
        f"{stats['this_week_messages']}\n"
        f"📆 This month: "
        f"{stats['this_month_messages']}\n"
        f"📊 Group share: "
        f"{percentage}%\n"
        f"🏆 Rank: "
        f"{rank['rank'] or 'N/A'}\n"
        f"🔥 Active days: "
        f"{stats['active_days']}\n"
        f"⭐ XP: "
        f"{stats['xp']}\n"
        f"🎯 Points: "
        f"{stats['points']}"
    )


# ============================================================
# ADD MEMBER POINTS
# ============================================================

def add_member_points(
    chat_id,
    user_id,
    points
):
    """
    Add analytics-related points to a group member.
    """

    points = _safe_int(
        points
    )

    if points <= 0:

        return {
            "success": False,
            "points_added": 0,
        }

    data = v4_data.load_v4_data()

    group = _initialize_group(
        data,
        chat_id
    )

    member = _initialize_member(
        group,
        user_id
    )

    old_points = _safe_int(
        member.get(
            "points",
            0
        )
    )

    new_points = (
        old_points
        + points
    )

    member["points"] = (
        new_points
    )

    group["updated_at"] = (
        _now().isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return {
        "success": True,
        "points_added": points,
        "old_points": old_points,
        "new_points": new_points,
    }


# ============================================================
# ADD MEMBER XP
# ============================================================

def add_member_xp(
    chat_id,
    user_id,
    xp
):
    """
    Add group-specific XP to a member.

    This is separate from the global user XP system.
    """

    xp = _safe_int(
        xp
    )

    if xp <= 0:

        return {
            "success": False,
            "xp_added": 0,
        }

    data = v4_data.load_v4_data()

    group = _initialize_group(
        data,
        chat_id
    )

    member = _initialize_member(
        group,
        user_id
    )

    old_xp = _safe_int(
        member.get(
            "xp",
            0
        )
    )

    new_xp = (
        old_xp
        + xp
    )

    member["xp"] = (
        new_xp
    )

    group["updated_at"] = (
        _now().isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return {
        "success": True,
        "xp_added": xp,
        "old_xp": old_xp,
        "new_xp": new_xp,
    }


# ============================================================
# RECORD QUIZ RESULT
# ============================================================

def record_quiz_result(
    chat_id,
    user_id,
    correct=False,
    points=0
):
    """
    Record group quiz activity for a member.
    """

    data = v4_data.load_v4_data()

    group = _initialize_group(
        data,
        chat_id
    )

    member = _initialize_member(
        group,
        user_id
    )

    quiz = group.setdefault(
        "quiz",
        {}
    )

    quiz["attempts"] = (
        _safe_int(
            quiz.get(
                "attempts",
                0
            )
        )
        + 1
    )

    if correct:

        quiz["correct"] = (
            _safe_int(
                quiz.get(
                    "correct",
                    0
                )
            )
            + 1
        )

        member["quiz_correct"] = (
            _safe_int(
                member.get(
                    "quiz_correct",
                    0
                )
            )
            + 1
        )

    member["quiz_attempts"] = (
        _safe_int(
            member.get(
                "quiz_attempts",
                0
            )
        )
        + 1
    )

    if points:

        points = max(
            0,
            _safe_int(
                points
            )
        )

        member["points"] = (
            _safe_int(
                member.get(
                    "points",
                    0
                )
            )
            + points
        )

    quiz["last_activity"] = (
        _now().isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return {
        "success": True,
        "correct": bool(
            correct
        ),
        "points": points,
        "quiz_attempts": member[
            "quiz_attempts"
        ],
        "quiz_correct": member[
            "quiz_correct"
        ],
    }


# ============================================================
# RECORD MOOD CHECK-IN
# ============================================================

def record_mood_checkin(
    chat_id,
    user_id
):
    """
    Record a group member mood check-in.
    """

    data = v4_data.load_v4_data()

    group = _initialize_group(
        data,
        chat_id
    )

    member = _initialize_member(
        group,
        user_id
    )

    member["mood_checkins"] = (
        _safe_int(
            member.get(
                "mood_checkins",
                0
            )
        )
        + 1
    )

    mood = group.setdefault(
        "mood",
        {}
    )

    mood["total_checkins"] = (
        _safe_int(
            mood.get(
                "total_checkins",
                0
            )
        )
        + 1
    )

    mood["last_checkin_at"] = (
        _now().isoformat()
    )

    v4_data.save_v4_data(
        data
    )

    return {
        "success": True,
        "member_mood_checkins": member[
            "mood_checkins"
        ],
        "group_mood_checkins": mood[
            "total_checkins"
        ],
    }


# ============================================================
# CLEAN OLD DAILY DATA
# ============================================================

def cleanup_old_daily_data(
    chat_id,
    keep_days=90
):
    """
    Remove very old daily message counters.

    This prevents unlimited JSON growth.
    """

    try:
        keep_days = int(
            keep_days
        )

    except Exception:
        keep_days = 90

    keep_days = max(
        7,
        min(
            keep_days,
            730
        )
    )

    group = get_group(
        chat_id
    )

    daily = group.get(
        "daily",
        {}
    )

    if not isinstance(
        daily,
        dict
    ):
        return False

    # Since keys are YYYY-MM-DD strings,
    # lexical sorting works correctly.
    dates = sorted(
        daily.keys()
    )

    if len(
        dates
    ) <= keep_days:

        return True

    remove = dates[
        :-keep_days
    ]

    data = v4_data.load_v4_data()

    group = _initialize_group(
        data,
        chat_id
    )

    daily = group.setdefault(
        "daily",
        {}
    )

    for date in remove:

        daily.pop(
            date,
            None
        )

    v4_data.save_v4_data(
        data
    )

    return True


# ============================================================
# GROUP ANALYTICS SNAPSHOT
# ============================================================

def get_analytics_snapshot(
    chat_id
):
    """
    Return a compact analytics snapshot without
    changing stored data.
    """

    stats = get_group_stats(
        chat_id
    )

    return {
        "chat_id": str(
            chat_id
        ),
        "title": stats.get(
            "title"
        ),
        "total_messages": stats[
            "total_messages"
        ],
        "today_messages": stats[
            "today_messages"
        ],
        "week_messages": stats[
            "this_week_messages"
        ],
        "month_messages": stats[
            "this_month_messages"
        ],
        "member_count": stats[
            "member_count"
        ],
        "activity_score": get_activity_score(
            chat_id
        ),
        "peak_hour": stats[
            "peak_hour"
        ],
        "peak_weekday": stats[
            "peak_weekday"
        ],
        "top_member": stats[
            "top_member"
        ],
    }


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    # Time
    "today_key",
    "current_hour",
    "current_weekday",
    "month_key",
    "week_key",

    # Message tracking
    "record_message",
    "record_group_message",

    # Data
    "get_group",
    "get_member",
    "get_member_stats",
    "get_group_stats",

    # Leaderboards
    "get_top_members",
    "get_top_member",
    "get_member_rank",

    # Analytics
    "get_peak_hour",
    "get_peak_weekday",
    "get_daily_messages",
    "get_weekly_messages",
    "get_monthly_messages",
    "get_member_activity_percentage",
    "get_activity_score",

    # Milestones
    "get_next_message_milestone",
    "check_message_milestone",

    # Snapshots
    "create_snapshot",
    "get_snapshots",
    "get_analytics_snapshot",

    # Formatting
    "format_top_members",
    "format_group_analytics",
    "format_member_analytics",

    # Points / XP
    "add_member_points",
    "add_member_xp",

    # Quiz / mood
    "record_quiz_result",
    "record_mood_checkin",

    # Maintenance
    "cleanup_old_daily_data",
]

