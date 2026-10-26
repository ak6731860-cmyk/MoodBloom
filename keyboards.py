from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ============================================================
# MOODBLOOM 4.1 — KEYBOARD SYSTEM
# ============================================================
# Goals:
#   • Short UI
#   • Cute wording
#   • No dead buttons
#   • Minimum clicks
#   • Group features first-class
#   • Admin tools separate
#   • Existing working callback_data preserved
# ============================================================


# ============================================================
# COMMON HELPERS
# ============================================================

def button(text, callback_data):
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data
    )


def row(*items):
    return list(items)


def markup(keyboard):
    return InlineKeyboardMarkup(keyboard)


# ============================================================
# PERSONAL HOME
# ============================================================

def start_keyboard():
    return markup([
        [button("😊 Mood", "menu_mood"), button("🌤️ Today", "menu_today")],
        [button("📋 Menu", "home")],
    ])


def home_keyboard():
    """Compact personal dashboard: one clear home for each core feature."""
    return markup([
        [button("💗 Check in", "menu_mood"), button("🌤️ Today", "menu_today")],
        [button("🌸 Bloom Journey", "v4_bloom"), button("👤 My Profile", "menu_profile")],
        [button("📊 My Charts", "menu_chart"), button("🧠 Insights", "menu_insights")],
        [button("🔥 Streak", "menu_streak"), button("🎂 Birthday", "v4_birthdays")],
        [button("⏰ Reminder Studio", "menu_reminder"), button("⚙️ Settings", "menu_settings")],
        [button("👥 Group Edition", "menu_group"), button("❓ Help Center", "menu_help")],
    ])

# ============================================================
# BLOOM DASHBOARD
# ============================================================

def bloom_dashboard_keyboard():
    return markup([
        [button("🎯 Goals", "v4_goals"), button("🎁 Reward", "v4_reward")],
        [button("⭐ XP", "v4_xp"), button("🌱 Journey", "v4_journey")],
        [button("📚 Study", "v4_study"), button("🔔 Notifications", "v4_notifications")],
        [button("📖 Stories", "mb_story|start"), button("🕵️ Mystery", "mb_mystery|start")],
        [button("🏠 Home", "home")],
    ])


def v4_dashboard_keyboard():
    return bloom_dashboard_keyboard()


# ============================================================
# MOOD
# ============================================================

def mood_keyboard():
    return markup([
        [
            button("😊 Happy", "mood_happy"),
            button("😔 Sad", "mood_sad"),
        ],
        [
            button("😡 Angry", "mood_angry"),
            button("😴 Tired", "mood_tired"),
        ],
        [
            button("❤️ Loved", "mood_loved"),
            button("😐 Okay", "mood_okay"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


def mood_result_keyboard():
    return markup([
        [
            button("💭 Again", "menu_mood"),
            button("📊 Stats", "menu_stats"),
        ],
        [
            button("🧠 Insights", "menu_insights"),
        ],
        [
            button("🎯 Goals", "v4_goals"),
            button("⭐ XP", "v4_xp"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# NAVIGATION
# ============================================================

def back_keyboard():
    return markup([
        [
            button("🏠 Home", "home")
        ]
    ])


def back_mood_keyboard():
    return markup([
        [
            button("😊 Mood", "menu_mood")
        ],
        [
            button("🏠 Home", "home")
        ],
    ])


def home_back_keyboard():
    return markup([
        [
            button("🏠 Home", "home")
        ]
    ])


def bloom_back_keyboard():
    return markup([
        [
            button("🌸 Bloom", "v4_bloom")
        ],
        [
            button("🏠 Home", "home")
        ],
    ])


def group_back_keyboard():
    return markup([
        [
            button("👥 Group", "menu_group")
        ],
        [
            button("🏠 Home", "home")
        ],
    ])


def simple_home_keyboard():
    return markup([
        [
            button("🏠 Home", "home")
        ]
    ])


def group_home_keyboard():
    return markup([
        [
            button("👥 Group", "menu_group")
        ]
    ])


# ============================================================
# DAILY
# ============================================================

def daily_keyboard():
    return markup([
        [
            button("😊 Mood", "menu_mood"),
            button("🎯 Goals", "v4_goals"),
        ],
        [
            button("🎁 Reward", "v4_reward"),
            button("🔥 Streak", "menu_streak"),
        ],
        [
            button("✨ Quote", "menu_quote"),
            button("🔥 Motivate", "menu_motivate"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


def daily_complete_keyboard():
    return markup([
        [
            button("🎁 Reward", "v4_reward"),
            button("⭐ XP", "v4_xp"),
        ],
        [
            button("🔥 Streak", "menu_streak"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# REMINDERS
# ============================================================

def reminder_keyboard():
    return markup([
        [
            button("🌅 8 AM", "remind_8"),
            button("☀️ 12 PM", "remind_12"),
        ],
        [
            button("🌆 6 PM", "remind_18"),
            button("🌙 9 PM", "remind_21"),
        ],
        [
            button("✏️ Custom", "remind_custom"),
        ],
        [
            button("🔕 Disable daily", "remind_cancel"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# NOTIFICATIONS
# ============================================================

def notification_keyboard():
    return markup([
        [
            button("🌅 Morning", "notif_toggle_morning"),
            button("💭 Mood check", "notif_toggle_mood_check"),
        ],
        [
            button("🎯 Goals", "notif_toggle_daily_goals"),
            button("🎁 Reward", "notif_toggle_daily_reward"),
        ],
        [
            button("🎂 Birthday", "notif_toggle_birthday"),
        ],
        [
            button("🌙 Quiet hours", "notif_quiet_menu"),
            button("📝 Custom reminders", "notif_reminders"),
        ],
        [
            button("📊 Notification stats", "notif_stats"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


def notifications_keyboard():
    return notification_keyboard()


# ============================================================
# HISTORY
# ============================================================

def history_keyboard():
    return markup([
        [
            button("📅 Today", "menu_today"),
            button("📅 Weekly", "menu_weekly"),
        ],
        [
            button("📈 Chart", "menu_chart"),
            button("📊 Weekly Chart", "menu_weekly_chart"),
        ],
        [
            button("🧠 Insights", "menu_insights"),
        ],
        [
            button("🗑️ Clear", "menu_clear"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# STATS
# ============================================================

def stats_keyboard():
    return markup([
        [
            button("📈 Chart", "menu_chart"),
            button("📊 Weekly", "menu_weekly_chart"),
        ],
        [
            button("🧠 Insights", "menu_insights"),
            button("🔮 Forecast", "menu_forecast"),
        ],
        [
            button("🏆 Achievements", "menu_achievements"),
        ],
        [
            button("🔥 Streak", "menu_streak"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# ANALYTICS
# ============================================================

def analytics_keyboard():
    return markup([
        [
            button("📊 Overview", "analytics_overview"),
            button("📈 Trends", "analytics_trends"),
        ],
        [
            button("😊 Mood", "analytics_mood"),
            button("🔥 Activity", "analytics_activity"),
        ],
        [
            button("📅 Weekly", "analytics_weekly"),
            button("📆 Monthly", "analytics_monthly"),
        ],
        [
            button("🧠 Insights", "menu_insights"),
            button("🔮 Forecast", "menu_forecast"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


def advanced_analytics_keyboard():
    return analytics_keyboard()


# ============================================================
# FORECAST
# ============================================================

def forecast_keyboard():
    return markup([
        [
            button("🧠 Insights", "menu_insights"),
            button("📊 Stats", "menu_stats"),
        ],
        [
            button("📈 Chart", "menu_chart"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# PROFILE
# ============================================================

def profile_keyboard():
    return markup([
        [
            button("🔥 Streak", "menu_streak"),
            button("🏆 Achievements", "menu_achievements"),
        ],
        [
            button("📊 Stats", "menu_stats"),
            button("⭐ XP", "v4_xp"),
        ],
        [
            button("🌱 Journey", "v4_journey"),
        ],
        [
            button("🎂 Birthday", "v4_birthdays"),
        ],
        [
            button("⚙️ Settings", "menu_settings"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


def account_keyboard():
    return markup([
        [
            button("👤 Profile", "menu_profile"),
        ],
        [
            button("⭐ XP", "v4_xp"),
            button("🏆 Achievements", "menu_achievements"),
        ],
        [
            button("🔥 Streak", "menu_streak"),
            button("📊 Stats", "menu_stats"),
        ],
        [
            button("🌱 Journey", "v4_journey"),
        ],
        [
            button("⚙️ Settings", "menu_settings"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# STREAK
# ============================================================

def streak_keyboard():
    return markup([
        [
            button("📊 Stats", "menu_stats"),
            button("📜 History", "menu_history"),
        ],
        [
            button("🏆 Achievements", "menu_achievements"),
        ],
        [
            button("🎯 Goals", "v4_goals"),
            button("⭐ XP", "v4_xp"),
        ],
        [
            button("🌱 Journey", "v4_journey"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# ACHIEVEMENTS
# ============================================================

def achievements_keyboard():
    return markup([
        [
            button("⭐ XP", "v4_xp"),
            button("🔥 Streak", "menu_streak"),
        ],
        [
            button("🌱 Journey", "v4_journey"),
        ],
        [
            button("📊 Stats", "menu_stats"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# GOALS
# ============================================================

def goals_keyboard(goals):
    buttons = []

    for goal in goals:
        goal_id = goal.get("id", "")
        title = goal.get("title", "Goal")
        icon = goal.get("icon", "🎯")
        completed = goal.get("completed", False)

        if completed:
            buttons.append([
                button(
                    f"✅ {title}",
                    f"v4_goal_done_{goal_id}"
                )
            ])
        else:
            buttons.append([
                button(
                    f"{icon} {title}",
                    f"v4_goal_{goal_id}"
                )
            ])

    buttons.append([
        button("🎁 Reward", "v4_reward"),
        button("⭐ XP", "v4_xp"),
    ])

    buttons.append([
        button("🏠 Bloom", "v4_bloom")
    ])

    return markup(buttons)


def goals_action_keyboard():
    return markup([
        [
            button("🎯 Goals", "v4_goals"),
        ],
        [
            button("📊 Goal Stats", "v4_goal_stats"),
            button("🔥 Goal Streak", "v4_goal_streak"),
        ],
        [
            button("📜 Goal History", "v4_goal_history"),
        ],
        [
            button("🎁 Reward", "v4_reward"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


def goal_result_keyboard():
    return markup([
        [
            button("🎯 More Goals", "v4_goals"),
            button("🎁 Reward", "v4_reward"),
        ],
        [
            button("⭐ XP", "v4_xp"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


# ============================================================
# REWARD
# ============================================================

def reward_keyboard(claimed=False):
    if claimed:
        return markup([
            [
                button("⭐ XP", "v4_xp"),
                button("🎯 Goals", "v4_goals"),
            ],
            [
                button("🌸 Bloom", "v4_bloom"),
            ],
        ])

    return markup([
        [
            button("🎁 CLAIM", "v4_claim_reward"),
        ],
        [
            button("🎯 Goals", "v4_goals"),
            button("⭐ XP", "v4_xp"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


def reward_stats_keyboard():
    return markup([
        [
            button("🎁 Reward", "v4_reward"),
        ],
        [
            button("📜 History", "v4_reward_history"),
            button("🔥 Streak", "v4_reward_streak"),
        ],
        [
            button("⭐ XP", "v4_xp"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


def reward_confirmation_keyboard():
    return markup([
        [
            button("🎁 Claim", "v4_claim_reward"),
            button("❌ Cancel", "v4_reward"),
        ],
    ])


# ============================================================
# XP
# ============================================================

def xp_keyboard():
    return markup([
        [
            button("🎯 Goals", "v4_goals"),
            button("🎁 Reward", "v4_reward"),
        ],
        [
            button("⭐ XP Progress", "v4_xp_history"),
        ],
        [
            button("🏆 Achievements", "menu_achievements"),
        ],
        [
            button("🌱 Journey", "v4_journey"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


def xp_history_keyboard():
    return markup([
        [
            button("⭐ XP", "v4_xp"),
        ],
        [
            button("🎯 Goals", "v4_goals"),
            button("🎁 Reward", "v4_reward"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


# ============================================================
# JOURNEY
# ============================================================

def journey_keyboard():
    return markup([
        [
            button("⭐ XP", "v4_xp"),
            button("🎯 Goals", "v4_goals"),
        ],
        [
            button("🔥 Streak", "menu_streak"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


def bloom_journey_keyboard():
    return journey_keyboard()


# ============================================================
# BIRTHDAYS
# ============================================================

def birthday_keyboard():
    return markup([
        [
            button("🎂 My Birthday", "birthday_my"),
        ],
        [
            button("➕ Add", "birthday_add"),
            button("✏️ Update", "birthday_update"),
        ],
        [
            button("🗑️ Remove", "birthday_remove"),
        ],
        [
            button("📅 Upcoming", "birthday_upcoming"),
            button("🎉 Today", "birthday_today"),
        ],
        [
            button("👥 Group", "birthday_group"),
        ],
        [
            button("🔔 Reminders", "birthday_reminders"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


def birthdays_keyboard():
    return birthday_keyboard()


def birthday_manage_keyboard():
    return markup([
        [
            button("➕ Add", "birthday_add"),
            button("✏️ Update", "birthday_update"),
        ],
        [
            button("🗑️ Remove", "birthday_remove"),
        ],
        [
            button("📅 Upcoming", "birthday_upcoming"),
            button("🎉 Today", "birthday_today"),
        ],
        [
            button("🔙 Birthdays", "v4_birthdays"),
        ],
    ])


# ============================================================
# STUDY MODE
# ============================================================

def study_keyboard(active=False):
    if active:
        return markup([
            [
                button("✅ Complete", "study_complete"),
            ],
            [
                button("🛑 Cancel", "study_cancel"),
            ],
            [
                button("🌸 Bloom", "v4_bloom"),
            ],
        ])

    return markup([
        [button("📚 25 min", "study_start_25"), button("⏱️ 45 min", "study_start_45")],
        [button("⏳ 60 min", "study_start_60"), button("✏️ Custom", "study_custom")],
        [button("🌸 Bloom", "v4_bloom")],
    ])


# ============================================================
# NOTIFICATION SETTINGS
# ============================================================

def notification_settings_keyboard(settings):
    """Premium notification controls; Reminder Studio is the single reminder hub."""
    def toggle_label(label, key):
        state = "🟢 ON" if settings.get(key, True) else "⚪ OFF"
        return f"{label}: {state}"

    quiet = settings.get("quiet_hours", {}) or {}
    quiet_state = "🔕 ON" if quiet.get("enabled") else "🔔 OFF"
    global_state = "🟢 ON" if settings.get("enabled", True) else "⚪ OFF"

    return markup([
        [button(f"🔔 All notifications: {global_state}", "notif_toggle_enabled")],
        [button(toggle_label("🌅 Morning", "morning"), "notif_toggle_morning"),
         button(toggle_label("💭 Mood check", "mood_check"), "notif_toggle_mood_check")],
        [button(toggle_label("🎯 Daily goals", "daily_goals"), "notif_toggle_daily_goals"),
         button(toggle_label("🎁 Daily reward", "daily_reward"), "notif_toggle_daily_reward")],
        [button(toggle_label("🎂 Birthday", "birthday"), "notif_toggle_birthday"),
         button(toggle_label("📚 Study", "study"), "notif_toggle_study")],
        [button(f"🌙 Quiet hours: {quiet_state}", "notif_quiet_menu")],
        [button("⏰ Open Reminder Studio", "menu_reminder"), button("📊 Notification stats", "notif_stats")],
        [button("🌸 Bloom Home", "v4_bloom")],
    ])

def quiet_hours_keyboard(settings):
    quiet = settings.get("quiet_hours", {}) or {}
    state = "🔕 ON" if quiet.get("enabled") else "🔔 OFF"

    return markup([
        [
            button(
                f"Toggle: {state}",
                "notif_quiet_toggle",
            ),
        ],
        [
            button("✏️ Set Range", "notif_quiet_set"),
        ],
        [
            button("⬅️ Back", "v4_notifications"),
        ],
    ])


def custom_reminders_keyboard(reminders):
    rows = []

    for reminder in reminders[:10]:
        state = "🟢" if reminder.get("enabled", True) else "🔴"
        rows.append([
            button(
                f"{state} {reminder.get('title', '?')} "
                f"({reminder.get('time', '')})",
                f"notif_rem_view_{reminder.get('id')}",
            ),
        ])

    rows.append([
        button("➕ Add Reminder", "notif_rem_add"),
    ])

    rows.append([
        button("⬅️ Back", "v4_notifications"),
    ])

    return markup(rows)


def custom_reminder_view_keyboard(reminder_id):
    return markup([
        [
            button("🗑️ Delete", f"notif_rem_del_{reminder_id}"),
        ],
        [
            button("⬅️ Back", "notif_reminders"),
        ],
    ])


# ============================================================
# GROUP DASHBOARD
# ============================================================

def group_keyboard():
    """Group-only dashboard with a clear split between activity and admin tools."""
    return markup([
        [button("😊 Group Mood", "group_mood"), button("📊 Group Report", "group_report")],
        [button("📈 Group Chart", "group_chart"), button("🏆 Leaderboard", "group_leaderboard")],
        [button("🔥 Group Streak", "group_streak"), button("🎮 Games", "group_games")],
        [button("💬 Daily Question", "group_question"), button("📖 Stories", "mb_story|start")],
        [button("🕵️ Mystery", "mb_mystery|start"), button("📈 Activity", "group_activity")],
        [button("⏰ Group Reminder Studio", "rem2|menu|group")],
        [button("🛡️ Admin Tools", "group_admin"), button("👋 Welcome", "group_welcome")],
        [button("❓ Group Help", "group_help"), button("🏠 Personal Home", "home")],
    ])

# ============================================================
# GROUP MOOD
# ============================================================

def group_mood_keyboard():
    return markup([
        [
            button("😊 Happy", "group_mood_happy"),
            button("😐 Okay", "group_mood_okay"),
        ],
        [
            button("😔 Sad", "group_mood_sad"),
            button("😴 Tired", "group_mood_tired"),
        ],
        [
            button("😡 Angry", "group_mood_angry"),
            button("❤️ Loved", "group_mood_loved"),
        ],
        [
            button("📊 Report", "group_report"),
        ],
        [
            button("👥 Group", "menu_group"),
        ],
    ])


# ============================================================
# GROUP REPORT
# ============================================================

def group_report_keyboard():
    return markup([
        [
            button("📈 Chart", "group_chart"),
            button("🏆 Rank", "group_leaderboard"),
        ],
        [
            button("🔥 Streak", "group_streak"),
        ],
        [
            button("😊 Mood", "group_mood"),
        ],
        [
            button("🎮 Fun", "group_games"),
        ],
        [
            button("🏠 Group", "menu_group"),
    ]])


# ============================================================
# GROUP ANALYTICS
# ============================================================

def group_analytics_keyboard():
    return markup([
        [
            button("📈 Activity", "group_activity"),
            button("👤 My Stats", "group_activity_me"),
        ],
        [
            button("📊 Overview", "group_report"),
            button("🏆 Top", "group_leaderboard"),
        ],
        [
            button("📈 Chart", "group_chart"),
            button("🔥 Streak", "group_streak"),
        ],
        [
            button("😊 Mood", "group_mood"),
        ],
        [
            button("🏠 Group", "menu_group"),
        ],
    ])


# ============================================================
# GROUP GAMES
# ============================================================

def group_games_keyboard():
    return markup([
        [
            button("🎲 Random", "group_game_random"),
        ],
        [
            button("🤔 WYR", "group_game_wyr"),
        ],
        [
            button("💬 Question", "group_question"),
        ],
        [
            button("🏆 Rank", "group_leaderboard"),
        ],
        [
            button("👥 Group", "menu_group"),
        ],
    ])


# ============================================================
# GROUP ADMIN
# ============================================================

def group_admin_keyboard():
    return markup([
        [
            button("👋 Welcome", "group_welcome"),
            button("🛡️ Moderation", "group_moderation"),
        ],
        [
            button("⏰ Reminder Studio", "rem2|menu|group"),
        ],
        [
            button("📢 Announcement", "group_announcement"),
        ],
        [
            button("⚙️ Settings", "group_settings"),
        ],
        [
            button("📊 Analytics", "group_report"),
        ],
        [
            button("👥 Group", "menu_group"),
        ],
    ])


# ============================================================
# GROUP WELCOME
# ============================================================

def group_welcome_keyboard():
    return markup([
        [
            button("✅ Enable", "welcome_enable"),
            button("❌ Disable", "welcome_disable"),
        ],
        [
            button("📝 Preview", "welcome_preview"),
        ],
        [
            button("🛡️ Admin", "group_admin"),
        ],
        [
            button("👥 Group", "menu_group"),
        ],
    ])


# ============================================================
# GROUP REMINDER
# ============================================================

def group_reminder_keyboard():
    return markup([
        [
            button("➕ New group reminder", "rem2|new|group"),
        ],
        [
            button("📨 Send to a person", "rem2|new|person_group"),
        ],
        [
            button("📋 Saved reminders", "rem2|list|group"),
        ],
        [
            button("🛡️ Admin", "group_admin"),
            button("👥 Group", "menu_group"),
        ],
    ])


# ============================================================
# LEADERBOARD
# ============================================================

def leaderboard_keyboard():
    return markup([
        [
            button("📊 Report", "group_report"),
            button("🔥 Streak", "group_streak"),
        ],
        [
            button("😊 Mood", "group_mood"),
        ],
        [
            button("🎮 Fun", "group_games"),
        ],
        [
            button("👥 Group", "menu_group"),
        ],
    ])


# ============================================================
# DAILY QUESTION
# ============================================================

def daily_question_keyboard():
    return markup([
        [
            button("💬 Answer", "group_question_answer"),
            button("🔄 Another", "group_question"),
        ],
        [
            button("🎮 Fun", "group_games"),
            button("🏆 Rank", "group_leaderboard"),
        ],
        [
            button("👥 Group", "menu_group"),
        ],
    ])


# ============================================================
# GROUP STREAK
# ============================================================

def group_streak_keyboard():
    return markup([
        [
            button("📊 Report", "group_report"),
            button("🏆 Rank", "group_leaderboard"),
        ],
        [
            button("😊 Mood", "group_mood"),
        ],
        [
            button("🎮 Fun", "group_games"),
        ],
        [
            button("👥 Group", "menu_group"),
        ],
    ])


# ============================================================
# SETTINGS
# ============================================================

def settings_keyboard():
    return markup([
        [button("🔔 Notifications", "v4_notifications"), button("⏰ Reminder Studio", "menu_reminder")],
        [button("🎂 Birthday", "v4_birthdays"), button("🎯 Daily Goals", "v4_goals")],
        [button("🌐 Timezone (IST)", "settings_timezone")],
        [button("🧹 Clear Mood History", "settings_reset")],
        [button("🏠 Back to Home", "home")],
    ])

# ============================================================
# V4 SETTINGS
# ============================================================

def v4_settings_keyboard():
    return markup([
        [
            button("🔔 Notifications", "v4_notifications"),
        ],
        [
            button("🎯 Goals", "v4_goal_settings"),
        ],
        [
            button("🎁 Reward", "v4_reward_settings"),
        ],
        [
            button("🎂 Birthday", "v4_birthday_settings"),
        ],
        [
            button("📊 Analytics", "v4_analytics_settings"),
        ],
        [
            button("⚙️ General", "menu_settings"),
        ],
        [
            button("🌸 Bloom", "v4_bloom"),
        ],
    ])


# ============================================================
# HELP
# ============================================================

def help_keyboard():
    return markup([
        [
            button("💭 Mood", "help_mood"),
            button("🎯 Goals", "help_goals"),
        ],
        [
            button("🎁 Rewards", "help_rewards"),
            button("⭐ XP", "help_xp"),
        ],
        [
            button("📊 Analytics", "help_analytics"),
        ],
        [
            button("👥 Group", "group_help"),
        ],
        [
            button("🔔 Notifications", "help_notifications"),
        ],
        [
            button("ℹ️ About", "menu_about"),
        ],
        [
            button("🏠 Home", "home"),
        ],
    ])


# ============================================================
# CONFIRMATIONS
# ============================================================

def confirmation_keyboard(
    confirm_callback="confirm",
    cancel_callback="cancel",
    confirm_text="✅ Confirm",
    cancel_text="❌ Cancel"
):
    return markup([
        [
            button(confirm_text, confirm_callback),
            button(cancel_text, cancel_callback),
        ]
    ])


def reset_confirmation_keyboard():
    return markup([
        [
            button("🗑️ Clear history", "clear_confirm"),
            button("❌ Cancel", "reset_cancel"),
        ]
    ])


def clear_confirmation_keyboard():
    return markup([
        [
            button("🗑️ Clear", "clear_confirm"),
            button("❌ Cancel", "clear_cancel"),
        ]
    ])


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    # Helpers
    "button",
    "row",
    "markup",

    # Home
    "home_keyboard",
    "simple_home_keyboard",
    "group_home_keyboard",
    "home_back_keyboard",

    # Mood
    "mood_keyboard",
    "mood_result_keyboard",
    "back_mood_keyboard",

    # Navigation
    "back_keyboard",
    "bloom_back_keyboard",
    "group_back_keyboard",

    # Daily
    "daily_keyboard",
    "daily_complete_keyboard",

    # Reminder
    "reminder_keyboard",
    "group_reminder_keyboard",

    # Notifications
    "notification_keyboard",
    "notifications_keyboard",

    # History / Stats
    "history_keyboard",
    "stats_keyboard",
    "analytics_keyboard",
    "advanced_analytics_keyboard",
    "forecast_keyboard",

    # Profile
    "profile_keyboard",
    "account_keyboard",
    "streak_keyboard",
    "achievements_keyboard",

    # V4
    "bloom_dashboard_keyboard",
    "v4_dashboard_keyboard",

    # Goals
    "goals_keyboard",
    "goals_action_keyboard",
    "goal_result_keyboard",

    # Rewards
    "reward_keyboard",
    "reward_stats_keyboard",
    "reward_confirmation_keyboard",

    # XP
    "xp_keyboard",
    "xp_history_keyboard",

    # Journey
    "journey_keyboard",
    "bloom_journey_keyboard",

    # Birthdays
    "birthday_keyboard",
    "birthdays_keyboard",
    "birthday_manage_keyboard",


    # Groups
    "group_keyboard",
    "group_mood_keyboard",
    "group_report_keyboard",
    "group_analytics_keyboard",
    "group_games_keyboard",
    "group_admin_keyboard",
    "group_welcome_keyboard",
    "leaderboard_keyboard",
    "daily_question_keyboard",
    "group_streak_keyboard",

    # Settings / Help
    "settings_keyboard",
    "v4_settings_keyboard",
    "help_keyboard",

    # Confirmations
    "clear_confirmation_keyboard",
    "confirmation_keyboard",
    "reset_confirmation_keyboard",
]