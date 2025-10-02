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
