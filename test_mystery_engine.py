from mystery_engine import mask_answer_text, build_mystery_choices


def test_masked_answer_is_not_full_text():
    full = "The missing key was hidden inside the broken lantern"
    masked = mask_answer_text(full)
    assert masked != full
    assert len(masked) < len(full)
    assert "..." in masked or "…" in masked


def test_choices_hide_full_answer_but_still_have_correct_option():
    choices = build_mystery_choices(
        [
            {"label": "The missing key was hidden inside the broken lantern", "correct": True},
            {"label": "The thief left by the front door", "correct": False},
        ]
    )
    assert any(choice["correct"] for choice in choices)
    assert all(choice["display"] != choice["full"] for choice in choices)
    assert all(len(choice["display"]) < len(choice["full"]) for choice in choices)
