from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    conn = sqlite3.connect('user_data.db')
    conn.row_factory = sqlite3.Row  # Это позволит вам получать данные в формате словаря
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_info")
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(items)

if __name__ == '__main__':
    app.run(debug=True)
