from flask import Flask, render_template, request, redirect
import sqlite3

# CREATE FLASK APP
app = Flask(__name__)


# DATABASE CONNECTION
def get_db_connection():

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row

    return conn


# CREATE TABLES
def init_db():

    conn = get_db_connection()

    # EXPENSE TABLE
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL

        )
    ''')

    # USER TABLE
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL

        )
    ''')

    conn.commit()
    conn.close()


# INITIALIZE DATABASE
init_db()


# HOME PAGE
@app.route('/')
def home():

    search = request.args.get('search', '')

    conn = get_db_connection()

    # SEARCH
    if search:

        expenses = conn.execute(
            '''
            SELECT * FROM expenses
            WHERE title LIKE ? OR category LIKE ?
            ''',
            ('%' + search + '%', '%' + search + '%')
        ).fetchall()

    else:

        expenses = conn.execute(
            'SELECT * FROM expenses'
        ).fetchall()

    # TOTAL EXPENSE
    total = conn.execute(
        'SELECT SUM(amount) FROM expenses'
    ).fetchone()[0]

    if total is None:
        total = 0

    # CHART DATA
    category_data = conn.execute(
        '''
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
        '''
    ).fetchall()

    conn.close()

    return render_template(
        'index.html',
        expenses=expenses,
        total=total,
        category_data=category_data
    )


# ADD EXPENSE
@app.route('/add', methods=['GET', 'POST'])
def add_expense():

    if request.method == 'POST':

        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        conn = get_db_connection()

        conn.execute(
            '''
            INSERT INTO expenses
            (title, amount, category, date)
            VALUES (?, ?, ?, ?)
            ''',
            (title, amount, category, date)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_expense.html')


# EDIT EXPENSE
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):

    conn = get_db_connection()

    expense = conn.execute(
        'SELECT * FROM expenses WHERE id = ?',
        (id,)
    ).fetchone()

    if request.method == 'POST':

        title = request.form['title']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        conn.execute(
            '''
            UPDATE expenses
            SET title = ?, amount = ?, category = ?, date = ?
            WHERE id = ?
            ''',
            (title, amount, category, date, id)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    conn.close()

    return render_template(
        'edit_expense.html',
        expense=expense
    )


# DELETE EXPENSE
@app.route('/delete/<int:id>')
def delete_expense(id):

    conn = get_db_connection()

    conn.execute(
        'DELETE FROM expenses WHERE id = ?',
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()

        conn.execute(
            '''
            INSERT INTO users
            (username, password)
            VALUES (?, ?)
            ''',
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()

        user = conn.execute(
            '''
            SELECT * FROM users
            WHERE username = ? AND password = ?
            ''',
            (username, password)
        ).fetchone()

        conn.close()

        if user:

            return redirect('/')

        else:

            return "Invalid Username or Password"

    return render_template('login.html')


# RUN APPLICATION
if __name__ == '__main__':
    app.run(debug=True)