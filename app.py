from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

#Absolute DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "print_server.db")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'doc', 'docx', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- ENTRY ----------
@app.route('/')
def entry():
    return render_template("entry.html")


# ---------- USER LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')

        if not user or not pwd:
            return render_template("login.html", error="Fill all fields")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT password FROM users WHERE username=? AND role='user'", (user,))
        data = c.fetchone()
        conn.close()

        if data and check_password_hash(data[0], pwd):
            session['user'] = user
            session['role'] = 'user'
            return redirect('/dashboard')

        return render_template("login.html", error="Invalid User Login")

    return render_template("login.html")


# ---------- USER SIGNUP ----------
@app.route('/signup', methods=['POST'])
def signup():
    user = request.form.get('username')
    pwd = request.form.get('password')

    if not user or not pwd:
        return render_template("login.html", error="Fill all fields")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (user, generate_password_hash(pwd), "user"))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return render_template("login.html", error="User already exists")

    conn.close()
    return redirect('/login')


# ---------- ADMIN AUTH ----------
@app.route('/admin_auth')
def admin_auth():
    return render_template("admin_auth.html")


# ---------- ADMIN SIGNUP ----------
@app.route('/admin_signup', methods=['POST'])
def admin_signup():
    user = request.form.get('username')
    pwd = request.form.get('password')

    if not user or not pwd:
        return render_template("admin_auth.html", error="Fill all fields")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (user, generate_password_hash(pwd), "admin"))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return render_template("admin_auth.html", error="Admin already exists")

    conn.close()
    return redirect('/admin_auth')


# ---------- ADMIN LOGIN ----------
@app.route('/admin_login', methods=['POST'])
def admin_login():
    user = request.form.get('username')
    pwd = request.form.get('password')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT password FROM users WHERE username=? AND role='admin'", (user,))
    data = c.fetchone()
    conn.close()

    if data and check_password_hash(data[0], pwd):
        session['user'] = user
        session['role'] = 'admin'
        return redirect('/admin')

    return render_template("admin_auth.html", error="Invalid Admin Login")


# ---------- USER DASHBOARD ----------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session.get('role') != 'user':
        return redirect('/login')

    user = session['user']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    error = None

    if request.method == 'POST':
        action = request.form.get("action")

        # ---------- UPLOAD ----------
        if action == "upload":
            file = request.files.get("file")

            from werkzeug.utils import secure_filename

            if file and file.filename:
                if allowed_file(file.filename):

                    filename = secure_filename(file.filename)
                    path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(path)

                    c.execute("INSERT INTO files (filename, status, user) VALUES (?, ?, ?)",
                              (filename, "Uploaded", user))
                    conn.commit()

                else:
                    error = "Only PDF, JPG, DOC, DOCX, PPTX allowed!"

        # ---------- PRINT ----------
        elif action == "print":
            filename = request.form.get("filename")

            if filename and allowed_file(filename):
                path = os.path.join(UPLOAD_FOLDER, filename)

                if os.path.exists(path):
                    os.system(f"lp '{path}'")

                    c.execute("UPDATE files SET status='Printed' WHERE filename=? AND user=?",
                              (filename, user))
                    conn.commit()

    # ---------- FETCH DATA ----------
    c.execute("SELECT filename, status FROM files WHERE user=?", (user,))
    history = c.fetchall()

    c.execute("SELECT filename FROM files WHERE user=?", (user,))
    file_list = [row[0] for row in c.fetchall()]

    conn.close()

    return render_template("dashboard.html",
                           history=history,
                           user=user,
                           file_list=file_list,
                           error=error)


# ---------- ADMIN DASHBOARD ----------
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/admin_auth')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT username FROM users WHERE role='user'")
    users = c.fetchall()

    c.execute("SELECT filename, status, user FROM files")
    files = c.fetchall()

    c.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM files")
    total_files = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM files WHERE status='Printed'")
    total_printed = c.fetchone()[0]

    conn.close()

    return render_template("admin.html",
                           users=users,
                           files=files,
                           total_users=total_users,
                           total_files=total_files,
                           total_printed=total_printed)


# ---------- View Table ----------
@app.route('/admin/database')
def view_database():
    if session.get('role') != 'admin':
        return redirect('/admin_auth')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    table = request.args.get('table', 'users')
    search = request.args.get('search', '')

    # Get tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in c.fetchall()]

    if table not in tables:
        table = tables[0]

    # Query with search
    if search:
        query = f"SELECT * FROM {table} WHERE " + " OR ".join(
            [f"{col} LIKE ?" for col in get_columns(c, table)]
        )
        values = ['%' + search + '%'] * len(get_columns(c, table))
        c.execute(query, values)
    else:
        c.execute(f"SELECT * FROM {table}")

    rows = c.fetchall()
    col_names = [desc[0] for desc in c.description]

    conn.close()

    return render_template("database.html",
                           tables=tables,
                           current_table=table,
                           rows=rows,
                           col_names=col_names,
                           search=search)


def get_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return [col[1] for col in cursor.fetchall()]

# ---------- Delete Row ----------
@app.route('/admin/delete_row/<table>/<int:id>')
def delete_row(table, id):
    if session.get('role') != 'admin':
        return redirect('/admin_auth')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(f"DELETE FROM {table} WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(f'/admin/database?table={table}')

# ---------- Add Row ----------
@app.route('/admin/add_row/<table>', methods=['POST'])
def add_row(table):
    if session.get('role') != 'admin':
        return redirect('/admin_auth')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    columns = get_columns(c, table)
    values = [request.form.get(col) for col in columns]

    query = f"INSERT INTO {table} VALUES ({','.join(['?']*len(values))})"
    c.execute(query, values)

    conn.commit()
    conn.close()

    return redirect(f'/admin/database?table={table}')

# ---------- DELETE USER ----------
@app.route('/delete_user/<username>')
def delete_user(username):
    if session.get('role') != 'admin':
        return redirect('/admin_auth')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM users WHERE username=? AND role='user'", (username,))
    c.execute("DELETE FROM files WHERE user=?", (username,))
    conn.commit()
    conn.close()

    return redirect('/admin')


# ---------- RESET PASSWORD ----------
@app.route('/reset_password/<username>', methods=['POST'])
def reset_password(username):
    if session.get('role') != 'admin':
        return redirect('/admin_auth')

    new_pass = request.form.get('new_password')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("UPDATE users SET password=? WHERE username=?",
              (generate_password_hash(new_pass), username))
    conn.commit()
    conn.close()

    return redirect('/admin')


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
