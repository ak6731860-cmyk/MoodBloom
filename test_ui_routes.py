"""Static integration checks for the MoodBloom inline UI and command routes."""
import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent


def _parse(name):
    return ast.parse((ROOT / name).read_text(encoding="utf-8"))


def test_every_keyboard_helper_used_by_bot_exists():
    keyboard_tree = _parse("keyboards.py")
    defined = {node.name for node in keyboard_tree.body if isinstance(node, ast.FunctionDef)}
    bot_text = (ROOT / "bot.py").read_text(encoding="utf-8")
    used = set(re.findall(r"keyboards\.([A-Za-z_][A-Za-z0-9_]*)", bot_text))
    assert not (used - defined), f"Missing keyboard helpers: {sorted(used - defined)}"


def test_reminder_studio_has_dedicated_callback_route():
    bot_text = (ROOT / "bot.py").read_text(encoding="utf-8")
    reminder_text = (ROOT / "reminder_engine.py").read_text(encoding="utf-8")
    assert 'pattern=r"^(home|menu_(?!group$|reminder$)' in bot_text
    assert 'pattern=r"^menu_reminder$"' in reminder_text
    assert 'pattern=r"^rem2\\|"' in reminder_text


def test_story_mystery_and_group_help_commands_are_registered():
    bot_text = (ROOT / "bot.py").read_text(encoding="utf-8")
    assert 'CommandHandler("story", story_engine.story_command)' in bot_text
    assert 'CommandHandler("mystery", mystery_engine.mystery_command)' in bot_text
    assert 'CommandHandler("grouphelp", group_help_command)' in bot_text


def test_personal_and_group_charts_are_separate():
    analytics_text = (ROOT / "analytics.py").read_text(encoding="utf-8")
    bot_text = (ROOT / "bot.py").read_text(encoding="utf-8")
    assert "def create_mood_chart(history):" in analytics_text
    assert "def create_weekly_mood_chart(history):" in analytics_text
    assert "async def group_chart_callback(" in bot_text
    assert "Group Mood Chart" in bot_text


def test_owner_only_broadcast_and_id_commands_are_registered():
    bot_text = (ROOT / "bot.py").read_text(encoding="utf-8")
    config_text = (ROOT / "config.py").read_text(encoding="utf-8")
    assert 'CommandHandler("cast", cast_command)' in bot_text
    assert 'CommandHandler("owner", owner_command)' in bot_text
    assert 'CommandHandler("myid", myid_command)' in bot_text
    assert "OWNER_ID" in config_text
    assert 'pattern=r"^owner_(?:stats|cast_confirm|cast_cancel)$"' in bot_text


def test_personal_birthday_menu_does_not_use_global_upcoming_lists():
    bot_text = (ROOT / "bot.py").read_text(encoding="utf-8")
    start = bot_text.index("async def show_birthday_menu(")
    end = bot_text.index("async def birthday_command(", start)
    personal_menu = bot_text[start:end]
    assert "get_next_birthday()" not in personal_menu
    assert "Your birthday is" in personal_menu


def test_group_birthday_scheduler_is_scoped_to_each_group():
    scheduler_text = (ROOT / "scheduler.py").read_text(encoding="utf-8")
    assert "get_group_today_birthdays(group_id)" in scheduler_text
    assert "Group birthday notification error" in scheduler_text
