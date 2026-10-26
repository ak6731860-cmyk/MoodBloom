from text_utils import bold, code, escape_html, italic, title, join_lines


def test_formatting_helpers_return_plain_text():
    assert escape_html("<tag> & hi") == "<tag> & hi"
    assert bold("Mood") == "Mood"
    assert italic("gentle") == "gentle"
    assert code("DD-MM") == "DD-MM"
    assert title("Daily Bloom") == "Daily Bloom"


def test_plain_text_preserves_special_characters():
    assert title("A & B < C") == "A & B < C"


def test_join_lines():
    assert join_lines(["one", "two"]) == "one\ntwo"
