from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return psycopg2.connect(
        host="localhost",
        database="voting_db",
        user="postgres",
        password="Sneha@40"  
    )

@app.route('/')
def home():
    return redirect('/login')

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (u, p))
            conn.commit()
            cur.close()
            conn.close()
        except:
            return "User already exists!"

        return redirect('/login')

    return render_template('register.html')

# LOGIN (Normal User)
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user'] = user[1]
            return redirect('/dashboard')
        else:
            return "Invalid credentials!"

    return render_template('login.html')

# ADMIN LOGIN
@app.route('/admin-login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s AND is_admin=TRUE", (u, p))
        admin = cur.fetchone()
        cur.close()
        conn.close()

        if admin:
            session['user'] = admin[1]
            return redirect('/admin')
        else:
            return "Invalid admin credentials!"

    return render_template('admin_login.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM candidates")
    candidates = cur.fetchall()

    cur.execute("SELECT voted FROM users WHERE username=%s", (session['user'],))
    voted = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template('dashboard.html', candidates=candidates, voted=voted)

# VOTE
@app.route('/vote/<int:id>')
def vote(id):
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT voted FROM users WHERE username=%s", (session['user'],))
    if cur.fetchone()[0]:
        return "You already voted!"

    cur.execute("UPDATE candidates SET votes = votes + 1 WHERE id=%s", (id,))
    cur.execute("UPDATE users SET voted = TRUE WHERE username=%s", (session['user'],))

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/dashboard')

# ADMIN PANEL (Protected)
@app.route('/admin', methods=['GET','POST'])
def admin():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    # check admin
    cur.execute("SELECT is_admin FROM users WHERE username=%s", (session['user'],))
    is_admin = cur.fetchone()[0]

    if not is_admin:
        cur.close()
        conn.close()
        return "Access Denied! Admins only."

    # admin work
    if request.method == 'POST':
        name = request.form['name']
        cur.execute("INSERT INTO candidates (name) VALUES (%s)", (name,))
        conn.commit()

    cur.execute("SELECT * FROM candidates")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin.html', data=data)

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)