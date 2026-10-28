/**
 * Front-end controller for the Emotion Detector.
 * Sends the statement to /emotionDetector and renders the plain-text response.
 */

function setResponse(message, isError) {
  var target = document.getElementById("system_response");
  target.textContent = message;
  target.classList.toggle("is-error", Boolean(isError));
}

function RunSentimentAnalysis() {
  var textToAnalyze = document.getElementById("textToAnalyze").value;
  var button = document.getElementById("analyseBtn");
  var xhttp = new XMLHttpRequest();

  setResponse("Analysing...", false);
  button.disabled = true;

  xhttp.onreadystatechange = function () {
    if (this.readyState !== 4) {
      return;
    }
    button.disabled = false;
    if (this.status === 200) {
      var isError = this.responseText.indexOf("Invalid text") === 0;
      setResponse(this.responseText, isError);
    } else {
      setResponse("The server could not process the request. Please try again.", true);
    }
  };

  xhttp.open(
    "GET",
    "/emotionDetector?textToAnalyze=" + encodeURIComponent(textToAnalyze),
    true
  );
  xhttp.send();
}

function UseExample(button) {
  document.getElementById("textToAnalyze").value = button.textContent;
  document.getElementById("textToAnalyze").focus();
}

function ClearResponse() {
  document.getElementById("textToAnalyze").value = "";
  document.getElementById("textToAnalyze").focus();
  setResponse("Your analysis will appear here.", false);
}

// Deep link support: /?text=<statement> analyses the statement on load.
document.addEventListener("DOMContentLoaded", function () {
  var requestedText = new URLSearchParams(window.location.search).get("text");
  if (requestedText === null) {
    return;
  }
  document.getElementById("textToAnalyze").value = requestedText;
  RunSentimentAnalysis();
});
