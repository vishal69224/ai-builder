"""Tests for follow-up prompt classification (polish / revert / edit)."""

from app.generation.edit.edit_mode import EditModeService, FollowUpKind


def test_classify_polish_make_it_perfect():
    svc = EditModeService()
    assert svc.classify("make it perfect", True) == FollowUpKind.polish
    assert svc.classify("improve the design", True) == FollowUpKind.polish
    assert svc.classify("polish it", True) == FollowUpKind.polish


def test_classify_revert():
    svc = EditModeService()
    assert svc.classify("revert the changes", True) == FollowUpKind.revert
    assert svc.classify("undo", True) == FollowUpKind.revert
    assert svc.classify("go back", True) == FollowUpKind.revert


def test_classify_targeted_edit():
    svc = EditModeService()
    assert svc.classify("change the hero to be bolder", True) == FollowUpKind.targeted_edit
    assert svc.classify("update the navbar colors", True) == FollowUpKind.targeted_edit


def test_classify_new_generate_without_project():
    svc = EditModeService()
    assert svc.classify("make it perfect", False) == FollowUpKind.generate


def test_polish_seed_keeps_brand_and_last_prompt():
    svc = EditModeService()
    seed = svc.polish_seed_prompt(
        project_name="Northstar",
        last_prompt="here i want clothing store website",
        niche_hint="luxury clothing fashion",
    )
    assert "Northstar" in seed
    assert "clothing" in seed.lower()
    assert "perfect" not in seed.lower() or "premium" in seed.lower()
