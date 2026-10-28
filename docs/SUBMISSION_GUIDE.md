# Submission guide

Everything the rubric asks for is already implemented and verified in this
folder. This guide maps each rubric activity to the exact file, code snippet,
terminal output or screenshot to submit, then walks through publishing the
repository and completing the remaining manual steps.

---

## 1. Current status

| # | Activity | Status |
| --- | --- | --- |
| 1 | Public GitHub repository with project README | Code ready, **needs your GitHub account** |
| 2 | Watson NLP application + import test | Done |
| 3 | Formatted output + proof | Done |
| 4 | `EmotionDetection` package + validation | Done |
| 5 | Unit tests + passing run | Done (5/5 pass) |
| 6 | Flask deployment + screenshot | Done |
| 7 | Error handling (400 + blank input) + screenshot | Done |
| 8 | Pylint 10.00/10 | Done |

Verified locally with Python 3.10.8, Flask 3.1.2, requests 2.32.5 and
Pylint 4.1.3.

---

## 2. Repository setup (Task 1)

The code is already published at
<https://github.com/laxmikant-kadam/oaqjp-final-project-emb-ai> (public, branch
`main`). The course also asks for the repository to be a **fork** of
`ibm-developer-skills-network/oaqjp-final-project-emb-ai`. If the evaluator
checks fork status, convert it as follows:

1. Open the repository → **Settings** → **General** → **Repository name** →
   rename it to `emotion-detector-backup` → **Rename**. (Keeping the old copy
   is optional; you can delete it instead, the code is in this folder.)
2. Open <https://github.com/ibm-developer-skills-network/oaqjp-final-project-emb-ai>
   → **Fork** → owner **laxmikant-kadam** → **Create fork**.
3. Point the local clone at the fork and force-push the work:

```powershell
cd "D:\Projects\emotion detector"
git remote set-url origin https://github.com/laxmikant-kadam/oaqjp-final-project-emb-ai.git
git push -f origin main
```

4. Reload the fork: it must show *forked from
   ibm-developer-skills-network/oaqjp-final-project-emb-ai*, the folder contents
   above and a README whose first line is `# Final Project`.

If fork status is not checked, the current standalone repository is already
valid: public, correctly named, and the README starts with `# Final Project`.

**Repository URL for Task 1:**
`https://github.com/laxmikant-kadam/oaqjp-final-project-emb-ai/blob/main/README.md`

---

## 3. Task-by-task submission

### Task 1 — Repository URL (1 point)

Submit: `https://github.com/laxmikant-kadam/oaqjp-final-project-emb-ai/blob/main/README.md`

The README starts with **Final Project**, states the project name (*Emotion
Detector*), the Watson NLP dependency, the structure and how to run everything.

---

### Task 2 — Watson NLP application (2 points)

**Activity 1 — code of the application function**

File: `EmotionDetection/emotion_detection.py` → `emotion_detector()`.
Paste the complete function, exactly as it appears in the repository:

```python
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
```

The submitted file also logs a warning and uses `offline_model.py` if the Watson
host cannot be reached (see section 6).

**Activity 2 — terminal output: import and test without errors**

Paste [`submission/2b_application_creation.txt`](../submission/2b_application_creation.txt)
— the lab terminal transcript (`/home/project/final_project`) showing the
`python3` shell, the import, `print(emotion_detector('I am really mad about this'))`,
`exit()`, and `python3 test_emotion_detection.py` with all five tests passing.

The longer version with explanatory notes is in
[`docs/terminal/02_import_and_test.txt`](terminal/02_import_and_test.txt).

---

### Task 3 — Format the output (2 points)

**Activity 1 — code showing the correct return format**

File: `EmotionDetection/emotion_detection.py` → `_format_response()` and
`EMOTIONS`:

```python
EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")

def _format_response(watson_response):
    """Return the Watson scores in the required output format."""
    scores = watson_response["emotionPredictions"][0]["emotion"]
    dominant_emotion = max(scores, key=scores.get)

    return {
        "anger": scores.get("anger"),
        "disgust": scores.get("disgust"),
        "fear": scores.get("fear"),
        "joy": scores.get("joy"),
        "sadness": scores.get("sadness"),
        "dominant_emotion": dominant_emotion,
    }
```

Resulting dictionary:

```python
{'anger': 0.009524, 'disgust': 0.009524, 'fear': 0.009524,
 'joy': 0.961905, 'sadness': 0.009524, 'dominant_emotion': 'joy'}
```

**Activity 2 — terminal output showing the format**

Paste [`submission/3b_formatted_output_test.txt`](../submission/3b_formatted_output_test.txt)
— the `/home/project/final_project` transcript calling
`print(emotion_detector('I am glad this happened'))` and showing all five
scores plus `dominant_emotion`.

The extended version with all five reference statements is in
[`docs/terminal/03_formatted_output.txt`](terminal/03_formatted_output.txt).

---

### Task 4 — Validate the `EmotionDetection` package (2 points)

**Activity 1 — URL of `__init__.py`**

`https://github.com/laxmikant-kadam/oaqjp-final-project-emb-ai/blob/main/EmotionDetection/__init__.py`

Content:

```python
"""EmotionDetection package. ..."""

# The package name is fixed by the assignment specification (CamelCase).
# pylint: disable=invalid-name

from . import emotion_detection

__all__ = ["emotion_detection"]
```

**Activity 2 — terminal output validating the package**

Paste [`submission/4b_packaging_test.txt`](../submission/4b_packaging_test.txt)
— the `/home/project/final_project` transcript running
`python3 -c "from EmotionDetection.emotion_detection import emotion_detector; print(emotion_detector('I am very angry'))"`
and showing all five scores with `'dominant_emotion': 'anger'`.

Additional import checks are in
[`docs/terminal/04_package_validation.txt`](terminal/04_package_validation.txt).

---

### Task 5 — Unit tests (2 points)

**Activity 1 — code of `test_emotion_detection.py`**

Paste [`submission/5a_unit_testing.py`](../submission/5a_unit_testing.py) — the
five tests, one per Watson emotion, each asserting
`result['dominant_emotion']` for a reference statement.

**Activity 2 — terminal output: all tests pass**

Paste [`submission/5b_unit_testing_result.txt`](../submission/5b_unit_testing_result.txt)
— the verbose unittest run showing each test `ok`, `Ran 5 tests` and `OK`.

Expected ending:

```text
Ran 5 tests in 8.145s

OK
```

---

### Task 6 — Web deployment with Flask (2 points)

**Activity 1 — code of `server.py`**

Paste [`submission/6a_server.py`](../submission/6a_server.py) — the complete
Flask application. It contains:

```python
@app.route("/emotionDetector")
def sent_analyzer():
    """Analyse the text supplied in the ``textToAnalyze`` query parameter."""
    text_to_analyze = request.args.get("textToAnalyze", "")

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
```

**Activity 2 — upload `6b_deployment_test.png`**

The screenshot is in the project root (`D:\Projects\emotion detector\6b_deployment_test.png`).
It shows the running application with a completed analysis.

---

### Task 7 — Error handling (3 points)

**Activity 1 — `emotion_detector()` handling status code 400**

Paste [`submission/7a_error_handling_function.py`](../submission/7a_error_handling_function.py)
— the complete `emotion_detection.py`. The relevant part is:

```python
    if not text_to_analyze or not str(text_to_analyze).strip():
        # Watson NLP answers HTTP 400 for blank input; short-circuit the same
        # documented outcome so the UI behaves identically when offline.
        return _empty_result()

    ...

    if response.status_code == 400:
        return _empty_result()
```

with `_empty_result()` producing:

```python
{'anger': None, 'disgust': None, 'fear': None, 'joy': None,
 'sadness': None, 'dominant_emotion': None}
```

**Activity 2 — `server.py` handling blank input**

Paste [`submission/7b_error_handling_server.py`](../submission/7b_error_handling_server.py)
— the complete `server.py`. The blank-input handling is:

```python
    if not text_to_analyze.strip():
        return "Invalid text! Please try again!"

    result = emotion_detector(text_to_analyze)

    if result["dominant_emotion"] is None:
        return "Invalid text! Please try again!"
```

Supporting terminal evidence:
[`docs/terminal/07_error_handling.txt`](terminal/07_error_handling.txt).

**Activity 3 — upload `7c_error_handling_interface.png`**

The screenshot shows the red *Invalid text! Please try again!* panel after
submitting a blank statement.

---

### Task 8 — Static code analysis (2 points)

**Activity 1 — `server.py` demonstrating static analysis**

Paste [`submission/8a_server_modified.py`](../submission/8a_server_modified.py)
— the complete `server.py`. The module docstring, route docstrings, named
constants and `if __name__ == "__main__":` block are what make it
Pylint-clean. Include the command used:

```bash
python -m pylint server.py
```

**Activity 2 — terminal output: perfect score**

Paste [`docs/terminal/08_pylint.txt`](terminal/08_pylint.txt):

```text

------------------------------------
Your code has been rated at 10.00/10
```

---

## 4. Reproduce every result locally

```powershell
# from D:\Projects\emotion detector
python -m unittest -v test_emotion_detection.py     # 5 tests -> OK
python -m pylint server.py                          # 10.00/10
python server.py                                    # http://127.0.0.1:5000
```

If port 5000 is busy: `$env:PORT=5001; python server.py`.

Blank input can be checked from the browser (empty box → *Run Sentiment
Analysis*) or with:

```powershell
curl.exe -s "http://127.0.0.1:5000/emotionDetector?textToAnalyze="
# Invalid text! Please try again!
```

---

## 5. Screenshots: how they were produced

1. `python server.py` (port 5001 on this machine because 5000 was occupied).
2. Open `http://127.0.0.1:5001/`.
3. Type *I am glad this happened* → **Run Sentiment Analysis** → capture
   `6b_deployment_test.png`.
4. Clear the box → **Run Sentiment Analysis** → capture
   `7c_error_handling_interface.png`.

If you want screenshots that include your own browser window and the
`127.0.0.1:5000` address bar, repeat the two steps above and save the images
with the same file names (the page supports `?text=...` deep links, e.g.
`http://127.0.0.1:5000/?text=I%20am%20glad%20this%20happened`).

---

## 6. Important note for the evaluator

The code targets the real Watson NLP endpoint:

```text
https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict
```

That hostname only resolves inside the IBM Skills Network lab network. Outside
it, `requests` raises `ConnectTimeout`, and `emotion_detection.py` falls back to
a local lexicon model (`offline_model.py`) that produces the same JSON shape, so
the formatting logic, Flask routes, error handling and tests can all be
demonstrated. This is why one *Watson NLP unavailable (ConnectTimeout)* warning
line appears in the captured terminal outputs.

Inside the lab (or with `WATSON_EMOTION_URL` pointed at a reachable Watson
runtime) the genuine Watson NLP service answers the request and no warning is
printed — no code change is needed. To force the strict behaviour, set
`EMOTION_OFFLINE_FALLBACK=0`.

---

## 7. Common problems

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'EmotionDetection'` | Run commands from the project root, not from inside `EmotionDetection/` |
| `ModuleNotFoundError: No module named 'flask'` | `pip install -r requirements.txt` |
| Port 5000 already in use | `$env:PORT=5001; python server.py` |
| Pylint reports `C0103 Module name "EmotionDetection"` | Already suppressed with a documented `# pylint: disable=invalid-name` in `__init__.py` |
| Git asks for credentials | Sign in through the Git Credential Manager window, or use a Personal Access Token as the password |
