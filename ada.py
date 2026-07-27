#!/usr/bin/env python3
"""Accessibility helpers for varied terminals and assistive hardware.

This module does not claim legal ADA compliance. It provides practical options
for plain text, line wrapping, reduced motion, screen-reader-friendly labels,
and high-contrast preferences used by the local communication interface.
"""
from __future__ import annotations

import json
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_FILE = Path.home() / '.config/hol-family-source-diagnostic/ada.json'


@dataclass
class ADAProfile:
    plain_ascii: bool = False
    wrap_width: int = 100
    reduced_motion: bool = True
    high_contrast: bool = True
    screen_reader_labels: bool = True

    @classmethod
    def load(cls) -> 'ADAProfile':
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
            allowed = {key: data[key] for key in asdict(cls()).keys() if key in data}
            profile = cls(**allowed)
            profile.wrap_width = max(40, min(int(profile.wrap_width), 240))
            return profile
        except Exception:
            return cls()

    def to_dict(self) -> dict:
        return asdict(self)


def format_accessible_line(name: str, message: str, channel: str, profile: ADAProfile) -> str:
    prefix = f'[{name}]'
    if channel:
        prefix += f' ({channel})'
    text = f'{prefix} {message}'
    if profile.plain_ascii:
        text = text.encode('ascii', errors='replace').decode('ascii')
    if profile.wrap_width:
        text = '\n'.join(textwrap.wrap(text, width=profile.wrap_width, subsequent_indent='  '))
    return text
