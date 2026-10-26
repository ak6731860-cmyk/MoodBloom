from datetime import datetime, timedelta
from collections import Counter

import moods

try:
    from config import TIMEZONE
except ImportError:
    TIMEZONE = None


# ============================================================
# DATE / TIME HELPERS
# ============================================================

def _now():
    """
    Returns current time using MoodBloom timezone when available.
    Falls back to local system time.
    """

    if TIMEZONE is not None:
        return datetime.now(TIMEZONE)

    return datetime.now()

def get_entry_date(entry):
    """
    Safely gets date from a history entry.
    Expected format: YYYY-MM-DD
    Returns datetime.date or None.
    """
    if not isinstance(entry, dict):
        return None

    date_text = entry.get("date")

    if not date_text:
        return None

    try:
        return datetime.strptime(
            str(date_text).strip(),
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError, AttributeError):
        return None

def get_counts(history):
    """
    Returns count of each mood.
    """

    counts = Counter()

    if not history:
        return {}

    for entry in history:

        if not isinstance(entry, dict):
            continue

        mood = entry.get("mood")

        if mood:
            counts[str(mood)] += 1

    return dict(counts)


# ============================================================
# BASIC STATISTICS
# ============================================================

def total_checkins(history):
    """
    Total number of valid mood check-ins.
    """

    if not history:
        return 0

    return sum(
        1
        for entry in history
        if isinstance(entry, dict)
        and entry.get("mood")
    )


def unique_days(history):
    """
    Number of different days tracked.
    """

    dates = set()

    if not history:
        return 0

    for entry in history:

        entry_date = get_entry_date(entry)

        if entry_date:
            dates.add(entry_date)

    return len(dates)


def favorite_mood(history):
    """
    Returns the most frequently selected mood.
    """

    counts = get_counts(history)

    if not counts:
        return None

    return max(
        counts,
        key=counts.get
    )


# ============================================================
# MOOD DISTRIBUTION
# ============================================================

def mood_distribution(history):
    """
    Returns mood counts and percentages.
    """

    total = total_checkins(history)

    if total == 0:
        return {}

    counts = get_counts(history)

    distribution = {}

    for mood, count in counts.items():

        percentage = round(
            (count / total) * 100
        )

        distribution[mood] = {
            "count": count,
            "percentage": percentage
        }

    return distribution


# ============================================================
# RECENT MOOD
# ============================================================

def recent_mood(history):
    """
    Returns latest recorded mood.
    """

    if not history:
        return None

    for entry in reversed(history):

        if not isinstance(entry, dict):
            continue

        mood = entry.get("mood")

        if mood:
            return mood

    return None


def recent_entries(history, limit=5):
    """
    Returns latest valid check-ins.
    """

    if not history:
        return []

    valid_entries = [
        entry
        for entry in history
        if isinstance(entry, dict)
        and entry.get("mood")
    ]

    return valid_entries[-limit:]


# ============================================================
# TODAY
# ============================================================

def today_entries(history):
    """
    Returns today's check-ins.
    """

    today = _now().date()

    result = []

    if not history:
        return result

    for entry in history:

        entry_date = get_entry_date(entry)

        if entry_date == today:
            result.append(entry)

    return result


def today_moods(history):
    """
    Returns only today's mood names.
    """

    return [
        entry.get("mood")
        for entry in today_entries(history)
        if isinstance(entry, dict)
        and entry.get("mood")
    ]


def today_counts(history):
    """
    Returns today's mood counts.
    """

    return get_counts(
        today_entries(history)
    )


# ============================================================
# WEEKLY DATA
# ============================================================

def weekly_entries(history):
    """
    Returns entries from the last 7 days,
    including today.
    """

    today = _now().date()

    start_date = today - timedelta(days=6)

    result = []

    if not history:
        return result

    for entry in history:

        entry_date = get_entry_date(entry)

        if (
            entry_date
            and start_date <= entry_date <= today
        ):
            result.append(entry)

    return result


def weekly_counts(history):
    """
    Returns mood counts for last 7 days.
    """

    return get_counts(
        weekly_entries(history)
    )


def weekly_mood_distribution(history):
    """
    Returns percentage distribution
    for last 7 days.
    """

    return mood_distribution(
        weekly_entries(history)
    )


def previous_week_entries(history):
    """
    Returns entries from the 7 days
    immediately before the current 7-day period.
    """

    today = _now().date()

    current_week_start = today - timedelta(days=6)

    previous_week_end = (
        current_week_start
        - timedelta(days=1)
    )

    previous_week_start = (
        previous_week_end
        - timedelta(days=6)
    )

    result = []

    if not history:
        return result

    for entry in history:

        entry_date = get_entry_date(entry)

        if (
            entry_date
            and previous_week_start <= entry_date
            <= previous_week_end
        ):
            result.append(entry)

    return result


def previous_week_counts(history):
    """
    Returns mood counts for previous 7-day period.
    """

    return get_counts(
        previous_week_entries(history)
    )


# ============================================================
# STREAK
# ============================================================

def _get_unique_dates(history):
    """
    Returns sorted unique tracking dates.
    """

    dates = set()

    if not history:
        return dates

    for entry in history:

        entry_date = get_entry_date(entry)

        if entry_date:
            dates.add(entry_date)

    return dates


def current_streak(history):
    """
    Calculates current consecutive-day streak.

    If there is no check-in today,
    yesterday can still keep the streak alive.
    """

    dates = _get_unique_dates(history)

    if not dates:
        return 0

    today = _now().date()

    yesterday = (
        today - timedelta(days=1)
    )

    if today in dates:
        current_day = today

    elif yesterday in dates:
        current_day = yesterday

    else:
        return 0

    streak = 0

    while current_day in dates:

        streak += 1

        current_day -= timedelta(days=1)

    return streak


def best_streak(history):
    """
    Calculates highest streak ever achieved.
    """

    dates = _get_unique_dates(history)

    if not dates:
        return 0

    sorted_dates = sorted(dates)

    best = 1
    current = 1

    for index in range(
        1,
        len(sorted_dates)
    ):

        difference = (
            sorted_dates[index]
            - sorted_dates[index - 1]
        ).days

        if difference == 1:

            current += 1

            best = max(
                best,
                current
            )

        else:

            current = 1

    return best


# ============================================================
# XP & LEVEL
# ============================================================

def get_xp(history):
    """
    Gives 10 XP for every mood check-in.
    """

    return total_checkins(history) * 10


def get_level(history):
    """
    Calculates current level.

    Every 100 XP = one level.
    """

    xp = get_xp(history)

    return (
        xp // 100
    ) + 1


def get_level_progress(history):
    """
    Returns XP progress inside current level.
    """

    xp = get_xp(history)

    return xp % 100


def get_xp_to_next_level(history):
    """
    Returns remaining XP required
    for the next level.

    At an exact level boundary,
    100 XP is needed for the next level.
    """

    progress = get_level_progress(
        history
    )

    return 100 - progress


def get_progress_bar(
    history,
    size=10
):
    """
    Creates a visual XP progress bar.
    """

    progress = get_level_progress(
        history
    )

    filled = int(
        (progress / 100) * size
    )

    empty = size - filled

    return (
        "🟩" * filled
        + "⬜" * empty
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

def achievements(history):
    """
    Returns unlocked achievements.
    """

    total = total_checkins(history)

    best = best_streak(history)

    unlocked = []

    # --------------------------------------------------------
    # Check-in achievements
    # --------------------------------------------------------

    if total >= 1:
        unlocked.append(
            "🌱 First Check-in"
        )

    if total >= 5:
        unlocked.append(
            "🌸 5 Check-ins"
        )

    if total >= 10:
        unlocked.append(
            "✨ 10 Check-ins"
        )

    if total >= 25:
        unlocked.append(
            "💎 25 Check-ins"
        )

    if total >= 50:
        unlocked.append(
            "👑 50 Check-ins"
        )

    if total >= 100:
        unlocked.append(
            "🏆 100 Check-ins"
        )

    # --------------------------------------------------------
    # Streak achievements
    # --------------------------------------------------------

    if best >= 3:
        unlocked.append(
            "🔥 3-Day Streak"
        )

    if best >= 7:
        unlocked.append(
            "🔥🔥 7-Day Streak"
        )

    if best >= 14:
        unlocked.append(
            "🚀 14-Day Streak"
        )

    if best >= 30:
        unlocked.append(
            "👑 30-Day Streak"
        )

    # --------------------------------------------------------
    # Variety achievement
    # --------------------------------------------------------

    if len(
        get_counts(history)
    ) >= 5:

        unlocked.append(
            "🌈 Mood Explorer"
        )

    # --------------------------------------------------------
    # Consistency achievement
    # --------------------------------------------------------

    if unique_days(history) >= 7:

        unlocked.append(
            "📅 Week Tracker"
        )

    return unlocked


# ============================================================
# MOOD SCORE
# ============================================================

def mood_score(mood_key):
    """
    Returns the statistical score defined
    by the MoodBloom mood database.

    This is NOT a medical or psychological score.
    """

    try:
        return moods.get_mood_score(
            mood_key
        )

    except AttributeError:

        scores = {
            "happy": 5,
            "loved": 5,
            "okay": 3,
            "tired": 2,
            "sad": 2,
            "angry": 2
        }

        return scores.get(
            mood_key,
            3
        )


def average_mood_score(history):
    """
    Calculates average mood score.
    """

    if not history:
        return 0

    scores = []

    for entry in history:

        if not isinstance(entry, dict):
            continue

        mood = entry.get("mood")

        if mood:
            scores.append(
                mood_score(mood)
            )

    if not scores:
        return 0

    return round(
        sum(scores) / len(scores),
        2
    )


def mood_score_label(score):
    """
    Converts average score into
    a simple MoodBloom label.
    """

    try:
        score = float(score)
    except (
        TypeError,
        ValueError
    ):
        return "Unknown"

    if score >= 4.5:
        return "Very Positive"

    if score >= 3.5:
        return "Positive"

    if score >= 2.5:
        return "Neutral"

    if score >= 1.5:
        return "Low"

    return "Very Low"


# ============================================================
# MOOD TREND
# ============================================================

def mood_trend(history):
    """
    Compares recent 7-day mood activity
    with the previous 7-day period.
    """

    today = _now().date()

    recent_start = (
        today - timedelta(days=6)
    )

    previous_start = (
        today - timedelta(days=13)
    )

    previous_end = (
        today - timedelta(days=7)
    )

    recent = []

    previous = []

    for entry in history or []:

        entry_date = get_entry_date(
            entry
        )

        if not entry_date:
            continue

        if recent_start <= entry_date <= today:

            recent.append(entry)

        elif (
            previous_start
            <= entry_date
            <= previous_end
        ):

            previous.append(entry)

    recent_score = average_mood_score(
        recent
    )

    previous_score = average_mood_score(
        previous
    )

    if not previous:

        direction = "new"

    elif recent_score > previous_score:

        direction = "up"

    elif recent_score < previous_score:

        direction = "down"

    else:

        direction = "stable"

    return {
        "recent_score": recent_score,
        "previous_score": previous_score,
        "direction": direction,
        "recent_entries": len(recent),
        "previous_entries": len(previous)
    }


# ============================================================
# DAILY MOOD SCORE
# ============================================================

def daily_mood_scores(history):
    """
    Returns average mood score for each of
    the last 7 days.
    """

    today = _now().date()

    result = []

    for offset in range(
        6,
        -1,
        -1
    ):

        target_date = (
            today
            - timedelta(days=offset)
        )

        day_entries = []

        for entry in history or []:

            if (
                get_entry_date(entry)
                == target_date
            ):
                day_entries.append(entry)

        score = average_mood_score(
            day_entries
        )

        result.append({
            "date": target_date,
            "score": score,
            "entries": len(day_entries)
        })

    return result


# ============================================================
# MOOD VARIETY
# ============================================================

def mood_variety(history):
    """
    Returns how many different moods
    have been tracked.
    """

    counts = get_counts(history)

    return len(counts)


# ============================================================
# MOST POSITIVE / LOWEST MOOD
# ============================================================

def highest_scored_mood(history):
    """
    Returns the mood with the highest
    average occurrence score among tracked moods.
    """

    counts = get_counts(history)

    if not counts:
        return None

    return max(
        counts.keys(),
        key=lambda mood: mood_score(mood)
    )


def lowest_scored_mood(history):
    """
    Returns the mood with the lowest
    statistical score among tracked moods.
    """

    counts = get_counts(history)

    if not counts:
        return None

    return min(
        counts.keys(),
        key=lambda mood: mood_score(mood)
    )


# ============================================================
# SMART INSIGHTS DATA
# ============================================================

def smart_insights(history):
    """
    Creates structured data for smart insights.
    """

    if not history:

        return {
            "has_data": False
        }

    distribution = mood_distribution(
        history
    )

    common = favorite_mood(
        history
    )

    latest = recent_mood(
        history
    )

    streak = current_streak(
        history
    )

    best = best_streak(
        history
    )

    score = average_mood_score(
        history
    )

    trend = mood_trend(
        history
    )

    mood_info = moods.get_mood_info(
        common
    )

    return {

        "has_data": True,

        "total": total_checkins(
            history
        ),

        "days": unique_days(
            history
        ),

        "favorite_mood": common,

        "favorite_name": mood_info.get(
            "name",
            common.title()
            if common
            else "Unknown"
        ),

        "favorite_emoji": mood_info.get(
            "emoji",
            "🌸"
        ),

        "recent_mood": latest,

        "streak": streak,

        "best_streak": best,

        "average_score": score,

        "score_label": mood_score_label(
            score
        ),

        "mood_variety": mood_variety(
            history
        ),

        "distribution": distribution,

        "trend": trend
    }


# ============================================================
# MOOD FORECAST
# ============================================================

def mood_forecast(history):
    """
    Creates a simple pattern-based mood forecast.

    IMPORTANT:
    This does NOT actually predict the future.
    It studies recent mood history and estimates
    which pattern is currently dominant.
    """

    if not history:

        return {
            "has_data": False,
            "message": (
                "🌱 I need some mood check-ins "
                "before I can show a pattern."
            )
        }

    recent = weekly_entries(
        history
    )

    if not recent:

        return {
            "has_data": False,
            "message": (
                "🌱 Keep checking in and "
                "I'll learn your mood pattern."
            )
        }

    counts = get_counts(
        recent
    )

    if not counts:

        return {
            "has_data": False
        }

    dominant_mood = max(
        counts,
        key=counts.get
    )

    dominant_count = counts[
        dominant_mood
    ]

    total = len(recent)

    percentage = round(
        (dominant_count / total) * 100
    )

    mood_info = moods.get_mood_info(
        dominant_mood
    )

    mood_name = mood_info.get(
        "name",
        dominant_mood.title()
    )

    mood_emoji = mood_info.get(
        "emoji",
        "🌸"
    )

    if percentage >= 70:

        confidence = "High"

    elif percentage >= 50:

        confidence = "Moderate"

    else:

        confidence = "Low"

    if percentage >= 70:

        pattern = (
            f"{mood_emoji} {mood_name} "
            "has been your strongest recent pattern."
        )

        forecast = (
            f"If your recent pattern continues, "
            f"your upcoming mood pattern may lean "
            f"toward {mood_name.lower()}."
        )

    elif percentage >= 50:

        pattern = (
            f"{mood_emoji} {mood_name} "
            "is currently your most common recent mood."
        )

        forecast = (
            f"Your next few check-ins may show a "
            f"slight tendency toward {mood_name.lower()}, "
            "but the pattern is not very strong."
        )

    else:

        pattern = (
            "🌈 Your recent moods are quite mixed."
        )

        forecast = (
            "There isn't a strong dominant pattern "
            "right now, so your upcoming mood pattern "
            "is difficult to estimate."
        )

    return {

        "has_data": True,

        "dominant_mood": dominant_mood,

        "dominant_name": mood_name,

        "dominant_emoji": mood_emoji,

        "dominant_count": dominant_count,

        "total_recent": total,

        "percentage": percentage,

        "confidence": confidence,

        "pattern": pattern,

        "forecast": forecast,

        "disclaimer": (
            "ℹ️ This is a pattern-based estimate, "
            "not a real prediction of the future."
        )
    }


# ============================================================
# MOOD PATTERN SUMMARY
# ============================================================

def mood_pattern_summary(history):
    """
    Returns compact summary of overall
    mood pattern.
    """

    if not history:

        return {
            "has_data": False
        }

    counts = get_counts(
        history
    )

    if not counts:

        return {
            "has_data": False
        }

    sorted_moods = sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    result = []

    total = total_checkins(
        history
    )

    for mood, count in sorted_moods:

        info = moods.get_mood_info(
            mood
        )

        result.append({

            "mood": mood,

            "name": info.get(
                "name",
                mood.title()
            ),

            "emoji": info.get(
                "emoji",
                "🌸"
            ),

            "count": count,

            "percentage": round(
                (count / total) * 100
            ),

            "score": mood_score(
                mood
            )
        })

    return {

        "has_data": True,

        "total": total,

        "moods": result
    }


# ============================================================
# GROUP ANALYTICS
# ============================================================

def group_mood_counts(group_history):
    """
    Counts moods from group mood records.
    """

    counts = Counter()

    if not group_history:
        return {}

    for entry in group_history:

        if not isinstance(entry, dict):
            continue

        mood = entry.get("mood")

        if mood:
            counts[str(mood)] += 1

    return dict(counts)


def group_total_checkins(group_history):
    """
    Total number of group mood check-ins.
    """

    if not group_history:
        return 0

    return sum(
        1
        for entry in group_history
        if isinstance(entry, dict)
        and entry.get("mood")
    )


def group_unique_members(group_history):
    """
    Number of unique users participating
    in group mood check-ins.
    """

    users = set()

    for entry in group_history or []:

        if not isinstance(entry, dict):
            continue

        user_id = entry.get(
            "user_id"
        )

        if user_id is not None:
            users.add(
                str(user_id)
            )

    return len(users)


def group_mood_distribution(group_history):
    """
    Returns group mood counts and percentages.
    """

    total = group_total_checkins(
        group_history
    )

    if total == 0:
        return {}

    counts = group_mood_counts(
        group_history
    )

    result = {}

    for mood, count in counts.items():

        result[mood] = {

            "count": count,

            "percentage": round(
                (count / total) * 100
            )
        }

    return result


def group_favorite_mood(group_history):
    """
    Returns most common group mood.
    """

    counts = group_mood_counts(
        group_history
    )

    if not counts:
        return None

    return max(
        counts,
        key=counts.get
    )


def group_average_mood_score(
    group_history
):
    """
    Returns average statistical mood score
    for the group.
    """

    scores = []

    for entry in group_history or []:

        if not isinstance(entry, dict):
            continue

        mood = entry.get("mood")

        if mood:
            scores.append(
                mood_score(mood)
            )

    if not scores:
        return 0

    return round(
        sum(scores) / len(scores),
        2
    )


def group_member_leaderboard(
    group_history,
    limit=10
):
    """
    Creates a group leaderboard based on
    mood check-in participation.

    Each check-in = 10 XP.
    """

    members = {}

    for entry in group_history or []:

        if not isinstance(entry, dict):
            continue

        user_id = entry.get(
            "user_id"
        )

        if user_id is None:
            continue

        user_id = str(user_id)

        if user_id not in members:

            members[user_id] = {

                "user_id": user_id,

                "username": entry.get(
                    "username",
                    ""
                ),

                "first_name": entry.get(
                    "first_name",
                    ""
                ),

                "checkins": 0,

                "xp": 0
            }

        member = members[user_id]

        member["checkins"] += 1

        member["xp"] += 10

        if entry.get("username"):
            member["username"] = entry[
                "username"
            ]

        if entry.get("first_name"):
            member["first_name"] = entry[
                "first_name"
            ]

    leaderboard = sorted(
        members.values(),
        key=lambda item: (
            item["xp"],
            item["checkins"]
        ),
        reverse=True
    )

    return leaderboard[:limit]


def group_daily_entries(
    group_history,
    target_date=None
):
    """
    Returns group mood entries for a date.
    """

    if target_date is None:
        target_date = _now().date()

    result = []

    for entry in group_history or []:

        if (
            get_entry_date(entry)
            == target_date
        ):
            result.append(entry)

    return result


def group_today_summary(
    group_history
):
    """
    Returns today's group mood summary.
    """

    entries = group_daily_entries(
        group_history
    )

    counts = group_mood_counts(
        entries
    )

    favorite = None

    if counts:

        favorite = max(
            counts,
            key=counts.get
        )

    return {

        "total": len(entries),

        "participants": group_unique_members(
            entries
        ),

        "counts": counts,

        "favorite_mood": favorite,

        "average_score": group_average_mood_score(
            entries
        )
    }


def group_smart_summary(
    group_history
):
    """
    Complete structured group analytics.
    """

    if not group_history:

        return {
            "has_data": False
        }

    favorite = group_favorite_mood(
        group_history
    )

    favorite_info = moods.get_mood_info(
        favorite
    )

    today_summary = group_today_summary(
        group_history
    )

    return {

        "has_data": True,

        "total_checkins":
            group_total_checkins(
                group_history
            ),

        "unique_members":
            group_unique_members(
                group_history
            ),

        "favorite_mood": favorite,

        "favorite_name":
            favorite_info.get(
                "name",
                favorite.title()
                if favorite
                else "Unknown"
            ),

        "favorite_emoji":
            favorite_info.get(
                "emoji",
                "🌸"
            ),

        "average_score":
            group_average_mood_score(
                group_history
            ),

        "distribution":
            group_mood_distribution(
                group_history
            ),

        "today":
            today_summary,

        "leaderboard":
            group_member_leaderboard(
                group_history
            )
    }


# ============================================================
# OVERALL MOOD CHART
# ============================================================

def create_mood_chart(history):
    """Create a polished personal mood distribution chart (PNG BytesIO)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from io import BytesIO

    distribution = mood_distribution(history or [])
    if not distribution:
        return None

    palette = {
        "happy": "#F4B942",
        "sad": "#6C8EBF",
        "angry": "#E76F51",
        "tired": "#9B8AC4",
        "loved": "#E78AB6",
        "okay": "#72B7A1",
    }
    items = []
    for mood, stats in distribution.items():
        info = moods.get_mood_info(mood)
        items.append((
            str(mood),
            f"{info.get('emoji', '🌸')} {info.get('name', str(mood).title())}",
            int(stats.get("count", 0)),
            palette.get(mood, "#8D99AE"),
        ))
    items.sort(key=lambda item: item[2])
    labels = [item[1] for item in items]
    values = [item[2] for item in items]
    colors = [item[3] for item in items]
    total = sum(values)

    fig, ax = plt.subplots(figsize=(9.2, max(4.8, 0.62 * len(items) + 1.7)), dpi=150)
    fig.patch.set_facecolor("#FFF9FC")
    ax.set_facecolor("#FFF9FC")
    bars = ax.barh(labels, values, color=colors, height=0.64, edgecolor="white", linewidth=1.2)
    ax.set_title("Your Mood Garden", loc="left", fontsize=18, fontweight="bold", color="#392B3D", pad=18)
    ax.set_xlabel("Check-ins", color="#6F6572", labelpad=10)
    ax.grid(axis="x", linestyle="--", linewidth=0.7, alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#E9DDE7")
    ax.tick_params(axis="y", length=0, labelsize=10, colors="#4C4050")
    ax.tick_params(axis="x", colors="#6F6572")
    max_value = max(values) if values else 1
    ax.set_xlim(0, max_value * 1.28 + 0.5)
    for bar, value in zip(bars, values):
        percent = round(value / total * 100) if total else 0
        ax.text(value + max_value * 0.025, bar.get_y() + bar.get_height()/2,
                f"{value}  ·  {percent}%", va="center", fontsize=9, color="#4C4050")
    fig.text(0.99, 0.015, f"{total} total check-ins", ha="right", fontsize=9, color="#7B6D7D")
    fig.tight_layout(rect=(0.02, 0.04, 0.99, 0.98))

    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buffer.seek(0)
    buffer.name = "moodbloom_personal_mood_garden.png"
    return buffer

# ============================================================
# WEEKLY MOOD CHART
# ============================================================

def create_weekly_mood_chart(history):
    """Create a premium 7-day personal mood activity chart (PNG BytesIO)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from io import BytesIO

    today = _now().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    order = ["happy", "loved", "okay", "tired", "sad", "angry"]
    palette = {
        "happy": "#F4B942", "loved": "#E78AB6", "okay": "#72B7A1",
        "tired": "#9B8AC4", "sad": "#6C8EBF", "angry": "#E76F51",
    }
    counts = {mood: [0] * 7 for mood in order}
    for entry in history or []:
        if not isinstance(entry, dict):
            continue
        entry_date = get_entry_date(entry)
        mood = entry.get("mood")
        if entry_date in dates and mood in counts:
            counts[mood][dates.index(entry_date)] += 1

    total = sum(sum(values) for values in counts.values())
    if total == 0:
        return None

    labels = [date.strftime("%a\n%d %b") for date in dates]
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=150)
    fig.patch.set_facecolor("#FFF9FC")
    ax.set_facecolor("#FFF9FC")
    bottom = [0] * 7
    for mood in order:
        values = counts[mood]
        if not any(values):
            continue
        info = moods.get_mood_info(mood)
        label = f"{info.get('emoji', '🌸')} {info.get('name', mood.title())}"
        ax.bar(labels, values, bottom=bottom, label=label, color=palette[mood], width=0.66,
               edgecolor="#FFF9FC", linewidth=0.7)
        bottom = [bottom[i] + values[i] for i in range(7)]

    ax.set_title("Your Week in Bloom", loc="left", fontsize=18, fontweight="bold", color="#392B3D", pad=18)
    ax.set_ylabel("Check-ins", color="#6F6572")
    ax.grid(axis="y", linestyle="--", linewidth=0.7, alpha=0.25)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#E9DDE7")
    ax.tick_params(axis="both", length=0, colors="#6F6572")
    ax.legend(frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(0, -0.14), fontsize=8)
    fig.text(0.99, 0.015, f"{total} check-ins across 7 days", ha="right", fontsize=9, color="#7B6D7D")
    fig.tight_layout(rect=(0.02, 0.07, 0.99, 0.98))

    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buffer.seek(0)
    buffer.name = "moodbloom_personal_week.png"
    return buffer

