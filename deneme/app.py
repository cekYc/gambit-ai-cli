from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Veritabanı ayarları (SQLite kullanıyoruz)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Blog Modeli
class Post(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    title = db.Column('title', db.String(100), nullable=False)
    content = db.Column('content', db.Text, nullable=False)

# Veritabanını oluştur
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('index.html', posts=Post.query.all()) # Basitlik için aynı sayfada gösteriyoruz ama normalde ayrı bir form sayfası olurdu

# Not: CRUD'u tek sayfada (index) yönetmek daha pratik olacak, 
# o yüzden HTML tarafında modal veya basit yönlendirmeler kullanacağız.

@app.route('/post/delete/<int:id>')
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/post/update/<int:id>', methods=['POST'])
def update_post(id):
    post = Post.query.get_or_404(id)
    post.title = request.form['title']
    post.content = request.form['content']
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
