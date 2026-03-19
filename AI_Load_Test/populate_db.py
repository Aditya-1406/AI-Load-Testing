import sqlite3

conn = sqlite3.connect("notes.db")
cursor = conn.cursor()

for i in range(200):
    cursor.execute(
        "INSERT INTO notes (title, description) VALUES (?, ?)",
        (f"Note {i}", "Test data")
    )

conn.commit()
conn.close()

print("Database populated successfully")