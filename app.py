
from flask import Flask, request, render_template_string
import os
import psycopg2

app = Flask(__name__)

# This function connects to your Azure PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        sslmode='require'
    )
    return conn

# This flag makes sure we only create the table once
db_initialized = False

@app.before_request
def init_db():
    global db_initialized
    if db_initialized:
        return
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        db_initialized = True
    except Exception as e:
        print("Database init error:", e)

# Simple HTML page
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>My Mega Azure App</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; background: #f0f4f8; }
        h1 { color: #0078d4; }
        input, button { padding: 12px; font-size: 16px; border-radius: 5px; border: 1px solid #ccc; }
        button { background: #0078d4; color: white; border: none; cursor: pointer; }
        button:hover { background: #005a9e; }
        .msg { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .meta { color: #888; font-size: 12px; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>🚀 Mega Azure DevOps App!</h1>
    <p><b>Stack:</b> Docker + PostgreSQL + GitHub Actions + Azure</p>
    <form method="POST">
        <input name="content" placeholder="Write a message..." required style="width: 70%;">
        <button type="submit">Save to Database</button>
    </form>
    <h2>Messages from PostgreSQL:</h2>
    {% for msg in messages %}
        <div class="msg">
            {{ msg[0] }}
            <div class="meta">{{ msg[1] }}</div>
        </div>
    {% endfor %}
    {% if not messages %}
        <p>No messages yet. Be the first! ☝️</p>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        content = request.form['content']
        cur.execute('INSERT INTO messages (content) VALUES (%s)', (content,))
        conn.commit()
    
    cur.execute('SELECT content, created_at FROM messages ORDER BY created_at DESC')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template_string(HTML, messages=messages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)