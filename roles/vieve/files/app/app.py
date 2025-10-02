from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
import sqlite3, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(
    __name__,
    template_folder='/opt/vieve/templates',
    static_folder='/opt/vieve/static'
)

UPLOAD_FOLDER = '/opt/vieve/static/uploads'
DB_PATH = '/opt/vieve/database.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT,
        ip TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if request.method == 'POST':
        file = request.files['photo']
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            c.execute("INSERT INTO photos (filename) VALUES (?)", (filename,))
            conn.commit()
    c.execute("SELECT filename FROM photos ORDER BY timestamp DESC LIMIT 12")
    photos = c.fetchall()
    conn.close()
    return render_template('upload.html', photos=photos)

@app.route('/delete/<filename>')
def delete(filename):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM photos WHERE filename=?", (filename,))
    conn.commit()
    conn.close()
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect('/upload')

@app.route('/calendar')
def calendar():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT label, timestamp FROM events ORDER BY timestamp DESC")
    events = c.fetchall()
    conn.close()
    return render_template('calendar.html', events=events)

@app.route('/calendar/add', methods=['POST'])
def calendar_add():
    label = request.form['label']
    date = request.form['date']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO events (label, ip, timestamp) VALUES (?, ?, ?)", (label, request.remote_addr, date))
    conn.commit()
    conn.close()
    return redirect('/calendar')

@app.route('/events.json')
def events_json():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT label, timestamp FROM events")
    rows = c.fetchall()
    conn.close()
    events = [
        {"title": label, "start": timestamp}
        for label, timestamp in rows
    ]
    return jsonify(events)

@app.route('/buttons', methods=['GET', 'POST'])
def buttons():
    if request.method == 'POST':
        label = request.form['label']
        ip = request.remote_addr
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO events (label, ip) VALUES (?, ?)", (label, ip))
        conn.commit()
        conn.close()
        return redirect('/calendar')
    return render_template('buttons.html')

@app.route('/stats')
def stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM photos")
    photo_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM events")
    event_count = c.fetchone()[0]
    conn.close()
    return render_template('stats.html', photo_count=photo_count, event_count=event_count)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10992)
