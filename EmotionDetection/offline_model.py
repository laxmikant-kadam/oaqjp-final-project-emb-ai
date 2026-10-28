"""
Offline emotion model used only when the Watson NLP service is unreachable.

The module scores text with a small affect lexicon and builds a payload that
mirrors the Watson Emotion Predict JSON shape, so the rest of the application
stays unaware of where the scores came from.  It is a development fallback:
inside the IBM Skills Network lab the real Watson NLP service is always used.
"""

import re

EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")

_WORD_PATTERN = re.compile(r"[a-z']+")

_LEXICON = {
    "anger": {
        "angry", "anger", "mad", "furious", "fury", "rage", "raging",
        "irritated", "irritating", "annoyed", "annoying", "hate", "hated",
        "resent", "resentment", "outrage", "outraged", "frustrated",
        "frustrating", "hostile", "bitter", "provoked", "infuriated",
    },
    "disgust": {
        "disgust", "disgusted", "disgusting", "gross", "revolting",
        "repulsive", "repulsed", "sickening", "vile", "yuck", "nasty",
        "hideous", "appalled", "appalling", "loathe", "abhorrent",
        "distasteful", "creepy",
    },
    "fear": {
        "afraid", "fear", "fearful", "scared", "scary", "terrified",
        "terrifying", "frightened", "frightening", "anxious", "anxiety",
        "nervous", "worried", "worry", "dread", "dreading", "panic",
        "panicked", "alarmed", "alarming", "horrified", "horror", "uneasy",
        "threatened",
    },
    "joy": {
        "glad", "happy", "joy", "joyful", "delighted", "delight",
        "thrilled", "excited", "exciting", "love", "loved", "lovely",
        "wonderful", "great", "amazing", "awesome", "pleased", "cheerful",
        "ecstatic", "enjoy", "enjoyed", "fantastic", "good", "fun",
        "grateful", "thankful", "smile", "smiling", "laugh", "laughing",
        "proud", "satisfied", "blissful", "excellent", "perfect",
    },
    "sadness": {
        "sad", "sadness", "unhappy", "depressed", "depressing", "miserable",
        "sorrow", "sorrowful", "grief", "grieving", "heartbroken", "gloomy",
        "disappointed", "disappointing", "lonely", "cry", "crying", "cried",
        "tears", "despair", "hopeless", "regret", "regretted", "devastated",
        "hurt", "melancholy",
    },
}

_INTENSIFIERS = {
    "really", "very", "so", "extremely", "incredibly", "truly", "super",
    "quite", "absolutely", "totally", "completely", "utterly",
}

_NEGATIONS = {"not", "never", "no", "isn't", "aren't", "wasn't", "don't"}

_BASE_SCORE = 0.01


def _normalise(scores):
    """Scale the raw emotion weights so that they sum to 1.0."""
    total = sum(scores.values())
    if total <= 0:
        uniform = 1.0 / len(scores)
        return {emotion: uniform for emotion in scores}
    return {emotion: round(value / total, 6) for emotion, value in scores.items()}


def emotion_scores(text):
    """Return a normalised emotion score for every Watson emotion."""
    tokens = _WORD_PATTERN.findall(text.lower())
    scores = {emotion: _BASE_SCORE for emotion in EMOTIONS}

    for position, token in enumerate(tokens):
        emotion = next(
            (name for name, words in _LEXICON.items() if token in words), None
        )
        if emotion is None:
            continue

        weight = 1.0
        if position > 0 and tokens[position - 1] in _INTENSIFIERS:
            weight *= 1.6

        negated = tokens[max(0, position - 2):position]
        if any(word in _NEGATIONS for word in negated):
            # "I am not happy" should not be reported as joy.
            scores["sadness"] += weight * 0.4
            continue

        scores[emotion] += weight

    return _normalise(scores)


def offline_payload(text):
    """Build a Watson-shaped Emotion Predict payload for ``text``."""
    return {"emotionPredictions": [{"emotion": emotion_scores(text)}]}
