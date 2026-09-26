from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.recommendation_model import recommend_book

# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__)
CORS(app)

# =========================================================
# RECOMMENDATION API
# =========================================================

@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received."
        }), 400

    title = data.get("title", "").strip()
    author = data.get("author", "").strip()
    work_key = data.get("work_key", "").strip()

    if not title or not work_key:
        return jsonify({
            "error": "Title and work_key are required."
        }), 400

    try:
        recommendations = recommend_book(
            work_key,
            title,
            author
        )

        live = recommendations["Live"]

        if live.empty:
            return jsonify({
                "recommendations": []
            })

        results = live.to_dict(orient="records")

        return jsonify({
            "recommendations": results
        })

    except Exception as e:

        print("API ERROR:", e)

        return jsonify({
            "error": "Could not generate recommendations."
        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )