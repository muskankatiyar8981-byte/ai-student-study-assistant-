from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
import os
import json
import time

from google import genai
from google.genai import types


app = Flask(__name__)

# =========================================================
# CONFIGURATION
# =========================================================

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "studynova-local-secret-key"
)

DATABASE = "study_assistant.db"

MODEL_NAME = "gemini-3.5-flash-lite"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS study_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# HISTORY
# =========================================================

def save_history(activity_type, topic, content):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO study_history
        (activity_type, topic, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            activity_type,
            topic,
            content,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()


def get_history():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM study_history
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return rows


def get_saved_notes():

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM study_history
        WHERE activity_type = 'Notes'
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return rows


def get_note_by_id(note_id):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM study_history
        WHERE id = ?
        AND activity_type = 'Notes'
        """,
        (note_id,)
    ).fetchone()

    conn.close()

    return row


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(prompt):

    if not GEMINI_API_KEY:
        return (
            "Gemini API key is not configured. "
            "Please add GEMINI_API_KEY in your environment variables."
        )

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2200
            )
        )

        if response and response.text:
            return response.text.strip()

        return "Sorry, Nova could not generate an answer."

    except Exception as e:

        print("Gemini Error:", e)

        return (
            "Sorry, Nova is temporarily unavailable. "
            "Please try again in a moment."
        )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    history = get_history()
    saved_notes = get_saved_notes()

    return render_template(
        "index.html",
        history=history,
        saved_notes=saved_notes
    )


# =========================================================
# ASK NOVA
# =========================================================

@app.route("/ask", methods=["POST"])
def ask():

    question = request.form.get("question", "").strip()
    language = request.form.get("language", "English")

    if not question:

        return redirect(url_for("home"))

    prompt = f"""
You are StudyNova AI, an educational assistant for B.Tech Computer Science students.

Answer the student's question clearly and in an easy-to-understand way.

Question:
{question}

Language:
{language}

Requirements:

- Give a direct answer first.
- Use clear headings.
- Use short paragraphs.
- Use bullet points when useful.
- Give examples when helpful.
- For programming questions, include simple code examples.
- Keep the explanation useful for a college student.
- Do not add unnecessary greetings.
- Do not repeat the question unnecessarily.
"""

    answer = ask_gemini(prompt)

    save_history(
        "Ask AI",
        question,
        answer
    )

    return render_template(
        "result.html",
        topic=question,
        content=answer,
        activity_type="Ask Nova"
    )


# =========================================================
# NOVA NOTES
# =========================================================

@app.route("/notes", methods=["POST"])
def notes():

    topic = request.form.get("topic", "").strip()
    language = request.form.get("language", "English")

    if not topic:

        return redirect(url_for("home"))

    prompt = f"""
Create clear study notes for a B.Tech Computer Science student.

Topic:
{topic}

Language:
{language}

Create well-organized notes.

Use this structure when appropriate:

# Topic Name

## Definition

## Key Points

## Important Concepts

## Example

## Advantages / Features

## Exam Points

Requirements:

- Keep paragraphs short.
- Use bullet points.
- Explain difficult concepts simply.
- Include important keywords.
- Make notes useful for revision.
- Do not add unnecessary greetings.
"""

    notes_content = ask_gemini(prompt)

    save_history(
        "Notes",
        topic,
        notes_content
    )

    return render_template(
        "result.html",
        topic=topic,
        content=notes_content,
        activity_type="Nova Notes",
        saved=True
    )


# =========================================================
# STUDY PLANNER
# =========================================================

@app.route("/planner", methods=["POST"])
def planner():

    subject = request.form.get("subject", "").strip()
    hours = request.form.get("hours", "2").strip()
    language = request.form.get("language", "English")

    if not subject:

        return redirect(url_for("home"))

    prompt = f"""
Create a practical study plan for a B.Tech Computer Science student.

Subject:
{subject}

Available study time:
{hours} hours

Language:
{language}

Create a simple plan with:

# Study Plan

## Session 1

## Session 2

## Revision

## Practice

## Quick Tips

Requirements:

- Divide the available time realistically.
- Use short focused sessions.
- Include revision.
- Include practice/questions.
- Keep the plan easy to follow.
- Do not add unnecessary greetings.
"""

    plan = ask_gemini(prompt)

    save_history(
        "Planner",
        subject,
        plan
    )

    return render_template(
        "result.html",
        topic=subject,
        content=plan,
        activity_type="Study Planner"
    )


# =========================================================
# QUIZ
# =========================================================

@app.route("/quiz", methods=["POST"])
def quiz():

    note_id = request.form.get("note_id")
    language = request.form.get("language", "English")

    if not note_id:

        return redirect(url_for("home"))

    note = get_note_by_id(note_id)

    if not note:

        return redirect(url_for("home"))

    prompt = f"""
Create exactly 10 multiple-choice questions from ONLY the study notes below.

Do not use outside information.

Language:
{language}

Return ONLY valid JSON.

Required JSON format:

[
  {{
    "question": "Question text",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Correct option"
  }}
]

Rules:

- Exactly 10 questions.
- Every question must have exactly 4 options.
- Only one option must be correct.
- The answer must exactly match one of the four options.
- Questions must be based ONLY on the provided notes.
- Do not include markdown.
- Do not include ```json.
- Do not include any explanation outside JSON.

STUDY NOTES:

{note["content"]}
"""

    quiz_response = ask_gemini(prompt)

    try:

        cleaned = quiz_response.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "")
            cleaned = cleaned.replace("```", "")
            cleaned = cleaned.strip()

        questions = json.loads(cleaned)

        if not isinstance(questions, list):
            raise ValueError("Quiz is not a list.")

        if len(questions) != 10:
            raise ValueError("Quiz does not contain exactly 10 questions.")

        for q in questions:

            if "question" not in q:
                raise ValueError("Missing question.")

            if "options" not in q:
                raise ValueError("Missing options.")

            if "answer" not in q:
                raise ValueError("Missing answer.")

            if len(q["options"]) != 4:
                raise ValueError("Question must have 4 options.")

            if q["answer"] not in q["options"]:
                raise ValueError("Correct answer not found in options.")

    except Exception as e:

        print("Quiz JSON Error:", e)
        print("Gemini Quiz Response:", quiz_response)

        return render_template(
            "result.html",
            topic=note["topic"],
            content=(
                "Nova could not create the quiz correctly this time. "
                "Please try again."
            ),
            activity_type="Quiz"
        )

    session["quiz_questions"] = questions
    session["quiz_topic"] = note["topic"]

    return render_template(
        "quiz.html",
        questions=questions,
        topic=note["topic"]
    )


# =========================================================
# SUBMIT QUIZ
# =========================================================

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

    questions = session.get("quiz_questions", [])
    topic = session.get("quiz_topic", "Quiz")

    if not questions:

        return redirect(url_for("home"))

    score = 0
    results = []

    for index, question in enumerate(questions):

        user_answer = request.form.get(
            f"q{index}",
            ""
        )

        correct_answer = question["answer"]

        is_correct = (
            user_answer == correct_answer
        )

        if is_correct:
            score += 1

        results.append({
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    total = len(questions)

    percentage = round(
        (score / total) * 100
    ) if total else 0

    quiz_summary = (
        f"Quiz completed: {score}/{total} "
        f"({percentage}%)"
    )

    save_history(
        "Quiz",
        topic,
        quiz_summary
    )

    session.pop("quiz_questions", None)
    session.pop("quiz_topic", None)

    return render_template(
        "quiz_result.html",
        score=score,
        total=total,
        percentage=percentage,
        results=results,
        topic=topic
    )


# =========================================================
# DELETE ONE HISTORY ITEM
# =========================================================

@app.route("/delete_history/<int:history_id>", methods=["POST"])
def delete_history(history_id):

    try:

        conn = get_connection()

        conn.execute(
            "DELETE FROM study_history WHERE id = ?",
            (history_id,)
        )

        conn.commit()
        conn.close()

    except Exception as e:

        print("Delete history error:", e)

    return redirect(url_for("home"))


# =========================================================
# DELETE ALL HISTORY
# =========================================================

@app.route("/clear_history", methods=["POST"])
def clear_history():

    try:

        conn = get_connection()

        conn.execute(
            "DELETE FROM study_history"
        )

        conn.commit()
        conn.close()

        print("All history deleted successfully.")

    except Exception as e:

        print("Clear history error:", e)

    return redirect(url_for("home"))


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return (
        render_template(
            "result.html",
            topic="Page Not Found",
            content="The page you are looking for does not exist.",
            activity_type="Error"
        ),
        404
    )


@app.errorhandler(500)
def internal_error(error):

    return (
        render_template(
            "result.html",
            topic="Something went wrong",
            content=(
                "StudyNova encountered a temporary error. "
                "Please go back and try again."
            ),
            activity_type="Error"
        ),
        500
    )


# =========================================================
# START APPLICATION
# =========================================================

init_db()


if __name__ == "__main__":

    print()
    print("======================================")
    print("        💜 STUDYNOVA AI")
    print("======================================")
    print("Database ready.")
    print("Starting StudyNova...")
    print("Local URL: http://127.0.0.1:5001")
    print("======================================")
    print()

    app.run(
        debug=True,
        port=5001
    )