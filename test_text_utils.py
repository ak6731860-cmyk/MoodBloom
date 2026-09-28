import pytest

from text_utils import bold, code, escape_html, italic, title


def test_escape_html_and_formatting_helpers():
    assert escape_html("<tag> & hi") == "&lt;tag&gt; &amp; hi"
    assert bold("Mood") == "<b>Mood</b>"
    assert italic("gentle") == "<i>gentle</i>"
    assert code("DD-MM") == "<code>DD-MM</code>"
    assert title("Daily Bloom") == "<b>Daily Bloom</b>"


def test_title_escapes_special_chars():
    assert title("A & B < C") == "<b>A &amp; B &lt; C</b>"
