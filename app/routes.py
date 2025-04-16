from flask import render_template

def init_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/study-plan')
    def study_plan():
        return render_template('study_plan.html')

    @app.route('/share')
    def share():
        return render_template('share.html')