from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOAD_FOLDER'] = 'musics'

db = SQLAlchemy(app)


class Music(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)


setup_done = False


def create_folders(categories):
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    for category in categories:
        path = os.path.join(app.config['UPLOAD_FOLDER'], category)
        if not os.path.exists(path):
            os.makedirs(path)


@app.before_request
def setup():
    global setup_done
    if not setup_done:
        db.create_all()
        categories = ['Pop', 'Rock', 'Jazz', 'Classical', 'HipHop']
        create_folders(categories)
        setup_done = True


@app.route('/upload', methods=['GET', 'POST'])
def upload_music():
    if request.method == 'POST':
        category = request.form['category']
        file = request.files['file']
        if file:
            filename = file.filename
            category_folder = os.path.join(app.config['UPLOAD_FOLDER'], category)
            filepath = os.path.join(category_folder, filename)
            file.save(filepath)

            new_music = Music(name=filename, path=filepath, category=category)
            db.session.add(new_music)
            db.session.commit()
            return redirect(url_for('upload_music'))
    return render_template('upload.html')


@app.route('/play', methods=['GET'])
def play_music():
    musics = Music.query.all()
    music_data = [
        {
            'id': music.id,
            'name': music.name,
            'category': music.category,
            'url': url_for('get_music_file', category=music.category, filename=music.name)
        } for music in musics
    ]
    return render_template('play.html', musics=music_data)


@app.route('/musics/<category>/<filename>')
def get_music_file(category, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], category), filename)


if __name__ == '__main__':
    app.run('0.0.0.0',port=5050)
