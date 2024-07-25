from flask import Flask, request
from transformers import pipeline
import textstat
from cache import get_from_cache, put_in_cache

pipe = pipeline("text-classification", model="./roberta-base-go_emotions")

app = Flask(__name__)


@app.route('/readability')
def readability():
    text = request.args.get('text')
    return textstat.flesch_kincaid_grade(text)


@app.route('/analyze')
def analyze():
    text = request.args.get('text')
    result = get_from_cache(text)

    if not result:
        result = pipe(text)
        put_in_cache(text, result)
    return result


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
