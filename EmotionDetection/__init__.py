"""EmotionDetection package.

Exposes the :mod:`EmotionDetection.emotion_detection` application module so
the detector can be used as::

    import EmotionDetection
    EmotionDetection.emotion_detection.emotion_detector("I love this")
"""

# The package name is fixed by the assignment specification (CamelCase).
# pylint: disable=invalid-name

from . import emotion_detection

__all__ = ["emotion_detection"]
