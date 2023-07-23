from flask import Flask, render_template, request, redirect, url_for, Markup
import markdown
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Sample blog posts data
posts = [
    {
        'title': 'First Blog Post',
        'content': '# This is the content of my first blog post.\n\n**Hello Markdown!**\n\nThis is an example blog post written in *Markdown*.',
        'date_posted': 'July 23, 2023'
    },
    {
        'title': 'Second Blog Post',
        'content': '# This is the content of my second blog post.\n\n**Markdown is great!**\n\nYou can easily write formatted text using Markdown syntax.',
        'date_posted': 'July 24, 2023'
    }
]

# Register 'markdown' filter with Jinja2
@app.template_filter('markdown')
def convert_markdown_to_html(markdown_text):
    return Markup(markdown.markdown(markdown_text))

@app.route('/')
def home():
    return render_template('index.html', posts=posts)

@app.route('/post/<int:index>')
def post(index):
    post = posts[index] if 0 <= index < len(posts) else None
    return render_template('post.html', post=post)

@app.route('/write_post', methods=['GET', 'POST'])
def write_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form['image_url'] if 'image_url' in request.form else None

        # Here you can process the form data and save the new blog post
        # to your list of posts or a database

        # For this example, let's just add a new post to the list of posts
        new_post = {
            'title': title,
            'content': content,
            'date_posted': 'July 25, 2023',
            'image_url': image_url
        }
        posts.append(new_post)

        # Redirect to the home page after creating the post
        return redirect(url_for('home'))

    return render_template('write_post.html')

if __name__ == '__main__':
    app.run(debug=True)
