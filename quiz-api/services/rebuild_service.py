import os
import sqlite3
DB_NAME = "quiz-db.db"

SCHEMA = """
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS participations;
DROP TABLE IF EXISTS questions;

CREATE TABLE "questions" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"title" TEXT NOT NULL,
	"position" INTEGER NOT NULL,
	"text" TEXT NOT NULL,
	"image" BLOB NOT NULL
);

CREATE TABLE "answers" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"question_id" INTEGER NOT NULL,
	"text" TEXT NOT NULL,
	"is_correct" INTEGER NOT NULL,
	"latitude" REAL,
	"longitude" REAL,
	FOREIGN KEY("question_id") REFERENCES "questions"("id") ON DELETE CASCADE
);

CREATE TABLE "participations" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"player_name" TEXT NOT NULL,
	"score" INTEGER NOT NULL,
	"date" TEXT NOT NULL
);
"""

def rebuild_database():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()