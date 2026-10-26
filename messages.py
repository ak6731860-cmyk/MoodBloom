"""User-facing message builders used by the MoodBloom bot."""

import random


_QUOTES = [
    "🌸 Every small step you take toward yourself matters.",
    "🌱 You are allowed to grow at your own pace.",
    "✨ Progress can be quiet and still be real.",
    "💛 Be as kind to yourself as you are to the people you love.",
]

_MOTIVATION = [
    "🔥 You do not need to be perfect. Just keep moving forward.",
    "🌿 One gentle step is still a step. Keep going.",
    "✨ You have made it through hard days before. Take today one moment at a time.",
    "💪 Your effort counts, even when nobody else can see it.",
]

_DAILY_QUESTIONS = [
    "What is one small thing that made you smile today?",
    "If your mood were weather, what would the forecast be?",
    "What is something kind you would like to hear today?",
    "Which song matches your energy right now?",
    "What is one little win you had this week?",
]

_GROUP_GAMES = [
    "🎲 Group game time! Pick a prompt and let everyone join in.",
    "🌸 A little group fun can brighten the day. Choose a game below!",
]

_RANDOM_GAMES = [
    "🎭 Quick round: describe your day using only three emojis.",
    "🧠 Quick round: name one tiny thing you are grateful for today.",
    "🎨 Quick round: invent a title for the group's day so far.",
    "🌈 Quick round: share one song that lifts your mood.",
]

_WOULD_YOU_RATHER = [
    "Would you rather explore a quiet forest or watch the sunrise by the sea?",
    "Would you rather have a cozy movie night or a spontaneous day trip?",
    "Would you rather instantly learn a new language or a musical instrument?",
    "Would you rather spend a day with no notifications or no chores?",
]


def quote():
    return random.choice(_QUOTES)


def motivate():
    return random.choice(_MOTIVATION)


def group_dashboard(group_name, member_count):
    return (
        f"🌸 {group_name}\n\n"
        f"👥 Members: {member_count}\n"
        "Check in with your mood, encourage one another, and grow together."
    )


def group_mood_prompt():
    return "💭 How are you feeling today? Choose the mood that fits best."


def group_mood_result(name, mood):
    return f"🌷 {name} checked in as feeling {str(mood).replace('_', ' ')}. Thanks for sharing."


def group_report(group_name, total_checkins, member_count, dominant_mood, average_score):
    mood_label = str(dominant_mood or "No check-ins yet").replace("_", " ").title()
    score = "N/A" if average_score is None else f"{average_score}/5"
    return (
        f"📊 Group report: {group_name}\n\n"
        f"👥 Members: {member_count}\n"
        f"🌱 Mood check-ins: {total_checkins}\n"
        f"💭 Most common mood: {mood_label}\n"
        f"⭐ Average mood score: {score}"
    )


def group_leaderboard(members):
    if not members:
        return "🏆 Group leaderboard\n\nNo points yet. Check in to get things started!"

    lines = ["🏆 Group leaderboard", ""]
    for position, member in enumerate(members, start=1):
        name = member.get("name") or member.get("username") or "Member"
        points = member.get("points", 0)
        lines.append(f"{position}. {name} · {points} points")
    return "\n".join(lines)


def group_streak(current, best):
    return (
        "🔥 Group mood streak\n\n"
        f"Current streak: {current} day(s)\n"
        f"Best streak: {best} day(s)\n\n"
        "A small check-in each day keeps the group connected."
    )


def daily_question():
    return random.choice(_DAILY_QUESTIONS)


def group_games():
    return random.choice(_GROUP_GAMES)


def random_group_game():
    return random.choice(_RANDOM_GAMES)


def would_you_rather():
    return "🤔 Would you rather…\n\n" + random.choice(_WOULD_YOU_RATHER)


def admin_only_message():
    return "🔒 This action is available to group admins only."


def group_admin():
    return "🛠️ Group admin tools\n\nChoose a setting to manage your group."


def group_moderation():
    return "🛡️ Group moderation\n\nReview the available tools and choose the action you need."


def group_welcome_settings(enabled):
    status = "enabled" if enabled else "disabled"
    return f"👋 Welcome messages are currently {status}."


def group_settings(group_name):
    return f"⚙️ Settings for {group_name}\n\nChoose an option below to update this group's experience."


def group_success(title, detail):
    return f"✅ {title}\n\n{detail}"


def group_welcome(name, group_name):
    return f"🌸 Welcome, {name}, to {group_name}! We are glad you are here."


def group_reminder():
    return (
        "⏰ Group reminder settings\n\n"
        "Set a daily check-in time for the group, or turn the reminder off."
    )


def group_help():
    return (
        "🌸 MoodBloom group help\n\n"
        "Use the group menu to check in, view the group report and streak, "
        "play a quick game, or manage reminders and welcome settings."
    )


def group_goodbye(name, group_name, custom_message=None):
    if custom_message:
        try:
            return custom_message.format(name=name, group=group_name)
        except (IndexError, KeyError, ValueError):
            return custom_message
    return f"🌷 {name} has left {group_name}. Wishing them well on their next chapter."
