import sqlite3


DB_NAME = "notes.db"


class Helper:

    def _connect(self):
        conn = sqlite3.connect(DB_NAME, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def create_table(self):
        conn = self._connect()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()

    def get_notes(self):
        conn = self._connect()
        notes = conn.execute("SELECT * FROM notes").fetchall()
        conn.close()
        return [dict(n) for n in notes]

    def post_notes(self, title, description):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, description) VALUES (?, ?)",
            (title, description)
        )
        conn.commit()
        note_id = cursor.lastrowid
        conn.close()
        return note_id

    def get_note(self, note_id):
        conn = self._connect()
        note = conn.execute(
            "SELECT * FROM notes WHERE id=?",
            (note_id,)
        ).fetchone()
        conn.close()
        return dict(note) if note else None

    def update_note(self, note_id, title, description):
        conn = self._connect()
        conn.execute(
            "UPDATE notes SET title=?, description=? WHERE id=?",
            (title, description, note_id)
        )
        conn.commit()
        conn.close()

    def delete_note(self, note_id):
        conn = self._connect()
        conn.execute(
            "DELETE FROM notes WHERE id=?",
            (note_id,)
        )
        conn.commit()
        conn.close()