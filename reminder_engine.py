"""MoodBloom custom reminder engine.

Personal reminders are isolated by Telegram user ID.
Group reminders are isolated by Telegram chat ID.
There is no application-level reminder count limit.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, date, time, timedelta
from pathlib import Path
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters,
)

import config

REMINDER_FILE = Path(config.DATA_FILE).parent / "reminders.json"
FLOW_KEY = "moodbloom_reminder_flow"
CHECK_INTERVAL_SECONDS = 20


def _now() -> datetime:
    return datetime.now(config.TIMEZONE)


def _load() -> dict[str, Any]:
    REMINDER_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not REMINDER_FILE.exists():
        return {"personal": {}, "groups": {}}
    try:
        data = json.loads(REMINDER_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Invalid reminder database")
    except (OSError, json.JSONDecodeError, ValueError):
        # Preserve the broken file for recovery rather than overwriting it.
        backup = REMINDER_FILE.with_suffix(".corrupt.json")
        try:
            if not backup.exists():
                REMINDER_FILE.replace(backup)
        except OSError:
            pass
        data = {"personal": {}, "groups": {}}
    data.setdefault("personal", {})
    data.setdefault("groups", {})
    return data


def _save(data: dict[str, Any]) -> None:
    REMINDER_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp = REMINDER_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(REMINDER_FILE)


def _scope_key(scope: str, scope_id: int | str) -> str:
    return str(scope_id)


def _items(data: dict[str, Any], scope: str, scope_id: int | str) -> list[dict[str, Any]]:
    return data.setdefault(scope, {}).setdefault(_scope_key(scope, scope_id), [])


def _markup(rows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(rows)


def _btn(text: str, callback: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=callback)


def _menu(scope: str) -> InlineKeyboardMarkup:
    if scope == "groups":
        rows = [
            [_btn("➕ Reminder in this group", "rem2|new|group")],
            [_btn("📨 Send reminder to a person", "rem2|new|person_group")],
            [_btn("📋 This group's reminders", "rem2|list|group")],
        ]
    else:
        rows = [
            [_btn("➕ Reminder for me", "rem2|new|self")],
            [_btn("📨 Send reminder to a person", "rem2|new|person_personal")],
            [_btn("📋 My saved reminders", "rem2|list|personal")],
        ]
    rows.append([_btn("🏠 Home", "home")])
    return _markup(rows)


def _scope_for(update: Update, requested: str | None = None) -> tuple[str, str]:
    chat = update.effective_chat
    user = update.effective_user
    if requested == "group" or (requested is None and chat and chat.type in ("group", "supergroup")):
        return "groups", str(chat.id if chat else "")
    return "personal", str(user.id if user else "")


async def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    if not chat or chat.type not in ("group", "supergroup"):
        return False
    if not user:
        return False
    try:
        admins = await context.bot.get_chat_administrators(chat.id)
        return any(member.user.id == user.id for member in admins)
    except Exception:
        return False


def _parse_content(raw: str) -> tuple[str, str]:
    raw = raw.strip()
    if "|" in raw:
        title, message = raw.split("|", 1)
        title, message = title.strip(), message.strip()
        if title and message:
            return title[:100], message[:3500]
    if not raw:
        raise ValueError("Message blank hai.")
    return raw[:80], raw[:3500]


def parse_due_datetime(raw: str) -> datetime:
    """Accept common date/time formats in configured timezone."""
    value = raw.strip().lower()
    now = _now()
    formats = (
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%d %b %Y %H:%M",
        "%d %B %Y %H:%M",
    )
    if value.startswith("tomorrow "):
        t = datetime.strptime(value[9:].strip(), "%H:%M").time()
        due = datetime.combine(now.date() + timedelta(days=1), t, tzinfo=config.TIMEZONE)
    elif value.startswith("today "):
        t = datetime.strptime(value[6:].strip(), "%H:%M").time()
        due = datetime.combine(now.date(), t, tzinfo=config.TIMEZONE)
    elif re.fullmatch(r"\d{1,2}:\d{2}", value):
        t = datetime.strptime(value, "%H:%M").time()
        due = datetime.combine(now.date(), t, tzinfo=config.TIMEZONE)
        if due <= now:
            due += timedelta(days=1)
    else:
        due = None
        for fmt in formats:
            try:
                parsed = datetime.strptime(raw.strip(), fmt)
                due = parsed.replace(tzinfo=config.TIMEZONE)
                break
            except ValueError:
                continue
        if due is None:
            raise ValueError("Date/time format samajh nahi aaya.")
    if due <= now + timedelta(seconds=3):
        raise ValueError("Time future mein hona chahiye. Thoda aage ka time do.")
    return due


def _resolve_username(raw: str) -> int | None:
    """Resolve only usernames previously observed in a group. Telegram bots cannot DM an arbitrary @username."""
    username = raw.strip().lstrip("@").casefold()
    if not username:
        return None
    # The group database is a local cache of members the bot has actually seen.
    path = Path(config.DATA_FILE).parent / "groups.json"
    try:
        groups = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(groups, dict):
        return None
    for group in groups.values():
        members = group.get("members", {}) if isinstance(group, dict) else {}
        for uid, member in members.items():
            if isinstance(member, dict):
                saved = str(member.get("username") or "").lstrip("@").casefold()
                if saved and saved == username:
                    try:
                        return int(member.get("user_id") or uid)
                    except (TypeError, ValueError):
                        continue
    return None


def _short_id(value: str) -> str:
    return value[:8]


def _list_keyboard(
    scope: str,
    scope_id: str,
    reminders: list[dict[str, Any]],
    page: int = 0,
) -> InlineKeyboardMarkup:
    page_size = 10
    total_pages = max(1, (len(reminders) + page_size - 1) // page_size)
    page = max(0, min(page, total_pages - 1))
    start = page * page_size
    rows = []
    for item in reminders[start:start + page_size]:
        due = item.get("due_at", "")
        try:
            dt = datetime.fromisoformat(due)
            due_label = dt.strftime("%d %b, %I:%M %p")
        except (ValueError, TypeError):
            due_label = "time unavailable"
        status_icon = {"pending": "⏳", "sent": "✅", "failed": "⚠️"}.get(
            item.get("status"), "📌"
        )
        label = f"🗑️ {status_icon} {due_label} · {item.get('title', 'Reminder')[:20]}"
        rows.append([
            _btn(
                label,
                f"rem2|del|{scope}|{scope_id}|{item.get('id', '')}",
            )
        ])
    nav = []
    kind = "group" if scope == "groups" else "personal"
    if page > 0:
        nav.append(_btn("⬅️ Previous", f"rem2|list|{kind}|{page - 1}"))
    if page < total_pages - 1:
        nav.append(_btn("Next ➡️", f"rem2|list|{kind}|{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([_btn("🔄 Refresh", f"rem2|list|{kind}|{page}")])
    rows.append([_btn("⬅️ Reminder menu", f"rem2|menu|{kind}")])
    return _markup(rows)


async def reminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user or not update.effective_message:
        return
    if update.effective_chat.type in ("group", "supergroup"):
        if not await _is_admin(update, context):
            await update.effective_message.reply_text("⛔ Group reminders sirf group admins manage kar sakte hain.")
            return
        scope = "groups"
        text = "⏰ GROUP REMINDER STUDIO\n\nIs group ke reminders sirf isi group mein save aur list honge."
    else:
        scope = "personal"
        text = "⏰ PERSONAL REMINDER STUDIO\n\nYahan save kiye reminders sirf aapke personal account mein dikhenge."
    await update.effective_message.reply_text(text, reply_markup=_menu(scope))


async def cancel_reminder_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop(FLOW_KEY, None)
    if update.effective_message:
        await update.effective_message.reply_text("Reminder setup cancel ho gaya. Naya reminder banane ke liye /reminders bhejo.")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    data = (query.data or "").split("|")
    await query.answer()
    if query.data == "menu_reminder":
        await query.edit_message_text(
            "⏰ PERSONAL REMINDER STUDIO\n\n"
            "Custom date/time, recipient delivery, and unlimited saved reminders.",
            reply_markup=_menu("personal"),
        )
        return
    if len(data) == 3 and data[0] == "rem2" and data[1] == "menu":
        scope = "groups" if data[2] == "group" else "personal"
        if scope == "groups" and not await _is_admin(update, context):
            await query.edit_message_text("⛔ Group reminders sirf admins manage kar sakte hain.")
            return
        title = "⏰ GROUP REMINDER STUDIO" if scope == "groups" else "⏰ PERSONAL REMINDER STUDIO"
        await query.edit_message_text(title + "\n\nCustom time, date, unlimited saved reminders.", reply_markup=_menu(scope))
        return
    if len(data) == 3 and data[0] == "rem2" and data[1] == "new":
        action = data[2]
        scope = "groups" if action in ("group", "person_group") else "personal"
        if scope == "groups" and not await _is_admin(update, context):
            await query.edit_message_text("⛔ Group reminders sirf admins manage kar sakte hain.")
            return
        delivery = "group" if action == "group" else ("self" if action == "self" else "person")
        context.user_data[FLOW_KEY] = {
            "scope": scope,
            "scope_id": str(update.effective_chat.id if scope == "groups" else update.effective_user.id),
            "delivery": delivery,
            "step": "content" if delivery != "person" else "target",
            "creator_id": update.effective_user.id,
        }
        if delivery == "person":
            prompt = "👤 Recipient ka Telegram user ID ya @username bhejo.\n\nNote: @username tabhi chalega jab bot ne us user ko pehle group mein dekha ho. Reliable option numeric user ID hai. /cancel se ruk sakte ho."
        else:
            prompt = "✍️ Reminder ka title aur message bhejo.\n\nFormat: Title | Message\nExample: Paani peena | Abhi ek glass paani pi lo"
        await query.message.reply_text(prompt)
        return
    if len(data) in (3, 4) and data[0] == "rem2" and data[1] == "list":
        scope = "groups" if data[2] == "group" else "personal"
        if scope == "groups" and not await _is_admin(update, context):
            await query.edit_message_text("⛔ Group reminders sirf admins manage kar sakte hain.")
            return
        try:
            page = int(data[3]) if len(data) == 4 else 0
        except (TypeError, ValueError):
            page = 0
        scope_id = str(update.effective_chat.id if scope == "groups" else update.effective_user.id)
        db = _load()
        reminders = _items(db, scope, scope_id)
        if not reminders:
            await query.edit_message_text("📭 Is jagah par abhi koi saved reminder nahi hai.", reply_markup=_menu(scope))
            return
        pending = sum(1 for item in reminders if item.get("status") == "pending")
        text = (
            f"📋 Saved reminders: {len(reminders)}\n"
            f"⏳ Pending: {pending}\n"
            "Delete karne ke liye reminder ke button par tap karo. Pages se saare reminders manage kar sakte ho."
        )
        await query.edit_message_text(
            text,
            reply_markup=_list_keyboard(scope, scope_id, reminders, page),
        )
        return
    if len(data) == 5 and data[0] == "rem2" and data[1] == "del":
        _, _, scope, scope_id, reminder_id = data
        expected_id = str(update.effective_chat.id if scope == "groups" else update.effective_user.id)
        if scope_id != expected_id:
            await query.edit_message_text("Ye reminder tumhare current scope ka nahi hai.")
            return
        if scope == "groups" and not await _is_admin(update, context):
            await query.edit_message_text("⛔ Sirf group admins reminders delete kar sakte hain.")
            return
        db = _load()
        items = _items(db, scope, scope_id)
        before = len(items)
        items[:] = [item for item in items if item.get("id") != reminder_id]
        _save(db)
        await query.edit_message_text("✅ Reminder delete kar diya." if len(items) < before else "Reminder nahi mila.", reply_markup=_menu(scope))
        return


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat or not message.text:
        return
    flow = context.user_data.get(FLOW_KEY)
    if not isinstance(flow, dict):
        return
    # Keep a group flow in the exact group where it was started.
    if flow.get("scope") == "groups" and str(chat.id) != flow.get("scope_id"):
        return
    text = message.text.strip()
    if text.startswith("/cancel"):
        await cancel_reminder_flow(update, context)
        return
    step = flow.get("step")
    if step == "target":
        recipient_id = None
        if re.fullmatch(r"\d{4,20}", text):
            recipient_id = int(text)
        else:
            recipient_id = _resolve_username(text)
        if not recipient_id:
            await message.reply_text("❗ User ID resolve nahi hua. Numeric Telegram user ID bhejo, ya bot ko us user ko kisi group mein dekhna hoga.")
            return
        flow["recipient_id"] = recipient_id
        flow["step"] = "content"
        await message.reply_text("✍️ Ab reminder ka title aur message bhejo.\n\nFormat: Title | Message")
        return
    if step == "content":
        try:
            title, body = _parse_content(text)
        except ValueError as error:
            await message.reply_text(str(error))
            return
        flow["title"] = title
        flow["message"] = body
        flow["step"] = "time"
        await message.reply_text(
            "🗓️ Reminder kab bhejna hai? Date + time bhejo (IST).\n\n"
            "Examples:\n"
            "• 2026-12-31 18:30\n"
            "• 31-12-2026 18:30\n"
            "• tomorrow 09:15\n"
            "• today 21:00\n"
            "• 18:30 (agar aaj ka time nikal gaya ho to kal maana jayega)"
        )
        return
    if step == "time":
        try:
            due = parse_due_datetime(text)
        except ValueError:
            await message.reply_text("❗ Date/time valid nahi hai ya past mein hai. `YYYY-MM-DD HH:MM`, `DD-MM-YYYY HH:MM`, `tomorrow HH:MM` ya `HH:MM` format try karo.")
            return
        db = _load()
        scope = flow["scope"]
        scope_id = str(flow["scope_id"])
        delivery = flow["delivery"]
        target_id = int(scope_id) if delivery == "self" else (
            int(scope_id) if delivery == "group" else int(flow["recipient_id"])
        )
        reminder = {
            "id": uuid.uuid4().hex[:12],
            "scope": scope,
            "scope_id": scope_id,
            "delivery": delivery,
            "target_id": target_id,
            "recipient_id": flow.get("recipient_id"),
            "creator_id": user.id,
            "title": flow["title"],
            "message": flow["message"],
            "due_at": due.isoformat(),
            "created_at": _now().isoformat(),
            "status": "pending",
        }
        _items(db, scope, scope_id).append(reminder)
        _save(db)
        context.user_data.pop(FLOW_KEY, None)
        target_text = "aapko" if delivery == "self" else ("is group mein" if delivery == "group" else f"user ID {target_id} ko")
        await message.reply_text(
            f"✅ Reminder save ho gaya!\n\n"
            f"📌 {reminder['title']}\n"
            f"🕒 {due.strftime('%d %b %Y, %I:%M %p')} IST\n"
            f"📨 Delivery: {target_text}\n\n"
            "Reminder persistent storage mein save hai; bot restart ke baad bhi pending reminder restore rahega.",
            reply_markup=_menu(scope),
        )


async def dispatch_due_reminders(context: ContextTypes.DEFAULT_TYPE) -> None:
    db = _load()
    now = _now()
    changed = False
    for scope in ("personal", "groups"):
        scopes = db.get(scope, {})
        for scope_id, reminders in list(scopes.items()):
            if not isinstance(reminders, list):
                continue
            for item in reminders:
                if item.get("status") != "pending":
                    continue
                try:
                    due = datetime.fromisoformat(item["due_at"])
                    if due.tzinfo is None:
                        due = due.replace(tzinfo=config.TIMEZONE)
                except (KeyError, TypeError, ValueError):
                    item["status"] = "failed"
                    item["error"] = "invalid_due_at"
                    changed = True
                    continue
                if due > now:
                    continue
                delivery = item.get("delivery")
                target = item.get("target_id")
                title = str(item.get("title") or "Reminder")
                body = str(item.get("message") or "")
                text = f"⏰ REMINDER\n\n📌 {title}\n\n{body}\n\n🌸 MoodBloom"
                try:
                    await context.bot.send_message(chat_id=int(target), text=text)
                    item["status"] = "sent"
                    item["sent_at"] = now.isoformat()
                except Exception as exc:
                    item["status"] = "failed"
                    item["error"] = str(exc)[:300]
                    creator = item.get("creator_id")
                    try:
                        await context.bot.send_message(
                            chat_id=int(creator),
                            text=(
                                f"⚠️ Reminder deliver nahi ho paya: {title}\n\n"
                                "Agar recipient personal chat hai, us user ko pehle bot ka /start karna hoga. "
                                "Group reminder ke liye bot ko group mein rehna chahiye."
                            ),
                        )
                    except Exception:
                        pass
                changed = True
    if changed:
        _save(db)


async def _job_error_handler(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await dispatch_due_reminders(context)
    except Exception as exc:
        print("MoodBloom reminder worker error:", exc)


def register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("reminders", reminders_command))
    application.add_handler(CommandHandler("cancel", cancel_reminder_flow))
    application.add_handler(CallbackQueryHandler(handle_callback, pattern=r"^rem2\|"))
    application.add_handler(CallbackQueryHandler(handle_callback, pattern=r"^menu_reminder$"))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
        group=-2,
    )
    if application.job_queue is not None:
        for job in application.job_queue.get_jobs_by_name("moodbloom_custom_reminder_worker"):
            job.schedule_removal()
        application.job_queue.run_repeating(
            dispatch_due_reminders,
            interval=CHECK_INTERVAL_SECONDS,
            first=5,
            name="moodbloom_custom_reminder_worker",
        )
    else:
        print("WARNING: JobQueue unavailable; install python-telegram-bot[job-queue]. Custom reminders won't auto-send.")
