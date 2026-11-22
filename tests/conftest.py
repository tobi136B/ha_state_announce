"""Gemeinsame Test Hilfen."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Eigene Integrationen in jedem Test erlauben."""
    return
