"""
Emotion detection application built on the IBM Watson NLP library.

The public entry point is :func:`emotion_detector`.  It sends the supplied
text to the Watson NLP *Emotion Predict* service and returns the five
Watson emotion scores together with the dominant emotion.

The Watson NLP endpoint used during the IBM Skills Network lab is only
reachable from inside the lab network.  If the endpoint cannot be reached,
the module logs a warning and falls back to ``offline_model``, which returns
a response in exactly the same Watson JSON shape.  The fallback is only used
when the Watson call actually fails; set ``EMOTION_OFFLINE_FALLBACK=0`` to
disable it and surface the network error instead.
"""

import logging
import os
import time

import requests

from .offline_model import offline_payload

LOGGER = logging.getLogger(__name__)

#: Watson NLP Emotion Predict endpoint (overridable for lab / on-prem setups).
WATSON_EMOTION_URL = os.getenv(
    "WATSON_EMOTION_URL",
    "https://sn-watson-emotion.labs.skills.network/v1/"
    "watson.runtime.nlp.v1/NlpService/EmotionPredict",
)

#: Model identifier required by the Watson NLP runtime.
MODEL_ID = os.getenv(
    "WATSON_MODEL_ID", "emotion_aggregated-workflow_lang_en_stock"
)

#: Timeout (seconds) for the Watson NLP request.
REQUEST_TIMEOUT = float(os.getenv("WATSON_TIMEOUT", "4"))

#: How long (seconds) to skip Watson after a connection failure.
FALLBACK_COOLDOWN = float(os.getenv("WATSON_RETRY_AFTER", "60"))

#: Emotions returned by the Watson NLP emotion model, in the order we report.
EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")

_FALLBACK_ENABLED = os.getenv("EMOTION_OFFLINE_FALLBACK", "1") != "0"

_EMPTY_RESULT = {emotion: None for emotion in EMOTIONS}
_EMPTY_RESULT["dominant_emotion"] = None


class _CircuitBreaker:
    """Skip Watson calls for a while after a connection failure."""

    def __init__(self, cooldown):
        self.cooldown = cooldown
        self._opened_at = None

    def is_open(self):
        """Return ``True`` while the breaker is still in its cooldown window."""
        if self._opened_at is None:
            return False
        if time.monotonic() - self._opened_at >= self.cooldown:
            self._opened_at = None
            return False
        return True

    def record_failure(self):
        """Start the cooldown window."""
        self._opened_at = time.monotonic()

    def record_success(self):
        """Reset the breaker after a successful Watson call."""
        self._opened_at = None


_BREAKER = _CircuitBreaker(FALLBACK_COOLDOWN)


def _empty_result():
    """Return a fresh copy of the "nothing detected" result."""
    return dict(_EMPTY_RESULT)


def _format_response(watson_response):
    """Extract the five emotion scores and the dominant emotion."""
    scores = watson_response["emotionPredictions"][0]["emotion"]
    dominant_emotion = max(scores, key=scores.get)

    result = {emotion: scores.get(emotion) for emotion in EMOTIONS}
    result["dominant_emotion"] = dominant_emotion
    return result


def emotion_detector(text_to_analyze):
    """
    Detect the emotions expressed in ``text_to_analyze``.

    Returns a dictionary with the five Watson NLP emotion scores and the
    ``dominant_emotion``.  Blank or invalid input returns the same keys with
    ``None`` values, which the web layer renders as an error message.
    """
    if not text_to_analyze or not str(text_to_analyze).strip():
        # Watson NLP answers HTTP 400 for blank input; short-circuit the same
        # documented outcome so the UI behaves identically when offline.
        return _empty_result()

    if _BREAKER.is_open():
        LOGGER.debug("Watson NLP circuit open; using the offline fallback model.")
        return _format_response(offline_payload(text_to_analyze))

    payload = {"raw_document": {"text": text_to_analyze}}
    headers = {
        "grpc-metadata-mm-model-id": MODEL_ID,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(
            WATSON_EMOTION_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 400:
            return _empty_result()
        response.raise_for_status()
        watson_response = response.json()
        _BREAKER.record_success()
        return _format_response(watson_response)
    except (requests.RequestException, ValueError, KeyError, IndexError) as error:
        if not _FALLBACK_ENABLED:
            raise
        _BREAKER.record_failure()
        LOGGER.warning(
            "Watson NLP unavailable (%s); using the offline fallback model.",
            type(error).__name__,
        )
        LOGGER.debug("Watson NLP error details: %s", error)
        return _format_response(offline_payload(text_to_analyze))
