import os
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Prevent GUI backend issues
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    subject TEXT,
                    marks INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route('/')
def index():
    conn = sqlite3.connect('students.db')
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    avg = df['marks'].mean() if not df.empty else 0
    return render_template('index.html', data=df.to_dict(orient='records'), avg=round(avg, 2))

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    subject = request.form['subject']
    marks = request.form['marks']

    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name, subject, marks) VALUES (?, ?, ?)",
              (name, subject, marks))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/visualize')
def visualize():
    conn = sqlite3.connect('students.db')
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    chart_path = 'static/performance.png'
    chart_exists = False

    if not df.empty:
        if not os.path.exists('static'):
            os.makedirs('static')
        plt.figure(figsize=(6, 4))
        df.groupby('subject')['marks'].mean().plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Average Marks by Subject')
        plt.ylabel('Marks')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        chart_exists = True

    return render_template('visualize.html', chart_exists=chart_exists)

if __name__ == '__main__':
    app.run(debug=True)
