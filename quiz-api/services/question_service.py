import sqlite3
from models.question_model import Question, question_from_json
from models.answer_model import Answer
from datetime import datetime, timezone 

DB_PATH = 'quiz-db.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.isolation_level = None 
    return conn

def create_question(json_data):
    question = question_from_json(json_data)
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("BEGIN")
        # Check if position already occupied
        cur.execute("SELECT COUNT(*) FROM questions WHERE position = ?", (question.position,))
        (count,) = cur.fetchone()

        if count > 0:
            # Shift down
            cur.execute("""
                SELECT id, position FROM questions
                WHERE position >= ?
                ORDER BY position DESC
            """, (question.position,))
            rows = cur.fetchall()
            for row_id, pos in rows:
                cur.execute("UPDATE questions SET position = ? WHERE id = ?", (pos + 1, row_id))

        # Insert new question
        cur.execute("""
            INSERT INTO questions (title, position, text, image)
            VALUES (?, ?, ?, ?)
        """, (question.title, question.position, question.text, question.image))

        question_id = cur.lastrowid

        for answer in question.possible_answers:
            cur.execute("""
                INSERT INTO answers (question_id, text, is_correct, latitude, longitude)
                VALUES (?, ?, ?, ?, ?)
            """, (
                question_id,
                answer.text,
                int(answer.is_correct),
                answer.latitude if hasattr(answer, 'latitude') else None,
                answer.longitude if hasattr(answer, 'longitude') else None
            ))

        cur.execute("COMMIT")
        return question_id

    except Exception as e:
        cur.execute("ROLLBACK")
        raise e

    finally:
        conn.close()

def update_question_by_id(question_id, json_data):
    question = question_from_json(json_data)
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("BEGIN")

        # Check if question exists
        cur.execute("SELECT position FROM questions WHERE id = ?", (question_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("ROLLBACK")
            return False  

        old_position = row[0]
        new_position = question.position

        if new_position < old_position:
            # Shift down
            cur.execute("""
                SELECT id, position FROM questions
                WHERE position >= ? AND position < ?
                ORDER BY position DESC
            """, (new_position, old_position))
            rows = cur.fetchall()
            for row_id, pos in rows:
                cur.execute("UPDATE questions SET position = ? WHERE id = ?", (pos + 1, row_id))

        elif new_position > old_position:
            # Shift up
            cur.execute("""
                SELECT id, position FROM questions
                WHERE position <= ? AND position > ?
                ORDER BY position ASC
            """, (new_position, old_position))
            rows = cur.fetchall()
            for row_id, pos in rows:
                cur.execute("UPDATE questions SET position = ? WHERE id = ?", (pos - 1, row_id))

        # Update the question itself
        cur.execute("""
            UPDATE questions
            SET title = ?, position = ?, text = ?, image = ?
            WHERE id = ?
        """, (question.title, new_position, question.text, question.image, question_id))

        # Replace answers
        cur.execute("DELETE FROM answers WHERE question_id = ?", (question_id,))
        for answer in question.possible_answers:
            cur.execute("""
                INSERT INTO answers (question_id, text, is_correct, latitude, longitude)
                VALUES (?, ?, ?, ?, ?)
            """, (
                question_id,
                answer.text,
                int(answer.is_correct),
                answer.latitude if hasattr(answer, 'latitude') else None,
                answer.longitude if hasattr(answer, 'longitude') else None
            ))

        cur.execute("COMMIT")
        return True

    except Exception as e:
        cur.execute("ROLLBACK")
        raise e

    finally:
        conn.close()

def get_question_by_id_from_db(question_id: int) -> Question:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")
        cursor.execute("SELECT title, position, text, image FROM questions WHERE id = ?", (question_id,))
        row = cursor.fetchone()

        if not row:
            cursor.execute("COMMIT")
            return None

        title, position, text, image = row

        cursor.execute("""
            SELECT text, is_correct, latitude, longitude
            FROM answers
            WHERE question_id = ?
        """, (question_id,))
        answers_rows = cursor.fetchall()

        answers = [
            Answer(
                text=ans[0],
                is_correct=bool(ans[1]),
                latitude=ans[2],
                longitude=ans[3]
            )
            for ans in answers_rows
        ]

        cursor.execute("COMMIT")
        return Question(
            title=title,
            position=position,
            text=text,
            image_bytes=image,
            possible_answers=answers,
            question_id=question_id
        )

    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e

    finally:
        conn.close()

def get_question_by_position(position: int) -> Question:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")
        cursor.execute("SELECT id, title, position, text, image FROM questions WHERE position = ?", (position,))
        row = cursor.fetchone()

        if not row:
            cursor.execute("COMMIT")
            return None

        question_id, title, position, text, image = row

        cursor.execute("""
            SELECT text, is_correct, latitude, longitude
            FROM answers
            WHERE question_id = ?
        """, (question_id,))
        answers_rows = cursor.fetchall()

        answers = [
            Answer(
                text=ans[0],
                is_correct=bool(ans[1]),
                latitude=ans[2],
                longitude=ans[3]
            )
            for ans in answers_rows
        ]

        cursor.execute("COMMIT")
        return Question(
            title=title,
            position=position,
            text=text,
            image_bytes=image,
            possible_answers=answers,
            question_id=question_id
        )

    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e

    finally:
        conn.close()

def get_quiz_info_handler():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # Get all participations
        cur.execute("SELECT id, player_name, score, date FROM participations ORDER BY score DESC")
        participations = [
            {
                "id": row["id"],
                "playerName": row["player_name"],
                "score": row["score"],
                "date": row["date"]
            }
            for row in cur.fetchall()
        ]

        # Count questions
        cur.execute("SELECT COUNT(*) as count FROM questions")
        size = cur.fetchone()["count"]

        return {
            "scores": participations,
            "size": size
        }

    finally:
        conn.close()

def delete_question_by_position(position: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        cur.execute("SELECT id FROM questions WHERE position = ?", (position,))
        row = cur.fetchone()
        if not row:
            cur.execute("ROLLBACK")
            return False  

        question_id = row[0]

        cur.execute("DELETE FROM answers WHERE question_id = ?", (question_id,))
        cur.execute("DELETE FROM questions WHERE id = ?", (question_id,))

        cur.execute("""
            UPDATE questions
            SET position = position - 1
            WHERE position > ?
        """, (position,))

        cur.execute("COMMIT")
        return True

    except Exception as e:
        cur.execute("ROLLBACK")
        raise e

    finally:
        conn.close()

def delete_question_by_id(question_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        cur.execute("SELECT position FROM questions WHERE id = ?", (question_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("ROLLBACK")
            return False  

        position = row[0]

        cur.execute("DELETE FROM answers WHERE question_id = ?", (question_id,))
        cur.execute("DELETE FROM questions WHERE id = ?", (question_id,))

        cur.execute("""
            UPDATE questions
            SET position = position - 1
            WHERE position > ?
        """, (position,))

        cur.execute("COMMIT")
        return True

    except Exception as e:
        cur.execute("ROLLBACK")
        raise e

    finally:
        conn.close()

def delete_all_questions():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("BEGIN")

        cur.execute("DELETE FROM answers")
        cur.execute("DELETE FROM questions")

        cur.execute("COMMIT")
        return True

    except Exception as e:
        cur.execute("ROLLBACK")
        raise e

    finally:
        conn.close()

def delete_all_participations():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM participations")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def create_participation_handler(player_name, submitted_answers):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Get quiz size
        cur.execute("SELECT COUNT(*) FROM questions")
        (quiz_size,) = cur.fetchone()

        # Validate answers length
        if len(submitted_answers) != quiz_size:
            raise ValueError("Invalid number of submitted answers")

        score = 0

        # Calculate score
        for position, submitted_answer_index in enumerate(submitted_answers, start=1):
            cur.execute("""
                SELECT a.id, a.is_correct
                FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE q.position = ?
                ORDER BY a.id ASC
            """, (position,))
            answers_for_question = cur.fetchall()

            idx = submitted_answer_index - 1  

            if 0 <= idx < len(answers_for_question):
                answer,is_correct = answers_for_question[idx]
                if is_correct == 1:
                    score += 1
            else:
                raise ValueError("Invalid answer index for question at position {}".format(position))

        current_date = datetime.now(timezone.utc).isoformat()

        cur.execute("""
            INSERT INTO participations (player_name, score, date)
            VALUES (?, ?, ?)
        """, (player_name, score, current_date))

        participation_id = cur.lastrowid

        conn.commit()

        return {
            "id": participation_id,
            "playerName": player_name,
            "score": score,
            "date": current_date
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

def get_all_questions() -> list[Question]:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN")

        cursor.execute("SELECT id, title, position, text, image FROM questions ORDER BY position ASC")
        rows = cursor.fetchall()

        questions = []

        for row in rows:
            question_id, title, position, text, image = row

            # Now includes latitude and longitude
            cursor.execute("""
                SELECT text, is_correct, latitude, longitude
                FROM answers
                WHERE question_id = ?
            """, (question_id,))
            answers_rows = cursor.fetchall()

            # Updated to unpack and pass optional lat/lon
            answers = [
                Answer(
                    text=ans[0],
                    is_correct=bool(ans[1]),
                    latitude=ans[2],
                    longitude=ans[3]
                )
                for ans in answers_rows
            ]

            question = Question(
                title=title,
                position=position,
                text=text,
                image_bytes=image,
                possible_answers=answers,
                question_id=question_id
            )
            questions.append(question)

        cursor.execute("COMMIT")
        return questions

    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e

    finally:
        conn.close()