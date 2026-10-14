"""
Braille Learning Device - Initial UI Python Prototype

Scope so Far: Only handles what the user interacts with, all other code in this model will
handled by Soft/Firm team at OAT Lab so explore the other repo.

This Initial Interface has:
    1. BUTTON_MAP:          what each of the physical control does at each mode
    2. CUES:                what feature will trigger, sound, haptic, or audio
    3. LessonPolicy         what the lesson structure is like: forgiving/ guided/ rewarding
                            for the user

Physical controls:
    FORWARD/ BACKWARD buttons, MIC button, volume SLIDER, scroll DIAL.

User outputs:
    jumbo braille cells, speaker (voice + tones), haptic vibration
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Deque, Dict, List, Optional, Tuple
