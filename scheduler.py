# ============================================================
# MOODBLOOM 4.0 — SCHEDULER
# ============================================================
# Handles:
#   🌅 Morning Wishes
#   🎯 Daily Goals
#   🎁 Daily Rewards
#   🎂 Birthday Reminders
#   🔔 Notification Checks
#   🧹 Daily Maintenance
#   💾 Automatic Backups
#   📊 Analytics Maintenance
#
# Existing morning-wish scheduler functionality preserved.
# ============================================================

from datetime import datetime, time

from telegram.ext import ContextTypes

import config
import database
import morning_wishes
import notifications
import backup
import birthdays
import goals
import rewards
import group_analytics
import mystery_engine


# ============================================================
# GENERAL SETTINGS
# ============================================================

TIMEZONE = getattr(
    config,
    "TIMEZONE",
    None,
)


# ============================================================
# JOB NAMES
# ============================================================

MORNING_WISH_JOB_NAME = (
    "moodbloom_morning_wish"
)

DAILY_GOALS_JOB_NAME = (
    "moodbloom_daily_goals"
)

DAILY_REWARD_JOB_NAME = (
    "moodbloom_daily_reward"
)

BIRTHDAY_JOB_NAME = (
    "moodbloom_birthday"
)

NOTIFICATION_JOB_NAME = (
    "moodbloom_notifications"
)

DAILY_MAINTENANCE_JOB_NAME = (
    "moodbloom_daily_maintenance"
)

WEEKLY_MAINTENANCE_JOB_NAME = (
    "moodbloom_weekly_maintenance"
)

AUTO_BACKUP_JOB_NAME = (
    "moodbloom_auto_backup"
)

AFTERNOON_WISH_JOB_NAME = "moodbloom_afternoon_wish"
NIGHT_WISH_JOB_NAME = "moodbloom_night_wish"
DAILY_MYSTERY_JOB_NAME = "moodbloom_daily_mystery"


# ============================================================
# SCHEDULE TIMES
# ============================================================

MORNING_WISH_HOUR = 8
MORNING_WISH_MINUTE = 0

DAILY_GOALS_HOUR = 8
DAILY_GOALS_MINUTE = 5

DAILY_REWARD_HOUR = 8
DAILY_REWARD_MINUTE = 10

BIRTHDAY_HOUR = 8
BIRTHDAY_MINUTE = 15

NOTIFICATION_CHECK_INTERVAL = 5

DAILY_MAINTENANCE_HOUR = 0
DAILY_MAINTENANCE_MINUTE = 10

WEEKLY_MAINTENANCE_HOUR = 0
WEEKLY_MAINTENANCE_MINUTE = 30

AUTO_BACKUP_HOUR = 3
AUTO_BACKUP_MINUTE = 0

# Daily community moments (Asia/Kolkata)
AFTERNOON_WISH_HOUR = 13
AFTERNOON_WISH_MINUTE = 0
NIGHT_WISH_HOUR = 21
NIGHT_WISH_MINUTE = 0
DAILY_MYSTERY_HOUR = 20
DAILY_MYSTERY_MINUTE = 0


# ============================================================
# CURRENT DATETIME HELPER
# ============================================================

def datetime_now():
    """
    Returns current datetime using configured timezone
    when available.
    """

    try:
        if TIMEZONE is not None:
            return datetime.now(TIMEZONE)

    except Exception as error:
        print(
            "⚠️ Timezone error:",
            error,
        )

    return datetime.now()


# ============================================================
# SAFE DATABASE HELPERS
# ============================================================

def _get_users():
    """
    Safely retrieves registered active users.
    """

    try:

        return database.get_all_registered_users(
            active_only=True
        )

    except TypeError:

        try:

            return database.get_all_registered_users()

        except Exception as error:

            print(
                "❌ User registry error:",
                error,
            )

            return []

    except Exception as error:

        print(
            "❌ User registry error:",
            error,
        )

        return []


def _get_groups():
    """
    Safely retrieves registered active groups.
    """

    try:

        return database.get_all_registered_groups(
            active_only=True
        )

    except TypeError:

        try:

            return database.get_all_registered_groups()

        except Exception as error:

            print(
                "❌ Group registry error:",
                error,
            )

            return []

    except Exception as error:

        print(
            "❌ Group registry error:",
            error,
        )

        return []


# ============================================================
# SAFE SEND MESSAGE
# ============================================================

async def _send_message(
    context,
    chat_id,
    text,
):
    """
    Safely sends a Telegram message.

    Returns:
        True  -> message sent
        False -> message failed
    """

    try:

        await context.bot.send_message(
            chat_id=int(chat_id),
            text=text,
        )

        return True

    except Exception as error:

        print(
            f"❌ Message send error "
            f"({chat_id}):",
            error,
        )

        return False


# ============================================================
# MORNING WISH
# ============================================================

async def send_morning_wishes(
    context: ContextTypes.DEFAULT_TYPE,
):
    """Send a fresh morning wish to every active private user and group."""
    users = _get_users()
    groups = _get_groups()
    user_success = user_failed = group_success = group_failed = 0

    for user in users:
        try:
            user_id = user.get("user_id")
            if not user_id:
                continue
            try:
                text = morning_wishes.get_morning_wish_for_user(user_id)
            except Exception:
                text = morning_wishes.get_morning_wish()
            name = user.get("first_name") or user.get("name")
            if name:
                text = f"🌅 Good morning, {name}!\n\n" + text
            if await _send_message(context, user_id, text):
                user_success += 1
            else:
                user_failed += 1
                try:
                    database.deactivate_user(user_id)
                except Exception:
                    pass
        except Exception as error:
            user_failed += 1
            print("🌅 Morning wish user error:", error)

    for group in groups:
        try:
            chat_id = group.get("chat_id")
            if not chat_id:
                continue
            try:
                text = morning_wishes.get_morning_wish_for_chat(chat_id)
            except Exception:
                text = morning_wishes.get_morning_wish()
            text = "🌅 Good morning, everyone!\n\n" + text
            if await _send_message(context, chat_id, text):
                group_success += 1
            else:
                group_failed += 1
                try:
                    database.deactivate_group(chat_id)
                except Exception:
                    pass
        except Exception as error:
            group_failed += 1
            print("🌅 Morning wish group error:", error)

    print(
        "🌅 Morning wishes completed | "
        f"Users: {user_success} sent / {user_failed} failed | "
        f"Groups: {group_success} sent / {group_failed} failed"
    )


# ============================================================
# AFTERNOON + NIGHT WISHES
# ============================================================

AFTERNOON_WISHES = [
    "🌤️ Good afternoon! Thoda pause lo, saans lo, aur din ko gently continue karo. 💛",
    "☀️ Afternoon check-in: paani pi lo, shoulders relax karo, aur aaj ka din apne pace par chalao. 🌿",
    "🌼 Good afternoon! Jo ho gaya usse chhodo, jo baaki hai usse calmly handle karo. 💖",
]

NIGHT_WISHES = [
    "🌙 Good night! Aaj jitna ho saka, utna enough tha. Ab araam karo. 💜",
    "✨ Raat ka reminder: kal ek naya din hai. Aaj ke liye bas rest. 🌙",
    "🌌 Good night! Dil halka rakho, phone side rakho, aur sweet dreams. 💫",
]


def _daily_choice(items):
    if not items:
        return "🌸 Have a lovely day!"
    return items[datetime_now().timetuple().tm_yday % len(items)]


async def _send_fixed_wish(context, kind):
    users = _get_users()
    groups = _get_groups()
    if kind == "afternoon":
        default = _daily_choice(AFTERNOON_WISHES)
    else:
        default = _daily_choice(NIGHT_WISHES)

    for user in users:
        try:
            uid = user.get("user_id")
            if not uid:
                continue
            text = default
            try:
                if kind == "afternoon":
                    name = user.get("first_name") or user.get("name") or "Bloom"
                    text = f"🌤️ Good afternoon, {name}!\n\n" + default.split(" ", 2)[-1]
                else:
                    name = user.get("first_name") or user.get("name") or "Bloom"
                    text = f"🌙 Good night, {name}!\n\n" + default.split(" ", 2)[-1]
            except Exception:
                pass
            try:
                await context.bot.send_message(chat_id=int(uid), text=text)
            except Exception as error:
                print(f"⚠️ {kind} wish user {uid}: {error}")
        except Exception as error:
            print(f"⚠️ {kind} wish user error: {error}")

    for group in groups:
        try:
            gid = group.get("chat_id")
            if not gid:
                continue
            text = default
            if kind == "afternoon":
                text = "🌤️ Good afternoon, everyone!\n\n" + default.split(" ", 2)[-1]
            else:
                text = "🌙 Good night, everyone!\n\n" + default.split(" ", 2)[-1]
            try:
                await context.bot.send_message(chat_id=int(gid), text=text)
            except Exception as error:
                print(f"⚠️ {kind} wish group {gid}: {error}")
        except Exception as error:
            print(f"⚠️ {kind} wish group error: {error}")


async def send_afternoon_wishes(context: ContextTypes.DEFAULT_TYPE):
    await _send_fixed_wish(context, "afternoon")


async def send_night_wishes(context: ContextTypes.DEFAULT_TYPE):
    await _send_fixed_wish(context, "night")


# ============================================================
# DAILY MYSTERY — ONE CASE, EVERY ACTIVE PLACE
# ============================================================

async def send_daily_mystery(context: ContextTypes.DEFAULT_TYPE):
    """Posts one mystery case per day to every active private chat and group."""
    cases = getattr(mystery_engine, "MYSTERIES", [])
    if not cases:
        print("⚠️ Daily mystery skipped: no mystery cases available.")
        return

    now = datetime_now()
    index = (now.date().toordinal() - 1) % len(cases)
    mystery = cases[index]
    title = mystery.get("title", "Aaj Ka Mystery")
    clues = mystery.get("clues", [])
    clue_text = "\n".join(f"• {clue}" for clue in clues)
    text = (
        f"🕵️ Aaj Ka Mystery\n\n"
        f"🔎 {title}\n\n"
        f"{clue_text}\n\n"
        "🧠 Clues ko dhyaan se dekho… answer socho!\n"
        "👇 Case open karke solve karo."
    )

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🕵️ Solve Mystery", callback_data=f"mb_mystery|open|{index}")]
    ])

    sent_users = sent_groups = 0
    for user in _get_users():
        try:
            uid = user.get("user_id")
            if uid:
                await context.bot.send_message(chat_id=int(uid), text=text, reply_markup=markup)
                sent_users += 1
        except Exception as error:
            print(f"⚠️ Daily mystery user error: {error}")

    for group in _get_groups():
        try:
            gid = group.get("chat_id")
            if gid:
                await context.bot.send_message(chat_id=int(gid), text=text, reply_markup=markup)
                sent_groups += 1
        except Exception as error:
            print(f"⚠️ Daily mystery group error: {error}")

    print(f"🕵️ Daily mystery sent | case={index} | users={sent_users} | groups={sent_groups}")


def _remove_named_job(application, name):
    try:
        for job in application.job_queue.get_jobs_by_name(name):
            job.schedule_removal()
    except Exception:
        pass


def schedule_afternoon_wishes(application):
    _remove_named_job(application, AFTERNOON_WISH_JOB_NAME)
    application.job_queue.run_daily(
        send_afternoon_wishes,
        time=time(AFTERNOON_WISH_HOUR, AFTERNOON_WISH_MINUTE, tzinfo=TIMEZONE),
        name=AFTERNOON_WISH_JOB_NAME,
    )
    return True


def schedule_night_wishes(application):
    _remove_named_job(application, NIGHT_WISH_JOB_NAME)
    application.job_queue.run_daily(
        send_night_wishes,
        time=time(NIGHT_WISH_HOUR, NIGHT_WISH_MINUTE, tzinfo=TIMEZONE),
        name=NIGHT_WISH_JOB_NAME,
    )
    return True


def schedule_daily_mystery(application):
    _remove_named_job(application, DAILY_MYSTERY_JOB_NAME)
    application.job_queue.run_daily(
        send_daily_mystery,
        time=time(DAILY_MYSTERY_HOUR, DAILY_MYSTERY_MINUTE, tzinfo=TIMEZONE),
        name=DAILY_MYSTERY_JOB_NAME,
    )
    return True


# ============================================================
# DAILY GOALS NOTIFICATION
# ============================================================

async def send_daily_goals_notifications(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Sends Daily Goal reminders.

    Actual goal completion remains handled by goals.py.
    """

    users = _get_users()

    success = 0
    skipped = 0

    for user in users:

        try:

            user_id = user.get(
                "user_id"
            )

            if not user_id:
                continue

            # ------------------------------------------------
            # Notification permission
            # ------------------------------------------------

            try:

                allowed = (
                    notifications.can_send_notification(
                        user_id,
                        "daily_goals",
                    )
                )

                if not allowed.get("allowed"):

                    skipped += 1
                    continue

            except Exception:

                # Backward-safe behavior
                pass

            # ------------------------------------------------
            # Check today's goals
            # ------------------------------------------------

            try:

                goal_data = goals.get_daily_goals(
                    user_id
                )

            except Exception:

                goal_data = []

            if isinstance(goal_data, dict):

                goal_list = goal_data.get(
                    "goals",
                    [],
                )

            else:

                goal_list = goal_data or []

            incomplete = [
                goal
                for goal in goal_list
                if isinstance(goal, dict)
                and not goal.get(
                    "completed",
                    False,
                )
            ]

            if not incomplete:
                continue

            text = (
                "🎯 <b>MoodBloom Daily Goals</b>\n\n"
                "Good morning, Bloom! 🌸\n"
                "Aaj ke goals aapka wait kar rahe hain. ✨\n\n"
                f"📌 Remaining goals: {len(incomplete)}\n\n"
                "Small steps → big progress. 🌱"
            )

            sent = await _send_message(
                context,
                user_id,
                text,
            )

            if sent:

                success += 1

                try:

                    notifications.record_notification_sent(
                        user_id,
                        "daily_goals",
                    )

                except Exception:
                    pass

        except Exception as error:

            print(
                f"🎯 Daily goal notification error "
                f"({user.get('user_id')}):",
                error,
            )

    print(
        "🎯 Daily goal notifications completed | "
        f"Sent: {success} | Skipped: {skipped}"
    )


# ============================================================
# DAILY REWARD NOTIFICATION
# ============================================================

async def send_daily_reward_notifications(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Reminds users about their daily reward.
    """

    users = _get_users()

    success = 0
    skipped = 0

    for user in users:

        try:

            user_id = user.get(
                "user_id"
            )

            if not user_id:
                continue

            try:

                allowed = (
                    notifications.can_send_notification(
                        user_id,
                        "daily_reward",
                    )
                )

                if not allowed.get("allowed"):

                    skipped += 1
                    continue

            except Exception:
                pass

            try:

                already_claimed = (
                    rewards.has_claimed_today(
                        user_id
                    )
                )

            except Exception:

                already_claimed = False

            if already_claimed:
                continue

            text = (
                "🎁 <b>Daily Reward</b>\n\n"
                "Good morning, Bloom! 🌸\n"
                "Aaj ka Daily Reward ready hai! ✨\n\n"
                "Claim karke apna XP grow kijiye. ⭐"
            )

            sent = await _send_message(
                context,
                user_id,
                text,
            )

            if sent:

                success += 1

                try:

                    notifications.record_notification_sent(
                        user_id,
                        "daily_reward",
                    )

                except Exception:
                    pass

        except Exception as error:

            print(
                f"🎁 Daily reward notification error "
                f"({user.get('user_id')}):",
                error,
            )

    print(
        "🎁 Daily reward notifications completed | "
        f"Sent: {success} | Skipped: {skipped}"
    )


# ============================================================
# BIRTHDAY REMINDERS
# ============================================================

async def send_birthday_notifications(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Sends birthday reminders/wishes when birthdays.py
    reports a birthday for the current day.
    """

    users = _get_users()

    success = 0
    skipped = 0

    now = datetime_now()

    for user in users:

        try:

            user_id = user.get(
                "user_id"
            )

            if not user_id:
                continue

            # ------------------------------------------------
            # Notification permission
            # ------------------------------------------------

            try:

                allowed = (
                    notifications.can_send_notification(
                        user_id,
                        "birthday",
                    )
                )

                if not allowed.get("allowed"):

                    skipped += 1
                    continue

            except Exception:
                pass

            # ------------------------------------------------
            # Get birthday
            # ------------------------------------------------

            try:

                birthday = birthdays.get_birthday(
                    user_id
                )

            except Exception:

                birthday = None

            if not birthday:
                continue

            # ------------------------------------------------
            # Extract birthday date
            # ------------------------------------------------

            birthday_month = None
            birthday_day = None

            try:

                if isinstance(
                    birthday,
                    dict,
                ):

                    birthday_month = birthday.get(
                        "month"
                    )

                    birthday_day = birthday.get(
                        "day"
                    )

                elif isinstance(
                    birthday,
                    (list, tuple),
                ) and len(birthday) >= 2:

                    birthday_month = birthday[0]
                    birthday_day = birthday[1]

            except Exception:

                birthday_month = None
                birthday_day = None

            # ------------------------------------------------
            # Validate today's birthday
            # ------------------------------------------------

            try:

                is_today = (
                    birthday_month is not None
                    and birthday_day is not None
                    and int(birthday_month) == now.month
                    and int(birthday_day) == now.day
                )

            except Exception:

                is_today = False

            if not is_today:
                continue

            # ------------------------------------------------
            # Birthday message
            # ------------------------------------------------

            try:

                birthday_wish = (
                    morning_wishes
                    .get_birthday_morning_wish()
                )

            except Exception:

                birthday_wish = (
                    "Wishing you a beautiful birthday! 🌸"
                )

            text = (
                "🎂 <b>Happy Birthday from MoodBloom!</b> 🎉\n\n"
                f"{birthday_wish}\n\n"
                "🌸 May your day be full of happiness, "
                "peace and beautiful moments! ✨"
            )

            sent = await _send_message(
                context,
                user_id,
                text,
            )

            if sent:

                success += 1

                try:

                    notifications.record_notification_sent(
                        user_id,
                        "birthday",
                    )

                except Exception:
                    pass

        except Exception as error:

            print(
                f"🎂 Birthday notification error "
                f"({user.get('user_id')}):",
                error,
            )

    print(
        "🎂 Birthday notifications completed | "
        f"Sent: {success} | Skipped: {skipped}"
    )


# ============================================================
# CUSTOM NOTIFICATION CHECK
# ============================================================

async def process_custom_notifications(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Checks custom reminders from notifications.py.
    """

    users = _get_users()

    sent_count = 0

    for user in users:

        try:

            user_id = user.get(
                "user_id"
            )

            if not user_id:
                continue

            # ------------------------------------------------
            # Get due reminders
            # ------------------------------------------------

            try:

                due = (
                    notifications
                    .get_due_custom_reminders(
                        user_id
                    )
                )

            except TypeError:

                try:

                    due = (
                        notifications
                        .get_due_custom_reminders(
                            user_id,
                            datetime_now(),
                        )
                    )

                except Exception:

                    due = []

            except Exception:

                due = []

            if not due:
                continue

            # ------------------------------------------------
            # Process reminders
            # ------------------------------------------------

            for reminder in due:

                try:

                    if not isinstance(
                        reminder,
                        dict,
                    ):
                        continue

                    reminder_id = reminder.get(
                        "id"
                    )

                    message = reminder.get(
                        "message",
                        "⏰ MoodBloom reminder",
                    )

                    if not message:
                        message = "⏰ MoodBloom reminder"

                    sent = await _send_message(
                        context,
                        user_id,
                        (
                            "⏰ <b>MoodBloom Reminder</b>\n\n"
                            f"{message}"
                        ),
                    )

                    if sent:

                        sent_count += 1

                        if reminder_id is not None:

                            try:

                                (
                                    notifications
                                    .record_custom_reminder_sent(
                                        user_id,
                                        reminder_id,
                                    )
                                )

                            except Exception:
                                pass

                except Exception as error:

                    print(
                        "⏰ Custom reminder error:",
                        error,
                    )

        except Exception as error:

            print(
                "⏰ Custom notification user error:",
                error,
            )

    if sent_count:

        print(
            f"⏰ Custom notifications sent: "
            f"{sent_count}"
        )


# ============================================================
# NOTIFICATION PROCESSOR
# ============================================================

async def process_notifications(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Central notification processor.

    Runs frequently and delegates actual checks
    to individual systems.
    """

    try:

        await process_custom_notifications(
            context
        )

    except Exception as error:

        print(
            "🔔 Notification processor error:",
            error,
        )


# ============================================================
# DAILY MAINTENANCE
# ============================================================

async def daily_maintenance(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Daily maintenance for V4 systems.
    """

    print(
        "🧹 MoodBloom daily maintenance started..."
    )

    # --------------------------------------------------------
    # Notification cleanup
    # --------------------------------------------------------

    try:

        cleaned_users = 0

        for user in _get_users():

            user_id = user.get("user_id")

            if not user_id:
                continue

            try:
                notifications.cleanup_old_notification_data(
                    user_id
                )
                cleaned_users += 1

            except Exception:
                pass

        print(
            f"   ✅ Notification cleanup "
            f"({cleaned_users} users)"
        )

    except Exception as error:

        print(
            "   ⚠️ Notification cleanup error:",
            error,
        )

    # --------------------------------------------------------
    # Group analytics cleanup
    # --------------------------------------------------------

    try:

        group_analytics.cleanup_old_daily_data()

        print(
            "   ✅ Group analytics cleanup"
        )

    except Exception as error:

        print(
            "   ⚠️ Group analytics cleanup error:",
            error,
        )

    # --------------------------------------------------------
    # Birthday cleanup
    # --------------------------------------------------------

    try:

        birthdays.cleanup_birthday_history()

        print(
            "   ✅ Birthday cleanup"
        )

    except Exception as error:

        print(
            "   ⚠️ Birthday cleanup error:",
            error,
        )

    # --------------------------------------------------------
    # Backup directory cleanup
    # --------------------------------------------------------

    try:

        backup.cleanup_old_backups()

        print(
            "   ✅ Backup cleanup"
        )

    except Exception as error:

        print(
            "   ⚠️ Backup cleanup error:",
            error,
        )

    print(
        "🧹 MoodBloom daily maintenance completed."
    )


# ============================================================
# WEEKLY MAINTENANCE
# ============================================================

async def weekly_maintenance(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Weekly analytics/maintenance job.
    """

    print(
        "📊 MoodBloom weekly maintenance started..."
    )

    try:

        snapshot_count = 0

        for group in _get_groups():

            chat_id = group.get("chat_id")

            if not chat_id:
                continue

            try:
                group_analytics.create_snapshot(chat_id)
                snapshot_count += 1

            except Exception:
                pass

        print(
            f"   ✅ Group analytics snapshots created "
            f"({snapshot_count} groups)"
        )

    except Exception as error:

        print(
            "   ⚠️ Analytics snapshot error:",
            error,
        )

    print(
        "📊 MoodBloom weekly maintenance completed."
    )


# ============================================================
# AUTOMATIC BACKUP
# ============================================================

async def automatic_backup(
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Creates an automatic MoodBloom backup.
    """

    print(
        "💾 MoodBloom automatic backup started..."
    )

    try:

        result = backup.create_full_backup()

        if result:

            print(
                "💾 Automatic backup completed."
            )

        else:

            print(
                "⚠️ Automatic backup returned no result."
            )

    except Exception as error:

        print(
            "❌ Automatic backup error:",
            error,
        )


# ============================================================
# REMOVE JOB BY NAME
# ============================================================

def remove_job(
    application,
    job_name,
):
    """
    Safely removes jobs with the given name.
    """

    try:

        job_queue = application.job_queue

    except Exception:

        return

    if not job_queue:
        return

    try:

        jobs = job_queue.get_jobs_by_name(
            job_name
        )

        for job in jobs:

            job.schedule_removal()

    except Exception as error:

        print(
            f"Job removal error "
            f"({job_name}):",
            error,
        )


# ============================================================
# REMOVE MORNING WISH JOB
# ============================================================

def remove_morning_wish_job(
    application,
):

    remove_job(
        application,
        MORNING_WISH_JOB_NAME,
    )


# ============================================================
# SCHEDULE MORNING WISHES
# ============================================================

def schedule_morning_wishes(
    application,
):
    """
    Preserved compatibility function.

    Schedules:
        08:00 AM
    """

    try:

        job_queue = application.job_queue

    except Exception:

        job_queue = None

    if not job_queue:

        print(
            "⚠️ JobQueue unavailable. "
            "Morning wishes could not be scheduled."
        )

        print(
            "Install with:"
        )

        print(
            "pip install "
            "python-telegram-bot[job-queue]==22.8"
        )

        return False

    remove_morning_wish_job(
        application
    )

    try:

        job_queue.run_daily(
            send_morning_wishes,

            time=time(
                hour=MORNING_WISH_HOUR,
                minute=MORNING_WISH_MINUTE,
                tzinfo=TIMEZONE,
            ),

            name=MORNING_WISH_JOB_NAME,
        )

        print(
            "🌅 Morning Wish Scheduler enabled."
        )

        print(
            f"⏰ Daily time: "
            f"{MORNING_WISH_HOUR:02d}:"
            f"{MORNING_WISH_MINUTE:02d}"
        )

        return True

    except Exception as error:

        print(
            "❌ Morning wish scheduling error:",
            error,
        )

        return False


# ============================================================
# SCHEDULE DAILY GOALS
# ============================================================

def schedule_daily_goals(
    application,
):

    try:

        job_queue = application.job_queue

        if not job_queue:
            return False

        remove_job(
            application,
            DAILY_GOALS_JOB_NAME,
        )

        job_queue.run_daily(
            send_daily_goals_notifications,

            time=time(
                hour=DAILY_GOALS_HOUR,
                minute=DAILY_GOALS_MINUTE,
                tzinfo=TIMEZONE,
            ),

            name=DAILY_GOALS_JOB_NAME,
        )

        print(
            "🎯 Daily Goals Scheduler enabled."
        )

        return True

    except Exception as error:

        print(
            "❌ Daily goals scheduling error:",
            error,
        )

        return False


# ============================================================
# SCHEDULE DAILY REWARD
# ============================================================

def schedule_daily_reward(
    application,
):

    try:

        job_queue = application.job_queue

        if not job_queue:
            return False

        remove_job(
            application,
            DAILY_REWARD_JOB_NAME,
        )

        job_queue.run_daily(
            send_daily_reward_notifications,

            time=time(
                hour=DAILY_REWARD_HOUR,
                minute=DAILY_REWARD_MINUTE,
                tzinfo=TIMEZONE,
            ),

            name=DAILY_REWARD_JOB_NAME,
        )

        print(
            "🎁 Daily Reward Scheduler enabled."
        )

        return True

    except Exception as error:

        print(
            "❌ Daily reward scheduling error:",
            error,
        )

        return False


# ============================================================
# SCHEDULE BIRTHDAYS
# ============================================================

def schedule_birthdays(
    application,
):

    try:

        job_queue = application.job_queue

        if not job_queue:
            return False

        remove_job(
            application,
            BIRTHDAY_JOB_NAME,
        )

        job_queue.run_daily(
            send_birthday_notifications,

            time=time(
                hour=BIRTHDAY_HOUR,
                minute=BIRTHDAY_MINUTE,
                tzinfo=TIMEZONE,
            ),

            name=BIRTHDAY_JOB_NAME,
        )

        print(
            "🎂 Birthday Scheduler enabled."
        )

        return True

    except Exception as error:

        print(
            "❌ Birthday scheduling error:",
            error,
        )

        return False


# ============================================================
# SCHEDULE NOTIFICATIONS
# ============================================================

def schedule_notifications(
    application,
):

    try:

        job_queue = application.job_queue

        if not job_queue:
            return False

        remove_job(
            application,
            NOTIFICATION_JOB_NAME,
        )

        job_queue.run_repeating(
            process_notifications,

            interval=NOTIFICATION_CHECK_INTERVAL * 60,

            first=10,

            name=NOTIFICATION_JOB_NAME,
        )

        print(
            "🔔 Notification Scheduler enabled."
        )

        print(
            f"⏱️ Check interval: "
            f"{NOTIFICATION_CHECK_INTERVAL} minutes"
        )

        return True

    except Exception as error:

        print(
            "❌ Notification scheduling error:",
            error,
        )

        return False


# ============================================================
# SCHEDULE DAILY MAINTENANCE
# ============================================================

def schedule_daily_maintenance(
    application,
):

    try:

        job_queue = application.job_queue

        if not job_queue:
            return False

        remove_job(
            application,
            DAILY_MAINTENANCE_JOB_NAME,
        )

        job_queue.run_daily(
            daily_maintenance,

            time=time(
                hour=DAILY_MAINTENANCE_HOUR,
                minute=DAILY_MAINTENANCE_MINUTE,
                tzinfo=TIMEZONE,
            ),

            name=DAILY_MAINTENANCE_JOB_NAME,
        )

        print(
            "🧹 Daily maintenance scheduler enabled."
        )

        return True

    except Exception as error:

        print(
            "❌ Daily maintenance scheduling error:",
            error,
        )

        return False


# ============================================================
# SCHEDULE WEEKLY MAINTENANCE
# ============================================================

def schedule_weekly_maintenance(
    application,
):

    try:

        job_queue = application.job_queue

        if not job_queue:
            return False

        remove_job(
            application,
            WEEKLY_MAINTENANCE_JOB_NAME,
        )

        # Sunday = 6
        job_queue.run_daily(
            weekly_maintenance,

            time=time(
                hour=WEEKLY_MAINTENANCE_HOUR,
                minute=WEEKLY_MAINTENANCE_MINUTE,
                tzinfo=TIMEZONE,
            ),

            days=(6,),

            name=WEEKLY_MAINTENANCE_JOB_NAME,
        )

        print(
            "📊 Weekly maintenance scheduler enabled."
        )

        return True

    except Exception as error:

        print(
            "❌ Weekly maintenance scheduling error:",
            error,
        )

        return False


# ============================================================
# SCHEDULE AUTO BACKUP
# ============================================================

def schedule_auto_backup(
    application,
):

    try:

        job_queue = application.job_queue

        if not job_queue:
            return False

        remove_job(
            application,
            AUTO_BACKUP_JOB_NAME,
        )

        job_queue.run_daily(
            automatic_backup,

            time=time(
                hour=AUTO_BACKUP_HOUR,
                minute=AUTO_BACKUP_MINUTE,
                tzinfo=TIMEZONE,
            ),

            name=AUTO_BACKUP_JOB_NAME,
        )

        print(
            "💾 Automatic Backup Scheduler enabled."
        )

        return True

    except Exception as error:

        print(
            "❌ Backup scheduling error:",
            error,
        )

        return False


# ============================================================
# MASTER SCHEDULER
# ============================================================

def setup_scheduler(
    application,
):
    """
    Registers all MoodBloom 4.0 scheduled jobs.

    bot.py should call this ONCE after the Application
    has been created.
    """

    try:

        job_queue = application.job_queue

    except Exception:

        job_queue = None

    if not job_queue:

        print(
            "❌ MoodBloom Scheduler unavailable."
        )

        print(
            "Install:"
        )

        print(
            "pip install "
            "python-telegram-bot[job-queue]==22.8"
        )

        return False

    results = {}

    # --------------------------------------------------------
    # Morning
    # --------------------------------------------------------

    results["morning"] = schedule_morning_wishes(
        application
    )

    results["afternoon"] = schedule_afternoon_wishes(application)
    results["night"] = schedule_night_wishes(application)
    results["daily_mystery"] = schedule_daily_mystery(application)

    results["goals"] = schedule_daily_goals(
        application
    )

    results["reward"] = schedule_daily_reward(
        application
    )

    results["birthday"] = schedule_birthdays(
        application
    )

    # --------------------------------------------------------
    # Repeating notifications
    # --------------------------------------------------------

    results["notifications"] = schedule_notifications(
        application
    )

    # --------------------------------------------------------
    # Maintenance
    # --------------------------------------------------------

    results["daily_maintenance"] = (
        schedule_daily_maintenance(
            application
        )
    )

    results["weekly_maintenance"] = (
        schedule_weekly_maintenance(
            application
        )
    )

    # --------------------------------------------------------
    # Backup
    # --------------------------------------------------------

    results["backup"] = schedule_auto_backup(
        application
    )

    successful = sum(
        1
        for result in results.values()
        if result
    )

    total = len(results)

    print(
        "================================================"
    )

    print(
        "🌸 MOODBLOOM 4.0 SCHEDULER"
    )

    print(
        f"✅ Enabled: {successful}/{total}"
    )

    for name, status in results.items():

        icon = "✅" if status else "❌"

        print(
            f"{icon} {name}"
        )

    print(
        "================================================"
    )

    return successful == total


# ============================================================
# SCHEDULER STATUS
# ============================================================

def get_scheduler_status(
    application,
):

    try:

        job_queue = application.job_queue

        if not job_queue:

            return {
                "available": False,
                "jobs": [],
                "count": 0,
            }

        jobs = job_queue.jobs()

        job_info = []

        for job in jobs:

            try:

                next_run = (
                    job.next_t
                    if hasattr(job, "next_t")
                    else ""
                )

            except Exception:

                next_run = ""

            job_info.append({
                "name": job.name,
                "next_run": str(
                    next_run
                ),
            })

        return {
            "available": True,
            "jobs": job_info,
            "count": len(job_info),
        }

    except Exception as error:

        return {
            "available": False,
            "jobs": [],
            "count": 0,
            "error": str(error),
        }


# ============================================================
# FORMAT SCHEDULER STATUS
# ============================================================

def format_scheduler_status(
    application,
):

    status = get_scheduler_status(
        application
    )

    if not status.get("available"):

        return (
            "⚠️ <b>Scheduler Status</b>\n\n"
            "❌ JobQueue unavailable."
        )

    jobs = status.get(
        "jobs",
        [],
    )

    if not jobs:

        return (
            "⚠️ <b>Scheduler Status</b>\n\n"
            "No scheduled jobs found."
        )

    lines = [
        "🌸 <b>MoodBloom Scheduler</b>",
        "",
        f"📊 Active Jobs: {len(jobs)}",
        "",
    ]

    for job in jobs:

        name = job.get(
            "name",
            "Unknown",
        )

        next_run = job.get(
            "next_run",
            "Unknown",
        )

        lines.append(
            f"• {name}"
        )

        if next_run:

            lines.append(
                f"  ⏰ {next_run}"
            )

    return "\n".join(
        lines
    )


# ============================================================
# MANUAL TEST FUNCTIONS
# ============================================================

async def test_morning_wish(
    context: ContextTypes.DEFAULT_TYPE,
):

    await send_morning_wishes(
        context
    )


async def test_daily_goals(
    context: ContextTypes.DEFAULT_TYPE,
):

    await send_daily_goals_notifications(
        context
    )


async def test_daily_reward(
    context: ContextTypes.DEFAULT_TYPE,
):

    await send_daily_reward_notifications(
        context
    )


async def test_birthdays(
    context: ContextTypes.DEFAULT_TYPE,
):

    await send_birthday_notifications(
        context
    )


async def test_notifications(
    context: ContextTypes.DEFAULT_TYPE,
):

    await process_notifications(
        context
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    # Main jobs
    "send_morning_wishes",
    "send_daily_goals_notifications",
    "send_daily_reward_notifications",
    "send_birthday_notifications",
    "process_notifications",
    "process_custom_notifications",
    "daily_maintenance",
    "weekly_maintenance",
    "automatic_backup",

    # Individual scheduling
    "schedule_morning_wishes",
    "schedule_afternoon_wishes",
    "schedule_night_wishes",
    "schedule_daily_mystery",
    "schedule_daily_goals",
    "schedule_daily_reward",
    "schedule_birthdays",
    "schedule_notifications",
    "schedule_daily_maintenance",
    "schedule_weekly_maintenance",
    "schedule_auto_backup",

    # Master scheduler
    "setup_scheduler",

    # Compatibility
    "remove_morning_wish_job",
    "remove_job",

    # Status
    "get_scheduler_status",
    "format_scheduler_status",

    # Testing
    "test_morning_wish",
    "test_daily_goals",
    "test_daily_reward",
    "test_birthdays",
    "test_notifications",
]