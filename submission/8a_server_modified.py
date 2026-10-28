"""Flask web server for the Emotion Detector application (Tasks 6 & 7)."""

import os

from flask import Flask, render_template, request

from EmotionDetection.emotion_detection import emotion_detector

app = Flask("Emotion Detector")

#: Port used by ``python server.py`` (5000, as in the lab, unless overridden).
PORT = int(os.getenv("PORT", "5000"))


@app.route("/emotionDetector")
def sent_analyzer():
    """Analyse the text supplied in the ``textToAnalyze`` query parameter."""
    text_to_analyze = request.args.get("textToAnalyze", "")

    # Task 7: blank / invalid input is reported to the user instead of a crash.
    if not text_to_analyze.strip():
        return "Invalid text! Please try again!"

    result = emotion_detector(text_to_analyze)

    if result["dominant_emotion"] is None:
        return "Invalid text! Please try again!"

    return (
        "For the given statement, the system response is "
        f"'anger': {result['anger']}, 'disgust': {result['disgust']}, "
        f"'fear': {result['fear']}, 'joy': {result['joy']} and "
        f"'sadness': {result['sadness']}. "
        f"The dominant emotion is {result['dominant_emotion']}."
    )


@app.route("/")
def render_index_page():
    """Render the single-page interface of the application."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
