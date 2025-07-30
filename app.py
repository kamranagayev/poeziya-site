from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

POEMS_DIR = "poeziya"

# Birdən çox poeziya oxuyan funksiya
def read_poem(filename):
    path = os.path.join(POEMS_DIR, filename)
    poems = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip().split("---")
            for index, poem_block in enumerate(content):
                lines = poem_block.strip().split("\n")
                if len(lines) > 1:
                    title = lines[0].strip()
                    poem_text = "\n".join(lines[1:]).strip()
                    poems.append({"id": index, "title": title, "poem": poem_text})
    return poems

# Poeziya silən funksiya
def delete_poem(category, poem_id):
    filename = f"{category}.txt"
    path = os.path.join(POEMS_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip().split("---")
        if 0 <= poem_id < len(content):
            del content[poem_id]
        with open(path, 'w', encoding='utf-8') as f:
            if content:
                f.write("---\n".join([c.strip() for c in content if c.strip()]) + "\n")
            else:
                f.write("")

# Poeziya redaktə funksiyası
def update_poem(category, poem_id, new_title, new_poem):
    filename = f"{category}.txt"
    path = os.path.join(POEMS_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip().split("---")

        if 0 <= poem_id < len(content):
            content[poem_id] = f"{new_title}\n{new_poem}\n"

        with open(path, 'w', encoding='utf-8') as f:
            f.write("---\n".join([c.strip() for c in content if c.strip()]) + "\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        category = request.form.get('category', 'love')
        if request.form.get('action') == 'delete':
            poem_id = int(request.form.get('delete_id'))
            delete_poem(category, poem_id)
        elif request.form.get('action') == 'add':
            title = request.form.get('title')
            poem = request.form.get('poem')

            if not os.path.exists(POEMS_DIR):
                os.makedirs(POEMS_DIR)

            filename = f"{category}.txt"
            path = os.path.join(POEMS_DIR, filename)
            with open(path, 'a', encoding='utf-8') as f:
                f.write(title + "\n" + poem + "\n---\n")
    else:
        category = request.args.get('category', 'love')  # URL-dən oxuyuruq

    poems = read_poem(f"{category}.txt")
    return render_template('admin.html', poems=poems, current_category=category)

@app.route('/edit/<category>/<int:poem_id>', methods=['GET', 'POST'])
def edit_poem(category, poem_id):
    poems = read_poem(f"{category}.txt")
    poem_to_edit = next((p for p in poems if p["id"] == poem_id), None)

    if poem_to_edit is None:
        return "Поезію не знайдено!", 404

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_poem = request.form.get('poem')
        update_poem(category, poem_id, new_title, new_poem)
        return redirect(url_for('admin', category=category))  # Düzəliş edilmiş yönləndirmə

    return render_template('edit.html', poem=poem_to_edit, category=category)

@app.route('/love')
def love():
    poems = read_poem("love.txt")
    return render_template('poeziya.html', category_name="ПРО ЛЮБОВ", poezia=poems)

@app.route('/patriotic')
def patriotic():
    poems = read_poem("patriotic.txt")
    return render_template('poeziya.html', category_name="ПАТРІОТИЧНІ", poezia=poems)

@app.route('/philosophy')
def philosophy():
    poems = read_poem("philosophy.txt")
    return render_template('poeziya.html', category_name="ФІЛОСОФСЬКІ", poezia=poems)

@app.route('/other')
def other():
    poems = read_poem("other.txt")
    return render_template('poeziya.html', category_name="ІНШІ", poezia=poems)

if __name__ == '__main__':
    app.run(debug=True)
