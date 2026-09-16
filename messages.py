# ============================================================
# MOODBLOOM 4.0 — MESSAGES
# ============================================================

import random

import analytics
import moods


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _mood_display(mood_key, default="No data"):
    if not mood_key:
        return default

    info = moods.MOODS.get(mood_key, {})
    emoji = info.get("emoji", "🌸")
    name = info.get("name", str(mood_key).title())

    return f"{emoji} {name}"


def _trend_text(direction):
    if direction == "up":
        return "📈 Looking more positive"
    if direction == "down":
        return "📉 Recent activity is lower"
    if direction == "stable":
        return "➡️ Relatively stable"
    return "🌱 Building your mood pattern"


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(user_name, history):
    total = analytics.total_checkins(history)
    days = analytics.unique_days(history)
    xp = analytics.get_xp(history)
    level = analytics.get_level(history)
    progress = analytics.get_level_progress(history)
    progress_bar = analytics.get_progress_bar(history)
    xp_to_next = analytics.get_xp_to_next_level(history)
    current_streak = analytics.current_streak(history)
    best_streak = analytics.best_streak(history)
    favorite = analytics.favorite_mood(history)
    favorite_display = _mood_display(favorite, "No mood data yet 🌱")
    latest = analytics.recent_mood(history)
    latest_display = _mood_display(latest, "No check-in yet")
    today_count = len(analytics.today_entries(history))
    achievement_count = len(analytics.achievements(history))
    trend_data = analytics.mood_trend(history)
    trend_text = _trend_text(trend_data["direction"])

    if not history:
        return (
            "🌸 <b>MoodBloom Dashboard</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"👋 Welcome, <b>{user_name}</b>!\n\n"
            "Your mood journey starts here 🌱\n\n"
            "💭 Check in with your mood\n"
            "⭐ Earn XP\n"
            "🔥 Build streaks\n"
            "🏆 Unlock achievements\n\n"
            "Start your first check-in 💖"
        )

    if current_streak >= 7:
        personal = "🔥 Amazing consistency!"
    elif current_streak >= 3:
        personal = "🌱 Nice consistency!"
    elif total >= 10:
        personal = "✨ Building a great habit."
    else:
        personal = "💖 Keep checking in."

    return (
        "🌸 <b>MoodBloom Dashboard</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 Hello, <b>{user_name}</b>!\n"
        f"{personal}\n\n"
        "⭐ <b>LEVEL</b>\n"
        f"Level <b>{level}</b>\n"
        f"{progress_bar}\n"
        f"XP: <b>{progress}/100</b> • Total: <b>{xp}</b>\n"
        f"✨ <b>{xp_to_next}</b> to next level\n\n"
        "💭 <b>MOOD JOURNEY</b>\n"
        f"Total check-ins: <b>{total}</b>\n"
        f"Days tracked: <b>{days}</b>\n"
        f"Latest mood: <b>{latest_display}</b>\n"
        f"Favorite: <b>{favorite_display}</b>\n\n"
        "🔥 <b>STREAK</b>\n"
        f"Current: <b>{current_streak} days</b>\n"
        f"Best: <b>{best_streak} days</b>\n\n"
        "📅 <b>TODAY</b>\n"
        f"Check-ins: <b>{today_count}</b>\n\n"
        "📈 <b>TREND</b>\n"
        f"{trend_text}\n\n"
        "🏆 <b>ACHIEVEMENTS</b>\n"
        f"Unlocked: <b>{achievement_count}</b>"
    )


# ============================================================
# MOOD PROMPT
# ============================================================

def mood_prompt():
    return (
        "💭 <b>How are you feeling right now?</b>\n\n"
        "Choose the mood that feels closest. 🌸"
    )


# ============================================================
# MOOD RESULT
# ============================================================

def mood_result(user_name, mood_key, response, activity):
    info = moods.MOODS.get(mood_key, {})
    emoji = info.get("emoji", "🌸")
    name = info.get("name", mood_key.title())

    return (
        f"{emoji} <b>{name}</b>\n\n"
        f"{response}\n\n"
        f"🌱 <b>Try this:</b>\n"
        f"{activity}\n\n"
        "✨ Thanks for checking in."
    )


# ============================================================
# STATS
# ============================================================

def stats(history):
    if not history:
        return (
            "📊 <b>Mood Statistics</b>\n\n"
            "No mood data yet 🌱\n\n"
            "Make your first check-in 💖"
        )

    total = analytics.total_checkins(history)
    days = analytics.unique_days(history)
    favorite = analytics.favorite_mood(history)
    distribution = analytics.mood_distribution(history)
    average_score = analytics.average_mood_score(history)
    current_streak = analytics.current_streak(history)
    best_streak = analytics.best_streak(history)
    level = analytics.get_level(history)
    xp = analytics.get_xp(history)
    favorite_display = _mood_display(favorite, "No data")

    lines = []
    for mood_key, data in sorted(
        distribution.items(),
        key=lambda x: x[1]["count"],
        reverse=True,
    ):
        display = _mood_display(mood_key)
        count = data["count"]
        percentage = data["percentage"]
        bar_size = min(10, max(1, round(percentage / 10)))
        bar = "🟩" * bar_size
        lines.append(f"{display} {bar} {percentage}% ({count})")

    distribution_text = "\n".join(lines)

    if average_score >= 4:
        score_text = "🌈 Mostly positive"
    elif average_score >= 3:
        score_text = "🌱 Fairly balanced"
    else:
        score_text = "🌿 Take things gently"

    return (
        "📊 <b>Mood Statistics</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📌 <b>OVERVIEW</b>\n"
        f"Total check-ins: <b>{total}</b>\n"
        f"Days tracked: <b>{days}</b>\n"
        f"Favorite mood: <b>{favorite_display}</b>\n\n"
        "😊 <b>DISTRIBUTION</b>\n"
        f"{distribution_text}\n\n"
        "🧠 <b>MOOD SCORE</b>\n"
        f"Average: <b>{average_score}/5</b>\n"
        f"{score_text}\n\n"
        "🔥 <b>STREAKS</b>\n"
        f"Current: <b>{current_streak} days</b>\n"
        f"Best: <b>{best_streak} days</b>\n\n"
        "⭐ <b>PROGRESS</b>\n"
        f"Level: <b>{level}</b>\n"
        f"Total XP: <b>{xp}</b>"
    )


# ============================================================
# INSIGHTS
# ============================================================

def mood_insights(history):
    if not history:
        return (
            "🧠 <b>Smart Insights</b>\n\n"
            "Need a few check-ins to find patterns 🌱"
        )

    data = analytics.smart_insights(history)

    total = data["total"]
    days = data["days"]
    favorite_name = data["favorite_name"]
    favorite_emoji = data["favorite_emoji"]
    recent_mood = data["recent_mood"]
    streak = data["streak"]
    best_streak = data["best_streak"]
    avg_score = data["average_score"]
    trend = data["trend"]

    recent_display = _mood_display(recent_mood, "Unknown")

    direction = trend["direction"]
    if direction == "up":
        trend_text = "📈 Looking more positive"
    elif direction == "down":
        trend_text = "📉 Recent activity is lower"
    elif direction == "stable":
        trend_text = "➡️ Relatively stable"
    else:
        trend_text = "🌱 Building your pattern"

    return (
        "🧠 <b>Smart Insights</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Based on <b>{total}</b> check-ins across <b>{days}</b> days.\n\n"
        f"💖 Most frequent: <b>{favorite_emoji} {favorite_name}</b>\n"
        f"🕐 Latest: <b>{recent_display}</b>\n\n"
        f"🧠 Avg score: <b>{avg_score}/5</b>\n"
        f"📈 Trend: <b>{trend_text}</b>\n\n"
        f"🔥 Streak: <b>{streak} days</b>\n"
        f"🏆 Best: <b>{best_streak} days</b>"
    )


# ============================================================
# FORECAST
# ============================================================

def forecast(history):
    data = analytics.mood_forecast(history)

    if not data.get("has_data"):
        return (
            "🔮 <b>Mood Forecast</b>\n\n"
            f"{data.get('message', '🌱 Keep checking in.')}"
        )

    return (
        "🔮 <b>Mood Forecast</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{data['pattern']}\n\n"
        f"🌸 Dominant: <b>{data['dominant_emoji']} {data['dominant_name']}</b>\n"
        f"📊 Share: <b>{data['percentage']}%</b>\n"
        f"🎯 Confidence: <b>{data['confidence']}</b>\n\n"
        f"🔮 {data['forecast']}\n\n"
        f"{data['disclaimer']}"
    )


# ============================================================
# PROFILE
# ============================================================

def profile(user_name, history):
    total = analytics.total_checkins(history)
    days = analytics.unique_days(history)
    level = analytics.get_level(history)
    xp = analytics.get_xp(history)
    progress = analytics.get_level_progress(history)
    progress_bar = analytics.get_progress_bar(history)
    current_streak = analytics.current_streak(history)
    best_streak = analytics.best_streak(history)
    favorite = analytics.favorite_mood(history)
    latest = analytics.recent_mood(history)
    achievement_count = len(analytics.achievements(history))
    favorite_display = _mood_display(favorite, "Not available")
    latest_display = _mood_display(latest, "No check-in yet")

    return (
        "👤 <b>MoodBloom Profile</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌸 <b>Name:</b> {user_name}\n\n"
        "⭐ <b>LEVEL</b>\n"
        f"Level <b>{level}</b>\n"
        f"{progress_bar}\n"
        f"XP: <b>{progress}/100</b> • Total: <b>{xp}</b>\n\n"
        "💭 <b>JOURNEY</b>\n"
        f"Total: <b>{total}</b>\n"
        f"Days: <b>{days}</b>\n"
        f"Favorite: <b>{favorite_display}</b>\n"
        f"Latest: <b>{latest_display}</b>\n\n"
        "🔥 <b>STREAK</b>\n"
        f"Current: <b>{current_streak} days</b>\n"
        f"Best: <b>{best_streak} days</b>\n\n"
        "🏆 <b>ACHIEVEMENTS</b>\n"
        f"Unlocked: <b>{achievement_count}</b>"
    )


# ============================================================
# WEEKLY
# ============================================================

def weekly(history):
    if not history:
        return "📈 <b>Weekly Analysis</b>\n\nNo data yet 🌱"

    entries = analytics.weekly_entries(history)

    if not entries:
        return "📈 <b>Weekly Analysis</b>\n\nNo check-ins in last 7 days 🌱"

    counts = analytics.weekly_counts(history)
    distribution = analytics.weekly_mood_distribution(history)
    total = len(entries)
    average_score = analytics.average_mood_score(entries)
    favorite = max(counts, key=counts.get) if counts else None
    favorite_display = _mood_display(favorite, "No data")

    lines = []
    for mood_key, data in sorted(
        distribution.items(),
        key=lambda x: x[1]["count"],
        reverse=True,
    ):
        display = _mood_display(mood_key)
        count = data["count"]
        percentage = data["percentage"]
        lines.append(f"{display} — {count} ({percentage}%)")

    distribution_text = "\n".join(lines)

    trend = analytics.mood_trend(history)
    trend_text = _trend_text(trend["direction"])
    current_streak = analytics.current_streak(history)
    best_streak = analytics.best_streak(history)

    if average_score >= 4:
        score_text = "🌈 Mostly positive"
    elif average_score >= 3:
        score_text = "🌱 Fairly balanced"
    else:
        score_text = "🌿 Take it gently"

    return (
        "📈 <b>Weekly Analysis</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📅 <b>LAST 7 DAYS</b>\n"
        f"Total: <b>{total}</b>\n"
        f"Most common: <b>{favorite_display}</b>\n\n"
        "😊 <b>BREAKDOWN</b>\n"
        f"{distribution_text}\n\n"
        "🧠 <b>AVG SCORE</b>\n"
        f"Score: <b>{average_score}/5</b>\n"
        f"{score_text}\n\n"
        "📊 <b>TREND</b>\n"
        f"{trend_text}\n\n"
        "🔥 <b>STREAK</b>\n"
        f"Current: <b>{current_streak} days</b>\n"
        f"Best: <b>{best_streak} days</b>"
    )


# ============================================================
# TODAY
# ============================================================

def today(history):
    entries = analytics.today_entries(history)

    if not entries:
        return (
            "📅 <b>Today's Mood</b>\n\n"
            "No check-in yet 🌱\n\n"
            "Take a moment and record how you feel."
        )

    lines = ["📅 <b>Today's Check-ins</b>", ""]
    for entry in entries:
        mood = entry.get("mood", "unknown")
        display = _mood_display(mood, "Unknown")
        time = entry.get("time", "")
        lines.append(display)
        if time:
            lines.append(f"   🕐 {time}")

    lines.append("")
    lines.append(f"💭 Total: <b>{len(entries)}</b>")

    return "\n".join(lines)


# ============================================================
# HISTORY
# ============================================================

def mood_history(history, limit=10):
    if not history:
        return (
            "📜 <b>Mood History</b>\n\n"
            "No moods recorded yet 🌱"
        )

    recent = history[-limit:]
    lines = []

    for index, entry in enumerate(reversed(recent), start=1):
        mood_key = entry.get("mood")
        display = _mood_display(mood_key, "Unknown")
        date = entry.get("date", "Unknown")
        time = entry.get("time", "")
        lines.append(f"<b>{index}.</b> {display}\n   📅 {date}\n   🕐 {time}")

    history_text = "\n\n".join(lines)

    total = analytics.total_checkins(history)
    streak = analytics.current_streak(history)
    best_streak = analytics.best_streak(history)
    xp = analytics.get_xp(history)
    level = analytics.get_level(history)

    return (
        "📜 <b>Mood History</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Showing latest <b>{len(recent)}</b> of <b>{total}</b>\n\n"
        f"{history_text}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🔥 Streak: <b>{streak} days</b>\n"
        f"🏆 Best: <b>{best_streak} days</b>\n"
        f"⭐ Level: <b>{level}</b>\n"
        f"✨ XP: <b>{xp}</b>"
    )


# ============================================================
# STREAK
# ============================================================

def streak(history):
    current = analytics.current_streak(history)
    best = analytics.best_streak(history)

    if current == 0:
        msg = "Start a new streak today 🌱"
    elif current < 3:
        msg = "Keep going! 🌸"
    elif current < 7:
        msg = "Nice consistency! 🔥"
    else:
        msg = "Amazing consistency! 🔥"

    return (
        "🔥 <b>Streak</b>\n\n"
        f"🔥 Current: <b>{current} days</b>\n"
        f"🏆 Best: <b>{best} days</b>\n\n"
        f"{msg}"
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

def achievement_message(history):
    total = analytics.total_checkins(history)
    best_streak = analytics.best_streak(history)
    current_streak = analytics.current_streak(history)

    achievements_list = [
        ("🌱 First Check-in", total >= 1),
        ("🌸 5 Check-ins", total >= 5),
        ("✨ 10 Check-ins", total >= 10),
        ("💎 25 Check-ins", total >= 25),
        ("👑 50 Check-ins", total >= 50),
        ("🏆 100 Check-ins", total >= 100),
        ("🔥 3-Day Streak", best_streak >= 3),
        ("🔥🔥 7-Day Streak", best_streak >= 7),
        ("🚀 14-Day Streak", best_streak >= 14),
        ("👑 30-Day Streak", best_streak >= 30),
    ]

    unlocked = sum(1 for _, status in achievements_list if status)
    total_a = len(achievements_list)
    percent = round((unlocked / total_a) * 100)
    filled = round(percent / 10)
    bar = "🟩" * filled + "⬜" * (10 - filled)

    lines = []
    for name, status in achievements_list:
        lines.append(f"{'✅' if status else '🔒'} {name}")

    achievement_text = "\n".join(lines)

    xp = analytics.get_xp(history)
    level = analytics.get_level(history)
    progress = analytics.get_level_progress(history)
    level_bar = analytics.get_progress_bar(history)

    return (
        "🏆 <b>Achievements</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"⭐ <b>Level {level}</b>\n"
        f"{level_bar}\n"
        f"XP: <b>{progress}/100</b> • Total: <b>{xp}</b>\n\n"
        f"🏆 <b>Progress</b>\n"
        f"{bar}\n"
        f"<b>{unlocked}/{total_a}</b> unlocked ({percent}%)\n\n"
        f"{achievement_text}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"🔥 Streak: <b>{current_streak} days</b>\n"
        f"🏅 Best: <b>{best_streak} days</b>\n"
        f"💭 Total: <b>{total}</b>"
    )


# ============================================================
# QUOTE / MOTIVATE
# ============================================================

def quote():
    return (
        "✨ <b>Today's Quote</b>\n\n"
        f"<i>{random.choice(moods.QUOTES)}</i>\n\n"
        "🌸 Keep this thought with you."
    )


def motivate():
    return (
        "🔥 <b>A Little Motivation</b>\n\n"
        f"{random.choice(moods.MOTIVATIONS)}\n\n"
        "💖 One small step at a time."
    )


def random_activity():
    activity = random.choice(moods.ACTIVITIES)
    return (
        "🎲 <b>Random Activity</b>\n\n"
        f"🌱 {activity}\n\n"
        "Give it a try if you feel like it ✨"
    )


# ============================================================
# ABOUT
# ============================================================

def about():
    return (
        "🌸 <b>About MoodBloom</b>\n\n"
        "MoodBloom is your personal mood companion.\n\n"
        "💭 Track moods\n"
        "📊 View patterns\n"
        "📈 Weekly trends\n"
        "🔮 Mood forecasts\n"
        "🔥 Build consistency\n"
        "🏆 Unlock achievements\n"
        "⭐ Earn XP\n"
        "Made with Python 🐍 + Telegram 💙"
    )


# ============================================================
# HELP
# ============================================================

def help_message():
    return (
        "🌸 <b>MoodBloom Help</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "💭 <b>MOOD</b>\n"
        "/mood — Record mood\n"
        "/daily — Today's overview\n\n"
        "📊 <b>JOURNEY</b>\n"
        "/stats — Statistics\n"
        "/today — Today's moods\n"
        "/weekly — Weekly analysis\n"
        "/history — Recent history\n"
        "/streak — Streak\n"
        "/achievements — Achievements\n"
        "/insights — Insights\n"
        "/profile — Profile\n"
        "/forecast — Forecast\n\n"
        "📈 <b>VISUALS</b>\n"
        "/chart — Mood chart\n"
        "/weeklychart — 7-day chart\n\n"
        "✨ <b>EXTRA</b>\n"
        "/quote — Quote\n"
        "/motivate — Motivation\n"
        "/random — Random\n"
        "⚙️ <b>SETTINGS</b>\n"
        "/settings — Notification settings\n"
        "/remind — Set reminder\n"
        "/remindoff — Disable\n\n"
        "🏠 <b>NAVIGATION</b>\n"
        "/start — Dashboard\n"
        "/menu — Main menu\n"
        "/about — About\n"
        "/help — Help"
    )


# ============================================================
# GROUP DASHBOARD
# ============================================================

def group_dashboard(group_name="This Group", member_count=0):
    return (
        "👥 <b>Group Dashboard</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌸 <b>Group:</b> {group_name}\n"
        f"👤 <b>Members:</b> {member_count}\n\n"
        "💭 <b>GROUP MOOD</b>\n"
        "Check how everyone feels.\n\n"
        "📊 <b>INSIGHTS</b>\n"
        "See group patterns.\n\n"
        "🏆 <b>COMMUNITY</b>\n"
        "Leaderboard & streaks.\n\n"
        "🎮 <b>FUN</b>\n"
        "Games and questions.\n\n"
        "🛡️ <b>ADMIN</b>\n"
        "Welcome, reminders, settings.\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🌈 Let's bloom together!"
    )


# ============================================================
# GROUP MOOD
# ============================================================

def group_mood_prompt():
    return (
        "😊 <b>Group Mood Check-in</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "How are you feeling right now?\n\n"
        "Your response contributes to the group's mood picture 🌸"
    )


def group_mood_result(user_name, mood_key):
    info = moods.MOODS.get(mood_key, {})
    emoji = info.get("emoji", "🌸")
    name = info.get("name", str(mood_key).title())

    return (
        f"{emoji} <b>Mood recorded!</b>\n\n"
        f"Hey <b>{user_name}</b>, your mood is:\n"
        f"<b>{emoji} {name}</b>\n\n"
        "🌸 Thanks for contributing!"
    )


# ============================================================
# GROUP REPORT
# ============================================================

def group_report(group_name="This Group", total_checkins=0, member_count=0,
                 dominant_mood=None, average_score=None):
    dominant_display = _mood_display(dominant_mood, "No data yet 🌱")

    if average_score is None:
        score_text = "No data yet"
    else:
        score_text = f"{average_score}/5"

    if total_checkins == 0:
        activity = "No check-ins yet. Be the first! 🌱"
    elif total_checkins < 5:
        activity = "Just getting started! 🌱"
    elif total_checkins < 20:
        activity = "Becoming active! ✨"
    else:
        activity = "Very active! 🔥"

    return (
        "📊 <b>Group Report</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>{group_name}</b>\n\n"
        "📌 <b>OVERVIEW</b>\n"
        f"👤 Members: <b>{member_count}</b>\n"
        f"💭 Check-ins: <b>{total_checkins}</b>\n\n"
        "😊 <b>GROUP MOOD</b>\n"
        f"Most common: <b>{dominant_display}</b>\n"
        f"Avg score: <b>{score_text}</b>\n\n"
        "📈 <b>ACTIVITY</b>\n"
        f"{activity}"
    )


# ============================================================
# GROUP CHART
# ============================================================

def group_chart(group_name="This Group", distribution=None):
    if not distribution:
        return (
            "📈 <b>Group Chart</b>\n\n"
            "🌱 Not enough data yet.\n\n"
            "Ask members to check in!"
        )

    lines = []
    for mood_key, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        display = _mood_display(mood_key, "Unknown")
        try:
            count_value = int(count)
        except (TypeError, ValueError):
            count_value = 0
        bar_length = min(10, max(1, count_value))
        bar = "🟩" * bar_length
        lines.append(f"{display} {bar} <b>{count_value}</b>")

    chart_text = "\n".join(lines)

    return (
        "📈 <b>Group Mood Chart</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>{group_name}</b>\n\n"
        f"{chart_text}"
    )


# ============================================================
# GROUP LEADERBOARD
# ============================================================

def group_leaderboard(leaderboard=None):
    if not leaderboard:
        return (
            "🏆 <b>Group Leaderboard</b>\n\n"
            "🌱 No data yet.\n\n"
            "Start checking in to earn points!"
        )

    lines = []
    medals = ["🥇", "🥈", "🥉"]

    for index, item in enumerate(leaderboard, start=1):
        if isinstance(item, dict):
            name = item.get("name", "Member")
            points = item.get("points", item.get("xp", 0))
            checkins = item.get("checkins", 0)
        else:
            try:
                name, points = item
            except (TypeError, ValueError):
                name, points = str(item), 0
            checkins = 0

        rank = medals[index - 1] if index <= 3 else f"<b>{index}.</b>"

        lines.append(f"{rank} {name} — ⭐ <b>{points}</b> • 💭 {checkins}")

    leaderboard_text = "\n".join(lines)

    return (
        "🏆 <b>Group Leaderboard</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{leaderboard_text}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⭐ Check in • Earn • Climb!"
    )


# ============================================================
# GROUP STREAK
# ============================================================

def group_streak(current_streak=0, best_streak=0):
    if current_streak == 0:
        msg = "🌱 Start today's check-in!"
    elif current_streak < 3:
        msg = "🌸 Nice start!"
    elif current_streak < 7:
        msg = "🔥 Building momentum!"
    elif current_streak < 30:
        msg = "🚀 Amazing consistency!"
    else:
        msg = "👑 Legendary!"

    return (
        "🔥 <b>Group Streak</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥 Current: <b>{current_streak} days</b>\n"
        f"🏆 Best: <b>{best_streak} days</b>\n\n"
        f"{msg}\n\n"
        "💭 Encourage members to check in daily!"
    )


# ============================================================
# DAILY QUESTION
# ============================================================

DAILY_QUESTIONS = [
    "🌈 What made you smile today?",
    "💭 What are you grateful for?",
    "✨ What are you looking forward to?",
    "🌱 What small win did you have?",
    "☀️ What made today better?",
    "🎯 What goal are you working on?",
    "💖 What do you appreciate about friends?",
    "🧠 What did you learn recently?",
    "🎵 What song matches your mood?",
    "🍀 If today had a color, what would it be?",
    "🚀 What do you want to accomplish this week?",
    "🌸 One positive thing happening in your life?",
]


def daily_question():
    question = random.choice(DAILY_QUESTIONS)
    return (
        "❓ <b>Daily Question</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{question}\n\n"
        "💬 Share your answer!"
    )


# ============================================================
# GROUP GAMES
# ============================================================

def group_games():
    return (
        "🎮 <b>Group Games</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🎲 <b>Random Game</b>\nSurprise activity!\n\n"
        "🤔 <b>Would You Rather</b>\nTwo fun choices.\n\n"
        "💬 <b>Daily Question</b>\nStart conversation."
    )


RANDOM_GROUP_GAMES = [
    "🎯 <b>Quick Challenge</b>\n\nDescribe mood with 3 emojis!",
    "🎵 <b>Music Challenge</b>\n\nSend a song matching your mood.",
    "🌈 <b>Color Challenge</b>\n\nWhat color is your mood?",
    "✨ <b>Positive Challenge</b>\n\nSay one nice thing about someone.",
    "😂 <b>Emoji Challenge</b>\n\nDescribe your day with 5 emojis.",
    "💭 <b>One Word</b>\n\nDescribe your mood in one word.",
]


def random_group_game():
    return (
        "🎮 <b>Random Game</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{random.choice(RANDOM_GROUP_GAMES)}"
    )


WOULD_YOU_RATHER = [
    "🌅 Perfect morning daily\nOR\n🌙 Perfect night daily?",
    "🎵 Favorite song forever\nOR\n🎬 Favorite movie forever?",
    "✈️ Travel anywhere instantly\nOR\n💰 Never worry about money?",
    "🧠 Always know the answer\nOR\n✨ Always know the question?",
    "🌈 One amazing day weekly\nOR\n🌸 Good days every day?",
]


def would_you_rather():
    question = random.choice(WOULD_YOU_RATHER)
    return (
        "🤔 <b>Would You Rather?</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{question}\n\n"
        "💬 Reply with your choice!"
    )


# ============================================================
# GROUP WELCOME — UPDATED
# ============================================================

def group_welcome(user_name, group_name="our group", custom_message=None):
    """Small, cute, group-friendly welcome. No bot branding or quiz wording."""
    if custom_message:
        try:
            return custom_message.format(name=user_name, group=group_name)
        except Exception:
            pass

    return (
        f"🌸 Welcome, {user_name}!\n\n"
        "💖 Glad to have you here.\n"
        "🌿 Feel free to join the chat and have a lovely time!"
    )


def group_goodbye(user_name, group_name="our group", custom_message=None):
    """Small, warm goodbye. No bot branding."""
    if custom_message:
        try:
            return custom_message.format(name=user_name, group=group_name)
        except Exception:
            pass

    return (
        f"👋 Bye, {user_name}!\n"
        "🌸 Take care and keep smiling.\n"
        "You’ll be missed here. 💖"
    )


# ============================================================
# GROUP WELCOME SETTINGS
# ============================================================

def group_welcome_settings(enabled=False):
    status = "🟢 Enabled" if enabled else "🔴 Disabled"

    return (
        "👋 <b>Welcome Settings</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Status: <b>{status}</b>\n\n"
        "When enabled, MoodBloom greets new members.\n\n"
        "🌸 Make every new member feel welcome!"
    )


# ============================================================
# GROUP ADMIN
# ============================================================

def group_admin():
    return (
        "🛡️ <b>Group Admin Center</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Manage MoodBloom for this group.\n\n"
        "👋 <b>Welcome</b> — Manage welcome messages\n"
        "✏️ <b>Customize</b> — Custom welcome/goodbye\n"
        "🛡️ <b>Moderation</b> — Group behavior\n"
        "⏰ <b>Reminders</b> — Group mood reminders\n"
        "📢 <b>Announcement</b> — Send announcements\n"
        "⚙️ <b>Settings</b> — Group preferences\n\n"
        "🔐 Admin-only controls."
    )


# ============================================================
# GROUP MODERATION
# ============================================================

def group_moderation():
    return (
        "🛡️ <b>Group Moderation</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "MoodBloom moderation controls:\n\n"
        "🔇 Reduce unnecessary bot messages\n"
        "🚫 Control repeated interactions\n"
        "🧹 Manage bot-generated content\n"
        "⚙️ Configure group behavior\n\n"
        "💡 Telegram permissions are checked before actions."
    )


# ============================================================
# GROUP REMINDER
# ============================================================

def group_reminder():
    return (
        "⏰ <b>Group Mood Reminder</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Choose when MoodBloom reminds the group:\n\n"
        "🌅 Morning — Start the day\n"
        "☀️ Afternoon — Midday check-in\n"
        "🌆 Evening — Reflect on the day\n"
        "🌙 Night — Final check-in\n\n"
        "🌸 A small reminder keeps the group active."
    )


# ============================================================
# GROUP SETTINGS
# ============================================================

def group_settings(group_name="This Group"):
    return (
        "⚙️ <b>Group Settings</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Group: <b>{group_name}</b>\n\n"
        "Available settings:\n\n"
        "👋 Welcome Messages\n"
        "✏️ Custom Welcome/Goodbye\n"
        "⏰ Group Reminders\n"
        "🎮 Games\n"
        "❓ Daily Questions\n"
        "📊 Group Reports\n"
        "🏆 Leaderboard\n\n"
        "🔐 Some settings need admin permissions."
    )


# ============================================================
# GROUP ANNOUNCEMENT
# ============================================================

def group_announcement():
    return (
        "📢 <b>Announcement</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Send an announcement to the group.\n\n"
        "💡 Examples:\n"
        "• New weekly challenge\n"
        "• Streak milestone\n"
        "• New feature\n"
        "• Activity reminder\n\n"
        "🌸 Keep it useful and positive."
    )


# ============================================================
# GROUP HELP
# ============================================================

def group_help():
    return (
        "❓ <b>Group Help</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👥 <b>FEATURES</b>\n\n"
        "😊 Group Mood — Share mood\n"
        "📊 Report — Group statistics\n"
        "📈 Chart — Mood distribution\n"
        "🏆 Leaderboard — Compare\n"
        "🔥 Streak — Track consistency\n"
        "❓ Question — Daily question\n"
        "🎮 Games — Have fun\n\n"
        "🛡️ <b>ADMIN</b>\n\n"
        "👋 Welcome settings\n"
        "✏️ Custom messages\n"
        "⏰ Reminders\n"
        "📢 Announcements\n"
        "⚙️ Settings\n\n"
        "💡 Admin-only features are protected."
    )


# ============================================================
# GROUP EMPTY STATE
# ============================================================

def group_empty_state():
    return (
        "🌱 <b>Group is just getting started!</b>\n\n"
        "Not enough data yet.\n\n"
        "Ask everyone to make their first 💭 Mood Check-in.\n\n"
        "Once members participate:\n\n"
        "📊 Group reports\n"
        "📈 Mood charts\n"
        "🏆 Leaderboards\n"
        "🔥 Group streaks\n\n"
        "🌸 Let's bloom together!"
    )


# ============================================================
# ADMIN ONLY
# ============================================================

def admin_only_message():
    return (
        "🔐 <b>Admin Only</b>\n\n"
        "This MoodBloom feature is for group admins.\n\n"
        "👤 If you're an admin, make sure the bot has permission."
    )


# ============================================================
# GROUP SUCCESS
# ============================================================

def group_success(title, message):
    return (
        f"✅ <b>{title}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{message}\n\n"
        "🌸 MoodBloom Group Edition"
    )


# ============================================================
# CUSTOM WELCOME/GOODBYE — NEW HELPERS
# ============================================================

def custom_welcome_prompt():
    return (
        "👋 <b>Custom Welcome Message</b>\n\n"
        "Send your custom welcome message now.\n\n"
        "Placeholders:\n"
        "• <code>{name}</code> → new member's name\n"
        "• <code>{group}</code> → group name\n\n"
        "Example:\n"
        "<code>Welcome {name} to {group}! 🌸</code>\n\n"
        "Send /cancel to cancel."
    )


def custom_goodbye_prompt():
    return (
        "👋 <b>Custom Goodbye Message</b>\n\n"
        "Send your custom goodbye message now.\n\n"
        "Placeholders:\n"
        "• <code>{name}</code> → member's name\n"
        "• <code>{group}</code> → group name\n\n"
        "Example:\n"
        "<code>Bye {name}! Take care 🌸</code>\n\n"
        "Send /cancel to cancel."
    )


def custom_message_saved(label, preview):
    return (
        f"✅ <b>{label} message saved!</b>\n\n"
        f"<b>Preview:</b>\n{preview}"
    )


def custom_preview_text(welcome, goodbye):
    return (
        "👀 <b>Preview</b>\n\n"
        "<b>Welcome:</b>\n"
        f"{welcome}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Goodbye:</b>\n"
        f"{goodbye}"
    )


def group_customize_menu():
    return (
        "✏️ <b>Customize Messages</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Customize welcome and goodbye messages for your group.\n\n"
        "👋 <b>Welcome</b> — Set welcome message\n"
        "👋 <b>Goodbye</b> — Set goodbye message\n"
        "👀 <b>Preview</b> — See how it looks\n"
        "🔄 <b>Reset</b> — Restore defaults"
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "dashboard", "mood_prompt", "mood_result",
    "stats", "mood_insights", "forecast", "profile",
    "weekly", "today", "mood_history",
    "streak", "achievement_message",
    "quote", "motivate", "random_activity",
    "about", "help_message",

    # Group
    "group_dashboard", "group_mood_prompt", "group_mood_result",
    "group_report", "group_chart", "group_leaderboard",
    "group_streak", "daily_question",
    "group_games", "random_group_game", "would_you_rather",
    "group_welcome", "group_goodbye",
    "group_welcome_settings", "group_admin", "group_moderation",
    "group_reminder", "group_settings", "group_announcement",
    "group_help", "group_empty_state",
    "admin_only_message", "group_success",

    # Custom
    "custom_welcome_prompt", "custom_goodbye_prompt",
    "custom_message_saved", "custom_preview_text",
    "group_customize_menu",
]