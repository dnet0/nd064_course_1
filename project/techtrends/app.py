import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Define the Flask application
app = Flask(__name__)

# Configurar logging global
logging.basicConfig(
    level=logging.DEBUG,  # Captura DEBUG
    format='%(levelname)s:%(name)s:%(asctime)s, %(message)s')

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.INFO)

# Amount connection
amount_connections = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    # Increment amount connections
    global amount_connections
    amount_connections += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Function to get total amount of post in DB
def get_amount_post():
    connection = get_db_connection()
    amount_post = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    connection.close()
    print(amount_post)
    return amount_post


app.config['SECRET_KEY'] = 'your secret key'

# Define the heltz endpoint
@app.route('/heltz')
def heltz():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )

    return response
    
# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    amount_post = get_amount_post()[0]
    response = app.response_class(
        response=json.dumps({"db_connection_count": amount_connections,
        "post_count": amount_post}),
        status=200,
        mimetype='application/json'
    )

    return response

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info("Article doesn't existed!")
      return render_template('404.html'), 404
    else:
      app.logger.info(f"Article \"{post['title']}\" retrieved!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("The \"About Us\" page is retrieved.")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            
            app.logger.info(f"Article \"{title}\" created!")
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
