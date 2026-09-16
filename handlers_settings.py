# ============================================================
# MOODBLOOM 4.0 — SETTINGS HANDLERS
# ============================================================

from telegram.ext import CommandHandler, CallbackQueryHandler

import notifications
import keyboards


# ============================================================
# COMMAND
# ============================================================

async def settings_command(update, context):
    user = update.effective_user
    if not user:
        return

    text = notifications.format_notification_settings(user.id)

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=keyboards.settings_toggle_keyboard(user.id),
    )


# ============================================================
# CALLBACKS
# ============================================================

async def settings_callback(update, context):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    user = update.effective_user
    if not user:
        return

    user_id = user.id
    data = query.data or ""

    if data == "menu_settings":
        text = notifications.format_notification_settings(user_id)
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=keyboards.settings_toggle_keyboard(user_id),
        )
        return

    if data == "set_refresh":
        text = notifications.format_notification_settings(user_id)
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=keyboards.settings_toggle_keyboard(user_id),
        )
        return

    if data.startswith("set_toggle_"):
        key = data[len("set_toggle_"):]

        settings = notifications.get_notification_settings(user_id)

        if key == "enabled":
            new_val = not settings.get("enabled", True)
            notifications.set_notifications_enabled(user_id, new_val)
        else:
            current = settings.get(key, True)
            notifications.update_notification_settings(user_id, **{key: not current})

        text = notifications.format_notification_settings(user_id)
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=keyboards.settings_toggle_keyboard(user_id),
        )
        return

    if data == "set_quiet":
        settings = notifications.get_notification_settings(user_id)
        quiet = settings.get("quiet_hours", {})
        new_state = not quiet.get("enabled", False)

        notifications.update_notification_settings(
            user_id, quiet_hours_enabled=new_state
        )

        text = notifications.format_notification_settings(user_id)
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=keyboards.settings_toggle_keyboard(user_id),
        )
        return

    if data == "set_stats":
        text = notifications.format_notification_stats(user_id)
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=keyboards.settings_toggle_keyboard(user_id),
        )
        return

    if data == "set_help":
        await query.edit_message_text(
            "⚙️ <b>Settings Help</b>\n\n"
            "Tap any toggle to enable/disable.\n"
            "Quiet hours pause notifications at night.",
            parse_mode="HTML",
            reply_markup=keyboards.settings_toggle_keyboard(user_id),
        )
        return


# ============================================================
# REGISTER
# ============================================================

def register_settings_handlers(application):
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(
        CallbackQueryHandler(
            settings_callback,
            pattern=r"^(menu_settings|set_)"
        )
    )