# ============================================================
# MOODBLOOM — BLOOM ENGINE
# ============================================================
# Personal Bloom Experience
#
# Includes:
#   🌸 Mood Check
#   💬 Quotes
#   💪 Motivation
#   🌈 Daily Vibe
#   🫶 Self-Care
#   🌱 Tiny Actions
#   ☀️ Positive Reminders
#   🌙 Night Thoughts
#   🎲 Random Bloom
#   💖 Comfort Messages
#   ✨ Compliments
#   🧠 Reflection Prompts
#   🍀 Lucky Bloom
#
# Designed for simple, friendly interaction.
# No Quiz / No All-Tag / No leaderboard.
# ============================================================

from __future__ import annotations

import datetime
import random
from typing import Any, Dict, List, Optional

from text_utils import escape_html

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
)

import moods


# ============================================================
# CONSTANTS
# ============================================================

BLOOM_CALLBACK_PREFIX = "mbe|"
BLOOM_SESSION_KEY = "moodbloom_bloom_session"


# ============================================================
# MOOD DATA
# ============================================================

MOOD_DATA: Dict[str, Dict[str, Any]] = {
    "happy": {
        "emoji": "😊",
        "name": "Happy",
        "color": "sunny",
        "messages": [
            "Aaj ki smile ko thoda aur bada hone do. 🌸",
            "Ye happy energy sambhal ke rakhna. ✨",
            "Aapki positive vibe kisi aur ka din bhi better kar sakti hai. 💖",
            "Khushi ko overthink mat karo, bas feel karo. 🌷",
        ],
        "actions": [
            "Kisi apne ko ek sweet message bhejo. 💌",
            "Apni favourite song suno. 🎧",
            "Aaj ki ek achhi memory save kar lo. 📸",
            "5 minute bas apni khushi enjoy karo. 🌸",
        ],
    },
    "calm": {
        "emoji": "😌",
        "name": "Calm",
        "color": "peaceful",
        "messages": [
            "Slow days bhi beautiful hote hain. 🌿",
            "Aaj bas thoda sa breathe karo aur relax karo. 🫶",
            "Har cheez ka answer abhi milna zaroori nahi hai. 🌙",
            "Peace bhi ek achievement hai. ✨",
        ],
        "actions": [
            "5 deep breaths lo. 🌿",
            "Thodi der phone side mein rakho. 📵",
            "Apna favourite calm song suno. 🎧",
            "Ek glass paani piyo aur slowly relax karo. 💧",
        ],
    },
    "sad": {
        "emoji": "🥺",
        "name": "Sad",
        "color": "soft",
        "messages": [
            "Aaj tough hai to tough hi rehne do. Aapko pretend karne ki zaroorat nahi. 🫶",
            "Ye feeling permanent nahi hai. 🌷",
            "Aapko har din strong dikhna zaroori nahi. 💖",
            "Thoda rest lena bhi progress hai. 🌙",
        ],
        "actions": [
            "Thoda paani piyo. 💧",
            "Kisi trusted person se baat karo. 🫶",
            "10 minute fresh air lo. 🌿",
            "Aaj khud par unnecessary pressure mat daalo. 🌸",
        ],
    },
    "angry": {
        "emoji": "😤",
        "name": "Angry",
        "color": "fire",
        "messages": [
            "Gussa valid hai, bas decision thoda calm hoke lena. 🌿",
            "Pause lena weakness nahi hota. 🫶",
            "Pehle breathe, phir respond. ✨",
            "Aapka peace kisi argument se zyada valuable hai. 🌸",
        ],
        "actions": [
            "10 deep breaths lo. 🌿",
            "Thodi walk karo. 🚶",
            "Reply karne se pehle 5 minute wait karo. ⏳",
            "Jo feel kar rahe ho, use likh do. 📝",
        ],
    },
    "tired": {
        "emoji": "😴",
        "name": "Tired",
        "color": "quiet",
        "messages": [
            "Aap machine nahi ho. Rest allowed hai. 🌙",
            "Slow down. Aaj body ko bhi suno. 🫶",
            "Har productive day full-speed hona zaroori nahi. 🌿",
            "Rest ke baad bloom aur beautiful hota hai. 🌸",
        ],
        "actions": [
            "10 minute rest lo. 🛋️",
            "Paani piyo. 💧",
            "Screen brightness thodi kam karo. 🌙",
            "Aaj ek unnecessary task skip kar do. 🌸",
        ],
    },
    "excited": {
        "emoji": "🤩",
        "name": "Excited",
        "color": "spark",
        "messages": [
            "Ye energy kuch beautiful create kar sakti hai. ✨",
            "Excitement ko action mein convert karo. 🚀",
            "Aaj kuch memorable ho sakta hai. 🌸",
            "Keep that spark alive. 🔥",
        ],
        "actions": [
            "Apne exciting idea ka first step lo. 🚀",
            "Kisi friend ke saath share karo. 💌",
            "Ek mini goal complete karo. 🎯",
            "Aaj ki excitement ka reason note karo. 📝",
        ],
    },
    "anxious": {
        "emoji": "😟",
        "name": "Anxious",
        "color": "gentle",
        "messages": [
            "Ek time par sirf ek cheez handle karo. 🫶",
            "Jo aap control nahi kar sakte, usse thoda release karo. 🌿",
            "Breathe. Abhi aap yahin ho. 💖",
            "Har thought ko fact samajhna zaroori nahi. 🌸",
        ],
        "actions": [
            "4 slow breaths lo. 🌿",
            "5 cheezein dekho, 4 touch karo, 3 sounds suno. 🫶",
            "Ek glass water piyo. 💧",
            "Jo worry hai usko paper par likho. 📝",
        ],
    },
    "loved": {
        "emoji": "🥰",
        "name": "Loved",
        "color": "heart",
        "messages": [
            "Love ko feel bhi karo aur appreciate bhi. 💖",
            "Aapki life mein jo achha hai, use notice karo. 🌸",
            "Small moments often become big memories. ✨",
            "Aaj gratitude ka din bana do. 🫶",
        ],
        "actions": [
            "Kisi apne ko thank-you bolo. 💌",
            "Ek favourite memory yaad karo. 📸",
            "Kisi ko genuine compliment do. 🌷",
            "Apne liye bhi kuch sweet karo. 💖",
        ],
    },
}


# ============================================================
# QUOTES
# ============================================================

QUOTES: List[str] = [
    "Small steps still move you forward. 🌱",
    "You do not have to have everything figured out today. 🌸",
    "Peace is also a form of success. 🌿",
    "A slow day is not a wasted day. 🌙",
    "Your future self will thank you for starting today. ✨",
    "Progress can be quiet. It still counts. 💖",
    "You are allowed to begin again. 🌷",
    "One good decision can change the direction of a day. 🌱",
    "Be patient with the person you are becoming. 🫶",
    "Some chapters are slow because they are building something beautiful. 📖",
    "Do not compare your behind-the-scenes with someone else's highlight reel. 🌸",
    "You can take your time and still reach somewhere beautiful. 🌙",
    "Your effort matters even when nobody sees it. ✨",
    "A little hope is enough to begin. 🌱",
    "You don't need a perfect day to have a good moment. 💖",
    "Sometimes the bravest thing is simply trying again. 🌷",
    "Keep going gently. 🌿",
    "Your pace is still a pace. 🫶",
    "There is something beautiful about not giving up on yourself. ✨",
    "Today can be softer than yesterday. 🌸",
]


# ============================================================
# MOTIVATION
# ============================================================

MOTIVATION: List[str] = [
    "Aaj bas 1% better. Itna kaafi hai. 🌱",
    "Start small. Momentum khud build hoga. 🚀",
    "Aap capable ho — bas first step lo. ✨",
    "Perfect timing ka wait mat karo. Start where you are. 🌸",
    "Consistency motivation se zyada powerful hoti hai. 💪",
    "Aaj ka tiny effort kal ka confidence banega. 🌱",
    "Jo kaam 5 minute mein start ho sakta hai, usse postpone mat karo. ⏳",
    "Aapko sab kuch ek saath nahi karna. Ek cheez choose karo. 🎯",
    "Keep moving, even slowly. 🫶",
    "Future aapke small decisions se banta hai. ✨",
    "Aaj ka effort invisible ho sakta hai, useless nahi. 🌷",
    "Discipline boring lag sakta hai, result beautiful hota hai. 🌸",
    "Give yourself a chance before giving up. 💖",
    "Aap jitna soch rahe ho usse zyada capable ho. 🔥",
    "One step. Then another. Bas itna hi. 🌱",
]


# ============================================================
# SELF CARE
# ============================================================

SELF_CARE: List[str] = [
    "💧 Ek glass paani piyo.",
    "🌿 5 deep breaths lo.",
    "🚶 5–10 minute walk karo.",
    "📵 10 minute phone side mein rakho.",
    "🎧 Apna favourite song suno.",
    "🧼 Fresh ho jao aur comfortable clothes pehno.",
    "🌤️ Thodi fresh air lo.",
    "📝 Jo feel kar rahe ho, likh do.",
    "🫶 Kisi trusted person se baat karo.",
    "😴 Agar tired ho to rest ko priority do.",
    "🍎 Kuch healthy kha lo.",
    "🌸 Apne room/desk ka ek small corner clean karo.",
    "📚 10 minute kisi useful cheez ko padho.",
    "☕ Apni favourite drink slowly enjoy karo.",
    "💖 Khud ko unnecessary criticism se break do.",
]


# ============================================================
# TINY ACTIONS
# ============================================================

TINY_ACTIONS: List[str] = [
    "🎯 5-minute task start karo.",
    "📚 Ek page padho.",
    "📝 Kal ke 3 important tasks likho.",
    "🧹 Apna desk clean karo.",
    "💧 Water bottle refill karo.",
    "📱 Ek unnecessary notification off karo.",
    "🌱 Ek pending small task finish karo.",
    "🎧 Ek song bina scrolling ke suno.",
    "🚶 Thoda walk karo.",
    "💌 Kisi ko good morning/good night message bhejo.",
    "🗂️ Ek folder organize karo.",
    "⏰ Agle task ke liye timer set karo.",
    "📖 10 minute focused study/work karo.",
    "🧠 Ek new concept seekho.",
    "🌸 Aaj ki ek achhi cheez note karo.",
]


# ============================================================
# COMFORT
# ============================================================

COMFORT_MESSAGES: List[str] = [
    "It's okay to have a difficult day. 🫶",
    "Aapko abhi sab kuch solve karna zaroori nahi. 🌙",
    "Thoda rest, thoda breathe, phir next step. 🌿",
    "You are doing better than you think. 💖",
    "Aaj bas khud ke saath thoda gentle raho. 🌸",
    "Every feeling has a beginning and an ending. 🌷",
    "Aap akela sab kuch carry karne ke liye nahi bane ho. 🫶",
    "Tomorrow doesn't need to be decided tonight. 🌙",
    "One difficult moment doesn't define your whole life. ✨",
    "Slowly is still moving. 🌱",
]


# ============================================================
# COMPLIMENTS
# ============================================================

COMPLIMENTS: List[str] = [
    "🌸 Aapki vibe genuinely achhi hai.",
    "✨ Aap mein kuch alag karne ki curiosity hai.",
    "💖 Aap jitna realize karte ho usse zyada valuable ho.",
    "🌱 Aap grow kar rahe ho, even on days you don't notice it.",
    "🫶 Aapko khud par thoda aur trust karna chahiye.",
    "🌷 Aapki consistency future mein bahut matter karegi.",
    "✨ You have more potential than your doubts suggest.",
    "💖 Aapka effort count karta hai.",
    "🌿 Aapko apni progress celebrate karni chahiye.",
    "🌸 You deserve your own kindness too.",
]


# ============================================================
# REFLECTION PROMPTS
# ============================================================

REFLECTION_PROMPTS: List[str] = [
    "🌸 Aaj ki sabse achhi cheez kya thi?",
    "🧠 Aaj aapne kya naya seekha?",
    "💖 Kis cheez ke liye aaj grateful ho?",
    "🌱 Kal kya ek small improvement kar sakte ho?",
    "🫶 Aaj kis moment ne aapko smile karaya?",
    "✨ Aaj aapne apne liye kya achha kiya?",
    "🌙 Aaj kis thought ko release karna chahte ho?",
    "🎯 Kal ka sabse important goal kya hai?",
    "📖 Aaj ka ek memorable moment kya tha?",
    "🌿 Abhi aapko actually kis cheez ki zaroorat hai?",
]


# ============================================================
# DAILY VIBES
# ============================================================

DAILY_VIBES: List[Dict[str, str]] = [
    {
        "title": "🌸 Soft Bloom",
        "text": "Aaj slow aur peaceful pace choose karo.",
    },
    {
        "title": "✨ Spark Day",
        "text": "Aaj kisi ek idea ko action mein convert karo.",
    },
    {
        "title": "🌿 Calm Day",
        "text": "Aaj unnecessary pressure ko thoda kam rakho.",
    },
    {
        "title": "🔥 Power Day",
        "text": "Aaj ek pending kaam ko finally finish karo.",
    },
    {
        "title": "💖 Heart Day",
        "text": "Aaj kisi apne ko appreciation feel karao.",
    },
    {
        "title": "🌙 Slow Bloom",
        "text": "Aaj rest aur recovery ko bhi priority do.",
    },
    {
        "title": "🌱 Growth Day",
        "text": "Aaj kuch naya seekhne ke liye 15 minutes nikalo.",
    },
]


# ============================================================
# SESSION
# ============================================================

def get_session(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    session = context.user_data.get(BLOOM_SESSION_KEY)

    if not isinstance(session, dict):
        session = {}
        context.user_data[BLOOM_SESSION_KEY] = session

    return session


def clear_session(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(BLOOM_SESSION_KEY, None)


# ============================================================
# USER ID
# ============================================================

def get_user_id(update: Update) -> Optional[int]:
    if update.effective_user:
        return update.effective_user.id

    return None


# ============================================================
# SAFE HTML
# ============================================================

def safe(value: Any) -> str:
    return escape_html(value)


# ============================================================
# MOOD NORMALIZER
# ============================================================

def normalize_mood(mood: str) -> str:
    mood = mood.lower().strip()

    aliases = {
        "good": "happy",
        "great": "happy",
        "khush": "happy",
        "happy": "happy",

        "peace": "calm",
        "peaceful": "calm",
        "calm": "calm",
        "relaxed": "calm",

        "sad": "sad",
        "dukhi": "sad",
        "upset": "sad",

        "angry": "angry",
        "gussa": "angry",
        "mad": "angry",

        "tired": "tired",
        "thaka": "tired",
        "exhausted": "tired",

        "excited": "excited",
        "excited": "excited",

        "anxious": "anxious",
        "anxiety": "anxious",
        "worried": "anxious",

        "love": "loved",
        "loved": "loved",
        "romantic": "loved",
    }

    return aliases.get(mood, mood)


# ============================================================
# MAIN MENU
# ============================================================

def bloom_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🌸 Mood",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}mood",
                ),
                InlineKeyboardButton(
                    "💬 Quote",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}quote",
                ),
            ],
            [
                InlineKeyboardButton(
                    "💪 Motivation",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}motivate",
                ),
                InlineKeyboardButton(
                    "🫶 Self-Care",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}care",
                ),
            ],
            [
                InlineKeyboardButton(
                    "✨ Random Bloom",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}random",
                ),
                InlineKeyboardButton(
                    "🌈 Daily Vibe",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}vibe",
                ),
            ],
            [
                InlineKeyboardButton(
                    "💖 Comfort",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}comfort",
                ),
                InlineKeyboardButton(
                    "🌱 Tiny Action",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}action",
                ),
            ],
        ]
    )


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🌸 Bloom",
                    callback_data=f"{BLOOM_CALLBACK_PREFIX}menu",
                ),
            ]
        ]
    )


# ============================================================
# MOOD KEYBOARD
# ============================================================

def mood_keyboard() -> InlineKeyboardMarkup:
    buttons = []

    row = []

    for key, data in MOOD_DATA.items():
        row.append(
            InlineKeyboardButton(
                f"{data['emoji']} {data['name']}",
                callback_data=f"{BLOOM_CALLBACK_PREFIX}setmood|{key}",
            )
        )

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append(
        [
            InlineKeyboardButton(
                "🌸 Bloom",
                callback_data=f"{BLOOM_CALLBACK_PREFIX}menu",
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


# ============================================================
# SHOW BLOOM MENU
# ============================================================

async def show_bloom_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "🌸 <b>MoodBloom</b>\n\n"
        "Aaj aapko kya chahiye? 💖"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=bloom_menu_keyboard(),
        )
    elif update.effective_message:
        await update.effective_message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=bloom_menu_keyboard(),
        )


# ============================================================
# SHOW MOOD MENU
# ============================================================

async def show_mood_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "🌸 <b>How are you feeling?</b>\n\n"
        "Jo closest lage, choose karo. 🫶"
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=mood_keyboard(),
        )
    else:
        await update.effective_message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=mood_keyboard(),
        )


# ============================================================
# MOOD RESPONSE
# ============================================================

def create_mood_response(mood: str) -> str:
    mood = normalize_mood(mood)

    data = MOOD_DATA.get(mood)

    if not data:
        return (
            "🌸 <b>Mood received</b>\n\n"
            "Har feeling valid hai. 🫶\n"
            "Thoda breathe karo aur khud ke saath gentle raho."
        )

    message = random.choice(data["messages"])
    action = random.choice(data["actions"])

    return (
        f"{data['emoji']} <b>{safe(data['name'])}</b>\n\n"
        f"{safe(message)}\n\n"
        f"🌱 <b>Tiny idea:</b>\n"
        f"{safe(action)}"
    )


# ============================================================
# SAVE MOOD
# ============================================================

def save_mood(
    context: ContextTypes.DEFAULT_TYPE,
    mood: str,
) -> None:

    session = get_session(context)

    session["last_mood"] = normalize_mood(mood)
    session["last_mood_at"] = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()


# ============================================================
# TRY EXISTING MOODS MODULE
# ============================================================

def record_existing_mood(
    user_id: int,
    mood: str,
) -> None:
    """
    Best-effort integration with existing moods.py.

    Different versions of MoodBloom may expose different
    function names, so this safely checks available methods.
    """

    possible_functions = [
        "save_mood",
        "record_mood",
        "add_mood",
        "set_mood",
    ]

    for function_name in possible_functions:

        function = getattr(moods, function_name, None)

        if not callable(function):
            continue

        try:
            function(user_id, mood)
            return
        except TypeError:
            try:
                function(user_id=user_id, mood=mood)
                return
            except Exception:
                continue
        except Exception:
            continue


# ============================================================
# HANDLE MOOD
# ============================================================

async def handle_mood_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    mood: str,
) -> None:

    query = update.callback_query

    if not query:
        return

    user_id = get_user_id(update)

    mood = normalize_mood(mood)

    save_mood(context, mood)

    if user_id is not None:
        record_existing_mood(user_id, mood)

    text = create_mood_response(mood)

    await query.answer("🌸 Mood saved!")

    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=back_keyboard(),
    )


# ============================================================
# RANDOM CONTENT
# ============================================================

def random_bloom() -> Dict[str, str]:

    choices = [
        {
            "type": "quote",
            "text": random.choice(QUOTES),
        },
        {
            "type": "motivation",
            "text": random.choice(MOTIVATION),
        },
        {
            "type": "care",
            "text": random.choice(SELF_CARE),
        },
        {
            "type": "action",
            "text": random.choice(TINY_ACTIONS),
        },
        {
            "type": "comfort",
            "text": random.choice(COMFORT_MESSAGES),
        },
        {
            "type": "compliment",
            "text": random.choice(COMPLIMENTS),
        },
        {
            "type": "reflection",
            "text": random.choice(REFLECTION_PROMPTS),
        },
    ]

    return random.choice(choices)


# ============================================================
# QUOTE
# ============================================================

async def show_quote(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "💬 <b>Quote for you</b>\n\n"
        f"“{safe(random.choice(QUOTES))}”"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# MOTIVATION
# ============================================================

async def show_motivation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "💪 <b>A little push for you</b>\n\n"
        f"{safe(random.choice(MOTIVATION))}"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# SELF CARE
# ============================================================

async def show_self_care(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "🫶 <b>Take care of yourself</b>\n\n"
        f"{safe(random.choice(SELF_CARE))}"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# TINY ACTION
# ============================================================

async def show_tiny_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "🌱 <b>Tiny Action</b>\n\n"
        f"{safe(random.choice(TINY_ACTIONS))}\n\n"
        "Bas itna sa step. ✨"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# COMFORT
# ============================================================

async def show_comfort(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "💖 <b>For you</b>\n\n"
        f"{safe(random.choice(COMFORT_MESSAGES))}"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# COMPLIMENT
# ============================================================

async def show_compliment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "🌷 <b>Today's little reminder</b>\n\n"
        f"{safe(random.choice(COMPLIMENTS))}"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# REFLECTION
# ============================================================

async def show_reflection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "🧠 <b>Little Reflection</b>\n\n"
        f"{safe(random.choice(REFLECTION_PROMPTS))}\n\n"
        "Iska answer apne notes mein likh sakte ho. 🌸"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# DAILY VIBE
# ============================================================

def get_daily_vibe() -> Dict[str, str]:

    today = datetime.date.today()

    index = today.toordinal() % len(DAILY_VIBES)

    return DAILY_VIBES[index]


async def show_daily_vibe(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    vibe = get_daily_vibe()

    text = (
        f"<b>{safe(vibe['title'])}</b>\n\n"
        f"{safe(vibe['text'])}\n\n"
        "🌸 Make today count in your own way."
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# RANDOM BLOOM
# ============================================================

async def show_random_bloom(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    item = random_bloom()

    labels = {
        "quote": "💬 Quote",
        "motivation": "💪 Motivation",
        "care": "🫶 Self-Care",
        "action": "🌱 Tiny Action",
        "comfort": "💖 Comfort",
        "compliment": "🌷 Compliment",
        "reflection": "🧠 Reflection",
    }

    label = labels.get(
        item["type"],
        "🌸 Bloom",
    )

    text = (
        f"<b>{safe(label)}</b>\n\n"
        f"{safe(item['text'])}"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# LUCKY BLOOM
# ============================================================

LUCKY_MESSAGES = [
    "🌱 Today is a good day to start something small.",
    "✨ Something simple may make you unexpectedly happy today.",
    "🌸 Trust your pace today.",
    "💖 Give one person a reason to smile.",
    "🌿 Protect your peace today.",
    "🔥 Finish one thing you've been postponing.",
    "🌙 Don't carry tomorrow's worries into today.",
    "🫶 Be a little kinder to yourself today.",
    "🎯 Focus on one important thing.",
    "🌷 Notice one beautiful little moment today.",
]


async def show_lucky_bloom(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    message = random.choice(LUCKY_MESSAGES)

    number = random.randint(1, 99)

    text = (
        "🍀 <b>Your Lucky Bloom</b>\n\n"
        f"{safe(message)}\n\n"
        f"✨ Lucky number: <b>{number}</b>"
    )

    await edit_or_send(
        update,
        text,
        back_keyboard(),
    )


# ============================================================
# BLOOM STATS
# ============================================================

def get_bloom_stats(
    context: ContextTypes.DEFAULT_TYPE,
) -> Dict[str, Any]:

    session = get_session(context)

    return {
        "last_mood": session.get("last_mood"),
        "last_mood_at": session.get("last_mood_at"),
    }


# ============================================================
# LAST MOOD
# ============================================================

def get_last_mood(
    context: ContextTypes.DEFAULT_TYPE,
) -> Optional[str]:

    session = get_session(context)

    mood = session.get("last_mood")

    if mood:
        return str(mood)

    return None


# ============================================================
# COMMAND: /bloom
# ============================================================

async def bloom_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    await show_bloom_menu(update, context)


# ============================================================
# COMMAND: /quote
# ============================================================

async def quote_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "💬 <b>Quote for you</b>\n\n"
        f"“{safe(random.choice(QUOTES))}”"
    )

    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# COMMAND: /motivate
# ============================================================

async def motivate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "💪 <b>You've got this!</b>\n\n"
        f"{safe(random.choice(MOTIVATION))}"
    )

    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# COMMAND: /care
# ============================================================

async def care_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    text = (
        "🫶 <b>Self-Care</b>\n\n"
        f"{safe(random.choice(SELF_CARE))}"
    )

    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# COMMAND: /vibe
# ============================================================

async def vibe_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    vibe = get_daily_vibe()

    text = (
        f"<b>{safe(vibe['title'])}</b>\n\n"
        f"{safe(vibe['text'])}"
    )

    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# COMMAND: /random
# ============================================================

async def random_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    item = random_bloom()

    text = (
        "🎲 <b>Random Bloom</b>\n\n"
        f"{safe(item['text'])}"
    )

    await update.effective_message.reply_text(
        text,
        parse_mode="HTML",
    )


# ============================================================
# EDIT OR SEND
# ============================================================

async def edit_or_send(
    update: Update,
    text: str,
    keyboard: InlineKeyboardMarkup,
) -> None:

    if update.callback_query:

        query = update.callback_query

        await query.answer()

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )

    elif update.effective_message:

        await update.effective_message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )


# ============================================================
# CALLBACK HANDLER
# ============================================================

async def handle_bloom_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    query = update.callback_query

    if not query:
        return

    data = query.data or ""

    if not data.startswith(BLOOM_CALLBACK_PREFIX):
        return

    payload = data[len(BLOOM_CALLBACK_PREFIX):]

    # --------------------------------------------------------
    # MAIN MENU
    # --------------------------------------------------------

    if payload == "menu":
        await query.answer()
        await show_bloom_menu(update, context)
        return

    # --------------------------------------------------------
    # MOOD
    # --------------------------------------------------------

    if payload == "mood":
        await query.answer()
        await show_mood_menu(update, context)
        return

    # --------------------------------------------------------
    # SELECT MOOD
    # --------------------------------------------------------

    if payload.startswith("setmood|"):

        mood = payload.split("|", 1)[1]

        await handle_mood_selection(
            update,
            context,
            mood,
        )

        return

    # --------------------------------------------------------
    # QUOTE
    # --------------------------------------------------------

    if payload == "quote":
        await show_quote(update, context)
        return

    # --------------------------------------------------------
    # MOTIVATION
    # --------------------------------------------------------

    if payload == "motivate":
        await show_motivation(update, context)
        return

    # --------------------------------------------------------
    # SELF CARE
    # --------------------------------------------------------

    if payload == "care":
        await show_self_care(update, context)
        return

    # --------------------------------------------------------
    # RANDOM
    # --------------------------------------------------------

    if payload == "random":
        await show_random_bloom(update, context)
        return

    # --------------------------------------------------------
    # DAILY VIBE
    # --------------------------------------------------------

    if payload == "vibe":
        await show_daily_vibe(update, context)
        return

    # --------------------------------------------------------
    # TINY ACTION
    # --------------------------------------------------------

    if payload == "action":
        await show_tiny_action(update, context)
        return

    # --------------------------------------------------------
    # COMFORT
    # --------------------------------------------------------

    if payload == "comfort":
        await show_comfort(update, context)
        return

    # --------------------------------------------------------
    # COMPLIMENT
    # --------------------------------------------------------

    if payload == "compliment":
        await show_compliment(update, context)
        return

    # --------------------------------------------------------
    # REFLECTION
    # --------------------------------------------------------

    if payload == "reflection":
        await show_reflection(update, context)
        return

    # --------------------------------------------------------
    # LUCKY
    # --------------------------------------------------------

    if payload == "lucky":
        await show_lucky_bloom(update, context)
        return

    await query.answer()


# ============================================================
# REGISTER HANDLERS
# ============================================================

def register_bloom_handlers(application) -> None:
    """
    Register Bloom Engine handlers.

    NOTE:
    Existing bot.py integration will be done later.
    """

    application.add_handler(
        CommandHandler(
            "bloom",
            bloom_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "quote",
            quote_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "motivate",
            motivate_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "care",
            care_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "vibe",
            vibe_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "random",
            random_command,
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_bloom_callback,
            pattern=r"^mbe\|",
        )
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "MOOD_DATA",
    "QUOTES",
    "MOTIVATION",
    "SELF_CARE",
    "TINY_ACTIONS",
    "COMFORT_MESSAGES",
    "COMPLIMENTS",
    "REFLECTION_PROMPTS",
    "DAILY_VIBES",
    "get_session",
    "clear_session",
    "get_last_mood",
    "get_bloom_stats",
    "create_mood_response",
    "show_bloom_menu",
    "show_mood_menu",
    "show_quote",
    "show_motivation",
    "show_self_care",
    "show_tiny_action",
    "show_comfort",
    "show_compliment",
    "show_reflection",
    "show_daily_vibe",
    "show_random_bloom",
    "show_lucky_bloom",
    "bloom_command",
    "quote_command",
    "motivate_command",
    "care_command",
    "vibe_command",
    "random_command",
    "handle_bloom_callback",
    "register_bloom_handlers",
]