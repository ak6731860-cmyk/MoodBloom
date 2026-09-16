import random
from datetime import datetime

import config


# ============================================================
# MOODBLOOM 4.0 — MORNING WISHES
# ============================================================
# Safe, reusable morning message system.
#
# Existing public functions preserved:
#   get_morning_wish()
#   get_random_morning_wish()
#   get_morning_wish_count()
#
# V4 additions:
#   get_mood_morning_wish()
#   get_goal_morning_wish()
#   get_reward_morning_wish()
#   get_birthday_morning_wish()
#   get_journey_morning_wish()
#   get_group_morning_wish()
#   get_personalized_morning_wish()
#   get_morning_wish_for_user()
# ============================================================


# ============================================================
# BASIC MORNING WISHES
# ============================================================

MORNING_WISHES = [

    "🌅 Good morning! Aaj ka din aapke liye beautiful ho. 🌸✨",

    "☀️ Good morning, Bloom! Nayi subah, nayi energy, nayi possibilities. 🌷",

    "🌸 Suprabhat! Aaj thoda smile kijiye, thoda relax kijiye aur apna best dijiye. 💫",

    "☀️ Rise & Bloom! 🌱 Aaj ka din kal se thoda better banate hain. ✨",

    "🌷 Good morning! May your day be peaceful, productive and full of little happy moments. 💖",

    "🌤️ Nayi subah aa gayi! Jo bhi plan hai, ek small step se start kijiye. 🌱",

    "💫 Good morning! Aaj khud ke liye bhi thoda time zaroor rakhiye. 🌸",

    "🌼 Morning! Aapka aaj ka mood kis colour ka hoga? 🌈",

    "☀️ Good morning! Aaj unnecessary stress ko thoda side mein rakhte hain. 😌🌸",

    "🌸 Another beautiful morning, another chance to bloom. Good morning! 🌷",

    "🌞 Good morning! Aaj ka goal simple hai — smile more, stress less. ✨",

    "🌱 New day. New energy. New chances. Keep blooming! 🌸",

    "☀️ Good morning! Aaj kuch chhota sa achha zaroor kijiye — apne liye. 💖",

    "🌷 Morning Bloom! Aaj ka din calm bhi ho aur productive bhi. ✨",

    "🌈 Good morning! Har din perfect nahi hota, lekin har din mein kuch achha zaroor ho sakta hai. 🌸",

    "☕ Good morning! Pehle ek deep breath... phir day officially start. 😌✨",

    "🌻 Rise and shine! Aaj ki story abhi likhi jaani baaki hai. 📖✨",

    "💖 Good morning! Kisi aur se compare nahi — bas kal wale version se better banna hai. 🌱",

    "🌤️ A fresh morning has arrived. Take it easy, take it positively. 🌸",

    "🌸 Good morning from MoodBloom! Aaj positivity thodi extra rakhiye. ✨"
]


# ============================================================
# MOOD-BASED MORNING WISHES
# ============================================================

MOOD_MORNING_WISHES = {

    "happy": [

        "😊 Good morning! Aaj ki happy energy ko poore din carry kijiye. 🌸✨",

        "🌞 Morning! Aapki smile aaj ka best mood booster ho sakti hai. 💛",

        "🌈 Good morning! Jo happiness feel ho rahi hai, usse enjoy kijiye. 🌷"

    ],

    "sad": [

        "🌸 Good morning! Aaj khud par thoda extra gentle rahiye. Small steps bhi enough hain. 💖",

        "🌤️ Good morning! Har din same nahi hota. Aaj bas ek peaceful step se start kijiye. 🌱",

        "☀️ Morning! Aapko aaj sab kuch solve karna zaroori nahi hai. Take it easy. 🌷"

    ],

    "angry": [

        "🌅 Good morning! Aaj ek deep breath ke saath fresh start kijiye. 😌🌸",

        "☀️ Morning Bloom! Aaj reactions se pehle thoda pause, phir response. 🌱",

        "🌷 Good morning! Calm mind ke saath day ko restart karte hain. ✨"

    ],

    "tired": [

        "☕ Good morning! Aaj apni energy ko wisely use kijiye. Har cheez immediately karna zaroori nahi. 🌸",

        "🌤️ Morning! Slow start bhi ek valid start hai. Take care of your energy. 🌱",

        "🌷 Good morning! Aaj productivity ke saath rest ko bhi importance dijiye. 💖"

    ],

    "loved": [

        "❤️ Good morning! Aaj jo love aur warmth feel ho rahi hai, use cherish kijiye. 🌸",

        "🌹 Morning Bloom! Aapke din mein aur bhi beautiful moments aayein. ✨",

        "💖 Good morning! Aaj kindness aur warmth spread karte hain. 🌷"

    ],

    "okay": [

        "🌼 Good morning! Normal days bhi beautiful ho sakte hain. Aaj ek small happy moment find kijiye. ✨",

        "☀️ Morning! Aaj ka mood okay hai — ab ise thoda better banate hain. 🌱",

        "🌸 Good morning! No pressure, bas one step at a time. 💫"

    ]
}


# ============================================================
# GOAL MORNING WISHES
# ============================================================

GOAL_MORNING_WISHES = [

    "🎯 Good morning! Aaj ke Daily Goals ko ek-ek karke complete karte hain. 🌱",

    "🌸 New day, new goals! Chhoti progress bhi progress hoti hai. ✨",

    "🌞 Morning Bloom! Aaj ke goals complete karke apna XP grow kijiye. ⭐",

    "🎯 Good morning! Aaj ek goal se start kijiye — momentum khud banega. 🌷",

    "🌱 Your Bloom Journey continues today. Let's make some progress! ✨"
]


# ============================================================
# REWARD MORNING WISHES
# ============================================================

REWARD_MORNING_WISHES = [

    "🎁 Good morning! Aaj ka Daily Reward aapka wait kar raha hai. ✨",

    "🌸 Morning Bloom! Daily Reward claim karna mat bhooliyega. 🎁",

    "⭐ Good morning! Aaj reward bhi hai aur XP grow karne ka chance bhi. 🌱",

    "🎁 New day, new reward! Let's keep the Bloom streak alive. 🔥",

    "🌞 Good morning! Aaj ka little reward aapki daily motivation ban sakta hai. 🌷"
]


# ============================================================
# BIRTHDAY MORNING WISHES
# ============================================================

BIRTHDAY_MORNING_WISHES = [

    "🎂 Good morning! Aaj ka din extra special hai. Birthday vibes are here! 🎉🌸",

    "🎉 Good morning! Aaj celebration, smiles aur beautiful memories ka din hai. 🎂✨",

    "🌷 Birthday morning! Aaj ka har moment special aur memorable ho. 💖",

    "🎂 Good morning, Birthday Bloom! Aaj khushiyon ko full volume par rakhiye. 🌈✨",

    "🎉 A special morning for a special day! Happy Birthday vibes from MoodBloom. 🌸"
]


# ============================================================
# JOURNEY MORNING WISHES
# ============================================================

JOURNEY_MORNING_WISHES = [

    "🌱 Good morning! Aapki Bloom Journey ka ek aur chapter aaj start ho raha hai. ✨",

    "🌸 Morning! Har small step aapko next Bloom level ke closer le jaata hai. ⭐",

    "🌞 Good morning! Keep growing, keep learning, keep blooming. 🌱",

    "⭐ New day, new XP, new progress. Let's continue the journey! 🌷",

    "🌱 Your journey doesn't need to be perfect — it just needs to keep moving. 🌸"
]


# ============================================================
# GROUP MORNING WISHES
# ============================================================

GROUP_MORNING_WISHES = [

    "👥🌅 Good morning everyone! Aaj ka group mood kaisa hai? 🌸",

    "☀️ Good morning, Bloom family! Aaj positivity thodi extra rakhein. 🌷",

    "🌸 Morning everyone! Ek smile ke saath group ka day start karte hain. ✨",

    "🌞 Good morning team! Aaj ka din productive, peaceful aur fun ho. 💫",

    "🌱 Rise & Bloom, everyone! Let's make today a good one. 🌸",

    "☕ Good morning everyone! Chaliye ek fresh start karte hain. ✨"
]


# ============================================================
# POSITIVE / MOTIVATIONAL WISHES
# ============================================================

MOTIVATIONAL_MORNING_WISHES = [

    "🔥 Good morning! Aaj excuses nahi, small progress choose kijiye. 🌱",

    "🌞 New morning, new opportunity. Aaj bas start karna hai. ✨",

    "💫 Good morning! Aapko perfect hone ki zaroorat nahi — consistent rehna enough hai. 🌸",

    "🌱 One small step today can become a big change tomorrow. Keep blooming! 🌷",

    "🔥 Morning! Aaj apne goals ke liye ek meaningful step zaroor lijiye. ⭐",

    "☀️ Good morning! Yesterday is done. Today is yours. 🌸"
]


# ============================================================
# DAILY UNIQUE WISH STATE
# ============================================================

_last_wish_date = None
_last_wish = None


# ============================================================
# SAFE TIME HELPER
# ============================================================

def _now():

    try:
        timezone = getattr(config, "TIMEZONE", None)

        if timezone is not None:
            return datetime.now(timezone)

    except Exception:
        pass

    return datetime.now()


def _today_key():

    return _now().strftime("%Y-%m-%d")


# ============================================================
# SAFE RANDOM CHOICE
# ============================================================

def _safe_choice(items, fallback=None):

    try:

        if items:
            return random.choice(list(items))

    except Exception:
        pass

    if fallback is not None:
        return fallback

    return get_morning_wish()


# ============================================================
# DAILY UNIQUE WISH
# ============================================================

def get_morning_wish():

    global _last_wish_date
    global _last_wish

    today = _today_key()

    # New day → choose a new wish
    if today != _last_wish_date:

        available = [
            wish
            for wish in MORNING_WISHES
            if wish != _last_wish
        ]

        if not available:
            available = MORNING_WISHES

        _last_wish = _safe_choice(
            available,
            MORNING_WISHES[0]
        )

        _last_wish_date = today

    return _last_wish


# ============================================================
# RANDOM MORNING WISH
# ============================================================

def get_random_morning_wish():

    return _safe_choice(
        MORNING_WISHES,
        "🌸 Good morning from MoodBloom! Keep blooming! ✨"
    )


# ============================================================
# MOOD MORNING WISH
# ============================================================

def get_mood_morning_wish(mood=None):

    if not mood:
        return get_morning_wish()

    mood_key = str(mood).strip().lower()

    wishes = MOOD_MORNING_WISHES.get(
        mood_key
    )

    if not wishes:
        return get_morning_wish()

    return _safe_choice(wishes)


# ============================================================
# GOAL MORNING WISH
# ============================================================

def get_goal_morning_wish():

    return _safe_choice(
        GOAL_MORNING_WISHES
    )


# ============================================================
# REWARD MORNING WISH
# ============================================================

def get_reward_morning_wish():

    return _safe_choice(
        REWARD_MORNING_WISHES
    )


# ============================================================
# BIRTHDAY MORNING WISH
# ============================================================

def get_birthday_morning_wish():

    return _safe_choice(
        BIRTHDAY_MORNING_WISHES
    )


# ============================================================
# JOURNEY MORNING WISH
# ============================================================

def get_journey_morning_wish():

    return _safe_choice(
        JOURNEY_MORNING_WISHES
    )


# ============================================================
# GROUP MORNING WISH
# ============================================================

def get_group_morning_wish():

    return _safe_choice(
        GROUP_MORNING_WISHES
    )


# ============================================================
# MOTIVATIONAL MORNING WISH
# ============================================================

def get_motivational_morning_wish():

    return _safe_choice(
        MOTIVATIONAL_MORNING_WISHES
    )


# ============================================================
# PERSONALIZED MORNING WISH
# ============================================================

def get_personalized_morning_wish(
    mood=None,
    has_goals=False,
    reward_available=False,
    birthday=False,
    journey=False
):
    """
    Selects a morning wish based on user context.

    Priority:
        Birthday
        Mood
        Reward
        Goals
        Journey
        Normal daily wish
    """

    try:

        if birthday:
            return get_birthday_morning_wish()

        if mood:
            mood_key = str(mood).strip().lower()

            if mood_key in MOOD_MORNING_WISHES:
                return get_mood_morning_wish(
                    mood_key
                )

        if reward_available:
            return get_reward_morning_wish()

        if has_goals:
            return get_goal_morning_wish()

        if journey:
            return get_journey_morning_wish()

    except Exception:
        pass

    return get_morning_wish()


# ============================================================
# USER CONTEXT MORNING WISH
# ============================================================

def get_morning_wish_for_user(
    user_id=None,
    mood=None,
    has_goals=False,
    reward_available=False,
    birthday=False,
    journey=False
):
    """
    User-facing helper for scheduler/bot.

    user_id is accepted for future personalization and
    compatibility with scheduler integration.
    """

    # Keep user_id intentionally optional.
    # The scheduler can pass it without breaking this function.

    return get_personalized_morning_wish(
        mood=mood,
        has_goals=has_goals,
        reward_available=reward_available,
        birthday=birthday,
        journey=journey
    )


# ============================================================
# GROUP CONTEXT WISH
# ============================================================

def get_group_morning_wish_for_chat(
    chat_id=None,
    member_count=None,
    active_today=False
):
    """
    Group-specific morning message.

    chat_id/member_count/active_today are accepted so the
    scheduler can later provide group context.
    """

    return get_group_morning_wish()


# ============================================================
# WISH COUNT
# ============================================================

def get_morning_wish_count():

    return len(
        MORNING_WISHES
    )


# ============================================================
# V4 WISH COUNTS
# ============================================================

def get_mood_wish_count():

    return sum(
        len(wishes)
        for wishes in MOOD_MORNING_WISHES.values()
    )


def get_total_wish_count():

    return (
        len(MORNING_WISHES)
        + get_mood_wish_count()
        + len(GOAL_MORNING_WISHES)
        + len(REWARD_MORNING_WISHES)
        + len(BIRTHDAY_MORNING_WISHES)
        + len(JOURNEY_MORNING_WISHES)
        + len(GROUP_MORNING_WISHES)
        + len(MOTIVATIONAL_MORNING_WISHES)
    )


# ============================================================
# WISH COLLECTION
# ============================================================

def get_all_morning_wishes():

    wishes = list(MORNING_WISHES)

    for mood_wishes in MOOD_MORNING_WISHES.values():
        wishes.extend(mood_wishes)

    wishes.extend(GOAL_MORNING_WISHES)
    wishes.extend(REWARD_MORNING_WISHES)
    wishes.extend(BIRTHDAY_MORNING_WISHES)
    wishes.extend(JOURNEY_MORNING_WISHES)
    wishes.extend(GROUP_MORNING_WISHES)
    wishes.extend(MOTIVATIONAL_MORNING_WISHES)

    return wishes


# ============================================================
# RESET DAILY WISH CACHE
# ============================================================

def reset_morning_wish_cache():

    global _last_wish_date
    global _last_wish

    _last_wish_date = None
    _last_wish = None


# ============================================================
# FORMAT MORNING MESSAGE
# ============================================================

def format_morning_message(
    wish=None,
    name=None
):

    if not wish:
        wish = get_morning_wish()

    if name:

        clean_name = str(name).strip()

        if clean_name:
            return (
                f"🌅 Good morning, {clean_name}!\n\n"
                f"{wish}"
            )

    return wish


# ============================================================
# MORNING HEADER
# ============================================================

def get_morning_header():

    return "🌅 Good Morning, Bloom! 🌸"


# ============================================================
# FULL MORNING GREETING
# ============================================================

def get_full_morning_greeting(
    name=None,
    mood=None,
    has_goals=False,
    reward_available=False,
    birthday=False,
    journey=False
):

    wish = get_personalized_morning_wish(
        mood=mood,
        has_goals=has_goals,
        reward_available=reward_available,
        birthday=birthday,
        journey=journey
    )

    header = get_morning_header()

    if name:

        clean_name = str(name).strip()

        if clean_name:
            header = (
                f"🌅 Good Morning, {clean_name}! 🌸"
            )

    return (
        f"{header}\n\n"
        f"{wish}"
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    # Basic
    "MORNING_WISHES",
    "MOOD_MORNING_WISHES",
    "GOAL_MORNING_WISHES",
    "REWARD_MORNING_WISHES",
    "BIRTHDAY_MORNING_WISHES",
    "JOURNEY_MORNING_WISHES",
    "GROUP_MORNING_WISHES",
    "MOTIVATIONAL_MORNING_WISHES",

    # Existing API
    "get_morning_wish",
    "get_random_morning_wish",
    "get_morning_wish_count",

    # V4
    "get_mood_morning_wish",
    "get_goal_morning_wish",
    "get_reward_morning_wish",
    "get_birthday_morning_wish",
    "get_journey_morning_wish",
    "get_group_morning_wish",
    "get_motivational_morning_wish",
    "get_personalized_morning_wish",
    "get_morning_wish_for_user",
    "get_group_morning_wish_for_chat",

    # Counts
    "get_mood_wish_count",
    "get_total_wish_count",
    "get_all_morning_wishes",

    # Utilities
    "reset_morning_wish_cache",
    "format_morning_message",
    "get_morning_header",
    "get_full_morning_greeting",
]