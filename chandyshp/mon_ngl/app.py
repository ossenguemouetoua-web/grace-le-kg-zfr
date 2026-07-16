from flask import Flask, request, render_template_string, redirect, url_for, session
from datetime import datetime
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-moi-en-prod")

DB_FILE = "messages.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")  # change ça !


# ---------- BASE DE DONNÉES ----------
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_message(content):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO messages (content, created_at) VALUES (?, ?)",
            (content, datetime.now().strftime("%d/%m/%Y %H:%M")),
        )


def get_messages():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT content, created_at FROM messages ORDER BY id DESC")
        return cur.fetchall()


# ---------- STYLE COMMUN ----------
BASE_STYLE = """
<style>
    * { box-sizing: border-box; }
    body {
        margin: 0;
        background: radial-gradient(circle at top, #1a1f2b, #0E1116 70%);
        color: white;
        font-family: 'Segoe UI', sans-serif;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 40px 20px;
    }
    .card {
        background: #161b22;
        border-radius: 20px;
        padding: 30px 25px;
        max-width: 420px;
        width: 100%;
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        text-align: center;
    }
    h2 { margin-top: 0; font-size: 22px; }
    .subtitle { color: #9aa4b2; font-size: 14px; margin-bottom: 20px; }
    textarea {
        width: 100%;
        height: 110px;
        border-radius: 14px;
        border: 1px solid #2a2f3a;
        background: #0E1116;
        color: white;
        padding: 14px;
        font-size: 15px;
        resize: none;
        outline: none;
    }
    textarea:focus { border-color: #ff3366; }
    button {
        background: linear-gradient(135deg, #ff3366, #ff5e8a);
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 25px;
        font-size: 16px;
        font-weight: 600;
        margin-top: 16px;
        cursor: pointer;
        width: 100%;
        transition: transform 0.15s ease;
    }
    button:hover { transform: scale(1.03); }
    .counter { color: #9aa4b2; font-size: 12px; margin-top: 8px; }
    a { color: #ff5e8a; text-decoration: none; font-size: 14px; }
    .footer { margin-top: 25px; color: #4b5563; font-size: 12px; }
    .msg-box {
        background: #0E1116;
        border: 1px solid #2a2f3a;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
        text-align: left;
        font-size: 15px;
    }
    .msg-date { color: #6b7280; font-size: 11px; margin-top: 6px; display: block; }
    input[type=password] {
        width: 100%;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #2a2f3a;
        background: #0E1116;
        color: white;
        font-size: 15px;
        margin-top: 10px;
    }
</style>
"""

HTML_FORM = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZFR - Messages Anonymes</title>
    """ + BASE_STYLE + """
</head>
<body>
    <div class="card">
        <h2>💌 Envoie-moi un message anonyme</h2>
        <div class="subtitle">Personne ne saura que c'est toi 🤫</div>
        <form action="/send" method="POST">
            <textarea name="message" maxlength="500" placeholder="Dis-moi ce que tu penses..." required oninput="document.getElementById('count').innerText = 500 - this.value.length"></textarea>
            <div class="counter"><span id="count">500</span> caractères restants</div>
            <button type="submit">Envoyer anonymement</button>
        </form>
    </div>
    <div class="footer">Propulsé par Flask 🐍</div>
</body>
</html>
"""

HTML_SENT = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Message envoyé</title>
    """ + BASE_STYLE + """
</head>
<body>
    <div class="card">
        <h2>✅ Message envoyé !</h2>
        <div class="subtitle">Ton message a été transmis anonymement.</div>
        <a href="/">← Envoyer un autre message</a>
    </div>
</body>
</html>
"""

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion</title>
    """ + BASE_STYLE + """
</head>
<body>
    <div class="card">
        <h2>🔒 Accès privé</h2>
        <div class="subtitle">Entre le mot de passe pour voir tes messages</div>
        <form method="POST">
            <input type="password" name="password" placeholder="Mot de passe" required>
            <button type="submit">Voir mes messages</button>
        </form>
        {error}
    </div>
</body>
</html>
"""

HTML_INBOX = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mes messages</title>
    """ + BASE_STYLE + """
</head>
<body>
    <div class="card">
        <h2>📥 Tes messages ({count})</h2>
        {messages}
        <a href="/logout">Se déconnecter</a>
    </div>
</body>
</html>
"""


# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template_string(HTML_FORM)


@app.route('/send', methods=['POST'])
def send():
    msg = (request.form.get('message') or "").strip()
    if msg:
        save_message(msg[:500])  # sécurité longueur
    return render_template_string(HTML_SENT)


@app.route('/inbox', methods=['GET', 'POST'])
def inbox():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['authed'] = True
        else:
            return render_template_string(
                HTML_LOGIN.format(error="<p style='color:#ff3366'>Mot de passe incorrect</p>")
            )

    if not session.get('authed'):
        return render_template_string(HTML_LOGIN.format(error=""))

    rows = get_messages()
    if rows:
        messages_html = "".join(
            f"<div class='msg-box'>{content}<span class='msg-date'>{date}</span></div>"
            for content, date in rows
        )
    else:
        messages_html = "<p style='color:#6b7280'>Aucun message pour l'instant.</p>"

    return render_template_string(HTML_INBOX.format(count=len(rows), messages=messages_html))


@app.route('/logout')
def logout():
    session.pop('authed', None)
    return redirect(url_for('inbox'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

