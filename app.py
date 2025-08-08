# app.py
import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, Poem

app = Flask(__name__)

# Render Postgres URL (Render → Environment → DATABASE_URL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# TXT fayllar yalnız bir dəfəlik köçürmə üçündür
POEMS_DIR = "poeziya"

# --- TXT oxuyub DB-yə köçürmək üçün köməkçi ---
def migrate_from_txt():
    categories = ["love", "patriotic", "philosophy", "other"]
    for category in categories:
        path = os.path.join(POEMS_DIR, f"{category}.txt")
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip().split("---")
        for block in content:
            lines = [l for l in block.strip().split("\n") if l.strip()]
            if len(lines) > 1:
                title = lines[0].strip()
                text = "\n".join(lines[1:]).strip()
                exists = Poem.query.filter_by(category=category, title=title, text=text).first()
                if not exists:
                    db.session.add(Poem(category=category, title=title, text=text))
    db.session.commit()

# --- İlk requestdə cədvəli yarat + DB boşdursa TXT-dən yüklə ---
@app.before_first_request
def init_db_and_maybe_migrate():
    db.create_all()
    if Poem.query.count() == 0:
        migrate_from_txt()

# --- (İstəyə görə) Dinamik səhifələrdə keşləməni söndür ---
@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp

# ================== ROUTES (hamısı DB ilə işləyir) ==================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    category = request.values.get('category', 'love')

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            title = (request.form.get('title') or '').strip()
            text  = (request.form.get('poem')  or '').strip()
            if title and text:
                db.session.add(Poem(category=category, title=title, text=text))
                db.session.commit()
        elif action == 'delete':
            poem_id = int(request.form.get('delete_id'))
            p = Poem.query.filter_by(id=poem_id, category=category).first()
            if p:
                db.session.delete(p)
                db.session.commit()

    poems = Poem.query.filter_by(category=category).order_by(Poem.created_at.desc()).all()
    view_poems = [{"id": p.id, "title": p.title, "poem": p.text} for p in poems]
    return render_template('admin.html', poems=view_poems, current_category=category)

@app.route('/edit/<category>/<int:poem_id>', methods=['GET', 'POST'])
def edit_poem(category, poem_id):
    p = Poem.query.filter_by(id=poem_id, category=category).first()
    if not p:
        return "Poem not found", 404
    if request.method == 'POST':
        p.title = request.form.get('title', p.title)
        p.text  = request.form.get('poem',  p.text)
        db.session.commit()
        return redirect(url_for('admin', category=category))
    return render_template('edit.html', poem={"title": p.title, "poem": p.text}, category=category)

def render_category(category_name, title_ua):
    poems = Poem.query.filter_by(category=category_name).order_by(Poem.created_at.desc()).all()
    return render_template('poeziya.html', category_name=title_ua,
                           poezia=[{"title": p.title, "poem": p.text} for p in poems])

@app.route('/love')
def love():
    return render_category("love", "ПРО ЛЮБОВ")

@app.route('/patriotic')
def patriotic():
    return render_category("patriotic", "ПАТРІОТИЧНІ")

@app.route('/philosophy')
def philosophy():
    return render_category("philosophy", "ФІЛОСОФСЬКІ")

@app.route('/other')
def other():
    return render_category("other", "ІНШІ")

# Lokal işlədəndə lazım olsa
if __name__ == '__main__':
    app.run(debug=True)
