from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "study_assistant.db"


# =========================
# DATABASE
# =========================

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_history(activity_type, topic, content):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO study_history
        (activity_type, topic, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        activity_type,
        topic,
        content,
        datetime.now().strftime("%d-%m-%Y %I:%M %p")
    ))

    conn.commit()
    conn.close()


def get_history():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, activity_type, topic, content, created_at
        FROM study_history
        ORDER BY id DESC
    """)

    history = cursor.fetchall()

    conn.close()

    return history


# =========================
# HOME
# =========================

@app.route("/")
def home():

    history = get_history()

    return render_template(
        "index.html",
        history=history
    )


# =========================
# ASK AI
# =========================

@app.route("/ask", methods=["POST"])
def ask():

    question = request.form.get("question", "").strip()

    q = question.lower()

    if "dbms" in q:

        answer = """DBMS stands for Database Management System.

It is software used to store, manage and retrieve data from a database.

Main features:
• Data storage
• Data security
• Data retrieval
• Data management
• Backup and recovery

Examples: MySQL, Oracle and PostgreSQL."""

    elif "python" in q:

        answer = """Python is a high-level programming language.

It is easy to learn because its syntax is simple and readable.

Python is commonly used for:
• Web Development
• Artificial Intelligence
• Machine Learning
• Data Analysis
• Automation"""

    elif "java" in q:

        answer = """Java is a high-level, object-oriented programming language.

Important concepts of Java include:
• Class and Object
• Inheritance
• Polymorphism
• Encapsulation
• Abstraction

Java is widely used for software and application development."""

    elif "computer" in q:

        answer = """A computer is an electronic device that accepts data as input,
processes it and produces useful output.

Basic working:

Input → Processing → Output

A computer can also store data for future use."""

    else:

        answer = f"""Here is an easy explanation of your question:

{question}

Start by understanding the basic definition and main concept.

Study Tips:
• Learn the definition first.
• Understand the concept with an example.
• Write short notes.
• Practice related questions."""

    save_history(
        "Ask AI",
        question,
        answer
    )

    history = get_history()

    return render_template(
        "index.html",
        answer=answer,
        answer_question=question,
        history=history
    )


# =========================
# GENERATE NOTES
# =========================

@app.route("/notes", methods=["POST"])
def notes():

    topic = request.form.get("topic", "").strip()

    t = topic.lower()

    if "dbms" in t:

        notes = f"""
📚 {topic.upper()} - Easy Study Notes

1. Definition
DBMS stands for Database Management System.
It is software used to store, manage and retrieve data.

2. Features
• Data security
• Data storage
• Data retrieval
• Backup and recovery
• Data consistency

3. Advantages
• Reduces data redundancy
• Easy data access
• Better security
• Easy data management

4. Examples
MySQL, Oracle, PostgreSQL

⭐ Exam Tip:
Learn the definition, features, advantages and examples.
"""

    elif "python" in t:

        notes = f"""
🐍 {topic.upper()} - Easy Study Notes

1. Definition
Python is a high-level, interpreted programming language.

2. Features
• Simple syntax
• Easy to learn
• Open source
• Portable
• Large library support

3. Applications
• Web Development
• AI and Machine Learning
• Data Analysis
• Automation

⭐ Exam Tip:
Remember Python's features and applications.
"""

    elif "java" in t:

        notes = f"""
☕ {topic.upper()} - Easy Study Notes

1. Definition
Java is a high-level, object-oriented programming language.

2. Features
• Object-oriented
• Platform independent
• Secure
• Robust
• Portable

3. OOP Concepts
• Encapsulation
• Inheritance
• Polymorphism
• Abstraction

⭐ Exam Tip:
Prepare the four pillars of OOP.
"""

    elif "operating system" in t or t == "os":

        notes = f"""
💻 {topic.upper()} - Easy Study Notes

1. Definition
An Operating System is system software that manages
computer hardware and software resources.

2. Main Functions
• Process Management
• Memory Management
• File Management
• Device Management
• Security

3. Examples
Windows, Linux, macOS, Android

⭐ Exam Tip:
Learn the definition and major functions of an Operating System.
"""

    else:

        notes = f"""
📖 {topic.upper()} - Easy Study Notes

1. Introduction
{topic} is an important topic in computer science.

2. Basic Concept
First understand the definition and basic working of {topic}.

3. Key Points
• Learn the basic definition.
• Understand important concepts.
• Study examples.
• Remember important applications.

4. Exam Preparation
• Learn important definitions.
• Make short notes.
• Practice questions.
• Revise regularly.

⭐ Study Tip:
Understand the concept first and then memorize important points.
"""

    save_history(
        "Notes",
        topic,
        notes
    )

    history = get_history()

    return render_template(
        "index.html",
        notes=notes,
        notes_topic=topic,
        history=history
    )


# =========================
# STUDY PLANNER
# =========================

@app.route("/planner", methods=["POST"])
def planner():

    subject = request.form.get("subject", "").strip()

    hours = request.form.get("hours", "").strip()

    try:
        hours = int(hours)
    except ValueError:
        hours = 2

    if hours <= 2:

        plan = f"""
📅 STUDY PLAN

Subject: {subject}
Daily Study Time: {hours} hour(s)

⏰ Schedule

1️⃣ Concept Learning — 45 minutes
Study the basic concepts of {subject}.

2️⃣ Short Break — 10 minutes

3️⃣ Practice — 45 minutes
Solve questions and examples related to {subject}.

4️⃣ Revision — 20 minutes
Revise everything studied today.

🎯 Daily Goal:
Understand → Practice → Revise

💡 Tip:
Study consistently every day.
"""

    elif hours <= 4:

        plan = f"""
📅 STUDY PLAN

Subject: {subject}
Daily Study Time: {hours} hours

⏰ Schedule

1️⃣ Concept Learning — 1 hour
Learn the main concepts of {subject}.

2️⃣ Break — 15 minutes

3️⃣ Practice — 1 hour
Solve questions and examples.

4️⃣ Break — 15 minutes

5️⃣ Revision — 45 minutes
Revise today's topics.

6️⃣ Quick Test — 30 minutes
Test yourself without looking at your notes.

🎯 Daily Goal:
Learn → Practice → Revise → Test
"""

    else:

        plan = f"""
📅 STUDY PLAN

Subject: {subject}
Daily Study Time: {hours} hours

⏰ Schedule

1️⃣ Concept Learning — 2 hours
Study the important concepts of {subject}.

2️⃣ Break — 20 minutes

3️⃣ Practice — 1.5 hours
Solve problems and previous questions.

4️⃣ Break — 20 minutes

5️⃣ Revision — 1 hour
Revise the topics studied today.

6️⃣ Self Test — 30 minutes
Solve questions without using notes.

🎯 Daily Goal:
Complete concepts → Practice → Revise → Test

💡 Tip:
Take short breaks and keep your study sessions focused.
"""

    save_history(
        "Study Planner",
        subject,
        plan
    )

    history = get_history()

    return render_template(
        "index.html",
        plan=plan,
        plan_subject=subject,
        history=history
    )


# =========================
# QUIZ GENERATOR
# =========================

@app.route("/quiz", methods=["POST"])
def quiz():

    topic = request.form.get("quiz_topic", "").strip()

    t = topic.lower()

    if "dbms" in t:

        questions = [

            {
                "question": "What does DBMS stand for?",
                "options": [
                    "Data Backup Management System",
                    "Database Management System",
                    "Database Memory System",
                    "Data Management Software"
                ],
                "answer": "Database Management System"
            },

            {
                "question": "Which is an example of DBMS?",
                "options": [
                    "MySQL",
                    "HTML",
                    "CSS",
                    "Python"
                ],
                "answer": "MySQL"
            },

            {
                "question": "Which language is commonly used to query databases?",
                "options": [
                    "HTML",
                    "SQL",
                    "CSS",
                    "Python"
                ],
                "answer": "SQL"
            },

            {
                "question": "Which key uniquely identifies a record?",
                "options": [
                    "Foreign Key",
                    "Primary Key",
                    "Alternate Key",
                    "Secondary Key"
                ],
                "answer": "Primary Key"
            },

            {
                "question": "DBMS helps to reduce:",
                "options": [
                    "Data redundancy",
                    "Computer speed",
                    "Internet usage",
                    "Screen size"
                ],
                "answer": "Data redundancy"
            }

        ]

    elif "python" in t:

        questions = [

            {
                "question": "Python is a:",
                "options": [
                    "High-level programming language",
                    "Database",
                    "Operating System",
                    "Web browser"
                ],
                "answer": "High-level programming language"
            },

            {
                "question": "Which symbol is used for comments in Python?",
                "options": [
                    "//",
                    "#",
                    "<!-- -->",
                    "**"
                ],
                "answer": "#"
            },

            {
                "question": "Which function is used to display output?",
                "options": [
                    "display()",
                    "print()",
                    "output()",
                    "show()"
                ],
                "answer": "print()"
            },

            {
                "question": "Which data type stores True or False?",
                "options": [
                    "int",
                    "string",
                    "boolean",
                    "float"
                ],
                "answer": "boolean"
            },

            {
                "question": "Python is widely used in:",
                "options": [
                    "AI",
                    "Data Analysis",
                    "Web Development",
                    "All of these"
                ],
                "answer": "All of these"
            }

        ]

    elif "java" in t:

        questions = [

            {
                "question": "Java is mainly a:",
                "options": [
                    "Object-oriented programming language",
                    "Database",
                    "Operating System",
                    "Browser"
                ],
                "answer": "Object-oriented programming language"
            },

            {
                "question": "Which is a pillar of OOP?",
                "options": [
                    "Encapsulation",
                    "Compilation",
                    "Execution",
                    "Debugging"
                ],
                "answer": "Encapsulation"
            },

            {
                "question": "Which keyword is used to create a class?",
                "options": [
                    "object",
                    "class",
                    "create",
                    "newclass"
                ],
                "answer": "class"
            },

            {
                "question": "Java is:",
                "options": [
                    "Platform dependent",
                    "Platform independent",
                    "Hardware dependent",
                    "Browser dependent"
                ],
                "answer": "Platform independent"
            },

            {
                "question": "Which concept allows one class to acquire properties of another?",
                "options": [
                    "Encapsulation",
                    "Inheritance",
                    "Abstraction",
                    "Compilation"
                ],
                "answer": "Inheritance"
            }

        ]

    else:

        questions = [

            {
                "question": f"What is the basic definition of {topic}?",
                "options": [
                    "A computer science concept",
                    "A type of hardware",
                    "A web browser",
                    "None of these"
                ],
                "answer": "A computer science concept"
            },

            {
                "question": f"Why is {topic} important?",
                "options": [
                    "For learning concepts",
                    "For understanding technology",
                    "For practical applications",
                    "All of these"
                ],
                "answer": "All of these"
            }

        ]

    return render_template(
        "index.html",
        quiz=questions,
        quiz_topic=topic,
        history=get_history()
    )


# =========================
# SUBMIT QUIZ
# =========================

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():

    topic = request.form.get("quiz_topic", "").strip()

    t = topic.lower()

    if "dbms" in t:

        answers = [
            "Database Management System",
            "MySQL",
            "SQL",
            "Primary Key",
            "Data redundancy"
        ]

    elif "python" in t:

        answers = [
            "High-level programming language",
            "#",
            "print()",
            "boolean",
            "All of these"
        ]

    elif "java" in t:

        answers = [
            "Object-oriented programming language",
            "Encapsulation",
            "class",
            "Platform independent",
            "Inheritance"
        ]

    else:

        answers = [
            "A computer science concept",
            "All of these"
        ]

    score = 0

    for i, correct_answer in enumerate(answers):

        user_answer = request.form.get(f"q{i}")

        if user_answer == correct_answer:
            score += 1

    total = len(answers)

    percentage = int((score / total) * 100)

    if percentage >= 80:

        message = "🏆 Excellent! Keep it up!"

    elif percentage >= 60:

        message = "👏 Good job! A little more revision will help."

    elif percentage >= 40:

        message = "📚 Keep practicing. You can improve!"

    else:

        message = "💪 Don't worry. Revise the topic and try again!"

    result = f"""
🎯 QUIZ RESULT

Subject: {topic}

Score: {score} / {total}

Percentage: {percentage}%

{message}
"""

    save_history(
        "Quiz",
        topic,
        result
    )

    history = get_history()

    return render_template(
        "index.html",
        result=result,
        result_topic=topic,
        history=history
    )


# =========================
# DELETE HISTORY
# =========================

@app.route("/delete_history/<int:history_id>")
def delete_history(history_id):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM study_history WHERE id = ?",
        (history_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# CLEAR ALL HISTORY
# =========================

@app.route("/clear_history")
def clear_history():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM study_history")

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        port=5001
    )