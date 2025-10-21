"""Synchronicity configuration for Archil SDK."""

from synchronicity import Synchronizer

# Shared synchronizer instance for the entire SDK
# This allows us to generate sync APIs from async implementations
synchronizer = Synchronizer()
