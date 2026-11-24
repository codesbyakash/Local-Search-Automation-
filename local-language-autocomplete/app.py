
from flask import Flask, render_template, request, jsonify
from pathlib import Path

from database import database
from trie.trie import Trie

app = Flask(__name__)
trie = Trie()


def load_words_into_trie():
    """Load database words into the Trie."""
    for word, frequency in database.get_all_words():
        trie.insert(word, frequency)


def refresh_word(word):
    """Refresh one word's frequency from SQLite."""
    for saved_word, frequency in database.get_all_words():
        if saved_word == word:
            trie.update_frequency(saved_word, frequency)
            return


database.init_db()
load_words_into_trie()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/suggest")
def suggest():
    query = request.args.get("q", "").strip()
    limit_text = request.args.get("limit", "8")

    if len(query) > 100:
        return jsonify({"error": "Search query is too long"}), 400

    try:
        limit = int(limit_text)
    except ValueError:
        return jsonify({"error": "Limit must be a number"}), 400

    limit = max(1, min(limit, 20))

    if not query:
        return jsonify({
            "query": query,
            "suggestions": []
        })

    suggestions = trie.suggest(query, limit)

    return jsonify({
        "query": query,
        "suggestions": suggestions
    })


@app.route("/api/select", methods=["POST"])
def select_word():
    data = request.get_json(silent=True) or {}
    word = data.get("word", "")

    if not isinstance(word, str) or not word.strip():
        return jsonify({"error": "A valid word is required"}), 400

    word = word.strip()

    if len(word) > 100:
        return jsonify({"error": "Word is too long"}), 400

    updated = database.increase_frequency(word)

    if not updated:
        return jsonify({"error": "Word not found"}), 404

    refresh_word(word)

    return jsonify({
        "message": "Word selection recorded",
        "word": word
    })


@app.route("/api/words", methods=["POST"])
def add_new_word():
    data = request.get_json(silent=True) or {}
    word = data.get("word", "")

    if not isinstance(word, str):
        return jsonify({"error": "Word must be text"}), 400

    word = word.strip()

    if not word or len(word) > 100:
        return jsonify({"error": "Enter a word under 100 characters"}), 400

    database.add_word(word)
    load_words_into_trie()

    return jsonify({
        "message": "Word saved successfully",
        "word": word
    }), 201


@app.route("/api/stats")
def stats():
    return jsonify({
        "total_words": database.get_word_count()
    })


if __name__ == "__main__":
    app.run(debug=True)
