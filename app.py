from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)

# Templates
TEMPLATE_HOME = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo List</title>
    <style>
    /* General Body Styles */
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5;
        margin: 0;
        padding: 0;
        color: #333;
    }

    header {
        background-color: #4CAF50;
        color: white;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    /* Container for Content */
    .container {
        margin: 40px auto;
        max-width: 450px;
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease-in-out;
    }

    /* Form Styling */
    form {
        margin-bottom: 20px;
        text-align: center;
    }

    input[type="text"] {
        width: 100%;
        padding: 12px 15px;
        margin: 8px 0;
        border: 1px solid #ddd;
        border-radius: 6px;
        font-size: 16px;
        box-sizing: border-box;
        transition: 0.3s ease-in-out;
    }

    input[type="text"]:focus {
        border-color: #4CAF50;
        outline: none;
    }

    button {
        padding: 12px 20px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease-in-out;
    }

    button:hover {
        background-color: #45a049;
    }

    /* Task List Styling */
    .task {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px;
        border-bottom: 1px solid #ddd;
        transition: background-color 0.3s ease;
    }

    .task:last-child {
        border-bottom: none;
    }

    .task:hover {
        background-color: #f0f0f0;
    }

    .task a {
        color: #d9534f;
        text-decoration: none;
        font-size: 14px;
        padding: 6px;
        border-radius: 4px;
    }

    .task a:hover {
        background-color: #d9534f;
        color: white;
    }

    /* Logout Link */
    .logout {
        margin-top: 20px;
        text-align: center;
    }

    .logout a {
        color: #4CAF50;
        text-decoration: none;
        font-size: 16px;
        font-weight: bold;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        header {
            padding: 12px;
        }

        .container {
            margin: 20px;
            padding: 15px;
        }

        input[type="text"], button {
            font-size: 14px;
            padding: 10px;
        }

        .task {
            padding: 10px;
        }

        .logout a {
            font-size: 14px;
        }
    }

    @media (max-width: 480px) {
        header {
            font-size: 20px;
            padding: 10px;
        }

        .container {
            padding: 10px;
            max-width: 90%;
        }

        input[type="text"], button {
            padding: 8px;
            font-size: 14px;
        }

        .task {
            font-size: 14px;
            padding: 8px;
        }

        .logout a {
            font-size: 14px;
        }
    }
    </style>
</head>
<body>
    <header>
        <h1>Todo List</h1>
    </header>
    <div class="container">
        <form method="POST" action="{{ url_for('add_task') }}">
            <input type="text" name="content" placeholder="Add a new task" required>
            <button type="submit">Add Task</button>
        </form>
        {% for task in tasks %}
        <div class="task">
            <span>{{ task.content }}</span>
            <a href="{{ url_for('delete_task', task_id=task.id) }}">Delete</a>
        </div>
        {% endfor %}
        <div class="logout">
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
</body>
</html>
"""

TEMPLATE_LOGIN_REGISTER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
        }
        .container {
            margin: 50px auto;
            max-width: 400px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        form {
            margin-bottom: 20px;
        }
        input[type="text"], input[type="password"] {
            width: calc(100% - 22px);
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        a {
            color: #4CAF50;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>{{ title }}</h2>
        <form method="POST" action="{{ url_for(endpoint) }}">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">{{ button_text }}</button>
        </form>
        {% if alternate %}
        <a href="{{ url_for(alternate) }}">{{ alternate_text }}</a>
        {% endif %}
    </div>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        tasks = Task.query.filter_by(user_id=session['user_id']).all()
        return render_template_string(TEMPLATE_HOME, tasks=tasks)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template_string(TEMPLATE_LOGIN_REGISTER, title='Register', endpoint='register', button_text='Register', alternate='login', alternate_text='Already have an account? Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'error')
    return render_template_string(TEMPLATE_LOGIN_REGISTER, title='Login', endpoint='login', button_text='Login', alternate='register', alternate_text='Don\'t have an account? Register')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' in session:
        content = request.form['content']
        new_task = Task(content=content, user_id=session['user_id'])
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' in session:
        task = Task.query.get_or_404(task_id)
        if task.user_id == session['user_id']:
            db.session.delete(task)
            db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
