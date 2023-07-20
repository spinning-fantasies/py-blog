from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3



app = Flask(__name__)

# Initialize the SQLite database connection
DATABASE = 'blog.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Create the database tables if they don't exist
init_db()

@app.route("/", methods=["GET"])
def index():
    db = get_db()
    cursor = db.cursor()

    # Retrieve all non-deleted blog posts with their associated tags
    cursor.execute("SELECT blog_posts.*, GROUP_CONCAT(tags.name) AS tag_names FROM blog_posts LEFT JOIN blog_post_tags ON blog_posts.id = blog_post_tags.post_id LEFT JOIN tags ON blog_post_tags.tag_id = tags.id WHERE blog_posts.deleted = 0 GROUP BY blog_posts.id ORDER BY blog_posts.id DESC")
    blog_posts = cursor.fetchall()

    # Set an empty string for tag_names if there are no tags for a post
    for post in blog_posts:
        post["tag_names"] = post["tag_names"] or ""

    return render_template("index.html", blog_posts=blog_posts)

@app.route("/create", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        tags = request.form["tags"].split(',')

        db = get_db()
        cursor = db.cursor()

        # Insert the new blog post into the database
        cursor.execute("INSERT INTO blog_posts (title, content) VALUES (?, ?)", (title, content))
        post_id = cursor.lastrowid
        db.commit()

        # Add tags to the blog post
        for tag in tags:
            tag = tag.strip()
            if tag:
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                db.commit()
                cursor.execute("SELECT id FROM tags WHERE name=?", (tag,))
                tag_id = cursor.fetchone()['id']
                cursor.execute("INSERT INTO blog_post_tags (post_id, tag_id) VALUES (?, ?)", (post_id, tag_id))
                db.commit()

        return redirect(url_for("index"))

    return render_template("create_post.html")

@app.route("/remove/<int:post_id>", methods=["GET"])
def remove_post(post_id):
    db = get_db()
    cursor = db.cursor()

    # Soft delete the post by updating the 'deleted' column to 1
    cursor.execute("UPDATE blog_posts SET deleted = ? WHERE id = ?", (1, post_id))
    db.commit()

    return redirect(url_for("index"))

@app.route("/edit/<int:post_id>", methods=["GET"])
def edit_post(post_id):
    db = get_db()
    cursor = db.cursor()

    # Retrieve the post to edit
    cursor.execute("SELECT * FROM blog_posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()

    return render_template("edit_post.html", post=post)

@app.route("/update/<int:post_id>", methods=["POST"])
def update_post(post_id):
    title = request.form["title"]
    content = request.form["content"]

    db = get_db()
    cursor = db.cursor()

    # Update the post with the new data
    cursor.execute("UPDATE blog_posts SET title = ?, content = ? WHERE id = ?", (title, content, post_id))
    db.commit()

    return redirect(url_for("index"))

@app.route("/read/<int:post_id>", methods=["GET"])
def read_post(post_id):
    db = get_db()
    cursor = db.cursor()

    # Retrieve the specific blog post
    cursor.execute("SELECT blog_posts.*, GROUP_CONCAT(tags.name) AS tag_names FROM blog_posts LEFT JOIN blog_post_tags ON blog_posts.id = blog_post_tags.post_id LEFT JOIN tags ON blog_post_tags.tag_id = tags.id WHERE blog_posts.deleted = 0 AND blog_posts.id = ? GROUP BY blog_posts.id", (post_id,))
    post = cursor.fetchone()

    # Set an empty string for tag_names if there are no tags
    post["tag_names"] = post["tag_names"] or ""

    return render_template("read_post.html", post=post)


@app.route("/tags", methods=["GET"])
def tags_list():
    db = get_db()
    cursor = db.cursor()

    # Retrieve all tags
    cursor.execute("SELECT * FROM tags ORDER BY name")
    tags = cursor.fetchall()

    return render_template("tags_list.html", tags=tags)

if __name__ == "__main__":
    app.run(debug=True)
