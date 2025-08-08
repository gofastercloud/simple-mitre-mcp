"""Simple E2E test to verify basic functionality."""

import pytest


@pytest.mark.e2e
def test_simple_e2e():
    """Simple test to verify E2E infrastructure."""
    assert True


def test_basic_functionality():
    """Basic test without E2E marker."""
    assert 1 + 1 == 2