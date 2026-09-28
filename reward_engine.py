# ============================================================
# MOODBLOOM — REWARD ENGINE
# ============================================================
# Handles:
#   🎁 Mystery Box
#   ✨ XP Rewards
#   🌱 Bloom Items
#   🎲 Random Rewards
#   📦 Reward History
#
# No Quiz / Quiz XP / Quiz Leaderboard
# ============================================================

from __future__ import annotations

import random
from typing import Any, Dict, Optional

from text_utils import bold

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

import content_engine


# ============================================================
# CONSTANTS
# ============================================================

REWARD_CALLBACK_PREFIX = "mbr|"
REWARD_SESSION_KEY = "moodbloom_reward_session"

DEFAULT_XP_REWARDS = [
    5,
    10,
    15,
    20,
    25,
    30,
]

DEFAULT_ITEMS = [
    "🌱 Mystery Seed",
    "🌸 Bloom Token",
    "✨ Sparkle",
    "💖 Heart Bloom",
    "🌙 Moon Token",
]


# ============================================================
# SESSION HELPERS
# ============================================================

def get_reward_session(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    """
    Get current reward session.
    """
    session = context.user_data.get(REWARD_SESSION_KEY)

    if not isinstance(session, dict):
        session = {}
        context.user_data[REWARD_SESSION_KEY] = session

    return session


def clear_reward_session(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Clear current reward session.
    """
    context.user_data.pop(REWARD_SESSION_KEY, None)


# ============================================================
# SAFE USER ID
# ============================================================

def get_user_id(update: Update) -> Optional[int]:
    """
    Safely get Telegram user ID.
    """
    if update.effective_user:
        return update.effective_user.id

    return None


# ============================================================
# REWARD CREATION
# ============================================================

def create_random_reward() -> Dict[str, Any]:
    """
    Create one random Mystery Box reward.

    Reward types:
        XP
        ITEM
    """

    reward_type = random.choice(["xp", "xp", "item"])

    if reward_type == "xp":
        xp = random.choice(DEFAULT_XP_REWARDS)

        return {
            "type": "xp",
            "value": xp,
            "name": f"+{xp} XP",
            "emoji": "✨",
        }

    item = random.choice(DEFAULT_ITEMS)

    return {
        "type": "item",
        "value": item,
        "name": item,
        "emoji": "🎁",
    }


# ============================================================
# FORMAT REWARD
# ============================================================

def format_reward(reward: Dict[str, Any]) -> str:
    """
    Convert reward dictionary into friendly text.
    """

    reward_type = reward.get("type", "item")
    value = reward.get("value", "")

    if reward_type == "xp":
        return f"✨ {bold(f'+{value} XP')}"

    return f"🎁 {bold(value)}"


# ============================================================
# OPEN BOX KEYBOARD
# ============================================================

def mystery_box_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown before opening the box.
    """

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎁 Open Mystery Box",
                    callback_data=f"{REWARD_CALLBACK_PREFIX}open",
                )
            ],
        ]
    )


# ============================================================
# RESULT KEYBOARD
# ============================================================

def result_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard shown after opening a box.
    """

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎁 Open Again",
                    callback_data=f"{REWARD_CALLBACK_PREFIX}open",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🌸 Bloom Menu",
                    callback_data=f"{REWARD_CALLBACK_PREFIX}close",
                ),
            ],
        ]
    )


# ============================================================
# SHOW MYSTERY BOX
# ============================================================

async def show_mystery_box(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Display Mystery Box screen.
    """

    text = (
        "🎁 <b>Mystery Box</b>\n\n"
        "Ek chhota sa surprise aapka wait kar raha hai. 🌸\n\n"
        "Box kholo aur dekho aaj kya milta hai ✨"
    )

    if update.callback_query:
        query = update.callback_query

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=mystery_box_keyboard(),
        )

    elif update.effective_message:
        await update.effective_message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=mystery_box_keyboard(),
        )


# ============================================================
# GET CONTENT ENGINE REWARD
# ============================================================

def get_engine_reward(user_id: int) -> Dict[str, Any]:
    """
    Try to get reward from ContentEngine.

    Falls back to local random reward if necessary.
    """

    try:
        reward = content_engine.get_mystery_box_reward(user_id)

        if isinstance(reward, dict):
            return reward

    except Exception:
        pass

    return create_random_reward()


# ============================================================
# OPEN MYSTERY BOX
# ============================================================

async def open_mystery_box(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Open Mystery Box and show reward.
    """

    user_id = get_user_id(update)

    if user_id is None:
        return

    session = get_reward_session(context)

    # --------------------------------------------------------
    # Prevent accidental double click
    # --------------------------------------------------------

    if session.get("opening"):
        if update.callback_query:
            await update.callback_query.answer(
                "🎁 Box already opening...",
                show_alert=False,
            )

        return

    session["opening"] = True

    try:
        reward = get_engine_reward(user_id)

        # ----------------------------------------------------
        # Save reward session
        # ----------------------------------------------------

        session["last_reward"] = reward

        # ----------------------------------------------------
        # Reward text
        # ----------------------------------------------------

        reward_text = format_reward(reward)

        text = (
            "🎁 <b>Mystery Box Opened!</b>\n\n"
            "✨ Aapko mila:\n\n"
            f"{reward_text}\n\n"
            "🌸 Keep blooming!"
        )

        # ----------------------------------------------------
        # Show result
        # ----------------------------------------------------

        if update.callback_query:
            query = update.callback_query

            await query.answer("🎁 Reward mil gaya!")

            await query.edit_message_text(
                text,
                parse_mode="HTML",
                reply_markup=result_keyboard(),
            )

        elif update.effective_message:
            await update.effective_message.reply_text(
                text,
                parse_mode="HTML",
                reply_markup=result_keyboard(),
            )

    finally:
        session["opening"] = False


# ============================================================
# COMMAND
# ============================================================

async def reward_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    /reward command.
    """

    await show_mystery_box(update, context)


# ============================================================
# CALLBACK HANDLER
# ============================================================

async def handle_reward_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Handle Mystery Box callbacks.
    """

    query = update.callback_query

    if not query:
        return

    data = query.data or ""

    if not data.startswith(REWARD_CALLBACK_PREFIX):
        return

    action = data[len(REWARD_CALLBACK_PREFIX):]

    # --------------------------------------------------------
    # OPEN
    # --------------------------------------------------------

    if action == "open":
        await open_mystery_box(update, context)
        return

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    if action == "close":
        clear_reward_session(context)

        await query.answer()

        await query.edit_message_text(
            "🌸 <b>MoodBloom</b>\n\n"
            "Jab mann kare, phir milte hain. 💖",
            parse_mode="HTML",
        )

        return

    await query.answer()


# ============================================================
# LAST REWARD
# ============================================================

def get_last_reward(
    context: ContextTypes.DEFAULT_TYPE,
) -> Optional[Dict[str, Any]]:
    """
    Return last reward from current session.
    """

    session = get_reward_session(context)

    reward = session.get("last_reward")

    if isinstance(reward, dict):
        return reward

    return None


# ============================================================
# REWARD NAME
# ============================================================

def get_last_reward_name(
    context: ContextTypes.DEFAULT_TYPE,
) -> Optional[str]:
    """
    Return last reward name.
    """

    reward = get_last_reward(context)

    if not reward:
        return None

    return str(
        reward.get(
            "name",
            reward.get("value", ""),
        )
    )


# ============================================================
# REGISTER HANDLERS
# ============================================================

def register_reward_handlers(application) -> None:
    """
    Register Mystery Box handlers.
    """

    application.add_handler(
        CommandHandler(
            "reward",
            reward_command,
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_reward_callback,
            pattern=r"^mbr\|",
        )
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "reward_command",
    "show_mystery_box",
    "open_mystery_box",
    "handle_reward_callback",
    "register_reward_handlers",
    "get_last_reward",
    "get_last_reward_name",
]