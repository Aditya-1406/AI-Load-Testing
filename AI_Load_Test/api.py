from flask import Flask, request, jsonify
from helper import Helper

app = Flask(__name__)
db = Helper()
db.create_table()


@app.route("/")
def home():
    return jsonify({"message": "API is running"})


@app.route("/notes", methods=["GET"])
def get_notes():
    return jsonify(db.get_notes())


@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "Title required"}), 400

    note_id = db.post_notes(
        data["title"],
        data.get("description", "")
    )

    return jsonify({
        "message": "Note created",
        "id": note_id
    }), 201


@app.route("/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    note = db.get_note(note_id)
    if note:
        return jsonify(note)
    return jsonify({"error": "Not found"}), 404


@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json()
    db.update_note(
        note_id,
        data.get("title"),
        data.get("description")
    )
    return jsonify({"message": "Updated"})


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    db.delete_note(note_id)
    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=8005)