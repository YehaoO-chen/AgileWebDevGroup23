<<<<<<< HEAD
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
=======
from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def home(name=None):
    return render_template('home.html')
>>>>>>> cf24331 (set a project)
