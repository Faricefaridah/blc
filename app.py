import sqlite3
import os
from flask import Flask, render_template, request, redirect, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'a_strong_secret_key')
DATABASE = "blacklist.db"

users = {
    "faridah": {"password": generate_password_hash("faridah1234"), "role": "admin"},
    "staff": {"password": generate_password_hash("staff1234"), "role": "staff"}
}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def create_table():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS blacklisted_clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        id_number TEXT UNIQUE NOT NULL,
                        shop TEXT,
                        phone_number TEXT
                    )''')
        conn.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    create_table()
    conn = get_db()
    clients = conn.execute("SELECT * FROM blacklisted_clients").fetchall()
    return render_template('index.html', clients=clients)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    user = users.get(username)
    if user and check_password_hash(user['password'], password) and user['role'] == role:
        session['logged_in'] = True
        session['role'] = role
        session['username'] = username
        return redirect('/')
    else:
        return "Invalid credentials. Please try again."

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add', methods=['POST'])
def add_client():
    if session.get('role') == 'admin':
        name = request.form['name']
        id_number = request.form['id_number']
        shop = request.form['shop']
        phone_number = request.form['phone_number']

        conn = get_db()
        try:
            conn.execute("INSERT INTO blacklisted_clients (name, id_number, shop, phone_number) VALUES (?, ?, ?, ?)", 
                         (name, id_number, shop, phone_number))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Error: ID number must be unique."
        
        return redirect('/')
    else:
        return "Access denied."

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    conn = get_db()
    clients = conn.execute("SELECT * FROM blacklisted_clients WHERE LOWER(name) LIKE LOWER(?) OR id_number LIKE ?", 
                           ('%' + search_term + '%', '%' + search_term + '%')).fetchall()
    return render_template('index.html', clients=clients)

@app.route('/delete/<int:client_id>')
def delete_client(client_id):
    if session.get('role') == 'admin':
        conn = get_db()
        conn.execute("DELETE FROM blacklisted_clients WHERE id=?", (client_id,))
        conn.commit()
        return redirect('/')
    else:
        return "Access denied."

if __name__ == '__main__':
    app.run(debug=True)
