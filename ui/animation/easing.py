"""
easing.py
=========

Collection of easing functions used by the War Chess animation engine.

Every easing function accepts a normalized progress value:

    t ∈ [0.0, 1.0]

and returns another normalized value.

These functions are intentionally independent of pygame and may be used
anywhere in the project.

Example
-------
progress = ease_out_quad(0.5)

Future Uses
-----------
- Button hover animations
- Menu transitions
- Fade effects
- Card scaling
- Black hole pulse
- Floating particles
- Screen transitions
- Campaign map animations
"""

from __future__ import annotations

import math


# ==========================================================
# Linear
# ==========================================================

def linear(t: float) -> float:
    """Constant speed."""
    return t


# ==========================================================
# Quadratic
# ==========================================================

def ease_in_quad(t: float) -> float:
    """Starts slowly and accelerates."""
    return t * t


def ease_out_quad(t: float) -> float:
    """Starts fast and slows toward the end."""
    return 1 - (1 - t) * (1 - t)


def ease_in_out_quad(t: float) -> float:
    """Slow → Fast → Slow."""
    if t < 0.5:
        return 2 * t * t
    return 1 - ((-2 * t + 2) ** 2) / 2


# ==========================================================
# Cubic
# ==========================================================

def ease_in_cubic(t: float) -> float:
    return t ** 3


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    if t < 0.5:
        return 4 * t ** 3
    return 1 - ((-2 * t + 2) ** 3) / 2


# ==========================================================
# Quartic
# ==========================================================

def ease_in_quart(t: float) -> float:
    return t ** 4


def ease_out_quart(t: float) -> float:
    return 1 - (1 - t) ** 4


def ease_in_out_quart(t: float) -> float:
    if t < 0.5:
        return 8 * t ** 4
    return 1 - ((-2 * t + 2) ** 4) / 2


# ==========================================================
# Quintic
# ==========================================================

def ease_in_quint(t: float) -> float:
    return t ** 5


def ease_out_quint(t: float) -> float:
    return 1 - (1 - t) ** 5


def ease_in_out_quint(t: float) -> float:
    if t < 0.5:
        return 16 * t ** 5
    return 1 - ((-2 * t + 2) ** 5) / 2


# ==========================================================
# Sinusoidal
# ==========================================================

def ease_in_sine(t: float) -> float:
    return 1 - math.cos((t * math.pi) / 2)


def ease_out_sine(t: float) -> float:
    return math.sin((t * math.pi) / 2)


def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


# ==========================================================
# Exponential
# ==========================================================

def ease_in_expo(t: float) -> float:
    if t == 0:
        return 0
    return 2 ** (10 * t - 10)


def ease_out_expo(t: float) -> float:
    if t == 1:
        return 1
    return 1 - 2 ** (-10 * t)


def ease_in_out_expo(t: float) -> float:

    if t == 0:
        return 0

    if t == 1:
        return 1

    if t < 0.5:
        return (2 ** (20 * t - 10)) / 2

    return (2 - 2 ** (-20 * t + 10)) / 2


# ==========================================================
# Circular
# ==========================================================

def ease_in_circ(t: float) -> float:
    return 1 - math.sqrt(1 - t * t)


def ease_out_circ(t: float) -> float:
    return math.sqrt(1 - (t - 1) ** 2)


def ease_in_out_circ(t: float) -> float:

    if t < 0.5:
        return (1 - math.sqrt(1 - (2 * t) ** 2)) / 2

    return (math.sqrt(1 - (-2 * t + 2) ** 2) + 1) / 2


# ==========================================================
# Back
# ==========================================================

def ease_in_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t ** 3 - c1 * t ** 2


def ease_out_back(t: float) -> float:
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def ease_in_out_back(t: float) -> float:

    c1 = 1.70158
    c2 = c1 * 1.525

    if t < 0.5:
        return ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2

    return (
        ((2 * t - 2) ** 2 * ((c2 + 1) * (2 * t - 2) + c2) + 2)
        / 2
    )


# ==========================================================
# Bounce
# ==========================================================

def ease_out_bounce(t: float) -> float:

    n1 = 7.5625
    d1 = 2.75

    if t < 1 / d1:
        return n1 * t * t

    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75

    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375

    t -= 2.625 / d1
    return n1 * t * t + 0.984375


def ease_in_bounce(t: float) -> float:
    return 1 - ease_out_bounce(1 - t)


def ease_in_out_bounce(t: float) -> float:

    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2

    return (1 + ease_out_bounce(2 * t - 1)) / 2


# ==========================================================
# Elastic
# ==========================================================

def ease_in_elastic(t: float) -> float:

    if t == 0:
        return 0

    if t == 1:
        return 1

    c4 = (2 * math.pi) / 3

    return -(2 ** (10 * t - 10)) * math.sin((t * 10 - 10.75) * c4)


def ease_out_elastic(t: float) -> float:

    if t == 0:
        return 0

    if t == 1:
        return 1

    c4 = (2 * math.pi) / 3

    return (
        2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
    )


def ease_in_out_elastic(t: float) -> float:

    if t == 0:
        return 0

    if t == 1:
        return 1

    c5 = (2 * math.pi) / 4.5

    if t < 0.5:
        return (
            -(2 ** (20 * t - 10))
            * math.sin((20 * t - 11.125) * c5)
        ) / 2

    return (
        (2 ** (-20 * t + 10))
        * math.sin((20 * t - 11.125) * c5)
    ) / 2 + 1


# ==========================================================
# Registry
# ==========================================================

EASING_FUNCTIONS = {
    "linear": linear,

    "ease_in_quad": ease_in_quad,
    "ease_out_quad": ease_out_quad,
    "ease_in_out_quad": ease_in_out_quad,

    "ease_in_cubic": ease_in_cubic,
    "ease_out_cubic": ease_out_cubic,
    "ease_in_out_cubic": ease_in_out_cubic,

    "ease_in_quart": ease_in_quart,
    "ease_out_quart": ease_out_quart,
    "ease_in_out_quart": ease_in_out_quart,

    "ease_in_quint": ease_in_quint,
    "ease_out_quint": ease_out_quint,
    "ease_in_out_quint": ease_in_out_quint,

    "ease_in_sine": ease_in_sine,
    "ease_out_sine": ease_out_sine,
    "ease_in_out_sine": ease_in_out_sine,

    "ease_in_expo": ease_in_expo,
    "ease_out_expo": ease_out_expo,
    "ease_in_out_expo": ease_in_out_expo,

    "ease_in_circ": ease_in_circ,
    "ease_out_circ": ease_out_circ,
    "ease_in_out_circ": ease_in_out_circ,

    "ease_in_back": ease_in_back,
    "ease_out_back": ease_out_back,
    "ease_in_out_back": ease_in_out_back,

    "ease_in_bounce": ease_in_bounce,
    "ease_out_bounce": ease_out_bounce,
    "ease_in_out_bounce": ease_in_out_bounce,

    "ease_in_elastic": ease_in_elastic,
    "ease_out_elastic": ease_out_elastic,
    "ease_in_out_elastic": ease_in_out_elastic,
}