"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_neon.tap import TapNeon

TestTapNeon = get_tap_test_class(
    TapNeon,
    config={},
    suite_config=SuiteConfig(
        max_records_limit=None,
    ),
)
