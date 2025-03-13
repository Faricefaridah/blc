import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
database = "blacklist.db"

# Sample users with roles
users = {
    "faridah": {"password": "faridah1234", "role": "admin"},
    "staff": {"password": "staff1234", "role": "staff"}
}

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(database)
    except sqlite3.Error as e:
        print(e)
    return conn

@app.route('/')
def index():
    return render_template('index.html', clients=None)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    if username in users and users[username]['password'] == password and users[username]['role'] == role:
        session['logged_in'] = True
        session['role'] = role
        session['username'] = username
        return redirect('/')
    else:
        return "Invalid credentials. Please try again."

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('role', None)
    session.pop('username', None)
    return redirect('/')

@app.route('/add', methods=['POST'])
def add_client():
    if session.get('role') == 'admin':
        conn = create_connection()
        cur = conn.cursor()
        name = request.form['name']
        id_number = request.form['id_number']
        shop = request.form['shop']
        phone_number = request.form['phone_number']
        cur.execute("INSERT INTO blacklisted_clients (name, id_number, shop, phone_number) VALUES (?, ?, ?, ?)", 
                    (name, id_number, shop, phone_number))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        return "Access denied."

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form['search_term']
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM blacklisted_clients WHERE name LIKE ? OR id_number LIKE ?", 
                ('%' + search_term + '%', '%' + search_term + '%'))
    clients = cur.fetchall()
    conn.close()
    return render_template('index.html', clients=clients)

@app.route('/delete/<int:client_id>')
def delete_client(client_id):
    if session.get('role') == 'admin':
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM blacklisted_clients WHERE id=?", (client_id,))
        conn.commit()
        conn.close()
        return redirect('/')
    else:
        return "Access denied."

if __name__ == '__main__':
    app.run(debug=True)
