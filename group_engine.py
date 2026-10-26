# ============================================================
# MOODBLOOM — GROUP ENGINE
# ============================================================
# Group Features:
#   👋 Welcome
#   👋 Goodbye
#   🌸 Group Mood
#   📖 Group Story
#   🕵️ Group Mystery
#   🎲 Group Fun
#   💬 Group Question
#   👑 Admin Controls
#   🛡️ Basic Group Utilities
#
# Removed intentionally:
#   ❌ /all
#   ❌ Mention-all system
#   ❌ Quiz
#   ❌ Quiz leaderboard
# ============================================================

from __future__ import annotations

import random
from typing import Any, Dict, Optional

from text_utils import escape_html

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.constants import ChatMemberStatus, ChatType

from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)


# ============================================================
# CONSTANTS
# ============================================================

GROUP_CALLBACK_PREFIX = "mbg|"
GROUP_SETTINGS_KEY = "moodbloom_group_settings"


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_GROUP_SETTINGS = {
    "welcome": True,
    "goodbye": True,
    "group_mood": True,
    "group_story": True,
    "group_mystery": True,
    "group_fun": True,
    "group_question": True,
}


# ============================================================
# WELCOME MESSAGES
# ============================================================

WELCOME_MESSAGES = [
    "🌸 Welcome {name}!\n\nMoodBloom family mein aapka welcome hai. 💖",
    "✨ Hey {name}, welcome to the group!\n\nHope aapka day beautiful ho. 🌷",
    "🌱 Welcome {name}!\n\nLet's keep the group positive and fun. 🫶",
    "💖 A warm welcome to {name}!\n\nMoodBloom ke saath bloom karte raho. 🌸",
    "🌈 Hey {name}!\n\nNew bloom has joined the garden. 🌱",
]


# ============================================================
# GOODBYE MESSAGES
# ============================================================

GOODBYE_MESSAGES = [
    "🌸 {name} group se leave kar gaye. Take care! 💖",
    "👋 Goodbye {name}!\n\nHope to see you again. 🌷",
    "🌙 {name} has left the garden.\n\nTake care! 🫶",
    "🌱 Bye {name}!\n\nKeep blooming wherever you go. ✨",
]


# ============================================================
# GROUP MOODS
# ============================================================

GROUP_MOODS = {
    "happy": {
        "emoji": "😊",
        "name": "Happy",
        "text": "Aaj group ki vibe kaafi positive lag rahi hai! ✨",
    },
    "chill": {
        "emoji": "😌",
        "name": "Chill",
        "text": "Aaj bas chill mode on rakho. 🌿",
    },
    "chaotic": {
        "emoji": "😂",
        "name": "Chaotic",
        "text": "Lagta hai aaj group mein thodi masti hone wali hai. 😂",
    },
    "sleepy": {
        "emoji": "😴",
        "name": "Sleepy",
        "text": "Group ko shayad ek coffee ki zaroorat hai. ☕",
    },
    "excited": {
        "emoji": "🤩",
        "name": "Excited",
        "text": "Energy high hai! Aaj kuch interesting ho sakta hai. 🔥",
    },
    "peaceful": {
        "emoji": "🌿",
        "name": "Peaceful",
        "text": "Aaj group ki vibe soft aur peaceful hai. 🌸",
    },
}


# ============================================================
# GROUP STORIES
# ============================================================

GROUP_STORIES = [
    {
        "title": "🌙 The Midnight Message",
        "text": (
            "Raat ke 12 baje group mein ek unknown message aaya...\n\n"
            "“Agar ye message aap sabko dikh raha hai, "
            "to garden ka secret activate ho chuka hai.”\n\n"
            "Message ke neeche sirf ek symbol tha: 🌸\n\n"
            "Kisi ko nahi pata tha sender kaun tha..."
        ),
    },
    {
        "title": "🚂 The Last Train",
        "text": (
            "Station par ek train khadi thi.\n\n"
            "Interesting baat ye thi ki us train ka koi number nahi tha.\n\n"
            "Group ke members ne decide kiya ki ek clue follow kiya jaye.\n\n"
            "Door khula...\n"
            "Aur andar ek note tha:\n\n"
            "“Jo pehle seat par baithega, wahi next clue dekhega.” 👀"
        ),
    },
    {
        "title": "🔐 Room 404",
        "text": (
            "Old building ke fourth floor par Room 404 tha.\n\n"
            "Room officially exist hi nahi karta tha.\n\n"
            "Lekin aaj raat door ke neeche se light aa rahi thi.\n\n"
            "Handle slowly move hua...\n\n"
            "Aur andar wall par likha tha:\n"
            "“You were expected.” 🌙"
        ),
    },
    {
        "title": "🌲 The Silent Garden",
        "text": (
            "Forest ke beech ek garden tha jahan koi awaaz nahi thi.\n\n"
            "Group ko wahan ek glowing flower mila. 🌸\n\n"
            "Flower ke paas ek small card tha:\n\n"
            "“Ek wish bolo. Lekin carefully...”\n\n"
            "Sab ek doosre ko dekhne lage."
        ),
    },
]


# ============================================================
# GROUP MYSTERIES
# ============================================================

GROUP_MYSTERIES = [
    {
        "title": "🕵️ The Missing Key",
        "clues": [
            "Clue 1: Key table par last time dekhi gayi thi.",
            "Clue 2: Room locked tha, lekin window open thi.",
            "Clue 3: Window ke paas muddy footprints mile.",
            "Clue 4: Footprints garden ki taraf ja rahe the.",
        ],
        "answer": "garden",
        "success": (
            "🎯 Correct!\n\n"
            "Key garden ki taraf le jaayi gayi thi. 🌿"
        ),
    },
    {
        "title": "🕰️ The Silent Clock",
        "clues": [
            "Clue 1: Clock exactly 10:15 par ruk gayi.",
            "Clue 2: Room mein kisi ne entry nahi ki.",
            "Clue 3: Window ke paas ek broken wire mila.",
            "Clue 4: Clock battery missing thi.",
        ],
        "answer": "battery",
        "success": (
            "🎯 Correct!\n\n"
            "Clock battery missing hone ki wajah se ruki thi. 🔋"
        ),
    },
    {
        "title": "📖 The Missing Book",
        "clues": [
            "Clue 1: Book library ke shelf par thi.",
            "Clue 2: Shelf ke paas dust disturbed thi.",
            "Clue 3: Ek bookmark floor par mila.",
            "Clue 4: Bookmark par room number 213 likha tha.",
        ],
        "answer": "213",
        "success": (
            "🎯 Correct!\n\n"
            "Book ka next clue Room 213 tha. 📖"
        ),
    },
]


# ============================================================
# GROUP FUN
# ============================================================

GROUP_FUN = {
    "truth": [
        "Aapka sabse funny school memory kya hai? 😂",
        "Group mein sabse zyada kiski messages dekhte ho? 👀",
        "Aapka ek secret talent kya hai? 😎",
        "Aapne sabse funny excuse kab banaya tha? 😂",
        "Aapka current favourite song kaunsa hai? 🎵",
    ],
    "dare": [
        "Apna current mood sirf emojis mein batao. 😂",
        "Group mein kisi ko ek genuine compliment do. 💖",
        "Apna last-used emoji 3 baar bhejo. 😭",
        "5 seconds ke liye apna status 'MoodBloom 🌸' rakho. 😎",
        "Ek funny one-liner group mein bhejo. 😂",
    ],
    "would_you_rather": [
        "🌙 Would you rather: past mein jao ya future mein?",
        "🍕 Would you rather: lifetime free pizza ya lifetime free coffee?",
        "✈️ Would you rather: world tour ya dream house?",
        "📱 Would you rather: phone ke bina 1 month ya internet ke bina 1 month?",
        "🌊 Would you rather: beach vacation ya mountain vacation?",
    ],
    "challenge": [
        "🎯 Challenge: 3 different emojis bhejo jo aapka personality describe karein.",
        "😂 Challenge: ek funny nickname khud ke liye choose karo.",
        "🌸 Challenge: group mein kisi ek member ko appreciate karo.",
        "🎵 Challenge: apna favourite song ka naam bhejo.",
        "🔥 Challenge: bina 'haan' ya 'nahi' bole ek question ka answer do.",
    ],
}


# ============================================================
# GROUP QUESTIONS
# ============================================================

GROUP_QUESTIONS = [
    "💬 Agar aapko ek superpower mile, to kya choose karoge?",
    "💬 Aapke liye perfect weekend kaisa hota hai?",
    "💬 Ek jagah jahan aap zaroor travel karna chahte ho?",
    "💬 Aap morning person ho ya night owl? 🌙",
    "💬 Childhood ka favourite cartoon kaunsa tha? 📺",
    "💬 Agar ek din ke liye famous ho jao, to kya karoge? 😎",
    "💬 Aapka comfort food kya hai? 🍕",
    "💬 Kaunsi ek skill sabko seekhni chahiye?",
    "💬 Agar ₹1 crore mil jaaye, sabse pehle kya karoge? 💰",
    "💬 Aapka current favourite movie/series kaunsa hai? 🎬",
    "💬 Life mein ek cheez jo aap kabhi try karna chahte ho?",
    "💬 Group ki vibe ko ek word mein describe karo. 🌸",
]


# ============================================================
# IN-MEMORY GROUP STATE
# ============================================================

GROUP_STATE: Dict[int, Dict[str, Any]] = {}


def get_group_state(chat_id: int) -> Dict[str, Any]:
    if chat_id not in GROUP_STATE:
        GROUP_STATE[chat_id] = {
            "mood": None,
            "story": None,
            "mystery": None,
            "mystery_clue": 0,
            "fun": None,
            "question": None,
        }

    return GROUP_STATE[chat_id]


# ============================================================
# SAFE HTML
# ============================================================

def safe(value: Any) -> str:
    return escape_html(value)


# ============================================================
# GROUP CHECK
# ============================================================

def is_group(update: Update) -> bool:
    chat = update.effective_chat

    if not chat:
        return False

    return chat.type in (
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    )


# ============================================================
# ADMIN CHECK
# ============================================================

async def is_admin(
    update: Update,
    user_id: Optional[int] = None,
) -> bool:

    chat = update.effective_chat

    if not chat:
        return False

    if user_id is None and update.effective_user:
        user_id = update.effective_user.id

    if user_id is None:
        return False

    try:
        member = await chat.get_member(user_id)

        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )

    except Exception:
        return False


# ============================================================
# SETTINGS
# ============================================================

def get_settings(
    context: ContextTypes.DEFAULT_TYPE,
) -> Dict[str, bool]:

    settings = context.chat_data.get(
        GROUP_SETTINGS_KEY
    )

    if not isinstance(settings, dict):
        settings = DEFAULT_GROUP_SETTINGS.copy()

        context.chat_data[
            GROUP_SETTINGS_KEY
        ] = settings

    # Add newly introduced settings safely
    for key, value in DEFAULT_GROUP_SETTINGS.items():
        if key not in settings:
            settings[key] = value

    return settings


def setting_enabled(
    context: ContextTypes.DEFAULT_TYPE,
    name: str,
) -> bool:

    settings = get_settings(context)

    return bool(
        settings.get(
            name,
            DEFAULT_GROUP_SETTINGS.get(name, True),
        )
    )


# ============================================================
# GROUP MENU
# ============================================================

def group_menu_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🌸 Group Mood",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}mood",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📖 Story",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}story",
                ),
                InlineKeyboardButton(
                    "🕵️ Mystery",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}mystery",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎲 Fun",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}fun",
                ),
                InlineKeyboardButton(
                    "💬 Question",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}question",
                ),
            ],
            [
                InlineKeyboardButton(
                    "👑 Admin",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}admin",
                ),
            ],
        ]
    )


# ============================================================
# ADMIN MENU
# ============================================================

def admin_menu_keyboard(
    settings: Dict[str, bool],
) -> InlineKeyboardMarkup:

    def state(name: str) -> str:
        return "ON" if settings.get(name, True) else "OFF"

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"👋 Welcome: {state('welcome')}",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}toggle|welcome"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    f"👋 Goodbye: {state('goodbye')}",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}toggle|goodbye"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🌸 Group Mood: {state('group_mood')}",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}toggle|group_mood"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    f"📖 Story: {state('group_story')}",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}toggle|group_story"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🕵️ Mystery: {state('group_mystery')}",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}toggle|group_mystery"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    f"🎲 Fun: {state('group_fun')}",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}toggle|group_fun"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    f"💬 Question: {state('group_question')}",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}toggle|group_question"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "🌸 Back",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}menu",
                ),
            ],
        ]
    )


# ============================================================
# GROUP COMMAND
# ============================================================

async def group_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):
        await update.effective_message.reply_text(
            "🌸 Ye feature group ke liye hai."
        )
        return

    text = (
        "🌸 MoodBloom Group\n\n"
        "Group mein kya karna hai?"
    )

    await update.effective_message.reply_text(
        text,
        
        reply_markup=group_menu_keyboard(),
    )


# ============================================================
# GROUP MOOD
# ============================================================

async def show_group_mood(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):
        return

    if not setting_enabled(
        context,
        "group_mood",
    ):
        await answer_callback(
            update,
            "🌸 Group Mood disabled hai.",
        )
        return

    mood = random.choice(
        list(GROUP_MOODS.values())
    )

    chat_id = update.effective_chat.id

    state = get_group_state(chat_id)
    state["mood"] = mood["name"]

    text = (
        f"{mood['emoji']} "
        f"Group Mood: "
        f"{safe(mood['name'])}\n\n"
        f"{safe(mood['text'])}"
    )

    await edit_or_send_group(
        update,
        text,
        group_menu_keyboard(),
    )


# ============================================================
# GROUP STORY
# ============================================================

async def show_group_story(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):
        return

    if not setting_enabled(
        context,
        "group_story",
    ):
        await answer_callback(
            update,
            "📖 Group Story disabled hai.",
        )
        return

    story = random.choice(GROUP_STORIES)

    chat_id = update.effective_chat.id

    state = get_group_state(chat_id)
    state["story"] = story["title"]

    text = (
        f"{safe(story['title'])}\n\n"
        f"{safe(story['text'])}\n\n"
        "🌸 To be continued..."
    )

    await edit_or_send_group(
        update,
        text,
        group_menu_keyboard(),
    )


# ============================================================
# GROUP FUN MENU
# ============================================================

def fun_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎭 Truth",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}fun|truth"
                    ),
                ),
                InlineKeyboardButton(
                    "🔥 Dare",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}fun|dare"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "🤔 Would You Rather",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}fun|would_you_rather"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎯 Challenge",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}fun|challenge"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "🌸 Back",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}menu",
                ),
            ],
        ]
    )


# ============================================================
# SHOW FUN MENU
# ============================================================

async def show_group_fun(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):
        return

    if not setting_enabled(
        context,
        "group_fun",
    ):
        await answer_callback(
            update,
            "🎲 Group Fun disabled hai.",
        )
        return

    text = (
        "🎲 Group Fun\n\n"
        "Kuch masti karte hain! 😄\n\n"
        "Ek option choose karo."
    )

    await edit_or_send_group(
        update,
        text,
        fun_keyboard(),
    )


# ============================================================
# PLAY FUN
# ============================================================

async def play_group_fun(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    fun_type: str,
) -> None:

    if not is_group(update):
        return

    if not setting_enabled(
        context,
        "group_fun",
    ):
        await answer_callback(
            update,
            "🎲 Group Fun disabled hai.",
        )
        return

    items = GROUP_FUN.get(fun_type)

    if not items:
        await answer_callback(
            update,
            "🎲 Fun option nahi mila."
        )
        return

    result = random.choice(items)

    chat_id = update.effective_chat.id

    state = get_group_state(chat_id)
    state["fun"] = fun_type

    labels = {
        "truth": "🎭 Truth",
        "dare": "🔥 Dare",
        "would_you_rather": "🤔 Would You Rather",
        "challenge": "🎯 Challenge",
    }

    title = labels.get(
        fun_type,
        "🎲 Fun",
    )

    text = (
        f"{title}\n\n"
        f"{safe(result)}\n\n"
        "👇 Next one ke liye button dabao."
    )

    await edit_or_send_group(
        update,
        text,
        fun_keyboard(),
    )


# ============================================================
# GROUP QUESTION
# ============================================================

def question_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💬 Another Question",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}question"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "🌸 Back",
                    callback_data=f"{GROUP_CALLBACK_PREFIX}menu",
                ),
            ],
        ]
    )


async def show_group_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):
        return

    if not setting_enabled(
        context,
        "group_question",
    ):
        await answer_callback(
            update,
            "💬 Group Question disabled hai.",
        )
        return

    question = random.choice(
        GROUP_QUESTIONS
    )

    chat_id = update.effective_chat.id

    state = get_group_state(chat_id)
    state["question"] = question

    text = (
        "💬 Group Question\n\n"
        f"{safe(question)}\n\n"
        "Sab apna answer de sakte ho. 🌸"
    )

    await edit_or_send_group(
        update,
        text,
        question_keyboard(),
    )


# ============================================================
# GROUP MYSTERY MENU
# ============================================================

def mystery_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🕵️ New Mystery",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}newmystery"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔎 Next Clue",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}clue"
                    ),
                ),
                InlineKeyboardButton(
                    "💡 Hint",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}hint"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "🎯 Solve",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}solve"
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    "🌸 Back",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}menu"
                    ),
                ),
            ],
        ]
    )


# ============================================================
# MYSTERY ANSWER KEYBOARD
# ============================================================

def mystery_answer_keyboard(
    mystery: Dict[str, Any],
) -> InlineKeyboardMarkup:

    correct_answer = str(
        mystery.get("answer", "")
    )

    all_answers = [
        str(item.get("answer", ""))
        for item in GROUP_MYSTERIES
    ]

    options = list(
        dict.fromkeys(all_answers)
    )

    random.shuffle(options)

    if correct_answer not in options:
        options.append(correct_answer)

    options = options[:3]

    if correct_answer not in options:
        options[-1] = correct_answer

    buttons = []

    for answer in options:
        buttons.append(
            [
                InlineKeyboardButton(
                    f"🔎 {answer}",
                    callback_data=(
                        f"{GROUP_CALLBACK_PREFIX}"
                        f"answer|{answer}"
                    ),
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "🌸 Back",
                callback_data=(
                    f"{GROUP_CALLBACK_PREFIX}mystery"
                ),
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)


# ============================================================
# START GROUP MYSTERY
# ============================================================

async def start_group_mystery(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):
        return

    if not setting_enabled(
        context,
        "group_mystery",
    ):
        await answer_callback(
            update,
            "🕵️ Group Mystery disabled hai.",
        )
        return

    mystery = random.choice(
        GROUP_MYSTERIES
    )

    chat_id = update.effective_chat.id

    state = get_group_state(chat_id)

    state["mystery"] = mystery
    state["mystery_clue"] = 0

    first_clue = mystery["clues"][0]

    text = (
        f"{safe(mystery['title'])}\n\n"
        "Case open hai. 🕵️\n\n"
        f"🔎 {safe(first_clue)}\n\n"
        "Group milkar solve karo!"
    )

    await edit_or_send_group(
        update,
        text,
        mystery_keyboard(),
    )


# ============================================================
# NEXT CLUE
# ============================================================

async def next_group_clue(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    chat = update.effective_chat

    if not chat:
        return

    state = get_group_state(chat.id)

    mystery = state.get("mystery")

    if not mystery:
        await answer_callback(
            update,
            "🕵️ Pehle new mystery start karo.",
        )
        return

    clue_index = int(
        state.get(
            "mystery_clue",
            0,
        )
    )

    clue_index += 1

    if clue_index >= len(mystery["clues"]):

        text = (
            f"{safe(mystery['title'])}\n\n"
            "🔎 Saare clues reveal ho chuke hain!\n\n"
            "🎯 Ab answer guess karo."
        )

        state["mystery_clue"] = (
            len(mystery["clues"]) - 1
        )

        await edit_or_send_group(
            update,
            text,
            mystery_keyboard(),
        )

        return

    state["mystery_clue"] = clue_index

    clue = mystery["clues"][clue_index]

    text = (
        f"{safe(mystery['title'])}\n\n"
        f"🔎 Clue {clue_index + 1}\n"
        f"{safe(clue)}\n\n"
        "🕵️ Think carefully..."
    )

    await edit_or_send_group(
        update,
        text,
        mystery_keyboard(),
    )


# ============================================================
# MYSTERY HINT
# ============================================================

async def group_mystery_hint(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    chat = update.effective_chat

    if not chat:
        return

    state = get_group_state(chat.id)

    mystery = state.get("mystery")

    if not mystery:
        await answer_callback(
            update,
            "🕵️ Pehle mystery start karo.",
        )
        return

    answer = str(
        mystery["answer"]
    )

    if len(answer) <= 2:
        hint = answer[0] + "_"
    else:
        hint = (
            answer[0]
            + ("_ " * (len(answer) - 2))
            + answer[-1]
        )

    text = (
        f"{safe(mystery['title'])}\n\n"
        "💡 Hint:\n"
        f"Answer looks like: "
        f"{safe(hint)}"
    )

    await edit_or_send_group(
        update,
        text,
        mystery_keyboard(),
    )


# ============================================================
# MYSTERY SOLVE MENU
# ============================================================

async def show_mystery_solve(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    chat = update.effective_chat

    if not chat:
        return

    state = get_group_state(chat.id)

    mystery = state.get("mystery")

    if not mystery:
        await answer_callback(
            update,
            "🕵️ Pehle new mystery start karo.",
        )
        return

    text = (
        f"{safe(mystery['title'])}\n\n"
        "🎯 Final Answer\n\n"
        "Group milkar ek option choose karo. 👇"
    )

    await edit_or_send_group(
        update,
        text,
        mystery_answer_keyboard(mystery),
    )


# ============================================================
# CHECK MYSTERY ANSWER
# ============================================================

async def check_mystery_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    answer: str,
) -> None:

    query = update.callback_query

    if not query:
        return

    chat = update.effective_chat

    if not chat:
        return

    state = get_group_state(chat.id)

    mystery = state.get("mystery")

    if not mystery:
        await query.answer(
            "🕵️ Pehle mystery start karo.",
            show_alert=False,
        )
        return

    correct = str(
        mystery.get("answer", "")
    ).strip().lower()

    selected = str(
        answer
    ).strip().lower()

    if selected == correct:

        await query.answer(
            "🎯 Correct!",
            show_alert=False,
        )

        text = (
            f"{safe(mystery['title'])}\n\n"
            f"{safe(mystery['success'])}\n\n"
            "🌸 Mystery solved!"
        )

        state["mystery"] = None
        state["mystery_clue"] = 0

        await query.edit_message_text(
            text,
            
            reply_markup=mystery_keyboard(),
        )

        return

    await query.answer(
        "❌ Not this one. Try again!",
        show_alert=False,
    )


# ============================================================
# ADMIN MENU
# ============================================================

async def show_admin_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):
        return

    if not await is_admin(update):

        await answer_callback(
            update,
            "👑 Sirf group admins ye settings change kar sakte hain.",
        )

        return

    settings = get_settings(context)

    text = (
        "👑 Group Admin\n\n"
        "Yahan se MoodBloom group features control kar sakte ho."
    )

    await edit_or_send_group(
        update,
        text,
        admin_menu_keyboard(settings),
    )


# ============================================================
# TOGGLE SETTING
# ============================================================

async def toggle_setting(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    setting: str,
) -> None:

    if not is_group(update):
        return

    if not await is_admin(update):

        await answer_callback(
            update,
            "👑 Sirf admins settings change kar sakte hain.",
        )

        return

    settings = get_settings(context)

    if setting not in DEFAULT_GROUP_SETTINGS:

        await answer_callback(
            update,
            "Invalid setting.",
        )

        return

    settings[setting] = not settings.get(
        setting,
        DEFAULT_GROUP_SETTINGS[setting],
    )

    context.chat_data[
        GROUP_SETTINGS_KEY
    ] = settings

    await answer_callback(
        update,
        "✅ Setting updated.",
    )

    await show_admin_menu(
        update,
        context,
    )


# ============================================================
# WELCOME NEW MEMBER
# ============================================================

async def welcome_new_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not update.message:
        return

    if not is_group(update):
        return

    if not setting_enabled(
        context,
        "welcome",
    ):
        return

    members = update.message.new_chat_members

    if not members:
        return

    for member in members:

        name = member.first_name or "friend"

        message = random.choice(
            WELCOME_MESSAGES
        ).format(
            name=safe(name)
        )

        try:
            await update.message.reply_text(
                message,
                
            )
        except Exception:
            pass


# ============================================================
# GOODBYE MEMBER
# ============================================================

async def goodbye_member(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not update.message:
        return

    if not is_group(update):
        return

    if not setting_enabled(
        context,
        "goodbye",
    ):
        return

    member = update.message.left_chat_member

    if not member:
        return

    name = member.first_name or "friend"

    message = random.choice(
        GOODBYE_MESSAGES
    ).format(
        name=safe(name)
    )

    try:
        await update.message.reply_text(
            message,
            
        )
    except Exception:
        pass


# ============================================================
# CALLBACK ANSWER
# ============================================================

async def answer_callback(
    update: Update,
    text: str,
) -> None:

    query = update.callback_query

    if query:

        try:
            await query.answer(
                text,
                show_alert=False,
            )
        except Exception:
            pass


# ============================================================
# EDIT OR SEND
# ============================================================

async def edit_or_send_group(
    update: Update,
    text: str,
    keyboard: InlineKeyboardMarkup,
) -> None:

    query = update.callback_query

    if query:

        try:
            await query.answer()
        except Exception:
            pass

        try:
            await query.edit_message_text(
                text,
                
                reply_markup=keyboard,
            )
            return
        except Exception:
            pass

    if update.effective_message:

        await update.effective_message.reply_text(
            text,
            
            reply_markup=keyboard,
        )


# ============================================================
# CALLBACK ROUTER
# ============================================================

async def handle_group_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    query = update.callback_query

    if not query:
        return

    data = query.data or ""

    if not data.startswith(
        GROUP_CALLBACK_PREFIX
    ):
        return

    payload = data[
        len(GROUP_CALLBACK_PREFIX):
    ]


    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    if payload == "menu":

        if not is_group(update):

            await query.answer(
                "🌸 Ye group feature hai."
            )

            return

        await query.answer()

        await query.edit_message_text(
            "🌸 MoodBloom Group\n\n"
            "Group mein kya karna hai?",
            
            reply_markup=group_menu_keyboard(),
        )

        return


    # --------------------------------------------------------
    # MOOD
    # --------------------------------------------------------

    if payload == "mood":

        await show_group_mood(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # STORY
    # --------------------------------------------------------

    if payload == "story":

        await show_group_story(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # MYSTERY
    # --------------------------------------------------------

    if payload == "mystery":

        if not is_group(update):
            return

        text = (
            "🕵️ Group Mystery\n\n"
            "Ek case choose karo aur clues milkar solve karo."
        )

        await edit_or_send_group(
            update,
            text,
            mystery_keyboard(),
        )

        return


    # --------------------------------------------------------
    # NEW MYSTERY
    # --------------------------------------------------------

    if payload == "newmystery":

        await start_group_mystery(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # NEXT CLUE
    # --------------------------------------------------------

    if payload == "clue":

        await next_group_clue(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # HINT
    # --------------------------------------------------------

    if payload == "hint":

        await group_mystery_hint(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # SOLVE
    # --------------------------------------------------------

    if payload == "solve":

        await show_mystery_solve(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    if payload.startswith("answer|"):

        answer = payload.split(
            "|",
            1,
        )[1]

        await check_mystery_answer(
            update,
            context,
            answer,
        )

        return


    # --------------------------------------------------------
    # FUN MENU
    # --------------------------------------------------------

    if payload == "fun":

        await show_group_fun(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # FUN TYPE
    # --------------------------------------------------------

    if payload.startswith("fun|"):

        fun_type = payload.split(
            "|",
            1,
        )[1]

        await play_group_fun(
            update,
            context,
            fun_type,
        )

        return


    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    if payload == "question":

        await show_group_question(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    if payload == "admin":

        await show_admin_menu(
            update,
            context,
        )

        return


    # --------------------------------------------------------
    # TOGGLE
    # --------------------------------------------------------

    if payload.startswith("toggle|"):

        setting = payload.split(
            "|",
            1,
        )[1]

        await toggle_setting(
            update,
            context,
            setting,
        )

        return


    try:
        await query.answer()
    except Exception:
        pass


# ============================================================
# COMMAND ALIASES
# ============================================================

async def group_mood_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):

        await update.effective_message.reply_text(
            "🌸 Ye feature group ke liye hai."
        )

        return

    if not setting_enabled(
        context,
        "group_mood",
    ):

        await update.effective_message.reply_text(
            "🌸 Group Mood disabled hai."
        )

        return

    mood = random.choice(
        list(GROUP_MOODS.values())
    )

    chat_id = update.effective_chat.id

    get_group_state(chat_id)[
        "mood"
    ] = mood["name"]

    await update.effective_message.reply_text(
        f"{mood['emoji']} "
        f"Group Mood: "
        f"{safe(mood['name'])}\n\n"
        f"{safe(mood['text'])}",
        
    )


async def group_story_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):

        await update.effective_message.reply_text(
            "📖 Ye group feature hai."
        )

        return

    await show_group_story(
        update,
        context,
    )


async def group_mystery_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):

        await update.effective_message.reply_text(
            "🕵️ Ye group feature hai."
        )

        return

    await start_group_mystery(
        update,
        context,
    )


async def group_fun_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):

        await update.effective_message.reply_text(
            "🎲 Ye group feature hai."
        )

        return

    await show_group_fun(
        update,
        context,
    )


async def group_question_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not is_group(update):

        await update.effective_message.reply_text(
            "💬 Ye group feature hai."
        )

        return

    await show_group_question(
        update,
        context,
    )


# ============================================================
# REGISTER HANDLERS
# ============================================================

def register_group_handlers(application) -> None:
    """
    Register all MoodBloom group handlers.
    """

    # Main group menu
    application.add_handler(
        CommandHandler(
            "group",
            group_command,
        )
    )

    # Group features
    application.add_handler(
        CommandHandler(
            "groupmood",
            group_mood_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "groupstory",
            group_story_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "groupmystery",
            group_mystery_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "groupfun",
            group_fun_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "groupquestion",
            group_question_command,
        )
    )

    # Callback router
    application.add_handler(
        CallbackQueryHandler(
            handle_group_callback,
            pattern=r"^mbg\|",
        )
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "GROUP_MOODS",
    "GROUP_STORIES",
    "GROUP_MYSTERIES",
    "GROUP_FUN",
    "GROUP_QUESTIONS",
    "get_group_state",
    "get_settings",
    "setting_enabled",
    "is_admin",
    "is_group",
    "group_command",
    "group_mood_command",
    "group_story_command",
    "group_mystery_command",
    "group_fun_command",
    "group_question_command",
    "welcome_new_member",
    "goodbye_member",
    "handle_group_callback",
    "register_group_handlers",
]