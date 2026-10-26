import datetime
import ssl
import json
import random
import os
import sys
import atexit
from io import BytesIO

from telegram import (
    Update,
    BotCommand,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    TypeHandler,
    filters,
)
from telegram.request import HTTPXRequest

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import config
import database
import moods
import analytics
import messages
import keyboards
import group_data
import scheduler

import goals
import rewards
import xp_system
import v4_data
import birthdays
import group_analytics
import study
import notifications

import story_engine
import mystery_engine

# ============================================================
# SETTINGS
# ============================================================

ANIMATION_FILE_ID = None


# ============================================================
# SAFE HELPERS
# ============================================================

import re as _re


def _clean_display_text(text):
    """Passthrough — parse_mode is now auto-detected per message
    instead of lossily rewriting tags (see edit_menu_message)."""
    if not isinstance(text, str):
        return text
    return text


def _auto_parse_mode(text):
    """
    Detects whether `text` was written with HTML tags or plain
    Markdown, so the right parse_mode is used automatically.

    This replaces the old approach of defaulting every menu to
    Markdown and rewriting / tags into asterisks/backticks
    — that silently broke any text style the converter didn't know
    about and left raw tags visible on screen.
    """
    if isinstance(text, str) and _re.search(
        r"</?(b|i|u|em|code|strong)>", text
    ):
        return "HTML"
    return "Markdown"


async def safe_answer(query):
    """
    Safely answers a Telegram callback query.
    """

    try:
        await query.answer()
    except Exception:
        pass


async def edit_menu_message(
    query,
    text,
    reply_markup=None,
    parse_mode=None,
):
    """
    Safely edits an existing menu message.

    Handles text and media messages. When parse_mode isn't given
    explicitly, it's auto-detected from the text (HTML tags vs
    plain Markdown) so callers don't have to remember to pass it.
    """

    try:

        message = query.message

        if not message:
            return

        text = _clean_display_text(text)

        if parse_mode is None:
            parse_mode = _auto_parse_mode(text)

        # ----------------------------------------------------
        # Media message
        # ----------------------------------------------------

        if (
            message.animation
            or message.photo
            or message.video
        ):

            try:

                await message.edit_caption(
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )

                return

            except Exception:
                pass

        # ----------------------------------------------------
        # Normal text message
        # ----------------------------------------------------

        try:

            await message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )

            return

        except Exception:
            pass

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        try:

            await message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )

        except Exception:
            pass

    except Exception as error:

        print(
            "edit_menu_message error:",
            error
        )


async def show_v4_goals(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if not user:
        return

    user_id = user.id

    v4_data.get_user(user_id)

    daily_goals = goals.get_daily_goals(user_id)
    progress = goals.get_goal_progress(user_id)

    lines = [
        "🎯 DAILY BLOOM GOALS",
        "━━━━━━━━━━━━━━━━━━",
        "",
        f"📅 Today's Progress: "
        f"{progress['completed']}/{progress['total']}",
        f"{goals.progress_bar(user_id)} "
        f"{progress['percentage']}%",
        "",
    ]

    for goal in daily_goals:
        if goal.get("completed"):
            status = "✅"
        else:
            status = "⬜"

        lines.append(
            f"{status} {goal.get('icon', '🎯')} "
            f"{goal['title']} "
            f"(+{goal['xp']} XP)"
        )

        if goal.get("description"):
            lines.append(
                f"   └ {goal['description']}"
            )

        lines.append("")

    text = "\n".join(lines)

    keyboard = keyboards.goals_keyboard(daily_goals)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            text,
            
            reply_markup=keyboard,
        )

async def show_v4_reward(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if not user:
        return

    user_id = user.id

    v4_data.get_user(user_id)

    reward = rewards.get_daily_reward(user_id)

    data = v4_data.load_v4_data()
    user_rewards = data["rewards"].get(
        str(user_id),
        {},
    )

    claimed = bool(
        user_rewards.get("claimed", False)
    )

    if claimed:
        status = "✅ Already Claimed Today"
    else:
        status = "🎁 Available to Claim"

    text = (
        "🎁 DAILY BLOOM REWARD\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌸 {reward['title']}\n\n"
        f"💌 {reward['message']}\n\n"
        f"✨ Reward XP: +{reward['xp']} XP\n\n"
        f"{status}\n\n"
        "Come back tomorrow for a new reward. 🌱"
    )

    keyboard = keyboards.reward_keyboard(
        claimed=claimed
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            text,
            
            reply_markup=keyboard,
        )


# ============================================================
# MOODBLOOM 4.0 — BIRTHDAY SYSTEM
# ============================================================

async def show_birthday_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Shows the main Birthday menu: current status + upcoming.
    """

    user = update.effective_user

    if not user:
        return

    user_id = user.id

    record = birthdays.get_birthday(user_id)

    if record:
        formatted = birthdays.format_birthday_record(
            record,
            include_year=True,
            include_age=True,
        )
        status_line = f"🎂 Your birthday: {formatted}"
    else:
        status_line = (
            "🎂 You haven't added your birthday yet."
        )

    next_birthday = birthdays.get_next_birthday()

    if next_birthday:

        name = birthdays.get_display_name(next_birthday)
        days = next_birthday.get("days_until", 0)

        if days == 0:
            upcoming_line = f"🎉 Today is {name}'s birthday!"
        elif days == 1:
            upcoming_line = f"🌸 Tomorrow is {name}'s birthday!"
        else:
            upcoming_line = (
                f"⏳ Next up: {name} in {days} days"
            )

    else:
        upcoming_line = "📅 No upcoming birthdays yet."

    text = (
        "🎂 BIRTHDAYS\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{status_line}\n\n"
        f"{upcoming_line}\n\n"
        "Manage your birthday and see who's celebrating "
        "soon. 🌸"
    )

    keyboard = keyboards.birthday_keyboard()

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            text,
            
            reply_markup=keyboard,
        )


async def birthday_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /birthday command — opens the Birthday menu.
    Supports a quick shortcut: /birthday DD-MM[-YYYY]
    """

    if context.args:

        user = update.effective_user

        result = birthdays.set_birthday(
            user.id,
            " ".join(context.args),
            first_name=user.first_name or "",
            username=user.username or "",
        )

        if not result.get("success"):
            await update.message.reply_text(
                "❌ "
                + result.get(
                    "message",
                    "Invalid date. Use DD-MM or "
                    "DD-MM-YYYY.",
                )
            )
            return

        await update.message.reply_text(
            "✅ Birthday saved: "
            f"{result['formatted']} 🎂",
            
        )

    await show_birthday_menu(update, context)


async def receive_birthday_date_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Captures the date typed after tapping Add/Update
    on the Birthday menu.
    """

    if not context.user_data.get(
        "awaiting_birthday_input"
    ):
        return

    if not update.message:
        return

    text = (update.message.text or "").strip()

    if text.lower() in ("/cancel", "cancel"):

        context.user_data["awaiting_birthday_input"] = False

        await update.message.reply_text(
            "❌ Cancelled."
        )

        await show_birthday_menu(update, context)
        return

    user = update.effective_user

    result = birthdays.set_birthday(
        user.id,
        text,
        first_name=user.first_name or "",
        username=user.username or "",
    )

    if not result.get("success"):

        await update.message.reply_text(
            "❌ "
            + result.get(
                "message",
                "Invalid format. Please try again, e.g. "
                "15-08 or 15-08-2000.",
            )
        )

        return

    context.user_data["awaiting_birthday_input"] = False

    await update.message.reply_text(
        "✅ Birthday saved: "
        f"{result['formatted']} 🎂\n\n"
        "You'll get a birthday wish from MoodBloom "
        "every year! 🌸",
        
    )

    await show_birthday_menu(update, context)


async def handle_birthday_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handles all birthday_* button presses.
    """

    query = update.callback_query

    if not query:
        return

    await safe_answer(query)

    user = update.effective_user

    if not user:
        return

    user_id = user.id
    data = query.data or ""

    # --------------------------------------------------------
    # MY BIRTHDAY
    # --------------------------------------------------------

    if data == "birthday_my":

        record = birthdays.get_birthday(user_id)

        if not record:

            text = (
                "🎂 My Birthday\n\n"
                "You haven't added your birthday yet.\n"
                "Tap ➕ Add to set it."
            )

        else:

            formatted = birthdays.format_birthday_record(
                record,
                include_year=True,
                include_age=True,
            )

            text = (
                "🎂 My Birthday\n\n"
                f"📅 {formatted}\n"
                "🔔 Reminders: "
                f"{'On' if record.get('reminder_enabled', True) else 'Off'}\n"
                "🎉 Wishes: "
                f"{'On' if record.get('wish_enabled', True) else 'Off'}\n"
                "👀 Visibility: "
                f"{'Public' if record.get('public', True) else 'Private'}"
            )

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.birthday_manage_keyboard(),
        )

        return

    # --------------------------------------------------------
    # ADD / UPDATE
    # --------------------------------------------------------

    if data in ("birthday_add", "birthday_update"):

        context.user_data["awaiting_birthday_input"] = True

        action = "Add" if data == "birthday_add" else "Update"

        text = (
            f"🎂 {action} Your Birthday\n\n"
            "Please send your birthday in one of these "
            "formats:\n"
            "• DD-MM (e.g. 15-08)\n"
            "• DD-MM-YYYY (e.g. 15-08-2000)\n\n"
            "Send /cancel to stop."
        )

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.bloom_back_keyboard(),
        )

        return

    # --------------------------------------------------------
    # REMOVE
    # --------------------------------------------------------

    if data == "birthday_remove":

        result = birthdays.remove_birthday(user_id)

        if result.get("success"):
            await query.answer(
                "🗑️ Birthday removed.",
                show_alert=True,
            )
        else:
            await query.answer(
                "You don't have a birthday saved.",
                show_alert=True,
            )

        await show_birthday_menu(update, context)
        return

    # --------------------------------------------------------
    # UPCOMING
    # --------------------------------------------------------

    if data == "birthday_upcoming":

        upcoming = birthdays.get_upcoming_birthdays(
            days=30
        )

        text = birthdays.format_birthday_list(
            upcoming,
            title="📅 Upcoming Birthdays (30 days)",
        )

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.birthday_manage_keyboard(),
        )

        return

    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

    if data == "birthday_today":

        today_list = birthdays.get_today_birthdays()

        text = birthdays.format_birthday_list(
            today_list,
            title="🎉 Today's Birthdays",
        )

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.birthday_manage_keyboard(),
        )

        return

    # --------------------------------------------------------
    # GROUP BIRTHDAYS
    # --------------------------------------------------------

    if data == "birthday_group":

        chat = update.effective_chat

        if not chat or chat.type == "private":

            text = (
                "👥 Group Birthdays\n\n"
                "This works inside a group chat.\n"
                "Add yourself there with:\n"
                "/groupbirthday DD-MM"
            )

        else:

            today_list = birthdays.get_group_today_birthdays(
                chat.id
            )

            upcoming_list = (
                birthdays.get_group_upcoming_birthdays(
                    chat.id,
                    days=30,
                )
            )

            lines = [
                "👥 Group Birthdays",
                "",
            ]

            if today_list:
                lines.append("🎉 Today:")
                for record in today_list:
                    lines.append(
                        f"• {birthdays.get_display_name(record)}"
                    )
                lines.append("")

            lines.append(
                birthdays.format_birthday_list(
                    upcoming_list,
                    title="📅 Upcoming (30 days)",
                )
            )

            lines.append("")
            lines.append(
                "Add yourself: "
                "/groupbirthday DD-MM"
            )

            text = "\n".join(lines)

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.birthday_manage_keyboard(),
        )

        return

    # --------------------------------------------------------
    # REMINDERS TOGGLE
    # --------------------------------------------------------

    if data == "birthday_reminders":

        record = birthdays.get_birthday(user_id)

        if not record:

            await query.answer(
                "Add your birthday first.",
                show_alert=True,
            )

            await show_birthday_menu(update, context)
            return

        new_state = not record.get(
            "reminder_enabled",
            True,
        )

        birthdays.update_birthday_settings(
            user_id,
            reminder_enabled=new_state,
        )

        await query.answer(
            "🔔 Reminders "
            + ("enabled." if new_state else "disabled."),
            show_alert=True,
        )

        await show_birthday_menu(update, context)
        return


async def group_birthday_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /groupbirthday DD-MM — adds/updates your birthday
    for THIS group specifically.
    """

    chat = update.effective_chat
    user = update.effective_user

    if not chat or chat.type == "private":
        await update.message.reply_text(
            "👥 This command only works inside a group."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "🎂 Usage: /groupbirthday DD-MM\n"
            "Example: /groupbirthday 15-08",
            
        )
        return

    result = birthdays.set_group_birthday(
        chat.id,
        user.id,
        " ".join(context.args),
        first_name=user.first_name or "",
        username=user.username or "",
    )

    if not result.get("success"):
        await update.message.reply_text(
            "❌ Invalid date. Use DD-MM or DD-MM-YYYY."
        )
        return

    await update.message.reply_text(
        "✅ Your birthday for this group is saved: "
        f"{birthdays.format_birthday(result['birthday']['month'], result['birthday']['day'])} 🎂",
        
    )


# ============================================================
# MOODBLOOM 4.0 — STUDY MODE
# ============================================================

def _study_job_name(user_id):
    return f"study_session_{user_id}"


async def _study_timer_complete(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Fires when a study session's timer runs out.
    Does NOT auto-complete the session — the user still
    taps ✅ Complete so it can't be gamed by starting and
    walking away.
    """

    job = context.job
    user_id = job.data.get("user_id")
    chat_id = job.data.get("chat_id")

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "⏰ Study Timer Done!\n\n"
                "Tap ✅ Complete to log this session "
                "and earn your Study goal XP. 📚"
            ),
            
            reply_markup=keyboards.study_keyboard(
                active=True
            ),
        )
    except Exception as error:
        print("Study timer notify error:", error)


async def show_study_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if not user:
        return

    summary = study.get_summary(user.id)

    if summary["active"]:

        text = (
            "📚 STUDY MODE\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🟢 A session is currently running.\n\n"
            "Tap ✅ when you're done, or 🛑 to cancel.\n\n"
            f"📈 Completed sessions: "
            f"{summary['completed_sessions']}\n"
            f"⏱️ Total study time: "
            f"{summary['total_minutes']} min"
        )

    else:

        text = (
            "📚 STUDY MODE\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Focus for a set time, then mark it complete "
            "to earn Study goal XP. 🌱\n\n"
            f"📈 Completed sessions: "
            f"{summary['completed_sessions']}\n"
            f"⏱️ Total study time: "
            f"{summary['total_minutes']} min\n\n"
            "Choose a duration to begin:"
        )

    keyboard = keyboards.study_keyboard(
        active=summary["active"]
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            text,
            
            reply_markup=keyboard,
        )


async def study_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await show_study_menu(update, context)


async def handle_study_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    await safe_answer(query)

    user = update.effective_user

    if not user:
        return

    user_id = user.id
    data = query.data or ""

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    if data.startswith("study_start_"):

        try:
            minutes = int(data[len("study_start_"):])
        except Exception:
            minutes = study.DEFAULT_STUDY_MINUTES

        result = study.start_session(
            user_id,
            minutes,
        )

        if result.get("already_active"):
            await query.answer(
                "📚 A session is already running.",
                show_alert=True,
            )
            await show_study_menu(update, context)
            return

        # Schedule a one-time timer notification.
        try:
            if context.job_queue:

                for job in context.job_queue.get_jobs_by_name(
                    _study_job_name(user_id)
                ):
                    job.schedule_removal()

                context.job_queue.run_once(
                    _study_timer_complete,
                    when=result["minutes"] * 60,
                    name=_study_job_name(user_id),
                    data={
                        "user_id": user_id,
                        "chat_id": update.effective_chat.id,
                    },
                )

        except Exception as error:
            print("Study timer schedule error:", error)

        await query.edit_message_text(
            "📚 Study Session Started!\n\n"
            f"⏱️ Duration: {result['minutes']} min\n\n"
            "Focus up — I'll ping you when time's up. 🌱",
            
            reply_markup=keyboards.study_keyboard(
                active=True
            ),
        )

        return

    # --------------------------------------------------------
    # CANCEL
    # --------------------------------------------------------

    if data == "study_cancel":

        cancelled = study.cancel_session(user_id)

        try:
            if context.job_queue:
                for job in context.job_queue.get_jobs_by_name(
                    _study_job_name(user_id)
                ):
                    job.schedule_removal()
        except Exception:
            pass

        if cancelled:
            await query.answer(
                "🛑 Session cancelled.",
                show_alert=True,
            )
        else:
            await query.answer(
                "No active session to cancel.",
                show_alert=True,
            )

        await show_study_menu(update, context)
        return

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    if data == "study_complete":

        result = study.complete_session(user_id)

        try:
            if context.job_queue:
                for job in context.job_queue.get_jobs_by_name(
                    _study_job_name(user_id)
                ):
                    job.schedule_removal()
        except Exception:
            pass

        if not result.get("success"):
            await query.answer(
                "No active session to complete.",
                show_alert=True,
            )
            await show_study_menu(update, context)
            return

        goal_result = result.get("goal") or {}

        xp_line = ""

        if goal_result.get("success"):
            xp_line = (
                f"✨ Study goal completed: "
                f"+{goal_result.get('xp', 0)} XP\n\n"
            )

        text = (
            "🎉 SESSION COMPLETE!\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ You studied for "
            f"{result['minutes']} min\n\n"
            f"{xp_line}"
            f"📈 Total sessions: "
            f"{result['sessions']}\n"
            f"⏳ Total time: "
            f"{result['total_minutes']} min\n\n"
            "Great focus! Keep blooming. 🌸"
        )

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.study_keyboard(
                active=False
            ),
        )

        return


# ============================================================
# MOODBLOOM 4.0 — NOTIFICATION SETTINGS
# ============================================================

async def show_notification_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    if not user:
        return

    settings = notifications.get_notification_settings(
        user.id
    )

    text = notifications.format_notification_settings(
        user.id
    )

    keyboard = keyboards.notification_settings_keyboard(
        settings
    )

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


async def notifications_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await show_notification_menu(update, context)


async def show_quiet_hours_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    settings = notifications.get_notification_settings(
        user.id
    )

    quiet = settings.get("quiet_hours", {}) or {}

    text = (
        "🔕 Quiet Hours\n\n"
        "During quiet hours, MoodBloom won't send you "
        "notifications.\n\n"
        f"Status: "
        f"{'🔕 ON' if quiet.get('enabled') else '🔔 OFF'}\n"
        f"Range: {quiet.get('start', '23:00')} → "
        f"{quiet.get('end', '07:00')}"
    )

    await update.callback_query.edit_message_text(
        text,
        
        reply_markup=keyboards.quiet_hours_keyboard(
            settings
        ),
    )


async def show_custom_reminders_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    reminders = notifications.get_custom_reminders(
        user.id
    )

    if reminders:
        text = (
            "📝 Custom Reminders\n\n"
            "Tap a reminder to manage it, or add a new one."
        )
    else:
        text = (
            "📝 Custom Reminders\n\n"
            "You don't have any custom reminders yet. "
            "Add one below! ⏰"
        )

    await update.callback_query.edit_message_text(
        text,
        
        reply_markup=keyboards.custom_reminders_keyboard(
            reminders
        ),
    )


async def handle_notification_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    await safe_answer(query)

    user = update.effective_user

    if not user:
        return

    user_id = user.id
    data = query.data or ""

    # --------------------------------------------------------
    # TOGGLE A NOTIFICATION TYPE
    # --------------------------------------------------------

    if data.startswith("notif_toggle_"):

        key = data[len("notif_toggle_"):]

        current = notifications.get_notification_settings(
            user_id
        )

        new_value = not current.get(key, True)

        notifications.update_notification_settings(
            user_id,
            **{key: new_value}
        )

        await show_notification_menu(update, context)
        return

    # --------------------------------------------------------
    # QUIET HOURS MENU
    # --------------------------------------------------------

    if data == "notif_quiet_menu":
        await show_quiet_hours_menu(update, context)
        return

    if data == "notif_quiet_toggle":

        current = notifications.get_notification_settings(
            user_id
        )

        quiet = current.get("quiet_hours", {}) or {}

        notifications.update_notification_settings(
            user_id,
            quiet_hours_enabled=not quiet.get(
                "enabled",
                False,
            ),
        )

        await show_quiet_hours_menu(update, context)
        return

    if data == "notif_quiet_set":

        context.user_data[
            "awaiting_quiet_hours_input"
        ] = True

        await query.edit_message_text(
            "🔕 Set Quiet Hours\n\n"
            "Send the range as "
            "HH:MM-HH:MM\n"
            "Example: 23:00-07:00\n\n"
            "Send /cancel to stop.",
            
        )

        return

    # --------------------------------------------------------
    # CUSTOM REMINDERS
    # --------------------------------------------------------

    if data == "notif_reminders":
        await show_custom_reminders_menu(update, context)
        return

    if data == "notif_rem_add":

        context.user_data[
            "awaiting_reminder_input"
        ] = True

        await query.edit_message_text(
            "📝 Add Custom Reminder\n\n"
            "Send it as:\n"
            "Title | HH:MM | Message\n\n"
            "Example:\n"
            "Drink Water | 15:30 | Stay "
            "hydrated! 💧\n\n"
            "(Message is optional.)\n"
            "Send /cancel to stop.",
            
        )

        return

    if data.startswith("notif_rem_view_"):

        reminder_id = data[len("notif_rem_view_"):]

        reminder = notifications.get_custom_reminder(
            user_id,
            reminder_id,
        )

        if not reminder:
            await query.answer(
                "Reminder not found.",
                show_alert=True,
            )
            await show_custom_reminders_menu(
                update, context
            )
            return

        text = (
            "📝 "
            f"{reminder.get('title', '')}\n\n"
            f"⏰ Time: {reminder.get('time', '')}\n"
            f"💬 Message: "
            f"{reminder.get('message') or '—'}\n"
            f"Status: "
            f"{'🟢 Enabled' if reminder.get('enabled', True) else '🔴 Disabled'}"
        )

        await query.edit_message_text(
            text,
            
            reply_markup=(
                keyboards.custom_reminder_view_keyboard(
                    reminder_id
                )
            ),
        )

        return

    if data.startswith("notif_rem_del_"):

        reminder_id = data[len("notif_rem_del_"):]

        deleted = notifications.delete_custom_reminder(
            user_id,
            reminder_id,
        )

        await query.answer(
            "🗑️ Reminder deleted."
            if deleted
            else "Couldn't delete that reminder.",
            show_alert=True,
        )

        await show_custom_reminders_menu(update, context)
        return

    # --------------------------------------------------------
    # STATS
    # --------------------------------------------------------

    if data == "notif_stats":

        text = notifications.format_notification_stats(
            user_id
        )

        back_keyboard = keyboards.markup([
            [
                keyboards.button(
                    "⬅️ Back",
                    "v4_notifications",
                ),
            ],
        ])

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=back_keyboard,
        )

        return


async def receive_quiet_hours_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not context.user_data.get(
        "awaiting_quiet_hours_input"
    ):
        return

    if not update.message:
        return

    text = (update.message.text or "").strip()

    if text.lower() in ("/cancel", "cancel"):

        context.user_data[
            "awaiting_quiet_hours_input"
        ] = False

        await update.message.reply_text("❌ Cancelled.")
        await show_notification_menu(update, context)
        return

    parts = text.split("-")

    if len(parts) != 2:

        await update.message.reply_text(
            "❌ Invalid format. Use "
            "HH:MM-HH:MM, e.g. "
            "23:00-07:00",
            
        )
        return

    user = update.effective_user

    result = notifications.update_notification_settings(
        user.id,
        quiet_start=parts[0].strip(),
        quiet_end=parts[1].strip(),
        quiet_hours_enabled=True,
    )

    if "quiet_start" not in result.get("changed", {}):

        await update.message.reply_text(
            "❌ Couldn't parse those times. Try "
            "23:00-07:00.",
            
        )
        return

    context.user_data[
        "awaiting_quiet_hours_input"
    ] = False

    await update.message.reply_text(
        "✅ Quiet hours updated & enabled 🔕"
    )

    await show_notification_menu(update, context)


async def receive_custom_reminder_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not context.user_data.get(
        "awaiting_reminder_input"
    ):
        return

    if not update.message:
        return

    text = (update.message.text or "").strip()

    if text.lower() in ("/cancel", "cancel"):

        context.user_data[
            "awaiting_reminder_input"
        ] = False

        await update.message.reply_text("❌ Cancelled.")
        await show_notification_menu(update, context)
        return

    parts = [
        part.strip()
        for part in text.split("|")
    ]

    if len(parts) < 2:

        await update.message.reply_text(
            "❌ Invalid format. Use:\n"
            "Title | HH:MM | Message",
            
        )
        return

    title = parts[0]
    reminder_time = parts[1]
    message = parts[2] if len(parts) > 2 else ""

    user = update.effective_user

    reminder = notifications.add_custom_reminder(
        user.id,
        title,
        reminder_time,
        message=message,
    )

    if not reminder:

        await update.message.reply_text(
            "❌ Couldn't add that reminder. Check the "
            "time format (HH:MM) and try again."
        )
        return

    context.user_data[
        "awaiting_reminder_input"
    ] = False

    await update.message.reply_text(
        f"✅ Reminder added: {title} at "
        f"{reminder_time} ⏰",
        
    )

    await show_notification_menu(update, context)


# ============================================================
# MOODBLOOM 4.0 — V4 CALLBACK HANDLER
# ============================================================

async def handle_v4_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    if not query:
        return

    await query.answer()

    user = update.effective_user

    if not user:
        return

    user_id = user.id
    data = query.data or ""

    # --------------------------------------------------------
    # BLOOM DASHBOARD
    # --------------------------------------------------------

    if data == "v4_bloom":
        level = xp_system.get_progress(user_id)
        goal_progress = goals.get_goal_progress(user_id)

        text = (
            "🌸 MOODBLOOM — BLOOM JOURNEY\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 {user.first_name}\n\n"
            f"⭐ Level {level['level']} — "
            f"{level['title']}\n"
            f"✨ XP: {level['xp']}\n\n"
            f"📈 Progress: {level['progress']}%\n"
            f"{xp_system.progress_bar(user_id)}\n\n"
            f"🎯 Today's Goals\n"
            f"{goals.progress_bar(user_id)} "
            f"{goal_progress['completed']}/"
            f"{goal_progress['total']}\n\n"
            "🌱 Every small step makes your Bloom Journey "
            "stronger. 💖"
        )

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.bloom_dashboard_keyboard(),
        )

        return

    # --------------------------------------------------------
    # DAILY GOALS
    # --------------------------------------------------------

    if data == "v4_goals":
        await show_v4_goals(update, context)
        return

    # --------------------------------------------------------
    # DAILY REWARD
    # --------------------------------------------------------

    if data == "v4_reward":
        await show_v4_reward(update, context)
        return

    # --------------------------------------------------------
    # BIRTHDAYS
    # --------------------------------------------------------

    if data == "v4_birthdays":
        await show_birthday_menu(update, context)
        return

    # --------------------------------------------------------
    # STUDY MODE
    # --------------------------------------------------------

    if data == "v4_study":
        await show_study_menu(update, context)
        return

    # --------------------------------------------------------
    # NOTIFICATIONS
    # --------------------------------------------------------

    if data == "v4_notifications":
        await show_notification_menu(update, context)
        return


    # --------------------------------------------------------
    # XP PROFILE
    # --------------------------------------------------------

    if data == "v4_xp":
        info = xp_system.get_progress(user_id)

        text = (
            "⭐ YOUR BLOOM LEVEL\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🌸 Level: {info['level']}\n"
            f"🏷️ Title: {info['title']}\n"
            f"✨ XP: {info['xp']}\n\n"
            f"{xp_system.progress_bar(user_id)}\n"
            f"📈 Progress: {info['progress']}%\n"
        )

        if info["next_level_xp"] is not None:
            text += (
                f"\n🚀 Next Level: "
                f"{info['next_level_xp']} XP\n"
                f"🎯 Remaining: "
                f"{info['remaining']} XP"
            )
        else:
            text += "\n🏆 MAX LEVEL REACHED!"

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.xp_keyboard(),
        )

        return

    # --------------------------------------------------------
    # COMPLETE GOAL
    # --------------------------------------------------------

    if data.startswith("v4_goal_"):
        goal_id = data[len("v4_goal_"):]

        # Safety check for the already-completed button
        if goal_id == "done":
            return

        result = goals.complete_goal(
            user_id,
            goal_id,
        )

        if result.get("already_completed"):
            await query.answer(
                "✅ Ye goal already complete hai!",
                show_alert=True,
            )
            return

        if not result.get("success"):
            await query.answer(
                "⚠️ Goal nahi mila.",
                show_alert=True,
            )
            return

        goal = result.get("goal", {})

        progress = goals.get_goal_progress(
            user_id
        )

        level_info = xp_system.get_progress(
            user_id
        )

        text = (
            "🎉 GOAL COMPLETED!\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"{goal.get('icon', '🎯')} "
            f"{goal.get('title', 'Goal')}\n\n"
            f"✨ You earned "
            f"+{result['xp']} XP\n\n"
            f"🎯 Today's Progress:\n"
            f"{goals.progress_bar(user_id)} "
            f"{progress['completed']}/"
            f"{progress['total']}\n\n"
            f"⭐ Current Level: "
            f"{level_info['level']}"
        )

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.goals_keyboard(
                goals.get_daily_goals(user_id)
            ),
        )

        return

    # --------------------------------------------------------
    # CLAIM DAILY REWARD
    # --------------------------------------------------------

    if data == "v4_claim_reward":
        result = rewards.claim_daily_reward(
            user_id
        )

        if result.get("already_claimed"):
            await query.answer(
                "🎁 Aaj ka reward already claim ho chuka hai!",
                show_alert=True,
            )

            await show_v4_reward(
                update,
                context,
            )
            return

        if not result.get("success"):
            await query.answer(
                "⚠️ Reward claim nahi ho paya.",
                show_alert=True,
            )
            return

        reward = result.get(
            "reward",
            {},
        )

        level_info = xp_system.get_progress(
            user_id
        )

        text = (
            "🎉 REWARD CLAIMED!\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🌸 {reward.get('title', 'Bloom Reward')}\n\n"
            f"💌 {reward.get('message', '')}\n\n"
            f"✨ You earned "
            f"+{result.get('xp', 0)} XP\n\n"
            f"⭐ Current Level: "
            f"{level_info['level']}\n\n"
            "Come back tomorrow for another reward. 🌱"
        )

        await query.edit_message_text(
            text,
            
            reply_markup=keyboards.reward_keyboard(
                claimed=True
            ),
        )

        return
    
# ============================================================
# ACTIVITY REGISTRATION
# ============================================================

async def register_activity(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Automatically registers users and groups
    whenever activity is received.
    """

    try:

        chat = update.effective_chat

        if not chat:
            return

        # ----------------------------------------------------
        # Private user
        # ----------------------------------------------------

        if chat.type == "private":

            user = update.effective_user

            if not user:
                return

            database.register_user(
                user.id,
                user.username or "",
                user.first_name or "",
            )

            database.update_user_last_seen(
                user.id
            )

        # ----------------------------------------------------
        # Group / Supergroup
        # ----------------------------------------------------

        elif chat.type in (
            "group",
            "supergroup",
        ):

            database.register_group(
                chat.id,
                chat.title or "This Group",
                getattr(
                    chat,
                    "username",
                    ""
                ) or "",
            )

            database.update_group_last_seen(
                chat.id
            )

            # ------------------------------------------------
            # Track message activity for the V4 group
            # analytics/leaderboard system. Only real
            # messages count (not callback taps, joins etc.)
            # ------------------------------------------------

            user = update.effective_user

            if (
                update.message
                and user
                and not user.is_bot
            ):

                try:

                    group_analytics.record_message(
                        chat.id,
                        user.id,
                        username=user.username or "",
                        first_name=user.first_name or "",
                        title=chat.title or "",
                        chat_type=chat.type,
                    )

                except Exception as error:

                    print(
                        "Group analytics record error:",
                        error
                    )

    except Exception as error:

        print(
            "Activity registration error:",
            error
        )


# ============================================================
# USER REMINDER HELPERS
# ============================================================

def remove_existing_reminder_jobs(
    application,
    user_id,
):
    """
    Removes existing reminder jobs for a user.
    """

    try:

        job_queue = application.job_queue

    except Exception:

        job_queue = None

    if not job_queue:
        return

    try:

        jobs = job_queue.get_jobs_by_name(
            f"daily_reminder_{user_id}"
        )

        for job in jobs:
            job.schedule_removal()

    except Exception as error:

        print(
            "Reminder job removal error:",
            error
        )


def schedule_user_reminder(
    application,
    user_id,
    hour,
    minute,
):
    """
    Schedules one daily reminder.
    """

    try:

        job_queue = application.job_queue

    except Exception:

        job_queue = None

    if not job_queue:

        print(
            "JobQueue unavailable. "
            "Install python-telegram-bot[job-queue]."
        )

        return False

    # --------------------------------------------------------
    # Validate time
    # --------------------------------------------------------

    try:

        hour = int(hour)
        minute = int(minute)

        if not 0 <= hour <= 23:
            return False

        if not 0 <= minute <= 59:
            return False

    except Exception:

        return False

    remove_existing_reminder_jobs(
        application,
        user_id,
    )

    try:

        job_queue.run_daily(
            send_daily_reminder,
            time=datetime.time(
                hour=hour,
                minute=minute,
                tzinfo=config.TIMEZONE,
            ),
            data={
                "user_id": user_id
            },
            name=f"daily_reminder_{user_id}",
        )

        return True

    except Exception as error:

        print(
            "Reminder scheduling error:",
            error
        )

        return False


# ============================================================
# STATISTICS HELPERS
# ============================================================

def build_stats_summary(history):
    """
    Builds statistics using functions that actually exist
    in analytics.py.

    This replaces the old analytics.analytics_summary()
    dependency.
    """

    total = analytics.total_checkins(history)

    if total <= 0:

        return {
            "has_data": False,
            "total_checkins": 0,
            "unique_days": 0,
            "favorite_mood": None,
            "level": analytics.get_level(history),
            "xp": analytics.get_xp(history),
            "current_streak": analytics.current_streak(history),
            "best_streak": analytics.best_streak(history),
            "average_mood_score": 0,
            "score_label": "No data yet",
            "trend": {
                "direction": "new"
            },
        }

    favorite = analytics.favorite_mood(
        history
    )

    average_score = analytics.average_mood_score(
        history
    )

    trend = analytics.mood_trend(
        history
    )

    # --------------------------------------------------------
    # Get score label safely
    # --------------------------------------------------------

    score_label = "Balanced"

    try:

        insight_data = analytics.smart_insights(
            history
        )

        score_label = insight_data.get(
            "score_label",
            score_label
        )

    except Exception:

        try:

            if average_score >= 4:
                score_label = "Very Positive"

            elif average_score >= 3:
                score_label = "Positive / Balanced"

            elif average_score >= 2:
                score_label = "Low / Mixed"

            else:
                score_label = "Needs Attention"

        except Exception:
            pass

    return {
        "has_data": True,
        "total_checkins": total,
        "unique_days": analytics.unique_days(history),
        "favorite_mood": favorite,
        "level": analytics.get_level(history),
        "xp": analytics.get_xp(history),
        "current_streak": analytics.current_streak(history),
        "best_streak": analytics.best_streak(history),
        "average_mood_score": average_score,
        "score_label": score_label,
        "trend": trend,
    }


def build_export_file(
    history,
    user_id,
):
    """
    Creates an in-memory JSON export file.
    """

    payload = json.dumps(
        history,
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")

    filename = f"moodbloom_history_{user_id}.json"

    document = BytesIO(payload)
    document.name = filename

    return document


# ============================================================
# START / DASHBOARD
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /start command.
    """

    user = update.effective_user

    if not user:
        return

    user_id = user.id

    try:

        history = database.get_user_history(
            user_id
        )

    except Exception:

        history = []

    total = analytics.total_checkins(
        history
    )

    level = analytics.get_level(
        history
    )

    xp = analytics.get_xp(
        history
    )

    streak = analytics.current_streak(
        history
    )

    progress = analytics.get_level_progress(
        history
    )

    progress_bar = analytics.get_progress_bar(
        history
    )

    first_name = (
        user.first_name
        or "there"
    )

    text = (
        f"🌸 *Welcome to {config.BOT_NAME}, "
        f"{first_name}!*\n\n"

        "Your little space for tracking "
        "moods, habits and daily feelings. 💗\n\n"

        f"🌱 Check-ins: *{total}*\n"
        f"🔥 Streak: *{streak} days*\n"
        f"⭐ Level: *{level}*\n"
        f"✨ XP: *{xp}*\n\n"

        f"{progress_bar}\n"
        f"*{progress}/100 XP*\n\n"

        "💭 How are you feeling today?"
    )

    try:

        if ANIMATION_FILE_ID:

            await update.message.reply_animation(
                animation=ANIMATION_FILE_ID,
                caption=text,
                parse_mode="Markdown",
                reply_markup=keyboards.home_keyboard(),
            )

        else:

            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=keyboards.home_keyboard(),
            )

    except Exception as error:

        print(
            "Start error:",
            error
        )

        try:

            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=keyboards.home_keyboard(),
            )

        except Exception:
            pass


# ============================================================
# MOODBLOOM 4.0 — BLOOM DASHBOARD
# ============================================================

async def bloom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not user:
        return

    user_id = user.id

    # Make sure V4 profile exists
    v4_data.get_user(user_id)

    level = xp_system.get_progress(user_id)
    goal_progress = goals.get_goal_progress(user_id)

    text = (
        "🌸 MOODBLOOM — BLOOM JOURNEY\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 {user.first_name}\n\n"
        f"⭐ Level {level['level']} — {level['title']}\n"
        f"✨ XP: {level['xp']}\n\n"
        f"📈 Progress: {level['progress']}%\n"
        f"{xp_system.progress_bar(user_id)}\n\n"
        f"🎯 Today's Goals\n"
        f"{goals.progress_bar(user_id)} "
        f"{goal_progress['completed']}/{goal_progress['total']}\n\n"
        "🌱 Keep taking small steps.\n"
        "Every little bloom counts. 💖"
    )

    await update.message.reply_text(
        text,
        
        reply_markup=keyboards.bloom_dashboard_keyboard(),
    )

# ============================================================
# HOME / MENU
# ============================================================

async def menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /menu command.
    """

    user_id = update.effective_user.id

    try:

        history = database.get_user_history(
            user_id
        )

    except Exception:

        history = []

    total = analytics.total_checkins(
        history
    )

    level = analytics.get_level(
        history
    )

    xp = analytics.get_xp(
        history
    )

    streak = analytics.current_streak(
        history
    )

    progress = analytics.get_level_progress(
        history
    )

    progress_bar = analytics.get_progress_bar(
        history
    )

    text = (
        "🌸 *MoodBloom Dashboard*\n\n"

        f"💭 Check-ins: *{total}*\n"
        f"⭐ Level: *{level}*\n"
        f"✨ XP: *{xp}*\n"
        f"🔥 Streak: *{streak} days*\n\n"

        f"{progress_bar}\n"
        f"*{progress}/100 XP*\n\n"

        "Choose something below ✨"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.home_keyboard(),
    )


# ============================================================
# MOOD MENU
# ============================================================

async def mood(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /mood command.
    """

    await update.message.reply_text(
        "💭 *How are you feeling right now?*\n\n"
        "Choose the mood that fits you best. 🌸",
        parse_mode="Markdown",
        reply_markup=keyboards.mood_keyboard(),
    )


# ============================================================
# DAILY
# ============================================================

async def daily(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /daily command.
    """

    user_id = update.effective_user.id

    history = database.get_user_history(
        user_id
    )

    today = analytics.today_entries(
        history
    )

    streak = analytics.current_streak(
        history
    )

    best = analytics.best_streak(
        history
    )

    xp = analytics.get_xp(
        history
    )

    level = analytics.get_level(
        history
    )

    progress = analytics.get_level_progress(
        history
    )

    if today:

        mood_lines = []

        for entry in today:

            mood_key = entry.get(
                "mood",
                "unknown"
            )

            info = moods.MOODS.get(
                mood_key,
                {}
            )

            emoji = info.get(
                "emoji",
                "🌸"
            )

            name = info.get(
                "name",
                mood_key.title()
            )

            mood_lines.append(
                f"{emoji} {name}"
            )

        today_text = "\n".join(
            mood_lines
        )

    else:

        today_text = (
            "No check-ins yet today."
        )

    text = (
        "📅 *Today's Mood*\n\n"

        f"{today_text}\n\n"

        f"💭 Today's check-ins: *{len(today)}*\n"
        f"🔥 Current streak: *{streak} days*\n"
        f"🏆 Best streak: *{best} days*\n\n"

        f"⭐ Level: *{level}*\n"
        f"✨ XP: *{xp}*\n"
        f"📈 Level progress: *{progress}/100*\n"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.mood_keyboard(),
    )


# ============================================================
# PROFILE
# ============================================================

async def profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /profile command.
    """

    user = update.effective_user

    history = database.get_user_history(
        user.id
    )

    total = analytics.total_checkins(
        history
    )

    days = analytics.unique_days(
        history
    )

    level = analytics.get_level(
        history
    )

    xp = analytics.get_xp(
        history
    )

    streak = analytics.current_streak(
        history
    )

    best = analytics.best_streak(
        history
    )

    favorite = analytics.favorite_mood(
        history
    )

    if favorite:

        info = moods.MOODS.get(
            favorite,
            {}
        )

        favorite_text = (
            f"{info.get('emoji', '🌸')} "
            f"{info.get('name', favorite.title())}"
        )

    else:

        favorite_text = "No data yet"

    text = (
        "👤 *Your MoodBloom Profile*\n\n"

        f"🌸 Name: *{user.first_name or 'User'}*\n\n"

        f"💭 Total check-ins: *{total}*\n"
        f"📅 Days tracked: *{days}*\n"
        f"⭐ Level: *{level}*\n"
        f"✨ XP: *{xp}*\n"
        f"🔥 Current streak: *{streak} days*\n"
        f"🏆 Best streak: *{best} days*\n"
        f"💖 Favorite mood: *{favorite_text}*\n"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# STATS
# ============================================================

async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /stats command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    summary = build_stats_summary(
        history
    )

    if not summary.get("has_data"):

        await update.message.reply_text(
            "🌱 You don't have enough mood data yet.\n\n"
            "Start with your first mood check-in! 💗",
            reply_markup=keyboards.mood_keyboard(),
        )

        return

    favorite = summary.get(
        "favorite_mood"
    )

    favorite_info = moods.MOODS.get(
        favorite,
        {}
    )

    favorite_text = (
        f"{favorite_info.get('emoji', '🌸')} "
        f"{favorite_info.get('name', favorite.title())}"
    )

    trend = summary.get(
        "trend",
        {}
    )

    direction = trend.get(
        "direction",
        "new"
    )

    trend_icons = {
        "up": "📈 Improving",
        "down": "📉 Lower",
        "stable": "➡️ Stable",
        "new": "🆕 New",
    }

    trend_text = trend_icons.get(
        direction,
        "🆕 New"
    )

    text = (
        "📊 *MoodBloom Statistics*\n\n"

        f"💭 Total check-ins: "
        f"*{summary['total_checkins']}*\n"

        f"📅 Days tracked: "
        f"*{summary['unique_days']}*\n"

        f"💖 Favorite mood: "
        f"*{favorite_text}*\n\n"

        f"⭐ Level: *{summary['level']}*\n"
        f"✨ XP: *{summary['xp']}*\n"
        f"🔥 Current streak: "
        f"*{summary['current_streak']} days*\n"
        f"🏆 Best streak: "
        f"*{summary['best_streak']} days*\n\n"

        f"🧠 Average mood score: "
        f"*{summary['average_mood_score']}/5*\n"

        f"🌈 Mood state: "
        f"*{summary['score_label']}*\n"

        f"📈 Trend: *{trend_text}*\n"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# CHART
# ============================================================

async def chart(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /chart command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    image = analytics.create_mood_chart(
        history
    )

    if image is None:

        await update.message.reply_text(
            "🌱 No mood data available yet.\n\n"
            "Add a few check-ins first!",
            reply_markup=keyboards.mood_keyboard(),
        )

        return

    await update.message.reply_photo(
        photo=image,
        caption=(
            "📊 *Your Mood Distribution*\n\n"
            "A visual overview of your recorded moods. 🌈"
        ),
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# WEEKLY CHART
# ============================================================

async def weekly_chart(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /weeklychart command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    image = analytics.create_weekly_mood_chart(
        history
    )

    if image is None:

        await update.message.reply_text(
            "🌱 No mood activity found "
            "for the last 7 days.",
            reply_markup=keyboards.mood_keyboard(),
        )

        return

    await update.message.reply_photo(
        photo=image,
        caption=(
            "📈 *Your Last 7 Days*\n\n"
            "Here's how your mood check-ins "
            "have been distributed this week. 🌸"
        ),
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# WEEKLY
# ============================================================

async def weekly(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /weekly command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    entries = analytics.weekly_entries(
        history
    )

    counts = analytics.weekly_counts(
        history
    )

    trend = analytics.mood_trend(
        history
    )

    if not entries:

        await update.message.reply_text(
            "🌱 No check-ins recorded "
            "during the last 7 days.",
            reply_markup=keyboards.mood_keyboard(),
        )

        return

    lines = []

    for mood_key, count in sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        info = moods.MOODS.get(
            mood_key,
            {}
        )

        emoji = info.get(
            "emoji",
            "🌸"
        )

        name = info.get(
            "name",
            mood_key.title()
        )

        lines.append(
            f"{emoji} {name}: *{count}*"
        )

    direction = trend.get(
        "direction",
        "stable"
    )

    trend_text = {
        "up": "📈 Your recent mood trend is improving.",
        "down": "📉 Your recent mood trend is lower.",
        "stable": "➡️ Your recent mood trend is stable.",
        "new": "🆕 Not enough previous data for comparison.",
    }.get(
        direction,
        "🌈 Your mood pattern is evolving."
    )

    text = (
        "📅 *Weekly Mood Summary*\n\n"
        f"💭 Check-ins: *{len(entries)}*\n\n"
        + "\n".join(lines)
        + "\n\n"
        + trend_text
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# TODAY
# ============================================================

async def today(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /today command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    entries = analytics.today_entries(
        history
    )

    if not entries:

        text = (
            "📅 *Today*\n\n"
            "🌱 No mood check-ins yet today.\n\n"
            "How are you feeling?"
        )

    else:

        lines = []

        for entry in entries:

            mood_key = entry.get(
                "mood",
                "unknown"
            )

            info = moods.MOODS.get(
                mood_key,
                {}
            )

            emoji = info.get(
                "emoji",
                "🌸"
            )

            name = info.get(
                "name",
                mood_key.title()
            )

            lines.append(
                f"{emoji} {name}"
            )

        text = (
            "📅 *Today's Check-ins*\n\n"
            + "\n".join(lines)
            + f"\n\n💭 Total: *{len(entries)}*"
        )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.mood_keyboard(),
    )


# ============================================================
# HISTORY
# ============================================================

async def history(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /history command.
    """

    data = database.get_user_history(
        update.effective_user.id
    )

    entries = analytics.recent_entries(
        data,
        limit=10,
    )

    if not entries:

        await update.message.reply_text(
            "📜 Your mood history is empty.\n\n"
            "Start your first check-in! 🌱",
            reply_markup=keyboards.mood_keyboard(),
        )

        return

    lines = []

    for entry in entries:

        date = entry.get(
            "date",
            "Unknown"
        )

        mood_key = entry.get(
            "mood",
            "unknown"
        )

        info = moods.MOODS.get(
            mood_key,
            {}
        )

        emoji = info.get(
            "emoji",
            "🌸"
        )

        name = info.get(
            "name",
            mood_key.title()
        )

        lines.append(
            f"📅 {date} — {emoji} {name}"
        )

    text = (
        "📜 *Recent Mood History*\n\n"
        + "\n".join(lines)
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# INSIGHTS
# ============================================================

async def insights(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /insights command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    data = analytics.smart_insights(
        history
    )

    if not data.get("has_data"):

        await update.message.reply_text(
            "🧠 *MoodBloom Insights*\n\n"
            "🌱 I need a few mood check-ins "
            "before I can find patterns.",
            parse_mode="Markdown",
            reply_markup=keyboards.mood_keyboard(),
        )

        return

    trend = data.get(
        "trend",
        {}
    )

    direction = trend.get(
        "direction",
        "new"
    )

    trend_text = {
        "up": "📈 Your recent mood trend is moving upward.",
        "down": "📉 Your recent mood trend is moving downward.",
        "stable": "➡️ Your recent mood pattern is stable.",
        "new": "🆕 Keep checking in for more comparisons.",
    }.get(
        direction,
        "🌈 Your mood pattern is evolving."
    )

    text = (
        "🧠 *MoodBloom Smart Insights*\n\n"

        f"💖 Most common mood: "
        f"{data['favorite_emoji']} "
        f"*{data['favorite_name']}*\n\n"

        f"📊 Average mood score: "
        f"*{data['average_score']}/5*\n"

        f"🌈 Overall state: "
        f"*{data['score_label']}*\n\n"

        f"🔥 Current streak: "
        f"*{data['streak']} days*\n"

        f"🏆 Best streak: "
        f"*{data['best_streak']} days*\n\n"

        f"{trend_text}\n"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# FORECAST
# ============================================================

async def forecast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /forecast command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    data = analytics.mood_forecast(
        history
    )

    if not data.get("has_data"):

        await update.message.reply_text(
            data.get(
                "message",
                "🌱 Keep checking in to build a mood pattern."
            ),
            reply_markup=keyboards.mood_keyboard(),
        )

        return

    text = (
        "🔮 *Mood Pattern Forecast*\n\n"

        f"{data['pattern']}\n\n"

        f"🌸 Dominant mood: "
        f"*{data['dominant_emoji']} "
        f"{data['dominant_name']}*\n"

        f"📊 Recent share: "
        f"*{data['percentage']}%*\n"

        f"🎯 Confidence: "
        f"*{data['confidence']}*\n\n"

        f"🔮 {data['forecast']}\n\n"

        f"{data['disclaimer']}"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# STREAK
# ============================================================

async def streak(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /streak command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    current = analytics.current_streak(
        history
    )

    best = analytics.best_streak(
        history
    )

    text = (
        "🔥 *MoodBloom Streak*\n\n"

        f"🔥 Current streak: *{current} days*\n"
        f"🏆 Best streak: *{best} days*\n\n"
    )

    if current == 0:

        text += (
            "🌱 Start a new streak today!"
        )

    elif current < 3:

        text += (
            "✨ Keep going — you're building momentum!"
        )

    elif current < 7:

        text += (
            "🔥 Nice streak! Keep it alive!"
        )

    elif current < 30:

        text += (
            "🚀 You're seriously consistent!"
        )

    else:

        text += (
            "👑 Legendary consistency!"
        )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# ACHIEVEMENTS
# ============================================================

async def achievements(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /achievements command.
    """

    history = database.get_user_history(
        update.effective_user.id
    )

    unlocked = analytics.achievements(
        history
    )

    if not unlocked:

        text = (
            "🏆 *Achievements*\n\n"
            "🌱 No achievements unlocked yet.\n\n"
            "Your first check-in will unlock "
            "your first badge! ✨"
        )

    else:

        text = (
            "🏆 *Your Achievements*\n\n"
            + "\n".join(
                f"✅ {item}"
                for item in unlocked
            )
            + f"\n\n🎖️ Unlocked: *{len(unlocked)}*"
        )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# QUOTE
# ============================================================

async def quote(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /quote command.
    """

    try:

        text = messages.quote()

    except Exception:

        text = (
            "🌸 Every small step you take "
            "toward yourself matters."
        )

    await update.message.reply_text(
        text,
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# MOTIVATE
# ============================================================

async def motivate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /motivate command.
    """

    try:

        text = messages.motivate()

    except Exception:

        text = (
            "🔥 You don't need to be perfect. "
            "Just keep moving forward."
        )

    await update.message.reply_text(
        text,
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# RANDOM
# ============================================================

def get_random_content():
    """Return one random MoodBloom content item."""

    options = [
        lambda: f"✨ {moods.random_quote()}",
        lambda: f"🔥 {moods.random_motivation()}",
        lambda: f"🎯 Try this: {moods.random_activity()}",
    ]

    try:

        return random.choice(options)()

    except Exception:

        return (
            "🎲 Random MoodBloom thought:\n\n"
            "🌸 Today can still surprise you."
        )


async def random_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /random command.
    """

    try:

        text = get_random_content()

    except Exception:

        text = (
            "🎲 Random MoodBloom thought:\n\n"
            "🌸 Today can still surprise you."
        )

    await update.message.reply_text(
        text,
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# ABOUT
# ============================================================

async def about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /about command.
    """

    text = (
        f"🌸 *{config.BOT_NAME}*\n\n"

        "Your cute personal mood companion. 💗\n\n"

        "✨ Track your moods\n"
        "📊 Understand your patterns\n"
        "🔥 Build streaks\n"
        "🏆 Unlock achievements\n"
        "🧠 Get simple insights\n"
        "🔮 Explore mood patterns\n"
        "📈 View charts\n"
        "⏰ Set reminders\n"
        "📤 Export your history\n\n"

        f"Version: *{config.VERSION}*\n\n"

        "Made with Python 🐍 + Telegram 💙"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# HELP
# ============================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /help command.
    """

    text = (
        "🌸 *MoodBloom Help*\n\n"

        "💭 */mood* — Record your mood\n"
        "📅 */daily* — Today's overview\n"
        "📊 */stats* — Your statistics\n"
        "📈 */chart* — Mood distribution chart\n"
        "📊 */weeklychart* — 7-day chart\n"
        "📅 */weekly* — Weekly summary\n"
        "📜 */history* — Recent history\n"
        "👤 */profile* — Your profile\n"
        "🧠 */insights* — Smart insights\n"
        "🔮 */forecast* — Mood pattern forecast\n"
        "🔥 */streak* — Streak information\n"
        "🏆 */achievements* — Your badges\n"
        "✨ */quote* — Random quote\n"
        "🔥 */motivate* — Motivation\n"
        "🎲 */random* — Random MoodBloom content\n"
        "⏰ */remind* — Set reminder\n"
        "❌ */remindoff* — Disable reminder\n"
        "📤 */export* — Export mood history\n"
        "🗑️ */clear* — Clear your history\n"
        "🏠 */menu* — Open dashboard\n"
        "ℹ️ */about* — About MoodBloom\n"
    )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# EXPORT
# ============================================================

async def export_history(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /export command.

    Exports the user's mood history as JSON.
    """

    user_id = update.effective_user.id

    try:

        history = database.get_user_history(
            user_id
        )

        if not history:

            await update.message.reply_text(
                "📤 *MoodBloom Export*\n\n"
                "🌱 Your mood history is empty.\n\n"
                "Add a few check-ins first!",
                parse_mode="Markdown",
                reply_markup=keyboards.mood_keyboard(),
            )

            return

        document = build_export_file(
            history,
            user_id,
        )

        await update.message.reply_document(
            document=document,
            caption=(
                "📤 *MoodBloom History Export*\n\n"
                "Your mood history is safely exported "
                "as a JSON file. 🌸"
            ),
            parse_mode="Markdown",
            reply_markup=keyboards.back_keyboard(),
        )

    except Exception as error:

        print(
            "Export command error:",
            error
        )

        await update.message.reply_text(
            "⚠️ I couldn't create your export right now.",
            reply_markup=keyboards.back_keyboard(),
        )


# ============================================================
# REMINDER
# ============================================================

async def send_daily_reminder(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Sends scheduled daily mood reminder.
    """

    job = context.job

    if not job:
        return

    data = job.data or {}

    user_id = data.get(
        "user_id"
    )

    if not user_id:
        return

    try:

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🌸 *MoodBloom Reminder*\n\n"
                "How are you feeling right now? 💭\n\n"
                "Take a tiny moment for yourself."
            ),
            parse_mode="Markdown",
            reply_markup=keyboards.mood_keyboard(),
        )

    except Exception as error:

        print(
            "Reminder send error:",
            error
        )


def restore_saved_reminders(
    application,
):
    """
    Restores reminders stored in database.
    """

    try:

        data = database.load_data()

    except Exception as error:

        print(
            "Could not load saved reminders:",
            error
        )

        return

    if not isinstance(data, dict):
        return

    restored = 0

    for key, settings in data.items():

        if not str(key).endswith(
            "_settings"
        ):
            continue

        if not isinstance(settings, dict):
            continue

        if not settings.get(
            "reminder_enabled"
        ):
            continue

        try:

            user_id = int(
                str(key).replace(
                    "_settings",
                    ""
                )
            )

            hour = int(
                settings.get(
                    "reminder_hour",
                    21
                )
            )

            minute = int(
                settings.get(
                    "reminder_minute",
                    0
                )
            )

            if not 0 <= hour <= 23:
                continue

            if not 0 <= minute <= 59:
                continue

            success = schedule_user_reminder(
                application,
                user_id,
                hour,
                minute,
            )

            if success:
                restored += 1

        except Exception as error:

            print(
                "Reminder restore error:",
                error
            )

    print(
        f"⏰ Restored {restored} saved reminder(s)."
    )


async def remind(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /remind command.
    """

    context.user_data[
        "waiting_for_reminder"
    ] = False

    await update.message.reply_text(
        "⏰ *Choose your daily reminder time:*",
        parse_mode="Markdown",
        reply_markup=keyboards.reminder_keyboard(),
    )


async def remindoff(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /remindoff command.
    """

    user_id = update.effective_user.id

    context.user_data[
        "waiting_for_reminder"
    ] = False

    try:

        database.disable_user_reminder(
            user_id
        )

    except Exception as error:

        print(
            "Reminder settings error:",
            error
        )

    remove_existing_reminder_jobs(
        context.application,
        user_id,
    )

    await update.message.reply_text(
        "❌ Daily reminder disabled.",
        reply_markup=keyboards.back_keyboard(),
    )


async def handle_reminder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handles reminder callback buttons.
    """

    query = update.callback_query

    await safe_answer(query)

    action = query.data

    user_id = query.from_user.id

    if action == "remind_cancel":

        context.user_data[
            "waiting_for_reminder"
        ] = False

        await edit_menu_message(
            query,
            "❌ Reminder setup cancelled.",
            keyboards.back_keyboard(),
        )

        return

    if action == "remind_custom":

        context.user_data[
            "waiting_for_reminder"
        ] = True

        await edit_menu_message(
            query,
            (
                "✏️ *Custom Reminder*\n\n"
                "Send a time like:\n"
                "`7:30 PM`\n\n"
                "Example: `9:15 PM`"
            ),
            keyboards.back_keyboard(),
        )

        return

    fixed_times = {
        "remind_8": (
            8,
            0,
            "8:00 AM"
        ),
        "remind_12": (
            12,
            0,
            "12:00 PM"
        ),
        "remind_18": (
            18,
            0,
            "6:00 PM"
        ),
        "remind_21": (
            21,
            0,
            "9:00 PM"
        ),
    }

    if action not in fixed_times:
        return

    hour, minute, label = (
        fixed_times[action]
    )

    try:

        database.set_user_reminder(
            user_id,
            hour,
            minute,
        )

    except Exception as error:

        print(
            "Reminder save error:",
            error
        )

    success = schedule_user_reminder(
        context.application,
        user_id,
        hour,
        minute,
    )

    context.user_data[
        "waiting_for_reminder"
    ] = False

    if success:

        text = (
            "⏰ *Reminder Set!*\n\n"
            f"🌸 I'll remind you every day at *{label}*."
        )

    else:

        text = (
            "⚠️ Reminder settings were saved, "
            "but the scheduler is unavailable.\n\n"
            "Install the JobQueue dependency to enable "
            "automatic reminders."
        )

    await edit_menu_message(
        query,
        text,
        keyboards.back_keyboard(),
    )


async def receive_custom_reminder_time(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Receives custom reminder time.
    """

    if not context.user_data.get(
        "waiting_for_reminder"
    ):
        return

    if not update.message:
        return

    text = (
        update.message.text
        or ""
    ).strip()

    formats = [
        "%I:%M %p",
        "%I:%M%p",
        "%H:%M",
    ]

    parsed_time = None

    for time_format in formats:

        try:

            parsed_time = datetime.datetime.strptime(
                text.upper(),
                time_format,
            ).time()

            break

        except ValueError:

            continue

    if parsed_time is None:

        await update.message.reply_text(
            "❌ I couldn't understand that time.\n\n"
            "Please send something like:\n"
            "`7:30 PM`\n"
            "or\n"
            "`21:00`",
            parse_mode="Markdown",
        )

        return

    user_id = update.effective_user.id

    hour = parsed_time.hour
    minute = parsed_time.minute

    try:

        database.set_user_reminder(
            user_id,
            hour,
            minute,
        )

    except Exception as error:

        print(
            "Custom reminder save error:",
            error
        )

    success = schedule_user_reminder(
        context.application,
        user_id,
        hour,
        minute,
    )

    context.user_data[
        "waiting_for_reminder"
    ] = False

    label = parsed_time.strftime(
        "%I:%M %p"
    ).lstrip("0")

    if success:

        text = (
            "⏰ *Custom Reminder Set!*\n\n"
            f"🌸 Daily reminder time: *{label}*"
        )

    else:

        text = (
            "⚠️ Your reminder time was saved, "
            "but automatic scheduling is unavailable."
        )

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboards.back_keyboard(),
    )


# ============================================================
# CLEAR HISTORY
# ============================================================

async def clear(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    /clear command.
    """

    await update.message.reply_text(
        "🗑️ *Clear Mood History?*\n\n"
        "This will remove your saved mood history.\n\n"
        "Are you sure?",
        parse_mode="Markdown",
        reply_markup=keyboards.clear_confirmation_keyboard(),
    )


async def handle_clear(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handles clear confirmation.
    """

    query = update.callback_query

    await safe_answer(query)

    user_id = query.from_user.id

    if query.data == "clear_cancel":

        await edit_menu_message(
            query,
            "❌ Nothing was deleted.",
            keyboards.back_keyboard(),
        )

        return

    if query.data == "clear_confirm":

        try:

            database.clear_user_history(
                user_id
            )

            context.user_data.pop(
                "waiting_for_reminder",
                None,
            )

            context.user_data.pop(
                "waiting_for_note",
                None,
            )

            context.user_data.pop(
                "last_mood",
                None,
            )

            await edit_menu_message(
                query,
                (
                    "🗑️ *History Cleared*\n\n"
                    "Your MoodBloom history has been reset. 🌱\n\n"
                    "Ready for a fresh start!"
                ),
                keyboards.home_keyboard(),
            )

        except Exception as error:

            print(
                "Clear history error:",
                error
            )

            await edit_menu_message(
                query,
                (
                    "⚠️ Something went wrong "
                    "while clearing your history."
                ),
                keyboards.back_keyboard(),
            )


# ============================================================
# MOOD CALLBACK
# ============================================================

async def handle_mood(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handles mood button selection.
    """

    query = update.callback_query

    await safe_answer(query)

    mood_key = (
        query.data
        .replace(
            "mood_",
            "",
            1
        )
        .strip()
        .lower()
    )

    user_id = query.from_user.id

    try:

        history_before = database.get_user_history(
            user_id
        )

    except Exception:

        history_before = []

    old_level = analytics.get_level(
        history_before
    )

    old_achievements = set(
        analytics.achievements(
            history_before
        )
    )

    try:

        response = moods.get_mood_response(
            mood_key
        )

    except Exception as error:

        print(
            "Mood response error:",
            error
        )

        response = ""

    # --------------------------------------------------------
    # Save mood
    # --------------------------------------------------------

    try:

        database.add_mood(
            user_id,
            mood_key
        )

    except Exception as error:

        print(
            "Mood save error:",
            error
        )

        await edit_menu_message(
            query,
            (
                "⚠️ I couldn't save your mood "
                "right now. Please try again."
            ),
            keyboards.back_keyboard(),
        )

        return

    try:

        history_after = database.get_user_history(
            user_id
        )

    except Exception:

        history_after = (
            history_before + [
                {
                    "mood": mood_key
                }
            ]
        )

    new_level = analytics.get_level(
        history_after
    )

    current_streak = analytics.current_streak(
        history_after
    )

    best_streak = analytics.best_streak(
        history_after
    )

    total = analytics.total_checkins(
        history_after
    )

    new_achievements = [
        achievement
        for achievement in analytics.achievements(
            history_after
        )
        if achievement not in old_achievements
    ]

    # ============================================================
    # MOODBLOOM 4.0 — AUTO COMPLETE MOOD GOAL
    # ============================================================

    try:
        goal_result = goals.complete_goal(
            update.effective_user.id,
            "mood_check",
        )

        if goal_result.get("success"):
            goal_xp = goal_result.get("xp", 0)

            print(
                f"🌸 V4 Goal completed: mood_check "
                f"(+{goal_xp} XP)"
            )

    except Exception as error:
        print(
            "⚠️ V4 mood goal error:",
            error,
        )

    # --------------------------------------------------------
    # Mood information
    # --------------------------------------------------------

    info = moods.MOODS.get(
        mood_key,
        {}
    )

    emoji = info.get(
        "emoji",
        "🌸"
    )

    name = info.get(
        "name",
        mood_key.title()
    )

    # --------------------------------------------------------
    # Response from moods.py
    # --------------------------------------------------------

    mood_response = ""
    activity = ""

    if isinstance(response, dict):

        mood_response = response.get(
            "response",
            response.get(
                "message",
                ""
            )
        )

        activity = response.get(
            "activity",
            ""
        )

    elif isinstance(response, str):

        mood_response = response

    elif isinstance(response, (tuple, list)):

        if len(response) >= 1:

            mood_response = (
                response[0]
                if response[0]
                else ""
            )

        if len(response) >= 2:

            activity = (
                response[1]
                if response[1]
                else ""
            )

    # --------------------------------------------------------
    # Build result
    # --------------------------------------------------------

    text = (
        f"{emoji} *Mood recorded: {name}!*\n\n"
    )

    if mood_response:

        text += (
            f"{mood_response}\n\n"
        )

    if activity:

        text += (
            f"✨ *Try this:* {activity}\n\n"
        )

    text += (
        "━━━━━━━━━━━━━━━\n"
        "✨ +10 XP\n"
        f"💭 Total check-ins: *{total}*\n"
        f"🔥 Current streak: *{current_streak} days*\n"
        f"🏆 Best streak: *{best_streak} days*\n"
    )

    if new_level > old_level:

        text += (
            f"\n🎉 *LEVEL UP!*\n"
            f"You reached *Level {new_level}*! ⭐\n"
        )

    if new_achievements:

        text += (
            "\n🏆 *New Achievement!*\n"
            + "\n".join(
                f"🎖️ {item}"
                for item in new_achievements
            )
        )

    context.user_data[
        "last_mood"
    ] = mood_key

    context.user_data[
        "waiting_for_note"
    ] = False

    context.user_data[
        "waiting_for_reminder"
    ] = False

    await edit_menu_message(
        query,
        text,
        keyboards.back_keyboard(),
    )


# ============================================================
# MENU CALLBACK
# ============================================================

async def handle_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Handles dashboard/menu callbacks.
    """

    query = update.callback_query

    await safe_answer(query)

    action = query.data

    user_id = query.from_user.id

    # --------------------------------------------------------
    # Leaving custom reminder mode
    # --------------------------------------------------------

    if action != "remind_custom":

        context.user_data[
            "waiting_for_reminder"
        ] = False

    # ========================================================
    # HOME
    # ========================================================

    if action == "home":

        history = database.get_user_history(
            user_id
        )

        total = analytics.total_checkins(
            history
        )

        level = analytics.get_level(
            history
        )

        streak = analytics.current_streak(
            history
        )

        xp = analytics.get_xp(
            history
        )

        progress = analytics.get_level_progress(
            history
        )

        progress_bar = analytics.get_progress_bar(
            history
        )

        text = (
            "🌸 *MoodBloom Dashboard*\n\n"

            f"💭 Check-ins: *{total}*\n"
            f"⭐ Level: *{level}*\n"
            f"✨ XP: *{xp}*\n"
            f"🔥 Streak: *{streak} days*\n\n"

            f"{progress_bar}\n"
            f"*{progress}/100 XP*\n\n"

            "What would you like to explore? 🌈"
        )

        await edit_menu_message(
            query,
            text,
            keyboards.home_keyboard(),
        )

        return

    # ========================================================
    # MOOD
    # ========================================================

    if action == "menu_mood":

        await edit_menu_message(
            query,
            (
                "💭 *Mood Check-in*\n\n"
                "How are you feeling right now? 🌸"
            ),
            keyboards.mood_keyboard(),
        )

        return

    # ========================================================
    # DAILY
    # ========================================================

    if action == "menu_daily":

        history = database.get_user_history(
            user_id
        )

        entries = analytics.today_entries(
            history
        )

        text = (
            "📅 *Today's Overview*\n\n"
            f"💭 Check-ins today: *{len(entries)}*\n"
            f"🔥 Current streak: "
            f"*{analytics.current_streak(history)} days*\n"
            f"🏆 Best streak: "
            f"*{analytics.best_streak(history)} days*\n"
            f"⭐ Level: *{analytics.get_level(history)}*\n"
            f"✨ XP: *{analytics.get_xp(history)}*\n"
        )

        if entries:

            latest = analytics.recent_mood(
                entries
            )

            info = moods.MOODS.get(
                latest,
                {}
            )

            text += (
                "\n💖 Latest mood: "
                f"{info.get('emoji', '🌸')} "
                f"*{info.get('name', latest.title())}*"
            )

        else:

            text += (
                "\n🌱 No check-in yet today."
            )

        await edit_menu_message(
            query,
            text,
            keyboards.mood_keyboard(),
        )

        return

    # ========================================================
    # STATS
    # ========================================================

    if action == "menu_stats":

        history = database.get_user_history(
            user_id
        )

        summary = build_stats_summary(
            history
        )

        if not summary.get(
            "has_data"
        ):

            text = (
                "📊 *Statistics*\n\n"
                "🌱 Start tracking your mood "
                "to see statistics here."
            )

        else:

            favorite = summary.get(
                "favorite_mood"
            )

            favorite_info = moods.MOODS.get(
                favorite,
                {}
            )

            favorite_text = (
                f"{favorite_info.get('emoji', '🌸')} "
                f"{favorite_info.get('name', favorite.title())}"
            )

            direction = summary.get(
                "trend",
                {}
            ).get(
                "direction",
                "new"
            )

            trend_text = {
                "up": "📈 Improving",
                "down": "📉 Lower",
                "stable": "➡️ Stable",
                "new": "🆕 New",
            }.get(
                direction,
                "🌈 Evolving"
            )

            text = (
                "📊 *Your Statistics*\n\n"

                f"💭 Check-ins: "
                f"*{summary['total_checkins']}*\n"

                f"📅 Days tracked: "
                f"*{summary['unique_days']}*\n"

                f"💖 Favorite: "
                f"*{favorite_text}*\n\n"

                f"⭐ Level: "
                f"*{summary['level']}*\n"

                f"✨ XP: "
                f"*{summary['xp']}*\n"

                f"🔥 Streak: "
                f"*{summary['current_streak']} days*\n"

                f"🏆 Best: "
                f"*{summary['best_streak']} days*\n\n"

                f"🧠 Mood score: "
                f"*{summary['average_mood_score']}/5*\n"

                f"🌈 State: "
                f"*{summary['score_label']}*\n"

                f"📈 Trend: *{trend_text}*"
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # CHART
    # ========================================================

    if action == "menu_chart":

        history = database.get_user_history(
            user_id
        )

        image = analytics.create_mood_chart(
            history
        )

        if image is None:

            await edit_menu_message(
                query,
                (
                    "📊 *Mood Chart*\n\n"
                    "🌱 Not enough mood data yet."
                ),
                keyboards.mood_keyboard(),
            )

            return

        try:

            try:

                await query.message.delete()

            except Exception:

                pass

            await query.message.chat.send_photo(
                photo=image,
                caption=(
                    "📊 *Your Mood Distribution*\n\n"
                    "A visual overview of your recorded moods. 🌈"
                ),
                parse_mode="Markdown",
                reply_markup=keyboards.back_keyboard(),
            )

        except Exception as error:

            print(
                "Chart callback error:",
                error
            )

            try:

                await edit_menu_message(
                    query,
                    "⚠️ Could not generate the chart.",
                    keyboards.back_keyboard(),
                )

            except Exception:
                pass

        return

    # ========================================================
    # WEEKLY CHART
    # ========================================================

    if action == "menu_weekly_chart":

        history = database.get_user_history(
            user_id
        )

        image = analytics.create_weekly_mood_chart(
            history
        )

        if image is None:

            await edit_menu_message(
                query,
                (
                    "📊 *Weekly Chart*\n\n"
                    "🌱 No activity found "
                    "for the last 7 days."
                ),
                keyboards.mood_keyboard(),
            )

            return

        try:

            try:

                await query.message.delete()

            except Exception:

                pass

            await query.message.chat.send_photo(
                photo=image,
                caption=(
                    "📈 *Your Last 7 Days*\n\n"
                    "Here's how your mood check-ins "
                    "have been distributed this week. 🌸"
                ),
                parse_mode="Markdown",
                reply_markup=keyboards.back_keyboard(),
            )

        except Exception as error:

            print(
                "Weekly chart error:",
                error
            )

        return

    # ========================================================
    # INSIGHTS
    # ========================================================

    if action == "menu_insights":

        history = database.get_user_history(
            user_id
        )

        data = analytics.smart_insights(
            history
        )

        if not data.get(
            "has_data"
        ):

            text = (
                "🧠 *Smart Insights*\n\n"
                "🌱 Keep checking in so I can "
                "discover your mood patterns."
            )

        else:

            direction = data[
                "trend"
            ].get(
                "direction",
                "new"
            )

            trend_text = {
                "up": "📈 Improving",
                "down": "📉 Lower",
                "stable": "➡️ Stable",
                "new": "🆕 New",
            }.get(
                direction,
                "🌈 Evolving"
            )

            text = (
                "🧠 *Smart Insights*\n\n"

                f"💖 Favorite: "
                f"{data['favorite_emoji']} "
                f"*{data['favorite_name']}*\n"

                f"🧠 Average score: "
                f"*{data['average_score']}/5*\n"

                f"🌈 State: "
                f"*{data['score_label']}*\n"

                f"📈 Trend: *{trend_text}*\n\n"

                f"🔥 Current streak: "
                f"*{data['streak']} days*\n"

                f"🏆 Best streak: "
                f"*{data['best_streak']} days*"
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # WEEKLY
    # ========================================================

    if action == "menu_weekly":

        history = database.get_user_history(
            user_id
        )

        entries = analytics.weekly_entries(
            history
        )

        counts = analytics.weekly_counts(
            history
        )

        if not entries:

            text = (
                "📅 *Weekly Summary*\n\n"
                "🌱 No check-ins in the last 7 days."
            )

        else:

            lines = []

            for mood_key, count in sorted(
                counts.items(),
                key=lambda item: item[1],
                reverse=True,
            ):

                info = moods.MOODS.get(
                    mood_key,
                    {}
                )

                lines.append(
                    f"{info.get('emoji', '🌸')} "
                    f"{info.get('name', mood_key.title())}: "
                    f"*{count}*"
                )

            trend = analytics.mood_trend(
                history
            )

            direction = trend.get(
                "direction",
                "new"
            )

            trend_text = {
                "up": "📈 Improving",
                "down": "📉 Lower",
                "stable": "➡️ Stable",
                "new": "🆕 New",
            }.get(
                direction,
                "🌈 Evolving"
            )

            text = (
                "📅 *Weekly Summary*\n\n"
                f"💭 Total: *{len(entries)}*\n\n"
                + "\n".join(lines)
                + f"\n\n📈 Trend: *{trend_text}*"
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # TODAY
    # ========================================================

    if action == "menu_today":

        history = database.get_user_history(
            user_id
        )

        entries = analytics.today_entries(
            history
        )

        if not entries:

            text = (
                "📅 *Today*\n\n"
                "🌱 No mood check-ins yet."
            )

        else:

            lines = []

            for entry in entries:

                mood_key = entry.get(
                    "mood",
                    "unknown"
                )

                info = moods.MOODS.get(
                    mood_key,
                    {}
                )

                lines.append(
                    f"{info.get('emoji', '🌸')} "
                    f"{info.get('name', mood_key.title())}"
                )

            text = (
                "📅 *Today's Moods*\n\n"
                + "\n".join(lines)
                + f"\n\n💭 Total: *{len(entries)}*"
            )

        await edit_menu_message(
            query,
            text,
            keyboards.mood_keyboard(),
        )

        return

    # ========================================================
    # STREAK
    # ========================================================

    if action == "menu_streak":

        history = database.get_user_history(
            user_id
        )

        current = analytics.current_streak(
            history
        )

        best = analytics.best_streak(
            history
        )

        text = (
            "🔥 *Streak*\n\n"
            f"🔥 Current: *{current} days*\n"
            f"🏆 Best: *{best} days*\n\n"
        )

        if current == 0:

            text += "🌱 Start a new streak today!"

        elif current < 7:

            text += "✨ Keep going!"

        elif current < 30:

            text += "🚀 Amazing consistency!"

        else:

            text += "👑 Legendary streak!"

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # ACHIEVEMENTS
    # ========================================================

    if action == "menu_achievements":

        history = database.get_user_history(
            user_id
        )

        unlocked = analytics.achievements(
            history
        )

        if not unlocked:

            text = (
                "🏆 *Achievements*\n\n"
                "🌱 No achievements yet."
            )

        else:

            text = (
                "🏆 *Achievements*\n\n"
                + "\n".join(
                    f"✅ {item}"
                    for item in unlocked
                )
                + f"\n\n🎖️ Total unlocked: "
                f"*{len(unlocked)}*"
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # HISTORY
    # ========================================================

    if action == "menu_history":

        history = database.get_user_history(
            user_id
        )

        entries = analytics.recent_entries(
            history,
            10,
        )

        if not entries:

            text = (
                "📜 *History*\n\n"
                "🌱 Your history is empty."
            )

        else:

            lines = []

            for entry in entries:

                mood_key = entry.get(
                    "mood",
                    "unknown"
                )

                info = moods.MOODS.get(
                    mood_key,
                    {}
                )

                lines.append(
                    f"📅 {entry.get('date', '?')} — "
                    f"{info.get('emoji', '🌸')} "
                    f"{info.get('name', mood_key.title())}"
                )

            text = (
                "📜 *Recent History*\n\n"
                + "\n".join(lines)
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # PROFILE
    # ========================================================

    if action == "menu_profile":

        history = database.get_user_history(
            user_id
        )

        total = analytics.total_checkins(
            history
        )

        days = analytics.unique_days(
            history
        )

        level = analytics.get_level(
            history
        )

        xp = analytics.get_xp(
            history
        )

        streak = analytics.current_streak(
            history
        )

        best = analytics.best_streak(
            history
        )

        favorite = analytics.favorite_mood(
            history
        )

        if favorite:

            info = moods.MOODS.get(
                favorite,
                {}
            )

            favorite_text = (
                f"{info.get('emoji', '🌸')} "
                f"{info.get('name', favorite.title())}"
            )

        else:

            favorite_text = "No data yet"

        text = (
            "👤 *Your Profile*\n\n"

            f"💭 Check-ins: *{total}*\n"
            f"📅 Days tracked: *{days}*\n"
            f"⭐ Level: *{level}*\n"
            f"✨ XP: *{xp}*\n"
            f"🔥 Current streak: *{streak} days*\n"
            f"🏆 Best streak: *{best} days*\n"
            f"💖 Favorite: *{favorite_text}*\n"
        )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # FORECAST
    # ========================================================

    if action == "menu_forecast":

        history = database.get_user_history(
            user_id
        )

        data = analytics.mood_forecast(
            history
        )

        if not data.get(
            "has_data"
        ):

            text = data.get(
                "message",
                "🌱 Keep checking in first."
            )

        else:

            text = (
                "🔮 *Mood Pattern Forecast*\n\n"

                f"{data['pattern']}\n\n"

                f"🌸 Dominant: "
                f"*{data['dominant_emoji']} "
                f"{data['dominant_name']}*\n"

                f"📊 Share: *{data['percentage']}%*\n"
                f"🎯 Confidence: *{data['confidence']}*\n\n"

                f"🔮 {data['forecast']}\n\n"

                f"{data['disclaimer']}"
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # QUOTE
    # ========================================================

    if action == "menu_quote":

        try:

            text = messages.quote()

        except Exception:

            text = (
                "🌸 Small steps still count."
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # MOTIVATE
    # ========================================================

    if action == "menu_motivate":

        try:

            text = messages.motivate()

        except Exception:

            text = (
                "🔥 Keep going. "
                "You're doing better than you think."
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # RANDOM
    # ========================================================

    if action == "menu_random":

        try:

            text = get_random_content()

        except Exception:

            text = (
                "🎲 Random thought:\n\n"
                "🌈 Something good can happen "
                "when you least expect it."
            )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # ABOUT
    # ========================================================

    if action == "menu_about":

        text = (
            f"🌸 *{config.BOT_NAME}*\n\n"

            "Your personal mood companion. 💗\n\n"

            f"Version: *{config.VERSION}*\n\n"

            "🐍 Built with Python\n"
            "💙 Powered by Telegram"
        )

        await edit_menu_message(
            query,
            text,
            keyboards.back_keyboard(),
        )

        return

    # ========================================================
    # GOALS
    # ========================================================

    if action == "menu_goals":
        await show_v4_goals(update, context)
        return

    # ========================================================
    # DAILY REWARD
    # ========================================================

    if action == "menu_reward":
        await show_v4_reward(update, context)
        return

    # ========================================================
    # EXPORT
    # ========================================================

    if action == "menu_export":

        try:

            history = database.get_user_history(
                user_id
            )

            if not history:

                await edit_menu_message(
                    query,
                    (
                        "📤 *MoodBloom Export*\n\n"
                        "🌱 Your mood history is empty.\n\n"
                        "Add a few check-ins first!"
                    ),
                    keyboards.mood_keyboard(),
                )

                return

            document = build_export_file(
                history,
                user_id,
            )

            await query.message.reply_document(
                document=document,
                caption=(
                    "📤 *MoodBloom History Export*\n\n"
                    "Your complete mood history is here. 🌸"
                ),
                parse_mode="Markdown",
            )

            await edit_menu_message(
                query,
                (
                    "✅ *Export Ready!*\n\n"
                    "Your MoodBloom history has been "
                    "sent as a JSON file. 📤"
                ),
                keyboards.back_keyboard(),
            )

        except Exception as error:

            print(
                "Export error:",
                error
            )

            await edit_menu_message(
                query,
                (
                    "⚠️ *Export Unavailable*\n\n"
                    "I couldn't generate your history export "
                    "right now."
                ),
                keyboards.back_keyboard(),
            )

        return

    # ========================================================
    # UNKNOWN ACTION
    # ========================================================

    await edit_menu_message(
        query,
        (
            "🌸 I couldn't understand that menu option.\n\n"
            "Let's go back to the dashboard."
        ),
        keyboards.home_keyboard(),
    )


# ============================================================
# GROUP EDITION
# ============================================================

def is_group_chat(update):
    chat = update.effective_chat
    return bool(
        chat
        and chat.type in (
            "group",
            "supergroup",
        )
    )


async def is_group_admin(update, context):

    if not is_group_chat(update):
        return False

    try:

        member = await context.bot.get_chat_member(
            update.effective_chat.id,
            update.effective_user.id,
        )

        return member.status in (
            "administrator",
            "creator",
        )

    except Exception as error:

        print(
            "Group admin check error:",
            error
        )

        return False


async def require_group(update, context):

    if is_group_chat(update):
        return True

    message = update.effective_message

    if message:

        await message.reply_text(
            "👥 *Group Edition*\n\n"
            "This feature works inside a Telegram group or supergroup.\n"
            "Add MoodBloom to a group and try again. 🌸",
            parse_mode="Markdown",
        )

    return False


def load_current_group(update):

    groups = group_data.load_groups()

    chat = update.effective_chat

    group = group_data.get_group(
        groups,
        chat.id,
        chat.title or "This Group",
    )

    return groups, group


async def group_home_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    groups, group = load_current_group(
        update
    )

    group_data.save_groups(
        groups
    )

    summary = group_data.get_group_summary(
        groups,
        update.effective_chat.id,
    )

    await edit_menu_message(
        query,
        messages.group_dashboard(
            group.get(
                "name",
                "This Group"
            ),
            summary["member_count"],
        ),
        keyboards.group_keyboard(),
    )


async def group_mood_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    action = query.data

    if action == "group_mood":

        await edit_menu_message(
            query,
            messages.group_mood_prompt(),
            keyboards.group_mood_keyboard(),
        )

        return

    mood_key = (
        action[
            len("group_mood_"):
        ]
        .strip()
        .lower()
    )

    if not mood_key:

        await edit_menu_message(
            query,
            messages.group_mood_prompt(),
            keyboards.group_mood_keyboard(),
        )

        return

    valid_moods = getattr(
        moods,
        "MOODS",
        {}
    )

    if valid_moods and mood_key not in valid_moods:

        await edit_menu_message(
            query,
            "🌸 Please choose a mood from the buttons below.",
            keyboards.group_mood_keyboard(),
        )

        return

    groups, group = load_current_group(
        update
    )

    user = query.from_user

    group_data.record_group_mood(
        groups,
        update.effective_chat.id,
        user.id,
        mood_key,
        user.first_name
        or user.username
        or "User",
        group.get(
            "name",
            "This Group"
        ),
    )

    group_data.save_groups(
        groups
    )

    member = group_data.get_member(
        groups,
        update.effective_chat.id,
        user.id,
    ) or {}

    current = group_data.calculate_group_streak(
        groups,
        update.effective_chat.id,
    )

    text = messages.group_mood_result(
        user.first_name
        or user.username
        or "User",
        mood_key,
    )

    text += (
        f"\n\n✨ Points: *{member.get('points', 0)}*"
        f"\n🔥 Group streak: *{current} days*"
    )

    await edit_menu_message(
        query,
        text,
        keyboards.group_keyboard(),
    )


async def group_report_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    groups, group = load_current_group(
        update
    )

    summary = group_data.get_group_summary(
        groups,
        update.effective_chat.id,
    )

    text = messages.group_report(
        group.get(
            "name",
            "This Group"
        ),
        summary["total_checkins"],
        summary["member_count"],
        summary["dominant_mood"],
        summary["average_score"],
    )

    await edit_menu_message(
        query,
        text,
        keyboards.group_report_keyboard(),
    )


async def group_chart_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    groups, group = load_current_group(
        update
    )

    distribution = group_data.get_group_mood_counts(
        groups,
        update.effective_chat.id,
    )

    if not distribution:

        await edit_menu_message(
            query,
            (
                "📈 *Group Chart*\n\n"
                "🌱 No group mood data yet."
            ),
            keyboards.group_report_keyboard(),
        )

        return

    try:

        import matplotlib.pyplot as plt

        labels = list(
            distribution.keys()
        )

        values = list(
            distribution.values()
        )

        fig, ax = plt.subplots(
            figsize=(7, 4.5)
        )

        ax.bar(
            labels,
            values
        )

        ax.set_title(
            f"{group.get('name', 'This Group')} — Mood Distribution"
        )

        ax.set_ylabel(
            "Check-ins"
        )

        ax.tick_params(
            axis="x",
            rotation=25,
        )

        fig.tight_layout()

        image = BytesIO()

        fig.savefig(
            image,
            format="png",
            dpi=150,
        )

        plt.close(fig)

        image.seek(0)

        image.name = (
            "moodbloom_group_chart.png"
        )

        try:

            await query.message.delete()

        except Exception:

            pass

        await query.message.chat.send_photo(
            photo=image,
            caption=(
                "📈 *Group Mood Chart*\n\n"
                "A visual overview of group mood check-ins. 🌈"
            ),
            parse_mode="Markdown",
            reply_markup=keyboards.group_report_keyboard(),
        )

    except Exception as error:

        print(
            "Group chart error:",
            error
        )

        await edit_menu_message(
            query,
            (
                "⚠️ I couldn't generate "
                "the group chart right now."
            ),
            keyboards.group_report_keyboard(),
        )


async def group_activity_callback(
    update,
    context,
):
    """
    Shows V4 message-activity analytics for the group:
    total/today/week/month messages, peak hour/day,
    top member, next milestone, activity score.

    group_activity_me shows the caller's own stats instead.
    """

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    chat_id = update.effective_chat.id
    data = query.data or ""

    if data == "group_activity_me":

        user = update.effective_user

        text = group_analytics.format_member_analytics(
            chat_id,
            user.id,
        )

    else:

        overview = group_analytics.format_group_analytics(
            chat_id
        )

        top = group_analytics.format_top_members(
            chat_id,
            limit=5,
        )

        text = f"{overview}\n\n{top}"

    await edit_menu_message(
        query,
        text,
        keyboards.group_analytics_keyboard(),
        parse_mode="Markdown",
    )


async def group_leaderboard_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    groups, _ = load_current_group(
        update
    )

    text = messages.group_leaderboard(
        group_data.get_group_leaderboard(
            groups,
            update.effective_chat.id,
        )
    )

    await edit_menu_message(
        query,
        text,
        keyboards.leaderboard_keyboard(),
    )


async def group_streak_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    groups, _ = load_current_group(
        update
    )

    current = group_data.calculate_group_streak(
        groups,
        update.effective_chat.id,
    )

    best = group_data.calculate_best_group_streak(
        groups,
        update.effective_chat.id,
    )

    await edit_menu_message(
        query,
        messages.group_streak(
            current,
            best,
        ),
        keyboards.group_keyboard(),
    )


async def group_question_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    groups, group = load_current_group(
        update
    )

    existing = group_data.get_daily_question_data(
        groups,
        update.effective_chat.id,
    )

    if existing and existing.get(
        "question"
    ):

        question = existing["question"]

    else:

        question = messages.daily_question()

        group_data.set_daily_question(
            groups,
            update.effective_chat.id,
            question,
            group.get(
                "name",
                "This Group"
            ),
        )

        group_data.save_groups(
            groups
        )

    await edit_menu_message(
        query,
        question,
        keyboards.daily_question_keyboard(),
    )


async def group_question_answer(
    update,
    context,
):
    query = update.callback_query
    await safe_answer(query)
    if not await require_group(update, context):
        return
    context.user_data["group_question_answering"] = True
    await edit_menu_message(
        query,
        "💬 Send your answer in the group.\n\n"
        "There is no wrong answer — just share what you think. 🌸",
        keyboards.group_keyboard(),
    )


async def receive_group_question_answer(
    update,
    context,
):
    if not update.message or not is_group_chat(update):
        return False
    if not context.user_data.get("group_question_answering"):
        return False
    text = (update.message.text or "").strip()
    if not text:
        return True
    groups, _ = load_current_group(update)
    group_data.record_question_participation(
        groups, update.effective_chat.id, update.effective_user.id
    )
    group_data.save_groups(groups)
    context.user_data.pop("group_question_answering", None)
    await update.message.reply_text(
        "🌸 Nice answer! Thanks for sharing.\n\n"
        "Keep the conversation going with everyone. 💬"
    )
    return True


async def group_question_participate(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    groups, _ = load_current_group(
        update
    )

    group_data.record_question_participation(
        groups,
        update.effective_chat.id,
        query.from_user.id,
    )

    group_data.save_groups(
        groups
    )

    await edit_menu_message(
        query,
        (
            "✅ *Participation recorded!*\n\n"
            "Now share your answer in the group. 💬"
        ),
        keyboards.group_keyboard(),
    )


async def group_games_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    action = query.data

    if action == "group_games":

        text = messages.group_games()

    elif action == "group_game_random":

        text = messages.random_group_game()

    elif action == "group_game_wyr":

        text = messages.would_you_rather()


    else:

        text = messages.group_games()

    groups, _ = load_current_group(
        update
    )

    group_data.record_group_activity(
        groups,
        update.effective_chat.id,
        "games_played",
    )

    group_data.save_groups(
        groups
    )

    await edit_menu_message(
        query,
        text,
        keyboards.group_games_keyboard(),
    )


async def group_admin_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    if not await is_group_admin(
        update,
        context,
    ):

        await edit_menu_message(
            query,
            messages.admin_only_message(),
            keyboards.group_keyboard(),
        )

        return

    action = query.data

    if action == "group_admin":

        text = messages.group_admin()

        markup = keyboards.group_admin_keyboard()

    elif action == "group_moderation":

        text = messages.group_moderation()

        markup = keyboards.group_admin_keyboard()

    elif action == "group_welcome":

        groups, _ = load_current_group(
            update
        )

        enabled = group_data.is_welcome_enabled(
            groups,
            update.effective_chat.id,
        )

        text = messages.group_welcome_settings(
            enabled
        )

        markup = keyboards.group_welcome_keyboard()

    elif action == "group_announcement":

        context.user_data[
            "group_announcement_mode"
        ] = True

        text = (
            "📢 *Announcement*\n\n"
            "Send the announcement text now."
        )

        markup = keyboards.group_admin_keyboard()

    else:

        text = messages.group_settings(
            update.effective_chat.title
            or "This Group"
        )

        markup = keyboards.group_admin_keyboard()

    await edit_menu_message(
        query,
        text,
        markup,
    )


async def group_welcome_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    if not await is_group_admin(
        update,
        context,
    ):

        await edit_menu_message(
            query,
            messages.admin_only_message(),
            keyboards.group_keyboard(),
        )

        return

    groups, group = load_current_group(
        update
    )

    action = query.data

    if action == "welcome_enable":

        group_data.set_welcome_enabled(
            groups,
            update.effective_chat.id,
            True,
            group.get(
                "name",
                "This Group"
            ),
        )

        text = messages.group_success(
            "Welcome Enabled",
            (
                "New members will receive "
                "a MoodBloom welcome message. 👋"
            ),
        )

    elif action == "welcome_disable":

        group_data.set_welcome_enabled(
            groups,
            update.effective_chat.id,
            False,
            group.get(
                "name",
                "This Group"
            ),
        )

        text = messages.group_success(
            "Welcome Disabled",
            (
                "Automatic welcome messages "
                "are now disabled."
            ),
        )

    else:

        text = messages.group_welcome(
            query.from_user.first_name
            or "New Member",
            group.get(
                "name",
                "our group"
            ),
        )

    group_data.save_groups(
        groups
    )

    await edit_menu_message(
        query,
        text,
        keyboards.group_welcome_keyboard(),
    )


async def group_reminder_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    if not await is_group_admin(
        update,
        context,
    ):

        await edit_menu_message(
            query,
            messages.admin_only_message(),
            keyboards.group_keyboard(),
        )

        return

    action = query.data

    chat_id = update.effective_chat.id

    if action == "group_reminder":

        await edit_menu_message(
            query,
            messages.group_reminder(),
            keyboards.group_reminder_keyboard(),
        )

        return

    groups, group = load_current_group(
        update
    )

    if action == "group_remind_disable":

        group_data.set_group_reminder(
            groups,
            chat_id,
            False,
            None,
            group.get(
                "name",
                "This Group"
            ),
        )

        group_data.save_groups(
            groups
        )

        remove_existing_group_reminder_jobs(
            context.application,
            chat_id,
        )

        await edit_menu_message(
            query,
            "❌ *Group reminder disabled.*",
            keyboards.group_keyboard(),
        )

        return

    fixed = {
        "group_remind_8": (
            8,
            0,
            "8:00 AM"
        ),
        "group_remind_12": (
            12,
            0,
            "12:00 PM"
        ),
        "group_remind_18": (
            18,
            0,
            "6:00 PM"
        ),
        "group_remind_21": (
            21,
            0,
            "9:00 PM"
        ),
    }

    if action not in fixed:
        return

    hour, minute, label = fixed[action]

    group_data.set_group_reminder(
        groups,
        chat_id,
        True,
        f"{hour:02d}:{minute:02d}",
        group.get(
            "name",
            "This Group"
        ),
    )

    group_data.save_groups(
        groups
    )

    success = schedule_group_reminder(
        context.application,
        chat_id,
        hour,
        minute,
    )

    if success:

        text = (
            f"⏰ *Group reminder set!*\n\n"
            f"Daily reminder: *{label}*"
        )

    else:

        text = (
            "⚠️ Reminder saved, "
            "but JobQueue is unavailable."
        )

    await edit_menu_message(
        query,
        text,
        keyboards.group_keyboard(),
    )


async def group_help_callback(
    update,
    context,
):

    query = update.callback_query

    await safe_answer(query)

    if not await require_group(
        update,
        context,
    ):
        return

    await edit_menu_message(
        query,
        messages.group_help(),
        keyboards.group_keyboard(),
    )


def remove_existing_group_reminder_jobs(
    application,
    chat_id,
):

    try:

        job_queue = application.job_queue

    except Exception:

        job_queue = None

    if not job_queue:
        return

    try:

        for job in job_queue.get_jobs_by_name(
            f"group_daily_reminder_{chat_id}"
        ):

            job.schedule_removal()

    except Exception as error:

        print(
            "Group reminder removal error:",
            error
        )


def schedule_group_reminder(
    application,
    chat_id,
    hour,
    minute,
):

    try:

        job_queue = application.job_queue

    except Exception:

        job_queue = None

    if not job_queue:
        return False

    try:

        remove_existing_group_reminder_jobs(
            application,
            chat_id,
        )

        job_queue.run_daily(
            send_group_reminder,
            time=datetime.time(
                hour=int(hour),
                minute=int(minute),
                tzinfo=config.TIMEZONE,
            ),
            data={
                "chat_id": chat_id
            },
            name=f"group_daily_reminder_{chat_id}",
        )

        return True

    except Exception as error:

        print(
            "Group reminder scheduling error:",
            error
        )

        return False


async def send_group_reminder(
    context,
):

    job = context.job

    if not job:
        return

    chat_id = (
        job.data or {}
    ).get(
        "chat_id"
    )

    if not chat_id:
        return

    try:

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "⏰ *MoodBloom Group Reminder*\n\n"
                "How is everyone feeling today? 💭\n\n"
                "Tap *Group Mood* and check in. 🌸"
            ),
            parse_mode="Markdown",
            reply_markup=keyboards.group_mood_keyboard(),
        )

    except Exception as error:

        print(
            "Group reminder send error:",
            error
        )


def restore_group_reminders(
    application,
):

    groups = group_data.load_groups()

    restored = 0

    for key, group in groups.items():

        try:

            settings = group.get(
                "settings",
                {}
            )

            if not settings.get(
                "reminder_enabled"
            ):

                continue

            if not settings.get(
                "reminder_time"
            ):

                continue

            hour, minute = map(
                int,
                settings[
                    "reminder_time"
                ].split(":")[:2]
            )

            if schedule_group_reminder(
                application,
                int(key),
                hour,
                minute,
            ):

                restored += 1

        except Exception as error:

            print(
                "Group reminder restore error:",
                error
            )

    print(
        f"⏰ Restored {restored} group reminder(s)."
    )


async def handle_group_welcome_event(
    update,
    context,
):

    if (
        not update.message
        or not update.message.new_chat_members
        or not is_group_chat(update)
    ):

        return

    groups, group = load_current_group(
        update
    )

    if not group_data.is_welcome_enabled(
        groups,
        update.effective_chat.id,
    ):

        return

    for member in update.message.new_chat_members:

        if member.is_bot:
            continue

        group_data.add_member(
            groups,
            update.effective_chat.id,
            member.id,
            member.username,
            member.first_name,
            group.get(
                "name",
                "This Group"
            ),
        )

        await update.message.reply_text(
            messages.group_welcome(
                member.first_name
                or member.username
                or "New Member",
                group.get(
                    "name",
                    "our group"
                ),
            ),
        )

    group_data.save_groups(
        groups
    )

# ============================================================
# GROUP GOODBYE / MEMBER LEFT
# ============================================================

async def handle_group_goodbye_event(
    update,
    context,
):
    """
    Sends a short goodbye message when a member leaves
    a MoodBloom group.
    """

    if (
        not update.message
        or not update.message.left_chat_member
        or not is_group_chat(update)
    ):
        return

    member = update.message.left_chat_member

    # Never send goodbye for bots
    if member.is_bot:
        return

    groups, group = load_current_group(update)

    # Remove member from MoodBloom group data
    try:
        if hasattr(group_data, "remove_member"):
            group_data.remove_member(
                groups,
                update.effective_chat.id,
                member.id,
            )
            group_data.save_groups(groups)

    except Exception as error:
        print(
            "Group goodbye member cleanup error:",
            error,
        )

    name = (
        member.first_name
        or member.username
        or "Member"
    )

    group_name = group.get(
        "name",
        update.effective_chat.title
        or "our group",
    )

    text = (
        f"👋 *Goodbye, {name}!*\n\n"
        f"🌸 Take care and keep blooming.\n"
        f"— MoodBloom • {group_name}"
    )

    try:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
        )

    except Exception as error:
        print(
            "Group goodbye message error:",
            error,
        )


async def handle_group_text(
    update,
    context,
):

    if (
        not update.message
        or not update.message.text
        or not is_group_chat(update)
    ):

        return

    if not context.user_data.get(
        "group_announcement_mode"
    ):

        return

    if not await is_group_admin(
        update,
        context,
    ):

        context.user_data.pop(
            "group_announcement_mode",
            None,
        )

        await update.message.reply_text(
            messages.admin_only_message()
        )

        return

    announcement = (
        update.message.text.strip()
    )

    context.user_data.pop(
        "group_announcement_mode",
        None,
    )

    if announcement:

        await update.message.reply_text(
            "📢 *Announcement*\n\n"
            + announcement,
            parse_mode="Markdown",
        )


# ============================================================
# BOT COMMANDS / POST INIT
# ============================================================

async def post_init(
    application: Application,
):
    """
    Registers Telegram bot commands,
    restores saved reminders,
    restores group reminders,
    and starts the morning-wish scheduler.
    """

    commands = [
        BotCommand(
            "start",
            "Open MoodBloom"
        ),
        BotCommand(
            "menu",
            "Open dashboard"
        ),
        BotCommand(
            "bloom",
            "Open Bloom Journey"
        ),
        BotCommand(
            "goals",
            "View daily goals"
        ),
        BotCommand(
            "reward",
            "Claim daily reward"
        ),
        BotCommand(
            "birthday",
            "Manage your birthday"
        ),
        BotCommand(
            "groupbirthday",
            "Add birthday for this group"
        ),
        BotCommand(
            "study",
            "Start a study session"
        ),
        BotCommand(
            "notifications",
            "Manage notification settings"
        ),
        BotCommand(
            "mood",
            "Record your mood"
        ),
        BotCommand(
            "daily",
            "Today's overview"
        ),
        BotCommand(
            "stats",
            "View statistics"
        ),
        BotCommand(
            "chart",
            "View mood chart"
        ),
        BotCommand(
            "weekly",
            "Weekly summary"
        ),
        BotCommand(
            "weeklychart",
            "Weekly chart"
        ),
        BotCommand(
            "insights",
            "Smart insights"
        ),
        BotCommand(
            "forecast",
            "Mood pattern forecast"
        ),
        BotCommand(
            "profile",
            "View profile"
        ),
        BotCommand(
            "history",
            "View history"
        ),
        BotCommand(
            "streak",
            "View streak"
        ),
        BotCommand(
            "achievements",
            "View achievements"
        ),
        BotCommand(
            "quote",
            "Get a quote"
        ),
        BotCommand(
            "motivate",
            "Get motivation"
        ),
        BotCommand(
            "random",
            "Random content"
        ),
        BotCommand(
            "remind",
            "Set daily reminder"
        ),
        BotCommand(
            "remindoff",
            "Disable reminder"
        ),
        BotCommand(
            "export",
            "Export mood history"
        ),
        BotCommand(
            "clear",
            "Clear mood history"
        ),
        BotCommand(
            "story",
            "Play an interactive story"
        ),
        BotCommand(
            "mystery",
            "Solve a mystery"
        ),
        BotCommand(
            "help",
            "Show help"
        ),
        BotCommand(
            "about",
            "About MoodBloom"
        ),
    ]

    # --------------------------------------------------------
    # Telegram commands
    # --------------------------------------------------------

    try:

        await application.bot.set_my_commands(
            commands
        )

    except Exception as error:

        print(
            "Command registration error:",
            error
        )

    # --------------------------------------------------------
    # Restore user reminders
    # --------------------------------------------------------

    try:

        restore_saved_reminders(
            application
        )

        print(
            "✅ Saved reminders restored."
        )

    except Exception as error:

        print(
            "⚠️ Reminder restoration error:",
            error
        )

    # --------------------------------------------------------
    # Restore group reminders
    # --------------------------------------------------------

    try:

        group_data.ensure_group_database()

        restore_group_reminders(
            application
        )

    except Exception as error:

        print(
            "⚠️ Group reminder restoration error:",
            error
        )

    # --------------------------------------------------------
    # MORNING WISH SCHEDULER
    # --------------------------------------------------------

    try:

        scheduler.setup_scheduler(
            application
        )

    except Exception as error:

        print(
            "⚠️ Scheduler initialization error:",
            error
        )


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Global error handler.
    """

    print(
        "MoodBloom error:",
        context.error
    )


# ============================================================
# MAIN
# ============================================================

def acquire_single_instance(lock_file="data/bot.lock"):
    """Ensure only one MoodBloom instance is running at a time."""
    lock_path = os.path.abspath(lock_file)
    lock_dir = os.path.dirname(lock_path)
    if lock_dir and not os.path.exists(lock_dir):
        os.makedirs(lock_dir, exist_ok=True)

    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        with os.fdopen(lock_fd, "w", encoding="utf-8") as lock_handle:
            lock_handle.write(str(os.getpid()))
        atexit.register(lambda: _release_single_instance(lock_path))
        return True
    except FileExistsError:
        try:
            with open(lock_path, "r", encoding="utf-8") as existing:
                pid_text = existing.read().strip()
            pid = int(pid_text) if pid_text else None
        except (OSError, ValueError):
            pid = None

        if pid and _pid_is_running(pid):
            print(f"⚠️ MoodBloom is already running (PID {pid}). Exiting.")
            return False

        try:
            os.remove(lock_path)
        except OSError:
            pass

        return acquire_single_instance(lock_file)


def _pid_is_running(pid):
    """Return True when the given PID is still active on this machine."""
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _release_single_instance(lock_file):
    try:
        if os.path.exists(lock_file):
            os.remove(lock_file)
    except OSError:
        pass


def main():
    """
    Starts MoodBloom bot.
    """

    if not acquire_single_instance():
        return

    print(
        f"🌸 Starting {config.BOT_NAME} "
        f"{config.VERSION}..."
    )

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    try:

        database.ensure_database()

        print(
            "✅ Database ready."
        )

    except Exception as error:

        print(
            "⚠️ Database initialization error:",
            error
        )

    try:

        group_data.ensure_group_database()

        print(
            "✅ Group database ready."
        )

    except Exception as error:

        print(
            "⚠️ Group database initialization error:",
            error
        )

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    telegram_ssl_context = ssl.create_default_context()
    telegram_ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    telegram_ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2

    application = (
        Application.builder()
        .token(
            config.BOT_TOKEN
        )
        .request(
            HTTPXRequest(
                httpx_kwargs={
                    "verify": telegram_ssl_context,
                }
            )
        )
        .post_init(
            post_init
        )
        .build()
    )

    # ========================================================
    # AUTOMATIC ACTIVITY REGISTRATION
    # ========================================================

    application.add_handler(
        TypeHandler(
            Update,
            register_activity,
            block=False,
        ),
        group=-1,
    )

    # ========================================================
    # COMMAND HANDLERS
    # ========================================================

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
    CommandHandler("bloom", bloom_command)
)

    application.add_handler(
    CommandHandler("goals", show_v4_goals)
)

    application.add_handler(
    CommandHandler("reward", show_v4_reward)
)

    application.add_handler(
    CommandHandler("birthday", birthday_command)
)

    application.add_handler(
    CommandHandler("groupbirthday", group_birthday_command)
)

    application.add_handler(
    CommandHandler("study", study_command)
)

    application.add_handler(
    CommandHandler("notifications", notifications_command)
)

    application.add_handler(
        CommandHandler("story", story_engine.story_command)
    )

    application.add_handler(
        CommandHandler("mystery", mystery_engine.mystery_command)
    )


    application.add_handler(
        CommandHandler(
            "menu",
            menu
        )
    )

    application.add_handler(
        CommandHandler(
            "mood",
            mood
        )
    )

    application.add_handler(
        CommandHandler(
            "daily",
            daily
        )
    )

    application.add_handler(
        CommandHandler(
            "profile",
            profile
        )
    )

    application.add_handler(
        CommandHandler(
            "stats",
            stats
        )
    )

    application.add_handler(
        CommandHandler(
            "chart",
            chart
        )
    )

    application.add_handler(
        CommandHandler(
            "weeklychart",
            weekly_chart
        )
    )

    application.add_handler(
        CommandHandler(
            "weekly",
            weekly
        )
    )

    application.add_handler(
        CommandHandler(
            "today",
            today
        )
    )

    application.add_handler(
        CommandHandler(
            "history",
            history
        )
    )

    application.add_handler(
        CommandHandler(
            "insights",
            insights
        )
    )

    application.add_handler(
        CommandHandler(
            "forecast",
            forecast
        )
    )

    application.add_handler(
        CommandHandler(
            "streak",
            streak
        )
    )

    application.add_handler(
        CommandHandler(
            "achievements",
            achievements
        )
    )

    application.add_handler(
        CommandHandler(
            "quote",
            quote
        )
    )

    application.add_handler(
        CommandHandler(
            "motivate",
            motivate
        )
    )

    application.add_handler(
        CommandHandler(
            "random",
            random_message
        )
    )

    application.add_handler(
        CommandHandler(
            "remind",
            remind
        )
    )

    application.add_handler(
        CommandHandler(
            "remindoff",
            remindoff
        )
    )

    application.add_handler(
        CommandHandler(
            "export",
            export_history
        )
    )

    application.add_handler(
        CommandHandler(
            "clear",
            clear
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    application.add_handler(
        CommandHandler(
            "about",
            about
        )
    )

    # ========================================================
    # CALLBACK HANDLERS
    # ========================================================

    application.add_handler(
        CallbackQueryHandler(
            handle_reminder,
            pattern=r"^remind_",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_clear,
            pattern=r"^clear_(confirm|cancel)$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_mood,
            pattern=r"^mood_",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_menu,
            pattern=r"^(home|menu_(?!group$))",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            story_engine.handle_story_callback,
            pattern=r"^mb_story\|",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            mystery_engine.handle_mystery_callback,
            pattern=r"^mb_mystery\|",
        )
    )

    # ========================================================
    # GROUP CALLBACK HANDLERS
    # ========================================================

    application.add_handler(
        CallbackQueryHandler(
            group_home_callback,
            pattern=r"^menu_group$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_mood_callback,
            pattern=r"^group_mood(?:_.+)?$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_report_callback,
            pattern=r"^group_report$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_chart_callback,
            pattern=r"^group_chart$",
        )
    )

    application.add_handler(
    CallbackQueryHandler(
        handle_v4_callback,
        pattern=r"^v4_"
    )
)

    application.add_handler(
    CallbackQueryHandler(
        handle_birthday_callback,
        pattern=r"^birthday_"
    )
)

    application.add_handler(
    CallbackQueryHandler(
        handle_study_callback,
        pattern=r"^study_"
    )
)

    application.add_handler(
    CallbackQueryHandler(
        handle_notification_callback,
        pattern=r"^notif_"
    )
)


    application.add_handler(
        CallbackQueryHandler(
            group_leaderboard_callback,
            pattern=r"^group_leaderboard$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_activity_callback,
            pattern=r"^group_activity(?:_me)?$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_streak_callback,
            pattern=r"^group_streak$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_question_callback,
            pattern=r"^group_question$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_question_answer,
            pattern=r"^group_question_answer$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_question_participate,
            pattern=r"^(question_answer)$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_games_callback,
            pattern=r"^group_(?:games|game_.+)$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_admin_callback,
            pattern=r"^(group_admin|group_moderation|group_welcome|group_announcement|group_settings)$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_welcome_callback,
            pattern=r"^(welcome_enable|welcome_disable|welcome_preview)$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_reminder_callback,
            pattern=r"^group_reminder$|^group_remind_(?:8|12|18|21|disable)$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            group_help_callback,
            pattern=r"^group_help$",
        )
    )

    # ========================================================
    # GROUP EVENTS
    # ========================================================

    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            handle_group_welcome_event,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.StatusUpdate.LEFT_CHAT_MEMBER,
            handle_group_goodbye_event,
        )
    )

    # ========================================================
    # TEXT HANDLERS
    # ========================================================

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            receive_group_question_answer,
        ),
        group=-1,
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            handle_group_text,
        ),
        group=0,
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            receive_custom_reminder_time,
        ),
        group=1,
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            receive_birthday_date_input,
        ),
        group=2,
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            receive_quiet_hours_input,
        ),
        group=3,
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            receive_custom_reminder_input,
        ),
        group=4,
    )

    # ========================================================
    # ERROR HANDLER
    # ========================================================

    application.add_error_handler(
        error_handler
    )

    # ========================================================
    # START POLLING
    # ========================================================

    print(
        "🤖 MoodBloom is running..."
    )

    application.run_polling(
        drop_pending_updates=True
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()