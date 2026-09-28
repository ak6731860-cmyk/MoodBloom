from notifications import parse_custom_reminder_input


def test_pipe_format_reminder_parsing():
    parsed = parse_custom_reminder_input("Drink Water | 15:30 | Stay hydrated")
    assert parsed["valid"] is True
    assert parsed["title"] == "Drink Water"
    assert parsed["time"] == "15:30"
    assert parsed["message"] == "Stay hydrated"


def test_basic_time_format_reminder_parsing():
    parsed = parse_custom_reminder_input("Team Standup at 09:00")
    assert parsed["valid"] is True
    assert parsed["title"] == "Team Standup"
    assert parsed["time"] == "09:00"
    assert parsed["message"] == ""
