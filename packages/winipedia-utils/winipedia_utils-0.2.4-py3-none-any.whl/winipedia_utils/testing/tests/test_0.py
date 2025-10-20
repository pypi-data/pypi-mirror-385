"""Contains an empty test."""

from winipedia_utils.testing.assertions import assert_with_msg


def test_0() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
    always_true = True
    assert_with_msg(always_true, "This should not raise")
