"""
Global settings holder for the MCP server.

Goals
- Single place to configure process-wide settings at startup, then freeze (read-only).
- Support layered sources (CLI/ENV/file) with clear precedence.
- Provide SLS endpoint resolution now, and leave room for more sections in future.

This module keeps dependencies to a minimum (standard library only).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Optional, Dict, Iterable
import json
import os
import re


# ----------------------
# Helpers & parsing
# ----------------------

def normalize_host(val: str) -> str:
    """Normalize an endpoint host: strip scheme and trailing slash."""
    v = (val or "").strip()
    v = re.sub(r"^https?://", "", v, flags=re.IGNORECASE)
    return v.rstrip("/")


def _parse_pairs_str(s: str | None) -> Dict[str, str]:
    """Parse "REGION=HOST,REGION2=HOST2" or whitespace/comma separated pairs."""
    out: Dict[str, str] = {}
    if not s:
        return out
    tokens = re.split(r"[,\s]+", s.strip())
    for t in tokens:
        if not t:
            continue
        if "=" not in t:
            raise ValueError(f"Invalid endpoint pair: '{t}', expected REGION=HOST")
        region, host = t.split("=", 1)
        out[region.strip()] = host.strip()
    return out


def build_endpoint_mapping(
    cli_pairs: Iterable[str] | None,
    combined: Optional[str],
) -> Dict[str, str]:
    """Build endpoint mapping from CLI inputs only.

    Precedence: combined string < repeated cli_pairs (last wins).
    """
    mapping: Dict[str, str] = {}

    # Combined string
    if combined:
        mapping.update(_parse_pairs_str(combined.strip()))

    # Repeated CLI pairs (override)
    for pair in (cli_pairs or []):
        mapping.update(_parse_pairs_str(pair))

    # Normalize
    return {k.strip(): normalize_host(v) for k, v in mapping.items()}


# ----------------------
# Settings schema
# ----------------------


@dataclass(frozen=True)
class SLSSettings:
    """Settings for SLS related configuration.

    - endpoints: region -> host mapping
    - template: fallback when region not mapped
    """

    endpoints: Dict[str, str] = field(default_factory=dict)
    template: str = "{region}.log.aliyuncs.com"

    def __post_init__(self):
        # normalize hosts
        normalized = {k: normalize_host(v) for k, v in (self.endpoints or {}).items()}
        object.__setattr__(self, "endpoints", normalized)

    def resolve(self, region: str) -> str:
        if not region:
            raise ValueError("region is required")
        host = self.endpoints.get(region)
        if host:
            return host
        return self.template.format(region=region)


@dataclass(frozen=True)
class ArmsSettings:
    """Settings for ARMS related configuration."""
    endpoints: Dict[str, str] = field(default_factory=dict)
    template: str = "arms.{region}.aliyuncs.com"

    def __post_init__(self):
        normalized = {k: normalize_host(v) for k, v in (self.endpoints or {}).items()}
        object.__setattr__(self, "endpoints", normalized)

    def resolve(self, region: str) -> str:
        if not region:
            raise ValueError("region is required")
        host = self.endpoints.get(region)
        if host:
            return host
        return self.template.format(region=region)


@dataclass(frozen=True)
class GlobalSettings:
    """Top-level settings container. Extend with more sections when needed."""

    sls: SLSSettings = field(default_factory=SLSSettings)
    arms: ArmsSettings = field(default_factory=ArmsSettings)
    # TODO: http: HttpSettings, logging: LoggingSettings, etc.


# ----------------------
# Global holder (configure once, then freeze)
# ----------------------

_lock = RLock()
_settings: Optional[GlobalSettings] = None
_frozen: bool = False


def configure_settings(settings: GlobalSettings, freeze: bool = True) -> GlobalSettings:
    """Configure global settings. Call once at process startup."""
    global _settings, _frozen
    with _lock:
        if _frozen:
            raise RuntimeError("GlobalSettings already frozen")
        _settings = settings
        if freeze:
            _frozen = True
        return _settings


def get_settings() -> GlobalSettings:
    """Get current global settings (lazily creates default)."""
    global _settings
    with _lock:
        if _settings is None:
            _settings = GlobalSettings()
            # Default is read-only unless explicitly reconfigured
        return _settings


# Test helpers (avoid using in production code)
def _override_settings(settings: GlobalSettings):
    global _settings
    with _lock:
        _settings = settings


def _reset_settings():
    global _settings, _frozen
    with _lock:
        _settings = None
        _frozen = False
